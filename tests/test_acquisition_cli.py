"""CLI parser and exit-code tests."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import pytest

from ior_mvp.acquisition.cli import build_parser


def test_build_parser_required_args() -> None:
    parser = build_parser()
    sub = next(
        a for a in parser._actions if isinstance(a, argparse._SubParsersAction)
    )
    acq = [n for n in sub.choices if n.startswith("acquire-")]
    assert set(acq) == {
        "acquire-universe",
        "acquire-partners",
        "acquire-tariff",
        "acquire-baci",
    }
    for name in ("acquire-universe", "acquire-partners", "acquire-baci"):
        years = next(
            a for a in sub.choices[name]._actions if a.dest == "years"
        )
        assert years.required and years.default is None
    # DD-19: the tariff tree is one period-free contract; no --years at all.
    assert not any(
        a.dest == "years" for a in sub.choices["acquire-tariff"]._actions
    )
    for name in acq:
        mr = next(
            a for a in sub.choices[name]._actions if a.dest == "max_requests"
        )
        assert mr.required and mr.default is None


def test_acquire_universe_missing_years_exits_2() -> None:
    env = os.environ.copy()
    env.pop("IOR_ACQUISITION_LIVE", None)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ior_mvp.acquisition",
            "acquire-universe",
            "--source",
            "wits_trade",
            "--max-requests",
            "1",
        ],
        env={**env, "PYTHONPATH": "src"},
        cwd=os.path.dirname(os.path.dirname(__file__)),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2


def test_acquire_offline_guard_exits_4() -> None:
    env = os.environ.copy()
    env.pop("IOR_ACQUISITION_LIVE", None)
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ior_mvp.acquisition",
            "acquire-tariff",
            "--source",
            "zatca_tariff",
            "--max-requests",
            "1",
        ],
        env=env,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 4
