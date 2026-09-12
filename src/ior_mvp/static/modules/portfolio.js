import {
  getJSON,
  opportunityListEndpoint,
} from "./api.js";
import {
  decisionChip,
  escapeHtml,
  sourceIsland,
  syntheticLabels,
  technical,
  technicalToken,
} from "./dom.js";
import { integer, number, usd } from "./formatters.js";
import { t } from "./i18n.js";
import { state } from "./state.js";
import { loadOpportunity } from "./workspace.js";

export function displayName(item) {
  return state.locale === "ar" && item.name_ar
    ? item.name_ar
    : item.name_en;
}

export function renderKPIs() {
  const activeStates = state.opportunities.reduce((accumulator, item) => {
    accumulator[item.active_state] = (accumulator[item.active_state] || 0) + 1;
    return accumulator;
  }, {});
  const resolved = (activeStates.ADVANCE || 0) + (activeStates.REJECT || 0);
  const imports = state.opportunities.reduce(
    (sum, item) => sum + (item.latest_imports_usd_m || 0),
    0,
  );
  const metrics = [
    [t("kpi.loaded_label"), integer(state.opportunities.length), t("kpi.loaded_note")],
    [
      t("kpi.decisive_label"),
      integer(resolved),
      t(
        state.mode === "simulated"
          ? "kpi.decisive_simulated_note"
          : "kpi.decisive_public_note",
      ),
    ],
    [t("kpi.imports_label"), usd(imports), t("kpi.imports_note")],
    [t("kpi.leakage_label"), integer(0), t("kpi.leakage_note")],
  ];
  document.getElementById("kpi-grid").innerHTML = metrics.map(
    ([label, value, note]) => `
      <article class="kpi-card">
        <small>${escapeHtml(label)}</small>
        <strong>${technical(value)}</strong>
        <p>${escapeHtml(note)}</p>
      </article>
    `,
  ).join("");
}

export function renderOpportunityCards() {
  const disclosure = state.mode === "simulated"
    ? `<div class="portfolio-synthetic-disclosure">${syntheticLabels(
      state.ui.synthetic_labels,
      "synthetic-warning synthetic-labels",
    )}</div>`
    : "";
  const cards = state.opportunities.map(
    (item) => {
      const arabicPrimary = state.locale === "ar" && item.name_ar;
      return `
        <article class="opportunity-card">
          <div class="opportunity-top">
            <div>
              <span class="opportunity-code">${technicalToken(`${t("technical.hs")} ${item.hs6}`)} · ${sourceIsland(item.sector_profile.replaceAll("_", " "))}</span>
              <h3 ${arabicPrimary ? 'lang="ar" dir="rtl"' : 'lang="en" dir="ltr"'}>${escapeHtml(displayName(item))}</h3>
            </div>
            ${decisionChip(item.active_state, item.screening_disposition)}
          </div>
          ${arabicPrimary
            ? sourceIsland(item.name_en, "p")
            : `<p class="arabic" lang="ar" dir="rtl">${escapeHtml(item.name_ar)}</p>`}
          <div class="opportunity-stats">
            <div><small>${escapeHtml(t("opportunity.public_state"))}</small><b>${decisionChip(item.real_state, item.screening_disposition)}</b></div>
            <div><small>${escapeHtml(t("opportunity.imports", { year: integer(item.latest_year) }))}</small><b>${technical(usd(item.latest_imports_usd_m))}</b></div>
            <div><small>${escapeHtml(t("opportunity.quantity"))}</small><b>${technical(`${number(item.latest_imports_kt)} ${t("unit.kt")}`)}</b></div>
          </div>
          <button class="card-action" data-open-id="${escapeHtml(item.id)}">${escapeHtml(t("opportunity.open"))}</button>
        </article>
      `;
    },
  ).join("");
  document.getElementById("opportunity-grid").innerHTML = disclosure + cards;
}

export function populateSelect() {
  const select = document.getElementById("opportunity-select");
  select.innerHTML = state.opportunities.map((item) => `
    <option value="${escapeHtml(item.id)}">${escapeHtml(t("opportunity.option", {
      hs6: item.hs6,
      name: displayName(item),
    }))}</option>
  `).join("");
  select.value = state.selectedId || "";
}

export async function loadPortfolio() {
  state.opportunities = await getJSON(opportunityListEndpoint(state.mode));
  if (!state.opportunities.some((item) => item.id === state.selectedId)) {
    state.selectedId = state.opportunities[0]?.id || null;
  }
  renderKPIs();
  renderOpportunityCards();
  populateSelect();
  if (state.selectedId) await loadOpportunity(state.selectedId);
}
