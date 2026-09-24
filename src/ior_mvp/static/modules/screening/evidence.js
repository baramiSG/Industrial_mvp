import {
  escapeHtml,
  technicalToken,
} from "../dom.js";
import { t } from "../i18n.js";
import { screeningLabel } from "./labels.js";
import { renderRecordPassports } from "./record-evidence.js";

function reasonItems(codes = []) {
  return codes.map(
    (code) => `<li>${escapeHtml(screeningLabel("reason", code))}</li>`,
  ).join("");
}

function statusLine(labelKey, record = {}) {
  const status = record.status || "NOT_CALCULABLE";
  return `
    <article class="coverage-card">
      <h5>${escapeHtml(t(labelKey))}</h5>
      <strong>${escapeHtml(screeningLabel("status", status))}</strong>
      <ul>${reasonItems(record.reason_codes)}</ul>
    </article>
  `;
}

export function renderCoverageAccounting(summary) {
  const coverage = summary?.coverage_accounting || {};
  const partner = coverage.partner_detail || {};
  return `
    <div class="coverage-accounting">
      <h4>${escapeHtml(t("screening.coverage.title"))}</h4>
      <div class="coverage-grid">
        ${statusLine("screening.coverage.tariff_tree", coverage.tariff_tree)}
        <article class="coverage-card">
          <h5>${escapeHtml(t("screening.coverage.partner_detail"))}</h5>
          <strong>${escapeHtml(t("screening.coverage.partner_detail_counts", {
            covered: partner.covered_hs6_count ?? 0,
            requested: partner.requested_hs6_count ?? 0,
          }))}</strong>
          <ul>${reasonItems(partner.reason_codes)}</ul>
        </article>
        ${statusLine(
          "screening.coverage.production_aggregates",
          coverage.production_aggregates,
        )}
        ${statusLine(
          "screening.coverage.entity_artifact",
          coverage.entity_artifact,
        )}
      </div>
    </div>
  `;
}

function unitKey(value) {
  return Array.isArray(value) ? value.map(String).join(":") : "";
}

function flowYear(value) {
  const [flow, year] = Array.isArray(value) ? value : ["", ""];
  return `${escapeHtml(screeningLabel("flow", flow))} ${technicalToken(year)}`;
}

function unitFields(unit) {
  if (!unit) {
    return `<p class="explicit-state">${escapeHtml(t("common.unavailable"))}</p>`;
  }
  const superseded = unit.superseded_run_ids?.length
    ? unit.superseded_run_ids.map(technicalToken).join(" ")
    : escapeHtml(t("screening.evidence.no_superseded_runs"));
  return `
    <dl class="passport-fields">
      <div><dt>${escapeHtml(t("screening.evidence.completeness_basis"))}</dt><dd>${technicalToken(unit.completeness_basis)}</dd></div>
      <div><dt>${escapeHtml(t("screening.evidence.query_hash"))}</dt><dd>${technicalToken(unit.query_hash)}</dd></div>
      <div><dt>${escapeHtml(t("screening.evidence.selected_run"))}</dt><dd>${technicalToken(unit.selected_run_id)}</dd></div>
      <div><dt>${escapeHtml(t("screening.evidence.superseded_runs"))}</dt><dd>${superseded}</dd></div>
    </dl>
  `;
}

function passportCard(passport, unit) {
  const retrieval = passport.retrieval || {};
  return `
    <article id="passport-${escapeHtml(passport.passport_id)}" class="passport-card" tabindex="-1">
      <h4>${escapeHtml(t("screening.evidence.passport_id"))} ${technicalToken(passport.passport_id)}</h4>
      <dl class="passport-fields">
        <div><dt>${escapeHtml(t("screening.evidence.passport_source"))}</dt><dd>${technicalToken(passport.source_id)}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_stage"))}</dt><dd>${technicalToken(passport.stage)}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_unit"))}</dt><dd>${flowYear(passport.unit_key)}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_class"))}</dt><dd>${technicalToken(passport.evidence_class)}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_status"))}</dt><dd><span data-screening-reviewer-status="${escapeHtml(passport.status)}">${passport.status === "unconfirmed_by_responsible_authority" ? escapeHtml(t("graph.reviewer.unconfirmed_by_responsible_authority")) : technicalToken(passport.status)}</span></dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_coverage"))}</dt><dd>${escapeHtml(screeningLabel("status", passport.coverage_status))}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_endpoint"))}</dt><dd>${technicalToken(retrieval.endpoint_or_document)}</dd></div>
        <div><dt>${escapeHtml(t("screening.evidence.passport_retrieved"))}</dt><dd>${technicalToken(retrieval.retrieved_at)}</dd></div>
      </dl>
      ${unitFields(unit)}
    </article>
  `;
}

export function renderScreeningEvidence(evidence) {
  const passports = evidence?.evidence_passports || [];
  const units = evidence?.universe_units || [];
  if (!passports.length) {
    return `
      <h3 id="screening-evidence-title">${escapeHtml(t("screening.evidence.title"))}</h3>
      <p>${escapeHtml(t("screening.evidence.intro"))}</p>
      <p class="explicit-state" data-evidence-state="none">${escapeHtml(t("screening.evidence.no_snapshot"))}</p>
      <ul>${reasonItems(evidence?.reason_codes)}</ul>
      ${technicalToken((evidence?.reason_codes || [])[0] || "NO_SCREENING_SNAPSHOT")}
    `;
  }
  const unitsByKey = new Map(units.map((unit) => [unitKey(unit.unit_key), unit]));
  const passportKeys = new Set(passports.map((row) => unitKey(row.unit_key)));
  const cards = passports.map(
    (passport) => passportCard(passport, unitsByKey.get(unitKey(passport.unit_key))),
  ).join("");
  const unmatched = units.filter((unit) => !passportKeys.has(unitKey(unit.unit_key)))
    .map((unit) => `
      <article class="unit-card explicit-state">
        <h4>${flowYear(unit.unit_key)}</h4>
        <p>${escapeHtml(t("screening.evidence.unit_without_passport"))}</p>
        ${unitFields(unit)}
      </article>
    `).join("");
  return `
    <h3 id="screening-evidence-title">${escapeHtml(t("screening.evidence.title"))}</h3>
    <p>${escapeHtml(t("screening.evidence.intro"))}</p>
    <div class="passport-grid">${cards}${unmatched}</div>
    <p class="explicit-state">${escapeHtml(t("screening.evidence.passport_detail_not_exposed"))}</p>
  `;
}

export function renderEvidenceBasis(record, summary, evidence) {
  const notEvaluated = (record.rules_not_evaluated_at_screening || [])
    .map((rule) => `<li>${technicalToken(rule)}</li>`).join("");
  const references = (evidence?.evidence_passports || []).map((passport) => `
    <li><a href="#passport-${escapeHtml(passport.passport_id)}" data-passport-ref data-passport-scope="universe">
      ${escapeHtml(t("screening.evidence.passport_reference"))}
      ${flowYear(passport.unit_key)} ${technicalToken(passport.passport_id)}
    </a></li>
  `).join("");
  return `
    <section class="record-evidence-basis">
      <h3>${escapeHtml(t("screening.record.evidence_basis_title"))}</h3>
      <p>${escapeHtml(t("screening.record.evidence_basis_intro"))}</p>
      ${renderCoverageAccounting(summary)}
      <h4>${escapeHtml(t("screening.record.not_evaluated"))}</h4>
      <p>${escapeHtml(t("screening.not_evaluated_reason.inputs_not_public_at_screening_grain"))}</p>
      <ul data-not-evaluated-rules>${notEvaluated}</ul>
      ${renderRecordPassports(record, evidence)}
      <ul data-passport-refs="universe">${references}</ul>
    </section>
  `;
}
