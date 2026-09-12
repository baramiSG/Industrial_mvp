# 01 — Product Charter and Functional Requirements

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Product statement

The Industrial Opportunity Resolution Engine is an evidence-governed decision system that converts an HS-based industrial signal into a specification-level route:

> **REJECT, MONITOR, INVESTIGATE or ADVANCE — with the route, evidence, economics, conditions and kill condition visible.**

The MVP is designed for a Ministry demonstration. It must prove two propositions simultaneously:

1. public data is sufficient to identify material candidates, reject false capacity conclusions and name the exact fact required next; and
2. when Ministry-grade line-level records are added, the same engine can resolve effective capacity, capability distance, economics, minimum intervention, national value and route.

It is not a generic “AI opportunity ranking” dashboard. It operationalises the methodology’s decision object:

```text
Product × Specification × Application × Capability × Demand × Route
```

## 2. Target users

### 2.1 Primary

- Industrial Incentives Team analyst
- Sector/process expert
- Competition reviewer
- Fiscal/economic reviewer
- Policy decision-maker

### 2.2 Secondary

- Data steward
- Ministry plant/licence administrator
- Investment promotion specialist
- External technical reviewer
- Strategic Gears delivery team

## 3. Product promise

For every loaded opportunity, the system must answer:

1. What commercial product and application are actually being discussed?
2. What evidence triggered attention?
3. Is the apparent gap genuine, false, specification-related, capacity-related, timing-related, resilience-related or simply unresolved?
4. Can an existing Saudi plant serve the target specification?
5. What exact capability is missing?
6. Is no action, market linkage, certification, brownfield, JV or greenfield the proper route?
7. Is the route viable without support?
8. What is the minimum effective intervention, if any?
9. What is the incremental national value relative to no action?
10. What missing fact has the highest expected decision value?
11. What conditions and kill condition protect the public decision?

## 4. Operating modes

### 4.1 Public Evidence Mode

Public Mode is the real evidence branch for the MVP.

Requirements:

- use only frozen, attributable public snapshots;
- preserve source, date, period, classification, measurement and transformation;
- show FULL, DEGRADED or DISABLED execution for every rule;
- stop at `INVESTIGATE` when route-changing decision-critical evidence is unavailable; permit `ADVANCE` when actual A/B/C evidence and every methodology gate pass.
- reject generic support when public evidence is already sufficient to show no defensible gap;
- never fabricate line-level facts.

### 4.2 Ministry Simulation Mode

Simulation Mode demonstrates the effect of adding internal Ministry records.

Requirements:

- evaluate synthetic records in an isolated branch;
- keep the public `real_decision` visible and unchanged;
- label the active simulated output prominently;
- disclose every synthetic block used;
- show how internal records change specific calculations and gates;
- produce `SIMULATED ADVANCE`, `SIMULATED REJECT`, `SIMULATED MONITOR` or `SIMULATED INVESTIGATE`, never an unlabeled official result.

## 5. MVP user journeys

### Journey A — Executive overview

The user opens the application and sees:

- the evidence mode;
- the frozen snapshot date;
- the loaded golden cases;
- each public state and active state;
- total latest import value represented;
- confirmation that synthetic leakage is zero.

### Journey B — Public steel case

The user opens HS 721049 and sees:

- public trade trend and quantity-led expansion;
- concentration and unit-value diagnostic;
- verified domestic galvanising capability;
- unresolved capacity, allocation and customer qualification;
- public state `INVESTIGATE`;
- brownfield as the priority route to test;
- named internal facts that can change the route.

### Journey C — Add Ministry-grade simulation

The user switches to Ministry Simulation and sees:

- the real state remains `INVESTIGATE`;
- a visible synthetic warning;
- target specification, demand and line parameters;
- effective qualified capacity and specification-adjusted gap;
- K, U and D\*;
- unsupported NPV/IRR and minimum effective support S\*;
- incremental national value, competition ratio and EVSI;
- `SIMULATED ADVANCE — brownfield specification upgrade`;
- conditions and kill conditions;
- bilingual simulated narrative rendered from scenario text or catalogue 1.1.0 keys in both locales without English source-language islands in Arabic mode;
- simulated route hypotheses for routes 0–7 with the same precedence and maximum-defensible-ΔNV selection semantics as the public branch;
- visible `class_if_confirmed` disclosure showing assumed classes separate from the actual Class-D synthetic records.

### Journey D — Public polypropylene rejection

The user opens HS 390210 and sees:

- imports coexist with exports above 50× import value;
- quantity-led growth does not fire;
- generic capacity support is rejected;
- only a named grade/application exception may be investigated;
- the simulated internal layer confirms equivalent qualified availability and retains `REJECT`.

### Journey E — Decision Dossier

The user opens or prints a one-page dossier containing:

- state and route;
- product identity and boundary;
- demand and supply conclusion;
- gap diagnosis;
- capability route;
- economics and national value;
- competition controls;
- evidence boundary;
- conditions, kill conditions and next evidence actions.

## 6. Functional requirements

### 6.1 Authority and configuration

- **FR-001** The application shall expose the methodology version, snapshot ID and as-of date for every case.
- **FR-002** R-rule thresholds shall be loaded from a versioned YAML artifact.
- **FR-003** Sector capability weights and hard gates shall be loaded from a versioned YAML artifact.
- **FR-004** Evidence classes and synthetic isolation rules shall be loaded from a versioned policy artifact.
- **FR-005** Integrity verification shall fail on a missing or changed governed file.

### 6.2 Opportunity and evidence

- **FR-010** The application shall represent an opportunity independently of its HS code.
- **FR-011** Each public evidence record shall state source, status, class and synthetic flag.
- **FR-012** Public records shall explicitly set `synthetic_flag=false`.
- **FR-013** Synthetic records shall set `synthetic_flag=true`, scenario ID, Class D and `source=DEMO_GENERATOR`.
- **FR-014** The UI shall distinguish public and synthetic rows visually.
- **FR-015** Contradictions shall be retained rather than silently harmonised away.

### 6.3 Rule engine

- **FR-020** The engine shall evaluate and display R0, R1-F, R1-D, R2, R3, R4-F, R4-D, R5, R6, R7, R8, R9-S, R10, R11 and R12.
- **FR-021** Every rule shall return execution state, fired state, result, metrics and decision effect.
- **FR-022** R2 shall calculate log changes and quantity contribution share deterministically.
- **FR-023** R4-D shall never claim a cluster or grade.
- **FR-024** R9-S shall open capability assessment but shall not itself publish D\*.
- **FR-025** R11 shall support rejection of generic capacity claims where the evidence warrants it.

### 6.4 Capability

- **FR-030** Effective qualified capacity shall equal nameplate × availability × yield × qualification share × market allocation.
- **FR-031** Capability shall use sector-specific weights.
- **FR-032** Unknown dimensions shall contribute to U and receive the configured λ penalty.
- **FR-033** D\* shall not be published below Kmin or while a hard gate is unresolved.
- **FR-034** Published route bands shall be immediate adjacency, incremental upgrade, major line/JV and greenfield likely.
- **FR-035** The engine shall load all five methodology §6.3 sector profiles, require weights that sum to 1.0, require each configured hard gate, and fail closed on an unknown profile.
- **FR-036** Public capability shall distinguish configured profile hard gates from decision-specific gates; either unresolved set shall withhold D* and a route band.
- **FR-037** The public engine shall assess product identity, target-specification demand, domestic supply/capability, and hard regulatory/process gates from covering evidence passports.
- **FR-038** The ADVANCE gate shall use configured blocked evidence classes and resolution statuses and shall not branch on evidence source type.
- **FR-039** The engine shall execute all six typed methodology §4.2 hard exclusions and emit exactly one primary methodology §5.3 gap class.

### 6.5 Economics and policy

- **FR-040** Unsupported economics shall be calculated before intervention.
- **FR-041** The engine shall calculate NPV and IRR deterministically.
- **FR-042** S\* shall be the minimum support step that satisfies NPV and IRR hurdle controls.
- **FR-043** Incremental national value shall be relative to no action and include benefits, fiscal cost, displacement, resource cost and risk.
- **FR-044** The post-entry capacity/downside-demand ratio shall be visible.
- **FR-045** EVSI shall identify whether a named evidence action is worth obtaining.
- **FR-046** The public branch shall emit ordered route hypotheses 0–8 with pass, fail, or NOT_CALCULABLE status and evidence-backed reasons.
- **FR-047** A fully resolving lower route shall block escalation; otherwise the engine shall select maximum defensible incremental national value among feasible, additional, permissible alternatives.
- **FR-048** Route 8 shall remain NOT_CALCULABLE with GRAPH_REQUIRED until a governed dependency graph supplies the shared-enabler calculation.
- **FR-049** Missing facts, conditions, kill conditions, and decision narratives shall be computed and rendered from a versioned bilingual catalogue rather than authored in a public snapshot.

### 6.6 Decisions

- **FR-050** Public decisions shall use only public evidence.
- **FR-051** Simulation decisions shall not mutate public decisions.
- **FR-052** Every decision shall include state, route, rationale, confidence, conditions and kill conditions.
- **FR-053** A real `ADVANCE` shall be blocked by D/E evidence in a decision-critical field.
- **FR-054** Brownfield and no-action routes shall precede supported greenfield.

### 6.9 Simulation branch

- **FR-055** Simulated route hypotheses evaluate routes 0–7 plus a route-8 `GRAPH_REQUIRED` contract without activating graph selection.
- **FR-056** Scenario contract 2.0.0 validates bilingual narratives, optional allocation/expansion/flow blocks, and fail-closed pairing with public unresolved gates.
- **FR-057** Simulated reconciliation compares tariff-line sums, buyer totals, expansion assumptions, retained flows, and base-demand probability inputs to public marginals.
- **FR-058** Simulated narratives render from scenario text when declared, otherwise from catalogue 1.1.0 keys, in both English and Arabic.
- **FR-059** UI and dossier surfaces mirror `simulation_decision` in simulated mode while `real_decision` and public `data_unlocks` remain unchanged.

### 6.7 GenUI and dossier

- **FR-060** The backend shall emit a constrained UI manifest based on the active decision context.
- **FR-061** The manifest shall use only approved component types.
- **FR-062** The UI shall adapt to available evidence; economics panels shall not appear when economics is unavailable.
- **FR-063** Runtime model output shall not generate arbitrary executable browser code.
- **FR-064** The application shall export a machine-readable dossier and printable HTML dossier.

### 6.8 Bilingual extraction

- **FR-070** Arabic and English source spans shall remain attached to normalized fields.
- **FR-071** The extraction contract shall support standard, coating, dimensions and environmental requirement fields.
- **FR-072** The offline demo extractor shall pass the labeled golden set.
- **FR-073** A future LLM adapter shall pass the same gate before it may populate a production record.

## 7. Non-functional requirements

- **NFR-001 Reproducibility:** a decision must be reproducible from frozen files and configuration.
- **NFR-002 Auditability:** every derived metric must have a deterministic formula and source pointer.
- **NFR-003 Fail-closed behavior:** unknown hard gates reduce permission, never increase it.
- **NFR-004 Offline demo:** the packaged POC shall run without API keys or live data calls.
- **NFR-005 Responsiveness:** local API responses should normally complete below 250 ms for the loaded demo cases.
- **NFR-006 Accessibility:** the interface shall use semantic controls, high contrast and keyboard-accessible navigation.
- **NFR-007 Bilingual interface and Arabic support:** All interface chrome and governed labels shall have Arabic/English content parity; the document language and direction shall switch correctly; Arabic and mixed-direction content shall render without corruption. Public and simulated engine narratives render from the governed bilingual catalogue or scenario-declared bilingual text; any remaining English-only analytical source spans outside those surfaces shall remain visibly identified and directionally isolated as source-language content.
- **NFR-008 Portability:** the demo shall run in WSL, native Linux and Docker.
- **NFR-009 Testability:** all domain calculations shall be callable independently of the web layer.
- **NFR-010 Security boundary:** no uploaded Ministry data is included in this package.

## 8. Deliberate exclusions from the MVP

- live Ministry integration;
- live customs transactions;
- production authentication and role-based approval;
- full-universe deep resolution beyond the acquired-universe screen;
- automated paid-data acquisition;
- arbitrary AI chat over decisions;
- investor CRM;
- workflow approval signatures;
- model training from Ministry applications;
- causal claims about incentive effectiveness.

These exclusions do not alter the target architecture. They keep the POC focused on proving the decision method.

## 9. MVP success criteria

The POC is successful when a Ministry audience can observe, without explanation from the developer, that:

1. the engine can refuse an unsupported factory recommendation;
2. public evidence creates meaningful decisions and precise evidence requests;
3. Ministry line-level data changes identifiable gates rather than merely “improving a score”;
4. synthetic evidence is honest and controlled;
5. calculations, thresholds and evidence are inspectable;
6. the output is a route and a Decision Dossier, not a generic ranking.

## 10. Demonstration headline

> **Public data tells us where the decision is blocked. Your line-level records make the same decision decisive.**

## 11. S13a public-universe screening requirements

- **FR-080 — Public-universe screening dispositions.** Every acquired HS6 is
  assigned `CANDIDATE`, `SCREENED_OUT`, or `NO_CANDIDATE` with a governed
  reason code. Screening never emits `ADVANCE` or a formal DecisionRecord.
- **FR-081 — Five route-specific queues without an ordinal master list.**
  Candidates may enter multiple owner-named queues; ordering is Pareto rank
  within each queue and deterministic HS6 tie order only.
- **FR-082 — Hashed reconstructible ScreeningSnapshot and API.** The offline
  engine writes a versioned input-hashed snapshot; runtime loaders and
  `/api/screening` expose summaries, queues, and drill-down without importing
  acquisition transport.
- **FR-083 — Fail-closed universe acceptance and honest UNAVAILABLE.** A Saudi
  HS6 universe exists only when every planned unit proves dataset shape,
  provider count, reporter/period/flow/partner scope, six-digit identity,
  classification continuity and duplicate absence. Otherwise the engine emits
  a zero-record typed unavailable snapshot.

The earlier MVP exclusion is limited to **deep resolution** of the full HS6
universe. S13a screens the acquired universe; deep cases remain a governed
subset.
