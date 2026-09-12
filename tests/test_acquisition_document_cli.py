"""Document CLI, Makefile and reconstruct script tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ior_mvp.acquisition.cli import build_parser
from ior_mvp.config import PROJECT_ROOT


def test_parser_acquire_documents_required_args_no_years_no_flows() -> None:
    parser = build_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    docs = sub.choices["acquire-documents"]
    for dest in ("source", "list_id", "max_requests"):
        action = next(a for a in docs._actions if a.dest == dest)
        assert action.required and action.default is None
    assert not any(a.dest == "years" for a in docs._actions)
    assert not any(a.dest == "flows" for a in docs._actions)


def test_parser_build_documents_required_args() -> None:
    parser = build_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    build = sub.choices["build-documents"]
    for dest in ("source", "list_id"):
        action = next(a for a in build._actions if a.dest == dest)
        assert action.required and action.default is None


def test_document_cli_data_root_resolves_raw_store_below_data_root(
    tmp_path: Path,
) -> None:
    from ior_mvp.acquisition import cli

    data_root = tmp_path / "data"
    assert cli._data_root(
        argparse.Namespace(command="build-documents", data_root=str(data_root))
    ) == data_root / "raw"


def test_offline_guard_exit_4_for_acquire_documents(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("IOR_ACQUISITION_LIVE", None)
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ior_mvp.acquisition",
            "acquire-documents",
            "--source",
            "producer_unicoil",
            "--list-id",
            "producer_unicoil-v1",
            "--max-requests",
            "1",
            "--data-root",
            str(tmp_path / "raw"),
        ],
        env=env,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 4


@pytest.mark.parametrize("command", ("acquire-documents", "build-documents"))
def test_document_cli_rejects_unsafe_list_id_before_dependencies(
    monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    from ior_mvp.acquisition import cli

    monkeypatch.setattr(
        cli,
        "_deps",
        lambda *args, **kwargs: pytest.fail("_deps must not run for an invalid list_id"),
    )
    argv = [
        command,
        "--source",
        "producer_unicoil",
        "--list-id",
        "../evil",
    ]
    if command == "acquire-documents":
        argv.extend(("--max-requests", "1"))

    with pytest.raises(SystemExit) as exc_info:
        cli.main(argv)
    assert exc_info.value.code == 2


def test_main_dispatch_acquire_documents_with_fake_deps(tmp_path: Path, monkeypatch) -> None:
    from dataclasses import replace

    from ior_mvp.acquisition import cli, pipeline
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.contracts import Stage
    from tests.acquisition_doubles import FakeTransport, pre_observation_document_source_config

    import json

    from tests.acquisition_doubles import document_list_payload

    source_id = "producer_unicoil"
    cfg = pre_observation_document_source_config(
        source_id, authority="TEST", evidence_class="C"
    )
    config = {"metadata": {"version": "1.2.0"}, "sources": {source_id: cfg}}
    from ior_mvp.acquisition.raw_store import RawStore

    data_root = tmp_path / "data"
    store = RawStore(data_root / "raw", max_artifact_bytes=1024 * 1024, max_store_bytes=1024 * 1024)
    list_path = data_root / "documents" / source_id / "lists" / f"{source_id}-v1.json"
    list_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.write_text(
        json.dumps(document_list_payload(source_id, entries=[])), encoding="utf-8"
    )
    from ior_mvp.acquisition.connectors.documents import ProducerUnicoilConnector

    deps = pipeline.PipelineDeps(
        config,
        store,
        FakeTransport({}, []),
        ConnectorRegistry({source_id: ProducerUnicoilConnector}),
        "20260912T120000Z",
        {},
        lambda _: None,
    )
    monkeypatch.setattr(cli, "_deps", lambda args, explicit_live: replace(deps, run_id="20260912T120000Z"))
    with pytest.raises(SystemExit) as exited:
        cli.main([
            "acquire-documents",
            "--source",
            source_id,
            "--list-id",
            f"{source_id}-v1",
            "--max-requests",
            "1",
            "--data-root",
            str(data_root / "raw"),
        ])
    assert exited.value.code == 3


def test_main_dispatch_build_documents_temp_root(tmp_path: Path, monkeypatch, capsys) -> None:
    from ior_mvp.acquisition import cli, pipeline
    from ior_mvp.acquisition.raw_store import TEST_FIXTURE_SOURCE
    from tests.test_acquisition_document_store import FixtureDocumentConnector, _acquire_fixture

    config, store, doc_store, record, _ = _acquire_fixture(tmp_path)
    doc_store.write_record(record, allow_test_double=True)
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    from tests.acquisition_doubles import FakeTransport

    deps = pipeline.PipelineDeps(
        config,
        store,
        FakeTransport({}, []),
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        "20260912T120000Z",
        {},
        lambda _: None,
    )
    monkeypatch.setattr(cli, "_deps", lambda args, explicit_live: deps)
    with pytest.raises(SystemExit) as exited:
        cli.main([
            "build-documents",
            "--source",
            TEST_FIXTURE_SOURCE,
            "--list-id",
            "test-fixture-v1",
            "--data-root",
            str(tmp_path / "data"),
        ])
    assert exited.value.code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["already_stored"]


def test_make_document_targets_enforce_operator_arguments() -> None:
    env = {**os.environ, "IOR_ACQUISITION_LIVE": "1"}
    env.pop("CI", None)
    values = {"SOURCE": "producer_unicoil", "LIST_ID": "producer_unicoil-v1", "MAX_REQUESTS": "2"}

    def invoke(changes: dict) -> subprocess.CompletedProcess[str]:
        assignments = {**values, **changes}
        return subprocess.run(
            [
                "make",
                "--no-print-directory",
                "acquire-documents",
                "UV_RUN=echo",
                *[f"{key}={value}" for key, value in assignments.items()],
            ],
            env=env,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

    good = invoke({})
    assert good.returncode == 0, good.stdout + good.stderr
    argv = good.stdout.splitlines()[-1].split()
    assert argv == [
        "python", "-m", "ior_mvp.acquisition", "acquire-documents",
        "--source", "producer_unicoil", "--list-id", "producer_unicoil-v1", "--max-requests", "2",
    ]
    for changes, message in [
        ({"IOR_ACQUISITION_LIVE": ""}, "IOR_ACQUISITION_LIVE=1 required"),
        ({"CI": "1"}, "CI may not acquire"),
        ({"SOURCE": ""}, "SOURCE required"),
        ({"LIST_ID": ""}, "LIST_ID required"),
        ({"MAX_REQUESTS": ""}, "MAX_REQUESTS required"),
    ]:
        refused = invoke(changes)
        assert refused.returncode == 2 and message in refused.stderr


def test_make_build_documents_argv() -> None:
    result = subprocess.run(
        [
            "make",
            "--no-print-directory",
            "build-documents",
            "UV_RUN=echo",
            "SOURCE=producer_unicoil",
            "LIST_ID=producer_unicoil-v1",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.splitlines()[-1].split() == [
        "python", "-m", "ior_mvp.acquisition", "build-documents",
        "--source", "producer_unicoil", "--list-id", "producer_unicoil-v1",
    ]


def _document_reconstruct_script(tmp_path: Path, *, tamper: str | None = None) -> subprocess.CompletedProcess[str]:
    from tests.test_acquisition_document_store import FixtureDocumentConnector, _acquire_fixture

    data_root = tmp_path / "data"
    config, store, doc_store, record, list_path = _acquire_fixture(tmp_path)
    record_path = doc_store.write_record(record, allow_test_double=True)
    rel_record = record_path.relative_to(data_root).as_posix()
    rel_list = list_path.relative_to(data_root).as_posix()
    payload_path = next(store.root.rglob("page-*.gz"))
    rel_payload = payload_path.relative_to(data_root).as_posix()
    manifest = {
        "manifest_version": "1.0",
        "generated_on": "2026-09-12",
        "policy": "test",
        "files": [
            {"path": f"data/{rel_record}", "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(), "bytes": record_path.stat().st_size},
            {"path": f"data/{rel_list}", "sha256": hashlib.sha256(list_path.read_bytes()).hexdigest(), "bytes": list_path.stat().st_size},
            {"path": f"data/{rel_payload}", "sha256": hashlib.sha256(payload_path.read_bytes()).hexdigest(), "bytes": payload_path.stat().st_size},
        ],
    }
    (data_root / "manifests").mkdir(parents=True)
    (data_root / "manifests" / "snapshot_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    if tamper == "record":
        tampered = json.loads(record_path.read_text(encoding="utf-8"))
        tampered["line_count"] += 1
        record_path.write_text(json.dumps(tampered), encoding="utf-8")
    elif tamper == "payload":
        data = bytearray(payload_path.read_bytes())
        data[-1] ^= 1
        payload_path.write_bytes(data)
    elif tamper == "list":
        tampered = json.loads(list_path.read_text(encoding="utf-8"))
        tampered["consultation_summary_text"] = "changed"
        list_path.write_text(json.dumps(tampered), encoding="utf-8")
    from ior_mvp.acquisition.source_config import acquisition_sources_config
    from ior_mvp.acquisition.raw_store import TEST_FIXTURE_SOURCE
    from tests.test_acquisition_document_store import _test_source_config

    injected = {
        **acquisition_sources_config(),
        "sources": {
            **acquisition_sources_config()["sources"],
            TEST_FIXTURE_SOURCE: _test_source_config(),
        },
    }
    script = """
import json, runpy, sys
from ior_mvp.acquisition import source_config
config = json.loads(sys.argv[1])
source_config.acquisition_sources_config = lambda: config
source_config.acquisition_sources_config.cache_clear = lambda: None
sys.argv = ['scripts/reconstruct_snapshot.py', '--all', '--data-root', sys.argv[2]]
runpy.run_path('scripts/reconstruct_snapshot.py', run_name='__main__')
"""
    return subprocess.run(
        [sys.executable, "-c", script, json.dumps(injected), str(data_root)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )


def test_reconstruct_script_documents_temp_root_exit_0_and_messages(tmp_path: Path) -> None:
    result = _document_reconstruct_script(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DOCUMENT RECONSTRUCTION PASS (1 records, 1 artifacts)" in result.stdout
    assert "RECONSTRUCTION PASS (0 snapshots, 0 artifacts)" in result.stdout


def test_reconstruct_script_document_missing_manifest_row_exit_2(tmp_path: Path) -> None:
    _document_reconstruct_script(tmp_path)
    data_root = tmp_path / "data"
    record_path = next((data_root / "documents").rglob("records/*.json"))
    for missing in ("record", "list", "payload"):
        root = tmp_path / f"missing-{missing}"
        if root.exists():
            import shutil
            shutil.rmtree(root)
        root.mkdir()
        import shutil
        shutil.copytree(data_root, root / "data", dirs_exist_ok=True)
        manifest_path = root / "data" / "manifests" / "snapshot_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if missing == "record":
            manifest["files"] = [f for f in manifest["files"] if not f["path"].endswith(record_path.name)]
        elif missing == "list":
            manifest["files"] = [f for f in manifest["files"] if "lists" not in f["path"]]
        else:
            manifest["files"] = [f for f in manifest["files"] if "payload" not in f["path"]]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        from ior_mvp.acquisition.source_config import acquisition_sources_config
        from ior_mvp.acquisition.raw_store import TEST_FIXTURE_SOURCE
        from tests.test_acquisition_document_store import _test_source_config

        injected = {
            **acquisition_sources_config(),
            "sources": {
                **acquisition_sources_config()["sources"],
                TEST_FIXTURE_SOURCE: _test_source_config(),
            },
        }
        script = """
import json, runpy, sys
from ior_mvp.acquisition import source_config
config = json.loads(sys.argv[1])
source_config.acquisition_sources_config = lambda: config
source_config.acquisition_sources_config.cache_clear = lambda: None
sys.argv = ['scripts/reconstruct_snapshot.py', '--all', '--data-root', sys.argv[2]]
runpy.run_path('scripts/reconstruct_snapshot.py', run_name='__main__')
"""
        result = subprocess.run(
            [sys.executable, "-c", script, json.dumps(injected), str(root / "data")],
            cwd=PROJECT_ROOT,
            env={**os.environ, "PYTHONPATH": "src"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2, result.stdout + result.stderr


@pytest.mark.parametrize("tamper", ["record", "payload", "list"])
def test_reconstruct_script_document_tamper_exit_1(tmp_path: Path, tamper: str) -> None:
    result = _document_reconstruct_script(tmp_path, tamper=tamper)
    assert result.returncode == 1
    assert "RECONSTRUCTION PASS" not in result.stdout


def test_build_manifests_enumerates_documents(tmp_path: Path, monkeypatch) -> None:
    import scripts.build_manifests as bm

    doc = tmp_path / "data" / "documents" / "producer_unicoil" / "lists" / "x.json"
    doc.parent.mkdir(parents=True)
    doc.write_text("{}", encoding="utf-8")
    (tmp_path / "data" / "manifests").mkdir(parents=True)
    (tmp_path / "docs" / "authority").mkdir(parents=True)
    monkeypatch.setattr(bm, "ROOT", tmp_path)
    bm.main()
    manifest = json.loads((tmp_path / "data" / "manifests" / "snapshot_manifest.json").read_text())
    paths = {row["path"] for row in manifest["files"]}
    assert "data/documents/producer_unicoil/lists/x.json" in paths
