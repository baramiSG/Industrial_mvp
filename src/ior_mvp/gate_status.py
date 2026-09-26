"""Finite hard-gate status classifier.

One case-folded prefix grammar serves capability, simulation and graph
projection. Raw scenario and snapshot declarations stay in their records.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class GateStatus(StrEnum):
    """Canonical hard-gate status."""

    RESOLVED = "RESOLVED"
    KNOWN_FAILURE = "KNOWN_FAILURE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNAVAILABLE = "UNAVAILABLE"


_PREFIXES: tuple[tuple[str, GateStatus], ...] = (
    ("resolved", GateStatus.RESOLVED),
    ("known failure", GateStatus.KNOWN_FAILURE),
    ("known_failure", GateStatus.KNOWN_FAILURE),
    ("not applicable", GateStatus.NOT_APPLICABLE),
    ("not_applicable", GateStatus.NOT_APPLICABLE),
)


def classify_gate_status(raw: Any) -> GateStatus:
    """Classify one declaration without rewriting it.

    Dict values are classified from their ``status`` field. Matching is a
    case-folded prefix of the declaration text. Typed ``NOT_APPLICABLE``
    stays non-applicable. Anything else is unavailable.
    """
    if isinstance(raw, dict):
        return classify_gate_status(raw.get("status"))
    if not isinstance(raw, str):
        return GateStatus.UNAVAILABLE
    text = raw.casefold()
    for prefix, status in _PREFIXES:
        if text.startswith(prefix):
            return status
    return GateStatus.UNAVAILABLE
