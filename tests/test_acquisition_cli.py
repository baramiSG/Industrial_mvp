"""CLI parser and exit-code tests."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ior_mvp.acquisition.cli import build_parser


def test_make_acquire_partners_quotes_variant_ampersand_for_cli_contract_and_url(
    tmp_path,
    monkeypatch,
) -> None:
    from ior_mvp.acquisition import cli
    from ior_mvp.acquisition.contracts import Stage
    from ior_mvp.acquisition.pipeline import CandidateList, plan_units
    from ior_mvp.acquisition.source_config import acquisition_sources_config

    candidate_path = tmp_path / "candidates.json"
    candidate_path.write_text(
        json.dumps(
            {
                "candidate_source": "TEST DOUBLE",
                "hs6_codes": ["721061"],
                "recorded_on": "2026-09-13",
            }
        )
    )
    rendered = subprocess.run(
        [
            "make",
            "-n",
            "acquire-partners",
            "SOURCE=un_comtrade",
            f"CANDIDATES={candidate_path}",
            "YEARS=2024",
            "FLOWS=imports",
            "MAX_REQUESTS=2",
            "PARAMETERS=partner_dimension_query=&includeDesc=true",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert (
        '--parameter "partner_dimension_query=&includeDesc=true"'
        in rendered
    )

    captured = {}
    monkeypatch.setattr(cli, "_deps", lambda *_args, **_kwargs: object())

    class Report:
        exit_code = 0
        __dict__ = {"exit_code": 0}

    def fake_acquire(*_args, **kwargs):
        captured.update(kwargs)
        return Report()

    monkeypatch.setattr(cli, "acquire_partners", fake_acquire)
    cli_args = [
        "acquire-partners",
        "--source",
        "un_comtrade",
        "--candidates",
        str(candidate_path),
        "--years",
        "2024",
        "--max-requests",
        "2",
        "--flows",
        "imports",
        "--parameter",
        "partner_dimension_query=&includeDesc=true",
    ]
    with pytest.raises(SystemExit, match="0"):
        cli.main(cli_args)
    expected = (("partner_dimension_query", "&includeDesc=true"),)
    assert captured["parameters"] == expected

    contract = plan_units(
        Stage.PARTNERS,
        source_id="un_comtrade",
        years=(2024,),
        flows=("imports",),
        candidates=CandidateList("TEST DOUBLE", ("721061",), "2026-09-13"),
        config=acquisition_sources_config(),
        parameters=expected,
    )[0]
    assert contract.parameters == expected
    template = acquisition_sources_config()["sources"]["un_comtrade"][
        "endpoint_templates"
    ]["PARTNERS"]
    assert template.format(
        reporter="682",
        period="2024",
        flow_code="M",
        product="721061",
        partner_dimension_query=contract.parameters[0][1],
    ).endswith("&includeDesc=true")


def test_acquire_partners_parameter_flag_enters_contract_parameters_and_query_hash_and_rejects_reserved_names(
    tmp_path,
    monkeypatch,
) -> None:
    from ior_mvp.acquisition import cli
    from ior_mvp.acquisition.cli import _parse_parameters
    from ior_mvp.acquisition.contracts import (
        AcquisitionConfigurationError,
        Stage,
    )
    from ior_mvp.acquisition.pipeline import CandidateList, plan_units
    from ior_mvp.acquisition.source_config import acquisition_sources_config

    parser = build_parser()
    args = parser.parse_args(
        [
            "acquire-partners",
            "--source",
            "un_comtrade",
            "--candidates",
            "test.json",
            "--years",
            "2024",
            "--max-requests",
            "2",
            "--parameter",
            "partner_dimension_query=",
        ]
    )
    parameters = _parse_parameters(args.parameter)
    config = acquisition_sources_config()
    candidate = CandidateList("TEST DOUBLE", ("721061",), "2026-09-13")
    plain = plan_units(
        Stage.PARTNERS,
        source_id="un_comtrade",
        years=(2024,),
        flows=("imports",),
        candidates=candidate,
        config=config,
    )[0]
    variant = plan_units(
        Stage.PARTNERS,
        source_id="un_comtrade",
        years=(2024,),
        flows=("imports",),
        candidates=candidate,
        config=config,
        parameters=parameters,
    )[0]
    assert variant.parameters == (("partner_dimension_query", ""),)
    assert variant.query_hash() != plain.query_hash()
    with pytest.raises(AcquisitionConfigurationError, match="reserved"):
        _parse_parameters(["partner=ALL"])
    candidate_path = tmp_path / "candidates.json"
    candidate_path.write_text(
        json.dumps(
            {
                "candidate_source": "TEST DOUBLE",
                "hs6_codes": ["721061"],
                "recorded_on": "2026-09-13",
            }
        ),
        encoding="utf-8",
    )
    captured = {}
    monkeypatch.setattr(cli, "_deps", lambda *_args, **_kwargs: object())

    class Report:
        exit_code = 0
        __dict__ = {"exit_code": 0}

    def fake_acquire(*_args, **kwargs):
        captured.update(kwargs)
        return Report()

    monkeypatch.setattr(cli, "acquire_partners", fake_acquire)
    with pytest.raises(SystemExit) as completed:
        cli.main(
            [
                "acquire-partners",
                "--source",
                "un_comtrade",
                "--candidates",
                str(candidate_path),
                "--years",
                "2024",
                "--max-requests",
                "2",
                "--parameter",
                "partner_dimension_query=",
            ]
        )
    assert completed.value.code == 0
    assert captured["parameters"] == (("partner_dimension_query", ""),)


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
        "acquire-aggregates",
        "acquire-directory",
        "acquire-registry",
        "acquire-documents",
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


INSTITUTIONAL_COMMANDS = [
    ("acquire-aggregates", "gastat", "AGGREGATE", "production"),
    ("acquire-directory", "ministry_of_industry", "DIRECTORY", "directory"),
    ("acquire-directory", "modon", "DIRECTORY", "directory"),
    ("acquire-registry", "saso_catalogue", "REGISTRY", "registry"),
    ("acquire-registry", "saber_registry", "REGISTRY", "registry"),
]


def _institutional_args(command, source, *, max_requests="1"):
    args = [command, "--source", source, "--max-requests", max_requests]
    return args + (["--years", "2024"] if command == "acquire-aggregates" else [])


@pytest.mark.parametrize("command,source,stage,kind", INSTITUTIONAL_COMMANDS)
def test_institutional_parser_requires_source_budget_and_correct_period(command, source, stage, kind):
    parser = build_parser()
    arguments = _institutional_args(command, source)
    parsed = parser.parse_args(arguments)
    assert parsed.source == source and parsed.max_requests == 1
    assert not hasattr(parsed, "flows")
    assert getattr(parsed, "years", None) == ("2024" if stage == "AGGREGATE" else None)
    for flag in ["--source", "--max-requests"] + (["--years"] if stage == "AGGREGATE" else []):
        position = arguments.index(flag)
        with pytest.raises(SystemExit) as refused:
            parser.parse_args(arguments[:position] + arguments[position + 2:])
        assert refused.value.code == 2
    for extra in [["--flows", "imports"]] + ([["--years", "2024"]] if stage != "AGGREGATE" else []):
        with pytest.raises(SystemExit) as refused:
            parser.parse_args(arguments + extra)
        assert refused.value.code == 2


@pytest.mark.parametrize("command,source,stage,kind", INSTITUTIONAL_COMMANDS)
def test_institutional_module_offline_guard_precedes_zero_request_attempt(tmp_path, command, source, stage, kind):
    root = tmp_path / "raw"
    env = {**os.environ, "PYTHONPATH": "src"}
    env.pop("IOR_ACQUISITION_LIVE", None)
    result = subprocess.run([sys.executable, "-m", "ior_mvp.acquisition", *_institutional_args(command, source), "--data-root", str(root)], env=env, capture_output=True, text=True)
    assert result.returncode == 4, result.stdout + result.stderr
    assert "IOR_ACQUISITION_LIVE" in result.stderr
    assert not list(root.rglob("attempt.json")) and not list(root.rglob("page-*.contract.json"))


@pytest.mark.parametrize("command,extra", [("acquire-universe", []), ("acquire-partners", ["--candidates", "not-read.json"])])
def test_existing_missing_source_remains_argument_error_before_offline_guard(tmp_path, command, extra):
    env = {**os.environ, "PYTHONPATH": "src"}
    env.pop("IOR_ACQUISITION_LIVE", None)
    result = subprocess.run([sys.executable, "-m", "ior_mvp.acquisition", command, "--years", "2024", "--max-requests", "1", "--data-root", str(tmp_path / "raw"), *extra], env=env, capture_output=True, text=True)
    assert result.returncode == 2 and "--source is required" in result.stderr
    assert not list(tmp_path.rglob("attempt.json"))


@pytest.mark.parametrize("command,source,stage,kind", INSTITUTIONAL_COMMANDS)
def test_institutional_module_pre_observation_writes_honest_attempt_when_permitted(tmp_path, command, source, stage, kind):
    # A fresh interpreter executes the unchanged module entry point with an
    # explicitly pre-observation config double and a transport that cannot fetch.
    script = '''
import runpy, sys
from ior_mvp.acquisition import source_config, transport
from ior_mvp.acquisition.contracts import Stage
from tests.acquisition_doubles import pre_observation_source_config
config = source_config.acquisition_sources_config()
source, stage = sys.argv[1:3]
config = {**config, 'sources': {source: pre_observation_source_config(source, stage=Stage(stage), authority='TEST authority')}}
def load_config():
    return config
load_config.cache_clear = lambda: None
source_config.acquisition_sources_config = load_config
def forbidden_fetch(*args, **kwargs):
    raise AssertionError('No fetch is permitted in a PRE_OBSERVATION test')
transport.UrllibTransport.fetch = forbidden_fetch
sys.argv = ['ior_mvp.acquisition', *sys.argv[3:]]
runpy.run_module('ior_mvp.acquisition', run_name='__main__')
'''
    root = tmp_path / "raw"
    result = subprocess.run([sys.executable, "-c", script, source, stage, *_institutional_args(command, source), "--data-root", str(root)], env={**os.environ, "PYTHONPATH": "src", "IOR_ACQUISITION_LIVE": "1"}, capture_output=True, text=True)
    assert result.returncode == 3, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["source_id"] == source and report["stage"] == stage
    assert report["years"] == ([2024] if stage == "AGGREGATE" else []) and report["flows"] == []
    assert report["unavailable"] == ["ENDPOINT_UNVERIFIED"] and report["requests_made"] == 0
    attempts = list(root.rglob("attempt.json"))
    assert len(attempts) == 1
    attempt = json.loads(attempts[0].read_text())
    assert attempt["credential_env_var"] is None and attempt["credential_present"] is False
    assert attempt["coverage"]["requests_made"] == 0
    assert not list(root.rglob("page-*.contract.json"))


@pytest.mark.parametrize("command,source,stage,kind", INSTITUTIONAL_COMMANDS)
def test_institutional_pipeline_and_cli_dispatch_preserve_units(tmp_path, monkeypatch, capsys, command, source, stage, kind):
    from ior_mvp.acquisition import cli, pipeline
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.contracts import Stage
    from tests.test_acquisition_institutional_connectors import setup

    config, store, connector, _, transport = setup(tmp_path, source, Stage(stage), kind)
    deps = pipeline.PipelineDeps(config, store, transport, ConnectorRegistry({source: type(connector)}), connector.run_id, {}, lambda _: None)
    wrapper_name = {"AGGREGATE": "acquire_aggregates", "DIRECTORY": "acquire_directory", "REGISTRY": "acquire_registry"}[stage]
    wrapper = getattr(pipeline, wrapper_name, None)
    assert callable(wrapper), "approved pipeline wrapper missing"
    report = wrapper(source, deps=deps, max_requests=2, **({"years": (2024,)} if stage == "AGGREGATE" else {}))
    assert report.exit_code == 0 and report.stage == stage and report.source_id == source
    assert report.years == ((2024,) if stage == "AGGREGATE" else ()) and report.flows == ()
    assert len(report.coverage) == 2 and all(row["status"] == "COMPLETE" for row in report.coverage)
    from dataclasses import replace
    monkeypatch.setattr(cli, "_deps", lambda args, explicit_live: replace(deps, run_id="20260905T120000Z"))
    with pytest.raises(SystemExit) as completed:
        cli.main(_institutional_args(command, source, max_requests="2"))
    assert completed.value.code == 0
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["stage"] == stage and emitted["source_id"] == source
    assert emitted["years"] == list(report.years) and emitted["flows"] == []
    latest = store.latest_runs(source_id=source, stage=stage)
    assert len(latest) == 2 and all(cov.run_id == "20260905T120000Z" for cov, _ in latest.values())


@pytest.mark.parametrize("kind,source,stage", [("production", "gastat", "AGGREGATE"), ("directory", "modon", "DIRECTORY"), ("registry", "saso_catalogue", "REGISTRY"), ("all", "modon", "DIRECTORY")])
def test_build_cli_dispatch_uses_registered_kinds_offline(tmp_path, monkeypatch, capsys, kind, source, stage):
    from functools import partial
    from ior_mvp.acquisition import cli, pipeline, snapshots
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from ior_mvp.acquisition.contracts import Stage
    from tests.test_acquisition_institutional_connectors import setup

    actual_kind = "directory" if kind == "all" else kind
    config, store, connector, contract, transport = setup(tmp_path, source, Stage(stage), actual_kind)
    connector.acquire(contract, max_requests=1)
    registry = ConnectorRegistry({source: type(connector)})
    deps = pipeline.PipelineDeps(config, store, transport, registry, connector.run_id, {}, lambda _: None)
    def injected_deps(args, *, explicit_live):
        assert explicit_live is False
        return deps
    monkeypatch.setattr(cli, "_deps", injected_deps)
    monkeypatch.setattr(cli, "build_snapshots", partial(pipeline.build_snapshots, allow_test_double=True))
    with pytest.raises(SystemExit) as completed:
        cli.main(["build-snapshots", "--kind", kind, "--source", source, "--data-root", str(tmp_path)])
    assert completed.value.code == 0
    output = json.loads(capsys.readouterr().out)
    assert len(output["built"]) == 1
    from pathlib import Path
    path = Path(output["built"][0])
    assert path.parent.name == actual_kind
    assert snapshots.reconstruct(path, store, config, registry).match


def test_build_unknown_kind_refuses_before_writes(tmp_path, monkeypatch):
    from ior_mvp.acquisition import cli, pipeline
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry
    from tests.acquisition_doubles import FakeTransport
    from tests.test_acquisition_snapshots import _temp_store

    deps = pipeline.PipelineDeps({}, _temp_store(tmp_path), FakeTransport({}, []), ConnectorRegistry({}), "TEST", {}, lambda _: None)
    monkeypatch.setattr(cli, "_deps", lambda args, explicit_live: deps)
    with pytest.raises(ValueError, match="Unknown snapshot kind"):
        cli.main(["build-snapshots", "--kind", "not-registered", "--data-root", str(tmp_path)])
    assert not (tmp_path / "snapshots").exists()


def test_dependency_live_seam_checks_permission_but_build_remains_offline(tmp_path, monkeypatch):
    from ior_mvp.acquisition import cli
    from ior_mvp.acquisition.contracts import OfflineGuardViolation

    monkeypatch.delenv("IOR_ACQUISITION_LIVE", raising=False)
    args = build_parser().parse_args(["build-snapshots", "--data-root", str(tmp_path / "raw")])
    with pytest.raises(OfflineGuardViolation):
        cli._deps(args, explicit_live=True)
    assert cli._deps(args, explicit_live=False).store.root == tmp_path / "raw"
    assert not list(tmp_path.rglob("attempt.json"))


@pytest.mark.parametrize("command,source,stage,kind", INSTITUTIONAL_COMMANDS)
def test_make_institutional_targets_enforce_operator_arguments(command, source, stage, kind):
    env = {**os.environ, "IOR_ACQUISITION_LIVE": "1"}
    env.pop("CI", None)
    values = {"SOURCE": source, "MAX_REQUESTS": "2", **({"YEARS": "2023,2024"} if stage == "AGGREGATE" else {})}
    def invoke(changes):
        assignments = {**values, **changes}
        return subprocess.run(["make", "--no-print-directory", command, "UV_RUN=echo", *[f"{key}={value}" for key, value in assignments.items()]], env=env, capture_output=True, text=True)
    good = invoke({})
    assert good.returncode == 0, good.stdout + good.stderr
    argv = good.stdout.splitlines()[-1].split()
    assert argv == ["python", "-m", "ior_mvp.acquisition", command, "--source", source, *(["--years", "2023,2024"] if stage == "AGGREGATE" else []), "--max-requests", "2"]
    for changes, message in [({"IOR_ACQUISITION_LIVE": ""}, "IOR_ACQUISITION_LIVE=1 required"), ({"CI": "1"}, "CI may not acquire"), ({"SOURCE": ""}, "SOURCE required"), ({"MAX_REQUESTS": ""}, "MAX_REQUESTS required")] + ([({"YEARS": ""}, "YEARS required")] if stage == "AGGREGATE" else []):
        refused = invoke(changes)
        assert refused.returncode == 2 and message in refused.stderr
        assert "python -m" not in refused.stdout
