const QUERY_KEYS = Object.freeze({
  company: "company_id", plant: "plant_id", line: "line_id",
  requirement: "requirement_item_id",
});

export function graphRequestContext(opportunityId, mode, viewId, analysis) {
  const query = new URL(window.location.href).searchParams;
  const selected = Object.fromEntries(
    Object.entries(QUERY_KEYS).map(([urlKey, key]) => [key, query.get(urlKey)]),
  );
  const any = Object.values(selected).some(Boolean);
  let invalid = false;
  if (any) {
    if (mode !== "simulated" || analysis?.mode !== "simulated"
      || analysis.opportunity?.id !== opportunityId
      || !analysis.candidate_discovery?.available
      || analysis.candidate_discovery.scenario_id !== analysis.simulation_scenario?.scenario_id) {
      invalid = true;
    } else {
      const rows = analysis.candidate_discovery.rows;
      const company = rows.find((row) => row.entity_kind === "COMPANY"
        && row.entity_id === selected.company_id);
      const plant = selected.plant_id ? rows.find((row) => row.entity_kind === "PLANT"
        && row.entity_id === selected.plant_id
        && row.company_id === selected.company_id) : null;
      const line = selected.line_id ? rows.find((row) => row.entity_kind === "LINE"
        && row.entity_id === selected.line_id
        && row.plant_id === selected.plant_id
        && row.company_id === selected.company_id) : null;
      const subject = line || plant || company;
      invalid = !company || (selected.plant_id && !plant)
        || (selected.line_id && !line)
        || (selected.requirement_item_id && !subject?.findings?.some(
          (finding) => finding.requirement_item_id === selected.requirement_item_id,
        ));
    }
  }
  return { opportunityId, mode, viewId, ...selected, invalid };
}

export function sameGraphContext(left, right) {
  return ["opportunityId", "mode", "viewId", "company_id", "plant_id",
    "line_id", "requirement_item_id", "invalid"].every(
    (key) => left?.[key] === right?.[key],
  );
}

export function responseMatchesContext(payload, context) {
  return Object.entries(QUERY_KEYS).every(([, key]) =>
    (payload.context?.[key] ?? null) === (context[key] ?? null),
  ) && (context.mode === "public" || !context.invalid);
}

export function graphEnabled(props) {
  return props?.mode === state.mode
    && props.opportunity_id === state.selectedId
    && state.analysis?.opportunity?.id === props.opportunity_id
    && state.analysis?.mode === props.mode
    && state.manifest?.context?.opportunity_id === props.opportunity_id
    && state.manifest?.context?.mode === props.mode;
}

export function graphCommitAllowed(epoch, requested) {
  return requested.mode === state.mode
    && requested.opportunityId === state.selectedId
    && epoch === state.graph.epoch
    && sameGraphContext(state.graph.context, requested)
    && graphEnabled(state.graph.descriptor);
}

export function consumeGraphOpenRequest() {
  const url = new URL(window.location.href);
  if (url.searchParams.get("graphOpen") !== "1") return false;
  url.searchParams.delete("graphOpen");
  window.history.replaceState(window.history.state, "", url);
  return true;
}
import { state } from "../state.js";
