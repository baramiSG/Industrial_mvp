# S04 Test Evidence

Observed local evidence only. No review, hosted CI, PR, commit, push, or merge result is claimed.

## Preflight

- `.workflow/logs/s04-t0-preflight.log`: branch `slice/S04-simulation-fidelity`; HEAD `ddf905d5051fe3b4468bdcd793a8a640f5040048`; `PROHIBITED FILE SCAN PASS (139 tracked files)`; all command exits 0; `__DONE__`.
- `.workflow/logs/s04-t0-inventory.log`: snapshot/authority manifest diff empty; PP baseline `202bdd1ca08fea485b27f40a539f25212bd1539ce0c26c51072ce7fde304c0ec`, 2159 bytes; steel baseline `6c8065cc848ba519246f0d99372ae0cb3166a4831b9187f14b8ea811d274fded`, 3071 bytes; `S04_GENERATOR_ARTIFACT_COUNT=0`.

## RED → GREEN observations

- Task 1 RED, `.workflow/logs/s04-t1-red.log`: 3 failed with missing `scenario_version`; exit 1. GREEN, `s04-t1-green.log`: 3 passed; exit 0. `s04-t1-audit.log`: only the exact scenario additions; protected diff empty.
- Task 2 RED, `.workflow/logs/s04-t2-red.log`: collection failed because `evaluate_simulated_rules` was absent; exit 4. GREEN, `s04-t2-green.log`: 10 passed; exit 0. Validation, `s04-t2-validation.log`: threshold scan passed (13 Python files, 23 configured numeric values); 68 passed.
- Task 3 RED, `.workflow/logs/s04-t3-red.log`: 18 failed and 3 passed for absent contract/generic path/rows and remaining ID dispatch. GREEN, `s04-t3-green.log`: 21 passed. Validation, `s04-t3-validation.log`: 32 passed; threshold scan passed.
- Task 4 initial RED, `.workflow/logs/s04-t4-red.log`: 4 failed; the mismatch fixture first violated PR-01 because its expected `REJECT` state lacked a `REJECT` narrative. Corrected RED, `s04-t4-red-corrected.log`: 4 failed for absent comparator/Gate B/runtime enforcement; detailed endpoint returned 200 before enforcement. GREEN, `s04-t4-green.log`: 4 passed. Integration, `s04-t4-validation.log`: 53 passed; Gate B passed 2 scenarios and printed `ground_truth_backtest: PASS` for PP and steel.
- Task 5, `.workflow/logs/s04-t5-assert-guard.log`: `REMOVED_GOLDEN_ASSERTS=0`, exit 0; diff contains additions only. `.workflow/logs/s04-t5-golden.log`: 4 passed.
- Task 6 RED, `.workflow/logs/s04-t6-red.log`: 3 failed on absent `gap_diagnosis.simulated_rules`. GREEN, `s04-t6-green.log`: 4 passed.
- Task 7 RED, `.workflow/logs/s04-t7-red.log`: synthetic-row test failed while 9 tests, including both TL-07 characterization checks, passed. GREEN, `s04-t7-green.log`: 10 passed; `node --check` exit 0.

## Gate B observed output

From `.workflow/logs/s04-t4-validation.log`:

- `SCENARIO VALIDATION PASS (2 scenarios)`.
- PP: all applicable public-marginal checks PASS; allocation NOT_APPLICABLE; `ground_truth_backtest: PASS`.
- Steel: all applicable public-marginal checks PASS; qualified availability and allocation NOT_APPLICABLE; `ground_truth_backtest: PASS`.

## Focused contract and golden observations

- `.workflow/logs/s04-t8-validation.log`: 136 focused tests passed; `git diff --check` exit 0.
- `.workflow/logs/s04-observed-summary-pre.log`: steel public `INVESTIGATE`, simulated `ADVANCE` route 5, capacity 57.509, gap 46.491, D* 0.2667, support 18.0, incremental national value 198.0, competition ratio 1.0751; PP public/simulated `REJECT` route 0, formula capacity 104.49, qualified availability 80.0, target 56.0, gap -24.0, support 0.0.
- The same observed summary reports 15 public rows and 18 simulated rows for each case. Steel synthetic rows: R6 `DEGRADED/True`, R7 `DEGRADED/False`, R8 `DISABLED/None`. PP synthetic rows: R6 `DEGRADED/False`, R7 `FULL/False`, R8 `DISABLED/None`. Both back-tests match.

## Manifest-generation preconditions (§24)

1. `.workflow/slices/S04-simulation-fidelity/plan_review.md` records `PLAN_APPROVED` and pre-authorises one generator run under §24.
2. Focused behavior proof passed: Tasks 1–8 logs above cover scenario metadata, six §7.3 failures, equivalence equality, typed back-test mismatch, R6/R7/R8, boundaries, dossier, frontend, API, and exact goldens.
3. `.workflow/logs/s04-t4-validation.log` and `.workflow/logs/s04-pre-manifest.log` each report Gate B PASS for two scenarios with both back-tests PASS. The 53-test integration run covers mismatch exit 1 and invalid-JSON exit 2.
4. `.workflow/logs/s04-pre-manifest.log`: prohibited scan PASS (139 tracked files) and threshold-literal scan PASS (13 Python files; 23 configured numeric values).
5. The same log records Python compile exit 0 and Node syntax exit 0.
6. The same log records 231 full-suite tests passed and `SMOKE PASS`; `.workflow/logs/s04-t5-golden.log` records all four exact golden tests passed, and the direct summary above records every governed number unchanged.
7. `.workflow/logs/s04-pre-manifest-audit.log` shows both synthetic scenario diffs contain additions only and exactly the approved §8 blocks; no pre-existing line is removed or changed.
8. The same audit records no diff for `data/manifests/snapshot_manifest.json` or `docs/authority/authority_hashes.json`.
9. The same audit records no diff in config, public snapshots, golden data, frozen core, or methodology DOCX.
10. The same audit records `S04_GENERATOR_ARTIFACT_COUNT=0`.

All ten preconditions above were observed before generator invocation. `scripts/build_manifests.py` invocation count remains zero at this point.

## Single manifest generation and verification

- `.workflow/logs/s04-generator.log`: the pre-authorised `scripts/build_manifests.py` command exited 0 and reached `__DONE__`. This was the sole S04 generator invocation.
- `.workflow/logs/s04-post-generator.log`: `snapshot_manifest.json` changed only the two synthetic entries; `generated_on` did not change. `docs/authority/authority_hashes.json` had no diff.
- Steel generated/actual: SHA-256 `8867f0833662108746e0639082847d40841c0b3e550628199be93e75d46f9aea`, 4711 bytes; manifest hash and byte matches both `True`; `sha256sum` identical.
- PP generated/actual: SHA-256 `06517bb93d68911b75c83adb5bf4eab085a2843d1aaa245b56555c999eeee5ea`, 3433 bytes; manifest hash and byte matches both `True`; `sha256sum` identical.
- Post-generator `INTEGRITY PASS`; all audit commands exited 0.

## Post-generation and final local gates

- `.workflow/logs/s04-t11-self-audit.log`: prohibited scan PASS; threshold scan PASS; integrity PASS; Gate B PASS with both ground-truth back-tests; 231 tests passed; smoke PASS; diff check exit 0.
- `.workflow/logs/s04-final.log`, `make ci` with `UV=/home/barami/.local/bin/uv`: uv sync, scanners, compile, Node syntax, integrity, Gate B, 231 tests, and smoke all passed; `EXIT_make_ci=0`.
- Required project `.venv` proof: integrity PASS; Gate B PASS with both back-tests; 231 tests passed; smoke PASS; all exits 0.
- Clean pip environment `.workflow/logs/s04-pip-venv`: editable install succeeded; prohibited/threshold scans, compile, Node syntax, integrity, Gate B, 231 tests, and smoke passed; all exits 0.
- Docker image `industrial-opportunity-resolution-mvp:s04-local` built successfully; `EXIT_docker=0`; final `__DONE__`.
- The Python test runs emitted one existing Starlette/httpx deprecation warning. Docker's isolated root install emitted pip's standard root-user warning. Neither gate failed.

## Explicit staging

- `.workflow/logs/s04-stage.log`: 27 approved implementation/data/docs/test/S04-record paths staged explicitly; cached diff check passed; prohibited scan passed for 146 tracked files; integrity passed.
- Supervisor-owned `.workflow/state.json` and `docs/BUILD_PROGRESS.md`, the S03 completion bookkeeping, `.workflow/runs/**`, and `.workflow/logs/**` were not staged.

Supervisor and independent reviews, hosted CI, PR, commit, push, and merge remain outside this implementer evidence.
