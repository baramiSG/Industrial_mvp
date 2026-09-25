**Verdict: APPROVE.** The D-S19-1 corrected source is ready for the separately bound replacement generation and capture operation. This approval covers only the reviewed source bytes. It does not give execution GO, does not accept a final candidate, and does not cover GitHub or Aura.

No files were written or patched. The plan file was not created either, because you asked for no writes. My checks ran only in memory or read-only: no bytecode, no pytest cache, and the source copy was rehashed afterwards.

# Independent source-readiness review: D-S19-1

**Reviewer seat:** Claude Code, model `claude-opus-5-5`, run in safe-mode plan permission with Read/Glob/Grep/Bash only. The effort level (high) and subscription OAuth (claude.ai Max, first-party, no API key) come from `CLAUDE-COMMAND.json`; I did not check them myself.

## 1. Bound subject (hashes I computed)

| Item | SHA-256 | Match |
|---|---|---|
| `source-readiness/SOURCE-BINDING.json` | `5688e75de20572104d0464f77b65ac52f0594d592ff50bf046fbd7bb9298ad08` | ✔ brief |
| `source-readiness/D-S19-1.diff` | `d4cd693b406004dc4a74c18b3f488ba17bb8ebf9bf7a119a2a6ba0ba954277ee` | ✔ brief |
| `src/ior_mvp/dossier.py` | `34f20faa89ea15f441285e56b238702df9de960097b4da69ed01336f4c3fb0f0` | ✔ brief |
| `tests/test_dossier_projection.py` | `af95c0e13822ccb32d9da7e1fc5d7112443bf1a9828786ad87801ffcd2f30915` | ✔ brief |
| Addendum `S19-COMPLETION-ADDENDUM.md` | `51cd644ce3ab189db108bd3998e6b18e8feb91e7927efc0c12ab6babc979b8ad` | ✔ |
| Packet `SHA256SUMS` | `59677f10a496238a9e0e497292bfd596982906e4f916eef6328984c583019c36` | ✔ |
| Prior Claude ruling | `9b83fef253e0854ba1d15d2938dc9711f7a7dc2cac103c65ac7e8297cff332b3` | ✔ |
| Project-Build-Guide.docx | `f790d20335a6435b4e1b6e39f0c24f1c776f1938ad483e0a9df7d80255d3ed3e` | ✔ |
| Methodology DOCX | `5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9` | ✔ Manifest §11 |
| `config/ui_strings.v1.yaml` (1.7.0) | `36934d057c4b330abfd9572acc8b6a1194be7aa20d58f3f898d1495ee2212a6b` | ✔ Manifest table; catalogue unchanged |

**Ledger integrity, checked by me before and after my test runs:**
- All 1,759 bound paths match, both in the review copy and in the worktree `/home/barami/projects/ior-worktrees/s19`.
- The copy has no extra files.
- Compared with `S19-PRE-WRITER-SOURCE.json`, only `dossier.py` changed (`0e74a4f0…` → `34f20faa…`) and `test_dossier_projection.py` changed (`c20ebedd…` → `af95c0e1…`).
- All 45 indexes in `INITIAL-INDEX-BINDING.json` still match their expected hashes.

## 2. Preparation, personas and skills

- **Read:**
  - `AGENTS.md` and the Authority Manifest (§5 dossier reading list, §6 invariants, §7 change classes).
  - DOCX §15, read directly. P1084: "The one-page decision is backed by a reproducible analytical record." P1104–1105: "Evidence — Top supporting and contradictory evidence…". This matches `DOCX-SECTION15.txt`.
  - Core04 §9 (lines 530–545) and the Core09 PDF gate (line 803: "Summary occupies page1; appendix begins page2").
  - Accepted plan `00-…IMPLEMENTATION-PLAN.md`: the Evidence row at `:78` ("support and contradiction separate"), and Tasks 4–6.
  - Accepted design `01-…EXPERIENCE-DESIGN.md`: `:15` (the first page includes "top supporting and contradictory evidence references") and `:35`.
  - The approved addendum, the prior ruling §3.3, the mandate, delegated decision (a), `HANDOFF.md`, `SUBSCRIPTION-ONLY-ROUTES.json`, and the guide's Prompt 0R/3B and B1–B7 blocker taxonomy.
- **Skills:** I read and applied project-orientation, task-standards, strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate from `/home/barami/.agents/skills/*/SKILL.md`.
- **Personas:**
  1. Contract auditor for the decision dossier: does page 1 meet §15 and design `:15` under the approved ruling?
  2. Test-quality reviewer: would the new tests catch the old concatenation and plausible mutants?
  3. Change-control and provenance auditor: exact bytes, graph and visual input consequences, and ordering before generation.
  4. Arabic/English print reviewer: is the result still one legible physical page?

## 3. The correction as implemented

At `src/ior_mvp/dossier.py:666-669,678`:
- The existing selections are unchanged: `summary_refs` is the first two public passports, and `contrary` is the public contradiction-register IDs.
- Instead of one concatenated line, it renders two separate paragraphs:
  - `<p class="summary-evidence">{evidence.title}: refs(summary_refs)</p>`
  - `<p class="summary-evidence">{dossier.public_contradictions}: refs(contrary)</p>`, rendered only when `contrary` is non-empty.
- No catalogue, CSS, projection, calculation or decision code changed. `build_dossier` is untouched.

## 4. Requirement → implementation → evidence

| Requirement (source) | Implementation | Evidence | Result |
|---|---|---|---|
| Separate labelled support and public-contradiction groups, EN/AR (ruling §3.3; delegated decision (a)) | Two `p.summary-evidence` groups using existing keys `evidence.title` and `dossier.public_contradictions` | **Checked by me:** keys exist in EN and AR (`ui_strings.v1.yaml:662/751/1768/1857`). In-memory render of steel gives `Evidence passport ledger: S-WITS-721049 S-UNICOIL-EPD` / `Public evidence contradictions: S-UNICOIL-SPEC`, and `سجل جوازات الأدلة:` / `تناقضات الأدلة العامة:` | PASS |
| No catalogue edit or version bump | Catalogue untouched | **Checked by me:** hash equals Manifest; not in the changed set | PASS |
| Keep IDs, order and the first-two selection | Same list expressions | **Checked by me:** my reconstruction of the retained source from the corrected file hashes to exactly `0e74a4f0…`, so the diff is exact | PASS |
| Omit an empty second group; no invented "none" on page 1 | `if contrary:` | **Checked by me:** PP renders one group; appendix still shows `dossier.no_public_contradictions` | PASS |
| Keep genuine dual-role references in both groups | No deduplication | **Checked by me:** dual-role test passes; a deduplicating mutant is killed | PASS |
| Evidence, calculation and decision identity unchanged | Renderer only | **Checked by me:** `build_dossier` JSON is equal old vs new for all 22 case/modes; analysis not mutated. **Checked by me:** re-running `comparison.py` (`eebc60a2…`) in memory on the two observations prints `ALL11_COMPLETE_REAL_DECISION_AND_GRAPH_SEMANTICS_PASS`, including steel = INVESTIGATE and PP = REJECT/route 0 | PASS |
| Public/synthetic isolation | Public-only filters unchanged | **Checked by me:** test asserts no synthetic IDs in the groups (simulated mode); register is built from `synthetic_flag is False` only (`dossier.py:73-84`) | PASS |
| Meaningful RED (old concatenation fails) | 3 new tests (9 parameter sets) | **Checked by me, in-memory mutants:** old concatenation → 5 fail / 4 pass, matching the attributed `red-pytest.log`. Deduplicated dual-role → 1 fail. "None" group on empty → 4 fail. Swapped labels → 9 fail. Contradiction also in support group → 5 fail | PASS |
| GREEN | — | **Checked by me:** focused tests 9 passed. The four dossier unit files: 674 passed, 1 warning (pre-existing Starlette/httpx deprecation), exit 0 | PASS |
| One legible physical summary page; unchanged fonts; appendix starts on page 2 (design `:15,:35`; Core09 `:803`) | No CSS change | **Checked by me:** viewed all four steel page-01 PNGs; page 1 ends at the snapshot line and page 2 starts with the "Supporting evidence pack" contents. Both groups are distinct and there is no clipping. In the simulated pages the footer disclosure sits clear of the content (about 250 px spare at 144 dpi on sim-AR, the tallest). **Attributed:** governed Docker run, 4 passed / 172 deselected; renderer 4 documents, 184 pages, 0 whole-page bound violations | PASS (preliminary sample) |
| Layout-risk scope | — | **Checked by me:** only `data/snapshots/public/{,historical/v1/}SAU-H0-721049.json` has a non-null contradiction. In-memory HTML differs from the retained renderer in **exactly 4 of 44** case/mode/locale outputs (steel), and only in the summary evidence line | INFO |
| Hashed docs complete before binding (addendum §3.2) | No Core or catalogue change needed | **Checked by me:** Core04 §9 does not describe the concatenation. The 230 graph inputs include only `docs/authority` DOCX and `docs/core` among docs. The visual `source_tree` has no `docs/`, `.workflow` or README entries. All 230 corrected-observation input rows match the bound ledger, including `dossier.py` = `34f20faa…` | PASS |

## 5. Findings

**Genuine blockers (B1–B7): none.**

**CARRY items for the operation stage.** None of these is a defect in the source bytes.
1. **Expected stale visual pin.** `browser_tests/baselines/v0.3.0/manifest.json` `source_tree` still pins `src/ior_mvp/dossier.py` at `0e74a4f0…`. Visual-contract and frozen-pin tests are therefore expected to fail until the one replacement capture and pin rebinding. The operation's step 1 must classify this explicitly as expected-gated and must not hide any other failure. I did not run those tests.
2. **Strict all-44 wrapper still required.** The sample render used diagnostic whole-page bounds ("does not prove declared content-region or overlap safety"). The operation must run the strict all-44 acceptance wrapper, including page-1 summary / page-2 appendix and the footer region, plus a manual review of all 44 first pages.
3. **Records not yet updated.** The ADR/slice-log entry saying D-S19-1 reopened generation, and the five controls and state, are not updated. They are not graph, visual or authority-hashed inputs, so they can follow `HANDOFF.md` step 4. They must be done before the freeze.
4. **Full gates not run.** Full `pytest -q`, `verify_integrity.py`, the browser/all-44 cohort, R1, and the two `make ci` runs have not run on these bytes. They remain Task 6 obligations.
5. **Correction to the prior ruling's CARRY #5.** In HTML, only the 4 steel first pages change, not all 44. The approved all-44 first-page review still applies; this fact only narrows where layout risk sits.

**Preferences (non-blocking):**
- In `test_summary_separates…`, also pin the literal steel supporting IDs `['S-WITS-721049','S-UNICOIL-EPD']`, so the oracle does not depend on the test's own copy of the `[:2]` selection.
- Add a `dossier == before` assertion to the dual-role test.
- The label "Evidence passport ledger" for the supporting group follows the approved ruling; I am not reopening it.

## 6. What this does and doesn't cover

It covers these exact source bytes: ledger `5688e75d…`, with `dossier.py` `34f20faa…` and the test file `af95c0e1…`, as the input to the prospectively allocated single replacement sequence.

It does not cover:
- operation GO (the exact input/operation binding, including the unreviewed `S19-REPLACEMENT-OPERATION-DRAFT-r1.json`, needs its own review);
- the projection ID `6f43b1a8c4aa` (in-memory only; not written);
- the manifest 728→730 expectation;
- the all-44 PDFs, the canonical capture, R1 or pins;
- any candidate, freeze, CI, GitHub or Aura step.

Any further change to a graph- or visual-hashed file invalidates this approval.

## 7. Sanad (sources)

**Checked by me:**
- All hashes in §1.
- The 1,759-path ledger (copy and worktree, before and after) and the 45 index hashes.
- A full read of the diff, `dossier.py:60-190,560-835`, the new tests and the relevant `browser_tests/test_dossier.py:223-543`.
- Catalogue keys, CSS `dossier.css:95-120`, Core04/Core09 lines, DOCX P1083–1105.
- In-memory old-vs-new differential over 44 outputs, mutant runs, and the 9 focused plus 674 dossier unit tests.
- Re-running the graph comparison and the input-row ledger match.
- The four page-01 images and the page-01/02 text.

**Attributed and not re-run by me:**
- `red-pytest.log`: 5 failed / 4 passed, consistent with my mutant result.
- `green-dossier-unit.log`.
- The Docker print run (`RESULT.json` exit 0, `stdout.log` 4 passed, image `sha256:938b534c…`).
- The renderer's `RENDER-RESULT.json`.
- The construction of the observation JSONs.
- The host `print-sample-pytest.log` setup failure (Chromium missing). No pass was claimed from it, and none is counted here.

## 8. Muhasabah

- **Khawatir (first framing):** it's a two-line change and the tests are green, so approve. Rejected as insufficient on its own: I checked the diff's exactness, looked for any appended RED, measured test strength with mutants, and looked at the actual pages.
- **Muraqaba (watching for bias):** the risks were trusting the coordinator's READINESS claims, reopening the approved label choice, and treating a green page count or an execution result as acceptance. I re-derived each claim myself, left the ruling alone, and marked all future gates as unrun.
- **Mujahada (the actual work):** the in-memory differential, the mutation matrix, the graph-input binding and the check of the hashed-document path. These found no blocker and narrowed layout risk to 4 outputs.
- **Gate:**
  - Provenance: PASS. Every claim above carries a path, hash, viewed image or command.
  - Assumptions: PASS, stated. The Docker samples ran against these bound bytes (their timing and read-only mount are consistent). Re-executing `comparison.py` inside an exec namespace is equivalent to its recorded run.
  - Fabrication: PASS. Nothing unrun is claimed as passed.
  - Requirements: PASS. Verdict, hashes, only the necessary corrections, and a CARRY/preference split are all given.
  - Risk: PASS. Read-only; the approval is limited to these bytes.

**Pending:** operation input/binding review and GO; the one replacement sequence; the all-44 strict proof and manual review; capture review; R1; pins; records; freeze; Task 6 gates; exact-tree review; acceptance; GitHub; Aura.
