from __future__ import annotations

import re
from urllib.parse import urlsplit

from playwright.sync_api import Page, Response, expect

from browser_tests.harness import (
    ASSERTION_TIMEOUT_MS,
    CASES,
    SYNTHETIC_LABEL,
    Case,
    Mode,
)


def _response_matches(response: Response, expected: str) -> bool:
    parsed = urlsplit(response.url)
    actual = f"{parsed.path}?{parsed.query}"
    return actual == expected


def wait_for_workspace(
    page: Page,
    case: Case,
    mode: Mode,
) -> None:
    expect(page.locator("#workspace-title")).to_contain_text(
        f"HS {case.hs6}",
        timeout=ASSERTION_TIMEOUT_MS,
    )
    expect(page.get_by_label("Opportunity")).to_have_value(case.id)
    banner = page.locator(".integrity-banner")
    expect(banner).to_be_visible()
    state_chips = banner.locator(".state-chip")
    expect(state_chips).to_have_count(2 if mode == "simulated" else 1)
    expect(state_chips.nth(0)).to_have_text(case.real_state)
    expect(state_chips.nth(-1)).to_have_text(case.active_state(mode))
    expect(
        page.locator(f'[data-dossier-html="{case.id}"]')
    ).to_be_visible()
    expect(
        page.locator(f'[data-copy-json="{case.id}"]')
    ).to_be_visible()
    if mode == "simulated":
        expect(banner).to_contain_text(SYNTHETIC_LABEL)
    else:
        expect(banner).not_to_contain_text(SYNTHETIC_LABEL)


def wait_for_portfolio(page: Page, mode: Mode) -> None:
    expect(page.locator("[data-open-id]")).to_have_count(
        len(CASES),
        timeout=ASSERTION_TIMEOUT_MS,
    )
    expect(page.locator("#opportunity-select option")).to_have_count(
        len(CASES)
    )
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))
    selected = page.get_by_label("Opportunity").input_value()
    case = next(case for case in CASES if case.id == selected)
    wait_for_workspace(page, case, mode)


def select_mode(page: Page, mode: Mode) -> None:
    button = page.locator(f'.mode-button[data-mode="{mode}"]')
    if "active" in (button.get_attribute("class") or "").split():
        wait_for_portfolio(page, mode)
        return
    selected = page.get_by_label("Opportunity").input_value()
    case = next(case for case in CASES if case.id == selected)
    expected_list = f"/api/opportunities?mode={mode}"
    with page.expect_response(
        lambda response: _response_matches(
            response,
            expected_list,
        )
    ):
        button.click()
    wait_for_portfolio(page, mode)
    wait_for_workspace(page, case, mode)


def goto_portfolio(page: Page, mode: Mode) -> None:
    page.goto("/", wait_until="domcontentloaded")
    wait_for_portfolio(page, "public")
    if mode != "public":
        select_mode(page, mode)


def _select_case_once(
    page: Page,
    case: Case,
    mode: Mode,
) -> tuple[Response, Response]:
    detail_path = f"/api/opportunities/{case.id}?mode={mode}"
    manifest_path = (
        f"/api/opportunities/{case.id}/ui-manifest?mode={mode}"
    )
    with page.expect_response(
        lambda response: _response_matches(
            response,
            detail_path,
        )
    ) as detail_info:
        with page.expect_response(
            lambda response: _response_matches(
                response,
                manifest_path,
            )
        ) as manifest_info:
            page.get_by_label("Opportunity").select_option(case.id)
    wait_for_workspace(page, case, mode)
    return detail_info.value, manifest_info.value


def select_case(
    page: Page,
    case: Case,
    mode: Mode,
) -> tuple[Response, Response]:
    if page.get_by_label("Opportunity").input_value() == case.id:
        other = next(item for item in CASES if item.id != case.id)
        _select_case_once(page, other, mode)
    return _select_case_once(page, case, mode)


def open_case_card(
    page: Page,
    case: Case,
    mode: Mode,
) -> None:
    page.locator(f'[data-open-id="{case.id}"]').click()
    wait_for_workspace(page, case, mode)


def open_dossier_popup(
    page: Page,
    case: Case,
    mode: Mode,
) -> Page:
    with page.expect_popup() as popup_info:
        page.locator(
            f'[data-dossier-html="{case.id}"]'
        ).click()
    popup = popup_info.value
    expect(popup.locator("main.page")).to_be_visible(
        timeout=ASSERTION_TIMEOUT_MS
    )
    expect(popup.locator(".meta")).to_contain_text(case.id)
    expect(popup.locator(".meta")).to_contain_text(f"Mode: {mode}")
    return popup
