# Test evidence — S14a case selection, evidence and families

## 2026-09-12T23:01:49Z — T0 baseline

Environment: `UV_OFFLINE=1`, `PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc`, `PATH=.venv/bin:$PATH`, `PYTHONPATH=src`.

```text
BRANCH_OK
?? .workflow/slices/S14-deep-cases-a/
INDEX_EMPTY_PASS
```

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

```text
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

## 2026-09-13T02:35:00Z — OD-21 CI test correction

Scratch RED at committed candidate HEAD `13eeea1`: `2 failed`. The Make test
executed the guarded target under `CI=1` and correctly hit `CI may not acquire`;
the history test compared retained 1.3.0 bytes to candidate HEAD's 1.4.0 file.

Retained config SHA-256:
`fbe061496bc6c9b5ddd039b25536d78fb24c22ba3d84650fcd2c9374977673cc`.
The retained bytes equal
`git show ab6211f86307ad95a0e61f0597664023f09b7177:config/acquisition_sources.v1.yaml`
byte-for-byte and parse with `metadata.version == "1.3.0"`.

GREEN commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_cli.py::test_make_acquire_partners_quotes_variant_ampersand_for_cli_contract_and_url tests/test_acquisition_config.py::test_1_3_0_history_copy_is_byte_identical_to_superseded_config
git diff -- tests/test_acquisition_cli.py tests/test_acquisition_config.py | git -C /tmp/ior-s14a-scratch apply
git -C /tmp/ior-s14a-scratch add tests/test_acquisition_cli.py tests/test_acquisition_config.py
git -C /tmp/ior-s14a-scratch commit -q -m 'test: make S14a checks CI-stable'
(cd /tmp/ior-s14a-scratch && CI=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=/home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_cli.py::test_make_acquire_partners_quotes_variant_ampersand_for_cli_contract_and_url tests/test_acquisition_config.py::test_1_3_0_history_copy_is_byte_identical_to_superseded_config)
```

GREEN locally: `2 passed in 0.12s`. GREEN in the committed scratch clone with
`CI=1`: `2 passed in 0.16s`.

Full suite: `2416 passed, 1 warning`.

Final commands recorded before execution:

```bash
git diff --cached --quiet && echo INDEX_EMPTY_PASS
git diff --check && echo DIFF_CHECK_PASS
git diff --name-only 13eeea1 -- .
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Canonical identity against base 13eeea1; exclude both S14 record folders,
# .autonomous-workflow and ignored roots; print identity, count and file list.
PY
```

```text
INDEX_EMPTY_PASS
DIFF_CHECK_PASS
CANDIDATE_IDENTITY 38e1fed5c512756635435c3ec372dd04b615d76562745d63e0ec2790c6856ead
CANDIDATE_FILE_COUNT 2
CANDIDATE_FILE tests/test_acquisition_cli.py
CANDIDATE_FILE tests/test_acquisition_config.py
```

Muhasib: verified the hosted failure log, committed scratch RED, retained-file
hash/base equality, local and committed-scratch GREEN, full pytest, exact
two-file scope, empty index and canonical trailing-LF identity. No network,
`.env`, product/config/data/Core/manifest edit, repository commit/stage/push,
or CI-guard bypass occurred. The remaining HEAD usages were inspected and are
synthetic-repository frozen-tree mechanics, not dependencies on slice-changed
file content.

## 2026-09-13T02:05:00Z — AM-3 RED/GREEN command record

The following command was recorded before execution. It covers the T-26
through T-39 doubles/stored-unit gate and must be GREEN before W-C V3:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_connectors.py tests/test_case_brief.py tests/test_case_projection.py
```

RED: `11 failed, 372 passed in 11.13s`.

GREEN: `383 passed in 11.28s`.

The executed behavior includes Decimal-from-raw-text reconciliation,
half-unit tolerance, positive-reference zero refusal, World reconciliation,
vacuous uniqueness for absent descriptions, duplicate-name refusal, exact
typed-reason mapping, V1 coverage immutability, typed-reason evidence
validation, and OBSERVED-only superseded-attempt wording.

## 2026-09-13T02:28:00Z — AM-3 window stop evidence

The recorded acquisition command was passed through the existing Make recipe,
which did not shell-quote the ampersand in
`partner_dimension_query=&includeDesc=true`. Captured stdout ended at the
recipe line. The stored contract proves the data request omitted includeDesc
and retained parameters `partner_dimension_query=""`; therefore it was a
repeated V1 request, not V3. The unit is
`e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184/20260913T014942Z`:
HTTP 200, 7,320 bytes, requests_made 2 (TERMS + data), 8 rows / 7 non-World,
descriptions absent, Decimal sum/reference 71149266.221, difference 0.000,
tolerance 0.0035, coverage INCOMPLETE /
PARTNER_DESCRIPTIONS_UNAVAILABLE.

SC-13 closed the window after that one data request. No retry or corrected V3
was attempted. V1 coverage from `20260913T010452Z` remains byte-identical at
`faa48dee5d066d9f26e6df4ec8f5973ed87ad672b5c728e62e6a429608351dc4`.
Because V3 did not execute, there is no third manifest run.

Stopped-candidate identity:

```text
CANDIDATE_IDENTITY 0868e32720f2ecf33e2332d3b7e081ee294c856bd632c1278349fb997f5fb4f6
CANDIDATE_FILE_COUNT 147
CANDIDATE_SERIALIZATION compact-sort_keys-trailing-LF
BASE ab6211f86307ad95a0e61f0597664023f09b7177
```

Full `pytest -q`, `make ci`, portability, T-40 through T-44, governed-text
updates and Case C manifest work were not run after this binding stop; no
passing claim is made for them.

## 2026-09-13T02:18:00Z — OD-18 corrected V3 evidence

Quoting test: RED `1 failed` with captured
`partner_dimension_query=`; GREEN `1 passed` after Make quoted
`"$(PARAMETERS)"`.

Corrected V3: query `050a03afdc48…`, run `20260913T015620Z`, HTTP 200,
8,425 bytes, 2 requests, COMPLETE. Eight rows include seven non-World rows;
all seven descriptions are present and unique. Decimal S and R are both
71149266.221, difference 0.000, tolerance 0.0035; values match V1. Snapshot
`PARTNERS-SAU-UN-COMTRADE-2026-09-13` was built.

Post-observation commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_briefs_real.py tests/test_case_projection.py tests/test_acquisition_snapshots.py tests/test_acquisition_connectors.py tests/test_acquisition_cli.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make validate-briefs
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make cases-reconstruct
```

Focused result: `122 passed`; all five briefs valid; case reconstruction
`PASS (0 snapshots, 5 briefs)`. 721061 engine proof:
`INVESTIGATE / null / ROUTE_CHANGING_EVIDENCE_UNRESOLVED`, fired
`R0,R1-D,R3,R10,R12`. The defective repeat passport says
`VARIANT_NOT_TRANSMITTED`; original V1 and WITS passports are superseded.

Manifest Case C receipt: `2026-09-13T02:28:00Z`; third and last invocation.
Generator and integrity exited 0. Immediate oracle initially had a read-only
authority-list parser error, then passed without rerunning the generator:
`PREEXISTING_ROWS_UNCHANGED_PASS 535`,
`AUTHORITY_PATH_SET_UNCHANGED_PASS 19`, `MANIFEST_ROWS_AFTER 628`.

Final gate commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make ci
rm -rf /tmp/ior-portability && cp -a . /tmp/ior-portability
(cd /tmp/ior-portability && UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py && UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all)
```

Full pytest: `2416 passed, 1 warning in 35.15s`.

Portability: integrity PASS; case 0/5, acquired 4/34, documents 20/20,
entities 2/44, screening 1; `PORTABILITY_AM3_PASS`.

`make ci` exit 0: 2416 pytest tests; smoke/frozen outcomes PASS; 152 functional
browser tests and 4 visual browser tests PASS.

Final identity/invariant commands recorded before execution:

```bash
git diff --cached --quiet && echo INDEX_EMPTY_PASS
git diff --check && echo DIFF_CHECK_PASS
git diff --quiet ab6211f86307ad95a0e61f0597664023f09b7177 -- .autonomous-workflow && echo AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
sha256sum data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-12.json data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Canonical IAC-6 identity over git-status files against base ab6211f;
# exclude .autonomous-workflow, ignored trees and both S14 record folders;
# compact sorted JSON plus trailing LF.
PY
```

Final results:

```text
INDEX_EMPTY_PASS
DIFF_CHECK_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
FROZEN_ROOTS_AND_TOP_LEVEL_PASS
CANDIDATE_IDENTITY 78c9b0c6c0085cdc89e303d159a56041b5923fd720b64637ff6829c5009fc6cb
CANDIDATE_FILE_COUNT 153
CANDIDATE_SERIALIZATION compact-sort_keys-trailing-LF
```

WITS snapshot hashes remain
`0a5a564594ecdb35ad129f7c111e3e5f62ba6d152fac275cea6d0ecc0e08dc63`
and
`cdcc904af656b8d1ba02f6dd23593071cddcf21739e58290d4cf197e6723657f`.
IDE diagnostics report no errors in the edited implementation/tests.

Muhasib self-audit:

- Verified from executed output and stored bytes: quoting RED/GREEN; corrected
  V3 URL/contract; request count/status/bytes; seven verbatim descriptions;
  Decimal reconciliation; COMPLETE snapshot selection and superseded runs;
  brief validation and passport markers; honest INVESTIGATE/null engine result
  with computed R3; third manifest receipt/oracle; full pytest, CI,
  portability, frozen roots, WITS hashes, empty index and canonical identity.
- Assumed/authority-sourced: `includeDesc` is an officially documented
  parameter is OD-16's statement; the official parameter table remains
  unobserved. Publisher data may change after retrieval; stored hashes govern.
- No self-approval, commit, stage, PR, merge, fourth manifest run or further
  network request is claimed.

## 2026-09-13T00:37:00Z — T9/T10 final evidence

### Manifest receipt

```text
MANIFEST_RUN_STARTED_UTC 2026-09-13T00:25:27Z
MANIFEST_RUN_FINISHED_UTC 2026-09-13T00:25:27Z
INTEGRITY PASS
MANIFEST_ORACLE_PASS
SNAPSHOT_ROWS_AFTER 607 ADDED 72 PREEXISTING_CHANGED 0
AUTHORITY_ROWS_AFTER 19 CHANGED config/acquisition_sources.v1.yaml config/product_families.v1.yaml docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/04_CANONICAL_DATA_MODEL.md docs/core/05_DATA_SOURCES_AND_INGESTION.md docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
```

Rows before: snapshot `535`, authority `19`. Exactly one
`scripts/build_manifests.py` invocation ran. The first immediate
integrity-contract run exposed two test-only partition-prefix omissions for
the new manifested roots; generated rows, integrity and the row-level oracle
were correct. After adding positive and sibling-prefix-negative test probes,
without a second generator run:

```text
INTEGRITY PASS
25 passed in 0.89s
```

### Final deterministic selection

```text
CASE SELECTION PASS (5 selected; 3 profiles; 4 families)
coated_steel: 721061, 721012 (runner-up 721069; 5 substitutes; 3 viability exclusions; 0 identity exclusions; 1 frozen exclusions)
fabricated_aluminium: 760711, 760429 (runner-up 761610; 22 substitutes; 4 viability exclusions; 0 identity exclusions; 0 frozen exclusions)
technical_plastics: 392010 (runner-up 391739; 36 substitutes; 0 viability exclusions; 1 identity exclusions; 1 frozen exclusions)
selection_sha256=19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016
```

Input hashes: screening `231b8c3c999f3b69fea9c45d38c2dfc93d1a1e9faccef0e735658aa4adab06cc`;
universe `758acdb41c5759e5be2c6215405e9c6829bc527b73850d8c4b54327c61b0c78d`;
product families `62fa9c2944474ffbc5952801ba676a2adf750870a88969c59e22337b4564446b`;
terms `27b97683ab41c75dc90ce9224db9f561d9c5f62ddc27fa581444f39e1b3f918f`;
identity exclusions `5e18dd7a5573610d6d02909cf9f6e792646de61650d1a6d7c5eb37a9308941c6`;
referenced documents `45be1d0e99460c9648c114f5dc8c4e1156759fedce52cd7893940f508d419023`.

### Operator-window outcomes

| Window/source | Actual requests | RunReport aggregate | Unit status | Stored response bytes |
|---|---:|---:|---|---:|
| W-A / WCO | 4 | 9 | 3 COMPLETE documents; terms captured | 695,398 |
| W-A / Hadeed | 1 | 1 | 1 COMPLETE document | 4,314,057 |
| W-A / ALUPCO | 1 | 1 | 1 COMPLETE document | 57,196 |
| W-A / TALCO | 1 | 1 | 1 COMPLETE document | 166,206 |
| W-A / Ma'aden | 3 | 5 | 2 COMPLETE documents; terms captured | 11,021,570 |
| W-T / Tasnee + SPIMACO | 2 | n/a | both UNAVAILABLE: `CERTIFICATE_VERIFY_FAILED`; no bypass/retry | 0 |
| W-P / WITS | 6 | 20 | 4 normalized; 721061 `FORMAT_NOT_PARSEABLE` after HTTP-200 `Error.aspx` | 227,389 |

RunReport aggregates retain KL-65 cumulative counting; actual requests equal
the recorded budgets. Compressed raw store: 41,673,354 bytes; largest artifact:
9,837,279 bytes.

DocumentRecords acquired:

- WCO: `DOC-WCO-HS-NOMENCLATURE-53d6f01ac062-0926bf9934da`,
  `DOC-WCO-HS-NOMENCLATURE-5530bdf97060-8da42b5156a2`,
  `DOC-WCO-HS-NOMENCLATURE-69bd7323c7aa-bd350605a78a`.
- Hadeed: `DOC-PRODUCER-HADEED-92ca24b2076f-253eed8b773e`.
- ALUPCO: `DOC-PRODUCER-ALUPCO-135870d0e4c7-0261d54ca8a6`.
- TALCO:
  `DOC-PRODUCER-ALTAISEER-TALCO-b68e0eef2440-b339b1ac8d87`.
- Ma'aden: `DOC-PRODUCER-MAADEN-b1dd369ea0fe-dae44e050e70`,
  `DOC-PRODUCER-MAADEN-a48b1f95cba9-956b9a16c655`.

### Brief and engine proof

```text
SAU-H6-392010 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R4-D,R12
SAU-H6-721012 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R4-D,R12
SAU-H6-721061 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R12
SAU-H6-760429 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R3,R4-D,R5,R9-S,R10,R12
SAU-H6-760711 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R12
```

Temporary PublicSnapshot SHA-256 values:

```text
056b693e15675e68123fb10cc4b5581415fc04ea80c0a16954744e07aaf68d1b  PUBLIC-SAU-H6-392010-2026-09-12.json
8e999b08a2086c5807a14a8732d6aed8ec214f1a3ce40e98a19437789a814999  PUBLIC-SAU-H6-721012-2026-09-12.json
93f7f713d637fc1f1daae11fd26a8305bdebbdceed4418e06df0498728022fc7  PUBLIC-SAU-H6-721061-2026-09-12.json
eddb302dc1e70b0231d940cee5cb670871c5533663a43beea4209a234803e3d2  PUBLIC-SAU-H6-760429-2026-09-12.json
669fc1b117782ae16c5eec090989837f21e77602b0bbf441207f7e67158d294a  PUBLIC-SAU-H6-760711-2026-09-12.json
```

### Release gates

```text
2373 passed, 1 warning in 32.86s
```

```text
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (3 snapshots, 32 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

## 2026-09-13T00:53:00Z — correction-round identity receipt

The original IAC-6 identity line above is retained as executed, but its
serialization omitted the recipe-required trailing LF. For the same 127-file
candidate tree, the corrected canonical serialization is:

```python
json.dumps(
    {"base": base, "files": files},
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
) + "\n"
```

```text
CANDIDATE_FILE_COUNT 127
CANDIDATE_IDENTITY 9c93643388cdb4dc99ca16ceeaa9ede5d0ce22a460ed139eaa0bc905c5531acd
```

Source: OD-14 records both the original no-LF identity and the
recipe-conformant trailing-LF identity for the same tree. All correction-round
identities use this canonical serialization.

## 2026-09-13T01:25:00Z — AM-2 pre-manifest verification

Commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_brief.py tests/test_case_projection.py \
  tests/test_case_briefs_real.py tests/test_acquisition_connectors.py \
  tests/test_acquisition_config.py tests/test_acquisition_cli.py \
  tests/test_acquisition_snapshots.py tests/test_acquisition_stored_artifacts.py
PYTHONPATH=src pytest -q tests/test_integrity_contract.py::test_s14a_core_v2_case_contracts
PYTHONPATH=src pytest -q
```

Focused AM-2 suite: `547 passed in 20.82s`.

Pre-manifest full suite: `2398 passed, 2 failed, 1 warning`. One failure was
the expected stale raw manifest for the two W-C payloads; the other was an
S13a exact-table-text test, updated to preserve its universe assertions while
pinning the new truthful W-C status. Final pre-generation commands recorded
before execution:

```bash
PYTHONPATH=src pytest -q \
  --deselect tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  data/snapshots/public data/synthetic data/golden browser_tests \
  ':(glob)src/ior_mvp/*.py')"
rg -n '/home/|/tmp/' config/acquisition_sources.v1.yaml data/cases \
  docs/core/04_CANONICAL_DATA_MODEL.md \
  docs/core/05_DATA_SOURCES_AND_INGESTION.md \
  docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md \
  docs/ARCHITECTURE_DECISIONS.md docs/KNOWN_LIMITATIONS.md
```

Result: `2399 passed, 1 deselected, 1 warning`;
`PRE_MANIFEST_PROTECTED_PASS`. The broad absolute-path scan matched the
pre-existing ADR cache example `/tmp/.cache` and the URL path
`https://saber.sa/home/aboutsaber`, neither an authored filesystem path.
Replacement added-line-only command recorded before execution:

```bash
git diff -U0 ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  config/acquisition_sources.v1.yaml data/cases docs/core \
  docs/ARCHITECTURE_DECISIONS.md docs/KNOWN_LIMITATIONS.md |
  rg '^\+.*(/home/|/tmp/)'
```

Expected: no match / ripgrep exit 1.

Result: `ADDED_ABSOLUTE_PATH_SCAN_PASS`.

### Second and final manifest invocation — commands recorded before execution

Case B applies. ADR-021 already contains both run receipts and reasons. The
following is the only further `build_manifests.py` invocation and the second
and last in S14a:

```bash
printf 'MANIFEST_RUN_STARTED_UTC %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PYTHONPATH=src python3 scripts/build_manifests.py
printf 'MANIFEST_RUN_FINISHED_UTC %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src python3 - <<'PY'
# Compare generated manifests to `git show ab6211f:...`: every base snapshot
# row exact; authority path set exact; print before/after row counts and changed
# authority paths.
PY
```

Any failure triggers SC-7; no third invocation is authorized.

Second/final manifest result:

```text
MANIFEST_RUN_STARTED_UTC 2026-09-13T01:15:40Z
MANIFEST_RUN_FINISHED_UTC 2026-09-13T01:15:40Z
INTEGRITY PASS
MANIFEST_ORACLE_PASS
SNAPSHOT_ROWS 535 -> 616 ADDED 81 PREEXISTING_CHANGED 0
AUTHORITY_ROWS 19 -> 19 PATH_SET_UNCHANGED True
AUTHORITY_CHANGED_PATHS ["config/acquisition_sources.v1.yaml", "config/product_families.v1.yaml", "docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md", "docs/core/04_CANONICAL_DATA_MODEL.md", "docs/core/05_DATA_SOURCES_AND_INGESTION.md", "docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"]
```

ADR-021's pre-invocation authorization receipt was written at
`2026-09-13T01:13:59Z` so its own bytes entered this run; the actual generator
start/finish receipt above is authoritative execution evidence. Run count is
exactly two for S14a and authorization is exhausted.

## Final correction-round gates — commands recorded before execution

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
PYTHONPATH=src python3 scripts/demo_smoke.py
PYTHONPATH=src python3 scripts/check_threshold_literals.py
sha256sum data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-12.json \
  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json
```

```bash
make ci
```

```bash
rm -rf /tmp/ior-portability-am2
cp -a . /tmp/ior-portability-am2
(cd /tmp/ior-portability-am2 &&
  UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-am2-pyc \
  PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py &&
  UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-am2-pyc \
  PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all)
echo PORTABILITY_AM2_PASS
```

Protected-byte, selection, credential-name, staged-index and canonical
trailing-LF identity commands are recorded after these gates and before their
execution.

Completed offline results:

```text
2400 passed, 1 warning in 35.11s
INTEGRITY PASS
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (3 snapshots, 32 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
THRESHOLD LITERAL SCAN PASS (78 Python files; 23 configured numeric values)
0a5a564594ecdb35ad129f7c111e3e5f62ba6d152fac275cea6d0ecc0e08dc63  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-12.json
cdcc904af656b8d1ba02f6dd23593071cddcf21739e58290d4cf197e6723657f  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json
PORTABILITY_AM2_PASS
```

The reconstruction emitted the pre-existing PDF extraction warnings recorded
by KL-63/KL-66; every reconstruction terminal line passed.

`make ci` exited 0 in 402.018 seconds. Tail:

```text
2400 passed, 1 warning in 33.87s
SMOKE PASS
152 passed, 4 deselected in 256.02s (0:04:16)
4 passed, 152 deselected in 46.78s
```

### Final invariants and canonical identity — commands recorded before execution

```bash
git diff --cached --quiet
git diff --check
git diff --quiet ab6211f86307ad95a0e61f0597664023f09b7177 -- .autonomous-workflow
PYTHONPATH=src python3 -c "import json; json.load(open('.workflow/state.json')); print('STATE_JSON_VALID_PASS')"
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- <protected-set>)"
sha256sum data/cases/selection/CASE-SELECTION-S14-*.json
rg -n '392190|RESIDUAL_CATCH_ALL_SUBHEADING' \
  data/cases/selection/hs6-identity-exclusions-v1.json \
  data/cases/selection/CASE-SELECTION-S14-*.json
rg -il "ocp-$(printf apim)-subscription-key" data/raw/un_comtrade data/snapshots \
  data/cases .workflow/slices/S14-deep-cases-a docs
```

```bash
PYTHONPATH=src python3 - <<'PY'
# Parse git status --porcelain=v1 -z; exclude
# .workflow/slices/S14-deep-cases-a/,
# .workflow/slices/S14b-deep-case-portfolio/, .autonomous-workflow/,
# .artifacts/ and .venv/; hash remaining present files; sort by path; serialize
# json.dumps({"base": base, "files": files}, sort_keys=True,
# separators=(",",":"), ensure_ascii=False) + "\n"; SHA-256 those bytes.
PY
```

No non-record file is edited after this identity.

The first final-invariant command used the wrong exclusion-table basename and
stopped before identity; the corrected path is
`data/cases/selection/identity-exclusions-v1.json`. A subsequent header-name
scan initially found only this evidence record's literal search pattern; the
pattern was split without changing its semantics and rerun.

Final results:

```text
INDEX_EMPTY_PASS
DIFF_CHECK_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
STATE_JSON_VALID_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016  data/cases/selection/CASE-SELECTION-S14-250cd516de0a.json
identity-exclusions-v1.json: 392190 / RESIDUAL_CATCH_ALL_SUBHEADING
CREDENTIAL_HEADER_NAME_SCAN_PASS
CANDIDATE_IDENTITY baf0b4dd4bab1316804a90e7e5a5017c6c71337fbacc5fd1b07bc550022eafb5
CANDIDATE_FILE_COUNT 141
CANDIDATE_SERIALIZATION compact-sort_keys-trailing-LF
```

Candidate is uncommitted and unstaged.

### Correction-round stop conditions and muhasib

- No AM-2 SC-11/SC-12 or inherited correction-round stop triggered.
- W-C ended under AM-2 C-5 branch (iii):
  `INCOMPLETE / COVERAGE_INDETERMINATE`; V2 was prohibited by the observed
  predicate result. This is the required honest termination, not a bypass.
- Earlier W-T verified-TLS source stops remain recorded unchanged.
- Verified: immutable W-C contracts and coverage; count 8 / 7 non-World /
  null descriptions; five brief tri-states and passports; five engine proofs;
  T-12; manifest base-row/path-set oracle; selection/exclusion and WITS hashes;
  final pytest, `make ci`, portability, protected-set, header-name, index and
  identity outputs.
- Assumed/interpreted for independent review: the owner's explicit OBSERVED
  WITS counts 42/12/43/27 govern those immutable H0-labelled partner rows,
  while H6 is enforced on the Comtrade substitution; ADR-021's
  `01:13:59Z` is the pre-invocation authorization-record time and
  `01:15:40Z` is the actual generator execution receipt.
- No self-approval, commit, PR, hosted CI or merge is claimed.

Muhasabah gate: PASS for an uncommitted correction candidate handoff, subject
to independent implementation review.

```text
RUNTIME_IMPORT_BOUNDARY_OK
PROTECTED_SET_BYTE_IDENTICAL_PASS
VISUAL_MANIFEST_OK 56
FROZEN_OUTCOMES_OK
PORTABLE_TEXT_PASS
PORTABILITY_PASS
```

`make ci` exit `0` tail:

```text
2373 passed, 1 warning in 32.64s
SMOKE PASS
152 passed, 4 deselected in 259.43s (0:04:19)
4 passed, 152 deselected in 44.77s
```

### IAC-6 compact candidate identity

- Base: `ab6211f86307ad95a0e61f0597664023f09b7177`.
- Excluded: both S14 slice-record folders and ignored trees.
- Payload keys: exactly `{"base","files"}`.
- File rows: `{bytes,path,sha256}`, path-sorted; deleted paths would use
  `sha256:null` (none).
- Serialization: `json.dumps(payload, ensure_ascii=False, sort_keys=True,
  separators=(",",":"))`, no trailing newline.
- `CANDIDATE_FILE_COUNT 127`.
- `CANDIDATE_IDENTITY 08f5f78395e5b99db55ba0ae9a6de36aff4d6f0b60b606dd1fa926b25fec04bb`.

```text
INDEX_EMPTY_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
STATE_JSON_VALID_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
```

Candidate remains unstaged and uncommitted.

### Stop conditions and muhasib self-audit

- SC-5 triggered at source level for Tasnee and SPIMACO: one verified-TLS
  request each failed; both were recorded `UNAVAILABLE`; no bypass or retry.
- SC-1, SC-2a, SC-2b, SC-3, SC-4, SC-6, SC-7, SC-8, SC-9 and SC-10 did not
  trigger. The immediate post-generator test-prefix failures required test-only
  corrections; no config/Core/data change or second generator invocation was
  made.
- One disclosed process deviation: the WCO index was read twice because the
  first bounded parser emitted no chapter hrefs. The second consultation was
  parameterized and logged before execution; it did not bypass a wall or guess
  a URL.

Verified:

- authority precedence and OD-11 data-row implementation against the approved
  plan/reviews;
- all changed product files, governed data records, control records and final
  diff scope; only the two authorized live config YAMLs changed;
- exact retained-config hashes, selection input/output hashes, stored page
  contracts, DocumentRecord spans, entity artifact, brief builds and engine
  outputs;
- exactly one manifest invocation, unchanged pre-existing snapshot rows,
  unchanged authority path set and exact six authority-row changes;
- full pytest, integrity, scenario, smoke, reconstruction, prohibited/threshold
  scans, runtime import boundary, frozen outcomes, protected paths, visual
  manifest, portability copy and `make ci` by actual exit-zero output;
- no `.env` read, no Git-state mutation, no Rajhi request, no TLS bypass and no
  staged file.

Assumed/open:

- WCO Class B and `TARGET_PRODUCT_IDENTITY`-only treatment is the binding
  owner/reviewer ruling, not independent legal advice on redistribution.
- Arabic commercial names are analyst translations and remain explicitly
  labelled as such.
- The 760429 core-process state 0 is a bounded interpretation of cited ALUPCO
  and TALCO extrusion/profile spans; every alloy, geometry, finishing,
  qualification, capacity and application gate remains unknown.
- Live publishers may change after retrieval; the stored hashes, not current
  pages, govern this candidate.
- No independent implementation approval, PR, hosted CI or merge is claimed.
  The next authorized role is the supervisor review followed by
  `reviewer-grok`.

Muhasabah gate: PASS for an uncommitted implementation handoff, not an approval.

The reconstruction command exited `0`. Existing `pypdf` warnings about rotated text, malformed CMaps, and the recorded HTTP-wrapped publisher PDF were emitted before the PASS lines; these match KL-63/KL-66 and were not suppressed.

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

```text
SCENARIO VALIDATION PASS (2 scenarios)
```

Both scenario reports completed with `ground_truth_backtest: PASS`.

```text
2275 tests collected in 1.34s
VISUAL_MANIFEST_OK 56
```

Frozen tree OIDs:

```text
data/snapshots/public 2ad27d6eaa9b3ce474f2c9ed62ecaa873ecd5e04
data/synthetic 3fb2247a36b57b85fc0f966717aad5502aa25f4b
data/golden 72618db654110823ec7a8d4dd6415a37e4554e33
browser_tests/baselines c2b3b66bbc6afaefe6e951772984d567cac53522
```

## 2026-09-13T00:20:37Z — T1 through T8

- Selection RED: 13 missing-package failures. Doubles GREEN: 12 passed; CLI
  RED/GREEN: 1 failed then 1 passed; final real selection suite: 14 passed.
- Final ruled selection:
  - coated steel 721061/721012; runner-up 721069;
  - fabricated aluminium 760711/760429; runner-up 761610;
  - technical plastics 392010; runner-up 391739; 392190 identity-excluded.
  - Record `CASE-SELECTION-S14-250cd516de0a.json`, SHA-256
    `19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016`.
- Family/history RED: 12 failed / 7 passed; GREEN: 19 passed. Exact history
  hashes: product families `841bc5ac…`; acquisition sources `fbe06149…`.
- Acquisition contracts RED: 263 failed / 53 passed; GREEN: 316 passed.
- T4 W-A: eight COMPLETE DocumentRecords; W-T: Tasnee/SPIMACO verified-TLS
  failures retained; W-P: four normalized selected HS6 and one
  `FORMAT_NOT_PARSEABLE` exclusion; partner snapshot built.
- Partner/history regression RED: 2 failed; GREEN: 2 passed. Existing
  latest-selection diagnostics are retained; release reconstruction is pinned
  to each snapshot's stored run ids.
- T5 entity RED: missing list, then two fail-closed invalid-link attempts before
  any artifact write. Final GREEN: artifact
  `ENTITIES-2026-09-13-bebc9d15cbf1`, 4 companies / 1 plant / 6 links; focused
  test 1 passed.
- T6 RED: 25 failed / 1 passed. Unit GREEN: 21 passed. Real engine proof:
  392010, 721012, 721061, 760429 and 760711 all compute
  `INVESTIGATE`, route null, `ROUTE_CHANGING_EVIDENCE_UNRESOLVED`; real suite
  4 passed; complete T6 suite 30 passed.
- T7 RED: 2 failed; GREEN: 2 passed. `make validate-briefs` validated five and
  `make cases-reconstruct` printed
  `CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)`.
- T8 Core RED: 1 failed; GREEN: 1 passed. State JSON valid and four focused
  governance contracts passed.
- Broad pre-manifest regression first found 19 compatibility/stale-manifest
  failures. After corrections, with only the expected pre-manifest raw
  inventory assertion deselected:

```text
2347 passed, 1 deselected, 1 warning in 31.82s
```

The warning is the existing Starlette/httpx deprecation warning.

Pre-manifest reconstruction:

```text
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (3 snapshots, 32 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

