import {
  escapeHtml,
  sourceCaption,
  sourceIsland,
  syntheticLabels,
  technical,
} from "../dom.js";
import { t } from "../i18n.js";

export function renderEvidenceLedger(props) {
  const rows = props.evidence.map((row) => `
    <tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
      <td><span class="evidence-class">${technical(row.evidence_class)}</span></td>
      <td>${sourceIsland(row.source)}</td>
      <td>
        ${sourceIsland(row.title)}
        ${row.synthetic_flag ? syntheticLabels(row.display_labels) : ""}
      </td>
      <td>${sourceIsland(row.status)}</td>
      <td>
        <span class="exec-chip exec-${row.synthetic_flag ? "DEGRADED" : "FULL"}">
          ${escapeHtml(t(row.synthetic_flag ? "boundary.simulated" : "boundary.public"))}
        </span>
      </td>
    </tr>
  `).join("");
  return `
    <article class="workspace-card full">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("evidence.title"))}</h3>
          <p>${escapeHtml(t("evidence.subtitle"))}</p>
        </div>
      </div>
      <div class="card-body card-body-scroll">
        ${sourceCaption()}
        <table class="evidence-table">
          <thead>
            <tr>
              <th>${escapeHtml(t("evidence.class"))}</th>
              <th>${escapeHtml(t("evidence.source"))}</th>
              <th>${escapeHtml(t("evidence.evidence"))}</th>
              <th>${escapeHtml(t("evidence.status"))}</th>
              <th>${escapeHtml(t("evidence.boundary"))}</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </article>
  `;
}

export function renderDataUnlocks(props) {
  const synthetic = props.synthetic_inputs_used || [];
  return `
    <article class="workspace-card">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("unlocks.title"))}</h3>
          <p>${escapeHtml(t("unlocks.subtitle"))}</p>
        </div>
      </div>
      <div class="card-body">
        ${sourceCaption()}
        <ul class="unlock-list">
          ${props.missing_facts.map(
            (item, index) => `<li><b>${technical(index + 1)}</b>${sourceIsland(item)}</li>`,
          ).join("")}
        </ul>
        ${synthetic.length
          ? `<div class="control-note">
              <b>${escapeHtml(t("unlocks.active_blocks"))}</b>
              ${sourceIsland(synthetic.join(", "))}
              ${syntheticLabels(props.synthetic_labels)}
            </div>`
          : ""}
      </div>
    </article>
  `;
}

export function renderDecisionActions(props) {
  return `
    <article class="workspace-card">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("actions.title"))}</h3>
          <p>${escapeHtml(t("actions.subtitle"))}</p>
        </div>
      </div>
      <div class="card-body">
        <div class="action-row">
          <button class="primary-button" data-dossier-html="${escapeHtml(props.opportunity_id)}">${escapeHtml(t("actions.open_dossier"))}</button>
          <button class="secondary-button" data-copy-json="${escapeHtml(props.opportunity_id)}">${escapeHtml(t("actions.copy_json"))}</button>
        </div>
      </div>
    </article>
  `;
}
