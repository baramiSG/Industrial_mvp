"""Load and validate acquisition source configuration.

The loader lives inside the acquisition package on purpose: the governed
visual baseline manifest pins the SHA-256 of every top-level
``src/ior_mvp/*.py`` module, so ``config.py`` stays byte-identical and the
acquisition configuration is loaded here with the same ``lru_cache`` pattern.
"""

from __future__ import annotations

import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config import PROJECT_ROOT
from .contracts import AcquisitionConfigurationError, Stage, UNAVAILABLE

ACQUISITION_SOURCES_PATH = PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml"
INSTITUTIONAL_SOURCE_STAGES = {
    "gastat": Stage.AGGREGATE,
    "ministry_of_industry": Stage.DIRECTORY,
    "modon": Stage.DIRECTORY,
    "saso_catalogue": Stage.REGISTRY,
    "saber_registry": Stage.REGISTRY,
}
DOCUMENT_SOURCE_STAGES = {
    "tadawul_disclosures": Stage.DOCUMENT,
    "etimad_tenders": Stage.DOCUMENT,
    "saso_documents": Stage.DOCUMENT,
    "producer_unicoil": Stage.DOCUMENT,
    "producer_sabic": Stage.DOCUMENT,
    "producer_advanced_petrochemical": Stage.DOCUMENT,
    "producer_tasnee": Stage.DOCUMENT,
}
INSTITUTIONAL_SOURCE_IDS = frozenset(INSTITUTIONAL_SOURCE_STAGES)
DOCUMENT_SOURCE_IDS = frozenset(DOCUMENT_SOURCE_STAGES)
SOURCE_IDS = (
    frozenset({"wits_trade", "un_comtrade", "baci_cepii", "zatca_tariff"})
    | INSTITUTIONAL_SOURCE_IDS
    | DOCUMENT_SOURCE_IDS
)
DOCUMENT_OBSERVED_FACT_FIELDS = (
    "access_classification",
    "documentation_reference",
    "terms_reference",
    "endpoint_templates.TERMS",
    "parameters.product_all_token",
    "parameters.partner_world_token",
    "parameters.reporter_token",
    "parameters.flow_tokens",
    "pagination.documentation_reference",
    "nomenclature",
    "credential_env_var",
    "rate_limit.documented_policy",
    "expected_content_types",
)
CREDENTIAL_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+$")
CREDENTIAL_HEADER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")
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
SOURCE_KEYS = frozenset({
    "authority", "access_classification", "documentation_reference", "terms_reference",
    "endpoint_templates", "parameters", "pagination", "nomenclature", "reporter_code",
    "credential_env_var", "rate_limit", "license_capture_required", "default_evidence_class",
    "default_reviewer_status", "expected_content_types", "user_agent", "recorded_on",
})
OPTIONAL_TRADE_SOURCE_KEYS = frozenset({"credential_header"})
OBSERVED_FACT_FIELDS = (
    "access_classification", "documentation_reference", "terms_reference",
    "endpoint_templates.{stage}", "endpoint_templates.TERMS",
    "parameters.product_all_token", "parameters.partner_world_token",
    "parameters.reporter_token", "parameters.flow_tokens", "parameters.units",
    "pagination.kind", "pagination.documentation_reference", "pagination.parameters",
    "nomenclature", "credential_env_var", "rate_limit.documented_policy", "expected_content_types",
)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _string_mapping(value: Any, *, nonempty_values: bool = False) -> bool:
    return isinstance(value, dict) and all(
        _nonempty_string(key) and isinstance(item, str) and (bool(item) or not nonempty_values)
        for key, item in value.items()
    )


def _credential_name(value: Any) -> bool:
    return value is None or (
        isinstance(value, str) and value != UNAVAILABLE
        and CREDENTIAL_PATTERN.fullmatch(value) is not None
    )


def _valid_fact(path: str, value: Any) -> bool:
    """One set of observed-value predicates for S11 and institutional sources."""
    if path == "access_classification":
        return isinstance(value, str) and value in ACCESS_CLASSES
    if path == "nomenclature":
        return isinstance(value, str) and NOMENCLATURE_PATTERN.fullmatch(value) is not None
    if path == "credential_env_var":
        return _credential_name(value)
    if path == "pagination.kind":
        return isinstance(value, str) and value in PAGINATION_KINDS
    if path == "parameters.flow_tokens":
        return _string_mapping(value, nonempty_values=True)
    if path == "pagination.parameters":
        return _string_mapping(value)
    if path == "parameters.units":
        return isinstance(value, list) and bool(value) and all(
            _string_mapping(unit) and bool(unit) for unit in value
        )
    if path == "expected_content_types":
        return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)
    return _nonempty_string(value)


def _fact_value(source: dict[str, Any], path: str) -> Any:
    value: Any = source
    for key in path.split("."):
        value = value[key]
    return value


def observed_fact_values(source_id: str, source: dict[str, Any]) -> dict[str, Any]:
    """Return observed source facts for institutional or document sources."""
    if source_id in INSTITUTIONAL_SOURCE_IDS:
        stage = INSTITUTIONAL_SOURCE_STAGES[source_id].value
        paths = [path.format(stage=stage) for path in OBSERVED_FACT_FIELDS]
        return {path: _fact_value(source, path) for path in paths}
    if source_id in DOCUMENT_SOURCE_IDS:
        return {path: _fact_value(source, path) for path in DOCUMENT_OBSERVED_FACT_FIELDS}
    raise AcquisitionConfigurationError(f"No observation phase for source {source_id}")


def observation_state(source_id: str, source: dict[str, Any]) -> str:
    """Derive the phase without confusing an observed null or mapping with absence."""
    return "PRE_OBSERVATION" if all(
        value == UNAVAILABLE for value in observed_fact_values(source_id, source).values()
    ) else "OBSERVED"


def configured_credential_env_var(source: dict[str, Any]) -> str | None:
    """Single credential interpretation for acquisition and stored-evidence checks."""
    value = source.get("credential_env_var")
    if value in (None, "", UNAVAILABLE):
        return None
    if not _credential_name(value):
        raise AcquisitionConfigurationError("credential_env_var invalid")
    return value


def configured_credential_header(
    source: dict[str, Any],
) -> tuple[str, str | None]:
    """Return request header name and optional credential scheme."""
    header = source.get("credential_header")
    if header is None:
        return "Authorization", "Bearer"
    if (
        not isinstance(header, str)
        or CREDENTIAL_HEADER_PATTERN.fullmatch(header) is None
        or configured_credential_env_var(source) is None
    ):
        raise AcquisitionConfigurationError("credential_header invalid")
    return header, None


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


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


def _check_no_forbidden_keys(payload: Any, path: str = "") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            current = f"{path}.{key}" if path else str(key)
            if key in FORBIDDEN_KEYS:
                raise AcquisitionConfigurationError(
                    f"Forbidden key in acquisition config: {current}"
                )
            _check_no_forbidden_keys(value, current)
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            _check_no_forbidden_keys(value, f"{path}[{index}]")


def validate_acquisition_sources(payload: dict[str, Any]) -> None:
    """Fail-closed validation of acquisition_sources.v1.yaml."""
    _check_no_forbidden_keys(payload)

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise AcquisitionConfigurationError("metadata must be a mapping")
    if metadata.get("version") != "1.3.0":
        raise AcquisitionConfigurationError(
            "metadata.version must be 1.3.0"
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

    for required in sorted(SOURCE_KEYS):
        if required not in source:
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.{required} is required"
            )

    institutional = source_id in INSTITUTIONAL_SOURCE_IDS
    document = source_id in DOCUMENT_SOURCE_IDS
    _validate_source_facts(source_id, source, institutional=institutional, document=document)
    _validate_credential_header(
        source_id,
        source,
        institutional=institutional,
        document=document,
    )
    access = source["access_classification"]

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
    if (institutional or document) and (
        (recorded_on != UNAVAILABLE and not _iso_date(recorded_on))
        or (observation_state(source_id, source) == "OBSERVED" and not _iso_date(recorded_on))
    ):
        raise AcquisitionConfigurationError(
            f"sources.{source_id}.recorded_on must be an ISO date once any fact is observed"
        )
    if document:
        if source["endpoint_templates"]["DOCUMENT"] != "{document_url}":
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.endpoint_templates.DOCUMENT must be '{{document_url}}'"
            )
        if source["pagination"]["kind"] != "NONE":
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.pagination.kind must be NONE"
            )
        if source["pagination"]["parameters"] != {}:
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.pagination.parameters must be empty"
            )
        if "units" in source.get("parameters", {}):
            raise AcquisitionConfigurationError(
                f"sources.{source_id}.parameters must not include units"
            )

def _validate_source_facts(
    source_id: str, source: dict[str, Any], *, institutional: bool, document: bool = False
) -> None:
    prefix = f"sources.{source_id}"
    nested_keys = {
        "parameters": {"product_all_token", "partner_world_token", "reporter_token", "flow_tokens"},
        "pagination": {"kind", "documentation_reference", "parameters"},
        "rate_limit": {"documented_policy", "min_interval_seconds", "max_attempts", "timeout_seconds"},
    }
    if institutional:
        if set(source) != SOURCE_KEYS:
            raise AcquisitionConfigurationError(f"{prefix} keys must be exactly {sorted(SOURCE_KEYS)}")
        nested_keys["parameters"].add("units")
        nested_keys["endpoint_templates"] = {INSTITUTIONAL_SOURCE_STAGES[source_id].value, "TERMS"}
    elif document:
        if set(source) != SOURCE_KEYS:
            raise AcquisitionConfigurationError(f"{prefix} keys must be exactly {sorted(SOURCE_KEYS)}")
        nested_keys["endpoint_templates"] = {"DOCUMENT", "TERMS"}
    else:
        nested_keys["endpoint_templates"] = set()
    for key, required in nested_keys.items():
        value = source[key]
        if not isinstance(value, dict):
            raise AcquisitionConfigurationError(f"{prefix}.{key} must be a mapping")
        if (
            ((institutional or document) and set(value) != required)
            or not required <= set(value)
        ):
            qualifier = "exactly" if institutional or document else "include"
            raise AcquisitionConfigurationError(
                f"{prefix}.{key} keys must {qualifier} {sorted(required)}"
            )

    if institutional or document:
        facts = observed_fact_values(source_id, source)
    else:
        paths = [path for path in OBSERVED_FACT_FIELDS
                 if not path.startswith("endpoint_templates.") and path != "parameters.units"]
        facts = {path: _fact_value(source, path) for path in paths}
        facts.update({f"endpoint_templates.{key}": value for key, value in source["endpoint_templates"].items()})
    for path, value in facts.items():
        if (institutional or document) and value == UNAVAILABLE:
            continue
        if not _valid_fact(path, value):
            raise AcquisitionConfigurationError(f"{prefix}.{path} invalid")


def _validate_credential_header(
    source_id: str,
    source: dict[str, Any],
    *,
    institutional: bool,
    document: bool,
) -> None:
    prefix = f"sources.{source_id}"
    if institutional or document:
        return
    allowed = SOURCE_KEYS | OPTIONAL_TRADE_SOURCE_KEYS
    if set(source) not in {SOURCE_KEYS, allowed}:
        raise AcquisitionConfigurationError(
            f"{prefix} keys must be exactly {sorted(SOURCE_KEYS)} "
            f"with optional {sorted(OPTIONAL_TRADE_SOURCE_KEYS)}"
        )
    if "credential_header" not in source:
        return
    header = source["credential_header"]
    if (
        not isinstance(header, str)
        or CREDENTIAL_HEADER_PATTERN.fullmatch(header) is None
    ):
        raise AcquisitionConfigurationError(
            f"{prefix}.credential_header invalid"
        )
    if configured_credential_env_var(source) is None:
        raise AcquisitionConfigurationError(
            f"{prefix}.credential_header requires credential_env_var"
        )
