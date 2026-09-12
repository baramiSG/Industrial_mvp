"""Runtime screening API router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from ior_mvp.config import thresholds_config

from . import repository
from .config import QUEUE_IDS, product_families_config, screening_config

router = APIRouter(prefix="/api/screening", tags=["screening"])


def _authority() -> dict[str, str]:
    return {
        "screening_config_version": screening_config()["metadata"]["version"],
        "thresholds_version": thresholds_config()["metadata"]["version"],
        "product_families_version": product_families_config()["metadata"]["version"],
        "acquisition_config_version": "1.3.0",
    }


def _missing_summary() -> dict[str, Any]:
    config = screening_config()
    return {
        "snapshot_id": None,
        "as_of_date": None,
        "universe_status": {
            "status": "UNAVAILABLE",
            "reason_codes": ["NO_SCREENING_SNAPSHOT"],
            "source_id": "un_comtrade",
            "years_present": [],
            "flows_present": [],
            "hs6_count": 0,
            "units": [],
        },
        "coverage_accounting": {},
        "counts": {
            "dispositions": {
                "CANDIDATE": 0,
                "SCREENED_OUT": 0,
                "NO_CANDIDATE": 0,
            },
            "indicated_states": {
                "INVESTIGATE": 0,
                "MONITOR": 0,
                "REJECT": 0,
            },
            "unqueued_candidates": 0,
            "by_reason_code": {},
            "by_queue": {queue_id: 0 for queue_id in QUEUE_IDS},
        },
        "queues": [
            {
                "queue_id": queue_id,
                "count": 0,
                "ordering_basis": config["queues"][queue_id]["ordering_metrics"],
                "methodology_ref": config["queues"][queue_id]["methodology_ref"],
            }
            for queue_id in QUEUE_IDS
        ],
        "methodology_queue_mapping": {},
        "unqueued_candidates": 0,
        "authority": _authority(),
        "synthetic_flag": False,
    }


@router.get("")
def summary() -> dict[str, Any]:
    snapshot = repository.screening_snapshot()
    if snapshot is None:
        return _missing_summary()
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "as_of_date": snapshot["as_of_date"],
        "universe_status": snapshot["universe_status"],
        "coverage_accounting": snapshot["coverage_accounting"],
        "counts": snapshot["counts"],
        "queues": [
            {
                "queue_id": queue_id,
                "count": len(queue["entries"]),
                "ordering_basis": queue["ordering_basis"],
                "methodology_ref": queue["methodology_ref"],
            }
            for queue_id, queue in snapshot["queues"].items()
        ],
        "methodology_queue_mapping": snapshot["methodology_queue_mapping"],
        "unqueued_candidates": snapshot["counts"]["unqueued_candidates"],
        "authority": _authority(),
        "synthetic_flag": False,
    }


@router.get("/queues/{queue_id}")
def queue(
    queue_id: str,
    offset: int = Query(default=0, ge=0),
    limit: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    config = screening_config()
    if queue_id not in QUEUE_IDS:
        raise HTTPException(404, detail={"code": "QUEUE_NOT_FOUND"})
    page_size = min(
        limit or config["api"]["page_size_default"],
        config["api"]["page_size_max"],
    )
    snapshot = repository.screening_snapshot()
    queue_record = (
        snapshot["queues"][queue_id]
        if snapshot is not None
        else {
            "ordering_basis": config["queues"][queue_id]["ordering_metrics"],
            "entries": [],
        }
    )
    entries = queue_record["entries"]
    return {
        "queue_id": queue_id,
        "total": len(entries),
        "offset": offset,
        "limit": page_size,
        "ordering_basis": queue_record["ordering_basis"],
        "entries": entries[offset : offset + page_size],
    }


def _evidence_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence_ids" and isinstance(child, list):
                found.update(str(item) for item in child)
            else:
                found.update(_evidence_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_evidence_ids(child))
    return found


@router.get("/records/{hs6}")
def record(hs6: str) -> dict[str, Any]:
    snapshot = repository.screening_snapshot()
    selected = repository.screening_record(hs6)
    if selected is None:
        raise HTTPException(404, detail={"code": "RECORD_NOT_FOUND"})
    ids = _evidence_ids(selected)
    passports = [
        passport
        for passport in snapshot["evidence_passports"]
        if passport["passport_id"] in ids
    ]
    return {**selected, "evidence_passports": passports}
