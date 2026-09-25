from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from .dossier_validation import DossierIntegrityError, validate_analysis, scenario_context
from .dossier_projection import project_dossier
from pathlib import Path
from html import escape
from urllib.parse import quote, urlencode, urlsplit
from string import Formatter
from typing import Any

from .case_selection_view import case_selection_view
from .config import ui_text, ui_strings_bundle


STATIC_DIR = Path(__file__).resolve().parent / "static"
S15B_PROFILES = {
    "SAU-H6-294110": "pharma_api",
    "SAU-H6-294120": "pharma_api",
    "SAU-H6-310430": "fertilizers",
    "SAU-H6-310510": "fertilizers",
}


def _selection_reference(opportunity_id: str) -> dict[str, str] | None:
    profile = S15B_PROFILES.get(opportunity_id)
    if profile is None:
        return None
    selection = case_selection_view()
    return {
        "selection_id": selection["selection_id"],
        "rule_version": selection["rule_version"],
        "reference": selection["selection_reference"]["path"],
        "profile": profile,
    }


def _dossier_styles() -> str:
    parts = (
        STATIC_DIR / "css" / "tokens.css",
        STATIC_DIR / "css" / "dossier.css",
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in parts)


def _css_string(value: str) -> str:
    """Serialize policy text without allowing CSS or HTML delimiters."""
    return '"' + ''.join('\\' + format(ord(char), 'x') + ' ' for char in value) + '"'


def build_dossier(analysis: dict[str, Any]) -> dict[str, Any]:
    validate_analysis(analysis)
    scenario = scenario_context(analysis)
    decision = analysis["active_decision"]
    opportunity = analysis["opportunity"]
    selection_reference = _selection_reference(opportunity["id"])
    latest = max(analysis["trade"], key=lambda row: row["year"]) if analysis["trade"] else {}
    capacity = analysis.get("capacity") or {}
    economics = analysis.get("economics") or {}
    evidence = analysis.get("evidence", [])
    public_count = sum(
        1 for row in evidence if row.get("synthetic_flag") is False
    )
    synthetic_count = sum(
        1 for row in evidence if row.get("synthetic_flag") is True
    )
    simulated_rules = [
        row
        for row in analysis.get("rules", [])
        if row.get("synthetic_flag") is True
    ]
    public_contradictions = [
        {
            "evidence_id": row["evidence_id"],
            "source": row["source"],
            "contradiction": row["contradiction"],
            "synthetic_flag": False,
        }
        for row in evidence
        if row.get("synthetic_flag") is False
        and isinstance(row.get("contradiction"), str)
        and row["contradiction"]
    ]
    synthetic_contradictions = (
        [
            {
                "evidence_id": row["evidence_id"],
                "source": row["source"],
                "contradiction": row["contradiction"],
                "synthetic_flag": True,
                "scenario_id": row["scenario_id"],
                "display_labels": row["display_labels"],
            }
            for row in evidence
            if row.get("synthetic_flag") is True
            and isinstance(row.get("contradiction"), str)
            and row["contradiction"]
        ]
        if analysis["mode"] == "simulated"
        else []
    )
    contradiction_register = {
        "public": public_contradictions,
        "synthetic": synthetic_contradictions,
        "synthetic_status": (
            "NOT_APPLICABLE"
            if analysis["mode"] == "public"
            else (
                "PRESENT"
                if synthetic_contradictions
                else "NONE_RECORDED"
            )
        ),
    }
    def measured(value):
        return f"{value:,.1f}" if isinstance(value, (int, float)) and not isinstance(value, bool) else "UNAVAILABLE"
    demand_conclusion = (
        f"Latest frozen public imports: USD {measured(latest.get('imports_usd_m'))}m and "
        f"{measured(latest.get('imports_kt'))} kt in {latest.get('year', 'UNAVAILABLE')}."
    )
    if capacity:
        demand_conclusion += (
            f" Simulation target demand is {measured(capacity.get('target_spec_demand_kt'))} kt; "
            f"the specification-adjusted gap is {measured(capacity.get('specification_adjusted_gap_kt'))} kt."
        )
    result = {
        "dossier_version": "2.0.0",
        "opportunity_id": opportunity["id"],
        "mode": analysis["mode"],
        "decision_headline": decision["headline"],
        "decision_rationale": decision["rationale"],
        "decision_state": decision["state"],
        "route": decision["route_label"],
        "localized_narrative": decision.get(
            "localized_narrative"
        ),
        "narrative_version": decision.get("narrative_version"),
        "screening_disposition": analysis[
            "screening_disposition"
        ],
        "gap_class": analysis["gap_class"],
        "route_hypotheses": analysis["route_hypotheses"],
        "preferred_hypothesis": analysis["preferred_hypothesis"],
        "evidence_class_assessment": analysis[
            "evidence_class_assessment"
        ],
        "advance_gate": analysis["advance_gate"],
        "hard_exclusions": analysis["hard_exclusions"],
        "rejection_conditions": analysis["rejection_conditions"],
        "product_identity": {
            "hs_revision": opportunity["hs_revision"],
            "hs6": opportunity["hs6"],
            "commercial_name_en": opportunity["commercial_name_en"],
            "commercial_name_ar": opportunity["commercial_name_ar"],
            "application_boundary": opportunity["application_boundary"],
        },
        "demand_conclusion": demand_conclusion,
        "supply_conclusion": analysis["domestic_capability"],
        "gap_diagnosis": {
            "public_state": analysis["real_decision"]["state"],
            "active_state": decision["state"],
            "gap_class": analysis["gap_class"],
            "capacity": capacity,
            "simulated_rules": simulated_rules,
        },
        "capability_route": analysis["capability"],
        "economics": economics,
        "competition_policy": analysis.get("competition"),
        "partner_detail": analysis.get("partner_detail"),
        "evidence_summary": {
            "public_records": public_count,
            "synthetic_records": synthetic_count,
            "snapshot_id": analysis["snapshot_id"],
            "as_of_date": analysis["as_of_date"],
            "authority": analysis["authority"],
            "integrity": analysis["integrity"],
            **(
                {"selection": selection_reference}
                if selection_reference is not None
                else {}
            ),
        },
        "contradiction_register": contradiction_register,
        "conditions": decision.get("conditions", []),
        "kill_conditions": decision.get("kill_conditions", []),
        "next_evidence_actions": decision.get("missing_facts", []),
        "counterfactual": (
            analysis.get("simulation_decision", {}).get("counterfactual")
            if analysis["mode"] == "simulated"
            else None
        ),
        "synthetic_disclosure": analysis.get("simulation_scenario"),
    }
    result.update(project_dossier(analysis, scenario))
    return deepcopy(result)

SECTION_LABELS = {'identity': 'dossier.section.identity', 'demand': 'dossier.section.demand', 'supply': 'dossier.section.supply', 'gap': 'dossier.section.gap', 'capability': 'dossier.section.capability', 'economics': 'dossier.section.economics', 'competition': 'dossier.section.competition', 'ledger': 'dossier.section.ledger', 'evidence': 'dossier.section.evidence', 'conditions': 'dossier.section.conditions', 'authority': 'dossier.section.authority'}
SECTIONS = tuple(SECTION_LABELS)
FIELD_LABELS = {'actual': 'dossier.field.actual',
 'additionality': 'dossier.field.additionality',
 'agronomic_performance': 'dossier.field.agronomic_performance',
 'alloy': 'dossier.field.alloy',
 'analytical_validation': 'dossier.field.analytical_validation',
 'announced_demand_kt': 'dossier.field.announced_demand_kt',
 'apparent_consumption_kt': 'dossier.field.apparent_consumption_kt',
 'application': 'dossier.field.application',
 'application_boundary': 'dossier.application_boundary',
 'application_qualification': 'dossier.field.application_qualification',
 'approximate_evsi_m_sar': 'dossier.field.approximate_evsi_m_sar',
 'attempt_passport_ids': 'dossier.field.attempt_passport_ids',
 'availability': 'dossier.field.availability',
 'base_demand_kt': 'dossier.field.base_demand_kt',
 'basis': 'dossier.field.basis',
 'benefits_m_sar': 'dossier.field.benefits_m_sar',
 'blocked_field': 'dossier.field.blocked_field',
 'blocking': 'dossier.field.blocking',
 'bulk_band_usd_t': 'dossier.field.bulk_band_usd_t',
 'bulk_uv_range_usd_t': 'dossier.field.bulk_uv_range_usd_t',
 'buyer_concentration': 'dossier.field.buyer_concentration',
 'buyer_id': 'dossier.field.buyer_id',
 'buyers': 'dossier.field.buyers',
 'calculation_basis': 'dossier.field.calculation_basis',
 'capacity_ratio': 'dossier.field.capacity_ratio',
 'capacity_time_window': 'executive.field.capacity_time_window',
 'cash_flows_without_support': 'dossier.field.cash_flows_without_support',
 'certification_customer_qualification': 'executive.field.certification_customer_qualification',
 'checks': 'dossier.field.checks',
 'coating_mass_g_m2': 'dossier.field.coating_mass_g_m2',
 'coating_route_and_mass': 'dossier.field.coating_route_and_mass',
 'commercial_name_ar': 'dossier.field.commercial_name_ar',
 'commercial_name_en': 'dossier.field.commercial_name_en',
 'commitment_probability': 'dossier.field.commitment_probability',
 'committed_demand_kt': 'dossier.field.committed_demand_kt',
 'committed_within_target': 'dossier.field.committed_within_target',
 'comparison_observations': 'dossier.field.comparison_observations',
 'components': 'dossier.field.components',
 'computed_export_import_value_ratio': 'dossier.field.computed_export_import_value_ratio',
 'concentration_before_after': 'dossier.field.concentration_before_after',
 'confidence_cap': 'dossier.field.confidence_cap',
 'confirmed_outlier': 'dossier.field.confirmed_outlier',
 'containment': 'dossier.field.containment',
 'conversion_route': 'dossier.field.conversion_route',
 'core_process_route': 'executive.field.core_process_route',
 'costs_m_sar': 'dossier.field.costs_m_sar',
 'criticality_evidence_id': 'dossier.field.criticality_evidence_id',
 'criticality_status': 'dossier.field.criticality_status',
 'currency': 'dossier.field.currency',
 'current_utilisation': 'dossier.field.current_utilisation',
 'customer_liability': 'dossier.field.customer_liability',
 'customer_qualification_required': 'dossier.field.customer_qualification_required',
 'd_star': 'dossier.field.d_star',
 'delay_cost_m_sar': 'dossier.field.delay_cost_m_sar',
 'delta': 'dossier.field.delta',
 'delta_ln_quantity': 'dossier.field.delta_ln_quantity',
 'delta_ln_unit_value': 'dossier.field.delta_ln_unit_value',
 'delta_ln_value': 'dossier.field.delta_ln_value',
 'demand_timing': 'dossier.field.demand_timing',
 'dependent_incremental_national_value_m_sar': 'dossier.field.dependent_incremental_national_value_m_sar',
 'description': 'dossier.field.description',
 'detail': 'dossier.field.detail',
 'disclosed_export_import_value_ratio': 'dossier.field.disclosed_export_import_value_ratio',
 'disclosed_installed_capacity_tpy': 'dossier.field.disclosed_installed_capacity_tpy',
 'disclosed_public_nameplate_kt': 'dossier.field.disclosed_public_nameplate_kt',
 'disclosed_ratio_consistent': 'dossier.field.disclosed_ratio_consistent',
 'displacement': 'dossier.field.displacement',
 'displacement_m_sar': 'dossier.field.displacement_m_sar',
 'domestic_origin_exports_kt': 'dossier.field.domestic_origin_exports_kt',
 'domestic_origin_exports_separated': 'dossier.field.domestic_origin_exports_separated',
 'domestic_production_kt': 'dossier.field.domestic_production_kt',
 'domestic_value_added': 'dossier.field.domestic_value_added',
 'downside_cash_flows_m_sar': 'dossier.field.downside_cash_flows_m_sar',
 'downside_demand_kt': 'dossier.field.downside_demand_kt',
 'downside_result': 'dossier.field.downside_result',
 'downside_within_target': 'dossier.field.downside_within_target',
 'effective_capacity_source_key': 'dossier.field.effective_capacity_source_key',
 'effective_qualified_capacity_kt': 'dossier.field.effective_qualified_capacity_kt',
 'effective_utilisation': 'dossier.field.effective_utilisation',
 'effluent': 'dossier.field.effluent',
 'eligible_partner_count': 'dossier.field.eligible_partner_count',
 'emissions_and_safe_handling': 'dossier.field.emissions_and_safe_handling',
 'enabler_id': 'dossier.field.enabler_id',
 'engineering_certification': 'dossier.field.engineering_certification',
 'equipment_envelope': 'executive.field.equipment_envelope',
 'established': 'dossier.field.established',
 'established_nameplate': 'dossier.field.established_nameplate',
 'evidence_class': 'dossier.field.evidence_class',
 'evidence_cost_m_sar': 'dossier.field.evidence_cost_m_sar',
 'evidence_ids': 'dossier.field.evidence_ids',
 'evidence_needs': 'dossier.field.evidence_needs',
 'execution_cap': 'dossier.field.execution_cap',
 'expansion_assumption_applied': 'dossier.field.expansion_assumption_applied',
 'expected': 'dossier.field.expected',
 'export_import_value_ratio': 'dossier.field.export_import_value_ratio',
 'export_import_value_ratio_threshold': 'dossier.field.export_import_value_ratio_threshold',
 'exports': 'dossier.field.exports',
 'feasibility': 'dossier.field.feasibility',
 'feedstock_chemistry': 'executive.field.feedstock_chemistry',
 'feedstock_route': 'dossier.field.feedstock_route',
 'finding': 'dossier.field.finding',
 'finishing_spec_control': 'executive.field.finishing_spec_control',
 'fiscal_receipts': 'dossier.field.fiscal_receipts',
 'flow': 'dossier.field.flow',
 'flow_basis': 'dossier.field.flow_basis',
 'forming_fabrication': 'dossier.field.forming_fabrication',
 'formula': 'dossier.field.formula',
 'formulation_granulation': 'dossier.field.formulation_granulation',
 'from_year': 'dossier.field.from_year',
 'gmp': 'dossier.field.gmp',
 'government_cost': 'dossier.field.government_cost',
 'greenfield_alternative': 'dossier.field.greenfield_alternative',
 'ground_truth_backtest': 'dossier.field.ground_truth_backtest',
 'heat_treatment': 'dossier.field.heat_treatment',
 'hhi': 'dossier.field.hhi',
 'hhi_after': 'dossier.field.hhi_after',
 'hhi_before': 'dossier.field.hhi_before',
 'hhi_threshold': 'dossier.field.hhi_threshold',
 'hs6': 'dossier.field.hs6',
 'hs_revision': 'dossier.field.hs_revision',
 'hurdle_rate': 'dossier.field.hurdle_rate',
 'imports_kt': 'dossier.field.imports_kt',
 'imports_usd_m': 'dossier.field.imports_usd_m',
 'impurity_control': 'dossier.field.impurity_control',
 'incremental_capacity_kt': 'dossier.field.incremental_capacity_kt',
 'incremental_national_value_m_sar': 'dossier.field.incremental_national_value_m_sar',
 'inputs': 'dossier.field.inputs',
 'installed_capacity_tpy': 'dossier.field.installed_capacity_tpy',
 'ip_fto': 'dossier.field.ip_fto',
 'iqr_usd_t': 'dossier.field.iqr_usd_t',
 'joining_finishing': 'dossier.field.joining_finishing',
 'knowledge_skills': 'dossier.field.knowledge_skills',
 'known_hard_gate_failure': 'dossier.field.known_hard_gate_failure',
 'known_hard_gate_failures': 'dossier.field.known_hard_gate_failures',
 'known_weight_coverage': 'dossier.field.known_weight_coverage',
 'largest_supplier_quantity_share': 'dossier.field.largest_supplier_quantity_share',
 'largest_supplier_share': 'dossier.field.largest_supplier_share',
 'largest_supplier_threshold': 'dossier.field.largest_supplier_threshold',
 'latest_imports_kt': 'dossier.field.latest_imports_kt',
 'latest_imports_usd_m': 'executive.value.latest_imports_usd_m',
 'latest_public_exports_kt': 'dossier.field.latest_public_exports_kt',
 'latest_public_imports_kt': 'dossier.field.latest_public_imports_kt',
 'latest_public_imports_usd_m': 'dossier.field.latest_public_imports_usd_m',
 'latest_public_year': 'dossier.field.latest_public_year',
 'line_nameplate_kt': 'dossier.field.line_nameplate_kt',
 'mandatory_or_customer_standard': 'dossier.field.mandatory_or_customer_standard',
 'market_allocation_share': 'dossier.field.market_allocation_share',
 'match': 'dossier.field.match',
 'maximum_effective_utilisation': 'dossier.field.maximum_effective_utilisation',
 'mes_fill': 'dossier.field.mes_fill',
 'minimum_effective_support_m': 'dossier.field.minimum_effective_support_m',
 'minimum_effective_utilisation': 'dossier.field.minimum_effective_utilisation',
 'minimum_efficient_scale_kt': 'dossier.field.minimum_efficient_scale_kt',
 'minimum_known_coverage': 'dossier.field.minimum_known_coverage',
 'minimum_mes_fill': 'dossier.field.minimum_mes_fill',
 'minimum_probability_adjusted_demand_addition': 'dossier.field.minimum_probability_adjusted_demand_addition',
 'minimum_retained_import_penetration': 'dossier.field.minimum_retained_import_penetration',
 'minimum_spec_matched_shortage': 'dossier.field.minimum_spec_matched_shortage',
 'minimum_valid_value_coverage': 'dossier.field.minimum_valid_value_coverage',
 'missing_years': 'dossier.field.missing_years',
 'monthly_partner_tariff_line_available': 'dossier.field.monthly_partner_tariff_line_available',
 'name': 'dossier.field.name',
 'named_missing_facts': 'dossier.field.named_missing_facts',
 'named_molecule_and_synthesis_route': 'dossier.field.named_molecule_and_synthesis_route',
 'nameplate_kt': 'dossier.field.nameplate_kt',
 'nameplate_source_evidence_id': 'dossier.field.nameplate_source_evidence_id',
 'nameplate_status': 'dossier.field.nameplate_status',
 'national_tariff_line': 'dossier.field.national_tariff_line',
 'national_value': 'dossier.field.national_value',
 'need_code': 'dossier.field.need_code',
 'net_import_exposure_kt': 'dossier.field.net_import_exposure_kt',
 'net_weight_kt': 'dossier.field.net_weight_kt',
 'next_fact': 'dossier.field.next_fact',
 'non_additionality': 'dossier.field.non_additionality',
 'note': 'dossier.field.note',
 'numeric_evsi': 'dossier.field.numeric_evsi',
 'nutrient_basis': 'dossier.field.nutrient_basis',
 'observed_partner_rows': 'dossier.field.observed_partner_rows',
 'observed_passport_id': 'dossier.field.observed_passport_id',
 'observed_span_years': 'dossier.field.observed_span_years',
 'opportunity_id': 'dossier.field.opportunity_id',
 'outlier_candidate': 'dossier.field.outlier_candidate',
 'partner': 'dossier.field.partner',
 'partner_quantity_hhi': 'dossier.field.partner_quantity_hhi',
 'partner_snapshot_id': 'dossier.field.partner_snapshot_id',
 'partner_value_hhi': 'dossier.field.partner_value_hhi',
 'passes': 'dossier.field.passes',
 'passes_default_warning': 'dossier.field.passes_default_warning',
 'performance_requirement': 'dossier.field.performance_requirement',
 'period_year': 'dossier.field.period_year',
 'physical_output_ceiling_kt': 'dossier.field.physical_output_ceiling_kt',
 'policy_permissibility': 'dossier.field.policy_permissibility',
 'polymer_additive_compatibility': 'dossier.field.polymer_additive_compatibility',
 'portfolio': 'dossier.field.portfolio',
 'positive': 'dossier.field.positive',
 'positive_years': 'dossier.field.positive_years',
 'post_entry_capacity_to_downside_demand': 'dossier.field.post_entry_capacity_to_downside_demand',
 'probability_adjusted_committed_demand_kt': 'dossier.field.probability_adjusted_committed_demand_kt',
 'probability_adjusted_demand_addition': 'dossier.field.probability_adjusted_demand_addition',
 'process_family': 'dossier.field.process_family',
 'process_route': 'dossier.field.process_route',
 'producers': 'dossier.field.producers',
 'profile_hard_gates': 'dossier.field.profile_hard_gates',
 'public_note': 'dossier.field.public_note',
 'public_snapshot_id': 'dossier.field.public_snapshot_id',
 'published_coating_range_g_m2': 'dossier.field.published_coating_range_g_m2',
 'published_standards': 'dossier.field.published_standards',
 'q1_incumbent_meets_specification_without_capital': 'dossier.field.q1_incumbent_meets_specification_without_capital',
 'q2_missing_capabilities': 'dossier.field.q2_missing_capabilities',
 'q3_brownfield_versus_greenfield': 'dossier.field.q3_brownfield_versus_greenfield',
 'q4_downside_demand_supports_incumbent_and_new_entrant': 'dossier.field.q4_downside_demand_supports_incumbent_and_new_entrant',
 'q5_new_entry_displaces_efficient_domestic_production': 'dossier.field.q5_new_entry_displaces_efficient_domestic_production',
 'q6_technology_jv_superior_to_expansion_or_greenfield': 'dossier.field.q6_technology_jv_superior_to_expansion_or_greenfield',
 'qa_lab_metrology': 'executive.field.qa_lab_metrology',
 'qualification_share': 'dossier.field.qualification_share',
 'qualified_available_kt': 'dossier.field.qualified_available_kt',
 'qualifying_signal_count': 'dossier.field.qualifying_signal_count',
 'quantity': 'dossier.field.quantity',
 'quantity_cagr': 'dossier.field.quantity_cagr',
 'quantity_comparable': 'dossier.field.quantity_comparable',
 'quantity_contribution_share': 'dossier.field.quantity_contribution_share',
 'quantity_kt': 'dossier.field.quantity_kt',
 'quantity_share': 'dossier.field.quantity_share',
 'ratio_basis': 'dossier.field.ratio_basis',
 'ratio_reason': 'dossier.field.ratio_reason',
 'ratio_status': 'dossier.field.ratio_status',
 'real_decision_unchanged_after_simulation': 'dossier.field.real_decision_unchanged_after_simulation',
 'real_decision_uses_public_only': 'dossier.field.real_decision_uses_public_only',
 'reason': 'dossier.field.reason',
 'reexports_kt': 'dossier.field.reexports_kt',
 'reexports_separated': 'dossier.field.reexports_separated',
 'resilience_value': 'dossier.field.resilience_value',
 'resolves_binding_constraint': 'dossier.field.resolves_binding_constraint',
 'resource_environment': 'dossier.field.resource_environment',
 'result': 'dossier.field.result',
 'retained_import_penetration': 'dossier.field.retained_import_penetration',
 'retained_import_share_of_apparent_consumption': 'dossier.field.retained_import_share_of_apparent_consumption',
 'retained_imports_kt': 'dossier.field.retained_imports_kt',
 'risk_allowance': 'dossier.field.risk_allowance',
 'route_change_probability': 'dossier.field.route_change_probability',
 'route_code': 'dossier.field.route_code',
 'route_effect': 'dossier.field.route_effect',
 'rule_id': 'dossier.field.rule_id',
 'same_process_family': 'dossier.field.same_process_family',
 'scenario_id': 'dossier.field.scenario_id',
 'scenario_reconciliation': 'dossier.field.scenario_reconciliation',
 'schedule_months': 'dossier.field.schedule_months',
 'segment': 'dossier.field.segment',
 'shortage_denominator': 'dossier.field.shortage_denominator',
 'shortage_ratio': 'dossier.field.shortage_ratio',
 'signal_type': 'dossier.field.signal_type',
 'skills_market_integration': 'executive.field.skills_market_integration',
 'small_high_uv_observation': 'dossier.field.small_high_uv_observation',
 'source': 'dossier.field.source',
 'source_evidence_id': 'dossier.field.source_evidence_id',
 'source_evidence_ids': 'dossier.field.source_evidence_ids',
 'source_id': 'dossier.field.source_id',
 'specification_adjusted_gap_kt': 'dossier.field.specification_adjusted_gap_kt',
 'specification_equivalence': 'dossier.field.specification_equivalence',
 'standard': 'dossier.field.standard',
 'state': 'dossier.field.state',
 'status': 'dossier.field.status',
 'substrate_range': 'dossier.field.substrate_range',
 'sum_quantity_kt': 'dossier.field.sum_quantity_kt',
 'sum_value_usd_m': 'dossier.field.sum_value_usd_m',
 'sunset_date': 'dossier.field.sunset_date',
 'support_instrument': 'dossier.field.support_instrument',
 'support_required': 'dossier.field.support_required',
 'supported_irr': 'dossier.field.supported_irr',
 'supported_npv_m': 'dossier.field.supported_npv_m',
 'surface_treatment': 'dossier.field.surface_treatment',
 'sustained_period': 'dossier.field.sustained_period',
 'synthetic_isolation': 'dossier.field.synthetic_isolation',
 'target_spec_demand_kt': 'dossier.field.target_spec_demand_kt',
 'temper': 'dossier.field.temper',
 'thickness_mm': 'dossier.field.thickness_mm',
 'thickness_um': 'dossier.field.thickness_um',
 'threshold': 'dossier.field.threshold',
 'tin_coating_g_m2': 'dossier.field.tin_coating_g_m2',
 'to_year': 'dossier.field.to_year',
 'tooling': 'dossier.field.tooling',
 'top_two_share': 'dossier.field.top_two_share',
 'top_two_value_share': 'dossier.field.top_two_value_share',
 'total_observed_nameplate_tpy': 'dossier.field.total_observed_nameplate_tpy',
 'unavailable_inputs': 'dossier.field.unavailable_inputs',
 'unavailable_reasons': 'dossier.field.unavailable_reasons',
 'unit_key': 'dossier.field.unit_key',
 'unit_value_usd_t': 'dossier.field.unit_value_usd_t',
 'unknown_penalty_lambda': 'dossier.field.unknown_penalty_lambda',
 'unknown_weight': 'dossier.field.unknown_weight',
 'unresolved_hard_gates': 'dossier.field.unresolved_hard_gates',
 'unsupported_irr': 'dossier.field.unsupported_irr',
 'unsupported_npv_m': 'dossier.field.unsupported_npv_m',
 'utilities_ehs_permitting': 'executive.field.utilities_ehs_permitting',
 'uv_usd_t': 'dossier.field.uv_usd_t',
 'valid_coverage': 'dossier.field.valid_coverage',
 'valid_quantity_coverage': 'dossier.field.valid_quantity_coverage',
 'valid_value_coverage': 'dossier.field.valid_value_coverage',
 'valuation_route_code': 'dossier.field.valuation_route_code',
 'value': 'dossier.field.value',
 'value_difference_m_sar': 'dossier.field.value_difference_m_sar',
 'warning_fires': 'dossier.field.warning_fires',
 'warning_threshold': 'dossier.field.warning_threshold',
 'weighted_median_usd_t': 'dossier.field.weighted_median_usd_t',
 'weighted_q1_usd_t': 'dossier.field.weighted_q1_usd_t',
 'weighted_q3_usd_t': 'dossier.field.weighted_q3_usd_t',
 'width_mm': 'dossier.field.width_mm',
 'width_thickness_envelope': 'dossier.field.width_thickness_envelope',
 'year': 'dossier.field.year',
 'yield': 'dossier.field.yield'}
STATUS_LABELS = {'NOT_APPLICABLE': 'dossier.availability.not_applicable', 'NOT_CALCULABLE': 'dossier.availability.not_calculable', 'UNAVAILABLE': 'dossier.availability.unavailable', 'FAILS': 'executive.status.fails', 'NOT_SATISFIED': 'executive.status.not_satisfied', 'PASSES': 'executive.status.passes', 'SATISFIED': 'executive.status.satisfied'}
AVAILABILITY_REASONS = {'UNAVAILABLE': 'dossier.availability_reason.unavailable', 'NOT_CALCULABLE': 'dossier.availability_reason.not_calculable', 'NOT_APPLICABLE': 'dossier.availability_reason.not_applicable'}

class DossierHTML:
    def __init__(self, locale: str):
        if locale not in ('en','ar'):raise DossierIntegrityError('Dossier locale is invalid')
        self.locale=locale
        self.strings=ui_strings_bundle(locale)['strings']

    @staticmethod
    def e(value: Any) -> str:return escape(str(value),quote=True)

    def t(self,key: str,**values: Any) -> str:return self.e(ui_text(key,self.locale,**values))

    def technical_template(self,key: str,**values: Any) -> str:
        template=ui_text(key,self.locale,**{name:'{'+name+'}' for name in values})
        return ''.join(self.e(literal)+(self.technical(values[field]) if field else '')
                       for literal,field,_,_ in Formatter().parse(template))

    def technical(self,value: Any) -> str:
        return f'<bdi class="ltr-isolate technical-token" dir="ltr">{self.e(value)}</bdi>'

    def source(self,value: Any) -> str:
        # Original quotations remain attributed; ordinary chrome uses the catalogue.
        arabic=any('\u0600' <= char <= '\u06ff' for char in str(value))
        return f'<span class="source-language-island" lang="{"ar" if arabic else "en"}" dir="{"rtl" if arabic else "ltr"}">{self.e(value)}</span>'

    def caption(self) -> str:
        return f'<p class="dossier-source-caption">{self.t("dossier.source_original")}</p>' if self.locale=='ar' else ''

    def narrative(self,entry: dict,tag: str='span') -> str:
        if not isinstance(entry,dict) or not isinstance(entry.get('text'),str):
            raise DossierIntegrityError('Dossier localized narrative missing')
        segments=entry.get('segments')
        if segments is None:return f'<{tag}>{self.e(entry["text"])}</{tag}>'
        if not isinstance(segments,list):raise DossierIntegrityError('Dossier narrative segments invalid')
        text=''.join(self.technical(s['text']) if s.get('ltr_isolate') is True else self.e(s['text']) for s in segments)
        return f'<{tag}>{text}</{tag}>'

    def narrative_list(self,entries: list) -> str:
        return '<ul>'+(''.join('<li>'+self.narrative(item)+'</li>' for item in entries) or '<li>'+self.t('dossier.none')+'</li>')+'</ul>'

    def labels(self,labels: dict,css: str='branch-disclosure') -> str:
        return f'<div class="{css}">'+''.join(f'<strong lang="{locale}" dir="{"rtl" if locale=="ar" else "ltr"}">{self.e(labels[locale])}</strong>' for locale in ('ar','en') if locale in labels)+'</div>'

    def status(self,value: Any) -> str:
        key=STATUS_LABELS.get(str(value).upper())
        return self.t(key) if key else self.technical(value)

    def value(self,value: Any,*,source: bool=True) -> str:
        if value is None:return self.t('dossier.availability.unavailable')
        if isinstance(value,bool):return self.t('dossier.boolean.true' if value else 'dossier.boolean.false')
        if isinstance(value,(int,float)):return self.technical(format(value,'.12g'))
        if isinstance(value,str) and value in ('UNAVAILABLE','NOT_CALCULABLE','NOT_APPLICABLE'):
            return self.status(value)
        if isinstance(value,list):
            css=' class="dossier-values"' if all(not isinstance(item,(dict,list)) for item in value) else ''
            return '<ul'+css+'>'+(''.join('<li>'+self.value(item,source=source)+'</li>' for item in value) or '<li>'+self.t('dossier.none_recorded')+'</li>')+'</ul>'
        if isinstance(value,dict):return self.record(value)
        return self.source(value) if source else self.technical(value)

    def label(self,key: str) -> str:
        candidate=FIELD_LABELS.get(key)
        if candidate:return self.t(candidate)
        # Verbatim metric/source identifiers, never untranslated interface prose.
        return self.technical(key)

    def record(self,record: dict,exclude: tuple=()) -> str:
        rows=[]
        preface=''
        localized=record.get('localized_narrative')
        if isinstance(localized,dict) and self.locale in localized:
            preface=self.narrative(localized[self.locale],'p')
            exclude=(*exclude,'localized_narrative','localized_text','text','template_key','variant')
        for key,value in record.items():
            if key in exclude:continue
            css='record-group' if isinstance(value,dict) or isinstance(value,list) and any(isinstance(item,(dict,list)) for item in value) else 'record-scalar'
            rows.append('<div class="'+css+'"><dt>'+self.label(key)+'</dt><dd>'+self.value(value)+'</dd></div>')
        # A record is a definition list, not a recursively nested table. Each
        # nested record keeps the available line width in print and at 390px.
        return preface+'<dl class="dossier-record">'+''.join(rows)+'</dl>'

    def table(self,headers: list[str],rows: list,kind: str='record') -> str:
        header=''.join(f'<th scope="col">{self.t(key)}</th>' for key in headers)
        body=''.join('<tr>'+''.join(f'<{"th scope="+chr(34)+"row"+chr(34) if i==0 else "td"}>{cell}</{"th" if i==0 else "td"}>' for i,cell in enumerate(row))+'</tr>' for row in rows)
        return f'<table data-dossier-table="{kind}"><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>'

    def refs(self,ids: list[str]) -> str:
        return ' '.join(f'<a href="#evidence-{self.e(value)}">{self.technical(value)}</a>' for value in ids)

    def fields(self,fields: list[dict],source_prose: tuple[str,...]=()) -> str:
        rows=[]
        for field in fields:
            if field['availability']=='AVAILABLE':
                value=(self.caption() if field['key'] in source_prose else '')+self.value(field['value'])
            else:value=f'<span class="availability">{self.status(field["availability"])}</span><br><span class="field-reason">{self.t(AVAILABILITY_REASONS[field["availability"]])}</span>'
            unit=self.technical(field['unit']) if field['unit'] else ''
            rows.append((self.label(field['key']),value+(f'<br>{self.refs(field["evidence_ids"])}' if field['evidence_ids'] else ''),unit))
        return self.table(['dossier.source_path','dossier.value','dossier.unit'],rows,'fields')

    def source_link(self,url: Any) -> str:
        if not isinstance(url,str):return self.value(url)
        try:
            parts=urlsplit(url)
        except ValueError:
            return self.source(url)
        if parts.scheme in ('http','https') and parts.netloc:
            return f'<a class="source-url" href="{self.e(url)}" rel="noreferrer">{self.technical(url)}</a>'
        return self.source(url)


def render_dossier_html(dossier: dict, locale: str='en') -> str:
    h=DossierHTML(locale);blocks=dossier['blocks'];pack=dossier['evidence_pack']
    public=dossier['public_decision']
    narrative=dossier['localized_narrative'][locale]
    public_narrative=public['localized_narrative'][locale]
    disclosure=dossier.get('synthetic_disclosure')
    labels=disclosure['display_labels'] if disclosure else None
    identity=dossier['product_identity'];evidence=dossier['evidence_summary']
    name=identity['commercial_name_ar' if locale=='ar' else 'commercial_name_en']
    state=dossier['decision_state'];state_code=state or 'NO_CANDIDATE'
    state_text=h.t('state.'+state.lower()) if state else h.t('disposition.no_candidate')
    state_markup=h.technical(state_code) if locale=='en' and state else state_text+' '+h.technical(state_code)
    mode_key='mode.simulated' if dossier['mode']=='simulated' else 'mode.public'
    case=quote(dossier['opportunity_id'],safe='');query=urlencode({'mode':dossier['mode'],'locale':locale})
    return_url='/?'+urlencode({'opportunity':dossier['opportunity_id'],'mode':dossier['mode'],'locale':locale})+'#workspace'
    def section(name,body,*,heading=True):
        title=f'<h2>{h.t(SECTION_LABELS[name])}</h2>' if heading else ''
        return f'<section id="dossier-{name}" class="dossier-section">{title}{body}</section>'
    def branch(name):
        if blocks[name]['synthetic_flag']:
            return f'<p class="branch-label">{h.t("dossier.simulation_record")} · {h.technical(blocks[name]["scenario_id"])}</p>'+h.labels(blocks[name]['display_labels'])
        return f'<p class="branch-label">{h.t("dossier.public_record")}</p>'
    def group(title,content):return '<h3>'+h.t(title)+'</h3>'+content
    def intro(content):return '<div class="dossier-intro">'+content+'</div>'
    def record_group(title,record,*,caption=False):
        heading='<h3>'+h.t(title)+'</h3>'+(h.caption() if caption else '')
        if not isinstance(record,Mapping) or not record:return intro(heading+h.value(record))
        # These two consumers begin with one small boolean fact. Keep that
        # complete pair with its heading; leave the long remainder flowing.
        first,*rest=record.items()
        return intro(heading+h.record(dict([first])))+(h.record(dict(rest)) if rest else '')
    def conditions(entry,css):
        return f'<div class="{css}">'+group('dossier.decision_conditions',h.narrative_list(entry['conditions']))+group('dossier.kill_conditions',h.narrative_list(entry['kill_conditions']))+group('dossier.next_actions',h.narrative_list(entry.get('missing_facts',[])))+'</div>'
    def decision(entry):
        return h.narrative(entry['headline'],'h3')+h.narrative(entry['route_label'],'p')+h.narrative(entry['rationale'],'p')
    def mini(field):
        item=next(f for b in blocks.values() for f in b['fields'] if f['key']==field)
        value=h.value(item['value']) if item['availability']=='AVAILABLE' else h.status(item['availability'])
        return f'<div><dt>{h.label(field)}</dt><dd>{value} {h.technical(item["unit"]) if item["unit"] else ""}</dd></div>'
    def lead(key):
        entries=narrative.get(key,[])
        first=h.narrative(entries[0]) if entries else h.t('dossier.none_recorded')
        more=f' <a href="#dossier-conditions">{h.t("dossier.more",count=len(entries)-1)}</a>' if len(entries)>1 else ''
        return '<p><strong>'+h.t('dossier.decision_conditions' if key=='conditions' else 'dossier.kill_conditions')+'</strong><br>'+first+more+'</p>'
    public_summary=(f'<div class="summary-public"><strong>{h.t("dossier.public_conclusion")}</strong>'+h.narrative(public_narrative['headline'],'p')+'</div>') if disclosure else ''
    summary_refs=[row['evidence_id'] for row in pack['passports'] if row.get('synthetic_flag') is False][:2]
    contrary=[row['evidence_id'] for row in dossier['contradiction_register']['public']]
    evidence_groups=f'<p class="summary-evidence">{h.t("evidence.title")}: {h.refs(summary_refs)}</p>'
    if contrary:evidence_groups+=f'<p class="summary-evidence">{h.t("dossier.public_contradictions")}: {h.refs(contrary)}</p>'
    summary=f'''<section class="dossier-summary" id="decision-summary">
<p class="eyebrow">{h.t('dossier.summary')}</p><div class="state">{state_markup}</div>
<section class="decision-narrative">{h.narrative(narrative['headline'],'h1')}{h.narrative(narrative['rationale'],'p')}
<div class="meta">{h.technical(dossier['opportunity_id'])} · {h.narrative(narrative['route_label'])} · {h.t('dossier.mode')}: {h.t(mode_key)}</div></section>
{h.labels(labels,'warning') if labels else ''}
<div class="summary-identity"><strong>{h.e(name)}</strong><br>{h.technical('HS '+identity['hs_revision']+' / '+identity['hs6'])}</div>
{public_summary}<dl class="summary-metrics">{''.join(mini(key) for key in ('target_spec_demand_kt','effective_qualified_capacity_kt','d_star','minimum_effective_support_m'))}</dl>
<div class="summary-conditions">{lead('conditions')}{lead('kill_conditions')}</div>
{evidence_groups}
<p class="summary-date">{h.t('dossier.snapshot')}: {h.technical(evidence['snapshot_id'])} · {h.t('dossier.as_of')}: {h.technical(evidence['as_of_date'])}</p>
</section>'''
    # The complete public conclusion is retained independently of the active branch.
    body=group('dossier.public_conclusion',decision(public_narrative)+conditions(public_narrative,'public-conditions')) if disclosure else ''
    body+=group('dossier.product_identity',h.fields(blocks['identity']['fields'],('application_boundary','name','application')))
    body+=group('dossier.concordance',h.status(pack['revision_concordance']['availability']))
    body+=group('dossier.source_spans',h.status(pack['specification_source_spans']['availability']))
    pages=[section('identity',branch('identity')+body)]
    demand=blocks['demand'];records=demand['records']
    body=group('dossier.demand_conclusion','<p>'+h.t('dossier.imports_note')+'</p>'+h.fields(demand['fields']))
    trade_rows=[(h.technical(row['year']),h.value(row.get('imports_usd_m')),h.value(row.get('imports_kt'))) for row in records['trade']]
    body+=h.table(['trade.year','trade.value','trade.quantity'],trade_rows,'trade')
    for key,label in [('trade_quality','dossier.trade_quality'),('domestic_flows','dossier.flows'),('supplier_metrics','dossier.supplier_metrics')]:
        body+=group(label,h.caption()+h.record(records[key] or {}))
    partner=dossier.get('partner_detail')
    if isinstance(partner,dict):
        if partner['state']=='PARTNER_DETAIL_OBSERVED':
            detail=h.technical_template('dossier.partner_detail_observed',source=partner.get('source_id','UNAVAILABLE'),rows=partner.get('observed_partner_rows','UNAVAILABLE'))
        elif partner['state']=='PARTNER_DETAIL_MISSING':
            detail=h.technical_template('dossier.partner_detail_missing',reason=partner.get('reason','UNAVAILABLE'),attempts=', '.join(partner.get('attempt_passport_ids',[])) or 'UNAVAILABLE')
        elif partner['state']=='PARTNER_TRADE_OBSERVED_ZERO':
            detail=h.technical_template('dossier.partner_detail_zero',source=partner.get('source_id','UNAVAILABLE'))
        else:raise DossierIntegrityError('Dossier partner detail state invalid')
        body+=group('dossier.partner_detail','<p>'+detail+'</p>'+h.record(partner))
    buyers=pack['scenario_inputs'].get('buyer_allocation')
    if buyers:body+=h.labels(buyers['display_labels'])+h.caption()+h.record(buyers['data'])
    pages.append(section('demand',branch('demand')+body))
    supply=blocks['supply'];rows=[]
    for producer in supply['records']['producers']:
        details=h.record(producer,exclude=('producer','evidence_ids'))
        rows.append((h.source(producer['producer']),details+h.refs(producer.get('evidence_ids',[]))))
    producers=h.table(['dossier.producer','dossier.value'],rows,'producers')
    body=group('dossier.supply_conclusion','<p>'+h.t('dossier.observed_supply')+'</p>'+h.caption()+producers)
    if not rows:body+='<p>'+h.t('dossier.no_producers')+'</p>'
    signals=supply['records']['coarse_adjacency_signals']
    body+=group('dossier.coarse_adjacency_signals',(h.caption() if signals else '')+h.value(signals))
    body+=branch('supply')+h.fields(supply['fields'],('description',))
    pages.append(section('supply',body))
    gap=blocks['gap']['records'];gap_data=gap.get('gap_class') or {}
    body='<p>'+h.e(gap_data.get('localized_label',{}).get(locale,''))+'</p>'+h.fields(blocks['gap']['fields'])
    rows=[(h.technical(row['code']),h.status(row['status']),h.e(row['localized_narrative'][locale])+h.refs(row.get('evidence_ids',[]))) for row in gap['hard_exclusions']]
    body+=h.table(['dossier.source_reference','dossier.field.status','dossier.value'],rows,'exclusions')
    rows=[(h.technical(row['code']),h.status(row['status']),h.technical(row['reason_code'])+h.refs(row['evidence_ids'])) for row in gap['rejection_conditions']]
    body+=group('executive.step.false_positive_controls',h.table(['dossier.source_reference','dossier.field.status','dossier.value'],rows,'rejection-conditions'))
    pages.append(section('gap',branch('gap')+body))
    capability=blocks['capability']['records'];body=h.fields(blocks['capability']['fields'])
    rows=[(h.label(row['dimension']),h.technical(row['state']),h.technical(row['weight'])) for row in capability['dimensions']]
    body+=h.table(['dossier.source_path','dossier.field.state','dossier.field.weight'],rows,'capability')
    body+=(h.caption() if capability['unresolved_hard_gates'] or capability['known_hard_gate_failures'] else '')+h.record({'profile_hard_gates':capability['profile_hard_gates'],'unresolved_hard_gates':capability['unresolved_hard_gates'],'known_hard_gate_failures':capability['known_hard_gate_failures']})
    def routes(rows,kind):
        output=[]
        for route in rows:
            start='<h3>'+h.t('executive.route.'+str(route['route_code']))+'</h3><p>'+h.status(route['status'])+'</p>'
            start+=h.table(['dossier.source_path','dossier.value'],[(h.label(key),h.status(route.get(key))) for key in ('feasibility','resolves_binding_constraint','additionality','policy_permissibility')])
            detail=h.record(route.get('economics') or {})
            blocker=route['precedence']['blocked_by_lower_route']
            precedence=h.t('executive.ui.not_blocked') if blocker is None else h.t('executive.route.'+str(blocker))
            detail+='<p><strong>'+h.t('dossier.field.precedence')+'</strong>: '+precedence+'</p>'
            detail+=h.record({'incremental_national_value_m_sar':route.get('incremental_national_value_m_sar')})
            detail+=h.value(route.get('competition'))
            detail+='<ul>'+''.join('<li>'+h.e(value)+'</li>' for value in route.get('localized_reasons',{}).get(locale,[]))+'</ul>'
            detail+=h.refs([e for e in route.get('evidence_ids',[]) if e in {p['evidence_id'] for p in pack['passports']}])
            external=[e for e in route.get('evidence_ids',[]) if e not in {p['evidence_id'] for p in pack['passports']}]
            if external:detail+='<p>'+h.t('dossier.external_dependency')+'</p>'+h.value(external,source=False)
            output.append('<article class="route-record">'+intro(start)+detail+'</article>')
        return '<div data-dossier-records="'+kind+'">'+''.join(output)+'</div>'
    body+=routes(capability['routes'],'routes')
    if disclosure:body+=group('dossier.public_routes',routes(capability['public_routes'],'public-routes'))
    counterfactual=dossier.get('counterfactual')
    q3=counterfactual.get('q3_brownfield_versus_greenfield') if isinstance(counterfactual,Mapping) else None
    alternative=q3.get('greenfield_alternative') if isinstance(q3,Mapping) else None
    body+=record_group('dossier.counterfactual',counterfactual,caption=bool(alternative and alternative!='UNAVAILABLE'))
    pages.append(section('capability',branch('capability')+body))
    body=h.fields(blocks['economics']['fields'])+group('dossier.national_value',h.value(blocks['economics']['records']['national_value']))
    inputs=pack['scenario_inputs'].get('economics')
    if inputs:
        body+=h.labels(inputs['display_labels'])+h.caption()+h.record(inputs['data'])+h.refs(inputs['evidence_ids'])
    route_inputs=pack['scenario_inputs'].get('route_evidence')
    if route_inputs:body+=group('dossier.cash_flows',h.caption()+h.value(route_inputs['data']))+h.refs(route_inputs['evidence_ids'])
    pages.append(section('economics',branch('economics')+body))
    assessment=blocks['competition']['records']['assessment']
    original_assessment=bool(assessment and (assessment.get('finding') or assessment.get('note') or isinstance(assessment.get('concentration_before_after'),dict) and assessment['concentration_before_after'].get('note')))
    body=h.fields(blocks['competition']['fields'])+(h.caption() if original_assessment else '')+h.value(assessment)+'<p>'+h.t('dossier.authorization_note')+'</p>'
    pages.append(section('competition',branch('competition')+body))
    body=''
    for synthetic in (False,True):
        rules=[r for r in blocks['ledger']['records']['rules'] if (r.get('synthetic_flag') is True)==synthetic]
        if not rules:continue
        rows=[]
        for rule in rules:
            local=rule['localized'][locale]
            detail=h.narrative(local['decision_effect'],'p')
            detail+=h.caption()+h.record(rule.get('metrics',{}))
            executed=h.t('execution.'+rule['execution'].lower())
            fired=h.t('fire.yes' if rule['fired'] is True else 'fire.no' if rule['fired'] is False else 'fire.na')
            start=group('dossier.simulated_ledger',h.labels(labels)) if synthetic and not rows else ''
            start+='<h3>'+h.technical(rule['rule_id'])+' · '+h.narrative(local['name'])+'</h3><p>'+executed+' · '+fired+'</p>'+h.narrative(local['result'],'p')
            rows.append('<article class="rule-record">'+intro(start)+detail+'</article>')
        body+='<div data-dossier-records="rules">'+''.join(rows)+'</div>'
    pages.append(section('ledger',body))
    start='<h2>'+h.t(SECTION_LABELS['evidence'])+'</h2><p>'+h.t('dossier.evidence_counts',public=evidence['public_records'],synthetic=evidence['synthetic_records'])+'</p>'
    contradictions=dossier['contradiction_register']
    start+='<h3>'+h.t('dossier.contradiction_register')+'</h3>'
    body='<div class="contradiction-register">'
    for key,label in [('public','dossier.public_contradictions'),('synthetic','dossier.synthetic_contradictions')]:
        rows=contradictions[key]
        rendered=['<p>'+h.refs([r['evidence_id']])+': '+h.source(r['contradiction'])+'</p>' for r in rows]
        if not rows:rendered=['<p>'+h.t('dossier.synthetic_not_applicable' if key=='synthetic' and not disclosure else 'dossier.no_public_contradictions' if key=='public' else 'dossier.no_synthetic_contradictions')+'</p>']
        heading='<h3>'+h.t(label)+'</h3>'+(h.caption() if rows else '')
        body+=intro(start+heading+rendered[0])+''.join(rendered[1:]) if key=='public' else heading+''.join(rendered)
    body+='</div>'
    if not pack['passports']:body+='<p>'+h.t('dossier.no_passports')+'</p>'
    for passport in pack['passports']:
        body+=f'<article class="passport" id="evidence-{h.e(passport["evidence_id"])}"><h3>{h.technical(passport["evidence_id"])}</h3>'
        if passport['synthetic_flag']:body+=h.labels(passport['display_labels'])
        body+=h.caption()+'<p class="passport-title">'+h.source(passport.get('title',passport['evidence_id']))+'</p>'
        rows=[]
        for key,label in [('source','evidence.source'),('evidence_class','evidence.class'),('status','evidence.status'),('period','dossier.source_period'),('retrieved_at','dossier.retrieval_date'),('reviewer_status','dossier.reviewer_status'),('transformation','dossier.transformation'),('supports','dossier.supports'),('contradiction','dossier.contradiction_register')]:
            rows.append((h.t(label),h.value(passport.get(key))))
        if 'url' in passport:rows.append((h.t('dossier.source_reference'),h.source_link(passport['url'])))
        for key in ('document_id','page','line','source_span'):
            if key in passport:rows.append((h.label(key),h.value(passport[key])))
        body+=h.table(['dossier.source_path','dossier.value'],rows,'passport')+'</article>'
    for dep in pack['external_dependencies']:body+='<p>'+h.t('dossier.external_dependency')+' '+h.technical(dep['evidence_id'])+'</p>'
    pages.append(section('evidence',body,heading=False))
    body='<div class="decision-conditions">'+group('dossier.decision_conditions',h.narrative_list(narrative['conditions']))+'</div>'
    body+='<div class="kill-conditions">'+group('dossier.kill_conditions',h.narrative_list(narrative['kill_conditions']))+'</div>'
    body+='<div class="next-actions">'+group('dossier.next_actions',h.narrative_list(narrative.get('missing_facts',[])))+'</div>'
    if 'evsi' in blocks['conditions']['records']:body+=h.fields(blocks['conditions']['fields'])+h.caption()+h.value(blocks['conditions']['records']['evsi'])
    body+=group('dossier.history','<p>'+h.t('dossier.none_recorded')+'</p>')
    pages.append(section('conditions',branch('conditions')+body))
    authority=evidence['authority']
    authority_rows=[(h.t('integrity.methodology'),h.technical(authority['methodology']['file'])+'<br>'+h.technical(authority['methodology']['sha256'])),(h.t('integrity.project'),h.technical(authority['project_version']))]
    for key in ('thresholds','sector_profiles','evidence_policy','ui_strings'):
        authority_rows.append((h.t('integrity.'+key),h.technical(authority['config_versions'][key])))
    body=group('dossier.authority',h.table(['dossier.source_reference','dossier.value'],authority_rows))
    if evidence.get('selection'):body+='<p class="selection-reference">'+h.t('dossier.selection_reference',**{key:evidence['selection'][key] for key in ('selection_id','rule_version','profile')})+'<br>'+h.technical(evidence['selection']['reference'])+'</p>'
    integrity=evidence['integrity']
    if dossier['mode']=='public':
        body+=intro(group('dossier.evidence_boundary',h.record(integrity)))
    else:
        terminal_keys=('latest_imports_usd_m','latest_imports_kt','real_decision_unchanged_after_simulation','ground_truth_backtest')
        flowing={key:value for key,value in integrity.items() if key not in terminal_keys}
        terminal={key:value for key,value in integrity.items() if key in terminal_keys}
        body+=record_group('dossier.evidence_boundary',flowing,caption=bool(integrity.get('scenario_reconciliation')))
        body+=intro(h.record(terminal))
    pages.append(section('authority',body))
    toc='<nav class="dossier-contents" aria-label="'+h.t('dossier.contents')+'"><h2>'+h.t('dossier.contents')+'</h2><ol>'+''.join('<li><a href="#dossier-'+name+'">'+h.t(SECTION_LABELS[name])+'</a></li>' for name in SECTIONS)+'</ol></nav>'
    styles=_dossier_styles()
    if labels:
        footer_content=_css_string(labels['ar']+'\n'+labels['en'])
        styles+='@media print { @page { @bottom-center { content: '+footer_content+'; } } }'
    title=h.t('dossier.document_title',state=ui_state(dossier['decision_state'],locale))
    return f'''<!doctype html>
<html lang="{locale}" dir="{'rtl' if locale=='ar' else 'ltr'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>{styles}</style><script type="module" src="/static/modules/dossier-actions.js"></script></head>
<body class="dossier-body"><div class="dossier-toolbar"><span>{h.t(mode_key)}</span><button type="button" data-dossier-print>{h.t('dossier.print')}</button><a href="/api/opportunities/{case}/dossier?{h.e(query)}" download="{case}-{dossier['mode']}.json">{h.t('dossier.download_json')}</a><a data-dossier-return href="{h.e(return_url)}">{h.t('dossier.return')}</a><p>{h.t('dossier.print_note')}</p></div>
<main class="page" aria-label="{h.t('dossier.print_aria')}">{summary}<div class="dossier-appendix">{toc}{''.join(pages)}</div></main></body></html>'''


def ui_state(state,locale):
    from .config import ui_text
    return ui_text('state.'+state.lower() if state else 'disposition.no_candidate',locale)
