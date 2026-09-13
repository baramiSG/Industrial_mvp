from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

import ior_mvp.decision_engine as decision_engine
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    reconcile_synthetic_scenario,
    require_scenario_reconciliation,
)
from scripts.validate_scenarios import (
    PUBLIC_DIR,
    SYNTHETIC_DIR,
    main,
    validate_scenario_directories,
)


def _scenario(opportunity_id: str) -> dict:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    return deepcopy(scenario)


def _checks(report: dict) -> dict[str, dict]:
    return {
        check["rule_id"]: check
        for check in report["checks"]
    }


@pytest.mark.parametrize(
    (
        "opportunity_id",
        "target",
        "public_imports",
        "nameplate",
        "public_nameplate",
    ),
    [
        (
            "SAU-H0-721049",
            104.0,
            287.9,
            250.0,
            250.0,
        ),
        (
            "SAU-H0-390210",
            56.0,
            56.0,
            1170.0,
            1170.0,
        ),
    ],
)
def test_current_scenarios_reconcile_to_public_marginals(
    opportunity_id: str,
    target: float,
    public_imports: float,
    nameplate: float,
    public_nameplate: float,
) -> None:
    report = reconcile_synthetic_scenario(
        _scenario(opportunity_id),
        get_public_case(opportunity_id),
    )
    checks = _checks(report)

    assert report["status"] == "PASS"
    demand = checks[
        "target_spec_demand_within_public_imports"
    ]
    assert demand["result"] == "PASS"
    assert demand["inputs"]["target_spec_demand_kt"] == target
    assert (
        demand["inputs"]["latest_public_imports_kt"]
        == public_imports
    )
    capacity = checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]
    assert capacity["result"] == "PASS"
    assert capacity["inputs"]["line_nameplate_kt"] == nameplate
    assert (
        capacity["inputs"]["disclosed_public_nameplate_kt"]
        == public_nameplate
    )
    assert (
        checks["capacity_factors_within_unit_interval"]["result"]
        == "PASS"
    )


def test_steel_reconciliation_arithmetic_is_exact() -> None:
    report = reconcile_synthetic_scenario(
        _scenario("SAU-H0-721049"),
        get_public_case("SAU-H0-721049"),
    )
    checks = _checks(report)

    assert checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]["inputs"]["disclosed_installed_capacity_tpy"] == [
        250000.0,
        None,
    ]
    assert checks[
        "qualified_availability_within_physical_output"
    ]["result"] == "NOT_APPLICABLE"
    layers = checks["demand_layers_remain_separate"]
    assert layers["result"] == "INFORMATIONAL"
    assert layers["blocking"] is False
    assert layers["inputs"] == {
        "target_spec_demand_kt": 104.0,
        "downside_demand_kt": 100.0,
        "committed_demand_kt": 74.0,
        "base_demand_kt": None,
        "downside_within_target": True,
        "committed_within_target": True,
    }


def test_pp_reconciliation_arithmetic_is_exact() -> None:
    report = reconcile_synthetic_scenario(
        _scenario("SAU-H0-390210"),
        get_public_case("SAU-H0-390210"),
    )
    checks = _checks(report)

    assert checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]["inputs"]["disclosed_installed_capacity_tpy"] == [
        None,
        450000.0,
        720000.0,
    ]
    availability = checks[
        "qualified_availability_within_physical_output"
    ]
    assert availability["result"] == "PASS"
    assert availability["inputs"][
        "physical_output_ceiling_kt"
    ] == pytest.approx(1055.457)
    assert availability["inputs"][
        "qualified_available_kt"
    ] == pytest.approx(80.0)
    layers = checks["demand_layers_remain_separate"]
    assert layers["result"] == "INFORMATIONAL"
    assert layers["inputs"][
        "downside_within_target"
    ] is True
    assert layers["inputs"][
        "committed_within_target"
    ] is True


@pytest.mark.parametrize(
    ("field_path", "invalid_value", "failed_rule"),
    [
        (
            ("demand", "target_spec_demand_kt"),
            288.0,
            "target_spec_demand_within_public_imports",
        ),
        (
            ("plant_line", "nameplate_kt"),
            250.001,
            "line_nameplate_within_disclosed_public_capacity",
        ),
    ],
)
def test_analyze_simulated_blocks_each_public_marginal_failure(
    monkeypatch: pytest.MonkeyPatch,
    field_path: tuple[str, str],
    invalid_value: float,
    failed_rule: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    block, field = field_path
    scenario["synthetic_inputs"][block][field] = invalid_value
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(EvidenceIntegrityError) as captured:
        decision_engine.analyze_simulated("SAU-H0-721049")

    assert failed_rule in str(captured.value)


def test_reconciliation_failure_report_is_rejected() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    assert report["status"] == "FAIL"
    with pytest.raises(
        EvidenceIntegrityError,
        match="target_spec_demand_within_public_imports",
    ):
        require_scenario_reconciliation(report)


def test_pp_physical_availability_equality_passes_and_excess_fails() -> None:
    public_case = get_public_case("SAU-H0-390210")
    scenario = _scenario("SAU-H0-390210")
    ceiling = 1170.0 * 0.93 * 0.97
    scenario["synthetic_inputs"]["equivalence"][
        "qualified_available_kt"
    ] = ceiling

    equality = reconcile_synthetic_scenario(
        scenario,
        public_case,
    )
    assert _checks(equality)[
        "qualified_availability_within_physical_output"
    ]["result"] == "PASS"

    scenario["synthetic_inputs"]["equivalence"][
        "qualified_available_kt"
    ] = ceiling + 0.001
    excess = reconcile_synthetic_scenario(
        scenario,
        public_case,
    )
    assert _checks(excess)[
        "qualified_availability_within_physical_output"
    ]["result"] == "FAIL"
    assert excess["status"] == "FAIL"


@pytest.mark.parametrize("invalid", [-0.001, 1.001])
def test_capacity_factor_outside_unit_interval_fails(
    invalid: float,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["plant_line"][
        "availability"
    ] = invalid

    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    assert _checks(report)[
        "capacity_factors_within_unit_interval"
    ]["result"] == "FAIL"
    assert report["status"] == "FAIL"


def test_demand_layer_ordering_is_informational_not_blocking() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "downside_demand_kt"
    ] = 105.0

    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )
    observation = _checks(report)[
        "demand_layers_remain_separate"
    ]

    assert observation["result"] == "INFORMATIONAL"
    assert observation["blocking"] is False
    assert observation["inputs"][
        "downside_within_target"
    ] is False
    assert report["status"] == "PASS"


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_absent_allocation_block_is_reported_not_applicable(
    opportunity_id: str,
) -> None:
    report = reconcile_synthetic_scenario(
        _scenario(opportunity_id),
        get_public_case(opportunity_id),
    )
    allocation = _checks(report)[
        "tariff_line_allocation_sums_to_public_hs6_total"
    ]

    assert allocation["result"] == "NOT_APPLICABLE"
    assert allocation["inputs"] == {}
    assert report["status"] == "PASS"


def test_successful_simulation_exposes_reconciliation_report() -> None:
    result = decision_engine.analyze_simulated(
        "SAU-H0-721049"
    )

    assert result["integrity"][
        "scenario_reconciliation"
    ]["status"] == "PASS"


def _write_temp_fixture_pair(
    root: Path,
    scenario: dict,
    public_case: dict,
) -> tuple[Path, Path]:
    synthetic_dir = root / "data" / "synthetic"
    public_dir = root / "data" / "snapshots" / "public"
    synthetic_dir.mkdir(parents=True)
    public_dir.mkdir(parents=True)
    (synthetic_dir / "scenario.json").write_text(
        json.dumps(scenario),
        encoding="utf-8",
    )
    live_name = Path(public_case["supersedes"]).name
    (public_dir / live_name).write_text(
        json.dumps(public_case),
        encoding="utf-8",
    )
    historical = root / public_case["supersedes"]
    historical.parent.mkdir(parents=True, exist_ok=True)
    historical.write_bytes(
        (
            Path(__file__).resolve().parents[1]
            / public_case["supersedes"]
        ).read_bytes()
    )
    return synthetic_dir, public_dir


def test_repository_scenario_validator_passes_current_fixtures(
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = main(SYNTHETIC_DIR, PUBLIC_DIR)

    assert status == 0
    output = capsys.readouterr().out
    assert "SCENARIO VALIDATION PASS (7 scenarios)" in output
    assert "status=PASS" in output
    assert (
        "tariff_line_allocation_sums_to_public_hs6_total: "
        "NOT_APPLICABLE"
    ) in output
    assert output.count("ground_truth_backtest: PASS") == 7


def test_validator_reports_exact_ground_truth_for_all_scenarios() -> None:
    reports = validate_scenario_directories(
        SYNTHETIC_DIR,
        PUBLIC_DIR,
    )
    by_scenario = {
        report["scenario_id"]: report
        for report in reports
    }

    expected = {
        "SYN-MINISTRY-STEEL-001": ("ADVANCE", 5),
        "SYN-MINISTRY-PP-001": ("REJECT", 0),
        "SYN-MINISTRY-GALVALUME-001": ("ADVANCE", 3),
        "SYN-MINISTRY-TINPLATE-001": ("ADVANCE", 7),
        "SYN-MINISTRY-ALU-FOIL-001": ("ADVANCE", 6),
        "SYN-MINISTRY-ALU-PROFILES-001": ("ADVANCE", 4),
        "SYN-MINISTRY-PE-FILM-001": ("REJECT", 0),
    }
    assert set(by_scenario) == set(expected)
    for scenario_id, (state, route_code) in expected.items():
        assert by_scenario[scenario_id]["ground_truth_backtest"] == {
            "expected": {"state": state, "route_code": route_code},
            "actual": {"state": state, "route_code": route_code},
            "match": True,
        }


def test_validator_returns_one_for_ground_truth_mismatch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    scenario["ground_truth"]["expected_route_code"] = 0
    scenario["decision_narrative"]["REJECT"] = deepcopy(
        _scenario("SAU-H0-390210")["decision_narrative"]["REJECT"]
    )
    synthetic_dir, public_dir = _write_temp_fixture_pair(
        tmp_path,
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    status = main(synthetic_dir, public_dir)

    assert status == 1
    output = capsys.readouterr().out
    assert (
        "SCENARIO VALIDATION FAIL (1/1 scenarios failed)"
        in output
    )
    assert "ground_truth_backtest: FAIL" in output
    assert (
        "expected state=REJECT, route_code=0; "
        "actual state=ADVANCE, route_code=5"
    ) in output


def test_validator_returns_one_for_temp_reconciliation_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    synthetic_dir, public_dir = _write_temp_fixture_pair(
        tmp_path,
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    status = main(synthetic_dir, public_dir)

    assert status == 1
    output = capsys.readouterr().out
    assert (
        "SCENARIO VALIDATION FAIL (1/1 scenarios failed)"
        in output
    )
    assert (
        "target_spec_demand_within_public_imports: FAIL"
        in output
    )


def test_validator_returns_two_for_invalid_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    synthetic_dir = tmp_path / "data" / "synthetic"
    public_dir = tmp_path / "data" / "snapshots" / "public"
    synthetic_dir.mkdir(parents=True)
    public_dir.mkdir(parents=True)
    (synthetic_dir / "broken.json").write_text(
        "{",
        encoding="utf-8",
    )
    public_case = get_public_case("SAU-H0-721049")
    (public_dir / "SAU-H0-721049.json").write_text(
        json.dumps(public_case),
        encoding="utf-8",
    )
    historical = tmp_path / public_case["supersedes"]
    historical.parent.mkdir(parents=True, exist_ok=True)
    historical.write_bytes(
        (
            Path(__file__).resolve().parents[1]
            / public_case["supersedes"]
        ).read_bytes()
    )

    status = main(synthetic_dir, public_dir)

    assert status == 2
    assert (
        "SCENARIO VALIDATION ERROR: JSONDecodeError"
        in capsys.readouterr().err
    )


def test_validator_returns_two_for_invalid_public_snapshot(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    public_case = deepcopy(get_public_case("SAU-H0-721049"))
    public_case["evidence"][0]["reviewer_status"] = ""
    synthetic_dir, public_dir = _write_temp_fixture_pair(
        tmp_path,
        _scenario("SAU-H0-721049"),
        public_case,
    )

    status = main(synthetic_dir, public_dir)

    assert status == 2
    assert "PublicSnapshotIntegrityError" in capsys.readouterr().err


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "simulation"


def _load_reconciliation_fixture() -> dict:
    return json.loads(
        (FIXTURE_ROOT / "sim-reconciliation-blocks.json").read_text(
            encoding="utf-8"
        )
    )


def test_reconciliation_fixture_passes_all_ten_checks() -> None:
    scenario = _load_reconciliation_fixture()
    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )
    assert report["status"] == "PASS"
    assert [check["rule_id"] for check in report["checks"]] == [
        "target_spec_demand_within_public_imports",
        "line_nameplate_within_disclosed_public_capacity",
        "capacity_factors_within_unit_interval",
        "qualified_availability_within_physical_output",
        "demand_layers_remain_separate",
        "tariff_line_allocation_sums_to_public_hs6_total",
        "buyer_allocation_within_public_imports",
        "expansion_assumption_disclosed_and_bounded",
        "retained_flows_reconcile_to_public_trade",
        "base_demand_and_commitment_probability_valid",
    ]


@pytest.mark.parametrize(
    ("mutation", "failed_rule"),
    [
        (
            lambda scenario: scenario["synthetic_inputs"][
                "tariff_line_allocation"
            ]["lines"][0].__setitem__("quantity_kt", 287.8),
            "tariff_line_allocation_sums_to_public_hs6_total",
        ),
        (
            lambda scenario: scenario["synthetic_inputs"][
                "buyer_allocation"
            ]["buyers"].append(
                {
                    "buyer_id": "B3",
                    "segment": "extra",
                    "quantity_kt": 1.0,
                }
            ),
            "buyer_allocation_within_public_imports",
        ),
        (
            lambda scenario: scenario["synthetic_inputs"][
                "expansion_assumption"
            ].__setitem__("commissioning_year", 2025),
            "expansion_assumption_disclosed_and_bounded",
        ),
        (
            lambda scenario: scenario["synthetic_inputs"][
                "tariff_line_allocation"
            ]["lines"][0].__setitem__("quantity_kt", 288.0),
            "tariff_line_allocation_sums_to_public_hs6_total",
        ),
        (
            lambda scenario: scenario["synthetic_inputs"][
                "production_and_retained_flows"
            ].__setitem__("retained_imports_kt", 288.0),
            "retained_flows_reconcile_to_public_trade",
        ),
        (
            lambda scenario: scenario["synthetic_inputs"]["demand"].__setitem__(
                "commitment_probability", 1.001
            ),
            "base_demand_and_commitment_probability_valid",
        ),
    ],
)
def test_reconciliation_fixture_mutations_fail_exactly_one_check(
    mutation: object,
    failed_rule: str,
) -> None:
    scenario = _load_reconciliation_fixture()
    mutation(scenario)
    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )
    assert report["status"] == "FAIL"
    failed = [
        check["rule_id"]
        for check in report["checks"]
        if check["result"] == "FAIL"
    ]
    assert failed == [failed_rule]
    with pytest.raises(
        EvidenceIntegrityError,
        match=failed_rule,
    ):
        require_scenario_reconciliation(report)
