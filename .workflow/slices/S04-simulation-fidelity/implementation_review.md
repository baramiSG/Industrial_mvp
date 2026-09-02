# Supervisor Implementation Review — S04 Simulation-Branch Fidelity

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Implementer: agent 7c3e692c (gpt-5.6-sol-max). Artifacts read: `.workflow/logs/s04_review_meta.txt`, `s04_governed.patch` (line by line), `s04_engine.patch` (`_simulate`, `analyze_simulated`, `evaluate_simulated_rules` R6/R7 in full; function inventory and every `raise`/comparison by grep), roadmap diff, golden-test removed-line check, independent `sha256sum` of both scenario files, implementer's observed results.

## Governed-change audit (Manifest §7.3 / ADR-006)

| Check | Result |
|---|---|
| Scenario JSONs | Additive top-level keys only (`scenario_version`, `ground_truth`, `decision_narrative`) inserted after `scenario_id`; narrative text verbatim from the removed engine literals; `synthetic_inputs` and `seed_basis` untouched. |
| `snapshot_manifest.json` | Only the two synthetic entries changed: PP `06517bb9…eeee5ea` / 3,433 bytes; steel `8867f083…f9aea` / 4,711 bytes — both equal independent `sha256sum`. |
| `authority_hashes.json` | No diff (as required). |
| Public snapshots, configs, `docs/core/**`, DOCX | Untouched. |
| Generator | One run after recorded gates (Gate B with both back-tests PASS; scans; 231 passed; smoke PASS). Integrity PASS. |

## Behaviour audit

| Check | Result |
|---|---|
| Generic selection | `_simulate`: contract validation → capacity projection (formula capacity; equivalence REJECT test §7.4) → capability → economics/competition → §7.3 conjunction with `incremental_upgrade_max` from config → INVESTIGATE fallback; narrative loaded only after state selection; `competition_finding` applied from narrative. No `SAU-H0-` string remains in `decision_engine.py` (grep). |
| Back-test | `evaluate_ground_truth_backtest` compares (state, route_code) only; `require_ground_truth_backtest` raises `EvidenceIntegrityError` before any simulated field is attached; report stored in `integrity.ground_truth_backtest`; Gate B `_ground_truth_check` added. |
| Contract validation | `SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})`; typed errors for version/ground-truth/narrative structure; computed state without narrative → typed error (PR-01). |
| R6/R7/R8 synthetic rows | Thresholds read from `rules.R6/R7/R8`; R6 DEGRADED (sustained NOT_CALCULABLE) fired steel / not PP with denominator effective qualified capacity (falls back to `formula_capacity_kt` for PP); R7 DEGRADED/false steel (equivalence NOT_CALCULABLE), FULL/false PP; R8 DISABLED/null with layers disclosed. Rows carry `synthetic_flag`, class D, source, label, `basis`; appended only in simulated mode. |
| Golden values | 57.509 / 46.491 / D\* 0.2667 / S\* 18 / ΔNV 198 / ratio 1.0751; steel ADVANCE 5; PP REJECT 0, gap −24, support 0 — smoke PASS on uv and clean pip; Docker PASS. `tests/test_golden_cases.py`: 0 removed lines; assertions added only. |
| Threshold guard | Scan PASS (no new comparison literals). |
| UI/dossier | Rule ledger renders synthetic rows with existing `.synthetic-row`/chip classes; dossier `gap_diagnosis.simulated_rules` and HTML section; TL-07 tests added. |
| Tests | 191 → 231. |
| Deviations | Test fixture for the mismatch case adjusted to satisfy PR-01 (narrative present for computed state) — consistent with the approved intent. `docs/BUILD_ROADMAP.md` S04 row aligned to final field names — accepted. |
| Traceability honesty | Rows at IMPLEMENTED; KL-07/08 pending wording; ADR-006 Accepted text present. |

## Findings

None. Supervisor findings unresolved: **0**.

Disposition: proceed to independent review.
