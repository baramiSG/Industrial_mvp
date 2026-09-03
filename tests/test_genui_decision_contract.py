from __future__ import annotations

from ior_mvp.decision_engine import analyze
from ior_mvp.genui import build_ui_manifest


def _component(manifest: dict, component_type: str) -> dict:
    return next(
        component
        for component in manifest["components"]
        if component["type"] == component_type
    )


def test_public_decision_hero_receives_localized_analysis_contract() -> None:
    analysis = analyze("SAU-H0-721049", "public")
    manifest = build_ui_manifest(analysis)
    hero = _component(manifest, "decision_hero")

    assert hero["props"] == {
        "state": "INVESTIGATE",
        "headline": analysis["active_decision"]["headline"],
        "route": analysis["active_decision"]["route_label"],
        "rationale": analysis["active_decision"]["rationale"],
        "confidence": "C",
        "conditions": analysis["active_decision"]["conditions"],
        "kill_conditions": analysis["active_decision"][
            "kill_conditions"
        ],
        "localized_narrative": analysis["active_decision"][
            "localized_narrative"
        ],
        "screening_disposition": "CANDIDATE",
        "gap_class": analysis["gap_class"],
        "preferred_hypothesis": analysis["preferred_hypothesis"],
        "narrative_version": "1.0.0",
    }


def test_public_unlocks_receive_localized_missing_fact_segments() -> None:
    analysis = analyze("SAU-H0-390210", "public")
    manifest = build_ui_manifest(analysis)
    unlocks = _component(manifest, "data_unlocks")

    assert unlocks["props"]["localized_missing_facts"] == {
        locale: analysis["real_decision"]["localized_narrative"][
            locale
        ]["missing_facts"]
        for locale in ("en", "ar")
    }
    assert unlocks["props"]["missing_facts"] == analysis["data_unlocks"]


def test_simulated_hero_keeps_scenario_narrative_without_catalogue_projection(
) -> None:
    analysis = analyze("SAU-H0-721049", "simulated")
    manifest = build_ui_manifest(analysis)
    hero = _component(manifest, "decision_hero")
    unlocks = _component(manifest, "data_unlocks")

    assert "localized_narrative" not in analysis["simulation_decision"]
    assert hero["props"]["localized_narrative"] is None
    assert hero["props"]["headline"] == (
        analysis["simulation_decision"]["headline"]
    )
    assert unlocks["props"]["localized_missing_facts"] is None


def test_genui_component_registry_remains_unchanged() -> None:
    manifest = build_ui_manifest(
        analyze("SAU-H0-721049", "simulated")
    )

    assert {
        component["type"] for component in manifest["components"]
    } == {
        "integrity_banner",
        "decision_hero",
        "metric_grid",
        "trade_chart",
        "rule_ledger",
        "capability_matrix",
        "economics_panel",
        "evidence_ledger",
        "data_unlocks",
        "decision_actions",
    }
