from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


BIDI_CONTROLS = re.compile(
    "[\u200e\u200f\u202a-\u202e\u2066-\u2069]"
)
WHITESPACE = re.compile(r"\s+")
LATIN_PROSE = re.compile(
    r"[A-Za-z]+(?:\s+[A-Za-z]+){2,}"
)
LATIN_RUN = re.compile(r"[A-Za-z]{2,}")

CLASS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("hs_code", re.compile(r"\d{6}")),
    ("hex_digest", re.compile(r"[0-9a-f]{12}|[0-9a-f]{64}")),
    ("run_id", re.compile(r"\d{8}T\d{6}Z")),
    (
        "iso_datetime",
        re.compile(
            r"\d{4}-\d{2}-\d{2}"
            r"(?:T\d{2}:\d{2}:\d{2}Z)?"
        ),
    ),
    ("url", re.compile(r"https?://\S+")),
    ("version", re.compile(r"v?\d+\.\d+\.\d+")),
    (
        "governed_id",
        re.compile(
            r"(?=.*\d)[A-Za-z][A-Za-z0-9_]*"
            r"(?:-[A-Za-z0-9_]+)+"
        ),
    ),
    (
        "code_token",
        re.compile(r"[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)*"),
    ),
    (
        "catalogue_key",
        re.compile(r"[a-z][a-z0-9]*(?:[._][a-z0-9]+)+"),
    ),
    (
        "number",
        re.compile(
            r"[-+−]?\d[\d,.\u066b\u066c]*"
            r"(?:\s?(?:%|kt|USD m|USD|×))?"
        ),
    ),
    (
        "number_range",
        re.compile(r"\d[\d,.]*\s?[–-]\s?\d[\d,.]*"),
    ),
]


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFC", str(text))
    value = BIDI_CONTROLS.sub("", value).replace("\u00a0", " ")
    return WHITESPACE.sub(" ", value).strip()


def classify_island(text: str) -> str:
    value = normalize(text)
    if not value:
        return "empty"
    for name, pattern in CLASS_PATTERNS:
        if pattern.fullmatch(value):
            return name
    return "unclassified"


def _label_key(text: str) -> str:
    value = normalize(text).lower()
    value = re.sub(r"[_.-]+", " ", value)
    return WHITESPACE.sub(" ", value).strip()


def label_leaks(
    islands: Iterable[dict[str, str]],
    en_values: Iterable[str],
) -> list[str]:
    labels = {_label_key(value) for value in en_values}
    guarded = {"code_token", "catalogue_key", "governed_id"}
    leaks: list[str] = []
    for island in islands:
        text = normalize(island.get("text", ""))
        if (
            island.get("class") in guarded
            and _label_key(text) in labels
        ):
            leaks.append(text)
    return leaks
