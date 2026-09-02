from __future__ import annotations

import re
from itertools import product
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    CASES,
    MODES,
    POLYPROPYLENE,
    STEEL,
    SYNTHETIC_LABEL,
    BrowserSession,
    Case,
    Mode,
)
from browser_tests.pages import (
    goto_portfolio,
    open_case_card,
    select_case,
    select_mode,
    wait_for_workspace,
)


pytestmark = pytest.mark.e2e
CASE_MODES = tuple(
    (mode, case)
    for mode, case in product(MODES, CASES)
)


@pytest.mark.parametrize("mode", MODES, ids=MODES)
def test_portfolio_loads_expected_cases_and_states(
    browser_session: BrowserSession,
    mode: Mode,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    expect(page.locator("#kpi-grid .kpi-card")).to_have_count(4)
    expect(page.locator("[data-open-id]")).to_have_count(2)
    expect(page.locator("#opportunity-select option")).to_have_count(2)
    assert {
        button.get_attribute("data-open-id")
        for button in page.locator("[data-open-id]").all()
    } == {case.id for case in CASES}
    for case in CASES:
        card = page.locator(
            f'[data-open-id="{case.id}"]'
        ).locator("xpath=ancestor::article[1]")
        expect(card).to_contain_text(case.id.split("-")[-1])
        expect(card).to_contain_text(case.real_state)
        expect(card).to_contain_text(case.active_state(mode))
    expect(page.locator("#kpi-grid")).to_contain_text(
        "Synthetic leakage"
    )
    expect(page.locator("#kpi-grid")).to_contain_text("0")
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))
    if mode == "simulated":
        expect(page.locator(".integrity-banner")).to_contain_text(
            SYNTHETIC_LABEL
        )
    else:
        expect(page.locator("body")).not_to_contain_text(
            SYNTHETIC_LABEL
        )


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_opportunity_card_opens_selected_workspace(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    open_case_card(page, case, mode)

    wait_for_workspace(page, case, mode)


@pytest.mark.parametrize(
    ("mode", "case"),
    CASE_MODES,
    ids=[f"{mode}-{case.slug}" for mode, case in CASE_MODES],
)
def test_opportunity_select_loads_each_case(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    detail, manifest = select_case(page, case, mode)

    expected_detail = (
        f"/api/opportunities/{case.id}?mode={mode}"
    )
    expected_manifest = (
        f"/api/opportunities/{case.id}/ui-manifest?mode={mode}"
    )
    assert (
        f"{urlsplit(detail.url).path}?{urlsplit(detail.url).query}"
        == expected_detail
    )
    assert (
        f"{urlsplit(manifest.url).path}?{urlsplit(manifest.url).query}"
        == expected_manifest
    )
    assert detail.status == manifest.status == 200
    wait_for_workspace(page, case, mode)


@pytest.mark.parametrize("mode", MODES, ids=MODES)
def test_hero_opens_steel_case_preserving_mode(
    browser_session: BrowserSession,
    mode: Mode,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)
    select_case(page, POLYPROPYLENE, mode)

    page.locator("#open-first-case").click()

    wait_for_workspace(page, STEEL, mode)
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))


@pytest.mark.parametrize(
    ("start_mode", "end_mode"),
    (("public", "simulated"), ("simulated", "public")),
    ids=("public-to-simulated", "simulated-to-public"),
)
def test_mode_switch_preserves_selected_case(
    browser_session: BrowserSession,
    start_mode: Mode,
    end_mode: Mode,
) -> None:
    page = browser_session.page
    goto_portfolio(page, start_mode)
    select_case(page, POLYPROPYLENE, start_mode)

    select_mode(page, end_mode)

    wait_for_workspace(page, POLYPROPYLENE, end_mode)


def test_navigation_and_methodology_action_reach_sections(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public")

    for section_id in (
        "overview",
        "workspace",
        "methodology",
        "extraction",
        "governance",
    ):
        button = page.locator(
            f'.nav-item[data-target="{section_id}"]'
        )
        button.click()
        expect(button).to_have_class(re.compile(r"\bactive\b"))
        expect(page.locator(f"#{section_id}")).to_be_in_viewport()

    page.locator(
        '.nav-item[data-target="overview"]'
    ).click()
    page.locator("#view-methodology").click()
    expect(page.locator("#methodology")).to_be_in_viewport()
