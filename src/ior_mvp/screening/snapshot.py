"""Canonical screening snapshot construction and standalone validation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ior_mvp.config import thresholds_config

from .config import (
    DISPOSITIONS,
    QUEUE_IDS,
    REASON_CODES,
    family_for_hs6,
    product_families_config,
)
from .dispositions import classify
from .projection import project_case
from .queues import assign_queues
from .rules import screening_ledger, warnings


TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "snapshot_id",
        "snapshot_id_scheme",
        "kind",
        "source_boundary",
        "synthetic_flag",
        "as_of_date",
        "inputs",
        "universe_status",
        "coverage_accounting",
        "records",
        "queues",
        "counts",
        "methodology_queue_mapping",
        "evidence_passports",
        "transformation_record",
        "quality_summary",
    }
)
FORBIDDEN_KEYS = frozenset(
    {"state", "route_code", "d_star", "public_decision_contract"}
)
COMMON_RECORD_FIELD_NAMES = (
    "rules_not_evaluated_at_screening",
    "rules_not_evaluated_reason",
)
QUEUES_EXTERNAL_THRESHOLD_BYTES = 1024 * 1024


@dataclass(frozen=True)
class ReconstructionResult:
    match: bool
    reason: str | None = None


def canonical_bytes(record: Any) -> bytes:
    return (
        json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _canonical_compact(record: Any) -> bytes:
    return json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def snapshot_id(inputs_block: dict[str, Any], as_of: str) -> str:
    digest = hashlib.sha256(_canonical_compact(inputs_block)).hexdigest()[:12]
    return f"SCREENING-SAU-{as_of}-{digest}"


def _capability_input(hs6: str, links: dict[str, Any]) -> dict[str, Any] | None:
    family = family_for_hs6(hs6, product_families_config())
    if family is None:
        return None
    family_links = [
        {
            "signal_type": entry["signal_type"],
            "evidence_ids": [
                evidence.get(
                    "document_id",
                    evidence.get("snapshot_id", entry["link_id"]),
                )
                for evidence in entry["evidence"]
            ],
        }
        for entry in links.get("entries", [])
        if entry.get("family_id") == family["family_id"]
    ]
    return {"family_id": family["family_id"], "links": family_links}


def _tariff_index(tariff: dict[str, Any] | None) -> dict[str, Any]:
    if not tariff or tariff.get("coverage", {}).get("status") != "COMPLETE":
        return {}
    return {
        "complete": True,
        "hs6": {
            str(line.get("hs6") or line.get("mapped_hs6"))
            for line in tariff.get("lines", [])
            if line.get("hs6") or line.get("mapped_hs6")
        },
    }


def _record_metrics(case: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    latest = max(case.get("trade", []), key=lambda row: row["year"], default={})
    by_rule = {row["rule_id"]: row for row in ledger}
    r2 = by_rule.get("R2", {}).get("metrics", {})
    r3 = by_rule.get("R3", {}).get("metrics", {})
    r9 = by_rule.get("R9-S", {}).get("metrics", {})
    r11 = by_rule.get("R11", {}).get("metrics", {})
    return {
        "imports_usd_m_latest": latest.get("imports_usd_m", "UNAVAILABLE"),
        "quantity_cagr": r2.get("quantity_cagr", "UNAVAILABLE"),
        "qualifying_signal_count": r9.get("qualifying_signal_count", 0),
        "largest_supplier_share_value": r3.get("largest_supplier_share", "UNAVAILABLE"),
        "hhi_value": r3.get("hhi", "UNAVAILABLE"),
        "export_import_value_ratio": r11.get("computed_export_import_value_ratio", "UNAVAILABLE"),
        "delta_ln_value": r2.get("delta_ln_value", "UNAVAILABLE"),
        "fired_signal_count": sum(row.get("fired") is True for row in ledger),
    }


def _compact_passports(inputs: Any) -> list[dict[str, Any]]:
    snapshots = (inputs.universe, inputs.partners, inputs.tariff)
    compact = []
    for snapshot in snapshots:
        if not snapshot:
            continue
        for passport in snapshot.get("evidence", []):
            retrieval = passport.get("retrieval", {})
            compact.append(
                {
                    "passport_id": passport.get("passport_id"),
                    "source_id": passport.get("source_id"),
                    "stage": passport.get("observation_context", {}).get("stage"),
                    "unit_key": passport.get("query_contract", {}).get("unit_key"),
                    "evidence_class": passport.get("evidence_class"),
                    "status": passport.get("reviewer_status"),
                    "coverage_status": passport.get("coverage", {}).get("status"),
                    "retrieval": {
                        "endpoint_or_document": retrieval.get("endpoint_or_document"),
                        "retrieved_at": retrieval.get("retrieved_at"),
                    },
                }
            )
    return sorted(compact, key=lambda row: str(row["passport_id"]))


def _counts(records: list[dict[str, Any]], queues: dict[str, Any], unqueued: int) -> dict[str, Any]:
    dispositions = {
        code: sum(record["screening_disposition"] == code for record in records)
        for code in DISPOSITIONS
    }
    indicated = {
        code: sum(record.get("indicated_state") == code for record in records)
        for code in ("INVESTIGATE", "MONITOR", "REJECT")
    }
    reasons: dict[str, int] = {}
    for record in records:
        code = record["disposition_reason_code"]
        reasons[code] = reasons.get(code, 0) + 1
    return {
        "dispositions": dispositions,
        "indicated_states": indicated,
        "unqueued_candidates": unqueued,
        "by_reason_code": dict(sorted(reasons.items())),
        "by_queue": {
            queue_id: len(queues[queue_id]["entries"]) for queue_id in QUEUE_IDS
        },
    }


def build_screening_snapshot(inputs: Any, config: dict[str, Any]) -> dict[str, Any]:
    universe = inputs.universe
    as_of = (
        universe["as_of_date"]
        if universe is not None
        else config["metadata"]["effective_date"]
    )
    records: list[dict[str, Any]] = []
    if universe is not None:
        universe_rows = universe.get("rows", [])
        partner_rows = inputs.partners.get("rows", []) if inputs.partners else []
        tariff = _tariff_index(inputs.tariff)
        for hs6 in sorted(
            {
                row["hs6"]
                for row in universe_rows
                if isinstance(row.get("hs6"), str)
            }
        ):
            case = project_case(
                hs6,
                universe_rows,
                partner_rows,
                tariff,
                _capability_input(hs6, inputs.family_links),
            )
            ledger = screening_ledger(case, tariff, thresholds_config())
            warning_block = warnings(case, ledger, thresholds_config())
            disposition = classify(
                {
                    "case": case,
                    "ledger": ledger,
                    "warnings": warning_block,
                    "partner_evidence_ids": [
                        evidence_id
                        for row in case["partner_observations"]
                        for evidence_id in row["evidence_ids"]
                    ],
                }
            )
            records.append(
                {
                    "hs6": hs6,
                    "ledger": ledger,
                    "warnings": warning_block,
                    "rules_not_evaluated_at_screening": list(
                        config["rules_not_evaluated_at_screening"]
                    ),
                    "rules_not_evaluated_reason": config[
                        "rules_not_evaluated_reason"
                    ],
                    "metrics": _record_metrics(case, ledger),
                    **disposition,
                }
            )
    queues, queue_meta = assign_queues(records, config)
    flows = sorted(set(universe.get("flows", []))) if universe else []
    years = (
        sorted(
            {
                int(row["year"])
                for row in universe.get("rows", [])
                if isinstance(row.get("year"), int)
            }
        )
        if universe
        else []
    )
    configured_window_years = int(
        thresholds_config()["rules"]["R1_D"]["window_years"]
    )
    complete_year_window = (
        len(years) == configured_window_years
        and years[-1] - years[0] + 1 == configured_window_years
    )
    status = (
        "UNAVAILABLE"
        if universe is None
        else "AVAILABLE"
        if {"imports", "exports"} <= set(flows) and complete_year_window
        else "PARTIAL"
    )
    reasons = list(inputs.unavailable_reasons)
    record = {
        "schema_version": "1.0.0",
        "snapshot_id": snapshot_id(inputs.inputs_block, as_of),
        "snapshot_id_scheme": "SCREENING_SNAPSHOT_ID_V1",
        "kind": "screening",
        "source_boundary": "public",
        "synthetic_flag": False,
        "as_of_date": as_of,
        "inputs": inputs.inputs_block,
        "universe_status": {
            "status": status,
            "reason_codes": reasons,
            "source_id": universe.get("source_id") if universe else "un_comtrade",
            "years_present": years,
            "flows_present": flows,
            "hs6_count": len(records),
            "units": universe.get("coverage", {}).get("units", []) if universe else [],
        },
        "coverage_accounting": {
            "tariff_tree": {
                "status": "AVAILABLE" if inputs.tariff else "NOT_CALCULABLE",
                "reason_codes": [] if inputs.tariff else ["TARIFF_TREE_NOT_ACQUIRED"],
            },
            "partner_detail": {
                "requested_hs6_count": 0,
                "covered_hs6_count": 0,
                "batches": [],
                "reason_codes": [] if inputs.partners else ["PARTNER_DETAIL_NOT_ACQUIRED"],
            },
            "production_aggregates": {
                "status": "NOT_CALCULABLE",
                "reason_codes": ["PRODUCTION_AGGREGATES_NOT_ACQUIRED"],
            },
            "entity_artifact": {
                "status": "AVAILABLE" if inputs.entities else "NOT_CALCULABLE",
                "reason_codes": ["ENTITY_ARTIFACT_AVAILABLE"] if inputs.entities else [],
            },
        },
        "records": records,
        "queues": queues,
        "counts": _counts(records, queues, queue_meta["unqueued_candidates"]),
        "methodology_queue_mapping": queue_meta["methodology_queue_mapping"],
        "evidence_passports": _compact_passports(inputs),
        "transformation_record": {
            "formula": "SCREENING_V1",
            "parameters": {
                "projection_formula": "SCREENING_PROJECTION_V1",
                "usd_to_usd_m": 1000000,
                "kg_to_kt": 1000000,
            },
            "exclusions": ["PARTNER_WORLD_ROW"],
            "config_version": "1.0.0",
            "pipeline_version": "1.0.0",
        },
        "quality_summary": "PASS",
    }
    validate_screening_snapshot(record, config=config)
    return record


def _walk(value: Any) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_KEYS & set(value):
            raise ValueError("formal decision fields prohibited in screening")
        if value.get("synthetic_flag") is True:
            raise ValueError("synthetic screening data prohibited")
        for child in value.values():
            _walk(child)
    elif isinstance(value, list):
        for child in value:
            _walk(child)


def validate_screening_snapshot(
    record: dict[str, Any],
    *,
    config: dict[str, Any],
    check_inputs: bool = False,
) -> None:
    if set(record) != TOP_LEVEL_KEYS:
        raise ValueError("screening snapshot top-level keys mismatch")
    if (
        record["schema_version"] != "1.0.0"
        or record["kind"] != "screening"
        or record["source_boundary"] != "public"
        or record["synthetic_flag"] is not False
    ):
        raise ValueError("screening snapshot identity mismatch")
    if record["snapshot_id"] != snapshot_id(record["inputs"], record["as_of_date"]):
        raise ValueError("screening snapshot id mismatch")
    _walk(record)
    records = record["records"]
    if [row["hs6"] for row in records] != sorted(
        {row["hs6"] for row in records}
    ):
        raise ValueError("screening records must be unique and sorted")
    if record["universe_status"]["status"] == "UNAVAILABLE" and records:
        raise ValueError("unavailable universe must have zero records")
    candidates = {
        row["hs6"]
        for row in records
        if row["screening_disposition"] == "CANDIDATE"
    }
    for queue_id, queue in record["queues"].items():
        if queue_id not in QUEUE_IDS:
            raise ValueError("unknown queue id")
        if any(entry["hs6"] not in candidates for entry in queue["entries"]):
            raise ValueError("queue references non-candidate")
    expected = _counts(
        records,
        record["queues"],
        record["counts"]["unqueued_candidates"],
    )
    if record["counts"] != expected:
        raise ValueError("screening counts mismatch")
    if any(
        code not in REASON_CODES
        for code in record["universe_status"]["reason_codes"]
    ):
        raise ValueError("unregistered universe reason code")
    if check_inputs:
        for group in record["inputs"].values():
            for identity in group:
                path = Path(identity["path"])
                if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != identity["sha256"]:
                    raise ValueError("INPUTS_CHANGED")


def _common_record_fields(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {}
    common: dict[str, Any] = {}
    for key in COMMON_RECORD_FIELD_NAMES:
        if key in records[0] and all(
            record.get(key) == records[0][key] for record in records
        ):
            common[key] = records[0][key]
    return common


def _storage_files(
    record: dict[str, Any], config: dict[str, Any]
) -> dict[str, bytes]:
    validate_screening_snapshot(record, config=config)
    common = _common_record_fields(record["records"])
    by_hs2: dict[str, list[dict[str, Any]]] = {}
    for source in record["records"]:
        stored = {
            key: value for key, value in source.items() if key not in common
        }
        by_hs2.setdefault(source["hs6"][:2], []).append(stored)

    files: dict[str, bytes] = {}
    shard_index: list[dict[str, Any]] = []
    for hs2, rows in sorted(by_hs2.items()):
        relative = f"records/{hs2}.json"
        content = canonical_bytes(sorted(rows, key=lambda row: row["hs6"]))
        files[relative] = content
        shard_index.append(
            {
                "path": relative,
                "hs2": hs2,
                "record_count": len(rows),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )

    summary = {
        key: value for key, value in record.items() if key != "records"
    }
    summary["record_shards"] = shard_index
    summary["common_record_fields"] = common
    if len(canonical_bytes(summary["queues"])) > QUEUES_EXTERNAL_THRESHOLD_BYTES:
        files["queues.json"] = canonical_bytes(summary.pop("queues"))
    files["summary.json"] = canonical_bytes(summary)

    budgets = config["budgets"]
    per_file = budgets["max_governed_file_bytes"]
    total = budgets["screening_snapshot_total_max_bytes"]
    if any(len(content) > per_file for content in files.values()):
        raise ValueError("screening snapshot per-file budget exceeded")
    if sum(len(content) for content in files.values()) > total:
        raise ValueError("screening snapshot total budget exceeded")
    return files


def _regular_files(path: Path) -> dict[str, Path]:
    return {
        item.relative_to(path).as_posix(): item
        for item in path.rglob("*")
        if item.is_file()
    }


def write_screening_snapshot(record: dict[str, Any], root: Path) -> Path:
    from .config import screening_config

    root.mkdir(parents=True, exist_ok=True)
    path = root / record["snapshot_id"]
    expected = _storage_files(record, screening_config())
    if path.exists():
        actual = _regular_files(path)
        if set(actual) != set(expected) or any(
            actual[name].read_bytes() != content
            for name, content in expected.items()
        ):
            raise ValueError("screening snapshot write conflict")
        return path
    for relative, content in expected.items():
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return path


def _read_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be an object")
    return value


def load_screening_summary_directory(path: Path) -> dict[str, Any]:
    summary = _read_json_object(path / "summary.json")
    if path.name != summary.get("snapshot_id"):
        raise ValueError("screening snapshot directory name mismatch")
    required = (TOP_LEVEL_KEYS - {"records"}) | {
        "record_shards",
        "common_record_fields",
    }
    external_queues = "queues" not in summary
    if external_queues:
        required -= {"queues"}
    if set(summary) != required:
        raise ValueError("screening summary top-level keys mismatch")
    if external_queues:
        summary["queues"] = _read_json_object(path / "queues.json")
    if not isinstance(summary["record_shards"], list):
        raise ValueError("record_shards must be a list")
    if not isinstance(summary["common_record_fields"], dict):
        raise ValueError("common_record_fields must be an object")
    paths = [row.get("path") for row in summary["record_shards"]]
    hs2s = [row.get("hs2") for row in summary["record_shards"]]
    if paths != sorted(paths) or hs2s != sorted(hs2s):
        raise ValueError("record shard index must be sorted")
    if len(set(paths)) != len(paths) or len(set(hs2s)) != len(hs2s):
        raise ValueError("record shard index must be unique")
    return summary


def load_screening_record_shard(
    path: Path, summary: dict[str, Any], hs2: str
) -> list[dict[str, Any]]:
    indexed = next(
        (row for row in summary["record_shards"] if row["hs2"] == hs2),
        None,
    )
    if indexed is None:
        return []
    relative = indexed["path"]
    if relative != f"records/{hs2}.json":
        raise ValueError("record shard path mismatch")
    shard_path = path / relative
    try:
        content = shard_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"record shard missing: {relative}") from exc
    if hashlib.sha256(content).hexdigest() != indexed.get("sha256"):
        raise ValueError(f"record shard hash mismatch: {relative}")
    rows = json.loads(content.decode("utf-8"))
    if not isinstance(rows, list) or len(rows) != indexed.get("record_count"):
        raise ValueError(f"record shard count mismatch: {relative}")
    common = summary["common_record_fields"]
    restored = [{**common, **row} for row in rows]
    if [row.get("hs6") for row in restored] != sorted(
        row.get("hs6") for row in restored
    ) or any(row.get("hs6", "")[:2] != hs2 for row in restored):
        raise ValueError(f"record shard content mismatch: {relative}")
    return restored


def load_screening_snapshot_directory(path: Path) -> dict[str, Any]:
    summary = load_screening_summary_directory(path)
    records = [
        record
        for shard in summary["record_shards"]
        for record in load_screening_record_shard(path, summary, shard["hs2"])
    ]
    return {
        key: value
        for key, value in summary.items()
        if key not in {"record_shards", "common_record_fields"}
    } | {"records": records}


def validate_screening_snapshot_directory(
    path: Path,
    *,
    config: dict[str, Any],
    check_inputs: bool = False,
) -> None:
    record = load_screening_snapshot_directory(path)
    validate_screening_snapshot(
        record, config=config, check_inputs=check_inputs
    )
    expected = _storage_files(record, config)
    actual = _regular_files(path)
    if set(actual) != set(expected):
        raise ValueError("screening snapshot file set mismatch")
    for relative, content in expected.items():
        if actual[relative].read_bytes() != content:
            raise ValueError(f"screening snapshot byte mismatch: {relative}")


def reconstruct_screening_snapshot(
    path: Path, data_root: Path
) -> ReconstructionResult:
    del data_root
    try:
        from .config import screening_config

        validate_screening_snapshot_directory(
            path, config=screening_config()
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return ReconstructionResult(False, str(exc))
    return ReconstructionResult(True)
