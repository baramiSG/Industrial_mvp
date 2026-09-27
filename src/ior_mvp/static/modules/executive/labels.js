import { t } from "../i18n.js";
import { escapeHtml, sourceCaption, sourceIsland, technicalToken as code } from "../dom.js";
import { state } from "../state.js";

export const STEP_IDS = Object.freeze([
  "SIGNAL", "FALSE_POSITIVE_CONTROLS", "PUBLIC_CONCLUSION",
  "MISSING_MINISTRY_FACTS", "SIMULATED_EVIDENCE", "ROUTE_COMPARISON",
  "INTERVENTION", "CONDITIONS_AND_KILL",
]);
export const VECTOR_IDS = Object.freeze([
  "MARKET_GAP", "STRATEGIC_RESILIENCE", "EXECUTION_FEASIBILITY", "EVIDENCE_CONFIDENCE",
]);
export const DATASET_IDS = Object.freeze([
  "IDENTITY_TARIFF", "TARGET_SPECIFICATION_DEMAND", "PRODUCER_CAPABILITY",
  "EFFECTIVE_CAPACITY_ALLOCATION", "RETAINED_FLOW", "ROUTE_ECONOMICS", "UNMAPPED",
]);

export function stepLabel(id) {
  if (!STEP_IDS.includes(id)) throw new Error("EXECUTIVE_STEP_INVALID");
  const keys = {
    SIGNAL: "executive.step.signal",
    FALSE_POSITIVE_CONTROLS: "executive.step.false_positive_controls",
    PUBLIC_CONCLUSION: "executive.step.public_conclusion",
    MISSING_MINISTRY_FACTS: "executive.step.missing_ministry_facts",
    SIMULATED_EVIDENCE: "executive.step.simulated_evidence",
    ROUTE_COMPARISON: "executive.step.route_comparison",
    INTERVENTION: "executive.step.intervention",
    CONDITIONS_AND_KILL: "executive.step.conditions_and_kill",
  };
  return t(keys[id]);
}

const KEYS = Object.freeze({
  "field": {"feedstock_chemistry": "executive.field.feedstock_chemistry", "core_process_route": "executive.field.core_process_route", "equipment_envelope": "executive.field.equipment_envelope", "finishing_spec_control": "executive.field.finishing_spec_control", "qa_lab_metrology": "executive.field.qa_lab_metrology", "certification_customer_qualification": "executive.field.certification_customer_qualification", "capacity_time_window": "executive.field.capacity_time_window", "utilities_ehs_permitting": "executive.field.utilities_ehs_permitting", "skills_market_integration": "executive.field.skills_market_integration", "product_identity": "executive.field.product_identity", "demand_at_required_specification": "executive.field.demand_at_required_specification", "domestic_supply_or_capability": "executive.field.domestic_supply_or_capability", "hard_regulatory_or_process_gate": "executive.field.hard_regulatory_or_process_gate"},
  "ui": {"sar_million": "executive.ui.sar_million", "route_probability": "executive.ui.route_probability", "back": "executive.ui.back", "next": "executive.ui.next", "first_case": "executive.ui.first_case", "snapshot": "executive.ui.snapshot", "shown_records": "executive.ui.shown_records", "capacity": "executive.ui.capacity", "effective_qualified_capacity_kt": "executive.ui.effective_qualified_capacity_kt", "target_spec_demand_kt": "executive.ui.target_spec_demand_kt", "specification_adjusted_gap_kt": "executive.ui.specification_adjusted_gap_kt", "used_blocks": "executive.ui.used_blocks", "hypothesis": "executive.ui.hypothesis", "competition_ratio": "executive.ui.competition_ratio", "comparison_threshold": "executive.ui.comparison_threshold", "public": "executive.ui.public", "simulated": "executive.ui.simulated", "public_boundary": "executive.ui.public_boundary", "simulation_boundary": "executive.ui.simulation_boundary", "route": "executive.ui.route", "confidence": "executive.ui.confidence", "vectors": "executive.ui.vectors", "vectors_note": "executive.ui.vectors_note", "detail": "executive.ui.detail", "sources": "executive.ui.sources", "close_sources": "executive.ui.close_sources", "case_needs": "executive.ui.case_needs", "no_sources": "executive.ui.no_sources", "source_unavailable": "executive.ui.source_unavailable", "retry": "executive.ui.retry", "error": "executive.ui.error", "not_found": "executive.ui.not_found", "empty": "executive.ui.empty", "locale_error": "executive.ui.locale_error", "no_simulation": "executive.ui.no_simulation", "signal_note": "executive.ui.signal_note", "route_note": "executive.ui.route_note", "dataset_note": "executive.ui.dataset_note", "loaded_cases": "executive.ui.loaded_cases", "screening_records": "executive.ui.screening_records", "evsi": "executive.ui.evsi", "evsi_note": "executive.ui.evsi_note", "available_cases": "executive.ui.available_cases", "unavailable_cases": "executive.ui.unavailable_cases", "total_evsi": "executive.ui.total_evsi", "next_fact": "executive.ui.next_fact", "conditions": "executive.ui.conditions", "kill": "executive.ui.kill", "scenario": "executive.ui.scenario", "class_if_confirmed": "executive.ui.class_if_confirmed", "actual_class": "executive.ui.actual_class", "seed_basis": "executive.ui.seed_basis", "graph": "executive.ui.graph", "graph_note": "executive.ui.graph_note", "precedence": "executive.ui.precedence", "not_blocked": "executive.ui.not_blocked", "reason": "executive.ui.reason", "integrity": "executive.ui.integrity", "affected": "executive.ui.affected", "exclusions": "executive.ui.exclusions", "missing": "executive.ui.missing", "all_evidence": "executive.ui.all_evidence"},
  "vector": {"MARKET_GAP": "executive.vector.market_gap", "STRATEGIC_RESILIENCE": "executive.vector.strategic_resilience", "EXECUTION_FEASIBILITY": "executive.vector.execution_feasibility", "EVIDENCE_CONFIDENCE": "executive.vector.evidence_confidence"},
  "dataset": {"IDENTITY_TARIFF": "executive.dataset.identity_tariff", "TARGET_SPECIFICATION_DEMAND": "executive.dataset.target_specification_demand", "PRODUCER_CAPABILITY": "executive.dataset.producer_capability", "EFFECTIVE_CAPACITY_ALLOCATION": "executive.dataset.effective_capacity_allocation", "RETAINED_FLOW": "executive.dataset.retained_flow", "ROUTE_ECONOMICS": "executive.dataset.route_economics", "UNMAPPED": "executive.dataset.unmapped"},
  "route": {"0": "executive.route.0", "1": "executive.route.1", "2": "executive.route.2", "3": "executive.route.3", "4": "executive.route.4", "5": "executive.route.5", "6": "executive.route.6", "7": "executive.route.7", "8": "executive.route.8"},
  "status": {"AVAILABLE": "executive.status.available", "UNAVAILABLE": "executive.status.unavailable", "NOT_CALCULABLE": "executive.status.not_calculable", "SUPPORTED": "executive.status.supported", "CONTRADICTED": "executive.status.contradicted", "UNRESOLVED": "executive.status.unresolved", "PASS": "executive.status.pass", "FAIL": "executive.status.fail", "PASSES": "executive.status.passes", "FAILS": "executive.status.fails", "SATISFIED": "executive.status.satisfied", "NOT_SATISFIED": "executive.status.not_satisfied", "UNDETERMINED": "executive.status.undetermined"},
  "value": {"gap_class": "executive.value.gap_class", "latest_imports_usd_m": "executive.value.latest_imports_usd_m", "secondary_gap_classes": "executive.value.secondary_gap_classes", "criticality_designation": "executive.value.criticality_designation", "route_publishable": "executive.value.route_publishable", "d_star": "executive.value.d_star", "unresolved_hard_gate_count": "executive.value.unresolved_hard_gate_count", "decision_confidence": "executive.value.decision_confidence", "unresolved_assessment_count": "executive.value.unresolved_assessment_count", "missing_fact_count": "executive.value.missing_fact_count", "fired_rule_ids": "executive.value.fired_rule_ids", "hard_exclusion_count": "executive.value.hard_exclusion_count", "r11_fired": "executive.value.r11_fired", "simulated_selected_route_code": "executive.value.simulated_selected_route_code", "simulated_unsupported_npv_m_sar": "executive.value.simulated_unsupported_npv_m_sar", "simulated_minimum_effective_support_m_sar": "executive.value.simulated_minimum_effective_support_m_sar", "simulated_incremental_national_value_m_sar": "executive.value.simulated_incremental_national_value_m_sar", "simulated_approximate_evsi_m_sar": "executive.value.simulated_approximate_evsi_m_sar", "feasibility": "executive.value.feasibility", "additionality": "executive.value.additionality", "competition": "executive.value.competition", "policy_permissibility": "executive.value.policy_permissibility", "resolves_binding_constraint": "executive.value.resolves_binding_constraint"},
  "code": {"false_or_measurement": "executive.code.false_or_measurement","evidence": "executive.code.evidence", "quantity": "executive.code.quantity", "quality": "executive.code.quality", "resilience": "executive.code.resilience", "timing": "executive.code.timing", "none": "executive.code.none", "cost": "executive.code.cost"},
});

export function label(kind, id) {
  const key = KEYS[kind]?.[id];
  if (!key) throw new Error("EXECUTIVE_LABEL_INVALID");
  return t(key);
}

export function policyLabels(labels) {
  if (!labels) return "";
  const order = state.locale === "ar" ? ["ar", "en"] : ["en", "ar"];
  return `<div class="synthetic-labels">${order.map((locale) => `<span lang="${locale}" dir="${locale === "ar" ? "rtl" : "ltr"}" class="${locale === "en" ? "source-language-island" : ""}">${escapeHtml(labels[locale])}</span>`).join("")}${sourceCaption()}</div>`;
}

function key(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

const MINISTRY_KEYS = Object.freeze({
  dataset: Object.freeze({
    application_tape: "ministry.dataset.application_tape",
    factory_customs: "ministry.dataset.factory_customs",
    factory_customs_attribution: "ministry.dataset.factory_customs_attribution",
    production_actuals: "ministry.dataset.production_actuals",
    registry: "ministry.dataset.registry",
    technical_enrichment: "ministry.dataset.technical_enrichment",
  }),
  effect: Object.freeze({
    factory_attribution: "ministry.effect.factory_attribution",
    in_scope_procurement_record: "ministry.effect.in_scope_procurement_record",
    capacity_availability_allocation: "ministry.effect.capacity_availability_allocation",
    identity_tariff_line: "ministry.effect.identity_tariff_line",
    line_level_production_or_producer_grade_matrix: "ministry.effect.line_level_production_or_producer_grade_matrix",
    qualification_profile_hard_gates: "ministry.effect.qualification_profile_hard_gates",
    re_export_origin_decomposition: "ministry.effect.re_export_origin_decomposition",
    route_economics: "ministry.effect.route_economics",
    target_specification_application: "ministry.effect.target_specification_application",
  }),
  field: Object.freeze({
    factory_attribution_link: "ministry.field.factory_attribution_link",
    in_scope_procurement_record: "ministry.field.in_scope_procurement_record",
  }),
  origin: Object.freeze({
    direct_record: "ministry.origin.direct_record",
    engineering_declaration: "ministry.origin.engineering_declaration",
    reviewed_inference: "ministry.origin.reviewed_inference",
    unknown: "ministry.origin.unknown",
  }),
  status: Object.freeze({
    conflicted: "ministry.status.conflicted",
    limitation_identified: "ministry.status.limitation_identified",
    not_established: "ministry.status.not_established",
    not_required: "ministry.status.not_required",
    supported: "ministry.status.supported",
  }),
  disposition: Object.freeze({
    not_established: "ministry.disposition.not_established",
    outside_target: "ministry.disposition.outside_target",
    pass_to_assessment: "ministry.disposition.pass_to_assessment",
    related_only: "ministry.disposition.related_only",
  }),
});
const RECORD_FIELDS = Object.freeze({
  admitted_hs6: "ministry.record.field.admitted_hs6",
  admitted_qualified_supply_kt: "ministry.record.field.admitted_qualified_supply_kt",
  country: "ministry.record.field.country",
  customer_qualification: "ministry.record.field.customer_qualification",
  dataset_kind: "ministry.record.field.dataset_kind",
  end: "ministry.record.field.end",
  equipment_model_id: "ministry.record.field.equipment_model_id",
  establishes_installation: "ministry.record.field.establishes_installation",
  operating_status_asserted_by_registry: "ministry.record.field.operating_status_asserted_by_registry",
  product_family: "ministry.record.field.product_family",
  production_kind: "ministry.record.field.production_kind",
  reason_code: "ministry.record.field.reason_code",
  reexport: "ministry.record.field.reexport",
  scope: "ministry.record.field.scope",
  stage: "ministry.record.field.stage",
  start: "ministry.record.field.start",
  substrate: "ministry.record.field.substrate",
  tooling_required: "ministry.record.field.tooling_required",
  transaction_id: "ministry.record.field.transaction_id",
  window: "ministry.record.field.window",
  window_result: "ministry.record.field.window_result",
});
const PP_FIELD_KEYS = Object.freeze({
  polymer_family: "ministry.item.polymer_family",
  manufacturing_scope: "ministry.item.manufacturing_scope",
  grade_family: "ministry.item.grade_family",
  additives_required: "ministry.item.additives_required",
});
export function ministryLabel(group, value) {
  const labelKey = MINISTRY_KEYS[group]?.[key(value)];
  if (!labelKey) throw new Error(`MINISTRY_LABEL_UNMAPPED:${group}:${value}`);
  return t(labelKey);
}

export function recordLabel(value) {
  return MINISTRY_KEYS.status[key(value)] || MINISTRY_KEYS.origin[key(value)] || null;
}

export function named(prefix, value) {
  if (prefix === "field") return `${fieldName(value)} · ${sourceIsland(value)}${sourceCaption()}`;
  const label = state.ui.strings[MINISTRY_KEYS[prefix]?.[key(value)]];
  return label ? `${escapeHtml(label)} · ${code(value)}` : code(value);
}

export function fieldName(field) {
  const pp = state.ui.strings[PP_FIELD_KEYS[field]];
  if (pp) return escapeHtml(pp);
  const recorded = state.ui.strings[RECORD_FIELDS[field]];
  if (recorded) return escapeHtml(recorded);
  for (const prefix of ["ministry.item.", "dossier.field.", "executive.field."]) {
    const label = state.ui.strings[prefix + field];
    if (label) return escapeHtml(label);
  }
  return `${sourceIsland(field)}${sourceCaption()}`;
}

export function capabilityMeanings() {
  return {
    0: t("executive.capability.state.0"), 1: t("executive.capability.state.1"),
    2: t("executive.capability.state.2"), 3: t("executive.capability.state.3"),
    U: t("executive.capability.state.u"),
  };
}

export function capabilityLegend(comparison = false) {
  const marker = comparison ? "data-comparison-capability-legend" : "data-capability-legend";
  return `<details ${marker}><summary>${escapeHtml(t("executive.capability.legend"))}</summary><dl>${Object.entries(capabilityMeanings()).map(([value, meaning]) => `<div><dt>${code(value)}</dt><dd data-capability-legend-state="${value}">${escapeHtml(meaning)}</dd></div>`).join("")}</dl><p>${escapeHtml(t("executive.capability.simulation_note"))}</p></details>`;
}
