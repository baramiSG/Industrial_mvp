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
- **S06-CI:** PR #8 run `33602331107` (head `8c56a71`) and default-branch run `33602662668` (merge `6d00e27`), five jobs green each, including `browser / Chromium / Python 3.12` with 62 Chromium nodes passed.
- **S06-LOCAL:** `.workflow/slices/S06-browser-acceptance-harness/test_evidence.md` and `implementation_log.md`; local `make e2e` observed 17 named tests / 62 Chromium nodes passed, with zero ordinary-journey collector errors, zero axe violations after focused UI defect fixes, four valid PDFs in the case/mode matrix, and 40 indexed documentary references. This entry is local implementation evidence only; it does not claim review, hosted CI, merge, closure, or release.
- **S07-CI:** PR #9 run `33622991390` (head `104dbac`) and default-branch run `33623528164` (merge `9f045a4`), five jobs green each, including `browser / Chromium / Python 3.12` with 118 functional + 4 visual Chromium nodes passed against the canonical baselines.
- **S07-LOCAL:** `.workflow/slices/S07-bilingual-interface-foundation/test_evidence.md` and `implementation_log.md`; local evidence covers catalogue/policy parity, token and ES-module scanners, exact vendored-font provenance, 118 bilingual functional Chromium nodes, four visual nodes comparing 40 canonical lossless WebPs, both Python versions, integrity/Gate B/smoke, and unchanged public/simulated goldens. This is implementation evidence only; it does not claim independent approval, hosted CI, PR, merge, closure, or release.
- **S08-CI:** PR #10 (head `38f033a`) five checks green incl. `browser / Chromium / Python 3.12`; default-branch run `33637594756` (merge `8b6d55c`) five jobs green.
- **S08-LOCAL:** `.workflow/slices/S08-snapshot-v2-computed-rules/test_evidence.md` and `implementation_log.md`; local evidence covers schema 2.0.0 validation/history, exact migration equivalence, computed R1-D/R2/R3/R4-D/R5/R9-S/R10/R11 behavior and boundaries, contradiction-register isolation/localization, host-owned canonical baseline regeneration, both Python versions, integrity/Gate B/smoke, and unchanged public/simulated goldens. This is implementation evidence only; it does not claim independent approval, hosted CI, PR, merge, effective limitation closure, or release.
- **S09-LOCAL:** `.workflow/slices/S09-public-decision-and-profiles/test_evidence.md` and `implementation_log.md`; local evidence covers PublicSnapshot 2.1.0 and contract removal, four evidence-class assessments and the source-independent ADVANCE gate, six exclusions, one-primary gap taxonomy, amended-I1 state branches, routes 0–8 hypotheses and amended-I5 selection, five sector profiles, predicate-selected evidence needs, bilingual public narratives, signals module and ADVANCE support guard, typed rejection narratives, route-determination INVESTIGATE, confidence cap, and unchanged scenario-authored simulation narratives/numbers. Five host-owned canonical baseline executions are recorded: the initial capture; one route-spacing defect correction; two provenance refreshes after methodology self-audit; and the correction-round refresh under `S09-generalized-public-decision-corrections`, each preceded by a complete 118-node functional pass. This registry item remains local execution evidence; independent approval and delivery are recorded separately in S09-CI.
- **S09-CI:** PR #12 head `f772da6d4f23d3e1c4263e577fbc5a756b35a7ad`, run `33754472700`, and default-branch merge `66d4835d8c13b0421de271222e2422aff0cb5eb7`, run `33755119710`; all five jobs green on both exact SHAs. Independent Grok approval had zero findings on tree `313edc480668d4e1201ba0c5a46525ed0000feb5`; post-merge integrity passed.
- **S10-LOCAL:** `.workflow/slices/S10-generalized-simulation/test_evidence.md` and `implementation_log.md`; local evidence covers scenario contract 2.0.0, generalized simulated routes 0–7 and MONITOR, route-8 `GRAPH_REQUIRED` contract, simulated R5/R8 ledger semantics, ten Gate B reconciliation checks, bilingual simulated narratives, `class_if_confirmed` ADVANCE gating, ten fixture proofs, migration equivalence with byte-identical historical 1.1.0 files, unchanged four frozen outcomes/numbers, and canonical visual baseline refresh `S10-generalized-simulation` with public workspace oracles restored byte-identical to base `66d4835`. Two justified `build_manifests.py` runs are recorded: candidate 2 (T13 initial) and candidate 3 (Core 01 T12 correction). This registry item remains local execution evidence; independent approval and delivery are recorded separately in S10-CI.
- **S10-CI:** PR #13 head `4b8a689ab36d65a8ff79864d236272b047eab8f2`, run `33794229014`, and default-branch merge `a610b49b1f9a34ffb6430e92b7a6cb7fafb82ca4`, run `33794894041`; all five jobs green on both exact SHAs. Independent Grok approval had zero findings on tree `4b43fda352910f5d5f056a0f603d7ec907b8cb35`; post-merge integrity, 62 focused regressions and smoke passed.

The Gate G/TL-07 proof scope now combines the preserved live HTTP/API and static contracts with Real Chromium interaction: case cards/select/hero, both evidence modes, adaptive manifests, dossier popup and clipboard, print media and PDF bytes, 15-control Tab order with visible focus, zero axe WCAG 2.1 A/AA violations, Arabic RTL/non-tofu rendering, and overflow/actionability at 1440×900, 1024×768, 1920×1080, and 2560×1440. S06 screenshots are documentary references only and are never compared; governed visual-regression oracles begin in S07 under ruling R-4.

## A. Functional requirements — Core 01 §6

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| FR-001 | Expose methodology version, snapshot ID, and as-of date for every case. | `config.authority_summary`, analysis, banner, dossier; `test_authority_disclosure.py`; CI-S03, CI-S04. | COMPLETE | S03 |
| FR-002 | Load R-rule thresholds from versioned YAML. | `config.thresholds_config`, rules/engine, `/api/thresholds`, recursive scanner; threshold tests; CI-S02–CI-S04. | COMPLETE | S02/S05 |
| FR-003 | Load sector weights and hard gates from versioned YAML. | `capability.evaluate_capability`; capability tests; CI-ALL. | COMPLETE | S01 |
| FR-004 | Load evidence classes and synthetic-isolation rules from policy. | `evidence_policy.v1.yaml` 1.1.0, typed validation and 422 mapping; isolation/API tests; CI-S03, CI-S04. | COMPLETE | S03 |
| FR-005 | Fail integrity verification on missing or changed governed files. | `scripts/verify_integrity.py`, `test_integrity_contract.py`; CI-ALL. | COMPLETE | S01 |
| FR-010 | Represent an opportunity independently of HS code. | Snapshot opportunity object and repository key; API/golden tests; CI-ALL. | COMPLETE | S01 |
| FR-011 | Public evidence states source, status, class, and synthetic flag. | Public evidence schema and ledger; isolation tests; CI-ALL. | COMPLETE | S01 |
| FR-012 | Public records explicitly set `synthetic_flag=false`. | `validate_public_evidence`; isolation tests; CI-ALL. | COMPLETE | S01 |
| FR-013 | Synthetic records carry flag, scenario ID, Class D, and generator source. | Policy validator and `synthetic_evidence_rows`; isolation/fidelity tests; CI-ALL. | COMPLETE | S01/S03/S04 |
| FR-014 | UI visually distinguishes public and synthetic rows. | `app.js` ledgers and `.synthetic-row`; static tests; CI-ALL. | COMPLETE | S01 |
| FR-015 | Retain contradictions rather than harmonising them away. | Steel evidence contradiction retained in analysis and S05 live-journey contract; CI-ALL, S05-LOCAL after observed. | COMPLETE | S01/S05 |
| FR-020 | Evaluate and display the complete R0–R12 contract. | Public ledger plus labelled simulated R6–R8; S08 replaces authored public flags with schema-v2 evidence derivation; fidelity, migration and boundary tests; CI-S04, S08-LOCAL. | COMPLETE | S01/S04/S08 |
| FR-021 | Every rule returns execution, fired, result, metrics, and effect. | `_rule`, synthetic row schema, live v2 contract and complete ordered migration diff; fidelity tests; CI-S04, S08-LOCAL. | COMPLETE | S01/S04/S08 |
| FR-022 | Calculate R2 log changes and quantity contribution deterministically. | `rules.log_change`, `quantity_contribution_share`, observed-span `compound_annual_growth`; one/two-year, missing-year and worked-case tests; CI-ALL, S08-LOCAL. | COMPLETE | S01/S08 |
| FR-023 | R4-D never claims a cluster or grade. | Typed row/disclosure dispersion, dedicated coverage gate, protected result/effect text and anti-grade tests; CI-ALL, S08-LOCAL. | COMPLETE | S01/S08 |
| FR-024 | R9-S opens capability assessment but does not publish D*. | Typed process-family/signal/known-failure derivation and steel public golden; CI-ALL, S08-LOCAL. | COMPLETE | S01/S08 |
| FR-025 | R11 can reject unsupported generic-capacity claims. | Computed gross ratio plus observed A/B/C nameplate predicate, strict boundaries, PP/steel/unavailable tests and computed selector; CI-S02–CI-S04, S08-LOCAL. | COMPLETE | S02/S08 |
| FR-030 | Effective qualified capacity equals the five-factor product. | `effective_qualified_capacity`; exact formula test; CI-ALL. | COMPLETE | S01 |
| FR-031 | Capability uses sector-specific weights. | `sector_profiles.v1.yaml`, `evaluate_capability`; route tests; CI-ALL. | COMPLETE | S01 |
| FR-032 | Unknown dimensions contribute U and receive λ penalty. | `evaluate_capability`; unknown-adjacency test; CI-ALL. | COMPLETE | S01 |
| FR-033 | D* is withheld below Kmin or with unresolved hard gates. | `publication_allowed`; Kmin/hard-gate boundary tests; CI-S02–CI-S04. | COMPLETE | S02 |
| FR-034 | Publish the four configured capability route bands. | `route_band`; below/equal/above matrix; CI-S02–CI-S04. | COMPLETE | S02 |
| FR-040 | Calculate unsupported economics before intervention. | `minimum_effective_support`; economics/golden tests; CI-ALL. | COMPLETE | S01 |
| FR-041 | Calculate NPV and IRR deterministically. | `economics.npv` and `irr`; exact economics tests; CI-ALL. | COMPLETE | S01 |
| FR-042 | S* is the minimum configured support step satisfying hurdles. | Support search and SAR 18m exact test; CI-ALL. | COMPLETE | S01 |
| FR-043 | Incremental national value is relative to no action. | `incremental_national_value`; component/value tests; CI-ALL. | COMPLETE | S01 |
| FR-044 | Show post-entry capacity/downside-demand ratio. | `decision_engine.competition_warning`, `_simulation_economics`, `_simulate`; configured boundary and payload tests; CI-S02, CI-S04, S05-LOCAL after observed. | COMPLETE | S02/S04/S05 |
| FR-045 | EVSI identifies whether a named evidence action is worth obtaining. | `approximate_evsi`; national-value/EVSI test; CI-ALL. | COMPLETE | S01 |
| FR-050 | Public decisions use public evidence only. | `analyze_public`, public repository, validation; isolation/golden tests; CI-ALL. | COMPLETE | S01 |
| FR-051 | Simulation does not mutate public decisions. | fingerprint guard and isolated public copy; isolation tests; CI-ALL. | COMPLETE | S01 |
| FR-052 | Decisions include state, route, rationale, confidence, conditions, and kill conditions. | public selector and scenario narratives; fidelity/golden tests; CI-S04. | COMPLETE | S04 |
| FR-053 | Real `ADVANCE` is blocked by decision-critical D/E evidence. | Public selector emits only `REJECT`/`INVESTIGATE`; goldens; CI-ALL. | COMPLETE | S01 |
| FR-054 | No-action and brownfield routes precede supported greenfield. | `_simulate` route 0 before route 5; no route 7; conjunction tests; CI-S04. | COMPLETE | S01/S04 |
| FR-060 | Backend emits a constrained UI manifest. | `build_ui_manifest`, `/ui-manifest`; API tests; CI-ALL. | COMPLETE | S01 |
| FR-061 | Manifest uses approved component types only. | Fixed registry and guardrails; approved-set test; CI-ALL. | COMPLETE | S01 |
| FR-062 | Omit economics panels when economics is unavailable. | Conditional manifest component; public omission test; CI-ALL. | COMPLETE | S01 |
| FR-063 | Runtime model output cannot generate executable browser code. | Fixed renderer registry and guardrail; API/static tests; CI-ALL. | COMPLETE | S01 |
| FR-064 | Export machine-readable and printable dossiers. | `dossier.py` and JSON/HTML routes; exact dossier tests; CI-ALL, S05-FOCUSED. | COMPLETE | S01/S05 |
| FR-070 | Keep Arabic/English source spans on normalized fields. | Extraction contract; 4/4 test; CI-ALL. | COMPLETE | S01 |
| FR-071 | Support standard, coating, dimensions, and environment fields. | Offline extractor schema; golden test; CI-ALL. | COMPLETE | S01 |
| FR-072 | Offline extractor passes the labelled golden set. | `run_extraction_golden_set`; exact 4/4 test; CI-ALL. | COMPLETE | S01 |
| FR-073 | Future production LLM adapter passes the same gate. | No production adapter exists; control note and Core 08 boundary retained. | NOT_APPLICABLE (production) | — |

## B. Non-functional requirements — Core 01 §7

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| NFR-001 | Reproducible from frozen files and configuration. | Hashed snapshots/config, integrity and goldens; CI-ALL. | COMPLETE | S01 |
| NFR-002 | Derived metrics have deterministic formulas and source pointers. | Rules/capability/economics modules and formula tests; CI-ALL. | COMPLETE | S01 |
| NFR-003 | Unknown hard gates reduce permission. | Capability publication conjunction; hard-gate test; CI-ALL. | COMPLETE | S01 |
| NFR-004 | Packaged demo runs without API keys or live data calls. | Offline loaders/static assets; CDN test and CI-ALL. | COMPLETE | S01 |
| NFR-005 | Warm loaded-case API responses normally complete below 250 ms. | `tests/test_performance.py`: one excluded warm-up and median of five real TestClient calls on all 18 routes; S05-FOCUSED. Live localhost medians are added by S05-LOCAL. | COMPLETE | S05 |
| NFR-006 | Semantic, high-contrast, keyboard-reachable interface. | Native controls and static contrast contracts; S06-LOCAL observes all 15 controls in DOM Tab order with `:focus-visible` and changed focus signatures at eight mode/viewport combinations, plus zero workspace/dossier axe violations. | COMPLETE | S01/S05/S06 |
| NFR-007 | Arabic text renders RTL without corruption. | RTL markup/source spans plus S06-LOCAL computed `direction: rtl`, non-empty/non-zero nodes, `document.fonts.ready`, fontconfig, canvas Arabic-vs-U+FFFD differentiation, and distinct glyph signatures. | COMPLETE | S01/S06 |
| NFR-008 | Demo runs in WSL, native Linux, and Docker. | Run scripts, pip/uv paths, Dockerfile; CI-ALL. | COMPLETE | S01 |
| NFR-009 | Domain calculations are callable without web layer. | `decision_engine.analyze` and direct unit callers; CI-ALL. | COMPLETE | S01 |
| NFR-010 | No uploaded Ministry data is packaged. | Public and explicit synthetic-only artifacts; isolation/prohibited tests; CI-ALL. | COMPLETE | S01 |

## C. Authority invariants

| ID | Invariant | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| INV-01 | Real branch uses public evidence only. | Public loader/analysis and isolation tests; CI-ALL. | COMPLETE | S01 |
| INV-02 | Synthetic evidence affects only simulation state. | fingerprint/back-test guards; fidelity tests; CI-S04. | COMPLETE | S01/S04 |
| INV-03 | Synthetic records are Class D, generator-sourced, flagged, and disclosed. | Policy validation and exact ledger tests; CI-S03, CI-S04. | COMPLETE | S03 |
| INV-04 | Missing real evidence remains unresolved. | Public D* gate/data unlocks and dossier; CI-S03, CI-S04. | COMPLETE | S03 |
| INV-05 | Decision-critical D/E evidence blocks real `ADVANCE`. | Public selector, class-if-confirmed simulated gate and goldens; `tests/test_simulation_generalized.py`; CI-ALL, S10-LOCAL. | COMPLETE | S01/S10 |
| INV-06 | Unknown capability cannot improve adjacency. | λ/U implementation and test; CI-ALL. | COMPLETE | S01 |
| INV-07 | Thresholds are versioned configuration, not hidden constants. | Config predicates, recursive scanner and boundaries; CI-S02–CI-S04, S05-FOCUSED. | COMPLETE | S02/S05 |
| INV-08 | Unit-value dispersion never proves grade. | R4-D row/disclosure wording, non-confirmed outlier candidate and anti-grade tests; CI-ALL, S08-LOCAL. | COMPLETE | S01/S08 |
| INV-09 | Lower-cost/no-action routes precede supported greenfield. | Route order/no route 7 tests; simulated route-selection fixtures; CI-S04, S10-LOCAL. | COMPLETE | S01/S04/S10 |
| INV-10 | Goldens use hashed local snapshots only. | Repository loaders/integrity; CI-ALL. | COMPLETE | S01 |
| INV-11 | Steel public `INVESTIGATE` and PP public `REJECT` remain exact. | `test_golden_cases.py`; CI-ALL. | COMPLETE | S01 |
| INV-12 | Calculation is autonomous; authorization is accountable. | Read-only GET API and governance copy; static/API tests; CI-ALL. | COMPLETE | S01 |

## D. Test layers and acceptance gates — Core 09

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| TL-01 | Integrity layer. | Integrity, PublicSnapshot v2 schema/history/passports, mandatory metadata, isolation and scenario validators; CI-ALL, S08-LOCAL. | COMPLETE | S01/S03/S08 |
| TL-02 | Formula unit tests. | Rules/capability/economics plus S08 CAGR/concentration/dispersion/domestic-flow/ratio/nameplate suites; CI-ALL, S08-LOCAL. | COMPLETE | S01/S08 |
| TL-03 | Rule tests. | Evidence-derived R1-D/R2/R3/R4-D/R5/R9-S/R10/R11, migration and boundary suites; CI-S02–CI-S04, S08-LOCAL. | COMPLETE | S02/S08 |
| TL-04 | Four golden decision combinations. | Golden, ground-truth and schema-migration equality tests; CI-ALL, S08-LOCAL. | COMPLETE | S01/S04/S08 |
| TL-05 | Four-field bilingual extraction golden. | Extraction suite; CI-ALL. | COMPLETE | S01 |
| TL-06 | API tests. | `test_api.py`, including list 404 and integrity 422; CI-ALL, S05-FOCUSED. | COMPLETE | S01/S05 |
| TL-07 | Frontend contract checks. | Scope statement above; preserved static/live contracts plus S06-LOCAL real-Chromium interaction, accessibility, network, RTL, responsive, print/PDF, and documentary-reference proof. | COMPLETE | S04/S05/S06 |
| TL-08 | Below/equal/above threshold boundaries. | `test_threshold_boundaries.py`: S08 adds both R3 bases, observed-span CAGR, R4-D coverage, R5 penetration and R11 capability conjunction; CI-S02–CI-S04, S08-LOCAL. | COMPLETE | S02/S08 |
| TL-09 | Synthetic leakage assertions 1–7. | Isolation, dossier, API, fidelity and contradiction-register separation suites; CI-S03, CI-S04, S08-LOCAL. | COMPLETE | S03/S04/S08 |
| GATE-A | Authority/core present; hashes pass. | Integrity and protected-byte audit; CI-ALL, S05-LOCAL after observed. | COMPLETE | S01/S05 |
| GATE-B | Data/scenarios validate, reconcile, and back-test. | `validate_scenarios.py`; CI-S03, CI-S04. | COMPLETE | S03/S04 |
| GATE-C | Rules visible; thresholds config-sourced; goldens exact. | Rule/golden suites and recursive scanner; CI-S02–CI-S04. | COMPLETE | S02/S05 |
| GATE-D | Capacity/unknown/D* gates are exact. | Capability suites; CI-ALL. | COMPLETE | S01 |
| GATE-E | Unsupported economics first; S* minimal; PP gets no support. | Economics and golden suites; CI-ALL. | COMPLETE | S01 |
| GATE-F | Zero leakage, dual states, labelled synthetic rows. | Isolation/fidelity/dossier suites; CI-S03, CI-S04. | COMPLETE | S03/S04 |
| GATE-G | Product controls, adaptive manifest, dossier, Arabic, responsiveness. | Exact combined scope statement above; S06-LOCAL observes every existing control path, adaptive states, popup/clipboard, axe/focus, Arabic glyphs, print/PDF, and four widths in Chromium. | COMPLETE | S04/S05/S06 |
| GATE-H | Authorized release gates only. | Authorized generators ran only in S02–S04. S05 has no governed change and does not run a generator; make/clean-pip/integrity/Gate B/pytest/smoke/Docker are S05-LOCAL evidence after observed. | COMPLETE | S01–S05 |

## E. Build-control requirements

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| BC-01 | Git repository with default `main` at `baramiSG/Industrial_mvp`. | S00 commit `0731ae5`; subsequent PR/merge records and CI registry. | COMPLETE | S00 |
| BC-02 | No secrets, private data, or prohibited files in Git. | Scanner/tests and CI-ALL. | COMPLETE | S00/S01 |
| BC-03 | Durable machine/slice/control state. | `.workflow/state.json`, slice records, control documents; S00–S04 records audited. | COMPLETE | S00–S05 |
| BC-04 | PR/push CI executes all required gates. | Workflow contract and CI-ALL. | COMPLETE | S01 |
| BC-05 | Each slice follows plan, review, independent review, gates, PR, CI, merge. | S01–S04 completion/review/PR records; S05 lifecycle remains in progress. | COMPLETE | all |
| BC-06 | Implementer, Supervisor, and Reviewer model separation. | ADR-002 and S01–S05 state/slice assignments. | COMPLETE | all |
| BC-07 | Requirements traceability is maintained. | This row-level document and S05 docs audit. | COMPLETE | all |
| BC-08 | Final acceptance, final documents, and different-model holistic review. | Runner/tests/docs implemented; final holistic reviewer (cursor-grok-4.6-xhigh) APPROVE after one fix round; hosted CI green on PR #5 and on main; S05 implementation merge 55304dbfbd49f69d567406faddcc308aea65c804 (PR #5; PR CI run 33589765172; default-branch CI run 33589819341 success); acceptance run 20260902T040100Z-95877 42/42; 280 tests; final reviewer APPROVE | COMPLETE | S05 |

## F. Packaged MVP definition of done — Core 09 §7

The complete S05 local harness run `20260902T033607Z-17501` observed the associated steps with all 42 exit codes zero. These rows are promoted no higher than `TESTED`; external review, hosted CI, merge, and release-state promotion remain separate.

| ID | Requirement | Implementation / required evidence | Status | Slice |
|---|---|---|---|---|
| DOD-01 | Starts from a clean Python environment with documented commands. | Clean venv create/install/gates and operator/deployment guides; S05-LOCAL steps 03–12. | COMPLETE | S05 |
| DOD-02 | No external key is required. | Offline package/install/runtime proof; S05-LOCAL steps 03–27. | COMPLETE | S05 |
| DOD-03 | All tests pass. | `make ci` and clean-pip pytest, each 260 passed; S05-LOCAL steps 02 and 11. | COMPLETE | S05 |
| DOD-04 | Integrity passes. | Locked and clean-pip integrity plus final protected audit; S05-LOCAL steps 09, 34–36, 41. | COMPLETE | S05 |
| DOD-05 | Two public golden outcomes are exact. | Golden suite and live HTTP states; S05-LOCAL steps 02, 11, 20. | COMPLETE | S05 |
| DOD-06 | Steel simulated transition is exact and disclosed. | Live detail/manifest/dossier contracts; S05-LOCAL step 20. | COMPLETE | S05 |
| DOD-07 | PP simulation still rejects support. | Live state/route/no-support contracts; S05-LOCAL step 20. | COMPLETE | S05 |
| DOD-08 | Interface is usable at desktop/tablet widths. | S05 static/live contracts plus S06-LOCAL real rendering, 15-control keyboard traversal, no page overflow, and actionability at desktop, tablet, and two presentation widths. | COMPLETE | S05/S06 |
| DOD-09 | Dossier exists in JSON and printable HTML. | Four case/mode live contracts plus S06-LOCAL real popup/clipboard, print computed styles, and four Chromium PDFs with valid header/trailer/page object and non-trivial bytes. | COMPLETE | S05/S06 |
| DOD-10 | Documentation and source are included in one zip. | CRC/member/prohibited-artifact archive audit; S05-LOCAL steps 38–40. | COMPLETE | S05 |

## G. MVP success criteria — Core 01 §9

| ID | Observable success criterion | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| SC-01 | Refuses unsupported factory recommendation. | PP public/simulated `REJECT`, route 0, no support; CI-ALL. | COMPLETE | S01/S04 |
| SC-02 | Public evidence produces meaningful decisions and precise evidence requests. | Steel public `INVESTIGATE`, `data_unlocks`, dossier; CI-ALL. | COMPLETE | S01 |
| SC-03 | Ministry-shaped inputs change named gates, not a generic score. | Dual state, capacity, D*, economics, rule and reconciliation outputs; CI-S04. | COMPLETE | S04 |
| SC-04 | Synthetic evidence is honest and controlled. | Class/source/flag/label/disclosure and fingerprint tests; CI-S03, CI-S04. | COMPLETE | S03/S04 |
| SC-05 | Calculations, thresholds, and evidence are inspectable. | Threshold endpoint, rule ledger, authority and evidence objects; CI-ALL. | COMPLETE | S01–S04 |
| SC-06 | Output is a route and Decision Dossier, not a ranking. | Decision route plus JSON/HTML dossier contracts; CI-ALL. | COMPLETE | S01 |

## H. Milestone v0.3.0 — Real-browser acceptance

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-A1 | Real Chromium Playwright end-to-end tests run in a dedicated gate. | Exact-pinned `e2e` extra, top-level `browser_tests/`, `make e2e`, and independent `browser-gates` workflow job; S06-LOCAL 62/62. | COMPLETE | S06 |
| V3-A2 | Every existing selector, evidence-mode, navigation, dossier, and clipboard path is exercised. | S06-LOCAL tests #1–#8 cover both cards, both select values, steel hero, both mode directions, five navigation buttons, methodology hero, four popups, and four real clipboard payloads. | COMPLETE | S06 |
| V3-A3 | Desktop, tablet, and presentation widths have no page overflow and retain actionable primary controls. | S06-LOCAL test #15 covers both modes at all four approved viewports with visible/enabled/trial-click checks; S07-LOCAL extends the same assertions to both document directions/locales without altering the S06 evidence. | COMPLETE | S06/S07 |
| V3-A4 | Keyboard/focus, Arabic RTL/non-tofu, print media, and PDF bytes are browser-observed. | S06-LOCAL tests #9–#10 and #13–#14; 15-control order, four case/mode print/PDF nodes, and six RTL nodes/matrices. | COMPLETE | S06 |
| V3-A5 | Browser console, page, request, HTTP, external-origin, accessibility, and action failures fail the gate. | S06-LOCAL tests #11–#12 and #17; ordinary collectors expose no exclusion API; observation-only self-test records all five failure categories. | COMPLETE | S06 |
| V3-A6 | Every principal state/width has compact indexed reference evidence without becoming an oracle. | `reference-screenshots/v0.2.0/index.md`: 40 SHA-256-indexed WebPs, 4,650,022 bytes total, explicit non-oracle warning; source contract forbids screenshot comparisons. S07-LOCAL adds a separate 40-image v0.3.0 lossless-WebP oracle for 10 screens × 2 locales × 2 viewports with a hashed manifest and fixed comparator; the S06 set remains documentary and untouched. | COMPLETE | S06/S07 |
| V3-A8 | Complete Arabic/English switching for interface chrome and governed labels. | Governed catalogue/API, URL→storage→English precedence, atomic switch, `lang`/`dir`, Western-digit formatting, source-language islands, and two-direction Playwright switch journeys; S07-LOCAL. | COMPLETE | S07 |
| V3-A10 | Token-only styling, named ES modules under 200 lines, keyboard/contrast and verified bidi layout. | `check_ui_contracts.py`, `check_es_modules.py`, browserless negative fixtures, 16 keyboard nodes, 16 responsive/mirroring nodes, and 16 axe nodes; S07-LOCAL. | COMPLETE | S07 |
| V3-G7 | Synthetic evidence is never described as observed, official, or Ministry-provided in either language. | Evidence policy 1.2.0 owns both labels; evidence/rules/decision/GenUI/dossier projections and every simulated browser surface display both; public surfaces display neither; S07-LOCAL. | COMPLETE | S07 |

## I. Milestone v0.3.0 — S08 computed public evidence

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-C2-partial | Any conforming PublicSnapshot v2 executes the public R-rule ledger without Python/product-ID dispatch; generalized public decision selection remains S09. | `public_snapshot.validate_public_snapshot`, non-recursive v2-only repository, evidence-derived `rules.evaluate_rules`, schema/loader/migration/API tests; S08-LOCAL. | TESTED | S08 |
| V3-D2 | R3 computes HHI and largest supplier independently on value and quantity, fires on either basis, and leaves absent bases `NOT_CALCULABLE`. | `trade_metrics.concentration_metrics`; both-basis below/equal/above tests; quantity-only firing test; steel value HHI 0.36; S08-LOCAL. | COMPLETE | S08 |
| V3-D4 | Decision Dossier JSON/HTML retains and separates contradictory public and synthetic evidence without public leakage. | Dossier 1.1 contradiction register, catalogue 1.1.0, escaped/localized unit and 16 existing browser dossier nodes; S08-LOCAL. | COMPLETE | S08 |
| V3-D7 | R5 calculates retained imports, net exposure, apparent consumption, and import penetration when inputs exist, and names every unavailable input otherwise. | `trade_metrics.domestic_flow_metrics`; numeric/unknown/penetration-boundary tests; public inputs remain unavailable pending S12; S08-LOCAL. | COMPLETE | S08 |
| V3-D12 | R1-D confidence cap is configuration-sourced. | Injected-cap rule test, thresholds 1.2.0, recursive literal scan; S08-LOCAL. | COMPLETE | S08 |
| V3-KL32 | Canonical baseline updates run as the host user and reject non-host-owned output. | `--user uid:gid`, identity assertion, ownership sweep tests, one 40-WebP S08 update with recursive UID 1000 proof, and green compare; S08-LOCAL. | TESTED | S08 |

## J. Milestone v0.3.0 — S09 generalized public decision

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-C1 | Public state, route, gap, needs and narrative are computed without an authored decision contract or case-ID dispatch. | `public_decision.py`, `evidence_needs.py`, `narratives.py`; schema 2.1 removes `public_decision_contract`; source-independence and fixture tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-C2 | Any conforming PublicSnapshot 2.1.0 is validated and analysable without Python changes. | `public_snapshot.py`; four synthetic-free complete fixtures; schema/migration/API tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-C4-public | Public `ADVANCE`, `INVESTIGATE`, `MONITOR`, and evidenced `REJECT` branches are executable. | Advance, monitor, exclusion-reject and equivalence-reject fixtures; per-field D/E downgrades; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-C5-public | Public analysis emits ordered route hypotheses with precedence and maximum-defensible-national-value selection. | `route_hypotheses.py`; order, max-ΔNV, tie, lower-route, support-sequence and route-7 tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-C8 | No product/opportunity ID, producer name or evidence source type determines a public decision or route. | Full passport-source mutation and AST predicate audit over six engine modules; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-D1 | All five methodology §6.3 sector profiles are loaded with complete gates and boundary proof. | `sector_profiles.v1.yaml` 1.1.0; 82 profile tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-D3 | The configured four-field ADVANCE gate executes on evidence class and resolution status. | `evidence.evaluate_advance_gate`; evidence policy 1.3.0; positive A/B/C and eight D/E downgrade tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |
| V3-D9-public | Routes 0–8 are exercised as public hypotheses; route 8 remains graph-required. | PP route 0, steel route-5 preference, route-3 positive fixture, pure route-selection matrix, route-8 rejection/GRAPH_REQUIRED tests; S09-LOCAL and S09-CI. | COMPLETE | S09 |

### S09 Core 01 FR-030–FR-049 evidence

| IDs | S09 local evidence | Status |
|---|---|---|
| FR-030–FR-034 | Existing effective-capacity/K/U/D*/band formulas re-proven across five profiles; ordinary state 3 no longer impersonates a hard-gate failure. | COMPLETE |
| FR-035–FR-039 | Five-profile validation, profile/decision gate separation, four field assessments, configured source-independent ADVANCE gate, six exclusions and one-primary taxonomy. | COMPLETE |
| FR-040–FR-045 | Existing unsupported economics, NPV/IRR/S*, national value, competition and EVSI exacts preserved; route-evidence fixture adds public route economics. | COMPLETE |
| FR-046–FR-049 | Nine route hypotheses, lower-route precedence/max-ΔNV, route-8 GRAPH_REQUIRED, computed needs/conditions/kills and governed EN/AR narratives. | COMPLETE |

## K. Milestone v0.3.0 — S10 generalized simulation branch

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-C3-schemas | Scenario contract 2.0.0 governs bilingual narratives, allocation/expansion/flow blocks and `class_if_confirmed`. | `scenario_contract.py`; Core 06 v2; migration and validation tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-C5-simulated | Simulated analysis emits ordered route hypotheses 0–7 with amended-I5 selection and route-8 refusal. | `simulation.py`, `route_hypotheses.py`; per-route fixtures; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-C7 | Every 2.0.0 scenario reconciles to public marginals and carries planted ground truth. | `evidence.reconcile_synthetic_scenario`; Gate B ten checks; ground-truth back-tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-D5 | Governed tariff-line and buyer-allocation scenario schemas reconcile to public imports. | Contract 2.0.0 blocks; reconciliation PASS/FAIL tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-D6 | Governed expansion-assumption schema is disclosed and bounded against public nameplate. | Contract 2.0.0 `expansion_assumption`; reconciliation test; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-D8 | R8 is calculable when base demand, commitment probability and MES exist. | `rules.evaluate_simulated_rules`; steel MES 50.0; boundary tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| V3-D9-simulated | Routes 0–7 and MONITOR are exercised in simulation; route 8 remains graph-required. | Ten fixture matrix; route-8 refusal; MONITOR trigger gate; S10-LOCAL and S10-CI. | COMPLETE | S10 |

### S10 Core 01 FR-055–FR-059 evidence

| ID | Requirement | Implementation and execution evidence | Status | Slice |
|---|---|---|---|---|
| FR-055 | Simulated route hypotheses evaluate routes 0–7 plus route-8 contract without graph activation. | `simulation.compute_simulated_decision`; route-8 `GRAPH_REQUIRED` tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| FR-056 | Scenario contract 2.0.0 validates bilingual narratives and optional blocks with public gate pairing. | `scenario_contract.validate_simulation_contract`; fail-closed tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| FR-057 | Simulated reconciliation compares declared blocks to public marginals. | Ten Gate B checks; reconciliation tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| FR-058 | Simulated narratives render bilingually from scenario or catalogue 1.1.0. | `narratives.py`; browser/dossier/API tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |
| FR-059 | UI and dossier mirror `simulation_decision` without mutating `real_decision`. | `genui.py`, `dossier.py`, `dom.js`; isolation and contract tests; S10-LOCAL and S10-CI. | COMPLETE | S10 |

## L. Milestone v0.3.0 — S11 public acquisition I

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-B1 | Operator-only acquisition with offline guard and explicit run parameters. | `acquisition/transport.py`, CLI/Makefile acquire targets; S11-LOCAL. | TESTED | S11 |
| V3-B2 | Deterministic raw store with coverage and attempt records per source. | `acquisition/raw_store.py`, `data/raw/**`; S11-LOCAL. | TESTED | S11 |
| V3-B3-trade-tariff | WITS partners snapshot with passports; other sources honestly UNAVAILABLE/INCOMPLETE. | `data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json`; KL-42–44; S11-LOCAL. | TESTED | S11 |
| V3-B4 | Offline reconstruction proof with manifest partition. | `scripts/reconstruct_snapshot.py`, integrity partition tests; S11-LOCAL. | TESTED | S11 |
| V3-§11-passports | Acquired evidence passports with eight §11 groups on normalized snapshots. | `acquisition/passports.py`, partner snapshot evidence array; S11-LOCAL. | TESTED | S11 |
| V3-RECON | Byte-exact reconstruction and SELECTION_CHANGED detection. | `tests/test_acquisition_reconstruction.py`; S11-LOCAL. | TESTED | S11 |

- **S11-LOCAL:** `.workflow/slices/S11-acquisition-trade-tariff/test_evidence.md` and `implementation_log.md`.

## M. Milestone v0.3.0 — S12a institutional framework

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-B3-institutional | Acquire institutional aggregates, directories and registry metadata where obtainable; otherwise retain honest per-source attempts. | Nine-source connector framework implemented; all five institutional sources have zero-request ENDPOINT_UNVERIFIED / INCOMPLETE attempts (KL-47–51), no live rows or snapshots. | BLOCKED | S12a |
| V3-D7-inputs | Public production/retained-flow inputs usable by R5 where published. | GASTAT 2025 IPI documentation is not relabelled physical production or retained-flow evidence; no institutional rows acquired, and engine projection remains S13/S14 (KL-45/47). | BLOCKED | S12a |
| V3-FRAMEWORK-openness | A test-only kind plugs into generic build, validation, write, load and reconstruction without per-kind dispatch edits. | `tests/test_acquisition_kind_registry.py`, `test_acquisition_stage_specs.py`, `test_acquisition_normalization_status.py`; injected registry/cache isolation and S11 compatibility proofs. | TESTED | S12a |
| V3-RECON-institutional | Three institutional kinds reconstruct from selected stored evidence with provenance, exclusions and tamper refusal. | `tests/test_acquisition_institutional_snapshots.py`, `test_acquisition_institutional_connectors.py`, `test_acquisition_reconstruction.py`; test-only parsers and temporary evidence. Existing S11 partner reconstruction remains 1 snapshot / 4 artifacts; no live institutional reconstruction claimed. | TESTED | S12a |

S12a evidence: `.workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md` and `test_evidence.md`; ADR-016; KL-47–51. T12 full pytest: 1755 passed, one existing warning; integrity/reconstruction/smoke and local make ci pass, including 118 functional + 4 visual browser nodes. Exactly one manifest generation retained all S11/frozen rows. Delivered on the squash merge of S12a (PR #15, `cc85cbc`) after independent implementation APPROVE (zero defects) and hosted CI 5/5 on the exact head (run 34669143106) and on the merge SHA (run 34669431254). The two BLOCKED rows remain BLOCKED: merge delivers the framework and honest attempt records, not live institutional data. Historical S11 §L TESTED rows remain unchanged. S12b documents and S12c entity IDs are separate approved children, not delivered here.

## N. Milestone v0.3.0 — S12b document store

| ID | Observable acceptance | Implementation and local execution evidence | Status | Slice |
|---|---|---|---|---|
| V3-B3-documents | Acquire public documents (disclosures, producer sheets/EPDs, tenders, SASO regulations) with span-addressable DocumentRecords where obtainable; otherwise retain honest per-source attempts. | Twelve COMPLETE DocumentRecords (`saso_documents` 6, `producer_unicoil` 6) from T7-v3; five sources remain ENDPOINT_UNVERIFIED / empty-list (KL-56–60). | PARTIAL | s12b |
| V3-DOC-store | Governed `data/documents/**` lists and records with verbatim text layer, reconstruction and manifest partition. | `documents/store.py`, `documents/textlayer.py`, `documents/lists.py`, reconstruct script document rows; doubles and fixture proofs. | TESTED | s12b |
| V3-DOC-framework | DOCUMENT stage on generalized pipeline without altering S11/S12a raw/snapshot bytes. | `Stage.DOCUMENT`, `connectors/documents.py`, frozen-root gates [6]–[8]; institutional connector pin tests byte-identical. | TESTED | s12b |

S12b evidence: `.workflow/slices/S12b-document-store-disclosures-tenders/implementation_log.md` and `test_evidence.md`; ADR-017; KL-54–55 resolved slot 3; KL-56–65 open. T7-v3 built twelve records; the independent review REJECTED candidate `87084ed2…` (S12B-IR3-F01 visual-order Arabic / wrong `languages`; F02 aggregate-count wording) and the slot-4 correction round rebuilt the six SASO records from `saso_documents-v4` against the same stored run (OD-11) with the text-order disclosure (OD-12, KL-64) and the artefact named (KL-65). The OR-3 slot-5 sweep found three further record-contract defects; OD-13 authorized and slot 5 test-first corrected page hashing, physical PDF page addressing and latest-run supersession, then rebuilt all twelve records offline with unchanged ids. Four manifest runs are recorded and exhausted (T11 05:26:47Z, OD-9 05:43:02Z, OD-10 06:37:37Z, OD-13 07:30:41Z), each with immediate [14] PASS; no fifth run is authorized. Independent Fable review of the final candidate, PR, CI and merge remain pending.
Delivered on the squash merge of S12b (PR #17, `9a9d5c7`) after Fable independent APPROVE (zero findings, owner ruling OR-3) and hosted CI 5/5 on the exact head (run 34683839745) and on the merge SHA (run 34684108497). Statuses above are unchanged by the merge: framework/store/reconstruction rows TESTED; the twelve acquired records are real public documents (SASO B, UNICOIL C); the five UNAVAILABLE sources remain BLOCKED for live data.

## Branch and release-state rules

1. No row on the S05 implementation branch is promoted above `TESTED`.
2. DOD-01–DOD-10 move to `TESTED` only after the matching first complete S05 local harness steps are observed.
3. BC-08 moves to `TESTED` only after the different-model final reviewer reports zero unresolved findings and the required final documents exist.
4. `FR-073` remains `NOT_APPLICABLE (production)`.
5. After the S05 implementation PR merges and default-branch CI for that merge is green, the Supervisor opens the narrow release-state PR. Only that PR may promote eligible rows to `COMPLETE`, record final CI/merge facts, and update durable project state.
