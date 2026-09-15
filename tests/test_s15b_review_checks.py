from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.s15b_review_checks as review_checks
from scripts.s15b_review_checks import (
    APPROVED_EXACT,
    ReviewCheckError,
    build_inventory,
    compare_inventory,
    controls_match,
    target_binding_matches,
)


def test_materialization_inventory_includes_binary_and_records(tmp_path: Path) -> None:
    (tmp_path / "image.webp").write_bytes(b"RIFFbinary")
    (tmp_path / "record.md").write_text("record\n", encoding="utf-8")

    inventory = build_inventory(tmp_path, ["image.webp", "record.md"])

    assert [row["path"] for row in inventory] == ["image.webp", "record.md"]
    assert inventory[0]["bytes"] == 10
    assert inventory[1]["bytes"] == 7


def test_tree_compare_detects_blob_or_mode_transform(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    (expected / "tool.py").write_text("x = 1\n", encoding="utf-8")
    (actual / "tool.py").write_text("x = 1\n", encoding="utf-8")
    (actual / "tool.py").chmod(0o755)

    assert compare_inventory(expected, actual, ["tool.py"]) == [
        "mode mismatch: tool.py"
    ]


def test_compare_detects_binary_drift(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    expected.mkdir()
    actual.mkdir()
    (expected / "image.webp").write_bytes(b"RIFFa")
    (actual / "image.webp").write_bytes(b"RIFFb")

    assert compare_inventory(expected, actual, ["image.webp"]) == [
        "content mismatch: image.webp"
    ]


def test_target_binding_detects_index_or_ref_drift() -> None:
    expected = {"head": "a", "ref": "a", "index": "one"}

    assert not target_binding_matches(
        expected,
        {"head": "a", "ref": "b", "index": "one"},
    )
    assert not target_binding_matches(
        expected,
        {"head": "a", "ref": "a", "index": "two"},
    )


def test_controls_mismatch_is_refusal_without_configuration_writes() -> None:
    expected = {"hooks": "active", "signing": True, "filter": "unchanged"}

    assert not controls_match(
        expected,
        {"hooks": "disabled", "signing": True, "filter": "unchanged"},
    )


@pytest.mark.parametrize(
    "path",
    [
        "tests/test_authority_disclosure.py",
        "tests/test_browser_harness_contract.py",
    ],
)
def test_am3_contract_paths_are_admitted_by_scope_guard(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    assert path in APPROVED_EXACT
    monkeypatch.setattr(review_checks, "_changed_paths", lambda root: [path])

    assert review_checks._require_scope(Path("/candidate")) == [path]


@pytest.mark.parametrize(
    "path",
    [
        "tests/test_am3_unapproved_probe.py",
        "tests/test_authority_disclosure.py.bak",
        "tests/test_browser_harness_contract_extra.py",
    ],
)
def test_am3_scope_guard_rejects_unapproved_dirty_path(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    changed = [
        "tests/test_authority_disclosure.py",
        "tests/test_browser_harness_contract.py",
        path,
    ]
    monkeypatch.setattr(review_checks, "_changed_paths", lambda root: changed)

    with pytest.raises(ReviewCheckError, match="path outside approved scope"):
        review_checks._require_scope(Path("/candidate"))


def test_am3_identity_still_enforces_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    admitted = [
        "tests/test_authority_disclosure.py",
        "tests/test_browser_harness_contract.py",
    ]
    monkeypatch.setattr(review_checks, "_head", lambda root: "base")
    monkeypatch.setattr(
        review_checks,
        "_git",
        lambda root, *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=b"refs/heads/feature\n",
        ),
    )
    monkeypatch.setattr(review_checks, "_changed_paths", lambda root: admitted)
    monkeypatch.setattr(review_checks, "build_inventory", lambda root, paths: [])
    monkeypatch.setattr(
        review_checks,
        "_target_index_identity",
        lambda root: {"path": "index", "sha256": "c" * 64},
    )

    assert review_checks.check_identity(Path("/candidate"), "base")[
        "complete_paths"
    ] == admitted

    monkeypatch.setattr(
        review_checks,
        "_changed_paths",
        lambda root: [*admitted, "tests/test_am3_unapproved_probe.py"],
    )
    with pytest.raises(ReviewCheckError, match="path outside approved scope"):
        review_checks.check_identity(Path("/candidate"), "base")


def test_workspace_regions_match_each_settled_before_after_union() -> None:
    key = "en/desktop-1440x900/journey-c-steel-simulated-workspace.webp"
    coverage = {
        "matrices": [
            {
                "locale": "en",
                "viewport": "desktop-1440x900",
                "before": {
                    "workspaces": {
                        "journey-c-steel-simulated-workspace": {
                            "authority_rectangle": [332, 480, 1061, 516]
                        }
                    }
                },
                "after": {
                    "workspaces": {
                        "journey-c-steel-simulated-workspace": {
                            "authority_rectangle": [332, 480, 1061, 517]
                        }
                    }
                },
            }
        ]
    }
    exact = {"regions": {key: [[332, 480, 1061, 517]]}}
    before_only = {"regions": {key: [[332, 480, 1061, 516]]}}

    assert review_checks.workspace_region_problems(exact, coverage) == []
    assert review_checks.workspace_region_problems(
        before_only,
        coverage,
    ) == [f"workspace region mismatch: {key}"]


def test_identity_emits_canonical_candidate_and_complete_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = [
        "src/ior_mvp/app.py",
        ".workflow/slices/S15b-deep-case-portfolio/test_evidence.md",
    ]
    inventory = [
        {"path": paths[0], "sha256": "a" * 64, "bytes": 7, "mode": 0o644},
        {"path": paths[1], "sha256": "b" * 64, "bytes": 9, "mode": 0o644},
    ]
    monkeypatch.setattr(review_checks, "_head", lambda root: "base")
    monkeypatch.setattr(
        review_checks,
        "_git",
        lambda root, *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=b"refs/heads/feature\n",
        ),
    )
    monkeypatch.setattr(review_checks, "_require_scope", lambda root: paths)
    monkeypatch.setattr(review_checks, "build_inventory", lambda root, value: inventory)
    monkeypatch.setattr(
        review_checks,
        "_target_index_identity",
        lambda root: {"path": "index", "sha256": "c" * 64},
        raising=False,
    )

    result = review_checks.check_identity(Path("/candidate"), "base")

    assert len(result["candidate_id"]) == 64
    assert result["files"] == [inventory[0]]
    assert result["records"] == [inventory[1]]
    assert result["target"]["head"] == "base"
    assert result["target"]["ref"] == "refs/heads/feature"
    assert result["target"]["index"]["sha256"] == "c" * 64


def test_frozen_oid_mechanism_reads_actual_bytes_and_modes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"one")
    first = review_checks.canonical_tree_identity(tmp_path)

    path.write_bytes(b"two")
    second = review_checks.canonical_tree_identity(tmp_path)
    path.chmod(0o755)
    executable = review_checks.canonical_tree_identity(tmp_path)

    assert first["oid"] != second["oid"]
    assert second["oid"] != executable["oid"]
    assert executable["files"] == [
        {
            "path": "payload.bin",
            "mode": "100755",
            "git_oid": review_checks._git_object_oid("blob", b"two"),
            "sha256": review_checks.hashlib.sha256(b"two").hexdigest(),
            "bytes": 3,
        }
    ]


EXPECTED_STATE = {
    "selected_id": "SAU-H0-721049",
    "hs6": "721049",
    "mode": "public",
    "real_state": "INVESTIGATE",
    "active_state": "INVESTIGATE",
    "synthetic_disclosure": False,
    "synthetic_label_count": 0,
    "locale": "en",
    "viewport": "desktop-1440x900",
    "view": "workspace",
}
PAINT_KEYS = (
    "fontFamily", "fontSize", "fontWeight", "fontStyle", "fontStretch",
    "fontFeatureSettings", "lineHeight", "letterSpacing", "wordSpacing",
    "whiteSpace", "textTransform", "color", "backgroundColor",
    "backgroundImage", "borderTop", "borderRight", "borderBottom",
    "borderLeft", "boxShadow", "opacity", "filter", "backdropFilter",
)


def _valid_phase_record() -> dict:
    shared = {
        "scroll": 100,
        "scroll_max": 1000,
        "viewport_size": [1440, 900],
        "margin": 95.0,
        "dpr": 1,
        "font_status": "loaded",
        "width": 100,
        "height": 200,
        "local": [["DIV", "same", 1, 0.0, 0.0, 10.0, 10.0]],
        "header": [[0.0, 0.0, 20.0, 900.0], [20.0, 0.0, 1420.0, 64.0]],
        "state": deepcopy(EXPECTED_STATE),
        "dom": {
            "roots": ["<aside></aside>", "<header></header>", "<section></section>"],
            "controls": {
                "opportunity-select": {
                    "tag": "SELECT", "name": None,
                    "value": "SAU-H0-721049", "checked": False,
                }
            },
            "stylesheets": [{"source": "/static/css/base.css", "rules": []}],
        },
        "styles": [{
            "path": "0:", "tag": "SECTION", "rect": [0.0, 0.0, 100.0, 200.0],
            "values": {key: "initial" for key in PAINT_KEYS},
        }],
        "document": {
            "lang": "en", "dir": "ltr", "body_class": "",
            "body_aria_busy": "false",
        },
        "element_style": None,
        "root_style": None,
        "element_style_map": {},
        "root_style_map": {},
        "element_margin_top": 0.0,
    }
    reference = {**deepcopy(shared), "top": 94.75}
    candidate = {**deepcopy(shared), "top": 94.875}
    adjusted = {**deepcopy(shared), "top": 94.875}
    adjusted["element_style"] = "margin-top: 0.125px;"
    adjusted["element_style_map"] = {
        "margin-top": {"value": "0.125px", "priority": ""}
    }
    adjusted["root_style"] = "overflow-anchor: none; scroll-behavior: auto;"
    adjusted["root_style_map"] = {
        "overflow-anchor": {"value": "none", "priority": ""},
        "scroll-behavior": {"value": "auto", "priority": ""},
    }
    adjusted["element_margin_top"] = 0.125
    restored = {**deepcopy(shared), "top": 94.75}
    return {
        "path": "en/desktop-1440x900/journey-b-steel-public-workspace.webp",
        "reference": reference,
        "candidate": candidate,
        "adjusted": adjusted,
        "restored": restored,
        "delta": 0.125,
        "reference_link_exact": True,
        "candidate_link_exact": True,
        "restoration_rgb_exact": True,
        "raw_drift_nonzero": True,
        "registered_metrics": {"passes": True},
    }


def test_phase_record_rejects_every_missing_snapshot_proof() -> None:
    required = (
        "top", "scroll", "scroll_max", "viewport_size", "margin", "dpr",
        "font_status", "width", "height", "local", "header", "state", "dom",
        "styles", "document", "element_style", "root_style",
        "element_style_map", "root_style_map", "element_margin_top",
    )
    for phase in ("reference", "candidate", "adjusted", "restored"):
        for key in required:
            record = _valid_phase_record()
            record[phase].pop(key)
            assert review_checks.phase_record_problems(
                record, expected_state=EXPECTED_STATE
            ), (phase, key)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row["candidate"].__setitem__("dpr", 2),
        lambda row: row["candidate"].__setitem__("font_status", "loading"),
        lambda row: row.__setitem__("delta", float("nan")),
        lambda row: row["candidate"].__setitem__("margin", 94.0),
        lambda row: row["candidate"].__setitem__("top", True),
        lambda row: row["candidate"].__setitem__("scroll", 1000),
        lambda row: row["candidate"].__setitem__("dom", {}),
        lambda row: row["candidate"].__setitem__("styles", []),
        lambda row: row["candidate"].__setitem__("local", []),
        lambda row: row["adjusted"]["styles"][0]["values"].__setitem__("color", "red"),
        lambda row: row["adjusted"]["element_style_map"].__setitem__(
            "padding", {"value": "1px", "priority": ""}
        ),
        lambda row: row["adjusted"]["root_style_map"].__setitem__(
            "color", {"value": "red", "priority": ""}
        ),
        lambda row: row["restored"]["root_style_map"].__setitem__(
            "color", {"value": "red", "priority": ""}
        ),
        lambda row: [
            row[phase]["state"].__setitem__("active_state", "REJECT")
            for phase in ("reference", "candidate", "adjusted", "restored")
        ],
        lambda row: row.__setitem__("reference_link_exact", False),
        lambda row: row.__setitem__("candidate_link_exact", False),
    ],
)
def test_phase_record_rejects_owner_bypasses(mutation) -> None:
    record = _valid_phase_record()
    mutation(record)

    assert review_checks.phase_record_problems(
        record, expected_state=EXPECTED_STATE
    )


def test_phase_record_accepts_complete_conjunctive_positive_case() -> None:
    assert review_checks.phase_record_problems(
        _valid_phase_record(), expected_state=EXPECTED_STATE
    ) == []


def test_phase_expected_state_is_manifest_derived() -> None:
    entry = {
        "locale": "en", "viewport": "desktop-1440x900", "mode": "public",
        "screen": "journey-b-steel-public-workspace", "case_id": "SAU-H0-721049",
    }

    assert review_checks.phase_expected_state(entry) == EXPECTED_STATE


def test_phase_bindings_reject_self_reported_substitution() -> None:
    bindings = {
        "base": "f671f36fe6ea56b2c009ede91847b7dbf950a939",
        "reference_manifest_sha256": "90ddfa015a6093048e235abe699cae570ef78d12e386c4266f59c39271c11164",
        "candidate_manifest_sha256": "4fd90577afe863b290cdff4a8932bc6627918c72e9834ef6c4ed01c248cdae16",
        "regions_sha256": "fcfb531d903b8bfd8e3b5384e700b416ae766f78641a8cddba8261fa99f46c8d",
        "capture_source": "browser_tests/test_s15b_selection.py",
        "browser_version": "151.0.7922.34",
        "chromium_revision": "chromium-1234",
        "playwright_version": "1.62.0",
        "pytest_playwright_version": "0.9.0",
        "launch_flags": [
            "--font-render-hinting=none", "--disable-lcd-text",
            "--force-color-profile=srgb",
        ],
    }
    assert review_checks.phase_binding_problems(bindings) == []
    bindings["capture_source"] = "../escape.py"
    assert review_checks.phase_binding_problems(bindings)


def test_default_review_modules_collect_with_pillow_unavailable() -> None:
    project = Path(__file__).resolve().parents[1]
    program = """
import importlib.abc
import runpy
import sys
class BlockPillow(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'PIL' or fullname.startswith('PIL.'):
            raise ModuleNotFoundError('Pillow intentionally unavailable')
        return None
sys.meta_path.insert(0, BlockPillow())
import scripts.s15b_review_checks
runpy.run_path('tests/test_s15b_review_checks.py', run_name='pillow_absence_probe')
"""
    result = subprocess.run(
        [sys.executable, "-c", program],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
