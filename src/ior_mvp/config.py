from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required configuration is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration must contain a mapping: {path}")
    return data


@lru_cache(maxsize=1)
def project_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "project.yaml")


@lru_cache(maxsize=1)
def thresholds_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "thresholds.v1.yaml")


@lru_cache(maxsize=1)
def sector_profiles_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "sector_profiles.v1.yaml")


@lru_cache(maxsize=1)
def evidence_policy_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "evidence_policy.v1.yaml")


def clear_config_caches() -> None:
    project_config.cache_clear()
    thresholds_config.cache_clear()
    sector_profiles_config.cache_clear()
    evidence_policy_config.cache_clear()
