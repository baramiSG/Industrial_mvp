"""Load and validate acquisition source configuration.

The loader lives inside the acquisition package on purpose: the governed
visual baseline manifest pins the SHA-256 of every top-level
``src/ior_mvp/*.py`` module, so ``config.py`` stays byte-identical and the
acquisition configuration is loaded here with the same ``lru_cache`` pattern.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config import PROJECT_ROOT
from .contracts import AcquisitionConfigurationError, UNAVAILABLE

ACQUISITION_SOURCES_PATH = PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml"
SOURCE_IDS = frozenset({"wits_trade", "un_comtrade", "baci_cepii", "zatca_tariff"})
CREDENTIAL_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+$")
NOMENCLATURE_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
ACCESS_CLASSES = frozenset(
    {"public_open", "public_registered", "public_terms_restricted"}
)
PAGINATION_KINDS = frozenset(
    {"NONE", "PAGE_NUMBER", "NEXT_TOKEN", "INDEX_ENUMERATION", UNAVAILABLE}
)
EVIDENCE_CLASSES = frozenset({"A", "B", "C", "D", "E"})
FORBIDDEN_KEYS = frozenset(
    {"years", "default_years", "max_requests", "default_max_requests"}
)


def _is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AcquisitionConfigurationError(
            f"Required acquisition configuration is missing: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise AcquisitionConfigurationError(
            f"Acquisition configuration must contain a mapping: {path}"
        )
    return data


@lru_cache(maxsize=1)
def acquisition_sources_config() -> dict[str, Any]:
    """Load ``acquisition_sources.v1.yaml`` once, fail-closed on validation."""
    payload = _load_yaml(ACQUISITION_SOURCES_PATH)
    validate_acquisition_sources(payload)
    return payload


def _check_no_forbidden_keys(payload: dict[str, Any], path: str = "") -> None:
    for key, value in payload.items():
        current = f"{path}.{key}" if path else key
        if key in FORBIDDEN_KEYS:
            raise AcquisitionConfigurationError(
                f"Forbidden key in acquisition config: {current}"
            )
        if isinstance(value, dict):
            _check_no_forbidden_keys(value, current)


def validate_acquisition_sources(payload: dict[str, Any]) -> None:
    """Fail-closed validation of acquisition_sources.v1.yaml."""
    _check_no_forbidden_keys(payload)

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise AcquisitionConfigurationError("metadata must be a mapping")
    if metadata.get("version") != "1.0.0":
        raise AcquisitionConfigurationError(
            "metadata.version must be 1.0.0"
        )

    raw_store = payload.get("raw_store")
    if not isinstance(raw_store, dict):
        raise AcquisitionConfigurationError("raw_store must be a mapping")
    for key in (
        "max_artifact_bytes_compressed",
        "max_store_bytes_compressed",
    ):
        value = raw_store.get(key)
        if not isinstance(value, int) or value <= 0:
            raise AcquisitionConfigurationError(
                f"raw_store.{key} must be a positive integer"
            )

    offline_guard = payload.get("offline_guard")
    if not isinstance(offline_guard, dict):
        raise AcquisitionConfigurationError(
            "offline_guard must be a mapping"
        )
    live_env_var = offline_guard.get("live_env_var")
    if not isinstance(live_env_var, str) or not live_env_var:
        raise AcquisitionConfigurationError(
            "offline_guard.live_env_var must be non-empty"
        )
    for list_key in ("header_allowlist", "header_denylist"):
        items = offline_guard.get(list_key)
        if not isinstance(items, list) or not items:
            raise AcquisitionConfigurationError(
                f"offline_guard.{list_key} must be a non-empty list"
            )

    rate_defaults = payload.get("rate_limit_defaults")
    if not isinstance(rate_defaults, dict):
        raise AcquisitionConfigurationError(
            "rate_limit_defaults must be a mapping"
        )
    floor = rate_defaults.get("undocumented_min_interval_seconds")
    if not isinstance(floor, (int, float)) or floor <= 0:
        raise AcquisitionConfigurationError(
            "rate_limit_defaults.undocumented_min_interval_seconds > 0"
        )

    sources = payload.get("sources")
    if not isinstance(sources, dict):
        raise AcquisitionConfigurationError("sources must be a mapping")
    if set(sources) != SOURCE_IDS:
        raise AcquisitionConfigurationError(
            f"sources must be exactly {sorted(SOURCE_IDS)}"
        )

    for source_id, source in sources.items():
        _validate_source(source_id, source, floor)


def _validate_source(
    source_id: str,
    source: Any,
    undocumented_floor: float,
) -> None:
    if not isinstance(source, dict):
        raise AcquisitionConfigurationError(
            f"sources.{source_id} must be a mapping"
        )

    for required in (
        "authority",
        "access_classification",
        "documentation_reference",
        "terms_reference",
        "endpoint_templates",
        "parameters",
        "pagination",
        "nomenclature",
        "reporter_code",
        "credential_env_var",
        "rate_limit",
        "license_capture_required",
        "default_evidence_class",
        "default_reviewer_status",
        "expected_content_types",
        "user_agent",
        "recorded_on",
    ):
        if required not in source:
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.{required} is required"
            )

    access = source["access_classification"]
    if access not in ACCESS_CLASSES:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.access_classification invalid"
        )

    nomenclature = source["nomenclature"]
    if NOMENCLATURE_PATTERN.fullmatch(nomenclature) is None:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.nomenclature must match ^[A-Za-z0-9]+$"
        )

    credential = source["credential_env_var"]
    if credential is not None and CREDENTIAL_PATTERN.fullmatch(credential) is None:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.credential_env_var invalid"
        )

    evidence_class = source["default_evidence_class"]
    if evidence_class not in EVIDENCE_CLASSES:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.default_evidence_class invalid"
        )

    reviewer_status = source["default_reviewer_status"]
    if not isinstance(reviewer_status, str) or not reviewer_status:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.default_reviewer_status required"
        )

    terms_reference = source["terms_reference"]
    license_required = source["license_capture_required"]
    if not isinstance(license_required, bool):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.license_capture_required must be bool"
        )

    if access != "public_open" and not license_required:
        raise AcquisitionConfigurationError(
            f"sources.{source_id} non-public_open requires license_capture"
        )
    if _is_url(str(terms_reference)) and not license_required:
        raise AcquisitionConfigurationError(
            f"sources.{source_id} URL terms_reference requires license_capture"
        )
    if source_id in {"baci_cepii", "un_comtrade"} and not license_required:
        raise AcquisitionConfigurationError(
            f"sources.{source_id} requires license_capture_required true"
        )

    rate_limit = source["rate_limit"]
    if not isinstance(rate_limit, dict):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.rate_limit must be a mapping"
        )
    min_interval = rate_limit.get("min_interval_seconds")
    documented = rate_limit.get("documented_policy")
    if not isinstance(min_interval, (int, float)) or min_interval <= 0:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.rate_limit.min_interval_seconds > 0"
        )
    if documented == UNAVAILABLE and min_interval < undocumented_floor:
        raise AcquisitionConfigurationError(
            f"sources.{source_id} undocumented min_interval below floor"
        )
    max_attempts = rate_limit.get("max_attempts")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.rate_limit.max_attempts >= 1"
        )
    timeout = rate_limit.get("timeout_seconds")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.rate_limit.timeout_seconds > 0"
        )

    pagination = source["pagination"]
    if not isinstance(pagination, dict):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.pagination must be a mapping"
        )
    kind = pagination.get("kind")
    if kind not in PAGINATION_KINDS:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.pagination.kind invalid"
        )

    content_types = source["expected_content_types"]
    if not isinstance(content_types, list) or not content_types:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.expected_content_types required"
        )

    user_agent = source["user_agent"]
    if not isinstance(user_agent, str) or not user_agent:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.user_agent required"
        )

    recorded_on = source["recorded_on"]
    if not isinstance(recorded_on, str) or not recorded_on:
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.recorded_on required"
        )

    endpoints = source["endpoint_templates"]
    if not isinstance(endpoints, dict):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.endpoint_templates must be a mapping"
        )

    parameters = source["parameters"]
    if not isinstance(parameters, dict):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.parameters must be a mapping"
        )
    for token_key in (
        "product_all_token",
        "partner_world_token",
        "reporter_token",
        "flow_tokens",
    ):
        if token_key not in parameters:
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.parameters.{token_key} required"
            )
