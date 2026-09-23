from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from browser_tests.graph_fixtures import (
    artifact_graph_payload,
    graph_catalogue_fixture,
    route_blocking_fixture,
)


GraphOverride = Callable[[str, str, str], dict[str, Any] | None]


def install_graph_routes(page: Any, override: GraphOverride | None = None) -> list[str]:
    requests: list[str] = []

    def handle(route: Any) -> None:
        url = urlsplit(route.request.url)
        requests.append(url.path + (f"?{url.query}" if url.query else ""))
        if url.path == "/api/graph/catalogue":
            payload = graph_catalogue_fixture()
        else:
            parts = url.path.split("/")
            if len(parts) != 7 or parts[1:4] != ["api", "graph", "opportunities"] or parts[5] != "views":
                route.fulfill(status=404, body="{}", content_type="application/json")
                return
            opportunity_id = unquote(parts[4])
            view_id = unquote(parts[6])
            mode = parse_qs(url.query).get("mode", ["public"])[0]
            payload = override(view_id, opportunity_id, mode) if override else None
            if payload is None:
                payload = (
                    route_blocking_fixture(opportunity_id)
                    if view_id == "route_blocking" and mode == "simulated"
                    else artifact_graph_payload(view_id, opportunity_id, mode)
                )
        route.fulfill(
            status=200,
            body=json.dumps(payload, ensure_ascii=False),
            content_type="application/json",
        )

    page.route("**/api/graph/**", handle)
    return requests


def wait_graph_request_complete(page: Any, view_id: str) -> None:
    page.wait_for_function(
        """viewId => {
          const toggle = document.querySelector('#graph-toggle');
          const select = document.querySelector('#graph-view-select');
          return toggle?.getAttribute('aria-expanded') === 'true'
            && select?.value === viewId
            && select.disabled === false
            && !document.querySelector('.graph-state-loading');
        }""",
        arg=view_id,
    )
    page.locator(".graph-state:not(.graph-state-loading), .graph-visual").wait_for()


def open_graph(page: Any) -> None:
    page.locator("#graph-toggle").click()
    page.locator("#graph-panel:not([hidden])").wait_for()
    wait_graph_request_complete(page, "adjacency")


def select_graph_view(page: Any, view_id: str) -> None:
    page.locator("#graph-view-select").select_option(view_id)
    wait_graph_request_complete(page, view_id)


def select_graph_element(page: Any, kind: str, index: int = 0) -> None:
    page.locator(
        f".graph-button-list [data-graph-select='{kind}']"
    ).nth(index).click()
    page.locator(".graph-details").wait_for()


def select_svg_graph_element(page: Any, kind: str, index: int = 0) -> None:
    element = page.locator(
        f".graph-diagram [data-graph-select='{kind}']"
    ).nth(index)
    element.click()
    page.locator(".graph-details").wait_for()
    assert "is-selected" in (element.get_attribute("class") or "")


def select_native_graph_element(
    page: Any,
    kind: str,
    key: str,
    index: int = 0,
) -> None:
    element = page.locator(
        f".graph-button-list [data-graph-select='{kind}']"
    ).nth(index)
    element.focus()
    page.keyboard.press(key)
    page.locator(".graph-details").wait_for()
    assert element.get_attribute("aria-pressed") == "true"


GRAPH_NODE_RADIUS = 30
GRAPH_MARKER_CLEARANCE = 8
GRAPH_CAPTION_EDGE_CLEARANCE = 6


def assert_graph_svg_labels_within_viewbox(page: Any) -> None:
    result = page.evaluate(
        """() => {
          const svg = document.querySelector('.graph-diagram');
          if (!svg) return { ok: false, reason: 'missing diagram' };
          const vb = svg.viewBox.baseVal;
          const svgMatrix = svg.getCTM();
          if (!svgMatrix) {
            return { ok: false, reason: 'missing SVG transformation matrix' };
          }
          const inverseSvgMatrix = svgMatrix.inverse();
          const checks = [...svg.querySelectorAll('.graph-svg-node text')].map((text) => {
            const box = text.getBBox();
            const matrix = text.getCTM();
            if (!matrix) {
              return {
                id: text.closest('[data-graph-id]')?.dataset.graphId || '',
                inside: false,
                reason: 'missing transformation matrix',
              };
            }
            const corners = [
              [box.x, box.y],
              [box.x + box.width, box.y],
              [box.x, box.y + box.height],
              [box.x + box.width, box.y + box.height],
            ].map(([x, y]) => (
              new DOMPoint(x, y)
                .matrixTransform(matrix)
                .matrixTransform(inverseSvgMatrix)
            ));
            const xs = corners.map((point) => point.x);
            const ys = corners.map((point) => point.y);
            const bounds = {
              left: Math.min(...xs),
              right: Math.max(...xs),
              top: Math.min(...ys),
              bottom: Math.max(...ys),
            };
            return {
              id: text.closest('[data-graph-id]')?.dataset.graphId || '',
              inside:
                bounds.left >= vb.x
                && bounds.top >= vb.y
                && bounds.right <= vb.x + vb.width
                && bounds.bottom <= vb.y + vb.height,
              bounds,
            };
          });
          return { ok: checks.every((row) => row.inside), checks };
        }"""
    )
    assert result["ok"], result


def assert_graph_visible_arrow_endpoints(page: Any) -> None:
    result = page.evaluate(
        f"""() => {{
          const svg = document.querySelector('.graph-diagram');
          if (!svg) return {{ ok: false, reason: 'missing diagram' }};
          const radius = {GRAPH_NODE_RADIUS};
          const marker = {GRAPH_MARKER_CLEARANCE};
          const centers = [...svg.querySelectorAll('.graph-svg-node')].map((node) => {{
            const match = /translate\\(([^ ]+) ([^)]+)\\)/.exec(node.getAttribute('transform') || '');
            return {{
              x: Number(match?.[1]),
              y: Number(match?.[2]),
            }};
          }});
          const checks = [...svg.querySelectorAll('.graph-svg-edge line')].map((line) => {{
            const x1 = line.x1.baseVal.value;
            const y1 = line.y1.baseVal.value;
            const x2 = line.x2.baseVal.value;
            const y2 = line.y2.baseVal.value;
            const segment = Math.hypot(x2 - x1, y2 - y1);
            if (segment === 0) {{
              return {{ trimmed: true, segment }};
            }}
            const nearest = centers.reduce((best, center) => {{
              const distance = Math.hypot(center.x - x2, center.y - y2);
              return distance < best.distance ? {{ distance, center }} : best;
            }}, {{ distance: Number.POSITIVE_INFINITY, center: null }});
            const minDistance = radius + marker * 0.5;
            return {{
              x2,
              y2,
              nearestDistance: nearest.distance,
              trimmed: nearest.distance >= minDistance,
            }};
          }});
          return {{
            ok: checks.length > 0 && checks.every((row) => row.trimmed),
            checks,
          }};
        }}"""
    )
    assert result["ok"], result


def assert_graph_caption_edge_clearance(page: Any) -> None:
    result = page.evaluate(
        f"""() => {{
          const svg = document.querySelector('.graph-diagram');
          if (!svg) return {{ ok: false, reason: 'missing diagram' }};
          const svgMatrix = svg.getCTM();
          if (!svgMatrix) {{
            return {{ ok: false, reason: 'missing SVG transformation matrix' }};
          }}
          const inverseSvgMatrix = svgMatrix.inverse();
          const clearance = {GRAPH_CAPTION_EDGE_CLEARANCE};
          const intersectsSegment = (bounds, line, padding) => {{
            const left = bounds.left - padding;
            const right = bounds.right + padding;
            const top = bounds.top - padding;
            const bottom = bounds.bottom + padding;
            const dx = line.x2 - line.x1;
            const dy = line.y2 - line.y1;
            let entry = 0;
            let exit = 1;
            for (const [p, q] of [
              [-dx, line.x1 - left],
              [dx, right - line.x1],
              [-dy, line.y1 - top],
              [dy, bottom - line.y1],
            ]) {{
              if (p === 0 && q < 0) return false;
              if (p === 0) continue;
              const ratio = q / p;
              if (p < 0) entry = Math.max(entry, ratio);
              else exit = Math.min(exit, ratio);
              if (entry > exit) return false;
            }}
            return true;
          }};
          const captions = [...svg.querySelectorAll('.graph-svg-node text')].map((text) => {{
            const box = text.getBBox();
            const matrix = text.getCTM();
            if (!matrix) return null;
            const corners = [
              [box.x, box.y],
              [box.x + box.width, box.y],
              [box.x, box.y + box.height],
              [box.x + box.width, box.y + box.height],
            ].map(([x, y]) => (
              new DOMPoint(x, y)
                .matrixTransform(matrix)
                .matrixTransform(inverseSvgMatrix)
            ));
            return {{
              id: text.closest('[data-graph-id]')?.dataset.graphId || '',
              left: Math.min(...corners.map((point) => point.x)),
              right: Math.max(...corners.map((point) => point.x)),
              top: Math.min(...corners.map((point) => point.y)),
              bottom: Math.max(...corners.map((point) => point.y)),
            }};
          }});
          const lines = [...svg.querySelectorAll('.graph-svg-edge line')].map((line) => {{
            const strokeWidth = Number.parseFloat(
              getComputedStyle(line).strokeWidth
            ) || 0;
            const marker = svg.querySelector('#graph-arrow');
            const markerRadius = marker
              ? Math.max(
                  marker.markerWidth.baseVal.value,
                  marker.markerHeight.baseVal.value,
                ) * strokeWidth / 2
              : 0;
            return {{
              id: line.closest('[data-graph-id]')?.dataset.graphId || '',
              x1: line.x1.baseVal.value,
              y1: line.y1.baseVal.value,
              x2: line.x2.baseVal.value,
              y2: line.y2.baseVal.value,
              strokeWidth,
              markerRadius,
            }};
          }});
          const collisions = [];
          for (const caption of captions) {{
            if (!caption) {{
              collisions.push({{ reason: 'missing caption transformation' }});
              continue;
            }}
            for (const line of lines) {{
              const lineHit = intersectsSegment(
                caption,
                line,
                clearance + line.strokeWidth / 2,
              );
              const nearestX = Math.max(
                caption.left,
                Math.min(line.x2, caption.right),
              );
              const nearestY = Math.max(
                caption.top,
                Math.min(line.y2, caption.bottom),
              );
              const markerHit = Math.hypot(
                line.x2 - nearestX,
                line.y2 - nearestY,
              ) <= line.markerRadius + clearance;
              if (lineHit || markerHit) {{
                collisions.push({{
                  caption: caption.id,
                  edge: line.id,
                  lineHit,
                  markerHit,
                }});
              }}
            }}
          }}
          return {{ ok: collisions.length === 0, clearance, collisions }};
        }}"""
    )
    assert result["ok"], result


def prepare_graph_capture(page: Any, view_id: str) -> None:
    if page.locator("#graph-panel[hidden]").count():
        open_graph(page)
    select_graph_view(page, view_id)
    page.locator("#graph-view").evaluate(
        "(node) => node.scrollIntoView({block: 'start', behavior: 'auto'})"
    )
