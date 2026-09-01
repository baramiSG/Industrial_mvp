from __future__ import annotations

from typing import Any


def build_ui_manifest(analysis: dict[str, Any]) -> dict[str, Any]:
    active = analysis["active_decision"]
    real = analysis["real_decision"]
    components: list[dict[str, Any]] = [
        {
            "type": "integrity_banner",
            "id": "evidence-boundary",
            "props": {
                "mode": analysis["mode"],
                "public_snapshot": analysis["snapshot_id"],
                "real_state": real["state"],
                "active_state": active["state"],
                "synthetic_label": (analysis.get("simulation_scenario") or {}).get("display_label"),
            },
        },
        {
            "type": "decision_hero",
            "id": "decision",
            "props": {
                "state": active["state"],
                "headline": active["headline"],
                "route": active["route_label"],
                "rationale": active["rationale"],
                "confidence": active["confidence"],
            },
        },
        {
            "type": "metric_grid",
            "id": "public-metrics",
            "props": {
                "trade": analysis["trade"],
                "supplier_metrics": analysis.get("supplier_metrics"),
                "capacity": analysis.get("capacity"),
                "economics": analysis.get("economics"),
            },
        },
        {
            "type": "trade_chart",
            "id": "trade-series",
            "props": {"trade": analysis["trade"]},
        },
        {
            "type": "rule_ledger",
            "id": "rules",
            "props": {"rules": analysis["rules"]},
        },
        {
            "type": "capability_matrix",
            "id": "capability",
            "props": analysis["capability"],
        },
    ]
    if analysis.get("economics"):
        components.append(
            {
                "type": "economics_panel",
                "id": "economics",
                "props": {
                    "economics": analysis["economics"],
                    "competition": analysis.get("competition"),
                    "evsi": analysis.get("evsi"),
                },
            }
        )
    components.extend(
        [
            {
                "type": "evidence_ledger",
                "id": "evidence",
                "props": {"evidence": analysis["evidence"]},
            },
            {
                "type": "data_unlocks",
                "id": "unlocks",
                "props": {
                    "missing_facts": analysis["data_unlocks"],
                    "synthetic_inputs_used": analysis["synthetic_inputs_used"],
                },
            },
            {
                "type": "decision_actions",
                "id": "actions",
                "props": {
                    "opportunity_id": analysis["opportunity"]["id"],
                    "mode": analysis["mode"],
                },
            },
        ]
    )
    return {
        "manifest_version": "1.0",
        "surface": "industrial_decision_workspace",
        "title": analysis["opportunity"]["commercial_name_en"],
        "context": {
            "opportunity_id": analysis["opportunity"]["id"],
            "mode": analysis["mode"],
            "decision_state": active["state"],
        },
        "components": components,
        "guardrails": {
            "approved_component_library_only": True,
            "real_decision_never_uses_synthetic": True,
            "no_executable_model_generated_code": True,
        },
    }
