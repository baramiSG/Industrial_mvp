# Independent exact-tree implementation review: S19 Bilingual Decision Dossier

## Verdict
- **Source correctness (review questions 1–5): APPROVE.** Scope is exactly tree `7c25b4616679d61f173f3d9072e3240e1a2a166b` (proof commit `29bf5db55adaa57de2fa1f78aa5c9a028f31dc75`, freeze `80c60cab802b6c851c2cfa5a7d18056e3564abedc4c3e6a6c65fc80bce32e20f`). I found no substantive product, test or record defect.
- **Overall implementation acceptance: BLOCKED** until the pending exact-tree gates pass and are independently closed. This is a gate-completeness block, not a source violation.

I ran no tests, browsers, services or product imports, and wrote nothing. Every Git call used `GIT_OPTIONAL_LOCKS=0`. All 53 protected indexes matched at the end.

**Personas:**
- bilingual decision-document product reviewer
- test-quality reviewer
- change-control and provenance auditor

**Skills:** the six installed skills, unchanged, applied. The PDF skill at the nested installed path adds no requirement beyond the plan's Task 4.

## Direct checks

**Subject integrity**
- The ci-root2 files I read are byte-identical to the tree's blobs: `dossier.py`, `dossier_projection.py`, `dossier_validation.py`, `app.py`, both dossier unit-test files, `state.json` and `implementation-log.md`.
- `tests/test_static_frontend.py` in the tree has blob `c8fd5341…`, which is the approved `7c5badd1…`.
- The tree contains no self-reference to `7c25`, `29bf` or `80c6`.

**Change boundary (Q4)**
- Compared with `ce407`: 1,748 paths (1,610 added, 138 modified). Outside the delivery-evidence and accepted-packet copies, the product, test, config and doc changes are exactly the 60 listed paths.
- Every product path is in plan §"Exact permitted file set" or an accepted amendment:
  - `config.py`, `graph_fixtures.py`, `test_authority_disclosure.py`, `test_es_modules.py` and `test_s17_graph_contract.py`: amendment 05, lines 38–42, and the diffs match those grants exactly.
  - `trade.js`, `workspace.css` and `test_trade_chart.py`: amendments 11/14.
  - Test literal updates: amendments 08/09.
- The planned `dossier_rendering.py`/`dossier_sections.py` split was not created. Fewer files, so no scope issue.
- No change to decision engine, thresholds, evidence policy, profiles, snapshots, scenarios, goldens or schemas (none appear in the name-status list).
- Catalogue `1.6.0` → `1.7.0`: **0 existing EN/AR values changed, 0 removed**, 365 added (`dossier.*` plus 6 `trade.*`), and EN/AR key parity holds.
- The authority manifest and hashes change only in the generated table rows (catalogue and four Core docs).
- No `config/history` copy is needed: Core04 §11.1 requires one only for configurations referenced by screening snapshots, and integrity passes.

**Projection (Q1): `dossier_projection.py` and `dossier_validation.py` read in full**
- Validation fails closed with a typed error on malformed required shapes.
- Public mode never loads scenario context and rejects any synthetic passport or rule.
- Simulated mode checks the scenario identity, version, source, class, flag and both policy labels, plus every synthetic passport's identity.
- The whitelist exactly matches the plan table. Unreviewed scenario fields raise an error. Buyer allocation goes through the existing validator.
- Scenario passports must exist under their exact ID.
- Scalar statuses: `AVAILABLE` for genuine numeric values, including 0; null → `NOT_CALCULABLE` (numeric fields) or `UNAVAILABLE`; non-finite or boolean numerics raise.
- Missing economics are `NOT_CALCULABLE`; `downside_result` and `sunset_date` are never invented.
- `internal_d_star` is not projected into the blocks.
- Route 8 external dependencies are computed separately from local passports.
- `build_dossier` returns a full `deepcopy`, and `public_decision` is the detached `real_decision`.

**Rendering and safety (Q1 and Q3)**
- One escaping helper (`escape(..., quote=True)`) is used throughout.
- Technical tokens go in LTR `bdi`. Source islands carry `lang`/`dir` set by script detection.
- Passport URLs become links only for `http`/`https` with a host; anything else is escaped text.
- The footer disclosure goes through the hex-escaped `_css_string`.
- There are no inline handlers; the only script is the external module `dossier-actions.js`.
- The return and download URLs are built with `quote`/`urlencode`.
- Rule ledger names, results and effects use `rule.localized[locale]`.

**Probes of the actual exports** (22 `-dossier.json` and 44 HTML from the functional cohort, whose product bytes equal the tree):
- Every export has routes 0–8 in order, for both active and public decisions.
- Public JSON and HTML contain no `SYN-`, `DEMO_GENERATOR`, synthetic flags or disclosure text.
- `internal_d_star` appears nowhere, and there are no raw dict/JSON dumps.
- There are no `<script>` elements other than the module, and no `on*=` attributes.
- Economics: 0 never becomes non-available, and null is never `AVAILABLE`.
- Every simulated block is tagged Class D with labels.
- External dependencies appear only on route 8, in the two aluminium simulated cases, each pointing at the other case's `::shared_enabler`.

**D-S19-1 (Q2)**
- Summary: first two public passports under "Evidence passport ledger", public contradictions as a separate group, the group omitted when empty, dual-role references kept, existing catalogue keys only.
- I verified this earlier, on these same product bytes, with mutants and in-memory rendering (review `7e78bf3b`). I also viewed the four steel first pages and the canonical steel dossier images (`c3fece87`, `c32c3425`).
- The steel `S-UNICOIL-SPEC` contradiction is real source data.

**Tests reviewed as product code (Q3)**
- The dossier tests cover:
  - detachment and no mutation of the analysis;
  - no scenario load in public mode;
  - typed-422 matrices for mismatched scenario identities, malformed required and optional shapes, rejection conditions and trade years;
  - unsafe URLs;
  - a manually enumerated source oracle and a consumer-coverage check of the literal mappings;
  - Arabic ledger localisation;
  - attributed source prose;
  - print introductions;
  - summary separation, empty-group and dual-role cases;
  - 44 Executive→Analyst→Dossier journeys, keyboard/print/download/return, and responsive bounds;
  - failure states for missing case and invalid mode;
  - distinct empty/unavailable/zero;
  - a trade table checked against the full public source in sorted order, in both locales, for three consumers, at narrow widths.
- The trade renderer sorts a non-mutating copy, adds a native data table and a scale note, and escapes everything.
- Earlier mutant evidence (`7e78bf3b`) showed the new tests catch the original defects.

**Records (Q5)**
- `state.json` and `implementation-log.md` are additive; historical blocks are preserved.
- Both index incidents, the failed `c746` gate (still FAIL), the test correction and every pending gate are recorded truthfully.
- `KNOWN_LIMITATIONS` keeps KL-33, KL-84, AR-V01 and TRADE-SCALE-01 **OPEN** pending review and gates. That is truthful at source freeze.
- `.workflow/slices/S19-bilingual-dossier/delivery-evidence/` and accepted packets 00–26 are present. Historical Codex approvals keep their Codex attribution.

**Retained and attributed (not re-run)**
- Offline gates: 14 of 14 exit 0 (`RESULTS.json` `1f2be1cf…`; full pytest 3,982 passed); preservation `190fea71…`.
- The earlier 839 functional run, the 44-PDF strict/raster evidence, and the manual lineage.
- Generation `6f43`/`6b54`, manifest `0d05eee7…`, pin `65a71b38…`.
- The historical Codex reviews.

## Findings

**Genuine blockers (source):** none.

**Gate completeness (this is why the overall verdict is BLOCKED):**
1. **Compare-only `make e2e` on this exact tree** is still running (about 19 minutes elapsed). No result yet. It includes the behavioral Arabic-font and journey checks on these frozen bytes.
2. **Actual-predecessor R1** (`a1dc` → `6b54`): my GO (`80e58dd6…`) is conditioned on e2e exiting first. `runtime-output/` is absent, so there is no result.
3. **Two clean-root `make ci` runs, each with its own 44-PDF proof:** pending.
4. **After those pass:** targeted closure, then exact-head review, delegated acceptance, GitHub/main, and the separate Aura checkpoint.

**CARRY:**
- After delivery, close KL-33, KL-84, AR-V01 and TRADE-SCALE-01 in an additive record, citing the passed gates. Do not close them before then.
- Exact-tree e2e/CI must be the evidence for Arabic font behavior on these bytes. Earlier browser results must not be transferred.

**Preferences (non-blocking):**
- `render_dossier_html` routes (`dossier.py`, the `routes()` helper) label *any* route evidence ID missing from the local passports as an "external dependency", whereas the projection limits external dependencies to route 8. No current data triggers this; I checked all 22 exports. Consider rendering from `evidence_pack.external_dependencies`, or failing closed for non-route-8 unknown IDs.
- The summary metric cells append the unit after a status, e.g. "Unavailable kt" and "Not calculable ratio". Cosmetic. It was accepted in earlier reviews, and I'm not reopening the design.

## Sanad
**Direct:** tree/blob equality; the name-status and diff reads; the amendment greps and grant matching; full reads of the projection, validation, renderer and app wrapper; the catalogue diff; the export and HTML probes; the test inventory reads; the records reads; the 53-index rehash; and the gate-state observation.

**Attributed:** the root offline executions; the earlier cohort, canonical and D-S19-1 evidence (reviewed by me earlier, not re-run now); the historical Codex reviews.

**Assumption, stated:** the functional-cohort exports reflect these product bytes. Product sources are unchanged between ledger `c104d456` and tree `7c25`; only records, pins, baselines and the test file differ, which I verified earlier.

**Unrun:** every browser, test and CI gate on this tree.

## Muhasabah
- **Khawatir (first framing):** "Green offline gates and many prior approvals, so APPROVE everything." I rejected that.
- **Muraqaba (watching for bias):** I separated source correctness from gate completeness, and checked scope against actual amendment text rather than the brief. I probed actual exports rather than trusting the tests alone.
- **Mujahada (the actual work):** surfaced the latent route-renderer external-label generalisation (a preference) and confirmed the catalogue is additive-only.
- **Gate:**
  - Provenance: PASS.
  - Fabrication: PASS. No gate result is claimed.
  - Requirements: PASS. Scoped verdict, findings and a separate gate-completeness list are given.
  - Risk: read-only; indexes preserved.

Nothing was written. Save this text externally.
