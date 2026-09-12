"""Screening snapshot identity, validation, and reconstruction."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ior_mvp.screening.inputs import ScreeningInputs


def _inputs(universe=None):
    return ScreeningInputs(
        universe=universe,
        partners=None,
        tariff=None,
        entities=None,
        family_links={
            "schema_version": "1.0.0",
            "list_id": "plant-family-links-v1",
            "recorded_on": "2026-09-12",
            "entries": [],
        },
        inputs_block={
            "universe_snapshots": [],
            "partner_snapshots": [],
            "tariff_snapshots": [],
            "entity_artifacts": [],
            "plant_family_links": [],
            "configs": [],
        },
        unavailable_reasons=("LICENSE_UNRECORDED",) if universe is None else (),
    )


def _record(universe=None):
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import build_screening_snapshot

    return build_screening_snapshot(_inputs(universe), screening_config())


def _available_universe(codes=("390210", "721049")):
    rows = []
    for year in (2021, 2022, 2023, 2024):
        for flow in ("imports", "exports"):
            for code in codes:
                rows.append(
                    {
                        "year": year,
                        "flow": flow,
                        "hs6": code,
                        "trade_value": 1_000_000,
                        "net_weight": 1_000_000,
                        "hs_revision": "H6",
                        "source_evidence_id": f"E-{year}-{flow}-{code}",
                    }
                )
    return {
        "snapshot_id": "U-AVAILABLE",
        "as_of_date": "2026-09-12",
        "source_id": "un_comtrade",
        "flows": ["imports", "exports"],
        "periods": ["2021", "2022", "2023", "2024"],
        "coverage": {"units": []},
        "rows": rows,
        "evidence": [],
    }


def test_snapshot_id_scheme_from_inputs_hash():
    from ior_mvp.screening.snapshot import snapshot_id

    value = snapshot_id({"a": 1}, "2026-09-12")
    assert value.startswith("SCREENING-SAU-2026-09-12-")
    assert len(value.rsplit("-", 1)[-1]) == 12


def _portable_inputs(repo_root: Path) -> ScreeningInputs:
    from ior_mvp.screening.inputs import _identity

    entity = repo_root / "data" / "entities" / "resolution" / "ENTITY.json"
    links = (
        repo_root
        / "data"
        / "screening"
        / "lists"
        / "plant-family-links-v1.json"
    )
    config = repo_root / "config" / "screening.v1.yaml"
    for path, content in (
        (entity, b'{"artifact_id":"ENTITY"}\n'),
        (links, b'{"list_id":"plant-family-links-v1"}\n'),
        (config, b"metadata:\n  version: 1.0.0\n"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return ScreeningInputs(
        universe=None,
        partners=None,
        tariff=None,
        entities=None,
        family_links={
            "schema_version": "1.0.0",
            "list_id": "plant-family-links-v1",
            "recorded_on": "2026-09-12",
            "entries": [],
        },
        inputs_block={
            "universe_snapshots": [],
            "partner_snapshots": [],
            "tariff_snapshots": [],
            "entity_artifacts": [
                _identity(entity, identity="ENTITY", repo_root=repo_root)
            ],
            "plant_family_links": [
                _identity(
                    links,
                    identity="plant-family-links-v1",
                    repo_root=repo_root,
                )
            ],
            "configs": [
                _identity(config, identity="1.0.0", repo_root=repo_root)
            ],
        },
        unavailable_reasons=("NO_UNIVERSE_SNAPSHOT",),
    )


def test_snapshot_build_records_manifest_key_paths_from_tmp_repo(tmp_path):
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import build_screening_snapshot

    record = build_screening_snapshot(
        _portable_inputs(tmp_path), screening_config()
    )
    paths = [
        item["path"]
        for group in record["inputs"].values()
        for item in group
    ]
    assert paths == [
        "data/entities/resolution/ENTITY.json",
        "data/screening/lists/plant-family-links-v1.json",
        "config/screening.v1.yaml",
    ]
    assert all(not Path(path).is_absolute() for path in paths)
    assert all(".." not in Path(path).parts for path in paths)


def test_snapshot_identity_is_portable_across_absolute_repo_roots(tmp_path):
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import build_screening_snapshot

    first = build_screening_snapshot(
        _portable_inputs(tmp_path / "checkout-a"), screening_config()
    )
    second = build_screening_snapshot(
        _portable_inputs(tmp_path / "checkout-b"), screening_config()
    )
    assert first["inputs"] == second["inputs"]
    assert first["snapshot_id"] == second["snapshot_id"]


def test_identity_rejects_path_outside_repo_root(tmp_path):
    from ior_mvp.screening.inputs import _identity

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="outside repository root"):
        _identity(outside, identity="OUTSIDE", repo_root=repo_root)


def test_validator_rejects_absolute_screening_input_path():
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import (
        snapshot_id,
        validate_screening_snapshot,
    )

    record = _record()
    record["inputs"]["entity_artifacts"] = [
        {
            "path": "/machine-specific/data/entities/ENTITY.json",
            "sha256": "a" * 64,
            "id": "ENTITY",
        }
    ]
    record["snapshot_id"] = snapshot_id(
        record["inputs"], record["as_of_date"]
    )
    with pytest.raises(
        ValueError,
        match="screening input path must be repository-relative manifest key",
    ):
        validate_screening_snapshot(record, config=screening_config())


def test_reconstruct_script_rejects_absolute_screening_input_path(
    tmp_path, capsys
):
    from scripts import reconstruct_snapshot
    from ior_mvp.screening.snapshot import (
        snapshot_id,
        write_screening_snapshot,
    )

    data_root = tmp_path / "data"
    path = write_screening_snapshot(
        _record(), data_root / "screening" / "snapshots"
    )
    summary_path = path / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["inputs"]["entity_artifacts"] = [
        {
            "path": "/machine-specific/data/entities/ENTITY.json",
            "sha256": "a" * 64,
            "id": "ENTITY",
        }
    ]
    summary["snapshot_id"] = snapshot_id(
        summary["inputs"], summary["as_of_date"]
    )
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
        encoding="utf-8",
    )
    renamed = path.with_name(summary["snapshot_id"])
    path.rename(renamed)
    with pytest.raises(SystemExit) as stopped:
        reconstruct_snapshot._reconstruct_screening(
            data_root,
            check_manifest=False,
            manifest_rows={},
        )
    assert stopped.value.code == 1
    assert (
        "SCREENING RECONSTRUCTION FAIL: screening input path must be "
        "repository-relative manifest key"
    ) in capsys.readouterr().out


def test_canonical_bytes_and_write_once_conflict(tmp_path):
    from ior_mvp.screening.snapshot import write_screening_snapshot

    record = _record()
    path = write_screening_snapshot(record, tmp_path)
    assert path.is_dir()
    assert (path / "summary.json").read_bytes().endswith(b"\n")
    assert write_screening_snapshot(record, tmp_path) == path
    changed = copy.deepcopy(record)
    changed["quality_summary"] = "FAIL"
    with pytest.raises(ValueError, match="conflict"):
        write_screening_snapshot(changed, tmp_path)


def test_validator_negative_probes():
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import validate_screening_snapshot

    valid = _record()
    probes = []
    missing = copy.deepcopy(valid); missing.pop("counts"); probes.append(missing)
    extra = copy.deepcopy(valid); extra["extra"] = 1; probes.append(extra)
    synthetic = copy.deepcopy(valid); synthetic["synthetic_flag"] = True; probes.append(synthetic)
    formal = copy.deepcopy(valid); formal["state"] = "INVESTIGATE"; probes.append(formal)
    mismatch = copy.deepcopy(valid); mismatch["counts"]["dispositions"]["NO_CANDIDATE"] = 1; probes.append(mismatch)
    for probe in probes:
        with pytest.raises(ValueError):
            validate_screening_snapshot(probe, config=screening_config())


def test_unavailable_universe_snapshot_has_zero_records_and_typed_reason():
    record = _record()
    assert record["universe_status"]["status"] == "UNAVAILABLE"
    assert record["universe_status"]["reason_codes"] == ["LICENSE_UNRECORDED"]
    assert record["records"] == []


def test_partial_universe_status_when_flow_missing():
    universe = {
        "snapshot_id": "U1",
        "as_of_date": "2026-09-12",
        "source_id": "un_comtrade",
        "flows": ["imports"],
        "periods": ["2024"],
        "coverage": {"units": []},
        "rows": [
            {
                "year": 2024,
                "flow": "imports",
                "hs6": "721049",
                "trade_value": 1_000_000,
                "net_weight": 1_000_000,
                "hs_revision": "H6",
                "source_evidence_id": "E1",
            }
        ],
        "evidence": [],
    }
    assert _record(universe)["universe_status"]["status"] == "PARTIAL"


def test_partial_universe_status_when_configured_four_year_window_incomplete():
    rows = []
    for year in (2022, 2023, 2024):
        for flow in ("imports", "exports"):
            rows.append(
                {
                    "year": year,
                    "flow": flow,
                    "hs6": "721049",
                    "trade_value": 1_000_000,
                    "net_weight": 1_000_000,
                    "hs_revision": "H6",
                    "source_evidence_id": f"E-{year}-{flow}",
                }
            )
    universe = {
        "snapshot_id": "U-THREE-YEARS",
        "as_of_date": "2026-09-12",
        "source_id": "un_comtrade",
        "flows": ["imports", "exports"],
        "periods": ["2022", "2023", "2024"],
        "coverage": {"units": []},
        "rows": rows,
        "evidence": [],
    }
    assert _record(universe)["universe_status"]["status"] == "PARTIAL"


def test_reconstruct_match_and_inputs_changed(tmp_path):
    from ior_mvp.screening.snapshot import (
        reconstruct_screening_snapshot,
        write_screening_snapshot,
    )

    path = write_screening_snapshot(_record(), tmp_path / "screening" / "snapshots")
    assert reconstruct_screening_snapshot(path, tmp_path).match
    summary_path = path / "summary.json"
    changed = json.loads(summary_path.read_text())
    changed["snapshot_id"] = changed["snapshot_id"][:-1] + "0"
    summary_path.write_text(json.dumps(changed))
    assert not reconstruct_screening_snapshot(path, tmp_path).match


def test_screening_snapshot_directory_layout_and_shard_index(tmp_path):
    from ior_mvp.screening.snapshot import write_screening_snapshot

    path = write_screening_snapshot(
        _record(_available_universe()), tmp_path / "snapshots"
    )
    summary = json.loads((path / "summary.json").read_text())
    assert not (path.with_suffix(".json")).exists()
    assert "records" not in summary
    assert [row["hs2"] for row in summary["record_shards"]] == ["39", "72"]
    assert [row["path"] for row in summary["record_shards"]] == [
        "records/39.json",
        "records/72.json",
    ]
    assert (path / "records" / "39.json").is_file()
    assert (path / "records" / "72.json").is_file()


def test_screening_shard_sha256_and_record_counts_match_summary(tmp_path):
    from ior_mvp.screening.snapshot import write_screening_snapshot

    path = write_screening_snapshot(
        _record(_available_universe()), tmp_path / "snapshots"
    )
    summary = json.loads((path / "summary.json").read_text())
    for row in summary["record_shards"]:
        shard = path / row["path"]
        records = json.loads(shard.read_text())
        assert row["record_count"] == len(records)
        assert row["sha256"] == hashlib.sha256(shard.read_bytes()).hexdigest()


def test_screening_validator_rejects_missing_or_tampered_shard(tmp_path):
    from ior_mvp.screening.snapshot import (
        validate_screening_snapshot_directory,
        write_screening_snapshot,
    )
    from ior_mvp.screening.config import screening_config

    path = write_screening_snapshot(
        _record(_available_universe()), tmp_path / "snapshots"
    )
    shard = path / "records" / "39.json"
    original = shard.read_bytes()
    shard.unlink()
    with pytest.raises(ValueError, match="shard"):
        validate_screening_snapshot_directory(path, config=screening_config())
    shard.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="shard"):
        validate_screening_snapshot_directory(path, config=screening_config())


def test_screening_reconstruction_rebuilds_every_file_byte_exact(tmp_path):
    from ior_mvp.screening.snapshot import (
        reconstruct_screening_snapshot,
        write_screening_snapshot,
    )

    path = write_screening_snapshot(
        _record(_available_universe()), tmp_path / "snapshots"
    )
    assert reconstruct_screening_snapshot(path, tmp_path).match
    shard = path / "records" / "72.json"
    shard.write_bytes(shard.read_bytes() + b" ")
    result = reconstruct_screening_snapshot(path, tmp_path)
    assert not result.match
    assert "records/72.json" in (result.reason or "")


def test_screening_common_record_fields_are_omitted_from_records_and_restored_by_loader(
    tmp_path,
):
    from ior_mvp.screening.snapshot import (
        load_screening_snapshot_directory,
        write_screening_snapshot,
    )

    record = _record(_available_universe())
    path = write_screening_snapshot(record, tmp_path / "snapshots")
    summary = json.loads((path / "summary.json").read_text())
    assert summary["common_record_fields"] == {
        "rules_not_evaluated_at_screening": record["records"][0][
            "rules_not_evaluated_at_screening"
        ],
        "rules_not_evaluated_reason": record["records"][0][
            "rules_not_evaluated_reason"
        ],
    }
    stored = json.loads((path / "records" / "39.json").read_text())
    assert "rules_not_evaluated_at_screening" not in stored[0]
    assert "rules_not_evaluated_reason" not in stored[0]
    assert load_screening_snapshot_directory(path) == record


def test_screening_size_budgets_per_file_and_total(tmp_path):
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.snapshot import write_screening_snapshot

    path = write_screening_snapshot(
        _record(_available_universe()), tmp_path / "snapshots"
    )
    sizes = [item.stat().st_size for item in path.rglob("*") if item.is_file()]
    budgets = screening_config()["budgets"]
    assert max(sizes) <= budgets["max_governed_file_bytes"]
    assert sum(sizes) <= budgets["screening_snapshot_total_max_bytes"]
    assert "screening_snapshot_max_bytes" not in budgets
