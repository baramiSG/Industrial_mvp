"""S19 source-equality and original-defect tests, independent of projection tables."""
from copy import deepcopy
from html import escape, unescape
from html.parser import HTMLParser
import json

import pytest

from ior_mvp.data_repository import public_cases, get_synthetic_scenario
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier, render_dossier_html

CASES = tuple(sorted(public_cases()))
SECTIONS = ('identity', 'demand', 'supply', 'gap', 'capability', 'economics',
            'competition', 'ledger', 'evidence', 'conditions', 'authority')

class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__(); self.tags=[]; self.text=[]; self.feed(markup)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def handle_data(self, data):
        self.text.append(data)

@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mode', ['public', 'simulated'])
def test_supply_is_named_structured_content_without_raw_dictionary(case, mode):
    analysis=analyze(case, mode)
    markup=render_dossier_html(build_dossier(analysis), 'ar')
    document=Document(markup)
    assert not any(tag=='code' and "source-language-island" in attrs.get('class','') for tag,attrs in document.tags), 'Original raw supply dictionary is not a document table'
    for producer in analysis['domestic_capability']['producer_evidence']:
        assert producer['producer'] in unescape(markup)
    assert any(tag=='table' and attrs.get('data-dossier-table')=='producers' for tag,attrs in document.tags)

@pytest.mark.parametrize('case', CASES)
def test_arabic_ledger_renders_localized_name_result_and_effect(case):
    analysis=analyze(case, 'simulated')
    text=''.join(Document(render_dossier_html(build_dossier(analysis),'ar')).text)
    for rule in analysis['rules']:
        for field in ['name','result','decision_effect']:
            assert rule['localized']['ar'][field]['text'] in text, (rule['rule_id'],field)

@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mode', ['public','simulated'])
def test_all_methodology_sections_exist_even_without_evidence(case,mode):
    document=Document(render_dossier_html(build_dossier(analyze(case,mode)),'en'))
    ids={attrs.get('id') for tag,attrs in document.tags if tag=='section'}
    assert {'dossier-'+section for section in SECTIONS} <= ids

@pytest.mark.parametrize('case',CASES)
def test_simulated_export_keeps_complete_visible_public_conclusion(case):
    analysis=analyze(case,'simulated');dossier=build_dossier(analysis)
    assert dossier.get('public_decision') == analysis['real_decision']
    for locale in ['en','ar']:
        text=''.join(Document(render_dossier_html(dossier,locale)).text)
        narrative=analysis['real_decision']['localized_narrative'][locale]
        for field in ['headline','rationale','route_label']:
            assert narrative[field]['text'] in text
        for field in ['conditions','kill_conditions','missing_facts']:
            for item in narrative[field]: assert item['text'] in text

@pytest.mark.parametrize('case',CASES)
@pytest.mark.parametrize('mode',['public','simulated'])
def test_projection_is_detached_and_preserves_decisions_routes_and_passports(case,mode):
    analysis=analyze(case,mode);before=deepcopy(analysis)
    scenario=get_synthetic_scenario(case);scenario_before=deepcopy(scenario)
    dossier=build_dossier(analysis)
    assert dossier['dossier_version']=='2.0.0'
    assert dossier['public_decision']==analysis['real_decision']
    assert dossier['blocks']['decision']['records']['active_decision']==analysis['active_decision']
    assert dossier['blocks']['capability']['records']['routes']==analysis['route_hypotheses']
    assert dossier['evidence_pack']['passports']==analysis['evidence']
    assert dossier['blocks']['supply']['records']['producers']==analysis['domestic_capability']['producer_evidence']
    for locale in ['en','ar']:render_dossier_html(dossier,locale)
    assert analysis==before and scenario==scenario_before
    dossier['public_decision']['headline']='mutation probe'
    dossier['supply_conclusion']['producer_evidence'].clear()
    assert analysis==before

@pytest.mark.parametrize('case',CASES)
def test_projection_has_no_internal_capability_score_in_html(case):
    analysis=analyze(case,'public')
    for locale in ['en','ar']:
        markup=render_dossier_html(build_dossier(analysis),locale)
        assert 'internal_d_star_before_gate' not in markup

@pytest.mark.parametrize('case',CASES)
def test_scalar_source_oracle_and_scenario_whitelist(case):
    analysis=analyze(case,'simulated'); scenario=get_synthetic_scenario(case)
    dossier=build_dossier(analysis)
    expected={
      'effective_qualified_capacity_kt': analysis['capacity'].get('effective_qualified_capacity_kt'),
      'target_spec_demand_kt': scenario['synthetic_inputs']['demand'].get('target_spec_demand_kt'),
      'known_weight_coverage': analysis['capability']['known_weight_coverage'],
      'd_star': analysis['capability']['d_star'],
      'minimum_effective_support_m': (analysis['economics'] or {}).get('minimum_effective_support_m'),
    }
    actual={f['key']:f for b in dossier['blocks'].values() for f in b['fields']}
    for key,value in expected.items():
        assert actual[key]['value']==value
        assert actual[key]['source_path']=={
            'effective_qualified_capacity_kt':'analysis.capacity.effective_qualified_capacity_kt',
            'target_spec_demand_kt':'scenario.synthetic_inputs.demand.target_spec_demand_kt',
            'known_weight_coverage':'analysis.capability.known_weight_coverage',
            'd_star':'analysis.capability.d_star',
            'minimum_effective_support_m':'analysis.economics.minimum_effective_support_m',
        }[key]
    inputs=dossier['evidence_pack']['scenario_inputs']
    assert 'class_if_confirmed' not in inputs
    assert 'evsi' not in inputs
    for key in ['target_specification','plant_line','demand','upgrade','economics']:
        if key in scenario['synthetic_inputs']:
            assert inputs[key]['data']==scenario['synthetic_inputs'][key]
            assert inputs[key]['evidence_ids']==[scenario['scenario_id']+'::'+key]
            assert inputs[key]['evidence_class']=='D'

@pytest.mark.parametrize('case',CASES)
@pytest.mark.parametrize('mode',['public','simulated'])
def test_explicit_record_source_oracle_covers_all_methodology_blocks(case,mode):
    analysis=analyze(case,mode);dossier=build_dossier(analysis);blocks=dossier['blocks']
    pairs=[
        (blocks['decision']['records']['active_decision'],analysis['active_decision']),
        (blocks['demand']['records']['trade'],analysis['trade']),
        (blocks['demand']['records']['trade_quality'],analysis['trade_quality']),
        (blocks['demand']['records']['domestic_flows'],analysis['domestic_flows']),
        (blocks['demand']['records']['supplier_metrics'],analysis['supplier_metrics']),
        (blocks['supply']['records']['producers'],analysis['domestic_capability']['producer_evidence']),
        (blocks['supply']['records']['coarse_adjacency_signals'],analysis['domestic_capability']['coarse_adjacency_signals']),
        (blocks['gap']['records']['hard_exclusions'],analysis['hard_exclusions']),
        (blocks['gap']['records']['rejection_conditions'],analysis['rejection_conditions']),
        (blocks['gap']['records']['advance_gate'],analysis['advance_gate']),
        (blocks['capability']['records']['dimensions'],analysis['capability']['dimensions']),
        (blocks['capability']['records']['public_routes'],analysis['real_decision']['route_hypotheses']),
        (blocks['economics']['records']['national_value'],(analysis['economics'] or {}).get('national_value')),
        (blocks['competition']['records']['assessment'],analysis['competition']),
        (blocks['ledger']['records']['rules'],analysis['rules']),
        (blocks['authority']['records']['integrity'],analysis['integrity']),
        (blocks['authority']['records']['authority'],analysis['authority']),
    ]
    for projected,original in pairs:assert projected==original
    ids={row['evidence_id'] for row in analysis['evidence']}
    for entry in dossier['evidence_pack']['scenario_inputs'].values():
        assert set(entry['evidence_ids'])<=ids
    assert {row['evidence_id'] for row in dossier['evidence_pack']['external_dependencies']}.isdisjoint(ids)


def test_all_literal_dossier_mappings_are_consumed_by_real_rendering(monkeypatch):
    import ior_mvp.dossier as module
    from ior_mvp.config import ui_strings_bundle
    calls=set();original=module.ui_text
    def observed(key,locale='en',**values):
        calls.add(key)
        return original(key,locale,**values)
    monkeypatch.setattr(module,'ui_text',observed)
    for case in CASES:
        for mode in ('public','simulated'):
            dossier=build_dossier(analyze(case,mode))
            for locale in ('en','ar'):
                markup=render_dossier_html(dossier,locale)
                strings=ui_strings_bundle(locale)['strings']
                for key in ('dossier.section.identity','dossier.section.demand','dossier.section.supply','dossier.section.gap','dossier.section.capability','dossier.section.economics','dossier.section.competition','dossier.section.ledger','dossier.section.evidence','dossier.section.conditions','dossier.section.authority','dossier.field.d_star','dossier.field.target_spec_demand_kt'):
                    assert strings[key] in unescape(markup)
    fixture=deepcopy(analyze('SAU-H0-390210','public'))
    fixture['domestic_capability']['producer_evidence']=[];fixture['evidence']=[]
    fixture['capacity']={'effective_qualified_capacity_kt':'NOT_APPLICABLE'}
    for state in ('PARTNER_DETAIL_MISSING','PARTNER_DETAIL_OBSERVED','PARTNER_TRADE_OBSERVED_ZERO'):
        fixture['partner_detail']={'state':state,'reason':'COVERAGE_INDETERMINATE','source_id':'SOURCE-FIXTURE','partner_snapshot_id':'PARTNER-FIXTURE','observed_partner_rows':0,'attempt_passport_ids':['ATTEMPT-FIXTURE'],'observed_passport_id':'OBSERVED-FIXTURE','unit_key':['390210','imports','2024']}
        for locale in ('en','ar'):render_dossier_html(build_dossier(fixture),locale)
    mapped=set(module.SECTION_LABELS.values())|set(module.FIELD_LABELS.values())|set(module.STATUS_LABELS.values())|set(module.AVAILABILITY_REASONS.values())
    assert mapped<=calls,sorted(mapped-calls)


def test_rendering_does_not_retrieve_scenario_context(monkeypatch):
    dossier=build_dossier(analyze('SAU-H0-721049','simulated'))
    from ior_mvp import data_repository
    def forbidden(*args):raise AssertionError('Rendering is pure')
    monkeypatch.setattr(data_repository,'get_synthetic_scenario',forbidden)
    for locale in ('en','ar'):assert render_dossier_html(dossier,locale)

@pytest.mark.parametrize('case',CASES)
def test_supply_section_keeps_complete_observed_producer_facts_and_signals(case):
    analysis=analyze(case,'public')
    for locale in ('en','ar'):
        html=render_dossier_html(build_dossier(analysis),locale)
        supply=html.split('<section id="dossier-supply"',1)[1].split('</section>',1)[0]
        text=''.join(Document(supply).text)
        for row in analysis['domestic_capability']['producer_evidence']:
            for key in ('public_note','portfolio','process_family','nameplate_source_evidence_id'):
                value=row.get(key)
                if isinstance(value,str) and value!='UNAVAILABLE':assert value in text,(case,key)
            coating=row.get('published_coating_range_g_m2')
            if isinstance(coating,list):
                for value in coating:assert format(value,'.12g') in text
        for signal in analysis['domestic_capability']['coarse_adjacency_signals']:
            assert signal['description'] in text

@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mode', ['public', 'simulated'])
def test_gap_appendix_retains_every_rejection_condition_and_reference(case, mode):
    from ior_mvp.config import ui_text
    analysis = analyze(case, mode)
    dossier = build_dossier(analysis)
    for locale in ('en', 'ar'):
        markup = render_dossier_html(dossier, locale)
        gap = markup.split('id="dossier-gap"', 1)[1].split('</section>', 1)[0]
        assert 'data-dossier-table="rejection-conditions"' in gap
        for row in analysis['rejection_conditions']:
            assert escape(row['code']) in gap
            assert escape(row['reason_code']) in gap
            status_key = ('dossier.availability.not_calculable' if row['status'] == 'NOT_CALCULABLE'
                          else 'executive.status.' + row['status'].lower())
            assert ui_text(status_key, locale) in unescape(gap)
            for evidence_id in row['evidence_ids']:
                assert 'href="#evidence-' + escape(evidence_id) + '"' in gap

@pytest.mark.parametrize('case', CASES)
def test_arabic_rule_metric_original_prose_is_visibly_attributed(case):
    import re
    from ior_mvp.config import ui_text
    analysis = analyze(case, 'simulated')
    rule = next(row for row in analysis['rules'] if row['rule_id'] == 'R12')
    markup = render_dossier_html(build_dossier(analysis), 'ar')
    articles = re.findall(r'<article class="rule-record">.*?</article>', markup, re.S)
    article = next(value for value in articles if '>R12</bdi>' in value)
    caption = ui_text('dossier.source_original', 'ar')
    assert caption in unescape(article)
    text = ''.join(Document(article).text)
    for key in ('name', 'result', 'decision_effect'):
        assert rule['localized']['ar'][key]['text'] in text
    originals = rule['metrics']['named_missing_facts'] + [row['route_effect'] for row in rule['metrics']['evidence_needs']]
    for value in originals:
        assert value in text
        assert text.index(caption) < text.index(value)
        assert '<span class="source-language-island" lang="en" dir="ltr">' + escape(value, quote=True) + '</span>' in article


@pytest.mark.parametrize('locale,expected', [('en', 'Description'), ('ar', 'الوصف')])
def test_observed_adjacency_description_has_no_planned_upgrade_meaning(locale, expected):
    from ior_mvp.config import ui_text
    dossier=build_dossier(analyze('SAU-H0-390210','public'))
    markup=render_dossier_html(dossier,locale)
    section=markup.split('id="dossier-supply"',1)[1].split('</section>',1)[0]
    assert ui_text('dossier.field.description',locale)==expected
    assert expected in ''.join(Document(section).text)
    for row in dossier['blocks']['supply']['records']['coarse_adjacency_signals']:
        assert row['description'] in ''.join(Document(section).text)


@pytest.mark.parametrize('site', ['identity','upgrade','adjacency','hard_gates','counterfactual','buyers','route_inputs','competition','contradiction','integrity'])
def test_original_source_prose_has_caption_in_its_actual_consumer(site):
    import re
    from ior_mvp.config import ui_text
    case={'counterfactual':'SAU-H6-721012','route_inputs':'SAU-H6-721012','buyers':'SAU-H6-760429','contradiction':'SAU-H0-721049'}.get(site,'SAU-H0-390210')
    mode='public' if site in ('adjacency','hard_gates','contradiction') else 'simulated'
    if site=='upgrade':case='SAU-H0-721049'
    dossier=build_dossier(analyze(case,mode));markup=render_dossier_html(dossier,'ar')
    block={'identity':'identity','upgrade':'supply','adjacency':'supply','hard_gates':'capability','counterfactual':'capability','buyers':'demand','route_inputs':'economics','competition':'competition','contradiction':'evidence','integrity':'authority'}[site]
    section=markup.split('id="dossier-'+block+'"',1)[1].split('</section>',1)[0]
    caption=ui_text('dossier.source_original','ar')
    if site in ('identity','upgrade'):
        keys=('application_boundary','name','application') if site=='identity' else ('description',)
        fields=[f for f in dossier['blocks'][block]['fields'] if f['key'] in keys and f['availability']=='AVAILABLE']
        assert fields
        for field in fields:
            row=next(row for row in re.findall(r'<tr>.*?</tr>',section,re.S) if escape(str(field['value']),quote=True) in row)
            text=''.join(Document(row).text)
            assert caption in text and text.index(caption)<text.index(str(field['value']))
        return
    heading={'adjacency':'dossier.coarse_adjacency_signals','counterfactual':'dossier.counterfactual','route_inputs':'dossier.cash_flows','contradiction':'dossier.public_contradictions','integrity':'dossier.evidence_boundary'}.get(site)
    if heading:section=section.split('<h3>'+ui_text(heading,'ar')+'</h3>',1)[1]
    if site=='adjacency':values=[r['description'] for r in dossier['blocks']['supply']['records']['coarse_adjacency_signals']]
    elif site=='hard_gates':
        section=section.split('</table>',2)[2].split('<article class="route-record">',1)[0]
        values=['named imported grade','buyer application and qualification']
    elif site=='counterfactual':values=[dossier['counterfactual']['q3_brownfield_versus_greenfield']['greenfield_alternative']]
    elif site=='buyers':
        section=section[section.rfind('<div class="branch-disclosure">'):]
        data=dossier['evidence_pack']['scenario_inputs']['buyer_allocation']['data'];values=[data['basis'],*[r['segment'] for r in data['buyers']]]
    elif site=='route_inputs':values=[r['basis'] for r in dossier['evidence_pack']['scenario_inputs']['route_evidence']['data'] if r.get('basis')]
    elif site=='competition':values=[dossier['blocks']['competition']['records']['assessment']['finding']]
    elif site=='contradiction':values=[r['contradiction'] for r in dossier['contradiction_register']['public']]
    else:values=[r['detail'] for r in dossier['evidence_summary']['integrity']['scenario_reconciliation']['checks'] if r.get('detail')]
    text=''.join(Document(section).text);assert values
    assert caption in text
    for value in values:
        assert value in text and text.index(caption)<text.index(value)
        assert 'class="source-language-island" lang="en" dir="ltr">'+escape(value,quote=True)+'</span>' in section


class IntroDocument(HTMLParser):
    """Capture only the bounded print units used by these actual consumers."""
    def __init__(self,markup):
        super().__init__();self.depth=0;self.current=None;self.intros=[];self.feed(markup)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='div':
            if attrs.get('class')=='dossier-intro':
                assert self.current is None
                self.current={'text':[],'rows':0};self.depth=0
            if self.current is not None:self.depth+=1
        if self.current is not None and tag=='tr':self.current['rows']+=1
    def handle_endtag(self,tag):
        if tag=='div' and self.current is not None:
            self.depth-=1
            if self.depth==0:self.intros.append(self.current);self.current=None
    def handle_data(self,text):
        if self.current is not None:self.current['text'].append(text)


@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mode', ['public','simulated'])
def test_print_introductions_contain_real_first_content_and_preserve_long_records(case,mode):
    from ior_mvp.config import ui_text
    dossier=build_dossier(analyze(case,mode))
    for locale in ('en','ar'):
        markup=render_dossier_html(dossier,locale);parsed=IntroDocument(markup)
        intros=[''.join(r['text']) for r in parsed.intros]
        assert intros
        for route in dossier['blocks']['capability']['records']['routes']:
            title=ui_text('executive.route.'+str(route['route_code']),locale)
            unit=next((r for r in parsed.intros if ''.join(r['text']).startswith(title)),None)
            assert unit is not None and unit['rows']==5  # header + four actual feasibility rows
            assert ui_text('dossier.field.policy_permissibility',locale) in ''.join(unit['text'])
        for rule in dossier['blocks']['ledger']['records']['rules']:
            local=rule['localized'][locale]
            assert any(local['name']['text'] in text and local['result']['text'] in text for text in intros)
        if mode=='simulated':
            first=next(r for r in dossier['blocks']['ledger']['records']['rules'] if r.get('synthetic_flag') is True)
            assert any(ui_text('dossier.simulated_ledger',locale) in text and first['localized'][locale]['result']['text'] in text for text in intros)
        assert any(ui_text('dossier.evidence_counts',locale,public=dossier['evidence_summary']['public_records'],synthetic=dossier['evidence_summary']['synthetic_records']) in text and ui_text('dossier.public_contradictions',locale) in text for text in intros)
        integrity=dossier['evidence_summary']['integrity'];assert next(iter(integrity.values())) is True
        assert any(ui_text('dossier.evidence_boundary',locale) in text and ui_text('dossier.field.real_decision_uses_public_only',locale) in text for text in intros)
        counter=dossier['counterfactual']
        if counter:assert isinstance(next(iter(counter.values())),bool)
        assert any(ui_text('dossier.counterfactual',locale) in text and (ui_text('dossier.field.q1_incumbent_meets_specification_without_capital',locale) if counter else ui_text('dossier.availability.unavailable',locale)) in text for text in intros)
        if dossier['evidence_summary'].get('selection'):
            authority=markup.split('id="dossier-authority"',1)[1]
            assert authority.index('class="selection-reference"')<authority.index(ui_text('dossier.evidence_boundary',locale))


@pytest.mark.parametrize('shape', ['list', 'null_q3'])
def test_counterfactual_optional_shapes_preserve_existing_json_and_html(shape, monkeypatch):
    import importlib
    from fastapi.testclient import TestClient
    analysis=deepcopy(analyze('SAU-H0-721049','simulated'))
    value=(['existing original value'] if shape=='list' else
           dict(analysis['simulation_decision']['counterfactual'],q3_brownfield_versus_greenfield=None))
    analysis['simulation_decision']['counterfactual']=value
    app_module=importlib.import_module('ior_mvp.app')
    monkeypatch.setattr(app_module,'_safe_analysis',lambda *args:deepcopy(analysis))
    client=TestClient(app_module.app,raise_server_exceptions=False)
    for locale in ('en','ar'):
        path='/api/opportunities/SAU-H0-721049/dossier'
        response=client.get(path+'?mode=simulated&locale='+locale)
        assert response.status_code==200
        assert response.json()['counterfactual']==value
        rendered=client.get(path+'.html?mode=simulated&locale='+locale)
        assert rendered.status_code==200
        if shape=='list':assert value[0] in ''.join(Document(rendered.text).text)
        else:
            from ior_mvp.config import ui_text
            section=rendered.text.split('id="dossier-capability"',1)[1].split('</section>',1)[0]
            assert ui_text('dossier.field.q3_brownfield_versus_greenfield',locale) in section
            assert ui_text('dossier.availability.unavailable',locale) in section


@pytest.mark.parametrize('case', CASES)
@pytest.mark.parametrize('mode', ['public','simulated'])
def test_authority_terminal_logical_record_keeps_complete_source_context(case,mode):
    from ior_mvp.config import ui_text
    dossier=build_dossier(analyze(case,mode));before=deepcopy(dossier)
    integrity=dossier['evidence_summary']['integrity']
    for locale in ('en','ar'):
        markup=render_dossier_html(dossier,locale)
        authority=markup.split('id="dossier-authority"',1)[1].split('</section>',1)[0]
        units=[''.join(row['text']) for row in IntroDocument(authority).intros]
        title=ui_text('dossier.evidence_boundary' if mode=='public' else 'dossier.field.ground_truth_backtest',locale)
        matches=[text for text in units if title in text]
        assert len(matches)==1, 'The complete terminal logical record must have one kept unit'
        complete=matches[0]
        keys=['executive.value.latest_imports_usd_m','dossier.field.latest_imports_kt']
        if mode=='public':
            keys+=['dossier.field.real_decision_uses_public_only','dossier.field.synthetic_isolation','dossier.field.scenario_reconciliation']
            assert ui_text('dossier.availability.unavailable',locale) in complete
        else:
            keys+=['dossier.field.real_decision_unchanged_after_simulation','dossier.field.expected','dossier.field.actual','dossier.field.match']
            assert ui_text('dossier.field.scenario_reconciliation',locale) not in complete
            for branch in ('expected','actual'):
                source=integrity['ground_truth_backtest'][branch]
                assert source['state'] in complete and str(source['route_code']) in complete
        for key in keys:assert ui_text(key,locale) in complete
        for key in ('latest_imports_usd_m','latest_imports_kt'):assert format(integrity[key],'.12g') in complete
        assert ui_text('dossier.boolean.true',locale) in complete
    assert dossier==before


class SummaryEvidence(HTMLParser):
    """Label and evidence-id groups inside the decision-summary section only."""

    def __init__(self, markup):
        super().__init__()
        self.groups=[]
        self._sections=[]
        self._group=None
        self._anchor=False
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='section':self._sections.append(attrs.get('id'))
        elif tag=='p' and 'decision-summary' in self._sections and 'summary-evidence' in attrs.get('class','').split():
            self._group={'label':'','ids':[]}
        elif tag=='a' and self._group is not None:
            self._anchor=True
            href=attrs.get('href','')
            if href.startswith('#evidence-'):self._group['ids'].append(href[len('#evidence-'):])

    def handle_endtag(self, tag):
        if tag=='section' and self._sections:self._sections.pop()
        elif tag=='a':self._anchor=False
        elif tag=='p' and self._group is not None:
            self.groups.append(self._group);self._group=None

    def handle_data(self, data):
        if self._group is not None and not self._anchor:self._group['label']+=data


def _public_summary_refs(dossier):
    return [row['evidence_id'] for row in dossier['evidence_pack']['passports'] if row.get('synthetic_flag') is False][:2]


def _public_contrary(dossier):
    return [row['evidence_id'] for row in dossier['contradiction_register']['public']]


@pytest.mark.parametrize('mode', ['public','simulated'])
@pytest.mark.parametrize('locale', ['en','ar'])
def test_summary_separates_supporting_and_public_contradiction_refs(mode, locale):
    from ior_mvp.config import ui_text
    analysis=analyze('SAU-H0-721049', mode)
    dossier=build_dossier(analysis)
    before=deepcopy(dossier)
    markup=render_dossier_html(dossier, locale)
    assert dossier==before
    assert dossier['public_decision']['state']==analysis['real_decision']['state']
    refs,contrary=_public_summary_refs(dossier),_public_contrary(dossier)
    assert contrary==['S-UNICOIL-SPEC'] and 'S-UNICOIL-SPEC' not in refs
    groups=SummaryEvidence(markup).groups
    assert [group['ids'] for group in groups]==[refs, contrary]
    assert ui_text('evidence.title', locale) in groups[0]['label']
    assert ui_text('dossier.public_contradictions', locale) in groups[1]['label']
    assert ui_text('dossier.no_public_contradictions', locale) not in ''.join(group['label'] for group in groups)
    synthetic=[row['evidence_id'] for row in dossier['evidence_pack']['passports'] if row.get('synthetic_flag') is True]
    assert not set(synthetic) & {item for group in groups for item in group['ids']}
    assert 'Published coating range differs from EPD and is retained for confirmation.' in markup


@pytest.mark.parametrize('mode', ['public','simulated'])
@pytest.mark.parametrize('locale', ['en','ar'])
def test_summary_omits_empty_public_contradiction_group(mode, locale):
    from ior_mvp.config import ui_text
    analysis=analyze('SAU-H0-390210', mode)
    dossier=build_dossier(analysis)
    before=deepcopy(dossier)
    markup=render_dossier_html(dossier, locale)
    assert dossier==before
    assert _public_contrary(dossier)==[]
    groups=SummaryEvidence(markup).groups
    assert [group['ids'] for group in groups]==[_public_summary_refs(dossier)]
    assert ui_text('evidence.title', locale) in groups[0]['label']
    assert ui_text('dossier.public_contradictions', locale) not in groups[0]['label']
    assert ui_text('dossier.no_public_contradictions', locale) not in groups[0]['label']
    assert ui_text('dossier.no_public_contradictions', locale) in markup


def test_summary_keeps_a_reference_that_is_both_supporting_and_contradictory():
    from ior_mvp.config import ui_text
    analysis=deepcopy(analyze('SAU-H0-721049', 'public'))
    target=next(row for row in analysis['evidence'] if row.get('synthetic_flag') is False)
    assert not row_contradiction(target)
    target['contradiction']='Dual-role probe retained for confirmation.'
    dossier=build_dossier(analysis)
    refs,contrary=_public_summary_refs(dossier),_public_contrary(dossier)
    assert target['evidence_id'] in refs and target['evidence_id'] in contrary
    for locale in ('en','ar'):
        markup=render_dossier_html(dossier, locale)
        groups=SummaryEvidence(markup).groups
        assert [group['ids'] for group in groups]==[refs, contrary]
        assert ui_text('evidence.title', locale) in groups[0]['label']
        assert ui_text('dossier.public_contradictions', locale) in groups[1]['label']
        assert 'Dual-role probe retained for confirmation.' in markup


def row_contradiction(row):
    return isinstance(row.get('contradiction'), str) and row['contradiction']
