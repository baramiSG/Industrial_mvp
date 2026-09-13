"""Frozen public evidence byte pins and frozen visual-oracle provenance."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

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

FROZEN_PATHS = (
    "data/snapshots/public",
    "data/synthetic",
    "data/golden",
    "browser_tests/baselines",
)

FROZEN_TREE_OIDS = {
    "data/snapshots/public": "a67a921c1909c20e1afe2647e6f41a792cecd08a",
    "data/synthetic": "7459beb8a8777fe33592c314bac54de0a1833f25",
    "data/golden": "72618db654110823ec7a8d4dd6415a37e4554e33",
    "browser_tests/baselines": "709325b65f4fb567f10d3fa23a0139b1ef0de602",
}

# Used only by the depth-1 detector of this repository to prove the object absent.
_BASE_COMMIT_FOR_ABSENCE_PROOF = (
    "a610b49b1f9a34ffb6430e92b7a6cb7fafb82ca4"
)

VISUAL_BASELINE_ROOT = PROJECT_ROOT / "browser_tests" / "baselines" / "v0.3.0"
VISUAL_BASELINE_ENTRIES = 76
TOP_LEVEL_MODULE = re.compile(r"^src/ior_mvp/[^/]+\.py$")

GIT_EXIT_SUCCESS = 0
GIT_EXIT_DIFFERS = 1

WORKING_TREE_DIFFERS = "working tree differs from HEAD under frozen roots"
COMMITTED_TREE_CHANGED_PREFIX = "committed tree changed:"
UNTRACKED_PATH_PREFIX = "untracked path under frozen root:"

_SYNTHETIC_FROZEN_ROOTS = FROZEN_PATHS
_SYNTHETIC_FIXTURE_NAME = "frozen.json"
_SYNTHETIC_FIXTURE_BYTES = b'{"fixture":true}\n'


class FrozenTreeCheckError(RuntimeError):
    """Raised when a frozen-tree git check cannot run or resolve."""


def _git_env(env: Mapping[str, str] | None) -> dict[str, str]:
    if env is None:
        return os.environ.copy()
    return dict(env)


def _run_git(
    repo_root: Path,
    *args: str,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=_git_env(env),
    )


def frozen_tree_problems(
    repo_root: Path,
    expected_tree_oids: Mapping[str, str],
    roots: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
) -> list[str]:
    """Return deterministic frozen-tree drift problems for ``roots`` at HEAD."""
    problems: list[str] = []
    for root in roots:
        if root not in expected_tree_oids:
            raise FrozenTreeCheckError(
                f"missing expected tree OID for frozen root: {root}"
            )

    for root in roots:
        expected = expected_tree_oids[root]
        rev_parse = _run_git(
            repo_root,
            "rev-parse",
            "--verify",
            "--quiet",
            f"HEAD:{root}",
            env=env,
        )
        if rev_parse.returncode != GIT_EXIT_SUCCESS or not rev_parse.stdout.strip():
            detail = rev_parse.stderr.strip() or rev_parse.stdout.strip()
            raise FrozenTreeCheckError(
                f"git rev-parse failed for HEAD:{root}: {detail}"
            )
        actual = rev_parse.stdout.strip()
        object_type = _run_git(repo_root, "cat-file", "-t", actual, env=env)
        if object_type.returncode != GIT_EXIT_SUCCESS:
            detail = object_type.stderr.strip() or object_type.stdout.strip()
            raise FrozenTreeCheckError(
                f"git cat-file failed for {actual}: {detail}"
            )
        if object_type.stdout.strip() != "tree":
            raise FrozenTreeCheckError(
                f"expected tree object at HEAD:{root}, got {object_type.stdout.strip()!r}"
            )
        if actual != expected:
            problems.append(
                f"{COMMITTED_TREE_CHANGED_PREFIX} {root} {actual} != {expected}"
            )

    if roots:
        diff = _run_git(repo_root, "diff", "--quiet", "HEAD", "--", *roots, env=env)
        if diff.returncode == GIT_EXIT_DIFFERS:
            problems.append(WORKING_TREE_DIFFERS)
        elif diff.returncode != GIT_EXIT_SUCCESS:
            detail = diff.stderr.strip() or diff.stdout.strip()
            raise FrozenTreeCheckError(
                f"git diff --quiet HEAD failed: {detail}"
            )

        untracked = _run_git(
            repo_root,
            "ls-files",
            "--others",
            "--",
            *roots,
            env=env,
        )
        if untracked.returncode != GIT_EXIT_SUCCESS:
            detail = untracked.stderr.strip() or untracked.stdout.strip()
            raise FrozenTreeCheckError(
                f"git ls-files --others failed: {detail}"
            )
        untracked_paths = sorted(
            line.strip()
            for line in untracked.stdout.splitlines()
            if line.strip()
        )
        for path in untracked_paths:
            problems.append(f"{UNTRACKED_PATH_PREFIX} {path}")

    return problems


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _isolated_git_env(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir()
    gitconfig = home / "gitconfig"
    gitconfig.write_text(
        "[init]\n\tdefaultBranch = main\n[commit]\n\tgpgsign = false\n",
        encoding="utf-8",
    )
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    env.update(
        {
            "HOME": str(home),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(gitconfig),
            "GIT_AUTHOR_NAME": "frozen-tree-detector",
            "GIT_AUTHOR_EMAIL": "frozen-tree-detector@example.com",
            "GIT_COMMITTER_NAME": "frozen-tree-detector",
            "GIT_COMMITTER_EMAIL": "frozen-tree-detector@example.com",
        }
    )
    return env


def _init_synthetic_origin(tmp_path: Path, env: Mapping[str, str]) -> Path:
    origin = tmp_path / "origin"
    origin.mkdir()
    _run_git(origin, "init", "-q", env=env)
    for root in _SYNTHETIC_FROZEN_ROOTS:
        fixture = origin / root / _SYNTHETIC_FIXTURE_NAME
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_bytes(_SYNTHETIC_FIXTURE_BYTES)
    _run_git(origin, "add", "-A", env=env)
    _run_git(origin, "commit", "-q", "-m", "base", env=env)
    (origin / "unrelated.txt").write_text("later\n", encoding="utf-8")
    _run_git(origin, "add", "unrelated.txt", env=env)
    _run_git(origin, "commit", "-q", "-m", "later", env=env)
    return origin


def _depth_one_clone(origin: Path, clone_dir: Path, env: Mapping[str, str]) -> Path:
    clone_url = f"file://{origin.resolve()}"
    result = subprocess.run(
        ["git", "clone", "-q", "--depth", "1", clone_url, str(clone_dir)],
        capture_output=True,
        text=True,
        check=False,
        env=_git_env(env),
    )
    if result.returncode != GIT_EXIT_SUCCESS:
        detail = result.stderr.strip() or result.stdout.strip()
        raise FrozenTreeCheckError(f"git clone failed: {detail}")
    return clone_dir


def _tree_oids_at_ref(
    repo_root: Path,
    ref: str,
    env: Mapping[str, str],
) -> dict[str, str]:
    return {
        root: _run_git(repo_root, "rev-parse", f"{ref}:{root}", env=env).stdout.strip()
        for root in _SYNTHETIC_FROZEN_ROOTS
    }


def _synthetic_tree_oids(origin: Path, env: Mapping[str, str]) -> dict[str, str]:
    base_commit = _run_git(origin, "rev-parse", "HEAD~1", env=env).stdout.strip()
    return _tree_oids_at_ref(origin, base_commit, env)


def _assert_base_commit_absent(
    repo_root: Path,
    base_commit: str,
    env: Mapping[str, str],
) -> None:
    result = _run_git(repo_root, "cat-file", "-e", base_commit, env=env)
    assert result.returncode != GIT_EXIT_SUCCESS


@pytest.fixture
def synthetic_depth_one_clone(tmp_path: Path) -> tuple[Path, dict[str, str], str, dict[str, str]]:
    env = _isolated_git_env(tmp_path)
    origin = _init_synthetic_origin(tmp_path, env)
    base_commit = _run_git(origin, "rev-parse", "HEAD~1", env=env).stdout.strip()
    oids = _synthetic_tree_oids(origin, env)
    clone = _depth_one_clone(origin, tmp_path / "clone", env)
    shallow = _run_git(clone, "rev-parse", "--is-shallow-repository", env=env)
    assert shallow.stdout.strip() == "true"
    _assert_base_commit_absent(clone, base_commit, env)
    return clone, oids, base_commit, env


def test_public_and_synthetic_bytes_unchanged_from_base() -> None:
    """S14b added five derived snapshots and five scenarios and regenerated the governed baselines once (ADR-022)."""
    for rel, (expected_hash, expected_bytes) in PINS.items():
        path = PROJECT_ROOT / rel
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected_hash
        assert len(data) == expected_bytes

    assert (
        frozen_tree_problems(PROJECT_ROOT, FROZEN_TREE_OIDS, FROZEN_PATHS) == []
    )


def test_visual_baseline_tree_unchanged_from_base() -> None:
    """S14b regenerated and SC-5 stabilized the baselines; no later byte moves."""
    assert (
        frozen_tree_problems(
            PROJECT_ROOT,
            {"browser_tests/baselines": FROZEN_TREE_OIDS["browser_tests/baselines"]},
            ("browser_tests/baselines",),
        )
        == []
    )


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


def test_frozen_tree_check_passes_in_depth_one_clone_without_base_commit(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, base_commit, env = synthetic_depth_one_clone
    _assert_base_commit_absent(clone, base_commit, env)
    assert frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env) == []


def test_frozen_tree_check_passes_in_depth_one_clone_of_this_repository_without_a610b49(
    tmp_path: Path,
) -> None:
    env = _isolated_git_env(tmp_path)
    clone = _depth_one_clone(
        PROJECT_ROOT,
        tmp_path / "repo-clone",
        env,
    )
    shallow = _run_git(clone, "rev-parse", "--is-shallow-repository", env=env)
    assert shallow.stdout.strip() == "true"
    _assert_base_commit_absent(clone, _BASE_COMMIT_FOR_ABSENCE_PROOF, env)
    clone_oids = {
        root: _run_git(
            clone,
            "rev-parse",
            f"HEAD:{root}",
            env=env,
        ).stdout.strip()
        for root in FROZEN_PATHS
    }
    assert {
        root: oid
        for root, oid in clone_oids.items()
        if root != "browser_tests/baselines"
    } == {
        root: oid
        for root, oid in FROZEN_TREE_OIDS.items()
        if root != "browser_tests/baselines"
    }
    assert (
        frozen_tree_problems(clone, clone_oids, FROZEN_PATHS, env=env) == []
    )


def test_frozen_tree_check_detects_working_tree_byte_mutation(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    target = clone / _SYNTHETIC_FROZEN_ROOTS[0] / _SYNTHETIC_FIXTURE_NAME
    target.write_bytes(target.read_bytes() + b"# drift")
    assert (
        frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env)
        == [WORKING_TREE_DIFFERS]
    )


def test_frozen_tree_check_detects_working_tree_path_mutation(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    root = _SYNTHETIC_FROZEN_ROOTS[0]
    source = clone / root / _SYNTHETIC_FIXTURE_NAME
    renamed = clone / root / "renamed.json"
    source.rename(renamed)
    assert frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env) == [
        WORKING_TREE_DIFFERS,
        f"{UNTRACKED_PATH_PREFIX} {root}/renamed.json",
    ]


def test_frozen_tree_check_detects_untracked_path(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    root = _SYNTHETIC_FROZEN_ROOTS[0]
    extra = clone / root / "extra.json"
    extra.write_text("{}", encoding="utf-8")
    assert frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env) == [
        f"{UNTRACKED_PATH_PREFIX} {root}/extra.json",
    ]


def test_frozen_tree_check_detects_committed_byte_mutation(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    root = _SYNTHETIC_FROZEN_ROOTS[0]
    target = clone / root / _SYNTHETIC_FIXTURE_NAME
    target.write_bytes(target.read_bytes() + b"# committed")
    _run_git(clone, "add", "-A", env=env)
    _run_git(clone, "commit", "-q", "-m", "mutate frozen bytes", env=env)
    actual = _run_git(
        clone,
        "rev-parse",
        "--verify",
        "--quiet",
        f"HEAD:{root}",
        env=env,
    ).stdout.strip()
    expected = oids[root]
    assert frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env) == [
        f"{COMMITTED_TREE_CHANGED_PREFIX} {root} {actual} != {expected}",
    ]


def test_frozen_tree_check_detects_committed_path_mutation(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    root = _SYNTHETIC_FROZEN_ROOTS[0]
    source = clone / root / _SYNTHETIC_FIXTURE_NAME
    destination = clone / root / "moved.json"
    _run_git(clone, "mv", str(source.relative_to(clone)), str(destination.relative_to(clone)), env=env)
    _run_git(clone, "commit", "-q", "-m", "rename frozen path", env=env)
    actual = _run_git(
        clone,
        "rev-parse",
        "--verify",
        "--quiet",
        f"HEAD:{root}",
        env=env,
    ).stdout.strip()
    expected = oids[root]
    assert frozen_tree_problems(clone, oids, _SYNTHETIC_FROZEN_ROOTS, env=env) == [
        f"{COMMITTED_TREE_CHANGED_PREFIX} {root} {actual} != {expected}",
    ]


def test_frozen_tree_check_fails_on_missing_root_object(
    synthetic_depth_one_clone: tuple[Path, dict[str, str], str, dict[str, str]],
) -> None:
    clone, oids, _base_commit, env = synthetic_depth_one_clone
    expected = dict(oids)
    expected["data/missing-root"] = oids[_SYNTHETIC_FROZEN_ROOTS[0]]
    with pytest.raises(FrozenTreeCheckError):
        frozen_tree_problems(
            clone,
            expected,
            (*_SYNTHETIC_FROZEN_ROOTS, "data/missing-root"),
            env=env,
        )


def test_frozen_tree_check_fails_on_git_command_error(tmp_path: Path) -> None:
    env = _isolated_git_env(tmp_path)
    not_a_repo = tmp_path / "not-a-repo"
    not_a_repo.mkdir()
    with pytest.raises(FrozenTreeCheckError):
        frozen_tree_problems(
            not_a_repo,
            FROZEN_TREE_OIDS,
            FROZEN_PATHS,
            env=env,
        )


def test_frozen_tree_check_fails_on_non_tree_root(tmp_path: Path) -> None:
    env = _isolated_git_env(tmp_path)
    origin = tmp_path / "origin"
    origin.mkdir()
    _run_git(origin, "init", "-q", env=env)
    blob_path = origin / "blob.txt"
    blob_path.write_text("blob\n", encoding="utf-8")
    _run_git(origin, "add", "blob.txt", env=env)
    _run_git(origin, "commit", "-q", "-m", "blob root", env=env)
    clone = _depth_one_clone(origin, tmp_path / "clone", env)
    blob_oid = _run_git(
        clone,
        "rev-parse",
        "--verify",
        "--quiet",
        "HEAD:blob.txt",
        env=env,
    ).stdout.strip()
    expected = {"blob.txt": blob_oid}
    with pytest.raises(FrozenTreeCheckError):
        frozen_tree_problems(clone, expected, ("blob.txt",), env=env)


def test_frozen_tree_oids_are_content_addresses(tmp_path: Path) -> None:
    env = _isolated_git_env(tmp_path)

    def build_origin(message: str) -> tuple[Path, dict[str, str]]:
        origin = tmp_path / f"origin-{message}"
        origin.mkdir()
        _run_git(origin, "init", "-q", env=env)
        for root in _SYNTHETIC_FROZEN_ROOTS:
            fixture = origin / root / _SYNTHETIC_FIXTURE_NAME
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_bytes(_SYNTHETIC_FIXTURE_BYTES)
        _run_git(origin, "add", "-A", env=env)
        _run_git(origin, "commit", "-q", "-m", message, env=env)
        return origin, _tree_oids_at_ref(origin, "HEAD", env)

    _origin_a, oids_a = build_origin("message-a")
    _origin_b, oids_b = build_origin("message-b")
    assert oids_a == oids_b
