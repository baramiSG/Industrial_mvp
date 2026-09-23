"""Branch-aware provenance models for executive claims and evidence."""

from __future__ import annotations

from enum import Enum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ClaimStatus(str, Enum):
    """Evidence resolution state for one executive claim."""

    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"


class DecisionBranch(str, Enum):
    """Executive comparison and claim branches."""

    PUBLIC = "PUBLIC"
    SIMULATED = "SIMULATED"


class EvidenceClass(str, Enum):
    """Governed evidence classes."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class EvidenceStatus(str, Enum):
    """Canonical evidence-record statuses."""

    OBSERVED = "observed"
    CALCULATED = "calculated"
    MODEL_ESTIMATED = "model_estimated"
    INFERRED = "inferred"
    ASSUMPTION = "assumption"
    UNRESOLVED = "unresolved"
    SYNTHETIC = "synthetic"


class FrozenModel(BaseModel):
    """Common immutable, fail-closed response-model configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class PolicyLabels(FrozenModel):
    """Bilingual policy-owned synthetic warning labels."""

    en: str = Field(min_length=1)
    ar: str = Field(min_length=1)


class ClaimReference(FrozenModel):
    """Stable branch-qualified claim with stored evidence or missing needs."""

    claim_id: str = Field(min_length=1)
    status: ClaimStatus
    evidence_ids: tuple[str, ...] = ()
    missing_need_codes: tuple[str, ...] = ()
    branch: DecisionBranch = DecisionBranch.PUBLIC
    synthetic_flag: bool = False
    scenario_id: str | None = None
    evidence_class: EvidenceClass | None = None
    source: str | None = None
    display_labels: PolicyLabels | None = None

    @model_validator(mode="after")
    def _validate_resolution_and_branch(self) -> Self:
        if self.status is ClaimStatus.UNRESOLVED:
            if self.evidence_ids or not self.missing_need_codes:
                raise ValueError(
                    "unresolved claims require missing needs and no evidence ids"
                )
        elif not self.evidence_ids:
            raise ValueError("resolved claims require stored evidence ids")
        metadata = (
            self.scenario_id,
            self.evidence_class,
            self.source,
            self.display_labels,
        )
        if self.branch is DecisionBranch.PUBLIC:
            if self.synthetic_flag or any(value is not None for value in metadata):
                raise ValueError("public claims cannot carry synthetic metadata")
            return self
        if (
            not self.synthetic_flag
            or not self.scenario_id
            or self.evidence_class is not EvidenceClass.D
            or self.source != "DEMO_GENERATOR"
            or self.display_labels is None
        ):
            raise ValueError(
                "simulated claims require complete Class-D metadata"
            )
        if self.status is ClaimStatus.UNRESOLVED:
            raise ValueError(
                "scenario-qualified simulated claims require stored evidence"
            )
        return self


class EvidenceReference(FrozenModel):
    """Stored evidence row exposed by exact evidence identifier."""

    evidence_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    status: EvidenceStatus
    evidence_class: EvidenceClass
    synthetic_flag: bool
    supports: tuple[str, ...]
    contradiction: str | None = None
    scenario_id: str | None = None
    display_labels: PolicyLabels | None = None

    @model_validator(mode="after")
    def _validate_partition(self) -> Self:
        if self.synthetic_flag:
            if (
                self.status is not EvidenceStatus.SYNTHETIC
                or self.evidence_class is not EvidenceClass.D
                or self.source != "DEMO_GENERATOR"
                or not self.scenario_id
                or self.display_labels is None
            ):
                raise ValueError(
                    "synthetic evidence reference metadata is invalid"
                )
        elif (self.scenario_id is not None or self.display_labels is not None
              or self.status is EvidenceStatus.SYNTHETIC
              or self.source == "DEMO_GENERATOR"):
            raise ValueError("public evidence cannot carry synthetic metadata")
        return self
