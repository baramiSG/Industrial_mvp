import { analystClaimContext } from "./claim-links.js";
import { clearAnalystClaims, updateExecutiveLink, openRequestedGraph } from "./analyst-navigation.js";
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
import {
  mountGraphComponent,
  prepareGraphContext,
} from "./graph/index.js";
import { renderComponent } from "./renderers/index.js";
import { nextRequestEpoch, state } from "./state.js";

export function renderManifest() {
  document.getElementById("workspace-manifest").innerHTML = (
    state.manifest.components.map(renderComponent).join("") + '<div id="analyst-claim-sources" class="full"></div>'
  );
  const descriptor = state.manifest.components.find(
    (component) => component.type === "graph_view",
  );
  if (descriptor) mountGraphComponent(descriptor.props);
}

export function renderWorkspaceTitle() {
  updateExecutiveLink();
  const opportunity = state.analysis.opportunity;
  const name = state.locale === "ar" && opportunity.commercial_name_ar
    ? `<span lang="ar" dir="rtl">${escapeHtml(opportunity.commercial_name_ar)}</span>`
    : sourceIsland(opportunity.commercial_name_en);
  document.getElementById("workspace-title").innerHTML = (
    `${technicalToken(`${t("technical.hs")} ${opportunity.hs6}`)} · ${name}`
  );
}

export async function loadOpportunity(id) {
  clearAnalystClaims();
  state.selectedId = id;
  const mode = state.mode;
  prepareGraphContext(id, mode);
  const epoch = nextRequestEpoch();
  const responses = await Promise.allSettled([
    getJSON(opportunityEndpoint(id, mode)),
    getJSON(manifestEndpoint(id, mode)),
    getJSON(`/api/executive/opportunities/${encodeURIComponent(id)}`).catch(() => null),
  ]);
  if (epoch !== state.requestEpoch || state.mode !== mode
    || state.selectedId !== id) return;
  const failure = responses.find((response) => response.status === "rejected");
  if (failure) throw failure.reason;
  const [analysis, manifest, executiveCase] = responses.map((response) => response.value);
  if (analysis?.opportunity?.id !== id || analysis?.mode !== mode
    || manifest?.context?.opportunity_id !== id
    || manifest?.context?.mode !== mode) return;
  state.claimContext = analystClaimContext(executiveCase, analysis);
  state.analysis = analysis;
  state.manifest = manifest;
  const select = document.getElementById("opportunity-select");
  if (select.value !== id) select.value = id;
  renderWorkspaceTitle();
  renderManifest();
  renderMethodology();
  await openRequestedGraph();
}

export function rerenderWorkspace() {
  if (!state.analysis || !state.manifest) return;
  renderWorkspaceTitle();
  renderManifest();
  renderMethodology();
}
