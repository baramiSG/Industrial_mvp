from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.public_decision import evaluate_hard_exclusions


UNAVAILABLE = "UNAVAILABLE"


def _inputs() -> dict:
    return {
        "heterogeneous_residual_code": {
            "commercial_product_separable": True,
            "product_level_evidence_available": True,
            "evidence_ids": ["E-ID"],
        },
        "downside_market_below_mes": {
            "sustainable_downside_demand_kt": 100.0,
            "minimum_efficient_scale_kt": 50.0,
            "credible_export_contract": False,
            "evidence_ids": ["E-DEMAND"],
        },
        "unsatisfiable_hard_gate": {
            "gate_domain": "safety",
            "gate_satisfiability": "SATISFIABLE",
            "evidence_ids": ["E-GATE"],
        },
        "idle_equivalent_domestic_capacity": {
            "domestic_specification_equivalent": False,
            "qualified_idle_capacity_kt": 0.0,
            "target_specification_demand_kt": 100.0,
            "binding_market_failure": True,
            "evidence_ids": ["E-CAP"],
        },
        "transitory_or_measurement_gap": {
            "dominant_cause": "OTHER",
            "evidence_ids": ["E-FLOW"],
        },
        "redundancy_or_crowd_out": {
            "competition_finding": "ACCEPTABLE",
            "evidence_ids": ["E-ROUTE"],
        },
    }


def _evaluate(inputs: dict | None = None) -> dict[str, dict]:
    results = evaluate_hard_exclusions(
        {"hard_exclusion_inputs": inputs or _inputs()}
    )
    assert [row["code"] for row in results] == [
        "EX-01_HETEROGENEOUS_RESIDUAL",
        "EX-02_MARKET_BELOW_MES",
        "EX-03_UNSATISFIABLE_HARD_GATE",
        "EX-04_IDLE_EQUIVALENT_CAPACITY",
        "EX-05_TRANSITORY_OR_MEASUREMENT",
        "EX-06_REDUNDANCY_OR_CROWD_OUT",
    ]
    return {row["code"]: row for row in results}


@pytest.mark.parametrize(
    ("separable", "product_evidence", "expected"),
    [
        (False, False, "SATISFIED"),
        (True, UNAVAILABLE, "NOT_SATISFIED"),
        (UNAVAILABLE, True, "NOT_SATISFIED"),
        (False, UNAVAILABLE, "NOT_CALCULABLE"),
    ],
)
def test_ex01_heterogeneous_residual_truth_table(
    separable,
    product_evidence,
    expected: str,
) -> None:
    inputs = _inputs()
    block = inputs["heterogeneous_residual_code"]
    block["commercial_product_separable"] = separable
    block["product_level_evidence_available"] = product_evidence

    assert _evaluate(inputs)[
        "EX-01_HETEROGENEOUS_RESIDUAL"
    ]["status"] == expected


@pytest.mark.parametrize(
    ("demand", "mes", "contract", "expected"),
    [
        (49.999, 50.0, False, "SATISFIED"),
        (50.0, 50.0, False, "NOT_SATISFIED"),
        (40.0, 50.0, True, "NOT_SATISFIED"),
        (UNAVAILABLE, 50.0, False, "NOT_CALCULABLE"),
    ],
)
def test_ex02_market_below_mes_truth_table(
    demand,
    mes,
    contract,
    expected: str,
) -> None:
    inputs = _inputs()
    block = inputs["downside_market_below_mes"]
    block["sustainable_downside_demand_kt"] = demand
    block["minimum_efficient_scale_kt"] = mes
    block["credible_export_contract"] = contract

    assert _evaluate(inputs)["EX-02_MARKET_BELOW_MES"][
        "status"
    ] == expected


@pytest.mark.parametrize(
    ("satisfiability", "expected"),
    [
        ("UNSATISFIABLE", "SATISFIED"),
        ("SATISFIABLE", "NOT_SATISFIED"),
        (UNAVAILABLE, "NOT_CALCULABLE"),
    ],
)
def test_ex03_unsatisfiable_gate_truth_table(
    satisfiability: str,
    expected: str,
) -> None:
    inputs = _inputs()
    inputs["unsatisfiable_hard_gate"][
        "gate_satisfiability"
    ] = satisfiability

    assert _evaluate(inputs)[
        "EX-03_UNSATISFIABLE_HARD_GATE"
    ]["status"] == expected


@pytest.mark.parametrize(
    ("equivalent", "idle", "demand", "market_failure", "expected"),
    [
        (True, 100.0, 100.0, False, "SATISFIED"),
        (True, 99.999, 100.0, False, "NOT_SATISFIED"),
        (False, 120.0, 100.0, False, "NOT_SATISFIED"),
        (True, 120.0, 100.0, True, "NOT_SATISFIED"),
        (True, UNAVAILABLE, 100.0, False, "NOT_CALCULABLE"),
    ],
)
def test_ex04_idle_equivalent_capacity_truth_table(
    equivalent,
    idle,
    demand,
    market_failure,
    expected: str,
) -> None:
    inputs = _inputs()
    block = inputs["idle_equivalent_domestic_capacity"]
    block["domestic_specification_equivalent"] = equivalent
    block["qualified_idle_capacity_kt"] = idle
    block["target_specification_demand_kt"] = demand
    block["binding_market_failure"] = market_failure

    assert _evaluate(inputs)[
        "EX-04_IDLE_EQUIVALENT_CAPACITY"
    ]["status"] == expected


@pytest.mark.parametrize(
    ("cause", "expected"),
    [
        ("REEXPORT", "SATISFIED"),
        ("ONE_OFF_PROJECT", "SATISFIED"),
        ("TEMPORARY_PRICE_ARBITRAGE", "SATISFIED"),
        ("CLASSIFICATION_DISCONTINUITY", "SATISFIED"),
        ("OTHER", "NOT_SATISFIED"),
        (UNAVAILABLE, "NOT_CALCULABLE"),
    ],
)
def test_ex05_transitory_gap_truth_table(
    cause: str,
    expected: str,
) -> None:
    inputs = _inputs()
    inputs["transitory_or_measurement_gap"][
        "dominant_cause"
    ] = cause

    assert _evaluate(inputs)[
        "EX-05_TRANSITORY_OR_MEASUREMENT"
    ]["status"] == expected


@pytest.mark.parametrize(
    ("finding", "expected"),
    [
        ("UNACCEPTABLE_REDUNDANT_CAPACITY", "SATISFIED"),
        ("UNACCEPTABLE_CROWD_OUT", "SATISFIED"),
        ("ACCEPTABLE", "NOT_SATISFIED"),
        (UNAVAILABLE, "NOT_CALCULABLE"),
    ],
)
def test_ex06_redundancy_truth_table(
    finding: str,
    expected: str,
) -> None:
    inputs = _inputs()
    inputs["redundancy_or_crowd_out"][
        "competition_finding"
    ] = finding

    assert _evaluate(inputs)[
        "EX-06_REDUNDANCY_OR_CROWD_OUT"
    ]["status"] == expected


@pytest.mark.parametrize(
    ("block_name", "field"),
    [
        (
            "heterogeneous_residual_code",
            "commercial_product_separable",
        ),
        (
            "heterogeneous_residual_code",
            "product_level_evidence_available",
        ),
        (
            "downside_market_below_mes",
            "sustainable_downside_demand_kt",
        ),
        (
            "downside_market_below_mes",
            "minimum_efficient_scale_kt",
        ),
        ("downside_market_below_mes", "credible_export_contract"),
        ("unsatisfiable_hard_gate", "gate_satisfiability"),
        (
            "idle_equivalent_domestic_capacity",
            "domestic_specification_equivalent",
        ),
        (
            "idle_equivalent_domestic_capacity",
            "qualified_idle_capacity_kt",
        ),
        (
            "idle_equivalent_domestic_capacity",
            "target_specification_demand_kt",
        ),
        (
            "idle_equivalent_domestic_capacity",
            "binding_market_failure",
        ),
        ("transitory_or_measurement_gap", "dominant_cause"),
        ("redundancy_or_crowd_out", "competition_finding"),
    ],
)
def test_each_unknown_exclusion_input_never_satisfies(
    block_name: str,
    field: str,
) -> None:
    inputs = _inputs()
    inputs[block_name][field] = UNAVAILABLE

    results = evaluate_hard_exclusions(
        {"hard_exclusion_inputs": inputs}
    )

    assert all(row["status"] != "SATISFIED" for row in results)


def test_all_six_checks_run_and_first_satisfied_remains_first() -> None:
    inputs = _inputs()
    inputs["heterogeneous_residual_code"].update(
        {
            "commercial_product_separable": False,
            "product_level_evidence_available": False,
        }
    )
    inputs["unsatisfiable_hard_gate"][
        "gate_satisfiability"
    ] = "UNSATISFIABLE"

    results = evaluate_hard_exclusions(
        {"hard_exclusion_inputs": inputs}
    )

    assert len(results) == 6
    satisfied = [
        row["code"]
        for row in results
        if row["status"] == "SATISFIED"
    ]
    assert satisfied == [
        "EX-01_HETEROGENEOUS_RESIDUAL",
        "EX-03_UNSATISFIABLE_HARD_GATE",
    ]


def test_exclusion_results_include_bilingual_catalogue_narratives() -> None:
    result = _evaluate()["EX-03_UNSATISFIABLE_HARD_GATE"]

    assert result["reason_code"] == "EXCLUSION_NOT_SATISFIED"
    assert result["narrative"] == (
        "A legal, safety, environmental, IP or "
        "customer-qualification hard gate cannot be satisfied."
    )
    assert result["localized_narrative"]["en"] == result["narrative"]
    assert result["localized_narrative"]["ar"].startswith(
        "يتعذر استيفاء"
    )


def test_ratio_warning_alone_never_becomes_ex06_evidence() -> None:
    inputs = _inputs()
    inputs["redundancy_or_crowd_out"][
        "competition_finding"
    ] = UNAVAILABLE
    case = {
        "hard_exclusion_inputs": inputs,
        "competition": {
            "post_entry_capacity_to_downside_demand": 1.25
        },
    }

    result = {
        row["code"]: row
        for row in evaluate_hard_exclusions(case)
    }["EX-06_REDUNDANCY_OR_CROWD_OUT"]

    assert result["status"] == "NOT_CALCULABLE"
