from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from string import Formatter
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
AUTHORITY_HASHES_PATH = (
    DOCS_DIR / "authority" / "authority_hashes.json"
)
UI_STRINGS_PATH = CONFIG_DIR / "ui_strings.v1.yaml"
DECISION_NARRATIVES_PATH = (
    CONFIG_DIR / "decision_narratives.v1.yaml"
)
SUPPORTED_UI_LOCALES: tuple[str, ...] = ("en", "ar")
UI_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)


class AuthorityConfigurationError(RuntimeError):
    pass


class UIStringConfigurationError(RuntimeError):
    pass


class UnsupportedUILocaleError(ValueError):
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
def decision_narratives_config() -> dict[str, Any]:
    from .narratives import (
        NarrativeCatalogueError,
        validate_decision_narratives,
    )

    try:
        payload = _load_yaml(DECISION_NARRATIVES_PATH)
        validate_decision_narratives(payload)
    except NarrativeCatalogueError:
        raise
    except (
        OSError,
        UnicodeError,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        raise NarrativeCatalogueError(
            "Decision narrative catalogue could not be loaded"
        ) from exc
    return payload


def _placeholders(value: str) -> set[str]:
    try:
        return {
            field
            for _, field, _, _ in Formatter().parse(value)
            if field is not None
        }
    except ValueError as exc:
        raise UIStringConfigurationError(
            "UI catalogue contains malformed placeholders"
        ) from exc


def validate_ui_strings(payload: dict[str, Any]) -> None:
    """Validate the complete bilingual UI catalogue fail-closed."""
    metadata = payload.get("metadata")
    locales = payload.get("locales")
    strings = payload.get("strings")
    if not all(
        isinstance(value, dict)
        for value in (metadata, locales, strings)
    ):
        raise UIStringConfigurationError(
            "UI catalogue metadata, locales, and strings must be mappings"
        )
    assert isinstance(metadata, dict)
    assert isinstance(locales, dict)
    assert isinstance(strings, dict)
    if metadata.get("version") != "1.3.0":
        raise UIStringConfigurationError(
            "UI catalogue metadata.version must be 1.3.0"
        )
    if metadata.get("default_locale") != "en":
        raise UIStringConfigurationError(
            "UI catalogue default locale must be en"
        )
    if tuple(locales) != SUPPORTED_UI_LOCALES or set(strings) != set(
        SUPPORTED_UI_LOCALES
    ):
        raise UIStringConfigurationError(
            "UI catalogue locale set must be exactly en and ar"
        )
    expected_locale_metadata = {
        "en": {"bcp47": "en-US", "direction": "ltr"},
        "ar": {"bcp47": "ar-SA", "direction": "rtl"},
    }
    if locales != expected_locale_metadata:
        raise UIStringConfigurationError(
            "UI catalogue locale metadata is invalid"
        )
    locale_strings: dict[str, dict[str, Any]] = {}
    for locale in SUPPORTED_UI_LOCALES:
        values = strings.get(locale)
        if not isinstance(values, dict):
            raise UIStringConfigurationError(
                f"UI catalogue strings.{locale} must be a mapping"
            )
        locale_strings[locale] = values
    if set(locale_strings["en"]) != set(locale_strings["ar"]):
        raise UIStringConfigurationError(
            "UI catalogue locale key sets do not match"
        )
    policy = evidence_policy_config().get("synthetic_isolation")
    policy_values = (
        {
            value
            for key in ("display_label", "display_label_ar")
            if isinstance(policy, dict)
            and isinstance(value := policy.get(key), str)
        }
    )
    for key in locale_strings["en"]:
        if UI_KEY_PATTERN.fullmatch(key) is None:
            raise UIStringConfigurationError(
                f"UI catalogue key is invalid: {key}"
            )
        if key.startswith("synthetic."):
            raise UIStringConfigurationError(
                "UI catalogue may not define synthetic policy labels"
            )
        for locale in SUPPORTED_UI_LOCALES:
            value = locale_strings[locale][key]
            if (
                not isinstance(value, str)
                or not value
                or value.strip() != value
                or unicodedata.normalize("NFC", value) != value
            ):
                raise UIStringConfigurationError(
                    f"UI catalogue value is invalid: {locale}.{key}"
                )
            if value in policy_values:
                raise UIStringConfigurationError(
                    "UI catalogue duplicates an evidence-policy label"
                )
        if _placeholders(locale_strings["en"][key]) != _placeholders(
            locale_strings["ar"][key]
        ):
            raise UIStringConfigurationError(
                f"UI catalogue placeholder mismatch: {key}"
            )


@lru_cache(maxsize=1)
def ui_strings_config() -> dict[str, Any]:
    """Load and validate the whole governed UI catalogue."""
    try:
        payload = _load_yaml(UI_STRINGS_PATH)
        validate_ui_strings(payload)
    except UIStringConfigurationError:
        raise
    except (OSError, UnicodeError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise UIStringConfigurationError(
            "UI catalogue could not be loaded"
        ) from exc
    return payload


def ui_strings_bundle(locale: str) -> dict[str, Any]:
    """Return one complete locale bundle plus policy-sourced labels."""
    if locale not in SUPPORTED_UI_LOCALES:
        raise UnsupportedUILocaleError(locale)
    payload = ui_strings_config()
    from .evidence import synthetic_display_labels

    return {
        "catalogue_version": payload["metadata"]["version"],
        "locale": locale,
        **deepcopy(payload["locales"][locale]),
        "strings": deepcopy(payload["strings"][locale]),
        "synthetic_labels": synthetic_display_labels(),
    }


def ui_text(key: str, locale: str = "en", **values: Any) -> str:
    """Resolve one validated catalogue value for server-rendered chrome."""
    if locale not in SUPPORTED_UI_LOCALES:
        raise UnsupportedUILocaleError(locale)
    strings = ui_strings_config()["strings"][locale]
    if key not in strings:
        raise UIStringConfigurationError(
            f"UI catalogue key is missing: {key}"
        )
    try:
        return strings[key].format(**values)
    except (KeyError, ValueError) as exc:
        raise UIStringConfigurationError(
            f"UI catalogue interpolation failed: {key}"
        ) from exc


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
            "ui_strings": _metadata_version(
                ui_strings_config(),
                "ui_strings",
            ),
            "decision_narratives": _metadata_version(
                decision_narratives_config(),
                "decision_narratives",
            ),
        },
        "project_version": project_version,
    }


def clear_config_caches() -> None:
    project_config.cache_clear()
    thresholds_config.cache_clear()
    sector_profiles_config.cache_clear()
    evidence_policy_config.cache_clear()
    decision_narratives_config.cache_clear()
    ui_strings_config.cache_clear()
    authority_hashes_config.cache_clear()
