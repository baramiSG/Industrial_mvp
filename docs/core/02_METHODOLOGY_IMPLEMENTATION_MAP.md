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
| 3 — Data Contract and Harmonisation | Preserve revision, tariff line, units, valuation, origin, entity, document and as-of date | `data_repository.py`, snapshot schema, `05_DATA_SOURCES...` | integrity and data-contract tests | snapshot ID, evidence ledger |
| 4 — Candidate Rulebook | R0–R12; FULL/DEGRADED/DISABLED; falsifiable thresholds | `rules.py`, `thresholds.v1.yaml` | rule and boundary tests | R-rule ledger |
| 5 — Test 1 Genuine Gap | Bilingual extraction, UV full/degraded controls, gap taxonomy | `ai_extraction.py`, `rules.py`, public snapshots | extraction golden, R4-D guard | extraction panel, gap statement |
| 6 — Test 2 Capability | Effective capacity, sector profiles, K/U/D\*, hard gates, route bands | `capability.py`, `sector_profiles.v1.yaml` | capability tests | capability matrix |
| 7 — Test 3 Intervention | Unsupported case, route order, S\*, national value, competition gates | `economics.py`, `decision_engine.py` | economics and steel simulation | economics/EVSI panel |
| 8 — Strategic Value and Portfolio | Keep strategic value separate; avoid one ordinal list | decision output fields; future portfolio adapter | state/route tests | resilience rule and separate metrics |
| 9 — EVSI | Research only when it can change a material decision | `economics.approximate_evsi` | EVSI unit test | highest-value next fact |
| 10 — AI and Authority | AI for language/ambiguity; code calculates; experts authorize | `ai_extraction.py`, GenUI guardrails, evidence policy | extraction and API tests | control note and governance screen |
| 11 — Evidence Governance | Passport, quality gates, frozen snapshots and reproducibility | evidence JSON, manifests, `evidence.py` | integrity tests | evidence ledger and boundary banner |
| 12 — End-to-End Algorithm | Ordered deterministic/evidence-gated workflow | `decision_engine.py` | golden end-to-end tests | complete case surface |
| 13 — Steel worked case | Public `INVESTIGATE`, greenfield blocked, brownfield priority | `SAU-H0-721049.json` | steel public golden | steel public workspace |
| 14 — PP worked case | Reject generic capacity support | `SAU-H0-390210.json` | PP public golden | PP decision workspace |
| 15 — Decision Dossier | One-page decision backed by evidence pack | `dossier.py` | dossier API tests | printable dossier |
| 16 — Outcome Learning | Freeze predicted values; compare actuals later | data-model extension point | deferred production tests | documented production extension |
| 5 / 10 — Bilingual presentation boundary | Interface chrome is localized from a governed catalogue; engine analytical text remains marked source-language content until a governed narrative exists | `config.ui_strings_bundle`, `app.ui_strings`, static ES modules | catalogue/API/browser parity tests | whole-interface AR/EN switch |
| 2.1 / 10 / 11 — Synthetic disclosure language | English and Arabic warning labels are policy controls and every synthetic projection uses them without changing evidence class or real decision | `evidence.synthetic_display_labels`, `rules`, `genui`, `dossier` | isolation, dossier, API and browser disclosure tests | bilingual synthetic warning |
| Appendix A | Formula reference | `rules.py`, `capability.py`, `economics.py` | formula tests | metric cards |
| Appendix B | Versioned thresholds and calibration | `thresholds.v1.yaml` | config and boundary tests | rule ledger metadata |
| Appendix C | Minimum data dictionary | `04_CANONICAL_DATA_MODEL.md` and snapshots | repository tests | evidence and opportunity views |
| Appendix D | Public source basis | frozen snapshot source records | integrity tests | source ledger |

## 3. R-rule map

| Rule | Methodology meaning | Function / data | Config | Golden behavior |
|---|---|---|---|---|
| R0 | Identity and classification gate | `rules.evaluate_rules`; snapshot opportunity identity | none | both demo cases retain HS revision and unresolved product boundary |
| R1-F | Full persistence | currently reports DISABLED where continuity/retained flow is absent | `R1_F` | no case falsely claims full persistence |
| R1-D | Degraded persistence | positive observed years within a four-year window, no interpolation | `R1_D` | fires for both cases; confidence C |
| R2 | Quantity-led expansion | `log_change`, `quantity_contribution_share` | `R2` | steel fires; PP does not fire |
| R3 | Supplier concentration | HHI / supplier-share check | `R3` | steel fires at HHI 0.36 |
| R4-F | Full UV clusters | explicitly DISABLED in current annual snapshots | `R4_F` | no grade claim |
| R4-D | Descriptive UV dispersion | snapshot signal + protected interpretation | `R4_D` | opens specification research only |
| R5 | Domestic supply plus imports | domestic capability and material import coexistence | `R5` | fires as mismatch test for both |
| R6 | Capacity pressure | requires synthetic or future internal utilisation and shortage | `R6` | public disabled; steel simulation resolves capacity gap |
| R7 | Latent qualified capacity | requires equivalence and availability | `R7` | public disabled; PP simulation confirms no gap |
| R8 | Committed future demand | requires awarded/financed target-spec demand | `R8` | public disabled; steel simulation provides separate demand layers |
| R9-S | Coarse incumbent adjacency | same process family plus another signal | none | opens capability assessment for both |
| R10 | Strategic criticality | authority-confirmed criticality or resilience review | none | steel shows resilience review but not formal designation |
| R11 | Economic exclusion | structural uncompetitiveness or generic-capacity warning | `R11` | PP public rejects generic capacity support |
| R12 | Evidence-value trigger | named missing facts and EVSI | none | public names facts; simulation quantifies EVSI |

## 4. Formula map

### 4.1 Price–quantity decomposition

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

### 4.2 Effective qualified capacity

```text
Nameplate × Availability × Yield × Qualification share × Market allocation
```

Implementation: `capability.effective_qualified_capacity`

Steel simulation result:

```text
250 × 0.92 × 0.94 × 0.38 × 0.70 = 57.509 kt
```

### 4.3 Capability uncertainty

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

### 4.4 Economics

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

### 4.5 Incremental national value

```text
Domestic value added + exports + resilience + knowledge/skills + fiscal receipts
− government cost − displacement − resource/environment cost − risk
```

Implementation: `economics.incremental_national_value`

### 4.6 EVSI

```text
P(route changes) × value difference − evidence cost − delay cost
```

Implementation: `economics.approximate_evsi`

## 5. Decision-state map

| State | Engine condition in MVP | UI treatment |
|---|---|---|
| REJECT | no genuine gap, generic capacity contradicted, or equivalent qualified supply is sufficient | red decision state and no-intervention route |
| MONITOR | supported by engine contract but not used by current golden cases | blue state |
| INVESTIGATE | material case but decision-critical evidence or hard gate unresolved | gold state and named data unlocks |
| ADVANCE | only in isolated steel simulation when capability, economics, national value and competition controls all pass | teal simulated state with visible warning |

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
| 8 | Shared enabling infrastructure | future portfolio extension |

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
