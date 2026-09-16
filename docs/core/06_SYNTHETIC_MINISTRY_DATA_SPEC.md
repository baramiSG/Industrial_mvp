# 06 — Synthetic Ministry Data Specification

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Purpose

The synthetic layer exists to demonstrate the complete power of the methodology before Ministry data is connected. It is not a substitute for Ministry evidence and is not used to make a real recommendation.

The product must show both truths at once:

- **Public truth:** what can be defended now.
- **Simulation truth:** what the engine would calculate if the displayed Ministry-grade facts were confirmed.

## 2. Governing invariant

> **Synthetic evidence can never change the real decision state.**

In code:

```text
real_decision = f(public_evidence)
simulation_decision = g(real_decision, synthetic_scenario)
real_decision_after_simulation == real_decision_before_simulation
```

The engine fingerprints the real record before simulation and asserts equality afterward.

## 3. Synthetic blocks permitted in the POC

### 3.1 Customs/internal demand

- Saudi 12-digit transaction allocation beneath HS6;
- invoice description;
- importer/offtaker;
- declared end use;
- re-export flag;
- domestic-origin export flag;
- target specification and standard;
- customer qualification reason.

### 3.2 Plant and line

- plant-month production;
- line nameplate;
- availability;
- yield;
- target-specification qualification share;
- domestic/export/product allocation;
- backlog and outage;
- equipment envelope;
- certification and customer approval;
- planned expansion.

### 3.3 Economics and support

- capex and working capital;
- opex by major driver;
- price and volume scenario;
- cash flows;
- hurdle rate;
- intervention timing;
- national-value components;
- displacement and resource costs.

### 3.4 Calibration corpus

- application facts;
- approval/rejection reason;
- approved instrument;
- historical decision date;
- realized outcomes.

The packaged POC does not claim to reproduce the Ministry’s actual calibration corpus. It only defines the schema.

## 4. Mandatory scenario metadata

Every scenario must contain:

```yaml
scenario_id: unique and immutable
opportunity_id: target opportunity
synthetic_flag: true
display_label: SIMULATED — NOT MINISTRY EVIDENCE
seed_basis: public marginals or explicit design basis
evidence_class: D
source: DEMO_GENERATOR
synthetic_inputs: structured blocks
```

A scenario missing any field is rejected.

## 5. Seeding rules

### 5.1 Reconcile to public marginals

Synthetic detail must reconcile to known public totals wherever the concepts are compatible.

Examples:

- buyer quantities sum to or below public import quantity;
- line capacities do not exceed disclosed plant nameplate without an explicit expansion assumption;
- synthetic exports/domestic allocation sum to total simulated production;
- tariff-line transactions sum to the parent HS6 public total.

### 5.2 Preserve uncertainty

Synthetic data may resolve a chosen demo question, but it must not falsely make every field perfect. A good scenario includes realistic boundaries and conditions.

### 5.3 Plant known ground truth

Each scenario has an intended correct route so the engine can be back-tested.

Steel ground truth:

```text
- material target-specification gap;
- incumbent core process exists;
- incremental finishing/qualification upgrade required;
- unsupported economics fail the hurdle;
- minimum support is calculable;
- national value and competition controls pass;
- correct route = conditional brownfield ADVANCE.
```

Polypropylene ground truth:

```text
- generic imported grade is equivalent to available local grade;
- qualified availability exceeds target demand;
- no binding market failure;
- correct route = REJECT generic capacity support.
```

## 6. Steel scenario design

### 6.1 Target product

```text
Z275 structural galvanized coil for coastal construction
SASO-ASTM A653/A653M
coating 275 g/m²
thickness 0.7–1.5 mm
width 1,000–1,250 mm
customer qualification required
```

This product definition is synthetic. It is selected to demonstrate specification resolution and coastal-performance logic.

### 6.2 Capacity

```text
nameplate: 250 kt
availability: 92%
yield: 94%
qualification share: 38%
market allocation: 70%
effective qualified capacity: 57.509 kt
```

### 6.3 Demand and gap

```text
target-spec demand: 104 kt
downside demand: 100 kt
committed demand: 74 kt
announced demand: 22 kt
specification-adjusted gap: 46.491 kt
```

### 6.4 Capability truth

The capability states produce an incremental-upgrade D\* band after all hard gates are resolved.

### 6.5 Economics truth

The unsupported cash-flow fixture produces:

```text
NPV at 12%: -SAR 18m
IRR: 9.5%
S*: SAR 18m
supported NPV: 0
supported IRR: 12%
```

### 6.6 Public value truth

The scenario includes positive incremental national value after government cost, displacement, resource cost and risk.

## 7. Polypropylene scenario design

The scenario tests the opposite behavior.

```text
target demand: 56 kt
qualified equivalent local availability: 80 kt
specification-adjusted gap: -24 kt
support required: 0
correct route: no intervention
```

The result proves that adding internal data does not automatically manufacture an `ADVANCE`.

## 8. Decision and UI rules

Simulation mode must display:

- public state;
- simulated active state;
- `SIMULATED — NOT MINISTRY EVIDENCE`;
- scenario ID and seed basis;
- synthetic inputs used;
- decision calculations enabled by those inputs.

The printable simulated dossier repeats the disclosure.

## 9. Prohibited behavior

- assigning Class A/B/C to synthetic values;
- using “Ministry data” without the word simulated;
- omitting the public state when showing a simulated advance;
- exporting a simulated dossier without disclosure;
- training or calibrating thresholds from the demo scenario;
- changing synthetic values until a preferred route passes without documenting the ground truth and test;
- merging synthetic rows into public snapshot files.

## 10. Scenario validation

A scenario passes when:

1. metadata is complete;
2. public reconciliation constraints pass;
3. all units and ranges are valid;
4. intended ground truth is explicit;
5. the engine reaches the expected simulated state;
6. the public decision fingerprint is unchanged;
7. the evidence ledger labels every synthetic block;
8. the dossier discloses the scenario.

## 11. Replacement by real Ministry data

Production connectors should map actual internal records into the same canonical fields. The synthetic adapter is then disabled for official use. The engine, formulas, UI manifest and dossier contract remain unchanged.

## 12. Scenario contract 2.0.0 (S10)

Runtime accepts only `scenario_version: 2.0.0`. Historical byte-identical 1.1.0 copies live under `data/synthetic/historical/v1_1/` and are manifested but never loaded.

Optional governed blocks include `class_if_confirmed`, `tariff_line_allocation`, `buyer_allocation`, `expansion_assumption`, `production_and_retained_flows`, and `economics.minimum_efficient_scale_kt`. Gate B reconciliation emits ten ordered checks including allocation sums, expansion bounds, retained-flow reconcile, and `base_demand_and_commitment_probability_valid`.

Simulated ADVANCE uses the `CLASS_IF_CONFIRMED` advance-gate basis: declared confirmed classes gate publication while actual synthetic rows remain Class D.

## 13. Scenario contract 2.1.0 shared enablers

Runtime accepts 2.0.0 and 2.1.0. A `shared_enabler` declaration is legal only in 2.1.0 and is rejected when null, malformed, incomplete or attached to 2.0.0. The declaration contains one immutable enabler identity; kind exactly `shared_laboratory`, `treatment_facility`, `tooling`, `utility`, `input_supply`, `logistics`, `skills_programme` or `policy_instrument`; bilingual synthetic-design label; non-negative cost; explicit valuation route code 1–7; addressed constraint classes; causal-removal boolean; probability and dependency share each strictly greater than zero and at most one; six component booleans; a competition triplet; and the Class-D design basis.

The valuation route code must resolve exactly one declared route-evidence record. Route 5 retains its existing economics national-value inheritance; every other route uses its own declared national-value block. Ground truth and derived Decision or Intervention results never select or supply valuation. The valuation must be finite and positive before projection.

Gate B appends `shared_enabler_declaration_valid` as check 11. Complete-directory validation additionally requires unique scenario and dependent identities and exact agreement of kind, label, cost and components for declarations sharing an enabler ID. Evaluated aggregation counts only dependents whose probability, dependency share and positive valuation are all eligible. The governed aluminium pair remains Class D, `DEMO_GENERATOR`, scenario-attributed and visibly labelled; its computed UnlockValue is 35.28 M SAR, while routes 6 and 4 continue to win through lower-route precedence.
