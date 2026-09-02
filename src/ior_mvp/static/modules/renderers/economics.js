import {
  escapeHtml,
  sourceCaption,
  sourceIsland,
  technical,
} from "../dom.js";
import { money, number, percent } from "../formatters.js";
import { t } from "../i18n.js";

export function renderEconomicsPanel(props) {
  const economics = props.economics || {};
  const competition = props.competition || {};
  const evsi = props.evsi || {};
  const nationalValue = economics.national_value || {};
  const metrics = [
    [t("economics.npv"), economics.unsupported_npv_m == null ? null : money(economics.unsupported_npv_m)],
    [t("economics.irr"), economics.unsupported_irr == null ? null : percent(economics.unsupported_irr, 1)],
    [t("economics.minimum_support"), economics.minimum_effective_support_m == null ? null : money(economics.minimum_effective_support_m)],
    [t("economics.national_value"), nationalValue.incremental_national_value_m_sar == null ? null : money(nationalValue.incremental_national_value_m_sar)],
    [t("economics.capacity_ratio"), competition.post_entry_capacity_to_downside_demand == null ? null : number(competition.post_entry_capacity_to_downside_demand, 2)],
    [t("economics.evsi"), evsi.approximate_evsi_m_sar == null ? null : money(evsi.approximate_evsi_m_sar)],
  ];
  const narratives = [
    economics.reason,
    competition.finding,
  ].filter(Boolean);
  return `
    <article class="workspace-card">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("economics.title"))}</h3>
          <p>${escapeHtml(t("economics.subtitle"))}</p>
        </div>
      </div>
      <div class="card-body">
        ${sourceCaption()}
        <div class="economics-grid">
          ${metrics.map(([label, value]) => `
            <div class="economics-box">
              <small>${escapeHtml(label)}</small>
              <strong>${technical(value ?? t("common.unavailable"))}</strong>
            </div>
          `).join("")}
        </div>
        ${narratives.map((value) => `<div class="control-note">${sourceIsland(value)}</div>`).join("")}
        ${evsi.next_fact
          ? `<div class="control-note"><b>${escapeHtml(t("economics.next_fact"))}</b> ${sourceIsland(evsi.next_fact)}</div>`
          : ""}
      </div>
    </article>
  `;
}
