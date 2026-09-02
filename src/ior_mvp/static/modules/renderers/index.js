import {
  renderDecisionHero,
  renderMetricGrid,
} from "./decision.js";
import { renderTradeChart } from "./trade.js";
import { renderRuleLedger } from "./rules.js";
import { renderCapabilityMatrix } from "./capability.js";
import { renderEconomicsPanel } from "./economics.js";
import {
  renderDataUnlocks,
  renderDecisionActions,
  renderEvidenceLedger,
} from "./evidence.js";
import { renderIntegrityBanner } from "./integrity.js";

export const RENDERERS = Object.freeze({
  integrity_banner: renderIntegrityBanner,
  decision_hero: renderDecisionHero,
  metric_grid: renderMetricGrid,
  trade_chart: renderTradeChart,
  rule_ledger: renderRuleLedger,
  capability_matrix: renderCapabilityMatrix,
  economics_panel: renderEconomicsPanel,
  evidence_ledger: renderEvidenceLedger,
  data_unlocks: renderDataUnlocks,
  decision_actions: renderDecisionActions,
});

export function renderComponent(component) {
  const renderer = RENDERERS[component.type];
  return renderer ? renderer(component.props) : "";
}
