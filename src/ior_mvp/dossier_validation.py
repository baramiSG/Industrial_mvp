"""Fail closed at the export boundary; never change an engine decision."""
from __future__ import annotations
from typing import Any
from math import isfinite
from . import data_repository
from .evidence import synthetic_display_labels


class DossierIntegrityError(ValueError):
    """The supplied analytical record and its export context disagree."""


def require_mapping(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise DossierIntegrityError(f'Dossier mapping required: {path}')
    return value


def require_records(value: Any, path: str) -> list[dict]:
    if not isinstance(value,list) or any(not isinstance(row,dict) for row in value):
        raise DossierIntegrityError(f'Dossier record list required: {path}')
    return value


def require_text(value: Any, path: str) -> None:
    if not isinstance(value, str):
        raise DossierIntegrityError(f'Dossier text required: {path}')


def require_ids(value: Any, path: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise DossierIntegrityError(f'Dossier reference list required: {path}')


def require_routes(value: Any, path: str) -> None:
    for row in require_records(value, path):
        code = row.get('route_code')
        if type(code) is not int or code not in range(9):
            raise DossierIntegrityError(f'Dossier route code invalid: {path}')
        require_text(row.get('status'), path + '.status')
        precedence = require_mapping(row.get('precedence'), path + '.precedence')
        if 'blocked_by_lower_route' not in precedence:
            raise DossierIntegrityError(f'Dossier route precedence required: {path}')
        blocker = precedence['blocked_by_lower_route']
        if blocker is not None and (type(blocker) is not int or blocker not in range(9)):
            raise DossierIntegrityError(f'Dossier precedence route code invalid: {path}')
        if row.get('economics') is not None:
            require_mapping(row['economics'], path + '.economics')
        if 'localized_reasons' in row:
            reasons = require_mapping(row['localized_reasons'], path + '.localized_reasons')
            for locale in ('en', 'ar'):
                if locale in reasons:
                    require_ids(reasons[locale], path + '.localized_reasons.' + locale)
        if 'evidence_ids' in row:
            require_ids(row['evidence_ids'], path + '.evidence_ids')


def has_synthetic_origin(row: dict) -> bool:
    return (row.get('synthetic_flag') is True or row.get('source') == 'DEMO_GENERATOR'
            or row.get('scenario_id') is not None)


def require_narrative(value: Any, path: str) -> None:
    entry=require_mapping(value,path)
    if not isinstance(entry.get('text'),str):
        raise DossierIntegrityError(f'Dossier narrative text required: {path}')
    segments=entry.get('segments')
    if segments is None:
        return
    if not isinstance(segments,list):
        raise DossierIntegrityError(f'Dossier narrative segments required: {path}')
    for segment in segments:
        require_mapping(segment,path+'.segments[]')
        if not isinstance(segment.get('text'),str):
            raise DossierIntegrityError(f'Dossier segment text required: {path}')
        if 'ltr_isolate' in segment and not isinstance(segment['ltr_isolate'],bool):
            raise DossierIntegrityError(f'Dossier segment isolation flag invalid: {path}')


def validate_analysis(analysis: dict) -> None:
    require_mapping(analysis, 'analysis')
    if analysis.get('mode') not in ('public', 'simulated'):
        raise DossierIntegrityError('Dossier mode is invalid')
    for key in ('opportunity', 'active_decision', 'real_decision', 'domestic_capability', 'capability', 'authority', 'integrity', 'evidence_class_assessment', 'advance_gate'):
        require_mapping(analysis.get(key), f'analysis.{key}')
    for key in ('snapshot_id', 'as_of_date', 'screening_disposition'):
        require_text(analysis.get(key), f'analysis.{key}')
    for key in ('gap_class', 'preferred_hypothesis'):
        if key not in analysis:
            raise DossierIntegrityError(f'Dossier field required: analysis.{key}')
        if analysis[key] is not None:
            require_mapping(analysis[key], f'analysis.{key}')
    gap = analysis['gap_class'] or {}
    if 'localized_label' in gap:
        labels = require_mapping(gap['localized_label'], 'gap_class.localized_label')
        for locale in ('en', 'ar'):
            if locale in labels:
                require_text(labels[locale], 'gap_class.localized_label.' + locale)
    if analysis['mode'] == 'simulated' and 'simulation_decision' in analysis:
        require_mapping(analysis['simulation_decision'], 'analysis.simulation_decision')
    for key in ('id','hs_revision','hs6','commercial_name_en','commercial_name_ar','application_boundary'):
        if not isinstance(analysis['opportunity'].get(key), str):
            raise DossierIntegrityError(f'Dossier identity field required: {key}')
    for key in ('trade', 'rules', 'evidence', 'route_hypotheses'):
        require_records(analysis.get(key),f'analysis.{key}')
    require_routes(analysis['route_hypotheses'], 'analysis.route_hypotheses')
    for row in analysis['evidence']:
        for key in ('evidence_id','source','title','evidence_class','status'):
            if not isinstance(row.get(key),str):
                raise DossierIntegrityError(f'Dossier passport field required: {key}')
        if not isinstance(row.get('synthetic_flag'),bool):
            raise DossierIntegrityError('Dossier passport synthetic flag required')
    for producer in require_records(analysis['domestic_capability'].get('producer_evidence',[]),'domestic_capability.producer_evidence'):
        if not isinstance(producer.get('producer'),str):
            raise DossierIntegrityError('Dossier producer name required')
        if 'evidence_ids' in producer:
            require_ids(producer['evidence_ids'], 'producer.evidence_ids')
    for row in require_records(analysis.get('hard_exclusions'), 'analysis.hard_exclusions'):
        for key in ('code', 'status'):
            require_text(row.get(key), 'hard_exclusion.' + key)
        narrative = require_mapping(row.get('localized_narrative'), 'hard_exclusion.localized_narrative')
        for locale in ('en', 'ar'):
            require_text(narrative.get(locale), 'hard_exclusion.localized_narrative.' + locale)
        if 'evidence_ids' in row:
            require_ids(row['evidence_ids'], 'hard_exclusion.evidence_ids')
    for row in require_records(analysis['capability'].get('dimensions'), 'capability.dimensions'):
        require_text(row.get('dimension'), 'capability.dimensions.dimension')
        if type(row.get('state')) is not int and row.get('state') != 'U':
            raise DossierIntegrityError('Dossier capability dimension state required')
        weight = row.get('weight')
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not isfinite(weight):
            raise DossierIntegrityError('Dossier finite capability dimension weight required')
    for row in require_records(analysis.get('rejection_conditions'),'analysis.rejection_conditions'):
        for key in ('code','status','reason_code'):
            if not isinstance(row.get(key),str):
                raise DossierIntegrityError(f'Dossier rejection condition field required: {key}')
        ids=row.get('evidence_ids')
        if not isinstance(ids,list) or any(not isinstance(value,str) for value in ids):
            raise DossierIntegrityError('Dossier rejection condition evidence IDs required')
    authority=analysis['authority']
    require_text(authority.get('project_version'), 'authority.project_version')
    methodology=require_mapping(authority.get('methodology'),'authority.methodology')
    versions=require_mapping(authority.get('config_versions'),'authority.config_versions')
    for key in ('file','sha256'):
        if not isinstance(methodology.get(key),str):
            raise DossierIntegrityError(f'Dossier methodology field required: {key}')
    for key in ('thresholds','sector_profiles','evidence_policy','ui_strings'):
        if not isinstance(versions.get(key),str):
            raise DossierIntegrityError(f'Dossier authority version required: {key}')
    for key in ('capacity','economics','competition','evsi','partner_detail','trade_quality','domestic_flows','supplier_metrics'):
        if analysis.get(key) is not None:
            require_mapping(analysis[key], f'analysis.{key}')
    partner = analysis.get('partner_detail')
    if partner is not None:
        if partner.get('state') not in ('PARTNER_DETAIL_OBSERVED', 'PARTNER_DETAIL_MISSING', 'PARTNER_TRADE_OBSERVED_ZERO'):
            raise DossierIntegrityError('Dossier partner detail state is invalid')
        if 'attempt_passport_ids' in partner:
            require_ids(partner['attempt_passport_ids'], 'partner_detail.attempt_passport_ids')
    for row in analysis['trade']:
        year=row.get('year')
        if isinstance(year,bool) or not isinstance(year,int):
            raise DossierIntegrityError('Dossier trade observation requires an integer year')
        for key in ('imports_usd_m','imports_kt'):
            value=row.get(key)
            if value is None or value in ('UNAVAILABLE','NOT_CALCULABLE','NOT_APPLICABLE'):
                continue
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value):
                raise DossierIntegrityError(f'Dossier finite trade value required: {key}')
    for decision in (analysis['active_decision'], analysis['real_decision']):
        require_routes(decision.get('route_hypotheses'),'decision.route_hypotheses')
        if 'state' not in decision or decision['state'] not in ('ADVANCE','INVESTIGATE','REJECT','MONITOR',None):
            raise DossierIntegrityError('Dossier decision state is invalid')
        for key in ('headline','rationale','route_label'):
            if not isinstance(decision.get(key), str):
                raise DossierIntegrityError(f'Dossier decision field required: {key}')
        for locale in ('en','ar'):
            narrative=require_mapping(require_mapping(decision.get('localized_narrative'), 'decision.localized_narrative').get(locale), f'decision.localized_narrative.{locale}')
            for key in ('headline','rationale','route_label'):
                require_narrative(narrative.get(key),f'{locale}.{key}')
            for key in ('conditions','kill_conditions','missing_facts'):
                entries=narrative.get(key,[]) if key=='missing_facts' else narrative.get(key)
                if not isinstance(entries,list):
                    raise DossierIntegrityError(f'Dossier narrative list required: {locale}.{key}')
                for entry in entries:require_narrative(entry,f'{locale}.{key}[]')
    for row in analysis['rules']:
        require_text(row.get('rule_id'), 'rule.rule_id')
        if row.get('execution') not in ('FULL', 'DEGRADED', 'DISABLED'):
            raise DossierIntegrityError('Dossier rule execution is invalid')
        if 'fired' not in row or (row['fired'] is not None and type(row['fired']) is not bool):
            raise DossierIntegrityError('Dossier rule fired flag required')
        if 'synthetic_flag' in row and type(row['synthetic_flag']) is not bool:
            raise DossierIntegrityError('Dossier rule synthetic flag invalid')
        require_mapping(row.get('metrics',{}),'rule.metrics')
        for locale in ('en','ar'):
            localized=require_mapping(require_mapping(row.get('localized'), 'rule.localized').get(locale), f'rule.localized.{locale}')
            for key in ('name','result','decision_effect'):
                require_narrative(localized.get(key),f'rule.{locale}.{key}')
    if analysis['mode']=='public':
        if analysis.get('simulation_scenario') is not None or any(has_synthetic_origin(row) for row in analysis['evidence']):
            raise DossierIntegrityError('Dossier public evidence contains synthetic context')
        if any(row.get('synthetic_flag') is True for row in analysis['rules']):
            raise DossierIntegrityError('Dossier public rules contain synthetic context')


def scenario_context(analysis: dict) -> dict | None:
    if analysis['mode']=='public':
        return None
    scenario=require_mapping(data_repository.get_synthetic_scenario(analysis['opportunity']['id']), 'scenario')
    disclosure=require_mapping(analysis.get('simulation_scenario'), 'analysis.simulation_scenario')
    labels=synthetic_display_labels()
    checks={
        'opportunity_id': analysis['opportunity']['id'],
        'scenario_id': disclosure.get('scenario_id'),
        'scenario_version': disclosure.get('scenario_version'),
        'source': 'DEMO_GENERATOR', 'evidence_class': 'D',
        'synthetic_flag': True, 'display_label': labels['en'],
    }
    for key,expected in checks.items():
        actual=scenario.get(key)
        if actual!=expected or type(actual) is not type(expected):
            raise DossierIntegrityError(f'Dossier scenario identity mismatch: {key}')
    if not scenario.get('scenario_id') or not scenario.get('scenario_version'):
        raise DossierIntegrityError('Dossier scenario identity missing')
    if disclosure.get('display_labels')!=labels or disclosure.get('display_label')!=labels['en']:
        raise DossierIntegrityError('Dossier disclosure does not match evidence policy')
    for row in analysis['evidence']:
        supporting = row['evidence_id'].startswith(scenario['scenario_id'] + '::')
        if (supporting or has_synthetic_origin(row)) and (
            row.get('synthetic_flag') is not True
            or row.get('scenario_id')!=scenario['scenario_id'] or row.get('source')!='DEMO_GENERATOR'
            or row.get('evidence_class')!='D' or row.get('display_labels')!=labels
            or row.get('display_label')!=labels['en']
        ):
            raise DossierIntegrityError('Dossier synthetic passport identity mismatch')
    require_mapping(scenario.get('synthetic_inputs'), 'scenario.synthetic_inputs')
    return scenario
