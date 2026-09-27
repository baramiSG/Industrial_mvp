import { escapeHtml as esc, technicalToken as code, syntheticLabels } from "../dom.js";
import { number, percent } from "../formatters.js";
import { t } from "../i18n.js";
import { state } from "../state.js";
import { policyLabels, label } from "./labels.js";

function control(value) {
  if (typeof value === "string") return esc(label("status", value.toUpperCase()));
  if (value && typeof value.passes === "boolean") return `${esc(label("status", value.passes ? "PASSES" : "FAILS"))}<p>${esc(label("ui", "competition_ratio"))}: ${code(value.capacity_ratio)} · ${esc(label("ui", "comparison_threshold"))}: ${code(value.warning_threshold)}</p>`;
  throw new Error("EXECUTIVE_ROUTE_CONTROL_INVALID");
}

function economics(row) {
  const values = [
    ["unsupported_npv_m", "executive.value.simulated_unsupported_npv_m_sar", row.economics.unsupported_npv_m],
    ["unsupported_irr", "economics.irr", row.economics.unsupported_irr],
    ["minimum_effective_support_m", "executive.value.simulated_minimum_effective_support_m_sar", row.economics.minimum_effective_support_m],
    ["incremental_national_value_m_sar", "executive.value.simulated_incremental_national_value_m_sar", row.incremental_national_value_m_sar],
  ];
  return `<dl>${values.map(([key, title, value]) => {
    const available = typeof value === "number";
    const display = available ? (key === "unsupported_irr" ? esc(percent(value, 3)) : code(number(value, 3))) : esc(label("status", "NOT_CALCULABLE"));
    return `<dt>${esc(t(title))}</dt><dd data-route-value="${key}" data-availability="${available ? "AVAILABLE" : "NOT_CALCULABLE"}">${display}</dd>`;
  }).join("")}</dl>`;
}

function routeRow(row) {
  const reasons = row.localized_reasons?.[state.locale];
  if (!Array.isArray(reasons)) throw new Error("EXECUTIVE_ROUTE_TRANSLATION_MISSING");
  return `<article data-route-row="${row.route_code}" class="executive-route-row"><div><span class="executive-route-number">${code(row.route_code)}</span><h4>${esc(label("route", String(row.route_code)))}</h4><span class="executive-status">${esc(label("status", row.status.toUpperCase()))}</span></div><details><summary>${esc(label("ui", "reason"))}</summary><ul>${reasons.map((reason) => `<li>${esc(reason)}</li>`).join("")}</ul><p>${esc(label("ui", "precedence"))}: ${row.precedence.blocked_by_lower_route === null ? esc(label("ui", "not_blocked")) : code(row.precedence.blocked_by_lower_route)}</p><dl>${["feasibility", "additionality", "competition", "policy_permissibility", "resolves_binding_constraint"].map((key) => `<dt>${esc(label("value", key))}</dt><dd>${control(row[key])}</dd>`).join("")}</dl>${economics(row)}</details></article>`;
}

export function renderRoutes(step, context) {
  const { publicAnalysis: real, simulatedAnalysis: sim, executiveCase: detail } = context;
  const branch = (rows, simulated) => `<section data-route-branch="${simulated ? "SIMULATED" : "PUBLIC"}" class="${simulated ? "executive-simulation" : "executive-public"}"><h3>${esc(label("ui", simulated ? "simulated" : "public"))}</h3>${simulated ? `<p>${esc(t("graph.boundary_synthetic"))}</p>` : ""}${rows.map(routeRow).join("")}</section>`;
  const cf = sim?.simulation_decision.counterfactual;
  const shown = (value, unit = "") => value === null || value === undefined || value === "UNAVAILABLE"
    ? esc(t("common.unavailable")) : code(`${typeof value === "number" ? number(value, 4) : value}${unit ? ` ${unit}` : ""}`);
  const q3 = cf?.q3_brownfield_versus_greenfield;
  const condition = cf ? `<section data-reference-comparison><h3>${esc(t("ministry.reference"))}</h3><p>${esc(t("ministry.no_winner"))}</p>
    <dl>${(cf.q2_missing_capabilities || []).map((field) => `<div><dt>${esc(label("field", field))}</dt><dd>${code(field)}</dd></div>`).join("")}</dl>
    <dl><div><dt>${esc(t("dossier.field.incremental_capacity_kt"))}</dt><dd>${shown(q3?.incremental_capacity_kt, t("ministry.unit.kt"))}</dd></div>
    <div><dt>${esc(t("dossier.field.schedule_months"))}</dt><dd>${shown(q3?.schedule_months, t("ministry.months"))}</dd></div>
    <div><dt>${esc(t("dossier.field.greenfield_alternative"))}</dt><dd>${shown(q3?.greenfield_alternative)}</dd></div></dl></section>` : "";
  const provenance = sim ? `<details data-executive-full-provenance><summary>${esc(t("ministry.provenance"))}</summary>${policyLabels(detail.decisions.simulated.display_labels)}<p>${code(detail.decisions.simulated.scenario_id)} · ${code(detail.decisions.simulated.source)} · ${code(detail.decisions.simulated.evidence_class)}</p></details>` : "";
  return `<p class="executive-callout">${esc(label("ui", "route_note"))}</p>${provenance}${condition}<div class="executive-route-grid">${branch(real.route_hypotheses, false)}${sim ? branch(sim.simulation_decision.route_hypotheses, true) : `<p>${esc(label("ui", "no_simulation"))}</p>`}</div>`;
}
