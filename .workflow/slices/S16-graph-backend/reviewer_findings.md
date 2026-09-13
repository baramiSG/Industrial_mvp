# Reviewer Findings — S16a Graph Projection, Provisioning and Loader

Reviewer seat: `reviewer-grok` (cursor-grok-4.6-xhigh), independent S16 approver. Review evidence is retained locally under `.autonomous-workflow/evidence/s16-graph-backend/`.

## Plan review

The reviewer approved plan `7e888e7a…` with no B1–B7 finding. It confirmed that:

- public route 8 remains `GRAPH_REQUIRED` until the governed Class-D enabler work in s16b;
- the 19-label/15-edge graph, provenance, projection/mirror boundary and Aura safety preserve the public/Class-D separation;
- required graph functionality is delivered with deterministic artifact computation and Cypher 5, without silently relying on GDS or APOC;
- S16a/S16b split at the visual-pinned runtime seam is valid.

## Implementation review — APPROVE, zero findings

Candidate `040d442d…` matched its 14-path IAC identity. The reviewer recomputed the full M16→W1' plus candidate scope, all six rebase resolutions, current graph `GRAPH-SAU-2026-09-12-3ce241f08f7a` (740 nodes, 835 edges, 219 inputs), historical graph `…941efbdf1e4a`, complete provenance, public/Class-D partition and generated-manifest exclusion from graph identity. It ran 2,676 pytest tests, integrity, smoke, case-selection plus graph reconstruction and loopback graph tests.

## Operational correction review — APPROVE, zero findings

Owner CI found a stopped disposable scratch container with the fixed graph name. The correction made `graph-down` use `docker compose down --remove-orphans` without volume removal. Candidate `79f469dc…` matched the 15-path IAC identity; only the Make target and its contract test changed. The reviewer proved the old test failed, the new one passed, graph cleanup removes the container while retaining the named volume, and the unrelated Postgres workload stays healthy. No Aura, `.env` or secret file was accessed.

The reviewer did not run owner `make ci`; the owner did on the exact corrected candidate and hosted CI ran the complete matrix.

## Delivery-record review — correction round

The first independent review of these eight delivery-record paths rejected two
receipt-only inaccuracies:

1. `.workflow/state.json` named a non-existent `s15b-deep-case-portfolio-pharma-fertilizers` queue item instead of the already recorded
   `s15b-deep-case-portfolio-scenarios-and-goldens`.
2. The `V3-S16-TOOLCHAIN` traceability evidence still said hosted CI was pending despite PR run `34754886672` and merged-main run `34755573206`
   having passed 6/6.

The correction changes only that queue identifier and the stale CI sentence.
It does not alter the merged S16a product, graph evidence, authority manifests,
route-8 boundary or Aura status. The same reviewer correction round returned
**APPROVE, zero findings** before this records branch was committed.
