UV ?= $(HOME)/.local/bin/uv
NODE ?= node
UV_RUN = $(UV) run --locked --extra dev
UV_RUN_E2E = $(UV) run --locked --extra dev --extra e2e
UI_CONTRACTS = $(UV_RUN) python scripts/check_ui_contracts.py
ES_MODULE_CHECK = $(UV_RUN) python scripts/check_es_modules.py --node "$(NODE)"
E2E_ARTIFACT_DIR ?= .artifacts/e2e
E2E_PREFLIGHT = $(UV_RUN_E2E) python scripts/check_browser_prerequisites.py
E2E_TESTS = IOR_E2E_EXPLICIT=1 \
	IOR_E2E_ARTIFACT_DIR="$(E2E_ARTIFACT_DIR)" \
	PYTHONPATH=src $(UV_RUN_E2E) pytest -q browser_tests \
	--browser chromium \
	--tracing retain-on-failure \
	--screenshot only-on-failure \
	--output="$(E2E_ARTIFACT_DIR)/playwright"
E2E_FUNCTIONAL_TESTS = $(E2E_TESTS) -m "e2e and not visual"
E2E_VISUAL_TESTS = $(E2E_TESTS) -m visual
VISUAL_BASELINE_IMAGE = ior-visual-baselines:playwright-1.62.0-noble

.PHONY: install test verify run smoke package uv-sync uv-sync-e2e lock \
	e2e e2e-functional e2e-visual e2e-visual-canonical \
	e2e-update-baselines visual-baseline-image ci \
	acquire-universe acquire-partners acquire-tariff acquire-baci \
	acquire-aggregates acquire-directory acquire-registry build-snapshots reconstruct \
	acquire-documents build-documents

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

e2e-functional: uv-sync-e2e
	$(E2E_PREFLIGHT)
	$(E2E_FUNCTIONAL_TESTS)

e2e-visual: uv-sync-e2e
	$(E2E_PREFLIGHT)
	$(E2E_VISUAL_TESTS)

e2e: e2e-functional e2e-visual

visual-baseline-image:
	docker build --file browser_tests/visual/Dockerfile \
		--tag "$(VISUAL_BASELINE_IMAGE)" .

e2e-visual-canonical: visual-baseline-image
	$(UV_RUN_E2E) python scripts/run_visual_baseline_container.py \
		--image "$(VISUAL_BASELINE_IMAGE)" \
		--mode compare

e2e-update-baselines: visual-baseline-image
	@test "$(IOR_UPDATE_VISUAL_BASELINES)" = "1" || \
		(echo "IOR_UPDATE_VISUAL_BASELINES=1 is required" >&2; exit 2)
	@test -n "$(IOR_BASELINE_CHANGE_REF)" || \
		(echo "IOR_BASELINE_CHANGE_REF is required" >&2; exit 2)
	@test -z "$(CI)" || \
		(echo "CI may not update visual baselines" >&2; exit 2)
	$(UV_RUN_E2E) python scripts/run_visual_baseline_container.py \
		--image "$(VISUAL_BASELINE_IMAGE)" \
		--mode update \
		--change-ref "$(IOR_BASELINE_CHANGE_REF)"

ci: uv-sync
	$(UV_RUN) python scripts/check_prohibited_files.py
	$(UV_RUN) python scripts/check_threshold_literals.py
	$(UI_CONTRACTS)
	$(UV_RUN) python -m compileall -q src scripts tests browser_tests
	$(ES_MODULE_CHECK)
	PYTHONPATH=src $(UV_RUN) python scripts/verify_integrity.py
	PYTHONPATH=src $(UV_RUN) python scripts/validate_scenarios.py
	PYTHONPATH=src $(UV_RUN) python scripts/reconstruct_snapshot.py --all
	PYTHONPATH=src $(UV_RUN) pytest -q
	PYTHONPATH=src $(UV_RUN) python scripts/demo_smoke.py
	$(E2E_PREFLIGHT)
	$(E2E_FUNCTIONAL_TESTS)
	$(E2E_VISUAL_TESTS)

acquire-universe:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(YEARS)" || (echo "YEARS required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-universe --source $(SOURCE) --years $(YEARS) --max-requests $(MAX_REQUESTS) $(if $(FLOWS),--flows $(FLOWS),)

acquire-partners:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(CANDIDATES)" || (echo "CANDIDATES required" >&2; exit 2)
	@test -n "$(YEARS)" || (echo "YEARS required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-partners --source $(SOURCE) --candidates $(CANDIDATES) --years $(YEARS) --max-requests $(MAX_REQUESTS) $(if $(FLOWS),--flows $(FLOWS),)

acquire-tariff:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-tariff --source $(or $(SOURCE),zatca_tariff) --max-requests $(MAX_REQUESTS)

acquire-baci:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(YEARS)" || (echo "YEARS required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-baci --years $(YEARS) --max-requests $(MAX_REQUESTS)

acquire-aggregates:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(YEARS)" || (echo "YEARS required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-aggregates --source $(SOURCE) --years $(YEARS) --max-requests $(MAX_REQUESTS)

acquire-directory:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-directory --source $(SOURCE) --max-requests $(MAX_REQUESTS)

acquire-registry:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-registry --source $(SOURCE) --max-requests $(MAX_REQUESTS)

build-snapshots:
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition build-snapshots --kind $(or $(KIND),all) $(if $(SOURCE),--source $(SOURCE),)

acquire-documents:
	@test "$(IOR_ACQUISITION_LIVE)" = "1" || (echo "IOR_ACQUISITION_LIVE=1 required" >&2; exit 2)
	@test -z "$(CI)" || (echo "CI may not acquire" >&2; exit 2)
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(LIST_ID)" || (echo "LIST_ID required" >&2; exit 2)
	@test -n "$(MAX_REQUESTS)" || (echo "MAX_REQUESTS required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition acquire-documents --source $(SOURCE) --list-id $(LIST_ID) --max-requests $(MAX_REQUESTS)

build-documents:
	@test -n "$(SOURCE)" || (echo "SOURCE required" >&2; exit 2)
	@test -n "$(LIST_ID)" || (echo "LIST_ID required" >&2; exit 2)
	PYTHONPATH=src $(UV_RUN) python -m ior_mvp.acquisition build-documents --source $(SOURCE) --list-id $(LIST_ID)

reconstruct:
	PYTHONPATH=src $(UV_RUN) python scripts/reconstruct_snapshot.py --all
