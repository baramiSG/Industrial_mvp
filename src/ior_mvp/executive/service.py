"""Cached read-only builders for executive API projections."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import lru_cache
from math import fsum
from typing import Any

from ior_mvp.config import project_config
from ior_mvp.data_repository import public_cases, synthetic_scenarios
from ior_mvp.decision_engine import analyze
from ior_mvp.evidence import synthetic_display_labels
from ior_mvp.screening.repository import iter_screening_records

from .case_projection import build_steps, build_vectors
from .claims import (
    build_authority_references, build_claim_registry, build_decision_projection,
    build_opportunity_reference,
)
from .models import (
    AvailabilityStatus, DecisionBranch, DecisionComparison, EvidenceClass,
    ExecutiveCase, ExecutiveSummary, IntegrityCheck, IntegrityCheckId,
    IntegrityResult, IntegritySummary, PolicyLabels, SyntheticEvsiCase,
    SyntheticEvsiSummary,
)
from .provenance import build_evidence_index
from .taxonomy import (
    ExecutiveIntegrityError, build_dataset_unlocks, extract_case_need_codes,
)

EXECUTIVE_SCHEMA_VERSION = "1.0.0"
SYNTHETIC_SOURCE = "DEMO_GENERATOR"
Analysis = Mapping[str, Any]
Pair = tuple[str, Analysis, Analysis | None]


class ExecutiveOpportunityNotFoundError(LookupError):
    """Raised when an executive case identity is not loaded."""


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


def _opportunity_order() -> tuple[str, ...]:
    configured = [
        row["opportunity_id"]
        for row in project_config().get("golden_cases", ())
        if isinstance(row, Mapping)
        and isinstance(row.get("opportunity_id"), str)
    ]
    loaded = public_cases()
    known = tuple(row for row in configured if row in loaded)
    return known + tuple(sorted(set(loaded) - set(configured)))


def _analysis_pairs() -> tuple[Pair, ...]:
    scenarios = set(synthetic_scenarios())
    return tuple(
        (opportunity_id, analyze(opportunity_id, "public"),
         analyze(opportunity_id, "simulated") if opportunity_id in scenarios else None)
        for opportunity_id in _opportunity_order()
    )


def _dataset_unlocks(pairs: Sequence[Pair]):
    loaded = {
        opportunity_id: extract_case_need_codes(public) for opportunity_id, public, _ in pairs
    }
    return build_dataset_unlocks(loaded, iter_screening_records())


def _integrity_summary(pairs: Sequence[Pair]) -> IntegritySummary:
    affected = {check_id: [] for check_id in IntegrityCheckId}
    labels = synthetic_display_labels()
    for opportunity_id, public, simulated in pairs:
        public_evidence = _rows(public.get("evidence"), "public evidence")
        marked = lambda row: (
            row.get("synthetic_flag") is True
            or row.get("status") == "synthetic"
            or row.get("source") == SYNTHETIC_SOURCE
            or row.get("scenario_id") is not None
        )
        if any(marked(row) for row in public_evidence):
            affected[IntegrityCheckId.PUBLIC_SYNTHETIC_LEAKAGE].append(opportunity_id)
        if simulated is None:
            continue
        if public.get("real_decision") != simulated.get("real_decision"):
            affected[IntegrityCheckId.REAL_DECISION_EQUALITY].append(opportunity_id)
        scenario = _mapping(simulated.get("simulation_scenario"), "scenario")
        scenario_id = scenario.get("scenario_id")
        synthetic = tuple(
            row
            for row in _rows(simulated.get("evidence"), "simulated evidence")
            if marked(row)
        )
        metadata_bad = (
            not isinstance(scenario_id, str)
            or scenario.get("display_labels") != labels
            or not synthetic
            or any(
                row.get("synthetic_flag") is not True
                or row.get("status") != "synthetic"
                or row.get("source") != SYNTHETIC_SOURCE
                or row.get("evidence_class") != "D"
                or row.get("scenario_id") != scenario_id
                for row in synthetic
            )
        )
        if metadata_bad:
            affected[IntegrityCheckId.SYNTHETIC_METADATA].append(opportunity_id)
        integrity = _mapping(simulated.get("integrity"), "integrity")
        reconciliation = _mapping(integrity.get("scenario_reconciliation"), "reconciliation")
        backtest = _mapping(integrity.get("ground_truth_backtest"), "backtest")
        if (
            reconciliation.get("status") != "PASS"
            or backtest.get("match") is not True
        ):
            affected[IntegrityCheckId.SCENARIO_VALIDATION].append(opportunity_id)
    checks = tuple(
        IntegrityCheck(
            check_id=check_id,
            status=IntegrityResult.FAIL if affected[check_id] else IntegrityResult.PASS,
            violation_count=len(affected[check_id]),
            affected_ids=tuple(affected[check_id]),
        )
        for check_id in IntegrityCheckId
    )
    total = sum(row.violation_count for row in checks)
    return IntegritySummary(
        status=IntegrityResult.FAIL if total else IntegrityResult.PASS,
        violation_count=total,
        checks=checks,
    )


def _evsi_summary(pairs: Sequence[Pair]) -> SyntheticEvsiSummary:
    cases: list[SyntheticEvsiCase] = []
    for opportunity_id, _, simulated in pairs:
        if simulated is None:
            continue
        scenario = _mapping(simulated.get("simulation_scenario"), "scenario")
        scenario_id = scenario.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise ExecutiveIntegrityError("Simulation scenario id is invalid")
        raw = simulated.get("evsi")
        if raw is None:
            cases.append(
                SyntheticEvsiCase(
                    opportunity_id=opportunity_id,
                    scenario_id=scenario_id,
                    availability=AvailabilityStatus.UNAVAILABLE,
                )
            )
            continue
        evsi = _mapping(raw, "EVSI")
        next_fact = evsi.get("next_fact")
        if not isinstance(next_fact, str) or not next_fact:
            raise ExecutiveIntegrityError("Available EVSI next_fact is invalid")
        cases.append(
            SyntheticEvsiCase(
                opportunity_id=opportunity_id,
                scenario_id=scenario_id,
                availability=AvailabilityStatus.AVAILABLE,
                next_fact=next_fact,
                approximate_evsi_m_sar=float(evsi["approximate_evsi_m_sar"]),
                route_change_probability=float(evsi["route_change_probability"]),
                value_difference_m_sar=float(evsi["value_difference_m_sar"]),
                evidence_cost_m_sar=float(evsi["evidence_cost_m_sar"]),
                delay_cost_m_sar=float(evsi["delay_cost_m_sar"]),
            )
        )
    values = tuple(
        row.approximate_evsi_m_sar
        for row in cases
        if row.approximate_evsi_m_sar is not None
    )
    return SyntheticEvsiSummary(
        synthetic_flag=True,
        evidence_class=EvidenceClass.D,
        source=SYNTHETIC_SOURCE,
        display_labels=PolicyLabels(**synthetic_display_labels()),
        available_case_count=len(values),
        unavailable_case_count=len(cases) - len(values),
        total_approximate_evsi_m_sar=fsum(values),
        positive_approximate_evsi_m_sar=fsum(row for row in values if row > 0),
        non_positive_approximate_evsi_m_sar=fsum(
            row for row in values if row <= 0
        ),
        cases=tuple(cases),
    )


@lru_cache(maxsize=1)
def build_executive_summary() -> ExecutiveSummary:
    """Build the immutable executive portfolio summary."""

    pairs = _analysis_pairs()
    if not pairs:
        raise ExecutiveIntegrityError("No public analyses are loaded")
    return ExecutiveSummary(
        schema_version=EXECUTIVE_SCHEMA_VERSION,
        opportunities=tuple(build_opportunity_reference(row) for _, row, _ in pairs),
        public_dataset_unlocks=_dataset_unlocks(pairs),
        synthetic_evsi=_evsi_summary(pairs),
        integrity=_integrity_summary(pairs),
        authority=build_authority_references(pairs[0][1]),
    )


@lru_cache(maxsize=32)
def build_executive_case(opportunity_id: str) -> ExecutiveCase:
    """Build one immutable executive case projection."""

    if opportunity_id not in public_cases():
        raise ExecutiveOpportunityNotFoundError(opportunity_id)
    public = analyze(opportunity_id, "public")
    simulated = (analyze(opportunity_id, "simulated")
                 if opportunity_id in synthetic_scenarios() else None)
    claims = build_claim_registry(public, simulated)
    claim_evidence = {
        claim.claim_id: claim.evidence_ids for claim in claims
    }
    evidence_source = simulated if simulated is not None else public
    return ExecutiveCase(
        schema_version=EXECUTIVE_SCHEMA_VERSION,
        opportunity=build_opportunity_reference(public),
        decisions=DecisionComparison(
            public=build_decision_projection(public, DecisionBranch.PUBLIC),
            simulated=build_decision_projection(simulated, DecisionBranch.SIMULATED),
        ),
        steps=build_steps(public, simulated, claim_evidence),
        vectors=build_vectors(public),
        claims=claims,
        evidence_index=build_evidence_index(evidence_source),
        authority=build_authority_references(public),
    )


def clear_executive_caches() -> None:
    """Clear cached executive projections for tests and operator reloads."""

    build_executive_summary.cache_clear()
    build_executive_case.cache_clear()
