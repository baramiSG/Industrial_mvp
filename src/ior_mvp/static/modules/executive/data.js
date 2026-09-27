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

function validateDiagnostics(detail, sim) {
  const discovery = detail.candidate_discovery;
  const lines = detail.line_assessment;
  requireMatch(discovery && lines && Array.isArray(discovery.rows) && Array.isArray(lines.rows));
  if (!sim) {
    requireMatch(!discovery.available && discovery.reason === "NO_SCENARIO"
      && !lines.available && lines.reason === "NO_SCENARIO"
      && !discovery.rows.length && !lines.rows.length && discovery.requirement === null);
    return;
  }
  const raw = sim.candidate_discovery;
  const rawLines = sim.line_assessment;
  requireMatch(raw && rawLines && discovery.available === raw.available
    && lines.available === rawLines.available && discovery.reason === raw.reason
    && lines.reason === rawLines.reason);
  if (!discovery.available) {
    requireMatch(!discovery.rows.length && !lines.rows.length && discovery.requirement === null
      && !discovery.synthetic_flag && !lines.synthetic_flag);
    return;
  }
  const scenario = sim.simulation_scenario.scenario_id;
  const requirement = discovery.requirement;
  requireMatch(requirement && typeof requirement.target_name === "string"
    && typeof requirement.application === "string"
    && requirement.target_name.length > 0 && requirement.application.length > 0
    && Number.isFinite(requirement.target_demand_kt)
    && Array.isArray(requirement.request_window_months)
    && requirement.request_window_months.length === 2
    && requirement.request_window_months.every(Number.isInteger)
    && requirement.request_window_months[0] >= 0
    && requirement.request_window_months[1] > requirement.request_window_months[0]
    && Object.keys(requirement.specification || {}).length > 0);
  requireMatch(discovery.opportunity_id === detail.opportunity.opportunity_id
    && discovery.scenario_id === scenario && lines.scenario_id === scenario
    && discovery.target_family === raw.target_family
    && discovery.synthetic_flag && lines.synthetic_flag
    && discovery.evidence_class === "D" && lines.evidence_class === "D"
    && discovery.source === "DEMO_GENERATOR" && lines.source === "DEMO_GENERATOR"
    && lines.winner === null);
  const rawRows = unique(raw.rows, "entity_id");
  const dtoRows = unique(discovery.rows, "entity_id");
  const rawLineRows = unique(rawLines.rows, "line_id");
  const dtoLineRows = unique(lines.rows, "line_id");
  requireMatch(rawRows.size === dtoRows.size && rawLineRows.size === dtoLineRows.size);
  const namesByCompany = new Map();
  dtoRows.forEach((row, id) => {
    const source = rawRows.get(id);
    requireMatch(source && row.scenario_id === scenario
      && row.company_id === source.company_id && row.entity_kind === source.entity_kind
      && row.plant_id === (source.plant_id ?? null)
      && row.disposition === source.disposition
      && typeof row.company_name_en === "string" && row.company_name_en.length > 0
      && typeof row.company_name_ar === "string" && row.company_name_ar.length > 0
      && stable(row.evidence_boundary) === stable(source.evidence_boundary)
      && row.findings.length === source.findings.length);
    const names = [row.company_name_en, row.company_name_ar];
    if (namesByCompany.has(row.company_id)) requireMatch(
      stable(namesByCompany.get(row.company_id)) === stable(names),
    );
    else namesByCompany.set(row.company_id, names);
    row.findings.forEach((finding, index) => {
      const found = source.findings[index];
      for (const key of ["requirement_item_id", "dimension", "current_recorded",
        "needed", "status", "origin", "rule_id", "temporal_scope",
        "quantified_gap", "reason_code", "action_code", "next_evidence"]) {
        requireMatch(stable(finding[key]) === stable(found[key] ?? null));
      }
      requireMatch(stable(finding.source_refs.map((ref) => Object.fromEntries(
        Object.entries(ref).filter(([, value]) => value !== null),
      ))) === stable(found.source_refs));
      if (finding.next_evidence) requireMatch(
        finding.next_evidence.subject_scope === id
        && finding.next_evidence.action_code === finding.action_code,
      );
      if (row.entity_kind === "LINE" && finding.rule_id === "P09") requireMatch(
        finding.needed === requirement.target_demand_kt
        && finding.quantified_gap === dtoLineRows.get(id)?.capacity.shortage_kt,
      );
    });
    if (row.entity_kind === "LINE") requireMatch(dtoLineRows.has(id));
  });
  dtoLineRows.forEach((row, id) => {
    const source = rawLineRows.get(id);
    requireMatch(source && source.reference_role === row.reference_role
      && stable(source.comparisons) === stable(row.comparisons)
      && stable(source.gates) === stable(row.gates)
      && stable(source.gate_requirements) === stable(row.gate_requirements)
      && stable(source.capacity) === stable(row.capacity)
      && source.capability.known_weight_coverage === row.known_weight_coverage
      && source.capability.d_star === row.d_star);
  });
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
  validateDiagnostics(detail, sim);
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
