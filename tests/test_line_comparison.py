from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from ior_mvp.decision_engine import analyze
from ior_mvp.line_comparison import compare_lines

ROOT = Path(__file__).resolve().parents[1]


def _scenario(name: str) -> dict:
    return json.loads(
        (ROOT / "data" / "synthetic" / name).read_text(encoding="utf-8")
    )


def test_steel_reference_capacity_and_width_limit_stay_diagnostic() -> None:
    simulated = analyze("SAU-H0-721049", "simulated")
    assert simulated["simulation_decision"]["state"] == "ADVANCE"
    by_line = {
        row["line_id"]: row for row in simulated["line_assessment"]["rows"]
    }
    reference = by_line["LINE-7315366f6a9166d8"]["capacity"]
    assert round(reference["formula_capacity_kt"], 4) == 57.5092
    assert round(reference["shortage_kt"], 4) == 46.4908
    def width_status(line_id: str) -> str:
        row = by_line[line_id]
        return next(
            item["status"]
            for item in row["comparisons"]
            if item["field_id"] == "width_mm"
        )

    assert width_status("LINE-7315366f6a9166d8") == "SUPPORTED"
    assert width_status("LINE-96f1bd96c5c6ccda") == "LIMITATION_IDENTIFIED"
    assert simulated["line_assessment"]["winner"] is None


def test_width_boundary_is_inclusive() -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(scenario["synthetic_inputs"]["candidate_register"])
    width = next(
        fact
        for fact in register["facts"]
        if fact["fact_id"] == "FACT-WIDTH-LINE-96f1bd96c5c6ccda"
    )
    width["values"]["value"] = [600, 1250]
    result = compare_lines(
        {
            **scenario,
            "synthetic_inputs": {
                **scenario["synthetic_inputs"],
                "candidate_register": register,
            },
        },
        register,
        sector_profile="coated_steel",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    limited = next(
        row for row in result["rows"] if row["line_id"] == "LINE-96f1bd96c5c6ccda"
    )
    assert next(
        item["status"]
        for item in limited["comparisons"]
        if item["field_id"] == "width_mm"
    ) == "SUPPORTED"
    qualification = next(
        item["status"]
        for item in limited["comparisons"]
        if item["field_id"] == "customer_qualification"
    )
    assert qualification == "LIMITATION_IDENTIFIED"
    assert limited["capacity"]["admitted_qualified_supply_kt"] == 0


def test_pp_declared_allocation_differs_from_formula() -> None:
    simulated = analyze("SAU-H0-390210", "simulated")
    assert simulated["real_decision"]["state"] == "REJECT"
    assert simulated["simulation_decision"]["state"] == "REJECT"
    resin = next(
        row
        for row in simulated["line_assessment"]["rows"]
        if row["line_id"] == "LINE-e403e85a85052861"
    )
    assert round(resin["capacity"]["formula_capacity_kt"], 5) == 85.24845
    assert resin["capacity"]["admitted_qualified_supply_kt"] == 70
    assert next(
        item["status"]
        for item in resin["comparisons"]
        if item["field_id"] == "mfr_range_g_10min"
    ) == "SUPPORTED"


def test_withheld_distance_names_typed_gate_and_affected_requirement() -> None:
    steel = {row["line_id"]: row for row in analyze("SAU-H0-721049", "simulated")["line_assessment"]["rows"]}
    resin = {row["line_id"]: row for row in analyze("SAU-H0-390210", "simulated")["line_assessment"]["rows"]}
    a = steel["LINE-7315366f6a9166d8"]
    c = steel["LINE-4fbdbb0b2c107968"]
    b = resin["LINE-cb9a42384c3523ec"]
    assert a["capability"]["known_weight_coverage"] == 1
    assert a["capability"]["d_star"] == 0.2667
    assert not any(status in {"known failure", "unavailable"} for status in a["gates"].values())
    assert c["capability"]["known_weight_coverage"] == 0
    assert c["capability"]["d_star"] is None
    assert c["gates"]["width_thickness_envelope"] == "unavailable"
    assert set(c["gate_requirements"]["width_thickness_envelope"]) == {"width_mm", "thickness_mm"}
    assert b["capability"]["known_weight_coverage"] == 1
    assert b["capability"]["d_star"] is None
    assert b["gates"]["performance_requirement"] == "known failure"
    assert b["gate_requirements"]["performance_requirement"] == ["mfr_range_g_10min"]


def test_mfr_mutation_preserves_customer_applicability() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    register = deepcopy(scenario["synthetic_inputs"]["candidate_register"])
    mfr = next(
        fact for fact in register["facts"]
        if fact["fact_id"] == "FACT-MFR-LINE-e403e85a85052861"
    )
    mfr["values"]["value"] = [8, 19]
    result = compare_lines(
        {**scenario, "synthetic_inputs": {**scenario["synthetic_inputs"], "candidate_register": register}},
        register,
        sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(item for item in result["rows"] if item["line_id"] == "LINE-e403e85a85052861")
    assert next(item["status"] for item in row["comparisons"] if item["field_id"] == "mfr_range_g_10min") == "LIMITATION_IDENTIFIED"
    assert next(item["status"] for item in row["comparisons"] if item["field_id"] == "customer_qualification") == "NOT_REQUIRED"


def test_lowering_declared_allocation_changes_admitted_supply() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    register = deepcopy(scenario["synthetic_inputs"]["candidate_register"])
    allocation = next(
        fact for fact in register["facts"]
        if fact["fact_id"] == "FACT-ALLOC-LINE-e403e85a85052861"
    )
    allocation["values"]["qualified_available_kt"] = 55
    result = compare_lines(
        {**scenario, "synthetic_inputs": {**scenario["synthetic_inputs"], "candidate_register": register}},
        register,
        sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(item for item in result["rows"] if item["line_id"] == "LINE-e403e85a85052861")
    assert row["capacity"]["formula_capacity_kt"] != 55
    assert row["capacity"]["admitted_qualified_supply_kt"] == 55


def test_register_inputs_are_not_mutated() -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    before = deepcopy(register)
    compare_lines(
        scenario,
        register,
        sector_profile="coated_steel",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    assert register == before


def test_unknown_current_mfr_withholds_declared_pp_supply() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    lines = scenario["synthetic_inputs"]["candidate_lines"]["lines"]
    line = next(row for row in lines if row["line_id"] == "LINE-e403e85a85052861")
    line["technical_fact_refs"]["mfr_range_g_10min"] = None
    register = scenario["synthetic_inputs"]["candidate_register"]
    result = compare_lines(
        scenario, register, sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(row for row in result["rows"] if row["line_id"] == line["line_id"])
    assert next(c["status"] for c in row["comparisons"] if c["field_id"] == "mfr_range_g_10min") == "NOT_ESTABLISHED"
    assert round(row["capacity"]["formula_capacity_kt"], 5) == 85.24845
    assert row["capacity"]["admitted_qualified_supply_kt"] is None
    assert row["capacity"]["shortage_kt"] is None


def test_disjoint_availability_withholds_pp_supply_without_process_failure() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    window = next(f for f in register["facts"] if f["fact_id"] == "FACT-WINDOW-LINE-e403e85a85052861")
    window["values"]["available_window_months"] = [12, 24]
    result = compare_lines(
        scenario, register, sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(row for row in result["rows"] if row["line_id"] == "LINE-e403e85a85052861")
    assert row["capacity"]["window_result"] == "MISMATCH"
    assert row["capacity"]["admitted_qualified_supply_kt"] is None
    assert row["capacity"]["formula_capacity_kt"] is not None
    assert row["gates"]["conversion_route"] == "resolved"
    assert next(d["state"] for d in row["capability"]["dimensions"] if d["dimension"] == "capacity_time_window") == "U"


def test_required_customer_approval_for_wrong_application_cannot_admit_steel_supply() -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    fact = next(f for f in register["facts"] if f["fact_id"] == "FACT-QUAL-LINE-7315366f6a9166d8")
    fact["values"]["application"] = "automotive parts"
    result = compare_lines(
        scenario, register, sector_profile="coated_steel",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(r for r in result["rows"] if r["line_id"] == "LINE-7315366f6a9166d8")
    qualification = next(c for c in row["comparisons"] if c["field_id"] == "customer_qualification")
    assert qualification["status"] == "NOT_ESTABLISHED"
    assert row["capacity"]["admitted_qualified_supply_kt"] is None
    assert row["gates"]["coating_route_and_mass"] == "resolved"


def test_exact_steel_qualification_preserves_positive_and_dated_negative() -> None:
    rows = {row["line_id"]: row for row in analyze("SAU-H0-721049", "simulated")["line_assessment"]["rows"]}
    supported = rows["LINE-7315366f6a9166d8"]
    negative = rows["LINE-96f1bd96c5c6ccda"]
    status = lambda row: next(item["status"] for item in row["comparisons"] if item["field_id"] == "customer_qualification")
    assert status(supported) == "SUPPORTED"
    assert status(negative) == "LIMITATION_IDENTIFIED"
    assert negative["capacity"]["admitted_qualified_supply_kt"] == 0
    assert negative["capacity"]["capacity_result"] == "KNOWN_ZERO"
    assert negative["capacity"]["window_result"] == "MISMATCH"


def test_qualification_scope_and_positive_window_fail_closed() -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    facts = {fact["fact_id"]: fact for fact in register["facts"]}
    positive = facts["FACT-QUAL-LINE-7315366f6a9166d8"]
    negative = facts["FACT-QUAL-LINE-96f1bd96c5c6ccda"]
    def rows():
        return {row["line_id"]: row for row in compare_lines(
            scenario, register, sector_profile="coated_steel",
            decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
        )["rows"]}
    def status(row):
        return next(item["status"] for item in row["comparisons"] if item["field_id"] == "customer_qualification")
    positive["values"]["valid_window_months"] = [0, 12]
    assert status(rows()["LINE-7315366f6a9166d8"]) == "NOT_ESTABLISHED"
    positive["values"]["valid_window_months"] = [18, 36]
    for fact, line_id in ((positive, "LINE-7315366f6a9166d8"), (negative, "LINE-96f1bd96c5c6ccda")):
        fact["values"]["application"] = "unrelated application"
        assert status(rows()[line_id]) == "NOT_ESTABLISHED"
        fact["values"]["application"] = "coastal construction panels"
        fact["values"]["requirement_id"] = "unrelated_requirement"
        assert status(rows()[line_id]) == "NOT_ESTABLISHED"
        fact["values"]["requirement_id"] = "customer_qualification"


def test_missing_qualification_row_remains_explicit() -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    line = scenario["synthetic_inputs"]["candidate_lines"]["lines"][0]
    line["qualification_ref"] = None
    row = next(item for item in compare_lines(
        scenario, scenario["synthetic_inputs"]["candidate_register"],
        sector_profile="coated_steel",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )["rows"] if item["line_id"] == line["line_id"])
    assert next(item["status"] for item in row["comparisons"] if item["field_id"] == "customer_qualification") == "NOT_ESTABLISHED"


def test_qualification_needs_literal_scope_required_flag_and_requested_window() -> None:
    def status(scenario):
        row = next(item for item in compare_lines(
            scenario, scenario["synthetic_inputs"]["candidate_register"],
            sector_profile="coated_steel",
            decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
        )["rows"] if item["line_id"] == "LINE-7315366f6a9166d8")
        return next(item["status"] for item in row["comparisons"] if item["field_id"] == "customer_qualification")

    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    assert status(scenario) == "SUPPORTED"
    fact = next(item for item in scenario["synthetic_inputs"]["candidate_register"]["facts"]
                if item["fact_id"] == "FACT-QUAL-LINE-7315366f6a9166d8")
    fact["values"]["application"] = "declared"
    assert status(scenario) == "NOT_ESTABLISHED"
    fact["values"]["application"] = "coastal construction panels"
    scenario["synthetic_inputs"]["target_specification"]["application"] = None
    assert status(scenario) == "NOT_ESTABLISHED"
    scenario["synthetic_inputs"]["target_specification"]["application"] = "coastal construction panels"
    scenario["synthetic_inputs"]["candidate_lines"]["requirements_additions"]["request_window_months"] = None
    assert status(scenario) == "NOT_ESTABLISHED"
    scenario["synthetic_inputs"]["candidate_lines"]["requirements_additions"]["request_window_months"] = [18, 30]
    scenario["synthetic_inputs"]["target_specification"]["customer_qualification_required"] = None
    assert status(scenario) == "NOT_ESTABLISHED"
    scenario["synthetic_inputs"]["target_specification"].pop("customer_qualification_required")
    assert status(scenario) == "NOT_ESTABLISHED"


def test_conflicting_current_mfr_facts_withhold_pp_supply() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    original = next(f for f in register["facts"] if f["fact_id"] == "FACT-MFR-LINE-e403e85a85052861")
    conflicting = deepcopy(original)
    conflicting["fact_id"] = "FACT-MFR-CONFLICT-LINE-e403e85a85052861"
    conflicting["values"]["value"] = [2, 6]
    register["facts"].append(conflicting)
    result = compare_lines(
        scenario, register, sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(r for r in result["rows"] if r["line_id"] == "LINE-e403e85a85052861")
    comparison = next(c for c in row["comparisons"] if c["field_id"] == "mfr_range_g_10min")
    assert comparison["status"] == "CONFLICTED"
    assert row["capacity"]["admitted_qualified_supply_kt"] is None


def test_false_tooling_requirement_needs_known_resin_scope() -> None:
    scenario = _scenario("SYN-MINISTRY-PP-001.json")
    line = next(r for r in scenario["synthetic_inputs"]["candidate_lines"]["lines"] if r["line_id"] == "LINE-e403e85a85052861")
    line["technical_fact_refs"]["manufacturing_scope"] = None
    register = scenario["synthetic_inputs"]["candidate_register"]
    result = compare_lines(
        scenario, register, sector_profile="technical_plastics",
        decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
    )
    row = next(r for r in result["rows"] if r["line_id"] == line["line_id"])
    tooling = next(c for c in row["comparisons"] if c["field_id"] == "tooling_required")
    assert tooling["status"] == "NOT_ESTABLISHED"
    assert row["gates"]["tooling"] == "unavailable"
    assert row["capacity"]["admitted_qualified_supply_kt"] is None
