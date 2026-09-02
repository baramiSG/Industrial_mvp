# Known Limitations

Updated by the Supervisor at every slice completion. Items marked *pre-existing* were present in the v0.1.0 package before this build.

## Open (to be closed by a roadmap slice)

| ID | Limitation | Source of requirement | Closing slice |
|---|---|---|---|
| KL-01 | S02 implementation removes the pre-existing threshold literals and adds an AST guard; closure remains pending independent review, CI and merge. | AGENTS.md #7; Core 07 §9 | S02 |
| KL-02 | S02 implementation compares like-for-like R3 measures and reports missing largest-supplier share as `NOT_CALCULABLE`; closure remains pending independent review, CI and merge. | Methodology §4 R3 | S02 |
| KL-03 | S02 implementation adds below/equal/above threshold tests; closure remains pending independent review, CI and merge. | Core 09 §3 | S02 |
| KL-04 | `evidence_policy.v1.yaml` does not list `display_label` as required; a scenario missing it raises `KeyError`, not `EvidenceIntegrityError` (*pre-existing*). | Core 06 §4 | S03 |
| KL-05 | No validator reconciles synthetic scenarios to public marginals (*pre-existing*). | Core 06 §5.1, §10.2; Core 09 Gate B | S03 |
| KL-06 | Analysis response does not expose methodology/config versions per case (*pre-existing*). | FR-001 | S03 |
| KL-07 | Simulated ledger repeats the public R6/R7/R8 `DISABLED` rows rather than re-evaluating with labelled synthetic inputs (*pre-existing*). | Core 02 §3 | S04 |
| KL-08 | Steel conditions/kill conditions and the steel/PP branch dispatch are hard-coded in engine code; scenarios carry no explicit ground truth (*pre-existing*). | Core 06 §5.3, §10.4–10.5; Core 07 §7.3–7.4 | S04 |

## Closed by completion slices

| ID | Limitation | Resolution | Evidence | Closure |
|---|---|---|---|---|
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
| KL-26 | R5 threshold (retained import share of apparent consumption) is not calculable from public data (no domestic production series). | Recorded as NOT_CALCULABLE in the ledger from S03. |
