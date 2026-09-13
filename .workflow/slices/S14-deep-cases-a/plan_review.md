# Plan review — S14 decomposition-1 and plan-1-s14a (attempt 1)

**Subjects:** `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/decomposition-1.json` (SHA-256 `48741467…`), `plan-1-s14a.json` (`8fbfa4e6…`) and amendment `plan-1-s14a-amendment-1.json` (`8c61a0a2…`, precedence AM-1 > plan-1), authored by `planner-fable` against `main` `ab6211f`. Mirrors: `decomposition.md`, `plan.md` in this folder.
**Supervisor (owner lead agent) material review — 2026-09-13:** no B1–B7 finding. Independent review by `reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: no authored public field — capability stays `U`/UNAVAILABLE without a verified verbatim span (SC-3); the engine proof states the expected state but never forces it (SC-2b stop); no synthetic marker in any public artifact (SC-4); thresholds untouched (SC-9 — only `product_families` and `acquisition_sources` may change); both public goldens and the frozen roots untouched in s14a (SC-1/SC-2a); one `build_manifests.py` run (SC-7); the §7.3 changes are owner-ruled (PR-1, OD-3, OD-11) with methodology-cited basis text; the retention rule keeps the frozen screening snapshot reconstructible (OD-4).
- B2: the planner recomputed the selection inputs from the real screening and universe snapshots (all family lines in `likely_false_positive`; 4,542/5,443 continuity flags; tiers; 2024 values and net weights; the UNICOIL GL/PPGI titles and the absence of a nameplate span) and verified the four couplings with file/line — reviewer to recompute.
- B3: exact oracles — pinned selection list per ruled variant, family/version tests, history-resolution negative tests, brief validators, engine proof (`INVESTIGATE`, route null; stop otherwise), reconstruction case pass, manifest oracle, portability copy, `INTEGRITY PASS`, goldens by direct `analyze`.
- B4: Manifest §7 mapping complete — §7.3 `product_families` 1.0.0 → 1.1.0 (fabricated aluminium; `technical_plastics_conversion` 3917/3920/3921) and `acquisition_sources` 1.3.0 → 1.4.0 (four producer sources + `wco_hs_nomenclature`), `config/history/**` retained bytes enumerated; §7.4 Core 02/04/05/09; §7.5 new raw runs, document lists/records, `mentions-v2` + entity artifact, optional WITS partner snapshot, `data/cases/{selection,briefs}/`; exactly one run after all governed text; §11 mirror.
- B5: RED-first tests named per task; ordering fixed by AM-1 C-3 (T1a code on doubles → T2 families → T1b real run and pin); windows recorded before execution; briefs built and proven before any manifest run.
- B6: robots/terms consultation first with bodies not stored; no bypass of walls or TLS failures (SC-5, PR-4/PR-5); RawStore budgets (SC-6); WITS window bounded (MAX_REQUESTS=6) and the 2026-09-03 partner snapshot untouched; the Comtrade key is not involved.
- B7: OUT respected — no portfolio, scenario, golden, visual or frozen-root change in s14a; no pharma/fertilizers; no route 8.

## Owner rulings (local record `.autonomous-workflow/owner-decisions/20260913-s14-plan-1-rulings.md`)

OD-1, OD-2, OD-4…OD-10 ACCEPTED as proposed. OD-3 ruled as an extension (technical plastics conversion headings 3917/3920/3921, Manifest §10 reading from the methodology's profile row). OD-11 ruled to exclude the residual catch-all 3921.90 through a governed `identity_exclusions` table so the rule selects 392010; 760429 retained (solid vs hollow alloy profiles — clear identity). Resulting default cases: coated steel 721061, 721012; fabricated aluminium 760711, 760429; technical plastics 392010 (runner-ups recorded).

## IAC (transferred to the implementer)

- IAC-1 Every operator window's parameters, robots/terms facts and rationale are logged before execution; RunReports pasted verbatim; any non-200, wall or TLS failure recorded as UNAVAILABLE with the observed fact, never retried around.
- IAC-2 The `identity_exclusions` table and every selection key are data rows in the hashed term/rule files with reasons; the pinned list is the output of the rule run, never a hand edit; the run is recorded with its inputs' hashes.
- IAC-3 No ledger figure is used as evidence; capability states, nameplates and product facts come only from stored verbatim spans with page/line addresses; otherwise `U`/UNAVAILABLE.
- IAC-4 IAC-6 identity as before (both S14 slice-record folders excluded when they exist; deleted paths encoded `sha256: null`); `PYTHONPYCACHEPREFIX` outside the repository; no absolute path in any governed artifact; deterministic (sorted) selections in tests.
- IAC-5 `make ci` exit 0 and the portability copy check before hand-off; exactly one manifest run with the oracle immediately after.
- IAC-6 The honest outcome of each built brief is recorded even when it differs from the expectation (stop, reassess, record for s14b) — no input may be adjusted to reach a state.

### Independent plan review — `reviewer-grok`, 2026-09-13: APPROVE, no B1–B7 findings — PLAN_APPROVED

Subject hashes matched. The reviewer verified the four couplings in code and independently recomputed from the frozen screening and universe snapshots: coated steel 721061/721012, aluminium 760711/760429, the viability exclusion of 721070 (no 2024 net weight), the continuity count 4,542/5,443 and — under OD-11 — plastics 392010 with 392190 excluded (`RESIDUAL_CATCH_ALL_SUBHEADING`; runner-up 391739) and 760429 kept. Public INVESTIGATE is a derived engine expectation guarded by SC-2b, not an authored field; s14a leaves the frozen roots and top-level `src/ior_mvp/*.py` untouched; one manifest run is planned. Binding overlay for the implementer (IAC-7): OD-11 replaces AM-1's 392190 oracles via a hashed `identity_exclusions` row and a re-run of the rule (W-P list and briefs follow `SAU-H6-392010`) — not a `--demote-residual` flag and not a hand edit of the list. Record: `.autonomous-workflow/evidence/s14-deep-cases-a/plan-1-review.json`.
