**Verdict: REJECT, not READY_FOR_CI.** The required final gate failed. `graph-open-final-checks/RESULT.json` reports `FAIL_STOP`: 7 commands completed, `failed_command: pytest`, **4197 passed, 1 failed**. The visual compare therefore never ran (`graph-open-visual-compare/RESULT.json`: `NOT_RUN_PREDECESSOR_FAILED`). Source and content review is otherwise clear, and the failure is a stale pin, not a product defect. All actions were read-only: no edits, tests, services, Aura or credentials.

**Subject:** private proof `b25a5a9e17580bdffc35ceee8e2a9525dfdbfb57` / tree `9cab9e90269af8a29af6debafa3d1e78c0f1ac69` (verified clean), differing from RT `d1916ce…` by exactly the seven admitted paths. The external helper `verify_app.py` hash is `cc36e586…`.

## Material finding

**`tests/test_s17_status_docs.py:35` pins the visual manifest's `change_ref`, and the approved capture changed it.**
- The test asserts `visual["change_ref"] == "MINISTRY-M-V3-1-20260926"`.
- The authorized capture wrote `"change_ref": "MINISTRY-M-GRAPH-OPEN-20260927"`, bound to the approved M-G1 plan as the plan required (`canonical-capture-graph-open/RESULT.json`, and the frozen `manifest.json:5`).
- The approved admitted-output list (my correction 1) covered `manifest.json`, `manifest.sha256` and the baseline-tree literal, but missed this existing assertion on the same captured field. It's the same class of stale pin as B1.
- **Fix, bounded, same Sol writer:**
  - Change exactly that one literal to `"MINISTRY-M-GRAPH-OPEN-20260927"`, the actual captured value. Keep every other assertion in that test unchanged: 748 snapshots, 140 entries, and the ADR-027 / S17 text checks.
  - No recapture, since the images and manifest are unchanged. No other test or literal edits.
  - Re-freeze the eight-path candidate, then rerun the full final checks (all 11 commands, exit 0) and then all 8 visual-compare tests on that exact proof.

## Verified directly and clear

- **`graph/index.js`:** `openGraph` is exported with `force=false`. The one-line guard is exactly my binding: `!force && open && !error && sameGraphContext(context, requested) && (loading || payload)`. `sameGraphContext` compares opportunity, mode, view, all four candidate fields and `invalid`. Only Retry passes `force=true`, and manual toggle and close are unchanged. The file is 199 lines, within the cap.
- **`analyst-navigation.js`:** explicit `openGraph()` replaces the toggle; 38 lines.
- **The Retry `force` path is a justified extension of my Retry binding.** `render.js:135` shows a GRAPH_UNAVAILABLE state with a Retry button, a present payload and a null error, which the ordinary predicate would have swallowed. `RED-UNAVAILABLE` reproduced that before the fix.
- **The regression `test_candidate_graph_open_requests_preserve_scope`** has 7 cases in each of EN and AR, 14 in total:
  - the both-flags, retry and manual-reopen cases use the native link;
  - the offline route calls `GraphService` over the saved projection with the parsed four-field context;
  - the held-catalogue nondefault case asserts `adjacency` is never requested and every payload is `evidence_to_change`;
  - the error and unavailable Retry cases assert exactly two adjacency requests;
  - manual close and reopen is covered;
  - it checks exact focus alias, canonical identity, `CANDIDATE_DISCOVERY`, finding membership, Class D, the source table, provenance and no console errors.

  The inventory goes from 96 to 97 with the literal name added.
- **Helper change:** only the existing `wait_graph_request_complete` import and one call after link navigation, with all assertions intact. It changes a GO-bound subject, so the old live GO is void.
- **Capture and pin:** 140/140 images byte-equal, 250 sources with only the two JS hashes changed, identical fonts and metadata. The proof HEAD baselines tree `dfc1b69d…` equals the pinned literal. `GRAPH-CLOSURE.json` shows the graph unchanged: 1248 edges, `fa61…`, current / projection / manifest hashes unchanged.

## Evidence basis

- **Directly inspected:** the proof identity and seven-path delta; both JS diffs; the context and render lines; the test, inventory and pin diffs; the helper diff and hash; the RED/GREEN tails; the capture and baseline receipts; the final-check and visual receipts; the failing assertion.
- **Relied on Sol/root:** executions of RED/GREEN (14 + 9), 115 focused tests, ES 55 and the capture.
- **Unrun:** the corrected full checks and visual compare. The six hosted jobs, merge and main CI, and the unbound live continuation come later.

**Muhasabah: PASS.** The rejection rests only on the actual failed gate, the fix is exact, and nothing that didn't run is claimed.
