# Independent Reviewer Findings — S04 Simulation-Branch Fidelity

**Reviewer model:** Cursor Grok 4.6 (`cursor-grok-4.6-xhigh`)
**Implementer model:** GPT-5.6 Sol (`gpt-5.6-sol-max`)
**Supervisor model:** Claude (`claude-fable-5-1-thinking-max`)
**Seat:** Independent Reviewer (read-only). Not the Supervisor. Not the Implementer. Cannot remediate or approve own findings.
**Discipline persona:** Delivery / decision-engine audit (sanad-provenance + al-muhasibi).
**Data classification:** `confidential_demo` (frozen public snapshots and Class-D demo scenarios only).
**Branch / base observed:** `slice/S04-simulation-fidelity` from `ddf905d5051fe3b4468bdcd793a8a640f5040048` (uncommitted staged slice work; HEAD still the S03 merge).
**Plan authority:** `plan_review.md` records `PLAN_APPROVED` 2026-09-02.
**Skill applied:** `requesting-code-review` / `code-reviewer.md` (plan alignment, fail-closed behaviour, test fidelity, architecture, production readiness; issues calibrated by actual severity).

This review does not authorise merge, commit, push, PR, or public support.

---

## Skill result (`code-reviewer.md`)

### Strengths

- Generic `_simulate` replaces `_simulate_steel` / `_simulate_pp`. No `SAU-H0-` comparison remains in `decision_engine.py`. Core 07 §7.4 (exact boolean equivalence and qualified availability ≥ target → REJECT route 0) is evaluated before the §7.3 conjunction (positive gap, publishable D*, D* ≤ configured incremental-upgrade max, economics `passes`, ΔNV `positive is True`, competition default warning passes → ADVANCE route 5); any other non-equivalence outcome is INVESTIGATE with route `None`.
- Narrative is loaded only after state/route selection (`_decision_narrative`). Ground-truth mismatch still yields ADVANCE for steel (`test_ground_truth_never_drives_selection_and_mismatch_fails`). Missing computed-state narrative raises `EvidenceIntegrityError`, not `KeyError`.
- Runtime back-test runs after `_simulate` and **before** any simulated field is attached to the returned analysis. Existing `app.py` maps `EvidenceIntegrityError` to HTTP 422 with `EVIDENCE_INTEGRITY_ERROR`. Gate B `_ground_truth_check` is blocking FAIL (exit 1); invalid JSON remains exit 2.
- Synthetic R6/R7/R8 rows are appended only in simulated mode, carry `synthetic_flag` / Class D / `DEMO_GENERATOR` / display label / `basis=synthetic`, and are absent from public `rules`. R6 uses configured utilisation/shortage thresholds, effective-qualified-capacity denominator with `formula_capacity_kt` fallback, division guard, and `sustained_period: NOT_CALCULABLE` → DEGRADED. R8 stays DISABLED and does not invent base/MES/probability.
- Packaged goldens are preserved: steel 57.509 / 46.491 / D* 0.2667 / S* 18 / ΔNV 198 / ratio 1.0751 / ADVANCE 5; PP 104.49 / 80 ≥ 56 / gap −24 / support 0 / REJECT 0. Independent arithmetic in this review reproduced those figures. `tests/test_golden_cases.py` gained assertions only (no removed `assert` lines vs base).
- Governed change is additive: `scenario_version` / `ground_truth` / `decision_narrative` after `scenario_id`; `synthetic_inputs` and `seed_basis` untouched. `snapshot_manifest.json` changed only the two synthetic SHA/byte entries. `authority_hashes.json` has no diff. Independent `sha256sum` equals the manifest. Threshold YAML and frozen core are untouched. Route 0/5 are methodology identities, not duplicated YAML thresholds.

### Issues

No Critical, Important, or Minor defects requiring remediation before independent-review close.

### Assessment

**Ready to merge?** Yes, from this seat, subject to Supervisor-controlled staging/commit/PR/hosted CI (not in reviewer authority).

**Reasoning:** The implementation matches the approved plan on selection order, fail-closed back-test, synthetic isolation, R6/R7/R8 abstention semantics, golden numbers, and the single-generator governed edit. Residual notes below are not unresolved findings.

---

## Files read (this review)

Authority / ritual: `AGENTS.md`; `.cursor/rules/10-domain-guardrails.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md` §6, §7.3, §8, §10; `docs/authority/methodology_extracted.md` (cited ranges); `docs/core/01`, `02` §3 and §5–§6, `04` §2.6/§2.9–2.10/§6, `06` §5.3/§6–§10, `07` §2–§3 and §7.2–7.4/§8/§10–§11, `09` §2.4/§2.7/§4; `docs/ARCHITECTURE_DECISIONS.md` ADR-006; `docs/REQUIREMENTS_TRACEABILITY.md`; `docs/KNOWN_LIMITATIONS.md`; `docs/implementation/API_REFERENCE.md`; `.workflow/state.json`.

Slice package: `persona.md`, `context.md`, `plan.md` (§7–§12, §14, §19, §24 and drafts), `plan_review.md`, `implementation_log.md`, `implementation_review.md`, `test_evidence.md`.

Review bundle: `.workflow/logs/s04_review_meta.txt`, `s04_governed.patch`, `s04_engine.patch`, `s04_other.patch`; logs `s04-post-generator.log`, `s04-t5-assert-guard.log`, `s04-t11-self-audit.log`, `s04-final.log`, `s04-generator.log`.

Current code / data / tests: `src/ior_mvp/decision_engine.py` (full); `rules.py` (`evaluate_simulated_rules`, `_synthetic_rule`); `evidence.py` (validator, reconcile, `synthetic_evidence_rows`, `isolated_copy`); `dossier.py`; `genui.py`; `app.py` 422 mapping; `data_repository.py`; `capability.py` (hard-gate / D* publication); `economics.py` (`passes`, `positive`); `static/app.js` (`renderRuleLedger`, `renderIntegrityBanner`, `renderDecisionActions`, `ruleBoundaryChip`, `renderMethodology`); `scripts/validate_scenarios.py`; `scripts/check_threshold_literals.py`; `config/thresholds.v1.yaml` R6/R7/R8 and `route_bands`; `config/sector_profiles.v1.yaml`; both `data/synthetic/*.json`; `data/manifests/snapshot_manifest.json`; `docs/authority/authority_hashes.json`; `tests/test_simulation_fidelity.py`, `test_golden_cases.py`, `test_threshold_boundaries.py`, `test_synthetic_isolation.py`, `test_scenario_validation.py`, `test_api.py`, `test_dossier_contract.py`, `test_static_frontend.py`.

Independent checks this session: `sha256sum` of both scenario files; Python reproduction of capacity/gap/ratio/Dknown/R6 precedence; `git diff` empty for `authority_hashes.json`, `config/`, public snapshots, and `docs/core/`; golden-test diff is addition-only.

---

## Steel / PP trace through `_simulate`

### Steel (`SYN-MINISTRY-STEEL-001`)

1. No `equivalence` block → `_capacity_projection` uses formula capacity `250×0.92×0.94×0.38×0.70 = 57.5092` (API 57.509); gap `104−57.5092 = 46.4908` (API 46.491); `equivalence_reject=False`.
2. Hard gates all `resolved…` → `route_publishable=True`; Dknown `= 0.2666…` (API D* 0.2667) ≤ configured `incremental_upgrade_max` 0.40.
3. Cash-flow economics pass with S*=18; ΔNV 198 `positive=True`; ratio `(57.5092+50)/100 = 1.075092` (API 1.0751) ≤ 1.25.
4. §7.3 conjunction true → **ADVANCE route 5**. Narrative from `decision_narrative.ADVANCE` (verbatim former engine literals). Back-test matches `ground_truth` (ADVANCE, 5).
5. Synthetic R6: utilisation 0.89 ≥ 0.85 and shortage `(104−57.509)/57.509 = 0.8084` ≥ 0.10, `sustained_period=NOT_CALCULABLE` → DEGRADED, fired true (not an input to §7.3). R7: 0.89 > 0.70, equivalence absent → DEGRADED, fired false. R8: DISABLED, layers disclosed, base/MES/probability `NOT_CALCULABLE`.

### Polypropylene (`SYN-MINISTRY-PP-001`)

1. Equivalence `true` and `80 ≥ 56` → §7.4 **REJECT route 0** before §7.3. Gap `56−80 = −24`. Formula capacity diagnostic 104.49 retained. `support_required` path: `passes=False`, support 0.0.
2. Back-test matches (REJECT, 0).
3. Synthetic R6: 0.78 < 0.85, shortage `(56−104.49)/104.49 = −0.4641` via `formula_capacity_kt` fallback → DEGRADED, fired false. R7: both inputs present, 0.78 > 0.70 → FULL, fired false. R8: DISABLED, committed/announced 0 disclosed.

Public `INVESTIGATE` / `REJECT` and `real_decision` fingerprint are unchanged (`analyze_public` first; `assert_real_decision_unchanged` after attach).

---

## Findings table

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | REQUIRED REMEDIATION |
|---|---|---|---|---|---|
| — | — | — | — | No unresolved findings. | — |

**Counts:** Critical 0 · Important/HIGH 0 · MEDIUM 0 · LOW/Minor 0. Unresolved: **0**.

---

## Cannot-verify

- This session did not re-execute `PYTHONPATH=src pytest -q`, `scripts/verify_integrity.py`, `scripts/demo_smoke.py`, or `make ci`. Those are evidenced in `.workflow/logs/s04-t11-self-audit.log` (`231 passed`; `INTEGRITY PASS`; Gate B PASS with both `ground_truth_backtest: PASS`) and `.workflow/logs/s04-final.log`. Hosted CI is not in scope before PR.
- Docker evidence is **image build** success (`EXIT_docker=0`), not an in-container test run. `test_evidence.md` states that accurately.
- The governing DOCX was not re-parsed as binary; Core 07 and the extracted mirror were used as specified. No DOCX/mirror conflict was found on the reviewed rules.
- Frontend proof remains static source inspection (Core 09 §2.7). No browser pass was performed.
- `implementation_review.md` was read; it was not listed in `s04_review_meta.txt` staged paths at snapshot time.

No `test_evidence.md` claim that was checked against files was found to be unsupported. Generator log shows a single `scripts/build_manifests.py` invocation after recorded §24 preconditions.

---

## Residual observations (not findings)

1. `analyze_simulated` does not `isolated_copy` the `lru_cache`d scenario (`decision_engine.py:729`). `_simulate` and `evaluate_simulated_rules` were inspected and do not mutate scenario mappings (condition lists are copied). Tests deepcopy before mutation. Defence-in-depth copy would match the public-case pattern; no defect demonstrated.
2. `_capacity_projection` leaves `has_equivalence` unused (`decision_engine.py:370-371`). Dead local, copied from the approved draft; no behaviour effect.
3. `effective_qualified_capacity` `ValueError` is not wrapped as `EvidenceIntegrityError` inside `_capacity_projection`. Packaged/runtime path is blocked earlier by reconciliation unit-interval checks. Direct `_simulate` with out-of-range factors could raise `ValueError` (API maps `ValueError` to 404). Not reachable on the reviewed fixtures.
4. Plan §9.1 prose asks for non-negative `qualified_available_kt`; the approved code draft and implementation only require a finite number. Packaged values are non-negative. A negative value could distort §7.4/§7.3; not exercised by fixtures or tests.
5. Methodology §4 R7 also names availability in the demand window. The approved slice contract evaluates utilisation ≤ configured maximum **and** equivalence when required. Implementation matches that contract; R7 boundary tests use the PP fixture where qualified availability is present. KL-25 already records R8 abstention; R7 availability/timing is out of this MVP’s executable test.
6. `docs/REQUIREMENTS_TRACEABILITY.md` FR-044 still names deleted `_simulate_steel`. Competition now lives in `_simulation_economics` / `_simulate`. Stale pointer in a row the plan did not require rewriting; not an engine defect.
7. GATE-H still describes the S01 “generator not run” situation. S04 did run the generator once. Historical row; Supervisor promotion after merge can refresh it.
8. Simulated methodology-summary counts in `renderMethodology` include the three synthetic rows, so FULL/DEGRADED/DISABLED totals are not comparable to public mode. Both ledgers are intended to show the appended rows.
9. Threshold-literal scanner inspects `ast.Compare` operands only. `round(..., 3|4)` and route codes 0/5 are allowed (methodology identities / existing rounding). No new YAML-threshold comparison literals were found in engine/rules.

Assumptions: packaged JSON is the only production scenario set; `evidence_policy` 1.1.0 still allows additive top-level keys; Supervisor remains the only seat for commit/PR/CI/merge.

---

## Al-muhasibi

Asked: independent REJECT/APPROVE against methodology, approved plan, and current files.
Verified: selection order, conjunction, goldens (independent arithmetic + source), leakage, typed back-test/422/Gate B FAIL, R6/R7/R8 semantics, governed hashes, golden-assert additivity, tests named in the review scope.
Not re-executed: full local gates and hosted CI.
Not assumed as fact: Docker-in-container tests; live UI behaviour.

---

Verdict: APPROVE — zero unresolved findings
