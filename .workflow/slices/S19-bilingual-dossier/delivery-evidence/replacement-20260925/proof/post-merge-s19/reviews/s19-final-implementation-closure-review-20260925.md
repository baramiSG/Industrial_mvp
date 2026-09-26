# Independent final implementation closure: S19 exact tree

## Verdict: APPROVE
I approve the final implementation of exact tree **`7c25b4616679d61f173f3d9072e3240e1a2a166b`** (proof commit `29bf5db55adaa57de2fa1f78aa5c9a028f31dc75`, freeze `80c60cab802b6c851c2cfa5a7d18056e3564abedc4c3e6a6c65fc80bce32e20f`, 3,307-path inventory `f906a444…`).

- My source-correctness APPROVE (`5ade2422…`) stands; no new source defect was found.
- The exact-tree gates it was waiting on are now complete and verified: two complete `make ci` runs in distinct clean roots, each with its own 44-PDF proof, plus the accepted offline, e2e and R1 gates.
- This is not delegated acceptance, exact-head review, hosted PR checks, merge/main, or Aura. Those remain later obligations.

I ran nothing and mutated nothing. Git used `GIT_OPTIONAL_LOCKS=0`; Docker reads were state and health only. All 54 protected indexes matched.

**Personas:**
- release engineer
- evidence-integrity auditor
- paged-media acceptance reviewer

**Skills:** the six installed skills, unchanged, applied. The PDF skill imposes no additional requirement.

## Bindings
All 29 files the brief cites match my own hashes, including:
- CI1 result `f3777dbc…`; CI1 seal `8c7488b3…`; CI1 raster `6167eb92…`, strict `aba83650…`, acceptance `6c24bffd…`, manual `f00426b2…`.
- CI2 result `6c049030…`, start `47b69bda…`, resources `ec923ef2…`, post-inventory `4b3cacd8…`.
- Root3 seal `4e44c930…`, render `bc27a3bb…`/`d015bd21…`, strict `7c326ca5…`/`cfd1dc1b…`, manual `9fb7b15b…`/`7ce98a46…`/`94086d66…`/`9d0fbea0…`.
- Restored identity `3e36fbae…`, graph `8156d58b…`/`aef8095d…`, events `f551f08e…`.
- Final preservation `62240271…`; index union `5ce928e9…`.
- My earlier reviews: `5ade2422`, `8855010a`, `6cf4a32b`, `8905e218`.

Additional records I checked:
- CI2 release `efce5bbd…`: all 23 bindings intact, including my replacement review.
- The released executor `4ebc6cfa…` differs from the reviewed `a459d8b2…` by exactly the 2 placeholder lines.
- Launch preflight: `LAUNCH-PREFLIGHT.json`.

## Direct checks

**Two complete runs, compared**

| | CI1 (`ci-root1`) | Replacement CI2 (`ci-root3`) |
|---|---|---|
| Command | literal `make ci` | literal `make ci` |
| Tree / proof commit | `7c25` / `29bf` | `7c25` / `29bf` |
| Namespace | `s19-ops2-ci1` | `s19-ops3-ci2` |
| `GIT_OPTIONAL_LOCKS` | 0 | 0 |
| Exit / duration | 0 / 2,795.8 s | 0 / 2,605.7 s |
| stdout/stderr hashes | match the result | match the result |

Both raw logs show every stage in order, with 0 `FAIL` lines:
- `GRAPH CLEAR/LOAD/LOAD(0)/VERIFY PASS` on `6f43` (925/1,045);
- graph tests `9 passed, 1 skipped`. The skip is `test_aura_verification.py:18` `AURA_OPERATOR_ONLY`, expected in compose CI, and `graph_tests` is unchanged since `ce407`;
- UI graph tests; `GRAPH_UNAVAILABLE_OK`;
- prohibited-file scan (3,307), threshold, UI contract and ES-module checks;
- `INTEGRITY PASS`; 11 scenarios PASS; all 7 reconstructions PASS;
- `3982 passed`; `SMOKE PASS`; browser preflight;
- `839 passed, 4 deselected`, then `4 passed, 839 deselected`.

The interrupted original root2 is preserved as incomplete: 33 records rehashed, no `ci2-result.json`. It is not counted and not reused.

**Operation conditions against actual event order**
- **CI1:** exit at 16:36:27; own seal 16:37:13, before the host restart. Its raster ran 17:31:37–17:32:54 and strict to 17:33:07, *after* the recovery closure (17:29:49). Its manual review was recorded at 17:42:10.
- **Replacement launch:** preflight at 17:43:40 recorded same boot, no active workloads or PDF containers, root1 manual complete, fresh namespace absent, the retained container healthy, lightweight processes listed, memory and load.
- **Replacement sequence:** one stop at 17:43:42 → one CI start at 17:43:48 → exit 0 at 18:27:14 → owned `down` → same-ID restore → healthy, with identity and original-graph verification at 18:27:26 → own seal at 18:27:26.9 → raster from 18:28:34 → strict to 18:30:04 → manual recorded at 18:40:01.
- No `INCOMPLETE`, `DEFERRED` or `STOP-INCOMPLETE` records, and no retry.
- After the run, the owned container and network were absent and the volume retained. The restored graph is `461bf4840962`, 925/1,045, 410/515, partition and provenance valid.

**Own PDF proofs** (independent recomputation for each root)
- **Seal:** 225 files; on-disk set equal; 0 hash or size mismatches. Counts 44/44/44/44/22/22/5.
- **Render:** 44 documents, 1,958 pages, 144 dpi, 0 bound violations. Every `pdf_sha256` equals the seal, every PNG rehashes, and there are no `.png`/`.txt` sidecars.
- **Strict:** 44 / 1,958 / `issues: []`.
- **Comparison with the pre-freeze cohort:** all 181 HTML/JSON exports in each root are **byte-identical** to the pre-freeze cohort I adjudicated (`c3fece87`, full-44 APPROVE). Only the 44 PDF binaries differ.
- **All 1,958 rasterised pages in each root are byte-identical to the pre-freeze rendered pages**, and root1 equals root3 page for page. My earlier direct views of the steel and other pages, and the accepted appendix lineage, therefore apply at exact pixel identity.
- **Manual (supporting Codex observer):** in each root, 44 fresh first-page views whose hashes equal the rendered page-01 files, 3 fresh appendix fallbacks and 1,911 exact reuses, covering all 1,958 pages with 0 uncovered and 0 findings. The referenced observation, reuse and fallback records rehash.

**Final preservation, re-checked now**
- W, root1 and root3 each match all 3,307 inventory files.
- W: HEAD `ce407db`, 0 staged.
- Roots 1 and 3: HEAD `29bf`, tree `7c25`, clean status (guarded).
- All 54 indexes equal.
- The retained container `42216eec…` is running and healthy.
- No owned `s19-ops*` or `ior-s19*` containers exist; all three owned volumes are retained; no CI or PDF process is running.

## Retained from earlier reviews, not re-run
- Source APPROVE `5ade2422`; offline `1f2be1cf` (14/14, 3,982 passed); standalone e2e `0d186b92`; R1 `9c74e0df`, accepted in `8855010a`.
- The recovery closure `d22e8c81`.
- The first-page and appendix observations by the supporting observer.
- The pre-freeze full-44 lineage.
- The cause of the host restart is unknown.

## Findings

**New source defects:** none.

**Missing or failed gates:** none for implementation closure.

**Preferences carried from `5ade2422` (non-blocking):**
- The route renderer's general "external dependency" labelling.
- Units shown after a status in the summary metric cells.

**CARRY:**
- Close KL-33, KL-84, AR-V01 and TRADE-SCALE-01 only in the later additive delivery record, citing these gates.
- Then: separate delegated acceptance; staged/commit tree equal to `7c25`; PR with all hosted checks at the exact head; exact-head Claude review; merge; main CI; and the separately reviewed Aura checkpoint.
- Record the unknown restart cause in the delivery limitations.

## Sanad
**Direct:** the 29 hashes; release/executor diff and bindings; both raw CI logs stage by stage; the Aura-only skip source; the event and timestamp ordering; the launch preflight; the post-run inventory; the restored graph; per-root seal, render, strict and manual recomputation, including byte identity with the pre-freeze cohort and pages; the preservation of W and both roots, the 54 indexes, the interrupted records and the retained service.

**Attributed:** the supporting observer's first-page and fallback views; historical appendix observations; recovery execution; offline, e2e and R1 executions (accepted earlier).

**Assumption, stated:** pixel-identical pages carry the earlier accepted observations at exact identity, which is the approved reuse rule.

## Muhasabah
- **Khawatir (first framing):** "Everything reports exit 0, APPROVE."
- **Muraqaba (watching for bias):** I re-derived each run's stages from the raw logs; checked event order against every GO condition; recomputed both PDF proofs; found the skipped test and traced its reason.
- **Mujahada (the actual work):** proving byte and pixel identity with the previously adjudicated cohort turned attributed manual coverage into exact-identity evidence.
- **Gate:**
  - Provenance: PASS.
  - Fabrication: PASS. No delivery, main or Aura claim.
  - Requirements: PASS. Verdict, exact tree, defects separated from gates, CARRY.
  - Risk: read-only; everything preserved.

Nothing was written. Save this text externally.
