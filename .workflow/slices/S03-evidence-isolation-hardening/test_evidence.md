# S03 Test Evidence

All results below are observed local outputs on
`slice/S03-evidence-isolation-hardening` from base
`c43837054c5581e68cfe7ed87d914a89cd4f63a3`. No hosted CI, review,
commit, PR, or merge result is claimed.

## Task 0 — Preflight

```text
PROBE-OK
slice/S03-evidence-isolation-hardening
c43837054c5581e68cfe7ed87d914a89cd4f63a3
```

```text
PROHIBITED FILE SCAN PASS (123 tracked files)
```

## Task 1 — Policy validation RED/GREEN

Command:
`PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_synthetic_isolation.py -q`

RED:

```text
10 failed, 9 passed in 0.05s
```

Observed failure reasons:

- policy metadata remained 1.0.0;
- three Core 06 §4 fields were not required;
- wrong display label and Class C were accepted;
- source validation was hard-coded rather than policy-described;
- non-mapping `synthetic_inputs` was accepted;
- ledger generation raised `KeyError: 'display_label'`;
- repository loading raised `RepositoryError` for missing
  `opportunity_id`.

GREEN:

```text
19 passed in 0.02s
```

## Exact governed YAML diff

```diff
 metadata:
-  version: "1.0.0"
-  effective_date: "2026-08-31"
+  version: "1.1.0"
+  effective_date: "2026-09-02"
 synthetic_isolation:
   required_fields:
     - synthetic_flag
     - scenario_id
+    - opportunity_id
+    - display_label
     - seed_basis
     - evidence_class
     - source
+    - synthetic_inputs
+  required_evidence_class: D
+  required_source: DEMO_GENERATOR
```

No other `config/evidence_policy.v1.yaml` semantic line changed.

## Task 2 — Reconciliation RED/GREEN

RED:

```text
ImportError: cannot import name 'reconcile_synthetic_scenario'
1 error during collection
```

GREEN:

```text
tests/test_scenario_validation.py: 14 passed in 0.03s
scenario validation + unchanged goldens: 18 passed in 0.03s
```

Current fixture arithmetic:

```text
Steel: demand 104.0 <= imports 287.9; nameplate 250.0 <= 250.0;
       qualified availability NOT_APPLICABLE; overall PASS.
PP:    demand 56.0 <= imports 56.0; nameplate 1170.0 <= 1170.0;
       qualified availability 80.0 <= 1055.457; overall PASS.
Both:  demand-layer observation INFORMATIONAL;
       allocation reconciliation NOT_APPLICABLE.
```

## Task 3 — Gate B validator RED/GREEN

RED:

```text
ModuleNotFoundError: No module named 'scripts.validate_scenarios'
1 error during collection
```

GREEN:

```text
tests/test_scenario_validation.py: 17 passed in 0.03s
```

Observed repository validator output:

```text
SCENARIO VALIDATION PASS (2 scenarios)
- SYN-MINISTRY-PP-001.json scenario=SYN-MINISTRY-PP-001 opportunity=SAU-H0-390210 status=PASS
  target_spec_demand_within_public_imports: PASS - 56 kt <= 56 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 1170 kt <= 1170 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: PASS - 80 kt <= 1055.46 kt.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_or_buyer_allocations_reconcile: NOT_APPLICABLE - No governed tariff-line or buyer allocation block is present; no allocation sum was evaluated.
- SYN-MINISTRY-STEEL-001.json scenario=SYN-MINISTRY-STEEL-001 opportunity=SAU-H0-721049 status=PASS
  target_spec_demand_within_public_imports: PASS - 104 kt <= 287.9 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 250 kt <= 250 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: NOT_APPLICABLE - No qualified_available_kt is declared.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_or_buyer_allocations_reconcile: NOT_APPLICABLE - No governed tariff-line or buyer allocation block is present; no allocation sum was evaluated.
```

Temp-only validator tests prove exit 1 for a planted reconciliation
failure and exit 2 for invalid JSON; both are included in the 17-test
GREEN count. No packaged data file was edited.

## Task 4 — HTTP 422 and 404

RED:

```text
2 failed: detailed and list simulated endpoints returned 500, expected 422
```

GREEN:

```text
422 exact-body parameterized test: 2 passed in 0.15s
missing-scenario exact 404 test: 1 passed in 0.15s
full tests/test_api.py: 10 passed in 0.17s
```

The 422 expected body is:

```json
{"detail":{"code":"EVIDENCE_INTEGRITY_ERROR","message":"Synthetic scenario reconciliation failed for SYN-MINISTRY-STEEL-001: target_spec_demand_within_public_imports"}}
```

## Tasks 5–7 — Authority, dossier, and banner

```text
Authority RED: missing AuthorityConfigurationError/authority loader.
Authority GREEN: 7 passed.
Dossier RED: 2 missing-authority failures; public no-disclosure characterization passed.
Dossier GREEN: 13 passed.
Frontend RED: 3 failed, 4 passed.
Frontend GREEN: 7 passed in 0.01s.
node --check src/ior_mvp/static/app.js: exit 0.
```

The frontend test measures `--teal-soft` against both existing banner
gradient stops and requires a contrast ratio of at least 4.5:1.

## Task 8 — R5

```text
RED: R5 metrics {}, 1 failed.
GREEN: 14 passed in 0.02s.
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
```

## Task 9 — CI contract

```text
RED: 5 failed, 7 passed.
GREEN: 12 passed in 0.05s.
```

`make -n ci` observed this relevant order:

```text
python scripts/verify_integrity.py
python scripts/validate_scenarios.py
pytest -q
python scripts/demo_smoke.py
```

Plan-test correction: the approved draft indexed the complete Makefile,
so its `pytest -q` search matched the earlier `test` target. The
assertion now scopes the same ordered fragments to `ci: uv-sync`.

## Focused S03 regression

Command: policy, reconciliation, authority, dossier, API, rules,
CI-contract, static frontend, and golden test files.

```text
94 passed, 1 warning in 0.36s
```

The warning is the existing FastAPI/Starlette `httpx` deprecation
warning.

## Task 10 — Complete pre-manifest regression

Detached script:
`.workflow/logs/s03-pre-manifest.sh` (ignored). The prescribed
`nohup setsid` process was not retained by this shell backend, so the
same unchanged script was executed with the shell backend's managed
background facility. Its repository log ended with
`__DONE__ status=0`.

Observed output:

```text
PROHIBITED FILE SCAN PASS (123 tracked files)
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
SCENARIO VALIDATION PASS (2 scenarios)
191 passed, 1 warning in 0.42s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
__DONE__ status=0
```

The Gate B details in this run again showed PP and steel overall
`status=PASS`, the exact demand/nameplate arithmetic, PP physical
ceiling pass, steel physical check `NOT_APPLICABLE`, informational
demand layers, and allocation `NOT_APPLICABLE`.

Pre-generator audits:

```text
git diff -- config/evidence_policy.v1.yaml: exact Task 1 diff recorded above
git diff -- data: empty
git diff --check: exit 0, no output
scripts/build_manifests.py invocation count by this implementer: 0
```

All Task 11 preconditions authorized by `plan_review.md` are now
recorded before manifest generation: focused tests, Gate B exit 0,
temp exit 1/2 tests, scanners, compile, JavaScript syntax, full pytest,
smoke, unchanged four golden outcomes, exact policy diff, and empty
data diff.

## Task 11 — Single manifest generation

Generator invocation count: exactly one.

Command:
`PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/build_manifests.py`

Observed generator diff:

```text
docs/authority/authority_hashes.json:
  config/evidence_policy.v1.yaml SHA-256 only:
    20dbcf06bccd76989f32e45f8083b9fc7aa38f0d2b2c40b12028bd3a2dd70d01
    -> f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2
  bytes only: 1246 -> 1373
  no generated_on or other entry changed

data/manifests/snapshot_manifest.json:
  no diff
```

Independent file checks:

```text
sha256sum config/evidence_policy.v1.yaml
f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2  config/evidence_policy.v1.yaml

stat:
1373 bytes
```

Machine JSON and human Manifest §11 now both contain
`f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2`
and bytes `1373` / `1,373`.

Post-generation integrity:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

## Task 12 — Documentation and builder audit

```text
Authority/dossier/API/CI/static contract audit: 41 passed, 1 warning in 0.34s
git diff --check: exit 0, no output
protected governed-path diff: empty
IDE diagnostics: none
bare-except scan on changed Python: no matches
```

Protected path audit covered `data/**`, `config/thresholds.v1.yaml`,
`config/sector_profiles.v1.yaml`, `docs/core/**`, and the methodology
DOCX. The generated snapshot manifest therefore remains unchanged.

Traceability rows FR-001, FR-004, INV-03, INV-04, TL-09, GATE-B, and
GATE-F are `IMPLEMENTED`. Existing TL-01 remains `TESTED` only because
that pre-existing S01 evidence status must not be demoted; its S03
scope pointer was appended without claiming new hosted evidence.

KL-04/05/06 remain open pending reviewed squash merge/current-head CI;
KL-26 remains accepted with explicit `NOT_CALCULABLE` treatment; KL-27
and KL-28 record the approved deferred-schema rulings. ADR-008 remains
`Proposed for S03`. No review, hosted CI, PR, or merge fact is claimed.

## Task 14 — Final local validation

The first final-script attempt passed complete `make ci` but stopped in
the additional raw-system proof because `/usr/bin/python3` had neither
a global `pytest` command nor the pytest module:

```text
.workflow/logs/s03-final.sh: line 15: pytest: command not found
__DONE__ status=127
/usr/bin/python3: No module named pytest
```

Root-cause check proved the uv-managed environment created by
`make ci` contained pytest:

```text
/home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin/pytest
pytest 8.4.2
```

The ignored validation script was corrected to activate that uv
environment only around the plan's raw proof commands. No production,
test, config, data, or governed file changed for this environment fix.

Final detached/managed-background run ended:

```text
__PHASE_DONE__ make-ci
__PHASE_DONE__ system-proof
__PHASE_DONE__ clean-pip
__PHASE_DONE__ docker
__DONE__ status=0
```

Observed phase results:

```text
make ci via /home/barami/.local/bin/uv:
  uv sync: Resolved 29 packages; Checked 28 packages
  prohibited scan: PASS (123 tracked files)
  threshold scan: PASS (13 Python files; 23 numeric values)
  compile: PASS
  node syntax: PASS
  integrity: PASS
  Gate B: PASS (2 scenarios)
  pytest: 191 passed, 1 warning in 0.38s
  smoke: PASS

uv-environment explicit proof:
  integrity: PASS
  Gate B: PASS (2 scenarios)
  pytest: 191 passed, 1 warning in 0.33s
  smoke: PASS

clean pip venv:
  editable dev install: PASS
  prohibited scan: PASS (123 tracked files)
  threshold scan: PASS (13 Python files; 23 numeric values)
  compile: PASS
  node syntax: PASS
  integrity: PASS
  Gate B: PASS (2 scenarios)
  pytest: 191 passed, 1 warning in 0.34s
  smoke: PASS

docker:
  docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s03-local .
  image named successfully; build exit 0
```

Every Gate B phase reported both packaged scenarios `status=PASS`.
Every smoke phase preserved steel public INVESTIGATE, steel simulated
ADVANCE with real state unchanged, and PP public REJECT. The one pytest
warning in each environment is the FastAPI/Starlette `httpx`
deprecation warning already recorded above.

## Final staged-patch hygiene

```text
approved S03 paths staged: yes
prohibited/Supervisor-only staged-path query: empty
PROHIBITED FILE SCAN PASS (133 tracked files)
INTEGRITY PASS
git diff --cached --check: exit 0 after removing three record-only trailing spaces
```

No commit, push, PR, hosted CI, review verdict, or merge is claimed.
