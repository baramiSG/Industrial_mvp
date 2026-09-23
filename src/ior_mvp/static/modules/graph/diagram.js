import { escapeHtml } from "../dom.js";
import { edgeLabel, nodeLabel } from "./labels.js";
import {
  GRAPH_MARKER_CLEARANCE,
  GRAPH_NODE_RADIUS,
  approximateTextBBox,
  layoutDimensions,
  layoutGraph,
  shortLabel,
  svgNodeLabelPresentation,
} from "./layout.js";

export { approximateTextBBox, shortLabel, svgNodeLabelPresentation };

export function visibleEdgeEndpoints(
  source,
  target,
  radius = GRAPH_NODE_RADIUS,
  markerClearance = GRAPH_MARKER_CLEARANCE,
) {
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const length = Math.hypot(dx, dy);
  if (!Number.isFinite(length) || length === 0) {
    throw new Error("GRAPH_EDGE_GEOMETRY_INVALID");
  }
  const unitX = dx / length;
  const unitY = dy / length;
  const trim = radius + markerClearance;
  if (length <= radius * 2 + markerClearance) {
    const midpoint = {
      x: (source.x + target.x) / 2,
      y: (source.y + target.y) / 2,
    };
    return { source: midpoint, target: midpoint };
  }
  return {
    source: {
      x: source.x + unitX * radius,
      y: source.y + unitY * radius,
    },
    target: {
      x: target.x - unitX * trim,
      y: target.y - unitY * trim,
    },
  };
}

export function edgeHitPolygon(source, target, halfWidth = 10) {
  const endpoints = visibleEdgeEndpoints(source, target);
  const dx = endpoints.target.x - endpoints.source.x;
  const dy = endpoints.target.y - endpoints.source.y;
  const length = Math.hypot(dx, dy);
  if (!Number.isFinite(length) || length === 0) {
    throw new Error("GRAPH_EDGE_GEOMETRY_INVALID");
  }
  const offsetX = (-dy / length) * halfWidth;
  const offsetY = (dx / length) * halfWidth;
  return [
    [endpoints.source.x + offsetX, endpoints.source.y + offsetY],
    [endpoints.target.x + offsetX, endpoints.target.y + offsetY],
    [endpoints.target.x - offsetX, endpoints.target.y - offsetY],
    [endpoints.source.x - offsetX, endpoints.source.y - offsetY],
  ];
}

export function labelWithinViewBox(
  label,
  x,
  y,
  viewWidth,
  viewHeight,
  direction = "ltr",
) {
  const presentation = svgNodeLabelPresentation(
    label,
    x,
    y,
    viewWidth,
    viewHeight,
    direction,
  );
  const box = approximateTextBBox(
    x + presentation.dx,
    y,
    presentation.text,
    presentation.textAnchor,
    presentation.dy,
  );
  return (
    box.x >= 0
    && box.y >= 0
    && box.x + box.width <= viewWidth
    && box.y + box.height <= viewHeight
  );
}

export function renderDiagram(
  payload,
  locale,
  selectedId = null,
  accessibility = {},
) {
  if (!accessibility.title || !accessibility.description) {
    throw new Error("GRAPH_ACCESSIBLE_LABEL_INVALID");
  }
  const direction = locale === "ar" ? "rtl" : "ltr";
  const positions = layoutGraph(payload.nodes, direction);
  const byId = Object.fromEntries(positions.map((row) => [row.id, row]));
  const { width, height } = layoutDimensions();
  const edgeGeometry = payload.edges.map((edge) => ({
    edge,
    ...visibleEdgeEndpoints(byId[edge.source], byId[edge.target]),
  }));
  const edges = edgeGeometry.map(({ edge, source, target }) => {
    const selected = edge.id === selectedId ? " is-selected" : "";
    const hitPoints = edgeHitPolygon(byId[edge.source], byId[edge.target])
      .map((point) => point.join(","))
      .join(" ");
    return `<g class="graph-svg-edge${selected}" data-graph-select="edge" data-graph-id="${escapeHtml(edge.id)}" aria-hidden="true"><polygon class="graph-svg-edge-hit" points="${hitPoints}"/><line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" marker-end="url(#graph-arrow)"/><title>${escapeHtml(edgeLabel(edge))}</title></g>`;
  }).join("");
  const labels = Object.fromEntries(
    payload.nodes.map((node) => [node.id, nodeLabel(node, locale)]),
  );
  const placedBoxes = [];
  const presentations = Object.fromEntries(positions.map((point) => {
    const presentation = svgNodeLabelPresentation(
      labels[point.id],
      point.x,
      point.y,
      width,
      height,
      direction,
      { edges: edgeGeometry, nodeId: point.id, placedBoxes, positions },
    );
    placedBoxes.push(approximateTextBBox(
      point.x + presentation.dx,
      point.y,
      presentation.text,
      presentation.textAnchor,
      presentation.dy,
    ));
    return [point.id, presentation];
  }));
  const nodes = payload.nodes.map((node) => {
    const point = byId[node.id];
    const label = labels[node.id];
    const selected = node.id === selectedId ? " is-selected" : "";
    const synthetic = node.provenance.synthetic_flag ? " is-synthetic" : "";
    const sourceLanguage = locale === "ar" && !node.name_ar && node.name_en
      ? ' direction="ltr"' : "";
    const presentation = presentations[node.id];
    return `<g class="graph-svg-node${selected}${synthetic}" data-graph-select="node" data-graph-id="${escapeHtml(node.id)}" aria-hidden="true" transform="translate(${point.x} ${point.y})"><circle r="${GRAPH_NODE_RADIUS}"/><text x="${presentation.dx}" text-anchor="${presentation.textAnchor}" dy="${presentation.dy}"${sourceLanguage}>${escapeHtml(presentation.text)}</text><title>${escapeHtml(label)}</title></g>`;
  }).join("");
  return `<svg class="graph-diagram" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="graph-svg-title graph-svg-description"><title id="graph-svg-title">${escapeHtml(accessibility.title)}</title><desc id="graph-svg-description">${escapeHtml(accessibility.description)}</desc><defs><marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z"/></marker></defs>${edges}${nodes}</svg>`;
}
