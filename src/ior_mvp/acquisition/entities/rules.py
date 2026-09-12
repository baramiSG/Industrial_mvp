"""Load the versioned entity-resolution rule table fail closed."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ...config import PROJECT_ROOT
from ..contracts import AcquisitionError

ENTITY_RULES_PATH = PROJECT_ROOT / "config" / "entity_resolution.v1.yaml"

ENTITY_TYPES = ("COMPANY", "PLANT", "LINE", "LICENCE_HOLDER")
LINK_STATUSES = (
    "DETERMINISTIC_IDENTIFIER",
    "EXACT_DOCUMENT_EVIDENCE",
    "PROPOSED_PENDING_REVIEW",
    "UNRESOLVED",
)
RESOLVED_STATUSES = LINK_STATUSES[:2]
IDENTIFIER_KINDS = (
    "COMMERCIAL_REGISTRATION",
    "INDUSTRIAL_LICENCE_NUMBER",
    "TADAWUL_ISSUER_CODE",
)
UNRESOLVED_REASONS = (
    "OUT_OF_SCOPE_ENTITY_TYPE",
    "COUNT_ONLY_NO_IDENTITY",
    "NO_MENTION_RECORDED",
    "LOCALITY_NOT_IN_TABLE",
    "NO_SUBJECT_ENTITY",
    "OWNER_UNNAMED",
)

_TOP_KEYS = {
    "metadata",
    "id_scheme",
    "normalisation",
    "linking",
    "localities",
    "span_screen",
}
_METADATA_KEYS = {
    "artifact",
    "version",
    "effective_date",
    "authority",
    "status",
    "change_gate",
}
_ID_KEYS = {"name", "hash", "hex_length", "entity_types"}
_NORMALISATION_KEYS = {"method_id", "version", "exact", "variant"}
_EXACT_KEYS = {
    "unicode_form",
    "casefold",
    "strip_arabic_tashkeel",
    "strip_tatweel",
    "fold_arabic_indic_digits",
    "punctuation_to_space",
    "collapse_whitespace",
}
_VARIANT_KEYS = {
    "arabic_letter_folds",
    "definite_article",
    "legal_form_tokens_en",
    "legal_form_tokens_ar",
    "transliteration_variants",
}
_LINKING_KEYS = {
    "precedence",
    "resolved_statuses",
    "plant_subject_window_lines",
    "identifier_kinds",
    "unresolved_reasons",
}
_LOCALITY_KEYS = {"canonical_en", "variants_en", "variants_ar"}
_SPAN_SCREEN_KEYS = {"forbidden_substrings_casefold"}
_EXPECTED_PUNCTUATION = (
    ".",
    ",",
    ";",
    ":",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    '"',
    "'",
    "&",
    "-",
    "_",
    "/",
    "\\",
    "«",
    "»",
    "“",
    "”",
    "‘",
    "’",
    "،",
    "؛",
)
_EXPECTED_ARABIC_FOLDS = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ى": "ي",
    "ة": "ه",
}
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class EntityResolutionError(AcquisitionError):
    """Entity-resolution input or artifact failed a governed contract."""


@dataclass(frozen=True)
class EntityRules:
    version: str
    id_scheme: str
    entity_types: tuple[str, ...]
    exact: dict[str, Any]
    variant: dict[str, Any]
    precedence: tuple[str, ...]
    resolved_statuses: tuple[str, ...]
    plant_subject_window_lines: int
    identifier_kinds: tuple[str, ...]
    unresolved_reasons: tuple[str, ...]
    localities: dict[str, dict[str, Any]]
    span_forbidden_substrings: tuple[str, ...]
    raw: dict[str, Any]


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EntityResolutionError(f"{field} must be a mapping")
    return value


def _require_exact_keys(value: dict[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        unknown = sorted(actual - expected)
        missing = sorted(expected - actual)
        raise EntityResolutionError(
            f"{field} has unknown keys {unknown} or missing keys {missing}"
        )


def _require_string_list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise EntityResolutionError(f"{field} must be a list of non-empty strings")
    return value


def _require_string_mapping(value: Any, field: str) -> dict[str, str]:
    mapping = _require_mapping(value, field)
    if not mapping or not all(
        isinstance(key, str)
        and key
        and isinstance(item, str)
        and item
        for key, item in mapping.items()
    ):
        raise EntityResolutionError(f"{field} must map non-empty strings")
    return mapping


def _validate_payload(payload: dict[str, Any]) -> None:
    _require_exact_keys(payload, _TOP_KEYS, "root")

    metadata = _require_mapping(payload["metadata"], "metadata")
    _require_exact_keys(metadata, _METADATA_KEYS, "metadata")
    expected_metadata = {
        "artifact": "industrial-opportunity-entity-resolution",
        "version": "1.0.0",
        "authority": "Methodology §3.2, §11; Core 04 §2.4/§4; Core 05 §6.5; Core 08 §10",
        "status": "frozen_for_demo_cycle",
        "change_gate": "Manifest §7.3 + ADR",
    }
    for key, expected in expected_metadata.items():
        if metadata[key] != expected:
            raise EntityResolutionError(f"metadata.{key} must be {expected!r}")
    if not isinstance(metadata["effective_date"], str) or not _ISO_DATE.fullmatch(
        metadata["effective_date"]
    ):
        raise EntityResolutionError("metadata.effective_date must be ISO YYYY-MM-DD")

    id_scheme = _require_mapping(payload["id_scheme"], "id_scheme")
    _require_exact_keys(id_scheme, _ID_KEYS, "id_scheme")
    if (
        id_scheme["name"] != "ENTITY_ID_V1"
        or id_scheme["hash"] != "sha256"
        or id_scheme["hex_length"] != 16
        or id_scheme["entity_types"] != list(ENTITY_TYPES)
    ):
        raise EntityResolutionError("id_scheme does not match ENTITY_ID_V1")

    normalisation = _require_mapping(payload["normalisation"], "normalisation")
    _require_exact_keys(normalisation, _NORMALISATION_KEYS, "normalisation")
    if normalisation["method_id"] != "NAME_NORMALISATION_V1":
        raise EntityResolutionError("normalisation.method_id must be NAME_NORMALISATION_V1")
    if normalisation["version"] != "1.0.0":
        raise EntityResolutionError("normalisation.version must be 1.0.0")

    exact = _require_mapping(normalisation["exact"], "normalisation.exact")
    _require_exact_keys(exact, _EXACT_KEYS, "normalisation.exact")
    if exact["unicode_form"] != "NFC":
        raise EntityResolutionError("normalisation.exact.unicode_form must be NFC")
    for key in (
        "casefold",
        "strip_arabic_tashkeel",
        "strip_tatweel",
        "fold_arabic_indic_digits",
        "collapse_whitespace",
    ):
        if type(exact[key]) is not bool:
            raise EntityResolutionError(f"normalisation.exact.{key} must be boolean")
    punctuation = _require_string_list(
        exact["punctuation_to_space"], "normalisation.exact.punctuation_to_space"
    )
    if tuple(punctuation) != _EXPECTED_PUNCTUATION or len(set(punctuation)) != len(punctuation):
        raise EntityResolutionError("normalisation.exact.punctuation_to_space is not the frozen list")

    variant = _require_mapping(normalisation["variant"], "normalisation.variant")
    _require_exact_keys(variant, _VARIANT_KEYS, "normalisation.variant")
    if _require_string_mapping(
        variant["arabic_letter_folds"], "normalisation.variant.arabic_letter_folds"
    ) != _EXPECTED_ARABIC_FOLDS:
        raise EntityResolutionError("normalisation.variant.arabic_letter_folds is not frozen")
    definite = _require_mapping(
        variant["definite_article"], "normalisation.variant.definite_article"
    )
    _require_exact_keys(definite, {"ar_prefix", "en_tokens"}, "definite_article")
    if definite["ar_prefix"] != "ال" or definite["en_tokens"] != ["the", "al"]:
        raise EntityResolutionError("normalisation.variant.definite_article is not frozen")
    _require_string_list(variant["legal_form_tokens_en"], "legal_form_tokens_en")
    _require_string_list(variant["legal_form_tokens_ar"], "legal_form_tokens_ar")
    _require_string_mapping(variant["transliteration_variants"], "transliteration_variants")

    linking = _require_mapping(payload["linking"], "linking")
    _require_exact_keys(linking, _LINKING_KEYS, "linking")
    enum_expectations = {
        "precedence": list(LINK_STATUSES),
        "resolved_statuses": list(RESOLVED_STATUSES),
        "identifier_kinds": list(IDENTIFIER_KINDS),
        "unresolved_reasons": list(UNRESOLVED_REASONS),
    }
    for key, expected in enum_expectations.items():
        if linking[key] != expected:
            raise EntityResolutionError(f"linking.{key} must be {expected!r}")
    if type(linking["plant_subject_window_lines"]) is not int or linking[
        "plant_subject_window_lines"
    ] != 2:
        raise EntityResolutionError("linking.plant_subject_window_lines must be 2")

    localities = _require_mapping(payload["localities"], "localities")
    if set(localities) != {"SAU-JUBAIL", "SAU-JEDDAH"}:
        raise EntityResolutionError("localities must contain the two frozen locality tokens")
    for token, raw_locality in localities.items():
        locality = _require_mapping(raw_locality, f"localities.{token}")
        _require_exact_keys(locality, _LOCALITY_KEYS, f"localities.{token}")
        if not isinstance(locality["canonical_en"], str) or not locality["canonical_en"]:
            raise EntityResolutionError(f"localities.{token}.canonical_en must be non-empty")
        _require_string_list(
            locality["variants_en"], f"localities.{token}.variants_en", allow_empty=True
        )
        _require_string_list(
            locality["variants_ar"], f"localities.{token}.variants_ar", allow_empty=True
        )

    span_screen = _require_mapping(payload["span_screen"], "span_screen")
    _require_exact_keys(span_screen, _SPAN_SCREEN_KEYS, "span_screen")
    forbidden = _require_string_list(
        span_screen["forbidden_substrings_casefold"],
        "span_screen.forbidden_substrings_casefold",
    )
    if forbidden != [
        "@",
        "contact name",
        "e-mail",
        "email",
        "phone",
        "mobile",
        "p.o.box",
        "p.o. box",
    ]:
        raise EntityResolutionError("span_screen.forbidden_substrings_casefold is not frozen")


def rules_sha256(path: Path = ENTITY_RULES_PATH) -> str:
    """Return the hash of the exact rule-table bytes."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise EntityResolutionError(f"Cannot read entity rules: {path}") from exc


def load_entity_rules(path: Path = ENTITY_RULES_PATH) -> EntityRules:
    """Load one rules file without caching and reject any schema drift."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise EntityResolutionError(f"Cannot load entity rules: {path}") from exc
    if not isinstance(payload, dict):
        raise EntityResolutionError("Entity rules root must be a mapping")
    _validate_payload(payload)
    normalisation = payload["normalisation"]
    linking = payload["linking"]
    return EntityRules(
        version=payload["metadata"]["version"],
        id_scheme=payload["id_scheme"]["name"],
        entity_types=tuple(payload["id_scheme"]["entity_types"]),
        exact=normalisation["exact"],
        variant=normalisation["variant"],
        precedence=tuple(linking["precedence"]),
        resolved_statuses=tuple(linking["resolved_statuses"]),
        plant_subject_window_lines=linking["plant_subject_window_lines"],
        identifier_kinds=tuple(linking["identifier_kinds"]),
        unresolved_reasons=tuple(linking["unresolved_reasons"]),
        localities=payload["localities"],
        span_forbidden_substrings=tuple(
            payload["span_screen"]["forbidden_substrings_casefold"]
        ),
        raw=payload,
    )


@lru_cache(maxsize=1)
def entity_resolution_rules() -> EntityRules:
    """Return the validated repository rule table."""
    return load_entity_rules(ENTITY_RULES_PATH)
