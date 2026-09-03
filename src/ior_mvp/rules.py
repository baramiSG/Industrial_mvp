from __future__ import annotations

import math
from typing import Any

from .config import thresholds_config
from .evidence import (
    EvidenceIntegrityError,
    synthetic_display_labels,
)
from .evidence_needs import derive_evidence_needs
from .public_snapshot import has_known_hard_gate_failure
from .trade_metrics import (
    UNAVAILABLE,
    _concentration_predicate_values,
    _domestic_penetration_full_precision,
    _export_import_ratio_full_precision,
    compound_annual_growth,
    concentration_metrics,
    degraded_dispersion_metrics,
    domestic_flow_metrics,
    established_domestic_nameplate,
    export_import_value_ratio,
    latest_usable_trade_pair,
)


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


def _synthetic_rule(
    scenario: dict[str, Any],
    rule_id: str,
    name: str,
    execution: str,
    fired: bool | None,
    result: str,
    decision_effect: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    row = _rule(
        rule_id,
        name,
        execution,
        fired,
        result,
        decision_effect,
        metrics,
    )
    row.update(
        {
            "synthetic_flag": True,
            "scenario_id": scenario["scenario_id"],
            "source": scenario["source"],
            "evidence_class": scenario["evidence_class"],
            "display_label": scenario["display_label"],
            "display_labels": synthetic_display_labels(),
            "basis": "synthetic",
        }
    )
    return row


def _numeric_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def evaluate_simulated_rules(
    scenario: dict[str, Any],
    public_case: dict[str, Any],
    capacity: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[dict[str, Any]]:
    opportunity = public_case.get("opportunity")
    public_opportunity_id = (
        opportunity.get("id")
        if isinstance(opportunity, dict)
        else None
    )
    if scenario.get("opportunity_id") != public_opportunity_id:
        raise EvidenceIntegrityError(
            "Synthetic rule evaluation opportunity_id does not match "
            "the public case"
        )

    inputs = scenario["synthetic_inputs"]
    demand = inputs.get("demand")
    line = inputs.get("plant_line")
    if not isinstance(demand, dict) or not isinstance(line, dict):
        raise EvidenceIntegrityError(
            "Synthetic rule evaluation requires demand and plant_line "
            "mappings"
        )

    rule_config = thresholds["rules"]
    target_demand = _numeric_or_none(
        demand.get("target_spec_demand_kt")
    )
    utilisation = _numeric_or_none(
        line.get("current_utilisation")
    )
    capacity_key = "effective_qualified_capacity_kt"
    effective_capacity = _numeric_or_none(
        capacity.get(capacity_key)
    )
    if effective_capacity is None:
        capacity_key = "formula_capacity_kt"
        effective_capacity = _numeric_or_none(
            capacity.get(capacity_key)
        )

    r6_config = rule_config["R6"]
    shortage_ratio = (
        (target_demand - effective_capacity) / effective_capacity
        if target_demand is not None
        and effective_capacity is not None
        and effective_capacity > 0
        else None
    )
    r6_fired = (
        utilisation
        >= float(r6_config["minimum_effective_utilisation"])
        and shortage_ratio
        >= float(r6_config["minimum_spec_matched_shortage"])
        if utilisation is not None and shortage_ratio is not None
        else None
    )
    r6_execution = (
        "DEGRADED" if r6_fired is not None else "DISABLED"
    )
    if r6_fired is True:
        r6_result = (
            "Synthetic utilisation and shortage proxy meet the "
            "configured R6 thresholds; sustained period is "
            "NOT_CALCULABLE."
        )
    elif r6_fired is False:
        r6_result = (
            "Synthetic R6 utilisation/shortage proxy does not meet "
            "both configured thresholds; sustained period is "
            "NOT_CALCULABLE."
        )
    else:
        r6_result = (
            "Synthetic utilisation or effective qualified capacity "
            "is unavailable; R6 is not calculable."
        )
    rows = [
        _synthetic_rule(
            scenario,
            "R6",
            "Capacity pressure",
            r6_execution,
            r6_fired,
            r6_result,
            (
                "Use as a DEGRADED capacity-pressure signal only; "
                "it cannot by itself support ADVANCE without a "
                "sustained period."
            ),
            {
                "effective_utilisation": (
                    utilisation
                    if utilisation is not None
                    else NOT_CALCULABLE
                ),
                "minimum_effective_utilisation": float(
                    r6_config["minimum_effective_utilisation"]
                ),
                "target_spec_demand_kt": (
                    target_demand
                    if target_demand is not None
                    else NOT_CALCULABLE
                ),
                "effective_qualified_capacity_kt": (
                    effective_capacity
                    if effective_capacity is not None
                    else NOT_CALCULABLE
                ),
                "effective_capacity_source_key": capacity_key,
                "shortage_ratio": (
                    round(shortage_ratio, 4)
                    if shortage_ratio is not None
                    else NOT_CALCULABLE
                ),
                "shortage_denominator": (
                    "effective_qualified_capacity_kt"
                ),
                "minimum_spec_matched_shortage": float(
                    r6_config["minimum_spec_matched_shortage"]
                ),
                "sustained_period": NOT_CALCULABLE,
            },
        )
    ]

    r7_config = rule_config["R7"]
    maximum_utilisation = float(
        r7_config["maximum_effective_utilisation"]
    )
    equivalence = inputs.get("equivalence")
    equivalence_value = (
        equivalence.get("domestic_grade_equivalent")
        if isinstance(equivalence, dict)
        else None
    )
    equivalence_known = isinstance(equivalence_value, bool)
    equivalence_required = bool(
        r7_config["require_specification_equivalence"]
    )
    if utilisation is None:
        r7_fired: bool | None = None
    elif utilisation > maximum_utilisation:
        r7_fired = False
    elif equivalence_required and not equivalence_known:
        r7_fired = None
    else:
        r7_fired = (
            utilisation <= maximum_utilisation
            and (
                not equivalence_required
                or equivalence_value is True
            )
        )
    if utilisation is None:
        r7_execution = "DISABLED"
    elif equivalence_known:
        r7_execution = "FULL"
    else:
        r7_execution = "DEGRADED"
    if r7_fired is True:
        r7_result = (
            "Synthetic utilisation and specification equivalence "
            "meet the configured latent-capacity test."
        )
    elif r7_fired is False:
        r7_result = (
            "Synthetic utilisation/equivalence does not meet the "
            "configured latent-capacity test."
        )
    else:
        r7_result = (
            "Synthetic latent capacity is not calculable because a "
            "required utilisation or equivalence input is absent."
        )
    rows.append(
        _synthetic_rule(
            scenario,
            "R7",
            "Latent domestic capacity",
            r7_execution,
            r7_fired,
            r7_result,
            (
                "Test no-support, market linkage, procurement, or "
                "barrier removal only when equivalence and latent "
                "capacity are established."
            ),
            {
                "effective_utilisation": (
                    utilisation
                    if utilisation is not None
                    else NOT_CALCULABLE
                ),
                "maximum_effective_utilisation": maximum_utilisation,
                "specification_equivalence": (
                    equivalence_value
                    if equivalence_known
                    else NOT_CALCULABLE
                ),
                "qualified_available_kt": (
                    equivalence.get("qualified_available_kt")
                    if isinstance(equivalence, dict)
                    and _numeric_or_none(
                        equivalence.get("qualified_available_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
            },
        )
    )

    r8_config = rule_config["R8"]
    rows.append(
        _synthetic_rule(
            scenario,
            "R8",
            "Committed future demand",
            "DISABLED",
            None,
            (
                "Committed and announced layers are disclosed, but "
                "base demand, commitment probability, and minimum "
                "efficient scale are absent."
            ),
            (
                "Do not infer probability-adjusted demand addition "
                "or MES fill; keep committed and announced demand "
                "separate."
            ),
            {
                "base_demand_kt": NOT_CALCULABLE,
                "committed_demand_kt": (
                    demand.get("committed_demand_kt")
                    if _numeric_or_none(
                        demand.get("committed_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "announced_demand_kt": (
                    demand.get("announced_demand_kt")
                    if _numeric_or_none(
                        demand.get("announced_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "target_spec_demand_kt": (
                    target_demand
                    if target_demand is not None
                    else NOT_CALCULABLE
                ),
                "downside_demand_kt": (
                    demand.get("downside_demand_kt")
                    if _numeric_or_none(
                        demand.get("downside_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "commitment_probability": NOT_CALCULABLE,
                "probability_adjusted_committed_demand_kt": (
                    NOT_CALCULABLE
                ),
                "probability_adjusted_demand_addition": (
                    NOT_CALCULABLE
                ),
                "minimum_probability_adjusted_demand_addition": (
                    float(
                        r8_config[
                            "minimum_probability_adjusted_demand_addition"
                        ]
                    )
                ),
                "minimum_efficient_scale_kt": NOT_CALCULABLE,
                "mes_fill": NOT_CALCULABLE,
                "minimum_mes_fill": float(
                    r8_config["minimum_mes_fill"]
                ),
            },
        )
    )
    return rows


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
    established_domestic_capability: bool,
    export_import_value_ratio: float | None,
    rule_config: dict[str, Any],
) -> bool:
    return bool(
        established_domestic_capability
        and export_import_value_ratio is not None
        and export_import_value_ratio
        > float(rule_config["generic_capacity_export_import_value_ratio"])
    )


def _r1d_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    trade = case.get("trade")
    rows = trade if isinstance(trade, list) else []
    positive_years = [
        row["year"]
        for row in rows
        if isinstance(row, dict)
        and isinstance(row.get("year"), int)
        and (_numeric_or_none(row.get("imports_usd_m")) or 0) > 0
    ]
    fired = r1d_fires(positive_years, rule_config)
    confidence_cap = rule_config["confidence_cap"]
    return _rule(
        "R1-D",
        "Persistence signal — degraded",
        "DEGRADED",
        fired,
        (
            f"{len(positive_years)} positive observed years within the "
            "configured window; no interpolation used."
        ),
        (
            "Generate INVESTIGATE only; confidence capped at "
            f"{confidence_cap}."
        ),
        {
            "positive_years": positive_years,
            "confidence_cap": confidence_cap,
        },
    )


def _r2_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    trade = case.get("trade")
    pair = latest_usable_trade_pair(
        trade if isinstance(trade, list) else []
    )
    if pair is None:
        return _rule(
            "R2",
            "Quantity-led expansion",
            "DISABLED",
            None,
            "Comparable value and quantity observations are unavailable.",
            "No inference.",
        )
    previous, latest = pair
    previous_value = float(previous["imports_usd_m"])
    latest_value = float(latest["imports_usd_m"])
    previous_quantity = float(previous["imports_kt"])
    latest_quantity = float(latest["imports_kt"])
    delta_v = log_change(latest_value, previous_value)
    delta_q = log_change(latest_quantity, previous_quantity)
    latest_uv = _numeric_or_none(latest.get("import_uv_usd_t"))
    previous_uv = _numeric_or_none(previous.get("import_uv_usd_t"))
    if latest_uv is None or latest_uv <= 0:
        latest_uv = latest_value * 1000 / latest_quantity
    if previous_uv is None or previous_uv <= 0:
        previous_uv = previous_value * 1000 / previous_quantity
    delta_uv = log_change(latest_uv, previous_uv)
    share = quantity_contribution_share(delta_q, delta_uv)
    years = int(latest["year"]) - int(previous["year"])
    quantity_cagr = compound_annual_growth(
        latest_quantity,
        previous_quantity,
        years,
    )
    fired = r2_fires(
        delta_q,
        share,
        quantity_cagr,
        rule_config,
    )
    return _rule(
        "R2",
        "Quantity-led expansion",
        "FULL",
        fired,
        (
            "Quantity-led expansion signal fires."
            if fired
            else "Value movement is not quantity-led under the configured test."
        ),
        "Separate structural volume growth from price movement.",
        {
            "from_year": previous["year"],
            "to_year": latest["year"],
            "observed_span_years": years,
            "delta_ln_value": round(delta_v, 4),
            "delta_ln_quantity": round(delta_q, 4),
            "delta_ln_unit_value": round(delta_uv, 4),
            "quantity_contribution_share": round(share, 4),
            "quantity_cagr": round(quantity_cagr, 4),
        },
    )


def _r3_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    value_metrics = concentration_metrics(case, "value")
    quantity_metrics = concentration_metrics(case, "quantity")
    value_hhi, value_largest = _concentration_predicate_values(
        case,
        "value",
        value_metrics,
    )
    quantity_hhi, quantity_largest = _concentration_predicate_values(
        case,
        "quantity",
        quantity_metrics,
    )
    value_full = value_metrics["status"] == "FULL"
    quantity_full = quantity_metrics["status"] == "FULL"
    value_fired = (
        r3_fires(
            value_hhi,
            value_largest,
            rule_config,
        )
        if value_full
        else False
    )
    quantity_fired = (
        r3_fires(
            quantity_hhi,
            quantity_largest,
            rule_config,
        )
        if quantity_full
        else False
    )
    if not value_full and not quantity_full:
        execution = "DISABLED"
        fired: bool | None = None
        result = (
            "Value- and quantity-basis partner concentration are "
            "NOT_CALCULABLE."
        )
    else:
        execution = "FULL"
        fired = value_fired or quantity_fired
        if value_fired and not quantity_full:
            result = (
                "External supply is concentrated on the value basis; "
                "quantity concentration is NOT_CALCULABLE."
            )
        elif quantity_fired and not value_full:
            result = (
                "External supply is concentrated on the quantity basis; "
                "value concentration is NOT_CALCULABLE."
            )
        elif fired:
            result = (
                "External supply is concentrated on at least one calculable "
                "basis."
            )
        else:
            result = (
                "Concentration thresholds are not met on the calculable "
                "basis or bases."
            )
    return _rule(
        "R3",
        "Supplier concentration",
        execution,
        fired,
        result,
        (
            "No concentration inference."
            if execution == "DISABLED"
            else (
                "Generate a resilience/diversification review, not an "
                "automatic localisation recommendation."
            )
        ),
        {
            "hhi": value_metrics["hhi"],
            "largest_supplier_share": value_metrics[
                "largest_supplier_share"
            ],
            "top_two_share": value_metrics["top_two_share"],
            "hhi_threshold": float(rule_config["supplier_hhi"]),
            "largest_supplier_threshold": float(
                rule_config["largest_supplier_share"]
            ),
            "value": value_metrics,
            "quantity": quantity_metrics,
        },
    )


def _r4d_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    minimum = float(rule_config["minimum_valid_value_coverage"])
    metrics = degraded_dispersion_metrics(case, minimum)
    if metrics["status"] == "CALCULABLE":
        execution = "DEGRADED"
        fired: bool | None = True
        result = (
            "Comparable annual partner unit values show descriptive "
            "dispersion; no cluster or grade conclusion."
        )
    elif metrics["status"] == "DISCLOSED":
        execution = "DEGRADED"
        fired = True
        result = (
            "A source-attributed annual unit-value dispersion summary "
            "supports a descriptive product-mix signal; no cluster or "
            "grade conclusion."
        )
    else:
        execution = "DISABLED"
        fired = None
        result = (
            "Comparable annual partner coverage is insufficient; "
            "R4-D is not calculable."
        )
    return _rule(
        "R4-D",
        "Unit-value dispersion — degraded",
        execution,
        fired,
        result,
        "Open specification research only; no grade conclusion.",
        metrics,
    )


def _latest_trade_row(case: dict[str, Any]) -> dict[str, Any]:
    trade = case.get("trade")
    if not isinstance(trade, list) or not trade:
        return {}
    dated = [
        row
        for row in trade
        if isinstance(row, dict)
        and isinstance(row.get("year"), int)
        and not isinstance(row.get("year"), bool)
    ]
    return max(dated, key=lambda row: row["year"]) if dated else {}


def _r5_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    latest = _latest_trade_row(case)
    flows = domestic_flow_metrics(latest, case["domestic_flows"])
    threshold = float(
        rule_config["retained_import_share_of_apparent_consumption"]
    )
    penetration = _domestic_penetration_full_precision(
        latest,
        case["domestic_flows"],
    )
    capability = case.get("domestic_capability")
    verified = (
        capability.get("verified_present")
        if isinstance(capability, dict)
        else UNAVAILABLE
    )
    imports_quantity = _numeric_or_none(latest.get("imports_kt"))
    imports_value = _numeric_or_none(latest.get("imports_usd_m"))
    positive_imports = (
        (imports_quantity is not None and imports_quantity > 0)
        or (imports_value is not None and imports_value > 0)
    )
    if penetration is not None:
        execution = "FULL"
        fired: bool | None = (
            verified is True and penetration >= threshold
        )
        result = (
            "Retained import penetration meets the configured mismatch test."
            if fired
            else "The configured retained-import penetration test does not fire."
        )
    elif verified is True and positive_imports:
        execution = "DEGRADED"
        fired = True
        result = (
            "Verified domestic capability coexists with material gross imports."
        )
    elif isinstance(verified, bool) and (
        imports_quantity is not None or imports_value is not None
    ):
        execution = "DEGRADED"
        fired = False
        result = "Coexistence condition not met."
    else:
        execution = "DISABLED"
        fired = None
        result = "Domestic capability or a usable import measure is unavailable."
    metrics = {
        **flows,
        "threshold": threshold,
        "reason": (
            None
            if penetration is not None
            else (
                "Domestic production quantity and retained-import flow are "
                "absent from the frozen public snapshot; gross imports "
                "cannot establish apparent consumption."
            )
        ),
    }
    return _rule(
        "R5",
        "Domestic supply plus continued imports",
        execution,
        fired,
        result,
        (
            "Test specification, qualification, capacity, price, "
            "application and allocation mismatch."
        ),
        metrics,
    )


def _r9s_rule(capability: dict[str, Any]) -> dict[str, Any]:
    same_family = capability.get("same_process_family")
    signals = capability.get("coarse_adjacency_signals")
    qualifying_count = (
        sum(
            1
            for signal in signals
            if isinstance(signal, dict)
            and signal.get("signal_type")
            in {
                "matching_feedstock",
                "core_process",
                "equipment",
                "adjacent_output",
                "relevant_certification",
                "imported_inputs",
            }
            and isinstance(signal.get("evidence_ids"), list)
            and bool(signal["evidence_ids"])
        )
        if isinstance(signals, list)
        else 0
    )
    known_failure = has_known_hard_gate_failure(capability)
    if same_family == UNAVAILABLE:
        execution = "DISABLED"
        fired: bool | None = None
    else:
        execution = "FULL"
        fired = (
            same_family is True
            and qualifying_count > 0
            and not known_failure
        )
    return _rule(
        "R9-S",
        "Coarse incumbent adjacency screen",
        execution,
        fired,
        (
            "A verified Saudi plant is in the same process family with "
            "additional capability signals."
            if fired
            else "No defensible coarse adjacency signal."
        ),
        (
            "Open the full line-level capability assessment; do not "
            "publish D* from screening alone."
        ),
        {
            "same_process_family": (
                same_family
                if isinstance(same_family, bool)
                else NOT_CALCULABLE
            ),
            "qualifying_signal_count": qualifying_count,
            "known_hard_gate_failure": known_failure,
        },
    )


def _r10_rule(
    case: dict[str, Any],
    r3: dict[str, Any],
) -> dict[str, Any]:
    designation = case.get("criticality_designation")
    if isinstance(designation, dict):
        execution = "FULL"
        fired: bool | None = True
        result = (
            "A responsible-authority criticality designation is present."
        )
        status = "DESIGNATED"
        evidence_id = designation.get("evidence_id")
    elif r3.get("fired") is True:
        execution = "DEGRADED"
        fired = True
        result = (
            "A resilience review is warranted by concentration; formal "
            "criticality still requires authority confirmation."
        )
        status = NOT_CALCULABLE
        evidence_id = None
    else:
        execution = "DISABLED"
        fired = None
        result = (
            "No responsible-authority criticality designation is present "
            "in the demo snapshot."
        )
        status = NOT_CALCULABLE
        evidence_id = None
    return _rule(
        "R10",
        "Strategic criticality",
        execution,
        fired,
        result,
        "Keep commercial viability and strategic value separate.",
        {
            "criticality_status": status,
            "criticality_evidence_id": evidence_id,
        },
    )


def _r11_rule(
    case: dict[str, Any],
    rule_config: dict[str, Any],
) -> dict[str, Any]:
    ratio = export_import_value_ratio(_latest_trade_row(case))
    capability = established_domestic_nameplate(
        case["domestic_capability"]
    )
    computed = _export_import_ratio_full_precision(
        _latest_trade_row(case)
    )
    computed_display = ratio["computed_export_import_value_ratio"]
    threshold = float(
        rule_config["generic_capacity_export_import_value_ratio"]
    )
    established = capability["established"] is True
    fired = r11_generic_capacity_fires(
        established,
        computed,
        rule_config,
    )
    execution = (
        "FULL"
        if ratio["status"] == "CALCULABLE" and established
        else "DEGRADED"
    )
    compatibility_ratio = ratio["export_import_value_ratio"]
    if fired:
        assert isinstance(compatibility_ratio, (int, float))
        result = (
            f"Gross exports are {compatibility_ratio:.1f}× imports; "
            "generic new capacity cannot be justified from HS6 imports alone."
        )
    elif ratio["status"] == "CALCULABLE" and established:
        assert computed is not None
        result = (
            f"Gross exports are {computed:.4f}× imports; the configured "
            "generic-capacity warning threshold is not met."
        )
    else:
        result = (
            "Export/import ratio or established nameplate capability is "
            "NOT_CALCULABLE; no generic-capacity exclusion fires."
        )
    return _rule(
        "R11",
        "Economic exclusion / generic-capacity warning",
        execution,
        fired,
        result,
        (
            "Reject generic support or move only a named specialty "
            "exception to investigation."
        ),
        {
            "export_import_value_ratio": compatibility_ratio,
            "export_import_value_ratio_threshold": threshold,
            "computed_export_import_value_ratio": computed_display,
            "disclosed_export_import_value_ratio": ratio[
                "disclosed_export_import_value_ratio"
            ],
            "disclosed_ratio_consistent": ratio[
                "disclosed_ratio_consistent"
            ],
            "ratio_basis": ratio["ratio_basis"],
            "ratio_status": ratio["status"],
            "ratio_reason": ratio["reason"],
            "established_nameplate": capability,
        },
    )


def _evaluate_rules_v2(case: dict[str, Any]) -> list[dict[str, Any]]:
    thresholds = thresholds_config()["rules"]
    quality = case["trade_quality"]
    results: list[dict[str, Any]] = [
        _rule(
            "R0",
            "Identity gate",
            "FULL",
            True,
            (
                f"HS revision {case['opportunity']['hs_revision']} and HS6 "
                f"{case['opportunity']['hs6']} are frozen in the snapshot; "
                "specification/application remains separately gated."
            ),
            (
                "Continue to screening while preserving the unresolved "
                "decision object."
            ),
        ),
        _rule(
            "R1-F",
            "Persistent retained exposure — full",
            "DISABLED" if quality.get("missing_years") else "FULL",
            None if quality.get("missing_years") else False,
            (
                "Full continuity is unavailable and gross flows are not "
                "retained imports."
                if quality.get("missing_years")
                else "Full persistence test did not fire."
            ),
            "Do not claim the full persistence rule.",
            {"missing_years": quality.get("missing_years", [])},
        ),
        _r1d_rule(case, thresholds["R1_D"]),
        _r2_rule(case, thresholds["R2"]),
    ]
    r3 = _r3_rule(case, thresholds["R3"])
    results.extend(
        [
            r3,
            _rule(
                "R4-F",
                "Product-tier heterogeneity — full",
                "DISABLED",
                None,
                "Partner-month × tariff-line cells are unavailable.",
                "Do not fit clusters or claim grades.",
            ),
            _r4d_rule(case, thresholds["R4_D"]),
            _r5_rule(case, thresholds["R5"]),
            _rule(
                "R6",
                "Capacity pressure",
                "DISABLED",
                None,
                (
                    "Effective utilisation and target-specification "
                    "shortage are not public."
                ),
                (
                    "Obtain line-level availability, yield, qualification "
                    "share and allocation."
                ),
            ),
            _rule(
                "R7",
                "Latent domestic capacity",
                "DISABLED",
                None,
                (
                    "Idle qualified capacity and specification equivalence "
                    "are not established publicly."
                ),
                "Do not assume latent capacity.",
            ),
            _rule(
                "R8",
                "Committed future demand",
                "DISABLED",
                None,
                (
                    "Awarded/financed demand at the target specification "
                    "is unavailable."
                ),
                (
                    "Keep base, committed and announced demand separate "
                    "when provided."
                ),
            ),
            _r9s_rule(case["domestic_capability"]),
            _r10_rule(case, r3),
            _r11_rule(case, thresholds["R11"]),
        ]
    )
    evidence_needs = derive_evidence_needs(case, results)
    missing_facts = [
        need["text"] for need in evidence_needs
    ]
    results.append(
        _rule(
            "R12",
            "Evidence-value trigger",
            "DEGRADED",
            bool(missing_facts),
            f"{len(missing_facts)} named facts could change the route.",
            (
                "Prioritise the smallest evidence request with a plausible "
                "route effect; quantify EVSI when cost and value inputs exist."
            ),
            {
                "named_missing_facts": missing_facts,
                "evidence_needs": evidence_needs,
            },
        )
    )
    return results


def evaluate_rules(case: dict[str, Any]) -> list[dict[str, Any]]:
    return _evaluate_rules_v2(case)
