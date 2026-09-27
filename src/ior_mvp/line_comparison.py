"""Finite line comparison over declared records and guarded capability."""

from __future__ import annotations

from typing import Any, Mapping

from .capability import effective_qualified_capacity, evaluate_capability
from .line_contract import has_current_technical_conflict, window_coverage

FIELD_GATE = {
    "substrate": ("substrate_range", "feedstock_chemistry"),
    "thickness_mm": ("width_thickness_envelope", "equipment_envelope"),
    "width_mm": ("width_thickness_envelope", "equipment_envelope"),
    "process_route": ("coating_route_and_mass", "core_process_route"),
    "coating_mass_g_m2": ("coating_route_and_mass", "finishing_spec_control"),
    "surface_treatment": ("surface_treatment", "finishing_spec_control"),
    "standard": ("mandatory_or_customer_standard", "certification_customer_qualification"),
    "polymer_family": ("polymer_additive_compatibility", "feedstock_chemistry"),
    "additives_required": ("polymer_additive_compatibility", "feedstock_chemistry"),
    "manufacturing_scope": ("conversion_route", "core_process_route"),
    "grade_family": ("conversion_route", "core_process_route"),
    "tooling_required": ("tooling", "equipment_envelope"),
    "mfr_range_g_10min": ("performance_requirement", "finishing_spec_control"),
    "mfr_test_condition": ("performance_requirement", "finishing_spec_control"),
}


def required_quantity_kt(scenario: Mapping[str, Any]) -> Any:
    """Use the governed detailed request when supplied, else its target demand."""
    inputs = scenario["synthetic_inputs"]
    additions = inputs["candidate_lines"]["requirements_additions"]
    return additions.get("detailed_quantity_kt", inputs.get("demand", {}).get("target_spec_demand_kt"))


def _resolve(
    scenario: Mapping[str, Any],
    register: Mapping[str, Any],
    ref: Any,
) -> Any:
    if ref is None:
        return None
    if isinstance(ref, str) and ref.startswith("/synthetic_inputs/"):
        current: Any = scenario["synthetic_inputs"]
        for part in ref.removeprefix("/synthetic_inputs/").split("/"):
            if not isinstance(current, Mapping) or part not in current:
                return None
            current = current[part]
        return current
    for fact in register["facts"]:
        if fact["fact_id"] == ref:
            return fact
    return None


def _contains(recorded: Any, required: Any) -> bool | None:
    if recorded is None or required is None:
        return None
    if (
        isinstance(recorded, list)
        and isinstance(required, list)
        and len(recorded) == 2
        and len(required) == 2
        and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in recorded + required)
    ):
        return recorded[0] <= required[0] and recorded[1] >= required[1]
    if (
        isinstance(recorded, list)
        and len(recorded) == 2
        and isinstance(required, (int, float))
        and not isinstance(required, bool)
        and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in recorded)
    ):
        return recorded[0] <= required <= recorded[1]
    if isinstance(recorded, (int, float)) and isinstance(required, (int, float)):
        return recorded == required
    return recorded == required


def _value_of(resolved: Any, field_id: str) -> Any:
    if resolved is None:
        return None
    if isinstance(resolved, Mapping) and "values" in resolved:
        values = resolved["values"]
        if field_id in values:
            return values[field_id]
        if values.get("field_id") == field_id:
            return values.get("value")
        return values
    if isinstance(resolved, Mapping) and field_id in resolved:
        return resolved[field_id]
    return resolved


def _field_gate(field_id: str, sector_profile: str) -> tuple[str, str] | None:
    if field_id in {"customer_qualification", "application"}:
        return (
            "application_qualification"
            if sector_profile == "technical_plastics"
            else "mandatory_or_customer_standard",
            "certification_customer_qualification",
        )
    return FIELD_GATE.get(field_id)


def _gate_declaration(statuses: list[str]) -> str:
    if any(status == "LIMITATION_IDENTIFIED" for status in statuses):
        return "known failure"
    if any(status in {"NOT_ESTABLISHED", "CONFLICTED"} for status in statuses):
        return "unavailable"
    if statuses and all(status == "NOT_REQUIRED" for status in statuses):
        return "not applicable"
    if statuses and all(status in {"SUPPORTED", "NOT_REQUIRED"} for status in statuses):
        return "resolved"
    return "unavailable"


def compare_lines(
    scenario: Mapping[str, Any],
    register: Mapping[str, Any],
    *,
    sector_profile: str,
    decision_gates: dict[str, Any] | None,
) -> dict[str, Any]:
    """Compare enriched lines without reading ground truth or selecting a winner."""
    block = scenario["synthetic_inputs"]["candidate_lines"]
    additions = block["requirements_additions"]
    demand = required_quantity_kt(scenario)
    rows: list[dict[str, Any]] = []
    for line in block["lines"]:
        states = _resolve(scenario, register, line["effort_ref"])
        declared = _value_of(states, "effort")
        if isinstance(declared, Mapping) and "values" in declared:
            declared = declared["values"]
        declared = dict(declared) if isinstance(declared, Mapping) else {}
        gate_results: dict[str, list[str]] = {}
        gate_requirements: dict[str, list[str]] = {}
        comparisons: list[dict[str, Any]] = []
        request_window = additions.get("request_window_months")
        for item in block["requirement_items"]:
            field_id = str(item["field_id"])
            mapped = _field_gate(field_id, sector_profile)
            if mapped is None:
                continue
            ref = line["technical_fact_refs"].get(field_id)
            recorded = _value_of(_resolve(scenario, register, ref), field_id)
            required = _resolve(scenario, register, item["required_value_ref"])
            if field_id == "tooling_required" and required is False:
                resin_scope = next(
                    (row["status"] for row in comparisons if row["field_id"] == "manufacturing_scope"),
                    "NOT_ESTABLISHED",
                )
                status = "NOT_REQUIRED" if resin_scope == "SUPPORTED" else "NOT_ESTABLISHED"
            elif has_current_technical_conflict(register, line["line_id"], field_id, ref):
                status = "CONFLICTED"
            elif recorded == "CONFLICTED":
                status = "CONFLICTED"
            else:
                contained = _contains(recorded, required)
                if contained is None:
                    status = "NOT_ESTABLISHED"
                elif contained:
                    status = "SUPPORTED"
                else:
                    status = "LIMITATION_IDENTIFIED"
            gate, dimension = mapped
            gate_results.setdefault(gate, []).append(status)
            gate_requirements.setdefault(gate, []).append(field_id)
            if status in {"NOT_ESTABLISHED", "CONFLICTED"}:
                declared[dimension] = "U"
            comparisons.append(
                {
                    "field_id": field_id,
                    "current_recorded": recorded,
                    "needed": required,
                    "status": status,
                    "origin": "REVIEWED_INFERENCE",
                    "rule_id": "P06",
                }
            )
        qualification = _qualification_status(
            scenario, register, line, request_window
        )
        if qualification is not None:
            gate, dimension = _field_gate("customer_qualification", sector_profile)
            gate_results.setdefault(gate, []).append(qualification["status"])
            gate_requirements.setdefault(gate, []).append("customer_qualification")
            if qualification["status"] in {"NOT_ESTABLISHED", "CONFLICTED"}:
                declared[dimension] = "U"
            comparisons.append(qualification)
        gates = {
            gate: _gate_declaration(statuses)
            for gate, statuses in gate_results.items()
        }
        gate_requirements = {
            gate: [
                field for field, status in zip(fields, gate_results[gate], strict=True)
                if status in ({"LIMITATION_IDENTIFIED"} if gates[gate] == "known failure"
                              else {"NOT_ESTABLISHED", "CONFLICTED"})
            ]
            for gate, fields in gate_requirements.items()
        }
        capacity_fact = _resolve(scenario, register, line["capacity_ref"])
        capacity_values = _value_of(capacity_fact, "capacity")
        if isinstance(capacity_values, Mapping) and "values" in capacity_values:
            capacity_values = capacity_values["values"]
        factors_known = isinstance(capacity_values, Mapping) and all(
            isinstance(capacity_values.get(key), (int, float))
            and not isinstance(capacity_values.get(key), bool)
            for key in (
                "nameplate_kt", "availability", "yield",
                "qualification_share", "market_allocation_share",
            )
        )
        if not factors_known:
            declared["capacity_time_window"] = "U"
        capacity = _capacity(
            scenario, register, line, demand, request_window, comparisons, declared
        )
        capability = None
        if declared:
            capability = evaluate_capability(
                sector_profile, dict(declared), gates, decision_gates
            )
        rows.append(
            {
                "line_id": line["line_id"],
                "reference_role": line["reference_role"],
                "comparisons": comparisons,
                "gates": gates,
                "gate_requirements": gate_requirements,
                "capability": capability,
                "capacity": capacity,
            }
        )
    return {
        "available": True,
        "reason": None,
        "rows": rows,
        "winner": None,
    }


def _qualification_status(
    scenario: Mapping[str, Any],
    register: Mapping[str, Any],
    line: Mapping[str, Any],
    request_window: Any,
) -> dict[str, Any]:
    fact = _resolve(scenario, register, line["qualification_ref"])
    values = fact["values"] if isinstance(fact, Mapping) and "values" in fact else {}
    recorded = values.get("customer_status") if isinstance(values, Mapping) else None
    additions = scenario["synthetic_inputs"]["candidate_lines"]["requirements_additions"]
    required = additions.get("customer_qualification_required")
    if required is None:
        required = scenario["synthetic_inputs"].get("target_specification", {}).get(
            "customer_qualification_required"
        )
    window = values.get("valid_window_months") if isinstance(values, Mapping) else None
    required_application = additions.get("application") or scenario["synthetic_inputs"].get(
        "target_specification", {}
    ).get("application")
    application_matches = (
        isinstance(required_application, str)
        and bool(required_application.strip())
        and values.get("requirement_id") == "customer_qualification"
        and values.get("application") == required_application
    )
    if required is False:
        status = "NOT_REQUIRED"
    elif required is True and application_matches and recorded == "NOT_QUALIFIED":
        status = "LIMITATION_IDENTIFIED"
    elif required is True and application_matches and recorded == "QUALIFIED" and (
        window_coverage(window, request_window) == "COVERED"
    ):
        status = "SUPPORTED"
    else:
        status = "NOT_ESTABLISHED"
    return {
        "field_id": "customer_qualification",
        "current_recorded": recorded,
        "needed": required,
        "status": status,
        "origin": "REVIEWED_INFERENCE",
        "rule_id": "P07",
    }


def _capacity(
    scenario: Mapping[str, Any],
    register: Mapping[str, Any],
    line: Mapping[str, Any],
    demand: Any,
    request_window: Any,
    comparisons: list[dict[str, Any]],
    declared: dict[str, Any],
) -> dict[str, Any]:
    resolved = _resolve(scenario, register, line["capacity_ref"])
    values = _value_of(resolved, "capacity")
    if isinstance(values, Mapping) and "values" in values:
        values = values["values"]
    formula = None
    if isinstance(values, Mapping) and all(
        isinstance(values.get(key), (int, float)) and not isinstance(values.get(key), bool)
        for key in (
            "nameplate_kt",
            "availability",
            "yield",
            "qualification_share",
            "market_allocation_share",
        )
    ):
        formula = effective_qualified_capacity(
            float(values["nameplate_kt"]),
            float(values["availability"]),
            float(values["yield"]),
            float(values["qualification_share"]),
            float(values["market_allocation_share"]),
        )
    allocation_number = None
    if line["availability_basis"] == "DECLARED_ALLOCATION":
        allocation = _resolve(scenario, register, line["allocation_ref"])
        allocation_values = _value_of(allocation, "qualified_available_kt")
        if isinstance(allocation_values, Mapping):
            allocation_values = allocation_values.get("qualified_available_kt")
        if isinstance(allocation_values, (int, float)) and not isinstance(allocation_values, bool):
            allocation_number = float(allocation_values)
    share = values.get("qualification_share") if isinstance(values, Mapping) else None
    qualification = next(
        (row for row in comparisons if row["field_id"] == "customer_qualification"),
        None,
    )
    qualification_status = qualification["status"] if qualification else "NOT_ESTABLISHED"
    line_window = _resolve(scenario, register, line["window_ref"])
    window_result = window_coverage(
        _value_of(line_window, "available_window_months"), request_window
    )
    if line["availability_basis"] == "DECLARED_ALLOCATION":
        allocation = _resolve(scenario, register, line["allocation_ref"])
        allocation_window = window_coverage(_value_of(allocation, "window_months"), request_window)
        if allocation_window == "MISMATCH" or (
            allocation_window == "NOT_ESTABLISHED" and window_result == "COVERED"
        ):
            window_result = allocation_window
    technical_failure = any(
        row["status"] == "LIMITATION_IDENTIFIED" and row["field_id"] != "customer_qualification"
        for row in comparisons
    )
    technical_unknown = any(
        row["status"] in {"NOT_ESTABLISHED", "CONFLICTED"}
        and row["field_id"] != "customer_qualification"
        for row in comparisons
    )
    positive_supply = (
        isinstance(share, (int, float)) and not isinstance(share, bool) and share > 0
    ) or (allocation_number is not None and allocation_number > 0)
    known_zero = (
        qualification_status == "LIMITATION_IDENTIFIED"
        and share == 0
        and allocation_number == 0
    )
    if formula is None or window_result != "COVERED":
        declared["capacity_time_window"] = "U"
    if known_zero:
        admitted, capacity_result = 0.0, "KNOWN_ZERO"
    elif technical_failure and positive_supply:
        admitted, capacity_result = None, "CONFLICTED"
    elif window_result == "MISMATCH":
        admitted, capacity_result = None, "WINDOW_MISMATCH"
    elif technical_unknown or qualification_status in {"NOT_ESTABLISHED", "CONFLICTED"} or window_result != "COVERED":
        admitted, capacity_result = None, "NOT_ESTABLISHED"
    elif (
        allocation_number is not None
        and formula is not None
        and allocation_number > formula
    ):
        admitted, capacity_result = None, "CONFLICTED"
    elif line["availability_basis"] == "DECLARED_ALLOCATION":
        admitted, capacity_result = allocation_number, (
            "ADMITTED" if allocation_number is not None else "NOT_ESTABLISHED"
        )
    elif qualification_status in {"SUPPORTED", "NOT_REQUIRED"} and not technical_failure:
        admitted, capacity_result = formula, "FORMULA" if formula is not None else "NOT_ESTABLISHED"
    else:
        admitted, capacity_result = None, "NOT_ESTABLISHED"
    shortage = None
    if isinstance(admitted, float) and isinstance(demand, (int, float)) and not isinstance(demand, bool):
        shortage = float(demand) - admitted
    return {
        "formula_capacity_kt": formula,
        "admitted_qualified_supply_kt": admitted,
        "allocation_basis": line["availability_basis"],
        "capacity_result": capacity_result,
        "window_result": window_result,
        "shortage_kt": shortage,
    }

def unavailable_lines(reason: str) -> dict[str, Any]:
    """Return a typed empty line assessment."""
    return {"available": False, "reason": reason, "rows": [], "winner": None}
