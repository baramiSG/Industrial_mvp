import { state } from "../state.js";
import { STEP_IDS } from "./labels.js";

export const executive = {
  epoch: 0, summary: null, context: null, selection: null,
  loading: true, error: null, sourceTrigger: null,
};

export function nextExecutiveEpoch() { return ++executive.epoch; }
export function isCurrentExecutiveEpoch(epoch) { return epoch === executive.epoch; }

export function readExecutiveLocation(summary) {
  const query = new URL(window.location.href).searchParams;
  const requested = query.get("opportunity");
  const opportunityId = requested || summary.opportunities[0]?.opportunity_id;
  const stepId = STEP_IDS.includes(query.get("step")) ? query.get("step") : "SIGNAL";
  return {
    opportunityId, stepId, locale: ["en", "ar"].includes(query.get("locale")) ? query.get("locale") : state.locale,
    companyId: query.get("company"), plantId: query.get("plant"),
    lineId: query.get("line"), requirementId: query.get("requirement"),
    invalidOpportunity: Boolean(opportunityId && !summary.opportunities.some(
      (row) => row.opportunity_id === opportunityId,
    )),
  };
}

export function writeExecutiveLocation(selection, { replace = false } = {}) {
  const url = new URL(window.location.href);
  url.searchParams.set("opportunity", selection.opportunityId);
  url.searchParams.set("step", selection.stepId);
  url.searchParams.set("locale", selection.locale);
  for (const [key, value] of Object.entries({
    company: selection.companyId, plant: selection.plantId,
    line: selection.lineId, requirement: selection.requirementId,
  })) {
    if (value) url.searchParams.set(key, value);
    else url.searchParams.delete(key);
  }
  window.history[replace ? "replaceState" : "pushState"]({}, "", url);
}
