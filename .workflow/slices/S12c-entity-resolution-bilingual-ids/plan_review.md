# Plan review — S12c (plan attempt 1)

**Subject:** `.autonomous-workflow/plans/s12c-entity-resolution-bilingual-ids/cycle-1/plan-1-dispatch1.json`, SHA-256
`6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd` (immutable copy of the planner's completed file).
**Supervisor (owner lead agent, claude-fable-5.1) material review — 2026-09-12:** no B1–B7 finding. Independent plan review by
`reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: no conflict with Core 04 §2.4/§4, Core 05 §6.5, Core 08 §10 (deterministic identifiers, exact document evidence, reviewer approval for
  ambiguity, time-versioning) or the Manifest; frozen snapshots are read-only inputs; no engine consumption.
- B2: spot-checked the plan's evidence claims against the stored records — `DOC-PRODUCER-UNICOIL-70151205e3a4-1762d53d6cab` p4 l4 "UNICOIL
  (Universal Metal Coating Company) was established in 1997…", p4 l12 "…became a 100% Saudi-owned company in 2004…", p4 l13 "…industrial cities of
  Al-Jubail and Jeddah, its five production lin…"; frozen snapshot producers `['UNICOIL','Hadeed']` and `['SABIC','Advanced Petrochemical','Tasnee']`.
  All present as claimed; nothing invented.
- B3: frozen-oracle proof commands [4], [5], [6], [7], [8], [9], [14], [17], [24].
- B4: ADR-018 (T7) precedes the single generation (T9) with [14] immediately after; §11 mirror named; authority path set grows by exactly the new rule table.
- B5: named RED tests per step; boundary tests as doubles refused under the repository root; the real artifact pinned read-only by a test.
- B6: no credentials, no network, no `.env`; the personal name embedded in the 1997 sentence is deliberately not harvested (OD-7).
- B7: no engine/screening/graph/UI/AI consumption; `pipeline.py`, `documents/**`, `connectors/**`, `pyproject.toml`, `uv.lock`, `ci.yml` byte-identical.

## Owner rulings (delegated authority; recorded locally in `.autonomous-workflow/owner-decisions/20260912-s12c-plan-1-rulings.md`)

OD-1…OD-8 ACCEPTED as proposed (see `plan.md`). Rationale highlights: the mention-list design mirrors the S12b DocumentList precedent and keeps
every link traceable to a verbatim span; SASO is a standards authority, not one of the four scope types; short frozen-snapshot labels are
governed evidence and mint stable ids with legal names left unresolved rather than guessed.

## IAC (transferred, not rejections)

- IAC-1 `scripts/reconstruct_snapshot.py` prints any PASS line only when snapshots, documents and entities all pass (s12b lesson; DD-9 already states it);
  the pre-existing tamper tests stay unchanged.
- IAC-2 Byte identity verified at T10 for `pipeline.py`, `documents/**`, `connectors/**`, `data/documents/**`, `data/raw/**`, `pyproject.toml`, `uv.lock`.
- IAC-3 The builder verifies every mention span verbatim against the stored line / JSON value and refuses the whole build on any mismatch
  (nothing written); the T5 log records the exact `make build-entities` command and the EntityBuildReport.
- IAC-4 The artifact id (`ENTITIES-<recorded_on>-<hash12>`) and content are deterministic across two process invocations (test) and the artifact is
  byte-reconstructible under default manifest checking after T9.
- IAC-5 Candidate identity at T10 by the IAC-6 procedure of S12a/S12b (slice records excluded); the implementer prints every verification command
  from the JSON before running it and records index + command + output.
- IAC-6 ADR-018 records that `config/entity_resolution.v1.yaml` is a new §7.3 authority file (path set 16 → 17) and the single manifest run receipt.
- IAC-7 A pre-existing acquisition or engine test may not be edited except for plan-authorized pin moves listed in `files.modify`.

### Independent plan review — `reviewer-grok` (cursor-grok-4.6-xhigh), 2026-09-12: APPROVE, zero findings, six advisories

Record: `.autonomous-workflow/evidence/s12c-entity-resolution-bilingual-ids/plan-1-review.json`. The reviewer verified the plan hash, ten-plus
baseline facts, all 38 real mentions verbatim at their addresses (and the deliberate omissions), the JSON pointers into the frozen snapshots, the
authority hashes and the frozen-scope reproduction. **State: `PLAN_APPROVED`** (decision D-0001 in the slice decisions ledger).

Transferred advisories (IAC):
- IAC-8 (A-01) T3 GATE: run [3] without `tests/test_entity_resolution_cli.py` until T4 creates it (builder + boundaries + existing acquisition suites at T3).
- IAC-9 (A-02) `ENTITY RECONSTRUCTION PASS` contains the substring `RECONSTRUCTION PASS`: print all three PASS lines only after snapshots, documents and
  entities succeed; none on any failure; byte-identical tamper tests untouched (reinforces IAC-1).
- IAC-10 (A-03) `plant_subject_window_lines` is inclusive (`abs(delta) <= 2`); M-009 (delta 2) stays pinned `LOCALITY_VARIANT` as DD-14 states.
- IAC-11 (A-04) Compare the exact-normalised span with the exact-normalised locality `canonical_en` (a literal `'Al-Jubail'` would mint zero plants).
- IAC-12 (A-05) Expand the 38 compact mention strings into full DD-6 JSON (full document ids, 1-based indexes, verbatim spans) before `make build-entities`.
- IAC-13 (A-06) Verification [19] is a multi-line `python -c`; preserve its newlines when printing/running from the JSON.

### Owner decision on the implementer seat (OD-9, recorded locally)

The ladder starts at `implementer-sol` (gpt-5.6-sol-max) for s12c instead of `implementer-composer`, for cause: in s12b composer needed three slots
(one incomplete, two corrected by supervisor and reviewer findings) while the Sol seat found three latent record-contract defects and delivered the
approved candidate. The configured models are unchanged; only the starting rung is chosen on evidence. Independent reviewer: `reviewer-grok`.

### Environment note before implementation (owner lead agent, 2026-09-12 ~10:58Z)

`implementer-sol` stopped at T0 because plan oracle [6] counts every untracked path under the frozen roots and found the ignored bytecode file
`browser_tests/__pycache__/harness.cpython-312.pyc` (created by an earlier browser-test run whose interpreter did not honour the bytecode prefix).
As in S12a's T0, the supervisor relocated all repository `__pycache__` directories intact to `/tmp/ior-s12c-bytecode-recovery/` (no tracked or
untracked product file touched); [6]-style and [5]-style checks then pass (`FROZEN_ROOTS_UNCHANGED`, `S11_S12A_S12B_BYTES_UNCHANGED`). Every seat
keeps `PYTHONPYCACHEPREFIX` outside the repository (the `make` targets inherit it).

#### Cache relocation — before/after evidence (owner lead agent)

- Before (implementer-sol T0 report, 2026-09-12 ~10:55Z): plan [6] exited 1 — `git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests`
  listed `browser_tests/__pycache__/harness.cpython-312.pyc` (ignored bytecode; no tracked drift); [0] `BRANCH_OK`, [5] and [7] passed; integrity PASS;
  reconstruction 1/4 and 12/12; no edits, no manifest run.
- Action (owner lead agent, ~10:58Z): `mv` of every repository `__pycache__` directory to `/tmp/ior-s12c-bytecode-recovery/` —
  `browser_tests/__pycache__`, `src/ior_mvp/acquisition/documents/__pycache__`, `src/ior_mvp/acquisition/connectors/__pycache__`,
  `src/ior_mvp/acquisition/__pycache__`, `src/ior_mvp/__pycache__`, `scripts/__pycache__`, `tests/__pycache__` (contents preserved; nothing deleted).
- After: `git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- …)"` →
  `FROZEN_ROOTS_UNCHANGED`; `git diff --quiet HEAD -- data/raw data/documents data/snapshots/partners config/acquisition_sources.v1.yaml && …` →
  `S11_S12A_S12B_BYTES_UNCHANGED`; `git status --porcelain` showed only the untracked slice-record directory; the implementer's rerun of [6] printed
  `FROZEN_ROOTS_UNCHANGED` (implementation_log.md T0 note). All seats run with `PYTHONPYCACHEPREFIX` outside the repository thereafter.

#### Owner acceptance run on candidate `c2370180…` (owner lead agent, 2026-09-12 11:46Z)

`make ci` (UV_OFFLINE=1) exit 0: scanners PASS; `INTEGRITY PASS`; scenario validation PASS; `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`,
`DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`, `ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)`; `2027 passed, 1 warning`; `SMOKE PASS`;
browser preflight PASS; `118 passed` functional; `4 passed` visual. Log kept locally (`/tmp/s12c-owner-make-ci.log`, copied to
`.autonomous-workflow/evidence/s12c-entity-resolution-bilingual-ids/owner-make-ci-slot-1.log`).
