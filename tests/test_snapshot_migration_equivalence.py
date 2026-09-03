from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import get_public_case
from ior_mvp.decision_engine import analyze_public
from ior_mvp.rules import _evaluate_rules_v2, evaluate_rules
from tests.legacy_snapshot_v1 import (
    HISTORICAL_V1_ROOT,
    LIVE_PUBLIC_ROOT,
    candidate_v21_from_legacy,
    legacy_evaluate_rules,
    legacy_public_decision,
    load_legacy_snapshot,
)


SNAPSHOT_FILES = (
    "SAU-H0-721049.json",
    "SAU-H0-390210.json",
)
MISSING = "<MISSING>"

COMMON_ADDITIVE_PATHS = {
    "rules.R2.metrics.observed_span_years",
    "rules.R2.metrics.quantity_cagr",
    "rules.R3.metrics.value",
    "rules.R3.metrics.quantity",
    "rules.R4-D.metrics.bulk_band_usd_t",
    "rules.R4-D.metrics.calculation_basis",
    "rules.R4-D.metrics.comparison_observations",
    "rules.R4-D.metrics.iqr_usd_t",
    "rules.R4-D.metrics.minimum_valid_value_coverage",
    "rules.R4-D.metrics.outlier_candidate",
    "rules.R4-D.metrics.reason",
    "rules.R4-D.metrics.source_evidence_id",
    "rules.R4-D.metrics.status",
    "rules.R4-D.metrics.valid_quantity_coverage",
    "rules.R4-D.metrics.valid_value_coverage",
    "rules.R4-D.metrics.weighted_median_usd_t",
    "rules.R4-D.metrics.weighted_q1_usd_t",
    "rules.R4-D.metrics.weighted_q3_usd_t",
    "rules.R5.metrics.apparent_consumption_kt",
    "rules.R5.metrics.calculation_basis",
    "rules.R5.metrics.net_import_exposure_kt",
    "rules.R5.metrics.retained_imports_kt",
    "rules.R5.metrics.unavailable_inputs",
    "rules.R5.metrics.unavailable_reasons",
    "rules.R9-S.metrics.known_hard_gate_failure",
    "rules.R9-S.metrics.qualifying_signal_count",
    "rules.R9-S.metrics.same_process_family",
    "rules.R10.metrics.criticality_evidence_id",
    "rules.R10.metrics.criticality_status",
    "rules.R11.metrics.computed_export_import_value_ratio",
    "rules.R11.metrics.disclosed_export_import_value_ratio",
    "rules.R11.metrics.disclosed_ratio_consistent",
    "rules.R11.metrics.established_nameplate",
    "rules.R11.metrics.ratio_basis",
    "rules.R11.metrics.ratio_reason",
    "rules.R11.metrics.ratio_status",
}
PP_R3_ADDITIVE_PATHS = {
    "rules.R3.metrics.hhi",
    "rules.R3.metrics.hhi_threshold",
    "rules.R3.metrics.largest_supplier_share",
    "rules.R3.metrics.largest_supplier_threshold",
    "rules.R3.metrics.top_two_share",
}
EXPECTED_CHANGED_VALUES = {
    "SAU-H0-721049.json": {
        "rules.R3.result": (
            "External supply is concentrated.",
            (
                "External supply is concentrated on the value basis; "
                "quantity concentration is NOT_CALCULABLE."
            ),
        ),
        "rules.R4-D.result": (
            "Annual/partner product-mix signal is visible.",
            (
                "A source-attributed annual unit-value dispersion summary "
                "supports a descriptive product-mix signal; no cluster or "
                "grade conclusion."
            ),
        ),
        "rules.R11.execution": ("DEGRADED", "FULL"),
        "rules.R11.metrics.export_import_value_ratio": (None, 0.1144),
        "rules.R11.result": (
            "No public-data generic-capacity exclusion fires.",
            (
                "Gross exports are 0.1144× imports; the configured "
                "generic-capacity warning threshold is not met."
            ),
        ),
    },
    "SAU-H0-390210.json": {
        "rules.R3.result": (
            (
                "Partner concentration metrics are absent from the "
                "frozen case snapshot."
            ),
            (
                "Value- and quantity-basis partner concentration are "
                "NOT_CALCULABLE."
            ),
        ),
        "rules.R4-D.result": (
            "Annual/partner product-mix signal is visible.",
            (
                "A source-attributed annual unit-value dispersion summary "
                "supports a descriptive product-mix signal; no cluster or "
                "grade conclusion."
            ),
        ),
    },
}


def _rule_map(rows: list[dict]) -> dict[str, dict]:
    return {row["rule_id"]: row for row in rows}


def _assert_rule_ledger_fields_equal(
    live_rules: list[dict],
    converted_rules: list[dict],
) -> None:
    assert [row["rule_id"] for row in live_rules] == [
        row["rule_id"] for row in converted_rules
    ]
    for live_row, converted_row in zip(
        live_rules,
        converted_rules,
        strict=True,
    ):
        for field in ("execution", "fired", "result", "metrics"):
            assert live_row[field] == converted_row[field], (
                live_row["rule_id"],
                field,
            )


def _deep_diff(
    old: object,
    new: object,
    path: str = "",
) -> dict[str, tuple[object, object]]:
    if isinstance(old, dict) and isinstance(new, dict):
        differences: dict[str, tuple[object, object]] = {}
        for key in sorted(set(old) | set(new)):
            nested = f"{path}.{key}" if path else key
            if key not in old:
                differences[nested] = (MISSING, new[key])
            elif key not in new:
                differences[nested] = (old[key], MISSING)
            else:
                differences.update(_deep_diff(old[key], new[key], nested))
        return differences
    if old != new:
        return {path: (old, new)}
    return {}


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_legacy_adapter_characterizes_pre_migration_production(
    filename: str,
) -> None:
    legacy = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    assert [row["rule_id"] for row in legacy_evaluate_rules(legacy)] == [
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


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_pre_cutover_in_memory_v2_diff_is_exactly_allow_listed(
    filename: str,
) -> None:
    legacy = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    candidate = candidate_v21_from_legacy(legacy)
    old_rules = legacy_evaluate_rules(legacy)
    new_rules = _evaluate_rules_v2(candidate)

    assert [row["rule_id"] for row in old_rules[:-1]] == [
        row["rule_id"] for row in new_rules[:-1]
    ]
    assert {
        row["rule_id"]: row["fired"] for row in old_rules[:-1]
    } == {
        row["rule_id"]: row["fired"] for row in new_rules[:-1]
    }
    differences = _deep_diff(
        _rule_map(old_rules[:-1]),
        _rule_map(new_rules[:-1]),
        "rules",
    )
    additive = set(COMMON_ADDITIVE_PATHS)
    if filename == "SAU-H0-390210.json":
        additive |= PP_R3_ADDITIVE_PATHS
    changed = EXPECTED_CHANGED_VALUES[filename]
    assert set(differences) == additive | set(changed)
    for path in additive:
        assert differences[path][0] == MISSING
    for path, expected in changed.items():
        assert differences[path] == expected

    assert len(new_rules[-1]["metrics"]["evidence_needs"]) == 5
    assert new_rules[-1]["metrics"]["named_missing_facts"] == [
        need["text"]
        for need in new_rules[-1]["metrics"]["evidence_needs"]
    ]


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_live_v2_retains_historical_v1_identity_before_rule_cutover(
    filename: str,
) -> None:
    historical_path = HISTORICAL_V1_ROOT / filename
    live_path = LIVE_PUBLIC_ROOT / filename

    assert historical_path.is_file(), (
        "migration remains RED until byte-identical v1 history exists"
    )
    historical = load_legacy_snapshot(historical_path)
    live = load_legacy_snapshot(live_path)
    assert live["schema_version"] == "2.1.0"
    assert live["snapshot_id"] == historical["snapshot_id"]
    assert live["as_of_date"] == historical["as_of_date"]
    assert live["opportunity"]["id"] == historical["opportunity"]["id"]
    assert live["supersedes"] == historical_path.relative_to(
        PROJECT_ROOT
    ).as_posix()
    assert "rule_context" not in live
    assert "public_decision_contract" not in live


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_live_v2_ledger_equals_converted_historical_v1(
    filename: str,
) -> None:
    historical = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    opportunity_id = historical["opportunity"]["id"]
    live = get_public_case(opportunity_id)
    live_rules = evaluate_rules(live)
    converted_rules = _evaluate_rules_v2(
        candidate_v21_from_legacy(historical)
    )

    _assert_rule_ledger_fields_equal(live_rules, converted_rules)
    legacy_decision = legacy_public_decision(
        historical,
        legacy_evaluate_rules(historical),
    )
    public_decision = analyze_public(opportunity_id)["real_decision"]
    for field in (
        "state",
        "route_code",
        "route_label",
        "headline",
        "rationale",
        "confidence",
        "conditions",
        "kill_conditions",
        "synthetic_flag",
    ):
        assert public_decision[field] == legacy_decision[field]
    assert public_decision["missing_facts"] != legacy_decision[
        "missing_facts"
    ]
    assert len(public_decision["missing_facts"]) == len(
        legacy_decision["missing_facts"]
    ) == 5
    assert set(public_decision) - set(legacy_decision) == {
        "screening_disposition",
        "gap_class",
        "route_hypotheses",
        "preferred_hypothesis",
        "evidence_class_assessment",
        "advance_gate",
        "hard_exclusions",
        "rejection_conditions",
        "narrative_version",
        "localized_narrative",
        "localized_missing_facts",
        "decision_reason_code",
        "advance_support_signal_rule_ids",
    }


def test_live_v2_ledger_equality_detects_in_memory_trade_drift() -> None:
    filename = "SAU-H0-721049.json"
    historical = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    live = deepcopy(get_public_case(historical["opportunity"]["id"]))
    live["trade"][-1]["imports_kt"] += 1

    with pytest.raises(AssertionError):
        _assert_rule_ledger_fields_equal(
            evaluate_rules(live),
            _evaluate_rules_v2(candidate_v21_from_legacy(historical)),
        )
