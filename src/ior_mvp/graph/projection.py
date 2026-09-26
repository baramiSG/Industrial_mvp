"""Deterministic projection of governed records into the graph vocabulary."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from ior_mvp import __version__
from ior_mvp.capability import evaluate_capability
from ior_mvp.gate_status import classify_gate_status
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    synthetic_display_labels,
    synthetic_evidence_rows,
)
from ior_mvp.public_decision import compute_public_decision
from ior_mvp.public_snapshot import capability_hard_gate_names
from ior_mvp.scenario_contract import (
    shared_enabler_valuation,
    validate_shared_enabler_consistency,
)
from ior_mvp.route_hypotheses import BROWNFIELD_ROUTE_CODE
from ior_mvp.rules import evaluate_rules

from .model import (
    GraphEdge,
    GraphNode,
    assert_endpoint,
    capability_id,
    relationship_key,
    slug,
)


class GraphProjectionError(ValueError):
    """Raised when governed graph inputs conflict or cannot be projected."""


@dataclass
class GraphProjection:
    """Canonical graph projection before serialization or loading."""

    projection_id: str
    as_of: str
    inputs: list[dict[str, Any]]
    engine: dict[str, Any]
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    counts: dict[str, Any] = field(default_factory=dict)

    def refresh_counts(self) -> None:
        """Recompute exact aggregate and per-vocabulary counts."""
        by_label: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for node in self.nodes:
            by_label[node.label] = by_label.get(node.label, 0) + 1
        for edge in self.edges:
            by_type[edge.type] = by_type.get(edge.type, 0) + 1
        self.counts = {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "nodes_by_label": dict(sorted(by_label.items())),
            "edges_by_type": dict(sorted(by_type.items())),
        }


def _list_union(left: Any, right: Any) -> list[Any]:
    values: list[Any] = []
    for candidate in (left, right):
        if isinstance(candidate, list):
            values.extend(candidate)
        elif candidate is not None:
            values.append(candidate)
    unique = {json.dumps(value, ensure_ascii=False, sort_keys=True): value for value in values}
    return [unique[key] for key in sorted(unique)]


class ProjectionAssembler:
    """Add graph elements with deterministic conflict handling."""

    _MERGED_LIST_KEYS = {
        "document_addresses",
        "evidence_ids",
        "origin_refs",
        "scenario_ids",
        "supports",
    }

    def __init__(self, projection: GraphProjection) -> None:
        self.projection = projection
        self.nodes: dict[str, GraphNode] = {
            node.id: node for node in projection.nodes
        }
        self.edges: dict[str, GraphEdge] = {
            edge.key: edge for edge in projection.edges
        }

    def add_node(self, node: GraphNode) -> GraphNode:
        existing = self.nodes.get(node.id)
        if existing is None:
            self.nodes[node.id] = node
            self.projection.nodes.append(node)
            return node
        if existing.label != node.label:
            raise GraphProjectionError(
                f"Node id collision across labels: {node.id}"
            )
        self._merge_properties(existing.properties, node.properties, node.id)
        return existing

    def _merge_properties(
        self,
        existing: dict[str, Any],
        incoming: Mapping[str, Any],
        identity: str,
    ) -> None:
        for key, value in incoming.items():
            if key not in existing:
                existing[key] = deepcopy(value)
                continue
            current = existing[key]
            if current == value:
                continue
            if key in self._MERGED_LIST_KEYS:
                existing[key] = _list_union(current, value)
                continue
            if key == "evidence_id":
                existing[key] = min(str(current), str(value))
                existing["evidence_ids"] = _list_union(
                    existing.get("evidence_ids"),
                    [current, value],
                )
                continue
            if key == "as_of":
                existing[key] = max(str(current), str(value))
                continue
            if key == "origin_ref":
                existing["origin_refs"] = _list_union(
                    existing.get("origin_refs"),
                    [current, value],
                )
                existing[key] = min(str(current), str(value))
                continue
            if current is None or current == "UNAVAILABLE":
                existing[key] = deepcopy(value)
                continue
            if value is None or value == "UNAVAILABLE":
                continue
            raise GraphProjectionError(
                f"Conflicting graph properties for {identity}: {key}"
            )

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        source = self.nodes.get(edge.source)
        target = self.nodes.get(edge.target)
        if source is None or target is None:
            raise GraphProjectionError(
                f"Relationship endpoint is missing: {edge.key}"
            )
        assert_endpoint(source.label, edge.type, target.label)
        existing = self.edges.get(edge.key)
        if existing is None:
            self.edges[edge.key] = edge
            self.projection.edges.append(edge)
            return edge
        if (
            existing.type,
            existing.source,
            existing.target,
        ) != (edge.type, edge.source, edge.target):
            raise GraphProjectionError(
                f"Relationship key collision: {edge.key}"
            )
        self._merge_properties(existing.properties, edge.properties, edge.key)
        return existing


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GraphProjectionError(f"Graph input cannot be read: {path}") from exc
    if not isinstance(value, dict):
        raise GraphProjectionError(f"Graph input must be an object: {path}")
    return value


def _version(record: Mapping[str, Any]) -> str:
    metadata = record.get("metadata")
    if isinstance(metadata, Mapping) and isinstance(metadata.get("version"), str):
        return str(metadata["version"])
    for key in ("schema_version", "scenario_version", "version"):
        if isinstance(record.get(key), str):
            return str(record[key])
    return "UNAVAILABLE"


def _input_row(path: Path, root: Path, kind: str) -> dict[str, Any]:
    version = "UNAVAILABLE"
    if path.suffix.lower() == ".json" and path.stat().st_size < 2_000_000:
        try:
            version = _version(_json(path))
        except GraphProjectionError:
            version = "UNAVAILABLE"
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "kind": kind,
        "version": version,
    }


def discover_inputs(root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    """Return every governed file that can influence this projection."""
    groups: tuple[tuple[str, Iterable[Path]], ...] = (
        (
            "PUBLIC_SNAPSHOT",
            (root / "data/snapshots/public").glob("*.json"),
        ),
        ("SCENARIO", (root / "data/synthetic").glob("*.json")),
        (
            "ENTITY_ARTIFACT",
            (root / "data/entities/resolution").glob("*.json"),
        ),
        ("CASE_BRIEF", (root / "data/cases/briefs").glob("*.json")),
        (
            "SCREENING_SNAPSHOT",
            (
                path
                for path in (root / "data/screening/snapshots").rglob("*")
                if path.is_file()
            ),
        ),
        (
            "TARIFF_SNAPSHOT",
            (root / "data/snapshots/tariff").glob("*.json"),
        ),
        (
            "TARIFF_ATTEMPT",
            (
                path
                for path in (root / "data/raw/zatca_tariff").rglob("*.json")
                if path.name in {"attempt.json", "coverage.json"}
            ),
        ),
        (
            "CASE_DEPENDENCY",
            (
                path
                for directory in (
                    root / "data/snapshots/universe",
                    root / "data/snapshots/partners",
                    root / "data/documents",
                )
                for path in directory.rglob("*.json")
                if (
                    "data/documents" not in path.as_posix()
                    or "/records/" in path.as_posix()
                )
            ),
        ),
        (
            "CONFIG",
            (
                root / "config/thresholds.v1.yaml",
                root / "config/sector_profiles.v1.yaml",
                root / "config/evidence_policy.v1.yaml",
                root / "config/graph_views.v1.yaml",
            ),
        ),
        (
            "AUTHORITY_FILE",
            (
                root
                / "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx",
                *(root / "docs/core").glob("*.md"),
                *(root / "config").glob("*.v1.yaml"),
            ),
        ),
        (
            "ENGINE_IMPLEMENTATION",
            (
                path
                for directory in (
                    root / "src/ior_mvp",
                    root / "src/ior_mvp/cases",
                    root / "src/ior_mvp/graph",
                )
                for path in directory.glob("*.py")
            ),
        ),
    )
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for kind, paths in groups:
        for path in sorted(paths):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in seen:
                continue
            seen.add(relative)
            rows.append(_input_row(path, root, kind))
    return sorted(rows, key=lambda row: row["path"])


def _base_properties(
    *,
    identity: str,
    evidence_id: str,
    as_of: str,
    evidence_class: str,
    synthetic_flag: bool,
    scenario_id: str,
    origin_kind: str,
    origin_ref: str,
    projection_id: str,
    derived: bool = False,
    engine_run_id: str | None = None,
    evidence_ids: Iterable[str] = (),
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "id": identity,
        "evidence_id": evidence_id,
        "as_of": as_of,
        "evidence_class": evidence_class,
        "synthetic_flag": synthetic_flag,
        "scenario_id": scenario_id,
        "origin_kind": origin_kind,
        "origin_ref": origin_ref,
        "derived": derived,
        "projection_id": projection_id,
        "evidence_ids": sorted(set(evidence_ids) | {evidence_id}),
    }
    if derived:
        properties["engine_run_id"] = engine_run_id
    if synthetic_flag:
        labels = synthetic_display_labels()
        properties["display_label"] = labels["en"]
        properties["display_label_ar"] = labels["ar"]
    return properties


def _edge(
    assembler: ProjectionAssembler,
    edge_type: str,
    source: str,
    target: str,
    properties: Mapping[str, Any],
    *,
    discriminator: str = "",
) -> GraphEdge:
    key = relationship_key(edge_type, source, target, discriminator)
    values = {"key": key, **deepcopy(dict(properties))}
    return assembler.add_edge(
        GraphEdge(
            type=edge_type,
            source=source,
            target=target,
            key=key,
            properties=values,
        )
    )


def _public_origin(case: Mapping[str, Any]) -> tuple[str, str]:
    kind = str(case.get("_graph_origin_kind", "PUBLIC_SNAPSHOT"))
    reference = str(
        case.get("_graph_origin_ref")
        or case.get("snapshot_id")
        or case.get("opportunity", {}).get("id")
    )
    return kind, reference


def _case_evidence_class(case: Mapping[str, Any]) -> str:
    classes = [
        str(row["evidence_class"])
        for row in case.get("evidence", [])
        if isinstance(row, Mapping)
        and row.get("evidence_class") in {"A", "B", "C", "D", "E"}
    ]
    return min(classes, default="E")


def _case_evidence_id(case: Mapping[str, Any]) -> str:
    ids = sorted(
        str(row["evidence_id"])
        for row in case.get("evidence", [])
        if isinstance(row, Mapping) and isinstance(row.get("evidence_id"), str)
    )
    if ids:
        return ids[0]
    return f"{case.get('snapshot_id', 'PUBLIC')}::record"


def _entity_union(
    entity_artifacts: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Mapping[str, Any]]]:
    entities: dict[str, dict[str, Any]] = {}
    origins: dict[str, Mapping[str, Any]] = {}
    for artifact in entity_artifacts:
        for row in artifact.get("entities", []):
            if not isinstance(row, Mapping) or not isinstance(
                row.get("entity_id"), str
            ):
                continue
            identity = str(row["entity_id"])
            value = deepcopy(dict(row))
            if identity in entities and entities[identity] != value:
                raise GraphProjectionError(
                    f"Conflicting entity record for {identity}"
                )
            entities[identity] = value
            origins[identity] = artifact
    return entities, origins


def _entity_label(entity_type: str) -> str:
    return {
        "COMPANY": "Company",
        "PLANT": "Plant",
        "LINE": "ProductionLine",
    }.get(entity_type, "Company")


def _entity_names(entity: Mapping[str, Any]) -> set[str]:
    values = {
        str(entity.get("primary_name_en", "")),
        str(entity.get("primary_name_ar", "")),
    }
    values.update(
        str(row.get("name_text", ""))
        for row in entity.get("names", [])
        if isinstance(row, Mapping)
    )
    return {slug(value) for value in values if value and value != "UNAVAILABLE"}


def _project_entities(
    assembler: ProjectionAssembler,
    artifacts: list[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    entities, origins = _entity_union(artifacts)
    by_name: dict[str, list[str]] = {}
    for identity, entity in sorted(entities.items()):
        artifact = origins[identity]
        mentions = sorted(str(value) for value in entity.get("evidence_mention_ids", []))
        evidence_id = mentions[0] if mentions else f"{artifact['artifact_id']}::{identity}"
        as_of = str(artifact.get("as_of_date", "UNAVAILABLE"))
        props = _base_properties(
            identity=identity,
            evidence_id=evidence_id,
            as_of=as_of,
            evidence_class="C",
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind="ENTITY_ARTIFACT",
            origin_ref=str(artifact.get("artifact_id", "UNAVAILABLE")),
            projection_id=assembler.projection.projection_id,
            evidence_ids=mentions,
        )
        props.update(
            {
                "identity_basis": "ENTITY_ID_V1",
                "entity_type": entity.get("entity_type"),
                "primary_name_en": entity.get("primary_name_en"),
                "primary_name_ar": entity.get("primary_name_ar"),
                "granularity": entity.get("granularity"),
            }
        )
        assembler.add_node(
            GraphNode(
                label=_entity_label(str(entity.get("entity_type"))),
                id=identity,
                properties=props,
            )
        )
        for name in _entity_names(entity):
            by_name.setdefault(name, []).append(identity)
    return entities, by_name


def _project_evidence_node(
    assembler: ProjectionAssembler,
    row: Mapping[str, Any],
    *,
    as_of: str,
    origin_kind: str,
    origin_ref: str,
    scenario_id: str = "PUBLIC",
    document_addresses: Iterable[Mapping[str, Any]] = (),
) -> GraphNode:
    identity = str(row["evidence_id"])
    synthetic = row.get("synthetic_flag") is True
    props = _base_properties(
        identity=identity,
        evidence_id=identity,
        as_of=as_of,
        evidence_class=str(row.get("evidence_class", "E")),
        synthetic_flag=synthetic,
        scenario_id=scenario_id if synthetic else "PUBLIC",
        origin_kind=origin_kind,
        origin_ref=origin_ref,
        projection_id=assembler.projection.projection_id,
    )
    props.update(
        {
            key: deepcopy(row.get(key))
            for key in (
                "title",
                "source",
                "url",
                "period",
                "retrieved_at",
                "status",
                "supports",
                "reviewer_status",
            )
            if key in row
        }
    )
    addresses = [dict(value) for value in document_addresses]
    if addresses:
        props["document_addresses"] = addresses
    return assembler.add_node(
        GraphNode(label="Evidence", id=identity, properties=props)
    )


def _project_public_case(
    assembler: ProjectionAssembler,
    case: Mapping[str, Any],
    *,
    entity_names: Mapping[str, list[str]],
) -> None:
    opportunity = case["opportunity"]
    product_id = str(opportunity["id"])
    snapshot_id = str(case["snapshot_id"])
    as_of = str(case["as_of_date"])
    evidence_id = _case_evidence_id(case)
    evidence_ids = [
        str(row["evidence_id"])
        for row in case.get("evidence", [])
        if isinstance(row, Mapping) and isinstance(row.get("evidence_id"), str)
    ]
    origin_kind, origin_ref = _public_origin(case)
    common = _base_properties(
        identity=product_id,
        evidence_id=evidence_id,
        as_of=as_of,
        evidence_class=_case_evidence_class(case),
        synthetic_flag=False,
        scenario_id="PUBLIC",
        origin_kind=origin_kind,
        origin_ref=origin_ref,
        projection_id=assembler.projection.projection_id,
        evidence_ids=evidence_ids,
    )
    common.update(
        {
            "snapshot_id": snapshot_id,
            "schema_version": case.get("schema_version"),
            "hs6": opportunity.get("hs6"),
            "hs_revision": opportunity.get("hs_revision"),
            "sector_profile": opportunity.get("sector_profile"),
            "name_en": opportunity.get("commercial_name_en"),
            "name_ar": opportunity.get("commercial_name_ar"),
            "decision_object_status": opportunity.get("decision_object_status"),
            "national_tariff_line": opportunity.get(
                "national_tariff_line", "UNAVAILABLE"
            ),
        }
    )
    assembler.add_node(GraphNode("Product", product_id, common))

    for row in case.get("evidence", []):
        if not isinstance(row, Mapping) or not isinstance(
            row.get("evidence_id"), str
        ):
            continue
        evidence = _project_evidence_node(
            assembler,
            row,
            as_of=as_of,
            origin_kind=origin_kind,
            origin_ref=origin_ref,
        )
        edge_props = _base_properties(
            identity="PENDING",
            evidence_id=evidence.id,
            as_of=as_of,
            evidence_class=str(row.get("evidence_class", "E")),
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=[evidence.id],
        )
        edge_props.pop("id")
        edge_props["supports"] = sorted(str(value) for value in row.get("supports", []))
        _edge(
            assembler,
            "SUPPORTED_BY_EVIDENCE",
            product_id,
            evidence.id,
            edge_props,
        )

    application_id = f"APP-{product_id}"
    application_props = _base_properties(
        identity=application_id,
        evidence_id=evidence_id,
        as_of=as_of,
        evidence_class=_case_evidence_class(case),
        synthetic_flag=False,
        scenario_id="PUBLIC",
        origin_kind=origin_kind,
        origin_ref=origin_ref,
        projection_id=assembler.projection.projection_id,
        evidence_ids=evidence_ids,
    )
    application_props["boundary_text"] = opportunity.get("application_boundary")
    assembler.add_node(GraphNode("Application", application_id, application_props))

    specification_id = f"SPEC-{product_id}-TARGET"
    target = case.get("decision_inputs", {}).get("target_specification_demand")
    spec_evidence = f"{snapshot_id}::decision_inputs.target_specification_demand"
    specification_props = _base_properties(
        identity=specification_id,
        evidence_id=spec_evidence,
        as_of=as_of,
        evidence_class="E" if target == "UNAVAILABLE" else _case_evidence_class(case),
        synthetic_flag=False,
        scenario_id="PUBLIC",
        origin_kind=origin_kind,
        origin_ref=origin_ref,
        projection_id=assembler.projection.projection_id,
    )
    specification_props.update(
        {
            "opportunity_id": product_id,
            "status": "UNAVAILABLE" if target == "UNAVAILABLE" else "OBSERVED",
            "target_specification_demand": deepcopy(target),
        }
    )
    assembler.add_node(
        GraphNode("Specification", specification_id, specification_props)
    )
    marker_row = {
        "evidence_id": spec_evidence,
        "title": "Target specification demand state",
        "source": snapshot_id,
        "status": "unresolved" if target == "UNAVAILABLE" else "observed",
        "evidence_class": specification_props["evidence_class"],
        "synthetic_flag": False,
        "supports": ["TARGET_SPECIFICATION_DEMAND"],
    }
    _project_evidence_node(
        assembler,
        marker_row,
        as_of=as_of,
        origin_kind=origin_kind,
        origin_ref=origin_ref,
    )
    for edge_type, source, target_id in (
        ("USED_IN", product_id, application_id),
        ("REQUIRES_SPECIFICATION", product_id, specification_id),
        ("REQUIRES_SPECIFICATION", application_id, specification_id),
    ):
        edge_props = _base_properties(
            identity="PENDING",
            evidence_id=evidence_id,
            as_of=as_of,
            evidence_class=_case_evidence_class(case),
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=evidence_ids,
        )
        edge_props.pop("id")
        _edge(assembler, edge_type, source, target_id, edge_props)

    capability = case.get("domestic_capability", {})
    producer_nodes: list[str] = []
    for index, producer in enumerate(capability.get("producer_evidence", [])):
        if not isinstance(producer, Mapping):
            continue
        name = str(producer.get("producer", "UNAVAILABLE"))
        matches = sorted(set(entity_names.get(slug(name), [])))
        if len(matches) > 1:
            raise GraphProjectionError(
                f"Producer entity mapping is ambiguous: {name}"
            )
        producer_evidence = sorted(
            str(value) for value in producer.get("evidence_ids", [])
        )
        producer_class = str(producer.get("evidence_class", "C"))
        if matches:
            company_id = matches[0]
        else:
            company_id = f"PRODUCER-{slug(snapshot_id)}-{index + 1}"
            company_props = _base_properties(
                identity=company_id,
                evidence_id=producer_evidence[0] if producer_evidence else evidence_id,
                as_of=as_of,
                evidence_class=producer_class,
                synthetic_flag=False,
                scenario_id="PUBLIC",
                origin_kind=origin_kind,
                origin_ref=origin_ref,
                projection_id=assembler.projection.projection_id,
                evidence_ids=producer_evidence,
            )
            company_props.update(
                {
                    "identity_basis": "SNAPSHOT_PRODUCER_LABEL",
                    "primary_name_en": name,
                    "primary_name_ar": "UNAVAILABLE",
                }
            )
            assembler.add_node(GraphNode("Company", company_id, company_props))
        producer_nodes.append(company_id)
        relation_evidence = producer_evidence[0] if producer_evidence else evidence_id
        relation_props = _base_properties(
            identity="PENDING",
            evidence_id=relation_evidence,
            as_of=as_of,
            evidence_class=producer_class,
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=producer_evidence,
        )
        relation_props.pop("id")
        _edge(
            assembler,
            "PRODUCED_BY",
            product_id,
            company_id,
            relation_props,
            discriminator=str(index),
        )
        process_route = producer.get("process_route")
        if isinstance(process_route, str) and process_route != "UNAVAILABLE":
            process_id = f"PROC-{slug(process_route)}"
            process_props = _base_properties(
                identity=process_id,
                evidence_id=relation_evidence,
                as_of=as_of,
                evidence_class=producer_class,
                synthetic_flag=False,
                scenario_id="PUBLIC",
                origin_kind=origin_kind,
                origin_ref=origin_ref,
                projection_id=assembler.projection.projection_id,
                evidence_ids=producer_evidence,
            )
            process_props["description"] = process_route
            assembler.add_node(GraphNode("Process", process_id, process_props))
            _edge(
                assembler,
                "USES_PROCESS",
                company_id,
                process_id,
                relation_props,
            )
        published_standards = producer.get("published_standards")
        if isinstance(published_standards, list):
            for standard in sorted(
                str(value)
                for value in published_standards
                if isinstance(value, str) and value
            ):
                standard_id = f"STD-{slug(standard)}"
                standard_props = _base_properties(
                    identity=standard_id,
                    evidence_id=relation_evidence,
                    as_of=as_of,
                    evidence_class=producer_class,
                    synthetic_flag=False,
                    scenario_id="PUBLIC",
                    origin_kind=origin_kind,
                    origin_ref=origin_ref,
                    projection_id=assembler.projection.projection_id,
                    evidence_ids=producer_evidence,
                )
                standard_props["standard"] = standard
                assembler.add_node(
                    GraphNode("Standard", standard_id, standard_props)
                )
                for supporting_id in producer_evidence:
                    if supporting_id not in assembler.nodes:
                        continue
                    support_props = deepcopy(standard_props)
                    support_props.pop("id")
                    support_props["evidence_id"] = supporting_id
                    support_props["supports"] = ["PUBLISHED_STANDARD"]
                    _edge(
                        assembler,
                        "SUPPORTED_BY_EVIDENCE",
                        standard_id,
                        supporting_id,
                        support_props,
                        discriminator=supporting_id,
                    )

    dimensions = capability.get("public_dimension_states", {})
    for dimension, value in sorted(dimensions.items()):
        state = value.get("state") if isinstance(value, Mapping) else value
        ids = (
            [str(item) for item in value.get("evidence_ids", value.get("span_ids", []))]
            if isinstance(value, Mapping)
            else []
        )
        known = state != "U"
        cap_id = capability_id(product_id, str(dimension))
        cap_props = _base_properties(
            identity=cap_id,
            evidence_id=ids[0] if ids else f"{snapshot_id}::capability.{dimension}",
            as_of=as_of,
            evidence_class="C" if known else "E",
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=ids,
        )
        cap_props.update(
            {
                "opportunity_id": product_id,
                "capability_kind": "dimension",
                "dimension": dimension,
                "state": state,
                "status": "RESOLVED" if known else "UNAVAILABLE",
            }
        )
        assembler.add_node(GraphNode("Capability", cap_id, cap_props))
        edge_props = deepcopy(cap_props)
        edge_props.pop("id")
        _edge(
            assembler,
            "HAS_CAPABILITY",
            product_id,
            cap_id,
            edge_props,
            discriminator="public",
        )

    for gate, row in sorted(capability.get("profile_hard_gates", {}).items()):
        status = classify_gate_status(
            row.get("status") if isinstance(row, Mapping) else row
        ).value
        ids = (
            [str(value) for value in row.get("evidence_ids", row.get("span_ids", []))]
            if isinstance(row, Mapping)
            else []
        )
        cap_id = capability_id(product_id, f"GATE-{gate}")
        cap_props = _base_properties(
            identity=cap_id,
            evidence_id=ids[0] if ids else f"{snapshot_id}::gate.{gate}",
            as_of=as_of,
            evidence_class="C" if status != "UNAVAILABLE" else "E",
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=ids,
        )
        cap_props.update(
            {
                "opportunity_id": product_id,
                "capability_kind": "gate",
                "gate": gate,
                "status": status,
            }
        )
        assembler.add_node(GraphNode("Capability", cap_id, cap_props))
        edge_props = deepcopy(cap_props)
        edge_props.pop("id")
        _edge(
            assembler,
            "HAS_CAPABILITY",
            product_id,
            cap_id,
            edge_props,
            discriminator="public",
        )

    for signal_index, signal in enumerate(
        capability.get("coarse_adjacency_signals", [])
    ):
        if not isinstance(signal, Mapping):
            continue
        signal_ids = sorted(str(value) for value in signal.get("evidence_ids", []))
        if not signal_ids:
            continue
        signal_type = signal.get("signal_type")
        description = str(signal.get("description", signal_type))
        signal_evidence = signal_ids[0]
        if signal_type == "relevant_certification":
            target_id = f"CERT-{slug(description)}"
            target_label = "Certification"
            edge_type = "CERTIFIED_TO"
        elif signal_type in {"core_process", "matching_feedstock"}:
            target_id = f"PROC-{slug(description)}"
            target_label = "Process"
            edge_type = "USES_PROCESS"
        else:
            continue
        target_props = _base_properties(
            identity=target_id,
            evidence_id=signal_evidence,
            as_of=as_of,
            evidence_class="C",
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind=origin_kind,
            origin_ref=origin_ref,
            projection_id=assembler.projection.projection_id,
            evidence_ids=signal_ids,
        )
        target_props.update(
            {
                "description": description,
                "signal_type": signal_type,
            }
        )
        assembler.add_node(GraphNode(target_label, target_id, target_props))
        for producer_id in sorted(set(producer_nodes)):
            edge_props = deepcopy(target_props)
            edge_props.pop("id")
            _edge(
                assembler,
                edge_type,
                producer_id,
                target_id,
                edge_props,
                discriminator=str(signal_index),
            )


def _scenario_delta_nv(
    scenario: Mapping[str, Any],
) -> tuple[int, float, str]:
    try:
        route_code, raw = shared_enabler_valuation(dict(scenario))
    except (EvidenceIntegrityError, ValueError) as exc:
        raise GraphProjectionError(str(exc)) from exc
    reference = (
        "synthetic_inputs.economics.national_value"
        if route_code == BROWNFIELD_ROUTE_CODE
        else (
            "synthetic_inputs.route_evidence"
            f"[route_code={route_code}].national_value"
        )
    )
    return route_code, raw, reference


def _project_scenario(
    assembler: ProjectionAssembler,
    scenario: Mapping[str, Any],
) -> None:
    scenario_id = str(scenario["scenario_id"])
    product_id = str(scenario["opportunity_id"])
    product = assembler.nodes.get(product_id)
    if product is None:
        raise GraphProjectionError(
            f"Scenario has no projected public Product: {scenario_id}"
        )
    as_of = str(product.properties["as_of"])
    rows = synthetic_evidence_rows(dict(scenario))
    evidence_ids = [row["evidence_id"] for row in rows]
    scenario_evidence = evidence_ids[0] if evidence_ids else scenario_id
    props = _base_properties(
        identity=scenario_id,
        evidence_id=scenario_evidence,
        as_of=as_of,
        evidence_class="D",
        synthetic_flag=True,
        scenario_id=scenario_id,
        origin_kind="SCENARIO",
        origin_ref=scenario_id,
        projection_id=assembler.projection.projection_id,
        evidence_ids=evidence_ids,
    )
    props.update(
        {
            "opportunity_id": product_id,
            "scenario_version": scenario.get("scenario_version"),
            "seed_basis": scenario.get("seed_basis"),
            "ground_truth_state": scenario.get("ground_truth", {}).get(
                "expected_simulation_state"
            ),
            "ground_truth_route": scenario.get("ground_truth", {}).get(
                "expected_route_code"
            ),
        }
    )
    decision_gates = scenario.get("synthetic_inputs", {}).get(
        "decision_specific_hard_gates"
    )
    if isinstance(decision_gates, Mapping) and decision_gates:
        props["decision_specific_hard_gates"] = {
            gate: {
                "status": classify_gate_status(declaration).value,
                "declaration": declaration,
                "evidence_id": f"{scenario_id}::decision_specific_hard_gates",
            }
            for gate, declaration in sorted(decision_gates.items())
        }
    assembler.add_node(GraphNode("Scenario", scenario_id, props))
    for row in rows:
        evidence = _project_evidence_node(
            assembler,
            row,
            as_of=as_of,
            origin_kind="SCENARIO",
            origin_ref=scenario_id,
            scenario_id=scenario_id,
        )
        edge_props = _base_properties(
            identity="PENDING",
            evidence_id=evidence.id,
            as_of=as_of,
            evidence_class="D",
            synthetic_flag=True,
            scenario_id=scenario_id,
            origin_kind="SCENARIO",
            origin_ref=scenario_id,
            projection_id=assembler.projection.projection_id,
        )
        edge_props.pop("id")
        edge_props["supports"] = deepcopy(row.get("supports", []))
        _edge(
            assembler,
            "SUPPORTED_BY_EVIDENCE",
            scenario_id,
            evidence.id,
            edge_props,
        )

    inputs = scenario.get("synthetic_inputs", {})
    target = inputs.get("target_specification", {})
    spec_id = f"SPEC-{scenario_id}-TARGET"
    spec_evidence = f"{scenario_id}::target_specification"
    spec_props = _base_properties(
        identity=spec_id,
        evidence_id=spec_evidence,
        as_of=as_of,
        evidence_class="D",
        synthetic_flag=True,
        scenario_id=scenario_id,
        origin_kind="SCENARIO",
        origin_ref=scenario_id,
        projection_id=assembler.projection.projection_id,
    )
    spec_props.update(
        {
            "opportunity_id": product_id,
            "status": "SYNTHETIC_DESIGN",
            "name": target.get("name") if isinstance(target, Mapping) else None,
            "standard": (
                target.get("standard") if isinstance(target, Mapping) else None
            ),
        }
    )
    assembler.add_node(GraphNode("Specification", spec_id, spec_props))
    standard = target.get("standard") if isinstance(target, Mapping) else None
    if isinstance(standard, str) and standard:
        standard_id = f"STD-{scenario_id}-{slug(standard)}"
        standard_props = _base_properties(
            identity=standard_id,
            evidence_id=spec_evidence,
            as_of=as_of,
            evidence_class="D",
            synthetic_flag=True,
            scenario_id=scenario_id,
            origin_kind="SCENARIO",
            origin_ref=scenario_id,
            projection_id=assembler.projection.projection_id,
        )
        standard_props["standard"] = standard
        assembler.add_node(
            GraphNode("Standard", standard_id, standard_props)
        )
        standard_edge_props = deepcopy(standard_props)
        standard_edge_props.pop("id")
        standard_edge_props["reason_code"] = (
            "SYNTHETIC_TARGET_STANDARD"
        )
        _edge(
            assembler,
            "CONSTRAINED_BY",
            spec_id,
            standard_id,
            standard_edge_props,
        )
        if spec_evidence in assembler.nodes:
            support_props = deepcopy(standard_props)
            support_props.pop("id")
            support_props["supports"] = [
                "SYNTHETIC_TARGET_SPECIFICATION"
            ]
            _edge(
                assembler,
                "SUPPORTED_BY_EVIDENCE",
                standard_id,
                spec_evidence,
                support_props,
            )
    application_id = f"APP-{scenario_id}"
    app_props = deepcopy(spec_props)
    app_props["id"] = application_id
    app_props["application"] = (
        target.get("application") if isinstance(target, Mapping) else None
    )
    assembler.add_node(GraphNode("Application", application_id, app_props))
    edge_props = deepcopy(spec_props)
    edge_props.pop("id")
    _edge(
        assembler,
        "REQUIRES_SPECIFICATION",
        product_id,
        spec_id,
        edge_props,
        discriminator=scenario_id,
    )
    _edge(
        assembler,
        "REQUIRES_SPECIFICATION",
        application_id,
        spec_id,
        edge_props,
    )
    _edge(
        assembler,
        "USED_IN",
        product_id,
        application_id,
        edge_props,
        discriminator=scenario_id,
    )
    segment_id = f"SEG-{scenario_id}-target-demand"
    segment_props = _base_properties(
        identity=segment_id,
        evidence_id=f"{scenario_id}::demand",
        as_of=as_of,
        evidence_class="D",
        synthetic_flag=True,
        scenario_id=scenario_id,
        origin_kind="SCENARIO",
        origin_ref=scenario_id,
        projection_id=assembler.projection.projection_id,
    )
    demand = inputs.get("demand", {})
    segment_props["segment_kind"] = "target_demand"
    if isinstance(demand, Mapping):
        segment_props.update(deepcopy(dict(demand)))
    assembler.add_node(
        GraphNode("CustomerSegment", segment_id, segment_props)
    )
    segment_edge_props = deepcopy(segment_props)
    segment_edge_props.pop("id")
    _edge(
        assembler,
        "QUALIFIED_FOR",
        segment_id,
        application_id,
        segment_edge_props,
    )

    plant_id = f"PLANT-{scenario_id}"
    line_id = f"LINE-{scenario_id}"
    line_values = inputs.get("plant_line", {})
    plant_props = _base_properties(
        identity=plant_id,
        evidence_id=f"{scenario_id}::plant_line",
        as_of=as_of,
        evidence_class="D",
        synthetic_flag=True,
        scenario_id=scenario_id,
        origin_kind="SCENARIO",
        origin_ref=scenario_id,
        projection_id=assembler.projection.projection_id,
    )
    plant_props["identity_basis"] = "SYNTHETIC_PLANT_LINE"
    assembler.add_node(GraphNode("Plant", plant_id, plant_props))
    line_props = deepcopy(plant_props)
    line_props["id"] = line_id
    if isinstance(line_values, Mapping):
        line_props.update(deepcopy(dict(line_values)))
    assembler.add_node(GraphNode("ProductionLine", line_id, line_props))
    edge_props = deepcopy(plant_props)
    edge_props.pop("id")
    _edge(
        assembler,
        "PRODUCED_BY",
        product_id,
        plant_id,
        edge_props,
        discriminator=scenario_id,
    )
    _edge(assembler, "HAS_LINE", plant_id, line_id, edge_props)

    for dimension, state in sorted(inputs.get("capability_states", {}).items()):
        cap_id = capability_id(scenario_id, str(dimension))
        cap_props = _base_properties(
            identity=cap_id,
            evidence_id=f"{scenario_id}::capability_states",
            as_of=as_of,
            evidence_class="D",
            synthetic_flag=True,
            scenario_id=scenario_id,
            origin_kind="SCENARIO",
            origin_ref=scenario_id,
            projection_id=assembler.projection.projection_id,
        )
        cap_props.update(
            {
                "opportunity_id": product_id,
                "capability_kind": "dimension",
                "dimension": dimension,
                "state": state,
                "status": "RESOLVED" if state != "U" else "UNAVAILABLE",
            }
        )
        assembler.add_node(GraphNode("Capability", cap_id, cap_props))
        edge_props = deepcopy(cap_props)
        edge_props.pop("id")
        _edge(
            assembler,
            "HAS_CAPABILITY",
            product_id,
            cap_id,
            edge_props,
            discriminator=scenario_id,
        )
    for gate, status in sorted(inputs.get("hard_gates", {}).items()):
        typed_status = classify_gate_status(status).value
        evidence_ids = [f"{scenario_id}::hard_gates"]
        cap_id = capability_id(scenario_id, f"GATE-{gate}")
        cap_props = _base_properties(
            identity=cap_id,
            evidence_id=evidence_ids[0],
            as_of=as_of,
            evidence_class="D",
            synthetic_flag=True,
            scenario_id=scenario_id,
            origin_kind="SCENARIO",
            origin_ref=scenario_id,
            projection_id=assembler.projection.projection_id,
            evidence_ids=evidence_ids,
        )
        cap_props.update(
            {
                "opportunity_id": product_id,
                "capability_kind": "gate",
                "gate": gate,
                "status": typed_status,
                "declaration": deepcopy(status),
            }
        )
        assembler.add_node(GraphNode("Capability", cap_id, cap_props))
        edge_props = deepcopy(cap_props)
        edge_props.pop("id")
        _edge(
            assembler,
            "HAS_CAPABILITY",
            product_id,
            cap_id,
            edge_props,
            discriminator=scenario_id,
        )


def _project_enablers(
    assembler: ProjectionAssembler,
    scenarios: Iterable[Mapping[str, Any]],
) -> None:
    declarations: dict[str, dict[str, Any]] = {}
    scenario_ids: dict[str, list[str]] = {}
    common_keys = ("enabler_kind", "label", "enabler_cost_m_sar", "components")
    for scenario in scenarios:
        block = scenario.get("synthetic_inputs", {}).get("shared_enabler")
        if not isinstance(block, Mapping):
            continue
        enabler_id = str(block["enabler_id"])
        common = {key: deepcopy(block.get(key)) for key in common_keys}
        if enabler_id in declarations and declarations[enabler_id] != common:
            raise GraphProjectionError(
                f"ENABLER_DECLARATION_CONFLICT: {enabler_id}"
            )
        declarations[enabler_id] = common
        scenario_ids.setdefault(enabler_id, []).append(str(scenario["scenario_id"]))

    by_scenario = {
        str(scenario["scenario_id"]): scenario for scenario in scenarios
    }
    for enabler_id, common in sorted(declarations.items()):
        ids = sorted(scenario_ids[enabler_id])
        first_scenario = by_scenario[ids[0]]
        product = assembler.nodes[str(first_scenario["opportunity_id"])]
        as_of = str(product.properties["as_of"])
        evidence_ids = [f"{scenario_id}::shared_enabler" for scenario_id in ids]
        props = _base_properties(
            identity=enabler_id,
            evidence_id=evidence_ids[0],
            as_of=as_of,
            evidence_class="D",
            synthetic_flag=True,
            scenario_id=ids[0],
            origin_kind="SCENARIO",
            origin_ref=ids[0],
            projection_id=assembler.projection.projection_id,
            evidence_ids=evidence_ids,
        )
        props.update(common)
        label = common.get("label")
        if isinstance(label, Mapping):
            props["label_en"] = label.get("en")
            props["label_ar"] = label.get("ar")
        props["kind"] = "shared_enabler"
        props["scenario_ids"] = ids
        assembler.add_node(GraphNode("Intervention", enabler_id, props))
        for scenario_id in ids:
            scenario = by_scenario[scenario_id]
            block = scenario["synthetic_inputs"]["shared_enabler"]
            product_id = str(scenario["opportunity_id"])
            valuation_route_code, delta_nv, valuation_reference = (
                _scenario_delta_nv(scenario)
            )
            edge_props = _base_properties(
                identity="PENDING",
                evidence_id=f"{scenario_id}::shared_enabler",
                as_of=str(assembler.nodes[product_id].properties["as_of"]),
                evidence_class="D",
                synthetic_flag=True,
                scenario_id=scenario_id,
                origin_kind="SCENARIO",
                origin_ref=f"{scenario_id}::shared_enabler",
                projection_id=assembler.projection.projection_id,
                evidence_ids=[f"{scenario_id}::shared_enabler"],
            )
            edge_props.pop("id")
            edge_props.update(
                {
                    "unlock_probability": block["unlock_probability"],
                    "dependency_share": block["dependency_share"],
                    "dependent_incremental_national_value_m_sar": delta_nv,
                    "valuation_route_code": valuation_route_code,
                    "valuation_input_reference": valuation_reference,
                    "constraint_classes_addressed": deepcopy(
                        block["constraint_classes_addressed"]
                    ),
                    "removes_binding_constraint": block[
                        "removes_binding_constraint"
                    ],
                    "basis": block["basis"],
                }
            )
            _edge(
                assembler,
                "UNLOCKED_BY",
                product_id,
                enabler_id,
                edge_props,
                discriminator=scenario_id,
            )


def _project_brief_addresses(
    assembler: ProjectionAssembler,
    briefs: Iterable[Mapping[str, Any]],
) -> None:
    for brief in briefs:
        spans_by_document: dict[str, list[dict[str, Any]]] = {}
        for span in brief.get("spans", []):
            if not isinstance(span, Mapping):
                continue
            address = {
                "document_id": span.get("document_id"),
                "page_index": span.get("page_index"),
                "line_index": span.get("line_index"),
                "span_id": span.get("span_id"),
            }
            spans_by_document.setdefault(str(span.get("document_id")), []).append(
                address
            )
        for row in brief.get("document_evidence", []):
            if not isinstance(row, Mapping):
                continue
            evidence_id = str(row["evidence_id"])
            addresses = spans_by_document.get(str(row.get("document_id")), [])
            existing = assembler.nodes.get(evidence_id)
            if existing is not None:
                existing.properties["document_addresses"] = _list_union(
                    existing.properties.get("document_addresses"),
                    addresses,
                )


def _project_tariff(
    assembler: ProjectionAssembler,
    public_cases: Mapping[str, Mapping[str, Any]],
    tariff_snapshots: list[Mapping[str, Any]],
    tariff_attempts: list[Mapping[str, Any]],
) -> None:
    complete = [
        snapshot
        for snapshot in tariff_snapshots
        if snapshot.get("coverage", {}).get("status") == "COMPLETE"
        or snapshot.get("quality_summary") == "PASS"
    ]
    if not complete:
        attempt = tariff_attempts[-1] if tariff_attempts else {}
        coverage = attempt.get("coverage", attempt)
        evidence_id = str(
            attempt.get("query_hash")
            or coverage.get("query_hash")
            or "ZATCA-TARIFF-UNAVAILABLE"
        )
        as_of = max(
            (
                str(case.get("as_of_date"))
                for case in public_cases.values()
                if case.get("as_of_date")
            ),
            default="UNAVAILABLE",
        )
        props = _base_properties(
            identity="TARIFF-SA12-UNAVAILABLE",
            evidence_id=evidence_id,
            as_of=as_of,
            evidence_class="E",
            synthetic_flag=False,
            scenario_id="PUBLIC",
            origin_kind="ACQUISITION_ATTEMPT",
            origin_ref=str(attempt.get("run_id", "UNAVAILABLE")),
            projection_id=assembler.projection.projection_id,
        )
        props.update(
            {
                "status": "UNAVAILABLE",
                "reason": coverage.get("stop_reason", "NO_COMPLETE_TARIFF_UNIT"),
            }
        )
        assembler.add_node(
            GraphNode("TariffLine", "TARIFF-SA12-UNAVAILABLE", props)
        )
        return

    for snapshot in complete:
        snapshot_id = str(snapshot.get("snapshot_id", "TARIFF-SNAPSHOT"))
        as_of = str(snapshot.get("as_of_date", "UNAVAILABLE"))
        passports = snapshot.get("evidence", [])
        default_evidence = (
            str(
                passports[0].get("passport_id")
                or passports[0].get("evidence_id")
            )
            if passports and isinstance(passports[0], Mapping)
            else snapshot_id
        )
        for row in snapshot.get("rows", []):
            if not isinstance(row, Mapping):
                continue
            national_code = str(row["national_code"])
            identity = f"TARIFF-SA12-{national_code}"
            props = _base_properties(
                identity=identity,
                evidence_id=default_evidence,
                as_of=as_of,
                evidence_class="B",
                synthetic_flag=False,
                scenario_id="PUBLIC",
                origin_kind="PUBLIC_SNAPSHOT",
                origin_ref=snapshot_id,
                projection_id=assembler.projection.projection_id,
            )
            props.update(
                {
                    "national_code": national_code,
                    "description": row.get("description"),
                    "duty_rate": row.get("duty_rate"),
                    "status": "OBSERVED",
                }
            )
            assembler.add_node(GraphNode("TariffLine", identity, props))
            hs6 = str(row.get("hs6", national_code[:6]))
            for product_id, case in sorted(public_cases.items()):
                if str(case.get("opportunity", {}).get("hs6")) != hs6:
                    continue
                edge_props = deepcopy(props)
                edge_props.pop("id")
                _edge(
                    assembler,
                    "CLASSIFIED_AS",
                    product_id,
                    identity,
                    edge_props,
                )


def build_evidence_layer(
    *,
    public_cases: Mapping[str, Mapping[str, Any]],
    scenarios: Mapping[str, Mapping[str, Any]],
    entity_artifacts: list[Mapping[str, Any]],
    briefs: list[Mapping[str, Any]],
    tariff_snapshots: list[Mapping[str, Any]],
    tariff_attempts: list[Mapping[str, Any]],
    projection_id: str,
    engine_run_id: str,
    inputs: list[dict[str, Any]],
) -> GraphProjection:
    """Build phase one from governed evidence only."""
    as_of = max(
        (
            str(case.get("as_of_date"))
            for case in public_cases.values()
            if case.get("as_of_date")
        ),
        default="UNAVAILABLE",
    )
    projection = GraphProjection(
        projection_id=projection_id,
        as_of=as_of,
        inputs=deepcopy(inputs),
        engine={
            "package_version": __version__,
            "engine_run_id": engine_run_id,
        },
    )
    assembler = ProjectionAssembler(projection)
    _entities, entity_names = _project_entities(
        assembler, list(entity_artifacts)
    )
    for _opportunity_id, case in sorted(public_cases.items()):
        _project_public_case(assembler, case, entity_names=entity_names)
    scenario_values = sorted(
        scenarios.values(), key=lambda row: str(row["scenario_id"])
    )
    try:
        validate_shared_enabler_consistency(
            [dict(scenario) for scenario in scenario_values]
        )
    except (EvidenceIntegrityError, ValueError) as exc:
        raise GraphProjectionError(str(exc)) from exc
    for scenario in scenario_values:
        _project_scenario(assembler, scenario)
    _project_enablers(assembler, scenario_values)
    _project_brief_addresses(assembler, briefs)
    _project_tariff(
        assembler,
        public_cases,
        tariff_snapshots,
        tariff_attempts,
    )
    projection.refresh_counts()
    return projection


def _load_repository_cases(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    from ior_mvp.cases.build import build_from_brief

    cases: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "data/snapshots/public").glob("*.json")):
        record = _json(path)
        record["_graph_origin_kind"] = "PUBLIC_SNAPSHOT"
        record["_graph_origin_ref"] = record["snapshot_id"]
        cases[str(record["opportunity"]["id"])] = record
    briefs: list[dict[str, Any]] = []
    for path in sorted((root / "data/cases/briefs").glob("*.json")):
        brief = _json(path)
        briefs.append(brief)
        record = build_from_brief(path, root=root)
        opportunity_id = str(record["opportunity"]["id"])
        if opportunity_id in cases:
            continue
        record["_graph_origin_kind"] = "CASE_BRIEF"
        record["_graph_origin_ref"] = brief["brief_id"]
        cases[opportunity_id] = record
    return cases, briefs


def _engine_run_id(root: Path, inputs: list[dict[str, Any]]) -> tuple[str, str]:
    del root
    authority_rows = [
        row
        for row in inputs
        if row["kind"] in {"AUTHORITY_FILE", "CONFIG"}
    ]
    authority_digest = hashlib.sha256(
        json.dumps(
            authority_rows,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    payload = {
        "inputs": inputs,
        "package_version": __version__,
        "authority_hashes_sha256": authority_digest,
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"ENGINE-{digest[:12]}", authority_digest


def _public_analysis(
    case: Mapping[str, Any],
    *,
    shared_enabler: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clean_case = {
        key: deepcopy(value)
        for key, value in case.items()
        if not key.startswith("_graph_")
    }
    rules = evaluate_rules(clean_case)
    capability = evaluate_capability(
        clean_case["opportunity"]["sector_profile"],
        clean_case["domestic_capability"]["public_dimension_states"],
        clean_case["domestic_capability"]["profile_hard_gates"],
        capability_hard_gate_names(clean_case["domestic_capability"]),
    )
    decision = compute_public_decision(
        clean_case,
        rules,
        capability,
        shared_enabler=shared_enabler,
    )
    r12 = next(row for row in rules if row["rule_id"] == "R12")
    return {
        "opportunity_id": clean_case["opportunity"]["id"],
        "mode": "public",
        "snapshot_id": clean_case["snapshot_id"],
        "as_of_date": clean_case["as_of_date"],
        "rules": rules,
        "capability": capability,
        "decision": decision,
        "evidence_needs": r12["metrics"]["evidence_needs"],
    }


def _simulated_analysis(
    case: Mapping[str, Any],
    scenario: Mapping[str, Any],
    *,
    shared_enabler: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from ior_mvp.simulation import simulate

    clean_case = {
        key: deepcopy(value)
        for key, value in case.items()
        if not key.startswith("_graph_")
    }
    rules = evaluate_rules(clean_case)
    clean_case["rules"] = rules
    branch = simulate(
        clean_case,
        dict(scenario),
        shared_enabler=shared_enabler,
    )
    r12 = next(row for row in rules if row["rule_id"] == "R12")
    return {
        "opportunity_id": clean_case["opportunity"]["id"],
        "mode": "simulated",
        "scenario_id": scenario["scenario_id"],
        "snapshot_id": clean_case["snapshot_id"],
        "as_of_date": clean_case["as_of_date"],
        "rules": rules + branch["synthetic_rules"],
        "capability": branch["capability"],
        "decision": branch["simulation_decision"],
        "evidence_needs": r12["metrics"]["evidence_needs"],
    }


def build_repository_projection(
    root: Path = PROJECT_ROOT,
) -> GraphProjection:
    """Build both projection phases from the repository's governed inputs."""
    from .artifact import projection_id as calculate_projection_id
    from .derived import project_engine_outputs

    inputs = discover_inputs(root)
    cases, briefs = _load_repository_cases(root)
    scenarios = {
        str(record["opportunity_id"]): record
        for path in sorted((root / "data/synthetic").glob("*.json"))
        for record in [_json(path)]
    }
    entities = [
        _json(path)
        for path in sorted((root / "data/entities/resolution").glob("*.json"))
    ]
    tariff_snapshots = [
        _json(path)
        for path in sorted((root / "data/snapshots/tariff").glob("*.json"))
    ]
    tariff_attempts = [
        _json(path)
        for path in sorted((root / "data/raw/zatca_tariff").rglob("attempt.json"))
    ]
    as_of = max(str(case["as_of_date"]) for case in cases.values())
    identity = calculate_projection_id(inputs, as_of=as_of)
    engine_run_id, authority_digest = _engine_run_id(root, inputs)
    projection = build_evidence_layer(
        public_cases=cases,
        scenarios=scenarios,
        entity_artifacts=entities,
        briefs=briefs,
        tariff_snapshots=tariff_snapshots,
        tariff_attempts=tariff_attempts,
        projection_id=identity,
        engine_run_id=engine_run_id,
        inputs=inputs,
    )
    projection.engine["authority_basis_sha256"] = authority_digest
    from .engine_feed import shared_enabler_inputs

    analyses: dict[tuple[str, str], dict[str, Any]] = {
        (opportunity_id, "public"): _public_analysis(
            case,
            shared_enabler=shared_enabler_inputs(
                projection,
                opportunity_id,
                branch="public",
            ),
        )
        for opportunity_id, case in sorted(cases.items())
    }
    for opportunity_id, scenario in sorted(scenarios.items()):
        analyses[(opportunity_id, "simulated")] = _simulated_analysis(
            cases[opportunity_id],
            scenario,
            shared_enabler=shared_enabler_inputs(
                projection,
                opportunity_id,
                branch=("simulated", scenario["scenario_id"]),
            ),
        )
    project_engine_outputs(projection, analyses)
    projection.refresh_counts()
    return projection
