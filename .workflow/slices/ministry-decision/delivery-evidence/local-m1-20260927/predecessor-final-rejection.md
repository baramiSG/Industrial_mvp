**Verdict: REJECT, not READY_FOR_CI.** Every required gate now passes, and B1 and B2 are closed. But the final artifact contains one new material correctness defect in per-producer graph attribution for real named companies.

**Subject:** `final-candidate-replacement-2/proof`, commit `241e4dfd935bee8017c147a0ee65f9308c4a4a19`, tree `fe98722cba6539514772d9009a4db4e1ccbe835b` (verified read-only, clean). Graph is `GRAPH-SAU-2026-09-12-c9841fe8e850` / `ENGINE-941521e7a5e5`.

## Material finding M1: PP public producers are wrongly marked "not same process family"

- **Where:** `src/ior_mvp/graph/projection.py`, in `public_producer_adjacency` (around lines 1899–1955), computes each producer's R9-S input as `"same_process_family": (family == sector ...)`. That compares the producer's recorded `process_family` with the case's `sector_profile`, which is a different vocabulary.
- **Why steel passes and PP fails:**
  - Steel: producer family `coated_steel` equals sector `coated_steel`, so it's correct by coincidence.
  - PP (`SAU-H0-390210`): all three producers are recorded as `polypropylene` (`data/snapshots/public/SAU-H0-390210.json` `domestic_capability.producer_evidence`), but the sector is `technical_plastics`, so all three compute as false.
  - The snapshot's case-level `same_process_family` is true. The governed family for HS 3902 is `polypropylene_primary_forms` (`config/product_families.v1.yaml`).
  - I scanned every public case. Only PP is affected; no other public snapshot has producer evidence.
- **Actual output in the frozen artifact (`c9841fe8e850` public `ADJACENT_TO` → `SAU-H0-390210`):**
  - `COMPANY-f2d406af94a8aac1` (SABIC): `same_process_family: false`, `fired: false`, `qualifying_signal_count: 1`, `NO_DEFENSIBLE_SIGNAL`, even though it solely owns an `adjacent_output` signal (`P-SABIC`).
  - `COMPANY-0f8e69531f415144` (Advanced) and `COMPANY-f3a50c477f158420` (Tasnee): `same_process_family: false`.
- **The feed proof records this as a change from delivered F** (`final-reference-feed-proof/comparison-summary.json` `changed_adjacency_metrics`): `same_process_family` true→false and `fired` true→false. That delta isn't source-backed. The approved contract admits only "exact source-backed" producer-row deltas and "no false adjacency" (DISCOVERY-GRAPH-CONTRACT; DOMAIN §4).
- **Consequence:**
  - The governed graph, the graph API (`/views/adjacency`) and the future live Aura mirror would state that Saudi Arabia's principal PP producers don't operate in the polypropylene family and that SABIC fails the R9-S screen. That would be published about real companies.
  - The M-A3 helper's per-producer equality check would faithfully copy the error to Aura.
  - It doesn't change the public REJECT decision or the separate reference ledger (fired / 2 signals / unchanged). The browser UI doesn't print these fields; the edge detail shows only the owned signals.
- **Required correction (bounded, same writer, no new framework):**
  1. Derive per-producer `same_process_family` from the governed family of the opportunity (`family_for_hs6(opportunity hs6)`), using an exact, finite, reviewed mapping of the recorded producer family labels (`coated_steel`→`coated_steel`, `polypropylene`→`polypropylene_primary_forms`). Root records it as a bounded amendment under the existing governed-family membership rule. Where a label can't be mapped exactly, emit UNKNOWN/null. Never infer `false` from a vocabulary mismatch.
  2. Add focused regressions:
     - PP: all three producers same-family true; SABIC fired with exactly one sole-owned `P-SABIC` `adjacent_output` → `ADJACENT_PLANT_WITH_SIGNALS`; Advanced and Tasnee not fired with 0 sole-owned signals, because the shared `core_process` signal is not transferred.
     - Steel: Hadeed and UNICOIL rows unchanged.
     - A mutation with an unmapped label gives UNKNOWN, not false.
     - The reference summary, the four unaffected feeds and all 11 decisions stay unchanged.
  3. Follow the existing generation sequence: stock build, then a semantic-delta inspection limited to those three PP producer edges plus their derived identities, then pins, then capture (expected byte-equal, since there is no PP graph scene; classify any difference), freeze, and rerun the affected gates (pytest/integrity, browser, strict R1, the single graph gate, and the reference-feed replay rebound to the new artifact). The M-A3 bindings are later re-bound to the delivered subject.

## Closed findings and completed gates (direct inspection of receipts)

- **B1:** closed. `final-checks-replacement-2` PASS: 4184 pytest passed, all nine commands.
- **B2:** closed.
  - `final-browser-replacement-2/RESULT.json`: PASS, exit 0, stderr empty, `source_changes: []`, ordinary index unchanged. `stdout.log` (`10939613…`) shows functional **881 passed, 8 deselected** and visual **8 passed, 881 deselected**, with no F, s, x or E markers.
  - `graph-gate-replacement-1`: gate exit 0, 9 passed with 1 skip (the Aura-only test), graph-UI and unavailable-state tests passing, and all-view equality now passing. Exact 42216/461bf restoration, 64 indexes, PID 34210 and the lock preserved.
  - `r1-execution-replacement-2`: PASS.
  - `canonical-capture-replacement-4`: 140/140 images byte-equal, and the manifest delta is only the two helper hashes.
- **G1.3:**
  - The two-file test diff matches the approved plan:
    - exact direct-child structure with count equality;
    - role, tabindex and the exact governed name;
    - overflow auto or scroll;
    - wrapper inside the panel;
    - reachable extent computed with RTL in mind;
    - full original bounds kept for everything else.
  - Nine reversible negatives restore the exact state.
  - The one-literal baseline pin is `9dea0ee0…`.
  - Conditions 1–3 are met. Condition 4 (disclosing the heap override) is for the publication records.
- **Reference-feed replay:** PASS. 88/88 feed slots, zero reference-ledger or projection mismatches, F probe byte-identical, two-line probe diff. This is the receipt that exposed M1.
- **Clarity:** the Astra Max EN/AR assessment (`283eec7f…`) and my own earlier rendered observations remain valid for the unchanged product and images. M1 lies outside the rendered text.

## Nonblocking (tracked, no scope expansion)

- The candidate-fact passport notice in the graph drilldown reads as "unavailable".
- One G1.3 negative matches a generic `role` substring.
- Terminal arrowheads converge in fan-outs; one pre-existing unique edge passes behind a node.
- The graph gate writes its local credential file inside the proof root.

**Evidence basis:** directly inspected (read-only) — proof identity, the complete browser receipt and stdout, the G1.3 diff, the graph-gate and capture receipts, the feed-proof files, the projection code, the frozen artifact edges and the snapshot and config values. Relied on root's executions. Pending and separate: hosted CI's six jobs, merge and green main, and M-A3 live Aura.

**Muhasabah: PASS.** M1 is established from actual artifact values, source code and governed config, not inferred.
