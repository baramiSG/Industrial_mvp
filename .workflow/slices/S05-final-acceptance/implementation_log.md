# Implementation Log — S05 Final Acceptance

Role: Senior QA / Verification and Release Engineer (Implementer).
Model: `gpt-5.6-sol-max`; Supervisor model: `claude-fable-5-1-thinking-max`.
Data classification: `confidential_demo`. No Restricted data, credential value, personal data, live industrial source, or cloud execution was used.

## Authority and scope

The Implementer read the approved S05 plan and `PLAN_APPROVED` record, relevant authority/core requirements, prior completion/reviewer residuals, current source/tests/build/docs, and the TDD/verification skills before production edits.

Observed preflight:

- branch `slice/S05-final-acceptance`;
- HEAD and merge-base `98c1a40225a94090238867bc9861e8c6544b5839`;
- prohibited scan `PASS (155 tracked files)`;
- pre-existing Supervisor-owned bookkeeping preserved, including `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, S04 completion, S05 plan/review, and the untracked `.workflow/runs/s04_promote.py` exclusion.

Protected scope remains unchanged: thresholds, sector profiles, evidence policy, all data, Core documents, methodology DOCX, authority hashes, snapshot manifest, and golden expectations. The sole config edit is unhashed `config/project.yaml project.version`.

## TDD record

### List-route 404 and recursive source scan

Initial focused run: `2 failed` for the intended reasons:

- simulated list returned HTTP `500` rather than expected `404`;
- nested scanner test observed `source_count == 0` rather than `1`.

Minimal production edits:

- catch `RepositoryError`/`ValueError` on the list route and map to HTTP 404;
- change threshold source discovery from `glob("*.py")` to `rglob("*.py")`;
- remove the dead `has_equivalence` local while retaining the same equivalence branch.

Observed GREEN:

- focused nodes: `2 passed`;
- API/threshold/fidelity/golden regression: `51 passed`;
- threshold scan: `PASS (13 Python files; 23 configured numeric values)`.

The first wider wrapper used bare `python` for the standalone scanner and observed environment exit `127` because only `python3`/locked uv is available outside a venv. The complete wrapper was rerun through locked uv and all three internal exits were zero.

### Characterization and NFR-005

These tests prove existing behavior and were not forced to fail:

- PP empty supplier-concentration projection: `1 passed`;
- exact public dossier HTML evidence paragraph: `2 passed`;
- cached-scenario identity/content after simulation: `2 passed`;
- all 18 TestClient timing paths: `18 passed`;
- combined characterization/performance files: `100 passed`.

### Release identity and lock

Version expectations were added before metadata changes. Initial focused run: `2 failed`, each observing actual `0.1.0` against required `0.2.0`.

Release edits then changed `pyproject.toml`, `src/ior_mvp/__init__.py`, and only `config/project.yaml project.version`; the 0.2.0 changelog entry was added.

Ordinary `uv lock` output:

```text
Resolved 29 packages
Updated industrial-opportunity-resolution-mvp v0.1.0 -> v0.2.0
uv.lock | 2 +-
1 file changed, 1 insertion(+), 1 deletion(-)
```

The full lock diff contains only the editable root package version. Locked sync, the two release identity tests, package import assertion, and integrity each exited zero. The project-config diff contains only `version: "0.1.0"` to `"0.2.0"`; `as_of_date` and all other fields are unchanged.

### Acceptance runner contract

The new runner contract first observed `3 failed` because `scripts/final_acceptance.sh` did not exist. After implementation and executable-bit update:

- `bash -n scripts/final_acceptance.sh`: exit 0;
- `tests/test_final_acceptance_contract.py`: `3 passed`.

The runner contains 42 stable steps, per-step exit/duration/log records, dependent-step code 125, cleanup traps, no required-result bypass, no governed manifest generation, and explicit local-vs-external evidence boundaries.

## Documentation

Created:

- `docs/FINAL_BUILD_REPORT.md`;
- `docs/OPERATOR_RUNBOOK.md`;
- `docs/DEPLOYMENT_GUIDE.md`.

Replaced or updated:

- `docs/DEVELOPMENT_GUIDE.md`;
- `docs/KNOWN_LIMITATIONS.md` (KL-20–KL-30, including KL-22/KL-29/KL-30);
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-004 final status and ADR-009);
- `docs/REQUIREMENTS_TRACEABILITY.md` (five-run registry, TESTED branch promotions, Gate G scope, DOD-01–DOD-10, SC-01–SC-06, no branch completion promotion);
- `docs/implementation/API_REFERENCE.md` (simulated list/detail 404 contract);
- `README.md` (0.2.0 identity and current gate list);
- `CHANGELOG.md`.

Final commit, hosted CI, merges, release-state promotions, and tag remain explicitly Supervisor-owned and unclaimed.

## First complete-run remediation

The first 42-step run (`20260902T033323Z-12166`) reached the final sentinel with local status 1. All analysis, clean-install, Docker, journey, timing, failure, revert, document, archive, and protected-byte actions ran; the runner exposed three implementation defects in its own control layer:

- elapsed values were nanoseconds but labelled milliseconds because this host did not truncate `date +%s%3N`;
- uvicorn handled SIGTERM and logged a complete graceful shutdown, but `wait` returned the expected signal status 143, which the runner propagated and therefore marked restart steps 25–27 as dependency code 125;
- the conservative keyword classifier left nine legitimate governed/fixture lines unresolved.

Tests were added first and observed `2 failed`. The runner then:

- records `date +%s%N` deltas divided by 1,000,000;
- accepts only wait exit 0 or the explicitly initiated SIGTERM exit 143 after process termination;
- classifies exact frozen temporary-demand wording, methodology control text, two explicit implementation deployment controls, and planted placeholder test data without broadly accepting all documentation/tests.

`bash -n` and all five runner contract tests then passed. The complete 42-step runner is rerun from step 1; no partial result is extrapolated.

## Successful complete local run

Run `20260902T033607Z-17501` replaced the generated acceptance result after the full rerun. Observed final lines:

```text
STEP 42 render_results               exit=0 duration_ms=33
__FINAL_ACCEPTANCE__ status=0
EXIT_final_acceptance=0
__DONE__
```

Every one of the 42 step codes is zero. Key observed results:

- `make ci`: 260 passed, integrity PASS, Gate B PASS for 2 scenarios, smoke PASS;
- clean pip path: 260 passed, integrity/Gate B/smoke PASS;
- Docker build, run, 0.2.0 health, stop, and remove passed;
- first uvicorn PID stopped, a distinct PID restarted, health/authority version matched 0.2.0, and the second PID stopped;
- Journey A–E contracts passed for both cases and both modes;
- all 18 live NFR-005 medians passed; observed range 0.551–1.587 ms;
- unknown opportunity 404, invalid mode 422, SPA fallback 200, and planted TestClient integrity 422 passed;
- S04 isolated revert, diff check, abort, clean check, and worktree removal passed;
- final prohibited/threshold/Gate B scans, document audit, source archive/CRC/member audit, and protected diff passed;
- keyword scan recorded 845 hits and 0 unresolved. The higher count includes the retained first-run `acceptance_results.md` disposition table, which the approved tracked-plus-intended scan contract scans as a historical governance record on rerun.

The complete per-step durations, timing samples, and keyword rows are in the generated `acceptance_results.md` and are summarized in `test_evidence.md`. No review, CI, merge, durable release-state, or tag fact is inferred from this local result.

## Assumptions and recovery

- Docker, curl, Node, Git, Python, uv, and free localhost ports 8001/8010 are required for the complete runner.
- Raw logs, clean environments, worktrees, and archives remain under ignored `.workflow/logs/`.
- Before merge, rollback is by reviewed inverse patches and deletion of S05-created files only. After release, rollback is a reviewed `git revert v0.2.0` branch with complete gates.

## Fix round 1 — holistic-review remediation

The Supervisor adjudicated RV-01 through RV-05 as valid. Tests were added before production changes. The first focused run observed `12 failed, 32 passed`: traversal served `pyproject.toml`, missing economics keys returned successful calculations/API 200, N/A hard-gate prefixes remained unresolved, PP D* stayed gated, packaging included an untracked `.env`, and packaging outside Git succeeded.

Minimal remediation:

- resolved SPA candidates are served only when they are files under the resolved static root;
- `make package` requires the project-root Git working tree and archives only the NUL-delimited `git ls-files` set;
- case-insensitive `resolved`, `not applicable`, and `not_applicable` prefixes resolve hard gates;
- all nine national-value keys and all four EVSI keys are mandatory, with named `ValueError`s wrapped as `EvidenceIntegrityError` by simulation;
- README scenario claims now match the actual packaged blocks and KL-28.

Observed current proof:

- focused API/capability/economics/golden/packaging selection: `45 passed`;
- full locked suite: `280 passed`;
- integrity: PASS unchanged;
- Gate B: PASS for 2 scenarios, including PP `REJECT` route 0;
- smoke: PASS.

The first post-review 42-step run (`20260902T035937Z-93821`) failed only because the protected-path audit correctly rejected additive capability assertions placed in `tests/test_golden_cases.py`. No expectation had changed. The new PP capability contract was relocated to `tests/test_capability_economics.py`, leaving the golden file unchanged. The complete runner was then restarted from step 1.

Run `20260902T040100Z-95877` ended `__FINAL_ACCEPTANCE__ status=0`; all 42 exits were zero. Both locked and clean-pip paths observed `280 passed`, integrity and Gate B passed, all live NFR-005 medians were below 250 ms, keyword scan recorded 48,416 hits with zero unresolved, archive/protected audits passed, and all runtime resources were cleaned up.

Steel simulated D* remains 0.2667 and ΔNV/EVSI remain 198.0/129.3. PP simulated capability now has no unresolved hard gate, publishes D* 0.0 in `immediate_adjacency`, and still selects `REJECT` route 0 with zero support because exact equivalence controls selection. No scenario, golden expectation, governed config, data, Core document, methodology, hash, or manifest byte changed.
