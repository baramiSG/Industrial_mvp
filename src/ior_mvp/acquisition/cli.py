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
from .contracts import (
    AcquisitionConfigurationError,
    OfflineGuardViolation,
    RESERVED_UNIT_PARAMETERS,
    canonical_dumps,
)
from .documents.store import validate_list_id
from .entities.mentions import LIST_ID_PATTERN
from .entities.rules import EntityResolutionError
from .entities.store import build_entity_resolution
from .pipeline import (
    PipelineDeps,
    acquire_aggregates,
    acquire_baci,
    acquire_directory,
    acquire_documents,
    acquire_partners,
    acquire_registry,
    acquire_tariff,
    acquire_universe,
    build_documents,
    build_snapshots,
    load_candidate_list,
)
from .raw_store import RawStore
from .source_config import acquisition_sources_config
from .transport import UrllibTransport, assert_live_permitted


def _parse_years(value: str) -> tuple[int, ...]:
    if "-" in value:
        start_s, end_s = value.split("-", 1)
        start, end = int(start_s), int(end_s)
        return tuple(range(start, end + 1))
    if "," in value:
        return tuple(int(part.strip()) for part in value.split(","))
    return (int(value),)


def _parse_parameters(values: list[str]) -> tuple[tuple[str, str], ...]:
    parsed: list[tuple[str, str]] = []
    for raw in values:
        if "=" not in raw:
            raise AcquisitionConfigurationError(
                "parameters require NAME=VALUE"
            )
        key, value = raw.split("=", 1)
        if not key or key in RESERVED_UNIT_PARAMETERS:
            raise AcquisitionConfigurationError(
                f"parameter name is reserved: {key!r}"
            )
        parsed.append((key, value))
    if len({key for key, _ in parsed}) != len(parsed):
        raise AcquisitionConfigurationError("parameter names must be unique")
    return tuple(sorted(parsed))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ior_mvp.acquisition")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_acquire(name: str, *, years: bool, source_required: bool = False, flows: bool = True) -> argparse.ArgumentParser:
        cmd = sub.add_parser(name)
        cmd.add_argument("--source", required=source_required)
        if years:
            cmd.add_argument("--years", required=True, default=None)
        cmd.add_argument("--max-requests", type=int, required=True, default=None)
        if flows:
            cmd.add_argument("--flows", default="imports,exports")
        cmd.add_argument("--data-root", default=None)
        return cmd

    add_acquire("acquire-universe", years=True)
    partners = add_acquire("acquire-partners", years=True)
    partners.add_argument("--candidates", required=True)
    partners.add_argument("--parameter", action="append", default=[])
    # DD-19: the tariff tree is one period-free contract; no --years at all.
    add_acquire("acquire-tariff", years=False)
    add_acquire("acquire-baci", years=True)
    add_acquire("acquire-aggregates", years=True, source_required=True, flows=False)
    add_acquire("acquire-directory", years=False, source_required=True, flows=False)
    add_acquire("acquire-registry", years=False, source_required=True, flows=False)
    docs = sub.add_parser("acquire-documents")
    docs.add_argument("--source", required=True)
    docs.add_argument("--list-id", required=True)
    docs.add_argument("--max-requests", type=int, required=True)
    docs.add_argument("--data-root", default=None)

    build_docs = sub.add_parser("build-documents")
    build_docs.add_argument("--source", required=True)
    build_docs.add_argument("--list-id", required=True)
    build_docs.add_argument("--data-root", default=None)

    build_cmd = sub.add_parser("build-snapshots")
    build_cmd.add_argument("--kind", default="all")
    build_cmd.add_argument("--source", default=None)
    build_cmd.add_argument("--data-root", default=None)
    build_entities = sub.add_parser("build-entities")
    build_entities.add_argument("--mention-list-id", required=True)
    build_entities.add_argument("--data-root", default=None)
    return parser


def _data_root(args: argparse.Namespace) -> Path:
    if args.data_root:
        root = Path(args.data_root)
        return root / "raw" if args.command == "build-documents" else root
    config = acquisition_sources_config()
    return PROJECT_ROOT / config["raw_store"]["root"]


def _deps(args: argparse.Namespace, *, explicit_live: bool) -> PipelineDeps:
    acquisition_sources_config.cache_clear()
    config = acquisition_sources_config()
    offline = config["offline_guard"]
    if explicit_live:
        assert_live_permitted(explicit_live, os.environ, offline["live_env_var"])
    raw_cfg = config["raw_store"]
    data_root = _data_root(args)
    store = RawStore(
        data_root,
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
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
        if args.command not in {
            "acquire-tariff", "acquire-directory", "acquire-registry", "acquire-documents",
        } and getattr(args, "years", None) is None:
            print("error: --years is required", file=sys.stderr)
            sys.exit(2)
        if args.command in {"acquire-universe", "acquire-partners"} and not args.source:
            print("error: --source is required", file=sys.stderr)
            sys.exit(2)
    if args.command in {"acquire-documents", "build-documents"}:
        try:
            validate_list_id(args.list_id)
        except AcquisitionConfigurationError as exc:
            parser.error(str(exc))
    if args.command == "acquire-partners":
        try:
            args.parameters = _parse_parameters(args.parameter)
        except AcquisitionConfigurationError as exc:
            parser.error(str(exc))
    if args.command == "build-entities":
        if LIST_ID_PATTERN.fullmatch(args.mention_list_id) is None:
            parser.error(f"Invalid entity mention list_id: {args.mention_list_id!r}")
        data_root = Path(args.data_root) if args.data_root else PROJECT_ROOT / "data"
        try:
            report = build_entity_resolution(
                data_root,
                mention_list_id=args.mention_list_id,
            )
        except EntityResolutionError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(3)
        print(canonical_dumps(report.__dict__))
        sys.exit(0)
    try:
        deps = _deps(args, explicit_live=args.command.startswith("acquire-"))
    except OfflineGuardViolation as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(4)

    try:
        if args.command == "acquire-universe":
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
                parameters=args.parameters,
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

        if args.command == "acquire-aggregates":
            report = acquire_aggregates(
                args.source, years=_parse_years(args.years),
                deps=deps, max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-directory":
            report = acquire_directory(args.source, deps=deps, max_requests=args.max_requests)
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-registry":
            report = acquire_registry(args.source, deps=deps, max_requests=args.max_requests)
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "acquire-documents":
            report = acquire_documents(
                args.source,
                list_id=args.list_id,
                deps=deps,
                max_requests=args.max_requests,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(report.exit_code)

        if args.command == "build-documents":
            report = build_documents(
                args.source,
                list_id=args.list_id,
                deps=deps,
            )
            print(canonical_dumps(report.__dict__))
            sys.exit(0)

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
