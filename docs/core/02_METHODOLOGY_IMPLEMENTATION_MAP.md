# 02 — Methodology-to-Implementation Map

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Purpose

This is the anti-drift document. Every material methodology requirement is mapped to:

- an implementation module;
- a versioned configuration artifact where applicable;
- one or more tests;
- a visible product output.

An autonomous agent may refactor implementation, but it may not remove a mapped behavior without an approved authority change.

## 2. Section-level traceability

| Methodology section | Contract | Implementation | Primary tests | Product proof |
|---|---|---|---|---|
| 1 — Decision Object and Governing Principles | Resolve identity before economics; brownfield before greenfield; intervention residual; uncertainty changes state | `decision_engine.py`, `models/data JSON`, `AGENTS.md` | golden cases, synthetic isolation | decision hero, route restriction, data-unlock queue |
| 2 — Canonical Opportunity Record | Structured record for identity, specification, application, demand, supply, capability, economics, policy, evidence and decision | `04_CANONICAL_DATA_MODEL.md`, snapshots, dossier | schema and repository tests | opportunity workspace and dossier |
| 3 — Data Contract and Harmonisation | Preserve revision, tariff line, units, valuation, origin, entity, document and as-of date | `data_repository.py`, `acquisition/*`, snapshot schema, `05_DATA_SOURCES...` | integrity, acquisition and data-contract tests | snapshot ID, evidence ledger |
| 4 — Candidate Rulebook | R0–R12; FULL/DEGRADED/DISABLED; falsifiable thresholds | `rules.py`, `thresholds.v1.yaml` | rule and boundary tests | R-rule ledger |
| 5 — Test 1 Genuine Gap | Bilingual extraction, UV full/degraded controls, gap taxonomy | `ai_extraction.py`, `rules.py`, public snapshots | extraction golden, R4-D guard | extraction panel, gap statement |
| 6 — Test 2 Capability | Effective capacity, sector profiles, K/U/D\*, hard gates, route bands | `capability.py`, `sector_profiles.v1.yaml` | capability tests | capability matrix |
| 7 — Test 3 Intervention | Unsupported case, route order, S\*, national value, competition gates | `economics.py`, `decision_engine.py` | economics and steel simulation | economics/EVSI panel |
| 8 — Strategic Value and Portfolio | Keep strategic value separate; avoid one ordinal list; project evidence-backed dependencies only | `graph.projection.build_repository_projection`, `graph.engine_feed`, decision output fields | graph artifact, Cypher-equality and state/route tests | four governed graph-view contracts and separate metrics |
| 9 — EVSI | Research only when it can change a material decision | `economics.approximate_evsi` | EVSI unit test | highest-value next fact |
| 10 — AI and Authority | AI for language/ambiguity; code calculates; experts authorize | `ai_extraction.py`, GenUI guardrails, evidence policy | extraction and API tests | control note and governance screen |
| 11 — Evidence Governance | Passport, quality gates, frozen snapshots and reproducibility | evidence JSON, manifests, `evidence.py`, `acquisition/passports.py` | integrity and passport tests | evidence ledger and boundary banner |
| 12 — End-to-End Algorithm | Ordered deterministic/evidence-gated workflow | `decision_engine.py` | golden end-to-end tests | complete case surface |
| 13 — Steel worked case | Public `INVESTIGATE`, greenfield blocked, brownfield priority | `SAU-H0-721049.json` | steel public golden | steel public workspace |
| 14 — PP worked case | Reject generic capacity support | `SAU-H0-390210.json` | PP public golden | PP decision workspace |
| 15 — Decision Dossier | One-page decision backed by evidence pack | `dossier.py` | dossier API tests | printable dossier |
| 16 — Outcome Learning | Freeze predicted values; compare actuals later | data-model extension point | deferred production tests | documented production extension |
| 5 / 10 — Bilingual presentation boundary | Interface chrome is localized from a governed catalogue; engine analytical text remains marked source-language content until a governed narrative exists | `config.ui_strings_bundle`, `app.ui_strings`, static ES modules | catalogue/API/browser parity tests | whole-interface AR/EN switch |
| 2 / 12 — Signal execution and ADVANCE support | fired FULL configuration-permitted candidate signals; DEGRADED never supports ADVANCE | `signals.advance_supporting_signal_rule_ids`, `thresholds.rules.<rule>.may_support_advance` | FULL-vs-degraded unit and API tests | decision reason code and supporting signal list |
| 2.1 / 10 / 11 — Synthetic disclosure language | English and Arabic warning labels are policy controls and every synthetic projection uses them without changing evidence class or real decision | `evidence.synthetic_display_labels`, `rules`, `genui`, `dossier` | isolation, dossier, API and browser disclosure tests | bilingual synthetic warning |
| 2.1 / 12 — Decision-critical evidence gate | Four field assessments from controlled passport support codes; configured class/status gate; no source-type predicate | `public_decision.assess_decision_critical_fields`, `evidence.evaluate_advance_gate`, `evidence_policy.v1.yaml` | field-class, source-independence, positive/downgrade ADVANCE tests | evidence assessment and gate diagnostics |
| 4.2 — Hard exclusions | Six typed checks; unknown is NOT_CALCULABLE; satisfied exclusion rejects before deep routes | `public_decision.evaluate_hard_exclusions` | six-check truth tables and unknown tests | hard-exclusion diagnostics |
| 5.3 — Gap taxonomy | Exactly one primary methodology class and ordered secondary classes | `public_decision.classify_gap` | taxonomy table tests | gap class |
| 7.1.1 / 7.4 / 12 — Public routes | Ordered 0–8 hypotheses; precedence then maximum defensible ΔNV; route 8 GRAPH_REQUIRED | `route_hypotheses.py` | order, precedence, max-ΔNV, tie and graph tests | route hypotheses and preferred hypothesis |
| 6.3 — Five sector profiles | Five frozen profiles, nine weights each, complete profile hard gates | `capability.py`, `sector_profiles.v1.yaml` | per-profile weight/Kmin/band/gate tests | capability matrix |
| 9 / 15 — Evidence needs and narrative | Computed evidence needs, conditions, kill conditions and governed EN/AR narrative | `evidence_needs.py`, `narratives.py`, `decision_narratives.v1.yaml` | exact golden copy, parity, escaping and browser tests | hero, unlocks, dossier |
| Appendix A | Formula reference | `rules.py`, `capability.py`, `economics.py` | formula tests | metric cards |
| Appendix B | Versioned thresholds and calibration | `thresholds.v1.yaml` | config and boundary tests | rule ledger metadata |
| Appendix C | Minimum data dictionary | `04_CANONICAL_DATA_MODEL.md` and snapshots | repository tests | evidence and opportunity views |
| Appendix D | Public source basis | frozen snapshot source records | integrity tests | source ledger |

## 3. R-rule map

| Rule | Methodology meaning | Function / data | Config | Golden behavior |
|---|---|---|---|---|
| R0 | Identity and classification gate | `rules.evaluate_rules`; snapshot opportunity identity | none | both demo cases retain HS revision and unresolved product boundary |
| R1-F | Full persistence | currently reports DISABLED where continuity/retained flow is absent | `R1_F` | no case falsely claims full persistence |
| R1-D | Degraded persistence | `rules._r1d_rule`; positive observed years within a four-year window, no interpolation, configured confidence cap | `R1_D` | fires for both cases; confidence C |
| R2 | Quantity-led expansion | `trade_metrics.compound_annual_growth`, `latest_usable_trade_pair`; log decomposition over the two latest usable observed years | `R2` | steel fires; PP does not fire |
| R3 | Supplier concentration | `trade_metrics.concentration_metrics`; independent HHI / largest-share checks on value and quantity | `R3` | steel value basis fires at HHI 0.36; quantity is not calculable |
| R4-F | Full UV clusters | explicitly DISABLED in current annual snapshots | `R4_F` | no grade claim |
| R4-D | Descriptive UV dispersion | `trade_metrics.degraded_dispersion_metrics`; row coverage/weighted dispersion or source-attributed disclosure | `R4_D` | opens specification research only |
| R5 | Domestic supply plus imports | `trade_metrics.domestic_flow_metrics`; retained imports, net exposure, apparent consumption, penetration, plus degraded coexistence proxy | `R5` | fires as mismatch test for both while public flow inputs remain unavailable |
| R6 | Capacity pressure | requires synthetic or future internal utilisation and shortage | `R6` | public disabled; steel simulation resolves capacity gap |
| R7 | Latent qualified capacity | requires equivalence and availability | `R7` | public disabled; PP simulation confirms no gap |
| R8 | Committed future demand | requires awarded/financed target-spec demand | `R8` | public disabled; steel simulation provides separate demand layers |
| R9-S | Coarse incumbent adjacency | typed same-process-family, methodology signal and known-failure gate via `rules._r9s_rule` | none | opens capability assessment for both |
| R10 | Strategic criticality | typed responsible-authority designation or computed R3 resilience review | none | steel shows resilience review but not formal designation |
| R11 | Economic exclusion | `trade_metrics.export_import_value_ratio`, `established_domestic_nameplate`; computed gross ratio plus observed A/B/C nameplate | `R11` | PP public rejects generic capacity support; steel computes 0.1144 and does not fire |
| R12 | Evidence-value trigger | named missing facts and EVSI | none | public names facts; simulation quantifies EVSI |

## 4. Formula map

### 4.1 Core trade-flow measures

```text
Retained imports = Gross imports − Verified re-exports
Net import exposure = Retained imports − Domestic-origin exports
Apparent consumption = Domestic production + Retained imports − Domestic-origin exports
Import penetration = Retained imports ÷ Apparent consumption
```

Implementation: `trade_metrics.domestic_flow_metrics`. Each dependent measure
remains `NOT_CALCULABLE` with named missing inputs when its physical evidence
is `UNAVAILABLE`; gross imports are never relabelled retained demand.

### 4.2 Price–quantity decomposition

```text
ΔlnV = ΔlnQ + ΔlnUV
Quantity contribution = |ΔlnQ| / (|ΔlnQ| + |ΔlnUV|)
```

Implementation: `rules.py`

Steel golden result:

```text
ΔlnV ≈ 0.242
ΔlnQ ≈ 0.505
ΔlnUV ≈ -0.262
quantity contribution ≈ 65.8%
```

### 4.3 Effective qualified capacity

```text
Nameplate × Availability × Yield × Qualification share × Market allocation
```

Implementation: `capability.effective_qualified_capacity`

Steel simulation result:

```text
250 × 0.92 × 0.94 × 0.38 × 0.70 = 57.509 kt
```

### 4.4 Capability uncertainty

```text
K = sum known weights
U = 1 − K
Dknown = sum(w × d / 3) / K
D* = min(1, Dknown + λU)
```

Implementation: `capability.evaluate_capability`

Publication controls:

- K ≥ Kmin;
- every sector hard gate resolved;
- no hard gate state 3;
- K=0 → no D\*, `INVESTIGATE`.

### 4.5 Economics

```text
NPV = Σ FCFt/(1+h)^t
S* = minimum S such that NPV(S) ≥ 0 and IRR(S) ≥ h
```

Implementation: `economics.npv`, `economics.irr`, `economics.minimum_effective_support`

Steel simulation result:

```text
Unsupported NPV at 12% = -SAR 18m
Unsupported IRR = 9.5%
Minimum effective support = SAR 18m
Supported NPV = 0
Supported IRR = 12%
```

### 4.6 Incremental national value

```text
Domestic value added + exports + resilience + knowledge/skills + fiscal receipts
− government cost − displacement − resource/environment cost − risk
```

Implementation: `economics.incremental_national_value`

### 4.7 EVSI

```text
P(route changes) × value difference − evidence cost − delay cost
```

Implementation: `economics.approximate_evsi`

## 5. Decision-state map

| State | Engine condition in MVP | UI treatment |
|---|---|---|
| REJECT | a typed hard exclusion or another evidenced rejection condition is satisfied | red decision state and no-intervention route |
| MONITOR | no rejection exists, at least one signal exists, the material trigger is absent, and a named observable trigger is present | blue state with the named trigger |
| INVESTIGATE | a route-changing decision-critical fact is unresolved or contradictory and has positive evidence value; route determination is unresolved with a material trigger; or all ADVANCE gates pass but no fired FULL configuration-permitted candidate signal exists (`ADVANCE_SUPPORT_SIGNAL_DEGRADED`) | gold state and named data unlocks |
| ADVANCE | actual A/B/C decision-critical evidence, all capability, route, economics, national-value, competition, additionality and policy gates pass, at least one fired FULL configuration-permitted candidate signal, and public evidence is not categorically barred | teal state; simulated results retain the visible warning |

Screening dispositions `CANDIDATE`, `NO_CANDIDATE`, and `SCREENED_OUT` are separate from these four formal states.

## 6. Route map

| Route code | Methodology route | MVP use |
|---:|---|---|
| 0 | No intervention | PP public and simulated |
| 1 | Administrative/classification barrier | supported as future route |
| 2 | Information or market linkage | identified as possible low-cost route |
| 3 | Certification/testing/quality | represented in steel upgrade conditions |
| 4 | Demand aggregation/offtake | represented as an alternative route input |
| 5 | Debottlenecking/incremental expansion | steel simulated route |
| 6 | Technology licence/JV | capability route band support |
| 7 | Targeted greenfield | deliberately not selected in golden cases |
| 8 | Shared enabling infrastructure | governed projection/feed and real Cypher mirror delivered in S16a; the unchanged `GRAPH_REQUIRED` decision contract is activated only by the S16b Class-D enabler change |

## 7. Quality-gate map

| Gate | Software proof |
|---|---|
| G0 Identity | opportunity ID, HS revision and boundary present in snapshot |
| G1 Measurement | units, gross-flow warning, missing years and snapshot hash visible |
| G2 Gap | public unresolved or simulated specification-adjusted gap calculated |
| G3 Capability | K/U/D\*, sector profile and hard-gate control |
| G4 Economics | deterministic NPV, IRR, S\* and scenarios |
| G5 Competition/policy | capacity ratio, displacement and national value |
| G6 Decision | state, route, alternatives, conditions, kill condition and evidence action |

## 8. Public/synthetic dual-state map

The response contract contains:

```json
{
  "real_decision": {"state": "INVESTIGATE", "synthetic_flag": false},
  "simulation_decision": {"state": "ADVANCE", "synthetic_flag": true},
  "active_decision": {"state": "ADVANCE", "synthetic_flag": true},
  "integrity": {"real_decision_unchanged_after_simulation": true}
}
```

`active_decision` is a presentation convenience. It never replaces or overwrites the real record.

## 9. Traceability maintenance rule

Any new domain function must be added to this map before implementation review can close. Any removal must identify the methodology requirement that has been formally retired. “Not used by the current UI” is not a valid reason to remove a governing behavior.

| Domain behavior | Implementation | Authority | Primary tests | Visible output |
|---|---|---|---|---|
| Public snapshot v2 validation | `public_snapshot.validate_public_snapshot` | Core 04 PublicSnapshot v2; Core 05 §§5–7 | `test_public_snapshot_schema.py` | snapshot/schema identity and fail-closed loader |
| Observed-span CAGR | `trade_metrics.compound_annual_growth`, `trade_metrics.latest_usable_trade_pair` | Methodology §4 R2; I3 | `test_trade_metrics.py`, `test_threshold_boundaries.py` | R2 ledger metrics |
| Dual-basis concentration | `trade_metrics.concentration_metrics` | Methodology §3.3/R3; I2 | rule/boundary/migration tests | R3 ledger and HHI card |
| Degraded dispersion | `trade_metrics.degraded_dispersion_metrics` | Methodology §5.2.2 | rule/boundary tests | R4-D ledger |
| Domestic flow formulas | `trade_metrics.domestic_flow_metrics` | Methodology §3.3/Appendix A | formula/rule tests | R5 ledger metrics |
| Gross export/import ratio | `trade_metrics.export_import_value_ratio` | Methodology §14.1/R11 | metric/rule/migration tests | R11 computed and disclosed ratio metrics |
| Established nameplate | `trade_metrics.established_domestic_nameplate` | Methodology R9-S/R11; worked case §14 | rule tests | R9-S/R11 ledger |
| Supplier compatibility projection | `trade_metrics.build_supplier_metrics` | Aggregate response contract | API/GenUI tests | metric grid |
| Hard-gate normalization | `public_snapshot.capability_hard_gate_names`, `public_snapshot.has_known_hard_gate_failure` | Core 04/07 v2 | schema/R9 tests | capability and R9-S |
| Public evidence needs | `evidence_needs.derive_evidence_needs` | Methodology §9; Core 07 v2 §6 | need-code/predicate/golden tests | missing facts and data unlocks |
| Public narrative catalogue | `narratives.render_catalogue_entry` | Methodology §§1.2/15; Core 07 v2 §8 | parity/escaping/browser tests | localized hero and dossier |
| Candidate-signal execution and ADVANCE support | `signals.py` | Methodology §4 execution states; Core 07 §7.6 | `tests/test_signals.py`, FULL-vs-degraded API tests | decision reason code and supporting signal list |
| Scenario contract validation | `scenario_contract.validate_simulation_contract` | Core 06 v2 §12 | `tests/test_scenario_contract.py` | HTTP 422 on malformed 2.0.0 scenarios |
| Scenario projection | `scenario_contract.project_simulated_case` | Core 06 v2 §12; Core 07 §7.9 | contract/generalized tests | composite case for public engine reuse |
| Simulated decision assembly | `simulation.compute_simulated_decision` | Core 07 §7.9 | `tests/test_simulation_generalized.py` | `simulation_decision` aggregate |
| Shared-enabler contract | `route_hypotheses.evaluate_shared_enabler_route` | Core 07 §7.7 | route hypothesis tests | route 8 `GRAPH_REQUIRED` |
| Shared-enabler unlock helper | `route_hypotheses.shared_enabler_unlock_value` | ADR-014 | route hypothesis tests | deterministic unlock value only |
| Source connector protocol | `acquisition.connectors.base.SourceConnector` | Core 05 §10–§11; ADR-015 | `tests/test_acquisition_connectors.py` | RunReport per source |
| Raw evidence store | `acquisition.raw_store.RawStore` | Core 05 §10; DD-3 | `tests/test_acquisition_raw_store.py` | hashed page contracts |
| Completeness accounting | `acquisition.coverage.evaluate_coverage` | Core 05 §11; DD-18 | `tests/test_acquisition_coverage.py` | coverage.json per unit |
| Latest-run source-partitioned selection | `acquisition.coverage.select_latest_units` | Core 05 §11; DD-21 | snapshot/coverage tests | selected_run_id in snapshots |
| Offline guard | `acquisition.transport.assert_live_permitted`, `tests/conftest.py` | Core 03 §8; DD-2 | `tests/test_offline_guard.py` | CI socket block |
| Harmonisation | `acquisition.harmonise` | Methodology §3.2; Core 05 §6 | `tests/test_acquisition_harmonise.py` | normalized rows |
| Acquired passports | `acquisition.passports.build_acquired_passport` | Methodology §11; Core 04 | `tests/test_acquisition_passports.py` | eight-group passports |
| Acquisition snapshots | `acquisition.snapshots` | Core 04 acquisition snapshots | `tests/test_acquisition_snapshots.py` | source-qualified IDs |
| Reconstruction proof | `scripts/reconstruct_snapshot.py` | Core 09 Gate H; DD-11 | `tests/test_acquisition_reconstruction.py` | RECONSTRUCTION PASS |
| Screening case projection | `screening.projection.project_case` | Methodology §§3.2–3.3 | `tests/test_screening_projection.py` | typed per-HS6 case |
| Screening rule ledger | `screening.rules.screening_ledger` | Methodology §§4–5 | `tests/test_screening_rules.py` | coded ledger |
| Screening dispositions | `screening.dispositions.classify` | Methodology §12; Core 07 §7.6 | `tests/test_screening_dispositions.py` | typed disposition |
| Route-specific queues | `screening.queues.assign_queues` | Methodology §8.2 | `tests/test_screening_queues.py` | five Pareto queues |
| Screening snapshot | `screening.snapshot.build_screening_snapshot` | Manifest §7.5 | `tests/test_screening_snapshot.py` | hashed artifact |
| Screening loader | `screening.repository.screening_snapshot` | Core 03 runtime boundary | `tests/test_screening_repository_and_api.py` | newest valid snapshot |
| Screening API | `screening.api.router` | Core 03 API contract | `tests/test_screening_repository_and_api.py` | summary/queue/record |
| Candidate emission | `screening.cli.emit_candidates` | Methodology §12 stage two | `tests/test_screening_candidates.py` | hashed HS6 batches |
| Governed deep-case selection | `cases.selection.select_cases` | Methodology §§1, 4, 12; S14/S15 owner rulings | `tests/test_case_selection.py` | version-gated `CASE-SELECTION-S14-*` / `CASE-SELECTION-S15-*` records with ruled `identity_exclusions` and typed `SERIES_GAP_YEARS` |
| Pinned selection public projection | `case_selection_view.build_case_selection_view`, `GET /api/case-selection` | Methodology §§1, 4, 11–12; S15 owner ruling | `tests/test_s15b_selection_view.py`, `browser_tests/test_s15b_selection.py` | manifest-verified public-only S15 selection, quotas, ordered substitutes and every recorded exclusion |
| Optional aggregate EVSI compatibility | `simulation.simulate`, `economics.approximate_evsi` | Methodology §9; Core 07 §6 | `tests/test_s15b_portfolio.py`, `tests/test_api.py` | absent estimates yield `evsi: null`; supplied mappings retain deterministic calculation and existing errors |
| Recorded selection reconstruction | `cases.selection.reconstruct_all_selections` | Methodology §11.3; Core 09 §10.2 | `tests/test_case_selection.py`, `tests/test_integrity_contract.py` | `CASE SELECTION RECONSTRUCTION PASS` from the identities frozen in each write-once record |
| CaseBrief validation | `cases.brief.validate_case_brief` | Methodology §§2, 5.1, 10–11 | `tests/test_case_brief.py`, `tests/test_case_briefs_real.py` | `CaseBrief 1.1.0` and verbatim page/line spans |
| Derived public snapshot | `cases.projection.build_public_snapshot` | Methodology §§2–6, 11–12 | `tests/test_case_projection.py`, `tests/test_case_briefs_real.py` | temporary `SAU-H6-` PublicSnapshot 2.2.0 proof |
| Superseded screening input resolution | `screening.snapshot.resolve_recorded_input` | Manifest §§7.3, 7.5, 8; Core 04 §11 | retention and reconstruction tests | current-or-`config/history/` content-hash resolution; otherwise `INPUTS_CHANGED` |
| Historical acquired-snapshot reconstruction | `acquisition.snapshots.reconstruct_pinned` | Methodology §11.3; Manifest §7.5 | `tests/test_acquisition_snapshots.py` | old and current source snapshots reconstruct from their recorded raw-run selection |
| Same-day partner-snapshot coexistence | `acquisition.kinds.snapshot_id`, `acquisition.snapshots.write_snapshot` | Core 04 §13; S15 OD-13/OD-14 | `tests/test_acquisition_snapshots.py` | deterministic scoped id, disjoint `scope_units`, one-way `coexists_with` |
| S15 public document sources | `acquisition.connectors.documents`, `acquisition.documents.lists` | Core 05 §§3.2, 11; S15 OD-12 | acquisition connector/list/stored-artifact tests | WCO 29/30/31, SPIMACO, SABIC Agri-Nutrients and SFDA records with `regulatory_authority` restricted to SFDA |
| S15 entity mentions | `acquisition.entities.mentions`, `acquisition.entities.resolver` | Methodology §11; Core 05 §6.5 | `tests/test_entity_resolution_artifact.py` | third write-once entity artifact from verified publisher-name spans |
| Governed graph projection | `graph.projection.build_repository_projection`, `graph.artifact.validate_projection` | Methodology §8.3; Core 04 §8 v2; R-3 | `tests/test_graph_projection.py`, `tests/test_graph_artifact.py` | write-once `data/graph/` projection |
| R9-S adjacency explanation | `graph.engine_feed.adjacency_explanation` | Methodology R9-S; S17 view 1 | artifact/Cypher equality tests | fixed `adjacency` view |
| Route-blocking capability | `graph.engine_feed.route_blocking_capability` | Core 07 §§4.3, 7.7; S17 view 2 | artifact/Cypher equality tests | fixed `route_blocking` view |
| Evidence-to-change linkage | `graph.engine_feed.evidence_linkage` | Methodology §9; S17 view 4 | artifact/Cypher equality tests | fixed `evidence_to_change` view |
| Shared-enabler projection feed | `graph.engine_feed.shared_enabler_inputs`, `graph.engine_feed.shared_enabler_queue_rows` | Methodology §§8.2–8.3; R-2 | public-empty, Class-D isolation and live equality tests | fixed `shared_enabler` view; route activation remains S16b |
| Idempotent graph mirror | `graph.loader.load`, `graph.loader.verify` | R-3, R-6, OR-7 | `graph_tests/test_loader.py`, provenance/count tests | Compose/CI/Aura-safe mirror |
| Fail-closed live graph service | `graph.service.GraphService`, `graph.api.router` | S16 objective; Core 03 §13 | stopped-service and offline API tests | typed `GRAPH_UNAVAILABLE` |
