from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


APPROVED_EXACT = frozenset(
    {
        ".workflow/state.json",
        "README.md",
        "browser_tests/harness.py",
        "browser_tests/pages.py",
        "browser_tests/test_accessibility.py",
        "browser_tests/test_journeys.py",
        "browser_tests/test_s15b_selection.py",
        "browser_tests/test_visual_baselines.py",
        "browser_tests/visual_baselines.py",
        "config/project.yaml",
        "config/ui_strings.v1.yaml",
        "data/graph/current.json",
        "data/manifests/snapshot_manifest.json",
        "data/snapshots/public/PUBLIC-SAU-H6-294110-2026-09-12.json",
        "data/snapshots/public/PUBLIC-SAU-H6-294120-2026-09-12.json",
        "data/snapshots/public/PUBLIC-SAU-H6-310430-2026-09-12.json",
        "data/snapshots/public/PUBLIC-SAU-H6-310510-2026-09-12.json",
        "data/synthetic/SYN-MINISTRY-FERT-RETAIL-PACKS-001.json",
        "data/synthetic/SYN-MINISTRY-PENICILLIN-API-001.json",
        "data/synthetic/SYN-MINISTRY-SOP-001.json",
        "data/synthetic/SYN-MINISTRY-STREPTOMYCIN-API-001.json",
        "docs/ARCHITECTURE_DECISIONS.md",
        "docs/BUILD_PROGRESS.md",
        "docs/BUILD_ROADMAP.md",
        "docs/KNOWN_LIMITATIONS.md",
        "docs/REQUIREMENTS_TRACEABILITY.md",
        "docs/authority/00_AUTHORITY_MANIFEST.md",
        "docs/authority/authority_hashes.json",
        "docs/core/01_PRODUCT_AND_REQUIREMENTS.md",
        "docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md",
        "docs/core/03_SYSTEM_ARCHITECTURE.md",
        "docs/core/04_CANONICAL_DATA_MODEL.md",
        "docs/core/07_DETERMINISTIC_ENGINE_SPEC.md",
        "docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md",
        "docs/implementation/API_REFERENCE.md",
        "docs/milestones/v0.3.0/SLICE_GRAPH.md",
        "scripts/s15b_review_checks.py",
        "src/ior_mvp/app.py",
        "src/ior_mvp/case_selection_view.py",
        "src/ior_mvp/config.py",
        "src/ior_mvp/dossier.py",
        "src/ior_mvp/simulation.py",
        "src/ior_mvp/static/css/overview.css",
        "src/ior_mvp/static/index.html",
        "src/ior_mvp/static/modules/api.js",
        "src/ior_mvp/static/modules/events.js",
        "src/ior_mvp/static/modules/portfolio.js",
        "src/ior_mvp/static/modules/renderers/decision.js",
        "src/ior_mvp/static/modules/selection/index.js",
        "src/ior_mvp/static/modules/selection/render.js",
        "src/ior_mvp/static/modules/state.js",
        "tests/test_api.py",
        "tests/test_authority_disclosure.py",
        "tests/test_browser_harness_contract.py",
        "tests/test_es_modules.py",
        "tests/test_frozen_public_evidence_pins.py",
        "tests/test_golden_cases.py",
        "tests/test_integrity_contract.py",
        "tests/test_performance.py",
        "tests/test_s15b_graph_refresh.py",
        "tests/test_s15b_portfolio.py",
        "tests/test_s15b_review_checks.py",
        "tests/test_s15b_selection_view.py",
        "tests/test_scenario_validation.py",
        "tests/test_static_frontend.py",
        "tests/test_synthetic_isolation.py",
        "tests/test_ui_catalogue.py",
        "tests/test_visual_baseline_contract.py",
    }
    | {
        f".workflow/slices/S15b-deep-case-portfolio/{name}.md"
        for name in (
            "completion",
            "context",
            "implementation_log",
            "implementation_review",
            "persona",
            "plan",
            "plan_review",
            "pr_record",
            "reviewer_findings",
            "test_evidence",
        )
    }
)
APPROVED_PREFIXES = (
    "browser_tests/baselines/v0.3.0/",
    "data/graph/projections/",
)
SAFE_CONTROL_KEYS = (
    "core.attributesfile",
    "core.hookspath",
    "commit.gpgsign",
    "tag.gpgsign",
    "gpg.format",
    "user.name",
    "user.email",
    "user.signingkey",
)
FROZEN_ROOTS = (
    "data/golden",
    "data/snapshots/public",
    "data/synthetic",
)
PRESERVED_DATA_EXCEPTIONS = {
    "data/graph/current.json",
    "data/manifests/snapshot_manifest.json",
}
RECORD_PREFIX = ".workflow/slices/S15b-deep-case-portfolio/"


class ReviewCheckError(ValueError):
    pass


def _regular_path(root: Path, relative: str) -> Path:
    parsed = PurePosixPath(relative)
    if parsed.is_absolute() or ".." in parsed.parts or not parsed.parts:
        raise ReviewCheckError(f"unsafe path: {relative}")
    canonical_root = root.resolve()
    path = canonical_root.joinpath(*parsed.parts)
    if path.is_symlink() or not path.is_file():
        raise ReviewCheckError(f"regular file required: {relative}")
    if not path.resolve().is_relative_to(canonical_root):
        raise ReviewCheckError(f"path escapes root: {relative}")
    return path


def _file_git_mode(path: Path) -> str:
    value = path.stat(follow_symlinks=False)
    if not stat.S_ISREG(value.st_mode):
        raise ReviewCheckError(f"regular file required: {path.name}")
    return "100755" if value.st_mode & 0o111 else "100644"


def _git_object_oid(kind: str, payload: bytes) -> str:
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def canonical_tree_identity(root: Path) -> dict[str, Any]:
    canonical = root.resolve()
    if root.is_symlink() or not canonical.is_dir():
        raise ReviewCheckError("canonical tree root must be a directory")
    files: list[dict[str, Any]] = []

    def tree(directory: Path, prefix: PurePosixPath) -> tuple[str, int]:
        values: list[tuple[str, str, bytes]] = []
        total = 0
        children = sorted(
            directory.iterdir(),
            key=lambda path: path.name + ("/" if path.is_dir() else ""),
        )
        for path in children:
            if path.is_symlink():
                raise ReviewCheckError(f"symlink is not allowed: {path.name}")
            relative = prefix / path.name
            if path.is_dir():
                oid, count = tree(path, relative)
                values.append((path.name, "40000", bytes.fromhex(oid)))
                total += count
            elif path.is_file():
                payload = path.read_bytes()
                mode = _file_git_mode(path)
                oid = _git_object_oid("blob", payload)
                values.append((path.name, mode, bytes.fromhex(oid)))
                files.append(
                    {
                        "path": relative.as_posix(),
                        "mode": mode,
                        "git_oid": oid,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "bytes": len(payload),
                    }
                )
                total += 1
            else:
                raise ReviewCheckError(f"unsupported tree entry: {path.name}")
        body = b"".join(
            mode.encode("ascii")
            + b" "
            + name.encode("utf-8")
            + b"\0"
            + oid
            for name, mode, oid in values
        )
        return _git_object_oid("tree", body), total

    oid, count = tree(canonical, PurePosixPath())
    return {"oid": oid, "count": count, "files": sorted(files, key=lambda row: row["path"])}


def build_inventory(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    if len(set(paths)) != len(paths):
        raise ReviewCheckError("duplicate inventory path")
    rows = []
    for relative in sorted(paths):
        path = _regular_path(root, relative)
        payload = path.read_bytes()
        rows.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "mode": stat.S_IMODE(path.stat().st_mode),
                "git_mode": _file_git_mode(path),
            }
        )
    return rows


def compare_inventory(
    expected_root: Path,
    actual_root: Path,
    paths: list[str],
) -> list[str]:
    problems = []
    for relative in sorted(paths):
        try:
            expected = _regular_path(expected_root, relative)
        except ReviewCheckError:
            problems.append(f"expected file missing: {relative}")
            continue
        try:
            actual = _regular_path(actual_root, relative)
        except ReviewCheckError:
            problems.append(f"actual file missing: {relative}")
            continue
        if stat.S_IMODE(expected.stat().st_mode) != stat.S_IMODE(actual.stat().st_mode):
            problems.append(f"mode mismatch: {relative}")
        elif expected.read_bytes() != actual.read_bytes():
            problems.append(f"content mismatch: {relative}")
    return problems


def controls_match(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return expected == actual


def target_binding_matches(expected: dict[str, str], actual: dict[str, str]) -> bool:
    return expected == actual


def _git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise ReviewCheckError("git inspection failed")
    return result


def _status_records(root: Path) -> list[dict[str, str]]:
    payload = _git(
        root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    ).stdout
    records = []
    for field in payload.split(b"\0"):
        if not field:
            continue
        text = field.decode("utf-8")
        if len(text) < 4:
            raise ReviewCheckError("invalid Git status record")
        status_code = text[:2]
        if "R" in status_code or "C" in status_code:
            raise ReviewCheckError("renamed or copied paths are not allowed")
        records.append({"status": status_code, "path": text[3:]})
    return sorted(records, key=lambda row: row["path"])


def _changed_paths(root: Path) -> list[str]:
    records = _status_records(root)
    removed = [row["path"] for row in records if "D" in row["status"]]
    if removed:
        raise ReviewCheckError(f"removed path is not allowed: {removed[0]}")
    return [row["path"] for row in records]


def _allowed(path: str) -> bool:
    return path in APPROVED_EXACT or any(
        path.startswith(prefix) for prefix in APPROVED_PREFIXES
    )


def _require_scope(root: Path) -> list[str]:
    paths = _changed_paths(root)
    unexpected = [path for path in paths if not _allowed(path)]
    if unexpected:
        raise ReviewCheckError(f"path outside approved scope: {unexpected[0]}")
    return paths


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD").stdout.decode().strip()


def _safe_controls(root: Path) -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    for key in SAFE_CONTROL_KEYS:
        result = _git(root, "config", "--get", key, check=False)
        if result.returncode not in {0, 1}:
            raise ReviewCheckError("Git control inspection failed")
        values[key] = result.stdout.decode().strip() if result.returncode == 0 else None
    attributes = root / ".gitattributes"
    values[".gitattributes"] = (
        hashlib.sha256(attributes.read_bytes()).hexdigest()
        if attributes.is_file() and not attributes.is_symlink()
        else None
    )
    return values


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _target_index_identity(root: Path) -> dict[str, Any]:
    value = _git(root, "rev-parse", "--git-path", "index").stdout.decode().strip()
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    if path.is_symlink() or not path.is_file():
        raise ReviewCheckError("target index must be a regular file")
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


def check_inventory(root: Path) -> dict[str, Any]:
    paths = _require_scope(root)
    return {"count": len(paths), "files": build_inventory(root, paths)}


def check_identity(root: Path, base: str) -> dict[str, Any]:
    head = _head(root)
    if head != base:
        raise ReviewCheckError("candidate HEAD does not match base")
    if _git(root, "diff", "--cached", "--quiet", check=False).returncode != 0:
        raise ReviewCheckError("candidate ordinary index is not clean")
    ref_result = _git(root, "symbolic-ref", "-q", "HEAD", check=False)
    if ref_result.returncode != 0:
        raise ReviewCheckError("candidate target ref is detached or unavailable")
    ref = ref_result.stdout.decode().strip()
    paths = _require_scope(root)
    inventory = build_inventory(root, paths)
    files = [row for row in inventory if not row["path"].startswith(RECORD_PREFIX)]
    records = [row for row in inventory if row["path"].startswith(RECORD_PREFIX)]
    subject = {
        "base": base,
        "files": files,
        "wip_commits": [],
        "wip_parent": base,
    }
    candidate_id = hashlib.sha256(_canonical_bytes(subject)).hexdigest()
    status_payload = {
        "paths": paths,
        "records": _status_records(root),
    }
    return {
        "base": base,
        "candidate_id": candidate_id,
        "files": files,
        "records": records,
        "complete_paths": paths,
        "count": len(paths),
        "target": {
            "head": head,
            "ref": ref,
            "index": _target_index_identity(root),
            "status_sha256": hashlib.sha256(
                _canonical_bytes(status_payload)
            ).hexdigest(),
            "staged_empty": True,
        },
    }


def _git_tree_records(root: Path, tree: str, path: str = "") -> dict[str, dict[str, str]]:
    arguments = ["ls-tree", "-r", "-z", tree]
    if path:
        arguments.extend(["--", path])
    payload = _git(root, *arguments).stdout
    records = {}
    for value in payload.split(b"\0"):
        if not value:
            continue
        metadata, raw_path = value.split(b"\t", maxsplit=1)
        mode, kind, oid = metadata.decode("ascii").split(" ")
        relative = raw_path.decode("utf-8")
        records[relative] = {"mode": mode, "kind": kind, "oid": oid}
    return records


def check_preservation(root: Path, base: str) -> dict[str, Any]:
    paths = _require_scope(root)
    base_data = _git_tree_records(root, base, "data")
    checked = 0
    for relative, expected in base_data.items():
        if relative in PRESERVED_DATA_EXCEPTIONS:
            continue
        path = _regular_path(root, relative)
        payload = path.read_bytes()
        if (
            expected["kind"] != "blob"
            or expected["mode"] != _file_git_mode(path)
            or expected["oid"] != _git_object_oid("blob", payload)
        ):
            raise ReviewCheckError(f"preserved payload changed: {relative}")
        checked += 1
    base_frozen = {
        relative
        for relative in base_data
        if relative.startswith(FROZEN_ROOTS)
    }
    actual_frozen = set()
    for relative_root in FROZEN_ROOTS:
        frozen_root = root / relative_root
        for path in frozen_root.rglob("*"):
            if path.is_symlink():
                raise ReviewCheckError(f"symlink is not allowed: {relative_root}")
            if path.is_file():
                actual_frozen.add(path.relative_to(root).as_posix())
    extras = sorted(
        relative
        for relative in actual_frozen - base_frozen
        if not _allowed(relative)
    )
    if extras:
        raise ReviewCheckError(f"unexpected frozen payload: {extras[0]}")
    return {
        "base": base,
        "checked_payloads": checked,
        "checked_roots": list(FROZEN_ROOTS),
        "changed_paths": paths,
    }


def check_frozen_oids(root: Path) -> dict[str, Any]:
    source = _regular_path(root, "tests/test_frozen_public_evidence_pins.py")
    module = ast.parse(source.read_text(encoding="utf-8"))
    values: dict[str, Any] = {}
    for node in module.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {"PINS", "FROZEN_TREE_OIDS"}:
                values[target.id] = ast.literal_eval(node.value)
    pins = values.get("PINS")
    oids = values.get("FROZEN_TREE_OIDS")
    if not isinstance(pins, dict) or not isinstance(oids, dict):
        raise ReviewCheckError("frozen pin declarations are missing")
    for relative, expected in pins.items():
        payload = _regular_path(root, relative).read_bytes()
        if [hashlib.sha256(payload).hexdigest(), len(payload)] != list(expected):
            raise ReviewCheckError(f"frozen byte pin mismatch: {relative}")
    computed = {}
    for relative in oids:
        identity = canonical_tree_identity(root / relative)
        computed[relative] = {
            "oid": identity["oid"],
            "count": identity["count"],
        }
    return {
        "byte_pins": len(pins),
        "tree_oids": computed,
    }


def check_compare(root: Path, mirror: Path, base: str) -> dict[str, Any]:
    paths = _require_scope(root)
    problems = compare_inventory(root, mirror, paths)
    if problems:
        raise ReviewCheckError(problems[0])
    mirror_head = _head(mirror)
    mirror_base = _git(mirror, "merge-base", mirror_head, base).stdout.decode().strip()
    if mirror_base != base:
        raise ReviewCheckError("mirror is not based on approved base")
    committed = {
        value.decode("utf-8")
        for value in _git(
            mirror,
            "diff",
            "--name-only",
            "-z",
            base,
            mirror_head,
        ).stdout.split(b"\0")
        if value
    }
    worktree = set(_changed_paths(mirror))
    mirror_paths = committed | worktree
    if mirror_paths != set(paths):
        raise ReviewCheckError("mirror changed-path set mismatch")
    return {"base": base, "paths": len(paths), "mirror_head": mirror_head}


def check_tree(root: Path, base: str, tree: str) -> dict[str, Any]:
    paths = _require_scope(root)
    base_paths = set(
        _git(root, "ls-tree", "-r", "--name-only", base).stdout.decode().splitlines()
    )
    expected_paths = base_paths | set(paths)
    tree_paths = set(
        _git(root, "ls-tree", "-r", "--name-only", tree).stdout.decode().splitlines()
    )
    if tree_paths != expected_paths:
        raise ReviewCheckError("candidate tree path set mismatch")
    tree_changes = set(
        _git(
            root,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            base,
            tree,
        ).stdout.decode().splitlines()
    )
    if tree_changes != set(paths):
        raise ReviewCheckError("candidate tree changed-path set mismatch")
    tree_records = _git_tree_records(root, tree)
    for relative in paths:
        path = _regular_path(root, relative)
        expected = tree_records.get(relative)
        if expected is None or expected["mode"] != _file_git_mode(path):
            raise ReviewCheckError(f"candidate tree mode mismatch: {relative}")
        payload = _git(root, "cat-file", "blob", f"{tree}:{relative}").stdout
        if payload != path.read_bytes():
            raise ReviewCheckError(f"candidate tree content mismatch: {relative}")
    return {"base": base, "tree": tree, "paths": len(paths)}


def workspace_region_problems(
    regions_payload: dict[str, Any],
    coverage_payload: dict[str, Any],
) -> list[str]:
    regions = regions_payload.get("regions")
    matrices = coverage_payload.get("matrices")
    if not isinstance(regions, dict) or not isinstance(matrices, list):
        return ["region or coverage mapping is missing"]
    expected: dict[str, list[list[int]]] = {}
    for matrix in matrices:
        if not isinstance(matrix, dict):
            return ["coverage matrix is invalid"]
        locale = matrix.get("locale")
        viewport = matrix.get("viewport")
        before_root = matrix.get("before")
        after_root = matrix.get("after")
        if not isinstance(before_root, dict) or not isinstance(after_root, dict):
            return ["workspace coverage section is invalid"]
        before = before_root.get("workspaces")
        after = after_root.get("workspaces")
        if (
            not isinstance(locale, str)
            or not isinstance(viewport, str)
            or not isinstance(before, dict)
            or not isinstance(after, dict)
            or set(before) != set(after)
        ):
            return ["workspace coverage identity is invalid"]
        for screen in sorted(before):
            left = before[screen].get("authority_rectangle")
            right = after[screen].get("authority_rectangle")
            if (
                not isinstance(left, list)
                or len(left) != 4
                or not isinstance(right, list)
                or len(right) != 4
                or not all(isinstance(value, int) for value in [*left, *right])
            ):
                return [f"workspace coverage rectangle is invalid: {screen}"]
            key = f"{locale}/{viewport}/{screen}.webp"
            if key in expected:
                return [f"duplicate workspace coverage identity: {key}"]
            expected[key] = [
                [
                    min(left[0], right[0]),
                    min(left[1], right[1]),
                    max(left[2], right[2]),
                    max(left[3], right[3]),
                ]
            ]
    actual_keys = {
        key for key in regions if isinstance(key, str) and "workspace" in key
    }
    problems = []
    if actual_keys != set(expected):
        problems.append("workspace region identity set mismatch")
    for key in sorted(actual_keys & set(expected)):
        if regions[key] != expected[key]:
            problems.append(f"workspace region mismatch: {key}")
    return problems


def check_workspace_region_coverage(
    regions_path: Path,
    coverage_path: Path,
) -> dict[str, int]:
    regions_payload = _load_json(regions_path)
    coverage_payload = _load_json(coverage_path)
    problems = workspace_region_problems(regions_payload, coverage_payload)
    if problems:
        raise ReviewCheckError(problems[0])
    regions = regions_payload["regions"]
    workspace_count = sum("workspace" in key for key in regions)
    if workspace_count != 36 or len(regions) != 44:
        raise ReviewCheckError("visual region count mismatch")
    return {"workspace_regions": workspace_count, "total_regions": len(regions)}


def registered_metrics(reference: Any, candidate: Any, rectangles: list[list[int]]) -> dict[str, Any]:
    from PIL import ImageDraw
    from browser_tests.visual_baselines import compare_images

    left = reference.convert("RGB").copy()
    right = candidate.convert("RGB").copy()
    if left.size != right.size:
        raise ReviewCheckError("registered image dimensions differ")
    for image in (left, right):
        draw = ImageDraw.Draw(image)
        for rectangle in rectangles:
            draw.rectangle(tuple(rectangle), fill=(0, 0, 0))
    return compare_images(left, right)


AM4_BASE = "f671f36fe6ea56b2c009ede91847b7dbf950a939"
AM4_REFERENCE_MANIFEST = "90ddfa015a6093048e235abe699cae570ef78d12e386c4266f59c39271c11164"
AM4_CANDIDATE_MANIFEST = "4fd90577afe863b290cdff4a8932bc6627918c72e9834ef6c4ed01c248cdae16"
AM4_REGIONS = "fcfb531d903b8bfd8e3b5384e700b416ae766f78641a8cddba8261fa99f46c8d"
AM4_CAPTURE_SOURCE = "browser_tests/test_s15b_selection.py"
AM4_VIEWPORTS = {"desktop-1440x900": [1440, 900], "tablet-1024x768": [1024, 768]}
AM4_PAINT_KEYS = frozenset((
    "fontFamily", "fontSize", "fontWeight", "fontStyle", "fontStretch",
    "fontFeatureSettings", "lineHeight", "letterSpacing", "wordSpacing",
    "whiteSpace", "textTransform", "color", "backgroundColor",
    "backgroundImage", "borderTop", "borderRight", "borderBottom",
    "borderLeft", "boxShadow", "opacity", "filter", "backdropFilter",
))


def _phase_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _phase_style_map(value: Any) -> bool:
    return isinstance(value, dict) and all(
        isinstance(key, str) and key
        and isinstance(item, dict) and set(item) == {"value", "priority"}
        and isinstance(item["value"], str)
        and item["priority"] in ("", "important")
        for key, item in value.items()
    )


def _phase_snapshot_errors(snapshot: Any, name: str, expected_state: dict[str, Any]) -> list[str]:
    required = {
        "top", "scroll", "scroll_max", "viewport_size", "margin", "dpr",
        "font_status", "width", "height", "local", "header", "state", "dom",
        "styles", "document", "element_style", "root_style",
        "element_style_map", "root_style_map", "element_margin_top",
    }
    if not isinstance(snapshot, dict) or required - snapshot.keys():
        return [f"{name} required snapshot fields missing"]
    numbers = ("top", "scroll", "scroll_max", "margin", "dpr", "width", "height", "element_margin_top")
    if any(not _phase_number(snapshot[key]) for key in numbers):
        return [f"{name} non-finite or invalid geometry"]
    errors = []
    if snapshot["dpr"] != 1 or snapshot["font_status"] != "loaded":
        errors.append(f"{name} runtime state invalid")
    viewport = AM4_VIEWPORTS.get(expected_state.get("viewport"))
    actual_viewport = snapshot["viewport_size"]
    if (
        viewport is None or not isinstance(actual_viewport, list)
        or len(actual_viewport) != 2
        or any(type(value) is not int for value in actual_viewport)
        or actual_viewport != viewport
    ):
        errors.append(f"{name} viewport mismatch")
    if snapshot["width"] <= 0 or snapshot["height"] <= 0:
        errors.append(f"{name} section dimensions invalid")
    if not 0 < snapshot["scroll"] < snapshot["scroll_max"]:
        errors.append(f"{name} scroll is clamped")
    state = snapshot["state"]
    if (
        not isinstance(state, dict) or state != expected_state
        or type(state.get("synthetic_disclosure")) is not bool
        or type(state.get("synthetic_label_count")) is not int
    ):
        errors.append(f"{name} observed state mismatch")
    document = snapshot["document"]
    if (
        not isinstance(document, dict)
        or set(document) != {"lang", "dir", "body_class", "body_aria_busy"}
        or document.get("lang") != expected_state.get("locale")
        or document.get("dir") != {"en": "ltr", "ar": "rtl"}.get(expected_state.get("locale"))
        or not isinstance(document.get("body_class"), str)
        or document.get("body_aria_busy") != "false"
    ):
        errors.append(f"{name} document state invalid")
    dom = snapshot["dom"]
    if (
        not isinstance(dom, dict) or set(dom) != {"roots", "controls", "stylesheets"}
        or not isinstance(dom.get("roots"), list) or len(dom["roots"]) != 3
        or any(not isinstance(value, str) or not value for value in dom["roots"])
        or not isinstance(dom.get("controls"), dict)
        or not isinstance(dom.get("stylesheets"), list) or not dom["stylesheets"]
    ):
        errors.append(f"{name} DOM proof incomplete")
    elif expected_state.get("view") == "workspace":
        control = dom["controls"].get("opportunity-select")
        if not isinstance(control, dict) or control.get("value") != expected_state["selected_id"]:
            errors.append(f"{name} selected control mismatch")
    styles = snapshot["styles"]
    if not isinstance(styles, list) or not styles:
        errors.append(f"{name} paint proof missing")
    else:
        for item in styles:
            if (
                not isinstance(item, dict) or set(item) != {"path", "tag", "rect", "values"}
                or not isinstance(item.get("path"), str) or not isinstance(item.get("tag"), str)
                or not isinstance(item.get("rect"), list) or len(item["rect"]) != 4
                or any(not _phase_number(value) for value in item["rect"])
                or item["rect"][2] < 0 or item["rect"][3] < 0
                or not isinstance(item.get("values"), dict) or set(item["values"]) != AM4_PAINT_KEYS
                or any(not isinstance(value, str) for value in item["values"].values())
            ):
                errors.append(f"{name} paint proof malformed")
                break
    local = snapshot["local"]
    if not isinstance(local, list) or not local:
        errors.append(f"{name} local geometry missing")
    else:
        for item in local:
            if (
                not isinstance(item, list) or len(item) != 7
                or not isinstance(item[0], str) or not isinstance(item[1], str)
                or type(item[2]) is not int or item[2] < 0
                or any(not _phase_number(value) for value in item[3:])
                or item[5] < 0 or item[6] < 0
            ):
                errors.append(f"{name} local geometry malformed")
                break
    header = snapshot["header"]
    if (
        not isinstance(header, list) or len(header) != 2
        or any(not isinstance(row, list) or len(row) != 4 or any(not _phase_number(value) for value in row) for row in header)
    ):
        errors.append(f"{name} chrome geometry missing")
    for key in ("element_style", "root_style"):
        if snapshot[key] is not None and not isinstance(snapshot[key], str):
            errors.append(f"{name} style attribute invalid: {key}")
    for key in ("element_style_map", "root_style_map"):
        if not _phase_style_map(snapshot[key]):
            errors.append(f"{name} style map invalid: {key}")
    return errors


def phase_record_problems(record: dict[str, Any], *, expected_state: dict[str, Any]) -> list[str]:
    if not isinstance(record, dict) or not isinstance(expected_state, dict) or not expected_state:
        return ["phase record or trusted state invalid"]
    problems = []
    for key in ("reference_link_exact", "candidate_link_exact", "restoration_rgb_exact", "raw_drift_nonzero"):
        if record.get(key) is not True:
            problems.append(f"phase record predicate failed: {key}")
    metrics = record.get("registered_metrics")
    if not isinstance(metrics, dict) or metrics.get("passes") is not True:
        problems.append("registered metrics failed")
    for name in ("reference", "candidate", "adjusted", "restored"):
        problems.extend(_phase_snapshot_errors(record.get(name), name, expected_state))
    if problems:
        return problems
    reference, candidate, adjusted, restored = (record[name] for name in ("reference", "candidate", "adjusted", "restored"))
    delta = record.get("delta")
    if not _phase_number(delta) or delta != candidate["top"] - reference["top"] or abs(delta) >= 1:
        return ["phase delta relation invalid"]
    if reference["margin"] != candidate["margin"]:
        problems.append("computed scroll margins differ")
    for name, snapshot in (("reference", reference), ("candidate", candidate)):
        if abs(snapshot["top"] - snapshot["margin"]) > 0.5:
            problems.append(f"{name} phase is outside rounding interval")
    if adjusted["top"] != candidate["top"] or adjusted["scroll"] != reference["scroll"]:
        problems.append("registration origin or scroll mismatch")
    cross_version = ("state", "dom", "styles", "width", "height", "header", "font_status", "dpr", "document", "viewport_size", "element_margin_top", "element_style_map")
    for key in cross_version:
        if reference[key] != candidate[key]:
            problems.append(f"cross-version mismatch: {key}")
    registration = ("state", "dom", "styles", "local", "width", "height", "header", "font_status", "dpr", "document", "viewport_size")
    for key in registration:
        if reference[key] != adjusted[key]:
            problems.append(f"registration changed: {key}")
    expected_element = dict(reference["element_style_map"])
    margin = adjusted["element_style_map"].get("margin-top")
    if not isinstance(margin, dict) or not margin["value"].endswith("px") or margin["priority"] != "":
        problems.append("registration margin declaration invalid")
    else:
        try:
            value = float(margin["value"][:-2])
        except ValueError:
            value = float("nan")
        if not _phase_number(value) or value != reference["element_margin_top"] + delta:
            problems.append("registration margin value invalid")
        expected_element["margin-top"] = margin
    if adjusted["element_margin_top"] != reference["element_margin_top"] + delta:
        problems.append("registration computed margin mismatch")
    if adjusted["element_style_map"] != expected_element:
        problems.append("registration changed unrelated element styles")
    expected_root = dict(reference["root_style_map"])
    expected_root.update({
        "overflow-anchor": {"value": "none", "priority": ""},
        "scroll-behavior": {"value": "auto", "priority": ""},
    })
    if adjusted["root_style_map"] != expected_root:
        problems.append("registration changed unrelated root styles")
    for key in reference:
        if reference[key] != restored.get(key):
            problems.append(f"restoration changed: {key}")
    return problems


def phase_expected_state(entry: dict[str, Any]) -> dict[str, Any]:
    locale, viewport, mode = (entry.get(key) for key in ("locale", "viewport", "mode"))
    if locale not in ("en", "ar") or viewport not in AM4_VIEWPORTS or mode not in ("public", "simulated"):
        raise ReviewCheckError("phase manifest state is invalid")
    screen, case_id = entry.get("screen"), entry.get("case_id")
    workspace_ids = {
        "SAU-H0-721049", "SAU-H0-390210", "SAU-H6-721061", "SAU-H6-721012",
        "SAU-H6-760711", "SAU-H6-760429", "SAU-H6-392010",
    }
    screening_screens = {
        "journey-f-screening-summary", "journey-f-screening-queue-robust",
        "journey-f-screening-queue-empty", "journey-f-screening-record",
    }
    if isinstance(screen, str) and screen.endswith("-workspace") and case_id in workspace_ids:
        if mode == "simulated" and case_id not in ("SAU-H0-721049", "SAU-H0-390210"):
            raise ReviewCheckError("phase workspace mode is not in the approved matrix")
        selected_id, hs6, view = case_id, case_id.rsplit("-", 1)[-1], "workspace"
        real_state = "REJECT" if case_id == "SAU-H0-390210" else "INVESTIGATE"
        active_state = "ADVANCE" if mode == "simulated" and case_id == "SAU-H0-721049" else real_state
    elif screen in screening_screens and mode == "public":
        if screen == "journey-f-screening-record":
            if not isinstance(case_id, str) or len(case_id) != 6 or not case_id.isascii() or not case_id.isdigit():
                raise ReviewCheckError("phase screening HS6 is invalid")
        elif case_id is not None:
            raise ReviewCheckError("phase screening case identity is invalid")
        selected_id, hs6, view, real_state, active_state = None, case_id, screen, None, None
    else:
        raise ReviewCheckError("phase screen is outside the approved matrix")
    return {
        "selected_id": selected_id, "hs6": hs6, "mode": mode,
        "real_state": real_state, "active_state": active_state,
        "synthetic_disclosure": mode == "simulated",
        "synthetic_label_count": 2 if mode == "simulated" else 0,
        "locale": locale, "viewport": viewport, "view": view,
    }


def phase_read_rgb(path: Path, dimensions: list[int], *, format_name: str):
    from PIL import Image

    with Image.open(path) as image:
        image.load()
        if image.size != tuple(dimensions) or image.format != format_name or getattr(image, "n_frames", 1) != 1:
            raise ReviewCheckError("phase image dimensions or format mismatch")
        if image.mode == "RGB":
            return image.copy()
        if format_name == "PNG" and image.mode == "RGBA" and image.getchannel("A").getextrema() == (255, 255):
            return image.convert("RGB")
        raise ReviewCheckError("phase image must be opaque RGB")


def phase_bound_manifest(root: Path, expected_digest: str, expected_count: int) -> dict[str, Any]:
    manifest_path = _regular_path(root, "manifest.json")
    digest_path = _regular_path(root, "manifest.sha256")
    if sha256_file(manifest_path) != expected_digest or digest_path.read_text(encoding="ascii").strip() != expected_digest:
        raise ReviewCheckError("phase manifest is not the approved subject")
    manifest = _load_json(manifest_path)
    project = root.parents[2]
    for key in ("source_tree", "font_hashes"):
        values = manifest.get(key)
        if not isinstance(values, dict) or not values:
            raise ReviewCheckError("phase source provenance is missing")
        for relative, digest in values.items():
            if sha256_file(_regular_path(project, relative)) != digest:
                raise ReviewCheckError(f"phase source provenance is stale: {relative}")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != expected_count:
        raise ReviewCheckError("phase manifest entry count is invalid")
    paths = [entry["path"] for entry in entries]
    if len(set(paths)) != len(paths):
        raise ReviewCheckError("phase manifest has duplicate paths")
    discovered = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ReviewCheckError("phase baseline contains a symlink")
        if path.is_file():
            discovered.add(path.relative_to(root).as_posix())
    if discovered != set(paths) | {"manifest.json", "manifest.sha256"}:
        raise ReviewCheckError("phase baseline file inventory differs")
    total = 0
    for entry in entries:
        path = _regular_path(root, entry["path"])
        dimensions = AM4_VIEWPORTS.get(entry["viewport"])
        size = path.stat().st_size
        if dimensions is None or entry["dimensions"] != dimensions or size != entry["bytes"] or size > 600 * 1024 or sha256_file(path) != entry["sha256"]:
            raise ReviewCheckError("phase baseline image binding differs")
        if path.read_bytes()[:16][8:16] != b"WEBPVP8L":
            raise ReviewCheckError("phase baseline is not lossless WebP")
        phase_read_rgb(path, dimensions, format_name="WEBP")
        total += size
    if total > 16 * 1024 * 1024:
        raise ReviewCheckError("phase baseline exceeds the approved budget")
    return manifest


def phase_binding_problems(bindings: Any) -> list[str]:
    expected = {
        "base": AM4_BASE,
        "reference_manifest_sha256": AM4_REFERENCE_MANIFEST,
        "candidate_manifest_sha256": AM4_CANDIDATE_MANIFEST,
        "regions_sha256": AM4_REGIONS,
        "capture_source": AM4_CAPTURE_SOURCE,
        "browser_version": "151.0.7922.34",
        "chromium_revision": "chromium-1234",
        "playwright_version": "1.62.0",
        "pytest_playwright_version": "0.9.0",
        "launch_flags": ["--font-render-hinting=none", "--disable-lcd-text", "--force-color-profile=srgb"],
    }
    if not isinstance(bindings, dict):
        return ["phase bindings missing"]
    return [f"phase approved binding differs: {key}" for key, value in expected.items() if bindings.get(key) != value]


def visual_summary(root: Path, baseline: Path | None = None) -> dict[str, Any]:
    from PIL import Image

    manifest = _load_json(root / "manifest.json")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ReviewCheckError("visual manifest entries are invalid")
    expected = {entry.get("path") for entry in entries if isinstance(entry, dict)}
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.webp")
        if path.is_file() and not path.is_symlink()
    }
    if None in expected or len(expected) != len(entries) or actual != expected:
        raise ReviewCheckError("visual manifest path set mismatch")
    total = 0
    maximum = {"path": "", "bytes": -1}
    owners = set()
    for entry in entries:
        path = _regular_path(root, entry["path"])
        payload = path.read_bytes()
        owners.add(path.stat().st_uid)
        if (
            len(payload) != entry.get("bytes")
            or hashlib.sha256(payload).hexdigest() != entry.get("sha256")
            or payload[12:16] != b"VP8L"
        ):
            raise ReviewCheckError(f"visual entry integrity mismatch: {entry['path']}")
        with Image.open(path) as image:
            if image.mode != "RGB" or list(image.size) != entry.get("dimensions"):
                raise ReviewCheckError(f"visual entry decode mismatch: {entry['path']}")
        total += len(payload)
        if len(payload) > maximum["bytes"]:
            maximum = {"path": entry["path"], "bytes": len(payload)}
    result = {
        "entries": len(entries),
        "total_bytes": total,
        "maximum": maximum,
        "owner_uids": sorted(owners),
        "expected_uid": os.getuid(),
    }
    if baseline is not None:
        before = {
            path.relative_to(baseline).as_posix()
            for path in baseline.rglob("*.webp")
            if path.is_file() and not path.is_symlink()
        }
        result.update(
            {
                "retained_paths": len(before & actual),
                "added_paths": len(actual - before),
                "removed_paths": len(before - actual),
            }
        )
    return result


def _difference_stats(difference: Any) -> dict[str, Any]:
    from PIL import ImageChops
    from scripts.visual_metrics import calculate_metrics

    red, green, blue = difference.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    histogram = maximum.histogram()
    changed_pixels = sum(histogram[1:])
    max_delta = max(
        (value for value, count in enumerate(histogram) if count),
        default=0,
    )
    significant = sum(histogram[9:])
    channel_error = sum(
        value * count
        for channel in (red, green, blue)
        for value, count in enumerate(channel.histogram())
    )
    metrics = calculate_metrics(
        significant_pixels=significant,
        total_pixels=difference.width * difference.height,
        absolute_channel_error=channel_error,
        dimensions=difference.size,
    )
    return {
        "bbox": list(difference.getbbox()) if difference.getbbox() else None,
        "changed_pixels": changed_pixels,
        "max_delta": max_delta,
        "metrics": metrics,
    }


def visual_residual_report(
    before: Path,
    after: Path,
    regions_path: Path,
) -> dict[str, Any]:
    from PIL import Image, ImageChops, ImageDraw

    regions = _load_json(regions_path).get("regions")
    if not isinstance(regions, dict):
        raise ReviewCheckError("visual regions mapping is required")
    before_files = {
        path.relative_to(before).as_posix(): path
        for path in before.rglob("*.webp")
        if path.is_file() and not path.is_symlink()
    }
    after_files = {
        path.relative_to(after).as_posix(): path
        for path in after.rglob("*.webp")
        if path.is_file() and not path.is_symlink()
    }
    rows = []
    for relative in sorted(set(before_files) & set(after_files)):
        old = Image.open(before_files[relative]).convert("RGB")
        new = Image.open(after_files[relative]).convert("RGB")
        if old.size != new.size:
            raise ReviewCheckError(f"visual size mismatch: {relative}")
        difference = ImageChops.difference(old, new)
        if difference.getbbox() is None:
            continue
        mask = Image.new("L", old.size, 0)
        draw = ImageDraw.Draw(mask)
        for rectangle in regions.get(relative, []):
            draw.rectangle(tuple(rectangle), fill=255)
        outside = ImageChops.multiply(
            difference,
            ImageChops.invert(mask).convert("RGB"),
        )
        outside_stats = _difference_stats(outside)
        if outside_stats["bbox"] is None:
            continue
        rows.append(
            {
                "path": relative,
                "overall": _difference_stats(difference),
                "outside": outside_stats,
            }
        )
    return {
        "residual_count": len(rows),
        "rows": rows,
    }


def diagnostic_residual_report(
    coverage_path: Path,
    regions_path: Path,
    section: str,
) -> dict[str, Any]:
    from PIL import Image, ImageChops, ImageDraw

    coverage = _load_json(coverage_path)
    regions = _load_json(regions_path).get("regions")
    matrices = coverage.get("matrices")
    if not isinstance(regions, dict) or not isinstance(matrices, list):
        raise ReviewCheckError("diagnostic coverage is invalid")
    rows = []
    for matrix in matrices:
        locale = matrix.get("locale")
        viewport = matrix.get("viewport")
        before = matrix.get("before", {}).get(section)
        after = matrix.get("after", {}).get(section)
        if not isinstance(before, dict) or not isinstance(after, dict):
            continue
        for screen in sorted(set(before) & set(after)):
            old = Image.open(before[screen]["screenshot"]).convert("RGB")
            new = Image.open(after[screen]["screenshot"]).convert("RGB")
            difference = ImageChops.difference(old, new)
            key = f"{locale}/{viewport}/{screen}.webp"
            outside = difference
            if section == "workspaces":
                mask = Image.new("L", old.size, 0)
                draw = ImageDraw.Draw(mask)
                for rectangle in regions.get(key, []):
                    draw.rectangle(tuple(rectangle), fill=255)
                outside = ImageChops.multiply(
                    difference,
                    ImageChops.invert(mask).convert("RGB"),
                )
            rows.append(
                {
                    "path": key,
                    "before_rectangle": before[screen].get(
                        "authority_rectangle",
                        before[screen].get("catalogue_rectangle"),
                    ),
                    "after_rectangle": after[screen].get(
                        "authority_rectangle",
                        after[screen].get("catalogue_rectangle"),
                    ),
                    "overall": _difference_stats(difference),
                    "outside": _difference_stats(outside),
                }
            )
    changed = [row for row in rows if row["overall"]["bbox"] is not None]
    outside = [row for row in rows if row["outside"]["bbox"] is not None]
    return {
        "section": section,
        "pairs": len(rows),
        "changed_pairs": len(changed),
        "outside_pairs": len(outside),
        "rows": rows,
    }


def check_visual_phase_drift(
    before: Path,
    after: Path,
    regions_path: Path,
    coverage_path: Path,
) -> dict[str, Any]:
    import importlib.metadata
    from PIL import Image, ImageChops, ImageDraw

    coverage = _load_json(coverage_path)
    bindings = coverage.get("bindings")
    binding_errors = phase_binding_problems(bindings)
    if binding_errors:
        raise ReviewCheckError(binding_errors[0])
    if coverage.get("schema_version") != 1 or coverage.get("method") != "S15B_DOM_PHASE_1":
        raise ReviewCheckError("visual phase coverage schema is invalid")
    before_manifest = phase_bound_manifest(before, AM4_REFERENCE_MANIFEST, 76)
    after_manifest = phase_bound_manifest(after, AM4_CANDIDATE_MANIFEST, 96)
    reference_project = before.parents[2]
    candidate_project = after.parents[2]
    if (
        _git(reference_project, "rev-parse", "HEAD").stdout.decode().strip() != AM4_BASE
        or _git(reference_project, "status", "--porcelain=v1", "--untracked-files=all").stdout
    ):
        raise ReviewCheckError("phase reference worktree is not clean at the approved base")
    if regions_path.is_symlink() or not regions_path.is_file() or sha256_file(regions_path) != AM4_REGIONS:
        raise ReviewCheckError("visual phase regions are not the approved subject")
    regions = _load_json(regions_path).get("regions")
    if not isinstance(regions, dict) or len(regions) != 44 or sum("workspace" in key for key in regions) != 36:
        raise ReviewCheckError("visual phase region count mismatch")
    capture_source = _regular_path(candidate_project, AM4_CAPTURE_SOURCE)
    if bindings.get("capture_source_sha256") != sha256_file(capture_source):
        raise ReviewCheckError("visual phase capture source mismatch")
    if (
        importlib.metadata.version("playwright") != "1.62.0"
        or importlib.metadata.version("pytest-playwright") != "0.9.0"
    ):
        raise ReviewCheckError("visual phase installed runtime mismatch")
    if (
        coverage.get("common") != 76
        or coverage.get("registered_pairs") != 52
        or coverage.get("unadjusted_portfolio_pairs") != 8
        or coverage.get("identical_dossier_pairs") != 16
        or coverage.get("additions") != 20
        or coverage.get("removals") != 0
        or coverage.get("raw_strict_failure_retained") is not True
    ):
        raise ReviewCheckError("visual phase matrix accounting mismatch")
    before_entries = {entry["path"]: entry for entry in before_manifest["entries"]}
    after_entries = {entry["path"]: entry for entry in after_manifest["entries"]}
    common = set(before_entries) & set(after_entries)
    additions = set(after_entries) - set(before_entries)
    if len(common) != 76 or len(additions) != 20 or set(before_entries) - set(after_entries):
        raise ReviewCheckError("visual phase manifest path accounting mismatch")
    for path, rectangles in regions.items():
        entry = after_entries.get(path)
        if entry is None or not isinstance(rectangles, list) or not rectangles:
            raise ReviewCheckError("invalid visual region identity")
        width, height = entry["dimensions"]
        for rectangle in rectangles:
            if (
                not isinstance(rectangle, list) or len(rectangle) != 4
                or any(type(value) is not int for value in rectangle)
                or not (0 <= rectangle[0] < rectangle[2] <= width)
                or not (0 <= rectangle[1] < rectangle[3] <= height)
            ):
                raise ReviewCheckError("invalid visual region bounds")
    portfolio = {path for path in common if "journey-a-portfolio-" in path}
    dossiers = {path for path in common if "dossier" in path}
    registered = common - portfolio - dossiers
    records = coverage.get("records")
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ReviewCheckError("visual phase records are invalid")
    record_paths = [record.get("path") for record in records]
    if (
        len(portfolio) != 8 or len(dossiers) != 16 or len(registered) != 52
        or len(record_paths) != 52 or len(set(record_paths)) != 52
        or set(record_paths) != registered
    ):
        raise ReviewCheckError("visual phase record identity mismatch")
    for path in sorted(portfolio):
        dimensions = after_entries[path]["dimensions"]
        reference = phase_read_rgb(_regular_path(before, path), dimensions, format_name="WEBP")
        candidate = phase_read_rgb(_regular_path(after, path), dimensions, format_name="WEBP")
        difference = ImageChops.difference(reference, candidate)
        mask = Image.new("L", reference.size, 0)
        draw = ImageDraw.Draw(mask)
        for rectangle in regions.get(path, []):
            draw.rectangle(tuple(rectangle), fill=255)
        outside = ImageChops.multiply(difference, ImageChops.invert(mask).convert("RGB"))
        if outside.getbbox() is not None:
            raise ReviewCheckError(f"portfolio drift outside region: {path}")
    for path in sorted(dossiers):
        dimensions = after_entries[path]["dimensions"]
        reference = phase_read_rgb(_regular_path(before, path), dimensions, format_name="WEBP")
        candidate = phase_read_rgb(_regular_path(after, path), dimensions, format_name="WEBP")
        if ImageChops.difference(reference, candidate).getbbox() is not None:
            raise ReviewCheckError(f"dossier image changed: {path}")
    coverage_root = coverage_path.parent.resolve()
    reports = []
    for record in records:
        path = record["path"]
        entry = after_entries[path]
        dimensions = entry["dimensions"]
        reference_baseline = phase_read_rgb(_regular_path(before, path), dimensions, format_name="WEBP")
        candidate_baseline = phase_read_rgb(_regular_path(after, path), dimensions, format_name="WEBP")
        if (
            record.get("reference_baseline_sha256") != sha256_file(_regular_path(before, path))
            or record.get("candidate_baseline_sha256") != sha256_file(_regular_path(after, path))
        ):
            raise ReviewCheckError(f"phase baseline linkage mismatch: {path}")
        images = {}
        for key in ("reference_capture", "candidate_capture", "adjusted_capture", "restored_capture"):
            supplied = record.get(key)
            if not isinstance(supplied, str):
                raise ReviewCheckError(f"phase capture path missing: {path}")
            try:
                relative = Path(supplied).resolve().relative_to(coverage_root).as_posix()
            except ValueError as exc:
                raise ReviewCheckError(f"phase capture escapes root: {path}") from exc
            image_path = _regular_path(coverage_root, relative)
            if sha256_file(image_path) != record.get(f"{key}_sha256"):
                raise ReviewCheckError(f"phase capture hash mismatch: {path}")
            images[key] = phase_read_rgb(image_path, dimensions, format_name="PNG")
        reference_link = ImageChops.difference(images["reference_capture"], reference_baseline).getbbox() is None
        candidate_link = ImageChops.difference(images["candidate_capture"], candidate_baseline).getbbox() is None
        restoration_link = ImageChops.difference(images["reference_capture"], images["restored_capture"]).getbbox() is None
        raw_nonzero = ImageChops.difference(images["reference_capture"], images["candidate_capture"]).getbbox() is not None
        if (
            record.get("reference_link_exact") is not reference_link
            or record.get("candidate_link_exact") is not candidate_link
            or record.get("restoration_rgb_exact") is not restoration_link
            or record.get("raw_drift_nonzero") is not raw_nonzero
        ):
            raise ReviewCheckError(f"phase recorded image predicate mismatch: {path}")
        expected_state = phase_expected_state(entry)
        problems = phase_record_problems(record, expected_state=expected_state)
        if problems:
            raise ReviewCheckError(f"phase record invalid: {path}: {problems[0]}")
        metrics = registered_metrics(images["adjusted_capture"], images["candidate_capture"], regions.get(path, []))
        if metrics != record.get("registered_metrics") or metrics.get("passes") is not True:
            raise ReviewCheckError(f"registered metric mismatch: {path}")
        locale, viewport, filename = path.split("/", maxsplit=2)
        if (
            record.get("locale") != locale or record.get("viewport") != viewport
            or record.get("mode") != entry.get("mode") or record.get("case_id") != entry.get("case_id")
            or record.get("view") != expected_state["view"] or filename != f"{entry.get('screen')}.webp"
        ):
            raise ReviewCheckError(f"phase record state identity mismatch: {path}")
        reports.append({"path": path, "metrics": metrics, "delta": record["delta"]})
    required_negative = {"semantic_text", "paint_style", "missing_element"}
    negative = coverage.get("negative_proof")
    details = coverage.get("negative_details")
    if (
        not isinstance(negative, dict) or set(negative) != required_negative
        or any(value is not True for value in negative.values())
        or not isinstance(details, dict) or set(details) != required_negative
        or details.get("missing_element") != "PHASE_AUTHORITY_MISSING"
        or any(not isinstance(value, str) or not value for value in details.values())
    ):
        raise ReviewCheckError("visual phase negative proof is incomplete")
    new_views = coverage.get("new_views")
    expected_new = sorted((after_entries[path] for path in additions), key=lambda entry: entry["path"])
    if not isinstance(new_views, list) or new_views != expected_new or len({entry["path"] for entry in new_views}) != 20:
        raise ReviewCheckError("visual phase new-view identity mismatch")
    inspections = coverage.get("new_view_inspections")
    if (
        not isinstance(inspections, list) or len(inspections) != 20
        or len({item.get("path") for item in inspections if isinstance(item, dict)}) != 20
        or {item.get("path") for item in inspections if isinstance(item, dict)} != additions
        or any(
            not isinstance(item, dict) or item.get("format") != "WEBP" or item.get("mode") != "RGB"
            or item.get("dimensions") != after_entries[item.get("path")]["dimensions"]
            or not item.get("nonblank_bbox") or not item.get("channel_extrema")
            for item in inspections
        )
    ):
        raise ReviewCheckError("visual phase new-view inspection mismatch")
    reference_overview = _regular_path(reference_project, "src/ior_mvp/static/css/overview.css")
    candidate_overview = _regular_path(candidate_project, "src/ior_mvp/static/css/overview.css")
    reference_css = reference_overview.read_bytes()
    candidate_css = candidate_overview.read_bytes()
    if (
        not candidate_css.startswith(reference_css)
        or bindings.get("overview_reference_sha256") != hashlib.sha256(reference_css).hexdigest()
        or bindings.get("overview_candidate_sha256") != hashlib.sha256(candidate_css).hexdigest()
        or bindings.get("overview_suffix") != candidate_css[len(reference_css):].decode("utf-8")
    ):
        raise ReviewCheckError("visual phase stylesheet boundary mismatch")
    reference_styles = {
        path.name: sha256_file(path)
        for path in (reference_project / "src/ior_mvp/static/css").glob("*.css")
        if path.name != "overview.css"
    }
    candidate_styles = {
        path.name: sha256_file(path)
        for path in (candidate_project / "src/ior_mvp/static/css").glob("*.css")
        if path.name != "overview.css"
    }
    if reference_styles != candidate_styles or bindings.get("unchanged_stylesheets") != candidate_styles:
        raise ReviewCheckError("visual phase stylesheet source mismatch")
    if bindings.get("font_hashes") != after_manifest.get("font_hashes"):
        raise ReviewCheckError("visual phase font identity mismatch")
    return {
        "accepted_under_am4": True,
        "raw_strict_failure_retained": True,
        "common": len(common),
        "registered_pairs": len(reports),
        "unadjusted_portfolio_pairs": len(portfolio),
        "identical_dossier_pairs": len(dossiers),
        "additions": len(additions),
        "removals": 0,
        "records": reports,
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _visual_drift(before: Path, after: Path, regions_path: Path) -> dict[str, Any]:
    from PIL import Image, ImageChops, ImageDraw

    regions_payload = _load_json(regions_path)
    regions = regions_payload.get("regions")
    if not isinstance(regions, dict):
        raise ReviewCheckError("visual regions mapping is required")
    before_files = {
        path.relative_to(before).as_posix(): path
        for path in before.rglob("*.webp")
        if path.is_file() and not path.is_symlink()
    }
    after_files = {
        path.relative_to(after).as_posix(): path
        for path in after.rglob("*.webp")
        if path.is_file() and not path.is_symlink()
    }
    common = sorted(set(before_files) & set(after_files))
    changed = 0
    unknown = sorted(set(regions) - set(common))
    if unknown:
        raise ReviewCheckError(f"visual region has no common image: {unknown[0]}")
    for relative in common:
        old = Image.open(before_files[relative]).convert("RGB")
        new = Image.open(after_files[relative]).convert("RGB")
        if old.size != new.size:
            raise ReviewCheckError(f"visual size mismatch: {relative}")
        allowed = regions.get(relative)
        if allowed is not None:
            if not isinstance(allowed, list) or not allowed:
                raise ReviewCheckError(f"invalid visual region: {relative}")
            for rectangle in allowed:
                if (
                    not isinstance(rectangle, list)
                    or len(rectangle) != 4
                    or not all(
                        isinstance(value, int) and not isinstance(value, bool)
                        for value in rectangle
                    )
                    or not (
                        0 <= rectangle[0] < rectangle[2] <= old.width
                        and 0 <= rectangle[1] < rectangle[3] <= old.height
                    )
                ):
                    raise ReviewCheckError(
                        f"invalid visual region bounds: {relative}"
                    )
        difference = ImageChops.difference(old, new)
        if difference.getbbox() is None:
            continue
        changed += 1
        if allowed is None:
            raise ReviewCheckError(f"changed visual has no approved region: {relative}")
        mask = Image.new("L", old.size, 0)
        draw = ImageDraw.Draw(mask)
        for rectangle in allowed:
            draw.rectangle(tuple(rectangle), fill=255)
        outside = ImageChops.multiply(
            difference,
            ImageChops.invert(mask).convert("RGB"),
        )
        outside_box = outside.getbbox()
        if outside_box is not None:
            raise ReviewCheckError(
                f"visual drift outside approved region: {relative}: {outside_box}"
            )
    return {
        "common": len(common),
        "changed_common": changed,
        "unchanged_common": len(common) - changed,
        "outside_changed": 0,
        "added": len(set(after_files) - set(before_files)),
        "removed": len(set(before_files) - set(after_files)),
    }


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReviewCheckError("JSON control cannot be loaded") from exc
    if not isinstance(value, dict):
        raise ReviewCheckError("JSON control must be a mapping")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--root", type=Path, required=True)
    for name in ("identity", "preservation", "frozen-oids"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        if name != "frozen-oids":
            command.add_argument("--base", required=True)
    controls = commands.add_parser("controls")
    controls.add_argument("--root", type=Path, required=True)
    controls.add_argument("--mirror", type=Path, required=True)
    compare = commands.add_parser("compare")
    compare.add_argument("--root", type=Path, required=True)
    compare.add_argument("--mirror", type=Path, required=True)
    compare.add_argument("--base", required=True)
    tree = commands.add_parser("tree-compare")
    tree.add_argument("--root", type=Path, required=True)
    tree.add_argument("--base", required=True)
    tree.add_argument("--tree", required=True)
    visual = commands.add_parser("visual-drift")
    visual.add_argument("--before", type=Path, required=True)
    visual.add_argument("--after", type=Path, required=True)
    visual.add_argument("--regions", type=Path, required=True)
    coverage = commands.add_parser("region-coverage")
    coverage.add_argument("--regions", type=Path, required=True)
    coverage.add_argument("--coverage", type=Path, required=True)
    summary = commands.add_parser("visual-summary")
    summary.add_argument("--root", type=Path, required=True)
    summary.add_argument("--baseline", type=Path)
    residuals = commands.add_parser("visual-residuals")
    residuals.add_argument("--before", type=Path, required=True)
    residuals.add_argument("--after", type=Path, required=True)
    residuals.add_argument("--regions", type=Path, required=True)
    diagnostic = commands.add_parser("diagnostic-residuals")
    diagnostic.add_argument("--coverage", type=Path, required=True)
    diagnostic.add_argument("--regions", type=Path, required=True)
    diagnostic.add_argument(
        "--section",
        required=True,
        choices=("workspaces", "dossiers", "screening"),
    )
    phase = commands.add_parser("visual-phase-drift")
    phase.add_argument("--before", type=Path, required=True)
    phase.add_argument("--after", type=Path, required=True)
    phase.add_argument("--regions", type=Path, required=True)
    phase.add_argument("--coverage", type=Path, required=True)
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        if args.command == "inventory":
            result = check_inventory(args.root)
        elif args.command == "identity":
            result = check_identity(args.root, args.base)
        elif args.command == "preservation":
            result = check_preservation(args.root, args.base)
        elif args.command == "frozen-oids":
            result = check_frozen_oids(args.root)
        elif args.command == "controls":
            left = _safe_controls(args.root)
            right = _safe_controls(args.mirror)
            if not controls_match(left, right):
                raise ReviewCheckError("Git control mismatch")
            result = {"controls": left}
        elif args.command == "compare":
            result = check_compare(args.root, args.mirror, args.base)
        elif args.command == "tree-compare":
            result = check_tree(args.root, args.base, args.tree)
        elif args.command == "visual-drift":
            result = _visual_drift(args.before, args.after, args.regions)
        elif args.command == "region-coverage":
            result = check_workspace_region_coverage(
                args.regions,
                args.coverage,
            )
        elif args.command == "visual-summary":
            result = visual_summary(args.root, args.baseline)
        elif args.command == "visual-residuals":
            result = visual_residual_report(
                args.before,
                args.after,
                args.regions,
            )
        elif args.command == "diagnostic-residuals":
            result = diagnostic_residual_report(
                args.coverage,
                args.regions,
                args.section,
            )
        else:
            result = check_visual_phase_drift(
                args.before,
                args.after,
                args.regions,
                args.coverage,
            )
    except ReviewCheckError as exc:
        print(f"S15B REVIEW CHECK FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "PASS", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
