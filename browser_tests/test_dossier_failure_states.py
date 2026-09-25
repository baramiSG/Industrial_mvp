import pytest

pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('suffix',['dossier','dossier.html'])
def test_dossier_missing_case_and_invalid_mode_never_return_success(browser_session,suffix):
    request=browser_session.page.request
    absent=request.get(f'/api/opportunities/NO-SUCH-CASE/{suffix}?mode=public')
    assert absent.status==404
    assert 'detail' in absent.json()
    assert '<main' not in absent.text()
    invalid=request.get(f'/api/opportunities/SAU-H0-721049/{suffix}?mode=official')
    assert invalid.status==422
    assert 'detail' in invalid.json()
    assert '<main' not in invalid.text()


from copy import deepcopy
import json
from playwright.sync_api import expect
from browser_tests.harness import LOCALES, POLYPROPYLENE
from browser_tests.pages import locale_bundle
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier, render_dossier_html


def _dossier_field_value(page, section, label):
    row=page.locator(f'#dossier-{section} table[data-dossier-table="fields"] tbody > tr').filter(has=page.get_by_role('rowheader',name=label,exact=True))
    expect(row).to_be_visible()
    assert row.count()==1
    return row.locator('td').first.inner_text().strip()


@pytest.mark.parametrize('locale',LOCALES,ids=lambda locale:locale.code)
def test_dossier_empty_unavailable_and_real_zero_are_distinct(browser_session,locale):
    page=browser_session.page;case=POLYPROPYLENE
    strings=locale_bundle(locale)['strings'];base=browser_session.app_server.base_url
    public_analysis=page.request.get(f'{base}/api/opportunities/{case.id}?mode=public').json()
    public_dossier=page.request.get(f'{base}/api/opportunities/{case.id}/dossier?mode=public').json()
    target=next(field for field in public_dossier['blocks']['demand']['fields'] if field['key']=='target_spec_demand_kt')
    assert not public_analysis['capacity']
    assert target['value'] is None and target['availability']=='UNAVAILABLE' and target['source_path'] is None
    assert public_dossier['public_decision']==public_analysis['real_decision']
    page.goto(f'{base}/api/opportunities/{case.id}/dossier.html?mode=public&locale={locale.code}')
    target_label=strings['dossier.field.target_spec_demand_kt']
    value=_dossier_field_value(page,'demand',target_label)
    assert strings['dossier.availability.unavailable'] in value and value!='0'

    simulated=page.request.get(f'{base}/api/opportunities/{case.id}?mode=simulated').json()
    dossier=page.request.get(f'{base}/api/opportunities/{case.id}/dossier?mode=simulated').json()
    assert simulated['economics']['minimum_effective_support_m']==0
    assert simulated['economics'].get('unsupported_npv_m') is None
    fields={field['key']:field for field in dossier['blocks']['economics']['fields']}
    assert fields['minimum_effective_support_m']['value']==0
    assert fields['minimum_effective_support_m']['availability']=='AVAILABLE'
    assert fields['unsupported_npv_m']['value'] is None
    assert fields['unsupported_npv_m']['availability']=='NOT_CALCULABLE'
    assert dossier['public_decision']==public_analysis['real_decision']
    page.goto(f'{base}/api/opportunities/{case.id}/dossier.html?mode=simulated&locale={locale.code}')
    assert _dossier_field_value(page,'economics',strings['dossier.field.minimum_effective_support_m'])=='0'
    npv=_dossier_field_value(page,'economics',strings['dossier.field.unsupported_npv_m'])
    assert strings['dossier.availability.not_calculable'] in npv and npv!='0'

    # Controlled fixture only: remove producer/passport evidence from a detached
    # actual public analysis and call both real production projection/renderers.
    fixture=deepcopy(analyze(case.id,'public'))
    fixture['domestic_capability']['producer_evidence']=[]
    fixture['evidence']=[]
    empty=build_dossier(fixture)
    assert empty['evidence_pack']['passports']==[]
    assert empty['blocks']['supply']['records']['producers']==[]
    fixture_url=f'{base}/api/opportunities/{case.id}/dossier.html?mode=public&locale={locale.code}&fixture=s19-empty'
    def show_fixture(value):
        markup=render_dossier_html(value,locale.code)
        page.unroute(fixture_url)
        page.route(fixture_url,lambda route:route.fulfill(status=200,content_type='text/html; charset=utf-8',body=markup))
        page.goto(fixture_url)
        page.evaluate('document.fonts.ready')
    def assert_empty():
        assert page.locator('#dossier-supply table[data-dossier-table="producers"] tbody tr').count()==0
        assert page.locator('#dossier-evidence .passport').count()==0
        expect(page.locator('#dossier-supply')).to_contain_text(strings['dossier.no_producers'])
        expect(page.locator('#dossier-evidence')).to_contain_text(strings['dossier.no_passports'])
        assert strings['dossier.availability.unavailable'] in _dossier_field_value(page,'demand',target_label)
    show_fixture(empty);assert_empty()
    output=browser_session.artifact_dir/'dossier-isolated-fixtures';output.mkdir(parents=True,exist_ok=True)
    (output/f'empty-{locale.code}.json').write_text(json.dumps({'kind':'ISOLATED TEST FIXTURE; not a governed case fact','input_analysis':fixture,'dossier':empty},ensure_ascii=False,indent=2)+'\n')
    page.locator('#dossier-supply').scroll_into_view_if_needed()
    page.screenshot(path=str(output/f'empty-supply-{locale.code}.png'))
    page.locator('#dossier-evidence').scroll_into_view_if_needed()
    page.screenshot(path=str(output/f'empty-passports-{locale.code}.png'))

    # Run the same browser oracle against deliberately wrong projected outputs;
    # actual renderer, never replacement HTML. Each corruption must be detected.
    false_zero=deepcopy(empty)
    field=next(field for field in false_zero['blocks']['demand']['fields'] if field['key']=='target_spec_demand_kt')
    field.update(value=0,availability='AVAILABLE',reason=None)
    show_fixture(false_zero)
    with pytest.raises(AssertionError):assert_empty()
    invented_producer=deepcopy(empty)
    invented_producer['blocks']['supply']['records']['producers']=[{'producer':'ISOLATED INVENTED ROW'}]
    show_fixture(invented_producer)
    with pytest.raises(AssertionError):assert_empty()
    invented_passport=deepcopy(empty)
    invented_passport['evidence_pack']['passports']=[deepcopy(public_analysis['evidence'][0])]
    show_fixture(invented_passport)
    with pytest.raises(AssertionError):assert_empty()
    show_fixture(empty);assert_empty();page.unroute(fixture_url)
