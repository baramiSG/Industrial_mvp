from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from acquisition_doubles import entity_snapshot_double
from ior_mvp.acquisition.contracts import canonical_dumps
from ior_mvp.acquisition.entities.rules import ENTITY_RULES_PATH, EntityResolutionError
from ior_mvp.acquisition.entities.store import (
    EntityBuildReport,
    SnapshotInput,
    build_entity_resolution,
)
from ior_mvp.config import PROJECT_ROOT


def _mention_payload(snapshot_id: str = "FIX-ENTITY-DOUBLE") -> dict:
    return {
        "schema_version": "1.0.0",
        "list_id": "test-double-mentions",
        "recorded_on": "2026-09-12",
        "recorded_by_seat": "TEST-DOUBLE",
        "consultation_summary_text": "TEST DOUBLE — NOT REAL EVIDENCE.",
        "mentions": [
            {
                "mention_id": "M-001",
                "source_kind": "PUBLIC_SNAPSHOT",
                "address": {
                    "snapshot_id": snapshot_id,
                    "json_pointer": "/domestic_capability/producer_evidence/0/producer",
                },
                "span_text": "Acme Company",
                "mention_kind": "PUBLISHER_NAME",
                "entity_type_observed": "COMPANY",
                "language": "en",
                "text_order": "logical",
                "subject_mention_id": None,
                "alias": None,
                "identifier": None,
                "statement": None,
                "designation_text": None,
            }
        ],
    }


def _build_entity_tree(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    data_root = tmp_path / "data"
    mention_path = data_root / "entities" / "mentions" / "test-double-mentions.json"
    mention_path.parent.mkdir(parents=True)
    mention_path.write_text(canonical_dumps(_mention_payload()), encoding="utf-8")
    rules_path = data_root / "config" / "entity_resolution.v1.yaml"
    rules_path.parent.mkdir(parents=True)
    shutil.copy2(ENTITY_RULES_PATH, rules_path)
    snapshot = entity_snapshot_double(
        producers=[{"producer": "Acme Company"}],
    )
    snapshot_path = data_root / "entity-inputs" / "FIX-ENTITY-DOUBLE.json"
    snapshot_path.parent.mkdir(parents=True)
    snapshot_path.write_text(canonical_dumps(snapshot), encoding="utf-8")

    def documents(_root: Path, *, allow_test_double: bool = False):
        assert allow_test_double
        return {}

    def snapshots(_root: Path):
        return {
            "FIX-ENTITY-DOUBLE": SnapshotInput.from_path(
                "FIX-ENTITY-DOUBLE", snapshot_path, snapshot
            )
        }

    report = build_entity_resolution(
        data_root,
        mention_list_id="test-double-mentions",
        rules_path=rules_path,
        document_loader=documents,
        snapshot_loader=snapshots,
        allow_test_double=True,
    )
    return data_root, mention_path, rules_path, Path(report.artifact_path)


def _manifest_entry(path: Path) -> dict:
    data_root = next(parent for parent in path.parents if parent.name == "data")
    return {
        "path": path.relative_to(data_root.parent).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }


def _run_reconstruct(data_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "scripts/reconstruct_snapshot.py",
            "--all",
            "--data-root",
            str(data_root),
        ],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )


def test_parser_build_entities_required_args() -> None:
    from ior_mvp.acquisition.cli import build_parser

    sub = next(
        action
        for action in build_parser()._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    parser = sub.choices["build-entities"]
    assert {
        action.dest: action.required
        for action in parser._actions
        if action.dest != "help"
    } == {"mention_list_id": True, "data_root": False}


def test_main_dispatch_build_entities_temp_root_exit_0_and_report(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from ior_mvp.acquisition import cli

    observed = {}

    def fake_build(data_root: Path, *, mention_list_id: str):
        observed.update(root=data_root, list_id=mention_list_id)
        return EntityBuildReport(
            "ENTITIES-2026-09-12-0123456789ab",
            str(data_root / "entities" / "resolution" / "artifact.json"),
            {"COMPANY": 1, "PLANT": 0, "LINE": 0, "LICENCE_HOLDER": 0},
            {
                "DETERMINISTIC_IDENTIFIER": 0,
                "EXACT_DOCUMENT_EVIDENCE": 1,
                "PROPOSED_PENDING_REVIEW": 0,
                "UNRESOLVED": 0,
            },
            {
                "DETERMINISTIC_IDENTIFIER": 0,
                "EXACT_DOCUMENT_EVIDENCE": 0,
                "PROPOSED_PENDING_REVIEW": 0,
                "UNRESOLVED": 0,
            },
            (),
        )

    monkeypatch.setattr(cli, "build_entity_resolution", fake_build)
    with pytest.raises(SystemExit) as exit_info:
        cli.main(
            [
                "build-entities",
                "--mention-list-id",
                "mentions-unit",
                "--data-root",
                str(tmp_path / "data"),
            ]
        )
    assert exit_info.value.code == 0
    assert observed == {"root": tmp_path / "data", "list_id": "mentions-unit"}
    assert '"artifact_id": "ENTITIES-2026-09-12-0123456789ab"' in capsys.readouterr().out


def test_build_entities_exit_3_on_refused_span_and_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from ior_mvp.acquisition import cli

    monkeypatch.setattr(
        cli,
        "build_entity_resolution",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            EntityResolutionError("span refused")
        ),
    )
    with pytest.raises(SystemExit) as exit_info:
        cli.main(
            [
                "build-entities",
                "--mention-list-id",
                "mentions-unit",
                "--data-root",
                str(tmp_path / "data"),
            ]
        )
    assert exit_info.value.code == 3
    assert "span refused" in capsys.readouterr().err
    assert not (tmp_path / "data").exists()


def test_build_entities_rejects_unsafe_list_id_before_io(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ior_mvp.acquisition import cli

    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "build_entity_resolution", fail_if_called)
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["build-entities", "--mention-list-id", "../unsafe"])
    assert exit_info.value.code == 2
    assert not called
    assert "list_id" in capsys.readouterr().err


def test_make_build_entities_requires_mention_list_id_and_argv() -> None:
    missing = subprocess.run(
        ["make", "build-entities", "UV_RUN=echo"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 2
    assert "MENTION_LIST_ID required" in missing.stderr
    present = subprocess.run(
        [
            "make",
            "build-entities",
            "UV_RUN=echo",
            "MENTION_LIST_ID=mentions-v1",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert present.returncode == 0
    assert (
        "python -m ior_mvp.acquisition build-entities --mention-list-id mentions-v1"
        in present.stdout
    )


def test_reconstruct_script_entities_temp_root_exit_0_and_three_pass_lines(
    tmp_path: Path,
) -> None:
    data_root, mention_path, _, artifact_path = _build_entity_tree(tmp_path)
    snapshot_path = data_root / "entity-inputs" / "FIX-ENTITY-DOUBLE.json"
    manifest = {
        "manifest_version": "1.0",
        "files": [
            _manifest_entry(path)
            for path in (mention_path, snapshot_path, artifact_path)
        ],
    }
    (data_root / "manifests").mkdir()
    (data_root / "manifests" / "snapshot_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    result = _run_reconstruct(data_root)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "CASE RECONSTRUCTION PASS (0 snapshots, 0 briefs)",
        "RECONSTRUCTION PASS (0 snapshots, 0 artifacts)",
        "DOCUMENT RECONSTRUCTION PASS (0 records, 0 artifacts)",
        "ENTITY RECONSTRUCTION PASS (1 artifacts, 1 links)",
    ]


def test_reconstruct_script_entity_missing_manifest_row_exit_2(
    tmp_path: Path,
) -> None:
    data_root, mention_path, _, artifact_path = _build_entity_tree(tmp_path)
    snapshot_path = data_root / "entity-inputs" / "FIX-ENTITY-DOUBLE.json"
    all_paths = (mention_path, snapshot_path, artifact_path)
    for missing in all_paths:
        manifest = {
            "manifest_version": "1.0",
            "files": [
                _manifest_entry(path) for path in all_paths if path != missing
            ],
        }
        manifest_path = data_root / "manifests" / "snapshot_manifest.json"
        manifest_path.parent.mkdir(exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = _run_reconstruct(data_root)
        assert result.returncode == 2
        assert "manifest row missing" in result.stdout
        assert "RECONSTRUCTION PASS" not in result.stdout


@pytest.mark.parametrize("tamper", ["artifact", "mention_list", "rules"])
def test_reconstruct_script_entity_tamper_exit_1_prints_no_pass_line(
    tmp_path: Path, tamper: str
) -> None:
    data_root, mention_path, rules_path, artifact_path = _build_entity_tree(tmp_path)
    snapshot_path = data_root / "entity-inputs" / "FIX-ENTITY-DOUBLE.json"
    manifest = {
        "manifest_version": "1.0",
        "files": [
            _manifest_entry(path)
            for path in (mention_path, snapshot_path, artifact_path)
        ],
    }
    (data_root / "manifests").mkdir()
    manifest_path = data_root / "manifests" / "snapshot_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    target = {
        "artifact": artifact_path,
        "mention_list": mention_path,
        "rules": rules_path,
    }[tamper]
    target.write_bytes(target.read_bytes() + b" ")
    if tamper == "artifact":
        manifest["files"] = [
            _manifest_entry(path)
            for path in (mention_path, snapshot_path, artifact_path)
        ]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = _run_reconstruct(data_root)
    assert result.returncode == 1
    assert "RECONSTRUCTION PASS" not in result.stdout


def test_build_manifests_enumerates_entities_and_hashes_rules_config() -> None:
    source = (PROJECT_ROOT / "scripts" / "build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert '"entities"' in source
    assert 'ROOT / "config" / "entity_resolution.v1.yaml"' in source


def test_repository_entity_artifacts_loader_validates_partition_and_cache_clear(
    tmp_path: Path,
) -> None:
    data_root, _, _, artifact_path = _build_entity_tree(tmp_path)
    from ior_mvp.acquisition import repository

    records = repository.entity_resolution_artifacts(
        data_root=data_root, allow_test_double=True
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert records == {artifact["artifact_id"]: artifact}
    renamed = artifact_path.with_name("wrong.json")
    artifact_path.rename(renamed)
    with pytest.raises(ValueError, match="file name"):
        repository.entity_resolution_artifacts(
            data_root=data_root, allow_test_double=True
        )
    repository.clear_acquisition_caches()
