from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

from .config import PROJECT_ROOT


class CaseSelectionIntegrityError(ValueError):
    pass


def _parse(content: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CaseSelectionIntegrityError(f"{label} cannot be loaded") from exc
    if not isinstance(value, dict):
        raise CaseSelectionIntegrityError(f"{label} must be a mapping")
    return value


def _load(path: Path, label: str) -> dict[str, Any]:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise CaseSelectionIntegrityError(f"{label} cannot be loaded") from exc
    return _parse(content, label)


def _relative_file(root: Path, path: Path) -> str:
    canonical_root = root.resolve()
    if path.is_symlink() or not path.is_file():
        raise CaseSelectionIntegrityError("selection file must be regular")
    try:
        relative = path.resolve().relative_to(canonical_root).as_posix()
    except ValueError as exc:
        raise CaseSelectionIntegrityError("selection file escapes project") from exc
    return relative


def _validate_references(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "path":
                if not isinstance(child, str):
                    raise CaseSelectionIntegrityError("invalid reference path")
                parsed = PurePosixPath(child)
                if parsed.is_absolute() or ".." in parsed.parts or not parsed.parts:
                    raise CaseSelectionIntegrityError("invalid reference path")
            if key == "synthetic_flag" and child is not False:
                raise CaseSelectionIntegrityError("synthetic selection content")
            _validate_references(child)
    elif isinstance(value, list):
        for child in value:
            _validate_references(child)
    elif isinstance(value, float) and not math.isfinite(value):
        raise CaseSelectionIntegrityError("non-finite selection metric")


def _profile(record: dict[str, Any], name: str, selected: list[str]) -> dict[str, Any]:
    profiles = record.get("profiles")
    source = profiles.get(name) if isinstance(profiles, dict) else None
    if not isinstance(source, dict):
        raise CaseSelectionIntegrityError("selection profile is missing")
    if source.get("quota") != 2 or source.get("selected") != selected:
        raise CaseSelectionIntegrityError("selection profile selected set is invalid")
    rows = source.get("rows")
    substitutions = source.get("substitution_order")
    if (
        not isinstance(rows, list)
        or not all(isinstance(row, dict) for row in rows)
        or not isinstance(substitutions, list)
        or not all(isinstance(value, str) for value in substitutions)
    ):
        raise CaseSelectionIntegrityError("selection profile rows are invalid")
    identities = source.get("excluded_by_identity")
    gaps = source.get("excluded_series_gap_years")
    if (
        not isinstance(identities, list)
        or not all(
            isinstance(row, dict)
            and row.get("reason") == "RESIDUAL_CATCH_ALL_SUBHEADING"
            for row in identities
        )
        or not isinstance(gaps, list)
        or not all(
            isinstance(row, dict)
            and row.get("reason") == "SERIES_GAP_YEARS"
            and isinstance(row.get("missing_import_years"), list)
            for row in gaps
        )
    ):
        raise CaseSelectionIntegrityError("selection exclusion code is invalid")
    for key in ("excluded_by_viability", "excluded_frozen"):
        values = source.get(key)
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise CaseSelectionIntegrityError("selection exclusions are invalid")
    identifiers = [row.get("hs6") for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise CaseSelectionIntegrityError("duplicate selection row")
    selected_rows = [
        row.get("hs6")
        for row in rows
        if isinstance(row, dict) and row.get("selected") is True
    ]
    if selected_rows != selected:
        raise CaseSelectionIntegrityError("selection profile row set is invalid")
    projected = deepcopy(source)
    projected["profile"] = name
    return projected


def build_case_selection_view(
    *,
    selection_path: Path | None = None,
    manifest_path: Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    project_root = (root or PROJECT_ROOT).resolve()
    selection = selection_path or (
        project_root
        / "data/cases/selection/CASE-SELECTION-S15-b96de36ff0ce.json"
    )
    manifest = manifest_path or project_root / "data/manifests/snapshot_manifest.json"
    relative = _relative_file(project_root, selection)
    content = selection.read_bytes()
    manifest_record = _load(manifest, "snapshot manifest")
    rows = manifest_record.get("files")
    if not isinstance(rows, list):
        raise CaseSelectionIntegrityError("selection manifest files are invalid")
    matching = [
        row
        for row in rows
        if isinstance(row, dict) and row.get("path") == relative
    ]
    if len(matching) != 1:
        raise CaseSelectionIntegrityError("selection manifest row is missing")
    digest = hashlib.sha256(content).hexdigest()
    if matching[0].get("sha256") != digest or matching[0].get("bytes") != len(content):
        raise CaseSelectionIntegrityError("selection manifest hash mismatch")
    record = _parse(content, "case selection")
    if record.get("schema_version") != "1.1.0":
        raise CaseSelectionIntegrityError("selection schema is unsupported")
    if record.get("selection_id") != "CASE-SELECTION-S15-b96de36ff0ce":
        raise CaseSelectionIntegrityError("selection identity is invalid")
    if record.get("rule_version") != "S14-CS-1.1":
        raise CaseSelectionIntegrityError("selection rule version is invalid")
    expected = ["294110", "294120", "310430", "310510"]
    if record.get("selected_hs6") != expected:
        raise CaseSelectionIntegrityError("selection selected set is invalid")
    if record.get("owner_designated_cases") != []:
        raise CaseSelectionIntegrityError("owner designation set is invalid")
    _validate_references(record)
    profiles = [
        _profile(record, "pharma_api", expected[:2]),
        _profile(record, "fertilizers", expected[2:]),
    ]
    return {
        "schema_version": "1.0.0",
        "source_boundary": "public",
        "synthetic_flag": False,
        "selection_id": record["selection_id"],
        "rule_version": record["rule_version"],
        "selection_reference": {
            "path": relative,
            "sha256": digest,
        },
        "input_references": deepcopy(record["inputs"]),
        "profiles": profiles,
    }


@lru_cache(maxsize=1)
def case_selection_view() -> dict[str, Any]:
    return build_case_selection_view()


def clear_case_selection_view_cache() -> None:
    case_selection_view.cache_clear()
