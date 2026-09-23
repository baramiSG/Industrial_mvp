import { getJSON, graphCatalogueEndpoint, graphViewEndpoint, opportunityEndpoint } from "../api.js";
import { state } from "../state.js";
import { resolveElementEvidence } from "./evidence.js";
import {
  elementReferences, graphElement, validateGraphCatalogue, validateGraphPayload,
} from "./model.js";
import { replaceGraphRoot, renderGraphShell } from "./render.js";
function context(opportunityId, mode, viewId = "adjacency") {
  return { opportunityId, mode, viewId };
}
function sameContext(left, right) {
  return left?.opportunityId === right?.opportunityId
    && left?.mode === right?.mode
    && left?.viewId === right?.viewId;
}
function enabled(props) {
  return props?.mode === state.mode
    && props.opportunity_id === state.selectedId
    && state.analysis?.opportunity?.id === props.opportunity_id
    && state.analysis?.mode === props.mode
    && state.manifest?.context?.opportunity_id === props.opportunity_id
    && state.manifest?.context?.mode === props.mode;
}
function replaceGraph() {
  const root = document.getElementById("graph-view");
  if (!root || !state.graph.descriptor) return;
  replaceGraphRoot(root, renderGraphComponent(state.graph.descriptor));
}
function clearContent({ collapse = true, nextContext = null } = {}) {
  state.graph.epoch += 1;
  state.graph.selectionEpoch += 1;
  state.graph.open = collapse ? false : state.graph.open;
  state.graph.context = nextContext;
  state.graph.viewId = nextContext?.viewId || "adjacency";
  state.graph.loading = false;
  state.graph.error = null;
  state.graph.payload = null;
  state.graph.selected = null;
  state.graph.evidenceLoading = false;
  state.graph.evidenceError = false;
  state.graph.evidenceResult = null;
  state.graph.evidenceResponses = {};
}
function commitAllowed(epoch, requested) {
  return requested.mode === state.mode
    && requested.opportunityId === state.selectedId
    && epoch === state.graph.epoch
    && sameContext(state.graph.context, requested)
    && enabled(state.graph.descriptor);
}
async function fetchView(requested, epoch) {
  if (!commitAllowed(epoch, requested)) return;
  try {
    const payload = validateGraphPayload(
      await getJSON(graphViewEndpoint(
        requested.opportunityId,
        requested.viewId,
        requested.mode,
      )),
      requested,
    );
    if (!commitAllowed(epoch, requested)) return;
    state.graph.payload = payload;
    state.graph.loading = false;
    state.graph.error = null;
  } catch (error) {
    if (!commitAllowed(epoch, requested)) return;
    state.graph.loading = false;
    state.graph.payload = null;
    state.graph.error = {
      kind: String(error?.message || "").startsWith("GRAPH_")
        ? "invalid" : "transport",
    };
  }
  replaceGraph();
}
async function openGraph() {
  if (!enabled(state.graph.descriptor)) return;
  const requested = context(
    state.graph.descriptor.opportunity_id,
    state.graph.descriptor.mode,
    state.graph.viewId,
  );
  clearContent({ collapse: false, nextContext: requested });
  state.graph.open = true;
  state.graph.loading = true;
  const epoch = state.graph.epoch;
  replaceGraph();
  try {
    const catalogue = state.graph.catalogue || validateGraphCatalogue(
      await getJSON(graphCatalogueEndpoint()),
    );
    if (!commitAllowed(epoch, requested)) return;
    state.graph.catalogue = catalogue;
    replaceGraph();
    await fetchView(requested, epoch);
  } catch (error) {
    if (!commitAllowed(epoch, requested)) return;
    state.graph.loading = false;
    state.graph.error = {
      kind: String(error?.message || "").startsWith("GRAPH_")
        ? "invalid" : "transport",
    };
    replaceGraph();
  }
}
async function changeView(viewId) {
  if (!enabled(state.graph.descriptor)
    || !state.graph.catalogue?.views.some((row) => row.view_id === viewId)) return;
  const requested = context(
    state.graph.descriptor.opportunity_id,
    state.graph.descriptor.mode,
    viewId,
  );
  clearContent({ collapse: false, nextContext: requested });
  state.graph.open = true;
  state.graph.loading = true;
  const epoch = state.graph.epoch;
  replaceGraph();
  await fetchView(requested, epoch);
}
async function selectElement(kind, identity) {
  if (!enabled(state.graph.descriptor)) return;
  const element = graphElement(state.graph.payload, kind, identity);
  if (!element) return;
  state.graph.selected = { kind, identity, element };
  state.graph.evidenceLoading = true;
  state.graph.evidenceError = false;
  state.graph.evidenceResult = null;
  const epoch = state.graph.epoch;
  const selectionEpoch = ++state.graph.selectionEpoch;
  const requested = { ...state.graph.context };
  replaceGraph();
  const evidenceResponses = { ...state.graph.evidenceResponses };
  try {
    const result = await resolveElementEvidence({
      payload: state.graph.payload,
      element,
      analysis: state.analysis,
      opportunities: state.opportunities,
      mode: requested.mode,
      fetchAnalysis: (id, mode) => getJSON(opportunityEndpoint(id, mode)),
      cache: evidenceResponses,
    });
    if (!commitAllowed(epoch, requested)
      || state.graph.selectionEpoch !== selectionEpoch
      || state.graph.selected?.identity !== identity) return;
    state.graph.evidenceResponses = evidenceResponses;
    state.graph.evidenceResult = result;
    state.graph.evidenceLoading = false;
  } catch {
    if (!commitAllowed(epoch, requested)
      || state.graph.selectionEpoch !== selectionEpoch
      || state.graph.selected?.identity !== identity) return;
    state.graph.evidenceError = true;
    state.graph.evidenceResult = {
      records: [],
      unresolved: elementReferences(state.graph.payload, element),
      documentAddresses: [],
    };
    state.graph.evidenceLoading = false;
  }
  replaceGraph();
}
export function prepareGraphContext(opportunityId, mode) {
  if (!enabled(state.graph.descriptor)
    || (state.graph.context
      && (state.graph.context.opportunityId !== opportunityId
      || state.graph.context.mode !== mode))) {
    clearContent();
    replaceGraph();
  }
}
export function resetGraph() {
  clearContent();
  replaceGraph();
}
export function renderGraphComponent(props) {
  return renderGraphShell(props, state.graph, enabled(props));
}
export function mountGraphComponent(props) {
  state.graph.descriptor = props;
  if (!enabled(props)) clearContent();
}
export function rerenderGraph() {
  replaceGraph();
}
export async function handleGraphAction(target) {
  if (target.dataset.graphToggle !== undefined) {
    if (state.graph.open) resetGraph();
    else await openGraph();
  } else if (target.dataset.graphView !== undefined) {
    await changeView(target.value);
  } else if (target.dataset.graphSelect) {
    await selectElement(target.dataset.graphSelect, target.dataset.graphId);
  } else if (target.dataset.graphRetry !== undefined) {
    await openGraph();
  }
}
