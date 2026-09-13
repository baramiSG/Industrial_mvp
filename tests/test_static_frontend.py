from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


STATIC_ROOT = PROJECT_ROOT / "src" / "ior_mvp" / "static"
CSS_ROOT = STATIC_ROOT / "css"


def _module_source(relative: str) -> str:
    return (STATIC_ROOT / relative).read_text(encoding="utf-8")


def _css_source(relative: str) -> str:
    return (CSS_ROOT / relative).read_text(encoding="utf-8")


def _token(name: str) -> str:
    match = re.search(
        rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})",
        _css_source("tokens.css"),
    )
    assert match is not None
    return match.group(1)


def test_frontend_contains_evidence_mode_and_arabic_support() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert 'data-i18n="mode.public"' in html
    assert 'data-i18n="mode.simulated"' in html
    assert '<html lang="en" dir="ltr">' in html
    assert 'data-i18n="workspace.title"' in html
    assert "data-locale-switch" in html


def test_frontend_has_no_external_cdn_dependency() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert "cdnjs" not in html
    assert "unpkg" not in html
    assert "jsdelivr" not in html
    assert "fonts.googleapis" not in html


def test_demo_shell_has_no_engineer_docs_anchor() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'href="/docs"' not in html
    assert "data-locale-switch" in html


def test_synthetic_warning_style_exists() -> None:
    css = _css_source("workspace.css")
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
    app_js = _module_source("modules/renderers/integrity.js")
    for expression in (
        "props.authority.methodology",
        "methodology.sha256_prefix",
        "props.authority.project_version",
        "versions.thresholds",
        "versions.sector_profiles",
        "versions.evidence_policy",
    ):
        assert expression in app_js
    assert "technical(methodology.sha256_prefix)" in app_js
    assert "technical(versions.evidence_policy)" in app_js
    assert "technical(versions.ui_strings)" in app_js


def test_workspace_region_names_authority_provenance() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "index.html"
    ).read_text(encoding="utf-8")
    assert (
        'role="region" aria-label="" '
        'data-i18n-attr="aria-label:workspace.region_aria"'
    ) in html


def test_authority_caption_uses_design_token_only() -> None:
    css = _css_source("workspace.css")
    block = css.split(
        ".integrity-banner .integrity-authority",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]

    assert "var(--color-accent-soft)" in block
    assert "#" not in block


def test_authority_caption_meets_text_contrast_on_banner() -> None:
    foreground = _token("color-accent-soft")
    gradient = re.search(
        r"--gradient-banner:\s*([^;]+);",
        _css_source("tokens.css"),
    )
    assert gradient is not None
    backgrounds = re.findall(r"#[0-9a-fA-F]{6}", gradient.group(1))
    assert len(backgrounds) == 2
    assert all(
        _contrast_ratio(
            foreground,
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
    helper = _app_function(
        _module_source("modules/dom.js"),
        "ruleBoundaryChip",
    )
    ledger = _app_function(
        _module_source("modules/renderers/rules.js"),
        "renderRuleLedger",
    )
    methodology = _app_function(
        _module_source("modules/methodology.js"),
        "renderMethodology",
    )

    assert "row.synthetic_flag" in helper
    assert "syntheticLabels(row.display_labels" in helper
    assert "exec-chip exec-DEGRADED" in helper
    for block in (ledger, methodology):
        assert '"synthetic-row"' in block
        assert "ruleBoundaryChip(row)" in block


def test_governance_synthetic_disclosure_uses_policy_bundle() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    i18n = _module_source("modules/i18n.js")

    assert 'data-policy-labels="governance"' in html
    assert "bundle.synthetic_labels" in i18n
    assert "applyPolicyLabels" in i18n


def test_integrity_banner_displays_public_and_active_states_together() -> None:
    app_js = _module_source("modules/renderers/integrity.js")
    banner = _app_function(app_js, "renderIntegrityBanner")

    assert "decisionChip(props.real_state" in banner
    assert "decisionChip(props.active_state" in banner
    assert "props.mode === \"simulated\"" in banner


def test_metric_grid_hhi_note_uses_partner_detail_catalogue_keys_and_never_renders_zero(
) -> None:
    source = _module_source("modules/renderers/decision.js")
    note = _app_function(source, "hhiNote")
    grid = _app_function(source, "renderMetricGrid")

    assert "hhiNote(hhi, threshold, partnerDetail)" in source
    assert "PARTNER_DETAIL_MISSING" in note
    assert "PARTNER_TRADE_OBSERVED_ZERO" in note
    assert 't("metric.hhi_partner_detail_missing"' in note
    assert 't("metric.hhi_partner_trade_zero")' in note
    assert 't("metric.hhi_unavailable")' in note
    assert "props.partner_detail" in grid
    assert (
        'technical(hhi == null ? t("common.unavailable") : number(hhi, 2))'
        in grid
    )
    assert "hhi == null ? 0" not in grid


def test_trade_chart_path_breaks_at_unavailable_points_instead_of_emitting_nan(
) -> None:
    source = _module_source("modules/renderers/trade.js")
    executable = "\n".join(source.splitlines()[3:])
    script = (
        executable
        + '\nconsole.log(chartPath([1, "UNAVAILABLE", 3], '
        + "(index) => index, (value) => value));\n"
    )

    result = subprocess.run(
        ["node", "--input-type=module"],
        input=script,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "M0,1 M2,3"


def test_decision_actions_exposes_dossier_html_action() -> None:
    app_js = _module_source("modules/renderers/evidence.js")
    actions = _app_function(app_js, "renderDecisionActions")

    assert "data-dossier-html" in actions
    assert 't("actions.open_dossier")' in actions
    assert "<button" in actions


def test_accessibility_text_tokens_meet_wcag_aa_on_used_surfaces() -> None:
    pairs = (
        (_token("color-accent-text"), _token("color-workspace")),
        (_token("color-accent-text"), _token("color-surface")),
        (_token("color-muted"), _token("color-control-bg")),
        (_token("color-muted"), _token("color-paper")),
        (_token("color-muted-strong"), _token("color-soft")),
        (_token("color-muted-strong"), _token("color-surface")),
        (_token("color-warning-text"), _token("color-surface")),
        (_token("color-on-dark"), _token("color-navy-950")),
    )
    assert all(
        _contrast_ratio(foreground, background) >= 4.5
        for foreground, background in pairs
    )
    workspace = _css_source("workspace.css")
    overview = _css_source("overview.css")
    assert "color: var(--color-navy-700);" in workspace
    assert "color: var(--color-warning-text);" in workspace
    assert "color: var(--color-on-dark);" in overview


def test_workspace_heading_can_wrap_without_page_overflow() -> None:
    css = _css_source("workspace.css")
    heading = css.split(
        ".workspace-heading {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    tools = css.split(
        ".workspace-tools {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    tablet = _css_source("tokens.css").split(
        "@media (max-width: 1180px) {",
        maxsplit=1,
    )[1].split(
        "@media (max-width: 900px) {",
        maxsplit=1,
    )[0]

    assert "flex-wrap: wrap" in heading
    assert "min-inline-size: var(--space-0)" in tools
    assert "max-inline-size: var(--size-full)" in tools
    assert "--layout-heading-direction: column" in tablet
    assert "--layout-workspace-tools-width: var(--size-full)" in tablet
    assert "--layout-select-width: var(--size-full)" in tablet


def test_bidi_state_chips_and_sticky_section_anchors_use_tokens() -> None:
    workspace = _css_source("workspace.css")
    overview = _css_source("overview.css")
    tokens = _css_source("tokens.css")

    state_chip = workspace.split(
        ".state-chip {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    assert "gap: var(--space-4)" in state_chip
    assert "scroll-margin-block-start: var(--size-topbar-min)" in overview
    assert ':root[dir="rtl"] .transition-icon' in workspace
    assert "transform: var(--motion-rtl-flip)" in workspace
    assert "--motion-rtl-flip: scaleX(-1)" in tokens


def test_source_language_code_islands_use_vendored_interface_font() -> None:
    base = _css_source("base.css")
    dossier = _css_source("dossier.css")

    assert (
        ".source-language-island,\ncode {\n"
        "  font-family: var(--font-family-interface);"
    ) in base
    assert (
        ".source-language-island,\ncode {\n"
        "  font-family: var(--font-family-interface);"
    ) in dossier


def test_reduced_motion_context_disables_transient_colour_states() -> None:
    css = _css_source("tokens.css")

    assert "@media (prefers-reduced-motion: reduce)" in css
    block = css.split(
        "@media (prefers-reduced-motion: reduce)",
        maxsplit=1,
    )[1]
    assert "--motion-duration: 0s" in block
    assert "--motion-shimmer: none" in block
    assert "--motion-scroll: auto" in block


def test_public_decision_renderer_uses_structured_localized_segments() -> None:
    dom = _module_source("modules/dom.js")
    decision = _module_source("modules/renderers/decision.js")
    evidence = _module_source("modules/renderers/evidence.js")

    assert "export function narrativeEntry" in dom
    assert "ltr_isolate" in dom
    assert 'lang="en" dir="ltr"' in dom
    assert "props.localized_narrative?.[state.locale]" in decision
    assert "narrativeEntry(localized.headline" in decision
    assert "sourceCaption()" in decision
    assert "props.localized_missing_facts?.[state.locale]" in evidence
    assert "narrativeEntry(item)" in evidence


def test_public_localization_does_not_change_simulation_source_islands() -> None:
    decision = _module_source("modules/renderers/decision.js")
    evidence = _module_source("modules/renderers/evidence.js")

    assert "sourceIsland(props.headline)" in decision
    assert "sourceIsland(props.rationale)" in decision
    assert "sourceIsland(props.route" in decision
    assert "sourceIsland(item)" in evidence


def test_shell_has_screening_nav_item_and_section() -> None:
    html = _module_source("index.html")

    assert 'data-target="screening"' in html
    assert "<span>06</span>" in html
    assert 'data-i18n="nav.screening"' in html
    assert '<section id="screening"' in html
    assert 'id="screening-view"' in html
    assert 'id="screening-evidence"' in html
    assert html.index('id="screening-view"') < html.index(
        'id="screening-evidence"'
    )
    assert 'data-i18n="screening.boundary_public_only"' in html


def test_screening_modules_render_explicit_states_and_no_ordinal() -> None:
    queue = _module_source("modules/screening/queue.js")
    summary = _module_source("modules/screening/summary.js")
    record = _module_source("modules/screening/record.js")
    record_evidence = _module_source("modules/screening/record-evidence.js")
    evidence = _module_source("modules/screening/evidence.js")
    api = _module_source("modules/api.js")
    index = _module_source("modules/screening/index.js")
    all_screening = "\n".join(
        (queue, summary, record, record_evidence, evidence, index)
    )

    assert 't("screening.queue.empty")' in queue
    assert "screening.queue.pareto_rank" in queue
    assert "data-hs6=" in queue
    assert "data-screening-page=" in queue
    assert not re.search(r"index\s*\+\s*1", queue)
    assert "screening.universe.unavailable_body" in summary
    assert "screening.universe.partial_body" in summary
    assert "data-queue-id=" in summary
    assert "renderCoverageAccounting" in summary
    assert "passport-" not in summary
    assert "renderEvidenceBasis" in record
    assert "screening.record.no_record_passports" in record_evidence
    assert 'data-record-passports="none"' in record_evidence
    assert 'data-passport-scope="record"' in record_evidence
    assert '<a href="http' not in record_evidence
    assert 'id="passport-' in evidence
    assert 'tabindex="-1"' in evidence
    assert "data-passport-ref" in evidence
    assert 'data-passport-scope="universe"' in evidence
    assert "screening.evidence.passport_detail_not_exposed" in evidence
    assert "screening.evidence.no_snapshot" in evidence
    assert "screening.evidence.unit_without_passport" in evidence
    assert 'data-evidence-state="none"' in evidence
    assert '<a href="http' not in evidence
    assert "screeningEvidenceEndpoint" in api
    assert "Promise.all" in index
    assert "screeningEvidenceEndpoint()" in index
    assert not re.search(
        r"passport_id\s*[:=]\s*`?\$\{",
        all_screening,
    )


def test_screening_need_codes_are_rendered_only_through_labels() -> None:
    evidence = _module_source("modules/screening/record-evidence.js")

    assert "screeningLabel(\"need\", need)" in evidence
    assert "technicalToken(need)" not in evidence


def test_screening_labels_fail_closed_on_unknown_codes() -> None:
    labels = _module_source("modules/screening/labels.js")

    assert "UI_CATALOGUE_KEY_MISSING" in labels
    assert "throw new Error" in labels


def test_rule_ledgers_render_localized_rows_not_english_islands() -> None:
    rules = _module_source("modules/renderers/rules.js")
    methodology = _module_source("modules/methodology.js")

    for source in (rules, methodology):
        assert "row.localized?.[state.locale]" in source
        assert "narrativeEntry(" in source
        assert "sourceIsland(row.result)" not in source
        assert "sourceIsland(row.name)" not in source
        assert "sourceIsland(row.decision_effect)" not in source


def test_null_state_renders_disposition_chip() -> None:
    dom = _module_source("modules/dom.js")
    decision = _module_source("modules/renderers/decision.js")
    integrity = _module_source("modules/renderers/integrity.js")
    portfolio = _module_source("modules/portfolio.js")
    workspace = _css_source("workspace.css")

    assert "export function decisionChip" in dom
    assert "props.state ?? props.screening_disposition" in decision
    assert "decisionChip(" in integrity
    assert "decisionChip(" in portfolio
    state_block = workspace.split(
        ".state-NO_CANDIDATE {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    assert "var(--" in state_block
    assert "#" not in state_block


def test_screening_css_layer_is_imported_and_token_only() -> None:
    styles = _module_source("styles.css")
    screening = _css_source("screening.css")

    assert '@import url("./css/screening.css") layer(screening);' in styles
    assert screening
