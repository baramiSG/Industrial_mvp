# Supervisor Plan Review — S03 Evidence-Isolation and Scenario-Validation Hardening

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Planner: agent 9fe6340e (gpt-5.6-sol-max). Plan sections read: Global constraints, §1–§2, §7 (contracts), §8 (governed YAML), §9 (reconciliation rules with fixture arithmetic), §10 (evidence.py through nameplate check; grep-verified that `reconcile_synthetic_scenario` and `synthetic_evidence_rows` call `validate_synthetic_scenario` first), §11 (config authority, decision_engine ordering, genui), §12 (API mapping), §16 test inventory (grep), §29 (open questions), §30.

## Verification performed

- Reconciliation rules A, B, C1, C2 traced to Core 06 §5.1 / §10 and Core 05 §8; arithmetic on the frozen fixtures re-derived: steel 104 ≤ 287.9; 250 ≤ 250,000/1000 (Hadeed null excluded); PP 56 ≤ 56 (equality passes); 1,170 ≤ (450,000+720,000)/1000 (SABIC null excluded); PP qualified 80 ≤ 1,170×0.93×0.97 = 1,055.457. Demand-layer relation correctly INFORMATIONAL (Core 04 §2.6 does not state a pass/fail inequality). Allocation sums correctly NOT_APPLICABLE (no governed schema). No invented rule.
- Policy validation covers all Core 06 §4 fields, class D, source and label from policy, typed errors only; `synthetic_inputs` must be a mapping.
- Ordering: validation → reconciliation → `require_scenario_reconciliation` → simulation arithmetic; public path sets `integrity.scenario_reconciliation = null`.
- Governed change limited to `evidence_policy.v1.yaml` (1.1.0; eight required fields; `required_evidence_class`, `required_source`); single generator run pattern as S02.
- `authority_summary()` reads the DOCX entry from `authority_hashes.json` (exactly one `.docx`), versions from config metadata, project version from `project.yaml`; no version string typed into code. Literals 64/12 are not configured threshold values.

## Round 1 findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| PR-01 | MEDIUM | Core 03 §10 ("unknown opportunity → 404"; "missing synthetic scenario → error"); `docs/implementation/API_REFERENCE.md` "Error behavior: missing synthetic scenario in simulated mode: HTTP 404" | Plan §11.2 changes `if scenario is None: raise ValueError(...)` to `raise EvidenceIntegrityError(...)`, which §12 maps to 422. | An absent artifact is a not-found condition, not an evidence-integrity violation; the change contradicts the published API reference and blurs the meaning of the new 422 code. | Keep `ValueError` (→ 404) for an absent scenario. Reserve 422 `EVIDENCE_INTEGRITY_ERROR` for policy and reconciliation failures. Add `docs/implementation/API_REFERENCE.md` to the modify list with one new error-behavior line for 422. Add an API test that a missing scenario in simulated mode returns 404 (monkeypatch `get_synthetic_scenario` to return `None`). |
| PR-02 | LOW (rulings) | Owner mandate §29 (BLOCKED_FOR_OWNER only when a real decision is needed) | Plan §29 OQ-1..3 | The safe defaults chosen by the plan require no owner decision now; leaving them "open" would misrepresent the state. | Record in §29 as resolved by Supervisor ruling: **OQ-1** — no expansion-assumption bypass in this MVP; nameplate ceiling applies; schema to be defined only if a future scenario needs it (add KL entry "accepted"). **OQ-2** — allocation blocks absent by design; NOT_APPLICABLE stands; schema deferred (add KL entry "accepted"). **OQ-3** — demand-layer relation is INFORMATIONAL, never blocking, absent methodology language. No `BLOCKED_FOR_OWNER`. |
| PR-03 | LOW | Core 03 §10 ("malformed config → startup or request failure"), fail-closed honesty | Plan §11.1 `authority_summary`/`_metadata_version` raise `ValueError`; `_safe_analysis` maps `ValueError` → 404. | A malformed authority manifest or config metadata would be reported as "not found", hiding a governance defect behind a routine status. | Raise a dedicated `RuntimeError` subclass (e.g. `AuthorityConfigurationError`) from `authority_summary`/`_metadata_version`/`_load_json`; leave it unmapped so it surfaces as a server error (loud), or map it explicitly to 500 with code `AUTHORITY_CONFIGURATION_ERROR`. Add one unit test with a temp manifest missing the DOCX entry. |

No BLOCKER or HIGH findings.

## Round 2

Planner revised `plan.md` (same agent). Supervisor verified: PR-01 at lines 163, 1321–1322, 2693–2710, 3374, 3583 (absent scenario stays `ValueError` → 404; API_REFERENCE 422 line; new 404 test); PR-02 at lines 3149–3153, 3582, 3710–3727 (rulings recorded; KL-27/KL-28 accepted); PR-03 at lines 1117–1239, 1446, 2405–2532, 3023, 3080 (`AuthorityConfigurationError` raised from config loading/validation, deliberately unmapped, unit-tested).

Unresolved findings: **0**.

## Decision

**PLAN_APPROVED** — 2026-09-02, Supervisor. Implementation may begin on `slice/S03-evidence-isolation-hardening` from base `c43837054c5581e68cfe7ed87d914a89cd4f63a3`, executing plan Tasks 0–12 and the Task 14 detached local validation as pre-review evidence. The single `scripts/build_manifests.py` run is pre-authorised under the plan's Task 10/11 conditions (planned-only YAML diff on `evidence_policy.v1.yaml`; Gate B validator clean; full pytest and smoke green). Rulings OQ-1/2/3 stand as recorded. Commit/push/PR/merge remain Supervisor-controlled.
