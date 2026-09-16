"""Cypher 5 templates for deterministic graph loading and governed views."""

from __future__ import annotations

import re

from .model import EDGE_TYPES, LABELS


def _name(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).replace("-", "_").lower()


CONSTRAINT_QUERIES: tuple[str, ...] = tuple(
    (
        f"CREATE CONSTRAINT graph_{_name(label)}_id IF NOT EXISTS "
        f"FOR (n:`{label}`) REQUIRE n.id IS UNIQUE"
    )
    for label in LABELS
)

INDEXED_PROPERTIES: tuple[str, ...] = (
    "synthetic_flag",
    "scenario_id",
    "opportunity_id",
    "projection_id",
)

INDEX_QUERIES: tuple[str, ...] = tuple(
    (
        f"CREATE INDEX graph_{_name(label)}_{property_name} IF NOT EXISTS "
        f"FOR (n:`{label}`) ON (n.{property_name})"
    )
    for label in LABELS
    for property_name in INDEXED_PROPERTIES
)


def node_merge_query(label: str) -> str:
    """Return the parameterized MERGE query for one governed label."""
    if label not in LABELS:
        raise ValueError(f"Unknown graph label: {label}")
    return (
        "UNWIND $rows AS row "
        f"MERGE (n:`{label}` {{id: row.id}}) "
        "SET n = row.properties"
    )


def edge_merge_query(
    edge_type: str,
    source_label: str,
    target_label: str,
) -> str:
    """Return the parameterized MERGE query for one endpoint group."""
    if edge_type not in EDGE_TYPES:
        raise ValueError(f"Unknown graph edge type: {edge_type}")
    if source_label not in LABELS or target_label not in LABELS:
        raise ValueError("Unknown graph relationship endpoint label")
    return (
        "UNWIND $rows AS row "
        f"MATCH (a:`{source_label}` {{id: row.source}}) "
        f"MATCH (b:`{target_label}` {{id: row.target}}) "
        f"MERGE (a)-[r:`{edge_type}` {{key: row.key}}]->(b) "
        "SET r = row.properties"
    )


VIEW_QUERIES: dict[str, str] = {
    "adjacency": """
        MATCH (producer)-[adj:ADJACENT_TO]->(product:Product {id: $opportunity_id})
        WHERE (
          ($mode = 'public'
            AND producer.synthetic_flag = false
            AND adj.synthetic_flag = false
            AND product.synthetic_flag = false)
          OR
          ($mode = 'simulated'
            AND product.synthetic_flag = false
            AND adj.scenario_id = $scenario_id)
        )
        RETURN producer.id AS producer_id,
               adj.fired AS fired,
               adj.execution AS execution,
               adj.same_process_family AS same_process_family,
               adj.qualifying_signal_count AS qualifying_signal_count,
               adj.result_code AS result_code,
               adj.evidence_ids AS evidence_ids
        ORDER BY producer_id
    """,
    "route_blocking": """
        MATCH (route:Intervention)-[block:CONSTRAINED_BY]->(capability:Capability)
        WHERE route.opportunity_id = $opportunity_id
          AND route.mode = $mode
          AND (
            ($mode = 'public'
              AND route.synthetic_flag = false
              AND block.synthetic_flag = false
              AND capability.synthetic_flag = false)
            OR
            ($mode = 'simulated'
              AND route.scenario_id = $scenario_id
              AND block.scenario_id = $scenario_id
              AND capability.scenario_id = $scenario_id)
          )
        RETURN route.route_code AS route_code,
               route.id AS intervention_id,
               block.reason_code AS reason_code,
               capability.id AS capability_id,
               capability.capability_kind AS capability_kind,
               capability.dimension AS dimension,
               capability.gate AS gate,
               capability.state AS state,
               capability.status AS status,
               block.evidence_ids AS evidence_ids
        ORDER BY route_code, reason_code, capability_id
    """,
    "shared_enabler": """
        MATCH (dependent:Product)-[unlock:UNLOCKED_BY]->(enabler:Intervention)
        WHERE enabler.kind = 'shared_enabler'
          AND dependent.derived = false
          AND unlock.derived = false
          AND enabler.derived = false
          AND unlock.unlock_probability > 0
          AND unlock.dependency_share > 0
          AND unlock.dependent_incremental_national_value_m_sar > 0
          AND (
            ($mode = 'public'
              AND dependent.synthetic_flag = false
              AND unlock.synthetic_flag = false
              AND enabler.synthetic_flag = false
              AND unlock.scenario_id = 'PUBLIC'
              AND enabler.scenario_id = 'PUBLIC')
            OR
            ($mode = 'simulated'
              AND dependent.synthetic_flag = false
              AND unlock.synthetic_flag = true
              AND enabler.synthetic_flag = true
              AND unlock.evidence_class = 'D'
              AND enabler.evidence_class = 'D'
              AND $scenario_id IN enabler.scenario_ids
              AND unlock.scenario_id IN enabler.scenario_ids
              AND EXISTS {
                MATCH (membership:Scenario)
                WHERE membership.id = unlock.scenario_id
                  AND membership.opportunity_id = dependent.id
                  AND membership.synthetic_flag = true
                  AND membership.derived = false
              })
          )
        WITH enabler, dependent, unlock
        ORDER BY enabler.id, dependent.id
        WITH enabler,
             collect(dependent.id) AS dependent_opportunity_ids,
             count(dependent) AS counted_dependents,
             sum(
               unlock.unlock_probability
               * unlock.dependent_incremental_national_value_m_sar
               * unlock.dependency_share
             ) - enabler.enabler_cost_m_sar AS unlock_value_m_sar,
             collect(unlock.evidence_ids) AS nested_evidence_ids
        RETURN enabler.id AS enabler_id,
               enabler.enabler_kind AS enabler_kind,
               enabler.label_en AS label_en,
               enabler.label_ar AS label_ar,
               dependent_opportunity_ids,
               counted_dependents,
               unlock_value_m_sar,
               enabler.projection_id AS graph_projection_id,
               nested_evidence_ids
        ORDER BY enabler_id
    """,
    "evidence_to_change": """
        MATCH (decision:Decision)-[need:CONSTRAINED_BY]->(target)
        WHERE decision.opportunity_id = $opportunity_id
          AND decision.mode = $mode
          AND need.need_code IS NOT NULL
          AND (
            ($mode = 'public'
              AND decision.synthetic_flag = false
              AND need.synthetic_flag = false
              AND target.synthetic_flag = false)
            OR
            ($mode = 'simulated'
              AND decision.scenario_id = $scenario_id
              AND need.scenario_id = $scenario_id)
          )
        RETURN decision.id AS decision_id,
               target.id AS target_id,
               need.need_code AS need_code,
               need.variant AS variant,
               need.blocked_field AS blocked_field,
               need.route_effect AS route_effect,
               need.numeric_evsi AS numeric_evsi,
               need.evidence_ids AS evidence_ids
        ORDER BY need_code, variant, target_id
    """,
}

VERIFY_QUERIES: dict[str, str] = {
    "node_provenance_missing": """
        MATCH (n)
        WHERE n.evidence_id IS NULL
           OR n.as_of IS NULL
           OR n.evidence_class IS NULL
           OR n.synthetic_flag IS NULL
           OR n.scenario_id IS NULL
        RETURN count(n) AS count
    """,
    "edge_provenance_missing": """
        MATCH ()-[r]->()
        WHERE r.evidence_id IS NULL
           OR r.as_of IS NULL
           OR r.evidence_class IS NULL
           OR r.synthetic_flag IS NULL
           OR r.scenario_id IS NULL
        RETURN count(r) AS count
    """,
    "partition_violations": """
        MATCH (a)-[r]->(b)
        WHERE r.synthetic_flag = false
          AND (a.synthetic_flag = true OR b.synthetic_flag = true)
        RETURN count(r) AS count
    """,
    "projection_ids": """
        MATCH (n)
        RETURN collect(DISTINCT n.projection_id) AS projection_ids
    """,
    "synthetic_partition": """
        MATCH (n)
        RETURN sum(CASE WHEN n.synthetic_flag = false THEN 1 ELSE 0 END)
                 AS public_nodes,
               sum(CASE WHEN n.synthetic_flag = true THEN 1 ELSE 0 END)
                 AS synthetic_nodes
    """,
}
