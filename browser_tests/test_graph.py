from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from browser_tests.graph_fixtures import (
    artifact_graph_payload,
    graph_catalogue_fixture,
    route_blocking_fixture,
    unavailable_graph_payload,
)
from browser_tests.graph_pages import (
    assert_graph_caption_edge_clearance,
    assert_graph_svg_labels_within_viewbox,
    assert_graph_visible_arrow_endpoints,
    install_graph_routes,
    open_graph,
    prepare_graph_capture,
    select_graph_element,
    select_graph_view,
    select_native_graph_element,
    select_svg_graph_element,
    wait_graph_request_complete,
)
from browser_tests.harness import (
    AR,
    CASES,
    DESKTOP,
    EN,
    TABLET,
    BrowserFailureCollector,
    BrowserSession,
    format_axe_violations,
    run_axe,
)
from browser_tests.pages import goto_portfolio, locale_bundle, select_case, select_mode
from ior_mvp.decision_engine import analyze
from ior_mvp.evidence import synthetic_display_labels


pytestmark = pytest.mark.e2e

GRAPH_REPLACEMENT_SCREENS = frozenset({
    "journey-i-graph-adjacency",
    "journey-i-graph-route-blocking",
    "journey-i-graph-shared-enabler",
    "journey-i-graph-evidence-to-change",
})


@pytest.fixture(scope="session")
def graph_visual_preflight_root() -> Path:
    root = Path(os.environ["IOR_E2E_ARTIFACT_DIR"]) / "graph-preflight"
    root.mkdir(parents=True, exist_ok=True)
    yield root
    files = sorted(root.glob("*/*/*.webp"))
    all_baselines = sorted(
        Path("browser_tests/baselines/v0.3.0").glob("*/*/*.webp")
    )
    graph_baselines = {
        path for path in all_baselines if path.stem in GRAPH_REPLACEMENT_SCREENS
    }
    retained = [
        path for path in all_baselines if path.stem not in GRAPH_REPLACEMENT_SCREENS
    ]
    assert len(files) == 16
    assert len(graph_baselines) == 16
    assert len(retained) == 96
    assert {path.stem for path in files} == GRAPH_REPLACEMENT_SCREENS
    assert all(path.stat().st_size <= 600 * 1024 for path in files)
    retained_bytes = sum(path.stat().st_size for path in retained)
    new_bytes = sum(path.stat().st_size for path in files)
    total_bytes = retained_bytes + new_bytes
    assert total_bytes <= 16 * 1024 * 1024
    (root / "summary.json").write_text(
        json.dumps(
            {
                "retained_images": len(retained),
                "retained_bytes": retained_bytes,
                "new_images": len(files),
                "new_bytes": new_bytes,
                "total_bytes": total_bytes,
                "headroom_bytes": (16 * 1024 * 1024) - total_bytes,
                "graph_replacement_screens": sorted(GRAPH_REPLACEMENT_SCREENS),
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def test_graph_collapsed_lazy_catalogue_and_views(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    requests = install_graph_routes(page)
    goto_portfolio(page, "public", EN)
    assert requests == []
    assert page.locator("#graph-toggle").get_attribute("aria-expanded") == "false"
    open_graph(page)
    assert requests[0] == "/api/graph/catalogue"
    assert "/views/adjacency?mode=public" in requests[1]
    for view_id in ("route_blocking", "shared_enabler", "evidence_to_change"):
        select_graph_view(page, view_id)
    assert page.locator("#graph-view-select option").count() == 4


def test_graph_node_edge_selection_and_passports(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    install_graph_routes(page)
    goto_portfolio(page, "public", EN)
    open_graph(page)
    select_svg_graph_element(page, "node")
    assert page.locator(".graph-provenance").count() == 1
    select_native_graph_element(page, "node", "Enter")
    select_svg_graph_element(page, "edge")
    assert page.locator(".graph-svg-edge-hit").first.is_visible()
    select_native_graph_element(page, "edge", "Space")
    assert page.locator(
        ".graph-button-list [data-graph-select='edge'][aria-pressed='true']"
    ).count() == 1


def test_graph_related_evidence_and_unresolved_references(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    install_graph_routes(page)
    goto_portfolio(page, "public", EN)
    open_graph(page)
    select_graph_view(page, "evidence_to_change")
    select_graph_element(page, "node")
    assert page.locator(".graph-passport, .graph-unresolved").count() >= 1
    foil = next(case for case in CASES if case.id == "SAU-H6-760711")
    goto_portfolio(page, "simulated", EN)
    select_case(page, foil, "simulated", EN)
    open_graph(page)
    select_graph_view(page, "shared_enabler")
    payload = artifact_graph_payload("shared_enabler", foil.id, "simulated")
    edge = payload["edges"][0]
    references = sorted({
        edge["provenance"]["evidence_id"],
        *edge["properties"].get("evidence_ids", []),
    })
    related_id = next(
        node["id"] for node in payload["nodes"]
        if node["label"] == "Product" and node["id"] != foil.id
    )

    def related(marker: str) -> dict:
        result = deepcopy(analyze(related_id, "simulated"))
        result["evidence"] = [
            {
                "evidence_id": evidence_id,
                "title": marker,
                "source": "DEMO_GENERATOR",
                "url": "https://example.invalid/test-only",
                "period": "2026",
                "retrieved_at": "2026-09-16",
                "status": "synthetic",
                "evidence_class": "D",
                "synthetic_flag": True,
                "supports": ["TEST_ONLY_SELECTION_RACE"],
                "reviewer_status": "test-only",
                "contradiction": None,
                "scenario_id": "TEST-ONLY-SELECTION-RACE",
                "display_label": synthetic_display_labels()["en"],
            }
            for evidence_id in references
        ]
        return result

    page.evaluate(
        """([needle, payloads]) => {
          const original = window.fetch;
          let callIndex = 0;
          window.__s17EvidencePending = [];
          window.__s17EvidenceSettled = 0;
          window.fetch = (input, init) => {
            if (String(input).includes(needle)) {
              const payload = payloads[callIndex];
              callIndex += 1;
              return new Promise(resolve => {
                window.__s17EvidencePending.push({
                  release: () => resolve({
                    ok: true,
                    status: 200,
                    json: async () => {
                      window.__s17EvidenceSettled += 1;
                      return payload;
                    },
                  }),
                });
              });
            }
            return original.call(window, input, init);
          };
        }""",
        [
            f"/api/opportunities/{related_id}?mode=simulated",
            [related("STALE-FIRST-SELECTION"), related("CURRENT-SECOND-SELECTION")],
        ],
    )
    button = page.locator(
        ".graph-button-list [data-graph-select='edge']"
    ).first
    button.click()
    page.wait_for_function("window.__s17EvidencePending.length === 1")
    button.click()
    page.wait_for_function("window.__s17EvidencePending.length === 2")
    page.evaluate("window.__s17EvidencePending.splice(1, 1)[0].release()")
    page.wait_for_function("window.__s17EvidenceSettled === 1")
    page.locator(".graph-passport").filter(
        has_text="CURRENT-SECOND-SELECTION"
    ).wait_for()
    page.evaluate("window.__s17EvidencePending.shift().release()")
    page.wait_for_function("window.__s17EvidenceSettled === 2")
    page.evaluate(
        "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
    )
    assert page.locator(".graph-passport", has_text="CURRENT-SECOND-SELECTION").count() >= 1
    assert page.locator(".graph-passport", has_text="STALE-FIRST-SELECTION").count() == 0


def test_graph_empty_unavailable_and_transport_states(
    new_context: Any,
    app_server: Any,
) -> None:
    context = new_context(
        base_url=app_server.base_url,
        locale=EN.bcp47,
        viewport=DESKTOP.as_dict(),
    )
    collector = BrowserFailureCollector(app_server.base_url)
    collector.attach_context(context)
    page = context.new_page()
    collector.attach_page(page)
    install_graph_routes(page)
    goto_portfolio(page, "public", EN)
    open_graph(page)
    select_graph_view(page, "route_blocking")
    assert page.locator(".graph-state").count() == 1
    page.unroute("**/api/graph/**")
    install_graph_routes(
        page,
        lambda view, opportunity, mode: unavailable_graph_payload(
            view, opportunity, mode, "CONNECTION_FAILED",
        ),
    )
    page.locator("#graph-toggle").click()
    open_graph(page)
    assert page.locator(".graph-state-error").count() == 1
    strings = locale_bundle(EN)["strings"]
    unavailable = page.locator(".graph-state-error").inner_text()
    assert strings["graph.unavailable_title"] in unavailable
    assert strings["graph.failure.connection_failed"] in unavailable
    assert collector.records == ()
    page.locator("#graph-toggle").click()
    page.unroute("**/api/graph/**")
    page.route(
        "**/api/graph/**",
        lambda route: route.fulfill(
            status=503,
            body='{"detail":"test-only graph transport failure"}',
            content_type="application/json",
        ),
    )
    open_graph(page)
    assert page.locator(".graph-state-error").count() == 1
    transport = page.locator(".graph-state-error").inner_text()
    assert strings["graph.error_title"] in transport
    assert strings["graph.unavailable_title"] not in transport
    assert len(collector.records) == 2
    http_error = next(
        record for record in collector.records
        if record.category == "app-http-error"
    )
    console_error = next(
        record for record in collector.records
        if record.category == "console-error"
    )
    expected_url = (
        f"{app_server.base_url}/api/graph/opportunities/"
        "SAU-H0-721049/views/adjacency?mode=public"
    )
    assert (
        http_error.method,
        http_error.status,
        http_error.url,
        http_error.detail,
    ) == (
        "GET",
        503,
        expected_url,
        "app response status is at least 400",
    )
    assert (
        console_error.method,
        console_error.status,
        console_error.url,
        console_error.detail,
    ) == (
        "",
        None,
        "",
        "Failed to load resource: the server responded with a status of 503 (Service Unavailable)",
    )
    context.close()


def _assert_public_mode_blocks_stale_simulated_graph(
    page: Any,
    graph_requests: list[str],
) -> None:
    goto_portfolio(page, "simulated", EN)
    page.evaluate(
        """() => {
          const original = window.fetch;
          window.__s17PublicOriginalFetch = original;
          window.__s17PublicPending = [];
          window.__s17PublicSettled = [];
          window.fetch = (input, init) => {
            const url = String(input);
            if (url.includes('/api/opportunities') && url.includes('mode=public')) {
              return new Promise((resolve, reject) => {
                window.__s17PublicPending.push({
                  release: () => original.call(window, input, init).then(
                    response => {
                      window.__s17PublicSettled.push(url);
                      resolve(response);
                    },
                    reject,
                  ),
                });
              });
            }
            return original.call(window, input, init);
          };
        }"""
    )
    page.locator(".mode-button[data-mode='public']").click()
    page.wait_for_function("window.__s17PublicPending.length === 1")
    transition_disabled = page.locator("#graph-toggle").is_disabled()
    page.locator("#graph-toggle").evaluate("(node) => node.click()")
    if not transition_disabled:
        page.locator(".graph-svg-node.is-synthetic").first.wait_for()
    stale_simulated_committed = (
        page.locator(".graph-svg-node.is-synthetic").count() > 0
    )
    stale_graph_requests = [
        request for request in graph_requests if "mode=simulated" in request
    ]
    page.evaluate(
        "window.__s17PublicPending.splice(0).forEach(entry => entry.release())"
    )
    page.wait_for_function(
        "window.__s17PublicSettled.length === 1"
        " && window.__s17PublicPending.length === 2"
    )
    page.evaluate(
        "window.__s17PublicPending.splice(0).forEach(entry => entry.release())"
    )
    page.wait_for_function("window.__s17PublicSettled.length === 3")
    select_mode(page, "public", EN)
    assert {
        "transition_disabled": transition_disabled,
        "stale_graph_requests": stale_graph_requests,
        "stale_simulated_committed": stale_simulated_committed,
    } == {
        "transition_disabled": True,
        "stale_graph_requests": [],
        "stale_simulated_committed": False,
    }
    assert page.locator(".graph-svg-node.is-synthetic").count() == 0
    page.evaluate("window.fetch = window.__s17PublicOriginalFetch")


def test_graph_context_races_and_close(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    graph_requests = install_graph_routes(page)
    _assert_public_mode_blocks_stale_simulated_graph(page, graph_requests)
    goto_portfolio(page, "simulated", EN)
    page.evaluate(
        """() => {
          const original = window.fetch;
          window.__s17GraphPending = [];
          window.__s17GraphSettled = [];
          window.fetch = (input, init) => {
            const url = String(input);
            if (url.includes('/api/graph/opportunities/')) {
              return new Promise((resolve, reject) => {
                window.__s17GraphPending.push({
                  url,
                  release: () => original.call(window, input, init).then(
                    response => {
                      window.__s17GraphSettled.push(url);
                      resolve(response);
                    },
                    error => {
                      window.__s17GraphSettled.push(url);
                      reject(error);
                    },
                  ),
                });
              });
            }
            return original.call(window, input, init);
          };
        }"""
    )
    page.locator("#graph-toggle").click()
    page.wait_for_function("window.__s17GraphPending.length === 1")
    page.locator(".mode-button[data-mode='public']").click()
    assert "active" in (
        page.locator(".mode-button[data-mode='simulated']").get_attribute("class")
        or ""
    )
    page.evaluate("window.__s17GraphPending.shift().release()")
    page.wait_for_function("window.__s17GraphSettled.length === 1")
    page.wait_for_function(
        "document.querySelector(\".mode-button[data-mode='public']\")"
        ".classList.contains('active')"
    )
    select_mode(page, "public", EN)
    assert page.locator("#graph-toggle").get_attribute("aria-expanded") == "false"
    assert page.locator("#graph-panel[hidden]").count() == 1
    assert page.locator(".graph-svg-node.is-synthetic").count() == 0
    select_mode(page, "simulated", EN)
    page.locator("#graph-toggle").click()
    page.wait_for_function("window.__s17GraphPending.length === 1")
    page.locator("#graph-toggle").click()
    page.locator("#graph-toggle").click()
    assert page.evaluate("window.__s17GraphPending.length") == 1
    page.evaluate("window.__s17GraphPending.shift().release()")
    page.wait_for_function("window.__s17GraphSettled.length === 2")
    page.wait_for_function("window.__s17GraphPending.length === 1")
    page.evaluate("window.__s17GraphPending.shift().release()")
    page.wait_for_function("window.__s17GraphSettled.length === 3")
    page.locator(".graph-visual").wait_for()
    assert page.locator("#graph-toggle").get_attribute("aria-expanded") == "true"
    assert page.locator("#graph-view-select").input_value() == "adjacency"
    page.locator("#graph-view-select").select_option("evidence_to_change")
    page.wait_for_function("window.__s17GraphPending.length === 1")
    next_id = CASES[1].id
    page.locator(f"[data-open-id='{next_id}']").click()
    page.wait_for_function(
        "id => document.querySelector('#graph-view')?.dataset.graphOpportunity === id",
        arg=next_id,
    )
    page.evaluate("window.__s17GraphPending.shift().release()")
    page.wait_for_function("window.__s17GraphSettled.length === 4")
    page.evaluate(
        "() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
    )
    assert page.locator("#graph-view").get_attribute("data-graph-opportunity") == next_id
    assert page.locator("#graph-toggle").get_attribute("aria-expanded") == "false"
    assert page.locator("#graph-panel[hidden]").count() == 1


@pytest.mark.parametrize(
    ("locale", "viewport"),
    [(locale, viewport) for locale in (EN, AR) for viewport in (DESKTOP, TABLET)],
    ids=[
        f"{locale.code}-{viewport.name}"
        for locale in (EN, AR)
        for viewport in (DESKTOP, TABLET)
    ],
)
def test_graph_keyboard_accessibility_rtl(
    browser_session: BrowserSession,
    locale: Any,
    viewport: Any,
) -> None:
    page = browser_session.page
    page.set_viewport_size(viewport.as_dict())
    install_graph_routes(page)
    goto_portfolio(page, "public", locale)
    toggle = page.locator("#graph-toggle")
    toggle.focus()
    page.keyboard.press("Enter")
    wait_graph_request_complete(page, "adjacency")
    assert page.evaluate("document.activeElement.id") == "graph-toggle"
    catalogue = graph_catalogue_fixture()["views"][0]
    assert page.locator("#graph-svg-title").text_content() == (
        catalogue["label"][locale.code]
    )
    assert page.locator("#graph-svg-description").text_content() == (
        catalogue["description"][locale.code]
    )
    report = run_axe(page)
    assert not report["violations"], format_axe_violations(report["violations"])
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.id") == "graph-view-select"
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.id") == "graph-scroll-region"
    scroll_region = page.locator("#graph-scroll-region")
    page.locator(".graph-svg-node").first.click()
    page.wait_for_function("document.activeElement.id === 'graph-scroll-region'")
    overflow = scroll_region.evaluate("node => node.scrollWidth > node.clientWidth")
    if overflow:
        before = scroll_region.evaluate("node => node.scrollLeft")
        page.keyboard.press("ArrowLeft" if locale.code == "ar" else "ArrowRight")
        page.wait_for_function(
            "before => document.querySelector('#graph-scroll-region').scrollLeft !== before",
            arg=before,
        )
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.dataset.graphSelect") == "node"
    first_node = page.evaluate("document.activeElement.dataset.graphId")
    page.keyboard.press("Space")
    assert page.evaluate("document.activeElement.dataset.graphId") == first_node
    assert page.evaluate("document.activeElement.getAttribute('aria-pressed')") == "true"
    node_count = page.locator(
        ".graph-button-list [data-graph-select='node']"
    ).count()
    for _ in range(node_count):
        page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.dataset.graphSelect") == "edge"
    first_edge = page.evaluate("document.activeElement.dataset.graphId")
    page.keyboard.press("Space")
    assert page.evaluate("document.activeElement.dataset.graphId") == first_edge
    assert page.evaluate("document.activeElement.getAttribute('aria-pressed')") == "true"
    for _ in range(node_count + 3):
        page.keyboard.press("Shift+Tab")
    assert page.evaluate("document.activeElement.id") == "graph-toggle"
    page.keyboard.press("Enter")
    assert page.evaluate("document.activeElement.id") == "graph-toggle"
    assert page.locator("#graph-panel[hidden]").count() == 1
    select_mode(page, "simulated", locale)
    open_graph(page)
    graph_text = page.locator("#graph-view").inner_text()
    for warning in synthetic_display_labels().values():
        assert warning in graph_text
    synthetic_nodes = page.locator(".graph-svg-node.is-synthetic").count()
    assert 0 < synthetic_nodes < page.locator(".graph-svg-node").count()
    select_graph_view(page, "route_blocking")
    report = run_axe(page)
    assert not report["violations"], format_axe_violations(report["violations"])
    assert page.locator("html").get_attribute("dir") == locale.direction


def test_graph_untrusted_content_and_public_isolation(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    invalid_public = route_blocking_fixture("SAU-H0-721049")
    invalid_public["view_id"] = "adjacency"
    invalid_public["mode"] = "public"
    install_graph_routes(
        page,
        lambda view, opportunity, mode: invalid_public
        if view == "adjacency" and mode == "public" else None,
    )
    goto_portfolio(page, "public", EN)
    open_graph(page)
    assert page.locator(".graph-state-error").count() == 1
    assert locale_bundle(EN)["strings"]["graph.invalid_title"] in (
        page.locator(".graph-state-error").inner_text()
    )
    assert page.locator(".graph-visual").count() == 0
    page.unroute("**/api/graph/**")
    malicious = route_blocking_fixture("SAU-H0-721049")
    synthetic = next(
        node for node in malicious["nodes"]
        if node["provenance"]["synthetic_flag"]
    )
    synthetic["name_en"] = "<img src=x onerror=window.__graphPwned=1>"
    synthetic["properties"]["source_url"] = "javascript:alert(1)"
    install_graph_routes(
        page,
        lambda view, opportunity, mode: malicious
        if view == "route_blocking" and mode == "simulated" else None,
    )
    goto_portfolio(page, "simulated", EN)
    open_graph(page)
    select_graph_view(page, "route_blocking")
    assert page.locator("#graph-view img").count() == 0
    assert page.evaluate("window.__graphPwned || 0") == 0
    assert "javascript:" not in page.locator("#graph-view").inner_html()
    for warning in synthetic_display_labels().values():
        assert warning in page.locator("#graph-view").inner_text()


@pytest.mark.parametrize(
    ("locale", "viewport"),
    [(locale, viewport) for locale in (EN, AR) for viewport in (DESKTOP, TABLET)],
    ids=[
        f"{locale.code}-{viewport.name}"
        for locale in (EN, AR)
        for viewport in (DESKTOP, TABLET)
    ],
)
def test_graph_visual_budget_preflight(
    browser_session: BrowserSession,
    graph_visual_preflight_root: Path,
    locale: Any,
    viewport: Any,
) -> None:
    from io import BytesIO
    from PIL import Image
    from browser_tests.visual_baselines import write_lossless_webp

    page = browser_session.page
    page.set_viewport_size(viewport.as_dict())
    install_graph_routes(page)
    foil = next(case for case in CASES if case.id == "SAU-H6-760711")
    states = (
        (CASES[0], "public", "adjacency", "journey-i-graph-adjacency"),
        (
            CASES[0],
            "simulated",
            "route_blocking",
            "journey-i-graph-route-blocking",
        ),
        (
            foil,
            "simulated",
            "shared_enabler",
            "journey-i-graph-shared-enabler",
        ),
        (
            CASES[0],
            "public",
            "evidence_to_change",
            "journey-i-graph-evidence-to-change",
        ),
    )
    intersection_failures = []
    for case, mode, view_id, screen in states:
        goto_portfolio(page, mode, locale)
        select_case(page, case, mode, locale)
        prepare_graph_capture(page, view_id)
        assert_graph_svg_labels_within_viewbox(page)
        assert_graph_visible_arrow_endpoints(page)
        try:
            assert_graph_caption_edge_clearance(page)
        except AssertionError as error:
            intersection_failures.append({
                "view_id": view_id,
                "error": str(error),
            })
        label = page.locator(".graph-svg-node text").first
        previous_transform = label.get_attribute("transform")
        label.evaluate(
            "(node) => node.setAttribute('transform', 'translate(2000 0)')"
        )
        try:
            with pytest.raises(AssertionError):
                assert_graph_svg_labels_within_viewbox(page)
        finally:
            label.evaluate(
                """(node, previous) => {
                  if (previous === null) node.removeAttribute('transform');
                  else node.setAttribute('transform', previous);
                }""",
                previous_transform,
            )
        assert_graph_svg_labels_within_viewbox(page)
        png = page.screenshot(type="png", full_page=False)
        with Image.open(BytesIO(png)) as image:
            assert image.size == (viewport.width, viewport.height)
            path = (
                graph_visual_preflight_root
                / locale.code
                / viewport.name
                / f"{screen}.webp"
            )
            write_lossless_webp(image, path)
        assert path.stat().st_size <= 600 * 1024
    assert intersection_failures == []


def test_graph_portfolio_out_of_order_does_not_restore_stale_selection(
    browser_session: BrowserSession,
) -> None:
    page = browser_session.page
    install_graph_routes(page)
    goto_portfolio(page, "public", EN)
    current = page.locator("#opportunity-select").input_value()
    page.evaluate(
        """() => {
          const original = window.fetch;
          window.__s17PortfolioPending = [];
          window.__s17PortfolioSettled = 0;
          window.fetch = (input, init) => {
            if (String(input).includes('/api/opportunities?mode=simulated')) {
              return new Promise((resolve, reject) => {
                window.__s17PortfolioPending.push(() => {
                  original.call(window, input, init).then(
                    response => {
                      window.__s17PortfolioSettled += 1;
                      resolve(response);
                    },
                    error => {
                      window.__s17PortfolioSettled += 1;
                      reject(error);
                    },
                  );
                });
              });
            }
            return original.call(window, input, init);
          };
        }"""
    )
    page.locator(".mode-button[data-mode='simulated']").click()
    page.wait_for_function("window.__s17PortfolioPending.length === 1")
    page.locator(".mode-button[data-mode='public']").click()
    assert "active" in (
        page.locator(".mode-button[data-mode='simulated']").get_attribute("class")
        or ""
    )
    page.evaluate("window.__s17PortfolioPending.shift()()")
    page.wait_for_function("window.__s17PortfolioSettled === 1")
    page.wait_for_function(
        "document.querySelector(\".mode-button[data-mode='public']\")"
        ".classList.contains('active')"
    )
    select_mode(page, "public", EN)
    assert page.locator("#opportunity-select").input_value() == current
    assert page.locator(".mode-button[data-mode='public']").get_attribute("class").endswith("active")
    assert page.locator("#graph-toggle").get_attribute("aria-expanded") == "false"
