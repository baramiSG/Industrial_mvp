# S19 read-only continuation review: APPROVE (targeted GO), with conditions

**Scope:** incident adjudication of attempt 4, plus a GO decision for `readonly-continuation-1/run-readonly.py` (`61c1bb39…`) only. This is not an S19 Aura completion, S21 or MVP claim. I wrote no files and made no Aura, browser, service, test or Git access. All checks were static reads, hashes and JSON parses.

## 1. Incident adjudication of attempt 4

**Outcome:** attempt 4 **FAILED**. It must never be counted as a pass. The recovery-blocked, no-clear handling was **correct**.

**What worked:**
- Every stock stage matched exactly and had empty stderr: clear; load 925/1045; reload 0/0; verify `GRAPH-SAU-2026-09-12-6f43b1a8c4aa; 925 nodes; 1045 edges`.
- The operator test gave `1 passed`.
- The browser preflight passed (Chromium 151.0.7922.34, blank page, no network).

**Where it failed:** at 01:14:32Z the stage `07-application` exited non-zero with `API_VIEW_STATUS`.
- `api-progress.json` shows 46 passes, then view 47 pending: `SAU-H6-310510` / simulated / `shared_enabler`.
- That view returned HTTP 200 with `GRAPH_UNAVAILABLE` / `CONNECTION_FAILED`. The service degraded as designed; it was not a wrong-data result.
- The attributed exception chain was `ReadServiceUnavailable` → `SessionExpired`. The full wrapper stderr was not kept, so this attribution is from the tool session only.

**What happened next:** the policy stopped there. `RECOVERY-BLOCKED.json` records no recovery command. Clearing would have been unsafe because the live state had not been re-established at that moment.

**Later diagnosis (`connectivity-diagnosis-1`, all exits 0, all stderr empty):**
- The probe at 01:16:54Z got DNS OK, TLS 1.3, and `RETURN 1` succeeded on both read and write routing. The write-routed call was a read-only statement.
- 12 of 12 cold-connection samples at 01:19 were OK.
- The full read-only inventory at 01:18:09Z returned `READONLY_FULL_INVENTORY_MATCH`: NEW `…6f43…`, 925/1045, 19 constraints, 97 indexes all ONLINE, no duplicates or dangling edges, hash `9b5cf8f9…`, `write_operations: 0`.
- `PRESERVATION-AFTER-DIAGNOSIS` shows 3,307 source files and 56 indexes unchanged.

**Root cause is unknown.** It is a transient Aura read-session or routing expiry. It also occurred in attempt 2, which failed the same way (`API_VIEW_STATUS`, cause unknown), so it recurs. Nothing points to a product defect. The service reported unavailability honestly instead of returning wrong data.

## 2. Ruling 1: keep NEW and resume read-only: **APPROVED**

- The script makes no writes. Every database access goes through `operator_core.inventory`, which runs only `routing_='r'` queries: `db.info`, `MATCH … RETURN`, `SHOW CONSTRAINTS`, `SHOW INDEXES`.
- `loader.resolve_target` only builds the connection settings. Clear, load and `fixed_views` are never imported or called.
- On failure it writes `FAILED_STOPPED_NO_DATABASE_MUTATION` and records `live_state: "Not re-certified after failure; no recovery clear authorized"`. That is the required "unknown, not pass" labelling.
- Attempt 4's stock receipts are reused against the same subject, which is gated fresh by `complete()` (keyed NEW, schema equal to baseline, all indexes ONLINE) plus byte hash `9b5cf8f9…`. No new load cycle is needed. The one prerequisite is met: attempt 4's load/verify receipts and the diagnostic inventory show NEW, and the script re-proves it before doing anything else.

## 3. Ruling 2: reuse of attempt 3's AVAILABLE API receipt: **APPROVED**

Every required gate is in the script, before stage one:

| Required gate | Where in `run-readonly.py` |
|---|---|
| Full NEW byte equality | `sha(full-before.json) == 9b5cf8f9…` after a fresh `complete()` |
| Source/settings/subject checks | `preservation()`: 3,307 source hashes, 56 index hashes, 17 subjects, 4 packet `SHA256SUMS`, browser binaries, credential identity (dev/inode/size/mtime plus SHA, never printed), retained container `42216eec…` healthy and `StartedAt` unchanged |
| Prior receipt is intact and complete | attempt-3 proof `ff95c389…` (verified); progress has 88 views, all pass (`4d1dade0…` verified); 88 views, 2 portfolios, 11 decisions |
| Fresh status exactly equals prior AVAILABLE | `app.get('/api/graph/status') == prior_api['status']` from the newly started app |
| Fixed-88 reuse still bound | `fixed-views.json` `0d9f8ea7…` (verified) |

- The prior status is deterministic (`artifact_projection_id`, `live_projection_id` NEW, counts 925/1045, partition 410/515, `target: aura`, `reason_code: null`). The exact-equality gate is therefore **stronger** than `api_proof`'s own status check, and it cannot fail spuriously on a timestamp.
- **Everything else stays fresh:**
  - 44 AVAILABLE journeys against the real API.
  - NOT_CONFIGURED and CONNECTION_FAILED: 88 views, 2 portfolios and the browser run each.
  - Restored AVAILABLE: 88 canonical views, 2 portfolios, 11 decisions and 44 journeys.
  - The 11-hash before/after equality, comparing attempt 3's hashes with the fresh restored hashes.
  - A fresh `full-after` NEW/schema check and a fresh `PRESERVATION-AFTER`.
- **Labelling:**
  - `report.initial_api_semantics_reused: true`.
  - `REUSED-RECEIPTS.json` records `new_api88_execution_claimed: false` and `new_queries_claimed: 0`.
  - `RESULT.json` records `initial_semantic_api_reused` and `fixed88_reused`.
- **Is any proof genuinely lost?** No. The only AVAILABLE-stage item not re-run is the `/api/graph/catalogue` 4-view check. Attempt 3's receipt covers it semantically, and it runs fresh in the other three stages. That is a timing difference, not lost proof.

## 4. Cleanup, scope and assertion fidelity against the approved `verify_application` (`3d4b25d9…`)

- **Stages** use the same tuple, order, selectors, fault flags and reasons. The fault stage is the external `fault_app` (`39306053…`, bound in the packet), not local. In the three fresh stages, `api_proof` and `browser_proof` are called exactly as in `verify_application`. The only deviation is the AVAILABLE api→status substitution already approved in ruling 2.
- **Children:** there is a leak check before each stage, `App.stop()` in `finally` (terminate, then kill after 15 s), a post-stage reaped check, and a sweep in the `except` block.
- **Final assertion** is identical: `len(before)==len(after)==11 and before==after`.
- **Output:** `OUT.mkdir(exist_ok=False)`; `readonly-execution-1` is confirmed absent.
- **Consumer gate:** it scans `/proc` for the known deployment. It reads env var *names* only, never values. It also checks for listeners on 8000/8001/8010 and Bolt connections on 7687/7688.
- **Browser preflight** repeats the blank-page launch with pinned Playwright 1.62.0 and Chromium 151.0.7922.34.

## Conditions (binding)

1. **One run, no retry.** Run it exactly as hashed, with `RT/.venv/bin/python -B`, under a fresh delegated release. On any failure, including a repeat of the transient `CONNECTION_FAILED` in the restored stage or in the browser stage:
   - no clear and no retry;
   - live state is reported UNKNOWN until a separate read-only inventory;
   - a new independent review is required.
2. **Pre-loop failure counts as UNKNOWN.** A failure before the `try` block (preservation, consumers, preflight, `complete()`) leaves no `RESULT.json`. The coordinator must record it as FAILED/UNKNOWN from the exit code and stderr, and must not re-run blindly.
3. **Report wording must say:**
   - "three fresh API stages plus one semantic reuse (attempt 3)";
   - "fixed-88 reused";
   - "restored after fault", never "continuously available";
   - attempt 4 = FAILED, not recovered, NEW state retained.

## CARRY items (not blocking)

- **a. Failure record is less detailed** than `verify_application`'s: it lacks `error_code`. `FAILURE.txt` still has the traceback with the `OperationError` code.
- **b.** The `except` sweep's `child.wait(timeout=15)` has no kill fallback. `App.stop()` has already done terminate-then-kill, so the risk is minimal.
- **c. Traceback redaction** covers only the URI and password; the username and host fragments may appear. No secret is exposed, but future scripts should redact the whole selected set.
- **d.** The whole wrapper stderr was not retained in attempt 4. Keep it in this run.
- **e.** The Aura session-expiry root cause is still open. The design handles it safely.

## Sanad / Muhasabah

**Sanad:** these findings rest on:
- direct reads of `run-readonly.py`, `verify_app.py`, `operator_core.py` and the attempt-3, attempt-4 and diagnosis artifacts;
- my own SHA-256 checks: the packet (4/4 OK), `SUBJECTS` (17/17), `ff95c389`, `4d1dade0`, `0d9f8ea7`, `3d4b25d9`, and `26fb9fea` for my previous review;
- JSON parses of the status, coverage counts and the 12 samples.

**Taken from artifacts, not re-observed:** the tool-session exception chain, and the live Aura state itself. I made no Aura access, so NEW is established by the 01:18:09Z receipt and the script's own fresh gate, not by me.

**Muhasabah:**
- My main risk of error is judging the catalogue omission "not lost". I'm confident in that, because the catalogue is a static 4-view list checked fresh three times.
- I also judged the transient-failure recurrence not blocking. That rests on the policy of failing honestly with no clear. It does not predict success: the run may fail again on the same flake.
- No earlier mistakes from this session carry into this verdict.

**Verdict: APPROVE** the targeted read-only continuation GO for `run-readonly.py` `61c1bb39…`, under Conditions 1–3.