from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT, thresholds_config
from ior_mvp.data_repository import get_public_case
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.rules import evaluate_rules
from ior_mvp.signals import (
    MATERIAL_TRIGGER_RULE_IDS,
    NON_SIGNAL_RULE_IDS,
    advance_supporting_signal_rule_ids,
    degraded_material_signal_rule_ids,
    fired_signal_rule_ids,
    material_trigger_rule_ids,
    threshold_rule_key,
)

FIXTURE = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "public_decision"
    / "advance-route-3.json"
)


def _row(rule_id: str, *, execution: str, fired: bool) -> dict:
    return {
        "rule_id": rule_id,
        "execution": execution,
        "fired": fired,
    }


def test_fired_signals_exclude_identity_and_evidence_trigger() -> None:
    rules = [
        _row("R0", execution="FULL", fired=True),
        _row("R12", execution="DEGRADED", fired=True),
        _row("R3", execution="FULL", fired=True),
    ]
    assert fired_signal_rule_ids(rules) == ["R3"]


def test_material_registry_is_exact() -> None:
    assert MATERIAL_TRIGGER_RULE_IDS == frozenset(
        {
            "R1-D",
            "R2",
            "R5",
            "R6",
            "R7",
            "R8",
            "R9-S",
            "R11",
        }
    )
    assert NON_SIGNAL_RULE_IDS == frozenset({"R0", "R12"})


def test_advance_supporting_requires_full_fired_and_config_permission() -> None:
    assert advance_supporting_signal_rule_ids(
        [_row("R2", execution="FULL", fired=True)]
    ) == ["R2"]
    assert advance_supporting_signal_rule_ids(
        [_row("R1-D", execution="DEGRADED", fired=True)]
    ) == []
    assert advance_supporting_signal_rule_ids(
        [_row("R1-D", execution="FULL", fired=True)]
    ) == []
    assert advance_supporting_signal_rule_ids(
        [_row("R9-S", execution="FULL", fired=True)]
    ) == ["R9-S"]
    assert advance_supporting_signal_rule_ids(
        [_row("R3", execution="FULL", fired=True)]
    ) == ["R3"]


def test_injected_config_disallows_r2() -> None:
    rules = [_row("R2", execution="FULL", fired=True)]
    assert advance_supporting_signal_rule_ids(
        rules,
        {"R2": {"may_support_advance": False}},
    ) == []


def test_non_boolean_permission_fails_closed() -> None:
    with pytest.raises(EvidenceIntegrityError, match="boolean"):
        advance_supporting_signal_rule_ids(
            [_row("R2", execution="FULL", fired=True)],
            {"R2": {"may_support_advance": "no"}},
        )


def test_ledger_order_preserved() -> None:
    rules = [
        _row("R9-S", execution="FULL", fired=True),
        _row("R2", execution="FULL", fired=True),
    ]
    assert advance_supporting_signal_rule_ids(rules) == [
        "R9-S",
        "R2",
    ]


def test_degraded_material_signals() -> None:
    assert degraded_material_signal_rule_ids(
        [_row("R1-D", execution="DEGRADED", fired=True)]
    ) == ["R1-D"]
    assert degraded_material_signal_rule_ids(
        [_row("R10", execution="DEGRADED", fired=True)]
    ) == []


def test_real_ledgers_yield_expected_supporting_signals() -> None:
    advance = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert advance_supporting_signal_rule_ids(
        evaluate_rules(advance)
    ) == ["R2"]
    steel = get_public_case("SAU-H0-721049")
    assert advance_supporting_signal_rule_ids(
        evaluate_rules(steel)
    ) == ["R2", "R3", "R9-S"]
    pp = get_public_case("SAU-H0-390210")
    assert advance_supporting_signal_rule_ids(
        evaluate_rules(pp)
    ) == ["R9-S", "R11"]


def test_threshold_rule_key_replaces_hyphen() -> None:
    assert threshold_rule_key("R1-D") == "R1_D"
    assert (
        thresholds_config()["rules"]["R1_D"]["may_support_advance"]
        is False
    )


def test_public_decision_has_no_private_material_registry() -> None:
    for module_path in (
        PROJECT_ROOT / "src" / "ior_mvp" / "public_decision.py",
        PROJECT_ROOT / "src" / "ior_mvp" / "route_hypotheses.py",
    ):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(
                node.targets[0], ast.Name
            ):
                names.add(node.targets[0].id)
            elif isinstance(node, ast.AnnAssign) and isinstance(
                node.target, ast.Name
            ):
                names.add(node.target.id)
        assert "_MATERIAL_RULES" not in names

    signals_tree = ast.parse(
        (PROJECT_ROOT / "src" / "ior_mvp" / "signals.py").read_text(
            encoding="utf-8"
        )
    )
    signal_names: set[str] = set()
    for node in signals_tree.body:
        if isinstance(node, ast.Assign) and isinstance(
            node.targets[0], ast.Name
        ):
            signal_names.add(node.targets[0].id)
        elif isinstance(node, ast.AnnAssign) and isinstance(
            node.target, ast.Name
        ):
            signal_names.add(node.target.id)
    assert "MATERIAL_TRIGGER_RULE_IDS" in signal_names
