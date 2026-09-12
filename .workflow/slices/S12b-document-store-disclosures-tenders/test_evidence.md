# S12b test evidence — slot 3 (superseded identity) and slot 4 correction round

## Candidate identity (IAC-6) — current (slot 4, 2026-09-12 ~06:58Z)

Base: `cdfd4ba4b016619b7ab33a373d334f22c337166d`  
**Candidate SHA-256: `19d9eea310c1d9b51b1fbb7643809e8352aa520f730a9dc6f42fc79b74039e8c`**  
**File count: 196** — recomputed 2026-09-12 ~07:05 UTC after the owner-authorized records follow-up (runbook T7-v3 paragraph and roadmap §s12b status line; both already in the changed set, so the count is unchanged; prior slot-4 identity `1f8a1f612426ea0d86670e8831e04e6828a45c09e26798f3d1b03f350b9aabe5`, same 196 files; index empty). IAC-6 procedure: `git diff --name-only HEAD` ∪ `git ls-files --others --exclude-standard`, paths under `.workflow/slices/S12b-document-store-disclosures-tenders/` excluded, sorted, canonical JSON `{"base","files":[{"path","sha256","bytes"}]}` with `sort_keys=True, separators=(',', ':'), ensure_ascii=False` + `\n`, SHA-256 of the UTF-8 bytes (`/tmp/s12b_slot4/identity.py`; index empty). Versus the reviewed candidate `87084ed23328962a8cdaa021738280823af702fb7bc2a5959aaea41b197a6314` (194 files): +2 paths (`data/documents/saso_documents/lists/saso_documents-v4.json`, `tests/test_acquisition_document_records.py`), 0 removed, 20 files with changed content (listed in the slot-4 section of `implementation_log.md`).

Historical (slot 3, A07): the figure previously written here — `4cfe3ec71f3e9cc2d6d4dff466d83762b58ca3bc683f7c6c58c1c4544bc282e4` / **200** files — included the six slice-record files and was not the review identity; the review identity of that tree was `87084ed2…` / 194 files (supervisor recomputation).

## T12 summary

```
pytest -q → 1878 passed, 1 warning
make ci → 1878 passed + 118 functional + 4 visual (all exit 0)
```

## Manifest runs (exactly 3 authorized and executed: T11, OD-9, OD-10)

| Run | UTC | Exit | Notes |
|---|---|---:|---|
| 1 (slot 2 T11) | 2026-09-12T05:26:47Z | 0 | Pre–T7-v3; +88 snapshot rows |
| 2 (slot 3 OD-9) | 2026-09-12T05:43:02Z | 0 | Post–T7-v3; twelve records + raw payloads |
| 3 (slot 4 OD-10) | 2026-09-12T06:37:37Z | 0 | Post F01/F02 corrections: `saso_documents-v4` list row added, six SASO record rows re-hashed, Core 04/05 and acquisition-config authority rows changed; snapshot manifest `4fb8592d…` (214 rows), authority hashes `79015f4c…`; §11 mirrored; immediate [14] PASS |

## Storage totals

- `data/documents/**`: **2,117,914** bytes
- `data/raw/` document-source partitions (7 sources): **24,672,164** bytes

## Plan verification commands (index + output)

### [5]
```
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
PREGEN_RECON_OK
```

### [14] (immediate post–OD-9 manifest)
```
MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT
```

### [15]
```
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

### [17]
```
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
POSTGEN_RECON_OK
```

### [19]
```
PARTNER_SNAPSHOT_BYTE_IDENTICAL
```

### [20]
```
ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12
```

### [25] verbatim (vacuous pathspec; recorded per IAC-9)
```
rg: :(glob)src/ior_mvp/*.py: No such file or directory (os error 2)
RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
exit=0
```

### [25] corrected (IAC-9)
```
RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
```

## T7-v3 re-run table

| source | list_id | entries | RunReport `requests_made` (aggregate-count artefact) | stored transport fetches | MAX_REQUESTS | records | per-entry outcome |
|---|---|---:|---:|---:|---:|---:|---|
| saso_documents | saso_documents-v3 | 6 | 27 (= 2+3+4+5+6+7 per-unit cumulative `RequestBudget.used` echoes) | 7 (1 TERMS `text/html` + 6 `application/pdf`) | 7 | 6 | All HTTP 200 `application/pdf`; coverage COMPLETE; `text_layer.status=COMPLETE`; `quality_summary=PASS` |
| producer_unicoil | producer_unicoil-v3 | 6 | 21 (= 1+2+3+4+5+6) | 6 (6 `application/pdf`; `license_capture_required: false`) | 6 | 6 | All HTTP 200 `application/pdf`; coverage COMPLETE; `text_layer.status=COMPLETE`; `quality_summary=PASS` |

S12B-IR3-F02 note (slot 4): the RunReport figures are the deferred S11/S12a aggregate-count artefact (`pipeline._run_units` sums per-unit `coverage.requests_made`), not transport counts; neither run exceeded its budget; `pipeline.py` unchanged (KL-65). The six SASO records were subsequently rebuilt from `saso_documents-v4` under OD-11 (see "Slot 4 correction round" below).

## Per-entry detail (T7-v3)

### saso_documents (run `20260912T053622Z`)

| entry | HTTP | pages | lines | text_layer.status |
|---|---:|---:|---:|---|
| Machinery Safety | 200 | 106 | 4854 | COMPLETE |
| Conformity Models | 200 | 37 | 1628 | COMPLETE |
| Explosive Atmospheres | 200 | 38 | 1666 | COMPLETE |
| Electromagnetic Compatibility | 200 | 28 | 1246 | COMPLETE |
| Electrical/Electronic Equipment | 200 | 14 | 638 | COMPLETE |
| Communications/IT Devices | 200 | 37 | 1842 | COMPLETE |

### producer_unicoil (run `20260912T053955Z`)

| entry | HTTP | pages | lines | text_layer.status |
|---|---:|---:|---:|---|
| ESG Report | 200 | 59 | 1527 | COMPLETE |
| EPD Hot Dip GL Steel | 200 | 22 | 1141 | COMPLETE |
| EPD PPGI Steel | 200 | 22 | 1141 | COMPLETE |
| GI-Coil Verification | 200 | 1 | 47 | COMPLETE |
| PPGI-Coil Verification | 200 | 1 | 46 | COMPLETE |
| HPD Hot Dip Galvanized Steel | 200 | 21 | 1720 | COMPLETE |

## Changed-file set vs plan + IAC-13

Plan `files.modify` / `files.create` / `files.generated_once` plus IAC-13 pin tests; slot-3 additions: `config/acquisition_sources.v1.yaml` (SR-06 terms), `-v3` lists, twelve records + raw payloads, `src/ior_mvp/acquisition/documents/store.py` (reconstruct fix), control docs (ADR-017, KL-54–63, runbook, BUILD_PROGRESS, REQUIREMENTS_TRACEABILITY §N, state.json), second manifest artifacts.

## Stop conditions

None triggered. [14] PASS after second manifest generation.

---

# Slot 4 correction round (implementer-fable, 2026-09-12 06:25Z–06:58Z) — S12B-IR3-F01/F02, A02/A03/A05/A07

No network in this round; `UV_OFFLINE=1` on every `make`/`uv run`; no `IOR_ACQUISITION_LIVE`; `.env` unread; index empty throughout. All plan commands were printed from `plan-1.json` by `/tmp/s12b_slot4/run_gates.py` before execution; full transcripts are under `/tmp/s12b_slot4/` (`gates_pre.md`, `gates_14a.md`, `gates_post.md`, `gates_final.md`, `make_ci*.txt`, `red_records*.txt`, `build_v4.txt`, `compare_records.txt`).

## Proving tests — RED against the pre-correction tree (06:27:35Z)

```
$ pytest -q tests/test_acquisition_document_records.py
E       AssertionError: assert 'ar' in ['en']                                   (…641a518f410a-1bfd6143aaa9, line 82)
E       AssertionError: assert 'ar' in ['en']                                   (…710bf26c140e-b25658901d54, line 82)
E           assert 'ar' in ['en']                                               (test_all_six_saso_records_declare_arabic_and_reference_v4)
E           assert ('ar' in ['en']) == True                                     (test_declared_languages_are_consistent_with_derived_script[saso_documents])
E       FileNotFoundError: … data/documents/saso_documents/lists/saso_documents-v4.json
E       AssertionError: assert 'aggregate-count' in ' (open, not fabricated)… (test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count ×2)
7 failed, 2 passed in 0.06s
```

## Proving tests — GREEN after the corrections (06:33Z) and CID pin unchanged

```
$ pytest -q tests/test_acquisition_document_records.py tests/test_integrity_contract.py::test_s12b_core_v2_document_contracts tests/test_acquisition_document_textlayer.py::test_arabic_cid_pdf_preserves_logical_order_verbatim
11 passed in 0.09s
```

## OD-11 rebuild — DocumentBuildReport (06:30:12Z–06:30:22Z, exit 0)

```
$ UV_OFFLINE=1 make build-documents SOURCE=saso_documents LIST_ID=saso_documents-v4
PYTHONPATH=src /home/barami/.local/bin/uv run --locked --extra dev python -m ior_mvp.acquisition build-documents --source saso_documents --list-id saso_documents-v4
Rotated text discovered. Output will be incomplete.
{
  "already_stored": [],
  "built": [
    "DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9",
    "DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661",
    "DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54",
    "DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d",
    "DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b",
    "DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf"
  ],
  "skipped_no_entry": [],
  "unavailable": []
}
```

## OD-11 per-record diff key list (removed v3-built record vs rebuilt v4 record; `/tmp/s12b_slot4/compare_records.py`)

Identical for all six records — `document_id` same, `pages` identical:

```
DIFF /declared/languages: ['en'] -> ['ar', 'en']      (E-001, E-003, E-004, E-006)   |  ['en'] -> ['ar']   (E-002, E-005)
DIFF /evidence[0]/observation_context/languages: same change (passport copy of the declared languages)
DIFF /list_ref/list_id: 'saso_documents-v3' -> 'saso_documents-v4'
DIFF /list_ref/path: 'documents/saso_documents/lists/saso_documents-v3.json' -> 'documents/saso_documents/lists/saso_documents-v4.json'
DIFF /list_ref/sha256: '8a12aca74e38a53b8f3f83f8a148b92f653bce73c382260322e9ef837b1b26f6' -> '16d9e29bd86f720c38a29ffcd7a24e5140c94a2893226fac7f67183a3a4338bb'
ALL_DIFFS_WITHIN list_ref.{path,sha256,list_id} + declared.languages + evidence[0].observation_context.languages
```

Removed-record and rebuilt-record SHA-256s: `implementation_log.md` (slot-4 section). Corrected `languages`: SASO E-001 `["ar","en"]`, E-002 `["ar"]`, E-003 `["ar","en"]`, E-004 `["ar","en"]`, E-005 `["ar"]`, E-006 `["ar","en"]`; UNICOIL E-001…E-006 `["en"]` (verified truthful, unchanged).

## T10 regression (06:36:00Z–06:36:19Z)

```
$ pytest -q --ignore=tests/test_integrity_contract.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths
1871 passed, 1 deselected, 1 warning in 18.98s
```

## Pre-generation gates (06:36:26Z–06:37:10Z; all exit 0)

`[0] BRANCH_OK` · `[1] PYPDF_PIN_OK` · `[3] 29 passed` · `[4] 938 passed` · `[5] RECONSTRUCTION PASS (1 snapshots, 4 artifacts) / DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts) / PREGEN_RECON_OK` · `[6] S11_S12A_BYTES_UNCHANGED` · `[7] FROZEN_ROOTS_UNCHANGED` · `[8] BYTE_IDENTICAL_SET_OK` · `[9] 42 passed` · `[10] SMOKE PASS` · `[11] CONFIG_1_2_0_AND_RAW_RECORDS_OK` · `[12] PYTHON_STANDARDS_OK` · `[13] PROHIBITED FILE SCAN PASS (560 tracked files) / THRESHOLD LITERAL SCAN PASS (52 Python files; 23 configured numeric values) / SCANNERS_OK` · `[22] CORE_05_STATUS_ROWS_OK` · `[23] CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]` · `[24] CORE_04_DOCUMENT_SECTION_OK` · `[25] RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK` · `[25] corrected RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK` · `[26] DOCUMENT_TREE_CLEAN 29`.

## Manifest run 3 (OD-10) and immediate [14]

```
$ python3 scripts/build_manifests.py          # 2026-09-12T06:37:37Z, exit 0 (sole generator invocation of this round)
before: d55aceb3f03c8b8bcdda2e7653f2b9d7a4cc620779200a0db8c536b611143fae  data/manifests/snapshot_manifest.json
        de7a9fd05d67a8fad32cfa9ea133cbfdd57300868d03df8af68bb28c00b9471e  docs/authority/authority_hashes.json
after:  4fb8592d1b9d1e67c82d22dc3cd7a90ca9ebfb62d08117a818819858d29764c4  data/manifests/snapshot_manifest.json
        79015f4cee58ca3e61b5fd1ce28bc5543c54b0556c899eb1895b66d0835f8364  docs/authority/authority_hashes.json
§11 rows mirrored: config/acquisition_sources.v1.yaml bf45f2e7259b6a2c3aba57e6b2375fafa5a990c04faf5d0d8d501b29feeb9981 20,093
                   docs/core/04_CANONICAL_DATA_MODEL.md 3f7a06c5c7d82da905030fcf808cb2016fc798ff9fdb7d740617ea6119721086 20,942
                   docs/core/05_DATA_SOURCES_AND_INGESTION.md 11c45ada39641986c6dcd97f53253a35924634741c36adbe441f8dc429bf3b0c 21,912
SECTION_11_MIRROR_OK
```

### [14] (immediate, 06:38:23Z)
```
MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT
exit=0
```

## Post-generation gates (06:38:33Z–06:39:46Z; all exit 0)

### [14] (again)
```
MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT
```

### [15]
```
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

### [16]
```
SCENARIO VALIDATION PASS (2 scenarios)
```

### [17]
```
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
POSTGEN_RECON_OK
```

### [18]
```
1888 passed, 1 warning in 18.69s
```

### [19]
```
PARTNER_SNAPSHOT_BYTE_IDENTICAL
```

### [20]
```
ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12
```

### [22]–[24], [26]
```
CORE_05_STATUS_ROWS_OK
CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
CORE_04_DOCUMENT_SECTION_OK
DOCUMENT_TREE_CLEAN 29
```

### [25] verbatim (vacuous pathspec; recorded per IAC-9)
```
$ ! rg -q 'pypdf' ':(glob)src/ior_mvp/*.py' Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
exit=0
```

### [25] corrected (IAC-9)
```
$ ! rg -q 'pypdf' src/ior_mvp/*.py Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK
exit=0
```

## [21] `make ci` on the exact final candidate tree (`UV_OFFLINE=1`; 06:54:25Z–06:57:52Z; exit 0)

Two earlier full passes (06:39:55Z–06:43:19Z and 06:46:12Z–06:49:38Z) were also green; the last one is the record because it follows the final non-slice-record edit (KL-63 phrase).

```
PROHIBITED FILE SCAN PASS (560 tracked files)
THRESHOLD LITERAL SCAN PASS (52 Python files; 23 configured numeric values)
UI CONTRACT CHECK PASS
ES MODULE CHECK PASS (19 files)
INTEGRITY PASS
SCENARIO VALIDATION PASS (2 scenarios)
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
1888 passed, 1 warning in 18.73s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
BROWSER PREFLIGHT PASS
118 passed, 4 deselected in 132.82s (0:02:12)
4 passed, 118 deselected in 26.02s
exit=0
```

`browser_tests/` byte-identical to HEAD (no baseline update); no `Downloading`/`Downloaded` lines (the e2e extra re-installed from the local uv cache under `UV_OFFLINE=1`).

## Handoff gates re-run on the final tree (06:49:49Z–06:51:11Z; all exit 0)

`[5] PREGEN_RECON_OK (1/4 + 12/12)` · `[14] MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT` · `[15] INTEGRITY PASS` · `[17] POSTGEN_RECON_OK (1/4 + 12/12)` · `[19] PARTNER_SNAPSHOT_BYTE_IDENTICAL` · `[20] ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12` · `[25] + corrected RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK` · `[6] S11_S12A_BYTES_UNCHANGED` · `[7] FROZEN_ROOTS_UNCHANGED`. The only later non-slice-record edit (KL-63 phrase, 06:52Z) was followed by `pytest -q tests/test_integrity_contract.py tests/test_acquisition_document_records.py` → 25 passed and by the final `make ci` above.

## Stop conditions (slot 4)

None triggered: [14] PASS immediately after the third generation; the rebuild proceeded offline from the existing run; no frozen oracle failed; no existing test needed editing.

## Slot 5 OD-13 record rebuild verification (2026-09-12)

The twelve pre-removal paths and SHA-256 values are recorded in `implementation_log.md`. Both offline rebuild commands exited 0: `make build-documents SOURCE=saso_documents LIST_ID=saso_documents-v4` built six records, and `make build-documents SOURCE=producer_unicoil LIST_ID=producer_unicoil-v3` built six records. The following scratch verification loaded each selected raw PDF with `pypdf`, compared physical page counts and indexes, recomputed every page hash as `sha256("\n".join(lines))`, compared `coverage.superseded_run_ids` with `RawStore.latest_runs`, ran `validate_document_record` and `assert_passport_complete`, reconstructed byte-for-byte, and compared the twelve ids with the pre-removal set:

| document_id | page_count | PDF pages | hash rule | superseded_run_ids | reconstruct |
|---|---:|---:|---|---|---|
| `DOC-PRODUCER-UNICOIL-70151205e3a4-1762d53d6cab` | 22 | 22 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0` | 1 | 1 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a` | 1 | 1 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-PRODUCER-UNICOIL-cec488bffcda-3017de71d962` | 21 | 21 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-PRODUCER-UNICOIL-d7302a241f7d-f35cfd06f777` | 22 | 22 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-PRODUCER-UNICOIL-ecb55cc26093-612efea9a835` | 59 | 59 | OK | `20260912T052305Z,20260912T052309Z` | MATCH |
| `DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9` | 37 | 37 | OK | `20260912T052304Z,20260912T052309Z` | MATCH |
| `DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661` | 37 | 37 | OK | `-` | MATCH |
| `DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54` | 106 | 106 | OK | `20260912T052304Z,20260912T052309Z` | MATCH |
| `DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d` | 38 | 38 | OK | `-` | MATCH |
| `DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b` | 21 | 21 | OK | `-` | MATCH |
| `DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf` | 28 | 28 | OK | `-` | MATCH |

Output terminator: `ALL_12_RECORDS_VALIDATED_PASSPORTED_RECONSTRUCTED_IDS_UNCHANGED` (exit 0). Pypdf emitted the already-disclosed rotated-text, malformed-CMap and embedded-HTTP-header diagnostics while reading the unchanged publisher bytes; validation and reconstruction still matched.

## Slot 5 OD-13 verification transcript

Approved plan: `.autonomous-workflow/plans/s12b-document-store-disclosures-tenders/cycle-1/plan-1.json`, SHA-256 `c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`. Each numbered command below was printed from that JSON immediately before execution; the immutable index is the exact command quotation source. All exits were 0.

- T10 command: `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q --ignore=tests/test_integrity_contract.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths`. Output: `1904 passed, 1 deselected, 1 warning in 19.16s`.
- `[0]` command: `test "$(git branch --show-current)" = slice/s12b-document-store-disclosures-tenders && git merge-base --is-ancestor cdfd4ba4b016619b7ab33a373d334f22c337166d HEAD && echo BRANCH_OK`. Output: `BRANCH_OK`.
- `[1]` command: plan `verification[1]`, the `pypdf==6.16.1` dev-only/runtime-free/lock/no-RTL-extras Python assertion. Output: `PYPDF_PIN_OK`.
- `[2]` command: `"$HOME/.local/bin/uv" sync --locked --extra dev && echo UV_LOCKED_OK`. **Skipped as owner-directed** because `UV_OFFLINE=1` is mandatory and the locked environment had already been proven by the prior candidate and by offline `make ci`; no network or standalone synchronization was attempted.
- `[3]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_document_textlayer.py tests/test_acquisition_document_lists.py`. Output: `40 passed in 0.33s`.
- `[4]` command: plan `verification[4]`, the complete named acquisition/document/config/reconstruction/stored-artifact pytest list. Output: `960 passed in 14.62s`.
- `[5]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest > /tmp/s12b_recon_pregen.txt; cat /tmp/s12b_recon_pregen.txt; grep -q '^RECONSTRUCTION PASS (1 snapshots, 4 artifacts)$' /tmp/s12b_recon_pregen.txt && grep -q '^DOCUMENT RECONSTRUCTION PASS (' /tmp/s12b_recon_pregen.txt && echo PREGEN_RECON_OK`. Output: `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`; `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`; `PREGEN_RECON_OK`.
- `[6]` command: plan `verification[6]`, the S11/S12a raw/partner tracked-and-untracked byte oracle. Output: `S11_S12A_BYTES_UNCHANGED`.
- `[7]` command: plan `verification[7]`, the public/synthetic/golden/browser tracked-and-untracked byte oracle. Output: `FROZEN_ROOTS_UNCHANGED`.
- `[8]` command: plan `verification[8]`, the scoped byte-identical source/config/Core/CI/Docker oracle. Output: `BYTE_IDENTICAL_SET_OK`.
- `[9]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py`. Output: `42 passed in 1.28s`.
- `[10]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/demo_smoke.py`. Output: `SMOKE PASS`; steel public `INVESTIGATE`; steel simulated `ADVANCE` with real state unchanged; polypropylene public `REJECT`; AR/EN extraction golden gate `100%`.
- `[11]` command: plan `verification[11]`, the config-1.2.0/source-class/structural-pin/unchanged-S11/raw-and-list Python oracle. Output: `CONFIG_1_2_0_AND_RAW_RECORDS_OK`.
- `[12]` command: plan `verification[12]`, the acquisition AST no-bare-except/public-type-hint oracle. Output: `PYTHON_STANDARDS_OK`.
- `[13]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/check_prohibited_files.py && python3 scripts/check_threshold_literals.py && python3 -m compileall -q src scripts tests && echo SCANNERS_OK`. Output: `PROHIBITED FILE SCAN PASS (560 tracked files)`; `THRESHOLD LITERAL SCAN PASS (52 Python files; 23 configured numeric values)`; `SCANNERS_OK`.
- `[14]` command: plan `verification[14]`, the Python oracle comparing HEAD and generated manifest rows for all S11/S12a/frozen prefixes, requiring all document raw/list rows and exact unchanged authority rows/path set. It ran immediately after the §11 mirror and again post-generation. Output both times: `MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`.
- `[15]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py`. Output: `INTEGRITY PASS` for `data/manifests/snapshot_manifest.json` and `docs/authority/authority_hashes.json`.
- `[16]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/validate_scenarios.py`. Output: `SCENARIO VALIDATION PASS (2 scenarios)`.
- `[17]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all > /tmp/s12b_recon_postgen.txt; cat /tmp/s12b_recon_postgen.txt; grep -q '^RECONSTRUCTION PASS (1 snapshots, 4 artifacts)$' /tmp/s12b_recon_postgen.txt && grep -q '^DOCUMENT RECONSTRUCTION PASS (' /tmp/s12b_recon_postgen.txt && echo POSTGEN_RECON_OK`. Output: `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`; `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`; `POSTGEN_RECON_OK`.
- `[18]` command: `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q`. Output: `1921 passed, 1 warning in 19.65s`.
- `[19]` command: plan `verification[19]`, the byte/hash/manifest-row oracle for `PARTNERS-SAU-WITS-TRADE-2026-09-03.json`. Output: `PARTNER_SNAPSHOT_BYTE_IDENTICAL`.
- `[20]` command: plan `verification[20]`, `DocumentStore.iter_records()` plus `validate_document_record`, `assert_passport_complete` and `reconstruct_document` for every record. Output: `ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12`.
- `[21]` command: `make ci` under the required environment prefix and `UV_OFFLINE=1`. Output: exit 0; `1921 passed, 1 warning`; `SMOKE PASS`; `BROWSER PREFLIGHT PASS`; `118 passed, 4 deselected`; `4 passed, 118 deselected`.
- `[22]` command: plan `verification[22]`, the Core 05 §3.1 byte identity and exact S12b §3.2/§3.3 row-delta oracle. Output: `CORE_05_STATUS_ROWS_OK`.
- `[23]` command: plan `verification[23]`, the Core 03/09 insertion-only oracle. Output: `CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]`.
- `[24]` command: plan `verification[24]`, the Core 04 unchanged-S12a-block, one-DocumentRecord-section and required-token oracle. Output: `CORE_04_DOCUMENT_SECTION_OK`.
- `[25]` command as written: `! rg -q 'pypdf' ':(glob)src/ior_mvp/*.py' Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK`. Output included the known invalid Git-pathspec-as-rg-path diagnostic, then `RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK`.
- `[25 corrected]` command: `! rg -q 'pypdf' src/ior_mvp/*.py Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK_CORRECTED`. Output: `RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK_CORRECTED`.
- `[26]` command: plan `verification[26]`, the path/source partition/no-test-double/known-source JSON tree oracle. Output: `DOCUMENT_TREE_CLEAN 29`.

Fourth/final manifest receipt: `OD13_MANIFEST_START_UTC=2026-09-12T07:30:41Z`, `OD13_MANIFEST_END_UTC=2026-09-12T07:30:41Z`, `OD13_MANIFEST_EXIT=0`; snapshot manifest 214 rows, SHA-256 `86328f39e9a2a44668184b1bedf4a2609bf58b34eb405d714ac51d69dfc353cb`; authority hashes 16 rows, SHA-256 `f6d681f481be7f7b8ae57b025865e15b423e5e6387bb8e624049d296826c5100`.

## Final slot-5 candidate identity (IAC-6)

Base `cdfd4ba4b016619b7ab33a373d334f22c337166d`; slice records under `.workflow/slices/S12b-document-store-disclosures-tenders/` excluded; `git diff --name-only HEAD` union `git ls-files --others --exclude-standard`; sorted canonical JSON with per-file path/SHA-256/byte count and `sort_keys=True,separators=(',', ':'),ensure_ascii=False` plus LF.

**SHA-256 `94eb2f4e95a1a8dedbdadd089680ef51932d3542b70d29df368ae9aa91dd45f7`; 196 files; index empty.**

Final-tree `[21]` rerun after the `.workflow/state.json` timestamp update: `make ci` under `UV_OFFLINE=1`, exit 0 at `2026-09-12T07:44:55Z`; `1921 passed, 1 warning in 19.06s`; `SMOKE PASS`; `BROWSER PREFLIGHT PASS`; `118 passed, 4 deselected in 131.60s`; `4 passed, 118 deselected in 25.98s`. No baseline update or network occurred.

## Slot 5 OD-14 correction evidence (2026-09-12T08:23:45Z)

Plan SHA-256 was rechecked before gates:

```text
c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5  .autonomous-workflow/plans/s12b-document-store-disclosures-tenders/cycle-1/plan-1.json
```

### F01/F02 RED and GREEN

Initial RED command:

```text
pytest -q tests/test_acquisition_document_textlayer.py::test_html_derivation_block_tags_script_style_bom_and_arabic tests/test_acquisition_document_textlayer.py::test_html_derivation_literal_dd5_block_boundaries tests/test_acquisition_document_lists.py::test_list_sha256_and_write_once_path_rules tests/test_acquisition_document_store.py::test_acquire_documents_rejects_unsafe_list_id_before_transport
```

Output: `6 failed in 0.11s`. Failures were the exact fixture tuple; table, nested and list tuples; missing store path rejection; and pipeline reaching `Path.read_text` for `../evil`.

CLI preflight RED command:

```text
pytest -q tests/test_acquisition_document_cli.py::test_document_cli_rejects_unsafe_list_id_before_dependencies
```

Output: `2 failed in 0.05s`; both acquire/build variants reached the fail-on-call `_deps` double.

First GREEN proving command:

```text
pytest -q tests/test_acquisition_document_textlayer.py::test_html_derivation_block_tags_script_style_bom_and_arabic tests/test_acquisition_document_textlayer.py::test_html_derivation_literal_dd5_block_boundaries tests/test_acquisition_document_textlayer.py::test_html_derivation_deterministic_across_processes tests/test_acquisition_document_lists.py::test_list_sha256_and_write_once_path_rules tests/test_acquisition_document_store.py::test_acquire_documents_rejects_unsafe_list_id_before_transport
```

Output: `7 passed in 0.13s`.

Final focused GREEN command:

```text
pytest -q tests/test_acquisition_document_cli.py::test_document_cli_rejects_unsafe_list_id_before_dependencies tests/test_acquisition_document_textlayer.py tests/test_acquisition_document_lists.py tests/test_acquisition_document_store.py
```

Output: `74 passed in 0.50s`.

Hand-derived literal DD-5 probe tuples:

```text
<table><tr><td>a</td><td>b</td></tr></table>
("", "", "", "a", "", "b", "", "")

<div><p>a</p></div>
("", "", "a", "")

<ul><li>one</li><li>two</li></ul>
("", "", "one", "", "two", "")
```

The exact fixture tuple is pinned in `tests/test_acquisition_document_textlayer.py`; its U+200F line is `"العربية paragraph with U+200F\u200f marker"`.

### Plan-gate transcript

Every command below was loaded from the immutable JSON, printed as `PLAN[index] COMMAND: <exact JSON command>` immediately before execution, and then run under the required environment prefix. The exact command strings are unchanged from, and quoted in full in, the preceding “Slot 5 OD-13 verification transcript”; this OD-14 run printed them again before execution. Outputs:

- `[0]` command `verification[0]` → `BRANCH_OK`; exit 0.
- `[1]` command `verification[1]` → `PYPDF_PIN_OK`; exit 0.
- `[2]` command `"$HOME/.local/bin/uv" sync --locked --extra dev && echo UV_LOCKED_OK` → **SKIPPED as owner-directed**; mandatory `UV_OFFLINE=1`, no standalone sync.
- `[3]` command `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_document_textlayer.py tests/test_acquisition_document_lists.py` → `44 passed in 0.37s`; exit 0.
- `[4]` command `verification[4]` (the exact acquisition/document/config/reconstruction/stored-artifact pytest list quoted above) → `963 passed in 14.65s`; exit 0.
- `[5]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest > /tmp/s12b_recon_pregen.txt; cat /tmp/s12b_recon_pregen.txt; grep -q '^RECONSTRUCTION PASS (1 snapshots, 4 artifacts)$' /tmp/s12b_recon_pregen.txt && grep -q '^DOCUMENT RECONSTRUCTION PASS (' /tmp/s12b_recon_pregen.txt && echo PREGEN_RECON_OK` → `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`; `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`; `PREGEN_RECON_OK`; exit 0.
- `[6]` command `verification[6]` → `S11_S12A_BYTES_UNCHANGED`; exit 0.
- `[7]` command `verification[7]` → `FROZEN_ROOTS_UNCHANGED`; exit 0.
- `[8]` command `verification[8]` → `BYTE_IDENTICAL_SET_OK`; exit 0.
- `[9]` command `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py` → `42 passed in 1.23s`; exit 0.
- `[10]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/demo_smoke.py` → `SMOKE PASS`; steel public `INVESTIGATE`; steel simulated `ADVANCE`, real state unchanged; polypropylene public `REJECT`; AR/EN 100%; exit 0.
- `[11]` command `verification[11]` → `CONFIG_1_2_0_AND_RAW_RECORDS_OK`; exit 0.
- `[12]` command `verification[12]` → `PYTHON_STANDARDS_OK`; exit 0.
- `[13]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/check_prohibited_files.py && python3 scripts/check_threshold_literals.py && python3 -m compileall -q src scripts tests && echo SCANNERS_OK` → prohibited scan 560 files; threshold scan 52 Python files/23 configured values; `SCANNERS_OK`; exit 0.
- `[14]` command `verification[14]` → `MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`; exit 0.
- `[15]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py` → `INTEGRITY PASS`; exit 0.
- `[16]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/validate_scenarios.py` → `SCENARIO VALIDATION PASS (2 scenarios)`; exit 0.
- `[17]` command `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all > /tmp/s12b_recon_postgen.txt; cat /tmp/s12b_recon_postgen.txt; grep -q '^RECONSTRUCTION PASS (1 snapshots, 4 artifacts)$' /tmp/s12b_recon_postgen.txt && grep -q '^DOCUMENT RECONSTRUCTION PASS (' /tmp/s12b_recon_postgen.txt && echo POSTGEN_RECON_OK` → reconstruction 1/4; documents 12/12; `POSTGEN_RECON_OK`; exit 0.
- `[18]` command `PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q` → **`1928 passed, 1 warning in 19.40s`**; exit 0.
- `[19]` command `verification[19]` → `PARTNER_SNAPSHOT_BYTE_IDENTICAL`; exit 0.
- `[20]` command `verification[20]` → `ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12`; exit 0.
- `[22]` command `verification[22]` → `CORE_05_STATUS_ROWS_OK`; exit 0.
- `[23]` command `verification[23]` → `CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]`; exit 0.
- `[24]` command `verification[24]` → `CORE_04_DOCUMENT_SECTION_OK`; exit 0.
- `[25]` command `! rg -q 'pypdf' ':(glob)src/ior_mvp/*.py' Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK` → expected invalid rg path diagnostic plus `RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK`; exit 0.
- `[25 corrected]` command `! rg -q 'pypdf' src/ior_mvp/*.py Dockerfile && ! rg -q -e 'import urllib' -e 'from urllib' -e 'import socket' -e 'import ssl' -e 'import http' src/ior_mvp/acquisition/documents src/ior_mvp/acquisition/connectors/documents.py && echo RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK_CORRECTED` → `RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK_CORRECTED`; exit 0.
- `[26]` command `verification[26]` → `DOCUMENT_TREE_CLEAN 29`; exit 0.

### Offline `make ci`

Command: `UV_OFFLINE=1 make ci`; exit 0. Tail:

```text
1928 passed, 1 warning in 19.27s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
BROWSER PREFLIGHT PASS
118 passed, 4 deselected in 131.50s (0:02:11)
4 passed, 118 deselected in 26.46s
```

No browser baseline was updated. The e2e extra was restored from the local cache under `UV_OFFLINE=1`; no network command ran.

### Protected bytes, manifest count and final IAC-6

Read-only comparison covered every `data/**` file, every path represented in `docs/authority/authority_hashes.json`, every Core file, `docs/authority/authority_hashes.json`, `docs/authority/00_AUTHORITY_MANIFEST.md` and the snapshot manifest. Candidate-listed paths were compared to `.autonomous-workflow/candidates/s12b-document-store-disclosures-tenders/candidate-slot-5.json`; paths unchanged by that candidate were compared to HEAD:

```text
PROTECTED_CANDIDATE_PATHS 233
PROTECTED_BYTE_IDENTICAL
```

Manifest run count remains **4/4**, with UTC receipts `05:26:47Z`, `05:43:02Z`, `06:37:37Z`, `07:30:41Z`. No manifest generator ran in OD-14.

IAC-6 recomputation used base `cdfd4ba4b016619b7ab33a373d334f22c337166d`, excluded the two S12b slice records, and canonicalized the sorted union of `git diff --name-only HEAD` and `git ls-files --others --exclude-standard` with per-file SHA-256 and byte count:

```text
IAC6_SHA256 5258e7d4dbc144d940792dcd57981e29d6faa1a301056fb9b26be0a00f3f674b
IAC6_FILE_COUNT 196
INDEX_EMPTY True
HEAD cdfd4ba4b016619b7ab33a373d334f22c337166d
```
