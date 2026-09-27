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
    if kind == 'edge' and element.locator(':scope > path.graph-svg-edge-hit').count():
        click_visible_graph_edge(page, element.get_attribute('data-graph-id'))
    else:
        element.click()
    page.locator(".graph-details").wait_for()
    assert "is-selected" in (element.get_attribute("class") or "")


def click_visible_graph_edge(page: Any, edge_id: str) -> None:
    """Use a real pointer at an unobscured point on this exact visible route."""
    edge = page.locator(f'.graph-svg-edge[data-graph-id="{edge_id}"]')
    edge.scroll_into_view_if_needed()
    point = page.evaluate("""identity => {
      const edge = [...document.querySelectorAll('.graph-svg-edge')]
        .find(node => node.dataset.graphId === identity);
      const path = edge?.querySelector(':scope > path.graph-svg-edge-hit');
      if (!path) return null;
      const scroll = edge.closest('.graph-visual');
      for (const fraction of [0.5, 0.45, 0.55, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8]) {
        const matrix = path.getScreenCTM();
        if (!matrix) return null;
        let position = path.getPointAtLength(path.getTotalLength() * fraction)
          .matrixTransform(matrix);
        if (scroll) {
          const bounds = scroll.getBoundingClientRect();
          scroll.scrollLeft += position.x - (bounds.left + bounds.right) / 2;
          position = path.getPointAtLength(path.getTotalLength() * fraction)
            .matrixTransform(path.getScreenCTM());
        }
        const top = document.elementFromPoint(position.x, position.y);
        if (top?.closest('.graph-svg-edge')?.dataset.graphId === identity) {
          return {x: position.x, y: position.y, fraction};
        }
      }
      return null;
    }""", edge_id)
    assert point is not None, f'no unobscured pointer target for {edge_id}'
    page.mouse.click(point['x'], point['y'])
    assert 'is-selected' in (edge.get_attribute('class') or ''), (edge_id, point)
    assert page.locator(f'.graph-button-list [data-graph-id="{edge_id}"]').get_attribute('aria-pressed') == 'true'


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
          const centers = new Map([...svg.querySelectorAll('.graph-svg-node')].map((node) => {{
            const match = /translate\\(([^ ]+) ([^)]+)\\)/.exec(node.getAttribute('transform') || '');
            return [node.dataset.graphId, {{
              x: Number(match?.[1]),
              y: Number(match?.[2]),
            }}];
          }}));
          const vb = svg.viewBox.baseVal;
          const edges = [...svg.querySelectorAll('.graph-svg-edge')];
          const nativeIds = [...document.querySelectorAll('.graph-button-list [data-graph-select="edge"]')]
            .map(node => node.dataset.graphId).sort();
          const checks = edges.map(edge => {{
            const source = centers.get(edge.dataset.graphSource);
            const target = centers.get(edge.dataset.graphTarget);
            const lines = [...edge.querySelectorAll(':scope > line')];
            const segments = lines.map(line => ({{
              x1: line.x1.baseVal.value, y1: line.y1.baseVal.value,
              x2: line.x2.baseVal.value, y2: line.y2.baseVal.value,
              arrow: line.getAttribute('marker-end') === 'url(#graph-arrow)',
            }}));
            const first = segments[0], last = segments.at(-1);
            const finiteInside = segments.every(segment =>
              [segment.x1, segment.y1, segment.x2, segment.y2].every(Number.isFinite)
              && [segment.x1, segment.x2].every(x => x >= vb.x && x <= vb.x + vb.width)
              && [segment.y1, segment.y2].every(y => y >= vb.y && y <= vb.y + vb.height));
            const connected = segments.slice(1).every((segment, index) =>
              segment.x1 === segments[index].x2 && segment.y1 === segments[index].y2);
            const sourceTrim = source && first && Math.abs(
              Math.hypot(first.x1 - source.x, first.y1 - source.y) - radius
            ) < 0.01;
            const targetTrim = target && last && Math.abs(
              Math.hypot(last.x2 - target.x, last.y2 - target.y) - radius - marker
            ) < 0.01;
            return {{id: edge.dataset.graphId, segmentCount: segments.length,
              finiteInside, connected, sourceTrim, targetTrim,
              oneTerminalArrow: segments.filter(segment => segment.arrow).length === 1 && last?.arrow,
              matchedHit: edge.querySelector(':scope > path.graph-svg-edge-hit, :scope > polygon.graph-svg-edge-hit') !== null}};
          }});
          return {{
            ok: checks.length > 0 && checks.reduce((sum, row) => sum + row.segmentCount, 0) >= checks.length
              && JSON.stringify(checks.map(row => row.id).sort()) === JSON.stringify(nativeIds)
              && checks.every(row => row.segmentCount > 0 && row.finiteInside && row.connected
                && row.sourceTrim && row.targetTrim && row.oneTerminalArrow && row.matchedHit),
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
            const markerRadius = marker && line.getAttribute('marker-end') === 'url(#graph-arrow)'
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


def assert_graph_panel_contains_controls_and_text(page: Any) -> dict:
    from browser_tests.harness import AR, EN
    from browser_tests.pages import locale_bundle

    language = (page.locator("html").get_attribute("lang") or "")[:2]
    assert language in ("en", "ar"), language
    details_name = locale_bundle(AR if language == "ar" else EN)["strings"]["graph.details_title"]
    page.evaluate("document.fonts.ready")
    result = page.evaluate("""expectedName => {
      const panel=document.querySelector('#graph-panel');
      const inner=node=>{const b=node.getBoundingClientRect(),s=getComputedStyle(node);return {left:b.left+parseFloat(s.paddingLeft),right:b.right-parseFloat(s.paddingRight)}};
      const bounds=inner(panel),panelBox=panel.getBoundingClientRect(),outside=[],text=[],structure=[],scoped=[];
      const tables=[...document.querySelectorAll('.graph-source-table')];
      const wrappers=[...panel.querySelectorAll('.graph-details > .card-body-scroll')];
      const recognized=new Map();
      if(wrappers.length!==tables.length) structure.push({kind:'source-table count',wrappers:wrappers.length,tables:tables.length});
      for(const wrapper of wrappers) {
        const direct=[...wrapper.children].filter(child=>child.matches('table.graph-source-table'));
        if(wrapper.children.length!==1 || direct.length!==1) {
          structure.push({kind:'direct source-table structure',children:wrapper.children.length,direct:direct.length});
          continue;
        }
        const table=direct[0],box=wrapper.getBoundingClientRect(),style=getComputedStyle(wrapper);
        if(wrapper.getAttribute('role')!=='region') structure.push({kind:'role',value:wrapper.getAttribute('role')});
        if(wrapper.getAttribute('tabindex')!=='0') structure.push({kind:'tabindex',value:wrapper.getAttribute('tabindex')});
        if(!expectedName || wrapper.getAttribute('aria-label')!==expectedName)
          structure.push({kind:'governed name',value:wrapper.getAttribute('aria-label'),expectedName});
        if(!['auto','scroll'].includes(style.overflowX)) structure.push({kind:'overflow',value:style.overflowX});
        if(!wrapper.getClientRects().length || box.width<=0 || box.height<=0 ||
           box.left<bounds.left-1 || box.right>bounds.right+1 ||
           box.top<panelBox.top-1 || box.bottom>panelBox.bottom+1)
          structure.push({kind:'wrapper bounds',box:{left:box.left,right:box.right,top:box.top,bottom:box.bottom},bounds});
        const extent=wrapper.scrollWidth-wrapper.clientWidth,scroll=wrapper.scrollLeft;
        const rtl=style.direction==='rtl';
        if(extent<0 || (rtl ? scroll>1 || scroll< -extent-1 : scroll< -1 || scroll>extent+1))
          scoped.push({kind:'scroll range',extent,scroll,rtl});
        const portLeft=box.left+wrapper.clientLeft,portRight=portLeft+wrapper.clientWidth;
        const reachLeft=rtl ? portRight-wrapper.scrollWidth-scroll : portLeft-scroll;
        const reachRight=reachLeft+wrapper.scrollWidth;
        recognized.set(table,{wrapper,reachLeft,reachRight,tableBox:table.getBoundingClientRect()});
      }
      if(recognized.size!==tables.length) structure.push({kind:'recognized source-table count',recognized:recognized.size,tables:tables.length});
      for(const [table,scope] of recognized) {
        for(const node of [table,...table.querySelectorAll('*')]) {
          if(!node.getClientRects().length) continue;
          const box=node.getBoundingClientRect();
          if(box.width && (box.left<scope.reachLeft-1 || box.right>scope.reachRight+1 ||
             box.left<scope.tableBox.left-1 || box.right>scope.tableBox.right+1))
            scoped.push({kind:'reachable table element',tag:node.tagName,left:box.left,right:box.right,
                         reachLeft:scope.reachLeft,reachRight:scope.reachRight});
        }
      }
      for(const node of panel.querySelectorAll('*')) {
        if(node.closest('.graph-visual svg') || !node.getClientRects().length) continue;
        const table=node.closest('table.graph-source-table');
        if(table && recognized.has(table)) continue;
        const box=node.getBoundingClientRect();
        if(box.width && (box.left<bounds.left-1 || box.right>bounds.right+1)) outside.push({kind:'panel bounds',tag:node.tagName,id:node.id,class:node.className,left:box.left,right:box.right,bounds});
      }
      const walker=document.createTreeWalker(panel,NodeFilter.SHOW_TEXT);
      while(walker.nextNode()) {
        const node=walker.currentNode,parent=node.parentElement;
        if(!node.textContent.trim() || parent.closest('svg,select,option') || !parent.getClientRects().length) continue;
        const range=document.createRange();range.selectNodeContents(node);
        const box=inner(parent);
        const table=parent.closest('table.graph-source-table'),scope=recognized.get(table);
        for(const rect of range.getClientRects()) {
          if(!rect.width) continue;
          if(scope) {
            if(rect.left<scope.reachLeft-1 || rect.right>scope.reachRight+1 ||
               rect.left<scope.tableBox.left-1 || rect.right>scope.tableBox.right+1 ||
               rect.left<box.left-1 || rect.right>box.right+1)
              scoped.push({kind:'reachable table text',value:node.textContent,left:rect.left,right:rect.right,parent:box});
          } else if(rect.left<bounds.left-1 || rect.right>bounds.right+1 || rect.left<box.left-1 || rect.right>box.right+1)
            text.push({kind:'panel text',text:node.textContent,left:rect.left,right:rect.right,parent:box,bounds});
        }
      }
      return {outside,text,structure,scoped,recognized:recognized.size,sourceTables:tables.length,
              documentOverflow:document.documentElement.scrollWidth>innerWidth};
    }""", details_name)
    assert result["structure"] == [], result
    assert result["scoped"] == [], result
    assert result["outside"] == [], result
    assert result["text"] == [], result
    assert result["documentOverflow"] is False, result
    return result


def assert_graph_source_name_disclosures(page: Any, locale: Any) -> None:
    from playwright.sync_api import expect
    from browser_tests.pages import arabic_parity_report, assert_arabic_parity, locale_bundle

    names = {"COMPANY-280abef66af82a6c": "Hadeed", "COMPANY-a0954792195adee5": "Universal Metal Coating Company"}
    strings = locale_bundle(locale)["strings"]
    caption = strings["source_language.caption"]
    for identity, name in names.items():
        native = page.locator(f'.graph-button-list [data-graph-id="{identity}"]')
        svg = page.locator(f'.graph-svg-node[data-graph-id="{identity}"]')
        expect(native).to_have_accessible_name(strings["graph.node_button"].replace("{label}", name))
        expect(svg.locator("title")).to_have_text(name)
        if locale.code == "ar":
            expect(native.locator(".source-language-island")).to_have_text(name)
            expect(native.locator(".source-language-caption")).to_have_text(caption)
            expect(native.locator(".source-language-caption")).to_be_visible()
            expect(native).to_have_accessible_description(caption)
            expect(native).to_have_attribute("aria-describedby", f"graph-name-source-{identity}")
            expect(page.locator(f'[id="graph-name-source-{identity}"]')).to_have_count(1)
            for selector in ("text", "title"):
                for attribute, value in (("lang","en"),("dir","ltr"),("direction","ltr")):
                    expect(svg.locator(selector)).to_have_attribute(attribute,value)
                assert "source-language-island" in svg.locator(selector).get_attribute("class")
            expect(svg.locator(":scope > desc.source-language-caption")).to_have_text(caption)
        else:
            expect(native.locator(".graph-node-name")).to_have_text(name)
            expect(native.locator(".source-language-caption")).to_have_count(0)
            expect(svg.locator(".source-language-island")).to_have_count(0)
    product = next(node for node in artifact_graph_payload("adjacency","SAU-H0-721049","public")["nodes"] if node["id"] == "SAU-H0-721049")
    expect(page.locator('.graph-svg-node[data-graph-id="SAU-H0-721049"] title')).to_have_text(product["name_ar" if locale.code == "ar" else "name_en"])
    expect(page.locator('.graph-button-list [data-graph-id="SAU-H0-721049"] .graph-node-name')).to_have_text(product["name_ar" if locale.code == "ar" else "name_en"])
    expect(page.locator('.graph-svg-node[data-graph-id="SAU-H0-721049"] .source-language-island')).to_have_count(0)
    if locale.code == "ar":
        assert_arabic_parity(arabic_parity_report(page,"#graph-view"),expected_source_spans=6)
        expect(page.locator('#graph-view[dir="ltr"], .graph-diagram[dir="ltr"], .graph-svg-node[dir="ltr"]')).to_have_count(0)
        view=graph_catalogue_fixture()["views"][0]
        expect(page.locator('.graph-diagram')).to_have_accessible_name(f'{view["label"]["ar"]} {view["description"]["ar"]} {caption}')


# AM4 field-by-field raw-fixture enumeration; independent source/UI review binds its receipt.
PASSPORT_SOURCE_COUNTS = {
    'SAU-H0-721049|public|adjacency|node': 30, 'SAU-H0-721049|public|adjacency|edge': 10,
    'SAU-H0-721049|public|route_blocking|empty': 0, 'SAU-H0-721049|public|shared_enabler|empty': 0,
    'SAU-H0-721049|public|evidence_to_change|node': 24, 'SAU-H0-721049|public|evidence_to_change|edge': 0,
    'SAU-H0-721049|simulated|adjacency|node': 25, 'SAU-H0-721049|simulated|adjacency|edge': 2,
    'SAU-H0-721049|simulated|route_blocking|node': 25, 'SAU-H0-721049|simulated|route_blocking|edge': 2,
    'SAU-H0-721049|simulated|shared_enabler|empty': 0,
    'SAU-H0-721049|simulated|evidence_to_change|node': 25, 'SAU-H0-721049|simulated|evidence_to_change|edge': 2,
    'SAU-H6-760711|public|adjacency|empty': 0, 'SAU-H6-760711|public|route_blocking|empty': 0,
    'SAU-H6-760711|public|shared_enabler|empty': 0,
    'SAU-H6-760711|public|evidence_to_change|node': 18, 'SAU-H6-760711|public|evidence_to_change|edge': 3,
    'SAU-H6-760711|simulated|adjacency|node': 19, 'SAU-H6-760711|simulated|adjacency|edge': 2,
    'SAU-H6-760711|simulated|route_blocking|node': 19, 'SAU-H6-760711|simulated|route_blocking|edge': 2,
    'SAU-H6-760711|simulated|shared_enabler|node': 19, 'SAU-H6-760711|simulated|shared_enabler|edge': 6,
    'SAU-H6-760711|simulated|evidence_to_change|node': 19, 'SAU-H6-760711|simulated|evidence_to_change|edge': 2,
    'SAU-H6-760711|public|evidence_to_change|route_economics_zero': 0,
}


# These ten literal count fixtures bind to relationship meaning, never REL/ENGINE order.
# A Decision source is resolved from the payload's case and branch properties.
GRAPH_COUNTED_EDGE_SPECS = {
    'SAU-H0-721049|public|adjacency|edge': ('ADJACENT_TO', 'COMPANY-280abef66af82a6c', 'SAU-H0-721049', {'attribution_scope': 'PRODUCER_DISCLOSURE'}, ['ENGINE-EVIDENCE-SAU-H0-721049-public', 'S-HADEED'], 'ENGINE-EVIDENCE-SAU-H0-721049-public', 'PUBLIC', False),
    'SAU-H0-721049|public|evidence_to_change|edge': ('CONSTRAINED_BY', 'Decision', 'INT-SAU-H0-721049-route-5', {'blocked_field': 'route_economics', 'variant': 'plausible_route_economics_unresolved'}, [], 'ENGINE-EVIDENCE-SAU-H0-721049-public', 'PUBLIC', False),
    'SAU-H0-721049|simulated|adjacency|edge': ('ADJACENT_TO', 'PLANT-SYN-MINISTRY-STEEL-001', 'SAU-H0-721049', {'attribution_scope': 'CANDIDATE_DISCOVERY'}, ['ENGINE-EVIDENCE-SYN-MINISTRY-STEEL-001-simulated', 'SYN-MINISTRY-STEEL-001::candidate_fact::FACT-CUS-STEEL-A', 'SYN-MINISTRY-STEEL-001::candidate_fact::FACT-OUT-PLANT-8932de539dd9d7d8'], 'ENGINE-EVIDENCE-SYN-MINISTRY-STEEL-001-simulated', 'SYN-MINISTRY-STEEL-001', True),
    'SAU-H0-721049|simulated|route_blocking|edge': ('CONSTRAINED_BY', 'TEST-ONLY-INTERVENTION-5', 'TEST-ONLY-CAPABILITY-CERTIFICATION', {'reason_code': 'TEST_ONLY_CLASS_D_BLOCKER'}, None, 'TEST-ONLY-CLASS-D-BLOCKER', 'TEST-ONLY-S17-BLOCKER', True),
    'SAU-H0-721049|simulated|evidence_to_change|edge': ('CONSTRAINED_BY', 'Decision', 'INT-SYN-MINISTRY-STEEL-001-route-5', {'blocked_field': 'route_economics', 'variant': 'plausible_route_economics_unresolved'}, [], 'ENGINE-EVIDENCE-SYN-MINISTRY-STEEL-001-simulated', 'SYN-MINISTRY-STEEL-001', True),
    'SAU-H6-760711|public|evidence_to_change|edge': ('CONSTRAINED_BY', 'Decision', 'SAU-H6-760711', {'blocked_field': 'product_identity', 'variant': 'generic_hs6_only'}, ['P-WCO-760711'], 'ENGINE-EVIDENCE-SAU-H6-760711-public', 'PUBLIC', False),
    'SAU-H6-760711|simulated|adjacency|edge': ('ADJACENT_TO', 'PLANT-SYN-MINISTRY-ALU-FOIL-001', 'SAU-H6-760711', {'attribution_scope': 'DECLARED_ENGINE_INPUT'}, ['ENGINE-EVIDENCE-SYN-MINISTRY-ALU-FOIL-001-simulated'], 'ENGINE-EVIDENCE-SYN-MINISTRY-ALU-FOIL-001-simulated', 'SYN-MINISTRY-ALU-FOIL-001', True),
    'SAU-H6-760711|simulated|route_blocking|edge': ('CONSTRAINED_BY', 'TEST-ONLY-INTERVENTION-5', 'TEST-ONLY-CAPABILITY-CERTIFICATION', {'reason_code': 'TEST_ONLY_CLASS_D_BLOCKER'}, None, 'TEST-ONLY-CLASS-D-BLOCKER', 'TEST-ONLY-S17-BLOCKER', True),
    'SAU-H6-760711|simulated|shared_enabler|edge': ('UNLOCKED_BY', 'SAU-H6-760429', 'ENABLER-SYN-ALU-CASTHOUSE-001', {'constraint_classes_addressed': ['demand_fragmentation_or_offtake'], 'valuation_route_code': 4}, ['SYN-MINISTRY-ALU-PROFILES-001::shared_enabler'], 'SYN-MINISTRY-ALU-PROFILES-001::shared_enabler', 'SYN-MINISTRY-ALU-PROFILES-001', True),
    'SAU-H6-760711|simulated|evidence_to_change|edge': ('CONSTRAINED_BY', 'Decision', 'INT-SYN-MINISTRY-ALU-FOIL-001-route-6', {'blocked_field': 'route_economics', 'variant': 'route_determination_unresolved'}, [], 'ENGINE-EVIDENCE-SYN-MINISTRY-ALU-FOIL-001-simulated', 'SYN-MINISTRY-ALU-FOIL-001', True),
    'SAU-H6-760711|public|evidence_to_change|route_economics_zero': ('CONSTRAINED_BY', 'Decision', 'SAU-H6-760711', {'blocked_field': 'route_economics', 'variant': 'route_determination_unresolved'}, [], 'ENGINE-EVIDENCE-SAU-H6-760711-public', 'PUBLIC', False),
}


def select_counted_graph_edge(payload: dict[str, Any], key: str) -> dict[str, Any]:
    relation, source, target, properties, evidence_ids, evidence_id, scenario_id, synthetic = GRAPH_COUNTED_EDGE_SPECS[key]
    case_id, mode, _, _ = key.split('|')
    if source == 'Decision':
        decisions = [node for node in payload['nodes'] if node['label'] == 'Decision'
                     and node['properties'].get('opportunity_id') == case_id
                     and node['properties'].get('mode') == mode
                     and node['provenance']['evidence_id'] == evidence_id
                     and node['provenance']['scenario_id'] == scenario_id
                     and node['provenance']['synthetic_flag'] is synthetic]
        assert len(decisions) == 1, (key, decisions)
        source = decisions[0]['id']
    matches = [edge for edge in payload['edges'] if edge['type'] == relation
               and edge['source'] == source and edge['target'] == target
               and all(edge['properties'].get(name) == value for name, value in properties.items())
               and (edge['properties'].get('evidence_ids', object()) == evidence_ids if evidence_ids is not None
                    else 'evidence_ids' not in edge['properties'])
               and edge['provenance']['evidence_id'] == evidence_id
               and edge['provenance']['scenario_id'] == scenario_id
               and edge['provenance']['synthetic_flag'] is synthetic]
    assert len(matches) == 1, (key, matches)
    if evidence_ids is None:
        assert matches[0]['id'] == 'TEST-ONLY-ROUTE-BLOCKER-EDGE'
    return matches[0]


def assert_selected_graph_passports(page: Any, locale: Any, mode: str, count_key: str) -> None:
    from browser_tests.pages import arabic_parity_report, assert_arabic_parity, locale_bundle
    from browser_tests.harness import run_axe, format_axe_violations
    if locale.code == 'ar':
        assert_arabic_parity(arabic_parity_report(page, '#graph-view'), expected_source_spans=PASSPORT_SOURCE_COUNTS[count_key])
    if count_key in GRAPH_COUNTED_EDGE_SPECS:
        expected = {
            'SAU-H0-721049|public|adjacency|edge': {'S-HADEED'},
            'SAU-H6-760711|public|evidence_to_change|edge': {'P-WCO-760711'},
            'SAU-H6-760711|simulated|shared_enabler|edge': {'SYN-MINISTRY-ALU-PROFILES-001::shared_enabler'},
        }.get(count_key, set())
        assert set(page.locator('#graph-view [data-passport-id]').evaluate_all(
            'rows => rows.map(row => row.dataset.passportId)'
        )) == expected
        if not expected:
            unresolved = page.locator('.graph-unresolved li bdi').all_text_contents()
            spec = GRAPH_COUNTED_EDGE_SPECS[count_key]
            assert set(unresolved) == {spec[5], *(spec[4] or [])}
    strings = locale_bundle(locale)['strings']
    for article in page.locator('#graph-view [data-passport-id]').all():
        identity = article.locator('[data-passport-value="opportunity_id"]').inner_text()
        rows = page.request.get(f'/api/opportunities/{identity}?mode={mode}').json()['evidence']
        row = next(value for value in rows if value['evidence_id'] == article.get_attribute('data-passport-id'))
        for name in ('title', 'source', 'period', 'retrieved_at', 'evidence_class', 'contradiction', 'scenario_id'):
            value = row.get(name)
            expected = strings['common.unavailable'] if value is None or value in ('', 'UNAVAILABLE') else str(value)
            actual = article.locator(f'[data-passport-value="{name}"]').evaluate("n=>{const c=n.cloneNode(true);c.querySelectorAll('.source-language-caption').forEach(n=>n.remove());return c.textContent}")
            assert actual == expected, (name, actual, expected)
        assert article.locator('[data-passport-value="status"]').inner_text() == strings[f"graph.status.{row['status']}"]
        assert article.locator('[data-passport-value="support"]').evaluate_all("rows=>rows.map(n=>{const c=n.cloneNode(true);c.querySelectorAll('.source-language-caption').forEach(n=>n.remove());return c.textContent})") == row.get('supports', [])
        assert article.locator('.technical-token').evaluate_all("nodes=>nodes.every(n=>n.dir==='ltr')")
        safe_url = page.evaluate("value=>{try{const u=new URL(value);return ['http:','https:'].includes(u.protocol)?u.href:null}catch{return null}}", row.get('url'))
        external = article.locator('a')
        assert external.count() == int(safe_url is not None)
        if safe_url:
            assert external.get_attribute('href') == safe_url
            assert external.get_attribute('target') == '_blank'
            assert external.get_attribute('rel') == 'noopener noreferrer'
        if row.get('synthetic_flag'):
            assert article.locator('.synthetic-labels').count() == 1
            for language in ('en', 'ar'):
                assert article.locator('.synthetic-labels').inner_text().find(row['display_labels'][language]) >= 0
        link = page.locator(f'[data-passport-ref][href="#{article.get_attribute("id")}"]')
        assert link.locator('[data-passport-value="title"]').evaluate("n=>{const c=n.cloneNode(true);c.querySelectorAll('.source-language-caption').forEach(n=>n.remove());return c.textContent}") == row.get('title', row['evidence_id'])
        if locale.code == 'ar':
            assert link.evaluate("a=>{const c=a.nextElementSibling;return c?.classList.contains('source-language-caption')&&c.id===a.getAttribute('aria-describedby')&&c.checkVisibility()}")
        link.focus(); page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.id') == article.get_attribute('id')
    assert_graph_panel_contains_controls_and_text(page)
    report = run_axe(page)
    assert not report['violations'], format_axe_violations(report['violations'])
