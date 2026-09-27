"""Executive journey behavior against the existing API contracts."""

import pytest
from playwright.sync_api import expect

from browser_tests.executive_pages import STEPS, api_json, goto_executive, select_step
from browser_tests.harness import AR, CASES, DESKTOP, EN, LOCALES, POLYPROPYLENE, STEEL, TABLET


pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('case', (STEEL, POLYPROPYLENE), ids=lambda item: item.slug)
@pytest.mark.parametrize('locale', LOCALES, ids=lambda item: item.code)
@pytest.mark.parametrize('viewport', (DESKTOP, TABLET), ids=lambda item: item.name)
def test_public_q2_producer_units_and_missing_process(browser_session, case, locale, viewport):
    import json
    from browser_tests.pages import arabic_parity_report

    page = browser_session.page
    public = api_json(page, f'/api/opportunities/{case.id}?mode=public')
    strings = api_json(page, f'/api/ui-strings/{locale.code}')['strings']
    records = public['domestic_capability']['producer_evidence']
    goto_executive(page, case, locale, 'PUBLIC_CONCLUSION')
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute('data-state', case.real_state)
    expect(page.locator('[data-branch="SIMULATED"]')).to_have_count(0)
    expect(page.locator('[data-simulation-headline]')).to_have_count(0)
    section = page.locator('[data-active-step="PUBLIC_CONCLUSION"] .ministry-public-producers')
    cards = section.locator('article')
    expect(cards).to_have_count(len(records))
    for index, record in enumerate(records):
        card = cards.nth(index)
        expect(card.locator('h5')).to_contain_text(record['producer'])
        for evidence_id in record['evidence_ids']:
            expect(card.locator('.technical-token').filter(has_text=evidence_id)).to_have_count(1)
        capacity = record['installed_capacity_tpy']
        if isinstance(capacity, (int, float)):
            expect(card).to_contain_text(strings['dossier.field.installed_capacity_tpy'])
            expect(card.locator('.technical-token').filter(has_text=f'{capacity:,}')).to_have_count(1)
            assert strings['dossier.field.established_nameplate'] not in card.inner_text()
        else:
            assert strings['dossier.field.installed_capacity_tpy'] not in card.inner_text()
        process = record['process_route']
        if process == 'UNAVAILABLE':
            expect(card.locator('p').filter(has_text=strings['common.unavailable'])).to_have_count(1)
            expect(card.locator('.source-language-caption')).to_have_count(1 if locale.code == 'ar' else 0)
            assert 'UNAVAILABLE' not in card.inner_text()
        else:
            expect(card.locator('.source-language-island').filter(has_text=process)).to_have_count(1)
            expect(card.locator('.source-language-caption')).to_have_count(2 if locale.code == 'ar' else 0)
    if locale.code == 'ar':
        report = arabic_parity_report(page, '[data-executive-main]')
        assert all(report[key] == [] for key in ('island_failures', 'latin_prose_runs', 'latin_runs', 'label_leaks')), report
    stem = f'q2-{case.slug}-{locale.code}-{viewport.name}'
    page.screenshot(path=str(browser_session.artifact_dir / f'{stem}.png'), full_page=True,
                    animations='disabled', caret='hide')
    (browser_session.artifact_dir / f'{stem}.json').write_text(json.dumps({
        'case': case.id, 'locale': locale.code, 'viewport': viewport.name,
        'real_decision': public['real_decision']['state'],
        'producer_records': records, 'rendered_html': section.inner_html(),
        'capacity_label': strings['dossier.field.installed_capacity_tpy'],
        'unavailable_label': strings['common.unavailable'],
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def test_direct_executive_route_renders_arabic_eight_step_shell(browser_session):
    page = browser_session.page
    goto_executive(page, locale=AR)
    expect(page.locator("main[data-executive-main]")).to_have_count(1)
    assert page.locator("[data-executive-step]").evaluate_all(
        "nodes => nodes.map(node => node.dataset.executiveStep)"
    ) == list(STEPS)
    expect(page.locator("[data-analyst-link]")).to_have_attribute(
        "href", "/?opportunity=SAU-H0-721049&locale=ar",
    )
    expect(page.locator("[data-mode]")).to_have_count(0)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.slug)
@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_case_comparison_and_vectors_match_api(browser_session, case, locale):
    page = browser_session.page
    oracle = api_json(page, f"/api/executive/opportunities/{case.id}")
    goto_executive(page, case, locale)
    assert page.locator("[data-branch='PUBLIC']").count() == 1
    for branch in ("public",):
        card = page.locator(f'[data-branch="{branch.upper()}"]')
        decision = oracle["decisions"][branch]
        expect(card).to_have_attribute("data-state", decision["state"])
        expect(card).to_have_attribute("data-route", str(decision["route_code"]) if decision["route_code"] is not None else "NOT_CALCULABLE")
    expect(page.locator('[data-branch="SIMULATED"]')).to_have_count(0)
    assert page.locator("[data-vector]").evaluate_all("nodes => nodes.map(n => n.dataset.vector)") == [
        "MARKET_GAP", "STRATEGIC_RESILIENCE", "EXECUTION_FEASIBILITY", "EVIDENCE_CONFIDENCE",
    ]
    claims = {row["claim_id"]: row for row in oracle["claims"]}
    for vector in oracle["vectors"]:
        card = page.locator(f'[data-vector="{vector["vector_id"]}"]')
        assert card.locator("[data-claim-id]").evaluate_all("rows=>rows.map(row=>[row.dataset.claimId,row.dataset.claimStatus])") == [[identity, claims[identity]["status"]] for identity in vector["claim_ids"]]
        assert card.locator("[data-value]").evaluate_all("rows=>rows.map(row=>[row.dataset.value,row.dataset.availability])") == [[row["key"], row["availability"]] for row in vector["values"]]
    if case.id == STEEL.id and locale.code == "en":
        # Actual English value words may wrap between words, never within these short words.
        for width in (1440, 1024, 390):
            page.set_viewport_size({"width": width, "height": 1000})
            for summary in page.locator("[data-vector] > summary").all():
                if summary.locator("..").get_attribute("open") is None:
                    summary.focus(); page.keyboard.press("Enter")
            words = page.locator("[data-vector] dd").evaluate_all("""(nodes, words) => words.map(word => {
              const occurrences=[];
              for(const node of nodes){const walker=document.createTreeWalker(node,NodeFilter.SHOW_TEXT);
                while(walker.nextNode()){const text=walker.currentNode;const index=text.data.indexOf(word);if(index<0)continue;
                  const range=document.createRange();range.setStart(text,index);range.setEnd(text,index+word.length);
                  occurrences.push([...range.getClientRects()].filter(r=>r.width>0&&r.height>0).map(r=>({top:r.top,bottom:r.bottom})));}}
              return {word,occurrences};})""", ["Unavailable", "Resilience", "Not", "calculable"])
            for word in words:
                assert word["occurrences"], (width, word)
                assert all(len(lines) == 1 for lines in word["occurrences"]), (width, word)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    public = page.locator('[data-branch="PUBLIC"]')
    assert "DEMO_GENERATOR" not in public.inner_text()
    assert "SIMULATED" not in public.inner_text()
    select_step(page, "ROUTE_COMPARISON")
    simulated = page.locator('[data-branch="SIMULATED"]')
    decision = oracle["decisions"]["simulated"]
    expect(simulated).to_have_attribute("data-state", decision["state"])
    for label in decision["display_labels"].values():
        expect(page.locator('[data-active-step]')).to_contain_text(label)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_all_steps_keep_public_decision_and_nine_routes(browser_session, locale):
    page = browser_session.page
    goto_executive(page, STEEL, locale)
    for step in STEPS:
        select_step(page, step)
        expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")
        if step in ("SIMULATED_EVIDENCE", "ROUTE_COMPARISON", "INTERVENTION", "CONDITIONS_AND_KILL"):
            expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-state", "ADVANCE")
        else:
            expect(page.locator('[data-branch="SIMULATED"]')).to_have_count(0)
        assert page.locator('[data-active-step]').get_attribute("data-active-step") == step
        if step == "ROUTE_COMPARISON":
            assert page.locator("[data-route-row]").count() == 18
            for branch in ("PUBLIC", "SIMULATED"):
                assert page.locator(f'[data-route-branch="{branch}"] [data-route-row]').evaluate_all(
                    "nodes => nodes.map(n => Number(n.dataset.routeRow))"
                ) == list(range(9))
        if step in ("SIMULATED_EVIDENCE", "INTERVENTION", "CONDITIONS_AND_KILL"):
            expect(page.locator('[data-active-step]')).to_contain_text("SIMULATED — NOT MINISTRY EVIDENCE")
            expect(page.locator('[data-active-step]')).to_contain_text("محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة")


def test_polypropylene_zero_support_is_distinct_from_missing_npv(browser_session):
    page = browser_session.page
    goto_executive(page, POLYPROPYLENE, step="INTERVENTION")
    support = page.locator('[data-value="simulated_minimum_effective_support_m_sar"]')
    npv = page.locator('[data-value="simulated_unsupported_npv_m_sar"]')
    assert support.count() == npv.count() == 1
    expect(support).to_have_attribute("data-availability", "AVAILABLE")
    expect(support).to_contain_text("0")
    expect(npv).to_have_attribute("data-availability", "NOT_CALCULABLE")
    expect(npv).to_contain_text("Not calculable")


def test_unavailable_evsi_case_remains_unavailable(browser_session):
    page = browser_session.page
    goto_executive(page, CASES[7], step="INTERVENTION")
    assert page.locator("[data-case-evsi]").count() == 1
    expect(page.locator("[data-case-evsi]")).to_have_attribute("data-availability", "UNAVAILABLE")
    expect(page.locator("[data-case-evsi]")).to_contain_text("Unavailable")


@pytest.mark.parametrize("claim_id", ["metric.trade", "rule.R1-F", "rule.R4-F", "rule.R4-D", "decision.public", "decision.simulated", "metric.product_specification", "metric.supply_capability"])
@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_claim_drill_uses_exact_stored_evidence_and_restores_focus(browser_session, claim_id, locale):
    page = browser_session.page
    oracle = api_json(page, f"/api/executive/opportunities/{STEEL.id}")
    claim = next(row for row in oracle["claims"] if row["claim_id"] == claim_id)
    goto_executive(page, STEEL, locale)
    if claim_id == "decision.simulated":
        select_step(page, "ROUTE_COMPARISON")
    trigger = page.locator(f'[data-claim-id="{claim_id}"]').first
    assert trigger.count() == 1
    if not trigger.is_visible():
        summary = trigger.locator("xpath=ancestor::details[1]").locator(":scope > summary")
        summary.focus(); page.keyboard.press("Enter")
        expect(trigger).to_be_visible()
    if claim_id in {"metric.product_specification", "metric.supply_capability"}:
        assert claim["status"] == "CONTRADICTED"
        expect(trigger.locator("xpath=ancestor::details[1]")).to_have_attribute("data-vector", "EXECUTION_FEASIBILITY")
    trigger.click()
    panel = page.locator("[data-claim-evidence]")
    expect(panel).to_be_focused()
    assert panel.locator("[data-passport-id]").evaluate_all(
        "rows => rows.map(row => row.dataset.passportId)"
    ) == claim["evidence_ids"]
    expect(panel).to_have_attribute("data-claim-status", claim["status"])
    if claim_id == "decision.simulated":
        expect(panel).to_contain_text("Published coating range differs")
        expect(panel).to_contain_text("SIMULATED — NOT MINISTRY EVIDENCE")
        expect(panel).to_contain_text("محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة")
    else:
        assert "DEMO_GENERATOR" not in panel.inner_text()
    for link in panel.locator('[data-passport-ref]').all():
        identity = link.get_attribute('href')[1:]
        link.focus(); page.keyboard.press('Enter')
        expect(page.locator(f'[id="{identity}"]')).to_be_focused()
        if locale.code == 'ar':
            assert link.evaluate("a=>a.nextElementSibling.id===a.getAttribute('aria-describedby') && a.nextElementSibling.checkVisibility()")
    if locale.code == 'ar':
        from browser_tests.pages import arabic_parity_report
        report = arabic_parity_report(page, '[data-executive-main]')
        assert all(report[key] == [] for key in ('island_failures', 'latin_prose_runs', 'latin_runs', 'label_leaks')), report
    from browser_tests.harness import run_axe, format_axe_violations
    result = run_axe(page)
    assert result["violations"] == [], format_axe_violations(result["violations"])
    page.keyboard.press("Escape")
    expect(trigger).to_be_focused()
    expect(panel).to_have_count(0)


@pytest.mark.parametrize("locale", LOCALES, ids=lambda locale: locale.code)
def test_journey_exposes_trade_capacity_capability_and_step_navigation(browser_session, locale):
    page = browser_session.page
    analysis = api_json(page, f"/api/opportunities/{STEEL.id}?mode=simulated")
    goto_executive(page, locale=locale)
    assert page.locator("[data-active-step] svg[role='img']").count() == 1
    expect(page.locator("[data-executive-next]")).to_have_attribute("data-executive-go", "FALSE_POSITIVE_CONTROLS")
    page.locator("[data-executive-next]").click()
    expect(page.locator("[data-executive-back]")).to_have_attribute("data-executive-go", "SIGNAL")
    select_step(page, "SIMULATED_EVIDENCE")
    page.locator('[data-scenario-context] > summary').click()
    for key in ["effective_qualified_capacity_kt", "target_spec_demand_kt", "specification_adjusted_gap_kt"]:
        assert float(page.locator(f'[data-capacity-key="{key}"]').inner_text()) == analysis["capacity"][key]
    assert page.locator("[data-capability-dimension]").evaluate_all("rows => rows.map(r => r.dataset.capabilityDimension)") == [row["dimension"] for row in analysis["capability"]["dimensions"]]
    strings = api_json(page, f'/api/ui-strings/{locale.code}')['strings']
    distance = page.locator('[data-scenario-context] > h4').filter(has_text=strings['capability.title']).locator('xpath=following-sibling::p[1]')
    glyphs = distance.evaluate("""p=>{const w=document.createTreeWalker(p,NodeFilter.SHOW_TEXT);while(w.nextNode()){const n=w.currentNode,i=n.data.indexOf('D*');if(i>=0){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+1);const d=r.getBoundingClientRect();r.setStart(n,i+1);r.setEnd(n,i+2);const star=r.getBoundingClientRect();return {d:d.left,star:star.left,widths:[d.width,star.width]}}}throw Error('DISTANCE_LABEL_MISSING')}""")
    assert min(glyphs['widths']) > 0 and glyphs['d'] < glyphs['star'], glyphs
    legend = page.locator('[data-capability-legend]')
    expect(legend.locator('summary')).to_have_text(strings['executive.capability.legend'])
    legend.locator('summary').focus(); page.keyboard.press('Enter')
    expect(legend).to_have_attribute('open', '')
    for code in ('0', '1', '2', '3', 'U'):
        expect(legend.locator(f'[data-capability-legend-state="{code}"]')).to_have_text(strings['executive.capability.state.' + ('u' if code == 'U' else code)])
    expect(legend).to_contain_text(strings['executive.capability.simulation_note'])
    for row in analysis['capability']['dimensions']:
        code = str(row['state']) if row['known'] else 'U'
        rendered = page.locator(f'[data-capability-dimension="{row["dimension"]}"] [data-capability-state]')
        expect(rendered).to_have_attribute('data-capability-state', code)
        expect(rendered.locator('bdi')).to_have_text(code)
        expect(rendered).to_contain_text(strings['executive.capability.state.' + ('u' if code == 'U' else code)])
    labels = page.locator('[data-executive-full-provenance] .synthetic-labels')
    for value in analysis['simulation_scenario']['display_labels'].values():
        assert any(value in text for text in labels.all_text_contents())
    assert api_json(page, f'/api/opportunities/{STEEL.id}?mode=simulated') == analysis
    select_step(page, "INTERVENTION")
    expect(page.locator("[data-competition-ratio]")).to_contain_text("1.0751")


def test_route_economics_preserve_available_values_and_typed_absence(browser_session):
    page = browser_session.page
    analysis = api_json(page, f"/api/opportunities/{STEEL.id}?mode=simulated")
    goto_executive(page, step="ROUTE_COMPARISON")
    for row in analysis["simulation_decision"]["route_hypotheses"]:
        card = page.locator(f'[data-route-branch="SIMULATED"] [data-route-row="{row["route_code"]}"]')
        card.locator("summary").click()
        expected = {**row["economics"], "incremental_national_value_m_sar": row["incremental_national_value_m_sar"]}
        for key, value in expected.items():
            cell = card.locator(f'[data-route-value="{key}"]')
            expect(cell).to_have_count(1)
            if value == "NOT_CALCULABLE":
                expect(cell).to_have_attribute("data-availability", "NOT_CALCULABLE")
                expect(cell).to_have_text("Not calculable")
            else:
                expect(cell).to_have_attribute("data-availability", "AVAILABLE")
                displayed = cell.inner_text().replace(",", "").replace("%", "")
                assert float(displayed) == pytest.approx(value * 100 if key == "unsupported_irr" else value)


@pytest.mark.parametrize("case", (STEEL, POLYPROPYLENE), ids=lambda item: item.slug)
@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_executive_discovery_names_requirement_and_progressive_context(browser_session, case, locale):
    from browser_tests.candidate_pages import goto_candidate

    page = browser_session.page
    detail, _ = goto_candidate(page, case, locale, discovery=True)
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    requirement = detail["candidate_discovery"]["requirement"]
    strip = page.locator("[data-requirement-strip]")
    expect(strip).to_have_count(1)
    demand = requirement["target_demand_kt"]
    expect(strip).to_contain_text(str(int(demand) if int(demand) == demand else demand))
    expect(strip).to_contain_text(f'[{requirement["request_window_months"][0]},{requirement["request_window_months"][1]})')
    expect(strip).to_contain_text(strings["ministry.target_specification"])
    assert page.locator("[data-simulation-headline]").count() == 1
    assert page.locator("[data-executive-reference]").evaluate("node => node.open") is False
    assert page.locator("[data-scenario-context]").evaluate("node => node.open") is False
    assert page.locator("[data-company-count]").get_attribute("data-company-count") == "8"
    rows = detail["candidate_discovery"]["rows"]
    for row in (value for value in rows if value["entity_kind"] == "COMPANY"):
        card = page.locator(f'[data-company="{row["entity_id"]}"]')
        expect(card).to_contain_text(row["company_name_ar" if locale.code == "ar" else "company_name_en"])
        assert card.locator("[data-ministry-company]").inner_text() != row["entity_id"]
    expected_other = 5 if case.id == STEEL.id else 6
    assert page.locator("[data-other-results] [data-company]").count() == expected_other
    discovery = page.locator("[data-candidate-discovery]")
    assert discovery.evaluate("node => Boolean(node.compareDocumentPosition(document.querySelector('[data-scenario-context]')) & Node.DOCUMENT_POSITION_FOLLOWING)")
    assert detail["decisions"]["public"]["state"] == case.real_state


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_related_steel_company_explains_known_output_and_missing_process(browser_session, locale):
    from browser_tests.candidate_pages import goto_candidate

    page = browser_session.page
    detail, _ = goto_candidate(page, STEEL, locale, discovery=True)
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    plant = next(row for row in detail["candidate_discovery"]["rows"]
                 if row["entity_id"] == "PLANT-5bb27c71985d4b9d")
    assert plant["disposition"] == "RELATED_ONLY"
    assert plant["r9s"]["fired"] is False
    card = page.locator(f'[data-company="{plant["company_id"]}"]')
    expect(card).to_contain_text(strings["ministry.family.cold_rolled_sheet"])
    expect(card).to_contain_text(strings["ministry.related_recorded"])
    expect(card).to_contain_text("720916")
    expect(card).to_contain_text("80")
    expect(card).to_contain_text(strings["ministry.related_limit"])
    expect(card).to_contain_text(strings["ministry.related_next"])
    card.locator("h4 button").click()
    page.locator(f'button[data-ministry-plant="{plant["entity_id"]}"]:not([data-ministry-line])').click()
    expect(page.locator("[data-selected-subject]")).to_have_attribute("data-selected-subject", plant["entity_id"])


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_executive_simulation_context_is_data_scoped(browser_session, locale):
    page = browser_session.page
    goto_executive(page, STEEL, locale, "MISSING_MINISTRY_FACTS")
    expect(page.locator("[data-simulation-headline]")).to_have_count(0)
    expect(page.locator("[data-requirement-strip]")).to_have_count(0)
    select_step(page, "SIMULATED_EVIDENCE")
    expect(page.locator("[data-simulation-headline]")).to_have_count(1)
    full = page.locator("[data-executive-full-provenance]")
    expect(full).to_have_count(1)
    full.locator("summary").click()
    labels = api_json(page, f"/api/ui-strings/{locale.code}")["synthetic_labels"]
    for value in labels.values():
        expect(full).to_contain_text(value)
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")


def test_dynamic_ninth_operating_company_without_line_is_navigable(browser_session):
    from copy import deepcopy

    from ior_mvp.decision_engine import analyze
    from ior_mvp.executive.candidate_projection import build_candidate_diagnostics
    from ior_mvp.executive.service import build_executive_case
    from tests.test_candidate_discovery import ninth_company_fixture

    scenario, _register, discovery = ninth_company_fixture()
    simulated = deepcopy(analyze(STEEL.id, "simulated"))
    simulated["candidate_discovery"] = discovery
    candidates, lines = build_candidate_diagnostics(simulated, STEEL.id, scenario)
    detail = build_executive_case(STEEL.id).model_dump(mode="json")
    detail["candidate_discovery"] = candidates.model_dump(mode="json")
    detail["line_assessment"] = lines.model_dump(mode="json")
    page = browser_session.page
    page.route(f"**/api/executive/opportunities/{STEEL.id}",
               lambda route: route.fulfill(json=detail))
    page.route(f"**/api/opportunities/{STEEL.id}?mode=simulated",
               lambda route: route.fulfill(json=simulated))
    goto_executive(page, STEEL, EN, "SIMULATED_EVIDENCE")
    expect(page.locator("[data-company-count]")).to_have_attribute("data-company-count", "9")
    company = page.locator('[data-company="COMPANY-aaaaaaaaaaaaaaaa"]')
    expect(company).to_contain_text("Synthetic Ninth")
    company.locator("[data-ministry-company]").first.click()
    plant = company.locator('[data-ministry-plant="PLANT-bbbbbbbbbbbbbbbb"]')
    expect(plant).to_be_visible()
    plant.click()
    expect(page.locator("[data-selected-subject]")).to_have_attribute(
        "data-selected-subject", "PLANT-bbbbbbbbbbbbbbbb")
    expect(page.locator(".ministry-lines")).to_contain_text(
        api_json(page, "/api/ui-strings/en")["strings"]["ministry.no_line"])
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", "INVESTIGATE")


@pytest.mark.parametrize("locale", LOCALES, ids=lambda item: item.code)
def test_q5_reference_condition_links_to_standalone_warned_dossier(browser_session, locale):
    page = browser_session.page
    simulated = api_json(page, f"/api/opportunities/{STEEL.id}?mode=simulated")
    counterfactual = simulated["simulation_decision"]["counterfactual"][
        "q3_brownfield_versus_greenfield"]
    goto_executive(page, STEEL, locale, "CONDITIONS_AND_KILL")
    condition = page.locator("[data-reference-condition]")
    expect(condition).to_contain_text(str(round(counterfactual["incremental_capacity_kt"])))
    expect(condition).to_contain_text(str(round(counterfactual["schedule_months"])))
    dossier = page.locator('[data-active-step] a[href*="/dossier.html"]')
    expect(dossier).to_have_attribute("target", "_blank")
    expect(dossier).to_have_attribute("rel", "noopener noreferrer")
    with page.expect_popup() as popup_info:
        dossier.click()
    popup = popup_info.value
    popup.wait_for_load_state()
    expect(popup.locator(".warning strong[lang='en']")).to_be_visible()
    expect(popup.locator(".warning strong[lang='ar']")).to_be_visible()
    expect(popup.locator("body")).not_to_contain_text("candidate_discovery")
    expect(popup.locator("body")).not_to_contain_text("candidate_lines")
    popup.close()
