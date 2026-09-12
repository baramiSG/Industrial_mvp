# S13a test evidence — implementer-sol slot 1

All commands run from `/home/barami/projects/industrial-opportunity-resolution-mvp` with:

```text
export PATH=$PWD/.venv/bin:$PATH PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s13a-bytecode UV_OFFLINE=1
```

No network was used during T0.

## T0 baseline

### [0] Branch and base

Command:

```text
test "$(git branch --show-current)" = slice/s13a-universe-acquisition-and-screening-engine && git merge-base --is-ancestor 81eac4f2aaaa2710b658b657e627294528785395 HEAD && echo BRANCH_OK
```

Output / exit:

```text
BRANCH_OK
exit 0
```

### [1] Integrity

Command:

```text
PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
```

Output / exit:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
exit 0
```

### [2] Full pytest

Command:

```text
PYTHONPATH=src .venv/bin/pytest -q
```

Output / exit:

```text
2027 passed, 1 warning in 23.45s
exit 0
```

Warning:

```text
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
```

### [3] Smoke

Command:

```text
PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
```

Output / exit:

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
exit 0
```

### [4] Acquisition/document/entity reconstruction

Command:

```text
PYTHONPATH=src .venv/bin/python scripts/reconstruct_snapshot.py --all
```

PASS output / exit:

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
exit 0
```

Known PDF parser warnings were emitted before the PASS lines and match ADR-017/KL-63/KL-66.

## T1 acquisition config and credential-header TDD

Focused command:

```text
PYTHONPATH=src .venv/bin/pytest -q tests/test_acquisition_config.py tests/test_acquisition_connectors.py -k "metadata_version_pinned_to_1_3_0 or credential_header_optional_only_with_credential_env_var or credential_header_rejects_invalid_name or institutional_and_document_sources_reject_credential_header or denylist_includes_ocp_apim_subscription_key or custom_credential_header_sent_and_never_stored or bearer_default_unchanged_for_wits_trade or 401_records_http_error_with_sanitized_observed_response"
```

RED / exit:

```text
10 failed, 14 passed, 271 deselected in 0.41s
exit 1
```

Expected failures proved: metadata still 1.2.0; custom header missing/unvalidated; custom request used Bearer; denylist entry absent.

GREEN / exit:

```text
24 passed, 271 deselected in 0.35s
exit 0
```

Regression command/output:

```text
PYTHONPATH=src .venv/bin/pytest -q tests/test_acquisition_config.py tests/test_acquisition_connectors.py
295 passed in 10.40s
exit 0
```

### [6] Threshold-literal scan

Command:

```text
.venv/bin/python scripts/check_threshold_literals.py
```

Output / exit:

```text
THRESHOLD LITERAL SCAN PASS (59 Python files; 23 configured numeric values)
exit 0
```

### [7] Prohibited-file scan

Command:

```text
.venv/bin/python scripts/check_prohibited_files.py
```

Output / exit:

```text
PROHIBITED FILE SCAN PASS (756 tracked files)
exit 0
```

## T2 connector replacement — RED and stop

Command:

```text
PYTHONPATH=src .venv/bin/pytest -q tests/test_acquisition_connectors.py tests/test_acquisition_kind_registry.py -k "un_comtrade_universe_single_response_complete_when_count_matches or un_comtrade_count_mismatch_is_incomplete_indeterminate or un_comtrade_error_envelope_is_incomplete or un_comtrade_html_landing_page_never_becomes_universe or un_comtrade_reporter_mismatch_fails_validation or un_comtrade_mixed_classification_in_unit_fails_validation or un_comtrade_duplicate_hs6_in_unit_fails_validation or un_comtrade_rows_carry_classification_code_as_hs_revision or un_comtrade_partner_rows_keep_partner_desc_and_world_row or universe_snapshot_records_hs_revisions_and_config_version_1_3_0 or partners_kind_config_version_unchanged_and_wits_snapshot_reconstructs"
```

RED / exit:

```text
7 failed, 4 passed, 30 deselected in 0.14s
exit 1
```

No T2 GREEN was run or claimed. The approved top-level `hs_revisions` snapshot behavior cannot be connected to normalized rows without editing the byte-identical `src/ior_mvp/acquisition/snapshots.py` generic builder (or obtaining an equivalent approved contract change).

Stop-time diagnostic outputs:

```text
SNAPSHOTS_PY_BYTE_IDENTICAL
MANIFESTS_UNCHANGED_NO_GENERATOR_RUN
plan sha256 9d1f8134da33715e8fcb85d1290be69d4bdab02e1335c1ef26f663cb3e654f5f
```

Owner-approved AM-1 re-expressed the never-green snapshot-key assertions as
row invariants. Amendment SHA-256:

```text
d562ddca000f2dd05c606c4ea2db4dc0b33da1adeb3630aef05c3273eade0130
```

Amended focused command:

```text
PYTHONPATH=src .venv/bin/pytest -q tests/test_acquisition_connectors.py tests/test_acquisition_kind_registry.py -k "un_comtrade_universe_single_response_complete_when_count_matches or un_comtrade_count_mismatch_is_incomplete_indeterminate or un_comtrade_error_envelope_is_incomplete or un_comtrade_html_landing_page_never_becomes_universe or un_comtrade_reporter_mismatch_fails_validation or un_comtrade_mixed_classification_in_unit_fails_validation or un_comtrade_duplicate_hs6_in_unit_fails_validation or universe_rows_carry_classification_code_verbatim or un_comtrade_partner_rows_keep_partner_desc_and_world_row or universe_snapshot_records_config_version_1_3_0 or universe_validator_requires_one_hs_revision_per_unit or universe_validator_requires_hs_revision_on_every_row or partners_kind_config_version_unchanged_and_wits_snapshot_reconstructs"
```

GREEN / exit:

```text
15 passed, 30 deselected in 0.12s
exit 0
```

IAC-13 identity proof:

```text
SNAPSHOTS_PY_BYTE_IDENTICAL
exit 0
```

Verification [4] remained green:

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
exit 0
```

## RED / GREEN evidence

| Step | RED | GREEN |
|---|---|---|
| T0 | Not applicable — baseline | [0]–[4] PASS; 2027 tests |
| T1 | 10 failed for intended missing config/header behavior | 24 focused passed; 295 acquisition regression passed |
| T2 | 7 failed for intended connector/kind behavior; 4 passed | AM-1 focused GREEN: 15 passed; reconstruction PASS |

## Manifest-run receipt

Run exactly once at T11; exit 0; immediate manifest oracle passed. No second
run is authorized or attempted.

## T3 W0/W1 and regression

W0 output and the complete W1 RunReport are recorded verbatim in
`implementation_log.md`. W1 run `20260912T134009Z` returned eight
`LICENSE_UNRECORDED` units, zero requests, zero artifacts, and exit code 3.
Snapshot construction refused with `FORMAT_NOT_PARSEABLE`.

```text
T3 pytest first run: 1 failed, 2065 passed
T3 pytest corrected approved universe pin: 2066 passed, 1 warning in 21.73s
THRESHOLD LITERAL SCAN PASS (59 Python files; 23 configured numeric values)
PROHIBITED FILE SCAN PASS (756 tracked files)
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
```

Pre-T11 integrity reported only the expected modified acquisition-config hash.

## T4–T6 screening engine

```text
T4 RED: 11 failed in 0.04s
T4 GREEN: 11 passed in 0.03s
T5 RED: 31 failed in 0.10s
T5 first GREEN: 1 failed, 30 passed in 0.06s
T5 GREEN: 31 passed in 0.05s
T6 RED: 22 failed in 0.09s
T6 GREEN: 22 passed in 0.08s
```

## T7 snapshot

```text
SCREENING VALIDATION PASS
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

Artifact measurements:

```text
screening snapshot: 5275 bytes
plant-family link list: 118 bytes
universe snapshot: absent
partner snapshot from W2: absent
```

## T8 runtime/API

```text
T8 RED: 8 failed, 2 passed, 1 warning in 0.17s
T8 GREEN: 10 passed, 1 warning in 0.28s
```

## T9–T11 generated proof

```text
T9 RED: 1 failed
T9 GREEN: 2 passed in 0.02s
T10 Core contract GREEN: 2 passed in 0.02s
pre-generation full pytest: 2142 passed, 1 warning in 21.99s
```

The single T11 command ran exactly once. Immediate [14]:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
20 passed in 0.04s
```

Generated diff:

```text
data/manifests/snapshot_manifest.json | 90 lines added
docs/authority/authority_hashes.json  | 42 lines changed
2 files changed, 116 insertions(+), 16 deletions(-)
```

Post-generation:

```text
2142 passed, 1 warning in 22.43s
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
INTEGRITY PASS
manifest oracle: 20 passed
make ci exit 0
make ci pytest: 2142 passed, 1 warning in 22.10s
browser functional: 118 passed, 4 deselected
browser visual: 4 passed, 118 deselected
```

## T12 status

STOPPED before candidate identity and completion. Strict self-review found the
post-generation DD-11 product-family `sector_profile` authority-config defect
and the additional DD-16/DD-17/state-record mismatches recorded in
`implementation_log.md`. The one authorized manifest run is exhausted, so no
authority-config correction or second generation was attempted.

## OD-10 corrective round evidence

### W0-bis and config

The five official Help Center observations, UTC times, HTTP/content types and
verbatim quotations are recorded in `implementation_log.md`. No credential
was loaded. Config validation:

```text
PYTHONPATH=src pytest -q tests/test_acquisition_config.py
285 passed in 4.50s
```

### Four defects RED → GREEN

```text
PYTHONPATH=src pytest -q tests/test_screening_config.py tests/test_screening_snapshot.py tests/test_screening_candidates.py
RED: 3 failed, 15 passed
GREEN: 18 passed in 0.08s
PASS milestones.v0.3.0.split.s13; sibling s13_split absent
IDE diagnostics: no linter errors
```

### W1-bis

Run `20260912T141128Z` used the pre-recorded nine-request cap. Application
exit code was 3 (Make exit 2). The RunReport and per-unit table are recorded
in `implementation_log.md`. All eight units stored one normalized page;
provider count equalled stored rows; classification was H5 in 2021 and H6 in
2022–2024; all eight coverage records remained:

```text
status=INCOMPLETE
completeness_basis=UNAVAILABLE
stop_reason=COVERAGE_INDETERMINATE
```

No universe snapshot, candidate list, W2 batch/request or partner snapshot was
created.

### Corrected fallback

```text
make build-screening
data/screening/snapshots/SCREENING-SAU-2026-09-12-4f722c45a691.json

make validate-screening
SCREENING VALIDATION PASS

make screening-reconstruct
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

Snapshot SHA-256
`f3fe7462ef5fef35fbf0157cf3665cdc3b3d6cc9986ed4144567f9e2b9c5e380`;
5,279 bytes; `UNAVAILABLE / COVERAGE_INDETERMINATE`; all disposition and five
queue counts zero; unqueued zero. OD-7 not triggered.

### Pre-generation correction and final manifest

```text
new connector RED: 1 failed
new connector GREEN: 1 passed in 0.05s
stored-attempt + KL focused gate: 10 passed in 0.06s
pre-generation full pytest: 1 failed, 2161 passed, 1 warning
sole failure: test_manifest_lists_gz_payload_paths (expected stale manifest)
SMOKE PASS
SCENARIO VALIDATION PASS (2 scenarios)
THRESHOLD LITERAL SCAN PASS (71 Python files; 23 configured numeric values)
PROHIBITED FILE SCAN PASS (756 tracked files)
VISUAL_MANIFEST_OK
24 golden/frozen/offline tests passed
3 performance/leakage tests passed, 1 warning
RUNTIME_IMPORT_BOUNDARY_OK
SIZE_BUDGETS_OK
FROZEN_OUTCOMES_OK
BYTE_IDENTICAL_ACTUAL_TOP_LEVEL_PASS
```

Manifest receipts:

```text
first planned T11: 2026-09-12; exit 0; immediate INTEGRITY PASS + 20 passed
second/final OD-10: 2026-09-12T14:21:10Z; exit 0
immediate oracle:
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
20 passed in 0.04s
```

Manifest run count is exactly two; authorization is exhausted.

### Final post-generation gates

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
2162 passed, 1 warning in 23.29s
SMOKE PASS
SCENARIO VALIDATION PASS (2 scenarios)
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SCREENING VALIDATION PASS
VISUAL_MANIFEST_OK
IAC13_SNAPSHOTS_BYTE_IDENTICAL_PASS
BROWSER_TESTS_BYTE_IDENTICAL_PASS
BYTE_IDENTICAL_ACTUAL_TOP_LEVEL_PASS
CREDENTIAL_NAME_ONLY_EXPECT_NO_VALUE_LINES
```

`make ci` exit 0 tail:

```text
2162 passed, 1 warning in 22.91s
SMOKE PASS
BROWSER PREFLIGHT PASS
118 passed, 4 deselected in 131.01s
4 passed, 118 deselected in 25.75s
```

W1-bis compressed raw payload total: 1,094,392 bytes (nine stored payloads,
including terms). Universe/UN Comtrade partner snapshots and candidate lists:
absent. Screening snapshot: 5,279 bytes.

## Final corrective-round candidate identity

Base/HEAD `81eac4f2aaaa2710b658b657e627294528785395`. Paths under both
`.workflow/slices/S13-public-universe-screening/` and
`.workflow/slices/S13a-universe-acquisition-and-screening-engine/` excluded.
Identity input is the sorted union of `git diff --name-only HEAD` and
`git ls-files --others --exclude-standard`, represented as canonical JSON
records containing path, SHA-256 and byte count with
`sort_keys=True,separators=(',', ':'),ensure_ascii=False`, plus LF.

**Candidate identity:
`fb861700986675a30a940065ad864e3c10b731993da1e42552dc6b9caa5aeece`;
108 files; index empty.**

Plan/amendment/decomposition SHA-256 checks:

```text
9d1f8134da33715e8fcb85d1290be69d4bdab02e1335c1ef26f663cb3e654f5f
d562ddca000f2dd05c606c4ea2db4dc0b33da1adeb3630aef05c3273eade0130
93ba2443455aa368ed83814f49795a0a04f59a66d3c5d7006125afe5b27793a8
```

Changed-file set versus the approved plan: all 108 identity paths fall within
the declared modified, created, generated or W1/W1-bis raw-evidence paths.
The live-evidence correction modifies already planned
`acquisition/connectors/base.py` and `test_acquisition_connectors.py`; the
eight attempt metadata files remain within planned `data/raw/un_comtrade/**`.
No path from `must_not_change` is present. The plan verification [8] quoted
Git pathspec recursively matches acquisition submodules; the actual
shell-expanded top-level-file oracle passed and IAC-11 classifies [8] as a
hint rather than fail-closed.

Final mechanical audit:

```text
DIFF_CHECK_PASS
INDEX_EMPTY_PASS
AUTONOMOUS_WORKFLOW_UNCHANGED_PASS
W1BIS_ATTEMPT_RESPONSE_PROVENANCE_PASS 8
IDE diagnostics: no linter errors
IDENTITY_RECHECK fb861700986675a30a940065ad864e3c10b731993da1e42552dc6b9caa5aeece 108
```

## OD-11 corrective round — stopped at OD-7

```text
RED: 12 failed, 2 passed
GREEN: 14 passed in 0.09s
ACQUISITION REGRESSION: 328 passed in 10.68s
W1_TER_RUN_ID 20260912T143742Z
W1_TER_COMPLETE_UNITS 8
W1_TER_INCOMPLETE_UNITS 0
UNIVERSE_SIZE_BYTES 24195845
SCREENING VALIDATION PASS
SCREENING RECONSTRUCTION PASS (1 snapshots)
W2_RUN_ID 20260912T144127Z
W2_REQUESTS_MADE 0
W2_COMPLETE_UNITS 0
W2_INCOMPLETE_UNITS 59
W2_STOP_REASON ENDPOINT_UNVERIFIED
R2_FULL_SURVIVORS 1471
SCREENING_SIZE_BYTES 57164360
MAX_GOVERNED_FILE_BYTES 50331648
OD7_STOP SCREENING_OVERSIZE_BY_BYTES 6832712
```

W1-ter per-unit evidence:

| Year | Flow | Provider count | Stored rows | classificationCode | Status |
|---|---|---:|---:|---|---|
| 2021 | imports | 4,819 | 4,819 | H5 | COMPLETE |
| 2021 | exports | 3,651 | 3,651 | H5 | COMPLETE |
| 2022 | imports | 5,061 | 5,061 | H6 | COMPLETE |
| 2022 | exports | 3,704 | 3,704 | H6 | COMPLETE |
| 2023 | imports | 5,038 | 5,038 | H6 | COMPLETE |
| 2023 | exports | 3,818 | 3,818 | H6 | COMPLETE |
| 2024 | imports | 5,012 | 5,012 | H6 | COMPLETE |
| 2024 | exports | 3,852 | 3,852 | H6 | COMPLETE |

The third/final manifest run, full regression, `make ci`, reconstruction
suite and candidate identity were not run because OD-7 is a mandatory stop
condition. Manifest run count remains two.

## AM-2 / OD-12 final evidence

```text
AM2_SHA256 88abbab21d44f547f308917d97db1835a8bcb594cb0de49663a9405a7b90b085
AM2_RED 8 failed
AM2_GREEN 27 passed, 1 warning
SCREENING_REGRESSION 83 passed, 1 warning
W0_TER_STATUS 200
W0_TER_FINAL_URL https://comtradedeveloper.un.org/signin?returnUrl=%2Fapi-details#api=comtrade-v1
W0_TER_ALL_PARAMETERS NOT_OBSERVED
W2_RERUN NOT_AUTHORIZED
UNIVERSE_STATUS AVAILABLE
UNIVERSE_HS6 5443
UNIVERSE_SIZE_BYTES 24195845
SCREENING_FILES 98
SCREENING_LARGEST_FILE records/84.json 5125636
SCREENING_TOTAL_BYTES 52798074
SCREENING_DISPOSITIONS CANDIDATE=4996 SCREENED_OUT=0 NO_CANDIDATE=447
SCREENING_QUEUES 15 0 4727 0 119
SCREENING_UNQUEUED 135
PARTNER_COVERED 0
PARTNER_UNCOVERED 1471
MANIFEST_RUN_3 2026-09-12T15:01:37Z EXIT_0
INTEGRITY PASS
MANIFEST_CONTRACT 20 passed
FINAL_PYTEST 2190 passed, 1 warning in 24.82s
SMOKE PASS
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SCENARIO VALIDATION PASS (2 scenarios)
IAC13_SNAPSHOTS_BYTE_IDENTICAL_PASS
BROWSER_TESTS_BYTE_IDENTICAL_PASS
TOP_LEVEL_SRC_BYTE_IDENTICAL_PASS
VISUAL_MANIFEST_OK
SCREENING_SIZE_BUDGETS_OK SCREENING-SAU-2026-09-12-311f105c4ccf 5125636 52798074
MAKE_CI_EXIT 0
MAKE_CI_PYTEST 2190 passed, 1 warning in 23.87s
MAKE_CI_BROWSER_FUNCTIONAL 118 passed, 4 deselected in 128.74s
MAKE_CI_BROWSER_VISUAL 4 passed, 118 deselected in 25.32s
DIFF_CHECK_PASS
```

W0-ter facts:

| Item | Verbatim observation |
|---|---|
| Rendered body | `Products`; `Sign in`; `Welcome to UN Comtrade API portal!`; `Sign in to Comtrade Developer portal`; `Powered by Azure API Management.` |
| partnerCode / cmdCode / period / flowCode / reporterCode | NOT OBSERVED |
| partner2Code / motCode / customsCode | NOT OBSERVED |
| pagination / record limit | NOT OBSERVED |
| terms link / GET operation | NOT OBSERVED |

W2:

| Batch | Requests | Covered | Uncovered | Outcome |
|---|---:|---:|---:|---|
| AM-2 rerun | 0 | 0 | 1,471 | Not authorized because all-partners token was NOT OBSERVED |

Manifest receipts:

1. Planned T11, 2026-09-12: exit 0; immediate oracle PASS.
2. OD-10, `2026-09-12T14:21:10Z`: exit 0; immediate oracle PASS.
3. OD-12, `2026-09-12T15:01:37Z`: exit 0; immediate oracle PASS.

Manifest authorization is exhausted; no fourth run occurred.

## Final AM-2 candidate identity

Base/HEAD `81eac4f2aaaa2710b658b657e627294528785395`. IAC-6 excludes both
S13 slice-record folders and hashes canonical JSON records of each remaining
changed/untracked path, SHA-256 and byte count.

```text
CANDIDATE_IDENTITY faf2201c1f512e829dbd88a222d7013b672781b8967324bcb00421f402b3dc20
CANDIDATE_FILE_COUNT 378
INDEX_EMPTY_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
STATE_JSON_VALID_PASS
IDE diagnostics: no linter errors
```

All 378 paths are within the original plan's create/modify/generated sets or
the explicit AM-1/AM-2/OD-10/OD-11 corrections. AM-2 replaces the planned
single screening JSON with its authorized directory files. No must-not-change
path is present.

## Identity correction — 2026-09-12T15:11Z

The earlier `faf2201c…` figure is stale/invalid. Its calculation serialized
only the `files` list and omitted the IAC-6 top-level `base` field. The exact
governed payload is
`{"base": HEAD, "files": [{"path","sha256","bytes"}...]}` with canonical JSON
and trailing LF.

At `2026-09-12T15:07:05Z`, `src/ior_mvp/screening/repository.py` was written
when the implementer re-added `import json` immediately after briefly removing
it as an unused-import cleanup. This was a manual revert, not a formatter or
linter action; it restored the pre-cleanup tested content but updated mtime.
No product file was changed during this correction request.

Current-tree tests:

```text
AM-2 focused: 8 passed, 1 warning in 0.20s
All screening: 83 passed, 1 warning in 0.43s
```

Correct current-tree identity:

```text
IAC6_IDENTITY 612626ed400446e7b13986f5d7213af89b6de178d80b23426cc637a502e26343
IAC6_FILE_COUNT 378
```

## OD-13 RED/GREEN evidence — 2026-09-12T15:35:19Z

```text
RED authority contract:
1 failed in 0.06s
test_s13a_core_v2_screening_contracts
  missing official-v1 COMPLETE Core 05 §3.1 status cell

RED runtime selection / GREEN CLI:
1 failed, 1 passed, 1 warning in 0.16s
test_latest_snapshot_selected_by_as_of_date_then_snapshot_id
  selected SCREENING-Z-OLDER instead of SCREENING-B-NEWER

GREEN corrected contracts:
3 passed, 1 warning in 0.14s
test_s13a_core_v2_screening_contracts
test_latest_snapshot_selected_by_as_of_date_then_snapshot_id
test_screening_cli_main_exit_codes_and_no_socket
```

No data, snapshot or raw file changed in this correction.

Pre-generation and manifest receipt:

```text
PRE_GENERATION_PYTEST 2192 passed, 1 warning in 24.60s
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SCENARIO VALIDATION PASS (2 scenarios)
SCREENING VALIDATION PASS
VISUAL_MANIFEST_OK
SIZE_BUDGETS_OK
FROZEN_OUTCOMES_OK
MANIFEST_RUN_4 2026-09-12T15:36:59Z EXIT_0
MANIFEST_RUN_4_IMMEDIATE_ORACLE INTEGRITY PASS
MANIFEST_RUN_4_CONTRACT 20 passed in 0.21s
```

Post-generation gates:

```text
FINAL_PYTEST 2192 passed, 1 warning in 24.73s
INTEGRITY PASS
SMOKE PASS
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SCENARIO VALIDATION PASS (2 scenarios)
SCREENING VALIDATION PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS 43
IAC13_SNAPSHOTS_BYTE_IDENTICAL_PASS
VISUAL_MANIFEST_OK
MAKE_CI_EXIT 0
MAKE_CI_PYTEST 2192 passed, 1 warning in 24.04s
MAKE_CI_BROWSER_FUNCTIONAL 118 passed, 4 deselected in 129.85s
MAKE_CI_BROWSER_VISUAL 4 passed, 118 deselected in 25.57s
INDEX_EMPTY_PASS
```

Reconstruction PDF-parser warnings are unchanged diagnostics; the command
exited 0 and printed every required PASS line.

Changed-file delta versus reviewer candidate `612626ed…`:

```text
.workflow/slices/S13a-universe-acquisition-and-screening-engine/implementation_log.md
.workflow/slices/S13a-universe-acquisition-and-screening-engine/test_evidence.md
docs/ARCHITECTURE_DECISIONS.md
docs/KNOWN_LIMITATIONS.md
docs/authority/00_AUTHORITY_MANIFEST.md
docs/authority/authority_hashes.json
docs/core/01_PRODUCT_AND_REQUIREMENTS.md
docs/core/05_DATA_SOURCES_AND_INGESTION.md
src/ior_mvp/screening/repository.py
tests/test_integrity_contract.py
tests/test_screening_candidates.py
tests/test_screening_repository_and_api.py
```

The two generated authority files changed only because OD-13 authorized
Core 01/Core 05 hash updates. No data, raw, universe, screening, candidate or
snapshot file changed.

## Final OD-13 candidate identity

```text
IAC6_BASE 81eac4f2aaaa2710b658b657e627294528785395
IAC6_IDENTITY e73aeba9d5d997eaf8973eac324b0f0f679a25ebfc8700e263709facfea70fc6
IAC6_FILE_COUNT 378
INDEX_EMPTY_PASS
```

The canonical payload includes top-level `base`, sorted path/SHA-256/byte
records and a trailing LF. Both S13 slice-record folders are excluded.

Manifest receipts:

1. Planned T11, 2026-09-12: exit 0; immediate oracle PASS.
2. OD-10, `2026-09-12T14:21:10Z`: exit 0; immediate oracle PASS.
3. OD-12, `2026-09-12T15:01:37Z`: exit 0; immediate oracle PASS.
4. OD-13, `2026-09-12T15:36:59Z`: exit 0; immediate oracle PASS.

Manifest authorization is exhausted; no fifth run occurred.
