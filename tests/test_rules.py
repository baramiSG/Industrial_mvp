from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.config import thresholds_config
from ior_mvp.data_repository import get_public_case
from ior_mvp.rules import evaluate_rules, log_change, quantity_contribution_share


def by_id(rules: list[dict], rule_id: str) -> dict:
    return next(row for row in rules if row["rule_id"] == rule_id)


def test_log_decomposition_steel_matches_worked_case() -> None:
    case = get_public_case("SAU-H0-721049")
    rules = evaluate_rules(case)
    r2 = by_id(rules, "R2")

    assert r2["fired"] is True
    assert r2["metrics"]["delta_ln_value"] == pytest.approx(0.2419, abs=1e-4)
    assert r2["metrics"]["delta_ln_quantity"] == pytest.approx(0.5047, abs=2e-4)
    assert r2["metrics"]["delta_ln_unit_value"] == pytest.approx(-0.2625, abs=2e-4)
    assert r2["metrics"]["quantity_contribution_share"] == pytest.approx(0.6579, abs=1e-3)


def test_pp_quantity_led_rule_does_not_fire() -> None:
    rules = evaluate_rules(get_public_case("SAU-H0-390210"))
    r2 = by_id(rules, "R2")
    assert r2["execution"] == "FULL"
    assert r2["fired"] is False


def test_pp_generic_capacity_warning_fires() -> None:
    rules = evaluate_rules(get_public_case("SAU-H0-390210"))
    r11 = by_id(rules, "R11")
    config = thresholds_config()["rules"]["R11"]
    assert r11["fired"] is True
    assert r11["metrics"]["export_import_value_ratio"] == pytest.approx(
        50.6
    )
    assert r11["metrics"]["export_import_value_ratio_threshold"] == (
        config["generic_capacity_export_import_value_ratio"]
    )


def test_r11_missing_ratio_is_degraded_and_does_not_fire() -> None:
    r11 = by_id(
        evaluate_rules(get_public_case("SAU-H0-721049")),
        "R11",
    )
    assert r11["execution"] == "DEGRADED"
    assert r11["fired"] is False
    assert r11["metrics"]["export_import_value_ratio"] is None


def test_r3_hhi_path_fires_when_largest_supplier_is_not_calculable() -> None:
    r3 = by_id(
        evaluate_rules(get_public_case("SAU-H0-721049")),
        "R3",
    )
    assert r3["fired"] is True
    assert r3["metrics"]["hhi"] == pytest.approx(0.36)
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"
    assert r3["metrics"]["top_two_share"] == pytest.approx(0.763)


def test_r3_does_not_substitute_top_two_share_for_largest_supplier() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    supplier = case["supplier_metrics_2024"]
    supplier["partner_value_hhi"] = 0.2499
    supplier["top_two_value_share"] = 0.9999
    supplier.pop("largest_supplier_share", None)

    r3 = by_id(evaluate_rules(case), "R3")

    assert r3["fired"] is False
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"


def test_r3_largest_supplier_path_uses_largest_supplier_metric() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    supplier = case["supplier_metrics_2024"]
    supplier["partner_value_hhi"] = 0.2499
    supplier["largest_supplier_share"] = 0.5000

    r3 = by_id(evaluate_rules(case), "R3")

    assert r3["fired"] is True
    assert r3["metrics"]["largest_supplier_share"] == pytest.approx(0.50)


def test_r4_full_rule_is_explicitly_disabled_on_annual_snapshots() -> None:
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        r4f = by_id(evaluate_rules(get_public_case(opportunity_id)), "R4-F")
        assert r4f["execution"] == "DISABLED"
        assert r4f["fired"] is None
        assert "Partner-month" in r4f["result"]


def test_degraded_uv_never_claims_grade() -> None:
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        r4d = by_id(evaluate_rules(get_public_case(opportunity_id)), "R4-D")
        text = f"{r4d['result']} {r4d['decision_effect']}".lower()
        assert "no grade conclusion" in text or "specification research" in text
        assert "confirmed grade" not in text


def test_threshold_is_loaded_from_versioned_config() -> None:
    config = thresholds_config()
    assert config["metadata"]["version"] == "1.1.0"
    assert config["metadata"]["effective_date"] == "2026-09-02"
    assert config["rules"]["R2"][
        "minimum_quantity_contribution_share"
    ] == pytest.approx(0.60)
    assert config["rules"]["R11"][
        "generic_capacity_export_import_value_ratio"
    ] == 50
    assert config["metadata"]["status"] == "frozen_for_demo_cycle"


def test_quantity_contribution_zero_denominator() -> None:
    assert quantity_contribution_share(0, 0) == 0


def test_log_change_rejects_non_positive() -> None:
    with pytest.raises(ValueError):
        log_change(0, 1)
