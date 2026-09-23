"""Explicit, loopback-only fixtures for live Neo4j graph tests."""

from __future__ import annotations

import os

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.loader import clear, load, resolve_target


_AURA_NAMES = (
    "AURA_INSTANCEID",
    "AURA_INSTANCENAME",
    "IOR_GRAPH_AURA_OPERATOR",
)
_CONNECTION_NAMES = (
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_DATABASE",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--confirm-instance",
        action="store",
        default=None,
        help="Exact Aura instance id for the explicit operator-only suite",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "graph: live loopback graph test")
    config.addinivalue_line(
        "markers",
        "graph_unavailable: requires the loopback graph service to be stopped",
    )
    config.addinivalue_line(
        "markers",
        "graph_ui: live loopback graph and Chromium integration test",
    )


def pytest_sessionstart(session: pytest.Session) -> None:
    if os.environ.get("IOR_GRAPH_TEST_EXPLICIT") != "1":
        pytest.exit(
            "IOR_GRAPH_TEST_EXPLICIT=1 is required for live graph tests",
            returncode=4,
        )
    operator = os.environ.get("IOR_GRAPH_AURA_OPERATOR") == "1"
    target = os.environ.get("IOR_GRAPH_TARGET")
    if operator:
        if (
            target != "aura"
            or not session.config.getoption("--confirm-instance")
        ):
            pytest.exit(
                "Aura operator tests require target aura and explicit confirmation",
                returncode=4,
            )
        return
    inherited_uri = os.environ.get("NEO4J_URI", "")
    if inherited_uri.startswith("neo4j+s://") or ".databases.neo4j.io" in inherited_uri:
        pytest.exit(
            "Aura-shaped NEO4J_URI is forbidden in graph_tests",
            returncode=4,
        )
    if target not in {"compose", "ci"}:
        os.environ["IOR_GRAPH_TARGET"] = "compose"
    for name in _AURA_NAMES:
        os.environ.pop(name, None)
    for name in _CONNECTION_NAMES:
        os.environ.pop(name, None)


@pytest.fixture(scope="session")
def projection():
    return load_projection(PROJECT_ROOT / "data/graph")


@pytest.fixture(scope="session")
def connection_spec(request: pytest.FixtureRequest):
    target = os.environ["IOR_GRAPH_TARGET"]
    return resolve_target(
        target,
        confirm_instance=(
            request.config.getoption("--confirm-instance")
            if target == "aura"
            else None
        ),
    )


@pytest.fixture(scope="session")
def loaded_graph(projection, connection_spec):
    clear(
        connection_spec,
        confirm=connection_spec.clear_identity,
    )
    first = load(connection_spec, projection)
    second = load(connection_spec, projection)
    return first, second
