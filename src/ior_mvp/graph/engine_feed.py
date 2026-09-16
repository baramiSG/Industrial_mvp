"""Deterministic graph-fed results over the governed projection artifact."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeAlias

from ior_mvp.route_hypotheses import (
    SHARED_ENABLER_CONTRACT_FIELDS,
    shared_enabler_unlock_value,
)

if TYPE_CHECKING:
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
    nodes = _node_index(projection)
    product = nodes.get(opportunity_id)
    if (
        product is None
        or product.label != "Product"
        or product.properties.get("synthetic_flag") is not False
        or product.properties.get("derived") is not False
    ):
        return None
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
                and edge.properties.get("scenario_id") == "PUBLIC"
            )
            or (
                mode == "simulated"
                and edge.properties.get("synthetic_flag") is True
                and edge.properties.get("evidence_class") == "D"
                and edge.properties.get("scenario_id") == scenario_id
            )
        )
    ]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise ValueError(
            f"Opportunity has ambiguous shared enablers: {opportunity_id}"
        )
    candidate = candidates[0]
    enabler_id = candidate.target
    enabler = nodes.get(enabler_id)
    if (
        enabler is None
        or enabler.label != "Intervention"
        or enabler.properties.get("kind") != "shared_enabler"
        or enabler.properties.get("derived") is not False
        or enabler.properties.get("projection_id") != projection.projection_id
    ):
        raise ValueError("Shared-enabler node is invalid")
    enabler_scenarios = enabler.properties.get("scenario_ids", [])
    if mode == "public":
        if (
            enabler.properties.get("synthetic_flag") is not False
            or enabler.properties.get("scenario_id") != "PUBLIC"
        ):
            raise ValueError("Public shared-enabler provenance is invalid")
    elif (
        enabler.properties.get("synthetic_flag") is not True
        or enabler.properties.get("evidence_class") != "D"
        or not isinstance(enabler_scenarios, list)
        or scenario_id not in enabler_scenarios
    ):
        raise ValueError("Simulated shared-enabler provenance is invalid")
    dependents = []
    for edge in projection.edges:
        if (
            edge.type != "UNLOCKED_BY"
            or edge.target != enabler_id
            or edge.properties.get("derived") is not False
            or edge.properties.get("projection_id") != projection.projection_id
        ):
            continue
        dependent = nodes.get(edge.source)
        if (
            dependent is None
            or dependent.label != "Product"
            or dependent.properties.get("synthetic_flag") is not False
            or dependent.properties.get("derived") is not False
        ):
            raise ValueError("Shared-enabler dependent Product is invalid")
        edge_scenario = edge.properties.get("scenario_id")
        if mode == "public":
            if (
                edge.properties.get("synthetic_flag") is not False
                or edge_scenario != "PUBLIC"
            ):
                continue
        else:
            membership = nodes.get(str(edge_scenario))
            if (
                edge.properties.get("synthetic_flag") is not True
                or edge.properties.get("evidence_class") != "D"
                or edge_scenario not in enabler_scenarios
                or membership is None
                or membership.label != "Scenario"
                or membership.properties.get("opportunity_id") != edge.source
                or membership.properties.get("synthetic_flag") is not True
                or membership.properties.get("derived") is not False
            ):
                raise ValueError("Shared-enabler scenario membership is invalid")
        dependents.append(edge)
    dependents.sort(key=lambda edge: edge.source)
    if not dependents:
        return None
    if len({edge.source for edge in dependents}) != len(dependents):
        raise ValueError("Shared-enabler dependent membership is duplicated")
    required_edge_properties = {
        "unlock_probability",
        "dependent_incremental_national_value_m_sar",
        "dependency_share",
        "valuation_route_code",
        "valuation_input_reference",
        "constraint_classes_addressed",
        "removes_binding_constraint",
    }
    if any(
        required_edge_properties - set(edge.properties)
        for edge in dependents
    ):
        raise ValueError("Shared-enabler dependency properties are incomplete")
    if (
        "enabler_cost_m_sar" not in enabler.properties
        or not isinstance(enabler.properties.get("components"), dict)
    ):
        raise ValueError("Shared-enabler common properties are incomplete")
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
        "valuation_route_codes": [
            edge.properties["valuation_route_code"] for edge in dependents
        ],
        "valuation_input_references": [
            edge.properties["valuation_input_reference"] for edge in dependents
        ],
        "components": enabler.properties.get("components"),
        "constraint_classes_addressed": candidate.properties.get(
            "constraint_classes_addressed", []
        ),
        "removes_binding_constraint": candidate.properties.get(
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
    mode, _scenario_id = _branch(branch)
    nodes = _node_index(projection)
    rows_by_enabler: dict[str, dict[str, Any]] = {}
    products = sorted(
        node.id for node in projection.nodes if node.label == "Product"
    )
    for opportunity_id in products:
        inputs = shared_enabler_inputs(
            projection,
            opportunity_id,
            branch=branch,
        )
        if inputs is None or inputs["enabler_id"] in rows_by_enabler:
            continue
        enabler = nodes[inputs["enabler_id"]]
        eligible_indexes = [
            index
            for index, (probability, value, share) in enumerate(
                zip(
                    inputs["unlock_probabilities"],
                    inputs["dependent_incremental_national_values_m_sar"],
                    inputs["dependency_shares"],
                    strict=True,
                )
            )
            if float(probability) > 0
            and float(share) > 0
            and float(value) > 0
        ]
        if not eligible_indexes:
            continue
        dependent_ids = [
            inputs["dependent_opportunity_ids"][index]
            for index in eligible_indexes
        ]
        unlock_value = shared_enabler_unlock_value(
            [
                float(inputs["unlock_probabilities"][index])
                for index in eligible_indexes
            ],
            [
                float(
                    inputs[
                        "dependent_incremental_national_values_m_sar"
                    ][index]
                )
                for index in eligible_indexes
            ],
            [
                float(inputs["dependency_shares"][index])
                for index in eligible_indexes
            ],
            float(inputs["enabler_cost_m_sar"]),
        )
        evidence_ids = sorted(
            {
                str(value)
                for edge in projection.edges
                if edge.type == "UNLOCKED_BY"
                and edge.target == inputs["enabler_id"]
                and edge.source in dependent_ids
                and (
                    edge.properties.get("synthetic_flag") is False
                    if mode == "public"
                    else edge.properties.get("synthetic_flag") is True
                )
                and float(edge.properties["unlock_probability"]) > 0
                and float(edge.properties["dependency_share"]) > 0
                and float(
                    edge.properties[
                        "dependent_incremental_national_value_m_sar"
                    ]
                )
                > 0
                for value in edge.properties.get("evidence_ids", [])
            }
        )
        rows_by_enabler[inputs["enabler_id"]] = {
            "enabler_id": inputs["enabler_id"],
            "enabler_kind": enabler.properties.get("enabler_kind"),
            "label": {
                "en": enabler.properties.get("label_en"),
                "ar": enabler.properties.get("label_ar"),
            },
            "dependent_opportunity_ids": dependent_ids,
            "counted_dependents": len(dependent_ids),
            "unlock_value_m_sar": unlock_value,
            "status": "POSITIVE" if unlock_value > 0 else "NONPOSITIVE",
            "graph_projection_id": projection.projection_id,
            "evidence_ids": evidence_ids,
        }
    return [rows_by_enabler[key] for key in sorted(rows_by_enabler)]
