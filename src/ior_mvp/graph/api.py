"""Unmounted S16a graph API contract for the S17 renderer."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

import yaml
from fastapi import APIRouter, Depends, HTTPException

from ior_mvp.config import CONFIG_DIR

from .repository import GraphRepositoryError, graph_projection
from .service import GraphNotFound, GraphService


GraphMode = Literal["public", "simulated"]
_VIEW_IDS = (
    "adjacency",
    "route_blocking",
    "shared_enabler",
    "evidence_to_change",
)

router = APIRouter(prefix="/api/graph", tags=["graph"])


@lru_cache(maxsize=1)
def load_view_catalogue() -> dict[str, Any]:
    """Load and validate the fixed bilingual S17 graph-view catalogue."""
    path = CONFIG_DIR / "graph_views.v1.yaml"
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RuntimeError("Graph view catalogue could not be loaded") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Graph view catalogue must be a mapping")
    metadata = payload.get("metadata")
    views = payload.get("views")
    if (
        not isinstance(metadata, dict)
        or metadata.get("version") != "1.0.0"
        or not isinstance(views, list)
        or tuple(row.get("view_id") for row in views) != _VIEW_IDS
    ):
        raise RuntimeError("Graph view catalogue contract is invalid")
    for row in views:
        if (
            not isinstance(row, dict)
            or set(row.get("label", {})) != {"en", "ar"}
            or set(row.get("description", {})) != {"en", "ar"}
            or not all(
                isinstance(value, str) and value.strip() == value and value
                for group in ("label", "description")
                for value in row[group].values()
            )
        ):
            raise RuntimeError("Graph view catalogue parity is invalid")
    return payload


def get_graph_service() -> GraphService:
    """Construct the live service from names already present in the process."""
    try:
        projection = graph_projection()
    except GraphRepositoryError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "GRAPH_ARTIFACT_INTEGRITY_ERROR"},
        ) from exc
    return GraphService.from_environment(projection)


@router.get("/status")
def graph_status(
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    """Return typed graph availability without leaking connection details."""
    return service.status()


@router.get("/catalogue")
def graph_catalogue() -> dict[str, Any]:
    """Return the fixed bilingual view catalogue even when Neo4j is down."""
    return load_view_catalogue()


@router.get("/opportunities/{opportunity_id}/views/{view_id}")
def graph_view(
    opportunity_id: str,
    view_id: str,
    mode: GraphMode = "public",
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    """Return one governed view or a typed fail-closed payload."""
    try:
        return service.view(view_id, opportunity_id, mode)
    except GraphNotFound as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": exc.code},
        ) from exc


@router.get("/portfolio/shared-enablers")
def shared_enablers(
    mode: GraphMode = "public",
    service: GraphService = Depends(get_graph_service),
) -> dict[str, Any]:
    """Return the typed shared-enabler portfolio input."""
    return service.shared_enablers(mode)
