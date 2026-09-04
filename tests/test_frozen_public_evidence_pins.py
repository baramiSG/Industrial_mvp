"""Frozen public evidence byte pins and frozen visual-oracle provenance."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT

PINS = {
    "data/snapshots/public/SAU-H0-721049.json": (
        "5c2ab676e5b68509e002eddff4f80107c0d2cc1b78c3b063e26f84d13355512e",
        11153,
    ),
    "data/snapshots/public/SAU-H0-390210.json": (
        "edaeaabf82276f75a1887aa0869b9e3a4070c3338fa0e9f677c55607cd8d0ac4",
        10144,
    ),
    "data/snapshots/public/historical/v1/SAU-H0-721049.json": (
        "10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7",
        6850,
    ),
    "data/snapshots/public/historical/v1/SAU-H0-390210.json": (
        "cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948",
        5572,
    ),
}

BASE = "a610b49b1f9a34ffb6430e92b7a6cb7fafb82ca4"
FROZEN_PATHS = (
    "data/snapshots/public",
    "data/synthetic",
    "data/golden",
    "browser_tests/baselines",
)
VISUAL_BASELINE_ROOT = PROJECT_ROOT / "browser_tests" / "baselines" / "v0.3.0"
VISUAL_BASELINE_ENTRIES = 40
TOP_LEVEL_MODULE = re.compile(r"^src/ior_mvp/[^/]+\.py$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_diff_quiet(*paths: str) -> int:
    result = subprocess.run(
        ["git", "diff", "--quiet", BASE, "--", *paths],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


def visual_provenance_problems(
    baseline_root: Path,
    project_root: Path,
) -> list[str]:
    """Mirror the provenance part of the visual oracle without Pillow.

    ``browser_tests.visual_baselines.validate_manifest`` (browser gate) pins
    the SHA-256 of every top-level ``src/ior_mvp/*.py`` module, the static
    bundle, the vendored fonts and the UI/evidence/narrative configs and fails
    closed on drift. Pillow is an e2e-only dependency, so this PIL-free mirror
    lets the plain pytest gate surface the same drift: a stale manifest digest,
    any recorded file whose bytes changed, and any top-level module added to
    or removed from ``src/ior_mvp/`` since the manifest was generated.
    """
    manifest_path = baseline_root / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []
    digest = (baseline_root / "manifest.sha256").read_text(encoding="ascii")
    if _sha256(manifest_path) != digest.strip():
        problems.append("manifest.sha256 does not match manifest.json")
    recorded: dict[str, str] = {
        **payload.get("source_tree", {}),
        **payload.get("font_hashes", {}),
    }
    for relative, expected in sorted(recorded.items()):
        path = project_root / relative
        if not path.is_file():
            problems.append(f"recorded file missing: {relative}")
        elif _sha256(path) != expected:
            problems.append(f"source-tree provenance is stale: {relative}")
    pinned_modules = {
        relative
        for relative in payload.get("source_tree", {})
        if TOP_LEVEL_MODULE.match(relative)
    }
    actual_modules = {
        path.relative_to(project_root).as_posix()
        for path in (project_root / "src" / "ior_mvp").glob("*.py")
    }
    for relative in sorted(actual_modules - pinned_modules):
        problems.append(f"top-level module not in visual manifest: {relative}")
    for relative in sorted(pinned_modules - actual_modules):
        problems.append(f"pinned top-level module missing: {relative}")
    return problems


def test_public_and_synthetic_bytes_unchanged_from_base() -> None:
    for rel, (expected_hash, expected_bytes) in PINS.items():
        path = PROJECT_ROOT / rel
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected_hash
        assert len(data) == expected_bytes

    assert _git_diff_quiet(*FROZEN_PATHS) == 0


def test_visual_baseline_tree_unchanged_from_base() -> None:
    """S11 is a non-visual slice: no byte under browser_tests/baselines moves."""
    assert _git_diff_quiet("browser_tests/baselines") == 0


def test_visual_baseline_provenance_matches_working_tree() -> None:
    payload = json.loads(
        (VISUAL_BASELINE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    assert payload["baseline_version"] == "v0.3.0"
    assert len(payload["entries"]) == VISUAL_BASELINE_ENTRIES
    assert visual_provenance_problems(VISUAL_BASELINE_ROOT, PROJECT_ROOT) == []


def _clone_recorded_tree(tmp_path: Path) -> tuple[Path, Path]:
    baseline_root = tmp_path / "baselines"
    baseline_root.mkdir()
    for name in ("manifest.json", "manifest.sha256"):
        shutil.copyfile(VISUAL_BASELINE_ROOT / name, baseline_root / name)
    project_root = tmp_path / "project"
    payload = json.loads(
        (baseline_root / "manifest.json").read_text(encoding="utf-8")
    )
    for relative in {**payload["source_tree"], **payload["font_hashes"]}:
        target = project_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT_ROOT / relative, target)
    return baseline_root, project_root


def test_provenance_check_detects_modified_top_level_module(
    tmp_path: Path,
) -> None:
    baseline_root, project_root = _clone_recorded_tree(tmp_path)
    assert visual_provenance_problems(baseline_root, project_root) == []
    module = project_root / "src" / "ior_mvp" / "config.py"
    module.write_bytes(module.read_bytes() + b"\n# drift\n")
    problems = visual_provenance_problems(baseline_root, project_root)
    assert problems == [
        "source-tree provenance is stale: src/ior_mvp/config.py"
    ]


def test_provenance_check_detects_new_top_level_module(tmp_path: Path) -> None:
    baseline_root, project_root = _clone_recorded_tree(tmp_path)
    (project_root / "src" / "ior_mvp" / "zz_unpinned.py").write_text(
        "", encoding="utf-8"
    )
    problems = visual_provenance_problems(baseline_root, project_root)
    assert problems == [
        "top-level module not in visual manifest: src/ior_mvp/zz_unpinned.py"
    ]


def test_provenance_check_detects_stale_manifest_digest(tmp_path: Path) -> None:
    baseline_root, project_root = _clone_recorded_tree(tmp_path)
    manifest = baseline_root / "manifest.json"
    manifest.write_bytes(manifest.read_bytes() + b"\n")
    problems = visual_provenance_problems(baseline_root, project_root)
    assert problems == ["manifest.sha256 does not match manifest.json"]
