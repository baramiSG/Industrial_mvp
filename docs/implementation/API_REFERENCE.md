# MVP API Reference

Base URL:

```text
http://127.0.0.1:8000
```

Interactive OpenAPI:

```text
/docs
```

## GET `/api/health`

Returns runtime status, version and evidence boundary.

## GET `/api/project`

Returns the project definition, modes, external build references and golden-case expectations.

## GET `/api/thresholds`

Returns the versioned threshold artifact exactly as loaded by the engine.

## GET `/api/opportunities?mode=public|simulated`

Returns portfolio summaries.

Example:

```json
[
  {
    "id": "SAU-H0-721049",
    "hs6": "721049",
    "real_state": "INVESTIGATE",
    "active_state": "ADVANCE",
    "mode": "simulated"
  }
]
```

## GET `/api/opportunities/{opportunity_id}?mode=...`

Returns the complete analysis contract:

- opportunity and snapshot;
- real, simulation and active decisions;
- R-rule ledger;
- capability;
- capacity/economics/competition/EVSI where available;
- trade, evidence and data unlocks;
- integrity assertions.

## GET `/api/opportunities/{opportunity_id}/ui-manifest?mode=...`

Returns the approved GenUI component manifest.

## GET `/api/opportunities/{opportunity_id}/dossier?mode=...`

Returns the structured Decision Dossier as JSON.

## GET `/api/opportunities/{opportunity_id}/dossier.html?mode=...`

Returns a printable one-page HTML dossier. Simulated mode includes the synthetic disclosure.

## GET `/api/extraction-demo`

Runs the offline AR/EN extraction golden set and returns accuracy, expected fields, actual fields and source spans.

## Error behavior

- unknown opportunity: HTTP 404;
- missing synthetic scenario in simulated mode: HTTP 404;
- malformed governed data: fail closed with a clear error;
- static frontend paths: served by the SPA fallback.
