# S08 test evidence — PublicSnapshot v2 and computed rule ledger

All results below are local, uncommitted Implementer evidence. This is
**implementation evidence, not approval**. Supervisor review, independent
Grok review, hosted CI, delivery, merge, limitation closure, and milestone
completion remain external gates.

## Environment and identity

```text
branch: slice/S08-snapshot-v2-computed-rules
base/HEAD: 9f045a4ecf929b82a0c4ad9013d255e148bc837d
primary Python: CPython 3.12 (.venv)
compatibility Python: CPython 3.14 (/tmp/venv314)
data classification: confidential_demo
Playwright: 1.62.0
pytest-playwright: 0.9.0
Chromium: chromium-1234 / 151.0.7922.34
Docker: available; canonical Noble image digest pinned by S07
```

No `sudo`, `apt`, dependency/lock edit, live source, `.env` read, staging,
commit, push, PR, merge, or tag occurred.

## Characterization and migration proof

Pre-change characterization:

```text
PROHIBITED FILE SCAN PASS (344 tracked files)
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
377 passed, 1 warning in 2.28s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Initial future-migration RED:

```text
..FF                                                                     [100%]
2 failed, 2 passed in 0.03s
```

Both failures were the intended absence of
`data/snapshots/public/historical/v1/*.json`.

Pre-cutover in-memory complete deep-diff proof:

```text
..                                                                       [100%]
2 passed, 4 deselected in 0.02s
```

Post-cutover historical-v1/live-v2 proof:

```text
......                                                                   [100%]
6 passed in 0.02s
```

Exact v1 retention:

```text
10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7  data/snapshots/public/historical/v1/SAU-H0-721049.json
cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948  data/snapshots/public/historical/v1/SAU-H0-390210.json
 6850 data/snapshots/public/historical/v1/SAU-H0-721049.json
 5572 data/snapshots/public/historical/v1/SAU-H0-390210.json
```

Field-for-field live-oracle check:

```text
SAU-H0-721049.json: exact field-for-field v2 oracle match
SAU-H0-390210.json: exact field-for-field v2 oracle match
```

## TDD evidence

Observed RED causes and final GREEN evidence:

| Contract | RED evidence | GREEN evidence |
|---|---|---|
| schema module | import failed: no `ior_mvp.public_snapshot` | 30 schema/loader tests in final suite |
| migration | historical v1 paths absent | pre-cutover 2/2 and post-cutover 6/6 |
| trade metrics | import failed: no `ior_mvp.trade_metrics` | 28 pure metric tests |
| R1-D/R2/R3 | missing rule helpers | config cap, CAGR, dual-basis rules/boundaries green |
| R4-D/R5/R9-S/R10/R11 | missing helpers/formulas | evidence-derived states, exact text, and boundaries green |
| dossier register | version 1.0/no register/no keys | dossier 1.1 + catalogue 1.1.0 tests green |
| KL-32 | no uid/gid command, identity, or sweep | command/identity/ownership tests green |
| Gate B v2 failure | invalid public schema escaped `main()` | controlled exit 2 test green |
| predicate precision | R3/R5 false-positive and R11 false-negative near rounded boundaries | all three predicates consume unrounded intermediates |
| source/flow integrity | disclosed HHI was rounded; contradictory direct/re-export inputs accepted by helper | source precision retained; helper raises |

No skip, xfail, mask, tolerance change, expected-golden change, or disabled
assertion was introduced.

## Focused S08 suite

Command:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_public_snapshot_schema.py tests/test_trade_metrics.py tests/test_snapshot_migration_equivalence.py tests/test_rules.py tests/test_threshold_boundaries.py tests/test_scenario_validation.py tests/test_simulation_fidelity.py tests/test_synthetic_isolation.py tests/test_dossier_contract.py tests/test_api.py tests/test_integrity_contract.py tests/test_authority_disclosure.py tests/test_threshold_literals.py tests/test_ui_catalogue.py tests/test_visual_baseline_contract.py
```

Output:

```text
343 passed, 1 warning in 1.01s
```

The warning is the pre-existing Starlette/httpx TestClient deprecation.

## Full Python suites

Python 3.12:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q
503 passed, 1 warning in 2.27s
exit 0
```

Python 3.14:

```text
UV_PROJECT_ENVIRONMENT=/tmp/venv314 uv sync --locked --extra dev --python 3.14
UV_PROJECT_ENVIRONMENT=/tmp/venv314 PYTHONPATH=src uv run --locked --extra dev --python 3.14 python -m pytest -q
503 passed, 1 warning in 2.22s
exit 0
```

The exact workspace aliases initially found no standalone system `pytest`.
With the project environment placed first on `PATH`, the required aliases
produced:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
503 passed, 1 warning in 2.28s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

## Static, authority, data, and smoke gates

```text
PROHIBITED FILE SCAN PASS (344 tracked files)
THRESHOLD LITERAL SCAN PASS (15 Python files; 23 configured numeric values)
UI CONTRACT CHECK PASS
ES MODULE CHECK PASS (19 files)
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
SCENARIO VALIDATION PASS (2 scenarios)
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Gate B details:

```text
SYN-MINISTRY-PP-001: target 56 <= imports 56; nameplate 1170 <= 1170; factors PASS; qualified availability 80 <= 1055.46; ground_truth_backtest PASS.
SYN-MINISTRY-STEEL-001: target 104 <= imports 287.9; nameplate 250 <= 250; factors PASS; qualified availability NOT_APPLICABLE; ground_truth_backtest PASS.
```

## Manifest generation and integrity

`PYTHONPATH=src .venv/bin/python scripts/build_manifests.py` ran exactly once.
Pre-run integrity failed only for the two replaced live public snapshots,
thresholds, catalogue, and Core 02/04/07/09.

Snapshot manifest:

```text
live PP v2:       02e807de8c016e35341a22ffbc30b78947a0725058641866e3d041dc413cb69c / 8,919
live steel v2:    173b45c821b932a6e82550ceecaa47a23bb98bdec82c8d602e0ef7da1db323f0 / 9,992
historical PP v1: cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948 / 5,572
historical steel: 10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7 / 6,850
synthetic/golden rows unchanged; generated_on unchanged.
```

Authority manifest changed only:

```text
thresholds  4e891b9706408f6a661565e09609d0d663e1a00a17bda4e283a4b2ee63d3c47a / 3,887
ui_strings cb1881fdfbbbd757c83a01f5ad489ab6587a39a28c387522d982e08338d4a08b / 24,254
Core 02     daab176c8d19fe454731e1f05e93697c0141a9bc7fba5458931a7a0100007c3d / 14,172
Core 04     354008fdec23d15fed6c00f89cd0ad79bb9e9b2fd62a31a219d078d09f89893d / 11,713
Core 07     da09c2523764ce35f1bbf7652a3b95a3558ec2a26f87403f7afb40381fbb1dcc / 11,305
Core 09     8c59e2d429fa01988977a16615f1c591196ba92d9d5e60e2698470695c31dfa8 / 7,797
```

Post-generation:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
6 passed in 0.01s
```

The six integrity tests include machine/human Manifest §11 equality.

## Browser and visual evidence

Functional precondition before the initial update:

```text
118 passed, 4 deselected in 122.68s
```

An unrounded-predicate self-audit after that update changed engine source
without changing golden rendered output. It received RED/GREEN tests and
another complete functional precondition:

```text
118 passed, 4 deselected in 122.40s
```

A corrective canonical recapture was therefore required so source-tree
provenance described the actual candidate. Both update executions are
recorded; the final one produced:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 118 deselected in 32.53s
```

No read-only-workspace pytest cache warning remained after the container
cache-provider fix.

Final ownership output, pasted verbatim:

```text
BASELINE OWNERSHIP PASS uid=1000 paths=236 webps=40
1000 browser_tests/baselines/v0.3.0
1000 browser_tests/baselines/v0.3.0/manifest.json
1000 browser_tests/baselines/v0.3.0/manifest.sha256
1000 .artifacts/e2e
```

Final visual manifest:

```text
manifest_sha256=452db1c96b8e86cdd4ab770f7a83c4e895f1307b5b41eb428cdf34983cfb7b41
manifest_recorded_sha256=452db1c96b8e86cdd4ab770f7a83c4e895f1307b5b41eb428cdf34983cfb7b41
change_ref=S08-computed-rules-dossier-contradictions
entries=40 webps=40 bytes=4998710
browser=151.0.7922.34 revision=chromium-1234
```

Final `make e2e`:

```text
functional: 118 passed, 4 deselected in 122.72s
visual: 4 passed, 118 deselected in 24.21s
exit 0
```

The browser inventory remains 18 named tests / 122 nodes. Exact RT-01–RT-06
and RT-08–RT-13 assertions were added inside existing parameterized
functions; RT-07 is covered by the unavailable-export unit fixture. Eight
desktop dossier baselines were viewed after the initial capture and four
representative final desktop dossiers were viewed after recapture. Both
directions/locales render the contradiction block correctly where in the
viewport, source text remains an English island, public mode has no synthetic
warning, and simulated mode retains both warnings.

## Complete local CI

```text
LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make ci
PROHIBITED FILE SCAN PASS (344 tracked files)
THRESHOLD LITERAL SCAN PASS (15 Python files; 23 configured numeric values)
UI CONTRACT CHECK PASS
ES MODULE CHECK PASS (19 files)
INTEGRITY PASS
SCENARIO VALIDATION PASS (2 scenarios)
503 passed, 1 warning
SMOKE PASS
118 functional browser nodes passed
4 visual browser nodes passed
exit 0
```

## Golden outcomes

```text
steel public:       INVESTIGATE
steel simulated:    ADVANCE route 5
polypropylene public:    REJECT route 0
polypropylene simulated: REJECT route 0
steel simulation exacts: effective capacity 57.509 kt; gap 46.491 kt; D* 0.2667; S* 18; incremental national value 198; capacity ratio 1.0751
polypropylene simulation: gap -24 kt; support 0
```

## Sanad recount

Exact command output, pasted verbatim:

```text
VERIFIED 43
SPECIFIED 135
DERIVED 18
PROPOSED 63
OPEN 0
```

## Known residuals

- Public R5 inputs remain `UNAVAILABLE` until S12; no public quantity was
  invented.
- `public_decision_contract` remains until S09 by approved scope.
- The Starlette/httpx TestClient deprecation warning is pre-existing.
- Standalone system `pytest` is unavailable; `.venv/bin` or uv is required.
- Two canonical baseline update executions occurred because the first was
  invalidated by a subsequent full-precision source correction. The final
  oracle, ownership, source hashes, images, and compare were reverified. The
  manifest generator still ran exactly once.

## Final diff and protected-path audit

```text
git diff --check
(no output; exit 0)

git diff --cached --name-only
(no output; candidate unstaged)

git diff --name-only -- data/synthetic data/golden config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/03_SYSTEM_ARCHITECTURE.md docs/core/05_DATA_SOURCES_AND_INGESTION.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md
(no output)

S06 documentary reference aggregate:
d71041e0811509746a94ec9baf7c2511236b64c22fd2774e732d08ed50dc6784
```

The methodology DOCX, sectors, evidence policy, synthetic scenarios, extraction
golden, Core 01/03/05/06/08, golden expectations, dependencies, and locks are
unchanged. The two untracked helper scripts remain outside the candidate.

```text
CANDIDATE PROHIBITED SCAN PASS (88 files; 2 helper scripts excluded)
```

## Fix round 1 — SR-01 migration anti-drift regression

RED command:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_snapshot_migration_equivalence.py
........F                                                                [100%]
FAILED tests/test_snapshot_migration_equivalence.py::test_live_v2_ledger_equality_detects_in_memory_trade_drift
AssertionError: ('R2', 'metrics')
1 failed, 8 passed in 0.05s
```

The failure followed an in-memory-only change to the copied live steel
`trade[-1]["imports_kt"]`; no snapshot file was edited.

GREEN focused command:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_snapshot_migration_equivalence.py
.........                                                                [100%]
9 passed in 0.03s
```

Required full default suite:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q
........................................................................ [ 14%]
........................................................................ [ 28%]
........................................................................ [ 42%]
........................................................................ [ 56%]
........................................................................ [ 71%]
........................................................................ [ 85%]
........................................................................ [ 99%]
..                                                                       [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
506 passed, 1 warning in 2.50s
```

No visual baseline command was run. The candidate remains uncommitted.
