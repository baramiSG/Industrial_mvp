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

Open `http://127.0.0.1:8000`. OpenAPI is at `http://127.0.0.1:8000/docs`.

## Preserved clean pip path

```bash
cd /home/barami/projects/industrial-opportunity-resolution-mvp
python3 -m venv --clear .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
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

`make ci` runs locked sync, prohibited and credential-pattern scan, recursive threshold-literal scan, Python compile, JavaScript syntax, integrity, Gate B scenario validation/back-test, pytest, and smoke. `final_acceptance.sh` additionally proves the clean pip path, container runtime, live journeys, performance, failures, restart, reversal, documents, archive, and repository keyword dispositions.

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

Do not weaken a test, change a golden result, or regenerate hashes to clear a failure.

## Logs and evidence

Application logs are emitted to the uvicorn terminal unless redirected by the operator. Raw acceptance logs, temporary environments, and archives stay under ignored `.workflow/logs/s05-final-acceptance/`. Sanitized results are in `.workflow/slices/S05-final-acceptance/acceptance_results.md`.

Never paste environment values, tokens, credentials, private datasets, or unrestricted logs into an issue or model.

## Escalation

Stop and request authority if a config/data/core/methodology change is needed, a public golden outcome changes, synthetic evidence appears official, an unresolved hard gate would permit real `ADVANCE`, or a required production control is missing. The application calculates and recommends; accountable officials authorize action.
