# Known Limitations

Updated by the Supervisor at every slice completion. Items marked *pre-existing* were present in the v0.1.0 package before this build.

## Open (to be closed by a roadmap slice)

| ID | Limitation | Source of requirement | Closing slice |
|---|---|---|---|

## Closed by completion slices

| ID | Limitation | Resolution | Evidence | Closure |
|---|---|---|---|---|
| KL-01 | Threshold literals `0.40`, `1.25`, `50` embedded in engine code (*pre-existing*). | Config-sourced predicates (`rules.py`, `decision_engine.py`), thresholds 1.1.0 R11 key, `scripts/check_threshold_literals.py` guard in CI and `make ci`. | `.workflow/slices/S02-threshold-governance/test_evidence.md`; CI run 33573669072 on PR #2 — 4/4 pass. | Squash merge of S02 (PR #2, `c438370`). |
| KL-02 | R3 compared `top_two_value_share` with the largest-supplier threshold (*pre-existing*). | `rules.r3_fires` uses `largest_supplier_share` only; absent → `NOT_CALCULABLE` in metrics. | Same evidence as KL-01; `test_r3_does_not_substitute_top_two_share_for_largest_supplier`. | Squash merge of S02 (PR #2, `c438370`). |
| KL-03 | No threshold boundary tests (*pre-existing*). | `tests/test_threshold_boundaries.py` (R1-D, R2, R3, R11, Kmin, D\* bands, competition; below/equal/above). | Same evidence as KL-01. | Squash merge of S02 (PR #2, `c438370`). |
| KL-04 | Evidence policy did not require `display_label`; a scenario missing it raised `KeyError` (*pre-existing*). | `evidence_policy.v1.yaml` 1.1.0 requires all Core 06 §4 fields plus class/source/label; `validate_synthetic_scenario` raises typed `EvidenceIntegrityError`; repository loader delegates. | `.workflow/slices/S03-evidence-isolation-hardening/test_evidence.md`; CI run 33579923763 on PR #3 — 4/4 pass. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-05 | No validator reconciled synthetic scenarios to public marginals (*pre-existing*). | `evidence.reconcile_synthetic_scenario` (demand, nameplate, factors, qualified availability; INFORMATIONAL demand layers; NOT_APPLICABLE allocation) blocks simulation on FAIL; `scripts/validate_scenarios.py` Gate B in CI and `make ci`. | Same evidence as KL-04; Gate B `SCENARIO VALIDATION PASS (2 scenarios)`. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-06 | Analysis response did not expose methodology/config versions per case (*pre-existing*). | `config.authority_summary` in every analysis, banner and dossier (FR-001). | Same evidence as KL-04; `tests/test_authority_disclosure.py`. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-07 | Simulated ledger repeated the public R6/R7/R8 `DISABLED` rows instead of re-evaluating with labelled synthetic inputs (*pre-existing*). | `rules.evaluate_simulated_rules` appends Class-D labelled R6/R7/R8 rows in simulated mode (FULL/DEGRADED/DISABLED with `NOT_CALCULABLE` metrics); public ledger carries none; UI and dossier disclose them. | `.workflow/slices/S04-simulation-fidelity/test_evidence.md`; CI run 33584437086 on PR #4 — 4/4 pass. | Squash merge of S04 (PR #4, `98c1a40`). |
| KL-08 | Steel/PP branch dispatch and decision narrative hard-coded in engine code; scenarios carried no ground truth (*pre-existing*). | Generic `_simulate` (Core 07 §7.4 → §7.3 → INVESTIGATE); scenarios 1.1.0 carry `ground_truth` and `decision_narrative`; runtime and Gate B back-test fail closed. | Same evidence as KL-07; Gate B back-tests PASS for both scenarios. | Squash merge of S04 (PR #4, `98c1a40`). |
| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*). | `.github/workflows/ci.yml` (uv 3.12/3.14, pip 3.12, Docker build) running scan → compile → node → integrity → pytest → smoke; local `make ci`. | `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`; CI run 33569855956 on PR #1 — all four jobs pass. | Effective on squash merge of S01 (PR #1). |

## Accepted for this MVP (recorded, not scheduled)

| ID | Limitation | Rationale |
|---|---|---|
| KL-20 | `sector_profiles.v1.yaml` implements 2 of the 5 methodology §6.3 profiles. | Only two golden cases exist; adding profiles without cases would be untested configuration. |
| KL-21 | `styles.css` contains pre-existing hard-coded hex colours outside `:root` tokens and `app.js` remains a single module of about 450 lines. | S05 does not edit the frontend. Full tokenisation and module decomposition are post-acceptance polish and cannot justify domain/release drift. |
| KL-22 | No Playwright or real-browser interaction/visual test is part of final acceptance. Gate G/TL-07 proof is live HTTP/API payload plus static HTML/CSS/JavaScript contract: case/mode controls, dual states, approved manifest, dossier action/HTML, responsive media rules, semantic native controls, RTL markup, disclosure, and offline assets. | Core 09 §2.7 defines static checks as the MVP minimum and browser tests as a production addition. S05 does not claim painted layout, actual keyboard traversal, print rendering, or browser console behavior. |
| KL-23 | `MONITOR` is supported by the contract but is not produced by either packaged golden case. | Core 02 §5 records this explicitly; inventing a third case or route trigger is outside the frozen evidence. |
| KL-24 | The public branch does not reach the complete-route-sequence else branch of Core 07 §7.1 because both fixtures stop at `REJECT`/`INVESTIGATE`. | Implementing untested public route selection without evidence would invent behavior. |
| KL-25 | R8 simulation is explicitly `DISABLED`/`NOT_CALCULABLE`: packaged scenarios disclose committed and announced layers but contain no governed base-demand, commitment-probability, or minimum-efficient-scale field. | Values are absent from authority; raw layers remain separate and cannot fire R8. |
| KL-26 | R5 retained-import share cannot be calculated because frozen public snapshots contain neither domestic-production quantity nor retained-import flow. | The engine exposes `NOT_CALCULABLE`, its reason, and the configured threshold. Gross imports are not coerced into apparent consumption. |
| KL-27 | No expansion-assumption bypass exists; the disclosed-public-nameplate ceiling applies to packaged scenarios. | Core 06 §5.1 names an exception but supplies no governed schema. A future scenario requiring it needs an authority decision. |
| KL-28 | Synthetic scenarios contain no tariff-line or buyer-allocation blocks; reconciliation reports `NOT_APPLICABLE`. | Core 06 §5.1 and Core 05 §8 require reconciliation when compatible blocks exist but do not define a current JSON schema. |
| KL-29 | Successful config, public, synthetic, and golden loads are process-local `lru_cache` values. An approved on-disk correction is not observed until process restart or explicit internal cache clear. | The MVP uses immutable hashed local files and no write endpoint. The operator runbook requires restart after an approved artifact change; startup/restart is acceptance-tested. |
| KL-30 | R1-D metrics emit `confidence_cap: "C"` as a stable result string rather than reading `rules.R1_D.confidence_cap` into that output field. | The emitted value equals frozen configuration 1.1.0 and no decision threshold is hidden. S02 preserved result text; the limitation is recorded rather than disguised. |
