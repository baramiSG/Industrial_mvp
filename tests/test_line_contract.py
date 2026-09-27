from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.line_contract import validate_candidate_lines
from ior_mvp.scenario_contract import validate_simulation_contract

ROOT = Path(__file__).resolve().parents[1]


def test_orphan_line_reference_fails_closed() -> None:
    scenario = json.loads(
        (
            ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json"
        ).read_text(encoding="utf-8")
    )
    register = scenario["synthetic_inputs"]["candidate_register"]
    lines = deepcopy(scenario["synthetic_inputs"]["candidate_lines"])
    lines["lines"][0]["capacity_ref"] = "FACT-DOES-NOT-EXIST"
    with pytest.raises(EvidenceIntegrityError, match="does not resolve"):
        validate_candidate_lines(lines, register, scenario=scenario, legacy_pointers=True)


def test_alternative_cannot_borrow_the_reference_legacy_pointer() -> None:
    scenario = json.loads(
        (
            ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json"
        ).read_text(encoding="utf-8")
    )
    register = scenario["synthetic_inputs"]["candidate_register"]
    lines = deepcopy(scenario["synthetic_inputs"]["candidate_lines"])
    alternative = next(
        line for line in lines["lines"] if line["reference_role"] == "ALTERNATIVE"
    )
    alternative["capacity_ref"] = "/synthetic_inputs/plant_line"
    with pytest.raises(EvidenceIntegrityError, match="legacy"):
        validate_candidate_lines(lines, register, scenario=scenario, legacy_pointers=True)


def test_formula_basis_rejects_an_allocation_ref() -> None:
    scenario = json.loads(
        (
            ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json"
        ).read_text(encoding="utf-8")
    )
    register = scenario["synthetic_inputs"]["candidate_register"]
    lines = deepcopy(scenario["synthetic_inputs"]["candidate_lines"])
    lines["lines"][0]["allocation_ref"] = "FACT-ALLOC-LINE-96f1bd96c5c6ccda"
    with pytest.raises(EvidenceIntegrityError, match="formula basis"):
        validate_candidate_lines(lines, register, scenario=scenario, legacy_pointers=True)


def test_dangling_required_value_pointer_fails_scenario_validation() -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    item = next(
        row for row in scenario["synthetic_inputs"]["candidate_lines"]["requirement_items"]
        if row["field_id"] == "mfr_range_g_10min"
    )
    item["required_value_ref"] = "/synthetic_inputs/candidate_lines/requirements_additions/DOES_NOT_EXIST"
    with pytest.raises(EvidenceIntegrityError, match="required_value_ref.*does not resolve"):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("unit", "cm", "unit"),
        ("requirement_id", "another_requirement", "requirement"),
        ("value", [1250, 1000], "range"),
        ("value", [600, float("nan")], "finite"),
    ],
)
def test_steel_width_fact_requires_exact_unit_requirement_and_ordered_finite_range(
    field: str, value: object, message: str,
) -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json").read_text(encoding="utf-8")
    )
    fact = next(
        row for row in scenario["synthetic_inputs"]["candidate_register"]["facts"]
        if row["fact_id"] == "FACT-WIDTH-LINE-7315366f6a9166d8"
    )
    fact["values"][field] = value
    with pytest.raises(EvidenceIntegrityError, match=message):
        validate_simulation_contract(scenario)


def test_pp_allocation_above_same_line_formula_is_integrity_error() -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    allocation = next(
        row for row in scenario["synthetic_inputs"]["candidate_register"]["facts"]
        if row["fact_id"] == "FACT-ALLOC-LINE-e403e85a85052861"
    )
    allocation["values"]["qualified_available_kt"] = 90
    with pytest.raises(EvidenceIntegrityError, match="allocation.*formula"):
        validate_simulation_contract(scenario)


def test_pp_allocation_wrong_requirement_is_integrity_error() -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    allocation = next(
        row for row in scenario["synthetic_inputs"]["candidate_register"]["facts"]
        if row["fact_id"] == "FACT-ALLOC-LINE-e403e85a85052861"
    )
    allocation["values"]["requirement_id"] = "unrelated_request"
    with pytest.raises(EvidenceIntegrityError, match="allocation.*requirement"):
        validate_simulation_contract(scenario)


def test_qualification_ref_requires_customer_requirement() -> None:
    scenario = json.loads((ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json").read_text())
    fact = next(row for row in scenario["synthetic_inputs"]["candidate_register"]["facts"]
                if row["fact_id"] == "FACT-QUAL-LINE-96f1bd96c5c6ccda")
    fact["values"]["requirement_id"] = "other_requirement"
    with pytest.raises(EvidenceIntegrityError, match="qualification requirement"):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize("invalid", ["true", 1, [], {}])
def test_candidate_line_qualification_requirement_must_be_boolean(invalid: object) -> None:
    scenario = json.loads((ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json").read_text())
    scenario["synthetic_inputs"]["target_specification"]["customer_qualification_required"] = invalid
    with pytest.raises(EvidenceIntegrityError, match="customer_qualification_required must be boolean"):
        validate_simulation_contract(scenario)


def test_candidate_line_addition_cannot_override_required_flag_with_nonboolean() -> None:
    scenario = json.loads((ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text())
    scenario["synthetic_inputs"]["candidate_lines"]["requirements_additions"]["customer_qualification_required"] = "false"
    with pytest.raises(EvidenceIntegrityError, match="customer_qualification_required must be boolean"):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize("window", [[0, float("nan")], [12, 0]])
def test_nonfinite_or_inverted_month_window_is_rejected(window: list[float]) -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    fact = next(
        row for row in scenario["synthetic_inputs"]["candidate_register"]["facts"]
        if row["fact_id"] == "FACT-WINDOW-LINE-e403e85a85052861"
    )
    fact["values"]["available_window_months"] = window
    with pytest.raises(EvidenceIntegrityError, match="month window"):
        validate_simulation_contract(scenario)


def test_dangling_local_source_pointer_is_rejected() -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    fact = scenario["synthetic_inputs"]["candidate_register"]["facts"][0]
    fact["source_refs"][0]["pointer"] = "/synthetic_inputs/candidate_register/facts/FACT-DOES-NOT-EXIST"
    with pytest.raises(EvidenceIntegrityError, match="source_refs.*does not resolve"):
        validate_simulation_contract(scenario)


def test_public_source_field_must_be_on_the_referenced_record() -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json").read_text(encoding="utf-8")
    )
    refs = [
        ref for fact in scenario["synthetic_inputs"]["candidate_register"]["facts"]
        for ref in fact["source_refs"] if "artifact" in ref
    ]
    assert len(refs) == 1
    refs[0]["field"] = "source_boundary"
    with pytest.raises(EvidenceIntegrityError, match="public ref.*field"):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    ("item_id", "field", "value"),
    [
        ("input_procurement", "admitted_hs6", ["390210"]),
        ("input_procurement", "record_selectors", [["FACTORY_CUSTOMS", "flow"]]),
        ("equipment_acquisition", "admitted_hs6", ["847981"]),
        ("operating_factory", "rule_id", "P09"),
    ],
)
def test_discovery_items_are_bound_to_the_finite_target_mapping(
    item_id: str, field: str, value: object,
) -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-PP-001.json").read_text(encoding="utf-8")
    )
    item = next(
        row for row in scenario["synthetic_inputs"]["candidate_lines"]["requirements_additions"]["discovery_items"]
        if row["item_id"] == item_id
    )
    item[field] = value
    with pytest.raises(EvidenceIntegrityError, match="discovery item"):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize("mutation", ["group_conflict", "nameplate_above_ceiling"])
def test_steel_ceiling_group_and_nameplate_must_reconcile(mutation: str) -> None:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / "SYN-MINISTRY-STEEL-001.json").read_text(encoding="utf-8")
    )
    facts = scenario["synthetic_inputs"]["candidate_register"]["facts"]
    if mutation == "group_conflict":
        ceiling = next(f for f in facts if f["fact_id"] == "FACT-CEIL-LINE-96f1bd96c5c6ccda")
        ceiling["values"]["group_id"] = "CEIL-STEEL-A"
    else:
        capacity = next(f for f in facts if f["fact_id"] == "FACT-CAP-LINE-96f1bd96c5c6ccda")
        capacity["values"]["nameplate_kt"] = 200
    with pytest.raises(EvidenceIntegrityError, match="ceiling"):
        validate_simulation_contract(scenario)
