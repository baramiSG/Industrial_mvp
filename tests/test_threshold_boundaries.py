from __future__ import annotations

import pytest

from ior_mvp.capability import (
    evaluate_capability,
    publication_allowed,
    route_band,
)
from ior_mvp.config import thresholds_config
from ior_mvp.decision_engine import analyze, competition_warning
from ior_mvp.genui import build_ui_manifest
from ior_mvp.rules import (
    r1d_fires,
    r2_fires,
    r3_fires,
    r11_generic_capacity_fires,
)


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
