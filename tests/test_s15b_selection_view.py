from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.case_selection_view import (
    CaseSelectionIntegrityError,
    build_case_selection_view,
    case_selection_view,
    clear_case_selection_view_cache,
)


def test_case_selection_view_projects_pinned_public_record() -> None:
    clear_case_selection_view_cache()
    payload = case_selection_view()

    assert payload["schema_version"] == "1.0.0"
    assert payload["source_boundary"] == "public"
    assert payload["synthetic_flag"] is False
    assert payload["selection_id"] == "CASE-SELECTION-S15-b96de36ff0ce"
    assert payload["rule_version"] == "S14-CS-1.1"
    assert payload["selection_reference"]["path"] == (
        "data/cases/selection/CASE-SELECTION-S15-b96de36ff0ce.json"
    )
    assert [row["profile"] for row in payload["profiles"]] == [
        "pharma_api",
        "fertilizers",
    ]
    assert [row["selected"] for row in payload["profiles"]] == [
        ["294110", "294120"],
        ["310430", "310510"],
    ]
    assert all(row["quota"] == 2 for row in payload["profiles"])
    assert payload["input_references"]["screening"]["snapshot_id"] == (
        "SCREENING-SAU-2026-09-12-9b6b22032fd8"
    )


def test_case_selection_endpoint_is_public_and_mode_independent() -> None:
    client = TestClient(app, raise_server_exceptions=False)

    public = client.get("/api/case-selection")
    simulated = client.get("/api/case-selection?mode=simulated")

    assert public.status_code == 200
    assert simulated.status_code == 200
    assert public.json() == simulated.json()
    assert public.json()["source_boundary"] == "public"
    assert public.json()["synthetic_flag"] is False


def _write_subject(tmp_path: Path, mutate: callable) -> tuple[Path, Path]:
    source = (
        Path(__file__).resolve().parents[1]
        / "data/cases/selection/CASE-SELECTION-S15-b96de36ff0ce.json"
    )
    record = json.loads(source.read_text(encoding="utf-8"))
    mutate(record)
    relative = Path("data/cases/selection/subject.json")
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    content = (json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    target.write_bytes(content)
    manifest = tmp_path / "snapshot_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": relative.as_posix(),
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "bytes": len(content),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return target, manifest


def test_case_selection_endpoint_returns_typed_integrity_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app_module = importlib.import_module("ior_mvp.app")

    def fail() -> dict:
        raise app_module.CaseSelectionIntegrityError("selection evidence is invalid")

    monkeypatch.setattr(app_module, "case_selection_view", fail)
    response = TestClient(app_module.app, raise_server_exceptions=False).get(
        "/api/case-selection"
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "CASE_SELECTION_INTEGRITY_ERROR",
            "message": "selection evidence is invalid",
        }
    }


def test_case_selection_view_rejects_wrong_selected_set(tmp_path: Path) -> None:
    selection, manifest = _write_subject(
        tmp_path,
        lambda record: record.__setitem__("selected_hs6", ["294110"]),
    )

    with pytest.raises(CaseSelectionIntegrityError, match="selected set"):
        build_case_selection_view(
            selection_path=selection,
            manifest_path=manifest,
            root=tmp_path,
        )


def test_case_selection_view_rejects_unsafe_input_reference(tmp_path: Path) -> None:
    def mutate(record: dict) -> None:
        record["inputs"]["terms"]["path"] = "/private/selection.json"

    selection, manifest = _write_subject(tmp_path, mutate)

    with pytest.raises(CaseSelectionIntegrityError, match="reference path"):
        build_case_selection_view(
            selection_path=selection,
            manifest_path=manifest,
            root=tmp_path,
        )


def test_case_selection_view_rejects_manifest_hash_mismatch(tmp_path: Path) -> None:
    selection, manifest = _write_subject(tmp_path, lambda record: None)
    selection.write_bytes(selection.read_bytes() + b" ")

    with pytest.raises(CaseSelectionIntegrityError, match="manifest hash"):
        build_case_selection_view(
            selection_path=selection,
            manifest_path=manifest,
            root=tmp_path,
        )


def test_s15b_dossier_adds_selection_reference_without_changing_old_cases() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    current = client.get("/api/opportunities/SAU-H6-294110/dossier?mode=public")
    old = client.get("/api/opportunities/SAU-H0-721049/dossier?mode=public")

    assert current.status_code == 200
    assert old.status_code == 200
    assert current.json()["dossier_version"] == "2.0.0"
    assert current.json()["evidence_summary"]["selection"] == {
        "selection_id": "CASE-SELECTION-S15-b96de36ff0ce",
        "rule_version": "S14-CS-1.1",
        "reference": (
            "data/cases/selection/CASE-SELECTION-S15-b96de36ff0ce.json"
        ),
        "profile": "pharma_api",
    }
    assert old.json()["dossier_version"] == "2.0.0"
    assert "selection" not in old.json()["evidence_summary"]


@pytest.mark.parametrize("locale", ["en", "ar"])
def test_s15b_dossier_html_renders_selection_reference(locale: str) -> None:
    response = TestClient(app, raise_server_exceptions=False).get(
        "/api/opportunities/SAU-H6-294110/dossier.html",
        params={"mode": "public", "locale": locale},
    )

    assert response.status_code == 200
    assert "CASE-SELECTION-S15-b96de36ff0ce" in response.text
    assert "S14-CS-1.1" in response.text
