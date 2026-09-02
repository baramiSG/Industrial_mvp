# Development Guide

## Authority and data boundary

Development uses repository code, frozen public evidence, and explicitly synthetic Class-D fixtures. No API key or live industrial source is required. Never run the manifest generator outside an approved Authority Manifest §7 change. The active slice ADR and PR must identify the exact governed bytes, approval basis, sensitivity/golden proof, and permitted generated diff before one controlled run.

## Prerequisites

Use WSL or native Linux with Python 3.11 or newer, Git, Make, Node, and `uv`. Docker is required for image/runtime compatibility checks.

The Makefile defaults to `NODE ?= node`. If Node is user-scoped:

```bash
make NODE="$HOME/.local/node/bin/node" ci
```

The Makefile invokes `$(HOME)/.local/bin/uv` unless overridden:

```bash
make UV=uv ci
make UV=/path/to/uv ci
```

Do not edit shell startup files merely to run the build.

## Install uv without changing shell profiles

```bash
curl -LsSf https://astral.sh/uv/install.sh \
  | env UV_NO_MODIFY_PATH=1 sh
"$HOME/.local/bin/uv" --version
make uv-sync
```

## Local CI-equivalent gates

```bash
make ci
```

The target executes:

1. locked development-environment sync;
2. prohibited tracked-file and deterministic credential-pattern scan;
3. configured-threshold comparison-literal scan;
4. Python compilation;
5. JavaScript syntax;
6. governed-file integrity;
7. Gate B scenario policy/reconciliation/ground-truth back-test;
8. full pytest;
9. domain/extraction smoke.

Any nonzero exit blocks review. Manifest generation is not a routine gate.

## Final acceptance

```bash
bash scripts/final_acceptance.sh
```

Run it detached under the active slice protocol and read the complete outer log plus `.workflow/slices/S05-final-acceptance/acceptance_results.md`. The 42-step runner adds a clean pip environment, Docker run/health, live HTTP journeys, median-of-five NFR-005 measurements, failure paths, restart, isolated revert/abort, repeated scans, documentation/source-archive checks, and per-hit keyword dispositions.

The script reports local evidence only. It does not approve review, hosted CI, merge, project completion, or tagging.

## Source packaging

```bash
make package
```

Packaging must run from the project-root Git working tree. The script reads the archive member list from `git ls-files -z`, so only tracked working-tree files are included. Untracked and ignored local files such as `.env`, `.venv`, `.git`, and `.workflow/logs` are outside the package input rather than maintained as an exclusion list.

## Preserved clean pip path

```bash
python3 -m venv --clear .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src python scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
```

## Lock maintenance

`pyproject.toml` is the dependency and package-metadata source. Regenerate `uv.lock` only after an intentional change:

```bash
"$HOME/.local/bin/uv" lock
"$HOME/.local/bin/uv" sync --locked --extra dev
```

Do not use opportunistic `--upgrade`. Review the complete lock diff. For S05 release metadata, only the editable root package version may change.

## Docker compatibility

```bash
docker build --file Dockerfile \
  --tag industrial-opportunity-resolution-mvp:local .
docker run -d --name ior-local \
  -p 127.0.0.1:8001:8000 \
  industrial-opportunity-resolution-mvp:local
curl --fail --silent --show-error \
  http://127.0.0.1:8001/api/health
docker stop ior-local
docker rm ior-local
```

## Slice workflow

Each bounded slice follows:

1. create the recorded `slice/SXX-name` branch from `main`;
2. read authority, core, control records, current code/tests, and adopt the slice persona;
3. a different-model Planner writes `plan.md`;
4. the Supervisor reviews until zero plan findings and records `PLAN_APPROVED`;
5. the Implementer executes the approved plan test-first and records evidence without self-approval;
6. the Supervisor reviews the complete diff;
7. a model different from the Implementer performs read-only independent review;
8. valid findings return to the Implementer, followed by focused/full tests and review of fixed work;
9. fresh local gates and explicit-path staging are performed;
10. the Supervisor controls commit, push, PR, current-head CI, ADR-007 gate, squash merge, and durable-state updates.

No subagent approves or merges its own work. A green pipeline is evidence, not approval.

## Authority-change procedure

Edits to hashed config, `data/**`, `docs/core/**`, the methodology, a golden expectation, or another governed artifact are not ordinary refactors.

1. Classify the change under Authority Manifest §7.
2. Record rationale, scope, owner approval, and affected golden cases in the active ADR, plan, and PR.
3. Add deterministic boundary/sensitivity and unchanged-golden tests before changing governed bytes.
4. Audit the exact hand diff and protected paths.
5. Run every allowed pre-generation gate.
6. Run the manifest generator only under the approved one-run gate.
7. Audit every generated hash, byte count, path, and date change; stop on any extra diff.
8. Run integrity, Gate B, full tests, smoke, reviews, and hosted CI.

Never regenerate hashes merely to accept unexplained bytes. Never weaken a golden expectation to obtain green.

The S05 edit to `config/project.yaml project.version` is an approved unhashed release-identity change; all hashed config remains protected.

## CI topology

GitHub Actions runs locked `uv` gates on Python 3.12 and 3.14, the documented pip path on Python 3.12, and an independent Docker image build. Workflow permissions are read-only for repository contents and checkout credentials are not persisted. Cancelled or skipped jobs are not green.

## Failure interpretation

- prohibited scan 1: prohibited tracked path or credential-pattern finding; output is path/rule only;
- prohibited scan 2: Git or tracked-file read error;
- threshold scan 1: embedded configured comparison literal;
- threshold scan 2: YAML, Python, or file-read error;
- lock/sync failure: lock absent, stale, or incompatible;
- compile/Node failure: syntax or required-tool failure;
- integrity failure: governed byte mismatch; do not regenerate without authority;
- Gate B 1: policy, reconciliation, or back-test failure;
- Gate B 2: execution/input error;
- pytest/smoke failure: implementation or frozen behavior is nonconformant;
- Docker/health failure: image/runtime compatibility issue;
- final acceptance nonzero: inspect every step code and its full log.

## Evidence and detached execution

Every substantial command is launched through a uniquely named ignored script and log under `.workflow/logs/`. A wrapper uses `set -u`, changes to the repository, records each command exit code, and ends with `__DONE__`; the complete log must be read before a result is reported.

Raw logs, clean environments, temporary worktrees, and acceptance archives remain ignored. Sanitized command/results evidence belongs in the active slice `test_evidence.md`.

## Test-first and review discipline

Write the smallest failing test, observe the intended RED, implement the minimum change, observe GREEN, and run affected/full regression. Characterization tests that prove existing behavior are labelled honestly instead of being forced to fail. Use real local behavior when it can be exercised directly.

Before handoff, audit acceptance criteria, changed paths, protected paths, assumptions, limitations, rollback, and actual command output. Do not substitute predicted results for evidence.
