"""Execute the actual ES-module boundary against governed API responses."""

from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT

MODULES = PROJECT_ROOT / "src/ior_mvp/static/modules"


def _node(body: str, fixture: object) -> object:
    script = f"""
import {{ validateExecutiveContext }} from {json.dumps((MODULES / 'executive/data.js').as_uri())};
import {{ scalar }} from {json.dumps((MODULES / 'executive/summary.js').as_uri())};
import {{ evidenceAnchor }} from {json.dumps((MODULES / 'claim-links.js').as_uri())};
import {{ analystClaimContext }} from {json.dumps((MODULES / 'claim-links.js').as_uri())};
import {{ state }} from {json.dumps((MODULES / 'state.js').as_uri())};
const fixture = {json.dumps(fixture, ensure_ascii=False)};
{body}
"""
    result = subprocess.run(
        ["node", "--experimental-default-type=module", "--input-type=module"],
        input=script, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def contexts() -> list[dict]:
    client = TestClient(app)
    summary = client.get("/api/executive/summary").json()
    return [
        {
            "summary": summary,
            "executiveCase": client.get(f"/api/executive/opportunities/{row['opportunity_id']}").json(),
            "publicAnalysis": client.get(f"/api/opportunities/{row['opportunity_id']}?mode=public").json(),
            "simulatedAnalysis": client.get(f"/api/opportunities/{row['opportunity_id']}?mode=simulated").json(),
        }
        for row in summary["opportunities"]
    ]


def test_all_loaded_api_contexts_join_without_changing_public_decisions(contexts):
    result = _node("""
const before = JSON.stringify(fixture);
const ids = fixture.map(context => validateExecutiveContext(context).executiveCase.opportunity.opportunity_id);
const analyst = fixture.flatMap(context => ['publicAnalysis','simulatedAnalysis'].map(key => {
  const joined=analystClaimContext(context.executiveCase,context[key]);
  return joined?.executiveCase.opportunity.opportunity_id ?? null;
}));
console.log(JSON.stringify({ids, analyst, unchanged: before === JSON.stringify(fixture)}));
""", contexts)
    assert result["ids"] == [row["executiveCase"]["opportunity"]["opportunity_id"] for row in contexts]
    assert len(result["ids"]) == 11
    assert result["analyst"] == [identity for identity in result["ids"] for _ in range(2)]
    assert len(result["analyst"]) == 22
    assert result["unchanged"] is True


@pytest.mark.parametrize("mutation", [
    "public-claim-metadata", "synthetic-labels", "foreign-reference", "duplicate-claim", "step-order", "scenario", "missing-evsi", "wrong-evsi",
])
def test_join_rejects_branch_laundering_and_foreign_or_malformed_context(contexts, mutation):
    context = deepcopy(contexts[0])
    detail = context["executiveCase"]
    if mutation == "public-claim-metadata":
        detail["claims"][0]["source"] = "DEMO_GENERATOR"
    elif mutation == "synthetic-labels":
        detail["decisions"]["simulated"]["display_labels"]["ar"] = "fabricated boundary"
    elif mutation == "foreign-reference":
        detail["claims"][0]["evidence_ids"] = ["FOREIGN"]
    elif mutation == "duplicate-claim":
        detail["claims"].append(deepcopy(detail["claims"][0]))
    elif mutation == "step-order":
        detail["steps"].reverse()
    elif mutation == "missing-evsi":
        context["summary"]["synthetic_evsi"]["cases"] = [row for row in context["summary"]["synthetic_evsi"]["cases"] if row["opportunity_id"] != detail["opportunity"]["opportunity_id"]]
    elif mutation == "wrong-evsi":
        next(row for row in context["summary"]["synthetic_evsi"]["cases"] if row["opportunity_id"] == detail["opportunity"]["opportunity_id"])["scenario_id"] = "FOREIGN"
    else:
        context["simulatedAnalysis"]["simulation_scenario"]["scenario_id"] = "FOREIGN"
    assert _node("""
let rejected = false;
try { validateExecutiveContext(fixture); } catch (error) { rejected = error.message === 'EXECUTIVE_CONTEXT_MISMATCH'; }
console.log(JSON.stringify(rejected));
""", context) is True


def test_zero_and_unavailable_scalar_render_differently_in_both_locales():
    client = TestClient(app)
    bundles = [client.get(f"/api/ui-strings/{locale}").json() for locale in ["en", "ar"]]
    result = _node("""
console.log(JSON.stringify(fixture.map(bundle => {
  state.ui = bundle; state.locale = bundle.locale;
  return [scalar({availability:'AVAILABLE', value:0}), scalar({availability:'NOT_CALCULABLE', value:null}), scalar({availability:'UNAVAILABLE', value:null})];
})));
""", bundles)
    for row, bundle in zip(result, bundles, strict=True):
        assert ">0</bdi>" in row[0]
        assert row[1] == bundle["strings"]["executive.status.not_calculable"]
        assert row[2] == bundle["strings"]["executive.status.unavailable"]


def test_evidence_anchor_preserves_segment_boundaries_and_literal_encodings():
    inputs = [
        ["PUBLIC", "A-B", "C"], ["PUBLIC", "A", "B-C"],
        ["PUBLIC", "A%20B", "C"], ["PUBLIC", "A B", "C"],
        ["SIMULATED", "A", "B-C"], ["PUBLIC", "A", "<script>"],
    ]
    result = _node("console.log(JSON.stringify(fixture.map(row => evidenceAnchor(...row))));", inputs)
    assert len(set(result)) == len(inputs)
    assert all("<" not in value and '"' not in value for value in result)


def test_only_declared_mixed_case_claim_identifiers_extend_parity_grammar():
    from browser_tests.parity_grammar import classify_island

    for value in ["rule.R4-F", "rule.R4-D", "step.SIGNAL", "step.SIMULATED_EVIDENCE", "step.INTERVENTION", "step.INTERVENTION.simulated"]:
        assert classify_island(value) == "executive_claim_id"
    for value in ["rule.ADMIN", "step.UNREVIEWED", "step.INTERVENTION.other", "step.SIMULATED_EVIDENCE.other", "rule.R4", "Arbitrary English Words", "Hadeed", "Universal Metal Coating Company"]:
        assert classify_island(value) == "unclassified"


def test_shared_passport_uses_exact_status_taxonomy_and_source_code_allowlist(contexts):
    from ior_mvp.config import ui_strings_bundle
    import re

    statuses = ["observed", "calculated", "model_estimated", "inferred", "assumption", "unresolved", "synthetic"]
    codes = ["DEMO_GENERATOR", "producer_altaiseer_talco", "producer_alupco", "wco_hs_nomenclature"]
    names = ["Hadeed", "SABIC", "UNICOIL", "UNComtrade", "Universal Metal Coating Company"]
    bundle = ui_strings_bundle('ar')
    result = _node(f"""
const {{renderEvidenceResult}} = await import({json.dumps((MODULES / 'graph/passports.js').as_uri())});
state.locale='ar'; state.ui=fixture.bundle;
const original=JSON.stringify(fixture.record);
const render=record=>renderEvidenceResult({{records:[{{opportunityId:'SAU-H0-721049',record}}],unresolved:[],documentAddresses:[]}},'public');
console.log(JSON.stringify({{statuses:fixture.statuses.map(status=>render({{...fixture.record,status}})),sources:fixture.sources.map(source=>render({{...fixture.record,source}})),unchanged:JSON.stringify(fixture.record)===original}}));
""", {'record': contexts[0]['publicAnalysis']['evidence'][0], 'bundle': bundle, 'statuses': statuses, 'sources': codes + names})
    assert result['unchanged'] is True
    for status, output in zip(statuses, result['statuses'], strict=True):
        assert f'<span data-passport-value="status">{bundle["strings"]["graph.status." + status]}</span>' in output
    for source, output in zip(codes + names, result['sources'], strict=True):
        value = re.search(r'<span data-passport-value="source">(.*?)</dd>', output).group(1)
        assert source in value
        if source in codes:
            assert re.search(r'<bdi class="[^"]*\btechnical-token\b[^"]*" dir="ltr">' + re.escape(source) + '</bdi>', value)
        else:
            assert 'source-language-island' in value and 'source-language-caption' in value
            assert 'technical-token' not in value


@pytest.mark.parametrize('locale', ('en', 'ar'))
def test_capability_legend_preserves_all_states_unknown_and_simulation_boundary(contexts, locale):
    from ior_mvp.config import ui_strings_bundle
    import html
    import re

    context = deepcopy(next(row for row in contexts if row['executiveCase']['opportunity']['opportunity_id'] == 'SAU-H0-721049'))
    rows = context['simulatedAnalysis']['capability']['dimensions'][:5]
    for row, value in zip(rows, [0, 1, 2, 3, None], strict=True):
        row.update(state=value, known=value is not None)
    context['simulatedAnalysis']['capability']['dimensions'] = rows
    bundle = ui_strings_bundle(locale)
    result = _node(f"""
const {{renderSimulationStep}}=await import({json.dumps((MODULES / 'executive/simulation.js').as_uri())});
state.locale=fixture.bundle.locale;state.ui=fixture.bundle;
const before=JSON.stringify(fixture.context);
const output=renderSimulationStep({{step_id:'SIMULATED_EVIDENCE'}},fixture.context);
console.log(JSON.stringify({{output,unchanged:JSON.stringify(fixture.context)===before}}));
""", {'context': context, 'bundle': bundle})
    output = result['output']; assert result['unchanged'] is True
    assert '<details data-capability-legend>' in output
    assert f'<summary>{html.escape(bundle["strings"]["executive.capability.legend"])}</summary>' in output
    for code in ['0', '1', '2', '3', 'U']:
        meaning = bundle['strings']['executive.capability.state.' + ('u' if code == 'U' else code)]
        assert output.count(html.escape(meaning)) == 2  # one legend and one original dimension
    for row, code in zip(rows, ['0', '1', '2', '3', 'U'], strict=True):
        match = re.search(r'data-capability-dimension="' + row['dimension'] + r'".*?</div>', output).group(0)
        assert f'data-capability-state="{code}"' in match and f'>{code}</bdi>' in match
        if code == 'U':
            assert bundle['strings']['executive.status.unavailable'] in match
            assert '>0</bdi>' not in match
    assert html.escape(bundle['strings']['executive.capability.simulation_note']) in output
    for policy in context['executiveCase']['decisions']['simulated']['display_labels'].values():
        assert policy in output and output.index(policy) < output.index('data-capability-legend')


@pytest.mark.parametrize('locale', ('en', 'ar'))
@pytest.mark.parametrize('status', ('FAIL', 'PASS', 'UNAVAILABLE'))
def test_executive_integrity_notice_preserves_computed_checks_and_states(contexts, locale, status):
    import html
    import re
    from ior_mvp.config import ui_strings_bundle
    from ior_mvp.executive.models import ExecutiveSummary

    context = deepcopy(contexts[0])
    if status == 'FAIL':
        context['summary']['integrity'].update(status='FAIL', violation_count=27)
        check = next(row for row in context['summary']['integrity']['checks'] if row['check_id'] == 'REAL_DECISION_EQUALITY')
        check.update(status='FAIL', violation_count=27, affected_ids=['SAU-H0-721049'])
    ExecutiveSummary.model_validate(context['summary'])
    bundle = ui_strings_bundle(locale)
    result = _node(f"""
const render = await import({json.dumps((MODULES / 'executive/render.js').as_uri())});
const {{executive}} = await import({json.dumps((MODULES / 'executive/context.js').as_uri())});
const nodes={{}};const node=id=>nodes[id]??=({{innerHTML:'',setAttribute(){{}}}});
globalThis.document={{getElementById:node,querySelector:node}};
state.ui=fixture.bundle;state.locale=fixture.bundle.locale;
const before=JSON.stringify(fixture.context);
executive.context=validateExecutiveContext(fixture.context);
executive.selection={{opportunityId:'SAU-H0-721049',stepId:'INTERVENTION',locale:state.locale}};
render.renderJourney();const comparison=node('executive-comparison').innerHTML;
if(fixture.status==='UNAVAILABLE') render.renderIntegrity?.(null);
console.log(JSON.stringify({{notice:node('executive-integrity').innerHTML,comparison,unchanged:before===JSON.stringify(fixture.context)}}));
""", {'context': context, 'bundle': bundle, 'status': status})
    output = result['notice']
    assert f'data-executive-integrity="{status}"' in output  # original omission must fail first
    assert result['unchanged'] is True
    assert 'data-state="INVESTIGATE" data-route="NOT_CALCULABLE"' in result['comparison']
    assert 'data-state="ADVANCE" data-route="5"' in result['comparison']
    assert html.escape(bundle['strings']['executive.ui.integrity']) in output
    if status == 'UNAVAILABLE':
        assert html.escape(bundle['strings']['executive.status.unavailable']) in output
        assert 'data-integrity-count' not in output and 'data-integrity-check' not in output
    else:
        assert re.search(r'data-integrity-count><bdi[^>]*>' + ("27" if status == "FAIL" else "0") + r'</bdi></span>', output)
        assert ('role="alert"' in output) is (status == 'FAIL')
        if status == 'FAIL':
            ids = ['PUBLIC_SYNTHETIC_LEAKAGE', 'REAL_DECISION_EQUALITY', 'SYNTHETIC_METADATA', 'SCENARIO_VALIDATION']
            assert re.findall(r'data-integrity-check="([^"]+)"', output) == ids
            for check in context['summary']['integrity']['checks']:
                row = re.search(r'data-integrity-check="' + check['check_id'] + r'".*?</li>', output).group(0)
                assert html.escape(bundle['strings']['executive.integrity.' + check['check_id'].lower()]) in row
                assert html.escape(bundle['strings']['executive.status.' + check['status'].lower()]) in row
                assert f'>{check["violation_count"]}</bdi>' in row
                for identity in check['affected_ids']:
                    assert f'>{identity}</bdi>' in row


@pytest.mark.parametrize('mode', ('public', 'simulated'))
@pytest.mark.parametrize('mutation', ('public-state', 'public-route', 'pp-route', 'active-state', 'active-route', 'simulation-state', 'simulation-route', 'foreign-scenario', 'missing-scenario', 'unavailable-simulation', 'policy'))
def test_analyst_decision_join_rejects_conflicting_projection(contexts, mode, mutation):
    from ior_mvp.executive.models import ExecutiveCase

    context = deepcopy(next(row for row in contexts if row['executiveCase']['opportunity']['opportunity_id'] == ('SAU-H0-390210' if mutation == 'pp-route' else 'SAU-H0-721049')))
    detail = context['executiveCase']; analysis = context['publicAnalysis' if mode == 'public' else 'simulatedAnalysis']
    if mutation == 'public-state':
        detail['decisions']['public']['state'] = 'ADVANCE'
    elif mutation in ('public-route', 'pp-route'):
        detail['decisions']['public']['route_code'] = None if mutation == 'pp-route' else 0
    elif mutation.startswith('active-'):
        analysis['active_decision']['state' if mutation == 'active-state' else 'route_code'] = 'REJECT' if mutation == 'active-state' else 8
    elif mutation.startswith('simulation-'):
        detail['decisions']['simulated']['state' if mutation == 'simulation-state' else 'route_code'] = 'REJECT' if mutation == 'simulation-state' else 8
    elif mutation in ('foreign-scenario', 'missing-scenario'):
        if mode == 'simulated':
            analysis['simulation_scenario'] = None if mutation == 'missing-scenario' else {**analysis['simulation_scenario'], 'scenario_id': 'FOREIGN'}
        else:
            analysis['simulation_scenario'] = context['simulatedAnalysis']['simulation_scenario']
    elif mutation == 'unavailable-simulation':
        # Defensive transport-boundary variant; complete model-valid absent branch is tested separately.
        detail['decisions']['simulated']['availability'] = 'UNAVAILABLE'
    else:
        detail['decisions']['simulated']['display_labels']['ar'] = 'غير مطابق'
    if mutation in ('public-state', 'public-route', 'pp-route'):
        ExecutiveCase.model_validate(detail)
    expected = mode == 'public' and mutation in ('simulation-state', 'simulation-route', 'unavailable-simulation', 'policy')
    result = _node("""
const before=JSON.stringify(fixture);const joined=analystClaimContext(fixture.detail,fixture.analysis);
console.log(JSON.stringify({accepted:joined!==null,unchanged:before===JSON.stringify(fixture),claims:joined?[...joined.claims.keys()]:[]}));
""", {'detail': detail, 'analysis': analysis})
    assert result['accepted'] is expected
    assert result['unchanged'] is True
    if expected:
        assert 'decision.simulated' not in result['claims']


@pytest.mark.parametrize('locale', ('en', 'ar'))
def test_screening_reviewer_status_uses_governed_copy_and_preserves_records(locale):
    import html
    import re
    from browser_tests.parity_grammar import classify_island, label_leaks
    from ior_mvp.config import ui_strings_bundle

    assert PROJECT_ROOT == Path(__file__).resolve().parents[1]
    evidence = TestClient(app).get('/api/screening/evidence').json()
    bundle = ui_strings_bundle(locale)
    result = _node(f"""
const {{renderScreeningEvidence}}=await import({json.dumps((MODULES / 'screening/evidence.js').as_uri())});
state.ui=fixture.bundle;state.locale=fixture.bundle.locale;
const before=JSON.stringify(fixture.evidence);const output=renderScreeningEvidence(fixture.evidence);
const hostile=structuredClone(fixture.evidence);hostile.evidence_passports[0].status='\"<script>alert(1)</script>';
hostile.evidence_passports[0].passport_id='\" onmouseover=\"alert(1)';
console.log(JSON.stringify({{output,hostile:renderScreeningEvidence(hostile),unchanged:before===JSON.stringify(fixture.evidence)}}));
""", {'evidence': evidence, 'bundle': bundle})
    raw = 'unconfirmed_by_responsible_authority'
    assert len(evidence['evidence_passports']) == 8
    assert all(row['status'] == raw for row in evidence['evidence_passports'])
    statuses = re.findall(r'data-screening-reviewer-status="([^"]*)">(.*?)</span>', result['output'])
    assert statuses == [(raw, html.escape(bundle['strings']['graph.reviewer.' + raw]))] * 8
    assert f'>{raw}</bdi>' not in result['output']
    islands = [{'text': html.unescape(re.sub('<[^>]+>', '', text)), 'class': classify_island(html.unescape(re.sub('<[^>]+>', '', text)))} for text in re.findall(r'<bdi[^>]*>(.*?)</bdi>', result['output'])]
    assert label_leaks(islands, ui_strings_bundle('en')['strings'].values()) == []
    for passport in evidence['evidence_passports']:
        assert 'id="passport-' + html.escape(passport['passport_id'], quote=True) + '"' in result['output']
        assert passport['source_id'] in result['output']
    assert result['unchanged'] is True
    assert '<script>' not in result['hostile'] and 'id="passport-" onmouseover=' not in result['hostile']
    assert '&lt;script&gt;' in result['hostile'] and '&quot; onmouseover=' in result['hostile']


@pytest.mark.parametrize('locale', ('en', 'ar'))
def test_vectors_expose_exact_ordered_api_claims_and_statuses(contexts, locale):
    import re
    from ior_mvp.config import ui_strings_bundle

    result = _node(f"""
const {{renderVectors}}=await import({json.dumps((MODULES / 'executive/summary.js').as_uri())});
state.ui=fixture.bundle;state.locale=fixture.bundle.locale;const before=JSON.stringify(fixture.contexts);
const output=fixture.contexts.map(context=>renderVectors(validateExecutiveContext(context)));
console.log(JSON.stringify({{output,unchanged:before===JSON.stringify(fixture.contexts)}}));
""", {'contexts': contexts, 'bundle': ui_strings_bundle(locale)})
    assert len(result['output']) == 11 and result['unchanged'] is True
    for context, output in zip(contexts, result['output'], strict=True):
        claims = {row['claim_id']: row for row in context['executiveCase']['claims']}
        for vector in context['executiveCase']['vectors']:
            markup = re.search(r'<details data-vector="' + vector['vector_id'] + r'".*?</details>', output).group(0)
            actual = re.findall(r'data-claim-id="([^"]+)" data-claim-status="([^"]+)"', markup)
            assert actual == [(identity, claims[identity]['status']) for identity in vector['claim_ids']]
            for value in vector['values']:
                assert f'data-value="{value["key"]}" data-availability="{value["availability"]}"' in markup


def _absent_simulation_context(monkeypatch):
    from ior_mvp.executive import service
    from ior_mvp.executive.models import ExecutiveCase, ExecutiveSummary

    scenarios = dict(service.synthetic_scenarios())
    scenarios.pop('SAU-H0-721049')
    with monkeypatch.context() as patch:
        patch.setattr(service, 'synthetic_scenarios', lambda: scenarios)
        service.clear_executive_caches()
        try:
            detail = service.build_executive_case('SAU-H0-721049').model_dump(mode='json')
            summary = service.build_executive_summary().model_dump(mode='json')
        finally:
            service.clear_executive_caches()
    ExecutiveCase.model_validate(detail)
    ExecutiveSummary.model_validate(summary)
    assert len(summary['opportunities']) == 11
    assert len(summary['synthetic_evsi']['cases']) == 10
    assert all(row['opportunity_id'] != 'SAU-H0-721049' for row in summary['synthetic_evsi']['cases'])
    return {'executiveCase': detail, 'summary': summary, 'publicAnalysis': service.analyze('SAU-H0-721049', 'public'), 'simulatedAnalysis': None}


@pytest.mark.parametrize('locale', ('en', 'ar'))
def test_absent_simulation_retains_public_context_without_invented_evsi(monkeypatch, locale):
    import html
    from ior_mvp.config import ui_strings_bundle

    context = _absent_simulation_context(monkeypatch)
    result = _node(f"""
const render=await import({json.dumps((MODULES/'executive/render.js').as_uri())});
const {{executive}}=await import({json.dumps((MODULES/'executive/context.js').as_uri())});
const nodes={{}};const node=id=>nodes[id]??=({{innerHTML:'',setAttribute(){{}}}});
globalThis.document={{getElementById:node,querySelector:node}};
state.ui=fixture.bundle;state.locale=fixture.bundle.locale;const before=JSON.stringify(fixture.context);
let joined,error=null;try{{joined=validateExecutiveContext(fixture.context)}}catch(e){{error=e.message}}
const outputs=[];
if(joined){{executive.context=joined;for(const step of fixture.context.executiveCase.steps.filter(row=>row.step_id==='INTERVENTION')){{executive.selection={{stepId:step.step_id,opportunityId:'SAU-H0-721049'}};render.renderJourney();outputs.push(node('executive-comparison').innerHTML+node('executive-body').innerHTML)}}}}
const analyst=analystClaimContext(fixture.context.executiveCase,fixture.context.publicAnalysis);
console.log(JSON.stringify({{accepted:!!joined,error,evsi:joined?.evsi??null,outputs,analyst:!!analyst,claims:analyst?[...analyst.claims.keys()]:[],unchanged:before===JSON.stringify(fixture.context)}}));
""", {'context': context, 'bundle': ui_strings_bundle(locale)})
    assert result['accepted'] is True, result['error']  # genuine original absence must fail first
    assert result['evsi'] is None and result['unchanged'] is True
    assert result['analyst'] is True and 'decision.public' in result['claims'] and 'decision.simulated' not in result['claims']
    # The lightweight sink renders INTERVENTION; actual browser regression traverses all eight steps.
    assert len(result['outputs']) == 1
    for output in result['outputs']:
        assert 'data-state="INVESTIGATE" data-route="NOT_CALCULABLE"' in output
        assert 'data-branch="SIMULATED" data-state="UNAVAILABLE"' in output
        assert html.escape(ui_strings_bundle(locale)['strings']['executive.ui.no_simulation']) in output
        assert 'data-case-evsi' not in output and 'synthetic-labels' not in output
        assert 'DEMO_GENERATOR' not in output and '>null</bdi>' not in output


@pytest.mark.parametrize('mutation', ('synthetic_flag', 'scenario_id', 'evidence_class', 'source', 'display_labels', 'simulated-analysis', 'forged-evsi'))
def test_absent_simulation_rejects_forged_metadata_or_evsi(monkeypatch, contexts, mutation):
    context = _absent_simulation_context(monkeypatch)
    canonical = contexts[0]
    if mutation == 'simulated-analysis':
        context['simulatedAnalysis'] = canonical['simulatedAnalysis']
    elif mutation == 'forged-evsi':
        context['summary']['synthetic_evsi']['cases'].append(next(row for row in canonical['summary']['synthetic_evsi']['cases'] if row['opportunity_id'] == 'SAU-H0-721049'))
    else:
        context['executiveCase']['decisions']['simulated'][mutation] = canonical['executiveCase']['decisions']['simulated'][mutation]
    assert _node("""
const before=JSON.stringify(fixture);let rejected=false;
try{validateExecutiveContext(fixture)}catch(error){rejected=error.message==='EXECUTIVE_CONTEXT_MISMATCH'}
console.log(JSON.stringify(rejected&&before===JSON.stringify(fixture)));
""", context) is True
