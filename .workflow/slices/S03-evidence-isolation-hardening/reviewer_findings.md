# Independent Reviewer Findings — S03 Evidence-Isolation and Scenario-Validation Hardening

**Reviewer model:** Grok (`cursor-grok-4.6-xhigh`), distinct from Implementer (GPT) and Supervisor (Claude).

**Seat:** Independent reviewer. Read-only. Not Supervisor, not Implementer. This file is the only write.

**Persona:** Evidence-governance skeptical senior reviewer. Data classification: `confidential_demo`.

**Reviewed head:** `slice/S03-evidence-isolation-hardening` from base `c43837054c5581e68cfe7ed87d914a89cd4f63a3` (from `.workflow/state.json` and `s03_review_meta.txt`).

## Files read

Authority and core: `AGENTS.md`; `.cursor/rules/10-domain-guardrails.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md` §6–§11; `docs/authority/methodology_extracted.md` §2.1, §10.2–10.3, §11, §15; `docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md` (all); `docs/core/05` §8–§9; `docs/core/09` §2.1, §4, §6 Gates B/F; `docs/core/04` §2.6, §2.8–2.9, §6; `docs/core/03` §9–§10; `docs/core/01` FR-001, FR-004, FR-011–015, FR-064.

Control records: `docs/ARCHITECTURE_DECISIONS.md` ADR-008; `docs/REQUIREMENTS_TRACEABILITY.md`; `docs/KNOWN_LIMITATIONS.md`; `docs/implementation/API_REFERENCE.md`; `.workflow/state.json`.

Slice records: `persona.md`, `context.md`, `plan.md` (APPROVED; §7–§12, §16, plus §9, §10.1, §14, §17, §29), `plan_review.md` (OQ rulings), `implementation_log.md`, `implementation_review.md`, `test_evidence.md`.

Review package: `.workflow/logs/s03_review_meta.txt`, `s03_governed.patch`, `s03_engine.patch` (app/config hunks plus current-file verification), `s03_tests_stat.txt`.

Current implementation: `config/evidence_policy.v1.yaml`; `src/ior_mvp/evidence.py` (full); `config.py`; `decision_engine.py`; `app.py`; `data_repository.py`; `dossier.py`; `genui.py`; `rules.py` (R5 and `NOT_CALCULABLE`); `static/app.js` (`renderIntegrityBanner`, `escapeHtml`, `getJSON`); `static/styles.css` (new caption rule); `static/index.html` (workspace region); `scripts/validate_scenarios.py`; `scripts/check_threshold_literals.py`; `config/thresholds.v1.yaml`; `config/project.yaml`; `docs/authority/authority_hashes.json`; `data/synthetic/SYN-MINISTRY-STEEL-001.json`; `data/synthetic/SYN-MINISTRY-PP-001.json`; public snapshot producer/trade fields.

Tests: `tests/test_synthetic_isolation.py`; `test_scenario_validation.py`; `test_authority_disclosure.py`; `test_dossier_contract.py`; `test_api.py`; `test_ci_contract.py`; `test_static_frontend.py`; `test_rules.py` (R5); `test_golden_cases.py`; `test_integrity_contract.py`.

CI: `.github/workflows/ci.yml`; `Makefile`.

Skill: `requesting-code-review/code-reviewer.md` (applied).

## Skill result (code-reviewer.md)

### Strengths

- Policy validation is policy-driven for all eight Core 06 §4 fields, class D, source, and display label; missing `display_label` raises `EvidenceIntegrityError` rather than `KeyError`.
- Reconciliation implements only the approved A/B/C1/C2 checks; demand-layer ordering is INFORMATIONAL and non-blocking even when reversed; allocation is always explicit `NOT_APPLICABLE` with no guessed JSON schema.
- Null public nameplates are excluded, not zeroed; missing public import quantity is `NOT_APPLICABLE`, not unlimited; non-finite and boolean values are rejected by `_finite_number`.
- `require_scenario_reconciliation` runs before `_simulate_steel` / `_simulate_pp`. Public analysis never calls `get_synthetic_scenario` / `synthetic_scenarios()`.
- HTTP 422 is reserved for `EvidenceIntegrityError`; absent scenario remains `ValueError` → 404; `AuthorityConfigurationError` is a `RuntimeError` subclass and is not caught by the 404 branch.
- Authority identity is read from `authority_hashes.json` (exactly one `.docx`) and config metadata; no methodology hash or config version is typed into production code. Dossier HTML and the banner escape provenance strings.
- R5 reuses `NOT_CALCULABLE`, reads the threshold from `thresholds["R5"]`, and keeps the approved result/decision-effect strings.
- Tests deepcopy cached fixtures, clear repository and config caches after monkeypatches, and plant Gate B failures only in `tmp_path`. Golden expectations are unchanged. CI Gate B step name and position match the plan.

### Issues

None that meet finding severity. Residual observations are recorded below and do not require remediation to merge this slice.

### Assessment

**Ready to merge?** Yes, from this seat’s domain review (zero unresolved findings). Commit/push/PR/hosted CI remain Supervisor-controlled.

**Reasoning:** The evidence-governance layer matches the approved plan and the cited Core 06 / Core 05 / Core 09 rules. Fail-closed paths block simulation before arithmetic. Public mode does not load synthetic scenarios. I found no invented blocking rule, unknown-to-value conversion in the reconciliation layer, import cycle, or weakened golden/isolation assertion.

## Findings

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | REQUIRED REMEDIATION |
|---|---|---|---|---|---|
| — | — | — | — | No unresolved findings. | — |

Unresolved by severity: **0 blocker / 0 high / 0 medium / 0 low**.

## Cannot verify from files

- Hosted GitHub Actions on the unpushed slice (no PR). Local 191-pass / Gate B / smoke / Docker results are taken from `test_evidence.md` and the Supervisor’s implementation review, not re-executed in this seat.
- Independent `sha256sum` / `wc -c` of `config/evidence_policy.v1.yaml`. Cross-file equality was checked: governed patch, `authority_hashes.json`, and Manifest §11 all carry `f2778c39649fa8d39e3a3311d3639de085cc9b6574ea31dadf259bb8f006cdb2` and 1,373 bytes. Supervisor recorded a matching `sha256sum`.
- Runtime contrast of the banner caption on a painted gradient (static WCAG arithmetic in `test_static_frontend.py` was reviewed and is sound against the two `#rrggbb` stops).
- Whether `/usr/bin/python3` without pytest still fails outside the uv `.venv` (recorded and corrected only in an ignored validation script).

## Residual observations (not findings)

These are assessed items from the review brief that are **not** defects against the approved plan or current fixtures.

1. **Public mode and loader isolation.** `analyze_public` uses only `get_public_case`. `get_synthetic_scenario` is called solely from `analyze_simulated` (`decision_engine.py:289`). `list_opportunities` in public mode therefore never enters `synthetic_scenarios()`. Load-time policy validation cannot change public-mode behaviour. There is no regression test that poisons `data/synthetic` and still expects public 200; the call graph is the proof.

2. **`lru_cache` stickiness.** `functools.lru_cache` does not cache exceptions, so a failed policy/hash/scenario load is retried. A *successful* load is process-sticky until `clear_config_caches` / `clear_repository_caches`. Tests that monkeypatch `AUTHORITY_HASHES_PATH` or `DATA_DIR` do clear caches. Acceptable for this hashed demo; a long-lived process will not see mid-run file fixes without a restart.

3. **Import graph.** `data_repository` → `evidence` → `config`. `config` does not import `evidence` or `data_repository`. No cycle.

4. **Missing demand / `plant_line` block is FAIL, not `NOT_APPLICABLE`.** Matches approved plan §10. Stricter than a literal “wherever concepts are compatible” reading of Core 06 §5.1; fail-closed and planned.

5. **C2 is synthetic-internal physical ceiling** (`nameplate × availability × yield`), not a public marginal. Traced in the approved plan to Core 06 §5.1 / §10 item 3. Not an invented allocation schema.

6. **Demand-layer check never blocks.** Reversed `downside > target` remains `INFORMATIONAL` and overall `PASS` (`test_demand_layer_ordering_is_informational_not_blocking`).

7. **Allocation check never inspects scenario keys.** Always `NOT_APPLICABLE` per OQ-2 / KL-28. A future allocation block under an unknown key would not be summed until a governed schema exists.

8. **`NOT_APPLICABLE` does not block simulation.** Planned §7.2. Missing public `imports_kt` yields `NOT_APPLICABLE` with the unknown visible, not a pass-as-unlimited. No constructed unit test for that missing-quantity path; current fixtures always have latest `imports_kt`.

9. **List endpoint maps only `EvidenceIntegrityError`.** Missing scenario on a *list* call would still be uncaught `ValueError` → 500. Detail routes map it to 404. Plan §12. Both packaged public cases have scenarios.

10. **`AuthorityConfigurationError` unmapped.** Surfaces as FastAPI 500. Unit-tested (`test_authority_summary_fails_loudly_without_methodology_entry`). No HTTP 500 contract test. Acceptable per plan PR-03.

11. **R5 result/decision-effect strings** match plan §14; the new test locks metrics only (`NOT_CALCULABLE`, reason, configured threshold). Execution remains `DEGRADED`. Same `NOT_CALCULABLE` constant as R3. Threshold guard still exempts `0`/`1`; S03 comparison literals are not configured threshold values.

12. **Leakage assertions 1–7.** (1) snapshot `synthetic_flag is False`; (2) public dossier `synthetic_records == 0` and no disclosure string; (3) simulated rows labelled Class D / `DEMO_GENERATOR`; (4) real-decision identity; (5) simulated dossier disclosure; (6) public `synthetic_disclosure is None`; (7) typed fail-closed + 422 + Gate B exit 1. Assertion 3 does not explicitly assert that public rows remain in simulated `evidence` (code appends). HTML check `"0 synthetic records" in text` is a weak substring; JSON `== 0` is the real lock.

13. **CSS / RTL.** New `.integrity-banner .integrity-authority` uses only `var(--teal-soft)` and `overflow-wrap: anywhere`. Contrast test uses WCAG relative luminance of `--teal-soft` against the two 6-digit gradient stops. Pre-existing banner hex colours remain (KL-21). `dir="rtl"` on Arabic names is unchanged.

14. **`getJSON` and object-shaped 422.** `throw new Error(detail.detail || …)` would stringify `{code, message}` as `[object Object]`. Out of plan scope; packaged fixtures do not hit 422 on the happy path.

15. **Traceability honesty.** FR-001 / FR-004 / GATE-B / TL-09 are `IMPLEMENTED`, not `TESTED`/`COMPLETE` (no hosted CI yet). KL-04/05/06 remain open pending merge. ADR-008 remains `Proposed for S03`. TL-01 stays `TESTED` on the S01 CI pointer.

16. **Makefile deviation.** Gate B order is asserted on the `ci:` target only, because `pytest -q` also appears in `test:`. Intent preserved; recorded in `implementation_log.md`.

17. **Pre-existing dossier narrative** still uses `latest.get('imports_kt', 0)` for display copy. Not introduced by S03 reconciliation; not a synthetic unknown-to-value conversion.

## Leakage assertion map (reviewed)

| # | Core 09 §4 | Test |
|---|---|---|
| 1 | Public evidence rows `synthetic_flag=false` | `test_public_snapshots_contain_no_synthetic_rows` |
| 2 | Public analysis contains no synthetic row | Public dossier `synthetic_records == 0` (analysis-derived) |
| 3 | Simulated analysis has public + labelled synthetic rows | `test_every_synthetic_row_is_labeled` |
| 4 | Public-decision fingerprint unchanged | `test_simulated_analysis_keeps_real_decision_identical` |
| 5 | Simulated dossier includes disclosure | `test_simulated_dossier_retains_disclosure`; `test_dossier_html_discloses_simulation` |
| 6 | Real dossier has no synthetic disclosure | `test_real_dossier_has_no_disclosure_and_zero_synthetic_rows` |
| 7 | Malformed scenario fails closed | Policy matrix; 422 API; Gate B temp FAIL/invalid JSON |

## Cross-slice S02

Threshold-literal scanner still walks `Compare` operands against configured numerics with `{0,1,2,3}` exempt. S03 range checks use 0 and 1. R5 threshold is `float(r5_config[...])`, not a literal. `NOT_CALCULABLE` is reused.

## al-muhasibi

- Asked: independent read-only review of S03 evidence isolation against authority, plan, and current files; findings file only; verdict and severity counts.
- Verified: current source, tests, CI/Make, policy YAML, hashes as recorded in JSON/Manifest/patch, call graph for public vs synthetic load, R5 text vs plan §14, OQ-1/2/3 implementation.
- Not re-executed: full pytest, `sha256sum`, hosted CI.
- Assumed: recorded local 191-pass / Gate B / smoke / single generator run in `test_evidence.md` is accurate.

## Verdict

Verdict: APPROVE — zero unresolved findings
