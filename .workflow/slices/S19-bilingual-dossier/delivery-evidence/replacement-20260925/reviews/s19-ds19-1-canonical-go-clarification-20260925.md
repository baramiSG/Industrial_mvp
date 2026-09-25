# Additive clarification of GO review `c3fece87…`

**The earlier A and B approvals stand**, subject to the clarified condition below. Everything is still bound to proposal r4 `7cbf9a77856f2709a84038f2e636649ce36e602dbdcd4496cfc133ab01211960`, which I re-hashed. No operation has been released or run by this text, and I wrote no files. The original review and the proposal are unchanged.

**Persona:** release-provenance reviewer (strict-reviewer, sanad-provenance and muhasabah-gate applied).

## 1. Clarified condition B.4(4).2
I did not intend to require that every one of the 130 files change bytes. My phrase "exactly the 130 permitted outputs differ" was imprecise. The condition should read:

- **Pathset:** after capture, the baseline root holds exactly the 130-file envelope: 128 WebP files plus `manifest.json` and `manifest.sha256`. There are no extra or missing paths, and `.candidate`/`.previous` are absent.
- **Where changes may occur:** byte changes are allowed only inside that 130-path set. Record the actual changed subset, derived by comparing content hashes with the bound S19-1 preimages.
- **Everything else:** the other 1,631 rows of ledger `c104d456` stay byte-identical.
- **No count requirement:** nothing requires a minimum or specific number of changed files. The stock swap (`visual_baselines.py:405-424`) renames all 130 files, so mtimes and inodes will change even where bytes don't. Decide "changed" from hashes, not mtimes.
- **Limits of the check:** a WebP byte or pixel change being inside the envelope does not make it acceptable. The post-capture adjudication under `pixel_scope` decides that: against S19-1, only the 8 steel dossier paths plus displayed run-ID text; against ce407, the inherited cumulative allowance.

This is the proposal's existing criterion (`capture.expected_file_envelope` and "Derive from postimages; do not force 130 byte changes"). It adds no tolerance and no scope.

## 2. PDF skill: correction
My earlier statement that no installed PDF skill was found was wrong. I missed the nested path. The skill is installed at `~/.agents/skills/synced/28575eb8…/pdf/SKILL.md` (SHA `9f78b835…`), and I have now read it along with the rendering section of its `REFERENCE.md`.

It is a general PDF-processing guide:
- pypdf for reading, metadata and text;
- pdfplumber;
- pypdfium2 page rendering at a chosen scale;
- CLI tools, and form, merge, split and OCR recipes.

It sets no acceptance criteria. The approved Task 4 gate already exercises its relevant methods through the unchanged tools: pypdf 6.16.1 structure, text and fonts in the strict checker, and pypdfium2 5.13.0 at scale 2 (144 dpi) in the renderer. I also viewed the rendered pages natively.

**It introduces no unmet requirement** for the completed full-44 review. No cohort re-review is needed, and I ran none.

## 3. HANDOFF citation: acknowledged
The r4 citation `b90d96d6…` resolves to an immutable copy. I verified:
- `handoff-history/HANDOFF-b90d96d6….md` = `b90d96d6146cff04349dc591dd2fa40bf31cb63bc0034bc0296697bf797c7800`;
- `HISTORICAL-CONTEXT-BINDING.json` = `28278f9c…`;
- the live HANDOFF is currently `cdfa1a1b9e34bfa129cf2db68adc37be34511704767b9e94e711facaecf0bddc`, which the delegated release should bind under B.4(5).

The proposal bytes don't need to change.

## Sanad
**Checked directly (read-only):**
- the saved review (`c3fece87…`), r4, the historical binding, the HANDOFF preimage and live HANDOFF, and the PDF skill;
- the r4 `capture` text at `expected_file_envelope` and `actual_write_and_pixel_change_counts`;
- the swap code I had already read in this session.

**Not re-run:** no tests and no operations. Every other result keeps the attribution given in `c3fece87…`.

## Muhasabah
- My original wording could have been read as requiring all 130 files to change. That reading is now withdrawn and corrected.
- My skill-search statement was wrong because I searched too narrowly. It is now corrected, and the skill adds no unmet obligation.
- No new scope, tolerance or ceremony has been added. Only the stated conditions, and later gates, still stand between this GO and delivery.

**Gate: PASS.**
