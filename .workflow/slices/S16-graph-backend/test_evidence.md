# S16a test evidence — implementer-sol slot 1

## 2026-09-13T03:17Z — T0 baseline

Environment for every Python invocation:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s16a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src UV_OFFLINE=1
```

Commands and observed results:

```text
$ sha256sum .autonomous-workflow/plans/s16-graph-backend/cycle-1/plan-1-s16.json
7e888e7a9b04d45579bfe799113a39066d4ea39e274aa2ceb5f573e0770d1b8d

$ git branch --show-current && git rev-parse HEAD && git diff --cached --quiet
slice/s16a-graph-projection-provisioning-loader
1289e31e50c1d835760f6943e697d6d537ac0a18
INDEX_EMPTY_PASS

$ .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS

$ .venv/bin/python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)

$ .venv/bin/python scripts/reconstruct_snapshot.py --all
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)

$ .venv/bin/python -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']))"
VISUAL_MANIFEST_OK 56

$ .venv/bin/python scripts/demo_smoke.py
SMOKE PASS

$ .venv/bin/pytest -q -p no:cacheprovider
2416 passed, 1 warning in 49.66s
```

Offline scratch lock and sync:

```text
$ UV_OFFLINE=1 uv lock
$ UV_OFFLINE=1 UV_PROJECT_ENVIRONMENT=.venv-312 uv sync --locked --extra dev --extra graph --python 3.12
$ UV_OFFLINE=1 UV_PROJECT_ENVIRONMENT=.venv-314 uv sync --locked --extra dev --extra graph --python 3.14
LOCK_SYNC_3_12 3.12.13 5.28.4
LOCK_SYNC_3_14 3.14.6 5.28.4
LOCK_RESOLVES_3_12_AND_3_14
```

The first scratch attempt represented `dev` as a dependency group and stopped before the requested sync. The corrected optional-extra project passed fully offline. No package or index data was fetched.

Docker/image preflight:

```text
$ docker image inspect neo4j:5.26.30 --format '{{json .RepoDigests}} {{.Id}}'
["neo4j@sha256:037cf5756f0135cbfd66b739b6df7c7c4bb100f9ce11602f6f9538e17e02c74d"] sha256:037cf5756f0135cbfd66b739b6df7c7c4bb100f9ce11602f6f9538e17e02c74d

$ docker run --rm --network none --entrypoint sh neo4j:5.26.30 -c 'command -v cypher-shell'
/var/lib/neo4j/bin/cypher-shell

$ ss -ltn | rg ':(7475|7688)\s'
<no matches>
PORTS_FREE 7475 7688
```

No Aura environment variable was present; `.env` was not read; no Aura connection was attempted.

## 2026-09-13T03:45Z — T1 RED/GREEN

```text
$ .venv/bin/pytest -q -p no:cacheprovider tests/test_graph_model.py tests/test_graph_projection.py tests/test_graph_artifact.py
ERROR tests/test_graph_model.py
ERROR tests/test_graph_projection.py
ERROR tests/test_graph_artifact.py
ModuleNotFoundError: No module named 'ior_mvp.graph'
```

After the minimal model/projection/artifact implementation:

```text
$ .venv/bin/pytest -q -p no:cacheprovider tests/test_graph_model.py tests/test_graph_projection.py tests/test_graph_artifact.py
...........................                                              [100%]
27 passed in 3.40s

$ .venv/bin/python -m ior_mvp.graph build --out data/graph
GRAPH BUILD PASS (GRAPH-SAU-2026-09-12-be973635c309; 331 nodes; 367 edges)

$ .venv/bin/python -m ior_mvp.graph build --out data/graph
GRAPH BUILD PASS (GRAPH-SAU-2026-09-12-be973635c309; 331 nodes; 367 edges)

$ .venv/bin/python -m ior_mvp.graph validate
GRAPH VALIDATION PASS (GRAPH-SAU-2026-09-12-be973635c309; 331 nodes; 367 edges)

$ diff -r <temporary-build-a> <temporary-build-b>
<no differences>
GRAPH_BUILD_DETERMINISTIC
```

Scanner RED and correction:

```text
$ .venv/bin/python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN FAIL
- src/ior_mvp/graph/projection.py:911:5

$ .venv/bin/python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (86 Python files; 23 configured numeric values)
```

The flagged value was a route-code comparison, not a threshold. It now uses the governed `BROWNFIELD_ROUTE_CODE` constant rather than suppressing the scanner.

## 2026-09-13T04:18Z — T2–T5 RED/GREEN summary

T2 initial RED:

```text
ERROR tests/test_graph_engine_feed.py
ModuleNotFoundError: No module named 'ior_mvp.graph.engine_feed'
ERROR tests/test_graph_service_offline.py
ModuleNotFoundError: No module named 'ior_mvp.graph.loader'
ERROR tests/test_graph_api_offline.py
ModuleNotFoundError: No module named 'ior_mvp.graph.api'
```

T2 GREEN:

```text
$ pytest tests/test_graph_engine_feed.py tests/test_graph_service_offline.py tests/test_graph_api_offline.py tests/test_offline_guard.py
30 passed, 1 warning in 0.71s

$ pytest T1+T2 after branch-edge correction
57 passed, 1 warning in 4.12s

RUNTIME_IMPORT_BOUNDARY_OK
```

Additional safety RED→GREEN:

```text
credential CLI RED: invalid choices credential/load
credential CLI GREEN: 2 passed
secret scanner RED: .secrets/neo4j_auth.txt not rejected
secret scanner GREEN: 33 passed
stale projection / Make fail-fast RED: 2 failed
stale projection / Make fail-fast GREEN: 2 passed
stopped-service latency RED: 34.17096079897601 >= 5.0
stopped-service latency GREEN: 1 passed in 0.50s
CustomerSegment endpoint/projection RED: 2 failed
CustomerSegment endpoint/projection GREEN: 2 passed
Standard projection RED: no governed Standard nodes
Standard projection GREEN: 1 passed
generated-authority-manifest cycle RED: authority_hashes.json was an input
generated-authority-manifest cycle GREEN: 1 passed
```

T3 provisioning RED and root cause:

```text
$ IOR_GRAPH_TEST_EXPLICIT=1 IOR_GRAPH_TARGET=compose pytest graph_tests -m "graph and not graph_unavailable"
1 passed, 2 deselected, 9 errors
GraphSafetyError: NEO4J_AUTH_FILE_UNAVAILABLE

First startup:
GRAPH ERROR: Neo4j readiness timeout

Container log:
The secret file '/run/secrets/neo4j_auth' does not exist or is not readable.

Observed metadata:
host secret: mode 600 uid:gid 1000:1000
image runtime user: uid=7474 gid=7474
runtime-user probe: SECRET_NOT_READABLE

After tmpfs runtime-secret staging:
GRAPH READY (compose)
```

Final T3 live gate for retained projection:

```text
GRAPH CLEAR PASS (compose)
GRAPH LOAD PASS (compose; GRAPH-SAU-2026-09-12-941efbdf1e4a; created 359 nodes / 413 relationships)
GRAPH LOAD PASS (compose; GRAPH-SAU-2026-09-12-941efbdf1e4a; created 0 nodes / 0 relationships)
GRAPH VERIFY PASS (compose; GRAPH-SAU-2026-09-12-941efbdf1e4a; 359 nodes; 413 edges)
8 passed, 2 skipped, 2 deselected
SKIPPED AURA_OPERATOR_ONLY
SKIPPED NO_UNLOCKED_BY_EDGES_IN_S16A
2 passed, 10 deselected
GRAPH_UNAVAILABLE_OK
```

The Compose service was stopped after the gate.

T4 lock proof:

```text
$ UV_OFFLINE=1 uv lock
Added neo4j v5.28.4
Added pytz v2026.3.post1

LOCK_SYNC_3_12 3.12.13 5.28.4
LOCK_SYNC_3_14 3.14.6 5.28.4
LOCK_RESOLVES_3_12_AND_3_14
network fetched: none
```

T5 reconstruction and authority contracts:

```text
Core graph contract RED: missing Graph projection runtime
manifest/reconstruction RED: graph root and _reconstruct_graph absent

$ pytest focused T5 graph authority contracts
7 passed

$ python scripts/reconstruct_snapshot.py --all --no-check-manifest
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
GRAPH RECONSTRUCTION PASS (1 projections, 359 nodes, 413 edges)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

## 2026-09-13T04:18Z — Final preparation verification

```text
$ pytest -q -p no:cacheprovider
2492 passed, 1 warning in 52.41s

$ python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)

$ python scripts/demo_smoke.py
SMOKE PASS

$ uv run --locked --offline --extra dev --extra e2e --extra graph python -c <validate visual manifest>
VISUAL_MANIFEST_OK 56

$ python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (91 Python files; 23 configured numeric values)

$ python scripts/check_prohibited_files.py
PROHIBITED FILE SCAN PASS (1274 tracked files)

$ candidate changed/untracked scan
CANDIDATE_SECRET_SCAN_PASS 62 files

PROVENANCE_100_PERCENT
TOP_LEVEL_MODULES_BYTE_IDENTICAL_PASS
FROZEN_ROOTS_BYTE_IDENTICAL_PASS
EXISTING_CONFIG_BYTE_IDENTICAL_PASS
MANIFEST_FILES_UNCHANGED_PASS
INDEX_EMPTY_PASS
GDS_TOKENS_EXPECT_0_PASS
APOC_REQUIRED_PATHS_EXPECT_0_PASS
SERVICE_STATE exited
```

Expected pre-manifest status:

```text
$ python scripts/verify_integrity.py
INTEGRITY FAIL
- hash mismatch: Core 02
- hash mismatch: Core 03
- hash mismatch: Core 04
- hash mismatch: Core 09
EXPECTED_PRE_MANIFEST_INTEGRITY_PENDING exit=1

$ make ci
<graph gate completed successfully>
INTEGRITY FAIL (same four pending Core hashes)
MAKE_CI_EXPECTED_PRE_MANIFEST_STOP exit=2
```

No manifest command was run. This is the intended preparation boundary, not a
waived gate. State: `PREP_HANDOFF_PENDING_M16`.

```text
GRAPH BUILD PASS (GRAPH-SAU-2026-09-12-941efbdf1e4a; 359 nodes; 413 edges)
uv lock --check --offline: resolved 43 packages
git diff --check: PASS
IDE lint diagnostics: none
PREP_CANDIDATE_IDENTITY b5f246d1f609dea0ca0cd21eee6d812e1f265092b58c9fb0a3d7088975f706a4
PREP_CANDIDATE_FILE_COUNT 58
SECRET_MODE 600
GENERATED_SECRET_IGNORED_PASS
INDEX_EMPTY_PASS
```

## 2026-09-13T10:24Z — Integrated pre-generation gate

```text
W1_PRIME 6567216ae5c5b95d994381499d48d590df6b1324
M16_PARENT b81a7bd30261969c455915659eb083f35101c38d
PUBLIC_SNAPSHOTS 7
SCENARIOS 7
CASE_BRIEFS 9
CASE_SELECTION_RECONSTRUCTION PASS (2 records)
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
VISUAL_MANIFEST_OK 76
focused S14/S15 selection/case interfaces: 57 passed in 13.56s

GRAPH BUILD PASS (GRAPH-SAU-2026-09-12-3ce241f08f7a; 740 nodes; 835 edges)
GRAPH VALIDATION PASS (GRAPH-SAU-2026-09-12-3ce241f08f7a; 740 nodes; 835 edges)
GRAPH_BUILD_DETERMINISTIC
INPUT_COUNT 219
AUTHORITY_BASIS_SHA256 fbdd6610e10e223b13109afcb84e606261c376dc70091fb76f30d902cec9fbe0
PROVENANCE_NODE_MISSING 0
PROVENANCE_EDGE_MISSING 0
GENERATED_MANIFEST_INPUTS 0
graph/selection/Core focused contracts: 89 passed in 12.01s

GRAPH LOAD PASS (compose; GRAPH-SAU-2026-09-12-3ce241f08f7a;
created 740 nodes / 835 relationships)
GRAPH LOAD PASS (compose; GRAPH-SAU-2026-09-12-3ce241f08f7a;
created 0 nodes / 0 relationships)
GRAPH VERIFY PASS (compose; GRAPH-SAU-2026-09-12-3ce241f08f7a;
740 nodes; 835 edges)
live graph tests: 8 passed, 2 skipped, 2 deselected, 1 warning in 2.96s
unavailable tests: 2 passed, 10 deselected, 1 warning in 0.52s
GRAPH_UNAVAILABLE_OK
PORTS_FREE_AFTER_GATE_7475_7688
SERVICE_STATE exited

full pre-generation pytest: 2676 passed, 1 warning in 68.95s
THRESHOLD LITERAL SCAN PASS (91 Python files; 23 configured numeric values)
PROHIBITED FILE SCAN PASS (1420 tracked files)
RUNTIME_IMPORT_BOUNDARY_OK
FROZEN_OUTCOMES_OK
SMOKE PASS

manifest-free reconstruction:
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
GRAPH RECONSTRUCTION PASS (1 projections, 740 nodes, 835 edges)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
CASE SELECTION RECONSTRUCTION PASS (2 records)

default pre-manifest reconstruction:
GRAPH RECONSTRUCTION FAIL: manifest row missing for data/graph/current.json
PRE_MANIFEST_RECONSTRUCTION_EXIT 2

default pre-manifest integrity:
four authorized hash mismatches only: Core 02, Core 03, Core 04, Core 09
PRE_MANIFEST_INTEGRITY_EXIT 1
```

The retained projection `GRAPH-SAU-2026-09-12-941efbdf1e4a` remains
byte-identical: `manifest.json`
`b6af32cde2aef847c92b12e52246a8efc47c3fa97483a3a2b0241fdb0489dd29`
(227 bytes), `projection.json`
`795975c4b89bd4a4769da831a2f76917a5cc69075f2042597df51ed0b1c16f1e`
(844574 bytes). The integrated projection adds 381 nodes and 422 edges.

Manifest run count remains zero at this receipt. ADR-024 and OD-18/OD-19
authorize exactly one invocation after this pre-generation gate; no second
run is authorized.

## 2026-09-13T10:59Z — Post-generation and exact-candidate evidence

```text
MANIFEST_RUN_STARTED 2026-09-13T10:24:10Z
MANIFEST_RUN_ENDED 2026-09-13T10:24:10Z
INTEGRITY PASS

SNAPSHOT_ROWS 698 703
SNAPSHOT_ADDED 5
SNAPSHOT_REMOVED 0
SNAPSHOT_CHANGED 0
SNAPSHOT_MANIFEST_SHA256 722d364118df361cd5693dcc14da94b2b733c78065f718b8a015f912c3d5570d
AUTHORITY_ROWS 19 20
AUTHORITY_ADDED 1
config/graph_views.v1.yaml
AUTHORITY_REMOVED 0
AUTHORITY_CHANGED 4
docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md
docs/core/03_SYSTEM_ARCHITECTURE.md
docs/core/04_CANONICAL_DATA_MODEL.md
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
AUTHORITY_MANIFEST_SHA256 d951a1be51c057e504c3aac309c8594bedd014e1466f8f0921e26743002265ac

post-generation graph build --check:
GRAPH BUILD PASS (GRAPH-SAU-2026-09-12-3ce241f08f7a; 740 nodes; 835 edges)

post-generation reconstruction:
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
GRAPH RECONSTRUCTION PASS (1 projections, 740 nodes, 835 edges)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
CASE SELECTION RECONSTRUCTION PASS (2 records)

post-generation partition-contract RED:
2 failed, 2674 passed, 1 warning in 70.79s
failing tests:
test_s08_snapshot_manifest_retains_live_and_historical_public_rows
test_s11_snapshot_manifest_rejects_public_partition_leak
root cause: authorized data/graph rows missing from both exact-prefix allowlists

partition-contract GREEN after exact-prefix test-only correction:
3 passed in 0.09s
final direct pytest:
2676 passed, 1 warning in 67.49s

local make ci exit 0:
graph live 8 passed, 2 skipped, 2 deselected
graph unavailable 2 passed, 10 deselected
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
CASE / GRAPH / SNAPSHOT / DOCUMENT / ENTITY / SCREENING /
CASE SELECTION reconstruction PASS
2676 passed, 1 warning in 67.74s
SMOKE PASS
339 passed, 4 deselected in 525.39s
4 passed, 339 deselected in 57.82s

PORTABILITY_FINAL_CANDIDATE_PASS
ABSOLUTE_PATHS_EXPECT_0
UV_LOCK_OFFLINE_CHECK_PASS
STATE_JSON_VALID_PASS
integrity/CI/browser control contracts: 75 passed in 3.93s

exact scratch commit 72e8125fa1f6c365ec5055a05994590e367eec60
scratch parent 6567216ae5c5b95d994381499d48d590df6b1324
scratch staged file count before commit 14
scratch worktree clean after commit

CI=1 scratch attempt 1, Python 3.14.6:
graph gate PASS; reconstruction PASS; 2676 pytest PASS;
BROWSER PREFLIGHT STOP — offline cache lacks pillow 12.3.0 cp314 wheel
exit 2

CI=1 scratch attempt 2, Python 3.12.13, same commit:
graph gate PASS
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
all reconstruction stages PASS
2676 passed, 1 warning in 64.13s
SMOKE PASS
339 passed, 4 deselected in 518.22s
4 passed, 339 deselected in 57.49s
exit 0

optional docker build --network=none:
STOPPED — build-isolation setuptools>=69 absent from image cache; exit 1
network remained disabled; no current-image success claimed

CANDIDATE_IDENTITY 040d442d0b140b99715ff4e9c2198d5c839779f2729afa87662699de35a43d14
CANDIDATE_FILE_COUNT 14
CANDIDATE_BASE 6567216ae5c5b95d994381499d48d590df6b1324
CANDIDATE_WIP_PARENT b81a7bd30261969c455915659eb083f35101c38d
CANDIDATE_WIP_COMMITS 6567216ae5c5b95d994381499d48d590df6b1324
FULL_CANDIDATE_SCAN_FILE_COUNT 66
FULL_CANDIDATE_SECRET_FINDINGS 0
INDEX_EMPTY_PASS
WHITESPACE_CHECK_PASS
CONFLICT_MARKERS_EXPECT_0
GENERATED_SECRET_MODE_600
GENERATED_SECRET_IGNORED_PASS
AURA_CONNECTION_ENV_NAME_COUNT 0
PORTS_FREE_FINAL_7475_7688
```

Manifest invocation count for S16a is exactly one and exhausted. No second run
occurred after the partition-test correction because neither tests nor control
records are authority/snapshot manifest inputs.
