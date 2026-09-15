import {
  escapeHtml,
  sourceIsland,
  technical,
} from "../dom.js";
import { integer } from "../formatters.js";
import { t } from "../i18n.js";

function technicalList(values) {
  if (!values.length) return `<li>${escapeHtml(t("selection.none"))}</li>`;
  return values.map((value) => `<li>${technical(value)}</li>`).join("");
}

function identityExclusions(values) {
  if (!values.length) return `<li>${escapeHtml(t("selection.none"))}</li>`;
  return values.map((row) => {
    const basis = Object.values(row.basis || {}).filter(Boolean);
    return `
      <li>
        <strong>${technical(row.hs6)}</strong>
        <span>${escapeHtml(t("selection.reason"))}: ${technical(row.reason)}</span>
        ${basis.map((value) => sourceIsland(value, "p")).join("")}
      </li>
    `;
  }).join("");
}

function seriesGaps(values) {
  if (!values.length) return `<li>${escapeHtml(t("selection.none"))}</li>`;
  return values.map((row) => `
    <li>
      <strong>${technical(row.hs6)}</strong>
      <span>${escapeHtml(t("selection.reason"))}: ${technical(row.reason)}</span>
      <span>${escapeHtml(t("selection.missing_years"))}: ${technical(
    row.missing_import_years.map(integer).join(", "),
  )}</span>
    </li>
  `).join("");
}

function referenceRows(inputs) {
  const rows = [
    inputs.screening,
    inputs.universe,
    inputs.product_families,
    inputs.terms,
    inputs.identity_exclusions,
    inputs.documents,
  ].filter(Boolean);
  return rows.map((row) => {
    const identity = row.snapshot_id || row.version || row.file_count || "";
    const digest = row.sha256 || row.files_sha256 || "";
    return `
      <li>
        ${technical(row.path)}
        ${identity ? technical(identity) : ""}
        ${digest ? technical(digest) : ""}
      </li>
    `;
  }).join("");
}

function profileHeading(profile) {
  const marker = "__IOR_PROFILE_IDENTIFIER__";
  return escapeHtml(t("selection.profile_quota", {
    profile: marker,
    quota: integer(profile.quota),
  })).replace(marker, technical(profile.profile));
}

function profileCard(profile) {
  return `
    <article class="selection-profile">
      <header>
        <h3>${profileHeading(profile)}</h3>
      </header>
      <div class="selection-columns">
        <section>
          <h4>${escapeHtml(t("selection.selected"))}</h4>
          <ul>${technicalList(profile.selected)}</ul>
        </section>
        <details>
          <summary data-selection-detail="${escapeHtml(profile.profile)}:substitution">${escapeHtml(t("selection.substitution_order"))}</summary>
          <ol>${technicalList(profile.substitution_order)}</ol>
        </details>
        <details>
          <summary data-selection-detail="${escapeHtml(profile.profile)}:identity">${escapeHtml(t("selection.identity_exclusions"))}</summary>
          <ul>${identityExclusions(profile.excluded_by_identity)}</ul>
        </details>
        <details>
          <summary data-selection-detail="${escapeHtml(profile.profile)}:viability">${escapeHtml(t("selection.viability_exclusions"))}</summary>
          <ul>${technicalList(profile.excluded_by_viability)}</ul>
        </details>
        <details>
          <summary data-selection-detail="${escapeHtml(profile.profile)}:series-gap">${escapeHtml(t("selection.series_gap_exclusions"))}</summary>
          <ul>${seriesGaps(profile.excluded_series_gap_years)}</ul>
        </details>
        <details>
          <summary data-selection-detail="${escapeHtml(profile.profile)}:frozen">${escapeHtml(t("selection.frozen_exclusions"))}</summary>
          <ul>${technicalList(profile.excluded_frozen)}</ul>
        </details>
      </div>
    </article>
  `;
}

export function renderSelectionPayload(payload) {
  return `
    <div class="selection-summary">
      <p>
        <strong>${escapeHtml(t("selection.reference"))}</strong>
        ${technical(payload.selection_id)}
        ${technical(payload.rule_version)}
      </p>
      <p>${technical(payload.selection_reference.path)}</p>
    </div>
    <div class="selection-profiles">
      ${payload.profiles.map(profileCard).join("")}
    </div>
    <details class="selection-inputs">
      <summary data-selection-detail="inputs">${escapeHtml(t("selection.inputs"))}</summary>
      <ul>${referenceRows(payload.input_references)}</ul>
    </details>
  `;
}

export function renderSelectionFailure() {
  return `
    <div class="selection-failure" role="alert">
      <p>${escapeHtml(t("selection.unavailable"))}</p>
      <button type="button" class="secondary-button" data-selection-retry>
        ${escapeHtml(t("selection.retry"))}
      </button>
    </div>
  `;
}
