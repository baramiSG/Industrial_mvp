# 04 — Canonical Data Model

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Modeling principle

The primary entity is not an HS code. An HS code is one coordinate used to locate evidence. The canonical decision object is:

```text
Product–Specification–Application–Capability–Demand–Route
```

The MVP stores each golden case as a versioned JSON aggregate. Production may normalize the same model into relational tables and a graph without changing the field semantics.

## 2. Core entities

### 2.1 Opportunity

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | string | yes | Persistent opportunity ID, independent of display name |
| `hs_revision` | string | yes | Reported nomenclature version |
| `hs6` | string | yes | Six-digit customs coordinate |
| `national_tariff_line` | string/null | production | Saudi line retained where available |
| `sector_profile` | enum | yes | Capability weight profile |
| `commercial_name_en/ar` | string | yes | Normalized bilingual names |
| `decision_object_status` | enum | yes | resolved, partially resolved or generic-HS-only |
| `application_boundary` | string | yes | Included and unresolved end-use boundary |
| `as_of_date` | date | yes | Reproducibility date |

### 2.2 Specification

| Group | Fields |
|---|---|
| Identity | material/chemical identity, model/part number, synonyms, excluded meanings |
| Composition | grade, purity, alloy, additive package, coating, impurity limits |
| Geometry | thickness, width, length, diameter, particle size, tolerance, surface, package |
| Performance | strength, barrier, conductivity, corrosion, temperature, pressure, sterility, shelf life |
| Standard | SASO, GSO, ASTM, ISO, EN, SFDA or customer standard and edition |
| Qualification | approved supplier, customer test, regulatory registration or application approval |
| Evidence | exact Arabic/English span, source, confidence and reviewer status |

The public steel case leaves the exact imported target specification unresolved. The simulated steel scenario adds a named, explicitly synthetic target specification.

### 2.3 TradeObservation

```json
{
  "year": 2024,
  "reporter": "Saudi Arabia",
  "partner": "World",
  "flow": "imports",
  "hs_revision": "H0",
  "hs6": "721049",
  "trade_value": 236.9,
  "currency": "USD_m",
  "net_weight": 287.9,
  "quantity_unit": "kt",
  "valuation": "CIF",
  "gross_flow": true,
  "reexport_status": "unresolved"
}
```

Value, weight, supplementary quantity and unit are never collapsed into one field.

### PublicSnapshot 2.1

A live public snapshot sets `schema_version: "2.1.0"`. The two frozen golden
files retain their snapshot IDs, as-of dates, and historical-v1 `supersedes`
links. A new snapshot with no predecessor may set `supersedes:
"UNAVAILABLE"`; an evidence refresh still follows Authority Manifest §7.5.

Evidence passports use the controlled support-code vocabulary defined by
Core 07 §7.2. Free-text support claims are invalid. `domestic_capability`
contains all configured `profile_hard_gates` with typed status and evidence
references, plus decision-specific unresolved gates.

`hard_exclusion_inputs` carries the six typed methodology §4.2 input blocks.
`decision_inputs` may carry target-specification demand, specification
equivalence, route evidence for routes 1–7, and a named monitor trigger.
Missing facts remain exact `UNAVAILABLE`.

The snapshot contains no `public_decision_contract`, authored state, route,
screening disposition, gap class, rule result, route-hypothesis result,
narrative, missing-fact list, condition, or kill-condition list. All are
computed.

### 2.4 Plant and ProductionLine

| Field | Meaning |
|---|---|
| `plant_id`, `company_id`, `parent_group_id` | Persistent entity IDs |
| `line_id` | Specific production line |
| `process_route` | Physical/chemical transformation sequence |
| `equipment_envelope` | Dimensions, scale, operating conditions and tolerances |
| `nameplate` | Published or verified installed capacity |
| `availability` | Time available for production |
| `yield` | Good output / input |
| `qualification_share` | Share capable of the target specification |
| `market_allocation_share` | Share available to the target market and window |
| `utilisation` | Actual effective load, not assumed from nameplate |
| `certifications` | Quality, lab, regulatory and customer approvals |

### 2.5 CapabilityAssessment

```json
{
  "sector_profile": "coated_steel",
  "dimensions": [
    {"dimension": "core_process_route", "weight": 0.20, "state": 0, "known": true},
    {"dimension": "capacity_time_window", "weight": 0.10, "state": "U", "known": false}
  ],
  "known_weight_coverage": 0.75,
  "unknown_weight": 0.25,
  "d_known": 0.18,
  "internal_d_star_before_gate": 0.305,
  "d_star": null,
  "unresolved_hard_gates": ["customer qualification"],
  "route_publishable": false
}
```

An internal calculation may exist for diagnostic purposes, but `d_star` remains null when publication controls fail.

### 2.6 DemandScenario

Demand layers remain separate:

- `base`
- `committed`
- `announced`
- `downside`
- `upside`

Each layer records quantity, timing, probability, buyer/application and evidence status. Announced demand is not silently added to the base.

### 2.7 EconomicsCase

| Block | Fields |
|---|---|
| Investment | engineering, equipment, construction, certification, working capital, contingency, commissioning |
| Operations | feedstock, utilities, labor, yield, ramp, maintenance, EHS, logistics and inventory |
| Revenue | volume and price by target specification, domestic/export split and timing |
| Finance/tax | hurdle rate, tax, depreciation, financing, incentive timing and residual value |
| Risk | technology, price, demand, feedstock, qualification and delay sensitivities |
| Output | unsupported NPV/IRR, S\*, supported NPV/IRR and scenario results |

### 2.8 EvidencePassport

Every decision-relevant fact must carry:

```json
{
  "evidence_id": "S-UNICOIL-EPD",
  "title": "UNICOIL 2024 Environmental Product Declaration",
  "source": "UNICOIL",
  "url": "...",
  "period": "2023/2024",
  "retrieved_at": "2026-08-31",
  "status": "observed",
  "evidence_class": "C",
  "synthetic_flag": false,
  "supports": ["installed capacity", "process route"],
  "transformation": null,
  "contradiction": "published coating range differs from web page",
  "reviewer_status": "unconfirmed by responsible authority"
}
```

### 2.9 SyntheticScenario

```json
{
  "scenario_id": "SYN-MINISTRY-STEEL-001",
  "opportunity_id": "SAU-H0-721049",
  "synthetic_flag": true,
  "display_label": "SIMULATED — NOT MINISTRY EVIDENCE",
  "seed_basis": "Public import and nameplate marginals",
  "evidence_class": "D",
  "source": "DEMO_GENERATOR",
  "synthetic_inputs": {}
}
```

The scenario is not inserted into the public opportunity record. It is loaded through a separate repository method.

### 2.10 DecisionRecord

```json
{
  "state": "INVESTIGATE",
  "route_code": null,
  "screening_disposition": "CANDIDATE",
  "route_label": "Brownfield priority to test",
  "headline": "INVESTIGATE — binding constraint unresolved",
  "rationale": "...",
  "confidence": "C",
  "gap_class": {},
  "evidence_class_assessment": {},
  "hard_exclusions": [],
  "route_hypotheses": [],
  "preferred_hypothesis": {},
  "narrative_version": "1.0.0",
  "conditions": [],
  "kill_conditions": [],
  "missing_facts": [],
  "decision_reason_code": "ROUTE_CHANGING_EVIDENCE_UNRESOLVED",
  "advance_support_signal_rule_ids": ["R2", "R3", "R9-S"],
  "synthetic_flag": false
}
```

Simulation creates a second `DecisionRecord` with `synthetic_flag=true`. The public record remains immutable.

## 3. Aggregate response contract

```json
{
  "opportunity": {},
  "snapshot_id": "PUBLIC-SAU-H0-721049-2026-08-31",
  "mode": "simulated",
  "real_decision": {},
  "simulation_decision": {},
  "active_decision": {},
  "screening_disposition": "CANDIDATE",
  "gap_class": {},
  "evidence_class_assessment": {},
  "hard_exclusions": [],
  "route_hypotheses": [],
  "preferred_hypothesis": {},
  "narrative_version": "1.0.0",
  "rules": [],
  "capacity": {},
  "capability": {},
  "economics": {},
  "competition": {},
  "evsi": {},
  "trade": [],
  "evidence": [],
  "data_unlocks": [],
  "synthetic_inputs_used": [],
  "integrity": {}
}
```

## 4. Identity and keys

- Opportunity IDs are stable across snapshot revisions.
- Snapshot IDs include boundary, opportunity and as-of date.
- Evidence IDs are stable within a source contract.
- Scenario IDs are unique and never reused for a different synthetic truth set.
- A future production decision ID should include opportunity, as-of date and decision version.

## 5. State enums

### Evidence status

```text
observed | calculated | model_estimated | inferred | assumption | unresolved | synthetic
```

### Evidence class

```text
A | B | C | D | E
```

### Rule execution

```text
FULL | DEGRADED | DISABLED
```

### Decision state

```text
REJECT | MONITOR | INVESTIGATE | ADVANCE
```

### Capability state

```text
0 | 1 | 2 | 3 | U
```

## 6. Data invariants

1. `synthetic_flag` is mandatory on every evidence row.
2. A public snapshot may not contain `synthetic_flag=true`.
3. A synthetic scenario may not omit scenario ID, seed basis, source, class or warning label.
4. `real_decision.synthetic_flag` is always false.
5. `simulation_decision.synthetic_flag` is always true.
6. `d_star` is null when route publication controls fail.
7. R4-D output cannot contain `grade_confirmed=true` or a cluster label.
8. Values and quantities retain units.
9. Gross flows are never labeled retained imports.
10. Missing years are explicit; no implicit interpolation.

## 7. Relational production mapping

A production implementation can normalize to:

```text
opportunity
classification
specification
application
trade_observation
company
plant
production_line
capability_dimension
capacity_observation
demand_scenario
economics_case
intervention_case
evidence_passport
rule_execution
decision_record
decision_condition
snapshot
```

## 8. Graph production mapping

Useful nodes:

```text
Product, Specification, Application, Standard, Plant, ProductionLine,
Process, Equipment, Certification, Buyer, Input, Utility, Technology,
Opportunity, Intervention, Evidence, Decision
```

Useful edges:

```text
HAS_SPECIFICATION, USED_IN, REQUIRES_STANDARD, PRODUCED_BY, HAS_LINE,
USES_PROCESS, REQUIRES_EQUIPMENT, QUALIFIED_BY, DEMANDED_BY, DEPENDS_ON,
SUPPORTED_BY_EVIDENCE, BLOCKED_BY, UNLOCKED_BY, ALTERNATIVE_TO
```

Only evidence-backed, decision-relevant edges enter the governed graph.

## 9. Dossier projection

The Decision Dossier is a projection, not a separate source of truth. It is generated from the canonical record and includes:

- decision headline;
- identity;
- demand and supply conclusions;
- gap;
- capability route;
- economics;
- competition/policy;
- evidence summary;
- conditions and kill conditions.

## 10. Evolution rule

A new field may be added when it is required by the methodology or a source contract. A field may not be repurposed to carry a different concept merely because it is convenient. Version the schema when meaning changes.
