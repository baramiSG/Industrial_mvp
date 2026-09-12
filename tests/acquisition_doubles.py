"""Test doubles for acquisition connector tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ior_mvp.acquisition.connectors.base import BaseConnector, ConnectorRegistry
from ior_mvp.acquisition.contracts import (
    CoverageRecord,
    PageMeta,
    ProductScope,
    QueryContract,
    RawArtifact,
    Stage,
    TariffLine,
    TradeObservation,
    UNAVAILABLE,
    UnavailableRecord,
    UnavailableReason,
    sha256_bytes,
)
from ior_mvp.acquisition.coverage import evaluate_coverage
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.transport import FetchResult, Transport


@dataclass
class FakeTransport(Transport):
    responses: dict[str, FetchResult | Exception]
    calls: list[str]
    request_headers: list[dict[str, str]] = field(default_factory=list)

    def fetch(
        self,
        url: str,
        *,
        explicit_live: bool,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        secrets: tuple[tuple[str, str], ...] = (),
        max_body_bytes: int | None = None,
    ) -> FetchResult:
        self.calls.append(url)
        self.request_headers.append(dict(headers or {}))
        outcome = self.responses.get(url)
        if isinstance(outcome, Exception):
            raise outcome
        if outcome is None:
            raise RuntimeError(f"No fake response for {url}")
        return outcome


def seed_unit(
    store: RawStore,
    *,
    contract: QueryContract,
    run_id: str,
    payload: bytes,
    source_config: dict[str, Any],
    page_index: int = 1,
    page_meta: PageMeta | None = None,
) -> RawArtifact:
    from ior_mvp.acquisition.connectors.base import BaseConnector

    connector = BaseConnector(
        source_config=source_config,
        store=store,
        transport=FakeTransport(responses={}, calls=[]),
        run_id=run_id,
        environ={},
    )
    result = FetchResult(
        http_status=200,
        headers_subset=(("content-type", "application/json"),),
        body=payload,
        final_url_redacted="http://example.test/data",
        fetched_at="2026-09-04T00:00:00Z",
        content_length_header=len(payload),
    )
    if page_meta:
        connector.page_meta = lambda p, c: page_meta  # type: ignore[method-assign]
    else:
        try:
            data = json.loads(payload.decode("utf-8"))
            if isinstance(data, dict) and "pages_expected" in data:
                connector.page_meta = lambda p, c, d=data: PageMeta(  # type: ignore[method-assign]
                    page_index=int(d.get("page_index", 1)),
                    pages_expected=int(d["pages_expected"]),
                    next_page_token_present=bool(d.get("next_page_token_present", False)),
                    rows_in_page=d.get("rows_in_page", 1),
                    enumerated_children=tuple(d.get("enumerated_children", [])) or None,
                )
        except (UnicodeError, json.JSONDecodeError, KeyError, TypeError):
            pass
    artifact = connector._store_page(
        contract, result, page_index=page_index, normalization_status="NORMALIZED"
    )
    pagination = source_config.get("pagination", {}).get("kind", "NONE")
    coverage = evaluate_coverage(
        [artifact.contract],
        pagination_kind=pagination,
        requests_made=1,
        stop_reason=None,
        observed_stop=None,
        contract=contract,
        run_id=run_id,
    )
    store.write_coverage(coverage)
    return artifact


class DoubleConnector(BaseConnector):
    source_id = "TEST-FIXTURE"
    snapshot_kinds = frozenset({"universe", "partners", "tariff"})

    def page_meta(self, payload: bytes, content_type: str) -> PageMeta:
        data = json.loads(payload.decode("utf-8"))
        return PageMeta(
            page_index=data.get("page_index", 1),
            pages_expected=data.get("pages_expected", 1),
            next_page_token_present=data.get("next_page_token_present", False),
            rows_in_page=data.get("rows_in_page", 1),
            enumerated_children=tuple(data.get("enumerated_children", [])) or None,
        )

    def normalize(
        self, raw: RawArtifact
    ) -> list[TradeObservation] | list[TariffLine]:
        payload = self.store.read_payload(raw.contract)
        data = json.loads(payload.decode("utf-8"))
        if "lines" in data:
            return []
        rows = data.get("rows", [])
        from ior_mvp.acquisition.harmonise import trade_observation_from_row

        return [
            trade_observation_from_row(
                row,
                field_map={},
                reporter_expected="SAU",
                hs_revision="H0",
                source_evidence_id=raw.contract.query_hash,
                valuation_by_flow={"imports": "CIF", "exports": "FOB"},
            )
            for row in rows
        ]


def double_registry() -> ConnectorRegistry:
    return ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})


def pre_observation_document_source_config(
    source_id: str,
    *,
    authority: str,
    evidence_class: str,
) -> dict[str, Any]:
    """PRE_OBSERVATION document source recipe — no invented facts."""
    return {
        "authority": authority,
        "access_classification": UNAVAILABLE,
        "documentation_reference": UNAVAILABLE,
        "terms_reference": UNAVAILABLE,
        "endpoint_templates": {"DOCUMENT": "{document_url}", "TERMS": UNAVAILABLE},
        "parameters": {
            "product_all_token": UNAVAILABLE,
            "partner_world_token": UNAVAILABLE,
            "reporter_token": UNAVAILABLE,
            "flow_tokens": UNAVAILABLE,
        },
        "pagination": {
            "kind": "NONE",
            "documentation_reference": UNAVAILABLE,
            "parameters": {},
        },
        "nomenclature": UNAVAILABLE,
        "reporter_code": "SAU",
        "credential_env_var": UNAVAILABLE,
        "rate_limit": {
            "documented_policy": UNAVAILABLE,
            "min_interval_seconds": 2.0,
            "max_attempts": 3,
            "timeout_seconds": 60,
        },
        "license_capture_required": True,
        "default_evidence_class": evidence_class,
        "default_reviewer_status": "unconfirmed_by_responsible_authority",
        "expected_content_types": UNAVAILABLE,
        "user_agent": "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)",
        "recorded_on": UNAVAILABLE,
    }


def document_list_payload(
    source_id: str,
    *,
    entries: list[dict[str, Any]] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Class-D document list double for tests."""
    default_entry = {
        "entry_id": "E-001",
        "document_url": "https://example.test/doc.pdf",
        "publisher_text": "TEST DOUBLE — NOT REAL EVIDENCE",
        "publisher_kind": "producer",
        "document_kind": "product_sheet",
        "languages": ["en"],
        "expected_content_type": "application/pdf",
        "evidence_class_target": "C",
        "supports": ["DOMESTIC_PRODUCT_PORTFOLIO"],
        "title_text": "TEST DOUBLE title",
        "document_date_text": "UNAVAILABLE",
        "source_reference_text": "UNAVAILABLE",
    }
    payload = {
        "schema_version": "1.0.0",
        "list_id": f"{source_id}-v1",
        "source_id": source_id,
        "recorded_on": "2026-09-12",
        "recorded_by_seat": "implementer-composer",
        "consultation_summary_text": "TEST DOUBLE list — not real evidence",
        "documentation_urls_observed": ["https://example.test/docs"],
        "entries": entries if entries is not None else [default_entry],
    }
    payload.update(overrides)
    return payload


def document_fetch_result(body: bytes, content_type: str) -> FetchResult:
    return FetchResult(
        http_status=200,
        headers_subset=(("content-type", content_type),),
        body=body,
        final_url_redacted="https://example.test/doc",
        fetched_at="2026-09-12T00:00:00Z",
        content_length_header=len(body),
    )


def pre_observation_source_config(
    source_id: str, *, stage: Stage, authority: str
) -> dict[str, Any]:
    """DD-12 config recipe only: no invented source facts or evidence rows."""
    return {
        "authority": authority,
        "access_classification": UNAVAILABLE,
        "documentation_reference": UNAVAILABLE,
        "terms_reference": UNAVAILABLE,
        "endpoint_templates": {stage.value: UNAVAILABLE, "TERMS": UNAVAILABLE},
        "parameters": {
            "product_all_token": UNAVAILABLE,
            "partner_world_token": UNAVAILABLE,
            "reporter_token": UNAVAILABLE,
            "flow_tokens": UNAVAILABLE,
            "units": UNAVAILABLE,
        },
        "pagination": {
            "kind": UNAVAILABLE,
            "documentation_reference": UNAVAILABLE,
            "parameters": UNAVAILABLE,
        },
        "nomenclature": UNAVAILABLE,
        "reporter_code": "SAU",
        "credential_env_var": UNAVAILABLE,
        "rate_limit": {
            "documented_policy": UNAVAILABLE,
            "min_interval_seconds": 2.0,
            "max_attempts": 3,
            "timeout_seconds": 60,
        },
        "license_capture_required": True,
        "default_evidence_class": "C" if source_id in {"modon", "saber_registry"} else "B",
        "default_reviewer_status": "unconfirmed_by_responsible_authority",
        "expected_content_types": UNAVAILABLE,
        "user_agent": "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)",
        "recorded_on": UNAVAILABLE,
    }


def institutional_config(source_id: str, stage: Stage) -> dict[str, Any]:
    """Obviously fake observed-contract double; never a production source claim."""
    return {"metadata": {"version": "1.1.0"}, "sources": {source_id: {
        "source_id": source_id, "authority": "FAKE TEST INSTITUTION — NOT REAL EVIDENCE",
        "access_classification": "test_double", "default_evidence_class": "D",
        "default_reviewer_status": "unconfirmed_by_responsible_authority",
        "reporter_code": "SAU", "nomenclature": "TEST-CLASSIFICATION",
        "parameters": {"units": [{"unit": "TEST-main"}, {"unit": "TEST-excluded"}]},
        "endpoint_templates": {stage.value: "https://example.test/data?page={page}"},
        "pagination": {"kind": "PAGE_NUMBER", "parameters": {}},
        "credential_env_var": None, "license_capture_required": False,
        "rate_limit": {"min_interval_seconds": 0},
        "terms_reference": "https://example.test/terms", "documentation_reference": "https://example.test/docs",
    }}}


class InstitutionalDouble(DoubleConnector):
    """Use real framework/mappers; only the external source parser is a double."""
    snapshot_kinds = frozenset({"production", "directory", "registry"})

    @staticmethod
    def parse_rows(payload: bytes, content_type: str) -> list[dict[str, Any]]:
        return json.loads(payload)["rows"]

    def normalize(self, raw: RawArtifact) -> list[Any]:
        from ior_mvp.acquisition import harmonise
        mapper = {Stage.AGGREGATE: harmonise.production_observation_from_row,
                  Stage.DIRECTORY: harmonise.directory_row_from_row,
                  Stage.REGISTRY: harmonise.registry_row_from_row}[raw.contract.query_contract.stage]
        return [mapper(row, field_map={}, source_evidence_id=raw.contract.query_hash)
                for row in self.parse_rows(self.store.read_payload(raw.contract), raw.contract.content_type)]

    def validate(self, raw: RawArtifact):
        from dataclasses import replace
        from ior_mvp.acquisition.contracts import QualityCheck
        rows = self.parse_rows(self.store.read_payload(raw.contract), raw.contract.content_type)
        stage = raw.contract.query_contract.stage
        valid = bool(rows) and all(isinstance(row, dict) and (
            row.get("geography_text") == raw.contract.reporter and bool(row.get("indicator_text"))
            if stage == Stage.AGGREGATE else bool(row.get("source_record_id"))) for row in rows)
        status = "PASS" if valid else "FAIL"
        return replace(super().validate(raw), status=status,
                       checks=(QualityCheck("TEST-row-shape-and-reporter", status, "Class D double only"),))
