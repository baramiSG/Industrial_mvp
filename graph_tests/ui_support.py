from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from browser_tests import harness


AURA_NAMES = (
    "AURA_INSTANCEID",
    "AURA_INSTANCENAME",
    "IOR_GRAPH_AURA_OPERATOR",
)


def build_graph_child_environment(
    root: Path,
    source_environment: Mapping[str, str],
    *,
    target: str,
    optional_probe: Callable[[], Any] | None = None,
) -> dict[str, str]:
    uri = source_environment.get("NEO4J_URI", "")
    if target not in {"compose", "ci"}:
        raise ValueError("GRAPH_UI_TARGET_FORBIDDEN")
    if any(source_environment.get(name) for name in AURA_NAMES):
        raise ValueError("GRAPH_UI_AURA_FORBIDDEN")
    if uri.startswith("neo4j+s://") or ".databases.neo4j.io" in uri:
        raise ValueError("GRAPH_UI_AURA_FORBIDDEN")
    if optional_probe is not None:
        optional_probe()
    child = harness.build_child_environment(root, source_environment)
    child["IOR_GRAPH_TARGET"] = target
    child["PYTHONDONTWRITEBYTECODE"] = "1"
    if target == "compose":
        auth_file = source_environment.get("NEO4J_AUTH_FILE")
        if not auth_file:
            raise ValueError("GRAPH_UI_AUTH_FILE_REQUIRED")
        child["NEO4J_AUTH_FILE"] = auth_file
    else:
        password = source_environment.get("NEO4J_PASSWORD")
        if not password:
            raise ValueError("GRAPH_UI_NEO4J_PASSWORD_REQUIRED")
        child["NEO4J_USERNAME"] = source_environment.get("NEO4J_USERNAME") or "neo4j"
        child["NEO4J_PASSWORD"] = password
        child["NEO4J_DATABASE"] = "neo4j"
    return child


def start_graph_app_server(
    root: Path,
    artifact_dir: Path,
    source_environment: Mapping[str, str],
    *,
    target: str,
):
    child = build_graph_child_environment(
        root,
        source_environment,
        target=target,
    )
    original = harness.build_child_environment
    harness.build_child_environment = lambda _root, _source=None: dict(child)
    try:
        return harness.start_app_server(root, artifact_dir, child)
    finally:
        harness.build_child_environment = original
