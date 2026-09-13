from __future__ import annotations

import pytest

from ior_mvp.graph.loader import GraphSafetyError, clear


pytestmark = pytest.mark.graph


def test_first_load_creates_counts_second_load_creates_nothing(
    projection,
    loaded_graph,
) -> None:
    first, second = loaded_graph
    assert first.nodes_created == projection.counts["nodes"]
    assert first.relationships_created == projection.counts["edges"]
    assert second.nodes_created == 0
    assert second.relationships_created == 0


def test_clear_refused_without_confirm(connection_spec) -> None:
    called = False

    def forbidden_driver(_spec):
        nonlocal called
        called = True
        raise AssertionError("driver must not be created")

    with pytest.raises(GraphSafetyError, match="CLEAR_CONFIRMATION_MISMATCH"):
        clear(
            connection_spec,
            confirm="wrong-target",
            driver_factory=forbidden_driver,
        )
    assert called is False
