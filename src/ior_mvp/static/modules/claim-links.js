import { escapeHtml as esc, technicalToken as code } from "./dom.js";
import { label } from "./executive/labels.js";

export function evidenceAnchor(branch, opportunityId, evidenceId) {
  return "claim-evidence-" + [branch, opportunityId, evidenceId].map((value) => {
    const encoded = encodeURIComponent(value);
    return `${encoded.length}:${encoded}`;
  }).join("|");
}

export function claimLink(claimId, context) {
  const claim = context?.claims?.get(claimId);
  if (!claim) return `<span class="claim-unavailable">${esc(label("ui", "source_unavailable"))}</span>`;
  return `<button class="claim-link" data-claim-id="${esc(claimId)}" data-claim-status="${claim.status}">${esc(label("ui", "sources"))} · ${code(claimId)} · ${esc(label("status", claim.status))}</button>`;
}

function sameDecision(left, right) {
  return Boolean(left && right && left.state === right.state && left.route_code === right.route_code);
}

function decisionsMatch(detail, analysis) {
  const real = detail.decisions.public;
  if (!["public", "simulated"].includes(analysis.mode) || real.availability !== "AVAILABLE" || real.branch !== "PUBLIC" || real.synthetic_flag !== false) return false;
  if ([real.scenario_id, real.evidence_class, real.source, real.display_labels].some((value) => value != null) || !sameDecision(real, analysis.real_decision)) return false;
  if (analysis.mode === "public") return sameDecision(analysis.active_decision, analysis.real_decision) && analysis.simulation_decision == null && analysis.simulation_scenario == null;
  const simulated = detail.decisions.simulated;
  const scenario = analysis.simulation_scenario;
  return Boolean(scenario && simulated.availability === "AVAILABLE" && simulated.branch === "SIMULATED" && simulated.synthetic_flag === true
    && simulated.scenario_id === scenario.scenario_id && simulated.evidence_class === "D" && simulated.source === "DEMO_GENERATOR"
    && simulated.display_labels && scenario.display_labels && simulated.display_labels.en === scenario.display_labels.en && simulated.display_labels.ar === scenario.display_labels.ar
    && sameDecision(simulated, analysis.simulation_decision) && sameDecision(analysis.active_decision, analysis.simulation_decision));
}

export function analystClaimContext(detail, analysis) {
  if (!detail || detail.opportunity.opportunity_id !== analysis.opportunity.id || detail.opportunity.snapshot_id !== analysis.snapshot_id) return null;
  if (!decisionsMatch(detail, analysis)) return null;
  const publicRows = new Map(analysis.evidence.filter((row) => row.synthetic_flag === false).map((row) => [row.evidence_id, row]));
  const scenarioRows = new Map(analysis.evidence.filter((row) => row.synthetic_flag === true).map((row) => [row.evidence_id, row]));
  const available = detail.claims.filter((claim) => claim.branch === "PUBLIC" || analysis.mode === "simulated");
  const references = new Map(detail.evidence_index.map((row) => [row.evidence_id, row]));
  for (const claim of available) {
    if (claim.synthetic_flag !== (claim.branch === "SIMULATED")) return null;
    if (!claim.synthetic_flag && (claim.scenario_id || claim.source || claim.evidence_class || claim.display_labels)) return null;
    if (claim.synthetic_flag && claim.scenario_id !== analysis.simulation_scenario?.scenario_id) return null;
    for (const id of claim.evidence_ids) {
      const ref = references.get(id);
      const row = ref && (ref.synthetic_flag ? scenarioRows : publicRows).get(id);
      if (!row || row.source !== ref.source || row.status !== ref.status || row.evidence_class !== ref.evidence_class) return null;
      if (claim.branch === "PUBLIC" && (row.synthetic_flag || row.source === "DEMO_GENERATOR" || row.status.toLowerCase() === "synthetic")) return null;
      if (row.synthetic_flag && (row.scenario_id !== analysis.simulation_scenario?.scenario_id || row.evidence_class !== "D" || row.source !== "DEMO_GENERATOR")) return null;
    }
  }
  return { executiveCase: detail, claims: new Map(available.map((row) => [row.claim_id, row])), publicRows, scenarioRows, references };
}
