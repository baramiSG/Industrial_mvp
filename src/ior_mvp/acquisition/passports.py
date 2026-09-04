"""Acquired evidence passport builder."""

from __future__ import annotations

from typing import Any, Sequence

from ..public_decision import SUPPORT_CODES
from .contracts import CoverageRecord, SourceContractRecord, UNAVAILABLE

ACQUIRED_SUPPORT_CODES = SUPPORT_CODES | {"NATIONAL_TARIFF_LINE_MAPPING"}


def build_acquired_passport(
    contracts: Sequence[SourceContractRecord],
    coverage: CoverageRecord,
    *,
    source_config: dict[str, Any],
    supports: list[str],
    transformation_record: dict[str, Any],
    observation_context: dict[str, Any],
    measurement: dict[str, Any],
    contradiction_record: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build one acquired evidence passport with eight §11 groups."""
    first = contracts[0] if contracts else None
    return {
        "passport_id": (
            f"{coverage.source_id}-{coverage.query_hash[:12]}-{coverage.run_id}"
        ),
        "source_id": coverage.source_id,
        "synthetic_flag": False,
        "status": "observed",
        "evidence_class": source_config["default_evidence_class"],
        "reviewer_status": source_config["default_reviewer_status"],
        "supports": supports,
        "source_identity": {
            "source_id": coverage.source_id,
            "authority": source_config.get("authority", UNAVAILABLE),
            "access_classification": source_config.get(
                "access_classification", UNAVAILABLE
            ),
            "documentation_reference": source_config.get(
                "documentation_reference", UNAVAILABLE
            ),
            "terms_reference": source_config.get("terms_reference", UNAVAILABLE),
            "license_or_usage_note": (
                first.license_or_usage_note if first else UNAVAILABLE
            ),
        },
        "query_contract": {
            "query_hash": coverage.query_hash,
            "run_id": coverage.run_id,
            "stage": coverage.stage.value,
            "unit_key": list(coverage.unit_key),
        },
        "retrieval": {
            "retrieved_at": first.retrieved_at if first else UNAVAILABLE,
            "source_refresh_date": (
                first.source_refresh_date if first else UNAVAILABLE
            ),
            "endpoint_or_document": (
                first.endpoint_or_document if first else UNAVAILABLE
            ),
        },
        "coverage": coverage.to_json(),
        "transformation_record": transformation_record,
        "observation_context": observation_context,
        "measurement": measurement,
        "contradiction_record": contradiction_record,
    }


def assert_passport_complete(passport: dict[str, Any]) -> None:
    """Fail closed when passport is incomplete or invalid."""
    required_top = (
        "passport_id",
        "source_id",
        "synthetic_flag",
        "status",
        "evidence_class",
        "reviewer_status",
        "supports",
        "source_identity",
        "query_contract",
        "retrieval",
        "coverage",
        "transformation_record",
        "observation_context",
        "measurement",
        "contradiction_record",
    )
    for key in required_top:
        if key not in passport:
            raise ValueError(f"Passport missing key: {key}")

    if passport["synthetic_flag"] is not False:
        raise ValueError("Passport synthetic_flag must be False")

    evidence_class = passport["evidence_class"]
    if evidence_class not in {"A", "B", "C", "D", "E"}:
        raise ValueError(f"Invalid evidence_class: {evidence_class}")

    supports = passport["supports"]
    if not isinstance(supports, list) or not supports:
        raise ValueError("Passport supports must be non-empty")
    if len(supports) != len(set(supports)):
        raise ValueError("Passport supports must be unique")
    unknown = set(supports) - ACQUIRED_SUPPORT_CODES
    if unknown:
        raise ValueError(f"Unknown support codes: {sorted(unknown)}")

    for group in (
        "source_identity",
        "query_contract",
        "retrieval",
        "coverage",
        "transformation_record",
        "observation_context",
        "measurement",
    ):
        value = passport[group]
        if not isinstance(value, dict):
            raise ValueError(f"Passport group must be mapping: {group}")
