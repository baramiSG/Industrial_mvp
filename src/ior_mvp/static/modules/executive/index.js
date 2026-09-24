import { getJSON } from "../api.js";
import { fetchLocaleBundle, applyLocaleBundle, targetLocale } from "../i18n.js";
import { state } from "../state.js";
import { executive, readExecutiveLocation, writeExecutiveLocation, nextExecutiveEpoch, isCurrentExecutiveEpoch } from "./context.js";
import { loadExecutiveContext } from "./data.js";
import { mountExecutiveShell, renderHeading, renderJourney, renderStatus, clearContextDisplay, renderFailure } from "./render.js";
import { handleClaimAction, closeClaimEvidence } from "./evidence.js";
import { STEP_IDS } from "./labels.js";

async function select(selection, history = "push", reload = false) {
  const epoch = nextExecutiveEpoch();
  const previous = executive.selection;
  const oldContext = executive.context;
  executive.pending = selection;
  renderHeading(selection);
  closeClaimEvidence();
  clearContextDisplay();
  renderStatus("executive.loading");
  try {
    const [bundle, context] = await Promise.all([
      selection.locale !== state.locale ? fetchLocaleBundle(selection.locale) : Promise.resolve(null),
      !reload && oldContext?.executiveCase.opportunity.opportunity_id === selection.opportunityId
        ? Promise.resolve(oldContext) : loadExecutiveContext(selection.opportunityId, executive.summary),
    ]);
    if (!isCurrentExecutiveEpoch(epoch)) return;
    if (history !== "none") writeExecutiveLocation(selection, { replace: history === "replace" });
    if (bundle) applyLocaleBundle(bundle);
    executive.selection = selection;
    executive.context = context;
    executive.pending = null;
    renderHeading();
    renderJourney();
    renderStatus(null);
    if (history === "push") document.querySelector("[data-active-step]").focus({ preventScroll: true });
  } catch {
    if (!isCurrentExecutiveEpoch(epoch)) return;
    if (previous && selection.locale !== previous.locale) {
      executive.pending = null;
      executive.selection = previous;
      executive.context = oldContext;
      writeExecutiveLocation(previous, { replace: true });
      renderHeading();
      renderJourney();
      renderStatus("executive.ui.locale_error");
    } else {
      executive.context = null;
      renderFailure();
    }
  }
}

async function start() {
  const epoch = nextExecutiveEpoch();
  executive.summary = null;
  closeClaimEvidence();
  clearContextDisplay();
  renderStatus("executive.loading");
  try {
    const summary = await getJSON("/api/executive/summary");
    if (!isCurrentExecutiveEpoch(epoch)) return;
    executive.summary = summary;
    const selection = readExecutiveLocation(summary);
    executive.selection = selection;
    renderHeading();
    if (!summary.opportunities.length) { renderFailure("empty"); return; }
    if (selection.invalidOpportunity) { renderFailure("not_found"); return; }
    await select(selection, "replace", true);
  } catch {
    if (isCurrentExecutiveEpoch(epoch)) renderFailure();
  }
}

export async function initExecutive() {
  mountExecutiveShell();
  document.addEventListener("change", (event) => {
    if (event.target.id !== "executive-case") return;
    const selection = executive.pending || executive.selection;
    select({ ...selection, opportunityId: event.target.value, invalidOpportunity: false });
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeClaimEvidence(); });
  document.addEventListener("click", (event) => {
    handleClaimAction(event, executive.context, document.getElementById("executive-sources"));
    const action = event.target.closest("[data-executive-step],[data-executive-go]");
    const step = action?.dataset.executiveStep || action?.dataset.executiveGo;
    const selection = executive.pending || executive.selection;
    if (STEP_IDS.includes(step) && selection) select({ ...selection, stepId: step });
    if (event.target.closest("[data-executive-locale]") && selection) select({ ...selection, locale: targetLocale() });
    if (event.target.closest("[data-executive-retry]")) start();
    if (event.target.closest("[data-executive-first]")) select({ ...selection, opportunityId: executive.summary.opportunities[0].opportunity_id, invalidOpportunity: false });
  });
  window.addEventListener("popstate", () => {
    if (!executive.summary) return;
    const selection = readExecutiveLocation(executive.summary);
    if (selection.invalidOpportunity) { nextExecutiveEpoch(); renderFailure("not_found"); return; }
    select(selection, "none");
  });
  await start();
}
