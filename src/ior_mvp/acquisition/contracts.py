"""Acquisition domain contracts — query hashes, coverage records, source contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

UNAVAILABLE = "UNAVAILABLE"
PRODUCT_SCOPE_ALL = "ALL"
SELECTION_RULE = "LATEST_RUN_PER_SOURCE_STAGE_UNIT"


class AcquisitionError(RuntimeError):
    """Base acquisition error."""


class OfflineGuardViolation(AcquisitionError):
    """Live network access attempted without explicit operator permission."""


class RawStoreIntegrityError(AcquisitionError):
    """Raw store write-once or hash verification failure."""


class SnapshotWriteConflict(AcquisitionError):
    """Snapshot write-once conflict."""


class AcquisitionConfigurationError(AcquisitionError):
    """Acquisition configuration validation failure."""


class SnapshotReconstructionError(AcquisitionError):
    """Snapshot reconstruction failure."""


class UnavailableReason(StrEnum):
    CREDENTIAL_ABSENT = "CREDENTIAL_ABSENT"
    ENDPOINT_UNVERIFIED = "ENDPOINT_UNVERIFIED"
    NETWORK_ERROR = "NETWORK_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    MAX_REQUESTS_EXHAUSTED = "MAX_REQUESTS_EXHAUSTED"
    LICENSE_UNRECORDED = "LICENSE_UNRECORDED"
    LICENSE_NOT_PERMITTED = "LICENSE_NOT_PERMITTED"
    PAID_ACCESS_REQUIRED = "PAID_ACCESS_REQUIRED"
    SIZE_BUDGET_EXCEEDED = "SIZE_BUDGET_EXCEEDED"
    FORMAT_NOT_PARSEABLE = "FORMAT_NOT_PARSEABLE"
    COVERAGE_INDETERMINATE = "COVERAGE_INDETERMINATE"
    COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE"
    NO_UNITS_IN_STORE = "NO_UNITS_IN_STORE"
    REPORTER_MISMATCH = "REPORTER_MISMATCH"
    OUT_OF_SCOPE_CONTENT = "OUT_OF_SCOPE_CONTENT"
    OPERATOR_DISABLED = "OPERATOR_DISABLED"


class CompletenessBasis(StrEnum):
    SINGLE_RESPONSE_NO_PAGINATION = "SINGLE_RESPONSE_NO_PAGINATION"
    SOURCE_TOTAL_INDICATOR = "SOURCE_TOTAL_INDICATOR"
    TERMINAL_PAGE_REACHED = "TERMINAL_PAGE_REACHED"
    INDEX_ENUMERATION_COMPLETE = "INDEX_ENUMERATION_COMPLETE"
    UNAVAILABLE = "UNAVAILABLE"


class Stage(StrEnum):
    UNIVERSE = "UNIVERSE"
    PARTNERS = "PARTNERS"
    TARIFF = "TARIFF"
    TERMS = "TERMS"
    BULK = "BULK"


class ProductScope(StrEnum):
    ALL_HS6 = "ALL_HS6"
    ALL_TARIFF_LINES = "ALL_TARIFF_LINES"
    EXPLICIT = "EXPLICIT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class AcquisitionUnavailable(AcquisitionError):
    """Acquisition unit or build unavailable with a governed reason."""

    def __init__(
        self,
        reason: UnavailableReason,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(reason.value)
        self.reason = reason
        self.detail = detail or {}


def canonical_dumps(obj: Any) -> str:
    """Serialize to canonical JSON with trailing newline."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def sha256_bytes(data: bytes) -> str:
    """Return SHA-256 hex digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def utc_now_iso(clock: datetime | None = None) -> str:
    """Return UTC ISO-8601 timestamp with Z suffix."""
    moment = clock or datetime.now(UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id(clock: datetime | None = None) -> str:
    """Return a lexicographically sortable UTC run identifier."""
    moment = clock or datetime.now(UTC)
    return moment.strftime("%Y%m%dT%H%M%SZ")


def source_tag(source_id: str) -> str:
    """Map source_id to snapshot ID tag segment."""
    return source_id.upper().replace("_", "-")


@dataclass(frozen=True)
class QueryContract:
    source_id: str
    stage: Stage
    reporter: str
    partner: str
    flow: str
    product_scope: ProductScope
    product_codes: tuple[str, ...]
    nomenclature: str
    periods: tuple[str, ...]
    parameters: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.stage == Stage.UNIVERSE:
            if self.product_scope != ProductScope.ALL_HS6:
                raise AcquisitionConfigurationError(
                    "UNIVERSE requires product_scope ALL_HS6"
                )
            if self.product_codes != (PRODUCT_SCOPE_ALL,):
                raise AcquisitionConfigurationError(
                    "UNIVERSE requires product_codes ('ALL',)"
                )
            if len(self.periods) != 1:
                raise AcquisitionConfigurationError(
                    "UNIVERSE requires exactly one period per contract"
                )
        elif self.stage == Stage.PARTNERS:
            if self.product_scope != ProductScope.EXPLICIT:
                raise AcquisitionConfigurationError(
                    "PARTNERS requires product_scope EXPLICIT"
                )
            if PRODUCT_SCOPE_ALL in self.product_codes:
                raise AcquisitionConfigurationError(
                    "PARTNERS rejects product_codes containing 'ALL'"
                )
            for code in self.product_codes:
                if len(code) != 6 or not code.isdigit():
                    raise AcquisitionConfigurationError(
                        f"PARTNERS requires 6-digit HS6 codes: {code!r}"
                    )
            if len(self.periods) != 1:
                raise AcquisitionConfigurationError(
                    "PARTNERS requires exactly one period per contract"
                )
        elif self.stage == Stage.TARIFF:
            if self.product_scope != ProductScope.ALL_TARIFF_LINES:
                raise AcquisitionConfigurationError(
                    "TARIFF requires product_scope ALL_TARIFF_LINES"
                )
            if self.product_codes != (PRODUCT_SCOPE_ALL,):
                raise AcquisitionConfigurationError(
                    "TARIFF requires product_codes ('ALL',)"
                )
        elif self.stage == Stage.TERMS:
            if self.product_scope != ProductScope.NOT_APPLICABLE:
                raise AcquisitionConfigurationError(
                    "TERMS requires product_scope NOT_APPLICABLE"
                )
            if self.product_codes != ():
                raise AcquisitionConfigurationError(
                    "TERMS requires empty product_codes"
                )
        elif self.stage == Stage.BULK:
            if len(self.periods) != 1:
                raise AcquisitionConfigurationError(
                    "BULK requires exactly one period per contract"
                )

    def canonical_json(self) -> str:
        """Return canonical JSON representation for hashing."""
        payload = {
            "source_id": self.source_id,
            "stage": self.stage.value,
            "reporter": self.reporter,
            "partner": self.partner,
            "flow": self.flow,
            "product_scope": self.product_scope.value,
            "product_codes": list(self.product_codes),
            "nomenclature": self.nomenclature,
            "periods": list(self.periods),
            "parameters": [
                {"key": key, "value": value}
                for key, value in sorted(self.parameters)
            ],
        }
        return canonical_dumps(payload)

    def query_hash(self) -> str:
        """Return SHA-256 of canonical contract JSON."""
        return sha256_bytes(self.canonical_json().encode("utf-8"))


def unit_key(contract: QueryContract) -> tuple[str, ...]:
    """Return the acquisition unit key per DD-21."""
    if contract.stage == Stage.UNIVERSE:
        return (contract.flow, contract.periods[0])
    if contract.stage == Stage.PARTNERS:
        return (contract.product_codes[0], contract.flow, contract.periods[0])
    if contract.stage == Stage.TARIFF:
        return ("ALL_TARIFF_LINES",)
    if contract.stage == Stage.BULK:
        return (contract.periods[0],)
    if contract.stage == Stage.TERMS:
        return ("TERMS",)
    raise AcquisitionConfigurationError(f"Unknown stage for unit_key: {contract.stage}")


@dataclass(frozen=True)
class PageMeta:
    page_index: int
    pages_expected: int | str
    next_page_token_present: bool
    rows_in_page: int | str
    enumerated_children: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ObservedResponse:
    http_status: int | None
    headers_subset: tuple[tuple[str, str], ...]
    body_sha256: str | None
    body_byte_count: int | None
    error_type: str | None
    error_message_redacted: str | None

    def to_json(self) -> dict[str, Any]:
        return {
            "http_status": self.http_status,
            "headers_subset": [
                {"name": name, "value": value}
                for name, value in self.headers_subset
            ],
            "body_sha256": self.body_sha256,
            "body_byte_count": self.body_byte_count,
            "error_type": self.error_type,
            "error_message_redacted": self.error_message_redacted,
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> ObservedResponse:
        headers_raw = payload.get("headers_subset", [])
        headers: tuple[tuple[str, str], ...] = tuple(
            (item["name"], item["value"])
            for item in headers_raw
            if isinstance(item, dict)
        )
        return cls(
            http_status=payload.get("http_status"),
            headers_subset=headers,
            body_sha256=payload.get("body_sha256"),
            body_byte_count=payload.get("body_byte_count"),
            error_type=payload.get("error_type"),
            error_message_redacted=payload.get("error_message_redacted"),
        )


@dataclass(frozen=True)
class CoverageRecord:
    source_id: str
    stage: Stage
    query_hash: str
    run_id: str
    unit_key: tuple[str, ...]
    unit: dict[str, Any]
    pages_fetched: int
    pages_expected: int | str
    requests_made: int
    status: str
    completeness_basis: CompletenessBasis
    stop_reason: UnavailableReason | None
    missing_pages: tuple[int, ...]
    observed_stop: ObservedResponse | None

    def to_json(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "stage": self.stage.value,
            "query_hash": self.query_hash,
            "run_id": self.run_id,
            "unit_key": list(self.unit_key),
            "unit": self.unit,
            "pages_fetched": self.pages_fetched,
            "pages_expected": self.pages_expected,
            "requests_made": self.requests_made,
            "status": self.status,
            "completeness_basis": self.completeness_basis.value,
            "stop_reason": (
                self.stop_reason.value if self.stop_reason else None
            ),
            "missing_pages": list(self.missing_pages),
            "observed_stop": (
                self.observed_stop.to_json() if self.observed_stop else None
            ),
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> CoverageRecord:
        observed = payload.get("observed_stop")
        stop_raw = payload.get("stop_reason")
        return cls(
            source_id=str(payload["source_id"]),
            stage=Stage(payload["stage"]),
            query_hash=str(payload["query_hash"]),
            run_id=str(payload["run_id"]),
            unit_key=tuple(payload["unit_key"]),
            unit=dict(payload["unit"]),
            pages_fetched=int(payload["pages_fetched"]),
            pages_expected=payload["pages_expected"],
            requests_made=int(payload["requests_made"]),
            status=str(payload["status"]),
            completeness_basis=CompletenessBasis(payload["completeness_basis"]),
            stop_reason=(
                UnavailableReason(stop_raw) if stop_raw else None
            ),
            missing_pages=tuple(payload.get("missing_pages", [])),
            observed_stop=(
                ObservedResponse.from_json(observed)
                if isinstance(observed, dict)
                else None
            ),
        )


@dataclass(frozen=True)
class SourceContractRecord:
    source_id: str
    authority: str
    access_classification: str
    endpoint_or_document: str
    query_contract: QueryContract
    reporter: str
    partner: str
    flow: str
    product_code: str
    product_scope: str
    nomenclature: str
    period: str
    retrieved_at: str
    source_refresh_date: str
    raw_file_path: str
    sha256: str
    license_or_usage_note: str
    query_hash: str
    run_id: str
    page_index: int
    page_meta: PageMeta | None
    compressed_sha256: str
    byte_count: int
    content_type: str
    http_status: int
    response_headers_subset: tuple[tuple[str, str], ...]
    credential_env_var: str | None
    credential_used: bool
    normalization_status: str
    normalization_reason: str | None

    def to_json(self) -> dict[str, Any]:
        contract = self.query_contract
        meta = self.page_meta
        return {
            "source_id": self.source_id,
            "authority": self.authority,
            "access_classification": self.access_classification,
            "endpoint_or_document": self.endpoint_or_document,
            "query_contract": json.loads(contract.canonical_json()),
            "reporter": self.reporter,
            "partner": self.partner,
            "flow": self.flow,
            "product_code": self.product_code,
            "product_scope": self.product_scope,
            "nomenclature": self.nomenclature,
            "period": self.period,
            "retrieved_at": self.retrieved_at,
            "source_refresh_date": self.source_refresh_date,
            "raw_file_path": self.raw_file_path,
            "sha256": self.sha256,
            "license_or_usage_note": self.license_or_usage_note,
            "query_hash": self.query_hash,
            "run_id": self.run_id,
            "page_index": self.page_index,
            "page_meta": (
                {
                    "page_index": meta.page_index,
                    "pages_expected": meta.pages_expected,
                    "next_page_token_present": meta.next_page_token_present,
                    "rows_in_page": meta.rows_in_page,
                    "enumerated_children": (
                        list(meta.enumerated_children)
                        if meta.enumerated_children is not None
                        else None
                    ),
                }
                if meta
                else None
            ),
            "compressed_sha256": self.compressed_sha256,
            "byte_count": self.byte_count,
            "content_type": self.content_type,
            "http_status": self.http_status,
            "response_headers_subset": [
                {"name": name, "value": value}
                for name, value in self.response_headers_subset
            ],
            "credential_env_var": self.credential_env_var,
            "credential_used": self.credential_used,
            "normalization_status": self.normalization_status,
            "normalization_reason": self.normalization_reason,
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> SourceContractRecord:
        qc_raw = payload["query_contract"]
        parameters = tuple(
            sorted(
                (item["key"], item["value"])
                for item in qc_raw.get("parameters", [])
            )
        )
        contract = QueryContract(
            source_id=qc_raw["source_id"],
            stage=Stage(qc_raw["stage"]),
            reporter=qc_raw["reporter"],
            partner=qc_raw["partner"],
            flow=qc_raw["flow"],
            product_scope=ProductScope(qc_raw["product_scope"]),
            product_codes=tuple(qc_raw["product_codes"]),
            nomenclature=qc_raw["nomenclature"],
            periods=tuple(qc_raw["periods"]),
            parameters=parameters,
        )
        meta_raw = payload.get("page_meta")
        page_meta = None
        if isinstance(meta_raw, dict):
            children = meta_raw.get("enumerated_children")
            page_meta = PageMeta(
                page_index=int(meta_raw["page_index"]),
                pages_expected=meta_raw["pages_expected"],
                next_page_token_present=bool(
                    meta_raw["next_page_token_present"]
                ),
                rows_in_page=meta_raw["rows_in_page"],
                enumerated_children=(
                    tuple(children) if children is not None else None
                ),
            )
        headers_raw = payload.get("response_headers_subset", [])
        headers: tuple[tuple[str, str], ...] = tuple(
            (item["name"], item["value"])
            for item in headers_raw
            if isinstance(item, dict)
        )
        return cls(
            source_id=str(payload["source_id"]),
            authority=str(payload["authority"]),
            access_classification=str(payload["access_classification"]),
            endpoint_or_document=str(payload["endpoint_or_document"]),
            query_contract=contract,
            reporter=str(payload["reporter"]),
            partner=str(payload["partner"]),
            flow=str(payload["flow"]),
            product_code=str(payload["product_code"]),
            product_scope=str(payload["product_scope"]),
            nomenclature=str(payload["nomenclature"]),
            period=str(payload["period"]),
            retrieved_at=str(payload["retrieved_at"]),
            source_refresh_date=str(payload["source_refresh_date"]),
            raw_file_path=str(payload["raw_file_path"]),
            sha256=str(payload["sha256"]),
            license_or_usage_note=str(payload["license_or_usage_note"]),
            query_hash=str(payload["query_hash"]),
            run_id=str(payload["run_id"]),
            page_index=int(payload["page_index"]),
            page_meta=page_meta,
            compressed_sha256=str(payload["compressed_sha256"]),
            byte_count=int(payload["byte_count"]),
            content_type=str(payload["content_type"]),
            http_status=int(payload["http_status"]),
            response_headers_subset=headers,
            credential_env_var=payload.get("credential_env_var"),
            credential_used=bool(payload["credential_used"]),
            normalization_status=str(payload["normalization_status"]),
            normalization_reason=payload.get("normalization_reason"),
        )


@dataclass(frozen=True)
class RawArtifact:
    contract: SourceContractRecord
    path: Path


@dataclass(frozen=True)
class UnavailableRecord:
    source_id: str
    query_contract: QueryContract
    query_hash: str
    run_id: str
    attempted_at: str
    reason: UnavailableReason
    observed_response: ObservedResponse | None
    endpoint_or_document: str
    credential_env_var: str | None
    credential_present: bool
    coverage: CoverageRecord | None

    def to_json(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "query_contract": json.loads(self.query_contract.canonical_json()),
            "query_hash": self.query_hash,
            "run_id": self.run_id,
            "attempted_at": self.attempted_at,
            "reason": self.reason.value,
            "observed_response": (
                self.observed_response.to_json()
                if self.observed_response
                else None
            ),
            "endpoint_or_document": self.endpoint_or_document,
            "credential_env_var": self.credential_env_var,
            "credential_present": self.credential_present,
            "coverage": (
                self.coverage.to_json() if self.coverage else None
            ),
        }


@dataclass(frozen=True)
class QualityCheck:
    check_id: str
    result: str
    detail: str


@dataclass(frozen=True)
class QualityReport:
    source_id: str
    query_hash: str
    run_id: str
    status: str
    checks: tuple[QualityCheck, ...]


@dataclass(frozen=True)
class TradeObservation:
    year: int
    reporter: str
    partner: str
    flow: str
    hs_revision: str
    hs6: str
    national_tariff_line: str | None
    trade_value_original_text: str
    trade_value: float | None
    currency: str
    valuation: str
    net_weight_original_text: str
    net_weight: float | None
    weight_unit: str
    supplementary_quantity: float | None
    supplementary_unit: str | None
    estimation_flags: tuple[str, ...]
    unit_value_analysis_enabled: bool
    gross_flow: bool
    reexport_status: str
    source_evidence_id: str


@dataclass(frozen=True)
class TariffLine:
    national_code: str
    hs6: str
    hs6_mapping_basis: str
    description_ar: str
    description_en: str
    duty_fields: tuple[tuple[str, str], ...]
    reported_nomenclature: str
    source_evidence_id: str
