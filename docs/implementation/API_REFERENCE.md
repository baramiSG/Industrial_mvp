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

Returns runtime status, release version `0.2.0` and evidence boundary.

## GET `/api/project`

Returns the project definition, modes, external build references and golden-case expectations.

## GET `/api/thresholds`

Returns the versioned threshold artifact exactly as loaded by the engine.

## GET `/api/case-selection`

Returns response schema `1.0.0` for the manifest-verified public S15 selection record: selection and rule identities, repository-relative reference and hash, recorded public input references, and ordered pharma/API and fertilizer profile objects with quotas, selected cases, substitutes and every recorded exclusion. The endpoint accepts no caller-selected file path and remains identical if an unused `mode` query is supplied. Selection-integrity failures return HTTP 422 with `CASE_SELECTION_INTEGRITY_ERROR` and no partial response.

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
- R-rule ledger; simulated mode appends labelled Class-D R6/R7/R8 rows while retaining the public rows;
- capability;
- capacity/economics/competition/EVSI where available;
- trade, evidence and data unlocks;
- integrity assertions, including `ground_truth_backtest` (`expected`, `actual`, `match`) on successful simulated responses.

In simulated mode the top-level aggregate mirrors `simulation_decision` for route hypotheses, gap class, hard exclusions, advance gate and preferred hypothesis while `real_decision` remains the public branch unchanged. `active_decision` equals `simulation_decision`. Simulated decisions expose bilingual `localized_narrative` from the scenario contract; `data_unlocks.localized_missing_facts` always reflects the five public evidence needs in both modes. `evsi` is the existing calculated mapping when a complete block is supplied, or `null` when the optional block is absent. Supplied null, wrong-type, empty, partial or non-convertible blocks remain evidence-integrity errors and return HTTP 422; null is never a numeric zero.

## GET `/api/opportunities/{opportunity_id}/ui-manifest?mode=...`

Returns the approved GenUI component manifest.

## GET `/api/opportunities/{opportunity_id}/dossier?mode=...`

Returns the structured Decision Dossier as JSON. Simulated mode sets `next_evidence_actions` to the active decision `missing_facts`, includes `counterfactual` from `simulation_decision`, and projects the scenario bilingual narrative. Public mode returns `counterfactual: null`. The four S15b cases use dossier version `1.3` and add `evidence_summary.selection` with the pinned selection id, rule, reference and profile; earlier dossiers remain version `1.2` without that field.

## GET `/api/opportunities/{opportunity_id}/dossier.html?mode=...`

Returns a printable one-page HTML dossier. Simulated mode includes the synthetic disclosure and renders the localized scenario narrative without source-language islands in Arabic.

Simulated dossier JSON and HTML include the labelled synthetic R6/R7/R8 evaluations; public dossier output contains none.

## GET `/api/extraction-demo`

Runs the offline AR/EN extraction golden set and returns accuracy, expected fields, actual fields and source spans.

## Graph API

`GET /api/graph/status` returns the live mirror state. `GET /api/graph/catalogue` returns the fixed bilingual four-view catalogue independently of mirror availability. `GET /api/graph/opportunities/{opportunity_id}/views/{view_id}?mode=public|simulated` returns one fixed view, and `GET /api/graph/portfolio/shared-enablers?mode=public|simulated` returns graph/artifact-equal shared-enabler rows.

Unavailable live configuration, driver, connection or projection equality returns HTTP 200 with `GRAPH_UNAVAILABLE`, a typed reason and no partial elements or artifact fallback. Unknown opportunity or view returns typed 404; an invalid mode uses FastAPI 422. A missing, corrupt or malformed canonical graph artifact returns sanitized HTTP 422 `GRAPH_ARTIFACT_INTEGRITY_ERROR`. Query failures after an available status check use the same typed unavailable boundary, while offline-guard and unexpected programming exceptions propagate.

## Error behavior

- unknown opportunity: HTTP 404;
- missing synthetic scenario in simulated list or detail mode: HTTP 404 with the unavailable opportunity in `detail`;
- evidence-integrity failure in simulated mode (policy, public-marginal reconciliation, scenario contract or ground-truth back-test): HTTP 422 with {"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", "message": ...}}; no partial analysis is returned.
- malformed governed data: fail closed with a clear error;
- static frontend paths: the catch-all resolves a candidate and serves it only when it is a file contained by the resolved `src/ior_mvp/static` directory; traversal and unknown paths return the SPA `index.html` and cannot expose project files.
