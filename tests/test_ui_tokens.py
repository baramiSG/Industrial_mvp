from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT


STATIC_ROOT = PROJECT_ROOT / "src" / "ior_mvp" / "static"
CSS_ROOT = STATIC_ROOT / "css"
TOKENS = CSS_ROOT / "tokens.css"
CHECKER = PROJECT_ROOT / "scripts" / "check_ui_contracts.py"
TOKEN_FAMILIES = {
    "color",
    "space",
    "size",
    "layout",
    "breakpoint",
    "border",
    "radius",
    "shadow",
    "font",
    "z",
    "motion",
    "gradient",
}


def _run_checker(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *arguments],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _tokens() -> dict[str, str]:
    source = TOKENS.read_text(encoding="utf-8")
    return dict(
        re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", source)
    )


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    return tuple(
        int(value[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )


def _luminance(value: str) -> float:
    channels = _hex_to_rgb(value)
    linear = tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    )
    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def _contrast(first: str, second: str) -> float:
    values = sorted((_luminance(first), _luminance(second)))
    return (values[1] + 0.05) / (values[0] + 0.05)


def test_token_layer_declares_every_required_token_family() -> None:
    names = set(_tokens())

    assert {
        family
        for family in TOKEN_FAMILIES
        if any(name.startswith(f"--{family}-") for name in names)
    } == TOKEN_FAMILIES


def test_every_production_stylesheet_is_literal_free_outside_tokens() -> None:
    result = _run_checker()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "UI CONTRACT CHECK PASS" in result.stdout


@pytest.mark.parametrize("locale", ["en", "ar"])
def test_rendered_dossier_css_is_literal_free_outside_tokens(
    locale: str,
) -> None:
    response = TestClient(app).get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=simulated&locale={locale}"
    )

    assert response.status_code == 200
    style = re.search(r"<style>(.*?)</style>", response.text, re.DOTALL)
    assert style is not None
    fixture = PROJECT_ROOT / ".artifacts" / "dossier-contract.css"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(style.group(1), encoding="utf-8")
    try:
        result = _run_checker("--scan-rendered-css", str(fixture))
    finally:
        fixture.unlink(missing_ok=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_only_bounded_capability_fill_inline_style_is_allowed() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((STATIC_ROOT / "modules").rglob("*.js"))
    )
    styles = re.findall(r"""style=["']([^"']+)["']""", sources)

    assert styles == ["--capability-fill:${fill}%"]
    assert "Math.max(0, Math.min(100," in sources


@pytest.mark.parametrize(
    ("payload", "category"),
    [
        (".x { color: #fff; }", "colour"),
        (".x { margin-inline: 1px; }", "length"),
        (".x { font-size: 1rem; }", "font"),
        (".x { box-shadow: 0 1px 2px #000; }", "shadow"),
        (".x { z-index: 2; }", "z-index"),
        (".x { margin-left: 0; }", "physical-direction"),
    ],
)
def test_scanner_rejects_colour_length_font_shadow_z_and_physical_direction_literals(
    tmp_path: Path,
    payload: str,
    category: str,
) -> None:
    fixture = tmp_path / "fixture.css"
    fixture.write_text(payload, encoding="utf-8")

    result = _run_checker("--scan-css", str(fixture))

    assert result.returncode == 1
    assert category in result.stdout


def test_accessibility_token_pairs_resolve_to_wcag_aa() -> None:
    tokens = _tokens()
    pairs = (
        ("--color-accent-text", "--color-paper"),
        ("--color-muted", "--color-surface"),
        ("--color-warning-text", "--color-surface"),
        ("--color-on-dark", "--color-navy-950"),
        ("--color-synthetic-text", "--color-synthetic-bg"),
    )
    for foreground, background in pairs:
        assert _contrast(tokens[foreground], tokens[background]) >= 4.5
