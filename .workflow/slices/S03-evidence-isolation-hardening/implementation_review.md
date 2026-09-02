# Supervisor Implementation Review — S03 Evidence-Isolation and Scenario-Validation Hardening

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Implementer: agent 03f26fc4 (gpt-5.6-sol-max; fresh agent after the first implementer's shell backend died — agent 9fe6340e stopped safely at the RED gate with no production edits). Artifacts read: `.workflow/logs/s03_review_meta.txt`, `s03_governed.patch` (line by line), `s03_engine.patch` (all non-`evidence.py` hunks in full; `evidence.py` orchestration `reconcile_synthetic_scenario`/`require_scenario_reconciliation`/`synthetic_evidence_rows` in full; check functions grep-verified against the approved §10 draft), `s03_other.patch` (CI, Makefile, ADR-008, KNOWN_LIMITATIONS, traceability, `validate_scenarios.py` main, `app.js`, `index.html`, `styles.css`), `implementation_log.md` deviations, `test_evidence.md` via the implementer's observed results; independent `sha256sum`/`wc -c` by shell subagent.

## Governed-change audit (Manifest §7.3, §8)

| Check | Result |
|---|---|
| `config/evidence_policy.v1.yaml` diff limited to planned lines | Yes — `version` 1.0.0→1.1.0, `effective_date` 2026-09-02, `required_fields` gains `opportunity_id`, `display_label`, `synthetic_inputs`; `required_evidence_class: D`; `required_source: DEMO_GENERATOR`; nothing else. |
| `authority_hashes.json` | Only the evidence_policy `sha256`/`bytes` changed (`generated_on` already 2026-09-02 from S02). |
| `sha256sum config/evidence_policy.v1.yaml` | `f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2`, 1,373 bytes — equals JSON and §11 row. |
| `snapshot_manifest.json` | No diff. |
| `data/**`, `thresholds`, `sector_profiles`, `docs/core/**`, DOCX | Untouched. |
| Generator run | Once, after recorded gates (Gate B PASS, threshold scan PASS, 191 passed, SMOKE PASS). Integrity PASS afterwards. |

## Behaviour audit

| Check | Result |
|---|---|
| Fail-closed policy validation | All eight Core 06 §4 fields; class/source/label read from policy; `synthetic_inputs` must be a mapping; every violation `EvidenceIntegrityError`. Repository loader delegates to the same validator (no duplicate rule). |
| Reconciliation | Rules A, B, C1, C2 as approved; opportunity-ID match guard; INFORMATIONAL demand-layer observation; NOT_APPLICABLE allocation check; overall status FAIL > PASS > NOT_APPLICABLE; `require_scenario_reconciliation` raises before any simulation arithmetic. Both fixtures PASS with no data edit (Gate B: `SCENARIO VALIDATION PASS (2 scenarios)`). |
| API | `EvidenceIntegrityError` → 422 `{"detail": {"code": "EVIDENCE_INTEGRITY_ERROR", ...}}` on detail, manifest, dossier and list routes; absent scenario stays `ValueError` → 404 (test added); `AuthorityConfigurationError` deliberately unmapped. |
| FR-001 authority | `config.authority_summary()` reads DOCX path/hash from `authority_hashes.json`, versions from config metadata, project version from `project.yaml`; present in analysis, banner props, dossier JSON and HTML; no version string typed in code. |
| R5 | `NOT_CALCULABLE` + reason + configured threshold; execution/fired unchanged. |
| UI | Banner caption from props; new CSS uses `var(--teal-soft)` only; `role="region"` + `aria-label` added; `node --check` OK. |
| Tests | 136 → 191; leakage assertions 1–7 all covered (`test_dossier_contract.py` for #6); planted-failure Gate B test on temp files; 422/404 API tests; authority tests; contrast test. Golden outcomes unchanged (smoke PASS on uv and clean pip; Docker PASS). |
| Deviation | Makefile assertion scoped to `ci:` target (the approved draft matched `pytest -q` in the earlier `test` target) — correct fix preserving intent; recorded in `implementation_log.md`. Managed background execution again used — no behavioural effect. |
| Traceability honesty | FR-001, FR-004, INV-03, INV-04, TL-01, TL-09, GATE-B, GATE-F → IMPLEMENTED with pointers; KL-04/05/06 pending wording; KL-27/28 accepted; ADR-008 Proposed (Supervisor sets Accepted at merge). |

## Findings

None. Supervisor findings unresolved: **0**.

Observation (no action): `renderIntegrityBanner` dereferences `props.authority.methodology` without a null guard; acceptable because `authority` is mandatory in every analysis and its absence is a loud server error by design.

Disposition: proceed to independent review.
