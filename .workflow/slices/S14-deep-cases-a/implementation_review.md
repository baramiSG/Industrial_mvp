# Supervisor Implementation Review — S14a Case Selection, Evidence and Families

Reviewer: owner lead agent (Cursor, claude-fable-5.1) as Flight Supervisor and delegated owner. Precedes and does not replace the independent `reviewer-grok` verdicts (`reviewer_findings.md`).

## Seats and rounds

Planner `planner-fable` (decomposition-1, plan-1-s14a, AM-1 OD-3 extension, AM-2 owner directive, AM-3 `includeDesc` variant); implementer `implementer-sol` slot 1 (OD-10 deviation from the configured ladder start, recorded) across the base round, the AM-2 correction, the AM-3 round (stopped correctly under SC-13 when the Make recipe did not quote `&includeDesc=true`), the OD-18 corrected V3 request and the CI-F-01 test fix; reviewer `reviewer-grok` one instance throughout. Parallel mode was active from 2026-09-13 00:25Z: s14b prepared in an isolated worktree, S15/S16 planned, deliveries kept strictly sequential through the single GitHub queue.

## Supervisor checks

- Owner directive OD-12 (missing ≠ zero; equivalent Comtrade query) routed through the reviewed acquisition rules (AM-2 → review → window → AM-3 → review → window); the untransmitted variant was ruled a tooling defect (OD-18) with one corrected request; W-C cumulative HTTP 7 (3 data) recorded.
- Before each gating: identity recomputed (the implementer's first figure lacked the trailing LF; the CI-fix figure used a short base sha — canonical values recorded and records corrected); frozen roots, other configs, existing partner snapshots and top-level modules byte-identical; goldens exact by direct `analyze`; secret scan over all changed/new paths (Comtrade key and Neo4j password literals, header/env patterns): zero hits; absolute-path scan (one URL false positive).
- Unplanned module changes (`acquisition/snapshots.py`, `connectors/base.py`, `connectors/documents.py`, `documents/lists.py`) were required to be justified by RED failures and were reviewed by grok (accepted; the pinned reconstruction path preserves the default oracle).
- Owner `make ci` on the final tree: exit 0 (2416 tests; 152 functional + 4 visual). Pre-push CI-equivalent scratch-clone gate (committed candidate, `CI=1`): 2416 passed — adopted as a standing rule after hosted CI caught two HEAD-dependent test mechanisms that local runs could not.
- Post-merge on `main` `ec859f7`: gates recorded in `pr_record.md`.

## Observations carried forward

- Precision of claims (owner refinement): records say "not identified within the searched sources" and "unverified", never "absent"; exclusions carry the HS revision and verbatim WCO basis; missing years and partner detail are typed states visible to users.
- s14b must carry the pinned-module obligations (PublicSnapshot 2.2.0 `partner_detail`, R3/R4-D reason codes, dossier labels) inside its single visual regeneration (s14b OD-13) and pin the `_scaled` 6-dp reconciliation dependency.
- The Comtrade partner query semantics observed here (partner dimension open → per-partner rows; `includeDesc=true` → descriptions) are recorded as observations, not as documentation facts (KL-80 remains).
