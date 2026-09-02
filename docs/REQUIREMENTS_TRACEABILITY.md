# Requirements Traceability

Statuses: `NOT_STARTED` · `PLANNED` · `IMPLEMENTED` (code and test exist; not yet executed under this build's CI) · `TESTED` (executed with recorded evidence) · `VALIDATED` (independent review passed) · `COMPLETE` (merged, CI green, evidence recorded) · `BLOCKED` · `NOT_APPLICABLE`.

Code existing is never sufficient for `COMPLETE`. Evidence lives in `.workflow/slices/*/test_evidence.md`.

Columns: ID · Requirement · Governing source · Implementation · API · UI · Test · Validator · Status · Slice

## A. Functional requirements (Core 01 §6)

| ID | Requirement | Source | Implementation | API | UI | Test | Validator | Status | Slice |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | Methodology version, snapshot ID, as-of date exposed for every case | Core 01 §6.1 | `decision_engine.analyze_public` (snapshot_id, as_of_date); methodology/config version **missing** | `/api/opportunities/{id}` | integrity banner | — | — | IMPLEMENTED (partial) | S03 |
| FR-002 | R-rule thresholds loaded from versioned YAML | Core 01 §6.1 | `config.thresholds_config`, `rules.py`, `decision_engine.py`, `thresholds.v1.yaml` 1.1.0 | `/api/thresholds` | configured R3 metric caption | `test_threshold_boundaries.py`, `test_rules.test_threshold_is_loaded_from_versioned_config` | `scripts/check_threshold_literals.py` | IMPLEMENTED | S02 |
| FR-003 | Sector weights and hard gates from versioned YAML | Core 01 §6.1 | `capability.evaluate_capability` | — | capability matrix | `test_capability_economics` | — | IMPLEMENTED | S01 |
| FR-004 | Evidence classes and synthetic isolation from versioned policy | Core 01 §6.1 | `evidence.validate_synthetic_scenario` | — | — | `test_synthetic_isolation` | policy lacks `display_label` | IMPLEMENTED (partial) | S03 |
| FR-005 | Integrity verification fails on missing/changed governed file | Core 01 §6.1 | `scripts/verify_integrity.py` | — | — | `test_integrity_contract` | `verify_integrity.py` | IMPLEMENTED | S01 |
| FR-010 | Opportunity represented independently of HS code | Core 01 §6.2 | snapshot `opportunity` block | `/api/opportunities` | cards | `test_golden_cases` | — | IMPLEMENTED | S01 |
| FR-011 | Each public evidence record states source, status, class, synthetic flag | Core 01 §6.2 | snapshots `evidence[]` | analysis `evidence` | evidence ledger | `test_public_snapshots_contain_no_synthetic_rows` | `validate_public_evidence` | IMPLEMENTED | S01 |
| FR-012 | Public records set `synthetic_flag=false` explicitly | Core 01 §6.2 | `evidence.validate_public_evidence` | — | — | `test_synthetic_isolation` | yes | IMPLEMENTED | S01 |
| FR-013 | Synthetic records set flag, scenario ID, Class D, DEMO_GENERATOR | Core 01 §6.2 | `evidence.validate_synthetic_scenario`, `synthetic_evidence_rows` | — | — | `test_every_synthetic_row_is_labeled` | yes | IMPLEMENTED | S01 |
| FR-014 | UI distinguishes public and synthetic rows | Core 01 §6.2 | `app.js renderEvidenceLedger`, `.synthetic-row` | — | yes | `test_static_frontend` | — | IMPLEMENTED | S01 |
| FR-015 | Contradictions retained | Core 01 §6.2 | snapshot `evidence[].contradiction` | yes | ledger | — | — | IMPLEMENTED | S01 |
| FR-020 | Engine evaluates and displays R0–R12 (15 rules) | Core 01 §6.3 | `rules.evaluate_rules` | yes | rule ledger | `test_golden_cases` | — | IMPLEMENTED | S01 |
| FR-021 | Every rule returns execution, fired, result, metrics, effect | Core 01 §6.3 | `rules._rule` | yes | yes | implicit | — | IMPLEMENTED | S01 |
| FR-022 | R2 log changes and contribution share deterministic | Core 01 §6.3 | `rules.log_change`, `quantity_contribution_share` | yes | yes | `test_log_decomposition_steel_matches_worked_case` | — | IMPLEMENTED | S01 |
| FR-023 | R4-D never claims cluster or grade | Core 01 §6.3 | `rules.py` R4-D | yes | yes | `test_degraded_uv_never_claims_grade` | — | IMPLEMENTED | S01 |
| FR-024 | R9-S opens capability but does not publish D\* | Core 01 §6.3 | `rules.py` R9-S | yes | yes | golden (R9-S fires; d_star None) | — | IMPLEMENTED | S01 |
| FR-025 | R11 supports rejection of generic capacity | Core 01 §6.3 | `rules.r11_generic_capacity_fires`; configured ratio key | yes | yes | R11 49.99/50.00/50.01 boundary; PP golden | `scripts/check_threshold_literals.py` | IMPLEMENTED | S02 |
| FR-030 | Effective capacity formula | Core 01 §6.4 | `capability.effective_qualified_capacity` | simulated `capacity` | metric grid | `test_effective_qualified_capacity_formula` | — | IMPLEMENTED | S01 |
| FR-031 | Sector-specific weights | Core 01 §6.4 | `sector_profiles.v1.yaml` | — | matrix | `test_simulated_steel_capability_is_incremental_upgrade` | — | IMPLEMENTED | S01 |
| FR-032 | Unknown dimensions → U and λ penalty | Core 01 §6.4 | `capability.evaluate_capability` | — | matrix | `test_unknowns_cannot_improve_adjacency` | — | IMPLEMENTED | S01 |
| FR-033 | D\* not published below Kmin or with unresolved hard gate | Core 01 §6.4 | `capability.publication_allowed`, `evaluate_capability` | — | "GATED" | exact Kmin predicate and profile integration in `test_threshold_boundaries.py` | — | IMPLEMENTED | S02 |
| FR-034 | Route bands (4) | Core 01 §6.4 | `capability.route_band` with configured bands | — | matrix | three below/equal/above band-edge matrices | — | IMPLEMENTED | S02 |
| FR-040 | Unsupported economics before intervention | Core 01 §6.5 | `economics.minimum_effective_support` | simulated `economics` | economics panel | `test_minimum_effective_support_is_18m` | — | IMPLEMENTED | S01 |
| FR-041 | NPV and IRR deterministic | Core 01 §6.5 | `economics.npv`, `irr` | yes | yes | same | — | IMPLEMENTED | S01 |
| FR-042 | S\* minimum support step satisfying NPV and IRR | Core 01 §6.5 | `economics.minimum_effective_support` | yes | yes | same | — | IMPLEMENTED | S01 |
| FR-043 | Incremental national value relative to no action | Core 01 §6.5 | `economics.incremental_national_value` | yes | yes | `test_national_value_and_evsi` | — | IMPLEMENTED | S01 |
| FR-044 | Post-entry capacity/downside ratio visible | Core 01 §6.5 | `decision_engine.competition_warning`, `_simulate_steel` | `competition` with configured threshold and warning | panel | 1.2499/1.2500/1.2501 boundary and payload provenance | `scripts/check_threshold_literals.py` | IMPLEMENTED | S02 |
| FR-045 | EVSI identifies whether evidence action is worth obtaining | Core 01 §6.5 | `economics.approximate_evsi` | `evsi` | panel | `test_national_value_and_evsi` | — | IMPLEMENTED | S01 |
| FR-050 | Public decisions use public evidence only | Core 01 §6.6 | `analyze_public` + `validate_public_evidence` | yes | banner | `test_public_snapshots_contain_no_synthetic_rows` | yes | IMPLEMENTED | S01 |
| FR-051 | Simulation does not mutate public decision | Core 01 §6.6 | `assert_real_decision_unchanged`, deep copy | `integrity` | banner | `test_simulated_analysis_keeps_real_decision_identical` | fingerprint | IMPLEMENTED | S01 |
| FR-052 | Every decision includes state, route, rationale, confidence, conditions, kill conditions | Core 01 §6.6 | `_public_decision`, `_simulate_*` (steel literals) | yes | hero + dossier | golden | — | IMPLEMENTED (partial) | S04 |
| FR-053 | Real ADVANCE blocked by D/E decision-critical evidence | Core 01 §6.6 | public branch never emits ADVANCE | yes | — | golden | — | IMPLEMENTED | S01 |
| FR-054 | Brownfield and no-action precede supported greenfield | Core 01 §6.6 | route labels; simulated route 5 | yes | hero | golden | — | IMPLEMENTED | S01 |
| FR-060 | Backend emits constrained UI manifest | Core 01 §6.7 | `genui.build_ui_manifest` | `/ui-manifest` | `renderManifest` | `test_steel_ui_manifest_uses_approved_components` | — | IMPLEMENTED | S01 |
| FR-061 | Manifest uses approved component types only | Core 01 §6.7 | `genui.py` | yes | renderer map | same | — | IMPLEMENTED | S01 |
| FR-062 | Economics panel absent when unavailable | Core 01 §6.7 | `genui.py` conditional | yes | yes | `test_public_manifest_omits_economics_panel` | — | IMPLEMENTED | S01 |
| FR-063 | No runtime model-generated executable code | Core 01 §6.7 | static renderer registry | guardrails | yes | manifest test | — | IMPLEMENTED | S01 |
| FR-064 | Dossier JSON and printable HTML | Core 01 §6.7 | `dossier.py` | `/dossier`, `/dossier.html` | actions | `test_dossier_html_discloses_simulation` | — | IMPLEMENTED | S01 |
| FR-070 | AR/EN spans attached to normalized fields | Core 01 §6.8 | `ai_extraction.extract_specification` | `/api/extraction-demo` | extraction cards | `test_ar_en_golden_set_is_exact` | — | IMPLEMENTED | S01 |
| FR-071 | Contract supports standard, coating, dimensions, environment | Core 01 §6.8 | same | yes | yes | same | — | IMPLEMENTED | S01 |
| FR-072 | Offline extractor passes golden set | Core 01 §6.8 | `run_extraction_golden_set` | yes | score chip | same (4/4) | — | IMPLEMENTED | S01 |
| FR-073 | Future LLM adapter must pass same gate | Core 01 §6.8 | control note; Core 08 §7 | yes | note | — | — | NOT_APPLICABLE (production) | — |

## B. Non-functional requirements (Core 01 §7)

| ID | Requirement | Source | Implementation | Test | Status | Slice |
|---|---|---|---|---|---|---|
| NFR-001 | Reproducible from frozen files and config | Core 01 §7 | hashed data, lru-cached config | integrity + golden | IMPLEMENTED | S01 |
| NFR-002 | Every derived metric has deterministic formula and source pointer | Core 01 §7 | rules/capability/economics metrics | formula tests | IMPLEMENTED | S01 |
| NFR-003 | Fail-closed: unknown hard gates reduce permission | Core 01 §7 | `evaluate_capability` | `test_public_steel_dstar_is_withheld...` | IMPLEMENTED | S01 |
| NFR-004 | Offline demo, no API key | Core 01 §7 | no network calls | frontend CDN test; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| NFR-005 | Local API responses normally < 250 ms | Core 01 §7 | in-memory JSON | **no test** | IMPLEMENTED (unmeasured) | S05 |
| NFR-006 | Accessibility: semantic controls, contrast, keyboard | Core 01 §7 | `index.html` buttons/labels | static test | IMPLEMENTED | S01 |
| NFR-007 | Arabic RTL without corruption | Core 01 §7 | `dir="rtl"` in cards, dossier | `test_frontend_contains_evidence_mode_and_arabic_support` | IMPLEMENTED | S01 |
| NFR-008 | Runs in WSL, Linux, Docker | Core 01 §7 | scripts, Dockerfile | WSL `make ci` (S01 evidence); CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| NFR-009 | Domain calculations callable without web layer | Core 01 §7 | `decision_engine.analyze` | unit tests | IMPLEMENTED | S01 |
| NFR-010 | No uploaded Ministry data included | Core 01 §7 | synthetic only | leakage tests | IMPLEMENTED | S01 |

## C. Authority-manifest invariants (Manifest §6) and AGENTS.md non-negotiables

| ID | Invariant | Source | Implementation | Test | Status | Slice |
|---|---|---|---|---|---|---|
| INV-01 | Real branch uses public evidence only | Manifest §6.1; AGENTS #1 | `analyze_public` | leakage tests | IMPLEMENTED | S01 |
| INV-02 | Synthetic affects only `simulation_decision` | Manifest §6.2; AGENTS #1 | fingerprint assertion | `test_simulated_analysis_keeps_real_decision_identical` | IMPLEMENTED | S01 |
| INV-03 | Synthetic always Class D, DEMO_GENERATOR, flagged, disclosed | Manifest §6.3; AGENTS #2 | `synthetic_evidence_rows` | `test_every_synthetic_row_is_labeled` | IMPLEMENTED (display_label not policy-required) | S03 |
| INV-04 | Missing evidence stays unresolved in real branch | Manifest §6.4 | INVESTIGATE state; `missing_facts` | golden | IMPLEMENTED | S01 |
| INV-05 | ADVANCE blocked while identity/spec-demand/capability/hard gate is D/E | Manifest §6.5; AGENTS #3 | public branch | golden | IMPLEMENTED | S01 |
| INV-06 | Unknown capability never improves adjacency | Manifest §6.6; AGENTS #4 | λ penalty | `test_unknowns_cannot_improve_adjacency` | IMPLEMENTED | S01 |
| INV-07 | Thresholds from versioned config, no hidden constants | Manifest §6.7; AGENTS #7 | configured predicates plus GenUI threshold payload | `test_threshold_literals.py`; local/hosted validator wiring | IMPLEMENTED | S02 |
| INV-08 | Unit value never proves grade | Manifest §6.8; AGENTS #6 | R4-D text | `test_degraded_uv_never_claims_grade` | IMPLEMENTED | S01 |
| INV-09 | Lower-cost routes precede supported greenfield | Manifest §6.9; AGENTS #5 | route 5 selection; no route 7 | golden | IMPLEMENTED | S01 |
| INV-10 | Golden tests on hashed snapshots only, never live | Manifest §6.10; AGENTS #8 | repository loaders | integrity; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| INV-11 | Steel public INVESTIGATE; PP public REJECT preserved | Manifest §6.11; AGENTS #9 | golden fixtures | `test_golden_cases` | IMPLEMENTED | S01 |
| INV-12 | Computation autonomous, authorization not anonymous | Manifest §6.12; AGENTS #10 | governance screen; no approval endpoint | — | IMPLEMENTED | S01 |

## D. Test and acceptance gates (Core 09)

| ID | Gate / layer | Source | Present in v0.1.0 | Status | Slice |
|---|---|---|---|---|---|
| TL-01 | Integrity layer (hashes, no synthetic in public, mandatory metadata) | Core 09 §2.1 | `verify_integrity.py`, `test_integrity_contract`, `test_synthetic_isolation`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| TL-02 | Formula unit tests | Core 09 §2.2 | `test_capability_economics`, `test_rules`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| TL-03 | Rule tests (R1-D boundary, R2, R3, R4-F disabled, R4-D, R11) | Core 09 §2.3 | `test_threshold_boundaries.py`, explicit R3/R4-F/R11 tests in `test_rules.py`; evidence in `.workflow/slices/S02-threshold-governance/test_evidence.md` | IMPLEMENTED | S02 |
| TL-04 | Golden A, A-S, B, B-S | Core 09 §2.4 | `test_golden_cases`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| TL-05 | Extraction golden (4 fields exact, spans retained) | Core 09 §2.5 | `test_extraction`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| TL-06 | API tests | Core 09 §2.6 | `test_api`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| TL-07 | Frontend contract tests | Core 09 §2.7 | `test_static_frontend` (no "states display together" or "dossier action" check) | IMPLEMENTED (partial) | S04 |
| TL-08 | Threshold boundary tests below/equal/above | Core 09 §3 | complete S02 matrix in `test_threshold_boundaries.py`; evidence in `.workflow/slices/S02-threshold-governance/test_evidence.md` | IMPLEMENTED | S02 |
| TL-09 | Synthetic leakage assertions 1–7 | Core 09 §4 | 1,2,3,4,5,7 present; **6 (real dossier has no disclosure) absent** | IMPLEMENTED (partial) | S03 |
| GATE-A | Authority: methodology present, core complete, hashes pass | Core 09 §6 | yes | IMPLEMENTED | S01 |
| GATE-B | Data: snapshots validate; scenarios reconcile to public marginals | Core 09 §6 | reconciliation validator **absent** | IMPLEMENTED (partial) | S03 |
| GATE-C | Rules visible; thresholds from config | Core 09 §6 | configured predicates, unchanged goldens, AST validator; S02 evidence | IMPLEMENTED | S02 |
| GATE-D | Capability exact, unknown penalty, D\* gated | Core 09 §6 | yes | IMPLEMENTED | S01 |
| GATE-E | Economics unsupported first, S\* minimal, PP no support | Core 09 §6 | yes | IMPLEMENTED | S01 |
| GATE-F | Zero leakage, dual states, labelled rows | Core 09 §6 | yes | IMPLEMENTED | S01 |
| GATE-G | Product: frontend, toggle, adaptive manifest, dossier, Arabic | Core 09 §6 | yes (manual) | IMPLEMENTED | S05 |
| GATE-H | Release: build_manifests (approved only), verify, pytest, smoke all pass | Core 09 §6 | `.github/workflows/ci.yml`, `Makefile` `ci`; `build_manifests.py` not run because S01 has no governed change; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |

## E. Build-control requirements (owner mandate 2026-09-02)

| ID | Requirement | Implementation | Status | Slice |
|---|---|---|---|---|
| BC-01 | Git repository with default branch `main` on `baramiSG/Industrial_mvp` | S00 | PLANNED | S00 |
| BC-02 | No secrets, private data or prohibited files in Git; `.env.example` placeholders only | `.gitignore`, `scripts/check_prohibited_files.py`, `tests/test_prohibited_files.py`, S01 test evidence | TESTED | S00/S01 |
| BC-03 | Durable state: `.workflow/state.json`, slice records, control docs | created 2026-09-02 | IMPLEMENTED | S00 |
| BC-04 | CI on PR/push executing integrity, tests, smoke, scans | `.github/workflows/ci.yml`, `tests/test_ci_contract.py`; CI run 33569855956 (PR #1, head b0b2ab4): uv 3.12, uv 3.14, pip 3.12, Docker all pass | TESTED | S01 |
| BC-05 | Every slice: branch → plan → review → implement → review → independent review → gates → PR → CI → merge | slice records | PLANNED | all |
| BC-06 | Model separation (Implementer ≠ Supervisor; Reviewer ≠ Implementer) | ADR-002 | PLANNED | all |
| BC-07 | Requirements traceability maintained | this file | IMPLEMENTED | all |
| BC-08 | Final acceptance with different-model final reviewer and final documents | S05 | NOT_STARTED | S05 |
