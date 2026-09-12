import {
  escapeHtml,
  technicalToken,
} from "../dom.js";
import { t } from "../i18n.js";
import { screeningLabel } from "./labels.js";

function booleanLabel(value) {
  if (value === true) return t("common.yes");
  if (value === false) return t("common.no");
  return t("common.unavailable");
}

function availableValue(value) {
  if (value == null || value === "UNAVAILABLE") {
    return escapeHtml(t("common.unavailable"));
  }
  if (value === "NOT_CALCULABLE") {
    return escapeHtml(screeningLabel("status", value));
  }
  return technicalToken(value);
}

function evidenceReferences(ids = [], scope = "record") {
  if (!ids.length) {
    return escapeHtml(t("screening.record.no_evidence_ids"));
  }
  return ids.map((id) => `
    <a href="#passport-${escapeHtml(id)}" data-passport-ref data-passport-scope="${scope}">
      ${technicalToken(id)}
    </a>
  `).join(" ");
}

export function renderRecordWarnings(record) {
  const warnings = record.warnings || {};
  const continuity = warnings.classification_continuity || {};
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.warnings"))}</h3>
      <dl class="record-facts">
        <div><dt>${escapeHtml(t("screening.record.continuity"))}</dt><dd>
          ${escapeHtml(screeningLabel("continuityStatus", continuity.status))}
          · ${escapeHtml(screeningLabel("continuityPattern", continuity.pattern))}
        </dd></div>
        <div><dt>${escapeHtml(t("screening.record.ratio_warning"))}</dt><dd>${escapeHtml(booleanLabel(warnings.export_import_ratio_warning))}</dd></div>
        <div><dt>${escapeHtml(t("screening.record.ratio_value"))}</dt><dd>${availableValue(warnings.export_import_value_ratio)}</dd></div>
        <div><dt>${escapeHtml(t("screening.record.price_led_growth"))}</dt><dd>${escapeHtml(booleanLabel(warnings.price_led_growth))}</dd></div>
      </dl>
    </section>
  `;
}

export function renderRecordNeeds(record) {
  const needs = (record.evidence_needs || []).map(
    ({ code: need, evidence_ids: evidenceIds }) => `
      <li>
        <strong>${escapeHtml(screeningLabel("need", need))}</strong>
        <span>${evidenceReferences(evidenceIds)}</span>
      </li>
    `,
  ).join("");
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.needs"))}</h3>
      <ul class="record-list">${needs}</ul>
    </section>
  `;
}

export function renderRecordExclusions(record) {
  const rows = (record.exclusions || []).map((exclusion) => `
    <tr>
      <td>${escapeHtml(screeningLabel("exclusion", exclusion.code))}<br>${technicalToken(exclusion.code)}</td>
      <td>${escapeHtml(screeningLabel("exclusionStatus", exclusion.status))}</td>
      <td>${escapeHtml(screeningLabel("exclusionReason", exclusion.reason_code))}</td>
      <td>${evidenceReferences(exclusion.evidence_ids)}</td>
    </tr>
  `).join("");
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.exclusions"))}</h3>
      <div class="card-body-scroll">
        <table class="screening-table">
          <thead><tr>
            <th>${escapeHtml(t("screening.record.exclusion"))}</th>
            <th>${escapeHtml(t("screening.record.exclusion_status"))}</th>
            <th>${escapeHtml(t("screening.record.exclusion_reason"))}</th>
            <th>${escapeHtml(t("screening.record.evidence_ids"))}</th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </section>
  `;
}

export function renderRecordAdjacency(record) {
  const row = (record.ledger || []).find((item) => item.rule_id === "R9-S");
  const metrics = row?.metrics || {};
  return `
    <section class="record-block">
      <h3>${escapeHtml(t("screening.record.adjacency"))}</h3>
      <dl class="record-facts">
        <div><dt>${escapeHtml(t("screening.record.same_process_family"))}</dt><dd>${escapeHtml(booleanLabel(metrics.same_process_family))}</dd></div>
        <div><dt>${escapeHtml(t("screening.record.qualifying_signals"))}</dt><dd>${technicalToken(metrics.qualifying_signal_count ?? t("common.unavailable"))}</dd></div>
        <div><dt>${escapeHtml(t("screening.record.known_gate_failure"))}</dt><dd>${escapeHtml(booleanLabel(metrics.known_hard_gate_failure))}</dd></div>
      </dl>
    </section>
  `;
}

function localPassportCard(passport) {
  return `
    <article id="passport-${escapeHtml(passport.passport_id)}" class="passport-card" tabindex="-1">
      <h5>${technicalToken(passport.passport_id)}</h5>
      <p>${technicalToken(passport.source_id)}</p>
    </article>
  `;
}

export function renderRecordPassports(record, evidence) {
  const passports = record.evidence_passports || [];
  if (!passports.length) {
    return `
      <p class="explicit-state" data-record-passports="none">
        ${escapeHtml(t("screening.record.no_record_passports"))}
      </p>
    `;
  }
  const universeIds = new Set(
    (evidence?.evidence_passports || []).map((row) => row.passport_id),
  );
  const content = passports.map((passport) => (
    universeIds.has(passport.passport_id)
      ? evidenceReferences([passport.passport_id])
      : localPassportCard(passport)
  )).join("");
  return `
    <section class="record-passports">
      <h4>${escapeHtml(t("screening.record.record_passports"))}</h4>
      <div data-passport-scope="record">${content}</div>
    </section>
  `;
}
