from __future__ import annotations

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
    assert r11["fired"] is True
    assert r11["metrics"]["export_import_value_ratio"] == pytest.approx(50.6)


def test_degraded_uv_never_claims_grade() -> None:
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        r4d = by_id(evaluate_rules(get_public_case(opportunity_id)), "R4-D")
        text = f"{r4d['result']} {r4d['decision_effect']}".lower()
        assert "no grade conclusion" in text or "specification research" in text
        assert "confirmed grade" not in text


def test_threshold_is_loaded_from_versioned_config() -> None:
    config = thresholds_config()
    assert config["metadata"]["version"] == "1.0.0"
    assert config["rules"]["R2"]["minimum_quantity_contribution_share"] == pytest.approx(0.60)
    assert config["metadata"]["status"] == "frozen_for_demo_cycle"


def test_quantity_contribution_zero_denominator() -> None:
    assert quantity_contribution_share(0, 0) == 0


def test_log_change_rejects_non_positive() -> None:
    with pytest.raises(ValueError):
        log_change(0, 1)
