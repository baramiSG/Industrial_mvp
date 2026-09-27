// Deterministic fan-out for repeated relationships between the same two nodes.
// Every route keeps its own source and target circle trim and visible middle lane.
export function repeatedEdgeRoutes(edges, byId, radius, markerClearance, direction = "ltr") {
  const groups = new Map();
  for (const edge of edges) {
    const key = [edge.source, edge.target].sort().join("\u0000");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(edge);
  }
  const routes = new Map();
  for (const group of groups.values()) {
    if (group.length < 2) continue;
    const ordered = [...group].sort((left, right) => (
      left.id < right.id ? -1 : left.id > right.id ? 1 : 0
    ));
    const canonical = [ordered[0].source, ordered[0].target].sort();
    const first = byId[canonical[0]];
    const second = byId[canonical[1]];
    const dx = second.x - first.x;
    const dy = second.y - first.y;
    const length = Math.hypot(dx, dy);
    if (!Number.isFinite(length) || length <= radius * 2 + markerClearance) {
      throw new Error("GRAPH_EDGE_GEOMETRY_INVALID");
    }
    const orientation = direction === "rtl" ? -1 : 1;
    const normal = { x: -dy / length * orientation, y: dx / length * orientation };
    ordered.forEach((edge, index) => {
      const source = byId[edge.source];
      const target = byId[edge.target];
      const lane = (index - (ordered.length - 1) / 2) * 22;
      const bend = (t) => ({
        x: source.x + (target.x - source.x) * t + normal.x * lane,
        y: source.y + (target.y - source.y) * t + normal.y * lane,
      });
      const nearSource = bend(0.40);
      const nearTarget = bend(0.60);
      const startLength = Math.hypot(nearSource.x - source.x, nearSource.y - source.y);
      const endLength = Math.hypot(target.x - nearTarget.x, target.y - nearTarget.y);
      const start = {
        x: source.x + (nearSource.x - source.x) * radius / startLength,
        y: source.y + (nearSource.y - source.y) * radius / startLength,
      };
      const end = {
        x: target.x + (nearTarget.x - target.x) * (radius + markerClearance) / endLength,
        y: target.y + (nearTarget.y - target.y) * (radius + markerClearance) / endLength,
      };
      const points = [start, nearSource, nearTarget, end];
      const segments = points.slice(1).map((point, segment) => ({
        source: points[segment], target: point,
        terminal: segment === points.length - 2,
      }));
      routes.set(edge.id, { points, segments });
    });
  }
  return routes;
}
