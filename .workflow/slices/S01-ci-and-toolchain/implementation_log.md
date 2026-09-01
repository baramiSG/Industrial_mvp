# Implementation Log — S01 CI Pipeline, Local Gates and Toolchain

## Authority and scope

- Role: Implementer (`gpt-5.6-sol-max`), not reviewer or Supervisor.
- Data classification: PUBLIC repository code, frozen public evidence and explicitly synthetic fixtures.
- Plan gate: `PLAN_APPROVED` recorded by the Supervisor on 2026-09-02 in `plan_review.md`.
- Branch/base confirmed: `slice/S01-ci-and-toolchain` at `0731ae546f79c9ac3bfd92612a01f07da67937ed`.
- No commit, push, PR, merge or self-approval performed.
- No change to `src/ior_mvp/**`, `config/**`, `data/**`, `docs/core/**`, `docs/authority/**`, `Dockerfile`, `START_DEMO_WSL.sh` or `.gitignore`.
- `scripts/build_manifests.py` was not run.

## Pre-existing Supervisor-owned working-tree state

The preflight found Supervisor-owned changes/records before implementation:

- modified `.workflow/state.json`;
- modified `docs/ARCHITECTURE_DECISIONS.md` (ADR-007);
- untracked S00 completion/test evidence;
- untracked S01 context, persona, plan and plan review.

These were preserved and were not attributed to the Implementer.

## Tool versions

- Python: `3.14.4`
- uv: `0.11.31` at `/home/barami/.local/bin/uv`
- Node: `v22.22.1` at `/usr/bin/node`; no installation was needed.
- Docker CLI: `29.7.2`, build `a7dcaa6`

## File-by-file implementation

- `uv.lock` — generated from the unchanged dependency declarations with uv; locked sync resolved 29 packages.
- `pyproject.toml` — changed pytest `pythonpath` only from `["src"]` to `["src", "."]`; locked sync still passed.
- `tests/test_prohibited_files.py` — added deterministic path, secret, binary, ordering, Git enumeration, missing-file and sanitized CLI tests.
- `scripts/check_prohibited_files.py` — added the standard-library tracked-file and secret-pattern scanner with pure scan logic and fail-closed exit codes.
- `tests/test_ci_contract.py` — added static workflow trigger, permission, matrix, cache, gate-order, Docker and non-optional contract tests.
- `.github/workflows/ci.yml` — added uv/Python 3.12 and 3.14, pip/Python 3.12 and Docker jobs.
- `Makefile` — added `UV`, `NODE`, `UV_RUN`, `uv-sync`, `lock` and `ci`; existing targets were preserved.
- `docs/DEVELOPMENT_GUIDE.md` — documented uv, pip, Node override, local gates, CI, Docker, failures and evidence handling.
- `README.md` — added only the approved CI/local-gates subsection.
- `docs/REQUIREMENTS_TRACEABILITY.md` — moved BC-02 to `TESTED`; moved BC-04 and GATE-H to `IMPLEMENTED`; left TL rows unchanged pending CI.
- `.workflow/slices/S01-ci-and-toolchain/implementation_log.md` and `test_evidence.md` — recorded actual implementation and observed evidence.

## Deviations and assumptions

- The prescribed `nohup setsid ... &` lock/sync launch created an empty log but did not keep the process alive through the WSL wrapper. The exact approved script was then run with the tool's managed background execution and completed with exit 0. No implementation behavior changed.
- The full-validation script used the same managed-background treatment while retaining `nohup setsid` and log redirection. It completed with exit 0: uv and clean pip paths each passed 66 tests plus integrity/smoke, and the Docker image built successfully.
- The approved planted-path command used `git add -N`, but `.gitignore` correctly rejects `Zone.Identifier`. The probe required `git add -N -f` so `git ls-files` could see the intentionally ignored test path. The path was reset and deleted immediately; `.gitignore` was not weakened.
- GitHub-hosted Node and Docker availability remains a CI assumption accepted in the approved plan. Local Node and Docker CLIs are present.

## Fix round 1

- **RV-01 / IR-01:** made `docs/DEVELOPMENT_GUIDE.md` permanent rather than S01-specific. Manifest regeneration now requires an approved authority change justified by the slice ADR/PR, and evidence points to the active slice path.
- **RV-02:** added a real temporary Git repository integration test covering a clean tracked file, forced tracked `.env`, sanitized failure output, and a tracked symlink whose untracked target contains a runtime-constructed secret. The production `scan_repository` path is not monkeypatched.
- **RV-03:** changed every path-rule assertion to exact tuple equality; added safe-path negatives, `./` and backslash normalization, and invalid-UTF-8 behavior that retains path findings while skipping secret matching.
- **RV-04:** documented the Makefile uv default and `make UV=uv ci` / explicit uv-path overrides without shell startup changes.
- **RV-05:** strengthened the workflow contract to require exact uv/pip proof commands and require `--locked --extra dev` on every uv-run command while preserving the order test.
- No production scanner/workflow/Makefile behavior changed in this round; fixes are documentation and regression-contract hardening only.
