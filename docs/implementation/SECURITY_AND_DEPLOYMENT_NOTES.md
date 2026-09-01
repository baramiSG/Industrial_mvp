# Security and Deployment Notes

## 1. POC posture

The packaged POC contains:

- public worked-case evidence;
- explicitly synthetic records;
- no Ministry data;
- no credentials;
- no external API calls;
- no user accounts;
- no write endpoint.

It is suitable for a controlled local demonstration, not production policy authorization.

## 2. Local deployment

Recommended for the first demonstration:

```bash
./START_DEMO_WSL.sh
```

Bind to `127.0.0.1` so the service is not exposed to the wider network.

## 3. Docker deployment

```bash
docker compose up --build
```

For a shared demonstration host, place the container behind an approved reverse proxy and restrict network access.

## 4. Production controls required before internal data

### Identity and access

- enterprise SSO;
- role-based access by analyst, technical reviewer, fiscal reviewer and authorizer;
- least privilege by data source and case;
- session and device controls.

### Data

- Saudi residency and approved hosting;
- encryption at rest and in transit;
- source-classification labels;
- separate raw, curated and decision stores;
- row/document access policy;
- retention and legal-hold rules.

### Audit

- immutable decision snapshots;
- user, model, prompt, code and config version;
- reviewer and override identity;
- before/after value for every manual correction;
- evidence access log.

### AI

- approved model/provider;
- no confidential data used for provider training;
- prompt injection and document-content controls;
- output schema enforcement;
- redaction and data-loss prevention;
- model-evaluation gate by sector.

### Application

- CSRF and secure headers;
- rate limiting;
- input validation;
- vulnerability and dependency scanning;
- secrets vault;
- backup and disaster recovery;
- environment separation.

## 5. Production environment separation

```text
DEV: synthetic and public only
TEST: masked or synthetic Ministry-shaped data
UAT: restricted representative internal data
PROD: approved source systems and authorization workflow
```

Synthetic mode must be disabled or unmistakably segregated in any official production decision environment.

## 6. Release control

A production release requires:

- integrity pass;
- unit/golden/integration tests;
- dependency scan;
- security review;
- configuration approval;
- snapshot and migration plan;
- rollback plan;
- named release authority.
