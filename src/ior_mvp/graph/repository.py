"""Offline repository for the governed graph projection artifact."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from ior_mvp.config import DATA_DIR

if TYPE_CHECKING:
    from .projection import GraphProjection


class GraphRepositoryError(RuntimeError):
    """Raised when the governed graph artifact is unavailable or invalid."""


@lru_cache(maxsize=1)
def graph_projection() -> GraphProjection:
    """Load the current immutable projection without opening a socket."""
    from .artifact import GraphIntegrityError, load_projection

    try:
        return load_projection(DATA_DIR / "graph")
    except GraphIntegrityError as exc:
        raise GraphRepositoryError(str(exc)) from exc


def load_graph_projection(root: Path) -> GraphProjection:
    """Load a projection from an explicit data/graph root."""
    from .artifact import GraphIntegrityError, load_projection

    try:
        return load_projection(root)
    except GraphIntegrityError as exc:
        raise GraphRepositoryError(str(exc)) from exc


def clear_graph_caches() -> None:
    """Clear process-local immutable projection caches."""
    graph_projection.cache_clear()
