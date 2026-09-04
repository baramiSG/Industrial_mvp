"""Snapshot builder validation tests."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from ior_mvp.acquisition import repository
from ior_mvp.acquisition.connectors.base import ConnectorRegistry
from ior_mvp.acquisition.contracts import (
    CompletenessBasis,
    ProductScope,
    QueryContract,
    Stage,
    UnavailableReason,
)
from ior_mvp.acquisition.coverage import evaluate_coverage, not_attempted_coverage
from ior_mvp.acquisition.passports import assert_passport_complete
from ior_mvp.acquisition.pipeline import build_snapshots
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.snapshots import (
    build_partner_snapshot,
    build_universe_snapshot,
    snapshot_id,
    validate_partner_snapshot,
    write_snapshot,
)
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import DoubleConnector, seed_unit


def _config_with_test_source(source_id: str = "TEST-FIXTURE") -> dict:
    config = acquisition_sources_config()
    source_cfg = {**config["sources"]["wits_trade"], "source_id": source_id}
    sources = dict(config["sources"])
    sources[source_id] = source_cfg
    return {**config, "sources": sources}


def _config_with_test_sources(*source_ids: str) -> dict:
    config = acquisition_sources_config()
    sources = dict(config["sources"])
    for source_id in source_ids:
        sources[source_id] = {
            **config["sources"]["wits_trade"],
            "source_id": source_id,
        }
    return {**config, "sources": sources}


def _temp_store(tmp_path: Path) -> RawStore:
    config = acquisition_sources_config()
    raw_cfg = config["raw_store"]
    return RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )


def _double_registry() -> ConnectorRegistry:
    return ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})


def _fixture(name: str) -> bytes:
    return (PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / name).read_bytes()


def test_repository_partner_snapshot_valid() -> None:
    snaps = list((PROJECT_ROOT / "data" / "snapshots" / "partners").glob("*.json"))
    assert snaps
    for path in snaps:
        record = json.loads(path.read_text(encoding="utf-8"))
        validate_partner_snapshot(record)
        assert record["evidence"]
        for passport in record["evidence"]:
            assert_passport_complete(passport)
        for ref in record["raw_artifact_refs"]:
            assert (PROJECT_ROOT / ref["path"]).exists()


def test_acquired_snapshot_loaders_read_only_their_kind_and_validate() -> None:
    repository.clear_acquisition_caches()
    loaders = {
        "universe": repository.universe_snapshots,
        "tariff": repository.tariff_snapshots,
        "partners": repository.partner_snapshots,
    }
    for kind, loader in loaders.items():
        directory = PROJECT_ROOT / "data" / "snapshots" / kind
        expected_ids = {
            json.loads(path.read_text(encoding="utf-8"))["snapshot_id"]
            for path in directory.glob("*.json")
        }
        records = loader()
        assert set(records) == expected_ids
        for snapshot_id_, record in records.items():
            assert record["snapshot_id"] == snapshot_id_
            assert record["kind"] == kind
            assert record["source_boundary"] == "public"
        assert loader() is records
    assert repository.partner_snapshots()


def test_acquired_snapshot_loaders_reject_test_double(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    registry = _double_registry()
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
        run_id="20260904T100000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    write_snapshot(record, tmp_path, allow_test_double=True)
    monkeypatch.setattr(repository, "DATA_ROOT", tmp_path)
    repository.clear_acquisition_caches()
    try:
        with pytest.raises(ValueError):
            repository.universe_snapshots()
        assert repository.tariff_snapshots() == {}
        assert repository.partner_snapshots() == {}
    finally:
        repository.clear_acquisition_caches()


def test_partner_rebuild_as_of_date_stable(tmp_path: Path) -> None:
    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    registry = _double_registry()
    source_cfg = {
        **config["sources"]["wits_trade"],
        "source_id": "TEST-FIXTURE",
    }
    contract = QueryContract(
        source_id="TEST-FIXTURE",
        stage=Stage.PARTNERS,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.EXPLICIT,
        product_codes=("721049",),
        nomenclature="H0",
        periods=("2024",),
    )
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T120000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    with patch("ior_mvp.acquisition.snapshots.date") as mock_date:
        mock_date.today.return_value = date(2099, 1, 1)
        mock_date.fromisoformat = date.fromisoformat
        record = build_partner_snapshot(
            store, config, registry, source_id="TEST-FIXTURE"
        )
    assert record["as_of_date"] == "2026-09-04"


def test_proof_a_superseded_run_not_selected(tmp_path: Path) -> None:
    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    registry = _double_registry()
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
        run_id="20260904T100000Z",
        payload=_fixture("test_double_trade_page1_of_2.json"),
        source_config=source_cfg,
    )
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T110000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    assert record["coverage"]["units"][0]["selected_run_id"] == "20260904T110000Z"
    assert "20260904T100000Z" in record["coverage"]["units"][0]["superseded_run_ids"]


def test_proof_b_sibling_source_isolation(tmp_path: Path) -> None:
    config = _config_with_test_sources("TEST-A", "TEST-B")
    store = _temp_store(tmp_path)
    registry = ConnectorRegistry(
        {"TEST-A": DoubleConnector, "TEST-B": DoubleConnector}
    )
    for sid in ("TEST-A", "TEST-B"):
        source_cfg = {**config["sources"]["wits_trade"], "source_id": sid}
        contract = QueryContract(
            source_id=sid,
            stage=Stage.UNIVERSE,
            reporter="SAU",
            partner="WLD",
            flow="imports",
            product_scope=ProductScope.ALL_HS6,
            product_codes=("ALL",),
            nomenclature="H0",
            periods=("2024",),
        )
        payload = (
            _fixture("test_double_trade_page1_of_2.json")
            if sid == "TEST-A"
            else _fixture("test_double_trade_rows.json")
        )
        seed_unit(
            store,
            contract=contract,
            run_id="20260904T120000Z",
            payload=payload,
            source_config=source_cfg,
        )
    with pytest.raises(Exception):
        build_universe_snapshot(store, config, registry, source_id="TEST-A")
    record_b = build_universe_snapshot(
        store, config, registry, source_id="TEST-B"
    )
    assert record_b["source_id"] == "TEST-B"


def test_proof_c_distinct_source_qualified_ids(tmp_path: Path) -> None:
    class ConnectorA(DoubleConnector):
        source_id = "TEST-A"

    class ConnectorB(DoubleConnector):
        source_id = "TEST-B"

    config = _config_with_test_sources("TEST-A", "TEST-B")
    store = _temp_store(tmp_path)
    registry = ConnectorRegistry({"TEST-A": ConnectorA, "TEST-B": ConnectorB})
    ids: list[str] = []
    for sid in ("TEST-A", "TEST-B"):
        source_cfg = {**config["sources"]["wits_trade"], "source_id": sid}
        contract = QueryContract(
            source_id=sid,
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
            payload=_fixture("test_double_trade_rows.json"),
            source_config=source_cfg,
        )
        record = build_universe_snapshot(
            store, config, registry, source_id=sid
        )
        ids.append(record["snapshot_id"])
    assert len(set(ids)) == 2


def test_proof_d_baci_raw_only_in_build_report(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.baci_cepii import BaciCepiiConnector
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.pipeline import PipelineDeps

    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    baci_cfg = {
        **config["sources"]["baci_cepii"],
        "pagination": {"kind": "NONE", "documentation_reference": "test", "parameters": {}},
    }
    baci_contract = QueryContract(
        source_id="baci_cepii",
        stage=Stage.BULK,
        reporter="SAU",
        partner="WLD",
        flow="UNAVAILABLE",
        product_scope=ProductScope.NOT_APPLICABLE,
        product_codes=(),
        nomenclature="H0",
        periods=("2024",),
    )
    seed_unit(
        store,
        contract=baci_contract,
        run_id="20260904T120000Z",
        payload=_fixture("test_double_bulk_rows.json"),
        source_config=baci_cfg,
    )
    source_cfg = {**config["sources"]["wits_trade"], "source_id": "TEST-FIXTURE"}
    universe_contract = QueryContract(
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
        contract=universe_contract,
        run_id="20260904T120000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    registry = ConnectorRegistry(
        {"TEST-FIXTURE": DoubleConnector, "baci_cepii": BaciCepiiConnector}
    )
    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    assert not any(
        ref["source_id"] == "baci_cepii" for ref in record["raw_artifact_refs"]
    )
    deps = PipelineDeps(
        config=config,
        store=store,
        transport=None,
        registry=registry,
        run_id="20260904T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    report = build_snapshots(
        "universe", deps, data_root=tmp_path, allow_test_double=True
    )
    assert "baci_cepii" in report.raw_only


def test_proof_e_selection_changed_on_newer_run(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import default_registry
    from ior_mvp.acquisition.snapshots import reconstruct, write_snapshot

    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    registry = _double_registry()
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
        run_id="20260904T100000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    path = write_snapshot(record, tmp_path, allow_test_double=True)
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T110000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    result = reconstruct(path, store, config, registry)
    assert not result.match
    assert result.detail.get("reason") == "SELECTION_CHANGED"
