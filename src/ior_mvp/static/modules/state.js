export const state = {
  mode: "public",
  locale: "en",
  ui: null,
  opportunities: [],
  selectedId: null,
  analysis: null,
  manifest: null,
  extraction: null,
  requestEpoch: 0,
  selection: {
    data: null,
    error: null,
    requestEpoch: 0,
  },
  screening: {
    summary: null,
    evidence: null,
    view: "summary",
    queueId: null,
    offset: 0,
    page: null,
    record: null,
    requestEpoch: 0,
  },
};

export function nextRequestEpoch() {
  state.requestEpoch += 1;
  return state.requestEpoch;
}
