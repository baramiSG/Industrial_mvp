import { getJSON, opportunityEndpoint } from "../api.js";
import { STEP_IDS, VECTOR_IDS } from "./labels.js";

function requireMatch(condition) {
  if (!condition) throw new Error("EXECUTIVE_CONTEXT_MISMATCH");
}

function stable(value) {
  if (Array.isArray(value)) return JSON.stringify(value.map(stable));
  if (value && typeof value === "object") return JSON.stringify(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return JSON.stringify(value);
}

function unique(rows, key) {
  requireMatch(Array.isArray(rows) && new Set(rows.map((row) => row[key])).size === rows.length);
  return new Map(rows.map((row) => [row[key], row]));
}

export function validateExecutiveContext(context) {
  const { summary, executiveCase: detail, publicAnalysis: real, simulatedAnalysis: sim } = context;
  const id = detail.opportunity.opportunity_id;
  const reference = summary.opportunities.find((row) => row.opportunity_id === id);
  requireMatch(reference && reference.snapshot_id === detail.opportunity.snapshot_id);
  requireMatch(real.opportunity.id === id && real.snapshot_id === detail.opportunity.snapshot_id && real.mode === "public");
  const publicDecision = detail.decisions.public;
  requireMatch(publicDecision.branch === "PUBLIC" && publicDecision.synthetic_flag === false);
  requireMatch(publicDecision.state === real.real_decision.state && publicDecision.route_code === real.real_decision.route_code);
  requireMatch(real.evidence.every((row) => row.synthetic_flag === false && row.source !== "DEMO_GENERATOR" && row.status.toLowerCase() !== "synthetic"));
  const simulated = detail.decisions.simulated;
  if (simulated.availability === "AVAILABLE") {
    requireMatch(sim && sim.mode === "simulated" && sim.opportunity.id === id && sim.snapshot_id === real.snapshot_id);
    requireMatch(stable(real.real_decision) === stable(sim.real_decision));
    requireMatch(simulated.scenario_id === sim.simulation_scenario.scenario_id);
    requireMatch(simulated.state === sim.simulation_decision.state && simulated.route_code === sim.simulation_decision.route_code);
    requireMatch(stable(simulated.display_labels) === stable(summary.synthetic_evsi.display_labels));
    requireMatch(stable(simulated.display_labels) === stable(sim.simulation_scenario.display_labels));
    requireMatch(simulated.synthetic_flag === true && simulated.evidence_class === "D" && simulated.source === "DEMO_GENERATOR");
  } else {
    requireMatch(simulated.availability === "UNAVAILABLE" && simulated.branch === "SIMULATED" && sim === null);
    requireMatch(simulated.synthetic_flag === false && simulated.state === null && simulated.route_code === null);
    requireMatch([simulated.scenario_id, simulated.evidence_class, simulated.source, simulated.display_labels].every((value) => value === null));
  }
  requireMatch(stable(detail.steps.map((row) => row.step_id)) === stable(STEP_IDS));
  requireMatch(stable(detail.vectors.map((row) => row.vector_id)) === stable(VECTOR_IDS));
  const claims = unique(detail.claims, "claim_id");
  const references = unique(detail.evidence_index, "evidence_id");
  const publicRows = unique(real.evidence, "evidence_id");
  const scenarioRows = unique(sim?.evidence || [], "evidence_id");
  references.forEach((ref, evidenceId) => {
    const record = (ref.synthetic_flag ? scenarioRows : publicRows).get(evidenceId);
    requireMatch(record && record.synthetic_flag === ref.synthetic_flag && record.source === ref.source && record.evidence_class === ref.evidence_class);
    requireMatch(record.status === ref.status && stable(record.contradiction ?? null) === stable(ref.contradiction));
    if (ref.synthetic_flag) {
      requireMatch(stable(ref.display_labels) === stable(simulated.display_labels) && stable(record.display_labels) === stable(simulated.display_labels));
      requireMatch(ref.scenario_id === simulated.scenario_id && record.scenario_id === simulated.scenario_id);
      requireMatch(ref.evidence_class === "D" && ref.source === "DEMO_GENERATOR" && ref.status.toLowerCase() === "synthetic");
    } else requireMatch(!ref.scenario_id && !ref.display_labels && ref.source !== "DEMO_GENERATOR" && ref.status.toLowerCase() !== "synthetic");
  });
  claims.forEach((claim) => {
    requireMatch(["PUBLIC", "SIMULATED"].includes(claim.branch));
    requireMatch(claim.synthetic_flag === (claim.branch === "SIMULATED"));
    if (claim.synthetic_flag) requireMatch(claim.scenario_id === simulated.scenario_id && claim.evidence_class === "D" && claim.source === "DEMO_GENERATOR" && stable(claim.display_labels) === stable(simulated.display_labels));
    else requireMatch(claim.scenario_id === null && claim.evidence_class === null && claim.source === null && claim.display_labels === null);
    claim.evidence_ids.forEach((id) => {
      const ref = references.get(id);
      requireMatch(ref && (claim.branch !== "PUBLIC" || ref.synthetic_flag === false));
    });
  });
  [...detail.steps, ...detail.vectors].forEach((row) => {
    row.claim_ids.forEach((id) => requireMatch(claims.has(id)));
    row.values.forEach((value) => value.evidence_ids.forEach((id) => requireMatch(references.has(id))));
  });
  const evsi = summary.synthetic_evsi.cases.find((row) => row.opportunity_id === id);
  requireMatch(simulated.availability === "AVAILABLE" ? evsi && evsi.scenario_id === simulated.scenario_id : evsi === undefined);
  return { ...context, claims, references, publicRows, scenarioRows, evsi };
}

export async function loadExecutiveContext(opportunityId, summary) {
  const [executiveCase, publicAnalysis] = await Promise.all([
    getJSON(`/api/executive/opportunities/${encodeURIComponent(opportunityId)}`),
    getJSON(opportunityEndpoint(opportunityId, "public")),
  ]);
  requireMatch(executiveCase.opportunity.opportunity_id === opportunityId);
  const simulatedAnalysis = executiveCase.decisions.simulated.availability === "AVAILABLE"
    ? await getJSON(opportunityEndpoint(opportunityId, "simulated")) : null;
  return validateExecutiveContext({ summary, executiveCase, publicAnalysis, simulatedAnalysis });
}
