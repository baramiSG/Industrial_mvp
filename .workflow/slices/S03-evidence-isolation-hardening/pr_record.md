## SLICE
S03 — Evidence-isolation and scenario-validation hardening (`slice/S03-evidence-isolation-hardening` → `main`, base `c438370`).

## OBJECTIVE
Synthetic scenarios are validated fail-closed against the evidence policy (all Core 06 §4 fields; Class D; DEMO_GENERATOR; exact display label) with typed `EvidenceIntegrityError`; every scenario is reconciled to its opportunity's public marginals with explicit PASS / FAIL / NOT_APPLICABLE / INFORMATIONAL results, blocking simulation on FAIL and running as a CI gate; the real dossier provably carries no synthetic disclosure; every response, banner and dossier disclose the methodology hash and configuration versions in force (FR-001); R5 discloses its uncomputable threshold as `NOT_CALCULABLE`.

## REQUIREMENTS
FR-001, FR-004, FR-011–FR-015, FR-064, INV-03, INV-04, TL-01, TL-09 (leakage assertion 6), GATE-B, GATE-F, ADR-008; closes KL-04, KL-05, KL-06, KL-26 (transparency) on merge; records KL-27, KL-28 as accepted.

## AUTHORITY CHANGE — evidence_policy 1.1.0 (Manifest §7.3 / ADR-008)
`config/evidence_policy.v1.yaml` 1.0.0 → 1.1.0 (effective 2026-09-02): `synthetic_isolation.required_fields` becomes the Core 06 §4 set (`synthetic_flag, scenario_id, opportunity_id, display_label, seed_basis, evidence_class, source, synthetic_inputs`); adds `required_evidence_class: D` and `required_source: DEMO_GENERATOR` (moved out of code). No evidence class definition, advance gate, label or status list changed. The owner's 2026-09-02 completion-build mandate is the recorded methodology-owner approval. `scripts/build_manifests.py` run once after Gate B PASS, threshold-guard PASS, 191 tests and smoke PASS; `authority_hashes.json` and Manifest §11 updated to `f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2` / 1,373 bytes (`sha256sum` verified). `snapshot_manifest.json` unchanged. Both packaged scenarios pass validation and reconciliation with no data edit.

## IMPLEMENTATION
- `evidence.py`: policy-driven `validate_synthetic_scenario`; `reconcile_synthetic_scenario` (rules: target demand ≤ latest public imports; line nameplate ≤ disclosed producer total; factors in [0,1]; qualified availability ≤ nameplate×availability×yield; demand-layer relation INFORMATIONAL; allocation NOT_APPLICABLE; opportunity-ID match); `require_scenario_reconciliation`.
- `decision_engine.analyze_simulated`: validate → reconcile → block → arithmetic; `integrity.scenario_reconciliation` report; `authority` block on every analysis.
- `config.authority_summary` (+ `AuthorityConfigurationError`, unmapped/loud) reading `authority_hashes.json`, config metadata and `project.yaml`.
- `app.py`: `EvidenceIntegrityError` → 422 `EVIDENCE_INTEGRITY_ERROR` JSON on detail/manifest/dossier/list; absent scenario stays 404.
- `data_repository`: loader delegates to the policy validator (single rule source).
- `dossier.py`/`genui.py`/`app.js`/`index.html`/`styles.css`: authority in JSON and printable HTML; banner caption (token `--teal-soft`); region landmark.
- `rules.py` R5: `NOT_CALCULABLE`, reason, configured threshold.
- `scripts/validate_scenarios.py` (Gate B; exit 0/1/2) after `Verify integrity` in both CI Python jobs and `make ci`.
- Tests: `test_scenario_validation.py`, `test_authority_disclosure.py`, `test_dossier_contract.py`; extended `test_synthetic_isolation.py`, `test_api.py`, `test_rules.py`, `test_ci_contract.py`, `test_static_frontend.py`.

## DATABASE/MIGRATION IMPACT
None.

## API/UI IMPACT
Additive: `authority` object; `integrity.scenario_reconciliation` (null in public mode); R5 metrics; 422 error contract documented in `docs/implementation/API_REFERENCE.md`. UI: banner authority caption; dossier "Authority and versions" section.

## TEST EVIDENCE
Gate B `SCENARIO VALIDATION PASS (2 scenarios)` (steel PASS, PP PASS). Focused 94 passed. Full suite 191 passed; INTEGRITY PASS; SMOKE PASS (golden outcomes unchanged) on `make ci` (uv) and clean pip venv; Docker build PASS. 422 tests (2) and missing-scenario 404 test pass. Details: `.workflow/slices/S03-evidence-isolation-hardening/test_evidence.md`.

## VALIDATOR EVIDENCE
`verify_integrity.py` PASS after single regeneration; `check_prohibited_files.py` PASS; `check_threshold_literals.py` PASS; `validate_scenarios.py` PASS; `git diff --check` clean.

## REVIEW STATUS
Plan: 2 rounds → PLAN_APPROVED (OQ-1/2/3 ruled: no bypass, NOT_APPLICABLE, INFORMATIONAL). Supervisor implementation review: 0 findings. Independent review (Grok, agent 5aef4c24): **APPROVE — zero unresolved findings**. Models: planner `gpt-5.6-sol-max` (9fe6340e), implementer `gpt-5.6-sol-max` (03f26fc4, fresh agent after shell-backend failure of 9fe6340e), reviewer `cursor-grok-4.6-xhigh`, supervisor `claude-fable-5-1-thinking-max`.

## SCREENSHOTS
Not applicable (caption and dossier section text).

## EXPLICIT NON-GOALS
No data edits; no scenario ground-truth or R6/R7/R8 re-evaluation (S04); no expansion-assumption or allocation schema (KL-27/28); no threshold or sector-profile change; no `docs/core`/DOCX change.
