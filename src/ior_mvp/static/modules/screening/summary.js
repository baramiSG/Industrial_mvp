import {
  escapeHtml,
  stateLabel,
  technicalToken,
} from "../dom.js";
import { integer } from "../formatters.js";
import { t } from "../i18n.js";
import { renderCoverageAccounting } from "./evidence.js";
import { screeningLabel } from "./labels.js";

function reasonList(codes = []) {
  return codes.map(
    (code) => `<li>${escapeHtml(screeningLabel("reason", code))}</li>`,
  ).join("");
}

function universeCard(summary) {
  const universe = summary.universe_status || {};
  const status = universe.status || "UNAVAILABLE";
  const stateBody = status === "UNAVAILABLE"
    ? `<p class="explicit-state">${escapeHtml(t("screening.universe.unavailable_body"))}</p>`
    : status === "PARTIAL"
      ? `<p class="explicit-state">${escapeHtml(t("screening.universe.partial_body"))}</p>`
      : "";
  return `
    <article class="screening-card universe-card">
      <h3>${escapeHtml(t("screening.universe.title"))}</h3>
      <dl class="record-facts">
        <div><dt>${escapeHtml(t("screening.universe.status"))}</dt><dd>${escapeHtml(screeningLabel("status", status))}</dd></div>
        <div><dt>${escapeHtml(t("screening.universe.hs6_count"))}</dt><dd>${technicalToken(integer(universe.hs6_count || 0))}</dd></div>
        <div><dt>${escapeHtml(t("screening.universe.years"))}</dt><dd>${(universe.years_present || []).map((year) => technicalToken(integer(year))).join(" ")}</dd></div>
        <div><dt>${escapeHtml(t("screening.universe.flows"))}</dt><dd>${(universe.flows_present || []).map((flow) => escapeHtml(screeningLabel("flow", flow))).join(" · ")}</dd></div>
        <div><dt>${escapeHtml(t("screening.universe.units"))}</dt><dd>${technicalToken(integer((universe.units || []).length))}</dd></div>
      </dl>
      <h4>${escapeHtml(t("screening.universe.reasons"))}</h4>
      <ul>${reasonList(universe.reason_codes)}</ul>
      ${stateBody}
    </article>
  `;
}

function countItems(values, vocabulary) {
  return Object.entries(values || {}).map(([code, value]) => `
    <li>
      ${vocabulary === "state"
        ? escapeHtml(stateLabel(code))
        : escapeHtml(screeningLabel(vocabulary, code))}
      ${technicalToken(integer(value))}
    </li>
  `).join("");
}

function countsCard(summary) {
  const counts = summary.counts || {};
  return `
    <article class="screening-card counts-card">
      <h3>${escapeHtml(t("screening.counts.title"))}</h3>
      <h4>${escapeHtml(t("screening.counts.dispositions"))}</h4>
      <ul>${countItems(counts.dispositions, "disposition")}</ul>
      <h4>${escapeHtml(t("screening.counts.indications"))}</h4>
      <ul>${countItems(counts.indicated_states, "state")}</ul>
      <h4>${escapeHtml(t("screening.counts.unqueued"))}</h4>
      <p>${technicalToken(integer(summary.unqueued_candidates || 0))}</p>
      <p>${escapeHtml(t("screening.counts.unqueued_note"))}</p>
      <p>${escapeHtml(screeningLabel("reason", "PERSISTENCE_ONLY"))}</p>
    </article>
  `;
}

function mappingCard(summary) {
  const rows = Object.entries(summary.methodology_queue_mapping || {}).map(
    ([reference, value]) => `
      <tr>
        <td>${escapeHtml(reference)}</td>
        <td>${escapeHtml(screeningLabel("status", value.status))}</td>
        <td>${value.queue_id
          ? escapeHtml(screeningLabel("queue", value.queue_id))
          : escapeHtml(screeningLabel("reason", value.reason_code))}</td>
      </tr>
    `,
  ).join("");
  return `
    <article class="screening-card mapping-card">
      <h3>${escapeHtml(t("screening.mapping.title"))}</h3>
      <p>${escapeHtml(t("screening.mapping.note"))}</p>
      <div class="card-body-scroll">
        <table class="screening-table"><tbody>${rows}</tbody></table>
      </div>
    </article>
  `;
}

function queueCards(summary) {
  return (summary.queues || []).map((queue) => `
    <article class="queue-card">
      <h4>${escapeHtml(screeningLabel("queue", queue.queue_id))}</h4>
      <dl class="record-facts">
        <div><dt>${escapeHtml(t("screening.queue.count"))}</dt><dd>${technicalToken(integer(queue.count))}</dd></div>
        <div><dt>${escapeHtml(t("screening.queue.ordering_basis"))}</dt><dd>${queue.ordering_basis.map((code) => escapeHtml(screeningLabel("metric", code))).join(" · ")}</dd></div>
        <div><dt>${escapeHtml(t("screening.queue.methodology_ref"))}</dt><dd>${queue.methodology_ref.startsWith("§")
          ? escapeHtml(queue.methodology_ref)
          : escapeHtml(screeningLabel("queue", queue.queue_id))}</dd></div>
      </dl>
      <button data-queue-id="${escapeHtml(queue.queue_id)}">${escapeHtml(t("screening.queue.open"))}</button>
    </article>
  `).join("");
}

export function renderScreeningSummary(summary) {
  return `
    <div class="screening-view screening-summary">
      <h2>${escapeHtml(t("screening.summary.title"))}</h2>
      <div class="screening-summary-grid">
        ${universeCard(summary)}
        ${countsCard(summary)}
        ${mappingCard(summary)}
      </div>
      ${renderCoverageAccounting(summary)}
      <h3>${escapeHtml(t("screening.queues.title"))}</h3>
      <p>${escapeHtml(t("screening.queues.subtitle"))}</p>
      <div class="queue-grid">${queueCards(summary)}</div>
    </div>
  `;
}
