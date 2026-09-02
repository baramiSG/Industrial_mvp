from __future__ import annotations

import json
from dataclasses import asdict
from itertools import product

import pytest

from browser_tests.harness import (
    AXE_TAGS,
    CASES,
    MODES,
    VIEWPORTS,
    BrowserSession,
    Case,
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
CASE_MODES = tuple(
    (mode, case)
    for mode, case in product(MODES, CASES)
)
MODE_VIEWPORTS = tuple(
    (mode, viewport)
    for mode, viewport in product(MODES, VIEWPORTS)
)


@pytest.mark.parametrize(
    ("mode", "viewport"),
    MODE_VIEWPORTS,
    ids=[
        f"{mode}-{viewport.name}"
        for mode, viewport in MODE_VIEWPORTS
    ],
)
def test_keyboard_tab_order_reaches_every_interactive_control_with_visible_focus(
    browser_session: BrowserSession,
    mode: Mode,
    viewport: Viewport,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    report = keyboard_focus_report(page)

    expected = (
        "nav:overview",
        "nav:workspace",
        "nav:methodology",
        "nav:extraction",
        "nav:governance",
        "mode:public",
        "mode:simulated",
        "href:/docs",
        "id:open-first-case",
        "id:view-methodology",
        f"open:{CASES[0].id}",
        f"open:{CASES[1].id}",
        "id:opportunity-select",
        f"dossier:{CASES[0].id}",
        f"copy:{CASES[0].id}",
    )
    assert report.dom_order == expected
    assert report.focused_order == expected
    assert report.wrap_identity == expected[0]
    assert all(item.focus_visible for item in report.records)
    assert all(
        item.before_signature != item.focused_signature
        for item in report.records
    )
    assert "/docs" not in page.url
    assert viewport.width == page.viewport_size["width"]
    output = (
        browser_session.artifact_dir
        / "focus"
        / f"{mode}-{viewport.name}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "mode": mode,
                "viewport": viewport.as_dict(),
                "expected_count": len(expected),
                "reached_count": len(report.records),
                "focus_visible": all(
                    item.focus_visible for item in report.records
                ),
                "records": [
                    asdict(item) for item in report.records
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_workspace_has_zero_wcag_21_aa_axe_violations(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)

    result = run_axe(page)
    violations = result["violations"]
    summary = (
        browser_session.artifact_dir
        / "axe"
        / f"workspace-{case.slug}-{mode}-summary.json"
    )
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        json.dumps(
            {
                "tags": list(AXE_TAGS),
                "violations": len(violations),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if violations:
        output = (
            browser_session.artifact_dir
            / "axe"
            / f"workspace-{case.slug}-{mode}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            format_axe_violations(violations),
            encoding="utf-8",
        )
    assert violations == [], format_axe_violations(violations)


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_dossier_has_zero_wcag_21_aa_axe_violations(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)
    popup = open_dossier_popup(page, case, mode)

    result = run_axe(popup)
    violations = result["violations"]
    summary = (
        browser_session.artifact_dir
        / "axe"
        / f"dossier-{case.slug}-{mode}-summary.json"
    )
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        json.dumps(
            {
                "tags": list(AXE_TAGS),
                "violations": len(violations),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if violations:
        output = (
            browser_session.artifact_dir
            / "axe"
            / f"dossier-{case.slug}-{mode}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            format_axe_violations(violations),
            encoding="utf-8",
        )
    assert violations == [], format_axe_violations(violations)


@pytest.mark.parametrize("mode", MODES, ids=MODES)
def test_workspace_rtl_elements_render_real_arabic_glyphs(
    browser_session: BrowserSession,
    mode: Mode,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    report = verify_arabic_rendering(page)

    assert report.visible_rtl_nodes >= 1
    assert report.arabic_width != report.replacement_width
    assert report.arabic_pixel_signature != (
        report.replacement_pixel_signature
    )
    assert report.distinct_arabic_glyph_signatures >= 2
    output = (
        browser_session.artifact_dir
        / "rtl"
        / f"workspace-{mode}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_dossier_rtl_element_renders_real_arabic_glyphs(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, case, mode)
    popup = open_dossier_popup(page, case, mode)

    report = verify_arabic_rendering(popup)

    assert report.visible_rtl_nodes == 1
    assert report.arabic_width != report.replacement_width
    assert report.arabic_pixel_signature != (
        report.replacement_pixel_signature
    )
    assert report.distinct_arabic_glyph_signatures >= 2
    output = (
        browser_session.artifact_dir
        / "rtl"
        / f"dossier-{case.slug}-{mode}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
