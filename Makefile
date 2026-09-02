UV ?= $(HOME)/.local/bin/uv
NODE ?= node
UV_RUN = $(UV) run --locked --extra dev
UV_RUN_E2E = $(UV) run --locked --extra dev --extra e2e
E2E_ARTIFACT_DIR ?= .artifacts/e2e
E2E_REFERENCE_DIR ?= $(E2E_ARTIFACT_DIR)/reference
E2E_PREFLIGHT = $(UV_RUN_E2E) python scripts/check_browser_prerequisites.py
E2E_TESTS = IOR_E2E_EXPLICIT=1 \
	IOR_E2E_ARTIFACT_DIR="$(E2E_ARTIFACT_DIR)" \
	IOR_E2E_REFERENCE_DIR="$(E2E_REFERENCE_DIR)" \
	PYTHONPATH=src $(UV_RUN_E2E) pytest -q browser_tests \
	--browser chromium \
	--tracing retain-on-failure \
	--screenshot only-on-failure \
	--output="$(E2E_ARTIFACT_DIR)/playwright"

.PHONY: install test verify run smoke package uv-sync uv-sync-e2e lock e2e ci

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

uv-sync-e2e:
	$(UV) sync --locked --extra dev --extra e2e

lock:
	$(UV) lock

e2e: uv-sync-e2e
	$(E2E_PREFLIGHT)
	$(E2E_TESTS)

ci: uv-sync
	$(UV_RUN) python scripts/check_prohibited_files.py
	$(UV_RUN) python scripts/check_threshold_literals.py
	$(UV_RUN) python -m compileall -q src scripts tests browser_tests
	$(NODE) --check src/ior_mvp/static/app.js
	PYTHONPATH=src $(UV_RUN) python scripts/verify_integrity.py
	PYTHONPATH=src $(UV_RUN) python scripts/validate_scenarios.py
	PYTHONPATH=src $(UV_RUN) pytest -q
	PYTHONPATH=src $(UV_RUN) python scripts/demo_smoke.py
	$(E2E_PREFLIGHT)
	$(E2E_TESTS)
