# S15a test evidence — implementer-sol slot 1

## 2026-09-13T03:58:00Z — STOPPED at T6 / SC-2a

Status: `BLOCKED_ON_OWNER_PLAN_AMENDMENT`, not
`PREP_HANDOFF_PENDING_M15`. T0–T5 completed; T6 stopped before any producer or
register acquisition transport. T7–T10 were not started. No git state change,
manifest generation, primary-checkout write, s14b-worktree write, secret read,
credential use, commit, stage, fetch or rebase occurred.

Approved identities:

- plan `819e08fd115373f300a3494f1b486fdf6ffa0779e55d0783a11efac253ae78b5`;
- decomposition
  `ea01de65ac299cb2914c01f8f76ec692ce6d691b6530ad868e13b007ac0ab611`;
- preparation base `1289e31e50c1d835760f6943e697d6d537ac0a18`.

### Baseline / T0

```text
BRANCH_OK
INTEGRITY PASS
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
SCENARIO VALIDATION PASS (2 scenarios)
2416 tests collected
VISUAL_MANIFEST_OK 56
```

PublicSnapshot 2.1.0 on the preparation base was recorded as expected; the
2.2.0 proof remains an M15 integration obligation.

### RED → GREEN evidence

- T1 RED: `17 failed, 7 passed`; GREEN-at-T1:
  `1 failed, 23 passed`, with only the deliberately T2-dependent live-family
  pin red.
- T2 RED: `7 failed, 12 passed`; GREEN: `42 passed`.
- T3 RED: `264 failed, 65 passed`; GREEN-at-T3:
  `2 failed, 327 passed`, with only WCO-v2 (T4) and ADR-023 (T11) red.
- T4 WCO-v2 list: `1 passed`.
- T5 multi-page address RED plus missing real selection RED: `2 failed`;
  address GREEN: `1 passed`; final selection/config suite:
  `43 passed`; `CASE SELECTION RECONSTRUCTION PASS (2 records)`.
- Stop-point focused suite: `1 failed, 371 passed`; the sole failure is
  `test_no_history_copy_required_for_1_4_0_is_documented`, whose ADR-023 text
  is explicitly deferred to T11.

### Window summaries

W-A15a WCO consultation:

- robots, terms and index HTTP 200 under verified TLS;
- two disclosed index parser attempts emitted no hrefs; one final captured
  index response was inspected offline;
- verbatim index rows identified 0629/0630/0631 for Chapters 29/30/31;
- no credential and no URL guessing.

W-A15a acquisition RunReport:

```text
run_id 20260913T033253Z
MAX_REQUESTS 4
actual transport fetches 4 (one TERMS + three PDFs)
top-level requests_made 9 = known cumulative-count artefact
units COMPLETE 3
units UNAVAILABLE 0
HTTP statuses 200 / 200 / 200
```

Built:

```text
Chapter 29 DOC-WCO-HS-NOMENCLATURE-fd99902db1af-d01a792902be
  raw 408932 bytes, raw sha256 d01a792902be71381aa2c8484ce7663a1bc9b7838ef692ee07db87c59e7d25bd
  record sha256 b60762f9c60b9ee26e176f6e8cf4ebee683549743ace207ecaf72ec604e2f168
  21 pages / 1115 lines
Chapter 30 DOC-WCO-HS-NOMENCLATURE-4e3dbeff29ba-7ad8d2b476a9
  raw 161048 bytes, raw sha256 7ad8d2b476a97e2326fee5fbf6af0947d5213cc9a7f5e337667a7cbaa07af11d
  record sha256 9d0cba7d3127b6dbc4aa715e667e7720ff60cbf5e2766926208e58b3a710dede
  4 pages / 225 lines
Chapter 31 DOC-WCO-HS-NOMENCLATURE-fe3ed4f5325a-88edcc1ee93d
  raw 136798 bytes, raw sha256 88edcc1ee93dec8e927500988c578fb155e6b66c89a2f7ab42dfb15c4f8865f2
  record sha256 8073a7e800d16b30b7ba169e6de6cc213b6005d15699fd36c7a82267bc2238e4
  3 pages / 173 lines
DOCUMENT RECONSTRUCTION PASS (23 records, 23 artifacts)
```

W-A15b consultations completed before acquisition:

- target robots/landing pages on `ir.spimaco.com.sa`, `safco.com.sa`,
  `www.sabic-agrinutrients.com`, and `www.sfda.gov.sa` returned HTTP 200 and
  permitted the target paths;
- linked SABIC legal pages and SFDA privacy/terms pages returned HTTP 200;
- separate `spimaco.com.sa/robots.txt` failed certificate-chain verification,
  so its linked privacy body was not requested and TLS was not bypassed.

W-A15b acquisition:

```text
producer_spimaco: no RunReport; 0 acquisition HTTP; local Unknown source_id
producer_sabic_agrinutrients: NOT RUN after stop
sfda_registers: NOT RUN after stop
```

OD-12 resume evidence:

```text
connector registry RED: 1 failed
  AssertionError: assert 'producer_spimaco' in registry.ids()
connector registry GREEN: 2 passed in 0.11s
producer_spimaco:
  run 20260913T035150Z; E-001 COMPLETE; HTTP 200; requests 1;
  322368 bytes; aggregate RunReport absent after local
  pypdf DependencyError; E-002 not requested and UNAVAILABLE; no retry
producer_sabic_agrinutrients:
  run 20260913T035235Z; COMPLETE; requests 2; HTTP 200;
  7313847 bytes; 47 pages / 3088 lines; rotated-text warning
sfda_registers:
  run 20260913T035254Z; COMPLETE; requests 2; HTTP 200;
  67381 bytes; 1 page / 2335 lines
raw-size budget: 1 passed in 0.06s
```

W-P15 acquisition and stop:

```text
run 20260913T035527Z; four COMPLETE units:
  294110, 294120, 310430, 310510
shared request budget: 5 actual HTTP (1 TERMS + 4 PARTNERS)
aggregate RunReport requests_made: 14 (known cumulative-sum reporting defect:
  2 + 3 + 4 + 5; pipeline.py unchanged because outside DD-14)
snapshot build: SnapshotWriteConflict on the pre-existing tracked
  PARTNERS-SAU-UN-COMTRADE-2026-09-13.json
snapshot SHA-256 remained:
  e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b
```

Final stop-state full suite:

```text
6 failed, 2455 passed, 1 warning in 52.98s
```

Expected/deferred RED set:

1. `test_no_history_copy_required_for_1_4_0_is_documented` — ADR-023 is
   deferred to T11.
2. `test_manifest_lists_gz_payload_paths` — the single T12 manifest run is
   intentionally not yet authorized.
3. `test_summary_contract_and_authority_versions` — outside-DD-14 screening
   API expectation still pins families 1.1.0.
4. `test_evidence_route_returns_eight_universe_passports_verbatim` — same.
5. `test_evidence_route_without_snapshot_is_explicit` — same.
6. `test_unavailable_and_partial_fixtures_match_api_output` — outside-DD-14
   fixture still pins families 1.1.0.

All connector registration/source-set oracles pass (`5 passed in 0.45s`).
Protected roots are unchanged; `git diff --check` passes; changed Python
files have no IDE lint errors; no credential-header name occurs under
`data/raw`. DocumentRecords contain only the required
`synthetic_flag=false`; selection/case evidence has no synthetic marker.

Stop: `BLOCKED_ON_PARTNER_SNAPSHOT_WRITE_ONCE_IDENTITY`. T8–T10 were not
started. Brief tri-states and provisional engine results therefore do not
exist and are not claimed.

## OD-13 resume through PREP_HANDOFF_PENDING_M15

IAC-OD12-REGISTRATION matches exactly: three empty connector subclasses,
three registry entries, 24 sorted ids, existing WCO connector only, and the
exact tuple/DD-22/stored-source oracles.

OD-13 RED reproduced `SnapshotWriteConflict`; generic scoped identity,
no-collision preservation and scoped pinned reconstruction are GREEN.
Production result:

```text
PARTNERS-SAU-UN-COMTRADE-2026-09-13-b77e879286ae
coexists_with PARTNERS-SAU-UN-COMTRADE-2026-09-13
existing SHA-256 e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b
existing diff: zero
RECONSTRUCTION PASS (5 snapshots, 44 artifacts)
```

T8:

```text
mentions-v3: 2 verbatim PUBLISHER_NAME spans
artifact: ENTITIES-2026-09-13-219b097bddda
links: 2 EXACT_DOCUMENT_EVIDENCE
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
```

T9 brief states:

```text
294110 PARTNER_DETAIL_OBSERVED 10 non-World rows; capability U; hard gates U
294120 PARTNER_DETAIL_OBSERVED  4 non-World rows; capability U; hard gates U
310430 PARTNER_DETAIL_OBSERVED 11 non-World rows; capability U; hard gates U
310510 PARTNER_DETAIL_OBSERVED 11 non-World rows; capability U; hard gates U
partner snapshot: PARTNERS-SAU-UN-COMTRADE-2026-09-13-b77e879286ae
engine each: INVESTIGATE / route null / ROUTE_CHANGING_EVIDENCE_UNRESOLVED
fired each: R0, R1-D, R2, R3, R4-D, R10, R12
```

T10:

```text
CASE RECONSTRUCTION PASS (0 snapshots, 9 briefs)
CASE SELECTION RECONSTRUCTION PASS (2 records)
```

Final preparation pytest:

```text
6 failed, 2459 passed, 1 warning in 57.55s
```

Expected/deferred RED set remains:

1. ADR-023/no-acquisition-history-copy contract — T11.
2. Manifest raw payload coverage — the one authorized manifest run is T12.
3–6. Four screening API/fixture authority expectations still pin product
families 1.1.0 and are outside the parallel-preparation file set.

`git diff --check` passes. Protected roots and the unscoped S14 partner
snapshot have zero diff. Changed Python files have no IDE lint errors. No
credential-header name occurs in raw evidence; no true synthetic marker,
scenario id or demo-generator marker occurs in case evidence.

Status: `PREP_HANDOFF_PENDING_M15`.

## OD-14 corrected handoff evidence

The prior 64-unit scoped file was deleted before commit. Correct identity:

```text
PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196
scope_units:
  294110/imports/2024
  294120/imports/2024
  310430/imports/2024
  310510/imports/2024
coverage: COMPLETE; 4 requested; 4 complete; 0 excluded
coexists_with: PARTNERS-SAU-UN-COMTRADE-2026-09-13
```

The unit sets are disjoint. The scoped file has no `721061`,
`ENDPOINT_UNVERIFIED`, `supersedes`, or transformation exclusions. The
unscoped sibling remains SHA-256
`e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b`
with zero Git diff.

IAC-OD13 tests now prove:

- no collision emits the unscoped id;
- a disjoint collision emits scope12 over canonical sorted recorded keys;
- both the scoped file and unscoped sibling reconstruct pinned;
- rebuilding the sibling returns the unscoped path;
- wrong scope12, overlapping units, missing sibling and any `supersedes`
  fail closed;
- the production scoped snapshot has exactly the four candidate keys, no
  S14 rows/exclusions, and both production siblings reconstruct pinned.

All four briefs cite the corrected scoped id and remain
`PARTNER_DETAIL_OBSERVED` with 10/4/11/11 non-World rows. Engine proof is
unchanged: each is `INVESTIGATE`, route null,
`ROUTE_CHANGING_EVIDENCE_UNRESOLVED`, with
`R0,R1-D,R2,R3,R4-D,R10,R12`.

Corrected reconstruction:

```text
CASE RECONSTRUCTION PASS (0 snapshots, 9 briefs)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
CASE SELECTION RECONSTRUCTION PASS (2 records)
```

Corrected final pytest:

```text
6 failed, 2460 passed, 1 warning in 57.57s
```

The same six failures are expected/deferred: ADR-023 (T11), manifest rows
(T12), and four post-M15 screening authority expectation/fixture updates.
No network or `.env` access occurred during correction.

## T11 SC-9 stop on M15

Integration receipt verified:

```text
W1' 7d4853e8d979d86a5fa932fbd4468bceacfb63b4
M15 6dc966a9f210b47a94b96aaeffadcbcc6642415f
PublicSnapshot 2.2.0 present
focused frozen/case gate: 70 passed in 13.78s
```

Required selection byte-identity failed:

```text
recorded id  CASE-SELECTION-S15-b96de36ff0ce
recorded sha 65d1fe62f7dba44a7dd52f5bc40d4566576d696cc679b5c0a97e3f31efcd3fbe
M15 id       CASE-SELECTION-S15-55869cad5a8c
M15 sha      931145fd7d16bb7c333da01074e4bbbab1526e4f61700ca08150f627692eb602
```

The four selected HS6 codes are unchanged. The M15 rerun includes the
post-selection T6 SABIC Agri-Nutrients DocumentRecord in the hashed document
inventory (4 → 5 files) and marks non-selected 310210 disclosure-covered.
That exact evidence drift changes the selection id. SC-9 requires a stop;
T11 authority/control edits and all of T12/T13 remain unstarted.

## T11 integrated proof under OD-16

```text
CASE SELECTION RECONSTRUCTION PASS (2 records)
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

The recorded selection remains `CASE-SELECTION-S15-b96de36ff0ce`; diagnostic
`55869cad5a8c` remains unpromoted. PublicSnapshot 2.2.0 builds:

```text
294110 OBSERVED 10 INVESTIGATE/null
294120 OBSERVED  4 INVESTIGATE/null
310430 OBSERVED 11 INVESTIGATE/null
310510 OBSERVED 11 INVESTIGATE/null
reason: ROUTE_CHANGING_EVIDENCE_UNRESOLVED
fired: R0,R1-D,R2,R3,R4-D,R10,R12
capability dimensions: all U
profile hard gates: all UNAVAILABLE
```

Authority contract TDD:

```text
RED  tests/test_integrity_contract.py::test_s15a_core_v2_contracts
GREEN 1 passed in 0.07s
```

Integration delta for independent review: W1 `697322e` → W1'
`7d4853e8d979d86a5fa932fbd4468bceacfb63b4` on M15
`6dc966a9f210b47a94b96aaeffadcbcc6642415f`; sole owner-resolved conflict is
`CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)`. OD-16's second ruled item
is the recorded-input versus current-state diagnostic distinction above.

## T12 manifest generation

Exactly one invocation was receipted before execution at
`2026-09-13T07:43:54Z`, then exited 0:

```text
snapshot rows 638 -> 698; 60 added; 0 changed prior; 0 removed
authority rows 19 -> 19; exactly 6 approved rows changed
INTEGRITY PASS
manifest/authority focused tests: 29 passed
```

Post-generation hashes:

```text
snapshot  9842fa8a75698fb18c662b36beaf10fb3128dad7b1a31649e858a82b21c6abc7
authority 5160a840aba54e383122dbd552cc5e4406606cbfad148d9ba1efe5bd6ba0ce47
```

The §11 table mirrors the machine authority file. The one-run authorization
is exhausted.

## T12/T13 final gates

```text
pytest -q: 2600 passed, 1 warning
INTEGRITY PASS
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
CASE SELECTION RECONSTRUCTION PASS (2 records)
SCENARIO VALIDATION PASS (7 scenarios)
SMOKE PASS
VISUAL_MANIFEST_OK 76
FROZEN_OUTCOMES_OK
PORTABILITY_PASS
BYTE_IDENTICAL_EXPECT_0_LINES_ABOVE 0
RUNTIME_IMPORT_BOUNDARY_OK
```

Local and exact-scratch CI:

```text
local make ci: exit 0; 2600 Python + 339 functional + 4 visual
scratch CI=1 make ci: exit 0; 2600 Python + 339 functional + 4 visual
scratch committed head: dde43a99638a9fc13c075752ca4335847f12920e
scratch exact-byte comparison: 20 files PASS
```

The scratch evidence retains two environment stops before the successful run:
offline CPython 3.14 Pillow wheel absent, then `/tmp` inode exhaustion from an
unrelated workload causing Chromium insufficient-resources failures. The final
run used the unchanged committed scratch candidate, locked Python 3.12, and
home-filesystem temp/cache paths.

Canonical hand-off identity:

```text
base 7d4853e8d979d86a5fa932fbd4468bceacfb63b4
wip_parent 6dc966a9f210b47a94b96aaeffadcbcc6642415f
wip_commits [7d4853e8d979d86a5fa932fbd4468bceacfb63b4]
CANDIDATE_FILE_COUNT 20
CANDIDATE_IDENTITY 9e2853cfc7a6ae4208c24ab12daf90dfd24a8ccabbb0e5f3ebf87c9df3dbca31
INDEX_EMPTY_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
STATE_JSON_VALID_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
```

Independent review remains pending; no approval is claimed.

## Muhasib hand-off audit

- Scope: T11–T13 only; no network, `.env`, source re-acquisition, frozen-root
  change, active-worktree Git mutation or second manifest run.
- Authority: plan `819e08fd…`, OD-12–OD-16 and IACs applied. OD-16's
  recorded-input oracle and sensitivity distinction are explicit.
- Evidence: all completion statements above cite observed command output.
  The two scratch environment failures are retained rather than hidden.
- Precision: `U` is not identified within cited evidence, not absent;
  `NO_PUBLIC_TENDER_FOUND` is search-scoped; missing is not zero; Class-D
  designs do not enter public facts.
- Security: credential-name and precise absolute-filesystem-path scans are
  zero; no secret value was accessed or stored.
- Recovery: W1' remains the active HEAD; the 20-file delta is unstaged and
  uncommitted; the single generated manifest state is reconstructible and
  integrity-valid.
- Review boundary: builder self-check only. Independent reviewer assessment of
  the OD-15 conflict resolution, OD-16 ruling and full candidate remains
  mandatory. No approval, PR, CI-hosted status, merge or S15 completion is
  claimed.

No raw file exists under any of those three source ids. W-P15 was not opened;
the Comtrade credential was not loaded.

### S15 selection

```text
selection_id CASE-SELECTION-S15-b96de36ff0ce
sha256 65d1fe62f7dba44a7dd52f5bc40d4566576d696cc679b5c0a97e3f31efcd3fbe
two runs byte-identical
pharma_api selected 294110, 294120
pharma_api runner-up 294130
pharma_api identity exclusions 293339, 294190
pharma_api SERIES_GAP_YEARS 293723 (2022), 293919 (2023)
pharma_api viability exclusion 293711
fertilizers selected 310430, 310510
fertilizers runner-up 310221
fertilizers identity exclusion 310590
fertilizers SERIES_GAP_YEARS 310229 (2021), 310530 (2021), 310551 (2024), 310560 (2023)
fertilizers viability exclusion 310420
owner_designated_cases []
```

Terms-v2 has 91 stored-WCO-addressed rows, SHA-256
`eebe4ffab2d541b4356209407cc53b5710b16d65c2a14179fb06495762f22756`.
Identity-exclusions-v2 has only ruled variant-B rows
`293339/294190/310590`, SHA-256
`464f25e3c88efd3bde577412792eebfa9a8b9244df3e262daf3094ad34b5f301`.
Retained product-families 1.1.0 bytes remain
`62fa9c2944474ffbc5952801ba676a2adf750870a88969c59e22337b4564446b`.

### Full pytest at stop

Actual result: `12 failed, 2438 passed, 1 warning in 51.35s`.

Exact failures:

1. `test_no_history_copy_required_for_1_4_0_is_documented` — T11 ADR-023
   deferred.
2. `test_manifest_lists_gz_payload_paths` — T12 manifest additions not run.
3. `test_repository_raw_store_has_no_stored_evidence_problems` — source
   registry/raw outcome incomplete at the T6 stop.
4. `test_detector_meta_credential_absent_credential_env_var_changed` — same
   incomplete new-source raw set.
5. `test_detector_sentinel_configured_source_is_uncredentialed` — same.
6. `test_every_source_has_raw_record[producer_sabic_agrinutrients]` — T6 not
   run.
7. `test_every_source_has_raw_record[producer_spimaco]` — local registry stop.
8. `test_every_source_has_raw_record[sfda_registers]` — T6 not run.
9. `test_summary_contract_and_authority_versions` — the approved plan changes
   live families to 1.2.0 but omits this outside-DD-14 test update.
10. `test_evidence_route_returns_eight_universe_passports_verbatim` — same
    omitted test expectation.
11. `test_evidence_route_without_snapshot_is_explicit` — same.
12. `test_unavailable_and_partial_fixtures_match_api_output` — same omitted
    fixture expectation.

Pre-manifest integrity fails only on the authorized live config hashes:
acquisition sources 1.5.0 and product families 1.2.0. No manifest run was
attempted.

### File set at stop

Tracked modifications: the two approved configs; selection/CLI; screening
config; acquisition source config/document-list policy; six test files.

New governed preparation data: retained families 1.1.0; terms-v2;
identity-exclusions-v2; S15 selection and Comtrade candidate files; WCO v2
list, three WCO records and their four-request raw run; three pre-acquisition
producer/register lists. Slice implementation/test records are untracked as
expected. Frozen public/synthetic/golden/browser roots and protected runtime
files have zero tracked or untracked changes.

IDE diagnostics: no linter errors on changed Python files. Credential-name and
synthetic-marker scans found no match in new case/document evidence paths.

### Binding blocker and muhasib

`default_registry()` is an explicit source-id map and the document connector
module defines explicit per-source subclasses. Persisting the required S15
sources therefore needs:

- `src/ior_mvp/acquisition/connectors/documents.py`;
- `src/ior_mvp/acquisition/connectors/base.py`;
- tests proving all governed document sources are registered.

Those two production files are outside DD-14/files.modify and are required
byte-identical by O-2/SC-2a. I did not edit them or inject a command-local
workaround. Owner action required: amend the approved plan/file set, then
resume T6 from the same write-once evidence tree.

Muhasib result: `BLOCKED`, not complete. Verified scope and hashes, reviewed
the tracked diff, ran focused and full tests, checked lints/protected roots,
recorded all network outcomes and did not hide the plan omission. Assumptions:
the owner intends these three ids to be executable through the ordinary
registry (derived from the approved acquisition objective); no assumption is
made about the unrun producer/register responses or later briefs/engine
states. Independent review, M15 integration, manifest generation and delivery
remain outstanding.
