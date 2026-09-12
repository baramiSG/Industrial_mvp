"""Registry injection, provenance pins and validation at snapshot boundaries."""

import importlib.util
import json
from dataclasses import replace
from datetime import date

import pytest

from ior_mvp.acquisition import repository, snapshots
from ior_mvp.acquisition.connectors.base import ConnectorRegistry, default_registry
from ior_mvp.acquisition.connectors.wits_trade import WitsTradeConnector
from ior_mvp.acquisition.contracts import AcquisitionUnavailable, ProductScope, QueryContract, Stage
from ior_mvp.acquisition.contracts import SnapshotWriteConflict
from ior_mvp.acquisition.pipeline import PipelineDeps, build_snapshots
from tests.acquisition_doubles import DoubleConnector, FakeTransport, seed_unit
from tests.test_acquisition_snapshots import _config_with_test_source, _temp_store, _fixture


def kinds_module():
    assert importlib.util.find_spec("ior_mvp.acquisition.kinds") is not None, "kind registry is missing"
    from ior_mvp.acquisition import kinds
    return kinds


def seed(tmp_path, *, source_id="TEST-FIXTURE", stage=Stage.PARTNERS, payload=None):
    config = _config_with_test_source(source_id)
    store = _temp_store(tmp_path)
    contract = QueryContract(source_id, stage, "SAU", "WLD", "imports", ProductScope.EXPLICIT if stage == Stage.PARTNERS else ProductScope.ALL_HS6, ("721049",) if stage == Stage.PARTNERS else ("ALL",), "H0", ("2024",))
    seed_unit(store, contract=contract, run_id="20260904T120000Z", payload=payload or _fixture("test_double_trade_rows.json"), source_config=config["sources"][source_id])
    return config, store


def test_default_registry_views_ids_and_pipeline_default(tmp_path):
    kinds = kinds_module().default_kind_registry()
    assert kinds.ids() == ("directory", "partners", "production", "registry", "tariff", "universe")
    assert snapshots.SNAPSHOT_ROOTS == kinds.roots()
    assert snapshots.KIND_STAGE == {kind: kinds.stage_for(kind) for kind in kinds.ids()}
    assert {kind: kinds.get(kind).config_version for kind in kinds.ids()} == {"universe": "1.3.0", "tariff": "1.0.0", "partners": "1.0.0", "production": "1.1.0", "directory": "1.1.0", "registry": "1.1.0"}
    assert kinds.snapshot_id("partners", source_id="wits_trade", nomenclature="H0", as_of_date=date(2026, 9, 3)) == "PARTNERS-SAU-WITS-TRADE-2026-09-03"
    deps = PipelineDeps({}, _temp_store(tmp_path), FakeTransport({}, []), default_registry(), "run", {}, lambda _: None)
    assert deps.kinds.ids() == kinds.ids()
    with pytest.raises(ValueError, match="Unknown"):
        kinds.snapshot_id("UNKNOWN", source_id="wits_trade", nomenclature="H0", as_of_date=date(2026, 9, 3))
    with pytest.raises(ValueError, match="Unknown"):
        build_snapshots("UNKNOWN", deps=deps)


@pytest.mark.parametrize("version", ["1.1.0", "arbitrary-other-version"])
def test_kind_pin_controls_every_transformation_stamp(tmp_path, version):
    kinds = kinds_module().default_kind_registry()
    config, store = seed(tmp_path)
    config["metadata"] = {"version": version}
    record = snapshots.build_row_snapshot(store, config, ConnectorRegistry({"TEST-FIXTURE": DoubleConnector}), kind="partners", source_id="TEST-FIXTURE", kinds=kinds)
    assert record["transformation_record"]["config_version"] == "1.0.0"
    assert record["evidence"]
    assert all(p["transformation_record"]["config_version"] == "1.0.0" for p in record["evidence"])


def test_connector_snapshot_helper_cannot_leak_live_config_version(tmp_path):
    payload = json.dumps({"dataset": {"data": json.loads(_fixture("test_double_trade_rows.json"))["rows"]}}).encode()
    config, store = seed(tmp_path, source_id="wits_trade", stage=Stage.UNIVERSE, payload=payload)
    connector = WitsTradeConnector(source_config=config["sources"]["wits_trade"], store=store, transport=None, run_id="", environ={}, config_version="1.1.0")
    record = connector.snapshot([], date(2099, 1, 1))
    assert record["transformation_record"]["config_version"] == "1.3.0"
    assert all(p["transformation_record"]["config_version"] == "1.3.0" for p in record["evidence"])


def test_registry_only_kind_build_write_load_reconstruct_and_cache_isolation(tmp_path):
    module = kinds_module()
    spec = replace(module.default_kind_registry().get("partners"), kind="TEST-KIND", root="data/snapshots/test-kind", id_prefix="TEST-KIND")
    kinds = module.KindRegistry({"TEST-KIND": spec})
    class TestConnector(DoubleConnector):
        snapshot_kinds = frozenset({"TEST-KIND"})
    config, store = seed(tmp_path)
    registry = ConnectorRegistry({"TEST-FIXTURE": TestConnector})
    repository.clear_acquisition_caches()
    before = repository.partner_snapshots()
    record = snapshots.build_row_snapshot(store, config, registry, kind="TEST-KIND", source_id="TEST-FIXTURE", kinds=kinds)
    path = snapshots.write_snapshot(record, tmp_path, allow_test_double=True, kinds=kinds)
    assert kinds.roots() == {"TEST-KIND": "data/snapshots/test-kind"}
    loaded = repository.acquired_snapshots("TEST-KIND", kinds=kinds, data_root=tmp_path, allow_test_double=True)
    assert loaded == {record["snapshot_id"]: json.loads(path.read_text())}
    assert snapshots.reconstruct(path, store, config, registry, kinds=kinds).match
    assert repository.partner_snapshots() is before
    with pytest.raises(ValueError, match="Unknown"):
        repository.acquired_snapshots("TEST-KIND")
    path.rename(path.with_name("wrong-id.json"))
    with pytest.raises(ValueError, match="file name"):
        repository.acquired_snapshots("TEST-KIND", kinds=kinds, data_root=tmp_path, allow_test_double=True)


def test_builder_refuses_connector_validation_failure(tmp_path):
    config, store = seed(tmp_path)
    class RejectingConnector(DoubleConnector):
        def validate(self, raw):
            return replace(super().validate(raw), status="FAIL")
    with pytest.raises(AcquisitionUnavailable):
        snapshots.build_partner_snapshot(store, config, ConnectorRegistry({"TEST-FIXTURE": RejectingConnector}), source_id="TEST-FIXTURE")


def _universe_validator_record(rows):
    return {
        "product_scope": "ALL_HS6",
        "rows": rows,
        "coverage": {
            "status": "COMPLETE",
            "units": [
                {
                    "status": "COMPLETE",
                    "completeness_basis": "PROVIDER_COUNT",
                }
            ],
        },
    }


def test_universe_validator_requires_one_hs_revision_per_unit():
    validator = kinds_module().default_kind_registry().get("universe").validator_extra
    record = _universe_validator_record([
        {"year": 2024, "flow": "imports", "hs_revision": "H5"},
        {"year": 2024, "flow": "imports", "hs_revision": "H6"},
    ])

    with pytest.raises(ValueError, match="one classification"):
        validator(record)


@pytest.mark.parametrize("revision", [None, "", 6])
def test_universe_validator_requires_hs_revision_on_every_row(revision):
    validator = kinds_module().default_kind_registry().get("universe").validator_extra
    record = _universe_validator_record([
        {"year": 2024, "flow": "imports", "hs_revision": revision},
    ])

    with pytest.raises(ValueError, match="hs_revision"):
        validator(record)


@pytest.mark.parametrize("row", [{}, {"year": 2024, "hs6": "BAD", "reporter": "SAU", "flow": "imports"}, {"year": 2024, "hs6": "721049", "reporter": "USA", "flow": "imports"}])
def test_wits_builder_rejects_invalid_row_shape_or_reporter(tmp_path, row):
    payload = json.dumps({"dataset": {"data": [row]}}).encode()
    config, store = seed(tmp_path, source_id="wits_trade", stage=Stage.UNIVERSE, payload=payload)
    with pytest.raises(AcquisitionUnavailable):
        snapshots.build_universe_snapshot(store, config, default_registry(), source_id="wits_trade")


def test_unknown_kind_fails_closed_at_write_and_reconstruct(tmp_path):
    with pytest.raises(ValueError, match="Unknown"):
        snapshots.write_snapshot({"kind": "UNKNOWN"}, tmp_path)
    config, store = seed(tmp_path)
    record = snapshots.build_partner_snapshot(store, config, ConnectorRegistry({"TEST-FIXTURE": DoubleConnector}), source_id="TEST-FIXTURE")
    record["kind"] = "UNKNOWN"
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Unknown"):
        snapshots.reconstruct(path, store, config, default_registry())


@pytest.mark.parametrize("unsafe", ["public", "synthetic", "parent", "absolute", "symlink"])
@pytest.mark.parametrize("operation", ["write", "load"])
def test_injected_kind_root_cannot_escape_or_access_frozen_evidence(tmp_path, monkeypatch, unsafe, operation):
    module = kinds_module()
    config, store = seed(tmp_path / "seed")
    record = snapshots.build_partner_snapshot(store, config, ConnectorRegistry({"TEST-FIXTURE": DoubleConnector}), source_id="TEST-FIXTURE")
    project = tmp_path / "project"
    data_root = project / "data"
    outside = tmp_path / "outside"
    roots = {
        "public": "data/snapshots/public", "synthetic": "data/synthetic",
        "parent": "data/../escape", "absolute": str(outside),
        "symlink": "data/snapshots/linked",
    }
    targets = {
        "public": data_root / "snapshots" / "public", "synthetic": data_root / "synthetic",
        "parent": project / "escape", "absolute": outside, "symlink": outside,
    }
    target = targets[unsafe]
    target.mkdir(parents=True)
    if unsafe == "symlink":
        (data_root / "snapshots").mkdir(parents=True)
        (data_root / "snapshots" / "linked").symlink_to(outside, target_is_directory=True)
    spec = replace(module.default_kind_registry().get("partners"), root=roots[unsafe])
    kinds = module.KindRegistry({"partners": spec})
    monkeypatch.setattr(snapshots, "PROJECT_ROOT", project)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    if operation == "load":
        def unexpected_read(path):
            raise AssertionError("unsafe root reached a snapshot read")
        monkeypatch.setattr(repository, "_read_record", unexpected_read)
    with pytest.raises((ValueError, SnapshotWriteConflict)):
        if operation == "write":
            snapshots.write_snapshot(record, data_root, kinds=kinds, allow_test_double=True)
        else:
            repository.acquired_snapshots("partners", data_root=data_root, kinds=kinds, allow_test_double=True)
    assert sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")) == before
