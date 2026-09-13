from __future__ import annotations

import os

import pytest

from ior_mvp.graph.loader import verify


pytestmark = pytest.mark.graph


def test_aura_verification_is_operator_only(
    connection_spec,
    projection,
) -> None:
    if os.environ.get("IOR_GRAPH_AURA_OPERATOR") != "1":
        pytest.skip("AURA_OPERATOR_ONLY")
    assert connection_spec.target == "aura"
    report = verify(connection_spec, projection)
    assert report.projection_id == projection.projection_id
    assert report.provenance_complete is True
    assert report.partition_valid is True
