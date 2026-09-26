# S19 post-delivery Aura result review (read-only continuation 2): APPROVE

**Verdict: APPROVE this exact S19 Aura result.**
- Application proof: `f4f0e725c84dcbdd3e3a053a8eb528ff3765c0c3926e569275005e05917af983`
- Result: `ea8aea20fd8b66620adaabf869c0763247d5d8a38ae9195a61929a6e98fbb421`
- Evidence index: `c7ced65edb40b03d636d7e4c630a83701841cad3ceecaff04b65bf5bbd1ea083`

This approves the result only. Delegated acceptance, the records-only delivery, S21, the Ministry work and MVP completion are all separate. I found no blocking finding; one coverage limit (L1) must be worded exactly as below.

**Personas:** a live-verification result auditor, a process-lifecycle and cleanup auditor, and a provenance and attribution auditor. I applied the installed strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate skills.

## 1. Bindings (hashes I recomputed)

- **Approvals:** the first continuation GO `d4d616d3…`, the second GO `9aa4a4ab…`, and the release `0d041a36…`, which binds that GO, the packet and the incident.
- **Continuation-2 packet:** `SHA256SUMS` is `890b4c28…` and passes 4/4. `run-readonly.py` is `6ee0acc9…` and `capture-exit.py` is `8668160c…`.
- **Result files:** `EXIT.json` `bb2c810d…`, `FINAL-HOST-CLEANUP.json` `d6ad3590…`, `COORDINATOR-RESULT-CHECKS.json` `0afd05c1…`.
- **History:** `INCIDENT.json` `300f40e7…`, the lock reconciliation `0abd829a…`.
- **Evidence index:** all 479 rows re-hashed with 0 mismatches, sizes included. All 461 files in the output folder are indexed, with none missing, and they include 448 PNGs.

## 2. Lifecycle (conditions 1, 2, 4 and 6 of GO `9aa4a4ab`)

- **New session proven.** `LAUNCH.json` shows `start_new_session: true`. `RUNNER.json` and `SESSION-PROOF.json` show pid = process group = session = 72222. The child 72223 is in group 72222, and `START.json` has the exact argv with the RT venv python `-B`.
- **One run.** The run lasted 01:59:04 → 03:03:28Z, 3863.884 s, and exited 0. `stdout.log` (`8e16ef77…`, matches `EXIT.json`) lists exactly four `… completed` lines, one per stage in order. `stderr.log` and the runner logs are empty, and there is no failure key in the proof.
- **Chromium ran in its own group, as expected.** The ancestry snapshot at 01:59:37 shows `chrome-headless-shell` from the bound runtime in its own session/group 72477. That confirms the Playwright detachment I flagged in the GO review.
- **Cleanup checked the right things.** The final cleanup at 03:04:29 checked 10 saved identities and found no survivors: none owned, none from the bound browser, no app process. It sent 0 signals.
- **My own read-only look at host `/proc` now:**
  - PIDs 72222, 72223, 8961, 17162, 17177, 72465 and 72477 are absent;
  - 0 processes run the bound browser executable;
  - lock owner 34210 still has start ticks 79799 and `fd/3` → `delivery.lock`.

  The later kernel-lock ordinal differs from the reconciliation record's (29 vs 33). That ordinal is only a line number in `/proc/locks`, not an identity.
- **Result status:** `RESULT.json` is `EXECUTED_PENDING_INDEPENDENT_RESULT_REVIEW` with `database_writes: 0`, `initial_semantic_api_reused: true` and `fixed88_reused: true`. Its `application_proof_sha256` matches the file.

## 3. Subject and preservation

- **Inventory unchanged.** `full-before.json` and `full-after.json` are byte-identical (`cmp`), and both hash to `9b5cf8f9…`.
- **Parsed contents of `full-after`:**
  - database `8a7338e0`;
  - 925 nodes and 1,045 edges;
  - 19 constraints and 97 indexes, all ONLINE;
  - 515 synthetic and 410 public nodes;
  - a single `projection_id`, `GRAPH-SAU-2026-09-12-6f43b1a8c4aa`.
- **Preservation.** The before (01:59:05) and after (03:03:27) records both show 3,307 sources, 56 indexes, and packets, binaries, credential identity and the retained container all equal. The consumer receipt shows no hits, listeners or connections, with only PIDs 440 and 442 unreadable; its scope is the known deployment. The browser preflight shows 151.0.7922.34 and a blank page.

## 4. Application proof: independent parse

**Reuse gates held.**
- `available_api` is identical to attempt 3's `available_api`.
- The fresh AVAILABLE status equals the prior status exactly.
- `REUSED-RECEIPTS` binds attempt 3 `ff95c389…` with `new_api88_execution_claimed: false`, and fixed-88 `0d9f8ea7…` with `new_queries_claimed: 0`.

**The three fresh API stages** (`api-progress.json`, 88 unique (opportunity, mode, view) keys each: 11 opportunities × {public, simulated} × 4 views; all `pass`, HTTP 200):

| Stage | Status | Portfolios | Decisions | Payloads |
|---|---|---|---|---|
| NOT_CONFIGURED | `GRAPH_UNAVAILABLE`/`NOT_CONFIGURED` | 2, empty | — | all 0 nodes / 0 edges |
| injected CONNECTION_FAILED | `GRAPH_UNAVAILABLE`/`CONNECTION_FAILED` | 2, empty | — | all 0 nodes / 0 edges |
| restored AVAILABLE | AVAILABLE, status equal to attempt 3 | 2 | 11 | all 88 view payload hashes and both portfolio hashes equal attempt 3's |

The restored-stage equality independently corroborates the semantic reuse.

**Decisions.** The 11 before/after real-decision hashes are equal. Polypropylene (`SAU-H0-390210`) is REJECT; the other ten are INVESTIGATE.

**The two 44-journey browser matrices** (initial AVAILABLE and restored), each checked as sets:
- 44 records with 44 unique keys, forming the exact product of 11 cases × 2 modes × 2 locales;
- every journey ran all four views;
- 100 typed-empty views per stage, none of which rendered IDs; 0 API-vs-DOM ID mismatches on non-empty views;
- every journey has a current-case passport, selected by keyboard;
- 0 synthetic passports in public mode;
- dossier public-decision equality holds for all 44;
- the return context exactly equals (opportunity, mode, locale) for all 44;
- the per-case public-decision hashes equal the API decision hashes;
- `errors: []`, `response_interception: false`, Playwright 1.62.0, Chromium 151.0.7922.34.

**Fault-stage browser states.** EN and AR records for each reason contain the exact catalogue failure text. Examples: "The live graph connection failed." and «فشل الاتصال بالرسم الحي».

**Images.** The two AVAILABLE folders each hold 220 PNGs: exactly locale × 11 slugs × mode × {dossier, evidence, evidence-graph, narrow, narrow-graph}. Each fault stage holds 4. Total 448.

## 5. Images I actually looked at (a sample, not all 448)

- **`restored/en-steel-simulated-evidence-graph`:** the bilingual "SIMULATED — NOT MINISTRY EVIDENCE" banner, a synthetic "Plant · D" node, the public Product · B, and passports with source, URL and class.
- **`available/ar-polypropylene-simulated-evidence-graph`:** an RTL layout with the Arabic simulation banner, «المصنع · D», and Arabic source-language captions.
- **`injected/ar-connection_failed-graph`:** the Arabic unavailable state with a retry button.
- Three full-page captures were too downscaled to judge detail.

In these full-page captures the fixed app header appears partway down the page. That is a full-page capture artefact, not a product finding.

## 6. Coverage limit L1 (wording required; not blocking)

- **What didn't run.** In every simulated journey the selected current-case passports were public records (`synthetic_flag` false for all 22 × 2). So `check_passports`'s synthetic branch, which asserts Class-D labels on a synthetic passport, **never ran live**.
- **Why this doesn't fail the result.** The approved assertions don't require that branch. Class-D disclosure is established by:
  - the fresh restored API assertion that every synthetic element is class D with EN/AR labels;
  - public isolation, both API and browser;
  - the sampled images above.
- **Required wording:** the record must not claim live browser verification of Class-D labels on a synthetic *passport*.

## 7. Required attribution (to preserve verbatim in substance)

- **Three fresh API stages plus one semantic reuse (attempt 3).**
- **Fixed-88 reused.** The attempt-2 origin is attributed; I checked the file hash only.
- **Attempt 4's** stock clear/load/reload/verify and operator receipts are reused on an equal subject. Attempt 4 itself remains **FAILED**; its recovery was blocked and nothing was cleared.
- **Attempts 1–3:** `RESULT.json` = `FAILED_RECOVERED_OLD` (I checked).
- **`readonly-execution-1`:** INTERRUPTED, tool exit 143, 35 partial EN images, no RESULT or EXIT. Not counted.
- **Restored after fault**, never "continuously available". The CONNECTION_FAILED stage was a process-local injected fault, not an Aura outage.
- The causes of the earlier Aura session expiry and of the exit 143 remain **unknown**. This run's success does not explain or fix either.

## Sources

- The continuation-2 execution receipts, `LAUNCH.json`, `SESSION-PROOF.json` and the three ancestry snapshots.
- All 461 files in the output folder; the evidence index; the attempt-3 proof; results from `live-execution-1` through `live-execution-4`.
- The approved `verify_app.py` browser and API assertions (`api-failure-correction-1`, `3d4b25d9…`).
- The S19 Aura handoff draft (`:41`) and `COMMANDS.md` (`:96`).
- Host `/proc`, read-only.

## What I checked myself versus what I relied on

- **Checked myself:** every hash, parse, set comparison, `cmp` and image view above, plus the current `/proc` absence check.
- **Relied on others' records:** that the receipts reflect genuine live Aura and app responses. They were produced by the hashed script, but I made no Aura access. Also relied on: the host process states at 01:59–03:04, the attempt-2 origin of fixed-88, and PR40/main-run success.

## Assumptions and limits

- The consumer and writer checks cover the known deployment only.
- I viewed 5 of the 448 images.
- The coordinator's check JSON was not used as evidence for my conclusions.

## Pending obligations

Delegated acceptance of this result, then the records-only candidate with its own independent review and delivery.

## Sanad / Muhasabah

**Sanad:** every claim above is tied to a hash I computed, a parsed field, or a direct observation. Where I rely on someone else's record, I say so.

**Muhasabah:**
- **Khawatir.** My first pull was to approve because it exited 0 and the coordinator's checks agree.
- **Muraqaba.** I rejected that and re-derived the matrices myself. That is how the unexercised synthetic-passport branch (L1) surfaced, rather than being hidden behind a count of 44.
- **Mujahada.** I rehashed all 479 files, compared sets rather than counts, and cross-checked the payload hashes that corroborate the reuse.

**Gate:** PASS. No unperformed check is reported as passing, no cause is invented, and no future or S21 claim is made.

**Final:** APPROVE this exact result, with the wording required in §6–§7.