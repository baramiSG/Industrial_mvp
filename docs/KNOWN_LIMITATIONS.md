# Known Limitations

Updated by the Supervisor at every slice completion. Items marked *pre-existing* were present in the v0.1.0 package before this build.

## Open (to be closed by a roadmap slice)

| ID | Limitation | Source of requirement | Closing slice |
|---|---|---|---|
| KL-04 | S03 policy 1.1.0 requires all Core 06 §4 fields and exact class/source/label, with violations typed as `EvidenceIntegrityError`; this remains open until the reviewed S03 squash merge and green current-head CI make the resolution effective. | Core 06 §4 | S03 |
| KL-05 | S03 adds one evidence-guard reconciliation report plus a repository Gate B validator with planted-failure proof; this remains open until the reviewed S03 squash merge and green current-head CI make the resolution effective. | Core 06 §5.1, §10.2; Core 09 Gate B | S03 |
| KL-06 | S03 exposes source-derived authority metadata in detailed analysis, the GenUI banner, dossier JSON and printable HTML; this remains open until the reviewed S03 squash merge and green current-head CI make the resolution effective. | FR-001 | S03 |
| KL-07 | Simulated ledger repeats the public R6/R7/R8 `DISABLED` rows rather than re-evaluating with labelled synthetic inputs (*pre-existing*). | Core 02 §3 | S04 |
| KL-08 | Steel conditions/kill conditions and the steel/PP branch dispatch are hard-coded in engine code; scenarios carry no explicit ground truth (*pre-existing*). | Core 06 §5.3, §10.4–10.5; Core 07 §7.3–7.4 | S04 |

## Closed by completion slices

| ID | Limitation | Resolution | Evidence | Closure |
|---|---|---|---|---|
| KL-01 | Threshold literals `0.40`, `1.25`, `50` embedded in engine code (*pre-existing*). | Config-sourced predicates (`rules.py`, `decision_engine.py`), thresholds 1.1.0 R11 key, `scripts/check_threshold_literals.py` guard in CI and `make ci`. | `.workflow/slices/S02-threshold-governance/test_evidence.md`; CI run 33573669072 on PR #2 — 4/4 pass. | Squash merge of S02 (PR #2, `c438370`). |
| KL-02 | R3 compared `top_two_value_share` with the largest-supplier threshold (*pre-existing*). | `rules.r3_fires` uses `largest_supplier_share` only; absent → `NOT_CALCULABLE` in metrics. | Same evidence as KL-01; `test_r3_does_not_substitute_top_two_share_for_largest_supplier`. | Squash merge of S02 (PR #2, `c438370`). |
| KL-03 | No threshold boundary tests (*pre-existing*). | `tests/test_threshold_boundaries.py` (R1-D, R2, R3, R11, Kmin, D\* bands, competition; below/equal/above). | Same evidence as KL-01. | Squash merge of S02 (PR #2, `c438370`). |
| KL-09 | No CI workflow; proof commands run manually only (*pre-existing*). | `.github/workflows/ci.yml` (uv 3.12/3.14, pip 3.12, Docker build) running scan → compile → node → integrity → pytest → smoke; local `make ci`. | `.workflow/slices/S01-ci-and-toolchain/test_evidence.md`; CI run 33569855956 on PR #1 — all four jobs pass. | Effective on squash merge of S01 (PR #1). |

## Accepted for this MVP (recorded, not scheduled)

| ID | Limitation | Rationale |
|---|---|---|
| KL-20 | `sector_profiles.v1.yaml` implements 2 of the 5 methodology §6.3 profiles. | Only two golden cases exist; adding profiles without cases would be untested configuration. |
| KL-21 | `styles.css` contains hard-coded hex colours outside `:root` tokens and `app.js` is a single ~450-line module. | Pre-existing demo frontend; SG-TR-008 applies to edited CSS/TSX. New CSS in this build uses tokens only. Full tokenisation is a post-acceptance polish item. |
| KL-22 | No Playwright/browser tests; frontend proof is static contract tests plus manual rendering. | Core 09 §2.7 calls browser tests a production addition. |
| KL-23 | `MONITOR` state is supported by the contract but never produced by the current golden cases. | Core 02 §5 records this explicitly. |
| KL-24 | Public branch never reaches the "evaluate complete route sequence" else-branch of Core 07 §7.1 because both fixtures stop at REJECT/INVESTIGATE. | Implementing an untested route sequence on absent public data would invent behaviour. |
| KL-25 | R8 in simulation cannot fire because scenarios carry no base-demand or minimum-efficient-scale field. | Values absent from authority; recorded as NOT_CALCULABLE rather than invented. |
| KL-26 | R5 retained-import share remains unavailable because the frozen public snapshots contain no domestic-production quantity or retained-import flow. | S03 emits explicit `NOT_CALCULABLE`, the reason and configured threshold; effective closure of the transparency defect remains pending reviewed merge and green current-head CI. |
| KL-27 | No expansion-assumption bypass is implemented; the disclosed-public-nameplate ceiling applies to every packaged scenario. | Core 06 §5.1 names an exception but defines no governed schema; defer the schema until a future scenario needs it. |
| KL-28 | Synthetic scenarios contain no tariff-line or buyer allocation blocks; reconciliation reports `NOT_APPLICABLE` for that check. | Core 06 §5.1 and Core 05 §8 require reconciliation when compatible blocks exist but define no current schema; defer the schema until a future scenario needs it. |
