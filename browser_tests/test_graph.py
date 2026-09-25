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
    assert_graph_panel_contains_controls_and_text,
    assert_graph_source_name_disclosures,
    assert_selected_graph_passports,
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
    assert len(retained) == 112
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
        + (" " + locale_bundle(locale)["strings"]["source_language.caption"] if locale.code == "ar" else "")
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


@pytest.mark.parametrize("locale", (EN, AR), ids=lambda value: value.code)
@pytest.mark.parametrize("width", (390, 1024, 1440))
def test_graph_node_names_preserve_sources_and_arabic(browser_session: BrowserSession, locale: Any, width: int) -> None:
    page = browser_session.page
    page.set_viewport_size({"width": width, "height": 900})
    install_graph_routes(page)
    goto_portfolio(page, "public", locale)
    open_graph(page)
    assert_graph_source_name_disclosures(page, locale)
    payload = artifact_graph_payload("adjacency", "SAU-H0-721049", "public")
    assert page.locator('.graph-button-list [data-graph-select="node"]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.graphId)') == [node['id'] for node in payload['nodes']]
    for identity in ('COMPANY-280abef66af82a6c', 'COMPANY-a0954792195adee5'):
        button = page.locator(f'.graph-button-list [data-graph-id="{identity}"]')
        button.focus(); page.keyboard.press('Enter')
        page.locator('.graph-passport, .graph-unresolved').first.wait_for()
        assert button.get_attribute('aria-pressed') == 'true'
        assert page.locator('.graph-provenance').inner_text().find(next(n['provenance']['evidence_id'] for n in payload['nodes'] if n['id']==identity)) >= 0
    page.locator('.graph-button-list [data-graph-id="SAU-H0-721049"]').click()
    page.locator('.graph-passport').first.wait_for()
    if locale.code == 'ar':
        link = page.locator('.graph-evidence-results [data-passport-ref]').first
        assert link.evaluate("a=>{const c=a.nextElementSibling;return c?.classList.contains('source-language-caption') && c.id===a.getAttribute('aria-describedby') && c.checkVisibility()}")
        assert link.locator('.source-language-caption').count() == 0



def test_graph_source_disclosure_mutations_fail_strict_oracles(browser_session: BrowserSession) -> None:
    from browser_tests.pages import arabic_parity_report, assert_arabic_parity
    page = browser_session.page
    page.set_viewport_size({"width":390,"height":844})
    install_graph_routes(page); goto_portfolio(page,'public',AR); open_graph(page)
    assert_graph_source_name_disclosures(page,AR)
    mutations = (
        "document.querySelector('.graph-svg-node .source-language-island').removeAttribute('dir')",
        "document.querySelector('.graph-svg-node .source-language-island').classList.remove('source-language-island')",
        "document.querySelector('.graph-svg-node .source-language-caption').remove()",
        "document.querySelector('.graph-node-name .source-language-caption').style.display='none'",
        "document.querySelector('.graph-button-list [aria-describedby]').removeAttribute('aria-describedby')",
    )
    original = page.locator('#graph-view').inner_html()
    for index, mutation in enumerate(mutations):
        page.evaluate(mutation)
        with pytest.raises(AssertionError):
            if index < 3:
                assert_arabic_parity(arabic_parity_report(page,'#graph-view'),expected_source_spans=6)
            else:
                assert_graph_source_name_disclosures(page,AR)
        page.locator('#graph-view').evaluate('(node,html)=>node.innerHTML=html',original)
        assert_graph_source_name_disclosures(page,AR)
    # AM4: actual stored passports, with independently enumerated literal counts.
    page.locator('.graph-button-list [data-graph-id="SAU-H0-721049"]').click()
    page.locator('.graph-passport').first.wait_for()
    key = 'SAU-H0-721049|public|adjacency|node'
    assert_selected_graph_passports(page, AR, 'public', key)
    original = page.locator('#graph-view').inner_html()
    passport_mutations = (
        "document.querySelector('.graph-passport h5 .source-language-island').classList.remove('source-language-island')",
        "document.querySelector('[data-passport-ref]').nextElementSibling.remove()",
        "document.querySelector('[data-passport-value=\"status\"]').textContent='observed'",
        "document.querySelector('[data-passport-value=\"source\"]').innerHTML='<bdi class=\"technical-token\" dir=\"ltr\">Hadeed</bdi>'",
        "document.querySelector('.graph-passport a').setAttribute('href','javascript:alert(1)')",
    )
    for mutation in passport_mutations:
        page.evaluate(mutation)
        with pytest.raises(AssertionError):
            assert_selected_graph_passports(page, AR, 'public', key)
        page.locator('#graph-view').evaluate('(node,html)=>node.innerHTML=html', original)
        assert_selected_graph_passports(page, AR, 'public', key)
    goto_portfolio(page, 'simulated', AR)
    select_case(page, next(case for case in CASES if case.id == 'SAU-H6-760711'), 'simulated', AR)
    open_graph(page); select_graph_view(page, 'shared_enabler')
    edge = artifact_graph_payload('shared_enabler', 'SAU-H6-760711', 'simulated')['edges'][0]
    page.locator(f'.graph-button-list [data-graph-id="{edge["id"]}"]').click()
    page.locator('.graph-passport').first.wait_for()
    key = 'SAU-H6-760711|simulated|shared_enabler|edge'
    assert_selected_graph_passports(page, AR, 'simulated', key)
    original = page.locator('#graph-view').inner_html()
    for mutation in (
        "document.querySelector('[data-passport-value=\"evidence_id\"] bdi').dir='rtl'",
        "document.querySelector('.graph-passport .synthetic-labels').remove()",
    ):
        page.evaluate(mutation)
        with pytest.raises(AssertionError):
            assert_selected_graph_passports(page, AR, 'simulated', key)
        page.locator('#graph-view').evaluate('(node,html)=>node.innerHTML=html', original)
        assert_selected_graph_passports(page, AR, 'simulated', key)


@pytest.mark.parametrize("locale", (EN, AR), ids=lambda value: value.code)
@pytest.mark.parametrize("width", (390, 1024, 1440))
@pytest.mark.parametrize("scenario", ('steel','aluminium'))
def test_graph_narrow_panel_contains_controls_and_text(browser_session: BrowserSession, locale: Any, width: int, scenario: str) -> None:
    page=browser_session.page
    page.set_viewport_size({'width':width,'height':900})
    install_graph_routes(page)
    case_id = 'SAU-H0-721049' if scenario == 'steel' else 'SAU-H6-760711'
    for mode in ('public', 'simulated'):
        goto_portfolio(page, mode, locale)
        if scenario == 'aluminium': select_case(page, next(case for case in CASES if case.id == case_id), mode, locale)
        open_graph(page)
        for view in ('adjacency', 'route_blocking', 'shared_enabler', 'evidence_to_change'):
            select_graph_view(page, view)
            payload = route_blocking_fixture(case_id) if view == 'route_blocking' and mode == 'simulated' else artifact_graph_payload(view, case_id, mode)
            assert_graph_panel_contains_controls_and_text(page)
            if scenario == "steel" and mode == "public" and view == "evidence_to_change" and width == 1440:
                page.evaluate("document.fonts.ready")
                new_token, old_token = "ENGINE-6b54371e99f3", "ENGINE-7ae34188bdec"
                measure = """() => {
                  const section = document.querySelector('.graph-native-controls > section:nth-child(2)');
                  const buttons = [...section.querySelectorAll('.graph-button-list > button[data-graph-select="edge"]')];
                  const rect = node => {
                    const box = node.getBoundingClientRect();
                    return Object.fromEntries(['left','right','top','bottom','width','height'].map(key => [key, Number(box[key].toFixed(2))]));
                  };
                  const walker = document.createTreeWalker(section, NodeFilter.SHOW_TEXT), texts = [];
                  while (walker.nextNode()) texts.push(walker.currentNode.nodeValue);
                  return {html: section.innerHTML, texts, rows: buttons.map(button => {
                    const small = button.querySelector(':scope > small');
                    const tokens = [...small.querySelectorAll(':scope > bdi')];
                    const box = rect(small);
                    return {id: button.dataset.graphId, source: tokens[0].textContent,
                      target: tokens[1].textContent, button: rect(button), small: {left: box.left, right: box.right}};
                  })};
                }"""
                before = page.evaluate(measure)
                repeat = page.evaluate(measure)
                assert repeat == before, f"{locale.code}: untouched repeat drift"
                assert len(before["rows"]) == 12
                assert before["rows"][1]["target"] == "INT-SAU-H0-721049-route-5"
                assert before["rows"][2]["target"] == "SAU-H0-721049"
                assert sum(row["source"].count(new_token) for row in before["rows"]) == 5
                assert sum(text.count(new_token) for text in before["texts"]) == 5
                assert all(old_token not in text for text in before["texts"])
                evidence = {"locale": locale.code, "new_token": new_token, "old_token": old_token,
                            "before": before, "repeat": repeat}
                try:
                    changed = page.evaluate("""({from, to}) => {
                      const section = document.querySelector('.graph-native-controls > section:nth-child(2)');
                      const buttons = [...section.querySelectorAll('.graph-button-list > button[data-graph-select="edge"]')];
                      const walker = document.createTreeWalker(section, NodeFilter.SHOW_TEXT), planned = [];
                      let index = -1;
                      while (walker.nextNode()) {
                        index++;
                        const node = walker.currentNode, before = node.nodeValue;
                        if (!before.includes(from)) continue;
                        const row = buttons.findIndex(button => button.contains(node));
                        const source = row < 0 ? null : buttons[row].querySelector(':scope > small > bdi');
                        if (before.split(from).length !== 2 || node.parentElement !== source)
                          throw Error('unexpected engine token location');
                        planned.push({node, row: row + 1, index, before, after: before.replace(from, to)});
                      }
                      if (buttons.length !== 12 || planned.length !== 5)
                        throw Error('expected twelve rows and five source text nodes');
                      window.__graphAnchorOriginalNodes = planned;
                      for (const item of planned) item.node.nodeValue = item.after;
                      return planned.map(({row,index,before,after}) => ({row,index,before,after}));
                    }""", {"from": new_token, "to": old_token})
                    evidence["changed_nodes"] = changed
                    after = page.evaluate(measure)
                    evidence["after"] = after
                    assert len(changed) == 5
                    assert [item["row"] for item in changed] == [1, 2, 3, 4, 5]
                    assert after["texts"] == [text.replace(new_token, old_token) for text in before["texts"]]
                    assert after["html"] == before["html"].replace(new_token, old_token)
                    anchor = "right" if locale.code == "en" else "left"
                    for row_number, (original, rewritten) in enumerate(zip(before["rows"], after["rows"], strict=True), 1):
                        assert rewritten["button"] == original["button"], f"{locale.code}/row/{row_number}/button"
                        assert rewritten["small"][anchor] == original["small"][anchor], (
                            f"{locale.code}/row/{row_number}/small.{anchor}: "
                            f"{original['small'][anchor]} -> {rewritten['small'][anchor]}"
                        )
                finally:
                    page.evaluate("""() => {
                      for (const item of window.__graphAnchorOriginalNodes || []) item.node.nodeValue = item.before;
                      delete window.__graphAnchorOriginalNodes;
                    }""")
                    restored = page.evaluate(measure)
                    evidence["restored"] = restored
                    (browser_session.artifact_dir / f"graph-run-id-anchors-{locale.code}.json").write_text(
                        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                    )
                    assert restored == before, f"{locale.code}: engine token round-trip drift"
            if not payload['edges']:
                assert page.locator('.graph-button-list button').count() == 0
                assert page.locator('.graph-state').inner_text().find(locale_bundle(locale)['strings']['graph.empty_title']) >= 0
                assert_selected_graph_passports(page, locale, mode, f'{case_id}|{mode}|{view}|empty')
                continue
            for kind in ('node', 'edge'):
                element = next((n for n in payload['nodes'] if n['id'] == case_id), payload['nodes'][0]) if kind == 'node' else payload['edges'][0]
                button = page.locator(f'.graph-button-list [data-graph-id="{element["id"]}"]')
                button.focus(); page.keyboard.press('Enter')
                page.locator('.graph-evidence-results').wait_for()
                assert button.get_attribute('aria-pressed') == 'true'
                assert_selected_graph_passports(page, locale, mode, f'{case_id}|{mode}|{view}|{kind}')


@pytest.mark.parametrize("mode", ("public", "simulated"))
@pytest.mark.parametrize("locale", (EN, AR), ids=lambda value: value.code)
def test_graph_scroll_region_reaches_both_keyboard_endpoints(browser_session: BrowserSession, locale: Any, mode: str) -> None:
    page=browser_session.page; page.set_viewport_size({'width':390,'height':844})
    install_graph_routes(page); goto_portfolio(page,mode,locale); open_graph(page)
    strings=locale_bundle(locale)['strings']
    from playwright.sync_api import expect
    for identity, label_key in (('evidence-scroll-region', 'evidence.title'), ('methodology-scroll-region', 'rules.title')):
        table_region = page.locator('#' + identity)
        expect(table_region).to_have_attribute('role', 'region')
        expect(table_region).to_have_attribute('aria-label', strings[label_key])
        page.locator('#opportunity-select').focus()
        for _ in range(55):
            page.keyboard.press('Tab')
            if page.evaluate('document.activeElement.id') == identity:
                break
        assert page.evaluate('document.activeElement.id') == identity
        assert table_region.evaluate("n=>n.matches(':focus-visible') && getComputedStyle(n).outlineStyle !== 'none'")
        extent = table_region.evaluate('n=>n.scrollWidth-n.clientWidth')
        if extent > 0:
            forward = 'ArrowLeft' if locale.code == 'ar' else 'ArrowRight'
            backward = 'ArrowRight' if locale.code == 'ar' else 'ArrowLeft'
            before = table_region.evaluate('n=>n.scrollLeft')
            page.keyboard.press(forward)
            page.wait_for_function("({id,before})=>document.getElementById(id).scrollLeft!==before", arg={'id':identity,'before':before})
            for _ in range(60): page.keyboard.press(forward)
            page.wait_for_function("id=>{const n=document.getElementById(id);return Math.abs(n.scrollLeft)>=n.scrollWidth-n.clientWidth-1}", arg=identity)
            far_endpoint = table_region.evaluate('n=>n.scrollLeft')
            for _ in range(60): page.keyboard.press(backward)
            page.wait_for_function("({id,far,extent})=>Math.abs(document.getElementById(id).scrollLeft-far)>=extent-1", arg={'id':identity,'far':far_endpoint,'extent':extent})
            assert page.evaluate('document.activeElement.id') == identity
        else:
            assert extent == 0
            assert table_region.evaluate('n=>[...n.querySelectorAll("th,td")].every(c=>{const b=c.getBoundingClientRect(),r=n.getBoundingClientRect();return b.left>=r.left-1&&b.right<=r.right+1})')
    region=page.locator('#graph-scroll-region')
    assert region.get_attribute('aria-describedby')=='graph-scroll-hint'
    assert page.locator('#graph-scroll-hint').inner_text()==strings['graph.scroll_hint']
    page.locator('#graph-toggle').focus(); page.keyboard.press('Tab'); page.keyboard.press('Tab')
    assert page.evaluate('document.activeElement.id')=='graph-scroll-region'
    assert region.evaluate('n=>n.scrollWidth>n.clientWidth')
    page_y=page.evaluate('scrollY')
    arrow='ArrowLeft' if locale.code=='ar' else 'ArrowRight'
    opposite='ArrowRight' if locale.code=='ar' else 'ArrowLeft'
    before=region.evaluate('n=>n.scrollLeft'); page.keyboard.press(arrow)
    page.wait_for_function("before=>document.querySelector('#graph-scroll-region').scrollLeft!==before",arg=before)
    for _ in range(40): page.keyboard.press(arrow)
    page.wait_for_function("()=>{const n=document.querySelector('#graph-scroll-region');return Math.abs(n.scrollLeft)>=n.scrollWidth-n.clientWidth-1}")
    for _ in range(40): page.keyboard.press(opposite)
    page.wait_for_function("()=>Math.abs(document.querySelector('#graph-scroll-region').scrollLeft)<1")
    assert page.evaluate('document.activeElement.id')=='graph-scroll-region'
    assert page.evaluate('scrollY')==page_y
    buttons=page.locator('.graph-button-list button').count()
    for _ in range(buttons):
        page.keyboard.press('Tab'); identity=page.evaluate('document.activeElement.dataset.graphId')
        assert identity
        page.keyboard.press('Enter')
        page.locator('.graph-passport, .graph-unresolved').first.wait_for()
        assert page.evaluate('document.activeElement.dataset.graphId')==identity
        assert page.evaluate("document.activeElement.getAttribute('aria-pressed')")=='true'
    report=run_axe(page)
    assert not report['violations'],format_axe_violations(report['violations'])


@pytest.mark.parametrize("locale", (EN, AR), ids=lambda value: value.code)
def test_graph_all_view_states_fit_narrow_panel(new_context: Any, app_server: Any, locale: Any) -> None:
    context=new_context(base_url=app_server.base_url,locale=locale.bcp47,viewport={'width':390,'height':844})
    collector=BrowserFailureCollector(app_server.base_url); collector.attach_context(context)
    page=context.new_page(); collector.attach_page(page)
    install_graph_routes(page)
    for mode in ('public','simulated'):
        goto_portfolio(page,mode,locale); open_graph(page)
        for view in ('adjacency','route_blocking','shared_enabler','evidence_to_change'):
            select_graph_view(page,view)
            for state_name in ('loading','empty','unavailable','invalid','error','retry'):
                page.evaluate("""stateName=>{
                  const original=window.fetch; window.__am2OriginalFetch=original;
                  window.fetch=(input,init)=>String(input).includes('/api/graph/opportunities/') ? new Promise(resolve=>{
                    window.__am2Release=async()=>{const originalResponse=await original(input,init);const payload=await originalResponse.json();
                      if(stateName==='empty'){payload.nodes=[];payload.edges=[];payload.drilldown=[];}
                      if(stateName==='unavailable'){payload.graph_status='GRAPH_UNAVAILABLE';payload.reason_code='CONNECTION_FAILED';payload.nodes=[];payload.edges=[];}
                      if(stateName==='invalid')payload.nodes=[{}];
                      resolve(new Response(JSON.stringify(payload),{status:stateName==='error'?503:200,headers:{'Content-Type':'application/json'}}));
                    };
                  }) : original(input,init);
                }""",state_name)
                page.locator('#graph-view-select').select_option(view)
                page.locator('.graph-state-loading').wait_for()
                assert_graph_panel_contains_controls_and_text(page)
                page.evaluate('window.__am2Release()'); wait_graph_request_complete(page,view)
                page.evaluate('window.fetch=window.__am2OriginalFetch')
                if state_name in ('empty','unavailable','invalid','error'):
                    assert page.locator('.graph-svg-node,.graph-native-controls').count()==0
                    assert page.locator('#graph-scroll-hint').count()==0
                    assert page.locator('.graph-state').count()==1
                assert_graph_panel_contains_controls_and_text(page)
                if page.locator('[data-graph-retry]').count():
                    page.locator('[data-graph-retry]').click(); wait_graph_request_complete(page,view)
                    assert_graph_panel_contains_controls_and_text(page)
    context.close(); collector.assert_clean()


@pytest.mark.parametrize("locale", (EN, AR), ids=lambda value: value.code)
def test_graph_hostile_name_text_is_escaped(browser_session: BrowserSession, locale: Any) -> None:
    page=browser_session.page
    hostile='<img src=x onerror="window.__am2Attack=true"> & \"quoted\"'
    def override(view: str, opportunity: str, mode: str) -> dict:
        payload=artifact_graph_payload(view,opportunity,mode)
        for node in payload['nodes']:
            if node['id']=='COMPANY-280abef66af82a6c':
                node['name_en']=hostile; node['name_ar']='UNAVAILABLE'
            if node['id']=='SAU-H0-721049': node['name_ar']='منتج '+hostile
        return payload
    install_graph_routes(page,override); goto_portfolio(page,'public',locale); open_graph(page)
    assert page.locator('#graph-view img, #graph-view script, #graph-view [onerror]').count()==0
    assert page.evaluate('window.__am2Attack') is None
    assert page.locator('.graph-button-list [data-graph-id="COMPANY-280abef66af82a6c"] .graph-node-name').text_content().startswith(hostile)
    assert page.locator('.graph-svg-node[data-graph-id="COMPANY-280abef66af82a6c"] title').text_content()==hostile
    if locale.code=='ar': assert page.locator('.graph-svg-node[data-graph-id="SAU-H0-721049"] title').text_content()=='منتج '+hostile
