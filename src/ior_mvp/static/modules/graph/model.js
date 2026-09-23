import { EDGE_LABEL_KEYS, FAILURE_KEYS, NODE_LABEL_KEYS } from "./labels.js";

export const VIEW_IDS = Object.freeze([
  "adjacency",
  "route_blocking",
  "shared_enabler",
  "evidence_to_change",
]);

function object(value) {
  return value && typeof value === "object" && !Array.isArray(value);
}

function nonempty(value) {
  return typeof value === "string" && value.length > 0;
}

function unique(values) {
  return new Set(values).size === values.length;
}

function validProvenance(value) {
  return object(value)
    && nonempty(value.evidence_id)
    && nonempty(value.as_of)
    && ["A", "B", "C", "D", "E"].includes(value.evidence_class)
    && typeof value.synthetic_flag === "boolean"
    && nonempty(value.scenario_id);
}

export function validateGraphCatalogue(payload) {
  if (!object(payload) || !object(payload.metadata) || !Array.isArray(payload.views)) {
    throw new Error("GRAPH_CATALOGUE_INVALID");
  }
  if (payload.metadata.version !== "1.0.0") {
    throw new Error("GRAPH_CATALOGUE_INVALID");
  }
  if (payload.views.map((row) => row?.view_id).join("|") !== VIEW_IDS.join("|")) {
    throw new Error("GRAPH_CATALOGUE_INVALID");
  }
  for (const row of payload.views) {
    if (!object(row.label) || !object(row.description)
      || !nonempty(row.label.en) || !nonempty(row.label.ar)
      || !nonempty(row.description.en) || !nonempty(row.description.ar)) {
      throw new Error("GRAPH_CATALOGUE_INVALID");
    }
  }
  return payload;
}

export function validateGraphPayload(payload, context) {
  if (!object(payload)
    || payload.view_id !== context.viewId
    || payload.opportunity_id !== context.opportunityId
    || payload.mode !== context.mode
    || !["AVAILABLE", "GRAPH_UNAVAILABLE"].includes(payload.graph_status)
    || !Array.isArray(payload.nodes)
    || !Array.isArray(payload.edges)
    || !Array.isArray(payload.drilldown)) {
    throw new Error("GRAPH_RESPONSE_INVALID");
  }
  if (payload.graph_status === "GRAPH_UNAVAILABLE") {
    if (!Object.hasOwn(FAILURE_KEYS, payload.reason_code)
      || payload.nodes.length || payload.edges.length) {
      throw new Error("GRAPH_RESPONSE_INVALID");
    }
    return payload;
  }
  if (payload.reason_code !== null || !nonempty(payload.projection_id)) {
    throw new Error("GRAPH_RESPONSE_INVALID");
  }
  const nodeIds = payload.nodes.map((node) => node?.id);
  const edgeIds = payload.edges.map((edge) => edge?.id);
  if (!nodeIds.every(nonempty) || !edgeIds.every(nonempty)
    || !unique(nodeIds) || !unique(edgeIds)) {
    throw new Error("GRAPH_RESPONSE_INVALID");
  }
  for (const node of payload.nodes) {
    if (!Object.hasOwn(NODE_LABEL_KEYS, node.label)
      || !object(node.properties) || !validProvenance(node.provenance)
      || typeof node.derived !== "boolean") {
      throw new Error("GRAPH_RESPONSE_INVALID");
    }
  }
  for (const edge of payload.edges) {
    if (!Object.hasOwn(EDGE_LABEL_KEYS, edge.type)
      || !nodeIds.includes(edge.source) || !nodeIds.includes(edge.target)
      || !object(edge.properties) || !validProvenance(edge.provenance)
      || typeof edge.derived !== "boolean") {
      throw new Error("GRAPH_RESPONSE_INVALID");
    }
  }
  const elements = [...payload.nodes, ...payload.edges];
  if (context.mode === "public" && elements.some(
    (row) => row.provenance.synthetic_flag === true,
  )) {
    throw new Error("GRAPH_PUBLIC_SYNTHETIC_REJECTED");
  }
  if (payload.synthetic_flag !== elements.some(
    (row) => row.provenance.synthetic_flag === true,
  )) {
    throw new Error("GRAPH_RESPONSE_INVALID");
  }
  if (payload.drilldown.some(
    (row) => !object(row) || ![...nodeIds, ...edgeIds].includes(row.element_id)
      || !Array.isArray(row.evidence_ids) || !Array.isArray(row.document_addresses),
  )) {
    throw new Error("GRAPH_RESPONSE_INVALID");
  }
  return payload;
}

export function graphElement(payload, kind, identity) {
  const rows = kind === "edge" ? payload?.edges : payload?.nodes;
  return rows?.find((row) => row.id === identity) || null;
}

export function elementReferences(payload, element) {
  const drilldown = payload.drilldown.find((row) => row.element_id === element.id);
  return [...new Set([
    element.provenance?.evidence_id,
    ...(Array.isArray(element.properties?.evidence_ids)
      ? element.properties.evidence_ids : []),
    ...(Array.isArray(drilldown?.evidence_ids) ? drilldown.evidence_ids : []),
  ].filter(nonempty))].sort();
}
