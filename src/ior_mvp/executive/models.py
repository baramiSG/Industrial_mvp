"""Frozen typed contracts for executive projections."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Self

from pydantic import Field, model_validator

from .provenance_models import (
    ClaimReference,
    ClaimStatus,
    DecisionBranch,
    EvidenceClass,
    EvidenceReference,
    EvidenceStatus,
    FrozenModel,
    PolicyLabels,
)

class ExecutiveStepId(str, Enum):
    """Fixed progressive executive narrative steps."""

    SIGNAL = "SIGNAL"
    FALSE_POSITIVE_CONTROLS = "FALSE_POSITIVE_CONTROLS"
    PUBLIC_CONCLUSION = "PUBLIC_CONCLUSION"
    MISSING_MINISTRY_FACTS = "MISSING_MINISTRY_FACTS"
    SIMULATED_EVIDENCE = "SIMULATED_EVIDENCE"
    ROUTE_COMPARISON = "ROUTE_COMPARISON"
    INTERVENTION = "INTERVENTION"
    CONDITIONS_AND_KILL = "CONDITIONS_AND_KILL"


class DecisionVectorId(str, Enum):
    """Separate methodology section 8 decision vectors."""

    MARKET_GAP = "MARKET_GAP"
    STRATEGIC_RESILIENCE = "STRATEGIC_RESILIENCE"
    EXECUTION_FEASIBILITY = "EXECUTION_FEASIBILITY"
    EVIDENCE_CONFIDENCE = "EVIDENCE_CONFIDENCE"


class DatasetKind(str, Enum):
    """Governed classes of missing public datasets."""

    IDENTITY_TARIFF = "IDENTITY_TARIFF"
    TARGET_SPECIFICATION_DEMAND = "TARGET_SPECIFICATION_DEMAND"
    PRODUCER_CAPABILITY = "PRODUCER_CAPABILITY"
    EFFECTIVE_CAPACITY_ALLOCATION = "EFFECTIVE_CAPACITY_ALLOCATION"
    RETAINED_FLOW = "RETAINED_FLOW"
    ROUTE_ECONOMICS = "ROUTE_ECONOMICS"
    UNMAPPED = "UNMAPPED"


class AvailabilityStatus(str, Enum):
    """Whether a projected value exists and is calculable."""

    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_CALCULABLE = "NOT_CALCULABLE"


class DecisionState(str, Enum):
    """Formal methodology decision states."""

    REJECT = "REJECT"
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    ADVANCE = "ADVANCE"


class IntegrityResult(str, Enum):
    """Computed executive integrity outcome."""

    PASS = "PASS"
    FAIL = "FAIL"


class IntegrityCheckId(str, Enum):
    """Required live integrity checks."""

    PUBLIC_SYNTHETIC_LEAKAGE = "PUBLIC_SYNTHETIC_LEAKAGE"
    REAL_DECISION_EQUALITY = "REAL_DECISION_EQUALITY"
    SYNTHETIC_METADATA = "SYNTHETIC_METADATA"
    SCENARIO_VALIDATION = "SCENARIO_VALIDATION"


class AuthorityReference(FrozenModel):
    """One authority identity exposed by an executive response."""

    key: str = Field(min_length=1)
    value: str = Field(min_length=1)


class OpportunityReference(FrozenModel):
    """Stable public identity for one loaded opportunity."""

    opportunity_id: str = Field(min_length=1)
    hs6: str = Field(pattern=r"^\d{6}$")
    name_en: str = Field(min_length=1)
    name_ar: str = Field(min_length=1)
    sector_profile: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)
    as_of_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class ExecutiveValue(FrozenModel):
    """One scalar value in a step or decision vector."""

    key: str = Field(min_length=1)
    availability: AvailabilityStatus
    value: str | int | float | bool | None
    unit: str | None = None
    evidence_ids: tuple[str, ...] = ()
    need_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_availability(self) -> Self:
        if self.availability is AvailabilityStatus.AVAILABLE and self.value is None:
            raise ValueError("available executive values require a value")
        if self.availability is not AvailabilityStatus.AVAILABLE and self.value is not None:
            raise ValueError("unavailable executive values cannot carry a value")
        return self


class DecisionProjection(FrozenModel):
    """One public or simulated decision branch."""

    branch: DecisionBranch
    availability: AvailabilityStatus
    state: DecisionState | None
    route_code: int | None = Field(default=None, ge=0, le=8)
    synthetic_flag: bool
    scenario_id: str | None = None
    evidence_class: EvidenceClass | None = None
    source: str | None = None
    display_labels: PolicyLabels | None = None
    headline: str | None = None
    rationale: str | None = None
    conditions: tuple[str, ...]
    kill_conditions: tuple[str, ...]

    @model_validator(mode="after")
    def _validate_branch(self) -> Self:
        synthetic_metadata = (
            self.scenario_id,
            self.evidence_class,
            self.source,
            self.display_labels,
        )
        if self.branch is DecisionBranch.PUBLIC:
            if self.synthetic_flag or any(value is not None for value in synthetic_metadata):
                raise ValueError("public decisions cannot carry synthetic metadata")
            return self
        if self.availability is AvailabilityStatus.UNAVAILABLE:
            if self.synthetic_flag or any(value is not None for value in synthetic_metadata):
                raise ValueError("unavailable simulation cannot carry synthetic metadata")
            return self
        if (
            not self.synthetic_flag
            or not self.scenario_id
            or self.evidence_class is not EvidenceClass.D
            or self.source != "DEMO_GENERATOR"
            or self.display_labels is None
        ):
            raise ValueError("available simulation requires complete Class-D metadata")
        if self.state is None:
            raise ValueError("available simulation requires a decision state")
        return self


class DecisionComparison(FrozenModel):
    """Side-by-side public and simulated decisions."""

    public: DecisionProjection
    simulated: DecisionProjection

    @model_validator(mode="after")
    def _validate_branches(self) -> Self:
        if self.public.branch is not DecisionBranch.PUBLIC:
            raise ValueError("public comparison branch is invalid")
        if self.simulated.branch is not DecisionBranch.SIMULATED:
            raise ValueError("simulated comparison branch is invalid")
        return self


class ExecutiveStep(FrozenModel):
    """One ordered progressive executive step."""

    step_id: ExecutiveStepId
    availability: AvailabilityStatus
    claim_ids: tuple[str, ...]
    values: tuple[ExecutiveValue, ...]


class DecisionVector(FrozenModel):
    """One separate, non-combined methodology section 8 vector."""

    vector_id: DecisionVectorId
    availability: AvailabilityStatus
    claim_ids: tuple[str, ...]
    values: tuple[ExecutiveValue, ...]


class DatasetUnlock(FrozenModel):
    """Public-derived dataset count kept separate from synthetic EVSI."""

    dataset_kind: DatasetKind
    need_codes: tuple[str, ...]
    synthetic_flag: Literal[False]
    loaded_case_count: int = Field(ge=0)
    loaded_opportunity_ids: tuple[str, ...]
    screening_record_count: int = Field(ge=0)
    screening_hs6: tuple[str, ...]

    @model_validator(mode="after")
    def _validate_counts(self) -> Self:
        if self.loaded_case_count != len(self.loaded_opportunity_ids):
            raise ValueError("loaded-case count does not match affected ids")
        if self.screening_record_count != len(self.screening_hs6):
            raise ValueError("screening count does not match affected HS6 values")
        if not self.need_codes:
            raise ValueError("dataset unlock requires at least one need code")
        return self


class SyntheticEvsiCase(FrozenModel):
    """One scenario-declared Class-D EVSI projection."""

    opportunity_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    availability: AvailabilityStatus
    next_fact: str | None = None
    approximate_evsi_m_sar: float | None = Field(default=None, strict=True, allow_inf_nan=False)
    route_change_probability: float | None = Field(default=None, strict=True, allow_inf_nan=False)
    value_difference_m_sar: float | None = Field(default=None, strict=True, allow_inf_nan=False)
    evidence_cost_m_sar: float | None = Field(default=None, strict=True, allow_inf_nan=False)
    delay_cost_m_sar: float | None = Field(default=None, strict=True, allow_inf_nan=False)

    @model_validator(mode="after")
    def _validate_values(self) -> Self:
        numeric = (
            self.approximate_evsi_m_sar,
            self.route_change_probability,
            self.value_difference_m_sar,
            self.evidence_cost_m_sar,
            self.delay_cost_m_sar,
        )
        if self.availability is AvailabilityStatus.AVAILABLE:
            if any(value is None for value in numeric):
                raise ValueError("available EVSI requires every numeric input and result")
        elif any(value is not None for value in numeric):
            raise ValueError("unavailable EVSI cannot carry numeric values")
        return self


class SyntheticEvsiSummary(FrozenModel):
    """Class-D EVSI aggregate isolated from public dataset counts."""

    synthetic_flag: Literal[True]
    evidence_class: EvidenceClass
    source: str
    display_labels: PolicyLabels
    available_case_count: int = Field(ge=0)
    unavailable_case_count: int = Field(ge=0)
    total_approximate_evsi_m_sar: float
    positive_approximate_evsi_m_sar: float
    non_positive_approximate_evsi_m_sar: float
    cases: tuple[SyntheticEvsiCase, ...]

    @model_validator(mode="after")
    def _validate_branch(self) -> Self:
        if self.evidence_class is not EvidenceClass.D or self.source != "DEMO_GENERATOR":
            raise ValueError("EVSI summary must remain Class D and generator-sourced")
        available = sum(
            case.availability is AvailabilityStatus.AVAILABLE for case in self.cases
        )
        if available != self.available_case_count:
            raise ValueError("available EVSI count does not match case rows")
        if len(self.cases) - available != self.unavailable_case_count:
            raise ValueError("unavailable EVSI count does not match case rows")
        return self


class IntegrityCheck(FrozenModel):
    """One computed integrity check and affected identifiers."""

    check_id: IntegrityCheckId
    status: IntegrityResult
    violation_count: int = Field(ge=0)
    affected_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_result(self) -> Self:
        expected = (
            IntegrityResult.PASS
            if self.violation_count == 0
            else IntegrityResult.FAIL
        )
        if self.status is not expected:
            raise ValueError("integrity check status does not match violations")
        return self


class IntegritySummary(FrozenModel):
    """Computed overall integrity result."""

    status: IntegrityResult
    violation_count: int = Field(ge=0)
    checks: tuple[IntegrityCheck, ...]

    @model_validator(mode="after")
    def _validate_checks(self) -> Self:
        if tuple(check.check_id for check in self.checks) != tuple(IntegrityCheckId):
            raise ValueError("integrity checks must be complete and ordered")
        total = sum(check.violation_count for check in self.checks)
        if total != self.violation_count:
            raise ValueError("integrity violation count does not match checks")
        expected = IntegrityResult.PASS if total == 0 else IntegrityResult.FAIL
        if self.status is not expected:
            raise ValueError("integrity summary status does not match violations")
        return self


class ExecutiveSummary(FrozenModel):
    """Portfolio-level executive projection."""

    schema_version: str
    opportunities: tuple[OpportunityReference, ...]
    public_dataset_unlocks: tuple[DatasetUnlock, ...]
    synthetic_evsi: SyntheticEvsiSummary
    integrity: IntegritySummary
    authority: tuple[AuthorityReference, ...]

    @model_validator(mode="after")
    def _validate_uniqueness(self) -> Self:
        opportunity_ids = tuple(row.opportunity_id for row in self.opportunities)
        if len(opportunity_ids) != len(set(opportunity_ids)):
            raise ValueError("summary opportunity ids must be unique")
        kinds = tuple(row.dataset_kind for row in self.public_dataset_unlocks)
        if len(kinds) != len(set(kinds)):
            raise ValueError("dataset unlock kinds must be unique")
        return self


class ExecutiveCase(FrozenModel):
    """Case-level executive projection with claims and stored evidence."""

    schema_version: str
    opportunity: OpportunityReference
    decisions: DecisionComparison
    steps: tuple[ExecutiveStep, ...]
    vectors: tuple[DecisionVector, ...]
    claims: tuple[ClaimReference, ...]
    evidence_index: tuple[EvidenceReference, ...]
    authority: tuple[AuthorityReference, ...]

    @model_validator(mode="after")
    def _validate_contract(self) -> Self:
        if tuple(step.step_id for step in self.steps) != tuple(ExecutiveStepId):
            raise ValueError("executive steps must be complete and ordered")
        if tuple(vector.vector_id for vector in self.vectors) != tuple(DecisionVectorId):
            raise ValueError("decision vectors must be complete and ordered")
        claim_ids = tuple(claim.claim_id for claim in self.claims)
        evidence_ids = tuple(row.evidence_id for row in self.evidence_index)
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("claim ids must be unique")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence ids must be unique")
        known_claims = set(claim_ids)
        referenced_claims = {
            claim_id
            for row in (*self.steps, *self.vectors)
            for claim_id in row.claim_ids
        }
        if not referenced_claims <= known_claims:
            raise ValueError("steps and vectors reference unknown claims")
        known_evidence = set(evidence_ids)
        referenced_evidence = {
            evidence_id
            for claim in self.claims
            for evidence_id in claim.evidence_ids
        } | {
            evidence_id
            for row in (*self.steps, *self.vectors)
            for value in row.values
            for evidence_id in value.evidence_ids
        }
        if not referenced_evidence <= known_evidence:
            raise ValueError("executive projection references unknown evidence")
        evidence_by_id = {
            row.evidence_id: row for row in self.evidence_index
        }
        for claim in self.claims:
            referenced_rows = tuple(
                evidence_by_id[evidence_id]
                for evidence_id in claim.evidence_ids
            )
            synthetic_rows = tuple(
                row for row in referenced_rows if row.synthetic_flag
            )
            if claim.branch is DecisionBranch.PUBLIC and synthetic_rows:
                raise ValueError(
                    "public claims cannot reference synthetic evidence"
                )
            if claim.branch is DecisionBranch.SIMULATED:
                if not synthetic_rows:
                    raise ValueError(
                        "simulated claims require scenario evidence"
                    )
                if any(
                    row.scenario_id != claim.scenario_id
                    or row.evidence_class is not EvidenceClass.D
                    or row.source != claim.source
                    or row.display_labels != claim.display_labels
                    for row in synthetic_rows
                ):
                    raise ValueError(
                        "simulated claim evidence metadata is inconsistent"
                    )
        return self
