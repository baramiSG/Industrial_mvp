export const GRAPH_NODE_RADIUS = 30;
export const GRAPH_LABEL_DY = 48;
export const GRAPH_LABEL_LINE_HEIGHT = 14;
export const GRAPH_MARKER_CLEARANCE = 8;
export const GRAPH_APPROX_CHAR_WIDTH = 8;
export const GRAPH_MAX_LABEL_CODE_POINTS = 28;
export const GRAPH_CAPTION_EDGE_CLEARANCE = 6;

const GRAPH_WIDTH = 880;
const GRAPH_HEIGHT = 360;
const GRAPH_PADDING = 72;
const GRAPH_EDGE_MAX_STROKE_RADIUS = 2;
const GRAPH_MARKER_MAX_RADIUS = 16;

function codePointOrder(left, right) {
  if (left.id === right.id) return 0;
  return left.id < right.id ? -1 : 1;
}

export function layoutGraph(nodes, direction = "ltr") {
  const ordered = [...nodes].sort(codePointOrder);
  const columns = Math.max(1, Math.ceil(Math.sqrt(ordered.length)));
  const rows = Math.max(1, Math.ceil(ordered.length / columns));
  const xStep = columns === 1
    ? 0 : (GRAPH_WIDTH - GRAPH_PADDING * 2) / (columns - 1);
  const yStep = rows === 1
    ? 0 : (GRAPH_HEIGHT - GRAPH_PADDING * 2) / (rows - 1);
  return ordered.map((node, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    const logicalX = columns === 1
      ? GRAPH_WIDTH / 2 : GRAPH_PADDING + column * xStep;
    const x = direction === "rtl" ? GRAPH_WIDTH - logicalX : logicalX;
    const y = rows === 1
      ? GRAPH_HEIGHT / 2 : GRAPH_PADDING + row * yStep;
    if (![x, y].every(Number.isFinite)) {
      throw new Error("GRAPH_LAYOUT_INVALID");
    }
    return { id: node.id, x, y };
  });
}

export function layoutDimensions() {
  return { width: GRAPH_WIDTH, height: GRAPH_HEIGHT };
}

export function shortLabel(value, maxCodePoints = GRAPH_MAX_LABEL_CODE_POINTS) {
  const points = [...String(value)];
  if (points.length <= maxCodePoints) return value;
  const limit = Math.max(1, maxCodePoints - 1);
  return `${points.slice(0, limit).join("")}…`;
}

function maxLabelCodePoints(availableWidth) {
  const capacity = Math.floor(availableWidth / GRAPH_APPROX_CHAR_WIDTH);
  return Math.max(1, Math.min(GRAPH_MAX_LABEL_CODE_POINTS, capacity));
}

export function approximateTextBBox(x, y, text, textAnchor, dy) {
  const width = [...String(text)].length * GRAPH_APPROX_CHAR_WIDTH;
  let left = x;
  if (textAnchor === "middle") left = x - width / 2;
  if (textAnchor === "end") left = x - width;
  return {
    x: left,
    y: y + dy - GRAPH_LABEL_LINE_HEIGHT,
    width,
    height: GRAPH_LABEL_LINE_HEIGHT,
  };
}

function segmentIntersectsBox(box, edge, padding) {
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
  ]) {
    if (p === 0 && q < 0) return false;
    if (p === 0) continue;
    const ratio = q / p;
    if (p < 0) entry = Math.max(entry, ratio);
    else exit = Math.min(exit, ratio);
    if (entry > exit) return false;
  }
  return true;
}

function boxIntersectsCircle(box, point, radius) {
  const nearestX = Math.max(box.x, Math.min(point.x, box.x + box.width));
  const nearestY = Math.max(box.y, Math.min(point.y, box.y + box.height));
  return Math.hypot(point.x - nearestX, point.y - nearestY) < radius;
}

function boxesIntersect(left, right) {
  return !(
    left.x + left.width <= right.x
    || right.x + right.width <= left.x
    || left.y + left.height <= right.y
    || right.y + right.height <= left.y
  );
}

function presentationBox(point, presentation) {
  return approximateTextBBox(
    point.x + presentation.dx,
    point.y,
    presentation.text,
    presentation.textAnchor,
    presentation.dy,
  );
}

function candidateIsClear(candidate, point, view, geometry) {
  const box = presentationBox(point, candidate);
  const inside = (
    box.x >= 0
    && box.y >= 0
    && box.x + box.width <= view.width
    && box.y + box.height <= view.height
  );
  if (!inside) return false;
  const edgePadding = (
    GRAPH_CAPTION_EDGE_CLEARANCE + GRAPH_EDGE_MAX_STROKE_RADIUS
  );
  if (geometry.edges.some((edge) => (
    segmentIntersectsBox(box, edge, edgePadding)
    || boxIntersectsCircle(
      box,
      edge.target,
      GRAPH_MARKER_MAX_RADIUS + GRAPH_CAPTION_EDGE_CLEARANCE,
    )
  ))) return false;
  if (geometry.placedBoxes.some((placed) => boxesIntersect(box, placed))) {
    return false;
  }
  return geometry.positions.every((other) => (
    other.id === geometry.nodeId
    || !boxIntersectsCircle(box, other, GRAPH_NODE_RADIUS)
  ));
}

export function svgNodeLabelPresentation(
  label,
  x,
  y,
  viewWidth,
  viewHeight,
  direction = "ltr",
  geometry = null,
) {
  const margin = GRAPH_NODE_RADIUS + GRAPH_APPROX_CHAR_WIDTH;
  let availableWidth = 2 * Math.min(x, viewWidth - x);
  if (x <= margin) {
    availableWidth = viewWidth - (x - GRAPH_NODE_RADIUS);
  } else if (x >= viewWidth - margin) {
    availableWidth = x + GRAPH_NODE_RADIUS;
  }
  const text = shortLabel(label, maxLabelCodePoints(availableWidth));
  const textWidth = [...String(text)].length * GRAPH_APPROX_CHAR_WIDTH;
  let baseDx = 0;
  if (x <= margin) baseDx = textWidth / 2;
  if (x >= viewWidth - margin) baseDx = -textWidth / 2;
  const belowDy = Math.min(
    GRAPH_LABEL_DY,
    Math.max(
      GRAPH_LABEL_LINE_HEIGHT,
      viewHeight - y - GRAPH_LABEL_LINE_HEIGHT,
    ),
  );
  const offset = GRAPH_NODE_RADIUS + GRAPH_CAPTION_EDGE_CLEARANCE;
  const sideDx = offset + textWidth / 2;
  const candidates = [
    { text, textAnchor: "middle", dx: baseDx, dy: belowDy },
    { text, textAnchor: "middle", dx: baseDx, dy: -offset },
    { text, textAnchor: "middle", dx: sideDx, dy: GRAPH_LABEL_LINE_HEIGHT / 2 },
    { text, textAnchor: "middle", dx: -sideDx, dy: GRAPH_LABEL_LINE_HEIGHT / 2 },
    { text, textAnchor: "middle", dx: sideDx, dy: belowDy },
    { text, textAnchor: "middle", dx: -sideDx, dy: belowDy },
    { text, textAnchor: "middle", dx: sideDx, dy: -offset },
    { text, textAnchor: "middle", dx: -sideDx, dy: -offset },
  ];
  if (!geometry) return candidates[0];
  const point = { x, y };
  const view = { width: viewWidth, height: viewHeight };
  return candidates.find(
    (candidate) => candidateIsClear(candidate, point, view, geometry),
  ) || candidates[0];
}
