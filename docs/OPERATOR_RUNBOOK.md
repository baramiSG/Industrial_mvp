# Operator Runbook — Industrial Opportunity Resolution MVP 0.2.0

## Operating boundary

This is an offline controlled demonstration using frozen public evidence and explicit Class-D synthetic scenarios. It contains no Ministry data, user accounts, write endpoint, or public-support authorization. Bind to localhost unless an approved reverse proxy and network controls are in place.

## Prerequisites

- WSL or native Linux;
- Python 3.11 or newer;
- `uv` for the primary path;
- Node for JavaScript syntax validation;
- Git and Make;
- Docker only for the container path.

## Primary uv start

```bash
cd /home/barami/projects/industrial-opportunity-resolution-mvp
make uv-sync
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/?locale=en` or
`http://127.0.0.1:8000/?locale=ar`. The visible topbar language control
switches the complete interface chrome and persists only `ior.locale`.
OpenAPI remains an engineer-only route at `http://127.0.0.1:8000/docs`; the
offline Ministry interface does not link to it.

## Preserved clean pip path

```bash
cd /home/barami/projects/industrial-opportunity-resolution-mvp
python3 -m venv --clear .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python scripts/check_ui_contracts.py
python -m compileall -q src scripts tests
python scripts/check_es_modules.py --node node
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src python scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
PYTHONPATH=src uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000
```

`START_DEMO_WSL.sh` remains the interactive convenience path. The commands above are its noninteractive acceptance equivalent with all current gates.

## Health check

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
```

A healthy release reports JSON `status: "ok"`, `version: "0.2.0"`, and the `public real decision / isolated synthetic simulation` evidence boundary.

## Stop and restart

For a foreground process, press Ctrl+C once and wait for uvicorn shutdown.

For a managed process:

```bash
kill -TERM "$IOR_PID"
wait "$IOR_PID"
```

Restart with the same start command and repeat the health check. Restart is required after any approved on-disk config/data correction because successful reads are process-local cached (KL-29).

## Docker operation

Build and start:

```bash
docker build --file Dockerfile \
  --tag industrial-opportunity-resolution-mvp:0.2.0 .
docker run -d --name ior-mvp \
  -p 127.0.0.1:8000:8000 \
  industrial-opportunity-resolution-mvp:0.2.0
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
```

Logs, restart, and stop/remove:

```bash
docker logs ior-mvp
docker restart ior-mvp
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
docker stop ior-mvp
docker rm ior-mvp
```

The repository `docker compose up --build` path also remains supported on port 8000.

## Evidence modes

- `public`: only frozen attributable public rows contribute to `real_decision`.
- `simulated`: the public result stays visible and unchanged; Class-D scenario rows affect only `simulation_decision` and the active demonstration surface.

Never describe a simulated value as observed, official, Ministry-provided, or Class A/B/C.
Every simulated surface shows both policy labels:
`SIMULATED — NOT MINISTRY EVIDENCE` and
`محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة`.

## Interface locale

- `?locale=en` sets `lang=en` and `dir=ltr`.
- `?locale=ar` sets `lang=ar` and `dir=rtl`.
- A valid URL locale overrides the stored choice; otherwise the stored
  `ior.locale` value is used, then English.
- To reset the choice, remove only `ior.locale` from browser local storage or
  navigate explicitly to `?locale=en`.
- Western digits and Gregorian dates are intentional presentation defaults in
  both locales. Original evidence spans remain unchanged.
- English analytical narrative in Arabic UI is a visibly captioned,
  directionally isolated source-language island; it is not presented as an
  Arabic translation.

## Real-browser acceptance

Prepare the separate pinned browser environment:

```bash
uv sync --locked --extra dev --extra e2e --python "3.12"
uv run --locked --extra dev --extra e2e \
  python -m playwright install chromium
make e2e
```

On an authorized Linux host, use Playwright's
`python -m playwright install --with-deps chromium` form to install operating
system dependencies. Do not use that form where `sudo` is unavailable or
unauthorized. Hosted CI performs the authorized dependency install. The
product uses exact local Noto Sans and Noto Sans Arabic bytes; `fc-match` is
diagnostic only.

The command owns a kernel-assigned localhost socket, waits for the exact
health contract, runs 118 functional and four visual Chromium nodes, and sends SIGTERM to its uvicorn
child. An explicit gate never skips missing prerequisites. Diagnostics,
failure screenshots/traces, PDFs, axe output, and ordinary references stay
under ignored `.artifacts/e2e/`.

The tracked S06 reference set remains documentary evidence only. The governed
v0.3.0 oracle contains 40 lossless WebPs covering ten states, two locales, and
the 1440×900 and 1024×768 viewports. Normal `make e2e` only compares.
Baseline updates require an explicit reviewed change reference and the
canonical container procedure documented in `docs/DEVELOPMENT_GUIDE.md`;
operators never update baselines to clear an unexplained failure.

## Demonstration sequence

Follow `docs/implementation/MINISTRY_DEMO_SCRIPT.md`:

1. executive overview;
2. public steel `INVESTIGATE`;
3. steel simulated `ADVANCE` with unchanged real state;
4. PP public/simulated `REJECT`;
5. Decision Dossier.

## Required gates

```bash
make ci
bash scripts/final_acceptance.sh
```

`make ci` runs locked sync, prohibited and credential-pattern scan, recursive threshold-literal scan, UI contracts, Python compile (including `browser_tests`), recursive ES-module syntax, integrity, Gate B scenario validation/back-test, pytest, smoke, browser preflight, and all 122 real-Chromium nodes. `final_acceptance.sh` additionally proves the clean pip path, container runtime, live HTTP journeys, performance, failures, restart, reversal, documents, archive, and repository keyword dispositions.

Do not run the manifest generator unless an approved authority change identifies the exact governed bytes and passes Authority Manifest §7.

## Failure interpretation

- HTTP 404: unknown opportunity or unavailable scenario for a requested simulated list/detail.
- HTTP 422 invalid mode: FastAPI rejected the query contract.
- HTTP 422 `EVIDENCE_INTEGRITY_ERROR`: scenario policy, reconciliation, contract, or ground-truth validation failed closed; no partial analysis is valid.
- Integrity failure: a governed file is missing or changed; establish authorization before regeneration.
- Gate B failure: a packaged scenario is invalid, unreconciled, or disagrees with planted state/route.
- Threshold scan failure: a configured decision threshold appears as a comparison literal in source.
- Prohibited scan failure: a tracked path or configured credential pattern violates policy.
- NFR-005 failure: preserve samples and endpoint and reproduce before optimization.
- Docker/health failure: inspect container logs, port occupancy, image build, and process exit.
- Browser preflight failure: install the exact e2e pins and matching Chromium,
  verify the vendored axe SHA-256/licence, and check `fc-match :lang=ar`.
- Browser launch shared-library failure: use an authorized supported Linux
  environment with Playwright's documented system dependencies.
- Browser journey failure: inspect `.artifacts/e2e/` for collector records,
  retained traces/screenshots, axe details, PDF output, and server logs. Never
  add an external-origin exception, axe exclusion, retry, or fixed wait.
- Visual mismatch: inspect the normalized actual, amplified diff, and metrics
  under `.artifacts/e2e/visual-diffs/`; do not loosen the global tolerance,
  mask a region, or update from CI.

Do not weaken a test, change a golden result, or regenerate hashes to clear a failure.

## Logs and evidence

Application logs are emitted to the uvicorn terminal unless redirected by the operator. Raw acceptance logs, temporary environments, and archives stay under ignored `.workflow/logs/s05-final-acceptance/`. Sanitized results are in `.workflow/slices/S05-final-acceptance/acceptance_results.md`.

Never paste environment values, tokens, credentials, private datasets, or unrestricted logs into an issue or model.

## Escalation

Stop and request authority if a config/data/core/methodology change is needed, a public golden outcome changes, synthetic evidence appears official, an unresolved hard gate would permit real `ADVANCE`, or a required production control is missing. The application calculates and recommends; accountable officials authorize action.
