import {
  getJSON,
  manifestEndpoint,
  opportunityEndpoint,
} from "./api.js";
import {
  escapeHtml,
  sourceIsland,
  technicalToken,
} from "./dom.js";
import { t } from "./i18n.js";
import { renderMethodology } from "./methodology.js";
import { renderComponent } from "./renderers/index.js";
import { nextRequestEpoch, state } from "./state.js";

export function renderManifest() {
  document.getElementById("workspace-manifest").innerHTML = (
    state.manifest.components.map(renderComponent).join("")
  );
}

export function renderWorkspaceTitle() {
  const opportunity = state.analysis.opportunity;
  const name = state.locale === "ar" && opportunity.commercial_name_ar
    ? `<span lang="ar" dir="rtl">${escapeHtml(opportunity.commercial_name_ar)}</span>`
    : sourceIsland(opportunity.commercial_name_en);
  document.getElementById("workspace-title").innerHTML = (
    `${technicalToken(`${t("technical.hs")} ${opportunity.hs6}`)} · ${name}`
  );
}

export async function loadOpportunity(id) {
  state.selectedId = id;
  const epoch = nextRequestEpoch();
  const [analysis, manifest] = await Promise.all([
    getJSON(opportunityEndpoint(id, state.mode)),
    getJSON(manifestEndpoint(id, state.mode)),
  ]);
  if (epoch !== state.requestEpoch) return;
  state.analysis = analysis;
  state.manifest = manifest;
  const select = document.getElementById("opportunity-select");
  if (select.value !== id) select.value = id;
  renderWorkspaceTitle();
  renderManifest();
  renderMethodology();
}

export function rerenderWorkspace() {
  if (!state.analysis || !state.manifest) return;
  renderWorkspaceTitle();
  renderManifest();
  renderMethodology();
}
