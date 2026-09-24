from __future__ import annotations

import hashlib
import ast
import json
import re
import subprocess
import tomllib
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from scripts import check_browser_prerequisites as browser_preflight
from browser_tests import harness


PYPROJECT = PROJECT_ROOT / "pyproject.toml"
MAKEFILE = PROJECT_ROOT / "Makefile"
BROWSER_TESTS = PROJECT_ROOT / "browser_tests"
AXE_ROOT = BROWSER_TESTS / "vendor" / "axe-core-4.13.0"


def test_browser_dependencies_are_isolated_in_exact_e2e_extra() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    extras = project["project"]["optional-dependencies"]

    assert extras["dev"] == ["pytest>=8,<9", "httpx>=0.27,<1", "pypdf==6.16.1"]
    assert extras["e2e"] == [
        "Pillow==12.3.0",
        "playwright==1.62.0",
        "pytest-playwright==0.9.0",
    ]
    pytest_options = project["tool"]["pytest"]["ini_options"]
    assert pytest_options["testpaths"] == ["tests"]
    assert pytest_options["markers"] == [
        "e2e: real-Chromium acceptance tests; excluded from default testpaths",
        "visual: governed visual-regression matrix",
    ]


def test_browser_harness_defines_bilingual_locale_matrix() -> None:
    locales = getattr(harness, "LOCALES", ())

    assert tuple(
        (locale.code, locale.bcp47, locale.direction)
        for locale in locales
    ) == (
        ("en", "en-US", "ltr"),
        ("ar", "ar-SA", "rtl"),
    )
    conftest = (BROWSER_TESTS / "conftest.py").read_text(encoding="utf-8")
    assert "locale.bcp47" in conftest
    assert "_requested_locale" in conftest


def test_browser_suite_has_the_approved_top_level_shape() -> None:
    assert BROWSER_TESTS.is_dir()
    assert {
        path.name
        for path in BROWSER_TESTS.iterdir()
        if path.is_file()
    } == {
        "THIRD_PARTY_NOTICES.md",
        "conftest.py",
        "graph_fixtures.py",
        "graph_pages.py",
        "harness.py",
        "parity_grammar.py",
        "pages.py",
        "test_accessibility.py",
        "test_dossier.py",
        "test_graph.py",
        "test_guardrails.py",
        "test_journeys.py",
        "test_responsive.py",
        "test_s15b_selection.py",
        "test_screening.py",
        "test_visual_baselines.py",
        "visual_baselines.py",
        "visual_container.py",
        "executive_pages.py",
        "test_executive.py",
        "test_executive_accessibility.py",
        "test_executive_races.py",
        "test_executive_states.py",
    }


def test_makefile_keeps_legacy_runner_and_adds_explicit_browser_gate() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert "UV_RUN = $(UV) run --locked --extra dev\n" in source
    assert (
        "UV_RUN_E2E = $(UV) run --locked --extra dev --extra e2e\n"
        in source
    )
    assert source.count("$(E2E_PREFLIGHT)") == 3
    assert source.count("$(E2E_TESTS)") == 2
    assert "IOR_E2E_EXPLICIT=1" in source
    assert "python -m compileall -q src scripts tests browser_tests" in source
    assert (
        'python scripts/check_es_modules.py --node "$(NODE)"'
        in source
    )
    assert "$(UV_RUN) python scripts/check_ui_contracts.py" in source
    assert "node --check src/ior_mvp/static/app.js" not in source


def test_makefile_syncs_e2e_dependencies_for_explicit_browser_gate() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert (
        "uv-sync-e2e:\n"
        "\t$(UV) sync --locked --extra dev --extra e2e\n"
    ) in source
    assert "e2e-functional: uv-sync-e2e\n" in source
    assert "e2e-visual: uv-sync-e2e\n" in source
    assert "e2e: e2e-functional e2e-visual\n" in source
    assert "ci: uv-sync\n" in source


def test_browser_provenance_uses_runtime_versions_without_application_literals() -> None:
    harness_source = (BROWSER_TESTS / "harness.py").read_text(
        encoding="utf-8"
    )
    visual_source = (BROWSER_TESTS / "visual_baselines.py").read_text(
        encoding="utf-8"
    )

    assert re.search(
        r"""["']0\.\d+\.\d+["']""",
        harness_source,
    ) is None
    assert "from ior_mvp import __version__" in harness_source
    assert 'version("playwright")' in visual_source
    assert 'version("pytest-playwright")' in visual_source


def test_visual_runtime_is_separate_from_s06_documentary_references() -> None:
    conftest_source = (BROWSER_TESTS / "conftest.py").read_text(
        encoding="utf-8"
    )
    harness_source = (BROWSER_TESTS / "harness.py").read_text(
        encoding="utf-8"
    )
    combined_source = conftest_source + harness_source

    assert "v0.2.0^{}" not in combined_source
    assert "git_revision(" not in conftest_source
    assert "ReferenceRecorder" not in conftest_source
    assert "reference-screenshots" not in combined_source


def test_vendored_axe_source_and_licence_are_exact_and_hash_verified() -> None:
    source = json.loads((AXE_ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    payload = (AXE_ROOT / "axe.min.js").read_bytes()
    licence = (AXE_ROOT / "LICENSE").read_text(encoding="utf-8")
    notices = (BROWSER_TESTS / "THIRD_PARTY_NOTICES.md").read_text(
        encoding="utf-8"
    )

    assert source == {
        "component": "axe-core",
        "version": "4.13.0",
        "source_url": (
            "https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz"
        ),
        "registry_sri": (
            "sha512-"
            "UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+"
            "XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A=="
        ),
        "axe_min_sha256": hashlib.sha256(payload).hexdigest(),
        "acquired_on": "2026-09-02",
        "disposition": "unmodified vendored distribution",
    }
    assert "Mozilla Public License, version 2.0" in licence
    for fragment in (
        "playwright 1.62.0",
        "pytest-playwright 0.9.0",
        "axe-core 4.13.0",
        "Apache-2.0",
        "MPL-2.0",
        source["source_url"],
    ):
        assert fragment in notices


def test_browser_suite_never_uses_screenshot_comparison_or_remote_axe() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(BROWSER_TESTS.glob("*.py"))
    )

    for prohibited in (
        "to_have_screenshot",
        "to_match_snapshot",
        "pixelmatch",
        "add_script_tag(url=",
        "cdnjs",
        "unpkg",
        "jsdelivr",
    ):
        assert prohibited not in sources


def _write_axe_fixture(root: Path, payload: bytes = b"axe fixture") -> Path:
    root.mkdir(parents=True)
    (root / "axe.min.js").write_bytes(payload)
    (root / "LICENSE").write_text(
        "Mozilla Public License, version 2.0\n",
        encoding="utf-8",
    )
    (root / "SOURCE.json").write_text(
        json.dumps(
            {
                "component": "axe-core",
                "version": "4.13.0",
                "source_url": (
                    "https://registry.npmjs.org/"
                    "axe-core/-/axe-core-4.13.0.tgz"
                ),
                "registry_sri": (
                    "sha512-"
                    "UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+"
                    "XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A=="
                ),
                "axe_min_sha256": hashlib.sha256(payload).hexdigest(),
                "acquired_on": "2026-09-02",
                "disposition": "unmodified vendored distribution",
            }
        ),
        encoding="utf-8",
    )
    return root


def _version_lookup(package: str) -> str:
    return {
        "playwright": "1.62.0",
        "pytest-playwright": "0.9.0",
    }[package]


def test_preflight_accepts_exact_versions_browser_axe_and_arabic_font(
    tmp_path: Path,
) -> None:
    chromium = tmp_path / "chromium"
    chromium.write_text("", encoding="utf-8")
    chromium.chmod(0o755)
    font = tmp_path / "NotoSansArabic-Regular.ttf"
    font.write_text("", encoding="utf-8")
    axe_root = _write_axe_fixture(tmp_path / "axe")

    report = browser_preflight.run_preflight(
        version_lookup=_version_lookup,
        chromium_path_lookup=lambda: chromium,
        axe_root=axe_root,
        command_runner=lambda command: subprocess.CompletedProcess(
            command,
            0,
            stdout=f"Noto Sans Arabic|{font}\n",
            stderr="",
        ),
    )

    assert report.playwright_version == "1.62.0"
    assert report.pytest_playwright_version == "0.9.0"
    assert report.chromium_executable == chromium
    assert report.font_family == "Noto Sans Arabic"
    assert report.font_file == font


def test_preflight_missing_browser_is_nonzero_with_safe_remediation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    axe_root = _write_axe_fixture(tmp_path / "axe")
    font = tmp_path / "font.ttf"
    font.write_text("", encoding="utf-8")

    result = browser_preflight.main(
        version_lookup=_version_lookup,
        chromium_path_lookup=lambda: tmp_path / "missing-chromium",
        axe_root=axe_root,
        command_runner=lambda command: subprocess.CompletedProcess(
            command,
            0,
            stdout=f"DejaVu Sans|{font}\n",
            stderr="",
        ),
    )

    captured = capsys.readouterr()
    assert result != 0
    assert "Chromium executable is missing" in captured.err
    assert (
        "python -m playwright install --with-deps chromium"
        in captured.err
    )


def test_preflight_rejects_axe_hash_mismatch(tmp_path: Path) -> None:
    axe_root = _write_axe_fixture(tmp_path / "axe")
    (axe_root / "axe.min.js").write_bytes(b"tampered")

    with pytest.raises(
        browser_preflight.PrerequisiteError,
        match="axe.min.js SHA-256 mismatch",
    ):
        browser_preflight.check_axe_assets(axe_root)


def test_preflight_rejects_missing_arabic_font() -> None:
    with pytest.raises(
        browser_preflight.PrerequisiteError,
        match="Arabic-capable fontconfig match is unavailable",
    ):
        browser_preflight.check_arabic_font(
            lambda command: subprocess.CompletedProcess(
                command,
                0,
                stdout="",
                stderr="",
            )
        )


def test_chromium_discovery_uses_cli_metadata_without_driver_warning(
    tmp_path: Path,
) -> None:
    install_root = tmp_path / "chromium-1234"
    chromium = install_root / "chrome-linux64" / "chrome"
    chromium.parent.mkdir(parents=True)
    chromium.write_text("", encoding="utf-8")
    commands: list[list[str]] = []

    def run(
        command: list[str],
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=(
                "Chrome for Testing 151 (playwright chromium v1234)\n"
                f"  Install location:    {install_root}\n"
            ),
            stderr="",
        )

    assert browser_preflight.discover_chromium_executable(run) == chromium
    assert commands == [
        [
            browser_preflight.sys.executable,
            "-m",
            "playwright",
            "install",
            "--dry-run",
            "chromium",
        ]
    ]


def test_failure_collector_classifies_required_channels_and_thresholds() -> None:
    collector = harness.BrowserFailureCollector(
        "http://127.0.0.1:43127"
    )

    collector.record_console("warning", "not an error")
    collector.record_console("error", "console probe")
    collector.record_page_error("pageerror probe")
    collector.record_request_failed(
        "GET",
        "http://127.0.0.1:43127/static/missing.js",
        "net::ERR_FAILED",
    )
    collector.record_response(
        399,
        "GET",
        "http://127.0.0.1:43127/api/health",
    )
    collector.record_response(
        400,
        "GET",
        "http://127.0.0.1:43127/api/probe?mode=public",
    )
    collector.record_request(
        "GET",
        "https://example.invalid/probe?token=redacted",
    )

    assert [record.category for record in collector.records] == [
        "console-error",
        "pageerror",
        "requestfailed",
        "app-http-error",
        "external-request",
    ]
    assert "token=redacted" not in collector.render()
    assert "mode=public" in collector.render()


def test_failure_collector_rendering_is_duplicate_free() -> None:
    collector = harness.BrowserFailureCollector(
        "http://127.0.0.1:43127"
    )

    collector.record_console("error", "same probe")
    collector.record_console("error", "same probe")

    assert len(collector.records) == 1
    assert collector.render().count("same probe") == 1


def test_server_child_environment_is_strictly_allow_listed(
    tmp_path: Path,
) -> None:
    environment = harness.build_child_environment(
        tmp_path,
        {
            "PATH": "/safe/bin",
            "HOME": "/safe/home",
            "SECRET_TOKEN": "must-not-pass",
            "LANG": "unsafe-parent-value",
        },
    )

    assert environment == {
        "PATH": "/safe/bin",
        "HOME": "/safe/home",
        "LANG": "C.UTF-8",
        "PYTHONPATH": str(tmp_path / "src"),
        "PYTHONUNBUFFERED": "1",
    }


def test_server_child_command_uses_current_interpreter_and_inherited_fd() -> None:
    assert harness.build_server_command(23) == [
        harness.sys.executable,
        "-m",
        "uvicorn",
        "ior_mvp.app:app",
        "--fd",
        "23",
        "--log-level",
        "warning",
    ]


def test_server_teardown_accepts_clean_exit_or_requested_sigterm() -> None:
    assert harness.is_expected_server_return_code(0) is True
    assert (
        harness.is_expected_server_return_code(-harness.signal.SIGTERM)
        is True
    )
    assert harness.is_expected_server_return_code(1) is False


def test_browser_inventory_has_exactly_76_named_tests() -> None:
    expected = {
        "test_portfolio_loads_expected_cases_and_states",
        "test_opportunity_card_opens_selected_workspace",
        "test_opportunity_select_loads_each_case",
        "test_new_case_view_distinguishes_observed_missing_and_simulated",
        "test_hero_opens_steel_case_preserving_mode",
        "test_mode_switch_preserves_selected_case",
        "test_navigation_and_methodology_action_reach_sections",
        "test_open_dossier_popup_matches_case_and_mode",
        "test_copy_decision_json_writes_expected_clipboard_payload",
        "test_dossier_print_media_and_pdf_are_valid",
        (
            "test_keyboard_tab_order_reaches_every_interactive_control_"
            "with_visible_focus"
        ),
        "test_workspace_has_zero_wcag_21_aa_axe_violations",
        "test_dossier_has_zero_wcag_21_aa_axe_violations",
        "test_workspace_rtl_elements_render_real_arabic_glyphs",
        "test_dossier_rtl_element_renders_real_arabic_glyphs",
        (
            "test_layout_has_no_horizontal_overflow_and_primary_"
            "controls_are_actionable"
        ),
        "test_governed_visual_baselines_match",
        (
            "test_locale_switch_updates_document_url_storage_and_"
            "preserves_state"
        ),
        "test_failure_collector_observes_all_required_channels",
        "test_screening_summary_renders_status_coverage_counts_and_five_queues",
        "test_screening_journey_queue_record_passport_anchor_back",
        "test_screening_empty_queue_renders_explicit_state",
        "test_screening_queue_pagination_shows_pareto_rank_without_ordinal_list",
        "test_screening_surface_is_public_only_when_simulation_mode_is_active",
        (
            "test_screening_unavailable_and_partial_universe_render_"
            "explicit_states"
        ),
        "test_screening_views_keyboard_traversal_with_visible_focus",
        "test_screening_views_have_zero_wcag_21_aa_axe_violations",
        "test_screening_surface_rtl_direction_and_arabic_glyphs",
        "test_screening_surface_has_no_english_catalogue_prose_in_arabic",
        "test_arabic_parity_predicate_fails_on_injected_english",
        "test_no_candidate_deep_case_renders_disposition_label_not_null",
        (
            "test_workspace_and_methodology_ledgers_have_no_english_"
            "catalogue_prose_in_arabic"
        ),
            "test_arabic_decision_subject_card_has_catalogue_parity",
        "test_s15b_evsi_absent_renders_localized_unavailable",
        "test_s15b_selection_and_every_exclusion_render_bilingually",
        "test_s15b_selection_endpoint_is_loaded_once_without_mode_query",
        "test_graph_collapsed_lazy_catalogue_and_views",
        "test_graph_node_edge_selection_and_passports",
        "test_graph_related_evidence_and_unresolved_references",
        "test_graph_empty_unavailable_and_transport_states",
        "test_graph_context_races_and_close",
        "test_graph_keyboard_accessibility_rtl",
        "test_graph_untrusted_content_and_public_isolation",
        "test_graph_visual_budget_preflight",
        "test_graph_portfolio_out_of_order_does_not_restore_stale_selection",
        "test_all_steps_keep_public_decision_and_nine_routes",
        "test_analyst_sources_and_native_executive_link_keep_current_case",
        "test_analyst_uses_computed_integrity_failure_and_affected_case",
        "test_arabic_source_passports_keep_full_subtree_parity",
        "test_case_comparison_and_vectors_match_api",
        "test_claim_drill_uses_exact_stored_evidence_and_restores_focus",
        "test_complete_arabic_executive_subtree_has_no_unmarked_english",
        "test_delayed_case_response_cannot_restore_old_case",
        "test_delayed_locale_response_cannot_restore_previous_case",
        "test_direct_executive_route_renders_arabic_eight_step_shell",
        "test_executive_native_keyboard_and_technical_isolation",
        "test_executive_steps_have_no_viewport_overflow",
        "test_graph_all_view_states_fit_narrow_panel",
        "test_graph_deep_link_uses_selected_context_and_handles_unavailable",
        "test_graph_hostile_name_text_is_escaped",
        "test_graph_narrow_panel_contains_controls_and_text",
        "test_graph_node_names_preserve_sources_and_arabic",
        "test_graph_scroll_region_reaches_both_keyboard_endpoints",
        "test_graph_source_disclosure_mutations_fail_strict_oracles",
        "test_history_restores_case_step_and_locale",
        "test_honest_absence_and_zero_states",
        "test_inconsistent_join_never_exposes_a_claim",
        "test_journey_exposes_trade_capacity_capability_and_step_navigation",
        "test_late_analyst_claim_response_cannot_restore_previous_sources",
        "test_loading_is_visible_before_summary_arrives",
        "test_malicious_source_is_text_and_unsafe_url_has_no_link",
        "test_polypropylene_zero_support_is_distinct_from_missing_npv",
        "test_route_economics_preserve_available_values_and_typed_absence",
        "test_transport_failures_are_explicit_without_stale_sources",
        "test_unavailable_evsi_case_remains_unavailable",
        "test_unresolved_claim_names_actual_case_wide_needs",
    }
    actual: set[str] = set()
    for path in BROWSER_TESTS.glob("test_*.py"):
        module = ast.parse(path.read_text(encoding="utf-8"))
        actual.update(
            node.name
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name.startswith("test_")
        )

    assert actual == expected


def test_explicit_gate_fails_while_direct_diagnostic_may_skip() -> None:
    source = (BROWSER_TESTS / "conftest.py").read_text(
        encoding="utf-8"
    )

    assert 'os.environ.get("IOR_E2E_EXPLICIT") == "1"' in source
    assert "pytest.fail(" in source
    assert "pytest.skip(" in source
    assert "DIRECT_SKIP_REASON" in source
    assert 'f"{CHROMIUM_REMEDIATION}"' in source


def test_axe_and_failure_collector_have_no_exclusion_api() -> None:
    assert harness.AXE_TAGS == (
        "wcag2a",
        "wcag2aa",
        "wcag21a",
        "wcag21aa",
    )
    harness_source = (BROWSER_TESTS / "harness.py").read_text(
        encoding="utf-8"
    )
    for prohibited in (
        "disableRules",
        "accepted violation",
        "impact filtering",
    ):
        assert prohibited not in harness_source
    public_methods = {
        name
        for name in dir(harness.BrowserFailureCollector)
        if not name.startswith("_")
    }
    assert not any(
        fragment in method
        for method in public_methods
        for fragment in ("ignore", "exclude", "suppress")
    )


def test_pdf_and_visual_contracts_are_nontrivial_and_governed() -> None:
    dossier_source = (
        BROWSER_TESTS / "test_dossier.py"
    ).read_text(encoding="utf-8")
    visual_test = (
        BROWSER_TESTS / "test_visual_baselines.py"
    ).read_text(encoding="utf-8")
    visual_source = (
        BROWSER_TESTS / "visual_baselines.py"
    ).read_text(encoding="utf-8")
    metrics_source = (
        PROJECT_ROOT / "scripts" / "visual_metrics.py"
    ).read_text(encoding="utf-8")

    for fragment in (
        'format="A4"',
        "print_background=True",
        "prefer_css_page_size=True",
        'pdf.startswith(b"%PDF-")',
        'pdf.rstrip().endswith(b"%%EOF")',
        "len(pdf) >= 10_240",
        'rb"/Type\\s*/Page\\b"',
    ):
        assert fragment in dossier_source
    assert "test_governed_visual_baselines_match" in visual_test
    assert "full_page=False" in visual_source
    assert "lossless=True" in visual_source
    assert "significant_pixel_ratio" in metrics_source
    assert "quality=55" not in visual_source


def test_browser_session_writes_a_deterministic_run_summary() -> None:
    source = (BROWSER_TESTS / "conftest.py").read_text(
        encoding="utf-8"
    )

    assert "def pytest_sessionfinish(" in source
    assert '"run-summary-functional.json"' in source
    assert '"run-summary-visual.json"' in source
    assert '"collected"' in source
    assert '"passed"' in source
    assert '"failed"' in source
    assert '"skipped"' in source
