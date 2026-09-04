"""Connector registry and acquire-path tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import BaseConnector, default_registry
from ior_mvp.acquisition.connectors.un_comtrade import UnComtradeConnector
from ior_mvp.acquisition.contracts import (
    ProductScope,
    QueryContract,
    Stage,
    UnavailableReason,
    UnavailableRecord,
)
from ior_mvp.acquisition.pipeline import PipelineDeps, _run_units
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.snapshots import build_universe_snapshot
from ior_mvp.acquisition.transport import FetchResult
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import DoubleConnector, FakeTransport, seed_unit


def test_default_registry_ids() -> None:
    reg = default_registry()
    assert reg.ids() == ("baci_cepii", "un_comtrade", "wits_trade", "zatca_tariff")


def test_snapshot_kinds_per_dd22() -> None:
    reg = default_registry()
    assert reg.snapshot_kinds("wits_trade") == frozenset({"universe", "partners"})
    assert reg.snapshot_kinds("zatca_tariff") == frozenset({"tariff"})
    assert reg.snapshot_kinds("baci_cepii") == frozenset()


def _test_store(tmp_path: Path) -> RawStore:
    raw_cfg = acquisition_sources_config()["raw_store"]
    return RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )


def _universe_contract(source_id: str = "TEST-PAGE") -> QueryContract:
    return QueryContract(
        source_id=source_id,
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )


def _paginated_source_config(source_id: str = "TEST-PAGE") -> dict:
    return {
        **acquisition_sources_config()["sources"]["wits_trade"],
        "source_id": source_id,
        "license_capture_required": False,
        "terms_reference": "UNAVAILABLE",
        "endpoint_templates": {
            "UNIVERSE": "http://fake.test/universe?page={page}",
            "TERMS": "UNAVAILABLE",
        },
        "pagination": {
            "kind": "PAGE_NUMBER",
            "documentation_reference": "test",
            "parameters": {},
        },
    }


def _fetch_result(body: bytes) -> FetchResult:
    return FetchResult(
        http_status=200,
        headers_subset=(("content-type", "application/json"),),
        body=body,
        final_url_redacted="http://fake.test/universe",
        fetched_at="2026-09-04T00:00:00Z",
        content_length_header=len(body),
    )


def test_acquire_credential_absent_records_unavailable(tmp_path: Path) -> None:
    config = acquisition_sources_config()
    store = _test_store(tmp_path)
    source_cfg = config["sources"]["un_comtrade"]
    connector = UnComtradeConnector(
        source_config=source_cfg,
        store=store,
        transport=FakeTransport(responses={}, calls=[]),
        run_id="20260904T120000Z",
        environ={},
    )
    contract = QueryContract(
        source_id="un_comtrade",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="HS2017",
        periods=("2024",),
    )
    result = connector.acquire(contract, max_requests=5)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.CREDENTIAL_ABSENT
    assert (tmp_path / "raw" / "un_comtrade").exists()


def test_acquire_endpoint_unverified_records_unavailable(tmp_path: Path) -> None:
    store = _test_store(tmp_path)
    source_cfg = {
        **_paginated_source_config("TEST-UNVERIFIED"),
        "parameters": {
            **acquisition_sources_config()["sources"]["wits_trade"]["parameters"],
            "product_all_token": "UNAVAILABLE",
        },
    }
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=FakeTransport(responses={}, calls=[]),
        run_id="20260904T120000Z",
        environ={},
    )
    result = connector.acquire(_universe_contract("TEST-UNVERIFIED"), max_requests=5)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED


def test_fake_transport_max_requests_one_stops_after_page_one(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    store = _test_store(tmp_path)
    source_id = "TEST-PAGE"
    source_cfg = _paginated_source_config(source_id)
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={},
    )
    contract = _universe_contract(source_id)
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.MAX_REQUESTS_EXHAUSTED
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.pages_fetched == 1
    assert len(transport.calls) == 1
    registry = ConnectorRegistry({source_id: DoubleConnector})
    config = acquisition_sources_config()
    config = {
        **config,
        "sources": {**config["sources"], source_id: source_cfg},
    }
    with pytest.raises(Exception):
        build_universe_snapshot(store, config, registry, source_id=source_id)


def test_fake_transport_two_page_complete_write(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    store = _test_store(tmp_path)
    source_id = "TEST-PAGE"
    source_cfg = _paginated_source_config(source_id)
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={},
    )
    result = connector.acquire(_universe_contract(source_id), max_requests=2)
    assert isinstance(result, tuple)
    artifacts, coverage = result
    assert coverage.status == "COMPLETE"
    assert len(artifacts) == 2
    assert len(transport.calls) == 2


def test_multi_unit_budget_exhaustion_never_attempted_coverage(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    source_id = "TEST-BUDGET"
    source_cfg = _paginated_source_config(source_id)
    config = acquisition_sources_config()
    config = {
        **config,
        "sources": {**config["sources"], source_id: source_cfg},
    }
    store = _test_store(tmp_path)
    registry = ConnectorRegistry({source_id: DoubleConnector})
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    units = (
        _universe_contract(source_id),
        QueryContract(
            source_id=source_id,
            stage=Stage.UNIVERSE,
            reporter="SAU",
            partner="WLD",
            flow="exports",
            product_scope=ProductScope.ALL_HS6,
            product_codes=("ALL",),
            nomenclature="H0",
            periods=("2024",),
        ),
    )
    deps = PipelineDeps(
        config=config,
        store=store,
        transport=transport,
        registry=registry,
        run_id="20260904T130000Z",
        environ={},
        sleeper=lambda _: None,
    )
    report = _run_units(
        deps,
        source_id=source_id,
        stage=Stage.UNIVERSE,
        units=units,
        max_requests=2,
    )
    assert report.exit_code == 3
    exports_hash = units[1].query_hash()
    cov_path = (
        tmp_path
        / "raw"
        / source_id
        / exports_hash
        / "20260904T130000Z"
        / "coverage.json"
    )
    assert cov_path.exists()
    cov = json.loads(cov_path.read_text(encoding="utf-8"))
    assert cov["pages_fetched"] == 0
    assert cov["status"] == "INCOMPLETE"
