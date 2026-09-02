from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
AUTHORITY_HASHES_PATH = (
    DOCS_DIR / "authority" / "authority_hashes.json"
)


class AuthorityConfigurationError(RuntimeError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required configuration is missing: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(
            f"Configuration must contain a mapping: {path}"
        )
    return data


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AuthorityConfigurationError(
            f"Required authority manifest is missing: {path}"
        )
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        raise AuthorityConfigurationError(
            f"Authority manifest cannot be loaded: {path}"
        ) from exc
    if not isinstance(data, dict):
        raise AuthorityConfigurationError(
            f"Authority manifest must contain a mapping: {path}"
        )
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


@lru_cache(maxsize=1)
def authority_hashes_config() -> dict[str, Any]:
    return _load_json(AUTHORITY_HASHES_PATH)


def _metadata_version(
    config: dict[str, Any],
    artifact: str,
) -> str:
    metadata = config.get("metadata")
    version = (
        metadata.get("version")
        if isinstance(metadata, dict)
        else None
    )
    if not isinstance(version, str) or not version:
        raise AuthorityConfigurationError(
            f"{artifact} configuration metadata.version is missing"
        )
    return version


def authority_summary() -> dict[str, Any]:
    files = authority_hashes_config().get("files")
    if not isinstance(files, list):
        raise AuthorityConfigurationError(
            "Authority manifest files must be a list"
        )
    methodology_entries = [
        item
        for item in files
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and item["path"].lower().endswith(".docx")
    ]
    if len(methodology_entries) != 1:
        raise AuthorityConfigurationError(
            "Authority manifest must contain exactly one methodology DOCX"
        )

    methodology = methodology_entries[0]
    digest = methodology.get("sha256")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(
            character not in "0123456789abcdef"
            for character in digest
        )
    ):
        raise AuthorityConfigurationError(
            "Methodology authority entry has an invalid SHA-256"
        )

    project = project_config().get("project")
    project_version = (
        project.get("version")
        if isinstance(project, dict)
        else None
    )
    if not isinstance(project_version, str) or not project_version:
        raise AuthorityConfigurationError(
            "Project version is missing"
        )

    return {
        "methodology": {
            "file": methodology["path"],
            "sha256": digest,
            "sha256_prefix": digest[:12],
        },
        "config_versions": {
            "thresholds": _metadata_version(
                thresholds_config(),
                "thresholds",
            ),
            "sector_profiles": _metadata_version(
                sector_profiles_config(),
                "sector_profiles",
            ),
            "evidence_policy": _metadata_version(
                evidence_policy_config(),
                "evidence_policy",
            ),
        },
        "project_version": project_version,
    }


def clear_config_caches() -> None:
    project_config.cache_clear()
    thresholds_config.cache_clear()
    sector_profiles_config.cache_clear()
    evidence_policy_config.cache_clear()
    authority_hashes_config.cache_clear()
