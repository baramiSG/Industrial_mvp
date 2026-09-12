import {
  decisionChip,
  escapeHtml,
  labelValue,
  narrativeEntry,
  sourceCaption,
  sourceIsland,
  technical,
} from "../dom.js";
import { integer, money, number, usd } from "../formatters.js";
import { t } from "../i18n.js";
import { state } from "../state.js";

export function renderDecisionHero(props) {
  const localized = props.localized_narrative?.[state.locale];
  const conditions = localized?.conditions || props.conditions;
  const killConditions = (
    localized?.kill_conditions || props.kill_conditions
  );
  const headline = localized
    ? narrativeEntry(localized.headline, "h3")
    : `<h3>${sourceIsland(props.headline)}</h3>`;
  const rationale = localized
    ? narrativeEntry(localized.rationale, "p")
    : `<p>${sourceIsland(props.rationale)}</p>`;
  const route = localized
    ? narrativeEntry(localized.route_label, "bdi")
    : sourceIsland(props.route, "bdi");
  return `
    <article class="workspace-card decision-hero">
      <div class="decision-state-large state-${escapeHtml(props.state ?? props.screening_disposition)}">${decisionChip(props.state, props.screening_disposition)}</div>
      <div>
        ${localized ? "" : sourceCaption()}
        ${headline}
        ${rationale}
        <div class="decision-lists">
          <div>
            <b>${escapeHtml(t("decision.conditions"))}</b>
            <ul>${conditions.map((item) => `<li>${localized ? narrativeEntry(item) : sourceIsland(item)}</li>`).join("")}</ul>
          </div>
          <div>
            <b>${escapeHtml(t("decision.kill_conditions"))}</b>
            <ul>${killConditions.map((item) => `<li>${localized ? narrativeEntry(item) : sourceIsland(item)}</li>`).join("")}</ul>
          </div>
        </div>
      </div>
      <span class="route-pill">
        ${labelValue(t("decision.route"), route)}
      </span>
    </article>
  `;
}

export function hhiNote(hhi, threshold) {
  if (hhi == null) return t("metric.hhi_unavailable");
  if (threshold == null) return t("metric.hhi_threshold_unavailable");
  return t("metric.hhi_threshold", { threshold: number(threshold, 2) });
}

export function renderMetricGrid(props) {
  const latest = [...props.trade].sort((a, b) => a.year - b.year).at(-1);
  const capacity = props.capacity;
  const economics = props.economics;
  const hhi = props.supplier_metrics?.partner_value_hhi;
  const threshold = props.supplier_concentration?.hhi_threshold;
  const metrics = [
    [
      t("metric.latest_imports"),
      technical(usd(latest.imports_usd_m)),
      t("metric.latest_imports_note", {
        quantity: number(latest.imports_kt),
        unit: t("unit.kt"),
        year: integer(latest.year),
      }),
      false,
    ],
    [
      t("metric.supplier_hhi"),
      technical(hhi == null ? t("common.unavailable") : number(hhi, 2)),
      hhiNote(hhi, threshold),
      false,
    ],
    [
      t(capacity ? "metric.specification_gap" : "metric.evidence_class"),
      capacity
        ? technical(`${number(capacity.specification_adjusted_gap_kt)} ${t("unit.kt")}`)
        : technical(state.analysis.real_decision.confidence),
      t(capacity ? "metric.gap_note" : "metric.confidence_note"),
      false,
    ],
    [
      t(economics ? "metric.minimum_support" : "metric.decision_object"),
      economics?.minimum_effective_support_m != null
        ? technical(money(economics.minimum_effective_support_m))
        : technical(t("common.unavailable")),
      economics
        ? (
          economics.passes
            ? t("metric.economics_pass")
            : economics.reason || t("metric.no_support")
        )
        : state.analysis.opportunity.decision_object_status.replaceAll("_", " "),
      Boolean(economics && !economics.passes && economics.reason),
    ],
  ];
  return `<div class="metric-panel">${metrics.map(
    ([label, value, note, source]) => `
      <article class="metric-box">
        <small>${escapeHtml(label)}</small>
        <strong>${value}</strong>
        <p>${source ? sourceIsland(note) : escapeHtml(note)}</p>
      </article>
    `,
  ).join("")}</div>`;
}
