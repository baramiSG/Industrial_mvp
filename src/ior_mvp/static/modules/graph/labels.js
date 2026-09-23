import { t } from "../i18n.js";

export const NODE_LABEL_KEYS = Object.freeze({
  Product: "graph.node.product",
  TariffLine: "graph.node.tariffline",
  Specification: "graph.node.specification",
  Application: "graph.node.application",
  Plant: "graph.node.plant",
  ProductionLine: "graph.node.productionline",
  Process: "graph.node.process",
  Equipment: "graph.node.equipment",
  Capability: "graph.node.capability",
  Standard: "graph.node.standard",
  Certification: "graph.node.certification",
  Input: "graph.node.input",
  Technology: "graph.node.technology",
  Company: "graph.node.company",
  CustomerSegment: "graph.node.customersegment",
  Evidence: "graph.node.evidence",
  Scenario: "graph.node.scenario",
  Decision: "graph.node.decision",
  Intervention: "graph.node.intervention",
});

export const EDGE_LABEL_KEYS = Object.freeze({
  CLASSIFIED_AS: "graph.edge.classified_as",
  REQUIRES_SPECIFICATION: "graph.edge.requires_specification",
  USED_IN: "graph.edge.used_in",
  PRODUCED_BY: "graph.edge.produced_by",
  HAS_LINE: "graph.edge.has_line",
  USES_PROCESS: "graph.edge.uses_process",
  HAS_CAPABILITY: "graph.edge.has_capability",
  REQUIRES_INPUT: "graph.edge.requires_input",
  CERTIFIED_TO: "graph.edge.certified_to",
  QUALIFIED_FOR: "graph.edge.qualified_for",
  DEPENDS_ON: "graph.edge.depends_on",
  ADJACENT_TO: "graph.edge.adjacent_to",
  SUPPORTED_BY_EVIDENCE: "graph.edge.supported_by_evidence",
  CONSTRAINED_BY: "graph.edge.constrained_by",
  UNLOCKED_BY: "graph.edge.unlocked_by",
});

export const EXPLANATION_KEYS = Object.freeze({
  "view.adjacency.explanation": "graph.explanation.adjacency",
  "view.route_blocking.explanation": "graph.explanation.route_blocking",
  "view.shared_enabler.explanation": "graph.explanation.shared_enabler",
  "view.evidence_to_change.explanation": "graph.explanation.evidence_to_change",
});

export const FAILURE_KEYS = Object.freeze({
  NOT_CONFIGURED: "graph.failure.not_configured",
  DRIVER_NOT_INSTALLED: "graph.failure.driver_not_installed",
  CONNECTION_FAILED: "graph.failure.connection_failed",
  INSTANCE_MISMATCH: "graph.failure.instance_mismatch",
  PROJECTION_MISMATCH: "graph.failure.projection_mismatch",
});

export function nodeLabel(node, locale) {
  const localized = locale === "ar"
    ? (node.name_ar || node.name_en) : node.name_en;
  return localized || t(NODE_LABEL_KEYS[node.label]);
}

export function nodeKindLabel(node) {
  return t(NODE_LABEL_KEYS[node.label]);
}

export function edgeLabel(edge) {
  return t(EDGE_LABEL_KEYS[edge.type]);
}

export function explanationLabel(explanation) {
  return t(
    EXPLANATION_KEYS[explanation.catalogue_key],
    explanation.values || {},
  );
}

export function failureLabel(reasonCode) {
  return t(FAILURE_KEYS[reasonCode]);
}
