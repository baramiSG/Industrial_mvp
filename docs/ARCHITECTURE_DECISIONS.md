# Architecture Decision Records

Decisions below are subordinate to the methodology DOCX, `docs/core/*` and `AGENTS.md`. They record how this build implements or operates around those authorities; they never redefine them.

---

## ADR-001 — Baseline import committed directly to `main` (one-time bootstrap exception)

**Status:** Accepted 2026-09-02.
**Context:** The workspace held the v0.1.0 package with no git history; the GitHub repository `baramiSG/Industrial_mvp` was private and empty. The owner mandate requires every change to flow through slice branches and PRs, which is impossible before a default branch exists.
**Decision:** The Supervisor imports the unmodified v0.1.0 package (minus Windows `*:Zone.Identifier` download artifacts) together with the build-control documents (`docs/BUILD_ROADMAP.md`, `BUILD_PROGRESS.md`, `REQUIREMENTS_TRACEABILITY.md`, `ARCHITECTURE_DECISIONS.md`, `KNOWN_LIMITATIONS.md`, `.workflow/`) as the first commit on `main`. No engine, config, data or test file is altered in that commit.
**Consequences:** All subsequent changes, including CI itself, go through `slice/SXX-*` branches and PRs. The exception is not repeatable.

## ADR-002 — Model separation implemented with Cursor native subagents

**Status:** Accepted 2026-09-02.
**Context:** The owner mandate specifies Windsurf/Cascade native subagents with distinct models for Planner/Implementer and Reviewer. This build runs in Cursor, whose native equivalent is the `Task` subagent with an explicit `model` parameter.
**Decision:** Supervisor = `claude-fable-5-1-thinking-max`; Planner/Implementer = `gpt-5.6-sol-max`; Independent Reviewer = `cursor-grok-4.6-xhigh`. Every dispatch names its model explicitly. If a model is unavailable, a *different* listed model is substituted and recorded in the slice record; the same model is never reused across the Implementer and Reviewer seats. If separation cannot be met, the slice is set to `BLOCKED_FOR_OWNER`.
**Consequences:** Every slice record names the models used. No subagent approves or merges its own work; the Supervisor is the final gate.

## ADR-003 — Shell execution delegated to shell subagents during a Supervisor tool outage

**Status:** Accepted 2026-09-02.
**Context:** The Supervisor's direct shell tool stopped returning results mid-session ("execution backend unavailable"), while subagent shells continued to work.
**Decision:** All commands (git, gh, uv, pytest, scripts) run through shell subagents given exact command lists; the Supervisor verifies outcomes independently by reading produced files, git metadata and GitHub API responses rather than trusting summaries.
**Consequences:** Every test-evidence record cites the subagent run that produced it and the verifying artifact the Supervisor read.

## ADR-004 — `uv` adopted as the developer/CI toolchain alongside the documented pip path

**Status:** Proposed for S01.
**Context:** Firm rule SG-TR-007 requires dependencies and environments via `uv`. The delivered runbook (`README.md`, `START_DEMO_WSL.sh`, `Dockerfile`) uses `venv` + `pip`, and the Ministry demonstration instructions must keep working unchanged.
**Decision:** Add `uv.lock` and `uv`-based `Makefile` targets and CI steps; keep `pip install -e .[dev]`, `START_DEMO_WSL.sh` and the `Dockerfile` functional and documented. `pyproject.toml` remains the single dependency source.
**Consequences:** Two supported install paths; CI proves both remain installable.

## ADR-005 — Threshold values live only in versioned configuration; config edits go through the §7.3 gate with owner authority

**Status:** Proposed for S02.
**Context:** `AGENTS.md` #7 and Core 07 §9 forbid threshold duplicates in code. The v0.1.0 engine embeds `0.40` (route band), `1.25` (competition warning) and `50` (R11 export/import ratio, stated in methodology §14.2). The first two already exist as keys in `thresholds.v1.yaml`; the third does not.
**Decision:** Engine code reads existing keys for `0.40` and `1.25`. The R11 export/import ratio is added as a new key under `rules.R11` with rationale, sector scope and revision date; `metadata.version` moves 1.0.0 → 1.1.0 (file name `thresholds.v1.yaml` retained as the v1 major line). Authority hashes are regenerated only through `scripts/build_manifests.py` inside the reviewed PR, with the golden regression proving both public outcomes unchanged. The owner's 2026-09-02 mandate is recorded as the methodology-owner approval for this operating-configuration change. An AST-based validator test fails the build if a threshold-bearing literal reappears in engine code.
**Consequences:** `test_threshold_is_loaded_from_versioned_config` asserts the new version string; the change is an explicit, reviewed authority update rather than a silent regeneration.

## ADR-006 — Simulated-state selection is data-driven from scenario content, not opportunity IDs

**Status:** Proposed for S04.
**Context:** `decision_engine.analyze_simulated` dispatches on hard-coded opportunity IDs and embeds steel conditions/kill conditions as string literals. Core 06 §5.3/§10 require each scenario to carry an explicit intended ground truth for back-testing; Core 07 §7.3 and §7.4 define the two selection rules generically.
**Decision:** Scenarios gain `ground_truth` (expected simulated state/route) and `decision_conditions` blocks. The engine applies §7.4 (equivalent qualified availability ≥ target demand → REJECT route 0) and §7.3 (all controls pass → ADVANCE route 5) from scenario content; validation asserts the engine result equals the scenario ground truth. Synthetic scenario files are versioned (`scenario_version`) and re-hashed through the gate.
**Consequences:** New scenarios need no engine code; back-testing is automatic.

## ADR-007 — Merge gating is enforced by the Supervisor protocol, not GitHub branch protection

**Status:** Accepted 2026-09-02.
**Context:** `baramiSG/Industrial_mvp` is a private repository on a GitHub plan where branch-protection rules and rulesets are not available. The owner mandate forbids merging past red checks and forbids administrative overrides.
**Decision:** Before any merge the Supervisor runs `gh pr checks <pr>` and requires every job (`uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build`) to be green on the current PR head, zero Supervisor findings and zero independent-reviewer findings, then merges with `gh pr merge --squash`. Cancelled or skipped jobs are not green. The PR record in `.workflow/slices/*/pr_record.md` captures the checks output.
**Consequences:** Enforcement is procedural and auditable through the slice records; if the repository later moves to a plan with rulesets, the same four checks become required checks.
