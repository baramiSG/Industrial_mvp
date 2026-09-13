"""Canonical graph artifact validation, persistence, and reconstruction."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .model import (
    EDGE_TYPES,
    LABELS,
    ORIGIN_KINDS,
    PROVENANCE_KEYS,
    GraphEdge,
    GraphModelError,
    GraphNode,
    assert_endpoint,
)
from .projection import GraphProjection


class GraphIntegrityError(ValueError):
    """Raised when a graph artifact violates its governed contract."""


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def projection_id(
    inputs: list[dict[str, Any]],
    *,
    as_of: str,
) -> str:
    """Derive the projection identity only from governed inputs and data date."""
    ordered = sorted(inputs, key=lambda row: str(row["path"]))
    digest = hashlib.sha256(
        json.dumps(
            ordered,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return f"GRAPH-SAU-{as_of}-{digest[:12]}"


def _node_dict(node: GraphNode) -> dict[str, Any]:
    return {
        "label": node.label,
        "id": node.id,
        "properties": node.properties,
    }


def _edge_dict(edge: GraphEdge) -> dict[str, Any]:
    return {
        "type": edge.type,
        "source": edge.source,
        "target": edge.target,
        "key": edge.key,
        "properties": edge.properties,
    }


def projection_payload(projection: GraphProjection) -> dict[str, Any]:
    """Return the canonical JSON-shaped projection payload."""
    projection.refresh_counts()
    return {
        "projection_id": projection.projection_id,
        "as_of": projection.as_of,
        "inputs": sorted(
            projection.inputs,
            key=lambda row: str(row["path"]),
        ),
        "engine": projection.engine,
        "counts": projection.counts,
        "nodes": [
            _node_dict(node)
            for node in sorted(
                projection.nodes,
                key=lambda item: (item.label, item.id),
            )
        ],
        "edges": [
            _edge_dict(edge)
            for edge in sorted(
                projection.edges,
                key=lambda item: (
                    item.type,
                    item.source,
                    item.target,
                    item.key,
                ),
            )
        ],
    }


def canonical_bytes(projection: GraphProjection) -> bytes:
    """Serialize a graph projection with stable ordering."""
    return _json_bytes(projection_payload(projection))


def _validate_provenance(
    properties: Mapping[str, Any],
    identity: str,
) -> None:
    missing = [
        key
        for key in PROVENANCE_KEYS
        if key not in properties or properties[key] is None
    ]
    if missing:
        raise GraphIntegrityError(
            f"Missing provenance on {identity}: {', '.join(missing)}"
        )
    if properties["evidence_class"] not in {"A", "B", "C", "D", "E"}:
        raise GraphIntegrityError(
            f"Invalid evidence class on {identity}"
        )
    synthetic = properties["synthetic_flag"]
    if not isinstance(synthetic, bool):
        raise GraphIntegrityError(
            f"Invalid synthetic provenance flag on {identity}"
        )
    scenario_id = properties["scenario_id"]
    if not synthetic and scenario_id != "PUBLIC":
        raise GraphIntegrityError(
            f"Public provenance requires the PUBLIC sentinel: {identity}"
        )
    if synthetic:
        if scenario_id == "PUBLIC":
            raise GraphIntegrityError(
                f"Synthetic provenance lacks a scenario id: {identity}"
            )
        for key in ("display_label", "display_label_ar"):
            if not isinstance(properties.get(key), str) or not properties[key]:
                raise GraphIntegrityError(
                    f"Synthetic graph element lacks {key}: {identity}"
                )
    if properties.get("origin_kind") not in ORIGIN_KINDS:
        raise GraphIntegrityError(
            f"Invalid canonical origin on {identity}"
        )
    if not isinstance(properties.get("origin_ref"), str) or not properties[
        "origin_ref"
    ]:
        raise GraphIntegrityError(
            f"Missing canonical origin reference on {identity}"
        )
    if properties.get("derived") is True and not isinstance(
        properties.get("engine_run_id"), str
    ):
        raise GraphIntegrityError(
            f"Derived graph element lacks engine_run_id: {identity}"
        )


def validate_projection(projection: GraphProjection) -> None:
    """Validate vocabulary, provenance, partition, and referential integrity."""
    if not projection.projection_id.startswith("GRAPH-SAU-") and not (
        projection.projection_id == "GRAPH-TEST"
    ):
        raise GraphIntegrityError("Graph projection id is invalid")
    node_ids: set[str] = set()
    labels_by_id: dict[str, str] = {}
    for node in projection.nodes:
        if node.label not in LABELS:
            raise GraphIntegrityError(
                f"Unknown governed node label: {node.label}"
            )
        if node.id in node_ids:
            raise GraphIntegrityError(f"Duplicate graph node id: {node.id}")
        node_ids.add(node.id)
        labels_by_id[node.id] = node.label
        if node.properties.get("id") != node.id:
            raise GraphIntegrityError(
                f"Node id property mismatch: {node.id}"
            )
        _validate_provenance(node.properties, node.id)

    edge_keys: set[str] = set()
    properties_by_id = {
        node.id: node.properties for node in projection.nodes
    }
    for edge in projection.edges:
        if edge.type not in EDGE_TYPES:
            raise GraphIntegrityError(
                f"Unknown governed edge type: {edge.type}"
            )
        if edge.key in edge_keys:
            raise GraphIntegrityError(
                f"Duplicate graph relationship key: {edge.key}"
            )
        edge_keys.add(edge.key)
        if edge.source not in node_ids or edge.target not in node_ids:
            raise GraphIntegrityError(
                f"Relationship endpoint is missing: {edge.key}"
            )
        try:
            assert_endpoint(
                labels_by_id[edge.source],
                edge.type,
                labels_by_id[edge.target],
            )
        except GraphModelError as exc:
            raise GraphIntegrityError(str(exc)) from exc
        if edge.properties.get("key") != edge.key:
            raise GraphIntegrityError(
                f"Relationship key property mismatch: {edge.key}"
            )
        _validate_provenance(edge.properties, edge.key)
        if edge.properties["synthetic_flag"] is False and (
            properties_by_id[edge.source]["synthetic_flag"] is True
            or properties_by_id[edge.target]["synthetic_flag"] is True
        ):
            raise GraphIntegrityError(
                f"Public/Class-D partition violation: {edge.key}"
            )

    tariff_markers = {
        node.id
        for node in projection.nodes
        if node.label == "TariffLine"
        and node.properties.get("status") == "UNAVAILABLE"
    }
    if tariff_markers and any(
        edge.type == "CLASSIFIED_AS" and edge.target in tariff_markers
        for edge in projection.edges
    ):
        raise GraphIntegrityError(
            "Tariff UNAVAILABLE marker cannot receive CLASSIFIED_AS"
        )

    projection.refresh_counts()
    if projection.counts["nodes"] != len(node_ids):
        raise GraphIntegrityError("Graph node count is inconsistent")
    if projection.counts["edges"] != len(edge_keys):
        raise GraphIntegrityError("Graph relationship count is inconsistent")


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_projection(
    projection: GraphProjection,
    root: Path,
) -> Path:
    """Write one immutable projection and update the canonical current pointer."""
    validate_projection(projection)
    projection_root = root / "projections" / projection.projection_id
    projection_path = projection_root / "projection.json"
    manifest_path = projection_root / "manifest.json"
    content = canonical_bytes(projection)
    manifest = {
        "projection_id": projection.projection_id,
        "projection_sha256": _sha256_bytes(content),
        "projection_bytes": len(content),
        "built_from_commit": "UNAVAILABLE_AT_BUILD",
    }
    manifest_content = _json_bytes(manifest)
    if projection_root.exists():
        if (
            not projection_path.is_file()
            or projection_path.read_bytes() != content
            or not manifest_path.is_file()
            or manifest_path.read_bytes() != manifest_content
        ):
            raise GraphIntegrityError(
                f"Graph write-once conflict: {projection.projection_id}"
            )
    else:
        projection_root.mkdir(parents=True)
        projection_path.write_bytes(content)
        manifest_path.write_bytes(manifest_content)
    pointer = {
        "projection_id": projection.projection_id,
        "sha256": manifest["projection_sha256"],
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "current.json").write_bytes(_json_bytes(pointer))
    return projection_root


def _projection_from_payload(payload: Mapping[str, Any]) -> GraphProjection:
    try:
        projection = GraphProjection(
            projection_id=str(payload["projection_id"]),
            as_of=str(payload["as_of"]),
            inputs=[dict(row) for row in payload["inputs"]],
            engine=dict(payload["engine"]),
            nodes=[
                GraphNode(
                    label=str(row["label"]),
                    id=str(row["id"]),
                    properties=dict(row["properties"]),
                )
                for row in payload["nodes"]
            ],
            edges=[
                GraphEdge(
                    type=str(row["type"]),
                    source=str(row["source"]),
                    target=str(row["target"]),
                    key=str(row["key"]),
                    properties=dict(row["properties"]),
                )
                for row in payload["edges"]
            ],
            counts=dict(payload["counts"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise GraphIntegrityError("Graph projection JSON shape is invalid") from exc
    validate_projection(projection)
    return projection


def load_projection(
    root: Path,
    projection_identity: str | None = None,
) -> GraphProjection:
    """Load and hash-check the current or named projection."""
    if projection_identity is None:
        pointer_path = root / "current.json"
        if not pointer_path.is_file():
            raise GraphIntegrityError("Graph current pointer is missing")
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        projection_identity = str(pointer["projection_id"])
        expected_hash = str(pointer["sha256"])
    else:
        expected_hash = ""
    projection_root = root / "projections" / projection_identity
    projection_path = projection_root / "projection.json"
    manifest_path = projection_root / "manifest.json"
    if not projection_path.is_file() or not manifest_path.is_file():
        raise GraphIntegrityError(
            f"Graph projection files are missing: {projection_identity}"
        )
    content = projection_path.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = _sha256_bytes(content)
    if (
        manifest.get("projection_id") != projection_identity
        or manifest.get("projection_sha256") != digest
        or manifest.get("projection_bytes") != len(content)
        or (expected_hash and expected_hash != digest)
    ):
        raise GraphIntegrityError(
            f"Graph projection manifest mismatch: {projection_identity}"
        )
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise GraphIntegrityError("Graph projection JSON is invalid") from exc
    if not isinstance(payload, Mapping):
        raise GraphIntegrityError("Graph projection must be an object")
    return _projection_from_payload(payload)
