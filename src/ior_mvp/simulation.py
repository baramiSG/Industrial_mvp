from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any

from .capability import evaluate_capability
from .config import evidence_policy_config, thresholds_config
from .economics import (
    approximate_evsi,
    incremental_national_value,
    minimum_effective_support,
)
from .evidence import EvidenceIntegrityError, evaluate_advance_gate
from .evidence_needs import (
    EXCLUSION_NEED_FALLBACKS,
    NEED_CODE_ORDER,
    render_need,
)
from .narratives import NarrativeValue, render_catalogue_entry
from .public_decision import (
    DecisionIntegrityError,
    compute_public_decision,
    derive_rejection_conditions,
    evaluate_hard_exclusions,
    select_deep_state,
)
from .public_decision import classify_gap as public_classify_gap
from .route_hypotheses import (
    evaluate_route_hypotheses,
    select_preferred_hypothesis,
)
from .rules import evaluate_rules, evaluate_simulated_rules
from .scenario_contract import (
    decision_narrative_for_state,
    project_simulated_case,
    validate_scenario_pairing,
    validate_simulation_contract,
)
from . import signals

VALID_SIMULATION_STATES = frozenset(
    {"REJECT", "MONITOR", "INVESTIGATE", "ADVANCE"}
)
NOT_CALCULABLE = "NOT_CALCULABLE"


def _required_mapping(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(f"{context}.{key} must be a mapping")
    return value


def _required_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(float(value))
    ):
        raise EvidenceIntegrityError(f"{field} must be a finite number")
    return float(value)


def capacity_projection(
    inputs: dict[str, Any],
) -> tuple[dict[str, Any], float, float, bool]:
    from .capability import effective_qualified_capacity

    line = _required_mapping(inputs, "plant_line", "scenario.synthetic_inputs")
    demand = _required_mapping(inputs, "demand", "scenario.synthetic_inputs")
    nameplate = _required_number(line.get("nameplate_kt"), "plant_line.nameplate_kt")
    availability = _required_number(line.get("availability"), "plant_line.availability")
    yield_rate = _required_number(line.get("yield"), "plant_line.yield")
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
    if equivalence is not None and not isinstance(equivalence, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.equivalence must be a mapping"
        )
    if isinstance(equivalence, dict):
        equivalent = equivalence.get("domestic_grade_equivalent")
        if not isinstance(equivalent, bool):
            raise EvidenceIntegrityError(
                "equivalence.domestic_grade_equivalent must be boolean"
            )
        declared_qualified = equivalence.get("qualified_available_kt")
        if declared_qualified is not None:
            qualified_available = _required_number(
                declared_qualified,
                "equivalence.qualified_available_kt",
            )
            specification_supply = (
                qualified_available if equivalent else formula_capacity
            )
            basis = "DECLARED_QUALIFIED_AVAILABILITY"
        else:
            qualified_available = formula_capacity
            specification_supply = formula_capacity
            basis = "EFFECTIVE_QUALIFIED_CAPACITY"
        raw_gap = target - specification_supply
        capacity = {
            "formula_capacity_kt": round(formula_capacity, 3),
            "effective_qualified_capacity_kt": round(formula_capacity, 3),
            "qualified_available_kt": qualified_available,
            "target_spec_demand_kt": target,
            "specification_adjusted_gap_kt": round(raw_gap, 3),
            "domestic_grade_equivalent": equivalent,
            "qualified_supply_basis": basis,
        }
        equivalence_reject = equivalent and qualified_available >= target
        return capacity, formula_capacity, raw_gap, equivalence_reject

    raw_gap = target - formula_capacity
    capacity = {
        "nameplate_kt": nameplate,
        "availability": availability,
        "yield": yield_rate,
        "qualification_share": qualification_share,
        "market_allocation_share": allocation,
        "effective_qualified_capacity_kt": round(formula_capacity, 3),
        "formula_capacity_kt": round(formula_capacity, 3),
        "target_spec_demand_kt": target,
        "specification_adjusted_gap_kt": round(raw_gap, 3),
        "qualified_supply_basis": "EFFECTIVE_QUALIFIED_CAPACITY",
    }
    return capacity, formula_capacity, raw_gap, False


def simulation_capability(
    public_case: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    states = inputs.get("capability_states")
    hard_gates = inputs.get("hard_gates")
    if not isinstance(states, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.capability_states must be a mapping"
        )
    if not isinstance(hard_gates, (dict, list)):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.hard_gates must be a mapping or list"
        )
    public_capability = public_case["domestic_capability"]
    raw_unresolved = public_capability.get("unresolved_hard_gates", [])
    decision_gates = inputs.get("decision_specific_hard_gates")
    if isinstance(decision_gates, dict):
        remaining = [
            row["name"]
            for row in raw_unresolved
            if isinstance(row, dict)
            and isinstance(row.get("name"), str)
            and (
                row["name"] not in decision_gates
                or not str(decision_gates[row["name"]]).lower().startswith(
                    "resolved"
                )
            )
        ]
    else:
        remaining = [
            row["name"]
            for row in raw_unresolved
            if isinstance(row, dict) and isinstance(row.get("name"), str)
        ]
    return evaluate_capability(
        public_case["opportunity"]["sector_profile"],
        states,
        hard_gates,
        remaining,
    )


def simulation_economics(
    inputs: dict[str, Any],
    formula_capacity: float,
    thresholds: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    economics_inputs = inputs.get("economics")
    demand = _required_mapping(inputs, "demand", "scenario.synthetic_inputs")
    competition_config = thresholds["competition"]
    warning_threshold = float(
        competition_config["post_entry_capacity_to_downside_demand_warning"]
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
    if "cash_flows_without_support" in economics_inputs:
        raw_cash_flows = economics_inputs["cash_flows_without_support"]
        if not isinstance(raw_cash_flows, list) or not raw_cash_flows:
            raise EvidenceIntegrityError(
                "economics.cash_flows_without_support must be a non-empty list"
            )
        cash_flows = [
            _required_number(value, "economics.cash_flows_without_support")
            for value in raw_cash_flows
        ]
        hurdle_rate = _required_number(
            economics_inputs.get("hurdle_rate"),
            "economics.hurdle_rate",
        )
        try:
            economics = minimum_effective_support(cash_flows, hurdle_rate)
        except ValueError as exc:
            raise EvidenceIntegrityError(
                "economics cash flows or hurdle rate are invalid"
            ) from exc
        economics["instrument"] = economics_inputs.get("support_instrument")
        national_components = economics_inputs.get("national_value")
        if isinstance(national_components, dict):
            checked = {
                key: _required_number(value, f"economics.national_value.{key}")
                for key, value in national_components.items()
            }
            try:
                national_value = incremental_national_value(checked)
            except ValueError as exc:
                raise EvidenceIntegrityError(
                    f"scenario.synthetic_inputs.economics.national_value is invalid: {exc}"
                ) from exc
        else:
            national_value = {
                "incremental_national_value_m_sar": NOT_CALCULABLE,
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
                    "demand.downside_demand_kt must be positive for competition"
                )
            ratio = (formula_capacity + incremental_capacity) / downside_demand
            warning_fires = competition_warning(ratio, competition_config)
            competition = {
                "post_entry_capacity_to_downside_demand": round(ratio, 4),
                "warning_threshold": warning_threshold,
                "warning_fires": warning_fires,
                "passes_default_warning": not warning_fires,
                "displacement_m_sar": (
                    national_components.get("displacement")
                    if isinstance(national_components, dict)
                    else NOT_CALCULABLE
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


def competition_warning(
    post_entry_capacity_to_downside_demand: float,
    competition_config: dict[str, Any],
) -> bool:
    return post_entry_capacity_to_downside_demand > float(
        competition_config["post_entry_capacity_to_downside_demand_warning"]
    )


def assess_simulated_decision_critical_fields(
    scenario: dict[str, Any],
    capacity: dict[str, Any],
    capability: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    sid = scenario["scenario_id"]
    inputs = scenario["synthetic_inputs"]
    gate_policy = policy["simulation_gate"]
    declared_block = inputs.get(gate_policy["declared_class_block"], {})
    if not isinstance(declared_block, dict):
        declared_block = {}
    undeclared = gate_policy["undeclared_field_class"]
    actual_class = gate_policy["actual_synthetic_evidence_class"]
    labels = scenario.get("display_label")
    target_spec = inputs.get("target_specification", {})
    demand = inputs.get("demand", {})
    hard_gates = inputs.get("hard_gates", {})
    decision_gates = inputs.get("decision_specific_hard_gates", {})
    assessments: dict[str, dict[str, Any]] = {}
    for field in policy["advance_gate"]["decision_critical_fields"]:
        class_if_confirmed = declared_block.get(field, undeclared)
        if field == "product_identity":
            resolved = (
                isinstance(target_spec, dict)
                and isinstance(target_spec.get("name"), str)
                and target_spec["name"]
                and isinstance(target_spec.get("application"), str)
                and target_spec["application"]
            )
        elif field == "demand_at_required_specification":
            value = demand.get("target_spec_demand_kt") if isinstance(demand, dict) else None
            resolved = isinstance(value, (int, float)) and float(value) >= 0
        elif field == "domestic_supply_or_capability":
            resolved = (
                class_if_confirmed in {"A", "B", "C"}
                and capability.get("route_publishable") is True
            )
        else:
            profile_resolved = not capability.get(
                "unresolved_profile_hard_gates"
            )
            decision_resolved = not capability.get(
                "unresolved_decision_specific_hard_gates"
            )
            resolved = (
                class_if_confirmed in {"A", "B", "C"}
                and capability.get("route_publishable") is True
                and profile_resolved
                and decision_resolved
                and not capability.get("known_hard_gate_failures")
            )
        assessments[field] = {
            "field": field,
            "evidence_class": actual_class,
            "class_if_confirmed": class_if_confirmed,
            "resolution_status": "RESOLVED" if resolved else "UNRESOLVED",
            "support_codes": [f"Simulation branch input: {field}"],
            "evidence_ids": [f"{sid}::class_if_confirmed"],
            "synthetic_flag": True,
            "display_label": labels,
        }
    return assessments


def simulated_evidence_needs(
    composite: dict[str, Any],
    assessments: dict[str, dict[str, Any]],
    capability: dict[str, Any],
    exclusions: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    preferred: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    needs: list[dict[str, Any]] = []
    field_need_map = {
        "product_identity": (
            "identity/tariff-line",
            "need.identity.tariff_line",
        ),
        "demand_at_required_specification": (
            "target specification/application",
            "need.demand.importer_specification",
        ),
        "domestic_supply_or_capability": (
            "capacity/availability/allocation",
            "need.capacity.availability_allocation",
        ),
        "hard_regulatory_or_process_gate": (
            "qualification/profile hard gates",
            "need.demand.importer_application_qualification",
        ),
    }
    for field, assessment in assessments.items():
        if assessment.get("resolution_status") != "RESOLVED":
            mapped = field_need_map.get(field)
            if mapped:
                need_code, template = mapped
                needs.append(
                    render_need(
                        need_code=need_code,
                        variant=field,
                        template_key=template,
                        blocked_field=field,
                        evidence_ids=assessment.get("evidence_ids", []),
                    )
                )
    for spec in EXCLUSION_NEED_FALLBACKS:
        exclusion = next(
            (
                row
                for row in exclusions
                if isinstance(row, dict)
                and row.get("code") == spec["exclusion_code"]
            ),
            None,
        )
        if isinstance(exclusion, dict) and exclusion.get("status") == NOT_CALCULABLE:
            needs.append(
                render_need(
                    need_code=spec["need_code"],
                    variant=spec["variant"],
                    template_key=spec["template_key"],
                    blocked_field=spec["blocked_field"],
                    evidence_ids=exclusion.get("evidence_ids", []),
                )
            )
    inputs = composite.get("decision_inputs", {})
    if not isinstance(
        composite.get("domestic_flows"), dict
    ) or composite["domestic_flows"].get("retained_imports_kt") == "UNAVAILABLE":
        needs.append(
            render_need(
                need_code="re-export/origin decomposition",
                variant="flows",
                template_key="need.flows.reexport_origin_decomposition",
                blocked_field="domestic_flows",
                evidence_ids=[],
            )
        )
    order = {code: index for index, code in enumerate(NEED_CODE_ORDER)}
    deduped: dict[str, dict[str, Any]] = {}
    for need in needs:
        deduped[need["need_code"]] = need
    return sorted(
        deduped.values(),
        key=lambda row: order.get(row["need_code"], len(order)),
    )


def render_simulated_narrative(
    scenario: dict[str, Any],
    state_result: dict[str, Any],
    preferred: dict[str, Any] | None,
    exclusions: list[dict[str, Any]],
    evidence_needs: list[dict[str, Any]],
) -> dict[str, Any]:
    del preferred, exclusions, evidence_needs
    state = state_result["state"]
    declared = decision_narrative_for_state(scenario, state)
    route_code = state_result.get("route_code")
    if declared is not None:
        localized: dict[str, dict[str, Any]] = {}
        for locale in ("en", "ar"):
            localized[locale] = {
                "headline": {
                    "text": declared["headline"][locale],
                    "template_key": None,
                    "narrative_source": "scenario",
                },
                "route_label": {
                    "text": declared["route_label"][locale],
                    "template_key": None,
                    "narrative_source": "scenario",
                },
                "rationale": {
                    "text": declared["rationale"][locale],
                    "template_key": None,
                    "narrative_source": "scenario",
                },
                "conditions": [
                    {
                        "text": item[locale],
                        "template_key": None,
                        "narrative_source": "scenario",
                    }
                    for item in declared.get("conditions", [])
                ],
                "kill_conditions": [
                    {
                        "text": item[locale],
                        "template_key": None,
                        "narrative_source": "scenario",
                    }
                    for item in declared.get("kill_conditions", [])
                ],
            }
        en = localized["en"]
        return {
            "headline": en["headline"]["text"],
            "route_label": en["route_label"]["text"],
            "rationale": en["rationale"]["text"],
            "conditions": [item["text"] for item in en["conditions"]],
            "kill_conditions": [item["text"] for item in en["kill_conditions"]],
            "localized_narrative": localized,
            "narrative_source": "scenario",
        }
    return _catalogue_simulated_narrative(state, route_code)


def _catalogue_simulated_narrative(
    state: str,
    route_code: int | None,
) -> dict[str, Any]:
    keys = {
        "ADVANCE": (
            "decision.simulated.advance.headline",
            None,
            "decision.simulated.advance.rationale",
            "decision.simulated.advance.condition",
            "decision.simulated.advance.kill",
        ),
        "REJECT": (
            "decision.simulated.reject.headline",
            "route.0.label",
            "decision.simulated.reject.rationale",
            "decision.simulated.reject.condition",
            "decision.simulated.reject.kill",
        ),
        "MONITOR": (
            "decision.simulated.monitor.headline",
            "decision.simulated.monitor.route",
            "decision.simulated.monitor.rationale",
            "decision.public.monitor.condition",
            None,
        ),
        "INVESTIGATE": (
            "decision.simulated.investigate.headline",
            "decision.simulated.investigate.route",
            "decision.simulated.investigate.rationale",
            None,
            None,
        ),
    }
    headline_key, route_key, rationale_key, condition_key, kill_key = keys[state]
    localized: dict[str, dict[str, Any]] = {}
    for locale in ("en", "ar"):
        values = (
            {"route_code": NarrativeValue.computed(route_code)}
            if route_code is not None and state == "ADVANCE"
            else None
        )
        localized[locale] = {
            "headline": render_catalogue_entry(headline_key, locale, values),
            "route_label": render_catalogue_entry(
                route_key or "route.0.label",
                locale,
            ),
            "rationale": render_catalogue_entry(rationale_key, locale),
            "conditions": (
                [render_catalogue_entry(condition_key, locale)]
                if condition_key
                else []
            ),
            "kill_conditions": (
                [render_catalogue_entry(kill_key, locale)] if kill_key else []
            ),
        }
    en = localized["en"]
    return {
        "headline": en["headline"]["text"],
        "route_label": en["route_label"]["text"],
        "rationale": en["rationale"]["text"],
        "conditions": [item["text"] for item in en["conditions"]],
        "kill_conditions": [item["text"] for item in en["kill_conditions"]],
        "localized_narrative": localized,
        "narrative_source": "catalogue",
    }


def counterfactual_answers(
    scenario: dict[str, Any],
    capability: dict[str, Any],
    economics: dict[str, Any],
    capacity: dict[str, Any],
) -> dict[str, Any]:
    inputs = scenario.get("synthetic_inputs", {})
    block = inputs.get("counterfactual")
    upgrade = inputs.get("upgrade")
    answers = {
        "q1_incumbent_meets_specification_without_capital": "UNAVAILABLE",
        "q4_downside_demand_supports_incumbent_and_new_entrant": "UNAVAILABLE",
        "q5_new_entry_displaces_efficient_domestic_production": "UNAVAILABLE",
        "q6_technology_jv_superior_to_expansion_or_greenfield": "UNAVAILABLE",
    }
    if isinstance(block, dict):
        for key in answers:
            value = block.get(key)
            if value in {True, False, "UNAVAILABLE"}:
                answers[key] = value
    dimensions = capability.get("dimensions", [])
    q2 = [
        row.get("dimension") or row.get("identifier")
        for row in dimensions
        if isinstance(row, dict)
        and isinstance(row.get("state"), int)
        and row["state"] >= 1
    ]
    greenfield_alternative = "UNAVAILABLE"
    route_evidence = inputs.get("route_evidence")
    if isinstance(route_evidence, list):
        route7 = next(
            (
                row
                for row in route_evidence
                if isinstance(row, dict) and row.get("route_code") == 7
            ),
            None,
        )
        if isinstance(route7, dict):
            greenfield_alternative = route7.get("basis", "UNAVAILABLE")
    q3 = {
        "incremental_capacity_kt": (
            upgrade.get("incremental_capacity_kt")
            if isinstance(upgrade, dict)
            else "UNAVAILABLE"
        ),
        "schedule_months": (
            upgrade.get("schedule_months")
            if isinstance(upgrade, dict)
            else "UNAVAILABLE"
        ),
        "unsupported_npv_m": economics.get("unsupported_npv_m"),
        "minimum_effective_support_m": economics.get(
            "minimum_effective_support_m"
        ),
        "greenfield_alternative": greenfield_alternative,
    }
    return {
        **answers,
        "q2_missing_capabilities": q2,
        "q3_brownfield_versus_greenfield": q3,
    }


def competition_gates(
    scenario: dict[str, Any],
    route_record: dict[str, Any] | None,
    competition: dict[str, Any],
) -> dict[str, Any]:
    non_additionality = {
        "status": NOT_CALCULABLE,
        "basis": NOT_CALCULABLE,
    }
    if isinstance(route_record, dict):
        additionality = route_record.get("additionality")
        if additionality in {"passes", "fails"}:
            non_additionality = {
                "status": additionality,
                "basis": "route_record_additionality",
            }
    concentration = NOT_CALCULABLE
    inputs = scenario.get("synthetic_inputs", {}).get("competition_inputs")
    if isinstance(inputs, dict):
        market = inputs.get("market_concentration")
        if isinstance(market, dict):
            concentration = {
                "hhi_before": market.get("hhi_before"),
                "hhi_after": market.get("hhi_after"),
                "delta": (
                    market.get("hhi_after", 0) - market.get("hhi_before", 0)
                    if isinstance(market.get("hhi_before"), (int, float))
                    and isinstance(market.get("hhi_after"), (int, float))
                    else NOT_CALCULABLE
                ),
                "status": "REPORTED",
                "note": (
                    "Lower concentration is not equated with benefit."
                ),
            }
    return {
        **competition,
        "non_additionality": non_additionality,
        "concentration_before_after": concentration,
    }


def compute_simulated_decision(
    public_case: dict[str, Any],
    scenario: dict[str, Any],
    rules: list[dict[str, Any]],
    capacity: dict[str, Any],
    capability: dict[str, Any],
    economics: dict[str, Any],
    competition: dict[str, Any],
) -> dict[str, Any]:
    policy = evidence_policy_config()
    composite = project_simulated_case(
        public_case,
        scenario,
        capacity,
        capability,
    )
    assessments = assess_simulated_decision_critical_fields(
        scenario,
        capacity,
        capability,
        policy,
    )
    gate_input = {
        field: {**row, "evidence_class": row["class_if_confirmed"]}
        for field, row in assessments.items()
    }
    advance_gate = evaluate_advance_gate(
        gate_input,
        policy["advance_gate"],
    )
    advance_gate = {
        **advance_gate,
        "basis": policy["simulation_gate"]["basis"],
        "synthetic_flag": True,
        "display_labels": scenario.get("display_labels"),
    }
    exclusions = evaluate_hard_exclusions(composite)
    gap = public_classify_gap(
        composite,
        rules,
        assessments,
        exclusions,
        capability,
    )
    rejections = derive_rejection_conditions(composite, rules, exclusions)
    hypotheses = evaluate_route_hypotheses(
        composite,
        rules,
        capability,
        gap,
        rejections,
        detected_constraint=gap.get("constraint_class"),
    )
    preferred = select_preferred_hypothesis(hypotheses)
    selected = None
    if preferred is not None and preferred["selection_basis"] in {
        "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE",
        "EVIDENCED_NO_INTERVENTION",
        "MONITOR_NO_IMMEDIATE_ACTION",
    }:
        selected = next(
            row
            for row in hypotheses
            if row["route_code"] == preferred["route_code"]
        )
    needs = simulated_evidence_needs(
        composite,
        assessments,
        capability,
        exclusions,
        hypotheses,
        preferred,
    )
    synthetic_rules = evaluate_simulated_rules(
        scenario,
        public_case,
        capacity,
        thresholds_config(),
    )
    all_rules = rules + synthetic_rules
    support = signals.advance_supporting_signal_rule_ids(all_rules)
    state_result = select_deep_state(
        case=composite,
        rules=all_rules,
        assessments=assessments,
        advance_gate=advance_gate,
        exclusions=exclusions,
        rejection_conditions=rejections,
        selected_hypothesis=selected,
        preferred_hypothesis=preferred,
        evidence_needs=needs,
        advance_support_signal_rule_ids=support,
    )
    if state_result["state"] == "MONITOR":
        monitor = composite.get("decision_inputs", {}).get(
            "monitor_trigger"
        )
        if not isinstance(monitor, dict):
            raise DecisionIntegrityError(
                "Simulated MONITOR requires a declared monitor_trigger"
            )
    narrative = render_simulated_narrative(
        scenario,
        state_result,
        preferred,
        exclusions,
        needs,
    )
    decision = {
        "state": state_result["state"],
        "route_code": state_result["route_code"],
        "decision_reason_code": state_result["decision_reason_code"],
        "advance_support_signal_rule_ids": support,
        "screening_disposition": "CANDIDATE",
        "gap_class": gap,
        "route_hypotheses": hypotheses,
        "preferred_hypothesis": preferred,
        "evidence_class_assessment": assessments,
        "advance_gate": advance_gate,
        "hard_exclusions": exclusions,
        "rejection_conditions": rejections,
        "missing_facts": [need["text"] for need in needs],
        "localized_missing_facts": {
            locale: [need["localized_text"][locale] for need in needs]
            for locale in ("en", "ar")
        },
        "counterfactual": counterfactual_answers(
            scenario,
            capability,
            economics,
            capacity,
        ),
        "headline": narrative["headline"],
        "route_label": narrative["route_label"],
        "rationale": narrative["rationale"],
        "conditions": narrative["conditions"],
        "kill_conditions": narrative["kill_conditions"],
        "localized_narrative": narrative["localized_narrative"],
        "narrative_version": "1.0.0",
        "narrative_source": narrative["narrative_source"],
        "confidence": "SIMULATED",
        "synthetic_flag": True,
        "display_label": scenario["display_label"],
    }
    if state_result["state"] == "ADVANCE":
        decision["minimum_effective_support_m_sar"] = economics.get(
            "minimum_effective_support_m"
        )
    return decision


def simulate(public: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    public_case = public
    rules = public["rules"] if "rules" in public else evaluate_rules(public_case)
    validate_scenario_pairing(scenario, public_case)
    inputs = scenario["synthetic_inputs"]
    thresholds = thresholds_config()
    capability = simulation_capability(public_case, inputs)
    capacity, formula_capacity, _raw_gap, _equiv_reject = capacity_projection(
        inputs
    )
    economics, competition, _national_value = simulation_economics(
        inputs,
        formula_capacity,
        thresholds,
    )
    if "evsi" not in inputs:
        evsi = None
    else:
        evsi_inputs = inputs["evsi"]
        if not isinstance(evsi_inputs, dict):
            raise EvidenceIntegrityError(
                "scenario.synthetic_inputs.evsi must be a mapping"
            )
        try:
            evsi = approximate_evsi(evsi_inputs)
        except (TypeError, ValueError) as exc:
            raise EvidenceIntegrityError(
                f"scenario.synthetic_inputs.evsi contains an invalid value: {exc}"
            ) from exc
    route_record = None
    decision = compute_simulated_decision(
        public_case,
        scenario,
        rules,
        capacity,
        capability,
        economics,
        competition,
    )
    if isinstance(decision.get("preferred_hypothesis"), dict):
        code = decision["preferred_hypothesis"].get("route_code")
        route_record = next(
            (
                row
                for row in decision["route_hypotheses"]
                if row.get("route_code") == code
            ),
            None,
        )
    competition = competition_gates(scenario, route_record, competition)
    finding = decision_narrative_for_state(
        scenario,
        decision["state"],
    )
    if isinstance(finding, dict) and "competition_finding" in finding:
        competition = dict(competition)
        competition["finding"] = finding["competition_finding"]["en"]
    synthetic_rules = evaluate_simulated_rules(
        scenario,
        public_case,
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
        "gap_class": decision["gap_class"],
        "route_hypotheses": decision["route_hypotheses"],
        "preferred_hypothesis": decision["preferred_hypothesis"],
        "evidence_class_assessment": decision["evidence_class_assessment"],
        "advance_gate": decision["advance_gate"],
        "hard_exclusions": decision["hard_exclusions"],
        "rejection_conditions": decision["rejection_conditions"],
    }


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
