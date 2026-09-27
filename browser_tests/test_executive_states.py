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
            if step in ("SIMULATED_EVIDENCE", "ROUTE_COMPARISON", "INTERVENTION", "CONDITIONS_AND_KILL"):
                expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-state", "ADVANCE")
                expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-route", "5")
            else:
                expect(page.locator('[data-branch="SIMULATED"]')).to_have_count(0)
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
            if change == "scenario":
                with pytest.raises(ValueError, match="diagnostic scenario differs"):
                    ExecutiveCase.model_validate(payload)
            else:
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


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
@pytest.mark.parametrize("case,item", [(STEEL, "qualified_volume"), (STEEL, "width_mm"),
                                       (POLYPROPYLENE, "tooling_required")],
                         ids=["steel-pending", "steel-supported", "pp-not-required"])
def test_candidate_request_four_slots_match_typed_finding(browser_session, locale, case, item):
    from browser_tests.candidate_pages import goto_candidate, select_candidate_request, assert_four_request_slots

    page = browser_session.page
    detail, row = goto_candidate(page, case, locale,
                                 role="REFERENCE_LINE" if case.id == STEEL.id else None)
    assert row is not None
    finding = next(value for value in row["findings"] if value["requirement_item_id"] == item)
    select_candidate_request(page, finding)
    assert_four_request_slots(page, row, finding)
    assert page.locator(f'[data-finding-item="{item}"]').get_attribute("data-finding") == finding["rule_id"]
    if finding["next_evidence"] is None:
        assert finding["action_code"] == "NO_ADDITIONAL_REQUEST"
    else:
        assert finding["next_evidence"]["subject_scope"] == row["entity_id"]
    if case.id == POLYPROPYLENE.id:
        assert finding["status"] == "NOT_REQUIRED"
        assert finding["current_recorded"] is False
        assert finding["needed"] is False
        assert finding["next_evidence"] is None
        strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
        for location in ("detail", "reason", "rail"):
            surface = page.locator(f'[data-request-location="{location}"][data-request-item="tooling_required"]')
            expect(surface.locator('[data-request-slot="field"] dd')).to_have_text(
                strings["ministry.slot.not_applicable"]
            )
            expect(surface.locator('[data-request-slot="source"] dd')).to_have_text(
                strings["ministry.slot.not_applicable"]
            )
            expect(surface.locator('[data-request-slot="effect"] dd')).to_have_text(
                strings["ministry.no_additional_request"]
            )
        for company_id, expected_item in (
            ("COMPANY-7b3497b64cf80470", "ministry.item.input_procurement"),
            ("COMPANY-7c27a105b0cfbcbc", "ministry.item.mfr_range_g_10min"),
        ):
            summary = page.locator(f'[data-company="{company_id}"] > p').nth(2)
            expect(summary).to_contain_text(strings[expected_item])
            expect(summary).not_to_contain_text("tooling_required")
    assert detail["decisions"]["public"]["state"] == case.real_state


@pytest.mark.parametrize("case,role", [(STEEL, "REFERENCE_LINE"), (POLYPROPYLENE, None)],
                         ids=["steel", "polypropylene"])
@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_native_finding_details_stays_open_until_actual_navigation(browser_session, case, role, locale):
    from browser_tests.candidate_pages import goto_candidate
    from browser_tests.executive_pages import select_step

    page = browser_session.page
    _, line = goto_candidate(page, case, locale, role=role)
    assert line is not None
    item = line["findings"][0]["requirement_item_id"]
    url = page.url
    parent = page.locator("[data-selected-subject] [data-all-findings]")
    parent.locator(":scope > summary").click()
    expect(parent).to_have_attribute("open", "")
    finding = parent.locator(f'[data-finding-item="{item}"]')
    finding.locator(":scope > summary").click()
    expect(parent).to_have_attribute("open", "")
    expect(finding).to_have_attribute("open", "")
    finding.locator("[data-finding-reason] > summary").click()
    expect(finding.locator("[data-finding-reason]")).to_have_attribute("open", "")
    page.locator("[data-candidate-discovery] > h3").click()
    expect(parent).to_have_attribute("open", "")
    expect(finding).to_have_attribute("open", "")
    assert page.url == url
    finding.locator("[data-ministry-requirement]").click()
    expect(page.locator("[data-selected-request]")).to_have_attribute("data-selected-request", item)
    direct_url = page.url
    select_step(page, "ROUTE_COMPARISON")
    page.locator("[data-executive-back]").click()
    expect(page.locator('[data-active-step="SIMULATED_EVIDENCE"]')).to_be_visible()
    page.goto(direct_url)
    expect(page.locator("[data-selected-request]")).to_have_attribute("data-selected-request", item)


def test_candidate_request_slot_omission_fails_each_local_surface(browser_session):
    from browser_tests.candidate_pages import goto_candidate, select_candidate_request, assert_four_request_slots

    page = browser_session.page
    _, row = goto_candidate(page, STEEL, EN, role="REFERENCE_LINE")
    assert row is not None
    finding = next(value for value in row["findings"] if value["requirement_item_id"] == "qualified_volume")
    select_candidate_request(page, finding)
    assert_four_request_slots(page, row, finding)
    for location in ("detail", "reason", "rail"):
        for slot in ("field", "source", "effect", "scope"):
            scope = page.locator(f'[data-request-location="{location}"][data-request-item="qualified_volume"]')
            cell = scope.locator(f'[data-request-slot="{slot}"]')
            original = cell.evaluate("node => node.outerHTML")
            cell.evaluate("node => node.remove()")
            try:
                with pytest.raises(AssertionError):
                    assert_four_request_slots(page, row, finding)
            finally:
                scope.evaluate("(node, html) => node.insertAdjacentHTML('beforeend', html)", original)
            assert_four_request_slots(page, row, finding)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_ministry_clarity_rendered_quantities_gates_and_range_direction(browser_session, locale):
    from hashlib import sha256
    from browser_tests.candidate_pages import goto_candidate
    from browser_tests.executive_pages import api_json, select_step
    from ior_mvp.config import PROJECT_ROOT

    page = browser_session.page
    page.set_viewport_size({"width": 1440, "height": 900})
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    unit = strings["ministry.unit.kt"]
    observed_ranges = []

    def range_order(token, first, second, unit_text):
        result = token.evaluate("""(node, parts) => {
          const text = node.firstChild, value = text.textContent;
          const a = value.indexOf(parts.first), b = value.indexOf(parts.second, a + parts.first.length);
          if (text.nodeType !== Node.TEXT_NODE || a < 0 || b < 0) throw Error('range text missing');
          const box = (start, end) => { const range = document.createRange();
            range.setStart(text, start); range.setEnd(text, end);
            const rect = range.getBoundingClientRect();
            return {left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom}; };
          return {value, dir: node.dir, first: box(a, a + parts.first.length),
            second: box(b, b + parts.second.length)};
        }""", {"first": first, "second": second})
        assert result["dir"] == "ltr" and result["value"].endswith(unit_text)
        first_box, second_box = result["first"], result["second"]
        assert (first_box["top"] < second_box["top"] or
                (first_box["top"] == second_box["top"] and first_box["right"] < second_box["left"])), result
        observed_ranges.append(result)
        return result

    steel, _ = goto_candidate(page, STEEL, locale, role="REFERENCE_LINE")
    if locale.code == "ar":
        assert page.locator("html").get_attribute("dir") == "rtl"
    requirement = page.locator("[data-requirement-strip]")
    steel_width = requirement.locator("bdi.technical-token", has_text="1,000–1,250 mm")
    steel_thickness = requirement.locator("bdi.technical-token", has_text="0.7–1.5 mm")
    range_order(steel_width, "1,000", "1,250", "mm")
    range_order(steel_thickness, "0.7", "1.5", "mm")
    assert requirement.locator("bdi.technical-token", has_text="275 g/m²").count() == 1
    selected = page.locator("[data-selected-subject]")
    selected.locator("[data-all-findings] > summary").click()
    p09 = selected.locator('[data-finding-item="qualified_volume"]')
    p09.locator(":scope > summary").click()
    quantity = p09.locator("[data-volume-context]")
    for key in ("ministry.target_demand", "ministry.record.field.admitted_qualified_supply_kt",
                "ministry.shortage_headroom", "ministry.record.field.window_result", "ministry.modeled_window"):
        expect(quantity).to_contain_text(strings[key])
    for value in (f"104 {unit}", f"57.5092 {unit}", f"46.4908 {unit}"):
        expect(quantity).to_contain_text(value)
    expect(quantity).to_contain_text(strings["ministry.window.covered"])
    for field, current_text, needed_text, current_parts, needed_parts, unit_text in (
        ("width_mm", "600–1,300 mm", "1,000–1,250 mm", ("600", "1,300"), ("1,000", "1,250"), "mm"),
        ("thickness_mm", "0.18–3 mm", "0.7–1.5 mm", ("0.18", "3"), ("0.7", "1.5"), "mm"),
        ("coating_mass_g_m2", "45–350 g/m²", None, ("45", "350"), None, "g/m²"),
    ):
        finding = selected.locator(f'[data-finding-item="{field}"]')
        finding.locator(":scope > summary").click()
        operands = finding.locator(".ministry-operands")
        range_order(operands.locator("bdi.technical-token", has_text=current_text), *current_parts, unit_text)
        if needed_parts:
            range_order(operands.locator("bdi.technical-token", has_text=needed_text), *needed_parts, unit_text)
        else:
            assert operands.locator("bdi.technical-token", has_text="275 g/m²").count() == 1
    comparison = page.locator("[data-line-comparison]")
    expect(comparison).to_contain_text(strings["ministry.coverage_explanation"])
    legend = comparison.locator("[data-comparison-capability-legend]")
    legend.locator("summary").click()
    for state_code in ("0", "1", "2", "3", "U"):
        expect(legend.locator(f'[data-capability-legend-state="{state_code}"]')).to_have_text(
            strings[f'executive.capability.state.{state_code.lower()}']
        )
    expect(legend).to_contain_text(strings["executive.capability.simulation_note"])
    a = comparison.locator('[data-line-row="LINE-7315366f6a9166d8"]')
    expect(a).to_contain_text("0.2667")
    expect(a.locator("[data-comparison-quantity]")).to_contain_text(strings["ministry.capacity_result"])
    expect(a.locator("[data-comparison-quantity]")).to_contain_text("FORMULA")
    expect(a.locator("[data-dstar-withheld]")).to_have_count(0)
    for field, text, first, second, unit_text in (
        ("width_mm", "1,000–1,250 mm", "1,000", "1,250", "mm"),
        ("thickness_mm", "0.7–1.5 mm", "0.7", "1.5", "mm"),
        ("coating_mass_g_m2", "45–350 g/m²", "45", "350", "g/m²"),
    ):
        range_order(a.locator(f'[data-comparison-field="{field}"] bdi.technical-token', has_text=text), first, second, unit_text)
    c = comparison.locator('[data-line-row="LINE-4fbdbb0b2c107968"]')
    expect(c.locator('[data-blocking-gate="width_thickness_envelope"]')).to_contain_text(strings["ministry.gate.unavailable"])
    expect(c.locator('[data-affected-requirement="width_mm"]')).to_have_count(1)
    assert c.locator("[data-comparison-quantity] dd").all_text_contents()[1:3] == [
        strings["common.unavailable"], strings["common.unavailable"],
    ]
    steel_quantity_text = quantity.inner_text()
    steel_c_quantity_text = c.locator("[data-comparison-quantity]").inner_text()
    steel_c_capacity_result = c.locator("[data-comparison-quantity] > div").first.locator("dd").inner_text()
    steel_c_gates = c.locator("[data-blocking-gate]").evaluate_all("nodes => nodes.map(node => ({id: node.dataset.blockingGate, text: node.innerText}))")
    steel_image = browser_session.artifact_dir / f"label-closure-steel-gates-{locale.code}.png"
    c.locator("[data-dstar-withheld]").scroll_into_view_if_needed()
    page.screenshot(path=str(steel_image), full_page=False, animations="disabled", caret="hide")
    select_step(page, "ROUTE_COMPARISON")
    reference = page.locator("[data-reference-comparison]")
    for key in ("dossier.field.incremental_capacity_kt", "dossier.field.schedule_months",
                "dossier.field.greenfield_alternative"):
        expect(reference).to_contain_text(strings[key])
    expect(reference).to_contain_text(f"50 {unit}")
    expect(reference).to_contain_text(f"18 {strings['ministry.months']}")
    expect(reference).to_contain_text(strings["common.unavailable"])

    pp_detail, _ = goto_candidate(page, POLYPROPYLENE, locale, line_id="LINE-cb9a42384c3523ec")
    requirement = page.locator("[data-requirement-strip]")
    range_order(requirement.locator("bdi.technical-token", has_text="12–20 g/10min"), "12", "20", "g/10min")
    selected = page.locator("[data-selected-subject]")
    selected.locator("[data-all-findings] > summary").click()
    mfr = selected.locator('[data-finding-item="mfr_range_g_10min"]')
    mfr.locator(":scope > summary").click()
    for token, start, end in (("2–6 g/10min", "2", "6"), ("12–20 g/10min", "12", "20")):
        range_order(mfr.locator(".ministry-operands bdi.technical-token", has_text=token), start, end, "g/10min")
    for field in ("polymer_family", "manufacturing_scope", "grade_family", "additives_required"):
        expect(selected.locator(f'[data-finding-item="{field}"] > summary')).to_contain_text(strings[f"ministry.item.{field}"])
    b = page.locator('[data-line-row="LINE-cb9a42384c3523ec"]')
    expect(b.locator("[data-comparison-quantity]")).to_contain_text("ADMITTED")
    expect(b.locator('[data-blocking-gate="performance_requirement"]')).to_contain_text(strings["ministry.gate.known_failure"])
    expect(b.locator('[data-affected-requirement="mfr_range_g_10min"]')).to_have_count(1)
    mfr_comparison = b.locator('[data-comparison-field="mfr_range_g_10min"]')
    for token, start, end in (("2–6 g/10min", "2", "6"), ("12–20 g/10min", "12", "20")):
        range_order(mfr_comparison.locator("bdi.technical-token", has_text=token), start, end, "g/10min")
    expect(b.locator("[data-comparison-quantity]")).to_contain_text(f"0 {unit}")
    expect(b.locator("[data-comparison-quantity]")).to_contain_text(f"56 {unit}")
    a_pp = page.locator('[data-line-row="LINE-e403e85a85052861"] [data-comparison-quantity]')
    expect(a_pp).to_contain_text(f"70 {unit}")
    assert f"-14 {unit}" in a_pp.inner_text().replace("\u200e", "")
    pp_labels = {field: selected.locator(f'[data-finding-item="{field}"] > summary').inner_text()
                 for field in ("polymer_family", "manufacturing_scope", "grade_family", "additives_required")}
    pp_gate = b.locator('[data-blocking-gate="performance_requirement"]')
    pp_image = browser_session.artifact_dir / f"label-closure-pp-labels-{locale.code}.png"
    selected.locator('[data-finding-item="polymer_family"] > summary').scroll_into_view_if_needed()
    page.screenshot(path=str(pp_image), full_page=False, animations="disabled", caret="hide")
    source_paths = (
        "src/ior_mvp/static/modules/executive/candidates.js",
        "src/ior_mvp/static/modules/executive/labels.js",
        "src/ior_mvp/static/css/executive.css",
        "config/ui_strings.v1.yaml",
        "browser_tests/parity_grammar.py",
    )
    receipt = {
        "locale": locale.code,
        "steel_public_state": steel["decisions"]["public"]["state"],
        "pp_public_state": pp_detail["decisions"]["public"]["state"],
        "steel_p09": steel_quantity_text,
        "steel_c_quantity": steel_c_quantity_text,
        "steel_c_capacity_result": steel_c_capacity_result,
        "steel_c_gates": steel_c_gates,
        "pp_b_quantity": b.locator("[data-comparison-quantity]").inner_text(),
        "pp_b_capacity_result": b.locator("[data-comparison-quantity] > div").first.locator("dd").inner_text(),
        "pp_b_gate": {"id": pp_gate.get_attribute("data-blocking-gate"), "text": pp_gate.inner_text()},
        "pp_mapped_labels": pp_labels,
        "pp_a_quantity": a_pp.inner_text(),
        "ranges": observed_ranges,
        "source_sha256": {path: sha256((PROJECT_ROOT / path).read_bytes()).hexdigest() for path in source_paths},
        "screenshots": {path.name: sha256(path.read_bytes()).hexdigest() for path in (steel_image, pp_image)},
    }
    (browser_session.artifact_dir / f"source-clarity-{locale.code}.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )


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
                if step in ("SIMULATED_EVIDENCE", "ROUTE_COMPARISON", "INTERVENTION", "CONDITIONS_AND_KILL"):
                    expect(unavailable).to_have_attribute("data-state", "UNAVAILABLE")
                    expect(unavailable).to_contain_text(strings["executive.ui.no_simulation"])
                    expect(unavailable).not_to_contain_text(strings["executive.ui.actual_class"])
                else:
                    expect(unavailable).to_have_count(0)
                expect(page.locator("[data-case-evsi], .synthetic-labels")).to_have_count(0)
                assert "DEMO_GENERATOR" not in page.locator("[data-executive-main]").inner_text()
                if unavailable.count():
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


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
@pytest.mark.parametrize(
    "opening",
    ("both", "view_only", "open_only", "both_nondefault_held", "error_retry", "unavailable_retry", "manual_reopen"),
)
def test_candidate_graph_open_requests_preserve_scope(browser_session, locale, opening):
    from types import SimpleNamespace
    from urllib.parse import parse_qs, unquote, urlencode, urlsplit, urlunsplit

    from browser_tests.candidate_pages import goto_candidate, select_candidate_request
    from browser_tests.graph_fixtures import _projection, _rows, graph_catalogue_fixture
    from browser_tests.graph_pages import wait_graph_request_complete
    from ior_mvp.graph.service import GraphService

    page = browser_session.page
    detail, line = goto_candidate(page, STEEL, locale, role="REFERENCE_LINE")
    assert line is not None
    finding = next(row for row in line["findings"] if row["requirement_item_id"] == "qualified_volume")
    select_candidate_request(page, finding)
    link = page.locator('[data-selected-subject] a[href*="graphOpen=1"]')
    expect(link).to_have_count(1)
    href = link.get_attribute("href")
    assert href is not None
    parsed = urlsplit(href)
    query = parse_qs(parsed.query)
    expected_context = {
        "company_id": line["company_id"],
        "plant_id": line["plant_id"],
        "line_id": line["entity_id"],
        "requirement_item_id": finding["requirement_item_id"],
    }
    assert expected_context == {
        key: query[name][0]
        for name, key in (
            ("company", "company_id"), ("plant", "plant_id"),
            ("line", "line_id"), ("requirement", "requirement_item_id"),
        )
    }
    assert query["opportunity"] == [STEEL.id]
    assert query["mode"] == ["simulated"]
    assert query["locale"] == [locale.code]
    assert query["graphView"] == ["adjacency"]
    assert query["graphOpen"] == ["1"]
    assert detail["candidate_discovery"]["available"] is True

    projection = _projection()
    service = GraphService(
        SimpleNamespace(target="fixture"),
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {
            "projection_id": projection.projection_id,
            "counts": projection.counts,
            "synthetic_partition": {},
        },
        view_reader=lambda _spec, view, identity, branch, _scenario: _rows(
            view, identity, branch,
        ),
    )
    requests = []
    payloads = []
    first_view_error = opening == "error_retry"
    first_unavailable = opening == "unavailable_retry"

    def graph_route(route):
        nonlocal first_view_error, first_unavailable
        url = urlsplit(route.request.url)
        if url.path == "/api/graph/catalogue":
            requests.append(("catalogue", None))
            route.fulfill(json=graph_catalogue_fixture())
            return
        parts = url.path.split("/")
        assert parts[1:4] == ["api", "graph", "opportunities"] and parts[5] == "views"
        view = unquote(parts[6])
        params = parse_qs(url.query)
        context = {key: params.get(key, [None])[0] for key in expected_context}
        requests.append((view, context))
        if first_view_error:
            first_view_error = False
            route.fulfill(json={"view_id": view, "graph_status": "INVALID_TEST_PAYLOAD"})
            return
        payload = service.view(view, unquote(parts[4]), params["mode"][0], context)
        if first_unavailable:
            first_unavailable = False
            route.fulfill(json={**payload, "graph_status": "GRAPH_UNAVAILABLE",
                                "reason_code": "CONNECTION_FAILED", "nodes": [], "edges": []})
            return
        payloads.append(payload)
        route.fulfill(json=payload)

    page.route("**/api/graph/**", graph_route)
    if opening == "both_nondefault_held":
        page.add_init_script("""(() => {
          const original = window.fetch;
          let held = false;
          window.__heldGraphCatalogue = { pending: false, settled: false, release: null };
          window.fetch = (...args) => {
            if (!held && String(args[0]).includes('/api/graph/catalogue')) {
              held = true;
              return new Promise((resolve, reject) => {
                window.__heldGraphCatalogue.pending = true;
                window.__heldGraphCatalogue.release = () => original(...args).then(
                  response => { window.__heldGraphCatalogue.settled = true; resolve(response); }, reject,
                );
              });
            }
            return original(...args);
          };
        })();""")
    if opening == "view_only":
        query.pop("graphOpen")
    elif opening == "open_only":
        query.pop("graphView")
    elif opening == "both_nondefault_held":
        query["graphView"] = ["evidence_to_change"]
    requested_view = "evidence_to_change" if opening == "both_nondefault_held" else "adjacency"
    if opening in {"both", "error_retry", "unavailable_retry", "manual_reopen"}:
        link.click()
    else:
        page.goto(urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query, doseq=True), parsed.fragment)))
    if opening == "both_nondefault_held":
        page.wait_for_function("window.__heldGraphCatalogue?.pending === true")
        page.evaluate("window.__heldGraphCatalogue.release()")
        page.wait_for_function("window.__heldGraphCatalogue?.settled === true")
    if opening in {"error_retry", "unavailable_retry"}:
        expect(page.locator(".graph-state-error [data-graph-retry]")).to_be_visible()
        assert len([row for row in requests if row[0] == requested_view]) == 1
        page.locator("[data-graph-retry]").click()
        expect(page.locator(".graph-visual")).to_be_visible(timeout=5000)
    wait_graph_request_complete(page, requested_view)
    expect(page.locator("#graph-panel")).to_be_visible()
    expect(page.locator("#graph-view-select")).to_have_value(requested_view)
    focus = "LINE-SYN-MINISTRY-STEEL-001"
    native = page.locator(f'.graph-button-list [data-graph-select="node"][data-graph-id="{focus}"]')
    expect(native).to_have_count(1)
    expect(native).to_have_attribute("aria-pressed", "true")
    assert payloads and payloads[-1]["focus_element_id"] == focus
    assert payloads[-1]["context"] == expected_context
    focused = next(node for node in payloads[-1]["nodes"] if node["id"] == focus)
    assert focused["properties"]["canonical_entity_id"] == line["entity_id"]
    assert focused["properties"]["attribution_scope"] == "CANDIDATE_DISCOVERY"
    assert finding["requirement_item_id"] in focused["properties"]["finding_item_ids"]
    assert focused["provenance"]["synthetic_flag"] is True
    assert focused["provenance"]["evidence_class"] == "D"
    expect(page.locator(".graph-source-table")).to_contain_text(line["entity_id"])
    expect(page.locator(".graph-provenance")).to_contain_text(focused["provenance"]["evidence_id"])
    assert all(context == expected_context for view, context in requests if view != "catalogue")
    view_requests = [view for view, _context in requests if view != "catalogue"]
    assert view_requests == (["adjacency", "adjacency"] if opening in {"error_retry", "unavailable_retry"} else [requested_view])
    if opening == "both_nondefault_held":
        assert "adjacency" not in view_requests
        assert all(payload["view_id"] == requested_view for payload in payloads)
    if opening == "manual_reopen":
        page.locator("#graph-toggle").click()
        expect(page.locator("#graph-toggle")).to_have_attribute("aria-expanded", "false")
        expect(page.locator("#graph-panel")).to_be_hidden()
        page.locator("#graph-toggle").click()
        wait_graph_request_complete(page, "adjacency")
        assert [view for view, _context in requests if view != "catalogue"] == ["adjacency", "adjacency"]
    assert browser_session.collector.records == ()
