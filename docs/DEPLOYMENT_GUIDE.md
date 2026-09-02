# Deployment Guide — Industrial Opportunity Resolution MVP 0.2.0

## Supported deployment scope

The supported MVP targets are WSL, native Linux, and Docker. The package is an offline controlled demonstration, not a production authorization system. It uses local immutable JSON/YAML/DOCX/Markdown assets and has no database, migration, queue, cloud service, external API dependency, authentication, or write endpoint.

## Release identity

- Python package/API release: `0.2.0`;
- annotated source tag after acceptance: `v0.2.0`;
- demo project contract: `config/project.yaml` version `0.2.0`;
- threshold configuration: `1.1.0`;
- evidence policy: `1.1.0`;
- sector profiles: `1.0.0`;
- packaged synthetic scenario contract: `1.1.0`.

These are separate versioned artifacts. S05 moves only the package/API and unhashed project-contract identity together and regenerates only the editable root package version in `uv.lock`. No hashed governed configuration changes.

## WSL

```bash
wsl -d Ubuntu
cd /home/barami/projects/industrial-opportunity-resolution-mvp
make uv-sync
make ci
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000
```

If `uv` or Node is installed elsewhere:

```bash
make UV=uv NODE=node ci
```

## Native Linux

From a clone of the accepted release:

```bash
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

## Docker

```bash
docker build --file Dockerfile \
  --tag industrial-opportunity-resolution-mvp:0.2.0 .
docker run -d --name ior-mvp \
  -p 127.0.0.1:8000:8000 \
  industrial-opportunity-resolution-mvp:0.2.0
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
```

Stop with:

```bash
docker stop ior-mvp
docker rm ior-mvp
```

Docker Compose:

```bash
docker compose up --build
docker compose down
```

The compose file publishes port 8000 on the host. Use it only on an approved local or controlled network.

## Ports and runtime environment

- default local/API port: 8000;
- final-acceptance container port: host 8001 to container 8000;
- final-acceptance uvicorn port: 8010;
- `IOR_HOST`: CLI/run-script host, default `127.0.0.1`;
- `IOR_PORT`: CLI/run-script port, default `8000`;
- `PYTHONUNBUFFERED`: optional container log behavior.

There is no `IOR_DATA_DIR` runtime override. Do not invent one to alter hashed inputs.

## Security posture

For the first demonstration, bind to `127.0.0.1`. If a shared host is unavoidable, place the container behind an approved reverse proxy, restrict source networks, and terminate TLS. Do not expose the application directly to the public Internet.

No confidential Ministry data belongs in this package. Before internal data or production use, implement enterprise SSO/RBAC, least privilege, Saudi-approved hosting/residency, encryption, immutable audit snapshots, evidence access logs, secure headers/CSRF/rate limits, secrets management, dependency/vulnerability review, environment separation, backup/disaster recovery, and named release/decision authorities as specified in `docs/implementation/SECURITY_AND_DEPLOYMENT_NOTES.md`.

Synthetic mode must be disabled or unmistakably segregated in any official production environment.

## Pre-deployment verification

```bash
make ci
bash scripts/final_acceptance.sh
```

Require fresh zero-exit evidence, zero Supervisor findings, zero different-model reviewer findings, and green current-head hosted checks before release. A green test run is evidence, not authorization.

## Health and smoke

```bash
curl --fail --silent --show-error http://127.0.0.1:8000/api/health
PYTHONPATH=src python scripts/demo_smoke.py
```

Health must report `status=ok` and `version=0.2.0`. Smoke must retain steel public `INVESTIGATE`, steel simulated `ADVANCE` with unchanged real state, PP public `REJECT`, and 4/4 extraction.

## Persistence, migration, backup, and restore

The MVP has no database or mutable user state, so schema migration and operational backup/restore are not applicable. Recovery uses the Git repository/tag plus hashed source/data artifacts. Process-local caches are cleared by restart.

## Rollback

Create a reviewed rollback branch; never rewrite `main`:

```bash
git fetch origin main --tags
git switch -c rollback/v0.2.0 origin/main
git revert v0.2.0
make ci
bash scripts/final_acceptance.sh
git push -u origin rollback/v0.2.0
```

Open a rollback PR, require independent review and all hosted checks, then merge according to ADR-007. Do not alter manifests or golden expectations during rollback.

## Release tag

Only the Supervisor creates `v0.2.0`, after the release-state PR is merged, default-branch CI for that exact commit is green, durable state is accurate, and the tag name is confirmed absent. The Implementer and Reviewer do not tag or push. The resulting commit and tag facts are recorded by the Supervisor in the release-state PR.
