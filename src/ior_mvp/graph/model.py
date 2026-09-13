"""Governed property-graph vocabulary and deterministic identifiers."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Any


class GraphModelError(ValueError):
    """Raised when an element is outside the governed graph vocabulary."""


@dataclass
class GraphNode:
    """One node in the governed projection."""

    label: str
    id: str
    properties: dict[str, Any]


@dataclass
class GraphEdge:
    """One directed relationship in the governed projection."""

    type: str
    source: str
    target: str
    key: str
    properties: dict[str, Any]


LABELS: tuple[str, ...] = (
    "Product",
    "TariffLine",
    "Specification",
    "Application",
    "Plant",
    "ProductionLine",
    "Process",
    "Equipment",
    "Capability",
    "Standard",
    "Certification",
    "Input",
    "Technology",
    "Company",
    "CustomerSegment",
    "Evidence",
    "Scenario",
    "Decision",
    "Intervention",
)

EDGE_TYPES: tuple[str, ...] = (
    "CLASSIFIED_AS",
    "REQUIRES_SPECIFICATION",
    "USED_IN",
    "PRODUCED_BY",
    "HAS_LINE",
    "USES_PROCESS",
    "HAS_CAPABILITY",
    "REQUIRES_INPUT",
    "CERTIFIED_TO",
    "QUALIFIED_FOR",
    "DEPENDS_ON",
    "ADJACENT_TO",
    "SUPPORTED_BY_EVIDENCE",
    "CONSTRAINED_BY",
    "UNLOCKED_BY",
)

_ALL_TO_EVIDENCE = frozenset((label, "Evidence") for label in LABELS)

ENDPOINT_RULES: dict[str, frozenset[tuple[str, str]]] = {
    "CLASSIFIED_AS": frozenset({("Product", "TariffLine")}),
    "REQUIRES_SPECIFICATION": frozenset(
        {
            ("Product", "Specification"),
            ("Application", "Specification"),
        }
    ),
    "USED_IN": frozenset({("Product", "Application")}),
    "PRODUCED_BY": frozenset(
        {
            ("Product", "Plant"),
            ("Product", "Company"),
            ("Product", "ProductionLine"),
        }
    ),
    "HAS_LINE": frozenset({("Plant", "ProductionLine")}),
    "USES_PROCESS": frozenset(
        {
            ("Plant", "Process"),
            ("ProductionLine", "Process"),
            ("Company", "Process"),
        }
    ),
    "HAS_CAPABILITY": frozenset({("Product", "Capability")}),
    "REQUIRES_INPUT": frozenset(
        {
            ("Process", "Input"),
            ("ProductionLine", "Input"),
        }
    ),
    "CERTIFIED_TO": frozenset(
        {
            ("Plant", "Certification"),
            ("Plant", "Standard"),
            ("Company", "Certification"),
            ("Company", "Standard"),
        }
    ),
    "QUALIFIED_FOR": frozenset(
        {
            ("Plant", "Specification"),
            ("Plant", "Application"),
            ("ProductionLine", "Specification"),
            ("ProductionLine", "Application"),
            ("Company", "Specification"),
            ("Company", "Application"),
            ("CustomerSegment", "Application"),
        }
    ),
    "DEPENDS_ON": frozenset(
        {
            ("Product", "Product"),
            ("Product", "Input"),
            ("Product", "Technology"),
            ("Product", "Process"),
            ("Process", "Equipment"),
            ("Decision", "Intervention"),
        }
    ),
    "ADJACENT_TO": frozenset(
        {
            ("Plant", "Product"),
            ("Company", "Product"),
        }
    ),
    "SUPPORTED_BY_EVIDENCE": _ALL_TO_EVIDENCE,
    "CONSTRAINED_BY": frozenset(
        {
            ("Intervention", "Capability"),
            ("Intervention", "Specification"),
            ("Intervention", "Standard"),
            ("Intervention", "Certification"),
            ("Decision", "Product"),
            ("Decision", "Specification"),
            ("Decision", "Capability"),
            ("Decision", "Intervention"),
            ("Specification", "Standard"),
            ("Product", "Capability"),
        }
    ),
    "UNLOCKED_BY": frozenset({("Product", "Intervention")}),
}

PROVENANCE_KEYS: tuple[str, ...] = (
    "evidence_id",
    "as_of",
    "evidence_class",
    "synthetic_flag",
    "scenario_id",
)

ORIGIN_KINDS: frozenset[str] = frozenset(
    {
        "PUBLIC_SNAPSHOT",
        "SCENARIO",
        "ENTITY_ARTIFACT",
        "CASE_BRIEF",
        "ACQUISITION_ATTEMPT",
        "ENGINE_RUN",
    }
)

V1_TO_V2_NODE_MAPPING: dict[str, str] = {
    "Product": "Product",
    "Specification": "Specification",
    "Application": "Application",
    "Standard": "Standard",
    "Plant": "Plant",
    "ProductionLine": "ProductionLine",
    "Process": "Process",
    "Equipment": "Equipment",
    "Certification": "Certification",
    "Buyer": "CustomerSegment",
    "Input": "Input",
    "Utility": "Input",
    "Technology": "Technology",
    "Opportunity": "Product",
    "Intervention": "Intervention",
    "Evidence": "Evidence",
    "Decision": "Decision",
}

V1_TO_V2_EDGE_MAPPING: dict[str, str] = {
    "HAS_SPECIFICATION": "REQUIRES_SPECIFICATION",
    "USED_IN": "USED_IN",
    "REQUIRES_STANDARD": "CONSTRAINED_BY",
    "PRODUCED_BY": "PRODUCED_BY",
    "HAS_LINE": "HAS_LINE",
    "USES_PROCESS": "USES_PROCESS",
    "REQUIRES_EQUIPMENT": "DEPENDS_ON",
    "QUALIFIED_BY": "CERTIFIED_TO",
    "DEMANDED_BY": "USED_IN + QUALIFIED_FOR",
    "DEPENDS_ON": "DEPENDS_ON",
    "SUPPORTED_BY_EVIDENCE": "SUPPORTED_BY_EVIDENCE",
    "BLOCKED_BY": "CONSTRAINED_BY",
    "UNLOCKED_BY": "UNLOCKED_BY",
    "ALTERNATIVE_TO": "RETIRED",
}

_SLUG_SEPARATOR = re.compile(r"[^a-z0-9]+")


def slug(value: str) -> str:
    """Return a stable ASCII slug, with a hash fallback for non-ASCII text."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").casefold()
    result = _SLUG_SEPARATOR.sub("-", ascii_value).strip("-")
    if result:
        return result
    return "u-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def capability_id(subject_id: str, dimension: str) -> str:
    """Return the governed Capability identifier."""
    return f"CAP-{subject_id}-{slug(dimension)}"


def assert_endpoint(source_label: str, edge_type: str, target_label: str) -> None:
    """Reject an edge outside the governed endpoint contract."""
    if edge_type not in ENDPOINT_RULES:
        raise GraphModelError(f"Unknown governed edge type: {edge_type}")
    if (source_label, target_label) not in ENDPOINT_RULES[edge_type]:
        raise GraphModelError(
            "Invalid governed endpoint pair: "
            f"{source_label}-[:{edge_type}]->{target_label}"
        )


def relationship_key(
    edge_type: str,
    source: str,
    target: str,
    discriminator: str = "",
) -> str:
    """Return a deterministic relationship key."""
    basis = "\x1f".join((edge_type, source, target, discriminator))
    return f"REL-{hashlib.sha256(basis.encode('utf-8')).hexdigest()[:20]}"
