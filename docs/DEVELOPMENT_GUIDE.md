# Development Guide

## Authority and data boundary

Development uses PUBLIC repository code, frozen public evidence and explicitly synthetic fixtures. No API key or live industrial evidence source is required. Never run `scripts/build_manifests.py` outside an approved authority change (manifest §7); the slice ADR and PR must justify it first.

## Prerequisites

Use WSL or native Linux with Python 3.12 or 3.14, Git, Make and Node. Docker is required only for the local Docker compatibility check.

The Makefile defaults to `NODE ?= node`. If Node is installed user-scoped under `~/.local/node`, run:

```bash
make NODE=$HOME/.local/node/bin/node ci
```

Do not modify shell startup files to support the override.

The Makefile invokes `$(HOME)/.local/bin/uv` unless overridden. If uv is already on `PATH` or installed elsewhere, use either form without editing shell startup files:

```bash
make UV=uv ci
make UV=/path/to/uv ci
```

## Install uv without changing shell profiles

Install uv in the approved user-scoped location:

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
~/.local/bin/uv --version
make uv-sync
```

## Run all local gates

```bash
make ci
```

The command runs these required gates in order:

1. prohibited tracked-file and deterministic secret-pattern scan;
2. Python compile check;
3. JavaScript syntax check;
4. integrity verification;
5. full pytest suite;
6. demo smoke test.

Any non-zero exit blocks review.

## Maintain the lock

```bash
make lock
make uv-sync
```

Regenerate `uv.lock` only after an intentional `pyproject.toml` dependency change. Review the lock diff and do not use opportunistic `--upgrade`.

## Preserved pip compatibility path

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

## Docker compatibility

```bash
docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:local .
```

The Dockerfile remains on its existing Python 3.12 pip installation path.

## CI topology and caches

GitHub Actions runs uv gates on Python 3.12 and 3.14, the preserved pip path on Python 3.12, and an independent Docker image build. Workflow permissions are `contents: read`, and checkout credentials are not persisted.

uv caching is keyed by `uv.lock` and guarded by `uv sync --locked`. The pip cache is keyed by `pyproject.toml` and acts as a compatibility check against the declared dependency ranges. There is no Node package cache or remote Docker layer cache.

## Failure interpretation

- Scanner exit 1: prohibited tracked path or secret-pattern finding; output is limited to path and rule.
- Scanner exit 2: Git or a tracked file could not be read safely.
- uv sync failure: lock is absent or stale.
- Compile or Node failure: syntax is invalid or the required tool is unavailable.
- Integrity failure: a governed artifact is missing or its hash changed; do not regenerate manifests.
- pytest or smoke failure: implementation or frozen-contract behavior is not conformant; do not weaken tests.
- Docker failure: the unchanged image build path is not compatible.

## Evidence and review

Detached execution logs stay under ignored `.workflow/logs/`. Sanitized command results and exit codes are recorded in the active slice's `.workflow/slices/<slice>/test_evidence.md`.

A green local or CI run is evidence, not approval. Supervisor implementation review, independent review and Supervisor merge authority remain separate gates.
