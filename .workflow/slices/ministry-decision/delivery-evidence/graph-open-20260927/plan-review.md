**Verdict: APPROVE M-G1**, plan SHA-256 `d40ee00e1f3c825cb1dd6039263256087ed1cb29b3c61533da40d6b06c5f34f7`, with four binding corrections. This approves the plan only: Sol's bounded fix, root's single authorized canonical capture, and proportionate verification. It is not the implementation, the canonical result, the live continuation or M acceptance. All actions were read-only; no writes, browser, Docker, Aura or credentials.

## Cause verified directly against the frozen runtime and root's diagnostics

- **Source trace (RT `d1916ce…`), in the order that runs on page load:**
  1. The candidate link carries both `graphView` and `graphOpen=1`.
  2. `mountGraphComponent` (`graph/index.js` lines 177–182) consumes `graphOpen` and calls `void openGraph()`, which synchronously sets `open=true`, captures the epoch and awaits the catalogue.
  3. `workspace.js:70` then calls `openRequestedGraph` (`analyst-navigation.js:31–38`), which sets `viewId` and calls `handleGraphAction(toggle)`.
  4. Because `open` is already true, the toggle calls `resetGraph` → `clearContent`: the epoch increments, `open` becomes false and the context is cleared (`index.js:15–28`, 186–190).
  5. `graphCommitAllowed` (`context.js:63–68`) correctly rejects the first request after the catalogue returns, so `fetchView` never runs.
- **Root's state capture agrees** (`aura-m1-graph-state-diagnostic/RESULT.json`):
  - with both flags: closed, epoch 3, context null, 0 nodes, catalogue 200 only;
  - with `graphView` only: open, epoch 2, scoped adjacency 200 with all four context fields, 17 nodes, one focus button.
- **Live failure** (`aura-m1-live-execution/FAILURE.json`): phase `application`, an AssertionError, state NEW, `schema_equal` true, all indexes ONLINE, children reaped, and no automatic inverse. No data action is needed.
- **Design is sound and correctly scoped:**
  - explicit open instead of a toggle, idempotent only for the same context;
  - a changed view or context opens under a fresh epoch;
  - manual close, lazy open, stale-response and invalid-context guards all kept.
- **Changed files:** two frontend files; one named regression, taking the browser inventory from 96 to 97; the external helper waits with the existing `wait_graph_request_complete`.
- **Projection closure is unaffected.** The graph input groups include only `.py` files, so the two JS modules don't change the projection. They are visual source inputs, which makes the capture necessary.

## Binding corrections

1. **Admitted generated paths are wrong.** `browser_tests/baselines/v0.3.0/baseline-set.json` does not exist; the directory holds only `ar/`, `en/`, `manifest.json` and `manifest.sha256`. The stock capture rewrites `manifest.json` **and** `manifest.sha256`, as the M1 successor delta showed. Admit exactly those two files plus the single baseline-tree literal in `tests/test_frozen_public_evidence_pins.py`. All 140 images must stay byte-equal; any image difference means stop and inspect.
2. **Exact idempotency predicate.** A repeated open may be a no-op only when all of these hold: `state.graph.open`, `!state.graph.error`, `sameGraphContext(state.graph.context, requested)` for the full requested context (view, opportunity, mode and all four candidate fields), and `(state.graph.loading || state.graph.payload)`.
   - Every other case must run a fresh-epoch open: closed, error (so Retry refetches), a different view or context, or invalid.
   - Keep the manual toggle's close behavior unchanged.
   - `graph/index.js` is at 198 physical lines against the enforced 199. The guard must fit readably (one line inside `openGraph` after `requested` is computed, with `export` added in place), or the predicate may live in `analyst-navigation.js` (39 lines). No compressed or hidden logic and no cap change.
3. **The regression must discriminate the two paths.** In the single named parameterized test:
   - **Nondefault view with both flags:** hold the catalogue response. The mount-time open starts on the default adjacency view, so assert that it is superseded: the final committed payload and panel are the requested view and context, and no stale adjacency payload commits after release.
   - **Error then Retry:** both flags followed by an injected view error, then Retry must issue a new view request, proving the predicate never swallows Retry.
   - **Remaining cases:** graphView-only, graphOpen-only, manual close then reopen, EN and AR.
   - **Fixture:** the offline route must parse the four context fields and call the existing `GraphService` over the saved hashed projection, as the checks-prep note requires. Never use a context-free payload or a fabricated focus.
4. **The helper edit changes a GO-bound subject.** `verify_app.py` is hash-bound in the current live packet (`fda4d014…`). Preserve its before-image. Any edit invalidates the existing `BINDING.json` and `DELEGATED-GO.json` subjects, and the continuation must rebind to the corrected merged runtime and new helper hash before any execution release. The plan already states this; it is binding.

## Evidence basis

- **Directly inspected:** the plan; both diagnoses; `FAILURE.json`; the state `RESULT.json`; `analyst-navigation.js` in full; `graph/index.js` in full; the `context.js` guards; the call sites; line counts; the baseline directory listing; the module inventory lines.
- **Root evidence relied on:** the live and diagnostic executions.
- **Inference:** the causal sequence, corroborated by the recorded state and requests.
- **Unrun:** the fix, the red/green results, the capture and the live continuation. These stay subject-bound in this same review.

**Muhasabah: PASS.** The one plan error is concrete and corrected, and no fix outcome is presumed.
