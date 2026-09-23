import { NODE_LABEL_KEYS } from "./labels.js";
import { elementReferences } from "./model.js";

function evidenceRows(analysis) {
  return Array.isArray(analysis?.evidence) ? analysis.evidence : [];
}

function matchingRecords(analysis, references) {
  const opportunityId = analysis?.opportunity?.id;
  return evidenceRows(analysis)
    .filter((row) => references.includes(row.evidence_id))
    .map((record) => ({ opportunityId, record }));
}

export async function resolveElementEvidence({
  payload,
  element,
  analysis,
  opportunities,
  mode,
  fetchAnalysis,
  cache,
}) {
  const references = elementReferences(payload, element);
  const records = matchingRecords(analysis, references);
  const visibleProducts = payload.nodes
    .filter((node) => NODE_LABEL_KEYS[node.label] === "graph.node.product")
    .map((node) => node.id)
    .filter((identity) => identity !== analysis.opportunity.id)
    .filter((identity) => opportunities.some((row) => row.id === identity));
  for (const identity of visibleProducts) {
    const key = `${mode}|${identity}`;
    let related = cache[key];
    if (!related) {
      related = await fetchAnalysis(identity, mode);
      if (related?.opportunity?.id !== identity || related?.mode !== mode) {
        throw new Error("GRAPH_EVIDENCE_CONTEXT_INVALID");
      }
      cache[key] = related;
    }
    records.push(...matchingRecords(related, references));
  }
  const deduplicated = [];
  const seen = new Set();
  for (const row of records) {
    const key = `${row.opportunityId}|${row.record.evidence_id}`;
    if (!seen.has(key)) {
      seen.add(key);
      deduplicated.push(row);
    }
  }
  const resolved = new Set(deduplicated.map((row) => row.record.evidence_id));
  const drilldown = payload.drilldown.find((row) => row.element_id === element.id);
  return {
    records: deduplicated,
    unresolved: references.filter((identity) => !resolved.has(identity)),
    documentAddresses: Array.isArray(drilldown?.document_addresses)
      ? drilldown.document_addresses : [],
  };
}
