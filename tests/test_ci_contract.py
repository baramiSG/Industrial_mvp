from __future__ import annotations

from typing import Any

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT

WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"


def _workflow() -> dict[str, Any]:
    assert WORKFLOW.exists()
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(payload, dict)
    return payload


def _run_commands(job: dict[str, Any]) -> str:
    return "\n".join(
        step["run"]
        for step in job["steps"]
        if isinstance(step, dict) and "run" in step
    )


def _used_actions(job: dict[str, Any]) -> list[str]:
    return [
        step["uses"]
        for step in job["steps"]
        if isinstance(step, dict) and "uses" in step
    ]


def test_ci_workflow_triggers_on_push_and_pull_request_to_main() -> None:
    workflow = _workflow()
    assert set(workflow["on"]) == {"push", "pull_request"}
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert workflow["on"]["pull_request"]["branches"] == ["main"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "true"
    group = workflow["concurrency"]["group"]
    assert "github.workflow" in group
    assert "github.event.pull_request.number || github.ref" in group


def test_uv_job_covers_python_312_and_314_with_locked_cache() -> None:
    job = _workflow()["jobs"]["uv-gates"]
    assert job["strategy"]["fail-fast"] == "false"
    assert job["strategy"]["matrix"]["python-version"] == ["3.12", "3.14"]
    assert "actions/setup-python@v5" in _used_actions(job)
    setup_uv = next(step for step in job["steps"] if step.get("uses") == "astral-sh/setup-uv@v6")
    assert setup_uv["with"]["enable-cache"] == "true"
    assert setup_uv["with"]["cache-dependency-glob"] == "uv.lock"
    assert 'uv sync --locked --extra dev --python "${{ matrix.python-version }}"' in _run_commands(job)


def test_pip_job_uses_the_documented_editable_dev_install() -> None:
    job = _workflow()["jobs"]["pip-gates"]
    setup_python = next(step for step in job["steps"] if step.get("uses") == "actions/setup-python@v5")
    assert setup_python["with"]["python-version"] == "3.12"
    assert setup_python["with"]["cache"] == "pip"
    assert setup_python["with"]["cache-dependency-path"] == "pyproject.toml"
    assert 'python -m pip install -e ".[dev]"' in _run_commands(job)


@pytest.mark.parametrize("job_name", ["uv-gates", "pip-gates"])
def test_each_python_job_runs_every_required_gate(job_name: str) -> None:
    commands = _run_commands(_workflow()["jobs"][job_name])
    required_fragments = (
        "python scripts/check_prohibited_files.py",
        "python scripts/check_threshold_literals.py",
        "python -m compileall -q src scripts tests",
        "node --check src/ior_mvp/static/app.js",
        "python scripts/verify_integrity.py",
        "pytest -q",
        "python scripts/demo_smoke.py",
    )
    for fragment in required_fragments:
        assert fragment in commands
    assert [commands.index(fragment) for fragment in required_fragments] == sorted(
        commands.index(fragment) for fragment in required_fragments
    )
    if job_name == "uv-gates":
        required_proof_commands = (
            "PYTHONPATH=src uv run --locked --extra dev "
            "python scripts/verify_integrity.py",
            "PYTHONPATH=src uv run --locked --extra dev pytest -q",
            "PYTHONPATH=src uv run --locked --extra dev "
            "python scripts/demo_smoke.py",
        )
        for command in required_proof_commands:
            assert command in commands.splitlines()
        for command in commands.splitlines():
            if "uv run" in command:
                assert "uv run --locked --extra dev" in command
    else:
        required_proof_commands = (
            "PYTHONPATH=src python scripts/verify_integrity.py",
            "PYTHONPATH=src pytest -q",
            "PYTHONPATH=src python scripts/demo_smoke.py",
        )
        for command in required_proof_commands:
            assert command in commands.splitlines()


@pytest.mark.parametrize(
    ("job_name", "expected_command"),
    [
        (
            "uv-gates",
            "uv run --locked --extra dev "
            "python scripts/check_threshold_literals.py",
        ),
        (
            "pip-gates",
            "python scripts/check_threshold_literals.py",
        ),
    ],
)
def test_threshold_literal_scan_immediately_follows_prohibited_scan(
    job_name: str,
    expected_command: str,
) -> None:
    steps = _workflow()["jobs"][job_name]["steps"]
    prohibited_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Scan prohibited files and secret patterns"
    )
    threshold_step = steps[prohibited_index + 1]
    assert threshold_step == {
        "name": "Reject embedded threshold literals",
        "run": expected_command,
    }


def test_docker_build_job_builds_the_repository_dockerfile() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["docker-build"]
    assert "actions/checkout@v4" in _used_actions(job)
    assert (
        "docker build --file Dockerfile "
        "--tag industrial-opportunity-resolution-mvp:ci ."
    ) in _run_commands(job)


def test_ci_workflow_contains_no_optional_failure_escape() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "continue-on-error" not in text
    assert "|| true" not in text
    workflow = _workflow()
    assert set(workflow["jobs"]) == {"uv-gates", "pip-gates", "docker-build"}
    for job in workflow["jobs"].values():
        assert "if" not in job
        assert "needs" not in job
        for step in job["steps"]:
            assert "if" not in step
            assert "continue-on-error" not in step
            if "uses" in step and step["uses"] == "actions/checkout@v4":
                assert step["with"]["persist-credentials"] == "false"
