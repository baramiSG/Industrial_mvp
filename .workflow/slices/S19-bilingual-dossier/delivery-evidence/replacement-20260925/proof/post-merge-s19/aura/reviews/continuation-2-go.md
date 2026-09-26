# S19 read-only continuation 2 (interruption and lifecycle review): APPROVE, targeted GO for one attempt

I'm approving one new attempt of `readonly-continuation-2/run-readonly.py` (`6ee0acc9…`), run through `capture-exit.py` (`8668160c…`), under a separate delegated release. This approves the operation only. It is not approval of any future result, and it does not fix or explain the earlier termination or the Aura session expiry.

**Personas:** a strict gatekeeper for the verdict, a process-lifecycle engineer for the wrapper and cleanup, and a provenance auditor for the incident facts. I applied the installed strict-reviewer, sanad-provenance, al-muhasibi and muhasabah-gate skills.

## Incident adjudication (`readonly-interruption-1`)

- **Run 1 got through its pre-loop gates.** `readonly-execution-1` holds:
  - `PRESERVATION-BEFORE`: 3,307 sources, 56 indexes, packets, binaries, credential identity and the retained container all equal.
  - `CONSUMERS`: no hits, no listeners, no connections; only PIDs 440 and 442 unreadable.
  - `BROWSER-PREFLIGHT`: 151.0.7922.34, blank page.
  - `full-before.json` hashes to `9b5cf8f9…` (I re-hashed it).
  - `REUSED-RECEIPTS`: labels correct.
  - `application-proof`: only `available_fresh_status`, which matches the attempt-3 status exactly, plus the reuse labels.
  - `CURRENT-STAGE`: available, started 01:43:50Z.
  - `available/`: 35 English-only PNGs; there is no `RESULT.json` and no exit receipt.
  - The `START.json` in continuation-1 shows PID 37056 and script `61c1bb39…`. Its `stdout.log` and `stderr.log` are both 0 bytes. That is consistent with a mid-stage stop, because the script prints only when a stage completes.
- **Classification: INTERRUPTED, no completion receipt.** The 35 partial captures count toward nothing, and no journey passed. Exit 143 matches a SIGTERM delivered to the tool shell. The sender is **UNKNOWN**; I don't attribute it to a timeout, OOM or the user.
- **After the interruption:**
  - `FULL-PREFLIGHT.stdout` (`c3f3c9b3…`, exit 0, stderr empty) shows exact NEW `…6f43…`, 925/1045, 19 constraints, 97 indexes ONLINE, hash `9b5cf8f9…`, `write_operations: 0`.
  - `PRESERVATION-AFTER-INTERRUPTION` (`4ab0385c…`) shows 3,307 / 56 and `no_drift`.
- **Lock owner:** the reconciliation record (`0abd829a…`) and my own read-only look at host `/proc/34210` agree. `fd/3` points to `delivery.lock`, fdinfo shows FLOCK, start ticks are 79799, and cwd is the repo. The lock is live, not stale.

## Packet check (`readonly-continuation-2`)

- **Hashes:** `SHA256SUMS` passes 4/4: CONTINUATION `8069527a…`, run-readonly `6ee0acc9…`, diff `e5b1bd72…`, capture-exit `8668160c…`.
- **Script change:** my own `diff` against continuation-1 (`61c1bb39…`, re-verified) shows exactly one changed line, `OUT = AR / 'readonly-execution-2'`. The shipped `.diff` matches. No assertion, reuse, stage, cleanup, failure or database policy changed.
- **Gates still bound:** the script's internal `Q` still points to continuation-1. Its packet re-verifies 4/4 and its 17 `SUBJECTS` entries all match, so the fresh preservation gate is satisfiable.
- **Fresh outputs:** `readonly-execution-2` and `readonly-continuation-2/execution` are both absent.
- **`capture-exit.py` is stdlib only and one-shot.** It:
  - asserts the script hash;
  - asserts the owner 34210's start ticks 79799, cwd, `fd/3` pointing to `delivery.lock` with FLOCK (all three matched the host when I checked);
  - requires that the output folder does not exist;
  - uses umask 077;
  - records RUNNER, START and EXIT receipts (EXIT includes the stdout/stderr SHAs);
  - strips `NEO4J_`, `AURA_`, `IOR_GRAPH_`, `ANTHROPIC_`, `OPENAI_`, `OPENROUTER_`, `*API_KEY*` and `*AUTH_TOKEN*` from the environment (the script still reads `.env` itself, unchanged);
  - has no retry and no loop, and never signals anything.
- **What this fixes:** a child exit code (including a negative signal code) and the full logs survive independently of the tool command handle. That is the missing evidence from run 1.
- **`claude-go/`** is this review's own capture. `AUTH-ROUTE` shows `authMethod: claude.ai`, `apiKeySource: null`, `subscriptionType: max`.

## Why GO despite the unknown cause

The attempt is read-only and fails closed:
- every database call is `routing_='r'`;
- all gates are fresh;
- a failure means no clear;
- the earlier conditions still apply.

If the same termination happens again, the worst case is another interruption with no mutation, and this time with better evidence. This is not a blind repeat, because the lifecycle change is concrete.

## Binding conditions

1. **Before launch:** confirm again the four hashes, a new delegated release, the lock identity, and that both output folders are absent. One launch only; no automatic retry.
2. **Prove the new session.** `RUNNER.json` must show `session == process_group == wrapper pid`, and `START.json` must show the child in that same group. The launcher isn't a hashed artifact, so this receipt is the proof that it used `start_new_session`. If it doesn't hold, record a lifecycle deviation.
3. **Chromium is outside the owned group.** Playwright 1.62's bundled launcher spawns the browser with `detached: process.platform !== "win32"` (`coreBundle.js`). That puts Chromium in its own process group, so "stop the owned group" does not reach it. If the run is stopped or interrupted:
   - also check for surviving processes from the bound `PLAYWRIGHT_BROWSERS_PATH` executable;
   - stop only processes that are provably children of this run (ancestry, start time after `RUNNER.utc`);
   - never touch 34210 or unknown processes;
   - then establish live state separately with the read-only inventory.
4. **Classify the exit honestly:**
   - missing `EXIT.json` or `RESULT.json` = INTERRUPTED/UNKNOWN;
   - negative `rc` = terminated by signal;
   - `rc == 1` = failed assertion, following conditions 1–2 of review `d4d616d3`;
   - none of these is a pass.
5. **Wording rules from review `d4d616d3` still apply:** "three fresh API stages plus one semantic reuse (attempt 3)", "fixed-88 reused", "restored after fault". Also record attempt 4 = FAILED, `readonly-execution-1` = INTERRUPTED and not counted, and the NEW state as retained.
6. **Independent review:** the result needs an independent result review and separate delegated acceptance.

## CARRY items (not blocking)

- a. The launcher and the wrapper's interpreter are described but not hashed. Condition 2 covers this after the fact.
- b. The wrapper has no signal trap. If only the wrapper is killed, the child keeps running and `EXIT.json` is missing; the script's own `RESULT.json` still records the outcome.
- c. The earlier CARRY items (`error_code` in the failure record, the kill fallback in the `except` sweep, full redaction) are unchanged.
- d. The root cause of exit 143 and of the Aura session expiry is still open.

## Sanad

**Checked directly by me:**
- the hashes of the prior review `d4d616d3…`, the continuation-2 packet, the continuation-1 packet and its 17 subjects, `full-before` `9b5cf8f9…`, the interruption preflight `c3f3c9b3…` and preservation `4ab0385c…`;
- the `diff` result;
- that both output folders are absent;
- host `/proc/34210` metadata;
- the Playwright bundle's `detached` spawn and its `process.kill(-pid)` group kill.

**Attributed, not observed by me:**
- tool session 78761's exit 143;
- PID 37056 being absent at 01:48:47;
- no children at 01:49:22;
- the empty host journal;
- the identities of the other Codex processes.

**Not performed:** no Aura access, no runs, no process signals, and no reading of credential contents.

## Muhasabah (gate: PASS)

- I did not invent a cause for the termination. The Chromium-detachment condition comes from reading the installed code, not from an assumption.
- The main judgement call is treating the recurrence risk as acceptable. That rests entirely on the fail-closed, zero-write design; it predicts nothing about success.
- The launcher's parameters are prose only, and I made them checkable after the fact (Condition 2) rather than approving them unseen.
- Nothing in this review claims an unperformed check passed, and nothing in it claims a future pass, S21 or the MVP.

**Verdict: APPROVE.** Targeted GO for a single attempt under Conditions 1–6.