# S03 Evidence-Isolation and Scenario-Validation Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task under the Supervisor's approval and review checkpoints. Do not dispatch further subagents from this subagent-authored plan unless the Supervisor explicitly directs it. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fail closed on malformed or unreconciled synthetic scenarios, prove public-dossier isolation, expose authority provenance everywhere required by FR-001, and make R5's unavailable retained-import ratio explicit without changing either public snapshot, either synthetic scenario, or any golden outcome.

**Architecture:** Keep policy validation and public-marginal reconciliation in the evidence guard, run both before simulation arithmetic, and expose the deterministic reconciliation report under `integrity.scenario_reconciliation`. Construct one additive `authority` object from the hash manifest and versioned config metadata, then project the same object into the analysis, GenUI integrity banner, dossier JSON, and printable HTML. A read-only repository validator applies the same evidence-guard functions to every synthetic fixture and is a mandatory local/hosted Gate B step.

**Tech stack:** Python 3.11+ (CI: 3.12 and 3.14), FastAPI, PyYAML, pytest, static HTML/CSS/JavaScript, GNU Make, GitHub Actions, and `uv --locked --extra dev`.

## Global constraints

- Data classification is `confidential_demo` from `config/project.yaml:1-7`. This slice reads only frozen public records, Class-D demo scenarios, schemas, and aggregates; no unrestricted client data, secret, credential, token, personal data, live source, or network connector may be introduced.
- Domain authority order is DOCX → frozen core → versioned config → hashed snapshots → code/tests (`docs/authority/00_AUTHORITY_MANIFEST.md:16-27`). The Markdown methodology mirror is a search aid only (`docs/authority/00_AUTHORITY_MANIFEST.md:133-136`).
- Synthetic evidence remains Class D, `source=DEMO_GENERATOR`, explicitly flagged and disclosed, and may never affect `real_decision` (`AGENTS.md:23-34`; Manifest §6 at `docs/authority/00_AUTHORITY_MANIFEST.md:80-92`).
- The steel public result remains `INVESTIGATE`; polypropylene generic-capacity support remains `REJECT` (`AGENTS.md:31-34`; Manifest §6.11 at `docs/authority/00_AUTHORITY_MANIFEST.md:90-92`).
- No file under `data/**` may be hand-edited; the single approved generator may change only `data/manifests/snapshot_manifest.json` as constrained in §24. No `docs/core/**`, methodology DOCX, golden expectation, `config/thresholds.v1.yaml`, or `config/sector_profiles.v1.yaml` may be edited.
- The only hand edit to a hashed file is the exact `config/evidence_policy.v1.yaml` change in §8. `scripts/build_manifests.py` runs exactly once, only under §24 conditions.
- All new public Python functions have type hints; no bare `except`; no new dependency. Any CSS added uses existing `:root` design tokens only.
- Threshold values remain in `config/thresholds.v1.yaml`; the new reconciliation comparisons use scenario/public values or structural unit bounds only. `scripts/check_threshold_literals.py` continues to inspect thresholds only and must remain unchanged.
- Test-first is mandatory: observe the intended RED before each production change, make the minimum GREEN change, then refactor only while green.
- One implementation task at a time. Every task ends **Confirm, Validate, Test**. No Task N+1 begins before Task N is green.
- Commit, push, PR, CI acceptance, and merge remain Supervisor-controlled. The implementer may self-check but may not approve or merge.
- Preserve all Supervisor-owned pre-existing working-tree changes listed in §3; never revert, overwrite, clean, or attribute them to this slice's implementer.

---

## 1. Objective and decision boundary

This slice closes five defects recorded in `.workflow/slices/S03-evidence-isolation-hardening/context.md:6-20`:

1. Policy validation must cover every Core 06 §4 top-level field and exact policy values, and every violation must raise `EvidenceIntegrityError`, never `KeyError`.
2. Every synthetic scenario must produce an explicit public-marginal reconciliation report. Any `FAIL` stops simulation before branch arithmetic; `NOT_APPLICABLE` is visible and non-blocking.
3. Core 09 §4 assertion 6 must prove that a real dossier has no synthetic disclosure and zero synthetic records in JSON and HTML.
4. Every detailed analysis must expose an `authority` object built from the methodology hash manifest and config metadata; the banner and both dossier forms must project it.
5. R5 must retain its degraded coexistence signal while admitting that retained imports/apparent consumption are not calculable and showing the configured threshold.

Reconciliation is a plausibility/integrity gate, not evidence that a scenario is observed, official, Ministry-provided, Class A/B/C, or decision-authorizing. Passing it does not alter the public branch or increase evidence class.

## 2. Requirements and acceptance IDs

| ID | Required behavior | Governing source | Planned proof |
|---|---|---|---|
| FR-001 | Expose methodology identity/hash, snapshot ID, as-of date, and config/project versions per detailed case | Core 01 `docs/core/01_PRODUCT_AND_REQUIREMENTS.md:147-153`; S03 context lines 11-12 | `tests/test_authority_disclosure.py`; static banner contract; dossier JSON/HTML assertions |
| FR-004 | Load evidence classes and isolation requirements from policy | Core 01 `:147-153`; Core 06 `:75-88` | policy matrix and source/class/label tests |
| FR-011–FR-015 | Preserve source/status/class/flag, exact synthetic identity, visible distinction, and contradictions | Core 01 `:156-162` | existing isolation/static tests plus new policy assertions |
| FR-064 | Machine-readable and printable dossiers | Core 01 `:198-205` | public/simulated dossier contract tests |
| NFR-002 | Deterministic formula and source pointer for derived results | Core 01 `:213-223` | each reconciliation check returns `source`, `formula`, `inputs`, `result`, and `detail` |
| NFR-007 | Arabic survives RTL display | Core 01 `:213-223` | existing RTL test remains green; no Arabic content is changed |
| INV-03 | Synthetic is Class D, generator-sourced, flagged, disclosed | Manifest §6.3 `docs/authority/00_AUTHORITY_MANIFEST.md:80-86` | exact policy-value tests and row tests |
| INV-04 | Missing real evidence remains unresolved | Manifest §6.4 `:80-86` | unchanged public goldens and public dossier isolation |
| TL-01 | Hashes, public isolation, mandatory metadata | Core 09 `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:14-22` | integrity, policy, and repository scenario validator |
| TL-09 | Synthetic leakage assertions 1–7 | Core 09 `:150-161` | new assertion-6 JSON/HTML test plus existing 1–5/7 tests |
| GATE-B | Synthetic scenarios reconcile to public marginals | Core 09 `:185-191` | `scripts/validate_scenarios.py`, temp-file RED, CI/Make wiring |
| GATE-F | Zero leakage, dual states, all synthetic rows labelled | Core 09 `:212-216` | isolation, dossier, golden, API tests |

## 3. Start-of-slice preflight, persona, skills, and repository state

The planner adopted the **Evidence Governance and Data-Integrity Engineer** persona from `.workflow/slices/S03-evidence-isolation-hardening/persona.md:1-12`.

Skills used:

- `superpowers:writing-plans`: exact file paths, interfaces, code drafts, bite-sized TDD steps, no placeholders, and a final consistency audit.
- `superpowers:test-driven-development`: every behavior change has an observed RED before production code and a GREEN proof afterward.
- No applicable installed skill found after discovery beyond writing-plans and test-driven-development.

Planner preflight observed:

- branch: `slice/S03-evidence-isolation-hardening`;
- HEAD/base: `c43837054c5581e68cfe7ed87d914a89cd4f63a3`;
- prohibited scan: `PROHIBITED FILE SCAN PASS (123 tracked files)`;
- pre-existing Supervisor-owned status, which must remain intact:

```text
 M .workflow/state.json
 M docs/BUILD_PROGRESS.md
 M docs/KNOWN_LIMITATIONS.md
 M docs/REQUIREMENTS_TRACEABILITY.md
?? .workflow/runs/s02_promote.py
?? .workflow/slices/S02-threshold-governance/completion.md
?? .workflow/slices/S03-evidence-isolation-hardening/
```

The implementer must repeat branch/HEAD/status/scanner checks after `PLAN_APPROVED`, distinguish these paths from new work, and stop if branch or HEAD differs before any production edit.

## 4. Existing-state assessment with file:line evidence

### 4.1 Policy and evidence guard

- Core 06 mandates `scenario_id`, `opportunity_id`, `synthetic_flag`, `display_label`, `seed_basis`, `evidence_class`, `source`, and `synthetic_inputs`, and says a scenario missing any is rejected (`docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md:75-88`).
- Current policy requires only five fields and contains the label but no required class/source keys (`config/evidence_policy.v1.yaml:20-31`).
- Current validation hard-codes `DEMO_GENERATOR`, does not enforce Class D or the policy label, and checks `synthetic_flag` before policy completeness (`src/ior_mvp/evidence.py:20-29`).
- `synthetic_evidence_rows` indexes `scenario["display_label"]` after incomplete validation, allowing a `KeyError` (`src/ior_mvp/evidence.py:50-67`).

### 4.2 Simulation order and missing reconciliation

- Core 07 orders scenario validation before target-demand/capacity/economic calculations (`docs/core/07_DETERMINISTIC_ENGINE_SPEC.md:220-234`) and identifies malformed scenarios as evidence-integrity errors (`:275-286`).
- Current `analyze_simulated` validates metadata but has no reconciliation and immediately dispatches into arithmetic (`src/ior_mvp/decision_engine.py:280-310`).
- The public and synthetic repositories remain separate (`src/ior_mvp/data_repository.py:28-57`), which must not change.
- Core 06 requires reconciliation to public totals (`docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md:91-101`) and Core 05 makes this a constrained demonstration rule (`docs/core/05_DATA_SOURCES_AND_INGESTION.md:182-203`).

### 4.3 Error path

- `EvidenceIntegrityError` is a `RuntimeError` (`src/ior_mvp/evidence.py:8-11`).
- `_safe_analysis` catches only `RepositoryError` and `ValueError`, maps them to 404, and therefore allows an evidence-integrity exception to become a 500 (`src/ior_mvp/app.py:29-34`).
- HTTP 422 is selected for evidence-integrity failures: the request and opportunity ID are syntactically valid, but the loaded scenario cannot be processed under domain policy. 409 would imply a mutable resource-state conflict; this is deterministic content validation.

### 4.4 Authority disclosure

- Public analysis already returns `snapshot_id` and `as_of_date` but no authority/config versions (`src/ior_mvp/decision_engine.py:60-98`).
- The methodology path and full SHA-256 are governed by `docs/authority/authority_hashes.json:4-9`; thresholds, sector profiles, policy, and project versions are present in their own metadata (`config/thresholds.v1.yaml:1-7`, `config/sector_profiles.v1.yaml:1-5`, `config/evidence_policy.v1.yaml:1-5`, `config/project.yaml:1-7`).
- Current GenUI banner props carry snapshot and states only (`src/ior_mvp/genui.py:17-29`), and `renderIntegrityBanner` renders no authority provenance (`src/ior_mvp/static/app.js:154-170`).
- Dossier evidence summary has snapshot/as-of/integrity only (`src/ior_mvp/dossier.py:50-58`); printable HTML shows only snapshot/as-of (`:100-110`).

### 4.5 Dossier leakage assertion

- `build_dossier` computes public/synthetic counts and sets public disclosure to `None` because `analysis.get("simulation_scenario")` is absent (`src/ior_mvp/dossier.py:10-15`, `:50-62`).
- Existing tests prove only simulated HTML disclosure (`tests/test_api.py:50-55`), while Core 09 assertion 6 explicitly requires no disclosure in a real dossier (`docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:150-161`).

### 4.6 R5 transparency

- The R5 configured threshold is `0.20` (`config/thresholds.v1.yaml:56-60`).
- Current R5 uses only a boolean public coexistence proxy and returns no metrics (`src/ior_mvp/rules.py:278-288`).
- Public snapshots have gross-flow boundaries and no retained-import/domestic-production series (`data/snapshots/public/SAU-H0-721049.json:48-57`; `data/snapshots/public/SAU-H0-390210.json:43-53`), so the ratio must remain unknown.

### 4.7 CI and manifest controls

- Hosted Python jobs currently run integrity directly before pytest (`.github/workflows/ci.yml:50-57`, `:80-87`); local `make ci` has the same gap (`Makefile:32-39`).
- The generator rewrites both machine manifests (`scripts/build_manifests.py:27-56`), so its one invocation requires a strict two-manifest diff audit.
- Current machine `generated_on` is already `2026-09-02` in both manifests (`docs/authority/authority_hashes.json:1-3`; `data/manifests/snapshot_manifest.json:1-4`).

## 5. Files and responsibilities

### Create

- `scripts/validate_scenarios.py` — deterministic Gate B validator with injectable directories and exits 0/1/2.
- `tests/test_scenario_validation.py` — reconciliation arithmetic, blocking order, NOT_APPLICABLE/informational behavior, and CLI exits.
- `tests/test_authority_disclosure.py` — source-derived authority contract across analysis, manifest, dossier JSON, and HTML.
- `tests/test_dossier_contract.py` — Core 09 §4.6 public-dossier isolation in both formats.

### Modify

- `config/evidence_policy.v1.yaml` — exact governed policy change in §8.
- `src/ior_mvp/evidence.py` — policy validation, reconciliation report, and fail-closed assertion.
- `src/ior_mvp/data_repository.py` — route every loaded synthetic artifact through the evidence-policy validator before indexing it.
- `src/ior_mvp/config.py` — read/validate authority hash JSON and build source-derived authority object.
- `src/ior_mvp/decision_engine.py` — authority in all detailed analyses; validation/reconciliation before simulation arithmetic; report exposure.
- `src/ior_mvp/app.py` — map `EvidenceIntegrityError` to exact 422 JSON.
- `src/ior_mvp/genui.py` — pass authority object to integrity-banner props.
- `src/ior_mvp/dossier.py` — project authority into `evidence_summary` and printable HTML.
- `src/ior_mvp/rules.py` — add explicit R5 `NOT_CALCULABLE` metrics from config.
- `src/ior_mvp/static/app.js` — render methodology hash prefix and versions.
- `src/ior_mvp/static/index.html` — label the dynamic workspace as an authority-provenance region.
- `src/ior_mvp/static/styles.css` — one token-only authority-caption rule.
- `tests/test_synthetic_isolation.py` — exact policy matrix and typed failures.
- `tests/test_api.py` — 422 fail-closed API contract.
- `tests/test_rules.py` — exact R5 metrics.
- `tests/test_ci_contract.py` — exact named step and order in both Python jobs plus Makefile order.
- `tests/test_static_frontend.py` — authority rendering/semantics/token-use contract.
- `.github/workflows/ci.yml` and `Makefile` — mandatory validator immediately after integrity.
- `docs/ARCHITECTURE_DECISIONS.md` — ADR-008 from §22.
- `docs/REQUIREMENTS_TRACEABILITY.md` and `docs/KNOWN_LIMITATIONS.md` — evidence-lifecycle changes in §23.
- `docs/implementation/API_REFERENCE.md` — add exactly this Error behavior line: `- evidence-integrity failure in simulated mode (policy or public-marginal reconciliation): HTTP 422 with {"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", "message": ...}}; no partial analysis is returned.`
- `docs/authority/00_AUTHORITY_MANIFEST.md` — only the evidence-policy hash/byte row copied from generated JSON.

### Generated once; never hand-edit

- `docs/authority/authority_hashes.json` — only `generated_on` and evidence-policy hash/bytes may differ.
- `data/manifests/snapshot_manifest.json` — only `generated_on` may differ; because it is already the target date, no diff is expected, but the audit rule remains exact.

### Supervisor bookkeeping, preserved and updated only in the proper seat

- `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, slice implementation/review/evidence/PR/completion records, and S02 post-merge records.

## 6. Architecture and integration flow

```text
GET detailed case / UI manifest / dossier
    -> analyze_public(opportunity_id)
       -> validate public evidence
       -> evaluate public rules/capability
       -> attach authority_summary() built from governed files
    -> when mode=simulated:
       -> load separate synthetic scenario
       -> validate_synthetic_scenario() from policy
       -> reconcile_synthetic_scenario(scenario, public analysis)
       -> require_scenario_reconciliation()
          -> FAIL => EvidenceIntegrityError => HTTP 422; no branch arithmetic/output
          -> PASS/NOT_APPLICABLE => continue
       -> existing steel/PP arithmetic (unchanged in this slice)
       -> append labelled synthetic rows
       -> expose report at integrity.scenario_reconciliation
       -> assert real-decision fingerprint unchanged

Repository Gate B:
sorted data/synthetic/*.json
    -> load/index sorted public snapshots
    -> same policy validator
    -> same reconciliation function
    -> deterministic report
    -> 0 all non-failing / 1 scenario-policy-or-reconciliation finding / 2 execution-input error
```

The evidence guard is the sole reconciliation implementation. The engine and CLI consume it; neither duplicates formulas. The repository loader remains separate and immutable. No scenario result is cached or written.

## 7. Exact API/data contracts

### 7.1 Top-level analysis authority object (public and simulated)

```json
{
  "authority": {
    "methodology": {
      "file": "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx",
      "sha256": "5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9",
      "sha256_prefix": "5717cbd42acc"
    },
    "config_versions": {
      "thresholds": "1.1.0",
      "sector_profiles": "1.0.0",
      "evidence_policy": "1.1.0"
    },
    "project_version": "0.1.0"
  }
}
```

Every value above is illustrative of the current governed files; production code reads it and never embeds these version/hash strings.

### 7.2 Simulated integrity report

```json
{
  "integrity": {
    "real_decision_uses_public_only": true,
    "synthetic_isolation": true,
    "scenario_reconciliation": {
      "status": "PASS",
      "scenario_id": "SYN-MINISTRY-STEEL-001",
      "opportunity_id": "SAU-H0-721049",
      "public_snapshot_id": "PUBLIC-SAU-H0-721049-2026-08-31",
      "checks": [
        {
          "rule_id": "target_spec_demand_within_public_imports",
          "source": "Core 06 §5.1 lines 92-101; Core 05 §8 lines 182-195",
          "formula": "target_spec_demand_kt <= latest_public_imports_kt",
          "result": "PASS",
          "blocking": true,
          "inputs": {},
          "detail": "..."
        }
      ]
    }
  }
}
```

Allowed overall statuses are `PASS`, `FAIL`, and `NOT_APPLICABLE`. Check results additionally allow `INFORMATIONAL` only for the non-normative demand-layer observation explained in §9.4. Any check result `FAIL` makes overall status `FAIL` and blocks; `NOT_APPLICABLE` and `INFORMATIONAL` never block. Public analysis sets `integrity.scenario_reconciliation` to `null`.

### 7.3 Error JSON

```json
{
  "detail": {
    "code": "EVIDENCE_INTEGRITY_ERROR",
    "message": "Synthetic scenario reconciliation failed for SYN-MINISTRY-STEEL-001: target_spec_demand_within_public_imports"
  }
}
```

Status is 422 and is reserved for policy/reconciliation `EvidenceIntegrityError`. No analysis, simulation decision, synthetic rows, or partial dossier is returned. An absent scenario keeps `ValueError` and HTTP 404.

### 7.4 R5 metrics

```json
{
  "retained_import_share_of_apparent_consumption": "NOT_CALCULABLE",
  "reason": "Domestic production quantity and retained-import flow are absent from the frozen public snapshot; gross imports cannot establish apparent consumption.",
  "threshold": 0.2
}
```

The R5 `execution`, `fired`, result, and decision effect remain unchanged.

## 8. Governed evidence-policy change — exact draft

Apply only this semantic diff; retain all other lines:

```yaml
metadata:
  version: "1.1.0"
  effective_date: "2026-09-02"
  authority: "Industrial Opportunity Resolution Methodology, Sections 2.1, 10 and 11"

classes:
  A: "Official, current, product-specific and validated against the responsible authority or owner."
  B: "Authoritative but aggregated, lagged, transformed or awaiting minor validation."
  C: "Credible technical/public evidence or company disclosure not yet confirmed by the responsible authority."
  D: "Proxy, inference, model assumption or incomplete mapping."
  E: "Missing, contradictory, unusable or outside the classification boundary."

advance_gate:
  blocked_if_D_or_E:
    - product_identity
    - demand_at_required_specification
    - domestic_supply_or_capability
    - hard_regulatory_or_process_gate

synthetic_isolation:
  invariant: "Synthetic evidence can never change the real decision state."
  required_fields:
    - synthetic_flag
    - scenario_id
    - opportunity_id
    - display_label
    - seed_basis
    - evidence_class
    - source
    - synthetic_inputs
  required_evidence_class: D
  required_source: DEMO_GENERATOR
  allowed_decision_field: simulation_decision
  forbidden_decision_field: real_decision
  display_label: "SIMULATED — NOT MINISTRY EVIDENCE"

source_statuses:
  - observed
  - calculated
  - model_estimated
  - inferred
  - assumption
  - unresolved
  - synthetic
```

This is a Manifest §7.3 operating-configuration change. The owner's 2026-09-02 completion-build mandate supplies the methodology-owner approval already recorded in `.workflow/state.json:20-28`; ADR-008 and the PR must record the rationale, scope, exact sensitivity evidence, and unchanged goldens before the generator runs.

## 9. Deterministic reconciliation rules and current-fixture arithmetic

Only rules directly grounded in Core 06 §5.1 (`docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md:91-101`), Core 06 §10 (`:226-237`), and Core 05 §8 (`docs/core/05_DATA_SOURCES_AND_INGESTION.md:182-203`) are executable.

### 9.1 Blocking rule A — target-spec demand within latest public imports

- Source: Core 06 §5.1 line 97; Core 05 §8 rule 1 lines 186-189.
- Formula: `synthetic_inputs.demand.target_spec_demand_kt <= latest(max(year)).imports_kt`.
- Scenario fields: `synthetic_inputs.demand.target_spec_demand_kt`.
- Public fields: `trade[].year`, latest row `imports_kt`.
- Equality passes.
- Steel: `104.0 <= 287.9` → `PASS`; headroom `183.9 kt`.
- PP: `56.0 <= 56.0` → `PASS`; equality headroom `0.0 kt`.
- A present demand block with missing/non-finite/negative target quantity is `FAIL`; an absent comparable public quantity is `NOT_APPLICABLE` with the unknown visible.

### 9.2 Blocking rule B — line nameplate within disclosed producer total

- Source: Core 06 §5.1 line 98; Core 05 §8 rule 2 lines 186-190.
- Formula when no governed explicit expansion assumption is available: `plant_line.nameplate_kt <= sum(non-null producer_evidence[].installed_capacity_tpy) / 1000`.
- Scenario field: `synthetic_inputs.plant_line.nameplate_kt`.
- Public fields: `domestic_capability.producer_evidence[].installed_capacity_tpy`; null values are excluded, not converted to zero.
- Steel: `250.0 <= 250000 / 1000 = 250.0` → `PASS`; Hadeed null excluded.
- PP: `1170.0 <= (450000 + 720000) / 1000 = 1170.0` → `PASS`; SABIC null excluded.
- Equality passes. A present line block with missing/non-finite/negative nameplate or a disclosed non-null nonnumeric public capacity is `FAIL`; no disclosed numeric total is `NOT_APPLICABLE`.
- `synthetic_inputs.upgrade.incremental_capacity_kt` is not treated as an exemption: it is a proposed future increment, not an explicit design-basis field authorizing the current line nameplate to exceed the public marginal.
- Core 06 names an “explicit expansion assumption” but defines no JSON key or minimum disclosure schema. The safe S03 implementation therefore has no bypass key; see resolved ruling OQ-1 in §29. A future bypass requires a governed schema decision rather than an invented or empty-field escape.

### 9.3 Blocking rule C1/C2 — ranges and physical availability

**C1 capacity factors**

- Source: Core 06 §10 item 3 lines 226-233 (units/ranges valid), the capacity design at `docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md:148-156`, and Core 05 example `:197-203`.
- Formula: each required physical factor in `plant_line` satisfies `0 <= factor <= 1`.
- Required checked fields when `plant_line` exists: `availability`, `yield`, `qualification_share`, `market_allocation_share`; also validate `current_utilisation` when present.
- Steel: `0.92`, `0.94`, `0.38`, `0.70`, `0.89` are each in `[0,1]` → `PASS`.
- PP: `0.93`, `0.97`, `0.18`, `0.55`, `0.78` are each in `[0,1]` → `PASS`.
- Missing/non-finite factors in a present line block or out-of-range factors are `FAIL`.

**C2 PP qualified availability**

- Source: Core 06 §5.1 public-total consistency (`:91-101`) and valid ranges/units in §10 item 3 (`:226-233`).
- Formula when `equivalence.qualified_available_kt` exists: `qualified_available_kt <= nameplate_kt * availability * yield`.
- Scenario fields: `synthetic_inputs.equivalence.qualified_available_kt`; `synthetic_inputs.plant_line.nameplate_kt`, `availability`, `yield`.
- Steel: no `equivalence.qualified_available_kt` → `NOT_APPLICABLE`.
- PP: physical ceiling `1170.0 * 0.93 * 0.97 = 1055.457 kt`; `80.0 <= 1055.457` → `PASS`; headroom `975.457 kt`.
- Equality at exactly `1055.457` passes; `1055.458` fails in the boundary test.

### 9.4 Informational demand-layer observation — not a blocking reconciliation rule

- Source: Core 04 §2.6 says base/committed/announced/downside/upside layers remain separate (`docs/core/04_CANONICAL_DATA_MODEL.md:102-112`).
- The cited authority does **not** state the inequalities `downside <= target` or `committed <= target` as a pass/fail reconciliation constraint. Enforcing them would invent policy.
- Report a check with result `INFORMATIONAL`, `blocking=false`, formula text `observe downside_demand_kt <= target_spec_demand_kt and committed_demand_kt <= target_spec_demand_kt; no decision effect`, and the raw values/comparison booleans.
- Steel observations: `100.0 <= 104.0` and `74.0 <= 104.0`.
- PP observations: `51.0 <= 56.0` and `0.0 <= 56.0`.
- Even if a future value reverses an inequality, the result remains `INFORMATIONAL`; it cannot create a hidden blocking rule without an owner/core change.

### 9.5 Tariff-line/buyer allocation — explicit NOT_APPLICABLE

- Source: Core 06 §5.1 lines 96 and 100-101; Core 05 §8 rule 4 lines 190-192.
- Formula when a governed schema exists: `sum(allocation quantities) <= latest public HS6 import quantity` for buyer quantities, and `sum(tariff-line transaction quantities) == parent HS6 public total` where concepts/coverage are compatible.
- Neither current scenario contains a tariff-line or buyer allocation block, and Core 06 does not define the JSON block/key/unit schema.
- Both fixtures therefore return `NOT_APPLICABLE`, `blocking=true`, empty `inputs`, and detail `No governed tariff-line or buyer allocation block is present; no allocation sum was evaluated.`
- Do not add guessed paths such as `buyer_allocations` or `tariff_line_allocations`. Resolved ruling OQ-2 in §29 defers the schema until a future scenario needs it.

### 9.6 Deliberately excluded rules

- Synthetic export/domestic allocations summing to production (Core 06 §5.1 line 99) are not present in either scenario and have no governed JSON fields or units. Do not invent them in S03.
- Core 05's “line shares within plausible plant totals” has no exact plausibility formula (`docs/core/05_DATA_SOURCES_AND_INGESTION.md:186-193`). The exact factor range and nameplate rules above are used; no additional threshold is created.
- No grade-equivalence, economics, capability, intended-ground-truth, or opportunity-ID branch-selection rule is added. Those belong to S04.

## 10. `evidence.py` complete implementation draft

Replace the current module with the following behavior-preserving plus additive implementation:

```python
from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Iterable, Literal

from .config import evidence_policy_config


class EvidenceIntegrityError(RuntimeError):
    pass


ReconciliationResult = Literal[
    "PASS",
    "FAIL",
    "NOT_APPLICABLE",
    "INFORMATIONAL",
]


def validate_public_evidence(evidence: Iterable[dict[str, Any]]) -> None:
    for item in evidence:
        if item.get("synthetic_flag") is not False:
            raise EvidenceIntegrityError(
                f"Public evidence {item.get('evidence_id', '<unknown>')} "
                "is not explicitly non-synthetic"
            )


def _synthetic_policy() -> dict[str, Any]:
    policy = evidence_policy_config().get("synthetic_isolation")
    if not isinstance(policy, dict):
        raise EvidenceIntegrityError(
            "Evidence policy synthetic_isolation must be a mapping"
        )
    return policy


def _required_policy_value(policy: dict[str, Any], field: str) -> Any:
    if field not in policy:
        raise EvidenceIntegrityError(
            f"Evidence policy synthetic_isolation is missing: {field}"
        )
    return policy[field]


def validate_synthetic_scenario(scenario: dict[str, Any]) -> None:
    policy = _synthetic_policy()
    required_fields = _required_policy_value(policy, "required_fields")
    if not isinstance(required_fields, list) or not all(
        isinstance(field, str) for field in required_fields
    ):
        raise EvidenceIntegrityError(
            "Evidence policy synthetic_isolation.required_fields "
            "must be a list of field names"
        )

    missing = [field for field in required_fields if field not in scenario]
    if missing:
        raise EvidenceIntegrityError(
            "Synthetic scenario is missing required field(s): "
            + ", ".join(missing)
        )

    if scenario.get("synthetic_flag") is not True:
        raise EvidenceIntegrityError(
            "Synthetic scenario must set synthetic_flag=true"
        )

    required_class = _required_policy_value(
        policy,
        "required_evidence_class",
    )
    if scenario.get("evidence_class") != required_class:
        raise EvidenceIntegrityError(
            "Synthetic scenario evidence_class must equal policy "
            f"required_evidence_class={required_class}"
        )

    required_source = _required_policy_value(policy, "required_source")
    if scenario.get("source") != required_source:
        raise EvidenceIntegrityError(
            "Synthetic scenario source must equal policy "
            f"required_source={required_source}"
        )

    required_label = _required_policy_value(policy, "display_label")
    if scenario.get("display_label") != required_label:
        raise EvidenceIntegrityError(
            "Synthetic scenario display_label must equal policy "
            f"display_label={required_label}"
        )

    if not isinstance(scenario.get("synthetic_inputs"), dict):
        raise EvidenceIntegrityError(
            "Synthetic scenario synthetic_inputs must be a mapping"
        )


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if isfinite(number) else None


def _check(
    rule_id: str,
    source: str,
    formula: str,
    result: ReconciliationResult,
    *,
    blocking: bool,
    inputs: dict[str, Any],
    detail: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "source": source,
        "formula": formula,
        "result": result,
        "blocking": blocking,
        "inputs": inputs,
        "detail": detail,
    }


def _latest_trade(public_case: dict[str, Any]) -> dict[str, Any]:
    trade = public_case.get("trade")
    if not isinstance(trade, list) or not trade:
        raise EvidenceIntegrityError(
            "Public case has no trade rows for scenario reconciliation"
        )
    rows = [
        row
        for row in trade
        if isinstance(row, dict)
        and _finite_number(row.get("year")) is not None
    ]
    if not rows:
        raise EvidenceIntegrityError(
            "Public case has no dated trade row for scenario reconciliation"
        )
    return max(rows, key=lambda row: float(row["year"]))


def _demand_check(
    inputs: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    source = "Core 06 §5.1 lines 92-101; Core 05 §8 lines 182-195"
    formula = "target_spec_demand_kt <= latest_public_imports_kt"
    demand = inputs.get("demand")
    if not isinstance(demand, dict):
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail="Synthetic demand block is missing or is not a mapping.",
        )

    target = _finite_number(demand.get("target_spec_demand_kt"))
    if target is None or target < 0:
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={
                "target_spec_demand_kt": demand.get(
                    "target_spec_demand_kt"
                )
            },
            detail=(
                "target_spec_demand_kt must be a finite, non-negative "
                "number."
            ),
        )

    latest = _latest_trade(public_case)
    public_imports = _finite_number(latest.get("imports_kt"))
    check_inputs = {
        "target_spec_demand_kt": target,
        "latest_public_year": latest.get("year"),
        "latest_public_imports_kt": public_imports,
    }
    if public_imports is None:
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs=check_inputs,
            detail=(
                "Latest public import quantity is unavailable; "
                "the compatible public marginal is explicit unknown."
            ),
        )

    passes = target <= public_imports
    return _check(
        "target_spec_demand_within_public_imports",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs=check_inputs,
        detail=(
            f"{target:g} kt <= {public_imports:g} kt."
            if passes
            else f"{target:g} kt exceeds {public_imports:g} kt."
        ),
    )


def _public_nameplate_total(
    public_case: dict[str, Any],
) -> tuple[float | None, list[float | None], bool]:
    capability = public_case.get("domestic_capability")
    producers = (
        capability.get("producer_evidence")
        if isinstance(capability, dict)
        else None
    )
    if not isinstance(producers, list):
        return None, [], False

    disclosed: list[float | None] = []
    invalid = False
    for producer in producers:
        raw = (
            producer.get("installed_capacity_tpy")
            if isinstance(producer, dict)
            else None
        )
        if raw is None:
            disclosed.append(None)
            continue
        capacity = _finite_number(raw)
        if capacity is None or capacity < 0:
            invalid = True
            disclosed.append(None)
            continue
        disclosed.append(capacity)

    numeric = [capacity for capacity in disclosed if capacity is not None]
    if not numeric:
        return None, disclosed, invalid
    return sum(numeric) / 1000.0, disclosed, invalid


def _nameplate_check(
    inputs: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    source = "Core 06 §5.1 lines 92-101; Core 05 §8 lines 182-195"
    formula = (
        "plant_line.nameplate_kt <= "
        "sum(non_null installed_capacity_tpy) / 1000"
    )
    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail="Synthetic plant_line block is missing or is not a mapping.",
        )

    nameplate = _finite_number(line.get("nameplate_kt"))
    if nameplate is None or nameplate < 0:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={"line_nameplate_kt": line.get("nameplate_kt")},
            detail="nameplate_kt must be a finite, non-negative number.",
        )

    public_total, disclosed, invalid = _public_nameplate_total(public_case)
    check_inputs = {
        "line_nameplate_kt": nameplate,
        "disclosed_installed_capacity_tpy": disclosed,
        "disclosed_public_nameplate_kt": public_total,
    }
    if invalid:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs=check_inputs,
            detail=(
                "A non-null public installed_capacity_tpy value is "
                "not a finite, non-negative number."
            ),
        )
    if public_total is None:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs=check_inputs,
            detail="No numeric public installed nameplate is disclosed.",
        )

    passes = nameplate <= public_total
    return _check(
        "line_nameplate_within_disclosed_public_capacity",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs=check_inputs,
        detail=(
            f"{nameplate:g} kt <= {public_total:g} kt."
            if passes
            else f"{nameplate:g} kt exceeds {public_total:g} kt."
        ),
    )


def _capacity_factor_check(inputs: dict[str, Any]) -> dict[str, Any]:
    source = (
        "Core 06 §10 item 3 lines 226-233; "
        "Core 06 §6.2 lines 148-156; Core 05 §8 lines 197-203"
    )
    formula = "for every capacity factor: 0 <= factor <= 1"
    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "capacity_factors_within_unit_interval",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail="Synthetic plant_line block is missing or is not a mapping.",
        )

    required = (
        "availability",
        "yield",
        "qualification_share",
        "market_allocation_share",
    )
    names = required + (
        ("current_utilisation",)
        if "current_utilisation" in line
        else ()
    )
    raw_values = {name: line.get(name) for name in names}
    values = {
        name: _finite_number(raw_values[name])
        for name in names
    }
    invalid = [
        name
        for name, value in values.items()
        if value is None or not 0 <= value <= 1
    ]
    return _check(
        "capacity_factors_within_unit_interval",
        source,
        formula,
        "FAIL" if invalid else "PASS",
        blocking=True,
        inputs=raw_values,
        detail=(
            "Invalid capacity factor(s): " + ", ".join(invalid)
            if invalid
            else "All declared capacity factors are within [0,1]."
        ),
    )


def _qualified_availability_check(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    source = (
        "Core 06 §5.1 lines 92-101; "
        "Core 06 §10 item 3 lines 226-233"
    )
    formula = (
        "qualified_available_kt <= "
        "nameplate_kt * availability * yield"
    )
    equivalence = inputs.get("equivalence")
    if not isinstance(equivalence, dict) or (
        "qualified_available_kt" not in equivalence
    ):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs={},
            detail="No qualified_available_kt is declared.",
        )

    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail="Physical output cannot be calculated without plant_line.",
        )

    qualified = _finite_number(equivalence.get("qualified_available_kt"))
    nameplate = _finite_number(line.get("nameplate_kt"))
    availability = _finite_number(line.get("availability"))
    yield_rate = _finite_number(line.get("yield"))
    values = (qualified, nameplate, availability, yield_rate)
    if any(value is None or value < 0 for value in values):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={
                "qualified_available_kt": equivalence.get(
                    "qualified_available_kt"
                ),
                "nameplate_kt": line.get("nameplate_kt"),
                "availability": line.get("availability"),
                "yield": line.get("yield"),
            },
            detail="Physical-availability inputs must be finite and non-negative.",
        )

    assert qualified is not None
    assert nameplate is not None
    assert availability is not None
    assert yield_rate is not None
    physical_ceiling = nameplate * availability * yield_rate
    passes = qualified <= physical_ceiling
    return _check(
        "qualified_availability_within_physical_output",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs={
            "qualified_available_kt": qualified,
            "nameplate_kt": nameplate,
            "availability": availability,
            "yield": yield_rate,
            "physical_output_ceiling_kt": round(physical_ceiling, 6),
        },
        detail=(
            f"{qualified:g} kt <= {physical_ceiling:g} kt."
            if passes
            else f"{qualified:g} kt exceeds {physical_ceiling:g} kt."
        ),
    )


def _demand_layer_observation(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    source = "Core 04 §2.6 lines 102-112"
    formula = (
        "observe downside_demand_kt <= target_spec_demand_kt and "
        "committed_demand_kt <= target_spec_demand_kt; no decision effect"
    )
    demand = inputs.get("demand")
    if not isinstance(demand, dict):
        return _check(
            "demand_layers_remain_separate",
            source,
            formula,
            "INFORMATIONAL",
            blocking=False,
            inputs={},
            detail="Demand layers are unavailable for observation.",
        )

    target = _finite_number(demand.get("target_spec_demand_kt"))
    downside = _finite_number(demand.get("downside_demand_kt"))
    committed = _finite_number(demand.get("committed_demand_kt"))
    return _check(
        "demand_layers_remain_separate",
        source,
        formula,
        "INFORMATIONAL",
        blocking=False,
        inputs={
            "target_spec_demand_kt": target,
            "downside_demand_kt": downside,
            "committed_demand_kt": committed,
            "downside_within_target": (
                None
                if target is None or downside is None
                else downside <= target
            ),
            "committed_within_target": (
                None
                if target is None or committed is None
                else committed <= target
            ),
        },
        detail=(
            "Demand layers are reported separately; no ordering "
            "constraint is enforced."
        ),
    )


def _allocation_check() -> dict[str, Any]:
    return _check(
        "tariff_line_or_buyer_allocations_reconcile",
        "Core 06 §5.1 lines 92-101; Core 05 §8 lines 182-195",
        (
            "sum(buyer quantities) <= public HS6 imports; "
            "sum(tariff-line transactions) == parent HS6 total "
            "when a governed compatible block exists"
        ),
        "NOT_APPLICABLE",
        blocking=True,
        inputs={},
        detail=(
            "No governed tariff-line or buyer allocation block is "
            "present; no allocation sum was evaluated."
        ),
    )


def reconcile_synthetic_scenario(
    scenario: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    validate_synthetic_scenario(scenario)
    public_opportunity = public_case.get("opportunity")
    public_opportunity_id = (
        public_opportunity.get("id")
        if isinstance(public_opportunity, dict)
        else None
    )
    if scenario.get("opportunity_id") != public_opportunity_id:
        raise EvidenceIntegrityError(
            "Synthetic scenario opportunity_id does not match "
            "the public case opportunity.id"
        )

    inputs = scenario["synthetic_inputs"]
    checks = [
        _demand_check(inputs, public_case),
        _nameplate_check(inputs, public_case),
        _capacity_factor_check(inputs),
        _qualified_availability_check(inputs),
        _demand_layer_observation(inputs),
        _allocation_check(),
    ]
    blocking_results = [
        check["result"]
        for check in checks
        if check["result"] != "INFORMATIONAL"
    ]
    if "FAIL" in blocking_results:
        status = "FAIL"
    elif "PASS" in blocking_results:
        status = "PASS"
    else:
        status = "NOT_APPLICABLE"
    return {
        "status": status,
        "scenario_id": scenario["scenario_id"],
        "opportunity_id": scenario["opportunity_id"],
        "public_snapshot_id": public_case.get("snapshot_id"),
        "checks": checks,
    }


def require_scenario_reconciliation(report: dict[str, Any]) -> None:
    failures = [
        check["rule_id"]
        for check in report.get("checks", [])
        if check.get("result") == "FAIL"
    ]
    if failures:
        raise EvidenceIntegrityError(
            "Synthetic scenario reconciliation failed for "
            f"{report.get('scenario_id', '<unknown>')}: "
            + ", ".join(failures)
        )


def public_decision_fingerprint(decision: dict[str, Any]) -> tuple[Any, ...]:
    return (
        decision.get("state"),
        decision.get("route_code"),
        decision.get("headline"),
        tuple(decision.get("missing_facts", [])),
    )


def assert_real_decision_unchanged(
    before: dict[str, Any],
    after: dict[str, Any],
) -> None:
    if public_decision_fingerprint(before) != public_decision_fingerprint(
        after
    ):
        raise EvidenceIntegrityError(
            "Synthetic analysis attempted to change the real decision state"
        )


def synthetic_evidence_rows(
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    validate_synthetic_scenario(scenario)
    inputs = scenario["synthetic_inputs"]
    rows: list[dict[str, Any]] = []
    for key in sorted(inputs):
        rows.append(
            {
                "evidence_id": f"{scenario['scenario_id']}::{key}",
                "title": key.replace("_", " ").title(),
                "source": scenario["source"],
                "status": "synthetic",
                "evidence_class": scenario["evidence_class"],
                "synthetic_flag": True,
                "scenario_id": scenario["scenario_id"],
                "supports": [f"Simulation branch input: {key}"],
                "display_label": scenario["display_label"],
            }
        )
    return rows


def isolated_copy(value: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy so the simulation branch cannot mutate public records."""
    return deepcopy(value)
```

The `assert` statements only narrow values already checked in the immediately preceding fail-closed branch; they do not enforce policy. If the implementer prefers cast-based narrowing, behavior and tests must remain identical.

### 10.1 `src/ior_mvp/data_repository.py` typed-policy delegation

Add:

```python
from .evidence import validate_synthetic_scenario
```

Replace the body of the synthetic-file loop with:

```python
for path in sorted(directory.glob("*.json")):
    record = _read_json(path)
    validate_synthetic_scenario(record)
    opportunity_id = record["opportunity_id"]
    scenarios[opportunity_id] = record
```

Remove the duplicate repository-specific `opportunity_id` and `synthetic_flag` checks. Policy violations must remain `EvidenceIntegrityError`; wrapping them as `RepositoryError` would break the 422 contract. `_read_json` continues to own missing/invalid JSON errors.

## 11. Authority loading and propagation — complete drafts

### 11.1 `src/ior_mvp/config.py`

Add JSON loading and construct a fresh additive authority object on each call. Replace the module with:

```python
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
AUTHORITY_HASHES_PATH = (
    DOCS_DIR / "authority" / "authority_hashes.json"
)


class AuthorityConfigurationError(RuntimeError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required configuration is missing: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(
            f"Configuration must contain a mapping: {path}"
        )
    return data


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AuthorityConfigurationError(
            f"Required authority manifest is missing: {path}"
        )
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as exc:
        raise AuthorityConfigurationError(
            f"Authority manifest cannot be loaded: {path}"
        ) from exc
    if not isinstance(data, dict):
        raise AuthorityConfigurationError(
            f"Authority manifest must contain a mapping: {path}"
        )
    return data


@lru_cache(maxsize=1)
def project_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "project.yaml")


@lru_cache(maxsize=1)
def thresholds_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "thresholds.v1.yaml")


@lru_cache(maxsize=1)
def sector_profiles_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "sector_profiles.v1.yaml")


@lru_cache(maxsize=1)
def evidence_policy_config() -> dict[str, Any]:
    return _load_yaml(CONFIG_DIR / "evidence_policy.v1.yaml")


@lru_cache(maxsize=1)
def authority_hashes_config() -> dict[str, Any]:
    return _load_json(AUTHORITY_HASHES_PATH)


def _metadata_version(
    config: dict[str, Any],
    artifact: str,
) -> str:
    metadata = config.get("metadata")
    version = (
        metadata.get("version")
        if isinstance(metadata, dict)
        else None
    )
    if not isinstance(version, str) or not version:
        raise AuthorityConfigurationError(
            f"{artifact} configuration metadata.version is missing"
        )
    return version


def authority_summary() -> dict[str, Any]:
    files = authority_hashes_config().get("files")
    if not isinstance(files, list):
        raise AuthorityConfigurationError(
            "Authority manifest files must be a list"
        )
    methodology_entries = [
        item
        for item in files
        if isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and item["path"].lower().endswith(".docx")
    ]
    if len(methodology_entries) != 1:
        raise AuthorityConfigurationError(
            "Authority manifest must contain exactly one methodology DOCX"
        )

    methodology = methodology_entries[0]
    digest = methodology.get("sha256")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(
            character not in "0123456789abcdef"
            for character in digest
        )
    ):
        raise AuthorityConfigurationError(
            "Methodology authority entry has an invalid SHA-256"
        )

    project = project_config().get("project")
    project_version = (
        project.get("version")
        if isinstance(project, dict)
        else None
    )
    if not isinstance(project_version, str) or not project_version:
        raise AuthorityConfigurationError(
            "Project version is missing"
        )

    return {
        "methodology": {
            "file": methodology["path"],
            "sha256": digest,
            "sha256_prefix": digest[:12],
        },
        "config_versions": {
            "thresholds": _metadata_version(
                thresholds_config(),
                "thresholds",
            ),
            "sector_profiles": _metadata_version(
                sector_profiles_config(),
                "sector_profiles",
            ),
            "evidence_policy": _metadata_version(
                evidence_policy_config(),
                "evidence_policy",
            ),
        },
        "project_version": project_version,
    }


def clear_config_caches() -> None:
    project_config.cache_clear()
    thresholds_config.cache_clear()
    sector_profiles_config.cache_clear()
    evidence_policy_config.cache_clear()
    authority_hashes_config.cache_clear()
```

The methodology is selected from the manifest, not named in source code. Exactly one DOCX is valid for the current authority model. The SHA prefix is derived from the full validated hash. The only numeric constant is the required SHA/prefix length, not a domain threshold.

### 11.2 `src/ior_mvp/decision_engine.py`

Change imports:

```python
from .config import authority_summary, project_config, thresholds_config
from .evidence import (
    EvidenceIntegrityError,
    assert_real_decision_unchanged,
    isolated_copy,
    reconcile_synthetic_scenario,
    require_scenario_reconciliation,
    synthetic_evidence_rows,
    validate_public_evidence,
)
```

Add authority and an explicit public-mode null to the `analyze_public` return:

```python
return {
    "opportunity": case["opportunity"],
    "snapshot_id": case["snapshot_id"],
    "as_of_date": case["as_of_date"],
    "authority": authority_summary(),
    "mode": "public",
    # existing fields unchanged
    "integrity": {
        "real_decision_uses_public_only": True,
        "synthetic_isolation": True,
        "scenario_reconciliation": None,
        "latest_imports_usd_m": latest.get("imports_usd_m"),
        "latest_imports_kt": latest.get("imports_kt"),
    },
}
```

Replace only `analyze_simulated` with:

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

    if opportunity_id == "SAU-H0-721049":
        branch = _simulate_steel(public, scenario)
    elif opportunity_id == "SAU-H0-390210":
        branch = _simulate_pp(public, scenario)
    else:
        raise ValueError(
            f"No simulation implementation exists for {opportunity_id}"
        )

    public["mode"] = "simulated"
    public["simulation_decision"] = branch["simulation_decision"]
    public["active_decision"] = branch["simulation_decision"]
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
    return public
```

The existing `_simulate_steel`, `_simulate_pp`, ID dispatch, conditions, kill conditions, formulas, and outcomes are untouched; S04 owns their data-driven replacement.

### 11.3 `src/ior_mvp/genui.py`

Add exactly one prop to the existing integrity-banner component:

```python
"props": {
    "mode": analysis["mode"],
    "public_snapshot": analysis["snapshot_id"],
    "real_state": real["state"],
    "active_state": active["state"],
    "synthetic_label": (
        analysis.get("simulation_scenario") or {}
    ).get("display_label"),
    "authority": analysis["authority"],
},
```

Do not duplicate or flatten version strings in GenUI.

## 12. Fail-closed API mapping — complete draft

In `src/ior_mvp/app.py`, import `Any`, import the typed error, add one shared exception constructor, annotate the helper, and replace the helper body:

```python
from typing import Any, Literal

from .evidence import EvidenceIntegrityError


def _evidence_integrity_http_exception(
    exc: EvidenceIntegrityError,
) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": str(exc),
        },
    )


def _safe_analysis(
    opportunity_id: str,
    mode: Literal["public", "simulated"],
) -> dict[str, Any]:
    try:
        return analyze(opportunity_id, mode)
    except EvidenceIntegrityError as exc:
        raise _evidence_integrity_http_exception(exc) from exc
    except (RepositoryError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
```

Wrap the list endpoint with the same typed mapping:

```python
@app.get("/api/opportunities")
def opportunities(
    mode: Literal["public", "simulated"] = Query(default="public"),
) -> list[dict]:
    try:
        return list_opportunities(mode)
    except EvidenceIntegrityError as exc:
        raise _evidence_integrity_http_exception(exc) from exc
```

This preserves existing unknown-opportunity 404 behavior on detailed routes. Detailed case, UI-manifest, dossier JSON, and dossier HTML use `_safe_analysis`; simulated list mode uses the same constructor. No API path converts typed evidence-integrity failure to 500 or partial 200.

`AuthorityConfigurationError` is deliberately not imported or mapped in `app.py`. It is a server-side governance/configuration defect and therefore surfaces loudly as a server error; it must never be caught by the existing `ValueError` → 404 branch.

## 13. Dossier and UI projection — complete drafts

### 13.1 `src/ior_mvp/dossier.py`

Keep all current decision content. Add the same authority object under `evidence_summary`:

```python
"evidence_summary": {
    "public_records": public_count,
    "synthetic_records": synthetic_count,
    "snapshot_id": analysis["snapshot_id"],
    "as_of_date": analysis["as_of_date"],
    "authority": analysis["authority"],
    "integrity": analysis["integrity"],
},
```

In `render_dossier_html`, calculate escaped authority values before the return:

```python
authority = dossier["evidence_summary"]["authority"]
methodology = authority["methodology"]
versions = authority["config_versions"]
authority_html = f"""
<p><strong>Methodology</strong><br>{e(methodology['file'])}</p>
<p class="small">SHA-256 {e(methodology['sha256'])}</p>
<p class="small">Project {e(authority['project_version'])}
 · Thresholds {e(versions['thresholds'])}
 · Sector profiles {e(versions['sector_profiles'])}
 · Evidence policy {e(versions['evidence_policy'])}</p>
"""
```

Insert this section inside the existing grid, immediately after Evidence boundary:

```html
<section class="box"><h2>Authority and versions</h2>{authority_html}</section>
```

The complete affected tail of the HTML grid becomes:

```python
<section class="box"><h2>Next evidence actions</h2><ul>{evidence_actions or '<li>None</li>'}</ul></section>
<section class="box"><h2>Evidence boundary</h2><p>{e(dossier['evidence_summary']['public_records'])} public records; {e(dossier['evidence_summary']['synthetic_records'])} synthetic records.</p><p class="small">Snapshot {e(dossier['evidence_summary']['snapshot_id'])} · As of {e(dossier['evidence_summary']['as_of_date'])}</p></section>
<section class="box"><h2>Authority and versions</h2>{authority_html}</section>
```

No disclosure fallback is added: public `synthetic_disclosure` remains JSON `null`, no warning HTML is rendered, and the Evidence boundary says `0 synthetic records`.

### 13.2 `src/ior_mvp/static/app.js`

Replace `renderIntegrityBanner` exactly with:

```javascript
function renderIntegrityBanner(props) {
  const simulated = props.mode === "simulated";
  const methodology = props.authority.methodology;
  const versions = props.authority.config_versions;
  const methodologyFile = methodology.file.split("/").at(-1);
  return `
    <article class="workspace-card integrity-banner">
      <div class="card-body">
        <div>
          <strong>Evidence boundary enforced</strong>
          <p>Real state is calculated from frozen public evidence. ${simulated ? "The active surface below is a sealed simulation." : "No synthetic record is active."}</p>
          <p class="integrity-authority">Methodology ${escapeHtml(methodologyFile)} · SHA-256 ${escapeHtml(methodology.sha256_prefix)} · Project ${escapeHtml(props.authority.project_version)} · Thresholds ${escapeHtml(versions.thresholds)} · Sector profiles ${escapeHtml(versions.sector_profiles)} · Evidence policy ${escapeHtml(versions.evidence_policy)}</p>
        </div>
        <div class="integrity-states">
          ${stateChip(props.real_state)}
          ${simulated ? `<span class="integrity-arrow">→</span>${stateChip(props.active_state)}<span class="synthetic-warning">${escapeHtml(props.synthetic_label)}</span>` : ""}
        </div>
      </div>
    </article>
  `;
}
```

Every backend value is escaped. The UI shows the 12-hex prefix, not a client-computed slice, so backend, dossier, and UI contracts are testable against the same source-derived value.

### 13.3 `src/ior_mvp/static/index.html`

Change only the dynamic workspace container opening tag:

```html
<div id="workspace-manifest" class="workspace-grid loading-block" role="region" aria-label="Decision analysis and authority provenance">
```

No interactive element is added; existing mode buttons and case selector remain keyboard reachable.

### 13.4 `src/ior_mvp/static/styles.css`

Add one rule after the existing `.integrity-banner p` declaration:

```css
.integrity-banner .integrity-authority {
  color: var(--teal-soft);
  overflow-wrap: anywhere;
}
```

This uses an existing token and no hardcoded color, spacing, font, radius, or breakpoint. No other CSS line is touched.

## 14. R5 transparency — exact draft

In `evaluate_rules`, replace only the R5 block:

```python
r5 = bool(
    context.get("domestic_production_exists")
    and context.get("material_imports_exist")
)
r5_config = thresholds["R5"]
results.append(
    _rule(
        "R5",
        "Domestic supply plus continued imports",
        "DEGRADED",
        r5,
        (
            "Verified domestic capability coexists with material "
            "gross imports."
            if r5
            else "Coexistence condition not met."
        ),
        (
            "Test specification, qualification, capacity, price, "
            "application and allocation mismatch."
        ),
        {
            "retained_import_share_of_apparent_consumption": (
                NOT_CALCULABLE
            ),
            "reason": (
                "Domestic production quantity and retained-import "
                "flow are absent from the frozen public snapshot; "
                "gross imports cannot establish apparent consumption."
            ),
            "threshold": float(
                r5_config[
                    "retained_import_share_of_apparent_consumption"
                ]
            ),
        },
    )
)
```

Do not compute with nameplate, gross net imports, exports, or the coexistence booleans. They are not apparent consumption.

## 15. `scripts/validate_scenarios.py` — complete draft

```python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from ior_mvp.config import DATA_DIR
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    reconcile_synthetic_scenario,
    validate_synthetic_scenario,
)


SYNTHETIC_DIR = DATA_DIR / "synthetic"
PUBLIC_DIR = DATA_DIR / "snapshots" / "public"


class ScenarioValidationExecutionError(RuntimeError):
    pass


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ScenarioValidationExecutionError(
            f"Expected a JSON object: {path}"
        )
    return value


def _index_public_cases(
    public_dir: Path,
) -> dict[str, dict[str, Any]]:
    paths = sorted(public_dir.glob("*.json"))
    if not paths:
        raise ScenarioValidationExecutionError(
            f"No public JSON files found in {public_dir}"
        )
    cases: dict[str, dict[str, Any]] = {}
    for path in paths:
        case = _read_json_object(path)
        opportunity = case.get("opportunity")
        opportunity_id = (
            opportunity.get("id")
            if isinstance(opportunity, dict)
            else None
        )
        if not isinstance(opportunity_id, str) or not opportunity_id:
            raise ScenarioValidationExecutionError(
                f"Public case lacks opportunity.id: {path}"
            )
        if opportunity_id in cases:
            raise ScenarioValidationExecutionError(
                f"Duplicate public opportunity.id={opportunity_id}"
            )
        cases[opportunity_id] = case
    return cases


def validate_scenario_directories(
    synthetic_dir: Path = SYNTHETIC_DIR,
    public_dir: Path = PUBLIC_DIR,
) -> list[dict[str, Any]]:
    public_cases = _index_public_cases(public_dir)
    scenario_paths = sorted(synthetic_dir.glob("*.json"))
    if not scenario_paths:
        raise ScenarioValidationExecutionError(
            f"No synthetic JSON files found in {synthetic_dir}"
        )

    reports: list[dict[str, Any]] = []
    for path in scenario_paths:
        scenario = _read_json_object(path)
        scenario_id = scenario.get("scenario_id", "<missing>")
        opportunity_id = scenario.get("opportunity_id")
        try:
            validate_synthetic_scenario(scenario)
            if opportunity_id not in public_cases:
                raise EvidenceIntegrityError(
                    "No public case matches scenario "
                    f"opportunity_id={opportunity_id}"
                )
            report = reconcile_synthetic_scenario(
                scenario,
                public_cases[opportunity_id],
            )
            reports.append({"file": path.name, **report})
        except EvidenceIntegrityError as exc:
            reports.append(
                {
                    "file": path.name,
                    "scenario_id": scenario_id,
                    "opportunity_id": opportunity_id,
                    "public_snapshot_id": None,
                    "status": "FAIL",
                    "checks": [],
                    "error": str(exc),
                }
            )
    return reports


def _print_reports(reports: list[dict[str, Any]]) -> None:
    for report in reports:
        print(
            f"- {report['file']} "
            f"scenario={report['scenario_id']} "
            f"opportunity={report['opportunity_id']} "
            f"status={report['status']}"
        )
        if report.get("error"):
            print(f"  ERROR: {report['error']}")
        for check in report.get("checks", []):
            print(
                f"  {check['rule_id']}: {check['result']} "
                f"- {check['detail']}"
            )


def main(
    synthetic_dir: Path = SYNTHETIC_DIR,
    public_dir: Path = PUBLIC_DIR,
) -> int:
    try:
        reports = validate_scenario_directories(
            synthetic_dir,
            public_dir,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ScenarioValidationExecutionError,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(
            "SCENARIO VALIDATION ERROR: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    failures = [
        report for report in reports if report["status"] == "FAIL"
    ]
    if failures:
        print(
            "SCENARIO VALIDATION FAIL "
            f"({len(failures)}/{len(reports)} scenarios failed)"
        )
        _print_reports(reports)
        return 1

    print(
        "SCENARIO VALIDATION PASS "
        f"({len(reports)} scenarios)"
    )
    _print_reports(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Exit semantics are exact:

- `0`: every loaded scenario is policy-valid, has a matching public case, and has no reconciliation `FAIL`; reports can contain visible `NOT_APPLICABLE`/`INFORMATIONAL` checks.
- `1`: a scenario artifact has a policy violation, missing public match, or reconciliation `FAIL`.
- `2`: validator execution input is unusable (directory/file I/O, encoding, JSON/YAML parse, non-object file, missing/duplicate public identity, or no files).

Output is deterministic because both path lists and the fixed check list are ordered. It prints no scenario contents, secrets, or unrestricted data.

## 16. Test drafts — write and observe RED before production edits

### 16.1 Replace `tests/test_synthetic_isolation.py`

```python
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

import ior_mvp.data_repository as data_repository
from ior_mvp.config import evidence_policy_config
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.decision_engine import analyze
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    synthetic_evidence_rows,
    validate_public_evidence,
    validate_synthetic_scenario,
)


MANDATORY_SCENARIO_FIELDS = [
    "synthetic_flag",
    "scenario_id",
    "opportunity_id",
    "display_label",
    "seed_basis",
    "evidence_class",
    "source",
    "synthetic_inputs",
]


def _steel_scenario() -> dict:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    return deepcopy(scenario)


def test_public_snapshots_contain_no_synthetic_rows() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        case = get_public_case(opportunity_id)
        validate_public_evidence(case["evidence"])
        assert all(
            row["synthetic_flag"] is False
            for row in case["evidence"]
        )


def test_simulated_analysis_keeps_real_decision_identical() -> None:
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    assert simulated["real_decision"] == public["real_decision"]
    assert (
        simulated["simulation_decision"]
        != public["real_decision"]
    )


def test_every_synthetic_row_is_labeled() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    synthetic = [
        row
        for row in result["evidence"]
        if row["synthetic_flag"]
    ]
    assert synthetic
    for row in synthetic:
        assert row["source"] == "DEMO_GENERATOR"
        assert row["evidence_class"] == "D"
        assert (
            row["display_label"]
            == "SIMULATED — NOT MINISTRY EVIDENCE"
        )


def test_evidence_policy_declares_the_core_06_metadata_contract() -> None:
    policy = evidence_policy_config()
    isolation = policy["synthetic_isolation"]
    assert policy["metadata"]["version"] == "1.1.0"
    assert policy["metadata"]["effective_date"] == "2026-09-02"
    assert isolation["required_fields"] == MANDATORY_SCENARIO_FIELDS
    assert isolation["required_evidence_class"] == "D"
    assert isolation["required_source"] == "DEMO_GENERATOR"
    assert (
        isolation["display_label"]
        == "SIMULATED — NOT MINISTRY EVIDENCE"
    )


@pytest.mark.parametrize("field", MANDATORY_SCENARIO_FIELDS)
def test_each_missing_mandatory_field_raises_typed_integrity_error(
    field: str,
) -> None:
    scenario = _steel_scenario()
    del scenario[field]

    with pytest.raises(EvidenceIntegrityError) as captured:
        validate_synthetic_scenario(scenario)

    assert field in str(captured.value)


@pytest.mark.parametrize(
    ("field", "invalid", "policy_key"),
    [
        (
            "display_label",
            "Ministry evidence",
            "display_label",
        ),
        ("evidence_class", "C", "required_evidence_class"),
        ("source", "MINISTRY", "required_source"),
    ],
)
def test_policy_controlled_value_mismatch_raises_integrity_error(
    field: str,
    invalid: str,
    policy_key: str,
) -> None:
    scenario = _steel_scenario()
    scenario[field] = invalid

    with pytest.raises(EvidenceIntegrityError) as captured:
        validate_synthetic_scenario(scenario)

    assert policy_key in str(captured.value)


def test_non_mapping_synthetic_inputs_raise_integrity_error() -> None:
    scenario = _steel_scenario()
    scenario["synthetic_inputs"] = []

    with pytest.raises(
        EvidenceIntegrityError,
        match="synthetic_inputs must be a mapping",
    ):
        validate_synthetic_scenario(scenario)


def test_false_synthetic_flag_raises_integrity_error() -> None:
    scenario = _steel_scenario()
    scenario["synthetic_flag"] = False

    with pytest.raises(
        EvidenceIntegrityError,
        match="synthetic_flag=true",
    ):
        validate_synthetic_scenario(scenario)


def test_missing_display_label_never_leaks_a_key_error() -> None:
    scenario = _steel_scenario()
    del scenario["display_label"]

    with pytest.raises(EvidenceIntegrityError) as captured:
        synthetic_evidence_rows(scenario)

    assert "display_label" in str(captured.value)


def test_repository_propagates_policy_failure_as_integrity_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    synthetic_dir = tmp_path / "synthetic"
    synthetic_dir.mkdir()
    scenario = _steel_scenario()
    del scenario["opportunity_id"]
    (synthetic_dir / "scenario.json").write_text(
        json.dumps(scenario),
        encoding="utf-8",
    )
    monkeypatch.setattr(data_repository, "DATA_DIR", tmp_path)
    data_repository.clear_repository_caches()
    try:
        with pytest.raises(
            EvidenceIntegrityError,
            match="opportunity_id",
        ):
            data_repository.synthetic_scenarios()
    finally:
        data_repository.clear_repository_caches()
```

Expected initial RED:

- policy contract fails because version/fields/class/source keys are absent;
- missing `display_label` through `synthetic_evidence_rows` raises `KeyError`;
- repository loading wraps/bypasses part of the policy contract instead of propagating `EvidenceIntegrityError`;
- wrong class/label currently pass.

### 16.2 Create `tests/test_scenario_validation.py`

```python
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

import ior_mvp.decision_engine as decision_engine
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    reconcile_synthetic_scenario,
    require_scenario_reconciliation,
)
from scripts.validate_scenarios import (
    PUBLIC_DIR,
    SYNTHETIC_DIR,
    main,
)


def _scenario(opportunity_id: str) -> dict:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    return deepcopy(scenario)


def _checks(report: dict) -> dict[str, dict]:
    return {
        check["rule_id"]: check
        for check in report["checks"]
    }


@pytest.mark.parametrize(
    (
        "opportunity_id",
        "target",
        "public_imports",
        "nameplate",
        "public_nameplate",
    ),
    [
        (
            "SAU-H0-721049",
            104.0,
            287.9,
            250.0,
            250.0,
        ),
        (
            "SAU-H0-390210",
            56.0,
            56.0,
            1170.0,
            1170.0,
        ),
    ],
)
def test_current_scenarios_reconcile_to_public_marginals(
    opportunity_id: str,
    target: float,
    public_imports: float,
    nameplate: float,
    public_nameplate: float,
) -> None:
    report = reconcile_synthetic_scenario(
        _scenario(opportunity_id),
        get_public_case(opportunity_id),
    )
    checks = _checks(report)

    assert report["status"] == "PASS"
    demand = checks[
        "target_spec_demand_within_public_imports"
    ]
    assert demand["result"] == "PASS"
    assert demand["inputs"]["target_spec_demand_kt"] == target
    assert (
        demand["inputs"]["latest_public_imports_kt"]
        == public_imports
    )
    capacity = checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]
    assert capacity["result"] == "PASS"
    assert capacity["inputs"]["line_nameplate_kt"] == nameplate
    assert (
        capacity["inputs"]["disclosed_public_nameplate_kt"]
        == public_nameplate
    )
    assert (
        checks["capacity_factors_within_unit_interval"]["result"]
        == "PASS"
    )


def test_steel_reconciliation_arithmetic_is_exact() -> None:
    report = reconcile_synthetic_scenario(
        _scenario("SAU-H0-721049"),
        get_public_case("SAU-H0-721049"),
    )
    checks = _checks(report)

    assert checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]["inputs"]["disclosed_installed_capacity_tpy"] == [
        250000.0,
        None,
    ]
    assert checks[
        "qualified_availability_within_physical_output"
    ]["result"] == "NOT_APPLICABLE"
    layers = checks["demand_layers_remain_separate"]
    assert layers["result"] == "INFORMATIONAL"
    assert layers["blocking"] is False
    assert layers["inputs"] == {
        "target_spec_demand_kt": 104.0,
        "downside_demand_kt": 100.0,
        "committed_demand_kt": 74.0,
        "downside_within_target": True,
        "committed_within_target": True,
    }


def test_pp_reconciliation_arithmetic_is_exact() -> None:
    report = reconcile_synthetic_scenario(
        _scenario("SAU-H0-390210"),
        get_public_case("SAU-H0-390210"),
    )
    checks = _checks(report)

    assert checks[
        "line_nameplate_within_disclosed_public_capacity"
    ]["inputs"]["disclosed_installed_capacity_tpy"] == [
        None,
        450000.0,
        720000.0,
    ]
    availability = checks[
        "qualified_availability_within_physical_output"
    ]
    assert availability["result"] == "PASS"
    assert availability["inputs"][
        "physical_output_ceiling_kt"
    ] == pytest.approx(1055.457)
    assert availability["inputs"][
        "qualified_available_kt"
    ] == pytest.approx(80.0)
    layers = checks["demand_layers_remain_separate"]
    assert layers["result"] == "INFORMATIONAL"
    assert layers["inputs"][
        "downside_within_target"
    ] is True
    assert layers["inputs"][
        "committed_within_target"
    ] is True


@pytest.mark.parametrize(
    ("field_path", "invalid_value", "failed_rule"),
    [
        (
            ("demand", "target_spec_demand_kt"),
            288.0,
            "target_spec_demand_within_public_imports",
        ),
        (
            ("plant_line", "nameplate_kt"),
            250.001,
            "line_nameplate_within_disclosed_public_capacity",
        ),
    ],
)
def test_analyze_simulated_blocks_each_public_marginal_failure(
    monkeypatch: pytest.MonkeyPatch,
    field_path: tuple[str, str],
    invalid_value: float,
    failed_rule: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    block, field = field_path
    scenario["synthetic_inputs"][block][field] = invalid_value
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(EvidenceIntegrityError) as captured:
        decision_engine.analyze_simulated("SAU-H0-721049")

    assert failed_rule in str(captured.value)


def test_reconciliation_failure_report_is_rejected() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    assert report["status"] == "FAIL"
    with pytest.raises(
        EvidenceIntegrityError,
        match="target_spec_demand_within_public_imports",
    ):
        require_scenario_reconciliation(report)


def test_pp_physical_availability_equality_passes_and_excess_fails() -> None:
    public_case = get_public_case("SAU-H0-390210")
    scenario = _scenario("SAU-H0-390210")
    ceiling = 1170.0 * 0.93 * 0.97
    scenario["synthetic_inputs"]["equivalence"][
        "qualified_available_kt"
    ] = ceiling

    equality = reconcile_synthetic_scenario(
        scenario,
        public_case,
    )
    assert _checks(equality)[
        "qualified_availability_within_physical_output"
    ]["result"] == "PASS"

    scenario["synthetic_inputs"]["equivalence"][
        "qualified_available_kt"
    ] = ceiling + 0.001
    excess = reconcile_synthetic_scenario(
        scenario,
        public_case,
    )
    assert _checks(excess)[
        "qualified_availability_within_physical_output"
    ]["result"] == "FAIL"
    assert excess["status"] == "FAIL"


@pytest.mark.parametrize("invalid", [-0.001, 1.001])
def test_capacity_factor_outside_unit_interval_fails(
    invalid: float,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["plant_line"][
        "availability"
    ] = invalid

    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    assert _checks(report)[
        "capacity_factors_within_unit_interval"
    ]["result"] == "FAIL"
    assert report["status"] == "FAIL"


def test_demand_layer_ordering_is_informational_not_blocking() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "downside_demand_kt"
    ] = 105.0

    report = reconcile_synthetic_scenario(
        scenario,
        get_public_case("SAU-H0-721049"),
    )
    observation = _checks(report)[
        "demand_layers_remain_separate"
    ]

    assert observation["result"] == "INFORMATIONAL"
    assert observation["blocking"] is False
    assert observation["inputs"][
        "downside_within_target"
    ] is False
    assert report["status"] == "PASS"


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_absent_allocation_block_is_reported_not_applicable(
    opportunity_id: str,
) -> None:
    report = reconcile_synthetic_scenario(
        _scenario(opportunity_id),
        get_public_case(opportunity_id),
    )
    allocation = _checks(report)[
        "tariff_line_or_buyer_allocations_reconcile"
    ]

    assert allocation["result"] == "NOT_APPLICABLE"
    assert allocation["inputs"] == {}
    assert report["status"] == "PASS"


def test_successful_simulation_exposes_reconciliation_report() -> None:
    result = decision_engine.analyze_simulated(
        "SAU-H0-721049"
    )

    assert result["integrity"][
        "scenario_reconciliation"
    ]["status"] == "PASS"


def _write_temp_fixture_pair(
    root: Path,
    scenario: dict,
    public_case: dict,
) -> tuple[Path, Path]:
    synthetic_dir = root / "synthetic"
    public_dir = root / "public"
    synthetic_dir.mkdir()
    public_dir.mkdir()
    (synthetic_dir / "scenario.json").write_text(
        json.dumps(scenario),
        encoding="utf-8",
    )
    (public_dir / "public.json").write_text(
        json.dumps(public_case),
        encoding="utf-8",
    )
    return synthetic_dir, public_dir


def test_repository_scenario_validator_passes_current_fixtures(
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = main(SYNTHETIC_DIR, PUBLIC_DIR)

    assert status == 0
    output = capsys.readouterr().out
    assert "SCENARIO VALIDATION PASS (2 scenarios)" in output
    assert "status=PASS" in output
    assert (
        "tariff_line_or_buyer_allocations_reconcile: "
        "NOT_APPLICABLE"
    ) in output


def test_validator_returns_one_for_temp_reconciliation_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    synthetic_dir, public_dir = _write_temp_fixture_pair(
        tmp_path,
        scenario,
        get_public_case("SAU-H0-721049"),
    )

    status = main(synthetic_dir, public_dir)

    assert status == 1
    output = capsys.readouterr().out
    assert "SCENARIO VALIDATION FAIL (1/1 scenarios failed)" in output
    assert (
        "target_spec_demand_within_public_imports: FAIL"
        in output
    )


def test_validator_returns_two_for_invalid_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    synthetic_dir = tmp_path / "synthetic"
    public_dir = tmp_path / "public"
    synthetic_dir.mkdir()
    public_dir.mkdir()
    (synthetic_dir / "broken.json").write_text(
        "{",
        encoding="utf-8",
    )
    (public_dir / "public.json").write_text(
        json.dumps(get_public_case("SAU-H0-721049")),
        encoding="utf-8",
    )

    status = main(synthetic_dir, public_dir)

    assert status == 2
    assert (
        "SCENARIO VALIDATION ERROR: JSONDecodeError"
        in capsys.readouterr().err
    )
```

Expected initial RED: import fails because `reconcile_synthetic_scenario` and `scripts.validate_scenarios` do not exist. After creating only evidence functions, CLI tests remain RED until the script exists.

### 16.3 Create `tests/test_authority_disclosure.py`

```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

import ior_mvp.config as config_module
from ior_mvp.app import app
from ior_mvp.config import AuthorityConfigurationError, PROJECT_ROOT
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import (
    build_dossier,
    render_dossier_html,
)
from ior_mvp.genui import build_ui_manifest


client = TestClient(app)


def _yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _expected_authority() -> dict:
    manifest = json.loads(
        (
            PROJECT_ROOT
            / "docs"
            / "authority"
            / "authority_hashes.json"
        ).read_text(encoding="utf-8")
    )
    methodology = next(
        item
        for item in manifest["files"]
        if item["path"].endswith(".docx")
    )
    thresholds = _yaml(
        PROJECT_ROOT / "config" / "thresholds.v1.yaml"
    )
    sectors = _yaml(
        PROJECT_ROOT / "config" / "sector_profiles.v1.yaml"
    )
    policy = _yaml(
        PROJECT_ROOT / "config" / "evidence_policy.v1.yaml"
    )
    project = _yaml(PROJECT_ROOT / "config" / "project.yaml")
    return {
        "methodology": {
            "file": methodology["path"],
            "sha256": methodology["sha256"],
            "sha256_prefix": methodology["sha256"][:12],
        },
        "config_versions": {
            "thresholds": thresholds["metadata"]["version"],
            "sector_profiles": sectors["metadata"]["version"],
            "evidence_policy": policy["metadata"]["version"],
        },
        "project_version": project["project"]["version"],
    }


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_every_detailed_analysis_exposes_source_derived_authority(
    opportunity_id: str,
    mode: str,
) -> None:
    result = analyze(opportunity_id, mode)
    response = client.get(
        f"/api/opportunities/{opportunity_id}?mode={mode}"
    )

    assert result["authority"] == _expected_authority()
    assert response.status_code == 200
    assert response.json()["authority"] == _expected_authority()
    assert len(
        result["authority"]["methodology"]["sha256_prefix"]
    ) == 12
    if mode == "public":
        assert result["integrity"][
            "scenario_reconciliation"
        ] is None


@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_integrity_banner_props_receive_the_same_authority(
    mode: str,
) -> None:
    analysis = analyze("SAU-H0-721049", mode)
    manifest = build_ui_manifest(analysis)
    banner = next(
        component
        for component in manifest["components"]
        if component["type"] == "integrity_banner"
    )

    assert banner["props"]["authority"] == analysis["authority"]


def test_authority_summary_fails_loudly_without_methodology_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = tmp_path / "authority_hashes.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "1.0",
                "generated_on": "2026-09-02",
                "files": [
                    {
                        "path": "config/evidence_policy.v1.yaml",
                        "sha256": "0" * 64,
                        "bytes": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        config_module,
        "AUTHORITY_HASHES_PATH",
        manifest,
    )
    config_module.clear_config_caches()
    try:
        with pytest.raises(
            AuthorityConfigurationError,
            match="exactly one methodology DOCX",
        ):
            config_module.authority_summary()
    finally:
        config_module.clear_config_caches()


@pytest.mark.parametrize("mode", ["public", "simulated"])
def test_dossier_json_and_html_project_the_same_authority(
    mode: str,
) -> None:
    analysis = analyze("SAU-H0-721049", mode)
    dossier = build_dossier(analysis)
    authority = _expected_authority()

    assert dossier["evidence_summary"]["authority"] == authority
    rendered = render_dossier_html(dossier)
    assert authority["methodology"]["file"] in rendered
    assert authority["methodology"]["sha256"] in rendered
    assert (
        f"Project {authority['project_version']}"
        in rendered
    )
    for label, key in (
        ("Thresholds", "thresholds"),
        ("Sector profiles", "sector_profiles"),
        ("Evidence policy", "evidence_policy"),
    ):
        assert (
            f"{label} {authority['config_versions'][key]}"
            in rendered
        )
```

These tests derive expected values independently from files, so a hard-coded source version cannot satisfy them after a future governed update.

### 16.4 Create `tests/test_dossier_contract.py`

```python
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app


client = TestClient(app)
DISCLOSURE = "SIMULATED — NOT MINISTRY EVIDENCE"


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_real_dossier_has_no_disclosure_and_zero_synthetic_rows(
    opportunity_id: str,
) -> None:
    json_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier"
        "?mode=public"
    )
    html_response = client.get(
        f"/api/opportunities/{opportunity_id}/dossier.html"
        "?mode=public"
    )

    assert json_response.status_code == 200
    dossier = json_response.json()
    assert dossier["synthetic_disclosure"] is None
    assert dossier["evidence_summary"]["synthetic_records"] == 0

    assert html_response.status_code == 200
    assert DISCLOSURE not in html_response.text
    assert "0 synthetic records" in html_response.text


def test_simulated_dossier_retains_disclosure_and_synthetic_rows() -> None:
    response = client.get(
        "/api/opportunities/SAU-H0-721049/dossier"
        "?mode=simulated"
    )

    assert response.status_code == 200
    dossier = response.json()
    assert (
        dossier["synthetic_disclosure"]["display_label"]
        == DISCLOSURE
    )
    assert dossier["evidence_summary"]["synthetic_records"] > 0
```

This is the missing Core 09 §4.6 proof. It tests exported endpoint payloads, not an internal helper only.

### 16.5 Add to `tests/test_api.py`

Add imports:

```python
from copy import deepcopy

import pytest

import ior_mvp.decision_engine as decision_engine
from ior_mvp.data_repository import get_synthetic_scenario
```

Add:

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
def test_evidence_integrity_failure_returns_422_json(
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    invalid = deepcopy(scenario)
    invalid["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: invalid,
    )

    integrity_client = TestClient(
        app,
        raise_server_exceptions=False,
    )
    response = integrity_client.get(endpoint)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": (
                "Synthetic scenario reconciliation failed for "
                "SYN-MINISTRY-STEEL-001: "
                "target_spec_demand_within_public_imports"
            ),
        }
    }
```

The exact response proves no 500 and no 200/partial body.

Add the missing-artifact compatibility test:

```python
def test_missing_scenario_in_simulated_mode_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: None,
    )

    response = client.get(
        "/api/opportunities/SAU-H0-721049"
        "?mode=simulated"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "No synthetic scenario is available for "
            "SAU-H0-721049"
        )
    }
```

### 16.6 Add to `tests/test_rules.py`

```python
def test_r5_exposes_not_calculable_ratio_reason_and_threshold() -> None:
    threshold = thresholds_config()["rules"]["R5"][
        "retained_import_share_of_apparent_consumption"
    ]
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        r5 = by_id(
            evaluate_rules(get_public_case(opportunity_id)),
            "R5",
        )

        assert r5["metrics"] == {
            "retained_import_share_of_apparent_consumption": (
                "NOT_CALCULABLE"
            ),
            "reason": (
                "Domestic production quantity and retained-import "
                "flow are absent from the frozen public snapshot; "
                "gross imports cannot establish apparent consumption."
            ),
            "threshold": threshold,
        }
```

### 16.7 Modify `tests/test_ci_contract.py`

Add:

```python
MAKEFILE = PROJECT_ROOT / "Makefile"
```

Replace `required_fragments` in `test_each_python_job_runs_every_required_gate` with:

```python
required_fragments = (
    "python scripts/check_prohibited_files.py",
    "python scripts/check_threshold_literals.py",
    "python -m compileall -q src scripts tests",
    "node --check src/ior_mvp/static/app.js",
    "python scripts/verify_integrity.py",
    "python scripts/validate_scenarios.py",
    "pytest -q",
    "python scripts/demo_smoke.py",
)
```

Extend each `required_proof_commands` tuple immediately after its integrity command:

```python
# uv job
"PYTHONPATH=src uv run --locked --extra dev "
"python scripts/validate_scenarios.py",

# pip job
"PYTHONPATH=src python scripts/validate_scenarios.py",
```

Add:

```python
@pytest.mark.parametrize(
    ("job_name", "expected_command"),
    [
        (
            "uv-gates",
            "PYTHONPATH=src uv run --locked --extra dev "
            "python scripts/validate_scenarios.py",
        ),
        (
            "pip-gates",
            "PYTHONPATH=src python scripts/validate_scenarios.py",
        ),
    ],
)
def test_scenario_validation_immediately_follows_integrity(
    job_name: str,
    expected_command: str,
) -> None:
    steps = _workflow()["jobs"][job_name]["steps"]
    integrity_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Verify integrity"
    )

    assert steps[integrity_index + 1] == {
        "name": (
            "Validate synthetic scenarios against public marginals"
        ),
        "run": expected_command,
    }


def test_make_ci_runs_scenario_validation_after_integrity() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")
    fragments = (
        "python scripts/verify_integrity.py",
        "python scripts/validate_scenarios.py",
        "pytest -q",
    )

    assert all(fragment in text for fragment in fragments)
    assert [text.index(fragment) for fragment in fragments] == sorted(
        text.index(fragment) for fragment in fragments
    )
```

Expected RED: the script command and exact named steps are absent.

### 16.8 Add to `tests/test_static_frontend.py`

Add `import re`, then add:

```python
def _relative_luminance(color: str) -> float:
    channels = [
        int(color[index : index + 2], 16) / 255
        for index in (1, 3, 5)
    ]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def _contrast_ratio(first: str, second: str) -> float:
    first_luminance = _relative_luminance(first)
    second_luminance = _relative_luminance(second)
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def test_integrity_banner_renders_authority_provenance_safely() -> None:
    app_js = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "app.js"
    ).read_text(encoding="utf-8")
    for expression in (
        "props.authority.methodology",
        "methodology.sha256_prefix",
        "props.authority.project_version",
        "versions.thresholds",
        "versions.sector_profiles",
        "versions.evidence_policy",
    ):
        assert expression in app_js
    assert "escapeHtml(methodology.sha256_prefix)" in app_js
    assert "escapeHtml(versions.evidence_policy)" in app_js


def test_workspace_region_names_authority_provenance() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "index.html"
    ).read_text(encoding="utf-8")
    assert (
        'role="region" aria-label="Decision analysis and '
        'authority provenance"'
    ) in html


def test_authority_caption_uses_design_token_only() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")
    block = css.split(
        ".integrity-banner .integrity-authority",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]

    assert "var(--teal-soft)" in block
    assert "#" not in block


def test_authority_caption_meets_text_contrast_on_banner() -> None:
    css = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "static"
        / "styles.css"
    ).read_text(encoding="utf-8")
    foreground_match = re.search(
        r"--teal-soft:\s*(#[0-9a-fA-F]{6})",
        css,
    )
    assert foreground_match is not None
    banner = css.split(
        ".integrity-banner {",
        maxsplit=1,
    )[1].split("}", maxsplit=1)[0]
    backgrounds = re.findall(
        r"#[0-9a-fA-F]{6}",
        banner,
    )

    assert len(backgrounds) == 2
    assert all(
        _contrast_ratio(
            foreground_match.group(1),
            background,
        )
        >= 4.5
        for background in backgrounds
    )
```

### 16.9 Existing regressions that remain unchanged

Do not edit these expectations:

- `tests/test_golden_cases.py`: steel public `INVESTIGATE`, steel simulated `ADVANCE` route 5, PP public/simulated `REJECT`.
- existing R-rule/capability/economics boundary tests;
- existing integrity paths/hashes test;
- simulated dossier disclosure test;
- existing public/synthetic row-label and real-decision fingerprint tests.

Run them in the focused and full suites in §26.

## 17. CI and Make wiring — exact edits

### 17.1 `.github/workflows/ci.yml`

In `uv-gates`, insert immediately after the existing `Verify integrity` step:

```yaml
      - name: Validate synthetic scenarios against public marginals
        run: PYTHONPATH=src uv run --locked --extra dev python scripts/validate_scenarios.py
```

In `pip-gates`, insert immediately after its existing `Verify integrity` step:

```yaml
      - name: Validate synthetic scenarios against public marginals
        run: PYTHONPATH=src python scripts/validate_scenarios.py
```

The name must match exactly. Do not add `continue-on-error`, shell escapes, conditions, or a Docker duplicate.

### 17.2 `Makefile`

Insert exactly one line immediately after local integrity:

```make
	PYTHONPATH=src $(UV_RUN) python scripts/validate_scenarios.py
```

The resulting local sequence is:

```text
prohibited scan
threshold-literal scan
compile
JavaScript syntax
integrity
scenario-to-public reconciliation
pytest
demo smoke
```

## 18. Integration, failure, unknown-input, privacy, concurrency, and compatibility

### 18.1 Integration points

- `evidence_policy_config()` is the sole source of mandatory fields, required class, required source, and display label.
- `reconcile_synthetic_scenario()` is the sole formula implementation used by API analysis and CLI.
- `analyze_simulated()` attaches the successful report only after `require_scenario_reconciliation()` has permitted arithmetic.
- `authority_summary()` is the sole authority projection; engine, GenUI, and dossier do not reload or duplicate versions.
- Existing `validate_public_evidence`, separate repositories, deep copy, fingerprint, and synthetic-ledger creation remain active.
- `validate_scenarios.py` reads files only and never calls live sources, mutates caches, rewrites manifests, or edits fixtures.

### 18.2 Failure matrix

| Condition | Domain result | CLI exit | API result |
|---|---|---:|---|
| Missing Core 06 §4 top-level field | `EvidenceIntegrityError` | 1 | 422 JSON |
| Wrong flag, class, source, or label | `EvidenceIntegrityError` | 1 | 422 JSON |
| `synthetic_inputs` not a mapping | `EvidenceIntegrityError` | 1 | 422 JSON |
| Scenario/public opportunity mismatch | `EvidenceIntegrityError` | 1 | 422 JSON |
| Reconciliation check `FAIL` | report `FAIL`, then `EvidenceIntegrityError` | 1 | 422 JSON |
| Check concept/block absent | visible `NOT_APPLICABLE` | 0 if no other failure | simulation may continue |
| Demand-layer observation reversed | visible `INFORMATIONAL` | 0 if no failure | no new decision effect |
| Missing scenario for simulated detail route | `ValueError` | repository gate would fail if committed | 404 JSON |
| Malformed authority manifest or authority metadata | `AuthorityConfigurationError` | not applicable to scenario validator | unmapped server error |
| Unknown opportunity | existing `RepositoryError` | not a scenario-validator case | existing 404 |
| Invalid JSON/encoding/I/O/no files/duplicate public ID | validator execution error | 2 | deployment prevented by CI |
| Hash mismatch | existing integrity failure | prior CI step fails | no release |

No `KeyError`, 500, or 200 partial detailed response is accepted for policy/reconciliation defects.

### 18.3 Unknown and absent inputs

- Null producer capacities are excluded from the sum and remain visible in reconciliation inputs. They do not become zero and do not improve capacity.
- No numeric public installed capacity yields `NOT_APPLICABLE`; no synthetic nameplate is inferred.
- No latest compatible public import quantity yields `NOT_APPLICABLE`; no retained-demand boundary is inferred.
- An invalid declared number is a `FAIL`, not `NOT_APPLICABLE`.
- Allocation checks are explicitly `NOT_APPLICABLE` until a governed schema exists.
- Demand layers remain separate and informational because no cited authority states the proposed ordering as a gate.
- No expansion-assumption bypass is accepted without a governed key/schema.

### 18.4 Privacy and security

- Temp tests use deep copies of the two packaged public/synthetic fixtures and write only to pytest `tmp_path`.
- The validator prints file name, synthetic scenario ID, opportunity ID, statuses, and arithmetic summaries only; it does not dump scenario blocks.
- API errors expose deterministic synthetic scenario/rule identifiers, not file-system paths or raw records.
- No network, external tool, live data, environment secret, upload, or deployment action is needed.
- `scripts/check_prohibited_files.py` runs at preflight, pre-manifest regression, final local gates, and hosted CI.

### 18.5 Concurrency and determinism

- API analysis remains stateless per request; config/repository caches hold read-only mappings as before.
- `authority_summary()` builds a fresh dictionary around cached source records, preventing downstream mutation from changing cached authority metadata.
- Validator paths and checks are sorted/fixed, so output order and exit are stable.
- No lock is needed because the validator performs no writes. `build_manifests.py` is the only write-producing command and runs once in a controlled single process.
- Given identical snapshots/config/code, reconciliation values and responses are byte-stable apart from ordinary JSON key ordering, consistent with Core 07 §11 (`docs/core/07_DETERMINISTIC_ENGINE_SPEC.md:287-295`).

### 18.6 Versioning and backward compatibility

- `evidence_policy.v1.yaml` remains on the v1 major file line and moves metadata 1.0.0 → 1.1.0 for additive stricter controls.
- Analysis adds `authority`; public integrity adds nullable `scenario_reconciliation`; simulated integrity replaces that null with a report. Existing fields and meanings remain unchanged.
- Integrity-banner props and dossier `evidence_summary` gain additive `authority`.
- `dossier_version` and GenUI `manifest_version` remain `"1.0"` because no existing field is removed, renamed, or repurposed.
- Existing unknown-opportunity 404 and successful response statuses remain unchanged.
- Both public and simulated golden decision/state/route expectations remain exact.
- The script's exit contract is new and versioned by repository history; no command-line argument contract is introduced.

## 19. Acceptance criteria

The slice is implementation-complete only when all are true on the current reviewed diff:

1. Policy metadata is exactly 1.1.0 / 2026-09-02 and the required field/class/source/label contract matches §8.
2. Missing/wrong policy fields raise `EvidenceIntegrityError`; the missing-label path is proven not to raise `KeyError`.
3. Both current scenarios report overall `PASS` with the exact arithmetic in §9; no data file changed.
4. Demand and public nameplate violations each block `analyze_simulated`.
5. PP physical availability equality passes and a 0.001-kt excess fails.
6. Demand-layer ordering is visible as `INFORMATIONAL`, not a hidden decision gate.
7. Tariff-line/buyer allocation is visible as `NOT_APPLICABLE` for both fixtures.
8. Successful simulated analysis exposes the complete report under `integrity.scenario_reconciliation`; public analysis exposes null.
9. Detailed/list API returns exact 422 JSON for policy/reconciliation integrity failures and no partial analysis; an absent synthetic scenario remains exact 404.
10. Real dossier endpoints for both opportunities have `synthetic_disclosure=null`, `synthetic_records=0`, no warning label in HTML, and visible zero count.
11. Analysis, banner props/rendering, dossier JSON, and dossier HTML carry the source-derived methodology path/hash/prefix and config/project versions; missing methodology authority raises unmapped `AuthorityConfigurationError`; the new banner caption meets at least 4.5:1 contrast at both gradient stops.
12. R5 returns the exact `NOT_CALCULABLE`, reason, and configured threshold metrics without calculating a ratio.
13. Gate B script returns 0 on repository fixtures, 1 on a temp planted reconciliation failure, and 2 on invalid temp JSON.
14. The exact named scenario-validation step immediately follows integrity in both Python jobs and `make ci`.
15. Threshold-literal scan, JavaScript syntax, compile, integrity, complete pytest, demo smoke, clean pip path, Docker build, and hosted current-head CI all pass.
16. `git diff -- data/` is empty before the one generator invocation; after it, any snapshot-manifest diff is `generated_on` only.
17. The generated evidence-policy hash/bytes, `sha256sum`, and Manifest §11 row agree exactly.
18. Supervisor review and independent different-model review have zero unresolved findings. No planner/implementer self-approval is used.

## 20. Validators and proof obligations

### Focused validators

- policy and evidence: `tests/test_synthetic_isolation.py`;
- reconciliation/CLI: `tests/test_scenario_validation.py`;
- authority: `tests/test_authority_disclosure.py`;
- dossier isolation: `tests/test_dossier_contract.py`;
- API 422 and missing-scenario 404: exact nodes in `tests/test_api.py`;
- R5: exact node in `tests/test_rules.py`;
- CI contract: `tests/test_ci_contract.py`;
- frontend contract: `tests/test_static_frontend.py`;
- threshold-copy guard: `scripts/check_threshold_literals.py`;
- JSON/hash integrity: `scripts/verify_integrity.py`;
- full behavior: complete pytest and `scripts/demo_smoke.py`.

### Required unchanged outcome assertions

```text
SAU-H0-721049 public    -> INVESTIGATE, route_code null
SAU-H0-721049 simulated -> ADVANCE, route_code 5
SAU-H0-390210 public    -> REJECT, route_code 0
SAU-H0-390210 simulated -> REJECT, route_code 0
```

Do not weaken, delete, xfail, skip, parameterize away, or regenerate a fixture to satisfy these.

## 21. Documentation and traceability lifecycle

### 21.1 `docs/REQUIREMENTS_TRACEABILITY.md`

During implementation, update pointers but do not claim hosted execution or review. After actual current-head evidence is recorded, the Supervisor may promote these rows to `TESTED`; `COMPLETE` is only appropriate after merge under the repository's status policy.

| ID | Implementation pointer after S03 | Test/validator pointer after S03 | Pre-evidence status | Evidence-backed status |
|---|---|---|---|---|
| FR-001 | `config.authority_summary`; `decision_engine.analyze_public`; `genui.build_ui_manifest`; `dossier.build_dossier/render_dossier_html`; `app.js renderIntegrityBanner` | `test_authority_disclosure.py`, `test_static_frontend.py` | IMPLEMENTED | TESTED after recorded local/current-head CI |
| FR-004 | policy 1.1.0; `evidence.validate_synthetic_scenario` | `test_synthetic_isolation.py`; scenario CLI | IMPLEMENTED | TESTED |
| INV-03 | policy-driven flag/class/source/label and synthetic rows | exact mismatch/missing tests; ledger tests | IMPLEMENTED | TESTED |
| INV-04 | public branch unchanged; reconciliation cannot populate real unknowns | public goldens, fingerprint, public dossier | IMPLEMENTED | TESTED |
| TL-01 | authority/snapshot integrity plus complete metadata validation | integrity script, policy matrix, scenario CLI | TESTED (retain existing S01 evidence; append S03 scope) | TESTED |
| TL-09 | leakage assertions 1–7, including real dossier assertion 6 | `test_synthetic_isolation.py`, `test_dossier_contract.py` | IMPLEMENTED | TESTED |
| GATE-B | evidence guard reconciliation and repository validator | `test_scenario_validation.py`; `scripts/validate_scenarios.py`; CI step | IMPLEMENTED | TESTED |
| GATE-F | zero leakage, dual states, labelled synthetic rows and public dossier absence | isolation/dossier/golden/API suites | IMPLEMENTED | TESTED |

Do not erase earlier CI evidence or demote an existing status; append S03 pointers/evidence. Record actual test counts, PR URL, run ID, head SHA, and outcomes only after observation.

### 21.2 `docs/KNOWN_LIMITATIONS.md`

Do not mark these closed during implementation. After squash merge and green current-head CI, move them with exact semantic resolutions:

- **KL-04:** policy 1.1.0 now requires all Core 06 §4 fields and exact class/source/label; all violation paths raise `EvidenceIntegrityError`, proven by `tests/test_synthetic_isolation.py`.
- **KL-05:** one evidence-guard reconciliation report is enforced by analysis and `scripts/validate_scenarios.py`, with Gate B wired after integrity; existing fixtures pass and temp planted failures fail.
- **KL-06:** source-derived authority metadata is exposed in detailed analysis, GenUI banner, dossier JSON, and printable HTML, proven by `tests/test_authority_disclosure.py`.
- **KL-26:** the ratio remains unavailable by authority; the defect is closed as a transparency issue because R5 now emits explicit `NOT_CALCULABLE`, reason, and configured threshold rather than implying a computed share.

Closure wording must say it is effective on the actual S03 squash merge and cite observed PR/current-head CI/test evidence. The Supervisor supplies those observed identifiers; the planner does not invent them.

Add these exact rows under **Accepted for this MVP (recorded, not scheduled)**:

```markdown
| KL-27 | No expansion-assumption bypass is implemented; the disclosed-public-nameplate ceiling applies to every packaged scenario. | Core 06 §5.1 names an exception but defines no governed schema; defer the schema until a future scenario needs it. |
| KL-28 | Synthetic scenarios contain no tariff-line or buyer allocation blocks; reconciliation reports `NOT_APPLICABLE` for that check. | Core 06 §5.1 and Core 05 §8 require reconciliation when compatible blocks exist but define no current schema; defer the schema until a future scenario needs it. |
```

KL-27 and KL-28 remain accepted limitations after S03; they are not close-on-merge items.

### 21.3 Other records

- Append implementation commands/results to the S03 implementation log.
- Record RED/GREEN/full-suite/generator/hash evidence in `test_evidence.md`.
- Record Supervisor and independent-review findings/verdicts in their respective slice files.
- Update `BUILD_PROGRESS.md` and `.workflow/state.json` only from observed lifecycle transitions.
- Preserve the pre-existing S02 completion/promotion bookkeeping and include it without misattribution when the Supervisor stages the eventual PR.

## 22. ADR-008 — complete text

Append exactly:

```markdown
## ADR-008 — Evidence-policy validation, public-marginal reconciliation and authority disclosure fail closed

**Status:** Proposed for S03.
**Context:** Core 06 §4 requires eight scenario metadata fields and fixes synthetic evidence as Class D with an explicit warning and generator source, while policy 1.0.0 lists only five required fields and code hard-codes part of the rule. Core 06 §5.1/§10 and Core 05 §8 require synthetic detail to reconcile to compatible public marginals, but no analysis or CI gate performs that reconciliation. FR-001 also requires methodology/snapshot identity per case; the detailed response exposes snapshot/as-of only. R5's configured retained-import-share threshold cannot be evaluated from gross flows without domestic-production and retained-import series.
**Decision:** Update `config/evidence_policy.v1.yaml` on its existing v1 major line from metadata version 1.0.0 to 1.1.0, effective 2026-09-02. Its required fields become `synthetic_flag`, `scenario_id`, `opportunity_id`, `display_label`, `seed_basis`, `evidence_class`, `source`, and `synthetic_inputs`; policy also declares `required_evidence_class: D` and `required_source: DEMO_GENERATOR` while retaining the exact display label. The evidence guard reads all controls from policy and raises `EvidenceIntegrityError` for every violation.

The same evidence guard deterministically reconciles target-spec demand to latest public import quantity, line nameplate to the sum of non-null disclosed producer nameplate, physical factors to [0,1], and declared qualified availability to nameplate × availability × yield. Equality passes. A FAIL blocks simulation before arithmetic; absent compatible blocks are reported as NOT_APPLICABLE. Demand-layer ordering is INFORMATIONAL because Core 04 requires layer separation but states no ordering gate. Tariff-line/buyer allocation is NOT_APPLICABLE until authority defines an executable JSON schema; no field or threshold is invented. Passing reconciliation is a plausibility control only and never upgrades Class D evidence.

`scripts/validate_scenarios.py` applies these same functions to every packaged scenario and matching public case with deterministic exits 0/1/2, and runs immediately after integrity in both Python CI jobs and `make ci`. Detailed API integrity failures return 422 JSON, never a partial 200 or 500.

Every detailed analysis adds one `authority` object sourced from `authority_hashes.json`, config metadata, and `project.yaml`: methodology file/full SHA-256/12-hex prefix, thresholds/sector-profile/evidence-policy versions, and project version. GenUI passes the object to the integrity banner; dossier JSON and printable HTML project the same object. R5 retains its degraded coexistence signal but reports the retained-import share as `NOT_CALCULABLE` with source reason and configured threshold.

The owner completion-build mandate dated 2026-09-02 is the methodology-owner approval for this Manifest §7.3 operating-configuration change. `scripts/build_manifests.py` runs exactly once only after focused and full regression, scenario validation, threshold scan, unchanged golden outcomes, and an exact policy-only governed diff. Generated changes are restricted to the evidence-policy hash/bytes plus `generated_on` in `authority_hashes.json`, and `generated_on` only in `snapshot_manifest.json`; the human Manifest §11 row is copied from generated JSON and verified with `sha256sum`.
**Consequences:** Malformed or unreconciled scenarios cannot reach simulation arithmetic or a successful detailed API response. Both current scenarios pass without editing `data/**`; both public golden outcomes and both simulated outcomes remain unchanged. Responses and exports become additively auditable. Future expansion-assumption or allocation bypasses require a governed schema decision. The stricter policy changes its hash and byte count, so authority JSON and the Manifest §11 evidence-policy row change under the single-generator gate.
```

Change ADR status only through review/merge lifecycle: `Accepted 2026-09-02` is recorded by the Supervisor once the authority change is approved on the reviewed implementation, not by the planner or implementer.

## 23. PR authority-change justification — exact text

Use this body section in the reviewed PR description:

```markdown
## Governed evidence-policy change (Manifest §7.3 / ADR-008)

This PR changes only one governed file by hand: `config/evidence_policy.v1.yaml`, metadata 1.0.0 → 1.1.0 effective 2026-09-02. The change makes the policy match Core 06 §4 by requiring all eight top-level scenario fields and by declaring the existing Class-D and `DEMO_GENERATOR` controls in policy rather than code. The owner completion-build mandate dated 2026-09-02 is the methodology-owner approval recorded by ADR-008.

Sensitivity/proof: both frozen scenarios pass the new policy and public-marginal reconciliation unchanged. Steel remains 104.0 kt demand ≤ 287.9 kt public imports and 250.0 kt line nameplate = 250.0 kt disclosed nameplate. PP equality remains valid at 56.0 kt demand = 56.0 kt public imports and 1,170.0 kt line nameplate = 450.0 + 720.0 kt disclosed nameplate; 80.0 kt qualified availability remains below the 1,055.457 kt physical ceiling. Temp-only tests prove demand/nameplate excesses and a 0.001-kt physical-ceiling excess fail closed. No `data/**`, golden expectation, methodology, frozen-core, thresholds, or sector-profile file changes.

After the full pre-manifest regression, `scripts/build_manifests.py` was run exactly once. The PR records the generated evidence-policy SHA-256/byte count, matching `sha256sum`, the synchronized Manifest §11 row, and the two-manifest diff audit. Both public golden outcomes remain exactly steel `INVESTIGATE` and polypropylene `REJECT`; simulated outcomes remain steel route-5 `ADVANCE` and polypropylene `REJECT`.
```

The final sentence may remain only if actual recorded output proves it. The Supervisor adds observed hash/bytes, test count, PR-head SHA, and CI run link; no planned value is substituted.

## 24. Manifest regeneration, audit, and one-run gate

Run `scripts/build_manifests.py` **exactly once**, only after all of these are observed and recorded:

1. ADR-008 and the exact YAML diff are reviewed;
2. policy/reconciliation/API/authority/dossier/R5/frontend/CI-contract focused tests pass;
3. `scripts/validate_scenarios.py` exits 0 on the two unchanged repository scenarios;
4. the temp-file validator test has proven exit 1 and invalid JSON has proven exit 2;
5. threshold-literal and prohibited-file scans pass;
6. Python compile and JavaScript syntax checks pass;
7. complete pytest passes against policy 1.1.0;
8. demo smoke passes and all four golden outcomes are unchanged;
9. `git diff -- config/evidence_policy.v1.yaml` contains only §8;
10. `git diff -- data` is empty before generation.

After the single invocation:

1. `docs/authority/authority_hashes.json` may change only:
   - `generated_on` to `2026-09-02` (it may remain unchanged because it already has that value);
   - the `config/evidence_policy.v1.yaml` SHA-256 and byte count produced from the reviewed file.
2. `data/manifests/snapshot_manifest.json` may change only `generated_on` to `2026-09-02`; no diff is expected on the same date. Any path/hash/bytes/policy change is a hard stop.
3. Run `sha256sum config/evidence_policy.v1.yaml`; require exact equality with the generated JSON entry.
4. Copy only that generated JSON entry's SHA-256 and byte count into the `config/evidence_policy.v1.yaml` row of Manifest §11.
5. Run integrity. Investigate failure; never rerun the generator merely to obtain green.
6. The computed hash/bytes are authoritative. No planner-predicted hash or byte count is a gate.

If any YAML byte must change after the one run, stop for renewed owner decision and plan revision. Do not run the generator a second time.

## 25. Rollback and recovery

Before commit, if ADR-008/policy 1.1.0 is rejected, apply a reviewed inverse patch that restores together:

- policy metadata 1.0.0 / 2026-08-31, the five-field list, and removal of required class/source keys;
- policy-dependent code/tests/docs;
- generated authority JSON policy hash/bytes;
- Manifest §11 policy row;
- any generator-produced snapshot-manifest date;
- traceability/limitation claims.

Do not leave policy bytes, machine hash, human hash row, tests, or exposed version out of sync. Do not use `git reset --hard`, `git checkout --`, history rewriting, fixture edits, or another manifest generation.

After merge, rollback is one Supervisor-controlled `git revert` of the S03 squash commit followed by scenario validation, integrity, complete pytest, smoke, clean pip compatibility, Docker, and hosted CI. This preserves history and atomically reverts code/config/hashes/docs.

If a non-governed Python/JavaScript defect is found after generation, fix it test-first without rerunning manifests. If a governed YAML correction is required, stop and obtain a renewed authority decision.

## 26. TDD-ordered implementation tasks

### Task 0: Approval and immutable preflight

**Files:** read-only.

**Interfaces:** consumes a Supervisor `PLAN_APPROVED` verdict for this exact plan; produces verified branch/base/status/classification/scope.

- [ ] Read the Supervisor plan review. Stop unless this exact plan is approved, including the resolved OQ-1/OQ-2/OQ-3 rulings in §29.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git branch --show-current"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git rev-parse HEAD"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git status --short"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_prohibited_files.py"
```

- [ ] Require branch `slice/S03-evidence-isolation-hardening` and base `c43837054c5581e68cfe7ed87d914a89cd4f63a3`.
- [ ] Record data classification `confidential_demo`; confirm no secret/private/client data or prohibited path will be staged.
- [ ] Preserve and inventory every Supervisor-owned path from §3.

**Confirm:** approved plan, exact branch/base, known pre-existing diff.

**Validate:** planned path list equals §5 and excludes `data/**` hand edits, core, DOCX, thresholds, sector profiles, secrets, and logs.

**Test:** prohibited scan exits 0.

### Task 1: Make top-level synthetic policy validation fail closed

**Files:** modify `tests/test_synthetic_isolation.py`, `docs/ARCHITECTURE_DECISIONS.md`, `config/evidence_policy.v1.yaml`, only the policy-validation portion of `src/ior_mvp/evidence.py`, and `src/ior_mvp/data_repository.py`.

**Interfaces:** produces `validate_synthetic_scenario(scenario: dict[str, Any]) -> None` governed by policy 1.1.0; no reconciliation function yet.

- [ ] Transcribe the final policy tests from §16.1 before any production/config edit.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_synthetic_isolation.py -q"
```

- [ ] Observe RED for the exact missing policy fields/version and current wrong-class/wrong-label acceptance. Confirm the missing-display-label ledger path exposes the current `KeyError`.
- [ ] Append ADR-008 from §22 with status `Proposed for S03`.
- [ ] Apply the exact YAML in §8; no other governed line.
- [ ] Implement `_synthetic_policy`, `_required_policy_value`, and the policy-validation portion of §10. Do not implement reconciliation before its tests.
- [ ] Apply §10.1 so the repository delegates every synthetic record to the same typed policy validator before indexing.
- [ ] Rerun the same test file to GREEN.
- [ ] Inspect:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- config/evidence_policy.v1.yaml"
```

**Confirm:** exact eight fields and policy-driven class/source/label.

**Validate:** every listed malformed case raises `EvidenceIntegrityError` through direct and repository loading; no `KeyError`; only planned YAML lines changed.

**Test:** all `test_synthetic_isolation.py` tests pass.

### Task 2: Add reconciliation and block simulation before arithmetic

**Files:** create the non-CLI portion of `tests/test_scenario_validation.py`; modify `src/ior_mvp/evidence.py` and `src/ior_mvp/decision_engine.py`.

**Interfaces:** produces `reconcile_synthetic_scenario(...) -> dict[str, Any]`, `require_scenario_reconciliation(...) -> None`, and successful `integrity.scenario_reconciliation`.

- [ ] Create `tests/test_scenario_validation.py` from §16.2 through `test_successful_simulation_exposes_reconciliation_report`, omitting the script import/temp CLI tests until Task 3.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_scenario_validation.py -q"
```

- [ ] Observe RED because reconciliation functions/report do not exist.
- [ ] Implement the reconciliation portion of §10 exactly.
- [ ] Apply the `decision_engine.py` changes in §11.2, preserving existing branch arithmetic and ID dispatch.
- [ ] Rerun the focused file to GREEN.
- [ ] Run unchanged goldens:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_scenario_validation.py tests/test_golden_cases.py -q"
```

**Confirm:** report order/fields/statuses match §7 and checks match §9.

**Validate:** demand and nameplate failures stop before branch output; equality passes; data files are untouched.

**Test:** reconciliation plus all four goldens pass.

### Task 3: Add the standalone Gate B validator

**Files:** append CLI tests/imports to `tests/test_scenario_validation.py`; create `scripts/validate_scenarios.py`.

**Interfaces:** produces `validate_scenario_directories(...) -> list[dict[str, Any]]` and `main(...) -> int` with 0/1/2 exits.

- [ ] Add the script import, temp helper, and final three CLI tests from §16.2.
- [ ] Run the test file and observe collection RED because `scripts.validate_scenarios` is absent.
- [ ] Transcribe §15 exactly.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_scenario_validation.py -q"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/validate_scenarios.py"
```

- [ ] Require repository CLI exit 0 and deterministic reports for both scenarios, including visible allocation `NOT_APPLICABLE`.

**Confirm:** same evidence functions are reused; no duplicated formulas.

**Validate:** temp files only; no `data/**` edits; exit 1/2 distinction is exact.

**Test:** all scenario tests and repository CLI pass.

### Task 4: Map evidence-integrity failures to HTTP 422

**Files:** modify `tests/test_api.py`, then `src/ior_mvp/app.py` and `docs/implementation/API_REFERENCE.md`.

**Interfaces:** detailed analysis routes return exact §7.3 JSON for `EvidenceIntegrityError`.

- [ ] Add both §16.5 tests: policy/reconciliation 422 and absent-scenario 404. Use a local `TestClient(app, raise_server_exceptions=False)` for the 422 request so the pre-fix state is an assertion RED with status 500 rather than an uncaught test-client exception.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_api.py::test_evidence_integrity_failure_returns_422_json -q"
```

- [ ] Observe RED for both detailed and list policy/reconciliation endpoints: status 500, not 422. Confirm the absent-scenario compatibility test is already GREEN at 404.
- [ ] Apply §12 exactly.
- [ ] Under `docs/implementation/API_REFERENCE.md` `## Error behavior`, retain the existing missing-scenario 404 line and append exactly: `- evidence-integrity failure in simulated mode (policy or public-marginal reconciliation): HTTP 422 with {"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", "message": ...}}; no partial analysis is returned.`
- [ ] Rerun the node and the full API file to GREEN.

**Confirm:** 422 is reserved for typed policy/reconciliation integrity failures; absent scenario remains 404.

**Validate:** 422 body has only `detail.code/message`; unknown opportunity and missing scenario remain 404; API reference states both behaviors.

**Test:** API focused node and full API suite pass.

### Task 5: Add source-derived authority to analysis and GenUI

**Files:** create the analysis/banner and authority-failure portion of `tests/test_authority_disclosure.py`; modify `src/ior_mvp/config.py`, `src/ior_mvp/decision_engine.py`, and `src/ior_mvp/genui.py`.

**Interfaces:** produces `authority_hashes_config()`, `authority_summary()`, top-level analysis `authority`, and banner prop `authority`.

- [ ] Create §16.3 through `test_authority_summary_fails_loudly_without_methodology_entry`, omitting the dossier test until Task 6.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_authority_disclosure.py -q"
```

- [ ] Observe RED because analysis/banner authority and `AuthorityConfigurationError` are absent.
- [ ] Apply §11.1, the `analyze_public` additions in §11.2, and §11.3.
- [ ] Rerun to GREEN for both opportunities and both modes.
- [ ] Confirm cache clearing includes authority manifest cache.

**Confirm:** methodology path/hash come from JSON; all versions come from YAML metadata; authority validation uses `AuthorityConfigurationError`.

**Validate:** no source version/hash literal; 12-character prefix derives from full validated hash; missing DOCX entry fails loudly and is not mapped to 404.

**Test:** analysis and GenUI authority tests pass.

### Task 6: Complete dossier authority and public-isolation proof

**Files:** append the dossier test in `tests/test_authority_disclosure.py`; create `tests/test_dossier_contract.py`; modify `src/ior_mvp/dossier.py`.

**Interfaces:** dossier `evidence_summary.authority`; printable Authority and versions block; unchanged disclosure semantics.

- [ ] Add the final §16.3 test and all of §16.4 before dossier production edits.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_authority_disclosure.py tests/test_dossier_contract.py -q"
```

- [ ] Observe authority projection RED. Record that the new Core 09 §4.6 characterization assertions may already pass against existing code; they close a missing proof, not a known runtime leak.
- [ ] Apply §13.1 exactly, reusing existing HTML classes with no style expansion.
- [ ] Rerun both files and existing dossier API test to GREEN.

**Confirm:** same authority object appears in JSON and HTML.

**Validate:** public disclosure remains null/absent from HTML; simulated disclosure remains visible.

**Test:** authority/dossier files and `test_dossier_html_discloses_simulation` pass.

### Task 7: Render authority provenance in the accessible banner

**Files:** modify `tests/test_static_frontend.py`, then `static/app.js`, `static/index.html`, and `static/styles.css`.

**Interfaces:** escaped methodology prefix/config versions; named dynamic region; token-only caption styling.

- [ ] Add §16.8 tests.
- [ ] Run the static test file and observe RED.
- [ ] Apply §13.2–§13.4 exactly.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_static_frontend.py -q"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- node --check src/ior_mvp/static/app.js
```

**Confirm:** all dynamic values pass through `escapeHtml`.

**Validate:** no new hardcoded CSS value; role/label semantics valid; measured caption contrast is at least 4.5:1 against both existing gradient stops; no interactive control changed.

**Test:** static frontend and JavaScript syntax pass.

### Task 8: Make R5's unavailable ratio explicit

**Files:** modify `tests/test_rules.py`, then `src/ior_mvp/rules.py`.

**Interfaces:** exact §7.4 metrics for both public cases.

- [ ] Add §16.6.
- [ ] Run the focused node and observe RED because R5 metrics are `{}`.
- [ ] Apply §14 exactly.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_rules.py::test_r5_exposes_not_calculable_ratio_reason_and_threshold tests/test_rules.py -q"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_threshold_literals.py"
```

**Confirm:** threshold is read from `thresholds["R5"]`.

**Validate:** no apparent-consumption arithmetic or threshold duplicate was introduced.

**Test:** rules and threshold-literal validator pass.

### Task 9: Wire local and hosted Gate B

**Files:** modify `tests/test_ci_contract.py`, then `.github/workflows/ci.yml` and `Makefile`.

**Interfaces:** exact step name/command/order in §17.

- [ ] Apply §16.7 tests first.
- [ ] Run `tests/test_ci_contract.py`; observe RED because commands/steps are absent.
- [ ] Apply §17.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_ci_contract.py -q"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- make -n ci
```

- [ ] Inspect dry-run order and require integrity → scenario validator → pytest.

**Confirm:** both Python jobs and local Make use the exact command.

**Validate:** no optional-failure escape; Docker job unchanged.

**Test:** CI contract passes; Make dry run has exact order.

### Task 10: Complete the pre-manifest regression

**Files:** implementation/evidence records only; no manifest write.

**Interfaces:** produces the single-run authorization facts required by §24.

- [ ] Create an ignored `.workflow/logs/s03-pre-manifest.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp
UV="$HOME/.local/bin/uv"

PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_prohibited_files.py
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/check_threshold_literals.py
PYTHONPATH=src "$UV" run --locked --extra dev python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/validate_scenarios.py
PYTHONPATH=src "$UV" run --locked --extra dev pytest -q
PYTHONPATH=src "$UV" run --locked --extra dev python scripts/demo_smoke.py
```

- [ ] Run detached using the repository's existing execution convention and read the complete log after completion.
- [ ] If anything fails, fix implementation test-first and rerun this pre-manifest suite. Do not run the generator.
- [ ] Run short audits:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- config/evidence_policy.v1.yaml"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- data"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff --check"
```

- [ ] Require exact policy-only governed diff, empty data diff, complete pytest pass, validator pass, smoke pass, and unchanged goldens. Record actual output.

**Confirm:** every §24 precondition is observed.

**Validate:** integrity was not bypassed or regenerated early.

**Test:** complete pre-manifest suite passes.

### Task 11: Regenerate manifests exactly once and synchronize the human row

**Files:** generated `authority_hashes.json`, conditionally generated `snapshot_manifest.json`; manually modify only Manifest §11 evidence-policy row.

**Interfaces:** produces synchronized policy hash/bytes and green integrity.

- [ ] Reconfirm Task 10 evidence and exact generator invocation count zero.
- [ ] Run exactly once:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/build_manifests.py"
```

- [ ] Immediately inspect:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- docs/authority/authority_hashes.json"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- data/manifests/snapshot_manifest.json"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "sha256sum config/evidence_policy.v1.yaml"
```

- [ ] Enforce §24. Stop on any disallowed entry/path/hash/bytes change.
- [ ] Copy generated policy hash/bytes into only Manifest §11's policy row.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/verify_integrity.py"
```

**Confirm:** one generator run, exact allowed generated diff.

**Validate:** JSON, `sha256sum`, and human row agree.

**Test:** integrity exits 0.

### Task 12: Documentation, traceability, and builder self-audit

**Files:** ADR, traceability, known-limitations lifecycle wording, S03 implementation/test records; Supervisor records only in Supervisor seat.

**Interfaces:** evidence-backed documentation without fake CI/review/merge facts.

- [ ] Apply §21 pointers/status lifecycle. Do not insert an unobserved test count, run, URL, SHA, review verdict, or merge.
- [ ] Record exact generator invocation, hash/bytes, diff audits, and integrity output.
- [ ] Retain KL-04/05/06 in Open and KL-26 in Accepted-for-MVP, with close-on-merge wording; add KL-27/KL-28 under Accepted for this MVP; move none to Closed until merge evidence exists.
- [ ] Update `docs/implementation/API_REFERENCE.md` with only the exact 422 line in §5/Task 4 while preserving missing-scenario 404.
- [ ] Audit all changed Python public functions for type hints and all exceptions for explicit handling.
- [ ] Audit every reconciliation assertion against §9 sources and ensure no extra rule exists.
- [ ] Audit all response field names against §§7, 11, and 13.
- [ ] Audit `git diff -- data` and prohibited paths.

**Confirm:** requirement-to-code-to-test pointers are complete.

**Validate:** assertions distinguish observed output from assumptions; statuses do not outrun evidence.

**Test:** docs/static contracts and `git diff --check` pass.

### Task 13: Supervisor review and independent review

**Files:** current complete diff; read-only review except test-first fixes.

**Interfaces:** zero unresolved Supervisor findings, then zero unresolved independent-review findings on the fixed diff.

- [ ] Implementer hands off without saying APPROVE.
- [ ] Supervisor reviews authority fidelity, policy diff, formulas/statuses, error semantics, API compatibility, UI escaping/accessibility, manifest audit, tests, and scope.
- [ ] Fix each finding test-first and rerun affected/full proof. Do not rerun the independent reviewer on unchanged rejected work.
- [ ] If any finding changes policy YAML after Task 11, stop for owner/plan renewal; do not regenerate.
- [ ] Dispatch the different-model independent reviewer only after Supervisor findings are zero.
- [ ] Record reviewer model/identity, exact diff/head, findings, fixes, and verdict. Planner/implementer never self-approves.

**Confirm:** reviews cover the current fixed diff.

**Validate:** zero unresolved findings; model separation preserved.

**Test:** affected suites and complete local gates pass after every fix.

### Task 14: Final local gates, explicit staging, PR, current-head CI, and merge gate

**Files:** reviewed intended paths only; ignored logs/venv never stage.

**Interfaces:** produces final local evidence and, only under Supervisor authority, PR/current-head CI/merge records.

- [ ] Create ignored `.workflow/logs/s03-final.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp

make ci

PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src python3 scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/demo_smoke.py

pip_env='.workflow/logs/s03-pip-venv'
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

docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s03-local .
```

- [ ] Run detached and inspect the complete log.
- [ ] Run final short hygiene:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff --check"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git status --short"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff --name-only"
```

- [ ] Supervisor stages only reviewed explicit paths; never `git add .`. Include `snapshot_manifest.json` only if its audited allowed generated diff exists.
- [ ] Supervisor authorizes commit/push/PR and uses §23 with only observed facts.
- [ ] Require green current-head checks: `uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, and `Docker image build`; cancelled/skipped is not green.
- [ ] If evidence-only record changes alter the PR head, rerun and require green checks on that final head.
- [ ] After merge, Supervisor records actual squash commit, promotes evidence-backed statuses, moves KL rows with actual citations, and runs post-merge integrity/scenario validation as directed.

**Confirm:** reviewed path inventory and final PR head only.

**Validate:** uv, exact proof trio, clean pip, Docker, scanners, reviews, and hosted CI are all current.

**Test:** all local commands exit 0 and hosted CI is 4/4 before Supervisor-only squash merge.

## 27. Exact command classification

### Short interactive

- branch/HEAD/status/diff/path inspection;
- prohibited and threshold-literal scanner CLIs;
- focused pytest files/node IDs;
- repository scenario validator CLI;
- Python compile and JavaScript syntax;
- `make -n ci`;
- `git diff --check`;
- SHA-256/byte/manifest comparisons;
- the single `scripts/build_manifests.py` invocation;
- post-generation integrity.

### Detached long-running

- complete pre-manifest pytest/smoke/scanner/validator script;
- final `make ci` + exact proof commands + clean pip compatibility + Docker build;
- hosted GitHub Actions after push/PR.

All transient scripts, logs, and virtual environments stay under ignored `.workflow/logs/` and never enter Git.

## 28. Explicit non-goals

- No edits to either public snapshot, either synthetic scenario, any golden data/expectation, methodology DOCX, frozen core, thresholds, or sector profiles.
- No live connector, Ministry upload, unrestricted dataset, data migration, database, network call, or deployment.
- No S04 work: scenario ground truth, decision conditions, generic data-driven branch selection, simulated R6/R7/R8 re-evaluation, or removal of opportunity-ID dispatch.
- No invented tariff-line/buyer/export/domestic allocation schema.
- No ungoverned expansion-assumption bypass.
- No change to capability D*, economics, support search, competition formula, route sequence, or public decisions.
- No attempt to calculate retained import share/apparent consumption from gross flows or nameplate.
- No broad frontend redesign, app.js refactor, CSS tokenization of pre-existing declarations, localization expansion, or new interactive element.
- No global API error-contract redesign beyond the typed evidence-integrity 422 mapping on simulated list/detail-derived routes.
- No dependency or lockfile change.
- No manifest regeneration before §24, and never more than one generator invocation.
- No commit, push, PR approval, CI override, or merge by planner/implementer/reviewer.

## 29. Resolved Supervisor rulings

### OQ-1 — governed expansion-assumption schema

**Resolved by Supervisor ruling (plan_review.md PR-02).**
No expansion-assumption bypass is implemented in this MVP. The disclosed-public-nameplate ceiling applies to every packaged scenario. The schema is deferred until a future scenario needs it, and KL-27 records that accepted limitation.

### OQ-2 — governed allocation-block schema

**Resolved by Supervisor ruling (plan_review.md PR-02).**
Tariff-line and buyer allocation blocks are absent by design in this MVP. The reconciliation check remains explicit `NOT_APPLICABLE`; its schema is deferred until a future scenario needs it, and KL-28 records that accepted limitation.

### OQ-3 — demand-layer ordering authority

**Resolved by Supervisor ruling (plan_review.md PR-02).**
The demand-layer relation is `INFORMATIONAL` and never blocking absent methodology language that establishes an ordering gate.

No owner decision is open for S03 and no blocked-owner state applies. The supplied policy values remain version 1.1.0, date 2026-09-02, the exact eight fields, Class D, `DEMO_GENERATOR`, and the exact display label.

## 30. Planner self-audit (al-muhasibi)

- **Scope traced:** defects 1–5 map to Tasks 1–9 and acceptance items 1–14.
- **Authority traced:** every executable reconciliation rule cites Core 06/Core 05; the demand relation is informational; allocation/expansion schema gaps are resolved as accepted MVP limitations by `plan_review.md` PR-02, not inventions.
- **Types consistent:** final names are `authority_summary`, `reconcile_synthetic_scenario`, `require_scenario_reconciliation`, `validate_scenario_directories`, and `integrity.scenario_reconciliation` throughout code/tests/API/docs.
- **TDD consistent:** each behavior-changing production edit has a preceding RED. The public-dossier no-disclosure test is explicitly a missing-proof characterization that can already pass.
- **Governed change bounded:** one YAML hand edit; one generator run after full regression; exact diff/hash audits; no data edit.
- **Outcomes protected:** unchanged golden tests and smoke run before and after generation and again in final gates.
- **Completion honest:** this document is a plan only. No implementation, test pass beyond the recorded preflight scanner, review verdict, CI result, hash, byte count, PR, or merge is claimed.
- **Assumptions:** current line citations and fixture values are from the frozen repository at base `c438370`; future schema or methodology changes remain outside S03.
