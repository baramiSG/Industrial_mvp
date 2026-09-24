import { state } from "./state.js";
import { handleGraphAction } from "./graph/index.js";
import { closeClaimEvidence, handleClaimAction } from "./executive/evidence.js";

const VIEWS = Object.freeze(["adjacency", "route_blocking", "shared_enabler", "evidence_to_change"]);
let requestedGraph = null;

export function initializeAnalystLocation() {
  const query = new URL(window.location.href).searchParams;
  state.selectedId = query.get("opportunity");
  if (["public", "simulated"].includes(query.get("mode"))) state.mode = query.get("mode");
  if (VIEWS.includes(query.get("graphView"))) requestedGraph = { opportunityId: state.selectedId, mode: state.mode, viewId: query.get("graphView") };
  document.querySelectorAll(".mode-button").forEach((button) => button.classList.toggle("active", button.dataset.mode === state.mode));
  document.addEventListener("click", (event) => handleClaimAction(event, state.claimContext, document.getElementById("analyst-claim-sources")));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeClaimEvidence(); });
}

export function updateExecutiveLink() {
  const link = document.querySelector("[data-executive-link]");
  if (!link) return;
  const query = new URLSearchParams({ opportunity: state.selectedId || "", locale: state.locale });
  link.href = `/executive?${query}`;
}

export function clearAnalystClaims() {
  closeClaimEvidence();
  state.claimContext = null;
  document.querySelectorAll("[data-claim-id]").forEach((node) => node.remove());
}

export async function openRequestedGraph() {
  if (!requestedGraph) return;
  const requested = requestedGraph;
  requestedGraph = null;
  if (state.analysis?.opportunity.id !== requested.opportunityId || state.analysis.mode !== requested.mode) return;
  state.graph.viewId = requested.viewId;
  const toggle = document.getElementById("graph-toggle");
  if (toggle) await handleGraphAction(toggle);
}
