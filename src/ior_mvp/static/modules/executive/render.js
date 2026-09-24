import { escapeHtml as esc, technicalToken, stateLabel, narrativeEntry, syntheticLabels } from "../dom.js";
import { t } from "../i18n.js";
import { state } from "../state.js";
import { executive } from "./context.js";
import { policyLabels, label, STEP_IDS, stepLabel } from "./labels.js";
import { claimLink } from "../claim-links.js";
import { renderClaimLinks } from "./evidence.js";
import { renderVectors } from "./summary.js";
import { narrative } from "./steps.js";
import { renderRegisteredStep } from "./registry.js";

export function analystUrl(opportunityId, mode, view) {
  const query = new URLSearchParams({ opportunity: opportunityId, locale: state.locale });
  if (mode) query.set("mode", mode);
  if (view) query.set("graphView", view);
  return `/?${query}`;
}

export function mountExecutiveShell() {
  document.querySelector(".app-shell").outerHTML = `
    <div class="executive-shell">
      <a class="executive-skip" href="#executive-content">${esc(t("executive.skip"))}</a>
      <header class="executive-header"><a class="executive-brand" href="/executive">${esc(t("brand.name"))}</a>
        <p>${esc(t("executive.eyebrow"))}</p>
        <div><a data-analyst-link href="/">${esc(t("executive.analyst"))}</a>
          <button id="locale-switch" class="locale-button" data-executive-locale>${esc(t("locale.switch"))}</button></div>
      </header>
      <main data-executive-main id="executive-content" tabindex="-1" aria-busy="true">
        <div id="executive-heading"></div><div id="executive-status" role="status" aria-live="polite"></div>
        <div id="executive-integrity"></div><div id="executive-comparison"></div><div id="executive-vectors"></div><div id="executive-body"></div><div id="executive-sources"></div>
      </main>
    </div>`;
  document.body.classList.remove("app-loading");
  document.body.setAttribute("aria-busy", "false");
}

export function renderHeading(selection = executive.selection) {
  const { summary } = executive;
  const opportunity = summary?.opportunities.find((row) => row.opportunity_id === selection?.opportunityId);
  const name = opportunity?.[state.locale === "ar" ? "name_ar" : "name_en"];
  document.getElementById("executive-heading").innerHTML = `<div class="executive-title">
    <div><p class="eyebrow">${esc(t("executive.title"))}</p><h1>${esc(name || t("executive.title"))}</h1>
      ${opportunity ? `<p>${technicalToken(opportunity.hs6)} · ${technicalToken(opportunity.as_of_date)}</p><p class="executive-snapshot">${esc(label("ui", "snapshot"))}: ${technicalToken(opportunity.snapshot_id)}</p>` : ""}</div>
    ${summary?.opportunities.length ? `<label>${esc(t("executive.choose_case"))}<select id="executive-case">
      ${summary.opportunities.map((row) => `<option value="${esc(row.opportunity_id)}" ${row.opportunity_id === selection?.opportunityId ? "selected" : ""}>${esc(row.hs6)} · ${esc(row[state.locale === "ar" ? "name_ar" : "name_en"])}</option>`).join("")}
    </select></label>` : ""}</div>`;
  const link = document.querySelector("[data-analyst-link]");
  link.href = analystUrl(selection?.opportunityId || "");
  link.textContent = t("executive.analyst");
  document.querySelector("[data-executive-locale]").textContent = t("locale.switch");
  document.querySelector(".executive-brand").textContent = t("brand.name");
  document.querySelector(".executive-header > p").textContent = t("executive.eyebrow");
  document.querySelector(".executive-skip").textContent = t("executive.skip");
}

export function renderJourney() {
  const { selection, context } = executive;
  const content = renderRegisteredStep(selection.stepId, context);
  const position = STEP_IDS.indexOf(selection.stepId);
  const movement = `<div class="executive-movement">${position > 0 ? `<button data-executive-back data-executive-go="${STEP_IDS[position - 1]}">${esc(label("ui", "back"))}</button>` : ""}${position < STEP_IDS.length - 1 ? `<button data-executive-next data-executive-go="${STEP_IDS[position + 1]}">${esc(label("ui", "next"))}</button>` : ""}</div>`;
  renderIntegrity(context.summary.integrity);
  document.getElementById("executive-comparison").innerHTML = renderComparison(context);
  document.getElementById("executive-vectors").innerHTML = renderVectors(context);
  document.getElementById("executive-body").innerHTML = `<div class="executive-layout">
    <nav class="executive-journey" aria-label="${esc(t("executive.journey"))}"><ol>
      ${STEP_IDS.map((id, index) => `<li><button data-executive-step="${id}" ${id === selection.stepId ? 'aria-current="step"' : ""}><span>${technicalToken(index + 1)}</span><b>${esc(stepLabel(id))}</b></button></li>`).join("")}
    </ol></nav><article class="executive-article" data-active-step="${selection.stepId}" tabindex="-1"><p class="eyebrow">${esc(t("executive.journey"))}</p><h2>${esc(stepLabel(selection.stepId))}</h2>${movement}${content}${renderClaimLinks(context.executiveCase.steps.find((row) => row.step_id === selection.stepId).claim_ids, context)}</article></div>`;
  document.querySelector("[data-executive-main]").setAttribute("data-executive-ready", selection.opportunityId);
  document.querySelector("[data-executive-main]").setAttribute("aria-busy", "false");
}

export function renderIntegrity(integrity) {
  const status = integrity?.status ?? "UNAVAILABLE";
  const checks = {
    PUBLIC_SYNTHETIC_LEAKAGE: "executive.integrity.public_synthetic_leakage",
    REAL_DECISION_EQUALITY: "executive.integrity.real_decision_equality",
    SYNTHETIC_METADATA: "executive.integrity.synthetic_metadata",
    SCENARIO_VALIDATION: "executive.integrity.scenario_validation",
  };
  document.getElementById("executive-integrity").innerHTML = `<section class="executive-integrity" data-executive-integrity="${esc(status)}" ${status === "FAIL" ? 'role="alert"' : ""}>
    <p><strong>${esc(label("ui", "integrity"))}: ${esc(label("status", status))}</strong>${integrity ? ` · ${esc(t("executive.integrity.violations"))}: <span data-integrity-count>${technicalToken(integrity.violation_count)}</span>` : ""}</p>
    ${status === "FAIL" ? `<h2>${esc(t("executive.integrity.checks"))}</h2><ul>${integrity.checks.map((check) => `<li data-integrity-check="${esc(check.check_id)}"><strong>${esc(t(checks[check.check_id]))}</strong> · ${esc(label("status", check.status))} · ${esc(t("executive.integrity.violations"))}: ${technicalToken(check.violation_count)}${check.affected_ids.length ? `<p>${esc(label("ui", "affected"))}: ${check.affected_ids.map(technicalToken).join(" · ")}</p>` : ""}</li>`).join("")}</ul>` : ""}</section>`;
}

export function renderStatus(key) {
  document.getElementById("executive-status").textContent = key ? t(key) : "";
}

function renderComparison(context) {
  return `<div class="executive-comparison">${["public", "simulated"].map((branch) => {
    const decision = context.executiveCase.decisions[branch];
    const sim = branch === "simulated";
    const available = decision.availability === "AVAILABLE";
    const localized = available ? narrative(context, sim) : null;
    return `<section class="executive-decision ${sim ? "executive-simulation" : "executive-public"}" data-branch="${decision.branch}" data-state="${esc(decision.state ?? "UNAVAILABLE")}" data-route="${decision.route_code ?? "NOT_CALCULABLE"}"><p class="eyebrow">${esc(label("ui", branch))}</p>${sim && available ? policyLabels(decision.display_labels) : ""}${available ? `<span class="state-chip state-${esc(decision.state)}">${esc(stateLabel(decision.state))}</span>${narrativeEntry(localized.rationale, "p")}<p>${esc(label("ui", "route"))}: ${decision.route_code === null ? esc(label("status", "NOT_CALCULABLE")) : `${technicalToken(decision.route_code)} · ${esc(label("route", String(decision.route_code)))}`}</p>` : `<p>${esc(label("ui", "no_simulation"))}</p>`}${!sim || available ? `<p>${esc(label("ui", sim ? "actual_class" : "confidence"))}: ${technicalToken(sim ? decision.evidence_class : context.publicAnalysis.real_decision.confidence)}</p>` : ""}<small>${esc(label("ui", sim ? "simulation_boundary" : "public_boundary"))}</small>${available ? claimLink(`decision.${branch}`, context) : ""}</section>`;
  }).join("")}</div>`;
}

export function clearContextDisplay() {
  ["executive-integrity", "executive-comparison", "executive-vectors", "executive-body", "executive-sources"].forEach((id) => document.getElementById(id).replaceChildren());
  const main = document.querySelector("[data-executive-main]");
  main.removeAttribute("data-executive-ready");
  main.setAttribute("aria-busy", "true");
}

export function renderFailure(kind = "error") {
  clearContextDisplay();
  renderIntegrity(executive.summary?.integrity);
  document.querySelector("[data-executive-main]").setAttribute("aria-busy", "false");
  document.getElementById("executive-status").innerHTML = `<p>${esc(label("ui", kind))}</p><button data-executive-retry>${esc(label("ui", "retry"))}</button>${kind === "not_found" && executive.summary?.opportunities.length ? `<button data-executive-first>${esc(label("ui", "first_case"))}</button>` : ""}`;
}
