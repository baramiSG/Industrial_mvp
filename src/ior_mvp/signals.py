from __future__ import annotations

from typing import Any

from .config import thresholds_config
from .evidence import EvidenceIntegrityError

NON_SIGNAL_RULE_IDS: frozenset[str] = frozenset({"R0", "R12"})
MATERIAL_TRIGGER_RULE_IDS: frozenset[str] = frozenset(
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


def threshold_rule_key(rule_id: str) -> str:
    return rule_id.replace("-", "_")


def fired_signal_rule_ids(rules: list[dict[str, Any]]) -> list[str]:
    return [
        str(row["rule_id"])
        for row in rules
        if row.get("fired") is True
        and str(row.get("rule_id")) not in NON_SIGNAL_RULE_IDS
    ]


def material_trigger_rule_ids(rules: list[dict[str, Any]]) -> list[str]:
    return [
        rule_id
        for rule_id in fired_signal_rule_ids(rules)
        if rule_id in MATERIAL_TRIGGER_RULE_IDS
    ]


def degraded_material_signal_rule_ids(
    rules: list[dict[str, Any]],
) -> list[str]:
    return [
        str(row["rule_id"])
        for row in rules
        if row.get("fired") is True
        and str(row.get("rule_id")) in MATERIAL_TRIGGER_RULE_IDS
        and row.get("execution") == "DEGRADED"
    ]


def advance_supporting_signal_rule_ids(
    rules: list[dict[str, Any]],
    rule_config: dict[str, Any] | None = None,
) -> list[str]:
    config = (
        rule_config
        if rule_config is not None
        else thresholds_config()["rules"]
    )
    supporting: list[str] = []
    for row in rules:
        rule_id = str(row.get("rule_id"))
        if rule_id in NON_SIGNAL_RULE_IDS:
            continue
        if row.get("fired") is not True:
            continue
        if row.get("execution") != "FULL":
            continue
        entry = config.get(threshold_rule_key(rule_id), {})
        if not isinstance(entry, dict):
            entry = {}
        permission = entry.get("may_support_advance")
        if permission is None:
            supporting.append(rule_id)
            continue
        if not isinstance(permission, bool):
            raise EvidenceIntegrityError(
                f"may_support_advance must be a boolean for {rule_id}"
            )
        if permission is not False:
            supporting.append(rule_id)
    return supporting
