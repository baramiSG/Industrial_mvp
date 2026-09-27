import { escapeHtml as esc, technicalToken as code, narrativeEntry, sourceIsland, sourceCaption } from "../dom.js";
import { t, interpolate } from "../i18n.js";
import { state } from "../state.js";
import { dossierHtmlEndpoint } from "../api.js";
import { number } from "../formatters.js";
import { policyLabels, label, capabilityMeanings, capabilityLegend } from "./labels.js";
import { valuesGrid, renderEvsi } from "./summary.js";
import { narrative } from "./steps.js";
import { executive } from "./context.js";
import { renderResolution } from "./resolution.js";

function conditionList(localized) {
  return `<div class="executive-condition-grid"><section><h4>${esc(label("ui", "conditions"))}</h4><ul>${localized.conditions.map((row) => narrativeEntry(row, "li")).join("")}</ul></section><section><h4>${esc(label("ui", "kill"))}</h4><ul>${localized.kill_conditions.map((row) => narrativeEntry(row, "li")).join("")}</ul></section></div>`;
}

export function renderSimulationStep(step, context) {
  const simulated = context.executiveCase.decisions.simulated;
  const sim = context.simulatedAnalysis;
  const publicConditions = step.step_id === "CONDITIONS_AND_KILL"
    ? `<section class="executive-public"><h3>${esc(label("ui", "public"))}</h3>${conditionList(narrative(context))}</section>` : "";
  if (!sim) return `${publicConditions}<p>${esc(label("ui", "no_simulation"))}</p>`;
  let content;
  if (step.step_id === "SIMULATED_EVIDENCE") {
    content = `${renderResolution(context, executive.selection)}<details data-scenario-context><summary>${esc(t("ministry.vectors_details"))}</summary>
      <h3>${esc(label("ui", "scenario"))}</h3><p>${code(simulated.scenario_id)}</p><p>${code(simulated.source)} · ${esc(label("ui", "actual_class"))} ${code(simulated.evidence_class)}</p>
      <details><summary>${esc(label("ui", "seed_basis"))}</summary>${sourceCaption()}${sourceIsland(sim.simulation_scenario.seed_basis, "p")}</details>
      <h4>${esc(label("ui", "class_if_confirmed"))}</h4><dl>${Object.entries(sim.simulation_decision.evidence_class_assessment).map(([key, row]) => `<dt>${esc(label("field", key))}</dt><dd>${esc(label("ui", "actual_class"))} ${code(row.evidence_class)} · ${esc(label("ui", "class_if_confirmed"))} ${code(row.class_if_confirmed)}</dd>`).join("")}</dl>
      <h4>${esc(label("ui", "used_blocks"))}</h4><div>${sourceCaption()}${sim.synthetic_inputs_used.map((block) => sourceIsland(block)).join(" · ")}</div>
      <h4>${esc(label("ui", "capacity"))}</h4><dl>${["effective_qualified_capacity_kt", "target_spec_demand_kt", "specification_adjusted_gap_kt"].map((key) => `<dt>${esc(label("ui", key))}</dt><dd data-capacity-key="${key}">${sim.capacity?.[key] == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.capacity[key], 3))}</dd>`).join("")}</dl>${capabilityDetail(sim.capability)}
    </details>`;
  } else if (step.step_id === "INTERVENTION") {
    content = valuesGrid(step.values) + `<dl><dt>${esc(label("ui", "competition_ratio"))}</dt><dd data-competition-ratio>${sim.competition?.post_entry_capacity_to_downside_demand == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.competition.post_entry_capacity_to_downside_demand, 4))}</dd><dt>${esc(label("ui", "comparison_threshold"))}</dt><dd>${sim.competition?.warning_threshold == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.competition.warning_threshold, 4))}</dd></dl>`;
  } else {
    const q3 = sim.simulation_decision.counterfactual?.q3_brownfield_versus_greenfield;
    const policy = state.ui.executive_policy.reference_condition[state.locale];
    const condition = q3 && typeof q3.incremental_capacity_kt === "number" && typeof q3.schedule_months === "number"
      ? `<p data-reference-condition>${esc(interpolate(policy, { increment_kt: number(q3.incremental_capacity_kt, 0), months: number(q3.schedule_months, 0) }))}</p>` : "";
    const dossier = dossierHtmlEndpoint(context.executiveCase.opportunity.opportunity_id, "simulated", state.locale);
    content = `<h3>${esc(label("ui", "simulated"))}</h3>${conditionList(narrative(context, true))}${condition}
      <p>${esc(t("ministry.dossier_scope"))}</p><a href="${esc(dossier)}" target="_blank" rel="noopener noreferrer">${esc(t("actions.open_dossier"))}</a>`;
  }
  return `${publicConditions}<section class="executive-simulation"><p>${esc(t("graph.boundary_synthetic"))}</p><p>${esc(label("ui", "simulation_boundary"))}</p><details data-executive-full-provenance><summary>${esc(t("ministry.provenance"))}</summary>${policyLabels(simulated.display_labels)}<p>${code(simulated.scenario_id)} · ${code(simulated.source)} · ${code(simulated.evidence_class)}</p></details>${content}</section>${step.step_id === "INTERVENTION" ? renderEvsi(context) : ""}`;
}

function capabilityDetail(capability) {
  const meanings = capabilityMeanings();
  const legend = capabilityLegend();
  const dimensions = capability.dimensions.map((row) => {
    const value = row.known ? row.state : "U";
    return `<div data-capability-dimension="${row.dimension}"><dt>${esc(label("field", row.dimension))}</dt><dd data-capability-state="${value}">${code(value)} · ${esc(meanings[value])}${row.known ? "" : ` · ${esc(label("status", "UNAVAILABLE"))}`}</dd></div>`;
  }).join("");
  return `<h4>${esc(t("capability.title"))}</h4><p><span class="ltr-isolate">${esc(t("capability.distance"))}</span>: ${capability.d_star === null ? esc(label("status", "NOT_CALCULABLE")) : code(number(capability.d_star, 4))}</p>${legend}<dl class="executive-capability">${dimensions}</dl><div>${sourceCaption()}${sourceIsland(capability.control_message)}</div>`;
}
