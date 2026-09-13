# Reviewer Findings — S14a Case Selection, Evidence and Families

Reviewer seat: `reviewer-grok` (cursor-grok-4.6-xhigh), one fresh instance for S14 (plan, three amendments, implementation, CI-fix round). Verdict files (local-only): `.autonomous-workflow/evidence/s14-deep-cases-a/{plan-1-review.json, plan-1-amendment-2-review.json, plan-1-amendment-3-review.json, implementation-review-s14a-slot-1.json}`.

## Plan reviews

- decomposition-1 (`48741467…`) + plan-1-s14a (`8fbfa4e6…`) + AM-1 (`8c61a0a2…`) with owner rulings OD-1…OD-11: **APPROVE**, no findings. The reviewer verified the four couplings in code and recomputed the selection from the frozen snapshots (721061/721012, 760711/760429; under OD-11 392010 with 392190 excluded; 721070 viability; continuity 4,542/5,443). Binding overlay: OD-11 via a hashed `identity_exclusions` row and a rule re-run, never a flag or hand edit.
- AM-2 (`5bccc8a5…`, owner directive OD-12: missing ≠ zero tri-state; Comtrade substitution window): **APPROVE**, ten advisories (unreferenced passport T-12 first; ZERO only on a well-formed `count==0` envelope; non-World counts 42/12/43/27; reason set from the enum; RED before W-C; config/template key names; no pinned-module edit; Case B manifest; no `all` token; selection hash unchanged).
- AM-3 (`6e596932…`, `includeDesc` variant + aggregate reconciliation): **APPROVE**, no findings; the reviewer verified the stored V1 payload (eight rows reconciling exactly to the universe World token; all descriptions null) and ruled R3 firing legitimate only on a COMPLETE observed result.

## Implementation review — identity `78c9b0c6c0085cdc89e303d159a56041b5923fd720b64637ff6829c5009fc6cb` (153 files, base `ab6211f`) — APPROVE, zero findings

Recomputed independently: the selection rule from the hashed inputs (byte-identical `19cb6e4c…`); the corrected V3 payload (8 rows, 7 non-World, unique descriptions, Decimal S = R = 71149266.221); V1 coverage bytes unchanged (write-once) and the defective attempt retained (`includeDesc` absent, `VARIANT_NOT_TRANSMITTED`); WITS 2026-09-12 non-World 42/12/43/27 with 721061 `FORMAT_NOT_PARSEABLE`; the frozen 2026-09-03 WITS snapshot unchanged; no `ocp-apim` in stored contracts; all five briefs `PARTNER_DETAIL_OBSERVED`, SUPERSEDED markers only on 721061; no synthetic marker; the five briefs built to `/tmp` and run through the public engine — INVESTIGATE / null route, 721061 firing {R0, R1-D, R3, R10, R12} (R3 FULL on HHI 0.7122 / largest share 0.8337; R10 DEGRADED because R3 fired) — not forced; goldens unchanged; OD-18 judged an authorized tooling-defect correction; the unplanned `reconstruct_pinned` path does not weaken the default `SELECTION_CHANGED` oracle; Manifest §7 — three receipts (00:25:27Z, 01:15:40Z, 02:28:00Z), 535 base rows unchanged, authority set 19 with six authorized rows changed, history files equal to the superseded `ab6211f` bytes, screening reconstruction PASS; tests — eight removed assertions are version/completeness updates, not weakenings; no absolute fixture paths. Gates run by the reviewer: `pytest -q` 2416, `INTEGRITY PASS`, smoke, reconstruction (4 snapshots/34 artifacts; 20 documents; screening; 5 briefs). Not run by the reviewer: `make ci` (owner ran it, exit 0).

## CI-fix round — identity `89ad2d5cd9a81f1a8d28e0a1ac6f19af35106598db571135d3ee00354cf659de` (2 test files, base `13eeea1`) — APPROVE, zero findings

No CI-guard bypass (quoting asserted via `make -n` plus the Python-level contract capture); the superseded 1.3.0 config pinned by SHA-256 `fbe06149…` equal to `git show ab6211f:…`; no assertion weakened; no remaining `HEAD:` dependency on slice-changed files; CI-equivalent scratch clone with `CI=1`: 2416 passed. The implementer's figure `38e1fed5…` used a short base sha; the canonical figure is recorded.

## Limits

The reviewer did not run `make ci` or the browser suites; the owner lead agent did (exit 0) and hosted CI ran the full matrix on every pushed head.
