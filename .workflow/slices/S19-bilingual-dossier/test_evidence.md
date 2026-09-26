# S19 test evidence

Historical development logs remain in [implementation-log.md](implementation-log.md). This file records the exact-tree gates for implementation tree `7c25b4616679d61f173f3d9072e3240e1a2a166b` after they completed. It does not embed this additive record's own Git tree.

The complete source-to-published inventory is [SOURCE-TO-PUBLISHED-BRIDGE.json](delivery-evidence/replacement-20260925/proof/post-merge-s19/SOURCE-TO-PUBLISHED-BRIDGE.json): 74 original-byte copies and 3 sanitized derivatives. Paths below are relative to `delivery-evidence/replacement-20260925/proof/post-merge-s19/`.

## Accepted local gates on tree 7c25

| Gate | Published receipt | SHA-256 | Result |
|---|---|---|---|
| Freeze / 3,307-path inventory | `subject/CANDIDATE-FREEZE.json` / `subject/FINAL-SOURCE-INVENTORY.json` | `80c60cab802b6c851c2cfa5a7d18056e3564abedc4c3e6a6c65fc80bce32e20f` / `f906a444da17be277755c8e403a4599db8d862a8db84f5799aa31d7469adbacb` | Proof commit `29bf5db55adaa57de2fa1f78aa5c9a028f31dc75`, tree `7c25` |
| Offline Task 6 | `gates/offline/RESULTS.json` | `1f2be1cf0be7bcc493bffe15e29b977e0bf26c1158385331690005e1b54db53f` | 14 commands exit 0; 3,982 passed in 122.86s |
| Compare-only e2e | `gates/e2e/RESULT.json` | `0d186b929ce5b1b0dedf7d10bbc731e2752a5d50b39994396d9d0dc946bcd95f` | 839 functional, 2,291.70s; 4 visual, 235.30s |
| Predecessor R1 | `gates/r1/COMPARISON.json` | `9c74e0dfbd6b3692ac7b74c1a7db420fd8ea237bea8a6d395b2741740a6cdbc3` | Pass, engine `a1dcbf0e7665` to `6b54371e99f3` |
| CI1 `make ci` | `gates/ci1/ci1-result.json` | `f3777dbc8e318b69fda73f86284f2a4c3150cc050030e417f7da4ed191a86bb2` | Exit 0, 15:49:51–16:36:27, 2,795.827s |
| CI1 own 44-PDF proof | `gates/ci1-pdf/FULL44-READINESS.json` | `f00426b2d7e4c43fd0ae36f8c4e498c2c7c34da7ebe08f3e165b69976525658f` | 44 PDFs, 1,958 pages; 44 fresh first pages, 3 fresh appendix fallbacks, 1,911 attributed reuses |
| Replacement CI2 root3 | `gates/ci2/ci2-result.json` | `6c049030da1034a12640199f50b23f4f9c0f237fea8527658edfe542102c6a38` | Exit 0, 17:43:48–18:27:14, 2,605.717s |
| CI2 own 44-PDF proof | `gates/ci2-pdf/FULL44-READINESS.json` | `9d0fbea00f8589053eda36e18c4fb00ea0d35c7e2d53c857eec4db93f5eda3fa` | Same page accounting as CI1, recomputed on root3 bytes |
| Restored local graph | `gates/ci2/RESTORED-GRAPH.json` | `8156d58b8d931aff78954a7b40c322fe910203d843b5fe4126a049828469f76d` | Same-ID container restored healthy at 18:27:26. This is local Neo4j, not Aura |

Claude review `8855010a043ad83c8d150ae6a1d17b445cf346c9af198ac1ed8c6c7d40cbc745` accepted the e2e and R1 operations. Claude implementation closure `50f33c00593f2cfc756bb5d7284a52b04f8dbc2dbe861807c0d0e30c01943f24` accepted the exact-tree set, including byte identity of each root's 1,958 rendered pages with the pre-freeze cohort. Coverage is 44 fresh first pages plus 1,914 retained appendix observations in each root, not 1,958 fresh native inspections.

## Failures retained

| Subject | Published receipt | SHA-256 | Disposition |
|---|---|---|---|
| Interrupted original root2 | `gates/interruption/INCIDENT.json` | `b39acec2b375d385f3e6b03178a48b86faf8a101a33fc63e13a2b61c9f047bfc` | Incomplete. No exit result. Restart cause unknown |
| Recovery closure | `gates/interruption/RECOVERY-CLOSURE.json` | `d22e8c8152e7417ee04b4f6af14dc184c44f0ed1f0e0560d13df366dc9021016` | Recovery of the retained service. Not a CI2 pass and not Aura |
| Interrupted attempt hashes | `gates/interruption/INTERRUPTED-ATTEMPT1-HASHES.json` | `836d0761207c4a263b013ded608f97e21018032c819f29fecb6d88e3c44d778a` | 33-file inventory of the incomplete attempt |

Candidate tree `c746de8510fcc4da0557cd0be4a47fc42fd0aa7d` remains a failed full offline gate: 3,981 passed and one static-font failure. The later test-only correction was reviewed separately. That failure is not restated as a pass.

## Hosted proof of the same tree

PR head `39614fcdd8d8eb9a96381c3d1b806343d5164419`, run `36175983021`, attempt 1: all six jobs success. Receipt `hosted-pr/HOSTED-RESULT.json` is `8df202a283e50bfc8ac70384a37a0ec1acb484a2eb38bff8fdeadcade225ade0`. Browser job: 839 functional in 3,422.78s and 4 visual in 352.04s. Python jobs: 3,982 passed. Graph load 925/1,045, then 0/0, equality, and fail-closed. The single `AURA_OPERATOR_ONLY` skip is the live-Aura operator test and is not Aura proof.

Main commit `6962105b4bee575a6271d08fe892144c6e6c1063`, run `36183985706`, attempt 1, event `push`: all six jobs success. Receipt `hosted-main/HOSTED-RESULT.json` is `c13eec3a4938c1112771746de5af9092a4d36649f37706c6bf830e73e8ec5f52`. Browser job: 839 functional in 3,502.53s and 4 visual in 355.77s; job duration 65m2s. `hosted-main/MAIN-READBACK.json` (`0b114f3ed87138719002698f316a1ef20811a1d57fd40b42de298e7dc0a3f156`) shows remote `main` and tree `7c25`.

## Sanitized derivatives

Three published files are not original bytes. The public workflow sets `NEO4J_PASSWORD` to `ci-${{ github.run_id }}-${{ github.run_attempt }}-pw`. Exact occurrences of that run-scoped value were replaced with `[REDACTED_CI_CREDENTIAL]`.

| Published path | Original SHA-256 | Published SHA-256 | Replacements |
|---|---|---|---:|
| `hosted-pr/jobs/job-108206570262.txt` | `34cb5215ea0b905510607f92e38297db381fd5ae8947cf03d11ba20a6553eb72` | `b53acae92ce6ce1f74cb1d3e7d74fb9c48ef033af0aa8574a21964df5d25df56` | 14 |
| `hosted-main/jobs/job-108232845414.txt` | `42e5a5044d4af808e226e98cbff563c6e5efcd70235dac471df484e866089226` | `72e819a817be0fda6fe6bc5715fd4d622e1915702f1bbce37fcc0febb9516279` | 14 |
| `hosted-main/SIX-JOB-LOGS.json` | `4633271781b7bba113686276db9d8000f1ad44d3f9c8324a138031de1c8da0c8` | `47e06051b74d25a781af9ff351678820fb0a8ab97ee605bb17bfc91b4361336b` | 13 |

`log_sha256` inside the published main summary, and `sha256` inside the original-byte PR summary, still name the raw logs. The published graph-log hashes above are the derivative bytes. Raw originals remain outside Git. This file does not approve the derivatives; independent review of this record is pending.

## Accepted Aura result on the delivered subject — 2026-09-26

The product gates above were not rerun for this records append. They remain the accepted receipts for tree `7c25`. The Aura rows below are the separate post-delivery checkpoint. Paths are relative to `delivery-evidence/replacement-20260925/proof/post-merge-s19/aura/`.

| Evidence | Published path | SHA-256 | Result |
|---|---|---|---|
| Execution receipt | `continuation-2/RESULT.json` | `ea8aea20fd8b66620adaabf869c0763247d5d8a38ae9195a61929a6e98fbb421` | Historical status `EXECUTED_PENDING_INDEPENDENT_RESULT_REVIEW`; `database_writes` 0; semantic API and fixed-88 reused |
| Application proof | `continuation-2/application-proof.json` | `f4f0e725c84dcbdd3e3a053a8eb528ff3765c0c3926e569275005e05917af983` | Three fresh API stages plus one semantic reuse; both 44-journey matrices; 11 equal real-decision hashes |
| Process exit | `continuation-2/execution/EXIT.json` | `bb2c810d26a5fd1a0c59531e8e956806166508a6104646992db3d8226da3e036` | Exit 0, 01:59:04–03:03:28Z, 3863.884s |
| Cleanup | `continuation-2/execution/FINAL-HOST-CLEANUP.json` | `d6ad35901812f7dafb817a12c810ef715567d21c0d82a3afcf75618ca5dd8303` | 0 signals; lock 34210 preserved; no owned survivors |
| Claude result review | `reviews/s19-aura-result-review.md` | `c412150d99c92c6f0e5b42cac1d215f90afb2bd02625bc89a9751fdbd9e96dfa` | APPROVE this exact result |
| Delegated acceptance | `authority/s19-aura-result-delegated-acceptance.json` | `a59e702c4658c15708544373bbbc2c5c390fa2ab708bb151fa46d6807db30e8a` | Accepts the Aura result, not this records candidate |
| External bundle index | `FULL-EXTERNAL-BUNDLE-INDEX.json` | `c7ced65edb40b03d636d7e4c630a83701841cad3ceecaff04b65bf5bbd1ea083` | 479 files, including 448 PNGs not all published |

Fourteen representative images, 8,480,405 bytes, are under `images/`. The map is [AURA-SOURCE-COPY-MAP.json](delivery-evidence/replacement-20260925/proof/post-merge-s19/aura/AURA-SOURCE-COPY-MAP.json): 65 exact copies, zero Aura sanitizations. The earlier 74/3 post-merge bridge is unchanged.

**L1.** This record does not claim live browser verification of Class-D labels on a synthetic passport. All selected current-case browser passports were public, including simulated journeys. The published proof has 392 selected passports with `synthetic_flag` false. Class-D graph-element EN/AR labels were asserted by the restored API and sampled in images; public isolation was checked. The synthetic-passport branch did not run live.

Attempt 4 remains FAILED. Attempts 1–3 remain `FAILED_RECOVERED_OLD`. Readonly-execution-1 remains interrupted, with 35 partial EN images and no completed result. The injected connection failure is not an Aura outage. Session-expiry and run-1 causes remain unknown. This section does not approve the records candidate.
