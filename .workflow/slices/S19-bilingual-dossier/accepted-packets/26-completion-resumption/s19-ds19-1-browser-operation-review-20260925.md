# Independent review: S19 literal adoption and browser/PDF operation GO

## Verdict: APPROVE (GO)

**What this approves:**
- The four literal changes in `ROOT-VERIFIED-DELTA.diff`.
- Independent operational GO for the exact six-stage sequence in `BROWSER-PDF-OPERATION-DRAFT-r2.json`, run on the two bound copies.

**Conditions:** GO holds only if the four execution conditions in §4 are met. They make r2's own preflight wording concrete. None of them needs a change to the proposal's bytes.

**What this does not approve:**
- canonical capture, change_ref or pins, R1, the final candidate, CI, GitHub or Aura;
- the `a1dc` alternate branch, which needs its own binding and targeted GO;
- any browser or PDF outcome, since nothing has run.

**Reviewer:** Claude Code (`claude-opus-5-5`), plan mode, read-only. I used only Read/Grep/Bash. No subagents, no tests, no Docker runs, no writes, no plan file. No API-key variable is set in the environment (the grep count was 0).

**Personas:**
- browser-regression / CSS-sensitivity reviewer
- paged-media PDF acceptance auditor
- change-control and provenance auditor

**Skills:** I read and applied project-orientation, task-standards, strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate from `/home/barami/.agents/skills/*/SKILL.md`.

## 1. Bound subjects (hashes I computed; all match)

| Subject | SHA-256 |
|---|---|
| `BROWSER-PDF-OPERATION-DRAFT-r2.json` | `8719ac4238509b6abedf388a57bc473880d1bb4cf92e4e418b710e66ed304262` |
| `POST-LITERAL-SOURCE-BINDING.json` | `c104d456735172817dc356fe17c349c46250de2dc98dd0195952e4f5565d7dc0` |
| `ROOT-VERIFIED-DELTA.diff` | `bf9271c8ea886c9893ec42aba76643c7b84d3eedc6fcffe277e0c6ffee2ec532` |
| `COPY-BINDING.json` | `fb19fd2040d4b6439e05d88a6736122837c11a46bfa4b485d61d4c8266569518` |
| `ORIGINAL-CSS-DELTA.diff` | `3d073380…6f7b56ce7d7e10585a19443304f9cb5573e55a` |
| `replacement-generation/RESULT.json` | `bc011a45…232b9d6d` |
| Source-readiness review / generation GO | `7e78bf3b…7e867` / `faa407e9…201a7` |
| HANDOFF, mandate, routes, assignment, brief, amendment 09 (W copy and source copy) | `281a0134…`, `9b91aba9…`, `fe4e3d1c…`, `ee2316b9…`, `04709fa0…`, `5d058300…` |
| All 5 historical recipes, `HISTORICAL-*`, `SOURCE-SENSITIVITY`, `PDF-COHORT-READY` | match r2's cited hashes |
| `render_pdf.py` / `check_pdf_matrix.py` | `80f17b6f…` / `a68250a4…` |
| `GENERATION-SOURCE-BINDING.json` | `c99cdafa…065b7` |

I read both earlier reviews in full. Their approvals stand unchanged.

## 2. Checks I performed myself

**Literal adoption: APPROVE**
- **Exact reversal.** In each of the four files, the new string occurs exactly once. Reverting only that string reproduces the byte-exact `PRE-WRITER-SOURCE` hash. So nothing else in those files changed: `old_token` is still `ENGINE-7ae34188bdec`, and the S17 historical assertions, change_ref and the 128 count are untouched.
- **Ledger delta.** `PRE-WRITER` → `POST-LITERAL` differs in exactly those four paths.
- **Generation ledger to post-literal.** Going from `c99cdafa` to `c104d456`, the only differences are:
  - the 2 new projection files (added);
  - `current.json` and `snapshot_manifest.json`;
  - the four literals.
  - All 130 files under `baselines/v0.3.0` are unchanged.
- **Values match the emitted result.** In the copy, `current.json` → `GRAPH-SAU-2026-09-12-6f43b1a8c4aa` and `projection.json` = `85b166d6…`. Engine is `ENGINE-6b54371e99f3`, with 925/1,045. The snapshot has 730 files; authority has 20. This agrees with `GRAPH-EMISSION-CHECK` and with `MANIFEST-MEMBERSHIP-CHECK` (728 + exactly the 2 new rows; `current.json` is the only changed existing row).
- **Permission.** Amendment 09 grants these edits, and generation-GO execution condition 4 is satisfied.

**Copies and preservation**
- The positive copy matches all 1,761 ledger rows, with no extra or missing paths.
- The negative copy matches 1,760 rows. Its only difference is `graph.css`:
  - `3c45f104…` → `22af477c…`;
  - equal to the correct CSS with exactly one occurrence of the `flex-grow` block removed.
- Neither copy has `.git`, `.venv` or symlinks. The two copies share 0 inodes.
- W matches all 1,761 rows. W itself was never swapped.
- All 45 indexes match `INITIAL-INDEX-BINDING.json`.
- W is at HEAD `ce407db…` on `slice/s19-bilingual-dossier`, with 0 staged paths (`GIT_OPTIONAL_LOCKS=0`).
- No writer is active in W. The three idle `cursor-agent acp` processes have their working directories elsewhere (27387 is at the repo root).

**How faithful the argv is**
- I diffed every r2 argv against its hash-bound historical recipe.
- The only differences are:
  - an added `--name` on the browser commands (a raster/strict container name changed);
  - the source and proof mount paths.
- Selectors, markers, env, `--ipc=host`, user, network and image are identical.
- The browser commands keep the stock recipe without `--pull`. The image is referenced by content ID, so it can't be silently substituted.

**Test semantics**
- Line `test_graph.py:845` holds the new/old tokens in both copies. The protected-anchor assertion is at `:906`; the button assertion just before it is at `:905`.
- 3 scenarios... more precisely, the parametrization is 2 scenarios × 3 widths × 2 locales = 12 tests. `-k 'steel and 1440'` selects 2 of them, which matches the historical `run-summary` (collected 2, failed 2).
- The anchor block runs only for steel/public/evidence_to_change/1440. Its `finally` restoration assertion is what separates a meaningful RED from an unrestored DOM, as r2 classifies it.

**Functional and PDF tooling**
- The harness writes PDFs to `artifact_dir/"pdf"` (`test_dossier.py:273`), so the raster/strict `/input` = `functional/pdf` mount is correct.
- `-m 'e2e and not visual'` doesn't reach the stale visual `source_tree` pins, which live only in `tests/`.
- The strict checker requires:
  - exactly 44 expected names and 44 rendered reports;
  - PDF/raster hash equality;
  - `-summary.json` page counts;
  - an exact `.png`/`.txt` inventory;
  - page 1 = summary, appendix on page 2;
  - all 11 sections, full narrative, IDs and numerics;
  - footer policy;
  - embedded fonts;
  - the five orphan/caption associations.
- It exits nonzero on any issue.

**Environment**
- Image `sha256:938b534c…` is present locally, tagged `ior-visual-baselines:playwright-1.62.0-noble`.
- No `ior-s19-ds191*` containers exist.
- `browser-execution/` is absent.
- The Dockerfile in the ledger-bound copy has `FROM …@sha256:aa81288e…`.

## 3. Retained from earlier records, not re-run
- Cursor's exit 0 and the 3 focused tests passing (`three-tests.log`).
- Generation's five gates.
- Historical 7ae sensitivity: 2.53 px, EN right / AR left.
- The historical 12-test matrix, the 839-test functional run and the 44-PDF cohort (1,958 pages, max 73).
- Earlier manual observations.
- The earlier 674-test, mutant and print-sample results. None of these is carried over as a pass for this operation.

## 4. Findings

**Genuine blockers:** none.

**Execution conditions** (the delegated release must record these; the proposal bytes stay as they are):
1. **Output directories.**
   - After confirming each output directory is absent, create it as `1000:1000` before launch, the way historical `historical-css-negative/` was created (owned by barami, holding `COMMAND.json`).
   - Never let `-v` auto-create a directory. Docker would create it as root, the container user couldn't write, and the run would fail at setup. For `functional` that would burn the single allocation.
   - `rendered/` and `strict/` must exist before `--mount`.
   - No sidecar file inside `rendered/` may end in `.png` or `.txt`, because the checker's `raster_issues` compares that inventory exactly. r2's `.json`/`.log` names are fine.
2. **Image identity.** r2 never mentions `aa81288`. The preflight must:
   - record `docker image inspect` for ID `938b…`;
   - record the `aa81288` base digest as read from the ledger-bound Dockerfile.
   - The base image isn't pulled locally, so layer lineage can't be re-proven. Record it as attributed (Dockerfile plus S18 AM-4 records), not as verified. Don't pull it.
3. **Cohort seal before raster.** Write a record equivalent to `PDF-COHORT-READY` that binds the source ledger `c104d456`, actual collected/passed counts, the 225-file inventory with per-file hashes, and page counts. Fill it into the execution record where r2 now has `cohort_sha256: null`.
4. **Negative classification.** A failure at the button assertion (`:905`), at the restoration assertion, or on a missing token (`0!=5`) is not a meaningful RED. It means stop and preserve; it does not trigger the `a1dc` branch. Only a protected-anchor failure at `:906` in both EN and AR, with 12 rows, 5 rewrites, an exact repeat and restoration, counts.

**CARRY** (future work, not required for this GO):
- The manual full-44 review brief must bind the accepted procedure document by path and hash. It must cover:
  - fresh review of all 44 first pages;
  - longest EN and AR;
  - steel, PP and route-8 read in full;
  - contact sheets.
- r2 describes this procedure but doesn't hash-bind it. The four steel HTML changes don't reduce the 44-page obligation, and no earlier cohort can stand in for it.
- The full non-browser pytest suite and `verify_integrity` haven't run on `c104d456`. Only the 3 focused tests have (Task 6).
- Still pending: canonical capture with 130 outputs under `S19-BILINGUAL-DOSSIER-2`, the `test_graph.py` visual pin and change_ref, R1 against `ce407db`/`a1dc`, records and freeze, CI, delivery and Aura.
- If the `a1dc` alternate is triggered, it needs a new writer unit, ledger, fresh copies and a targeted GO. The accepted copies must not be mutated.

**Preference:** the CSS removal leaves a double blank line. It has no effect on CSS and no change is required.

## 5. Sanad
Every PASS above rests on direct reads or SHA-256 hashes I computed over the copies, W, the ledgers, the indexes, the recipes, the tools and the test source. Docker checks were read-only (`image inspect`, `ps -a`). Section 3 items are attributed to their records. No free facts.

## 6. Muhasabah
- **Khawatir:** "Hashes match and the recipes are stock, so GO." I didn't accept that on its own.
- **Muraqaba:** I didn't rely on the coordinator's or author's copy verification. I re-derived the reversal, the ledger deltas, the inodes, the index hashes and the argv diff myself.
- **Mujahada:** reading the strict checker and the Docker mount behaviour turned up execution conditions 1 and 3. Grepping r2 for `aa81288` turned up condition 2.
- **Gate:**
  - Provenance: PASS.
  - Assumptions: the image stays present until launch, and nothing writes to the copies between now and the preflight rehash. Both are covered by r2's preflight.
  - Fabrication: PASS. No browser, PDF or manual result is claimed.
  - Requirements: PASS. The verdict, hashes, what I checked versus what I attributed, and the condition/CARRY split are all given.
  - Risk: read-only; W, the ledger, the copies and the indexes were unchanged when I finished.

Nothing was written. Save this text externally.
