# Independent Reviewer Findings — S02 Threshold Governance

**Reviewer model:** cursor-grok-4.6-xhigh (Grok). Distinct from Implementer (gpt-5.6-sol-max) and Supervisor (claude-fable-5-1-thinking-max).

**Seat:** Independent Reviewer. Read-only. Not Supervisor. Not Implementer. No fix authority. No self-approval.

**Persona held:** skeptical senior reviewer of a deterministic policy engine and its authority chain.

**Data classification:** Internal repository source/configuration plus public and synthetic fixtures. No Restricted data, credentials, secrets, personal data, or live sources were accessed.

**Branch / base (from review package):** `slice/S02-threshold-governance` at recorded base `432af8af1fa88a2258a0fd8d825a6855e408270f`.

**Skill applied:** `requesting-code-review` / `code-reviewer.md` (read in full before the file audit). Calibration: Critical = golden/authority/strictness breakage; Important = missing required behaviour or unsound proof; Minor = non-blocking residuals. Nitpicks are not findings.

---

## Files read

Authority and ritual:

- `AGENTS.md` (non-negotiable #7, proof rule, build-control, authority-change paragraph)
- `.cursor/rules/10-domain-guardrails.mdc`
- `docs/authority/00_AUTHORITY_MANIFEST.md` §6.7, §7.2–7.3, §8, §10, §11 (full file)
- `docs/authority/methodology_extracted.md` lines 340–432, 638–705, 863–872, 1545–1560, 1737–1762
- `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md` §3, §4.3–4.4, §5.6, §7.3, §9, §10
- `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` §2.3–2.4, §3, §8
- `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md` §3
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-005)
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/KNOWN_LIMITATIONS.md`
- `.workflow/state.json`

Slice package:

- `.workflow/slices/S02-threshold-governance/persona.md`
- `context.md`, `plan.md` (APPROVED), `plan_review.md`
- `implementation_log.md`, `implementation_review.md`, `test_evidence.md`

Review package:

- `.workflow/logs/s02_review_meta.txt`
- `.workflow/logs/s02_governed.patch`
- `.workflow/logs/s02_code.patch`
- `.workflow/logs/s02_docs.patch`

Current files:

- `config/thresholds.v1.yaml`
- `config/sector_profiles.v1.yaml`
- `src/ior_mvp/rules.py`, `decision_engine.py`, `capability.py`, `genui.py`, `config.py`, `data_repository.py`, `evidence.py`, `economics.py`, `static/app.js` (`renderMetricGrid`)
- `scripts/check_threshold_literals.py`
- `tests/test_threshold_boundaries.py`, `test_threshold_literals.py`, `test_rules.py`, `test_ci_contract.py`, `test_golden_cases.py`
- `.github/workflows/ci.yml`, `Makefile`
- `docs/authority/authority_hashes.json`
- `data/manifests/snapshot_manifest.json`
- `data/snapshots/public/SAU-H0-721049.json` (supplier metrics and trade)
- `data/snapshots/public/SAU-H0-390210.json` (trade rows, no supplier block, `generic_capacity_reject: true`)

Skill:

- `C:\Users\Admin\.cursor\plugins\cache\cursor-public\superpowers\d884ae04edebef577e82ff7c4e143debd0bbec99\skills\requesting-code-review\SKILL.md`
- `...\skills\requesting-code-review\code-reviewer.md`

---

## Skill result (`code-reviewer.md`)

### Strengths

- Governed YAML change is the planned 1.1.0 metadata edit plus the single new R11 key; no existing numeric threshold was retuned.
- Predicate extraction preserves prior strictness: R2/R3/Kmin/bands inclusive; competition and R11 strictly greater.
- R3 now compares HHI with HHI and largest-supplier share with largest-supplier share; `top_two_value_share` is diagnostic only.
- Boundary matrices match Core 09 §3 (below/equal/above) including R11 49.99 / 50.00 / 50.01.
- AST validator matches the approved algorithm; CI and Makefile insert it immediately after the prohibited-file scan; existing CI assertions were not weakened.
- Response-contract changes are additive. `passes_default_warning` remains the inverse of the warning predicate.
- Traceability stays at `IMPLEMENTED` (not `TESTED`/`COMPLETE`). ADR-005 is Accepted with the final key name. KL-01..03 remain Open with pending-closure wording.
- Golden expectation files were not edited.

### Issues

No Critical, Important, or Minor issues that require remediation before merge. Residual plan-level limitations are recorded below the findings table and are not unresolved defects of this implementation.

### Recommendations

None that are merge-blocking. Future hardening (not this slice): recursive `rglob` if engine subpackages appear; keep BinOp/Call aliases out of comparison sites; continue to treat named-constant aliases as outside this validator’s contract.

### Assessment

**Ready to merge?** Yes, subject to Supervisor-controlled local gates, PR, and hosted CI (not in this reviewer’s authority).

**Reasoning:** The slice externalises the three named literals, corrects unlike R3 measures, versions the methodology-backed 50× test, and proves boundaries without changing the two public or two simulated golden outcomes.

---

## Findings

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | REQUIRED REMEDIATION |
|---|---|---|---|---|---|
| — | — | — | — | No unresolved findings. | — |

Zero rows. Residual observations below are not findings and do not require a return to the Implementer.

---

## Cannot verify from files

Independent process execution in this reviewer turn (WSL shell returned no result):

- Direct `sha256sum` / `wc -c` of `config/thresholds.v1.yaml` from this seat. Cross-file consistency of the quoted digest `32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261` and 3700 bytes was checked among `authority_hashes.json`, Manifest §11, and `test_evidence.md`; the digest itself was not recomputed here.
- Re-execution of `pytest -q`, `make ci`, clean pip gates, `scripts/demo_smoke.py`, `scripts/verify_integrity.py`, `scripts/check_threshold_literals.py`, and Docker build. Counts in `test_evidence.md` (136 tests, 13 Python files / 23 numeric values, 58 focused tests, 116 tracked files) are internally consistent with the files; they are not a fresh run by this reviewer.
- That `scripts/build_manifests.py` ran **exactly once**. The resulting diffs are consistent with a single generation (`generated_on` 2026-09-02; thresholds hash/bytes only; snapshot `files[]` unchanged). Process invocation count is not independently countable from git objects.
- Hosted GitHub Actions on this branch (correctly unclaimed in `test_evidence.md`).
- Byte identity of the governing DOCX versus the searchable mirror. The mirror was used as a search aid per `AGENTS.md`; the DOCX remains authoritative.

`test_evidence.md` claims that are supported by diffs/files (not re-executed): planned-only YAML hunk; authority JSON limited to `generated_on` plus thresholds hash/bytes; snapshot manifest limited to `generated_on`; golden file unedited; validator/CI/Makefile wiring present; FR/KL/ADR status wording.

No `test_evidence.md` claim was found to contradict the current files or patches. Docker “image exported and tagged” is an extra local-build narrative; the Dockerfile/tag string is not a source-tree fact this reviewer could confirm.

---

## What was verified

### Methodology / strictness

- No existing threshold **value** in `config/thresholds.v1.yaml` changed. Added only `rules.R11.generic_capacity_export_import_value_ratio: 50`.
- R2: `>=` share and CAGR, strictly positive quantity. Steel fixture: ΔlnQ 0.5047, share 0.6579, YoY 287.9/173.8−1 ≈ 0.6565 → still fires. PP 67.0→56.0 quantity decline → still does not fire.
- R3: `HHI >= 0.25` or `largest_supplier_share >= 0.50`. Steel HHI 0.36, no `largest_supplier_share` → HHI path still fires. PP has no `supplier_metrics_2024` → R3 remains DISABLED.
- R11: strictly `>` configured 50. PP latest `export_import_value_ratio: 50.6` and `generic_capacity_reject: true` → still fires. Equality 50.00 does not fire (boundary tests).
- Competition: warning iff ratio `>` 1.25; `passes_default_warning = not warning_fires` ≡ prior `ratio <= 1.25`. Steel simulated ratio remains the golden `< 1.25` assertion (unedited `tests/test_golden_cases.py:31`).
- D\* steel gate: `<= incremental_upgrade_max` (0.40). D\* 0.2667 remains incremental. `publication_allowed` is the previous conjunction.
- R1-D: `span < window_years` for integer years ≡ prior `span <= window_years - 1`.

R11 rationale rewording (`thresholds.v1.yaml:82`): does **not** introduce a new executable policy claim. It restates Appendix B economic exclusion plus the already-coded §14.2 generic-capacity test, using Core 07 “warning” vocabulary. `sector_scope: all` documents pre-existing engine behaviour (the ratio test already ran whenever `generic_capacity_reject` was true). REJECT for PP remains `_public_decision` + context flag, not the rationale sentence.

### Behaviour equivalence (four goldens)

Predicate diff versus base (`s02_code.patch`) cannot change:

- Steel/public `INVESTIGATE` (R1-D, R2, R3, R4-D, R9-S fire; D\* unpublished)
- Steel/simulated `ADVANCE` route 5 (D\* 0.2667 ≤ 0.40; competition passes)
- PP/public `REJECT` route 0 (R2 false, R11 true at 50.6)
- PP/simulated `REJECT`

`tests/test_golden_cases.py` is absent from the code patch. Core 09 §8 anti-gaming is intact.

Intended R3 semantic change (do not treat top-two as largest-supplier) does not affect either public fixture.

### Authority chain

- Governed YAML hunk matches plan §10.2 (version, effective_date, new key, rationale sentence, R11 revision_date only).
- `authority_hashes.json`: only `generated_on` and the thresholds `sha256`/`bytes` change in `s02_governed.patch`. Other listed hashes, including `docs/core/**`, `sector_profiles.v1.yaml`, and `evidence_policy.v1.yaml`, are unchanged in that patch.
- Manifest §11 thresholds row equals the JSON entry (hash `32d868…d261`, bytes 3,700 / 3700).
- `snapshot_manifest.json`: only `generated_on` `2026-08-31` → `2026-09-02`; `files[]` hashes/bytes/paths unchanged in the patch.
- `s02_review_meta.txt` staged names do not include `docs/core/**`, `sector_profiles`, `evidence_policy`, snapshot payloads, or golden JSON.
- Regeneration is recorded after Task 5 conditions in `test_evidence.md` lines 156–172.

### Validator soundness

- Approved rule: `ast.walk` → `ast.Compare` → left and comparators that are numeric `ast.Constant`, value in YAML numeric set, excluding `{0,1,2,3}`.
- Formula non-hits confirmed by inspection: `state / 3` (BinOp), `0 <= state <= 3` (exempt), `* 1000` (BinOp), `rate <= -1` (−1 not configured), `high < 1024`, `range(250)` (Call, not Compare), `1e-9` (BinOp with Name), `support <= maximum + 1e-9` (BinOp).
- `ast.walk` does visit list comprehensions and lambdas; a Compare inside them would be flagged. There is no dedicated comprehension fixture; that is coverage polish, not a hole in `ast.walk`.
- Known non-hits **by design** (plan §9.1): `x <= 0.4 + 0.0` (BinOp), `x <= float("0.4")` (Call), `x <= LIMIT` after `LIMIT = 0.40` (Name). These are not implementation defects against the approved algorithm.
- `EXEMPT_NUMERIC_VALUES = {0,1,2,3}` is correct per the approved rule. Side effect: configured `economics.support_search_step_m_sar: 1.0` and R1 year-count `3` cannot be guarded as comparison literals. Accepted tradeoff; the defects this slice was required to catch (`0.40`, `1.25`, `50`) are in the banned set and not exempt.
- Scan is `src/ior_mvp/*.py` (13 top-level modules). There is no engine subpackage. Recursive `rglob` would currently yield the same set. Acceptable for this layout; not a present-tense defect.

### Test fidelity

- Boundary tests hit the exact below/equal/above values required (R2 0.5999/0.6000/0.6001; R3 HHI 0.2499/0.2500/0.2501; R3 largest 0.4999/0.5000/0.5001; R11 49.99/50.00/50.01; Kmin predicate 0.6999/0.7000/0.7001; bands at 0.20/0.40/0.65 with open/closed edges; competition 1.2499/1.2500/1.2501).
- Kmin integration uses frozen hashed `coated_steel` weights 0.65 / 0.70 / 0.75. Addition order follows YAML insertion order of selected keys. That is a theoretical float-order coupling to a hashed profile, not an assertion of a private helper. Implementer recorded the 0.70 case passed; PR-03 stop rule was not triggered.
- Deepcopy tests (`test_rules.py` R3 mutations) copy `get_public_case`’s `lru_cache` payload before write. `analyze_public` also `isolated_copy`s. Cache poisoning path is closed.
- `test_threshold_is_loaded_from_versioned_config` pinning `effective_date == "2026-09-02"` is not harmfully brittle: it identifies the approved 1.1.0 authority artifact (plan §11.3; Core 07 §9 allows tests to assert initial values). It fails only when that metadata changes, which is an authority event.
- Frontend caption test asserts the payload path rather than runtime rendering; that matches the approved static contract.

### Response contract / UI

- R3 metrics add `hhi_threshold`, `largest_supplier_share` (`"NOT_CALCULABLE"` when absent), `largest_supplier_threshold`. `top_two_share` retained.
- R11 metrics add `export_import_value_ratio_threshold`.
- Steel `competition` keeps `warning_threshold` (now config-sourced) and `passes_default_warning`; adds `warning_fires`.
- GenUI always sets `supplier_concentration` (R3 metrics, else `{}`) in both modes.
- PP: R3 DISABLED / `{}` metrics; `supplier_metrics` absent; `renderMetricGrid` takes the `hhi == null` branch and never calls `toFixed` on a missing threshold. Optional chaining covers `{}` and omitted props. No throw path on the PP case.

### Hygiene

- New public functions have type hints. No bare `except` in new or scanned engine code.
- No hidden default threshold in the new predicates (missing keys raise). R3 no longer uses `.get(..., 0)` as a fake HHI/share.
- No dead new code. Pre-existing unused `greenfield_likely_above` and unused R11 cost-premium evaluator are out of slice scope.

### Traceability honesty

- FR-002, FR-025, FR-033, FR-034, FR-044, INV-07, TL-03, TL-08, GATE-C are `IMPLEMENTED`, not `TESTED`/`COMPLETE`.
- TL-03 was narrowed from S01 `TESTED (partial)` to `IMPLEMENTED` because new S02 cases are not yet hosted-CI-tested. Conservative and honest.
- ADR-005 **Accepted 2026-09-02** names `rules.R11.generic_capacity_export_import_value_ratio`.
- KL-01..03 remain Open: implementation described, closure pending independent review, CI, and merge.

---

## Residual observations (not findings)

1. Validator will not catch BinOp/Call/Name aliases of configured numbers. That is the approved AST contract.
2. Exempting `{0,1,2,3}` also exempts configured `1.0` and `3`.
3. Top-level `glob("*.py")` should become recursive if a subpackage is added later.
4. No dedicated GenUI test for PP `supplier_concentration == {}`; the code path is safe.
5. R1-D `confidence_cap: "C"` remains a string in metrics/copy rather than a config read; plan forbade result-text changes.

---

## Al-muhasibi

Asked: independent review of S02 against methodology, plan, diffs, and current files; findings table; cannot-verify list; verdict.

Verified: file-level methodology fidelity, predicate equivalence for the four goldens, governed-diff scope, validator/test/CI/UI contracts, traceability honesty.

Assumed, not re-executed: local 136-test / smoke / integrity / Docker outputs recorded in `test_evidence.md`; Supervisor’s independent `sha256sum`.

No owner decision is missing for this review.

---

Verdict: APPROVE — zero unresolved findings
