from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT


client = TestClient(app)
DISCLOSURE = "SIMULATED — NOT MINISTRY EVIDENCE"
ARABIC_DISCLOSURE = "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"


def _ui_strings(locale: str) -> dict[str, str]:
    payload = yaml.safe_load(
        (
            PROJECT_ROOT / "config" / "ui_strings.v1.yaml"
        ).read_text(encoding="utf-8")
    )
    return payload["strings"][locale]


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_real_dossier_has_no_disclosure_and_zero_synthetic_rows(
    opportunity_id: str,
) -> None:
    json_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier"
        "?mode=public"
    )
    html_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier.html"
        "?mode=public"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert dossier["synthetic_disclosure"] is None
    assert dossier["evidence_summary"]["synthetic_records"] == 0
    assert dossier["gap_diagnosis"]["simulated_rules"] == []

    assert html_response.status_code == 200
    assert DISCLOSURE not in html_response.text
    expected_evidence_paragraph = (
        "<p>"
        f"{dossier['evidence_summary']['public_records']} "
        "public records; 0 synthetic records."
        "</p>"
    )
    assert expected_evidence_paragraph in html_response.text
    assert "Simulated R6–R8 ledger" not in html_response.text


def test_simulated_dossier_retains_disclosure_and_synthetic_rows() -> None:
    json_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier"
        "?mode=simulated"
    )
    html_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=simulated"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert (
        dossier["synthetic_disclosure"]["display_label"]
        == DISCLOSURE
    )
    assert dossier["synthetic_disclosure"]["display_labels"] == {
        "en": DISCLOSURE,
        "ar": ARABIC_DISCLOSURE,
    }
    assert dossier["evidence_summary"]["synthetic_records"] > 0
    rows = dossier["gap_diagnosis"]["simulated_rules"]
    assert [row["rule_id"] for row in rows] == [
        "R6",
        "R7",
        "R8",
    ]
    assert all(row["synthetic_flag"] is True for row in rows)
    assert all(row["evidence_class"] == "D" for row in rows)
    assert all(row["display_label"] == DISCLOSURE for row in rows)
    assert all(
        row["display_labels"] == {
            "en": DISCLOSURE,
            "ar": ARABIC_DISCLOSURE,
        }
        for row in rows
    )

    assert html_response.status_code == 200
    assert DISCLOSURE in html_response.text
    assert ARABIC_DISCLOSURE in html_response.text
    assert "Simulated R6–R8 ledger" in html_response.text
    for rule_id in ("R6", "R7", "R8"):
        assert rule_id in html_response.text


def test_dossier_metadata_uses_a_wcag_aa_design_token() -> None:
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=public"
    )

    assert response.status_code == 200
    token_source = (
        PROJECT_ROOT / "src" / "ior_mvp" / "static" / "css" / "tokens.css"
    ).read_text(encoding="utf-8")
    dossier_source = (
        PROJECT_ROOT / "src" / "ior_mvp" / "static" / "css" / "dossier.css"
    ).read_text(encoding="utf-8")
    foreground_match = re.search(
        r"--color-muted:\s*(#[0-9a-fA-F]{6})",
        token_source,
    )
    background_match = re.search(
        r"--color-surface:\s*(#[0-9a-fA-F]{6})",
        token_source,
    )
    assert foreground_match is not None
    assert background_match is not None
    assert "color: var(--color-muted);" in dossier_source
    assert token_source in response.text
    assert dossier_source in response.text

    def luminance(color: str) -> float:
        channels = [
            int(color[index : index + 2], 16) / 255
            for index in (1, 3, 5)
        ]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return (
            0.2126 * linear[0]
            + 0.7152 * linear[1]
            + 0.0722 * linear[2]
        )

    foreground = luminance(foreground_match.group(1))
    background = luminance(background_match.group(1))
    assert (
        max(foreground, background) + 0.05
    ) / (
        min(foreground, background) + 0.05
    ) >= 4.5


@pytest.mark.parametrize(
    ("locale", "direction"),
    [("en", "ltr"), ("ar", "rtl")],
)
def test_dossier_html_localizes_chrome_and_document_direction(
    locale: str,
    direction: str,
) -> None:
    strings = _ui_strings(locale)
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=simulated&locale={locale}"
    )

    assert response.status_code == 200
    assert f'<html lang="{locale}" dir="{direction}">' in response.text
    assert (
        f'<main class="page" aria-label="{strings["dossier.print_aria"]}">'
        in response.text
    )
    for key in (
        "dossier.product_identity",
        "dossier.demand_conclusion",
        "dossier.simulated_ledger",
        "dossier.decision_conditions",
        "dossier.kill_conditions",
        "dossier.next_actions",
        "dossier.evidence_boundary",
        "dossier.authority",
    ):
        assert strings[key] in response.text
    assert DISCLOSURE in response.text
    assert ARABIC_DISCLOSURE in response.text


def test_arabic_dossier_marks_engine_text_as_source_language_islands() -> None:
    strings = _ui_strings("ar")
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=simulated&locale=ar"
    )

    assert response.status_code == 200
    assert strings["source_language.caption"] in response.text
    assert response.text.count(
        'class="source-language-island" lang="en" dir="ltr"'
    ) >= 12
    assert (
        "SIMULATED ADVANCE — brownfield specification upgrade"
        in response.text
    )


def test_dossier_locale_defaults_to_english_and_rejects_unknown() -> None:
    default = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=public"
    )
    invalid = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=public&locale=fr"
    )

    assert default.status_code == 200
    assert '<html lang="en" dir="ltr">' in default.text
    assert invalid.status_code == 422


def test_dossier_json_remains_locale_neutral() -> None:
    base = client.get(
        "/api/opportunities/SAU-H0-721049/dossier?mode=simulated"
    )
    with_locale = client.get(
        "/api/opportunities/SAU-H0-721049/dossier"
        "?mode=simulated&locale=ar"
    )

    assert base.status_code == with_locale.status_code == 200
    assert base.json() == with_locale.json()


@pytest.mark.parametrize("locale", ["en", "ar"])
def test_public_dossier_contains_neither_policy_label(
    locale: str,
) -> None:
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=public&locale={locale}"
    )

    assert response.status_code == 200
    assert DISCLOSURE not in response.text
    assert ARABIC_DISCLOSURE not in response.text
