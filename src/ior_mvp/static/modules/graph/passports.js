import { escapeHtml, technicalToken, sourceIsland } from "../dom.js";
import { t } from "../i18n.js";
import { state } from "../state.js";

const STATUS_KEYS = Object.freeze({
  observed: "graph.status.observed", calculated: "graph.status.calculated",
  model_estimated: "graph.status.model_estimated", inferred: "graph.status.inferred",
  assumption: "graph.status.assumption", unresolved: "graph.status.unresolved",
  synthetic: "graph.status.synthetic",
});
const MACHINE_SOURCES = new Set(["DEMO_GENERATOR", "producer_altaiseer_talco", "producer_alupco", "wco_hs_nomenclature"]);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$/;
const unavailable = () => escapeHtml(t("common.unavailable"));
const absent = (value) => value === null || value === undefined || value === "" || value === "UNAVAILABLE";

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

function caption(id = "") {
  return state.locale === "ar" ? `<span class="source-language-caption"${id ? ` id="${escapeHtml(id)}"` : ""} lang="ar" dir="rtl">${escapeHtml(t("source_language.caption"))}</span>` : "";
}

function sourceText(value, captionId = "") {
  if (absent(value) || !["string", "number"].includes(typeof value)) return unavailable();
  const runs = [];
  for (const char of String(value)) {
    const language = /[\u0600-\u06ff]/.test(char) ? "ar" : /[A-Za-z]/.test(char) ? "en" : /\p{L}/u.test(char) ? "und" : null;
    const last = runs.at(-1);
    if (!last) runs.push({ language, text: char });
    else if (!language || !last.language || language === last.language) {
      last.text += char; last.language ||= language;
    } else runs.push({ language, text: char });
  }
  let english = 0;
  return runs.map(({ language, text }) => {
    if (language === "en") return sourceIsland(text) + caption(captionId ? `${captionId}${english++ ? "-" + english : ""}` : "");
    return `<span lang="${language || "und"}" dir="${language === "ar" ? "rtl" : "auto"}">${escapeHtml(text)}</span>`;
  }).join("");
}

function technical(value) {
  return absent(value) || !["string", "number"].includes(typeof value) ? unavailable() : technicalToken(value);
}

function valueSpan(name, rendered) {
  return `<span data-passport-value="${name}">${rendered}</span>`;
}

function field(labelKey, name, rendered) {
  return `<div><dt>${escapeHtml(t(labelKey))}</dt><dd>${valueSpan(name, rendered)}</dd></div>`;
}

function template(key, values) {
  const markers = Object.fromEntries(Object.keys(values).map((name) => [name, `__IOR_${name}__`]));
  let text = escapeHtml(t(key, markers));
  for (const name of Object.keys(values)) text = text.replaceAll(markers[name], values[name]);
  return text;
}

function documentAddress(value) {
  if (typeof value === "string") return `<li>${valueSpan("document_address", sourceText(value))}</li>`;
  if (!value || typeof value !== "object" || Array.isArray(value)) return "";
  const page = value.page_index ?? value.page;
  const line = value.line_index ?? value.line;
  return `<li>${template("graph.document_address", {
    document: technical(value.document_id ?? value.document),
    page: Number.isInteger(page) ? technical(page) : unavailable(),
    line: Number.isInteger(line) ? technical(line) : unavailable(),
  })}</li>`;
}

export function renderGraphDisclosure(labels) {
  if (!labels || typeof labels.en !== "string" || typeof labels.ar !== "string") throw new Error("GRAPH_DISCLOSURE_INVALID");
  const order = state.locale === "ar" ? ["ar", "en"] : ["en", "ar"];
  return `<div class="synthetic-warning synthetic-labels">${order.map((locale) => locale === "en" ? sourceIsland(labels.en) + caption() : `<span lang="ar" dir="rtl">${escapeHtml(labels.ar)}</span>`).join("")}</div>`;
}

function disclosure(record) {
  if (!record.synthetic_flag) return sourceText(record.display_label);
  let labels = record.display_labels;
  if (!labels) {
    labels = state.ui.synthetic_labels;
    if (!labels || record.display_label !== labels.en) throw new Error("GRAPH_DISCLOSURE_INVALID");
  }
  return renderGraphDisclosure(labels);
}

function recordFields(record, url) {
  const period = typeof record.period === "number" || /^\d{4}(?:\/\d{4})*$/.test(record.period) ? technical(record.period) : sourceText(record.period);
  const status = Object.hasOwn(STATUS_KEYS, record.status) ? escapeHtml(t(STATUS_KEYS[record.status])) : sourceText(record.status);
  const reviewer = record.reviewer_status === "unconfirmed_by_responsible_authority" ? escapeHtml(t("graph.reviewer.unconfirmed_by_responsible_authority")) : sourceText(record.reviewer_status);
  const supports = Array.isArray(record.supports) ? record.supports.length ? `<ul>${record.supports.map((item) => `<li>${valueSpan("support", sourceText(item))}</li>`).join("")}</ul>` : unavailable() : sourceText(record.supports);
  return [
    field("graph.evidence_source", "source", MACHINE_SOURCES.has(record.source) ? technical(record.source) : sourceText(record.source)),
    field("graph.evidence_period", "period", period),
    field("graph.evidence_retrieved", "retrieved_at", ISO_DATE.test(record.retrieved_at) ? technical(record.retrieved_at) : sourceText(record.retrieved_at)),
    field("graph.evidence_status", "status", status),
    field("graph.evidence_class", "evidence_class", /^[ABCDE]$/.test(record.evidence_class) ? technical(record.evidence_class) : sourceText(record.evidence_class)),
    field("graph.evidence_supports", "supports", supports),
    field("graph.evidence_reviewer", "reviewer_status", reviewer),
    field("graph.evidence_contradiction", "contradiction", sourceText(record.contradiction)),
    field("graph.evidence_scenario", "scenario_id", technical(record.scenario_id)),
    field("graph.evidence_disclosure", "disclosure", disclosure(record)),
    field("graph.evidence_url", "url", technical(url)),
  ].join("");
}

export function renderEvidenceResult(result, mode) {
  if (!result) return "";
  const records = result.records.map(({ opportunityId, record }) => {
    const evidenceId = record.evidence_id;
    const anchor = passportAnchor(mode, opportunityId, evidenceId);
    const url = safeExternalUrl(record.url);
    const title = typeof record.title === "string" && !absent(record.title) ? record.title : null;
    const captionId = `${anchor}-source`;
    const described = title && /[A-Za-z]/.test(title) && state.locale === "ar" ? ` aria-describedby="${escapeHtml(captionId)}"` : "";
    const englishTitle = title && /[A-Za-z]/.test(title) && !/[\u0600-\u06ff]|[^\p{Script=Latin}\p{N}\p{P}\p{S}\p{Z}\p{C}]/u.test(title);
    const titleLink = valueSpan("title", englishTitle ? escapeHtml(title) : title ? sourceText(title) : technical(evidenceId));
    const sourceAttributes = englishTitle ? ' class="source-language-island" lang="en" dir="ltr"' : "";
    const linkCaption = described ? caption(captionId) : "";
    const heading = valueSpan("title", title ? sourceText(title) : technical(evidenceId));
    const identity = `<dl class="graph-passport-identity">${field("workspace.opportunity", "opportunity_id", technical(opportunityId))}${field("graph.provenance_id", "evidence_id", technical(evidenceId))}</dl>`;
    return `<a href="#${escapeHtml(anchor)}" data-passport-ref${described}${sourceAttributes}>${titleLink}</a>${linkCaption}<article class="graph-passport" id="${escapeHtml(anchor)}" tabindex="-1" data-passport-id="${escapeHtml(evidenceId)}"><h5>${heading}</h5>${identity}<dl>${recordFields(record, url)}</dl>${url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("graph.evidence_open"))}</a>` : ""}</article>`;
  }).join("");
  const unresolved = result.unresolved.map((evidenceId) => `<li>${template("graph.evidence_unresolved", { evidence_id: technical(evidenceId) })}</li>`).join("");
  const addresses = result.documentAddresses.map(documentAddress).join("");
  return `<div class="graph-evidence-results">${records}${unresolved ? `<ul class="graph-unresolved">${unresolved}</ul>` : ""}${addresses ? `<h5>${escapeHtml(t("graph.document_addresses"))}</h5><ul>${addresses}</ul>` : ""}${!records && !unresolved && !addresses ? `<p>${escapeHtml(t("graph.evidence_none"))}</p>` : ""}</div>`;
}
