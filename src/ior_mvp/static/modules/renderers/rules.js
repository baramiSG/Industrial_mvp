import { claimLink } from "../claim-links.js";
import {
  escapeHtml,
  executionLabel,
  fireText,
  narrativeEntry,
  ruleBoundaryChip,
  sourceIsland,
  technical,
} from "../dom.js";
import { t } from "../i18n.js";
import { state } from "../state.js";

function localizedField(row, field) {
  const localized = row.localized?.[state.locale];
  return localized?.[field]
    ? narrativeEntry(localized[field])
    : sourceIsland(row[field]);
}

export function renderRuleLedger(props) {
  const rows = props.rules.map((row) => `
    <tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
      <td>
        <b>${technical(row.rule_id)}</b> ${ruleBoundaryChip(row)}
        <br>${localizedField(row, "name")}
      </td>
      <td>
        ${escapeHtml(executionLabel(row.execution))}
        <br>${fireText(row.fired)}
      </td>
      <td>${localizedField(row, "result")}</td>
      <td>${localizedField(row, "decision_effect")} ${claimLink(row.synthetic_flag ? "decision.simulated" : `rule.${row.rule_id}`,  state.claimContext)}</td>
    </tr>
  `).join("");
  return `
    <article class="workspace-card full">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("rules.title"))}</h3>
          <p>${escapeHtml(t("rules.subtitle"))}</p>
        </div>
      </div>
      <div class="card-body card-body-scroll">
        <table class="rule-table">
          <thead>
            <tr>
              <th>${escapeHtml(t("rules.rule"))}</th>
              <th>${escapeHtml(t("rules.execution"))}</th>
              <th>${escapeHtml(t("rules.result"))}</th>
              <th>${escapeHtml(t("rules.effect"))}</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </article>
  `;
}
