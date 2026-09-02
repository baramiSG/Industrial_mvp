from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AXE_ROOT = (
    ROOT
    / "browser_tests"
    / "vendor"
    / "axe-core-4.13.0"
)
EXPECTED_VERSIONS = {
    "playwright": "1.62.0",
    "pytest-playwright": "0.9.0",
}
EXPECTED_AXE_VERSION = "4.13.0"
EXPECTED_AXE_SOURCE = (
    "https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz"
)
EXPECTED_AXE_SRI = (
    "sha512-"
    "UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+"
    "XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A=="
)
CHROMIUM_REMEDIATION = (
    "uv run --locked --extra dev --extra e2e "
    "python -m playwright install --with-deps chromium"
)

VersionLookup = Callable[[str], str]
ChromiumPathLookup = Callable[[], Path]
CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


class PrerequisiteError(RuntimeError):
    """Raised when a required real-browser prerequisite is unavailable."""


@dataclass(frozen=True)
class PreflightReport:
    playwright_version: str
    pytest_playwright_version: str
    chromium_executable: Path
    axe_sha256: str
    font_family: str
    font_file: Path


def check_axe_assets(axe_root: Path) -> str:
    source_path = axe_root / "SOURCE.json"
    asset_path = axe_root / "axe.min.js"
    licence_path = axe_root / "LICENSE"
    try:
        source = json.loads(source_path.read_text(encoding="utf-8"))
        payload = asset_path.read_bytes()
        licence = licence_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        raise PrerequisiteError(
            "Vendored axe-core asset, metadata, or licence is unavailable"
        ) from exc

    expected_metadata = {
        "component": "axe-core",
        "version": EXPECTED_AXE_VERSION,
        "source_url": EXPECTED_AXE_SOURCE,
        "registry_sri": EXPECTED_AXE_SRI,
        "disposition": "unmodified vendored distribution",
    }
    for key, expected in expected_metadata.items():
        if source.get(key) != expected:
            raise PrerequisiteError(
                f"axe-core SOURCE.json has invalid {key}"
            )
    digest = hashlib.sha256(payload).hexdigest()
    if source.get("axe_min_sha256") != digest:
        raise PrerequisiteError("axe.min.js SHA-256 mismatch")
    if "Mozilla Public License, version 2.0" not in licence:
        raise PrerequisiteError("axe-core MPL-2.0 licence is missing")
    return digest


def check_arabic_font(command_runner: CommandRunner) -> tuple[str, Path]:
    command = [
        "fc-match",
        "-f",
        "%{family}|%{file}\n",
        ":lang=ar",
    ]
    try:
        result = command_runner(command)
    except FileNotFoundError as exc:
        raise PrerequisiteError(
            "Arabic-capable fontconfig match is unavailable"
        ) from exc
    if result.returncode != 0:
        raise PrerequisiteError(
            "Arabic-capable fontconfig match is unavailable"
        )
    first_match = next(
        (
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ),
        "",
    )
    if "|" not in first_match:
        raise PrerequisiteError(
            "Arabic-capable fontconfig match is unavailable"
        )
    family, raw_path = first_match.split("|", maxsplit=1)
    font_path = Path(raw_path)
    if (
        not family.strip()
        or not font_path.is_file()
        or not os.access(font_path, os.R_OK)
    ):
        raise PrerequisiteError(
            "Arabic-capable fontconfig match is unavailable"
        )
    return family.strip(), font_path


def _default_command_runner(
    command: Sequence[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
    )


def discover_chromium_executable(
    command_runner: CommandRunner,
) -> Path:
    command = [
        sys.executable,
        "-m",
        "playwright",
        "install",
        "--dry-run",
        "chromium",
    ]
    result = command_runner(command)
    if result.returncode != 0:
        raise PrerequisiteError(
            "Unable to inspect the Playwright Chromium installation"
        )
    install_prefix = "Install location:"
    install_root = next(
        (
            Path(line.split(install_prefix, maxsplit=1)[1].strip())
            for line in result.stdout.splitlines()
            if install_prefix in line
        ),
        None,
    )
    if install_root is None:
        raise PrerequisiteError(
            "Unable to inspect the Playwright Chromium installation"
        )
    candidates = (
        install_root / "chrome-linux64" / "chrome",
        install_root / "chrome-linux" / "chrome",
    )
    return next(
        (candidate for candidate in candidates if candidate.is_file()),
        candidates[0],
    )


def _installed_chromium_path() -> Path:
    return discover_chromium_executable(_default_command_runner)


def run_preflight(
    *,
    version_lookup: VersionLookup = importlib.metadata.version,
    chromium_path_lookup: ChromiumPathLookup = _installed_chromium_path,
    axe_root: Path = AXE_ROOT,
    command_runner: CommandRunner = _default_command_runner,
) -> PreflightReport:
    versions: dict[str, str] = {}
    for package, expected in EXPECTED_VERSIONS.items():
        try:
            actual = version_lookup(package)
        except importlib.metadata.PackageNotFoundError as exc:
            raise PrerequisiteError(
                f"Required package is missing: {package}=={expected}"
            ) from exc
        if actual != expected:
            raise PrerequisiteError(
                f"Required package version mismatch: "
                f"{package} expected {expected}, found {actual}"
            )
        versions[package] = actual

    chromium = chromium_path_lookup()
    if (
        not chromium.is_file()
        or not os.access(chromium, os.X_OK)
    ):
        raise PrerequisiteError(
            "Chromium executable is missing for Playwright 1.62.0. "
            f"Install it with: {CHROMIUM_REMEDIATION}"
        )

    axe_sha256 = check_axe_assets(axe_root)
    font_family, font_file = check_arabic_font(command_runner)
    return PreflightReport(
        playwright_version=versions["playwright"],
        pytest_playwright_version=versions["pytest-playwright"],
        chromium_executable=chromium,
        axe_sha256=axe_sha256,
        font_family=font_family,
        font_file=font_file,
    )


def main(
    *,
    version_lookup: VersionLookup = importlib.metadata.version,
    chromium_path_lookup: ChromiumPathLookup = _installed_chromium_path,
    axe_root: Path = AXE_ROOT,
    command_runner: CommandRunner = _default_command_runner,
) -> int:
    try:
        report = run_preflight(
            version_lookup=version_lookup,
            chromium_path_lookup=chromium_path_lookup,
            axe_root=axe_root,
            command_runner=command_runner,
        )
    except PrerequisiteError as exc:
        print(f"BROWSER PREFLIGHT FAIL: {exc}", file=sys.stderr)
        return 1

    print("BROWSER PREFLIGHT PASS")
    print(f"playwright={report.playwright_version}")
    print(f"pytest-playwright={report.pytest_playwright_version}")
    print(f"chromium={report.chromium_executable}")
    print(f"axe_sha256={report.axe_sha256}")
    print(f"font_family={report.font_family}")
    print(f"font_file={report.font_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
