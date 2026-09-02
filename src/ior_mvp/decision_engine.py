from __future__ import annotations

from typing import Any, Literal

from .capability import effective_qualified_capacity, evaluate_capability
from .config import project_config, thresholds_config
from .data_repository import get_public_case, get_synthetic_scenario, public_cases
from .economics import (
    approximate_evsi,
    incremental_national_value,
    minimum_effective_support,
)
from .evidence import (
    assert_real_decision_unchanged,
    isolated_copy,
    synthetic_evidence_rows,
    validate_public_evidence,
    validate_synthetic_scenario,
)
from .rules import evaluate_rules


Mode = Literal["public", "simulated"]


def _latest_trade(case: dict[str, Any]) -> dict[str, Any]:
    return max(case["trade"], key=lambda row: row["year"])


def _public_decision(case: dict[str, Any], rules: list[dict[str, Any]]) -> dict[str, Any]:
    contract = case["public_decision_contract"]
    r11 = next(row for row in rules if row["rule_id"] == "R11")
    if case["rule_context"].get("generic_capacity_reject") and r11["fired"]:
        return {
            "state": "REJECT",
            "route_code": 0,
            "route_label": "No intervention for generic capacity",
            "headline": "REJECT — generic capacity support",
            "rationale": contract["route_restriction"],
            "confidence": "C",
            "missing_facts": contract["missing_facts"],
            "conditions": ["Only a named specialty grade/application exception may re-enter INVESTIGATE."],
            "kill_conditions": contract["kill_conditions"],
            "synthetic_flag": False,
        }
    return {
        "state": "INVESTIGATE",
        "route_code": None,
        "route_label": "Brownfield priority to test",
        "headline": "INVESTIGATE — binding constraint unresolved",
        "rationale": contract["route_restriction"],
        "confidence": "C",
        "missing_facts": contract["missing_facts"],
        "conditions": ["No greenfield or financial support recommendation before effective capacity and target specification are resolved."],
        "kill_conditions": contract["kill_conditions"],
        "synthetic_flag": False,
    }


def analyze_public(opportunity_id: str) -> dict[str, Any]:
    case = isolated_copy(get_public_case(opportunity_id))
    validate_public_evidence(case["evidence"])
    rules = evaluate_rules(case)
    capability = evaluate_capability(
        case["opportunity"]["sector_profile"],
        case["domestic_capability"]["public_dimension_states"],
        case["domestic_capability"]["unresolved_hard_gates"],
    )
    decision = _public_decision(case, rules)
    latest = _latest_trade(case)
    return {
        "opportunity": case["opportunity"],
        "snapshot_id": case["snapshot_id"],
        "as_of_date": case["as_of_date"],
        "mode": "public",
        "real_decision": decision,
        "simulation_decision": None,
        "active_decision": decision,
        "rules": rules,
        "capability": capability,
        "capacity": None,
        "economics": None,
        "competition": None,
        "evsi": None,
        "trade": case["trade"],
        "trade_quality": case["trade_quality"],
        "supplier_metrics": case.get("supplier_metrics_2024"),
        "domestic_capability": case["domestic_capability"],
        "evidence": case["evidence"],
        "data_unlocks": decision["missing_facts"],
        "synthetic_inputs_used": [],
        "integrity": {
            "real_decision_uses_public_only": True,
            "synthetic_isolation": True,
            "latest_imports_usd_m": latest.get("imports_usd_m"),
            "latest_imports_kt": latest.get("imports_kt"),
        },
    }


def competition_warning(
    post_entry_capacity_to_downside_demand: float,
    competition_config: dict[str, Any],
) -> bool:
    return post_entry_capacity_to_downside_demand > float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )


def _simulate_steel(public: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    inputs = scenario["synthetic_inputs"]
    thresholds = thresholds_config()
    competition_config = thresholds["competition"]
    warning_threshold = float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
    incremental_upgrade_max = float(
        thresholds["capability"]["route_bands"]["incremental_upgrade_max"]
    )
    line = inputs["plant_line"]
    capacity = effective_qualified_capacity(
        line["nameplate_kt"],
        line["availability"],
        line["yield"],
        line["qualification_share"],
        line["market_allocation_share"],
    )
    demand = inputs["demand"]
    gap = demand["target_spec_demand_kt"] - capacity
    capability = evaluate_capability(
        public["opportunity"]["sector_profile"],
        inputs["capability_states"],
        inputs["hard_gates"],
    )
    economics = minimum_effective_support(
        inputs["economics"]["cash_flows_without_support"],
        inputs["economics"]["hurdle_rate"],
    )
    economics["instrument"] = inputs["economics"]["support_instrument"]
    national_value = incremental_national_value(inputs["economics"]["national_value"])
    economics["national_value"] = national_value
    ratio = (
        capacity + inputs["upgrade"]["incremental_capacity_kt"]
    ) / demand["downside_demand_kt"]
    warning_fires = competition_warning(ratio, competition_config)
    competition = {
        "post_entry_capacity_to_downside_demand": round(ratio, 4),
        "warning_threshold": warning_threshold,
        "warning_fires": warning_fires,
        "passes_default_warning": not warning_fires,
        "displacement_m_sar": inputs["economics"]["national_value"][
            "displacement"
        ],
    }
    evsi = approximate_evsi(inputs["evsi"])

    passes = (
        gap > 0
        and capability["route_publishable"]
        and capability["d_star"] is not None
        and capability["d_star"] <= incremental_upgrade_max
        and economics["passes"]
        and national_value["positive"]
        and competition["passes_default_warning"]
    )
    if passes:
        decision = {
            "state": "ADVANCE",
            "route_code": 5,
            "route_label": "Conditional brownfield debottlenecking / line expansion",
            "headline": "SIMULATED ADVANCE — brownfield specification upgrade",
            "rationale": "The simulated Ministry-grade evidence resolves a sustained target-specification gap, establishes incremental adjacency, and passes minimum-support, national-value and competition controls.",
            "confidence": "SIMULATED",
            "minimum_effective_support_m_sar": economics["minimum_effective_support_m"],
            "conditions": [
                "Achieve customer acceptance for the named target specification.",
                "Deliver 50 kt of incremental qualified capacity within 18 months.",
                "Support is milestone-based, sunset-bound and subject to clawback.",
            ],
            "kill_conditions": [
                "Committed target-specification demand falls below 72 kt.",
                "Incumbent output or another expansion closes the gap before award.",
                "Customer qualification is not achieved by the contractual milestone.",
            ],
            "synthetic_flag": True,
            "display_label": scenario["display_label"],
        }
    else:
        decision = {
            "state": "INVESTIGATE",
            "route_code": None,
            "route_label": "Simulation controls did not all pass",
            "headline": "SIMULATED INVESTIGATE — one or more gates remain unresolved",
            "rationale": "The simulated branch did not satisfy every hard gate.",
            "confidence": "SIMULATED",
            "conditions": [],
            "kill_conditions": [],
            "synthetic_flag": True,
            "display_label": scenario["display_label"],
        }

    return {
        "simulation_decision": decision,
        "capacity": {
            "nameplate_kt": line["nameplate_kt"],
            "availability": line["availability"],
            "yield": line["yield"],
            "qualification_share": line["qualification_share"],
            "market_allocation_share": line["market_allocation_share"],
            "effective_qualified_capacity_kt": round(capacity, 3),
            "target_spec_demand_kt": demand["target_spec_demand_kt"],
            "specification_adjusted_gap_kt": round(gap, 3),
        },
        "capability": capability,
        "economics": economics,
        "competition": competition,
        "evsi": evsi,
    }


def _simulate_pp(public: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    inputs = scenario["synthetic_inputs"]
    line = inputs["plant_line"]
    capacity = effective_qualified_capacity(
        line["nameplate_kt"],
        line["availability"],
        line["yield"],
        line["qualification_share"],
        line["market_allocation_share"],
    )
    demand = inputs["demand"]
    equivalent = bool(inputs["equivalence"]["domestic_grade_equivalent"])
    qualified_available = float(inputs["equivalence"]["qualified_available_kt"])
    gap = demand["target_spec_demand_kt"] - qualified_available
    capability = evaluate_capability(
        public["opportunity"]["sector_profile"],
        inputs["capability_states"],
        inputs["hard_gates"],
    )
    evsi = approximate_evsi(inputs["evsi"])
    decision = {
        "state": "REJECT",
        "route_code": 0,
        "route_label": "No intervention",
        "headline": "SIMULATED REJECT — no generic specification-adjusted gap",
        "rationale": "The simulated internal grade matrix shows equivalent qualified supply above target demand; generic capacity support would be non-additional.",
        "confidence": "SIMULATED",
        "conditions": ["Reopen only for a named specialty-grade exception supported by buyer evidence."],
        "kill_conditions": ["Any proposed generic-capacity support is stopped while equivalent qualified capacity is available."],
        "synthetic_flag": True,
        "display_label": scenario["display_label"],
    }
    return {
        "simulation_decision": decision,
        "capacity": {
            "formula_capacity_kt": round(capacity, 3),
            "qualified_available_kt": qualified_available,
            "target_spec_demand_kt": demand["target_spec_demand_kt"],
            "specification_adjusted_gap_kt": round(gap, 3),
            "domestic_grade_equivalent": equivalent,
        },
        "capability": capability,
        "economics": {
            "passes": False,
            "minimum_effective_support_m": 0.0,
            "reason": inputs["economics"]["reason"],
        },
        "competition": {
            "passes_default_warning": True,
            "finding": "No new capacity is proposed; redundant support is avoided.",
        },
        "evsi": evsi,
    }


def analyze_simulated(opportunity_id: str) -> dict[str, Any]:
    public = analyze_public(opportunity_id)
    scenario = get_synthetic_scenario(opportunity_id)
    if scenario is None:
        raise ValueError(f"No synthetic scenario is available for {opportunity_id}")
    validate_synthetic_scenario(scenario)
    real_before = isolated_copy(public["real_decision"])

    if opportunity_id == "SAU-H0-721049":
        branch = _simulate_steel(public, scenario)
    elif opportunity_id == "SAU-H0-390210":
        branch = _simulate_pp(public, scenario)
    else:
        raise ValueError(f"No simulation implementation exists for {opportunity_id}")

    public["mode"] = "simulated"
    public["simulation_decision"] = branch["simulation_decision"]
    public["active_decision"] = branch["simulation_decision"]
    public["capacity"] = branch["capacity"]
    public["capability"] = branch["capability"]
    public["economics"] = branch["economics"]
    public["competition"] = branch["competition"]
    public["evsi"] = branch["evsi"]
    public["synthetic_inputs_used"] = sorted(scenario["synthetic_inputs"].keys())
    public["evidence"] = public["evidence"] + synthetic_evidence_rows(scenario)
    public["simulation_scenario"] = {
        "scenario_id": scenario["scenario_id"],
        "display_label": scenario["display_label"],
        "seed_basis": scenario["seed_basis"],
    }
    assert_real_decision_unchanged(real_before, public["real_decision"])
    public["integrity"]["real_decision_unchanged_after_simulation"] = True
    return public


def analyze(opportunity_id: str, mode: Mode = "public") -> dict[str, Any]:
    if mode == "public":
        return analyze_public(opportunity_id)
    if mode == "simulated":
        return analyze_simulated(opportunity_id)
    raise ValueError(f"Unsupported mode: {mode}")


def list_opportunities(mode: Mode = "public") -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    configured_order = [
        item["opportunity_id"]
        for item in project_config().get("golden_cases", [])
    ]
    remaining = sorted(set(public_cases()) - set(configured_order))
    for opportunity_id in configured_order + remaining:
        if opportunity_id not in public_cases():
            continue
        result = analyze(opportunity_id, mode)
        latest = max(result["trade"], key=lambda row: row["year"])
        summaries.append(
            {
                "id": opportunity_id,
                "hs6": result["opportunity"]["hs6"],
                "name_en": result["opportunity"]["commercial_name_en"],
                "name_ar": result["opportunity"]["commercial_name_ar"],
                "sector_profile": result["opportunity"]["sector_profile"],
                "real_state": result["real_decision"]["state"],
                "active_state": result["active_decision"]["state"],
                "headline": result["active_decision"]["headline"],
                "latest_year": latest["year"],
                "latest_imports_usd_m": latest.get("imports_usd_m"),
                "latest_imports_kt": latest.get("imports_kt"),
                "mode": mode,
            }
        )
    return summaries
