from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.trade_metrics import (
    build_supplier_metrics,
    compound_annual_growth,
    concentration_metrics,
    degraded_dispersion_metrics,
    domestic_flow_metrics,
    established_domestic_nameplate,
    export_import_value_ratio,
    latest_usable_trade_pair,
)
from tests.legacy_snapshot_v1 import (
    LIVE_PUBLIC_ROOT,
    candidate_v2_from_legacy,
    load_legacy_snapshot,
)


def test_compound_annual_growth_handles_one_and_two_year_spans() -> None:
    assert compound_annual_growth(105.0, 100.0, 1) == pytest.approx(
        0.05
    )
    assert compound_annual_growth(110.25, 100.0, 2) == pytest.approx(
        0.05
    )


@pytest.mark.parametrize(
    ("latest", "previous", "years"),
    [
        (0.0, 100.0, 1),
        (100.0, 0.0, 1),
        (100.0, 100.0, 0),
        (100.0, 100.0, -1),
    ],
)
def test_compound_annual_growth_rejects_nonpositive_inputs(
    latest: float,
    previous: float,
    years: int,
) -> None:
    with pytest.raises(ValueError):
        compound_annual_growth(latest, previous, years)


def test_latest_usable_pair_uses_latest_observations_without_interpolation(
) -> None:
    trade = [
        {"year": 2021, "imports_usd_m": 90.0, "imports_kt": 100.0},
        {"year": 2023, "imports_usd_m": 95.0, "imports_kt": 105.0},
        {"year": 2024, "imports_usd_m": 100.0, "imports_kt": 110.0},
    ]

    pair = latest_usable_trade_pair(trade)

    assert pair is not None
    assert [row["year"] for row in pair] == [2023, 2024]


def test_latest_usable_pair_skips_invalid_rows_and_can_span_missing_year(
) -> None:
    trade = [
        {"year": 2021, "imports_usd_m": 90.0, "imports_kt": 100.0},
        {"year": 2023, "imports_usd_m": 95.0, "imports_kt": 105.0},
        {
            "year": 2024,
            "imports_usd_m": "UNAVAILABLE",
            "imports_kt": 110.0,
        },
    ]

    pair = latest_usable_trade_pair(trade)

    assert pair is not None
    assert [row["year"] for row in pair] == [2021, 2023]


def _row_case() -> dict:
    return {
        "trade": [
            {
                "year": 2024,
                "imports_usd_m": 100.0,
                "imports_kt": 100.0,
                "exports_usd_m": 1.0,
                "exports_kt": 1.0,
            }
        ],
        "trade_quality": {"flow_basis": "gross"},
        "partner_observations": [
            {
                "year": 2024,
                "partner": "Alpha",
                "flow": "imports",
                "trade_value_usd_m": 60.0,
                "net_weight_kt": 25.0,
                "quantity_unit": "kt",
                "validity_flags": {
                    "value_valid": True,
                    "net_weight_valid": True,
                    "quantity_comparable": True,
                },
                "gross_flow": True,
                "source_evidence_id": "E1",
            },
            {
                "year": 2024,
                "partner": "Beta",
                "flow": "imports",
                "trade_value_usd_m": 40.0,
                "net_weight_kt": 75.0,
                "quantity_unit": "kt",
                "validity_flags": {
                    "value_valid": True,
                    "net_weight_valid": True,
                    "quantity_comparable": True,
                },
                "gross_flow": True,
                "source_evidence_id": "E1",
            },
        ],
        "disclosed_concentration": {
            "value": {
                "year": 2024,
                "flow": "imports",
                "flow_basis": "gross",
                "basis": "value",
                "hhi": 0.36,
                "largest_supplier_share": "UNAVAILABLE",
                "top_two_share": 0.763,
                "top_two_suppliers": ["Other A", "Other B"],
                "source_evidence_id": "E1",
                "status": "calculated",
            },
            "quantity": "UNAVAILABLE",
        },
    }


def test_concentration_computes_value_and_quantity_separately() -> None:
    case = _row_case()

    value = concentration_metrics(case, "value")
    quantity = concentration_metrics(case, "quantity")

    assert value == {
        "basis": "value",
        "status": "FULL",
        "year": 2024,
        "flow_basis": "gross",
        "source": "partner_observations",
        "hhi": 0.52,
        "largest_supplier_share": 0.6,
        "top_two_share": 1.0,
        "valid_coverage": 1.0,
        "eligible_partner_count": 2,
        "reason": None,
    }
    assert quantity == {
        "basis": "quantity",
        "status": "FULL",
        "year": 2024,
        "flow_basis": "gross",
        "source": "partner_observations",
        "hhi": 0.625,
        "largest_supplier_share": 0.75,
        "top_two_share": 1.0,
        "valid_coverage": 1.0,
        "eligible_partner_count": 2,
        "reason": None,
    }


def test_incomplete_partner_basis_is_not_calculable_and_does_not_fallback(
) -> None:
    case = _row_case()
    case["partner_observations"][1]["trade_value_usd_m"] = 30.0

    result = concentration_metrics(case, "value")

    assert result["status"] == "NOT_CALCULABLE"
    assert result["valid_coverage"] == pytest.approx(0.9)
    assert result["source"] == "partner_observations"
    assert "reconcile" in result["reason"]
    assert result["hhi"] == "NOT_CALCULABLE"


def test_disclosed_concentration_is_full_only_when_rows_are_unavailable(
) -> None:
    legacy = load_legacy_snapshot(
        LIVE_PUBLIC_ROOT / "SAU-H0-721049.json"
    )
    case = candidate_v2_from_legacy(legacy)

    value = concentration_metrics(case, "value")
    quantity = concentration_metrics(case, "quantity")

    assert value["status"] == "FULL"
    assert value["source"] == "disclosed_concentration"
    assert value["hhi"] == pytest.approx(0.36)
    assert value["largest_supplier_share"] == "NOT_CALCULABLE"
    assert value["top_two_share"] == pytest.approx(0.763)
    assert quantity["status"] == "NOT_CALCULABLE"
    assert quantity["source"] == "none"


def test_disclosed_concentration_preserves_source_precision() -> None:
    legacy = load_legacy_snapshot(
        (
            LIVE_PUBLIC_ROOT
            / "historical"
            / "v1"
            / "SAU-H0-721049.json"
        )
    )
    case = candidate_v2_from_legacy(legacy)
    case["disclosed_concentration"]["value"]["hhi"] = 0.24995

    result = concentration_metrics(case, "value")

    assert result["hhi"] == 0.24995


def test_partner_rows_take_precedence_over_disclosed_aggregate() -> None:
    case = deepcopy(_row_case())

    result = concentration_metrics(case, "value")

    assert result["source"] == "partner_observations"
    assert result["hhi"] == pytest.approx(0.52)


def _dispersion_case() -> dict:
    observations = (
        ("A", 40.0, 40.0),
        ("B", 30.0, 30.0),
        ("C", 40.0, 20.0),
        ("D", 50.0, 10.0),
    )
    return {
        "trade": [
            {
                "year": 2024,
                "imports_usd_m": 160.0,
                "imports_kt": 100.0,
                "exports_usd_m": 1.0,
                "exports_kt": 1.0,
            }
        ],
        "trade_quality": {"flow_basis": "gross"},
        "partner_observations": [
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
                "source_evidence_id": "E1",
            }
            for partner, value, quantity in observations
        ],
        "disclosed_dispersion": "UNAVAILABLE",
    }


def test_degraded_dispersion_uses_quantity_weighted_quartiles_and_candidate(
) -> None:
    result = degraded_dispersion_metrics(
        _dispersion_case(),
        minimum_valid_value_coverage=0.70,
    )

    assert result["status"] == "CALCULABLE"
    assert result["calculation_basis"] == "partner_observations"
    assert result["valid_value_coverage"] == pytest.approx(1.0)
    assert result["valid_quantity_coverage"] == pytest.approx(1.0)
    assert result["weighted_q1_usd_t"] == pytest.approx(1000.0)
    assert result["weighted_median_usd_t"] == pytest.approx(1000.0)
    assert result["weighted_q3_usd_t"] == pytest.approx(2000.0)
    assert result["iqr_usd_t"] == pytest.approx(1000.0)
    assert result["outlier_candidate"] == {
        "partner": "D",
        "unit_value_usd_t": 5000.0,
        "quantity_share": 0.1,
        "confirmed_outlier": False,
    }


@pytest.mark.parametrize(
    ("coverage", "expected_status"),
    [
        (0.6999, "NOT_CALCULABLE"),
        (0.7000, "CALCULABLE"),
        (0.7001, "CALCULABLE"),
    ],
)
def test_degraded_dispersion_value_coverage_boundary(
    coverage: float,
    expected_status: str,
) -> None:
    case = _dispersion_case()
    case["trade"][0]["imports_usd_m"] = 100.0
    case["partner_observations"] = [
        {
            **deepcopy(case["partner_observations"][0]),
            "trade_value_usd_m": coverage * 70,
            "net_weight_kt": 30.0,
        },
        {
            **deepcopy(case["partner_observations"][1]),
            "trade_value_usd_m": coverage * 30,
            "net_weight_kt": 20.0,
        },
    ]

    result = degraded_dispersion_metrics(
        case,
        minimum_valid_value_coverage=0.70,
    )

    assert result["status"] == expected_status
    assert result["valid_value_coverage"] == pytest.approx(
        round(coverage, 4)
    )


def test_degraded_dispersion_falls_back_to_source_disclosure() -> None:
    case = candidate_v2_from_legacy(
        load_legacy_snapshot(
            LIVE_PUBLIC_ROOT / "SAU-H0-721049.json"
        )
    )

    result = degraded_dispersion_metrics(
        case,
        minimum_valid_value_coverage=0.70,
    )

    assert result["status"] == "DISCLOSED"
    assert result["calculation_basis"] == "disclosed_dispersion"
    assert result["bulk_band_usd_t"] == [776, 864]
    assert result["outlier_candidate"]["partner"] == "Austria"
    assert result["outlier_candidate"]["confirmed_outlier"] is False


def test_domestic_flows_compute_all_four_methodology_measures() -> None:
    result = domestic_flow_metrics(
        {"year": 2024, "imports_kt": 100.0},
        {
            "period_year": 2024,
            "domestic_production_kt": 50.0,
            "retained_imports_kt": "UNAVAILABLE",
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": 20.0,
            "source_evidence_ids": ["E1"],
        },
    )

    assert result["retained_imports_kt"] == pytest.approx(80.0)
    assert result["net_import_exposure_kt"] == pytest.approx(70.0)
    assert result["apparent_consumption_kt"] == pytest.approx(120.0)
    assert result[
        "retained_import_share_of_apparent_consumption"
    ] == pytest.approx(0.6667)
    assert result["calculation_basis"] == "computed_from_reexports"
    assert result["unavailable_inputs"] == ["retained_imports_kt"]


def test_domestic_flows_use_verified_direct_retained_imports() -> None:
    result = domestic_flow_metrics(
        {"year": 2024, "imports_kt": 100.0},
        {
            "period_year": 2024,
            "domestic_production_kt": 50.0,
            "retained_imports_kt": 80.0,
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": "UNAVAILABLE",
            "source_evidence_ids": ["E1"],
        },
    )

    assert result["retained_imports_kt"] == pytest.approx(80.0)
    assert result["calculation_basis"] == (
        "reported_verified_retained_imports"
    )


@pytest.mark.parametrize(
    "flows",
    [
        {
            "period_year": 2024,
            "domestic_production_kt": 50.0,
            "retained_imports_kt": 79.0,
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": 20.0,
            "source_evidence_ids": [],
        },
        {
            "period_year": 2024,
            "domestic_production_kt": 50.0,
            "retained_imports_kt": "UNAVAILABLE",
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": 101.0,
            "source_evidence_ids": [],
        },
    ],
)
def test_domestic_flows_reject_contradictory_physical_arithmetic(
    flows: dict,
) -> None:
    with pytest.raises(ValueError, match="reexports|retained"):
        domestic_flow_metrics(
            {"year": 2024, "imports_kt": 100.0},
            flows,
        )


def test_domestic_flows_name_every_unknown_without_coercing_zero() -> None:
    result = domestic_flow_metrics(
        {"year": 2024, "imports_kt": 100.0},
        {
            "period_year": 2024,
            "domestic_production_kt": "UNAVAILABLE",
            "retained_imports_kt": "UNAVAILABLE",
            "domestic_origin_exports_kt": "UNAVAILABLE",
            "reexports_kt": "UNAVAILABLE",
            "source_evidence_ids": [],
        },
    )

    assert result["retained_imports_kt"] == "NOT_CALCULABLE"
    assert result["net_import_exposure_kt"] == "NOT_CALCULABLE"
    assert result["apparent_consumption_kt"] == "NOT_CALCULABLE"
    assert result[
        "retained_import_share_of_apparent_consumption"
    ] == "NOT_CALCULABLE"
    assert result["unavailable_inputs"] == [
        "domestic_origin_exports_kt",
        "domestic_production_kt",
        "reexports_kt",
        "retained_imports_kt",
    ]
    assert "reexports_kt" in result["unavailable_reasons"][
        "retained_imports_kt"
    ]


def test_nonpositive_apparent_consumption_disables_penetration() -> None:
    result = domestic_flow_metrics(
        {"year": 2024, "imports_kt": 10.0},
        {
            "period_year": 2024,
            "domestic_production_kt": 0.0,
            "retained_imports_kt": 10.0,
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": "UNAVAILABLE",
            "source_evidence_ids": [],
        },
    )

    assert result["apparent_consumption_kt"] == pytest.approx(0.0)
    assert result[
        "retained_import_share_of_apparent_consumption"
    ] == "NOT_CALCULABLE"
    assert "positive apparent_consumption_kt" in result[
        "unavailable_reasons"
    ]["retained_import_share_of_apparent_consumption"]


def test_export_import_ratio_is_computed_and_disclosure_is_separate() -> None:
    steel = export_import_value_ratio(
        {
            "imports_usd_m": 236.9,
            "exports_usd_m": 27.1,
        }
    )
    polypropylene = export_import_value_ratio(
        {
            "imports_usd_m": 92.3,
            "exports_usd_m": 4670.5,
            "export_import_value_ratio": 50.6,
        }
    )

    assert steel == {
        "status": "CALCULABLE",
        "computed_export_import_value_ratio": 0.1144,
        "disclosed_export_import_value_ratio": None,
        "disclosed_ratio_consistent": None,
        "export_import_value_ratio": 0.1144,
        "ratio_basis": "gross_trade_value",
        "reason": None,
    }
    assert polypropylene == {
        "status": "CALCULABLE",
        "computed_export_import_value_ratio": 50.6013,
        "disclosed_export_import_value_ratio": 50.6,
        "disclosed_ratio_consistent": True,
        "export_import_value_ratio": 50.6,
        "ratio_basis": "gross_trade_value",
        "reason": None,
    }


def test_export_import_ratio_missing_input_remains_not_calculable() -> None:
    result = export_import_value_ratio(
        {
            "imports_usd_m": 100.0,
            "exports_usd_m": "UNAVAILABLE",
        }
    )

    assert result["status"] == "NOT_CALCULABLE"
    assert result["computed_export_import_value_ratio"] is None
    assert result["export_import_value_ratio"] is None
    assert "exports_usd_m" in result["reason"]


def test_established_nameplate_requires_observed_positive_abc_evidence(
) -> None:
    case = candidate_v2_from_legacy(
        load_legacy_snapshot(
            LIVE_PUBLIC_ROOT / "SAU-H0-390210.json"
        )
    )
    result = established_domestic_nameplate(
        case["domestic_capability"]
    )

    assert result["established"] is True
    assert result["total_observed_nameplate_tpy"] == pytest.approx(
        1_170_000
    )
    assert result["producers"] == [
        "Advanced Petrochemical",
        "Tasnee",
    ]

    case["domestic_capability"]["verified_present"] = False
    assert established_domestic_nameplate(
        case["domestic_capability"]
    )["established"] is False


def test_supplier_compatibility_projection_preserves_steel_hhi() -> None:
    case = candidate_v2_from_legacy(
        load_legacy_snapshot(
            LIVE_PUBLIC_ROOT / "SAU-H0-721049.json"
        )
    )
    r3 = {
        "value": concentration_metrics(case, "value"),
        "quantity": concentration_metrics(case, "quantity"),
    }
    r4d = degraded_dispersion_metrics(case, 0.70)

    projection = build_supplier_metrics(case, r3, r4d)

    assert projection == {
        "partner_value_hhi": 0.36,
        "largest_supplier_share": "NOT_CALCULABLE",
        "top_two_value_share": 0.763,
        "partner_quantity_hhi": "NOT_CALCULABLE",
        "largest_supplier_quantity_share": "NOT_CALCULABLE",
        "bulk_uv_range_usd_t": [776, 864],
        "small_high_uv_observation": {
            "partner": "Austria",
            "quantity_kt": 1.0,
            "uv_usd_t": 4179,
        },
    }


def test_supplier_compatibility_projection_is_null_without_concentration(
) -> None:
    case = candidate_v2_from_legacy(
        load_legacy_snapshot(
            LIVE_PUBLIC_ROOT / "SAU-H0-390210.json"
        )
    )
    r3 = {
        "value": concentration_metrics(case, "value"),
        "quantity": concentration_metrics(case, "quantity"),
    }
    r4d = degraded_dispersion_metrics(case, 0.70)

    assert build_supplier_metrics(case, r3, r4d) is None
