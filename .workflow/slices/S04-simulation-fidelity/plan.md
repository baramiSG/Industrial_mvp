# S04 Simulation-Branch Fidelity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task under the Supervisor's approval and review checkpoints. Do not dispatch further subagents unless the Supervisor explicitly directs it. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace opportunity-ID simulation dispatch with one evidence-gated data path, back-test every packaged scenario against explicit ground truth, re-evaluate R6/R7/R8 as labelled Class-D synthetic rule rows, and complete the dossier/frontend proof without changing any public decision or existing numeric fixture value.

**Architecture:** Public analysis remains the immutable first branch. A generic `_simulate(public_case, scenario)` derives capacity, capability, economics, competition, EVSI, synthetic R6/R7/R8 rows, and a state from scenario content; it checks Core 07 §7.4 before the §7.3 conjunction and otherwise returns `INVESTIGATE`. Ground truth never drives selection: the runtime and Gate B independently compare the selected `(state, route_code)` with the scenario's expected pair and fail closed on mismatch.

**Tech stack:** Python 3.11+ (CI: 3.12 and 3.14), FastAPI, PyYAML, pytest, static HTML/CSS/JavaScript, GNU Make, GitHub Actions, and `uv --locked --extra dev`.

## Global constraints

- Data classification is `confidential_demo` (`config/project.yaml:1-7`). This slice uses only frozen public evidence and explicitly synthetic Class-D demo scenarios. No secret, credential, token, personal data, unrestricted client dataset, live source, external call, or deployment action may be introduced.
- Planner persona: **Decision-Engine Architect**, holding an evidence-gated simulation and back-test stance throughout this slice (`.workflow/slices/S04-simulation-fidelity/persona.md:1-14`).
- Authority precedence is methodology DOCX → frozen Core 01–09 → versioned config → hashed data → implementation/tests (`docs/authority/00_AUTHORITY_MANIFEST.md:16-27`). The extracted Markdown is only the specified search aid (`:133-136`).
- `real_decision` remains public-only and immutable; synthetic records remain `synthetic_flag=true`, Class D, `source=DEMO_GENERATOR`, scenario-linked, and visibly disclosed (`AGENTS.md:23-34`; Manifest §6 at `docs/authority/00_AUTHORITY_MANIFEST.md:80-92`).
- Preserve Golden A public steel=`INVESTIGATE`, Golden B public polypropylene=`REJECT`, Golden A-S=`ADVANCE` route 5, and Golden B-S=`REJECT` route 0. No public snapshot, golden expectation, numeric scenario input, threshold, sector profile, evidence policy, frozen core file, or methodology file changes.
- The only governed hand-edits are `data/synthetic/SYN-MINISTRY-STEEL-001.json` and `data/synthetic/SYN-MINISTRY-PP-001.json`, exactly as §8 specifies. They add metadata/narrative only; every existing numeric and `seed_basis` value remains byte-for-byte unchanged.
- `scripts/build_manifests.py` runs exactly once and only after §24's pre-generator regression and governed-diff audit. It may update only the two synthetic entries in `data/manifests/snapshot_manifest.json` plus `generated_on` if the date differs. `docs/authority/authority_hashes.json` must have no semantic entry change; `generated_on` is the only permitted diff.
- Threshold comparisons read `thresholds["rules"]["R6"]`, `["R7"]`, `["R8"]`, `thresholds["capability"]["route_bands"]["incremental_upgrade_max"]`, and `thresholds["competition"]["post_entry_capacity_to_downside_demand_warning"]`. No configured numeric comparison literal enters `src/**`.
- Missing R6/R7/R8 inputs remain `NOT_CALCULABLE`. Do not invent a sustained-period observation, base demand, commitment probability, minimum efficient scale, Ministry record, or official evidence class.
- The R6 shortage denominator is effective qualified capacity: `max(0 is not applied; signed shortage ratio) = (target-specification demand − effective qualified capacity) / effective qualified capacity`. A zero/missing denominator is `NOT_CALCULABLE`, never coerced.
- Test-first is mandatory. Observe the intended RED before each production change, make the minimum GREEN change, then refactor only while green. Characterization tests for already-present TL-07 behavior are explicitly identified and need not manufacture a false RED.
- Every command uses the detached-script + complete-log-read protocol in §26. No direct interactive execution, no `cat`/`tail`, and no empty-output retry beyond two attempts.
- All new public Python functions have complete type hints; no bare `except`; no new dependency. No CSS edit is planned. Existing `.synthetic-row` and `.exec-*` tokenized classes are reused.
- One task at a time; every task ends **Confirm, Validate, Test**. The planner/implementer may self-check but cannot approve, push, merge, or impersonate accountable authorization.

---

## 1. Objective and decision boundary

This slice closes the three authoritative defects in `.workflow/slices/S04-simulation-fidelity/context.md:6-24`:

1. Replace `_simulate_steel`, `_simulate_pp`, and opportunity-ID branching with one data-driven path implementing Core 07 §7.4, then §7.3, then a fail-closed `INVESTIGATE` fallback.
2. Version the two scenarios and move their selected/fallback decision narrative out of code. Compare the engine's actual state/route with planted ground truth at request time and in Gate B.
3. Keep the public R0–R12 ledger unchanged, but append distinct labelled synthetic R6/R7/R8 evaluations only in simulated mode; render/export those rows and complete TL-07's two missing static assertions.

This is an implementation-fidelity and governed synthetic-fixture change, not a methodology or threshold change. Scenario `ground_truth` is an oracle for detecting engine drift, never an input to route selection. Scenario narrative supplies presentation text only, never control truth.

## 2. Requirements and acceptance IDs

| ID | Required behavior | Governing source | Planned proof |
|---|---|---|---|
| FR-020 | Evaluate/display all rules, including simulation-specific R6/R7/R8 results | Core 01 `docs/core/01_PRODUCT_AND_REQUIREMENTS.md:163-170`; Core 02 `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md:50-55` | synthetic-rule unit/API/dossier/frontend tests |
| FR-021 | Each rule exposes execution, fired, result, metrics, and effect | Core 01 `:163-170`; Core 07 `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md:7-27` | exact row-schema assertions |
| FR-052 | Every selected decision has state, route, rationale, confidence, conditions, and kill conditions | Core 01 `:190-198`; Core 07 `:253-266` | scenario-narrative equality tests and goldens |
| FR-054 | No-action and brownfield precede supported greenfield | Core 01 `:190-198`; methodology mirror `docs/authority/methodology_extracted.md:765-777` | §7.4 route 0, §7.3 route 5, no route 7 |
| FR-062 | UI adapts to available evidence rather than inventing economics | Core 01 `:198-205`; Core 03 `docs/core/03_SYSTEM_ARCHITECTURE.md:250-259` | existing GenUI tests remain green; unknown controls investigate |
| NFR-003 | Unknown hard gates reduce permission | Core 01 `:213-223`; Core 07 `:275-285` | unpublishable and missing-input cases never advance |
| INV-02 | Synthetic affects only `simulation_decision` | Manifest §6.2 `docs/authority/00_AUTHORITY_MANIFEST.md:80-86`; AGENTS #1 | unchanged fingerprint test plus mismatch 422 |
| INV-03 | Every synthetic row remains Class D/generator-sourced/flagged/disclosed | Manifest §6.3 `:80-86` | exact row metadata, UI chip, dossier disclosure |
| TL-04 | Golden A/A-S/B/B-S remain exact | Core 09 `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:45-105` | expanded `test_golden_cases.py` |
| TL-07 | Mode toggle, warning, states together, dossier action, RTL, offline assets | Core 09 `:124-134` | complete static contract suite |
| TL-09 | Public has no synthetic row; simulated rows are labelled; dossier disclosure is correct | Core 09 `:150-161` | isolation, dossier, and API tests |
| GATE-B | Scenario intended ground truth is explicit and engine reaches it | Core 06 `docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md:106-129`, `:226-237`; Core 09 `:185-191` | validator PASS/FAIL tests and repository CLI |
| GATE-C | Rule ledger visible and thresholds config-sourced | Core 09 `:192-197` | boundary tests and threshold-literal scan |
| GATE-F | Zero leakage, dual states, all synthetic rows labelled | Core 09 `:212-216` | rule/evidence/dossier/frontend tests |

## 3. Start-of-slice preflight, persona, skills, and repository state

Planner discovery:

- Persona adopted: **Decision-Engine Architect (evidence-gated simulation with back-testable scenarios)**.
- Data classification: `confidential_demo`; no restricted or real Ministry dataset is in scope.
- `superpowers:writing-plans` was read and used: this plan gives exact paths, interfaces, complete drafts, TDD-sized tasks, command evidence, and a self-audit.
- `superpowers:test-driven-development` was read and used: every behavior change has RED → GREEN ordering; existing-behavior characterization is named honestly.
- The requested plan path overrides the writing-plans skill's default path.
- `docs/project/` does not exist. Project facts used here come from `config/project.yaml`, the authority/core chain, and the authoritative S04 `context.md`; no cross-project fact is imported.
- Branch command observed `slice/S04-simulation-fidelity`.
- HEAD/base command observed `ddf905d5051fe3b4468bdcd793a8a640f5040048`.
- Current workflow state records the same branch/base and `PLAN_DRAFT` (`.workflow/state.json:18-29`).
- No implementation or test command was run by the planner. The implementer must repeat branch/HEAD/status/prohibited-scan checks after an exact `PLAN_APPROVED` verdict.
- Planned staging excludes `.env`, credentials, private keys, tokens, uploaded Ministry data, `.workflow/logs/**`, virtual environments, generated scratch scripts, Windows sidecars, and every unlisted governed path. The prohibited-file/secret scanner is mandatory before work and after explicit staging.

No owner decision is inferred from a missing external orchestration path. If `${FLIGHT_CONTROL_HOME}` or `${UNIVERSAL_NEW_PROJECT_GUIDE}` is unavailable, this repository plan remains subordinate to `AGENTS.md`; the implementer must not invent replacement orchestration.

## 4. Existing-state assessment with file:line evidence

### 4.1 Opportunity-ID dispatch and embedded simulated narrative

- `_simulate_steel` occupies `src/ior_mvp/decision_engine.py:119-229`; `_simulate_pp` occupies `:232-284`.
- `analyze_simulated` compares the requested opportunity ID to `"SAU-H0-721049"` and `"SAU-H0-390210"` and dispatches to those functions at `decision_engine.py:287-306`. The final `else` emits `"No simulation implementation exists..."`, proving a new valid scenario cannot run without code.
- Steel selected narrative literals are embedded at `decision_engine.py:179-197`: route label, headline, rationale, three conditions, and three kill conditions.
- Steel fallback narrative literals are embedded at `decision_engine.py:199-210`: route label, headline, rationale, empty conditions, and empty kill conditions.
- PP selected narrative literals are embedded at `decision_engine.py:252-261`: route label, headline, rationale, one condition, and one kill condition.
- PP's competition finding `"No new capacity is proposed; redundant support is avoided."` is embedded at `decision_engine.py:279-282`.
- The complete public-only narrative inventory at `decision_engine.py:35-62` is: `"No intervention for generic capacity"`, `"REJECT — generic capacity support"`, `"Only a named specialty grade/application exception may re-enter INVESTIGATE."`, `"Brownfield priority to test"`, `"INVESTIGATE — binding constraint unresolved"`, and `"No greenfield or financial support recommendation before effective capacity and target specification are resolved."` The public rationale and kill conditions already come from the snapshot contract. These public literals are not moved in S04.
- The complete simulated narrative inventory is reproduced verbatim in §8: steel selected route/headline/rationale/three conditions/three kills (`decision_engine.py:179-197`), shared fallback route/headline/rationale/empty lists (`:199-210`), PP selected route/headline/rationale/condition/kill (`:252-261`), and PP competition finding (`:279-282`). The repeated `"SIMULATED"` confidence marker at `:185`, `:206`, and `:257` is a schema value rather than narrative and remains one generic code literal; the warning label is already scenario-sourced.
- Non-narrative comparisons remain legitimate: public `rule_id == "R11"` at `:35-38`, `mode == "public"/"simulated"` at `:327-333`, and configured opportunity iteration at `:336-363`. S04 removes only opportunity-specific simulation dispatch.

### 4.2 Public ledger reused unchanged in simulation

- `analyze_public` evaluates `rules = evaluate_rules(case)` and returns that list at `decision_engine.py:65-104`.
- `analyze_simulated` updates decision/capacity/capability/economics/competition/EVSI/evidence but never updates `public["rules"]` (`decision_engine.py:307-325`). Simulated output therefore reuses the public ledger.
- Public R6, R7, and R8 are deliberately `DISABLED` at `src/ior_mvp/rules.py:316-346`. These rows must remain exactly public; simulated mode appends three new rows rather than mutating/relabeling public evidence.
- Core 02 already maps R6/R7/R8 to internal/synthetic evidence and the two golden behaviors (`docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md:50-55`), so no frozen Core edit is needed. `docs/REQUIREMENTS_TRACEABILITY.md` will record the new concrete function.

### 4.3 Scenario contract and validation

- Both synthetic JSON files currently contain only the Core 06 §4 metadata and `synthetic_inputs`; neither has `scenario_version`, `ground_truth`, or `decision_narrative` (`data/synthetic/SYN-MINISTRY-STEEL-001.json:1-99`; `data/synthetic/SYN-MINISTRY-PP-001.json:1-65`).
- `validate_synthetic_scenario` validates required policy fields and exact class/source/label, then only checks that `synthetic_inputs` is a mapping (`src/ior_mvp/evidence.py:51-108`). It has no rejection of additive top-level keys; policy 1.1.0 therefore remains unchanged.
- Runtime reconciliation already precedes branch arithmetic (`decision_engine.py:287-299`), and typed `EvidenceIntegrityError` already maps to HTTP 422 (`src/ior_mvp/app.py:30-52`). S04 reuses this mapping.
- Gate B currently performs policy/reconciliation only and appends its report without running the decision engine (`scripts/validate_scenarios.py:65-105`). It must add the same state/route comparison as runtime.

### 4.4 Capacity, capability, economics, and selection

- Effective qualified capacity is already a pure validated formula (`src/ior_mvp/capability.py:7-18`).
- Capability publication already enforces Kmin, unresolved-hard-gate, and state-3 controls and emits a config-sourced route band (`capability.py:20-45`, `:47-120`).
- Minimum support, national value, and EVSI are deterministic (`src/ior_mvp/economics.py:42-125`).
- Steel's existing conjunction uses positive gap, publishable D*, configured incremental-upgrade bound, passing economics, positive national value, and passing competition warning (`decision_engine.py:167-177`). This is retained generically.
- PP currently returns REJECT unconditionally after reading equivalence (`decision_engine.py:242-261`); the generic engine must instead require exact `domestic_grade_equivalent is True` and `qualified_available_kt >= target_spec_demand_kt`.

### 4.5 UI, dossier, and TL-07 proof gaps

- The rule ledger currently emits unclassified `<tr>` rows and no boundary chip (`src/ior_mvp/static/app.js:255-268`).
- The evidence ledger demonstrates the reusable pattern: `.synthetic-row` and `exec-chip exec-DEGRADED` SYNTHETIC chip (`app.js:323-339`); the CSS classes already exist (`src/ior_mvp/static/styles.css:229-238`, `:251-257`).
- `renderMethodology` also renders every rule and would otherwise expose the appended rows without a boundary (`app.js:387-407`); it must use the same helper.
- `build_dossier` includes capacity and evidence counts but no synthetic-rule projection (`src/ior_mvp/dossier.py:7-63`); printable HTML has no rule section (`:65-127`).
- The implementation already displays real and active states together in `renderIntegrityBanner` (`app.js:154-171`) and already renders a keyboard-reachable `data-dossier-html` button (`:357-376`). `tests/test_static_frontend.py:7-139` lacks those two required assertions; these are characterization tests, not runtime defects.
- `genui.build_ui_manifest` already passes the complete `analysis["rules"]` list and both states (`src/ior_mvp/genui.py:6-66`) and needs no change.

### 4.6 Manifest/change gate

- The generator hashes every synthetic JSON and rewrites both manifests (`scripts/build_manifests.py:27-55`).
- Current snapshot entries are PP SHA `202bdd1ca08fea485b27f40a539f25212bd1539ce0c26c51072ce7fde304c0ec`, 2,159 bytes and steel SHA `6c8065cc848ba519246f0d99372ae0cb3166a4831b9187f14b8ea811d274fded`, 3,071 bytes (`data/manifests/snapshot_manifest.json:14-25`).
- `authority_hashes.json` contains only DOCX/core/config artifacts, none changed by S04 (`docs/authority/authority_hashes.json:1-70`).

## 5. Files and responsibilities

### Create

- `tests/test_simulation_fidelity.py` — generic selection, ground-truth separation, scenario narrative, labelled rule rows, no-ID/no-literal source audit, and unknown-input controls.
- Implementation/review evidence files under `.workflow/slices/S04-simulation-fidelity/` only in the proper implementer/Supervisor/reviewer seats.

### Governed hand-edits

- `data/synthetic/SYN-MINISTRY-STEEL-001.json` — add only the exact `scenario_version`, `ground_truth`, and `decision_narrative` in §8.1.
- `data/synthetic/SYN-MINISTRY-PP-001.json` — add only the exact blocks in §8.2.

### Modify

- `src/ior_mvp/rules.py` — add `_synthetic_rule` and `evaluate_simulated_rules`.
- `src/ior_mvp/decision_engine.py` — replace both ID-specific branches with generic `_simulate`; add scenario-contract/narrative and ground-truth helpers; append synthetic rules; expose successful back-test/version.
- `scripts/validate_scenarios.py` — run generic selection and append a blocking `ground_truth_backtest` check.
- `src/ior_mvp/dossier.py` — project and print synthetic rule rows only when present.
- `src/ior_mvp/static/app.js` — use one escaped synthetic-rule chip helper in both rule renderers.
- `tests/test_golden_cases.py` — exact A/A-S/B/B-S values and back-test assertions.
- `tests/test_synthetic_isolation.py` — prove policy accepts the additive scenario metadata while preserving Class-D controls.
- `tests/test_scenario_validation.py` — scenario contract and Gate B PASS/mismatch FAIL.
- `tests/test_api.py` — runtime mismatch returns exact typed 422 on detail and list endpoints.
- `tests/test_dossier_contract.py` — public empty/simulated labelled rule projections and HTML.
- `tests/test_static_frontend.py` — synthetic rule styling plus missing TL-07 characterization.
- `tests/test_threshold_boundaries.py` — R6 utilisation/shortage and R7 utilisation below/equal/above tests.
- `docs/implementation/API_REFERENCE.md` — additive rule/back-test schema and ground-truth mismatch error.
- `docs/ARCHITECTURE_DECISIONS.md` — replace ADR-006 with §22's Accepted text.
- `docs/BUILD_ROADMAP.md` — replace obsolete `decision_conditions` wording with final `scenario_version`/`ground_truth`/`decision_narrative` names.
- `docs/REQUIREMENTS_TRACEABILITY.md` — exact S04 pointers/status lifecycle for FR-020/021/052/054, TL-04/07, INV-02, Gate B/F.
- `docs/KNOWN_LIMITATIONS.md` — KL-07/KL-08 close-on-merge lifecycle and KL-25 exact residual wording.

### Generated exactly once; never hand-edit

- `data/manifests/snapshot_manifest.json` — only two synthetic hash/byte entries and optionally `generated_on`.
- `docs/authority/authority_hashes.json` — no semantic entry change; only `generated_on` is permitted if the date differs.

### Explicitly unchanged

- `src/ior_mvp/evidence.py`, `app.py`, `capability.py`, `economics.py`, `genui.py`, `static/styles.css`, `scripts/demo_smoke.py`, CI/Make wiring, all config, all public/golden data, all `docs/core/**`, the methodology DOCX, and Manifest §11.

### Supervisor bookkeeping, not implementer-owned completion claims

- `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, plan/implementation reviews, reviewer verdict, PR record, CI evidence, completion record, and post-merge status promotion.

## 6. Architecture and integration flow

```text
analyze_simulated(opportunity_id)
  -> analyze_public(opportunity_id)                         # immutable real branch
  -> get_synthetic_scenario(opportunity_id)                # separate repository
  -> reconcile_synthetic_scenario(scenario, public)
  -> require_scenario_reconciliation()                     # existing Gate B content checks
  -> real_before = isolated_copy(real_decision)
  -> _simulate(public, scenario)
       -> validate scenario_version / ground_truth / narrative structure
       -> calculate formula effective qualified capacity
       -> if verified equivalence + qualified availability >= target:
            state=REJECT, route=0                           # Core 07 §7.4
          else:
            calculate spec-adjusted gap, capability,
            economics, national value, competition, EVSI
            if every §7.3 control passes:
              state=ADVANCE, route=5
            else:
              state=INVESTIGATE, route=None
       -> select decision_narrative[computed state]         # text only
       -> evaluate_simulated_rules(...): R6/R7/R8
  -> evaluate_ground_truth_backtest(scenario, decision)
  -> require_ground_truth_backtest()
       -> mismatch => EvidenceIntegrityError => HTTP 422; no partial response
  -> append synthetic rules/evidence to presentation branch only
  -> assert real fingerprint unchanged
  -> expose integrity.ground_truth_backtest

Gate B:
  sorted packaged/temp scenario + matching raw public case
  -> existing policy and reconciliation
  -> same _simulate() selection
  -> same evaluate_ground_truth_backtest()
  -> append ground_truth_backtest PASS/FAIL check
  -> exit 0 all PASS / 1 domain FAIL / 2 execution-input error
```

Concurrency remains request-local: `_simulate` and rule/back-test helpers return new dictionaries and never mutate the cached scenario or public snapshot. Only the already-isolated analysis response is enriched after both integrity gates pass.

## 7. Exact API/data contracts

### 7.1 Scenario metadata

Both packaged scenarios add:

```json
{
  "scenario_version": "1.1.0",
  "ground_truth": {
    "expected_simulation_state": "ADVANCE | REJECT",
    "expected_route_code": 5,
    "basis": "authority citation and planted-ground-truth rationale"
  },
  "decision_narrative": {
    "ADVANCE": {
      "headline": "verbatim fixture text",
      "route_label": "verbatim fixture text",
      "rationale": "verbatim fixture text",
      "conditions": [],
      "kill_conditions": [],
      "competition_finding": "optional; PP REJECT only"
    },
    "INVESTIGATE": {
      "headline": "SIMULATED INVESTIGATE — one or more gates remain unresolved",
      "route_label": "Simulation controls did not all pass",
      "rationale": "The simulated branch did not satisfy every hard gate.",
      "conditions": [],
      "kill_conditions": []
    }
  }
}
```

The shown selected key is the steel form; PP uses `REJECT` exactly as §8.2. `expected_route_code` is integer or null. Valid expected states use the existing enum. `decision_narrative` must contain entries for `ground_truth.expected_simulation_state` and `INVESTIGATE`. Runtime accepts only versions in `SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})`; a missing/unsupported version, malformed required narrative, or computed state without a narrative raises `EvidenceIntegrityError`, never `KeyError`.

### 7.2 Successful back-test response

Only successful simulated responses add:

```json
{
  "integrity": {
    "ground_truth_backtest": {
      "expected": {"state": "ADVANCE", "route_code": 5},
      "actual": {"state": "ADVANCE", "route_code": 5},
      "match": true
    }
  },
  "simulation_scenario": {
    "scenario_id": "SYN-MINISTRY-STEEL-001",
    "scenario_version": "1.1.0",
    "display_label": "SIMULATED — NOT MINISTRY EVIDENCE",
    "seed_basis": "unchanged existing text"
  }
}
```

On mismatch there is no analysis body:

```json
{
  "detail": {
    "code": "EVIDENCE_INTEGRITY_ERROR",
    "message": "Synthetic scenario ground-truth back-test failed for SYN-MINISTRY-STEEL-001: expected state=REJECT, route_code=0; actual state=ADVANCE, route_code=5"
  }
}
```

### 7.3 Synthetic rule-row schema

The existing `_rule` fields remain unchanged and these fields are additive only on simulated R6/R7/R8 rows:

```json
{
  "rule_id": "R6",
  "name": "Capacity pressure",
  "execution": "DEGRADED",
  "fired": true,
  "result": "...",
  "decision_effect": "...",
  "metrics": {},
  "synthetic_flag": true,
  "scenario_id": "SYN-MINISTRY-STEEL-001",
  "source": "DEMO_GENERATOR",
  "evidence_class": "D",
  "display_label": "SIMULATED — NOT MINISTRY EVIDENCE",
  "basis": "synthetic"
}
```

Public rows remain untouched and have no true synthetic flag. Simulated `rules` contains the 15 public rows plus three appended synthetic rows in deterministic `R6`, `R7`, `R8` order. Duplicate rule IDs are intentional and distinguished by `synthetic_flag`/`basis`.

### 7.4 Capacity compatibility

- Steel preserves `nameplate_kt`, `availability`, `yield`, `qualification_share`, `market_allocation_share`, `effective_qualified_capacity_kt`, `target_spec_demand_kt`, and `specification_adjusted_gap_kt`.
- PP preserves `formula_capacity_kt`, `qualified_available_kt`, `target_spec_demand_kt`, `specification_adjusted_gap_kt`, and `domestic_grade_equivalent`.
- No existing key is renamed or removed. Raw arithmetic remains internal; API values keep existing three-decimal rounding.

### 7.5 Dossier addition

`gap_diagnosis` adds one always-present list:

```json
{
  "gap_diagnosis": {
    "public_state": "INVESTIGATE",
    "active_state": "ADVANCE",
    "capacity": {},
    "simulated_rules": []
  }
}
```

Public mode returns `[]`; simulated mode returns exactly the three labelled rule rows. Printable HTML emits a “Simulated R6–R8 ledger” section only when the list is non-empty and keeps the top synthetic disclosure.

## 8. Governed scenario additions — exact drafts

No existing line in either `synthetic_inputs` or `seed_basis` changes. Insert the following top-level keys after `scenario_id`.

### 8.1 Steel

```json
"scenario_version": "1.1.0",
"ground_truth": {
  "expected_simulation_state": "ADVANCE",
  "expected_route_code": 5,
  "basis": "Core 06 §5.3 planted ground truth; Core 07 §7.3 requires the positive gap, publishable D* within the incremental-upgrade band, passing minimum-support economics, positive incremental national value, and no competition warning supplied by this scenario."
},
"decision_narrative": {
  "ADVANCE": {
    "headline": "SIMULATED ADVANCE — brownfield specification upgrade",
    "route_label": "Conditional brownfield debottlenecking / line expansion",
    "rationale": "The simulated Ministry-grade evidence resolves a sustained target-specification gap, establishes incremental adjacency, and passes minimum-support, national-value and competition controls.",
    "conditions": [
      "Achieve customer acceptance for the named target specification.",
      "Deliver 50 kt of incremental qualified capacity within 18 months.",
      "Support is milestone-based, sunset-bound and subject to clawback."
    ],
    "kill_conditions": [
      "Committed target-specification demand falls below 72 kt.",
      "Incumbent output or another expansion closes the gap before award.",
      "Customer qualification is not achieved by the contractual milestone."
    ]
  },
  "INVESTIGATE": {
    "headline": "SIMULATED INVESTIGATE — one or more gates remain unresolved",
    "route_label": "Simulation controls did not all pass",
    "rationale": "The simulated branch did not satisfy every hard gate.",
    "conditions": [],
    "kill_conditions": []
  }
},
```

The word “sustained” is retained only because the owner required the existing narrative to move verbatim. It is never converted into an R6 observation: R6 explicitly reports `sustained_period: "NOT_CALCULABLE"` and remains `DEGRADED`.

### 8.2 Polypropylene

```json
"scenario_version": "1.1.0",
"ground_truth": {
  "expected_simulation_state": "REJECT",
  "expected_route_code": 0,
  "basis": "Core 06 §5.3 planted ground truth; Core 07 §7.4 selects REJECT route 0 when equivalent qualified availability is at least target demand."
},
"decision_narrative": {
  "REJECT": {
    "headline": "SIMULATED REJECT — no generic specification-adjusted gap",
    "route_label": "No intervention",
    "rationale": "The simulated internal grade matrix shows equivalent qualified supply above target demand; generic capacity support would be non-additional.",
    "conditions": [
      "Reopen only for a named specialty-grade exception supported by buyer evidence."
    ],
    "kill_conditions": [
      "Any proposed generic-capacity support is stopped while equivalent qualified capacity is available."
    ],
    "competition_finding": "No new capacity is proposed; redundant support is avoided."
  },
  "INVESTIGATE": {
    "headline": "SIMULATED INVESTIGATE — one or more gates remain unresolved",
    "route_label": "Simulation controls did not all pass",
    "rationale": "The simulated branch did not satisfy every hard gate.",
    "conditions": [],
    "kill_conditions": []
  }
},
```

### 8.3 Scenario validation ownership

`validate_synthetic_scenario` remains the policy validator and accepts these additive fields. `decision_engine.validate_simulation_contract` owns scenario-version, ground-truth, and narrative structure because those are engine/back-test contracts, not evidence-policy values. It requires narrative entries for `ground_truth.expected_simulation_state` and `INVESTIGATE`; `_decision_narrative` uses the typed `_required_mapping` guard so any other computed state without an entry raises `EvidenceIntegrityError`, never `KeyError`. This keeps policy 1.1.0 unchanged and avoids hard-coding scenario metadata into evidence policy.

## 9. Exact algorithms and fixture arithmetic

### 9.1 Generic state selection

1. Reconciliation succeeds before `_simulate`.
2. Calculate formula effective qualified capacity from the five existing plant-line values.
3. If an `equivalence` block exists, require a boolean `domestic_grade_equivalent` and finite non-negative `qualified_available_kt`. Use qualified availability as specification-matched supply only when equivalence is exactly true.
4. Evaluate §7.4 first: exact equivalence true **and** qualified availability `>=` target demand → `REJECT`, route 0.
5. Otherwise calculate the signed gap from target demand minus formula effective qualified capacity.
6. Calculate capability from scenario states/hard gates. Missing/unknown dimensions do not improve D*; a missing hard-gate block is an integrity error, not an empty resolved list.
7. If cash flows exist, calculate minimum support and, when present, national value and competition. Missing decision-critical controls set that control to non-passing/`NOT_CALCULABLE`; malformed types raise `EvidenceIntegrityError`.
8. §7.3 advances only when all are true: gap > 0; `route_publishable`; `d_star` present and `<=` configured incremental-upgrade maximum; economics `passes`; national value `positive`; competition default warning passes. Select route 5.
9. Any non-equivalence case not satisfying every §7.3 control is `INVESTIGATE`, route null.
10. Only after state/route selection, load the computed state's narrative through `_decision_narrative`. The scenario contract already requires entries for `ground_truth.expected_simulation_state` and `INVESTIGATE`; if computation selects another state with no entry, `_required_mapping` raises `EvidenceIntegrityError`, never `KeyError`. The narrative cannot change the computed result.
11. Compare actual and planted ground truth. Runtime raises on mismatch before enriching/returning the response; Gate B reports a blocking FAIL.

### 9.2 Steel exact arithmetic

```text
formula effective qualified capacity
= 250 × 0.92 × 0.94 × 0.38 × 0.70
= 57.5092 kt
API effective_qualified_capacity_kt = 57.509

specification-adjusted gap
= 104.0 − 57.5092
= 46.4908 kt
API gap = 46.491

D* = 0.2667; route_publishable = true; configured bound = 0.40
unsupported NPV = -18.0 SAR m
unsupported IRR = 0.095
minimum S* = 18.0 SAR m
incremental national value = 198.0 SAR m
competition ratio = (57.5092 + 50.0) / 100.0 = 1.075092
API ratio = 1.0751 <= configured 1.25
therefore §7.3 => ADVANCE, route 5
```

R6:

```text
effective utilisation = 0.89 >= configured 0.85
signed shortage ratio = (104.0 − 57.509) / 57.509 = 0.8084
0.8084 >= configured 0.10
sustained period = NOT_CALCULABLE
execution=DEGRADED, fired=true
```

R7: `0.89 > 0.70`, so it cannot fire; equivalence is absent and reported `NOT_CALCULABLE`; `execution=DEGRADED`, `fired=false`.

R8: disclose committed 74, announced 22, target 104, downside 100. Base demand, committed probability, probability-adjusted addition, and MES are absent; `execution=DISABLED`, `fired=null`.

### 9.3 PP exact arithmetic

```text
formula effective qualified capacity
= 1170 × 0.93 × 0.97 × 0.18 × 0.55
= 104.490243 kt
API formula_capacity_kt = 104.49

domestic_grade_equivalent = true
qualified_available_kt = 80.0
target_spec_demand_kt = 56.0
80.0 >= 56.0
specification-adjusted gap = 56.0 − 80.0 = -24.0
support = 0.0
therefore §7.4 => REJECT, route 0
```

R6 uses formula effective qualified capacity as denominator: utilisation `0.78 < 0.85`; shortage is negative (`(56 − 104.49) / 104.49 ≈ -0.4641`); `execution=DEGRADED` because no sustained window exists, `fired=false`.

R7 has both required current-fixture inputs: utilisation `0.78 > 0.70` and equivalence `true`; `execution=FULL`, `fired=false`; metrics also disclose qualified availability 80.

R8 discloses committed 0, announced 0, target 56, downside 51 and reports absent base/probability/MES as `NOT_CALCULABLE`; `execution=DISABLED`, `fired=null`.

### 9.4 Back-test comparison

Compare only:

```text
expected.state       = ground_truth.expected_simulation_state
expected.route_code  = ground_truth.expected_route_code
actual.state         = simulation_decision.state
actual.route_code    = simulation_decision.route_code
match                = both exact equalities
```

Headline, rationale, economics, and numeric fixture values are independently asserted by golden/narrative tests but are not back-test identity fields. This avoids allowing presentation copy to redefine route truth.

## 10. `rules.evaluate_simulated_rules` — complete draft

Add the evidence-error import, `_synthetic_rule`, `_numeric_or_none`, and `evaluate_simulated_rules` below `_rule`; keep `evaluate_rules` unchanged.

```python
from .evidence import EvidenceIntegrityError


def _synthetic_rule(
    scenario: dict[str, Any],
    rule_id: str,
    name: str,
    execution: str,
    fired: bool | None,
    result: str,
    decision_effect: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    row = _rule(
        rule_id,
        name,
        execution,
        fired,
        result,
        decision_effect,
        metrics,
    )
    row.update(
        {
            "synthetic_flag": True,
            "scenario_id": scenario["scenario_id"],
            "source": scenario["source"],
            "evidence_class": scenario["evidence_class"],
            "display_label": scenario["display_label"],
            "basis": "synthetic",
        }
    )
    return row


def _numeric_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def evaluate_simulated_rules(
    scenario: dict[str, Any],
    public_case: dict[str, Any],
    capacity: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[dict[str, Any]]:
    opportunity = public_case.get("opportunity")
    public_opportunity_id = (
        opportunity.get("id")
        if isinstance(opportunity, dict)
        else None
    )
    if scenario.get("opportunity_id") != public_opportunity_id:
        raise EvidenceIntegrityError(
            "Synthetic rule evaluation opportunity_id does not match "
            "the public case"
        )

    inputs = scenario["synthetic_inputs"]
    demand = inputs.get("demand")
    line = inputs.get("plant_line")
    if not isinstance(demand, dict) or not isinstance(line, dict):
        raise EvidenceIntegrityError(
            "Synthetic rule evaluation requires demand and plant_line "
            "mappings"
        )

    rule_config = thresholds["rules"]
    target_demand = _numeric_or_none(
        demand.get("target_spec_demand_kt")
    )
    utilisation = _numeric_or_none(
        line.get("current_utilisation")
    )
    capacity_key = "effective_qualified_capacity_kt"
    effective_capacity = _numeric_or_none(
        capacity.get(capacity_key)
    )
    if effective_capacity is None:
        capacity_key = "formula_capacity_kt"
        effective_capacity = _numeric_or_none(
            capacity.get(capacity_key)
        )

    r6_config = rule_config["R6"]
    shortage_ratio = (
        (target_demand - effective_capacity) / effective_capacity
        if target_demand is not None
        and effective_capacity is not None
        and effective_capacity > 0
        else None
    )
    r6_fired = (
        utilisation
        >= float(r6_config["minimum_effective_utilisation"])
        and shortage_ratio
        >= float(r6_config["minimum_spec_matched_shortage"])
        if utilisation is not None and shortage_ratio is not None
        else None
    )
    r6_execution = (
        "DEGRADED" if r6_fired is not None else "DISABLED"
    )
    if r6_fired is True:
        r6_result = (
            "Synthetic utilisation and shortage proxy meet the "
            "configured R6 thresholds; sustained period is "
            "NOT_CALCULABLE."
        )
    elif r6_fired is False:
        r6_result = (
            "Synthetic R6 utilisation/shortage proxy does not meet "
            "both configured thresholds; sustained period is "
            "NOT_CALCULABLE."
        )
    else:
        r6_result = (
            "Synthetic utilisation or effective qualified capacity "
            "is unavailable; R6 is not calculable."
        )
    rows = [
        _synthetic_rule(
            scenario,
            "R6",
            "Capacity pressure",
            r6_execution,
            r6_fired,
            r6_result,
            (
                "Use as a DEGRADED capacity-pressure signal only; "
                "it cannot by itself support ADVANCE without a "
                "sustained period."
            ),
            {
                "effective_utilisation": (
                    utilisation
                    if utilisation is not None
                    else NOT_CALCULABLE
                ),
                "minimum_effective_utilisation": float(
                    r6_config["minimum_effective_utilisation"]
                ),
                "target_spec_demand_kt": (
                    target_demand
                    if target_demand is not None
                    else NOT_CALCULABLE
                ),
                "effective_qualified_capacity_kt": (
                    effective_capacity
                    if effective_capacity is not None
                    else NOT_CALCULABLE
                ),
                "effective_capacity_source_key": capacity_key,
                "shortage_ratio": (
                    round(shortage_ratio, 4)
                    if shortage_ratio is not None
                    else NOT_CALCULABLE
                ),
                "shortage_denominator": (
                    "effective_qualified_capacity_kt"
                ),
                "minimum_spec_matched_shortage": float(
                    r6_config["minimum_spec_matched_shortage"]
                ),
                "sustained_period": NOT_CALCULABLE,
            },
        )
    ]

    r7_config = rule_config["R7"]
    maximum_utilisation = float(
        r7_config["maximum_effective_utilisation"]
    )
    equivalence = inputs.get("equivalence")
    equivalence_value = (
        equivalence.get("domestic_grade_equivalent")
        if isinstance(equivalence, dict)
        else None
    )
    equivalence_known = isinstance(equivalence_value, bool)
    equivalence_required = bool(
        r7_config["require_specification_equivalence"]
    )
    if utilisation is None:
        r7_fired: bool | None = None
    elif utilisation > maximum_utilisation:
        r7_fired = False
    elif equivalence_required and not equivalence_known:
        r7_fired = None
    else:
        r7_fired = (
            utilisation <= maximum_utilisation
            and (
                not equivalence_required
                or equivalence_value is True
            )
        )
    if utilisation is None:
        r7_execution = "DISABLED"
    elif equivalence_known:
        r7_execution = "FULL"
    else:
        r7_execution = "DEGRADED"
    if r7_fired is True:
        r7_result = (
            "Synthetic utilisation and specification equivalence "
            "meet the configured latent-capacity test."
        )
    elif r7_fired is False:
        r7_result = (
            "Synthetic utilisation/equivalence does not meet the "
            "configured latent-capacity test."
        )
    else:
        r7_result = (
            "Synthetic latent capacity is not calculable because a "
            "required utilisation or equivalence input is absent."
        )
    rows.append(
        _synthetic_rule(
            scenario,
            "R7",
            "Latent domestic capacity",
            r7_execution,
            r7_fired,
            r7_result,
            (
                "Test no-support, market linkage, procurement, or "
                "barrier removal only when equivalence and latent "
                "capacity are established."
            ),
            {
                "effective_utilisation": (
                    utilisation
                    if utilisation is not None
                    else NOT_CALCULABLE
                ),
                "maximum_effective_utilisation": maximum_utilisation,
                "specification_equivalence": (
                    equivalence_value
                    if equivalence_known
                    else NOT_CALCULABLE
                ),
                "qualified_available_kt": (
                    equivalence.get("qualified_available_kt")
                    if isinstance(equivalence, dict)
                    and _numeric_or_none(
                        equivalence.get("qualified_available_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
            },
        )
    )

    r8_config = rule_config["R8"]
    rows.append(
        _synthetic_rule(
            scenario,
            "R8",
            "Committed future demand",
            "DISABLED",
            None,
            (
                "Committed and announced layers are disclosed, but "
                "base demand, commitment probability, and minimum "
                "efficient scale are absent."
            ),
            (
                "Do not infer probability-adjusted demand addition "
                "or MES fill; keep committed and announced demand "
                "separate."
            ),
            {
                "base_demand_kt": NOT_CALCULABLE,
                "committed_demand_kt": (
                    demand.get("committed_demand_kt")
                    if _numeric_or_none(
                        demand.get("committed_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "announced_demand_kt": (
                    demand.get("announced_demand_kt")
                    if _numeric_or_none(
                        demand.get("announced_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "target_spec_demand_kt": (
                    target_demand
                    if target_demand is not None
                    else NOT_CALCULABLE
                ),
                "downside_demand_kt": (
                    demand.get("downside_demand_kt")
                    if _numeric_or_none(
                        demand.get("downside_demand_kt")
                    )
                    is not None
                    else NOT_CALCULABLE
                ),
                "commitment_probability": NOT_CALCULABLE,
                "probability_adjusted_committed_demand_kt": (
                    NOT_CALCULABLE
                ),
                "probability_adjusted_demand_addition": (
                    NOT_CALCULABLE
                ),
                "minimum_probability_adjusted_demand_addition": (
                    float(
                        r8_config[
                            "minimum_probability_adjusted_demand_addition"
                        ]
                    )
                ),
                "minimum_efficient_scale_kt": NOT_CALCULABLE,
                "mes_fill": NOT_CALCULABLE,
                "minimum_mes_fill": float(
                    r8_config["minimum_mes_fill"]
                ),
            },
        )
    )
    return rows
```

The R6 `fired=true` value is a degraded proxy, not a full rule or an input to §7.3 state selection. R7 short-circuits to `false` when utilisation already exceeds its maximum even if equivalence is unknown; it remains `DEGRADED` to disclose that unknown. R8 intentionally does not read hypothetical optional field names.

## 11. `decision_engine.py` generic simulation — complete draft

### 11.1 Imports and contract helpers

Add `isfinite`, `EvidenceIntegrityError`, and `evaluate_simulated_rules` imports:

```python
from math import isfinite

from .evidence import (
    EvidenceIntegrityError,
    assert_real_decision_unchanged,
    isolated_copy,
    reconcile_synthetic_scenario,
    require_scenario_reconciliation,
    synthetic_evidence_rows,
    validate_public_evidence,
)
from .rules import evaluate_rules, evaluate_simulated_rules
```

Add these helpers before `competition_warning`:

```python
SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})
VALID_SIMULATION_STATES = {
    "REJECT",
    "MONITOR",
    "INVESTIGATE",
    "ADVANCE",
}


def _required_mapping(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            f"{context}.{key} must be a mapping"
        )
    return value


def _required_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(float(value))
    ):
        raise EvidenceIntegrityError(
            f"{field} must be a finite number"
        )
    return float(value)


def validate_simulation_contract(
    scenario: dict[str, Any],
) -> None:
    version = scenario.get("scenario_version")
    if (
        not isinstance(version, str)
        or version not in SUPPORTED_SCENARIO_CONTRACT_VERSIONS
    ):
        raise EvidenceIntegrityError(
            "Synthetic scenario scenario_version is unsupported: "
            f"{version}"
        )
    ground_truth = _required_mapping(
        scenario,
        "ground_truth",
        "scenario",
    )
    expected_state = ground_truth.get(
        "expected_simulation_state"
    )
    if expected_state not in VALID_SIMULATION_STATES:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_simulation_state "
            "must be a decision state"
        )
    route_code = ground_truth.get("expected_route_code")
    if (
        route_code is not None
        and (
            isinstance(route_code, bool)
            or not isinstance(route_code, int)
        )
    ):
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_route_code "
            "must be an integer or null"
        )
    basis = ground_truth.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.basis must be a non-empty string"
        )
    narratives = _required_mapping(
        scenario,
        "decision_narrative",
        "scenario",
    )
    required_narratives = (
        (expected_state,)
        if expected_state == "INVESTIGATE"
        else (expected_state, "INVESTIGATE")
    )
    for state in required_narratives:
        narrative = _required_mapping(
            narratives,
            state,
            "scenario.decision_narrative",
        )
        for field in ("headline", "route_label", "rationale"):
            value = narrative.get(field)
            if not isinstance(value, str) or not value:
                raise EvidenceIntegrityError(
                    "scenario.decision_narrative."
                    f"{state}.{field} must be a non-empty string"
                )
        for field in ("conditions", "kill_conditions"):
            value = narrative.get(field)
            if (
                not isinstance(value, list)
                or not all(
                    isinstance(item, str)
                    for item in value
                )
            ):
                raise EvidenceIntegrityError(
                    "scenario.decision_narrative."
                    f"{state}.{field} must be a list of strings"
                )


def _decision_narrative(
    scenario: dict[str, Any],
    state: str,
) -> dict[str, Any]:
    narratives = _required_mapping(
        scenario,
        "decision_narrative",
        "scenario",
    )
    narrative = _required_mapping(
        narratives,
        state,
        "scenario.decision_narrative",
    )
    for field in ("headline", "route_label", "rationale"):
        value = narrative.get(field)
        if not isinstance(value, str) or not value:
            raise EvidenceIntegrityError(
                "scenario.decision_narrative."
                f"{state}.{field} must be a non-empty string"
            )
    for field in ("conditions", "kill_conditions"):
        value = narrative.get(field)
        if (
            not isinstance(value, list)
            or not all(isinstance(item, str) for item in value)
        ):
            raise EvidenceIntegrityError(
                "scenario.decision_narrative."
                f"{state}.{field} must be a list of strings"
            )
    finding = narrative.get("competition_finding")
    if finding is not None and (
        not isinstance(finding, str) or not finding
    ):
        raise EvidenceIntegrityError(
            "scenario.decision_narrative."
            f"{state}.competition_finding must be a non-empty string"
        )
    return narrative


def evaluate_ground_truth_backtest(
    scenario: dict[str, Any],
    simulation_decision: dict[str, Any],
) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    ground_truth = scenario["ground_truth"]
    expected = {
        "state": ground_truth["expected_simulation_state"],
        "route_code": ground_truth["expected_route_code"],
    }
    actual = {
        "state": simulation_decision.get("state"),
        "route_code": simulation_decision.get("route_code"),
    }
    return {
        "expected": expected,
        "actual": actual,
        "match": expected == actual,
    }


def ground_truth_backtest_error(
    scenario: dict[str, Any],
    report: dict[str, Any],
) -> str:
    expected = report["expected"]
    actual = report["actual"]
    return (
        "Synthetic scenario ground-truth back-test failed for "
        f"{scenario['scenario_id']}: "
        f"expected state={expected['state']}, "
        f"route_code={expected['route_code']}; "
        f"actual state={actual['state']}, "
        f"route_code={actual['route_code']}"
    )


def require_ground_truth_backtest(
    scenario: dict[str, Any],
    report: dict[str, Any],
) -> None:
    if report.get("match") is not True:
        raise EvidenceIntegrityError(
            ground_truth_backtest_error(scenario, report)
        )
```

### 11.2 Calculation helpers

Add:

```python
def _capacity_projection(
    inputs: dict[str, Any],
) -> tuple[dict[str, Any], float, float, bool]:
    line = _required_mapping(
        inputs,
        "plant_line",
        "scenario.synthetic_inputs",
    )
    demand = _required_mapping(
        inputs,
        "demand",
        "scenario.synthetic_inputs",
    )
    nameplate = _required_number(
        line.get("nameplate_kt"),
        "plant_line.nameplate_kt",
    )
    availability = _required_number(
        line.get("availability"),
        "plant_line.availability",
    )
    yield_rate = _required_number(
        line.get("yield"),
        "plant_line.yield",
    )
    qualification_share = _required_number(
        line.get("qualification_share"),
        "plant_line.qualification_share",
    )
    allocation = _required_number(
        line.get("market_allocation_share"),
        "plant_line.market_allocation_share",
    )
    formula_capacity = effective_qualified_capacity(
        nameplate,
        availability,
        yield_rate,
        qualification_share,
        allocation,
    )
    target = _required_number(
        demand.get("target_spec_demand_kt"),
        "demand.target_spec_demand_kt",
    )

    equivalence = inputs.get("equivalence")
    has_equivalence = equivalence is not None
    if has_equivalence and not isinstance(equivalence, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.equivalence must be a mapping"
        )
    if isinstance(equivalence, dict):
        equivalent = equivalence.get(
            "domestic_grade_equivalent"
        )
        if not isinstance(equivalent, bool):
            raise EvidenceIntegrityError(
                "equivalence.domestic_grade_equivalent "
                "must be boolean"
            )
        qualified_available = _required_number(
            equivalence.get("qualified_available_kt"),
            "equivalence.qualified_available_kt",
        )
        specification_supply = (
            qualified_available
            if equivalent
            else formula_capacity
        )
        raw_gap = target - specification_supply
        capacity = {
            "formula_capacity_kt": round(
                formula_capacity,
                3,
            ),
            "qualified_available_kt": qualified_available,
            "target_spec_demand_kt": target,
            "specification_adjusted_gap_kt": round(
                raw_gap,
                3,
            ),
            "domestic_grade_equivalent": equivalent,
        }
        equivalence_reject = (
            equivalent and qualified_available >= target
        )
        return (
            capacity,
            formula_capacity,
            raw_gap,
            equivalence_reject,
        )

    raw_gap = target - formula_capacity
    capacity = {
        "nameplate_kt": nameplate,
        "availability": availability,
        "yield": yield_rate,
        "qualification_share": qualification_share,
        "market_allocation_share": allocation,
        "effective_qualified_capacity_kt": round(
            formula_capacity,
            3,
        ),
        "target_spec_demand_kt": target,
        "specification_adjusted_gap_kt": round(
            raw_gap,
            3,
        ),
    }
    return capacity, formula_capacity, raw_gap, False


def _simulation_capability(
    public: dict[str, Any],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    states = inputs.get("capability_states")
    hard_gates = inputs.get("hard_gates")
    if not isinstance(states, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.capability_states "
            "must be a mapping"
        )
    if not isinstance(hard_gates, (dict, list)):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.hard_gates "
            "must be a mapping or list"
        )
    return evaluate_capability(
        public["opportunity"]["sector_profile"],
        states,
        hard_gates,
    )


def _simulation_economics(
    inputs: dict[str, Any],
    formula_capacity: float,
    thresholds: dict[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    economics_inputs = inputs.get("economics")
    demand = _required_mapping(
        inputs,
        "demand",
        "scenario.synthetic_inputs",
    )
    if not isinstance(economics_inputs, dict):
        return (
            {
                "passes": False,
                "minimum_effective_support_m": None,
                "reason": "Economics inputs are NOT_CALCULABLE.",
            },
            {
                "warning_fires": None,
                "passes_default_warning": False,
                "reason": "Competition control is NOT_CALCULABLE.",
            },
            {},
        )

    competition_config = thresholds["competition"]
    warning_threshold = float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
    if "cash_flows_without_support" in economics_inputs:
        raw_cash_flows = economics_inputs[
            "cash_flows_without_support"
        ]
        if not isinstance(raw_cash_flows, list) or not raw_cash_flows:
            raise EvidenceIntegrityError(
                "economics.cash_flows_without_support "
                "must be a non-empty list"
            )
        cash_flows = [
            _required_number(
                value,
                "economics.cash_flows_without_support",
            )
            for value in raw_cash_flows
        ]
        hurdle_rate = _required_number(
            economics_inputs.get("hurdle_rate"),
            "economics.hurdle_rate",
        )
        try:
            economics = minimum_effective_support(
                cash_flows,
                hurdle_rate,
            )
        except ValueError as exc:
            raise EvidenceIntegrityError(
                "economics cash flows or hurdle rate are invalid"
            ) from exc
        economics["instrument"] = economics_inputs.get(
            "support_instrument"
        )

        national_components = economics_inputs.get(
            "national_value"
        )
        if isinstance(national_components, dict):
            checked_components = {
                key: _required_number(
                    value,
                    f"economics.national_value.{key}",
                )
                for key, value in national_components.items()
            }
            national_value = incremental_national_value(
                checked_components
            )
        else:
            national_value = {
                "incremental_national_value_m_sar": (
                    "NOT_CALCULABLE"
                ),
                "positive": False,
            }
        economics["national_value"] = national_value

        upgrade = inputs.get("upgrade")
        downside = demand.get("downside_demand_kt")
        if isinstance(upgrade, dict) and downside is not None:
            incremental_capacity = _required_number(
                upgrade.get("incremental_capacity_kt"),
                "upgrade.incremental_capacity_kt",
            )
            downside_demand = _required_number(
                downside,
                "demand.downside_demand_kt",
            )
            if downside_demand <= 0:
                raise EvidenceIntegrityError(
                    "demand.downside_demand_kt must be positive "
                    "for competition analysis"
                )
            ratio = (
                formula_capacity + incremental_capacity
            ) / downside_demand
            warning_fires = competition_warning(
                ratio,
                competition_config,
            )
            competition = {
                "post_entry_capacity_to_downside_demand": round(
                    ratio,
                    4,
                ),
                "warning_threshold": warning_threshold,
                "warning_fires": warning_fires,
                "passes_default_warning": not warning_fires,
                "displacement_m_sar": (
                    national_components.get("displacement")
                    if isinstance(national_components, dict)
                    else "NOT_CALCULABLE"
                ),
            }
        else:
            competition = {
                "warning_threshold": warning_threshold,
                "warning_fires": None,
                "passes_default_warning": False,
                "reason": "Competition control is NOT_CALCULABLE.",
            }
        return economics, competition, national_value

    if "support_required" in economics_inputs:
        support = _required_number(
            economics_inputs.get("support_required"),
            "economics.support_required",
        )
        return (
            {
                "passes": False,
                "minimum_effective_support_m": support,
                "reason": economics_inputs.get("reason"),
            },
            {"passes_default_warning": True},
            {"positive": False},
        )

    return (
        {
            "passes": False,
            "minimum_effective_support_m": None,
            "reason": "Economics controls are NOT_CALCULABLE.",
        },
        {
            "warning_threshold": warning_threshold,
            "warning_fires": None,
            "passes_default_warning": False,
            "reason": "Competition control is NOT_CALCULABLE.",
        },
        {"positive": False},
    )
```

`formula_capacity` is passed to competition because existing steel competition uses current effective qualified capacity plus incremental capacity. PP's explicit qualified availability remains the specification-gap input and does not alter the formula-capacity diagnostic.

### 11.3 Replace `_simulate_steel` and `_simulate_pp`

Delete both functions in full and replace them with:

```python
def _simulate(
    public: dict[str, Any],
    scenario: dict[str, Any],
) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    inputs = scenario["synthetic_inputs"]
    thresholds = thresholds_config()
    (
        capacity,
        formula_capacity,
        raw_gap,
        equivalence_reject,
    ) = (
        _capacity_projection(inputs)
    )
    capability = _simulation_capability(public, inputs)
    economics, competition, national_value = (
        _simulation_economics(
            inputs,
            formula_capacity,
            thresholds,
        )
    )
    evsi_inputs = inputs.get("evsi")
    if not isinstance(evsi_inputs, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.evsi must be a mapping"
        )
    try:
        evsi = approximate_evsi(evsi_inputs)
    except (TypeError, ValueError) as exc:
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.evsi contains an invalid value"
        ) from exc

    incremental_upgrade_max = float(
        thresholds["capability"]["route_bands"][
            "incremental_upgrade_max"
        ]
    )
    advance = (
        not equivalence_reject
        and raw_gap > 0
        and capability["route_publishable"]
        and capability["d_star"] is not None
        and capability["d_star"] <= incremental_upgrade_max
        and economics["passes"]
        and national_value.get("positive") is True
        and competition["passes_default_warning"]
    )
    if equivalence_reject:
        state = "REJECT"
        route_code: int | None = 0
    elif advance:
        state = "ADVANCE"
        route_code = 5
    else:
        state = "INVESTIGATE"
        route_code = None

    narrative = _decision_narrative(scenario, state)
    decision = {
        "state": state,
        "route_code": route_code,
        "route_label": narrative["route_label"],
        "headline": narrative["headline"],
        "rationale": narrative["rationale"],
        "confidence": "SIMULATED",
        "conditions": list(narrative["conditions"]),
        "kill_conditions": list(
            narrative["kill_conditions"]
        ),
        "synthetic_flag": True,
        "display_label": scenario["display_label"],
    }
    if state == "ADVANCE":
        decision["minimum_effective_support_m_sar"] = (
            economics["minimum_effective_support_m"]
        )
    finding = narrative.get("competition_finding")
    if finding is not None:
        competition["finding"] = finding

    synthetic_rules = evaluate_simulated_rules(
        scenario,
        public,
        capacity,
        thresholds,
    )
    return {
        "simulation_decision": decision,
        "capacity": capacity,
        "capability": capability,
        "economics": economics,
        "competition": competition,
        "evsi": evsi,
        "synthetic_rules": synthetic_rules,
    }
```

There is no opportunity ID read or comparison inside `_simulate`. Route codes 0 and 5 are methodology route identities, not thresholds. The §7.4 condition is evaluated before §7.3 and equality rejects unnecessary generic capacity support.

### 11.4 Replace `analyze_simulated`

```python
def analyze_simulated(opportunity_id: str) -> dict[str, Any]:
    public = analyze_public(opportunity_id)
    scenario = get_synthetic_scenario(opportunity_id)
    if scenario is None:
        raise ValueError(
            f"No synthetic scenario is available for {opportunity_id}"
        )

    reconciliation = reconcile_synthetic_scenario(
        scenario,
        public,
    )
    require_scenario_reconciliation(reconciliation)
    real_before = isolated_copy(public["real_decision"])

    branch = _simulate(public, scenario)
    backtest = evaluate_ground_truth_backtest(
        scenario,
        branch["simulation_decision"],
    )
    require_ground_truth_backtest(scenario, backtest)

    public["mode"] = "simulated"
    public["simulation_decision"] = branch[
        "simulation_decision"
    ]
    public["active_decision"] = branch["simulation_decision"]
    public["rules"] = (
        public["rules"] + branch["synthetic_rules"]
    )
    public["capacity"] = branch["capacity"]
    public["capability"] = branch["capability"]
    public["economics"] = branch["economics"]
    public["competition"] = branch["competition"]
    public["evsi"] = branch["evsi"]
    public["synthetic_inputs_used"] = sorted(
        scenario["synthetic_inputs"].keys()
    )
    public["evidence"] = (
        public["evidence"] + synthetic_evidence_rows(scenario)
    )
    public["simulation_scenario"] = {
        "scenario_id": scenario["scenario_id"],
        "scenario_version": scenario["scenario_version"],
        "display_label": scenario["display_label"],
        "seed_basis": scenario["seed_basis"],
    }
    assert_real_decision_unchanged(
        real_before,
        public["real_decision"],
    )
    public["integrity"][
        "real_decision_unchanged_after_simulation"
    ] = True
    public["integrity"][
        "scenario_reconciliation"
    ] = reconciliation
    public["integrity"][
        "ground_truth_backtest"
    ] = backtest
    return public
```

The back-test occurs before any simulated branch field is attached to the returned analysis. Existing `app.py` converts its typed mismatch to 422; no `app.py` edit is required.

## 12. `validate_scenarios.py` back-test extension — complete draft

Add imports:

```python
from ior_mvp.decision_engine import (
    _simulate,
    evaluate_ground_truth_backtest,
    ground_truth_backtest_error,
)
```

Add this helper before `validate_scenario_directories`:

```python
def _ground_truth_check(
    scenario: dict[str, Any],
    backtest: dict[str, Any],
) -> dict[str, Any]:
    match = backtest["match"] is True
    return {
        "rule_id": "ground_truth_backtest",
        "source": (
            "Core 06 §5.3 and §10 item 5; "
            "Core 07 §7.3-§7.4"
        ),
        "formula": (
            "(actual state, actual route_code) == "
            "(expected state, expected route_code)"
        ),
        "result": "PASS" if match else "FAIL",
        "blocking": True,
        "inputs": backtest,
        "detail": (
            "Engine state and route match planted ground truth."
            if match
            else ground_truth_backtest_error(
                scenario,
                backtest,
            )
        ),
    }
```

Replace only the successful `try` body inside the scenario loop with:

```python
            validate_synthetic_scenario(scenario)
            if opportunity_id not in public_cases:
                raise EvidenceIntegrityError(
                    "No public case matches scenario "
                    f"opportunity_id={opportunity_id}"
                )
            public_case = public_cases[opportunity_id]
            report = reconcile_synthetic_scenario(
                scenario,
                public_case,
            )
            if report["status"] != "FAIL":
                branch = _simulate(public_case, scenario)
                backtest = evaluate_ground_truth_backtest(
                    scenario,
                    branch["simulation_decision"],
                )
                check = _ground_truth_check(
                    scenario,
                    backtest,
                )
                report["checks"].append(check)
                report["ground_truth_backtest"] = backtest
                if check["result"] == "FAIL":
                    report["status"] = "FAIL"
                    report["error"] = check["detail"]
            reports.append({"file": path.name, **report})
```

The existing catch remains unchanged and therefore converts malformed scenario-contract input into a scenario-level `FAIL`, while invalid JSON/I/O remains exit 2. `_print_reports` already prints `ERROR` and each check; no duplicate formatter is added.

## 13. Dossier and frontend projection — complete drafts

### 13.1 `dossier.py`

In `build_dossier`, after evidence counts, add:

```python
    simulated_rules = [
        row
        for row in analysis.get("rules", [])
        if row.get("synthetic_flag") is True
    ]
```

Replace `gap_diagnosis` with:

```python
        "gap_diagnosis": {
            "public_state": analysis["real_decision"]["state"],
            "active_state": decision["state"],
            "capacity": capacity,
            "simulated_rules": simulated_rules,
        },
```

In `render_dossier_html`, after `disclosure_html`, add:

```python
    def fired_label(value: bool | None) -> str:
        if value is True:
            return "FIRES"
        if value is False:
            return "DOES NOT FIRE"
        return "NOT EVALUABLE"

    simulated_rules = dossier["gap_diagnosis"].get(
        "simulated_rules",
        [],
    )
    simulated_rules_html = ""
    if simulated_rules:
        items = "".join(
            (
                "<li>"
                f"<strong>{e(row['rule_id'])}</strong> "
                f"· {e(row['execution'])} "
                f"· {e(fired_label(row['fired']))}"
                f"<br><span class=\"small\">{e(row['result'])}</span>"
                f"<br><span class=\"small\">{e(row['display_label'])}</span>"
                "</li>"
            )
            for row in simulated_rules
        )
        simulated_rules_html = f"""
<section class="box"><h2>Simulated R6–R8 ledger</h2><ul>{items}</ul></section>
"""
```

Insert `{simulated_rules_html}` in the existing `.grid` after Demand conclusion and before Decision conditions. All dynamic values pass through `html.escape`; no new inline style or CSS declaration is added. Public HTML emits no synthetic-rule heading because its list is empty.

### 13.2 `app.js`

Add this helper immediately after `fireText`:

```javascript
function ruleBoundaryChip(row) {
  if (!row.synthetic_flag) return "";
  return `<span class="exec-chip exec-DEGRADED" aria-label="${escapeHtml(row.display_label)}">SYNTHETIC</span>`;
}
```

Replace only the mapped row in `renderRuleLedger`:

```javascript
          ${props.rules.map((row) => `<tr class="${row.synthetic_flag ? "synthetic-row" : ""}">
            <td><b>${escapeHtml(row.rule_id)}</b> ${ruleBoundaryChip(row)}<br><span>${escapeHtml(row.name)}</span></td>
            <td><span class="exec-chip exec-${escapeHtml(row.execution)}">${escapeHtml(row.execution)}</span><br>${fireText(row.fired)}</td>
            <td>${escapeHtml(row.result)}</td>
            <td>${escapeHtml(row.decision_effect)}</td>
          </tr>`).join("")}
```

Replace only the mapped row in `renderMethodology`:

```javascript
        ${rules.map((row) => `<tr class="${row.synthetic_flag ? "synthetic-row" : ""}"><td><b>${escapeHtml(row.rule_id)}</b> ${ruleBoundaryChip(row)} · ${escapeHtml(row.name)}</td><td><span class="exec-chip exec-${escapeHtml(row.execution)}">${escapeHtml(row.execution)}</span></td><td>${fireText(row.fired)}</td><td>${escapeHtml(row.result)}</td></tr>`).join("")}
```

`renderIntegrityBanner` and `renderDecisionActions` are not edited: their existing real/active-state and dossier-action behavior is covered by new characterization tests. `styles.css` is not edited; existing classes satisfy the requested visual contract and avoid adding hard-coded CSS.

## 14. Test drafts — write and observe RED before production edits

The following are the complete S04 test additions/replacements. Existing unrelated tests remain unchanged.

### 14.1 New `tests/test_simulation_fidelity.py`

```python
from __future__ import annotations

import ast
from copy import deepcopy

import pytest

import ior_mvp.decision_engine as decision_engine
from ior_mvp.config import PROJECT_ROOT, thresholds_config
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.rules import (
    NOT_CALCULABLE,
    evaluate_simulated_rules,
)


def _scenario(opportunity_id: str) -> dict:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    return deepcopy(scenario)


def _synthetic_rules(result: dict) -> list[dict]:
    return [
        row
        for row in result["rules"]
        if row.get("synthetic_flag") is True
    ]


def _by_id(rows: list[dict], rule_id: str) -> dict:
    return next(row for row in rows if row["rule_id"] == rule_id)


def test_simulation_contract_version_and_ground_truth_are_explicit() -> None:
    expected = {
        "SAU-H0-721049": ("ADVANCE", 5),
        "SAU-H0-390210": ("REJECT", 0),
    }
    for opportunity_id, pair in expected.items():
        scenario = _scenario(opportunity_id)
        assert scenario["scenario_version"] == "1.1.0"
        assert (
            scenario["ground_truth"][
                "expected_simulation_state"
            ],
            scenario["ground_truth"]["expected_route_code"],
        ) == pair
        assert scenario["ground_truth"]["basis"]
        assert "INVESTIGATE" in scenario["decision_narrative"]


def test_supported_scenario_contract_version_is_accepted() -> None:
    scenario = _scenario("SAU-H0-721049")

    assert (
        decision_engine.SUPPORTED_SCENARIO_CONTRACT_VERSIONS
        == frozenset({"1.1.0"})
    )
    decision_engine.validate_simulation_contract(scenario)


def test_unsupported_scenario_contract_version_is_rejected() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["scenario_version"] = "1.2.0"

    with pytest.raises(
        EvidenceIntegrityError,
        match="scenario_version is unsupported: 1.2.0",
    ):
        decision_engine.validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    "field",
    ["scenario_version", "ground_truth", "decision_narrative"],
)
def test_missing_simulation_contract_field_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    del scenario[field]
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(EvidenceIntegrityError) as captured:
        decision_engine.analyze_simulated("SAU-H0-721049")

    assert field in str(captured.value)


def test_malformed_investigate_narrative_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    del scenario["decision_narrative"]["INVESTIGATE"][
        "rationale"
    ]
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(
        EvidenceIntegrityError,
        match="INVESTIGATE.rationale",
    ):
        decision_engine.analyze_simulated("SAU-H0-721049")


def test_computed_state_without_narrative_is_typed_integrity_error() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["equivalence"] = {
        "domestic_grade_equivalent": True,
        "qualified_available_kt": 104.0,
        "binding_market_failure": "none verified",
    }
    assert "REJECT" not in scenario["decision_narrative"]

    with pytest.raises(
        EvidenceIntegrityError,
        match="scenario.decision_narrative.REJECT must be a mapping",
    ):
        decision_engine._simulate(
            get_public_case("SAU-H0-721049"),
            scenario,
        )


def test_decision_narrative_is_projected_verbatim_from_scenario() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        scenario = _scenario(opportunity_id)
        result = decision_engine.analyze(
            opportunity_id,
            "simulated",
        )
        decision = result["simulation_decision"]
        narrative = scenario["decision_narrative"][
            decision["state"]
        ]

        for field in ("headline", "route_label", "rationale"):
            assert decision[field] == narrative[field]
        assert decision["conditions"] == narrative["conditions"]
        assert (
            decision["kill_conditions"]
            == narrative["kill_conditions"]
        )
        if "competition_finding" in narrative:
            assert (
                result["competition"]["finding"]
                == narrative["competition_finding"]
            )


def test_public_has_zero_synthetic_rule_rows_and_simulated_has_three() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        public = decision_engine.analyze(
            opportunity_id,
            "public",
        )
        simulated = decision_engine.analyze(
            opportunity_id,
            "simulated",
        )

        assert not any(
            row.get("synthetic_flag") is True
            for row in public["rules"]
        )
        rows = _synthetic_rules(simulated)
        assert [row["rule_id"] for row in rows] == [
            "R6",
            "R7",
            "R8",
        ]
        assert len(simulated["rules"]) == len(public["rules"]) + 3
        scenario = get_synthetic_scenario(opportunity_id)
        assert scenario is not None
        for row in rows:
            assert row["synthetic_flag"] is True
            assert row["scenario_id"] == scenario["scenario_id"]
            assert row["source"] == "DEMO_GENERATOR"
            assert row["evidence_class"] == "D"
            assert row["display_label"] == (
                "SIMULATED — NOT MINISTRY EVIDENCE"
            )
            assert row["basis"] == "synthetic"
            assert set(
                (
                    "rule_id",
                    "execution",
                    "fired",
                    "result",
                    "decision_effect",
                    "metrics",
                )
            ) <= set(row)


def test_steel_simulated_r6_r7_r8_are_evidence_faithful() -> None:
    result = decision_engine.analyze(
        "SAU-H0-721049",
        "simulated",
    )
    rows = _synthetic_rules(result)
    r6 = _by_id(rows, "R6")
    r7 = _by_id(rows, "R7")
    r8 = _by_id(rows, "R8")

    assert r6["execution"] == "DEGRADED"
    assert r6["fired"] is True
    assert r6["metrics"]["effective_utilisation"] == pytest.approx(
        0.89
    )
    assert r6["metrics"][
        "effective_qualified_capacity_kt"
    ] == pytest.approx(57.509)
    assert r6["metrics"]["shortage_ratio"] == pytest.approx(
        0.8084
    )
    assert r6["metrics"]["shortage_denominator"] == (
        "effective_qualified_capacity_kt"
    )
    assert r6["metrics"]["sustained_period"] == NOT_CALCULABLE

    assert r7["execution"] == "DEGRADED"
    assert r7["fired"] is False
    assert r7["metrics"]["effective_utilisation"] == pytest.approx(
        0.89
    )
    assert (
        r7["metrics"]["specification_equivalence"]
        == NOT_CALCULABLE
    )

    assert r8["execution"] == "DISABLED"
    assert r8["fired"] is None
    assert r8["metrics"]["committed_demand_kt"] == 74.0
    assert r8["metrics"]["announced_demand_kt"] == 22.0
    assert r8["metrics"]["target_spec_demand_kt"] == 104.0
    assert r8["metrics"]["downside_demand_kt"] == 100.0
    for key in (
        "base_demand_kt",
        "commitment_probability",
        "probability_adjusted_committed_demand_kt",
        "probability_adjusted_demand_addition",
        "minimum_efficient_scale_kt",
        "mes_fill",
    ):
        assert r8["metrics"][key] == NOT_CALCULABLE
    assert r8["metrics"][
        "minimum_probability_adjusted_demand_addition"
    ] == pytest.approx(0.20)
    assert r8["metrics"]["minimum_mes_fill"] == pytest.approx(
        0.25
    )


def test_pp_simulated_r6_r7_r8_are_evidence_faithful() -> None:
    result = decision_engine.analyze(
        "SAU-H0-390210",
        "simulated",
    )
    rows = _synthetic_rules(result)
    r6 = _by_id(rows, "R6")
    r7 = _by_id(rows, "R7")
    r8 = _by_id(rows, "R8")

    assert r6["execution"] == "DEGRADED"
    assert r6["fired"] is False
    assert r6["metrics"]["effective_utilisation"] == pytest.approx(
        0.78
    )
    assert r6["metrics"][
        "effective_qualified_capacity_kt"
    ] == pytest.approx(104.49)
    assert r6["metrics"]["shortage_ratio"] == pytest.approx(
        -0.4641
    )
    assert r6["metrics"]["sustained_period"] == NOT_CALCULABLE

    assert r7["execution"] == "FULL"
    assert r7["fired"] is False
    assert r7["metrics"]["effective_utilisation"] == pytest.approx(
        0.78
    )
    assert r7["metrics"]["specification_equivalence"] is True
    assert r7["metrics"]["qualified_available_kt"] == 80.0

    assert r8["execution"] == "DISABLED"
    assert r8["fired"] is None
    assert r8["metrics"]["committed_demand_kt"] == 0.0
    assert r8["metrics"]["announced_demand_kt"] == 0.0
    assert r8["metrics"]["target_spec_demand_kt"] == 56.0
    assert r8["metrics"]["downside_demand_kt"] == 51.0


@pytest.mark.parametrize(
    "failed_control",
    [
        "positive_gap",
        "route_publishable",
        "incremental_distance",
        "economics",
        "national_value",
        "competition",
    ],
)
def test_each_failed_steel_advance_control_selects_investigate(
    failed_control: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    inputs = scenario["synthetic_inputs"]
    if failed_control == "positive_gap":
        inputs["demand"]["target_spec_demand_kt"] = 50.0
    elif failed_control == "route_publishable":
        inputs["hard_gates"][
            "mandatory_or_customer_standard"
        ] = "unresolved"
    elif failed_control == "incremental_distance":
        for dimension in inputs["capability_states"]:
            inputs["capability_states"][dimension] = 2
    elif failed_control == "economics":
        inputs["economics"][
            "cash_flows_without_support"
        ] = [-1.0]
    elif failed_control == "national_value":
        for component in inputs["economics"]["national_value"]:
            inputs["economics"]["national_value"][component] = 0.0
    elif failed_control == "competition":
        inputs["upgrade"]["incremental_capacity_kt"] = 68.0

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )

    assert branch["simulation_decision"]["state"] == "INVESTIGATE"
    assert branch["simulation_decision"]["route_code"] is None
    assert branch["simulation_decision"]["headline"] == (
        scenario["decision_narrative"]["INVESTIGATE"][
            "headline"
        ]
    )


def test_equivalence_at_target_selects_reject_without_id_dispatch() -> None:
    scenario = _scenario("SAU-H0-721049")
    pp = _scenario("SAU-H0-390210")
    scenario["synthetic_inputs"]["equivalence"] = {
        "domestic_grade_equivalent": True,
        "qualified_available_kt": 104.0,
        "binding_market_failure": "none verified",
    }
    scenario["decision_narrative"]["REJECT"] = deepcopy(
        pp["decision_narrative"]["REJECT"]
    )

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )

    assert branch["capacity"][
        "specification_adjusted_gap_kt"
    ] == 0.0
    assert branch["simulation_decision"]["state"] == "REJECT"
    assert branch["simulation_decision"]["route_code"] == 0


def test_ground_truth_never_drives_selection_and_mismatch_fails() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    scenario["ground_truth"]["expected_route_code"] = 0

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )
    report = decision_engine.evaluate_ground_truth_backtest(
        scenario,
        branch["simulation_decision"],
    )

    assert branch["simulation_decision"]["state"] == "ADVANCE"
    assert branch["simulation_decision"]["route_code"] == 5
    assert report == {
        "expected": {"state": "REJECT", "route_code": 0},
        "actual": {"state": "ADVANCE", "route_code": 5},
        "match": False,
    }
    with pytest.raises(
        EvidenceIntegrityError,
        match="ground-truth back-test failed",
    ):
        decision_engine.require_ground_truth_backtest(
            scenario,
            report,
        )


def test_engine_source_has_no_scenario_id_dispatch_or_narrative() -> None:
    source = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "decision_engine.py"
    ).read_text(encoding="utf-8")
    assert "SAU-H0-721049" not in source
    assert "SAU-H0-390210" not in source
    assert "_simulate_steel" not in source
    assert "_simulate_pp" not in source
    literal_strings = {
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        narratives = _scenario(opportunity_id)[
            "decision_narrative"
        ]
        for narrative in narratives.values():
            values = [
                narrative["headline"],
                narrative["route_label"],
                narrative["rationale"],
                *narrative["conditions"],
                *narrative["kill_conditions"],
            ]
            if "competition_finding" in narrative:
                values.append(narrative["competition_finding"])
            for value in values:
                assert value not in literal_strings


def test_evaluate_simulated_rules_rejects_cross_case_use() -> None:
    scenario = _scenario("SAU-H0-721049")
    with pytest.raises(
        EvidenceIntegrityError,
        match="opportunity_id",
    ):
        evaluate_simulated_rules(
            scenario,
            get_public_case("SAU-H0-390210"),
            {
                "effective_qualified_capacity_kt": 57.509,
                "target_spec_demand_kt": 104.0,
            },
            thresholds_config(),
        )
```

### 14.2 Add assertions only to `tests/test_golden_cases.py`

This file is not replaced or reformatted. S04 may only **add** assertions around the existing golden proof. Every base assertion must remain verbatim; a stricter check is added beside it rather than replacing/removing its line.

Existing assertions that must remain verbatim or stricter:

- Golden A: real state `INVESTIGATE`; active state `INVESTIGATE`; real route `None`; public `d_star is None`; R1-D, R2, R3, R4-D, and R9-S each fire.
- Golden A-S: real state remains `INVESTIGATE`; simulation state `ADVANCE`; active route code 5; effective capacity `pytest.approx(57.509, abs=1e-3)`; gap `pytest.approx(46.491, abs=1e-3)`; minimum support `pytest.approx(18.0)`; incremental national value `pytest.approx(198.0)`; competition ratio `< 1.25`; real-decision-unchanged integrity is true.
- Golden B: real state `REJECT`; real route code 0; R1-D fires; R2 does not fire; R11 fires.
- Golden B-S: real state remains `REJECT`; simulation state `REJECT`; specification-adjusted gap `< 0`; minimum support `== 0`.

Add to `test_steel_public_golden_case` after the existing `d_star` assertion:

```python
    assert not any(
        row.get("synthetic_flag") is True
        for row in result["rules"]
    )
```

Add to `test_steel_simulated_golden_case` without changing any existing assertion:

```python
    assert result["simulation_decision"]["route_code"] == 5
    assert result["capability"]["d_star"] == pytest.approx(
        0.2667,
        abs=1e-4,
    )
    assert result["capability"]["route_band"]["code"] == (
        "incremental_upgrade"
    )
    assert result["economics"][
        "unsupported_npv_m"
    ] == pytest.approx(-18.0)
    assert result["economics"]["unsupported_irr"] == pytest.approx(
        0.095,
        abs=1e-5,
    )
    assert result["competition"][
        "post_entry_capacity_to_downside_demand"
    ] == pytest.approx(1.0751)
    assert result["competition"]["warning_fires"] is False
    assert result["simulation_scenario"]["scenario_version"] == (
        "1.1.0"
    )
    assert result["integrity"]["ground_truth_backtest"] == {
        "expected": {"state": "ADVANCE", "route_code": 5},
        "actual": {"state": "ADVANCE", "route_code": 5},
        "match": True,
    }
```

The exact-ratio assertion is additional; the existing `< 1.25` assertion remains.

Add to `test_polypropylene_public_golden_case` after the existing route assertion:

```python
    assert not any(
        row.get("synthetic_flag") is True
        for row in result["rules"]
    )
```

Add to `test_polypropylene_simulation_still_rejects_support` without changing the existing negative-gap or zero-support assertions:

```python
    assert result["simulation_decision"]["route_code"] == 0
    assert result["capacity"]["formula_capacity_kt"] == pytest.approx(
        104.49,
    )
    assert result["capacity"]["qualified_available_kt"] == 80.0
    assert result["capacity"]["target_spec_demand_kt"] == 56.0
    assert result["capacity"][
        "specification_adjusted_gap_kt"
    ] == -24.0
    assert result["capacity"]["domestic_grade_equivalent"] is True
    assert result["integrity"]["ground_truth_backtest"] == {
        "expected": {"state": "REJECT", "route_code": 0},
        "actual": {"state": "REJECT", "route_code": 0},
        "match": True,
    }
```

The exact `-24.0` assertion is additional; the existing `< 0` assertion remains. The existing `minimum_effective_support_m == 0` line also remains verbatim.

### 14.3 Append R6/R7 boundaries to `tests/test_threshold_boundaries.py`

Add imports:

```python
from copy import deepcopy

from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.rules import evaluate_simulated_rules
```

Append:

```python
def _synthetic_rule(
    scenario: dict,
    capacity: dict,
    rule_id: str,
) -> dict:
    rows = evaluate_simulated_rules(
        scenario,
        get_public_case(scenario["opportunity_id"]),
        capacity,
        thresholds_config(),
    )
    return next(row for row in rows if row["rule_id"] == rule_id)


@pytest.mark.parametrize(
    ("utilisation", "expected"),
    [
        (0.8499, False),
        (0.8500, True),
        (0.8501, True),
    ],
)
def test_r6_effective_utilisation_boundary(
    utilisation: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-721049")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = utilisation
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 110.0

    row = _synthetic_rule(
        scenario,
        {
            "effective_qualified_capacity_kt": 100.0,
            "target_spec_demand_kt": 110.0,
        },
        "R6",
    )

    assert row["fired"] is expected


@pytest.mark.parametrize(
    ("target_demand", "expected"),
    [
        (109.99, False),
        (110.00, True),
        (110.01, True),
    ],
)
def test_r6_specification_shortage_boundary(
    target_demand: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-721049")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = 0.85
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = target_demand

    row = _synthetic_rule(
        scenario,
        {
            "effective_qualified_capacity_kt": 100.0,
            "target_spec_demand_kt": target_demand,
        },
        "R6",
    )

    assert row["fired"] is expected


@pytest.mark.parametrize(
    ("utilisation", "expected"),
    [
        (0.6999, True),
        (0.7000, True),
        (0.7001, False),
    ],
)
def test_r7_effective_utilisation_boundary(
    utilisation: float,
    expected: bool,
) -> None:
    loaded = get_synthetic_scenario("SAU-H0-390210")
    assert loaded is not None
    scenario = deepcopy(loaded)
    scenario["synthetic_inputs"]["plant_line"][
        "current_utilisation"
    ] = utilisation

    row = _synthetic_rule(
        scenario,
        {
            "formula_capacity_kt": 104.49,
            "qualified_available_kt": 80.0,
            "target_spec_demand_kt": 56.0,
        },
        "R7",
    )

    assert row["execution"] == "FULL"
    assert row["fired"] is expected
```

R8 threshold boundaries are not fabricated because the governed scenarios have no base-demand, commitment-probability, or MES fields. KL-25 explicitly retains that limitation.

### 14.4 Append to `tests/test_synthetic_isolation.py`

```python
@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_policy_validation_accepts_additive_s04_metadata(
    opportunity_id: str,
) -> None:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    assert scenario["scenario_version"] == "1.1.0"
    assert isinstance(scenario["ground_truth"], dict)
    assert isinstance(scenario["decision_narrative"], dict)

    validate_synthetic_scenario(scenario)
```

This confirms evidence policy 1.1.0 permits additive engine metadata while continuing to validate its own exact required fields/values.

### 14.5 Change `tests/test_scenario_validation.py`

Add `validate_scenario_directories` to the existing script import:

```python
from scripts.validate_scenarios import (
    PUBLIC_DIR,
    SYNTHETIC_DIR,
    main,
    validate_scenario_directories,
)
```

In `test_repository_scenario_validator_passes_current_fixtures`, add:

```python
    assert output.count("ground_truth_backtest: PASS") == 2
```

Append:

```python
def test_validator_reports_exact_ground_truth_for_both_scenarios() -> None:
    reports = validate_scenario_directories(
        SYNTHETIC_DIR,
        PUBLIC_DIR,
    )
    by_scenario = {
        report["scenario_id"]: report
        for report in reports
    }

    assert by_scenario[
        "SYN-MINISTRY-STEEL-001"
    ]["ground_truth_backtest"] == {
        "expected": {"state": "ADVANCE", "route_code": 5},
        "actual": {"state": "ADVANCE", "route_code": 5},
        "match": True,
    }
    assert by_scenario[
        "SYN-MINISTRY-PP-001"
    ]["ground_truth_backtest"] == {
        "expected": {"state": "REJECT", "route_code": 0},
        "actual": {"state": "REJECT", "route_code": 0},
        "match": True,
    }


def test_validator_returns_one_for_ground_truth_mismatch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    scenario["ground_truth"]["expected_route_code"] = 0
    synthetic_dir, public_dir = _write_temp_fixture_pair(
        tmp_path,
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    status = main(synthetic_dir, public_dir)

    assert status == 1
    output = capsys.readouterr().out
    assert (
        "SCENARIO VALIDATION FAIL (1/1 scenarios failed)"
        in output
    )
    assert "ground_truth_backtest: FAIL" in output
    assert (
        "expected state=REJECT, route_code=0; "
        "actual state=ADVANCE, route_code=5"
    ) in output
```

The existing reconciliation exit-1 test and invalid-JSON exit-2 test remain unchanged.

### 14.6 Append to `tests/test_api.py`

```python
@pytest.mark.parametrize(
    "endpoint",
    [
        (
            "/api/opportunities/SAU-H0-721049"
            "?mode=simulated"
        ),
        "/api/opportunities?mode=simulated",
    ],
)
def test_ground_truth_mismatch_returns_422_without_partial_analysis(
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    invalid = deepcopy(scenario)
    invalid["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    invalid["ground_truth"]["expected_route_code"] = 0
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: invalid,
    )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get(endpoint)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": (
                "Synthetic scenario ground-truth back-test failed "
                "for SYN-MINISTRY-STEEL-001: "
                "expected state=REJECT, route_code=0; "
                "actual state=ADVANCE, route_code=5"
            ),
        }
    }
```

Before implementation this test is RED because the current engine ignores `ground_truth` and returns 200.

### 14.7 Change `tests/test_dossier_contract.py`

In the public dossier test, add:

```python
    assert dossier["gap_diagnosis"]["simulated_rules"] == []
```

Replace the simulated test with:

```python
def test_simulated_dossier_retains_disclosure_and_synthetic_rows() -> None:
    json_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier"
        "?mode=simulated"
    )
    html_response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        "?mode=simulated"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert (
        dossier["synthetic_disclosure"]["display_label"]
        == DISCLOSURE
    )
    assert dossier["evidence_summary"]["synthetic_records"] > 0
    rows = dossier["gap_diagnosis"]["simulated_rules"]
    assert [row["rule_id"] for row in rows] == [
        "R6",
        "R7",
        "R8",
    ]
    assert all(row["synthetic_flag"] is True for row in rows)
    assert all(row["evidence_class"] == "D" for row in rows)
    assert all(row["display_label"] == DISCLOSURE for row in rows)

    assert html_response.status_code == 200
    assert DISCLOSURE in html_response.text
    assert "Simulated R6–R8 ledger" in html_response.text
    for rule_id in ("R6", "R7", "R8"):
        assert rule_id in html_response.text
```

Also add to the public test after the existing disclosure assertions:

```python
    assert "Simulated R6–R8 ledger" not in html_response.text
```

### 14.8 Append to `tests/test_static_frontend.py`

```python
def _app_function(source: str, name: str) -> str:
    assert f"function {name}" in source
    return source.split(
        f"function {name}",
        maxsplit=1,
    )[1].split("\n}", maxsplit=1)[0]


def test_rule_ledger_visibly_labels_synthetic_rows() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    helper = _app_function(app_js, "ruleBoundaryChip")
    ledger = _app_function(app_js, "renderRuleLedger")
    methodology = _app_function(app_js, "renderMethodology")

    assert "row.synthetic_flag" in helper
    assert "escapeHtml(row.display_label)" in helper
    assert "exec-chip exec-DEGRADED" in helper
    assert "SYNTHETIC" in helper
    for block in (ledger, methodology):
        assert '"synthetic-row"' in block
        assert "ruleBoundaryChip(row)" in block


def test_integrity_banner_displays_public_and_active_states_together() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    banner = _app_function(app_js, "renderIntegrityBanner")

    assert "stateChip(props.real_state)" in banner
    assert "stateChip(props.active_state)" in banner
    assert "props.mode === \"simulated\"" in banner


def test_decision_actions_exposes_dossier_html_action() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    actions = _app_function(app_js, "renderDecisionActions")

    assert "data-dossier-html" in actions
    assert "Open dossier" in actions
    assert "<button" in actions
```

The first test is RED before `app.js` changes. The final two are expected to pass immediately as honest characterization of already-present TL-07 behavior; record that outcome rather than altering the tests to force failure.

## 15. Integration points and ordering

1. `data_repository.synthetic_scenarios()` continues to run `validate_synthetic_scenario` and cache immutable JSON. It does not merge public/synthetic data or learn ground truth.
2. `analyze_public` remains unchanged and is always called before loading/using scenario arithmetic.
3. Existing evidence-policy validation and public-marginal reconciliation remain the first two simulation gates. The new scenario-contract validation occurs inside `_simulate` after reconciliation and before calculations.
4. `_simulate` is a pure calculation/selection function usable by runtime and Gate B. It reads only `public["opportunity"]` and scenario content; raw public cases and public analysis responses both satisfy that narrow contract.
5. `evaluate_simulated_rules` consumes the already-produced capacity projection and full threshold config. It neither recalculates capability/economics nor influences selected state.
6. Runtime compares ground truth before attaching branch fields, synthetic rules, or synthetic evidence to the public analysis response.
7. `assert_real_decision_unchanged` remains the final dual-branch invariant.
8. `build_ui_manifest` already passes both states and the entire rules list. It automatically carries the appended rows without backend UI-manifest changes.
9. Existing `_safe_analysis`/opportunity list mapping turns every ground-truth `EvidenceIntegrityError` into 422 for analysis, list, manifest, and dossier routes.
10. Gate B is already mandatory immediately after integrity in CI/Make. Extending the script automatically extends both hosted Python jobs and local gates without CI YAML/Make edits.
11. Manifest generation happens only after all behavior tests and Gate B pass with the intentionally stale synthetic hashes; post-generation integrity is then required.

## 16. Failure, unknown-input, privacy, concurrency, versioning, and compatibility

### Failure behavior

- Missing scenario remains existing `ValueError` → HTTP 404.
- Reconciliation `FAIL` remains `EvidenceIntegrityError` → HTTP 422 before simulation.
- Missing/unsupported `scenario_version`, malformed ground truth/narrative, malformed required calculation types, or mismatch → `EvidenceIntegrityError` → HTTP 422. No partial analysis, manifest, or dossier is returned.
- Gate B maps policy/reconciliation/contract/back-test defects to scenario `status=FAIL` and process exit 1. JSON/I/O/YAML/execution failure remains exit 2.
- A support search that does not pass yields `economics.passes=false`; it does not raise and causes `INVESTIGATE`.
- Missing national-value or competition controls are explicit non-passing/`NOT_CALCULABLE`; they cannot advance.
- Unknown or unresolved capability remains governed by existing K/U/D*/hard-gate behavior and causes `INVESTIGATE`.
- Ground truth does not repair an engine result. Any mismatch stops runtime and Gate B.

### Unknown R-rule inputs

- R6: missing utilisation, target demand, or positive effective-capacity denominator → `DISABLED`, `fired=null`, missing metric(s)=`NOT_CALCULABLE`. Current fixtures have those values but no sustained window, so both are `DEGRADED`.
- R7: missing utilisation → `DISABLED`; known utilisation above the configured maximum deterministically yields `false`; when equivalence is absent the execution is `DEGRADED`; when both current-fixture inputs are present it is `FULL`.
- R8: both fixtures remain `DISABLED`, `fired=null`. Raw committed/announced quantities are disclosed but never converted to probability-adjusted demand; no base or MES value is inferred.

### Privacy and evidence boundary

- Added scenario text is synthetic methodology/demo narrative only. It carries no Ministry record, personal data, key, credential, or new public claim.
- Rule rows repeat the scenario's exact Class D, source, scenario ID, flag, and disclosure. They never say observed, official, or Ministry-provided.
- The selected narrative phrase “simulated Ministry-grade evidence” remains visibly under the exact `SIMULATED — NOT MINISTRY EVIDENCE` label and does not upgrade evidence class.
- No live source or network operation enters tests, Gate B, or runtime.

### Concurrency and determinism

- Cached repository objects are read-only. `_simulate`, `evaluate_simulated_rules`, back-test helpers, dossier projection, and UI manifest construction allocate new structures.
- No global mutable scenario result, timestamp, random number, environment-dependent branch, or opportunity-ID registry is added.
- Sorted scenario paths, sorted synthetic input lists, and fixed synthetic-rule order preserve deterministic output.
- Parallel API requests share only immutable cached source dictionaries; request-local analysis remains isolated.

### Versioning

- Scenario contract moves additively to `scenario_version="1.1.0"`; existing `scenario_id` values remain immutable.
- Version 1.1.0 adds ground truth and narrative but changes no numeric scenario semantics.
- Runtime fails closed on absent/unknown scenario contract versions so old data cannot silently bypass the back-test.
- Evidence policy stays 1.1.0; thresholds stay 1.1.0; sector profiles stay 1.0.0; project stays 0.1.0.

### API/UI compatibility

- All existing top-level response keys remain. `integrity.ground_truth_backtest`, `simulation_scenario.scenario_version`, rule metadata, and dossier `simulated_rules` are additive.
- Existing steel and PP `capacity` keys are preserved exactly as §7.4 lists.
- Public rule rows and count remain unchanged. Simulated consumers must tolerate 18 rows and duplicate R6/R7/R8 IDs distinguished by synthetic metadata; current UI iterates rows and needs no keying change.
- Existing public/simulated evidence rows, authority object, reconciliation report, GenUI component types, and dossier actions remain unchanged.
- No CSS, HTML structure, locale content, keyboard interaction, dependency, lockfile, endpoint, or OpenAPI route change.

## 17. Acceptance criteria

1. `decision_engine.py` contains neither packaged opportunity ID and defines neither `_simulate_steel` nor `_simulate_pp`.
2. One generic simulation path selects PP-style §7.4 REJECT first, steel-style §7.3 ADVANCE only on the full conjunction, and otherwise INVESTIGATE.
3. Equality `qualified_available_kt == target_spec_demand_kt` selects REJECT route 0.
4. Each individual §7.3 failure—gap, route publication, D* band, economics, national value, competition—selects INVESTIGATE route null in a constructed scenario.
5. Ground truth is never consulted during selection; changing only expected state/route leaves actual selection unchanged and causes a deterministic mismatch.
6. Runtime mismatch returns exact HTTP 422 for detailed and list-derived routes with no partial analysis.
7. Gate B reports `ground_truth_backtest: PASS` twice for packaged scenarios and exit 1/FAIL for a temp mismatch.
8. Both scenarios have exact `scenario_version`, `ground_truth`, and state-keyed `decision_narrative` additions; all previous numeric and `seed_basis` values are unchanged.
9. Selected decision text/conditions/kill conditions and PP competition finding equal scenario text verbatim; none remains as a quoted simulated narrative literal in `decision_engine.py`.
10. Steel A-S remains: real INVESTIGATE, simulated ADVANCE route 5, capacity 57.509, gap 46.491, D*=0.2667, NPV=-18, IRR=.095, S*=18, ΔNV=198, ratio=1.0751.
11. PP B-S remains: real REJECT, simulated REJECT route 0, formula capacity 104.49, qualified availability 80, target 56, gap=-24, support=0.
12. Public A/B outcomes and their 15-row public ledgers remain unchanged and have zero synthetic rule rows.
13. Simulated results append exactly R6/R7/R8 in that order, each with full `_rule` schema and exact synthetic flag/scenario/source/Class-D/label/basis metadata.
14. Steel R6=`DEGRADED/true`, shortage .8084, sustained `NOT_CALCULABLE`; steel R7=`DEGRADED/false`, equivalence `NOT_CALCULABLE`; R8 disabled with exact separate layers.
15. PP R6=`DEGRADED/false`; PP R7=`FULL/false`; PP R8 disabled with exact separate layers.
16. R6 utilisation and shortage and R7 utilisation below/equal/above boundaries are config-driven and pass; threshold-literal scan remains clean.
17. Public dossier has empty simulated rules/no synthetic HTML section; simulated dossier JSON/HTML lists all three labelled rows under disclosure.
18. Main rule ledger and methodology ledger apply `.synthetic-row` and an escaped SYNTHETIC chip; no CSS edit or hard-coded style is added.
19. TL-07 explicitly proves both states can render together and a keyboard-native dossier button exists, while all prior RTL/offline/warning checks remain green.
20. ADR-006 is Accepted with final field names; traceability/limitations use evidence-honest pre/post-merge lifecycle.
21. The pre-generator audit contains only the two exact synthetic hand-edits among governed files. One generator run produces only allowed manifest changes.
22. Post-generation integrity, Gate B, complete pytest, demo smoke, compile, node syntax, scans, clean pip path, Docker build, independent review, and current-head CI are green before Supervisor merge.
23. No secret/prohibited file or unintended path is staged. Planner/implementer/reviewer does not self-approve or merge.

## 18. Validators and proof obligations

Focused RED/GREEN:

- `tests/test_simulation_fidelity.py`
- `tests/test_threshold_boundaries.py` R6/R7 nodes
- `tests/test_scenario_validation.py`
- `tests/test_api.py::test_ground_truth_mismatch_returns_422_without_partial_analysis`
- `tests/test_dossier_contract.py`
- `tests/test_static_frontend.py`
- `tests/test_golden_cases.py`

Pre-generator proof (integrity intentionally omitted because scenario hashes are stale until the one approved generation):

```bash
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_prohibited_files.py
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_threshold_literals.py
PYTHONPATH=src "$UV" run --locked --extra dev python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/validate_scenarios.py
PYTHONPATH=src "$UV" run --locked --extra dev pytest -q
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/demo_smoke.py
```

After the single generator:

```bash
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/verify_integrity.py
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/validate_scenarios.py
PYTHONPATH=src "$UV" run --locked --extra dev pytest -q
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/demo_smoke.py
```

Final local proof runs `make ci`, the required raw proof trio from `.cursor/rules/20-proof.mdc`, clean-pip compatibility, and Docker as §26 Task 11 specifies. Hosted proof requires all four current-head jobs green; cancelled/skipped is not green.

## 19. Documentation and traceability lifecycle

### During implementation, before hosted CI/review

- `docs/BUILD_ROADMAP.md`: in S04, replace “Scenario `ground_truth` and `decision_conditions` blocks” with “Scenario `scenario_version`, `ground_truth`, and `decision_narrative` blocks”; preserve objective/gates.
- `docs/REQUIREMENTS_TRACEABILITY.md`:
  - FR-020 implementation: `rules.evaluate_rules` plus `rules.evaluate_simulated_rules`; test: public zero/simulated exact R6/R7/R8 and boundaries; status no higher than `IMPLEMENTED`.
  - FR-021 implementation: `_rule` plus additive synthetic row metadata; test exact schema; status no higher than `IMPLEMENTED`.
  - FR-052 implementation: `_public_decision` plus scenario-derived `_decision_narrative`; tests narrative equality/goldens; replace “partial” with `IMPLEMENTED`.
  - FR-054 implementation: generic `_simulate` §7.4 route 0 before §7.3 route 5; tests equivalence and conjunction; keep evidence-honest status.
  - INV-02 implementation: existing fingerprint plus `evaluate_ground_truth_backtest`; tests unchanged public and mismatch; status no higher than `IMPLEMENTED`.
  - TL-04 test pointer: expanded numeric goldens/back-test; status remains existing `TESTED` until current S04 evidence is promoted.
  - TL-07 pointer: `test_static_frontend` now includes states-together and dossier-action checks; set `IMPLEMENTED`, not TESTED before recorded execution/CI.
  - GATE-B pointer: reconciliation plus ground-truth back-test; status no higher than `IMPLEMENTED`.
  - GATE-F pointer: synthetic rule rows/dossier/frontend; status no higher than `IMPLEMENTED`.
- `docs/KNOWN_LIMITATIONS.md`: keep KL-07 and KL-08 under Open with resolution-pending-reviewed-merge language. Do not move them to Closed during implementation.
- Replace KL-25's text with:

```text
| KL-25 | R8 simulation is explicitly `DISABLED`/`NOT_CALCULABLE`: packaged scenarios disclose committed and announced layers but contain no governed base-demand, commitment-probability or minimum-efficient-scale field. The engine does not invent those inputs. | Values are absent from authority; raw layers remain separate and cannot fire R8. |
```

### Supervisor-only after squash merge and green current-head CI

- Promote only actually evidenced rows to `TESTED`/`COMPLETE` under the repository's status definitions and cite test evidence, PR URL, CI run, and merge SHA.
- Move KL-07 and KL-08 to Closed with actual PR/CI/merge evidence.
- Update `docs/BUILD_PROGRESS.md`, `.workflow/state.json`, ADR/conformance records, and `completion.md` with observed facts only.
- Never write a predicted test count, commit SHA, PR number, CI run, review verdict, or merge result.

No `docs/core/**` edit is made: Core 02 already maps R6/R7/R8 and their golden behavior to `rules.py`; traceability supplies the new exact function name without changing frozen authority.

## 20. API reference — exact edits

Under the complete analysis contract, replace `- R-rule ledger;` with:

```text
- R-rule ledger; simulated mode appends labelled Class-D R6/R7/R8 rows while retaining the public rows;
```

Replace `- integrity assertions.` with:

```text
- integrity assertions, including `ground_truth_backtest` (`expected`, `actual`, `match`) on successful simulated responses.
```

Replace the current evidence-integrity error line with:

```text
- evidence-integrity failure in simulated mode (policy, public-marginal reconciliation, scenario contract or ground-truth back-test): HTTP 422 with {"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", "message": ...}}; no partial analysis is returned.
```

Append beneath the simulated dossier description:

```text
Simulated dossier JSON and HTML include the labelled synthetic R6/R7/R8 evaluations; public dossier output contains none.
```

## 21. Review and authority boundary

- The implementer hands off a complete diff and evidence but never says APPROVE.
- Supervisor review must cover: authority interpretation, exact governed JSON-only additions, no opportunity IDs/narrative literals, §7.4 precedence, every §7.3 control, three-valued rule semantics, denominator, row labels, 422/no-partial behavior, Gate B exits, API compatibility, escaping/accessibility, generator audit, and documentation honesty.
- Every finding is reproduced with a failing test before a fix. A governed JSON correction after generator use stops the slice for renewed authority; the generator is not rerun.
- Only after Supervisor findings are zero does the different-model independent reviewer inspect the fixed current diff. A REJECT is fixed and reviewed again; unchanged rejected work is not repeatedly submitted.
- Planner/implementer/reviewer cannot approve, push, merge, or claim accountable public authorization. Supervisor controls explicit staging, commit, push, PR, hosted checks, and squash merge.

## 22. ADR-006 — complete Accepted text

Replace the current ADR-006 section, stopping before ADR-007, with exactly:

```markdown
## ADR-006 — Simulated-state selection is data-driven from scenario content, not opportunity IDs

**Status:** Accepted 2026-09-02.
**Context:** The v0.1.0 simulation dispatches on the two packaged opportunity IDs, embeds simulated decision narrative in `decision_engine.py`, and reuses public `DISABLED` R6/R7/R8 rows. Core 06 §5.3 and §10 require explicit planted ground truth and an engine back-test; Core 07 §7.3 and §7.4 define generic ADVANCE and no-gap REJECT selection; Core 02 §3 requires internal evidence to resolve or explicitly abstain on R6/R7/R8. Synthetic scenario edits are governed snapshot/scenario-parameter changes under Authority Manifest §5, §7.3 and §8.
**Decision:** Version both packaged scenarios as `scenario_version: "1.1.0"` and declare that support once in code as `SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})`. Add `ground_truth` with `expected_simulation_state`, `expected_route_code` and authority `basis`, and add state-keyed `decision_narrative` carrying the existing selected and INVESTIGATE fallback text verbatim. Ground truth and narrative never drive selection. One generic `_simulate` first applies Core 07 §7.4 (exact equivalence and qualified availability at least target demand → REJECT route 0), then §7.3 (positive gap, publishable D*, D* within the configured incremental-upgrade band, passing minimum-support economics, positive incremental national value and no competition warning → ADVANCE route 5), otherwise INVESTIGATE. Runtime and Gate B compare only actual/expected state and route and fail closed on mismatch. Simulated mode appends Class-D, generator-sourced, visibly labelled R6/R7/R8 rows; absent sustained-period, base-demand, probability and MES inputs remain `NOT_CALCULABLE`. The R6 shortage denominator is effective qualified capacity.
The owner's 2026-09-02 completion-build mandate is the methodology-owner approval for the two governed scenario metadata/narrative edits. No numeric scenario input, threshold, evidence policy, sector profile, public/golden snapshot, frozen core or methodology file changes. After complete regression and exact governed-diff review, `scripts/build_manifests.py` runs once; only the two synthetic snapshot-manifest entries and, if needed, generated dates may change.
**Consequences:** A conforming future scenario can use the same calculation/selection path without adding an opportunity-ID branch. A planted mismatch blocks the API with typed 422 and fails Gate B rather than changing the engine result. Public decisions and public ledgers remain untouched; simulated users and dossiers see both public rows and separately labelled synthetic R6/R7/R8 evaluations. R8 remains disabled for the packaged scenarios until governed base-demand/probability/MES inputs exist. The two public golden outcomes and all existing synthetic numeric results remain unchanged.
```

## 23. PR authority-change justification — exact text

Use this verbatim in the PR body under its own heading, adding only observed hashes/test/CI references after they exist:

```markdown
## Governed synthetic-scenario change (Manifest §5/§7.3/§8; ADR-006)

This PR changes the two packaged Class-D demo scenarios only to make their already-governed intended outcomes back-testable and to move existing simulated presentation narrative out of opportunity-specific code. `SYN-MINISTRY-STEEL-001.json` and `SYN-MINISTRY-PP-001.json` add `scenario_version: "1.1.0"`, explicit `ground_truth`, and state-keyed `decision_narrative`. No existing numeric input, seed basis, evidence class/source/label, scenario ID, public snapshot, golden expectation, threshold, sector profile, evidence policy, frozen core, or methodology byte changes.

The engine does not use ground truth to select a route. It applies Core 07 §7.4, then the complete §7.3 conjunction, otherwise INVESTIGATE; runtime and Gate B independently compare actual `(state, route_code)` with the planted pair and fail closed on mismatch. Simulated R6/R7/R8 rows are separate Class-D synthetic records. R6 remains DEGRADED because no sustained window is supplied, and R8 remains DISABLED because base demand, commitment probability and MES are absent.

The owner completion-build mandate dated 2026-09-02 is the methodology-owner approval for this governed scenario-parameter/snapshot update. `scripts/build_manifests.py` was run exactly once only after focused and full regression, Gate B back-tests, scans, compile, JavaScript syntax, smoke, unchanged A/A-S/B/B-S outcomes, and an exact two-file governed hand-diff. Generated snapshot changes are restricted to the two synthetic hash/byte entries plus `generated_on` if required; `authority_hashes.json` has no semantic entry change. Computed hashes/bytes and actual test/CI evidence are recorded in the slice evidence; no expected result was weakened to obtain green.
```

## 24. Manifest regeneration, audit, and one-run gate

Run `scripts/build_manifests.py` **exactly once**, only after all are observed and recorded:

1. Supervisor has approved this exact plan and ADR-006/scenario additions.
2. Scenario metadata, generic selection, all six §7.3 failure controls, equivalence equality, back-test, R6/R7/R8, dossier, frontend, API, boundaries, and golden focused tests pass.
3. `scripts/validate_scenarios.py` exits 0, reports both back-tests PASS, and temp tests prove mismatch exit 1 and invalid JSON exit 2.
4. Prohibited and threshold-literal scans pass.
5. Python compile and JavaScript syntax pass.
6. Complete pytest and demo smoke pass with all four golden outcomes/numbers unchanged.
7. `git diff -- data/synthetic/SYN-MINISTRY-STEEL-001.json data/synthetic/SYN-MINISTRY-PP-001.json` contains only §8 additions and no pre-existing line change.
8. `git diff -- data/manifests/snapshot_manifest.json docs/authority/authority_hashes.json` is empty before generation.
9. `git diff -- config docs/core docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx data/snapshots/public data/golden` is empty, except planned non-core documentation outside those protected paths.
10. Generator invocation count for S04 is zero.

Do not run pre-generator integrity as a success gate: it must detect the intentionally stale two synthetic hashes until the approved single generation. Do not regenerate early to make it green.

After the single invocation:

1. `data/manifests/snapshot_manifest.json` may change only:
   - `generated_on` if the generator date differs;
   - SHA-256 and byte count for `data/synthetic/SYN-MINISTRY-PP-001.json`;
   - SHA-256 and byte count for `data/synthetic/SYN-MINISTRY-STEEL-001.json`.
2. Public snapshot and golden entries, manifest version/policy/path/order, and every other hash/byte must be exact unchanged. Any other diff is a hard stop.
3. `docs/authority/authority_hashes.json` must have no file-entry change. Only `generated_on` may differ. Any hash/byte/path change is a hard stop.
4. Compute `sha256sum` and `stat --printf='%s\n'` for both synthetic files and require exact equality with generated JSON.
5. Run integrity once and investigate any failure. Never rerun the generator merely to obtain green.
6. Record actual hashes/bytes; no planner-predicted hash or byte count is a gate.

If a governed JSON byte must change after the one run, stop for renewed owner decision and plan revision. Do not run the generator a second time.

## 25. Rollback and recovery

Before commit, if ADR-006 or the scenario additions are rejected, apply a reviewed inverse patch that restores together:

- both scenario files byte-for-byte, removing only `scenario_version`, `ground_truth`, and `decision_narrative`;
- PP snapshot-manifest entry to SHA `202bdd1ca08fea485b27f40a539f25212bd1539ce0c26c51072ce7fde304c0ec`, bytes `2159`;
- steel snapshot-manifest entry to SHA `6c8065cc848ba519246f0d99372ae0cb3166a4831b9187f14b8ea811d274fded`, bytes `3071`;
- any generator-only date change;
- all dependent code/tests/docs/traceability/limitation claims.

Do not rerun the generator for rollback and do not use `git reset --hard`, `git checkout --`, clean/history rewriting, or broad file restoration. Verify restored hashes and integrity with explicit reads/commands.

After merge, rollback is one Supervisor-controlled `git revert` of the S04 squash commit followed by integrity, Gate B, complete pytest, smoke, clean-pip compatibility, Docker, and hosted CI. This preserves history and atomically reverts scenario bytes, manifest entries, implementation, tests, and documentation.

If a non-governed code/test defect is found after generation, fix it test-first without rerunning manifests. If either scenario JSON requires correction, stop and obtain renewed authority.

## 26. TDD-ordered implementation tasks

### Mandatory detached-script + log-read protocol

Every command below, including short git/scanner/focused-test commands, is executed through a uniquely named ignored script and complete log:

```bash
#!/usr/bin/env bash
set +e
(
  set -euo pipefail
  cd /home/barami/projects/industrial-opportunity-resolution-mvp
  # The body is one exact command block from Tasks 0–13.
)
status=$?
printf '\n__DONE__ status=%s\n' "$status"
exit "$status"
```

Store each script under a unique descriptive ignored name, for example `.workflow/logs/s04-t0-preflight.sh`, and launch it with the shell tool in managed background. The Task 0 launch is:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "bash .workflow/logs/s04-t0-preflight.sh > .workflow/logs/s04-t0-preflight.log 2>&1"
```

For later commands, use the task/phase names already stated in their checklist headings (for example `s04-t1-red`, `s04-t1-green`, `s04-t1-audit`, `s04-pre-manifest`, `s04-generator`, `s04-post-generator`, and `s04-final`) without changing the wrapper. Then read the **complete** corresponding `.log` with the file-read tool and require the final sentinel. Never infer success from launch, read through `cat`/`tail`, or stage scripts/logs. If launch/log output is empty, retry at most twice, then record the shell blocker and stop that command.

### Task 0: Approval and immutable preflight

**Files:** read-only.

**Interfaces:** consumes Supervisor `PLAN_APPROVED` for this exact plan; produces branch/base/status/classification/scope evidence.

- [ ] Read `plan_review.md`. Stop unless the verdict approves this exact revision and resolves any finding.
- [ ] Using the mandatory protocol, run:

```bash
git branch --show-current
git rev-parse HEAD
git status --short
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_prohibited_files.py
```

- [ ] Require branch `slice/S04-simulation-fidelity`, HEAD `ddf905d5051fe3b4468bdcd793a8a640f5040048`, and prohibited scan exit 0.
- [ ] Inventory all pre-existing Supervisor-owned changes. Preserve them and distinguish them from implementation edits.
- [ ] Record `confidential_demo`; confirm no secret/private/real Ministry data or prohibited path will enter Git.
- [ ] Confirm generator invocation count is zero and current manifest entries match §25.

**Confirm:** approved plan, exact branch/base, observed status.

**Validate:** planned path list equals §5; no unapproved governed path.

**Test:** prohibited scanner exits 0 with `__DONE__ status=0`.

### Task 1: Add the approved scenario contract bytes

**Files:** modify `tests/test_simulation_fidelity.py` initially with only its helpers and `test_simulation_contract_version_and_ground_truth_are_explicit`; modify `tests/test_synthetic_isolation.py`; then hand-edit only the two synthetic JSON files.

**Interfaces:** produces scenario contract version 1.1.0, planted state/route, and state-keyed narrative; evidence policy remains 1.1.0.

- [ ] Add the scenario-contract test and policy-additive test from §§14.1/14.4 before data edits.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_simulation_fidelity.py::test_simulation_contract_version_and_ground_truth_are_explicit \
  tests/test_synthetic_isolation.py::test_policy_validation_accepts_additive_s04_metadata \
  -q
```

- [ ] Observe the expected RED: missing `scenario_version`/`ground_truth`/`decision_narrative`, not a typo or environment failure.
- [ ] Apply §8.1/§8.2 exactly. Do not reformat or alter any existing scenario value.
- [ ] Rerun the same nodes and require GREEN.
- [ ] Using the protocol, inspect exact diffs:

```bash
git diff -- \
  data/synthetic/SYN-MINISTRY-STEEL-001.json \
  data/synthetic/SYN-MINISTRY-PP-001.json
git diff -- \
  config \
  data/snapshots/public \
  data/golden \
  docs/core \
  docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
```

- [ ] Require only §8 additions in the first output and empty protected output in the second. Do not run integrity or the generator.

**Confirm:** exact version/ground truth/narrative exists; all old bytes outside insertion points remain.

**Validate:** policy accepts additive keys; source/Class-D/label/seed/numerics unchanged.

**Test:** two focused nodes pass; governed diff is exact.

### Task 2: Re-evaluate synthetic R6/R7/R8

**Files:** complete the rule-row and boundary portions of `tests/test_simulation_fidelity.py` and `tests/test_threshold_boundaries.py`; then modify `src/ior_mvp/rules.py`.

**Interfaces:** produces `evaluate_simulated_rules(scenario, public_case, capacity, thresholds) -> list[dict[str, Any]]`.

- [ ] Add the exact rule fidelity, cross-case, and boundary tests from §§14.1/14.3.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_simulation_fidelity.py::test_evaluate_simulated_rules_rejects_cross_case_use \
  tests/test_threshold_boundaries.py::test_r6_effective_utilisation_boundary \
  tests/test_threshold_boundaries.py::test_r6_specification_shortage_boundary \
  tests/test_threshold_boundaries.py::test_r7_effective_utilisation_boundary \
  -q
```

- [ ] Observe RED because `evaluate_simulated_rules` is absent.
- [ ] Implement §10 exactly. Do not edit public `evaluate_rules`.
- [ ] Rerun boundary/cross-case nodes to GREEN.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_threshold_literals.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_threshold_boundaries.py tests/test_rules.py -q
```

**Confirm:** ordered R6/R7/R8 rows, exact synthetic metadata, denominator, and tri-state behavior.

**Validate:** all comparisons load config; R8 does not fabricate optional schema.

**Test:** boundaries/rules pass; threshold scan exits 0.

### Task 3: Replace ID dispatch with generic selection and scenario narrative

**Files:** complete generic-selection/narrative/source/missing-contract tests in `tests/test_simulation_fidelity.py`; replace the branch region in `src/ior_mvp/decision_engine.py`, initially excluding ground-truth helper/enforcement; update `analyze_simulated` to call `_simulate` and append synthetic rules.

**Interfaces:** produces `validate_simulation_contract`, `_simulate`, preserved capacity shapes, and scenario-derived decisions.

- [ ] Add these exact tests before production edits: missing contract, narrative projection, public/simulated rule count, steel/PP R6/R7/R8, six failed controls, equivalence equality, and source audit. Temporarily omit the ground-truth helper test until Task 4.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_simulation_fidelity.py -q
```

- [ ] Observe RED for missing `_simulate`/contract handling, ID dispatch, embedded narratives, and absent appended rows. Existing packaged goldens may also fail until the generic path is complete.
- [ ] Implement §§11.1–11.3 except the three ground-truth helper functions; implement the generic/analyze portion of §11.4 without back-test evaluation/exposure.
- [ ] Rerun `tests/test_simulation_fidelity.py` excluding the Task 4 ground-truth test and require GREEN.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_golden_cases.py \
  tests/test_capability_economics.py \
  tests/test_synthetic_isolation.py \
  -q
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_threshold_literals.py
```

**Confirm:** no packaged opportunity ID/narrative literal in engine; §7.4 before §7.3; fallback INVESTIGATE.

**Validate:** ground truth not yet used; public branch/fingerprint unchanged; exact capacity keys retained.

**Test:** simulation fidelity (except Task 4), legacy formula/isolation/goldens, and threshold scan pass.

### Task 4: Enforce ground truth at runtime and Gate B

**Files:** add remaining ground-truth test in `tests/test_simulation_fidelity.py`; modify `tests/test_scenario_validation.py`, `tests/test_api.py`; finish `src/ior_mvp/decision_engine.py`; modify `scripts/validate_scenarios.py`.

**Interfaces:** produces `evaluate_ground_truth_backtest`, `ground_truth_backtest_error`, `require_ground_truth_backtest`, successful `integrity.ground_truth_backtest`, runtime 422, and Gate B check.

- [ ] Add §§14.1 ground-truth separation, 14.5, and 14.6 tests first.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_simulation_fidelity.py::test_ground_truth_never_drives_selection_and_mismatch_fails \
  tests/test_scenario_validation.py::test_validator_returns_one_for_ground_truth_mismatch \
  tests/test_api.py::test_ground_truth_mismatch_returns_422_without_partial_analysis \
  -q
```

- [ ] Observe RED because no comparator, Gate B check, or runtime mismatch exists; confirm the API returns 200, not a different infrastructure error.
- [ ] Add the ground-truth helpers from §11.1, enforce/expose them exactly as §11.4, and apply §12.
- [ ] Rerun the focused nodes to GREEN.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_simulation_fidelity.py \
  tests/test_scenario_validation.py \
  tests/test_api.py \
  -q
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/validate_scenarios.py
```

- [ ] Require exactly two packaged back-test PASS lines, overall PASS, and existing reconciliation details.

**Confirm:** actual selection precedes comparison; expected pair never flows into `_simulate`.

**Validate:** mismatch is 422/exit 1 with exact expected/actual fields; invalid JSON remains exit 2.

**Test:** three files and repository Gate B pass.

### Task 5: Expand exact golden proof

**Files:** modify `tests/test_golden_cases.py` only by adding the §14.2 assertions. Do not replace or reformat the file, remove an assertion line, or substitute a stricter assertion for an existing line; keep the existing assertion and add the stricter one beside it.

**Interfaces:** freezes A/A-S/B/B-S outcomes and all S04-sensitive numeric values.

- [ ] Add the §14.2 assertions before any further production edit.
- [ ] Through the §26 detached-script + log-read protocol, diff the file against the fixed base and fail if any `assert` line was removed:

```bash
python3 - <<'PY'
import subprocess

base = "ddf905d5051fe3b4468bdcd793a8a640f5040048"
path = "tests/test_golden_cases.py"
diff = subprocess.run(
    ["git", "diff", "--unified=0", base, "--", path],
    check=True,
    capture_output=True,
    text=True,
).stdout
print(diff, end="")
removed_asserts = [
    line
    for line in diff.splitlines()
    if line.startswith("-")
    and not line.startswith("---")
    and "assert " in line
]
if removed_asserts:
    raise SystemExit(
        "Removed golden assert lines:\n"
        + "\n".join(removed_asserts)
    )
PY
```

- [ ] Record the observed `tests/test_golden_cases.py` diff and the zero-removed-assert result in `.workflow/slices/S04-simulation-fidelity/test_evidence.md`.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_golden_cases.py -q
```

- [ ] Require all four tests GREEN against the already test-driven implementation. If a new assertion fails, treat it as a defect: fix production test-first; never loosen expected authority values.

**Confirm:** public and simulated state/route pairs exact.

**Validate:** 57.509/46.491/.2667/-18/.095/18/198/1.0751 and 104.49/80/56/-24/0 exact.

**Test:** all Golden A/A-S/B/B-S assertions pass.

### Task 6: Project synthetic rules into dossier

**Files:** modify `tests/test_dossier_contract.py`, then `src/ior_mvp/dossier.py`.

**Interfaces:** produces `gap_diagnosis.simulated_rules` and conditional escaped HTML section.

- [ ] Add §14.7 tests.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_dossier_contract.py -q
```

- [ ] Observe RED for missing `simulated_rules` and HTML section.
- [ ] Apply §13.1 exactly.
- [ ] Rerun dossier contract and existing dossier API test:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_dossier_contract.py \
  tests/test_api.py::test_dossier_html_discloses_simulation \
  -q
```

**Confirm:** simulated rows include labels; public list empty/section absent.

**Validate:** every inserted dynamic HTML value escaped; no style change.

**Test:** dossier JSON/HTML suites pass.

### Task 7: Label synthetic rule rows and complete TL-07 proof

**Files:** modify `tests/test_static_frontend.py`, then `src/ior_mvp/static/app.js`; do not edit CSS.

**Interfaces:** produces one `ruleBoundaryChip` used by both rule renderers; records complete TL-07 static proof.

- [ ] Add §14.8 tests.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_static_frontend.py -q
```

- [ ] Record expected mixed RED: synthetic-rule test fails because the helper/markup is absent; states-together and dossier-action characterization already pass.
- [ ] Apply §13.2 exactly.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest tests/test_static_frontend.py -q
node --check src/ior_mvp/static/app.js
```

**Confirm:** both ledgers show `.synthetic-row` and SYNTHETIC chip.

**Validate:** dynamic label escaped, existing `<button>` keyboard semantics retained, no CSS/hardcoded token change.

**Test:** static suite and node syntax pass.

### Task 8: Documentation, ADR, and traceability

**Files:** modify only the documentation listed in §5 and create/update implementation evidence records in the authorized seat.

**Interfaces:** evidence-honest S04 mapping without predicted completion facts.

- [ ] Replace ADR-006 with §22 exactly and apply §§19–20 documentation edits.
- [ ] Keep KL-07/KL-08 open pending merge; apply KL-25 wording.
- [ ] Record RED/GREEN outputs, formula values, Gate B outputs, and assumptions in `implementation_log.md`/`test_evidence.md`; do not claim review/CI/merge.
- [ ] Run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest \
  tests/test_simulation_fidelity.py \
  tests/test_golden_cases.py \
  tests/test_scenario_validation.py \
  tests/test_dossier_contract.py \
  tests/test_api.py \
  tests/test_static_frontend.py \
  tests/test_threshold_boundaries.py \
  tests/test_threshold_literals.py \
  -q
git diff --check
```

**Confirm:** all named requirements point to code/test/validator.

**Validate:** statuses do not outrun evidence; no core/authority/config edit; ADR final names match code/data.

**Test:** focused contract suite and diff check pass.

### Task 9: Complete pre-manifest regression and exact governed audit

**Files:** ignored `.workflow/logs/s04-pre-manifest.sh/.log`; evidence record only.

**Interfaces:** produces every §24 precondition while generator count remains zero.

- [ ] Create the protocol-wrapped script with exactly:

```bash
UV="$HOME/.local/bin/uv"

PYTHONPATH=src "$UV" run --locked --extra dev \
  python scripts/check_prohibited_files.py
PYTHONPATH=src "$UV" run --locked --extra dev \
  python scripts/check_threshold_literals.py
PYTHONPATH=src "$UV" run --locked --extra dev \
  python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src "$UV" run --locked --extra dev \
  python scripts/validate_scenarios.py
PYTHONPATH=src "$UV" run --locked --extra dev pytest -q
PYTHONPATH=src "$UV" run --locked --extra dev \
  python scripts/demo_smoke.py
```

- [ ] Launch detached and read the complete log. Fix any non-governed defect test-first and rerun this suite; do not generate.
- [ ] Run a separate protocol-wrapped audit:

```bash
git diff --check
git diff -- \
  data/synthetic/SYN-MINISTRY-STEEL-001.json \
  data/synthetic/SYN-MINISTRY-PP-001.json
git diff -- \
  data/manifests/snapshot_manifest.json \
  docs/authority/authority_hashes.json
git diff -- \
  config \
  data/snapshots/public \
  data/golden \
  docs/core \
  docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
git status --short
```

- [ ] Require complete test/Gate B/smoke/scanner/syntax success, exact two-file hand-diff, empty manifests before generation, empty protected diff, and generator count zero.

**Confirm:** every §24 prerequisite is observed.

**Validate:** integrity has not been bypassed or regenerated early.

**Test:** pre-manifest suite sentinel 0 and exact audits.

### Task 10: Generate manifests exactly once and verify

**Files:** generated manifests only; evidence record.

**Interfaces:** synchronizes the two synthetic hashes/bytes and restores integrity.

- [ ] Reconfirm Task 9 evidence and generator invocation count zero.
- [ ] In a uniquely named protocol script containing no other write command, run exactly once:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/build_manifests.py
```

- [ ] Increment and record generator invocation count to one. Never launch this script again.
- [ ] Run a separate protocol audit:

```bash
git diff -- data/manifests/snapshot_manifest.json
git diff -- docs/authority/authority_hashes.json
sha256sum \
  data/synthetic/SYN-MINISTRY-STEEL-001.json \
  data/synthetic/SYN-MINISTRY-PP-001.json
stat --printf='%s %n\n' \
  data/synthetic/SYN-MINISTRY-STEEL-001.json \
  data/synthetic/SYN-MINISTRY-PP-001.json
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/verify_integrity.py
```

- [ ] Enforce §24 exactly. Stop on any disallowed diff; do not rerun the generator.

**Confirm:** exactly one invocation and only two synthetic manifest entries changed.

**Validate:** actual file hashes/bytes equal generated JSON; authority entries unchanged.

**Test:** post-generation integrity exits 0.

### Task 11: Builder self-audit and current-diff review preparation

**Files:** complete intended diff and S04 implementation/evidence records.

**Interfaces:** reviewable current diff with no fake completion.

- [ ] Audit all changed Python public functions for type hints and all exception paths for explicit handling.
- [ ] Audit scenario narrative strings against source JSON and verify none remains quoted in `decision_engine.py`.
- [ ] Audit every numeric output and R6/R7/R8 metric against §9.
- [ ] Audit response key compatibility and simulated/public row counts.
- [ ] Audit staged-intent paths against §5, protected paths, secret/prohibited patterns, and generated-diff limits.
- [ ] Using the protocol, run:

```bash
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_prohibited_files.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_threshold_literals.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/verify_integrity.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/validate_scenarios.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  pytest -q
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/demo_smoke.py
git diff --check
```

**Confirm:** code/data/docs/tests match approved plan.

**Validate:** assumptions and residual KL-25 are recorded; no unsupported completion fact.

**Test:** complete post-generation proof passes.

### Task 12: Supervisor review and independent review

**Files:** current complete diff; fixes only after test reproduction.

**Interfaces:** zero unresolved Supervisor findings, then zero unresolved different-model reviewer findings.

- [ ] Implementer hands off without an approval verdict.
- [ ] Supervisor reviews the §21 checklist on the current diff.
- [ ] Reproduce each finding with a failing test, fix, and rerun affected/full proof. A scenario JSON finding after Task 10 is a stop for renewed authority, not a second generator run.
- [ ] When Supervisor findings are zero, dispatch the independent reviewer model required by `.workflow/state.json`; record model, exact head/diff, findings, fixes, and verdict.
- [ ] Do not rerun a reviewer on unchanged rejected work. Do not self-approve.

**Confirm:** reviews cover the fixed current diff.

**Validate:** model separation and authority boundaries hold.

**Test:** every fix's focused test and full local proof are current.

### Task 13: Final local gates, explicit staging, PR, current-head CI, and merge gate

**Files:** reviewed intended paths only; ignored scripts/logs/venvs never stage.

**Interfaces:** final local evidence and Supervisor-controlled PR/CI/merge records.

- [ ] Create a protocol-wrapped `.workflow/logs/s04-final.sh` containing:

```bash
make ci

source .venv/bin/activate
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src python3 scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/demo_smoke.py
deactivate

pip_env=".workflow/logs/s04-pip-venv"
python3 -m venv --clear "$pip_env"
source "$pip_env/bin/activate"
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src python scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
deactivate

docker build --file Dockerfile \
  --tag industrial-opportunity-resolution-mvp:s04-local .
```

- [ ] Launch detached; read the complete log; require all phases and final sentinel 0.
- [ ] Run final protocol hygiene:

```bash
git diff --check
git status --short
git diff --name-only
git diff -- data/manifests/snapshot_manifest.json
git diff -- docs/authority/authority_hashes.json
```

- [ ] Supervisor explicitly stages only reviewed paths; never `git add .`. Use this path-explicit command after every listed record exists:

```bash
git add \
  data/synthetic/SYN-MINISTRY-STEEL-001.json \
  data/synthetic/SYN-MINISTRY-PP-001.json \
  data/manifests/snapshot_manifest.json \
  src/ior_mvp/rules.py \
  src/ior_mvp/decision_engine.py \
  src/ior_mvp/dossier.py \
  src/ior_mvp/static/app.js \
  scripts/validate_scenarios.py \
  tests/test_simulation_fidelity.py \
  tests/test_golden_cases.py \
  tests/test_synthetic_isolation.py \
  tests/test_scenario_validation.py \
  tests/test_api.py \
  tests/test_dossier_contract.py \
  tests/test_static_frontend.py \
  tests/test_threshold_boundaries.py \
  docs/implementation/API_REFERENCE.md \
  docs/ARCHITECTURE_DECISIONS.md \
  docs/BUILD_ROADMAP.md \
  docs/REQUIREMENTS_TRACEABILITY.md \
  docs/KNOWN_LIMITATIONS.md \
  .workflow/slices/S04-simulation-fidelity/persona.md \
  .workflow/slices/S04-simulation-fidelity/context.md \
  .workflow/slices/S04-simulation-fidelity/plan.md \
  .workflow/slices/S04-simulation-fidelity/plan_review.md \
  .workflow/slices/S04-simulation-fidelity/implementation_log.md \
  .workflow/slices/S04-simulation-fidelity/test_evidence.md \
  .workflow/slices/S04-simulation-fidelity/implementation_review.md \
  .workflow/slices/S04-simulation-fidelity/reviewer_findings.md
```

- [ ] Add `docs/authority/authority_hashes.json` only if its audited diff is permitted `generated_on` only. Omit any listed path with no diff only after an explicit path-scoped `git diff` is empty.
- [ ] Run:

```bash
git diff --cached --name-only
git diff --cached --check
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/check_prohibited_files.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev \
  python scripts/verify_integrity.py
```

- [ ] Require staged names to be a subset of the reviewed list, no ignored/log/secret path, clean cached diff, scanner pass, and integrity pass.
- [ ] Supervisor alone commits/pushes/creates PR using §23 plus observed evidence.
- [ ] Require green current-head checks: `uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build`. Cancelled/skipped is not green.
- [ ] If an evidence-only commit changes PR head, require all checks green on that final head.
- [ ] After Supervisor squash merge, record actual SHA/PR/CI, promote traceability, close KL-07/KL-08, mark ADR/completion, and run post-merge integrity and Gate B.

**Confirm:** final reviewed path inventory and final PR head only.

**Validate:** exact proof trio, Gate B, uv, clean pip, Docker, scanners, reviews, and hosted CI are all current.

**Test:** all local commands and four hosted checks pass before Supervisor-only merge.

## 27. Exact command classification

All categories still use §26's detached script and complete log read.

### Short/read-only

- branch, HEAD, status, name-only, staged-path, and diff inspection;
- prohibited and threshold-literal scanners;
- focused pytest nodes/files;
- Python compile and JavaScript syntax;
- repository Gate B CLI;
- `git diff --check`;
- SHA-256/stat/manifest comparisons;
- final staged hygiene and post-merge integrity/Gate B.

### Detached long-running

- focused multi-file regression;
- complete pre-manifest regression;
- complete post-generation regression;
- final `make ci` + required proof + clean pip + Docker;
- hosted GitHub Actions after Supervisor push/PR.

### Single governed write

- the one `scripts/build_manifests.py` invocation after §24 authorization. Its uniquely named script is never launched twice.

### Prohibited command behavior

- no direct command outside the script/log envelope;
- no `git add .`, force push, hard reset, checkout restoration, clean, amend, history rewrite, skipped hook, optional-failure escape, or test weakening;
- no network/live-source/deployment command;
- no second generator run;
- no commit/push/PR/merge from planner, implementer, or reviewer seats.

## 28. Explicit non-goals

- No edit to public snapshots, golden extraction data/expectations, methodology DOCX/mirror, `docs/core/**`, thresholds, sector profiles, evidence policy, project config, dependencies, lockfile, CI workflow, Makefile, app routes/error mapper, capability/economics/evidence/GenUI services, or `styles.css`.
- No numeric scenario input, `seed_basis`, scenario ID, class, source, warning-label, or public golden outcome change.
- No `MONITOR` or greenfield route implementation; no public complete-route sequence.
- No new threshold, route score, composite ranking, sustained-demand proxy, base demand, committed probability, MES, application qualification, market-failure test, or Ministry-data schema.
- No use of R6 firing as an ADVANCE gate beyond the explicit Core 07 §7.3 conjunction.
- No replacement of public R6/R7/R8 rows; simulated rows are appended and separately labelled.
- No broad `app.js` refactor, frontend redesign, CSS tokenization, new interactive control, localization expansion, browser/Playwright test, or accessibility claim beyond the exact static contracts.
- No live connector, upload, database, graph, model, AI chat, CRM, workflow authorization, deployment, calibration, or portfolio expansion.
- No hash regeneration before regression, no manual manifest hash edit, and no authority-hash/Core row change.
- No self-approval, reviewer impersonation, fake passing evidence, predicted CI/PR/merge fact, or public-support authorization.

## 29. Open owner decisions and stop conditions

There is **no open owner decision required to execute this plan**. The authoritative S04 context resolves:

- scenario field names/version;
- exact narrative copy;
- §7.4 precedence and equality behavior;
- §7.3 conjunction/fallback;
- R6 denominator and missing sustained treatment;
- R7 current-fixture execution states;
- R8 abstention;
- API back-test shape;
- two-file governed edit and one-run manifest policy.

The following are not guessed; they are explicit stop conditions for a new owner/authority decision:

1. Any request to add/interpret base demand, commitment probability, MES, sustained-period evidence, or another R6/R7/R8 input.
2. Any defensible alternative to the specified §7.4 → §7.3 → INVESTIGATE ordering.
3. Any desired state/route or numeric golden change.
4. Any scenario JSON correction after the single generator run.
5. Any required config, public snapshot, frozen core, methodology, or authority-hash entry change.
6. Any interpretation that would label synthetic data official, observed, Ministry-provided, or Class A/B/C.
7. Any ADVANCE while a §7.3 control or hard gate is unresolved.

`docs/project/` absence is recorded, not filled with invented project facts; `config/project.yaml`, the repository authority chain, and S04 context supply every fact used by this bounded plan.

## 30. Planner self-audit (al-muhasibi)

- **Scope traced:** all three S04 defects map to scenario contract, generic selection/back-test, synthetic rule rows, dossier/UI, TL-07, docs, and Tasks 1–8.
- **Authority traced:** §7.4 equality is first; §7.3 is a strict conjunction; lower-cost routes remain 0/5; no public or methodology behavior is changed.
- **Existing state traced:** both opportunity-ID comparisons, all simulated narrative literals (including fallback and PP competition finding), and unchanged public-ledger reuse are cited with base line ranges.
- **Arithmetic checked:** steel 57.5092/46.4908/.2667/18/198/1.075092 and PP 104.490243/80/56/-24/0 are preserved. R6 signed shortage denominator is explicit.
- **Unknowns honest:** sustained period, base demand, commitment probability, probability-adjusted addition, and MES remain `NOT_CALCULABLE`; R8 remains disabled.
- **Types consistent:** final names are `validate_simulation_contract`, `_simulate`, `evaluate_simulated_rules`, `evaluate_ground_truth_backtest`, `ground_truth_backtest_error`, `require_ground_truth_backtest`, `integrity.ground_truth_backtest`, and `gap_diagnosis.simulated_rules` throughout drafts/tests/docs.
- **Ground-truth independence:** selection never reads the expected pair; one test deliberately changes only ground truth and proves actual selection remains ADVANCE before mismatch enforcement.
- **TDD consistent:** each behavior-changing edit has an intended RED. TL-07's already-present state/action behavior is explicitly characterized without a fake RED.
- **Governed change bounded:** exactly two scenario hand-edits; no old scenario value changes; one generator run after full non-integrity regression; strict two-manifest audits.
- **Compatibility checked:** existing capacity keys, endpoint behavior, authority/reconciliation objects, evidence rows, public rules, public decisions, and GenUI component types are preserved.
- **Privacy/security checked:** data remains `confidential_demo`; no secret, personal data, real Ministry data, network call, or prohibited path is planned; scanner runs before work and after staging.
- **Review discipline checked:** implementer self-check is not approval; Supervisor and different-model independent review remain required; merge is Supervisor-only.
- **Rollback covered:** pre-merge inverse patch and post-merge revert preserve history and synchronize scenario/manifest/code/docs.
- **Completion honest:** this is a plan only. No implementation, RED/GREEN result, manifest output, test count, reviewer verdict, PR, CI, or merge is claimed.
- **Assumptions:** line citations, hashes, and fixture values are from branch `slice/S04-simulation-fidelity` at base `ddf905d5051fe3b4468bdcd793a8a640f5040048`; any later authority change triggers replanning.
