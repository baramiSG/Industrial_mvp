from __future__ import annotations

from typing import Any


def build_ui_manifest(analysis: dict[str, Any]) -> dict[str, Any]:
    active = analysis["active_decision"]
    real = analysis["real_decision"]
    r3_metrics = next(
        (
            row["metrics"]
            for row in analysis["rules"]
            if row["rule_id"] == "R3"
        ),
        {},
    )
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
                "synthetic_labels": (analysis.get("simulation_scenario") or {}).get(
                    "display_labels"
                ),
                "authority": analysis["authority"],
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
                "conditions": active.get("conditions", []),
                "kill_conditions": active.get("kill_conditions", []),
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
                "supplier_concentration": r3_metrics,
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
                    "synthetic_labels": (
                        analysis.get("simulation_scenario") or {}
                    ).get("display_labels"),
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
