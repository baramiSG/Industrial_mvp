"""Connector registry and shared acquisition mechanics."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Mapping, Protocol, Sequence, Type

from ior_mvp.config import PROJECT_ROOT
from ..contracts import (
    AcquisitionError,
    AcquisitionUnavailable,
    CoverageRecord,
    ObservedResponse,
    PageMeta,
    ProductScope,
    QueryContract,
    QualityCheck,
    QualityReport,
    RawArtifact,
    SourceContractRecord,
    Stage,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
    UnavailableRecord,
    UnavailableReason,
    new_run_id,
    sha256_bytes,
    utc_now_iso,
)
from ..coverage import evaluate_coverage, not_attempted_coverage
from ..raw_store import RawStore
from ..transport import FetchResult, NetworkError, SizeBudgetExceeded, Transport


class SourceConnector(Protocol):
    source_id: str
    snapshot_kinds: frozenset[str]

    def acquire(
        self,
        query_contract: QueryContract,
        *,
        max_requests: int,
    ) -> tuple[list[RawArtifact], CoverageRecord] | UnavailableRecord:
        ...

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        ...

    def validate(self, raw: RawArtifact) -> QualityReport:
        ...

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        ...

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        ...


class BudgetExhausted(Exception):
    """Request budget exhausted."""


class CredentialEchoed(AcquisitionError):
    """Response body contains a credential value; body must not be stored."""

    def __init__(self, result: FetchResult) -> None:
        super().__init__("credential value echoed in response body")
        self.result = result


@dataclass
class RequestBudget:
    max_requests: int
    used: int = 0

    def take(self) -> None:
        if self.used >= self.max_requests:
            raise BudgetExhausted()
        self.used += 1


class ConnectorRegistry:
    """Registry mapping source_id to connector class."""

    def __init__(
        self,
        mapping: Mapping[str, Type[SourceConnector]],
    ) -> None:
        self._mapping = dict(mapping)

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._mapping))

    def get(self, source_id: str, **deps: Any) -> SourceConnector:
        if source_id not in self._mapping:
            raise KeyError(f"Unknown source_id: {source_id}")
        return self._mapping[source_id](**deps)

    def snapshot_kinds(self, source_id: str) -> frozenset[str]:
        connector_cls = self._mapping[source_id]
        return connector_cls.snapshot_kinds


class BaseConnector:
    """Shared acquire mechanics for production connectors."""

    source_id: str = ""
    snapshot_kinds: frozenset[str] = frozenset()

    def __init__(
        self,
        source_config: dict[str, Any],
        store: RawStore,
        transport: Transport,
        run_id: str,
        environ: Mapping[str, str],
        sleeper: Callable[[float], None] | None = None,
        request_budget: RequestBudget | None = None,
        config_version: str = "1.0.0",
    ) -> None:
        self.source_config = source_config
        self.store = store
        self.transport = transport
        self.run_id = run_id
        self.environ = environ
        self.sleeper = sleeper or time.sleep
        self.request_budget = request_budget or RequestBudget(max_requests=1)
        self.config_version = config_version
        self._license_note = UNAVAILABLE
        self._terms_done = False

    def _resolve_template(
        self,
        contract: QueryContract,
    ) -> str | UnavailableRecord:
        templates = self.source_config.get("endpoint_templates", {})
        template = templates.get(contract.stage.value, UNAVAILABLE)
        if template == UNAVAILABLE:
            return self._unavailable(
                contract,
                UnavailableReason.ENDPOINT_UNVERIFIED,
                endpoint=UNAVAILABLE,
            )
        params = self.source_config.get("parameters", {})
        product_token = params.get("product_all_token", UNAVAILABLE)
        if (
            contract.product_scope == ProductScope.ALL_HS6
            and product_token == UNAVAILABLE
        ):
            return self._unavailable(
                contract,
                UnavailableReason.ENDPOINT_UNVERIFIED,
                endpoint=template,
            )
        return template

    def _build_url(
        self,
        contract: QueryContract,
        template: str,
        *,
        page_index: int = 1,
        page_token: str | None = None,
    ) -> str:
        params = self.source_config.get("parameters", {})
        flow_tokens = params.get("flow_tokens", {})
        flow_code = flow_tokens.get(contract.flow, contract.flow)
        product = (
            contract.product_codes[0]
            if contract.product_scope == ProductScope.EXPLICIT
            else params.get("product_all_token", "ALL")
        )
        partner = (
            contract.partner
            if contract.stage == Stage.PARTNERS
            else params.get("partner_world_token", "WLD")
        )
        period = contract.periods[0] if contract.periods else ""
        url = template.format(
            reporter=params.get("reporter_token", contract.reporter),
            partner=partner,
            product=product,
            flow=contract.flow,
            flow_code=flow_code,
            flow_label=flow_code,
            period=period,
            year=period,
            page=page_index,
            page_token=page_token or "",
        )
        return url

    def _credential_info(self) -> tuple[str | None, bool]:
        env_var = self.source_config.get("credential_env_var")
        if not env_var:
            return None, False
        value = self.environ.get(env_var)
        return env_var, bool(value)

    def _unavailable(
        self,
        contract: QueryContract,
        reason: UnavailableReason,
        *,
        endpoint: str,
        observed: ObservedResponse | None = None,
        coverage: CoverageRecord | None = None,
    ) -> UnavailableRecord:
        env_var, present = self._credential_info()
        if coverage is None:
            coverage = not_attempted_coverage(
                contract,
                run_id=self.run_id,
                stop_reason=reason,
            )
            self.store.write_coverage(coverage)
        record = UnavailableRecord(
            source_id=contract.source_id,
            query_contract=contract,
            query_hash=contract.query_hash(),
            run_id=self.run_id,
            attempted_at=utc_now_iso(),
            reason=reason,
            observed_response=observed,
            endpoint_or_document=endpoint,
            credential_env_var=env_var,
            credential_present=present,
            coverage=coverage,
        )
        self.store.write_unavailable(record)
        return record

    def _capture_terms(self, contract: QueryContract) -> bool:
        if self._terms_done:
            return self._license_note != UNAVAILABLE or not self.source_config.get(
                "license_capture_required", False
            )
        self._terms_done = True
        terms_ref = self.source_config.get("terms_reference", UNAVAILABLE)
        if terms_ref == UNAVAILABLE:
            return False
        if not self.source_config.get("license_capture_required", False):
            return True
        terms_contract = QueryContract(
            source_id=contract.source_id,
            stage=Stage.TERMS,
            reporter=contract.reporter,
            partner=contract.partner,
            flow=contract.flow,
            product_scope=ProductScope.NOT_APPLICABLE,
            product_codes=(),
            nomenclature=contract.nomenclature,
            periods=contract.periods,
        )
        templates = self.source_config.get("endpoint_templates", {})
        terms_url = templates.get("TERMS", terms_ref)
        if terms_url == UNAVAILABLE:
            return False
        try:
            self.request_budget.take()
            result = self._fetch(terms_url)
            if result.http_status != 200:
                return False
            self._license_note = f"Terms captured from {terms_url}"
            self._store_page(terms_contract, result, page_index=1)
            return True
        except (NetworkError, BudgetExhausted, SizeBudgetExceeded, CredentialEchoed):
            return False

    def _fetch(self, url: str) -> FetchResult:
        env_var, _ = self._credential_info()
        secrets: list[tuple[str, str]] = []
        headers: dict[str, str] = {}
        if env_var:
            value = self.environ.get(env_var)
            if value:
                secrets.append((env_var, value))
                headers["Authorization"] = f"Bearer {value}"
        min_interval = self.source_config["rate_limit"]["min_interval_seconds"]
        self.sleeper(min_interval)
        result = self.transport.fetch(
            url,
            explicit_live=True,
            headers=headers,
            secrets=secrets,
            max_body_bytes=self.store.max_artifact_bytes,
        )
        for _, value in secrets:
            if value and value.encode("utf-8") in result.body:
                raise CredentialEchoed(result)
        return result

    def _store_page(
        self,
        contract: QueryContract,
        result: FetchResult,
        *,
        page_index: int,
        normalization_status: str = "PENDING",
        normalization_reason: str | None = None,
    ) -> RawArtifact:
        meta = self.page_meta(result.body, self._content_type(result))
        env_var, credential_used = self._credential_info()
        record = SourceContractRecord(
            source_id=contract.source_id,
            authority=str(self.source_config.get("authority", UNAVAILABLE)),
            access_classification=str(
                self.source_config.get("access_classification", UNAVAILABLE)
            ),
            endpoint_or_document=result.final_url_redacted,
            query_contract=contract,
            reporter=contract.reporter,
            partner=contract.partner,
            flow=contract.flow,
            product_code=(
                contract.product_codes[0]
                if contract.product_codes
                else UNAVAILABLE
            ),
            product_scope=contract.product_scope.value,
            nomenclature=contract.nomenclature,
            period=contract.periods[0] if contract.periods else UNAVAILABLE,
            retrieved_at=result.fetched_at,
            source_refresh_date=result.fetched_at[:10],
            raw_file_path="",
            sha256=sha256_bytes(result.body),
            license_or_usage_note=self._license_note,
            query_hash=contract.query_hash(),
            run_id=self.run_id,
            page_index=page_index,
            page_meta=meta,
            compressed_sha256="",
            byte_count=len(result.body),
            content_type=self._content_type(result),
            http_status=result.http_status,
            response_headers_subset=result.headers_subset,
            credential_env_var=env_var,
            credential_used=credential_used,
            normalization_status=normalization_status,
            normalization_reason=normalization_reason,
        )
        artifact = self.store.write_page(result.body, record)
        return artifact

    def _content_type(self, result: FetchResult) -> str:
        for name, value in result.headers_subset:
            if name == "content-type":
                return value.split(";")[0].strip()
        return "application/octet-stream"

    def acquire(
        self,
        query_contract: QueryContract,
        *,
        max_requests: int,
    ) -> tuple[list[RawArtifact], CoverageRecord] | UnavailableRecord:
        if self.request_budget is None or self.request_budget.max_requests != max_requests:
            self.request_budget = RequestBudget(max_requests=max_requests)
        env_var, present = self._credential_info()
        if env_var and not present:
            return self._unavailable(
                query_contract,
                UnavailableReason.CREDENTIAL_ABSENT,
                endpoint=UNAVAILABLE,
            )

        template_result = self._resolve_template(query_contract)
        if isinstance(template_result, UnavailableRecord):
            return template_result
        template = template_result

        license_required = self.source_config.get(
            "license_capture_required", False
        )
        terms_ref = self.source_config.get("terms_reference", UNAVAILABLE)
        if license_required and terms_ref != UNAVAILABLE:
            if not self._capture_terms(query_contract):
                return self._unavailable(
                    query_contract,
                    UnavailableReason.LICENSE_UNRECORDED,
                    endpoint=template,
                )
        elif terms_ref == UNAVAILABLE and license_required:
            return self._unavailable(
                query_contract,
                UnavailableReason.LICENSE_UNRECORDED,
                endpoint=template,
            )
        else:
            self._license_note = UNAVAILABLE

        pagination = self.source_config.get("pagination", {})
        kind = pagination.get("kind", UNAVAILABLE)
        artifacts: list[RawArtifact] = []
        stop_reason: UnavailableReason | None = None
        observed_stop: ObservedResponse | None = None
        last_result: FetchResult | None = None
        page_index = 1
        page_token: str | None = None

        while True:
            try:
                self.request_budget.take()
            except BudgetExhausted:
                stop_reason = UnavailableReason.MAX_REQUESTS_EXHAUSTED
                if last_result is not None:
                    observed_stop = ObservedResponse(
                        http_status=last_result.http_status,
                        headers_subset=last_result.headers_subset,
                        body_sha256=sha256_bytes(last_result.body),
                        body_byte_count=len(last_result.body),
                        error_type=None,
                        error_message_redacted=None,
                    )
                break

            url = self._build_url(
                query_contract,
                template,
                page_index=page_index,
                page_token=page_token,
            )
            try:
                result = self._fetch(url)
            except SizeBudgetExceeded as exc:
                stop_reason = UnavailableReason.SIZE_BUDGET_EXCEEDED
                observed_stop = ObservedResponse(
                    http_status=None,
                    headers_subset=(),
                    body_sha256=None,
                    body_byte_count=None,
                    error_type=type(exc).__name__,
                    error_message_redacted=str(exc),
                )
                break
            except NetworkError as exc:
                stop_reason = UnavailableReason.NETWORK_ERROR
                observed_stop = ObservedResponse(
                    http_status=None,
                    headers_subset=(),
                    body_sha256=None,
                    body_byte_count=None,
                    error_type=type(exc).__name__,
                    error_message_redacted=str(exc),
                )
                break
            except CredentialEchoed as exc:
                stop_reason = UnavailableReason.OUT_OF_SCOPE_CONTENT
                observed_stop = ObservedResponse(
                    http_status=exc.result.http_status,
                    headers_subset=exc.result.headers_subset,
                    body_sha256=sha256_bytes(exc.result.body),
                    body_byte_count=len(exc.result.body),
                    error_type="CredentialEchoed",
                    error_message_redacted=(
                        "credential value echoed in response body; body not stored"
                    ),
                )
                break

            if result.http_status == 429:
                stop_reason = UnavailableReason.RATE_LIMITED
                observed_stop = ObservedResponse(
                    http_status=429,
                    headers_subset=result.headers_subset,
                    body_sha256=sha256_bytes(result.body),
                    body_byte_count=len(result.body),
                    error_type="HTTPError",
                    error_message_redacted="Rate limited",
                )
                break
            if result.http_status >= 400:
                stop_reason = UnavailableReason.HTTP_ERROR
                observed_stop = ObservedResponse(
                    http_status=result.http_status,
                    headers_subset=result.headers_subset,
                    body_sha256=sha256_bytes(result.body),
                    body_byte_count=len(result.body),
                    error_type="HTTPError",
                    error_message_redacted=f"HTTP {result.http_status}",
                )
                break

            last_result = result
            artifact = self._store_page(query_contract, result, page_index=page_index)
            artifacts.append(artifact)
            meta = artifact.contract.page_meta
            if kind == "NONE":
                break
            if kind == "PAGE_NUMBER":
                if meta and isinstance(meta.pages_expected, int):
                    if page_index >= meta.pages_expected:
                        break
                page_index += 1
                continue
            if kind == "NEXT_TOKEN":
                if meta and not meta.next_page_token_present:
                    break
                page_token = self._extract_next_token(result.body)
                if not page_token:
                    break
                page_index += 1
                continue
            if kind == "INDEX_ENUMERATION":
                if meta and meta.enumerated_children:
                    if page_index >= len(meta.enumerated_children):
                        break
                page_index += 1
                continue
            break

        coverage = evaluate_coverage(
            [a.contract for a in artifacts],
            pagination_kind=kind,
            requests_made=self.request_budget.used,
            stop_reason=stop_reason,
            observed_stop=observed_stop,
            contract=query_contract,
            run_id=self.run_id,
        )
        self.store.write_coverage(coverage)
        if coverage.status != "COMPLETE":
            return self._unavailable(
                query_contract,
                stop_reason or UnavailableReason.COVERAGE_INCOMPLETE,
                endpoint=template,
                observed=observed_stop,
                coverage=coverage,
            )
        return artifacts, coverage

    def _extract_next_token(self, payload: bytes) -> str | None:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        token_field = (
            self.source_config.get("pagination", {})
            .get("parameters", {})
            .get("next_token_field", "next")
        )
        token = data.get(token_field)
        return str(token) if token else None

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        return PageMeta(
            page_index=1,
            pages_expected=1,
            next_page_token_present=False,
            rows_in_page=UNAVAILABLE,
            enumerated_children=None,
        )

    def validate(self, raw: RawArtifact) -> QualityReport:
        return QualityReport(
            source_id=raw.contract.source_id,
            query_hash=raw.contract.query_hash,
            run_id=raw.contract.run_id,
            status="PASS",
            checks=(QualityCheck("rows_present", "PASS", "default"),),
        )

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        return []

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        raise NotImplementedError


def default_registry() -> ConnectorRegistry:
    from .wits_trade import WitsTradeConnector
    from .un_comtrade import UnComtradeConnector
    from .baci_cepii import BaciCepiiConnector
    from .zatca_tariff import ZatcaTariffConnector

    return ConnectorRegistry(
        {
            "wits_trade": WitsTradeConnector,
            "un_comtrade": UnComtradeConnector,
            "baci_cepii": BaciCepiiConnector,
            "zatca_tariff": ZatcaTariffConnector,
        }
    )
