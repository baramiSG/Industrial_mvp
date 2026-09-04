"""Test doubles for acquisition connector tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
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
