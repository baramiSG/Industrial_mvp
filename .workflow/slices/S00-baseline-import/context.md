# Context — S00 Baseline Import

- Workspace: `/home/barami/projects/industrial-opportunity-resolution-mvp` (WSL Ubuntu), Python 3.14.4, git 2.53.0, `gh` authenticated as `baramiSG` (active) — a second inactive account `albarami` exists and must not be used.
- Pre-state: no `.git`, no `.venv`, ~80 `*:Zone.Identifier` sidecar files, v0.1.0 package as delivered (`CHANGELOG.md`).
- GitHub: `https://github.com/baramiSG/Industrial_mvp` — PRIVATE, EMPTY (verified via `gh repo view` 2026-09-02).
- Files added by the Supervisor before import: `docs/BUILD_ROADMAP.md`, `docs/BUILD_PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/KNOWN_LIMITATIONS.md`, `.workflow/**`, AGENTS.md build-control section, `.gitignore` additions. No governed file (`authority_hashes.json` / `snapshot_manifest.json` scope) is touched.
- Execution: shell subagent (ADR-003), exact command list, raw output returned; Supervisor verifies by reading `.git/HEAD`, `.git/config`, and GitHub API.
