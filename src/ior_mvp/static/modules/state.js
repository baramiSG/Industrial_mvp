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
  graph: {
    open: false,
    descriptor: null,
    context: null,
    viewId: "adjacency",
    epoch: 0,
    selectionEpoch: 0,
    loading: false,
    error: null,
    catalogue: null,
    payload: null,
    selected: null,
    evidenceLoading: false,
    evidenceError: false,
    evidenceResult: null,
    evidenceResponses: {},
  },
};

export function nextRequestEpoch() {
  state.requestEpoch += 1;
  return state.requestEpoch;
}
