import { escapeHtml as esc, technicalToken as code, sourceIsland, sourceCaption, syntheticLabels } from "../dom.js";
import { number, integer, percent } from "../formatters.js";
import { t } from "../i18n.js";
import { policyLabels, label } from "./labels.js";
import { claimLink } from "../claim-links.js";

export function scalar(value) {
  if (value.availability !== "AVAILABLE" || value.value === null) return esc(label("status", value.availability));
  if (typeof value.value === "boolean") return esc(t(value.value ? "common.yes" : "common.no"));
  if (typeof value.value === "number") return code(number(value.value, 3));
  if (["UNAVAILABLE", "NOT_CALCULABLE"].includes(value.value)) return esc(label("status", value.value));
  if (["gap_class", "secondary_gap_classes"].includes(value.key)) return (value.value ? value.value.split(",") : ["none"]).map((id) => esc(label("code", id.trim()))).join(" · ");
  if (value.key === "fired_rule_ids") return value.value.split(",").map(code).join(" · ");
  return code(value.value);
}

export function valuesGrid(values) {
  return `<dl class="executive-values">${values.map((value) => `<div data-value="${esc(value.key)}" data-availability="${esc(value.availability)}"><dt>${esc(label("value", value.key))}</dt><dd>${scalar(value)}</dd></div>`).join("")}</dl>`;
}

export function renderVectors(context) {
  return `<section class="executive-vectors" aria-label="${esc(label("ui", "vectors"))}"><p>${esc(label("ui", "vectors_note"))}</p><div>${context.executiveCase.vectors.map((vector) => `<details data-vector="${vector.vector_id}"><summary>${esc(label("vector", vector.vector_id))}</summary>${valuesGrid(vector.values)}<div class="executive-claim-links">${vector.claim_ids.map((id) => claimLink(id, context)).join("")}</div></details>`).join("")}</div></section>`;
}

export function renderDatasets(context) {
  return `<section class="executive-datasets"><h3>${esc(label("ui", "missing"))}</h3><p>${esc(label("ui", "dataset_note"))}</p><div class="executive-dataset-grid">${context.summary.public_dataset_unlocks.map((row) => `<article data-dataset="${esc(row.dataset_kind)}"><h4>${esc(label("dataset", row.dataset_kind))}</h4><dl><dt>${esc(label("ui", "loaded_cases"))}</dt><dd>${code(integer(row.loaded_case_count))}</dd><dt>${esc(label("ui", "screening_records"))}</dt><dd>${code(integer(row.screening_record_count))}</dd></dl><details><summary>${esc(label("ui", "detail"))}</summary><div>${sourceCaption()}${row.need_codes.map((need) => sourceIsland(need)).join(" · ")}</div><p>${row.loaded_opportunity_ids.map(code).join(" · ")}</p><p>${esc(t("executive.ui.shown_records", { shown: row.screening_hs6.slice(0, 50).length, total: row.screening_record_count }))}</p><p>${row.screening_hs6.slice(0, 50).map(code).join(" · ")}</p></details></article>`).join("")}</div></section>`;
}

export function renderEvsi(context) {
  const summary = context.summary.synthetic_evsi;
  const row = context.evsi;
  return `<section class="executive-simulation" data-case-evsi data-availability="${esc(row.availability)}"><h3>${esc(label("ui", "evsi"))}</h3>${policyLabels(summary.display_labels)}<p>${esc(label("ui", "evsi_note"))}</p>
    <p>${code(row.scenario_id ?? "UNAVAILABLE")} · ${esc(label("status", row.availability))}</p>
    ${row.availability === "AVAILABLE" ? `<p class="executive-number">${code(number(row.approximate_evsi_m_sar))} ${esc(label("ui", "sar_million"))}</p><details><summary>${esc(label("ui", "next_fact"))}</summary>${sourceCaption()}${sourceIsland(row.next_fact, "p")}<dl><dt>${esc(label("ui", "route_probability"))}</dt><dd>${esc(percent(row.route_change_probability))}</dd></dl></details>` : ""}
    <details><summary>${esc(label("ui", "detail"))}</summary><dl><dt>${esc(label("ui", "available_cases"))}</dt><dd>${code(integer(summary.available_case_count))}</dd><dt>${esc(label("ui", "unavailable_cases"))}</dt><dd>${code(integer(summary.unavailable_case_count))}</dd><dt>${esc(label("ui", "total_evsi"))}</dt><dd>${code(number(summary.total_approximate_evsi_m_sar))}</dd></dl></details></section>`;
}
