import { escapeHtml as esc, technicalToken as code, narrativeEntry, fireText, executionLabel } from "../dom.js";
import { claimLink } from "../claim-links.js";
import { renderTradeChart } from "../renderers/trade.js";
import { t } from "../i18n.js";
import { state } from "../state.js";
import { label } from "./labels.js";
import { valuesGrid, renderDatasets } from "./summary.js";

export function narrative(context, simulated = false) {
  const decision = simulated ? context.simulatedAnalysis?.simulation_decision : context.publicAnalysis.real_decision;
  const localized = decision?.localized_narrative?.[state.locale];
  if (!localized) throw new Error("EXECUTIVE_NARRATIVE_UNAVAILABLE");
  return localized;
}

export function renderPublicStep(step, context) {
  const analysis = context.publicAnalysis;
  if (step.step_id === "SIGNAL") return `<p class="executive-callout">${esc(label("ui", "signal_note"))}</p>${valuesGrid(step.values)}${renderTradeChart({ trade: analysis.trade })}<div class="executive-rule-list">${analysis.rules.map((row) => `<details data-rule="${esc(row.rule_id)}"><summary>${code(row.rule_id)} ${narrativeEntry(row.localized[state.locale].name)} <span class="exec-chip exec-${esc(row.execution)}">${esc(executionLabel(row.execution))}</span></summary>${narrativeEntry(row.localized[state.locale].result, "p")}${narrativeEntry(row.localized[state.locale].decision_effect, "p")}${claimLink(`rule.${row.rule_id}`, context)}</details>`).join("")}</div>`;
  if (step.step_id === "FALSE_POSITIVE_CONTROLS") return `${valuesGrid(step.values)}<h3>${esc(label("ui", "exclusions"))}</h3><div class="executive-rule-list">${analysis.hard_exclusions.map((row) => `<article><p>${code(row.code)} <span class="executive-status">${esc(label("status", row.status))}</span></p><p>${esc(row.localized_narrative[state.locale])}</p></article>`).join("")}</div>`;
  const localized = narrative(context);
  if (step.step_id === "PUBLIC_CONCLUSION") return `<div class="executive-public">${narrativeEntry(localized.headline, "h3")}${narrativeEntry(localized.rationale, "p")}<p>${esc(label("ui", "public_boundary"))}</p><h4>${esc(label("ui", "hypothesis"))}</h4><p>${step.values.find((row) => row.key === "preferred_route_code").value === null ? esc(label("status", "NOT_CALCULABLE")) : code(step.values.find((row) => row.key === "preferred_route_code").value)}</p>${narrativeEntry(localized.route_label, "p")}<h4>${esc(label("ui", "missing"))}</h4><ul>${localized.missing_facts.map((row) => narrativeEntry(row, "li")).join("")}</ul></div>`;
  if (step.step_id === "MISSING_MINISTRY_FACTS") return `<ul class="executive-facts">${localized.missing_facts.map((row) => narrativeEntry(row, "li")).join("")}</ul>${renderDatasets(context)}`;
  throw new Error("EXECUTIVE_PUBLIC_STEP_INVALID");
}

export function markStoredSourceNames(html, context) {
  if (state.locale !== "ar") return html;
  const names = [...new Set(context.publicAnalysis.evidence.flatMap((row) => [row.source, ...row.source.split("/").map((name) => name.trim())]))].filter((name) => /[A-Za-z]/.test(name));
  const template = document.createElement("template");
  template.innerHTML = html;
  const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    if (!node.parentElement || node.parentElement.closest('[dir="ltr"]')) continue;
    let parts = [node.textContent];
    for (const name of names) parts = parts.flatMap((part) => typeof part !== "string" ? [part] : part.split(name).flatMap((text, index) => index ? [{ source: name }, text] : [text]));
    if (!parts.some((part) => typeof part !== "string")) continue;
    const wrapper = document.createElement("span");
    for (const part of parts) {
      if (typeof part === "string") wrapper.append(document.createTextNode(part));
      else {
        const source = document.createElement("span");
        source.className = "source-language-island"; source.lang = "en"; source.dir = "ltr";
        source.textContent = part.source; wrapper.append(source);
      }
    }
    const caption = document.createElement("span");
    caption.className = "source-language-caption"; caption.textContent = t("source_language.caption");
    wrapper.append(caption); node.replaceWith(wrapper);
  }
  return template.innerHTML;
}
