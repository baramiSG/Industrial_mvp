"""Executive and analyst degradation must remain explicit and context-bound."""

import json

import pytest
from playwright.sync_api import expect

from browser_tests.executive_pages import api_json, goto_executive
from browser_tests.harness import EN, LOCALES, STEEL, POLYPROPYLENE
from browser_tests.pages import goto_portfolio, select_case

pytestmark = pytest.mark.e2e


def test_analyst_sources_and_native_executive_link_keep_current_case(browser_session):
    page = browser_session.page
    goto_portfolio(page, "public", EN)
    select_case(page, POLYPROPYLENE, "public", EN)
    link = page.locator("[data-executive-link]")
    expect(link).to_have_attribute("href", f"/executive?opportunity={POLYPROPYLENE.id}&locale=en")
    trigger = page.locator('[data-claim-id="metric.trade"]')
    assert trigger.count() == 1
    trigger.click()
    panel = page.locator("[data-claim-evidence]")
    expect(panel).to_be_focused()
    assert panel.locator("[data-passport-id]").evaluate_all("rows => rows.map(r => r.dataset.passportId)") == ["P-WITS-390210"]
    expect(page.locator("[data-claim-graph]")).to_have_attribute("href", f"/?opportunity={POLYPROPYLENE.id}&locale=en&mode=public&graphView=evidence_to_change")
    page.keyboard.press("Escape")
    expect(trigger).to_be_focused()


@pytest.mark.parametrize("surface", ("analyst", "executive"))
@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
@pytest.mark.parametrize("status", ("PASS", "FAIL"))
def test_analyst_uses_computed_integrity_failure_and_affected_case(browser_session, surface, locale, status):
    from ior_mvp.executive.models import ExecutiveSummary
    from browser_tests.executive_pages import STEPS, select_step
    from browser_tests.harness import run_axe, format_axe_violations
    from browser_tests.pages import arabic_parity_report

    page = browser_session.page
    summary = api_json(page, "/api/executive/summary")
    count = 27 if status == "FAIL" else 0
    if status == "FAIL":
        summary["integrity"].update(status=status, violation_count=count)
        check = next(row for row in summary["integrity"]["checks"] if row["check_id"] == "REAL_DECISION_EQUALITY")
        check.update(status=status, violation_count=count, affected_ids=[STEEL.id])
    ExecutiveSummary.model_validate(summary)
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    page.route("**/api/executive/summary", lambda route: route.fulfill(json=summary))
    if surface == "analyst":
        goto_portfolio(page, "public", locale)
        metric = page.locator("[data-computed-integrity]")
        assert metric.count() == 1
        expect(metric).to_have_attribute("data-computed-integrity", status)
        expect(metric).to_contain_text(str(count))
        if status == "FAIL":
            expect(metric).to_contain_text(STEEL.id)
        return
    goto_executive(page, locale=locale)
    notice = page.locator("[data-executive-integrity]")
    for width in (390, 1024, 1440):
        page.set_viewport_size({"width": width, "height": 1000})
        for step in STEPS:
            select_step(page, step)
            expect(notice).to_be_visible()
            expect(notice).to_have_attribute("data-executive-integrity", status)
            expect(notice.locator("[data-integrity-count]")).to_have_text(str(count))
            assert notice.get_attribute("role") == ("alert" if status == "FAIL" else None)
            assert notice.evaluate("n=>Boolean(n.compareDocumentPosition(document.querySelector('#executive-comparison')) & Node.DOCUMENT_POSITION_FOLLOWING)")
            expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")
            expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-route", "NOT_CALCULABLE")
            expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-state", "ADVANCE")
            expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-route", "5")
            if status == "FAIL":
                assert notice.locator("[data-integrity-check]").evaluate_all("rows=>rows.map(row=>row.dataset.integrityCheck)") == [row["check_id"] for row in summary["integrity"]["checks"]]
                for check in summary["integrity"]["checks"]:
                    row = notice.locator(f'[data-integrity-check="{check["check_id"]}"]')
                    expect(row).to_be_visible()
                    expect(row).to_contain_text(strings["executive.integrity." + check["check_id"].lower()])
                    expect(row).to_contain_text(strings["executive.status." + check["status"].lower()])
                    assert row.locator("bdi").all_text_contents() == [str(check["violation_count"]), *check["affected_ids"]]
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            result = run_axe(page)
            assert result["violations"] == [], format_axe_violations(result["violations"])
            if locale.code == "ar":
                report = arabic_parity_report(page, "[data-executive-main]")
                assert all(report[key] == [] for key in ("island_failures", "latin_prose_runs", "latin_runs", "label_leaks")), report
    select_step(page, "SIGNAL")
    page.locator("[data-executive-next]").focus(); page.keyboard.press("Enter")
    expect(page.locator("[data-active-step]")).to_have_attribute("data-active-step", "FALSE_POSITIVE_CONTROLS")
    page.locator("[data-executive-back]").focus(); page.keyboard.press("Enter")
    expect(page.locator("[data-active-step]")).to_have_attribute("data-active-step", "SIGNAL")
    trigger = page.locator('[data-branch="PUBLIC"] [data-claim-id="decision.public"]')
    trigger.focus(); page.keyboard.press("Enter")
    expect(page.locator("[data-claim-evidence]")).to_be_focused()
    page.keyboard.press("Escape"); expect(trigger).to_be_focused()


@pytest.mark.parametrize("mutation", ["foreign-evidence", "public-synthetic", "snapshot", "real-decision", *[f"analyst-{mode}-{change}" for mode in ("public", "simulated") for change in ("public-state", "public-route", "active-state", "active-route")], *[f"analyst-simulated-{change}" for change in ("simulation-state", "simulation-route", "scenario")]])
@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_inconsistent_join_never_exposes_a_claim(browser_session, mutation, locale):
    from ior_mvp.executive.models import ExecutiveCase
    page = browser_session.page
    analyst = mutation.startswith("analyst-")
    mode = mutation.split("-")[1] if analyst else "public"
    if analyst:
        change = mutation.split("-", 2)[2]
        if change.startswith("active-"):
            url = f"/api/opportunities/{STEEL.id}?mode={mode}"
            payload = api_json(page, url)
            payload["active_decision"]["state" if change == "active-state" else "route_code"] = "REJECT" if change == "active-state" else 8
        else:
            url = f"/api/executive/opportunities/{STEEL.id}"
            payload = api_json(page, url)
            if change == "scenario":
                payload["decisions"]["simulated"]["scenario_id"] = "FOREIGN"
            else:
                branch, field = change.split("-")
                branch = "simulated" if branch == "simulation" else branch
                payload["decisions"][branch]["state" if field == "state" else "route_code"] = "REJECT" if field == "state" else 0
            ExecutiveCase.model_validate(payload)
    elif mutation == "real-decision":
        url = f"/api/opportunities/{STEEL.id}?mode=simulated"
        payload = api_json(page, url)
        payload["real_decision"]["state"] = "ADVANCE"
    else:
        url = f"/api/executive/opportunities/{STEEL.id}"
        payload = api_json(page, url)
        if mutation == "foreign-evidence":
            payload["claims"][0]["evidence_ids"] = ["FOREIGN-ROW"]
        elif mutation == "public-synthetic":
            payload["evidence_index"][0]["source"] = "DEMO_GENERATOR"
        else:
            payload["opportunity"]["snapshot_id"] = "UNRELATED-SNAPSHOT"
    page.route(f"**{url}", lambda route: route.fulfill(json=payload))
    if not analyst:
        page.goto(f"/executive?opportunity={STEEL.id}&locale={locale.code}")
        expect(page.locator("[data-executive-retry]")).to_be_visible()
        expect(page.locator("[data-claim-id]")).to_have_count(0)
        expect(page.locator("[data-branch]")).to_have_count(0)
        return
    goto_portfolio(page, mode, locale)
    expect(page.locator("[data-claim-id]")).to_have_count(0)
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    expect(page.locator(".claim-unavailable").first).to_have_text(strings["executive.ui.source_unavailable"])
    expect(page.locator("#analyst-claim-sources")).to_be_empty()
    # The real analysis still renders; a rejected optional source join cannot replace its conclusion.
    expect(page.locator(".integrity-banner .state-chip").first).to_contain_text(STEEL.real_state)
    select_case(page, POLYPROPYLENE, mode, locale)
    trigger = page.locator('[data-claim-id="metric.trade"]')
    expect(trigger).to_have_count(1)
    trigger.click()
    expect(page.locator("[data-claim-evidence]")).to_be_focused()
    assert page.locator("[data-passport-id]").evaluate_all("rows=>rows.map(row=>row.dataset.passportId)") == ["P-WITS-390210"]


def test_unresolved_claim_names_actual_case_wide_needs(browser_session):
    page = browser_session.page
    oracle = api_json(page, f"/api/executive/opportunities/{STEEL.id}")
    needs = next(row for row in oracle["claims"] if row["claim_id"] == "rule.R6")["missing_need_codes"]
    goto_executive(page)
    page.locator('[data-rule="R6"] > summary').click()
    page.locator('[data-claim-id="rule.R6"]').click()
    panel = page.locator("[data-claim-evidence]")
    expect(panel).to_contain_text("Case-wide unmet needs")
    assert panel.locator("li").all_text_contents() == needs
    expect(panel.locator("[data-passport-id]")).to_have_count(0)


def test_loading_is_visible_before_summary_arrives(browser_session):
    page = browser_session.page
    page.add_init_script("""(() => {
      const original = window.fetch;
      window.fetch = async (...args) => {
        if (String(args[0]).endsWith('/api/executive/summary')) {
          await new Promise(resolve => { window.releaseSummary = resolve; });
        }
        return original(...args);
      };
    })();""")
    page.goto(f"/executive?opportunity={STEEL.id}&locale=en")
    expect(page.locator("[data-executive-main]")).to_have_attribute("aria-busy", "true")
    expect(page.locator("#executive-status")).to_contain_text("Loading")
    expect(page.locator("[data-branch]")).to_have_count(0)
    page.evaluate("() => window.releaseSummary()")
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", STEEL.id)


@pytest.mark.parametrize("kind,locale", [(kind, EN) for kind in ("empty", "empty-explicit-case", "not-found", "unmapped-zero")] + [("no-simulation", locale) for locale in LOCALES])
def test_honest_absence_and_zero_states(browser_session, monkeypatch, kind, locale):
    page = browser_session.page
    summary = api_json(page, "/api/executive/summary")
    if kind in {"empty", "empty-explicit-case"}:
        summary["opportunities"] = []
    elif kind == "unmapped-zero":
        row = {"dataset_kind": "UNMAPPED", "need_codes": ["unmapped-test-need"], "synthetic_flag": False}
        summary["public_dataset_unlocks"].append(row)
        row.update(loaded_case_count=0, loaded_opportunity_ids=[], screening_record_count=0, screening_hs6=[])
    elif kind == "no-simulation":
        from ior_mvp.executive import service
        from ior_mvp.executive.models import ExecutiveCase, ExecutiveSummary
        scenarios = dict(service.synthetic_scenarios())
        scenarios.pop(STEEL.id)
        with monkeypatch.context() as patch:
            patch.setattr(service, "synthetic_scenarios", lambda: scenarios)
            service.clear_executive_caches()
            try:
                detail = service.build_executive_case(STEEL.id).model_dump(mode="json")
                summary = service.build_executive_summary().model_dump(mode="json")
            finally:
                service.clear_executive_caches()
        ExecutiveCase.model_validate(detail)
        ExecutiveSummary.model_validate(summary)
        assert len(summary["opportunities"]) == 11 and len(summary["synthetic_evsi"]["cases"]) == 10
        assert all(row["opportunity_id"] != STEEL.id for row in summary["synthetic_evsi"]["cases"])
        page.route(f"**/api/executive/opportunities/{STEEL.id}", lambda route: route.fulfill(json=detail))
        page.route(f"**/api/opportunities/{STEEL.id}?mode=simulated", lambda route: pytest.fail("Unavailable scenario must not be fetched"))
    page.route("**/api/executive/summary", lambda route: route.fulfill(json=summary))
    if kind in {"empty", "empty-explicit-case", "not-found"}:
        page.goto("/executive?locale=en&opportunity=UNKNOWN" if kind == "not-found" else f"/executive?locale=en&opportunity={STEEL.id}" if kind == "empty-explicit-case" else "/executive?locale=en")
        expect(page.locator("#executive-status")).to_contain_text("not in the loaded" if kind == "not-found" else "No opportunities")
        expect(page.locator("[data-branch]")).to_have_count(0)
    else:
        goto_executive(page, locale=locale, step="MISSING_MINISTRY_FACTS" if kind == "unmapped-zero" else "SIMULATED_EVIDENCE")
        if kind == "unmapped-zero":
            expect(page.locator('[data-dataset="UNMAPPED"]')).to_contain_text("Unmapped need")
            assert page.locator('[data-dataset="UNMAPPED"] dd').all_text_contents() == ["0", "0"]
        else:
            from browser_tests.executive_pages import STEPS, select_step
            from browser_tests.pages import arabic_parity_report
            from browser_tests.harness import run_axe, format_axe_violations
            strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
            expect(page.locator("[data-active-step]")).to_contain_text(strings["executive.ui.no_simulation"])
            for step in STEPS:
                select_step(page, step)
                expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")
                expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-route", "NOT_CALCULABLE")
                unavailable = page.locator('[data-branch="SIMULATED"]')
                expect(unavailable).to_have_attribute("data-state", "UNAVAILABLE")
                expect(unavailable).to_contain_text(strings["executive.ui.no_simulation"])
                expect(unavailable).not_to_contain_text(strings["executive.ui.actual_class"])
                expect(page.locator("[data-case-evsi], .synthetic-labels")).to_have_count(0)
                assert "DEMO_GENERATOR" not in page.locator("[data-executive-main]").inner_text()
                assert "null" not in unavailable.inner_text()
                expect(page.locator('[data-claim-id="decision.simulated"]')).to_have_count(0)
                if locale.code == "ar":
                    report = arabic_parity_report(page, "[data-executive-main]")
                    assert all(report[key] == [] for key in ("island_failures", "latin_prose_runs", "latin_runs", "label_leaks")), report
                result = run_axe(page)
                assert result["violations"] == [], format_axe_violations(result["violations"])
            trigger = page.locator('[data-branch="PUBLIC"] [data-claim-id="decision.public"]')
            trigger.focus(); page.keyboard.press("Enter")
            expect(page.locator("[data-claim-evidence]")).to_be_focused()
            page.keyboard.press("Escape"); expect(trigger).to_be_focused()


def test_malicious_source_is_text_and_unsafe_url_has_no_link(browser_session):
    page = browser_session.page
    original = api_json(page, f"/api/opportunities/{STEEL.id}?mode=public")
    original["evidence"][0].update(title='<img src="https://invalid.example/x" onerror="window.pwned=true">', url="javascript:window.pwned=true")
    page.route(f"**/api/opportunities/{STEEL.id}?mode=public", lambda route: route.fulfill(json=original))
    goto_executive(page)
    page.locator('[data-active-step] [data-claim-id="metric.trade"]').click()
    panel = page.locator("[data-claim-evidence]")
    expect(panel).to_contain_text('<img src="https://invalid.example/x"')
    expect(panel.locator("img, a[href^='javascript:']")).to_have_count(0)
    assert page.evaluate("window.pwned === undefined")


@pytest.mark.parametrize("failure,locale_code,repeat", [(kind, "en", False) for kind in ("summary", "detail", "locale", "analyst-source", "analyst-summary")] + [("summary", "ar", False), ("summary", "en", True), ("summary", "ar", True)])
def test_transport_failures_are_explicit_without_stale_sources(new_context, app_server, failure, locale_code, repeat):
    from browser_tests.harness import BrowserFailureCollector

    context = new_context(base_url=app_server.base_url, locale="en-US", viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    collector = BrowserFailureCollector(app_server.base_url)
    collector.attach_context(context)
    page = context.new_page()
    collector.attach_page(page)
    strings = api_json(page, f"/api/ui-strings/{locale_code}")["strings"]
    if repeat:
        page.goto(f"/executive?opportunity=UNKNOWN&locale={locale_code}")
        expect(page.locator("[data-executive-retry]")).to_be_visible()
        expect(page.locator("[data-executive-integrity]")).to_have_attribute("data-executive-integrity", "PASS")
        expect(page.locator("[data-integrity-count]")).to_have_text("0")
    if failure == "locale":
        goto_executive(page)
        old_url = page.url
        endpoint, status = "/api/ui-strings/ar", 503
    elif failure in {"summary", "analyst-summary"}:
        endpoint, status = "/api/executive/summary", 503
    else:
        endpoint, status = f"/api/executive/opportunities/{STEEL.id}", 422
    page.route(f"**{endpoint}", lambda route: route.fulfill(status=status, json={"detail": {"code": "TEST_ONLY_FAILURE", "message": "Unavailable test response"}}))
    if failure == "locale":
        page.locator("[data-executive-locale]").click()
        expect(page.locator("#executive-status")).to_contain_text("Language could not be changed")
        assert page.url == old_url
        expect(page.locator("html")).to_have_attribute("lang", "en")
        expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")
    elif failure.startswith("analyst"):
        goto_portfolio(page, "public", EN)
        if failure == "analyst-source":
            expect(page.locator("[data-claim-id]")).to_have_count(0)
            expect(page.locator(".claim-unavailable").first).to_contain_text("Source linkage unavailable")
        else:
            expect(page.locator("[data-computed-integrity]")).to_have_attribute("data-computed-integrity", "UNAVAILABLE")
            assert page.locator("[data-computed-integrity] strong").inner_text() == "Unavailable"
    else:
        if repeat:
            page.locator("[data-executive-retry]").click()
        else:
            page.goto(f"/executive?opportunity={STEEL.id}&locale={locale_code}")
        expect(page.locator("[data-executive-retry]")).to_be_visible()
        expect(page.locator("#executive-status")).to_contain_text(strings["executive.ui.error"])
        if failure == "summary":
            expect(page.locator("[data-executive-integrity]")).to_have_attribute("data-executive-integrity", "UNAVAILABLE")
            expect(page.locator("[data-executive-integrity]")).to_contain_text(strings["executive.status.unavailable"])
            expect(page.locator("[data-integrity-count], [data-integrity-check]")).to_have_count(0)
        expect(page.locator("[data-branch], [data-claim-id]")).to_have_count(0)
        page.unroute(f"**{endpoint}")
        page.locator("[data-executive-retry]").click()
        if repeat:
            page.locator("[data-executive-first]").click()
        expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", STEEL.id)
        expect(page.locator("[data-executive-integrity]")).to_have_attribute("data-executive-integrity", "PASS")
        expect(page.locator("[data-integrity-count]")).to_have_text("0")
    records = collector.records
    assert len(records) == 2, records
    http = next(row for row in records if row.category == "app-http-error")
    console = next(row for row in records if row.category == "console-error")
    assert (http.url, http.status, http.method) == (app_server.base_url + endpoint, status, "GET")
    assert (console.method, console.status, console.url) == ("", None, "")
    reason = "Service Unavailable" if status == 503 else "Unprocessable Entity"
    assert console.detail == f"Failed to load resource: the server responded with a status of {status} ({reason})"
    context.close()


def test_graph_deep_link_uses_selected_context_and_handles_unavailable(browser_session):
    from browser_tests.graph_pages import install_graph_routes
    from browser_tests.graph_fixtures import unavailable_graph_payload

    page = browser_session.page
    install_graph_routes(page, lambda view, opportunity, mode: unavailable_graph_payload(view, opportunity, mode, "CONNECTION_FAILED"))
    page.goto(f"/?opportunity={POLYPROPYLENE.id}&locale=en&mode=simulated&graphView=evidence_to_change")
    expect(page.locator("#opportunity-select")).to_have_value(POLYPROPYLENE.id)
    expect(page.locator(".graph-state-error")).to_be_visible()
    expect(page.locator("[data-graph-view]")).to_have_value("evidence_to_change")
    expect(page.locator(".mode-button.active")).to_have_attribute("data-mode", "simulated")
