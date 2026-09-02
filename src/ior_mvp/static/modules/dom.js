import { t } from "./i18n.js";
import { state } from "./state.js";

export function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function toast(message) {
  const node = document.getElementById("toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(
    () => node.classList.remove("show"),
    2400,
  );
}

export function technical(value) {
  return `<bdi class="ltr-isolate technical-token" dir="ltr">${escapeHtml(value)}</bdi>`;
}

export function technicalToken(value) {
  return technical(value);
}

export function sourceIsland(value, tag = "span") {
  return `<${tag} class="source-language-island" lang="en" dir="ltr">${escapeHtml(value)}</${tag}>`;
}

export function sourceCaption() {
  return state.locale === "ar"
    ? `<p class="source-language-caption">${escapeHtml(t("source_language.caption"))}</p>`
    : "";
}

export function stateLabel(value) {
  const labels = {
    ADVANCE: () => t("state.advance"),
    REJECT: () => t("state.reject"),
    INVESTIGATE: () => t("state.investigate"),
    MONITOR: () => t("state.monitor"),
  };
  return labels[value]?.() || value;
}

export function executionLabel(value) {
  const labels = {
    FULL: () => t("execution.full"),
    DEGRADED: () => t("execution.degraded"),
    DISABLED: () => t("execution.disabled"),
  };
  return labels[value]?.() || value;
}

function localizedCode(label, value) {
  if (state.locale === "en") {
    return technicalToken(value);
  }
  return `${escapeHtml(label)} ${technicalToken(value)}`;
}

export function stateChip(value) {
  return `<span class="state-chip state-${escapeHtml(value)}">${localizedCode(stateLabel(value), value)}</span>`;
}

export function executionChip(value) {
  return `<span class="exec-chip exec-${escapeHtml(value)}">${localizedCode(executionLabel(value), value)}</span>`;
}

export function labelValue(label, valueHtml) {
  const labelMarker = "__IOR_LABEL__";
  const valueMarker = "__IOR_VALUE__";
  return escapeHtml(t("common.label_value", {
    label: labelMarker,
    value: valueMarker,
  }))
    .replace(labelMarker, `<bdi>${escapeHtml(label)}</bdi>`)
    .replace(valueMarker, valueHtml);
}

export function fireText(value) {
  if (value === true) {
    return `<span class="rule-fire fire-yes">${escapeHtml(t("fire.yes"))}</span>`;
  }
  if (value === false) {
    return `<span class="rule-fire fire-no">${escapeHtml(t("fire.no"))}</span>`;
  }
  return `<span class="rule-fire fire-na">${escapeHtml(t("fire.na"))}</span>`;
}

export function orderedSyntheticLabels(labels) {
  const order = state.locale === "ar" ? ["ar", "en"] : ["en", "ar"];
  return order.map((locale) => labels?.[locale]).filter(Boolean);
}

export function syntheticLabels(labels, className = "synthetic-labels") {
  return `<span class="${className}">${orderedSyntheticLabels(labels)
    .map((label) => `<span>${escapeHtml(label)}</span>`)
    .join("")}</span>`;
}

export function ruleBoundaryChip(row) {
  if (!row.synthetic_flag) return "";
  return syntheticLabels(row.display_labels, "exec-chip exec-DEGRADED synthetic-labels");
}
