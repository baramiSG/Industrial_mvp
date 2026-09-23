from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from browser_tests.harness import build_child_environment
from graph_tests.ui_support import build_graph_child_environment
from ior_mvp.config import PROJECT_ROOT


def test_graph_ui_modules_import_without_optional_packages_or_side_effects(
    pytestconfig: pytest.Config,
) -> None:
    pytestconfig.addinivalue_line("markers", "graph: live loopback graph test")
    pytestconfig.addinivalue_line("markers", "graph_ui: graph browser integration test")
    for name in (
        "graph_tests.ui_support",
        "graph_tests.test_graph_ui",
        "tests.test_s17_graph_ui_gate",
    ):
        assert importlib.import_module(name)


def test_default_browser_environment_remains_graph_and_credential_stripped() -> None:
    source = {
        "PATH": "/usr/bin",
        "HOME": "/tmp/home",
        "IOR_GRAPH_TARGET": "compose",
        "NEO4J_URI": "bolt://localhost:7688",
        "NEO4J_AUTH_FILE": "/tmp/auth",
        "NEO4J_PASSWORD": "not-copied",
        "AURA_INSTANCEID": "not-copied",
    }
    child = build_child_environment(PROJECT_ROOT, source)
    assert set(child) == {"PATH", "HOME", "LANG", "PYTHONPATH", "PYTHONUNBUFFERED"}


@pytest.mark.parametrize("target", ("aura", "other"))
def test_graph_ui_adapter_rejects_unsupported_targets_before_optional_probe(
    target: str,
) -> None:
    called = False

    def probe() -> None:
        nonlocal called
        called = True

    with pytest.raises(ValueError, match="GRAPH_UI_TARGET_FORBIDDEN"):
        build_graph_child_environment(
            PROJECT_ROOT,
            {"PATH": "/usr/bin", "HOME": "/tmp/home"},
            target=target,
            optional_probe=probe,
        )
    assert called is False


def test_graph_ui_adapter_rejects_aura_shaped_input_before_optional_probe() -> None:
    called = False

    def probe() -> None:
        nonlocal called
        called = True

    with pytest.raises(ValueError, match="GRAPH_UI_AURA_FORBIDDEN"):
        build_graph_child_environment(
            PROJECT_ROOT,
            {
                "PATH": "/usr/bin",
                "HOME": "/tmp/home",
                "NEO4J_AUTH_FILE": "/tmp/auth",
                "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            },
            target="compose",
            optional_probe=probe,
        )
    assert called is False


def test_graph_ui_adapter_passes_only_minimum_compose_configuration() -> None:
    auth = "/tmp/graph-ui-auth"
    child = build_graph_child_environment(
        PROJECT_ROOT,
        {
            "PATH": "/usr/bin",
            "HOME": "/tmp/home",
            "NEO4J_AUTH_FILE": auth,
            "NEO4J_USERNAME": "ignored",
            "NEO4J_PASSWORD": "ignored",
        },
        target="compose",
    )
    assert child["IOR_GRAPH_TARGET"] == "compose"
    assert child["NEO4J_AUTH_FILE"] == auth
    assert "NEO4J_URI" not in child
    assert "NEO4J_USERNAME" not in child
    assert "NEO4J_PASSWORD" not in child


def test_graph_ui_adapter_uses_fixed_ci_identity_and_required_password() -> None:
    child = build_graph_child_environment(
        PROJECT_ROOT,
        {
            "PATH": "/usr/bin",
            "HOME": "/tmp/home",
            "NEO4J_PASSWORD": "run-scoped-test-value",
        },
        target="ci",
    )
    assert child["IOR_GRAPH_TARGET"] == "ci"
    assert child["NEO4J_USERNAME"] == "neo4j"
    assert child["NEO4J_DATABASE"] == "neo4j"
    assert "NEO4J_URI" not in child


def test_live_graph_ui_source_does_not_use_clearing_fixture_or_interception() -> None:
    source = (
        PROJECT_ROOT / "graph_tests/test_graph_ui.py"
    ).read_text(encoding="utf-8")
    assert "loaded_graph" not in source
    assert "page.route" not in source
    assert "context.route" not in source
    assert "verify(connection_spec, projection)" in source
