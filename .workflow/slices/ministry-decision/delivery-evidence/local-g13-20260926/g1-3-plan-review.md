**Verdict: APPROVE G1.3**, plan SHA-256 `36410d008a43ceff1514a7253536e9666dc0353df1da2f91eb9989ed7d18a169`. This approves the plan only, with four binding conditions below. It does not approve the implementation, the retry outcome or READY_FOR_CI. Everything was read-only: no tests, writes, services or Aura.

## A. Scoped-table containment oracle

**The diagnosis matches the actual traces.** I decoded the failing `evaluate` results in both `…narrow-panel…-steel-390-{en,ar}/trace.zip` files.
- Every element flagged outside the panel is `table.graph-source-table` or one of its descendants (TBODY, TR, TD, the technical-token `bdi` and its text):
  - EN: table spans x = 80..400;
  - AR: table spans x = −10..310;
  - the panel's inner bounds are 63..327 in both.
- The `.card-body-scroll` wrapper itself is not flagged, so it sits inside the panel.
- `documentOverflow` is false.

This is intentional horizontal scroll content from the approved G1 focusable region, which I judged usable earlier. It is not uncontained content. The existing helper already exempts the scrolling `.graph-visual svg` region (`graph_pages.py:396`), so a narrowly guarded exemption for one scroll region follows established precedent.

**The amendment preserves containment rather than weakening it:**
- It recognizes only the exact direct-child structure `.graph-details > .card-body-scroll > table.graph-source-table`.
- The wrapper must be a native region: `role=region`, `tabindex=0`, a nonempty governed accessible name, computed overflow of auto or scroll, and a visible box fully inside the panel.
- Everything outside the table keeps the original panel, text and document-overflow checks, with the unchanged 1 px tolerance.
- The real Tab / focus-visible / arrow-key test to both endpoints and back in EN and AR, plus axe, is retained.
- Reversible negative controls are required: inaccessible tabindex, hidden or clipped overflow, a wrapper outside the panel, and genuinely overwide non-scroll text.
- Product bytes are unchanged, and the capture must be re-run and classified.

**Binding conditions:**
1. **Close the exemption.**
   - The number of recognized wrappers must equal the number of `.graph-source-table` elements present. Any source table outside the exact recognized structure must fail.
   - Each table descendant must lie within the wrapper's reachable horizontal scroll extent, computed with RTL's negative `scrollLeft` in mind, not merely within the table's own box.
   - Add two negatives: role removed, and empty accessible name.

## B. Bounded local graph-gate retry

**What the evidence establishes.**
- Neo4j `debug.log` records `VmPauseMonitor` pauses of 789 ms, then a 5,417 ms stop-the-world pause (gcTime 5,557 ms) ending 21:27:26.921Z. That exceeds the unchanged 2 s Bolt deadline and explains the handshake timeout in `test_views_equal_artifact`.
- The heap bounds were not configured: the max heuristic was 23.58 GiB and the initial heuristic 1.59 GiB.
- Recovery (`recovery-g1-continuation/RESULT.json`) is PASS: the same container 42216eec…, the original 461bf projection, and 58 protected indexes.

**What it doesn't establish.** It doesn't show that the unbounded heap heuristic *caused* a 5.4 s GC on a 160 MiB heap.
- The "Free Physical memory 1.318GiB" line is page-cache accounting. `free` shows about 84.8 GiB available.
- Memory PSI shows full avg60 ≈ 2.59.
- The failed gate ran from 21:26:53 to 21:27:31, while the full browser suite, started at 21:22:45, was running concurrently.

So host contention or memory reclaim is a plausible co-cause. Setting initial and max heap to 1G each (the Neo4j documentation recommends configuring both explicitly) is reasonable hygiene, but it is a mitigation, not a proven fix. The plan correctly avoids claiming OOM or guaranteed success.

**Binding conditions:**
2. **Isolate the single retry.** Run it only after the full browser suite, and any other heavy owned job, has exited. Record host `free`/PSI before and after, plus the retry's Neo4j `VmPauseMonitor` lines, as receipts.
3. **Keep the retry bounded.** Change only the two heap values in an external override. Keep:
   - the pinned 5.26.30 image;
   - 512 MiB pagecache;
   - the 2 s application timeout with no retry;
   - all stock tests and assertions;
   - the identity, reader, index and PID guards;
   - the one-SIGTERM stop;
   - exact retained restoration and old-graph verification, even if the test fails.

   If a pause recurs, stop and report. Don't make an equivalent repeat attempt.
4. **Disclose the setting.** Record in the gate receipt and publication records that the local gate used this external heap override. Hosted CI's stock configuration remains the required check.

## Preserved

- All v3.1 and G1/G1.1/G1.2 requirements.
- The 320 px table minimum and 90 px narrow scroll, which I judged usable.
- Strict R1 and the whole M-O = F-N comparison.
- Zero actual failures before publication.
- The completed full browser run must be classified in full; the two 390 failures are not assumed to be the only ones.
- The clarity method stays Astra Max plus this review, with no human or Ministry endorsement.

## Evidence basis

- **Directly inspected:** the plan hash; both failing trace payloads; the current helper code; the Neo4j log diagnostic; host memory and pressure snapshots; the recovery RESULT; the gate and browser timing records.
- **Uncertain:** the root cause of the pause (heap heuristic versus contention); the remaining browser failures, since the run is still going; whether the retry will pass.

**Muhasabah: PASS.** The approval rests on the trace-verified failure mechanism and the recorded GC and timing evidence. Unproven causes are labelled as such, and no gate result is claimed.
