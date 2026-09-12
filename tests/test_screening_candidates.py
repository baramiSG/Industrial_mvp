"""Stage-two candidate-list emission."""

from __future__ import annotations

import json
import socket

import pytest
from ior_mvp.acquisition.pipeline import load_candidate_list
from ior_mvp.config import PROJECT_ROOT


def _records():
    return [
        {
            "hs6": "721050",
            "screening_disposition": "CANDIDATE",
            "ledger": [{"rule_id": "R2", "execution": "FULL", "fired": True}],
        },
        {
            "hs6": "721049",
            "screening_disposition": "CANDIDATE",
            "ledger": [{"rule_id": "R2", "execution": "FULL", "fired": True}],
        },
        {
            "hs6": "390210",
            "screening_disposition": "NO_CANDIDATE",
            "ledger": [{"rule_id": "R2", "execution": "FULL", "fired": False}],
        },
    ]


def _emit(tmp_path, batch_size=10):
    from ior_mvp.screening.cli import emit_candidates

    return emit_candidates(
        universe_id="U1",
        records=_records(),
        inputs={"universe": {"path": "u.json", "sha256": "a" * 64}},
        batch_size=batch_size,
        root=tmp_path,
        recorded_on="2026-09-12",
    )


def test_emit_candidates_selects_r2_full_fired_only(tmp_path):
    payload = json.loads(_emit(tmp_path)[0].read_text())
    assert payload["hs6_codes"] == ["721049", "721050"]


def test_batches_lexicographic_and_hash_pinned_inputs(tmp_path):
    paths = _emit(tmp_path, batch_size=1)
    assert len(paths) == 2
    first = json.loads(paths[0].read_text())
    assert first["hs6_codes"] == ["721049"]
    assert len(first["sha256_of_hs6_codes"]) == 64
    assert first["inputs"]["universe"]["sha256"] == "a" * 64


def test_candidate_list_loadable_by_pipeline_load_candidate_list(tmp_path):
    candidate = load_candidate_list(_emit(tmp_path)[0])
    assert candidate.hs6_codes == ("721049", "721050")


def test_candidate_source_screening_cheap_rules_v1(tmp_path):
    payload = json.loads(_emit(tmp_path)[0].read_text())
    assert payload["candidate_source"] == "SCREENING_CHEAP_RULES_V1"


def test_screening_cli_main_exit_codes_and_no_socket(tmp_path, monkeypatch):
    from ior_mvp.screening import cli

    snapshot = tmp_path / "screening" / "snapshots" / "SCREENING-TEST"
    snapshot.mkdir(parents=True)

    def block_socket(*args, **kwargs):
        raise AssertionError("screening CLI must not open a socket")

    monkeypatch.setattr(socket, "socket", block_socket)
    monkeypatch.setattr(socket, "create_connection", block_socket)
    monkeypatch.setattr(
        cli,
        "validate_screening_snapshot_directory",
        lambda path, **kwargs: None,
    )
    assert cli.main(["validate", "--data-root", str(tmp_path)]) is None

    with pytest.raises(SystemExit) as missing:
        cli.main(["validate", "--data-root", str(tmp_path / "missing")])
    assert missing.value.code == 1

    with pytest.raises(SystemExit) as invalid:
        cli.main(["not-a-command"])
    assert invalid.value.code == 2


def test_makefile_pins_governed_screening_target_names():
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ("screen-candidates", "build-screening", "validate-screening"):
        assert f"\n{target}:" in makefile
    for obsolete in (
        "screening-emit-candidates",
        "screening-build",
        "screening-validate",
    ):
        assert f"\n{obsolete}:" not in makefile
