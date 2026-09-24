import { escapeHtml as esc, technicalToken as code, syntheticLabels, sourceIsland, sourceCaption } from "../dom.js";
import { state } from "../state.js";
import { renderEvidenceResult } from "../graph/passports.js";
import { claimLink, evidenceAnchor } from "../claim-links.js";
import { policyLabels, label } from "./labels.js";

let sourceTrigger = null;
let activeRegion = null;

export function renderClaimLinks(ids, context) {
  return `<div class="executive-claim-links">${ids.map((id) => claimLink(id, context)).join("")}</div>`;
}

export function closeClaimEvidence() {
  activeRegion?.replaceChildren();
  if (sourceTrigger?.isConnected) sourceTrigger.focus({ preventScroll: true });
  sourceTrigger = null;
  activeRegion = null;
}

function passports(claim, context) {
  const id = context.executiveCase.opportunity.opportunity_id;
  return claim.evidence_ids.map((evidenceId) => {
    const ref = context.references.get(evidenceId);
    const row = (ref.synthetic_flag ? context.scenarioRows : context.publicRows).get(evidenceId);
    if (!row) throw new Error("EXECUTIVE_PASSPORT_MISSING");
    const template = document.createElement("template");
    template.innerHTML = renderEvidenceResult({ records: [{ opportunityId: id, record: row }], unresolved: [], documentAddresses: row.document_addresses || [] }, ref.synthetic_flag ? "simulated" : "public");
    const article = template.content.querySelector("[data-passport-id]");
    const anchor = "detail-" + evidenceAnchor(ref.synthetic_flag ? "SIMULATED" : "PUBLIC", id, evidenceId);
    article.id = anchor;
    article.dataset.evidenceBranch = ref.synthetic_flag ? "SIMULATED" : "PUBLIC";
    template.content.querySelector("[data-passport-ref]").href = `#${anchor}`;
    return `${sourceCaption()}${ref.synthetic_flag ? policyLabels(ref.display_labels) : ""}${template.innerHTML}`;
  }).join("");
}

export function openClaimEvidence(claimId, trigger, context, region) {
  const claim = context?.claims?.get(claimId);
  if (!claim || !region) return;
  sourceTrigger = trigger;
  activeRegion = region;
  const query = new URLSearchParams({ opportunity: context.executiveCase.opportunity.opportunity_id, locale: state.locale, mode: claim.branch === "SIMULATED" ? "simulated" : "public", graphView: "evidence_to_change" });
  region.innerHTML = `<section class="executive-source-panel" data-claim-evidence data-claim-status="${claim.status}" tabindex="-1" aria-label="${esc(label("ui", "sources"))}"><button data-close-claim>${esc(label("ui", "close_sources"))}</button><h3>${esc(label("ui", "sources"))} · ${code(claimId)}</h3><p class="executive-status">${esc(label("status", claim.status))}</p>${claim.synthetic_flag ? policyLabels(claim.display_labels) : ""}${claim.missing_need_codes.length ? `<h4>${esc(label("ui", "case_needs"))}</h4>${sourceCaption()}<ul>${claim.missing_need_codes.map((need) => `<li>${sourceCaption()}${sourceIsland(need)}</li>`).join("")}</ul>` : ""}${claim.evidence_ids.length ? passports(claim, context) : `<p>${esc(label("ui", "no_sources"))}</p>`}<p>${esc(label("ui", "graph_note"))}</p><a href="/?${esc(query)}" data-claim-graph>${esc(label("ui", "graph"))}</a></section>`;
  const panel = region.querySelector("[data-claim-evidence]");
  panel.focus();
  panel.scrollIntoView({ block: "start" });
}

export function handleClaimAction(event, context, region) {
  const trigger = event.target.closest("[data-claim-id]");
  if (trigger) openClaimEvidence(trigger.dataset.claimId, trigger, context, region);
  if (event.target.closest("[data-close-claim]")) closeClaimEvidence();
  const reference = event.target.closest("[data-passport-ref]");
  if (reference && activeRegion?.contains(reference)) {
    event.preventDefault();
    document.getElementById(reference.getAttribute("href").slice(1))?.focus();
  }
}
