"""Screening-grain reuse of governed rule builders."""

from __future__ import annotations

from typing import Any

import ior_mvp.rules as governed

UNAVAILABLE = "UNAVAILABLE"


def _coded(row: dict[str, Any]) -> dict[str, Any]:
    rule_id = str(row["rule_id"])
    key = rule_id.replace("-", "_")
    fired = (
        "FIRED"
        if row.get("fired") is True
        else "NOT_FIRED"
        if row.get("fired") is False
        else "NA"
    )
    return {
        "rule_id": rule_id,
        "execution": row["execution"],
        "fired": row.get("fired"),
        "metrics": row.get("metrics", {}),
        "result_code": f"{key}_{row['execution']}_{fired}",
        "decision_effect_code": f"{key}_EFFECT",
    }


def _custom(
    rule_id: str,
    execution: str,
    fired: bool | None,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return _coded(
        {
            "rule_id": rule_id,
            "execution": execution,
            "fired": fired,
            "metrics": metrics,
        }
    )


def screening_ledger(
    case: dict[str, Any],
    tariff_index: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[dict[str, Any]]:
    rules_config = thresholds["rules"]
    hs6 = case.get("hs6", "")
    rows = case.get("trade", [])
    if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
        r0 = _custom("R0", "DISABLED", None, {"mapping_status": "NOT_CALCULABLE"})
    elif tariff_index.get("complete") is True and hs6 in tariff_index.get("hs6", set()):
        r0 = _custom("R0", "FULL", True, {"mapping_status": "VALID"})
    else:
        r0 = _custom(
            "R0",
            "DEGRADED",
            True,
            {
                "mapping_status": "NOT_CALCULABLE",
                "evidence_need_code": "identity/tariff-line",
            },
        )
    missing = case.get("trade_quality", {}).get("missing_years", [])
    r1f = _custom(
        "R1-F",
        "DISABLED" if missing else "FULL",
        None if missing else False,
        {"missing_years": list(missing)},
    )
    built = [
        governed._r1d_rule(case, rules_config["R1_D"]),
        governed._r2_rule(case, rules_config["R2"]),
        governed._r3_rule(case, rules_config["R3"]),
        governed._r4d_rule(case, rules_config["R4_D"]),
        governed._r5_rule(case, rules_config["R5"]),
        governed._r9s_rule(case["domestic_capability"]),
    ]
    r3 = built[2]
    built.extend(
        [
            governed._r10_rule(case, r3),
            governed._r11_rule(case, rules_config["R11"]),
        ]
    )
    return [r0, r1f, *(_coded(row) for row in built)]


def _ledger_row(ledger: list[dict[str, Any]], rule_id: str) -> dict[str, Any]:
    return next(
        (row for row in ledger if row.get("rule_id") == rule_id),
        {"execution": "DISABLED", "fired": None, "metrics": {}},
    )


def _continuity(case: dict[str, Any]) -> dict[str, str]:
    quality = case.get("trade_quality", {})
    if quality.get("missing_years"):
        return {"status": "GAP_YEARS", "pattern": "GAP_YEARS"}
    by_year = quality.get("hs_revisions_by_year", {})
    revisions = [
        tuple(value)
        for _, value in sorted(by_year.items())
        if isinstance(value, list) and value
    ]
    if len(set(revisions)) > 1:
        return {
            "status": "REVISION_CHANGE_IN_WINDOW",
            "pattern": "ABSENT_BEFORE_REVISION_CHANGE",
        }
    return {"status": "CONTINUOUS", "pattern": "NONE"}


def warnings(
    case: dict[str, Any],
    ledger: list[dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    latest = max(
        (
            row
            for row in case.get("trade", [])
            if isinstance(row, dict) and isinstance(row.get("year"), int)
        ),
        key=lambda row: row["year"],
        default={},
    )
    imports = latest.get("imports_usd_m")
    exports = latest.get("exports_usd_m")
    ratio = (
        float(exports) / float(imports)
        if isinstance(exports, (int, float))
        and isinstance(imports, (int, float))
        and imports > 0
        else UNAVAILABLE
    )
    r2 = _ledger_row(ledger, "R2")
    metrics = r2.get("metrics", {})
    share = metrics.get("quantity_contribution_share")
    delta = metrics.get("delta_ln_value")
    minimum = float(
        thresholds["rules"]["R2"]["minimum_quantity_contribution_share"]
    )
    price_led = bool(
        r2.get("execution") == "FULL"
        and r2.get("fired") is False
        and isinstance(delta, (int, float))
        and delta > 0
        and isinstance(share, (int, float))
        and share < minimum
    )
    ratio_warning = bool(
        isinstance(ratio, (int, float))
        and ratio
        > float(
            thresholds["rules"]["R11"][
                "generic_capacity_export_import_value_ratio"
            ]
        )
    )
    return {
        "export_import_ratio_warning": ratio_warning,
        "export_import_value_ratio": ratio,
        "price_led_growth": price_led,
        "classification_continuity": _continuity(case),
    }
