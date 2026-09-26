# S19 post-delivery Aura evidence

Status on 2026-09-26: the Aura result for the delivered subject is independently approved and separately accepted. This page assembles the durable subset of that result. It does not approve this records candidate, and it does not embed this candidate's Git tree.

Historical sentences elsewhere in the S19 record that leave Aura open are the 2026-09-25 checkpoints. They stay as written. The current Aura-result status is this page. Review and delivery of this additive record remain pending.

## Subject

| Fact | Value |
|---|---|
| Main | `6962105b4bee575a6271d08fe892144c6e6c1063` |
| Implementation tree | `7c25b4616679d61f173f3d9072e3240e1a2a166b` |
| Instance and database | `8a7338e0` |
| Display name | Industrial_mvp |
| Projection | `GRAPH-SAU-2026-09-12-6f43b1a8c4aa` |
| Full inventory hash | `9b5cf8f9aa4db3849587da7a138f5e41e5d46cc4ea0e4df8fea62e92ba089429` |
| Application proof | `f4f0e725c84dcbdd3e3a053a8eb528ff3765c0c3926e569275005e05917af983` |
| Execution receipt | `ea8aea20fd8b66620adaabf869c0763247d5d8a38ae9195a61929a6e98fbb421` |
| External 479-file index | `c7ced65edb40b03d636d7e4c630a83701841cad3ceecaff04b65bf5bbd1ea083` |

The application proof records 925 nodes, 1,045 edges, 410 public nodes and 515 synthetic nodes on the fresh AVAILABLE status. The full property inventory stays external under that 479-file index. This assembly did not open Aura.

## Current acceptance

`continuation-2/RESULT.json` still says `EXECUTED_PENDING_INDEPENDENT_RESULT_REVIEW`. That sentence belongs to the receipt's own time. Actual Claude result review `reviews/s19-aura-result-review.md` (`c412150d99c92c6f0e5b42cac1d215f90afb2bd02625bc89a9751fdbd9e96dfa`) approves this exact result. Separate delegated acceptance `authority/s19-aura-result-delegated-acceptance.json` (`a59e702c4658c15708544373bbbc2c5c390fa2ab708bb151fa46d6807db30e8a`) accepts the checkpoint and permits this records assembly. Neither act accepts this records candidate or authorizes the next implementation slice.

## Required attribution

- Attempt 4 stock clear, load, reload, verify and operator receipts are reused on the freshly equal NEW subject. Attempt 4 remains FAILED. Recovery was blocked and nothing was cleared. Those receipts are under `reused/attempt4-stock/` and `failures/attempt4-FAILURE.json` / `failures/attempt4-RECOVERY-BLOCKED.json`.
- Fixed-88 is reused from attempt 2. `continuation-2/REUSED-RECEIPTS.json` sets `new_queries_claimed` to 0. The reused file `reused/attempt2-fixed-views.json` is a list of 88. No new fixed-view query is claimed.
- The initial AVAILABLE semantic API, 88 views, two portfolios and 11 decisions, is reused from attempt 3 after the fresh equality and status gates. The published attempt 3 proof is the whole file, including its later browser failure. Attempt 3 remains `FAILED_RECOVERED_OLD`.
- Three fresh API stages plus one semantic reuse. `continuation-2/execution/stdout.log` records, in order, `available completed`, `not_configured completed`, `injected_network_unavailability completed`, and `restored_available completed`. The initial 44 and restored 44 bilingual journeys are distinct stage runs in that sequence. Their stored journey arrays in `continuation-2/application-proof.json` are content-equal. Both fault states have 88 API views, two portfolios and two locales. All 11 real-decision hashes in the initial AVAILABLE API and the restored AVAILABLE API are equal, and each of those 11 decisions records `real_decision_equal` true. Polypropylene `SAU-H0-390210` is REJECT. The other ten are INVESTIGATE.
- The graph was restored after the fault. It was not continuously available. The connection-failure stage was a process-local injected fault, not an Aura outage. The earlier Aura session-expiry cause and the readonly-execution-1 interruption cause remain unknown.

The restored API progress file is byte-identical to attempt 3's available API progress file, SHA-256 `4d1dade077379063b0d0bed1d54a98dba9bd70f07a1144d7d9517a40b4fb36be`. That equality matches the reused semantic payloads. It is not a claim that the restored stage was omitted. Stdout still records a separate `restored_available completed` line.

## What this assembly parsed

From `continuation-2/application-proof.json` and the three fresh `api-progress.json` files:

| Stage | API views | Portfolios | Decisions | Browser |
|---|---:|---:|---:|---|
| Initial AVAILABLE, semantic reuse | 88 unique keys, all pass, HTTP 200 | 2 | 11, all `real_decision_equal` | 44 journeys, 11 cases × 2 modes × 2 locales, 4 views each, errors empty |
| NOT_CONFIGURED | 88, `GRAPH_UNAVAILABLE` / `NOT_CONFIGURED`, 0 nodes and 0 edges | 2, both row lists empty | 0 | EN and AR `NOT_CONFIGURED` states |
| Injected CONNECTION_FAILED | 88, `GRAPH_UNAVAILABLE` / `CONNECTION_FAILED`, 0 nodes and 0 edges | 2, both row lists empty | 0 | EN and AR `CONNECTION_FAILED` states. EN contains "The live graph connection failed." AR contains the Arabic catalogue sentence recorded in the result review |
| Restored AVAILABLE | 88, payload hashes equal to the initial AVAILABLE API | 2, portfolio hashes equal to the initial AVAILABLE API | 11, hashes equal to the initial AVAILABLE API | 44 journeys, same key set as the initial matrix |

Every initial and restored journey has `dossier_public_decision_equal` true, a return context equal to that journey's opportunity, mode and locale, and zero response interception. Public-mode browser decision hashes match the API decision hashes. Playwright 1.62.0 and Chromium 151.0.7922.34 are the versions recorded in the proof.

`continuation-2/execution/EXIT.json` records start `2026-09-26T01:59:04.396037+00:00`, end `2026-09-26T03:03:28.123807+00:00`, exit 0, and 3863.884 seconds. Stderr's recorded hash is the empty SHA-256. Final cleanup checked 10 saved identities, found no owned, browser or app survivors, sent 0 signals, and preserved coordinator lock PID 34210. Preservation before and after both record 3,307 sources and 56 indexes equal. `database_writes` in the execution receipt is 0.

## Coverage limit L1

This record does not claim live browser verification of Class-D labels on a synthetic passport. All selected current-case browser passports were public, including simulated journeys. In the published application proof, all 392 selected passports across the initial and restored matrices have `synthetic_flag` false: 98 public and 98 simulated in each matrix. The synthetic-passport branch therefore did not run live. Class-D graph-element EN/AR labels were asserted by the restored API and sampled in images, as recorded by the independent result review; the published API progress rows do not themselves carry those label strings. Public isolation was checked: no selected public-mode passport has `synthetic_flag` true. This assembly did not re-inspect all 448 images.

## Published subset and external bundle

[AURA-SOURCE-COPY-MAP.json](AURA-SOURCE-COPY-MAP.json) lists 65 exact byte copies and zero sanitized Aura derivatives. Fourteen representative PNGs are published, 8,480,405 bytes in total:

- EN and AR steel public evidence graphs and public dossiers
- EN and AR polypropylene public evidence graphs
- EN and AR steel simulated evidence graphs
- EN and AR steel public narrow graphs
- EN and AR `NOT_CONFIGURED` and injected `CONNECTION_FAILED` graph states

The other full-page dossier images, including the polypropylene dossiers, remain in the external 479-file index with the rest of the 448 PNGs. Full property inventories stay external. Private CLI streams, credential fingerprints, raw connection errors and Git index files are not in this subset. The 65 published sources had zero matches for connection-scheme, password-assignment, bearer, GitHub-token, private-key and CI-fixture patterns at copy time. That scan is not a universal credential scan.

The earlier 77 post-merge receipts stay unchanged: 74 original-byte copies and 3 sanitized CI-log derivatives, with [SOURCE-TO-PUBLISHED-BRIDGE.json](../SOURCE-TO-PUBLISHED-BRIDGE.json).

## Failure history that stays failed

| Subject | Published receipt | Disposition |
|---|---|---|
| Attempt 1 | `failures/attempt1-RESULT.json` | `FAILED_RECOVERED_OLD` |
| Attempt 2 | `failures/attempt2-RESULT.json` | `FAILED_RECOVERED_OLD`. Cause of the API view failure remains the receipt's unknown cause |
| Attempt 3 | `failures/attempt3-RESULT.json` and `reused/attempt3-application-proof.json` | `FAILED_RECOVERED_OLD` after the semantic API. The browser failure stays in the proof |
| Attempt 4 | `failures/attempt4-FAILURE.json` | FAILED. `operation_error` is `07-application_NONZERO`. Not recovered |
| Readonly-execution-1 | `history/readonly-interruption-1.json` | `INTERRUPTED_NO_COMPLETION_RECEIPT`. 35 capture files, 0 completed browser stages, no RESULT or EXIT. Cause unknown. Not counted as this result |

Research that treated readonly-execution-1 as still running is not the source of this page. The coordinator disposition of that research is external. The incident file above is the published history.

## Still open

- Independent review of this exact records candidate, including the existing whitespace disposition for 153 trailing-whitespace locations in 14 copied logs. Those historical bytes were not trimmed. This page does not call that full check clean.
- Separate delegated acceptance of the records delivery, then ordinary staging, commit, push, pull request, hosted checks, final-head review, merge and green main.
- Unknown Aura session-expiry cause and unknown readonly-execution-1 interruption cause.
- S21, complete MVP acceptance, PDF-UA, Appendix CARRY, KL-85, KL-107, KL-133, KL-134, KL-135 and KL-136. This Aura checkpoint does not close them.

Sanad: the hashes and counts in this page were read from the published copies and from the cited review and acceptance files. GitHub job success and the Claude verdict stay attributed to those records. Muhasabah for this page is a materialization statement only. Approval of the records candidate remains outside this writer.
