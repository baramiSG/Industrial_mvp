"""Closed candidate_lines reference contract for scenario 2.2."""

from __future__ import annotations

from typing import Any, Mapping

from .candidate_record_contract import (
    TECHNICAL_UNITS, _exact_keys, _fail, _technical_value,
)
from .capability import effective_qualified_capacity

LINE_KEYS = frozenset(
    {
        "line_id",
        "reference_role",
        "technical_fact_refs",
        "capacity_ref",
        "qualification_ref",
        "window_ref",
        "effort_ref",
        "capacity_ceiling_ref",
        "availability_basis",
        "allocation_ref",
    }
)
BLOCK_KEYS = frozenset(
    {
        "reference_basis",
        "requirements_additions",
        "requirement_items",
        "lines",
    }
)
BASIS_KEYS = frozenset({"kind", "line_id"})
ITEM_KEYS = frozenset(
    {
        "item_id",
        "dimension",
        "field_id",
        "required_value_ref",
        "record_selectors",
        "basis",
    }
)
P03_ITEM_KEYS = ITEM_KEYS | frozenset(
    {"rule_id", "hs_revision", "admitted_hs6"}
)
REFERENCE_LINE_ID = "LINE-7315366f6a9166d8"
LEGACY_LINE_POINTERS = frozenset(
    {
        "/synthetic_inputs/plant_line",
        "/synthetic_inputs/capability_states",
        "/synthetic_inputs/equivalence",
    }
)
REQUIRED_PATHS = {
    "width_mm": "/synthetic_inputs/target_specification/width_mm",
    "thickness_mm": "/synthetic_inputs/target_specification/thickness_mm",
    "coating_mass_g_m2": "/synthetic_inputs/target_specification/coating_mass_g_m2",
    "standard": "/synthetic_inputs/target_specification/standard",
    "substrate": "/synthetic_inputs/candidate_lines/requirements_additions/substrate",
    "process_route": "/synthetic_inputs/candidate_lines/requirements_additions/process_route",
    "surface_treatment": "/synthetic_inputs/candidate_lines/requirements_additions/surface_treatment",
    "mfr_range_g_10min": "/synthetic_inputs/candidate_lines/requirements_additions/mfr_required",
    "polymer_family": "/synthetic_inputs/candidate_lines/requirements_additions/polymer_family",
    "manufacturing_scope": "/synthetic_inputs/candidate_lines/requirements_additions/manufacturing_scope",
    "grade_family": "/synthetic_inputs/candidate_lines/requirements_additions/grade_family",
    "mfr_test_condition": "/synthetic_inputs/candidate_lines/requirements_additions/mfr_test_condition",
    "additives_required": "/synthetic_inputs/candidate_lines/requirements_additions/additives_required",
    "tooling_required": "/synthetic_inputs/candidate_lines/requirements_additions/tooling_required",
}
STEEL_FIELDS = frozenset({
    "substrate", "process_route", "thickness_mm", "width_mm",
    "coating_mass_g_m2", "surface_treatment", "standard", "application",
})
PP_FIELDS = frozenset({
    "polymer_family", "manufacturing_scope", "grade_family",
    "mfr_range_g_10min", "mfr_test_condition", "additives_required",
    "tooling_required", "application",
})
REF_KIND = {
    "capacity_ref": "CAPACITY",
    "qualification_ref": "QUALIFICATION",
    "window_ref": "WINDOW",
    "effort_ref": "EFFORT",
    "capacity_ceiling_ref": "CEILING",
    "allocation_ref": "ALLOCATION",
}
SELECTOR_PAIRS = frozenset(
    {
        ("REGISTRY_ACTIVITY", "operating_status_asserted_by_registry"),
        ("REGISTRY_ACTIVITY", "product_family"),
        ("REGISTRY_ACTIVITY", "process_route"),
        ("PRODUCTION_ACTUAL", "hs6"),
        ("PRODUCTION_ACTUAL", "quantity_kt"),
        ("PRODUCTION_ACTUAL", "process_family"),
        ("FACTORY_CUSTOMS", "hs6"),
        ("FACTORY_CUSTOMS", "flow"),
        ("FACTORY_CUSTOMS", "reexport"),
        ("EQUIPMENT_TECHNICAL", "function"),
        ("EQUIPMENT_TECHNICAL", "workpiece_material"),
        ("APPLICATION", "stage"),
        ("APPLICATION", "reason_code"),
        ("TECHNICAL_FIELD", "value"),
        ("QUALIFICATION", "customer_status"),
        ("CERTIFICATE", "scope"),
        ("CAPACITY", "qualification_share"),
        ("ALLOCATION", "qualified_available_kt"),
        ("WINDOW", "available_window_months"),
    }
)
P03_KEYS = frozenset(
    {"item_id", "rule_id", "record_selectors", "hs_revision", "admitted_hs6", "basis"}
)
DISCOVERY_RULES = {
    "operating_factory": ("P01", [["REGISTRY_ACTIVITY", "operating_status_asserted_by_registry"]]),
    "current_process": ("P05", [["REGISTRY_ACTIVITY", "process_route"]]),
    "input_procurement": ("P03", [["FACTORY_CUSTOMS", "hs6"]]),
    "own_output": ("P02", [["PRODUCTION_ACTUAL", "quantity_kt"]]),
    "equipment_acquisition": ("P04", [["FACTORY_CUSTOMS", "hs6"], ["EQUIPMENT_TECHNICAL", "function"]]),
    "relevant_certificate": ("P07", [["CERTIFICATE", "scope"]]),
    "planned_change": ("P08", [["APPLICATION", "stage"]]),
}


def _selectors(value: Any, label: str) -> None:
    if not isinstance(value, list):
        _fail(f"{label} record_selectors must be a list")
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2 or tuple(pair) not in SELECTOR_PAIRS:
            _fail(f"{label} selector is not admitted")


def _ref_ok(
    value: Any,
    fact_ids: set[str],
    *,
    legacy: bool,
    reference_line: bool,
) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value in fact_ids:
        return True
    if not isinstance(value, str):
        return False
    if value in LEGACY_LINE_POINTERS:
        return legacy and reference_line
    return False


def _required_pointer_value(scenario: Mapping[str, Any], pointer: str) -> Any:
    current: Any = scenario
    for part in pointer.removeprefix("/").split("/"):
        if not isinstance(current, Mapping) or part not in current:
            _fail(f"required_value_ref {pointer} does not resolve")
        current = current[part]
    if current is None:
        _fail(f"required_value_ref {pointer} does not resolve")
    return current


def window_coverage(available: Any, requested: Any) -> str:
    """Classify half-open month-window coverage without treating missingness as failure."""
    if requested is None:
        return "NOT_REQUESTED"
    if available is None:
        return "NOT_ESTABLISHED"
    if not (
        isinstance(available, list) and isinstance(requested, list)
        and len(available) == len(requested) == 2
    ):
        return "NOT_ESTABLISHED"
    return "COVERED" if available[0] <= requested[0] and available[1] >= requested[1] else "MISMATCH"


def has_current_technical_conflict(
    register: Mapping[str, Any], line_id: str, field: str, selected_ref: Any,
) -> bool:
    """A same-scope competing current declaration cannot be ignored by ref choice."""
    selected = next((fact for fact in register["facts"] if fact["fact_id"] == selected_ref), None)
    if selected is None or selected["kind"] != "TECHNICAL_FIELD":
        return False
    window = selected["window"]
    value = selected["values"]["value"]
    return any(
        fact["fact_id"] != selected_ref
        and fact["kind"] == "TECHNICAL_FIELD"
        and fact["subject_type"] == "LINE" and fact["subject_id"] == line_id
        and fact["values"]["field_id"] == field
        and fact["values"]["requirement_id"] == field
        and fact["window"]["start"] < window["end"]
        and window["start"] < fact["window"]["end"]
        and fact["values"]["value"] != value
        for fact in register["facts"]
    )


def validate_candidate_lines(
    block: dict[str, Any],
    register: Mapping[str, Any],
    *,
    scenario: Mapping[str, Any],
    legacy_pointers: bool,
) -> dict[str, Any]:
    """Validate line references against one register."""
    if not isinstance(block, dict):
        _fail("candidate_lines must be an object")
    _exact_keys(block, BLOCK_KEYS, "candidate_lines")
    basis = block["reference_basis"]
    _exact_keys(basis, BASIS_KEYS, "reference_basis")
    if basis["kind"] not in {"LINE", "AGGREGATE"}:
        _fail("reference_basis.kind is unknown")
    facts = {fact["fact_id"]: fact for fact in register["facts"]}
    fact_ids = set(facts)
    line_ids = {line["line_id"] for line in register["lines"]}
    if basis["kind"] == "LINE" and basis["line_id"] not in line_ids:
        _fail("reference_basis.line_id is not in the register")
    if basis["kind"] == "AGGREGATE" and basis["line_id"] is not None:
        _fail("aggregate reference_basis.line_id must be null")
    expected_fields = STEEL_FIELDS if basis["kind"] == "LINE" else PP_FIELDS
    additions = block["requirements_additions"]
    if not isinstance(additions, dict) or "discovery_items" not in additions:
        _fail("requirements_additions.discovery_items is required")
    for requirement in (
        additions.get("customer_qualification_required"),
        scenario["synthetic_inputs"].get("target_specification", {}).get(
            "customer_qualification_required"
        ),
    ):
        if requirement is not None and not isinstance(requirement, bool):
            _fail("customer_qualification_required must be boolean")
    seen_items: set[str] = set()
    for item in additions["discovery_items"]:
        if not isinstance(item, dict) or item.get("item_id") in seen_items:
            _fail("discovery item identity is duplicated or missing")
        seen_items.add(item["item_id"])
        item_id = item["item_id"]
        if item_id == "target_family":
            expected = {"item_id": "target_family"}
            if basis["kind"] == "LINE":
                expected["related_hs4"] = ["7209"]
            if item != expected:
                _fail("discovery item target_family does not match the target")
            continue
        if item_id not in DISCOVERY_RULES:
            _fail(f"discovery item {item_id} is unknown")
        expected_rule, expected_selectors = DISCOVERY_RULES[item_id]
        extra = {"current_process": {"process_route"}, "relevant_certificate": {"scope"}}
        allowed = P03_KEYS if item_id in {"input_procurement", "equipment_acquisition"} else frozenset(
            {"item_id", "rule_id", "record_selectors"} | extra.get(item_id, set())
        )
        _exact_keys(item, allowed, f"discovery item {item_id}")
        if item["rule_id"] != expected_rule or item["record_selectors"] != expected_selectors:
            _fail(f"discovery item {item_id} rule or selectors do not match")
        if item_id == "current_process":
            route = "HOT_DIP_GALVANISING" if basis["kind"] == "LINE" else "RESIN_PRODUCTION"
            if item["process_route"] != route:
                _fail("discovery item current_process route does not match")
        if item_id == "relevant_certificate" and item["scope"] is not None:
            _fail("discovery item certificate scope is not admitted")
        if item_id in {"input_procurement", "equipment_acquisition"}:
            sector_codes = (
                {"input_procurement": ["790111", "790112"], "equipment_acquisition": ["847981"]}
                if basis["kind"] == "LINE" else
                {"input_procurement": ["290122"], "equipment_acquisition": ["847720"]}
            )
            if item["hs_revision"] != "H6" or item["admitted_hs6"] != sector_codes[item_id]:
                _fail(f"discovery item {item_id} HS set does not match")
            if not isinstance(item["basis"], str) or not item["basis"].strip():
                _fail(f"discovery item {item_id} basis is missing")
    if seen_items != {"target_family", *DISCOVERY_RULES}:
        _fail("discovery items must cover the finite target mapping")
    item_fields: set[str] = set()
    for item in block["requirement_items"]:
        if "admitted_hs6" in item or "hs_revision" in item:
            _fail(f"{item.get('item_id')} P03 parameters belong on discovery_items")
        _exact_keys(item, ITEM_KEYS, f"requirement item {item.get('item_id')}")
        if item["item_id"] in seen_items:
            _fail(f"duplicate item_id {item['item_id']}")
        seen_items.add(item["item_id"])
        _selectors(item["record_selectors"], item["item_id"])
        field = item["field_id"]
        if field not in expected_fields or item["item_id"] != field or field in item_fields:
            _fail(f"requirement item {field} is not a unique admitted field")
        item_fields.add(field)
        if item["record_selectors"] != [["TECHNICAL_FIELD", "value"]]:
            _fail(f"requirement item {field} has an inadmissible selector")
        expected_pointer = REQUIRED_PATHS.get(field)
        if field == "application":
            expected_pointer = (
                "/synthetic_inputs/target_specification/application"
                if basis["kind"] == "LINE" else
                "/synthetic_inputs/candidate_lines/requirements_additions/application"
            )
        pointer = item["required_value_ref"]
        if not isinstance(pointer, str) or not pointer.startswith("/synthetic_inputs/"):
            _fail(f"required_value_ref {pointer} is not an admitted local pointer")
        required = _required_pointer_value(scenario, pointer)
        if pointer != expected_pointer:
            _fail(f"required_value_ref {pointer} is not admitted for {field}")
        _technical_value(field, required, f"required {field}")
    if item_fields != expected_fields:
        _fail("requirement_items must cover exactly the target technical fields")
    seen_lines: set[str] = set()
    reference_rows = [
        line for line in block["lines"] if line.get("reference_role") == "REFERENCE_LINE"
    ]
    if basis["kind"] == "LINE" and (
        len(reference_rows) != 1 or reference_rows[0]["line_id"] != basis["line_id"]
    ):
        _fail("reference role does not match reference_basis")
    if basis["kind"] == "AGGREGATE" and reference_rows:
        _fail("aggregate basis cannot name a reference line")
    for line in block["lines"]:
        _exact_keys(line, LINE_KEYS, "candidate line")
        if line["line_id"] in seen_lines:
            _fail(f"duplicate line_id {line['line_id']}")
        seen_lines.add(line["line_id"])
        if line["line_id"] not in line_ids:
            _fail(f"{line['line_id']} is not a register line")
        reference_line = (
            line["reference_role"] == "REFERENCE_LINE"
            and line["line_id"] == REFERENCE_LINE_ID
            and basis["line_id"] == REFERENCE_LINE_ID
        )
        if line["reference_role"] not in {"REFERENCE_LINE", "ALTERNATIVE"}:
            _fail(f"{line['line_id']} reference_role is unknown")
        if line["availability_basis"] not in {"FORMULA", "DECLARED_ALLOCATION"}:
            _fail(f"{line['line_id']} availability_basis is unknown")
        if line["availability_basis"] == "FORMULA" and line["allocation_ref"] is not None:
            _fail(f"{line['line_id']} formula basis cannot name an allocation")
        if (
            line["availability_basis"] == "DECLARED_ALLOCATION"
            and not _ref_ok(
                line["allocation_ref"], fact_ids, legacy=False, reference_line=False
            )
        ):
            _fail(f"{line['line_id']} allocation_ref does not resolve")
        for key, kind in REF_KIND.items():
            ref = line[key]
            if isinstance(ref, str) and ref in LEGACY_LINE_POINTERS and not reference_line:
                _fail(f"{line['line_id']} legacy pointer is only admitted on the reference line")
            if not _ref_ok(
                ref, fact_ids, legacy=legacy_pointers, reference_line=reference_line
            ):
                _fail(f"{line['line_id']} {key} does not resolve")
            if isinstance(ref, str) and ref in facts:
                fact = facts[ref]
                if fact["kind"] != kind or fact["subject_id"] != line["line_id"]:
                    _fail(f"{line['line_id']} {key} subject or kind does not match")
                if key == "qualification_ref" and fact["values"]["requirement_id"] != "customer_qualification":
                    _fail(f"{line['line_id']} qualification requirement does not match")
        refs = line["technical_fact_refs"]
        if not isinstance(refs, dict):
            _fail(f"{line['line_id']} technical_fact_refs must be an object")
        if set(refs) - expected_fields:
            _fail(f"{line['line_id']} technical_fact_refs contains an unknown field")
        for field, ref in refs.items():
            if isinstance(ref, str) and ref in LEGACY_LINE_POINTERS and not reference_line:
                _fail(f"{line['line_id']} legacy pointer is only admitted on the reference line")
            if not _ref_ok(
                ref, fact_ids, legacy=legacy_pointers, reference_line=reference_line
            ):
                _fail(f"{line['line_id']} technical ref {field} does not resolve")
            if isinstance(ref, str) and ref in facts:
                fact = facts[ref]
                if (
                    fact["kind"] != "TECHNICAL_FIELD"
                    or fact["subject_id"] != line["line_id"]
                    or fact["values"].get("field_id") != field
                ):
                    _fail(f"{line['line_id']} technical ref {field} does not match the line")
                values = fact["values"]
                if values["unit"] != TECHNICAL_UNITS[field]:
                    _fail(f"{line['line_id']} technical ref {field} has wrong unit")
                if values["requirement_id"] != field:
                    _fail(f"{line['line_id']} technical ref {field} has wrong requirement")
                _technical_value(field, values["value"], f"{line['line_id']} {field}")
        allocation_ref = line["allocation_ref"]
        if isinstance(allocation_ref, str) and allocation_ref in facts:
            allocation = facts[allocation_ref]["values"]
            if allocation["requirement_id"] != "qualified_quantity":
                _fail(f"{line['line_id']} allocation requirement does not match")
            capacity_ref = line["capacity_ref"]
            if isinstance(capacity_ref, str) and capacity_ref in facts:
                capacity = facts[capacity_ref]["values"]
                factor_keys = (
                    "nameplate_kt", "availability", "yield",
                    "qualification_share", "market_allocation_share",
                )
                if all(capacity[key] is not None for key in factor_keys):
                    formula = effective_qualified_capacity(
                        capacity["nameplate_kt"], capacity["availability"],
                        capacity["yield"], capacity["qualification_share"],
                        capacity["market_allocation_share"],
                    )
                    if allocation["qualified_available_kt"] > formula + 1e-9:
                        _fail(f"{line['line_id']} allocation exceeds formula")
    ceilings: dict[str, tuple[str, float]] = {}
    total_nameplate: dict[str, float] = {}
    for line in block["lines"]:
        ceiling_ref = line["capacity_ceiling_ref"]
        if not isinstance(ceiling_ref, str) or ceiling_ref not in facts:
            continue
        ceiling = facts[ceiling_ref]["values"]
        group = ceiling["group_id"]
        definition = (ceiling["ceiling_kind"], ceiling["value_kt"])
        if not isinstance(group, str) or not group:
            _fail("capacity ceiling group_id is required")
        if group in ceilings and ceilings[group] != definition:
            _fail(f"capacity ceiling group {group} conflicts")
        ceilings[group] = definition
        capacity_ref = line["capacity_ref"]
        if isinstance(capacity_ref, str) and capacity_ref in facts:
            nameplate = facts[capacity_ref]["values"]["nameplate_kt"]
            if nameplate is not None:
                total_nameplate[group] = total_nameplate.get(group, 0.0) + nameplate
    for group, nameplate in total_nameplate.items():
        if nameplate > ceilings[group][1] + 1e-9:
            _fail(f"capacity ceiling group {group} is exceeded")
    return block
