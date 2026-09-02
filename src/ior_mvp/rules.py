from __future__ import annotations

import math
from typing import Any

from .config import thresholds_config


def _rule(
    rule_id: str,
    name: str,
    execution: str,
    fired: bool | None,
    result: str,
    decision_effect: str,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "name": name,
        "execution": execution,
        "fired": fired,
        "result": result,
        "decision_effect": decision_effect,
        "metrics": metrics or {},
    }


def log_change(new: float, old: float) -> float:
    if new <= 0 or old <= 0:
        raise ValueError("Log change requires positive values")
    return math.log(new / old)


def quantity_contribution_share(delta_ln_q: float, delta_ln_uv: float) -> float:
    denominator = abs(delta_ln_q) + abs(delta_ln_uv)
    if denominator == 0:
        return 0.0
    return abs(delta_ln_q) / denominator


NOT_CALCULABLE = "NOT_CALCULABLE"


def r1d_fires(
    positive_years: list[int],
    rule_config: dict[str, Any],
) -> bool:
    if not positive_years:
        return False
    window_span_years = max(positive_years) - min(positive_years)
    return (
        len(positive_years) >= int(rule_config["positive_observed_years"])
        and window_span_years < int(rule_config["window_years"])
    )


def r2_fires(
    delta_ln_quantity: float,
    contribution_share: float,
    quantity_growth: float,
    rule_config: dict[str, Any],
) -> bool:
    positive_quantity_required = bool(
        rule_config["require_positive_quantity_growth"]
    )
    return (
        (not positive_quantity_required or delta_ln_quantity > 0)
        and contribution_share
        >= float(rule_config["minimum_quantity_contribution_share"])
        and quantity_growth >= float(rule_config["minimum_quantity_cagr"])
    )


def r3_fires(
    hhi: float | None,
    largest_supplier_share: float | None,
    rule_config: dict[str, Any],
) -> bool:
    hhi_fires = (
        hhi is not None and hhi >= float(rule_config["supplier_hhi"])
    )
    largest_supplier_fires = (
        largest_supplier_share is not None
        and largest_supplier_share
        >= float(rule_config["largest_supplier_share"])
    )
    return hhi_fires or largest_supplier_fires


def r11_generic_capacity_fires(
    generic_capacity_reject: bool,
    export_import_value_ratio: float | None,
    rule_config: dict[str, Any],
) -> bool:
    return bool(
        generic_capacity_reject
        and export_import_value_ratio is not None
        and export_import_value_ratio
        > float(rule_config["generic_capacity_export_import_value_ratio"])
    )


def evaluate_rules(case: dict[str, Any]) -> list[dict[str, Any]]:
    thresholds = thresholds_config()["rules"]
    trade = sorted(case["trade"], key=lambda row: row["year"])
    quality = case["trade_quality"]
    context = case["rule_context"]
    results: list[dict[str, Any]] = []

    results.append(
        _rule(
            "R0",
            "Identity gate",
            "FULL",
            True,
            f"HS revision {case['opportunity']['hs_revision']} and HS6 {case['opportunity']['hs6']} are frozen in the snapshot; specification/application remains separately gated.",
            "Continue to screening while preserving the unresolved decision object.",
        )
    )

    results.append(
        _rule(
            "R1-F",
            "Persistent retained exposure — full",
            "DISABLED" if quality.get("missing_years") else "FULL",
            None if quality.get("missing_years") else False,
            "Full continuity is unavailable and gross flows are not retained imports."
            if quality.get("missing_years")
            else "Full persistence test did not fire.",
            "Do not claim the full persistence rule.",
            {"missing_years": quality.get("missing_years", [])},
        )
    )

    positive_years = [
        row["year"] for row in trade if row.get("imports_usd_m", 0) > 0
    ]
    r1d_fired = r1d_fires(positive_years, thresholds["R1_D"])
    results.append(
        _rule(
            "R1-D",
            "Persistence signal — degraded",
            "DEGRADED",
            r1d_fired,
            f"{len(positive_years)} positive observed years within the configured window; no interpolation used.",
            "Generate INVESTIGATE only; confidence capped at C.",
            {"positive_years": positive_years, "confidence_cap": "C"},
        )
    )

    if len(trade) >= 2 and all(
        trade[-1].get(key) is not None and trade[-2].get(key) is not None
        for key in ("imports_usd_m", "imports_kt")
    ):
        previous, latest = trade[-2], trade[-1]
        delta_v = log_change(latest["imports_usd_m"], previous["imports_usd_m"])
        delta_q = log_change(latest["imports_kt"], previous["imports_kt"])
        uv_latest = latest.get("import_uv_usd_t") or (
            latest["imports_usd_m"] * 1000 / latest["imports_kt"]
        )
        uv_previous = previous.get("import_uv_usd_t") or (
            previous["imports_usd_m"] * 1000 / previous["imports_kt"]
        )
        delta_uv = log_change(uv_latest, uv_previous)
        share = quantity_contribution_share(delta_q, delta_uv)
        quantity_growth = latest["imports_kt"] / previous["imports_kt"] - 1
        r2_fired = r2_fires(
            delta_q,
            share,
            quantity_growth,
            thresholds["R2"],
        )
        r2_result = (
            "Quantity-led expansion signal fires."
            if r2_fired
            else "Value movement is not quantity-led under the configured test."
        )
        results.append(
            _rule(
                "R2",
                "Quantity-led expansion",
                "FULL",
                r2_fired,
                r2_result,
                "Separate structural volume growth from price movement.",
                {
                    "from_year": previous["year"],
                    "to_year": latest["year"],
                    "delta_ln_value": round(delta_v, 4),
                    "delta_ln_quantity": round(delta_q, 4),
                    "delta_ln_unit_value": round(delta_uv, 4),
                    "quantity_contribution_share": round(share, 4),
                },
            )
        )
    else:
        results.append(
            _rule(
                "R2",
                "Quantity-led expansion",
                "DISABLED",
                None,
                "Comparable value and quantity observations are unavailable.",
                "No inference.",
            )
        )

    supplier = case.get("supplier_metrics_2024")
    if supplier:
        r3_config = thresholds["R3"]
        hhi = supplier.get("partner_value_hhi")
        largest_supplier_share = supplier.get("largest_supplier_share")
        r3_fired = r3_fires(
            hhi,
            largest_supplier_share,
            r3_config,
        )
        results.append(
            _rule(
                "R3",
                "Supplier concentration",
                "FULL",
                r3_fired,
                "External supply is concentrated."
                if r3_fired
                else "Concentration threshold not met.",
                "Generate a resilience/diversification review, not an automatic localisation recommendation.",
                {
                    "hhi": hhi,
                    "hhi_threshold": float(r3_config["supplier_hhi"]),
                    "largest_supplier_share": (
                        largest_supplier_share
                        if largest_supplier_share is not None
                        else NOT_CALCULABLE
                    ),
                    "largest_supplier_threshold": float(
                        r3_config["largest_supplier_share"]
                    ),
                    "top_two_share": supplier.get("top_two_value_share"),
                },
            )
        )
    else:
        results.append(
            _rule(
                "R3",
                "Supplier concentration",
                "DISABLED",
                None,
                "Partner concentration metrics are absent from the frozen case snapshot.",
                "No concentration inference.",
            )
        )

    results.append(
        _rule(
            "R4-F",
            "Product-tier heterogeneity — full",
            "DISABLED",
            None,
            "Partner-month × tariff-line cells are unavailable.",
            "Do not fit clusters or claim grades.",
        )
    )
    r4d = bool(context.get("r4_degraded_dispersion_signal"))
    results.append(
        _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            "DEGRADED",
            r4d,
            "Annual/partner product-mix signal is visible." if r4d else "No material degraded dispersion signal recorded.",
            "Open specification research only; no grade conclusion.",
        )
    )

    r5 = bool(context.get("domestic_production_exists") and context.get("material_imports_exist"))
    results.append(
        _rule(
            "R5",
            "Domestic supply plus continued imports",
            "DEGRADED",
            r5,
            "Verified domestic capability coexists with material gross imports." if r5 else "Coexistence condition not met.",
            "Test specification, qualification, capacity, price, application and allocation mismatch.",
        )
    )

    results.append(
        _rule(
            "R6",
            "Capacity pressure",
            "DISABLED",
            None,
            "Effective utilisation and target-specification shortage are not public.",
            "Obtain line-level availability, yield, qualification share and allocation.",
        )
    )
    results.append(
        _rule(
            "R7",
            "Latent domestic capacity",
            "DISABLED",
            None,
            "Idle qualified capacity and specification equivalence are not established publicly.",
            "Do not assume latent capacity.",
        )
    )
    results.append(
        _rule(
            "R8",
            "Committed future demand",
            "DISABLED",
            None,
            "Awarded/financed demand at the target specification is unavailable.",
            "Keep base, committed and announced demand separate when provided.",
        )
    )

    r9 = bool(context.get("same_process_family_plus_signal"))
    results.append(
        _rule(
            "R9-S",
            "Coarse incumbent adjacency screen",
            "FULL",
            r9,
            "A verified Saudi plant is in the same process family with additional capability signals." if r9 else "No defensible coarse adjacency signal.",
            "Open the full line-level capability assessment; do not publish D* from screening alone.",
        )
    )

    r10 = bool(context.get("strategic_resilience_review"))
    results.append(
        _rule(
            "R10",
            "Strategic criticality",
            "DEGRADED" if r10 else "DISABLED",
            r10 if r10 else None,
            "A resilience review is warranted by concentration; formal criticality still requires authority confirmation."
            if r10
            else "No responsible-authority criticality designation is present in the demo snapshot.",
            "Keep commercial viability and strategic value separate.",
        )
    )

    latest = trade[-1]
    export_import_ratio = latest.get("export_import_value_ratio")
    r11_config = thresholds["R11"]
    r11 = r11_generic_capacity_fires(
        bool(context.get("generic_capacity_reject")),
        export_import_ratio,
        r11_config,
    )
    results.append(
        _rule(
            "R11",
            "Economic exclusion / generic-capacity warning",
            "FULL" if export_import_ratio is not None else "DEGRADED",
            r11,
            (
                f"Gross exports are {export_import_ratio:.1f}× imports; generic new capacity cannot be justified from HS6 imports alone."
                if r11
                else "No public-data generic-capacity exclusion fires."
            ),
            "Reject generic support or move only a named specialty exception to investigation.",
            {
                "export_import_value_ratio": export_import_ratio,
                "export_import_value_ratio_threshold": float(
                    r11_config["generic_capacity_export_import_value_ratio"]
                ),
            },
        )
    )

    missing_facts = case["public_decision_contract"].get("missing_facts", [])
    results.append(
        _rule(
            "R12",
            "Evidence-value trigger",
            "DEGRADED",
            bool(missing_facts),
            f"{len(missing_facts)} named facts could change the route.",
            "Prioritise the smallest evidence request with a plausible route effect; quantify EVSI when cost and value inputs exist.",
            {"named_missing_facts": missing_facts},
        )
    )

    return results
