from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.capability import (
    evaluate_capability,
    publication_allowed,
    route_band,
)
from ior_mvp.config import thresholds_config
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.decision_engine import analyze, competition_warning
from ior_mvp.genui import build_ui_manifest
from ior_mvp.rules import (
    _r3_rule,
    _r4d_rule,
    _r5_rule,
    _r11_rule,
    evaluate_simulated_rules,
    r1d_fires,
    r2_fires,
    r3_fires,
    r11_generic_capacity_fires,
)
from ior_mvp.trade_metrics import compound_annual_growth
from tests.legacy_snapshot_v1 import candidate_v2_from_legacy


@pytest.mark.parametrize(
    ("positive_years", "expected"),
    [
        ([2022, 2023], False),
        ([2021, 2022, 2023], True),
        ([2020, 2021, 2022, 2023], True),
    ],
)
def test_r1d_positive_year_count_boundary(
    positive_years: list[int],
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R1_D"]
    assert r1d_fires(positive_years, config) is expected


@pytest.mark.parametrize(
    ("positive_years", "expected"),
    [
        ([2020, 2021, 2022], True),
        ([2020, 2021, 2023], True),
        ([2020, 2021, 2024], False),
    ],
)
def test_r1d_window_span_boundary(
    positive_years: list[int],
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R1_D"]
    assert r1d_fires(positive_years, config) is expected


@pytest.mark.parametrize(
    ("share", "expected"),
    [
        (0.5999, False),
        (0.6000, True),
        (0.6001, True),
    ],
)
def test_r2_quantity_contribution_share_boundary(
    share: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=0.01,
            contribution_share=share,
            quantity_growth=0.05,
            rule_config=config,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("growth", "expected"),
    [
        (0.0499, False),
        (0.0500, True),
        (0.0501, True),
    ],
)
def test_r2_quantity_growth_boundary(
    growth: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=0.01,
            contribution_share=0.60,
            quantity_growth=growth,
            rule_config=config,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("latest", "expected"),
    [
        (104.99, False),
        (105.00, True),
        (105.01, True),
    ],
)
def test_r2_cagr_boundary_uses_full_precision(
    latest: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    cagr = compound_annual_growth(latest, 100.0, 1)
    assert (
        r2_fires(
            delta_ln_quantity=0.01,
            contribution_share=0.60,
            quantity_growth=cagr,
            rule_config=config,
        )
        is expected
    )


def test_r2_two_year_span_100_to_110_25_is_exactly_five_percent() -> None:
    config = thresholds_config()["rules"]["R2"]
    cagr = compound_annual_growth(110.25, 100.0, 2)

    assert cagr == pytest.approx(0.05)
    assert r2_fires(0.01, 0.60, cagr, config) is True


@pytest.mark.parametrize("delta_ln_quantity", [-0.0001, 0.0])
def test_r2_requires_strictly_positive_quantity_change(
    delta_ln_quantity: float,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=delta_ln_quantity,
            contribution_share=0.60,
            quantity_growth=0.05,
            rule_config=config,
        )
        is False
    )


@pytest.mark.parametrize(
    ("hhi", "expected"),
    [
        (0.2499, False),
        (0.2500, True),
        (0.2501, True),
    ],
)
def test_r3_hhi_boundary(
    hhi: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(hhi, None, config) is expected


@pytest.mark.parametrize(
    ("largest_supplier_share", "expected"),
    [
        (0.4999, False),
        (0.5000, True),
        (0.5001, True),
    ],
)
def test_r3_largest_supplier_boundary(
    largest_supplier_share: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(None, largest_supplier_share, config) is expected


def test_r3_largest_supplier_missing_is_not_a_trigger() -> None:
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(0.2499, None, config) is False


@pytest.mark.parametrize("basis", ["value", "quantity"])
@pytest.mark.parametrize(
    ("hhi", "expected"),
    [
        (0.2499, False),
        (0.2500, True),
        (0.2501, True),
    ],
)
def test_r3_hhi_boundary_applies_to_each_basis(
    basis: str,
    hhi: float,
    expected: bool,
) -> None:
    del basis
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(hhi, None, config) is expected


@pytest.mark.parametrize("basis", ["value", "quantity"])
@pytest.mark.parametrize(
    ("share", "expected"),
    [
        (0.4999, False),
        (0.5000, True),
        (0.5001, True),
    ],
)
def test_r3_largest_share_boundary_applies_to_each_basis(
    basis: str,
    share: float,
    expected: bool,
) -> None:
    del basis
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(None, share, config) is expected


def test_r3_orchestrator_compares_unrounded_hhi_below_boundary() -> None:
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-721049")
    )
    case["trade"][-1]["imports_usd_m"] = 100.0
    shares = (0.3999, 0.150025, 0.150025, 0.150025, 0.150025)
    case["partner_observations"] = [
        {
            "year": 2024,
            "partner": f"P{index}",
            "flow": "imports",
            "trade_value_usd_m": share * 100,
            "net_weight_kt": "UNAVAILABLE",
            "quantity_unit": "UNAVAILABLE",
            "validity_flags": {
                "value_valid": True,
                "net_weight_valid": False,
                "quantity_comparable": False,
            },
            "gross_flow": True,
            "source_evidence_id": "S-WITS-721049",
        }
        for index, share in enumerate(shares, start=1)
    ]

    row = _r3_rule(case, thresholds_config()["rules"]["R3"])

    assert row["metrics"]["value"]["hhi"] == pytest.approx(0.25)
    assert row["fired"] is False


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (49.99, False),
        (50.00, False),
        (50.01, True),
    ],
)
def test_r11_export_import_value_ratio_boundary(
    ratio: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R11"]
    assert r11_generic_capacity_fires(True, ratio, config) is expected


@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        (0.6999, None),
        (0.7000, True),
        (0.7001, True),
    ],
)
def test_r4d_dedicated_value_coverage_boundary(
    coverage: float,
    expected: bool | None,
) -> None:
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-721049")
    )
    case["trade"][-1]["imports_usd_m"] = 100.0
    case["trade"][-1]["imports_kt"] = 50.0
    case["disclosed_dispersion"] = "UNAVAILABLE"
    case["partner_observations"] = [
        {
            "year": 2024,
            "partner": partner,
            "flow": "imports",
            "trade_value_usd_m": value,
            "net_weight_kt": quantity,
            "quantity_unit": "kt",
            "validity_flags": {
                "value_valid": True,
                "net_weight_valid": True,
                "quantity_comparable": True,
            },
            "gross_flow": True,
            "source_evidence_id": "S-WITS-721049",
        }
        for partner, value, quantity in (
            ("A", coverage * 70, 30.0),
            ("B", coverage * 30, 20.0),
        )
    ]

    row = _r4d_rule(
        case,
        thresholds_config()["rules"]["R4_D"],
    )

    assert row["fired"] is expected


@pytest.mark.parametrize(
    ("penetration", "expected"),
    [
        (0.1999, False),
        (0.2000, True),
        (0.2001, True),
    ],
)
def test_r5_penetration_boundary(
    penetration: float,
    expected: bool,
) -> None:
    retained = penetration * 100
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-721049")
    )
    case["trade"][-1]["imports_kt"] = retained
    case["domestic_flows"].update(
        {
            "domestic_production_kt": 100 - retained,
            "retained_imports_kt": retained,
            "domestic_origin_exports_kt": 0.0,
            "reexports_kt": 0.0,
        }
    )

    row = _r5_rule(case, thresholds_config()["rules"]["R5"])

    assert row["execution"] == "FULL"
    assert row["fired"] is expected


def test_r5_orchestrator_compares_unrounded_penetration_below_boundary(
) -> None:
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-721049")
    )
    retained = 19.996
    case["trade"][-1]["imports_kt"] = retained
    case["domestic_flows"].update(
        {
            "domestic_production_kt": 100 - retained,
            "retained_imports_kt": retained,
            "domestic_origin_exports_kt": 0.0,
            "reexports_kt": 0.0,
        }
    )

    row = _r5_rule(case, thresholds_config()["rules"]["R5"])

    assert row["metrics"][
        "retained_import_share_of_apparent_consumption"
    ] == pytest.approx(0.2)
    assert row["fired"] is False


@pytest.mark.parametrize(
    ("ratio", "has_nameplate", "expected"),
    [
        (49.99, True, False),
        (50.00, True, False),
        (50.01, True, True),
        (50.01, False, False),
    ],
)
def test_r11_ratio_and_nameplate_conjunction(
    ratio: float,
    has_nameplate: bool,
    expected: bool,
) -> None:
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-390210")
    )
    case["trade"][-1].pop("export_import_value_ratio", None)
    case["trade"][-1]["imports_usd_m"] = 1.0
    case["trade"][-1]["exports_usd_m"] = ratio
    if not has_nameplate:
        for producer in case["domestic_capability"][
            "producer_evidence"
        ]:
            producer["installed_capacity_tpy"] = "UNAVAILABLE"
            producer["nameplate_status"] = "unresolved"
            producer["nameplate_source_evidence_id"] = "UNAVAILABLE"

    row = _r11_rule(case, thresholds_config()["rules"]["R11"])

    assert row["fired"] is expected


def test_r11_orchestrator_compares_unrounded_ratio_above_boundary() -> None:
    case = candidate_v2_from_legacy(
        get_public_case("SAU-H0-390210")
    )
    case["trade"][-1].pop("export_import_value_ratio", None)
    case["trade"][-1]["imports_usd_m"] = 1.0
    case["trade"][-1]["exports_usd_m"] = 50.00001

    row = _r11_rule(case, thresholds_config()["rules"]["R11"])

    assert row["metrics"][
        "computed_export_import_value_ratio"
    ] == pytest.approx(50.0)
    assert row["fired"] is True


@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        (0.6999, False),
        (0.7000, True),
        (0.7001, True),
    ],
)
def test_publication_allowed_kmin_boundary(
    coverage: float,
    expected: bool,
) -> None:
    capability_config = thresholds_config()["capability"]
    assert (
        publication_allowed(
            d_star=0.1,
            known_weight_coverage=coverage,
            minimum_known_weight_coverage=float(
                capability_config["minimum_known_weight_coverage"]
            ),
            unresolved_hard_gates=[],
            has_known_state_three=False,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("states", "expected_coverage", "expected_publishable"),
    [
        (
            {
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
            },
            0.65,
            False,
        ),
        (
            {
                "feedstock_chemistry": 0,
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
            },
            0.70,
            True,
        ),
        (
            {
                "feedstock_chemistry": 0,
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
                "utilities_ehs_permitting": 0,
            },
            0.75,
            True,
        ),
    ],
)
def test_evaluate_capability_integrates_kmin_with_profile_weights(
    states: dict[str, int],
    expected_coverage: float,
    expected_publishable: bool,
) -> None:
    result = evaluate_capability("coated_steel", states, [])
    assert result["known_weight_coverage"] == pytest.approx(expected_coverage)
    assert result["route_publishable"] is expected_publishable


@pytest.mark.parametrize(
    ("distance", "expected_code"),
    [
        (0.1999, "immediate_adjacency"),
        (0.2000, "immediate_adjacency"),
        (0.2001, "incremental_upgrade"),
        (0.3999, "incremental_upgrade"),
        (0.4000, "incremental_upgrade"),
        (0.4001, "major_line_or_jv"),
        (0.6499, "major_line_or_jv"),
        (0.6500, "major_line_or_jv"),
        (0.6501, "greenfield_likely"),
    ],
)
def test_dstar_route_band_boundaries(
    distance: float,
    expected_code: str,
) -> None:
    bands = thresholds_config()["capability"]["route_bands"]
    assert route_band(distance, bands)["code"] == expected_code


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (1.2499, False),
        (1.2500, False),
        (1.2501, True),
    ],
)
def test_competition_warning_boundary(
    ratio: float,
    expected: bool,
) -> None:
    config = thresholds_config()["competition"]
    assert competition_warning(ratio, config) is expected


def test_r3_metrics_expose_configured_thresholds() -> None:
    result = analyze("SAU-H0-721049", "public")
    r3 = next(row for row in result["rules"] if row["rule_id"] == "R3")
    config = thresholds_config()["rules"]["R3"]
    assert r3["metrics"]["hhi_threshold"] == config["supplier_hhi"]
    assert r3["metrics"]["largest_supplier_threshold"] == (
        config["largest_supplier_share"]
    )
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"


def test_r11_metrics_expose_configured_threshold() -> None:
    result = analyze("SAU-H0-390210", "public")
    r11 = next(row for row in result["rules"] if row["rule_id"] == "R11")
    config = thresholds_config()["rules"]["R11"]
    assert r11["metrics"]["export_import_value_ratio_threshold"] == (
        config["generic_capacity_export_import_value_ratio"]
    )


def test_competition_payload_exposes_configured_warning() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    config = thresholds_config()["competition"]
    assert result["competition"]["warning_threshold"] == (
        config["post_entry_capacity_to_downside_demand_warning"]
    )
    assert result["competition"]["warning_fires"] is False
    assert result["competition"]["passes_default_warning"] is True


def test_metric_grid_receives_r3_threshold_metrics() -> None:
    analysis = analyze("SAU-H0-721049", "public")
    manifest = build_ui_manifest(analysis)
    metric_grid = next(
        component
        for component in manifest["components"]
        if component["type"] == "metric_grid"
    )
    r3 = next(row for row in analysis["rules"] if row["rule_id"] == "R3")
    assert metric_grid["props"]["supplier_concentration"] == r3["metrics"]


def test_pp_metric_grid_receives_empty_supplier_concentration() -> None:
    analysis = analyze("SAU-H0-390210", "public")
    r3 = next(
        row
        for row in analysis["rules"]
        if row["rule_id"] == "R3"
    )
    manifest = build_ui_manifest(analysis)
    metric_grid = next(
        component
        for component in manifest["components"]
        if component["type"] == "metric_grid"
    )

    assert r3["execution"] == "DISABLED"
    assert r3["metrics"]["value"]["status"] == "NOT_CALCULABLE"
    assert r3["metrics"]["quantity"]["status"] == "NOT_CALCULABLE"
    assert metric_grid["props"]["supplier_concentration"] == r3["metrics"]
    assert metric_grid["props"]["supplier_metrics"] is None


def _synthetic_rule(
    scenario: dict,
    capacity: dict,
    rule_id: str,
) -> dict:
    rows = evaluate_simulated_rules(
        scenario,
        get_public_case(scenario["opportunity_id"]),
        capacity,
        thresholds_config(),
    )
    return next(row for row in rows if row["rule_id"] == rule_id)


@pytest.mark.parametrize(
    ("utilisation", "expected"),
    [
        (0.8499, False),
        (0.8500, True),
        (0.8501, True),
    ],
)
def test_r6_effective_utilisation_boundary(
    utilisation: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-721049")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = utilisation
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 110.0

    row = _synthetic_rule(
        scenario,
        {
            "effective_qualified_capacity_kt": 100.0,
            "target_spec_demand_kt": 110.0,
        },
        "R6",
    )

    assert row["fired"] is expected


@pytest.mark.parametrize(
    ("target_demand", "expected"),
    [
        (109.99, False),
        (110.00, True),
        (110.01, True),
    ],
)
def test_r6_specification_shortage_boundary(
    target_demand: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-721049")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = 0.85
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = target_demand

    row = _synthetic_rule(
        scenario,
        {
            "effective_qualified_capacity_kt": 100.0,
            "target_spec_demand_kt": target_demand,
        },
        "R6",
    )

    assert row["fired"] is expected


@pytest.mark.parametrize(
    ("utilisation", "expected"),
    [
        (0.6999, True),
        (0.7000, True),
        (0.7001, False),
    ],
)
def test_r7_effective_utilisation_boundary(
    utilisation: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-390210")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = utilisation

    row = _synthetic_rule(
        scenario,
        {
            "formula_capacity_kt": 104.49,
            "qualified_available_kt": 80.0,
            "target_spec_demand_kt": 56.0,
        },
        "R7",
    )

    assert row["execution"] == "FULL"
    assert row["fired"] is expected
