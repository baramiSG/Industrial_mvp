from __future__ import annotations

from math import isfinite
from typing import Any, Literal

from .capability import effective_qualified_capacity, evaluate_capability
from .config import (
    authority_summary,
    project_config,
    thresholds_config,
)
from .data_repository import get_public_case, get_synthetic_scenario, public_cases
from .economics import (
    approximate_evsi,
    incremental_national_value,
    minimum_effective_support,
)
from .evidence import (
    EvidenceIntegrityError,
    assert_real_decision_unchanged,
    isolated_copy,
    reconcile_synthetic_scenario,
    require_scenario_reconciliation,
    synthetic_display_labels,
    synthetic_evidence_rows,
    validate_public_evidence,
)
from .rules import evaluate_rules, evaluate_simulated_rules
from .public_snapshot import capability_hard_gate_names
from .public_decision import compute_public_decision
from .narratives import localize_rule_rows
from .trade_metrics import build_supplier_metrics


Mode = Literal["public", "simulated"]


def _latest_trade(case: dict[str, Any]) -> dict[str, Any]:
    return max(case["trade"], key=lambda row: row["year"])


def analyze_public(opportunity_id: str) -> dict[str, Any]:
    case = isolated_copy(get_public_case(opportunity_id))
    validate_public_evidence(case["evidence"])
    rules = evaluate_rules(case)
    capability = evaluate_capability(
        case["opportunity"]["sector_profile"],
        case["domestic_capability"]["public_dimension_states"],
        case["domestic_capability"]["profile_hard_gates"],
        capability_hard_gate_names(case["domestic_capability"]),
    )
    decision = compute_public_decision(case, rules, capability)
    latest = _latest_trade(case)
    r3 = next(row for row in rules if row["rule_id"] == "R3")
    r4d = next(row for row in rules if row["rule_id"] == "R4-D")
    localized_rules = localize_rule_rows(rules)
    return {
        "schema_version": case["schema_version"],
        "opportunity": case["opportunity"],
        "snapshot_id": case["snapshot_id"],
        "as_of_date": case["as_of_date"],
        "authority": authority_summary(),
        "mode": "public",
        "real_decision": decision,
        "simulation_decision": None,
        "active_decision": decision,
        "screening_disposition": decision[
            "screening_disposition"
        ],
        "gap_class": decision["gap_class"],
        "route_hypotheses": decision["route_hypotheses"],
        "preferred_hypothesis": decision[
            "preferred_hypothesis"
        ],
        "evidence_class_assessment": decision[
            "evidence_class_assessment"
        ],
        "advance_gate": decision["advance_gate"],
        "hard_exclusions": decision["hard_exclusions"],
        "rejection_conditions": decision[
            "rejection_conditions"
        ],
        "narrative_version": decision["narrative_version"],
        "rules": localized_rules,
        "capability": capability,
        "capacity": None,
        "economics": None,
        "competition": None,
        "evsi": None,
        "trade": case["trade"],
        "trade_quality": case["trade_quality"],
        "partner_detail": case.get("partner_detail"),
        "supplier_metrics": build_supplier_metrics(
            case,
            r3["metrics"],
            r4d["metrics"],
        ),
        "domestic_flows": case["domestic_flows"],
        "criticality_designation": case["criticality_designation"],
        "domestic_capability": case["domestic_capability"],
        "evidence": case["evidence"],
        "data_unlocks": decision["missing_facts"],
        "synthetic_inputs_used": [],
        "integrity": {
            "real_decision_uses_public_only": True,
            "synthetic_isolation": True,
            "scenario_reconciliation": None,
            "latest_imports_usd_m": latest.get("imports_usd_m"),
            "latest_imports_kt": latest.get("imports_kt"),
        },
    }


from .scenario_contract import (
    SUPPORTED_SCENARIO_CONTRACT_VERSIONS,
    validate_simulation_contract,
)
from .simulation import (
    VALID_SIMULATION_STATES,
    competition_warning,
    evaluate_ground_truth_backtest,
    ground_truth_backtest_error,
    require_ground_truth_backtest,
    simulate as _simulate,
)


def analyze_simulated(opportunity_id: str) -> dict[str, Any]:
    public = analyze_public(opportunity_id)
    scenario = get_synthetic_scenario(opportunity_id)
    if scenario is None:
        raise ValueError(f"No synthetic scenario is available for {opportunity_id}")

    reconciliation = reconcile_synthetic_scenario(
        scenario,
        public,
    )
    require_scenario_reconciliation(reconciliation)
    real_before = isolated_copy(public["real_decision"])

    branch = _simulate(public, scenario)
    backtest = evaluate_ground_truth_backtest(
        scenario,
        branch["simulation_decision"],
    )
    require_ground_truth_backtest(scenario, backtest)

    public["mode"] = "simulated"
    decision = branch["simulation_decision"]
    public["simulation_decision"] = decision
    public["active_decision"] = decision
    public["screening_disposition"] = decision["screening_disposition"]
    public["gap_class"] = branch["gap_class"]
    public["route_hypotheses"] = branch["route_hypotheses"]
    public["preferred_hypothesis"] = branch["preferred_hypothesis"]
    public["evidence_class_assessment"] = branch["evidence_class_assessment"]
    public["advance_gate"] = branch["advance_gate"]
    public["hard_exclusions"] = branch["hard_exclusions"]
    public["rejection_conditions"] = branch["rejection_conditions"]
    public["narrative_version"] = decision["narrative_version"]
    public["rules"] = localize_rule_rows(
        public["rules"] + branch["synthetic_rules"]
    )
    public["capacity"] = branch["capacity"]
    public["capability"] = branch["capability"]
    public["economics"] = branch["economics"]
    public["competition"] = branch["competition"]
    public["evsi"] = branch["evsi"]
    public["synthetic_inputs_used"] = sorted(scenario["synthetic_inputs"].keys())
    public["evidence"] = public["evidence"] + synthetic_evidence_rows(scenario)
    public["simulation_scenario"] = {
        "scenario_id": scenario["scenario_id"],
        "scenario_version": scenario["scenario_version"],
        "display_label": scenario["display_label"],
        "display_labels": synthetic_display_labels(),
        "seed_basis": scenario["seed_basis"],
    }
    assert_real_decision_unchanged(real_before, public["real_decision"])
    public["integrity"]["real_decision_unchanged_after_simulation"] = True
    public["integrity"]["scenario_reconciliation"] = reconciliation
    public["integrity"]["ground_truth_backtest"] = backtest
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
                "screening_disposition": result[
                    "screening_disposition"
                ],
                "headline": result["active_decision"]["headline"],
                "latest_year": latest["year"],
                "latest_imports_usd_m": latest.get("imports_usd_m"),
                "latest_imports_kt": latest.get("imports_kt"),
                "mode": mode,
            }
        )
    return summaries
