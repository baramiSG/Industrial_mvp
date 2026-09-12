from __future__ import annotations

import json
import re
from copy import deepcopy
from itertools import product
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import Page, Route, expect

from browser_tests.harness import (
    AR,
    LOCALES,
    BrowserSession,
    Locale,
    format_axe_violations,
    keyboard_focus_report,
    run_axe,
    verify_arabic_rendering,
)
from browser_tests.pages import (
    arabic_parity_report,
    assert_arabic_parity,
    first_queue_entry_hs6,
    goto_portfolio,
    locale_bundle,
    open_queue,
    open_record,
    open_screening,
    screening_back,
)
from ior_mvp.config import PROJECT_ROOT


pytestmark = pytest.mark.e2e
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "screening"
PARITY_FIXTURE = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "parity"
    / "parity-negative-cases.json"
)
PARITY_CASE_IDS = (
    "prose-island",
    "hyphenated-english-island",
    "empty-island",
    "bare-prose",
    "two-word-bare",
    "label-as-code-island",
)


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _frozen_summary() -> dict:
    return json.loads(
        (
            PROJECT_ROOT
            / "data"
            / "screening"
            / "snapshots"
            / "SCREENING-SAU-2026-09-12-9b6b22032fd8"
            / "summary.json"
        ).read_text(encoding="utf-8")
    )


def _api_json(page: Page, path: str) -> dict:
    return page.evaluate(
        """async (path) => {
          const response = await fetch(path);
          if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
          return await response.json();
        }""",
        path,
    )


def _shot(session: BrowserSession, name: str, locale: Locale) -> None:
    output = session.artifact_dir / "screening" / f"{name}-{locale.code}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    session.page.screenshot(path=output, full_page=False)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_summary_renders_status_coverage_counts_and_five_queues(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    strings = locale_bundle(locale)["strings"]
    payload = _api_json(page, "/api/screening")

    summary = page.locator("#screening-view")
    expect(summary.locator(".universe-card")).to_contain_text(
        strings["screening.status.available"]
    )
    expect(summary.locator(".universe-card")).to_contain_text("5443")
    coverage = summary.locator(".coverage-accounting")
    expect(coverage).to_contain_text(
        strings["screening.status.not_calculable"]
    )
    expect(coverage).to_contain_text(
        strings["reason.partner_detail_not_acquired"]
    )
    expect(coverage).to_contain_text(
        strings["reason.entity_artifact_available"]
    )
    expect(summary).to_contain_text("4996")
    expect(summary).to_contain_text("447")
    expect(summary).to_contain_text("135")
    expect(summary).to_contain_text(
        strings["reason.d_star_not_assigned_at_screening"]
    )
    buttons = summary.locator("[data-queue-id]")
    expect(buttons).to_have_count(5)
    assert [button.get_attribute("data-queue-id") for button in buttons.all()] == [
        row["queue_id"] for row in payload["queues"]
    ]
    for row in payload["queues"]:
        card = summary.locator(
            f'[data-queue-id="{row["queue_id"]}"]'
        ).locator("xpath=ancestor::article[1]")
        expect(card).to_contain_text(str(row["count"]))
    expect(page.locator("#screening")).to_contain_text(
        strings["screening.boundary_public_only"]
    )
    expect(page.locator("#screening-evidence [id^='passport-']")).to_have_count(8)
    expect(page.locator("#screening")).to_contain_text(
        strings["screening.evidence.passport_detail_not_exposed"]
    )
    _shot(browser_session, "summary", locale)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_journey_queue_record_passport_anchor_back(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    requests: list[str] = []
    page.on(
        "request",
        lambda request: (
            requests.append(request.url)
            if "/api/screening" in request.url
            else None
        ),
    )
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    strings = locale_bundle(locale)["strings"]
    evidence = _api_json(page, "/api/screening/evidence")
    cards = page.locator("#screening-evidence [id^='passport-']")
    expect(cards).to_have_count(8)
    expect(page.locator("[id^='passport-']")).to_have_count(8)
    assert [card.get_attribute("id") for card in cards.all()] == [
        f"passport-{row['passport_id']}"
        for row in evidence["evidence_passports"]
    ]
    passport = evidence["evidence_passports"][0]
    unit = next(
        row
        for row in evidence["universe_units"]
        if row["unit_key"] == passport["unit_key"]
    )
    first_card = cards.first
    for value in (
        passport["source_id"],
        passport["stage"],
        passport["evidence_class"],
        passport["status"],
        passport["retrieval"]["retrieved_at"],
        unit["completeness_basis"],
        unit["query_hash"],
        unit["selected_run_id"],
        *unit["superseded_run_ids"],
    ):
        expect(first_card).to_contain_text(str(value))
    expect(first_card).to_contain_text(
        strings["screening.status.complete"]
    )
    endpoint = passport["retrieval"]["endpoint_or_document"]
    endpoint_node = first_card.get_by_text(endpoint, exact=True)
    expect(endpoint_node).to_be_visible()
    assert endpoint_node.evaluate("(node) => node.tagName") != "A"
    assert page.locator(".unit-card.explicit-state").count() == 0
    expect(page.locator("#screening .explicit-state")).to_have_count(1)

    queue_response = open_queue(
        page,
        "robust_public_finding",
        locale,
    )
    queue_payload = queue_response.json()
    expect(page.locator("#screening-view tbody tr")).to_have_count(50)
    first_entry = queue_payload["entries"][0]
    first_row = page.locator("#screening-view tbody tr").first
    expect(first_row).to_contain_text(first_entry["hs6"])
    expect(first_row).to_contain_text(str(first_entry["pareto_rank"]))
    _shot(browser_session, "queue-robust", locale)

    record_response = open_record(page, first_entry["hs6"], locale)
    record = record_response.json()
    view = page.locator("#screening-view")
    expect(view).to_contain_text(first_entry["hs6"])
    expect(view).to_contain_text(strings["disposition.candidate"])
    expect(view).to_contain_text(strings["reason.material_trigger_fired"])
    expect(view).to_contain_text(strings["state.investigate"])
    expect(view).to_contain_text(
        strings["reason.route_changing_evidence_unresolved"]
    )
    expect(view.locator(".rule-table tbody tr")).to_have_count(10)
    for row in record["ledger"]:
        expect(view).to_contain_text(
            strings[f"screening.result.{row['result_code'].lower()}"]
        )
    expected_common = _frozen_summary()["common_record_fields"]
    assert record["rules_not_evaluated_at_screening"] == (
        expected_common["rules_not_evaluated_at_screening"]
    )
    assert [
        item.inner_text()
        for item in view.locator("[data-not-evaluated-rules] li").all()
    ] == expected_common["rules_not_evaluated_at_screening"]
    expect(view).to_contain_text(
        strings[
            "screening.not_evaluated_reason.inputs_not_public_at_screening_grain"
        ]
    )
    expect(view).to_contain_text(
        strings["reason.tariff_tree_not_acquired"]
    )
    expect(view).to_contain_text(
        strings["reason.production_aggregates_not_acquired"]
    )
    assert record["evidence_passports"] == []
    expect(view.locator("[data-record-passports='none']")).to_have_count(1)
    expect(view.locator("[data-record-passports='none']")).to_have_text(
        strings["screening.record.no_record_passports"]
    )
    assert view.locator("[id^='passport-']").count() == 0
    expect(page.locator("[id^='passport-']")).to_have_count(8)
    anchors = view.locator(
        "[data-passport-ref][data-passport-scope='universe']"
    )
    expect(anchors).to_have_count(8)
    assert [anchor.get_attribute("href") for anchor in anchors.all()] == [
        f"#passport-{row['passport_id']}"
        for row in evidence["evidence_passports"]
    ]
    before_click = len(requests)
    anchors.first.click()
    expected_id = f"passport-{passport['passport_id']}"
    assert page.evaluate("() => document.activeElement.id") == expected_id
    expect(page.locator(f"#{expected_id}")).to_be_in_viewport()
    assert urlsplit(page.url).fragment == ""
    assert len(requests) == before_click
    _shot(browser_session, "record", locale)

    screening_back(page, "queue", locale)
    expect(page.locator("#screening-view tbody tr")).to_have_count(50)
    expect(page.locator("#screening-evidence [id^='passport-']")).to_have_count(8)
    screening_back(page, "summary", locale)
    expect(page.locator("[data-queue-id]")).to_have_count(5)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_empty_queue_renders_explicit_state(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    response = open_queue(page, "resilience_case", locale)
    assert response.json()["total"] == 0
    view = page.locator("#screening-view")
    expect(view).to_contain_text(
        locale_bundle(locale)["strings"]["screening.queue.empty"]
    )
    expect(view.locator("table")).to_have_count(0)
    expect(view.locator("[data-screening-back='summary']")).to_be_enabled()
    _shot(browser_session, "queue-empty", locale)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_queue_pagination_shows_pareto_rank_without_ordinal_list(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    first = open_queue(page, "likely_false_positive", locale).json()
    strings = locale_bundle(locale)["strings"]
    expect(page.locator(".screening-pagination")).to_contain_text(
        strings["screening.queue.showing"].format(
            **{"from": "1", "to": "50", "total": "4727"}
        )
    )
    displayed = [
        int(row.locator("td").nth(1).inner_text())
        for row in page.locator("#screening-view tbody tr").all()
    ]
    assert displayed == [row["pareto_rank"] for row in first["entries"]]
    page.locator("[data-screening-page='next']").click()
    expect(page.locator(".screening-pagination")).to_contain_text(
        strings["screening.queue.showing"].format(
            **{"from": "51", "to": "100", "total": "4727"}
        )
    )
    second = _api_json(
        page,
        "/api/screening/queues/likely_false_positive?offset=50&limit=50",
    )
    displayed = [
        int(row.locator("td").nth(1).inner_text())
        for row in page.locator("#screening-view tbody tr").all()
    ]
    assert displayed == [row["pareto_rank"] for row in second["entries"]]
    headers = page.locator("#screening-view th").all_inner_texts()
    assert not any(value.casefold() in {"rank", "ordinal"} for value in headers)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_surface_is_public_only_when_simulation_mode_is_active(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    urls: list[str] = []
    page.on(
        "request",
        lambda request: (
            urls.append(request.url)
            if "/api/screening" in request.url
            else None
        ),
    )
    goto_portfolio(page, "simulated", locale)
    open_screening(page, locale)
    queue = open_queue(page, "robust_public_finding", locale).json()
    open_record(page, queue["entries"][0]["hs6"], locale)
    text = page.locator("#screening").inner_text()
    for label in locale_bundle(locale)["synthetic_labels"].values():
        assert label not in text
    assert urls
    assert all("mode" not in parse_qs(urlsplit(url).query) for url in urls)


def _fulfill(route: Route, payload: dict, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        headers={"x-ior-mock": "1"},
        body=json.dumps(payload, ensure_ascii=False),
    )


def _install_screening_mocks(
    page: Page,
    summary: dict,
    evidence: dict,
    partial: bool,
) -> None:
    empty = _fixture("queue-empty.json")
    partial_queue = _fixture(
        "queue-partial-robust_public_finding.json"
    )
    partial_record = _fixture("record-partial-030579.json")

    def queue_handler(route: Route) -> None:
        queue_id = urlsplit(route.request.url).path.rsplit("/", 1)[-1]
        summary_row = next(
            row for row in summary["queues"] if row["queue_id"] == queue_id
        )
        payload = deepcopy(empty)
        payload.update(
            {
                "queue_id": queue_id,
                "ordering_basis": summary_row["ordering_basis"],
            }
        )
        if partial and queue_id == "robust_public_finding":
            payload = deepcopy(partial_queue)
        _fulfill(route, payload)

    def record_handler(route: Route) -> None:
        hs6 = urlsplit(route.request.url).path.rsplit("/", 1)[-1]
        if partial and hs6 == partial_record["hs6"]:
            _fulfill(route, partial_record)
        else:
            _fulfill(
                route,
                {"detail": {"code": "RECORD_NOT_FOUND"}},
                status=404,
            )

    page.route(
        re.compile(r".*/api/screening/evidence(?:\?.*)?$"),
        lambda route: _fulfill(route, evidence),
    )
    page.route(
        re.compile(r".*/api/screening/queues/[^?]+(?:\?.*)?$"),
        queue_handler,
    )
    page.route(
        re.compile(r".*/api/screening/records/[^?]+(?:\?.*)?$"),
        record_handler,
    )
    page.route(
        re.compile(r".*/api/screening(?:\?.*)?$"),
        lambda route: _fulfill(route, summary),
    )


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_unavailable_and_partial_universe_render_explicit_states(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    strings = locale_bundle(locale)["strings"]
    real_ids = [
        row["passport_id"] for row in _frozen_summary()["evidence_passports"]
    ]
    scenarios = (
        (
            _fixture("summary-unavailable.json"),
            _fixture("evidence-unavailable.json"),
            False,
        ),
        (
            _fixture("summary-partial.json"),
            _fixture("evidence-partial.json"),
            True,
        ),
    )
    responses = []
    page.on(
        "response",
        lambda response: (
            responses.append(response)
            if "/api/screening" in response.url
            else None
        ),
    )
    for summary, evidence, partial in scenarios:
        page.unroute_all()
        responses.clear()
        _install_screening_mocks(page, summary, evidence, partial)
        goto_portfolio(page, "public", locale)
        open_screening(page, locale)
        evidence_area = page.locator("#screening-evidence")
        if not partial:
            expect(page.locator(".universe-card")).to_contain_text(
                strings["screening.status.unavailable"]
            )
            expect(evidence_area.locator("[data-evidence-state='none']")).to_have_text(
                strings["screening.evidence.no_snapshot"]
            )
            expect(evidence_area).to_contain_text(
                strings["reason.no_screening_snapshot"]
            )
            expect(evidence_area).to_contain_text("NO_SCREENING_SNAPSHOT")
            expect(page.locator("[id^='passport-']")).to_have_count(0)
            page.locator("[data-queue-id]").first.click()
            expect(page.locator("#screening-view")).to_contain_text(
                strings["screening.queue.empty"]
            )
        else:
            expect(page.locator(".universe-card")).to_contain_text(
                strings["screening.status.partial"]
            )
            expect(evidence_area.locator("[id^='passport-']")).to_have_count(
                len(evidence["evidence_passports"])
            )
            assert evidence_area.locator(
                ".unit-card.explicit-state"
            ).count() == (
                len(evidence["universe_units"])
                - len(evidence["evidence_passports"])
            )
        screening_text = page.locator("#screening").inner_text()
        absent = set(real_ids) - {
            row["passport_id"] for row in evidence["evidence_passports"]
        }
        assert all(value not in screening_text for value in absent)
        assert "SCREENING-SAU-2026-09-12-9b6b22032fd8" not in screening_text
        assert responses
        assert all(
            response.header_value("x-ior-mock") == "1"
            for response in responses
        )


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_screening_views_keyboard_traversal_with_visible_focus(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    queue = open_queue(page, "robust_public_finding", locale).json()
    queue_report = keyboard_focus_report(page)
    expected_records = tuple(
        f"record:{row['hs6']}" for row in queue["entries"]
    )
    assert "screening-back:summary" in queue_report.dom_order
    assert "page:next" in queue_report.dom_order
    assert all(value in queue_report.dom_order for value in expected_records)
    assert all(item.focus_visible for item in queue_report.records)
    page.locator(f"[data-hs6='{queue['entries'][0]['hs6']}']").focus()
    page.keyboard.press("Enter")
    expect(page.locator(".screening-record")).to_be_visible()
    record_report = keyboard_focus_report(page)
    hrefs = tuple(
        f"href:{anchor.get_attribute('href')}"
        for anchor in page.locator(
            "[data-passport-ref][data-passport-scope='universe']"
        ).all()
    )
    assert "screening-back:queue" in record_report.dom_order
    assert all(value in record_report.dom_order for value in hrefs)
    anchor = page.locator(
        "[data-passport-ref][data-passport-scope='universe']"
    ).first
    target = anchor.get_attribute("href").removeprefix("#")
    anchor.focus()
    page.keyboard.press("Enter")
    assert page.evaluate("() => document.activeElement.id") == target


@pytest.mark.parametrize(
    ("view", "locale"),
    tuple(product(("summary", "queue", "record"), LOCALES)),
    ids=[
        f"{view}-{locale.code}"
        for view, locale in product(("summary", "queue", "record"), LOCALES)
    ],
)
def test_screening_views_have_zero_wcag_21_aa_axe_violations(
    browser_session: BrowserSession,
    view: str,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    if view in {"queue", "record"}:
        queue = open_queue(page, "robust_public_finding", locale).json()
        if view == "record":
            open_record(page, queue["entries"][0]["hs6"], locale)
    result = run_axe(page)
    assert result["violations"] == [], format_axe_violations(
        result["violations"]
    )


def test_screening_surface_rtl_direction_and_arabic_glyphs(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", AR)
    open_screening(page, AR)
    queue = open_queue(page, "robust_public_finding", AR).json()
    open_record(page, queue["entries"][0]["hs6"], AR)
    assert page.locator("#screening").evaluate(
        "(node) => getComputedStyle(node).direction"
    ) == "rtl"
    assert all(
        node.evaluate("(value) => getComputedStyle(value).direction") == "ltr"
        for node in page.locator("#screening .technical-token").all()
    )
    report = verify_arabic_rendering(page)
    assert report.document_direction == "rtl"
    assert report.intended_font_loaded is True


def test_screening_surface_has_no_english_catalogue_prose_in_arabic(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", AR)
    open_screening(page, AR)
    reports: list[tuple[str, dict]] = []
    reports.append(("summary", arabic_parity_report(page, "#screening")))
    open_queue(page, "robust_public_finding", AR)
    reports.append(("queue-robust", arabic_parity_report(page, "#screening")))
    screening_back(page, "summary", AR)
    open_queue(page, "likely_false_positive", AR)
    reports.append(("queue-lfp", arabic_parity_report(page, "#screening")))
    screening_back(page, "summary", AR)
    queue = open_queue(page, "robust_public_finding", AR).json()
    open_record(page, queue["entries"][0]["hs6"], AR)
    reports.append(("record", arabic_parity_report(page, "#screening")))

    allowed = {
        "hs_code",
        "hex_digest",
        "run_id",
        "iso_datetime",
        "url",
        "version",
        "governed_id",
        "code_token",
        "catalogue_key",
        "number",
        "number_range",
    }
    for name, report in reports:
        assert_arabic_parity(report, expected_source_spans=0)
        assert set(report["islands_by_class"]) <= allowed
        output = (
            browser_session.artifact_dir
            / "screening"
            / f"parity-{name}-ar.json"
        )
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    record = dict(reports)["record"]["islands_by_class"]
    assert record.get("hex_digest", 0) >= 8
    assert record.get("run_id", 0) >= 8


@pytest.mark.parametrize(
    "case_id",
    PARITY_CASE_IDS,
    ids=lambda value: f"ar-{value}",
)
def test_arabic_parity_predicate_fails_on_injected_english(
    browser_session: BrowserSession,
    case_id: str,
) -> None:
    case = next(
        row
        for row in json.loads(PARITY_FIXTURE.read_text(encoding="utf-8"))
        if row["id"] == case_id
    )
    page = browser_session.page
    goto_portfolio(page, "public", AR)
    open_screening(page, AR)
    queue = open_queue(page, "robust_public_finding", AR).json()
    open_record(page, queue["entries"][0]["hs6"], AR)
    clean = arabic_parity_report(page, "#screening")
    assert_arabic_parity(clean, expected_source_spans=0)
    if case["kind"] == "island":
        page.evaluate(
            """(html) => {
              document.querySelector("#screening-view")
                .insertAdjacentHTML("beforeend", html);
            }""",
            case["html"],
        )
    else:
        page.evaluate(
            """(text) => {
              const node = document.createElement("p");
              node.appendChild(document.createTextNode(text));
              document.querySelector("#screening-view").appendChild(node);
            }""",
            case["text"],
        )
    report = arabic_parity_report(page, "#screening")
    for field, expected in case["expect"].items():
        if field == "class":
            continue
        value = report[field]
        count = len(value) if isinstance(value, list) else value
        assert count >= 1 if expected == ">=1" else count == expected
    with pytest.raises(AssertionError):
        assert_arabic_parity(report, expected_source_spans=0)
    page.reload(wait_until="domcontentloaded")


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_no_candidate_deep_case_renders_disposition_label_not_null(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    expected = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "public_decision"
            / "no-candidate-no-fired-signal.expected.json"
        ).read_text(encoding="utf-8")
    )
    opportunity_id = expected["analysis"]["opportunity"]["id"]
    page.route(
        re.compile(r".*/api/opportunities\?mode=public$"),
        lambda route: _fulfill(route, [expected["list_entry"]]),
    )
    page.route(
        re.compile(
            rf".*/api/opportunities/{opportunity_id}"
            r"/ui-manifest\?mode=public$"
        ),
        lambda route: _fulfill(route, expected["ui_manifest"]),
    )
    page.route(
        re.compile(
            rf".*/api/opportunities/{opportunity_id}\?mode=public$"
        ),
        lambda route: _fulfill(route, expected["analysis"]),
    )
    page.goto(f"/?locale={locale.code}", wait_until="domcontentloaded")
    expect(page.locator("body")).to_have_attribute("aria-busy", "false")
    strings = locale_bundle(locale)["strings"]
    for selector in (
        ".decision-hero",
        ".integrity-banner",
        ".opportunity-card",
    ):
        node = page.locator(selector)
        expect(node).to_contain_text(strings["disposition.no_candidate"])
        expect(node).to_contain_text("NO_CANDIDATE")
    expect(page.locator(".decision-hero")).to_contain_text(
        expected["analysis"]["real_decision"]["localized_narrative"][
            locale.code
        ]["headline"]["text"]
    )
    visible = page.locator("body").inner_text()
    assert not re.search(r"\b(?:None|null)\b", visible)
