from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import get_public_case
from ior_mvp.evidence import synthetic_evidence_rows
from ior_mvp.graph.derived import project_engine_outputs
from ior_mvp.graph.engine_feed import evidence_linkage
from ior_mvp.graph.model import GraphNode, capability_id
from ior_mvp.graph.projection import (
    GraphProjection,
    GraphProjectionError,
    build_evidence_layer,
    build_repository_projection,
)

_BROAD_NEED_FIELDS = (
    "domestic_supply_or_capability",
    "hard_regulatory_or_process_gate",
    "idle_equivalent_domestic_capacity",
)


@pytest.fixture(scope="module")
def projection():
    return build_repository_projection(PROJECT_ROOT)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _nodes(projection, label: str) -> list:
    return [node for node in projection.nodes if node.label == label]


def test_every_public_snapshot_and_scenario_is_projected(projection) -> None:
    expected_products = {
        _json(path)["opportunity"]["id"]
        for path in (PROJECT_ROOT / "data/snapshots/public").glob("*.json")
    } | {
        _json(path)["opportunity_id"]
        for path in (PROJECT_ROOT / "data/cases/briefs").glob("*.json")
    }
    expected_scenarios = {
        _json(path)["scenario_id"]
        for path in (PROJECT_ROOT / "data/synthetic").glob("*.json")
    }
    assert {node.id for node in _nodes(projection, "Product")} == expected_products
    assert {node.id for node in _nodes(projection, "Scenario")} == expected_scenarios


def test_candidate_graph_scopes_aliases_and_sources_are_exact(projection) -> None:
    steel = "SYN-MINISTRY-STEEL-001"
    pp = "SYN-MINISTRY-PP-001"
    a_plant = "PLANT-8932de539dd9d7d8"
    a_line = "LINE-7315366f6a9166d8"
    nodes = {node.id: node for node in projection.nodes}
    assert nodes[f"PLANT-{steel}"].properties["canonical_entity_id"] == a_plant
    assert nodes[f"LINE-{steel}"].properties["canonical_entity_id"] == a_line
    assert f"{steel}::plant::{a_plant}" not in nodes
    assert f"{steel}::line::{a_line}" not in nodes
    assert nodes[f"{pp}::plant::{a_plant}"].properties["scenario_id"] == pp
    assert nodes[f"PLANT-{pp}"].properties.get("canonical_entity_id") is None
    fact = nodes[f"{steel}::candidate_fact::FACT-CUS-STEEL-A"]
    assert fact.properties["record_origin"] == "DIRECT_RECORD"
    assert fact.properties["subject_id"] == a_plant
    assert fact.properties["source_refs"][0]["pointer"].endswith("FACT-CUS-STEEL-A")
    candidate_edges = [edge for edge in projection.edges
                       if edge.properties.get("attribution_scope") == "CANDIDATE_DISCOVERY"
                       and edge.type == "ADJACENT_TO"]
    assert {edge.source for edge in candidate_edges if edge.target == "SAU-H0-721049"} == {
        f"PLANT-{steel}", f"{steel}::plant::PLANT-b24ad239aa497c75",
    }
    assert not any(edge.source.startswith("LINE-") and edge.type in {
        "HAS_CAPABILITY", "CERTIFIED_TO", "ADJACENT_TO"}
        for edge in projection.edges)


def test_graph_context_rejects_foreign_subject_and_stays_unavailable(projection) -> None:
    from ior_mvp.graph.service import GraphNotFound, GraphService

    service = GraphService(None, artifact_projection_id=projection.projection_id,
                           projection=projection)
    context = {
        "company_id": "COMPANY-ed24005b198e52e5",
        "plant_id": "PLANT-8932de539dd9d7d8",
        "line_id": "LINE-7315366f6a9166d8",
        "requirement_item_id": "width_mm",
    }
    result = service.view("adjacency", "SAU-H0-721049", "simulated", context)
    assert result["graph_status"] == "GRAPH_UNAVAILABLE"
    assert result["nodes"] == result["edges"] == []
    assert result["focus_element_id"] == "LINE-SYN-MINISTRY-STEEL-001"
    assert result["context"] == context
    with pytest.raises(GraphNotFound, match="GRAPH_CONTEXT_NOT_FOUND"):
        service.view("adjacency", "SAU-H0-390210", "simulated", context)
    with pytest.raises(GraphNotFound, match="GRAPH_CONTEXT_NOT_FOUND"):
        service.view("adjacency", "SAU-H0-721049", "public", context)
    wrong = {**context, "plant_id": "PLANT-b24ad239aa497c75"}
    with pytest.raises(GraphNotFound, match="GRAPH_CONTEXT_NOT_FOUND"):
        service.view("adjacency", "SAU-H0-721049", "simulated", wrong)


def test_available_adjacency_focus_uses_exact_candidate_source_table(projection) -> None:
    from types import SimpleNamespace

    from ior_mvp.graph.engine_feed import adjacency_explanation
    from ior_mvp.graph.service import GraphService

    def rows(_spec, _view, opportunity_id, mode, scenario_id):
        result = adjacency_explanation(
            projection, opportunity_id,
            branch=(mode, scenario_id),
        )
        return [{"producer_id": producer_id} for producer_id in result["producer_ids"]]

    service = GraphService(
        SimpleNamespace(target="local"),
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {"projection_id": projection.projection_id},
        view_reader=rows,
    )
    context = {
        "company_id": "COMPANY-ed24005b198e52e5",
        "plant_id": "PLANT-8932de539dd9d7d8",
        "line_id": "LINE-7315366f6a9166d8",
        "requirement_item_id": "width_mm",
    }
    result = service.view("adjacency", "SAU-H0-721049", "simulated", context)
    assert result["graph_status"] == "AVAILABLE"
    assert result["focus_element_id"] == "LINE-SYN-MINISTRY-STEEL-001"
    node_ids = {node["id"] for node in result["nodes"]}
    assert result["focus_element_id"] in node_ids
    assert any(node["label"] == "Capability"
               and node["properties"].get("requirement_item_id") == "width_mm"
               for node in result["nodes"])
    assert all(edge["type"] not in {"CERTIFIED_TO", "ADJACENT_TO", "HAS_CAPABILITY"}
               for edge in result["edges"] if edge["source"] == result["focus_element_id"])


def test_public_elements_have_public_sentinel_and_false_flag(projection) -> None:
    public_nodes = [
        node for node in projection.nodes if not node.properties["synthetic_flag"]
    ]
    assert public_nodes
    assert {node.properties["scenario_id"] for node in public_nodes} == {"PUBLIC"}
    public_edges = [
        edge for edge in projection.edges if not edge.properties["synthetic_flag"]
    ]
    assert public_edges
    assert {edge.properties["scenario_id"] for edge in public_edges} == {"PUBLIC"}


def test_synthetic_elements_carry_scenario_id_class_d_and_display_labels(
    projection,
) -> None:
    synthetic = [
        node for node in projection.nodes if node.properties["synthetic_flag"]
    ]
    assert synthetic
    assert all(node.properties["evidence_class"] == "D" for node in synthetic)
    assert all(node.properties["scenario_id"] != "PUBLIC" for node in synthetic)
    assert all(node.properties["display_label"] for node in synthetic)
    assert all(node.properties["display_label_ar"] for node in synthetic)
    assert {
        node.properties["scenario_id"]
        for node in _nodes(projection, "CustomerSegment")
    } == {
        node.id for node in _nodes(projection, "Scenario")
    }


def test_no_public_edge_ends_at_a_synthetic_node(projection) -> None:
    nodes = {node.id: node for node in projection.nodes}
    for edge in projection.edges:
        if edge.properties["synthetic_flag"] is False:
            assert nodes[edge.source].properties["synthetic_flag"] is False
            assert nodes[edge.target].properties["synthetic_flag"] is False


def test_tariff_marker_when_no_complete_unit_and_zero_classified_as(
    projection,
) -> None:
    assert {node.id for node in _nodes(projection, "TariffLine")} == {
        "TARIFF-SA12-UNAVAILABLE"
    }
    assert not [edge for edge in projection.edges if edge.type == "CLASSIFIED_AS"]


def test_tariff_lines_from_complete_unit_double() -> None:
    case = _json(PROJECT_ROOT / "data/snapshots/public/SAU-H0-721049.json")
    graph = build_evidence_layer(
        public_cases={case["opportunity"]["id"]: case},
        scenarios={},
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[
            {
                "snapshot_id": "TARIFF-SAU-TEST-2026-01-01",
                "as_of_date": "2026-01-01",
                "coverage": {"status": "COMPLETE"},
                "evidence": [{"passport_id": "TARIFF-PASSPORT"}],
                "rows": [
                    {
                        "national_code": "721049000000",
                        "hs6": "721049",
                        "description": "Test line",
                        "duty_rate": "5%",
                    }
                ],
            }
        ],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )
    assert {node.id for node in _nodes(graph, "TariffLine")} == {
        "TARIFF-SA12-721049000000"
    }
    classified = [edge for edge in graph.edges if edge.type == "CLASSIFIED_AS"]
    assert [(edge.source, edge.target) for edge in classified] == [
        ("SAU-H0-721049", "TARIFF-SA12-721049000000")
    ]


def test_specification_marker_when_target_spec_unavailable(projection) -> None:
    markers = [
        node
        for node in _nodes(projection, "Specification")
        if node.properties.get("status") == "UNAVAILABLE"
    ]
    assert {node.properties["opportunity_id"] for node in markers} == {
        node.id for node in _nodes(projection, "Product")
    }


def test_entities_union_by_id_and_conflict_is_error(projection) -> None:
    expected = {}
    artifacts = [
        _json(path)
        for path in (PROJECT_ROOT / "data/entities/resolution").glob("*.json")
    ]
    for artifact in artifacts:
        for entity in artifact["entities"]:
            expected[entity["entity_id"]] = entity["entity_type"].title().replace(
                "Productionline", "ProductionLine"
            )
    actual = {
        node.id: node.label
        for node in projection.nodes
        if node.properties.get("identity_basis") == "ENTITY_ID_V1"
    }
    assert expected.items() <= actual.items()

    conflict = deepcopy(artifacts[0])
    conflict["entities"][0]["primary_name_en"] = "Conflicting name"
    with pytest.raises(GraphProjectionError, match="entity"):
        build_evidence_layer(
            public_cases={},
            scenarios={},
            entity_artifacts=[artifacts[0], conflict],
            briefs=[],
            tariff_snapshots=[],
            tariff_attempts=[],
            projection_id="GRAPH-TEST",
            engine_run_id="ENGINE-TEST",
            inputs=[],
        )


def test_producer_without_entity_gets_snapshot_label_identity(projection) -> None:
    generated = [
        node
        for node in _nodes(projection, "Company")
        if node.properties.get("identity_basis") == "SNAPSHOT_PRODUCER_LABEL"
    ]
    assert generated
    assert all(node.id.startswith("PRODUCER-") for node in generated)


def test_evidence_nodes_equal_passports_and_synthetic_rows(projection) -> None:
    expected = set()
    for path in (PROJECT_ROOT / "data/snapshots/public").glob("*.json"):
        expected.update(row["evidence_id"] for row in _json(path)["evidence"])
    for path in (PROJECT_ROOT / "data/synthetic").glob("*.json"):
        expected.update(
            row["evidence_id"] for row in synthetic_evidence_rows(_json(path))
        )
    actual = {node.id for node in _nodes(projection, "Evidence")}
    assert expected <= actual


def test_unlocked_by_edges_from_shared_enabler_block_with_derived_delta_nv() -> None:
    public = _json(PROJECT_ROOT / "data/snapshots/public/SAU-H0-721049.json")
    scenario_a = _json(PROJECT_ROOT / "data/synthetic/SYN-MINISTRY-STEEL-001.json")
    public_b = deepcopy(public)
    public_b["opportunity"]["id"] = "SAU-H0-721050"
    public_b["opportunity"]["hs6"] = "721050"
    public_b["snapshot_id"] = "PUBLIC-SAU-H0-721050-2026-08-31"
    scenario_b = deepcopy(scenario_a)
    scenario_b["scenario_id"] = "SYN-TEST-B"
    scenario_b["opportunity_id"] = "SAU-H0-721050"
    scenario_a["scenario_version"] = "2.1.0"
    scenario_b["scenario_version"] = "2.1.0"
    block = {
        "enabler_id": "ENABLER-SYN-TEST-001",
        "enabler_kind": "shared_laboratory",
        "label": {
            "en": "Shared laboratory (synthetic design basis)",
            "ar": "مختبر مشترك (أساس تصميم محاكى)",
        },
        "constraint_classes_addressed": ["capacity_or_availability"],
        "removes_binding_constraint": True,
        "unlock_probability": 0.5,
        "dependency_share": 0.5,
        "enabler_cost_m_sar": 10.0,
        "valuation_route_code": 5,
        "components": {
            "technical_feasibility_confirmed": True,
            "investment_already_approved_or_financed": False,
            "proceeds_without_intervention": False,
            "policy_prohibition_identified": False,
            "distortion_unacceptable": False,
            "intervention_proportionate_to_constraint": True,
            "competition": {
                "existing_effective_capacity_kt": 0.0,
                "proposed_incremental_capacity_kt": 1.0,
                "downside_demand_kt": 1.0,
            },
        },
        "basis": "DEMO_GENERATOR test double",
    }
    scenario_a["synthetic_inputs"]["shared_enabler"] = deepcopy(block)
    scenario_b["synthetic_inputs"]["shared_enabler"] = deepcopy(block)
    graph = build_evidence_layer(
        public_cases={
            public["opportunity"]["id"]: public,
            public_b["opportunity"]["id"]: public_b,
        },
        scenarios={
            scenario_a["opportunity_id"]: scenario_a,
            scenario_b["opportunity_id"]: scenario_b,
        },
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )
    unlocked = [edge for edge in graph.edges if edge.type == "UNLOCKED_BY"]
    assert len(unlocked) == 2
    assert all(
        edge.properties["dependent_incremental_national_value_m_sar"] == 198.0
        for edge in unlocked
    )
    assert {edge.target for edge in unlocked} == {"ENABLER-SYN-TEST-001"}


def test_enabler_declaration_conflict_is_error() -> None:
    public = _json(PROJECT_ROOT / "data/snapshots/public/SAU-H0-721049.json")
    scenario_a = _json(PROJECT_ROOT / "data/synthetic/SYN-MINISTRY-STEEL-001.json")
    scenario_b = deepcopy(scenario_a)
    scenario_b["scenario_id"] = "SYN-TEST-B"
    scenario_a["scenario_version"] = "2.1.0"
    scenario_b["scenario_version"] = "2.1.0"
    block = {
        "enabler_id": "ENABLER-SYN-TEST-001",
        "enabler_kind": "shared_laboratory",
        "label": {"en": "Test", "ar": "اختبار"},
        "constraint_classes_addressed": ["capacity_or_availability"],
        "removes_binding_constraint": True,
        "unlock_probability": 0.5,
        "dependency_share": 0.5,
        "enabler_cost_m_sar": 10.0,
        "valuation_route_code": 5,
        "components": {
            "technical_feasibility_confirmed": True,
            "investment_already_approved_or_financed": False,
            "proceeds_without_intervention": False,
            "policy_prohibition_identified": False,
            "distortion_unacceptable": False,
            "intervention_proportionate_to_constraint": True,
            "competition": {
                "existing_effective_capacity_kt": 0.0,
                "proposed_incremental_capacity_kt": 1.0,
                "downside_demand_kt": 1.0,
            },
        },
        "basis": "test",
    }
    scenario_a["synthetic_inputs"]["shared_enabler"] = deepcopy(block)
    scenario_b["synthetic_inputs"]["shared_enabler"] = deepcopy(block)
    scenario_b["synthetic_inputs"]["shared_enabler"]["enabler_cost_m_sar"] = 11.0
    with pytest.raises(GraphProjectionError, match="ENABLER_DECLARATION_CONFLICT"):
        build_evidence_layer(
            public_cases={public["opportunity"]["id"]: public},
            scenarios={"a": scenario_a, "b": scenario_b},
            entity_artifacts=[],
            briefs=[],
            tariff_snapshots=[],
            tariff_attempts=[],
            projection_id="GRAPH-TEST",
            engine_run_id="ENGINE-TEST",
            inputs=[],
        )


def test_supports_codes_on_supported_by_evidence_edges(projection) -> None:
    edges = [
        edge
        for edge in projection.edges
        if edge.type == "SUPPORTED_BY_EVIDENCE"
        and edge.properties.get("supports")
    ]
    assert edges
    assert all(
        isinstance(edge.properties["supports"], list)
        and all(isinstance(value, str) for value in edge.properties["supports"])
        for edge in edges
    )


def test_published_standards_are_projected_without_asserting_certification(
    projection,
) -> None:
    standards = _nodes(projection, "Standard")
    assert any(
        node.properties.get("standard") == "SASO-ASTM A653/A653M"
        for node in standards
    )
    standard_ids = {node.id for node in standards}
    assert not [
        edge
        for edge in projection.edges
        if edge.type == "CERTIFIED_TO" and edge.target in standard_ids
    ]
    assert any(
        edge.type == "SUPPORTED_BY_EVIDENCE"
        and edge.source in standard_ids
        for edge in projection.edges
    )
    synthetic_standards = [
        node
        for node in standards
        if node.properties["synthetic_flag"] is True
    ]
    assert synthetic_standards
    assert any(
        edge.type == "CONSTRAINED_BY"
        and edge.target in {node.id for node in synthetic_standards}
        for edge in projection.edges
    )


def _node_properties(identity: str, *, scenario_id: str, synthetic: bool) -> dict:
    return {
        "id": identity,
        "evidence_id": f"E-{identity}",
        "as_of": "2026-01-01",
        "evidence_class": "D" if synthetic else "C",
        "synthetic_flag": synthetic,
        "scenario_id": scenario_id,
        "origin_kind": "SCENARIO" if synthetic else "PUBLIC_SNAPSHOT",
        "origin_ref": scenario_id,
        "derived": False,
        "projection_id": "GRAPH-TEST",
        "evidence_ids": [f"E-{identity}"],
    }


def _need_analysis(
    product_id: str,
    *,
    mode: str = "public",
    scenario_id: str = "PUBLIC",
) -> dict:
    return {
        "opportunity_id": product_id,
        "mode": mode,
        "scenario_id": scenario_id,
        "snapshot_id": "SNAP",
        "as_of_date": "2026-01-01",
        "rules": [],
        "capability": {
            "d_star": None,
            "known_weight_coverage": 0.8,
            "unknown_weight": 0.2,
            "route_band": None,
            "route_publishable": False,
        },
        "decision": {
            "state": "INVESTIGATE",
            "route_code": 5,
            "confidence": "C",
            "decision_reason_code": "TEST",
            "screening_disposition": "INVESTIGATE",
            "preferred_hypothesis": {"route_code": 5},
            "route_hypotheses": [
                {
                    "route_code": 5,
                    "route_key": "brownfield",
                    "status": "candidate",
                    "reason_codes": [],
                    "precedence": {},
                }
            ],
        },
        "evidence_needs": [
            {
                "need_code": "capacity/availability/allocation",
                "variant": "supply",
                "blocked_field": "domestic_supply_or_capability",
                "route_effect": "Can distinguish capacity routes.",
                "numeric_evsi": None,
                "evidence_ids": ["E-NEED-SUPPLY"],
            },
            {
                "need_code": "qualification/profile hard gates",
                "variant": "gate",
                "blocked_field": "hard_regulatory_or_process_gate",
                "route_effect": "Can resolve a hard gate.",
                "numeric_evsi": None,
                "evidence_ids": ["E-NEED-GATE"],
            },
            {
                "need_code": "line-level production or producer-grade matrix",
                "variant": "idle",
                "blocked_field": "idle_equivalent_domestic_capacity",
                "route_effect": "Can distinguish idle capacity.",
                "numeric_evsi": None,
                "evidence_ids": ["E-NEED-IDLE"],
            },
            {
                "need_code": "target specification/application",
                "variant": "specification",
                "blocked_field": "target_specification",
                "route_effect": "Can establish target demand.",
                "numeric_evsi": None,
                "evidence_ids": ["E-NEED-SPEC"],
            },
            {
                "need_code": "route economics",
                "variant": "economics",
                "blocked_field": "economics",
                "route_effect": "Can determine whether the route proceeds.",
                "numeric_evsi": None,
                "evidence_ids": ["E-NEED-ECON"],
            },
        ],
    }


def project_sorted_capability_needs(*, spec_scenario_id: str = "PUBLIC") -> GraphProjection:
    """Project several sorted capabilities plus one specification target."""
    product_id = "SAU-TEST"
    projection = GraphProjection(
        projection_id="GRAPH-TEST",
        as_of="2026-01-01",
        inputs=[],
        engine={"engine_run_id": "ENGINE-TEST"},
    )
    projection.nodes.append(
        GraphNode(
            "Product",
            product_id,
            _node_properties(product_id, scenario_id="PUBLIC", synthetic=False),
        )
    )
    for dimension in (
        "capacity_time_window",
        "utilities_ehs_permitting",
        "zzz_late",
    ):
        identity = capability_id(product_id, dimension)
        projection.nodes.append(
            GraphNode(
                "Capability",
                identity,
                _node_properties(identity, scenario_id="PUBLIC", synthetic=False),
            )
        )
    spec_id = f"SPEC-{product_id}-TARGET"
    projection.nodes.append(
        GraphNode(
            "Specification",
            spec_id,
            _node_properties(
                spec_id,
                scenario_id=spec_scenario_id,
                synthetic=False,
            ),
        )
    )
    analysis = _need_analysis(product_id)
    return project_engine_outputs(
        projection,
        {(product_id, "public"): analysis},
    )


def _need_edges(projection: GraphProjection) -> list:
    return [
        edge
        for edge in projection.edges
        if edge.type == "CONSTRAINED_BY" and edge.properties.get("need_code")
    ]


def test_broad_needs_do_not_guess_the_first_sorted_capability() -> None:
    projection = project_sorted_capability_needs()
    product_id = "SAU-TEST"
    guessed = capability_id(product_id, "capacity_time_window")
    edges = _need_edges(projection)
    broad = [
        edge
        for edge in edges
        if edge.properties["blocked_field"] in _BROAD_NEED_FIELDS
    ]
    assert len(broad) == 3
    assert {edge.target for edge in broad} == {product_id}
    assert all(edge.target != guessed for edge in edges)
    assert all(edge.properties["evidence_ids"] for edge in broad)
    assert {edge.properties["need_code"] for edge in broad} == {
        "capacity/availability/allocation",
        "qualification/profile hard gates",
        "line-level production or producer-grade matrix",
    }


def test_genuine_specification_and_route_targets_stay_in_scope() -> None:
    projection = project_sorted_capability_needs()
    edges = {edge.properties["blocked_field"]: edge for edge in _need_edges(projection)}
    assert edges["target_specification"].target == "SPEC-SAU-TEST-TARGET"
    assert edges["economics"].target == "INT-SAU-TEST-route-5"
    assert edges["target_specification"].properties["evidence_ids"] == [
        "E-NEED-SPEC"
    ]
    assert edges["economics"].properties["evidence_ids"] == ["E-NEED-ECON"]


def test_out_of_scope_specification_does_not_become_the_need_target() -> None:
    projection = project_sorted_capability_needs(spec_scenario_id="OTHER")
    edges = {edge.properties["blocked_field"]: edge for edge in _need_edges(projection)}
    assert edges["target_specification"].target == "SAU-TEST"


def test_repository_broad_needs_target_products_on_all_22_branches(projection) -> None:
    opportunities = (
        "SAU-H0-721049",
        "SAU-H0-390210",
        "SAU-H6-721061",
        "SAU-H6-721012",
        "SAU-H6-760711",
        "SAU-H6-760429",
        "SAU-H6-392010",
        "SAU-H6-294110",
        "SAU-H6-294120",
        "SAU-H6-310430",
        "SAU-H6-310510",
    )
    scenarios = {
        node.properties["opportunity_id"]: node.id
        for node in _nodes(projection, "Scenario")
    }
    nodes = {node.id: node for node in projection.nodes}
    checked = 0
    for product_id in opportunities:
        for mode, scenario_id in (
            ("public", None),
            ("simulated", scenarios[product_id]),
        ):
            branch = "public" if mode == "public" else ("simulated", scenario_id)
            rows = evidence_linkage(projection, product_id, branch=branch)
            assert rows
            for row in rows:
                assert isinstance(row["evidence_ids"], list)
                assert "route_effect" in row
                if row["blocked_field"] in _BROAD_NEED_FIELDS:
                    assert row["target_id"] == product_id
                    assert "capacity_time_window" not in row["target_id"]
                if row["blocked_field"] in {
                    "target_specification",
                    "demand_at_required_specification",
                }:
                    assert row["target_id"].startswith("SPEC-") or (
                        row["target_id"] == product_id
                    )
            checked += 1
    assert checked == 22
    broad_capability_edges = [
        edge
        for edge in projection.edges
        if edge.type == "CONSTRAINED_BY"
        and edge.properties.get("need_code")
        and edge.properties.get("blocked_field") in _BROAD_NEED_FIELDS
        and nodes[edge.source].label == "Decision"
        and nodes[edge.target].label == "Capability"
    ]
    assert broad_capability_edges == []


def test_streptomycin_gate_scopes_keep_separate_sources(projection) -> None:
    scenario_id = "SYN-MINISTRY-STREPTOMYCIN-API-001"
    gate_id = capability_id(scenario_id, "GATE-effluent")
    node = next(node for node in projection.nodes if node.id == gate_id)
    assert node.properties["status"] == "KNOWN_FAILURE"
    assert node.properties["declaration"] == (
        "known failure: synthetic environmental-effluent gate is unsatisfiable"
    )
    assert node.properties["evidence_ids"] == [f"{scenario_id}::hard_gates"]
    scenario = next(node for node in projection.nodes if node.id == scenario_id)
    assert scenario.properties["decision_specific_hard_gates"]["effluent"] == {
        "status": "KNOWN_FAILURE",
        "declaration": "known failure: synthetic environmental-effluent gate is unsatisfiable",
        "evidence_id": f"{scenario_id}::decision_specific_hard_gates",
    }


def test_conflicting_profile_and_decision_gate_declarations_keep_their_scopes() -> None:
    public = deepcopy(get_public_case("SAU-H6-294120"))
    scenario = _json(
        PROJECT_ROOT / "data/synthetic/SYN-MINISTRY-STREPTOMYCIN-API-001.json"
    )
    scenario["synthetic_inputs"]["hard_gates"]["effluent"] = (
        "resolved: synthetic profile declaration"
    )
    graph = build_evidence_layer(
        public_cases={"SAU-H6-294120": public},
        scenarios={scenario["scenario_id"]: scenario},
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )
    scenario_id = scenario["scenario_id"]
    gate = next(
        node for node in graph.nodes
        if node.id == capability_id(scenario_id, "GATE-effluent")
    )
    scenario_node = next(node for node in graph.nodes if node.id == scenario_id)

    assert gate.properties["status"] == "RESOLVED"
    assert gate.properties["declaration"] == "resolved: synthetic profile declaration"
    assert gate.properties["evidence_ids"] == [f"{scenario_id}::hard_gates"]
    assert scenario_node.properties["decision_specific_hard_gates"]["effluent"] == {
        "status": "KNOWN_FAILURE",
        "declaration": "known failure: synthetic environmental-effluent gate is unsatisfiable",
        "evidence_id": f"{scenario_id}::decision_specific_hard_gates",
    }


def test_decision_only_gate_is_attributed_on_existing_scenario_node() -> None:
    public = _json(PROJECT_ROOT / "data/snapshots/public/SAU-H0-721049.json")
    scenario = _json(PROJECT_ROOT / "data/synthetic/SYN-MINISTRY-STEEL-001.json")
    graph = build_evidence_layer(
        public_cases={"SAU-H0-721049": public},
        scenarios={scenario["scenario_id"]: scenario},
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )
    scenario_id = scenario["scenario_id"]
    node = next(node for node in graph.nodes if node.id == scenario_id)
    expected = scenario["synthetic_inputs"]["decision_specific_hard_gates"][
        "exact imported specification"
    ]

    assert node.properties["decision_specific_hard_gates"][
        "exact imported specification"
    ] == {
        "status": "RESOLVED",
        "declaration": expected,
        "evidence_id": f"{scenario_id}::decision_specific_hard_gates",
    }
    assert not any(
        candidate.id == capability_id(scenario_id, "GATE-exact imported specification")
        for candidate in graph.nodes
    )


def _steel_public_layer():
    public = _json(PROJECT_ROOT / "data/snapshots/public/SAU-H0-721049.json")
    return public, build_evidence_layer(
        public_cases={public["opportunity"]["id"]: public},
        scenarios={},
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )


def _producer_id(graph, evidence_id: str) -> str:
    matches = [
        node.id
        for node in graph.nodes
        if node.label == "Company"
        and evidence_id in node.properties.get("evidence_ids", [])
    ]
    assert len(matches) == 1
    return matches[0]


def test_hadeed_does_not_inherit_unicoil_process_or_certification() -> None:
    """Original defect: opportunity signals were copied onto every producer."""
    _public, graph = _steel_public_layer()
    hadeed = _producer_id(graph, "S-HADEED")
    unicoil = _producer_id(graph, "S-UNICOIL-EPD")
    inherited = [
        edge
        for edge in graph.edges
        if edge.source == hadeed
        and edge.type in {"USES_PROCESS", "CERTIFIED_TO"}
        and "S-UNICOIL-EPD" in edge.properties.get("evidence_ids", [])
    ]
    own_process = [
        edge
        for edge in graph.edges
        if edge.source == hadeed
        and edge.type == "USES_PROCESS"
        and "S-HADEED" in edge.properties.get("evidence_ids", [])
    ]
    unicoil_cert = [
        edge
        for edge in graph.edges
        if edge.source == unicoil and edge.type == "CERTIFIED_TO"
    ]

    assert inherited == []
    assert own_process
    assert unicoil_cert
    assert all(
        "S-HADEED" not in edge.properties.get("evidence_ids", [])
        for edge in unicoil_cert
    )


def test_public_adjacency_is_per_producer_and_keeps_reference_summary() -> None:
    from ior_mvp.graph.derived import project_engine_outputs
    from ior_mvp.graph.engine_feed import adjacency_explanation
    from ior_mvp.graph.projection import _public_analysis

    public, graph = _steel_public_layer()
    analysis = _public_analysis(public, shared_enabler=None)
    project_engine_outputs(
        graph,
        {(public["opportunity"]["id"], "public"): analysis},
    )
    hadeed = _producer_id(graph, "S-HADEED")
    unicoil = _producer_id(graph, "S-UNICOIL-EPD")
    rows = {
        edge.source: edge
        for edge in graph.edges
        if edge.type == "ADJACENT_TO" and edge.target == "SAU-H0-721049"
    }
    reference = next(
        node
        for node in graph.nodes
        if node.id == "ENGINE-EVIDENCE-SAU-H0-721049-public"
    )
    explanation = adjacency_explanation(
        graph,
        "SAU-H0-721049",
        branch="public",
    )

    assert rows[hadeed].properties["fired"] is False
    assert rows[hadeed].properties["qualifying_signal_count"] == 0
    assert rows[hadeed].properties["attribution_scope"] == "PRODUCER_DISCLOSURE"
    assert rows[unicoil].properties["fired"] is True
    assert rows[unicoil].properties["qualifying_signal_count"] == 4
    assert reference.properties["attribution_scope"] == "REFERENCE_CASE"
    assert reference.properties["r9s_fired"] is True
    assert reference.properties["r9s_qualifying_signal_count"] == 4
    assert explanation["fired"] is True
    assert explanation["qualifying_signal_count"] == 4
    assert explanation["producer_rows"][hadeed]["fired"] is False
    assert explanation["producer_rows"][unicoil]["qualifying_signal_count"] == 4


def test_public_pp_producer_family_and_sole_owned_signals() -> None:
    from ior_mvp.graph.engine_feed import adjacency_explanation

    graph = build_repository_projection(PROJECT_ROOT)
    result = adjacency_explanation(graph, "SAU-H0-390210", branch="public")
    expected = {
        "COMPANY-f2d406af94a8aac1": (True, True, 1, "ADJACENT_PLANT_WITH_SIGNALS", ["P-SABIC"]),
        "COMPANY-0f8e69531f415144": (True, False, 0, "NO_DEFENSIBLE_SIGNAL", []),
        "COMPANY-f3a50c477f158420": (True, False, 0, "NO_DEFENSIBLE_SIGNAL", []),
    }
    assert set(result["producer_rows"]) == set(expected)
    for producer_id, (family, fired, count, code, signal_ids) in expected.items():
        row = result["producer_rows"][producer_id]
        assert row["same_process_family"] is family
        assert row["fired"] is fired
        assert row["execution"] == "FULL"
        assert row["qualifying_signal_count"] == count
        assert row["result_code"] == code
        assert row["signal_evidence_ids"] == signal_ids
        assert {item["evidence_ids"][0] for item in row["signals"]} == set(signal_ids)
        assert row["attribution_scope"] == "PRODUCER_DISCLOSURE"
    assert result["fired"] is True
    assert result["qualifying_signal_count"] == 2


def test_public_aluminium_exact_producer_rows_preserve_evidence_and_scope(projection) -> None:
    expected = {
        "COMPANY-69d10bdb78064a59": (
            "REL-86e0f9feaada056b9067", "P-ALUPCO-760429"
        ),
        "PRODUCER-public-sau-h6-760429-2026-09-12-2": (
            "REL-514c0b83c09734657191", "P-TALCO-760429"
        ),
    }
    rows = {
        edge.source: edge
        for edge in projection.edges
        if edge.type == "ADJACENT_TO"
        and edge.target == "SAU-H6-760429"
        and edge.properties.get("attribution_scope") == "PRODUCER_DISCLOSURE"
    }
    assert set(rows) == set(expected)
    for producer_id, (key, evidence_id) in expected.items():
        edge = rows[producer_id]
        row = edge.properties
        assert edge.key == key
        assert row["key"] == key
        assert row["attribution_scope"] == "PRODUCER_DISCLOSURE"
        assert row["evidence_ids"] == [
            "ENGINE-EVIDENCE-SAU-H6-760429-public", evidence_id
        ]
        assert row["scenario_id"] == "PUBLIC"
        assert row["synthetic_flag"] is False
        assert row["same_process_family"] is True
        assert row["execution"] == "FULL"
        assert row["fired"] is False
        assert row["qualifying_signal_count"] == 0
        assert row["result_code"] == "NO_DEFENSIBLE_SIGNAL"
        assert row["signal_evidence_ids"] == []
        assert row["signals"] == []


def test_public_family_aliases_cover_actual_repository_case_loader_inputs() -> None:
    from ior_mvp.graph.projection import (
        _PUBLIC_SOURCE_FAMILY_IDS,
        _load_repository_cases,
    )

    cases, _briefs = _load_repository_cases(PROJECT_ROOT)
    labels_by_case = {
        opportunity_id: [
            record.get("process_family")
            for record in case["domestic_capability"].get("producer_evidence", [])
        ]
        for opportunity_id, case in cases.items()
    }
    assert any(labels_by_case.values())
    unmapped = [
        (opportunity_id, label)
        for opportunity_id, labels in labels_by_case.items()
        for label in labels
        if label not in _PUBLIC_SOURCE_FAMILY_IDS
    ]
    assert not unmapped


@pytest.mark.parametrize(
    "label",
    ["technical_plastics", "technical_plastics_conversion", "unmapped_resin", None],
)
def test_public_pp_unmapped_source_family_is_unknown_not_false(label) -> None:
    from ior_mvp.graph.projection import _public_analysis, public_producer_adjacency

    public = deepcopy(get_public_case("SAU-H0-390210"))
    public["domestic_capability"]["producer_evidence"][0]["process_family"] = label
    rows = public_producer_adjacency(_public_analysis(public))
    assert rows is not None
    sabic = rows[0]
    assert sabic["same_process_family"] is None
    assert sabic["execution"] == "DISABLED"
    assert sabic["fired"] is None
    assert sabic["qualifying_signal_count"] == 1
    assert sabic["result_code"] == "NO_DEFENSIBLE_SIGNAL"
    assert sabic["signal_evidence_ids"] == ["P-SABIC"]


def test_public_pp_missing_target_and_conversion_family_do_not_invent_match() -> None:
    from ior_mvp.graph.projection import _public_analysis, public_producer_adjacency
    from ior_mvp.screening.config import product_families_config

    public = deepcopy(get_public_case("SAU-H0-390210"))
    missing = deepcopy(product_families_config())
    missing["families"]["polypropylene_primary_forms"]["hs4_headings"] = []
    missing["families"]["polypropylene_primary_forms"]["status"] = "MEMBERSHIP_UNAVAILABLE"
    unknown = public_producer_adjacency(_public_analysis(public, product_families=missing))
    assert unknown is not None
    assert [(row["same_process_family"], row["execution"], row["fired"]) for row in unknown] == [
        (None, "DISABLED", None), (None, "DISABLED", None), (None, "DISABLED", None)
    ]

    public["opportunity"]["hs6"] = "392010"
    conversion = public_producer_adjacency(_public_analysis(public))
    assert conversion is not None
    assert [(row["same_process_family"], row["execution"], row["fired"]) for row in conversion] == [
        (False, "FULL", False), (False, "FULL", False), (False, "FULL", False)
    ]


def test_public_producer_signal_sources_are_exact_and_inspectable() -> None:
    from types import SimpleNamespace

    from ior_mvp.graph.engine_feed import adjacency_explanation
    from ior_mvp.graph.projection import _public_analysis
    from ior_mvp.graph.service import GraphService

    public, graph = _steel_public_layer()
    project_engine_outputs(
        graph,
        {(public["opportunity"]["id"], "public"): _public_analysis(public)},
    )
    unicoil = _producer_id(graph, "S-UNICOIL-EPD")
    hadeed = _producer_id(graph, "S-HADEED")
    source_signals = public["domestic_capability"]["coarse_adjacency_signals"]
    expected = [
        {
            "signal_type": signal["signal_type"],
            "description": signal["description"],
            "evidence_ids": signal["evidence_ids"],
        }
        for signal in source_signals
    ]
    result = adjacency_explanation(graph, "SAU-H0-721049", branch="public")
    assert result["producer_rows"][unicoil]["signals"] == expected
    assert result["producer_rows"][unicoil]["signal_evidence_ids"] == [
        "S-UNICOIL-EPD", "S-UNICOIL-SPEC"
    ]
    assert result["producer_rows"][unicoil]["attribution_scope"] == "PRODUCER_DISCLOSURE"
    assert result["producer_rows"][hadeed]["signals"] == []
    assert result["producer_rows"][hadeed]["signal_evidence_ids"] == []
    assert result["producer_rows"][hadeed]["evidence_ids"] == [
        "ENGINE-EVIDENCE-SAU-H0-721049-public", "S-HADEED"
    ]

    rows = [
        {"producer_id": producer, "fired": row["fired"]}
        for producer, row in result["producer_rows"].items()
    ]
    service = GraphService(
        SimpleNamespace(target="compose"),
        artifact_projection_id=graph.projection_id,
        projection=graph,
        status_reader=lambda _spec: {"projection_id": graph.projection_id,
                                      "counts": graph.counts,
                                      "synthetic_partition": {}},
        view_reader=lambda *_args: rows,
    )
    payload = service.view("adjacency", "SAU-H0-721049", "public")
    edges = payload["edges"]
    unicoil_adjacent = next(edge for edge in edges if edge["type"] == "ADJACENT_TO"
                            and edge["source"] == unicoil)
    assert unicoil_adjacent["properties"]["signals"] == expected
    assert unicoil_adjacent["properties"]["signal_evidence_ids"] == [
        "S-UNICOIL-EPD", "S-UNICOIL-SPEC"
    ]
    assert {
        edge["type"] for edge in edges
        if edge["source"] == unicoil and edge["type"] != "ADJACENT_TO"
    } == {"USES_PROCESS", "CERTIFIED_TO"}
    assert not any(
        "S-UNICOIL-EPD" in edge["properties"].get("evidence_ids", [])
        for edge in edges if edge["source"] == hadeed
    )
