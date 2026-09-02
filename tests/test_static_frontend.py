from __future__ import annotations

import re
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


def test_frontend_contains_evidence_mode_and_arabic_support() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert "Public evidence" in html
    assert "Ministry simulation" in html
    assert 'dir="rtl"' in html
    assert "Decision workspace" in html


def test_frontend_has_no_external_cdn_dependency() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert "cdnjs" not in html
    assert "unpkg" not in html
    assert "jsdelivr" not in html
    assert "fonts.googleapis" not in html


def test_synthetic_warning_style_exists() -> None:
    css = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "styles.css").read_text(encoding="utf-8")
    assert ".synthetic-warning" in css
    assert ".synthetic-row" in css


def _relative_luminance(color: str) -> float:
    channels = [
        int(color[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def _contrast_ratio(first: str, second: str) -> float:
    first_luminance = _relative_luminance(first)
    second_luminance = _relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def test_integrity_banner_renders_authority_provenance_safely() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    for expression in (
        "props.authority.methodology",
        "methodology.sha256_prefix",
        "props.authority.project_version",
        "versions.thresholds",
        "versions.sector_profiles",
        "versions.evidence_policy",
    ):
        assert expression in app_js
    assert "escapeHtml(methodology.sha256_prefix)" in app_js
    assert "escapeHtml(versions.evidence_policy)" in app_js


def test_workspace_region_names_authority_provenance() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "index.html"
    ).read_text(encoding="utf-8")
    assert (
        'role="region" aria-label="Decision analysis and '
        'authority provenance"'
    ) in html


def test_authority_caption_uses_design_token_only() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")
    block = css.split(
        ".integrity-banner .integrity-authority",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]

    assert "var(--teal-soft)" in block
    assert "#" not in block


def test_authority_caption_meets_text_contrast_on_banner() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")
    foreground_match = re.search(
        r"--teal-soft:\s*(#[0-9a-fA-F]{6})",
        css,
    )
    assert foreground_match is not None
    banner = css.split(
        ".integrity-banner {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    backgrounds = re.findall(
        r"#[0-9a-fA-F]{6}",
        banner,
    )

    assert len(backgrounds) == 2
    assert all(
        _contrast_ratio(
            foreground_match.group(1),
            background,
        )
        >= 4.5
        for background in backgrounds
    )


def _app_function(source: str, name: str) -> str:
    assert f"function {name}" in source
    return source.split(
        f"function {name}",
        maxsplit=1,
    )[1].split("\n}", maxsplit=1)[0]


def test_rule_ledger_visibly_labels_synthetic_rows() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    helper = _app_function(app_js, "ruleBoundaryChip")
    ledger = _app_function(app_js, "renderRuleLedger")
    methodology = _app_function(app_js, "renderMethodology")

    assert "row.synthetic_flag" in helper
    assert "escapeHtml(row.display_label)" in helper
    assert "exec-chip exec-DEGRADED" in helper
    assert "SYNTHETIC" in helper
    for block in (ledger, methodology):
        assert '"synthetic-row"' in block
        assert "ruleBoundaryChip(row)" in block


def test_integrity_banner_displays_public_and_active_states_together() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    banner = _app_function(app_js, "renderIntegrityBanner")

    assert "stateChip(props.real_state)" in banner
    assert "stateChip(props.active_state)" in banner
    assert "props.mode === \"simulated\"" in banner


def test_decision_actions_exposes_dossier_html_action() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    actions = _app_function(app_js, "renderDecisionActions")

    assert "data-dossier-html" in actions
    assert "Open dossier" in actions
    assert "<button" in actions


def test_accessibility_text_tokens_meet_wcag_aa_on_used_surfaces() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")

    def token(name: str) -> str:
        match = re.search(
            rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})",
            css,
        )
        assert match is not None
        return match.group(1)

    pairs = (
        (token("teal-text"), "#edf3f6"),
        (token("teal-text"), "#ffffff"),
        (token("ink-600"), "#e8eef2"),
        (token("ink-600"), "#f4f7f9"),
        (token("ink-500"), "#f5f8fa"),
        (token("ink-500"), "#ffffff"),
        (token("gold-text"), "#ffffff"),
        (token("teal-on-dark"), "#071726"),
    )
    assert all(
        _contrast_ratio(foreground, background) >= 4.5
        for foreground, background in pairs
    )
    assert (
        ".exec-DISABLED { background: #edf1f4; "
        "color: var(--ink-700); }"
        in css
    )
    assert ".fire-na { color: var(--gold-text); }" in css
    assert (
        ".hero-section .eyebrow, .governance-section .eyebrow "
        "{ color: var(--teal-on-dark); }"
        in css
    )


def test_workspace_heading_can_wrap_without_page_overflow() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")
    heading = css.split(
        ".workspace-heading {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    tools = css.split(
        ".workspace-tools {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    tablet = css.split(
        "@media (max-width: 1180px) {",
        maxsplit=1,
    )[1].split(
        "@media (max-width: 900px) {",
        maxsplit=1,
    )[0]

    assert "flex-wrap: wrap" in heading
    assert "min-width: 0" in tools
    assert "max-width: 100%" in tools
    assert ".workspace-heading" in tablet
    assert "flex-direction: column" in tablet
    assert ".workspace-tools { width: 100%;" in tablet
    assert "select { width: 100%;" in tablet


def test_reduced_motion_context_disables_transient_colour_states() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")

    assert "@media (prefers-reduced-motion: reduce)" in css
    block = css.split(
        "@media (prefers-reduced-motion: reduce)",
        maxsplit=1,
    )[1]
    assert "transition-duration: 0s !important" in block
    assert "animation-duration: 0s !important" in block
    assert "scroll-behavior: auto !important" in block
