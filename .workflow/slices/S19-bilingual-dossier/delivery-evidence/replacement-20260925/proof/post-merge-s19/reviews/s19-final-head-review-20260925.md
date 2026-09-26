# Independent exact-head review: S19 PR #40

## Verdict: APPROVE
I approve PR [#40](https://github.com/baramiSG/Industrial_mvp/pull/40) at exact head **`39614fcdd8d8eb9a96381c3d1b806343d5164419`**, tree **`7c25b4616679d61f173f3d9072e3240e1a2a166b`**, which is the implementation tree I approved (`50f33c00…`). All six hosted checks completed successfully in run `36175983021`, attempt 1.

There are no blockers and no divergence from the approved subject. This verdict does not merge the PR or prove `main` green. I mutated nothing: GitHub reads were `gh` GET/view only under the existing read route, with no account switch or credential exposure. Git used `GIT_OPTIONAL_LOCKS=0`.

**Personas:**
- release/CI reviewer
- evidence-integrity auditor

**Skills:** the six installed skills, unchanged, applied.

## Bindings (hashes I computed; all match)
- Implementation APPROVE `50f33c00…`; delegated acceptance `534d242f…`; `COMMIT.json` `32dcf5ae…`.
- `HOSTED-RESULT` `8df202a2…`; `RUN-FINAL` `6bc5e14a…`; `PR-FINAL-CHECKS` `ecaf4db1…`; `HEAD-AND-PRESERVATION` `6a357e8e…`; published body `2c5218f6…`; `SIX-JOB-LOGS` `d19da0db…`; `run.log` `f2152a32…`.
- The six job logs: `36f7c682…`, `34cb5215…`, `53ece3e4…`, `a2c7a1b8…`, `b58f0d44…`, `ffa3808e…`.

## Direct checks

**Live PR readback**
- State OPEN, not a draft, base `main` at `ce407db9832b61c5a8a85dfda2e3b7623da2fbc9`.
- `headRefOid` is exactly `39614fcd…` on `slice/s19-bilingual-dossier`, with 1 commit. Mergeable, `mergeStateStatus` CLEAN.
- The live body equals the retained published body; they differ only in the trailing newline `gh` adds.

**Commit ancestry**
- `39614fcd` has a single parent, `ce407db`, and tree `7c25…`.
- Remote `slice/s19-bilingual-dossier` points to `39614fcd`; remote `main` still points to `ce407db`.
- Locally: HEAD `39614fcd`, tree `7c25…`, upstream equals HEAD, 0 staged and 0 tracked changes.
- `COMMIT`/`STAGED-TREE` receipts record the staged tree equal to `7c25`.

**Synthetic checkout**
- Commit `0ba7806c8d9c0960d6647389a6b11694f00aaf5c` is "Merge 39614fcd into ce407db", with parents `[ce407db, 39614fcd]` and **tree `7c25…`**. Because the head's only parent is the current `main`, the PR merge tree is identical to the approved tree. It is not a new source commit.
- All six logs contain `0ba7806c…`.

**Run and jobs**
- Exactly one run exists for this head: `36175983021`, `pull_request`, attempt 1, completed/success.
- The six check-runs on `39614fcd` are all completed/success:
  - `uv / Python 3.12`
  - `uv / Python 3.14`
  - `pip / Python 3.12`
  - `Docker image build`
  - `graph / Neo4j service / Python 3.12`
  - `browser / Chromium / Python 3.12`
- No failed steps. The only skipped step is `Upload browser diagnostics on failure`, which runs only on failure.
- No cancellations or reruns.

**Workflow definition**
- `.github/`, `Makefile` and `browser_tests/conftest.py` are unchanged between `ce407` and the head, so this is the same gate `main` already uses.

**Raw logs** (no `##[error]`, Traceback, `FAILED`, `N failed`, `--mode update` or `IOR_UPDATE_VISUAL` lines in any of them)
- **Both uv jobs and the pip job:** prohibited-file scan (3,307), threshold scan, UI contract, ES modules (51), `INTEGRITY PASS`, 11 scenarios, all 7 reconstruction passes, `3982 passed`, `SMOKE PASS`.
- **Docker:** build, then `IMAGE_HAS_NO_NEO4J_OK`.
- **Graph:**
  - `build --check`: `GRAPH BUILD PASS (6f43…; 925; 1045)`;
  - load twice (925/1,045, then 0/0) and `GRAPH VERIFY PASS`;
  - equality suite 9 passed with `SKIPPED [1] … test_aura_verification.py:18: AURA_OPERATOR_ONLY`;
  - graph UI 1 passed;
  - service stop, then the fail-closed `graph_unavailable` suite, 2 passed.
  - The skip is the explicit live-Aura operator test. It is not proof of anything about Aura, and not a failed local check.
- **Browser:**
  - literal `make UV=uv e2e` with two passing preflights;
  - `839 passed, 4 deselected` (3,422.78 s);
  - then `4 passed, 839 deselected` (352.04 s) under the default `IOR_VISUAL_MODE=compare` (`conftest.py:223`). The workflow sets no update variables, and update mode would additionally require the canonical container.

**Local preservation**
- The ordinary index is at the authorized post-staging `d5e9a315…`.
- The other 53 protected indexes are equal to their bound hashes.
- W matches all 3,307 inventory files.

**PR body truthfulness**
- Its claims match the verified evidence:
  - tree `7c25`;
  - offline 14/14 and 3,982 passed;
  - e2e 839 plus 4;
  - R1 pass;
  - both `make ci` durations;
  - each root's 44-PDF proof (1,958 pages, 3 fresh appendix fallbacks, 1,911 attributed reuses, explicitly not claimed as fresh);
  - the interrupted attempt not counted;
  - the receipt hashes;
  - Codex versus Claude attribution;
  - the limits (native print only, no PDF/UA certification, Class D synthetic data, unknown reboot trigger, Aura/S21/MVP not claimed).
- Its unchecked boxes for hosted checks, head review and merge/main were accurate at submission.

## Retained from earlier records
- Implementation approval `50f33c00` and its full evidence chain.
- Delegated acceptance, the push, and PR-creation receipts. The earlier HTTP 403 was an account mismatch, retained in `GITHUB-CREDENTIAL-CORRECTION`, with no source change.
- The early log-read failure (`EARLY-LOG-READ.json`) was a GitHub availability limit, not a test outcome.
- The host-restart trigger remains unknown.

## Findings

**Blockers:** none.

**Divergence from the approved subject:** none. Head, base, tree, body and workflow are all consistent with the approved `7c25`.

**CARRY:**
1. Record a separate delegated merge release. Squash-merge using `--match-head-commit 39614fcdd8d8eb9a96381c3d1b806343d5164419`. Then verify the actual merge SHA and that its tree equals `7c25` (base is still `ce407`), and that all six **main push** jobs are green. Any change to the head requires a renewed review.
2. Only then may the additive delivery record close KL-33, KL-84, AR-V01 and TRADE-SCALE-01. It should keep the earlier preferences (route external-label generalisation; units after a status) and the unknown restart cause as limitations.
3. The post-delivery Aura checkpoint and live bilingual verification remain separate obligations. The hosted graph job used a local service and skipped the Aura test. No S21 or complete-MVP claim.

## Sanad
**Direct:** the live `gh pr view`, run, check-run, commit and branch readbacks; the body comparison; the workflow, Makefile and conftest diffs and reads; the six raw logs; local HEAD, tree, upstream, status and index hashes; the 3,307-file rehash; all bound file hashes.

**Attributed:** staging and push mechanics; the credential correction; early-log availability notes; prior local gates accepted in `50f33c00`.

**Limits:** GitHub has no required contexts configured, so the six-job list comes from the unchanged workflow and was checked by name. Hosted CI does not certify Aura.

## Muhasabah
- **Khawatir (first framing):** "`gh pr checks` is green, APPROVE." Not enough on its own.
- **Muraqaba (watching for bias):**
  - I derived the tree of the synthetic merge checkout myself rather than accepting the checkout SHA;
  - verified there is exactly one run for the head, with no reruns;
  - read every log for stages and failure patterns;
  - confirmed compare mode from source;
  - traced the graph skip to its exact reason.
- **Mujahada (the actual work):** checked that the workflow is unchanged from `main`, so the gate is the established one, and checked every claim in the PR body against evidence.
- **Gate:**
  - Provenance: PASS.
  - Fabrication: PASS. No merge, main or Aura claim.
  - Requirements: PASS. Exact-head verdict, six jobs, body and CARRY are given.
  - Risk: read-only.

Nothing was written. Save this text externally.
