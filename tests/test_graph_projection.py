from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.evidence import synthetic_evidence_rows
from ior_mvp.graph.projection import (
    GraphProjectionError,
    build_evidence_layer,
    build_repository_projection,
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
        "components": {},
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
    block = {
        "enabler_id": "ENABLER-SYN-TEST-001",
        "enabler_kind": "shared_laboratory",
        "label": {"en": "Test", "ar": "اختبار"},
        "constraint_classes_addressed": ["capacity_or_availability"],
        "removes_binding_constraint": True,
        "unlock_probability": 0.5,
        "dependency_share": 0.5,
        "enabler_cost_m_sar": 10.0,
        "components": {},
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
