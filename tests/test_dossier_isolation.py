from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from ior_mvp.app import app
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier,render_dossier_html
from ior_mvp import data_repository

@pytest.mark.parametrize('mode',['public','simulated'])
def test_public_decision_is_never_changed_by_export(mode):
    analysis=analyze('SAU-H0-721049',mode); before=deepcopy(analysis)
    dossier=build_dossier(analysis)
    assert dossier.get('public_decision')==before['real_decision']
    for locale in ['en','ar']:render_dossier_html(dossier,locale)
    assert analysis==before

def test_public_projection_never_loads_scenario_context(monkeypatch):
    analysis=analyze('SAU-H0-721049','public')
    def forbidden(*args):raise AssertionError('Public dossier must not retrieve synthetic context')
    monkeypatch.setattr(data_repository,'get_synthetic_scenario',forbidden)
    dossier=build_dossier(analysis)
    assert dossier.get('evidence_pack',{}).get('scenario_inputs')=={}
    assert dossier['synthetic_disclosure'] is None
    for block in dossier['blocks'].values():
        for field in block['fields']:
            assert not (field['source_path'] or '').startswith('scenario.')
            if field['key'] in ('base_demand_kt','target_spec_demand_kt','buyers','buyer_concentration','demand_timing'):
                assert field['source_path'] is None
    for locale in ['en','ar']:
        assert 'scenario.synthetic_inputs' not in render_dossier_html(dossier,locale)

@pytest.mark.parametrize(('field','value'),[
 ('scenario_id','WRONG'),('opportunity_id','SAU-H0-390210'),('scenario_version','999'),
 ('source','MINISTRY'),('evidence_class','A'),('synthetic_flag',False),('display_label','official'),
])
@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_mismatched_scenario_context_has_typed_422(monkeypatch,field,value,suffix):
    import ior_mvp.app as app_module
    # Use the real precomputed analysis while corrupting only export context.
    import importlib
    app_module=importlib.import_module('ior_mvp.app')
    analysis=analyze('SAU-H0-721049','simulated')
    context=deepcopy(data_repository.get_synthetic_scenario('SAU-H0-721049'));context[field]=value
    monkeypatch.setattr(app_module,'_safe_analysis',lambda *args: deepcopy(analysis))
    monkeypatch.setattr(data_repository,'get_synthetic_scenario',lambda *args:context)
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=simulated')
    assert response.status_code==422
    assert response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

def test_invalid_analysis_disclosure_fails_without_promoting_class():
    analysis=analyze('SAU-H0-721049','simulated')
    analysis['simulation_scenario']['display_labels']['ar']='وزارة'
    with pytest.raises(ValueError,match='dossier|Dossier|disclosure'):
        build_dossier(analysis)

@pytest.mark.parametrize('key',['localized_narrative'])
def test_malformed_nested_required_narrative_has_typed_failure(key):
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    analysis['active_decision'][key]=None
    with pytest.raises(ValueError,match='Dossier'):
        build_dossier(analysis)

@pytest.mark.parametrize('field',['capacity','economics','competition','evsi'])
@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_malformed_optional_mapping_has_typed_422(monkeypatch,field,suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis=deepcopy(analyze('SAU-H0-721049','simulated'))
    analysis[field]=[1]
    with pytest.raises(DossierIntegrityError):build_dossier(analysis)
    app_module=importlib.import_module('ior_mvp.app')
    monkeypatch.setattr(app_module,'_safe_analysis',lambda *args:deepcopy(analysis))
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=simulated')
    assert response.status_code==422
    assert response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_trade_missing_required_year_has_typed_422(monkeypatch,suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    del analysis['trade'][0]['year']
    with pytest.raises(DossierIntegrityError):build_dossier(analysis)
    app_module=importlib.import_module('ior_mvp.app')
    monkeypatch.setattr(app_module,'_safe_analysis',lambda *args:deepcopy(analysis))
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=public')
    assert response.status_code==422
    assert response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize(('field','value'),[
    ('route_evidence',[None]),
    ('buyer_allocation',{'basis':'synthetic fixture','buyers':[{'buyer_id':'B','segment':'fixture','quantity_kt':True}]}),
    ('buyer_allocation',{'basis':'synthetic fixture','buyers':[{'buyer_id':'B','segment':'fixture','quantity_kt':-1}]}),
])
@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_malformed_scenario_records_have_typed_422(monkeypatch,field,value,suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis=deepcopy(analyze('SAU-H0-721049','simulated'))
    context=deepcopy(data_repository.get_synthetic_scenario('SAU-H0-721049'))
    context['synthetic_inputs'][field]=value
    if field=='buyer_allocation':
        passport=deepcopy(next(row for row in analysis['evidence'] if row.get('synthetic_flag')))
        passport['evidence_id']=context['scenario_id']+'::buyer_allocation'
        analysis['evidence'].append(passport)
    monkeypatch.setattr(data_repository,'get_synthetic_scenario',lambda *args:context)
    with pytest.raises(DossierIntegrityError):build_dossier(analysis)
    app_module=importlib.import_module('ior_mvp.app')
    monkeypatch.setattr(app_module,'_safe_analysis',lambda *args:deepcopy(analysis))
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=simulated')
    assert response.status_code==422
    assert response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize(('field','value'),[
    ('headline',{}),('rationale',{'text':None}),
    ('route_label',{'text':'fixture','segments':[None]}),
    ('headline',{'text':'fixture','segments':[{'text':4}]}),
    ('conditions',None),('kill_conditions',[None]),
    ('missing_facts',[{'segments':[]}]),
])
@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_malformed_required_narrative_has_typed_422(monkeypatch,field,value,suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    analysis['active_decision']['localized_narrative']['en'][field]=value
    with pytest.raises(DossierIntegrityError):build_dossier(analysis)
    monkeypatch.setattr(importlib.import_module('ior_mvp.app'),'_safe_analysis',lambda *args:deepcopy(analysis))
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=public')
    assert response.status_code==422
    assert response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize('malformation',['passport_id','producer_record','authority_methodology','public_route'])
@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_required_consumed_source_shapes_fail_typed(monkeypatch,malformation,suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    if malformation=='passport_id':del analysis['evidence'][0]['evidence_id']
    elif malformation=='producer_record':analysis['domestic_capability']['producer_evidence']=[None]
    elif malformation=='authority_methodology':analysis['authority']['methodology']=None
    else:analysis['real_decision']['route_hypotheses']=[None]
    with pytest.raises(DossierIntegrityError):build_dossier(analysis)
    monkeypatch.setattr(importlib.import_module('ior_mvp.app'),'_safe_analysis',lambda *args:deepcopy(analysis))
    response=TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=public')
    assert response.status_code==422 and response.json()['detail']['code']=='DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize('value', [[None], [{'code':'fixture','status':'NOT_CALCULABLE','evidence_ids':[]}], [{'code':'fixture','status':'NOT_CALCULABLE','reason_code':'FIXTURE','evidence_ids':None}]])
@pytest.mark.parametrize('suffix', ['dossier', 'dossier.html'])
def test_malformed_rejection_conditions_fail_at_shared_boundary(monkeypatch, value, suffix):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    analysis = deepcopy(analyze('SAU-H0-721049', 'public'))
    analysis['rejection_conditions'] = value
    with pytest.raises(DossierIntegrityError):
        build_dossier(analysis)
    monkeypatch.setattr(importlib.import_module('ior_mvp.app'), '_safe_analysis', lambda *args: deepcopy(analysis))
    response = TestClient(app).get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=public')
    assert response.status_code == 422
    assert response.json()['detail']['code'] == 'DOSSIER_INTEGRITY_ERROR'

@pytest.mark.parametrize('url', ['javascript:alert(1)', 'data:text/html,<script>alert(1)</script>', 'https://[invalid-host'])
def test_unsafe_or_malformed_passport_urls_remain_escaped_plain_source_text(url):
    from html import escape
    analysis = deepcopy(analyze('SAU-H0-721049', 'public'))
    analysis['evidence'][0]['url'] = url
    analysis['evidence'][0]['title'] = '<script data-probe="passport">alert(1)</script>'
    dossier = build_dossier(analysis)
    for locale in ('en', 'ar'):
        markup = render_dossier_html(dossier, locale)
        assert escape(url, quote=True) in markup
        assert 'href="' + escape(url, quote=True) + '"' not in markup
        assert '<script data-probe="passport">' not in markup
        assert escape(analysis['evidence'][0]['title'], quote=True) in markup
    assert dossier['evidence_pack']['passports'][0]['url'] == url


# Manually enumerated exporter consumers, independent of validator helpers.
_REQUIRED_EXPORT_PATHS = [
    ('snapshot_id',), ('as_of_date',), ('screening_disposition',),
    ('gap_class',), ('preferred_hypothesis',), ('evidence_class_assessment',),
    ('advance_gate',), ('active_decision', 'state'), ('real_decision', 'state'),
    ('authority', 'project_version'), ('rules', 0, 'rule_id'),
    ('rules', 0, 'execution'), ('rules', 0, 'fired'),
    ('hard_exclusions',), ('hard_exclusions', 0, 'code'),
    ('hard_exclusions', 0, 'status'),
    ('hard_exclusions', 0, 'localized_narrative'),
    ('hard_exclusions', 0, 'localized_narrative', 'en'),
    ('hard_exclusions', 0, 'localized_narrative', 'ar'),
    ('capability', 'dimensions'), ('capability', 'dimensions', 0, 'dimension'),
    ('capability', 'dimensions', 0, 'state'),
    ('capability', 'dimensions', 0, 'weight'), ('partner_detail', 'state'),
]
_ROUTE_EXPORT_ROOTS = [
    ('route_hypotheses',), ('active_decision', 'route_hypotheses'),
    ('real_decision', 'route_hypotheses'),
]
_REQUIRED_EXPORT_PATHS += [
    root + (0,) + field
    for root in _ROUTE_EXPORT_ROOTS
    for field in [('route_code',), ('status',), ('precedence',),
                  ('precedence', 'blocked_by_lower_route')]
]
_WRONG_EXPORT_SHAPES = [
    (('snapshot_id',), None), (('as_of_date',), []),
    (('screening_disposition',), {}), (('preferred_hypothesis',), []),
    (('evidence_class_assessment',), []), (('advance_gate',), []),
    (('simulation_decision',), None), (('gap_class',), [1]),
    (('gap_class', 'localized_label'), None),
    (('gap_class', 'localized_label', 'ar'), []),
    (('authority', 'project_version'), 3),
    (('rules', 0, 'rule_id'), []), (('rules', 0, 'execution'), 1),
    (('rules', 0, 'execution'), 'UNKNOWN'), (('rules', 0, 'fired'), 0),
    (('rules', 0, 'synthetic_flag'), 'false'),
    (('hard_exclusions',), [None]), (('hard_exclusions', 0, 'code'), {}),
    (('hard_exclusions', 0, 'status'), None),
    (('hard_exclusions', 0, 'localized_narrative', 'en'), []),
    (('hard_exclusions', 0, 'evidence_ids'), 'PASSPORT'),
    (('capability', 'dimensions'), [None]),
    (('capability', 'dimensions', 0, 'dimension'), None),
    (('capability', 'dimensions', 0, 'state'), {}),
    (('capability', 'dimensions', 0, 'weight'), True),
    (('capability', 'dimensions', 0, 'weight'), float('nan')),
    (('partner_detail', 'state'), 'UNKNOWN'),
    (('partner_detail', 'attempt_passport_ids'), [None]),
    (('domestic_capability', 'producer_evidence', 0, 'evidence_ids'), None),
    (('trade_quality',), [1]), (('domestic_flows',), [1]),
    (('supplier_metrics',), [1]),
]
_WRONG_EXPORT_SHAPES += [
    (root + (0,) + field, value)
    for root in _ROUTE_EXPORT_ROOTS
    for field, value in [
        (('route_code',), True), (('route_code',), 9),
        (('status',), {}), (('precedence',), []),
        (('precedence', 'blocked_by_lower_route'), False),
        (('precedence', 'blocked_by_lower_route'), 9),
        (('localized_reasons',), []), (('localized_reasons', 'ar'), 'reason'),
        (('evidence_ids',), [None]), (('economics',), [1]),
    ]
]


def _assert_typed_export_failure(monkeypatch, analysis, delivery):
    import importlib
    from ior_mvp.dossier_validation import DossierIntegrityError
    if delivery == 'build':
        with pytest.raises(DossierIntegrityError):
            build_dossier(analysis)
        return
    monkeypatch.setattr(importlib.import_module('ior_mvp.app'), '_safe_analysis',
                        lambda *args: deepcopy(analysis))
    response = TestClient(app, raise_server_exceptions=False).get(
        f'/api/opportunities/SAU-H0-721049/{delivery}?mode={analysis["mode"]}&locale=ar')
    assert response.status_code == 422
    assert response.json()['detail']['code'] == 'DOSSIER_INTEGRITY_ERROR'


def _detached_export_analysis():
    analysis = deepcopy(analyze('SAU-H0-721049', 'simulated'))
    # Validate each route source independently even if the engine shares rows.
    analysis['active_decision'] = deepcopy(analysis['active_decision'])
    analysis['real_decision'] = deepcopy(analysis['real_decision'])
    analysis['route_hypotheses'] = deepcopy(analysis['route_hypotheses'])
    return analysis


@pytest.mark.parametrize('path', _REQUIRED_EXPORT_PATHS)
@pytest.mark.parametrize('delivery', ['build', 'dossier', 'dossier.html'])
def test_missing_export_consumer_is_typed(monkeypatch, path, delivery):
    analysis = _detached_export_analysis()
    if path[0] == 'partner_detail':
        # Steel legitimately has no partner detail; exercise an optional record
        # that is present, using its explicit missing-detail state.
        analysis['partner_detail'] = {'state': 'PARTNER_DETAIL_MISSING', 'attempt_passport_ids': []}
    parent = analysis
    for key in path[:-1]:
        parent = parent[key]
    del parent[path[-1]]
    _assert_typed_export_failure(monkeypatch, analysis, delivery)


@pytest.mark.parametrize(('path', 'value'), _WRONG_EXPORT_SHAPES)
@pytest.mark.parametrize('delivery', ['build', 'dossier', 'dossier.html'])
def test_wrong_export_consumer_shape_is_typed(monkeypatch, path, value, delivery):
    analysis = _detached_export_analysis()
    if path[0] == 'partner_detail':
        analysis['partner_detail'] = {'state': 'PARTNER_DETAIL_MISSING', 'attempt_passport_ids': []}
    parent = analysis
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    _assert_typed_export_failure(monkeypatch, analysis, delivery)


@pytest.mark.parametrize('delivery', ['build', 'dossier', 'dossier.html'])
@pytest.mark.parametrize('field', ['synthetic_flag', 'evidence_class', 'source', 'scenario_id', 'display_labels', 'display_label', 'origin_markers'])
def test_scenario_passport_identity_cannot_be_relabelled_public(monkeypatch, field, delivery):
    analysis = _detached_export_analysis()
    passport = next(row for row in analysis['evidence']
                    if row['evidence_id'] == 'SYN-MINISTRY-STEEL-001::demand')
    # False is the original single-field bypass; every other probe retains it
    # to ensure marker checks do not depend solely on the mutable flag.
    passport['synthetic_flag'] = False
    if field == 'origin_markers':
        # The exact supporting ID must retain its provenance even when the
        # flag, source and scenario markers are changed together.
        passport.update(source='PUBLIC_RECORD', evidence_class='C', scenario_id=None,
                        display_labels={}, display_label=None)
    elif field != 'synthetic_flag':
        passport[field] = {'evidence_class': 'A', 'source': 'MINISTRY',
                           'scenario_id': None, 'display_labels': {}, 'display_label': None}[field]
    _assert_typed_export_failure(monkeypatch, analysis, delivery)


@pytest.mark.parametrize('delivery', ['build', 'dossier', 'dossier.html'])
@pytest.mark.parametrize(('field', 'value'), [('source', 'DEMO_GENERATOR'), ('scenario_id', 'SYN-MINISTRY-STEEL-001')])
def test_public_export_rejects_synthetic_origin_without_loading_scenario(monkeypatch, field, value, delivery):
    analysis = deepcopy(analyze('SAU-H0-721049', 'public'))
    analysis['evidence'][0][field] = value
    def forbidden(*args):
        raise AssertionError('Public boundary must not retrieve scenario context')
    monkeypatch.setattr(data_repository, 'get_synthetic_scenario', forbidden)
    _assert_typed_export_failure(monkeypatch, analysis, delivery)


def test_export_boundary_preserves_null_states_zero_false_and_optional_absence():
    analysis = _detached_export_analysis()
    for decision in (analysis['active_decision'], analysis['real_decision']):
        decision['state'] = None
    analysis['screening_disposition'] = 'NO_CANDIDATE'
    analysis['preferred_hypothesis'] = None
    analysis['gap_class'] = None
    analysis['rules'][0]['fired'] = None
    analysis['capability']['dimensions'][0].update(state=0, weight=0)
    for key in ('trade_quality', 'domestic_flows', 'supplier_metrics', 'partner_detail',
                'capacity', 'economics', 'competition', 'evsi'):
        analysis.pop(key, None)
    dossier = build_dossier(analysis)
    assert dossier['decision_state'] is None
    assert dossier['preferred_hypothesis'] is None
    assert dossier['blocks']['capability']['records']['dimensions'][0]['state'] == 0
    assert dossier['blocks']['ledger']['records']['rules'][0]['fired'] is None
    for locale in ('en', 'ar'):
        assert 'NO_CANDIDATE' in render_dossier_html(dossier, locale)
