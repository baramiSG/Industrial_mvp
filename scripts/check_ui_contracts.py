from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ROOT / "src" / "ior_mvp" / "static"
TOKENS_PATH = STATIC_ROOT / "css" / "tokens.css"
CATALOGUE_PATH = ROOT / "config" / "ui_strings.v1.yaml"
ALLOWED_INLINE_STYLE = "--capability-fill:${fill}%"

COLOR_PATTERN = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|(?:rgb|rgba|hsl|hsla)\s*\(",
)
LENGTH_PATTERN = re.compile(
    r"(?<![-\w.])(?:[1-9]\d*(?:\.\d+)?|0?\.\d+)"
    r"(?:px|rem|em|%|vh|vw|vmin|vmax|ch|pt|ms|s)\b",
)
PHYSICAL_PATTERN = re.compile(
    r"(?m)^\s*(?:left|right|margin-left|margin-right|padding-left|"
    r"padding-right|inset-left|inset-right|border-left|border-right)"
    r"\s*:|text-align\s*:\s*(?:left|right)\b",
)
STYLE_PATTERN = re.compile(r"""style\s*=\s*["']([^"']*)["']""")
DECLARATION_PATTERN = re.compile(
    r"([a-zA-Z-]+)\s*:\s*([^;{}]+);",
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    category: str
    detail: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.category}: {self.detail}"


def _line(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def _finding(
    path: str,
    source: str,
    match: re.Match[str],
    category: str,
) -> Finding:
    return Finding(
        path=path,
        line=_line(source, match.start()),
        category=category,
        detail=match.group(0).strip(),
    )


def scan_css(source: str, *, path: str) -> list[Finding]:
    """Scan one non-token stylesheet for raw visual values."""
    findings: set[Finding] = set()
    for match in PHYSICAL_PATTERN.finditer(source):
        findings.add(_finding(path, source, match, "physical-direction"))
    for match in COLOR_PATTERN.finditer(source):
        findings.add(_finding(path, source, match, "colour"))
    for match in LENGTH_PATTERN.finditer(source):
        findings.add(_finding(path, source, match, "length"))
    for match in re.finditer(r"(?m)^\s*--[a-z0-9-]+\s*:", source):
        findings.add(_finding(path, source, match, "custom-property"))
    for match in DECLARATION_PATTERN.finditer(source):
        name, value = match.groups()
        normalized = name.lower()
        if normalized in {
            "left",
            "right",
            "margin-left",
            "margin-right",
            "padding-left",
            "padding-right",
            "inset-left",
            "inset-right",
            "border-left",
            "border-right",
        } or (
            normalized == "text-align"
            and value.strip().lower() in {"left", "right"}
        ):
            findings.add(
                _finding(path, source, match, "physical-direction")
            )
        if normalized in {
            "font",
            "font-family",
            "font-size",
            "font-weight",
            "line-height",
            "letter-spacing",
        } and "var(--" not in value and normalized != "font":
            findings.add(_finding(path, source, match, "font"))
        if normalized == "font" and value.strip() != "inherit":
            findings.add(_finding(path, source, match, "font"))
        if normalized == "box-shadow" and "var(--" not in value:
            findings.add(_finding(path, source, match, "shadow"))
        if normalized == "z-index" and "var(--" not in value:
            findings.add(_finding(path, source, match, "z-index"))
        if normalized == "border-radius" and "var(--" not in value:
            findings.add(_finding(path, source, match, "radius"))
    return sorted(findings)


def _matching_brace(source: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced token layer")


def without_embedded_tokens(source: str) -> str:
    """Blank an embedded @layer tokens block while preserving line numbers."""
    marker = re.search(r"@layer\s+tokens\s*\{", source)
    if marker is None:
        raise ValueError("rendered CSS does not embed @layer tokens")
    opening = source.find("{", marker.start())
    closing = _matching_brace(source, opening)
    blank = "".join("\n" if char == "\n" else " " for char in source[: closing + 1])
    return blank + source[closing + 1 :]


def scan_inline_styles(paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        display = path.relative_to(ROOT).as_posix()
        for match in STYLE_PATTERN.finditer(source):
            if match.group(1) != ALLOWED_INLINE_STYLE:
                findings.append(
                    Finding(
                        path=display,
                        line=_line(source, match.start()),
                        category="inline-style",
                        detail=match.group(1),
                    )
                )
    return sorted(findings)


def project_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted((STATIC_ROOT / "css").glob("*.css")):
        if path == TOKENS_PATH:
            continue
        findings.extend(
            scan_css(
                path.read_text(encoding="utf-8"),
                path=path.relative_to(ROOT).as_posix(),
            )
        )
    findings.extend(
        scan_inline_styles(
            [
                STATIC_ROOT / "index.html",
                *sorted((STATIC_ROOT / "modules").rglob("*.js")),
            ]
        )
    )
    return sorted(findings)


def catalogue_payload() -> dict:
    payload = yaml.safe_load(CATALOGUE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("UI catalogue must be a mapping")
    strings = payload.get("strings")
    if not isinstance(strings, dict):
        raise ValueError("UI catalogue strings must be a mapping")
    return payload


def catalogue_keys() -> set[str]:
    strings = catalogue_payload()["strings"]
    if not all(isinstance(strings.get(locale), dict) for locale in ("en", "ar")):
        raise ValueError("UI catalogue locales must be mappings")
    if set(strings["en"]) != set(strings["ar"]):
        raise ValueError("UI catalogue key parity failed")
    return set(strings["en"])


def referenced_ui_keys(keys: set[str]) -> set[str]:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    referenced = set(
        re.findall(r'data-i18n="([a-z0-9._-]+)"', html)
    )
    referenced.update(
        re.findall(
            r'data-i18n-attr="[^":]+:([a-z0-9._-]+)"',
            html,
        )
    )
    paths = [
        STATIC_ROOT / "app.js",
        *sorted((STATIC_ROOT / "modules").rglob("*.js")),
        ROOT / "src" / "ior_mvp" / "dossier.py",
    ]
    literal_pattern = re.compile(r"""["']([a-z][a-z0-9._-]+)["']""")
    for path in paths:
        source = path.read_text(encoding="utf-8")
        referenced.update(
            value
            for value in literal_pattern.findall(source)
            if value in keys
        )
    return referenced


def catalogue_usage_findings() -> list[Finding]:
    keys = catalogue_keys()
    used = referenced_ui_keys(keys)
    findings = [
        Finding("config/ui_strings.v1.yaml", 1, "unused-key", key)
        for key in sorted(keys - used)
    ]
    findings.extend(
        Finding("src/ior_mvp/static", 1, "missing-key", key)
        for key in sorted(used - keys)
    )
    return findings


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.visible: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.hidden_depth:
            return
        text = " ".join(data.split())
        if text:
            self.visible.append(text)


def copy_findings() -> list[Finding]:
    findings: list[Finding] = []
    html_path = STATIC_ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    parser = _VisibleTextParser()
    parser.feed(html)
    for text in parser.visible:
        if re.search(r"[A-Za-z\u0600-\u06ff]", text):
            findings.append(
                Finding(
                    html_path.relative_to(ROOT).as_posix(),
                    1,
                    "hard-coded-copy",
                    text,
                )
            )
    payload = catalogue_payload()
    values = {
        value
        for locale in ("en", "ar")
        for value in payload["strings"][locale].values()
        if len(value) >= 4
    }
    production_paths = [
        html_path,
        STATIC_ROOT / "app.js",
        *sorted((STATIC_ROOT / "modules").rglob("*.js")),
        ROOT / "src" / "ior_mvp" / "dossier.py",
    ]
    for path in production_paths:
        source = path.read_text(encoding="utf-8")
        for match in re.finditer(r"""["']([^"'\n]+)["']""", source):
            value = match.group(1)
            if value in values:
                findings.append(
                    Finding(
                        path.relative_to(ROOT).as_posix(),
                        _line(source, match.start()),
                        "catalogue-copy",
                        value,
                    )
                )
        for pattern in (
            r"""\.textContent\s*=\s*["']([^"']*[A-Za-z\u0600-\u06ff][^"']*)["']""",
            r"""toast\(\s*["']([^"']*[A-Za-z\u0600-\u06ff][^"']*)["']""",
        ):
            for match in re.finditer(pattern, source):
                findings.append(
                    Finding(
                        path.relative_to(ROOT).as_posix(),
                        _line(source, match.start()),
                        "hard-coded-copy",
                        match.group(1),
                    )
                )
    return sorted(set(findings))


def _print_findings(findings: Sequence[Finding]) -> int:
    if findings:
        print("UI CONTRACT CHECK FAIL")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1
    print("UI CONTRACT CHECK PASS")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--scan-css", type=Path)
    group.add_argument("--scan-rendered-css", type=Path)
    group.add_argument("--check-catalogue-usage", action="store_true")
    group.add_argument("--check-copy", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.scan_css:
            source = args.scan_css.read_text(encoding="utf-8")
            return _print_findings(scan_css(source, path=str(args.scan_css)))
        if args.scan_rendered_css:
            source = args.scan_rendered_css.read_text(encoding="utf-8")
            stripped = without_embedded_tokens(source)
            return _print_findings(
                scan_css(stripped, path=str(args.scan_rendered_css))
            )
        if args.check_catalogue_usage:
            findings = catalogue_usage_findings()
            if findings:
                return _print_findings(findings)
            print("UI CONTRACT CHECK PASS: catalogue usage exact")
            return 0
        if args.check_copy:
            findings = copy_findings()
            if findings:
                return _print_findings(findings)
            print("UI CONTRACT CHECK PASS: visible copy catalogue-sourced")
            return 0
        if not TOKENS_PATH.is_file():
            raise FileNotFoundError(TOKENS_PATH)
        findings = [
            *project_findings(),
            *catalogue_usage_findings(),
            *copy_findings(),
        ]
        return _print_findings(findings)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(
            f"UI CONTRACT CHECK ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
