from __future__ import annotations

import os
from pathlib import Path

import pytest

from graph_tests.ui_support import start_graph_app_server
from ior_mvp.config import PROJECT_ROOT


pytestmark = [pytest.mark.graph, pytest.mark.graph_ui]


def test_live_graph_ui_matches_mirror_without_interception(
    projection,
    connection_spec,
    tmp_path: Path,
) -> None:
    from browser_tests.harness import stop_app_server
    from ior_mvp.graph.loader import verify
    from playwright.sync_api import sync_playwright

    before = verify(connection_spec, projection)
    assert before.projection_id == projection.projection_id
    server = start_graph_app_server(
        PROJECT_ROOT,
        tmp_path / "server",
        os.environ,
        target=os.environ["IOR_GRAPH_TARGET"],
    )
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for locale in ("en", "ar"):
                    page = browser.new_page(
                        viewport={"width": 1440, "height": 900},
                        locale="ar-SA" if locale == "ar" else "en-US",
                    )
                    page.goto(f"{server.base_url}/?locale={locale}")
                    page.locator("[data-open-id]").first.wait_for()
                    page.locator("#graph-toggle").click()
                    page.locator(".graph-visual").wait_for()
                    response = page.request.get(
                        f"{server.base_url}/api/graph/opportunities/"
                        "SAU-H0-721049/views/adjacency?mode=public"
                    )
                    payload = response.json()
                    rendered = set(
                        page.locator(".graph-button-list [data-graph-id]")
                        .evaluate_all("nodes => nodes.map(node => node.dataset.graphId)")
                    )
                    expected = {
                        row["id"] for row in [*payload["nodes"], *payload["edges"]]
                    }
                    assert rendered == expected
                    page.locator(".graph-button-list [data-graph-select='node']").first.click()
                    page.locator(".graph-provenance").wait_for()
                    page.locator("#graph-view-select").select_option("evidence_to_change")
                    page.locator(".graph-state, .graph-visual").wait_for()
                    page.locator("#graph-toggle").click()
                    page.close()
                page = browser.new_page(viewport={"width": 1024, "height": 768})
                page.goto(f"{server.base_url}/?locale=en")
                page.locator("[data-open-id='SAU-H6-760711']").click()
                page.locator(".mode-button[data-mode='simulated']").click()
                page.locator("#graph-toggle").click()
                page.locator("#graph-view-select").select_option("shared_enabler")
                page.locator(".graph-visual").wait_for()
                page.locator("#graph-view-select").select_option("route_blocking")
                page.locator(".graph-state").wait_for()
                page.close()
            finally:
                browser.close()
    finally:
        stop_app_server(server)
    after = verify(connection_spec, projection)
    assert after.projection_id == projection.projection_id
    assert (after.node_count, after.edge_count) == (
        before.node_count,
        before.edge_count,
    )
