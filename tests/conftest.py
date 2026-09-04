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

    original_connect = socket.socket.connect

    def guarded_connect(self: socket.socket, address: object) -> None:
        raise OfflineGuardViolation(
            f"Test suite blocked socket connect to {address!r}"
        )

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
