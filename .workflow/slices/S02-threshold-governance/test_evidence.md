# Test Evidence — S02 Threshold Governance

All outputs below were observed on `slice/S02-threshold-governance` at base `432af8af1fa88a2258a0fd8d825a6855e408270f`. No CI, review or merge result is claimed.

## Preflight

```text
PROHIBITED FILE SCAN PASS (107 tracked files)
```

## Validator TDD

Initial test red, before the validator module existed:

```text
ModuleNotFoundError: No module named 'scripts.check_threshold_literals'
1 error during collection
```

Pure validator tests after implementation:

```text
9 passed, 2 deselected in 0.02s
```

Initial repository scan before the R11 config key existed:

```text
THRESHOLD LITERAL SCAN FAIL
- src/ior_mvp/decision_engine.py:131:1.25
- src/ior_mvp/decision_engine.py:140:0.4
```

Required red scan after adding the approved R11 key and before source fixes:

```text
THRESHOLD LITERAL SCAN FAIL
- src/ior_mvp/decision_engine.py:131:1.25
- src/ior_mvp/decision_engine.py:140:0.4
- src/ior_mvp/rules.py:276:50
```

Frontend red:

```text
test_frontend_hhi_caption_uses_payload_threshold FAILED
AssertionError: "Resilience review threshold: 0.25" remained in app.js
1 failed in 0.01s
```

Final Python repository validator after source externalisation:

```text
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
```

## Rule, boundary and frontend TDD

Boundary/rule red before predicates:

```text
ImportError: cannot import name 'publication_allowed' from 'ior_mvp.capability'
1 error during collection
```

Engine-focused boundaries, rules, capability and goldens:

```text
68 passed, 1 deselected in 0.05s
```

The Kmin 0.70 integration case passed; no float-precision concern occurred.

Metric-grid red before GenUI propagation:

```text
KeyError: 'supplier_concentration'
1 failed in 0.02s
```

Frontend caption and metric-grid integration green:

```text
2 passed in 0.02s
```

`node --check src/ior_mvp/static/app.js` exited 0. The approved literal search returned no matches.

## CI contract TDD

Before workflow/Makefile wiring:

```text
4 failed, 5 passed in 0.05s
```

Observed failures were the missing validator command in both Python job gate sets and the missing immediately-following step in both jobs.

After wiring:

```text
9 passed in 0.03s
```

`make -n ci` showed this order:

```text
check_prohibited_files.py
check_threshold_literals.py
compileall
node --check
verify_integrity.py
pytest -q
demo_smoke.py
```

## Pre-manifest governed YAML diff

Observed before the manifest run:

```diff
diff --git a/config/thresholds.v1.yaml b/config/thresholds.v1.yaml
index 8de5ed3..0518cd8 100644
--- a/config/thresholds.v1.yaml
+++ b/config/thresholds.v1.yaml
@@ -1,7 +1,7 @@
 metadata:
   artifact: industrial-opportunity-thresholds
-  version: "1.0.0"
-  effective_date: "2026-08-31"
+  version: "1.1.0"
+  effective_date: "2026-09-02"
   authority: "Industrial Opportunity Resolution Methodology, Appendix B"
   status: frozen_for_demo_cycle
   change_gate: "methodology-owner approval + golden-case regression"
@@ -77,10 +77,11 @@ rules:
     sector_scope: all
     revision_date: "2026-08-31"
   R11:
+    generic_capacity_export_import_value_ratio: 50
     downside_cost_premium_over_import_parity: 0.25
-    rationale: "Economic exclusion absent verified strategic externality."
+    rationale: "Economic exclusion absent verified strategic externality; established exports above the configured import ratio warn against generic capacity support."
     sector_scope: all
-    revision_date: "2026-08-31"
+    revision_date: "2026-09-02"

 capability:
   unknown_penalty_lambda: 0.50
```

The diff contains only the planned metadata and R11 lines.

## Pre-manifest full regression

The detached Task 5 script exited 0 after all pre-authorisation conditions were observed:

```text
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
136 passed, 1 warning in 0.31s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

The warning is the pre-existing Starlette `httpx` test-client deprecation warning. The planned-only YAML diff, clean validator, full pytest pass and demo-smoke pass on thresholds 1.1.0 were all recorded before manifest generation.

## Single manifest generation

`scripts/build_manifests.py` was invoked once after the recorded Task 5 conditions and exited 0.

Generated authority-manifest diff:

```diff
diff --git a/docs/authority/authority_hashes.json b/docs/authority/authority_hashes.json
index ae82e01..84c6d97 100644
--- a/docs/authority/authority_hashes.json
+++ b/docs/authority/authority_hashes.json
@@ -1,6 +1,6 @@
 {
   "manifest_version": "1.0",
-  "generated_on": "2026-08-31",
+  "generated_on": "2026-09-02",
   "files": [
@@ -9,8 +9,8 @@
     {
       "path": "config/thresholds.v1.yaml",
-      "sha256": "dbfd20408169f4a379a0461d18eee1e137b537e2796b69715f144ee038330231",
-      "bytes": 3556
+      "sha256": "32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261",
+      "bytes": 3700
     },
```

Generated snapshot-manifest diff:

```diff
diff --git a/data/manifests/snapshot_manifest.json b/data/manifests/snapshot_manifest.json
index 3778f3c..44eed34 100644
--- a/data/manifests/snapshot_manifest.json
+++ b/data/manifests/snapshot_manifest.json
@@ -1,6 +1,6 @@
 {
   "manifest_version": "1.0",
-  "generated_on": "2026-08-31",
+  "generated_on": "2026-09-02",
   "policy": "Golden cases and synthetic scenarios run only against pinned files in this manifest.",
   "files": [
```

No snapshot path, hash, byte count, policy or version changed.

Observed `sha256sum`:

```text
32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261  config/thresholds.v1.yaml
```

Generated JSON entry:

```text
{'path': 'config/thresholds.v1.yaml', 'sha256': '32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261', 'bytes': 3700}
```

The Manifest §11 row was copied from that JSON entry.

Integrity after regeneration:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

## Task 9 pre-review local validation

The detached final-validation script exited 0.

`make ci`:

```text
PROHIBITED FILE SCAN PASS (116 tracked files)
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
INTEGRITY PASS
136 passed, 1 warning in 0.30s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Clean pip virtual-environment gates:

```text
editable development install: PASS
PROHIBITED FILE SCAN PASS (116 tracked files)
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
compileall: PASS
node --check: PASS
INTEGRITY PASS
136 passed, 1 warning in 0.22s
SMOKE PASS
```

Docker:

```text
docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s02-local .
exit 0
image exported and tagged industrial-opportunity-resolution-mvp:s02-local
```

Focused boundary/rule confirmation after final validation:

```text
58 passed in 0.03s
```

The warning in both pytest runs is the same pre-existing Starlette `httpx` test-client deprecation warning.
