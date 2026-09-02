from __future__ import annotations

import json
import re
from itertools import product
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    CASES,
    LOCALES,
    MODES,
    BrowserSession,
    Case,
    Locale,
    Mode,
)
from browser_tests.pages import (
    goto_portfolio,
    locale_bundle,
    open_dossier_popup,
    select_case,
)


pytestmark = pytest.mark.e2e
CASE_MODE_LOCALES = tuple(product(MODES, CASES, LOCALES))


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_open_dossier_popup_matches_case_and_mode(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    popup = open_dossier_popup(page, case, mode, locale)

    parsed = urlsplit(popup.url)
    assert parsed.path == f"/api/opportunities/{case.id}/dossier.html"
    assert parse_qs(parsed.query) == {
        "mode": [mode],
        "locale": [locale.code],
    }
    strings = locale_bundle(locale)["strings"]
    assert popup.title().strip().startswith(
        strings["dossier.document_title"].split("{state}")[0]
    )
    expect(popup.locator("main.page")).to_be_visible()
    expect(popup.locator(".state")).to_contain_text(case.active_state(mode))
    expect(popup.locator(".meta")).to_contain_text(case.id)
    state_words = re.findall(
        r"[\w-]+",
        popup.locator(".state").inner_text().casefold(),
    )
    assert all(
        current != following
        for current, following in zip(
            state_words,
            state_words[1:],
            strict=False,
        )
    )
    if locale.code == "ar":
        hs_token = popup.locator(
            "bdi.technical-token",
            has_text=f"HS H0 / {case.hs6}",
        )
        expect(hs_token).to_have_count(1)
        token_detail = hs_token.evaluate(
            """node => ({
              text: node.textContent,
              direction: getComputedStyle(node).direction,
              unicodeBidi: getComputedStyle(node).unicodeBidi,
            })"""
        )
        assert token_detail == {
            "text": f"HS H0 / {case.hs6}",
            "direction": "ltr",
            "unicodeBidi": "isolate",
        }
    labels = locale_bundle(locale)["synthetic_labels"]
    for key in (
        "dossier.contradiction_register",
        "dossier.public_contradictions",
        "dossier.synthetic_contradictions",
    ):
        expect(popup.locator("body")).to_contain_text(strings[key])
    if case.id == "SAU-H0-721049":
        expect(popup.locator("body")).to_contain_text(
            "Published coating range differs from EPD and is retained "
            "for confirmation."
        )
    else:
        expect(popup.locator("body")).to_contain_text(
            strings["dossier.no_public_contradictions"]
        )
    if mode == "simulated":
        for label in labels.values():
            expect(popup.locator(".warning")).to_contain_text(label)
        expect(popup.locator("body")).to_contain_text(
            strings["dossier.no_synthetic_contradictions"]
        )
    else:
        for label in labels.values():
            expect(popup.locator("body")).not_to_contain_text(label)
        expect(popup.locator("body")).to_contain_text(
            strings["dossier.synthetic_not_applicable"]
        )


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_copy_decision_json_writes_expected_clipboard_payload(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    page.locator(f'[data-copy-json="{case.id}"]').click()
    expect(page.locator("#toast")).to_have_text(
        locale_bundle(locale)["strings"]["actions.copied"]
    )
    payload = json.loads(
        page.evaluate("() => navigator.clipboard.readText()")
    )
    assert payload["opportunity_id"] == case.id
    assert payload["mode"] == mode
    assert payload["decision_state"] == case.active_state(mode)
    if mode == "simulated":
        assert payload["synthetic_disclosure"]["display_labels"] == (
            locale_bundle(locale)["synthetic_labels"]
        )
    else:
        assert payload["synthetic_disclosure"] is None
        assert payload["evidence_summary"]["synthetic_records"] == 0


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_dossier_print_media_and_pdf_are_valid(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    popup = open_dossier_popup(page, case, mode, locale)
    popup.emulate_media(media="print")
    styles = popup.evaluate(
        """() => {
          const body = getComputedStyle(document.body);
          const page = document.querySelector("main.page");
          const sheet = getComputedStyle(page);
          return {
            print: matchMedia("print").matches,
            bodyBackground: body.backgroundColor,
            boxShadow: sheet.boxShadow,
            margins: [
              sheet.marginTop,
              sheet.marginRight,
              sheet.marginBottom,
              sheet.marginLeft,
            ],
            maxWidth: sheet.maxWidth,
            overflow: (
              document.documentElement.scrollWidth <=
                document.documentElement.clientWidth &&
              document.body.scrollWidth <= document.body.clientWidth
            ),
          };
        }"""
    )
    assert styles == {
        "print": True,
        "bodyBackground": "rgb(255, 255, 255)",
        "boxShadow": "none",
        "margins": ["0px", "0px", "0px", "0px"],
        "maxWidth": "none",
        "overflow": True,
    }
    pdf = popup.pdf(
        format="A4",
        print_background=True,
        prefer_css_page_size=True,
    )
    pdf_dir = browser_session.artifact_dir / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"{case.slug}-{mode}-{locale.code}.pdf"
    pdf_path.write_bytes(pdf)
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) >= 10_240
    page_objects = len(re.findall(rb"/Type\s*/Page\b", pdf))
    assert page_objects >= 1
    summary_path = (
        pdf_dir / f"{case.slug}-{mode}-{locale.code}-summary.json"
    )
    summary_path.write_text(
        json.dumps(
            {
                "bytes": len(pdf),
                "locale": locale.code,
                "page_objects": page_objects,
                "path": str(
                    pdf_path.relative_to(browser_session.artifact_dir)
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
