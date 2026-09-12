"""Typed screening dispositions without formal decision states."""

from __future__ import annotations

from typing import Any

from ior_mvp import public_decision, signals

from .config import screening_config


def _row(ledger: list[dict[str, Any]], rule_id: str) -> dict[str, Any]:
    return next(
        (row for row in ledger if row.get("rule_id") == rule_id),
        {"execution": "DISABLED", "fired": None, "metrics": {}},
    )


def _compact_exclusions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "code": row.get("code"),
            "status": row.get("status"),
            "reason_code": row.get("reason_code"),
            "evidence_ids": list(row.get("evidence_ids", [])),
        }
        for row in rows
    ]


def classify(record_inputs: dict[str, Any]) -> dict[str, Any]:
    ledger = record_inputs["ledger"]
    case = record_inputs["case"]
    warning_block = record_inputs.get("warnings", {})
    if "exclusions" in record_inputs:
        exclusions = _compact_exclusions(record_inputs["exclusions"])
    else:
        exclusions = _compact_exclusions(
            public_decision.evaluate_hard_exclusions(case)
        )
    fired = signals.fired_signal_rule_ids(ledger)
    material = signals.material_trigger_rule_ids(ledger)
    supporting = signals.advance_supporting_signal_rule_ids(ledger)
    r0 = _row(ledger, "R0")
    r3 = _row(ledger, "R3")
    r9s = _row(ledger, "R9-S")
    r11 = _row(ledger, "R11")
    hard_satisfied = any(row["status"] == "SATISFIED" for row in exclusions)
    generic_capacity = (
        r11.get("execution") == "FULL" and r11.get("fired") is True
    )
    screening = public_decision.screen_candidate(
        has_candidate_trigger=bool(fired),
        screen_exclusion_satisfied=hard_satisfied or generic_capacity,
    )["screening_disposition"]
    import_rows = [
        row
        for row in case.get("trade", [])
        if isinstance(row, dict)
        and isinstance(row.get("imports_usd_m"), (int, float))
        and row["imports_usd_m"] > 0
    ]
    if screening == "SCREENED_OUT":
        reason = (
            "HARD_EXCLUSION_SATISFIED"
            if hard_satisfied
            else "GENERIC_CAPACITY_CONTRADICTED"
        )
    elif screening == "NO_CANDIDATE":
        if r0.get("execution") == "DISABLED":
            reason = "IDENTITY_UNRESOLVED"
        elif not import_rows:
            reason = "NO_IMPORT_OBSERVATIONS"
        else:
            reason = "NO_TRIGGER_FIRED"
    else:
        reason = (
            "MATERIAL_TRIGGER_FIRED"
            if material
            else "NON_MATERIAL_SIGNAL_ONLY"
        )
    indicated_state: str | None = None
    indication_reason: str | None = None
    monitor_trigger: dict[str, Any] | None = None
    if screening == "SCREENED_OUT":
        indicated_state = "REJECT"
        indication_reason = reason
    elif material:
        indicated_state = "INVESTIGATE"
        indication_reason = "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
    elif r3.get("fired") is True:
        indicated_state = "MONITOR"
        indication_reason = "NON_MATERIAL_SIGNAL_ONLY"
        monitor_trigger = {
            "domain": "supplier_concentration",
            "condition_code": screening_config()["monitor_trigger"][
                "condition_code"
            ],
            "evidence_ids": list(
                record_inputs.get("partner_evidence_ids", [])
            ),
        }
    needs: list[dict[str, Any]] = []

    def need(code: str, evidence_ids: list[str] | None = None) -> None:
        if code not in {item["code"] for item in needs}:
            needs.append(
                {"code": code, "evidence_ids": list(evidence_ids or [])}
            )

    if r0.get("execution") == "DEGRADED":
        need("identity/tariff-line")
    if screening == "CANDIDATE" and material:
        need("target specification/application")
        need("line-level production or producer-grade matrix")
    if warning_block.get("export_import_ratio_warning") is True or warning_block.get(
        "price_led_growth"
    ) is True:
        need("re-export/origin decomposition")
    if r9s.get("fired") is True:
        need("capacity/availability/allocation")
    result: dict[str, Any] = {
        "fired_signal_rule_ids": fired,
        "material_trigger_rule_ids": material,
        "advance_supporting_signal_rule_ids": supporting,
        "exclusions": exclusions,
        "screening_disposition": screening,
        "disposition_reason_code": reason,
        "indicated_state": indicated_state,
        "indication_reason_code": indication_reason,
        "evidence_needs": needs,
    }
    if monitor_trigger is not None:
        result["monitor_trigger"] = monitor_trigger
    return result
