import {
  escapeHtml,
  stateLabel,
  technicalToken,
} from "../dom.js";
import { integer, number } from "../formatters.js";
import { t } from "../i18n.js";
import { screeningLabel } from "./labels.js";

function metricValue(value) {
  return typeof value === "number"
    ? number(value, 4)
    : value ?? t("common.unavailable");
}

function metricList(metrics = {}) {
  return Object.entries(metrics).map(([key, value]) => `
    <li>
      ${escapeHtml(screeningLabel("metric", key))}
      ${technicalToken(metricValue(value))}
    </li>
  `).join("");
}

function reasonList(codes = []) {
  return codes.map(
    (code) => `<li>${escapeHtml(screeningLabel("queueReason", code))}</li>`,
  ).join("");
}

function queueRow(entry) {
  return `
    <tr>
      <td>${technicalToken(entry.hs6)}</td>
      <td>${technicalToken(integer(entry.pareto_rank))}</td>
      <td>
        ${escapeHtml(screeningLabel("disposition", entry.screening_disposition))}
      </td>
      <td>${entry.indicated_state
        ? escapeHtml(stateLabel(entry.indicated_state))
        : escapeHtml(t("screening.record.no_indication"))}</td>
      <td><ul>${reasonList(entry.queue_reason_codes)}</ul></td>
      <td><ul>${metricList(entry.ordering_metrics)}</ul></td>
      <td>
        <button data-hs6="${escapeHtml(entry.hs6)}">
          ${escapeHtml(t("screening.queue.open_record"))}
        </button>
      </td>
    </tr>
  `;
}

function pagination(page) {
  const start = page.total ? page.offset + 1 : 0;
  const end = Math.min(page.offset + page.entries.length, page.total);
  const previous = page.offset > 0
    ? `<button data-screening-page="previous">${escapeHtml(t("screening.queue.previous"))}</button>`
    : "";
  const next = page.offset + page.limit < page.total
    ? `<button data-screening-page="next">${escapeHtml(t("screening.queue.next"))}</button>`
    : "";
  return `
    <nav class="screening-pagination">
      ${previous}
      <span>${escapeHtml(t("screening.queue.showing", {
        from: integer(start),
        to: integer(end),
        total: integer(page.total),
      }))}</span>
      ${next}
    </nav>
  `;
}

export function renderScreeningQueue(page, summaryQueue) {
  const header = `
    <div class="screening-view-header">
      <button data-screening-back="summary">${escapeHtml(t("screening.queue.back_to_summary"))}</button>
      <div>
        <h2>${escapeHtml(screeningLabel("queue", page.queue_id))}</h2>
        <p>
          ${escapeHtml(t("screening.queue.count"))}
          ${technicalToken(integer(page.total))}
        </p>
        <p>
          ${escapeHtml(t("screening.queue.ordering_basis"))}:
          ${(summaryQueue?.ordering_basis || page.ordering_basis)
            .map((code) => escapeHtml(screeningLabel("metric", code))).join(" · ")}
        </p>
        <p>
          ${escapeHtml(t("screening.queue.methodology_ref"))}
          ${(summaryQueue?.methodology_ref || "").startsWith("§")
            ? escapeHtml(summaryQueue.methodology_ref)
            : escapeHtml(screeningLabel("queue", page.queue_id))}
        </p>
      </div>
    </div>
  `;
  if (!page.entries.length) {
    return `
      <div class="screening-view screening-queue">
        ${header}
        <section class="explicit-state">
          <h3>${escapeHtml(t("screening.queue.empty"))}</h3>
          <p>${escapeHtml(t("screening.queue.empty_body"))}</p>
        </section>
      </div>
    `;
  }
  return `
    <div class="screening-view screening-queue">
      ${header}
      <p>${escapeHtml(t("screening.queue.pareto_note"))}</p>
      <div class="card-body-scroll">
        <table class="screening-table">
          <thead><tr>
            <th>${escapeHtml(t("screening.queue.hs6"))}</th>
            <th>${escapeHtml(t("screening.queue.pareto_rank"))}</th>
            <th>${escapeHtml(t("screening.queue.disposition"))}</th>
            <th>${escapeHtml(t("screening.queue.indicated_state"))}</th>
            <th>${escapeHtml(t("screening.queue.reasons"))}</th>
            <th>${escapeHtml(t("screening.queue.metrics"))}</th>
            <th></th>
          </tr></thead>
          <tbody>${page.entries.map(queueRow).join("")}</tbody>
        </table>
      </div>
      ${pagination(page)}
    </div>
  `;
}
