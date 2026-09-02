## SLICE
S02 — Threshold governance (`slice/S02-threshold-governance` → `main`, base `432af8a`).

## OBJECTIVE
No threshold value exists in engine or frontend code; every rule and gate compares against a key read from `config/thresholds.v1.yaml`; a static AST validator fails CI if a configured value reappears as a comparison literal; every threshold has below/equal/above tests (Core 09 §3); R3 compares like with like; the methodology §14.2 R11 export/import ratio enters configuration through the manifest §7.3 gate.

## REQUIREMENTS
FR-002, FR-025, FR-033, FR-034, FR-044, INV-07 (Manifest §6.7 / AGENTS #7), TL-03, TL-08, GATE-C, ADR-005; closes KL-01, KL-02, KL-03 on merge.

## AUTHORITY CHANGE — thresholds 1.1.0 (Manifest §7.3)
Add `rules.R11.generic_capacity_export_import_value_ratio = 50` for `sector_scope: all`. This does not invent or tune a policy value; it makes the methodology §14.2 "more than 50×" generic-capacity test explicit in the versioned operating configuration. Existing thresholds are unchanged. Sensitivity is proven at 49.99 / 50.00 / 50.01, with equality not firing, and by the unchanged steel/public, steel/simulated, PP/public and PP/simulated golden outcomes. The owner's 2026-09-02 completion-build mandate is the recorded methodology-owner approval basis. `metadata.version` 1.0.0 → 1.1.0; `scripts/build_manifests.py` run once after full regression; `authority_hashes.json` and Manifest §11 updated (`32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261`, 3,700 bytes; `sha256sum` verified). `snapshot_manifest.json` changed only in `generated_on`.

## IMPLEMENTATION
- `rules.py`: pure predicates `r1d_fires`, `r2_fires`, `r3_fires`, `r11_generic_capacity_fires`; R3 uses `largest_supplier_share` only (absent → `NOT_CALCULABLE`), never `top_two_value_share`; R3/R11 metrics expose the configured thresholds used.
- `decision_engine.py`: `competition_warning` and the D\* route gate read `competition.post_entry_capacity_to_downside_demand_warning` and `capability.route_bands.incremental_upgrade_max`; `competition` payload adds `warning_fires`.
- `capability.py`: `publication_allowed` predicate (same conjunction).
- `genui.py` + `app.js`: metric grid receives `supplier_concentration` (R3 metrics); the "Resilience review threshold" caption renders the configured value, no numeric fallback.
- `scripts/check_threshold_literals.py`: AST scan of `src/ior_mvp/*.py` comparison literals against all numeric values in `thresholds.v1.yaml` (exempt 0–3); exit 1 on hit, 2 on error; wired into both CI Python jobs and `make ci` immediately after the prohibited-file scan.
- Tests: `test_threshold_boundaries.py` (R1-D count/window; R2 share/growth; R3 HHI/largest; R11 49.99/50/50.01; Kmin 0.6999/0.70/0.7001 + profile sets 0.65/0.70/0.75; D\* edges 0.20/0.40/0.65; competition 1.2499/1.25/1.2501; payload provenance), `test_threshold_literals.py`, R3/R4-F/R11 explicit tests in `test_rules.py`, CI contract step test.

## DATABASE/MIGRATION IMPACT
None.

## API/UI IMPACT
Additive metrics only (`hhi_threshold`, `largest_supplier_share`, `largest_supplier_threshold`, `export_import_value_ratio_threshold`, `warning_fires`); `passes_default_warning` semantics unchanged. UI caption sourced from payload.

## TEST EVIDENCE
Validator red run: 3 hits (`decision_engine.py` 1.25, 0.40; `rules.py` 50) → green `13 Python files; 23 configured numeric values`. Focused 58 passed. Full suite 136 passed; INTEGRITY PASS; SMOKE PASS (steel/public INVESTIGATE; steel/simulated ADVANCE, real unchanged; PP/public REJECT; extraction 100%) on `make ci` (uv) and on a clean pip venv; Docker build PASS. Details: `.workflow/slices/S02-threshold-governance/test_evidence.md`.

## VALIDATOR EVIDENCE
`verify_integrity.py` PASS after the single regeneration; prohibited-file scan PASS; threshold-literal scan PASS; `git diff --check` clean.

## REVIEW STATUS
Plan: 2 rounds → PLAN_APPROVED. Supervisor implementation review: 0 findings. Independent review (Grok, agent 080a70fa): **APPROVE — zero unresolved findings** (5 residual observations recorded, none a defect). Models: planner/implementer `gpt-5.6-sol-max`; reviewer `cursor-grok-4.6-xhigh`; supervisor `claude-fable-5-1-thinking-max`.

## SCREENSHOTS
Not applicable (one caption text change).

## EXPLICIT NON-GOALS
No threshold value tuning; no R5–R8 evaluators; no scenario/dossier changes (S03/S04); no `docs/core`, DOCX, `sector_profiles`, `evidence_policy` or `data/**` change; no CSS change.
