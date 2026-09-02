# Supervisor Plan Review — S02 Threshold Governance

Reviewer: Supervisor (claude-fable-5-1-thinking-max). Planner: agent 3c1e305b (gpt-5.6-sol-max). Plan read in full (24 sections, ~2,010 lines).

## Verification performed by the Supervisor

- Traced the proposed AST rule against every `ast.Compare` in `src/ior_mvp/*.py` at base `432af8a`: hits are exactly `decision_engine.py` `ratio <= 1.25`, `d_star <= 0.40`, `rules.py` `export_import_ratio > 50`. Non-hits confirmed: `rate <= -1` (−1 not configured), `high < 1024`, `len(values) >= 6`, `0 <= state <= 3` / `== 3` / `>= 2` (exempt), BinOp/UnaryOp comparators (`maximum + 1e-9`, `-npv_tolerance`, `hurdle_rate - irr_tolerance`), `is not None/False/True` and string comparisons (skipped). Configured numeric set after the change = 23 unique values, matching the plan.
- Verified predicate equivalence with current behaviour: R1-D (`span < window` ≡ `span <= window-1`), R2 (positive-quantity flag read from config, identical result), R3 (HHI path unchanged; steel fires on 0.36), R11 (strictly greater, PP 50.6 fires; steel has no ratio → DEGRADED/False), competition (`passes = not (ratio > 1.25)` ≡ `ratio <= 1.25`), D\* gate (`<= incremental_upgrade_max`), `publication_allowed` (same conjunction). Golden values unaffected.
- Verified boundary matrices and the coated-steel Kmin sets (0.65 / 0.70 / 0.75) against `sector_profiles.v1.yaml`; the 0.70 set sums to the double for 0.7 under YAML insertion order.
- Verified the CI contract additions, GenUI prop, and `app.js` replacement have no numeric fallback.

## Round 1 findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| PR-01 | MEDIUM | Manifest §8 (hashes computed by the approved script over the reviewed file) | Plan §10.2, §15, §17 use a planner-predicted SHA-256 `32d868…d261` / 3,700 bytes as an acceptance constant and instruct "stop" on mismatch. | A predicted hash is fragile (line endings, trailing newline, transcription of the rationale sentence) and is not the authority; the authority is the script's output over the Supervisor-reviewed YAML. A spurious mismatch would stall the slice for a non-defect. | Reword: the predicted hash is advisory only. Acceptance becomes: (a) `git diff -- config/thresholds.v1.yaml` shows ONLY the planned lines (metadata `version`/`effective_date`; the R11 block); (b) `sha256sum config/thresholds.v1.yaml` equals the `authority_hashes.json` entry; (c) the §11 table row equals that JSON entry (hash and byte count copied from the JSON, not from the plan). Remove "stop on predicted-hash mismatch"; keep "stop if any YAML line outside the planned lines changed or if `snapshot_manifest.json` changes anything except `generated_on`". |
| PR-02 | LOW | Autonomous flow (owner mandate §1, §18) | Plan Task 5 last bullet: "obtain Supervisor confirmation before regeneration". | A mid-task pause would stall implementation waiting for a message the Implementer cannot receive. | Replace with the pre-authorisation recorded here: the Implementer may run `scripts/build_manifests.py` exactly once when all of (i) the YAML diff equals the planned lines, (ii) the threshold validator is clean, (iii) full pytest and demo smoke pass on 1.1.0, are observed and recorded. |
| PR-03 | LOW | Core 09 §8 (do not alter expectations to pass) | `test_evaluate_capability_integrates_kmin_with_profile_weights` 0.70 case depends on float accumulation order. | Supervisor arithmetic says it passes, but if it fails for precision reasons the Implementer must not "fix" the predicate or the expectation silently. | Add to Task 2: if only this case fails and the failure is a float-precision artefact (coverage prints 0.7 but compares below), stop, record the observed value, and report DONE_WITH_CONCERNS; do not change `publication_allowed`, Kmin, or the expected boolean. |

No BLOCKER or HIGH findings. Data classification "Internal" accepted (code + public evidence + synthetic fixtures; package labelled confidential demo).

## Round 2

Planner revised `plan.md` (same agent). Supervisor verified in text: PR-01 at lines 495–502, 1554, 1647–1652, 1821, 1847–1848 (advisory hash; `sha256sum` equality; JSON-sourced §11 row; stop conditions retained for unplanned YAML lines and snapshot-manifest changes); PR-02 at lines 1823, 1833 (pre-authorised single generator run after recorded gates); PR-03 at line 1755 (float-precision stop rule).

Unresolved findings: **0**.

## Decision

**PLAN_APPROVED** — 2026-09-02, Supervisor. Implementation may begin on `slice/S02-threshold-governance` from base `432af8af1fa88a2258a0fd8d825a6855e408270f`, executing plan Tasks 0–7 and the Task 9 detached local validation as pre-review evidence. The single `scripts/build_manifests.py` run is pre-authorised under the Task 5 conditions. Commit/push/PR/merge remain Supervisor-controlled. The authority-change justification in plan §16 is adopted verbatim for the PR description.
