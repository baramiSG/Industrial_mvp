from __future__ import annotations

import json
from dataclasses import asdict
from itertools import product

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    AXE_TAGS,
    CASES,
    LOCALES,
    MODES,
    VIEWPORTS,
    BrowserSession,
    Case,
    Locale,
    Mode,
    Viewport,
    format_axe_violations,
    keyboard_focus_report,
    run_axe,
    verify_arabic_rendering,
)
from browser_tests.pages import (
    goto_portfolio,
    open_dossier_popup,
    select_case,
)


pytestmark = pytest.mark.e2e
CASE_MODE_LOCALES = tuple(product(MODES, CASES, LOCALES))
MODE_VIEWPORT_LOCALES = tuple(product(MODES, VIEWPORTS, LOCALES))
MODE_LOCALES = tuple(product(MODES, LOCALES))


@pytest.mark.parametrize(
    ("mode", "viewport", "locale"),
    MODE_VIEWPORT_LOCALES,
    ids=[
        f"{mode}-{viewport.name}-{locale.code}"
        for mode, viewport, locale in MODE_VIEWPORT_LOCALES
    ],
)
def test_keyboard_tab_order_reaches_every_interactive_control_with_visible_focus(
    browser_session: BrowserSession,
    mode: Mode,
    viewport: Viewport,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    expect(page.locator("[data-queue-id]")).to_have_count(
        5,
        timeout=10_000,
    )
    report = keyboard_focus_report(page)
    expected = (
        "nav:overview",
        "nav:workspace",
        "nav:methodology",
        "nav:extraction",
        "nav:governance",
        "nav:screening",
        "mode:public",
        "mode:simulated",
        "id:locale-switch",
        "id:open-first-case",
        "id:view-methodology",
        *(f"open:{case.id}" for case in CASES),
        "id:opportunity-select",
        f"dossier:{CASES[0].id}",
        f"copy:{CASES[0].id}",
        "queue:high_evsi_evidence_investigation",
        "queue:incumbent_upgrade_investigation",
        "queue:likely_false_positive",
        "queue:resilience_case",
        "queue:robust_public_finding",
    )
    assert report.dom_order == expected
    assert report.focused_order == expected
    assert report.wrap_identity == expected[0]
    assert all(item.focus_visible for item in report.records)
    assert all(
        item.before_signature != item.focused_signature
        for item in report.records
    )
    assert "/docs" not in page.locator("body").inner_html()
    assert viewport.width == page.viewport_size["width"]
    output = (
        browser_session.artifact_dir
        / "focus"
        / f"{mode}-{viewport.name}-{locale.code}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "locale": locale.code,
                "mode": mode,
                "records": [asdict(item) for item in report.records],
                "viewport": viewport.as_dict(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _assert_axe_clean(
    result: dict,
    output: object,
) -> None:
    violations = result["violations"]
    if violations:
        output.write_text(
            format_axe_violations(violations),
            encoding="utf-8",
        )
    assert violations == [], format_axe_violations(violations)


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_workspace_has_zero_wcag_21_aa_axe_violations(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    output = (
        browser_session.artifact_dir
        / "axe"
        / f"workspace-{case.slug}-{mode}-{locale.code}.txt"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    _assert_axe_clean(run_axe(page), output)


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_dossier_has_zero_wcag_21_aa_axe_violations(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    popup = open_dossier_popup(page, case, mode, locale)
    output = (
        browser_session.artifact_dir
        / "axe"
        / f"dossier-{case.slug}-{mode}-{locale.code}.txt"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    _assert_axe_clean(run_axe(popup), output)


@pytest.mark.parametrize(
    ("mode", "locale"),
    MODE_LOCALES,
    ids=[f"{mode}-{locale.code}" for mode, locale in MODE_LOCALES],
)
def test_workspace_rtl_elements_render_real_arabic_glyphs(
    browser_session: BrowserSession,
    mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    report = verify_arabic_rendering(page)
    assert report.document_direction == locale.direction
    assert report.intended_font_loaded is True
    assert report.arabic_width != report.replacement_width
    assert report.arabic_pixel_signature != report.replacement_pixel_signature
    assert report.distinct_arabic_glyph_signatures >= 2
    if locale.code == "ar":
        islands = page.locator(".source-language-island")
        assert islands.count() >= 10
        assert all(
            island.evaluate(
                "(node) => getComputedStyle(node).direction"
            ) == "ltr"
            for island in islands.all()
        )
    output = (
        browser_session.artifact_dir
        / "rtl"
        / f"workspace-{mode}-{locale.code}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_dossier_rtl_element_renders_real_arabic_glyphs(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, case, mode, locale)
    popup = open_dossier_popup(page, case, mode, locale)
    report = verify_arabic_rendering(popup)
    assert report.document_direction == locale.direction
    assert report.intended_font_loaded is True
    assert report.arabic_width != report.replacement_width
    assert report.arabic_pixel_signature != report.replacement_pixel_signature
    assert report.distinct_arabic_glyph_signatures >= 2
    if locale.code == "ar":
        minimum_islands = 8 if mode == "simulated" else 4
        assert (
            popup.locator(".source-language-island").count()
            >= minimum_islands
        )
    output = (
        browser_session.artifact_dir
        / "rtl"
        / f"dossier-{case.slug}-{mode}-{locale.code}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
