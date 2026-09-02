import {
  escapeHtml,
  executionChip,
  fireText,
  ruleBoundaryChip,
  sourceCaption,
  sourceIsland,
  technical,
} from "./dom.js";
import { integer } from "./formatters.js";
import { t } from "./i18n.js";
import { state } from "./state.js";

export function renderMethodology() {
  if (!state.analysis) return;
  const rules = state.analysis.rules;
  const summary = [
    [t("methodology.full"), rules.filter((row) => row.execution === "FULL").length],
    [t("methodology.degraded"), rules.filter((row) => row.execution === "DEGRADED").length],
    [t("methodology.disabled"), rules.filter((row) => row.execution === "DISABLED").length],
    [t("methodology.signals"), rules.filter((row) => row.fired === true).length],
  ];
  document.getElementById("methodology-summary").innerHTML = `
    <div class="methodology-topline">
      ${summary.map(([label, value]) => `
        <div><small>${escapeHtml(label)}</small><strong>${technical(integer(value))}</strong></div>
      `).join("")}
    </div>
    <div class="methodology-table-wrap">
      ${sourceCaption()}
      <table class="rule-table">
        <thead>
          <tr>
            <th>${escapeHtml(t("rules.rule"))}</th>
            <th>${escapeHtml(t("rules.execution"))}</th>
            <th>${escapeHtml(t("rules.fired"))}</th>
            <th>${escapeHtml(t("rules.result"))}</th>
          </tr>
        </thead>
        <tbody>
          ${rules.map((row) => `
            <tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
              <td><b>${technical(row.rule_id)}</b> ${ruleBoundaryChip(row)} · ${sourceIsland(row.name)}</td>
              <td>${executionChip(row.execution)}</td>
              <td>${fireText(row.fired)}</td>
              <td>${sourceIsland(row.result)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}
