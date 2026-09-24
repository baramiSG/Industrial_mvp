"""Response order and history must never overwrite newer evidence context."""

import pytest
from playwright.sync_api import expect

from browser_tests.executive_pages import goto_executive, select_step
from browser_tests.harness import POLYPROPYLENE, STEEL

pytestmark = pytest.mark.e2e


def test_delayed_case_response_cannot_restore_old_case(browser_session):
    page = browser_session.page
    goto_executive(page)
    page.evaluate("""() => {
      const original = window.fetch;
      window.fetch = async (...args) => {
        if (String(args[0]).includes('390210')) {
          await new Promise(resolve => { (window.releaseOld ??= []).push(resolve); });
        }
        return original(...args);
      };
    }""")
    page.locator("#executive-case").select_option(POLYPROPYLENE.id)
    page.locator("#executive-case").select_option(STEEL.id)
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", STEEL.id)
    page.evaluate("() => window.releaseOld.forEach(resolve => resolve())")
    page.wait_for_timeout(300)
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", STEEL.id)
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")


def test_history_restores_case_step_and_locale(browser_session):
    page = browser_session.page
    goto_executive(page)
    select_step(page, "ROUTE_COMPARISON")
    page.locator("#executive-case").select_option(POLYPROPYLENE.id)
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", POLYPROPYLENE.id)
    page.locator("[data-executive-locale]").click()
    expect(page.locator("html")).to_have_attribute("lang", "ar")
    page.go_back()
    expect(page.locator("html")).to_have_attribute("lang", "en")
    page.go_back()
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", STEEL.id)
    expect(page.locator("[data-active-step]")).to_have_attribute("data-active-step", "ROUTE_COMPARISON")
    page.go_forward()
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", POLYPROPYLENE.id)


def test_delayed_locale_response_cannot_restore_previous_case(browser_session):
    page = browser_session.page
    goto_executive(page)
    page.evaluate("""() => {
      const original = window.fetch;
      window.localeReleases = []; window.localeFinished = 0;
      window.fetch = async (...args) => {
        if (!String(args[0]).endsWith('/api/ui-strings/ar')) return original(...args);
        await new Promise(resolve => window.localeReleases.push(resolve));
        const response = await original(...args); window.localeFinished++; return response;
      };
    }""")
    page.locator("[data-executive-locale]").click()
    page.locator("#executive-case").select_option(POLYPROPYLENE.id)
    page.wait_for_function("window.localeReleases.length === 2")
    page.evaluate("window.localeReleases[1]()")
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", POLYPROPYLENE.id)
    expect(page.locator("html")).to_have_attribute("lang", "ar")
    page.evaluate("window.localeReleases[0]()")
    page.wait_for_function("window.localeFinished === 2")
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", POLYPROPYLENE.id)
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "REJECT")
    page.locator('[data-active-step] [data-claim-id="metric.trade"]').click()
    assert page.locator('[data-claim-evidence] [data-passport-id]').evaluate_all("rows => rows.map(r => r.dataset.passportId)") == ["P-WITS-390210"]


def test_late_analyst_claim_response_cannot_restore_previous_sources(browser_session):
    from browser_tests.harness import EN
    from browser_tests.pages import goto_portfolio

    page = browser_session.page
    goto_portfolio(page, "public", EN)
    page.evaluate("""() => {
      const original = window.fetch;
      window.oldClaimFinished = false;
      window.fetch = async (...args) => {
        if (!String(args[0]).endsWith('/api/executive/opportunities/SAU-H0-390210')) return original(...args);
        await new Promise(resolve => window.releaseOldClaim = resolve);
        const response = await original(...args); window.oldClaimFinished = true; return response;
      };
    }""")
    page.locator("#opportunity-select").select_option(POLYPROPYLENE.id)
    page.wait_for_function("typeof window.releaseOldClaim === 'function'")
    expect(page.locator("[data-claim-id]")).to_have_count(0)
    page.locator("#opportunity-select").select_option(STEEL.id)
    # Analyst context actions retain their existing serialization: the selected
    # steel load starts after the pending polypropylene request settles.
    expect(page.locator("[data-claim-id]")).to_have_count(0)
    page.evaluate("window.releaseOldClaim()")
    page.wait_for_function("window.oldClaimFinished")
    expect(page.locator('[data-executive-link]')).to_have_attribute("href", f"/executive?opportunity={STEEL.id}&locale=en")
    expect(page.locator('[data-claim-id="metric.trade"]')).to_have_count(1)
    page.locator('[data-claim-id="metric.trade"]').click()
    ids = page.locator('[data-claim-evidence] [data-passport-id]').evaluate_all("rows => rows.map(r => r.dataset.passportId)")
    assert ids == ["S-WITS-721049"]
