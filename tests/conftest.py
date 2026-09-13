"""Pytest fixtures — offline guard for entire test suite."""

from __future__ import annotations

import os
import socket

import pytest

from ior_mvp.acquisition.contracts import OfflineGuardViolation


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
