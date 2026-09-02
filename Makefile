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
	$(UV_RUN) python scripts/check_threshold_literals.py
	$(UV_RUN) python -m compileall -q src scripts tests
	$(NODE) --check src/ior_mvp/static/app.js
	PYTHONPATH=src $(UV_RUN) python scripts/verify_integrity.py
	PYTHONPATH=src $(UV_RUN) python scripts/validate_scenarios.py
	PYTHONPATH=src $(UV_RUN) pytest -q
	PYTHONPATH=src $(UV_RUN) python scripts/demo_smoke.py
