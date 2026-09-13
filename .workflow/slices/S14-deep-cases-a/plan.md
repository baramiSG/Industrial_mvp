# S14a — Case selection, evidence and families: plan-1 (mirror)

Machine record: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14a.json`
(SHA-256 `8fbfa4e6ffa3b70c3c17d987ba5ee2267963204843d0834444d99cd1b7548169`; the JSON is binding, this
Markdown is a mirror). Child 0 of the S14 decomposition (`decomposition-1.json`
`48741467ed2e3d6185cb0e5aac13b56d6c9d81847a3b114b960547740b877f3a`).

Seat: `planner-fable`. Base: `origin/main` at dispatch (`ab6211f8…` at planning; T0 records the exact
sha). Branch: `slice/s14a-case-selection-evidence-and-families`. Implementer: `implementer-sol` first
(recorded deviation), `implementer-fable` fallback; `reviewer-grok` sole approver. Docker not required.

## Objective (abridged)

Deliver the S14 evidence base without touching the portfolio, the frozen roots or the visual oracle:
(1) selection rule S14-CS-1 as code, executed once on the frozen screening snapshot, pinned and
recorded; (2) `config/product_families.v1.yaml` 1.1.0 (PR-1) with superseded bytes retained under
`config/history/` and the screening input check resolving recorded config inputs by content hash;
(3) `config/acquisition_sources.v1.yaml` 1.4.0 with producer sources Hadeed, ALUPCO, Al Taiseer/TALCO,
Ma'aden, their DocumentLists and one recorded window W-A (+ W-T TLS observation, + W-P WITS partner
detail under OD-5); (4) mentions-v2 and a second ENTITIES artifact; (5) CaseBrief 1.0.0 and the
deterministic PublicSnapshot builder with five briefs proven by building into a temporary directory and
running the public engine (expected INVESTIGATE, route null — recorded, never forced); (6) Core
02/04/05/09 text, ADR-021, KLs, runbook, control documents, the SLICE_GRAPH §5 split record, exactly
one `build_manifests.py` run, uncommitted hand-off with IAC-6 identity.

## Tasks

| Id | Goal | RED tests (exact names in the JSON) | Oracle strings |
|---|---|---|---|
| T0 | Preflight/baseline: branch, clean tree, gates, counts, frozen tree OIDs, BF-18 confirmation | — | `BRANCH_OK`, `INTEGRITY PASS`, `SCREENING RECONSTRUCTION PASS (1 snapshots)`, `SMOKE PASS`, `2275 tests collected`, `VISUAL_MANIFEST_OK 56` |
| T1 | Selection rule as code + term table + recorded list | `tests/test_case_selection.py` (10 tests incl. `test_s14_selection_from_frozen_screening_snapshot_matches_recorded_list`) | `CASE SELECTION PASS (5 selected; 3 profiles)`; two runs byte-identical |
| T2 | product_families 1.1.0 + `config/history/product_families.v1-1.0.0.yaml` + screening input resolution | `tests/test_screening_snapshot.py` (4), `tests/test_screening_config.py` (4), `tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only` | `SCREENING RECONSTRUCTION PASS (1 snapshots)`; history copy sha256 `841bc5ac…` |
| T3 | acquisition_sources 1.4.0 + four sources + v1 lists (offline) | `tests/test_acquisition_config.py` (4), `tests/test_acquisition_document_lists.py` (1) | `SCREENING RECONSTRUCTION PASS (1 snapshots)` |
| T4 | Windows W-A (consultation → acquisition), W-T, W-P; builds; reconstruct | — (parameters logged before execution) | `DOCUMENT RECONSTRUCTION PASS (12+n records, 12+n artifacts)`; `RECONSTRUCTION PASS (2 or 3 snapshots, …)`; no rajhisteel.com request; size budgets green |
| T5 | mentions-v2 + second ENTITIES artifact | `tests/test_entity_resolution_artifact.py::test_s14_mentions_v2_spans_verified_and_second_artifact_reconstructs` | `ENTITY RECONSTRUCTION PASS (2 artifacts, M links)` |
| T6 | CaseBrief 1.0.0 + builder + five briefs + engine proof | `tests/test_case_brief.py` (7), `tests/test_case_projection.py` (14), `tests/test_case_briefs_real.py` (4), `tests/test_offline_guard.py::test_runtime_app_does_not_import_cases_package` | `CASE BUILD PASS (5 briefs → 5 snapshots validated; 0 committed)`; each built snapshot INVESTIGATE / route null; builds byte-identical |
| T7 | build_manifests roots, reconstruct case pass, Makefile targets, runbook | `tests/test_integrity_contract.py` (2) | `CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)` |
| T8 | Core 02/04/05/09 text, ADR-021, KLs, split record, control docs (before any manifest run) | `tests/test_integrity_contract.py::test_s14a_core_v2_case_contracts` | integrity-contract suite green except the §11 mirror until T9 |
| T9 | Pre-generation regression; **exactly one** `build_manifests.py`; §11 mirror; post-generation regression; portability copy | — | `INTEGRITY PASS`, six PASS lines, `SMOKE PASS`, `BYTE_IDENTICAL_EXPECT_0_LINES_ABOVE` (0), `VISUAL_MANIFEST_OK 56`, `FROZEN_OUTCOMES_OK`, `PORTABILITY_PASS`, `make ci` exit 0 |
| T10 | IAC-6 identity; stop uncommitted for reviewer-grok | — | `CANDIDATE_IDENTITY`, `INDEX_EMPTY_PASS`, `PROTECTED_SET_BYTE_IDENTICAL_PASS`, `STATE_JSON_VALID_PASS` |

## Selection rule S14-CS-1 and computed list

Tiers T1 robust → T2 high-EVSI → T3 LFP continuity-only → T4 price-led → T5 ratio warning → T6
unqueued → T7 NO_CANDIDATE (never); viability = positive 2024 import net weight; in-tier order:
disclosure-covered (stored producer records) → R2 fired → 2024 imports USD desc → hs6 asc; quota 2/2/1.

Default result: coated_steel **721061, 721012** (subs 721069, 721041, 721011, 721020, 721090);
fabricated_aluminium **760711, 760429** (subs 761610, 760421, 760519, 760511, …);
technical_plastics **390220** (subs 390230, 390290). Without the coverage key: 721012, 721069.
PR-7's literal two-queue rule is empty for all three profiles (verified).

## Manifest §7 mapping

- §7.2: `src/ior_mvp/cases/**` (new, offline); `screening/config.py` (pin 1.1.0); `screening/snapshot.py`
  (history resolution); `acquisition/source_config.py` (four sources, pin 1.4.0); scripts; Makefile; tests.
- §7.3: `config/product_families.v1.yaml` 1.1.0 (fabricated_aluminium 7604–7614, 7616; PR-1 basis);
  `config/acquisition_sources.v1.yaml` 1.4.0; `config/history/*.yaml` retained superseded bytes.
- §7.4: Core 02 §2/§9; Core 04 CaseBrief 1.0.0 + derived-snapshot provenance + §11 retention; Core 05
  §3.2/§11; Core 09 §5/§9.
- §7.5: new raw runs, four document sources' lists/records, mentions-v2 + entity artifact, optional WITS
  partner snapshot, new root `data/cases/{selection,briefs}/**`.
- Exactly one `build_manifests.py` run (T9) after ADR-021 and full regression; permitted generated diff:
  added snapshot-manifest rows only; authority rows changed only for the two configs and Core 02/04/05/09.

## Frozen pins policy

This child: nothing under `data/snapshots/public`, `data/synthetic`, `data/golden`,
`browser_tests/**` is added or changed; `tests/test_frozen_public_evidence_pins.py` byte-identical;
verification [8] and [10] print 0. Built snapshots live only under `/tmp`. Next child (s14b): the
owner-lead WIP protocol (s13b OD-4/OD-15/OD-16) updates the three tree OIDs and `VISUAL_BASELINE_ENTRIES`
once, with additions-only proof and the four per-file PINS unchanged.

## Stop conditions

SC-1 golden change; SC-2a frozen root / top-level module / pinned config change; SC-2b a brief's
engine state ≠ INVESTIGATE (reassess honestly, never adjust inputs); SC-3 any public fact without a
verified span; SC-4 synthetic marker in public artifacts; SC-5 robots/login/TLS → no request, no bypass;
SC-6 raw-store budget; SC-7 post-manifest-run authority edit or a changed pre-existing manifest row;
SC-8 portability/absolute path; SC-9 any other screening input config change; SC-10 reviewer
infrastructure (OR-2 applies to the reviewer seat only).

## Open decisions (defaults)

OD-1 two-child split; OD-2 selection keys (tiers yes; viability yes — waiving selects 721070 PPGI;
coverage key yes — dropping selects 721069); OD-3 technical_plastics 3902 only → 390220; OD-4
`config/history/` retention; OD-5 W-P WITS partner window (open, MAX_REQUESTS=6); OD-6 source set
(Hadeed, ALUPCO, Al Taiseer/TALCO, Ma'aden; no Tadawul, no PP producers); OD-7 accept unreachability
KLs; OD-8 `SAU-H6-<hs6>` + H6-only series; OD-9 names from stored WCO spans if the WCO consultation
permits acquisition, else flagged descriptions; OD-10 seats.

## Sanad / muhasib

Every baseline fact carries a path/line or a read-only command executed at `ab6211f`; PR-7 was executed
literally and found empty before the extension was proposed; no ledger figure is used as evidence; the
INVESTIGATE expectation is a derivation guarded by SC-2b; assumptions BF-18 (a)–(d) are to be confirmed
at T0. Nothing was implemented, committed, fetched or read from `.env`.

## Amendment AM-1

Gated file: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14a-amendment-1.json` (overlays
plan-1-s14a `8fbfa4e6…`; where they differ, AM-1 controls; the two gated JSONs are byte-unchanged).
Trigger: owner rulings `.autonomous-workflow/owner-decisions/20260913-s14-plan-1-rulings.md` (`61d9b640…`) —
OD-1/2/4/5/6/7/8/9/10 accepted as defaults; OD-3 ruled as an extension: `technical_plastics` gains 3917,
3920, 3921 in the same 1.1.0 change, 3902 retained.

Re-run of S14-CS-1 (OD-2 default) over {3902, 3917, 3920, 3921}, read-only against the frozen screening
snapshot and universe: 39 HS6 lines, all CANDIDATE in likely_false_positive (23 T3 / 15 T4 / 1 T5 =
frozen 390210); every line has a positive 2024 import net weight (no viability exclusion); no plastics
producer record exists at the base store (coverage False for all). Selected: **392190** (T3, fired
R1-D + R2, 2024 imports 241.52 M USD / 98,254 t, X/M 0.19). Runner-up: **392010** (70.43 M USD, X/M 4.0).
390220 falls to substitution_order[10] — not the fallback, because viable extension lines exist.
Steel (721061, 721012) and aluminium (760711, 760429) unchanged.

Changed clauses (C-1…C-10): selection inputs/S1 (union of families per profile) and computed lists; DD-5 /
§7.3 / T2 — new family `technical_plastics_conversion` [3917, 3920, 3921] with the ruled basis text
(methodology profile row verbatim + WCO Chapter 39 titles with a `TITLE_VERIFICATION` marker filled after
W-A), `polypropylene_primary_forms` byte-unchanged, seven named family tests; T1 split into T1a (code +
doubles) → T2 → T1b (real run + pin); DD-3 terms table gains `sector_profile` and `sources` (coverage only
from listed producer sources; generic terms forbidden; recorded results unchanged); DD-6/DD-7/T4 — fifth
document source `wco_hs_nomenclature` (publisher kind `nomenclature_authority`, Class B, supports
TARGET_PRODUCT_IDENTITY; Chapter 39/72/76 PDFs, URLs read from the index page, MAX_REQUESTS ≤ 4, first in
W-A) making OD-9 executable; W-P list → [392190, 721012, 721061, 760429, 760711]; OD-6 consequence: no
plastics producer added (ledger names none for 3921.90 products); DD-9/DD-10/DD-11/T6 — brief
`CASE-BRIEF-SAU-H6-392190-v1.json`, `SAU-H6-392190`, R2 expected for 392190 instead of 390220, SC-2b
unchanged; every "ruling requested" read as RULED; OD-10 seats (implementer-sol → implementer-fable;
reviewer-grok sole approver, fresh instances).

New open decision OD-11 (before dispatch; silence = default): accept the residual subheading 3921.90
"Other" as the plastics case (default) or demote residual subheadings and take 392010 (alternative,
`--demote-residual`, rule re-run — never a hand edit).

Muhasib: membership, tiers, viability, coverage, ordering, selected/runner-up and the unchanged
steel/aluminium results were recomputed from the frozen data this session; WCO title texts, the Chapter
39/72 PDF URLs and WCO terms are UNVERIFIED until stored (flagged); no implementation, network, git or
`.env` access.

## Amendment AM-2

Gated file: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14a-amendment-2.json` (planner-fable, 2026-09-13). Amends plan-1-s14a (`8fbfa4e6…`) and AM-1 (`8c61a0a2…`); precedence AM-2 > AM-1 > base. Triggered by owner directive OD-12 (721061 partner detail) and the AM-2 planner brief. Applied as the correction round after implementer-sol's hand-off and the supervisor check, by the same implementer seat, only after reviewer-grok APPROVE.

**Defect being corrected (verified in the in-flight tree).** Brief 721061 carries `partner_snapshot_id: UNAVAILABLE`; the projection emits `partner_observations: UNAVAILABLE` and no partner passport; PublicSnapshot 2.1.0 forbids an empty partner list. So a stored-but-unparsed WITS unit (HTTP 200 after redirect to `Error.aspx`, page `UNPARSED`, derived `FORMAT_NOT_PARSEABLE` exclusion in `PARTNERS-SAU-WITS-TRADE-2026-09-12`) is indistinguishable from "never requested" and from "normalized response with zero rows" — and the connector today classifies an empty dataset as `UNPARSED`, which the builder turns into `FORMAT_NOT_PARSEABLE`.

**C-1 Tri-state in CaseBrief 1.1.0** — new required `partner_detail` block: `state` ∈ {`PARTNER_DETAIL_OBSERVED`, `PARTNER_DETAIL_MISSING`, `PARTNER_TRADE_OBSERVED_ZERO`}; `reason` (null unless MISSING; then an `UnavailableReason` member or `NOT_ACQUIRED` / `REVISION_MISMATCH`); `source_id`; `partner_snapshot_id` (must equal the retained legacy key); `unit_key` `[hs6, "imports", "2024"]`; `observed_partner_rows` (≥ 1 / 0 / UNAVAILABLE); `attempts` (one entry per stored PARTNERS unit for the unit key: source_id, query_hash, run_id, endpoint_or_document, http_status, normalization_status, coverage_status, stop_reason, contract_path, contract_sha256); `basis`. The validator reads the RawStore and partner snapshots read-only: MISSING needs a typed reason and a resolvable stored attempt (for `FORMAT_NOT_PARSEABLE` an UNPARSED/PENDING page on a transport-COMPLETE unit); OBSERVED needs a COMPLETE unit with ≥ 1 non-World row of the brief's HS revision; ZERO needs a COMPLETE unit whose pages are `NORMALIZED_EMPTY` and zero non-World rows; the cross-refusals make MISSING↔ZERO↔OBSERVED non-interchangeable. 721061 before W-C: `MISSING / FORMAT_NOT_PARSEABLE / wits_trade`, one attempt (unit `ed5759a3…/20260912T233403Z`).

**C-2 PublicSnapshot 2.1.0 carriers (no pinned edit).** OBSERVED → rows + passport `P-<WITS|COMTRADE>-<hs6>-PARTNERS` (status `calculated`, url = stored unit endpoint). MISSING → `partner_observations: UNAVAILABLE` + passport `…-PARTNERS-ATTEMPT` (status `unresolved`, url = the stored Error.aspx endpoint, transformation marker `PARTNER_DETAIL_MISSING:<reason>; unit …; this passport evidences the attempt, not trade.`). ZERO → UNAVAILABLE + passport `…-PARTNERS-ZERO` (status `observed`, marker `PARTNER_TRADE_OBSERVED_ZERO; …`). `trade_quality.execution_cap` and `authority_note` carry the state sentence. The projection refuses a brief state that contradicts the loaded snapshot. After a COMPLETE W-C the 721061 snapshot carries the Comtrade rows + COMTRADE passport + the WITS ATTEMPT passport.

**C-3 / OD-13 (new open decision, default ACCEPT).** `public_snapshot.py`, `trade_metrics.py`, `rules.py`, `evidence.py` are visual-manifest pins (SC-2a). The schema-level 2.2.0 `partner_detail` block, the validator rule "no UNAVAILABLE/empty partner list without a typed state", the `concentration_metrics` reason naming the state and the R3 result codes `PARTNER_DETAIL_MISSING` / `PARTNER_TRADE_OBSERVED_ZERO` (and the R4-D reason) are specified now and executed in s14b together with the single visual regeneration. Alternative: pinned edits in s14a with a second regeneration (not recommended). KL-100 records the interim.

**C-4/C-5/C-6 W-C Comtrade substitution window for 721061.**
- Config 1.4.0 (same in-flight change): `un_comtrade.endpoint_templates.PARTNERS = https://comtradeapi.un.org/data/v1/get/C/A/HS?reporterCode={reporter}&period={period}&flowCode={flow_code}&cmdCode={product}&motCode=0&customsCode=C00{partner_dimension_query}` — no `{partner}` token (it would inject World `0`); every literal is observed in stored rows or the working UNIVERSE template. `parameters.partner_dimension_variants`: **V1** `""` (partnerCode omitted; nothing assumed), **V2** `"&partner2Code=0"` (observed field name + observed World value; only after V1 rows show `partner2Code` multi-valued). No `all`/`ALL` token is tried — never observed.
- CLI `acquire-partners --parameter NAME=VALUE` (repeatable; reserved names refused); parameters enter the contract canonical JSON and `query_hash`, so V1/V2 are distinct hashed units under one unit key (latest run selected).
- Ladder: O-0 offline field-name observation from the stored 2024 universe payload → RUN 1 (V1, `MAX_REQUESTS=2` = 1 TERMS + 1 data) → observe verbatim (count, len(data), error, distinct partnerCode/partner2Code/motCode/customsCode/classificationCode, partnerDesc presence, World row, reconciliation vs universe) → COMPLETE: stop; INCOMPLETE only on `partner_rows_unique_per_unit`/`secondary_dimensions_single_valued` with `partner2Code` multi-valued: RUN 2 (V2, `MAX_REQUESTS=2`); anything else: stop, 721061 stays MISSING with the typed reason and both attempts listed. ≤ 2 data requests (+ ≤ 2 governed TERMS captures = ≤ 4 HTTP).
- Completeness mapping (PARTNERS unit COMPLETE iff all): JSON content type; envelope (int `count`, list `data`); `error` empty; `count == len(data)`; `count < 100000`; every row reporterCode 682, period 2024, flowCode M, cmdCode 721061; one classificationCode; no duplicate (cmdCode, partnerCode); each of partner2Code/motCode/customsCode present is single-valued; partnerDesc on every non-World row; at least one partnerCode ≠ 0 **or** a `count == 0` zero envelope (→ `NORMALIZED_EMPTY`, state ZERO, never `FORMAT_NOT_PARSEABLE`). Basis `PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000`. Failure → INCOMPLETE with typed stop reason and failing check ids. UNIVERSE validation unchanged (test). SC-11 (contradicting rows are never filtered) and SC-12 (non-H6 classification → `REVISION_MISMATCH`).
- Rows: reuse `partners` KindSpec 1.0.0 + `UnComtradeConnector.normalize` (TradeObservation; partner = partnerDesc; hs_revision H6); snapshot `PARTNERS-SAU-UN-COMTRADE-<as_of>` (distinct artifact; expected 1 complete unit + 59 historical `ENDPOINT_UNVERIFIED` exclusions, KL-102). Class B; RawStore write-once; credential only as env var `IOR_COMTRADE_SUBSCRIPTION_KEY` (name recorded, value never read/printed/stored; `.env` never read by an agent); header never stored (contract keeps `credential_env_var`/`credential_used` only; response headers filtered; echoed credential refused); budgets 16,777,216 / 100,663,296 bytes (store now 41,673,354). WITS snapshots `0a5a5645…` and `cdcc904a…` byte-identical after W-C.

**C-8** SC-2b for 721061: state must remain INVESTIGATE; fired set may grow by R3/R4-D — recorded, never forced. **C-9/C-10** Core 04 §12, Core 05 §3.1/§3.2/§11 (source-substitution rule), Core 09; runbook W-C row; ADR-021 "Correction round AM-2"; KL-97 rewritten truthfully; KL-100/101/102 added; KL-75/80 narrowed only to what W-C observed.

**C-11 Manifest-run count.** Case A (count 0 at hand-off — the state observed): correction before T9; one run. Case B (count 1): exactly one more run, owner-authorized under OD-12/brief §3, receipted in ADR-021 ("S14a manifest run count is 2 …"), oracle immediately; no third run. Pre-existing rows at base `ab6211f` unchanged (O-8); rows first created by this child may change because nothing is committed.

**C-12 Review obligations (OD-12(c)).** reviewer-grok verifies r1–r7: tri-state consistency of all five built snapshots; 721061 attempt passport URL = stored WITS endpoint; no credential header name/value anywhere; WITS bytes and pre-existing raw units unchanged; observed vs missing vs Class-D (none in s14a) distinguished; `identity_exclusions`/selection hash unchanged; observation table recomputed offline.

Tests T-1…T-25, oracles O-1…O-10 and verification changes [4], [11]–[14], [24]–[26] are in the JSON.

Muhasib: the defect, the validator gaps, the connector's zero-vs-unparsed conflation, the `ENDPOINT_UNVERIFIED` cause, the row fields of a stored Comtrade payload and the manifest state were verified in code/data this session; the API's behaviour when `partnerCode` is omitted is deliberately UNVERIFIED and is what W-C observes; the pinned-module limit is stated as OD-13 rather than hidden; no product file, gated JSON or owner record was modified; no git state change, no network, no `.env` read.

## Amendment AM-3

**Gated artifact:** `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14a-amendment-3.json` (planner-fable, 2026-09-13). Amends plan-1-s14a (`8fbfa4e6…`), AM-1 (`8c61a0a2…`) and AM-2 (`5bccc8a5…`); precedence AM-3 > AM-2 > AM-1 > base. No gated JSON or product file is modified by this amendment. Trigger: OD-16 (owner rulings file, sha256 `ebbc91d1…`), after the AM-2 correction round (identity `baf0b4dd…`, 141 files, manifest run count 2).

**Why.** W-C V1 (unit `e71395bb…/20260913T010452Z`) returned 8 H6 rows (1 World + 7 non-World), single-valued `partner2Code`/`motCode`/`customsCode`, no duplicates, and non-World `primaryValue` tokens summing in Decimal to exactly the universe World value `71149266.221` (net weight likewise `93232034.488`); it stopped honestly on the one failing predicate `partner_desc_present_for_non_world_rows`. Verified from the stored payload: all ten `*Desc`/`*ISO` fields are null on every row — including `reporterDesc` and `flowDesc` — and on the stored 2024 universe row; the S11 contract in git history (`a043ed8`) used `&includeDesc=true`; s13a IAC-5 names `includeDesc` as the description source. The official v1 parameter table is unobserved in-repo (KL-80): AM-3 cites the basis and lets the V3 rows prove the effect.

**C-1 Config.** One governed variant `partner_dimension_variants.V3 = "&includeDesc=true"` with `observation_basis`; `partnerCode` still omitted, no `partner2Code` pin (V1 observed single-valued 0); V2 retained unused; distinct `query_hash` under unit_key `[721061, imports, 2024]`; V1 becomes `superseded_run_ids`.

**C-2 Window W-C V3.** After reviewer-grok APPROVE only. `make acquire-partners SOURCE=un_comtrade CANDIDATES=data/cases/selection/comtrade-partners-s14-v1.json YEARS=2024 FLOWS=imports MAX_REQUESTS=2 PARAMETERS='partner_dimension_query=&includeDesc=true'`, key sourced in-shell from `.env` inside the command only. HTTP budget: 1 data request + 1 governed TERMS capture = **2** requests; no second data request under any outcome (cumulative W-C: 1 robots + 2 + 2 = 5 HTTP, 2 data). Offline `WC_V3_*` observation lines (Decimal, from the stored payload): envelope, distinct dimensions, per-row `partnerDesc`/`partnerISO`, descriptions present/unique, S, R, |S−R|, tolerance, net-weight sum (recorded), row-for-row equality with V1 (recorded), QualityReport and coverage verbatim.

**C-3 Completeness.** COMPLETE iff the fifteen AM-2 checks PASS plus (16) `aggregate_reconciles`: S = Decimal Σ non-World `primaryValue`; R = the same cmdCode's `primaryValue` token in the latest COMPLETE UNIVERSE unit of the same source/(flow, period) (`71149266.221`, identical to the universe snapshot `trade_value_original_text` — pinned by test); s = max fractional digits over the unit's tokens and R (V1: 3); u = 10^−s; tolerance = n_non_World × u/2 (V1: 7 × 0.0005 = 0.0035 USD); PASS iff |S−R| ≤ tolerance and, when a World row is present, |World−R| ≤ u/2; R unavailable → FAIL; count-0 envelope passes only if R == 0 (so ZERO is impossible for 721061 while the universe records 71.1 M USD); and (17) `partner_desc_unique_for_non_world_rows` (consequential: the 2.1.0 validator refuses duplicate partner identities). Net weight is recorded, not gated (`isNetWgtEstimated` exists). `coverage_stop_reason`: failing set exactly `{partner_desc_present_for_non_world_rows}` → `PARTNER_DESCRIPTIONS_UNAVAILABLE`; any other FAIL set → `COVERAGE_INDETERMINATE`. V1's stored coverage bytes are never rewritten; UNIVERSE validation unchanged.

**C-4 Reason vocabulary.** `UnavailableReason.PARTNER_DESCRIPTIONS_UNAVAILABLE` (enum extension; brief vocabulary inherits; explicit membership test; WITS never emits it). Brief V-a extension: this reason requires a NORMALIZED attempt whose stored stop_reason is that value. If V3 still lacks descriptions: brief 721061 stays `PARTNER_DETAIL_MISSING / PARTNER_DESCRIPTIONS_UNAVAILABLE`, attempts = [V3, V1, WITS]; no names inferred from M49 codes.

**C-5 COMPLETE path.** `make build-snapshots KIND=partners SOURCE=un_comtrade` → `PARTNERS-SAU-UN-COMTRADE-<as_of>.json` (8 rows incl. World; V3 selected, V1 superseded; 59 historical exclusions); WITS snapshots byte-identical. Brief → `PARTNER_DETAIL_OBSERVED`, reason null, `observed_partner_rows 7`, attempts [V3, V1, WITS] (V1 retained). Public snapshot via the AM-2 encoding: 7 `partner_observations`, passports `P-COMTRADE-721061-PARTNERS` (calculated), `P-COMTRADE-721061-PARTNERS-ATTEMPT` (V1), `P-WITS-721061-PARTNERS-ATTEMPT`; superseded attempts on an OBSERVED case carry the marker `PARTNER_DETAIL_ATTEMPT_SUPERSEDED:<reason>; … superseded by COMPLETE unit …` (current code would say `PARTNER_DETAIL_MISSING:` — fixed test-first). Engine re-proof: state must stay INVESTIGATE (SC-2b); fired set recorded, never forced — offline from the V1 values R3 is expected to FIRE (largest value share 0.8337, HHI ≈ 0.712; quantity share 0.8566) and `_scaled` 6-dp rounding reconciles exactly.

**C-6 SC-13.** The window closes after the single V3 request whatever the outcome; typed stop reasons; rows never filtered or rescaled to reconcile; no snapshot and no inferred names on any non-COMPLETE outcome.

**C-7 Manifest Case C.** `data/raw/**`, `data/cases/**` and the config hash are governed, so any executed V3 changes governed artifacts → exactly one third and last run after all corrections, receipted in ADR-021 before invocation ("S14a manifest run count is **3** (owner-authorized third and last run under OD-16/AM-3 Case C); no fourth run is authorized."), oracle immediately after, pre-existing `ab6211f` rows unchanged. No V3 → no third run.

**C-8 Records.** Core 05 §3.1/§11 V3 sentences; Core 04 §12 vocabulary; Core 09; ADR-021 "Correction round AM-3 (OD-16)"; KL-97/KL-102 rewritten; new KL-103 (description toggle established or not; official table unobserved); KL-75/80 narrowed; runbook row. **C-9 Review.** reviewer-grok gates AM-3 before the window and reviews AM-2 + AM-3 together (r8–r12: Decimal recomputation, endpoint/parameter check, V1 bytes unchanged, marker/verbatim-name checks, Case C receipt, credential-name scan).

Tests T-26…T-44, oracles O-11…O-18 and verification changes [11]–[14], [24], [26]–[28] are in the JSON.

Muhasib: verified from the stored V1 payload — the eight rows' exact tokens, the 3-decimal scale, the exact Decimal reconciliation (value and net weight), the ten null description fields, single-valued secondary dimensions, H6, the contract endpoint/parameter; verified elsewhere — the S11 `includeDesc=true` history, IAC-5, current code paths, manifest roots, run count 2. Assumed and left to the V3 rows — that the v1 endpoint accepts `includeDesc=true` and populates the description fields (the owner's statement; no stored v1 response in this repository has it), and that the provider has not revised the 2024 figures since V1. Consequential additions beyond OD-16's list are disclosed: description uniqueness check, superseded-attempt marker, ZERO-vs-aggregate consistency, HTTP total 2 (TERMS capture per invocation). No implementation, no product edit, no network, no `.env`, no git state change.
