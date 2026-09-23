import { escapeHtml, technicalToken } from "../dom.js";
import { t } from "../i18n.js";

export function safeExternalUrl(value) {
  if (typeof value !== "string") return null;
  try {
    const parsed = new URL(value);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null;
  } catch {
    return null;
  }
}

export function passportAnchor(mode, opportunityId, evidenceId) {
  const encoded = [mode, opportunityId, evidenceId]
    .map((value) => encodeURIComponent(value).replaceAll("%", "_"))
    .join("-");
  return `graph-passport-${encoded}`;
}

function field(labelKey, value) {
  const rendered = Array.isArray(value) ? value.join(", ") : value;
  const display = rendered === null || rendered === undefined || rendered === ""
    ? t("common.unavailable") : rendered;
  return `<div><dt>${escapeHtml(t(labelKey))}</dt><dd>${escapeHtml(display)}</dd></div>`;
}

function documentAddress(value) {
  if (typeof value === "string") return `<li>${escapeHtml(value)}</li>`;
  if (!value || typeof value !== "object") return "";
  return `<li>${escapeHtml(t("graph.document_address", {
    document: value.document_id || value.document || "—",
    page: value.page_index ?? value.page ?? "—",
    line: value.line_index ?? value.line ?? "—",
  }))}</li>`;
}

export function renderEvidenceResult(result, mode) {
  if (!result) return "";
  const records = result.records.map(({ opportunityId, record }) => {
    const evidenceId = record.evidence_id;
    const anchor = passportAnchor(mode, opportunityId, evidenceId);
    const url = safeExternalUrl(record.url);
    const title = record.title || evidenceId;
    return `<a href="#${escapeHtml(anchor)}" data-passport-ref>${escapeHtml(title)}</a><article class="graph-passport" id="${escapeHtml(anchor)}" tabindex="-1" data-passport-id="${escapeHtml(evidenceId)}"><h5>${escapeHtml(title)}</h5><p>${technicalToken(opportunityId)} · ${technicalToken(evidenceId)}</p><dl>${field("graph.evidence_source", record.source)}${field("graph.evidence_period", record.period)}${field("graph.evidence_retrieved", record.retrieved_at)}${field("graph.evidence_status", record.status)}${field("graph.evidence_class", record.evidence_class)}${field("graph.evidence_supports", record.supports)}${field("graph.evidence_reviewer", record.reviewer_status)}${field("graph.evidence_contradiction", record.contradiction)}${field("graph.evidence_scenario", record.scenario_id)}${field("graph.evidence_disclosure", record.display_label)}${field("graph.evidence_url", url)}</dl>${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("graph.evidence_open"))}</a>` : ""}</article>`;
  }).join("");
  const unresolved = result.unresolved.map((evidenceId) => `<li>${escapeHtml(t("graph.evidence_unresolved", { evidence_id: evidenceId }))}</li>`).join("");
  const addresses = result.documentAddresses.map(documentAddress).join("");
  return `<div class="graph-evidence-results">${records}${unresolved ? `<ul class="graph-unresolved">${unresolved}</ul>` : ""}${addresses ? `<h5>${escapeHtml(t("graph.document_addresses"))}</h5><ul>${addresses}</ul>` : ""}${!records && !unresolved && !addresses ? `<p>${escapeHtml(t("graph.evidence_none"))}</p>` : ""}</div>`;
}
