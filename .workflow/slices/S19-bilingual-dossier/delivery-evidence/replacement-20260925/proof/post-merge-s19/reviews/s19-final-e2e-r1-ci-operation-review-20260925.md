# Independent review: S19 exact-tree e2e/R1 adjudication (A) and two-root CI plus own-PDF operation (B)

## Verdicts
- **A. ACCEPT** the completed standalone compare-only `make e2e` and the actual-predecessor R1 result for tree `7c25b4616679d61f173f3d9072e3240e1a2a166b` (proof commit `29bf5db55adaa57de2fa1f78aa5c9a028f31dc75`, freeze `80c60cab…`).
- **B. APPROVE (GO)** for the exact sequential two-root `make ci` operation, followed by each root's own 44-PDF seal, raster, strict and manual proof, as bound below. GO holds only under the conditions in B.3.

No blockers. This is not final implementation acceptance. My source APPROVE `5ade2422…` stays bound to this tree. I ran nothing and mutated nothing. The only Docker calls were read-only `inspect`/`ps`/`ls` with no environment fields. Git reads used `GIT_OPTIONAL_LOCKS=0`, and all 53 protected indexes matched at the end.

**Personas:**
- CI isolation/recovery engineer
- browser-regression adjudicator
- release-provenance auditor

**Skills:** the six installed skills (unchanged), applied.

## A. Completed e2e and R1

**Standalone e2e (direct checks)**
- `RESULT.json` `0d186b92…`, stdout `bcc5f1da…` and stderr `0c38bd07…` all match.
- The literal `make e2e` ran:
  - `839 passed, 4 deselected in 2291.70s` (functional);
  - `4 passed, 839 deselected in 235.30s` (visual, `-m visual`, compare mode);
  - both after the browser preflight passed.
- stderr contains only the `uv` environment-creation output.
- Exit 0, ended 15:36:31Z. The result records all 53 indexes and all 3,307 bytes equal in both the root and W.

**R1 (direct checks)**
- Capture argv and compare argv equal the bound `COMMANDS.json` (`e8715cef…`).
- R1 started at 15:38:59Z, after the e2e exited, which satisfies my condition 1.
- Capture exited 0 in 9.158 s (`R1_CAPTURE_COMPLETE_CHILDREN_CLOSED`); compare exited 0 in 0.21 s (`R1_RUNTIME_COMPARISON_PASS`). Both stderr files are empty and both processes were reaped.
- `COMPARISON.json` (`9c74e0df…`): `evidence_kind` RUNTIME, `pass: true`, `findings: []`, binding `3e66089e…`.
- `measurements/` holds exactly the 8 phase files, plus only `runtime/server.log`.

**My own analysis of the eight phase files:**
- Every file carries the exact runtime binding (`RUNTIME-BINDING.json` `ec459dc2…`).
- In both EN and AR:
  - N = N2 = N3, byte-equal as measurements;
  - 12 rows;
  - 5 run-ID rows;
  - normalised tuples equal the binding;
  - state is steel, public, `evidence_to_change`, 1440×900, DPR 1, with correct `lang`/`dir`.
- **O** rewrites exactly rows 1–5, one token each: `ENGINE-6b54371e99f3` → `ENGINE-a1dcbf0e7665`, the actual delivered `ce407` token, not the `7ae` CSS-sensitivity token. **N3** restores all five.
- Comparing N with O, the *only* differences are the five `source` text leaves and the five matching text nodes.
- Geometry, line bands, anchors and fold fields are **identical at 0.01**, which is stricter than the allowed EN/AR span/small-width leaves permit.
- The `below_fold` and `clipped_at_fold` flags describe the scrollable section. They are stable across all phases and are not failure criteria in `compare.py`.

**Closure**
- `EXECUTION-CLOSURE.json` (`76632a0f…`) asserts source, helpers, no pycache, binding and 53 indexes unchanged, and the container absent. My independent re-checks agree:
  - `r1-source` still equals the 3,306-row inventory;
  - the helper directory has 7 files and no pycache;
  - no `ior-s19-r1*` container exists;
  - the 53 indexes are equal.

## B. Two-root CI and own PDFs

### B.1 Checks I performed myself

**Packet**
- `FINAL-OPERATION-SHA256SUMS` `e63b5f1d…`: all 8 entries OK. The packet `SHA256SUMS` passes as well.
- Bound files:
  - `CI-RUNTIME-PROPOSAL.json` `140df801…`
  - `PER-ROOT-PDF-COMMANDS.json` `89562d8b…` (byte-identical to its `.draft`)
  - `EXECUTE-ALLOCATED-PAIR-S19.py.draft` `7bbc0dce…`
  - `PREPAUSE-COPY-BINDING.json` `fdcf444b…`
  - `PREPAUSE-PREPARATION.json` `66f736bf…`
  - `PREPAUSE-VERIFY-EXECUTION.json` `e4b49e37…`
  - override files `af2e6b77…` / `6bbdb334…`
- The BASE copies have the same hashes, and `attempt1` is absent.

**Proposal**
- The diff from the draft changes only status text and the completed e2e, R1 and copy bindings. Commands, environments, namespaces, configs, protected indexes and recovery method are unchanged.
- Runs: literal `["make","ci"]` in `ci-root1` and then `ci-root2`.
- Each environment explicitly sets `GIT_OPTIONAL_LOCKS=0`, `COMPOSE_FILE` (stock compose plus the bound override), project `s19-ops2-ci{1,2}`, `COMPOSE_DISABLE_ENV_FILE=1`, and a per-root graph pycache prefix outside the root.
- Overrides: only the container, volume and network names differ from the reviewed `ops1` version. Ports are `!override` loopback `127.0.0.1:7475/7688`.

**Makefile `ci`**
- It runs the graph gate: fresh credential, owned compose `up`, a `clear` on its own target, load twice, verify, graph tests and UI tests, then `graph-down` = `compose down --remove-orphans` (no volume removal) via trap, then the unavailable-graph test.
- Then it runs:
  - prohibited-file and threshold checks, UI contract, `compileall` and ES-module checks;
  - integrity, scenarios, reconstruction;
  - full pytest and smoke;
  - e2e preflight, the functional e2e (which produces the PDF cohort) and the visual e2e.
- Owned `down` commands are the same stock `compose down --remove-orphans`, so the executor's post-run assertion that the owned `-data` volume still exists is consistent.

**Executor (read in full; the literal diff changes only BASE/Q/F)**
- **Before any stop**, it checks:
  - retained identity, running/healthy status, the full mount multiset, network identity, the non-Env config hash, and credential stat 0600 (values never read);
  - the original graph verification: `461bf4840962`, 925/1,045, 410/515, partition and provenance valid;
  - no active readers;
  - namespace absence;
  - the full 3,307-file source and all 53 indexes.
- **Stop:** one SIGTERM stop with no forced timeout, observed for 60 s. If it doesn't complete, it records `STOP-INCOMPLETE` and does no CI and no restart. Once stopped, it confirms the ports are free on IPv4 and IPv6.
- **Each run:**
  - `root_ready` checks: namespace absent, no `.env`/credential, exact HEAD and tree, clean status (guarded), override and resolved-config hashes, Node v22.22.3, ports free;
  - it captures the owned graph container's identity while CI runs;
  - CI2 starts only after CI1 exits 0 and CI1's namespace is down (container and network gone, volume retained);
  - afterwards the tree must be clean and unchanged.
- **Finally:**
  - if a CI process is still live, it records `RECOVERY-DEFERRED` and makes **no** Docker mutation;
  - otherwise: owned `down`, inventory, ports free, `docker start` of the **same** container ID, wait up to 240 s for healthy, then full identity plus original-graph verification;
  - the 53 indexes are re-asserted.
- Every failure writes a record and re-raises. There is no retry, force or cleanup.
- Git inside the executor inherits `GIT_OPTIONAL_LOCKS=0`.

**Safety of the graph clear**
- `make ci`'s `clear` targets `--target compose` using the root's fresh credential. It runs only after the retained container is stopped and ports are proven free, and the override binds 127.0.0.1 only.
- The retained database (fresh credential mismatch, and stopped) cannot be the target.

**PDF commands**
- Raster and strict argv differ from the accepted recipes only in:
  - container names `ior-s19-final-r2-ci{1,2}-pdf-{raster,strict}`;
  - the sealed-cohort, rendered and strict mounts under `E/s19/ops-ci-runtime-r2/ci-root{1,2}-pdf/`;
  - the strict `/workspace` mount, which now points at the sanitized `r1-source` (3,306 files; no credential-bearing post-CI root is mounted).
- Pinned image, network none, read-only inputs; renderer `80f17b6f…` and checker `a68250a4…` unchanged.
- The preconditions and manual rule require:
  - an own 225-file seal per root;
  - 44 fresh first pages per root;
  - appendix reuse only through exact same-report/page image lineage;
  - no pre-freeze or other-root substitution.

**Point-in-time state, read-only**
- The retained container `42216eec…` (`/ior-aura-operator-proof-20260923`) is running and healthy, with ports 7475/7688 bound on all interfaces.
- No `s19-ops2*` containers, volumes or networks exist. Only the retained container's two listeners are on those ports.
- No CI, e2e, pytest or R1 process is running.
- Both CI roots are at HEAD `29bf5db5`, tree `7c25b46`, clean status, with no `.env` or `.secrets/`. Every CI by-product location is ignored (`.artifacts/`, `.secrets/*`, `*.log`, `.venv/`, `__pycache__/`).
- `nproc` = 1.

### B.2 Genuine blockers
None.

### B.3 Execution conditions (the root release must record these)
1. **GO record and executor finalisation.**
   - The GO record's `bindings` must include this review's hash; the proposal `140df801`; PDF commands `89562d8b`; the executor draft `7bbc0dce`; both overrides; the BASE prepause copies; `FINAL-SOURCE-INVENTORY` `f906a444`; the 53-index union `bd5a0be2`; e2e `RESULT` `0d186b92`; R1 `COMPARISON` `9c74e0df`; and R1 closure `76632a0f`.
   - Fill in only the two placeholders in the executor. Record its final hash and the placeholder-only diff externally.
2. **Nothing else running.** From the pre-pause checks until the retained container is restored and verified, run no other browser, raster, CI or service workload (one CPU).
   - The only exception: copying and sealing root 1's 225 producer files while CI2 runs.
   - Renderer, strict and manual work for both roots happens only after restoration and verification.
3. **Launch-time rechecks happen inside the executor, unchanged.** Any assertion failure stops the run before the stop step.
4. **If the stop does not complete (`STOP-INCOMPLETE`).**
   - Don't leave the retained service silently down.
   - Record its observed state, then obtain a separately reviewed recovery (start the same ID only after the stop is confirmed, then verify identity and graph).
   - Do not start any CI.
5. **If recovery is deferred because CI is still live (`RECOVERY-DEFERRED`).**
   - Wait for that CI process to exit.
   - Then do the owned `down`, confirm ports free, `start` the same ID, and verify identity and graph, under a separately recorded recovery step.
   - No global cleanup and no volume removal.
6. **Seal each root's cohort.** Immediately after each root's CI exits 0, copy and hash that root's 225 files from `.artifacts/e2e/pdf` into its sealed input (44 PDF, 44 HTML, 44 summary, 44 layout, 22 analysis, 22 dossier, 5 record-associations; derive the actual counts).
   - Then, in order per root: raster, strict (exit 0 with `issues: []`), then fresh manual review of 44 first pages with appendix lineage.
   - Create each output directory fresh, empty and owned 1000:1000. No `.png`/`.txt` sidecars in `rendered/`.
7. **Failures.** Any nonzero exit preserves all partials and stops. No replay, no retry, and no substitution of another root's or a pre-freeze PDF result.
8. **After everything:** rehash the 53 indexes, both roots' trees and status (guarded), and `r1-source`. Confirm the owned namespaces are down, the owned volumes retained, and the retained container healthy with the original graph verified.

### B.4 CARRY
- Independent adjudication of both CI results and both roots' 44-PDF proofs.
- Then targeted implementation closure, exact-head review, delegated acceptance, GitHub/main, and Aura.
- The retained container publishes on all interfaces (`HostIp ""`). That is pre-existing and outside S19. Note it for the later Aura/operator hygiene review.

## Sanad
**Direct:** every hash above; the e2e and R1 logs and results; my full diff of the eight phase files; the argv equality checks; the full executor read and its literal diffs; the proposal draft-to-final diff; the Makefile and compose reads; the PDF argv diffs against the accepted recipes; read-only Docker, port and process state; the guarded Git root checks; the 53-index rehash.

**Attributed:** the root executions of e2e and R1; the prepause graph verification using the existing credential reference; the offline results `1f2be1cf`.

**Assumptions, stated:**
- Docker and the retained container behave as they did in the earlier S18b execution of this method.
- The retained graph's health returns within 240 s.

**Unrun:** CI, PDF and every recovery step.

## Muhasabah
- **Khawatir (first framing):** "Same method, new names, so GO." Not enough on its own.
- **Muraqaba (watching for bias):**
  - I re-derived the R1 pass from the raw phase files instead of trusting `pass: true`.
  - I checked the volume, network and `git status` post-conditions against the actual Makefile and ignore rules.
  - I checked that the destructive `clear` cannot reach the retained database.
- **Mujahada (the actual work):** surfaced the stop-incomplete and deferred-recovery states that leave the service down, now conditions 4 and 5, and the single-CPU sequencing, condition 2.
- **Gate:**
  - Provenance: PASS.
  - Fabrication: PASS. No CI or PDF result is claimed.
  - Requirements: PASS. Both verdicts, hashes, conditions and CARRY are given.
  - Risk: read-only; the indexes were preserved.

Nothing was written. Save this text externally.
