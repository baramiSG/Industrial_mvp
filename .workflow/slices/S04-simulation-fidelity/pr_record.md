## SLICE
S04 — Simulation-branch fidelity (`slice/S04-simulation-fidelity` → `main`, base `ddf905d`).

## OBJECTIVE
One generic engine path selects the simulated state from scenario content per Core 07 §7.4 (equivalent qualified availability ≥ target → REJECT route 0) then §7.3 (strict conjunction → ADVANCE route 5; else INVESTIGATE), with no opportunity-ID dispatch; each scenario declares its planted ground truth and decision narrative so the engine is back-tested at validation and request time; R6/R7/R8 are re-evaluated in the simulated ledger from labelled synthetic inputs with explicit execution states and NOT_CALCULABLE metrics; UI and dossier disclose the synthetic rule rows; public mode carries zero synthetic rule rows.

## REQUIREMENTS
FR-020, FR-021, FR-052, FR-054, FR-062, TL-04, TL-07, INV-02, ADR-006; Core 02 §3; Core 06 §5.3, §10.5; Core 07 §7.2–7.4, §8; closes KL-07, KL-08 on merge; KL-25 wording (R8 abstention).

## AUTHORITY CHANGE — synthetic scenarios (Manifest §7.3 / ADR-006)
`data/synthetic/SYN-MINISTRY-STEEL-001.json` and `SYN-MINISTRY-PP-001.json` gain additive top-level keys only: `scenario_version: "1.1.0"`, `ground_truth` (expected state/route with authority basis) and state-keyed `decision_narrative` carrying verbatim the texts previously embedded in `decision_engine.py` (Core 07 §8 conditions and kill conditions). No numeric value, `synthetic_inputs` or `seed_basis` line changed. The owner's 2026-09-02 mandate is the recorded approval. `scripts/build_manifests.py` run once after Gate B (with back-tests) PASS, scans PASS, 231 tests and smoke PASS; `snapshot_manifest.json` changed only the two synthetic entries (steel `8867f0833662108746e0639082847d40841c0b3e550628199be93e75d46f9aea` / 4,711; PP `06517bb93d68911b75c83adb5bf4eab085a2843d1aaa245b56555c999eeee5ea` / 3,433; `sha256sum` verified); `authority_hashes.json` unchanged.

## IMPLEMENTATION
- `decision_engine.py`: `validate_simulation_contract` (`SUPPORTED_SCENARIO_CONTRACT_VERSIONS`), `_simulate` (generic §7.4→§7.3→INVESTIGATE), `evaluate_ground_truth_backtest`/`require_ground_truth_backtest` (typed, before any simulated field is attached), `integrity.ground_truth_backtest`; `_simulate_steel`/`_simulate_pp` and ID dispatch removed.
- `rules.evaluate_simulated_rules`: R6 (utilisation ≥ 0.85 and shortage ≥ 0.10 over effective qualified capacity; DEGRADED — sustained period NOT_CALCULABLE), R7 (utilisation ≤ 0.70 and equivalence when required; FULL/DEGRADED), R8 (DISABLED; base demand/probability/MES NOT_CALCULABLE; layers disclosed); rows carry `synthetic_flag`, class D, source, label, `basis`.
- `scripts/validate_scenarios.py`: ground-truth back-test per scenario (FAIL blocks).
- `dossier.py` (`gap_diagnosis.simulated_rules` + HTML section), `app.js` rule ledger synthetic rows/chip, `API_REFERENCE.md`.
- Tests: `test_simulation_fidelity.py` (constructed scenarios for each failing §7.3 control, equivalence equality, mismatch 422 and Gate B FAIL, version accept/reject, narrative-missing typed error), golden assertions added (0 removed — guard run recorded), R6/R7 boundaries, leakage (public ledger zero synthetic rows), dossier, API, TL-07 frontend checks.

## DATABASE/MIGRATION IMPACT
None.

## API/UI IMPACT
Additive: `integrity.ground_truth_backtest`, `simulation_scenario.scenario_version`, synthetic rule rows appended to simulated `rules`, `gap_diagnosis.simulated_rules`. Existing `capacity` keys preserved for both cases.

## TEST EVIDENCE
Gate B PASS (2 scenarios; steel back-test ADVANCE/5 PASS; PP REJECT/0 PASS). Steel rows: R6 DEGRADED/true, R7 DEGRADED/false, R8 DISABLED/null; PP rows: R6 DEGRADED/false, R7 FULL/false, R8 DISABLED/null. Full suite 231 passed; INTEGRITY PASS; SMOKE PASS (goldens unchanged) on `make ci` (uv), project venv and clean pip; Docker PASS. Details: `.workflow/slices/S04-simulation-fidelity/test_evidence.md`.

## VALIDATOR EVIDENCE
`verify_integrity.py` PASS after single regeneration; prohibited-file, threshold-literal and scenario validators PASS; golden assert-removal guard: 0 removed; `git diff --check` clean.

## REVIEW STATUS
Plan: 2 rounds → PLAN_APPROVED. Supervisor implementation review: 0 findings. Independent review (Grok, agent 1194ea8b): **APPROVE — zero unresolved findings**. Models: planner `gpt-5.6-sol-max` (08cc9197); implementer `gpt-5.6-sol-max` (7c3e692c); reviewer `cursor-grok-4.6-xhigh`; supervisor `claude-fable-5-1-thinking-max`.

## SCREENSHOTS
Not applicable (ledger rows reuse existing synthetic styling).

## EXPLICIT NON-GOALS
No public snapshot, config, `docs/core` or DOCX change; no new R-rule inputs (base demand, MES, sustained window); no expansion/allocation schema (KL-27/28); no UI redesign.
