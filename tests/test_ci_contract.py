from __future__ import annotations

from typing import Any

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT

WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
MAKEFILE = PROJECT_ROOT / "Makefile"


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
        "python scripts/check_ui_contracts.py",
        "python -m compileall -q src scripts tests",
        "python scripts/check_es_modules.py --node node",
        "python scripts/verify_integrity.py",
        "python scripts/validate_scenarios.py",
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
            "PYTHONPATH=src uv run --locked --extra dev "
            "python scripts/validate_scenarios.py",
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
            "PYTHONPATH=src python scripts/validate_scenarios.py",
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


@pytest.mark.parametrize(
    ("job_name", "expected_command"),
    [
        (
            "uv-gates",
            "uv run --locked --extra dev "
            "python scripts/check_ui_contracts.py",
        ),
        (
            "pip-gates",
            "python scripts/check_ui_contracts.py",
        ),
    ],
)
def test_ui_contract_gate_immediately_follows_threshold_scan(
    job_name: str,
    expected_command: str,
) -> None:
    steps = _workflow()["jobs"][job_name]["steps"]
    threshold_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Reject embedded threshold literals"
    )
    assert steps[threshold_index + 1] == {
        "name": "Validate UI catalogue, token and copy contracts",
        "run": expected_command,
    }


@pytest.mark.parametrize(
    ("job_name", "expected_command"),
    [
        (
            "uv-gates",
            "PYTHONPATH=src uv run --locked --extra dev "
            "python scripts/validate_scenarios.py",
        ),
        (
            "pip-gates",
            "PYTHONPATH=src python scripts/validate_scenarios.py",
        ),
    ],
)
def test_scenario_validation_immediately_follows_integrity(
    job_name: str,
    expected_command: str,
) -> None:
    steps = _workflow()["jobs"][job_name]["steps"]
    integrity_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Verify integrity"
    )

    assert steps[integrity_index + 1] == {
        "name": (
            "Validate synthetic scenarios against public marginals"
        ),
        "run": expected_command,
    }


def test_make_ci_runs_scenario_validation_after_integrity() -> None:
    makefile = MAKEFILE.read_text(encoding="utf-8")
    text = makefile.split("\nci: uv-sync\n", maxsplit=1)[1]
    fragments = (
        "python scripts/verify_integrity.py",
        "python scripts/validate_scenarios.py",
        "pytest -q",
    )

    assert all(fragment in text for fragment in fragments)
    assert [
        text.index(fragment)
        for fragment in fragments
    ] == sorted(
        text.index(fragment)
        for fragment in fragments
    )


def test_docker_build_job_builds_the_repository_dockerfile() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["docker-build"]
    assert "actions/checkout@v4" in _used_actions(job)
    assert (
        "docker build --file Dockerfile "
        "--tag industrial-opportunity-resolution-mvp:ci ."
    ) in _run_commands(job)


def test_browser_job_is_independent_locked_and_fail_closed() -> None:
    job = _workflow()["jobs"]["browser-gates"]
    commands = _run_commands(job)
    actions = _used_actions(job)

    assert job["name"] == "browser / Chromium / Python 3.12"
    assert job["runs-on"] == "ubuntu-24.04"
    assert "needs" not in job
    assert "if" not in job
    assert "actions/checkout@v4" in actions
    assert "actions/setup-python@v5" in actions
    assert "astral-sh/setup-uv@v6" in actions
    assert "actions/cache@v6.1.0" in actions
    assert "actions/upload-artifact@v7.0.1" in actions

    setup_python = next(
        step
        for step in job["steps"]
        if step.get("uses") == "actions/setup-python@v5"
    )
    assert setup_python["with"]["python-version"] == "3.12"
    setup_uv = next(
        step
        for step in job["steps"]
        if step.get("uses") == "astral-sh/setup-uv@v6"
    )
    assert setup_uv["with"] == {
        "enable-cache": "true",
        "cache-dependency-glob": "uv.lock",
    }

    assert (
        'uv sync --locked --extra dev --extra e2e --python "3.12"'
        in commands
    )
    assert "fonts-noto-core" not in commands
    assert (
        "uv run --locked --extra dev --extra e2e "
        "python -m playwright install --with-deps chromium"
        in commands
    )
    assert "make UV=uv e2e" in commands
    assert any(
        step.get("name") == "Run bilingual real-browser and visual gates"
        for step in job["steps"]
    )

    cache_step = next(
        step
        for step in job["steps"]
        if step.get("uses") == "actions/cache@v6.1.0"
    )
    assert cache_step["with"]["path"] == "~/.cache/ms-playwright"
    assert "runner.os" in cache_step["with"]["key"]
    assert "runner.arch" in cache_step["with"]["key"]
    assert "hashFiles('uv.lock')" in cache_step["with"]["key"]

    upload = next(
        step
        for step in job["steps"]
        if step.get("uses") == "actions/upload-artifact@v7.0.1"
    )
    assert upload["if"] == "${{ failure() }}"
    assert upload["with"]["path"] == ".artifacts/e2e/"
    assert upload["with"]["include-hidden-files"] == "true"
    assert upload["with"]["if-no-files-found"] == "warn"
    assert upload["with"]["retention-days"] == "14"


def test_ci_workflow_contains_no_optional_failure_escape() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "continue-on-error" not in text
    assert "|| true" not in text
    workflow = _workflow()
    assert set(workflow["jobs"]) == {
        "uv-gates",
        "pip-gates",
        "docker-build",
        "browser-gates",
    }
    for job_name, job in workflow["jobs"].items():
        assert "if" not in job
        assert "needs" not in job
        conditional_steps = [
            step
            for step in job["steps"]
            if "if" in step
        ]
        if job_name == "browser-gates":
            assert len(conditional_steps) == 1
            assert conditional_steps[0]["if"] == "${{ failure() }}"
        else:
            assert conditional_steps == []
        for step in job["steps"]:
            assert "continue-on-error" not in step
            if "uses" in step and step["uses"] == "actions/checkout@v4":
                assert step["with"]["persist-credentials"] == "false"
