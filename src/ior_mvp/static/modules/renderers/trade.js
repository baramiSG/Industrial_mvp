import { escapeHtml } from "../dom.js";
import { integer, number } from "../formatters.js";
import { t } from "../i18n.js";

export function chartPath(values, x, y) {
  return values
    .map((value, index) => `${index === 0 ? "M" : "L"}${x(index)},${y(value)}`)
    .join(" ");
}

export function renderTradeChart(props) {
  const trade = [...props.trade].sort((a, b) => a.year - b.year);
  const width = 760;
  const height = 250;
  const pad = { l: 48, r: 25, t: 20, b: 38 };
  const maxValue = Math.max(...trade.map((row) => row.imports_usd_m || 0)) * 1.12;
  const maxQty = Math.max(...trade.map((row) => row.imports_kt || 0)) * 1.12;
  const x = (index) => pad.l + (
    trade.length === 1 ? 0 : index * ((width - pad.l - pad.r) / (trade.length - 1))
  );
  const yValue = (value) => height - pad.b - (
    (value || 0) / maxValue
  ) * (height - pad.t - pad.b);
  const yQty = (value) => height - pad.b - (
    (value || 0) / maxQty
  ) * (height - pad.t - pad.b);
  const grid = [0, 0.25, 0.5, 0.75, 1].map((fraction) => {
    const y = pad.t + fraction * (height - pad.t - pad.b);
    return `<line class="chart-grid" x1="${pad.l}" y1="${y}" x2="${width - pad.r}" y2="${y}"/>`;
  }).join("");
  const labels = trade.map(
    (row, index) => `<text class="chart-label" x="${x(index)}" y="${height - 12}" text-anchor="middle">${escapeHtml(integer(row.year))}</text>`,
  ).join("");
  const valuePoints = trade.map(
    (row, index) => `<circle class="chart-point-value" cx="${x(index)}" cy="${yValue(row.imports_usd_m)}" r="4"><title>${escapeHtml(t("trade.value_point", { value: number(row.imports_usd_m) }))}</title></circle>`,
  ).join("");
  const qtyPoints = trade.map(
    (row, index) => `<circle class="chart-point-quantity" cx="${x(index)}" cy="${yQty(row.imports_kt)}" r="4"><title>${escapeHtml(t("trade.quantity_point", { value: number(row.imports_kt) }))}</title></circle>`,
  ).join("");
  return `
    <article class="workspace-card full">
      <div class="card-header">
        <div><h3>${escapeHtml(t("trade.title"))}</h3><p>${escapeHtml(t("trade.subtitle"))}</p></div>
        <span class="exec-chip exec-DEGRADED">${escapeHtml(t("trade.boundary"))}</span>
      </div>
      <div class="card-body">
        <div class="chart-wrap">
          <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(t("trade.aria"))}">
            ${grid}
            <line class="chart-axis" x1="${pad.l}" y1="${height - pad.b}" x2="${width - pad.r}" y2="${height - pad.b}"/>
            <path class="chart-value" d="${chartPath(trade.map((row) => row.imports_usd_m), x, yValue)}"/>
            <path class="chart-quantity" d="${chartPath(trade.map((row) => row.imports_kt), x, yQty)}"/>
            ${valuePoints}${qtyPoints}${labels}
          </svg>
        </div>
        <div class="chart-legend">
          <span><i class="legend-dot legend-value"></i>${escapeHtml(t("trade.value"))}</span>
          <span><i class="legend-dot legend-quantity"></i>${escapeHtml(t("trade.quantity"))}</span>
        </div>
      </div>
    </article>
  `;
}
