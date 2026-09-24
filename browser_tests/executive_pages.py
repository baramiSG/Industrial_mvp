"""Native executive journey controls and assertions; no alternate product logic."""

from urllib.parse import urlencode

from playwright.sync_api import expect

from browser_tests.harness import STEEL, EN


STEPS = (
    "SIGNAL", "FALSE_POSITIVE_CONTROLS", "PUBLIC_CONCLUSION",
    "MISSING_MINISTRY_FACTS", "SIMULATED_EVIDENCE", "ROUTE_COMPARISON",
    "INTERVENTION", "CONDITIONS_AND_KILL",
)


def goto_executive(page, case=STEEL, locale=EN, step="SIGNAL"):
    query = urlencode({"opportunity": case.id, "locale": locale.code, "step": step})
    page.goto(f"/executive?{query}")
    expect(page.locator("[data-executive-ready]")).to_have_attribute(
        "data-executive-ready", case.id, timeout=15000,
    )
    expect(page.locator("html")).to_have_attribute("lang", locale.code)
    expect(page.locator("html")).to_have_attribute("dir", locale.direction)


def select_step(page, step):
    page.locator(f'[data-executive-step="{step}"]').click()
    expect(page.locator("[data-active-step]")).to_have_attribute("data-active-step", step)


def api_json(page, path):
    response = page.request.get(path)
    assert response.ok
    return response.json()
