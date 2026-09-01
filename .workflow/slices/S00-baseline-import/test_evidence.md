# Test Evidence — S00 Baseline Import

Run: `.workflow/runs/s00_bootstrap.sh`, detached via nohup, log `.workflow/logs/s00_bootstrap.log` (read by the Supervisor at 01:14 on 2026-09-02). Environment: WSL Ubuntu, Python 3.14.4, fresh `.venv`, `pip install -e '.[dev]'` → fastapi 0.141.1, PyYAML 6.0.3, pytest 8.4.2, httpx 0.28.1, uvicorn 0.52.4.

| Command | Result | Exit |
|---|---|---|
| `find . -name '*Zone.Identifier' -delete` | 78 files removed; recount 0 | 0 |
| `PYTHONPATH=src python3 scripts/verify_integrity.py` | `INTEGRITY PASS` (snapshot_manifest.json, authority_hashes.json) | 0 |
| `PYTHONPATH=src pytest -q` | `35 passed, 1 warning in 0.18s` (warning: StarletteDeprecationWarning for httpx test client) | 0 |
| `PYTHONPATH=src python3 scripts/demo_smoke.py` | `SMOKE PASS` — steel/public INVESTIGATE; steel/simulated ADVANCE with real unchanged; PP/public REJECT; extraction 100% | 0 |
| `git ls-files \| grep -Ei 'zone\.identifier\|^\.venv/\|^\.env$\|__pycache__\|\.pyc$'` | no matches (`prohibited_check=clean`); 86 tracked files | — |
| `git push -u origin main` | `* [new branch] main -> main` | 0 |
| `gh repo view --json ...` | `{"defaultBranchRef":{"name":"main"},"isEmpty":false,"visibility":"PRIVATE"}` | 0 |

Observation carried forward: the Starlette test-client deprecation warning is upstream (starlette 1.6.0 prefers `httpx2`); no action in this build unless it becomes an error in CI.
