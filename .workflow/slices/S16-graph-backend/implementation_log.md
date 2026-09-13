# S16a implementation log — implementer-sol slot 1

## 2026-09-13T03:17Z — Orientation and T0 preparation preflight

- Seat/persona: `implementer-sol`, senior graph-data and decision-systems engineer, using the data-engineering discipline.
- Data classification: `confidential_demo` — governed public evidence plus explicitly labelled Class-D synthetic scenarios; no restricted or personal data is introduced.
- Worktree: `/home/barami/projects/ior-worktrees/s16a`.
- Branch: `slice/s16a-graph-projection-provisioning-loader`.
- Base/HEAD: `1289e31e50c1d835760f6943e697d6d537ac0a18`.
- Approved plan SHA-256: `7e888e7a9b04d45579bfe799113a39066d4ea39e274aa2ceb5f573e0770d1b8d` — MATCH.
- Index: empty. Initial untracked records were only `.workflow/slices/S16-graph-backend/{plan.md,plan_review.md}`.
- Connection environment names `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `NEO4J_AUTH_FILE`, `AURA_INSTANCEID`, `AURA_INSTANCENAME`, `IOR_GRAPH_TARGET`, and `IOR_GRAPH_AURA_OPERATOR`: all ABSENT.
- `.env` was not read or sourced. No Aura connection was attempted.
- Authority read: `AGENTS.md`; Manifest §§7, 10, 11; authoritative methodology DOCX §§8.2–8.3; Core 03/04/06/07/09; S16 plan/reviews/rulings; SLICE_GRAPH S16/S17/§9; five control documents; route-8 and route-8 consumer code paths.
- `docs/project/` is not present on this branch. The approved project overlay used here is `docs/milestones/v0.3.0/{GAP_ANALYSIS,SLICE_GRAPH}.md`, as cited by the approved plan and ADR-010.
- Preparation boundary: S14b is not present on this base. This child intentionally projects the two current PublicSnapshot 2.1.0 files and two current scenario 2.0.0 files, then stops at `PREP_HANDOFF_PENDING_M16` before merged-interface integration or manifest generation.

Commands were printed before execution by the shell trace. Every Python command used:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONPYCACHEPREFIX=/tmp/ior-s16a-pyc
PATH=.venv/bin:$PATH
PYTHONPATH=src
UV_OFFLINE=1
```

Observed T0 evidence:

- Baseline integrity: `INTEGRITY PASS`.
- Baseline scenario gate: `SCENARIO VALIDATION PASS (2 scenarios)`.
- Baseline reconstruction: `CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)`; `RECONSTRUCTION PASS (4 snapshots, 34 artifacts)`; `DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)`; `ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)`; `SCREENING RECONSTRUCTION PASS (1 snapshots)`.
- Baseline visual manifest: `VISUAL_MANIFEST_OK 56`.
- Baseline smoke: `SMOKE PASS`.
- Baseline tests: `2416 passed, 1 warning in 49.66s`.
- Offline lock proof: an initial scratch harness encoded `dev` as a dependency group and was rejected before the requested sync; this was a harness setup error, not a Neo4j resolution failure. The corrected `/tmp` project used optional extras and, with `UV_OFFLINE=1`, locked and synced `neo4j==5.28.4` plus `pytz==2026.3.post1` on Python `3.12.13` and `3.14.6`: `LOCK_RESOLVES_3_12_AND_3_14`.
- Network fetched for lock resolution: none.
- Local image: `neo4j:5.26.30` repo digest `sha256:037cf5756f0135cbfd66b739b6df7c7c4bb100f9ce11602f6f9538e17e02c74d`.
- Image command: `/var/lib/neo4j/bin/cypher-shell`.
- Ports: `PORTS_FREE 7475 7688`.
- Stop conditions reached: none.

## 2026-09-13T04:05Z — Development projection cleanup ledger

Before deleting pre-handoff development-only projections, their content hashes
were recorded as required by ADR-023 recovery:

```text
1e8e93950486 projection a111335f8bdd0216c2514ab54751c0176ec91533183a468ccbe986ce9eb38095
1e8e93950486 manifest   ec0b04c160aa25d0072919c392764a305fd136ff67ba7c8602de95aa6fb0e158
5244f00cc4f9 projection de3fb67f203ad60e1ed3a46f31ba98d66cebeecc0b810e66711e9dc81691369f
5244f00cc4f9 manifest   08a983cf5eba237d1564c6e7164ed6bbf3650540fdeb560c12afd06fc1ee365f
531ca332926b projection 5c39f43e64907324bc16af8cbffebe894891b7c31c9fc15228e34d1f00171513
531ca332926b manifest   5feee9c95e2a8aea412bf17518406917abcca9d7faaa8c2af61a669ec45a1c4f
ae814afa058e projection b24174b96518895e7a3cdbc8af401b486a71e56b7de83c8c5b8ab2710dbef168
ae814afa058e manifest   e2aa2daea574974afca1df8000b0bd084df5d28f0d3c30d7c1a838cad817ed59
dc6299798865 projection e51287ef6da280ba0e63024cacc6dbfc89759765d09247110185eb88a39294c9
dc6299798865 manifest   d6e10d34869b86b05b3e42eabb42c0d49dcc4eddf16a4d28ad367609f3c8ead3
```

These identities were produced while source contracts were still changing
test-first. None was committed or manifested. Only the final reconstruction-
passing projection is retained in the candidate.

## 2026-09-13T03:45Z — T1 graph projection artifact

- RED first: the 27 approved T1 tests were created before `ior_mvp.graph` existed. Collection failed in all three files with `ModuleNotFoundError: No module named 'ior_mvp.graph'`.
- GREEN: added the governed 19-label/15-edge model, total v1→v2 mapping, deterministic ids, evidence-layer projection, derived engine-output projection, canonical artifact validation/write/load, repository and build CLI.
- The base projection consumes the two committed PublicSnapshot 2.1.0 records, two scenario 2.0.0 records, five CaseBriefs (built deterministically in memory), both entity artifacts, the current screening snapshot, tariff attempt records, and their governed dependencies. No unmerged s14b artifact was copied into this worktree.
- The first two repository builds were byte-identical and idempotently reused the same write-once projection:
  `GRAPH-SAU-2026-09-12-be973635c309`, 331 nodes, 367 edges.
- `GRAPH VALIDATION PASS` observed for that identity.
- Independent `/tmp` builds compared recursively equal: `GRAPH_BUILD_DETERMINISTIC`.
- The first threshold scan correctly flagged a comparison to route-code literal `5`. The implementation now imports the governed `BROWNFIELD_ROUTE_CODE`; the rerun reports `THRESHOLD LITERAL SCAN PASS (86 Python files; 23 configured numeric values)`.
- GREEN suite: `27 passed in 3.40s`.
- Frozen public/synthetic/golden/browser roots and top-level `src/ior_mvp/*.py` were not edited.
- Stop conditions reached: none.

## 2026-09-13T04:18Z — T2 feed, loader, fail-closed service and API

- RED: engine-feed, loader/service and API tests failed collection because
  `graph.engine_feed`, `graph.loader` and `graph.api` did not exist.
- GREEN: fixed artifact readers for adjacency, route blocking,
  evidence-to-change and shared-enabler queues; Cypher 5 templates with
  deterministic ordering; primitive property codec; Aura-safe target
  resolution; idempotent loader/verify/clear/wait; fail-closed GraphService;
  and the unmounted bilingual `/api/graph` router.
- Reviewer advisories applied: loopback targets ignore inherited URI; ordinary
  graph tests reject Aura-shaped URI state; Neo4j property maps contain only
  primitives/homogeneous primitive arrays; indexes are emitted per label; all
  shared-enabler dependents are ordered before aggregation; all 19 uniqueness
  constraints are created even when a label has no nodes.
- Branch-specific evidence-link relationships initially collided between
  public and simulated derivations. The failing combined T1/T2 run traced the
  collision to a key discriminator missing mode/scenario; the corrected key is
  deterministic and the combined suite passed 57 tests.
- T2 focused GREEN: 30 tests, one existing Starlette/httpx deprecation warning.
- Runtime import proof: `RUNTIME_IMPORT_BOUNDARY_OK`; importing
  `ior_mvp.app` imports neither `neo4j` nor acquisition transport.

## 2026-09-13T04:18Z — T3 Compose and live Cypher gate

- Live RED: nine graph tests stopped on
  `NEO4J_AUTH_FILE_UNAVAILABLE` before provisioning.
- Credential and scanner RED→GREEN: mode-0600 create-once credential,
  state-only output, `.secrets/` prohibited-path rule with the committed
  example exception, and candidate secret scan.
- First Compose startup timed out after 180 seconds. Sanitized container logs
  said the secret was unreadable. Boundary probes established the exact cause:
  the host bind was mode 0600 uid/gid 1000 while the image runtime user is
  uid/gid 7474. The corrected Compose entrypoint stages a mode-0400
  uid/gid-7474 copy into tmpfs, preserves
  `NEO4J_AUTH_FILE=/run/secrets/neo4j_auth`, and then executes the vendor
  entrypoint. Rerun: `GRAPH READY (compose)`.
- First live load: 355 nodes / 407 relationships; second load 0/0; verify
  equal. Subsequent model completion added CustomerSegment and Standard
  elements; final counts are recorded below.
- The first Make graph-gate exposed two valid fail-closed defects: verification
  detected stale prior-projection rows, but the shell recipe continued because
  it lacked `set -e`. RED tests now require read-before-write projection-id
  refusal and Make fail-fast plus an explicit target-scoped test clear.
  Corrected gate stops on first failure and refuses a different live
  projection before any write.
- Stopped-service latency RED was 34.17 seconds because driver retry backoff
  remained enabled. Graph-only connection/acquisition timeouts of two seconds
  and zero transaction retries reduced the proof to 0.50 seconds.
- Final live result for retained projection `941efbdf1e4a`: first load
  359/413, second load 0/0, exact verify, 8 live tests passed, Aura operator
  test skipped `AURA_OPERATOR_ONLY`, UnlockValue live test skipped
  `NO_UNLOCKED_BY_EDGES_IN_S16A`, then 2/2 stopped-service tests passed and
  `GRAPH_UNAVAILABLE_OK`. The service is stopped.

## 2026-09-13T04:18Z — T4 dependency and hosted-CI contract

- Worktree lock generation ran exactly once with `UV_OFFLINE=1`.
  `neo4j==5.28.4` and `pytz==2026.3.post1` were added.
- Locked sync passed on Python 3.12.13 and 3.14.6:
  `LOCK_RESOLVES_3_12_AND_3_14`. Network fetched: none.
- Added the optional `graph` extra (`neo4j>=5.28,<6`) and the digest-pinned
  `graph-gates` service job with a run-scoped credential, build check, double
  load, verification, live suite, service stop and unavailable suite.
- Existing runtime Dockerfile bytes remain unchanged; the Docker job now
  asserts the application image contains no optional Neo4j driver.
- CI YAML and CI/Make contract tests pass. Availability of
  `${{ job.services.neo4j.id }}` remains a hosted-run observation for the later
  delivery phase; no hosted CI was run in preparation.

## 2026-09-13T04:18Z — T5 authority text, reconstruction and records

- RED: the S16a Core contract test found no graph runtime/v2 vocabulary; the
  manifest-root and graph-reconstruction tests found no graph integration.
- GREEN: Core 02 maps every new domain function; Core 03 §13 defines the
  artifact/mirror/fail-closed boundary; Core 04 §8 v2 defines 19 labels,
  15 edges, total v1→v2 mapping, provenance, partition and artifact; Core 09
  §2.8/TL-09 10–12/Gate I defines offline and live proof.
- ADR-023 records decisions and the local secret/startup/latency incidents.
  KL-104…KL-109 record tariff, absent public graph facts, out-of-scope
  portfolio analytics, no S16a enabler, unmounted API and OR-7 Aura scope.
- `scripts/build_manifests.py` now knows the graph root and graph-view
  catalogue, but was never executed. Manifest run count remains **0**.
- A RED regression exposed that using generated `authority_hashes.json` as a
  graph input would make the later single manifest run circular. The graph now
  hashes the live methodology/Core/config bytes directly and excludes
  generated manifests from its inputs. This preserves both reproducibility
  and the one-run integration gate; the derivation is recorded in Core 04 and
  ADR-023.
- Final no-manifest reconstruction:
  `GRAPH RECONSTRUCTION PASS (1 projections, 359 nodes, 413 edges)` plus all
  pre-existing reconstruction PASS lines.

## 2026-09-13T04:18Z — Preparation handoff state

- Retained projection: `GRAPH-SAU-2026-09-12-941efbdf1e4a`.
- Nodes: 359. Present labels:
  Application 9; Capability 137; Certification 1; Company 10;
  CustomerSegment 2; Decision 9; Evidence 75; Intervention 81; Plant 5;
  Process 7; Product 7; ProductionLine 2; Scenario 2; Specification 9;
  Standard 2; TariffLine 1. Equipment, Input and Technology are honestly zero.
- Edges: 413. Present types:
  ADJACENT_TO 9; CERTIFIED_TO 2; CONSTRAINED_BY 46; DEPENDS_ON 81;
  HAS_CAPABILITY 137; HAS_LINE 2; PRODUCED_BY 9; QUALIFIED_FOR 2;
  REQUIRES_SPECIFICATION 18; SUPPORTED_BY_EVIDENCE 85; USED_IN 9;
  USES_PROCESS 13. CLASSIFIED_AS, REQUIRES_INPUT and UNLOCKED_BY are honestly
  zero.
- Provenance: all five mandatory properties on 100% of nodes and edges.
- Final default test suite: 2492 passed, one existing Starlette/httpx warning.
- Full no-manifest reconstruction: PASS. Smoke: PASS. Frozen outcomes: PASS.
  Visual manifest: 56 entries, unchanged. Threshold and prohibited-file
  scanners: PASS. Candidate scan: 62 changed/untracked files, zero findings.
- Expected pending gate: `verify_integrity.py` and `make ci` stop at the four
  changed Core hashes because the brief forbids the manifest run. `make ci`
  first completed the graph gate, then stopped at integrity with exit 2.
  Generated manifest files and Manifest §11 remain byte-identical to base.
- Frozen public/synthetic/golden/browser roots, every existing config,
  every top-level `src/ior_mvp/*.py`, Dockerfile, Core 05/06/07/08,
  methodology DOCX, smoke/final-acceptance scripts and manifest files are
  byte-identical to base.
- Index empty; no commit, stage, rebase, checkout, merge, pull or push.
- `.env` never read or sourced; all Aura/Neo4j connection variables absent at
  handoff; no Aura connection attempted.
- Additional superseded-development hashes before removal:
  `729fe72e5445` projection
  `b20f51f5be31374388a556aebff0e6526d81b296b570cff5a35b806883adfae5`,
  manifest
  `ea5732920342915db4f5c19f8599f381fa64b2593619220aa0f08f94910568d7`;
  `910d086ba936` projection
  `ec33dcd417c066ab19c481cbd37639c5c60026833de298ea6d00ee1fbe477ed2`,
  manifest
  `b763a2f716114fdd89bc535942d8262e65f73d182e6575a3c95676c5425d8584`.
  Only the retained projection has files in `data/graph/projections/`.
- State: `PREP_HANDOFF_PENDING_M16`.

## 2026-09-13T04:20Z — Muhasib candidate identity

- Re-read the implementer brief, standing rules and Muhasib checklist.
- Product candidate identity excludes slice logs and the pre-existing
  plan/review mirrors:
  `b5f246d1f609dea0ca0cd21eee6d812e1f265092b58c9fb0a3d7088975f706a4`
  across 58 files, base
  `1289e31e50c1d835760f6943e697d6d537ac0a18`.
- Fresh `build --check`, offline `uv lock --check`, `git diff --check`,
  candidate secret scan and IDE lint scan all passed.
- Generated credential mode is 0600 and the path is ignored. The service state
  remains `exited`.
- Scope/authority assumption disclosed: the direct live-authority input hash
  replaces the plan's generated-manifest hash wording because the latter would
  force a graph→manifest→graph cycle and a prohibited second manifest run.
  Core 04 and ADR-023 record the derivation for owner/reviewer scrutiny.
- This implementer does not approve the candidate. Independent review,
  owner-lead WIP/rebase onto M16, the single manifest run, portability,
  CI-equivalent committed scratch proof, hosted CI, Aura operator verification
  and delivery remain outside this preparation handoff.

## 2026-09-13T10:04Z — Owner W1 EOF formatting correction

- Removed only the extra terminal blank line from each of the 32 owner-listed
  newly added graph/docs/test files, preserving exactly one terminal LF.
- This was a pre-commit formatting-only correction. No git-state operation,
  dependency, behavior, data, manifest, credential or secret-file change was
  made; the implementation log remains unstaged.

## 2026-09-13 — OD-19 M16 content-conflict resolution

- Resolved only the six owner-identified content conflicts under OD-19:
  `Makefile` retains the complete S15 selection and S16 graph target sets;
  Core 02 retains the three S15 mapping rows followed by all seven graph rows;
  `reconstruct_snapshot.py` retains both reconstruction functions and both
  calls; the limitations retain KL-104…KL-117 and add the unchanged S16 facts
  as KL-118…KL-123; ADR-022/ADR-023 remain the M16 records and the graph block
  is ADR-024; the integrity module retains the S14b, S15a and S16 tests with
  only the S16 identifier assertions changed to ADR-024/KL-118.
- Exact conflict-marker scan returned no matches. The remaining non-log,
  non-data ADR-023/KL-104…KL-109 references were inspected and are historical
  S14b/S15a references, so they were not changed. `git diff HEAD --check`
  exited zero with no output.
- Focused combined run: 50 passed, 1 failed in 9.55s. The isolated selection
  reconstruction/Makefile/main-wiring set then passed 3 tests in 1.85s. The
  isolated graph reconstruction test still fails with
  `GRAPH RECONSTRUCTION FAIL:
  GRAPH-SAU-2026-09-12-941efbdf1e4a byte mismatch`.
- The graph failure is the expected pre-regeneration boundary after M16 added
  governed S14b/S15a inputs. This content-only instruction prohibits changing
  unconflicted `data/graph/**`; OD-18 requires the graph projection to be
  rebuilt against M16 after the owner lead completes this rebase and before
  manifest generation. No network, Aura, `.env`, credential or secret-file
  access occurred, and no git-state operation was performed.

## 2026-09-13T10:24Z — M16 integration and final manifest authorization

- Verified W1' `6567216ae5c5b95d994381499d48d590df6b1324` has M16
  `b81a7bd30261969c455915659eb083f35101c38d` as its parent. OD-19's six
  additive conflict resolutions are now the integration delta recorded in
  ADR-024: Make target union; Core 02 row union; both reconstruction functions
  and calls; KL-104…KL-117 preserved with graph KL-118…KL-123; ADR-022/023
  preserved with graph ADR-024; S14b/S15a/S16 integrity tests retained.
- M16 interfaces: seven public snapshots, seven scenarios, nine CaseBriefs,
  two case-selection records and 76 visual-manifest entries. Scenario
  validation passed seven; recorded selection reconstruction passed two;
  case reconstruction passed five committed snapshots from nine briefs;
  57 focused S14/S15 selection/case tests passed.
- The retained pre-M16 projection
  `GRAPH-SAU-2026-09-12-941efbdf1e4a` failed byte reconstruction as expected.
  Its two files remain byte-identical. The integrated, write-once projection
  is `GRAPH-SAU-2026-09-12-3ce241f08f7a`: 740 nodes, 835 edges and 219 hashed
  inputs, with zero missing mandatory provenance fields. Relative to the
  retained projection this is +381 nodes, +422 edges, 22 added input paths,
  zero removed paths and 34 changed common-path hashes.
- Two independent temporary builds were byte-identical and matched the current
  artifact. Manifest-free reconstruction passed all stages, including
  `CASE SELECTION RECONSTRUCTION PASS (2 records)` and
  `GRAPH RECONSTRUCTION PASS (1 projections, 740 nodes, 835 edges)`.
  Default reconstruction then failed closed with exit 2 because
  `data/graph/current.json` was not yet in the M16 snapshot manifest.
- The local graph gate used only Compose service
  `industrial-mvp-neo4j` on 7475/7688. First load created 740/835; second load
  created 0/0; verification reported 740/835; live equality/constraint/
  provenance tests passed 8 with two governed skips; stopped-service tests
  passed 2 and emitted `GRAPH_UNAVAILABLE_OK`. The service is exited and both
  ports are free; only `industrial-mvp-net` and
  `industrial-mvp-neo4j-data` were used.
- Pre-generation regression: 2676 tests passed with one existing
  Starlette/httpx warning; focused graph/selection contracts passed 89;
  smoke, threshold scan, prohibited-file scan, runtime import boundary and
  frozen outcomes passed. Integrity fails only on the four authorized S16
  Core hashes, and manifest-checked graph reconstruction fails only on the
  not-yet-generated graph rows.
- Direct live-authority cycle proof: the current projection contains the
  methodology DOCX, all nine live Core files and live versioned configs, while
  neither generated manifest is among its 219 inputs. A post-generation
  `build --check` must retain the same id and bytes.
- All S16 governed text and the integrated graph artifact are now final.
  Under ADR-024 and OD-18/OD-19, exactly one S16a
  `scripts/build_manifests.py` invocation is authorized next. No second run is
  authorized.

## 2026-09-13T10:59Z — Final integrated S16a candidate

- The sole manifest invocation ran at `2026-09-13T10:24:10Z` and exited zero.
  Snapshot rows changed 698→703 through five graph-only additions with zero
  changed/removed prior rows; authority rows changed 19→20 by adding
  `config/graph_views.v1.yaml` and changing only Core 02/03/04/09. Machine
  hashes are `722d3641…` and `d951a1be…`; the §11 human table and immediate
  integrity oracle passed. No second manifest invocation occurred.
- Post-generation `graph build --check` retained
  `GRAPH-SAU-2026-09-12-3ce241f08f7a`, proving generated manifests are not
  graph inputs. Full reconstruction passed Case 5/9, Graph 1/740/835,
  acquired snapshots 5/42, documents 26/26, entities 3/46, screening 1 and
  selections 2.
- The first post-generation full suite exposed two valid test-contract
  failures: the S08/S11 snapshot-manifest partition allowlists had no
  `data/graph/` governed partition. RED was 2 failed/2674 passed. The smallest
  test-only correction adds the exact `data/graph/` prefix plus a
  `data/graph-other/` negative control; focused GREEN was 3 passed. No
  manifest or production file changed for this correction. Final direct
  pytest passed 2676 with one existing warning.
- Post-manifest graph gate passed again (740/835 then 0/0; verify 740/835;
  live 8 passed/2 governed skips; unavailable 2 passed). Local `make ci`
  exited zero: integrity, seven-scenario validation, all reconstruction,
  2676 pytest, smoke, 339 functional browser nodes and four visual nodes.
- The final different-path copy passed integrity and every reconstruction
  stage. The exact 14-file delta was committed only in scratch as
  `72e8125fa1f6c365ec5055a05994590e367eec60` over W1'. Its first `CI=1 make
  ci` used host-default Python 3.14, passed the graph gate/reconstruction/2676
  tests and then stopped because the offline cache lacks the CPython 3.14
  Pillow wheel. The same exact scratch commit was rerun under the plan's
  Python 3.12.13 environment and exited zero with 2676 + 339 + 4.
- An optional exact Dockerfile build with `--network=none` stopped at its
  PEP-517 build-isolation request because `setuptools>=69` was not present
  inside the image cache. Network remained disabled. This is recorded as an
  unperformed current-image rebuild, not a passing proof; the Dockerfile and
  package-extra contract tests remain green and `make ci` does not build the
  application image.
- IAC-6 canonical identity is
  `040d442d0b140b99715ff4e9c2198d5c839779f2729afa87662699de35a43d14`
  across 14 uncommitted files, base W1'
  `6567216ae5c5b95d994381499d48d590df6b1324`, M16 parent
  `b81a7bd30261969c455915659eb083f35101c38d`, `wip_commits=[W1']`.
  The full reviewer/security scope contains 66 files; `.secrets/**` was
  excluded and zero credential/private-key token findings were found.
- Data classification remains `confidential_demo`: public evidence and
  deterministic derived outputs plus visibly labelled Class-D synthetic
  subgraphs; no personal/restricted client data or credential value. The
  generated credential remains ignored mode 0600 and was not read, printed,
  staged or copied by the implementer; the scratch used an ignored symlink
  into the same permitted Compose secret handoff.
- Final service state is stopped, ports 7475/7688 are free, and only the named
  `industrial-mvp-neo4j` container, `industrial-mvp-net` network and
  `industrial-mvp-neo4j-data` volume were used. Aura environment-name count
  is zero; no Aura connection and no `.env` read occurred.
- Worktree index and whitespace checks pass. Candidate remains uncommitted and
  unstaged for independent review. State:
  `FINAL_HANDOFF_PENDING_INDEPENDENT_REVIEW`.

## 2026-09-13T11:18Z — OD-20 Compose collision correction

- Owner ruling OD-20 classified the fixed-container-name collision as a valid
  operational defect: the old `graph-down` stopped the service but retained
  the `industrial-mvp-neo4j` container, allowing a scratch/current Compose
  project collision.
- TDD RED extended
  `test_graph_gate_stops_on_failure_and_clears_only_with_confirmation` to
  require `docker compose down --remove-orphans` and prohibit both
  `--volumes` and `-v`. It failed exactly on the old
  `docker compose stop industrial-mvp-neo4j` recipe: 1 failed, exit 1.
- The only product correction changes the `graph-down` Makefile recipe to
  `docker compose down --remove-orphans`. Focused GREEN passed 1 test; the
  complete integrity-contract module passed 33 tests.
- `make graph-gate` passed: first load 740 nodes/835 relationships; second
  load 0/0; verify 740/835; live suite 8 passed with the two governed skips;
  stopped-service suite 2 passed and emitted `GRAPH_UNAVAILABLE_OK`.
- Cleanup proof after the gate found zero container ids with the fixed name or
  graph-service Compose label. `industrial-mvp-neo4j-data` remained present.
  All 20 other container records retained the same id/state/health tuple,
  including running healthy `mol-executive-intelligence-postgres-1`.
- No credential value was displayed. The approved Compose flow reported only
  `CREDENTIAL_PRESENT` and the ignored path name. No `.env`, secret-file
  content or Aura connection was accessed.
- Integrity passed. The snapshot manifest, machine authority manifest and §11
  mirror remained byte-identical at `722d3641…`, `d951a1be…` and
  `cb06cc00…`; no manifest command ran. Whitespace check passed.
- The plan-exact IAC-6 identity recomputed to
  `79f469dc48f56d774de4faafb459a95e40ec441e892b3601de9080a9b36ad487`
  across 15 uncommitted candidate files, with W1'
  `6567216ae5c5b95d994381499d48d590df6b1324` as `base` and sole
  `wip_commits` entry, and M16
  `b81a7bd30261969c455915659eb083f35101c38d` as `wip_parent`. The index
  remains empty; independent re-review is pending.
