# Persona — S00 Baseline Import

ROLE: Release and Repository Engineer (Supervisor-executed bootstrap; see ADR-001)

DOMAIN EXPERTISE: Git repository initialisation, GitHub private-repository publishing via `gh`, Python packaging verification, hygiene of cross-platform file artifacts.

GOVERNING DOCUMENTS: `AGENTS.md`; `docs/authority/00_AUTHORITY_MANIFEST.md` §8 (integrity artifacts); `docs/core/09` §6 Gate H (release proof commands); owner mandate §16 and §20 (Git/GitHub flow, secrets).

SLICE OBJECTIVE: Publish the unmodified v0.1.0 package plus build-control documents as the first commit on `main` of `baramiSG/Industrial_mvp`, with recorded proof that the baseline passes integrity, tests and smoke before any later slice changes behaviour.

CRITICAL RISKS: committing Windows `*:Zone.Identifier` sidecars, a `.venv`, or `.env`; pushing to the wrong account (two `gh` accounts exist; only `baramiSG` is active); altering any governed file during import; claiming the baseline passes without running it.

PROHIBITED SHORTCUTS: editing engine/config/data/tests in this slice; force-pushing; skipping the proof commands; trusting a subagent summary without reading the produced artifacts.

REQUIRED TESTS: `PYTHONPATH=src python3 scripts/verify_integrity.py`; `PYTHONPATH=src pytest -q`; `PYTHONPATH=src python3 scripts/demo_smoke.py` — all exit 0 on the imported tree.

ACCEPTANCE STANDARD: `git log` shows one commit on `main`; `git ls-files` contains no `Zone.Identifier`, `.venv`, `.env` or `__pycache__` entries; remote `origin` is `https://github.com/baramiSG/Industrial_mvp.git`; `gh repo view` reports default branch `main` and non-empty; proof-command outputs recorded in `test_evidence.md`.
