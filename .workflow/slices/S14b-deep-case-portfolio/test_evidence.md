# S14b test evidence

## 2026-09-13T01:54:00Z — T0 baseline

Environment on every Python command:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc
UV_OFFLINE=1
PATH=.venv/bin:$PATH
PYTHONPATH=src
```

Observed:

- branch/base oracle: `BRANCH_OK`;
- integrity: `INTEGRITY PASS`;
- reconstruction: public `2 snapshots, 20 artifacts`; documents
  `12 records, 12 artifacts`; entities `1 artifacts, 38 links`; screening
  `1 snapshots`;
- smoke: `SMOKE PASS`, including the two frozen public outcomes;
- scenarios: `SCENARIO VALIDATION PASS (2 scenarios)`, both back-tests PASS;
- pytest collection: `2275 tests collected`;
- visual manifest: `VISUAL_MANIFEST_OK 56`;
- frozen tree OIDs exactly match plan BF-2;
- five provisional PublicSnapshot 2.1.0 builds completed under `/tmp`.

The reconstruction command emitted the already-recorded pypdf warnings for
rotated/irregular publisher PDFs, then exited 0 with all four PASS lines.

These are baseline observations only. Independent review, integration,
authority regeneration, hosted CI, PR, and merge are not claimed.

## 2026-09-13T02:00:00Z — T1–T4 preparation RED/GREEN

- T1 dry run: five Gate B reports PASS; five planted-truth back-tests match;
  five public fingerprints unchanged; every designed numeric pin equals the
  computed value; `DRY_RUN_FAILURES 0`.
- T1 portfolio RED before T4b: `42 failed, 5 passed`; snapshot-dependent
  nodes report `integration snapshot is pending`; the zero-state double
  exposed the absent state-specific R3 code.
- T2 frozen goldens: `4 passed, 10 deselected`.
- T2 new goldens: `10 failed`, each `Unknown opportunity: SAU-H6-*`.
- T2 scenario/API contracts: `3 failed`; five scenarios report no matching
  public case and the portfolio count is 2 instead of 7.
- Frozen prefix: `GOLDEN_FIRST_119_LINES_BYTE_IDENTICAL_PASS`.
- T3 collection: `332/336 tests collected (4 deselected)`.
- T3 browser RED: 30 nodes failed on the common expected boundary
  `Locator expected count 7; actual value 2`.
- T4 code oracle: `_expected_matrix()` is 76.
- T4 visual RED: `visual baseline matrix is incomplete`; four visual nodes
  report that exact setup error. No regeneration occurred.

## 2026-09-13T02:24:00Z — T4b RED/GREEN

Initial focused run:

```text
19 failed, 3 passed, 1 warning in 0.92s
```

Focused post-implementation run:

```text
21 passed, 1 warning in 0.90s
```

Complete T4b component suites:

```text
11 failed, 270 passed, 1 warning in 3.31s
```

The 11 failures are integration-only: the seven-case API count and ten new
goldens. All PublicSnapshot, trade-metric, rule, catalogue, GenUI, dossier,
static and ES-module tests pass.

Additional checks:

```text
11 passed, 1 warning in 1.22s
```

This confirms source-derived authority 1.3.0, the additive no-candidate
payload fixture, and the 32-test browser inventory.

```text
THRESHOLD LITERAL SCAN PASS (71 Python files; 23 configured numeric values)
ES MODULE CHECK PASS (27 files)
decision.js 124 lines
```

The warning is the pre-existing Starlette/httpx deprecation warning.

The `_scaled` six-decimal reconciliation test is authored and intentionally
RED because `src/ior_mvp/cases/projection.py` is supplied only by the pending
s14a merge. T-23 is intentionally RED because the merged Core 04 §12 does not
exist at the preparation base and Core 04/07 edits are deferred across the
approved integration seam.

## 2026-09-13T02:38:00Z — final preparation verification

The final read-only provisional refresh observed 721061 as
`PARTNER_DETAIL_OBSERVED` with seven rows. Re-running all five scenarios gave
Gate B PASS ×5, back-test match ×5, public fingerprint unchanged ×5 and
`DRY_RUN_FAILURES 0`. The only planned sensitivity was 721061 support signals
`[R8] → [R3,R8]`; its designed/computed outcome remains ADVANCE route 3 with
all numeric pins unchanged.

Fresh full worktree pytest:

```text
108 failed, 2294 passed, 1 warning in 42.78s
```

All 108 failures are preparation-state oracles:

- 1 seven-case API count;
- 5 frozen-root/visual-provenance tests awaiting W2/T8;
- 10 new golden tests awaiting five committed snapshots;
- 1 Core 04/07 contract awaiting integration/shared authority text;
- 40 new-case performance nodes awaiting the snapshots;
- 42 S14 portfolio nodes awaiting snapshots or the merged case builder
  (including the six-decimal `_scaled` pin);
- 2 seven-scenario repository validation tests awaiting snapshots;
- 6 synthetic-isolation nodes awaiting snapshots;
- 1 visual source-tree contract awaiting T8.

The complete T4b component regression independently remains:

```text
11 failed, 270 passed, 1 warning in 3.31s
```

Its failures are exactly the API count plus ten new goldens. The four original
goldens are `4 passed, 10 deselected`.

Final non-test oracles:

```text
THRESHOLD LITERAL SCAN PASS (71 Python files; 23 configured numeric values)
ES MODULE CHECK PASS (27 files)
INDEX_EMPTY_PASS
FROZEN_EXISTING_BYTES_UNCHANGED_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
```

IDE diagnostics report no linter errors in the changed source, test and
browser files.

Post-muhasabah fresh rerun (after adding the malformed-attempt fail-closed
negative and the two-attempt SUPERSEDED observed fixture):

```text
pytest -q: 108 failed, 2294 passed, 1 warning in 41.69s
T4b component suites: 11 failed, 270 passed, 1 warning in 3.29s
schema edge cases: 3 passed in 0.17s
THRESHOLD LITERAL SCAN PASS
ES MODULE CHECK PASS
```

Failure membership is unchanged and remains exactly the integration/T8/W2
set enumerated above.

## 2026-09-13T03:05:16Z — INT-3 through T6 evidence

Merged SC-9 observation before `cases/**` changes:

```text
BRIEF 1.1.0 PARTNER_DETAIL_OBSERVED None 4
SNAPSHOT_SCHEMA 2.1.0
PARTNER_ROWS 7
ATTEMPTS: two Comtrade SUPERSEDED + one WITS SUPERSEDED
EXECUTION_CAP partner sentence present
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
SCENARIO VALIDATION FAIL (5/7 scenarios failed)
  exact cause ×5: No public case matches scenario opportunity_id=...
```

The baseline integrity check had exactly two expected pre-T10 hash
mismatches: `config/ui_strings.v1.yaml` and
`config/decision_narratives.v1.yaml`.

INT-4a focused RED:

```text
5 failed in 0.14s
```

Failures proved the merged builder still emitted 2.1.0/no partner block and
CaseBrief duplicated the vocabularies. Post-implementation:

```text
pytest -q tests/test_case_projection.py tests/test_case_brief.py \
  tests/test_public_snapshot_schema.py
100 passed in 0.23s
```

INT-4b:

```text
CASE BRIEF VALID ×5
BYTE_IDENTICAL_TWO_BUILDS 5
WORKTREE_MATCHES_PROVISIONAL_BUILD 5
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

Post-build scenario gate:

```text
SCENARIO VALIDATION PASS (7 scenarios)
ground_truth_backtest: PASS ×7
new-case Gate B overall: PASS ×5
```

The first integrated Python run exposed seven stale assertions, not product
failures: five tests named a non-contract field
`actual_evidence_class`; the 721061 public pin predated observed Comtrade R3
and R10; and the route-0 REJECT helper indexed optional competition fields.
Verification [21] was recorded first. After the three assertion corrections:

```text
pytest -q tests/test_case_briefs_real.py tests/test_s14b_portfolio.py \
  tests/test_golden_cases.py tests/test_scenario_validation.py tests/test_api.py
136 passed, 1 warning in 6.26s
```

The warning remains the pre-existing Starlette/httpx deprecation warning.

## 2026-09-13T03:26:15Z — T7 functional browser evidence

Initial full run:

```text
make e2e-functional
10 failed, 322 passed, 4 deselected, 36 errors
```

RED root causes:

- The Tinplate `UNAVAILABLE` trade point reached SVG path serialization as
  `NaN`.
- The evidence-unlock journey assertion used resolved simulation
  `missing_facts` rather than the public manifest's
  `localized_missing_facts`.

Test-first renderer evidence:

```text
RED: M0,1 L1,UNAVAILABLE L2,3
GREEN: static frontend + ES regression 5 passed
ES MODULE CHECK PASS (27 files)
focused browser: 38 passed, 58 deselected
```

Required full rerun:

```text
332 passed, 4 deselected in 517.16s (0:08:37)
```

The collected functional matrix is 336 nodes. All 332 selected nodes passed;
the four visual nodes were intentionally deselected by the target. The
matrix exercises `CASES=7`, both modes and both locales. No browser failure
collector artifact was reported.

## 2026-09-13T03:31:24Z — T8 canonical visual evidence

The sole canonical regeneration used the approved plan hash:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234
4 passed, 332 deselected in 78.61s
VISUAL_MANIFEST_OK 76
VISUAL_TOTAL_BYTES 11116140 LIMIT 12582912
VISUAL_MAX_FILE_BYTES 230892 LIMIT 614400
VISUAL_OWNERSHIP_WRONG 0
VISUAL_ABSOLUTE_PATHS 0
make e2e-visual: 4 passed, 332 deselected in 57.40s
```

Drift was measured against s14a merge
`ec859f72a1b438b7e5946334f60a4d72cbbf1fb1`. `R` means the intended
element region contains the material change and any remainder passes
tolerance; `T` means the complete image passes tolerance. Full metrics,
DOM rectangles and crops are in
`.autonomous-workflow/evidence/s14-deep-cases-a/visual-s14b/`.

| identity | sig. px | bbox | result |
|---|---:|---|---|
| ar/desktop/journey-a-portfolio-public | 91032 | `[0,343,1170,900]` | R |
| ar/desktop/journey-a-portfolio-simulated | 16555 | `[43,343,1127,900]` | R |
| ar/desktop/journey-b-steel-public-workspace | 3108 | `[42,340,1128,510]` | R |
| ar/desktop/journey-c-steel-simulated-workspace | 3100 | `[285,340,766,513]` | R |
| ar/desktop/journey-d-polypropylene-public-workspace | 3099 | `[285,252,1022,422]` | R |
| ar/desktop/journey-d-polypropylene-simulated-workspace | 3115 | `[170,252,803,425]` | R |
| ar/desktop/journey-e-polypropylene-public-dossier | 0 | none | T |
| ar/desktop/journey-e-polypropylene-simulated-dossier | 0 | none | T |
| ar/desktop/journey-e-steel-public-dossier | 0 | none | T |
| ar/desktop/journey-e-steel-simulated-dossier | 0 | none | T |
| ar/desktop/journey-f-screening-queue-empty | 0 | none | T |
| ar/desktop/journey-f-screening-queue-robust | 0 | none | T |
| ar/desktop/journey-f-screening-record | 0 | none | T |
| ar/desktop/journey-f-screening-summary | 0 | none | T |
| ar/tablet/journey-a-portfolio-public | 838 | `[642,389,741,556]` | R |
| ar/tablet/journey-a-portfolio-simulated | 983 | `[358,389,741,556]` | R |
| ar/tablet/journey-b-steel-public-workspace | 46 | `[42,493,762,523]` | T |
| ar/tablet/journey-c-steel-simulated-workspace | 36 | `[63,520,592,559]` | T |
| ar/tablet/journey-d-polypropylene-public-workspace | 35 | `[281,404,287,414]` | T |
| ar/tablet/journey-d-polypropylene-simulated-workspace | 34 | `[613,449,620,459]` | T |
| ar/tablet/journey-e-polypropylene-public-dossier | 0 | none | T |
| ar/tablet/journey-e-polypropylene-simulated-dossier | 0 | none | T |
| ar/tablet/journey-e-steel-public-dossier | 0 | none | T |
| ar/tablet/journey-e-steel-simulated-dossier | 0 | none | T |
| ar/tablet/journey-f-screening-queue-empty | 0 | none | T |
| ar/tablet/journey-f-screening-queue-robust | 0 | none | T |
| ar/tablet/journey-f-screening-record | 0 | none | T |
| ar/tablet/journey-f-screening-summary | 0 | none | T |
| en/desktop/journey-a-portfolio-public | 99576 | `[270,343,1440,900]` | R |
| en/desktop/journey-a-portfolio-simulated | 25082 | `[312,343,1398,900]` | R |
| en/desktop/journey-b-steel-public-workspace | 6797 | `[525,340,1284,510]` | R |
| en/desktop/journey-c-steel-simulated-workspace | 6808 | `[312,340,1398,535]` | R |
| en/desktop/journey-d-polypropylene-public-workspace | 6797 | `[472,252,1284,422]` | R |
| en/desktop/journey-d-polypropylene-simulated-workspace | 6806 | `[312,252,1398,425]` | R |
| en/desktop/journey-e-polypropylene-public-dossier | 0 | none | T |
| en/desktop/journey-e-polypropylene-simulated-dossier | 0 | none | T |
| en/desktop/journey-e-steel-public-dossier | 0 | none | T |
| en/desktop/journey-e-steel-simulated-dossier | 0 | none | T |
| en/desktop/journey-f-screening-queue-empty | 0 | none | T |
| en/desktop/journey-f-screening-queue-robust | 0 | none | T |
| en/desktop/journey-f-screening-record | 0 | none | T |
| en/desktop/journey-f-screening-summary | 0 | none | T |
| en/tablet/journey-a-portfolio-public | 845 | `[283,388,419,555]` | R |
| en/tablet/journey-a-portfolio-simulated | 990 | `[283,388,666,555]` | R |
| en/tablet/journey-b-steel-public-workspace | 35 | `[334,493,341,503]` | T |
| en/tablet/journey-c-steel-simulated-workspace | 52 | `[262,392,982,577]` | T |
| en/tablet/journey-d-polypropylene-public-workspace | 35 | `[777,404,783,414]` | T |
| en/tablet/journey-d-polypropylene-simulated-workspace | 46 | `[262,320,982,450]` | T |
| en/tablet/journey-e-polypropylene-public-dossier | 0 | none | T |
| en/tablet/journey-e-polypropylene-simulated-dossier | 0 | none | T |
| en/tablet/journey-e-steel-public-dossier | 0 | none | T |
| en/tablet/journey-e-steel-simulated-dossier | 0 | none | T |
| en/tablet/journey-f-screening-queue-empty | 0 | none | T |
| en/tablet/journey-f-screening-queue-robust | 0 | none | T |
| en/tablet/journey-f-screening-record | 0 | none | T |
| en/tablet/journey-f-screening-summary | 0 | none | T |

All eight portfolio entries changed only in the predicted regions. The eight
desktop workspace entries changed in `#opportunity-select`; all eight tablet
workspace entries passed whole-image tolerance. All 32 dossier/screening
entries passed tolerance. Seven screening WebP bytes changed with zero
significant pixels and MAE 0.000003–0.000016; no dossier byte changed.
`DRIFT_FAILURES 0`.

Future frozen tree OIDs, computed with an isolated temporary index and object
store:

```text
data/snapshots/public   a67a921c1909c20e1afe2647e6f41a792cecd08a
data/synthetic          7459beb8a8777fe33592c314bac54de0a1833f25
data/golden             72618db654110823ec7a8d4dd6415a37e4554e33
browser_tests/baselines 709325b65f4fb567f10d3fa23a0139b1ef0de602
INDEX_EMPTY_PASS
```

Final T8 worktree pytest:

```text
5 failed, 2542 passed, 1 warning in 53.65s
```

Exact expected-RED set:

```text
tests/test_frozen_public_evidence_pins.py::test_public_and_synthetic_bytes_unchanged_from_base
tests/test_frozen_public_evidence_pins.py::test_visual_baseline_tree_unchanged_from_base
tests/test_frozen_public_evidence_pins.py::test_frozen_tree_check_passes_in_depth_one_clone_of_this_repository_without_a610b49
tests/test_integrity_contract.py::test_reconstruct_script_prints_case_reconstruction_pass_line
tests/test_integrity_contract.py::test_s14b_core_04_and_07_partner_detail_sentences
```

The first three resolve only after W2 makes the future frozen trees HEAD.
The fourth is the T9 update from the pre-integration zero-snapshot recording
to five reproducible snapshots. The fifth awaits the approved T9 Core text.
The visual baseline contract is GREEN: `21 passed in 0.21s`.

Post-muhasib gate refresh:

```text
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
INDEX_EMPTY_PASS
DIFF_CHECK_PASS
IDE diagnostics: no linter errors
```

Integrity remains intentionally pre-T10 RED with exactly the two approved
catalogue hash mismatches: `config/ui_strings.v1.yaml` and
`config/decision_narratives.v1.yaml`. No snapshot-manifest row failure is
reported because the five new files are untracked until W2.

## 2026-09-13T03:52:00Z — OD-15 RED/GREEN and visual-stop evidence

The stale rendered values were proved before implementation:

```text
11 failed, 92 deselected in 62.58s
portfolio: expected 7 cases and computed 15/19 rule paths; saw fixed 2/15
decision subject: expected Arabic catalogue text; saw raw English status ×7
```

Post-implementation:

```text
tests/test_ui_catalogue.py tests/test_static_frontend.py:
  42 passed, 1 warning in 1.22s
ES MODULE CHECK PASS (27 files)
focused Chromium:
  11 passed, 92 deselected in 7.43s
```

The chip occupies non-zero pixels in every governed portfolio capture:

```text
EN desktop [1213,222,1398,257]  EN tablet [262,267,447,302]
AR desktop [42,222,218,257]     AR tablet [586,268,762,303]
```

The W2 provenance oracle is now expected RED and names exactly four changed
visual-pinned sources:

```text
source-tree provenance is stale: config/ui_strings.v1.yaml
source-tree provenance is stale: src/ior_mvp/static/modules/events.js
source-tree provenance is stale: src/ior_mvp/static/modules/portfolio.js
source-tree provenance is stale: src/ior_mvp/static/modules/renderers/decision.js
```

This proves a second canonical regeneration and owner W2' pin update are
required. No canonical command was executed after W2.

## 2026-09-13T04:12:00Z — OD-16 second canonical execution

Final corrected functional evidence:

```text
make e2e-functional
339 passed, 4 deselected in 521.47s (0:08:41)
```

Canonical execution 2, verbatim:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF="S14b-deep-case-portfolio-scenarios-and-goldens:af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2" make e2e-update-baselines
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 339 deselected in 78.01s (0:01:18)
```

Validation:

```text
VISUAL_MANIFEST_OK 76
VISUAL_TOTAL_BYTES 11117096 LIMIT 12582912
VISUAL_MAX_FILE_BYTES 230892 en/desktop-1440x900/journey-c-steel-simulated-workspace.webp LIMIT 614400
VISUAL_ROOT_BYTES 11157252
VISUAL_ROOT_FILES 78
VISUAL_OWNERSHIP_WRONG 0
VISUAL_ABSOLUTE_PATHS 0
VISUAL_IMAGE_ID sha256:2cc7b584a332ed79b2538d27d9f8dd015d767134215eeb64ba9dd97a6ba5e179
```

Changed WebP entries against W2 `ec2eae1`:

| Entries | Count | Significant drift region | Outside |
|---|---:|---|---:|
| `*/journey-a-portfolio-{public,simulated}.webp` | 8 | locale/viewport chip bbox | 0 |
| `ar/desktop-1440x900/journey-b-steel-public-workspace.webp` | 1 | `[198,847,286,861]` | 0 |
| `ar/desktop-1440x900/journey-d-polypropylene-public-workspace.webp` | 1 | `[163,760,287,774]` | 0 |
| `ar/desktop-1440x900/journey-g-alu-foil-public-workspace.webp` | 1 | `[163,804,287,818]` | 0 |
| `ar/desktop-1440x900/journey-g-alu-profiles-public-workspace.webp` | 1 | `[163,804,287,818]` | 0 |
| `ar/desktop-1440x900/journey-g-galvalume-public-workspace.webp` | 1 | `[163,847,287,861]` | 0 |
| `ar/desktop-1440x900/journey-g-pe-film-public-workspace.webp` | 1 | `[163,804,287,818]` | 0 |
| `ar/desktop-1440x900/journey-g-tinplate-public-workspace.webp` | 1 | `[163,847,287,861]` | 0 |

The complete 76-row table is
`.autonomous-workflow/evidence/s14-deep-cases-a/visual-s14b/drift-t8b.md`.
Before/after/diff/composite crops exist for the EN desktop public portfolio
chip and AR desktop galvalume public decision-subject card. Result:
`DRIFT_FAILURES 0`.

Host comparison:

```text
make e2e-visual
4 passed, 339 deselected in 58.73s
```

Future baseline tree from isolated temporary index:

```text
0259f800dbcc4c3726549b3af2ed78cc570ef281
INDEX_EMPTY_PASS
```

Pre-W2' pin result:

```text
2 failed, 15 passed in 2.19s
```

Both failures are confined to the committed/working baseline tree mismatch
(`709325b6…` versus future `0259f800…`). Source provenance is current. State:
`T8b_HANDOFF_W2PRIME_PENDING`.

## 2026-09-13T04:57:00Z — T9–T11 execution evidence

T9 RED/GREEN:

```text
test_s14b_governed_docs_record_portfolio_routes_and_limits: RED, then PASS
test_s14b_core_04_and_07_partner_detail_sentences: RED, then PASS
browser inventory: expected 32, observed new OD-15 test 33; corrected PASS
case reconstruction: expected 0/5, observed 5/5; corrected PASS
pre-manifest pytest: 2549 passed, 1 warning in 52.89s
```

Single T10 generator execution and immediate oracle:

```text
receipt 2026-09-13T04:25:49Z
SNAPSHOT_ROWS 628 -> 638
SNAPSHOT_ADDED 10
SNAPSHOT_PRIOR_CHANGED 0
AUTHORITY_ROWS 19 -> 19
AUTHORITY_CHANGED 5
AUTHORITY_CHANGED_PATH config/decision_narratives.v1.yaml
AUTHORITY_CHANGED_PATH config/ui_strings.v1.yaml
AUTHORITY_CHANGED_PATH docs/core/04_CANONICAL_DATA_MODEL.md
AUTHORITY_CHANGED_PATH docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
AUTHORITY_CHANGED_PATH docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
MANIFEST_DELTA_ORACLE_PASS
test_human_authority_table_matches_machine_manifest_exactly: PASS
INTEGRITY PASS
```

Portability copy:

```text
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
ABSOLUTE_PATHS_PASS
PORTABILITY_GATE_PASS
```

Final local CI:

```text
make ci
2549 passed, 1 warning in 50.68s
339 passed, 4 deselected in 515.04s
4 passed, 339 deselected in 59.41s
exit 0
```

Committed scratch-clone CI on W2' parent:

```text
scratch commit 4e39cc8053197b2a6a17a9fbdfe5c60eb1c154a3
parent 5354a6f230bfee24e3aed97ad8120f804e97f603
CI=1 UV_PYTHON=3.12 make ci
2549 passed, 1 warning in 47.77s
339 passed, 4 deselected in 508.99s
4 passed, 339 deselected in 56.28s
exit 0
```

The prior Python 3.14 scratch attempt is retained as environment evidence: all
2,549 tests passed, then offline e2e dependency resolution stopped because the
CPython 3.14 Pillow wheel was not cached. No product file changed before the
successful Python 3.12 rerun.

## 2026-09-13T05:00:00Z — T12 IAC-6 identity

Recipe-conformant metadata:

```text
base 5354a6f230bfee24e3aed97ad8120f804e97f603
wip_parent 1289e31
excluded .workflow/slices/S14-deep-cases-a/**
excluded .workflow/slices/S14b-deep-case-portfolio/**
CANDIDATE_IDENTITY 6307ccb311c208f4874d96ec48386f2411a5134a96d3e592d2b88347e2e3d156
CANDIDATE_FILE_COUNT 121
PAYLOAD_KEYS ['base', 'files', 'wip_parent']
ROW_KEYS ['bytes', 'path', 'sha256']
TRAILING_NEWLINE True
EXCLUDED_S14_RECORD_FOLDERS_PASS True
INDEX_EMPTY_PASS
STATE_JSON_VALID_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
tests/test_frozen_public_evidence_pins.py: 17 passed
```

The payload is
`json.dumps(payload, sort_keys=True, separators=(",", ":"),
ensure_ascii=False) + "\n"` encoded as UTF-8 before SHA-256. Deleted paths,
if any, use JSON null and zero bytes.

Final default suite:

```text
2549 passed, 1 warning in 48.61s
```

State: `T12_HANDOFF_REVIEW_PENDING`.

### Exact-final-candidate scratch rerun

Muhasib found that `4e39cc8` omitted three later control-record updates. The
exact 121-file candidate was recommitted on the same W2' parent as local-only
scratch commit `d41ed7df5c1d942ac5fb67abdc1437232a2deb13` and rerun:

```text
CI=1 UV_PYTHON=3.12 make ci
2549 passed, 1 warning in 48.45s
339 passed, 4 deselected in 517.84s
4 passed, 339 deselected in 56.79s
exit 0
```

This is the governing scratch-clone proof for the final identity.

## 2026-09-13T05:36:00Z — Review correction RED

Authority: reviewer finding S14B-IR1-F01 and owner ruling OD-18. Test-first
command and result:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-correction-pyc
PYTHONPATH=src
.venv/bin/pytest -q \
  tests/test_integrity_contract.py::test_s14b_core_04_and_07_partner_detail_sentences

FAILED — AssertionError: exact-key `partner_detail` marker absent
1 failed in 0.09s
```

The test requires, in order, `state`, `reason`, `source_id`,
`partner_snapshot_id`, `unit_key`, `observed_partner_rows`,
`attempt_passport_ids`, `observed_passport_id`, and rejects
`source_snapshot_id`, `observed_row_count`, `calculated_passport_id` anywhere
in Core 04 §12.

GREEN after correcting only Core 04 §12:

```text
tests/test_integrity_contract.py::
test_s14b_core_04_and_07_partner_detail_sentences
1 passed in 0.07s
```

Pre-generation suites:

```text
pytest -q: 2549 passed, 1 warning in 52.05s
verify_integrity.py: INTEGRITY FAIL — Core 04 hash mismatch only
PRE_MANIFEST_CORE04_ONLY_RED_PASS
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
make e2e-functional: 339 passed, 4 deselected in 512.73s
make e2e-visual: 4 passed, 339 deselected in 56.17s
```

Second/final S14b manifest pre-invocation receipt:
`2026-09-13T05:49:09Z`. Authorized delta: no snapshot-manifest change; only
Core 04 changes in the 19-row authority manifest relative to identity
`6307ccb3…`; §11 mirrors the machine file. No third run is authorized.

Observed result:

```text
BUILD_MANIFESTS_EXIT 0
SNAPSHOT_MANIFEST_BYTE_IDENTICAL_PASS rows=638
AUTHORITY_ROWS 19 -> 19
AUTHORITY_CHANGED 1
AUTHORITY_CHANGED_PATH docs/core/04_CANONICAL_DATA_MODEL.md
SECOND_MANIFEST_DELTA_ORACLE_PASS
test_human_authority_table_matches_machine_manifest_exactly: 1 passed
INTEGRITY PASS
```

Correction portability:

```text
/tmp/ior-s14b-correction-portability
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
ABSOLUTE_PATHS_PASS
CORRECTION_PORTABILITY_GATE_PASS
```

Exact corrected scratch candidate:

```text
commit 7d597015bdba41f7a6bc55aab4bbde95159aaf91
parent 5354a6f230bfee24e3aed97ad8120f804e97f603
CI=1; UV_PYTHON=3.12; UV_OFFLINE=1
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
all reconstruction stages PASS
2549 passed, 1 warning in 50.92s
SMOKE PASS
339 passed, 4 deselected in 514.70s
4 passed, 339 deselected in 56.86s
exit 0
```

`make ci` was intentionally not rerun; OD-18 assigns it to the owner after
re-review.

Corrected IAC-6 identity:

```text
base 5354a6f230bfee24e3aed97ad8120f804e97f603
wip_parent 1289e31
CORRECTED_CANDIDATE_IDENTITY 24c3b3cc219168dae4b1d720f7913cc71a31217ff6eafc0dccd39172335c3a38
CANDIDATE_FILE_COUNT 121
CHANGED_VS_6307CCB3 5
CHANGED_PATH docs/ARCHITECTURE_DECISIONS.md
CHANGED_PATH docs/authority/00_AUTHORITY_MANIFEST.md
CHANGED_PATH docs/authority/authority_hashes.json
CHANGED_PATH docs/core/04_CANONICAL_DATA_MODEL.md
CHANGED_PATH tests/test_integrity_contract.py
ADDED_VS_6307CCB3 0
REMOVED_VS_6307CCB3 0
FULL_DELTA_PLUS_UNTRACKED_PASS
EXCLUDED_S14_RECORD_FOLDERS_PASS
COMPACT_JSON_TRAILING_LF_PASS
EXACT_CORRECTION_SCRATCH_MATCH_PASS
INDEX_EMPTY_PASS
```

The path set is the NUL-safe union of the full diff from `1289e31` and
untracked non-ignored files, minus both S14 slice-record folders. The evidence
files containing this block are therefore outside the identity by rule.
