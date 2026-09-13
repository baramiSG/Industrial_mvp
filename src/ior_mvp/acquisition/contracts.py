"""Acquisition domain contracts — query hashes, coverage records, source contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from types import MappingProxyType

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
    COUNT_MISMATCH = "COUNT_MISMATCH"
    RECORD_CAP_REACHED = "RECORD_CAP_REACHED"
    COVERAGE_INDETERMINATE = "COVERAGE_INDETERMINATE"
    COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE"
    PARTNER_DESCRIPTIONS_UNAVAILABLE = "PARTNER_DESCRIPTIONS_UNAVAILABLE"
    NO_UNITS_IN_STORE = "NO_UNITS_IN_STORE"
    REPORTER_MISMATCH = "REPORTER_MISMATCH"
    OUT_OF_SCOPE_CONTENT = "OUT_OF_SCOPE_CONTENT"
    OPERATOR_DISABLED = "OPERATOR_DISABLED"


class CompletenessBasis(StrEnum):
    SINGLE_RESPONSE_NO_PAGINATION = "SINGLE_RESPONSE_NO_PAGINATION"
    PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000 = (
        "PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000"
    )
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
    AGGREGATE = "AGGREGATE"
    DIRECTORY = "DIRECTORY"
    REGISTRY = "REGISTRY"
    DOCUMENT = "DOCUMENT"


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
        stage_spec(self.stage).invariants(self)

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


@dataclass(frozen=True)
class StageSpec:
    """Governed behavior of one acquisition stage family."""

    stage: Stage
    unit_key: Callable[[QueryContract], tuple[str, ...]]
    unit_dict: Callable[[QueryContract], dict[str, Any]]
    invariants: Callable[[QueryContract], None]
    plan_units: Callable[..., tuple[QueryContract, ...]]
    period_scoped: bool
    url_tokens: Callable[[QueryContract, Mapping[str, Any]], dict[str, Any]]


def _scope_invariants(contract: QueryContract, scope: ProductScope, codes: tuple[str, ...]) -> None:
    if contract.product_scope != scope:
        raise AcquisitionConfigurationError(f"{contract.stage.value} requires product_scope {scope.value}")
    if contract.product_codes != codes:
        raise AcquisitionConfigurationError(f"{contract.stage.value} requires product_codes {codes!r}")


def _period_invariant(contract: QueryContract) -> None:
    if len(contract.periods) != 1:
        raise AcquisitionConfigurationError(f"{contract.stage.value} requires exactly one period per contract")


def _universe_invariants(contract: QueryContract) -> None:
    _scope_invariants(contract, ProductScope.ALL_HS6, (PRODUCT_SCOPE_ALL,))
    _period_invariant(contract)


def _partners_invariants(contract: QueryContract) -> None:
    if contract.product_scope != ProductScope.EXPLICIT:
        raise AcquisitionConfigurationError("PARTNERS requires product_scope EXPLICIT")
    if PRODUCT_SCOPE_ALL in contract.product_codes:
        raise AcquisitionConfigurationError("PARTNERS rejects product_codes containing 'ALL'")
    for code in contract.product_codes:
        if len(code) != 6 or not code.isdigit():
            raise AcquisitionConfigurationError(f"PARTNERS requires 6-digit HS6 codes: {code!r}")
    _period_invariant(contract)


def _s11_unit_dict(contract: QueryContract) -> dict[str, Any]:
    return {
        "stage": contract.stage.value,
        "flow": contract.flow,
        "period": contract.periods[0] if contract.periods else None,
        "product_scope": contract.product_scope.value,
        "hs6": contract.product_codes[0] if contract.product_scope == ProductScope.EXPLICIT else None,
    }


def _planned_contract(source_id: str, config: dict[str, Any], *, stage: Stage,
                      scope: ProductScope, codes: tuple[str, ...], flow: str,
                      periods: tuple[str, ...],
                      parameters: tuple[tuple[str, str], ...] = ()) -> QueryContract:
    cfg = config["sources"][source_id]
    return QueryContract(
        source_id, stage, cfg["reporter_code"],
        cfg["parameters"].get("partner_world_token", "WLD"), flow,
        scope, codes, cfg["nomenclature"], periods, parameters,
    )


def _plan_universe(*, source_id: str, years: Sequence[int], flows: Sequence[str],
                   candidates: Any, config: dict[str, Any]) -> tuple[QueryContract, ...]:
    return tuple(_planned_contract(source_id, config, stage=Stage.UNIVERSE,
                 scope=ProductScope.ALL_HS6, codes=(PRODUCT_SCOPE_ALL,),
                 flow=flow, periods=(str(year),)) for year in years for flow in flows)


def _plan_partners(*, source_id: str, years: Sequence[int], flows: Sequence[str],
                   candidates: Any, config: dict[str, Any],
                   parameters: tuple[tuple[str, str], ...] = ()) -> tuple[QueryContract, ...]:
    if candidates is None:
        raise AcquisitionConfigurationError("PARTNERS requires candidates")
    return tuple(_planned_contract(source_id, config, stage=Stage.PARTNERS,
                 scope=ProductScope.EXPLICIT, codes=(code,), flow=flow,
                 periods=(str(year),), parameters=parameters)
                 for year in years for flow in flows for code in candidates.hs6_codes)


def _plan_tariff(*, source_id: str, config: dict[str, Any], **_: Any) -> tuple[QueryContract, ...]:
    return (_planned_contract(source_id, config, stage=Stage.TARIFF,
            scope=ProductScope.ALL_TARIFF_LINES, codes=(PRODUCT_SCOPE_ALL,),
            flow=UNAVAILABLE, periods=()),)


def _plan_bulk(*, source_id: str, years: Sequence[int], config: dict[str, Any], **_: Any) -> tuple[QueryContract, ...]:
    return tuple(_planned_contract(source_id, config, stage=Stage.BULK,
                 scope=ProductScope.NOT_APPLICABLE, codes=(), flow=UNAVAILABLE,
                 periods=(str(year),)) for year in years)


def _world_partner_token(contract: QueryContract, parameters: Mapping[str, Any]) -> dict[str, Any]:
    return {"partner": parameters.get("partner_world_token", "WLD")}


def _explicit_partner_token(contract: QueryContract, parameters: Mapping[str, Any]) -> dict[str, Any]:
    return {"partner": contract.partner}


RESERVED_UNIT_PARAMETERS = frozenset({
    "reporter", "partner", "product", "flow", "flow_code", "flow_label",
    "period", "year", "page", "page_token", "units", "reporter_token",
    "partner_world_token", "product_all_token", "flow_tokens",
})


def _institutional_invariants(contract: QueryContract, *, period_scoped: bool) -> None:
    _scope_invariants(contract, ProductScope.NOT_APPLICABLE, ())
    if contract.reporter != "SAU" or contract.partner != UNAVAILABLE or contract.flow != UNAVAILABLE:
        raise AcquisitionConfigurationError("Institutional units require SAU and unavailable partner/flow")
    if period_scoped:
        _period_invariant(contract)
    elif contract.periods:
        raise AcquisitionConfigurationError("Institutional directory/registry units reject periods")
    keys = [key for key, _ in contract.parameters]
    if (not keys or len(keys) != len(set(keys)) or set(keys) & RESERVED_UNIT_PARAMETERS
            or any(not isinstance(key, str) or not key or not isinstance(value, str)
                   for key, value in contract.parameters)):
        raise AcquisitionConfigurationError("Institutional parameters require unique non-reserved named strings")


def _institutional_unit_key(contract: QueryContract) -> tuple[str, ...]:
    # JSON pair framing preserves names, delimiters and Unicode without ambiguity.
    return (json.dumps(sorted(contract.parameters), ensure_ascii=False, separators=(",", ":")), *contract.periods)


def _institutional_unit_dict(contract: QueryContract) -> dict[str, Any]:
    return {"stage": contract.stage.value, "period": contract.periods[0] if contract.periods else None,
            "parameters": dict(sorted(contract.parameters))}


def _plan_institutional(*, stage: Stage, source_id: str, years: Sequence[int],
                        config: dict[str, Any], **_: Any) -> tuple[QueryContract, ...]:
    if stage_spec(stage).period_scoped and not years:
        raise AcquisitionConfigurationError(f"{stage.value} planning requires at least one period")
    cfg = config["sources"][source_id]
    parameters = cfg.get("parameters", UNAVAILABLE)
    units = parameters.get("units", UNAVAILABLE) if isinstance(parameters, Mapping) else UNAVAILABLE
    if units == UNAVAILABLE:
        units = [{"unit": UNAVAILABLE}]
    if not isinstance(units, list) or not units or any(not isinstance(unit, Mapping) for unit in units):
        raise AcquisitionConfigurationError("Institutional units must be nonempty mappings or UNAVAILABLE")
    periods = [(str(year),) for year in years] if stage_spec(stage).period_scoped else [()]
    return tuple(QueryContract(source_id, stage, cfg["reporter_code"], UNAVAILABLE, UNAVAILABLE,
                 ProductScope.NOT_APPLICABLE, (), cfg["nomenclature"], period, tuple(sorted(unit.items())))
                 for period in periods for unit in units)


def _institutional_url_tokens(contract: QueryContract, parameters: Mapping[str, Any]) -> dict[str, Any]:
    units = parameters.get("units", UNAVAILABLE)
    identity = dict(contract.parameters)
    if (any(not value or value == UNAVAILABLE for value in identity.values())
            or not isinstance(units, list) or identity not in units):
        raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED)
    return {"partner": contract.partner}


def _document_invariants(contract: QueryContract) -> None:
    _institutional_invariants(contract, period_scoped=False)
    keys = {key for key, _ in contract.parameters}
    if keys != {"document_url"}:
        raise AcquisitionConfigurationError("DOCUMENT units require exactly document_url parameter")


def _plan_documents(
    *,
    source_id: str,
    config: dict[str, Any],
    candidates: Any | None = None,
    **_: Any,
) -> tuple[QueryContract, ...]:
    cfg = config["sources"][source_id]
    if candidates is None or not getattr(candidates, "entries", None):
        return (
            QueryContract(
                source_id,
                Stage.DOCUMENT,
                cfg["reporter_code"],
                UNAVAILABLE,
                UNAVAILABLE,
                ProductScope.NOT_APPLICABLE,
                (),
                cfg["nomenclature"],
                (),
                (("document_url", UNAVAILABLE),),
            ),
        )
    contracts: list[QueryContract] = []
    for entry in candidates.entries:
        contracts.append(
            QueryContract(
                source_id,
                Stage.DOCUMENT,
                cfg["reporter_code"],
                UNAVAILABLE,
                UNAVAILABLE,
                ProductScope.NOT_APPLICABLE,
                (),
                cfg["nomenclature"],
                (),
                (("document_url", entry.document_url),),
            )
        )
    return tuple(contracts)


def _document_url_tokens(contract: QueryContract, parameters: Mapping[str, Any]) -> dict[str, Any]:
    url = dict(contract.parameters).get("document_url", UNAVAILABLE)
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED)
    return {"document_url": url}


STAGE_SPECS: Mapping[Stage, StageSpec] = MappingProxyType({
    Stage.UNIVERSE: StageSpec(Stage.UNIVERSE, lambda c: (c.flow, c.periods[0]), _s11_unit_dict, _universe_invariants, _plan_universe, True, _world_partner_token),
    Stage.PARTNERS: StageSpec(Stage.PARTNERS, lambda c: (c.product_codes[0], c.flow, c.periods[0]), _s11_unit_dict, _partners_invariants, _plan_partners, True, _explicit_partner_token),
    Stage.TARIFF: StageSpec(Stage.TARIFF, lambda c: ("ALL_TARIFF_LINES",), _s11_unit_dict, lambda c: _scope_invariants(c, ProductScope.ALL_TARIFF_LINES, (PRODUCT_SCOPE_ALL,)), _plan_tariff, False, _world_partner_token),
    Stage.TERMS: StageSpec(Stage.TERMS, lambda c: ("TERMS",), _s11_unit_dict, lambda c: _scope_invariants(c, ProductScope.NOT_APPLICABLE, ()), lambda **_: (), False, _world_partner_token),
    Stage.BULK: StageSpec(Stage.BULK, lambda c: (c.periods[0],), _s11_unit_dict, _period_invariant, _plan_bulk, True, _world_partner_token),
    Stage.AGGREGATE: StageSpec(Stage.AGGREGATE, _institutional_unit_key, _institutional_unit_dict,
        lambda c: _institutional_invariants(c, period_scoped=True),
        lambda **kwargs: _plan_institutional(stage=Stage.AGGREGATE, **kwargs), True, _institutional_url_tokens),
    Stage.DIRECTORY: StageSpec(Stage.DIRECTORY, _institutional_unit_key, _institutional_unit_dict,
        lambda c: _institutional_invariants(c, period_scoped=False),
        lambda **kwargs: _plan_institutional(stage=Stage.DIRECTORY, **kwargs), False, _institutional_url_tokens),
    Stage.REGISTRY: StageSpec(Stage.REGISTRY, _institutional_unit_key, _institutional_unit_dict,
        lambda c: _institutional_invariants(c, period_scoped=False),
        lambda **kwargs: _plan_institutional(stage=Stage.REGISTRY, **kwargs), False, _institutional_url_tokens),
    Stage.DOCUMENT: StageSpec(
        Stage.DOCUMENT,
        _institutional_unit_key,
        _institutional_unit_dict,
        _document_invariants,
        _plan_documents,
        False,
        _document_url_tokens,
    ),
})


def stage_spec(stage: Stage) -> StageSpec:
    try:
        return STAGE_SPECS[Stage(stage)]
    except (ValueError, KeyError, TypeError) as exc:
        raise AcquisitionConfigurationError(f"Unknown stage: {stage}") from exc


def unit_key(contract: QueryContract) -> tuple[str, ...]:
    """Return the acquisition unit key per the governed stage specification."""
    return stage_spec(contract.stage).unit_key(contract)


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


@dataclass(frozen=True)
class ProductionObservation:
    period_text: str
    period_type_text: str
    geography_text: str
    activity_code_text: str
    activity_classification_text: str
    product_code_text: str
    product_classification_text: str
    indicator_text: str
    value_original_text: str
    value: float|None
    unit_text: str
    currency_text: str
    estimation_flags: tuple[str,...]
    source_dataset_id: str
    source_evidence_id: str

@dataclass(frozen=True)
class DirectoryRow:
    entity_name_ar: str
    entity_name_en: str
    record_type_text: str
    licence_number_text: str
    activity_description_ar: str
    activity_description_en: str
    activity_code_text: str
    region_text: str
    city_text: str
    industrial_city_text: str
    status_text: str
    capacity_text: str
    record_date_text: str
    source_record_id: str
    source_evidence_id: str

@dataclass(frozen=True)
class RegistryRow:
    registry: str
    standard_reference_text: str
    title_ar: str
    title_en: str
    edition_or_year_text: str
    scope_text: str
    status_text: str
    product_or_certificate_reference_text: str
    conformity_type_text: str
    issued_to_text: str
    validity_text: str
    source_record_id: str
    source_evidence_id: str


Row = TradeObservation | TariffLine | ProductionObservation | DirectoryRow | RegistryRow
