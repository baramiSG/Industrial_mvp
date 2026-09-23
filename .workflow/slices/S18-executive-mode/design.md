# S18 Executive Mode design

Status: delegated-owner approved design; implementation not started. Commit is deferred to the governed reviewed candidate because repository workflow prohibits an unreviewed planning commit.

## 1. Objective

Deliver a separate bilingual `/executive` surface where a Deputy Minister can follow one selected opportunity through eight progressive evidence-backed steps, compare public and simulated states side by side, inspect the four methodology §8 decision vectors, see which missing dataset classes block loaded cases and public screening records, and drill every major claim to stored evidence.

The analyst workspace at `/` remains behaviorally intact. Executive output is explanatory projection only; it cannot approve, override or allocate support.

## 2. Resolved design questions

No external question remains after authority reading:

1. **Surface boundary:** use a direct `/executive` SPA route with an explicit switch back to `/`; do not embed executive content into the analyst workspace.
2. **Default case:** use a valid `opportunity` query parameter, otherwise the first configured portfolio case; never dispatch decision logic by product ID.
3. **Public versus synthetic quantification:** public missing-dataset counts and Class-D EVSI are separate payload branches and visual blocks. EVSI is never added to a public score.
4. **EVSI grouping:** current scenarios do not declare a dataset identifier. Therefore S18 may aggregate declared scenario EVSI across cases and show each declared `next_fact`, but it must not assign those values to dataset categories by guessing from prose.
5. **Screening scale:** aggregate the existing structured `evidence_needs[].code` across all 5,443 records through a cached read-only service; do not rebuild the screening snapshot.
6. **Delivery size:** split S18 into backend/provenance and UI/visual children. Parent S18 completes only after both merge.

A visual companion was not needed: route, hierarchy, component and viewport rules are already explicit in the governing UX and visual-oracle contracts.

## 3. Approaches considered

### A. Server-composed projection, split backend/UI — selected

A deterministic `executive` service produces typed summary and case projections; a separate route renders only those contracts. This centralizes cross-case counts, integrity and claim provenance, supports API/unit tests without a browser, and prevents JavaScript from reimplementing decision semantics. Cost: one new read-only API package and versioned contracts.

### B. Browser orchestration over existing APIs — rejected

The client could fetch public and simulated analysis for every case plus screening data and calculate counts itself. This avoids backend endpoints but duplicates domain semantics in JavaScript, creates many requests, weakens NFR-005 and makes claim/evidence completeness harder to prove.

### C. Executive components inside the existing analyst GenUI grid — rejected

This maximizes registry reuse but violates the requirement for a separate Executive Mode, complicates analyst navigation and makes progressive narrative state compete with analytical cards.

## 4. Parent decomposition

### S18a — executive projection, provenance and API

- New `ior_mvp.executive` package with Pydantic v2 models and enums.
- Deterministic executive summary/case services and mounted read-only API.
- Structured dataset taxonomy from existing R12/screening need codes.
- Public unlock counts, separate Class-D EVSI aggregation, live integrity result and four decision vectors.
- Claim registry reused by analyst GenUI and executive projection.
- Core 01/02/04/07/09 and ADR-028 mapping, generated authority manifests, no UI or visual bytes.

### S18b — bilingual route, analyst claim links and visual acceptance

- `/executive` route/surface, URL-preserved case and locale, explicit analyst/executive switch.
- Fixed executive component registry and modular renderers.
- Existing metric, rule and narrative components gain claim-to-evidence anchors.
- UI strings 1.5.0 → 1.6.0; Core 03/09 and UX spec updates.
- Real-browser journeys, accessibility/RTL/race/security tests and 16 canonical images, taking the matrix 112 → 128.

## 5. Backend architecture

### 5.1 Typed contracts

Enums:

- `ExecutiveStepId`: `SIGNAL`, `FALSE_POSITIVE_CONTROLS`, `PUBLIC_CONCLUSION`, `MISSING_MINISTRY_FACTS`, `SIMULATED_EVIDENCE`, `ROUTE_COMPARISON`, `INTERVENTION`, `CONDITIONS_AND_KILL`.
- `DecisionVectorId`: `MARKET_GAP`, `STRATEGIC_RESILIENCE`, `EXECUTION_FEASIBILITY`, `EVIDENCE_CONFIDENCE`.
- `DatasetKind`: `IDENTITY_TARIFF`, `TARGET_SPECIFICATION_DEMAND`, `PRODUCER_CAPABILITY`, `EFFECTIVE_CAPACITY_ALLOCATION`, `RETAINED_FLOW`, `ROUTE_ECONOMICS`, `UNMAPPED`.
- `ClaimStatus`: `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`.

Pydantic models cover claim references, progressive steps, side-by-side decisions, vectors, dataset unlock rows, Class-D EVSI summary, integrity checks, summary and case responses. Unknown input codes remain `UNMAPPED` with their exact source code; they are never dropped or treated as zero.

### 5.2 API

- `GET /api/executive/summary`: portfolio identity, live integrity, public dataset counts across loaded cases and screening, separate synthetic EVSI summary, authority versions.
- `GET /api/executive/opportunities/{opportunity_id}`: eight steps, public/simulated comparison, vectors, claims and stored evidence index.

Both endpoints are mode-independent because comparison is side by side. Unknown cases return typed 404; malformed governed inputs fail closed as typed 422. No endpoint accepts a path or evidence source.

### 5.3 Dataset unlock aggregation

Use structured `need_code` from each case's R12 `metrics.evidence_needs` and `code` from every screening record. Map exact known codes to the six dataset kinds. Count each opportunity or HS6 once per dataset kind even when multiple needs map to it. Return separate `loaded_case_count` and `screening_record_count`, exact need codes, and the affected IDs.

`UNMAPPED` remains visible. The frozen demonstration must have zero unmapped codes; a new future code produces a typed visible residual and a failing contract test until governed mapping is added.

### 5.4 Class-D EVSI

For scenarios with declared EVSI inputs, reuse the existing deterministic calculation and return:

- available and unavailable case counts;
- total, positive and non-positive approximate EVSI;
- per-case scenario ID, `next_fact`, inputs and result;
- `synthetic_flag=true`, evidence Class D, `source=DEMO_GENERATOR`, scenario IDs and both policy labels.

Do not attach EVSI to a dataset kind unless a future scenario contract explicitly declares one. Do not present the aggregate as observed value or a public ranking.

### 5.5 Live integrity KPI

Calculate, do not hard-code:

- synthetic rows in every public analysis;
- real-decision differences between public and simulated responses;
- malformed synthetic metadata;
- failed scenario reconciliation/back-test indicators.

Return individual checks, violation count and `PASS`/`FAIL`. The analyst overview and Executive Mode consume the same result. Any failure is displayed and fails tests; zero is a computed result.

### 5.6 Claim provenance

Build stable claim IDs for:

- decision headline/conclusion;
- major metric cards;
- each rule row;
- route comparison/intervention conclusion;
- every executive step.

Evidence links derive only from existing passport/evidence support codes, R12 need references, hard exclusions, route hypotheses and graph drill-down. A claim without stored support is `UNRESOLVED` and links to the missing-fact action, never to invented evidence. Conflicting evidence remains separately linked and visibly contradicted.

## 6. Executive surface

The route has one case selector, locale switch and analyst-mode return link. It does not reuse the analyst's Public/Simulation toggle because both states are always visible.

Progressive steps are an ordered native-control sequence. Opening a step reveals a fixed approved component; URL/history preserve selected case and step. Case/step/locale requests use epochs so stale responses cannot restore prior content.

Component types:

1. `executive_signal`
2. `executive_false_positive_controls`
3. `executive_public_conclusion`
4. `executive_missing_facts`
5. `executive_simulated_evidence`
6. `executive_route_comparison`
7. `executive_intervention`
8. `executive_conditions`
9. `executive_decision_vectors`
10. `executive_ministry_unlocks`
11. `executive_integrity`

Side-by-side cards always label Public Evidence and Ministry Simulation. Every simulated card repeats both policy labels. The public card contains no synthetic row, EVSI or disclosure. Missing economics, support or EVSI renders `NOT_CALCULABLE`, never zero.

## 7. Evidence drill-down and analyst preservation

Evidence ledger rows receive stable focusable IDs. Claim anchors use only evidence IDs present in the response and reuse the existing focus/scroll behavior. Major analyst metric cards, rule rows and decision narrative gain the same anchors without changing their values, order or decision behavior.

The `/` analyst workspace, screening, graph, dossier actions and existing keyboard order remain unchanged except for one explicit Executive Mode navigation control. `/executive` has its own audited keyboard order.

## 8. Bilingual, accessibility and security

All executive chrome and labels come from UI catalogue 1.6.0 with exact EN/AR parity. Technical values remain LTR islands. Arabic layout uses logical properties; steps remain 1→8 semantically while placement mirrors.

Use native buttons/links, visible focus, `aria-current` for the active step, labelled regions and live loading/error states. No raw HTML, arbitrary catalogue key, external fetch, executable model output or unsanitized evidence value enters the DOM.

## 9. Visual contract

Add four screens in EN/AR at desktop 1440×900 and tablet 1024×768:

- `journey-j-executive-signal-public`
- `journey-j-executive-simulated-route`
- `journey-j-executive-ministry-unlocks`
- `journey-j-executive-reject`

This adds 16 paths and produces 128 total images under existing image/aggregate budgets and unchanged tolerances. Canonical generation remains one owner-authorized allocation after functional proof.

## 10. Testing and failures

S18a minimum:

- happy: eight-step steel projection, dataset counts, Class-D EVSI;
- edge: missing EVSI/economics and duplicate needs deduplicate correctly;
- failure: unknown need code remains `UNMAPPED`, malformed synthetic metadata/integrity fails closed, unknown case 404;
- source-link completeness and public/synthetic leakage tests;
- NFR-005 warm endpoint measurements.

S18b minimum:

- direct `/executive` load, case/step/locale history and stale-response races;
- side-by-side values equal existing analysis APIs;
- all eight steps and four vectors in both locales;
- claim anchors focus exact stored evidence;
- computed integrity KPI negative probe;
- axe, keyboard, RTL, responsive and synthetic-label checks;
- 16 visual paths and exact preservation of all 112 old paths.

Both children run integrity, scenario validation, reconstruction, full pytest, smoke and applicable browser/graph gates. Public goldens and all eleven outcomes remain exact.

## 11. Authority and generation

S18a: ADR-028 plus Core 01/02/04/07/09; one authorized manifest generation after source/contracts are final. No scenario or evidence artifact changes.

S18b: UI strings 1.6.0, Core 03/09 and UX spec; one authorized manifest generation and one canonical visual allocation after functional proof.

Any new need code, dataset mapping, EVSI input or claim source outside delivered structured fields is a new authority decision, not an implementation convenience.

## 12. Non-goals

No approval/signature/override workflow; no public-support authorization; no scenario re-authoring; no new monetary model; no ordinal opportunity ranking; no graph refresh/Aura mutation; no dossier/PDF redesign; no S19/S20/S21 work; no acquisition or live connector.

## 13. Design self-review

- Placeholder scan: PASS — no TBD/TODO or unbound numerical policy.
- Consistency: PASS — separate route, typed APIs, registry and split align.
- Scope: PASS only with S18a/S18b decomposition; one PR would be too broad.
- Ambiguity: PASS — public counts, Class-D EVSI, unmapped codes and claim support behavior are explicit.
- Delegated owner design gate: APPROVE. No external intent choice is required; all decisions are derived from ADR-010/I8 and S18 authority.
