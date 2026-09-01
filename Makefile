.PHONY: install test verify run smoke package

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
