# S15a — Case selection, evidence and families (pharma/API, fertilizers): plan-1 (mirror)

Machine record: `.autonomous-workflow/plans/s15-deep-cases-b/cycle-1/plan-1-s15a.json`
(SHA-256 `819e08fd115373f300a3494f1b486fdf6ffa0779e55d0783a11efac253ae78b5`; the JSON is binding, this
Markdown is a mirror). Child 0 of the S15 decomposition (`decomposition-1.json`
`ea01de65ac299cb2914c01f8f76ec692ce6d691b6530ad868e13b007ac0ab611`).

Seat: `planner-fable`. Base: merged main `M15` after both S14 children (parallel preparation allowed
per OD-11 with the DD-14 file set; integration at T11). Branch:
`slice/s15a-case-selection-evidence-pharma-fertilizers`. Implementer: `implementer-sol` (fresh) first,
`implementer-fable` fallback; `reviewer-grok` sole approver. Docker not required. Bytecode isolation
for every invocation.

## Objective (abridged)

(1) Rule S14-CS-1.1 as code: uniform typed `SERIES_GAP_YEARS` exclusion before tiering; evidence-based
`identity_exclusions` rows with stored WCO addresses; rule-version-gated output (the S14 record stays
byte-identical under S14-CS-1); `CASE-SELECTION-S15-<hash12>.json` pinned; recorded-input resolution by
content hash; `CASE SELECTION RECONSTRUCTION PASS (2 records)`. (2) `config/product_families.v1.yaml`
1.2.0 — pharma_api {2933, 2934, 2935, 2936, 2937, 2939, 2941}, fertilizers {3102, 3103, 3104, 3105};
boundary sets named as excluded by scope; `config/history/product_families.v1-1.1.0.yaml` retained; the
history rule extended to case-selection inputs. (3) `config/acquisition_sources.v1.yaml` 1.5.0 —
`producer_spimaco` (C), `producer_sabic_agrinutrients` (C), `sfda_registers` (B; new publisher kind
`regulatory_authority`), `wco_hs_nomenclature-v2` (Chapters 29/30/31); windows W-A15a (WCO first) →
identity rows → S15 selection run → W-A15b (producers/register) → W-P15 (Comtrade V3 partner detail per
selected line; ≤ 2 HTTP per unit). (4) mentions-v3 + third ENTITIES artifact. (5) Four CaseBrief 1.1.0
briefs (SAU-H6-294110, -294120, -310430, -310510; a fifth for 310560 only under OD-4) from stored spans
only; temporary-build engine proof INVESTIGATE / route null (recorded, never forced). (6) Core 02/04/05/09,
ADR-023, KLs (PR-S15-3/PR-S15-5 wording; MONITOR finding; SERIES_GAP_YEARS lines; boundary set;
310420 KCl), runbook, control documents, SLICE_GRAPH §5 split record, exactly one `build_manifests.py`
run after integration, uncommitted hand-off with IAC-6 identity.

## Tasks

| Id | Goal | RED tests (exact names in the JSON) | Oracle strings |
|---|---|---|---|
| T0 | Preflight: branch/base, parallel-mode declaration, baseline gates, BF-13 confirmations | — | `BRANCH_OK`, `INTEGRITY PASS`, `SCREENING RECONSTRUCTION PASS (1 snapshots)`, `SMOKE PASS`, `VISUAL_MANIFEST_OK` |
| T1 | Rule S14-CS-1.1 as code (TDD on doubles); S14 pin re-pointed to recorded inputs | `tests/test_case_selection.py` (11 new incl. `test_gap_years_candidate_is_excluded_series_gap_years_before_tiering_regardless_of_flags`, `test_identity_row_requires_complete_wco_record_and_verbatim_address`, `test_reconstruct_selection_reproduces_bytes_and_refuses_changed_inputs`, `test_s14_selection_reproduces_from_recorded_inputs_with_families_1_2_0_live`) | doubles green; real pins GREEN at T2/T5 |
| T2 | Families 1.2.0 + history 1.1.0 + history-rule extension | `tests/test_screening_config.py` (5); `tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only` (extended) | `SCREENING RECONSTRUCTION PASS (1 snapshots)`; sha256(history 1.1.0) = `62fa9c29…`; S14 lists unchanged |
| T3 | Acquisition 1.5.0, three sources, regulator kind, lists | `tests/test_acquisition_config.py` (4); `tests/test_acquisition_document_lists.py` (3) | suites green (ADR-text test GREEN at T11) |
| T4 | W-A15a — WCO Chapters 29/30/31 (consultation, index hrefs verbatim, acquisition, build) | — | `DOCUMENT RECONSTRUCTION PASS (m+3 records)` |
| T5 | Identity rows from stored text; terms-v2 (91 rows); S15 selection run twice; pin; candidates list | `tests/test_case_selection.py::test_s15_selection_from_frozen_screening_snapshot_matches_recorded_list` | `CASE SELECTION PASS (4 selected; 2 profiles; 2 families)`; equal hashes; expected variant B pharma_api [294110, 294120], fertilizers [310430, 310510] |
| T6 | W-A15b — SPIMACO, SABIC Agri-Nutrients, SFDA register | — | `DOCUMENT RECONSTRUCTION PASS (…)`; budgets green; no personal field |
| T7 | W-P15 — Comtrade V3 partner detail | — | `RECONSTRUCTION PASS (n+1 snapshots, …)`; ≤ 2 HTTP per unit; credential name absent |
| T8 | mentions-v3 + third ENTITIES artifact | `tests/test_entity_resolution_artifact.py` (+1) | `ENTITY RECONSTRUCTION PASS (3 artifacts, …)` |
| T9 | Briefs + provisional engine proof | `tests/test_case_briefs_real.py` (4) | `CASE BUILD PASS (4|5 briefs …)`; INVESTIGATE / route None |
| T10 | Scripts, Makefile, runbook (selection pass) | `tests/test_integrity_contract.py` (+1) | `CASE SELECTION RECONSTRUCTION PASS (2 records)` |
| T11 | INTEGRATION onto `M15` (W1 prep WIP by owner lead; linear rebase; re-run select/build/engine proof) + Core 02/04/05/09, ADR-023, KLs, split record, control docs | `tests/test_integrity_contract.py::test_s15a_core_v2_contracts` | rebase linear; S15 hash equal on M15; engine proof INVESTIGATE / None |
| T12 | Regression, exactly one `build_manifests.py`, §11 mirror, portability, `make ci` | — | `INTEGRITY PASS`; all PASS lines; `BYTE_IDENTICAL_EXPECT_0_LINES_ABOVE` 0; `VISUAL_MANIFEST_OK 76`; `FROZEN_OUTCOMES_OK`; `PORTABILITY_PASS`; `make ci` exit 0 |
| T13 | IAC-6 identity (base W1', wip_parent M15), stop uncommitted | — | `CANDIDATE_IDENTITY`; `INDEX_EMPTY_PASS`; `PROTECTED_SET_BYTE_IDENTICAL_PASS`; `STATE_JSON_VALID_PASS` |

## Design decisions (ids in the JSON)

DD-1 version-gated rule 1.1 in the same module · DD-2 uniform SERIES_GAP_YEARS · DD-3 evidence-based
identity rows with addresses (PROVISIONAL 294190, 293339, 310590; 310510 kept) · DD-4 families 1.2.0 +
retention + history rule · DD-5 acquisition 1.5.0 (three sources; `regulatory_authority`) · DD-6 window
order and honesty · DD-7 W-P15 Comtrade V3 · DD-8 briefs from stored spans (capability U; adjacency
signals only with spans; authority note names the rule version and selection id) · DD-9 engine proof
recorded, never forced · DD-10 selection reconstruction pass · DD-11 entities v3 · DD-12 import boundary
· DD-13 records (ADR-023, KLs in the ruled wording) · DD-14 parallel-mode file discipline.

## Stop conditions

SC-1 golden change · SC-2a frozen root / pinned module / catalogue edit · SC-2b non-INVESTIGATE brief ·
SC-3 span-less fact · SC-4 synthetic marker · SC-5 wall/TLS/non-200 → typed UNAVAILABLE · SC-6 budget ·
SC-7 post-manifest edit · SC-8 portability · SC-9 selection hash differs on M15 or the S14 record cannot
be reproduced · SC-10 identity row without a verbatim stored address is not entered · SC-11 rebase
conflict · SC-12 reviewer infrastructure.

## Scenario designs handed to s15b (advisory; computed on provisional snapshots)

Penicillin API → ADVANCE route 1 (route 0 fails, 2/3/4/6 not applicable, 5/7 blocked); Streptomycin
API → REJECT EX-03; Potassium sulphate → ADVANCE route 2 (route 1 fails by constraint class); Retail-pack
fertilisers → REJECT EX-01; PK fertilisers → MONITOR only with observed partner rows and the OD-4 waiver.
Full designs (synthetic inputs, bilingual narrative drafts, computed values) in the JSON section
`scenario_designs_for_s15b`.

## Open decisions

OD-1…OD-11 as in `decomposition-1.json`; OD-4 (MONITOR waiver) and OD-6 (visual budget) require explicit
owner-lead rulings; the others default on silence.
