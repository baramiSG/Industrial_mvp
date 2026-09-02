from __future__ import annotations

import argparse
import importlib.metadata
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REVISION = "chromium-1234"


def assert_container_chromium() -> Path:
    """Assert the canonical image contains Playwright chromium-1234."""
    if importlib.metadata.version("playwright") != "1.62.0":
        raise RuntimeError("canonical container Playwright must be 1.62.0")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "playwright",
            "install",
            "--dry-run",
            "chromium",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or EXPECTED_REVISION not in result.stdout:
        raise RuntimeError(
            "canonical container must provide chromium-1234"
        )
    executable = (
        Path("/ms-playwright")
        / EXPECTED_REVISION
        / "chrome-linux64"
        / "chrome"
    )
    if not executable.is_file():
        raise RuntimeError(
            "canonical chromium-1234 executable is missing"
        )
    return executable


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("compare", "update"),
        required=True,
    )
    parser.add_argument("--change-ref", default="")
    args = parser.parse_args(argv)
    try:
        executable = assert_container_chromium()
    except (OSError, RuntimeError) as exc:
        print(f"CANONICAL CHROMIUM ASSERTION FAIL: {exc}", file=sys.stderr)
        return 2
    environment = dict(os.environ)
    environment.update(
        {
            "IOR_VISUAL_MODE": args.mode,
            "IOR_BASELINE_CHANGE_REF": args.change_ref,
            "IOR_CHROMIUM_REVISION": EXPECTED_REVISION,
            "PLAYWRIGHT_BROWSERS_PATH": "/ms-playwright",
        }
    )
    print(
        "CANONICAL CHROMIUM ASSERTION PASS "
        f"revision={EXPECTED_REVISION} executable={executable}"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "browser_tests",
            "-m",
            "visual",
            "--browser",
            "chromium",
            "--tracing",
            "retain-on-failure",
            "--screenshot",
            "only-on-failure",
            "--output=/workspace/.artifacts/e2e/playwright",
        ],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
