# S12c test evidence

## Approved plan

Path: `.autonomous-workflow/plans/s12c-entity-resolution-bilingual-ids/cycle-1/plan-1-dispatch1.json`  
SHA-256: `6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd`

Every command below was printed directly from the approved JSON before execution.

## T0 verification

### Baseline suite and repository checks

```text
pytest -q
1928 passed, 1 warning in 21.75s
exit=0

python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
exit=0

python3 scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
exit=0

TEST_FIXTURE_RECORDS_FILE_FREE
exit=0
```

### [0]

Command:

```text
test "$(git branch --show-current)" = slice/s12c-entity-resolution-bilingual-ids && git merge-base --is-ancestor a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941 HEAD && echo BRANCH_OK
```

Output, exit 0:

```text
BRANCH_OK
```

### [6]

Command:

```text
git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)" && echo FROZEN_ROOTS_UNCHANGED
```

Output (re-run after the owner-confirmed bytecode relocation), exit 0:

```text
FROZEN_ROOTS_UNCHANGED
```

### [5]

Command:

```text
git diff --quiet HEAD -- data/raw data/documents data/snapshots/partners config/acquisition_sources.v1.yaml && test -z "$(git ls-files --others -- data/raw data/documents data/snapshots/partners)" && echo S11_S12A_S12B_BYTES_UNCHANGED
```

Output (owner-requested re-run), exit 0:

```text
S11_S12A_S12B_BYTES_UNCHANGED
```

### [7]

Command:

```text
git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition ':(exclude)src/ior_mvp/acquisition/cli.py' ':(exclude)src/ior_mvp/acquisition/repository.py' ':(exclude)src/ior_mvp/acquisition/entities' .github/workflows/ci.yml Dockerfile pyproject.toml uv.lock tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py tests/test_offline_guard.py tests/test_acquisition_document_records.py config ':(exclude)config/entity_resolution.v1.yaml' docs/core ':(exclude,glob)docs/core/0[3459]_*' docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx && echo BYTE_IDENTICAL_SET_OK
```

Output, exit 0:

```text
BYTE_IDENTICAL_SET_OK
```

### [8]

Command:

```text
PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py tests/test_acquisition_document_records.py
```

Output, exit 0:

```text
51 passed in 1.57s
```

### [9]

Command:

```text
PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/demo_smoke.py
```

Output, exit 0:

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

## T1 verification

### [1]

Command: exact plan verification [1] (printed from the approved JSON).

Output, exit 0:

```text
ENTITY_RULES_OK
```

### [2] — first-file gate required by T1

The approved [2] command was printed. T1 runs its designated first file; the full exact [2] command follows at T2 after the other two files exist.

```text
pytest -q tests/test_entity_normalisation.py
23 passed in 0.07s
exit=0
```

### [7]

Command: exact plan verification [7] as recorded under T0 (printed again before this run).

Output, exit 0:

```text
BYTE_IDENTICAL_SET_OK
```

## T2 verification

### [2]

Command:

```text
PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_entity_normalisation.py tests/test_entity_ids.py tests/test_entity_mentions.py
```

Output, exit 0:

```text
50 passed in 0.16s
```

### [7]

Command: exact plan verification [7] as recorded under T0.

Output, exit 0:

```text
BYTE_IDENTICAL_SET_OK
```

## T3 verification

### [2]

Command: exact plan verification [2].

```text
50 passed in 0.18s
exit=0
```

### [3] — IAC-8 T3 subset

The exact [3] command was printed. Per IAC-8, `tests/test_entity_resolution_cli.py` was omitted until T4; all other listed files ran:

```text
213 passed in 4.78s
exit=0
```

### [7]

```text
BYTE_IDENTICAL_SET_OK
exit=0
```

### [10]

Command: exact plan verification [10].

```text
PYTHON_STANDARDS_OK
exit=0
```

## T4 verification

### [3]

```text
225 passed in 5.31s
exit=0
```

### [4]

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (0 artifacts, 0 links)
PREGEN_RECON_OK
exit=0
```

### [5]–[11]

```text
[5] S11_S12A_S12B_BYTES_UNCHANGED
[6] FROZEN_ROOTS_UNCHANGED
[7] BYTE_IDENTICAL_SET_OK
[8] 51 passed in 1.63s
[9] SMOKE PASS
    Steel / public: INVESTIGATE
    Polypropylene / public: REJECT generic capacity
[10] PYTHON_STANDARDS_OK
[11] PROHIBITED FILE SCAN PASS (729 tracked files)
     THRESHOLD LITERAL SCAN PASS (59 Python files; 23 configured numeric values)
     SCANNERS_OK
all exit=0
```

### [24]

```text
ENTITY_MODULES_OFFLINE_AND_ENGINE_FREE_OK
exit=0
```

### [26]

```text
BUILD_ENTITIES_PARSER_OK
MAKE_TARGET_OK
exit=0
```

## T5 real evidence build and verification

Mention list: `mentions-v1`, 38 mentions, SHA-256 `a12e24c31b02f11a0a7e116760b8a80814ddd97241716651c8cc60184ca1cc83`, 21,091 bytes.

Final artifact after two test-first resolver corrections: `ENTITIES-2026-09-12-a12e24c31b02`, SHA-256 `97e68dd3e79b0ec1acb01bcdb5c5695296ba3d917f639afbd4079702d052f701`, 57,033 bytes.

Final EntityBuildReport:

```text
entities_by_type: COMPANY 5, PLANT 2, LINE 0, LICENCE_HOLDER 0
links_by_status: DETERMINISTIC_IDENTIFIER 0, EXACT_DOCUMENT_EVIDENCE 27,
                 PROPOSED_PENDING_REVIEW 3, UNRESOLVED 8
passport_links_by_status: DETERMINISTIC_IDENTIFIER 0,
                          EXACT_DOCUMENT_EVIDENCE 10,
                          PROPOSED_PENDING_REVIEW 0, UNRESOLVED 8
documents_without_mentions:
  DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0
  DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a
exit=0
```

### [4]

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
PREGEN_RECON_OK
exit=0
```

### [12]

```text
ZERO_LINKS_ABOVE_DETERMINISTIC_WITHOUT_EVIDENCE 38
exit=0
```

### [13]

```text
ENTITY_TREE_CLEAN 2
exit=0
```

### [3]

```text
225 passed in 5.35s
exit=0
```

The repository-tree artifact oracle is intentionally W3 until T7: `4 passed, 1 failed`; the only failure names the two verification-statement document IDs absent from the not-yet-updated Known Limitations record.

## T6 governed Core documentation

### [21]

```text
CORE_05_ENTITY_SECTIONS_OK
exit=0
```

### [22]

```text
CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
exit=0
```

### [23]

```text
CORE_04_ENTITY_SECTIONS_OK
exit=0
```

W2 closure:

```text
pytest -q tests/test_integrity_contract.py::test_s12c_core_v2_entity_contracts
1 passed in 0.02s
exit=0
```

## T7 control records

Artifact-oracle W3 closure:

```text
pytest -q tests/test_entity_resolution_artifact.py
5 passed in 0.05s
exit=0
```

### [25]

```text
CONTROL_RECORDS_PRESENT
exit=0
```

ADR-018 and machine-state pre-generation check:

```text
ADR018_PREGEN_AND_STATE_VALID
S12c manifest run count = 0
exit=0
```

## T8 pre-generation regression

```text
PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q --ignore=tests/test_integrity_contract.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths
2008 passed, 1 deselected, 1 warning in 22.18s
exit=0
```

Exact approved-plan verification [0]–[13] and [21]–[26] were printed and executed in index order; every command exited 0. Key outputs:

```text
[0] BRANCH_OK
[1] ENTITY_RULES_OK
[2] 50 passed in 0.16s
[3] 225 passed in 5.35s
[4] RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
    DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
    ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
    PREGEN_RECON_OK
[5] S11_S12A_S12B_BYTES_UNCHANGED
[6] FROZEN_ROOTS_UNCHANGED
[7] BYTE_IDENTICAL_SET_OK
[8] 51 passed in 1.69s
[9] SMOKE PASS — Steel public INVESTIGATE; Polypropylene public REJECT generic capacity
[10] PYTHON_STANDARDS_OK
[11] PROHIBITED FILE SCAN PASS (729 tracked files)
     THRESHOLD LITERAL SCAN PASS (59 Python files; 23 configured numeric values)
     SCANNERS_OK
[12] ZERO_LINKS_ABOVE_DETERMINISTIC_WITHOUT_EVIDENCE 38
[13] ENTITY_TREE_CLEAN 2
[21] CORE_05_ENTITY_SECTIONS_OK
[22] CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
[23] CORE_04_ENTITY_SECTIONS_OK
[24] ENTITY_MODULES_OFFLINE_AND_ENGINE_FREE_OK
[25] CONTROL_RECORDS_PRESENT
[26] BUILD_ENTITIES_PARSER_OK
     MAKE_TARGET_OK
```

## T9 single manifest generation

Exactly one S12c generator invocation:

```text
UTC=2026-09-12T11:25:47Z
PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/build_manifests.py
exit=0
```

Immediate [14], exit 0:

```text
MANIFEST_S11_S12A_S12B_ROWS_UNCHANGED_ENTITIES_PRESENT 2
```

The generated authority manifest contains 17 rows; its exact rows were mirrored into `docs/authority/00_AUTHORITY_MANIFEST.md` §11. No further generator run is authorized.

## T10 post-generation proof

### [14]

```text
MANIFEST_S11_S12A_S12B_ROWS_UNCHANGED_ENTITIES_PRESENT 2
exit=0
```

### [15]

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
exit=0
```

### [16]

```text
SCENARIO VALIDATION PASS (2 scenarios)
exit=0
```

### [17]

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
POSTGEN_RECON_OK
exit=0
```

### [18]

```text
2027 passed, 1 warning in 22.12s
exit=0
```

### [19] — executed with the approved multi-line command unchanged

```text
ALL_ENTITY_ARTIFACTS_VALIDATE_AND_RECONSTRUCT 1
exit=0
```

### [20]

`make ci`, exit 0. Tail:

```text
2027 passed, 1 warning in 22.01s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
BROWSER PREFLIGHT PASS
118 passed, 4 deselected in 130.66s (0:02:10)
4 passed, 118 deselected in 25.89s
```

### [21]–[26]

```text
[21] CORE_05_ENTITY_SECTIONS_OK
[22] CORE_03_09_INSERTION_ONLY_OK [['1', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
[23] CORE_04_ENTITY_SECTIONS_OK
[24] ENTITY_MODULES_OFFLINE_AND_ENGINE_FREE_OK
[25] CONTROL_RECORDS_PRESENT
[26] BUILD_ENTITIES_PARSER_OK
     MAKE_TARGET_OK
all exit=0
```

Final byte-identity proof after `make ci`:

```text
[5] S11_S12A_S12B_BYTES_UNCHANGED
[6] FROZEN_ROOTS_UNCHANGED
[7] BYTE_IDENTICAL_SET_OK
```

Plan hash re-verification:

```text
6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd
PLAN_HASH_REVERIFIED
```

## Candidate identity (IAC-6)

Base: `a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941`  
SHA-256: `c2370180494658f0e845584e39c212994d7c2f594efe5044142a5bd275e88649`  
File count: **38**  
Index: empty. Slice-record paths are excluded. Serialization is the canonical IAC-6 JSON plus trailing newline.

| Path | SHA-256 | Bytes |
|---|---|---:|
| `.workflow/state.json` | `da2c9285caf6e9e6d6a1f0c365785369c4e5232da34700cfd7fb4c869fe7bc57` | 25,100 |
| `Makefile` | `84a542fe628627268d2ed8b72ee0a948eb6bd197d6fc41d7f10b17c0c115a9aa` | 7,800 |
| `config/entity_resolution.v1.yaml` | `c320d2e8a92ad18786935f86366d2d826ffb33d413ebe493c11811f40da00bc9` | 2,594 |
| `data/entities/mentions/mentions-v1.json` | `a12e24c31b02f11a0a7e116760b8a80814ddd97241716651c8cc60184ca1cc83` | 21,091 |
| `data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json` | `97e68dd3e79b0ec1acb01bcdb5c5695296ba3d917f639afbd4079702d052f701` | 57,033 |
| `data/manifests/snapshot_manifest.json` | `471f104b10dfe3e25229de7122d460e3f7bf588c40cc715504e6ae5f5f748bd9` | 53,505 |
| `docs/ARCHITECTURE_DECISIONS.md` | `e92ae3002c3c72600c35365ef607846614e76b3f2b1b1463acb8e67602a9b3cf` | 90,450 |
| `docs/BUILD_PROGRESS.md` | `20609519a71e12ea7bc27275d9e06ee26a36d3142b1479402b73ce8c6b172003` | 27,016 |
| `docs/BUILD_ROADMAP.md` | `79f4d0b58069170f5a2a4defca1a3c04e10ddf912db5605565013668b69d1026` | 13,217 |
| `docs/KNOWN_LIMITATIONS.md` | `86c64e7bad4128fe0c63a8558269f222a08ab5f6b163ad5b92d06e2e3274ac52` | 32,491 |
| `docs/REQUIREMENTS_TRACEABILITY.md` | `ee39b51ad280f62ced42b02154985db38db7635413f140635470e497c821d27f` | 45,294 |
| `docs/authority/00_AUTHORITY_MANIFEST.md` | `bcb9486d281530a9fd1ecb29db6597d40ba4dc99c077510fa27be33b1d5fd9da` | 10,688 |
| `docs/authority/authority_hashes.json` | `a3d63ccf1b160e66da1e74a732085ec4a066e3b7bf5a1ac983ac4a1f7c461d71` | 3,052 |
| `docs/core/03_SYSTEM_ARCHITECTURE.md` | `5aa7dff4fb7631f9d991d08405b3540c413adcce913619df4f618e4a79d0291c` | 11,470 |
| `docs/core/04_CANONICAL_DATA_MODEL.md` | `b278e0918850b84879d4ab8c541980031a9f5d11b855275343b15408c9828705` | 23,320 |
| `docs/core/05_DATA_SOURCES_AND_INGESTION.md` | `892285e564026bf2afb0b3138111a8857e9814a7e979c3fbfe46fcb799d12d1b` | 23,120 |
| `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` | `f021ea4e9373a8b17b98984237f09c0b2bf8ece3581154bb12e02a2c6b3f2bd4` | 13,999 |
| `docs/implementation/ACQUISITION_RUNBOOK.md` | `9ffa1ce57c3f4359801af00cf960ff9e5d810c0dd8590e96b918bca3e258f21c` | 14,350 |
| `scripts/build_manifests.py` | `72645372b8bcc97320481c31381c3d3be75b62080b3ec4416208cffe7260fb5d` | 2,763 |
| `scripts/reconstruct_snapshot.py` | `4a2d24152a8692f8d239ae578dabf29a1bc7c0cedd6efbc77e292aad84921c65` | 10,441 |
| `src/ior_mvp/acquisition/cli.py` | `e23088719843dec075fda2c7d3caf565ca5fa380bbb7bbb16a9e44351036f217` | 10,273 |
| `src/ior_mvp/acquisition/entities/__init__.py` | `5e93c945605f39838abb8d3f6e5f1f631f26e9d94f7172c41f94f733499c9325` | 150 |
| `src/ior_mvp/acquisition/entities/ids.py` | `27056f0aff1aba6c6614392d64548c95ac9d25cd11d2a7fe54fa7c9099bf87b7` | 2,150 |
| `src/ior_mvp/acquisition/entities/mentions.py` | `0b56eb4345d9e95b85474186b49f1f546a70c5d76693e9e7dd50be9937a9950e` | 18,801 |
| `src/ior_mvp/acquisition/entities/normalisation.py` | `1532cb41699f588485d47b3a5c8f19842ed025a33c2d797e87d10bfeae8c7365` | 4,533 |
| `src/ior_mvp/acquisition/entities/resolver.py` | `d125c77c56772ff36fdabdc1c1e994c5152443c743545f7f698910ab4999a270` | 32,726 |
| `src/ior_mvp/acquisition/entities/rules.py` | `09fc0281de261871d6c9a59666a7d3612a25c7385a0d25fcaeb3e79b835316fb` | 11,902 |
| `src/ior_mvp/acquisition/entities/store.py` | `de3328550209d6ea0bb9c869858f7453c024221b5061e5e50714a0b364182adb` | 27,160 |
| `src/ior_mvp/acquisition/repository.py` | `46db20bd989fd6d5353ad0259f3c1cdcd7f66d2df15f0764c6f4fcc332d30032` | 6,435 |
| `tests/acquisition_doubles.py` | `38ee81ef10c94c5dfffffb904b35445a7736957e4fe87c24324cb7c4b087cb71` | 14,828 |
| `tests/test_entity_ids.py` | `5375ebdd1c32f492dfe68a2a02eac7d577ff6acbc4712de9d884ab6d7c7ae039` | 2,235 |
| `tests/test_entity_mentions.py` | `500ee974e89888e53ec684c0d28506faa9086ec6fbb7f37dc4dffd2798403a14` | 8,222 |
| `tests/test_entity_normalisation.py` | `acb7a25db731458f4fb3a1553ed7ee6a0bf35cd30eca01141ef85b2c7525283a` | 5,508 |
| `tests/test_entity_resolution_artifact.py` | `531b6383c67393c0c08e4866262224637fa74086bef9ca9b22719cd3b493f8e5` | 6,678 |
| `tests/test_entity_resolution_boundaries.py` | `cc1e846c3c92070bbf1bba8152175393ca1b2a1bb65c572026ca84272a737eff` | 4,393 |
| `tests/test_entity_resolution_builder.py` | `fdfec20882576f1513745bfc4c918db58f1852287237c9317c2a49a5b33397f6` | 19,159 |
| `tests/test_entity_resolution_cli.py` | `9bc9e19bc87874a7d297e2b28311466bb9d81f8743dcbaf59a4ad435b2e062f6` | 12,111 |
| `tests/test_integrity_contract.py` | `7b053436ea0ba3bbf0210e59e731c2c16dcee650af8adcec2d0bf210b10eba54` | 27,322 |

Changed-file set versus approved plan: exact match — 38 actual, 38 expected, no unexpected paths, no missing paths. `git diff --check` passed. `.autonomous-workflow/**` is unchanged and the Git index is empty.

## Real artifact summary

- Entities: COMPANY 5; PLANT 2; LINE 0; LICENCE_HOLDER 0.
- Mention links: exact 27; pending 3; unresolved 8; deterministic identifier 0.
- Pending: M-009 `LOCALITY_VARIANT`, M-017 `SUBJECT_OUTSIDE_WINDOW`, M-020 `VARIANT_NAME_EQUALITY`.
- Unresolved: M-007 count-only; M-021…M-027 out-of-scope SASO.
- Passport links: exact 10; unresolved 8 (two no-mention verification statements and six out-of-scope SASO passports).
- Producer observation links: exact 5.
- Ownership: one 2004 `OWNERSHIP_CHANGE`, owner unnamed/unresolved, citations M-004 and M-012.
- Documents without mentions: `DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0`, `DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a`.

## Stop conditions and Muhasib audit

No stop condition remains. The initial T0 bytecode stop was resolved by the owner lead's stated relocation and [6]/[5] re-verification. Scope equals plan; real spans reverify; protected bytes pass after CI; no network or `.env` access; one manifest run only; index empty; no commit/stage/push/stash/reset/checkout. This is implementation evidence awaiting independent review, not approval or delivery.
