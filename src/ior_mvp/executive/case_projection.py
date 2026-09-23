"""Eight-step and four-vector executive case projection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .models import (
    AvailabilityStatus,
    DecisionVector,
    DecisionVectorId,
    ExecutiveStep,
    ExecutiveStepId,
    ExecutiveValue,
)
from .taxonomy import (
    ExecutiveIntegrityError,
    classify_need_code,
    extract_case_need_codes,
)

Analysis = Mapping[str, Any]
Scalar = str | int | float | bool | None


def _mapping(value: Any, field: str) -> Analysis:
    if not isinstance(value, Mapping):
        raise ExecutiveIntegrityError(f"{field} must be a mapping")
    return value


def _rows(value: Any, field: str) -> tuple[Analysis, ...]:
    valid_sequence = isinstance(value, Sequence) and not isinstance(
        value, (str, bytes)
    )
    if not valid_sequence or not all(isinstance(row, Mapping) for row in value):
        raise ExecutiveIntegrityError(f"{field} must contain mappings")
    return tuple(value)


def _value(
    key: str,
    value: Scalar,
    *,
    unavailable: bool = False,
    need_codes: tuple[str, ...] = (),
    evidence_ids: tuple[str, ...] = (),
) -> ExecutiveValue:
    missing = value is None or value == "NOT_CALCULABLE"
    availability = (
        AvailabilityStatus.UNAVAILABLE
        if unavailable
        else AvailabilityStatus.NOT_CALCULABLE
        if missing
        else AvailabilityStatus.AVAILABLE
    )
    return ExecutiveValue(
        key=key,
        availability=availability,
        value=None if unavailable or missing else value,
        need_codes=need_codes,
        evidence_ids=evidence_ids,
    )


def _values(
    *items: tuple[str, Scalar],
    unavailable: bool = False,
    evidence_ids: tuple[str, ...] = (),
) -> tuple[ExecutiveValue, ...]:
    return tuple(
        _value(
            key,
            value,
            unavailable=unavailable,
            evidence_ids=evidence_ids,
        )
        for key, value in items
    )


def _step(
    step_id: ExecutiveStepId,
    values: tuple[ExecutiveValue, ...],
    *claims: str,
    unavailable: bool = False,
    public_claim: bool = True,
) -> ExecutiveStep:
    public_claim_ids = (f"step.{step_id.value}",) if public_claim else ()
    return ExecutiveStep(
        step_id=step_id,
        availability=(
            AvailabilityStatus.UNAVAILABLE
            if unavailable
            else AvailabilityStatus.AVAILABLE
        ),
        claim_ids=(*public_claim_ids, *claims),
        values=values,
    )


def build_steps(
    public: Analysis,
    simulated: Analysis | None,
    claim_evidence: Mapping[str, tuple[str, ...]],
) -> tuple[ExecutiveStep, ...]:
    """Project the fixed eight executive steps and branch evidence."""

    rules = _rows(public.get("rules"), "rules")
    fired = tuple(
        str(row["rule_id"]) for row in rules if row.get("fired") is True
    )
    needs = extract_case_need_codes(public)
    trade = max(
        _rows(public.get("trade"), "trade"),
        key=lambda row: row["year"],
    )
    decision = _mapping(public.get("real_decision"), "real decision")
    gap = _mapping(public.get("gap_class"), "gap")
    route_rows = _rows(public.get("route_hypotheses"), "routes")
    route_codes = tuple(row.get("route_code") for row in route_rows)
    if any(type(code) is not int or not 0 <= code <= 8 for code in route_codes):
        raise ExecutiveIntegrityError("Route codes must be integers 0-8")
    if len(set(route_codes)) != len(route_codes):
        raise ExecutiveIntegrityError("Route codes must be unique")
    routes = tuple(f"route.{code}" for code in route_codes)
    if "preferred_hypothesis" not in public:
        raise ExecutiveIntegrityError("Preferred route field is missing")
    preferred = public["preferred_hypothesis"]
    preferred_code = None
    if preferred is not None:
        preferred = _mapping(preferred, "preferred route")
        preferred_code = preferred.get("route_code")
        if (type(preferred_code) is not int or not 0 <= preferred_code <= 8
                or preferred_code not in route_codes):
            raise ExecutiveIntegrityError("Preferred route code must be a declared integer 0-8")

    def sim(key: str) -> Analysis:
        value = simulated.get(key) if simulated is not None else None
        return _mapping(value, key) if isinstance(value, Mapping) else {}

    sim_decision, economics = sim("simulation_decision"), sim("economics")
    national_value = (
        _mapping(economics["national_value"], "national value")
        if isinstance(economics.get("national_value"), Mapping)
        else {}
    )
    evsi, scenario = sim("evsi"), sim("simulation_scenario")
    absent = simulated is None
    simulated_step_id = "step.SIMULATED_EVIDENCE.simulated"
    route_step_id = "step.ROUTE_COMPARISON.simulated"
    intervention_step_id = "step.INTERVENTION.simulated"
    conditions_step_id = "step.CONDITIONS_AND_KILL.simulated"
    return (
        _step(
            ExecutiveStepId.SIGNAL,
            _values(
                ("latest_imports_usd_m", trade.get("imports_usd_m")),
                ("fired_rule_ids", ",".join(fired)),
            ),
            "metric.trade",
            "metric.concentration",
            *(f"rule.{rule_id}" for rule_id in fired),
        ),
        _step(
            ExecutiveStepId.FALSE_POSITIVE_CONTROLS,
            _values(
                ("hard_exclusion_count", len(public["hard_exclusions"])),
                (
                    "r11_fired",
                    next(
                        row.get("fired")
                        for row in rules
                        if row.get("rule_id") == "R11"
                    ),
                ),
            ),
            "rule.R11",
            "metric.generic_capacity",
        ),
        _step(
            ExecutiveStepId.PUBLIC_CONCLUSION,
            _values(
                ("state", decision.get("state")),
                ("gap_class", gap.get("primary")),
                ("preferred_route_code", preferred_code),
                ("rationale", decision.get("rationale")),
            ),
            "decision.public",
        ),
        _step(
            ExecutiveStepId.MISSING_MINISTRY_FACTS,
            (
                _value("need_codes", ",".join(needs), need_codes=needs),
                _value(
                    "dataset_kinds",
                    ",".join(
                        sorted(
                            {
                                classify_need_code(code).value
                                for code in needs
                            }
                        )
                    ),
                ),
            ),
            "rule.R12",
        ),
        _step(
            ExecutiveStepId.SIMULATED_EVIDENCE,
            _values(
                ("scenario_id", scenario.get("scenario_id")),
                ("evidence_class", "D" if not absent else None),
                ("warning_label", scenario.get("display_label")),
                unavailable=absent,
                evidence_ids=claim_evidence.get(simulated_step_id, ()),
            ),
            *((simulated_step_id, "decision.simulated") if not absent else ()),
            unavailable=absent,
            public_claim=absent,
        ),
        _step(
            ExecutiveStepId.ROUTE_COMPARISON,
            (
                _value("public_route_code", decision.get("route_code")),
                _value(
                    "simulated_route_code",
                    sim_decision.get("route_code"),
                    unavailable=absent,
                    evidence_ids=claim_evidence.get(route_step_id, ()),
                ),
                _value("route_hypothesis_count", len(routes)),
            ),
            *routes,
            *((route_step_id,) if not absent else ()),
        ),
        _step(
            ExecutiveStepId.INTERVENTION,
            _values(
                ("simulated_selected_route_code", sim_decision.get("route_code")),
                ("simulated_unsupported_npv_m_sar", economics.get("unsupported_npv_m")),
                (
                    "simulated_minimum_effective_support_m_sar",
                    economics.get("minimum_effective_support_m"),
                ),
                (
                    "simulated_incremental_national_value_m_sar",
                    national_value.get("incremental_national_value_m_sar"),
                ),
                ("simulated_approximate_evsi_m_sar", evsi.get("approximate_evsi_m_sar")),
                unavailable=absent,
                evidence_ids=claim_evidence.get(intervention_step_id, ()),
            ),
            *((intervention_step_id,) if not absent else ()),
            unavailable=absent,
            public_claim=False,
        ),
        _step(
            ExecutiveStepId.CONDITIONS_AND_KILL,
            (
                _value(
                    "public_conditions",
                    " | ".join(decision.get("conditions", ())),
                ),
                _value(
                    "public_kill_conditions",
                    " | ".join(decision.get("kill_conditions", ())),
                ),
                _value(
                    "simulated_conditions",
                    (
                        " | ".join(sim_decision.get("conditions", ()))
                        if not absent
                        else None
                    ),
                    unavailable=absent,
                    evidence_ids=claim_evidence.get(conditions_step_id, ()),
                ),
                _value(
                    "simulated_kill_conditions",
                    (
                        " | ".join(sim_decision.get("kill_conditions", ()))
                        if not absent
                        else None
                    ),
                    unavailable=absent,
                    evidence_ids=claim_evidence.get(conditions_step_id, ()),
                ),
            ),
            "decision.public",
            *((conditions_step_id,) if not absent else ()),
        ),
    )


def build_vectors(public: Analysis) -> tuple[DecisionVector, ...]:
    """Project four separate methodology section 8 decision vectors."""

    gap = _mapping(public.get("gap_class"), "gap")
    capability = _mapping(public.get("capability"), "capability")
    decision = _mapping(public.get("real_decision"), "decision")
    assessments = _mapping(
        public.get("evidence_class_assessment"),
        "assessments",
    )
    trade = max(
        _rows(public.get("trade"), "trade"),
        key=lambda row: row["year"],
    )
    unresolved = sum(
        _mapping(row, "assessment").get("resolution_status") != "RESOLVED"
        for row in assessments.values()
    )

    def vector(
        vector_id: DecisionVectorId,
        claims: tuple[str, ...],
        values: tuple[ExecutiveValue, ...],
    ) -> DecisionVector:
        return DecisionVector(
            vector_id=vector_id,
            availability=AvailabilityStatus.AVAILABLE,
            claim_ids=claims,
            values=values,
        )

    return (
        vector(
            DecisionVectorId.MARKET_GAP,
            ("metric.trade", "decision.public"),
            _values(
                ("gap_class", gap.get("primary")),
                ("latest_imports_usd_m", trade.get("imports_usd_m")),
            ),
        ),
        vector(
            DecisionVectorId.STRATEGIC_RESILIENCE,
            ("decision.public",),
            _values(
                ("secondary_gap_classes", ",".join(gap.get("secondary", ()))),
                (
                    "criticality_designation",
                    public.get("criticality_designation"),
                ),
            ),
        ),
        vector(
            DecisionVectorId.EXECUTION_FEASIBILITY,
            (
                "metric.product_specification",
                "metric.supply_capability",
                "metric.generic_capacity",
            ),
            _values(
                ("route_publishable", capability.get("route_publishable")),
                ("d_star", capability.get("d_star")),
                (
                    "unresolved_hard_gate_count",
                    len(capability.get("unresolved_hard_gates", ())),
                ),
            ),
        ),
        vector(
            DecisionVectorId.EVIDENCE_CONFIDENCE,
            ("decision.public", "rule.R12"),
            _values(
                ("decision_confidence", decision.get("confidence")),
                ("unresolved_assessment_count", unresolved),
                ("missing_fact_count", len(decision.get("missing_facts", ()))),
            ),
        ),
    )
