import {
  escapeHtml,
  sourceCaption,
  sourceIsland,
  technical,
} from "../dom.js";
import { number, percent } from "../formatters.js";
import { t } from "../i18n.js";

export function capabilityFill(row) {
  const raw = row.known
    ? Math.max(6, ((3 - row.state) / 3) * 100)
    : 100;
  return Math.max(0, Math.min(100, raw));
}

export function renderCapabilityMatrix(props) {
  const distance = props.d_star == null
    ? t("capability.gated")
    : number(props.d_star, 3);
  const rows = props.dimensions.map((row) => {
    const label = row.dimension.replaceAll("_", " ");
    const fill = capabilityFill(row);
    return `
      <div class="capability-row">
        ${sourceIsland(label)}
        <div class="capability-bar">
          <div class="capability-fill ${row.known ? "" : "capability-unknown"}" style="--capability-fill:${fill}%"></div>
        </div>
        <b>${technical(row.known ? row.state : "U")}</b>
      </div>
    `;
  }).join("");
  return `
    <article class="workspace-card">
      <div class="card-header">
        <div>
          <h3>${escapeHtml(t("capability.title"))}</h3>
          ${sourceIsland(props.profile_label, "p")}
        </div>
      </div>
      <div class="card-body">
        ${sourceCaption()}
        <div class="capability-summary">
          <div><small>${escapeHtml(t("capability.known"))}</small><strong>${technical(percent(props.known_weight_coverage))}</strong></div>
          <div><small>${escapeHtml(t("capability.unknown"))}</small><strong>${technical(percent(props.unknown_weight))}</strong></div>
          <div><small>${escapeHtml(t("capability.distance"))}</small><strong>${technical(distance)}</strong></div>
        </div>
        ${rows}
        <div class="control-note">${sourceIsland(props.control_message)}</div>
      </div>
    </article>
  `;
}
