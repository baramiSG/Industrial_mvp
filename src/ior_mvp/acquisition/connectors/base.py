"""Connector registry and shared acquisition mechanics."""

from __future__ import annotations

import json
import csv
import io
import re
import time
import unicodedata
from html.parser import HTMLParser
from string import Formatter
from types import MappingProxyType
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Mapping, Protocol, Type

from ..contracts import (
    AcquisitionError,
    AcquisitionUnavailable,
    CompletenessBasis,
    CoverageRecord,
    ObservedResponse,
    PageMeta,
    ProductScope,
    QueryContract,
    QualityCheck,
    QualityReport,
    RawArtifact,
    Row,
    SourceContractRecord,
    Stage,
    UNAVAILABLE,
    UnavailableRecord,
    UnavailableReason,
    sha256_bytes,
    utc_now_iso,
    stage_spec,
    unit_key,
)
from ..coverage import evaluate_coverage, not_attempted_coverage
from ..raw_store import RawStore
from ..source_config import (
    configured_credential_env_var,
    configured_credential_header,
)
from ..transport import FetchResult, NetworkError, SizeBudgetExceeded, Transport


class SourceConnector(Protocol):
    source_id: str
    snapshot_kinds: frozenset[str]
    parse_rows: Callable[[bytes, str], list[dict[str, Any]]] | None

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
    ) -> list[Row]:
        ...

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        ...


class BudgetExhausted(Exception):
    """Request budget exhausted."""


class _ObservedTokenFormatter(Formatter):
    """Reject unobserved values even through nested format specifications."""

    def get_field(self, field_name: str, args: tuple, kwargs: dict) -> tuple[Any, Any]:
        value, key = super().get_field(field_name, args, kwargs)
        if value == UNAVAILABLE or value is None:
            raise ValueError(f"Unobserved endpoint token: {field_name}")
        return value, key


class CredentialEchoed(AcquisitionError):
    """Response body contains a credential value; body must not be stored."""

    def __init__(self, result: FetchResult) -> None:
        super().__init__("credential value echoed in response body")
        self.result = result


_PERSONAL_ENGLISH = (
    "phone", "phone_number", "phone_no", "telephone", "telephone_number",
    "telephone_no", "mobile", "mobile_number", "mobile_no", "email",
    "email_address", "e_mail", "e_mail_address", "contact_person",
    "contact_person_name", "contact_name", "person_name", "national_id",
    "national_id_number", "national_id_no",
)
_PERSONAL_ARABIC = frozenset({
    "هاتف", "الهاتف", "رقم_الهاتف", "جوال", "الجوال", "رقم_الجوال",
    "البريد_الإلكتروني", "البريد_الالكتروني", "بريد_إلكتروني", "بريد_الكتروني",
    "اسم_شخص_الاتصال", "اسم_مسؤول_التواصل", "الهوية_الوطنية", "رقم_الهوية_الوطنية",
})
_PERSONAL_SUFFIX = re.compile(
    r"(?:^|_)(?:" + "|".join(_PERSONAL_ENGLISH) + r")(?:_ar|_en|_text)?$"
)


def _personal_field(label: str) -> bool:
    label = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", label)
    label = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", label)
    label = unicodedata.normalize("NFC", label).casefold()
    label = re.sub(r"[\s_\-/.]+", "_", label).strip("_")
    return label in _PERSONAL_ARABIC or _PERSONAL_SUFFIX.search(label) is not None


class _HTMLFieldLabels(HTMLParser):
    """Extract only table headers and named form controls, excluding script/style."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.labels: list[str] = []
        self._header: list[str] | None = None
        self._suppressed: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._suppressed:
            return
        if tag in {"script", "style"}:
            self._suppressed = tag
        elif tag == "th":
            self._finish_header()
            self._header = []
        elif tag in {"input", "select", "textarea", "button"}:
            self.labels.extend(value for name, value in attrs if name == "name" and value is not None)

    def handle_endtag(self, tag: str) -> None:
        if self._suppressed:
            if tag == self._suppressed:
                self._suppressed = None
        elif tag == "th":
            self._finish_header()

    def handle_data(self, data: str) -> None:
        if self._header is not None and not self._suppressed:
            self._header.append(data)

    def _finish_header(self) -> None:
        if self._header is not None:
            self.labels.append("".join(self._header))
            self._header = None

    def close(self) -> None:
        super().close()
        self._finish_header()


def _institutional_privacy_error(payload: bytes, declared: str) -> str | None:
    """Approved text-only label screen; never sniff envelopes or inspect values."""
    mime = declared.casefold()
    if mime in {"application/pdf", "application/zip", "application/gzip"} or mime.startswith(("image/", "audio/", "video/", "font/")):
        return "UninspectableTextPayload"
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError:
        return "UninspectableTextPayload"
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", text):
        return "UninspectableTextPayload"
    labels: list[str] = []
    try:
        if mime in {"application/json", "text/json"} or re.fullmatch(r"application/[^/\s]+\+json", mime):
            # object_pairs_hook sees every key, including duplicate-key objects
            # that a normal dict conversion would otherwise discard.
            def collect(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
                labels.extend(key for key, _ in pairs)
                return dict(pairs)
            json.loads(text, object_pairs_hook=collect)
        elif mime in {"text/csv", "text/tab-separated-values"}:
            reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t" if mime == "text/tab-separated-values" else ",", strict=True)
            labels = next((row for row in reader if any(cell.strip() for cell in row)), [])
        elif mime in {"text/html", "application/xhtml+xml"}:
            parser = _HTMLFieldLabels()
            parser.feed(text)
            parser.close()
            labels = parser.labels
        # Every other declaration is opaque text: no inferred fields.
    except (ValueError, csv.Error, RecursionError):
        return None  # Unknown selected-format shape, without another parser.
    return "PersonalDataFields" if any(_personal_field(label) for label in labels) else None


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
    parse_rows: Callable[[bytes, str], list[dict[str, Any]]] | None = None

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

    def coverage_stop_reason(
        self, raw: RawArtifact
    ) -> UnavailableReason | None:
        """Return a source-specific reason that prevents page completeness."""
        return None

    def single_response_completeness_basis(self) -> CompletenessBasis:
        """Return the governed basis for a one-response non-paginated unit."""
        return CompletenessBasis.SINGLE_RESPONSE_NO_PAGINATION

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
        spec = stage_spec(contract.stage)
        if any(not value or value == UNAVAILABLE for value in unit_key(contract)):
            raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED)
        if spec.period_scoped and (len(contract.periods) != 1 or not contract.periods[0] or contract.periods[0] == UNAVAILABLE):
            raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED)
        params = self._observed_mapping(self.source_config.get("parameters"))
        flow_tokens = self._observed_mapping(params.get("flow_tokens"))
        flow_code = flow_tokens.get(contract.flow, contract.flow)
        product = (
            contract.product_codes[0]
            if contract.product_scope == ProductScope.EXPLICIT
            else params.get("product_all_token", "ALL")
        )
        period = contract.periods[0] if contract.periods else ""
        tokens = {
            **params,
            "reporter": params.get("reporter_token", contract.reporter),
            "product": product, "flow": contract.flow,
            "flow_code": flow_code, "flow_label": flow_code,
            "period": period, "year": period,
            **spec.url_tokens(contract, params),
            **self._page_tokens(page_index, page_token),
        }
        parameter_names = [key for key, _ in contract.parameters]
        reserved_overlap = set(parameter_names) & set(tokens)
        if contract.stage is Stage.DOCUMENT:
            reserved_overlap.discard("document_url")
        if len(set(parameter_names)) != len(parameter_names) or reserved_overlap:
            raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED)
        tokens.update(dict(contract.parameters))
        try:
            return _ObservedTokenFormatter().vformat(template, (), tokens)
        except (KeyError, IndexError, ValueError, AttributeError, TypeError) as exc:
            raise AcquisitionUnavailable(UnavailableReason.ENDPOINT_UNVERIFIED) from exc

    @staticmethod
    def _observed_mapping(value: Any) -> Mapping:
        if value is None or value == UNAVAILABLE:
            return MappingProxyType({})
        if not isinstance(value, Mapping):
            raise ValueError("Observed value must be a mapping")
        return value

    def _page_tokens(self, page_index: int, page_token: str | None) -> dict[str, Any]:
        return {"page": page_index, "page_token": page_token or ""}

    def classify_page(self, payload: bytes, content_type: str, stage: Stage) -> tuple[str, str | None]:
        if stage == Stage.TERMS:
            return "UNPARSED", "no_rows_parsed"
        if self.parse_rows is None:
            return "PENDING", None
        try:
            if self.parse_rows(payload, content_type):
                return "NORMALIZED", None
        except (ValueError, TypeError, AttributeError, OverflowError):
            # Preserve malformed responses as raw evidence. The parser's
            # normalization behavior is unchanged; classification emits no rows.
            return "UNPARSED", "no_rows_parsed"
        return "UNPARSED", "no_rows_parsed"

    def _credential_info(self) -> tuple[str | None, bool]:
        env_var = configured_credential_env_var(self.source_config)
        if env_var is None:
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
            status, reason = self.classify_page(result.body, self._content_type(result), Stage.TERMS)
            self._store_page(terms_contract, result, page_index=1,
                             normalization_status=status, normalization_reason=reason)
            return True
        except (NetworkError, BudgetExhausted, SizeBudgetExceeded, CredentialEchoed):
            return False

    def _pre_storage_refusal(
        self, result: FetchResult, stage: Stage
    ) -> tuple[str, str] | None:
        if stage in {Stage.DIRECTORY, Stage.REGISTRY}:
            privacy_error = _institutional_privacy_error(
                result.body, self._content_type(result)
            )
            if privacy_error:
                return (
                    privacy_error,
                    "Response refused by institutional text-only privacy policy; body not stored",
                )
        return None

    def _fetch(self, url: str) -> FetchResult:
        env_var, _ = self._credential_info()
        secrets: list[tuple[str, str]] = []
        headers: dict[str, str] = {}
        if env_var:
            value = self.environ.get(env_var)
            if value:
                secrets.append((env_var, value))
                header_name, scheme = configured_credential_header(
                    self.source_config
                )
                headers[header_name] = (
                    f"{scheme} {value}" if scheme else value
                )
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
        try:
            self._build_url(query_contract, template)
        except AcquisitionUnavailable as exc:
            return self._unavailable(query_contract, exc.reason, endpoint=template)

        if self.source_config.get("access_classification") == UNAVAILABLE:
            return self._unavailable(query_contract, UnavailableReason.LICENSE_UNRECORDED, endpoint=template)

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
                url = self._build_url(query_contract, template, page_index=page_index, page_token=page_token)
            except AcquisitionUnavailable as exc:
                stop_reason = exc.reason
                break
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

            refusal = self._pre_storage_refusal(result, query_contract.stage)
            if refusal:
                error_type, error_message = refusal
                stop_reason = UnavailableReason.OUT_OF_SCOPE_CONTENT
                observed_stop = ObservedResponse(
                    http_status=result.http_status,
                    headers_subset=result.headers_subset,
                    body_sha256=sha256_bytes(result.body),
                    body_byte_count=len(result.body),
                    error_type=error_type,
                    error_message_redacted=error_message,
                )
                break

            last_result = result
            status, reason = self.classify_page(result.body, self._content_type(result), query_contract.stage)
            artifact = self._store_page(query_contract, result, page_index=page_index,
                                        normalization_status=status, normalization_reason=reason)
            artifacts.append(artifact)
            page_stop_reason = self.coverage_stop_reason(artifact)
            if page_stop_reason is not None:
                stop_reason = page_stop_reason
                break
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
                elif not self._observed_mapping(pagination.get("parameters")):
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
            single_response_basis=self.single_response_completeness_basis(),
        )
        self.store.write_coverage(coverage)
        if coverage.status != "COMPLETE":
            observed = observed_stop
            if observed is None and last_result is not None:
                observed = ObservedResponse(
                    http_status=last_result.http_status,
                    headers_subset=last_result.headers_subset,
                    body_sha256=sha256_bytes(last_result.body),
                    body_byte_count=len(last_result.body),
                    error_type=None,
                    error_message_redacted=None,
                )
            return self._unavailable(
                query_contract,
                stop_reason or UnavailableReason.COVERAGE_INCOMPLETE,
                endpoint=template,
                observed=observed,
                coverage=coverage,
            )
        return artifacts, coverage

    def _extract_next_token(self, payload: bytes) -> str | None:
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        token_field = self._observed_mapping(
            self.source_config.get("pagination", {}).get("parameters")
        ).get("next_token_field")
        if not token_field or not isinstance(data, dict):
            return None
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
    ) -> list[Row]:
        return []

    def snapshot(
        self,
        observations: list[Any],
        as_of_date: date,
    ) -> dict[str, Any]:
        raise NotImplementedError


class InstitutionalConnector(BaseConnector):
    """Shared row validation for institutional sources with no observed parser yet."""

    row_kind: str = ""

    def snapshot(self, observations: list[Any], as_of_date: date) -> dict[str, Any]:
        """Build from selected stored evidence, as with the existing S11 helpers."""
        from ..snapshots import build_row_snapshot

        return build_row_snapshot(
            self.store,
            {"sources": {self.source_id: self.source_config}, "metadata": {"version": self.config_version}},
            default_registry(),
            source_id=self.source_id,
            kind=self.row_kind,
        )

    def parse_rows(self, payload: bytes, content_type: str) -> list[dict[str, Any]]:
        # Implement a source parser only after an actual shape is observed.
        return []

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        return PageMeta(
            page_index=1,
            pages_expected=1 if self.source_config.get("pagination", {}).get("kind") == "NONE" else UNAVAILABLE,
            next_page_token_present=False,
            rows_in_page=UNAVAILABLE,
            enumerated_children=None,
        )

    def normalize(self, raw: RawArtifact) -> list[Row]:
        from ..harmonise import directory_row_from_row, production_observation_from_row, registry_row_from_row

        mapper = {"production": production_observation_from_row, "directory": directory_row_from_row, "registry": registry_row_from_row}[self.row_kind]
        return [mapper(row, field_map={}, source_evidence_id=raw.contract.query_hash)
                for row in self.parse_rows(self.store.read_payload(raw.contract), raw.contract.content_type)]

    def validate(self, raw: RawArtifact) -> QualityReport:
        contract = raw.contract
        expected_stage = {"production": Stage.AGGREGATE, "directory": Stage.DIRECTORY, "registry": Stage.REGISTRY}[self.row_kind]
        identity_ok = (
            contract.source_id == self.source_id
            and contract.query_contract.stage == expected_stage
            and contract.reporter == contract.query_contract.reporter == self.source_config.get("reporter_code")
        )
        valid = False
        try:
            rows = self.normalize(raw)
            def observed(value: Any) -> bool:
                return isinstance(value, str) and bool(value.strip()) and value != UNAVAILABLE
            if self.row_kind == "production":
                valid = bool(rows) and all(
                    row.geography_text == contract.reporter
                    and row.period_text in contract.query_contract.periods
                    and observed(row.indicator_text) and observed(row.source_dataset_id)
                    for row in rows
                )
            elif self.row_kind == "directory":
                valid = bool(rows) and all(observed(row.source_record_id) and (observed(row.entity_name_ar) or observed(row.entity_name_en)) for row in rows)
            else:
                valid = bool(rows) and all(observed(row.source_record_id) and row.registry == self.source_id and (observed(row.standard_reference_text) or observed(row.product_or_certificate_reference_text)) for row in rows)
        except (ValueError, TypeError, AttributeError, OverflowError):
            valid = False
        checks = (
            QualityCheck("source_stage_reporter", "PASS" if identity_ok else "FAIL", "Source identity, stage and reporter match the query and configuration"),
            QualityCheck("institutional_row_shape", "PASS" if valid else "FAIL", "Published row types and kind-specific identities are valid"),
        )
        return QualityReport(contract.source_id, contract.query_hash, contract.run_id,
                             "PASS" if identity_ok and valid else "FAIL", checks)


def default_registry() -> ConnectorRegistry:
    from .wits_trade import WitsTradeConnector
    from .un_comtrade import UnComtradeConnector
    from .baci_cepii import BaciCepiiConnector
    from .zatca_tariff import ZatcaTariffConnector
    from .gastat import GastatConnector
    from .ministry_of_industry import MinistryOfIndustryConnector
    from .modon import ModonConnector
    from .saso_catalogue import SasoCatalogueConnector
    from .saber_registry import SaberRegistryConnector
    from .documents import (
        EtimadTendersConnector,
        ProducerAlupcoConnector,
        ProducerAdvancedPetrochemicalConnector,
        ProducerAltaiseerTalcoConnector,
        ProducerHadeedConnector,
        ProducerMaadenConnector,
        ProducerSabicConnector,
        ProducerTasneeConnector,
        ProducerUnicoilConnector,
        SasoDocumentsConnector,
        TadawulDisclosuresConnector,
        WcoHsNomenclatureConnector,
    )

    return ConnectorRegistry(
        {
            "wits_trade": WitsTradeConnector,
            "un_comtrade": UnComtradeConnector,
            "baci_cepii": BaciCepiiConnector,
            "zatca_tariff": ZatcaTariffConnector,
            "gastat": GastatConnector,
            "ministry_of_industry": MinistryOfIndustryConnector,
            "modon": ModonConnector,
            "saso_catalogue": SasoCatalogueConnector,
            "saber_registry": SaberRegistryConnector,
            "tadawul_disclosures": TadawulDisclosuresConnector,
            "etimad_tenders": EtimadTendersConnector,
            "saso_documents": SasoDocumentsConnector,
            "producer_unicoil": ProducerUnicoilConnector,
            "producer_sabic": ProducerSabicConnector,
            "producer_advanced_petrochemical": ProducerAdvancedPetrochemicalConnector,
            "producer_tasnee": ProducerTasneeConnector,
            "producer_hadeed": ProducerHadeedConnector,
            "producer_alupco": ProducerAlupcoConnector,
            "producer_altaiseer_talco": ProducerAltaiseerTalcoConnector,
            "producer_maaden": ProducerMaadenConnector,
            "wco_hs_nomenclature": WcoHsNomenclatureConnector,
        }
    )
