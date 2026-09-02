from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

from PIL import Image, ImageChops
from scripts.visual_metrics import TOLERANCE, calculate_metrics


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = ROOT / "browser_tests" / "baselines" / "v0.3.0"
ARTIFACT_ROOT = ROOT / ".artifacts" / "e2e"
CANONICAL_IMAGE = (
    "mcr.microsoft.com/playwright/python:v1.62.0-noble@"
    "sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d"
)
CHROMIUM_REVISION = "chromium-1234"
LAUNCH_FLAGS = (
    "--font-render-hinting=none",
    "--disable-lcd-text",
    "--force-color-profile=srgb",
)
BASELINE_VIEWPORTS = {
    "desktop-1440x900": (1440, 900),
    "tablet-1024x768": (1024, 768),
}
SCREENS = (
    "journey-a-portfolio-public",
    "journey-a-portfolio-simulated",
    "journey-b-steel-public-workspace",
    "journey-c-steel-simulated-workspace",
    "journey-d-polypropylene-public-workspace",
    "journey-d-polypropylene-simulated-workspace",
    "journey-e-steel-public-dossier",
    "journey-e-steel-simulated-dossier",
    "journey-e-polypropylene-public-dossier",
    "journey-e-polypropylene-simulated-dossier",
)
MAX_FILE_BYTES = 600 * 1024
MAX_TOTAL_BYTES = 12 * 1024 * 1024
VisualMode = Literal["compare", "update"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def normalized_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image.copy()
    if "A" in image.getbands():
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.alpha_composite(image.convert("RGBA"))
        return background.convert("RGB")
    return image.convert("RGB")


def write_lossless_webp(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized_rgb(image).save(
        path,
        format="WEBP",
        lossless=True,
        method=6,
        exact=True,
    )


def compare_images(
    baseline: Image.Image,
    actual: Image.Image,
) -> dict[str, Any]:
    if baseline.mode != "RGB":
        raise ValueError(f"baseline mode must be RGB, found {baseline.mode}")
    current = normalized_rgb(actual)
    if baseline.size != current.size:
        raise ValueError(
            f"image dimensions differ: {baseline.size} != {current.size}"
        )
    difference = ImageChops.difference(baseline, current)
    red, green, blue = difference.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = maximum.point(
        lambda value: 255
        if value > TOLERANCE["channel_delta"]
        else 0
    )
    pixels = baseline.width * baseline.height
    significant = mask.histogram()[255]
    channel_error = sum(
        value * count
        for channel in (red, green, blue)
        for value, count in enumerate(channel.histogram())
    )
    return calculate_metrics(
        significant_pixels=significant,
        total_pixels=pixels,
        absolute_channel_error=channel_error,
        dimensions=baseline.size,
    )


def compare_paths(baseline_path: Path, actual_path: Path) -> dict[str, Any]:
    with Image.open(baseline_path) as baseline:
        baseline.load()
        with Image.open(actual_path) as actual:
            actual.load()
            return compare_images(baseline, actual)


def _source_hashes() -> dict[str, str]:
    static = ROOT / "src" / "ior_mvp" / "static"
    paths = [
        *sorted((ROOT / "src" / "ior_mvp").glob("*.py")),
        static / "index.html",
        static / "app.js",
        static / "styles.css",
        *sorted((static / "css").glob("*.css")),
        *sorted((static / "modules").rglob("*.js")),
        ROOT / "config" / "ui_strings.v1.yaml",
        ROOT / "config" / "evidence_policy.v1.yaml",
    ]
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in paths
    }


def _font_hashes() -> dict[str, str]:
    paths = sorted(
        (
            ROOT
            / "src"
            / "ior_mvp"
            / "static"
            / "assets"
            / "fonts"
        ).rglob("*.woff2")
    )
    return {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in paths
    }


def _expected_matrix() -> set[tuple[str, str, str]]:
    return {
        (locale, viewport, screen)
        for locale in ("en", "ar")
        for viewport in BASELINE_VIEWPORTS
        for screen in SCREENS
    }


def validate_manifest(root: Path = BASELINE_ROOT) -> dict[str, Any]:
    manifest_path = root / "manifest.json"
    digest_path = root / "manifest.sha256"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(manifest_path) != digest_path.read_text(
        encoding="ascii"
    ).strip():
        raise ValueError("visual manifest SHA-256 mismatch")
    entries = payload.get("entries", [])
    matrix = {
        (entry["locale"], entry["viewport"], entry["screen"])
        for entry in entries
    }
    if len(entries) != 40 or matrix != _expected_matrix():
        raise ValueError("visual baseline matrix is incomplete")
    if payload.get("source_tree") != _source_hashes():
        raise ValueError("visual baseline source-tree provenance is stale")
    if payload.get("font_hashes") != _font_hashes():
        raise ValueError("visual baseline font provenance is stale")
    total = 0
    for entry in entries:
        path = root / entry["path"]
        if (
            path.stat().st_size != entry["bytes"]
            or sha256(path) != entry["sha256"]
        ):
            raise ValueError(f"visual baseline integrity mismatch: {path}")
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f"visual baseline file exceeds budget: {path}")
        with Image.open(path) as image:
            if (
                image.mode != "RGB"
                or list(image.size) != entry["dimensions"]
                or image.size
                != BASELINE_VIEWPORTS[entry["viewport"]]
            ):
                raise ValueError(f"visual baseline decode mismatch: {path}")
        total += path.stat().st_size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("visual baseline aggregate exceeds budget")
    return payload


@dataclass
class VisualBaselineSession:
    mode: VisualMode
    browser_version: str
    artifact_root: Path = ARTIFACT_ROOT
    baseline_root: Path = BASELINE_ROOT
    change_ref: str = ""

    def __post_init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.staging = self.baseline_root / ".candidate"
        if self.mode == "compare":
            self.manifest = validate_manifest(self.baseline_root)
        else:
            if os.environ.get("IOR_CANONICAL_VISUAL") != "1":
                raise ValueError("baseline update requires canonical container")
            if os.environ.get("IOR_CHROMIUM_REVISION") != CHROMIUM_REVISION:
                raise ValueError("baseline update requires chromium-1234")
            if not self.change_ref:
                raise ValueError("baseline update requires a change reference")
            shutil.rmtree(self.staging, ignore_errors=True)
            self.staging.mkdir(parents=True)

    def capture(
        self,
        page: Any,
        *,
        locale: str,
        viewport: str,
        screen: str,
        case_id: str | None,
        mode: str,
    ) -> None:
        if (locale, viewport, screen) not in _expected_matrix():
            raise ValueError("unexpected visual baseline identity")
        page.evaluate(
            """async () => {
              await document.fonts.ready;
              const active = document.activeElement;
              if (active instanceof HTMLElement) active.blur();
            }"""
        )
        screenshot = page.screenshot(
            full_page=False,
            animations="disabled",
            caret="hide",
        )
        with Image.open(io.BytesIO(screenshot)) as image:
            actual = normalized_rgb(image)
        relative = Path(locale) / viewport / f"{screen}.webp"
        if self.mode == "update":
            output = self.staging / relative
            write_lossless_webp(actual, output)
            self.entries.append(
                {
                    "path": relative.as_posix(),
                    "locale": locale,
                    "viewport": viewport,
                    "screen": screen,
                    "case_id": case_id,
                    "mode": mode,
                    "dimensions": list(actual.size),
                    "bytes": output.stat().st_size,
                    "sha256": sha256(output),
                }
            )
            return
        baseline = self.baseline_root / relative
        with Image.open(baseline) as expected:
            expected.load()
            metrics = compare_images(expected, actual)
        if metrics["passes"]:
            return
        output_root = (
            self.artifact_root
            / "visual-diffs"
            / locale
            / viewport
            / screen
        )
        output_root.mkdir(parents=True, exist_ok=True)
        write_lossless_webp(actual, output_root / "actual.webp")
        with Image.open(baseline) as expected:
            difference = ImageChops.difference(
                expected,
                actual,
            ).point(lambda value: min(255, value * 4))
            write_lossless_webp(difference, output_root / "diff.webp")
        metrics["baseline"] = relative.as_posix()
        (output_root / "metrics.json").write_bytes(
            canonical_json(metrics)
        )
        raise AssertionError(
            f"visual baseline mismatch: {relative}: {metrics}"
        )

    def finalize(self) -> None:
        if self.mode == "compare":
            return
        identities = {
            (entry["locale"], entry["viewport"], entry["screen"])
            for entry in self.entries
        }
        if len(self.entries) != 40 or identities != _expected_matrix():
            raise ValueError("visual update matrix is incomplete")
        if any(entry["bytes"] > MAX_FILE_BYTES for entry in self.entries):
            raise ValueError("visual update file exceeds budget")
        if sum(entry["bytes"] for entry in self.entries) > MAX_TOTAL_BYTES:
            raise ValueError("visual update aggregate exceeds budget")
        payload = {
            "manifest_version": "1.0",
            "baseline_version": "v0.3.0",
            "generated_on": "2026-09-02",
            "change_ref": self.change_ref,
            "canonical_image": CANONICAL_IMAGE,
            "chromium_revision": CHROMIUM_REVISION,
            "browser_version": self.browser_version,
            "playwright_version": version("playwright"),
            "pytest_playwright_version": version("pytest-playwright"),
            "launch_flags": list(LAUNCH_FLAGS),
            "tolerance": TOLERANCE,
            "source_tree": _source_hashes(),
            "font_hashes": _font_hashes(),
            "entries": sorted(
                self.entries,
                key=lambda entry: (
                    entry["locale"],
                    entry["viewport"],
                    entry["screen"],
                ),
            ),
        }
        manifest = self.staging / "manifest.json"
        manifest.write_bytes(canonical_json(payload))
        (self.staging / "manifest.sha256").write_text(
            sha256(manifest) + "\n",
            encoding="ascii",
        )
        backup = self.baseline_root / ".previous"
        shutil.rmtree(backup, ignore_errors=True)
        backup.mkdir()
        existing = [
            path
            for path in self.baseline_root.iterdir()
            if path not in {self.staging, backup}
        ]
        try:
            for path in existing:
                path.rename(backup / path.name)
            for path in list(self.staging.iterdir()):
                path.rename(self.baseline_root / path.name)
        except BaseException:
            for path in list(backup.iterdir()):
                path.rename(self.baseline_root / path.name)
            raise
        finally:
            shutil.rmtree(self.staging, ignore_errors=True)
            shutil.rmtree(backup, ignore_errors=True)
