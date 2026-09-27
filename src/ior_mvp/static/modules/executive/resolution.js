import { escapeHtml as esc, technicalToken as code, sourceIsland, sourceCaption } from "../dom.js";
import { t } from "../i18n.js";
import { state } from "../state.js";
import { number } from "../formatters.js";
import { renderFindings, renderLineComparison } from "./candidates.js";
import { ministryLabel } from "./labels.js";

export function selectionKey(selection) {
  return [selection.opportunityId, selection.companyId, selection.plantId,
    selection.lineId, selection.requirementId].map((value) => value || "").join("|");
}

export function validateCandidateSelection(selection, context) {
  const { companyId, plantId, lineId, requirementId } = selection;
  if (![companyId, plantId, lineId, requirementId].some(Boolean)) return true;
  const discovery = context.executiveCase.candidate_discovery;
  if (!discovery.available || !companyId) return false;
  const rows = discovery.rows;
  const company = rows.find((row) => row.entity_kind === "COMPANY"
    && row.entity_id === companyId);
  if (!company) return false;
  const plant = plantId ? rows.find((row) => row.entity_kind === "PLANT"
    && row.entity_id === plantId && row.company_id === companyId) : null;
  if (plantId && !plant) return false;
  const line = lineId ? rows.find((row) => row.entity_kind === "LINE"
    && row.entity_id === lineId && row.company_id === companyId
    && row.plant_id === plantId) : null;
  if (lineId && !line) return false;
  const subject = line || plant || company;
  return !requirementId || subject.findings.some(
    (finding) => finding.requirement_item_id === requirementId,
  );
}

function subjectRows(discovery) {
  const rows = [...discovery.rows].sort((a, b) => a.entity_id.localeCompare(b.entity_id));
  return {
    companies: rows.filter((row) => row.entity_kind === "COMPANY"),
    plants: rows.filter((row) => row.entity_kind === "PLANT"),
    lines: rows.filter((row) => row.entity_kind === "LINE"),
  };
}

function selectedRow(rows, selection) {
  return rows.lines.find((row) => row.entity_id === selection.lineId)
    || rows.plants.find((row) => row.entity_id === selection.plantId)
    || rows.companies.find((row) => row.entity_id === selection.companyId) || null;
}

const ITEM_KEYS = Object.freeze({
  operating_factory: "ministry.item.operating_factory",
  current_process: "ministry.item.current_process",
  own_output: "ministry.item.own_output",
  input_procurement: "ministry.item.input_procurement",
  planned_change: "ministry.item.planned_change",
  qualified_volume: "ministry.item.qualified_volume",
  width_mm: "ministry.item.width_mm",
  thickness_mm: "ministry.item.thickness_mm",
  coating_mass_g_m2: "ministry.item.coating_mass_g_m2",
  standard: "ministry.item.standard",
  mfr_test_condition: "ministry.item.mfr_test_condition",
  mfr_range_g_10min: "ministry.item.mfr_range_g_10min",
});
const SPEC_UNITS = Object.freeze({ coating_mass_g_m2: "g/m²", thickness_mm: "mm", width_mm: "mm", mfr_required: "g/10min" });
function companyName(row) {
  return row[state.locale === "ar" ? "company_name_ar" : "company_name_en"];
}

function itemName(item) {
  const key = ITEM_KEYS[item];
  return key ? esc(t(key)) : code(item);
}
export function renderRequirementStrip(context) {
  const requirement = context.executiveCase.candidate_discovery.requirement;
  if (!requirement) return "";
  const specification = Object.entries(requirement.specification).map(([field, value]) => {
    const item = field === "mfr_required" ? "mfr_range_g_10min" : field;
    const unit = SPEC_UNITS[field] ? ` ${SPEC_UNITS[field]}` : "";
    const displayed = Array.isArray(value)
      ? code(`${value.map((item) => number(item, 4)).join("–")}${unit}`)
      : field === "standard" ? `${sourceIsland(value)}${sourceCaption()}` : code(`${typeof value === "number" ? number(value, 4) : value}${unit}`);
    return `<div><dt>${itemName(item)}</dt><dd>${displayed}</dd></div>`;
  }).join("");
  const [start, end] = requirement.request_window_months;
  return `<section class="ministry-requirement-strip" data-requirement-strip>
    <strong>${esc(t("ministry.target_specification"))} · ${code(context.executiveCase.opportunity.hs6)}</strong>
    <dl>${specification}<div><dt>${esc(t("ministry.target_demand"))}</dt><dd>${code(`${number(requirement.target_demand_kt, 4)} ${t("ministry.unit.kt")}`)}</dd></div>
      <div><dt>${esc(t("ministry.modeled_window"))}</dt><dd>${code(`[${start},${end})`)} ${esc(t("ministry.months"))}</dd></div>
      <div><dt>${esc(t("ministry.application"))}</dt><dd>${sourceIsland(requirement.application)}${sourceCaption()}</dd></div></dl>
    ${sourceCaption()}<small>${esc(t("ministry.source_boundary"))}</small>
  </section>`;
}
function why(plant, company) {
  if (plant?.disposition === "RELATED_ONLY") {
    const output = plant.findings.find((finding) => finding.reason_code === "P02_RELATED_STAGE_OUTPUT");
    const process = plant.findings.find((finding) => finding.reason_code === "P05_STAGE_NOT_ESTABLISHED");
    if (output?.current_recorded && process?.current_recorded) {
      const current = output.current_recorded;
      const family = current.process_family === "cold_rolled_sheet" ? esc(t("ministry.family.cold_rolled_sheet")) : code(current.process_family);
      return `${esc(t("ministry.related_recorded"))} ${family} · ${code(current.hs_revision)}/${code(current.hs6)} · ${code(current.quantity_kt)} ${code("kt")}. ${esc(t("ministry.related_limit"))}`;
    }
  }
  const facts = (plant || company).findings.filter((finding) =>
    ["operating_factory", "own_output", "current_process", "input_procurement", "planned_change"].includes(finding.requirement_item_id)
    && finding.status === "SUPPORTED",
  ).slice(0, 3);
  return facts.length ? facts.map((finding) => `${itemName(finding.requirement_item_id)} · ${esc(ministryLabel("status", finding.status))} ${code(finding.rule_id)}`).join(" · ")
    : esc(t("ministry.no_supporting_record"));
}

function nextFinding(plant, company, lines) {
  if (plant?.disposition === "RELATED_ONLY" && plant.findings.some((finding) =>
    finding.reason_code === "P05_STAGE_NOT_ESTABLISHED" && finding.next_evidence?.missing_field === "process_route")) {
    return esc(t("ministry.related_next"));
  }
  const scopes = [
    ...lines.filter((line) => line.plant_id === plant?.entity_id), ...(plant ? [plant] : []), company,
  ];
  for (const scope of scopes) {
    const finding = scope.findings.find((item) => item.next_evidence && item.status !== "SUPPORTED");
    if (finding) return `${itemName(finding.requirement_item_id)} · ${esc(ministryLabel("status", finding.status))}`;
  }
  return esc(t("ministry.no_additional_request"));
}

function companyList(rows, selection) {
  const renderCompany = (company) => {
    const plants = rows.plants.filter((plant) => plant.company_id === company.entity_id);
    const chosen = selection.companyId === company.entity_id;
    return `<article class="ministry-company" data-company="${esc(company.entity_id)}">
      <h4><button data-ministry-company="${esc(company.entity_id)}" aria-expanded="${chosen}" aria-controls="company-${esc(company.entity_id)}">${esc(companyName(company))}</button></h4>
      <p class="ministry-identity">${code(company.entity_id)} · ${esc(t("graph.boundary_synthetic"))}</p>
      <p><strong>${esc(t("ministry.why_appears"))}:</strong> ${plants.length ? plants.map((plant) => `${code(plant.entity_id)} · ${why(plant, company)}`).join("<br>") : why(null, company)}</p>
      <p><strong>${esc(t("ministry.what_next"))}:</strong> ${plants.length ? plants.map((plant) => `${code(plant.entity_id)} · ${nextFinding(plant, company, rows.lines)}`).join("<br>") : nextFinding(null, company, rows.lines)}</p>
      ${chosen ? `<div id="company-${esc(company.entity_id)}"><h5>${esc(t("ministry.plant"))}</h5>
        ${plants.length ? `<ul>${plants.map((plant) => `<li><button data-ministry-company="${esc(company.entity_id)}" data-ministry-plant="${esc(plant.entity_id)}" aria-expanded="${selection.plantId === plant.entity_id}">${esc(t("ministry.plant"))} · ${esc(companyName(plant))}</button><small>${code(plant.entity_id)} · ${esc(ministryLabel("disposition", plant.disposition))} · ${esc(t("ministry.registry_assertion"))} ${code(plant.plant_status)}</small></li>`).join("")}</ul>` : `<p>${esc(t("ministry.no_plant"))}</p>`}
      </div>` : `<p>${code(plants.length)} ${esc(t("ministry.plant"))}</p>`}
    </article>`;
  };
  const primary = rows.companies.filter((company) => rows.plants.some((plant) =>
    plant.company_id === company.entity_id && ["PASS_TO_ASSESSMENT", "RELATED_ONLY"].includes(plant.disposition)));
  const primaryIds = new Set(primary.map((row) => row.entity_id));
  const other = rows.companies.filter((row) => !primaryIds.has(row.entity_id));
  return `<div data-company-count="${rows.companies.length}">
    <div class="ministry-companies">${primary.map(renderCompany).join("")}</div>
    <details data-other-results><summary>${esc(t("ministry.other_results"))} · ${code(other.length)}</summary>
      <p>${esc(t("ministry.other_results_limit"))}</p>
      <div class="ministry-companies">${other.map(renderCompany).join("")}</div></details></div>`;
}

function lineList(rows, selection) {
  if (!selection.plantId) return "";
  const lines = rows.lines.filter((row) => row.plant_id === selection.plantId);
  return `<section class="ministry-lines"><h4>${esc(t("ministry.line"))}</h4>
    ${lines.length ? `<ul>${lines.map((line) => `<li><button data-ministry-company="${esc(line.company_id)}" data-ministry-plant="${esc(line.plant_id)}" data-ministry-line="${esc(line.entity_id)}" aria-expanded="${selection.lineId === line.entity_id}">${esc(t("ministry.line"))} · ${esc(companyName(line))}</button><small>${code(line.entity_id)}</small></li>`).join("")}</ul>` : `<p>${esc(t("ministry.no_line"))}</p>`}
  </section>`;
}

export function renderResolution(context, selection) {
  selection ||= { companyId: null, plantId: null, lineId: null, requirementId: null, selectionUnavailable: false };
  const discovery = context.executiveCase.candidate_discovery;
  if (!discovery.available) return `<section data-candidate-unavailable="${esc(discovery.reason)}"><p>${esc(t("ministry.no_register"))} · ${code(discovery.reason)}</p></section>`;
  if (selection.selectionUnavailable) return `<section data-candidate-selection-unavailable role="status"><p>${esc(t("ministry.selection_unavailable"))}</p></section>`;
  const rows = subjectRows(discovery);
  const selected = selectedRow(rows, selection);
  const graphQuery = new URLSearchParams({
    opportunity: context.executiveCase.opportunity.opportunity_id,
    mode: "simulated", locale: state.locale, graphView: "adjacency", graphOpen: "1",
  });
  for (const [key, value] of Object.entries({
    company: selection.companyId, plant: selection.plantId,
    line: selection.lineId, requirement: selection.requirementId,
  })) if (value) graphQuery.set(key, value);
  return `<section class="ministry-resolution" data-candidate-discovery>
    <h3>${esc(t("ministry.q3"))}</h3><p>${esc(t("ministry.register"))} · ${esc(t("ministry.no_winner"))}</p>
    ${selected ? `<section class="ministry-selected" data-selected-subject="${esc(selected.entity_id)}">
      <h3>${esc(t(selected.entity_kind === "LINE" ? "ministry.line" : selected.entity_kind === "PLANT" ? "ministry.plant" : "ministry.company"))}: ${esc(companyName(selected))}</h3>
      <p>${code(selected.entity_id)} · ${esc(ministryLabel("disposition", selected.disposition))} · ${esc(t("ministry.source_boundary"))}</p>
      <a href="/?${esc(graphQuery.toString())}">${esc(t("ministry.trace"))}</a>
      ${renderFindings(selected, selection, discovery.requirement)}</section>` : ""}
    ${companyList(rows, selection)}${lineList(rows, selection)}
    ${renderLineComparison(context, selection)}
  </section>`;
}
export function renderPublicProducers(context) {
  const records = context.publicAnalysis.domestic_capability?.producer_evidence || [];
  if (!records.length) return "";
  const seen = new Set(context.publicRows.keys());
  return `<section class="ministry-public-producers"><h4>${esc(t("ministry.q2"))}</h4>
    <p>${esc(t("ministry.public_producer_limit"))}</p>
    <div>${records.map((row) => {
      if (!row.evidence_ids.every((id) => seen.has(id))) throw new Error("EXECUTIVE_PUBLIC_PRODUCER_SOURCE_INVALID");
      const hasProcess = typeof row.process_route === "string" && row.process_route.trim().length > 0 && row.process_route !== "UNAVAILABLE";
      return `<article><h5>${esc(row.producer)}</h5><p>${hasProcess ? `${sourceCaption()}${sourceIsland(row.process_route)}` : esc(t("common.unavailable"))}</p>
        ${Array.isArray(row.published_coating_range_g_m2) ? `<p>${esc(t("dossier.field.published_coating_range_g_m2"))}: ${code(`${row.published_coating_range_g_m2.map((value) => number(value, 4)).join("–")} g/m²`)}</p>` : ""}
        ${typeof row.installed_capacity_tpy === "number" ? `<p>${esc(t("dossier.field.installed_capacity_tpy"))}: ${code(number(row.installed_capacity_tpy, 4))}</p>` : ""}
        <p>${row.evidence_ids.map(code).join(" · ")}</p></article>`;
    }).join("")}</div></section>`;
}
