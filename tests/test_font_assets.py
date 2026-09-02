from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from ior_mvp.config import PROJECT_ROOT
from scripts import check_browser_prerequisites as preflight


FONT_ROOT = (
    PROJECT_ROOT / "src" / "ior_mvp" / "static" / "assets" / "fonts"
)
LATIN_RANGE = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,"
    "U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,"
    "U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
)
ARABIC_RANGE = (
    "U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,"
    "U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,"
    "U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC,U+102E0-102FB,"
    "U+10E60-10E7E,U+10EC2-10EC4,U+10EFC-10EFF,U+1EE00-1EE03,"
    "U+1EE05-1EE1F,U+1EE21-1EE22,U+1EE24,U+1EE27,U+1EE29-1EE32,"
    "U+1EE34-1EE37,U+1EE39,U+1EE3B,U+1EE42,U+1EE47,U+1EE49,"
    "U+1EE4B,U+1EE4D-1EE4F,U+1EE51-1EE52,U+1EE54,U+1EE57,"
    "U+1EE59,U+1EE5B,U+1EE5D,U+1EE5F,U+1EE61-1EE62,U+1EE64,"
    "U+1EE67-1EE6A,U+1EE6C-1EE72,U+1EE74-1EE77,U+1EE79-1EE7C,"
    "U+1EE7E,U+1EE80-1EE89,U+1EE8B-1EE9B,U+1EEA1-1EEA3,"
    "U+1EEA5-1EEA9,U+1EEAB-1EEBB,U+1EEF0-1EEF1"
)
ASSETS = {
    "noto-sans": {
        "font": "noto-sans-latin-wght-normal.woff2",
        "bytes": 35820,
        "sha256": (
            "51ca196f49a33e79e7870ff88ebd2829a3f627a51e7d690986618f0e7ad2b52d"
        ),
        "license_bytes": 4518,
        "license_sha256": (
            "54ec7b5a35310ad66f9f3091426f7028484cbf9ae1ab5da30122ee412a3009e1"
        ),
        "version": "5.3.0",
        "unicode_range": LATIN_RANGE,
    },
    "noto-sans-arabic": {
        "font": "noto-sans-arabic-arabic-wght-normal.woff2",
        "bytes": 165960,
        "sha256": (
            "ce85091f020920b65762b387b194ef59457ea5b25b760f2dcc35240a94bb8669"
        ),
        "license_bytes": 4380,
        "license_sha256": (
            "91053c23e8a0fe5fc9b5fdbe5ff74ceffd66f6f996c123f1a6ca4c23487c1fff"
        ),
        "version": "5.2.10",
        "unicode_range": ARABIC_RANGE,
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_vendored_fonts_and_licenses_match_exact_bytes_and_hashes() -> None:
    for directory, expected in ASSETS.items():
        root = FONT_ROOT / directory
        font = root / expected["font"]
        license_path = root / "LICENSE"
        assert font.stat().st_size == expected["bytes"]
        assert _sha256(font) == expected["sha256"]
        assert license_path.stat().st_size == expected["license_bytes"]
        assert _sha256(license_path) == expected["license_sha256"]
        assert "SIL OPEN FONT LICENSE Version 1.1" in license_path.read_text(
            encoding="utf-8"
        )


def test_font_source_metadata_records_exact_fontsource_unicode_ranges_and_local_urls() -> None:
    for directory, expected in ASSETS.items():
        source = json.loads(
            (FONT_ROOT / directory / "SOURCE.json").read_text(encoding="utf-8")
        )
        assert source["package_version"] == expected["version"]
        assert source["font_sha256"] == expected["sha256"]
        assert source["license_sha256"] == expected["license_sha256"]
        assert source["unicode_range"] == expected["unicode_range"]
        assert source["runtime_url"].startswith("/static/assets/fonts/")
        assert "cdn.jsdelivr.net/npm/@fontsource-variable/" in source[
            "source_url"
        ]
    notices = (FONT_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "@fontsource-variable/noto-sans@5.3.0" in notices
    assert "@fontsource-variable/noto-sans-arabic@5.2.10" in notices
    assert "OFL-1.1" in notices


def test_browser_preflight_requires_intended_product_fonts() -> None:
    assets = getattr(preflight, "EXPECTED_FONT_ASSETS", {})

    assert set(assets) == {"IOR Noto Sans", "IOR Noto Sans Arabic"}
    assert assets["IOR Noto Sans"]["sha256"] == ASSETS["noto-sans"]["sha256"]
    assert (
        assets["IOR Noto Sans Arabic"]["sha256"]
        == ASSETS["noto-sans-arabic"]["sha256"]
    )
    source = (
        PROJECT_ROOT / "scripts" / "check_browser_prerequisites.py"
    ).read_text(encoding="utf-8")
    assert "fc-match" in source
    assert "diagnostic" in source.lower()
    assert "check_product_fonts" in source


def _parse_ranges(value: str) -> list[tuple[int, int]]:
    parsed: list[tuple[int, int]] = []
    for item in value.split(","):
        bounds = item.removeprefix("U+").split("-")
        start = int(bounds[0], 16)
        parsed.append((start, int(bounds[-1], 16)))
    return parsed


def _covered(character: str) -> bool:
    point = ord(character)
    ranges = _parse_ranges(LATIN_RANGE) + _parse_ranges(ARABIC_RANGE)
    return point < 128 or any(start <= point <= end for start, end in ranges)


def test_catalogue_and_renderer_literals_are_covered_by_vendored_unicode_ranges() -> None:
    catalogue = yaml.safe_load(
        (PROJECT_ROOT / "config" / "ui_strings.v1.yaml").read_text(
            encoding="utf-8"
        )
    )
    values = [
        value
        for strings in catalogue["strings"].values()
        for value in strings.values()
    ]
    literal_pattern = re.compile(r"""["']([^"'\n]+)["']""")
    sources = [
        path.read_text(encoding="utf-8")
        for path in sorted(
            (
                PROJECT_ROOT / "src" / "ior_mvp" / "static" / "modules"
            ).rglob("*.js")
        )
    ]
    sources.append(
        (
            PROJECT_ROOT / "src" / "ior_mvp" / "dossier.py"
        ).read_text(encoding="utf-8")
    )
    literals = [
        value
        for source in sources
        for value in literal_pattern.findall(source)
    ]
    uncovered = sorted(
        {
            character
            for value in [*values, *literals]
            for character in value
            if not _covered(character)
        }
    )
    assert uncovered == []


def test_uncovered_chrome_symbols_use_accessible_svg_or_css_glyphs() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html",
            *sorted(
                (
                    PROJECT_ROOT
                    / "src"
                    / "ior_mvp"
                    / "static"
                    / "modules"
                ).rglob("*.js")
            ),
            PROJECT_ROOT / "src" / "ior_mvp" / "dossier.py",
        ]
    )

    assert not any(symbol in sources for symbol in ("→", "✓", "✕"))
    assert "transitionIcon" in sources
    assert "statusIcon" in sources
    assert 'role="img"' in sources
    assert "integrity.transition_aria" in sources
    assert "extraction.pass_aria" in sources
    assert "extraction.fail_aria" in sources
