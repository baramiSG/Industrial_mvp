"""Branch-aware simulated claim and evidence provenance projection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ior_mvp.data_repository import RepositoryError, synthetic_scenarios
from ior_mvp.evidence import (
    EvidenceIntegrityError, synthetic_display_labels, synthetic_evidence_rows,
)
from ior_mvp.graph.engine_feed import shared_enabler_inputs
from ior_mvp.graph.repository import GraphRepositoryError, graph_projection

from .claims import _linked_claim_status

from .models import (
    ClaimReference,
    DecisionBranch,
    EvidenceClass,
    EvidenceReference,
    EvidenceStatus,
    PolicyLabels,
)
from .taxonomy import ExecutiveIntegrityError

ROUTE_SUFFIXES = frozenset(
    {
        "route_evidence",
        "counterfactual",
        "hard_exclusion_inputs",
        "class_if_confirmed",
    }
)
INTERVENTION_SUFFIXES = frozenset(
    {"economics", "evsi", "route_evidence", "counterfactual"}
)


@dataclass(frozen=True)
class _SimulationEvidence:
    scenario_id: str
    labels: PolicyLabels
    combined_ids: frozenset[str]
    indexed_rows: Mapping[str, Mapping[str, Any]]
    public_ids: frozenset[str]
    synthetic_ids: frozenset[str]
    synthetic_by_suffix: Mapping[str, str]


def _rows(value: Any, *, field: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ExecutiveIntegrityError(f"{field} must be a sequence")
    if not all(isinstance(row, Mapping) for row in value):
        raise ExecutiveIntegrityError(f"{field} must contain mappings")
    return tuple(value)


def _row_id(row: Mapping[str, Any]) -> str:
    evidence_id = row.get("evidence_id")
    if not isinstance(evidence_id, str) or not evidence_id:
        raise ExecutiveIntegrityError("Evidence id must be a non-empty string")
    return evidence_id


def _indexed_rows(
    analysis: Mapping[str, Any],
    *,
    field: str,
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in _rows(analysis.get("evidence"), field=field):
        evidence_id = _row_id(row)
        if evidence_id in indexed:
            raise ExecutiveIntegrityError(
                f"Duplicate stored evidence id: {evidence_id}"
            )
        indexed[evidence_id] = row
    return indexed


def _looks_synthetic(row: Mapping[str, Any]) -> bool:
    return (
        row.get("synthetic_flag") is True
        or row.get("status") == "synthetic"
        or row.get("source") == "DEMO_GENERATOR"
        or row.get("scenario_id") is not None
    )


def _simulation_evidence(
    public: Mapping[str, Any],
    simulated: Mapping[str, Any],
) -> _SimulationEvidence:
    scenario = simulated.get("simulation_scenario")
    if not isinstance(scenario, Mapping):
        raise ExecutiveIntegrityError("simulation_scenario must be a mapping")
    scenario_id = scenario.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ExecutiveIntegrityError("Simulation scenario id is invalid")
    expected_labels = synthetic_display_labels()
    if (
        scenario.get("display_label") != expected_labels["en"]
        or scenario.get("display_labels") != expected_labels
    ):
        raise ExecutiveIntegrityError(
            f"Simulation scenario labels are invalid: {scenario_id}"
        )
    labels = PolicyLabels(**expected_labels)
    public_rows = _indexed_rows(public, field="public evidence")
    combined_rows = _indexed_rows(simulated, field="simulated evidence")
    synthetic_ids: set[str] = set()
    by_suffix: dict[str, str] = {}
    for evidence_id, row in combined_rows.items():
        if not _looks_synthetic(row):
            if evidence_id not in public_rows or row != public_rows[evidence_id]:
                raise ExecutiveIntegrityError(
                    f"Simulated branch contains invalid public evidence: {evidence_id}"
                )
            continue
        if (
            row.get("synthetic_flag") is not True
            or row.get("status") != "synthetic"
            or row.get("source") != "DEMO_GENERATOR"
            or row.get("evidence_class") != "D"
            or row.get("scenario_id") != scenario_id
            or row.get("display_label") != expected_labels["en"]
            or row.get("display_labels") != expected_labels
        ):
            raise ExecutiveIntegrityError(
                f"Synthetic evidence metadata or scenario is invalid: {evidence_id}"
            )
        prefix = f"{scenario_id}::"
        if not evidence_id.startswith(prefix):
            raise ExecutiveIntegrityError(
                f"Synthetic evidence id does not match scenario: {evidence_id}"
            )
        suffix = evidence_id.removeprefix(prefix)
        if not suffix or suffix in by_suffix:
            raise ExecutiveIntegrityError(
                f"Synthetic evidence suffix is invalid: {evidence_id}"
            )
        by_suffix[suffix] = evidence_id
        synthetic_ids.add(evidence_id)
    if not synthetic_ids:
        raise ExecutiveIntegrityError(
            f"Simulation scenario has no Class-D evidence: {scenario_id}"
        )
    return _SimulationEvidence(
        scenario_id=scenario_id,
        labels=labels,
        combined_ids=frozenset(combined_rows),
        indexed_rows=combined_rows,
        public_ids=frozenset(public_rows),
        synthetic_ids=frozenset(synthetic_ids),
        synthetic_by_suffix=by_suffix,
    )


def _reference_ids(value: Any, path: tuple[str | int, ...]) -> tuple[str, ...]:
    if (not isinstance(value, Sequence) or isinstance(value, (str, bytes))
            or any(not isinstance(item, str) or not item.strip() for item in value)):
        raise ExecutiveIntegrityError(f"Malformed evidence ids at {path}")
    return tuple(value)


def _evidence_references(
    value: Any, path: tuple[str | int, ...] = (),
) -> list[tuple[tuple[str | int, ...], tuple[str, ...]]]:
    references = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            location = (*path, key)
            if key == "evidence_ids":
                references.append((location, _reference_ids(item, location)))
            else:
                references.extend(_evidence_references(item, location))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            references.extend(_evidence_references(item, (*path, index)))
    return references


def _shared_enabler_allowance(
    public: Mapping[str, Any], decision: Mapping[str, Any], evidence: _SimulationEvidence,
) -> dict[tuple[str | int, ...], frozenset[str]]:
    """Validate the graph feed and stored dependencies before allowing foreign IDs."""
    routes = _rows(decision.get("route_hypotheses"), field="simulated routes")
    candidates = [(i, row) for i, row in enumerate(routes) if row.get("route_code") == 8]
    if not any("shared_enabler" in row for _, row in candidates):
        return {}
    if len(candidates) != 1 or type(candidates[0][1].get("route_code")) is not int:
        raise ExecutiveIntegrityError("Shared enabler requires one integer route 8")
    index, route = candidates[0]
    payload = route.get("shared_enabler")
    opportunity = public.get("opportunity")
    opportunity_id = opportunity.get("id") if isinstance(opportunity, Mapping) else None
    if not isinstance(payload, Mapping) or not isinstance(opportunity_id, str):
        raise ExecutiveIntegrityError("Shared-enabler payload or opportunity is invalid")
    try:
        feed = shared_enabler_inputs(
            graph_projection(), opportunity_id, branch=("simulated", evidence.scenario_id),
        )
        scenarios = synthetic_scenarios()
    except (GraphRepositoryError, RepositoryError, EvidenceIntegrityError, ValueError, OSError) as exc:
        raise ExecutiveIntegrityError("Shared-enabler dependency sources are unavailable or invalid") from exc
    if not isinstance(feed, Mapping):
        raise ExecutiveIntegrityError("Shared enabler has no bound graph feed")
    for field in ("enabler_id", "graph_projection_id", "dependent_opportunity_ids"):
        if field not in feed or payload.get(field) != feed[field]:
            raise ExecutiveIntegrityError(f"Shared-enabler {field} differs from bound graph feed")
    dependents = _reference_ids(feed["dependent_opportunity_ids"], ("dependent_opportunity_ids",))
    if opportunity_id not in dependents or len(set(dependents)) != len(dependents):
        raise ExecutiveIntegrityError("Shared-enabler current opportunity membership is invalid")
    verified: set[str] = set()
    for dependent in dependents:
        scenario = scenarios.get(dependent)
        if not isinstance(scenario, dict) or scenario.get("opportunity_id") != dependent:
            raise ExecutiveIntegrityError(f"Missing dependent scenario: {dependent}")
        scenario_id = scenario.get("scenario_id")
        if (not isinstance(scenario_id, str) or not scenario_id
                or sum(row.get("scenario_id") == scenario_id for row in scenarios.values()) != 1
                or (dependent == opportunity_id and scenario_id != evidence.scenario_id)):
            raise ExecutiveIntegrityError("Shared-enabler scenario membership is invalid")
        declaration = scenario.get("synthetic_inputs", {}).get("shared_enabler")
        if not isinstance(declaration, Mapping) or declaration.get("enabler_id") != feed["enabler_id"]:
            raise ExecutiveIntegrityError(f"Missing or forged shared-enabler declaration: {dependent}")
        try:
            stored_rows = synthetic_evidence_rows(scenario)
        except (EvidenceIntegrityError, ValueError, KeyError, TypeError) as exc:
            raise ExecutiveIntegrityError(f"Invalid dependent scenario evidence: {dependent}") from exc
        stored_ids = tuple(_row_id(row) for row in stored_rows)
        required_id = f"{scenario_id}::shared_enabler"
        if len(set(stored_ids)) != len(stored_ids) or required_id not in stored_ids:
            raise ExecutiveIntegrityError(f"Missing or duplicate stored dependency evidence: {required_id}")
        verified.add(required_id)
    route_path = ("route_hypotheses", index, "evidence_ids")
    nested_path = ("route_hypotheses", index, "shared_enabler", "evidence_ids")
    for path, raw in ((route_path, route.get("evidence_ids")),
                      (nested_path, payload.get("evidence_ids")),
                      (("graph_feed", "evidence_ids"), feed.get("evidence_ids"))):
        ids = _reference_ids(raw, path)
        if len(ids) != len(set(ids)) or set(ids) != verified:
            raise ExecutiveIntegrityError(f"Shared-enabler evidence differs from verified dependencies at {path}")
    foreign = frozenset(verified - {f"{evidence.scenario_id}::shared_enabler"})
    return {route_path: foreign, nested_path: foreign}


def _decision_evidence_ids(
    public: Mapping[str, Any], decision: Mapping[str, Any], evidence: _SimulationEvidence,
) -> set[str]:
    references = _evidence_references(decision)
    allowance = _shared_enabler_allowance(public, decision, evidence)
    local_ids: set[str] = set()
    for path, ids in references:
        for evidence_id in ids:
            if evidence_id in evidence.combined_ids:
                local_ids.add(evidence_id)
            elif evidence_id not in allowance.get(path, ()):
                raise ExecutiveIntegrityError(f"Absent or foreign evidence id at {path}: {evidence_id}")
    return local_ids


def _ids_for_suffixes(
    evidence: _SimulationEvidence,
    suffixes: frozenset[str],
) -> set[str]:
    return {
        evidence.synthetic_by_suffix[suffix]
        for suffix in suffixes
        if suffix in evidence.synthetic_by_suffix
    }


def _simulated_claim(
    *,
    claim_id: str,
    evidence_ids: set[str],
    evidence: _SimulationEvidence,
) -> ClaimReference:
    absent = evidence_ids - evidence.combined_ids
    if absent:
        raise ExecutiveIntegrityError(
            "Simulated claim references absent evidence ids: "
            + ", ".join(sorted(absent))
        )
    if not evidence_ids & evidence.synthetic_ids:
        raise ExecutiveIntegrityError(
            f"Simulated claim lacks current-scenario evidence: {claim_id}"
        )
    return ClaimReference(
        claim_id=claim_id,
        status=_linked_claim_status(
            evidence.indexed_rows[evidence_id].get("contradiction") for evidence_id in evidence_ids
        ),
        evidence_ids=tuple(sorted(evidence_ids)),
        branch=DecisionBranch.SIMULATED,
        synthetic_flag=True,
        scenario_id=evidence.scenario_id,
        evidence_class=EvidenceClass.D,
        source="DEMO_GENERATOR",
        display_labels=evidence.labels,
    )


def build_simulated_claim_registry(
    public: Mapping[str, Any],
    simulated: Mapping[str, Any],
    public_claims: Sequence[ClaimReference],
) -> tuple[ClaimReference, ...]:
    """Build exact current-scenario claims for the simulated branch."""

    evidence = _simulation_evidence(public, simulated)
    decision = simulated.get("simulation_decision")
    if not isinstance(decision, Mapping):
        raise ExecutiveIntegrityError("simulation_decision must be a mapping")
    public_decision = next(
        (
            claim
            for claim in public_claims
            if claim.claim_id == "decision.public"
        ),
        None,
    )
    if public_decision is None:
        raise ExecutiveIntegrityError("Public decision claim is missing")
    decision_ids = _decision_evidence_ids(public, decision, evidence)
    decision_ids.update(public_decision.evidence_ids)
    if (
        isinstance(decision.get("counterfactual"), Mapping)
        and "counterfactual" in evidence.synthetic_by_suffix
    ):
        decision_ids.add(evidence.synthetic_by_suffix["counterfactual"])
    claims = (
        _simulated_claim(
            claim_id="decision.simulated",
            evidence_ids=decision_ids,
            evidence=evidence,
        ),
        _simulated_claim(
            claim_id="step.SIMULATED_EVIDENCE.simulated",
            evidence_ids=set(evidence.synthetic_ids),
            evidence=evidence,
        ),
        _simulated_claim(
            claim_id="step.ROUTE_COMPARISON.simulated",
            evidence_ids=_ids_for_suffixes(evidence, ROUTE_SUFFIXES),
            evidence=evidence,
        ),
        _simulated_claim(
            claim_id="step.INTERVENTION.simulated",
            evidence_ids=_ids_for_suffixes(evidence, INTERVENTION_SUFFIXES),
            evidence=evidence,
        ),
        _simulated_claim(
            claim_id="step.CONDITIONS_AND_KILL.simulated",
            evidence_ids=decision_ids,
            evidence=evidence,
        ),
    )
    if len({claim.claim_id for claim in claims}) != len(claims):
        raise ExecutiveIntegrityError("Simulated claim ids must be unique")
    return claims


def build_evidence_index(
    analysis: Mapping[str, Any],
) -> tuple[EvidenceReference, ...]:
    """Project a deterministic evidence index without changing provenance."""

    rows: dict[str, EvidenceReference] = {}
    for row in _rows(analysis.get("evidence"), field="analysis.evidence"):
        display_labels = row.get("display_labels")
        reference = EvidenceReference(
            evidence_id=_row_id(row),
            source=str(row["source"]),
            status=EvidenceStatus(row["status"]),
            evidence_class=EvidenceClass(row["evidence_class"]),
            synthetic_flag=row.get("synthetic_flag") is True,
            supports=tuple(row.get("supports", ())),
            contradiction=row.get("contradiction"),
            scenario_id=row.get("scenario_id"),
            display_labels=(
                PolicyLabels.model_validate(display_labels)
                if display_labels is not None
                else None
            ),
        )
        if reference.evidence_id in rows:
            raise ExecutiveIntegrityError(
                f"Duplicate executive evidence id: {reference.evidence_id}"
            )
        rows[reference.evidence_id] = reference
    return tuple(rows[key] for key in sorted(rows))
