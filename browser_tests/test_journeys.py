from __future__ import annotations

import re
from itertools import product
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    AR,
    EN,
    CASES,
    LOCALES,
    MODES,
    POLYPROPYLENE,
    STEEL,
    BrowserSession,
    Case,
    Locale,
    Mode,
)
from browser_tests.pages import (
    goto_portfolio,
    locale_bundle,
    open_case_card,
    select_case,
    select_mode,
    wait_for_document,
    wait_for_portfolio,
    wait_for_workspace,
)


pytestmark = pytest.mark.e2e
MODE_LOCALES = tuple(product(MODES, LOCALES))
CASE_MODE_LOCALES = tuple(product(MODES, CASES, LOCALES))


@pytest.mark.parametrize(
    ("mode", "locale"),
    MODE_LOCALES,
    ids=[f"{mode}-{locale.code}" for mode, locale in MODE_LOCALES],
)
def test_portfolio_loads_expected_cases_and_states(
    browser_session: BrowserSession,
    mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)

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
        expect(card).to_contain_text(case.hs6)
        expect(card).to_contain_text(case.real_state)
        expect(card).to_contain_text(case.active_state(mode))
    visible_text = page.locator("body").inner_text()
    assert re.search(r"\b[12][,\u066c]\d{3}\b", visible_text) is None
    for chip in page.locator(".state-chip, .exec-chip, .rule-fire").all():
        words = re.findall(r"[\w-]+", chip.inner_text().casefold())
        assert all(
            current != following
            for current, following in zip(words, words[1:], strict=False)
        ), chip.inner_text()
    strings = locale_bundle(locale)["strings"]
    expect(page.locator("#kpi-grid")).to_contain_text(
        strings["kpi.leakage_label"]
    )
    expect(page.locator("#kpi-grid")).to_contain_text("0")
    portfolio = page.locator("section.compact-section")
    labels = locale_bundle(locale)["synthetic_labels"]
    for label in labels.values():
        if mode == "simulated":
            expect(portfolio).to_contain_text(label)
        else:
            expect(portfolio).not_to_contain_text(label)
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_opportunity_card_opens_selected_workspace(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    open_case_card(page, case, mode, locale)
    wait_for_workspace(page, case, mode, locale)


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_opportunity_select_loads_each_case(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    detail, manifest = select_case(page, case, mode, locale)

    assert (
        f"{urlsplit(detail.url).path}?{urlsplit(detail.url).query}"
        == f"/api/opportunities/{case.id}?mode={mode}"
    )
    assert (
        f"{urlsplit(manifest.url).path}?{urlsplit(manifest.url).query}"
        == f"/api/opportunities/{case.id}/ui-manifest?mode={mode}"
    )
    assert detail.status == manifest.status == 200


@pytest.mark.parametrize(
    ("mode", "locale"),
    MODE_LOCALES,
    ids=[f"{mode}-{locale.code}" for mode, locale in MODE_LOCALES],
)
def test_hero_opens_steel_case_preserving_mode(
    browser_session: BrowserSession,
    mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, POLYPROPYLENE, mode, locale)
    page.locator("#open-first-case").click()
    wait_for_workspace(page, STEEL, mode, locale)


@pytest.mark.parametrize(
    ("start_mode", "end_mode", "locale"),
    tuple(
        (start, end, locale)
        for start, end in (
            ("public", "simulated"),
            ("simulated", "public"),
        )
        for locale in LOCALES
    ),
    ids=[
        f"{start}-to-{end}-{locale.code}"
        for start, end in (
            ("public", "simulated"),
            ("simulated", "public"),
        )
        for locale in LOCALES
    ],
)
def test_mode_switch_preserves_selected_case(
    browser_session: BrowserSession,
    start_mode: Mode,
    end_mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, start_mode, locale)
    select_case(page, POLYPROPYLENE, start_mode, locale)
    select_mode(page, end_mode, locale)
    wait_for_workspace(page, POLYPROPYLENE, end_mode, locale)


@pytest.mark.parametrize(
    "locale",
    LOCALES,
    ids=[locale.code for locale in LOCALES],
)
def test_navigation_and_methodology_action_reach_sections(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
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
    page.locator('.nav-item[data-target="overview"]').click()
    page.locator("#view-methodology").click()
    expect(page.locator("#methodology")).to_be_in_viewport()


@pytest.mark.parametrize(
    ("locale", "target"),
    ((EN, AR), (AR, EN)),
    ids=("en-to-ar", "ar-to-en"),
)
def test_locale_switch_updates_document_url_storage_and_preserves_state(
    browser_session: BrowserSession,
    locale: Locale,
    target: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "simulated", locale)
    select_case(page, POLYPROPYLENE, "simulated", locale)

    page.locator("#locale-switch").click()
    wait_for_workspace(page, POLYPROPYLENE, "simulated", target)
    assert parse_qs(urlsplit(page.url).query)["locale"] == [target.code]
    storage = page.evaluate(
        "() => Object.fromEntries(Object.entries(localStorage))"
    )
    assert storage == {"ior.locale": target.code}
    strings = locale_bundle(target)["strings"]
    expect(page.locator('[data-target="overview"]')).to_contain_text(
        strings["nav.overview"]
    )

    page.reload(wait_until="domcontentloaded")
    wait_for_portfolio(page, "public", target)
    select_mode(page, "simulated", target)
    select_case(page, POLYPROPYLENE, "simulated", target)
    page.evaluate(
        """(code) => {
          const url = new URL(location.href);
          url.searchParams.set("locale", code);
          history.pushState({}, "", url);
          dispatchEvent(new PopStateEvent("popstate"));
        }""",
        locale.code,
    )
    wait_for_document(page, locale)
    wait_for_workspace(page, POLYPROPYLENE, "simulated", locale)
