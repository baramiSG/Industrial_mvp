import {
  escapeHtml,
  executionLabel,
  fireText,
  stateLabel,
  technicalToken,
} from "../dom.js";
import { number } from "../formatters.js";
import { t } from "../i18n.js";
import { renderEvidenceBasis } from "./evidence.js";
import {
  effectLabel,
  resultLabel,
  ruleName,
} from "./ledger-labels.js";
import { screeningLabel } from "./labels.js";
import {
  renderRecordAdjacency,
  renderRecordExclusions,
  renderRecordNeeds,
  renderRecordWarnings,
} from "./record-evidence.js";

function ledgerRows(record) {
  return (record.ledger || []).map((row) => `
    <tr>
      <td>
        ${escapeHtml(ruleName(row.rule_id))}
        ${technicalToken(row.rule_id)}
      </td>
      <td>${escapeHtml(executionLabel(row.execution))} ${fireText(row.fired)}</td>
      <td>${escapeHtml(resultLabel(row.result_code))}</td>
      <td>${escapeHtml(effectLabel(row.decision_effect_code))}</td>
    </tr>
  `).join("");
}

function renderLedger(record) {
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.ledger"))}</h3>
      <div class="card-body-scroll">
        <table class="screening-table rule-table">
          <thead><tr>
            <th>${escapeHtml(t("rules.rule"))}</th>
            <th>${escapeHtml(t("rules.execution"))}</th>
            <th>${escapeHtml(t("rules.result"))}</th>
            <th>${escapeHtml(t("rules.effect"))}</th>
          </tr></thead>
          <tbody>${ledgerRows(record)}</tbody>
        </table>
      </div>
    </section>
  `;
}

function metricValue(value) {
  if (value == null || value === "UNAVAILABLE") {
    return escapeHtml(t("common.unavailable"));
  }
  if (value === "NOT_CALCULABLE") {
    return escapeHtml(screeningLabel("status", value));
  }
  return technicalToken(
    typeof value === "number" ? number(value, 4) : value,
  );
}

function renderRecordMetrics(record) {
  const rows = Object.entries(record.metrics || {}).map(([key, value]) => `
    <li>
      ${escapeHtml(screeningLabel("metric", key))}
      ${metricValue(value)}
    </li>
  `).join("");
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.metrics"))}</h3>
      <ul class="record-list">${rows}</ul>
    </section>
  `;
}

export function renderScreeningRecord(record, queueId, summary, evidence) {
  const indicated = record.indicated_state
    ? escapeHtml(stateLabel(record.indicated_state))
    : escapeHtml(t("screening.record.no_indication"));
  return `
    <div class="screening-view screening-record" data-current-queue="${escapeHtml(queueId)}">
      <div class="screening-view-header">
        <button data-screening-back="queue">${escapeHtml(t("screening.record.back_to_queue"))}</button>
        <div>
          <p>${escapeHtml(t("screening.record.title"))}</p>
          <h2>${technicalToken(record.hs6)}</h2>
          <p>
            ${escapeHtml(t("screening.record.disposition"))}:
            ${escapeHtml(screeningLabel("disposition", record.screening_disposition))}
          </p>
          <p>
            ${escapeHtml(t("screening.record.disposition_reason"))}:
            ${escapeHtml(screeningLabel("reason", record.disposition_reason_code))}
          </p>
          <p>${escapeHtml(t("screening.record.indicated_state"))}: ${indicated}</p>
          <p>
            ${escapeHtml(t("screening.record.indication_reason"))}:
            ${record.indication_reason_code
              ? escapeHtml(screeningLabel("reason", record.indication_reason_code))
              : escapeHtml(t("screening.record.no_indication"))}
          </p>
        </div>
      </div>
      ${renderLedger(record)}
      ${renderRecordMetrics(record)}
      ${renderRecordExclusions(record)}
      ${renderRecordWarnings(record)}
      ${renderRecordNeeds(record)}
      ${renderRecordAdjacency(record)}
      ${renderEvidenceBasis(record, summary, evidence)}
    </div>
  `;
}
