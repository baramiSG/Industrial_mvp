# Plan review — s13b plan-1 (attempt 1)

**Subject:** `.autonomous-workflow/plans/s13-public-universe-screening/cycle-1/plan-1-s13b.json` (SHA-256 `560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e`, 168,449 bytes), authored by `planner-fable` against base `ab4add6`; mirror `plan.md` in this folder.
**Supervisor (owner lead agent) material review — 2026-09-12:** no B1–B7 finding. Independent review by `reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: screening routes stay public-only (no `mode` parameter; DD-1, SC-9); KL-34 returns a null formal state with disposition `NO_CANDIDATE` and a registered reason code — never `ADVANCE` (DD-5; SC-2 protects both goldens and the simulated outcomes); TL-09 synthetic-leakage extended to API and DOM (DD-10); thresholds untouched; `data/**` and the seven frozen configs byte-identical (SC-3); UX-01 parity delivered through governed catalogues, not machine translation, with EN templates proven byte-equal to engine prose (DD-3/DD-4).
- B2: the KL-34 fixture recipe was executed against the live engine by the planner (raises today at step 8); route-order shadowing in `app.py`, the CLI lexical-selection defect, catalogue validators/pins and the hard-coded visual matrix size were inspected in code; assumptions are flagged as BF-24 for T0/T6 confirmation.
- B3: exact oracle strings for every gate (INTEGRITY PASS, four reconstruction lines, `VISUAL_MANIFEST_OK 56`, `ES MODULE CHECK PASS`, 118+ functional nodes, goldens by direct `analyze`), the UX-01 predicate (DD-9) with exemptions limited to source-language islands and technical values, route-mocked UNAVAILABLE/PARTIAL/empty states, keyboard/axe/RTL gates, and the pre-push portability copy (DD-14).
- B4: Manifest §7 mapping complete — §7.3 `ui_strings` and `decision_narratives` 1.1.0 → 1.2.0 additive; §7.4 Core 01/03/07/09; frozen visual oracle regenerated once in the canonical container with the tree-OID pin and `VISUAL_BASELINE_ENTRIES` updated; exactly one `build_manifests.py` run after all governed text (T10; SC-4).
- B5: RED-first tests named per task; the engine change (T3/T4) precedes the surface (T6) and browser acceptance (T7); the visual regeneration (T8) precedes authority text and the manifest run.
- B6: no external navigation from passport references (OD-9); offline browser tests; no credential involvement; TL-09 on every screening view.
- B7: OUT respected — no acquisition, engine rule, queue or snapshot semantics change; no deep cases, graph, executive mode, dossier redesign, live connectors.

## Owner rulings (local record `.autonomous-workflow/owner-decisions/20260912-s13b-plan-1-rulings.md`)

OD-1, OD-2, OD-3, OD-5, OD-8, OD-9 ACCEPTED as proposed. OD-4 ruled to the ALTERNATIVE with an owner-lead WIP commit of the T8 file set so the reviewed tree is fully green (the implementer never touches git state). OD-6 moot (Docker available under OR-6). OD-7 pre-ruled stop-and-report. OD-10: implementer ladder starts at `implementer-sol` (fresh instance); `reviewer-grok` fresh instance.

## IAC (transferred to the implementer)

- IAC-1 The regenerated visual set must come with a measured drift table per entry (mask bounding boxes) and before/after crops of every changed region for both locales stored under `.autonomous-workflow/evidence/s13-public-universe-screening/visual-s13b/` (local-only, never in the repository), so the reviewer can inspect the actual rendered changes.
- IAC-2 Identity recipe as in s13a (modified ∪ untracked-not-ignored, both S13 slice-record folders excluded, top-level `base` = HEAD which will be the OD-4 WIP commit; a deleted path is encoded `{"path", "sha256": null, "bytes": 0}`); print every verification command from the JSON before running it; `PYTHONPYCACHEPREFIX` outside the repository.
- IAC-3 No machine-specific absolute path in any governed artifact (visual `manifest.json` entry paths and `source_tree` keys must be repository-relative); assert with a grep for `/home/` over `browser_tests/baselines/**` and every new fixture.
- IAC-4 Every UNAVAILABLE / PARTIAL / empty-queue state is exercised through route-mocked fixtures or a tmp data root — never by mutating `data/**`.
- IAC-5 `make ci` (exit 0) before every hand-off; the T8 hand-off to the owner lead happens with the functional suite green and the regenerated set validated (ownership, image, manifest, compare).
- IAC-6 Arabic content checks are semantic, not only the DD-9 predicate: the implementer records, for one deep case and one screening record, the Arabic rendering of every rule title, result and effect and confirms it is catalogue-sourced (key → value), and that Western digits, Gregorian dates and LTR technical islands follow the S07 presentation defaults.
- IAC-7 KL-85 (routed shell deferred) and any new limitation discovered in the surface are recorded truthfully; no limitation may be closed by wording.

### Independent plan review — `reviewer-grok`, 2026-09-12: REJECT (one B3 finding), no B1 block

Subject hash matched (`56069502…`). No B1: screening public-only, KL-34 cannot `ADVANCE`, goldens and `config/screening.v1.yaml` frozen, one manifest run; the OD-4 owner-lead WIP-commit protocol does not weaken the frozen-tree pin provided the implementation review inspects the WIP set plus the delta versus `ab4add6`.

- F-1 (B3, VALID — owner-verified): the T7 passport click-journey is unsatisfiable on the frozen snapshot — 0 of 5,443 records carry `evidence_ids`, so `/api/screening/records/{hs6}` always returns `evidence_passports: []`; the eight universe passports live on `summary.json`; the not-evaluated list is `summary.common_record_fields`, not a record field. Correction: amendment AM-1 (OD-11) — summary-level passport cards, record "evidence basis" block linking to them, rewritten T7 oracle.
- Advisory on DD-9 (owner-elevated into AM-1): the parity predicate is necessary but not sufficient — it can pass while English prose remains inside `dir="ltr"` islands; AM-1 adds the two-part predicate (no Latin prose outside islands; every island is a technical value or a captioned verbatim source span).

Record: `.autonomous-workflow/evidence/s13-public-universe-screening/plan-1-s13b-review.json`.

### Amendments AM-1 and AM-2 (2026-09-12) — PLAN_APPROVED

- AM-1 (`plan-1-s13b-amendment-1.json`, SHA-256 `341d813f6988e9ac4621b047c9762220e0f4831f290a7a66814ce12b108105d9`): closes F-1 (summary-level passports), strengthens the DD-9 parity predicate (two-part; 11-class technical grammar in `browser_tests/parity_grammar.py`), reflects OD-4 (owner-lead WIP commit) and OD-10 (seats). It surfaced that `GET /api/screening` exposes no passport data; owner decision OD-12 selected the ALTERNATIVE — one additive read-only route `GET /api/screening/evidence`. reviewer-grok: REJECT F-AM1-1 (B3 — AM-1's oracles were written for the withdrawn default).
- AM-2 (`plan-1-s13b-amendment-2.json`, SHA-256 `fae4ec0276077609bbb049472470a682b36a55ada43b5633bda2b6ceca46a58a`): reconciles every clause with OD-12-alternative (A-1…A-10): T2 owns the route with three named tests and a key-set pin; `api.py` additive-only with verification [25] `API_ADDITIVE_ONLY_PASS`; one persistent `#screening-evidence` region with eight `#passport-<id>` cards and record-view anchors (OD-14); UNAVAILABLE/PARTIAL fixtures mock all four routes with a leak check; KL-86/KL-89 and Core 03 §4.10/ADR-020 wording; `label_leaks` mitigation for the parity grammar. reviewer-grok round 3: **APPROVE**, no findings. Precedence AM-2 > AM-1 > base.
- Reviewer advisories carried to the implementer (binding): IAC-G1 load `strings.en`/`templates.en` for the leak check and apply the same normalisation to islands and EN values; IAC-G2 `reason.no_screening_snapshot` EN must not equal the token text; IAC-G3 never `display:none` `#screening-evidence`; IAC-G4 AM-1 oracles [1]/[3] (`#universe-unit-*`) are withdrawn; IAC-G5 the reviewer's earlier IAC-4…IAC-8 (T4/T5 key order, tab-order wait, Core 07 CANDIDATE paragraph, ≥10 source-language islands, leakage glob) still apply.

Records: `.autonomous-workflow/evidence/s13-public-universe-screening/plan-1-s13b-review.json`, `plan-1-s13b-amendment-1-review.json`, `plan-1-s13b-amendment-2-review.json`. Owner decisions OD-1…OD-14 in `.autonomous-workflow/owner-decisions/20260912-s13b-plan-1-rulings.md`.
