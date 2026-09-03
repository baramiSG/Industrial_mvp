from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

import ior_mvp.config as config_module
from ior_mvp.app import app
from ior_mvp.config import (
    AuthorityConfigurationError,
    PROJECT_ROOT,
)
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import (
    build_dossier,
    render_dossier_html,
)
from ior_mvp.genui import build_ui_manifest


client = TestClient(app)


def _yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _expected_authority() -> dict:
    manifest = json.loads(
        (
            PROJECT_ROOT
            / "docs"
            / "authority"
            / "authority_hashes.json"
        ).read_text(encoding="utf-8")
    )
    methodology = next(
        item
        for item in manifest["files"]
        if item["path"].endswith(".docx")
    )
    thresholds = _yaml(
        PROJECT_ROOT / "config" / "thresholds.v1.yaml"
    )
    sectors = _yaml(
        PROJECT_ROOT / "config" / "sector_profiles.v1.yaml"
    )
    policy = _yaml(
        PROJECT_ROOT / "config" / "evidence_policy.v1.yaml"
    )
    ui_strings = _yaml(
        PROJECT_ROOT / "config" / "ui_strings.v1.yaml"
    )
    decision_narratives = _yaml(
        PROJECT_ROOT / "config" / "decision_narratives.v1.yaml"
    )
    project = _yaml(
        PROJECT_ROOT / "config" / "project.yaml"
    )
    return {
        "methodology": {
            "file": methodology["path"],
            "sha256": methodology["sha256"],
            "sha256_prefix": methodology["sha256"][:12],
        },
        "config_versions": {
            "thresholds": thresholds["metadata"]["version"],
            "sector_profiles": sectors["metadata"]["version"],
            "evidence_policy": policy["metadata"]["version"],
            "ui_strings": ui_strings["metadata"]["version"],
            "decision_narratives": decision_narratives[
                "metadata"
            ]["version"],
        },
        "project_version": project["project"]["version"],
    }


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_every_detailed_analysis_exposes_source_derived_authority(
    opportunity_id: str,
    mode: str,
) -> None:
    result = analyze(opportunity_id, mode)
    response = client.get(
        f"/api/opportunities/{opportunity_id}?mode={mode}"
    )

    assert result["authority"] == _expected_authority()
    assert response.status_code == 200
    assert response.json()["authority"] == _expected_authority()
    assert result["authority"]["config_versions"]["thresholds"] == "1.2.0"
    assert result["authority"]["config_versions"]["ui_strings"] == "1.1.0"
    assert result["authority"]["config_versions"][
        "decision_narratives"
    ] == "1.0.0"
    assert len(
        result["authority"]["methodology"]["sha256_prefix"]
    ) == 12
    if mode == "public":
        assert result["integrity"][
            "scenario_reconciliation"
        ] is None


@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_integrity_banner_props_receive_the_same_authority(
    mode: str,
) -> None:
    analysis = analyze("SAU-H0-721049", mode)
    manifest = build_ui_manifest(analysis)
    banner = next(
        component
        for component in manifest["components"]
        if component["type"] == "integrity_banner"
    )

    assert banner["props"]["authority"] == analysis["authority"]


def test_authority_summary_fails_loudly_without_methodology_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = tmp_path / "authority_hashes.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "1.0",
                "generated_on": "2026-09-02",
                "files": [
                    {
                        "path": "config/evidence_policy.v1.yaml",
                        "sha256": "0" * 64,
                        "bytes": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        config_module,
        "AUTHORITY_HASHES_PATH",
        manifest,
    )
    config_module.clear_config_caches()
    try:
        with pytest.raises(
            AuthorityConfigurationError,
            match="exactly one methodology DOCX",
        ):
            config_module.authority_summary()
    finally:
        config_module.clear_config_caches()


@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_dossier_json_and_html_project_the_same_authority(
    mode: str,
) -> None:
    analysis = analyze("SAU-H0-721049", mode)
    dossier = build_dossier(analysis)
    authority = _expected_authority()

    assert dossier["evidence_summary"]["authority"] == authority
    rendered = render_dossier_html(dossier)
    assert authority["methodology"]["file"] in rendered
    assert authority["methodology"]["sha256"] in rendered
    assert "Project" in rendered
    assert authority["project_version"] in rendered
    for label, key in (
        ("Thresholds", "thresholds"),
        ("Sector profiles", "sector_profiles"),
        ("Evidence policy", "evidence_policy"),
        ("UI strings", "ui_strings"),
    ):
        assert label in rendered
        assert authority["config_versions"][key] in rendered
