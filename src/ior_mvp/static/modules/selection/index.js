import {
  caseSelectionEndpoint,
  getJSON,
} from "../api.js";
import { state } from "../state.js";
import {
  renderSelectionFailure,
  renderSelectionPayload,
} from "./render.js";


export function renderSelection() {
  const root = document.getElementById("case-selection-view");
  if (!root) return;
  if (state.selection.error || !state.selection.data) {
    root.innerHTML = renderSelectionFailure();
    return;
  }
  root.innerHTML = renderSelectionPayload(state.selection.data);
}


export async function loadSelection() {
  const epoch = state.selection.requestEpoch + 1;
  state.selection.requestEpoch = epoch;
  state.selection.error = null;
  try {
    const payload = await getJSON(caseSelectionEndpoint());
    if (epoch !== state.selection.requestEpoch) return;
    state.selection.data = payload;
  } catch (error) {
    if (epoch !== state.selection.requestEpoch) return;
    state.selection.data = null;
    state.selection.error = error;
  }
  renderSelection();
}


export async function retrySelection() {
  await loadSelection();
}
