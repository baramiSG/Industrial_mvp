# Independent review: S19 replacement canonical capture acceptance

## Verdict: APPROVE
I accept the single replacement canonical capture under `S19-BILINGUAL-DOSSIER-2`: the 130 frozen outputs, with manifest `0d05eee71eb214c65d21209b52d3933144bb888eb1ddc100f9006e9c9d3621bc`.

This accepts the capture only. It is not final-candidate or implementation acceptance. There are no blockers. I ran no operations and wrote no files.

**Reviewer:** Claude Code `claude-opus-5-5`, continuing the same session. Read-only; image decoding used the project `.venv` Pillow with `-B` and `PYTHONDONTWRITEBYTECODE=1`.

**Skills:** project-orientation, task-standards, strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate. The PDF skill at the nested installed path is not relevant to image acceptance, and the full-44 approval is unchanged.

**Personas:**
- visual-regression acceptance reviewer
- bilingual UI reviewer
- release-provenance auditor

## Bindings (hashes I computed; all match)
| Subject | SHA-256 |
|---|---|
| Brief | `6699d88687c4c13a7ea36fa9468d84693625bb187145f75134b82c64063c95ed` |
| Proposal r4 | `7cbf9a77856f2709a84038f2e636649ce36e602dbdcd4496cfc133ab01211960` |
| Owner release | `bfc6cc1d12613ea58b2fdca9a1e458180b2beca027115791e4da8218b4ba860c` |
| Launch handoff (history copy) | `cdfa1a1b9e34bfa129cf2db68adc37be34511704767b9e94e711facaecf0bddc` |
| My GO / clarification | `c3fece87…44e9` / `7cc3e40c…b75a` |
| `capture/POSTCHECKS.json` | `e9bb3a7a5e374ca4259faf7bf9c3a0a8aa1c92d21fe28be5757695b7472b2481` |
| `POST-CODEC-PRESERVATION.json` | `eac191456ae78214123c966144ad1371570496fe1075852b0608f7a825afdfaa` |
| `ROOT-CHANGED-PAIR-OBSERVATIONS.json` | `b3480162bc79ee2828612fad3f9b5795f09acc9b1e504152cd4708d53d503854` |
| `PAIR-REUSE-JOIN.json` (hash not given in the brief) | `3cdde21edf7a786b455378fa2086e2817700418f50809f0e08716ca700a5fcd9` |
| `RETAINED-PAIR-OBSERVATION-INDEX.json` | `2086766b3c7cdf7be68261b9745953e91c8452e29ff530c7a5ef5a5bf0b83e49` |
| `BOUNDS-OBSERVATIONS.json` | `1162901a60fbcd1c12fd3d1e00270227efde673d3587f2fa0228b15cd9a6b87a` |
| New manifest (frozen copy = W) | `0d05eee7…21bc` |

## Checks I performed myself

**Operation fidelity**
- `capture/COMMAND.json` argv, environment and working directory equal r4 `capture.command`/`environment`/`cwd`.
- One runner container started (`dffa2f3b…`, image `938b…`, network `none`). Stdout: `4 passed, 839 deselected in 394.14s`. Stderr empty; exit 0.
- Both codec `COMMAND.json` argv equal r4 `future_command`, with stdin `e4fddc81…`. Both exit 0, stderr empty, and stdout ends with `CANONICAL128_CODEC_AND_OLD128_PIXEL_MACHINE_CHECKS_PASS`.
- No `938b` containers remain.

**Manifest and output**
- The frozen postimages and W's baseline root are the same 130 paths with identical bytes.
- `change_ref` is `S19-BILINGUAL-DOSSIER-2`. The manifest has 128 entries, and every entry's hash and size match.
- The sidecar matches.
- `source_tree` equals r4 `source_hashes` (109 paths), and `font_hashes` equal r4 (2 fonts).
- Budgets: maximum 153,438 bytes, total 11,759,010.

**Both 128-row ledgers, recomputed independently**
- I decoded every old and new image in both contexts. Raw and RGB hashes match each ledger row exactly.
- Dimensions and RGB mode are preserved. There are no encoded-only rows.
- **Compared with S19-1:** 124 byte-identical and 4 changed:
  - `{en,ar}/desktop-1440x900/journey-e-steel-public-dossier`
  - `{en,ar}/desktop-1440x900/journey-i-graph-evidence-to-change`
- **Compared with ce407:** 36 identical and 92 changed.

**Where the four immediate diffs fall**
- Dossier: bounding box (198,780)–(1242,900), in text-line bands only.
- Graph EN: (1089,802)–(1307,816). Graph AR: (133,802)–(550,819). Each is one relationship line.
- Everywhere outside those bands, new equals S19-1 exactly (checked for all four).

**Pairs I viewed myself** (12 images: 4 new, 4 S19-1, 4 ce407):
- **Dossier compared with S19-1.** The old image shows the defect D-S19-1 fixes: "Evidence passport ledger: S-WITS-721049 S-UNICOIL-EPD **S-UNICOIL-SPEC**". The new image shows separate "Evidence passport ledger: S-WITS-721049 S-UNICOIL-EPD" and "Public evidence contradictions: S-UNICOIL-SPEC" lines, with correct Arabic labels and RTL order. The snapshot line moves down one line, and the "Supporting evidence pack" heading moves below the viewport. Nothing else changes, and nothing is clipped.
- **Graph compared with S19-1.** The only visible change is the relationship run ID `ENGINE-5e01ef7c4b9d` → `ENGINE-6b54371e99f3`. The neighbouring target text moves slightly, within the inherited allowance for locale-specific span/small widths. The diagram, nodes and anchors are unchanged.
- **Compared with ce407.** The dossier moves from the old S18b card layout (which included a raw JSON dump in "Supply conclusion") to the approved compact S19 summary. That is inside the cumulative 16-dossier allowance. On the graph, the run ID changes `a1dcbf0e7665` → `6b54371e99f3`. The diagram-area raster bands from ce407 are identical to those already observed in the ce407→S19-1 pair, and I saw no visible drift in them.
- **Pixel thresholds.** Three of the four immediate pairs exceed the ordinary compare-mode thresholds: AR/EN dossier and AR graph. This is an intended update inside approved scope. No tolerance was changed.

**Cumulative coverage**
- `reused` = changed from ce407 and byte-identical to S19-1: 88 rows, matching the join exactly.
- `fresh` = changed in both comparisons: exactly the 4 paths above, which I viewed.
- `identical` = the 36 byte-identical rows.
- Total 36 + 88 + 4 = 128.
- For every reused row:
  - current and retained before/after raw and RGB hashes are equal;
  - all four image files rehash;
  - the index pointers resolve to the same path.
- All 8 distinct observation, ledger, codec and closure records rehash. Closure is through `s19-canonical-other56-r1` and the owner freeze release.
- Reused observations stay attributed to their original Codex observers and closure. They are not presented as Claude views.

**Fresh bounds**
- All 50 files in `W/.artifacts/e2e` have mtimes after the launch timestamp (`1790341955861905344` ns) and after their recorded previous mtimes. The external copy `capture/artifacts-e2e` is byte-identical.
- There are 16 bounds JSONs. In each, initial equals leftmost and nothing is `clipped`. Every report has `scrollX` 0, `scrollWidth` ≤ `width`, and fonts `loaded`.
- All 16 initial/leftmost PNG pairs are pixel-identical to each other and to the canonical WebP.
- Scroll restoration is asserted in the stock code (`test_visual_baselines.py:320-350`: restore `original_scroll`, then assert equality before capture), and the test passed. There is no separate raw restoration record, and none is claimed.

**Preservation after both proofs**
- The W git-visible pathset equals the 1,761-row ledger. Exactly the 6 permitted baseline files differ from `c104d456`, which fits the clarified envelope.
- The immutable copy is unchanged. Both old 130-file trees are intact.
- All 45 indexes match. The 43 `.venv` metadata and interpreter bindings match.
- `.candidate`/`.previous` are absent. HEAD is `ce407db`, with 0 staged paths.

## Retained from earlier records, not re-run
- The 88 historical pair observations and their accepted closure (Codex authors).
- The `aa81288` base lineage.
- The supporting root and bounds observations, which my own checks corroborate.
- Full-44 readiness (`c3fece87`), which is unchanged: the producer cohort was not affected.

## Findings
**Genuine blockers:** none.

**Pin literals and assembly: yes, both may proceed** under the existing approvals, as a separately assigned sole-writer unit:
- **Pin literals:**
  - `tests/test_frozen_public_evidence_pins.py:48` → the actual subtree OID, computed with a new alternate index from exactly these 130 files (manifest `0d05eee7…`). Use the existing `PIN-COMMANDS` procedure and keep every old index.
  - `tests/test_s17_status_docs.py:35` → `S19-BILINGUAL-DOSSIER-2`.
  - Both files are outside the 109-path visual `source_tree` and the 230 graph inputs, so there is no self-hash cycle or recapture.
- **Finite durable/control assembly:** it may proceed only if it changes no graph- or visual-hashed file and no baseline. Record a new complete ledger after the edits. If an edit touches a hashed input, this capture acceptance is invalidated.

**CARRY (outstanding gates, not required for this acceptance):**
- Full pytest will fail the visual-contract and frozen-pin tests until the pins land. Classify that as expected, not hidden.
- Exact-tree freeze, and all Task 6 gates, including compare-only `make e2e` against this capture.
- Actual delivered `a1dc` → `6b54` bilingual R1 same-layout diagnostic.
- Two clean-root CI runs, each with its own 44-PDF proof.
- Claude implementation/tree and final-head reviews, delegated acceptance, GitHub/main CI, and Aura.

**Preference:** a record of the scroll-restoration assertion's actual values would be stronger than inferring it from the passing test. This doesn't block.

## Sanad
**Direct:** every hash, argv equality, decoded ledger recomputation, band and bounding-box calculation, set arithmetic, join and closure rehash, mtime check, bounds analysis, preservation check, and the 12 native image views listed above.

**Attributed:** historical pair observations and closure, base lineage, and the supporting observers' prose.

**Not verified:** any later gate.

## Muhasabah
- **Khawatir (first framing):** "Machine proofs passed, so APPROVE." Not enough on its own.
- **Muraqaba (watching for bias):** I didn't trust the 88/4/36 split or the claim that the artifacts were fresh. I re-derived both, and I checked threshold failures against scope instead of waving them through.
- **Mujahada (the actual work):**
  - The band-equality check showed that the new-vs-ce407 graph diffs come from the already-observed pair plus a single run-ID line.
  - Viewing the images confirmed that the dossier change is exactly the approved D-S19-1 fix.
- **Gate:**
  - Provenance: PASS.
  - Assumptions: the stock scroll assertion executed as written; the historical closures have no unrecorded invalidating finding.
  - Fabrication: PASS.
  - Requirements: PASS. Verdict, bindings, what I checked versus what I attributed, and whether pins and assembly may proceed are all given.
  - Risk: read-only; everything was preserved at the end.

Nothing was written. Save this text externally.
