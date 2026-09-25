import { escapeHtml } from "../dom.js";
import { integer, number } from "../formatters.js";
import { t } from "../i18n.js";

function knownNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

export function chartPath(values, x, y) {
  let penDown = false;
  return values
    .map((value, index) => {
      if (!knownNumber(value)) {
        penDown = false;
        return "";
      }
      const command = penDown ? "L" : "M";
      penDown = true;
      return `${command}${x(index)},${y(value)}`;
    })
    .filter(Boolean)
    .join(" ");
}

export function renderTradeChart(props) {
  const trade = [...props.trade].sort((a, b) => a.year - b.year);
  const width = 760;
  const height = 250;
  const pad = { l: 48, r: 25, t: 20, b: 38 };
  const maxValue = Math.max(
    1,
    ...trade.filter((row) => knownNumber(row.imports_usd_m))
      .map((row) => row.imports_usd_m),
  ) * 1.12;
  const maxQty = Math.max(
    1,
    ...trade.filter((row) => knownNumber(row.imports_kt))
      .map((row) => row.imports_kt),
  ) * 1.12;
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
    (row, index) => knownNumber(row.imports_usd_m)
      ? `<circle class="chart-point-value" cx="${x(index)}" cy="${yValue(row.imports_usd_m)}" r="4"><title>${escapeHtml(t("trade.value_point", { value: number(row.imports_usd_m) }))}</title></circle>`
      : "",
  ).join("");
  const qtyPoints = trade.map(
    (row, index) => knownNumber(row.imports_kt)
      ? `<circle class="chart-point-quantity" cx="${x(index)}" cy="${yQty(row.imports_kt)}" r="4"><title>${escapeHtml(t("trade.quantity_point", { value: number(row.imports_kt) }))}</title></circle>`
      : "",
  ).join("");
  const cell = (value, unit) => knownNumber(value)
    ? `<bdi class="technical-token" dir="ltr">${escapeHtml(number(value))} ${escapeHtml(unit)}</bdi>`
    : escapeHtml(t("trade.data_unavailable"));
  const observedRows = trade.map((row) => `<tr><th scope="row"><bdi dir="ltr">${escapeHtml(integer(row.year))}</bdi></th><td>${cell(row.imports_usd_m, "USD m")}</td><td>${cell(row.imports_kt, "kt")}</td></tr>`).join("");
  const observedData = trade.length
    ? `<table><caption>${escapeHtml(t("trade.data_caption"))}</caption><thead><tr><th scope="col">${escapeHtml(t("trade.year"))}</th><th scope="col">${escapeHtml(t("trade.value"))}</th><th scope="col">${escapeHtml(t("trade.quantity"))}</th></tr></thead><tbody>${observedRows}</tbody></table>`
    : `<p>${escapeHtml(t("trade.data_empty"))}</p>`;
  return `
    <article class="workspace-card full trade-chart">
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
        <p class="trade-scale-note">${escapeHtml(t("trade.scale_note"))}</p>
        <details><summary id="trade-data-summary">${escapeHtml(t("trade.data_summary"))}</summary>${observedData}</details>
      </div>
    </article>
  `;
}
