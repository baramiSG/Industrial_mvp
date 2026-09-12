# S12a test evidence

## T0 — 2026-09-11

Environment: existing `.venv/bin` prepended to PATH; `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`. No live flag, dependency install, `.env` read or manifest generation.

Plan SHA: `b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64`.
Original plan SHA verified; canonical [4], [5], [12], [17], [20], [26] copied from parsed JSON and verified exact UTF-8 equality. [22] is SUPERSEDED_BY_OWNER_RULING, not PASS.

Branch: `slice/s12a-acquisition-framework-institutional-sources`; HEAD: `a043ed8dc1d477de50149b39de657bc963e785d7`. Tracked/nonignored tree clean before slice records.

### Canonical [0] before cache relocation

Command:
```bash
test "$(git branch --show-current)" = slice/s12a-acquisition-framework-institutional-sources && git merge-base --is-ancestor a043ed8dc1d477de50149b39de657bc963e785d7 HEAD
```

Exit: 0.

(No output.)

### Canonical [4] before cache relocation

Command:
```bash
git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
```

Exit: 0.

(No output.)

### Canonical [5] before cache relocation

Command:
```bash
git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
```

Exit: 1.

(No output.)

### Canonical [6] before cache relocation

Command:
```bash
git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
```

Exit: 0.

(No output.)

Canonical [5] initially failed solely on 23 pre-existing ignored `.pyc` files under `browser_tests/__pycache__`. The entire cache directory was moved intact to `/tmp/ior-s12a-cache-recovery-6KM89p/browser_tests-pycache`. It is recoverable there; no tracked fixture/baseline/raw evidence was changed or removed. The gate was not weakened.

### Baseline command

```bash
PYTHONPATH=src pytest -q
```

Exit: 0.

```text
........................................................................ [  7%]
........................................................................ [ 14%]
........................................................................ [ 21%]
........................................................................ [ 28%]
........................................................................ [ 35%]
........................................................................ [ 43%]
........................................................................ [ 50%]
........................................................................ [ 57%]
........................................................................ [ 64%]
........................................................................ [ 71%]
........................................................................ [ 79%]
........................................................................ [ 86%]
........................................................................ [ 93%]
..................................................................       [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1002 passed, 1 warning in 14.58s
```

### Baseline command

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

Exit: 0.

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
```

### Baseline command

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
```

Exit: 0.

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

### Baseline command

```bash
PYTHONPATH=src pytest -q tests/test_frozen_public_evidence_pins.py
```

Exit: 0.

```text
.................                                                        [100%]
17 passed in 1.00s
```

### Baseline command

```bash
git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
```

Exit: 0.

```text
(No output.)```

T0 result: PASS. Full baseline 1002 tests; one pre-existing Starlette deprecation warning. Frozen pins 17 passed. Reconstruction 1 snapshot/4 artifacts and integrity PASS. No implementation tests or code existed at this gate.

## Browser prerequisite recovery — 2026-09-11

Owner authorized the requested existing-runtime download in this exchange: "yse download whatever is needed". These commands used `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`.

1. `.venv/bin/python scripts/check_browser_prerequisites.py` before download: exit 1, `BROWSER PREFLIGHT FAIL: Chromium executable is missing for Playwright 1.62.0`.
2. `.venv/bin/python -m playwright install --with-deps chromium`: exit 1, `sudo: A terminal is required to authenticate`; `Failed to install browsers`; `Installation process exited with code: 1`. No sudo authentication was supplied.
3. `.venv/bin/python -m playwright install chromium`: exit 0. Downloaded Chrome for Testing `151.0.7922.34` / Chromium `v1234`, FFmpeg `v1011`, and Chrome Headless Shell `151.0.7922.34` / `v1234` to `/home/barami/.cache/ms-playwright/` from Playwright's distribution URLs.
4. `.venv/bin/python scripts/check_browser_prerequisites.py`: exit 0:

```text
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
chromium=/home/barami/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome
axe_sha256=c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1
font_family=DejaVu Sans
font_file=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
product_fonts=IOR Noto Sans,IOR Noto Sans Arabic
```

5. `ldd /home/barami/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`: exit 0; all listed dependencies resolved, none reported `not found`.
6. Actual offline launch (no navigation or external source):

```bash
PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/python -c 'from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); page=b.new_page(); page.set_content("<title>S12a browser runtime</title><p>Offline launch check</p>"); assert page.title() == "S12a browser runtime"; print("CHROMIUM OFFLINE LAUNCH PASS", b.version); b.close(); p.stop()'
```

Exit 0: `CHROMIUM OFFLINE LAUNCH PASS 151.0.7922.34`.

This is runtime readiness evidence, not the T12 browser-suite result. No baseline update was invoked.

### Early complete browser comparison gate

```bash
IOR_E2E_EXPLICIT=1 IOR_E2E_ARTIFACT_DIR=.artifacts/e2e PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode PYTHONPATH=src .venv/bin/pytest -q browser_tests --browser chromium --tracing retain-on-failure --screenshot only-on-failure --output=.artifacts/e2e/playwright
```

Exit 0: `122 passed in 163.43s (0:02:43)`. This ran while T1 acquisition-only work was in progress; it proves the downloaded runtime runs the existing functional and visual suite. T12 must rerun the browser gates on the finished candidate. The literal canonical frozen-root command [5] was rerun afterward and exited 0. No visual baseline changes or new frozen-root files.

## T1 coordinator verification before root-containment review fix

Environment: existing .venv PATH and external PYTHONPYCACHEPREFIX as T0. These results apply to the candidate after the ZATCA regex fix and before the later registry-root containment fix. They do not close T1; review findings remain binding.

### Command

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

Exit 0.

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
```

### Command

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
```

Exit 0.

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

### Command

```bash
PYTHONPATH=src python3 scripts/demo_smoke.py
```

Exit 0.

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

### Command

```bash
PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py
```

Exit 0.

```text
.....................                                                    [100%]
21 passed in 0.93s
```

### Command

```bash
PYTHONPATH=src pytest -q
```

Exit 0.

```text
........................................................................ [  6%]
........................................................................ [ 13%]
........................................................................ [ 20%]
........................................................................ [ 27%]
........................................................................ [ 34%]
........................................................................ [ 41%]
........................................................................ [ 48%]
........................................................................ [ 55%]
........................................................................ [ 62%]
........................................................................ [ 69%]
........................................................................ [ 76%]
........................................................................ [ 82%]
........................................................................ [ 89%]
........................................................................ [ 96%]
..................................                                       [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1042 passed, 1 warning in 13.60s
```

## T1 final coordinator gate after T1-R2

All commands below used the existing .venv PATH and external PYTHONPYCACHEPREFIX as above. Independent snapshot re-review APPROVE (no findings); registry review no findings. T1 accepted for T2, not final implementation approval.

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

Exit 0.

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
```

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
```

Exit 0.

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

```bash
PYTHONPATH=src python3 scripts/demo_smoke.py
```

Exit 0.

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

```bash
git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
```

Exit 0.

```text
(No output.)
```

```bash
git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
```

Exit 0.

```text
(No output.)
```

```bash
git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
```

Exit 0.

```text
(No output.)
```

```bash
PYTHONPATH=src python3 -c "import ast,sys; from pathlib import Path; bad=[]; [bad.append((str(p),n.lineno)) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,ast.ExceptHandler) and n.type is None]; miss=[(str(p),f.name) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for f in ast.parse(p.read_text(encoding='utf-8')).body if isinstance(f,ast.FunctionDef) and not f.name.startswith('_') and (f.returns is None or any(a.annotation is None for a in f.args.args if a.arg not in ('self','cls')))]; assert not bad, bad; assert not miss, miss; print('PYTHON_STANDARDS_OK')"
```

Exit 0.

```text
PYTHON_STANDARDS_OK
```

```bash
git diff --quiet HEAD -- src/ior_mvp/acquisition/__init__.py src/ior_mvp/acquisition/__main__.py src/ior_mvp/acquisition/connectors/__init__.py config/project.yaml docs/milestones tests/test_offline_guard.py
```

Exit 0.

```text
(No output.)
```

```bash
git diff --check
```

Exit 0.

```text
(No output.)
```

```bash
PYTHONPATH=src pytest -q
```

Exit 0.

```text
........................................................................ [  6%]
........................................................................ [ 13%]
........................................................................ [ 20%]
........................................................................ [ 27%]
........................................................................ [ 34%]
........................................................................ [ 41%]
........................................................................ [ 47%]
........................................................................ [ 54%]
........................................................................ [ 61%]
........................................................................ [ 68%]
........................................................................ [ 75%]
........................................................................ [ 82%]
........................................................................ [ 88%]
........................................................................ [ 95%]
............................................                             [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1052 passed, 1 warning in 13.75s
```

## T2 coordinator gate — 2026-09-11

All commands use `PYTHONPATH=src`, `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`, and the existing `.venv/bin` at the front of PATH. Implementer RED/GREEN history is recorded in the local `t2-report.md`; these are fresh coordinator observations.

```bash
.venv/bin/pytest -q
```

Exit 1: **1 failed, 1099 passed, 1 warning in 13.77s**. Sole failure is approved W2: `tests/test_integrity_contract.py::test_missing_snapshot_kinds_cited_in_known_limitations`, `KeyError: 'directory'` at line 153 from the existing three-kind `stage_for_kind` literal. The warning is the existing Starlette/httpx deprecation. No test was weakened or deselected for this full run; this is not a full-suite GREEN claim.

```bash
.venv/bin/python scripts/reconstruct_snapshot.py --all
.venv/bin/python scripts/verify_integrity.py
.venv/bin/python scripts/demo_smoke.py
.venv/bin/pytest -q tests/test_acquisition_stage_specs.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_kind_registry.py tests/test_acquisition_normalization_status.py tests/test_frozen_public_evidence_pins.py tests/test_golden_cases.py
```

Each exit 0, respectively:

```text
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
INTEGRITY PASS (snapshot_manifest.json and authority_hashes.json)
SMOKE PASS — steel/public INVESTIGATE; steel/simulated ADVANCE with real state unchanged; polypropylene/public REJECT generic capacity; extraction golden gate 100%
119 passed in 1.24s
```

Canonical verification [4], [5], [6], [10] were loaded from the immutable parsed plan-5 JSON and executed unchanged via `subprocess.run(command, shell=True, env=env)`. Each exited 0; [10] printed `PYTHON_STANDARDS_OK`. Their exact command strings are retained in the immutable plan and in the preceding T1 evidence section. `git diff --check` and `git diff --cached --quiet` also exited 0. Manifest runs and source live windows remain zero.

### T2 final coordinator gate after review fixes

Same environment and exact full/focused/reconstruction/integrity/smoke commands as above, rerun after all three review fixes:

- Full pytest exit 1: **1 failed, 1117 passed, 1 warning in 13.67s**; sole approved W2 remains `KeyError: 'directory'` at `test_integrity_contract.py:153`; existing Starlette warning unchanged.
- Focused plus frozen/golden pytest exit 0: **137 passed in 1.19s**.
- Reconstruction exit 0: `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`.
- Integrity exit 0: `INTEGRITY PASS` for both manifests.
- Smoke exit 0: steel/public `INVESTIGATE`, steel/simulated `ADVANCE` with real unchanged, polypropylene/public `REJECT` generic capacity, extraction golden gate 100%.
- Canonical [4]/[5]/[6]/[10], executed byte-exact from parsed immutable plan again: all exit 0; [10] `PYTHON_STANDARDS_OK`.
- Extra frozen paths (`acquisition/__init__.py`, `__main__.py`, `connectors/__init__.py`, `config/project.yaml`, `docs/milestones`, `tests/test_offline_guard.py`) unchanged; `git diff --check` and cached diff quiet pass.
- `git check-ignore .env .autonomous-workflow/checkpoint.json .autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json` printed all three paths; index remains empty. No file contents from `.env` were read.

Independent T2 re-review APPROVE; scoped T2 accepted. Approved W2 is explicitly retained, never presented as full-suite GREEN. T3 begins only after these observations.


## Archived implementer TDD command logs — T1 and T2

These excerpts are the named implementers' contemporaneous command/result reports, copied into the slice record under the owner's ordinary-log substitution. They are historical RED/GREEN observations, not current acceptance claims; later coordinator reruns and independent re-review dispositions above govern acceptance. All use the existing `.venv` with `PYTHONPATH=src` and external `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`.

### T1 implementer observations (`s12a_t1_framework`, local t1-report.md)

Commands were executed with these environment assignments inline, not by reading an environment file.

1. Before production edits:
   `pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py`
   → **20 failed, 1 passed in 0.14s**. Expected failures: missing kind/stage registries; helper stamp 1.1.0 instead of 1.0.0; validation failure did not refuse; unknown stage accepted; acquired pages stayed PENDING; build refused PENDING; malformed URL placeholders raised KeyError/IndexError/ValueError after terms/budget rather than recording ENDPOINT_UNVERIFIED. BaseConnector PENDING characterization passed. The tool truncated the lengthy repeated tracebacks; this report preserves the command, failure categories and exact terminal count rather than inventing missing traceback output.

2. After first implementation:
   `pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py tests/test_acquisition_snapshots.py tests/test_acquisition_connectors.py tests/test_acquisition_contracts.py tests/test_acquisition_coverage.py`
   → **1 failed, 49 passed in 6.19s**. The new injected-load assertion compared JSON lists with in-memory tuple fields. Corrected its expected representation to the written JSON; production serialization was already correct.

3. Added tests for stage-independent unit identity refusal, duplicate/reserved parameters, sentinel mappings, continuation preflight, and Comtrade/ZATCA classifications:
   `pytest -q tests/test_acquisition_normalization_status.py --tb=short`
   → **1 failed, 19 passed in 0.09s**. Expected RED: ZATCA had no parse_rows and classified parsed JSON as PENDING. Extracted the existing parser.

4. Added WITS quality tests:
   `pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py --tb=short`
   → **3 failed, 33 passed in 0.13s**. Empty row, bad HS6 and mismatched reporter were not rejected. Added actual row validation; no parser rows were fabricated.

5. Focused full acquisition regression:
   `pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py tests/test_acquisition_snapshots.py tests/test_acquisition_connectors.py tests/test_acquisition_contracts.py tests/test_acquisition_coverage.py tests/test_acquisition_reconstruction.py --tb=short`
   → **78 passed in 6.69s**.

6. Parent identified malformed-parser classification risk; added two real-acquire Comtrade regressions and a source-token URL compatibility regression:
   `pytest -q tests/test_acquisition_normalization_status.py --tb=short`
   → **3 failed, 20 passed in 0.10s**. Comtrade data:null raised TypeError, malformed period raised ValueError; the universe partner token incorrectly used WLD rather than configured 0. Added classification-only expected-error handling and the StageSpec URL callback.
   Three new modules then → **39 passed in 0.12s**.

7. Initial full gate:
   `pytest -q` → **1041 passed, 1 warning in 13.77s**.
   Reconstruction, integrity, frozen/golden and smoke also passed.

8. Parent caught an escaped ZATCA HTML regex regression introduced during extraction. Added original HTML attribute-shape test:
   `pytest -q tests/test_acquisition_normalization_status.py -k zatca_html --tb=short`
   → **1 failed, 23 deselected in 0.06s** (UNPARSED instead of NORMALIZED).
   Restored original single-backslash raw regex semantics and reran the same command:
   → **1 passed, 23 deselected in 0.04s**.
## Parent review correction: injected path containment

Parent and its bounded snapshot reviewer found that injected KindSpec.root could route write_snapshot or repository._load_kind outside the supplied data root or into protected public/synthetic evidence. This was a confirmed HIGH finding; the prior gate was not sufficient to approve the candidate.

Added ten temporary-directory regressions covering both write and load for public, synthetic, parent traversal, absolute and symlink-escape paths. Tests monkeypatch snapshots.PROJECT_ROOT to a temporary project and never use real frozen trees. Both operations must reject the path without creating files or directories; loader access must stop before reading a record.

RED command (same inline virtualenv/cache environment as above):

`pytest -q tests/test_acquisition_kind_registry.py -k injected_kind_root --tb=short`

Observed: **10 failed, 10 deselected in 0.11s**, each with `DID NOT RAISE` for the unsafe root. No real evidence was involved.

Implemented one private `_snapshot_directory(root, kind_root)` helper in existing snapshots.py, reused by write_snapshot and repository._load_kind. It rejects absolute roots, missing `data/` prefixes and parent traversal; resolves the final directory; checks containment in the supplied data root including symlink resolution; and rejects final paths inside protected public/synthetic evidence. The original write_snapshot root guard remains in place. No new module or public API was added for this correction.

Focused GREEN command:

`pytest -q tests/test_acquisition_kind_registry.py --tb=short`

Observed: **20 passed in 0.09s**, including legitimate TEST-KIND build/write/load/reconstruct and default-cache isolation.

### T2 implementer observations (`s12a_t2_contracts`, local t2-report.md)

## TDD and exact observed commands

Every Python/pytest command used the existing `.venv` executable with `PYTHONPATH=src` and `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`. No environment file was read.

1. RED before stage/kind implementation:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_stage_specs.py tests/test_acquisition_kind_registry.py --tb=short`
   Result: **5 failed, 25 passed in 0.13s**. Missing three institutional stages, named-key behavior, and new kind registrations.
2. After stage implementation, added institutional snapshot tests and all six fixtures; before row/kind implementation:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_stage_specs.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_kind_registry.py --tb=short`
   Result: **16 failed, 45 passed in 0.26s**. Missing kinds/mappers; one test-double setup error was a missing rate_limit key, corrected before further implementation. Repeated tracebacks were truncated by the tool, so only observed counts and categories are recorded.
3. Added numeric and row-validation tests and corrected the config double:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_institutional_snapshots.py --tb=no`
   Result: **19 failed, 16 passed in 0.10s** (missing kinds and mappers).
4. Implemented row contracts/mappers/kinds/support codes:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_stage_specs.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_kind_registry.py --tb=short`
   Result: **65 passed in 0.23s**.
5. Added loader and further preflight tests before wrappers:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_institutional_snapshots.py --tb=short`
   Result: **3 failed, 41 passed in 0.19s**, all three missing loader wrappers. Added thin wrappers.
6. Final focused proof:
   `PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_stage_specs.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_kind_registry.py tests/test_acquisition_normalization_status.py --tb=short`
   Result: **98 passed in 0.26s**.

RED, before production fixes:

```sh
.venv/bin/pytest -q tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_stage_specs.py -k 'cannot_hide or empty_years or row_interface' --tb=short
```

Observed **18 failed, 54 deselected in 0.16s**: fifteen DID NOT RAISE failures for default test-double acceptance, two DID NOT RAISE failures for aggregate empty years, and one missing Row alias assertion. Same command after fixes: **18 passed, 54 deselected in 0.09s**.

## T3 coordinator gate — 2026-09-11 UTC

Same existing virtualenv/PYTHONPATH/external-bytecode environment as above. Fresh coordinator command:

```bash
.venv/bin/pytest -q
```

Exit 1: **7 failed, 1348 passed, 1 warning in 15.22s**. Exactly the approved interim windows, without deselecting or weakening any test:

- W1: `test_repository_raw_store_has_no_stored_evidence_problems` reports only the five sources without raw records; `test_every_source_has_raw_record` fails for gastat, ministry_of_industry, modon, saber_registry and saso_catalogue. No credential/header detector error appears.
- W2: `test_missing_snapshot_kinds_cited_in_known_limitations` still raises `KeyError: 'directory'` in the old three-kind lookup.
- Existing Starlette/httpx deprecation is the sole warning.

Canonical [4]/[5]/[6]/[10]/[20]/[21]/[24] were read directly from parsed immutable plan-5 and executed unchanged via subprocess; all exit 0. [10] prints `PYTHON_STANDARDS_OK`, [20] `CONFIG_VERSION_PROVENANCE_OK`, [24] `SINGLE_SENTINEL_REPRESENTATION_OK`. [21]'s exact command and result:

```bash
PYTHONPATH=src pytest -q tests/test_acquisition_config.py -k "pre_observation or observed_values or recorded_on or unavailable_access or s11_mappings or unknown_source_key or forbidden_keys or live_yaml or sentinel or configured_credential"
```

Exit 0: **227 passed, 10 deselected in 1.58s**.

```bash
.venv/bin/python scripts/reconstruct_snapshot.py --all --no-check-manifest
.venv/bin/pytest -q tests/test_acquisition_reconstruction.py::test_reconstruct_matches_repository_partner_snapshot tests/test_frozen_public_evidence_pins.py tests/test_golden_cases.py
.venv/bin/python scripts/demo_smoke.py
```

Each exit 0: reconstruction **1 snapshot, 4 artifacts**; **22 passed in 0.95s**; smoke confirms steel/public `INVESTIGATE`, steel/simulated `ADVANCE` with real unchanged, polypropylene/public `REJECT` generic capacity, extraction 100%.

The approved config change intentionally precedes T11's single manifest generation. No manifest refresh occurred; this section does not claim a fresh standalone integrity PASS after the config change. T3 independent review is pending at this observation.

### Final T3 observations and acceptance

After the implementer constrained the detector meta-tests' missing-directory baseline to exactly the five institutional source IDs, coordinator reran:

```bash
.venv/bin/pytest -q tests/test_acquisition_stored_artifacts.py -k 'detector_'
.venv/bin/pytest -q
.venv/bin/python scripts/verify_integrity.py
```

Results, respectively: exit 0, **16 passed, 30 deselected in 0.10s**; exit 1, **7 failed, 1348 passed, 1 warning in 15.47s**, exactly the same W1/W2 failures above; exit 1, only the expected config hash difference:

```text
INTEGRITY FAIL
- Hash mismatch: config/acquisition_sources.v1.yaml expected=106ebfd8c4172fb8707789b61e6501c5254f41a58b1b8e524d54d26129a9d9f2 actual=3b64e4632dc2631085b1f4ada25c438ebbe3bf020a4665ab304cab39c74836d0
```

Independent T3 review APPROVE, no findings. The documented T3 gate is satisfied; not full-slice completion or full-suite GREEN. T4 begins after this gate; no manifest generation occurred.

### T3 implementer RED/GREEN command log

Source: the implementer's local `t3-report.md`, read by the coordinator; the coordinator's independent final executions are recorded above. These are archived implementer observations, not additional coordinator executions. All commands used the existing virtualenv PATH, `PYTHONPATH=src`, and external bytecode prefix recorded above.

Before production/config changes:

```bash
pytest -q tests/test_acquisition_config.py tests/test_acquisition_stored_artifacts.py --tb=no
```

Exit 1: **225 failed, 43 passed in 1.54s**; no collection errors. This predates ten later positive/key-completeness tests.

```bash
pytest -q tests/test_acquisition_config.py::test_loads_yaml_version_and_nine_sources tests/test_acquisition_config.py::test_institutional_pre_observation_entry_accepted tests/test_acquisition_config.py::test_configured_credential_env_var_helper tests/test_acquisition_config.py::test_institutional_observed_values_accepted tests/test_acquisition_stored_artifacts.py::test_detector_sentinel_configured_source_is_uncredentialed --tb=short
```

Exit 1: **16 failed in 0.18s**. RED reasons: old 1.0.0/version-four-source expectation, absent shared credential helper, sentinel interpreted as an environment-variable name. Invalid-input cases first validate their unmutated valid fixture so the old version gate cannot falsely satisfy rejection tests.

After production/config changes:

```bash
pytest -q tests/test_acquisition_config.py tests/test_acquisition_stored_artifacts.py --tb=short
```

Exit 1: **277 passed, 6 failed in 1.81s**; the six failures are exactly W1, not a fully GREEN command.

```bash
pytest -q tests/test_acquisition_config.py tests/test_acquisition_stored_artifacts.py::test_detector_meta_credential_absent_credential_env_var_changed tests/test_acquisition_stored_artifacts.py::test_detector_meta_sentinel_credential_in_stored_record_flagged tests/test_acquisition_stored_artifacts.py::test_detector_sentinel_configured_source_is_uncredentialed tests/test_acquisition_reconstruction.py::test_reconstruct_matches_repository_partner_snapshot tests/test_frozen_public_evidence_pins.py tests/test_golden_cases.py
```

Exit 0: **262 passed in 2.51s**. The complete coordinator gate above follows the final detector-test strengthening and independent review.

## T4 coordinator observations — independent reviews pending

Same existing virtualenv PATH, `PYTHONPATH=src`, external bytecode prefix as above. No live source calls or manifest generation.

```bash
.venv/bin/pytest -q tests/test_acquisition_institutional_connectors.py tests/test_acquisition_connectors.py tests/test_acquisition_reconstruction.py::test_reconstruct_matches_repository_partner_snapshot tests/test_frozen_public_evidence_pins.py tests/test_golden_cases.py
.venv/bin/pytest -q --tb=short
.venv/bin/python scripts/reconstruct_snapshot.py --all --no-check-manifest
.venv/bin/python scripts/demo_smoke.py
.venv/bin/python scripts/verify_integrity.py
```

Observed results in order:

- Focused/frozen: exit 0, **369 passed in 7.50s**.
- Full suite: exit 1, **7 failed, 1688 passed, 1 warning in 15.96s**. Exactly six W1 failures (the missing-record detector plus one missing raw directory per institutional source) and one W2 (`test_missing_snapshot_kinds_cited_in_known_limitations`, existing `KeyError: directory`). No unexpected failure. Existing Starlette/httpx deprecation warning only.
- Reconstruction: exit 0, **1 snapshot, 4 artifacts**.
- Smoke: exit 0, steel/public `INVESTIGATE`, steel/simulated `ADVANCE` with real unchanged, polypropylene/public `REJECT` generic capacity, extraction 100%.
- Integrity: exit 1, only acquisition config hash difference expected until T11: expected `106ebfd8c4172fb8707789b61e6501c5254f41a58b1b8e524d54d26129a9d9f2`, actual `3b64e4632dc2631085b1f4ada25c438ebbe3bf020a4665ab304cab39c74836d0`.

Canonical commands loaded from parsed plan-5 bytes after SHA verification and passed unchanged to subprocess execution. Exact command/output capture:

```text
VERIFICATION[4] COMMAND: git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
VERIFICATION[4] EXIT: 0
VERIFICATION[5] COMMAND: git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
VERIFICATION[5] EXIT: 0
VERIFICATION[6] COMMAND: git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
VERIFICATION[6] EXIT: 0
VERIFICATION[10] COMMAND: PYTHONPATH=src python3 -c "import ast,sys; from pathlib import Path; bad=[]; [bad.append((str(p),n.lineno)) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,ast.ExceptHandler) and n.type is None]; miss=[(str(p),f.name) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for f in ast.parse(p.read_text(encoding='utf-8')).body if isinstance(f,ast.FunctionDef) and not f.name.startswith('_') and (f.returns is None or any(a.annotation is None for a in f.args.args if a.arg not in ('self','cls')))]; assert not bad, bad; assert not miss, miss; print('PYTHON_STANDARDS_OK')"
PYTHON_STANDARDS_OK
VERIFICATION[10] EXIT: 0
VERIFICATION[20] COMMAND: PYTHONPATH=src python3 -c "import json,yaml,subprocess; from pathlib import Path; from ior_mvp.acquisition.kinds import default_kind_registry; from ior_mvp.acquisition.harmonise import PIPELINE_VERSION; k=default_kind_registry(); assert PIPELINE_VERSION=='1.0.0'; assert {x:k.get(x).config_version for x in k.ids()}=={'universe':'1.0.0','tariff':'1.0.0','partners':'1.0.0','production':'1.1.0','directory':'1.1.0','registry':'1.1.0'}; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; head=yaml.safe_load(subprocess.check_output(['git','show','HEAD:config/acquisition_sources.v1.yaml'])); assert all(cfg['sources'][s]==head['sources'][s] for s in ('wits_trade','un_comtrade','baci_cepii','zatca_tariff')); snap=json.loads(Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json').read_text(encoding='utf-8')); assert snap['transformation_record']['config_version']=='1.0.0' and snap['transformation_record']['pipeline_version']=='1.0.0' and all(e['transformation_record']['config_version']=='1.0.0' for e in snap['evidence']); print('CONFIG_VERSION_PROVENANCE_OK')"
CONFIG_VERSION_PROVENANCE_OK
VERIFICATION[20] EXIT: 0
VERIFICATION[24] COMMAND: PYTHONPATH=src python3 -c "from ior_mvp.acquisition.contracts import UNAVAILABLE; from ior_mvp.acquisition.source_config import CREDENTIAL_PATTERN, INSTITUTIONAL_SOURCE_IDS, acquisition_sources_config, configured_credential_env_var, observation_state, observed_fact_values; assert configured_credential_env_var({'credential_env_var': UNAVAILABLE}) is None and configured_credential_env_var({'credential_env_var': None}) is None and configured_credential_env_var({'credential_env_var': ''}) is None and configured_credential_env_var({'credential_env_var': 'IOR_X'}) == 'IOR_X'; src=acquisition_sources_config()['sources']; pins={'wits_trade': None, 'baci_cepii': None, 'zatca_tariff': None, 'un_comtrade': 'IOR_COMTRADE_SUBSCRIPTION_KEY'}; assert {s: src[s]['credential_env_var'] for s in pins} == pins, 'S11 credential pins changed'; assert set(INSTITUTIONAL_SOURCE_IDS) == {'gastat', 'ministry_of_industry', 'modon', 'saso_catalogue', 'saber_registry'}; bad=[(s, k, v) for s in sorted(INSTITUTIONAL_SOURCE_IDS) if src[s]['recorded_on'] == UNAVAILABLE for k, v in observed_fact_values(s, src[s]).items() if v != UNAVAILABLE]; assert not bad, bad; assert all(len(observed_fact_values(s, src[s])) == 17 for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == ('PRE_OBSERVATION' if all(v == UNAVAILABLE for v in observed_fact_values(s, src[s]).values()) else 'OBSERVED') for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == 'PRE_OBSERVATION' for s in INSTITUTIONAL_SOURCE_IDS if src[s]['recorded_on'] == UNAVAILABLE); assert all(src[s]['credential_env_var'] is None or src[s]['credential_env_var'] == UNAVAILABLE or (isinstance(src[s]['credential_env_var'], str) and CREDENTIAL_PATTERN.fullmatch(src[s]['credential_env_var']) is not None) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['parameters']['flow_tokens'] == UNAVAILABLE or isinstance(src[s]['parameters']['flow_tokens'], dict) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['pagination']['parameters'] == UNAVAILABLE or isinstance(src[s]['pagination']['parameters'], dict) for s in INSTITUTIONAL_SOURCE_IDS); print('SINGLE_SENTINEL_REPRESENTATION_OK')"
SINGLE_SENTINEL_REPRESENTATION_OK
VERIFICATION[24] EXIT: 0
VERIFICATION[25] COMMAND: PYTHONPATH=src pytest -q tests/test_acquisition_institutional_connectors.py -k "pre_observation or sentinel or credential or license_unrecorded"
..........................                                               [100%]
26 passed, 314 deselected in 0.09s
VERIFICATION[25] EXIT: 0
```

These observations do not pre-approve the candidate; both bounded independent T4 reviews remain pending. T5 has not begun.

### T4 implementer initial RED

Source: local `t4-red.log`, command and final result read by the coordinator. This is an archived implementer observation, not a new execution.

```bash
PATH=/home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin:$PATH PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode pytest -q --tb=line tests/test_acquisition_institutional_connectors.py tests/test_acquisition_connectors.py
```

Exit 1: **142 failed, 74 passed in 6.39s** before implementation. Examples in the captured output: missing institutional registrations, literal sentinel stored as credential name, canary Authorization sent for sentinel, and absent privacy refusal. After implementation the implementer disclosed seven test-construction errors using a QueryContract reporter prohibited by its existing constructor; these were corrected to test mismatched configured reporters and are not misrepresented as new production defects. The later coordinator focused/full results above include the expanded privacy matrix.

### T4-R1/R2 repair and final coordinator gate

The initial candidate was rejected for two missing approved interfaces despite passing tests of its implemented paths: snapshot delegation and nullable parser protocol membership. Implementer correction log `t4-r1-r2-red.log` records this exact command under the same environment:

```bash
pytest -q --tb=short tests/test_acquisition_institutional_connectors.py -k 'snapshot_helper or protocol_has_optional_parser'
```

RED exit 1: **11 failed, 340 deselected in 0.21s**—ten NotImplementedError snapshot cases and one absent protocol declaration. Implementer reran unchanged after the two production fixes: **11 passed, 340 deselected**. No test-construction correction was needed in this repair.

Coordinator independently reran the focused/frozen command and complete suite shown in the T4 observations above after the fixes:

- Focused/frozen: exit 0, **380 passed in 7.57s**.
- `.venv/bin/pytest -q --tb=short`: exit 1, **7 failed, 1699 passed, 1 warning in 15.89s**. Exact same six W1 and one W2 failures, no unexpected failure.
- Re-executed canonical [4]/[5]/[6]/[10]/[20]/[24]/[25] from SHA-verified parsed immutable JSON, unchanged strings printed above: every exit 0; [25] now **26 passed, 325 deselected in 0.09s**.
- Reconstruction `--all --no-check-manifest`: exit 0, 1 snapshot/4 artifacts. Smoke: exit 0, unchanged four invariants. The smoke rerun used the explicit virtualenv executable; the preceding reconstruction command carried the explicit cache/PYTHONPATH environment.
- `git diff --check`, `git diff --cached --quiet`, and extra HEAD-byte checks for acquisition init/main/connectors-init plus machine manifests: exit 0. Branch and HEAD remain the approved branch/base.

Independent privacy review APPROVE and connector re-review APPROVE, no remaining findings. Coordinator accepts T4 for T5. No manifest generation; standalone integrity remains the disclosed config-only mismatch until T11. This is not full-slice delivery approval.

## T5 implementer initial RED

Source: local `t5-red.log` and `t5-guard-red.log`; command and final output read by the coordinator. Existing virtualenv PATH, `PYTHONPATH=src`, external bytecode prefix as above. These are archived implementer runs, not coordinator reruns.

```bash
pytest -q --tb=short tests/test_acquisition_cli.py tests/test_acquisition_reconstruction.py
```

Exit 1: **26 failed, 37 passed in 15.13s** before production changes. Missing commands, wrappers and Make targets explain the RED; existing generic kind build, unit planning and temp institutional reconstruction paths already pass.

```bash
pytest -q --tb=short tests/test_acquisition_cli.py::test_dependency_live_seam_checks_permission_but_build_remains_offline
```

Exit 1: **1 failed in 0.42s**, DID NOT RAISE OfflineGuardViolation, independently exposing the pre-dependency permission gap without depending on missing parser commands. No test-construction errors reported in either RED run. Positive module tests inject pre-observation config and a fetch double that raises if called; positive Make tests use `UV_RUN=echo`.

### T5 coordinator candidate gate — review pending

After implementation, coordinator ran with the same virtualenv/cache environment:

```bash
.venv/bin/pytest -q --tb=short
.venv/bin/pytest -q tests/test_acquisition_cli.py tests/test_acquisition_reconstruction.py tests/test_frozen_public_evidence_pins.py tests/test_golden_cases.py
.venv/bin/python scripts/reconstruct_snapshot.py --all --no-check-manifest
.venv/bin/python scripts/verify_integrity.py
```

Observed results, in order:

- Full suite: exit 1, **7 failed, 1747 passed, 1 warning in 15.62s**. Exact same six W1 and one W2 failures listed above; no new failure.
- Focused/frozen: exit 0, **85 passed in 8.55s**.
- Reconstruction: exit 0, **1 snapshot/4 artifacts**.
- Integrity: exit 1, only unchanged acquisition-config hash mismatch expected until T11 (expected `106ebfd8c4172fb8707789b61e6501c5254f41a58b1b8e524d54d26129a9d9f2`, actual `3b64e4632dc2631085b1f4ada25c438ebbe3bf020a4665ab304cab39c74836d0`).

Canonical [4]/[5]/[6]/[7]/[8]/[10]/[11]/[20]/[24]/[25] were loaded directly from SHA-verified plan JSON and executed unchanged, all exit 0. [4]/[5]/[6]/[10]/[20]/[24]/[25] command strings are already captured above. Additional exact commands in this run:

```bash
PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py
PYTHONPATH=src python3 scripts/demo_smoke.py
python3 scripts/check_prohibited_files.py && python3 scripts/check_threshold_literals.py && python3 -m compileall -q src scripts tests
```

[7]: **42 passed in 5.85s**. [8]: smoke PASS, all four frozen demonstration invariants unchanged. [11]: prohibited scan PASS (524 tracked files), threshold scan PASS (47 Python files; 23 configured values), compileall exit 0. [25]: **26 passed, 325 deselected in 0.40s**. This tracked-file scan does not claim to scan prospective untracked additions.

`git diff --check`, empty-index check, and direct frozen acquisition init/main/connectors-init plus machine-manifest checks exit 0. Eight existing reconstruction subprocess environment mappings now preserve PATH/external PYTHONPYCACHEPREFIX; their assertions remain unchanged. Independent T5 review pending; T6 has not begun.

T5 independent review subsequently APPROVE with no findings. No candidate edits followed the coordinator observations above. T5 accepted for T6; neither full-suite GREEN nor delivery approval is claimed while the named interim windows remain open.

## T6 test-first and coordinator verification

All commands used the existing virtualenv PATH, `PYTHONPATH=src` and external bytecode prefix recorded above. Coordinator read complete implementer RED/GREEN logs and candidate report.

```bash
pytest -q tests/test_integrity_contract.py tests/test_acquisition_snapshots.py
```

Implementer baseline: exit 1, 21 passed / W2 KeyError (0.09s). After stronger assertions but before pin infrastructure: exit 1, 19 passed / 4 failed (0.13s): exact-prefix acceptance, loader completeness, W2 and new W4. No test-construction error. After implementation:

```bash
pytest -q tests/test_integrity_contract.py::test_s08_snapshot_manifest_retains_live_and_historical_public_rows tests/test_integrity_contract.py::test_s11_snapshot_manifest_rejects_public_partition_leak tests/test_acquisition_snapshots.py
```

Exit 0, 11 passed (0.08s). Full implementer run: 1747 passed / exactly 8 W1/W2/W4 failures, one existing warning (15.71s). Coordinator independently reran:

```bash
.venv/bin/pytest -q --tb=short
pytest -q tests/test_integrity_contract.py::test_s11_snapshot_manifest_rejects_public_partition_leak tests/test_acquisition_snapshots.py tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py
python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
python3 scripts/verify_integrity.py
python3 scripts/demo_smoke.py
git diff --check
git diff --cached --exit-code
git diff --quiet HEAD -- src/ior_mvp/acquisition/__init__.py src/ior_mvp/acquisition/__main__.py src/ior_mvp/acquisition/connectors/__init__.py docs/core data/manifests docs/authority/authority_hashes.json
```

Results: full exit 1, **1747 passed, exactly 8 failed, one existing warning in 15.97s**. Six W1 failures are unchanged; W2 correctly reaches missing ministry raw directory; W4 reaches the unchanged Core 05 first institutional row. Focused/frozen exit 0, **31 passed in 0.95s**. Reconstruction exit 0, **1 snapshot/4 artifacts**. Integrity exit 1, only the same config mismatch (actual `3b64e4632dc2631085b1f4ada25c438ebbe3bf020a4665ab304cab39c74836d0`). Smoke exit 0, all four prior invariants. Diagnostic command-entry mistake `python3 scripts/smoke_demo.py` first exited 2 (nonexistent filename), then corrected to the existing command shown above; no code change. Git checks exit 0.

Canonical [4]/[5]/[6]/[10]/[20]/[24]/[25] executed unchanged from parsed immutable plan, all exit 0. [25]: 26 passed / 325 deselected (0.09s). Their exact strings are archived above. Additional implementer canonical results [0]/[1]/[3]/[7]/[8]/[11]/[21]/[23] exit 0 in `t6-gates.log`; coordinator does not label these as personal reruns. No generation or post-generation [12]/[17], no premature [26]. [22] remains superseded, never PASS.

Independent T6 review APPROVE, zero findings. T6 accepted for T7 only. Full delivery gates remain mandatory after the explicitly bounded windows close.

## T7 interim GASTAT config regression

After recording only verified GASTAT documentation/terms facts and making its guarded zero-request attempt, coordinator ran (normal offline test environment, no live flag):

```bash
.venv/bin/pytest -q tests/test_acquisition_config.py tests/test_acquisition_institutional_connectors.py tests/test_acquisition_stored_artifacts.py -k 'not test_repository_raw_store_has_no_stored_evidence_problems and not test_every_source_has_raw_record'
```

Exit 0, 624 passed / 10 deselected in 2.38s. This is a focused interim regression, not a full-suite result; the raw-record oracles are deferred only until all five T7 commands finish. GASTAT guarded Make command and complete RunReport are captured in implementation_log.md.

## T7 full candidate checks after all five runs

Acquisition commands, their exact parameters, Make/app exit-code distinction and complete emitted RunReport JSON values are archived in implementation_log.md. Each emitted application exit 3 (Make exit 2), ENDPOINT_UNVERIFIED, zero requests/pages. Build command exit 0; BuildReport values archived there; only the preexisting partner snapshot is built. No live flag on any command below:

```bash
.venv/bin/pytest -q --tb=short
.venv/bin/pytest -q tests/test_acquisition_stored_artifacts.py tests/test_acquisition_config.py tests/test_acquisition_reconstruction.py tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py
python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
python3 scripts/verify_integrity.py
python3 scripts/demo_smoke.py
git diff --check
git diff --cached --quiet
git diff --quiet HEAD -- data/manifests docs/authority/authority_hashes.json docs/core src/ior_mvp/acquisition/__main__.py
```

Coordinator full suite: exit 1, **1753 passed, exactly 2 failed, one existing warning in 15.78s**. W1 is closed. Remaining failures are W4 Core status literals (T8) and W2 missing Ministry KL citation (T9). Focused group: exit 0, **332 passed in 4.07s**. Reconstruction: exit 0, 1 snapshot/4 artifacts. Smoke: exit 0, all four invariants unchanged. Integrity: exit 1, only authorized acquisition-config mismatch, current SHA `cb84f1632632e531778dbc9f7c1fe249bfa87d34604de27b538eac696dd708c2`. Git checks exit 0.

Canonical [4]/[5]/[6]/[9]/[20]/[24] executed directly from parsed plan JSON, every exit 0. [9] now prints CONFIG_AND_RAW_RECORDS_OK. Exact [9] command is retained in immutable plan and the final full ladder capture; no substitute command used. Read-only raw audit confirms exactly attempt.json + coverage.json per new source, sibling coverage equals embedded coverage, credentials null/false, response null, zero pages/requests and honest INCOMPLETE/ENDPOINT_UNVERIFIED. Dates are 2026-09-11 UTC; Ministry/MODON PRE_OBSERVATION, GASTAT/SASO/SABER OBSERVED due only to recorded documentation facts. Source records are write-once; no acquired bodies exist for these runs. Independent T7 review pending; T8 has not started.

T7 independent review subsequently APPROVE, zero findings. Reviewer independently recomputed all five query hashes and compared canonical embedded coverage bytes to sibling file hashes. No edits followed the coordinator gate. T7 accepted and live window closed; T8 authorized.

## T8 Core contract gate

Implementer observed the existing `test_s12a_core_v2_institutional_contracts` RED before edits (1 failed), then the same test plus the marker test GREEN (2 passed). Only Core03/04/05/09 changed. Implementer full regression: 1754 passed, one W2 failure, one existing warning in 15.59s. Core03 and Core09 each have exactly 2 additions / 0 deletions; Core05 §3.1 and the six non-S12a institutional table rows remain byte-identical. W4 is closed.

Coordinator independently ran, with the established external bytecode environment and no live flag:

```bash
.venv/bin/pytest -q --tb=short
```

Exit 1: **1754 passed, exactly one W2 failure, one existing warning in 18.08s**. The sole failure is `tests/test_integrity_contract.py::test_missing_snapshot_kinds_cited_in_known_limitations`, missing the Ministry source/query citation that T9 owns. No tests were weakened.

Coordinator ran exact parsed plan commands [3]/[4]/[5]/[6]/[8]/[20]/[23]/[26]; every exit 0. Reconstruction: 1 snapshot / 4 artifacts. Smoke: steel public INVESTIGATE, steel simulated ADVANCE with unchanged real state, polypropylene public REJECT generic capacity, extraction golden 100%. [23] reports 2/0 additions/deletions for each Core03/09 file; [26] prints CORE_05_STATUS_ROWS_OK. The six identity commands will all be captured verbatim again in the final ladder after the single generation.

Implementer additionally ran canonical [0]/[7]/[9]/[10]/[11]/[24], all exit 0; [7] 42 passed. Its diagnostic integrity check exits 1 on exactly the five authorized pre-T11 hash mismatches (acquisition config and Core03/04/05/09), not a PASS. Full integrity-contract module: 13 passed, same W2 failure. Exact detailed implementer logs remain local at `.autonomous-workflow/drafts/s12a-acquisition-framework-institutional-sources/t8-{red,green,full,gates}.log`; report at `t8-report.md`. No manifest generation or source network during T8.

Independent pre-manifest review of contracts/kinds/coverage/snapshots/repository and associated tests by `s12a_t6_boundary_map`: APPROVE, zero findings. This is a bounded review, not session implementation approval or whole-slice completion.

T8 independent Core review by `s12a_t5_boundary_map`: APPROVE, zero findings. It independently ran [23]/[26] and the two scoped Core/marker tests (2 passed), checked exact policy and dataclass/registry correspondence, and verified all four Core candidate hashes. T8 accepted; T9 authorized. The manifests and generator remain byte-identical to HEAD and count remains 0.

## Complementary pre-manifest production review

`s12a_t6_boundary_map` independently reviewed source configuration, shared connector lifecycle/privacy, five thin institutional connectors, CLI/pipeline/Make interfaces, reconstruction and old-source parser exposure: APPROVE, zero findings in that bounded scope. It ran:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode .venv/bin/pytest -q tests/test_acquisition_config.py tests/test_acquisition_connectors.py tests/test_acquisition_normalization_status.py tests/test_acquisition_institutional_connectors.py tests/test_acquisition_cli.py tests/test_acquisition_reconstruction.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths --tb=short
git diff --check
```

Both exit 0; focused suite **682 passed, 1 deselected in 12.30s**. Only the named manifest-coupled test was deselected. No review edits, network, generation or staging. The preexisting RunReport/Comtrade/custom-build-root limitations were retained as explicit deferrals. Together with its earlier contracts/kinds/coverage/snapshots/repository review, this covers the generalized production implementation before T11; it does not substitute for session implementation approval or final full verification.

## T9 controls and citation gate

Implementer: named missing-KL RED 1 failed before edits; full integrity-contract GREEN 14 passed. Unrestricted full suite 1755 passed / 1 warning in 16.00s, repeated after final template additions: 1755 passed / 1 warning in 15.85s. Exact local commands/output at `t9-{red,green,full,final,gates,invariants}.log` beside `t9-report.md`. No tests changed or excluded. Diagnostic integrity still reports only the five authorized pre-T11 hash mismatches, not PASS.

Coordinator independently ran `.venv/bin/pytest -q --tb=short` with the established PATH/PYTHONPATH/external cache environment: **exit 0, 1755 passed, 1 existing Starlette warning in 15.80s**. Read-only assertions verified historical controls unchanged and all three exact original split goals/dependencies in state and roadmap (SPLIT_EXACT_GOALS_AND_DEPENDENCIES_PASS). The first diagnostic used the wrong original child key (`task_id`); corrected to existing `child_task_id`, then passed without file changes. `git diff --check`, empty-index check and unchanged-manifests/generator check exit 0. Independent T9 review APPROVE, zero findings, including exact future template, raw identities, owner/ADR scope and honest statuses; its named W2 test passes. T9 accepted; T10 authorized. Both manifests remain at HEAD and generation count is 0.


## T10 pre-generation full ladder — coordinator capture

All commands below inherit existing `.venv/bin` first in PATH, `PYTHONPATH=src`, `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode` and `UV_OFFLINE=1`, no live flag. Plan-5 SHA was checked before parsing commands. Every executed command exited 0; [22] is superseded, not executed or called PASS. [12] was not run before generation. The filtered command excludes only the approved integrity module and single reconstruction test; independent T9 full pytest already passes with no exclusions.

```text
COMMAND [T10 full filtered] PYTHONPATH=src pytest -q --ignore=tests/test_integrity_contract.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths
........................................................................ [  4%]
........................................................................ [  8%]
........................................................................ [ 12%]
........................................................................ [ 16%]
........................................................................ [ 20%]
........................................................................ [ 24%]
........................................................................ [ 28%]
........................................................................ [ 33%]
........................................................................ [ 37%]
........................................................................ [ 41%]
........................................................................ [ 45%]
........................................................................ [ 49%]
........................................................................ [ 53%]
........................................................................ [ 57%]
........................................................................ [ 62%]
........................................................................ [ 66%]
........................................................................ [ 70%]
........................................................................ [ 74%]
........................................................................ [ 78%]
........................................................................ [ 82%]
........................................................................ [ 86%]
........................................................................ [ 91%]
........................................................................ [ 95%]
........................................................................ [ 99%]
............                                                             [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1740 passed, 1 deselected, 1 warning in 15.81s
EXIT 0

COMMAND [0] test "$(git branch --show-current)" = slice/s12a-acquisition-framework-institutional-sources && git merge-base --is-ancestor a043ed8dc1d477de50149b39de657bc963e785d7 HEAD
EXIT 0

COMMAND [1] PYTHONPATH=src pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py
.........................................................                [100%]
57 passed in 0.15s
EXIT 0

COMMAND [2] PYTHONPATH=src pytest -q tests/test_acquisition_institutional_connectors.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_config.py tests/test_acquisition_connectors.py tests/test_acquisition_cli.py tests/test_acquisition_contracts.py tests/test_acquisition_reconstruction.py tests/test_acquisition_snapshots.py tests/test_acquisition_stored_artifacts.py
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 27%]
........................................................................ [ 36%]
........................................................................ [ 45%]
........................................................................ [ 55%]
........................................................................ [ 64%]
........................................................................ [ 73%]
........................................................................ [ 82%]
........................................................................ [ 91%]
...............................................................          [100%]
783 passed in 11.22s
EXIT 0

COMMAND [3] PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
EXIT 0

COMMAND [4] git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
EXIT 0

COMMAND [5] git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
EXIT 0

COMMAND [6] git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
EXIT 0

COMMAND [7] PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py
..........................................                               [100%]
42 passed in 1.19s
EXIT 0

COMMAND [8] PYTHONPATH=src python3 scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
EXIT 0

COMMAND [9] PYTHONPATH=src python3 -c "import json,yaml,sys; from pathlib import Path; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; ids=set(cfg['sources']); assert ids=={'wits_trade','un_comtrade','baci_cepii','zatca_tariff','gastat','ministry_of_industry','modon','saso_catalogue','saber_registry'}, ids; cls={'gastat':'B','ministry_of_industry':'B','modon':'C','saso_catalogue':'B','saber_registry':'C'}; assert all(cfg['sources'][s]['default_evidence_class']==c for s,c in cls.items()); assert all((Path('data/raw')/s).is_dir() and (any((Path('data/raw')/s).rglob('page-*.contract.json')) or any((Path('data/raw')/s).rglob('attempt.json'))) for s in cls), 'raw record missing'; print('CONFIG_AND_RAW_RECORDS_OK')"
CONFIG_AND_RAW_RECORDS_OK
EXIT 0

COMMAND [10] PYTHONPATH=src python3 -c "import ast,sys; from pathlib import Path; bad=[]; [bad.append((str(p),n.lineno)) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,ast.ExceptHandler) and n.type is None]; miss=[(str(p),f.name) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for f in ast.parse(p.read_text(encoding='utf-8')).body if isinstance(f,ast.FunctionDef) and not f.name.startswith('_') and (f.returns is None or any(a.annotation is None for a in f.args.args if a.arg not in ('self','cls')))]; assert not bad, bad; assert not miss, miss; print('PYTHON_STANDARDS_OK')"
PYTHON_STANDARDS_OK
EXIT 0

COMMAND [11] python3 scripts/check_prohibited_files.py && python3 scripts/check_threshold_literals.py && python3 -m compileall -q src scripts tests
PROHIBITED FILE SCAN PASS (524 tracked files)
THRESHOLD LITERAL SCAN PASS (47 Python files; 23 configured numeric values)
EXIT 0

COMMAND [20] PYTHONPATH=src python3 -c "import json,yaml,subprocess; from pathlib import Path; from ior_mvp.acquisition.kinds import default_kind_registry; from ior_mvp.acquisition.harmonise import PIPELINE_VERSION; k=default_kind_registry(); assert PIPELINE_VERSION=='1.0.0'; assert {x:k.get(x).config_version for x in k.ids()}=={'universe':'1.0.0','tariff':'1.0.0','partners':'1.0.0','production':'1.1.0','directory':'1.1.0','registry':'1.1.0'}; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; head=yaml.safe_load(subprocess.check_output(['git','show','HEAD:config/acquisition_sources.v1.yaml'])); assert all(cfg['sources'][s]==head['sources'][s] for s in ('wits_trade','un_comtrade','baci_cepii','zatca_tariff')); snap=json.loads(Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json').read_text(encoding='utf-8')); assert snap['transformation_record']['config_version']=='1.0.0' and snap['transformation_record']['pipeline_version']=='1.0.0' and all(e['transformation_record']['config_version']=='1.0.0' for e in snap['evidence']); print('CONFIG_VERSION_PROVENANCE_OK')"
CONFIG_VERSION_PROVENANCE_OK
EXIT 0

COMMAND [21] PYTHONPATH=src pytest -q tests/test_acquisition_config.py -k "pre_observation or observed_values or recorded_on or unavailable_access or s11_mappings or unknown_source_key or forbidden_keys or live_yaml or sentinel or configured_credential"
........................................................................ [ 31%]
........................................................................ [ 63%]
........................................................................ [ 95%]
...........                                                              [100%]
227 passed, 10 deselected in 1.41s
EXIT 0

COMMAND [22] SUPERSEDED_BY_OWNER_RULING: .autonomous-workflow/owner-decisions/20260911-owner-direct-s12a-implementation.md — no plugin-classifier command is executed or claimed PASS; substantive no-destructive-Git policy remains.
SUPERSEDED_BY_OWNER_RULING; NOT EXECUTED; NOT PASS

COMMAND [23] PYTHONPATH=src python3 -c "import subprocess; rows=[l.split('\t') for l in subprocess.check_output(['git','diff','--numstat','HEAD','--','docs/core/03_SYSTEM_ARCHITECTURE.md','docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md'],text=True).splitlines() if l.strip()]; assert all(r[1]=='0' for r in rows), rows; assert all(int(r[0])<=3 for r in rows), rows; print('CORE_03_09_INSERTION_ONLY_OK', rows)"
CORE_03_09_INSERTION_ONLY_OK [['2', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
EXIT 0

COMMAND [24] PYTHONPATH=src python3 -c "from ior_mvp.acquisition.contracts import UNAVAILABLE; from ior_mvp.acquisition.source_config import CREDENTIAL_PATTERN, INSTITUTIONAL_SOURCE_IDS, acquisition_sources_config, configured_credential_env_var, observation_state, observed_fact_values; assert configured_credential_env_var({'credential_env_var': UNAVAILABLE}) is None and configured_credential_env_var({'credential_env_var': None}) is None and configured_credential_env_var({'credential_env_var': ''}) is None and configured_credential_env_var({'credential_env_var': 'IOR_X'}) == 'IOR_X'; src=acquisition_sources_config()['sources']; pins={'wits_trade': None, 'baci_cepii': None, 'zatca_tariff': None, 'un_comtrade': 'IOR_COMTRADE_SUBSCRIPTION_KEY'}; assert {s: src[s]['credential_env_var'] for s in pins} == pins, 'S11 credential pins changed'; assert set(INSTITUTIONAL_SOURCE_IDS) == {'gastat', 'ministry_of_industry', 'modon', 'saso_catalogue', 'saber_registry'}; bad=[(s, k, v) for s in sorted(INSTITUTIONAL_SOURCE_IDS) if src[s]['recorded_on'] == UNAVAILABLE for k, v in observed_fact_values(s, src[s]).items() if v != UNAVAILABLE]; assert not bad, bad; assert all(len(observed_fact_values(s, src[s])) == 17 for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == ('PRE_OBSERVATION' if all(v == UNAVAILABLE for v in observed_fact_values(s, src[s]).values()) else 'OBSERVED') for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == 'PRE_OBSERVATION' for s in INSTITUTIONAL_SOURCE_IDS if src[s]['recorded_on'] == UNAVAILABLE); assert all(src[s]['credential_env_var'] is None or src[s]['credential_env_var'] == UNAVAILABLE or (isinstance(src[s]['credential_env_var'], str) and CREDENTIAL_PATTERN.fullmatch(src[s]['credential_env_var']) is not None) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['parameters']['flow_tokens'] == UNAVAILABLE or isinstance(src[s]['parameters']['flow_tokens'], dict) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['pagination']['parameters'] == UNAVAILABLE or isinstance(src[s]['pagination']['parameters'], dict) for s in INSTITUTIONAL_SOURCE_IDS); print('SINGLE_SENTINEL_REPRESENTATION_OK')"
SINGLE_SENTINEL_REPRESENTATION_OK
EXIT 0

COMMAND [25] PYTHONPATH=src pytest -q tests/test_acquisition_institutional_connectors.py -k "pre_observation or sentinel or credential or license_unrecorded"
..........................                                               [100%]
26 passed, 325 deselected in 0.11s
EXIT 0

COMMAND [26] PYTHONPATH=src python3 -c "import subprocess; from pathlib import Path; P='docs/core/05_DATA_SOURCES_AND_INGESTION.md'; new=Path(P).read_text(encoding='utf-8'); old=subprocess.check_output(['git','show','HEAD:'+P],text=True); blk=lambda t,a,b: t.split(a,1)[1].split(b,1)[0]; H=('### 3.1 Trade and demand','### 3.2 Supply and capability','### 3.3 Specifications and qualification','### 3.4 Economics'); s31=blk(new,H[0],H[1]); assert s31==blk(old,H[0],H[1]), 'Core 05 section 3.1 changed'; assert '| GASTAT foreign trade and open data | official domestic aggregate anchor | reconcile definitions and revisions | connector planned |' in s31.splitlines() and 'S12a' not in s31; S='; connector implemented (S12a); availability and coverage recorded per run |'; PFX=('| GASTAT economic census and industrial surveys |','| Ministry of Industry open data |','| MODON directories |','| SASO catalogue |','| SABER registry |'); o=blk(old,H[1],H[3]).splitlines(); n=blk(new,H[1],H[3]).splitlines(); assert all(l.endswith(' |') for l in o if l.startswith(PFX)); exp=[(l[:-2]+S if l.startswith(PFX) else l) for l in o]; assert n==exp, [x for x in zip(o,n) if x[0]!=x[1]]; assert sum(1 for a,b in zip(o,n) if a!=b)==5; print('CORE_05_STATUS_ROWS_OK')"
CORE_05_STATUS_ROWS_OK
EXIT 0
T10_PRE_GENERATION_LADDER_PASS
```

Additional scope/frozen/prospective-secret check (read-only, no staging):

```bash
PATH=/home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin:$PATH PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode python3 -B - <<'PY'
import json,subprocess
from pathlib import Path
from scripts.check_prohibited_files import load_tracked_files,scan_tracked_files
p=json.loads(Path('.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json').read_bytes())
changed=subprocess.check_output(['git','diff','--name-only','HEAD','-z']).decode().strip('\0').split('\0')
new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().strip('\0').split('\0')
allowed_modify={x.split(' (')[0] for x in p['files']['modify']}
assert not set(changed)-allowed_modify, set(changed)-allowed_modify
new=[x for x in new if x]
raw=tuple('data/raw/'+s+'/' for s in ['gastat','ministry_of_industry','modon','saso_catalogue','saber_registry'])
assert all(x in p['files']['create'] or x.startswith(raw) for x in new)
assert all('.env' not in Path(x).parts and not x.startswith('.autonomous-workflow/') for x in new)
assert not subprocess.check_output(['git','diff','--cached','--name-only'])
f=scan_tracked_files(load_tracked_files(Path('.'),new)); assert not f,f
extra=['src/ior_mvp/acquisition/__init__.py','src/ior_mvp/acquisition/__main__.py','src/ior_mvp/acquisition/connectors/__init__.py','config/project.yaml','docs/milestones','tests/test_offline_guard.py','tests/fixtures/acquisition','scripts/build_manifests.py','data/manifests','docs/authority/authority_hashes.json']
subprocess.run(['git','diff','--quiet','HEAD','--',*extra],check=True)
for path in ['Makefile','.github/workflows/ci.yml']: assert '--no-check-manifest' not in Path(path).read_text()
print('SCOPE_AND_PROSPECTIVE_SECRET_SCAN_PASS',len(changed),'modified',len(new),'new files; index empty; extra frozen paths unchanged')
PY
```

```text
SCOPE_AND_PROSPECTIVE_SECRET_SCAN_PASS 35 modified 32 new files; index empty; extra frozen paths unchanged
```

T10 accepted. Both bounded production reviews and the T8/T9 independent reviews have zero unresolved findings. ADR-016 exists before generation. Only the single T11 generator invocation is now authorized; [12] must pass immediately after the authority-table mirror or work stops without rerunning generation.


## T11 single manifest run and immediate identity gate

2026-09-11 UTC: invocation occurred between 22:31:18 (authorization log) and 22:31:25 (exit captured). Exact command, with existing virtualenv PATH and external bytecode environment:

```bash
PYTHONPATH=src python3 scripts/build_manifests.py
```

Exit 0; no stdout/stderr. **Exactly one invocation**, count recorded as 1. No retry, hand edit of generated JSON, restoration or evidence rewrite. Coordinator mirrored only the five changed machine authority rows into §11 using apply_patch, then immediately executed parsed canonical [12]:

```text
COMMAND [12] PYTHONPATH=src python3 -c "import json,subprocess; old=json.loads(subprocess.check_output(['git','show','HEAD:data/manifests/snapshot_manifest.json'])); new=json.load(open('data/manifests/snapshot_manifest.json')); keep=('data/raw/wits_trade/','data/raw/un_comtrade/','data/raw/baci_cepii/','data/raw/zatca_tariff/','data/snapshots/partners/','data/snapshots/public/','data/synthetic/','data/golden/'); o={f['path']:(f['sha256'],f['bytes']) for f in old['files'] if f['path'].startswith(keep)}; n={f['path']:(f['sha256'],f['bytes']) for f in new['files'] if f['path'].startswith(keep)}; assert o==n, set(o.items())^set(n.items()); paths=[f['path'] for f in new['files']]; missing=[s for s in ('gastat','ministry_of_industry','modon','saso_catalogue','saber_registry') if not any(q.startswith('data/raw/'+s+'/') for q in paths)]; assert not missing, missing; oa=json.loads(subprocess.check_output(['git','show','HEAD:docs/authority/authority_hashes.json'])); na=json.load(open('docs/authority/authority_hashes.json')); frozen=[r for r in oa['files'] if not r['path'].startswith(('config/acquisition_sources','docs/core/03_','docs/core/04_','docs/core/05_','docs/core/09_'))]; nm={r['path']:(r['sha256'],r['bytes']) for r in na['files']}; assert all(nm[r['path']]==(r['sha256'],r['bytes']) for r in frozen); print('MANIFEST_S11_ROWS_UNCHANGED')"
MANIFEST_S11_ROWS_UNCHANGED
EXIT 0
```

Separate coordinator read-only generated-delta enumeration:

```text
data/manifests/snapshot_manifest.json sha256=96a98f278a532aed1bad42707da8d2a5a682b4113e64fce6505b284c1e9c45c5 rows=73 generated_on=2026-09-11
added ['data/raw/gastat/e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d/20260911T215546Z/attempt.json', 'data/raw/gastat/e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d/20260911T215546Z/coverage.json', 'data/raw/ministry_of_industry/b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f/20260911T215956Z/attempt.json', 'data/raw/ministry_of_industry/b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f/20260911T215956Z/coverage.json', 'data/raw/modon/94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135/20260911T215956Z/attempt.json', 'data/raw/modon/94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135/20260911T215956Z/coverage.json', 'data/raw/saber_registry/e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3/20260911T220134Z/attempt.json', 'data/raw/saber_registry/e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3/20260911T220134Z/coverage.json', 'data/raw/saso_catalogue/9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49/20260911T220134Z/attempt.json', 'data/raw/saso_catalogue/9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49/20260911T220134Z/coverage.json']
removed []
changed []
docs/authority/authority_hashes.json sha256=42706ee68e8364715093ec86cb0841ab57aaf08270d61cac762cc10f62ab7ec3 rows=16 generated_on=2026-09-11
added []
removed []
changed ['docs/core/04_CANONICAL_DATA_MODEL.md', 'docs/core/05_DATA_SOURCES_AND_INGESTION.md', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md', 'config/acquisition_sources.v1.yaml', 'docs/core/03_SYSTEM_ARCHITECTURE.md']
```

Snapshot manifest has ten new attempt/coverage entries only; all 63 original rows unchanged, none removed. Authority manifest has the same 16 paths, exactly five approved changed rows and no additions/removals. Human §11 mirror changes only those five rows. T11 accepted; generation is exhausted, and T12 is authorized. No more code/config/Core/raw/manifest edits or source network are planned. Any unexpected hash/identity failure now stops for owner direction, never another generation.


## T11 independent post-generation review

`s12a_t6_boundary_map` independently recomputed every generated row's hash/size, checked exact allowed deltas and the human §11 mirror, and confirmed ADR/runbook receipts were tail-only additions to T9. It found the v0.3.0 state `last_updated` still preceded the T11 receipt; coordinator reproduced the read-only timestamp assertion failure, set that field to the actual clock `2026-09-11T22:36:11Z`, and reran the same assertion successfully. No hashed file or manifest rerun was involved. Re-review **APPROVE, zero unresolved findings**, bounded to T11. Historical top-level S05 timestamp stayed unchanged.

## T12 final full ladder — coordinator capture

Every executed command below exited 0; all 26 executable plan entries passed. [22] remains explicitly superseded by owner ruling, never executed or marked PASS. Environment: existing virtualenv first in PATH, `PYTHONPATH=src`, `PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode`, `UV_OFFLINE=1`, `UV=uv`, `NODE=node`; no live acquisition flag. Commands are exact parsed plan-5 strings after SHA verification. All six canonical commands ran against the uncommitted base HEAD. No full-suite exclusion, baseline update, manifest rerun or source request occurred. `uv sync`/`uv run` switched the existing dev/e2e extras using cached locked packages; dependency declarations/lockfile stayed unchanged.

```text
COMMAND [12] PYTHONPATH=src python3 -c "import json,subprocess; old=json.loads(subprocess.check_output(['git','show','HEAD:data/manifests/snapshot_manifest.json'])); new=json.load(open('data/manifests/snapshot_manifest.json')); keep=('data/raw/wits_trade/','data/raw/un_comtrade/','data/raw/baci_cepii/','data/raw/zatca_tariff/','data/snapshots/partners/','data/snapshots/public/','data/synthetic/','data/golden/'); o={f['path']:(f['sha256'],f['bytes']) for f in old['files'] if f['path'].startswith(keep)}; n={f['path']:(f['sha256'],f['bytes']) for f in new['files'] if f['path'].startswith(keep)}; assert o==n, set(o.items())^set(n.items()); paths=[f['path'] for f in new['files']]; missing=[s for s in ('gastat','ministry_of_industry','modon','saso_catalogue','saber_registry') if not any(q.startswith('data/raw/'+s+'/') for q in paths)]; assert not missing, missing; oa=json.loads(subprocess.check_output(['git','show','HEAD:docs/authority/authority_hashes.json'])); na=json.load(open('docs/authority/authority_hashes.json')); frozen=[r for r in oa['files'] if not r['path'].startswith(('config/acquisition_sources','docs/core/03_','docs/core/04_','docs/core/05_','docs/core/09_'))]; nm={r['path']:(r['sha256'],r['bytes']) for r in na['files']}; assert all(nm[r['path']]==(r['sha256'],r['bytes']) for r in frozen); print('MANIFEST_S11_ROWS_UNCHANGED')"
MANIFEST_S11_ROWS_UNCHANGED
EXIT 0

COMMAND [13] PYTHONPATH=src python3 scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
EXIT 0

COMMAND [14] PYTHONPATH=src python3 scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)
- SYN-MINISTRY-PP-001.json scenario=SYN-MINISTRY-PP-001 opportunity=SAU-H0-390210 status=PASS
  target_spec_demand_within_public_imports: PASS - 56 kt <= 56 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 1170 kt <= 1170 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: PASS - 80 kt <= 1055.46 kt.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_allocation_sums_to_public_hs6_total: NOT_APPLICABLE - No tariff_line_allocation block is declared.
  buyer_allocation_within_public_imports: NOT_APPLICABLE - No buyer_allocation block is declared.
  expansion_assumption_disclosed_and_bounded: NOT_APPLICABLE - No expansion_assumption block is declared.
  retained_flows_reconcile_to_public_trade: NOT_APPLICABLE - No production_and_retained_flows block is declared.
  base_demand_and_commitment_probability_valid: NOT_APPLICABLE - No base demand, commitment probability or MES block is declared.
  ground_truth_backtest: PASS - Engine state and route match planted ground truth.
- SYN-MINISTRY-STEEL-001.json scenario=SYN-MINISTRY-STEEL-001 opportunity=SAU-H0-721049 status=PASS
  target_spec_demand_within_public_imports: PASS - 104 kt <= 287.9 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 250 kt <= 250 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: NOT_APPLICABLE - No qualified_available_kt is declared.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_allocation_sums_to_public_hs6_total: NOT_APPLICABLE - No tariff_line_allocation block is declared.
  buyer_allocation_within_public_imports: NOT_APPLICABLE - No buyer_allocation block is declared.
  expansion_assumption_disclosed_and_bounded: NOT_APPLICABLE - No expansion_assumption block is declared.
  retained_flows_reconcile_to_public_trade: NOT_APPLICABLE - No production_and_retained_flows block is declared.
  base_demand_and_commitment_probability_valid: PASS - Base demand, commitment probability and MES inputs are valid.
  ground_truth_backtest: PASS - Engine state and route match planted ground truth.
EXIT 0

COMMAND [15] PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
EXIT 0

COMMAND [16] PYTHONPATH=src pytest -q
........................................................................ [  4%]
........................................................................ [  8%]
........................................................................ [ 12%]
........................................................................ [ 16%]
........................................................................ [ 20%]
........................................................................ [ 24%]
........................................................................ [ 28%]
........................................................................ [ 32%]
........................................................................ [ 36%]
........................................................................ [ 41%]
........................................................................ [ 45%]
........................................................................ [ 49%]
........................................................................ [ 53%]
........................................................................ [ 57%]
........................................................................ [ 61%]
........................................................................ [ 65%]
........................................................................ [ 69%]
........................................................................ [ 73%]
........................................................................ [ 77%]
........................................................................ [ 82%]
........................................................................ [ 86%]
........................................................................ [ 90%]
........................................................................ [ 94%]
........................................................................ [ 98%]
...........................                                              [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1755 passed, 1 warning in 15.75s
EXIT 0

COMMAND [17] PYTHONPATH=src python3 -c "import json,hashlib,subprocess; from pathlib import Path; p=Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json'); head=subprocess.check_output(['git','show','HEAD:'+p.as_posix()]); assert p.read_bytes()==head; m=json.load(open('data/manifests/snapshot_manifest.json')); row=next(r for r in m['files'] if r['path']==p.as_posix()); assert row['sha256']==hashlib.sha256(head).hexdigest() and row['bytes']==len(head); print('PARTNER_SNAPSHOT_BYTE_IDENTICAL')"
PARTNER_SNAPSHOT_BYTE_IDENTICAL
EXIT 0

COMMAND [18] PYTHONPATH=src python3 -c "import json; from pathlib import Path; from ior_mvp.acquisition.kinds import default_kind_registry; from ior_mvp.acquisition.snapshots import validate_snapshot; from ior_mvp.acquisition.passports import assert_passport_complete; kinds=default_kind_registry(); n=0; [ (validate_snapshot(json.loads(f.read_text(encoding='utf-8')), kinds=kinds), [assert_passport_complete(pp) for pp in json.loads(f.read_text(encoding='utf-8'))['evidence']]) for k,root in kinds.roots().items() for f in sorted(Path(root).glob('*.json')) ]; print('ALL_ACQUIRED_SNAPSHOTS_VALIDATE', sorted(kinds.roots()))"
ALL_ACQUIRED_SNAPSHOTS_VALIDATE ['directory', 'partners', 'production', 'registry', 'tariff', 'universe']
EXIT 0

COMMAND [8] PYTHONPATH=src python3 scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
EXIT 0

COMMAND [19] make ci
uv sync --locked --extra dev
Resolved 40 packages in 0.77ms
Uninstalled 11 packages in 19ms
 - charset-normalizer==3.5.1
 - greenlet==3.5.5
 - pillow==12.3.0
 - playwright==1.62.0
 - pyee==13.0.1
 - pytest-base-url==2.1.0
 - pytest-playwright==0.9.0
 - python-slugify==8.0.4
 - requests==2.34.2
 - text-unidecode==1.3
 - urllib3==2.7.0
uv run --locked --extra dev python scripts/check_prohibited_files.py
PROHIBITED FILE SCAN PASS (524 tracked files)
uv run --locked --extra dev python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (47 Python files; 23 configured numeric values)
uv run --locked --extra dev python scripts/check_ui_contracts.py
UI CONTRACT CHECK PASS
uv run --locked --extra dev python -m compileall -q src scripts tests browser_tests
uv run --locked --extra dev python scripts/check_es_modules.py --node "node"
ES MODULE CHECK PASS (19 files)
PYTHONPATH=src uv run --locked --extra dev python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
PYTHONPATH=src uv run --locked --extra dev python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)
- SYN-MINISTRY-PP-001.json scenario=SYN-MINISTRY-PP-001 opportunity=SAU-H0-390210 status=PASS
  target_spec_demand_within_public_imports: PASS - 56 kt <= 56 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 1170 kt <= 1170 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: PASS - 80 kt <= 1055.46 kt.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_allocation_sums_to_public_hs6_total: NOT_APPLICABLE - No tariff_line_allocation block is declared.
  buyer_allocation_within_public_imports: NOT_APPLICABLE - No buyer_allocation block is declared.
  expansion_assumption_disclosed_and_bounded: NOT_APPLICABLE - No expansion_assumption block is declared.
  retained_flows_reconcile_to_public_trade: NOT_APPLICABLE - No production_and_retained_flows block is declared.
  base_demand_and_commitment_probability_valid: NOT_APPLICABLE - No base demand, commitment probability or MES block is declared.
  ground_truth_backtest: PASS - Engine state and route match planted ground truth.
- SYN-MINISTRY-STEEL-001.json scenario=SYN-MINISTRY-STEEL-001 opportunity=SAU-H0-721049 status=PASS
  target_spec_demand_within_public_imports: PASS - 104 kt <= 287.9 kt.
  line_nameplate_within_disclosed_public_capacity: PASS - 250 kt <= 250 kt.
  capacity_factors_within_unit_interval: PASS - All declared capacity factors are within [0,1].
  qualified_availability_within_physical_output: NOT_APPLICABLE - No qualified_available_kt is declared.
  demand_layers_remain_separate: INFORMATIONAL - Demand layers are reported separately; no ordering constraint is enforced.
  tariff_line_allocation_sums_to_public_hs6_total: NOT_APPLICABLE - No tariff_line_allocation block is declared.
  buyer_allocation_within_public_imports: NOT_APPLICABLE - No buyer_allocation block is declared.
  expansion_assumption_disclosed_and_bounded: NOT_APPLICABLE - No expansion_assumption block is declared.
  retained_flows_reconcile_to_public_trade: NOT_APPLICABLE - No production_and_retained_flows block is declared.
  base_demand_and_commitment_probability_valid: PASS - Base demand, commitment probability and MES inputs are valid.
  ground_truth_backtest: PASS - Engine state and route match planted ground truth.
PYTHONPATH=src uv run --locked --extra dev python scripts/reconstruct_snapshot.py --all
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
PYTHONPATH=src uv run --locked --extra dev pytest -q
........................................................................ [  4%]
........................................................................ [  8%]
........................................................................ [ 12%]
........................................................................ [ 16%]
........................................................................ [ 20%]
........................................................................ [ 24%]
........................................................................ [ 28%]
........................................................................ [ 32%]
........................................................................ [ 36%]
........................................................................ [ 41%]
........................................................................ [ 45%]
........................................................................ [ 49%]
........................................................................ [ 53%]
........................................................................ [ 57%]
........................................................................ [ 61%]
........................................................................ [ 65%]
........................................................................ [ 69%]
........................................................................ [ 73%]
........................................................................ [ 77%]
........................................................................ [ 82%]
........................................................................ [ 86%]
........................................................................ [ 90%]
........................................................................ [ 94%]
........................................................................ [ 98%]
...........................                                              [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1755 passed, 1 warning in 15.66s
PYTHONPATH=src uv run --locked --extra dev python scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
uv run --locked --extra dev --extra e2e python scripts/check_browser_prerequisites.py
Installed 11 packages in 14ms
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
chromium=/home/barami/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome
axe_sha256=c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1
font_family=DejaVu Sans
font_file=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
product_fonts=IOR Noto Sans,IOR Noto Sans Arabic
IOR_E2E_EXPLICIT=1 IOR_E2E_ARTIFACT_DIR=".artifacts/e2e" PYTHONPATH=src uv run --locked --extra dev --extra e2e pytest -q browser_tests --browser chromium --tracing retain-on-failure --screenshot only-on-failure --output=".artifacts/e2e/playwright" -m "e2e and not visual"
........................................................................ [ 61%]
..............................................                           [100%]
118 passed, 4 deselected in 131.49s (0:02:11)
IOR_E2E_EXPLICIT=1 IOR_E2E_ARTIFACT_DIR=".artifacts/e2e" PYTHONPATH=src uv run --locked --extra dev --extra e2e pytest -q browser_tests --browser chromium --tracing retain-on-failure --screenshot only-on-failure --output=".artifacts/e2e/playwright" -m visual
....                                                                     [100%]
4 passed, 118 deselected in 25.75s
EXIT 0

COMMAND [0] test "$(git branch --show-current)" = slice/s12a-acquisition-framework-institutional-sources && git merge-base --is-ancestor a043ed8dc1d477de50149b39de657bc963e785d7 HEAD
EXIT 0

COMMAND [1] PYTHONPATH=src pytest -q tests/test_acquisition_kind_registry.py tests/test_acquisition_stage_specs.py tests/test_acquisition_normalization_status.py
.........................................................                [100%]
57 passed in 0.15s
EXIT 0

COMMAND [2] PYTHONPATH=src pytest -q tests/test_acquisition_institutional_connectors.py tests/test_acquisition_institutional_snapshots.py tests/test_acquisition_config.py tests/test_acquisition_connectors.py tests/test_acquisition_cli.py tests/test_acquisition_contracts.py tests/test_acquisition_reconstruction.py tests/test_acquisition_snapshots.py tests/test_acquisition_stored_artifacts.py
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 27%]
........................................................................ [ 36%]
........................................................................ [ 45%]
........................................................................ [ 55%]
........................................................................ [ 64%]
........................................................................ [ 73%]
........................................................................ [ 82%]
........................................................................ [ 91%]
...............................................................          [100%]
783 passed in 11.07s
EXIT 0

COMMAND [3] PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
RECONSTRUCTION PASS (1 snapshots, 4 artifacts)
EXIT 0

COMMAND [4] git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
EXIT 0

COMMAND [5] git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
EXIT 0

COMMAND [6] git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
EXIT 0

COMMAND [7] PYTHONPATH=src pytest -q tests/test_golden_cases.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_offline_guard.py
..........................................                               [100%]
42 passed in 1.13s
EXIT 0

COMMAND [9] PYTHONPATH=src python3 -c "import json,yaml,sys; from pathlib import Path; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; ids=set(cfg['sources']); assert ids=={'wits_trade','un_comtrade','baci_cepii','zatca_tariff','gastat','ministry_of_industry','modon','saso_catalogue','saber_registry'}, ids; cls={'gastat':'B','ministry_of_industry':'B','modon':'C','saso_catalogue':'B','saber_registry':'C'}; assert all(cfg['sources'][s]['default_evidence_class']==c for s,c in cls.items()); assert all((Path('data/raw')/s).is_dir() and (any((Path('data/raw')/s).rglob('page-*.contract.json')) or any((Path('data/raw')/s).rglob('attempt.json'))) for s in cls), 'raw record missing'; print('CONFIG_AND_RAW_RECORDS_OK')"
CONFIG_AND_RAW_RECORDS_OK
EXIT 0

COMMAND [10] PYTHONPATH=src python3 -c "import ast,sys; from pathlib import Path; bad=[]; [bad.append((str(p),n.lineno)) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,ast.ExceptHandler) and n.type is None]; miss=[(str(p),f.name) for p in Path('src/ior_mvp/acquisition').rglob('*.py') for f in ast.parse(p.read_text(encoding='utf-8')).body if isinstance(f,ast.FunctionDef) and not f.name.startswith('_') and (f.returns is None or any(a.annotation is None for a in f.args.args if a.arg not in ('self','cls')))]; assert not bad, bad; assert not miss, miss; print('PYTHON_STANDARDS_OK')"
PYTHON_STANDARDS_OK
EXIT 0

COMMAND [11] python3 scripts/check_prohibited_files.py && python3 scripts/check_threshold_literals.py && python3 -m compileall -q src scripts tests
PROHIBITED FILE SCAN PASS (524 tracked files)
THRESHOLD LITERAL SCAN PASS (47 Python files; 23 configured numeric values)
EXIT 0

COMMAND [20] PYTHONPATH=src python3 -c "import json,yaml,subprocess; from pathlib import Path; from ior_mvp.acquisition.kinds import default_kind_registry; from ior_mvp.acquisition.harmonise import PIPELINE_VERSION; k=default_kind_registry(); assert PIPELINE_VERSION=='1.0.0'; assert {x:k.get(x).config_version for x in k.ids()}=={'universe':'1.0.0','tariff':'1.0.0','partners':'1.0.0','production':'1.1.0','directory':'1.1.0','registry':'1.1.0'}; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; head=yaml.safe_load(subprocess.check_output(['git','show','HEAD:config/acquisition_sources.v1.yaml'])); assert all(cfg['sources'][s]==head['sources'][s] for s in ('wits_trade','un_comtrade','baci_cepii','zatca_tariff')); snap=json.loads(Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json').read_text(encoding='utf-8')); assert snap['transformation_record']['config_version']=='1.0.0' and snap['transformation_record']['pipeline_version']=='1.0.0' and all(e['transformation_record']['config_version']=='1.0.0' for e in snap['evidence']); print('CONFIG_VERSION_PROVENANCE_OK')"
CONFIG_VERSION_PROVENANCE_OK
EXIT 0

COMMAND [21] PYTHONPATH=src pytest -q tests/test_acquisition_config.py -k "pre_observation or observed_values or recorded_on or unavailable_access or s11_mappings or unknown_source_key or forbidden_keys or live_yaml or sentinel or configured_credential"
........................................................................ [ 31%]
........................................................................ [ 63%]
........................................................................ [ 95%]
...........                                                              [100%]
227 passed, 10 deselected in 1.38s
EXIT 0

COMMAND [22] SUPERSEDED_BY_OWNER_RULING: .autonomous-workflow/owner-decisions/20260911-owner-direct-s12a-implementation.md — no plugin-classifier command is executed or claimed PASS; substantive no-destructive-Git policy remains.
SUPERSEDED_BY_OWNER_RULING; NOT EXECUTED; NOT PASS

COMMAND [23] PYTHONPATH=src python3 -c "import subprocess; rows=[l.split('\t') for l in subprocess.check_output(['git','diff','--numstat','HEAD','--','docs/core/03_SYSTEM_ARCHITECTURE.md','docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md'],text=True).splitlines() if l.strip()]; assert all(r[1]=='0' for r in rows), rows; assert all(int(r[0])<=3 for r in rows), rows; print('CORE_03_09_INSERTION_ONLY_OK', rows)"
CORE_03_09_INSERTION_ONLY_OK [['2', '0', 'docs/core/03_SYSTEM_ARCHITECTURE.md'], ['2', '0', 'docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md']]
EXIT 0

COMMAND [24] PYTHONPATH=src python3 -c "from ior_mvp.acquisition.contracts import UNAVAILABLE; from ior_mvp.acquisition.source_config import CREDENTIAL_PATTERN, INSTITUTIONAL_SOURCE_IDS, acquisition_sources_config, configured_credential_env_var, observation_state, observed_fact_values; assert configured_credential_env_var({'credential_env_var': UNAVAILABLE}) is None and configured_credential_env_var({'credential_env_var': None}) is None and configured_credential_env_var({'credential_env_var': ''}) is None and configured_credential_env_var({'credential_env_var': 'IOR_X'}) == 'IOR_X'; src=acquisition_sources_config()['sources']; pins={'wits_trade': None, 'baci_cepii': None, 'zatca_tariff': None, 'un_comtrade': 'IOR_COMTRADE_SUBSCRIPTION_KEY'}; assert {s: src[s]['credential_env_var'] for s in pins} == pins, 'S11 credential pins changed'; assert set(INSTITUTIONAL_SOURCE_IDS) == {'gastat', 'ministry_of_industry', 'modon', 'saso_catalogue', 'saber_registry'}; bad=[(s, k, v) for s in sorted(INSTITUTIONAL_SOURCE_IDS) if src[s]['recorded_on'] == UNAVAILABLE for k, v in observed_fact_values(s, src[s]).items() if v != UNAVAILABLE]; assert not bad, bad; assert all(len(observed_fact_values(s, src[s])) == 17 for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == ('PRE_OBSERVATION' if all(v == UNAVAILABLE for v in observed_fact_values(s, src[s]).values()) else 'OBSERVED') for s in INSTITUTIONAL_SOURCE_IDS); assert all(observation_state(s, src[s]) == 'PRE_OBSERVATION' for s in INSTITUTIONAL_SOURCE_IDS if src[s]['recorded_on'] == UNAVAILABLE); assert all(src[s]['credential_env_var'] is None or src[s]['credential_env_var'] == UNAVAILABLE or (isinstance(src[s]['credential_env_var'], str) and CREDENTIAL_PATTERN.fullmatch(src[s]['credential_env_var']) is not None) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['parameters']['flow_tokens'] == UNAVAILABLE or isinstance(src[s]['parameters']['flow_tokens'], dict) for s in INSTITUTIONAL_SOURCE_IDS); assert all(src[s]['pagination']['parameters'] == UNAVAILABLE or isinstance(src[s]['pagination']['parameters'], dict) for s in INSTITUTIONAL_SOURCE_IDS); print('SINGLE_SENTINEL_REPRESENTATION_OK')"
SINGLE_SENTINEL_REPRESENTATION_OK
EXIT 0

COMMAND [25] PYTHONPATH=src pytest -q tests/test_acquisition_institutional_connectors.py -k "pre_observation or sentinel or credential or license_unrecorded"
..........................                                               [100%]
26 passed, 325 deselected in 0.10s
EXIT 0

COMMAND [26] PYTHONPATH=src python3 -c "import subprocess; from pathlib import Path; P='docs/core/05_DATA_SOURCES_AND_INGESTION.md'; new=Path(P).read_text(encoding='utf-8'); old=subprocess.check_output(['git','show','HEAD:'+P],text=True); blk=lambda t,a,b: t.split(a,1)[1].split(b,1)[0]; H=('### 3.1 Trade and demand','### 3.2 Supply and capability','### 3.3 Specifications and qualification','### 3.4 Economics'); s31=blk(new,H[0],H[1]); assert s31==blk(old,H[0],H[1]), 'Core 05 section 3.1 changed'; assert '| GASTAT foreign trade and open data | official domestic aggregate anchor | reconcile definitions and revisions | connector planned |' in s31.splitlines() and 'S12a' not in s31; S='; connector implemented (S12a); availability and coverage recorded per run |'; PFX=('| GASTAT economic census and industrial surveys |','| Ministry of Industry open data |','| MODON directories |','| SASO catalogue |','| SABER registry |'); o=blk(old,H[1],H[3]).splitlines(); n=blk(new,H[1],H[3]).splitlines(); assert all(l.endswith(' |') for l in o if l.startswith(PFX)); exp=[(l[:-2]+S if l.startswith(PFX) else l) for l in o]; assert n==exp, [x for x in zip(o,n) if x[0]!=x[1]]; assert sum(1 for a,b in zip(o,n) if a!=b)==5; print('CORE_05_STATUS_ROWS_OK')"
CORE_05_STATUS_ROWS_OK
EXIT 0
T12_ALL_26_EXECUTABLE_GATES_PASS; [22] SUPERSEDED
```

Final ladder results: unexcluded pytest **1755 passed / 1 existing warning in 15.75s**; inside `make ci`, **1755 passed / 1 warning in 15.66s**, then **118 functional passed in 131.49s** and **4 visual passed in 25.75s**. Both browser groups together cover all 122 nodes; their marker deselections are complementary, not omitted nodes. Integrity PASS; scenario validation PASS (2 scenarios); default-manifest reconstruction PASS (1 snapshot / 4 artifacts); smoke/frozen decisions exact. Four standard static checks (prohibited-file, threshold literals, UI contracts, ES modules) and compileall pass. Additional exact 18 policy-test names were programmatically confirmed present. No database/models/migrations or new dependency/service was introduced; filesystem persistence/cache/isolation/tamper integration tests run in the full and focused suites. DB drift and migration upgrade/downgrade checks are not applicable. Hosted multi-job CI remains pending a later authorized PR, not implied by local `make ci`.

T12 gates completed by the actual clock `2026-09-11 22:37:36 UTC`; HEAD remains `a043ed8dc1d477de50149b39de657bc963e785d7`, branch unchanged and index empty. The remaining work is evidence/diff handoff and session implementation review, not a commit or S12b.


## Final record-candidate verification and self-audit

After the final non-hashed control-record updates, coordinator reran unrestricted pytest, integrity and all four standard static checks. Same virtualenv/PYTHONPATH/external-cache environment:

```text
FINAL COMMAND PYTHONPATH=src pytest -q
........................................................................ [  4%]
........................................................................ [  8%]
........................................................................ [ 12%]
........................................................................ [ 16%]
........................................................................ [ 20%]
........................................................................ [ 24%]
........................................................................ [ 28%]
........................................................................ [ 32%]
........................................................................ [ 36%]
........................................................................ [ 41%]
........................................................................ [ 45%]
........................................................................ [ 49%]
........................................................................ [ 53%]
........................................................................ [ 57%]
........................................................................ [ 61%]
........................................................................ [ 65%]
........................................................................ [ 69%]
........................................................................ [ 73%]
........................................................................ [ 77%]
........................................................................ [ 82%]
........................................................................ [ 86%]
........................................................................ [ 90%]
........................................................................ [ 94%]
........................................................................ [ 98%]
...........................                                              [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1755 passed, 1 warning in 15.83s
EXIT 0

FINAL COMMAND PYTHONPATH=src python3 scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
EXIT 0

FINAL COMMAND python3 scripts/check_prohibited_files.py
PROHIBITED FILE SCAN PASS (524 tracked files)
EXIT 0

FINAL COMMAND python3 scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (47 Python files; 23 configured numeric values)
EXIT 0

FINAL COMMAND python3 scripts/check_ui_contracts.py
UI CONTRACT CHECK PASS
EXIT 0

FINAL COMMAND python3 scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (19 files)
EXIT 0

FINAL COMMAND git diff --check
EXIT 0

FINAL COMMAND git diff --cached --quiet
EXIT 0
FINAL_RECORD_CANDIDATE_REGRESSION_PASS
```

Final scope/secret/pin/frozen check, including the prospective untracked files without staging and exact six canonical-command byte comparison:

```bash
PATH=/home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin:$PATH PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/ior-s12a-cache-recovery-6KM89p/new-bytecode python3 -B - <<'PY'
import json,hashlib,subprocess
from pathlib import Path
from scripts.check_prohibited_files import load_tracked_files,scan_tracked_files
plan_path=Path('.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json');b=plan_path.read_bytes();assert hashlib.sha256(b).hexdigest()=='b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64';p=json.loads(b)
b4=plan_path.with_name('plan-4.json').read_bytes();assert hashlib.sha256(b4).hexdigest()=='fb9b3d290c079809639e97f1604f7200b5f7f8622be5fcb583ce741bed88e376';p4=json.loads(b4)
cp=json.loads(Path('.autonomous-workflow/checkpoint.json').read_bytes());assert cp['approved_plan']['sha256']==hashlib.sha256(b).hexdigest();assert cp['manifest_runs_this_slice']==1;assert cp['current_engineering_step']=='T12_COMPLETE_AWAITING_SESSION_IMPLEMENTATION_REVIEW'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='a043ed8dc1d477de50149b39de657bc963e785d7'
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='slice/s12a-acquisition-framework-institutional-sources'
changed=[x for x in subprocess.check_output(['git','diff','--name-only','HEAD','-z']).decode().split('\0') if x]
new=[x for x in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0') if x]
allowed={x.split(' (')[0] for x in p['files']['modify']}|set(p['files']['generated_once']);assert set(changed)<=allowed,set(changed)-allowed
raw=tuple('data/raw/'+s+'/' for s in ['gastat','ministry_of_industry','modon','saso_catalogue','saber_registry'])
assert all(x in p['files']['create'] or x.startswith(raw) for x in new)
assert all('.env' not in Path(x).parts and not x.startswith('.autonomous-workflow/') for x in changed+new)
assert not subprocess.check_output(['git','diff','--cached','--name-only'])
assert not subprocess.check_output(['git','ls-files','--','.env','.autonomous-workflow'])
subprocess.run(['git','check-ignore','--quiet','.env'],check=True);subprocess.run(['git','check-ignore','--quiet','.autonomous-workflow/checkpoint.json'],check=True)
assert not scan_tracked_files(load_tracked_files(Path('.'),new))
print('FINAL_SCOPE_SECRET_AND_PINS_PASS',len(changed),'modified',len(new),'new files; index empty; local-only files ignored',flush=True)
extra=['src/ior_mvp/acquisition/__init__.py','src/ior_mvp/acquisition/__main__.py','src/ior_mvp/acquisition/connectors/__init__.py','config/project.yaml','docs/milestones','tests/test_offline_guard.py','tests/fixtures/acquisition','scripts/build_manifests.py']
subprocess.run(['git','diff','--quiet','HEAD','--',*extra],check=True)
for f,h in [('data/manifests/snapshot_manifest.json','96a98f278a532aed1bad42707da8d2a5a682b4113e64fce6505b284c1e9c45c5'),('docs/authority/authority_hashes.json','42706ee68e8364715093ec86cb0841ab57aaf08270d61cac762cc10f62ab7ec3')]: assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
for i in [4,5,6,12,17,20,26]:
 if i!=6: assert p['verification'][i].encode()==p4['verification'][i].encode()
 cmd=p['verification'][i]; print('\nFINAL CANONICAL ['+str(i)+'] '+cmd,flush=True)
 r=subprocess.run(cmd,shell=True,executable='/bin/bash');print('EXIT',r.returncode,flush=True);assert r.returncode==0
print('FINAL_FROZEN_CANONICAL_AND_SINGLE_GENERATION_IDENTITY_PASS',flush=True)
PY
```

```text
FINAL_SCOPE_SECRET_AND_PINS_PASS 38 modified 32 new files; index empty; local-only files ignored

FINAL CANONICAL [4] git diff --quiet HEAD -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners && test -z "$(git ls-files --others -- data/raw/wits_trade data/raw/un_comtrade data/raw/baci_cepii data/raw/zatca_tariff data/snapshots/partners)"
EXIT 0

FINAL CANONICAL [5] git diff --quiet HEAD -- data/snapshots/public data/synthetic data/golden browser_tests && test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)"
EXIT 0

FINAL CANONICAL [6] git diff --quiet HEAD -- ':(glob)src/ior_mvp/*.py' src/ior_mvp/acquisition/transport.py src/ior_mvp/acquisition/raw_store.py src/ior_mvp/acquisition/connectors/baci_cepii.py .github/workflows/ci.yml pyproject.toml uv.lock Dockerfile tests/conftest.py tests/test_frozen_public_evidence_pins.py tests/test_ci_contract.py tests/test_golden_cases.py config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml docs/core/01_PRODUCT_AND_REQUIREMENTS.md docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md docs/core/07_DETERMINISTIC_ENGINE_SPEC.md docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
EXIT 0

FINAL CANONICAL [12] PYTHONPATH=src python3 -c "import json,subprocess; old=json.loads(subprocess.check_output(['git','show','HEAD:data/manifests/snapshot_manifest.json'])); new=json.load(open('data/manifests/snapshot_manifest.json')); keep=('data/raw/wits_trade/','data/raw/un_comtrade/','data/raw/baci_cepii/','data/raw/zatca_tariff/','data/snapshots/partners/','data/snapshots/public/','data/synthetic/','data/golden/'); o={f['path']:(f['sha256'],f['bytes']) for f in old['files'] if f['path'].startswith(keep)}; n={f['path']:(f['sha256'],f['bytes']) for f in new['files'] if f['path'].startswith(keep)}; assert o==n, set(o.items())^set(n.items()); paths=[f['path'] for f in new['files']]; missing=[s for s in ('gastat','ministry_of_industry','modon','saso_catalogue','saber_registry') if not any(q.startswith('data/raw/'+s+'/') for q in paths)]; assert not missing, missing; oa=json.loads(subprocess.check_output(['git','show','HEAD:docs/authority/authority_hashes.json'])); na=json.load(open('docs/authority/authority_hashes.json')); frozen=[r for r in oa['files'] if not r['path'].startswith(('config/acquisition_sources','docs/core/03_','docs/core/04_','docs/core/05_','docs/core/09_'))]; nm={r['path']:(r['sha256'],r['bytes']) for r in na['files']}; assert all(nm[r['path']]==(r['sha256'],r['bytes']) for r in frozen); print('MANIFEST_S11_ROWS_UNCHANGED')"
MANIFEST_S11_ROWS_UNCHANGED
EXIT 0

FINAL CANONICAL [17] PYTHONPATH=src python3 -c "import json,hashlib,subprocess; from pathlib import Path; p=Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json'); head=subprocess.check_output(['git','show','HEAD:'+p.as_posix()]); assert p.read_bytes()==head; m=json.load(open('data/manifests/snapshot_manifest.json')); row=next(r for r in m['files'] if r['path']==p.as_posix()); assert row['sha256']==hashlib.sha256(head).hexdigest() and row['bytes']==len(head); print('PARTNER_SNAPSHOT_BYTE_IDENTICAL')"
PARTNER_SNAPSHOT_BYTE_IDENTICAL
EXIT 0

FINAL CANONICAL [20] PYTHONPATH=src python3 -c "import json,yaml,subprocess; from pathlib import Path; from ior_mvp.acquisition.kinds import default_kind_registry; from ior_mvp.acquisition.harmonise import PIPELINE_VERSION; k=default_kind_registry(); assert PIPELINE_VERSION=='1.0.0'; assert {x:k.get(x).config_version for x in k.ids()}=={'universe':'1.0.0','tariff':'1.0.0','partners':'1.0.0','production':'1.1.0','directory':'1.1.0','registry':'1.1.0'}; cfg=yaml.safe_load(Path('config/acquisition_sources.v1.yaml').read_text(encoding='utf-8')); assert cfg['metadata']['version']=='1.1.0'; head=yaml.safe_load(subprocess.check_output(['git','show','HEAD:config/acquisition_sources.v1.yaml'])); assert all(cfg['sources'][s]==head['sources'][s] for s in ('wits_trade','un_comtrade','baci_cepii','zatca_tariff')); snap=json.loads(Path('data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json').read_text(encoding='utf-8')); assert snap['transformation_record']['config_version']=='1.0.0' and snap['transformation_record']['pipeline_version']=='1.0.0' and all(e['transformation_record']['config_version']=='1.0.0' for e in snap['evidence']); print('CONFIG_VERSION_PROVENANCE_OK')"
CONFIG_VERSION_PROVENANCE_OK
EXIT 0

FINAL CANONICAL [26] PYTHONPATH=src python3 -c "import subprocess; from pathlib import Path; P='docs/core/05_DATA_SOURCES_AND_INGESTION.md'; new=Path(P).read_text(encoding='utf-8'); old=subprocess.check_output(['git','show','HEAD:'+P],text=True); blk=lambda t,a,b: t.split(a,1)[1].split(b,1)[0]; H=('### 3.1 Trade and demand','### 3.2 Supply and capability','### 3.3 Specifications and qualification','### 3.4 Economics'); s31=blk(new,H[0],H[1]); assert s31==blk(old,H[0],H[1]), 'Core 05 section 3.1 changed'; assert '| GASTAT foreign trade and open data | official domestic aggregate anchor | reconcile definitions and revisions | connector planned |' in s31.splitlines() and 'S12a' not in s31; S='; connector implemented (S12a); availability and coverage recorded per run |'; PFX=('| GASTAT economic census and industrial surveys |','| Ministry of Industry open data |','| MODON directories |','| SASO catalogue |','| SABER registry |'); o=blk(old,H[1],H[3]).splitlines(); n=blk(new,H[1],H[3]).splitlines(); assert all(l.endswith(' |') for l in o if l.startswith(PFX)); exp=[(l[:-2]+S if l.startswith(PFX) else l) for l in o]; assert n==exp, [x for x in zip(o,n) if x[0]!=x[1]]; assert sum(1 for a,b in zip(o,n) if a!=b)==5; print('CORE_05_STATUS_ROWS_OK')"
CORE_05_STATUS_ROWS_OK
EXIT 0
FINAL_FROZEN_CANONICAL_AND_SINGLE_GENERATION_IDENTITY_PASS
```

Independent `s12a_t5_boundary_map` final handoff-record consistency review: **APPROVE, zero findings**. It confirms the actual counts/timings, one generation, accurate timestamps, BLOCKED live-data versus TESTED double proofs, null PR/merge and review hold. This is not the session reviewer's implementation approval. No edits followed that record review except these evidence/identity handoff entries.

Muhasabah self-audit **PASS**: claims are sourced to the immutable plan/owner ruling, raw attempts, actual command outputs and independent reviews; unknown source contracts remain unknown, no availability/compliance/capacity claim is inferred from doubles. Scope is S12a only, with the approved unavailable terminal outcomes and explicit privacy narrowing; no additional services, migrations, dependencies, source parsers, engine/UI changes or unrelated repairs. Engineering gates are green and no hash refresh was used to hide drift. Git remains uncommitted and unstaged, protected bytes unchanged, .env never read and local-only files ignored. Remaining session review/hosted CI/PR/merge are expressly pending. Read-first, TDD, provenance, strict-review and branch-handoff skills were adapted to the existing project records and owner instructions; no parallel orchestration was introduced.
