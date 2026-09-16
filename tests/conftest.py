"""Pytest fixtures — offline guard for entire test suite."""

from __future__ import annotations

import os
import socket

import pytest

from ior_mvp.acquisition.contracts import OfflineGuardViolation
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.engine_feed import shared_enabler_inputs
from ior_mvp.graph.projection import build_repository_projection


@pytest.fixture(autouse=True)
def _offline_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block all socket connections and remove live acquisition env var."""
    monkeypatch.delenv("IOR_ACQUISITION_LIVE", raising=False)
    monkeypatch.delenv("NEO4J_URI", raising=False)
    monkeypatch.delenv("NEO4J_USERNAME", raising=False)
    monkeypatch.delenv("NEO4J_PASSWORD", raising=False)
    monkeypatch.delenv("NEO4J_DATABASE", raising=False)
    monkeypatch.delenv("NEO4J_AUTH_FILE", raising=False)
    monkeypatch.delenv("AURA_INSTANCEID", raising=False)
    monkeypatch.delenv("AURA_INSTANCENAME", raising=False)
    monkeypatch.delenv("IOR_GRAPH_TARGET", raising=False)
    monkeypatch.delenv("IOR_GRAPH_AURA_OPERATOR", raising=False)

    original_connect = socket.socket.connect

    def guarded_connect(self: socket.socket, address: object) -> None:
        raise OfflineGuardViolation(
            f"Test suite blocked socket connect to {address!r}"
        )

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)


@pytest.fixture(scope="session")
def s16b_fresh_projection():
    return build_repository_projection(PROJECT_ROOT)


@pytest.fixture
def s16b_graph_cache(monkeypatch: pytest.MonkeyPatch, s16b_fresh_projection):
    from ior_mvp.graph import repository

    monkeypatch.setattr(repository, "graph_projection", lambda: s16b_fresh_projection)
    return s16b_fresh_projection


@pytest.fixture
def s16b_simulate(s16b_fresh_projection):
    from ior_mvp.simulation import simulate

    def run(public: dict, scenario: dict) -> dict:
        return simulate(
            public,
            scenario,
            shared_enabler=shared_enabler_inputs(
                s16b_fresh_projection,
                public["opportunity"]["id"],
                branch=("simulated", scenario["scenario_id"]),
            ),
        )

    return run
