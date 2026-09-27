from __future__ import annotations

import json
import hashlib
from copy import deepcopy
from pathlib import Path

import yaml

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.artifact import (
    GraphIntegrityError,
    canonical_bytes,
    load_projection,
    projection_id,
    validate_projection,
    write_projection,
)
from ior_mvp.graph.model import GraphEdge, GraphNode
from ior_mvp.graph.projection import (
    GraphProjection,
    build_repository_projection,
    discover_inputs,
)


@pytest.fixture(scope="module")
def projection() -> GraphProjection:
    return build_repository_projection(PROJECT_ROOT)


def test_canonical_bytes_sorted_and_stable(projection: GraphProjection) -> None:
    first = canonical_bytes(projection)
    second = canonical_bytes(deepcopy(projection))
    assert first == second
    assert first.endswith(b"\n")
    payload = json.loads(first)
    assert payload["nodes"] == sorted(
        payload["nodes"], key=lambda row: (row["label"], row["id"])
    )
    assert payload["edges"] == sorted(
        payload["edges"],
        key=lambda row: (row["type"], row["source"], row["target"], row["key"]),
    )


def test_projection_id_from_inputs_not_date() -> None:
    inputs = [
        {
            "path": "data/example.json",
            "sha256": "a" * 64,
            "bytes": 1,
            "kind": "PUBLIC_SNAPSHOT",
            "version": "2.1.0",
        }
    ]
    assert projection_id(inputs, as_of="2026-01-01") == projection_id(
        list(reversed(inputs)), as_of="2026-01-01"
    )
    assert projection_id(inputs, as_of="2026-01-01").startswith(
        "GRAPH-SAU-2026-01-01-"
    )


def test_live_authority_files_are_inputs_without_generated_manifest_cycle() -> None:
    rows = discover_inputs(PROJECT_ROOT)
    paths = {row["path"] for row in rows}
    assert "docs/authority/authority_hashes.json" not in paths
    assert (
        "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx"
        in paths
    )
    assert "docs/core/04_CANONICAL_DATA_MODEL.md" in paths
    assert "config/graph_views.v1.yaml" in paths


_FAMILY_IMPLEMENTATION_INPUTS = {
    "src/ior_mvp/screening/__init__.py",
    "src/ior_mvp/screening/config.py",
}


def _alternate_graph_root(tmp_path: Path) -> Path:
    root = tmp_path / "alternate"
    root.mkdir()
    for directory in ("data", "docs"):
        (root / directory).symlink_to(PROJECT_ROOT / directory, target_is_directory=True)
    config = root / "config"
    config.mkdir()
    for path in (PROJECT_ROOT / "config").iterdir():
        target = config / path.name
        if path.name == "product_families.v1.yaml":
            target.write_bytes(path.read_bytes())
        else:
            target.symlink_to(path, target_is_directory=path.is_dir())
    package = root / "src/ior_mvp"
    package.mkdir(parents=True)
    for path in (PROJECT_ROOT / "src/ior_mvp").glob("*.py"):
        (package / path.name).symlink_to(path)
    for directory in ("cases", "graph"):
        (package / directory).symlink_to(
            PROJECT_ROOT / "src/ior_mvp" / directory, target_is_directory=True
        )
    screening = package / "screening"
    screening.mkdir()
    for name in ("__init__.py", "config.py"):
        (screening / name).symlink_to(PROJECT_ROOT / "src/ior_mvp/screening" / name)
    return root


def test_graph_inputs_bind_exact_required_screening_family_helpers() -> None:
    rows = discover_inputs(PROJECT_ROOT)
    by_path = {row["path"]: row for row in rows}
    assert len(rows) == 240
    assert {
        path for path in by_path if path.startswith("src/ior_mvp/screening/")
    } == _FAMILY_IMPLEMENTATION_INPUTS
    for path in _FAMILY_IMPLEMENTATION_INPUTS:
        assert by_path[path]["kind"] == "ENGINE_IMPLEMENTATION"
        assert by_path[path]["sha256"] == hashlib.sha256(
            (PROJECT_ROOT / path).read_bytes()
        ).hexdigest()


@pytest.mark.parametrize("missing", sorted(_FAMILY_IMPLEMENTATION_INPUTS))
def test_graph_inputs_fail_closed_when_family_helper_is_missing(tmp_path: Path, missing: str) -> None:
    root = _alternate_graph_root(tmp_path)
    (root / missing).unlink()
    with pytest.raises(ValueError, match="Required graph implementation input"):
        discover_inputs(root)


@pytest.mark.parametrize("changed", sorted(_FAMILY_IMPLEMENTATION_INPUTS))
def test_changed_family_helper_changes_graph_input_identity(tmp_path: Path, changed: str) -> None:
    root = _alternate_graph_root(tmp_path)
    baseline = discover_inputs(root)
    target = root / changed
    target.unlink()
    target.write_bytes((PROJECT_ROOT / changed).read_bytes() + b"\n# isolated graph-input mutation\n")
    mutated = discover_inputs(root)
    before = {row["path"]: row for row in baseline}
    after = {row["path"]: row for row in mutated}
    assert len(before) == len(after) == 240
    assert {path for path in before if before[path] != after[path]} == {changed}
    assert projection_id(baseline, as_of="2026-09-26") != projection_id(mutated, as_of="2026-09-26")


def test_graph_build_uses_validated_alternate_root_family_config(
    tmp_path: Path, projection: GraphProjection, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ior_mvp.graph import projection as graph_projection

    root = _alternate_graph_root(tmp_path)
    original_case_loader = graph_projection._load_repository_cases
    # Case-brief paths require real in-root files; only configuration differs here.
    monkeypatch.setattr(
        graph_projection, "_load_repository_cases",
        lambda _root: original_case_loader(PROJECT_ROOT),
    )
    config_path = root / "config/product_families.v1.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["families"]["polypropylene_primary_forms"]["hs4_headings"] = []
    config["families"]["polypropylene_primary_forms"]["status"] = "MEMBERSHIP_UNAVAILABLE"
    config["families"]["technical_plastics_conversion"]["hs4_headings"].append("3902")
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    changed = build_repository_projection(root)

    def sabic_family(graph: GraphProjection) -> bool | None:
        rows = [edge for edge in graph.edges if edge.type == "ADJACENT_TO"
                and edge.source == "COMPANY-f2d406af94a8aac1"
                and edge.target == "SAU-H0-390210"
                and edge.properties.get("attribution_scope") == "PRODUCER_DISCLOSURE"]
        assert len(rows) == 1
        return rows[0].properties["same_process_family"]

    assert sabic_family(projection) is True
    assert sabic_family(changed) is False
    assert projection.projection_id != changed.projection_id
    config["metadata"]["version"] = "invalid"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="product-family version"):
        build_repository_projection(root)


def test_two_builds_are_byte_identical() -> None:
    assert canonical_bytes(
        build_repository_projection(PROJECT_ROOT)
    ) == canonical_bytes(build_repository_projection(PROJECT_ROOT))


def test_write_once_refuses_overwrite(
    tmp_path, projection: GraphProjection
) -> None:
    write_projection(projection, tmp_path)
    changed = deepcopy(projection)
    changed.nodes[0].properties["tampered"] = True
    with pytest.raises(GraphIntegrityError, match="write-once"):
        write_projection(changed, tmp_path)


def test_validate_rejects_missing_provenance_property(
    projection: GraphProjection,
) -> None:
    changed = deepcopy(projection)
    changed.nodes[0].properties.pop("evidence_id")
    with pytest.raises(GraphIntegrityError, match="provenance"):
        validate_projection(changed)


def test_validate_rejects_partition_violation(
    projection: GraphProjection,
) -> None:
    changed = deepcopy(projection)
    public_edge = next(
        edge for edge in changed.edges if not edge.properties["synthetic_flag"]
    )
    target = next(node for node in changed.nodes if node.id == public_edge.target)
    target.properties["synthetic_flag"] = True
    target.properties["scenario_id"] = "SYN-TEST"
    target.properties["evidence_class"] = "D"
    target.properties["display_label"] = "SIMULATED — NOT MINISTRY EVIDENCE"
    target.properties["display_label_ar"] = (
        "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"
    )
    with pytest.raises(GraphIntegrityError, match="partition"):
        validate_projection(changed)


def test_validate_rejects_unknown_label_or_edge_type(
    projection: GraphProjection,
) -> None:
    changed = deepcopy(projection)
    changed.nodes.append(
        GraphNode(
            label="Unknown",
            id="UNKNOWN-1",
            properties=deepcopy(changed.nodes[0].properties),
        )
    )
    with pytest.raises(GraphIntegrityError, match="label"):
        validate_projection(changed)

    changed = deepcopy(projection)
    changed.edges.append(
        GraphEdge(
            type="UNKNOWN",
            source=changed.nodes[0].id,
            target=changed.nodes[1].id,
            key="UNKNOWN-1",
            properties=deepcopy(changed.edges[0].properties),
        )
    )
    with pytest.raises(GraphIntegrityError, match="edge type"):
        validate_projection(changed)


def test_validate_rejects_dangling_endpoint(
    projection: GraphProjection,
) -> None:
    changed = deepcopy(projection)
    changed.edges[0].target = "MISSING-NODE"
    with pytest.raises(GraphIntegrityError, match="endpoint"):
        validate_projection(changed)


def test_derived_elements_flagged_with_engine_run_id(
    projection: GraphProjection,
) -> None:
    derived_nodes = [
        node for node in projection.nodes if node.properties.get("derived") is True
    ]
    derived_edges = [
        edge for edge in projection.edges if edge.properties.get("derived") is True
    ]
    assert derived_nodes
    assert derived_edges
    assert all(node.properties.get("engine_run_id") for node in derived_nodes)
    assert all(edge.properties.get("engine_run_id") for edge in derived_edges)


def test_current_pointer_matches_written_projection(
    tmp_path, projection: GraphProjection
) -> None:
    write_projection(projection, tmp_path)
    pointer = json.loads((tmp_path / "current.json").read_text(encoding="utf-8"))
    assert pointer["projection_id"] == projection.projection_id
    loaded = load_projection(tmp_path)
    assert canonical_bytes(loaded) == canonical_bytes(projection)


def test_s16b_invalid_pointer_and_shared_enabler_provenance_fail_closed(
    tmp_path,
    projection: GraphProjection,
) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "current.json").write_text("{", encoding="utf-8")
    with pytest.raises(GraphIntegrityError, match="current pointer"):
        load_projection(tmp_path)
    changed = deepcopy(projection)
    unlocked = next(edge for edge in changed.edges if edge.type == "UNLOCKED_BY")
    unlocked.properties["valuation_route_code"] = True
    with pytest.raises(GraphIntegrityError, match="Shared-enabler provenance"):
        validate_projection(changed)
