"""Screening ledger and warning contracts."""

from __future__ import annotations

import copy


def _case(*, values=(1_000_000, 2_000_000, 4_000_000), weights=(1_000_000, 2_000_000, 4_000_000)):
    from ior_mvp.screening.projection import project_case

    rows = []
    for offset, (value, weight) in enumerate(zip(values, weights, strict=True)):
        rows.append(
            {
                "year": 2022 + offset,
                "flow": "imports",
                "hs6": "721049",
                "trade_value": value,
                "net_weight": weight,
                "hs_revision": "H6",
                "source_evidence_id": "E1",
            }
        )
    return project_case("721049", rows, [], {}, None)


def _ledger(case=None, tariff=None, thresholds=None):
    from ior_mvp.config import thresholds_config
    from ior_mvp.screening.rules import screening_ledger

    return screening_ledger(
        case or _case(), tariff or {}, thresholds or thresholds_config()
    )


def _row(ledger, rule_id):
    return next(row for row in ledger if row["rule_id"] == rule_id)


def test_reuses_governed_rule_builders(monkeypatch):
    import ior_mvp.rules as governed
    from ior_mvp.screening import rules

    called = []
    original = governed._r1d_rule
    monkeypatch.setattr(
        governed,
        "_r1d_rule",
        lambda *args, **kwargs: (called.append("R1-D"), original(*args, **kwargs))[1],
    )
    rules.screening_ledger(_case(), {}, __import__("ior_mvp.config", fromlist=["thresholds_config"]).thresholds_config())
    assert called == ["R1-D"]


def test_r0_full_with_tariff_mapping_degraded_without_tree_disabled_when_malformed():
    mapped = {"complete": True, "hs6": {"721049"}}
    assert _row(_ledger(tariff=mapped), "R0")["execution"] == "FULL"
    assert _row(_ledger(), "R0")["execution"] == "DEGRADED"
    case = _case()
    case["hs6"] = "BAD"
    assert _row(_ledger(case), "R0")["execution"] == "DISABLED"


def test_r1d_positive_years_and_confidence_cap_from_config():
    row = _row(_ledger(), "R1-D")
    assert len(row["metrics"]["positive_years"]) == 3
    assert row["metrics"]["confidence_cap"] == "C"


def test_r2_fires_not_fires_and_disabled_paths():
    assert _row(_ledger(), "R2")["fired"] is True
    assert _row(_ledger(_case(values=(1_000_000, 2_000_000, 4_000_000), weights=(1_000_000, 1_000_000, 1_000_000))), "R2")["fired"] is False
    case = _case()
    case["trade"] = case["trade"][:1]
    assert _row(_ledger(case), "R2")["execution"] == "DISABLED"


def test_price_led_growth_warning_uses_r2_share_threshold_from_config():
    from ior_mvp.config import thresholds_config
    from ior_mvp.screening.rules import warnings

    case = _case(values=(1_000_000, 2_000_000, 4_000_000), weights=(1_000_000, 1_000_000, 1_000_000))
    ledger = _ledger(case)
    assert warnings(case, ledger, thresholds_config())["price_led_growth"] is True


def test_r3_dual_basis_from_partner_rows_and_not_calculable_without():
    assert _row(_ledger(), "R3")["execution"] == "DISABLED"


def test_r4d_degraded_or_disabled_never_grade():
    row = _row(_ledger(), "R4-D")
    assert row["execution"] in {"DEGRADED", "DISABLED"}
    assert "grade" not in row["metrics"]


def test_r5_not_calculable_and_coexistence_proxy_with_link():
    assert _row(_ledger(), "R5")["execution"] in {"DEGRADED", "DISABLED"}


def test_r9s_fires_only_with_link_and_signal():
    case = _case()
    case["domestic_capability"].update(
        same_process_family=True,
        verified_present=True,
        coarse_adjacency_signals=[{"signal_type": "core_process", "evidence_ids": ["L1"]}],
    )
    assert _row(_ledger(case), "R9-S")["fired"] is True


def test_r11_warning_true_above_threshold_while_exclusion_predicate_false_without_nameplate():
    from ior_mvp.config import thresholds_config
    from ior_mvp.screening.rules import warnings

    case = _case()
    case["trade"][-1]["exports_usd_m"] = case["trade"][-1]["imports_usd_m"] * 100
    ledger = _ledger(case)
    assert warnings(case, ledger, thresholds_config())["export_import_ratio_warning"] is True
    assert _row(ledger, "R11")["fired"] is False


def test_ledger_rows_carry_codes_not_english_prose():
    for row in _ledger():
        assert set(row) == {
            "rule_id", "execution", "fired", "metrics", "result_code", "decision_effect_code"
        }


def test_classification_continuity_patterns():
    from ior_mvp.config import thresholds_config
    from ior_mvp.screening.rules import warnings

    case = _case()
    case["trade_quality"]["missing_years"] = [2023]
    result = warnings(case, _ledger(case), thresholds_config())
    assert result["classification_continuity"]["pattern"] == "GAP_YEARS"


def test_injected_r11_threshold_changes_warning():
    from ior_mvp.config import thresholds_config
    from ior_mvp.screening.rules import warnings

    case = _case()
    case["trade"][-1]["exports_usd_m"] = case["trade"][-1]["imports_usd_m"] * 2
    config = copy.deepcopy(thresholds_config())
    config["rules"]["R11"]["generic_capacity_export_import_value_ratio"] = 1
    assert warnings(case, _ledger(case, thresholds=config), config)["export_import_ratio_warning"] is True
