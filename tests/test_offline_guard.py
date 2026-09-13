"""Offline guard autouse and import isolation tests."""

from __future__ import annotations

import ast
import importlib
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


def test_runtime_app_imports_no_neo4j_at_import_time() -> None:
    for module_name in list(sys.modules):
        if module_name == "neo4j" or module_name.startswith("neo4j."):
            del sys.modules[module_name]
        if module_name.startswith("ior_mvp"):
            del sys.modules[module_name]
    importlib.import_module("ior_mvp.app")
    assert "neo4j" not in sys.modules


def test_graph_package_imports_driver_lazily() -> None:
    for module_name in list(sys.modules):
        if module_name == "neo4j" or module_name.startswith("neo4j."):
            del sys.modules[module_name]
        if module_name.startswith("ior_mvp.graph"):
            del sys.modules[module_name]
    importlib.import_module("ior_mvp.graph")
    assert "neo4j" not in sys.modules


def test_default_suite_removes_all_graph_connection_environment_names() -> None:
    source = (PROJECT_ROOT / "tests/conftest.py").read_text(encoding="utf-8")
    for name in (
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
        "NEO4J_AUTH_FILE",
        "AURA_INSTANCEID",
        "AURA_INSTANCENAME",
        "IOR_GRAPH_TARGET",
        "IOR_GRAPH_AURA_OPERATOR",
    ):
        assert f'monkeypatch.delenv("{name}", raising=False)' in source
