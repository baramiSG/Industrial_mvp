# Governed graph projection and mirror runbook

## Boundary

`data/graph/` is the governed, offline source. Neo4j is an idempotently
rebuildable mirror used for fixed Cypher views; it is never a second source of
evidence. The graph contains public evidence and explicitly labelled Class-D
scenario elements only. The graph API module is mounted; ordinary opportunity computation remains artifact-backed and socket-free.

Every Python command in this runbook uses:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX=/tmp/ior-s16a-pyc
export PYTHONPATH=src
export UV_OFFLINE=1
```

Do not source `.env` for local Compose, CI, ordinary tests, artifact builds or
reconstruction.

## Pinned local service

- image:
  `neo4j:5.26.30@sha256:037cf5756f0135cbfd66b739b6df7c7c4bb100f9ce11602f6f9538e17e02c74d`;
- container: `industrial-mvp-neo4j`;
- host ports: Browser 7475, Bolt 7688;
- dedicated network: `industrial-mvp-net`;
- dedicated Compose volume: `industrial-mvp-neo4j-data`;
- generated credential: `.secrets/neo4j_auth.txt`, mode 0600, ignored by Git;
- environment-variable name: `NEO4J_AUTH_FILE`.

Local Compose bind mounts preserve the host owner of the mode-0600 source,
which the image's uid 7474 cannot read directly. The root entrypoint therefore
copies the bind-mounted source into an in-container tmpfs as mode 0400 owned by
uid/gid 7474, keeps `NEO4J_AUTH_FILE=/run/secrets/neo4j_auth`, and then executes
the vendor entrypoint. No credential is placed in Compose YAML, an image layer
or command output.

## Artifact workflow

```bash
make graph-build
make graph-validate
```

Two builds from identical governed inputs must produce the same
`projection_id` and bytes. `python -m ior_mvp.graph build --check` compares a
fresh build with the current artifact without writing.

Scenario contract 2.1.0 permits a complete Class-D `shared_enabler` declaration with an explicit route-1–7 valuation reference. Phase one projects only declared evidence, validates scenario membership and valuation provenance, and injects branch-qualified inputs before engine outputs are projected. The governed aluminium pair computes UnlockValue 35.28 M SAR but remains blocked by fully resolving routes 6/4. A test-only pair proves route 8 can win honestly at 178 M SAR.

After approved code/config/scenario edits and before the separately controlled graph generation, the persisted pointer is expected to differ from a fresh build. Preserve that failure; do not overwrite `data/graph/**`, regenerate manifests or start a mirror until the later operation packet binds the literal projection output.

Reconstruction is part of:

```bash
python scripts/reconstruct_snapshot.py --all
```

and must print `GRAPH RECONSTRUCTION PASS`.

## Local Compose workflow

```bash
make graph-up
make graph-load
make graph-load
make graph-verify
make graph-tests
make graph-down
make graph-unavailable-test
```

The second load must report 0 nodes and 0 relationships created. Verification
requires exact label/type counts, one projection id, complete provenance and
zero public/Class-D partition violations.

`make graph-gate` performs the same sequence. It explicitly clears only the
dedicated local test mirror with
`--confirm-clear industrial-mvp-neo4j`, stops on the first failed command, and
stops the service on exit. This clear is test-gate setup, not a general reset
operation.

## Credential and volume lifecycle

`make graph-credential` creates the credential only when absent and prints
only `CREDENTIAL_CREATED` or `CREDENTIAL_PRESENT`. Never display, copy into a
log or commit the file.

Neo4j initial authentication is applied only to a new `/data` volume. Changing
the host credential does not reseed an existing volume. Credential rotation or
the future S21 `demo-reset` therefore requires an explicit, documented
recreation of this project's dedicated volume. S16a provides no implicit
volume deletion.

Loading a different `projection_id` into a non-empty mirror is refused before
any constraint, node or relationship write. An operator must first use the
target-scoped clear command:

```bash
python -m ior_mvp.graph clear \
  --target compose \
  --confirm-clear industrial-mvp-neo4j
```

## CI target

The `graph-gates` job starts a clean digest-pinned service container and
generates a run-scoped credential expression. `resolve_target("ci")` ignores
any inherited URI and uses `bolt://localhost:7688`. The job rebuild-checks the
artifact, loads twice, verifies, runs `graph_tests/`, stops the service and
runs the `graph_unavailable` tests. The designated job may not convert service
failure into a skip.

The application Docker image intentionally excludes the optional `neo4j`
package; CI proves that boundary.

## Aura operator target

Aura is the later owner-led deployment verification target under OR-7, not an
ordinary test target. Connection values exist only under these variable names:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
NEO4J_DATABASE
AURA_INSTANCEID
AURA_INSTANCENAME
```

`load --target aura` and `verify --target aura` require an explicit
`--confirm-instance`. Before driver creation, the value must equal both
`AURA_INSTANCEID` and the `neo4j+s` host prefix. Any mismatch exits with safety
code 3. A clear additionally requires
`--confirm-clear <exact-instance-id>`.

Only the recorded operator command may source `.env`, in-shell, without
printing values. Ordinary `tests/`, `graph_tests/`, `make ci` and hosted CI
must never receive Aura variables. Verification reports contain target and
instance identity only, never URI, username or password.

## Fail-closed states

The graph API returns HTTP 200 with `graph_status=GRAPH_UNAVAILABLE`, empty
nodes/edges and one of:

```text
NOT_CONFIGURED
DRIVER_NOT_INSTALLED
CONNECTION_FAILED
INSTANCE_MISMATCH
PROJECTION_MISMATCH
```

The fixed bilingual catalogue remains available. No live-view failure falls
back silently to artifact rows. A missing or corrupt canonical artifact returns
sanitized HTTP 422 `GRAPH_ARTIFACT_INTEGRITY_ERROR`; query-time connection or
driver failures after a successful status check return the same typed
unavailable shape. The default test-suite `OfflineGuardViolation` and
unexpected programming exceptions propagate rather than being translated.
