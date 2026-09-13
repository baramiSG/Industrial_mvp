# Plan review — s14b plan-1 (attempt 1)

**Subject:** `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14b.json` (SHA-256 `af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2`, 221,683 bytes), authored by `planner-fable` against `ab6211f` for the isolated worktree `/home/barami/projects/ior-worktrees/s14b`; mirror `plan.md` in this folder.
**Supervisor (owner lead agent) material review — 2026-09-13:** no B1–B7 finding. Independent review by `reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: public snapshots are builder output from committed briefs — any byte not reproduced by the merged builder is a stop (SC-3); no synthetic marker in any public artifact or view and no `real_decision` change after simulation (SC-2); the two original cases' goldens protected (SC-1); scenarios under contract 2.0.0 with Gate B and planted ground truth, each designed outcome reached by computation on the first dry run without tuning and a redesign treated as a new scenario version (SC-4); MONITOR not manufactured (OD-2); thresholds untouched; one manifest run (SC-7); frozen roots change only through the owner-lead WIP commits.
- B2: the planner rebuilt the five briefs with the in-flight builder (hashes equal to the s14a log), ran the public engine, verified MONITOR unreachability per case, and dry-ran the five scenarios through contract validation, Gate B, `simulate` and the back-test — figures are computed, provisional until merged main (T5/T6 re-run them).
- B3: exact oracles — `SCENARIO VALIDATION PASS (7 scenarios)`, `CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)`, goldens by direct `analyze`, `harness.CASES` = 7, `VISUAL_MANIFEST_OK 76`, frozen-tree OIDs recomputed from a temporary index, functional journeys 7 cases × 2 modes × 2 locales, the observed / missing / Class-D distinction test, portability copy.
- B4: Manifest §7 mapping complete — §7.5 `data/snapshots/public` (+5) and `data/synthetic` (+5); §7.3 `config/project.yaml`; §7.4 Core 07 §7.8/§7.9 and Core 09 §2.4/§2.7/§7/§10 (the only authority-hash changes); SLICE_GRAPH §9 rows; frozen pins and `VISUAL_BASELINE_ENTRIES` 76; exactly one `build_manifests.py` run after integration and all governed text.
- B5: RED-first tests (`tests/test_s14b_portfolio.py`, golden appends, harness/journey/accessibility updates) before integration; recordings written before golden assertions are finalised (T6); regeneration (T8) after the integrated functional suite.
- B6: no network; no credential; scenarios never leak into public views (TL-09); the reviewer assesses `git diff M W1'`, `git diff W1' W2` and the uncommitted delta separately (integration_task INT-7).
- B7: OUT respected — no engine/rule change, no route 8, no S15 profiles, no release-script change (OD-11 with a visible S22 backlog item), Core 06 byte-identical (OD-12).

## Owner rulings (local record `.autonomous-workflow/owner-decisions/20260913-s14b-plan-1-rulings.md`)

OD-1 default (public-workspace screens; functional assertions protect the simulated routes; SC-11 stop on budget breach); OD-2…OD-12 accepted as proposed with the notes recorded (OD-8 Arabic drafts marked analyst-authored and reviewed for parity; OD-11 S22 backlog item).

## IAC (transferred to the implementer)

- IAC-1 Bytecode isolation and the isolated worktree venv (`uv venv --python 3.12`; `UV_OFFLINE=1`); never touch the primary checkout.
- IAC-2 Every scenario file states the designed outcome, route and planted ground truth in its basis fields; Arabic narrative drafts are marked analyst-authored; no value is nudged after a dry run — a redesign is a new scenario version with the old one deleted only if never committed.
- IAC-3 Preparation work (T0–T4) may proceed before the s14a merge; nothing under the frozen roots is written until INT-4 (snapshots) and T8 (baselines); scenarios stay untracked until the owner-lead WIP W1.
- IAC-4 The 721061 public view must show the AM-2 tri-state (missing ≠ zero) and every case view must distinguish observed facts, missing evidence and Class-D blocks (owner directive OD-12(c) of s14a); the observed/missing/Class-D distinction test is RED-first.
- IAC-5 Visual regeneration once, in the canonical container, with the measured drift table and crops for the reviewer; predicted drift confined to portfolio/nav regions; SC-5/SC-11 stops honoured.
- IAC-6 IAC-6 identity with `base` = W2, `wip_parent` = M (merged main), canonical serialization with trailing LF; `make ci` exit 0 and the portability copy before hand-off; one manifest run after integration.

### Independent plan review — `reviewer-grok`, 2026-09-13: REJECT (two findings), no B1 block

Hash matched. The reviewer recomputed two of the five scenario designs from the plan in `/tmp` with the in-flight s14a builder (721061 → ADVANCE route 3, `ALL_ADVANCE_GATES_PASS`; 392010 → REJECT route 0, `HARD_EXCLUSION_SATISFIED` EX-04; Gate B PASS; back-tests match) and confirmed MONITOR unreachability against `public_decision.py`. Findings: S14B-C3-NOT-CARRIED (B7) — the plan did not carry the AM-2 C-3 pinned-module obligations that s14a OD-13 deferred to this child (PublicSnapshot 2.2.0 `partner_detail`, `trade_metrics`/R3/R4-D reason codes, dossier labels) inside its single regeneration; S14B-SC9-MISREADS-AM2-C2 (B3) — SC-9/INT-3 would treat a correct AM-2 C-2 merge as failure. Owner ruling OD-13: Option A — carry C-3 and rewrite SC-9 via amendment AM-1; advisories (no nudging, re-record hashes at T6, no manufactured MONITOR, SC-11 headroom ≈ 798 KB, goldens after [21], worktree isolation, s14a overlays) carried. Record: `.autonomous-workflow/evidence/s14-deep-cases-a/plan-1-s14b-review.json`.

### Amendment AM-1 (`8dc1b75d…`) — reviewer-grok re-review 2026-09-13: APPROVE, no findings — PLAN_APPROVED

Both findings closed: additive, version-gated PublicSnapshot 2.2.0 (frozen 2.1.0 files untouched; migrating them would relabel disclosure-backed R3/R4-D as MISSING — rejected), eleven modules plus both catalogues (1.3.0) and Core 04 §12 leave the byte-identical set with named tests, R4-D state-specific result codes (protect frozen ledger rows), `evidence.py` unchanged (no partner logic), SC-9/INT-3 rewritten to accept a correct AM-2 C-2 merge (MISSING or OBSERVED) with the 2.2.0 block produced only by the builder; single T8 regeneration with ~798 KB budget headroom. Binding advisories: accept the AM-3 SUPERSEDED prefix; reason set from the enum; never migrate frozen snapshots; extend the T8 drift table for the new 721061 workspace content; T4b before W1; hashes after INT-4b; five authority rows and one manifest run; builder never by hand. Record: `.autonomous-workflow/evidence/s14-deep-cases-a/plan-1-s14b-amendment-1-review.json`.
