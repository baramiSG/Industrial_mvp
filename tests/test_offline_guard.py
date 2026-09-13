"""Offline guard autouse and import isolation tests."""

from __future__ import annotations

import ast
import socket
import sys
from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import OfflineGuardViolation
from ior_mvp.config import PROJECT_ROOT


def test_conftest_blocks_socket_connect() -> None:
    with pytest.raises(OfflineGuardViolation):
        socket.socket().connect(("127.0.0.1", 9))


def test_only_transport_imports_network_modules() -> None:
    acquisition_dir = PROJECT_ROOT / "src" / "ior_mvp" / "acquisition"
    network_modules = {"urllib.request", "urllib.error", "http.client", "socket", "ssl"}
    offenders: list[str] = []
    for path in acquisition_dir.rglob("*.py"):
        if path.name == "transport.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split(".")[0]
                    if base in {"urllib", "http", "socket", "ssl"}:
                        offenders.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                base = node.module.split(".")[0]
                if base in {"urllib", "http", "socket", "ssl"}:
                    offenders.append(f"{path.name}: from {node.module}")
    assert not offenders, offenders


def test_runtime_modules_do_not_import_acquisition_transport() -> None:
    for mod in list(sys.modules):
        if mod.startswith("ior_mvp.acquisition"):
            del sys.modules[mod]
    import ior_mvp.app  # noqa: F401
    import ior_mvp.data_repository  # noqa: F401

    assert "ior_mvp.acquisition.transport" not in sys.modules


def test_runtime_app_does_not_import_cases_package() -> None:
    for module_name in list(sys.modules):
        if module_name.startswith("ior_mvp"):
            del sys.modules[module_name]
    import ior_mvp.app  # noqa: F401

    assert not any(
        module_name.startswith("ior_mvp.cases") for module_name in sys.modules
    )
    assert "ior_mvp.acquisition.transport" not in sys.modules
