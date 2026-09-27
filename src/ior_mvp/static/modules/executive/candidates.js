import { escapeHtml as esc, technicalToken as code, sourceIsland, sourceCaption } from "../dom.js";
import { number } from "../formatters.js";
import { t } from "../i18n.js";
import { ministryLabel, named, fieldName, recordLabel, capabilityLegend } from "./labels.js";

const TECH_UNITS = Object.freeze({
  width_mm: "mm", thickness_mm: "mm", coating_mass_g_m2: "g/m²",
  mfr_range_g_10min: "g/10min",
});

function quantity(value) {
  return value === null || value === undefined
    ? esc(t("common.unavailable")) : code(`${number(value, 4)} ${t("ministry.unit.kt")}`);
}

function requestWindow(requirement) {
  const [start, end] = requirement.request_window_months;
  return `${code(`[${start},${end})`)} ${esc(t("ministry.months"))}`;
}

function windowResult(value) {
  if (value === null || value === undefined) return esc(t("common.unavailable"));
  const label = value === "COVERED" ? "ministry.window.covered"
    : value === "MISMATCH" ? "ministry.window.mismatch" : "ministry.status.not_established";
  return esc(t(label));
}

function recorded(value, field = "") {
  if (value === null || value === undefined) return esc(t("common.unavailable"));
  if (typeof value === "number") return code(`${number(value, 4)}${TECH_UNITS[field] ? ` ${TECH_UNITS[field]}` : ""}`);
  if (typeof value === "boolean") return esc(t(value ? "common.yes" : "common.no"));
  if (typeof value === "string") {
    const statusKey = recordLabel(value);
    if (statusKey) return esc(t(statusKey));
    return /^[A-Z0-9][A-Z0-9_-]*$|^\d{4}-\d{2}-\d{2}$|^[\[(]\d[\d.,]*,\d[\d.,]*[\])]$|^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$/.test(value)
      ? code(value) : `${sourceIsland(value)}${sourceCaption()}`;
  }
  if (Array.isArray(value) && value.length === 2 && value.every((item) => typeof item === "number"))
    return code(`${value.map((item) => number(item, 4)).join("–")}${TECH_UNITS[field] ? ` ${TECH_UNITS[field]}` : ""}`);
  if (Array.isArray(value)) return value.map((item) => recorded(item)).join("–");
  return `<dl class="ministry-recorded">${Object.entries(value).map(([name, item]) => `<div><dt>${fieldName(name)}</dt><dd>${recorded(item, name)}</dd></div>`).join("")}</dl>`;
}

function volumeContext(finding, requirement) {
  return `<dl data-volume-context><div><dt>${esc(t("ministry.target_demand"))}</dt><dd>${quantity(finding.needed)}</dd></div>
    <div><dt>${esc(t("ministry.record.field.admitted_qualified_supply_kt"))}</dt><dd>${quantity(finding.current_recorded?.admitted_qualified_supply_kt)}</dd></div>
    <div><dt>${esc(t("ministry.shortage_headroom"))}</dt><dd>${quantity(finding.quantified_gap)}</dd></div>
    <div><dt>${esc(t("ministry.record.field.window_result"))}</dt><dd>${windowResult(finding.current_recorded?.window_result)}</dd></div>
    <div><dt>${esc(t("ministry.modeled_window"))}</dt><dd>${requestWindow(requirement)}</dd></div></dl>`;
}

function scope(row, finding) {
  const action = finding.next_evidence?.action_code;
  const parts = [code(row.company_id)];
  if (action === "FACTORY_ATTRIBUTION") {
    parts.push(esc(t("ministry.scoped_company")));
  } else {
    if (row.entity_kind !== "COMPANY") parts.push(code(row.entity_id));
    if (row.entity_kind === "LINE" && row.plant_id) parts.push(code(row.plant_id));
  }
  parts.push(fieldName(finding.requirement_item_id), `${sourceIsland(finding.requirement_item_id)}${sourceCaption()}`);
  return parts.join(" · ");
}

export function requestSlots(finding, row, location = "detail") {
  const request = finding.next_evidence;
  const none = esc(t("ministry.slot.not_applicable"));
  const noRequest = esc(t("ministry.no_additional_request"));
  const field = request ? named("field", request.missing_field) : none;
  const dataset = request ? named("dataset", request.dataset_or_action) : none;
  const effect = request
    ? esc(ministryLabel("effect", request.action_code === "FACTORY_ATTRIBUTION" || request.action_code === "IN_SCOPE_PROCUREMENT_RECORD" ? request.action_code : request.need_code))
    : noRequest;
  if (request && (request.subject_scope !== row.entity_id || request.action_code !== finding.action_code)) {
    throw new Error("EXECUTIVE_REQUEST_SCOPE_INVALID");
  }
  return `<dl class="ministry-request" data-request-location="${esc(location)}" data-request-item="${esc(finding.requirement_item_id)}" data-request-rule="${esc(finding.rule_id)}">
    <div data-request-slot="field"><dt>${esc(t("ministry.slot.field"))}</dt><dd>${field}</dd></div>
    <div data-request-slot="source"><dt>${esc(t("ministry.slot.source"))}</dt><dd>${dataset}</dd></div>
    <div data-request-slot="effect"><dt>${esc(t("ministry.slot.effect"))}</dt><dd>${effect}</dd></div>
    <div data-request-slot="scope"><dt>${esc(t("ministry.slot.scope"))}</dt><dd>${scope(row, finding)}</dd></div>
  </dl>`;
}

function sourceDetails(finding) {
  const inputs = finding.input_records.map((input) => `<li data-input-origin="${esc(input.origin)}">
    ${code(input.fact_id)} · ${esc(ministryLabel("origin", input.origin))} ·
    ${code(input.subject_id)} · ${code(input.window.start)}–${code(input.window.end)}
  </li>`).join("");
  const refs = finding.source_refs.map((ref) => `<li>${sourceIsland(ref.pointer || `${ref.artifact}:${ref.evidence_id}:${ref.field}`)}${sourceCaption()}</li>`).join("");
  return `<details data-finding-provenance><summary>${esc(t("ministry.provenance"))}</summary>
    <p>${esc(t("ministry.source_boundary"))}</p><ul>${inputs}${refs}</ul></details>`;
}

function findingDetails(finding, row, requirement) {
  return `<details class="ministry-finding" data-finding="${esc(finding.rule_id)}" data-finding-item="${esc(finding.requirement_item_id)}">
    <summary><span>${code(finding.rule_id)} · ${fieldName(finding.dimension)}</span>
      <span>${esc(ministryLabel("status", finding.status))} · ${esc(ministryLabel("origin", finding.origin))}</span>
      <span>${finding.next_evidence ? named("field", finding.next_evidence.missing_field) : esc(t("ministry.no_additional_request"))}</span></summary>
    ${finding.rule_id === "P09" ? volumeContext(finding, requirement) : `<dl class="ministry-operands"><div><dt>${esc(t("ministry.current"))}</dt><dd>${recorded(finding.current_recorded, finding.dimension)}</dd></div>
      <div><dt>${esc(t("ministry.needed"))}</dt><dd>${recorded(finding.needed, finding.dimension)}</dd></div></dl>`}
    <p>${esc(t("ministry.rule"))}: ${code(finding.rule_id)} · ${code(finding.reason_code)}</p>
    ${requestSlots(finding, row)}
    <details data-finding-reason><summary>${esc(t("ministry.reason"))}</summary>
      <p>${code(finding.rule_id)} · ${code(finding.reason_code)} · ${esc(ministryLabel("origin", finding.origin))}</p>
      ${requestSlots(finding, row, "reason")}${sourceDetails(finding)}</details>
    <button data-ministry-requirement="${esc(finding.requirement_item_id)}">${esc(t("ministry.next_record"))}</button>
  </details>`;
}

export function renderFindings(row, selection, requirement) {
  if (!row) return "";
  const selected = selection.requirementId
    ? row.findings.find((finding) => finding.requirement_item_id === selection.requirementId)
    : null;
  return `<section class="ministry-findings"><h3>${esc(t("ministry.findings"))}</h3>
    ${selected ? `<aside class="ministry-request-rail" data-selected-request="${esc(selected.requirement_item_id)}"><h4>${esc(t("ministry.next_record"))}</h4>${requestSlots(selected, row, "rail")}</aside>` : ""}
    <details data-all-findings><summary>${esc(t("ministry.findings"))} · ${code(row.findings.length)}</summary>
      <div class="ministry-finding-list">${row.findings.map((finding) => findingDetails(finding, row, requirement)).join("")}</div></details>
  </section>`;
}

export function renderLineComparison(context, selection) {
  const assessment = context.executiveCase.line_assessment;
  if (!assessment.available) return `<p>${esc(t("ministry.no_line"))}</p>`;
  const rows = [...assessment.rows].sort((a, b) => a.line_id.localeCompare(b.line_id));
  const requirement = context.executiveCase.candidate_discovery.requirement;
  return `<section class="ministry-comparison" data-line-comparison><h3>${esc(t("ministry.comparison"))}</h3>
    <p>${esc(t("ministry.no_winner"))}</p><p>${esc(t("ministry.target_demand"))}: ${quantity(requirement.target_demand_kt)} · ${esc(t("ministry.modeled_window"))}: ${requestWindow(requirement)}</p>
    <p>${esc(t("ministry.coverage_explanation"))} ${esc(t("ministry.declared_scope"))}</p>${capabilityLegend(true)}<div class="card-body-scroll"><table>
      <thead><tr><th>${esc(t("ministry.line"))}</th><th>${esc(t("ministry.finding"))}</th>
      <th>${esc(t("ministry.known_coverage"))}</th><th>${code("D*")}</th><th>${esc(t("ministry.declared_effort"))}</th></tr></thead>
      <tbody>${rows.map((row) => `<tr data-line-row="${esc(row.line_id)}" ${selection.lineId === row.line_id ? 'aria-selected="true"' : ""}>
        <th><button data-ministry-line="${esc(row.line_id)}">${code(row.line_id)}</button><small>${code(row.reference_role)}</small></th>
        <td><dl>${row.comparisons.map((item) => `<div data-comparison-field="${esc(item.field_id)}"><dt>${fieldName(item.field_id)}</dt><dd>${esc(ministryLabel("status", item.status))} · ${esc(t("ministry.current"))}: ${recorded(item.current_recorded, item.field_id)} · ${esc(t("ministry.needed"))}: ${recorded(item.needed, item.field_id)}</dd></div>`).join("")}</dl>
          <dl data-comparison-quantity><div><dt>${esc(t("ministry.capacity_result"))}</dt><dd>${recorded(row.capacity.capacity_result)}</dd></div>
          <div><dt>${esc(t("ministry.record.field.admitted_qualified_supply_kt"))}</dt><dd>${quantity(row.capacity.admitted_qualified_supply_kt)}</dd></div>
          <div><dt>${esc(t("ministry.shortage_headroom"))}</dt><dd>${quantity(row.capacity.shortage_kt)}</dd></div>
          <div><dt>${esc(t("ministry.record.field.window_result"))}</dt><dd>${windowResult(row.capacity.window_result)}</dd></div></dl></td>
        <td>${recorded(row.known_weight_coverage)}</td><td>${recorded(row.d_star)}${row.d_star === null ? `<div data-dstar-withheld><p>${code("D*")} · ${esc(t("ministry.dstar_withheld"))}</p><ul>${Object.entries(row.gates).filter(([, status]) => ["known failure", "unavailable"].includes(status)).map(([gate, status]) => `<li data-blocking-gate="${esc(gate)}">${fieldName(gate)} · ${esc(status === "known failure" ? t("ministry.gate.known_failure") : t("ministry.gate.unavailable"))}<ul>${(row.gate_requirements[gate] || []).map((field) => `<li data-affected-requirement="${esc(field)}">${fieldName(field)}</li>`).join("")}</ul></li>`).join("")}</ul></div>` : ""}</td>
        <td>${row.declared_effort ? `<dl>${Object.entries(row.declared_effort).map(([field, value]) => `<div><dt>${fieldName(field)}</dt><dd>${recorded(value)}</dd></div>`).join("")}</dl>` : esc(t("common.unavailable"))}</td>
      </tr>`).join("")}</tbody></table></div></section>`;
}
