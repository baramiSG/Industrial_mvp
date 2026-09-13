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
    partner_detail_state,
)


def _rule(
    rule_id: str,
    name: str,
    execution: str,
    fired: bool | None,
    result: str,
    decision_effect: str,
    metrics: dict[str, Any] | None = None,
    *,
    result_code: str,
    decision_effect_code: str,
    result_values: dict[str, str] | None = None,
    effect_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "name": name,
        "execution": execution,
        "fired": fired,
        "result": result,
        "decision_effect": decision_effect,
        "metrics": metrics or {},
        "result_code": result_code,
        "decision_effect_code": decision_effect_code,
        "result_values": result_values or {},
        "effect_values": effect_values or {},
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
    *,
    result_code: str,
    decision_effect_code: str,
    result_values: dict[str, str] | None = None,
    effect_values: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "name": name,
        "execution": execution,
        "fired": fired,
        "result": result,
        "decision_effect": decision_effect,
        "metrics": metrics,
        "result_code": result_code,
        "decision_effect_code": decision_effect_code,
        "result_values": result_values or {},
        "effect_values": effect_values or {},
        "synthetic_flag": True,
        "scenario_id": scenario["scenario_id"],
        "source": scenario["source"],
        "evidence_class": scenario["evidence_class"],
        "display_label": scenario["display_label"],
        "display_labels": synthetic_display_labels(),
        "basis": "synthetic",
    }


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

    rows: list[dict[str, Any]] = []

    r5_config = rule_config["R5"]
    flows = inputs.get("production_and_retained_flows")
    latest_trade = max(public_case.get("trade", []), key=lambda row: row["year"])
    flow_block: dict[str, Any] = {}
    if isinstance(flows, dict):
        flow_block = {
            "domestic_production_kt": flows.get("domestic_production_kt"),
            "retained_imports_kt": flows.get("retained_imports_kt"),
            "domestic_origin_exports_kt": flows.get(
                "domestic_origin_exports_kt"
            ),
            "reexports_kt": flows.get("reexports_kt"),
        }
    flow_metrics = domestic_flow_metrics(latest_trade, flow_block)
    penetration = _domestic_penetration_full_precision(
        latest_trade,
        flow_block,
    )
    production_kt = _numeric_or_none(flows.get("domestic_production_kt")) if isinstance(flows, dict) else None
    retained_kt = _numeric_or_none(flows.get("retained_imports_kt")) if isinstance(flows, dict) else None
    imports_kt = _numeric_or_none(latest_trade.get("imports_kt"))
    verified_present = bool(
        public_case.get("domestic_capability", {}).get("verified_present")
    )
    r5_threshold = float(
        r5_config["retained_import_share_of_apparent_consumption"]
    )
    if penetration is None:
        r5_fired: bool | None = None
        r5_execution = "DISABLED"
        r5_result = (
            "Synthetic retained-flow inputs are absent; R5 is not calculable."
        )
    else:
        r5_fired = verified_present and penetration >= r5_threshold
        r5_execution = "FULL"
        r5_result = (
            "Synthetic retained-import penetration meets the configured R5 "
            "threshold."
            if r5_fired
            else "Synthetic retained-import penetration does not meet the "
            "configured R5 threshold."
        )
    r5_metrics = {
        "retained_imports_kt": (
            retained_kt if retained_kt is not None else NOT_CALCULABLE
        ),
        "domestic_production_kt": (
            production_kt if production_kt is not None else NOT_CALCULABLE
        ),
        "imports_kt": (
            imports_kt if imports_kt is not None else NOT_CALCULABLE
        ),
        "retained_import_penetration": (
            penetration if penetration is not None else NOT_CALCULABLE
        ),
        "apparent_consumption_kt": flow_metrics.get(
            "apparent_consumption_kt"
        ),
        "minimum_retained_import_penetration": r5_threshold,
    }
    if penetration is None:
        r5_row = _synthetic_rule(
            scenario,
            "R5",
            "Retained import penetration",
            r5_execution,
            r5_fired,
            r5_result,
            "Use only when production and retained-flow blocks are declared.",
            r5_metrics,
            result_code="SYNTHETIC_INPUTS_ABSENT",
            decision_effect_code="SYNTHETIC_DECLARED_BLOCKS_ONLY",
        )
    elif r5_fired:
        r5_row = _synthetic_rule(
            scenario,
            "R5",
            "Retained import penetration",
            r5_execution,
            r5_fired,
            r5_result,
            "Use only when production and retained-flow blocks are declared.",
            r5_metrics,
            result_code="SYNTHETIC_PENETRATION_FIRED",
            decision_effect_code="SYNTHETIC_DECLARED_BLOCKS_ONLY",
        )
    else:
        r5_row = _synthetic_rule(
            scenario,
            "R5",
            "Retained import penetration",
            r5_execution,
            r5_fired,
            r5_result,
            "Use only when production and retained-flow blocks are declared.",
            r5_metrics,
            result_code="SYNTHETIC_PENETRATION_NOT_FIRED",
            decision_effect_code="SYNTHETIC_DECLARED_BLOCKS_ONLY",
        )
    rows.append(r5_row)

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
    r6_effect = (
        "Use as a DEGRADED capacity-pressure signal only; "
        "it cannot by itself support ADVANCE without a "
        "sustained period."
    )
    r6_metrics = {
        "effective_utilisation": (
            utilisation if utilisation is not None else NOT_CALCULABLE
        ),
        "minimum_effective_utilisation": float(
            r6_config["minimum_effective_utilisation"]
        ),
        "target_spec_demand_kt": (
            target_demand if target_demand is not None else NOT_CALCULABLE
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
        "shortage_denominator": "effective_qualified_capacity_kt",
        "minimum_spec_matched_shortage": float(
            r6_config["minimum_spec_matched_shortage"]
        ),
        "sustained_period": NOT_CALCULABLE,
    }
    if r6_fired is True:
        r6_row = _synthetic_rule(
            scenario,
            "R6",
            "Capacity pressure",
            r6_execution,
            r6_fired,
            r6_result,
            r6_effect,
            r6_metrics,
            result_code="SYNTHETIC_PRESSURE_FIRED",
            decision_effect_code="SYNTHETIC_DEGRADED_SIGNAL_ONLY",
        )
    elif r6_fired is False:
        r6_row = _synthetic_rule(
            scenario,
            "R6",
            "Capacity pressure",
            r6_execution,
            r6_fired,
            r6_result,
            r6_effect,
            r6_metrics,
            result_code="SYNTHETIC_PRESSURE_NOT_FIRED",
            decision_effect_code="SYNTHETIC_DEGRADED_SIGNAL_ONLY",
        )
    else:
        r6_row = _synthetic_rule(
            scenario,
            "R6",
            "Capacity pressure",
            r6_execution,
            r6_fired,
            r6_result,
            r6_effect,
            r6_metrics,
            result_code="SYNTHETIC_INPUTS_UNAVAILABLE",
            decision_effect_code="SYNTHETIC_DEGRADED_SIGNAL_ONLY",
        )
    rows.append(r6_row)

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
    r7_effect = (
        "Test no-support, market linkage, procurement, or "
        "barrier removal only when equivalence and latent "
        "capacity are established."
    )
    r7_metrics = {
        "effective_utilisation": (
            utilisation if utilisation is not None else NOT_CALCULABLE
        ),
        "maximum_effective_utilisation": maximum_utilisation,
        "specification_equivalence": (
            equivalence_value if equivalence_known else NOT_CALCULABLE
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
    }
    if r7_fired is True:
        r7_row = _synthetic_rule(
            scenario,
            "R7",
            "Latent domestic capacity",
            r7_execution,
            r7_fired,
            r7_result,
            r7_effect,
            r7_metrics,
            result_code="SYNTHETIC_LATENT_FIRED",
            decision_effect_code="SYNTHETIC_TEST_ROUTES_WHEN_ESTABLISHED",
        )
    elif r7_fired is False:
        r7_row = _synthetic_rule(
            scenario,
            "R7",
            "Latent domestic capacity",
            r7_execution,
            r7_fired,
            r7_result,
            r7_effect,
            r7_metrics,
            result_code="SYNTHETIC_LATENT_NOT_FIRED",
            decision_effect_code="SYNTHETIC_TEST_ROUTES_WHEN_ESTABLISHED",
        )
    else:
        r7_row = _synthetic_rule(
            scenario,
            "R7",
            "Latent domestic capacity",
            r7_execution,
            r7_fired,
            r7_result,
            r7_effect,
            r7_metrics,
            result_code="SYNTHETIC_LATENT_NOT_CALCULABLE",
            decision_effect_code="SYNTHETIC_TEST_ROUTES_WHEN_ESTABLISHED",
        )
    rows.append(r7_row)

    r8_config = rule_config["R8"]
    economics = inputs.get("economics")
    base_demand = (
        _numeric_or_none(demand.get("base_demand_kt"))
        if isinstance(demand, dict)
        else None
    )
    commitment_probability = (
        _numeric_or_none(demand.get("commitment_probability"))
        if isinstance(demand, dict)
        else None
    )
    committed = _numeric_or_none(demand.get("committed_demand_kt"))
    mes = (
        _numeric_or_none(economics.get("minimum_efficient_scale_kt"))
        if isinstance(economics, dict)
        else None
    )
    probability_adjusted = (
        committed * commitment_probability
        if committed is not None and commitment_probability is not None
        else None
    )
    addition = (
        probability_adjusted / base_demand
        if probability_adjusted is not None
        and base_demand is not None
        and base_demand > 0
        else None
    )
    mes_fill = (
        probability_adjusted / mes
        if probability_adjusted is not None
        and mes is not None
        and mes > 0
        else None
    )
    min_addition = float(
        r8_config["minimum_probability_adjusted_demand_addition"]
    )
    min_mes_fill = float(r8_config["minimum_mes_fill"])
    addition_computable = addition is not None
    mes_computable = mes_fill is not None
    if addition_computable and mes_computable:
        r8_execution = "FULL"
        r8_fired = addition >= min_addition or mes_fill >= min_mes_fill
    elif addition_computable or mes_computable:
        r8_execution = "DEGRADED"
        r8_fired = (
            (addition is not None and addition >= min_addition)
            if addition_computable
            else (mes_fill is not None and mes_fill >= min_mes_fill)
        )
    else:
        r8_execution = "DISABLED"
        r8_fired = None
    rows.append(
        _synthetic_rule(
            scenario,
            "R8",
            "Committed future demand",
            r8_execution,
            r8_fired,
            (
                "Committed and announced layers are disclosed, but "
                "base demand, commitment probability, and minimum "
                "efficient scale govern R8 calculability."
            ),
            (
                "Do not infer probability-adjusted demand addition "
                "or MES fill; keep committed and announced demand "
                "separate."
            ),
            {
                "base_demand_kt": (
                    base_demand if base_demand is not None else NOT_CALCULABLE
                ),
                "committed_demand_kt": (
                    committed if committed is not None else NOT_CALCULABLE
                ),
                "announced_demand_kt": (
                    demand.get("announced_demand_kt")
                    if _numeric_or_none(demand.get("announced_demand_kt"))
                    is not None
                    else NOT_CALCULABLE
                ),
                "target_spec_demand_kt": (
                    target_demand if target_demand is not None else NOT_CALCULABLE
                ),
                "downside_demand_kt": (
                    demand.get("downside_demand_kt")
                    if _numeric_or_none(demand.get("downside_demand_kt"))
                    is not None
                    else NOT_CALCULABLE
                ),
                "commitment_probability": (
                    commitment_probability
                    if commitment_probability is not None
                    else NOT_CALCULABLE
                ),
                "probability_adjusted_committed_demand_kt": (
                    round(probability_adjusted, 6)
                    if probability_adjusted is not None
                    else NOT_CALCULABLE
                ),
                "probability_adjusted_demand_addition": (
                    round(addition, 6)
                    if addition is not None
                    else NOT_CALCULABLE
                ),
                "minimum_probability_adjusted_demand_addition": min_addition,
                "minimum_efficient_scale_kt": (
                    mes if mes is not None else NOT_CALCULABLE
                ),
                "mes_fill": (
                    round(mes_fill, 6)
                    if mes_fill is not None
                    else NOT_CALCULABLE
                ),
                "minimum_mes_fill": min_mes_fill,
            },
            result_code="SYNTHETIC_LAYERS_DISCLOSED",
            decision_effect_code="SYNTHETIC_DO_NOT_INFER_ADDITION",
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
        result_code="POSITIVE_YEARS_OBSERVED",
        decision_effect_code="INVESTIGATE_ONLY_CONFIDENCE_CAPPED",
        result_values={"positive_year_count": str(len(positive_years))},
        effect_values={"confidence_cap": str(confidence_cap)},
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
            result_code="INPUTS_UNAVAILABLE",
            decision_effect_code="NO_INFERENCE",
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
    result = (
        "Quantity-led expansion signal fires."
        if fired
        else "Value movement is not quantity-led under the configured test."
    )
    metrics = {
        "from_year": previous["year"],
        "to_year": latest["year"],
        "observed_span_years": years,
        "delta_ln_value": round(delta_v, 4),
        "delta_ln_quantity": round(delta_q, 4),
        "delta_ln_unit_value": round(delta_uv, 4),
        "quantity_contribution_share": round(share, 4),
        "quantity_cagr": round(quantity_cagr, 4),
    }
    if fired:
        return _rule(
            "R2",
            "Quantity-led expansion",
            "FULL",
            fired,
            result,
            "Separate structural volume growth from price movement.",
            metrics,
            result_code="FIRED",
            decision_effect_code="SEPARATE_VOLUME_FROM_PRICE",
        )
    return _rule(
        "R2",
        "Quantity-led expansion",
        "FULL",
        fired,
        result,
        "Separate structural volume growth from price movement.",
        metrics,
        result_code="NOT_QUANTITY_LED",
        decision_effect_code="SEPARATE_VOLUME_FROM_PRICE",
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
    effect = (
        "No concentration inference."
        if execution == "DISABLED"
        else (
            "Generate a resilience/diversification review, not an "
            "automatic localisation recommendation."
        )
    )
    metrics = {
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
    }
    if execution == "DISABLED":
        detail = partner_detail_state(case)
        if (
            detail is not None
            and detail[0] == "PARTNER_DETAIL_MISSING"
            and detail[1] is not None
        ):
            reason = detail[1]
            return _rule(
                "R3",
                "Supplier concentration",
                execution,
                fired,
                (
                    f"Partner detail MISSING ({reason}): value- and "
                    "quantity-basis partner concentration are "
                    "NOT_CALCULABLE because no partner rows were parsed — "
                    "missing evidence, not zero trade."
                ),
                effect,
                metrics,
                result_code="PARTNER_DETAIL_MISSING",
                decision_effect_code="NO_CONCENTRATION_INFERENCE",
                result_values={"partner_detail_reason": reason},
            )
        if (
            detail is not None
            and detail[0] == "PARTNER_TRADE_OBSERVED_ZERO"
        ):
            return _rule(
                "R3",
                "Supplier concentration",
                execution,
                fired,
                (
                    "Partner trade OBSERVED ZERO: value- and "
                    "quantity-basis partner concentration are "
                    "NOT_CALCULABLE because zero partner rows were observed."
                ),
                effect,
                metrics,
                result_code="PARTNER_TRADE_OBSERVED_ZERO",
                decision_effect_code="NO_CONCENTRATION_INFERENCE",
            )
        return _rule(
            "R3",
            "Supplier concentration",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="BOTH_BASES_NOT_CALCULABLE",
            decision_effect_code="NO_CONCENTRATION_INFERENCE",
        )
    if value_fired and not quantity_full:
        return _rule(
            "R3",
            "Supplier concentration",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="VALUE_CONCENTRATED_QUANTITY_NOT_CALCULABLE",
            decision_effect_code="RESILIENCE_REVIEW",
        )
    if quantity_fired and not value_full:
        return _rule(
            "R3",
            "Supplier concentration",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="QUANTITY_CONCENTRATED_VALUE_NOT_CALCULABLE",
            decision_effect_code="RESILIENCE_REVIEW",
        )
    if fired:
        return _rule(
            "R3",
            "Supplier concentration",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="CONCENTRATED_ON_CALCULABLE_BASIS",
            decision_effect_code="RESILIENCE_REVIEW",
        )
    return _rule(
        "R3",
        "Supplier concentration",
        execution,
        fired,
        result,
        effect,
        metrics,
        result_code="THRESHOLDS_NOT_MET",
        decision_effect_code="RESILIENCE_REVIEW",
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
    if metrics["status"] == "CALCULABLE":
        return _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            execution,
            fired,
            result,
            "Open specification research only; no grade conclusion.",
            metrics,
            result_code="DESCRIPTIVE_DISPERSION",
            decision_effect_code="SPECIFICATION_RESEARCH_ONLY",
        )
    if metrics["status"] == "DISCLOSED":
        return _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            execution,
            fired,
            result,
            "Open specification research only; no grade conclusion.",
            metrics,
            result_code="DISCLOSED_DISPERSION",
            decision_effect_code="SPECIFICATION_RESEARCH_ONLY",
        )
    detail = partner_detail_state(case)
    if (
        detail is not None
        and detail[0] == "PARTNER_DETAIL_MISSING"
        and detail[1] is not None
    ):
        reason = detail[1]
        return _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            execution,
            fired,
            (
                f"Partner detail MISSING ({reason}): comparable annual "
                "partner coverage is unavailable — missing evidence, not "
                "zero trade; R4-D is not calculable."
            ),
            "Open specification research only; no grade conclusion.",
            metrics,
            result_code="PARTNER_DETAIL_MISSING",
            decision_effect_code="SPECIFICATION_RESEARCH_ONLY",
            result_values={"partner_detail_reason": reason},
        )
    if (
        detail is not None
        and detail[0] == "PARTNER_TRADE_OBSERVED_ZERO"
    ):
        return _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            execution,
            fired,
            (
                "Partner trade OBSERVED ZERO: no partner unit values exist; "
                "R4-D is not calculable."
            ),
            "Open specification research only; no grade conclusion.",
            metrics,
            result_code="PARTNER_TRADE_OBSERVED_ZERO",
            decision_effect_code="SPECIFICATION_RESEARCH_ONLY",
        )
    return _rule(
        "R4-D",
        "Unit-value dispersion — degraded",
        execution,
        fired,
        result,
        "Open specification research only; no grade conclusion.",
        metrics,
        result_code="COVERAGE_INSUFFICIENT",
        decision_effect_code="SPECIFICATION_RESEARCH_ONLY",
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
    effect = (
        "Test specification, qualification, capacity, price, "
        "application and allocation mismatch."
    )
    if execution == "FULL" and fired:
        return _rule(
            "R5",
            "Domestic supply plus continued imports",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="PENETRATION_FIRED",
            decision_effect_code="TEST_MISMATCH_DIMENSIONS",
        )
    if execution == "FULL":
        return _rule(
            "R5",
            "Domestic supply plus continued imports",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="PENETRATION_NOT_FIRED",
            decision_effect_code="TEST_MISMATCH_DIMENSIONS",
        )
    if execution == "DEGRADED" and fired:
        return _rule(
            "R5",
            "Domestic supply plus continued imports",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="COEXISTENCE_FIRED",
            decision_effect_code="TEST_MISMATCH_DIMENSIONS",
        )
    if execution == "DEGRADED":
        return _rule(
            "R5",
            "Domestic supply plus continued imports",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="COEXISTENCE_NOT_MET",
            decision_effect_code="TEST_MISMATCH_DIMENSIONS",
        )
    return _rule(
        "R5",
        "Domestic supply plus continued imports",
        execution,
        fired,
        result,
        effect,
        metrics,
        result_code="INPUTS_UNAVAILABLE",
        decision_effect_code="TEST_MISMATCH_DIMENSIONS",
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
    result = (
        "A verified Saudi plant is in the same process family with "
        "additional capability signals."
        if fired
        else "No defensible coarse adjacency signal."
    )
    effect = (
        "Open the full line-level capability assessment; do not "
        "publish D* from screening alone."
    )
    metrics = {
        "same_process_family": (
            same_family
            if isinstance(same_family, bool)
            else NOT_CALCULABLE
        ),
        "qualifying_signal_count": qualifying_count,
        "known_hard_gate_failure": known_failure,
    }
    if fired:
        return _rule(
            "R9-S",
            "Coarse incumbent adjacency screen",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="ADJACENT_PLANT_WITH_SIGNALS",
            decision_effect_code="OPEN_LINE_LEVEL_ASSESSMENT",
        )
    return _rule(
        "R9-S",
        "Coarse incumbent adjacency screen",
        execution,
        fired,
        result,
        effect,
        metrics,
        result_code="NO_DEFENSIBLE_SIGNAL",
        decision_effect_code="OPEN_LINE_LEVEL_ASSESSMENT",
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
    metrics = {
        "criticality_status": status,
        "criticality_evidence_id": evidence_id,
    }
    if isinstance(designation, dict):
        return _rule(
            "R10",
            "Strategic criticality",
            execution,
            fired,
            result,
            "Keep commercial viability and strategic value separate.",
            metrics,
            result_code="DESIGNATED",
            decision_effect_code="SEPARATE_VIABILITY_FROM_STRATEGY",
        )
    if r3.get("fired") is True:
        return _rule(
            "R10",
            "Strategic criticality",
            execution,
            fired,
            result,
            "Keep commercial viability and strategic value separate.",
            metrics,
            result_code="RESILIENCE_REVIEW_WARRANTED",
            decision_effect_code="SEPARATE_VIABILITY_FROM_STRATEGY",
        )
    return _rule(
        "R10",
        "Strategic criticality",
        execution,
        fired,
        result,
        "Keep commercial viability and strategic value separate.",
        metrics,
        result_code="NO_DESIGNATION",
        decision_effect_code="SEPARATE_VIABILITY_FROM_STRATEGY",
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
    effect = (
        "Reject generic support or move only a named specialty "
        "exception to investigation."
    )
    metrics = {
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
    }
    if fired:
        assert isinstance(compatibility_ratio, (int, float))
        return _rule(
            "R11",
            "Economic exclusion / generic-capacity warning",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="GENERIC_CAPACITY_FIRED",
            decision_effect_code="REJECT_GENERIC_OR_NAMED_EXCEPTION",
            result_values={"ratio": f"{compatibility_ratio:.1f}"},
        )
    if ratio["status"] == "CALCULABLE" and established:
        assert computed is not None
        return _rule(
            "R11",
            "Economic exclusion / generic-capacity warning",
            execution,
            fired,
            result,
            effect,
            metrics,
            result_code="WARNING_THRESHOLD_NOT_MET",
            decision_effect_code="REJECT_GENERIC_OR_NAMED_EXCEPTION",
            result_values={"ratio": f"{computed:.4f}"},
        )
    return _rule(
        "R11",
        "Economic exclusion / generic-capacity warning",
        execution,
        fired,
        result,
        effect,
        metrics,
        result_code="NOT_CALCULABLE",
        decision_effect_code="REJECT_GENERIC_OR_NAMED_EXCEPTION",
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
            result_code="IDENTITY_FROZEN",
            decision_effect_code="CONTINUE_SCREENING",
            result_values={
                "hs_revision": str(case["opportunity"]["hs_revision"]),
                "hs6": str(case["opportunity"]["hs6"]),
            },
        ),
    ]
    if quality.get("missing_years"):
        results.append(
            _rule(
                "R1-F",
                "Persistent retained exposure — full",
                "DISABLED",
                None,
                (
                    "Full continuity is unavailable and gross flows are not "
                    "retained imports."
                ),
                "Do not claim the full persistence rule.",
                {"missing_years": quality.get("missing_years", [])},
                result_code="CONTINUITY_UNAVAILABLE",
                decision_effect_code="DO_NOT_CLAIM_FULL_PERSISTENCE",
            )
        )
    else:
        results.append(
            _rule(
                "R1-F",
                "Persistent retained exposure — full",
                "FULL",
                False,
                "Full persistence test did not fire.",
                "Do not claim the full persistence rule.",
                {"missing_years": []},
                result_code="NOT_FIRED",
                decision_effect_code="DO_NOT_CLAIM_FULL_PERSISTENCE",
            )
        )
    results.extend(
        [
            _r1d_rule(case, thresholds["R1_D"]),
            _r2_rule(case, thresholds["R2"]),
        ]
    )
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
                result_code="CELLS_UNAVAILABLE",
                decision_effect_code="NO_CLUSTERS_OR_GRADES",
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
                result_code="NOT_PUBLIC",
                decision_effect_code="OBTAIN_LINE_LEVEL_INPUTS",
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
                result_code="NOT_ESTABLISHED_PUBLICLY",
                decision_effect_code="DO_NOT_ASSUME_LATENT_CAPACITY",
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
                result_code="COMMITTED_DEMAND_UNAVAILABLE",
                decision_effect_code="KEEP_DEMAND_LAYERS_SEPARATE",
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
            result_code="NAMED_FACTS_COULD_CHANGE_ROUTE",
            decision_effect_code="PRIORITISE_SMALLEST_REQUEST",
            result_values={
                "named_fact_count": str(len(missing_facts)),
            },
        )
    )
    return results


def evaluate_rules(case: dict[str, Any]) -> list[dict[str, Any]]:
    return _evaluate_rules_v2(case)
