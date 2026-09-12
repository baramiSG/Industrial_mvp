import { t } from "../i18n.js";

export const LABEL_KEYS = Object.freeze({
  disposition: {
    CANDIDATE: "disposition.candidate",
    NO_CANDIDATE: "disposition.no_candidate",
    SCREENED_OUT: "disposition.screened_out",
  },
  reason: {
    MATERIAL_TRIGGER_FIRED: "reason.material_trigger_fired",
    NON_MATERIAL_SIGNAL_ONLY: "reason.non_material_signal_only",
    HARD_EXCLUSION_SATISFIED: "reason.hard_exclusion_satisfied",
    GENERIC_CAPACITY_CONTRADICTED: "reason.generic_capacity_contradicted",
    IDENTITY_UNRESOLVED: "reason.identity_unresolved",
    NO_IMPORT_OBSERVATIONS: "reason.no_import_observations",
    NO_TRIGGER_FIRED: "reason.no_trigger_fired",
    NO_UNIVERSE_SNAPSHOT: "reason.no_universe_snapshot",
    LICENSE_UNRECORDED: "reason.license_unrecorded",
    CREDENTIAL_ABSENT: "reason.credential_absent",
    HTTP_ERROR: "reason.http_error",
    COVERAGE_INDETERMINATE: "reason.coverage_indeterminate",
    PARTNER_DETAIL_NOT_ACQUIRED: "reason.partner_detail_not_acquired",
    TARIFF_TREE_NOT_ACQUIRED: "reason.tariff_tree_not_acquired",
    PRODUCTION_AGGREGATES_NOT_ACQUIRED: "reason.production_aggregates_not_acquired",
    ENTITY_ARTIFACT_AVAILABLE: "reason.entity_artifact_available",
    D_STAR_NOT_ASSIGNED_AT_SCREENING: "reason.d_star_not_assigned_at_screening",
    PERSISTENCE_ONLY: "reason.persistence_only",
    ROUTE_CHANGING_EVIDENCE_UNRESOLVED: "reason.route_changing_evidence_unresolved",
    NO_SCREENING_SNAPSHOT: "reason.no_screening_snapshot",
  },
  queue: {
    robust_public_finding: "queue.robust_public_finding",
    incumbent_upgrade_investigation: "queue.incumbent_upgrade_investigation",
    resilience_case: "queue.resilience_case",
    likely_false_positive: "queue.likely_false_positive",
    high_evsi_evidence_investigation: "queue.high_evsi_evidence_investigation",
  },
  queueReason: {
    MULTIPLE_MATERIAL_SIGNALS: "queue_reason.multiple_material_signals",
    R9S_AND_OTHER_MATERIAL_TRIGGER: "queue_reason.r9s_and_other_material_trigger",
    SUPPLIER_CONCENTRATION_SIGNAL: "queue_reason.supplier_concentration_signal",
    SCREENING_WARNING: "queue_reason.screening_warning",
    R2_FULL_FIRED: "queue_reason.r2_full_fired",
    EVSI_NOT_CALCULABLE: "queue_reason.evsi_not_calculable",
    PERSISTENCE_ONLY: "queue_reason.persistence_only",
  },
  need: {
    "identity/tariff-line": "need.identity_tariff_line",
    "target specification/application": "need.target_specification_application",
    "line-level production or producer-grade matrix": "need.line_level_production_or_producer_grade_matrix",
    "re-export/origin decomposition": "need.re_export_origin_decomposition",
    "capacity/availability/allocation": "need.capacity_availability_allocation",
  },
  exclusion: {
    "EX-01_HETEROGENEOUS_RESIDUAL": "exclusion.ex-01_heterogeneous_residual",
    "EX-02_MARKET_BELOW_MES": "exclusion.ex-02_market_below_mes",
    "EX-03_UNSATISFIABLE_HARD_GATE": "exclusion.ex-03_unsatisfiable_hard_gate",
    "EX-04_IDLE_EQUIVALENT_CAPACITY": "exclusion.ex-04_idle_equivalent_capacity",
    "EX-05_TRANSITORY_OR_MEASUREMENT": "exclusion.ex-05_transitory_or_measurement",
    "EX-06_REDUNDANCY_OR_CROWD_OUT": "exclusion.ex-06_redundancy_or_crowd_out",
  },
  exclusionStatus: {
    SATISFIED: "exclusion_status.satisfied",
    NOT_SATISFIED: "exclusion_status.not_satisfied",
    NOT_CALCULABLE: "exclusion_status.not_calculable",
  },
  exclusionReason: {
    EXCLUSION_SATISFIED: "exclusion_reason.exclusion_satisfied",
    EXCLUSION_NOT_SATISFIED: "exclusion_reason.exclusion_not_satisfied",
    EXCLUSION_INPUT_UNAVAILABLE: "exclusion_reason.exclusion_input_unavailable",
  },
  continuityStatus: {
    CONTINUOUS: "continuity_status.continuous",
    GAP_YEARS: "continuity_status.gap_years",
    REVISION_CHANGE_IN_WINDOW: "continuity_status.revision_change_in_window",
  },
  continuityPattern: {
    NONE: "continuity_pattern.none",
    GAP_YEARS: "continuity_pattern.gap_years",
    ABSENT_BEFORE_REVISION_CHANGE: "continuity_pattern.absent_before_revision_change",
    ABSENT_AFTER_REVISION_CHANGE: "continuity_pattern.absent_after_revision_change",
  },
  status: {
    AVAILABLE: "screening.status.available",
    PARTIAL: "screening.status.partial",
    UNAVAILABLE: "screening.status.unavailable",
    NOT_CALCULABLE: "screening.status.not_calculable",
    CALCULATED: "screening.status.calculated",
    COMPLETE: "screening.status.complete",
  },
  metric: {
    imports_usd_m_latest: "screening.metric.imports_usd_m_latest",
    quantity_cagr: "screening.metric.quantity_cagr",
    export_import_value_ratio: "screening.metric.export_import_value_ratio",
    largest_supplier_share_value: "screening.metric.largest_supplier_share_value",
    qualifying_signal_count: "screening.metric.qualifying_signal_count",
    fired_signal_count: "screening.metric.fired_signal_count",
    hhi_value: "screening.metric.hhi_value",
    delta_ln_value: "screening.metric.delta_ln_value",
  },
  flow: {
    imports: "screening.flow.imports",
    exports: "screening.flow.exports",
  },
});

export function screeningLabel(vocabulary, code) {
  const key = LABEL_KEYS[vocabulary]?.[code];
  if (!key) {
    throw new Error(`UI_CATALOGUE_KEY_MISSING:${vocabulary}:${code}`);
  }
  return t(key);
}
