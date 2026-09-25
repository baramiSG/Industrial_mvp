# Independent review: S19 full-44 readiness (A) and single canonical-operation GO (B)

## Verdicts
- **A — full-44 readiness: APPROVE.**
- **B — canonical operation: APPROVE (GO).** This covers exactly one stock canonical capture under `S19-BILINGUAL-DOSSIER-2`, followed by the two read-only codec proofs, as bound by `CANONICAL-OPERATION-PROPOSAL-r4.json`. GO holds only if the five execution conditions in §B.4 are met. None of them changes the proposal's bytes.
- **Erratum: confirmed.** In my earlier browser review (`4cdee844…`), the abbreviated CSS-diff hash row has the wrong suffix. The correct value is `3d073380aab0a28b6295e623a8738a87a26d041112f225e7e6d1306d25b7f6cb`, which is what I computed in that session and what the proposal and copy binding carry. I acknowledge this as an additive erratum; the original review text stays as it is.

No blockers. I did not run the capture or any operation, and I wrote no files.

**Reviewer:** Claude Code `claude-opus-5-5`, plan mode, Read/Grep/Bash only. No subagents.

**Personas:**
- bilingual paged-media reviewer
- visual-regression and release engineer
- provenance auditor

**Skills:** I re-read and applied project-orientation, task-standards, strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate. Their hashes are unchanged since my last review. The `~/.claude` copy of project-orientation differs only in naming CLAUDE.md instead of AGENTS.md. I found no installed PDF skill under `~/.agents/skills`, `~/.claude/skills` or `~/.codex/skills`. I applied the plan's Task 4 PDF requirements directly instead.

## Bound hashes (all computed by me; all match)

| Subject | SHA-256 |
|---|---|
| Brief r2 | `aaa5c9ac7bb5cae75416c3ec9638a2e45527f07bbf0d68f763c264fb4f73d893` |
| Canonical proposal r4 | `7cbf9a77856f2709a84038f2e636649ce36e602dbdcd4496cfc133ab01211960` |
| Source ledger | `c104d456735172817dc356fe17c349c46250de2dc98dd0195952e4f5565d7dc0` |
| Prior browser GO / release record | `4cdee844ce3705346bc0b5f4ad815aa2ac230ca49d807c8547f926f20bfdfe3c` / `fe4272d4e008770a61da135ec316b2eead1eb27e9b9c272088699b748165f4cc` |
| `SENSITIVITY-RESULT.json` | `0b095c75628bc9c3858507ce0c84a9643b70e409c18fcd84d5cb4140eb78b7e8` |
| `graph-matrix/RESULT.json` | `d788950caa1891830604f7d77ba636be93c882af37b786cd1caae2e747bc9845` |
| `functional/RESULT.json` | `04eb4e732786992c0775a944f70aab41e67e2a174fe939c7012228799f717479` |
| `PDF-COHORT-READY.json` | `90344ae1e7f7ae1c5d03b2c3d2a5ae90afb3ff3f04ecba52c46acbb5333e9134` |
| `RENDER-RESULT.json` | `5eee51a9f84c633b819059bd953caf8ba36a335f50662d3209d63e03e5ef0698` |
| `PDF-ACCEPTANCE.json` | `bc0a02fa73bd0bb04fd2af5798b56a5685fbd2fe29b44567d83ea5a758327d65` |
| `FULL44-READINESS.json` | `1b137e967b478b14562bacfa7d7ecabef9f5a2fa91d5954f9acbf2a747105b35` |
| `APPENDIX-REUSE.json` / `RETAINED-APPENDIX-OBSERVATION-INDEX.json` | `395dcb90…` / `8e3dbb33…` |
| `MANUAL-REVIEW-BRIEF.md` | `386578249303dadd4b6d6b345bb2c9d815b13c1e7cdab2587cf403a7b13a3b5d` |
| `POST-BROWSER-PRESERVATION.json` | `b70b5c542727b0d3bdea8ea1efd2b4fbfab45baed61add3370af069fa33c2957` |
| `PREEXISTING-E2E-PRESERVATION.json` | `7dd2091ac08dddd97fad7bfc43b36ed1bdbb76ab4a69cfdca9522cbac6f936d1` |
| `HOST-ENVIRONMENT-BINDING.json` | `4f1b05f2a192e506052e5708e1340673154ee493ade93728282dda14eea143f3` |
| Materialized `codec-pixel-check.py` / retained helper | `e4fddc810bf516535b980dcf3ccdc34b26cc0abf3b6eb063027396c81205f31b` / `eef1c23a…` |
| S19 plan | `7749006ae850adf66fea862934c8362d9ea5c9254aaf74ded702504e69ce44d1` |

All 24 `sources` rows in r4 still match, except `HANDOFF.md`: r4 cites `b90d96d6…`, and the HANDOFF has since been updated additively. This is normal evolution, not a change to any subject (see condition B5).

---

## A. Full-44 readiness: APPROVE

### Checks I performed myself

**Sensitivity**
- The negative and positive `COMMAND.json` argv are identical to r2's argv.
- The negative stdout shows `2 failed, 10 deselected`. Both failures are at `test_graph.py:906`:
  - `en/row/2/small.right: 1344.2 -> 1346.06`
  - `ar/row/2/small.left: 95.8 -> 93.94`
- From the raw anchor JSONs in both locales:
  - 12 rows, rewrites at rows [1,2,3,4,5];
  - repeat equals before, and restored equals before;
  - **0 button-box changes**;
  - anchor shifts of 1.86 px on rows 2 and 3 only.
- The positive run and the matrix run show no anchor or button changes.
- Tokens are new `6b54…` / old `7ae3…`, and the alternate token was not used. This meets condition 4 of my earlier review.

**Graph matrix**
- argv matches r2.
- Collected 12, passed 12, exit 0.

**Functional run**
- argv matches r2.
- `839 passed, 4 deselected`, stderr empty.
- run-summary: collected 839, failed 0, skipped 0.

**Cohort seal**
- All 225 files match the seal's hash and size.
- Suffix counts: 44 / 44 / 44 / 44 / 22 / 22 / 5.
- 1,958 pages, maximum 73. Page counts are unchanged against the r4 predecessor.
- **Independent diff against the r4 predecessor:**
  - Only the 4 steel HTML files changed.
  - In `-analysis.json` and `-dossier.json`, only 12 `…/route_hypotheses/8/shared_enabler/graph_projection_id` leaves differ (`ccd1a2abd05c` → `6f43b1a8c4aa`), in the 4 aluminium simulated files.
  - The 4 steel `-layout.json` and `-summary.json` files also differ (reference-row geometry and PDF bytes). That is the expected consequence of D-S19-1. The seal's wording is scoped to analysis/dossier, so it is accurate and does not claim that all JSON is byte-identical.
- The seal (12:43:13) came before the raster run (12:43:59), and both raster and strict carry the cohort hash `90344ae1`. This meets release condition 3.

**Raster**
- argv matches r2; exit 0.
- 44 documents, 1,958 pages, all 1190×1684 at 144 dpi, 0 page-bound violations.
- 3,921 files = 1,958 × 2 + 5 sidecars. No extra `.png` or `.txt` files.

**Strict**
- argv matches r2; exit 0.
- `{"documents":44,"pages":1958,"failures":[]}`.
- The checker is unchanged (`a68250a4…`).

**First-page coverage**
- All 44 `page-01` PNG hashes equal the `FULL44-READINESS` coverage.
- Coverage split: root 8, authority 16, domain 20.
- All three observation records match their hashes, and each reports 0 findings.

**Appendix reuse, all 1,914 pages**
- The appendix key set equals the index key set.
- Every current PNG equals its retained r4 PNG byte for byte, with 0 mismatches.
- Every r4 PNG, prior observed PNG, observation ledger, contact image, contact manifest and coverage record rehashes cleanly (6,115 distinct files, 0 failures).
- The render record matches the files on disk.
- Inspection levels: CONTACT 1,866, NATIVE 48.

**Pages I viewed myself** (7 native PNGs):
- `steel-{public,simulated}-{en,ar}-page-01`, `polypropylene-public-en-page-01`, `alu-profiles-simulated-ar-page-01` (the longest report, 73 pages) and `steel-simulated-ar-page-02`.
- Steel:
  - Page 1 fits on one physical page with a legible font and no clipping.
  - Evidence roles are separate: "Evidence passport ledger: S-WITS-721049 S-UNICOIL-EPD" and "Public evidence contradictions: S-UNICOIL-SPEC". Both have correct Arabic labels, with RTL shaping and the IDs kept as LTR runs.
  - Public pages have no simulation banner. Simulated pages show the bilingual banner and footer, the unchanged public INVESTIGATE, and 104 / 57.509 / 0.2667 / 18.
- PP shows only the support group (zero contradictions), with no invented "none" line.
- The appendix starts on page 2 with the contents list.
- The SPEC contradiction is real source data: `data/snapshots/public/SAU-H0-721049.json:331` reads "Published coating range differs from EPD…". It is propagated only into the public contradiction register.

**Preservation (re-checked at the end)**
- W and the positive copy match all 1,761 ledger rows. The negative copy differs only in `graph.css`.
- All 45 indexes match.
- HEAD is `ce407db`, with 0 staged paths.
- No writer has its working directory in W.

### Retained from earlier records, not re-run
- 38 first-page native views by Codex root, authority and domain agents. The domain observations are case-specific. The root record reuses one observation text per case.
- The original contact/native appendix observations, and their closure through the retained r4 readiness review `4fcd30d3…`. I did not reopen that review.
- The `aa81288` base-image lineage (the base image isn't present locally).

**Limitation:** most appendix pages in the "all pages" cases (steel, PP, route-8 aluminium, longest EN/AR) are covered at contact-sheet level through exact-pixel lineage, not native glyph reading. That is the procedure already accepted and hash-bound in the manual brief. I am not claiming 1,958 fresh views.

---

## B. Canonical operation: APPROVE (GO)

### B.1 Checks I performed myself

**Host command**
- Compared with the retained S19-1 `COMMAND.json`, the only argv change is change_ref `-1` → `-2`.
- The environment adds only `UV_NO_SYNC`, `UV_OFFLINE` and `UV_PYTHON_DOWNLOADS`. The working directory is W in both.
- **Docker argv:** I loaded the stock runner in memory and ran `build_command(update, S19-BILINGUAL-DOSSIER-2, 1000:1000, W)`. It reproduces r4's `docker_argv` exactly.
- **What the runner and update path write** (from `visual_baselines.py:262-424`): only the baseline root (through the `.candidate`/`.previous` swap) and `.artifacts/e2e`. The swap enforces the 128-row matrix and the byte budgets (≤614,400 per file, ≤16,777,216 total). The runner checks ownership afterwards.
- `.candidate`/`.previous` are absent, and `canonical-execution/` is absent.
- Image `938b…` is present. No `ior-s19*` containers exist.

**Visual source closure**
- I re-implemented `_source_hashes` from lines 154-192. It gives 109 paths in both W and the copy, equal to r4's `source_hashes`. The 2 fonts equal r4's `font_hashes`, and the 6 supplemental producer files match.
- Differences from the S19-1 `source_tree` are exactly:
  - `dossier.py`;
  - `test_graph.py`;
  - `current.json`;
  - the new `6f43` projection and manifest in place of `ccd1`.
- This matters because the helper requires `manifest.source_tree == BIND['source_hashes'] == _source_hashes()`. Mounting r4 itself as `/binding.json` therefore works.

**Helper**
- The diff against the retained helper is exactly one line (`:28`, change_ref `-1` → `-2`). There is no logic change.
- Both codec commands differ from the retained `CODEC-COMMAND` only in the `/old`, `/binding.json` and `/evidence` mounts.

**Predecessor trees**
- Both trees have 130 files matching r4's `files`, and the manifest and sidecar hashes match.
- The ce407 tree is identical to `git ls-tree ce407db` at the blob level, with 130 paths.
- The S19-1 tree equals W's current baselines, with 0 mismatches.
- The producer keys and font hashes the helper checks are equal across both old manifests and r4.

**Pre-existing artifacts**
- The 50 files in `W/.artifacts/e2e` are 48 dossier-bounds files (16 JSON plus 32 initial/leftmost PNG), `server.log` and `run-summary-visual.json`.
- The originals and the external copy both match `7dd2091a`, share 0 inodes and are owned by uid 1000.
- `.artifacts/` is gitignored.

**Host environment**
- 42 `METADATA` files plus `pyvenv.cfg` = 43, all matching. There are no unbound `METADATA` files.
- The interpreter resolves to the bound path and hash. `pyproject.toml` and `uv.lock` match.
- uv is 0.11.31. A parse-only probe of the exact flags outside the project (`/tmp`) raised no flag conflict. I did not probe inside W.

### B.2 Adjudication of the brief's five details
1. **Artifact overwrite: allowed.** The stock producer may overwrite only `W/.artifacts/e2e` (plus its own baseline swap), and only after the preservation copy is re-verified. No purge, move or deletion of history. External output directories must be fresh and owned 1000:1000.
2. **Host environment: accepted.** `UV_NO_SYNC`, `UV_OFFLINE` and `UV_PYTHON_DOWNLOADS=never` with the stock argv. There is no claim of fresh lock resolution, and no install, pull or retag. The image is `938b…`; the declared base `aa81288…` is attributed, not re-proven.
3. **Helper: accepted.** One literal change, and two read-only proofs against the same single capture. I verified the old manifests, raw-tree identity, producer, budgets and coverage independently (see B.1).
4. **Scope: accepted as written in `pixel_scope`.**
   - Compared with S19-1, the only new eligibility is the 8 steel dossier paths and the displayed run-ID text.
   - Compared with ce407, the cumulative comparison inherits the reviewed 16-dossier and ≤56-chart eligibility.
   - Reusing an earlier observation of a pair requires both members to match on raw and decoded identity, plus the view ledger and the accepted closure.
   - No transitive comparisons, no forced counts, and no relabelling of Codex approval as Claude approval.
5. **Stop rules: accepted as written.** Rehash immediately before launch. The first unexpected failure stops the run and is preserved. No automatic retry.

### B.3 Genuine blockers
None.

### B.4 Execution conditions
The delegated release must record these.

1. **Proving the artifacts are fresh.**
   - Record the UTC launch time.
   - After exit 0, all 48 dossier-bounds files, plus `run-summary-visual.json` and `server.log`, must have mtimes at or after launch. Record their inventory and hashes.
   - Copy the whole new area to the external capture evidence root before any later browser run.
   - Any file that wasn't rewritten is stale, and that means STOP. The PP bounds may legitimately be byte-identical to the old ones, so hash equality proves nothing about freshness; the mtime check is the one that counts.
2. **External roots.** Create `canonical-execution/{capture,immediate_s19_1,delivered_ce407}` empty and owned 1000:1000 before any `--mount`:
   - a bind source that doesn't exist fails the mount;
   - the helper writes with `open('x')`.
3. **Pre-runner uv refusal.** If `uv` exits nonzero before the runner starts (no container created, and a rehash shows the baselines and `.artifacts` unchanged):
   - record it as a preflight stop that does not consume the allocation, and return it for review;
   - do not retry, and do not edit the flags.
   - Any failure after the runner has started consumes the single allocation.
4. **Order.** Run the steps strictly in this sequence:
   1. Capture exits 0 and passes the runner ownership check.
   2. Postcheck the paths: exactly the 130 permitted outputs differ from the `c104d456` ledger; the other 1,631 rows are byte-identical; `.candidate`/`.previous` are absent; the `.venv` metadata set is unchanged.
   3. Run each codec proof once, with `/binding.json` equal to r4 (`7cbf9a77…` rehashed at launch) and stdin equal to `e4fddc81…`.
5. **Handoff hash.** Bind the current `HANDOFF.md` hash in the release. r4's `b90d96d6…` has been superseded by additive handoff updates.

### B.5 CARRY (future work, not required for this GO)
- **Independent review of all 128 images after capture**, in both contexts, under `pixel_scope`: fresh native views, or exact-pair reuse with both members' raw and RGB identities. It also covers the 16 fresh bounds records and the 32 PNGs.
- **Pins:** the `test_frozen_public_evidence_pins.py:48` tree OID through a new alternate index, and `test_s17_status_docs.py:35` → `-2`.
- **R1:** actual `a1dc…` (ce407) → `6b54…`.
- **Records and candidate:** new ledger, durable records/controls, exact candidate, all Task 6 gates, two clean-root CI runs each with its own 44-PDF proof, Claude exact-tree and head reviews, delegated acceptances, GitHub/main, and Aura.
- **Scope of this readiness:** A's approval binds only cohort `90344ae1` on `c104d456`. Any later change to graph- or visual-hashed source reopens it.
- **Unrelated container:** `ior-aura-operator-proof-20260923` (neo4j, up 17 h) is running. It is outside this unit, and the capture runs with `--network=none`. Don't stop it here; it matters for the later Aura exclusivity check.

### B.6 Preference
The root first-page record reuses the same observation text for pages within a case. Page-specific notes would be stronger evidence. I viewed those four steel pages myself, so this doesn't block anything.

---

## Sanad
**Direct:** every hash, diff, set equality, argv reconstruction, source-closure recomputation, git-blob comparison, cohort and predecessor diff, lineage rehash, and the 7 native page views listed above. All are read-only or in-memory.

**Attributed:** 38 first-page views by Codex agents; the original appendix contact/native observations and the r4 closure (`4fcd30d3…`); the `aa81288` base lineage; historical runs that I did not re-run.

**Unverified:** every future capture, codec or manual result.

## Muhasabah
- **Khawatir (first framing):** "Receipts are green and hashes match, so APPROVE." I didn't accept that on its own.
- **Muraqaba (watching for bias):** I didn't rely on the cohort-seal wording. My own JSON diff showed that the steel layout and summary files differ as well, so I checked that the seal's claim is correctly scoped. I didn't rely on the reuse counts either; I rejoined all 1,914 pages myself. And I viewed the steel pages myself rather than trusting template observations.
- **Mujahada (the actual work):**
  - Reading the runner, helper and update code surfaced the stale-artifact risk (condition B4.1) and the need to pre-create the output roots (B4.2).
  - Reading uv's flags surfaced the unverified in-project `--locked` + no-sync behaviour (B4.3).
  - Recomputing the 109-input closure confirmed that r4 works as `/binding.json`.
- **Gate:**
  - Provenance: PASS.
  - Assumptions, stated: the image stays present; nothing writes to W or the copies before the preflight rehash.
  - Fabrication: PASS. No capture or codec result is claimed.
  - Requirements: PASS. Separate verdicts, full hashes, what I checked versus what I attributed, conditions, CARRY and the erratum are all given.
  - Risk: PASS. Read-only review, except harmless `/tmp` stdout from the uv parse probe. W, the copies, the indexes and the environment were unchanged at the end.

Nothing was written. Save this text externally.
