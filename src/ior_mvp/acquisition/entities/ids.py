"""Stable ENTITY_ID_V1 canonical keys and identifiers."""

from __future__ import annotations

import hashlib
import re

from .rules import EntityResolutionError

ENTITY_ID_SCHEME = "ENTITY_ID_V1"
ENTITY_TYPES = ("COMPANY", "PLANT", "LINE", "LICENCE_HOLDER")
ENTITY_ID_PATTERN = re.compile(
    r"^(COMPANY|PLANT|LINE|LICENCE_HOLDER)-[0-9a-f]{16}$"
)


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise EntityResolutionError(f"{field} must be a non-empty string")
    return value


def company_key(primary_exact: str) -> str:
    return f"{ENTITY_ID_SCHEME}|COMPANY|{_nonempty(primary_exact, 'primary_exact')}"


def licence_holder_key(name_exact: str) -> str:
    return (
        f"{ENTITY_ID_SCHEME}|LICENCE_HOLDER|"
        f"{_nonempty(name_exact, 'name_exact')}"
    )


def plant_key(company_entity_id: str, locality_token: str) -> str:
    company = _nonempty(company_entity_id, "company_entity_id")
    if not company.startswith("COMPANY-"):
        raise EntityResolutionError("company_entity_id must use the COMPANY namespace")
    return (
        f"{ENTITY_ID_SCHEME}|PLANT|{company}|"
        f"{_nonempty(locality_token, 'locality_token')}"
    )


def line_key(plant_entity_id: str, designation_exact: str) -> str:
    plant = _nonempty(plant_entity_id, "plant_entity_id")
    if not plant.startswith("PLANT-"):
        raise EntityResolutionError("plant_entity_id must use the PLANT namespace")
    return (
        f"{ENTITY_ID_SCHEME}|LINE|{plant}|"
        f"{_nonempty(designation_exact, 'designation_exact')}"
    )


def entity_id(entity_type: str, canonical_key: str) -> str:
    if entity_type not in ENTITY_TYPES:
        raise EntityResolutionError(f"Unsupported entity type: {entity_type!r}")
    key = _nonempty(canonical_key, "canonical_key")
    expected_prefix = f"{ENTITY_ID_SCHEME}|{entity_type}|"
    if not key.startswith(expected_prefix):
        raise EntityResolutionError(
            f"canonical_key must start with {expected_prefix!r}"
        )
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return f"{entity_type}-{digest}"
