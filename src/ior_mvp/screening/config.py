"""Versioned screening and product-family configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import yaml

from ior_mvp.config import PROJECT_ROOT


class ScreeningConfigurationError(ValueError):
    """Raised when a screening configuration is not governed."""


QUEUE_IDS = (
    "robust_public_finding",
    "incumbent_upgrade_investigation",
    "resilience_case",
    "likely_false_positive",
    "high_evsi_evidence_investigation",
)
DISPOSITIONS = ("CANDIDATE", "SCREENED_OUT", "NO_CANDIDATE")
INDICATED_STATES = ("INVESTIGATE", "MONITOR", "REJECT")
REASON_CODES = frozenset(
    {
        "MATERIAL_TRIGGER_FIRED",
        "NON_MATERIAL_SIGNAL_ONLY",
        "HARD_EXCLUSION_SATISFIED",
        "GENERIC_CAPACITY_CONTRADICTED",
        "IDENTITY_UNRESOLVED",
        "NO_IMPORT_OBSERVATIONS",
        "NO_TRIGGER_FIRED",
        "NO_UNIVERSE_SNAPSHOT",
        "LICENSE_UNRECORDED",
        "CREDENTIAL_ABSENT",
        "HTTP_ERROR",
        "COVERAGE_INDETERMINATE",
        "PARTNER_DETAIL_NOT_ACQUIRED",
        "TARIFF_TREE_NOT_ACQUIRED",
        "PRODUCTION_AGGREGATES_NOT_ACQUIRED",
        "ENTITY_ARTIFACT_AVAILABLE",
        "D_STAR_NOT_ASSIGNED_AT_SCREENING",
        "PERSISTENCE_ONLY",
        "ROUTE_CHANGING_EVIDENCE_UNRESOLVED",
    }
)
SECTOR_PROFILES = frozenset(
    {
        "coated_steel",
        "technical_plastics",
        "pharma_api",
        "fertilizers",
        "fabricated_aluminium",
    }
)


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ScreeningConfigurationError(f"{path.name} must be a mapping")
    return value


def validate_screening_config(value: dict[str, Any]) -> None:
    if value.get("metadata", {}).get("version") != "1.0.0":
        raise ScreeningConfigurationError("screening version must be 1.0.0")
    if tuple(value.get("queues", {})) != QUEUE_IDS:
        raise ScreeningConfigurationError("screening queues must match governed ids")
    vocab = value.get("vocabularies", {})
    if tuple(vocab.get("dispositions", ())) != DISPOSITIONS:
        raise ScreeningConfigurationError("disposition vocabulary mismatch")
    if set(vocab.get("indicated_states", ())) != set(INDICATED_STATES):
        raise ScreeningConfigurationError("indicated-state vocabulary mismatch")
    if set(vocab.get("reason_codes", ())) != REASON_CODES:
        raise ScreeningConfigurationError("reason-code vocabulary mismatch")
    robust = value["queues"]["robust_public_finding"]
    if (
        isinstance(robust.get("minimum_fired_material_signals"), bool)
        or not isinstance(robust.get("minimum_fired_material_signals"), int)
        or robust["minimum_fired_material_signals"] <= 0
    ):
        raise ScreeningConfigurationError("minimum signals must be a positive int")
    for key, amount in value.get("budgets", {}).items():
        if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
            raise ScreeningConfigurationError(f"budget {key} must be a positive int")
    api = value.get("api", {})
    if not all(
        isinstance(api.get(key), int) and not isinstance(api.get(key), bool)
        and api[key] > 0
        for key in ("page_size_default", "page_size_max")
    ) or api["page_size_default"] > api["page_size_max"]:
        raise ScreeningConfigurationError("invalid API page sizes")


def validate_product_families(value: dict[str, Any]) -> None:
    if value.get("metadata", {}).get("version") != "1.0.0":
        raise ScreeningConfigurationError("product-family version must be 1.0.0")
    seen: set[str] = set()
    for family_id, family in value.get("families", {}).items():
        if family.get("sector_profile") not in SECTOR_PROFILES:
            raise ScreeningConfigurationError(f"invalid sector profile: {family_id}")
        headings = family.get("hs4_headings")
        if not isinstance(headings, list):
            raise ScreeningConfigurationError("hs4_headings must be a list")
        expected = "AVAILABLE" if headings else "MEMBERSHIP_UNAVAILABLE"
        if family.get("status") != expected or not family.get("basis"):
            raise ScreeningConfigurationError("family membership must be cited or unavailable")
        for heading in headings:
            if not isinstance(heading, str) or re.fullmatch(r"\d{4}", heading) is None:
                raise ScreeningConfigurationError("invalid HS4 heading")
            if heading in seen:
                raise ScreeningConfigurationError("HS4 membership must be unique")
            seen.add(heading)


@lru_cache(maxsize=1)
def screening_config() -> dict[str, Any]:
    value = _load(PROJECT_ROOT / "config" / "screening.v1.yaml")
    validate_screening_config(value)
    return value


@lru_cache(maxsize=1)
def product_families_config() -> dict[str, Any]:
    value = _load(PROJECT_ROOT / "config" / "product_families.v1.yaml")
    validate_product_families(value)
    return value


def family_for_hs6(
    hs6: str, value: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    matches = []
    for family_id, family in (value or product_families_config())["families"].items():
        if any(hs6.startswith(heading) for heading in family["hs4_headings"]):
            matches.append({"family_id": family_id, **family})
    if len(matches) > 1:
        raise ScreeningConfigurationError("HS6 maps to multiple families")
    return matches[0] if matches else None
