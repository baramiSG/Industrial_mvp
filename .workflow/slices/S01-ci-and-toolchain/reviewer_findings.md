# Independent Reviewer Findings — Slice S01 (CI Pipeline, Local Gates and Toolchain)

- **Reviewer role:** Independent Reviewer (not Supervisor, not Implementer). Read-only except this file.
- **Reviewer model:** Cursor Grok 4.6 (`cursor-grok-4.6-xhigh`), distinct from Implementer (GPT `gpt-5.6-sol-max`) and Supervisor (Claude `claude-fable-5-1-thinking-max`) per ADR-002.
- **Date:** 2026-09-02
- **Data classification:** PUBLIC (repository code, frozen public evidence, explicitly synthetic fixtures). No secret value is reproduced here.
- **Branch / base (from review package):** `slice/S01-ci-and-toolchain` at `0731ae546f79c9ac3bfd92612a01f07da67937ed`
- **Verdict:** **REJECT** — 0 BLOCKER, 0 HIGH, 2 MEDIUM, 3 LOW. MEDIUM items must be fixed and re-reviewed; this seat does not approve.

## Skill discovery

Read `requesting-code-review/SKILL.md` and `requesting-code-review/code-reviewer.md`. Applied that template’s rigor (plan alignment, test fidelity vs mocks, production readiness, calibration of severity, read-only git/file inspection). No other installed skill governed GitHub Actions / uv toolchain review.

## Files read

**Authority / control:** `AGENTS.md`; `docs/authority/00_AUTHORITY_MANIFEST.md` §6, §7, §8, §10; `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` (all); `docs/core/01_PRODUCT_AND_REQUIREMENTS.md` §7–§8; `docs/BUILD_ROADMAP.md`; `docs/ARCHITECTURE_DECISIONS.md` (ADR-001..007); `docs/KNOWN_LIMITATIONS.md`; `docs/REQUIREMENTS_TRACEABILITY.md`; `.workflow/state.json`; `.workflow/slices/S01-ci-and-toolchain/{persona,context,plan,plan_review,implementation_log,implementation_review,test_evidence}.md`.

**Review package:** `.workflow/logs/s01_review_meta.txt`; `.workflow/logs/s01_review.patch` (skimmed; code paths also read as files).

**Code under review (files, not only patch):** `.github/workflows/ci.yml`; `scripts/check_prohibited_files.py`; `tests/test_prohibited_files.py`; `tests/test_ci_contract.py`; `Makefile`; `pyproject.toml`; `README.md`; `docs/DEVELOPMENT_GUIDE.md`; `docs/REQUIREMENTS_TRACEABILITY.md`; `uv.lock` (header, package names, extras, 3.12/3.14 wheels).

**Style / existing proof:** `tests/test_static_frontend.py`; `tests/test_integrity_contract.py`; `tests/test_api.py`; `scripts/verify_integrity.py`; `scripts/demo_smoke.py`; `scripts/build_manifests.py` (existence/role only); `.env.example`; `.gitignore`; `Dockerfile`; `src/ior_mvp/config.py`.

**External references used only to check Action/runner semantics:** `astral-sh/setup-uv@v6` `action.yml`; `actions/setup-python@v5` `action.yml`; GitHub-hosted Ubuntu 24.04 / 26.04 included-software lists.

## Strengths (so findings are not read as a blanket rejection)

- Workflow, scanner, Makefile, tests and `pyproject.toml` pythonpath change are faithful transcriptions of the approved plan (post PR-01/PR-02).
- Gate H relative order is preserved (integrity → pytest → smoke) with additive scanner/compile/Node gates first. `build_manifests.py` was not run.
- No staged edits to `src/ior_mvp/**`, `config/**`, `data/**`, `docs/core/**`, `docs/authority/**`, `Dockerfile`, `START_DEMO_WSL.sh`, or `.gitignore`.
- Workflow: `contents: read`, `persist-credentials: false`, `fail-fast: false`, no `needs`, no `continue-on-error` / `|| true`, no job/step `if`. Concurrency expression is the documented PR-number-or-ref pattern.
- Scanner: NUL `git ls-files`, fail-closed exit 2, sanitized stderr, `.env` as a full path component (so `.env.example` is allowed), case-insensitive suffix rules as specified, symlink not followed, binary skip for secrets.
- Traceability is conservative: BC-04 / GATE-H are `IMPLEMENTED` not `TESTED`; TL-01..06 unchanged; KL-09 still open; no green GitHub URL invented.
- `uv.lock` lists 29 packages derivable from `fastapi`, `uvicorn[standard]`, `PyYAML`, `pytest`, `httpx` (including `python-dotenv` via uvicorn standard, `pygments` via pytest 8.4.2). Lock includes cp312 and cp314 wheels for native deps (e.g. pydantic-core, uvloop).
- Four approved secret regexes do not match their own source strings in `plan.md` / scanner / tests; workspace search found no live `ghp_` / `AKIA` / private-key-header / `sk-`+20 matches in tracked text.

---

## Findings

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | REQUIRED REMEDIATION |
|---|---|---|---|---|---|
| RV-01 | MEDIUM | Permanent developer documentation must remain accurate beyond this slice (owner mandate §28; Core 09 §6 Gate H allows `build_manifests.py` after an approved governed change; Manifest §7/§8). Also unfixed Supervisor IR-01. | `docs/DEVELOPMENT_GUIDE.md:5`; `docs/DEVELOPMENT_GUIDE.md:95` | The lasting development guide hard-codes S01 policy: “Do not run `scripts/build_manifests.py` for S01…” and points evidence at `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`. After S01 merges, S02 is required to regenerate hashes under §7.3. A later worker following this guide can skip an authorized manifest rebuild, or file evidence in a closed slice path. This matches the plan’s §11 S01 wording, but that wording is wrong for a permanent file. | Reword line 5 to: never run `scripts/build_manifests.py` outside an approved authority change (Manifest §7); the slice ADR and PR must justify it first. Reword line 95 to the active slice’s `test_evidence.md` (`./workflow/slices/<slice>/test_evidence.md`). Do not keep “for S01” in this file. |
| RV-02 | MEDIUM | BC-02 (no secrets/prohibited files in Git); plan §7 `scan_repository` is the only production wiring of git → read → scan; reviewer brief: tests that pass against a broken implementation / monkeypatching that hides real behaviour. | `tests/test_prohibited_files.py:96-136`; `scripts/check_prohibited_files.py:138-141` | `test_main_returns_one_for_a_planted_zone_identifier`, `test_main_never_prints_a_matched_secret` and `test_main_returns_two_when_git_is_unavailable` all `monkeypatch.setattr(scanner, "scan_repository", ...)`. They never call the real `scan_repository`. A no-op `scan_repository` that always returns `(), 0`, or a version that follows symlinks / uses `os.walk` instead of `git ls-files -z`, would still pass the entire unit file. `test_git_tracked_paths` only tests the helper in isolation. The one-time planted-path probe in `test_evidence.md` is not a regression test. This is how the approved plan drafted the tests; it is still insufficient against BC-02 regressions. | Add an automated integration test on a temporary `git init` worktree (no monkeypatch of `scan_repository`): write a safe file, `git add` it, assert `main(tmp)` returns 0; add a prohibited path (e.g. `.env` or a `*:Zone.Identifier` name) and assert exit 1 with only path+rule on stderr; add a symlink whose target file contains a constructed secret and assert the secret regex does **not** fire on the followed contents. Keep constructing secrets at runtime. |
| RV-03 | LOW | BC-02; plan §7–§8 (normalization, `.env.template` allowed, invalid UTF-8 is binary, exact finding set). Reviewer brief: missing negative cases; tests that pass against a broken implementation. | `tests/test_prohibited_files.py:13-30`; `tests/test_prohibited_files.py:33-34`; `tests/test_prohibited_files.py:54-56` | Path-rule cases assert `Finding in scan_tracked_files(...)`, so extra rules on the same path still pass. The only clean-map assertion is `.env.example`. There is no test for: `.env.template` / `foo.env`; `./.env` after `normalize_path`; backslash normalization; `.workflow/logs` exact; invalid UTF-8 without NUL (only NUL is tested as binary). An implementation that dropped `./` stripping or UTF-8 fail-closed decoding would not be caught. | Change the parametrized path test to exact tuple equality `(Finding(path, rule),)`. Add negatives for `.env.template` and `src/ior_mvp/app.py`. Add `normalize_path("./.env") == ".env"` and an invalid-UTF-8 payload (`b"\xff"`) that skips secret matching while still applying path rules. |
| RV-04 | LOW | NFR-008 portability; plan §11 (“A developer with uv elsewhere can override it (`make UV=uv ci`)”); reviewer brief: judge whether `$(HOME)/.local/bin/uv` is documented adequately. | `Makefile:1`; `docs/DEVELOPMENT_GUIDE.md:11-16`; `docs/DEVELOPMENT_GUIDE.md:19-27` | Makefile default `UV ?= $(HOME)/.local/bin/uv` matches the approved install path and is the right default. The guide documents `NODE ?= node` and the `make NODE=... ci` override, but never states the UV default or `make UV=uv ci`. A developer with uv on PATH (pipx, distro, previous installer) gets `make: ~/.local/bin/uv: No such file or directory` even though `uv --version` works. | In Prerequisites (or Install uv), state that `make` invokes `$(HOME)/.local/bin/uv` unless overridden, and document `make UV=uv ci` (and `make UV=/path/to/uv ci`) without editing shell rc files. |
| RV-05 | LOW | Core 09 §6 Gate H; AGENTS.md proof commands (`PYTHONPATH=src` + integrity, `pytest -q`, smoke); plan §6 uv `run --locked --extra dev` on every gate. Reviewer brief: tests that would pass against a broken workflow. | `tests/test_ci_contract.py:68-83`; `.github/workflows/ci.yml:44-55`; `.github/workflows/ci.yml:73-84` | `test_each_python_job_runs_every_required_gate` only searches substrings. It would still pass if `PYTHONPATH=src` were removed from the three proof steps, or if `uv run` dropped `--locked` (sync still checked separately). The committed workflow currently has both; the contract does not lock them. Editable install + pytest `pythonpath` likely keep pytest working without `PYTHONPATH`, so this is a contract hole, not a current runtime failure. | Assert the uv proof lines contain `PYTHONPATH=src uv run --locked --extra dev` and the pip proof lines contain `PYTHONPATH=src python` / `PYTHONPATH=src pytest -q`. Keep the existing order check. |

---

## Residual coverage (plan-faithful; do not treat as implementer transcription errors)

These are BC-02 / scanner completeness notes. The implementation matches the **approved** path list and four regexes. Expanding them needs a plan amendment, not a silent implementer change.

- Path matching is case-sensitive except `.pyc`/`.pem`/`.key`/`.p12`. `zone.identifier`, `.ENV`, `.workflow/Logs/` would not match. Windows ADS is normally exactly `Zone.Identifier`.
- Secret regexes do not detect `github_pat_`, `gho_`/`ghs_`/`ghu_`, or `-----BEGIN ENCRYPTED PRIVATE KEY-----`. Fine-grained GitHub PATs and PKCS#8 encrypted keys would pass the scanner.
- Scanner enumerates `git ls-files` only (index). Untracked files are out of scope by design; `DEVELOPMENT_GUIDE.md` already says “tracked-file”.
- Action major tags (`@v4`/`@v5`/`@v6`) and unpinned uv (setup-uv default “latest”) were accepted in plan §14 / §29. Supply-chain pinning is out of S01 scope.

## Risk areas checked and found clean (for this implementation)

| Area | Result |
|---|---|
| Spec drift vs Core 09 Gate H order | Clean. Scanner → compile → node → integrity → pytest → smoke. The three proof commands keep relative order. Manifest regeneration omitted with an honest GATE-H note. |
| Manifest §6.10 / NFR-004 live sources | Clean. No `httpx`/`requests`/`urllib` client usage in `src/` or `scripts/` proof paths. API tests use in-process `TestClient`. Golden/smoke load local hashed artifacts. CI network use is Action/package install only. |
| AGENTS.md scope | Clean. Staged names and patch hunks do not touch domain, config, data, core, authority, Dockerfile, startup script, or `.gitignore`. `pyproject.toml` change is pytest `pythonpath` only. |
| GHA triggers / permissions / concurrency | Clean. `push`/`pull_request` to `main`; `contents: read`; group `ci-${{ github.workflow }}-${{ github.event.pull_request.number \|\| github.ref }}`; `cancel-in-progress: true`. |
| `strategy.fail-fast` | Clean. `false` at workflow; contract uses BaseLoader so it sees `"false"`. |
| `uv sync --python` + `setup-python` | Acceptable. Redundant but valid: setup-python puts 3.12/3.14 on PATH; `uv sync --python` selects that version into `.venv`; later `uv run --locked --extra dev` uses the project env. |
| `astral-sh/setup-uv@v6` inputs | Clean. `enable-cache` and `cache-dependency-glob` exist on v6; `uv.lock` is a valid relative glob at repo root. |
| `uv run --locked --extra dev` | Clean in the workflow file (every uv gate). Optional extra `dev` matches `[project.optional-dependencies]`, not a uv dependency-group. |
| `node` / `docker` on `ubuntu-latest` | Clean per GitHub runner images (Ubuntu 24.04 current latest: Node 22/24 and Docker engine; 26.04 preview also has both). Plan §29 assumption holds. |
| Python 3.14 via `actions/setup-python@v5` | Clean for 2026-09: 3.14 is GA; input is quoted `"3.14"`; `allow-prereleases` not required. Lock contains cp314 wheels. |
| pip `cache-dependency-path: pyproject.toml` | Clean. Documented `setup-python` input; hashes `pyproject.toml` for the pip download cache. Not a requirements.txt parser. |
| `.env.example` vs `.env` | Clean. Component equality; `.env.example` content is placeholders only (`IOR_HOST` etc.). |
| Secret false positives on `uv.lock` / methodology / plan regex source | Clean for current tracked text (search of constructed regexes: no matches). SHA-256 hex cannot contain `sk-` (`s` is not hex). |
| Intent-to-add | Scanner uses `git ls-files -z` (index). Intent-to-add paths are visible after `git add -N`; implementer needed `-f` because `.gitignore` already blocks `Zone.Identifier`. `.gitignore` was not weakened. |
| `pythonpath = ["src", "."]` shadowing | Acceptable. No root-level `*.py` modules; `ior_mvp` still resolves from `src` first. `.` is required so `import scripts.check_prohibited_files` works without an `__init__.py` (PEP 420). No `import config` / `from config import` in tests. Residual: root dirs (`config/`, `data/`) become importable namespace packages if someone later writes `import config`. |
| Hidden TODOs / placeholders / fake integrations | Clean in S01 code and `DEVELOPMENT_GUIDE.md`. Contract tests are static file reads (same pattern as `test_static_frontend.py`). |
| Windows/WSL | NFR-008 is WSL, native Linux, Docker — not native Windows. `$(HOME)` is correct for those. |
| README vs Makefile/workflow | Clean for the added subsection. `make ci` is the six Python gates; Docker is described as an additional GHA job, matching Makefile (no docker in `ci`) and the independent `docker-build` job. |
| Traceability honesty | Clean. BC-02 `TESTED` after unit tests + probe + clean scan (plan §22). BC-04 and GATE-H `IMPLEMENTED` before GitHub CI. TL rows still `IMPLEMENTED` / `IMPLEMENTED (partial)`. KL-09 still Open. ADR-004 left “Proposed” as the plan required. |
| `test_evidence.md` vs files | Counts check out: 11+13 scanner tests = 24; 5+2 contract tests = 7; 35+24+7 = 66; 86 baseline + 14 added paths = 100 tracked. “29 packages” matches `uv.lock` `name =` entries. No claim of GitHub CI green, `VALIDATED`, or `COMPLETE`. Local pip evidence is honestly Python 3.14.4, not 3.12 (CI pip job remains unproven until GHA). |

## Cannot verify from files

1. **GitHub Actions execution** of `uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build` — no run URL exists yet; BC-04/GATE-H/NFR-008 correctly remain short of `TESTED`.
2. **Raw local full-validation log** (`.workflow/logs/s01_full_validation.log`) is gitignored and not in the review package. Integrity PASS, 66 passed, SMOKE PASS, Docker build, and planted-path probe are claimed in `test_evidence.md` and corroborated by code/lock arithmetic, but this reviewer did not re-execute commands.
3. **Whether setup-uv cache save / setup-python pip cache succeed** with workflow `permissions: contents: read` only. Current Actions cache uses a runtime token rather than `actions: write`; a 403 would typically warn rather than fail the job, but that is not proven on this repository.
4. **Live `actions/setup-python@v5` 3.14 index** on the exact runner image that will run the first PR (docs and local 3.14.4 plus cp314 wheels make failure unlikely).
5. **Whether a future `ubuntu-latest` image omits `node` in PATH.** Present 24.04/26.04 images include Node; this is the accepted plan assumption.

## Assumptions

- Review package staged set is the complete S01 implementation under review (`implementation_review.md` exists unstaged as a Supervisor artifact and was read; it is not a code deliverable).
- “Material defect” includes permanent-doc falsehoods and security-scanner tests that would not catch a broken `scan_repository`, not only defects that would fail the first CI run of the current bytes.
- Expanding secret regexes beyond the four approved patterns would be a plan change; it is recorded as residual coverage, not a required S01 code change.

## al-muhasibi (self-audit of this review)

- Asked: independent CI/security review of S01 vs Gate H, Manifest, NFR-004, GHA semantics, scanner bypasses, test fidelity, docs, traceability, evidence honesty.
- Verified from files: workflow, scanner, tests, Makefile, pyproject, README, guide, traceability, lock, existing proof scripts, review meta/patch, authority docs.
- Not verified: live GHA, ignored validation logs, cache-permission behaviour on this repo.
- Did not modify any file except this findings record. Did not approve. Did not implement fixes.

## Re-review round 1

- **Reviewer:** same seat (Cursor Grok 4.6 / `cursor-grok-4.6-xhigh`). Read-only except this append.
- **Scope:** RV-01..RV-05 fixes only. Confirmed `scripts/check_prohibited_files.py`, `.github/workflows/ci.yml` and `Makefile` are unchanged from the first review.
- **Files re-read:** `tests/test_prohibited_files.py`; `tests/test_ci_contract.py`; `docs/DEVELOPMENT_GUIDE.md`; Fix round 1 in `implementation_log.md` and `test_evidence.md`.

### Per-finding disposition

| ID | Disposition | Evidence |
|---|---|---|
| RV-01 | RESOLVED | `docs/DEVELOPMENT_GUIDE.md:5` now requires an approved Manifest §7 change plus slice ADR/PR, not an S01 ban. `docs/DEVELOPMENT_GUIDE.md:102` points at `.workflow/slices/<slice>/test_evidence.md`. Grep of the guide: no `S01`. |
| RV-02 | RESOLVED | `tests/test_prohibited_files.py:162-194` calls `scanner.main(tmp_path)` with no `scan_repository` monkeypatch. Real `git init` + `git add` (no commit, so no identity). Clean tracked file → exit 0; forced `.env` → exit 1 with `- .env: path:.env` and no `placeholder` leak; `.env` removed from index/worktree; symlink `link.txt` → untracked `target.txt` holding a runtime-constructed `ghp_`+36 token → exit 0 and secret absent from stdout/stderr. No complete token literal in source. Deterministic on GitHub `ubuntu-latest`: git is preinstalled, `core.symlinks` is on, `os.symlink` works, `git ls-files` reads the index without a commit. |
| RV-03 | RESOLVED | Exact tuple equality at `tests/test_prohibited_files.py:31-33`. Negatives `.env.template`, `foo.env`, `src/ior_mvp/app.py` at `:40-45`. `normalize_path("./.env")` and backslash case at `:48-50`. Invalid UTF-8 (`b"\xff"` + constructed PAT) keeps `path:*.key` only at `:75-79`. |
| RV-04 | RESOLVED | `docs/DEVELOPMENT_GUIDE.md:19-24` states the `$(HOME)/.local/bin/uv` default and documents `make UV=uv ci` and `make UV=/path/to/uv ci`. Makefile default at `Makefile:1` is unchanged. |
| RV-05 | RESOLVED | `tests/test_ci_contract.py:84-104` asserts the exact uv and pip Gate H lines as full `splitlines()` members. Every workflow line containing `uv run` must contain `uv run --locked --extra dev`. Matches unchanged `.github/workflows/ci.yml:45-55` and `:80-84`. Order check kept at `:71-83`. |

### Test arithmetic

Scanner file: 11 path + 1 `.env.example` + 3 negatives + 1 normalize + 4 secrets + 1 NUL-binary + 1 invalid-UTF-8 + 1 deterministic + 1 parse + 1 git helper + 1 missing-file + 3 CLI wrapper + 1 real-git integration = **30**. Contract file still **7**. Focused **37**. Prior full suite 66 + 6 new cases = **72**. Matches `test_evidence.md` Fix round 1. This reviewer did not re-execute pytest.

### New-defect check

No production scanner, workflow or Makefile behaviour changed. The integration test does not commit, does not write a token literal, and does not follow the symlink (scanner `readlink` path unchanged at `scripts/check_prohibited_files.py:129-130`). No new RV-06+ findings.

### New findings

None.

Verdict: APPROVE — zero unresolved findings
