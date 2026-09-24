import { escapeHtml as esc, technicalToken as code, narrativeEntry, syntheticLabels, sourceIsland, sourceCaption } from "../dom.js";
import { t } from "../i18n.js";
import { number } from "../formatters.js";
import { policyLabels, label } from "./labels.js";
import { valuesGrid, renderEvsi } from "./summary.js";
import { narrative } from "./steps.js";

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
    content = `<h3>${esc(label("ui", "scenario"))}</h3><p>${code(simulated.scenario_id)}</p><p>${code(simulated.source)} · ${esc(label("ui", "actual_class"))} ${code(simulated.evidence_class)}</p><details><summary>${esc(label("ui", "seed_basis"))}</summary>${sourceCaption()}${sourceIsland(sim.simulation_scenario.seed_basis, "p")}</details><h4>${esc(label("ui", "class_if_confirmed"))}</h4><dl>${Object.entries(sim.simulation_decision.evidence_class_assessment).map(([key, row]) => `<dt>${esc(label("field", key))}</dt><dd>${esc(label("ui", "actual_class"))} ${code(row.evidence_class)} · ${esc(label("ui", "class_if_confirmed"))} ${code(row.class_if_confirmed)}</dd>`).join("")}</dl>`;
    content += `<h4>${esc(label("ui", "used_blocks"))}</h4><div>${sourceCaption()}${sim.synthetic_inputs_used.map((block) => sourceIsland(block)).join(" · ")}</div><h4>${esc(label("ui", "capacity"))}</h4><dl>${["effective_qualified_capacity_kt", "target_spec_demand_kt", "specification_adjusted_gap_kt"].map((key) => `<dt>${esc(label("ui", key))}</dt><dd data-capacity-key="${key}">${sim.capacity?.[key] == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.capacity[key], 3))}</dd>`).join("")}</dl>${policyLabels(simulated.display_labels)}${capabilityDetail(sim.capability)}`;
  } else if (step.step_id === "INTERVENTION") {
    content = valuesGrid(step.values) + `<dl><dt>${esc(label("ui", "competition_ratio"))}</dt><dd data-competition-ratio>${sim.competition?.post_entry_capacity_to_downside_demand == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.competition.post_entry_capacity_to_downside_demand, 4))}</dd><dt>${esc(label("ui", "comparison_threshold"))}</dt><dd>${sim.competition?.warning_threshold == null ? esc(label("status", "NOT_CALCULABLE")) : code(number(sim.competition.warning_threshold, 4))}</dd></dl>`;
  } else content = `<h3>${esc(label("ui", "simulated"))}</h3>${conditionList(narrative(context, true))}`;
  return `${publicConditions}<section class="executive-simulation">${policyLabels(simulated.display_labels)}<p>${esc(label("ui", "simulation_boundary"))}</p>${content}</section>${step.step_id === "INTERVENTION" ? renderEvsi(context) : ""}`;
}

function capabilityDetail(capability) {
  const meanings = {
    0: t("executive.capability.state.0"), 1: t("executive.capability.state.1"),
    2: t("executive.capability.state.2"), 3: t("executive.capability.state.3"),
    U: t("executive.capability.state.u"),
  };
  const legend = `<details data-capability-legend><summary>${esc(t("executive.capability.legend"))}</summary><dl>${Object.entries(meanings).map(([value, meaning]) => `<div><dt>${code(value)}</dt><dd data-capability-legend-state="${value}">${esc(meaning)}</dd></div>`).join("")}</dl><p>${esc(t("executive.capability.simulation_note"))}</p></details>`;
  const dimensions = capability.dimensions.map((row) => {
    const value = row.known ? row.state : "U";
    return `<div data-capability-dimension="${row.dimension}"><dt>${esc(label("field", row.dimension))}</dt><dd data-capability-state="${value}">${code(value)} · ${esc(meanings[value])}${row.known ? "" : ` · ${esc(label("status", "UNAVAILABLE"))}`}</dd></div>`;
  }).join("");
  return `<h4>${esc(t("capability.title"))}</h4><p><span class="ltr-isolate">${esc(t("capability.distance"))}</span>: ${capability.d_star === null ? esc(label("status", "NOT_CALCULABLE")) : code(number(capability.d_star, 4))}</p>${legend}<dl class="executive-capability">${dimensions}</dl><div>${sourceCaption()}${sourceIsland(capability.control_message)}</div>`;
}
