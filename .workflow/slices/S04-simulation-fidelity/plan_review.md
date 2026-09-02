# Supervisor Plan Review — S04 Simulation-Branch Fidelity

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Planner: agent 08cc9197 (gpt-5.6-sol-max). Sections read: Global constraints, §1–§2, §7 (contracts), §8 (governed scenario additions — verbatim narrative verified against current `decision_engine.py` literals), §9 (algorithms and arithmetic), §11.4 (`analyze_simulated` ordering), §24 (single-generator gate), §25 (rollback), §29 (stop conditions), §30; section inventory for §10–§14, §26.

## Verification performed

- Selection order §7.4 (equivalence true AND qualified ≥ target → REJECT 0) before §7.3 conjunction (gap > 0; publishable; D\* ≤ configured band; economics passes; ΔNV > 0; no competition warning → ADVANCE 5) else INVESTIGATE — matches Core 07 §7.3–7.4 and the context.
- Steel arithmetic 57.5092 / 46.4908 / D\* 0.2667 / S\* 18 / ΔNV 198 / ratio 1.075092; R6 0.89 ≥ 0.85 and 0.8084 ≥ 0.10 fires (DEGRADED, `sustained_period` NOT_CALCULABLE); R7 0.89 > 0.70 not fired, equivalence NOT_CALCULABLE; R8 DISABLED with layers disclosed. PP 104.490243 kt formula capacity; 80 ≥ 56 → REJECT 0; R6 not fired; R7 FULL not fired; R8 DISABLED. All consistent with the frozen fixtures.
- Back-test compares only (state, route_code) and runs before any simulated field is attached; mismatch → `EvidenceIntegrityError` → existing 422 mapping; Gate B extension reports FAIL.
- Governed change limited to the two synthetic JSON files (additive keys after `scenario_id`; no `synthetic_inputs`/`seed_basis` byte changes); `snapshot_manifest.json` may change only those two entries (+ date); `authority_hashes.json` must not change entries.
- Narrative moved verbatim; the word "sustained" is not converted into an R6 observation.

## Round 1 findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| PR-01 | LOW | Core 07 §10 / owner mandate §24 (typed fail-closed; unknown never becomes KeyError) | Plan §7.1/§8.3: `validate_simulation_contract` validates ground-truth/narrative structure; §9.1 step 10 loads `decision_narrative[computed_state]`. | If a scenario's computed state has no narrative entry, the lookup could raise `KeyError` instead of a typed error. | State explicitly: `validate_simulation_contract` requires narrative entries for `ground_truth.expected_simulation_state` and `INVESTIGATE`; at runtime a computed state without a narrative raises `EvidenceIntegrityError` (typed), and the back-test then also fails. Add one unit test for a scenario whose narrative lacks the computed state. |
| PR-02 | LOW | ADR-006 completeness; no hidden constants | Plan §7.1: "Runtime supports exactly scenario contract version 1.1.0". | A version literal in code is acceptable as a schema-contract constant but must be named and documented, not scattered. | Declare `SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})` (or equivalent) once in `decision_engine.py` (or `evidence.py`), reference it in ADR-006, and test both accepted and rejected versions. |
| PR-03 | LOW (binding condition) | Core 09 §8 (no loosening of golden expectations) | Plan §14.2 "Replace `tests/test_golden_cases.py`". | Replacing a golden file risks silently dropping an assertion. | The replacement may only ADD assertions; every existing assertion (states, route codes, `d_star is None`, fired rules, 57.509, 46.491, 18.0, 198.0, `< 1.25`, `real_decision_unchanged_after_simulation`, PP gap `< 0`, support `== 0`) must remain verbatim or stricter. Task 5 must include a diff check that no `assert` line was removed. |

No BLOCKER/HIGH/MEDIUM findings. No owner decision required (§29 confirmed).

## Round 2

Planner revised `plan.md` (same agent). Supervisor verified: PR-01 at lines 248, 405, 420, 897–905, 1844 (narrative required for expected state and INVESTIGATE; typed error; unit test); PR-02 at lines 248, 860, 900, 1785, 2883 (`SUPPORTED_SCENARIO_CONTRACT_VERSIONS` constant, ADR text, tests); PR-03 at lines 3161–3198 (additive-only golden test edits; base-diff assert-removal guard recorded in evidence).

Unresolved findings: **0**.

## Decision

**PLAN_APPROVED** — 2026-09-02, Supervisor. Implementation may begin on `slice/S04-simulation-fidelity` from base `ddf905d5051fe3b4468bdcd793a8a640f5040048`, executing plan Tasks 0–11 and the Task 13 detached local validation as pre-review evidence. The single `scripts/build_manifests.py` run is pre-authorised under the plan §24 conditions (two synthetic JSON files the only governed edits, additive keys only; Gate B with back-test PASS; scans, full pytest and smoke green; `authority_hashes.json` entries unchanged). Commit/push/PR/merge remain Supervisor-controlled.
