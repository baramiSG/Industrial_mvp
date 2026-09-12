"""Offline screening CLI; no network transport is imported."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from ior_mvp.config import PROJECT_ROOT

from .config import screening_config
from .inputs import assemble_inputs
from .snapshot import (
    build_screening_snapshot,
    canonical_bytes,
    load_screening_summary_directory,
    load_screening_snapshot_directory,
    reconstruct_screening_snapshot,
    validate_screening_snapshot_directory,
    write_screening_snapshot,
)


def _compact(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def emit_candidates(
    *,
    universe_id: str,
    records: list[dict[str, Any]],
    inputs: dict[str, Any],
    batch_size: int,
    root: Path,
    recorded_on: str,
) -> list[Path]:
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    codes = sorted(
        {
            record["hs6"]
            for record in records
            if record.get("screening_disposition") == "CANDIDATE"
            and any(
                row.get("rule_id") == "R2"
                and row.get("execution") == "FULL"
                and row.get("fired") is True
                for row in record.get("ledger", [])
            )
        }
    )
    if not codes:
        return []
    root.mkdir(parents=True, exist_ok=True)
    inputs_hash = hashlib.sha256(_compact(inputs)).hexdigest()
    total = (len(codes) + batch_size - 1) // batch_size
    paths = []
    for offset in range(0, len(codes), batch_size):
        index = offset // batch_size + 1
        batch = codes[offset : offset + batch_size]
        payload = {
            "schema_version": "1.0.0",
            "candidate_source": "SCREENING_CHEAP_RULES_V1",
            "hs6_codes": batch,
            "recorded_on": recorded_on,
            "selection_rule": "R2_FULL_FIRED_ON_UNIVERSE",
            "inputs": inputs,
            "batch": {
                "index": index,
                "total": total,
                "batch_size": batch_size,
            },
            "sha256_of_hs6_codes": hashlib.sha256(_compact(batch)).hexdigest(),
        }
        path = root / (
            f"CANDIDATES-{universe_id}-{inputs_hash[:12]}-batch-{index:02d}.json"
        )
        content = canonical_bytes(payload)
        if path.exists() and path.read_bytes() != content:
            raise ValueError("candidate-list write conflict")
        if not path.exists():
            path.write_bytes(content)
        paths.append(path)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ior_mvp.screening")
    sub = parser.add_subparsers(dest="command", required=True)
    emit = sub.add_parser("emit-candidates")
    emit.add_argument("--universe", required=True)
    emit.add_argument("--batch-size", type=int, default=50)
    emit.add_argument("--data-root")
    build = sub.add_parser("build")
    build.add_argument("--data-root")
    validate = sub.add_parser("validate")
    validate.add_argument("--check-inputs", action="store_true")
    validate.add_argument("--data-root")
    reconstruct = sub.add_parser("reconstruct")
    reconstruct.add_argument("--data-root")
    return parser


def _root(value: str | None) -> Path:
    return Path(value) if value else PROJECT_ROOT / "data"


def _latest_snapshot(root: Path) -> Path | None:
    paths = [
        path
        for path in (root / "screening" / "snapshots").glob("SCREENING-*")
        if path.is_dir()
    ]
    if not paths:
        return None
    summaries = [
        (load_screening_summary_directory(path), path)
        for path in paths
    ]
    return max(
        summaries,
        key=lambda item: (
            item[0]["as_of_date"],
            item[0]["snapshot_id"],
        ),
    )[1]


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    root = _root(args.data_root)
    try:
        if args.command == "build":
            inputs = assemble_inputs(root, source_id="un_comtrade")
            record = build_screening_snapshot(inputs, screening_config())
            path = write_screening_snapshot(
                record, root / "screening" / "snapshots"
            )
            print(path)
            return
        path = _latest_snapshot(root)
        if path is None:
            raise ValueError("NO_SCREENING_SNAPSHOT")
        if args.command == "validate":
            validate_screening_snapshot_directory(
                path,
                config=screening_config(),
                check_inputs=args.check_inputs,
            )
            print("SCREENING VALIDATION PASS")
            return
        if args.command == "reconstruct":
            result = reconstruct_screening_snapshot(path, root)
            if not result.match:
                raise ValueError(result.reason)
            print("SCREENING RECONSTRUCTION PASS (1 snapshots)")
            return
        if args.command == "emit-candidates":
            record = load_screening_snapshot_directory(path)
            if record["universe_status"]["status"] == "UNAVAILABLE":
                raise ValueError("NO_AVAILABLE_UNIVERSE")
            paths = emit_candidates(
                universe_id=args.universe,
                records=record["records"],
                inputs=record["inputs"],
                batch_size=args.batch_size,
                root=root / "screening" / "candidates",
                recorded_on=record["as_of_date"],
            )
            for candidate in paths:
                print(candidate)
            return
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
