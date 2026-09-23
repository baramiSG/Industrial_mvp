"""Read-only runtime loader for the newest screening snapshot."""

from __future__ import annotations

from copy import deepcopy
import json
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any

from ior_mvp.config import PROJECT_ROOT

from .snapshot import (
    load_screening_record_shard,
    load_screening_summary_directory,
)

SNAPSHOT_ROOT = PROJECT_ROOT / "data" / "screening" / "snapshots"


@lru_cache(maxsize=1)
def _screening_directory() -> Path | None:
    if not SNAPSHOT_ROOT.is_dir():
        return None
    directories = [
        path
        for path in SNAPSHOT_ROOT.glob("SCREENING-*")
        if path.is_dir()
    ]
    if not directories:
        return None
    summaries = [
        (load_screening_summary_directory(path), path)
        for path in directories
    ]
    return max(
        summaries,
        key=lambda item: (
            item[0]["as_of_date"],
            item[0]["snapshot_id"],
        ),
    )[1]


@lru_cache(maxsize=1)
def screening_snapshot() -> dict[str, Any] | None:
    path = _screening_directory()
    return load_screening_summary_directory(path) if path else None


@lru_cache(maxsize=128)
def _screening_shard(snapshot_id: str, hs2: str) -> tuple[dict[str, Any], ...]:
    path = _screening_directory()
    summary = screening_snapshot()
    if (
        path is None
        or summary is None
        or summary["snapshot_id"] != snapshot_id
    ):
        return ()
    return tuple(load_screening_record_shard(path, summary, hs2))


def screening_record(hs6: str) -> dict[str, Any] | None:
    snapshot = screening_snapshot()
    if snapshot is None or len(hs6) < 2:
        return None
    return next(
        (
            record
            for record in _screening_shard(snapshot["snapshot_id"], hs6[:2])
            if record["hs6"] == hs6
        ),
        None,
    )


def iter_screening_records() -> Iterator[dict[str, Any]]:
    """Yield deterministic copies of every public screening record.

    Yields:
        HS6-sorted record copies that cannot mutate the process-local cache.
    """
    snapshot = screening_snapshot()
    if snapshot is None:
        return
    for shard in sorted(
        snapshot["record_shards"],
        key=lambda row: row["hs2"],
    ):
        for record in _screening_shard(
            snapshot["snapshot_id"],
            shard["hs2"],
        ):
            yield deepcopy(record)


def clear_screening_caches() -> None:
    _screening_directory.cache_clear()
    screening_snapshot.cache_clear()
    _screening_shard.cache_clear()
