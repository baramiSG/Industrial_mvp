# Requirements Traceability

Statuses used on this branch are `NOT_STARTED`, `PLANNED`, `IMPLEMENTED`, `TESTED`, `BLOCKED`, and `NOT_APPLICABLE`. `COMPLETE` is reserved for the Supervisor’s release-state PR after the S05 implementation merge and its default-branch CI are observed. A file or test existing is not execution evidence.

## Evidence registry

- **CI-S01-A:** run `33569855956`, PR #1, head `b0b2ab4`, four jobs green.
- **CI-S01-B:** run `33570112914`, PR #1 promotion head `030dbfe`, four jobs green.
- **CI-S02:** run `33573669072`, PR #2 head `1da6a0e`, four jobs green.
- **CI-S03:** run `33579923763`, PR #3 head `f6ef33b`, four jobs green.
- **CI-S04:** run `33584437086`, PR #4 head `bd72207`, four jobs green.
- **CI-ALL:** CI-S01-A, CI-S01-B, CI-S02, CI-S03, and CI-S04; these five runs repeatedly executed the full then-current pytest suite and required uv/pip/Docker jobs.
- **S05-FOCUSED:** `.workflow/slices/S05-final-acceptance/implementation_log.md` and `test_evidence.md`; includes observed RED→GREEN and characterization/NFR runs.
- **S05-LOCAL:** `.workflow/slices/S05-final-acceptance/acceptance_results.md` and `test_evidence.md`; cited only after the complete 42-step runner is observed.
- **S05-REVIEW/CI/MERGE:** `reviewer_findings.md`, `pr_record.md`, and `completion.md`; cited only after those external events are observed.

The Gate G/TL-07 proof scope is: live HTTP/API contracts plus static HTML/CSS/JavaScript checks for case selection and mode controls, dual states, adaptive approved-component manifest, dossier action and printable HTML, RTL markup, semantic native controls, responsive media rules, disclosure, and offline assets. No Playwright/real-browser interaction, paint, keyboard traversal, or print-render run is claimed; see KL-22.

## A. Functional requirements — Core 01 §6

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| FR-001 | Expose methodology version, snapshot ID, and as-of date for every case. | `config.authority_summary`, analysis, banner, dossier; `test_authority_disclosure.py`; CI-S03, CI-S04. | TESTED | S03 |
| FR-002 | Load R-rule thresholds from versioned YAML. | `config.thresholds_config`, rules/engine, `/api/thresholds`, recursive scanner; threshold tests; CI-S02–CI-S04. | TESTED | S02/S05 |
| FR-003 | Load sector weights and hard gates from versioned YAML. | `capability.evaluate_capability`; capability tests; CI-ALL. | TESTED | S01 |
| FR-004 | Load evidence classes and synthetic-isolation rules from policy. | `evidence_policy.v1.yaml` 1.1.0, typed validation and 422 mapping; isolation/API tests; CI-S03, CI-S04. | TESTED | S03 |
| FR-005 | Fail integrity verification on missing or changed governed files. | `scripts/verify_integrity.py`, `test_integrity_contract.py`; CI-ALL. | TESTED | S01 |
| FR-010 | Represent an opportunity independently of HS code. | Snapshot opportunity object and repository key; API/golden tests; CI-ALL. | TESTED | S01 |
| FR-011 | Public evidence states source, status, class, and synthetic flag. | Public evidence schema and ledger; isolation tests; CI-ALL. | TESTED | S01 |
| FR-012 | Public records explicitly set `synthetic_flag=false`. | `validate_public_evidence`; isolation tests; CI-ALL. | TESTED | S01 |
| FR-013 | Synthetic records carry flag, scenario ID, Class D, and generator source. | Policy validator and `synthetic_evidence_rows`; isolation/fidelity tests; CI-ALL. | TESTED | S01/S03/S04 |
| FR-014 | UI visually distinguishes public and synthetic rows. | `app.js` ledgers and `.synthetic-row`; static tests; CI-ALL. | TESTED | S01 |
| FR-015 | Retain contradictions rather than harmonising them away. | Steel evidence contradiction retained in analysis and S05 live-journey contract; CI-ALL, S05-LOCAL after observed. | TESTED | S01/S05 |
| FR-020 | Evaluate and display the complete R0–R12 contract. | Public ledger plus labelled simulated R6–R8; fidelity and boundary tests; CI-S04. | TESTED | S01/S04 |
| FR-021 | Every rule returns execution, fired, result, metrics, and effect. | `_rule`, synthetic row schema, live contract; fidelity tests; CI-S04. | TESTED | S01/S04 |
| FR-022 | Calculate R2 log changes and quantity contribution deterministically. | `rules.log_change`, `quantity_contribution_share`; worked-case tests; CI-ALL. | TESTED | S01 |
| FR-023 | R4-D never claims a cluster or grade. | R4-D result/effect; anti-grade test; CI-ALL. | TESTED | S01 |
| FR-024 | R9-S opens capability assessment but does not publish D*. | R9-S ledger and steel public golden; CI-ALL. | TESTED | S01 |
| FR-025 | R11 can reject unsupported generic-capacity claims. | Configured R11 predicate; boundary and PP golden tests; CI-S02–CI-S04. | TESTED | S02 |
| FR-030 | Effective qualified capacity equals the five-factor product. | `effective_qualified_capacity`; exact formula test; CI-ALL. | TESTED | S01 |
| FR-031 | Capability uses sector-specific weights. | `sector_profiles.v1.yaml`, `evaluate_capability`; route tests; CI-ALL. | TESTED | S01 |
| FR-032 | Unknown dimensions contribute U and receive λ penalty. | `evaluate_capability`; unknown-adjacency test; CI-ALL. | TESTED | S01 |
| FR-033 | D* is withheld below Kmin or with unresolved hard gates. | `publication_allowed`; Kmin/hard-gate boundary tests; CI-S02–CI-S04. | TESTED | S02 |
| FR-034 | Publish the four configured capability route bands. | `route_band`; below/equal/above matrix; CI-S02–CI-S04. | TESTED | S02 |
| FR-040 | Calculate unsupported economics before intervention. | `minimum_effective_support`; economics/golden tests; CI-ALL. | TESTED | S01 |
| FR-041 | Calculate NPV and IRR deterministically. | `economics.npv` and `irr`; exact economics tests; CI-ALL. | TESTED | S01 |
| FR-042 | S* is the minimum configured support step satisfying hurdles. | Support search and SAR 18m exact test; CI-ALL. | TESTED | S01 |
| FR-043 | Incremental national value is relative to no action. | `incremental_national_value`; component/value tests; CI-ALL. | TESTED | S01 |
| FR-044 | Show post-entry capacity/downside-demand ratio. | `decision_engine.competition_warning`, `_simulation_economics`, `_simulate`; configured boundary and payload tests; CI-S02, CI-S04, S05-LOCAL after observed. | TESTED | S02/S04/S05 |
| FR-045 | EVSI identifies whether a named evidence action is worth obtaining. | `approximate_evsi`; national-value/EVSI test; CI-ALL. | TESTED | S01 |
| FR-050 | Public decisions use public evidence only. | `analyze_public`, public repository, validation; isolation/golden tests; CI-ALL. | TESTED | S01 |
| FR-051 | Simulation does not mutate public decisions. | fingerprint guard and isolated public copy; isolation tests; CI-ALL. | TESTED | S01 |
| FR-052 | Decisions include state, route, rationale, confidence, conditions, and kill conditions. | public selector and scenario narratives; fidelity/golden tests; CI-S04. | TESTED | S04 |
| FR-053 | Real `ADVANCE` is blocked by decision-critical D/E evidence. | Public selector emits only `REJECT`/`INVESTIGATE`; goldens; CI-ALL. | TESTED | S01 |
| FR-054 | No-action and brownfield routes precede supported greenfield. | `_simulate` route 0 before route 5; no route 7; conjunction tests; CI-S04. | TESTED | S01/S04 |
| FR-060 | Backend emits a constrained UI manifest. | `build_ui_manifest`, `/ui-manifest`; API tests; CI-ALL. | TESTED | S01 |
| FR-061 | Manifest uses approved component types only. | Fixed registry and guardrails; approved-set test; CI-ALL. | TESTED | S01 |
| FR-062 | Omit economics panels when economics is unavailable. | Conditional manifest component; public omission test; CI-ALL. | TESTED | S01 |
| FR-063 | Runtime model output cannot generate executable browser code. | Fixed renderer registry and guardrail; API/static tests; CI-ALL. | TESTED | S01 |
| FR-064 | Export machine-readable and printable dossiers. | `dossier.py` and JSON/HTML routes; exact dossier tests; CI-ALL, S05-FOCUSED. | TESTED | S01/S05 |
| FR-070 | Keep Arabic/English source spans on normalized fields. | Extraction contract; 4/4 test; CI-ALL. | TESTED | S01 |
| FR-071 | Support standard, coating, dimensions, and environment fields. | Offline extractor schema; golden test; CI-ALL. | TESTED | S01 |
| FR-072 | Offline extractor passes the labelled golden set. | `run_extraction_golden_set`; exact 4/4 test; CI-ALL. | TESTED | S01 |
| FR-073 | Future production LLM adapter passes the same gate. | No production adapter exists; control note and Core 08 boundary retained. | NOT_APPLICABLE (production) | — |

## B. Non-functional requirements — Core 01 §7

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| NFR-001 | Reproducible from frozen files and configuration. | Hashed snapshots/config, integrity and goldens; CI-ALL. | TESTED | S01 |
| NFR-002 | Derived metrics have deterministic formulas and source pointers. | Rules/capability/economics modules and formula tests; CI-ALL. | TESTED | S01 |
| NFR-003 | Unknown hard gates reduce permission. | Capability publication conjunction; hard-gate test; CI-ALL. | TESTED | S01 |
| NFR-004 | Packaged demo runs without API keys or live data calls. | Offline loaders/static assets; CDN test and CI-ALL. | TESTED | S01 |
| NFR-005 | Warm loaded-case API responses normally complete below 250 ms. | `tests/test_performance.py`: one excluded warm-up and median of five real TestClient calls on all 18 routes; S05-FOCUSED. Live localhost medians are added by S05-LOCAL. | TESTED | S05 |
| NFR-006 | Semantic, high-contrast, keyboard-reachable interface. | Native buttons/select/labels and contrast/static contracts; CI-ALL. Real traversal is outside KL-22. | TESTED | S01/S05 |
| NFR-007 | Arabic text renders RTL without corruption. | RTL markup and source spans; static test; CI-ALL. | TESTED | S01 |
| NFR-008 | Demo runs in WSL, native Linux, and Docker. | Run scripts, pip/uv paths, Dockerfile; CI-ALL. | TESTED | S01 |
| NFR-009 | Domain calculations are callable without web layer. | `decision_engine.analyze` and direct unit callers; CI-ALL. | TESTED | S01 |
| NFR-010 | No uploaded Ministry data is packaged. | Public and explicit synthetic-only artifacts; isolation/prohibited tests; CI-ALL. | TESTED | S01 |

## C. Authority invariants

| ID | Invariant | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| INV-01 | Real branch uses public evidence only. | Public loader/analysis and isolation tests; CI-ALL. | TESTED | S01 |
| INV-02 | Synthetic evidence affects only simulation state. | fingerprint/back-test guards; fidelity tests; CI-S04. | TESTED | S01/S04 |
| INV-03 | Synthetic records are Class D, generator-sourced, flagged, and disclosed. | Policy validation and exact ledger tests; CI-S03, CI-S04. | TESTED | S03 |
| INV-04 | Missing real evidence remains unresolved. | Public D* gate/data unlocks and dossier; CI-S03, CI-S04. | TESTED | S03 |
| INV-05 | Decision-critical D/E evidence blocks real `ADVANCE`. | Public selector and goldens; CI-ALL. | TESTED | S01 |
| INV-06 | Unknown capability cannot improve adjacency. | λ/U implementation and test; CI-ALL. | TESTED | S01 |
| INV-07 | Thresholds are versioned configuration, not hidden constants. | Config predicates, recursive scanner and boundaries; CI-S02–CI-S04, S05-FOCUSED. | TESTED | S02/S05 |
| INV-08 | Unit-value dispersion never proves grade. | R4-D wording and anti-grade test; CI-ALL. | TESTED | S01 |
| INV-09 | Lower-cost/no-action routes precede supported greenfield. | Route order/no route 7 tests; CI-S04. | TESTED | S01/S04 |
| INV-10 | Goldens use hashed local snapshots only. | Repository loaders/integrity; CI-ALL. | TESTED | S01 |
| INV-11 | Steel public `INVESTIGATE` and PP public `REJECT` remain exact. | `test_golden_cases.py`; CI-ALL. | TESTED | S01 |
| INV-12 | Calculation is autonomous; authorization is accountable. | Read-only GET API and governance copy; static/API tests; CI-ALL. | TESTED | S01 |

## D. Test layers and acceptance gates — Core 09

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| TL-01 | Integrity layer. | Integrity, mandatory metadata, isolation and scenario validators; CI-ALL. | TESTED | S01/S03 |
| TL-02 | Formula unit tests. | Rules/capability/economics suites; CI-ALL. | TESTED | S01 |
| TL-03 | Rule tests. | R1-D/R2/R3/R4/R11 and boundary suites; CI-S02–CI-S04. | TESTED | S02 |
| TL-04 | Four golden decision combinations. | Golden and ground-truth tests; CI-ALL. | TESTED | S01/S04 |
| TL-05 | Four-field bilingual extraction golden. | Extraction suite; CI-ALL. | TESTED | S01 |
| TL-06 | API tests. | `test_api.py`, including list 404 and integrity 422; CI-ALL, S05-FOCUSED. | TESTED | S01/S05 |
| TL-07 | Frontend contract checks. | Scope statement above; static suite and live payload contracts; CI-S04, S05-LOCAL after observed; KL-22. | TESTED | S04/S05 |
| TL-08 | Below/equal/above threshold boundaries. | `test_threshold_boundaries.py`; CI-S02–CI-S04. | TESTED | S02 |
| TL-09 | Synthetic leakage assertions 1–7. | Isolation, dossier, API, and fidelity suites; CI-S03, CI-S04. | TESTED | S03/S04 |
| GATE-A | Authority/core present; hashes pass. | Integrity and protected-byte audit; CI-ALL, S05-LOCAL after observed. | TESTED | S01/S05 |
| GATE-B | Data/scenarios validate, reconcile, and back-test. | `validate_scenarios.py`; CI-S03, CI-S04. | TESTED | S03/S04 |
| GATE-C | Rules visible; thresholds config-sourced; goldens exact. | Rule/golden suites and recursive scanner; CI-S02–CI-S04. | TESTED | S02/S05 |
| GATE-D | Capacity/unknown/D* gates are exact. | Capability suites; CI-ALL. | TESTED | S01 |
| GATE-E | Unsupported economics first; S* minimal; PP gets no support. | Economics and golden suites; CI-ALL. | TESTED | S01 |
| GATE-F | Zero leakage, dual states, labelled synthetic rows. | Isolation/fidelity/dossier suites; CI-S03, CI-S04. | TESTED | S03/S04 |
| GATE-G | Product controls, adaptive manifest, dossier, Arabic, responsiveness. | Exact API/static scope statement above; CI-S04, S05-LOCAL after observed; KL-22. | TESTED | S04/S05 |
| GATE-H | Authorized release gates only. | Authorized generators ran only in S02–S04. S05 has no governed change and does not run a generator; make/clean-pip/integrity/Gate B/pytest/smoke/Docker are S05-LOCAL evidence after observed. | TESTED | S01–S05 |

## E. Build-control requirements

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| BC-01 | Git repository with default `main` at `baramiSG/Industrial_mvp`. | S00 commit `0731ae5`; subsequent PR/merge records and CI registry. | TESTED | S00 |
| BC-02 | No secrets, private data, or prohibited files in Git. | Scanner/tests and CI-ALL. | TESTED | S00/S01 |
| BC-03 | Durable machine/slice/control state. | `.workflow/state.json`, slice records, control documents; S00–S04 records audited. | TESTED | S00–S05 |
| BC-04 | PR/push CI executes all required gates. | Workflow contract and CI-ALL. | TESTED | S01 |
| BC-05 | Each slice follows plan, review, independent review, gates, PR, CI, merge. | S01–S04 completion/review/PR records; S05 lifecycle remains in progress. | TESTED | all |
| BC-06 | Implementer, Supervisor, and Reviewer model separation. | ADR-002 and S01–S05 state/slice assignments. | TESTED | all |
| BC-07 | Requirements traceability is maintained. | This row-level document and S05 docs audit. | TESTED | all |
| BC-08 | Final acceptance, final documents, and different-model holistic review. | Runner/tests/docs are implemented; final reviewer, hosted CI, merge, and release-state facts remain Supervisor-controlled. | IMPLEMENTED | S05 |

## F. Packaged MVP definition of done — Core 09 §7

The complete S05 local harness run `20260902T033607Z-17501` observed the associated steps with all 42 exit codes zero. These rows are promoted no higher than `TESTED`; external review, hosted CI, merge, and release-state promotion remain separate.

| ID | Requirement | Implementation / required evidence | Status | Slice |
|---|---|---|---|---|
| DOD-01 | Starts from a clean Python environment with documented commands. | Clean venv create/install/gates and operator/deployment guides; S05-LOCAL steps 03–12. | TESTED | S05 |
| DOD-02 | No external key is required. | Offline package/install/runtime proof; S05-LOCAL steps 03–27. | TESTED | S05 |
| DOD-03 | All tests pass. | `make ci` and clean-pip pytest, each 260 passed; S05-LOCAL steps 02 and 11. | TESTED | S05 |
| DOD-04 | Integrity passes. | Locked and clean-pip integrity plus final protected audit; S05-LOCAL steps 09, 34–36, 41. | TESTED | S05 |
| DOD-05 | Two public golden outcomes are exact. | Golden suite and live HTTP states; S05-LOCAL steps 02, 11, 20. | TESTED | S05 |
| DOD-06 | Steel simulated transition is exact and disclosed. | Live detail/manifest/dossier contracts; S05-LOCAL step 20. | TESTED | S05 |
| DOD-07 | PP simulation still rejects support. | Live state/route/no-support contracts; S05-LOCAL step 20. | TESTED | S05 |
| DOD-08 | Interface is usable at desktop/tablet widths. | API/static scoped proof only; KL-22; S05-LOCAL steps 02, 11, 20. | TESTED | S05 |
| DOD-09 | Dossier exists in JSON and printable HTML. | Four case/mode live contracts; S05-LOCAL step 20. | TESTED | S05 |
| DOD-10 | Documentation and source are included in one zip. | CRC/member/prohibited-artifact archive audit; S05-LOCAL steps 38–40. | TESTED | S05 |

## G. MVP success criteria — Core 01 §9

| ID | Observable success criterion | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| SC-01 | Refuses unsupported factory recommendation. | PP public/simulated `REJECT`, route 0, no support; CI-ALL. | TESTED | S01/S04 |
| SC-02 | Public evidence produces meaningful decisions and precise evidence requests. | Steel public `INVESTIGATE`, `data_unlocks`, dossier; CI-ALL. | TESTED | S01 |
| SC-03 | Ministry-shaped inputs change named gates, not a generic score. | Dual state, capacity, D*, economics, rule and reconciliation outputs; CI-S04. | TESTED | S04 |
| SC-04 | Synthetic evidence is honest and controlled. | Class/source/flag/label/disclosure and fingerprint tests; CI-S03, CI-S04. | TESTED | S03/S04 |
| SC-05 | Calculations, thresholds, and evidence are inspectable. | Threshold endpoint, rule ledger, authority and evidence objects; CI-ALL. | TESTED | S01–S04 |
| SC-06 | Output is a route and Decision Dossier, not a ranking. | Decision route plus JSON/HTML dossier contracts; CI-ALL. | TESTED | S01 |

## Branch and release-state rules

1. No row on the S05 implementation branch is promoted above `TESTED`.
2. DOD-01–DOD-10 move to `TESTED` only after the matching first complete S05 local harness steps are observed.
3. BC-08 moves to `TESTED` only after the different-model final reviewer reports zero unresolved findings and the required final documents exist.
4. `FR-073` remains `NOT_APPLICABLE (production)`.
5. After the S05 implementation PR merges and default-branch CI for that merge is green, the Supervisor opens the narrow release-state PR. Only that PR may promote eligible rows to `COMPLETE`, record final CI/merge facts, and update durable project state.
