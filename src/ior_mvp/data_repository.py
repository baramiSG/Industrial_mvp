from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import DATA_DIR
from .evidence import validate_synthetic_scenario


class RepositoryError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RepositoryError(f"Data artifact not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as exc:
        raise RepositoryError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RepositoryError(f"Expected a JSON object in {path}")
    return value


@lru_cache(maxsize=1)
def public_cases() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    directory = DATA_DIR / "snapshots" / "public"
    for path in sorted(directory.glob("*.json")):
        record = _read_json(path)
        opportunity_id = record.get("opportunity", {}).get("id")
        if not opportunity_id:
            raise RepositoryError(f"Public snapshot lacks opportunity.id: {path}")
        if record.get("source_boundary") != "public":
            raise RepositoryError(f"Public snapshot has an invalid boundary: {path}")
        cases[opportunity_id] = record
    if not cases:
        raise RepositoryError("No public opportunity snapshots were found")
    return cases


@lru_cache(maxsize=1)
def synthetic_scenarios() -> dict[str, dict[str, Any]]:
    scenarios: dict[str, dict[str, Any]] = {}
    directory = DATA_DIR / "synthetic"
    for path in sorted(directory.glob("*.json")):
        record = _read_json(path)
        validate_synthetic_scenario(record)
        opportunity_id = record["opportunity_id"]
        scenarios[opportunity_id] = record
    return scenarios


@lru_cache(maxsize=1)
def extraction_golden_set() -> dict[str, Any]:
    return _read_json(DATA_DIR / "golden" / "ar_en_spec_extraction.json")


def get_public_case(opportunity_id: str) -> dict[str, Any]:
    try:
        return public_cases()[opportunity_id]
    except KeyError as exc:
        raise RepositoryError(f"Unknown opportunity: {opportunity_id}") from exc


def get_synthetic_scenario(opportunity_id: str) -> dict[str, Any] | None:
    return synthetic_scenarios().get(opportunity_id)


def clear_repository_caches() -> None:
    public_cases.cache_clear()
    synthetic_scenarios.cache_clear()
    extraction_golden_set.cache_clear()
