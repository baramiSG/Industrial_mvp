"""Strict simulated candidate and line diagnostic response contracts."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, JsonValue, model_validator

from .provenance_models import EvidenceClass, FrozenModel

UnavailableReason = Literal["NO_SCENARIO", "NO_REGISTER", "NO_LINE_RECORDS"]
FindingStatus = Literal[
    "SUPPORTED", "LIMITATION_IDENTIFIED", "NOT_ESTABLISHED", "CONFLICTED",
    "NOT_REQUIRED",
]
FieldOrigin = Literal[
    "DIRECT_RECORD", "REVIEWED_INFERENCE", "ENGINEERING_DECLARATION", "UNKNOWN",
]


class SourcePointer(FrozenModel):
    """One exact Class-D local or allowlisted public source reference."""

    pointer: str | None = None
    artifact: str | None = None
    evidence_id: str | None = None
    purpose: str = Field(min_length=1)
    field: str | None = None

    @model_validator(mode="after")
    def _closed_reference(self) -> Self:
        local = self.pointer is not None
        public = self.artifact is not None or self.evidence_id is not None
        if local == public:
            raise ValueError("source pointer must be local or public")
        if local and (
            not self.pointer.startswith("/synthetic_inputs/candidate_register/facts/")
            or self.artifact is not None or self.evidence_id is not None
        ):
            raise ValueError("local source pointer is invalid")
        if public and (
            not self.artifact or not self.evidence_id or not self.field
            or self.pointer is not None
        ):
            raise ValueError("public source pointer is incomplete")
        return self


class RecordWindow(FrozenModel):
    start: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    end: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class NextEvidence(FrozenModel):
    need_code: str = Field(min_length=1)
    missing_field: str = Field(min_length=1)
    dataset_or_action: str = Field(min_length=1)
    route_effect: str = Field(min_length=1)
    subject_scope: str = Field(min_length=1)
    numeric_evsi: Literal["NOT_CALCULABLE"]
    action_code: str = Field(min_length=1)


class InputRecord(FrozenModel):
    fact_id: str = Field(min_length=1)
    origin: FieldOrigin
    subject_type: Literal["COMPANY", "PLANT", "LINE"]
    subject_id: str = Field(min_length=1)
    window: RecordWindow


class PreliminaryFinding(FrozenModel):
    requirement_item_id: str = Field(min_length=1)
    dimension: str = Field(min_length=1)
    current_recorded: JsonValue = None
    needed: JsonValue = None
    status: FindingStatus
    origin: FieldOrigin
    rule_id: Literal["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"]
    source_refs: tuple[SourcePointer, ...]
    input_records: tuple[InputRecord, ...] = ()
    temporal_scope: RecordWindow | None
    quantified_gap: float | None = Field(default=None, allow_inf_nan=False)
    reason_code: str = Field(min_length=1)
    action_code: str = Field(min_length=1)
    next_evidence: NextEvidence | None

    @model_validator(mode="after")
    def _request_binding(self) -> Self:
        if self.next_evidence is None:
            if self.action_code != "NO_ADDITIONAL_REQUEST":
                raise ValueError("missing next evidence for action")
        elif self.action_code != self.next_evidence.action_code:
            raise ValueError("finding and request action differ")
        if self.status == "SUPPORTED" and not self.source_refs:
            raise ValueError("supported finding requires a source")
        return self


class R9SScreen(FrozenModel):
    fired: bool | None
    result_code: str = Field(min_length=1)
    qualifying_signal_count: int = Field(ge=0)


class CandidateRow(FrozenModel):
    entity_id: str = Field(min_length=1)
    entity_kind: Literal["COMPANY", "PLANT", "LINE"]
    company_id: str = Field(min_length=1)
    company_name_en: str = Field(min_length=1)
    company_name_ar: str = Field(min_length=1)
    plant_id: str | None = None
    plant_status: Literal["OPERATING", "UNDER_ESTABLISHMENT"] | None = None
    assessment_depth: Literal["REGISTER_ONLY", "ENRICHED"]
    disposition: Literal[
        "PASS_TO_ASSESSMENT", "RELATED_ONLY", "NOT_ESTABLISHED", "OUTSIDE_TARGET",
    ]
    r9s: R9SScreen | None = None
    findings: tuple[PreliminaryFinding, ...]
    evidence_boundary: dict[str, JsonValue]
    next_evidence_actions: tuple[NextEvidence, ...]
    scenario_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def _scope(self) -> Self:
        if self.entity_kind == "LINE" and self.plant_id is None:
            raise ValueError("line diagnostic requires plant identity")
        if self.entity_kind == "PLANT" and self.r9s is None:
            raise ValueError("plant diagnostic requires R9-S")
        for finding in self.findings:
            if finding.next_evidence is not None and (
                finding.next_evidence.subject_scope != self.entity_id
            ):
                raise ValueError("finding request crosses subject scope")
        return self


class TargetRequirement(FrozenModel):
    """Validated Class-D request context, never a public observed specification."""

    target_name: str = Field(min_length=1)
    application: str = Field(min_length=1)
    specification: dict[str, JsonValue]
    target_demand_kt: float = Field(ge=0, allow_inf_nan=False)
    request_window_months: tuple[int, int]

    @model_validator(mode="after")
    def _window(self) -> Self:
        start, end = self.request_window_months
        if start < 0 or end <= start or not self.specification:
            raise ValueError("target requirement needs a finite scope and window")
        return self


class CandidateDiagnostic(FrozenModel):
    available: bool
    reason: UnavailableReason | None
    opportunity_id: str | None = None
    scenario_id: str | None = None
    target_family: str | None = None
    synthetic_flag: bool = False
    evidence_class: EvidenceClass | None = None
    source: str | None = None
    requirement: TargetRequirement | None = None
    rows: tuple[CandidateRow, ...]

    @model_validator(mode="after")
    def _branch(self) -> Self:
        if self.available:
            if (
                self.reason is not None or not self.scenario_id
                or self.requirement is None
                or not self.synthetic_flag or self.evidence_class is not EvidenceClass.D
                or self.source != "DEMO_GENERATOR"
                or any(row.scenario_id != self.scenario_id for row in self.rows)
            ):
                raise ValueError("available discovery requires current Class-D scenario")
        elif (
            self.reason is None or self.rows or self.requirement is not None or self.synthetic_flag
            or self.evidence_class is not None or self.source is not None
        ):
            raise ValueError("unavailable discovery cannot carry synthetic records")
        return self


class TechnicalComparison(FrozenModel):
    field_id: str = Field(min_length=1)
    current_recorded: JsonValue = None
    needed: JsonValue = None
    status: FindingStatus
    origin: FieldOrigin
    rule_id: Literal["P06", "P07"]


class CapacityDiagnostic(FrozenModel):
    formula_capacity_kt: float | None = Field(allow_inf_nan=False)
    admitted_qualified_supply_kt: float | None = Field(allow_inf_nan=False)
    allocation_basis: Literal["FORMULA", "DECLARED_ALLOCATION"]
    capacity_result: str = Field(min_length=1)
    window_result: str = Field(min_length=1)
    shortage_kt: float | None = Field(allow_inf_nan=False)


class CapabilityDimension(FrozenModel):
    dimension: str = Field(min_length=1)
    weight: float = Field(ge=0, le=1, allow_inf_nan=False)
    state: int | Literal["U"]
    known: bool

    @model_validator(mode="after")
    def _state(self) -> Self:
        if self.state not in {0, 1, 2, 3, "U"} or self.known != (self.state != "U"):
            raise ValueError("capability dimension state is invalid")
        return self


class LineRow(FrozenModel):
    line_id: str = Field(min_length=1)
    reference_role: Literal["REFERENCE_LINE", "ALTERNATIVE"]
    comparisons: tuple[TechnicalComparison, ...]
    gates: dict[str, str]
    gate_requirements: dict[str, tuple[str, ...]]
    known_weight_coverage: float | None = Field(allow_inf_nan=False)
    d_star: float | None = Field(allow_inf_nan=False)
    dimensions: tuple[CapabilityDimension, ...]
    declared_effort: dict[str, int | Literal["U"]] | None
    capacity: CapacityDiagnostic

    @model_validator(mode="after")
    def _gate_links(self) -> Self:
        fields = {row.field_id for row in self.comparisons}
        if set(self.gate_requirements) != set(self.gates) or any(
            field not in fields
            for linked in self.gate_requirements.values() for field in linked
        ):
            raise ValueError("gate requirements do not link to compared fields")
        return self


class LineDiagnostic(FrozenModel):
    available: bool
    reason: UnavailableReason | None
    scenario_id: str | None = None
    synthetic_flag: bool = False
    evidence_class: EvidenceClass | None = None
    source: str | None = None
    rows: tuple[LineRow, ...]
    winner: None = None

    @model_validator(mode="after")
    def _branch(self) -> Self:
        if self.available:
            if (
                self.reason is not None or not self.scenario_id
                or not self.synthetic_flag or self.evidence_class is not EvidenceClass.D
                or self.source != "DEMO_GENERATOR" or self.winner is not None
            ):
                raise ValueError("available line assessment requires current Class-D scenario")
        elif (
            self.reason is None or self.rows or self.synthetic_flag
            or self.evidence_class is not None or self.source is not None
        ):
            raise ValueError("unavailable line assessment cannot carry synthetic records")
        return self


def unavailable_candidates(reason: UnavailableReason = "NO_SCENARIO") -> CandidateDiagnostic:
    return CandidateDiagnostic(available=False, reason=reason, rows=())


def unavailable_lines(reason: UnavailableReason = "NO_SCENARIO") -> LineDiagnostic:
    return LineDiagnostic(available=False, reason=reason, rows=())
