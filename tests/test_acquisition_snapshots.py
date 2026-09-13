"""Snapshot builder validation tests."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from ior_mvp.acquisition import repository
from ior_mvp.acquisition.connectors.base import ConnectorRegistry, default_registry
from ior_mvp.acquisition.contracts import (
    CompletenessBasis,
    ProductScope,
    QueryContract,
    Stage,
    UnavailableReason,
    canonical_dumps,
)
from ior_mvp.acquisition.coverage import (
    evaluate_coverage,
    not_attempted_coverage,
    select_latest_units,
)
from ior_mvp.acquisition.kinds import default_kind_registry
from ior_mvp.acquisition.passports import assert_passport_complete
from ior_mvp.acquisition.pipeline import build_snapshots
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.snapshots import (
    build_partner_snapshot,
    build_row_snapshot,
    build_universe_snapshot,
    reconstruct_pinned,
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


def test_un_comtrade_partner_snapshot_id_is_distinct_and_wits_snapshot_bytes_unchanged() -> None:
    import hashlib

    root = PROJECT_ROOT / "data" / "snapshots" / "partners"
    expected = {
        "PARTNERS-SAU-WITS-TRADE-2026-09-12.json": (
            "0a5a564594ecdb35ad129f7c111e3e5f62ba6d152fac275cea6d0ecc0e08dc63"
        ),
        "PARTNERS-SAU-WITS-TRADE-2026-09-03.json": (
            "cdcc904af656b8d1ba02f6dd23593071cddcf21739e58290d4cf197e6723657f"
        ),
    }
    for name, digest in expected.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    for path in root.glob("PARTNERS-SAU-UN-COMTRADE-*.json"):
        assert path.name not in expected
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["source_id"] == "un_comtrade"


def test_same_day_collision_uses_deterministic_scope_and_reconstructs(
    tmp_path: Path,
) -> None:
    config = _config_with_test_source()
    store = _temp_store(tmp_path)
    registry = ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})
    source_config = config["sources"]["TEST-FIXTURE"]

    first = QueryContract(
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
        contract=first,
        run_id="20260904T120000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_config,
    )
    unscoped = build_partner_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    unscoped_path = write_snapshot(
        unscoped, tmp_path, allow_test_double=True
    )
    assert unscoped_path.stem == "PARTNERS-SAU-TEST-FIXTURE-2026-09-04"
    assert "scope_units" not in unscoped
    assert "coexists_with" not in unscoped

    second = QueryContract(
        source_id="TEST-FIXTURE",
        stage=Stage.PARTNERS,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.EXPLICIT,
        product_codes=("730110",),
        nomenclature="H0",
        periods=("2024",),
    )
    seed_unit(
        store,
        contract=second,
        run_id="20260904T130000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_config,
    )
    latest = select_latest_units(
        store, source_id="TEST-FIXTURE", stage=Stage.PARTNERS
    )
    second_key = ("730110", "imports", "2024")
    collision = build_row_snapshot(
        store,
        config,
        registry,
        kind="partners",
        source_id="TEST-FIXTURE",
        selected_override={second_key: latest[second_key]},
    )
    scoped_path = write_snapshot(
        collision, tmp_path, allow_test_double=True
    )
    scoped = json.loads(scoped_path.read_text(encoding="utf-8"))
    scope_units = sorted(
        (unit["unit_key"] for unit in collision["coverage"]["units"]),
        key=canonical_dumps,
    )
    scope12 = hashlib.sha256(
        canonical_dumps(scope_units).encode("utf-8")
    ).hexdigest()[:12]

    assert scoped_path.stem == f"{unscoped_path.stem}-{scope12}"
    assert scoped["snapshot_id"] == scoped_path.stem
    assert scoped["scope_units"] == scope_units
    assert scoped["coexists_with"] == unscoped_path.stem
    assert "supersedes" not in scoped
    assert unscoped_path.read_text(encoding="utf-8") == canonical_dumps(unscoped)
    assert reconstruct_pinned(scoped_path, store, config, registry).match
    assert reconstruct_pinned(unscoped_path, store, config, registry).match
    assert write_snapshot(
        unscoped, tmp_path, allow_test_double=True
    ) == unscoped_path

    wrong_scope = deepcopy(scoped)
    wrong_scope["snapshot_id"] = f"{scoped['snapshot_id'][:-1]}0"
    with pytest.raises(ValueError, match="snapshot_id mismatch"):
        validate_partner_snapshot(
            wrong_scope, allow_test_double=True, data_root=tmp_path
        )

    overlapping = build_partner_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    with pytest.raises(ValueError, match="overlap"):
        write_snapshot(overlapping, tmp_path, allow_test_double=True)

    missing_sibling = deepcopy(scoped)
    with pytest.raises(ValueError, match="sibling does not exist"):
        validate_partner_snapshot(
            missing_sibling,
            allow_test_double=True,
            data_root=tmp_path / "missing",
        )

    superseding = deepcopy(scoped)
    superseding["supersedes"] = unscoped_path.stem
    with pytest.raises(ValueError, match="must not supersede"):
        validate_partner_snapshot(
            superseding, allow_test_double=True, data_root=tmp_path
        )


def test_s15_scoped_partner_snapshot_is_four_units_and_s14_is_unchanged() -> None:
    root = PROJECT_ROOT / "data"
    partner_root = root / "snapshots" / "partners"
    sibling_path = (
        partner_root / "PARTNERS-SAU-UN-COMTRADE-2026-09-13.json"
    )
    scoped_path = (
        partner_root
        / "PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196.json"
    )
    assert hashlib.sha256(sibling_path.read_bytes()).hexdigest() == (
        "e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b"
    )
    sibling = json.loads(sibling_path.read_text(encoding="utf-8"))
    scoped = json.loads(scoped_path.read_text(encoding="utf-8"))
    scoped_units = {tuple(unit) for unit in scoped["scope_units"]}
    sibling_units = {
        tuple(unit["unit_key"]) for unit in sibling["coverage"]["units"]
    }
    assert scoped_units == {
        ("294110", "imports", "2024"),
        ("294120", "imports", "2024"),
        ("310430", "imports", "2024"),
        ("310510", "imports", "2024"),
    }
    assert scoped_units.isdisjoint(sibling_units)
    assert scoped["coverage"]["units_requested"] == 4
    assert scoped["coverage"]["units_complete"] == 4
    assert scoped["coverage"]["units_excluded"] == []
    assert scoped["transformation_record"]["exclusions"] == []
    assert not any(row["hs6"] == "721061" for row in scoped["rows"])
    validate_partner_snapshot(scoped, data_root=root)

    config = acquisition_sources_config()
    raw_config = config["raw_store"]
    store = RawStore(
        root / "raw",
        max_artifact_bytes=raw_config["max_artifact_bytes_compressed"],
        max_store_bytes=raw_config["max_store_bytes_compressed"],
    )
    registry = default_registry()
    assert reconstruct_pinned(
        sibling_path, store, config, registry
    ).match
    assert reconstruct_pinned(
        scoped_path, store, config, registry
    ).match


def test_acquired_snapshot_loaders_read_only_their_kind_and_validate() -> None:
    repository.clear_acquisition_caches()
    loaders = {
        "universe": repository.universe_snapshots,
        "tariff": repository.tariff_snapshots,
        "partners": repository.partner_snapshots,
        "production": repository.production_snapshots,
        "directory": repository.directory_snapshots,
        "registry": repository.registry_snapshots,
    }
    assert set(loaders) == set(default_kind_registry().ids())
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


def test_partner_snapshot_excludes_complete_transport_unit_with_unparsed_page(
    tmp_path: Path,
) -> None:
    config = _config_with_test_source("TEST-FIXTURE")
    store = _temp_store(tmp_path)
    registry = _double_registry()
    source_cfg = {
        **config["sources"]["wits_trade"],
        "source_id": "TEST-FIXTURE",
    }
    for code in ("721049", "721061"):
        contract = QueryContract(
            source_id="TEST-FIXTURE",
            stage=Stage.PARTNERS,
            reporter="SAU",
            partner="WLD",
            flow="imports",
            product_scope=ProductScope.EXPLICIT,
            product_codes=(code,),
            nomenclature="H0",
            periods=("2024",),
        )
        artifact = seed_unit(
            store,
            contract=contract,
            run_id="20260904T120000Z",
            payload=_fixture("test_double_trade_rows.json"),
            source_config=source_cfg,
        )
        if code == "721061":
            page_path = (
                store.unit_dir(
                    "TEST-FIXTURE",
                    artifact.contract.query_hash,
                    artifact.contract.run_id,
                )
                / "page-0001.contract.json"
            )
            page = json.loads(page_path.read_text(encoding="utf-8"))
            page["normalization_status"] = "UNPARSED"
            page["normalization_reason"] = "no_rows_parsed"
            page_path.write_text(
                json.dumps(page, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n",
                encoding="utf-8",
            )

    record = build_partner_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    assert record["coverage"]["units_requested"] == 2
    assert record["coverage"]["units_complete"] == 1
    assert record["coverage"]["units_excluded"] == [
        {
            "reason": "FORMAT_NOT_PARSEABLE",
            "selected_run_id": "20260904T120000Z",
            "unit_key": ["721061", "imports", "2024"],
        }
    ]
    assert record["transformation_record"]["exclusions"] == record["coverage"][
        "units_excluded"
    ]


def test_pinned_reconstruction_keeps_historical_snapshot_reproducible(
    tmp_path: Path,
) -> None:
    from ior_mvp.acquisition.snapshots import reconstruct, reconstruct_pinned

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
    original = build_partner_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    path = write_snapshot(original, tmp_path, allow_test_double=True)
    seed_unit(
        store,
        contract=contract,
        run_id="20260905T120000Z",
        payload=_fixture("test_double_trade_rows.json"),
        source_config=source_cfg,
    )
    assert reconstruct(path, store, config, registry).detail["reason"] == (
        "SELECTION_CHANGED"
    )
    assert reconstruct_pinned(path, store, config, registry).match


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
