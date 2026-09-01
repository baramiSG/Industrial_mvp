# Supervisor Plan Review — S01 CI Pipeline, Local Gates and Toolchain

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Plan author: Planner subagent 8d536d85 (gpt-5.6-sol-max). Plan read in full (29 sections, 1,570 lines) against Core 09 §2.1/§5/§6/§7, Core 01 NFR-004/NFR-008, Manifest §6.10/§7/§8, AGENTS.md proof rule and scope control, ADR-001..006, S00 evidence, existing tests and `pyproject.toml`.

## Round 1 findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| PR-01 | HIGH | TL-01..06 executable in CI (BC-04); plan §18 test drafts | `tests/test_prohibited_files.py` draft: `import scripts.check_prohibited_files as scanner`. `pyproject.toml` `[tool.pytest.ini_options] pythonpath = ["src"]`; `scripts/` has no `__init__.py`; CI runs the `pytest` console entry (which does not add CWD to `sys.path`) via `uv run` and `pip` jobs. | Collection will fail with `ModuleNotFoundError: scripts` in CI and in `make ci`; both Python jobs go red for a packaging reason, not a defect. | Add `"."` to `[tool.pytest.ini_options].pythonpath` → `pythonpath = ["src", "."]` in `pyproject.toml` (test configuration only; no dependency change; `uv.lock` unaffected). Amend plan §5 "Explicitly unchanged" and §25 Task 2 accordingly, and add to Task 2 Step 2 the expectation that red is `ModuleNotFoundError`/`ImportError` on `scripts.check_prohibited_files` *after* the pythonpath change, proving the test fails for the right reason. |
| PR-02 | MEDIUM | `make ci` must reproduce gates locally (persona acceptance; §11) | §6/§11 hard-code `node --check`; §13 says "Node unavailable locally → make ci fails". Node presence in WSL is unverified (S00 probe did not check). | Local gate may be unrunnable on the workstation, blocking Task 8 evidence, while CI would pass — a local/CI mismatch the plan should not leave to chance. | Makefile: add `NODE ?= node` and use `$(NODE) --check src/ior_mvp/static/app.js` in `ci`. Task 1 gains Step 0: run `node --version`; if absent, install Node LTS user-scoped from the official tarball under `~/.local/node` (no shell-rc edits, no system package), record the version in `implementation_log.md`, and run `make NODE=$HOME/.local/node/bin/node ci` or export PATH for the detached script only. Update the contract test to accept `node --check` as a substring (it already does) and DEVELOPMENT_GUIDE prerequisites. |
| PR-03 | LOW | BC-03 durable state; §25 Task 8 staging list | Task 8 stages only Implementer deliverables. | Control records must ride in the same PR or the branch/PR is not self-describing. | Task 8 Step 1: also stage `.workflow/slices/S01-ci-and-toolchain/{persona,context,plan,plan_review}.md`, `.workflow/slices/S00-baseline-import/{test_evidence,completion}.md`, `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/ARCHITECTURE_DECISIONS.md` when the Supervisor directs; scanner runs over the full staged set. |
| PR-04 | LOW (decision) | TL-03 wording (plan §28 Q1) | — | — | Approved wording: `TESTED (partial; existing cases executed in CI; R1-D boundary, R3 explicit and R4-F explicit tests remain S02)`. |
| PR-05 | LOW (decision) | Merge enforcement (plan §28 Q2) | Repository is private on a plan where branch protection/rulesets are not available. | — | No plan change. Recorded as ADR-007: merge gating is enforced by the Supervisor protocol — `gh pr checks` must show every job green on the PR head before `gh pr merge --squash`; no administrative override. |

Assumptions in §29 (ubuntu-latest provides Docker and Node; action major tags acceptable absent a SHA-pinning policy) — accepted.

## Round 2

Planner revised `plan.md` (same agent, resumed). Supervisor verified each correction in the plan text: PR-01 at lines 20, 125, 671, 985, 1205–1228 (`pythonpath = ["src", "."]`, expected-red reason stated, lock unaffected); PR-02 at lines 506, 539, 568, 1135–1144, 1330, 1482 (`NODE ?= node`, user-scoped Node install with SHASUMS verification, override documented); PR-03 at lines 1451–1452 and surrounding (control records staged); PR-04/PR-05 at lines 1038 and 1603–1604.

Unresolved findings: **0**.

## Decision

**PLAN_APPROVED** — 2026-09-02, Supervisor. Implementation may begin on `slice/S01-ci-and-toolchain` from base `0731ae546f79c9ac3bfd92612a01f07da67937ed`, executing plan Tasks 0–5 plus the local validation of Task 8 Step 2 as pre-review evidence; commit/push/PR/merge remain Supervisor-controlled.
