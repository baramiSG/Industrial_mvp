from __future__ import annotations

import json
import re
from itertools import product
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    CASES,
    MODES,
    SYNTHETIC_LABEL,
    BrowserSession,
    Case,
    Mode,
)
from browser_tests.pages import (
    goto_portfolio,
    open_dossier_popup,
    select_case,
)


pytestmark = pytest.mark.e2e
CASE_MODES = tuple(
    (mode, case)
    for mode, case in product(MODES, CASES)
)


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_open_dossier_popup_matches_case_and_mode(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)

    popup = open_dossier_popup(page, case, mode)

    parsed = urlsplit(popup.url)
    assert parsed.path == (
        f"/api/opportunities/{case.id}/dossier.html"
    )
    assert parse_qs(parsed.query) == {"mode": [mode]}
    decision_headline = popup.locator("h1").inner_text().strip()
    assert decision_headline
    assert popup.title().strip() == decision_headline
    expect(popup.locator("main.page")).to_be_visible()
    expect(popup.locator(".state")).to_have_text(
        case.active_state(mode)
    )
    expect(popup.locator(".meta")).to_contain_text(case.id)
    expect(popup.locator(".meta")).to_contain_text(
        f"Mode: {mode}"
    )
    rtl = popup.locator('[dir="rtl"]')
    expect(rtl).to_have_count(1)
    expect(rtl).not_to_have_text("")
    if mode == "simulated":
        expect(popup.locator(".warning")).to_contain_text(
            SYNTHETIC_LABEL
        )
    else:
        expect(popup.locator("body")).not_to_contain_text(
            SYNTHETIC_LABEL
        )


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_copy_decision_json_writes_expected_clipboard_payload(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)

    page.locator(f'[data-copy-json="{case.id}"]').click()
    expect(page.locator("#toast")).to_have_text(
        "Decision dossier JSON copied"
    )
    clipboard = page.evaluate(
        "() => navigator.clipboard.readText()"
    )
    payload = json.loads(clipboard)

    assert payload["opportunity_id"] == case.id
    assert payload["mode"] == mode
    assert payload["decision_state"] == case.active_state(mode)
    if mode == "simulated":
        assert (
            payload["synthetic_disclosure"]["display_label"]
            == SYNTHETIC_LABEL
        )
    else:
        assert payload["synthetic_disclosure"] is None
        assert payload["evidence_summary"]["synthetic_records"] == 0


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_dossier_print_media_and_pdf_are_valid(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)
    popup = open_dossier_popup(page, case, mode)

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
    pdf_path = pdf_dir / f"{case.slug}-{mode}.pdf"
    pdf_path.write_bytes(pdf)

    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) >= 10_240
    page_objects = len(re.findall(rb"/Type\s*/Page\b", pdf))
    assert page_objects >= 1
    summary_path = (
        pdf_dir / f"{case.slug}-{mode}-summary.json"
    )
    summary_path.write_text(
        json.dumps(
            {
                "bytes": len(pdf),
                "eof": pdf.rstrip().endswith(b"%%EOF"),
                "header": pdf.startswith(b"%PDF-"),
                "page_objects": page_objects,
                "path": str(pdf_path.relative_to(
                    browser_session.artifact_dir
                )),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
