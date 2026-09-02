# Test Evidence — S05 Final Acceptance

All commands ran from `/home/barami/projects/industrial-opportunity-resolution-mvp` through ignored detached wrappers. Raw logs are under `.workflow/logs/`; this file records observed sanitized output, not predicted results.

## Preflight

Source: `.workflow/logs/s05-t0-preflight.log`.

| Check | Observed result |
|---|---|
| Branch | `slice/S05-final-acceptance` |
| HEAD | `98c1a40225a94090238867bc9861e8c6544b5839` |
| Merge base with main | `98c1a40225a94090238867bc9861e8c6544b5839` |
| Prohibited scan | `PASS (155 tracked files)` |
| Wrapper sentinel | `__DONE__`; all internal exits 0 |

## Residual RED→GREEN

Source: `.workflow/logs/s05-t1-red.log`, `.workflow/logs/s05-t1-green.log`.

| Phase | Observed result |
|---|---|
| RED list mapping | expected 404, actual 500 |
| RED recursive scan | expected source count 1, actual 0 |
| RED total | `2 failed, 1 warning` |
| GREEN focused | `2 passed, 1 warning` |
| API/threshold/fidelity/golden regression | `51 passed, 1 warning` |
| Recursive threshold scan | `PASS (13 Python files; 23 configured numeric values)` |

The warning is the existing Starlette TestClient/httpx deprecation; it was not hidden or silenced.

## Characterization and performance test

Source: `.workflow/logs/s05-t2-characterization.log`.

| Check | Observed result |
|---|---|
| PP empty concentration | `1 passed` |
| Exact public HTML evidence paragraph | `2 passed, 1 warning` |
| Cached scenarios unchanged | `2 passed` |
| NFR-005 TestClient paths | `18 passed, 1 warning` |
| Combined four-file regression | `100 passed, 1 warning` |

Each performance parameter performs one excluded warm-up followed by five measured real TestClient calls and asserts a strict median below 250.0 ms.

## Release metadata and lock

Sources: `.workflow/logs/s05-t3-version-red.log`, `s05-t3-version-lock.log`, `s05-t3-version.log`.

| Check | Observed result |
|---|---|
| Version RED | `2 failed`; actual health/authority version `0.1.0` |
| `uv lock` | exit 0; 29 packages resolved; root package updated to 0.2.0 |
| `uv.lock` diff stat | `uv.lock \| 2 +-`; 1 insertion, 1 deletion |
| Dependency diff | none; only editable root package version changed |
| Locked sync | exit 0 |
| Health/authority equality | `2 passed, 1 warning` |
| Package `__version__` assertion | exit 0 |
| Integrity | `INTEGRITY PASS`; exit 0 |
| `project.yaml` diff | only `project.version` changed; exit 0 |

## Acceptance runner static contract

Sources: `.workflow/logs/s05-t4-runner-red.log`, `s05-t4-runner.log`.

| Phase | Observed result |
|---|---|
| RED | `3 failed`; runner absent |
| Shell syntax | exit 0 |
| Executable bit | set successfully |
| Static contract | `3 passed` |

## First complete 42-step run

Sources: `.workflow/logs/s05-t6-first-acceptance.log` and `.workflow/logs/s05-final-acceptance/20260902T033323Z-12166/`.

Final line: `__FINAL_ACCEPTANCE__ status=1`.

Nonzero steps:

| Step | Exit | Observed cause |
|---|---:|---|
| `uvicorn_stop` | 143 | Server log shows orderly application shutdown and finished process; expected SIGTERM wait status was propagated. |
| `uvicorn_restart` | 125 | Dependency on the stop row. |
| `restart_health` | 125 | Dependency on restart. |
| `restart_stop` | 125 | Dependency on restart. |
| `keyword_scan` | 1 | 200 hits, 9 unresolved governed/fixture lines. |

The same run observed: both full suites green, Docker build/run/health/cleanup green, journeys A–E green, 18 live timing medians below 250 ms, required failure statuses, revert/abort/clean green, document/archive audits green, and protected diff green. Those passing subsets do not convert the failed overall run into acceptance.

Runner remediation was test-first:

- new control tests: `2 failed` before the runner edits;
- shell syntax: exit 0 after edits;
- complete runner contract suite: `5 passed`.

The elapsed-unit defect is also corrected before rerun: nanosecond deltas are now divided into integer milliseconds.

## Successful complete 42-step rerun

Sources: `.workflow/logs/s05-t6-second-acceptance.log` and `.workflow/logs/s05-final-acceptance/20260902T033607Z-17501/`.

Final status: `__FINAL_ACCEPTANCE__ status=0`; outer command exit 0; `__DONE__` observed.

| # | Step | Exit | Duration ms |
|---:|---|---:|---:|
| 01 | `preflight` | 0 | 18 |
| 02 | `make_ci` | 0 | 1424 |
| 03 | `clean_venv_create` | 0 | 1229 |
| 04 | `clean_pip_install` | 0 | 6244 |
| 05 | `clean_prohibited` | 0 | 30 |
| 06 | `clean_thresholds` | 0 | 39 |
| 07 | `clean_compile` | 0 | 27 |
| 08 | `clean_node` | 0 | 60 |
| 09 | `clean_integrity` | 0 | 16 |
| 10 | `clean_gate_b` | 0 | 28 |
| 11 | `clean_pytest` | 0 | 931 |
| 12 | `clean_smoke` | 0 | 30 |
| 13 | `docker_build` | 0 | 1120 |
| 14 | `docker_run` | 0 | 276 |
| 15 | `docker_health` | 0 | 1032 |
| 16 | `docker_stop` | 0 | 454 |
| 17 | `docker_remove` | 0 | 31 |
| 18 | `uvicorn_start` | 0 | 204 |
| 19 | `uvicorn_health` | 0 | 48 |
| 20 | `http_journeys` | 0 | 62 |
| 21 | `http_nfr_005` | 0 | 142 |
| 22 | `http_failures` | 0 | 37 |
| 23 | `integrity_422_testclient` | 0 | 309 |
| 24 | `uvicorn_stop` | 0 | 158 |
| 25 | `uvicorn_restart` | 0 | 205 |
| 26 | `restart_health` | 0 | 49 |
| 27 | `restart_stop` | 0 | 106 |
| 28 | `revert_worktree_add` | 0 | 27 |
| 29 | `revert_apply` | 0 | 19 |
| 30 | `revert_diff_check` | 0 | 25 |
| 31 | `revert_abort` | 0 | 14 |
| 32 | `revert_clean` | 0 | 9 |
| 33 | `revert_worktree_remove` | 0 | 13 |
| 34 | `final_prohibited` | 0 | 30 |
| 35 | `final_thresholds` | 0 | 43 |
| 36 | `final_gate_b` | 0 | 28 |
| 37 | `keyword_scan` | 0 | 72 |
| 38 | `docs_audit` | 0 | 13 |
| 39 | `source_archive` | 0 | 105 |
| 40 | `archive_audit` | 0 | 31 |
| 41 | `protected_diff` | 0 | 6 |
| 42 | `render_results` | 0 | 33 |

### Full suites and gates

- Locked `make ci`: `260 passed, 1 warning in 0.68s`; integrity PASS; scenario validation PASS (2 scenarios and 2 ground-truth checks); smoke PASS.
- Fresh clean-pip suite: `260 passed, 1 warning in 0.66s`.
- The warning is the previously recorded upstream Starlette TestClient/httpx deprecation.
- Final prohibited scan, recursive threshold scan (`13 Python files; 23 configured numeric values`), Gate B, and protected diff all exited 0.
- Docker and both uvicorn lifecycles were cleaned up; restart PID differed from the initial PID.

### Live NFR-005 medians

Each path has one excluded warm-up and five measured localhost HTTP calls.

| Endpoint | Median ms |
|---|---:|
| `/api/opportunities?mode=public` | 0.746 |
| `/api/opportunities?mode=simulated` | 1.550 |
| `/api/opportunities/SAU-H0-721049?mode=public` | 0.742 |
| `/api/opportunities/SAU-H0-721049/ui-manifest?mode=public` | 0.692 |
| `/api/opportunities/SAU-H0-721049/dossier?mode=public` | 0.748 |
| `/api/opportunities/SAU-H0-721049/dossier.html?mode=public` | 0.616 |
| `/api/opportunities/SAU-H0-390210?mode=public` | 0.723 |
| `/api/opportunities/SAU-H0-390210/ui-manifest?mode=public` | 0.722 |
| `/api/opportunities/SAU-H0-390210/dossier?mode=public` | 0.662 |
| `/api/opportunities/SAU-H0-390210/dossier.html?mode=public` | 0.551 |
| `/api/opportunities/SAU-H0-721049?mode=simulated` | 1.554 |
| `/api/opportunities/SAU-H0-721049/ui-manifest?mode=simulated` | 1.534 |
| `/api/opportunities/SAU-H0-721049/dossier?mode=simulated` | 1.587 |
| `/api/opportunities/SAU-H0-721049/dossier.html?mode=simulated` | 1.585 |
| `/api/opportunities/SAU-H0-390210?mode=simulated` | 0.790 |
| `/api/opportunities/SAU-H0-390210/ui-manifest?mode=simulated` | 0.798 |
| `/api/opportunities/SAU-H0-390210/dossier?mode=simulated` | 0.846 |
| `/api/opportunities/SAU-H0-390210/dossier.html?mode=simulated` | 0.661 |

All medians are strictly below 250.0 ms.

### Journey, failure, scan, and artifact results

- Journey matrix: project/health/threshold contracts PASS; extraction 4/4; detail, approved manifest, dossier JSON, and dossier HTML PASS for steel/PP in public/simulated modes.
- Failure paths: unknown opportunity 404; invalid mode 422; unknown SPA path 200; planted evidence-integrity TestClient path 422.
- Reversal: isolated `git revert --no-commit 98c1a40`, diff check, abort, clean check, and worktree removal all exited 0.
- Keyword scan: 845 hits, 0 unresolved, 3 binary/non-UTF-8 files skipped from text matching. The count includes the retained first failed-run acceptance table, whose rows are historical governance content.
- Documentation audit: 8 required document contracts passed.
- Source archive and CRC/member/prohibited-artifact audit passed.
- Protected threshold/profile/policy/data/core/methodology/manifest/golden diff was empty.

## Documentation validation

Task 5 `git diff --check` exited 0 and the documentation/CI/static contract selection reported `25 passed`. The complete rerun evidence above was added after its full outer log, results, journey, timing, and keyword files were read. No hosted review, PR, merge, default-branch CI, release-state promotion, or tag result is claimed here.

## Fix round 1 evidence

Sources: `.workflow/logs/s05-fix-round1-red.log`, `s05-fix-round1-green.log`, `s05-fix-round1-verify.log`, `s05-fix-round1-acceptance.log`, and `.workflow/logs/s05-final-acceptance/20260902T040100Z-95877/`.

| Check | Observed result |
|---|---|
| RED focused selection | `12 failed, 32 passed, 1 warning`; failures matched RV-01/RV-02/RV-03/RV-05 |
| Initial GREEN selection | `44 passed, 1 warning` |
| Current focused selection after protected-test relocation | `45 passed, 1 warning in 0.26s` |
| Current full locked suite | `280 passed, 1 warning in 0.68s` |
| Integrity | `INTEGRITY PASS`; governed hashes unchanged |
| Gate B | `SCENARIO VALIDATION PASS (2 scenarios)`; both ground-truth back-tests PASS |
| Smoke | PASS |

The first complete post-review run (`20260902T035937Z-93821`) ended status 1 with only `protected_diff` nonzero because the PP capability assertion had been added to protected `tests/test_golden_cases.py`. The assertion moved to the focused capability/economics test file; no golden expectation changed.

The mandatory complete rerun (`20260902T040100Z-95877`) ended:

```text
STEP 42 render_results               exit=0 duration_ms=97
__FINAL_ACCEPTANCE__ status=0
EXIT_final_acceptance=0
__DONE__
```

All 42 step exits were zero. Locked `make ci` observed `280 passed in 0.72s`; the clean-pip suite observed `280 passed in 0.73s`. Final integrity, Gate B, archive, and protected-path checks passed. Keyword scan recorded 48,416 hits and zero unresolved. All 18 live medians passed, ranging from 0.600 ms to 1.732 ms.

Focused assertions confirm steel simulated D* 0.2667 and national value/EVSI 198.0/129.3. PP simulated capability has `unresolved_hard_gates == []`, `route_publishable is True`, D* 0.0 and `immediate_adjacency`; simulation remains `REJECT` route 0 with zero support. Gate B independently confirms both planted state/route pairs.
