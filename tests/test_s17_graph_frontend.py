from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from browser_tests.graph_fixtures import artifact_graph_payload, route_blocking_fixture
from browser_tests.graph_pages import GRAPH_COUNTED_EDGE_SPECS, PASSPORT_SOURCE_COUNTS, select_counted_graph_edge
from ior_mvp.config import PROJECT_ROOT, ui_strings_bundle


NODE = "node"
MODULE_ROOT = PROJECT_ROOT / "src/ior_mvp/static/modules/graph"


def test_counted_relationship_selectors_are_unique_on_current_artifact() -> None:
    keys = list(GRAPH_COUNTED_EDGE_SPECS)
    assert set(keys[:10]) == {key for key in PASSPORT_SOURCE_COUNTS if key.endswith('|edge')}
    assert [PASSPORT_SOURCE_COUNTS[key] for key in keys[:10]] == [10, 0, 2, 2, 2, 3, 2, 2, 6, 2]
    assert PASSPORT_SOURCE_COUNTS[keys[10]] == 0
    for key in keys:
        case_id, mode, view, _ = key.split('|')
        payload = (route_blocking_fixture(case_id) if view == 'route_blocking' else
                   artifact_graph_payload(view, case_id, mode))
        selected = select_counted_graph_edge(payload, key)
        assert selected in payload['edges']
        corrupted = deepcopy(payload)
        row = next(edge for edge in corrupted['edges'] if edge['id'] == selected['id'])
        row['provenance']['evidence_id'] = 'WRONG-EVIDENCE'
        with pytest.raises(AssertionError):
            select_counted_graph_edge(corrupted, key)


def _run(script: str) -> dict:
    result = subprocess.run(
        [NODE, "--input-type=module"],
        input=script,
        text=True,
        capture_output=True,
        check=False,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _url(path: Path) -> str:
    return path.resolve().as_uri()


def test_actual_model_rejects_duplicates_dangling_edges_and_public_synthetic() -> None:
    payload = artifact_graph_payload("adjacency", "SAU-H0-721049", "public")
    script = f"""
const {{validateGraphPayload}} = await import({_url(MODULE_ROOT / 'model.js')!r});
const payload = {json.dumps(payload, ensure_ascii=False)};
const context = {{viewId: 'adjacency', opportunityId: 'SAU-H0-721049', mode: 'public'}};
const outcomes = [];
outcomes.push(validateGraphPayload(structuredClone(payload), context).graph_status);
for (const mutate of [
  value => value.nodes.push(structuredClone(value.nodes[0])),
  value => value.edges[0].target = 'MISSING-NODE',
  value => {{ value.nodes[0].provenance.synthetic_flag = true; value.synthetic_flag = true; }},
]) {{
  const value = structuredClone(payload);
  try {{ mutate(value); validateGraphPayload(value, context); outcomes.push('accepted'); }}
  catch (error) {{ outcomes.push(error.message); }}
}}
console.log(JSON.stringify({{outcomes}}));
"""
    result = _run(script)
    assert result["outcomes"] == [
        "AVAILABLE",
        "GRAPH_RESPONSE_INVALID",
        "GRAPH_RESPONSE_INVALID",
        "GRAPH_PUBLIC_SYNTHETIC_REJECTED",
    ]


def test_actual_layout_is_deterministic_finite_and_mirrored_for_rtl() -> None:
    script = f"""
const {{layoutGraph, layoutDimensions}} = await import({_url(MODULE_ROOT / 'layout.js')!r});
const nodes = [{{id:'z'}}, {{id:'a'}}, {{id:'م'}}];
const ltr = layoutGraph(nodes, 'ltr');
const again = layoutGraph([...nodes].reverse(), 'ltr');
const rtl = layoutGraph(nodes, 'rtl');
console.log(JSON.stringify({{ltr, again, rtl, dimensions: layoutDimensions()}}));
"""
    result = _run(script)
    assert result["ltr"] == result["again"]
    width = result["dimensions"]["width"]
    assert all(
        left["id"] == right["id"] and left["x"] + right["x"] == width
        for left, right in zip(result["ltr"], result["rtl"], strict=True)
    )
    assert all(
        isinstance(row["x"], (int, float)) and isinstance(row["y"], (int, float))
        for row in result["ltr"]
    )


def test_actual_svg_edge_hit_polygon_has_finite_pointer_area() -> None:
    script = f"""
const {{edgeHitPolygon, visibleEdgeEndpoints}} = await import({_url(MODULE_ROOT / 'diagram.js')!r});
const horizontal = edgeHitPolygon({{x:10,y:20}}, {{x:110,y:20}});
const vertical = edgeHitPolygon({{x:30,y:10}}, {{x:30,y:90}});
const trimmed = visibleEdgeEndpoints({{x:10,y:20}}, {{x:110,y:20}});
console.log(JSON.stringify({{horizontal, vertical, trimmed}}));
"""
    result = _run(script)
    assert result["trimmed"] == {
        "source": {"x": 40, "y": 20},
        "target": {"x": 72, "y": 20},
    }
    assert result["horizontal"] == [
        [40, 30],
        [72, 30],
        [72, 10],
        [40, 10],
    ]
    assert result["vertical"] == [
        [20, 40],
        [20, 52],
        [40, 52],
        [40, 40],
    ]


def test_repeated_routes_keep_five_distinct_lanes_and_mirror_each_identity() -> None:
    payloads = [
        artifact_graph_payload('adjacency', 'SAU-H0-721049', 'public'),
        artifact_graph_payload('evidence_to_change', 'SAU-H0-721049', 'simulated'),
    ]
    script = f"""
const {{layoutGraph, layoutDimensions}} = await import({_url(MODULE_ROOT / 'layout.js')!r});
const {{repeatedEdgeRoutes}} = await import({_url(MODULE_ROOT / 'edge-geometry.js')!r});
const payloads = {json.dumps(payloads, ensure_ascii=False)};
const rows = payloads.map(payload => {{
  const directions = ['ltr', 'rtl'].map(direction => {{
    const byId = Object.fromEntries(layoutGraph(payload.nodes, direction).map(point => [point.id, point]));
    return repeatedEdgeRoutes(payload.edges, byId, 30, 8, direction);
  }});
  const groups = new Map();
  for (const edge of payload.edges) {{
    const key = [edge.source, edge.target].sort().join('|');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(edge.id);
  }}
  return [...groups.values()].filter(ids => ids.length > 1).map(ids => ({{
    count: ids.length,
    distinct: new Set(ids.map(id => JSON.stringify(directions[0].get(id).points.slice(1, 3)))).size === ids.length,
    mirrored: ids.every(id => directions[0].get(id).points.every((point, index) => {{
      const counterpart = directions[1].get(id).points[index];
      return Math.abs(point.x + counterpart.x - layoutDimensions().width) < 1e-9
        && Math.abs(point.y - counterpart.y) < 1e-9;
    }})),
  }}));
}});
console.log(JSON.stringify(rows));
"""
    rows = _run(script)
    assert any(group['count'] == 5 for group in rows[1])
    assert any(group['count'] == 2 for group in rows[0])
    assert all(group['distinct'] and group['mirrored'] for groups in rows for group in groups)


def test_actual_svg_labels_and_edges_stay_inside_intrinsic_viewbox() -> None:
    payloads = (
        artifact_graph_payload("adjacency", "SAU-H0-721049", "public"),
        route_blocking_fixture("SAU-H0-721049"),
        artifact_graph_payload(
            "shared_enabler",
            "SAU-H6-760711",
            "simulated",
        ),
        artifact_graph_payload(
            "evidence_to_change",
            "SAU-H0-721049",
            "public",
        ),
        artifact_graph_payload(
            "evidence_to_change",
            "SAU-H0-721049",
            "simulated",
        ),
        artifact_graph_payload(
            "evidence_to_change",
            "SAU-H6-760711",
            "public",
        ),
        artifact_graph_payload(
            "evidence_to_change",
            "SAU-H6-760711",
            "simulated",
        ),
    )
    script = f"""
const {{
  approximateTextBBox,
  svgNodeLabelPresentation,
  visibleEdgeEndpoints,
}} = await import({_url(MODULE_ROOT / 'diagram.js')!r});
const {{repeatedEdgeRoutes}} = await import({_url(MODULE_ROOT / 'edge-geometry.js')!r});
const {{
  GRAPH_MARKER_CLEARANCE,
  GRAPH_NODE_RADIUS,
  layoutGraph,
  layoutDimensions,
}} = await import({_url(MODULE_ROOT / 'layout.js')!r});
const {{state}} = await import({_url(MODULE_ROOT.parent / 'state.js')!r});
const {{nodeLabel}} = await import({_url(MODULE_ROOT / 'labels.js')!r});
const bundles = {json.dumps({locale: ui_strings_bundle(locale) for locale in ('en', 'ar')}, ensure_ascii=False)};
const GEOMETRY_TOLERANCE = 1e-9;
const GRAPH_CAPTION_EDGE_CLEARANCE = 6;
const GRAPH_EDGE_STROKE_RADIUS = 1;
const payloads = {json.dumps(payloads, ensure_ascii=False)};
const outcomes = [];
const intersectsSegment = (box, edge, padding) => {{
  const left = box.x - padding;
  const right = box.x + box.width + padding;
  const top = box.y - padding;
  const bottom = box.y + box.height + padding;
  const dx = edge.target.x - edge.source.x;
  const dy = edge.target.y - edge.source.y;
  let entry = 0;
  let exit = 1;
  for (const [p, q] of [
    [-dx, edge.source.x - left],
    [dx, right - edge.source.x],
    [-dy, edge.source.y - top],
    [dy, bottom - edge.source.y],
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
const intersectsMarker = (box, target) => {{
  const nearestX = Math.max(box.x, Math.min(target.x, box.x + box.width));
  const nearestY = Math.max(box.y, Math.min(target.y, box.y + box.height));
  return Math.hypot(target.x - nearestX, target.y - nearestY)
    <= GRAPH_MARKER_CLEARANCE + GRAPH_CAPTION_EDGE_CLEARANCE;
}};
const intersectsBox = (left, right) => !(
  left.x + left.width <= right.x
  || right.x + right.width <= left.x
  || left.y + left.height <= right.y
  || right.y + right.height <= left.y
);
const intersectsCircle = (box, point) => {{
  const nearestX = Math.max(box.x, Math.min(point.x, box.x + box.width));
  const nearestY = Math.max(box.y, Math.min(point.y, box.y + box.height));
  return Math.hypot(point.x - nearestX, point.y - nearestY)
    < GRAPH_NODE_RADIUS;
}};
for (const payload of payloads) {{
  for (const direction of ['ltr', 'rtl']) {{
    state.ui = bundles[direction === 'rtl' ? 'ar' : 'en'];
    const positions = layoutGraph(payload.nodes, direction);
    const {{width, height}} = layoutDimensions();
    const byId = Object.fromEntries(positions.map((point) => [point.id, point]));
    const routes = repeatedEdgeRoutes(payload.edges, byId, GRAPH_NODE_RADIUS, GRAPH_MARKER_CLEARANCE, direction);
    const visibleEdges = payload.edges.flatMap((edge) => routes.has(edge.id)
      ? routes.get(edge.id).segments.map((segment) => ({{id: edge.id, ...segment}}))
      : [{{id: edge.id, ...visibleEdgeEndpoints(byId[edge.source], byId[edge.target]), terminal: true}}]);
    const placedBoxes = [];
    const labels = positions.map((point) => {{
      const node = payload.nodes.find((row) => row.id === point.id);
      const label = nodeLabel(node, direction === 'rtl' ? 'ar' : 'en');
      const presentation = svgNodeLabelPresentation(
        label,
        point.x,
        point.y,
        width,
        height,
        direction,
        {{
          edges: visibleEdges,
          nodeId: point.id,
          placedBoxes,
          positions,
        }},
      );
      const box = approximateTextBBox(
        point.x + (presentation.dx || 0),
        point.y,
        presentation.text,
        presentation.textAnchor,
        presentation.dy,
      );
      const edgeClear = visibleEdges.every((edge) => (
        !intersectsSegment(
          box,
          edge,
          GRAPH_CAPTION_EDGE_CLEARANCE + GRAPH_EDGE_STROKE_RADIUS,
        )
        && (!edge.terminal || !intersectsMarker(box, edge.target))
      ));
      const captionsClear = placedBoxes.every(
        (placed) => !intersectsBox(box, placed),
      );
      const circlesClear = positions.every(
        (other) => other.id === point.id || !intersectsCircle(box, other),
      );
      const inside = (
        box.x >= 0
        && box.y >= 0
        && box.x + box.width <= width
        && box.y + box.height <= height
      );
      placedBoxes.push(box);
      return {{inside, edgeClear, captionsClear, circlesClear}};
    }});
    const edges = payload.edges.map((edge) => {{
      const source = positions.find((row) => row.id === edge.source);
      const target = positions.find((row) => row.id === edge.target);
      const route = routes.get(edge.id);
      const endpoints = route ? {{source: route.points[0], target: route.points.at(-1)}}
        : visibleEdgeEndpoints(source, target);
      const sourceDistance = Math.hypot(
        endpoints.source.x - source.x,
        endpoints.source.y - source.y,
      );
      const targetDistance = Math.hypot(
        target.x - endpoints.target.x,
        target.y - endpoints.target.y,
      );
      const terminal = route ? route.segments.at(-1) : endpoints;
      const segmentX = terminal.target.x - terminal.source.x;
      const segmentY = terminal.target.y - terminal.source.y;
      const directionDot = (
        segmentX * (target.x - source.x)
        + segmentY * (target.y - source.y)
      );
      return (
        Number.isFinite(sourceDistance)
        && Number.isFinite(targetDistance)
        && Math.abs(sourceDistance - GRAPH_NODE_RADIUS) < GEOMETRY_TOLERANCE
        && Math.abs(
          targetDistance - GRAPH_NODE_RADIUS - GRAPH_MARKER_CLEARANCE
        ) < GEOMETRY_TOLERANCE
        && directionDot > 0
        && (!route || route.segments.length === 3)
        && (!route || route.points.every(point => point.x >= 0 && point.x <= width && point.y >= 0 && point.y <= height))
      );
    }});
    outcomes.push({{viewId: payload.view_id, direction, labels, edges,
      segmentCount: visibleEdges.length, edgeCount: payload.edges.length,
      routeCount: routes.size}});
  }}
}}
console.log(JSON.stringify({{outcomes}}));
"""
    result = _run(script)
    assert len(result["outcomes"]) == 14
    for row in result["outcomes"]:
        assert all(
            label["inside"]
            and label["edgeClear"]
            and label["captionsClear"]
            and label["circlesClear"]
            for label in row["labels"]
        )
        assert all(row["edges"]), (row["viewId"], row["direction"], [i for i, valid in enumerate(row["edges"]) if not valid])
        assert row["segmentCount"] >= row["edgeCount"] > 0
    assert any(row["routeCount"] >= 5 for row in result["outcomes"])


def test_actual_diagram_escapes_untrusted_labels_and_has_no_tab_stop() -> None:
    script = f"""
const {{renderDiagram}} = await import({_url(MODULE_ROOT / 'diagram.js')!r});
const payload = {{view_id:'adjacency', projection_id:'GRAPH-TEST', edges:[], nodes:[{{
  id:'n1', label:'Product', name_en:'<img onerror=alert(1)>', name_ar:'منتج',
  provenance:{{synthetic_flag:false}}
}}]}};
const html = renderDiagram(payload, 'en', null, {{
  title:'Governed graph title', description:'Governed graph description',
}});
console.log(JSON.stringify({{html}}));
"""
    html = _run(script)["html"]
    assert "<img" not in html
    assert "&lt;img" in html
    assert 'role="img"' in html
    assert 'aria-hidden="true"' in html
    assert 'role="button"' not in html
    assert "tabindex=" not in html
    assert "Governed graph title" in html
    assert "Governed graph description" in html
    assert "GRAPH-TEST" not in html


def test_native_edge_control_uses_decorative_svg_without_changing_name() -> None:
    script = f"""
const {{state}} = await import({_url(MODULE_ROOT.parent / "state.js")!r});
const {{renderGraphShell}} = await import({_url(MODULE_ROOT / "render.js")!r});
state.locale = 'en';
state.ui = {{strings: {{
  'graph.title': 'Graph',
  'graph.scroll_hint': 'Scroll the diagram with arrow keys.',
  'graph.close': 'Close graph',
  'graph.panel_aria': 'Graph panel',
  'graph.view_selector': 'View',
  'graph.explanation.adjacency': 'Explanation',
  'graph.node_button': 'Select node {{label}}',
  'graph.edge_button': 'Select edge {{label}}',
  'graph.node.product': 'Product',
  'graph.edge.depends_on': 'Depends on',
  'graph.nodes_title': 'Nodes',
  'graph.edges_title': 'Edges',
  'graph.details_title': 'Details',
  'graph.selection_none': 'Nothing selected',
}}}};
const provenance = {{synthetic_flag:false, evidence_class:'C'}};
const payload = {{
  display_labels:null,
  explanation:{{catalogue_key:'view.adjacency.explanation', values:{{}}}},
  nodes:[
    {{id:'SOURCE', label:'Product', name_en:'Source', provenance}},
    {{id:'TARGET', label:'Product', name_en:'Target', provenance}},
  ],
  edges:[{{id:'EDGE', type:'DEPENDS_ON', source:'SOURCE', target:'TARGET'}}],
}};
const graph = {{
  open:true,
  viewId:'adjacency',
  catalogue:{{views:[{{
    view_id:'adjacency',
    label:{{en:'Adjacency', ar:'التجاور'}},
    description:{{en:'Description', ar:'الوصف'}},
  }}]}},
  payload,
  selected:null,
}};
const html = renderGraphShell(
  {{opportunity_id:'SOURCE', mode:'public'}},
  graph,
  true,
);
console.log(JSON.stringify({{html}}));
"""
    html = _run(script)["html"]
    edge_marker = (
        'data-graph-select="edge" data-graph-id="EDGE" '
        'aria-label="Select edge Depends on"'
    )
    marker_index = html.index(edge_marker)
    button_start = html.rindex("<button", 0, marker_index)
    edge_button = html[button_start : html.index("</button>", button_start)]
    assert 'aria-label="Select edge Depends on"' in edge_button
    assert "→" not in edge_button
    assert '<svg class="transition-icon graph-edge-direction"' in edge_button
    assert 'aria-hidden="true"' in edge_button
    assert 'focusable="false"' in edge_button
    assert (
        edge_button.index("SOURCE")
        < edge_button.index("<svg")
        < edge_button.index("TARGET")
    )


def test_scoped_graph_fact_table_is_named_and_keyboard_focusable_in_both_locales() -> None:
    payload = artifact_graph_payload('adjacency', 'SAU-H0-721049', 'simulated')
    selected = next(edge for edge in payload['edges']
                    if edge['properties'].get('attribution_scope') == 'CANDIDATE_DISCOVERY')
    bundles = {locale: ui_strings_bundle(locale) for locale in ('en', 'ar')}
    script = f"""
const {{state}} = await import({_url(MODULE_ROOT.parent / 'state.js')!r});
const {{renderGraphShell}} = await import({_url(MODULE_ROOT / 'render.js')!r});
const payload = {json.dumps(payload, ensure_ascii=False)};
const selected = {json.dumps(selected, ensure_ascii=False)};
const bundles = {json.dumps(bundles, ensure_ascii=False)};
const html = {{}};
for (const locale of ['en', 'ar']) {{
  state.locale = locale; state.ui = bundles[locale];
  html[locale] = renderGraphShell({{opportunity_id:'SAU-H0-721049', mode:'simulated'}}, {{
    open:true, viewId:'adjacency', payload, context:{{mode:'simulated'}},
    catalogue:{{views:[{{view_id:'adjacency',label:{{en:'Adjacency',ar:'التجاور'}},description:{{en:'Graph',ar:'رسم'}}}}]}},
    selected:{{identity:selected.id, element:selected}},
    evidenceResult:{{records:[],unresolved:[],documentAddresses:[]}},
  }}, true);
}}
console.log(JSON.stringify(html));
"""
    rendered = _run(script)
    for locale in ('en', 'ar'):
        label = bundles[locale]['strings']['graph.details_title']
        assert f'role="region" tabindex="0" aria-label="{label}"' in rendered[locale]
        assert 'class="graph-source-table"' in rendered[locale]


def test_actual_passport_url_guard_accepts_only_http_and_https() -> None:
    script = f"""
const {{safeExternalUrl}} = await import({_url(MODULE_ROOT / 'passports.js')!r});
const values = ['https://example.com/a', 'http://example.com/b', 'file:///tmp/a', 'javascript:alert(1)', 'not a url'];
console.log(JSON.stringify({{values: values.map(safeExternalUrl)}}));
"""
    assert _run(script)["values"] == [
        "https://example.com/a",
        "http://example.com/b",
        None,
        None,
        None,
    ]


def test_actual_evidence_resolver_qualifies_conflicts_and_keeps_missing_refs() -> None:
    script = f"""
const {{resolveElementEvidence}} = await import({_url(MODULE_ROOT / 'evidence.js')!r});
const element = {{id:'CURRENT', label:'Product', provenance:{{evidence_id:'E-1'}}, properties:{{evidence_ids:['E-MISSING','SYN-MINISTRY-ALU-FOIL-001::forged']}}}};
const payload = {{nodes:[element, {{id:'RELATED', label:'Product'}}], drilldown:[{{element_id:'CURRENT', evidence_ids:['E-1'], document_addresses:['doc:1']}}]}};
const analysis = {{mode:'public', opportunity:{{id:'CURRENT'}}, evidence:[{{evidence_id:'E-1', title:'current'}}]}};
const result = await resolveElementEvidence({{
  payload, element, analysis,
  opportunities:[{{id:'CURRENT'}}, {{id:'RELATED'}}], mode:'public', cache:{{}},
  fetchAnalysis: async () => ({{mode:'public', opportunity:{{id:'RELATED'}}, evidence:[{{evidence_id:'E-1', title:'related'}}]}}),
}});
console.log(JSON.stringify(result));
"""
    result = _run(script)
    assert [row["opportunityId"] for row in result["records"]] == [
        "CURRENT",
        "RELATED",
    ]
    assert result["unresolved"] == ["E-MISSING", "SYN-MINISTRY-ALU-FOIL-001::forged"]
    assert result["documentAddresses"] == ["doc:1"]


def test_actual_company_name_fallback_preserves_literal_canonical_names() -> None:
    payload = artifact_graph_payload("adjacency", "SAU-H0-721049", "public")
    script = f"""
const {{state}} = await import({_url(MODULE_ROOT.parent / 'state.js')!r});
const {{nodeLabel}} = await import({_url(MODULE_ROOT / 'labels.js')!r});
state.ui = {json.dumps(ui_strings_bundle('ar'), ensure_ascii=False)};
const nodes = {json.dumps(payload['nodes'], ensure_ascii=False)};
console.log(JSON.stringify(Object.fromEntries(nodes.filter(n=>n.label==='Company').map(n=>[n.id,nodeLabel(n,'ar')]))));
"""
    assert _run(script) == {
        "COMPANY-280abef66af82a6c": "Hadeed",
        "COMPANY-a0954792195adee5": "Universal Metal Coating Company",
    }


def test_actual_name_presentation_handles_typed_absence_and_keeps_real_names() -> None:
    script = f"""
const {{state}} = await import({_url(MODULE_ROOT.parent / 'state.js')!r});
const {{nodeNamePresentation}} = await import({_url(MODULE_ROOT / 'labels.js')!r});
state.ui = {json.dumps(ui_strings_bundle('ar'), ensure_ascii=False)};
const missing=[undefined,null,'','   ','UNAVAILABLE',' UNAVAILABLE ',false,0,1];
const fallback=missing.map(name_ar=>nodeNamePresentation({{label:'Company',name_ar,name_en:' Hadeed '}},'ar'));
const absent=missing.map(name=>nodeNamePresentation({{label:'Company',name_ar:name,name_en:name}},'ar'));
const real=['شركة حديد','unavailable','N/A','UNAVAILABLE supplier'].map(name_ar=>nodeNamePresentation({{label:'Company',name_ar,name_en:'Hadeed'}},'ar'));
const english=nodeNamePresentation({{label:'Company',name_ar:'شركة حديد',name_en:'Hadeed'}},'en');
console.log(JSON.stringify({{fallback,absent,real,english}}));
"""
    result = _run(script)
    assert result['fallback'] == [{'text': ' Hadeed ', 'sourceLanguage': 'en'}] * 9
    assert result['absent'] == [{'text': ui_strings_bundle('ar')['strings']['graph.node.company'], 'sourceLanguage': None}] * 9
    assert result['real'] == [{'text': text, 'sourceLanguage': None} for text in ('شركة حديد', 'unavailable', 'N/A', 'UNAVAILABLE supplier')]
    assert result['english'] == {'text': 'Hadeed', 'sourceLanguage': None}


def test_actual_passports_preserve_typed_sources_statuses_and_hostile_values() -> None:
    import html
    import re
    from fastapi.testclient import TestClient
    from ior_mvp.app import app
    client = TestClient(app)
    public = client.get('/api/opportunities/SAU-H0-721049?mode=public').json()['evidence'][0]
    synthetic = next(row for row in client.get('/api/opportunities/SAU-H6-760711?mode=simulated').json()['evidence'] if row['evidence_id'].endswith('::shared_enabler'))
    variants = [public, synthetic, {**public, 'title': 'مصدر عربي Hadeed', 'source': 'Hadeed', 'status': 'Unknown review prose', 'period': None, 'supports': []}, {**public, 'title': '<img onerror="alert(1)"> & source', 'source': {'bad': 1}, 'url': 'javascript:alert(1)'}, {**public, 'title': 'مصدر عربي', 'contradiction': 'Contradictory source retained'}, {**public, 'title': 'Источник', 'evidence_class': 'Unverified class prose'}]
    script = f"""
const {{state}} = await import({_url(MODULE_ROOT.parent / 'state.js')!r});
const {{renderEvidenceResult}} = await import({_url(MODULE_ROOT / 'passports.js')!r});
const variants = {json.dumps(variants, ensure_ascii=False)};
state.locale='ar'; state.ui={json.dumps(ui_strings_bundle('ar'), ensure_ascii=False)};
const render = record => renderEvidenceResult({{records:[{{opportunityId:'SAU-H0-721049',record}}],unresolved:['SYN-MINISTRY-ALU-FOIL-001::forged'],documentAddresses:[{{document_id:'DOC-001',page_index:0,line_index:0}},'Original document prose']}},'simulated');
const outputs=variants.map(render); let mismatch=false;
try {{render({{...variants[1],display_labels:null,display_label:'WRONG POLICY'}});}} catch {{mismatch=true;}}
console.log(JSON.stringify({{outputs,mismatch}}));
"""
    result = _run(script)
    output = result['outputs']
    assert 'lang="en" dir="ltr"' in output[1] and 'source-language-caption' in output[1]
    assert 'اصطناعي' in output[1] and '>synthetic<' not in output[1]
    assert 'SYN-MINISTRY-ALU-FOIL-001::shared_enabler</bdi>' in output[1]
    assert '2021/2023/2024</bdi>' in output[0]
    assert 'graph-passport-' in output[0] and 'aria-describedby=' in output[0]
    assert 'غير مؤكد من الجهة المسؤولة' in output[0]
    assert '<img' not in output[3] and 'javascript:' not in output[3]
    assert '[object Object]' not in output[3]
    for index, record in enumerate(variants):
        spans = re.findall(r'<span data-passport-value="title">(.*?)</span></(?:a|h5)>', output[index])
        assert len(spans) == 2
        for span in spans:
            without_captions = re.sub(r'<span class="source-language-caption"[^>]*>.*?</span>', '', span)
            assert html.unescape(re.sub('<[^>]+>', '', without_captions)) == record['title']
    assert 'lang="ar" dir="rtl">مصدر عربي ' in output[2]
    assert 'lang="ar" dir="rtl">مصدر عربي</span>' in output[4]
    assert 'lang="und" dir="auto">Источник</span>' in output[5]
    assert 'Contradictory source retained' in output[4]
    assert 'SYN-MINISTRY-ALU-FOIL-001::forged</bdi>' in output[0]
    assert output[0].count('>0</bdi>') == 2
    assert result['mismatch'] is True
