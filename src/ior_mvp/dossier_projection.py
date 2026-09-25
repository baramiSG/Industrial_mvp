"""Detached, additive methodology §15 projection. No decision calculations."""
from __future__ import annotations
from copy import deepcopy
from math import isfinite
from typing import Any
from .evidence import EvidenceIntegrityError, synthetic_display_labels
from .scenario_contract import _validate_buyer_allocation
from .dossier_validation import DossierIntegrityError, require_mapping

MISSING=object()
SCENARIO_FIELDS={
 'target_specification': ('name','standard','alloy','temper','application','coating_mass_g_m2','tin_coating_g_m2','thickness_mm','thickness_um','width_mm','customer_qualification_required'),
 'plant_line': ('nameplate_kt','availability','yield','qualification_share','market_allocation_share','current_utilisation'),
 'demand': ('base_demand_kt','target_spec_demand_kt','downside_demand_kt','committed_demand_kt','announced_demand_kt','commitment_probability'),
 'upgrade': ('description','incremental_capacity_kt','schedule_months'),
 'economics': ('currency','cash_flows_without_support','hurdle_rate','minimum_efficient_scale_kt','support_instrument','support_required','reason','national_value'),
 'buyer_allocation': ('basis','buyers'),
}
NUMERIC_SCENARIO={
 'plant_line':set(SCENARIO_FIELDS['plant_line']), 'demand':set(SCENARIO_FIELDS['demand']),
 'target_specification':{'coating_mass_g_m2','tin_coating_g_m2','thickness_mm','thickness_um','width_mm'},
 'upgrade':{'incremental_capacity_kt','schedule_months'},
 'economics':{'hurdle_rate','minimum_efficient_scale_kt'},
}


def boundary(mode: str, scenario: dict | None) -> dict:
    if mode=='public': return {'branch':'public','synthetic_flag':False}
    return {'branch':'simulated','synthetic_flag':True,'evidence_class':'D',
            'source':'DEMO_GENERATOR','scenario_id':scenario['scenario_id'],
            'display_labels':synthetic_display_labels()}


def scalar(key: str, value: Any, source_path: str | None, unit: str | None=None,
           *, numeric: bool=False, evidence_ids: list | None=None,
           branch: dict | None=None, missing_status: str='UNAVAILABLE') -> dict:
    absent=value is MISSING
    if absent:
        status=missing_status; value=None
    elif value is None:
        status='NOT_CALCULABLE' if numeric else 'UNAVAILABLE'
    elif isinstance(value,str) and value in ('UNAVAILABLE','NOT_CALCULABLE','NOT_APPLICABLE'):
        status=value;value=None
    else:
        status='AVAILABLE'
        values = value if isinstance(value, list) and key in NUMERIC_SCENARIO['target_specification'] else [value]
        if numeric and (not values or any(isinstance(item,bool) or not isinstance(item,(int,float)) or not isfinite(item) for item in values)):
            raise DossierIntegrityError(f'Dossier finite numeric value required: {source_path}')
    return {'key':key,'availability':status,'value':deepcopy(value),'unit':unit,
            'source_path':None if absent else source_path,'evidence_ids':list(evidence_ids or []),
            'reason':None if status=='AVAILABLE' else f'dossier.availability_reason.{status.lower()}',
            **(branch or {'branch':'public','synthetic_flag':False})}


def project_inputs(scenario: dict | None, evidence: list[dict]) -> dict:
    if scenario is None:return {}
    passports={row['evidence_id'] for row in evidence}
    inputs=scenario['synthetic_inputs'];result={};tag=boundary('simulated',scenario)
    for name,whitelist in SCENARIO_FIELDS.items():
        if name not in inputs:continue
        value=require_mapping(inputs[name],f'scenario.synthetic_inputs.{name}')
        if set(value)-set(whitelist):
            raise DossierIntegrityError(f'Dossier unreviewed scenario fields: {name}')
        evidence_id=f"{scenario['scenario_id']}::{name}"
        if evidence_id not in passports:
            raise DossierIntegrityError(f'Dossier scenario passport missing: {evidence_id}')
        if name=='buyer_allocation':
            buyers=value.get('buyers',[])
            if not isinstance(buyers,list) or any(not isinstance(row,dict) or set(row)-{'buyer_id','segment','quantity_kt'} for row in buyers):
                raise DossierIntegrityError('Dossier buyer allocation whitelist mismatch')
            try:
                _validate_buyer_allocation(value)
            except EvidenceIntegrityError as exc:
                raise DossierIntegrityError('Dossier buyer allocation is invalid') from exc
        result[name]={'data':deepcopy(value),'source_path':f'scenario.synthetic_inputs.{name}',
                      'evidence_ids':[evidence_id],**tag}
    routes=inputs.get('route_evidence',[])
    if not isinstance(routes,list):raise DossierIntegrityError('Dossier route evidence must be a list')
    for row in routes:require_mapping(row,'scenario.synthetic_inputs.route_evidence[]')
    selected=[{key:deepcopy(row[key]) for key in ('route_code','downside_cash_flows_m_sar','hurdle_rate','basis') if key in row}
              for row in routes]
    if selected:
        evidence_id=f"{scenario['scenario_id']}::route_evidence"
        if evidence_id not in passports:raise DossierIntegrityError('Dossier route passport missing')
        result['route_evidence']={'data':selected,'source_path':'scenario.synthetic_inputs.route_evidence',
                                  'evidence_ids':[evidence_id],**tag}
    return result


def project_dossier(analysis: dict, scenario: dict | None) -> dict:
    active=boundary(analysis['mode'],scenario);public=boundary('public',None)
    names=('decision','identity','demand','supply','gap','capability','economics','competition','ledger','evidence','conditions','authority')
    blocks={name:{'key':name,'status':'AVAILABLE','fields':[],'records':{},**active} for name in names}
    inputs=project_inputs(scenario,analysis['evidence'])
    blocks['decision']['records']={'active_decision':deepcopy(analysis['active_decision'])}
    def add(block,key,value,path,unit=None,*,numeric=False,tag=None,ids=None,missing_status='UNAVAILABLE'):
        blocks[block]['fields'].append(scalar(key,value,path,unit,numeric=numeric,branch=tag or active,evidence_ids=ids,missing_status=missing_status))
    for key in ('hs_revision','hs6','national_tariff_line','commercial_name_en','commercial_name_ar','application_boundary'):
        add('identity',key,analysis['opportunity'].get(key,MISSING),'analysis.opportunity.'+key,tag=public)
    # The explicit whitelist maps only inputs already accepted by the engine.
    for name,block in [('target_specification','identity'),('plant_line','supply'),('demand','demand'),('upgrade','supply')]:
        item=inputs.get(name)
        if scenario is None and name in ('plant_line','upgrade'):continue
        for key in SCENARIO_FIELDS[name]:
            value=item['data'].get(key,MISSING) if item else MISSING
            numeric=key in NUMERIC_SCENARIO.get(name,set())
            unit=('kt' if key.endswith('_kt') else 'mm' if key.endswith('_mm') else 'µm' if key.endswith('_um') else 'g/m²' if key.endswith('_g_m2') else 'months' if key=='schedule_months' else 'ratio' if numeric else None)
            add(block,key,value,f'scenario.synthetic_inputs.{name}.{key}' if item and key in item['data'] else None,unit,numeric=numeric,
                ids=item['evidence_ids'] if item else [])
    trade=analysis['trade'];latest=max(trade,key=lambda row:row['year']) if trade else {}
    for key,unit in [('year','year'),('imports_usd_m','USD m'),('imports_kt','kt')]:
        path=f"analysis.trade[{trade.index(latest)}].{key}" if trade else f'analysis.trade[].{key}'
        add('demand',key,latest.get(key,MISSING),path,unit,numeric=True,tag=public)
    for key in ('buyers','buyer_concentration','demand_timing'):
        add('demand',key,MISSING,None)
    blocks['demand']['records']={key:deepcopy(analysis.get(key)) for key in ('trade','trade_quality','domestic_flows','supplier_metrics','partner_detail')}
    blocks['demand']['records']['r8']=[deepcopy(r) for r in analysis['rules'] if r['rule_id']=='R8']
    blocks['supply']['records']={'producers':deepcopy(analysis['domestic_capability'].get('producer_evidence',[])),
                               'coarse_adjacency_signals':deepcopy(analysis['domestic_capability'].get('coarse_adjacency_signals',[]))}
    for key in ('effective_qualified_capacity_kt','qualified_available_kt','specification_adjusted_gap_kt'):
        add('supply' if key!='specification_adjusted_gap_kt' else 'gap',key,(analysis.get('capacity') or {}).get(key,MISSING),'analysis.capacity.'+key,'kt',numeric=True)
    blocks['gap']['records']={key:deepcopy(analysis.get(key)) for key in ('gap_class','hard_exclusions','rejection_conditions','advance_gate','evidence_class_assessment')}
    capability=analysis['capability']
    for key in ('known_weight_coverage','unknown_weight','unknown_penalty_lambda','minimum_known_coverage','d_star'):
        add('capability',key,capability.get(key,MISSING),'analysis.capability.'+key,'ratio',numeric=True)
    blocks['capability']['records']={key:deepcopy(capability.get(key)) for key in ('dimensions','profile_hard_gates','unresolved_hard_gates','known_hard_gate_failures','route_band','route_publishable')}
    blocks['capability']['records'].update({'routes':deepcopy(analysis['route_hypotheses']),
                                         'public_routes':deepcopy(analysis['real_decision']['route_hypotheses']),
                                         'counterfactual':deepcopy(analysis['active_decision'].get('counterfactual'))})
    economics=analysis.get('economics') or {}
    for key,unit in [('unsupported_npv_m','SAR m'),('unsupported_irr','ratio'),('minimum_effective_support_m','SAR m'),('supported_npv_m','SAR m'),('supported_irr','ratio'),('hurdle_rate','ratio')]:
        add('economics',key,economics.get(key,MISSING),'analysis.economics.'+key,unit,numeric=True,missing_status='NOT_CALCULABLE')
    add('economics','downside_result',MISSING,'analysis.economics.downside_result','SAR m',numeric=True,missing_status='NOT_CALCULABLE')
    blocks['economics']['records']['national_value']=deepcopy(economics.get('national_value'))
    if scenario:
        evsi=analysis.get('evsi')
        blocks['conditions']['records']['evsi']=deepcopy(evsi)
        add('conditions','approximate_evsi_m_sar',(evsi or {}).get('approximate_evsi_m_sar',MISSING),'analysis.evsi.approximate_evsi_m_sar','SAR m',numeric=True)
    competition=analysis.get('competition') or {}
    for key,unit in [('post_entry_capacity_to_downside_demand','ratio'),('displacement_m_sar','SAR m')]:
        add('competition',key,competition.get(key,MISSING),'analysis.competition.'+key,unit,numeric=True)
    add('competition','sunset_date',MISSING,'analysis.active_decision.sunset_date')
    blocks['competition']['records']['assessment']=deepcopy(analysis.get('competition'))
    blocks['ledger']['records']['rules']=deepcopy(analysis['rules'])
    blocks['conditions']['records'].update({key:deepcopy(analysis['active_decision'].get(key,[])) for key in ('conditions','kill_conditions','missing_facts')})
    blocks['authority']['records']={key:deepcopy(analysis[key]) for key in ('authority','integrity','snapshot_id','as_of_date')}
    local_ids={row['evidence_id'] for row in analysis['evidence']}
    external=sorted({e for route in analysis['route_hypotheses'] if route.get('route_code')==8 for e in route.get('evidence_ids',[]) if e not in local_ids})
    pack={'passports':deepcopy(analysis['evidence']),'scenario_inputs':inputs,
          'external_dependencies':[{'evidence_id':e,'status':'EXTERNAL_DEPENDENCY','source_path':'analysis.route_hypotheses[route_code=8].evidence_ids'} for e in external],
          'decision_history':{'status':'NONE_RECORDED','records':[]},'expert_overrides':{'status':'NONE_RECORDED','records':[]},
          'revision_concordance':{'availability':'UNAVAILABLE','source_path':None},
          'specification_source_spans':{'availability':'UNAVAILABLE','records':[]}}
    blocks['evidence']['records']={'local_evidence_ids':sorted(local_ids),'external_dependencies':deepcopy(pack['external_dependencies'])}
    return {'dossier_version':'2.0.0','public_decision':deepcopy(analysis['real_decision']),
            'blocks':blocks,'evidence_pack':pack}
