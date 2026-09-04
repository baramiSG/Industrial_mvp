"""Coverage selection tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import BaseConnector, ConnectorRegistry
from ior_mvp.acquisition.contracts import (
    CompletenessBasis,
    ProductScope,
    QueryContract,
    Stage,
    UnavailableReason,
)
from ior_mvp.acquisition.coverage import evaluate_coverage, not_attempted_coverage
from ior_mvp.acquisition.pipeline import build_snapshots
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import FakeTransport, seed_unit


def _config_with_test_source(source_id: str = "TEST-FIXTURE") -> dict:
    config = acquisition_sources_config()
    sources = dict(config["sources"])
    sources[source_id] = {
        **config["sources"]["wits_trade"],
        "source_id": source_id,
    }
    return {**config, "sources": sources}


def test_not_attempted_coverage_unavailable_basis() -> None:
    contract = QueryContract(
        source_id="wits_trade",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )
    cov = not_attempted_coverage(
        contract,
        run_id="20260904T000000Z",
        stop_reason=UnavailableReason.MAX_REQUESTS_EXHAUSTED,
    )
    assert cov.status == "INCOMPLETE"
    assert cov.completeness_basis == CompletenessBasis.UNAVAILABLE
    assert cov.pages_fetched == 0


def test_page_one_of_two_blocks_universe_snapshot(tmp_path: Path) -> None:
    from tests.acquisition_doubles import DoubleConnector
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.snapshots import build_universe_snapshot

    config = _config_with_test_source()
    raw_cfg = config["raw_store"]
    store = RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    registry = ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})
    source_cfg = {**config["sources"]["wits_trade"], "source_id": "TEST-FIXTURE"}
    contract = QueryContract(
        source_id="TEST-FIXTURE",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T120000Z",
        payload=(
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "acquisition"
            / "test_double_trade_page1_of_2.json"
        ).read_bytes(),
        source_config=source_cfg,
    )
    with pytest.raises(Exception):
        build_universe_snapshot(
            store, config, registry, source_id="TEST-FIXTURE"
        )


def test_complete_universe_write_from_single_page(tmp_path: Path) -> None:
    from tests.acquisition_doubles import DoubleConnector

    config = _config_with_test_source()
    raw_cfg = config["raw_store"]
    store = RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    registry = ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})
    source_cfg = {**config["sources"]["wits_trade"], "source_id": "TEST-FIXTURE"}
    contract = QueryContract(
        source_id="TEST-FIXTURE",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T120000Z",
        payload=(
            PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_rows.json"
        ).read_bytes(),
        source_config=source_cfg,
    )
    from ior_mvp.acquisition.snapshots import build_universe_snapshot

    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    assert record["coverage"]["status"] == "COMPLETE"
