## SLICE
S01 — CI pipeline, local gates and toolchain (`slice/S01-ci-and-toolchain` → `main`, base `0731ae5`).

## OBJECTIVE
Every push and pull request to `main` is machine-verified: prohibited-file/secret scan, Python compile, JavaScript syntax check, then the repository's three proof commands (`verify_integrity.py`, `pytest -q`, `demo_smoke.py`) on uv/Python 3.12, uv/Python 3.14 and the documented pip path, plus an independent Docker image build. `make ci` reproduces the gates locally. `uv` becomes the developer toolchain (ADR-004) while the README/START_DEMO_WSL.sh/Dockerfile pip paths are unchanged.

## REQUIREMENTS
BC-02, BC-04, GATE-H (Core 09 §6), TL-01..TL-06 (executed in CI), NFR-004 (offline), NFR-008 (WSL/Linux/Docker), Manifest §6.10 (no live sources), ADR-004, ADR-007, SG-TR-007.

## IMPLEMENTATION
- `.github/workflows/ci.yml` — jobs `uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build`; `permissions: contents: read`; `persist-credentials: false`; `fail-fast: false`; no `needs`, `if`, or `continue-on-error`.
- `scripts/check_prohibited_files.py` — standard-library scanner over `git ls-files -z`: ten path rules (Zone.Identifier, `.env` component, `.venv`, `__pycache__`, `*.pyc`, `.DS_Store`, `*.pem`, `*.key`, `*.p12`, `.workflow/logs/`) and four secret regexes; `.env.example` allowed; binary/undecodable payloads skip secret matching; symlinks not followed; exit 1 on finding (path+rule only), exit 2 on scanner error.
- `tests/test_prohibited_files.py` (30 tests incl. real-git integration) and `tests/test_ci_contract.py` (7 tests) — TDD red-green recorded.
- `Makefile` — `UV`, `NODE`, `UV_RUN`, `uv-sync`, `lock`, `ci`; existing targets preserved.
- `pyproject.toml` — `[tool.pytest.ini_options].pythonpath = ["src", "."]` only.
- `uv.lock` — generated from unchanged dependency declarations (29 packages; cp312/cp314 wheels).
- `docs/DEVELOPMENT_GUIDE.md` (new), `README.md` (one subsection), `docs/REQUIREMENTS_TRACEABILITY.md` (BC-02 TESTED; BC-04, GATE-H IMPLEMENTED), build-control records under `.workflow/`.

## DATABASE/MIGRATION IMPACT
None.

## API/UI IMPACT
None. No domain, config, data, core or authority file changed; `build_manifests.py` not run; integrity hashes unchanged.

## TEST EVIDENCE
Local (WSL, Python 3.14.4, uv 0.11.31, Node v22.22.1, Docker 29.7.2), from `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`: focused 37 passed; `make ci` → scanner PASS, compileall OK, `node --check` OK, INTEGRITY PASS, 72 passed, SMOKE PASS (steel/public INVESTIGATE; steel/simulated ADVANCE with real unchanged; PP/public REJECT; extraction 100%); clean pip venv → same gates, 66→72 passed; `docker build` → DOCKER_BUILD_PASS; planted-path probe exit 1 → exit 0.

## VALIDATOR EVIDENCE
`verify_integrity.py` PASS (no governed change); prohibited-file scanner PASS over the full staged set; `git diff --check` clean; protected-path staged diff empty.

## REVIEW STATUS
Plan: 2 rounds → PLAN_APPROVED (Supervisor). Implementation review: 1 LOW (IR-01) → fixed. Independent review (Grok): round 1 REJECT (2 MEDIUM, 3 LOW) → all fixed → re-review **APPROVE — zero unresolved findings**. Models: planner/implementer `gpt-5.6-sol-max`; reviewer `cursor-grok-4.6-xhigh`; supervisor `claude-fable-5-1-thinking-max`.

## SCREENSHOTS
Not applicable (no UI change).

## OUTCOME (appended after merge)
PR #1 https://github.com/baramiSG/Industrial_mvp/pull/1 — heads `b0b2ab4` (run 33569855956, 4/4 pass) and `030dbfe` (run 33570112914, 4/4 pass). `gh pr checks 1`: 4 pass / 4 total. Squash-merged to `main` as `432af8af1fa88a2258a0fd8d825a6855e408270f` at 2026-09-01T23:15:14Z; branch deleted.

## EXPLICIT NON-GOALS
No engine/threshold/data/core changes; no hash regeneration; no new runtime dependency; no live connectors; no branch-protection configuration (unavailable on this plan — ADR-007); no change to Dockerfile, START_DEMO_WSL.sh, docker-compose.yml, requirements.txt, .env.example or .gitignore.
