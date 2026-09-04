"""Acquisition CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from ..config import PROJECT_ROOT
from .connectors.base import default_registry
from .contracts import OfflineGuardViolation, canonical_dumps
from .pipeline import (
    PipelineDeps,
    acquire_baci,
    acquire_partners,
    acquire_tariff,
    acquire_universe,
    build_snapshots,
    load_candidate_list,
)
from .raw_store import RawStore
from .source_config import acquisition_sources_config
from .transport import UrllibTransport


def _parse_years(value: str) -> tuple[int, ...]:
    if "-" in value:
        start_s, end_s = value.split("-", 1)
        start, end = int(start_s), int(end_s)
        return tuple(range(start, end + 1))
    if "," in value:
        return tuple(int(part.strip()) for part in value.split(","))
    return (int(value),)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ior_mvp.acquisition")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_acquire(name: str, *, years: bool) -> argparse.ArgumentParser:
        cmd = sub.add_parser(name)
        cmd.add_argument("--source", required=False)
        if years:
            cmd.add_argument("--years", required=True, default=None)
        cmd.add_argument("--max-requests", type=int, required=True, default=None)
        cmd.add_argument("--flows", default="imports,exports")
        cmd.add_argument("--data-root", default=None)
        return cmd

    add_acquire("acquire-universe", years=True)
    partners = add_acquire("acquire-partners", years=True)
    partners.add_argument("--candidates", required=True)
    # DD-19: the tariff tree is one period-free contract; no --years at all.
    add_acquire("acquire-tariff", years=False)
    add_acquire("acquire-baci", years=True)

    build_cmd = sub.add_parser("build-snapshots")
    build_cmd.add_argument("--kind", default="all")
    build_cmd.add_argument("--source", default=None)
    build_cmd.add_argument("--data-root", default=None)
    return parser


def _data_root(args: argparse.Namespace) -> Path:
    if args.data_root:
        return Path(args.data_root)
    config = acquisition_sources_config()
    return PROJECT_ROOT / config["raw_store"]["root"]


def _deps(args: argparse.Namespace, *, explicit_live: bool) -> PipelineDeps:
    acquisition_sources_config.cache_clear()
    config = acquisition_sources_config()
    raw_cfg = config["raw_store"]
    data_root = _data_root(args)
    store = RawStore(
        data_root,
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    offline = config["offline_guard"]
    transport = UrllibTransport(
        user_agent=offline["user_agent"],
        timeout_seconds=60,
        allowed_headers=offline["header_allowlist"],
        denied_headers=offline["header_denylist"],
        live_env_var=offline["live_env_var"],
        environ=os.environ,
    )
    from .contracts import new_run_id

    return PipelineDeps(
        config=config,
        store=store,
        transport=transport,
        registry=default_registry(),
        run_id=new_run_id(),
        environ=os.environ,
        sleeper=time.sleep,
    )


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command.startswith("acquire-"):
        if args.max_requests is None:
            print("error: --max-requests is required", file=sys.stderr)
            sys.exit(2)
        if args.command != "acquire-tariff" and getattr(args, "years", None) is None:
            print("error: --years is required", file=sys.stderr)
            sys.exit(2)
    try:
        deps = _deps(args, explicit_live=args.command.startswith("acquire-"))
    except OfflineGuardViolation as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(4)

    try:
        if args.command == "acquire-universe":
            if not args.source:
                print("error: --source is required", file=sys.stderr)
                sys.exit(2)
            years = _parse_years(args.years)
            flows = tuple(args.flows.split(","))
            report = acquire_universe(
                args.source,
                years=years,
                flows=flows,
                deps=deps,
                max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-partners":
            if not args.source:
                print("error: --source is required", file=sys.stderr)
                sys.exit(2)
            years = _parse_years(args.years)
            flows = tuple(args.flows.split(","))
            candidates = load_candidate_list(Path(args.candidates))
            report = acquire_partners(
                args.source,
                candidates=candidates,
                years=years,
                flows=flows,
                deps=deps,
                max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-tariff":
            source = args.source or "zatca_tariff"
            report = acquire_tariff(
                source,
                deps=deps,
                max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-baci":
            years = _parse_years(args.years)
            report = acquire_baci(
                years=years,
                deps=deps,
                max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "build-snapshots":
            data_root = Path(args.data_root) if args.data_root else PROJECT_ROOT / "data"
            report = build_snapshots(
                args.kind,
                deps,
                source_id=args.source,
                data_root=data_root,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(0)

        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(2)
    except OfflineGuardViolation as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(4)
