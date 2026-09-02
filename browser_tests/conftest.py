from __future__ import annotations

import json
import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest

from browser_tests.harness import (
    AppServer,
    BrowserFailureCollector,
    BrowserSession,
    DESKTOP,
    ReferenceRecorder,
    ROOT,
    V0_2_0_RELEASE_SHA,
    Viewport,
    git_revision,
    reference_capture_command,
    start_app_server,
    stop_app_server,
)
from scripts.check_browser_prerequisites import (
    CHROMIUM_REMEDIATION,
    PreflightReport,
    PrerequisiteError,
    run_preflight,
)


DIRECT_SKIP_REASON = (
    "real-browser prerequisites are unavailable; install them with: "
    f"{CHROMIUM_REMEDIATION}"
)
_TEST_OUTCOMES: dict[str, str] = {}


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "e2e: real-Chromium acceptance tests; excluded from default testpaths",
    )


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == "call":
        _TEST_OUTCOMES[report.nodeid] = report.outcome
    elif report.when in {"setup", "teardown"} and report.failed:
        _TEST_OUTCOMES[report.nodeid] = "failed"
    elif report.when == "setup" and report.skipped:
        _TEST_OUTCOMES[report.nodeid] = "skipped"


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int | pytest.ExitCode,
) -> None:
    output_root = _configured_directory(
        "IOR_E2E_ARTIFACT_DIR",
        ROOT / ".artifacts" / "e2e",
    )
    output_root.mkdir(parents=True, exist_ok=True)
    outcomes = tuple(_TEST_OUTCOMES.values())
    summary = {
        "collected": session.testscollected,
        "passed": outcomes.count("passed"),
        "failed": outcomes.count("failed"),
        "skipped": outcomes.count("skipped"),
        "exit_status": int(exitstatus),
        "explicit_gate": os.environ.get("IOR_E2E_EXPLICIT") == "1",
        "named_tests": sorted(
            {
                nodeid.split("::", maxsplit=1)[1].split(
                    "[",
                    maxsplit=1,
                )[0]
                for nodeid in _TEST_OUTCOMES
                if "::" in nodeid
            }
        ),
    }
    (output_root / "run-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


@pytest.fixture(scope="session", autouse=True)
def browser_prerequisites() -> PreflightReport:
    try:
        return run_preflight()
    except PrerequisiteError as exc:
        if os.environ.get("IOR_E2E_EXPLICIT") == "1":
            pytest.fail(
                f"real-browser prerequisite failure: {exc}",
                pytrace=False,
            )
        pytest.skip(f"{DIRECT_SKIP_REASON} ({exc})")


def _configured_directory(
    variable: str,
    default: Path,
) -> Path:
    value = os.environ.get(variable)
    path = Path(value) if value else default
    if not path.is_absolute():
        path = ROOT / path
    return path


@pytest.fixture(scope="session")
def artifact_dir() -> Path:
    path = _configured_directory(
        "IOR_E2E_ARTIFACT_DIR",
        ROOT / ".artifacts" / "e2e",
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def reference_dir(artifact_dir: Path) -> Path:
    path = _configured_directory(
        "IOR_E2E_REFERENCE_DIR",
        artifact_dir / "reference",
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def app_server(
    browser_prerequisites: PreflightReport,
    artifact_dir: Path,
) -> Generator[AppServer, None, None]:
    server = start_app_server(ROOT, artifact_dir)
    yield server
    stop_app_server(server)


def _requested_viewport(request: pytest.FixtureRequest) -> Viewport:
    callspec = getattr(request.node, "callspec", None)
    if callspec is None:
        return DESKTOP
    candidate = callspec.params.get("viewport", DESKTOP)
    if not isinstance(candidate, Viewport):
        raise TypeError("viewport parameter must be a Viewport")
    return candidate


@pytest.fixture
def browser_session(
    request: pytest.FixtureRequest,
    new_context: Callable[..., Any],
    app_server: AppServer,
    artifact_dir: Path,
) -> Generator[BrowserSession, None, None]:
    viewport = _requested_viewport(request)
    context = new_context(
        base_url=app_server.base_url,
        locale="en-US",
        permissions=["clipboard-read", "clipboard-write"],
        reduced_motion="reduce",
        viewport=viewport.as_dict(),
    )
    context.grant_permissions(
        ["clipboard-read", "clipboard-write"],
        origin=app_server.base_url,
    )
    collector = BrowserFailureCollector(app_server.base_url)
    collector.attach_context(context)
    page = context.new_page()
    collector.attach_page(page)
    session = BrowserSession(
        page=page,
        context=context,
        collector=collector,
        app_server=app_server,
        artifact_dir=artifact_dir,
    )

    yield session

    context.clear_permissions()
    context.close()
    collector.assert_clean()


@pytest.fixture(scope="session")
def reference_recorder(
    browser: Any,
    browser_prerequisites: PreflightReport,
    reference_dir: Path,
) -> Generator[ReferenceRecorder, None, None]:
    for path in reference_dir.glob("*.webp"):
        path.unlink()
    index_path = reference_dir / "index.md"
    if index_path.exists():
        index_path.unlink()
    recorder = ReferenceRecorder(
        reference_dir,
        browser_version=browser.version,
        font_family=browser_prerequisites.font_family,
        font_file=browser_prerequisites.font_file,
        capture_command=reference_capture_command(reference_dir),
        base_sha=git_revision("HEAD"),
        release_sha=V0_2_0_RELEASE_SHA,
    )
    yield recorder
    recorder.finalize()
