import {
  getJSON,
  screeningEvidenceEndpoint,
  screeningQueueEndpoint,
  screeningRecordEndpoint,
  screeningSummaryEndpoint,
} from "../api.js";
import { escapeHtml } from "../dom.js";
import { t } from "../i18n.js";
import { state } from "../state.js";
import { renderScreeningEvidence } from "./evidence.js";
import { renderScreeningQueue } from "./queue.js";
import { renderScreeningRecord } from "./record.js";
import { renderScreeningSummary } from "./summary.js";

function nextEpoch() {
  state.screening.requestEpoch += 1;
  return state.screening.requestEpoch;
}

function viewNode() {
  return document.getElementById("screening-view");
}

function evidenceNode() {
  return document.getElementById("screening-evidence");
}

function summaryQueue(queueId) {
  return state.screening.summary?.queues?.find(
    (row) => row.queue_id === queueId,
  );
}

export function renderCurrentScreeningView() {
  if (!state.screening.summary) return;
  if (state.screening.view === "queue" && state.screening.page) {
    viewNode().innerHTML = renderScreeningQueue(
      state.screening.page,
      summaryQueue(state.screening.queueId),
    );
  } else if (state.screening.view === "record" && state.screening.record) {
    viewNode().innerHTML = renderScreeningRecord(
      state.screening.record,
      state.screening.queueId,
      state.screening.summary,
      state.screening.evidence,
    );
  } else {
    state.screening.view = "summary";
    viewNode().innerHTML = renderScreeningSummary(
      state.screening.summary,
    );
  }
}

export function renderPersistentScreeningEvidence() {
  if (!state.screening.evidence) return;
  evidenceNode().innerHTML = renderScreeningEvidence(
    state.screening.evidence,
  );
}

export async function loadScreening() {
  const epoch = nextEpoch();
  viewNode().innerHTML = escapeHtml(t("screening.loading"));
  evidenceNode().innerHTML = escapeHtml(t("screening.loading"));
  try {
    const [summary, evidence] = await Promise.all([
      getJSON(screeningSummaryEndpoint()),
      getJSON(screeningEvidenceEndpoint()),
    ]);
    if (epoch !== state.screening.requestEpoch) return;
    Object.assign(state.screening, {
      summary,
      evidence,
      view: "summary",
      queueId: null,
      offset: 0,
      page: null,
      record: null,
    });
    renderCurrentScreeningView();
    renderPersistentScreeningEvidence();
  } catch (error) {
    if (epoch !== state.screening.requestEpoch) return;
    const message = `<p class="explicit-state">${escapeHtml(t("screening.error"))}</p>`;
    viewNode().innerHTML = message;
    evidenceNode().innerHTML = message;
    throw error;
  }
}

export async function openQueue(queueId, offset = 0) {
  const epoch = nextEpoch();
  viewNode().innerHTML = escapeHtml(t("screening.loading"));
  const page = await getJSON(
    screeningQueueEndpoint(queueId, offset, 50),
  );
  if (epoch !== state.screening.requestEpoch) return;
  Object.assign(state.screening, {
    view: "queue",
    queueId,
    offset,
    page,
    record: null,
  });
  renderCurrentScreeningView();
}

export async function openRecord(hs6) {
  const epoch = nextEpoch();
  viewNode().innerHTML = escapeHtml(t("screening.loading"));
  const record = await getJSON(screeningRecordEndpoint(hs6));
  if (epoch !== state.screening.requestEpoch) return;
  Object.assign(state.screening, {
    view: "record",
    record,
  });
  renderCurrentScreeningView();
}

export function screeningBack(target) {
  if (target === "summary") {
    state.screening.view = "summary";
    state.screening.queueId = null;
    state.screening.page = null;
  } else if (target === "queue" && state.screening.page) {
    state.screening.view = "queue";
    state.screening.record = null;
  }
  renderCurrentScreeningView();
}

export function rerenderScreening() {
  renderCurrentScreeningView();
  renderPersistentScreeningEvidence();
}
