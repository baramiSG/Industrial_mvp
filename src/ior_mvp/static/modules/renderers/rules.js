import {
  escapeHtml,
  executionChip,
  fireText,
  ruleBoundaryChip,
  sourceCaption,
  sourceIsland,
  technical,
} from "../dom.js";
import { t } from "../i18n.js";

export function renderRuleLedger(props) {
  const rows = props.rules.map((row) => `
    <tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
      <td>
        <b>${technical(row.rule_id)}</b> ${ruleBoundaryChip(row)}
        <br>${sourceIsland(row.name)}
      </td>
      <td>
        ${executionChip(row.execution)}
        <br>${fireText(row.fired)}
      </td>
      <td>${sourceIsland(row.result)}</td>
      <td>${sourceIsland(row.decision_effect)}</td>
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
        ${sourceCaption()}
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
