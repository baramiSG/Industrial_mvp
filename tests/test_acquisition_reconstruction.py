"""Reconstruction proof tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import ConnectorRegistry, default_registry
from ior_mvp.acquisition.contracts import (
    AcquisitionConfigurationError,
    ProductScope,
    QueryContract,
    Stage,
    unit_key,
)
from ior_mvp.acquisition.pipeline import plan_requests, plan_units
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.snapshots import reconstruct, snapshot_sha256, write_snapshot
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import DoubleConnector, seed_unit


def test_reconstruct_matches_repository_partner_snapshot() -> None:
    config = acquisition_sources_config()
    raw_cfg = config["raw_store"]
    store = RawStore(
        PROJECT_ROOT / "data" / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    registry = default_registry()
    snaps = list((PROJECT_ROOT / "data" / "snapshots" / "partners").glob("*.json"))
    assert snaps
    for path in snaps:
        result = reconstruct(path, store, config, registry)
        assert result.match, result.detail


def test_reconstruct_script_no_snapshots_exits_1(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    (data_root / "snapshots" / "partners").mkdir(parents=True)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--no-check-manifest",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "no acquired snapshots" in result.stdout


def test_reconstruct_script_no_snapshots_with_manifest_exits_1(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    partners = data_root / "snapshots" / "partners"
    partners.mkdir(parents=True)
    snap = partners / "PARTNERS-SAU-TEST-2026-09-04.json"
    snap.write_text("{}", encoding="utf-8")
    manifest = {
        "manifest_version": "1.0",
        "generated_on": "2026-09-04",
        "policy": "test",
        "files": [
            {
                "path": f"data/snapshots/partners/{snap.name}",
                "sha256": hashlib.sha256(snap.read_bytes()).hexdigest(),
                "bytes": snap.stat().st_size,
            }
        ],
    }
    (data_root / "manifests").mkdir(parents=True)
    (data_root / "manifests" / "snapshot_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_reconstruct_missing_manifest_row_exits_2(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    partners = data_root / "snapshots" / "partners"
    partners.mkdir(parents=True)
    snap = partners / "PARTNERS-SAU-TEST-2026-09-04.json"
    snap.write_text('{"kind":"partners"}', encoding="utf-8")
    (data_root / "manifests").mkdir(parents=True)
    (data_root / "manifests" / "snapshot_manifest.json").write_text(
        json.dumps({"files": []}), encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_reconstruct_hash_mismatch_exits_1(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    partners = data_root / "snapshots" / "partners"
    partners.mkdir(parents=True)
    snap = partners / "PARTNERS-SAU-TEST-2026-09-04.json"
    snap.write_text('{"kind":"partners"}', encoding="utf-8")
    rel = f"data/snapshots/partners/{snap.name}"
    manifest = {
        "files": [
            {
                "path": rel,
                "sha256": "0" * 64,
                "bytes": snap.stat().st_size,
            }
        ]
    }
    (data_root / "manifests").mkdir(parents=True)
    (data_root / "manifests" / "snapshot_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1


def test_manifest_lists_gz_payload_paths() -> None:
    manifest = json.loads(
        (PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    gz_paths = {
        row["path"]
        for row in manifest["files"]
        if "page-" in row["path"] and row["path"].endswith(".gz")
    }
    raw_gz = {
        str(p.relative_to(PROJECT_ROOT))
        for p in (PROJECT_ROOT / "data" / "raw").rglob("page-*.payload.*.gz")
    }
    assert raw_gz <= gz_paths or not raw_gz


def _test_config_with_fixture() -> dict:
    config = acquisition_sources_config()
    sources = dict(config["sources"])
    sources["TEST-FIXTURE"] = {
        **config["sources"]["wits_trade"],
        "source_id": "TEST-FIXTURE",
    }
    return {**config, "sources": sources}


def _seed_complete_universe(tmp_path: Path) -> Path:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.contracts import ProductScope, QueryContract, Stage
    from ior_mvp.acquisition.snapshots import build_universe_snapshot

    config = _test_config_with_fixture()
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
    payload = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_rows.json"
    ).read_bytes()
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T100000Z",
        payload=payload,
        source_config=source_cfg,
    )
    record = build_universe_snapshot(
        store, config, registry, source_id="TEST-FIXTURE"
    )
    return write_snapshot(record, tmp_path, allow_test_double=True)


def test_selection_changed_after_newer_run(tmp_path: Path) -> None:
    from ior_mvp.acquisition.contracts import ProductScope, QueryContract, Stage

    config = _test_config_with_fixture()
    raw_cfg = config["raw_store"]
    store = RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    path = _seed_complete_universe(tmp_path)
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
    source_cfg = {**config["sources"]["wits_trade"], "source_id": "TEST-FIXTURE"}
    payload = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_rows.json"
    ).read_bytes()
    seed_unit(
        store,
        contract=contract,
        run_id="20260904T110000Z",
        payload=payload,
        source_config=source_cfg,
    )
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    registry = ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})
    result = reconstruct(path, store, config, registry)
    assert not result.match
    assert result.detail.get("reason") == "SELECTION_CHANGED"


def test_plan_units_tariff_is_one_period_free_unit() -> None:
    """DD-5/DD-19: TARIFF is one contract for the whole tree and takes no --years."""
    config = acquisition_sources_config()
    units = plan_units(
        Stage.TARIFF,
        source_id="zatca_tariff",
        years=(),
        flows=(),
        candidates=None,
        config=config,
    )
    assert len(units) == 1
    (unit,) = units
    assert unit.stage is Stage.TARIFF
    assert unit.product_scope is ProductScope.ALL_TARIFF_LINES
    assert unit.product_codes == ("ALL",)
    assert unit.periods == ()
    assert unit_key(unit) == ("ALL_TARIFF_LINES",)
    with_years = plan_units(
        Stage.TARIFF,
        source_id="zatca_tariff",
        years=(2024,),
        flows=(),
        candidates=None,
        config=config,
    )
    assert with_years == units
    source_cfg = {**config["sources"]["zatca_tariff"], "source_id": "zatca_tariff"}
    assert (
        plan_requests(
            Stage.TARIFF,
            years=(),
            flows=(),
            candidates=None,
            source_config=source_cfg,
        )
        == 1
    )


def _manifest_for_snapshot(data_root: Path, snap_path: Path, refs: list[dict]) -> None:
    rel_snap = f"data/{snap_path.relative_to(data_root).as_posix()}"
    files = [
        {
            "path": rel_snap,
            "sha256": hashlib.sha256(snap_path.read_bytes()).hexdigest(),
            "bytes": snap_path.stat().st_size,
        }
    ]
    for ref in refs:
        abs_ref = data_root.parent / ref["path"]
        files.append(
            {
                "path": ref["path"],
                "sha256": hashlib.sha256(abs_ref.read_bytes()).hexdigest(),
                "bytes": abs_ref.stat().st_size,
            }
        )
    manifest_dir = data_root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "snapshot_manifest.json").write_text(
        json.dumps({"files": files}), encoding="utf-8"
    )


def _copy_partners_temp_root(data_root: Path) -> tuple[Path, dict]:
    import shutil

    snap_src = (
        PROJECT_ROOT / "data" / "snapshots" / "partners" / "PARTNERS-SAU-WITS-TRADE-2026-09-03.json"
    )
    partners_dir = data_root / "snapshots" / "partners"
    partners_dir.mkdir(parents=True)
    shutil.copy(snap_src, partners_dir / snap_src.name)
    snap_path = partners_dir / snap_src.name
    record = json.loads(snap_path.read_text(encoding="utf-8"))
    copied_hashes: set[tuple[str, str]] = set()
    for ref in record["raw_artifact_refs"]:
        hash_key = (ref["source_id"], ref["query_hash"])
        if hash_key in copied_hashes:
            continue
        copied_hashes.add(hash_key)
        hash_dir = (
            PROJECT_ROOT / "data" / "raw" / ref["source_id"] / ref["query_hash"]
        )
        dst_hash = (
            data_root.parent / "data" / "raw" / ref["source_id"] / ref["query_hash"]
        )
        shutil.copytree(hash_dir, dst_hash)
    return snap_path, record


def test_reconstruct_script_matching_temp_root_exits_0(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    snap_path, record = _copy_partners_temp_root(data_root)
    _manifest_for_snapshot(data_root, snap_path, record["raw_artifact_refs"])
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RECONSTRUCTION PASS" in result.stdout


def test_reconstruct_script_tampered_payload_exits_nonzero(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    snap_path, record = _copy_partners_temp_root(data_root)
    _manifest_for_snapshot(data_root, snap_path, record["raw_artifact_refs"])
    gz_ref = next(
        ref for ref in record["raw_artifact_refs"] if ref["artifact"].startswith("page-")
    )
    gz_path = data_root.parent / gz_ref["path"]
    payload = bytearray(gz_path.read_bytes())
    payload[0] ^= 0x01
    gz_path.write_bytes(bytes(payload))
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_reconstruct_script_tampered_coverage_exits_nonzero(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    snap_path, record = _copy_partners_temp_root(data_root)
    _manifest_for_snapshot(data_root, snap_path, record["raw_artifact_refs"])
    cov_ref = next(
        ref for ref in record["raw_artifact_refs"] if ref["artifact"] == "coverage"
    )
    cov_path = data_root.parent / cov_ref["path"]
    payload = bytearray(cov_path.read_bytes())
    payload[-1] ^= 0x01
    cov_path.write_bytes(bytes(payload))
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_reconstruct_script_tampered_snapshot_exits_nonzero(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    snap_path, record = _copy_partners_temp_root(data_root)
    _manifest_for_snapshot(data_root, snap_path, record["raw_artifact_refs"])
    snap_payload = bytearray(snap_path.read_bytes())
    snap_payload[-1] ^= 0x01
    snap_path.write_bytes(bytes(snap_payload))
    result = subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={"PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_same_run_id_incomplete_returns_coverage_incomplete(tmp_path: Path) -> None:
    config = _test_config_with_fixture()
    raw_cfg = config["raw_store"]
    store = RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    path = _seed_complete_universe(tmp_path)
    record = json.loads(path.read_text(encoding="utf-8"))
    unit = record["coverage"]["units"][0]
    cov_path = (
        tmp_path
        / "raw"
        / "TEST-FIXTURE"
        / unit["query_hash"]
        / unit["selected_run_id"]
        / "coverage.json"
    )
    cov = json.loads(cov_path.read_text(encoding="utf-8"))
    cov["status"] = "INCOMPLETE"
    cov["stop_reason"] = "HTTP_ERROR"
    cov_path.write_text(json.dumps(cov), encoding="utf-8")
    registry = ConnectorRegistry({"TEST-FIXTURE": DoubleConnector})
    result = reconstruct(path, store, config, registry)
    assert not result.match
    assert result.detail.get("reason") == "COVERAGE_INCOMPLETE"
