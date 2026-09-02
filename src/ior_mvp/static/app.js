const state = {
  mode: "public",
  opportunities: [],
  selectedId: null,
  analysis: null,
  manifest: null,
};

const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });
const pct = (value, digits = 0) => value == null ? "—" : `${(value * 100).toFixed(digits)}%`;
const money = (value) => value == null ? "—" : `SAR ${fmt.format(value)}m`;
const usd = (value) => value == null ? "—" : `$${fmt.format(value)}m`;
const escapeHtml = (value = "") => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

function toast(message) {
  const node = document.getElementById("toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => node.classList.remove("show"), 2400);
}

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

function stateChip(value) {
  return `<span class="state-chip state-${escapeHtml(value)}">${escapeHtml(value)}</span>`;
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".mode-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  loadPortfolio().catch(handleError);
}

async function loadPortfolio() {
  state.opportunities = await getJSON(`/api/opportunities?mode=${state.mode}`);
  if (!state.selectedId || !state.opportunities.some((item) => item.id === state.selectedId)) {
    state.selectedId = state.opportunities[0]?.id || null;
  }
  renderKPIs();
  renderOpportunityCards();
  populateSelect();
  if (state.selectedId) await loadOpportunity(state.selectedId);
}

function renderKPIs() {
  const node = document.getElementById("kpi-grid");
  const activeStates = state.opportunities.reduce((acc, item) => {
    acc[item.active_state] = (acc[item.active_state] || 0) + 1;
    return acc;
  }, {});
  const resolved = (activeStates.ADVANCE || 0) + (activeStates.REJECT || 0);
  const imports = state.opportunities.reduce((sum, item) => sum + (item.latest_imports_usd_m || 0), 0);
  node.innerHTML = [
    ["Loaded golden cases", state.opportunities.length, "Deeply resolved, hashed examples"],
    ["Decisive outcomes", resolved, state.mode === "simulated" ? "After isolated Ministry simulation" : "From public evidence only"],
    ["Latest import value", usd(imports), "Across the loaded public snapshots"],
    ["Synthetic leakage", "0", "Real decisions remain immutable"],
  ].map(([label, value, note]) => `
    <article class="kpi-card">
      <small>${escapeHtml(label)}</small>
      <strong>${escapeHtml(value)}</strong>
      <p>${escapeHtml(note)}</p>
    </article>
  `).join("");
}

function renderOpportunityCards() {
  const node = document.getElementById("opportunity-grid");
  node.innerHTML = state.opportunities.map((item) => `
    <article class="opportunity-card">
      <div class="opportunity-top">
        <div>
          <span class="opportunity-code">HS ${escapeHtml(item.hs6)} · ${escapeHtml(item.sector_profile.replaceAll("_", " "))}</span>
          <h3>${escapeHtml(item.name_en)}</h3>
        </div>
        ${stateChip(item.active_state)}
      </div>
      <p class="arabic" dir="rtl">${escapeHtml(item.name_ar)}</p>
      <div class="opportunity-stats">
        <div><small>Public state</small><b>${escapeHtml(item.real_state)}</b></div>
        <div><small>${escapeHtml(item.latest_year)} imports</small><b>${usd(item.latest_imports_usd_m)}</b></div>
        <div><small>Quantity</small><b>${fmt.format(item.latest_imports_kt)} kt</b></div>
      </div>
      <button class="card-action" data-open-id="${escapeHtml(item.id)}">Open decision workspace</button>
    </article>
  `).join("");
  node.querySelectorAll("[data-open-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedId = button.dataset.openId;
      document.getElementById("opportunity-select").value = state.selectedId;
      loadOpportunity(state.selectedId).then(() => scrollToSection("workspace")).catch(handleError);
    });
  });
}

function populateSelect() {
  const select = document.getElementById("opportunity-select");
  select.innerHTML = state.opportunities.map((item) => `
    <option value="${escapeHtml(item.id)}">HS ${escapeHtml(item.hs6)} — ${escapeHtml(item.name_en)}</option>
  `).join("");
  select.value = state.selectedId || "";
}

async function loadOpportunity(id) {
  state.selectedId = id;
  const [analysis, manifest] = await Promise.all([
    getJSON(`/api/opportunities/${encodeURIComponent(id)}?mode=${state.mode}`),
    getJSON(`/api/opportunities/${encodeURIComponent(id)}/ui-manifest?mode=${state.mode}`),
  ]);
  state.analysis = analysis;
  state.manifest = manifest;
  document.getElementById("workspace-title").textContent = `HS ${analysis.opportunity.hs6} · ${analysis.opportunity.commercial_name_en}`;
  renderManifest();
  renderMethodology();
}

function renderManifest() {
  const node = document.getElementById("workspace-manifest");
  node.innerHTML = state.manifest.components.map(renderComponent).join("");
  bindWorkspaceActions();
}

function renderComponent(component) {
  const renderers = {
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
  };
  return renderers[component.type] ? renderers[component.type](component.props) : "";
}

function renderIntegrityBanner(props) {
  const simulated = props.mode === "simulated";
  const methodology = props.authority.methodology;
  const versions = props.authority.config_versions;
  const methodologyFile = methodology.file.split("/").at(-1);
  return `
    <article class="workspace-card integrity-banner">
      <div class="card-body">
        <div>
          <strong>Evidence boundary enforced</strong>
          <p>Real state is calculated from frozen public evidence. ${simulated ? "The active surface below is a sealed simulation." : "No synthetic record is active."}</p>
          <p class="integrity-authority">Methodology ${escapeHtml(methodologyFile)} · SHA-256 ${escapeHtml(methodology.sha256_prefix)} · Project ${escapeHtml(props.authority.project_version)} · Thresholds ${escapeHtml(versions.thresholds)} · Sector profiles ${escapeHtml(versions.sector_profiles)} · Evidence policy ${escapeHtml(versions.evidence_policy)}</p>
        </div>
        <div class="integrity-states">
          ${stateChip(props.real_state)}
          ${simulated ? `<span class="integrity-arrow">→</span>${stateChip(props.active_state)}<span class="synthetic-warning">${escapeHtml(props.synthetic_label)}</span>` : ""}
        </div>
      </div>
    </article>
  `;
}

function renderDecisionHero(props) {
  return `
    <article class="workspace-card decision-hero">
      <div class="decision-state-large state-${escapeHtml(props.state)}">${escapeHtml(props.state)}</div>
      <div>
        <h3>${escapeHtml(props.headline)}</h3>
        <p>${escapeHtml(props.rationale)}</p>
      </div>
      <span class="route-pill">${escapeHtml(props.route)}</span>
    </article>
  `;
}

function renderMetricGrid(props) {
  const latest = [...props.trade].sort((a, b) => a.year - b.year).at(-1);
  const cap = props.capacity;
  const econ = props.economics;
  const hhi = props.supplier_metrics?.partner_value_hhi;
  const hhiThreshold = props.supplier_concentration?.hhi_threshold;
  const hhiNote = hhi == null
    ? "Not available in this snapshot"
    : hhiThreshold == null
      ? "Configured resilience threshold unavailable"
      : `Resilience review threshold: ${hhiThreshold.toFixed(2)}`;
  const metrics = [
    ["Latest imports", usd(latest.imports_usd_m), `${fmt.format(latest.imports_kt)} kt in ${latest.year}`],
    ["Supplier HHI", hhi == null ? "—" : hhi.toFixed(2), hhiNote],
    [cap ? "Specification gap" : "Evidence class", cap ? `${fmt.format(cap.specification_adjusted_gap_kt)} kt` : state.analysis.real_decision.confidence, cap ? "Target demand minus qualified supply" : "Public decision confidence cap"],
    [econ ? "Minimum support" : "Decision object", econ?.minimum_effective_support_m != null ? money(econ.minimum_effective_support_m) : "—", econ ? (econ.passes ? "Passes NPV and IRR hurdle" : econ.reason || "No support case") : state.analysis.opportunity.decision_object_status.replaceAll("_", " ")],
  ];
  return `<div class="metric-panel">${metrics.map(([label, value, note]) => `
    <article class="metric-box"><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong><p>${escapeHtml(note)}</p></article>
  `).join("")}</div>`;
}

function chartPath(values, x, y) {
  return values.map((value, index) => `${index === 0 ? "M" : "L"}${x(index)},${y(value)}`).join(" ");
}

function renderTradeChart(props) {
  const trade = [...props.trade].sort((a, b) => a.year - b.year);
  const width = 760, height = 250, pad = { l: 48, r: 25, t: 20, b: 38 };
  const maxValue = Math.max(...trade.map((row) => row.imports_usd_m || 0)) * 1.12;
  const maxQty = Math.max(...trade.map((row) => row.imports_kt || 0)) * 1.12;
  const x = (index) => pad.l + (trade.length === 1 ? 0 : index * ((width - pad.l - pad.r) / (trade.length - 1)));
  const yValue = (value) => height - pad.b - ((value || 0) / maxValue) * (height - pad.t - pad.b);
  const yQty = (value) => height - pad.b - ((value || 0) / maxQty) * (height - pad.t - pad.b);
  const grid = [0, .25, .5, .75, 1].map((fraction) => {
    const y = pad.t + fraction * (height - pad.t - pad.b);
    return `<line class="chart-grid" x1="${pad.l}" y1="${y}" x2="${width - pad.r}" y2="${y}"/>`;
  }).join("");
  const labels = trade.map((row, index) => `<text class="chart-label" x="${x(index)}" y="${height - 12}" text-anchor="middle">${row.year}</text>`).join("");
  const valuePoints = trade.map((row, index) => `<circle class="chart-point-value" cx="${x(index)}" cy="${yValue(row.imports_usd_m)}" r="4"><title>$${row.imports_usd_m}m</title></circle>`).join("");
  const qtyPoints = trade.map((row, index) => `<circle class="chart-point-quantity" cx="${x(index)}" cy="${yQty(row.imports_kt)}" r="4"><title>${row.imports_kt} kt</title></circle>`).join("");
  return `
    <article class="workspace-card full">
      <div class="card-header"><div><h3>Public trade signal</h3><p>Frozen gross WITS/UN Comtrade observations; not retained domestic demand</p></div><span class="exec-chip exec-DEGRADED">EVIDENCE-BOUNDED</span></div>
      <div class="card-body">
        <div class="chart-wrap">
          <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Import value and quantity trend">
            ${grid}
            <line class="chart-axis" x1="${pad.l}" y1="${height - pad.b}" x2="${width - pad.r}" y2="${height - pad.b}"/>
            <path class="chart-value" d="${chartPath(trade.map((r) => r.imports_usd_m), x, yValue)}"/>
            <path class="chart-quantity" d="${chartPath(trade.map((r) => r.imports_kt), x, yQty)}"/>
            ${valuePoints}${qtyPoints}${labels}
          </svg>
        </div>
        <div class="chart-legend"><span><i class="legend-dot legend-value"></i>Import value, USD m</span><span><i class="legend-dot legend-quantity"></i>Import quantity, kt</span></div>
      </div>
    </article>
  `;
}

function fireText(value) {
  if (value === true) return `<span class="rule-fire fire-yes">FIRES</span>`;
  if (value === false) return `<span class="rule-fire fire-no">DOES NOT FIRE</span>`;
  return `<span class="rule-fire fire-na">NOT EVALUABLE</span>`;
}

function renderRuleLedger(props) {
  return `
    <article class="workspace-card full">
      <div class="card-header"><div><h3>R0–R12 execution ledger</h3><p>Thresholds are versioned configuration, never hidden in code</p></div></div>
      <div class="card-body" style="overflow-x:auto">
        <table class="rule-table"><thead><tr><th>Rule</th><th>Execution</th><th>Result</th><th>Decision effect</th></tr></thead><tbody>
          ${props.rules.map((row) => `<tr>
            <td><b>${escapeHtml(row.rule_id)}</b><br><span>${escapeHtml(row.name)}</span></td>
            <td><span class="exec-chip exec-${escapeHtml(row.execution)}">${escapeHtml(row.execution)}</span><br>${fireText(row.fired)}</td>
            <td>${escapeHtml(row.result)}</td>
            <td>${escapeHtml(row.decision_effect)}</td>
          </tr>`).join("")}
        </tbody></table>
      </div>
    </article>
  `;
}

function renderCapabilityMatrix(props) {
  const d = props.d_star == null ? "GATED" : props.d_star.toFixed(3);
  const rows = props.dimensions.map((row) => {
    const label = row.dimension.replaceAll("_", " ");
    const known = row.known;
    const width = known ? Math.max(6, ((3 - row.state) / 3) * 100) : 100;
    return `<div class="capability-row">
      <span>${escapeHtml(label)}</span>
      <div class="capability-bar"><div class="capability-fill ${known ? "" : "capability-unknown"}" style="width:${width}%"></div></div>
      <b>${known ? row.state : "U"}</b>
    </div>`;
  }).join("");
  return `
    <article class="workspace-card">
      <div class="card-header"><div><h3>Plant-capability distance</h3><p>${escapeHtml(props.profile_label)}</p></div></div>
      <div class="card-body">
        <div class="capability-summary">
          <div><small>Known coverage K</small><strong>${pct(props.known_weight_coverage)}</strong></div>
          <div><small>Unknown weight U</small><strong>${pct(props.unknown_weight)}</strong></div>
          <div><small>D*</small><strong>${escapeHtml(d)}</strong></div>
        </div>
        ${rows}
        <div class="control-note">${escapeHtml(props.control_message)}</div>
      </div>
    </article>
  `;
}

function renderEconomicsPanel(props) {
  const e = props.economics || {};
  const c = props.competition || {};
  const v = props.evsi || {};
  const nv = e.national_value || {};
  return `
    <article class="workspace-card">
      <div class="card-header"><div><h3>Economics, public value and EVSI</h3><p>Unsupported case first; support is residual</p></div></div>
      <div class="card-body">
        <div class="economics-grid">
          <div class="economics-box"><small>Unsupported NPV</small><strong>${e.unsupported_npv_m == null ? "—" : money(e.unsupported_npv_m)}</strong></div>
          <div class="economics-box"><small>Unsupported IRR</small><strong>${e.unsupported_irr == null ? "—" : pct(e.unsupported_irr,1)}</strong></div>
          <div class="economics-box"><small>Minimum S*</small><strong>${e.minimum_effective_support_m == null ? "SAR 0m" : money(e.minimum_effective_support_m)}</strong></div>
          <div class="economics-box"><small>Incremental national value</small><strong>${nv.incremental_national_value_m_sar == null ? "—" : money(nv.incremental_national_value_m_sar)}</strong></div>
          <div class="economics-box"><small>Capacity ratio</small><strong>${c.post_entry_capacity_to_downside_demand == null ? "—" : c.post_entry_capacity_to_downside_demand.toFixed(2)}</strong></div>
          <div class="economics-box"><small>Approx. EVSI</small><strong>${v.approximate_evsi_m_sar == null ? "—" : money(v.approximate_evsi_m_sar)}</strong></div>
        </div>
        ${v.next_fact ? `<div class="control-note"><b>Highest-value next fact:</b> ${escapeHtml(v.next_fact)}</div>` : ""}
      </div>
    </article>
  `;
}

function renderEvidenceLedger(props) {
  return `
    <article class="workspace-card full">
      <div class="card-header"><div><h3>Evidence passport ledger</h3><p>Every decision field retains source, class, status and synthetic boundary</p></div></div>
      <div class="card-body" style="overflow-x:auto">
        <table class="evidence-table"><thead><tr><th>Class</th><th>Source</th><th>Evidence</th><th>Status</th><th>Boundary</th></tr></thead><tbody>
          ${props.evidence.map((row) => `<tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
            <td><span class="evidence-class">${escapeHtml(row.evidence_class)}</span></td>
            <td><span class="evidence-source">${escapeHtml(row.source)}</span></td>
            <td><span class="evidence-title">${escapeHtml(row.title)}</span></td>
            <td>${escapeHtml(row.status)}</td>
            <td>${row.synthetic_flag ? `<span class="exec-chip exec-DEGRADED">SYNTHETIC</span>` : `<span class="exec-chip exec-FULL">PUBLIC</span>`}</td>
          </tr>`).join("")}
        </tbody></table>
      </div>
    </article>
  `;
}

function renderDataUnlocks(props) {
  const synthetic = props.synthetic_inputs_used || [];
  return `
    <article class="workspace-card">
      <div class="card-header"><div><h3>What Ministry data unlocks</h3><p>The engine asks for the minimum route-changing fact</p></div></div>
      <div class="card-body">
        <ul class="unlock-list">
          ${props.missing_facts.map((item, index) => `<li><b>${index + 1}</b><span>${escapeHtml(item)}</span></li>`).join("")}
        </ul>
        ${synthetic.length ? `<div class="control-note"><b>Active synthetic blocks:</b> ${escapeHtml(synthetic.join(", "))}</div>` : ""}
      </div>
    </article>
  `;
}

function renderDecisionActions(props) {
  return `
    <article class="workspace-card">
      <div class="card-header"><div><h3>Decision outputs</h3><p>One-page dossier and machine-readable record</p></div></div>
      <div class="card-body">
        <div class="action-row">
          <button class="primary-button" data-dossier-html="${escapeHtml(props.opportunity_id)}">Open dossier</button>
          <button class="secondary-button" data-copy-json="${escapeHtml(props.opportunity_id)}">Copy decision JSON</button>
        </div>
      </div>
    </article>
  `;
}

function bindWorkspaceActions() {
  document.querySelectorAll("[data-dossier-html]").forEach((button) => {
    button.addEventListener("click", () => {
      window.open(`/api/opportunities/${encodeURIComponent(button.dataset.dossierHtml)}/dossier.html?mode=${state.mode}`, "_blank", "noopener");
    });
  });
  document.querySelectorAll("[data-copy-json]").forEach((button) => {
    button.addEventListener("click", async () => {
      const dossier = await getJSON(`/api/opportunities/${encodeURIComponent(button.dataset.copyJson)}/dossier?mode=${state.mode}`);
      await navigator.clipboard.writeText(JSON.stringify(dossier, null, 2));
      toast("Decision dossier JSON copied");
    });
  });
}

function renderMethodology() {
  if (!state.analysis) return;
  const rules = state.analysis.rules;
  const full = rules.filter((row) => row.execution === "FULL").length;
  const degraded = rules.filter((row) => row.execution === "DEGRADED").length;
  const disabled = rules.filter((row) => row.execution === "DISABLED").length;
  const fired = rules.filter((row) => row.fired === true).length;
  const node = document.getElementById("methodology-summary");
  node.innerHTML = `
    <div class="methodology-topline">
      <div><small>Full</small><strong>${full}</strong></div>
      <div><small>Degraded</small><strong>${degraded}</strong></div>
      <div><small>Disabled</small><strong>${disabled}</strong></div>
      <div><small>Signals fired</small><strong>${fired}</strong></div>
    </div>
    <div class="methodology-table-wrap">
      <table class="rule-table"><thead><tr><th>Rule</th><th>Execution</th><th>Fired</th><th>Result</th></tr></thead><tbody>
        ${rules.map((row) => `<tr><td><b>${escapeHtml(row.rule_id)}</b> · ${escapeHtml(row.name)}</td><td><span class="exec-chip exec-${escapeHtml(row.execution)}">${escapeHtml(row.execution)}</span></td><td>${fireText(row.fired)}</td><td>${escapeHtml(row.result)}</td></tr>`).join("")}
      </tbody></table>
    </div>
  `;
}

async function loadExtractionDemo() {
  const result = await getJSON("/api/extraction-demo");
  document.getElementById("extraction-score").textContent = `${result.passed}/${result.total} golden fields passed`;
  document.getElementById("extraction-grid").innerHTML = result.records.map((row) => `
    <article class="extraction-card">
      <h3>${escapeHtml(row.field)} <span class="${row.passed ? "pass-mark" : "fail-mark"}">${row.passed ? "✓" : "✕"}</span></h3>
      <div class="language-block" dir="rtl"><b>AR</b><br>${escapeHtml(row.source_spans.ar)}</div>
      <div class="language-block"><b>EN</b><br>${escapeHtml(row.source_spans.en)}</div>
      <div class="normalized-block"><b>Normalized</b><br><code>${escapeHtml(JSON.stringify(row.actual))}</code></div>
    </article>
  `).join("");
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function bindGlobalEvents() {
  document.querySelectorAll(".mode-button").forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
  document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((node) => node.classList.remove("active"));
    button.classList.add("active");
    scrollToSection(button.dataset.target);
  }));
  document.getElementById("opportunity-select").addEventListener("change", (event) => {
    state.selectedId = event.target.value;
    loadOpportunity(state.selectedId).catch(handleError);
  });
  document.getElementById("open-first-case").addEventListener("click", () => {
    const steel = state.opportunities.find((item) => item.hs6 === "721049") || state.opportunities[0];
    if (steel) {
      state.selectedId = steel.id;
      document.getElementById("opportunity-select").value = steel.id;
      loadOpportunity(steel.id).then(() => scrollToSection("workspace")).catch(handleError);
    }
  });
  document.getElementById("view-methodology").addEventListener("click", () => scrollToSection("methodology"));
}

function handleError(error) {
  console.error(error);
  toast(error.message || "Something went wrong");
}

async function init() {
  bindGlobalEvents();
  await Promise.all([loadPortfolio(), loadExtractionDemo()]);
}

init().catch(handleError);
