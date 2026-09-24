from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT
from browser_tests.parity_grammar import (
    LATIN_PROSE,
    LATIN_RUN,
    classify_island,
    label_leaks,
    normalize,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("030579", "hs_code"),
        ("3f892bf254a9", "hex_digest"),
        (
            "3f892bf254a9c9c141cc413a24a9c82a771a56aff8d883c53b53c59b46283859",
            "hex_digest",
        ),
        ("20260912T143742Z", "run_id"),
        ("2026-09-12", "iso_datetime"),
        ("2026-09-12T14:37:52Z", "iso_datetime"),
        (
            "https://comtradeapi.un.org/data/v1/get/C/A/HS?reporterCode=682",
            "url",
        ),
        ("1.2.0", "version"),
        ("SCREENING-SAU-2026-09-12-9b6b22032fd8", "governed_id"),
        (
            "un_comtrade-37d131466dff-20260912T143742Z",
            "governed_id",
        ),
        ("R4-F", "governed_id"),
        ("EX-01_HETEROGENEOUS_RESIDUAL", "governed_id"),
        ("UNIVERSE", "code_token"),
        ("B", "code_token"),
        ("NO_CANDIDATE", "code_token"),
        (
            "PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000",
            "code_token",
        ),
        ("FIX-PUBLIC-NO-CANDIDATE", "code_token"),
        ("un_comtrade", "catalogue_key"),
        ("robust_public_finding", "catalogue_key"),
        ("unconfirmed_by_responsible_authority", "catalogue_key"),
        ("5443", "number"),
        ("1,234.5", "number"),
        ("12.5 %", "number"),
        ("−0.42", "number"),
        ("1–50", "number_range"),
    ],
)
def test_technical_value_grammar_classifies_known_values(
    value: str,
    expected: str,
) -> None:
    assert classify_island(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "Evidence not acquired for this line",
        "re-export",
        "Not acquired",
        "imports",
        "Route-changing evidence",
    ],
)
def test_technical_value_grammar_rejects_prose_and_hyphenated_words(
    value: str,
) -> None:
    assert classify_island(value) == "unclassified"


def test_technical_value_grammar_rejects_empty_island() -> None:
    assert classify_island("") == "empty"


@pytest.mark.parametrize(
    ("value", "prose", "latin"),
    [
        ("one two", False, True),
        ("one two three", True, True),
        ("HS 6 code", False, True),
        ("a b c", True, False),
    ],
)
def test_latin_prose_regex_boundaries(
    value: str,
    prose: bool,
    latin: bool,
) -> None:
    assert bool(LATIN_PROSE.search(value)) is prose
    assert bool(LATIN_RUN.search(value)) is latin


def test_normalize_removes_bidi_controls_and_collapses_space() -> None:
    assert normalize("\u2066  A\u00a0  B  \u2069") == "A B"


def _fixture() -> list[dict]:
    path = (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "parity"
        / "parity-negative-cases.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _html_text(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def test_parity_negative_fixture_classes_match_grammar() -> None:
    for row in _fixture():
        if row["kind"] != "island":
            continue
        value = _html_text(row["html"])
        if "class" in row["expect"]:
            assert classify_island(value) == row["expect"]["class"]


def test_parity_grammar_documented_residuals() -> None:
    for value in ("THE", "AND", "NOT"):
        assert classify_island(value) == "code_token"
    for value in ("not_acquired", "route_changing", "not.acquired"):
        assert classify_island(value) == "catalogue_key"
    for value in ("Chapter-1", "HS-6"):
        assert classify_island(value) == "governed_id"


def _real_english_values() -> set[str]:
    ui = yaml.safe_load(
        (PROJECT_ROOT / "config" / "ui_strings.v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    narratives = yaml.safe_load(
        (
            PROJECT_ROOT / "config" / "decision_narratives.v1.yaml"
        ).read_text(encoding="utf-8")
    )
    return set(ui["strings"]["en"].values()) | set(
        narratives["templates"]["en"].values()
    )


def test_label_leak_detects_english_label_disguised_as_code() -> None:
    islands = [
        {"text": "NOT_ACQUIRED", "class": "code_token"},
        {"text": "not_acquired", "class": "catalogue_key"},
    ]
    assert label_leaks(islands, {"Not acquired"}) == [
        "NOT_ACQUIRED",
        "not_acquired",
    ]
    real = _real_english_values()
    safe = [
        {"text": "un_comtrade", "class": "catalogue_key"},
        {"text": "NO_CANDIDATE", "class": "code_token"},
        {"text": "R4-F", "class": "governed_id"},
    ]
    assert label_leaks(safe, real) == []
    assert label_leaks(
        [{"text": "NOT_CALCULABLE", "class": "code_token"}],
        real,
    ) == ["NOT_CALCULABLE"]


@pytest.mark.parametrize(('value', 'expected'), [
    ('SYN-MINISTRY-ALU-FOIL-001::shared_enabler', 'synthetic_evidence_id'),
    ('SYN-MINISTRY-STEEL-001::capacity', 'synthetic_evidence_id'),
    ('2021/2023/2024', 'period_years'), ('2023/2024', 'period_years'),
])
def test_passport_technical_grammar_accepts_only_exact_composite_ids_and_years(value, expected):
    assert classify_island(value) == expected


@pytest.mark.parametrize('value', [
    'Hadeed', 'Universal Metal Coating Company', 'ordinary English source',
    'SYN-MINISTRY-ALU-FOIL-001:shared_enabler', 'SYN-MINISTRY-ALU-FOIL-001:::shared_enabler',
    'FAKE-MINISTRY-ALU-FOIL-001::shared_enabler', 'SYN-MINISTRY-ALU-FOIL-001::',
    'SYN-MINISTRY-ALU-FOIL-001::shared-enabler', 'SYN-MINISTRY-ALU-FOIL-001::shared enabler',
    '2024/source', 'source/2024', '2024A/2025', '2024//2025',
])
def test_passport_technical_grammar_rejects_prose_and_malformed_lookalikes(value):
    assert classify_island(value) == 'unclassified'
