from __future__ import annotations

from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


RUNNER = PROJECT_ROOT / "scripts" / "final_acceptance.sh"


def test_final_acceptance_runner_has_required_order() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    ordered = (
        'run_step "make_ci"',
        'run_step "clean_venv_create"',
        'run_step "clean_pip_install"',
        'run_step "clean_prohibited"',
        'run_step "clean_thresholds"',
        'run_step "clean_compile"',
        'run_step "clean_node"',
        'run_step "clean_integrity"',
        'run_step "clean_gate_b"',
        'run_step "clean_pytest"',
        'run_step "clean_smoke"',
        'run_step "docker_build"',
        'record_server_step "uvicorn_start"',
        'run_step "http_journeys"',
        'run_step "http_nfr_005"',
        'run_step "http_failures"',
        'run_step "integrity_422_testclient"',
        'record_server_step "uvicorn_restart"',
        'run_step "revert_apply"',
        'run_step "revert_abort"',
        'run_step "final_prohibited"',
        'run_step "final_thresholds"',
        'run_step "final_gate_b"',
        'run_step "keyword_scan"',
        'run_step "docs_audit"',
        'run_step "source_archive"',
        'run_step "protected_diff"',
        'render_results',
    )
    indexes = [source.index(fragment) for fragment in ordered]
    assert indexes == sorted(indexes)


def test_final_acceptance_runner_locks_required_contracts() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    for fragment in (
        "python3 -m venv",
        "--clear",
        'pip install -e ".[dev]"',
        "docker run -d",
        "-p 8001:8000",
        "--host 127.0.0.1",
        "--port 8010",
        'RELEASE_VERSION="0.2.0"',
        "git revert --no-commit "
        "98c1a40225a94090238867bc9861e8c6544b5839",
        "git revert --abort",
        "acceptance_results.md",
        "__FINAL_ACCEPTANCE__",
    ):
        assert fragment in source
    assert "scripts/build_manifests.py" not in source
    assert "|| true" not in source


def test_runner_is_executable() -> None:
    assert RUNNER.stat().st_mode & 0o111


def test_runner_records_milliseconds_and_accepts_expected_sigterm() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert source.count('date +%s%N') == 4
    assert source.count(
        "duration=$(((ended - started) / 1000000))"
    ) == 2
    assert '0|143)' in source


def test_keyword_classifier_handles_governed_and_fixture_hits() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    for fragment in (
        'path.startswith("data/")',
        'path == "docs/authority/methodology_extracted.md"',
        'path.startswith("docs/implementation/")',
        '"placeholder",',
    ):
        assert fragment in source


def test_runner_reports_real_browser_proof_and_exact_axe_disposition() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "Browser paint or interaction was not executed" not in source
    assert "KL-22 limits product proof" not in source
    assert (
        "The real-browser gate ran through `make ci`"
        in source
    )
    assert (
        'path == "browser_tests/vendor/axe-core-4.13.0/axe.min.js"'
        in source
    )
    assert (
        "LEGITIMATE — SHA-verified vendored third-party source"
        in source
    )
    assert 'path.startswith("browser_tests/")' not in source
    keyword_function = source.split(
        "step_keyword_scan() {",
        maxsplit=1,
    )[1].split(
        "step_docs_audit() {",
        maxsplit=1,
    )[0]
    assert 'require_step "make_ci"' in keyword_function
    assert 'if [[ "$STEP_NUMBER" -ne 42 ]]' in source


def test_runner_checks_every_frontend_es_module() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    node_function = source.split(
        "step_clean_node() {",
        maxsplit=1,
    )[1].split(
        "step_clean_integrity() {",
        maxsplit=1,
    )[0]

    assert (
        '"$PIP_PYTHON" scripts/check_es_modules.py --node node'
        in node_function
    )
    assert "node --check src/ior_mvp/static/app.js" not in node_function


def test_runner_checks_ui_contracts_before_compilation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    compile_function = source.split(
        "step_clean_compile() {",
        maxsplit=1,
    )[1].split(
        "step_clean_node() {",
        maxsplit=1,
    )[0]

    assert (
        '"$PIP_PYTHON" scripts/check_ui_contracts.py'
        in compile_function
    )
    assert (
        compile_function.index("scripts/check_ui_contracts.py")
        < compile_function.index("-m compileall")
    )
    assert 'if [[ "$STEP_NUMBER" -ne 42 ]]' in source
