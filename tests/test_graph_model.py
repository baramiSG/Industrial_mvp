from __future__ import annotations

import pytest

from ior_mvp.graph.model import (
    EDGE_TYPES,
    ENDPOINT_RULES,
    LABELS,
    V1_TO_V2_EDGE_MAPPING,
    V1_TO_V2_NODE_MAPPING,
    GraphModelError,
    assert_endpoint,
    capability_id,
    slug,
)


def test_exactly_nineteen_labels_and_fifteen_edge_types() -> None:
    assert len(LABELS) == 19
    assert len(set(LABELS)) == 19
    assert len(EDGE_TYPES) == 15
    assert len(set(EDGE_TYPES)) == 15
    assert set(ENDPOINT_RULES) == set(EDGE_TYPES)


def test_endpoint_rules_reject_unknown_pairs() -> None:
    assert_endpoint("Product", "USED_IN", "Application")
    assert_endpoint("CustomerSegment", "QUALIFIED_FOR", "Application")
    with pytest.raises(GraphModelError, match="endpoint"):
        assert_endpoint("Evidence", "USED_IN", "Product")
    with pytest.raises(GraphModelError, match="edge type"):
        assert_endpoint("Product", "UNKNOWN_EDGE", "Evidence")


def test_ids_are_deterministic_and_slug_is_stable() -> None:
    assert slug("  ISO/IEC 17025 — Laboratory ") == "iso-iec-17025-laboratory"
    assert slug("ISO/IEC 17025 — Laboratory") == slug(
        "  ISO/IEC 17025 — Laboratory "
    )
    assert capability_id("SAU-H0-721049", "core_process_route") == (
        "CAP-SAU-H0-721049-core-process-route"
    )


def test_v1_to_v2_mapping_table_is_total() -> None:
    old_nodes = {
        "Product",
        "Specification",
        "Application",
        "Standard",
        "Plant",
        "ProductionLine",
        "Process",
        "Equipment",
        "Certification",
        "Buyer",
        "Input",
        "Utility",
        "Technology",
        "Opportunity",
        "Intervention",
        "Evidence",
        "Decision",
    }
    old_edges = {
        "HAS_SPECIFICATION",
        "USED_IN",
        "REQUIRES_STANDARD",
        "PRODUCED_BY",
        "HAS_LINE",
        "USES_PROCESS",
        "REQUIRES_EQUIPMENT",
        "QUALIFIED_BY",
        "DEMANDED_BY",
        "DEPENDS_ON",
        "SUPPORTED_BY_EVIDENCE",
        "BLOCKED_BY",
        "UNLOCKED_BY",
        "ALTERNATIVE_TO",
    }
    assert set(V1_TO_V2_NODE_MAPPING) == old_nodes
    assert set(V1_TO_V2_EDGE_MAPPING) == old_edges
