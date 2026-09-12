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
from typing import Any

from ..config import PROJECT_ROOT
from .snapshots import _snapshot_directory, validate_snapshot
from .kinds import KindRegistry, default_kind_registry
from .source_config import acquisition_sources_config

DATA_ROOT = PROJECT_ROOT / "data"

def _read_record(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _load_kind(kind: str, *, kinds: KindRegistry, data_root: Path,
               allow_test_double: bool = False) -> dict[str, dict[str, Any]]:
    """Read and validate an explicitly scoped kind without affecting caches."""
    spec = kinds.get(kind)
    directory = _snapshot_directory(data_root, spec.root)
    records: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.json")):
        record = _read_record(path)
        if record.get("kind") != kind:
            raise ValueError(f"kind mismatch: {kind}")
        validate_snapshot(record, kinds=kinds, allow_test_double=allow_test_double)
        snapshot_id = record["snapshot_id"]
        if path.stem != snapshot_id:
            raise ValueError(f"Snapshot file name must equal snapshot_id: {path}")
        records[snapshot_id] = record
    return records


@lru_cache(maxsize=None)
def _cached_acquired_snapshots(kind: str) -> dict[str, dict[str, Any]]:
    return _load_kind(kind, kinds=default_kind_registry(), data_root=DATA_ROOT)


def acquired_snapshots(kind: str, *, kinds: KindRegistry | None = None,
                       data_root: Path | None = None,
                       allow_test_double: bool = False) -> dict[str, dict[str, Any]]:
    if kinds is not None or data_root is not None or allow_test_double:
        return _load_kind(kind, kinds=kinds or default_kind_registry(),
                          data_root=data_root if data_root is not None else DATA_ROOT,
                          allow_test_double=allow_test_double)
    return _cached_acquired_snapshots(kind)


def universe_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("universe")


def tariff_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("tariff")


def partner_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("partners")


def production_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("production")


def directory_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("directory")


def registry_snapshots() -> dict[str, dict[str, Any]]:
    return acquired_snapshots("registry")


def clear_acquisition_caches() -> None:
    """Clear config and every default kind cache; injected loads are uncached."""
    acquisition_sources_config.cache_clear()
    _cached_acquired_snapshots.cache_clear()
