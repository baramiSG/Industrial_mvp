# Context — S01 CI Pipeline, Local Gates and Toolchain

- Base: `main` @ `0731ae546f79c9ac3bfd92612a01f07da67937ed`. Branch: `slice/S01-ci-and-toolchain`.
- Baseline proof on the workstation (S00): integrity PASS, 35 tests pass, smoke PASS on Python 3.14.4 with fastapi 0.141.1 / starlette 1.6.0 / pytest 8.4.2. Dockerfile uses `python:3.12-slim` with pip.
- Toolchain: `uv` is NOT installed in WSL. Install user-scoped without modifying shell profiles: `curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh` (installs to `~/.local/bin/uv`); invoke via absolute path in scripts.
- Execution reliability: the tool shell drops output on long-running commands. Run long commands detached (`nohup setsid bash script.sh > .workflow/logs/<name>.log 2>&1 &`) and read the log; keep interactive commands short.
- GitHub: `origin = https://github.com/baramiSG/Industrial_mvp.git`, private, default `main`; `gh` active account `baramiSG` (do not switch to `albarami`). Merge policy: squash (ADR default).
- Governed files (hash-locked, DO NOT TOUCH in this slice): `docs/authority/*.docx`, `config/*.yaml`, `docs/core/*.md`, `data/**`.
- Existing test conventions: `tests/test_static_frontend.py` and `tests/test_integrity_contract.py` are static contract tests reading files under `PROJECT_ROOT`; follow the same style for the CI contract test.
- Prior observations to preserve: Starlette deprecation warning is upstream; do not silence with a blanket filter.
