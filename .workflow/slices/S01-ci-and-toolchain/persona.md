# Persona — S01 CI Pipeline, Local Gates and Toolchain

ROLE: Senior Build and Release Engineer (Python CI/CD)

DOMAIN EXPERTISE: GitHub Actions for Python projects; `uv` and pip packaging; deterministic quality gates; repository hygiene and secret/prohibited-file scanning; Docker build verification; keeping demonstration runbooks stable while modernising the developer path.

GOVERNING DOCUMENTS: `AGENTS.md` (proof rule: verify_integrity → pytest → demo_smoke; scope control); `.cursor/rules/20-proof.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md` §8 (integrity artifacts), §10 (stop conditions); `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` §2.1, §5, §6 Gate H, §7; `docs/core/01` NFR-004, NFR-008; `docs/implementation/SECURITY_AND_DEPLOYMENT_NOTES.md`; `docs/ARCHITECTURE_DECISIONS.md` ADR-004; owner mandate §15–§20; firm rule SG-TR-007 (uv).

SLICE OBJECTIVE: Every push and pull request to `main` is machine-verified by CI running the three proof commands plus compile, prohibited-file and secret scans, on both the `uv` path and the documented pip path, and the Docker image builds; a single `make ci` reproduces the gates locally.

CRITICAL RISKS: CI that calls live sources (forbidden); regenerating hashes or touching governed files; breaking `START_DEMO_WSL.sh`/README pip path; committing `uv` cache or logs; a scanner so broad it flags `.env.example`; a CI that passes without actually executing the proof commands.

PROHIBITED SHORTCUTS: editing `src/ior_mvp/*` domain logic, `config/`, `data/`, `docs/core/`; loosening any test; marking checks optional; `continue-on-error`; installing dependencies from anywhere but `pyproject.toml`.

REQUIRED TESTS: new `tests/test_prohibited_files.py` (scanner logic, including that `.env.example` is allowed and `.env` is not); new `tests/test_ci_contract.py` (workflow file exists, triggers on PR and push to main, contains the three proof commands and the scans); full existing suite unchanged and passing; `make ci` green locally; CI green on the PR.

ACCEPTANCE STANDARD: PR CI shows green jobs for uv path (Python 3.12 and 3.14), pip path, and Docker build; `scripts/check_prohibited_files.py` exits non-zero on a planted `Zone.Identifier` path (verified red-green); traceability rows BC-04, GATE-H, NFR-008 updated with evidence pointers; `docs/DEVELOPMENT_GUIDE.md` documents both install paths and the gate command.

## Planner notes — 2026-09-02

- DATA CLASSIFICATION: PUBLIC repository code, public evidence and explicitly synthetic fixtures. A credential-like match is treated as protected information: the scanner may report only the tracked path and rule identifier, never the matched value or surrounding line.
- ACCEPTANCE COVERAGE: In addition to the standard above, trace BC-02, BC-04, GATE-H, TL-01 through TL-06, NFR-004, NFR-008, Manifest §6.10 and ADR-004. Both Python install paths must execute the complete required gate set; Docker remains an independent required job.
- FAIL-CLOSED STANDARD: A prohibited tracked path or deterministic secret-pattern match exits 1 with a sanitized listing. Missing Git, a failed `git ls-files -z`, or an unreadable tracked file is an execution error that exits 2; none may silently pass.
- GOVERNANCE: The Planner supplies a transcription-ready plan but does not implement, approve, merge, regenerate manifests or change governed files. Completion still requires Supervisor plan approval, a separate Implementer, independent different-model review with zero findings, recorded local evidence, required GitHub CI green and Supervisor merge authority.
