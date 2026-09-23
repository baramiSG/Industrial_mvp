"""Deterministic executive claims linked only to stored evidence."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ior_mvp.evidence import synthetic_display_labels

from .models import (
    AuthorityReference,
    AvailabilityStatus,
    ClaimReference,
    ClaimStatus,
    DecisionBranch,
    DecisionProjection,
    DecisionState,
    EvidenceClass,
    ExecutiveStepId,
    OpportunityReference,
    PolicyLabels,
)
from .taxonomy import ExecutiveIntegrityError

TRADE_SUPPORTS = frozenset(
    {"TRADE_VALUE", "TRADE_QUANTITY", "SUPPLIER_CONCENTRATION"}
)
PRODUCT_SPECIFICATION_SUPPORTS = frozenset(
    {
        "TARGET_PRODUCT_IDENTITY",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
    }
)
GENERIC_CAPACITY_SUPPORTS = frozenset({"EXPORT_IMPORT_RATIO"})

TRADE_NEEDS = ("identity/tariff-line",)
PRODUCT_SPECIFICATION_NEEDS = (
    "identity/tariff-line",
    "line-level production or producer-grade matrix",
    "target specification/application",
)
SUPPLY_NEEDS = (
    "capacity/availability/allocation",
    "line-level production or producer-grade matrix",
)
GENERIC_CAPACITY_NEEDS = (
    "capacity/availability/allocation",
    "route economics",
)


@dataclass(frozen=True)
class _Evidence:
    evidence_id: str
    supports: frozenset[str]
    contradiction: bool
    synthetic: bool


def _mapping_rows(value: Any, *, field: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ExecutiveIntegrityError(f"{field} must be a sequence")
    if not all(isinstance(row, Mapping) for row in value):
        raise ExecutiveIntegrityError(f"{field} must contain mappings")
    return tuple(value)


def _text_sequence(value: Any, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ExecutiveIntegrityError(f"{field} must be a sequence of strings")
    if not all(isinstance(item, str) and item for item in value):
        raise ExecutiveIntegrityError(f"{field} must contain non-empty strings")
    return tuple(value)


def _looks_synthetic(row: Mapping[str, Any]) -> bool:
    return (
        row.get("synthetic_flag") is True
        or row.get("status") == "synthetic"
        or row.get("source") == "DEMO_GENERATOR"
        or row.get("scenario_id") is not None
    )


def _evidence_index(
    analysis: Mapping[str, Any],
) -> dict[str, _Evidence]:
    index: dict[str, _Evidence] = {}
    for row in _mapping_rows(analysis.get("evidence"), field="analysis.evidence"):
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ExecutiveIntegrityError("Evidence id must be a non-empty string")
        if evidence_id in index:
            raise ExecutiveIntegrityError(
                f"Duplicate stored evidence id: {evidence_id}"
            )
        supports = _text_sequence(
            row.get("supports", ()),
            field=f"evidence {evidence_id} supports",
        )
        contradiction = row.get("contradiction")
        index[evidence_id] = _Evidence(
            evidence_id=evidence_id,
            supports=frozenset(supports),
            contradiction=bool(contradiction),
            synthetic=_looks_synthetic(row),
        )
    return index


def _domestic_supports(index: Mapping[str, _Evidence]) -> frozenset[str]:
    return frozenset(
        support
        for evidence in index.values()
        for support in evidence.supports
        if support.startswith("DOMESTIC_")
    )


def _ids_for_supports(
    index: Mapping[str, _Evidence],
    supports: Iterable[str],
) -> tuple[str, ...]:
    accepted = frozenset(supports)
    return tuple(
        sorted(
            evidence.evidence_id
            for evidence in index.values()
            if evidence.supports & accepted
        )
    )


def _validate_ids(
    evidence_ids: Iterable[str],
    index: Mapping[str, _Evidence],
) -> tuple[str, ...]:
    stable_ids = tuple(sorted(set(evidence_ids)))
    absent = tuple(
        evidence_id
        for evidence_id in stable_ids
        if evidence_id not in index
    )
    if absent:
        raise ExecutiveIntegrityError(
            f"Claim references absent evidence ids: {', '.join(absent)}"
        )
    return stable_ids


def _linked_claim_status(contradictions: Iterable[Any]) -> ClaimStatus:
    """Preserve any truthy contradiction among the claim's linked rows."""
    return ClaimStatus.CONTRADICTED if any(contradictions) else ClaimStatus.SUPPORTED


def _claim(
    *,
    claim_id: str,
    evidence_ids: Iterable[str],
    missing_need_codes: Iterable[str],
    index: Mapping[str, _Evidence],
) -> ClaimReference:
    stable_ids = _validate_ids(evidence_ids, index)
    if not stable_ids:
        needs = tuple(sorted(set(missing_need_codes)))
        if not needs:
            raise ExecutiveIntegrityError(f"Claim {claim_id} has no support or missing need")
        return ClaimReference(
            claim_id=claim_id,
            status=ClaimStatus.UNRESOLVED,
            missing_need_codes=needs,
        )
    if any(index[evidence_id].synthetic for evidence_id in stable_ids):
        raise ExecutiveIntegrityError(
            f"Public claim {claim_id} cannot link synthetic evidence"
        )
    status = _linked_claim_status(index[evidence_id].contradiction for evidence_id in stable_ids)
    return ClaimReference(
        claim_id=claim_id,
        status=status,
        evidence_ids=stable_ids,
    )


def _r12_inputs(
    analysis: Mapping[str, Any],
    index: Mapping[str, _Evidence],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    rules = _mapping_rows(analysis.get("rules"), field="analysis.rules")
    r12 = next((row for row in rules if row.get("rule_id") == "R12"), None)
    if r12 is None:
        raise ExecutiveIntegrityError("analysis.rules must contain R12")
    metrics = r12.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ExecutiveIntegrityError("R12 metrics must be a mapping")
    needs = _mapping_rows(
        metrics.get("evidence_needs", ()),
        field="metrics.evidence_needs",
    )
    evidence_ids: list[str] = []
    need_codes: list[str] = []
    for need in needs:
        need_code = need.get("need_code")
        if not isinstance(need_code, str) or not need_code:
            raise ExecutiveIntegrityError("Evidence need code is missing")
        need_codes.append(need_code)
        evidence_ids.extend(
            _text_sequence(
                need.get("evidence_ids", ()),
                field=f"evidence need {need_code} evidence_ids",
            )
        )
    return _validate_ids(evidence_ids, index), tuple(sorted(set(need_codes)))


def _rule_evidence(
    *,
    rule_id: str,
    support_ids: Mapping[str, tuple[str, ...]],
    r12_ids: tuple[str, ...],
) -> tuple[str, ...]:
    if rule_id == "R12":
        return r12_ids
    if rule_id in {
        "R1-F",
        "R1-D",
        "R2",
        "R3",
        "R4-F",
        "R4-D",
        "R5",
    }:
        return support_ids["trade"]
    if rule_id == "R0":
        return support_ids["product"]
    if rule_id == "R9-S":
        return support_ids["supply"]
    if rule_id == "R11":
        return support_ids["generic"]
    return ()


def _append_unique(
    claims: list[ClaimReference],
    claim: ClaimReference,
    claim_ids: set[str],
) -> None:
    if claim.claim_id in claim_ids:
        raise ExecutiveIntegrityError(
            f"Duplicate executive claim id: {claim.claim_id}"
        )
    claim_ids.add(claim.claim_id)
    claims.append(claim)


def build_claim_registry(
    analysis: Mapping[str, Any],
    simulated_analysis: Mapping[str, Any] | None = None,
) -> tuple[ClaimReference, ...]:
    """Build immutable branch-aware claims from stored evidence relationships."""

    index = _evidence_index(analysis)
    domestic_supports = _domestic_supports(index)
    support_ids = {
        "trade": _ids_for_supports(index, TRADE_SUPPORTS),
        "product": _ids_for_supports(index, PRODUCT_SPECIFICATION_SUPPORTS),
        "supply": _ids_for_supports(index, domestic_supports),
        "generic": _ids_for_supports(
            index,
            GENERIC_CAPACITY_SUPPORTS | domestic_supports,
        ),
    }
    r12_ids, r12_needs = _r12_inputs(analysis, index)
    claims: list[ClaimReference] = []
    claim_ids: set[str] = set()

    metric_specs = (
        ("metric.trade", support_ids["trade"], TRADE_NEEDS),
        ("metric.concentration", _ids_for_supports(
            index, {"SUPPLIER_CONCENTRATION"}
        ), TRADE_NEEDS),
        (
            "metric.product_specification",
            support_ids["product"],
            PRODUCT_SPECIFICATION_NEEDS,
        ),
        ("metric.supply_capability", support_ids["supply"], SUPPLY_NEEDS),
        (
            "metric.generic_capacity",
            support_ids["generic"],
            GENERIC_CAPACITY_NEEDS,
        ),
    )
    for claim_id, evidence_ids, need_codes in metric_specs:
        _append_unique(
            claims,
            _claim(
                claim_id=claim_id,
                evidence_ids=evidence_ids,
                missing_need_codes=need_codes,
                index=index,
            ),
            claim_ids,
        )

    fired_evidence: set[str] = set()
    for rule in _mapping_rows(
        analysis.get("rules"),
        field="analysis.rules",
    ):
        rule_id = rule.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id:
            raise ExecutiveIntegrityError("Rule id must be a non-empty string")
        evidence_ids = _rule_evidence(
            rule_id=rule_id,
            support_ids=support_ids,
            r12_ids=r12_ids,
        )
        if rule.get("fired") is True:
            fired_evidence.update(evidence_ids)
        _append_unique(
            claims,
            _claim(
                claim_id=f"rule.{rule_id}",
                evidence_ids=evidence_ids,
                missing_need_codes=r12_needs,
                index=index,
            ),
            claim_ids,
        )

    decision_ids = tuple(sorted(fired_evidence))
    _append_unique(
        claims,
        _claim(
            claim_id="decision.public",
            evidence_ids=decision_ids,
            missing_need_codes=r12_needs,
            index=index,
        ),
        claim_ids,
    )

    route_evidence: set[str] = set()
    for route in _mapping_rows(
        analysis.get("route_hypotheses"),
        field="analysis.route_hypotheses",
    ):
        route_code = route.get("route_code")
        if not isinstance(route_code, int):
            raise ExecutiveIntegrityError("Route code must be an integer")
        direct_ids = _text_sequence(
            route.get("evidence_ids", ()),
            field=f"route {route_code} evidence_ids",
        )
        evidence_ids = _validate_ids(
            (*direct_ids, *fired_evidence),
            index,
        )
        route_evidence.update(evidence_ids)
        _append_unique(
            claims,
            _claim(
                claim_id=f"route.{route_code}",
                evidence_ids=evidence_ids,
                missing_need_codes=r12_needs,
                index=index,
            ),
            claim_ids,
        )

    step_inputs = {
        ExecutiveStepId.SIGNAL: support_ids["trade"],
        ExecutiveStepId.FALSE_POSITIVE_CONTROLS: tuple(
            sorted(
                {
                    *support_ids["product"],
                    *support_ids["supply"],
                    *support_ids["generic"],
                }
            )
        ),
        ExecutiveStepId.PUBLIC_CONCLUSION: decision_ids,
        ExecutiveStepId.MISSING_MINISTRY_FACTS: r12_ids,
        ExecutiveStepId.SIMULATED_EVIDENCE: (),
        ExecutiveStepId.ROUTE_COMPARISON: tuple(sorted(route_evidence)),
        ExecutiveStepId.INTERVENTION: tuple(sorted(route_evidence)),
        ExecutiveStepId.CONDITIONS_AND_KILL: decision_ids,
    }
    for step_id in ExecutiveStepId:
        _append_unique(
            claims,
            _claim(
                claim_id=f"step.{step_id.value}",
                evidence_ids=step_inputs[step_id],
                missing_need_codes=r12_needs,
                index=index,
            ),
            claim_ids,
        )
    public_claims = tuple(claims)
    if simulated_analysis is None:
        return public_claims
    from .provenance import build_simulated_claim_registry

    return public_claims + build_simulated_claim_registry(
        analysis,
        simulated_analysis,
        public_claims,
    )


def build_opportunity_reference(analysis: Mapping[str, Any]) -> OpportunityReference:
    """Project the stored public opportunity identity."""

    row = analysis.get("opportunity")
    if not isinstance(row, Mapping):
        raise ExecutiveIntegrityError("opportunity must be a mapping")
    return OpportunityReference(
        opportunity_id=str(row["id"]),
        hs6=str(row["hs6"]),
        name_en=str(row["commercial_name_en"]),
        name_ar=str(row["commercial_name_ar"]),
        sector_profile=str(row["sector_profile"]),
        snapshot_id=str(analysis["snapshot_id"]),
        as_of_date=str(analysis["as_of_date"]),
    )


def build_authority_references(
    analysis: Mapping[str, Any],
) -> tuple[AuthorityReference, ...]:
    """Project deterministic methodology and configuration identities."""

    authority = analysis.get("authority")
    if not isinstance(authority, Mapping):
        raise ExecutiveIntegrityError("authority must be a mapping")
    methodology = authority.get("methodology")
    versions = authority.get("config_versions")
    if not isinstance(methodology, Mapping) or not isinstance(versions, Mapping):
        raise ExecutiveIntegrityError("authority metadata is invalid")
    values = {
        "project_version": authority.get("project_version"),
        "methodology.sha256": methodology.get("sha256"),
        **{f"config.{key}": value for key, value in versions.items()},
    }
    if not all(isinstance(value, str) and value for value in values.values()):
        raise ExecutiveIntegrityError("Executive authority values are invalid")
    return tuple(
        AuthorityReference(key=key, value=values[key]) for key in sorted(values)
    )


def build_decision_projection(
    analysis: Mapping[str, Any] | None,
    branch: DecisionBranch,
) -> DecisionProjection:
    """Project one public or Class-D decision branch."""

    if analysis is None:
        return DecisionProjection(
            branch=branch,
            availability=AvailabilityStatus.UNAVAILABLE,
            state=None,
            synthetic_flag=False,
            conditions=(),
            kill_conditions=(),
        )
    key = "real_decision" if branch is DecisionBranch.PUBLIC else "simulation_decision"
    row = analysis.get(key)
    if not isinstance(row, Mapping):
        raise ExecutiveIntegrityError(f"{key} must be a mapping")
    values = {
        "branch": branch,
        "availability": AvailabilityStatus.AVAILABLE,
        "state": DecisionState(row["state"]),
        "route_code": row.get("route_code"),
        "headline": row.get("headline"),
        "rationale": row.get("rationale"),
        "conditions": tuple(row.get("conditions", ())),
        "kill_conditions": tuple(row.get("kill_conditions", ())),
    }
    if branch is DecisionBranch.PUBLIC:
        return DecisionProjection(**values, synthetic_flag=False)
    scenario = analysis.get("simulation_scenario")
    if not isinstance(scenario, Mapping):
        raise ExecutiveIntegrityError("simulation_scenario must be a mapping")
    return DecisionProjection(
        **values,
        synthetic_flag=True,
        scenario_id=str(scenario["scenario_id"]),
        evidence_class=EvidenceClass.D,
        source="DEMO_GENERATOR",
        display_labels=PolicyLabels(**synthetic_display_labels()),
    )
