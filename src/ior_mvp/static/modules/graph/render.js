import {
  escapeHtml,
  sourceIsland,
  syntheticLabels,
  technicalToken,
} from "../dom.js";
import { state } from "../state.js";
import { t } from "../i18n.js";
import { renderDiagram } from "./diagram.js";
import {
  edgeLabel,
  explanationLabel,
  failureLabel,
  nodeKindLabel,
  nodeLabel,
} from "./labels.js";
import { renderEvidenceResult } from "./passports.js";

function selectedIdentity(graph) {
  return graph.selected?.identity || null;
}

function focusDescriptor(root) {
  const active = document.activeElement;
  if (!active || !root.contains(active)) return null;
  if (active.id === "graph-toggle") return { type: "toggle" };
  if (active.id === "graph-view-select") return { type: "view" };
  if (active.id === "graph-scroll-region") return { type: "scroll" };
  if (active.dataset.graphRetry !== undefined) return { type: "retry" };
  if (active.dataset.graphSelect) {
    return {
      type: "element",
      kind: active.dataset.graphSelect,
      identity: active.dataset.graphId,
    };
  }
  return null;
}

export function replaceGraphRoot(root, html) {
  const descriptor = focusDescriptor(root);
  root.outerHTML = html;
  if (!descriptor) return;
  let replacement = null;
  if (descriptor.type === "toggle") {
    replacement = document.getElementById("graph-toggle");
  } else if (descriptor.type === "view") {
    replacement = document.getElementById("graph-view-select");
  } else if (descriptor.type === "scroll") {
    replacement = document.getElementById("graph-scroll-region");
  } else if (descriptor.type === "retry") {
    replacement = document.querySelector("[data-graph-retry]");
  } else {
    replacement = [...document.querySelectorAll(
      `.graph-button-list [data-graph-select="${descriptor.kind}"]`,
    )].find((node) => node.dataset.graphId === descriptor.identity);
  }
  (replacement || document.getElementById("graph-toggle"))?.focus({
    preventScroll: true,
  });
}

function provenance(element) {
  if (!element) return "";
  const value = element.provenance;
  const boundary = value.synthetic_flag
    ? t("graph.boundary_synthetic") : t("graph.boundary_public");
  return `<section class="graph-provenance"><h5>${escapeHtml(t("graph.provenance_title"))}</h5><dl><div><dt>${escapeHtml(t("graph.provenance_id"))}</dt><dd>${technicalToken(value.evidence_id)}</dd></div><div><dt>${escapeHtml(t("graph.provenance_as_of"))}</dt><dd>${technicalToken(value.as_of)}</dd></div><div><dt>${escapeHtml(t("graph.evidence_class"))}</dt><dd>${technicalToken(value.evidence_class)}</dd></div><div><dt>${escapeHtml(t("graph.provenance_boundary"))}</dt><dd>${escapeHtml(boundary)}</dd></div><div><dt>${escapeHtml(t("graph.provenance_derived"))}</dt><dd>${escapeHtml(t(element.derived ? "graph.value_yes" : "graph.value_no"))}</dd></div></dl></section>`;
}

function edgeDirectionIcon() {
  return '<svg class="transition-icon graph-edge-direction" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12h12m-4-4 4 4-4 4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/></svg>';
}

function nativeControls(graph) {
  const payload = graph.payload;
  const selected = selectedIdentity(graph);
  const nodes = payload.nodes.map((node) => {
    const label = nodeLabel(node, state.locale);
    const visible = state.locale === "ar" && !node.name_ar && node.name_en
      ? sourceIsland(label) : escapeHtml(label);
    return `<button type="button" class="graph-element-button${selected === node.id ? " is-selected" : ""}" data-graph-select="node" data-graph-id="${escapeHtml(node.id)}" aria-label="${escapeHtml(t("graph.node_button", { label }))}" aria-pressed="${selected === node.id}"><span>${visible}</span><small>${escapeHtml(nodeKindLabel(node))} · ${technicalToken(node.provenance.evidence_class)}</small></button>`;
  }).join("");
  const edges = payload.edges.map((edge) => {
    const label = edgeLabel(edge);
    return `<button type="button" class="graph-element-button${selected === edge.id ? " is-selected" : ""}" data-graph-select="edge" data-graph-id="${escapeHtml(edge.id)}" aria-label="${escapeHtml(t("graph.edge_button", { label }))}" aria-pressed="${selected === edge.id}"><span>${escapeHtml(label)}</span><small>${technicalToken(edge.source)} ${edgeDirectionIcon()} ${technicalToken(edge.target)}</small></button>`;
  }).join("");
  return `<div class="graph-native-controls"><section><h4>${escapeHtml(t("graph.nodes_title"))}</h4><div class="graph-button-list">${nodes}</div></section><section><h4>${escapeHtml(t("graph.edges_title"))}</h4><div class="graph-button-list">${edges}</div></section></div>`;
}

function details(graph) {
  const element = graph.selected?.element;
  if (!element) return `<p>${escapeHtml(t("graph.selection_none"))}</p>`;
  const labels = element.provenance.synthetic_flag
    ? syntheticLabels(element.display_labels, "synthetic-warning synthetic-labels")
    : "";
  const error = graph.evidenceError
    ? `<p class="graph-unresolved">${escapeHtml(t("graph.error_body"))}</p>` : "";
  return `<div class="graph-details">${labels}${provenance(element)}<h5>${escapeHtml(t("graph.evidence_title"))}</h5>${error}${graph.evidenceLoading ? `<p>${escapeHtml(t("graph.loading"))}</p>` : renderEvidenceResult(graph.evidenceResult, graph.context.mode)}</div>`;
}

function available(graph) {
  const payload = graph.payload;
  const view = graph.catalogue.views.find((row) => row.view_id === graph.viewId);
  const disclosure = payload.synthetic_flag
    ? syntheticLabels(payload.display_labels, "synthetic-warning synthetic-labels")
    : "";
  if (!payload.edges.length) {
    return `${disclosure}<div class="graph-state"><h4>${escapeHtml(t("graph.empty_title"))}</h4><p>${escapeHtml(t("graph.empty_body"))}</p></div>`;
  }
  return `${disclosure}<p class="graph-explanation">${escapeHtml(explanationLabel(payload.explanation))}</p><div class="graph-visual" id="graph-scroll-region" role="region" tabindex="0" aria-label="${escapeHtml(view.label[state.locale])}">${renderDiagram(payload, state.locale, selectedIdentity(graph), { title: view.label[state.locale], description: view.description[state.locale] })}</div>${nativeControls(graph)}<section class="graph-selection"><h4>${escapeHtml(t("graph.details_title"))}</h4>${details(graph)}</section>`;
}

function body(graph) {
  if (graph.loading) return `<div class="graph-state graph-state-loading" aria-live="polite">${escapeHtml(t("graph.loading"))}</div>`;
  if (graph.error) {
    const invalid = graph.error.kind === "invalid";
    return `<div class="graph-state graph-state-error"><h4>${escapeHtml(t(invalid ? "graph.invalid_title" : "graph.error_title"))}</h4><p>${escapeHtml(t(invalid ? "graph.invalid_body" : "graph.error_body"))}</p><button type="button" data-graph-retry>${escapeHtml(t("graph.retry"))}</button></div>`;
  }
  if (graph.payload?.graph_status === "GRAPH_UNAVAILABLE") {
    return `<div class="graph-state graph-state-error"><h4>${escapeHtml(t("graph.unavailable_title"))}</h4><p>${escapeHtml(t("graph.unavailable_body"))}</p><p>${escapeHtml(failureLabel(graph.payload.reason_code))}</p><button type="button" data-graph-retry>${escapeHtml(t("graph.retry"))}</button></div>`;
  }
  return graph.payload ? available(graph) : "";
}

export function renderGraphShell(props, graph, enabled) {
  const views = graph.catalogue?.views || [];
  const options = views.map((view) => `<option value="${escapeHtml(view.view_id)}"${view.view_id === graph.viewId ? " selected" : ""}>${escapeHtml(view.label[state.locale])}</option>`).join("");
  const description = views.find((view) => view.view_id === graph.viewId)?.description?.[state.locale] || t("graph.subtitle");
  return `<section class="workspace-card full graph-card" id="graph-view" data-graph-opportunity="${escapeHtml(props.opportunity_id)}" data-graph-mode="${escapeHtml(props.mode)}"><header class="card-header"><div><h3>${escapeHtml(t("graph.title"))}</h3><p>${escapeHtml(description)}</p></div><button type="button" id="graph-toggle" data-graph-toggle aria-expanded="${graph.open}" aria-controls="graph-panel"${enabled ? "" : " disabled"}>${escapeHtml(t(graph.open ? "graph.close" : "graph.open"))}</button></header><div class="card-body graph-panel" id="graph-panel" aria-label="${escapeHtml(t("graph.panel_aria"))}"${graph.open ? "" : " hidden"}><label for="graph-view-select">${escapeHtml(t("graph.view_selector"))}</label><select id="graph-view-select" data-graph-view${graph.loading ? " disabled" : ""}>${options}</select>${body(graph)}</div></section>`;
}
