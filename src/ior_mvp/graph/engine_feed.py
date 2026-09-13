"""Deterministic graph-fed results over the governed projection artifact."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeAlias

from ior_mvp.route_hypotheses import (
    SHARED_ENABLER_CONTRACT_FIELDS,
    shared_enabler_unlock_value,
)

from .projection import GraphProjection


GraphBranch: TypeAlias = str | tuple[str, str]


def _branch(branch: GraphBranch) -> tuple[str, str]:
    if branch == "public":
        return "public", "PUBLIC"
    if (
        isinstance(branch, tuple)
        and len(branch) == 2
        and branch[0] == "simulated"
        and isinstance(branch[1], str)
        and branch[1]
    ):
        return branch
    raise ValueError("Graph branch must be public or ('simulated', scenario_id)")


def _visible(properties: Mapping[str, Any], branch: GraphBranch) -> bool:
    mode, scenario_id = _branch(branch)
    if mode == "public":
        return properties.get("synthetic_flag") is False
    return (
        properties.get("synthetic_flag") is False
        or properties.get("scenario_id") == scenario_id
        or scenario_id in properties.get("scenario_ids", [])
    )


def _node_index(projection: GraphProjection) -> dict[str, Any]:
    return {node.id: node for node in projection.nodes}


def shared_enabler_inputs(
    projection: GraphProjection,
    opportunity_id: str,
    *,
    branch: GraphBranch,
) -> dict[str, Any] | None:
    """Return route-8 inputs only from non-derived UNLOCKED_BY evidence."""
    mode, scenario_id = _branch(branch)
    candidates = [
        edge
        for edge in projection.edges
        if edge.type == "UNLOCKED_BY"
        and edge.source == opportunity_id
        and edge.properties.get("derived") is False
        and (
            (
                mode == "public"
                and edge.properties.get("synthetic_flag") is False
            )
            or (
                mode == "simulated"
                and edge.properties.get("scenario_id") == scenario_id
            )
        )
    ]
    if not candidates:
        return None
    if len({edge.target for edge in candidates}) != 1:
        raise ValueError(
            f"Opportunity has multiple shared enablers: {opportunity_id}"
        )
    enabler_id = candidates[0].target
    nodes = _node_index(projection)
    enabler = nodes.get(enabler_id)
    if enabler is None or enabler.properties.get("derived") is not False:
        return None
    dependents = [
        edge
        for edge in projection.edges
        if edge.type == "UNLOCKED_BY"
        and edge.target == enabler_id
        and edge.properties.get("derived") is False
        and (
            edge.properties.get("synthetic_flag") is False
            if mode == "public"
            else edge.properties.get("synthetic_flag") is True
        )
    ]
    dependents.sort(key=lambda edge: edge.source)
    if not dependents:
        return None
    result: dict[str, Any] = {
        "enabler_id": enabler_id,
        "dependent_opportunity_ids": [edge.source for edge in dependents],
        "unlock_probabilities": [
            edge.properties["unlock_probability"] for edge in dependents
        ],
        "dependent_incremental_national_values_m_sar": [
            edge.properties["dependent_incremental_national_value_m_sar"]
            for edge in dependents
        ],
        "dependency_shares": [
            edge.properties["dependency_share"] for edge in dependents
        ],
        "enabler_cost_m_sar": enabler.properties["enabler_cost_m_sar"],
        "graph_projection_id": projection.projection_id,
        "components": enabler.properties.get("components"),
        "constraint_classes_addressed": candidates[0].properties.get(
            "constraint_classes_addressed", []
        ),
        "removes_binding_constraint": candidates[0].properties.get(
            "removes_binding_constraint"
        ),
        "evidence_ids": sorted(
            {
                str(value)
                for edge in dependents
                for value in edge.properties.get("evidence_ids", [])
            }
            | {
                str(value)
                for value in enabler.properties.get("evidence_ids", [])
            }
        ),
    }
    missing = set(SHARED_ENABLER_CONTRACT_FIELDS) - set(result)
    if missing:
        raise ValueError(
            "Projection omitted route-8 contract fields: "
            + ", ".join(sorted(missing))
        )
    return result


def adjacency_explanation(
    projection: GraphProjection,
    opportunity_id: str,
    *,
    branch: GraphBranch,
) -> dict[str, Any]:
    """Explain the deterministic R9-S adjacency projection."""
    mode, scenario_id = _branch(branch)
    rows = [
        edge
        for edge in projection.edges
        if edge.type == "ADJACENT_TO"
        and edge.target == opportunity_id
        and _visible(edge.properties, branch)
        and (
            edge.properties.get("scenario_id") == "PUBLIC"
            if mode == "public"
            else edge.properties.get("scenario_id") == scenario_id
        )
    ]
    rows.sort(key=lambda edge: edge.source)
    first = rows[0].properties if rows else {}
    return {
        "opportunity_id": opportunity_id,
        "mode": mode,
        "scenario_id": scenario_id,
        "fired": first.get("fired"),
        "execution": first.get("execution"),
        "same_process_family": first.get("same_process_family"),
        "qualifying_signal_count": int(
            first.get("qualifying_signal_count") or 0
        ),
        "result_code": first.get("result_code"),
        "producer_ids": [edge.source for edge in rows],
        "evidence_ids": sorted(
            {
                str(value)
                for edge in rows
                for value in edge.properties.get("evidence_ids", [])
            }
        ),
    }


def route_blocking_capability(
    projection: GraphProjection,
    opportunity_id: str,
    *,
    branch: GraphBranch,
) -> list[dict[str, Any]]:
    """Return route-to-capability blockers for one branch."""
    mode, scenario_id = _branch(branch)
    nodes = _node_index(projection)
    rows: list[dict[str, Any]] = []
    for edge in projection.edges:
        if edge.type != "CONSTRAINED_BY" or not _visible(
            edge.properties, branch
        ):
            continue
        source = nodes.get(edge.source)
        target = nodes.get(edge.target)
        if source is None or target is None or target.label != "Capability":
            continue
        if (
            source.label != "Intervention"
            or source.properties.get("opportunity_id") != opportunity_id
            or source.properties.get("mode") != mode
            or (
                mode == "simulated"
                and source.properties.get("scenario_id") != scenario_id
            )
        ):
            continue
        rows.append(
            {
                "route_code": source.properties.get("route_code"),
                "intervention_id": source.id,
                "reason_code": edge.properties.get("reason_code"),
                "capability_id": target.id,
                "capability_kind": target.properties.get("capability_kind"),
                "dimension": target.properties.get("dimension"),
                "gate": target.properties.get("gate"),
                "state": target.properties.get("state"),
                "status": target.properties.get("status"),
                "evidence_ids": sorted(
                    str(value)
                    for value in edge.properties.get("evidence_ids", [])
                ),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            int(row["route_code"]),
            str(row["reason_code"]),
            row["capability_id"],
        ),
    )


def evidence_linkage(
    projection: GraphProjection,
    opportunity_id: str,
    *,
    branch: GraphBranch,
) -> list[dict[str, Any]]:
    """Return Decision evidence-needs and their blocked graph elements."""
    mode, scenario_id = _branch(branch)
    nodes = _node_index(projection)
    rows: list[dict[str, Any]] = []
    for edge in projection.edges:
        if (
            edge.type != "CONSTRAINED_BY"
            or not edge.properties.get("need_code")
            or not _visible(edge.properties, branch)
        ):
            continue
        decision = nodes.get(edge.source)
        if (
            decision is None
            or decision.label != "Decision"
            or decision.properties.get("opportunity_id") != opportunity_id
            or decision.properties.get("mode") != mode
            or (
                mode == "simulated"
                and decision.properties.get("scenario_id") != scenario_id
            )
        ):
            continue
        rows.append(
            {
                "decision_id": decision.id,
                "target_id": edge.target,
                "need_code": edge.properties.get("need_code"),
                "variant": edge.properties.get("variant"),
                "blocked_field": edge.properties.get("blocked_field"),
                "route_effect": edge.properties.get("route_effect"),
                "numeric_evsi": edge.properties.get("numeric_evsi"),
                "evidence_ids": sorted(
                    str(value)
                    for value in edge.properties.get("evidence_ids", [])
                ),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["need_code"]),
            str(row["variant"]),
            row["target_id"],
        ),
    )


def shared_enabler_queue_rows(
    projection: GraphProjection,
    *,
    branch: GraphBranch,
) -> list[dict[str, Any]]:
    """Aggregate shared-enabler portfolio rows from governed evidence edges."""
    mode, scenario_id = _branch(branch)
    nodes = _node_index(projection)
    enabler_ids = sorted(
        {
            edge.target
            for edge in projection.edges
            if edge.type == "UNLOCKED_BY"
            and edge.properties.get("derived") is False
            and (
                edge.properties.get("synthetic_flag") is False
                if mode == "public"
                else (
                    edge.properties.get("synthetic_flag") is True
                    and scenario_id
                    in nodes[edge.target].properties.get("scenario_ids", [])
                )
            )
        }
    )
    rows: list[dict[str, Any]] = []
    for enabler_id in enabler_ids:
        dependents = sorted(
            (
                edge
                for edge in projection.edges
                if edge.type == "UNLOCKED_BY"
                and edge.target == enabler_id
                and edge.properties.get("derived") is False
                and (
                    edge.properties.get("synthetic_flag") is False
                    if mode == "public"
                    else edge.properties.get("synthetic_flag") is True
                )
            ),
            key=lambda edge: edge.source,
        )
        enabler = nodes[enabler_id]
        probabilities = [
            float(edge.properties["unlock_probability"]) for edge in dependents
        ]
        values = [
            float(
                edge.properties[
                    "dependent_incremental_national_value_m_sar"
                ]
            )
            for edge in dependents
        ]
        shares = [
            float(edge.properties["dependency_share"]) for edge in dependents
        ]
        cost = float(enabler.properties["enabler_cost_m_sar"])
        unlock_value = shared_enabler_unlock_value(
            probabilities,
            values,
            shares,
            cost,
        )
        rows.append(
            {
                "enabler_id": enabler_id,
                "enabler_kind": enabler.properties.get("enabler_kind"),
                "label": enabler.properties.get("label"),
                "dependent_opportunity_ids": [
                    edge.source for edge in dependents
                ],
                "counted_dependents": len(dependents),
                "unlock_value_m_sar": unlock_value,
                "status": (
                    "POSITIVE" if unlock_value > 0 else "NONPOSITIVE"
                ),
                "graph_projection_id": projection.projection_id,
                "evidence_ids": sorted(
                    {
                        str(value)
                        for edge in dependents
                        for value in edge.properties.get("evidence_ids", [])
                    }
                ),
            }
        )
    return rows
