import {
  escapeHtml,
  stateChip,
  syntheticLabels,
  technical,
} from "../dom.js";
import { t } from "../i18n.js";

export function transitionIcon() {
  return `
    <svg class="transition-icon" viewBox="0 0 24 24" role="img" aria-label="${escapeHtml(t("integrity.transition_aria"))}">
      <path d="M5 12h12m-4-4 4 4-4 4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
}

export function renderIntegrityBanner(props) {
  const simulated = props.mode === "simulated";
  const methodology = props.authority.methodology;
  const versions = props.authority.config_versions;
  const methodologyFile = methodology.file.split("/").at(-1);
  return `
    <article class="workspace-card integrity-banner">
      <div class="card-body">
        <div>
          <strong>${escapeHtml(t("integrity.title"))}</strong>
          <p>${escapeHtml(t(
            simulated ? "integrity.simulated_body" : "integrity.public_body",
          ))}</p>
          <p class="integrity-authority">
            ${escapeHtml(t("integrity.methodology"))} ${technical(methodologyFile)}
            · ${escapeHtml(t("technical.sha256"))} ${technical(methodology.sha256_prefix)}
            · ${escapeHtml(t("integrity.project"))} ${technical(props.authority.project_version)}
            · ${escapeHtml(t("integrity.thresholds"))} ${technical(versions.thresholds)}
            · ${escapeHtml(t("integrity.sector_profiles"))} ${technical(versions.sector_profiles)}
            · ${escapeHtml(t("integrity.evidence_policy"))} ${technical(versions.evidence_policy)}
            · ${escapeHtml(t("integrity.ui_strings"))} ${technical(versions.ui_strings)}
          </p>
        </div>
        <div class="integrity-states">
          ${stateChip(props.real_state)}
          ${simulated
            ? `${transitionIcon()}${stateChip(props.active_state)}${syntheticLabels(props.synthetic_labels, "synthetic-warning synthetic-labels")}`
            : ""}
        </div>
      </div>
    </article>
  `;
}
