"""Read-only loaders for acquired analytical snapshots (plan DD-15).

These loaders mirror ``ior_mvp.data_repository`` — ``lru_cache``, fail-closed
validation, keyed by identifier — but live inside the acquisition package so
that ``data_repository.py`` stays byte-identical to the governed visual
baseline provenance (``browser_tests/baselines/v0.3.0/manifest.json``
``source_tree`` pins every top-level ``src/ior_mvp/*.py`` module).

Nothing here is consumed by the engine until S13/S14 (KL-45).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from ..config import PROJECT_ROOT
from .snapshots import (
    SNAPSHOT_ROOTS,
    validate_partner_snapshot,
    validate_tariff_snapshot,
    validate_universe_snapshot,
)
from .source_config import acquisition_sources_config

DATA_ROOT = PROJECT_ROOT / "data"

_VALIDATORS: dict[str, Callable[..., None]] = {
    "universe": validate_universe_snapshot,
    "tariff": validate_tariff_snapshot,
    "partners": validate_partner_snapshot,
}


def _kind_directory(kind: str) -> Path:
    relative = SNAPSHOT_ROOTS[kind].removeprefix("data/")
    return DATA_ROOT / relative


def _read_record(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _load_kind(kind: str) -> dict[str, dict[str, Any]]:
    """Load every snapshot of one kind, validated, keyed by snapshot_id."""
    validate = _VALIDATORS[kind]
    directory = _kind_directory(kind)
    records: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.json")):
        record = _read_record(path)
        validate(record)
        snapshot_id = record["snapshot_id"]
        if path.stem != snapshot_id:
            raise ValueError(
                f"Snapshot file name must equal snapshot_id: {path}"
            )
        records[snapshot_id] = record
    return records


@lru_cache(maxsize=1)
def universe_snapshots() -> dict[str, dict[str, Any]]:
    return _load_kind("universe")


@lru_cache(maxsize=1)
def tariff_snapshots() -> dict[str, dict[str, Any]]:
    return _load_kind("tariff")


@lru_cache(maxsize=1)
def partner_snapshots() -> dict[str, dict[str, Any]]:
    return _load_kind("partners")


def clear_acquisition_caches() -> None:
    """Clear the acquisition config cache and the three snapshot loaders."""
    acquisition_sources_config.cache_clear()
    universe_snapshots.cache_clear()
    tariff_snapshots.cache_clear()
    partner_snapshots.cache_clear()
