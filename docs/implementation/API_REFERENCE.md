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

Returns the structured Decision Dossier as JSON, with `dossier_version: "2.0.0"`. Simulated mode sets `next_evidence_actions` to the active decision `missing_facts`, includes `counterfactual` from `simulation_decision`, and projects the scenario bilingual narrative. Public mode returns `counterfactual: null`. Where applicable, `evidence_summary.selection` retains the pinned public selection identity, rule, reference and profile. The dossier projection excludes the Executive candidate and line diagnostics, their passports, and raw scenario/register records; use their dedicated analysis surfaces instead.

## GET `/api/opportunities/{opportunity_id}/dossier.html?mode=...`

Returns the printable A4 multipage dossier in English or Arabic (`locale=en|ar`). The first page is the decision summary and the following pages carry the full appendix. Browser print/Save PDF is the supported export path. Simulated mode repeats the full synthetic disclosure on every printed page and renders the localized scenario narrative with correctly attributed source-language spans.

Simulated dossier JSON and HTML include the labelled synthetic R6/R7/R8 evaluations; public dossier output contains none.

## GET `/api/extraction-demo`

Runs the offline AR/EN extraction golden set and returns accuracy, expected fields, actual fields and source spans.

## Graph API

`GET /api/graph/status` returns the live mirror state. `GET /api/graph/catalogue` returns the fixed bilingual four-view catalogue independently of mirror availability. `GET /api/graph/opportunities/{opportunity_id}/views/{view_id}?mode=public|simulated` returns one fixed view; optional canonical context parameters are `company_id`, `plant_id`, `line_id` and `requirement_item_id`. Public adjacency carries source-bound rows for each producer, with its own signal membership; opportunity-wide reference R9-S remains a separate engine-evidence summary and cannot be attributed to a producer. `GET /api/graph/portfolio/shared-enablers?mode=public|simulated` returns graph/artifact-equal shared-enabler rows.

Unavailable live configuration, driver, connection or projection equality returns HTTP 200 with `GRAPH_UNAVAILABLE`, a typed reason and no partial elements or artifact fallback. Unknown opportunity or view returns typed 404; an invalid mode uses FastAPI 422. A missing, corrupt or malformed canonical graph artifact returns sanitized HTTP 422 `GRAPH_ARTIFACT_INTEGRITY_ERROR`. Query failures after an available status check use the same typed unavailable boundary, while offline-guard and unexpected programming exceptions propagate.

## Error behavior

- unknown opportunity: HTTP 404;
- missing synthetic scenario in simulated list or detail mode: HTTP 404 with the unavailable opportunity in `detail`;
- evidence-integrity failure in simulated mode (policy, public-marginal reconciliation, scenario contract or ground-truth back-test): HTTP 422 with {"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", "message": ...}}; no partial analysis is returned.
- malformed governed data: fail closed with a clear error;
- static frontend paths: the catch-all resolves a candidate and serves it only when it is a file contained by the resolved `src/ior_mvp/static` directory; traversal and unknown paths return the SPA `index.html` and cannot expose project files.

## Screening record and Ministry decision diagnostics

`GET /api/screening/records/{hs6}` returns the selected public screening record and its evidence passports. Its `deep_assessment` is a six-field public link (`opportunity_id`, `brief_id`, `screening_snapshot_id`, `hs_revision`, `hs6`, `period_year`) only for the validated H6 cases `294110`, `294120`, `310430`, `310510`, `392010`, `721012`, `721061`, `760429` and `760711`; it is `null` for other records. The join checks public source, HS revision, universe identity and selected import period.

`GET /api/executive/summary` supplies the aggregate decision list. `GET /api/executive/opportunities/{opportunity_id}` supplies the typed case, including `candidate_discovery` and `line_assessment` diagnostics. Both diagnostics have `available`, `reason`, scenario provenance and `rows`; unavailable reasons are `NO_SCENARIO`, `NO_REGISTER` or `NO_LINE_RECORDS`, with empty rows and no synthetic records. Available candidate rows identify company/plant/line scope, recorded findings under P01–P09, source references, and next-evidence requests with missing field, dataset/action, route effect and subject scope alongside request codes and `NOT_CALCULABLE` numeric EVSI. Available line rows carry technical comparisons, gates, known-weight coverage, D*, dimensions and capacity diagnostics; `winner` remains null. These diagnostics are Class-D simulated evidence and do not alter `real_decision`. Public opportunity analysis omits scenario-only candidate keys; typed unavailability in the Executive case is a different contract. Unknown Executive opportunities return typed `EXECUTIVE_OPPORTUNITY_NOT_FOUND` (404); Executive integrity errors return typed `EXECUTIVE_INTEGRITY_ERROR` (422).

## S18b read-only presentation joins

The `/executive` client reads `/api/executive/summary` once per route session/retry, then `/api/executive/opportunities/{opportunity_id}` and the selected public `/api/opportunities/{opportunity_id}?mode=public` together. Only an available simulation triggers the corresponding simulated analysis read. Existing response contracts are unchanged: summary owns counts/integrity/EVSI; selected analyses supply localized narrative, trade, capability, economics and full passports. No all-case browser aggregation or domain calculation replaces the executive API.

Before rendering, the client requires matching opportunity/snapshot, complete immutable `real_decision`, state/route/scenario equality and exact branch-qualified claims/references. Failed requests or joins display localized retry/unavailable states without previous-case sources. `ExecutiveCase` still has no new EVSI availability field: the client joins the exact summary row by opportunity and scenario. Zero remains available; null/NOT_CALCULABLE/UNAVAILABLE are not converted to zero. Graph deep links accept only validated case/mode/fixed-view inputs and use the existing live graph unavailable contract.
