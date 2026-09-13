from __future__ import annotations

import ast
import re
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import thresholds_config
from ior_mvp.data_repository import get_public_case
from ior_mvp.rules import (
    _evaluate_rules_v2,
    _r1d_rule,
    _r2_rule,
    _r3_rule,
    _r4d_rule,
    _r5_rule,
    _r9s_rule,
    _r10_rule,
    _r11_rule,
    evaluate_rules,
    log_change,
    quantity_contribution_share,
)
from tests.legacy_snapshot_v1 import candidate_v21_from_legacy


def by_id(rules: list[dict], rule_id: str) -> dict:
    return next(row for row in rules if row["rule_id"] == rule_id)


def test_every_rule_row_carries_typed_result_and_effect_codes() -> None:
    from ior_mvp.decision_engine import analyze

    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        for mode in ("public", "simulated"):
            for row in analyze(opportunity_id, mode)["rules"]:
                assert re.fullmatch(
                    r"^[A-Z][A-Z0-9_]+$",
                    row["result_code"],
                )
                assert re.fullmatch(
                    r"^[A-Z][A-Z0-9_]+$",
                    row["decision_effect_code"],
                )
                assert isinstance(row["result_values"], dict)
                assert isinstance(row["effect_values"], dict)
                assert all(
                    isinstance(key, str) and isinstance(value, str)
                    for values in (row["result_values"], row["effect_values"])
                    for key, value in values.items()
                )


def test_rule_builders_pass_codes_at_every_call_site() -> None:
    path = Path(__file__).resolve().parents[1] / "src" / "ior_mvp" / "rules.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"_rule", "_synthetic_rule"}
    ]

    assert calls
    for call in calls:
        keywords = {keyword.arg: keyword.value for keyword in call.keywords}
        for name in ("result_code", "decision_effect_code"):
            assert name in keywords
            assert isinstance(keywords[name], ast.Constant)
            assert isinstance(keywords[name].value, str)


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
    case = deepcopy(get_public_case("SAU-H0-721049"))
    case["trade"][-1]["exports_usd_m"] = "UNAVAILABLE"
    r11 = by_id(
        evaluate_rules(case),
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
    supplier = case["disclosed_concentration"]["value"]
    supplier["hhi"] = 0.2499
    supplier["top_two_share"] = 0.9999
    supplier["largest_supplier_share"] = "UNAVAILABLE"

    r3 = by_id(evaluate_rules(case), "R3")

    assert r3["fired"] is False
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"


def test_r3_largest_supplier_path_uses_largest_supplier_metric() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    supplier = case["disclosed_concentration"]["value"]
    supplier["hhi"] = 0.2499
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
    assert config["metadata"]["version"] == "1.2.0"
    assert config["metadata"]["effective_date"] == "2026-09-02"
    assert config["rules"]["R2"][
        "minimum_quantity_contribution_share"
    ] == pytest.approx(0.60)
    assert config["rules"]["R11"][
        "generic_capacity_export_import_value_ratio"
    ] == 50
    assert config["rules"]["R4_D"][
        "minimum_valid_value_coverage"
    ] == pytest.approx(0.70)
    assert config["metadata"]["status"] == "frozen_for_demo_cycle"


def test_quantity_contribution_zero_denominator() -> None:
    assert quantity_contribution_share(0, 0) == 0


def test_log_change_rejects_non_positive() -> None:
    with pytest.raises(ValueError):
        log_change(0, 1)


def test_r5_exposes_not_calculable_ratio_reason_and_threshold() -> None:
    threshold = thresholds_config()["rules"]["R5"][
        "retained_import_share_of_apparent_consumption"
    ]
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        r5 = by_id(
            evaluate_rules(get_public_case(opportunity_id)),
            "R5",
        )

        assert r5["metrics"][
            "retained_import_share_of_apparent_consumption"
        ] == "NOT_CALCULABLE"
        assert r5["metrics"]["reason"] == (
            "Domestic production quantity and retained-import "
            "flow are absent from the frozen public snapshot; "
            "gross imports cannot establish apparent consumption."
        )
        assert r5["metrics"]["threshold"] == threshold
        assert r5["metrics"]["retained_imports_kt"] == (
            "NOT_CALCULABLE"
        )
        assert set(r5["metrics"]["unavailable_inputs"]) == {
            "domestic_production_kt",
            "retained_imports_kt",
            "domestic_origin_exports_kt",
            "reexports_kt",
        }


def _v2_case(opportunity_id: str) -> dict:
    return candidate_v21_from_legacy(get_public_case(opportunity_id))


def test_v2_r1d_confidence_cap_is_projected_from_injected_config() -> None:
    config = deepcopy(thresholds_config()["rules"]["R1_D"])
    config["confidence_cap"] = "B"

    row = _r1d_rule(_v2_case("SAU-H0-721049"), config)

    assert row["metrics"]["confidence_cap"] == "B"
    assert row["decision_effect"].endswith("confidence capped at B.")


@pytest.mark.parametrize(
    ("opportunity_id", "expected"),
    [
        (
            "SAU-H0-721049",
            {
                "from_year": 2023,
                "to_year": 2024,
                "observed_span_years": 1,
                "delta_ln_value": 0.2419,
                "delta_ln_quantity": 0.5047,
                "delta_ln_unit_value": -0.2625,
                "quantity_contribution_share": 0.6579,
                "quantity_cagr": 0.6565,
            },
        ),
        (
            "SAU-H0-390210",
            {
                "from_year": 2023,
                "to_year": 2024,
                "observed_span_years": 1,
                "delta_ln_value": 0.0142,
                "delta_ln_quantity": -0.1793,
                "delta_ln_unit_value": 0.194,
                "quantity_contribution_share": 0.4804,
                "quantity_cagr": -0.1642,
            },
        ),
    ],
)
def test_v2_r2_uses_latest_observed_pair_and_cagr(
    opportunity_id: str,
    expected: dict,
) -> None:
    row = _r2_rule(
        _v2_case(opportunity_id),
        thresholds_config()["rules"]["R2"],
    )

    assert row["metrics"] == expected


def test_v2_r3_reports_both_bases_and_exact_golden_text() -> None:
    config = thresholds_config()["rules"]["R3"]
    steel = _r3_rule(_v2_case("SAU-H0-721049"), config)
    polypropylene = _r3_rule(_v2_case("SAU-H0-390210"), config)

    assert steel["execution"] == "FULL"
    assert steel["fired"] is True
    assert steel["result"] == (
        "External supply is concentrated on the value basis; "
        "quantity concentration is NOT_CALCULABLE."
    )
    assert steel["metrics"]["value"]["hhi"] == pytest.approx(0.36)
    assert steel["metrics"]["quantity"]["status"] == "NOT_CALCULABLE"
    assert polypropylene["execution"] == "DISABLED"
    assert polypropylene["fired"] is None
    assert polypropylene["result"] == (
        "Value- and quantity-basis partner concentration are "
        "NOT_CALCULABLE."
    )


def test_v2_r3_can_fire_from_quantity_basis_only() -> None:
    case = _v2_case("SAU-H0-721049")
    case["trade"][-1]["imports_usd_m"] = 100.0
    case["trade"][-1]["imports_kt"] = 100.0
    quantities = (60.0, 10.0, 10.0, 10.0, 10.0)
    case["partner_observations"] = [
        {
            "year": 2024,
            "partner": f"P{index}",
            "flow": "imports",
            "trade_value_usd_m": 20.0,
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
        for index, quantity in enumerate(quantities, start=1)
    ]

    row = _r3_rule(case, thresholds_config()["rules"]["R3"])

    assert row["metrics"]["value"]["hhi"] == pytest.approx(0.2)
    assert row["metrics"]["quantity"]["hhi"] == pytest.approx(0.4)
    assert row["fired"] is True


def test_v2_computed_golden_rule_states_are_evidence_derived() -> None:
    steel = {
        row["rule_id"]: row
        for row in _evaluate_rules_v2(_v2_case("SAU-H0-721049"))
    }
    polypropylene = {
        row["rule_id"]: row
        for row in _evaluate_rules_v2(_v2_case("SAU-H0-390210"))
    }

    assert list(steel) == [
        "R0",
        "R1-F",
        "R1-D",
        "R2",
        "R3",
        "R4-F",
        "R4-D",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9-S",
        "R10",
        "R11",
        "R12",
    ]
    assert (steel["R4-D"]["execution"], steel["R4-D"]["fired"]) == (
        "DEGRADED",
        True,
    )
    assert (steel["R5"]["execution"], steel["R5"]["fired"]) == (
        "DEGRADED",
        True,
    )
    assert (steel["R9-S"]["execution"], steel["R9-S"]["fired"]) == (
        "FULL",
        True,
    )
    assert (steel["R10"]["execution"], steel["R10"]["fired"]) == (
        "DEGRADED",
        True,
    )
    assert (steel["R11"]["execution"], steel["R11"]["fired"]) == (
        "FULL",
        False,
    )
    assert steel["R11"]["metrics"][
        "computed_export_import_value_ratio"
    ] == pytest.approx(0.1144)
    assert steel["R11"]["result"] == (
        "Gross exports are 0.1144× imports; the configured "
        "generic-capacity warning threshold is not met."
    )

    assert (
        polypropylene["R4-D"]["execution"],
        polypropylene["R4-D"]["fired"],
    ) == ("DEGRADED", True)
    assert (
        polypropylene["R5"]["execution"],
        polypropylene["R5"]["fired"],
    ) == ("DEGRADED", True)
    assert (
        polypropylene["R9-S"]["execution"],
        polypropylene["R9-S"]["fired"],
    ) == ("FULL", True)
    assert (
        polypropylene["R10"]["execution"],
        polypropylene["R10"]["fired"],
    ) == ("DISABLED", None)
    assert (
        polypropylene["R11"]["execution"],
        polypropylene["R11"]["fired"],
    ) == ("FULL", True)
    assert polypropylene["R11"]["metrics"][
        "computed_export_import_value_ratio"
    ] == pytest.approx(50.6013)
    assert polypropylene["R11"]["metrics"][
        "disclosed_export_import_value_ratio"
    ] == pytest.approx(50.6)
    assert polypropylene["R11"]["metrics"][
        "disclosed_ratio_consistent"
    ] is True


def test_r4d_row_and_disabled_result_texts_are_exact() -> None:
    case = _v2_case("SAU-H0-721049")
    case["trade"][-1]["imports_usd_m"] = 100.0
    case["trade"][-1]["imports_kt"] = 100.0
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
            ("A", 40.0, 50.0),
            ("B", 60.0, 50.0),
        )
    ]
    config = thresholds_config()["rules"]["R4_D"]

    row = _r4d_rule(case, config)
    assert row["result"] == (
        "Comparable annual partner unit values show descriptive "
        "dispersion; no cluster or grade conclusion."
    )

    case["partner_observations"][1]["trade_value_usd_m"] = 20.0
    disabled = _r4d_rule(case, config)
    assert disabled["execution"] == "DISABLED"
    assert disabled["fired"] is None
    assert disabled["result"] == (
        "Comparable annual partner coverage is insufficient; "
        "R4-D is not calculable."
    )


def _partner_detail_rule_case(
    state: str,
    reason: str | None,
) -> dict:
    case = _v2_case("SAU-H0-390210")
    case.pop("disclosed_concentration", None)
    case.pop("disclosed_dispersion", None)
    case["partner_observations"] = "UNAVAILABLE"
    case["partner_detail"] = {
        "state": state,
        "reason": reason,
    }
    return case


def test_r3_reports_partner_detail_missing_code_reason_value_and_disabled_execution(
) -> None:
    case = _partner_detail_rule_case(
        "PARTNER_DETAIL_MISSING",
        "COVERAGE_INDETERMINATE",
    )

    r3 = _r3_rule(case, thresholds_config()["rules"]["R3"])
    r4d = _r4d_rule(case, thresholds_config()["rules"]["R4_D"])

    assert (r3["execution"], r3["fired"]) == ("DISABLED", None)
    assert r3["result_code"] == "PARTNER_DETAIL_MISSING"
    assert r3["result_values"] == {
        "partner_detail_reason": "COVERAGE_INDETERMINATE"
    }
    assert r3["result"] == (
        "Partner detail MISSING (COVERAGE_INDETERMINATE): value- and "
        "quantity-basis partner concentration are NOT_CALCULABLE because "
        "no partner rows were parsed — missing evidence, not zero trade."
    )
    assert (r4d["execution"], r4d["fired"]) == ("DISABLED", None)
    assert r4d["result_code"] == "PARTNER_DETAIL_MISSING"
    assert r4d["result_values"] == {
        "partner_detail_reason": "COVERAGE_INDETERMINATE"
    }


def test_r3_and_r4d_report_partner_trade_observed_zero_codes_on_zero_doubles(
) -> None:
    case = _partner_detail_rule_case(
        "PARTNER_TRADE_OBSERVED_ZERO",
        None,
    )

    r3 = _r3_rule(case, thresholds_config()["rules"]["R3"])
    r4d = _r4d_rule(case, thresholds_config()["rules"]["R4_D"])

    assert (r3["execution"], r3["fired"]) == ("DISABLED", None)
    assert r3["result_code"] == "PARTNER_TRADE_OBSERVED_ZERO"
    assert r3["result_values"] == {}
    assert "Partner trade OBSERVED ZERO" in r3["result"]
    assert (r4d["execution"], r4d["fired"]) == ("DISABLED", None)
    assert r4d["result_code"] == "PARTNER_TRADE_OBSERVED_ZERO"
    assert r4d["result_values"] == {}
    assert "Partner trade OBSERVED ZERO" in r4d["result"]


def test_r3_r4d_codes_unchanged_for_frozen_2_1_0_cases_and_observed_state(
) -> None:
    config_r3 = thresholds_config()["rules"]["R3"]
    config_r4d = thresholds_config()["rules"]["R4_D"]
    steel = _v2_case("SAU-H0-721049")
    polypropylene = _v2_case("SAU-H0-390210")

    assert _r3_rule(steel, config_r3)["result_code"] == (
        "VALUE_CONCENTRATED_QUANTITY_NOT_CALCULABLE"
    )
    assert _r4d_rule(steel, config_r4d)["result_code"] == (
        "DISCLOSED_DISPERSION"
    )
    assert _r3_rule(polypropylene, config_r3)["result_code"] == (
        "BOTH_BASES_NOT_CALCULABLE"
    )
    assert _r4d_rule(polypropylene, config_r4d)["result_code"] == (
        "DISCLOSED_DISPERSION"
    )

    observed = _partner_detail_rule_case(
        "PARTNER_DETAIL_OBSERVED",
        None,
    )
    observed["partner_observations"] = [
        {
            "year": 2024,
            "partner": "Observed but incomplete",
            "flow": "imports",
            "trade_value_usd_m": 1.0,
            "net_weight_kt": 1.0,
            "quantity_unit": "kt",
            "validity_flags": {
                "value_valid": True,
                "net_weight_valid": True,
                "quantity_comparable": True,
            },
            "gross_flow": True,
            "source_evidence_id": "P-WITS-390210",
        }
    ]
    assert _r3_rule(observed, config_r3)["result_code"] == (
        "BOTH_BASES_NOT_CALCULABLE"
    )
    assert _r4d_rule(observed, config_r4d)["result_code"] == (
        "COVERAGE_INSUFFICIENT"
    )


def test_r5_full_path_applies_configured_penetration_threshold() -> None:
    case = _v2_case("SAU-H0-721049")
    case["trade"][-1]["imports_kt"] = 100.0
    case["domestic_flows"].update(
        {
            "domestic_production_kt": 50.0,
            "retained_imports_kt": 80.0,
            "domestic_origin_exports_kt": 10.0,
            "reexports_kt": 20.0,
        }
    )

    row = _r5_rule(case, thresholds_config()["rules"]["R5"])

    assert row["execution"] == "FULL"
    assert row["fired"] is True
    assert row["metrics"]["retained_imports_kt"] == pytest.approx(80.0)
    assert row["metrics"]["net_import_exposure_kt"] == pytest.approx(
        70.0
    )
    assert row["metrics"]["apparent_consumption_kt"] == pytest.approx(
        120.0
    )


def test_r9s_uses_typed_signals_and_known_failure_gate() -> None:
    case = _v2_case("SAU-H0-721049")
    capability = case["domestic_capability"]
    assert _r9s_rule(capability)["fired"] is True

    capability["unresolved_hard_gates"][0][
        "state"
    ] = "known_failure"
    assert _r9s_rule(capability)["fired"] is False

    capability["same_process_family"] = "UNAVAILABLE"
    disabled = _r9s_rule(capability)
    assert disabled["execution"] == "DISABLED"
    assert disabled["fired"] is None


def test_r10_requires_designation_or_computed_concentration() -> None:
    case = _v2_case("SAU-H0-390210")
    r3 = _r3_rule(case, thresholds_config()["rules"]["R3"])
    assert _r10_rule(case, r3)["execution"] == "DISABLED"

    case["criticality_designation"] = {
        "authority": "Responsible authority",
        "reference": "REF-1",
        "date": "2026-08-31",
        "evidence_id": "P-WITS-390210",
    }
    designated = _r10_rule(case, r3)
    assert designated["execution"] == "FULL"
    assert designated["fired"] is True
    assert designated["metrics"]["criticality_evidence_id"] == (
        "P-WITS-390210"
    )


def test_r11_missing_exports_is_degraded_and_does_not_fire() -> None:
    case = _v2_case("SAU-H0-721049")
    case["trade"][-1]["exports_usd_m"] = "UNAVAILABLE"

    row = _r11_rule(case, thresholds_config()["rules"]["R11"])

    assert row["execution"] == "DEGRADED"
    assert row["fired"] is False
    assert row["metrics"]["export_import_value_ratio"] is None
    assert row["result"] == (
        "Export/import ratio or established nameplate capability is "
        "NOT_CALCULABLE; no generic-capacity exclusion fires."
    )


def test_public_rule_engine_has_no_authored_context_or_product_dispatch() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "ior_mvp"
        / "rules.py"
    ).read_text(encoding="utf-8")

    assert "rule_context" not in source
    assert "SAU-H0-721049" not in source
    assert "SAU-H0-390210" not in source
    assert "public_decision_contract" not in source


@pytest.mark.parametrize(
    ("opportunity_id", "expected_keys"),
    [
        (
            "SAU-H0-721049",
            [
                "need.specification.line_production",
                "need.capacity.availability_allocation",
                "need.demand.importer_specification",
                "need.flows.reexport_origin_decomposition",
                "need.economics.route_delivered_cost",
            ],
        ),
        (
            "SAU-H0-390210",
            [
                "need.identity.tariff_line",
                "need.demand.importer_application_qualification",
                "need.specification.producer_grade_matrix",
                "need.capacity.availability_allocation",
                "need.economics.named_exception_delivered_cost",
            ],
        ),
    ],
)
def test_r12_uses_computed_predicate_selected_evidence_needs(
    opportunity_id: str,
    expected_keys: list[str],
) -> None:
    row = by_id(
        evaluate_rules(get_public_case(opportunity_id)),
        "R12",
    )

    assert row["execution"] == "DEGRADED"
    assert row["fired"] is True
    assert row["result"] == "5 named facts could change the route."
    assert [
        need["template_key"]
        for need in row["metrics"]["evidence_needs"]
    ] == expected_keys
    assert row["metrics"]["named_missing_facts"] == [
        need["text"]
        for need in row["metrics"]["evidence_needs"]
    ]
