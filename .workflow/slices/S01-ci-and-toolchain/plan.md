# Slice S01 — CI Pipeline, Local Gates and Toolchain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` only after the Supervisor records plan approval. Track every implementation step with checkboxes. The Planner is not an approver and this plan does not authorize merge.

**Goal:** Make every push and pull request to `main` execute the complete deterministic release gate on uv/Python 3.12, uv/Python 3.14 and the documented pip install path, require an independent Docker image build, and give developers the same gates through one `make ci`.

**Architecture:** One least-privilege GitHub Actions workflow fans out into an uv matrix, a pip compatibility job and an independent Docker build job. Both Python jobs run the prohibited-file scanner, compile check, JavaScript syntax check and the three proof commands; the local `make ci` target runs the same gates through the locked uv environment. A standard-library scanner separates Git/file-system collection from a pure `Mapping[str, bytes] -> tuple[Finding, ...]` scan core so all matching rules are deterministic and unit-testable without Git.

**Tech stack:** GitHub Actions; `actions/checkout`; `actions/setup-python`; `astral-sh/setup-uv`; Python 3.12 and 3.14; uv lock/sync/run; pip editable extras; pytest; Make; Node `--check`; Docker.

## Global constraints

- Data classification is **PUBLIC**: repository code, frozen public evidence and explicitly synthetic fixtures. If the scanner finds credential-like text, that value becomes protected information and must never be printed, copied into evidence or sent to another service.
- Base is `main` commit `0731ae546f79c9ac3bfd92612a01f07da67937ed`; implementation branch is `slice/S01-ci-and-toolchain`.
- Do not begin implementation until the Supervisor records plan approval.
- Do not modify `src/ior_mvp/**`, `config/**`, `data/**`, `docs/core/**`, `docs/authority/**`, `Dockerfile`, `START_DEMO_WSL.sh`, `requirements.txt`, `docker-compose.yml` or `.gitignore`.
- Do not run `scripts/build_manifests.py`; this slice has no approved authority/config/snapshot change.
- Do not loosen, delete, skip or make any check optional. Do not use `continue-on-error`, `|| true` or an equivalent failure mask.
- Do not add runtime dependencies or live/network calls to tests. Dependency/action downloads are build setup, not evidence acquisition; all application proof remains against local hashed artifacts.
- `pyproject.toml` remains the dependency source. Change only `[tool.pytest.ini_options].pythonpath` to `["src", "."]`; its existing `dev` optional extra is sufficient, and no dependency, `[tool.uv]` or `[dependency-groups]` change is allowed.
- Keep `README.md`, `START_DEMO_WSL.sh` and `Dockerfile` pip paths working. `START_DEMO_WSL.sh` and `Dockerfile` remain byte-for-byte unchanged.
- Python public functions must have type hints; do not use bare `except`.
- All generated caches, virtual environments, detached scripts and logs stay untracked.
- Every implementation task ends Confirm, Validate, Test. A separate Reviewer and the Supervisor retain approval and merge authority.

---

## 1. Objective

Deliver a required CI and local-gate system that:

1. triggers on both `push` to `main` and `pull_request` targeting `main`;
2. runs, in relative order, `verify_integrity.py`, `pytest -q` and `demo_smoke.py`;
3. also runs `scripts/check_prohibited_files.py`, `python -m compileall` and `node --check src/ior_mvp/static/app.js`;
4. executes all six gates through uv on Python 3.12 and 3.14;
5. executes all six gates through `python -m pip install -e ".[dev]"` on Python 3.12;
6. builds the unchanged Dockerfile in a separate required job;
7. provides `make uv-sync`, `make lock` and a one-command `make ci`;
8. commits a generated `uv.lock`;
9. records test evidence without exposing a matched secret; and
10. preserves frozen evidence, configuration, domain behavior and the two public golden outcomes.

## 2. Governing requirement IDs

- **BC-02:** no secrets, private data or prohibited files in Git; `.env.example` placeholders only.
- **BC-04:** CI on PR/push executes integrity, tests, smoke and scans.
- **GATE-H:** release proof is integrity, pytest and smoke; manifest regeneration is conditional on an approved governed change and is prohibited in this slice.
- **TL-01:** integrity layer.
- **TL-02:** formula unit tests.
- **TL-03:** rule tests. Existing coverage is explicitly partial; S01 can execute that coverage but cannot create the missing R1-D/R3/R4-F tests assigned to S02.
- **TL-04:** four golden end-to-end cases.
- **TL-05:** AR/EN extraction golden tests.
- **TL-06:** API tests.
- **NFR-004:** offline demo, no API keys or live evidence calls.
- **NFR-008:** WSL, native Linux and Docker portability.
- **Manifest §6.10:** golden tests use hashed local snapshots only, never live sources.
- **ADR-004 / SG-TR-007:** uv is the developer/CI toolchain while the documented pip path remains supported.

## 3. Existing-state assessment

### Present

- The mandatory proof order and non-regeneration rule already exist in `AGENTS.md:38-47` and `.cursor/rules/20-proof.mdc:7-14`.
- Build control requires slice branches, plan/review separation, local gates, PR and CI in `AGENTS.md:52-61`.
- Integrity fails closed on missing files and hash mismatches in `scripts/verify_integrity.py:21-49`.
- Smoke asserts steel/public `INVESTIGATE`, steel/simulated `ADVANCE` with unchanged real state, polypropylene/public `REJECT`, and 100% extraction in `scripts/demo_smoke.py:6-24`.
- `pyproject.toml:1-38` already defines the build backend, Python `>=3.11`, runtime dependencies and the `dev` optional extra. No uv-specific configuration is required.
- The documented pip compatibility command already exists in `Makefile:3-4` and `START_DEMO_WSL.sh:4-12`.
- Docker already uses Python 3.12 and `pip install --no-cache-dir .` in `Dockerfile:1-13`.
- Existing local targets cover test, integrity/test, smoke and package separately in `Makefile:1-20`.
- Existing static-contract tests read repository files under `PROJECT_ROOT` without invoking external services in `tests/test_static_frontend.py:1-27` and `tests/test_integrity_contract.py:1-25`.
- Existing API tests use FastAPI's in-process `TestClient` in `tests/test_api.py:1-64`.
- Existing golden and leakage tests cover the two frozen public outcomes and synthetic isolation in `tests/test_golden_cases.py:7-50` and `tests/test_synthetic_isolation.py:10-43`.
- Core release authority says golden tests never call live sources and requires the three proof commands in `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:161-175,226-235`.
- NFR-004 and NFR-008 are defined in `docs/core/01_PRODUCT_AND_REQUIREMENTS.md:214-225`.
- ADR-004 selects uv plus the preserved pip path in `docs/ARCHITECTURE_DECISIONS.md:28-36`.
- The baseline recorded integrity PASS, 35 tests, smoke PASS and a clean tracked-file check in `.workflow/slices/S00-baseline-import/test_evidence.md:5-13`.
- `.gitignore:1-20` already ignores `.venv/`, `__pycache__/`, `*.py[cod]` (therefore `.pyc`), `.pytest_cache/`, `.coverage`, `htmlcov/`, `.env`, `.DS_Store`, `*.log`, build/dist/egg metadata, both `Zone.Identifier` variants, `.superpowers/` and `.workflow/logs/`.
- A root `.env` exists locally but `git check-ignore -v --no-index` confirms `.gitignore:7` excludes it, and `git ls-files` confirms it is not tracked. It was not opened and must remain unstaged; `.env.example` remains the only tracked environment template.

### Missing

- `.github/` does not exist; there is no workflow for BC-04 or Gate H.
- `uv.lock` does not exist; uv is not installed in the current WSL context (`.workflow/slices/S01-ci-and-toolchain/context.md:1-5`).
- `Makefile:1-20` has no `ci`, `uv-sync` or `lock` target.
- No tracked-path/secret scanner exists.
- No unit tests cover scanner matching, binary handling, sanitized output or Git failure.
- No static test protects workflow triggers, permissions, matrices, caching, required commands or non-optional failure behavior.
- `README.md:70-89` documents `make verify` but not uv, `make ci` or CI job coverage.
- `docs/DEVELOPMENT_GUIDE.md` does not exist.
- `docs/REQUIREMENTS_TRACEABILITY.md:90-118` records GATE-H and BC-04 as `NOT_STARTED`; relevant test layers are only `IMPLEMENTED`.
- `docs/KNOWN_LIMITATIONS.md:7-18` keeps KL-09 open because proof is manual.
- `.gitignore` does **not** ignore `*.pem`, `*.key` or `*.p12`; `.gitignore` is out of S01 scope, so the scanner must reject any such tracked path. `.env.example` is deliberately tracked and must remain allowed.
- A source search found no outbound HTTP client or `http(s)://` use in `src/**/*.py`, `tests/**/*.py` or `scripts/**/*.py`; CI must preserve that offline proof boundary.
- `docs/project/` is absent. No project fact is inferred from another engagement; this plan uses the current repository authorities, slice context and owner task contract only.

## 4. Relevant existing code and contracts

- `pyproject.toml`: single dependency declaration; use `uv sync --locked --extra dev` and pip editable install from this file.
- `Makefile`: preserve all existing target recipes exactly and append the uv/local-CI targets.
- `Dockerfile`: unchanged pip/runtime compatibility target; the Docker job builds it directly.
- `START_DEMO_WSL.sh`: unchanged user-facing pip startup path.
- `scripts/verify_integrity.py`: first proof command; no manifest rewrite.
- `scripts/demo_smoke.py`: third proof command and golden outcome smoke.
- `src/ior_mvp/static/app.js`: existing JavaScript artifact checked with Node syntax mode only.
- `tests/test_static_frontend.py` and `tests/test_integrity_contract.py`: style precedent for `test_ci_contract.py`.
- `.workflow/slices/S01-ci-and-toolchain/context.md`: approved uv install command, branch/base, execution reliability and protected governed-file boundary.

## 5. Files to create or change

### Create

- `.github/workflows/ci.yml` — required GitHub Actions workflow.
- `scripts/check_prohibited_files.py` — standard-library scanner and CLI.
- `tests/test_prohibited_files.py` — pure scanner/CLI behavior tests.
- `tests/test_ci_contract.py` — static workflow contract tests.
- `uv.lock` — generated by uv from unchanged dependency declarations in `pyproject.toml`.
- `docs/DEVELOPMENT_GUIDE.md` — uv, pip, CI, local gates and failure guidance.
- `.workflow/slices/S01-ci-and-toolchain/implementation_log.md` — Implementer change ledger.
- `.workflow/slices/S01-ci-and-toolchain/test_evidence.md` — actual command outputs, exits and later CI links.

### Change

- `Makefile` — add `UV`, `UV_RUN`, `.PHONY` entries and `uv-sync`, `lock`, `ci` targets; preserve all existing targets.
- `pyproject.toml` — test configuration only: set `[tool.pytest.ini_options].pythonpath = ["src", "."]`; do not change dependencies.
- `README.md` — add only a short `CI and local gates` subsection.
- `docs/REQUIREMENTS_TRACEABILITY.md` — update only the rows listed in §21, with evidence-backed status.
- `docs/KNOWN_LIMITATIONS.md` — close KL-09 only at the completion/merge evidence gate.

### Explicitly unchanged

- `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `START_DEMO_WSL.sh`, `.env.example`, `.gitignore`.
- All domain, governed authority/configuration and evidence files.

## 6. Architecture

### CI job graph

- Workflow trigger creates three independent required branches:
  - `uv-gates` matrix leg for Python 3.12;
  - `uv-gates` matrix leg for Python 3.14;
  - `pip-gates` for Python 3.12 and the exact documented editable dev install;
  - `docker-build` for the unchanged Dockerfile.
- GitHub represents the two uv matrix legs separately. `strategy.fail-fast: false` ensures one failing Python version does not suppress evidence from the other.
- No job has `needs`; all start independently so a failing Python gate does not hide Docker compatibility and vice versa.
- Every job is required by workflow semantics: no conditional skip, no `continue-on-error`.

### Triggers and concurrency

- Trigger only `push.branches: [main]` and `pull_request.branches: [main]`.
- Workflow-level concurrency group is `ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`.
- `cancel-in-progress: true` cancels superseded runs for the same PR/ref; different PRs and branches do not cancel one another.

### Permissions

- Workflow-level permissions are exactly `contents: read`.
- `actions/checkout` sets `persist-credentials: false`.
- No job receives repository secrets or a write-capable token.

### Caching policy

- uv jobs use `astral-sh/setup-uv`'s built-in cache keyed from `uv.lock`; `uv sync --locked` prevents cache contents from changing the locked resolution.
- The pip job uses `actions/setup-python`'s pip cache keyed from `pyproject.toml`; this is a compatibility canary against the declared ranges, not the reproducible uv path.
- There is no Node dependency cache because the repository has no Node package manifest.
- The Docker build uses no remote layer cache in S01; it builds the small image from the checked-out tree without requiring cache-write permissions.

### Exact `.github/workflows/ci.yml` draft

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  uv-gates:
    name: uv / Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version:
          - "3.12"
          - "3.14"
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Set up uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: uv.lock
      - name: Sync locked development environment
        run: uv sync --locked --extra dev --python "${{ matrix.python-version }}"
      - name: Scan prohibited files and secret patterns
        run: uv run --locked --extra dev python scripts/check_prohibited_files.py
      - name: Compile Python
        run: uv run --locked --extra dev python -m compileall -q src scripts tests
      - name: Check JavaScript syntax
        run: node --check src/ior_mvp/static/app.js
      - name: Verify integrity
        run: PYTHONPATH=src uv run --locked --extra dev python scripts/verify_integrity.py
      - name: Run test suite
        run: PYTHONPATH=src uv run --locked --extra dev pytest -q
      - name: Run demo smoke
        run: PYTHONPATH=src uv run --locked --extra dev python scripts/demo_smoke.py

  pip-gates:
    name: pip / Python 3.12
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pyproject.toml
      - name: Install documented pip development path
        run: python -m pip install -e ".[dev]"
      - name: Scan prohibited files and secret patterns
        run: python scripts/check_prohibited_files.py
      - name: Compile Python
        run: python -m compileall -q src scripts tests
      - name: Check JavaScript syntax
        run: node --check src/ior_mvp/static/app.js
      - name: Verify integrity
        run: PYTHONPATH=src python scripts/verify_integrity.py
      - name: Run test suite
        run: PYTHONPATH=src pytest -q
      - name: Run demo smoke
        run: PYTHONPATH=src python scripts/demo_smoke.py

  docker-build:
    name: Docker image build
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Build image
        run: docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:ci .
```

## 7. Scanner algorithm

### Required path rules, in deterministic reporting order

1. `Zone.Identifier` — substring anywhere in the normalized tracked path.
2. `.env` exactly — any complete path component equal to `.env`; `.env.example` is a different component and is allowed.
3. `.venv/` — any path component equal to `.venv`.
4. `__pycache__` — any path component equal to `__pycache__`.
5. `*.pyc` — basename suffix, compared case-insensitively.
6. `.DS_Store` — any complete path component equal to `.DS_Store`.
7. `*.pem` — basename suffix, compared case-insensitively.
8. `*.key` — basename suffix, compared case-insensitively.
9. `*.p12` — basename suffix, compared case-insensitively.
10. `.workflow/logs/` — normalized root-relative path equal to `.workflow/logs` or beginning `.workflow/logs/`.

Backslashes normalize to `/`; leading `./` segments are removed without stripping the leading dot from `.env`.

### Required secret regexes

- `ghp_[A-Za-z0-9]{36}` — report rule `secret:github-pat`.
- `AKIA[0-9A-Z]{16}` — report rule `secret:aws-access-key`.
- `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----` — report rule `secret:private-key-header`.
- `sk-[A-Za-z0-9]{20,}` — report rule `secret:sk-token`.

Tests construct matching examples at runtime by concatenation/repetition; no tracked test source contains a complete token-like fixture.

### Enumeration and text/binary handling

- Invoke exactly `git ls-files -z` with `cwd=ROOT`, capture bytes and split only on NUL.
- Sort decoded paths before reading/scanning; mapping insertion order cannot alter output.
- Read regular tracked files as bytes.
- Do not follow tracked symlinks. Scan the symlink target text itself.
- A tracked payload is text only if it contains no NUL byte and decodes as strict UTF-8. Path rules still apply to binary files; secret regexes skip binary payloads.
- A missing Git executable, non-zero `git ls-files -z`, malformed empty path or unreadable tracked file is a `ScannerError`, never a clean result.
- Findings are immutable, de-duplicated and sorted by `(path, rule)`.
- Failure output contains only normalized path and rule identifier. It never includes matched text, line content or subprocess stderr.

### Exact `scripts/check_prohibited_files.py` draft

```python
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    rule: str


class ScannerError(RuntimeError):
    """Raised when the repository cannot be scanned safely."""


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("secret:github-pat", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("secret:aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "secret:private-key-header",
        re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("secret:sk-token", re.compile(r"sk-[A-Za-z0-9]{20,}")),
)


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def prohibited_path_rules(path: str) -> tuple[str, ...]:
    normalized = normalize_path(path)
    parts = tuple(part for part in normalized.split("/") if part)
    basename = parts[-1] if parts else normalized
    lowercase_basename = basename.lower()
    rules: list[str] = []

    if "Zone.Identifier" in normalized:
        rules.append("path:Zone.Identifier")
    if ".env" in parts:
        rules.append("path:.env")
    if ".venv" in parts:
        rules.append("path:.venv/")
    if "__pycache__" in parts:
        rules.append("path:__pycache__")
    if lowercase_basename.endswith(".pyc"):
        rules.append("path:*.pyc")
    if ".DS_Store" in parts:
        rules.append("path:.DS_Store")
    if lowercase_basename.endswith(".pem"):
        rules.append("path:*.pem")
    if lowercase_basename.endswith(".key"):
        rules.append("path:*.key")
    if lowercase_basename.endswith(".p12"):
        rules.append("path:*.p12")
    if normalized == ".workflow/logs" or normalized.startswith(".workflow/logs/"):
        rules.append("path:.workflow/logs/")

    return tuple(rules)


def decode_tracked_text(content: bytes) -> str | None:
    if b"\x00" in content:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan_tracked_files(files: Mapping[str, bytes]) -> tuple[Finding, ...]:
    findings: set[Finding] = set()
    for raw_path in sorted(files):
        path = normalize_path(raw_path)
        for rule in prohibited_path_rules(path):
            findings.add(Finding(path=path, rule=rule))

        text = decode_tracked_text(files[raw_path])
        if text is None:
            continue
        for rule, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.add(Finding(path=path, rule=rule))

    return tuple(sorted(findings))


def parse_git_ls_files(output: bytes) -> tuple[str, ...]:
    raw_paths = output.split(b"\0")
    if raw_paths and raw_paths[-1] == b"":
        raw_paths.pop()
    if any(raw_path == b"" for raw_path in raw_paths):
        raise ScannerError("git ls-files returned an empty tracked path")
    return tuple(sorted(os.fsdecode(raw_path) for raw_path in raw_paths))


def git_tracked_paths(root: Path) -> tuple[str, ...]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as error:
        raise ScannerError("git executable not found") from error
    if result.returncode != 0:
        raise ScannerError(f"git ls-files failed with exit code {result.returncode}")
    return parse_git_ls_files(result.stdout)


def load_tracked_files(root: Path, paths: Sequence[str]) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in paths:
        candidate = root / path
        try:
            if candidate.is_symlink():
                files[path] = os.fsencode(os.readlink(candidate))
            else:
                files[path] = candidate.read_bytes()
        except OSError as error:
            raise ScannerError(f"unable to read tracked file: {path}") from error
    return files


def scan_repository(root: Path) -> tuple[tuple[Finding, ...], int]:
    paths = git_tracked_paths(root)
    files = load_tracked_files(root, paths)
    return scan_tracked_files(files), len(paths)


def main(root: Path = ROOT) -> int:
    try:
        findings, tracked_count = scan_repository(root)
    except ScannerError as error:
        print(f"PROHIBITED FILE SCAN ERROR: {error}", file=sys.stderr)
        return 2

    if findings:
        print("PROHIBITED FILE SCAN FAIL", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.path}: {finding.rule}", file=sys.stderr)
        return 1

    print(f"PROHIBITED FILE SCAN PASS ({tracked_count} tracked files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 8. Deterministic rules

- The scanner depends only on the exact tracked path strings and bytes supplied to `scan_tracked_files`; it reads no environment variable, clock, network resource or random source.
- Matching is case-sensitive except the four file suffixes `.pyc`, `.pem`, `.key` and `.p12`, which use a lowercase basename to prevent case-based bypass.
- `.env.example`, `.env.template` and names containing `.env` are allowed unless a complete component is exactly `.env`.
- A file matching more than one rule reports every distinct `(path, rule)` pair once.
- Binary classification is deterministic: NUL byte or invalid strict UTF-8 means binary.
- Secret scans stop at existence; they do not report count, offset, line or matched value.
- CI uses only the committed lock on the uv path (`--locked`) and must fail if `pyproject.toml` and `uv.lock` disagree.
- The pip path intentionally resolves the current versions allowed by unchanged `pyproject.toml` dependency declarations; it is a compatibility check, not the reproducible primary path.
- Gate order in both Python jobs and `make ci` is scanner → compileall → Node syntax → integrity → pytest → smoke. The three authoritative proof commands retain their required relative order.
- Tests never invoke live evidence sources. The scanner tests use in-memory bytes; the CI contract test reads local YAML text; all existing domain tests use frozen files/in-process API calls.

## 9. API changes

None. No endpoint, payload, schema, package entry point or domain function changes.

## 10. UI changes

None. `app.js` is read-only in this slice and receives syntax validation only.

## 11. Integration points

### Makefile

- Keep `install`, `test`, `verify`, `run`, `smoke` and `package` recipes unchanged.
- Default `UV` to the approved user-scoped installer location. A developer with uv elsewhere can override it (`make UV=uv ci`) without changing the file.
- `uv-sync` validates and installs from the committed lock.
- `lock` is the deliberate lock-regeneration command; it does not upgrade dependencies implicitly.
- `ci` depends on `uv-sync` and runs every local gate once.

Exact resulting `Makefile` draft:

```make
UV ?= $(HOME)/.local/bin/uv
NODE ?= node
UV_RUN = $(UV) run --locked --extra dev

.PHONY: install test verify run smoke package uv-sync lock ci

install:
	python3 -m pip install -e ".[dev]"

test:
	PYTHONPATH=src pytest -q

verify:
	PYTHONPATH=src python3 scripts/verify_integrity.py
	PYTHONPATH=src pytest -q

run:
	PYTHONPATH=src uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000 --reload

smoke:
	PYTHONPATH=src python3 scripts/demo_smoke.py

package:
	bash scripts/package_project.sh

uv-sync:
	$(UV) sync --locked --extra dev

lock:
	$(UV) lock

ci: uv-sync
	$(UV_RUN) python scripts/check_prohibited_files.py
	$(UV_RUN) python -m compileall -q src scripts tests
	$(NODE) --check src/ior_mvp/static/app.js
	PYTHONPATH=src $(UV_RUN) python scripts/verify_integrity.py
	PYTHONPATH=src $(UV_RUN) pytest -q
	PYTHONPATH=src $(UV_RUN) python scripts/demo_smoke.py
```

### README

Add one short subsection after `Integrity and tests`, without rewriting start/Docker instructions:

~~~~markdown
## CI and local gates

GitHub Actions runs the prohibited-file scan, Python compile check, JavaScript syntax check, integrity verification, full test suite and demo smoke on uv/Python 3.12, uv/Python 3.14 and the documented pip path; it also builds the Docker image.

After installing uv as described in `docs/DEVELOPMENT_GUIDE.md`, reproduce the required gates locally with:

```bash
make ci
```

The existing `pip install -e ".[dev]"`, `START_DEMO_WSL.sh` and Docker paths remain supported.
~~~~

### Development guide

Create `docs/DEVELOPMENT_GUIDE.md` with these concrete sections and commands:

1. `Authority and data boundary` — PUBLIC classification; frozen local evidence; no keys; never run `build_manifests.py` in S01.
2. `Prerequisites` — WSL/native Linux, Python 3.12 or 3.14, Git, Make, Node (for `node --check`) and Docker only for the Docker compatibility check. Explain that Make defaults `NODE ?= node`; when Node is installed user-scoped under `~/.local/node`, run `make NODE=$HOME/.local/node/bin/node ci` without editing shell rc files.
3. `Install uv without changing shell profiles`:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
   ~/.local/bin/uv --version
   make uv-sync
   ```

4. `Run all local gates`:

   ```bash
   make ci
   ```

   List the six gates in their exact execution order and state that any non-zero exit blocks review.
5. `Maintain the lock`:

   ```bash
   make lock
   make uv-sync
   ```

   Regenerate only after an intentional `pyproject.toml` dependency change, review the `uv.lock` diff, and do not use opportunistic `--upgrade`.
6. `Preserved pip compatibility path`:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -e ".[dev]"
   python scripts/check_prohibited_files.py
   python -m compileall -q src scripts tests
   node --check src/ior_mvp/static/app.js
   PYTHONPATH=src python scripts/verify_integrity.py
   PYTHONPATH=src pytest -q
   PYTHONPATH=src python scripts/demo_smoke.py
   ```

7. `Docker compatibility`:

   ```bash
   docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:local .
   ```

8. `CI topology and caches` — describe the two uv matrix legs, pip job, Docker job, read-only permissions and lock/cache semantics from §6.
9. `Failure interpretation` — exit 1 finding, exit 2 scanner execution error, stale lock, test/integrity/smoke failure, Node syntax failure and Docker build failure.
10. `Evidence and review` — logs stay under ignored `.workflow/logs/`; sanitized evidence goes in the slice test record; a green run is evidence, not approval.

## 12. Failure behavior

- **Scanner finding:** exit 1; print `PROHIBITED FILE SCAN FAIL`, then sorted `path: rule` lines; Python job and `make ci` stop.
- **Scanner execution problem:** exit 2; print one sanitized `PROHIBITED FILE SCAN ERROR` line; never pass because Git/file input is unavailable.
- **Stale/missing lock:** `uv sync --locked` exits non-zero before uv proof commands.
- **Compile failure:** `python -m compileall` exits non-zero and blocks the Python leg.
- **JavaScript syntax failure:** `node --check` exits non-zero and blocks the Python leg.
- **Integrity mismatch/missing governed artifact:** `verify_integrity.py` exits 1; do not regenerate hashes.
- **Pytest failure:** job exits non-zero; do not change/skip an expectation merely to pass.
- **Smoke assertion failure:** job exits non-zero; treat a changed golden state as an implementation/authority investigation.
- **pip install failure:** pip compatibility job is red even if uv passes.
- **one uv Python failure:** that matrix leg is red; `fail-fast: false` lets the other leg finish, but the workflow remains failed.
- **Docker build failure:** independent Docker job is red even if Python jobs pass.
- **superseded run:** concurrency cancels only the older run for the same PR/ref. A cancelled run is not acceptance evidence.

## 13. Unknown or missing-input behavior

- Git executable absent → scanner error exit 2.
- Not a Git work tree / `git ls-files -z` non-zero → scanner error exit 2.
- Tracked file absent, unreadable, a directory/submodule path or otherwise not safely readable → scanner error exit 2.
- Empty but successful tracked set → deterministic clean scan with count 0; CI contract still proves checkout and this repository normally has tracked files.
- Invalid UTF-8/NUL payload → treat as binary and skip only secret content matching; path rules still run.
- Symlink → scan link target bytes and never dereference it.
- Node unavailable locally → `make ci` fails; the guide identifies Node as a prerequisite.
- Docker unavailable locally → only the optional local Docker validation is unavailable; required GitHub Docker evidence must still be green.
- uv unavailable locally → `make ci` fails at the approved `~/.local/bin/uv` path; install with the approved user-scoped command, do not modify shell rc files or install system-wide.
- A required policy value or dependency change not present in repository authority → stop and request an owner decision; do not add it to `pyproject.toml`.

## 14. Privacy and security implications

- Workflow permission is `contents: read`; checkout does not persist credentials.
- No workflow secret is referenced. Fork/PR code receives no privileged token.
- The scanner reads only the checked-out work tree's Git-tracked paths; untracked local files are outside its declared Git-entry control.
- Secret matches are never echoed. Evidence records may contain only path, rule, command, exit and pass/fail outcome.
- Subprocess stderr is captured but deliberately not relayed, avoiding accidental credential-bearing Git configuration text.
- Symlinks are not followed, preventing a tracked link from reading an external local file.
- CI installs declared public dependencies/actions over the network, but no application test acquires live industrial evidence.
- Do not plant a real or realistic credential in Git for testing. Tests construct token shapes in memory.
- GitHub action major tags are used because no repository policy supplies immutable action SHAs. Changing to SHA pinning is a separate supply-chain policy decision, not a silent S01 addition.

## 15. Concurrency implications

- Matrix and pip/Docker jobs can run concurrently without shared writable state.
- Every job receives a fresh checkout and isolated runner; uv/pip caches are content-addressed accelerators, not shared virtual environments.
- `fail-fast: false` maximizes diagnostic evidence across Python versions.
- `cancel-in-progress: true` reduces wasted runs while keeping PRs/ref groups isolated.
- Scanner output order is stable even if filesystem/Git enumeration order differs.
- Local `make ci` is intentionally serial so the first failed gate stops later gates and preserves the authority proof order.

## 16. Versioning implications

- `uv.lock` becomes a committed generated artifact controlling the developer/uv CI dependency graph.
- The lock must resolve the existing `requires-python = ">=3.11"` project across the required Python 3.12 and 3.14 legs.
- Python 3.12 is the pip and Docker compatibility floor demonstrated by this slice; Python 3.14 validates the current workstation/new interpreter path.
- `make lock` runs `uv lock` without `--upgrade`. Future intentional dependency changes must regenerate and review the lock in the same authorized slice.
- A changed `pyproject.toml` dependency declaration with stale `uv.lock` fails `--locked`; the pytest-only `pythonpath` change does not alter the lock, and no automatic CI lock rewrite is permitted.
- Application version `0.1.0`, authority hashes, snapshot manifests and config versions do not change.
- ADR-004 remains the governing proposed decision document; `docs/ARCHITECTURE_DECISIONS.md` is outside the approved S01 edit list, so this plan does not change its status.

## 17. Compatibility

- **uv:** primary reproducible developer path using optional extra `dev`.
- **pip:** exact existing `python -m pip install -e ".[dev]"` path tested on Python 3.12.
- **WSL:** `make ci` defaults to the approved `~/.local/bin/uv`; current workstation proof is recorded separately.
- **native Linux:** GitHub `ubuntu-latest` runs uv and pip jobs.
- **Docker:** unchanged `python:3.12-slim` image and pip install build.
- **Demo startup:** `START_DEMO_WSL.sh` remains unchanged and continues creating `.venv`, using pip and running integrity/tests before Uvicorn.
- **No frontend build tool:** runner-provided Node is used only for `node --check`; no package manifest or Node dependency is introduced.

## 18. Tests

### Exact `tests/test_prohibited_files.py` draft

```python
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

import scripts.check_prohibited_files as scanner
from scripts.check_prohibited_files import Finding, ScannerError


@pytest.mark.parametrize(
    ("path", "rule"),
    [
        ("download:Zone.Identifier", "path:Zone.Identifier"),
        (".env", "path:.env"),
        ("nested/.env/value", "path:.env"),
        (".venv/bin/python", "path:.venv/"),
        ("pkg/__pycache__/module.py", "path:__pycache__"),
        ("pkg/module.PYC", "path:*.pyc"),
        ("assets/.DS_Store", "path:.DS_Store"),
        ("certs/server.PEM", "path:*.pem"),
        ("certs/server.KEY", "path:*.key"),
        ("certs/server.P12", "path:*.p12"),
        (".workflow/logs/run.log", "path:.workflow/logs/"),
    ],
)
def test_scan_tracked_files_flags_every_prohibited_path(path: str, rule: str) -> None:
    assert Finding(path=path, rule=rule) in scanner.scan_tracked_files({path: b"safe"})


def test_scan_tracked_files_allows_env_example() -> None:
    assert scanner.scan_tracked_files({".env.example": b"IOR_HOST=127.0.0.1\n"}) == ()


@pytest.mark.parametrize(
    ("content", "rule"),
    [
        (("ghp_" + "A" * 36).encode(), "secret:github-pat"),
        (("AKIA" + "A" * 16).encode(), "secret:aws-access-key"),
        (
            ("-" * 5 + "BEGIN OPENSSH PRIVATE KEY" + "-" * 5).encode(),
            "secret:private-key-header",
        ),
        (("sk-" + "A" * 20).encode(), "secret:sk-token"),
    ],
)
def test_scan_tracked_files_flags_each_secret_pattern(content: bytes, rule: str) -> None:
    findings = scanner.scan_tracked_files({"fixture.txt": content})
    assert findings == (Finding(path="fixture.txt", rule=rule),)


def test_scan_tracked_files_skips_secret_matching_for_binary_content() -> None:
    content = b"\x00" + ("ghp_" + "A" * 36).encode()
    assert scanner.scan_tracked_files({"image.bin": content}) == ()


def test_scan_tracked_files_is_deterministic() -> None:
    first = {".env": b"x", "private.key": b"y"}
    second = {"private.key": b"y", ".env": b"x"}
    assert scanner.scan_tracked_files(first) == scanner.scan_tracked_files(second)
    assert scanner.scan_tracked_files(first) == tuple(sorted(scanner.scan_tracked_files(first)))


def test_parse_git_ls_files_uses_nul_delimiters() -> None:
    assert scanner.parse_git_ls_files(b"b file.txt\0a.txt\0") == ("a.txt", "b file.txt")


def test_git_tracked_paths_invokes_nul_delimited_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_run(
        command: list[str],
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[bytes]:
        assert command == ["git", "ls-files", "-z"]
        assert kwargs["cwd"] == tmp_path
        return subprocess.CompletedProcess(
            command,
            returncode=0,
            stdout=b"b.txt\0a.txt\0",
            stderr=b"",
        )

    monkeypatch.setattr(scanner.subprocess, "run", fake_run)
    assert scanner.git_tracked_paths(tmp_path) == ("a.txt", "b.txt")


def test_load_tracked_files_fails_closed_for_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ScannerError, match="unable to read tracked file: missing.txt"):
        scanner.load_tracked_files(tmp_path, ("missing.txt",))


def test_main_returns_one_for_a_planted_zone_identifier(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    finding = Finding(
        path="scanner-probe:Zone.Identifier",
        rule="path:Zone.Identifier",
    )
    monkeypatch.setattr(scanner, "scan_repository", lambda _root: ((finding,), 1))

    assert scanner.main(Path("/repository")) == 1
    captured = capsys.readouterr()
    assert "PROHIBITED FILE SCAN FAIL" in captured.err
    assert "scanner-probe:Zone.Identifier: path:Zone.Identifier" in captured.err


def test_main_never_prints_a_matched_secret(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret = "ghp_" + "A" * 36
    findings = scanner.scan_tracked_files({"fixture.txt": secret.encode()})
    monkeypatch.setattr(scanner, "scan_repository", lambda _root: (findings, 1))

    assert scanner.main(Path("/repository")) == 1
    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err
    assert "fixture.txt: secret:github-pat" in captured.err


def test_main_returns_two_when_git_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_scan(_root: Path) -> tuple[tuple[Finding, ...], int]:
        raise ScannerError("git executable not found")

    monkeypatch.setattr(scanner, "scan_repository", fail_scan)
    assert scanner.main(Path("/repository")) == 2
    assert "PROHIBITED FILE SCAN ERROR: git executable not found" in capsys.readouterr().err
```

### Exact `tests/test_ci_contract.py` draft

```python
from __future__ import annotations

from typing import Any

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT

WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"


def _workflow() -> dict[str, Any]:
    assert WORKFLOW.exists()
    payload = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(payload, dict)
    return payload


def _run_commands(job: dict[str, Any]) -> str:
    return "\n".join(
        step["run"]
        for step in job["steps"]
        if isinstance(step, dict) and "run" in step
    )


def _used_actions(job: dict[str, Any]) -> list[str]:
    return [
        step["uses"]
        for step in job["steps"]
        if isinstance(step, dict) and "uses" in step
    ]


def test_ci_workflow_triggers_on_push_and_pull_request_to_main() -> None:
    workflow = _workflow()
    assert set(workflow["on"]) == {"push", "pull_request"}
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert workflow["on"]["pull_request"]["branches"] == ["main"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "true"
    group = workflow["concurrency"]["group"]
    assert "github.workflow" in group
    assert "github.event.pull_request.number || github.ref" in group


def test_uv_job_covers_python_312_and_314_with_locked_cache() -> None:
    job = _workflow()["jobs"]["uv-gates"]
    assert job["strategy"]["fail-fast"] == "false"
    assert job["strategy"]["matrix"]["python-version"] == ["3.12", "3.14"]
    assert "actions/setup-python@v5" in _used_actions(job)
    setup_uv = next(step for step in job["steps"] if step.get("uses") == "astral-sh/setup-uv@v6")
    assert setup_uv["with"]["enable-cache"] == "true"
    assert setup_uv["with"]["cache-dependency-glob"] == "uv.lock"
    assert 'uv sync --locked --extra dev --python "${{ matrix.python-version }}"' in _run_commands(job)


def test_pip_job_uses_the_documented_editable_dev_install() -> None:
    job = _workflow()["jobs"]["pip-gates"]
    setup_python = next(step for step in job["steps"] if step.get("uses") == "actions/setup-python@v5")
    assert setup_python["with"]["python-version"] == "3.12"
    assert setup_python["with"]["cache"] == "pip"
    assert setup_python["with"]["cache-dependency-path"] == "pyproject.toml"
    assert 'python -m pip install -e ".[dev]"' in _run_commands(job)


@pytest.mark.parametrize("job_name", ["uv-gates", "pip-gates"])
def test_each_python_job_runs_every_required_gate(job_name: str) -> None:
    commands = _run_commands(_workflow()["jobs"][job_name])
    required_fragments = (
        "python scripts/check_prohibited_files.py",
        "python -m compileall -q src scripts tests",
        "node --check src/ior_mvp/static/app.js",
        "python scripts/verify_integrity.py",
        "pytest -q",
        "python scripts/demo_smoke.py",
    )
    for fragment in required_fragments:
        assert fragment in commands
    assert [commands.index(fragment) for fragment in required_fragments] == sorted(
        commands.index(fragment) for fragment in required_fragments
    )


def test_docker_build_job_builds_the_repository_dockerfile() -> None:
    workflow = _workflow()
    job = workflow["jobs"]["docker-build"]
    assert "actions/checkout@v4" in _used_actions(job)
    assert (
        "docker build --file Dockerfile "
        "--tag industrial-opportunity-resolution-mvp:ci ."
    ) in _run_commands(job)


def test_ci_workflow_contains_no_optional_failure_escape() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "continue-on-error" not in text
    assert "|| true" not in text
    workflow = _workflow()
    assert set(workflow["jobs"]) == {"uv-gates", "pip-gates", "docker-build"}
    for job in workflow["jobs"].values():
        assert "if" not in job
        assert "needs" not in job
        for step in job["steps"]:
            assert "if" not in step
            assert "continue-on-error" not in step
            if "uses" in step and step["uses"] == "actions/checkout@v4":
                assert step["with"]["persist-credentials"] == "false"
```

### Required test names and assertions

- `test_scan_tracked_files_flags_every_prohibited_path`: every approved path rule, including case-insensitive suffixes.
- `test_scan_tracked_files_allows_env_example`: `.env.example` produces no finding.
- `test_scan_tracked_files_flags_each_secret_pattern`: all four regexes detect runtime-constructed values.
- `test_scan_tracked_files_skips_secret_matching_for_binary_content`: NUL payload does not undergo secret matching.
- `test_scan_tracked_files_is_deterministic`: mapping order does not change sorted output.
- `test_parse_git_ls_files_uses_nul_delimiters`: spaces survive and NUL boundaries parse correctly.
- `test_git_tracked_paths_invokes_nul_delimited_git`: subprocess command is exactly `git ls-files -z`.
- `test_load_tracked_files_fails_closed_for_a_missing_file`: unreadable/missing tracked input raises the scanner error instead of passing.
- `test_main_returns_one_for_a_planted_zone_identifier`: red half of scanner red-green; exit 1 and sanitized listing.
- `test_main_never_prints_a_matched_secret`: no value in stdout/stderr.
- `test_main_returns_two_when_git_is_unavailable`: missing input fails closed.
- `test_ci_workflow_triggers_on_push_and_pull_request_to_main`: triggers, read-only permissions and concurrency.
- `test_uv_job_covers_python_312_and_314_with_locked_cache`: matrix, action, cache and locked sync.
- `test_pip_job_uses_the_documented_editable_dev_install`: exact install and pip cache.
- `test_each_python_job_runs_every_required_gate`: scanner, compile, Node, integrity, pytest and smoke in both Python job definitions.
- `test_docker_build_job_builds_the_repository_dockerfile`: independent required build command.
- `test_ci_workflow_contains_no_optional_failure_escape`: no conditional/optional failure bypass and checkout credentials are not persisted.

## 19. Validators

Run these without changing governed artifacts:

1. Targeted scanner tests.
2. Targeted workflow contract tests (also parses YAML).
3. Actual clean scanner CLI exit 0.
4. Actual planted tracked-path scanner CLI exit 1, then clean removal and exit 0.
5. `make ci` through uv.
6. Clean pip virtual-environment install and the same six gates.
7. `docker build` of the unchanged Dockerfile.
8. `git diff --check`.
9. `git status --short` and `git ls-files` hygiene review.
10. Required GitHub Actions run: both uv matrix legs, pip job and Docker job green.
11. Independent different-model review with zero findings.

Do not run `scripts/build_manifests.py`. Integrity should pass against existing hashes.

## 20. Acceptance criteria

- [ ] Branch is `slice/S01-ci-and-toolchain` at base `0731ae546f79c9ac3bfd92612a01f07da67937ed`.
- [ ] Supervisor plan approval is recorded before implementation.
- [ ] Only approved paths are changed; no domain/config/data/core/authority file changes.
- [ ] `uv.lock` is generated from unchanged dependency declarations; changing only pytest `pythonpath` to `["src", "."]` leaves `uv.lock` unaffected and `uv sync --locked --extra dev` still succeeds.
- [ ] Workflow triggers on push and pull request to `main`.
- [ ] Workflow permission is only `contents: read`; checkout credentials are not persisted.
- [ ] Concurrency groups runs per PR/ref and cancels superseded runs.
- [ ] uv/Python 3.12 and uv/Python 3.14 each run all six required gates.
- [ ] pip/Python 3.12 installs exactly `-e ".[dev]"` and runs all six required gates.
- [ ] Docker image build is an independent non-optional job.
- [ ] No `continue-on-error`, conditional job skip or failure masking exists.
- [ ] Scanner enumerates with `git ls-files -z`, applies all ten path patterns and four exact secret regexes, and allows `.env.example`.
- [ ] Scanner pure function tests do not invoke Git.
- [ ] Secret findings never expose the value.
- [ ] Git absence/read failure exits 2, not 0.
- [ ] Planted `Zone.Identifier` path produces exit 1; cleanup restores exit 0.
- [ ] `make ci` runs scanner, compile, Node, integrity, pytest and smoke in required order.
- [ ] No live evidence source is called; golden tests use current hashed local snapshots.
- [ ] Existing pip startup and Dockerfile remain unchanged and working.
- [ ] Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`.
- [ ] README change is limited to the short subsection; development guide documents both paths and all gates.
- [ ] Traceability status reflects actual evidence and preserves TL-03's known partial coverage.
- [ ] KL-09 is not declared closed until required CI is green and merge/completion evidence exists.
- [ ] `implementation_log.md` and `test_evidence.md` contain actual outputs/exit codes, assumptions and limitations, but no secret values.
- [ ] Independent reviewer reports zero findings; the builder does not self-approve.
- [ ] Supervisor—not Planner/Implementer/Reviewer—authorizes PR merge.

## 21. Documentation changes

- `README.md`: only the short subsection in §11; do not alter demo claims, start commands, Docker commands or evidence-mode explanation.
- `docs/DEVELOPMENT_GUIDE.md`: create the ten-section developer/runbook content specified in §11.
- `docs/REQUIREMENTS_TRACEABILITY.md`: update only evidence-backed rows listed below; retain the status definitions and all unrelated rows.
- `docs/KNOWN_LIMITATIONS.md`: move KL-09 only when completion evidence exists; retain every other limitation exactly.
- `.workflow/slices/S01-ci-and-toolchain/implementation_log.md`: record file-by-file changes, why they were authorized, lock-generation command/tool version, confirmation that governed files were untouched, and assumptions.
- `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`: record command, environment/Python/tool version, actual output summary, exit status and evidence path/URL. Never paste a detected credential value.

## 22. Requirement traceability updates

Evidence pointers to add where applicable:

- `.github/workflows/ci.yml`
- `scripts/check_prohibited_files.py`
- `tests/test_prohibited_files.py`
- `tests/test_ci_contract.py`
- `Makefile`
- `uv.lock`
- `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`
- exact GitHub Actions run URL after it exists

Status transitions must follow evidence, not anticipation:

- **BC-02:** `PLANNED` → `TESTED` after scanner unit tests, actual red-green probe and clean tracked scan pass; later merge/completion may promote it under the repository status policy.
- **BC-04:** `NOT_STARTED` → `IMPLEMENTED` when workflow/contract tests exist; → `TESTED` only after an actual push/PR run shows all four displayed jobs/legs green.
- **GATE-H:** `NOT_STARTED` → `IMPLEMENTED` when workflow/local target contain the three proof commands; → `TESTED` after local and GitHub evidence. Record `build_manifests.py: NOT RUN — no governed change; prohibited by S01 scope`.
- **TL-01:** `IMPLEMENTED` → `TESTED` when integrity, integrity-contract and synthetic-isolation tests execute in CI.
- **TL-02:** `IMPLEMENTED` → `TESTED` when formula suites execute in CI.
- **TL-03:** `IMPLEMENTED (partial)` → at most `TESTED (partial; existing cases executed in CI; R1-D boundary, R3 explicit and R4-F explicit tests remain S02)`. Do not claim the absent tests are complete.
- **TL-04:** `IMPLEMENTED` → `TESTED` when all four golden cases execute in CI.
- **TL-05:** `IMPLEMENTED` → `TESTED` when extraction golden tests execute in CI.
- **TL-06:** `IMPLEMENTED` → `TESTED` when API tests execute in CI.
- **NFR-004:** `IMPLEMENTED` → `TESTED` after offline local/CI proof runs with no application key/live evidence call; dependency installation is identified separately as build setup.
- **NFR-008:** `IMPLEMENTED` → `TESTED` after WSL `make ci`, GitHub Linux uv/pip jobs and Docker build all pass.
- **INV-10 / Manifest §6.10:** `IMPLEMENTED` → `TESTED` after integrity/golden CI executes only against the current hashed local artifacts.
- **ADR-004:** not a traceability status row; evidence it through the lock, Makefile, workflow and preserved pip paths. Do not edit the ADR file in this slice.

Do not use `VALIDATED` until the independent reviewer returns zero findings. Do not use `COMPLETE` before squash merge, final CI evidence and completion record exist.

For KL-09, the Supervisor-owned final documentation update must move it from `Open` to a new `Closed by completion slice` section with:

- resolution: required CI workflow, local `make ci`, uv/pip proof and Docker build;
- evidence: S01 test evidence and exact green GitHub run URL;
- closure: effective on squash merge of S01.

The implementation branch may say `resolved pending merge`; it must not state that merge has already occurred.

## 23. Explicit non-goals

- No domain decision behavior, API, UI, CSS or JavaScript edit.
- No config, threshold, evidence-policy, sector-profile, snapshot, synthetic scenario, golden expectation, core or methodology change.
- No `build_manifests.py` execution or hash update.
- No new runtime dependency, linter, formatter, browser test, dependency vulnerability product or deployment.
- No live connector, external evidence call or Ministry data.
- No modification to pip startup scripts, Dockerfile, Compose file, requirements file, `.env.example` or `.gitignore`.
- No shell profile edit, system-wide uv installation or hidden fallback from uv to pip.
- No branch-protection/API/repository-settings mutation by the Implementer.
- No approval, merge or self-review verdict by Planner or Implementer.
- No unrelated cleanup of the upstream Starlette deprecation warning.

## 24. Rollback and recovery

- Before merge, recover by fixing or reverting only S01 files in a normal reviewed commit; never rewrite branch history or use `git reset --hard`.
- If uv adoption breaks local development, the preserved `install`, `START_DEMO_WSL.sh` and Docker pip paths remain the operational recovery route while S01 is corrected.
- If a lock resolution is invalid, regenerate `uv.lock` from the unchanged `pyproject.toml` dependency declarations with the approved uv version, inspect the diff and rerun both uv Python legs; do not hand-edit the lock.
- If CI syntax is invalid, the static contract/YAML parse should fail locally. Correct the workflow and rerun local tests before another push.
- If a scanner false positive occurs, compare it to the exact owner-supplied pattern list. Do not weaken a mandated rule; raise a policy decision if an intentionally tracked file matches.
- GitHub/uv/pip caches are disposable. Clear/disable a suspect cache for diagnosis without changing lock or tests; cache state is never acceptance evidence.
- No authority/snapshot rollback is required because those files must remain unchanged.

## 25. Step-by-step implementation tasks

### Task 0: Approval and branch preflight

**Files:** no implementation edit.

**Interfaces:**

- Consumes: Supervisor plan-review record.
- Produces: confirmed branch/base and a recorded pre-existing-worktree inventory.

- [ ] **Step 1 — Confirm approval**

Read the Supervisor's plan review. Stop if it is not an explicit approval or if it changes scope.

- [ ] **Step 2 — Confirm branch/base with short interactive Git commands**

```bash
git rev-parse HEAD
git branch --show-current
git status --short
```

Expected first two outputs:

```text
0731ae546f79c9ac3bfd92612a01f07da67937ed
slice/S01-ci-and-toolchain
```

The current work tree already contains Supervisor-owned `.workflow/state.json`/S00 record changes plus S01 records. Record them; do not revert, overwrite or silently include them as Implementer work.

- [ ] **Step 3 — Confirm scope**

Re-read `git status --short`; create an implementation-log preflight entry with the exact existing paths and data classification.

**Confirm:** branch and approval are correct.
**Validate:** pre-existing changes are distinguished from Implementer edits.
**Test:** no code test in this task.

### Task 1: Install uv user-scoped and generate the lock

**Files:**

- Create: `uv.lock`
- Do not modify: `pyproject.toml`

**Interfaces:**

- Consumes: existing `pyproject.toml` optional extra `dev`.
- Produces: universal lock accepted by `uv sync --locked --extra dev`.

- [ ] **Step 0 — Confirm a local Node executable**

```bash
node --version
```

If Node is absent, install the current Node LTS release from the official `https://nodejs.org/dist/` tarball for the workstation architecture under `~/.local/node`, verify the archive against the official `SHASUMS256.txt`, and run:

```bash
$HOME/.local/node/bin/node --version
```

Do not use a system package, modify a shell rc file or add the user-scoped binary permanently to `PATH`. Record the resolved Node version and executable path in `implementation_log.md`; later local validation uses `make NODE=$HOME/.local/node/bin/node ci` when the default `node` command is absent.

- [ ] **Step 1 — Install uv with the approved short bootstrap command**

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
~/.local/bin/uv --version
```

Do not source installer modifications, edit a shell rc file or use a system package install. Record the exact uv version.

- [ ] **Step 2 — Run lock/sync as a detached network operation**

Create this transient ignored script; never add it to Git:

```bash
mkdir -p .workflow/logs
cat > .workflow/logs/s01_lock_and_sync.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp
"$HOME/.local/bin/uv" lock
"$HOME/.local/bin/uv" sync --locked --extra dev
EOF
nohup setsid bash .workflow/logs/s01_lock_and_sync.sh > .workflow/logs/s01_lock_and_sync.log 2>&1 &
```

Read the complete log after process completion. Expected: both commands exit 0 and `uv.lock` exists.

- [ ] **Step 3 — Inspect generated scope**

```bash
git status --short
git diff -- pyproject.toml
```

Expected: `uv.lock` is new; `pyproject.toml` has no diff.

**Confirm:** recorded Node and uv versions and generated lock.
**Validate:** locked sync succeeds without pyproject edit.
**Test:** the selected Node executable reports its version and `~/.local/bin/uv sync --locked --extra dev` exits 0.

### Task 2: Build the scanner test-first

**Files:**

- Modify: `pyproject.toml`
- Create: `tests/test_prohibited_files.py`
- Create: `scripts/check_prohibited_files.py`

**Interfaces:**

- Consumes: root Git work tree and `git ls-files -z`.
- Produces: `Finding`, `ScannerError`, `normalize_path`, `prohibited_path_rules`, `decode_tracked_text`, `scan_tracked_files`, `parse_git_ls_files`, `git_tracked_paths`, `load_tracked_files`, `scan_repository`, `main`.

- [ ] **Step 1 — Make repository-root test helpers importable**

Change only the existing pytest configuration:

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "."]
testpaths = ["tests"]
addopts = "-ra"
```

Run:

```bash
~/.local/bin/uv sync --locked --extra dev
```

Expected: exit 0 and no `uv.lock` change because pytest `pythonpath` is test configuration, not dependency metadata.

- [ ] **Step 2 — Write the failing tests**

Transcribe the final `tests/test_prohibited_files.py` draft from §18, including `pytest`, dynamic secret construction and all named tests.

- [ ] **Step 3 — Run the focused test and prove red**

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_prohibited_files.py -q
```

Expected: after the pytest `pythonpath` change, collection fails with `ModuleNotFoundError`/`ImportError` on `scripts.check_prohibited_files` because that module file does not exist. This proves red for the intended missing implementation, not because the repository root is absent from the import path. Record only the observed failure class.

- [ ] **Step 4 — Implement the pure scanner and CLI**

Transcribe the complete `scripts/check_prohibited_files.py` draft from §7 exactly.

- [ ] **Step 5 — Run focused tests and prove green**

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_prohibited_files.py -q
```

Expected: all tests in that file pass.

- [ ] **Step 6 — Perform the actual planted-path red-green probe**

Run interactively from the repository root:

```bash
probe='scanner-probe:Zone.Identifier'
printf 'probe\n' > "$probe"
git add -N -- "$probe"
set +e
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_prohibited_files.py
probe_status=$?
set -e
git reset -- "$probe"
rm -- "$probe"
test "$probe_status" -eq 1
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_prohibited_files.py
```

Expected red: exit 1 and `scanner-probe:Zone.Identifier: path:Zone.Identifier`. Expected green after cleanup: exit 0. If cleanup is interrupted, remove only this named probe and its intent-to-add entry before continuing.

**Confirm:** every exact pattern is represented.
**Validate:** pure core has no Git/filesystem call and output is sanitized.
**Test:** focused unit suite and actual exit-1/exit-0 probe.

### Task 3: Define the workflow contract test-first

**Files:**

- Create: `tests/test_ci_contract.py`
- Create: `.github/workflows/ci.yml`

**Interfaces:**

- Consumes: committed lock, scanner, current pyproject and Dockerfile.
- Produces: `uv-gates`, `pip-gates`, `docker-build` checks with the exact topology in §6.

- [ ] **Step 1 — Write the failing static contract**

Transcribe the corrected `tests/test_ci_contract.py` draft from §18. It must import both `pytest` and `yaml`.

- [ ] **Step 2 — Run the focused test and prove red**

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_ci_contract.py -q
```

Expected: failure because `.github/workflows/ci.yml` does not exist.

- [ ] **Step 3 — Create the workflow**

Create `.github/workflows/ci.yml` by exact transcription of §6. Do not add conditions, permissions, secrets or omitted checks.

- [ ] **Step 4 — Run the focused test and prove green**

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_ci_contract.py -q
```

Expected: all workflow contract tests pass, including YAML parse and both job gate sets.

**Confirm:** trigger, permissions, matrix and job graph match §6.
**Validate:** no optional failure path.
**Test:** focused contract suite green.

### Task 4: Add the local uv toolchain targets

**Files:**

- Modify: `Makefile`

**Interfaces:**

- Consumes: `~/.local/bin/uv`, `uv.lock`, Node executable and existing proof scripts.
- Produces: `make uv-sync`, `make lock`, `make ci`.

- [ ] **Step 1 — Apply the exact Makefile draft**

Use §11 as the resulting full file. Preserve existing recipes byte-for-byte apart from the `.PHONY` expansion and new declarations/targets.

- [ ] **Step 2 — Validate expansion without executing long commands**

```bash
make -n uv-sync
make -n lock
make -n ci
```

Expected: `ci` prints all six gates in required order and uses `--locked --extra dev`.
The JavaScript line must expand to `node --check src/ior_mvp/static/app.js` by default, or to `$HOME/.local/node/bin/node --check src/ior_mvp/static/app.js` with `make NODE=$HOME/.local/node/bin/node -n ci`.

- [ ] **Step 3 — Run focused tests again**

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_prohibited_files.py tests/test_ci_contract.py -q
```

**Confirm:** all old targets remain.
**Validate:** dry-run command order.
**Test:** focused suites green.

### Task 5: Document both paths and evidence lifecycle

**Files:**

- Create: `docs/DEVELOPMENT_GUIDE.md`
- Modify: `README.md`
- Modify: `docs/REQUIREMENTS_TRACEABILITY.md`
- Modify later at completion gate: `docs/KNOWN_LIMITATIONS.md`
- Create: `.workflow/slices/S01-ci-and-toolchain/implementation_log.md`
- Create: `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`

**Interfaces:**

- Consumes: implemented commands/job names and actual local evidence.
- Produces: operator guidance and honest traceability.

- [ ] **Step 1 — Create the development guide**

Write every section/command specified in §11. Do not claim a command passed until its output has been observed.

- [ ] **Step 2 — Add only the README subsection**

Insert the exact §11 wording after `Integrity and tests`. Do not alter any other README content.

- [ ] **Step 3 — Update traceability to the evidence currently available**

Apply §22 status transitions. Before GitHub CI, BC-04/GATE-H may be only `IMPLEMENTED`; do not pre-write a green URL. Keep TL-03 explicitly partial.

- [ ] **Step 4 — Create implementation/evidence records**

`implementation_log.md` records actual authorized edits and uv version. `test_evidence.md` starts with local environment and focused red-green outputs. Do not add placeholder text, fake exits or future URLs.

- [ ] **Step 5 — Defer KL-09 closure**

Do not move KL-09 yet. The Supervisor performs that edit only after the CI/merge evidence gate described in §22.

**Confirm:** documentation matches actual commands.
**Validate:** no unsupported completion claim.
**Test:** focused static contract test remains green.

### Task 6: Supervisor implementation review

**Files:** all S01 diffs, read-only review.

**Interfaces:**

- Consumes: Implementer diff and focused evidence.
- Produces: Supervisor findings or authorization to request independent review.

- [ ] **Step 1 — Hand off without self-approval**

Implementer reports changed files, red-green evidence, assumptions and known limitations. The Implementer does not say APPROVE.

- [ ] **Step 2 — Resolve Supervisor findings**

Fix only evidence-backed findings inside scope, rerun affected focused tests, and append actual results. Do not weaken tests.

**Confirm:** Supervisor has reviewed current diff.
**Validate:** findings are resolved on the current files.
**Test:** affected focused tests rerun.

### Task 7: Independent different-model review

**Files:** all S01 diffs, read-only review except Implementer fixes after a finding.

**Interfaces:**

- Consumes: Supervisor-reviewed implementation.
- Produces: independent zero-finding verdict or actionable findings.

- [ ] **Step 1 — Dispatch the required Reviewer**

Reviewer model must differ from Implementer and Supervisor, per ADR-002. Review security, workflow semantics, scanner bypasses, test fidelity and scope.

- [ ] **Step 2 — If rejected, fix then request a new review**

Do not repeatedly rerun the same reviewer on unchanged rejected work. Fix findings, rerun affected tests, then obtain review of the fixed work.

**Confirm:** reviewer identity/model is recorded.
**Validate:** current diff has zero findings.
**Test:** review verdict is evidence, not self-approval.

### Task 8: Stage intended files and run final local gates

**Files:**

- All approved S01 deliverables.
- Transient ignored scripts/logs under `.workflow/logs/`.

**Interfaces:**

- Consumes: zero-finding implementation.
- Produces: final local uv, pip and Docker evidence.

- [ ] **Step 1 — Stage only intended deliverables for the tracked-file scanner**

The scanner intentionally enumerates Git's tracked/index set, so newly created deliverables must be in the index before final proof. Use explicit paths; do not use `git add .`:

```bash
git add .github/workflows/ci.yml
git add scripts/check_prohibited_files.py
git add tests/test_prohibited_files.py tests/test_ci_contract.py
git add Makefile pyproject.toml uv.lock
git add docs/DEVELOPMENT_GUIDE.md README.md
git add docs/REQUIREMENTS_TRACEABILITY.md
git add .workflow/slices/S01-ci-and-toolchain/implementation_log.md
git add .workflow/slices/S01-ci-and-toolchain/test_evidence.md
git add .workflow/slices/S01-ci-and-toolchain/{persona,context,plan,plan_review}.md
git add .workflow/slices/S00-baseline-import/{test_evidence,completion}.md
git add .workflow/state.json
git add docs/BUILD_PROGRESS.md
git add docs/KNOWN_LIMITATIONS.md
git add docs/ARCHITECTURE_DECISIONS.md
```

The control-record commands run when the Supervisor directs; do not invent edits to those records, but include the directed records in the same PR so the branch is self-describing. Inspect:

```bash
git status --short
git diff --cached --name-only
```

Expected: no `.env`, key/certificate, cache, logs, governed file or out-of-scope path.

- [ ] **Step 2 — Create the detached full-validation script**

This ignored script is exact and must not enter Git:

```bash
cat > .workflow/logs/s01_full_validation.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp

printf '%s\n' '=== UV LOCAL GATES ==='
if command -v node >/dev/null 2>&1; then
    node_bin="$(command -v node)"
    make ci
else
    node_bin="$HOME/.local/node/bin/node"
    make NODE=$HOME/.local/node/bin/node ci
fi

printf '%s\n' '=== CLEAN PIP COMPATIBILITY GATES ==='
pip_env='.workflow/logs/s01-pip-venv'
python3 -m venv --clear "$pip_env"
source "$pip_env/bin/activate"
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python -m compileall -q src scripts tests
"$node_bin" --check src/ior_mvp/static/app.js
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
deactivate

printf '%s\n' '=== DOCKER BUILD ==='
docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s01-local .
EOF
nohup setsid bash .workflow/logs/s01_full_validation.sh > .workflow/logs/s01_full_validation.log 2>&1 &
```

Read the complete log after completion. Every command must exit 0. Record actual versions/output, including test count and golden smoke text; do not predict them.

- [ ] **Step 3 — Run short repository validators**

```bash
git diff --check
git status --short
git diff --cached --name-only
```

Also execute the required scanner once more after every intended file is staged:

```bash
PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_prohibited_files.py
```

- [ ] **Step 4 — Audit governed paths**

Inspect the staged name list. If any `config/`, `data/`, `docs/core/`, `docs/authority/` or `src/ior_mvp/` path appears, stop and investigate; do not regenerate hashes.

**Confirm:** staged set exactly matches authorized deliverables.
**Validate:** uv, clean pip, Docker and hygiene outputs are real and sanitized.
**Test:** full local gates exit 0 after independent review.

### Task 9: PR CI evidence and completion bookkeeping

**Files:**

- Append: `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`
- Modify with evidence: `docs/REQUIREMENTS_TRACEABILITY.md`
- Modify at Supervisor completion gate: `docs/KNOWN_LIMITATIONS.md`

**Interfaces:**

- Consumes: approved/staged diff and local green evidence.
- Produces: green required GitHub run, tested traceability and merge-ready completion records.

- [ ] **Step 1 — Supervisor controls commit/push/PR**

The Implementer does not merge. Commit/push/PR commands run only under explicit Supervisor authorization and the repository Git safety protocol.

- [ ] **Step 2 — Observe required jobs**

Required displayed results:

```text
uv / Python 3.12
uv / Python 3.14
pip / Python 3.12
Docker image build
```

All must be green on the current PR head. A cancelled/skipped job is not green evidence.

- [ ] **Step 3 — Record actual CI evidence**

Append exact run URL, head SHA, job names, outcomes and relevant output summaries to `test_evidence.md`; do not include secrets. Update §22 rows to `TESTED` only now. This evidence-only update triggers CI again; the final PR head must also be green.

- [ ] **Step 4 — Close KL-09 conditionally and honestly**

After current-head CI is green, the Supervisor moves KL-09 as specified in §22 with wording that closure is effective on merge. Run focused contract tests/local scanner after the docs-only edit and require final CI green.

- [ ] **Step 5 — Merge authority**

Only the Supervisor may squash merge after plan review, implementation review, independent zero findings, final local gates and final-head CI green. Record the resulting merge commit before any `COMPLETE` status.

**Confirm:** evidence refers to current PR head.
**Validate:** traceability and KL-09 wording match lifecycle.
**Test:** final-head GitHub run is fully green.

## 26. Exact command classification

### Short interactive commands

- Git branch/status/diff inspection.
- `~/.local/bin/uv --version`.
- Focused pytest files.
- `make -n` targets.
- Planted-path scanner red-green probe.
- `git diff --check`.
- Final clean scanner.

### Detached long/network commands

- Initial uv lock/sync: `nohup setsid bash .workflow/logs/s01_lock_and_sync.sh > .workflow/logs/s01_lock_and_sync.log 2>&1 &`.
- Full uv + clean pip + Docker validation: `nohup setsid bash .workflow/logs/s01_full_validation.sh > .workflow/logs/s01_full_validation.log 2>&1 &`.
- GitHub Actions runs asynchronously on push/PR and are recorded only after completion.

Transient scripts, environments and logs remain under ignored `.workflow/logs/` and must never be staged.

## 27. Skills

- Read and used `superpowers/writing-plans`: exact paths, complete drafts, TDD red-green tasks, small reviewable actions, commands and self-review.
- Read `superpowers/using-superpowers`; its `SUBAGENT-STOP` applies because this is a dispatched subagent task, so no further generic skill workflow was invoked.
- Inspected `C:\Users\Admin\.cursor\skills-cursor\` and `C:\Users\Admin\.cursor\skills\`. Cursor Automations targets Cursor-native automations, Autopilot targets maintaining an existing PR, and the SDK skill targets programmatic Cursor agents; none governs creation of this repository's GitHub Actions/toolchain slice.
- **No applicable installed skill found after discovery beyond writing-plans.**

## 28. Open questions and decisions not to guess

1. **TL-03 wording — resolved by PR-04:** use `TESTED (partial; existing cases executed in CI; R1-D boundary, R3 explicit and R4-F explicit tests remain S02)`. S01 does not add the out-of-scope missing tests or claim full coverage.
2. **Merge enforcement — resolved by PR-05 and ADR-007:** private-repository branch protection/rulesets are unavailable, so the Supervisor protocol is the merge gate. `gh pr checks` must show every job green on the PR head before `gh pr merge --squash`; no administrative override is permitted.

No domain threshold, policy value, secret, action credential, budget, effort or timeline is inferred.

## 29. Planner self-review (al-muhasibi)

- Spec coverage: every required plan section, approved file, gate, exact scanner pattern/regex, Python version, compatibility route and lifecycle gate maps to a task above.
- Scope: no planned edit to domain/config/data/core/authority or preserved pip/Docker startup files; no manifest build.
- Placeholder scan: implementation content contains no deferred-work marker or fake result. Evidence files are instructed to contain only observed output.
- Type consistency: scanner signatures used by tests match the exact draft; `main` returns 0/1/2; workflow job IDs match static tests and documentation.
- Security: findings expose path/rule only; no real secret fixture; read-only workflow permissions; symlinks not followed.
- Evidence: the plan distinguishes implemented, tested, validated and complete; TL-03 remains explicitly partial; no self-approval.
- Assumptions: GitHub-hosted `ubuntu-latest` provides Docker and a `node` executable; action major tags in the exact draft are accepted because no repository SHA-pinning policy is supplied. If either assumption is rejected, the Supervisor must amend/approve the plan before implementation.
