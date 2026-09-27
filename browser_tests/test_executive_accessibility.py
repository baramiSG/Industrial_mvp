"""Rendered executive accessibility and viewport behavior."""

import pytest
from playwright.sync_api import expect

from browser_tests.executive_pages import STEPS, goto_executive, select_step
from browser_tests.candidate_pages import goto_candidate, select_candidate_request, assert_four_request_slots
from browser_tests.harness import AR, LOCALES, POLYPROPYLENE, STEEL, format_axe_violations, run_axe

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
@pytest.mark.parametrize("width", [390, 1024, 1440, 1920, 2560])
def test_executive_steps_have_no_viewport_overflow(browser_session, locale, width):
    page = browser_session.page
    page.set_viewport_size({"width": width, "height": 1000})
    goto_executive(page, locale=locale)
    for step in STEPS:
        select_step(page, step)
        if step == 'SIMULATED_EVIDENCE':
            _, line = goto_candidate(page, STEEL, locale, role="REFERENCE_LINE")
            assert line is not None
            finding = next(value for value in line["findings"] if value["requirement_item_id"] == "qualified_volume")
            select_candidate_request(page, finding)
            assert_four_request_slots(page, line, finding)
            summary = page.locator('[data-capability-legend] summary')
            page.locator('[data-scenario-context] > summary').click()
            summary.focus(); page.keyboard.press('Enter')
            expect(page.locator('[data-capability-legend]')).to_have_attribute('open', '')
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (locale.code, width, step)
        assert page.locator("[data-executive-step]").count() == 8
        expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")
        if width in {390, 1024, 1440}:
            result = run_axe(page)
            assert result["violations"] == [], format_axe_violations(result["violations"])


@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_executive_native_keyboard_and_technical_isolation(browser_session, locale):
    page = browser_session.page
    goto_executive(page, locale=locale)
    page.keyboard.press("Tab")
    expect(page.locator(".executive-skip")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("[data-executive-main]")).to_be_focused()
    page.locator('[data-executive-step="SIGNAL"]').focus()
    page.keyboard.press("Tab")
    expect(page.locator('[data-executive-step="FALSE_POSITIVE_CONTROLS"]')).to_be_focused()
    assert page.locator("bdi.technical-token").evaluate_all("nodes => nodes.every(n => n.dir === 'ltr')")
    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    _, line = goto_candidate(page, STEEL, locale, role="REFERENCE_LINE")
    assert line is not None
    outer = page.locator('[data-all-findings] > summary')
    outer.focus(); page.keyboard.press("Enter")
    expect(page.locator('[data-all-findings]')).to_have_attribute('open', '')
    finding = page.locator('[data-finding-item="qualified_volume"] > summary')
    finding.focus(); page.keyboard.press("Enter")
    expect(page.locator('[data-finding-item="qualified_volume"]')).to_have_attribute('open', '')
    reason = page.locator('[data-finding-item="qualified_volume"] [data-finding-reason] > summary')
    reason.focus(); page.keyboard.press("Enter")
    expect(page.locator('[data-finding-item="qualified_volume"] [data-finding-reason]')).to_have_attribute('open', '')
    page.locator('[data-finding-item="qualified_volume"] [data-ministry-requirement]').focus()
    page.keyboard.press("Enter")
    expect(page.locator('[data-selected-request="qualified_volume"]')).to_have_count(1)


def test_complete_arabic_executive_subtree_has_no_unmarked_english(browser_session):
    from browser_tests.pages import arabic_parity_report

    page = browser_session.page
    goto_executive(page, locale=AR)
    for step in STEPS:
        select_step(page, step)
        if step == 'SIMULATED_EVIDENCE':
            _, line = goto_candidate(page, STEEL, AR, role="REFERENCE_LINE")
            assert line is not None
            finding = next(value for value in line["findings"] if value["requirement_item_id"] == "qualified_volume")
            select_candidate_request(page, finding)
            page.locator('[data-scenario-context] > summary').click()
            page.locator('[data-capability-legend] summary').click()
        report = arabic_parity_report(page, "[data-executive-main]")
        assert report["island_failures"] == [], (step, report)
        assert report["latin_prose_runs"] == [], (step, report)
        assert report["latin_runs"] == [], (step, report)
        assert report["label_leaks"] == [], (step, report)
        assert report["arabic_present"] is True


@pytest.mark.parametrize(('case', 'line_id'), (
    (STEEL, 'LINE-7315366f6a9166d8'),
    (STEEL, 'LINE-96f1bd96c5c6ccda'),
    (STEEL, 'LINE-4fbdbb0b2c107968'),
    (POLYPROPYLENE, 'LINE-e403e85a85052861'),
    (POLYPROPYLENE, 'LINE-cb9a42384c3523ec'),
), ids=('steel-a', 'steel-b', 'steel-c', 'pp-a', 'pp-b'))
def test_arabic_candidate_line_request_and_comparison_keep_full_parity(browser_session, case, line_id):
    from browser_tests.pages import arabic_parity_report

    page = browser_session.page
    detail, line = goto_candidate(page, case, AR, line_id=line_id)
    assert line is not None and line['entity_id'] == line_id
    assert detail['decisions']['public']['state'] == case.real_state
    expect(page.locator('[data-selected-subject]')).to_have_attribute('data-selected-subject', line_id)
    finding = next((row for row in line['findings'] if row['next_evidence']), None)
    if finding:
        select_candidate_request(page, finding)
        assert_four_request_slots(page, line, finding)
    report = arabic_parity_report(page, '[data-executive-main]')
    assert report['island_failures'] == [], report
    assert report['latin_prose_runs'] == [], report
    assert report['latin_runs'] == [], report
    assert report['label_leaks'] == [], report
    assert report['arabic_present'] is True


def test_arabic_source_passports_keep_full_subtree_parity(browser_session):
    from browser_tests.harness import AR
    from browser_tests.pages import arabic_parity_report

    page = browser_session.page
    goto_executive(page, locale=AR)
    for claim in ("decision.public", "decision.simulated"):
        if claim == "decision.simulated":
            select_step(page, "ROUTE_COMPARISON")
        page.locator(f'[data-claim-id="{claim}"]').first.click()
        report = arabic_parity_report(page, "[data-executive-main]")
        assert report["island_failures"] == [], report
        assert report["latin_prose_runs"] == [], report
        assert report["latin_runs"] == [], report
        assert report["label_leaks"] == [], report
        page.keyboard.press("Escape")
