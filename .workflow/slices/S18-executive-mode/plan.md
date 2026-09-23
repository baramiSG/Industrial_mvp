# S18a Executive projection and provenance API — PLAN v1

> **For agentic workers:** use the governed retained S18 implementation child. TDD is mandatory. The candidate remains uncommitted for independent review; task-level commits from generic planning guidance are prohibited by repository workflow.

**Goal:** Deliver a deterministic, typed, read-only executive projection/API that explains each loaded case in eight steps, exposes four separate decision vectors, computes public dataset-unlock counts across cases and screening, keeps Class-D EVSI separate, calculates a live integrity KPI, and binds major claims to stored evidence.

**Architecture:** Add a focused `ior_mvp.executive` package above existing decision and screening services. Pydantic v2 response models, exhaustive enums and deterministic builders project existing governed data without changing rules, outcomes, scenarios, snapshots or graph. Mount two read-only endpoints before the SPA fallback. S18b later consumes these contracts and adds all frontend/catalogue/visual work.

**Tech stack:** Python 3.11+, Pydantic v2, FastAPI, existing immutable repositories, pytest, `uv`; no new dependency, database, service or network call.

## Global constraints

- Public unlock counts use public evidence and structured need codes only.
- EVSI remains a separate `synthetic_flag=true`, Class-D, `DEMO_GENERATOR` branch with scenario IDs and both visible policy labels.
- Never assign scenario EVSI to a dataset kind by parsing `next_fact` prose.
- Unknown need codes remain visible as `UNMAPPED`; they never disappear or improve permission.
- Do not change public/simulated decisions, routes, thresholds, scenario/data bytes, graph bytes or the two frozen golden outcomes.
- No approval, override, signature or public-support authorization behavior.
- All public function signatures carry types and Google-style docstrings; structured outputs use Pydantic models/enums, not raw output dictionaries.
- No file exceeds 500 lines; each new module has one responsibility.
- No implementation task commits. Stop with one exact uncommitted candidate for independent review.

---

## 1. Scope, authority and parent split

Parent S18 is split before implementation:

1. `s18a-executive-projection-provenance-api` — this plan.
2. `s18b-bilingual-executive-surface` — depends on s18a and owns `/executive`, UI strings 1.6.0, analyst claim anchors, browser and visual acceptance.

Parent completion requires both children delivered. The owner records the split in `docs/BUILD_ROADMAP.md` and `.workflow/state.json`; implementation child permissions exclude `.workflow/**`.

Authority:

- governing DOCX §§8, 9, 10.3, 15;
- Core 01/02/03/04/07/09;
- ADR-010 and owner interpretation I8;
- `GAP_ANALYSIS.md` A7/A11/G3/G4/G5 and uncovered §8 vectors;
- `SLICE_GRAPH.md` S18;
- approved design `.workflow/slices/S18-executive-mode/design.md`.

Change classification:

- Manifest §7.4: Core 01/02/04/07/09 executive contracts;
- implementation-preserving API/service changes around existing decisions;
- one authorized `scripts/build_manifests.py` run after final source/docs checks;
- no methodology DOCX, config, snapshot, scenario, golden or visual change.

## 2. Existing patterns to reuse

- FastAPI route/service boundaries: `screening/api.py`, `graph/api.py`, `app.py` mount ordering.
- Immutable cached loaders: `screening/repository.py`, decision/config caches and explicit clear helpers in tests.
- Structured need codes: R12 `metrics.evidence_needs`; screening `evidence_needs[].code`.
- Existing evidence rows and `supports` vocabulary; no parallel passport store.
- Existing public/simulated `analyze()` results and scenario EVSI calculation.
- Existing authority/error mapping in `app.py`; no raw stack traces.
- Existing performance TestClient pattern and synthetic-isolation tests.

## 3. File structure

### New implementation files

- `src/ior_mvp/executive/__init__.py` — package exports only.
- `src/ior_mvp/executive/models.py` — enums and frozen Pydantic response models.
- `src/ior_mvp/executive/taxonomy.py` — exact need-code → dataset-kind mapping and exhaustive validation.
- `src/ior_mvp/executive/claims.py` — stable major-claim IDs and evidence-reference projection.
- `src/ior_mvp/executive/service.py` — cached summary/case builders, steps, vectors, integrity and EVSI branches.
- `src/ior_mvp/executive/api.py` — read-only FastAPI router and structured error mapping.

### Existing implementation files

- `src/ior_mvp/screening/repository.py` — add public deterministic record iterator and cache-clear coverage.
- `src/ior_mvp/app.py` — mount executive router before graph/router SPA fallback; no handler business logic.

### New tests

- `tests/test_executive_models.py`
- `tests/test_executive_taxonomy.py`
- `tests/test_executive_claims.py`
- `tests/test_executive_service.py`
- `tests/test_executive_api.py`
- `tests/test_executive_isolation.py`
- `tests/test_executive_performance.py`

### Authority/control files

- `docs/core/01_PRODUCT_AND_REQUIREMENTS.md`
- `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`
- `docs/core/04_CANONICAL_DATA_MODEL.md`
- `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`
- `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`
- `docs/ARCHITECTURE_DECISIONS.md` — ADR-028.
- `docs/BUILD_ROADMAP.md`, `docs/BUILD_PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`.
- `.workflow/state.json` and `.workflow/slices/S18-executive-mode/*` — owner only.
- Generated once: `docs/authority/authority_hashes.json`, Authority Manifest §11 table, and only the generator's mechanically required manifest metadata delta.

## 4. Locked interfaces

### 4.1 Enums

`ExecutiveStepId`, in exact order:

`SIGNAL`, `FALSE_POSITIVE_CONTROLS`, `PUBLIC_CONCLUSION`, `MISSING_MINISTRY_FACTS`, `SIMULATED_EVIDENCE`, `ROUTE_COMPARISON`, `INTERVENTION`, `CONDITIONS_AND_KILL`.

`DecisionVectorId`:

`MARKET_GAP`, `STRATEGIC_RESILIENCE`, `EXECUTION_FEASIBILITY`, `EVIDENCE_CONFIDENCE`.

`DatasetKind`:

`IDENTITY_TARIFF`, `TARGET_SPECIFICATION_DEMAND`, `PRODUCER_CAPABILITY`, `EFFECTIVE_CAPACITY_ALLOCATION`, `RETAINED_FLOW`, `ROUTE_ECONOMICS`, `UNMAPPED`.

`ClaimStatus`:

`SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`.

### 4.2 Public functions

- `classify_need_code(code: str) -> DatasetKind`
- `validate_frozen_need_codes(codes: Collection[str]) -> None`
- `iter_screening_records() -> Iterator[dict[str, Any]]`
- `build_claim_registry(analysis: Mapping[str, Any]) -> tuple[ClaimReference, ...]`
- `build_executive_summary() -> ExecutiveSummary`
- `build_executive_case(opportunity_id: str) -> ExecutiveCase`
- `clear_executive_caches() -> None`

### 4.3 API

- `GET /api/executive/summary` → `ExecutiveSummary`
- `GET /api/executive/opportunities/{opportunity_id}` → `ExecutiveCase`

Responses are mode-independent and include both branches where simulation exists. Unknown opportunity → typed 404 `EXECUTIVE_OPPORTUNITY_NOT_FOUND`. Governed integrity/taxonomy failure → typed 422 `EXECUTIVE_INTEGRITY_ERROR`. Unexpected exceptions propagate to the normal server boundary.

## 5. Taxonomy contract

Exact mapping:

| Need code | Dataset kind |
|---|---|
| `identity/tariff-line` | `IDENTITY_TARIFF` |
| `target specification/application` | `TARGET_SPECIFICATION_DEMAND` |
| `line-level production or producer-grade matrix` | `PRODUCER_CAPABILITY` |
| `capacity/availability/allocation` | `EFFECTIVE_CAPACITY_ALLOCATION` |
| `re-export/origin decomposition` | `RETAINED_FLOW` |
| `route economics` | `ROUTE_ECONOMICS` |

Unknown codes map to `UNMAPPED` and remain in the response with exact code and affected IDs. A repository-level frozen-input test requires zero unmapped current codes; generic unit tests prove visible unmapped behavior.

Counts deduplicate by `(dataset_kind, opportunity_id)` and `(dataset_kind, hs6)`. Return loaded-case and screening-record counts separately; never add them into one ranking count.

## 6. Claim provenance contract

Evidence selection uses existing `evidence[].supports` only:

- trade signal: `TRADE_VALUE`, `TRADE_QUANTITY`, `SUPPLIER_CONCENTRATION`;
- product/specification: `TARGET_PRODUCT_IDENTITY`, `BILINGUAL_SPECIFICATION_EXTRACTION`, `DOMESTIC_SPECIFICATION_ENVELOPE`, `DOMESTIC_DIMENSION_ENVELOPE`;
- supply/capability: every delivered `DOMESTIC_*` support code;
- generic-capacity control: `EXPORT_IMPORT_RATIO` plus domestic capability supports;
- evidence needs: exact R12 `evidence_ids`;
- route claims: route hypothesis `evidence_ids` plus evidence IDs supporting fired rules.

Stable claim IDs are semantic (`decision.public`, `metric.trade`, `metric.concentration`, `rule.<rule_id>`, `route.<route_code>`, `step.<step_id>`), not index-derived.

If evidence IDs are empty, emit `UNRESOLVED` and the relevant missing need codes. Never choose the first evidence row as a fallback. Contradictory evidence rows remain linked and set `CONTRADICTED` when the evidence contract marks a contradiction.

## 7. Eight-step and vector contract

Steps are fixed and all eight are always present. Missing data produces typed `NOT_CALCULABLE`/`UNAVAILABLE` values.

1. Signal — trade metrics and fired signal rules.
2. False-positive controls — exclusions, R11 and measurement warnings.
3. Public conclusion — real state, gap, preferred route and rationale.
4. Missing Ministry facts — R12 needs and dataset kinds.
5. Simulated evidence — scenario identity, Class-D inputs and warnings, or typed unavailable.
6. Route comparison — public/simulated route hypotheses and selected routes.
7. Intervention — unsupported economics, S*, ΔNV, competition and EVSI where calculable.
8. Conditions and kill — both branch conditions/kill conditions.

Four separate vectors:

- market/gap;
- strategic/resilience;
- execution feasibility;
- evidence confidence.

No combined score or ordinal rank is allowed.

## 8. Integrity and EVSI contract

Integrity checks calculate:

- synthetic evidence rows in public analysis;
- exact public-vs-simulated `real_decision` equality;
- required Class-D/source/scenario/policy-label metadata on synthetic rows;
- reconciliation and ground-truth back-test PASS where simulation exists.

Return each check, violation count and overall `PASS`/`FAIL`. Do not literalize zero. Any malformed case raises `ExecutiveIntegrityError`; negative tests inject violations without weakening production guards.

EVSI remains a separate `SyntheticEvsiSummary` with Class D, `source=DEMO_GENERATOR`, scenario IDs, both policy labels, available/unavailable counts, `math.fsum` totals and per-case declared `next_fact`. It is never merged into public dataset rows or assigned to a dataset kind.

## 9. TDD task sequence

### Task 1 — Models and strict validation

**Interfaces:** produces all enums/models consumed by later tasks.

- [ ] Add tests that valid summary/case models serialize deterministically.
- [ ] Add edge tests for `NOT_CALCULABLE`, unavailable simulation and `UNMAPPED` rows.
- [ ] Add failure tests for duplicate step/vector IDs, wrong step order, public synthetic flags, Class-D metadata omissions and mixed public/EVSI branches.
- [ ] Run `PYTHONPATH=src uv run --locked --extra dev pytest -q tests/test_executive_models.py`; require RED for missing module, then GREEN with all tests passing.

### Task 2 — Need taxonomy and screening iterator

**Interfaces:** consumes screening snapshot/shards; produces `classify_need_code`, `validate_frozen_need_codes`, `iter_screening_records`.

- [ ] RED tests for all six mappings, visible unknown code, deduplication inputs and exact 5,443-record iteration without mutation.
- [ ] Implement exact map in `taxonomy.py` and public iterator in `screening/repository.py`; include cache clearing.
- [ ] GREEN focused tests; require unique HS6 set and zero unmapped frozen codes.
- [ ] Re-run screening repository/API/reconstruction tests to prove no snapshot or queue change.

### Task 3 — Claim registry

**Interfaces:** consumes one analysis mapping; produces immutable ordered `ClaimReference` models.

- [ ] RED happy tests for trade, R3, R11, route and R12 claim evidence IDs.
- [ ] RED edge tests for contradicted evidence and genuinely unresolved claims.
- [ ] RED failure tests for referenced IDs absent from `analysis.evidence`, duplicate claim IDs and synthetic evidence attached to a public claim.
- [ ] Implement support-code mapping and fail-closed reference validation.
- [ ] GREEN focused claims and existing rule/evidence isolation suites.

### Task 4 — Executive summary

**Interfaces:** consumes loaded public/simulated cases plus all screening records; produces cached `ExecutiveSummary`.

- [ ] RED test exact current dataset counts from independently calculated fixtures and separate case/screening affected IDs.
- [ ] RED test current Class-D EVSI availability/unavailability, policy labels, scenario IDs and `math.fsum` totals.
- [ ] RED negative integrity fixtures: leaked public synthetic row, changed real decision, wrong source/class/flag/scenario and failed reconciliation.
- [ ] Implement summary/integrity/EVSI builders and cache clear.
- [ ] GREEN tests plus full synthetic-leakage suite; assert no public row contains EVSI or synthetic labels.

### Task 5 — Executive case projection

**Interfaces:** consumes public analysis, optional simulation analysis and claim registry; produces `ExecutiveCase`.

- [ ] RED test steel has exact eight ordered steps and four vectors; public/simulated states/routes equal existing APIs.
- [ ] RED test polypropylene rejection does not invent intervention/support.
- [ ] RED edge test a case without scenario emits simulation `UNAVAILABLE`, not a fabricated panel.
- [ ] RED failure test unknown opportunity and malformed route/claim evidence.
- [ ] Implement step/vector projectors with existing fields only.
- [ ] GREEN focused tests and all eleven outcome equality assertions.

### Task 6 — API and performance

**Interfaces:** produces mounted `executive_router` and typed HTTP responses.

- [ ] RED API tests for summary, case, 404, 422, no caller mode/path and schema equality.
- [ ] RED route-order test proving mount before SPA fallback.
- [ ] RED warm performance test: median of five real TestClient calls for summary and one case each below existing NFR-005 250 ms, after one excluded warm-up.
- [ ] Implement route handlers containing only service calls/error mapping; mount in `app.py`.
- [ ] GREEN API/performance/OpenAPI tests; confirm runtime imports no acquisition transport/network client.

### Task 7 — Authority mapping and generation

**Interfaces:** documents the exact implemented contracts; changes no behavior.

- [ ] Update Core 01 with S18 executive FRs; Core 02 implementation mapping; Core 04 typed Executive models/dataset taxonomy/claim contract; Core 07 count/EVSI/integrity rules; Core 09 tests/gates.
- [ ] Record ADR-028 and S18 split/control rows without claiming review or delivery.
- [ ] Add tests pinning exact authority statements and absence of public/synthetic conflation.
- [ ] Run focused docs/contracts, integrity, goldens, all eleven outcomes and reconstruction before generation.
- [ ] Run `scripts/build_manifests.py` exactly once under owner authorization.
- [ ] Require authority row count unchanged and changed hashes confined to Core 01/02/04/07/09; inspect actual snapshot-manifest metadata delta and reject any data-row change.
- [ ] Mirror Authority Manifest §11 from generated JSON and run immediate integrity verification.

### Task 8 — Complete candidate proof

- [ ] Run prohibited-file, secret, compile, threshold and UI-contract scans.
- [ ] Run `PYTHONPATH=src pytest -q`.
- [ ] Run required proof: integrity, scenario validation, reconstruction and demo smoke.
- [ ] Run browser functional/visual compare to prove zero S18a visual/source-provenance change; no canonical update.
- [ ] Materialize a clean different-path portability root and rerun complete non-live gates.
- [ ] Record base SHA, candidate tree/aggregate, changed files/content hashes, exact commands and outcomes; leave ordinary index unstaged/uncommitted.
- [ ] Submit exact candidate to independent review; adjudicate findings with the same retained implementation child; separate owner acceptance precedes delivery.

## 10. Verification commands

Focused commands use `PYTHONPATH=src /home/barami/.local/bin/uv run --locked --extra dev`.

Required complete gates:

1. `PYTHONPATH=src python3 scripts/verify_integrity.py`
2. `PYTHONPATH=src pytest -q`
3. `PYTHONPATH=src python3 scripts/demo_smoke.py`
4. `PYTHONPATH=src uv run --locked --extra dev python scripts/validate_scenarios.py`
5. `PYTHONPATH=src uv run --locked --extra dev python scripts/reconstruct_snapshot.py --all`
6. `make e2e` in compare-only mode
7. different-path clean candidate repeats integrity, pytest, smoke and reconstruction.

No graph load/Aura operation is required because S18a changes no graph input or graph service. Existing graph reconstruction/build-check remains part of the full repository gates.

## 11. Data, security, lifecycle and migration implications

- Persistence/schema migration: none; no SQL/database state.
- API: two additive read-only routes and versioned response models.
- Data isolation: public counts and synthetic EVSI are separate model fields with incompatible invariants.
- Audit: every claim carries stored evidence IDs or explicit unresolved need codes.
- Immutability: no snapshot/scenario/graph/golden byte changes; manifest generation covers Core hashes only.
- Security/privacy: no source body, filesystem path, credential or new external URL; existing evidence URLs are returned only as stored passport fields in later S18b drill-down.
- Cache lifecycle: immutable-file `lru_cache`; operator restart/explicit test cache clear after approved artifact changes.

## 12. Risks and review focus

1. **Taxonomy laundering:** prose parsing or unknown-code dropping would fabricate dataset certainty. Review exact enum map and `UNMAPPED` behavior.
2. **Synthetic leakage:** EVSI must never appear in public counts/vectors/real decisions. Review Pydantic separation and negative fixtures.
3. **Claim overstatement:** evidence support-code mapping may over-link. Review each support-code family and unresolved behavior.
4. **Performance:** screening aggregation over 96 shards must be cached and warm endpoint proof must stay below 250 ms.
5. **Scope:** no UI, visual, config catalogue, scenario or S18b work in S18a.
6. **Authority generation:** exactly one run; no acceptance of unexpected data/manifests to make integrity pass.

## 13. Non-goals and explicit deferrals

Deferred to S18b: `/executive` HTML/JS/CSS, analyst claim anchors, UI strings, browser journeys, accessibility/RTL and 128-image visual matrix.

Deferred to S19+: dossier/PDF, extraction corpus, demo orchestration and release acceptance.

## 14. Open decisions

None. The design choices are bound by the governing S18 scope and delegated owner decision. Any request to add a dataset identifier to scenarios, aggregate EVSI by guessed dataset, create a combined score, authorize intervention, change evidence/scenario bytes or refresh Aura is outside this plan and requires a new owner/authority decision.

## 15. Plan self-review

- Spec coverage: PASS; every S18a design section maps to Tasks 1–8.
- Placeholder scan: PASS; no unresolved marker or unspecified handler.
- Type consistency: PASS; model/enums/functions/routes are defined once and reused.
- Scope: PASS with parent split; S18b work is explicit non-goal.
- Test minimum: PASS; happy, edge and failure cases are explicit for every new behavior.
- Workflow: PASS; TDD, one retained child, uncommitted candidate, independent review and separate owner acceptance are preserved.

Paused for independent plan review. No implementation, generation, staging, commit, push or PR is authorized by PLAN v1.
