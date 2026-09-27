"""Existing executive journey helpers for the three admitted candidate scenes."""

from __future__ import annotations

from urllib.parse import urlencode

from playwright.sync_api import expect

from browser_tests.executive_pages import api_json


def candidate_line(detail: dict, role: str | None = None) -> dict:
    assessments = detail["line_assessment"]["rows"]
    eligible = [row for row in assessments if role is None or row["reference_role"] == role]
    assert eligible, (detail["opportunity"]["opportunity_id"], role)
    line_id = sorted(eligible, key=lambda row: row["line_id"])[0]["line_id"]
    rows = detail["candidate_discovery"]["rows"]
    return next(row for row in rows if row["entity_kind"] == "LINE" and row["entity_id"] == line_id)


def goto_candidate(page, case, locale, *, role: str | None = None, discovery: bool = False,
                   line_id: str | None = None) -> tuple[dict, dict | None]:
    detail = api_json(page, f"/api/executive/opportunities/{case.id}")
    assert detail["candidate_discovery"]["available"] is True
    line = None if discovery else (
        next(row for row in detail["candidate_discovery"]["rows"]
             if row["entity_kind"] == "LINE" and row["entity_id"] == line_id)
        if line_id else candidate_line(detail, role)
    )
    query = {
        "opportunity": case.id,
        "locale": locale.code,
        "step": "SIMULATED_EVIDENCE",
    }
    if line is not None:
        query.update(company=line["company_id"], plant=line["plant_id"], line=line["entity_id"])
    page.goto("/executive?" + urlencode(query))
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", case.id)
    expect(page.locator('[data-active-step="SIMULATED_EVIDENCE"]')).to_be_visible()
    expect(page.locator("[data-candidate-discovery]")).to_have_count(1)
    if line is not None:
        expect(page.locator("[data-selected-subject]")).to_have_attribute("data-selected-subject", line["entity_id"])
    return detail, line


def select_candidate_request(page, finding: dict) -> None:
    selector = f'[data-finding-item="{finding["requirement_item_id"]}"]'
    page.locator("[data-selected-subject] [data-all-findings] > summary").click()
    record = page.locator("[data-selected-subject] " + selector)
    expect(record).to_have_count(1)
    record.locator("summary").first.click()
    record.locator("[data-finding-reason] > summary").click()
    record.locator("[data-ministry-requirement]").click()
    expect(page.locator("[data-selected-request]")).to_have_attribute(
        "data-selected-request", finding["requirement_item_id"],
    )
    page.locator("[data-selected-subject] [data-all-findings] > summary").click()
    record = page.locator("[data-selected-subject] " + selector)
    record.locator("summary").first.click()
    record.locator("[data-finding-reason] > summary").click()


def assert_four_request_slots(page, row: dict, finding: dict) -> None:
    """Check each local surface; page-wide copies cannot mask an omitted slot."""
    selector = f'[data-selected-subject="{row["entity_id"]}"] [data-finding-item="{finding["requirement_item_id"]}"]'
    record = page.locator(selector)
    expected = finding["next_evidence"]
    surfaces = [
        record.locator('[data-request-location="detail"]'),
        record.locator('[data-request-location="reason"]'),
        page.locator('[data-selected-request] [data-request-location="rail"]'),
    ]
    for surface in surfaces:
        expect(surface).to_have_count(1)
        expect(surface).to_have_attribute("data-request-item", finding["requirement_item_id"])
        expect(surface).to_have_attribute("data-request-rule", finding["rule_id"])
        for slot in ("field", "source", "effect", "scope"):
            cell = surface.locator(f'[data-request-slot="{slot}"]')
            expect(cell).to_have_count(1, timeout=250)
            expect(cell.locator("dt")).not_to_be_empty()
            expect(cell.locator("dd")).not_to_be_empty()
        if expected:
            expect(surface.locator('[data-request-slot="field"]')).to_contain_text(expected["missing_field"])
            expect(surface.locator('[data-request-slot="source"]')).to_contain_text(expected["dataset_or_action"])
        expect(surface.locator('[data-request-slot="scope"]')).to_contain_text(row["company_id"])
        expect(surface.locator('[data-request-slot="scope"]')).to_contain_text(row["entity_id"])
        expect(surface.locator('[data-request-slot="scope"]')).to_contain_text(finding["requirement_item_id"])
