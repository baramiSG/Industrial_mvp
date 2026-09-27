**Verdict: APPROVE G1.2**, plan SHA-256 `62533307db677faac81bdfe6942e248040848098fa5432ceff6a9793ade9944b`. This approves the plan only. It does not approve any implementation, the regenerated graph, test results or delivery. Everything was read-only: no tests, writes, Git changes or services.

**Bindings checked:**
- G1.2 incorporates G1 at `d286c7e4…` and G1.1 at `2a6f02a9…`, and both hashes match the files.
- It cites my G1.1 REJECT (`claude-correction-plan-review-v2/REVIEW.md`) at `0aa61256…`, which also matches.
- The appended diagnosis that defines the ten selectors is at `0f3f39bb…`. Its "Follow-up" section, from line 71, is the ten-row table.

## My three findings: all closed

**1. Steel B's qualification limitation.** Closed.
- Exact `customer_qualification` requirement matching and nonempty exact application equality now apply to both QUALIFIED and NOT_QUALIFIED records.
- An exact-scope NOT_QUALIFIED record stays LIMITATION_IDENTIFIED even when its period `[0,12)` doesn't cover the request `[18,30)`.
- Only positive QUALIFIED support requires the request window to be covered.
- This matches the current `_capacity` logic: KNOWN_ZERO is decided before WINDOW_MISMATCH, and the window result stays a separate field. B keeps 0 kt / KNOWN_ZERO with its window mismatch still reported, as REGISTER §4 requires.
- The required regressions cover:
  - B unchanged;
  - A's `[18,36)` still SUPPORTED;
  - a QUALIFIED record that doesn't cover the request gives NOT_ESTABLISHED;
  - a wrong application gives neither support nor a limitation;
  - a wrong `requirement_id` is rejected by the typed reference contract, not turned into an output state.
- Nonboolean-requirement rejection applies only on the 2.2 candidate-line path. No fixture window, status or allocation may change.

**2. Semantic binding for all ten edge rows.** Closed.
- The appended table binds every artifact-derived and test-only `|edge` key in `PASSPORT_SOURCE_COUNTS`, in table order 10, 0, 2, 2, 2, 3, 2, 2, 6, 2. I counted the same ten keys and literals in `browser_tests/graph_pages.py:405–421`.
- Each selector uses the relation type, stable endpoints (Decision nodes matched by label + `opportunity_id` + mode, never by engine hash), a discriminating property, and the exact evidence and provenance.
- Each must match exactly one edge in both f507 and the actual regenerated successor.
- The existing literal counts are kept. The aluminium public WCO identity edge stays at 3, with a separate route_economics case bound at 0 for the no-passport path.
- The plan states the whole-graph count semantics correctly: simulated contexts without passports keep 2 from the required synthetic disclosures, and public ones are 0.
- The node-selection fallback is removed, ordinal and DOM-derived expectations are banned, and the source/caption-removal mutation must still fail. Service ordering and projection semantics stay unchanged.

**3. Synthetic subtree guard pin.** Closed.
- Exactly five `values.application` leaves change per register, and the two registers must stay byte-identical to each other.
- Every other synthetic member stays byte-identical, including the `v2_0` histories, and the `data/golden` and `data/snapshots/public` tree OIDs are unchanged.
- The new tree OID is computed through a separate external index, and only then adopted in `tests/test_frozen_public_evidence_pins.py`, with all guard and mutation tests kept.
- No new scenario history. The visual subtree pin stays a separate update that is already admitted.

## Conditions carried into implementation review

These are not reasons to reject.
- **Count justification:** before the implementation review, the helper must finish and hash-bind the per-row raw-field justification the plan cites: the selected passport's title, link and support fields, plus the fixed synthetic warning spans. Until then, the literals rest on the prior AM4 enumeration and the existing passing observations.
- **Selector uniqueness:** each selector must be shown unique in the regenerated successor, in the actual browser run.
- **Unchanged G1/G1.1 obligations:**
  - routing proof for up to five edges per pair, with every segment checked and exactly one arrow per relationship;
  - the single `edge-geometry.js` helper under the 199-line cap, with the exact module inventory updated;
  - the focusable scoped-fact region;
  - the exact partition oracle for reference-dossier PDF passports;
  - the P05 selected operand;
  - ADR, then data edits, then the generation and semantic-delta inspection, then pins, then capture, freeze and full gates.

**Scope:** plan review only, limited to the three findings and G1.2's consistency with them. Implementation by the Sol CLI can start. The same Claude review then covers the diff and the successor gates.

**Muhasabah: PASS.** Each closure is checked against the plan text, the appended selector table, the `_capacity` ordering and the literal table. No execution result is claimed.
