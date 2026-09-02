# Known Limitations

Updated by the Supervisor at every slice completion. Items marked *pre-existing* were present in the v0.1.0 package before this build.

## Open (to be closed by a roadmap slice)

| ID | Limitation | Source of requirement | Closing slice |
|---|---|---|---|
| KL-07 | S04 re-evaluates R6/R7/R8 as separately labelled synthetic rows while preserving the public ledger; resolution remains pending reviewed merge and green current-head CI. | Core 02 §3 | S04 |
| KL-08 | S04 replaces opportunity-ID dispatch with generic scenario-driven selection, moves narrative to versioned scenarios, and adds planted-ground-truth back-testing; resolution remains pending reviewed merge and green current-head CI. | Core 06 §5.3, §10.4–10.5; Core 07 §7.3–7.4 | S04 |

## Closed by completion slices

| ID | Limitation | Resolution | Evidence | Closure |
|---|---|---|---|---|
| KL-01 | Threshold literals `0.40`, `1.25`, `50` embedded in engine code (*pre-existing*). | Config-sourced predicates (`rules.py`, `decision_engine.py`), thresholds 1.1.0 R11 key, `scripts/check_threshold_literals.py` guard in CI and `make ci`. | `.workflow/slices/S02-threshold-governance/test_evidence.md`; CI run 33573669072 on PR #2 — 4/4 pass. | Squash merge of S02 (PR #2, `c438370`). |
| KL-02 | R3 compared `top_two_value_share` with the largest-supplier threshold (*pre-existing*). | `rules.r3_fires` uses `largest_supplier_share` only; absent → `NOT_CALCULABLE` in metrics. | Same evidence as KL-01; `test_r3_does_not_substitute_top_two_share_for_largest_supplier`. | Squash merge of S02 (PR #2, `c438370`). |
| KL-03 | No threshold boundary tests (*pre-existing*). | `tests/test_threshold_boundaries.py` (R1-D, R2, R3, R11, Kmin, D\* bands, competition; below/equal/above). | Same evidence as KL-01. | Squash merge of S02 (PR #2, `c438370`). |
| KL-04 | Evidence policy did not require `display_label`; a scenario missing it raised `KeyError` (*pre-existing*). | `evidence_policy.v1.yaml` 1.1.0 requires all Core 06 §4 fields plus class/source/label; `validate_synthetic_scenario` raises typed `EvidenceIntegrityError`; repository loader delegates. | `.workflow/slices/S03-evidence-isolation-hardening/test_evidence.md`; CI run 33579923763 on PR #3 — 4/4 pass. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-05 | No validator reconciled synthetic scenarios to public marginals (*pre-existing*). | `evidence.reconcile_synthetic_scenario` (demand, nameplate, factors, qualified availability; INFORMATIONAL demand layers; NOT_APPLICABLE allocation) blocks simulation on FAIL; `scripts/validate_scenarios.py` Gate B in CI and `make ci`. | Same evidence as KL-04; Gate B `SCENARIO VALIDATION PASS (2 scenarios)`. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-06 | Analysis response did not expose methodology/config versions per case (*pre-existing*). | `config.authority_summary` in every analysis, banner and dossier (FR-001). | Same evidence as KL-04; `tests/test_authority_disclosure.py`. | Squash merge of S03 (PR #3, `ddf905d`). |
| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*). | `.github/workflows/ci.yml` (uv 3.12/3.14, pip 3.12, Docker build) running scan → compile → node → integrity → pytest → smoke; local `make ci`. | `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`; CI run 33569855956 on PR #1 — all four jobs pass. | Effective on squash merge of S01 (PR #1). |

## Accepted for this MVP (recorded, not scheduled)

| ID | Limitation | Rationale |
|---|---|---|
| KL-20 | `sector_profiles.v1.yaml` implements 2 of the 5 methodology §6.3 profiles. | Only two golden cases exist; adding profiles without cases would be untested configuration. |
| KL-21 | `styles.css` contains hard-coded hex colours outside `:root` tokens and `app.js` is a single ~450-line module. | Pre-existing demo frontend; SG-TR-008 applies to edited CSS/TSX. New CSS in this build uses tokens only. Full tokenisation is a post-acceptance polish item. |
| KL-22 | No Playwright/browser tests; frontend proof is static contract tests plus manual rendering. | Core 09 §2.7 calls browser tests a production addition. |
| KL-23 | `MONITOR` state is supported by the contract but never produced by the current golden cases. | Core 02 §5 records this explicitly. |
| KL-24 | Public branch never reaches the "evaluate complete route sequence" else-branch of Core 07 §7.1 because both fixtures stop at REJECT/INVESTIGATE. | Implementing an untested route sequence on absent public data would invent behaviour. |
| KL-25 | R8 simulation is explicitly `DISABLED`/`NOT_CALCULABLE`: packaged scenarios disclose committed and announced layers but contain no governed base-demand, commitment-probability or minimum-efficient-scale field. The engine does not invent those inputs. | Values are absent from authority; raw layers remain separate and cannot fire R8. |
| KL-26 | R5 retained-import share remains unavailable because the frozen public snapshots contain no domestic-production quantity or retained-import flow. | S03 emits explicit `NOT_CALCULABLE`, the reason and configured threshold; effective closure of the transparency defect remains pending reviewed merge and green current-head CI. |
| KL-27 | No expansion-assumption bypass is implemented; the disclosed-public-nameplate ceiling applies to every packaged scenario. | Core 06 §5.1 names an exception but defines no governed schema; defer the schema until a future scenario needs it. |
| KL-28 | Synthetic scenarios contain no tariff-line or buyer allocation blocks; reconciliation reports `NOT_APPLICABLE` for that check. | Core 06 §5.1 and Core 05 §8 require reconciliation when compatible blocks exist but define no current schema; defer the schema until a future scenario needs it. |
