from copy import deepcopy
import pytest
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier,render_dossier_html

def fields(dossier):
    return {field['key']:field for block in dossier['blocks'].values() for field in block['fields']}

def test_zero_support_is_not_unavailable_npv():
    dossier=build_dossier(analyze('SAU-H0-390210','simulated')); rows=fields(dossier)
    assert rows['minimum_effective_support_m']['value']==0
    assert rows['minimum_effective_support_m']['availability']=='AVAILABLE'
    assert rows['unsupported_npv_m']['value'] is None
    assert rows['unsupported_npv_m']['availability']=='NOT_CALCULABLE'

@pytest.mark.parametrize('missing',['trade','capacity','economics','evsi'])
def test_optional_missing_data_does_not_invent_zero(missing):
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    analysis[missing]=[] if missing=='trade' else None
    dossier=build_dossier(analysis)
    rows=fields(dossier)
    assert rows['unsupported_npv_m']['value'] is None
    assert rows['effective_qualified_capacity_kt']['value'] is None
    if missing=='trade':assert '0.0' not in dossier['demand_conclusion']
    for locale in ['en','ar']:assert render_dossier_html(dossier,locale)

@pytest.mark.parametrize('value',[True,False,'123',float('nan'),float('inf')])
def test_malformed_numeric_source_fails_typed_instead_of_coercing(value):
    analysis=deepcopy(analyze('SAU-H0-721049','simulated'))
    analysis['capacity']['effective_qualified_capacity_kt']=value
    with pytest.raises(ValueError,match='numeric|finite|number'):
        build_dossier(analysis)

def test_unavailable_producer_value_and_empty_passports_remain_honest():
    analysis=deepcopy(analyze('SAU-H0-721049','public'))
    analysis['domestic_capability']['producer_evidence']=[];analysis['evidence']=[]
    dossier=build_dossier(analysis)
    assert dossier['evidence_summary']['public_records']==0
    assert dossier['blocks']['supply']['records']['producers']==[]
    assert dossier['evidence_pack']['passports']==[]
