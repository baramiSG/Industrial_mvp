"""Phase-two projection of deterministic engine outputs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .model import GraphNode, capability_id
from .projection import (
    GraphProjection,
    ProjectionAssembler,
    _base_properties,
    _edge,
)


_CAPABILITY_REASON_CODES = {
    "CAPABILITY_BAND_FAILED",
    "CAPABILITY_UNPUBLISHED",
    "ROUTE_7_CAPABILITY_BAND_FAILED",
}


def _branch_identity(
    analysis: Mapping[str, Any],
) -> tuple[str, bool, str]:
    mode = str(analysis["mode"])
    if mode == "public":
        return str(analysis["opportunity_id"]), False, "PUBLIC"
    scenario_id = str(analysis["scenario_id"])
    return scenario_id, True, scenario_id


def _derived_properties(
    projection: GraphProjection,
    *,
    identity: str,
    analysis: Mapping[str, Any],
    evidence_id: str,
) -> dict[str, Any]:
    _subject, synthetic, scenario_id = _branch_identity(analysis)
    decision = analysis["decision"]
    evidence_class = "D" if synthetic else str(decision.get("confidence", "E"))
    if evidence_class not in {"A", "B", "C", "D", "E"}:
        evidence_class = "E"
    return _base_properties(
        identity=identity,
        evidence_id=evidence_id,
        as_of=str(analysis["as_of_date"]),
        evidence_class=evidence_class,
        synthetic_flag=synthetic,
        scenario_id=scenario_id,
        origin_kind="ENGINE_RUN",
        origin_ref=str(analysis["snapshot_id"]),
        projection_id=projection.projection_id,
        derived=True,
        engine_run_id=str(projection.engine["engine_run_id"]),
        evidence_ids=[evidence_id],
    )


def _engine_evidence(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
) -> str:
    subject, _synthetic, _scenario_id = _branch_identity(analysis)
    mode = str(analysis["mode"])
    identity = f"ENGINE-EVIDENCE-{subject}-{mode}"
    props = _derived_properties(
        assembler.projection,
        identity=identity,
        analysis=analysis,
        evidence_id=identity,
    )
    props.update(
        {
            "title": "Deterministic graph projection engine run",
            "source": "ior_mvp",
            "status": "calculated",
            "supports": ["ENGINE_DERIVATION"],
        }
    )
    assembler.add_node(GraphNode("Evidence", identity, props))
    return identity


def _dstar_node(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    evidence_id: str,
) -> str:
    subject, _synthetic, _scenario_id = _branch_identity(analysis)
    identity = capability_id(subject, "DSTAR")
    capability = analysis["capability"]
    props = _derived_properties(
        assembler.projection,
        identity=identity,
        analysis=analysis,
        evidence_id=evidence_id,
    )
    props.update(
        {
            "opportunity_id": analysis["opportunity_id"],
            "capability_kind": "d_star",
            "d_star": capability.get("d_star"),
            "known_weight_coverage": capability.get("known_weight_coverage"),
            "unknown_weight": capability.get("unknown_weight"),
            "route_band": capability.get("route_band"),
            "route_publishable": capability.get("route_publishable"),
        }
    )
    assembler.add_node(GraphNode("Capability", identity, props))
    edge_props = deepcopy(props)
    edge_props.pop("id")
    _edge(
        assembler,
        "HAS_CAPABILITY",
        str(analysis["opportunity_id"]),
        identity,
        edge_props,
        discriminator=str(analysis["mode"]),
    )
    return identity


def _intervention_nodes(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    decision_id: str,
    evidence_id: str,
) -> dict[int, str]:
    subject, _synthetic, _scenario_id = _branch_identity(analysis)
    preferred = analysis["decision"].get("preferred_hypothesis")
    selected_code = analysis["decision"].get("route_code")
    preferred_code = (
        preferred.get("route_code") if isinstance(preferred, Mapping) else None
    )
    result: dict[int, str] = {}
    for route in analysis["decision"]["route_hypotheses"]:
        route_code = int(route["route_code"])
        identity = f"INT-{subject}-route-{route_code}"
        props = _derived_properties(
            assembler.projection,
            identity=identity,
            analysis=analysis,
            evidence_id=evidence_id,
        )
        props.update(
            {
                "kind": "route_hypothesis",
                "opportunity_id": analysis["opportunity_id"],
                "mode": analysis["mode"],
                "route_code": route_code,
                "route_key": route.get("route_key"),
                "status": route.get("status"),
                "reason_codes": deepcopy(route.get("reason_codes", [])),
                "incremental_national_value_m_sar": route.get(
                    "incremental_national_value_m_sar"
                ),
                "unrounded_incremental_national_value_m_sar": route.get(
                    "unrounded_incremental_national_value_m_sar"
                ),
                "blocked_by_lower_route": route.get("precedence", {}).get(
                    "blocked_by_lower_route"
                ),
                "resolves_binding_constraint": route.get(
                    "resolves_binding_constraint"
                ),
            }
        )
        assembler.add_node(GraphNode("Intervention", identity, props))
        role = (
            "SELECTED"
            if route_code == selected_code
            else ("PREFERRED" if route_code == preferred_code else "EVALUATED")
        )
        edge_props = deepcopy(props)
        edge_props.pop("id")
        edge_props["role"] = role
        _edge(
            assembler,
            "DEPENDS_ON",
            decision_id,
            identity,
            edge_props,
            discriminator=role,
        )
        result[route_code] = identity
    return result


def _adjacency_edges(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    evidence_id: str,
) -> None:
    r9s = next(
        (
            row
            for row in analysis["rules"]
            if row.get("rule_id") == "R9-S"
        ),
        None,
    )
    if not isinstance(r9s, Mapping):
        return
    product_id = str(analysis["opportunity_id"])
    producers = sorted(
        {
            edge.target
            for edge in assembler.projection.edges
            if edge.type == "PRODUCED_BY"
            and edge.source == product_id
            and edge.properties["synthetic_flag"]
            == (analysis["mode"] == "simulated")
        }
    )
    if not producers and analysis["mode"] == "simulated":
        producers = sorted(
            {
                edge.target
                for edge in assembler.projection.edges
                if edge.type == "PRODUCED_BY"
                and edge.source == product_id
                and edge.properties["synthetic_flag"] is False
            }
        )
    for producer in producers:
        if assembler.nodes[producer].label not in {"Plant", "Company"}:
            continue
        props = _derived_properties(
            assembler.projection,
            identity="PENDING",
            analysis=analysis,
            evidence_id=evidence_id,
        )
        props.pop("id")
        props.update(
            {
                "fired": r9s.get("fired"),
                "execution": r9s.get("execution"),
                "same_process_family": r9s.get("metrics", {}).get(
                    "same_process_family"
                ),
                "qualifying_signal_count": r9s.get("metrics", {}).get(
                    "qualifying_signal_count"
                ),
                "result_code": r9s.get("result_code"),
            }
        )
        _edge(
            assembler,
            "ADJACENT_TO",
            producer,
            product_id,
            props,
            discriminator=str(analysis["mode"]),
        )


def _route_constraints(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    interventions: Mapping[int, str],
    dstar_id: str,
    evidence_id: str,
) -> None:
    for route in analysis["decision"]["route_hypotheses"]:
        reason_codes = [
            str(value) for value in route.get("reason_codes", [])
        ]
        for reason_code in reason_codes:
            if reason_code not in _CAPABILITY_REASON_CODES:
                continue
            props = _derived_properties(
                assembler.projection,
                identity="PENDING",
                analysis=analysis,
                evidence_id=evidence_id,
            )
            props.pop("id")
            props["reason_code"] = reason_code
            props["route_code"] = route["route_code"]
            _edge(
                assembler,
                "CONSTRAINED_BY",
                interventions[int(route["route_code"])],
                dstar_id,
                props,
                discriminator=reason_code,
            )


def _need_target(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    interventions: Mapping[int, str],
    blocked_field: str,
) -> str:
    product_id = str(analysis["opportunity_id"])
    subject, synthetic, scenario_id = _branch_identity(analysis)
    if blocked_field in {
        "demand_at_required_specification",
        "target_specification",
    }:
        candidate = (
            f"SPEC-{scenario_id}-TARGET"
            if synthetic
            else f"SPEC-{product_id}-TARGET"
        )
        if candidate in assembler.nodes:
            return candidate
    if blocked_field in {
        "domestic_supply_or_capability",
        "hard_regulatory_or_process_gate",
        "idle_equivalent_domestic_capacity",
    }:
        prefix = f"CAP-{subject}-"
        candidates = sorted(
            node.id
            for node in assembler.projection.nodes
            if node.label == "Capability" and node.id.startswith(prefix)
        )
        if candidates:
            return candidates[0]
    if blocked_field in {"route_economics", "economics"}:
        preferred = analysis["decision"].get("preferred_hypothesis")
        code = (
            preferred.get("route_code")
            if isinstance(preferred, Mapping)
            else None
        )
        if isinstance(code, int) and code in interventions:
            return interventions[code]
    return product_id


def _evidence_linkage(
    assembler: ProjectionAssembler,
    analysis: Mapping[str, Any],
    decision_id: str,
    interventions: Mapping[int, str],
    evidence_id: str,
) -> None:
    for need in analysis.get("evidence_needs", []):
        if not isinstance(need, Mapping):
            continue
        target = _need_target(
            assembler,
            analysis,
            interventions,
            str(need.get("blocked_field")),
        )
        props = _derived_properties(
            assembler.projection,
            identity="PENDING",
            analysis=analysis,
            evidence_id=evidence_id,
        )
        props.pop("id")
        props.update(
            {
                "need_code": need.get("need_code"),
                "variant": need.get("variant"),
                "blocked_field": need.get("blocked_field"),
                "route_effect": need.get("route_effect"),
                "numeric_evsi": need.get("numeric_evsi"),
                "evidence_ids": sorted(
                    str(value) for value in need.get("evidence_ids", [])
                ),
            }
        )
        _edge(
            assembler,
            "CONSTRAINED_BY",
            decision_id,
            target,
            props,
            discriminator=f"{need.get('need_code')}:{need.get('variant')}",
        )
        for linked_evidence in props["evidence_ids"]:
            if linked_evidence not in assembler.nodes:
                continue
            support_props = deepcopy(props)
            support_props["evidence_id"] = linked_evidence
            support_props["supports"] = [str(need.get("need_code"))]
            _edge(
                assembler,
                "SUPPORTED_BY_EVIDENCE",
                target,
                linked_evidence,
                support_props,
                discriminator=(
                    f"{analysis['mode']}:{analysis.get('scenario_id', 'PUBLIC')}:"
                    f"{need.get('need_code')}"
                ),
            )


def project_engine_outputs(
    projection: GraphProjection,
    analyses: Mapping[tuple[str, str], Mapping[str, Any]],
) -> GraphProjection:
    """Add derived Decision, Intervention, D* and explanation elements."""
    assembler = ProjectionAssembler(projection)
    for (_opportunity_id, _mode), analysis in sorted(analyses.items()):
        evidence_id = _engine_evidence(assembler, analysis)
        subject, _synthetic, _scenario_id = _branch_identity(analysis)
        decision_id = (
            f"DEC-{subject}-{analysis['mode']}-"
            f"{projection.engine['engine_run_id']}"
        )
        decision = analysis["decision"]
        props = _derived_properties(
            projection,
            identity=decision_id,
            analysis=analysis,
            evidence_id=evidence_id,
        )
        props.update(
            {
                "opportunity_id": analysis["opportunity_id"],
                "mode": analysis["mode"],
                "state": decision.get("state"),
                "route_code": decision.get("route_code"),
                "decision_reason_code": decision.get("decision_reason_code"),
                "confidence": decision.get("confidence"),
                "screening_disposition": decision.get(
                    "screening_disposition"
                ),
            }
        )
        assembler.add_node(GraphNode("Decision", decision_id, props))
        dstar_id = _dstar_node(assembler, analysis, evidence_id)
        interventions = _intervention_nodes(
            assembler,
            analysis,
            decision_id,
            evidence_id,
        )
        _adjacency_edges(assembler, analysis, evidence_id)
        _route_constraints(
            assembler,
            analysis,
            interventions,
            dstar_id,
            evidence_id,
        )
        _evidence_linkage(
            assembler,
            analysis,
            decision_id,
            interventions,
            evidence_id,
        )
    projection.refresh_counts()
    return projection
