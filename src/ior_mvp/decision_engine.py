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
    synthetic_evidence_rows,
    validate_public_evidence,
)
from .rules import evaluate_rules, evaluate_simulated_rules


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
        "authority": authority_summary(),
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
            "scenario_reconciliation": None,
            "latest_imports_usd_m": latest.get("imports_usd_m"),
            "latest_imports_kt": latest.get("imports_kt"),
        },
    }


SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})
VALID_SIMULATION_STATES = {
    "REJECT",
    "MONITOR",
    "INVESTIGATE",
    "ADVANCE",
}


def _required_mapping(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            f"{context}.{key} must be a mapping"
        )
    return value


def _required_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(float(value))
    ):
        raise EvidenceIntegrityError(
            f"{field} must be a finite number"
        )
    return float(value)


def validate_simulation_contract(
    scenario: dict[str, Any],
) -> None:
    version = scenario.get("scenario_version")
    if (
        not isinstance(version, str)
        or version not in SUPPORTED_SCENARIO_CONTRACT_VERSIONS
    ):
        raise EvidenceIntegrityError(
            "Synthetic scenario scenario_version is unsupported: "
            f"{version}"
        )
    ground_truth = _required_mapping(
        scenario,
        "ground_truth",
        "scenario",
    )
    expected_state = ground_truth.get(
        "expected_simulation_state"
    )
    if expected_state not in VALID_SIMULATION_STATES:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_simulation_state "
            "must be a decision state"
        )
    route_code = ground_truth.get("expected_route_code")
    if (
        route_code is not None
        and (
            isinstance(route_code, bool)
            or not isinstance(route_code, int)
        )
    ):
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_route_code "
            "must be an integer or null"
        )
    basis = ground_truth.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.basis must be a non-empty string"
        )
    narratives = _required_mapping(
        scenario,
        "decision_narrative",
        "scenario",
    )
    required_narratives = (
        (expected_state,)
        if expected_state == "INVESTIGATE"
        else (expected_state, "INVESTIGATE")
    )
    for state in required_narratives:
        narrative = _required_mapping(
            narratives,
            state,
            "scenario.decision_narrative",
        )
        for field in ("headline", "route_label", "rationale"):
            value = narrative.get(field)
            if not isinstance(value, str) or not value:
                raise EvidenceIntegrityError(
                    "scenario.decision_narrative."
                    f"{state}.{field} must be a non-empty string"
                )
        for field in ("conditions", "kill_conditions"):
            value = narrative.get(field)
            if (
                not isinstance(value, list)
                or not all(
                    isinstance(item, str)
                    for item in value
                )
            ):
                raise EvidenceIntegrityError(
                    "scenario.decision_narrative."
                    f"{state}.{field} must be a list of strings"
                )


def _decision_narrative(
    scenario: dict[str, Any],
    state: str,
) -> dict[str, Any]:
    narratives = _required_mapping(
        scenario,
        "decision_narrative",
        "scenario",
    )
    narrative = _required_mapping(
        narratives,
        state,
        "scenario.decision_narrative",
    )
    for field in ("headline", "route_label", "rationale"):
        value = narrative.get(field)
        if not isinstance(value, str) or not value:
            raise EvidenceIntegrityError(
                "scenario.decision_narrative."
                f"{state}.{field} must be a non-empty string"
            )
    for field in ("conditions", "kill_conditions"):
        value = narrative.get(field)
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) for item in value)
        ):
            raise EvidenceIntegrityError(
                "scenario.decision_narrative."
                f"{state}.{field} must be a list of strings"
            )
    finding = narrative.get("competition_finding")
    if finding is not None and (
        not isinstance(finding, str) or not finding
    ):
        raise EvidenceIntegrityError(
            "scenario.decision_narrative."
            f"{state}.competition_finding must be a non-empty string"
        )
    return narrative


def evaluate_ground_truth_backtest(
    scenario: dict[str, Any],
    simulation_decision: dict[str, Any],
) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    ground_truth = scenario["ground_truth"]
    expected = {
        "state": ground_truth["expected_simulation_state"],
        "route_code": ground_truth["expected_route_code"],
    }
    actual = {
        "state": simulation_decision.get("state"),
        "route_code": simulation_decision.get("route_code"),
    }
    return {
        "expected": expected,
        "actual": actual,
        "match": expected == actual,
    }


def ground_truth_backtest_error(
    scenario: dict[str, Any],
    report: dict[str, Any],
) -> str:
    expected = report["expected"]
    actual = report["actual"]
    return (
        "Synthetic scenario ground-truth back-test failed for "
        f"{scenario['scenario_id']}: "
        f"expected state={expected['state']}, "
        f"route_code={expected['route_code']}; "
        f"actual state={actual['state']}, "
        f"route_code={actual['route_code']}"
    )


def require_ground_truth_backtest(
    scenario: dict[str, Any],
    report: dict[str, Any],
) -> None:
    if report.get("match") is not True:
        raise EvidenceIntegrityError(
            ground_truth_backtest_error(scenario, report)
        )


def competition_warning(
    post_entry_capacity_to_downside_demand: float,
    competition_config: dict[str, Any],
) -> bool:
    return post_entry_capacity_to_downside_demand > float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )


def _capacity_projection(
    inputs: dict[str, Any],
) -> tuple[dict[str, Any], float, float, bool]:
    line = _required_mapping(
        inputs,
        "plant_line",
        "scenario.synthetic_inputs",
    )
    demand = _required_mapping(
        inputs,
        "demand",
        "scenario.synthetic_inputs",
    )
    nameplate = _required_number(
        line.get("nameplate_kt"),
        "plant_line.nameplate_kt",
    )
    availability = _required_number(
        line.get("availability"),
        "plant_line.availability",
    )
    yield_rate = _required_number(
        line.get("yield"),
        "plant_line.yield",
    )
    qualification_share = _required_number(
        line.get("qualification_share"),
        "plant_line.qualification_share",
    )
    allocation = _required_number(
        line.get("market_allocation_share"),
        "plant_line.market_allocation_share",
    )
    formula_capacity = effective_qualified_capacity(
        nameplate,
        availability,
        yield_rate,
        qualification_share,
        allocation,
    )
    target = _required_number(
        demand.get("target_spec_demand_kt"),
        "demand.target_spec_demand_kt",
    )

    equivalence = inputs.get("equivalence")
    if equivalence is not None and not isinstance(
        equivalence,
        dict,
    ):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.equivalence must be a mapping"
        )
    if isinstance(equivalence, dict):
        equivalent = equivalence.get(
            "domestic_grade_equivalent"
        )
        if not isinstance(equivalent, bool):
            raise EvidenceIntegrityError(
                "equivalence.domestic_grade_equivalent "
                "must be boolean"
            )
        qualified_available = _required_number(
            equivalence.get("qualified_available_kt"),
            "equivalence.qualified_available_kt",
        )
        specification_supply = (
            qualified_available
            if equivalent
            else formula_capacity
        )
        raw_gap = target - specification_supply
        capacity = {
            "formula_capacity_kt": round(
                formula_capacity,
                3,
            ),
            "qualified_available_kt": qualified_available,
            "target_spec_demand_kt": target,
            "specification_adjusted_gap_kt": round(
                raw_gap,
                3,
            ),
            "domestic_grade_equivalent": equivalent,
        }
        equivalence_reject = (
            equivalent and qualified_available >= target
        )
        return (
            capacity,
            formula_capacity,
            raw_gap,
            equivalence_reject,
        )

    raw_gap = target - formula_capacity
    capacity = {
        "nameplate_kt": nameplate,
        "availability": availability,
        "yield": yield_rate,
        "qualification_share": qualification_share,
        "market_allocation_share": allocation,
        "effective_qualified_capacity_kt": round(
            formula_capacity,
            3,
        ),
        "target_spec_demand_kt": target,
        "specification_adjusted_gap_kt": round(
            raw_gap,
            3,
        ),
    }
    return capacity, formula_capacity, raw_gap, False


def _simulation_capability(
    public: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    states = inputs.get("capability_states")
    hard_gates = inputs.get("hard_gates")
    if not isinstance(states, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.capability_states "
            "must be a mapping"
        )
    if not isinstance(hard_gates, (dict, list)):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.hard_gates "
            "must be a mapping or list"
        )
    return evaluate_capability(
        public["opportunity"]["sector_profile"],
        states,
        hard_gates,
    )


def _simulation_economics(
    inputs: dict[str, Any],
    formula_capacity: float,
    thresholds: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    economics_inputs = inputs.get("economics")
    demand = _required_mapping(
        inputs,
        "demand",
        "scenario.synthetic_inputs",
    )
    if not isinstance(economics_inputs, dict):
        return (
            {
                "passes": False,
                "minimum_effective_support_m": None,
                "reason": "Economics inputs are NOT_CALCULABLE.",
            },
            {
                "warning_fires": None,
                "passes_default_warning": False,
                "reason": "Competition control is NOT_CALCULABLE.",
            },
            {},
        )

    competition_config = thresholds["competition"]
    warning_threshold = float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
    if "cash_flows_without_support" in economics_inputs:
        raw_cash_flows = economics_inputs[
            "cash_flows_without_support"
        ]
        if not isinstance(raw_cash_flows, list) or not raw_cash_flows:
            raise EvidenceIntegrityError(
                "economics.cash_flows_without_support "
                "must be a non-empty list"
            )
        cash_flows = [
            _required_number(
                value,
                "economics.cash_flows_without_support",
            )
            for value in raw_cash_flows
        ]
        hurdle_rate = _required_number(
            economics_inputs.get("hurdle_rate"),
            "economics.hurdle_rate",
        )
        try:
            economics = minimum_effective_support(
                cash_flows,
                hurdle_rate,
            )
        except ValueError as exc:
            raise EvidenceIntegrityError(
                "economics cash flows or hurdle rate are invalid"
            ) from exc
        economics["instrument"] = economics_inputs.get(
            "support_instrument"
        )

        national_components = economics_inputs.get(
            "national_value"
        )
        if isinstance(national_components, dict):
            checked_components = {
                key: _required_number(
                    value,
                    f"economics.national_value.{key}",
                )
                for key, value in national_components.items()
            }
            try:
                national_value = incremental_national_value(
                    checked_components
                )
            except ValueError as exc:
                raise EvidenceIntegrityError(
                    "scenario.synthetic_inputs.economics."
                    f"national_value is invalid: {exc}"
                ) from exc
        else:
            national_value = {
                "incremental_national_value_m_sar": (
                    "NOT_CALCULABLE"
                ),
                "positive": False,
            }
        economics["national_value"] = national_value

        upgrade = inputs.get("upgrade")
        downside = demand.get("downside_demand_kt")
        if isinstance(upgrade, dict) and downside is not None:
            incremental_capacity = _required_number(
                upgrade.get("incremental_capacity_kt"),
                "upgrade.incremental_capacity_kt",
            )
            downside_demand = _required_number(
                downside,
                "demand.downside_demand_kt",
            )
            if downside_demand <= 0:
                raise EvidenceIntegrityError(
                    "demand.downside_demand_kt must be positive "
                    "for competition analysis"
                )
            ratio = (
                formula_capacity + incremental_capacity
            ) / downside_demand
            warning_fires = competition_warning(
                ratio,
                competition_config,
            )
            competition = {
                "post_entry_capacity_to_downside_demand": round(
                    ratio,
                    4,
                ),
                "warning_threshold": warning_threshold,
                "warning_fires": warning_fires,
                "passes_default_warning": not warning_fires,
                "displacement_m_sar": (
                    national_components.get("displacement")
                    if isinstance(national_components, dict)
                    else "NOT_CALCULABLE"
                ),
            }
        else:
            competition = {
                "warning_threshold": warning_threshold,
                "warning_fires": None,
                "passes_default_warning": False,
                "reason": "Competition control is NOT_CALCULABLE.",
            }
        return economics, competition, national_value

    if "support_required" in economics_inputs:
        support = _required_number(
            economics_inputs.get("support_required"),
            "economics.support_required",
        )
        return (
            {
                "passes": False,
                "minimum_effective_support_m": support,
                "reason": economics_inputs.get("reason"),
            },
            {"passes_default_warning": True},
            {"positive": False},
        )

    return (
        {
            "passes": False,
            "minimum_effective_support_m": None,
            "reason": "Economics controls are NOT_CALCULABLE.",
        },
        {
            "warning_threshold": warning_threshold,
            "warning_fires": None,
            "passes_default_warning": False,
            "reason": "Competition control is NOT_CALCULABLE.",
        },
        {"positive": False},
    )


def _simulate(
    public: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    inputs = scenario["synthetic_inputs"]
    thresholds = thresholds_config()
    (
        capacity,
        formula_capacity,
        raw_gap,
        equivalence_reject,
    ) = _capacity_projection(inputs)
    capability = _simulation_capability(public, inputs)
    economics, competition, national_value = (
        _simulation_economics(
            inputs,
            formula_capacity,
            thresholds,
        )
    )
    evsi_inputs = inputs.get("evsi")
    if not isinstance(evsi_inputs, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.evsi must be a mapping"
        )
    try:
        evsi = approximate_evsi(evsi_inputs)
    except (TypeError, ValueError) as exc:
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.evsi contains an invalid "
            f"value: {exc}"
        ) from exc

    incremental_upgrade_max = float(
        thresholds["capability"]["route_bands"][
            "incremental_upgrade_max"
        ]
    )
    advance = (
        not equivalence_reject
        and raw_gap > 0
        and capability["route_publishable"]
        and capability["d_star"] is not None
        and capability["d_star"] <= incremental_upgrade_max
        and economics["passes"]
        and national_value.get("positive") is True
        and competition["passes_default_warning"]
    )
    if equivalence_reject:
        state = "REJECT"
        route_code: int | None = 0
    elif advance:
        state = "ADVANCE"
        route_code = 5
    else:
        state = "INVESTIGATE"
        route_code = None

    narrative = _decision_narrative(scenario, state)
    decision = {
        "state": state,
        "route_code": route_code,
        "route_label": narrative["route_label"],
        "headline": narrative["headline"],
        "rationale": narrative["rationale"],
        "confidence": "SIMULATED",
        "conditions": list(narrative["conditions"]),
        "kill_conditions": list(
            narrative["kill_conditions"]
        ),
        "synthetic_flag": True,
        "display_label": scenario["display_label"],
    }
    if state == "ADVANCE":
        decision["minimum_effective_support_m_sar"] = (
            economics["minimum_effective_support_m"]
        )
    finding = narrative.get("competition_finding")
    if finding is not None:
        competition["finding"] = finding

    synthetic_rules = evaluate_simulated_rules(
        scenario,
        public,
        capacity,
        thresholds,
    )
    return {
        "simulation_decision": decision,
        "capacity": capacity,
        "capability": capability,
        "economics": economics,
        "competition": competition,
        "evsi": evsi,
        "synthetic_rules": synthetic_rules,
    }


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
    public["simulation_decision"] = branch["simulation_decision"]
    public["active_decision"] = branch["simulation_decision"]
    public["rules"] = public["rules"] + branch["synthetic_rules"]
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
                "headline": result["active_decision"]["headline"],
                "latest_year": latest["year"],
                "latest_imports_usd_m": latest.get("imports_usd_m"),
                "latest_imports_kt": latest.get("imports_kt"),
                "mode": mode,
            }
        )
    return summaries
