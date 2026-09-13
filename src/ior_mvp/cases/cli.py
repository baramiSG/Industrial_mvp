"""Command-line interface for offline case derivation."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Sequence

from ior_mvp.config import PROJECT_ROOT

from .brief import load_case_brief
from .build import build_brief_to_directory, reconstruct_briefs
from .selection import select_cases, write_selection


def _quotas(values: Sequence[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        for item in value.split(","):
            try:
                profile, raw_quota = item.split("=", 1)
                quota = int(raw_quota)
            except (ValueError, TypeError) as exc:
                raise argparse.ArgumentTypeError(
                    f"invalid quota: {item!r}"
                ) from exc
            if not profile or quota <= 0 or profile in result:
                raise argparse.ArgumentTypeError(f"invalid quota: {item!r}")
            result[profile] = quota
    if not result:
        raise argparse.ArgumentTypeError("at least one quota is required")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ior_mvp.cases")
    commands = parser.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select")
    select.add_argument("--screening", type=Path, required=True)
    select.add_argument("--universe", type=Path, required=True)
    select.add_argument(
        "--families",
        type=Path,
        default=PROJECT_ROOT / "config" / "product_families.v1.yaml",
    )
    select.add_argument("--terms", type=Path, required=True)
    select.add_argument("--identity-exclusions", type=Path)
    select.add_argument(
        "--documents-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "documents",
    )
    select.add_argument("--quota", action="append", required=True)
    select.add_argument("--out", type=Path, required=True)
    select.add_argument("--no-viability", action="store_true")
    select.add_argument("--no-disclosure-key", action="store_true")
    validate = commands.add_parser("validate-brief")
    validate.add_argument("--brief", type=Path, required=True)
    build = commands.add_parser("build")
    build.add_argument("--brief", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)
    commands.add_parser("reconstruct")
    return parser


def _print_selection(record: dict, path: Path) -> None:
    profiles = record["profiles"]
    selected = record["selected_hs6"]
    family_count = record.get("family_count", len(profiles))
    print(
        "CASE SELECTION PASS "
        f"({len(selected)} selected; {len(profiles)} profiles; "
        f"{family_count} families)"
    )
    for profile, result in profiles.items():
        selected_text = ", ".join(result["selected"]) or "none"
        substitutes = result["substitution_order"]
        runner_up = substitutes[0] if substitutes else "none"
        print(
            f"{profile}: {selected_text} "
            f"(runner-up {runner_up}; {len(substitutes)} substitutes; "
            f"{len(result['excluded_by_viability'])} viability exclusions; "
            f"{len(result['excluded_by_identity'])} identity exclusions; "
            f"{len(result['excluded_frozen'])} frozen exclusions)"
        )
    for name, identity in record["inputs"].items():
        if not isinstance(identity, dict):
            continue
        digest = identity.get("sha256") or identity.get("files_sha256")
        if isinstance(digest, str):
            print(f"{name} sha256={digest}")
    print(f"selection_path={path.as_posix()}")
    print(f"selection_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")


def main(argv: Sequence[str] | None = None) -> int:
    """Execute an offline cases command."""
    args = _parser().parse_args(argv)
    if args.command == "validate-brief":
        record = load_case_brief(args.brief)
        print(f"CASE BRIEF VALID {record['brief_id']}")
        return 0
    if args.command == "build":
        path = build_brief_to_directory(args.brief, args.out)
        print(path.as_posix())
        return 0
    if args.command == "reconstruct":
        committed, briefs = reconstruct_briefs()
        print(
            f"CASE RECONSTRUCTION PASS ({committed} snapshots, "
            f"{briefs} briefs)"
        )
        return 0
    if args.command != "select":
        return 2
    quotas = _quotas(args.quota)
    exclusions = (
        args.identity_exclusions
        if args.identity_exclusions is not None
        else args.terms.with_name("identity-exclusions-v1.json")
    )
    record = select_cases(
        screening_dir=args.screening,
        universe_path=args.universe,
        families_path=args.families,
        quotas=quotas,
        terms_path=args.terms,
        identity_exclusions_path=exclusions,
        documents_root=args.documents_root,
        frozen_hs6=frozenset({"390210", "721049"}),
        use_viability=not args.no_viability,
        use_disclosure_key=not args.no_disclosure_key,
    )
    path = write_selection(record, args.out)
    _print_selection(record, path)
    return 0
