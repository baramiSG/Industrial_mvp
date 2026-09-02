# Supervisor Implementation Review — S08 Public Snapshot Schema v2 and Computed Rule Ledger

Reviewer: Supervisor (Claude, `claude-fable-5-1-thinking-max`). Implementer: agent f1587e62 (GPT-5.6 Sol, `gpt-5.6-sol-max`). Candidate: uncommitted working tree on `slice/S08-snapshot-v2-computed-rules` at base `9f045a4`; 84 candidate paths (two byte-identical v1 moves, two v2 snapshots, `public_snapshot.py`, `trade_metrics.py`, rules/engine/dossier/config/repository changes, tests incl. the migration-equivalence suite, regenerated baselines, Core 02/04/07/09 v2, thresholds 1.2.0, catalogue 1.1.0, ADR-012, docs, records).

## What I inspected (2026-09-02)

- Protected paths: `git diff --name-only -- data/synthetic data/golden sector_profiles evidence_policy docs/core/01,03,05,06,08 DOCX` → empty. Governed diff: `thresholds.v1.yaml` 1.2.0 with only `rules.R4_D.minimum_valid_value_coverage: 0.70` plus the ruled rationale/revision date; catalogue 1.1.0 with exactly the six approved key pairs; Core 02/04/07/09 v2 edits; `snapshot_manifest.json` two v1 rows moved to `historical/v1/` with unchanged hashes (`cc28e77d…`, `10efb192…`) plus two v2 rows; `authority_hashes.json` and Manifest §11 rows for thresholds, catalogue and Core 02/04/07/09. One generator run.
- `tests/test_golden_cases.py` diff is additive only (R2 span/CAGR, R11 execution/ratio assertions); all frozen expectations retained.
- `public_snapshot.py` (1,310 lines) allow-lists keys and rejects authored outcome keys: my negative probes — `rule_context`, top-level `fired`, and a nested unknown `domestic_capability.r9_fired` — were all rejected with typed errors.
- `decision_engine._public_decision` now branches on the computed R11 `fired` (no `rule_context`); `analyze_public` exposes `schema_version`, `domestic_flows`, `criticality_designation` and the compatibility `supplier_metrics` built from computed R3/R4-D metrics (steel HHI 0.36 still displayed).
- Migration-equivalence suite (`tests/test_snapshot_migration_equivalence.py`): converts historical v1 through a test-only adapter, asserts identical rule-ID order and identical `fired` map, and asserts the deep diff equals exactly an additive path allow-list plus the enumerated intended changes (R3/R4-D result texts; steel R11 `DEGRADED`→`FULL`, ratio `null`→0.1144); public decisions identical. Honest anti-drift proof.
- Dossier: `contradiction_register` (public/synthetic/`synthetic_status`) present in JSON (`dossier_version` 1.1) and rendered in both locales with catalogue chrome and source-language islands; PP simulated register shows `NONE_RECORDED`, public shows `NOT_APPLICABLE`.
- Rules/metrics: no threshold literals (scanner PASS, 15 Python files); R9-S/R10/R11 derivations as planned.
- KL-32: regenerated baselines and directories are host-owned (`stat` → uid 1000 `barami`).

## Verification I ran myself

| Check | Result |
|---|---|
| `make ci` (with `LD_LIBRARY_PATH`) | exit 0 in 2m33s: prohibited scan 344 files, threshold scan PASS, UI contracts PASS, ES modules PASS, `INTEGRITY PASS`, Gate B PASS, `503 passed`, `SMOKE PASS` (steel INVESTIGATE / simulated ADVANCE real unchanged / PP REJECT), preflight PASS, functional `118 passed`, visual `4 passed` |
| Live v2 vs converted v1 (my probe): `evaluate_rules(live_v2)` compared field-by-field with `_evaluate_rules_v2(candidate_v2_from_legacy(historical_v1))` for both goldens | **identical** (execution, fired, result, metrics) — the hand-authored v2 files carry exactly the v1 facts |
| Negative probes on the validator | authored outcome keys and nested unknown keys rejected |
| Dossier HTML `?locale=ar` public steel | register renders `سجل التناقضات` with the S-UNICOIL-SPEC contradiction as an LTR island |
| Regenerated `en` desktop steel public dossier baseline (viewed) | contradiction register present; no new visual defect |

## Findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| SR-01 | LOW | Core 09 §8 anti-gaming; plan §17 migration-equivalence intent | `test_snapshot_migration_equivalence.py` proves converted-v1 ≡ v2 *rules* and v2 identity fields, but the live hand-authored v2 files are compared to the converted candidate only indirectly (goldens + rule-ID order). My manual probe shows they are identical. | A future hand edit to a live v2 file that drifts from the historical facts would not be caught by a dedicated equality assertion. | Add `test_live_v2_ledger_equals_converted_historical_v1` asserting, for both goldens, that `evaluate_rules(live_v2)` equals `_evaluate_rules_v2(candidate_v2_from_legacy(historical_v1))` on execution/fired/result/metrics, and that `_public_decision` outputs are equal. Record in the log. |

Non-blocking observation (recorded as KL-33, scheduled S19, not an S08 finding): the dossier "Supply conclusion" renders the `domestic_capability` object as a raw JSON `<code>` island (pre-existing since S07 at `dossier.py` line 266 of `main`; unchanged behaviour, now with the richer v2 object). Methodology §15 requires a structured supply conclusion (named producers, effective capacity, utilisation, target specifications, planned changes); S19 owns the dossier redesign.

## Round 2

Implementer (same agent) added `test_live_v2_ledger_equals_converted_historical_v1` (both goldens; execution/fired/result/metrics and public decision equality) plus an in-memory drift negative test (mutating `trade[-1]["imports_kt"]` breaks equality), RED→GREEN recorded. Supervisor verified: migration-equivalence file passes; default suite `506 passed`. Candidate identity captured at `/tmp/s08_candidate_hashes_v1.txt` (excluding Supervisor/reviewer records).

Unresolved Supervisor findings: **0**. Handing to the independent reviewer (Grok 4.6).
