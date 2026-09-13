"""Command-line interface for graph projection and mirror operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ior_mvp.config import DATA_DIR, PROJECT_ROOT

from .artifact import (
    GraphIntegrityError,
    canonical_bytes,
    load_projection,
    validate_projection,
    write_projection,
)
from .projection import GraphProjectionError, build_repository_projection
from .loader import (
    GraphConnectionFailure,
    GraphDriverNotInstalled,
    GraphSafetyError,
    GraphVerificationError,
    clear,
    ensure_credential,
    load,
    resolve_target,
    verify,
    wait,
)


def _build(args: argparse.Namespace) -> int:
    projection = build_repository_projection(PROJECT_ROOT)
    out = args.out
    if args.check:
        current = load_projection(out)
        if canonical_bytes(current) != canonical_bytes(projection):
            print("GRAPH BUILD FAIL: committed projection differs", file=sys.stderr)
            return 1
    else:
        write_projection(projection, out)
    print(
        "GRAPH BUILD PASS "
        f"({projection.projection_id}; "
        f"{projection.counts['nodes']} nodes; "
        f"{projection.counts['edges']} edges)"
    )
    return 0


def _validate(args: argparse.Namespace) -> int:
    projection = load_projection(args.root)
    validate_projection(projection)
    print(
        "GRAPH VALIDATION PASS "
        f"({projection.projection_id}; "
        f"{projection.counts['nodes']} nodes; "
        f"{projection.counts['edges']} edges)"
    )
    return 0


def _credential(args: argparse.Namespace) -> int:
    print(ensure_credential(args.path))
    return 0


def _spec(args: argparse.Namespace):
    return resolve_target(
        args.target,
        confirm_instance=getattr(args, "confirm_instance", None),
    )


def _wait(args: argparse.Namespace) -> int:
    wait(_spec(args), args.timeout)
    print(f"GRAPH READY ({args.target})")
    return 0


def _load(args: argparse.Namespace) -> int:
    projection = load_projection(args.root, args.projection)
    report = load(_spec(args), projection)
    print(
        "GRAPH LOAD PASS "
        f"({report.target}; {report.projection_id}; "
        f"created {report.nodes_created} nodes / "
        f"{report.relationships_created} relationships)"
    )
    return 0


def _verify(args: argparse.Namespace) -> int:
    projection = load_projection(args.root, args.projection)
    report = verify(_spec(args), projection)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    print(
        "GRAPH VERIFY PASS "
        f"({report.target}; {report.projection_id}; "
        f"{report.node_count} nodes; {report.edge_count} edges)"
    )
    return 0


def _clear(args: argparse.Namespace) -> int:
    clear(_spec(args), confirm=args.confirm_clear)
    print(f"GRAPH CLEAR PASS ({args.target})")
    return 0


def parser() -> argparse.ArgumentParser:
    """Build the graph CLI parser."""
    command = argparse.ArgumentParser(prog="python -m ior_mvp.graph")
    subcommands = command.add_subparsers(dest="command", required=True)

    build = subcommands.add_parser("build")
    build.add_argument("--out", type=Path, default=DATA_DIR / "graph")
    build.add_argument("--check", action="store_true")
    build.set_defaults(handler=_build)

    validate = subcommands.add_parser("validate")
    validate.add_argument("--root", type=Path, default=DATA_DIR / "graph")
    validate.set_defaults(handler=_validate)

    credential = subcommands.add_parser("credential")
    credential.add_argument(
        "--path",
        type=Path,
        default=PROJECT_ROOT / ".secrets/neo4j_auth.txt",
    )
    credential.set_defaults(handler=_credential)

    def target_parser(name: str) -> argparse.ArgumentParser:
        target = subcommands.add_parser(name)
        target.add_argument(
            "--target",
            required=True,
            choices=("compose", "ci", "aura"),
        )
        target.add_argument("--confirm-instance")
        return target

    wait_command = target_parser("wait")
    wait_command.add_argument("--timeout", type=float, default=180.0)
    wait_command.set_defaults(handler=_wait)

    load_command = target_parser("load")
    load_command.add_argument("--root", type=Path, default=DATA_DIR / "graph")
    load_command.add_argument("--projection")
    load_command.set_defaults(handler=_load)

    verify_command = target_parser("verify")
    verify_command.add_argument("--root", type=Path, default=DATA_DIR / "graph")
    verify_command.add_argument("--projection")
    verify_command.add_argument("--report", type=Path)
    verify_command.set_defaults(handler=_verify)

    clear_command = target_parser("clear")
    clear_command.add_argument("--confirm-clear", required=True)
    clear_command.set_defaults(handler=_clear)
    return command


def main(argv: Sequence[str] | None = None) -> int:
    """Execute one graph command with stable exit semantics."""
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except GraphSafetyError as exc:
        print(f"GRAPH SAFETY REFUSAL: {exc}", file=sys.stderr)
        return 3
    except (
        GraphConnectionFailure,
        GraphDriverNotInstalled,
        GraphIntegrityError,
        GraphProjectionError,
        GraphVerificationError,
    ) as exc:
        print(f"GRAPH ERROR: {exc}", file=sys.stderr)
        return 1
