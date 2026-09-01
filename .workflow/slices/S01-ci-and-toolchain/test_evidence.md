# Test Evidence — S01 CI Pipeline, Local Gates and Toolchain

## Environment

- Date: 2026-09-02
- Branch: `slice/S01-ci-and-toolchain`
- Base/HEAD before implementation: `0731ae546f79c9ac3bfd92612a01f07da67937ed`
- WSL Ubuntu; Python `3.14.4`; uv `0.11.31`; Node `v22.22.1`; Docker CLI `29.7.2`
- Data classification: PUBLIC. No matched secret value is recorded.

## Preflight and hygiene

- `git branch --show-current` → `slice/S01-ci-and-toolchain`, exit 0.
- `git rev-parse HEAD` → `0731ae546f79c9ac3bfd92612a01f07da67937ed`, exit 0.
- Initial `git ls-files` review → 86 tracked files; no prohibited tracked path observed.
- Deterministic secret-pattern workspace search → no match.
- Root `.env` remained ignored and untracked; it was not read.

## Lock and environment

Command: `~/.local/bin/uv lock` followed by `~/.local/bin/uv sync --locked --extra dev`.

Observed: 29 packages resolved; the local project was built and installed; exit 0.

After the pytest-only `pythonpath = ["src", "."]` change, `~/.local/bin/uv sync --locked --extra dev` again resolved 29 packages and exited 0 without a lock update.

## Scanner TDD

Red command:

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_prohibited_files.py -q
```

Observed before implementation: collection error on `ModuleNotFoundError: No module named 'scripts.check_prohibited_files'`; exit 2.

Green result after implementation: `24 passed in 0.02s`; exit 0.

## Planted-path red-green

The approved first attempt with `git add -N -- scanner-probe:Zone.Identifier` was rejected because the path is intentionally ignored; the scanner therefore saw 86 clean tracked files. That command sequence exited 2 because no probe status was available.

Corrected probe used `git add -N -f -- scanner-probe:Zone.Identifier` without changing `.gitignore`.

Observed red:

```text
PROHIBITED FILE SCAN FAIL
- scanner-probe:Zone.Identifier: path:Zone.Identifier
PROBE_EXIT=1
```

The intent-to-add entry was reset and the probe file deleted. Clean scanner result: `PROHIBITED FILE SCAN PASS (86 tracked files)`; exit 0.

## CI workflow contract TDD

Red command:

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_ci_contract.py -q
```

Observed before workflow creation: seven failures because `.github/workflows/ci.yml` did not exist; exit 1.

Green result after workflow creation: `7 passed in 0.03s`; exit 0.

Combined focused result:

```text
31 passed in 0.04s
```

Exit 0.

## Makefile dry run

`make -n uv-sync`, `make -n lock` and `make -n ci` exited 0. The expanded `ci` recipe showed locked uv sync followed by scanner, compileall, `node --check`, integrity, pytest and smoke in the approved order.

## Full pre-review local validation

Execution script: `.workflow/logs/s01_full_validation.sh`.

The WSL wrapper did not preserve the plan's trailing-background `nohup setsid ... &` launch. The same ignored script was therefore run under `nohup setsid` with managed background execution and output redirected to `.workflow/logs/s01_full_validation.log`. The managed process exited 0, and the log ended with `S01_FULL_VALIDATION_COMPLETE`.

### uv / `make ci`

- `uv sync --locked --extra dev` → 29 packages resolved/checked.
- prohibited-file scan → `PROHIBITED FILE SCAN PASS (100 tracked files)`.
- `python -m compileall -q src scripts tests` → exit 0.
- `node --check src/ior_mvp/static/app.js` → exit 0.
- integrity → `INTEGRITY PASS`.
- pytest → `66 passed, 1 warning in 0.23s`; exit 0.
- smoke → `SMOKE PASS`; steel/public `INVESTIGATE`, steel/simulated `ADVANCE` with real unchanged, polypropylene/public `REJECT`, extraction 100%.

The warning is the pre-existing Starlette `httpx` test-client deprecation recorded by S00; it was not filtered or silenced.

### Clean pip compatibility environment

- Environment: `.workflow/logs/s01-pip-venv`, Python 3.14.4.
- `python -m pip install -e ".[dev]"` → project and declared development dependencies installed; exit 0.
- prohibited-file scan → `PROHIBITED FILE SCAN PASS (100 tracked files)`.
- compileall and Node syntax → exit 0.
- integrity → `INTEGRITY PASS`.
- pytest → `66 passed, 1 warning in 0.17s`; exit 0.
- smoke → `SMOKE PASS` with the same frozen outcomes; exit 0.

### Docker

- Docker CLI was present, so the guarded block ran.
- `docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s01-local .` → image exported and tagged; `DOCKER_BUILD_PASS`; exit 0.

## Final staged audit

- 20 approved implementation/control-record paths are staged; no commit was created.
- `git diff --check` and `git diff --cached --check` → exit 0.
- Protected-path staged diff (`src`, `config`, `data`, `docs/core`, `docs/authority`, `Dockerfile`, `START_DEMO_WSL.sh`, `.gitignore`) → empty, exit 0.
- Full staged scanner → `PROHIBITED FILE SCAN PASS (100 tracked files)`, exit 0.
- Deterministic secret-pattern workspace search → no match.

## GitHub Actions evidence (recorded by the Supervisor from `.workflow/logs/ci_watch_pr1.log`)

- PR: https://github.com/baramiSG/Industrial_mvp/pull/1 — head `b0b2ab4787b3da75c1cb7d8c223d16f5c1d68c80`, base `main`.
- Workflow run: https://github.com/baramiSG/Industrial_mvp/actions/runs/33569855956
- `gh pr checks 1 --watch` exit 0. Jobs on the PR head:

| Job | Result | Duration |
|---|---|---|
| uv / Python 3.12 | pass | 15s |
| uv / Python 3.14 | pass | 13s |
| pip / Python 3.12 | pass | 18s |
| Docker image build | pass | 23s |

- A second CI run is required on the evidence-promotion commit (traceability, KL-09, this section) and must also be green before merge; it is recorded below when it completes.

## Governance

- `scripts/build_manifests.py`: NOT RUN — no governed change; prohibited by S01 scope.
- TL-01 through TL-06 statuses remain unchanged until CI evidence exists.
- BC-04 and GATE-H are at most `IMPLEMENTED` before CI.
- This evidence is an Implementer self-check, not approval.

## Fix round 1

Focused command:

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_prohibited_files.py tests/test_ci_contract.py -q
```

Observed: `37 passed in 0.08s`; exit 0.

Full command:

```bash
make ci
```

Observed:

- locked uv sync → 29 packages resolved/checked;
- staged scanner → `PROHIBITED FILE SCAN PASS (100 tracked files)`;
- compileall and Node syntax → exit 0;
- integrity → `INTEGRITY PASS`;
- pytest → `72 passed, 1 warning in 0.27s`;
- smoke → `SMOKE PASS`, with steel/public `INVESTIGATE`, steel/simulated `ADVANCE` while real remained unchanged, polypropylene/public `REJECT`, and extraction 100%;
- overall `make ci` exit 0.

The single warning remains the pre-existing Starlette `httpx` test-client deprecation; it was not filtered or silenced.

After staging the three fixed files, both evidence records, `implementation_review.md` and `reviewer_findings.md`:

- `git diff --check` and `git diff --cached --check` → exit 0;
- protected-path staged diff → empty, exit 0;
- scanner → `PROHIBITED FILE SCAN PASS (102 tracked files)`, exit 0;
- IDE lint diagnostics for the changed test/guide files → none.
