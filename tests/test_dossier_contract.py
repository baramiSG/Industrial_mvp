from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

import ior_mvp.decision_engine as decision_engine
from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier, render_dossier_html


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
        "R5",
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
    for rule_id in ("R5", "R6", "R7", "R8"):
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


def test_arabic_simulated_dossier_uses_localized_narrative_without_islands() -> None:
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=simulated&locale=ar"
    )
    analysis = analyze("SAU-H0-721049", "simulated")
    block = response.text.split(
        '<section class="decision-narrative">',
        maxsplit=1,
    )[1].split("</section>", maxsplit=1)[0]

    assert response.status_code == 200
    assert (
        analysis["simulation_decision"]["localized_narrative"]["ar"][
            "headline"
        ]["text"]
        in block
    )
    assert 'class="source-language-island"' not in block
    assert DISCLOSURE in response.text
    assert ARABIC_DISCLOSURE in response.text


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


def test_public_dossier_v11_projects_only_public_contradictions() -> None:
    steel = build_dossier(analyze("SAU-H0-721049", "public"))
    polypropylene = build_dossier(
        analyze("SAU-H0-390210", "public")
    )

    assert steel["dossier_version"] == "1.1"
    assert steel["contradiction_register"] == {
        "public": [
            {
                "evidence_id": "S-UNICOIL-SPEC",
                "source": "UNICOIL",
                "contradiction": (
                    "Published coating range differs from EPD and is "
                    "retained for confirmation."
                ),
                "synthetic_flag": False,
            }
        ],
        "synthetic": [],
        "synthetic_status": "NOT_APPLICABLE",
    }
    assert polypropylene["contradiction_register"] == {
        "public": [],
        "synthetic": [],
        "synthetic_status": "NOT_APPLICABLE",
    }


def test_simulated_dossier_separates_public_and_synthetic_contradictions(
) -> None:
    analysis = analyze("SAU-H0-721049", "simulated")
    dossier = build_dossier(analysis)
    assert len(dossier["contradiction_register"]["public"]) == 1
    assert dossier["contradiction_register"]["synthetic"] == []
    assert (
        dossier["contradiction_register"]["synthetic_status"]
        == "NONE_RECORDED"
    )

    planted = deepcopy(analysis)
    synthetic = next(
        row
        for row in planted["evidence"]
        if row["synthetic_flag"] is True
    )
    synthetic["contradiction"] = "Synthetic contradiction probe."
    dossier = build_dossier(planted)
    assert dossier["contradiction_register"]["synthetic"] == [
        {
            "evidence_id": synthetic["evidence_id"],
            "source": "DEMO_GENERATOR",
            "contradiction": "Synthetic contradiction probe.",
            "synthetic_flag": True,
            "scenario_id": synthetic["scenario_id"],
            "display_labels": synthetic["display_labels"],
        }
    ]
    assert (
        dossier["contradiction_register"]["synthetic_status"]
        == "PRESENT"
    )


@pytest.mark.parametrize("locale", ["en", "ar"])
def test_contradiction_register_html_uses_exact_catalogue_copy(
    locale: str,
) -> None:
    strings = _ui_strings(locale)
    steel = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=public&locale={locale}"
    )
    polypropylene = client.get(
        "/api/opportunities/SAU-H0-390210/dossier.html"
        f"?mode=public&locale={locale}"
    )
    simulated = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=simulated&locale={locale}"
    )

    assert steel.status_code == 200
    assert polypropylene.status_code == 200
    assert simulated.status_code == 200
    for response in (steel, polypropylene, simulated):
        assert strings["dossier.contradiction_register"] in response.text
        assert strings["dossier.public_contradictions"] in response.text
        assert strings["dossier.synthetic_contradictions"] in response.text
    assert (
        strings["dossier.synthetic_not_applicable"]
        in steel.text
    )
    assert (
        strings["dossier.no_public_contradictions"]
        in polypropylene.text
    )
    assert (
        strings["dossier.no_synthetic_contradictions"]
        in simulated.text
    )
    assert (
        "Published coating range differs from EPD and is retained "
        "for confirmation."
    ) in steel.text
    if locale == "ar":
        assert (
            'class="source-language-island" lang="en" dir="ltr">'
            "Published coating range differs"
        ) in steel.text


def test_contradiction_html_escapes_untrusted_passport_text() -> None:
    analysis = deepcopy(analyze("SAU-H0-721049", "public"))
    analysis["evidence"][0]["contradiction"] = (
        '<script data-probe="x">alert(1)</script>'
    )

    rendered = render_dossier_html(build_dossier(analysis), locale="en")

    assert "<script data-probe" not in rendered
    assert "&lt;script data-probe=&quot;x&quot;&gt;" in rendered


def test_public_dossier_projects_generalized_decision_diagnostics() -> None:
    analysis = analyze("SAU-H0-721049", "public")
    dossier = build_dossier(analysis)

    assert dossier["decision_rationale"] == (
        analysis["real_decision"]["rationale"]
    )
    assert dossier["localized_narrative"] == (
        analysis["real_decision"]["localized_narrative"]
    )
    assert dossier["narrative_version"] == "1.0.0"
    assert dossier["screening_disposition"] == "CANDIDATE"
    assert dossier["gap_class"] == analysis["gap_class"]
    assert dossier["route_hypotheses"] == analysis["route_hypotheses"]
    assert dossier["preferred_hypothesis"] == (
        analysis["preferred_hypothesis"]
    )
    assert dossier["evidence_class_assessment"] == (
        analysis["evidence_class_assessment"]
    )
    assert dossier["hard_exclusions"] == analysis["hard_exclusions"]


def test_dossier_renders_no_candidate_disposition_label_instead_of_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "public_decision"
            / "no-candidate-no-fired-signal.json"
        ).read_text(encoding="utf-8")
    )
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    analysis = decision_engine.analyze(case["opportunity"]["id"], "public")
    dossier = build_dossier(analysis)

    assert dossier["decision_state"] is None
    assert dossier["screening_disposition"] == "NO_CANDIDATE"
    for locale in ("en", "ar"):
        rendered = render_dossier_html(dossier, locale=locale)
        state_block = rendered.split(
            '<div class="state">',
            maxsplit=1,
        )[1].split("</div>", maxsplit=1)[0]
        assert _ui_strings(locale)["disposition.no_candidate"] in rendered
        assert "NO_CANDIDATE" in state_block
        assert not re.search(r"(?:None|null)", state_block)


@pytest.mark.parametrize(
    ("locale", "headline", "rationale"),
    [
        (
            "en",
            "INVESTIGATE — binding constraint unresolved",
            (
                "Test brownfield first; greenfield is not justified "
                "from public evidence."
            ),
        ),
        (
            "ar",
            "تحقّق — القيد الملزم غير محسوم",
            (
                "اختبر المسار القائم أولاً؛ فلا تبرر الأدلة العامة "
                "إنشاء مشروع جديد مستقل."
            ),
        ),
    ],
)
def test_public_dossier_renders_active_locale_without_source_islands(
    locale: str,
    headline: str,
    rationale: str,
) -> None:
    rendered = render_dossier_html(
        build_dossier(analyze("SAU-H0-721049", "public")),
        locale=locale,
    )

    assert headline in rendered
    assert rationale in rendered
    decision_block = rendered.split(
        '<section class="decision-narrative">',
        maxsplit=1,
    )[1].split("</section>", maxsplit=1)[0]
    assert "source-language-island" not in decision_block
    if locale == "ar":
        assert (
            "INVESTIGATE — binding constraint unresolved"
            not in decision_block
        )


def test_simulated_dossier_localized_narrative_and_counterfactual() -> None:
    analysis = analyze("SAU-H0-721049", "simulated")
    dossier = build_dossier(analysis)

    assert dossier["localized_narrative"] == (
        analysis["simulation_decision"]["localized_narrative"]
    )
    assert dossier["next_evidence_actions"] == (
        analysis["simulation_decision"]["missing_facts"]
    )
    assert dossier["counterfactual"] == (
        analysis["simulation_decision"]["counterfactual"]
    )


def test_public_dossier_counterfactual_is_null() -> None:
    dossier = build_dossier(analyze("SAU-H0-721049", "public"))
    assert dossier["counterfactual"] is None


def test_simulated_dossier_renders_arabic_narrative_without_islands() -> None:
    analysis = analyze("SAU-H0-721049", "simulated")
    rendered = render_dossier_html(
        build_dossier(analysis),
        locale="ar",
    )
    block = rendered.split(
        '<section class="decision-narrative">',
        maxsplit=1,
    )[1].split("</section>", maxsplit=1)[0]

    assert (
        analysis["simulation_decision"]["localized_narrative"]["ar"][
            "headline"
        ]["text"]
        in block
    )
    assert 'class="source-language-island"' not in block


def test_public_dossier_escapes_every_structured_narrative_segment() -> None:
    dossier = build_dossier(analyze("SAU-H0-721049", "public"))
    malicious = '<script data-probe="narrative">x</script>'
    entry = dossier["localized_narrative"]["en"]["headline"]
    entry["text"] = malicious
    entry["segments"] = [
        {
            "kind": "computed",
            "text": malicious,
            "ltr_isolate": False,
        }
    ]

    rendered = render_dossier_html(dossier, locale="en")

    assert malicious not in rendered
    assert (
        "&lt;script data-probe=&quot;narrative&quot;&gt;"
        in rendered
    )
