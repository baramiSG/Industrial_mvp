"""Route-specific queue assignment and Pareto ordering."""

from __future__ import annotations

import math
from typing import Any, Iterable

from .config import QUEUE_IDS


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return float("-inf")
    number = float(value)
    return number if math.isfinite(number) else float("-inf")


def pareto_ranks(points: Iterable[Iterable[Any]]) -> list[int]:
    rows = [tuple(_number(value) for value in point) for point in points]
    remaining = set(range(len(rows)))
    ranks = [0] * len(rows)
    rank = 1
    while remaining:
        frontier = []
        for index in remaining:
            dominated = any(
                all(a >= b for a, b in zip(rows[other], rows[index], strict=True))
                and any(a > b for a, b in zip(rows[other], rows[index], strict=True))
                for other in remaining
                if other != index
            )
            if not dominated:
                frontier.append(index)
        for index in frontier:
            ranks[index] = rank
        remaining.difference_update(frontier)
        rank += 1
    return ranks


def _rule(record: dict[str, Any], rule_id: str) -> dict[str, Any]:
    return next(
        (row for row in record.get("ledger", []) if row.get("rule_id") == rule_id),
        {},
    )


def _warnings_clear(record: dict[str, Any]) -> bool:
    warnings = record.get("warnings", {})
    continuity = warnings.get("classification_continuity", {})
    return (
        warnings.get("export_import_ratio_warning") is not True
        and warnings.get("price_led_growth") is not True
        and continuity.get("pattern") == "NONE"
    )


def _membership(record: dict[str, Any], config: dict[str, Any]) -> dict[str, list[str]]:
    fired = set(record.get("fired_signal_rule_ids", []))
    material = set(record.get("material_trigger_rule_ids", []))
    memberships: dict[str, list[str]] = {}
    robust_cfg = config["queues"]["robust_public_finding"]
    full_material = any(
        row.get("rule_id") in material and row.get("execution") == "FULL"
        for row in record.get("ledger", [])
    )
    if (
        len(material) >= robust_cfg["minimum_fired_material_signals"]
        and (not robust_cfg["require_full_signal"] or full_material)
        and _warnings_clear(record)
    ):
        memberships["robust_public_finding"] = ["MULTIPLE_MATERIAL_SIGNALS"]
    if "R9-S" in fired and len(material - {"R9-S"}) >= config["queues"][
        "incumbent_upgrade_investigation"
    ]["minimum_other_material_signals"]:
        memberships["incumbent_upgrade_investigation"] = [
            "R9S_AND_OTHER_MATERIAL_TRIGGER"
        ]
    if "R3" in fired:
        memberships["resilience_case"] = ["SUPPLIER_CONCENTRATION_SIGNAL"]
    warning = record.get("warnings", {})
    if (
        warning.get("export_import_ratio_warning") is True
        or warning.get("price_led_growth") is True
        or warning.get("classification_continuity", {}).get("pattern") != "NONE"
    ):
        memberships["likely_false_positive"] = ["SCREENING_WARNING"]
    r2 = _rule(record, "R2")
    if (
        r2.get("execution") == "FULL"
        and r2.get("fired") is True
        and not memberships
    ):
        memberships["high_evsi_evidence_investigation"] = [
            "R2_FULL_FIRED",
            "EVSI_NOT_CALCULABLE",
        ]
    return memberships


def assign_queues(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    queues = {
        queue_id: {
            "queue_id": queue_id,
            "ordering_basis": list(config["queues"][queue_id]["ordering_metrics"]),
            "methodology_ref": config["queues"][queue_id]["methodology_ref"],
            "entries": [],
        }
        for queue_id in QUEUE_IDS
    }
    unqueued = 0
    for record in records:
        if record.get("screening_disposition") != "CANDIDATE":
            continue
        memberships = _membership(record, config)
        if not memberships:
            unqueued += 1
            record["queue_reason_codes"] = ["PERSISTENCE_ONLY"]
        metrics = record.get("metrics", {})
        for queue_id, reasons in memberships.items():
            basis = queues[queue_id]["ordering_basis"]
            entry = {
                "hs6": record["hs6"],
                "pareto_rank": 0,
                "ordering_metrics": {
                    key: metrics.get(key, "UNAVAILABLE") for key in basis
                },
                "queue_reason_codes": reasons,
                "screening_disposition": record["screening_disposition"],
                "indicated_state": record.get("indicated_state"),
            }
            if queue_id == "high_evsi_evidence_investigation":
                entry["evsi_status"] = "NOT_CALCULABLE"
            queues[queue_id]["entries"].append(entry)
    for queue in queues.values():
        basis = queue["ordering_basis"]
        entries = queue["entries"]
        ranks = pareto_ranks(
            [tuple(entry["ordering_metrics"][key] for key in basis) for entry in entries]
        )
        for entry, rank in zip(entries, ranks, strict=True):
            entry["pareto_rank"] = rank
        entries.sort(key=lambda entry: (entry["pareto_rank"], entry["hs6"]))
    mapping = {
        "§8.2(a)": {"queue_id": "robust_public_finding", "status": "CALCULATED"},
        "§8.2(b)": {"queue_id": "incumbent_upgrade_investigation", "status": "CALCULATED"},
        "§8.2(c)": {
            "queue_id": None,
            "status": "NOT_CALCULABLE",
            "reason_code": "D_STAR_NOT_ASSIGNED_AT_SCREENING",
        },
        "§8.2(d)": {"queue_id": "resilience_case", "status": "CALCULATED"},
        "§8.2(e)": {"queue_id": "likely_false_positive", "status": "CALCULATED"},
    }
    return queues, {
        "unqueued_candidates": unqueued,
        "methodology_queue_mapping": mapping,
    }
