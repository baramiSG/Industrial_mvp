**Verdict: not approved, and not READY_FOR_CI yet.** My remaining source and content review is complete with no new blocking findings, and prior finding B1 is closed. Prior finding B2 is still open: the local graph gate failed with exit 2 and incomplete recovery, and the full browser run is still going with one `F` so far.

Personas and skills are as recorded earlier in this review. All actions were read-only against the frozen successor proof, with `GIT_OPTIONAL_LOCKS=0`. No tests, edits, services or Aura.

**Subject verified:** `final-candidate-replacement-1/proof` has HEAD `4f2108ff…` and tree `3436be03…`, matching `BINDING.json` (3,544 files). The current graph is `GRAPH-SAU-2026-09-12-c9841fe8e850`. Pins: synthetic `58cf58e1…`, public `12eace2f…`, golden `72618db6…`, baselines `b1a5bde7…`. The old frozen commit isn't in this clone, so I compared the old and new proof trees file by file.

## Blocking: B2, final gates still open

1. **Local graph gate failed (`graph-gate/execution-g1`).**
   - Credential, `compose up`, wait, clear, load (1160 nodes / 1248 relationships), reload (0/0) and verify all passed on c9841fe8.
   - `graph_tests/test_views_equal_artifact.py::test_view_v1_v4_cypher_equal_artifact_for_every_opportunity_and_mode` then failed: `ServiceUnavailable`, "Failed to read four byte Bolt handshake response" from `127.0.0.1:7688` with the 2 s deadline. Result: 1 failed, 8 passed, 1 skipped.
   - The executor then recorded `RECOVERY_INCOMPLETE` because its own `docker ps -a` failed.
   - Those symptoms point to the Neo4j container or the Docker daemon becoming unavailable, not to a product query mismatch. The equality test never received rows.
   - **Required actions for root:**
     - diagnose and restore Docker;
     - verify the retained container (42216eec…) is restored exactly and that PID 34210 and all unrelated services are preserved;
     - re-run the stock graph gate on the same frozen tree with a new receipt showing exit 0.
   - Don't classify this as product-neutral until the views test actually passes.
2. **Full browser run (`final-browser-replacement-1`)** is still running. At about 8% its stdout shows one `F`, not yet classified. The full functional suite and the canonical compare need a completed `RESULT.json` and a classification of every failure.

**Gates already passed (receipts):**
- `final-checks-replacement-1`: PASS, full pytest 4184 passed, which closes B1.
- `r1-execution-replacement-1`: PASS, with the original strict helpers and whole M-O = F-N equality.
- `canonical-capture-replacement-3`: PASS, runner and wrapper exit 0, 132 images byte-equal and 8 graph images changed, 250 inputs.

## Source and content coverage completed (direct)

- **G1 qualification (`line_comparison.py`, `line_contract.py`)** matches G1.2 exactly:
  - The `"declared"` wildcard is removed.
  - Support requires `requirement_id == customer_qualification`, a nonempty exact application, required `is True`, QUALIFIED status, and window coverage of COVERED.
  - An exact-scope NOT_QUALIFIED record gives a limitation regardless of its window. Steel B stays KNOWN_ZERO / 0 with a separate MISMATCH window result.
  - Literal False gives NOT_REQUIRED. A null or missing requirement or window gives NOT_ESTABLISHED, and the qualification row is always emitted.
  - Nonboolean rejection sits only in the 2.2 `validate_candidate_lines`, and a qualification ref with the wrong requirement is rejected.
  - The regressions are meaningful and include the old wildcard as a negative case.
- **P05 operand** now comes from the selected fact, with a regression that tests both fact orders.
- **Data delta:** exactly five `values.application` leaves per register, the two registers are identical, and there is no other leaf change. This matches the ADR scope.
- **G1 graph interaction:**
  - `edge-geometry.js` (56 lines) fans out repeated pairs at 22-unit lanes using a canonical normal, so reciprocal edges share lanes. It trims to the source radius and to the target radius plus clearance.
  - Unique pairs keep identical geometry.
  - `layout.js` now treats only terminal segments as marker circles.
  - The helper uses real `page.mouse` clicks on an unobscured route point, with exact-ID and native `aria-pressed` agreement. No force or dispatch.
  - The geometry oracle covers every segment: finite and inside the viewbox, connected, trimmed at both ends, exactly one arrow per relationship, a matching hit target, and route IDs equal to the native IDs.
  - The ten semantic count selectors plus the public zero case match the approved table.
  - The scoped table is a labelled, focusable region with visible focus.
- **Graph service context:**
  - Any candidate context in public mode fails closed with a 404.
  - Focus is limited to `CANDIDATE_DISCOVERY` Company, Plant and ProductionLine nodes for the exact scenario and opportunity, with company/plant/line parentage and requirement membership validated.
  - Public expansion admits only producer `PRODUCED_BY` edges, plus `USES_PROCESS`/`CERTIFIED_TO` edges whose evidence is a subset of that producer's adjacency evidence.
- **Executive DTOs:**
  - `candidate_projection` fails closed on scenario or opportunity mismatch and unresolved source pointers. Rows are Class D, sourced from `DEMO_GENERATOR`, with `winner: None`.
  - The frozen models use closed literals.
  - Candidates render only in the SIMULATED_EVIDENCE step when a simulation exists (`simulation.js:21–24`); public mode shows only public producers.
- **`line_contract`:** closed selectors and pointers; fact subject, kind, unit and requirement binding; allocation ≤ formula for new candidates only; ceiling groups reconciled.
- **Renders (viewed directly):**
  - EN desktop evidence-to-change and AR desktop adjacency: repeated pairs are readable, directional and localized.
  - AR/EN 390 px scoped table: the 90 px horizontal scroll is acceptable. It's a keyboard-reachable labelled region holding one technical-ID row, and desktop fits without scrolling.
- **Delegated clarity supplement (`283eec7f…`):** substantive and correctly bounded, with no human or Ministry endorsement. C1–C5 remain closed.

## Nonblocking refinements

1. **Candidate fact references read as missing.** The drilldown for a candidate adjacency edge lists each `…::candidate_fact::FACT-*` as "not available in stored opportunity records" (AR 390 render). That is accurate at passport level, and the scoped table above it lists the same facts. Still, a reader may take it to mean the facts are missing. Consider resolving these references to the `::candidate_register` passport plus the fact pointer.
2. **Unique-edge markup:** unique edges gained `data-graph-source` and `data-graph-target` attributes. Geometry and pixels are unchanged.
3. **Converging arrowheads:** in the four-edge Decision→product fan-out, the terminal arrowheads converge at the target. Direction stays clear and the middle lanes are distinct click targets.
4. **Pre-existing edge overlap:** the unique UNICOIL→certification edge passes behind the Hadeed circle. This predates G1 and is out of scope.
5. **Credential file:** the graph gate writes `.secrets/neo4j_auth.txt` into the proof root. Make sure it is ignored by Git and excluded from preservation comparisons.

## Evidence basis

- **Direct:** proof identity, all G1 source and test diffs, the data leaf delta, service, DTO, UI gating and `line_contract` code, four viewed renders, the gate receipt contents, and the graph-gate stdout/stderr.
- **Agent receipts relied on:** gate executions, the capture and 132/8 equality, the generation and semantic-delta inspection (`SEMANTIC-DELTA-INSPECTION.json`), Sol's handoff test counts, and the clarity assessor's viewing of the other images.
- **Uncertain:** the graph-gate root cause and retained-container state, and the in-progress browser failure. Live Aura, publication, the six hosted checks and S20–22 remain pending and named.

**Muhasabah: PASS.** No gate is reported as passed without its receipt, the running and failed gates are named, and source coverage is complete within the scope stated.
