# Independent disposition: S19 ordinary-index incident and exact-byte recovery

## Verdict: APPROVE
- **Q1. APPROVE:** the exact-byte restoration is accepted as the resolution of the index incident. The incident stays recorded as a preservation failure followed by a documented recovery. It must not be relabelled as "never happened", and no expected hash may be reset.
- **Q2. APPROVE:** the paused GPT-6 Sol correction writer may finish the already-approved prospective-union correction before freeze, under the conditions below.

No blockers. This is not candidate implementation acceptance, and I ran no operations. Every Git command in this review was run with `GIT_OPTIONAL_LOCKS=0`: `ls-files`, `diff --cached`, `rev-parse`, `symbolic-ref`, `cat-file`, `ls-tree`. I wrote no files. The review was interrupted once (exit 143, cause unknown per `CLAUDE-INTERRUPTION.json`); no verdict had been issued before this one.

**Personas:**
- Git index-integrity auditor
- release-provenance auditor

**Skills:** strict-reviewer, sanad-provenance, al-muhasibi, muhasabah-gate, task-standards and project-orientation, all from `/home/barami/.agents/skills` and unchanged.

## Bindings (hashes I computed; all match)
| Subject | SHA-256 |
|---|---|
| Brief | `bb12146aff09f71f42c08c40162044a4d438a1cd369859cd37e48fe642b85bbb` |
| `INCIDENT.json` / `INCIDENT.md` | `cd074a54…1f625` / `3f06c279…8ee2` |
| `ROOT-EXACT-INDEX-RESTORATION.json` | `ad62d301961967bbf7af725613097a4f6aeca8127e17d2c08e0466c7d265f00e` |
| Observed changed index copy (mode 0600) | `6451da67da6dbcf8344a897b806a4cbce20d75751185593c0659ec906cbb57e3` |
| Live `.git/worktrees/s19/index` now | `799d94a7b865644e0cd658e52687a9805224beb40c846f6403d0b87b3dd49722`, 272,314 bytes, mtime 14:01:58.600 (the restoration time; unchanged through my review) |
| Preimages `E/s19/index-stat-refresh-recovery-r1/observed.index` and `E/reviews/s19-canonical-other56-r1/W19-INDEX-OBSERVED-799d94.bin` | both `799d94a7…` |
| `final-assembly/baseline-pin.index` | `2a671f8c939f8cdbb207069212be0e17d35f55c4e80062ec2576b998ccf4c4e2` |
| `POST-ASSEMBLY-SOURCE-BINDING.json` | `2e006999624ba2ba3399aa0fcff6199de7d07991571c9e9ead2d7842b8e02ce4` |
| Assembly release | `33fa4570837bafb991872d7e3ec46c21f9dd91909b7db5df06da2b28f72d6e69` |
| `audit_once.py` | `7338b7e3e1bf1f4d995359ca34df9e159b49624d0908e415d8ddf0a8ffa7cf90` |

## Checks I performed myself

**What changed in the index, parsed at binary level (DIRC v2)**
- `799d` and `6451` both have 1,697 entries.
- Names, modes, blob SHAs, flags and extended flags are identical, and the `TREE` extension bytes are identical (27,570 bytes).
- Exactly **36 entries differ, and only in ctime/mtime/inode.**
- Those 36 are exactly the 36 baseline WebPs that are byte-identical to HEAD `ce407`, taken from the direct ce407 codec ledger.
- Git's stat-cache refresh only rewrites stat data for entries whose working file still matches the index blob. The 36 baselines are the files the capture swap replaced (new inodes and mtimes) with content still equal to the index blob. So the recorded causal inference, an unprotected `git status`, is strongly corroborated by the mechanism. The command's timestamp is still not retained, as the incident states.
- The logical entries in the restored index equal those in the observed index. Root's `ls-files --stage` and `-v` equality results are consistent with what I found.

**Restoration**
- The live bytes equal both independently retained `799d` preimages exactly. This is exact-byte restoration, not reconstruction.
- The changed bytes are preserved at `observed-index-6451da67.bin`.
- The file-level mtime and inode now reflect the restoration. That is disclosed in the restoration record and is not claimed as untouched.

**Preservation**
- All 45 protected indexes match `INITIAL-INDEX-BINDING.json`. The pin index is `2a671f8c…`.
- HEAD is `ce407db…` on `slice/s19-bilingual-dossier`, with 0 cached paths.
- All 3,227 rows of `POST-ASSEMBLY-SOURCE-BINDING` match W's bytes, and W's git-visible pathset equals that ledger.
- Compared with ledger `c104d456`, the 16 changed paths are:
  - the 6 accepted baseline files;
  - the 2 pin tests;
  - 8 record/doc paths (`.workflow/slices/S19…/implementation-log.md`, `plan-review.md`, `.workflow/state.json`, and five `docs/*.md` files).
  - Plus 1,466 added paths from the approved assembly.
- All 109 visual inputs and 2 fonts match r4.
- All 130 baseline files equal the accepted frozen capture (manifest `0d05eee7…`).
- All 230 graph inputs match the projection's recorded input hashes.

**Pin**
- `git ls-tree 65a71b38` shows `040000 tree 121e5622… v0.3.0`.
- My independent in-memory git-tree computation over W's 130 baseline files gives exactly `121e56221a2a1b41c6c144eb9a44cb9dfab3e4dc`.
- `tests/test_frozen_public_evidence_pins.py` pins `"browser_tests/baselines": "65a71b38…"`, and `test_s17_status_docs.py` contains `S19-BILINGUAL-DOSSIER-2`. Both are permitted assembly deltas.
- My first computation briefly appeared to mismatch because I had hashed one directory level too deep. I corrected my own error; it is not a finding.

**The 74 omitted logs**
- The physical approved delivery-evidence tree plus accepted packet 26, minus the git-visible set, is exactly 74 paths, all `.log`.
- The union is 3,301 paths.
- Every one of the 74 is bound in either the 1,000-row history selection or the 508-row replacement copy binding. Both the copy and its source match the bound SHA-256.

**Precedent**
- `799d` is itself the accepted result of an earlier, identical kind of stat refresh (from `fb883938`), dispositioned through `INDEX-DISPOSITION-REVIEW.md` and owner decision `…active-index-metadata-disposition-1.json`.
- This is therefore a **recurrence** of the same hazard, not a new kind of failure.

## Retained from earlier records, not re-run
- The command that caused the incident and its timing, from the incident record.
- Root's lock and atomic-replace procedure.
- Paused writer state and the root-held `delivery.lock`.
- The earlier `fb88` → `799d` disposition.

## Findings

**Genuine blockers:** none.

**Conditions for Q2 (continuation)**
1. **Git reads.** Every Git invocation by any seat must set `GIT_OPTIONAL_LOCKS=0` explicitly (or use `git --no-optional-locks`), including the first orientation command.
   - The restored `799d` again carries stale stat data for those 36 baselines. Any unprotected `git status` or `diff` will predictably reproduce `6451`-style drift.
   - Prefer `ls-files`, `rev-parse` and `diff --cached` over `status`.
2. **Rehash around the writer's unit.** Immediately before and after it, rehash the 45 protected indexes, the pin index `2a671f8c` and the live `799d`. Any drift means STOP and preserve. No self-restoration by the writer.
3. **Scope of the writer's unit:**
   - the explicit prospective 3,301-path union ledger;
   - the unchanged prohibited-content scan over that union;
   - the smallest truthful additive record notes.
   - No staging, force-add, `.gitignore` change, or edit to a graph- or visual-hashed file or baseline.
   - Only root may later force-add exactly these 74 bound paths, and only into the new freeze index.
   - If `audit_once.py` is reused, bind it at `7338b7e3…` or a hash-recorded revision whose only change is completing receipts. No new framework.
4. **Truthful chronology.** The candidate chronology and records must record both index incidents and their exact recoveries: `fb88` → `799d` earlier, and today's `799d` → `6451` → `799d`. Keep `INCIDENT.*`, the observed copy and the restoration receipts unchanged.

**CARRY (outstanding gates, not required for this disposition):**
- New complete ledger and scan receipts after the correction.
- Independent exact-tree freeze review.
- All Task 6 gates, delivered `a1dc` → `6b54` R1, two CI runs each with its own 44-PDF proof.
- Claude implementation, tree and head reviews, delegated acceptance, GitHub/main and Aura.

**Preference:** consider having the orientation step read `ls-files`/`rev-parse` only, never `status`, to remove the trigger for this recurring hazard.

## Sanad
**Direct:** every hash listed; the binary index parse and field diff; the 36-path identity join to the ce407 codec ledger; the ledger, pathset, visual, graph and baseline rehashes; the pin tree verified by git read and by independent computation; the 74-log binding joins; and the precedent records.

**Attributed:** the command timing and cause (inferred, not proven); root's restoration procedure; writer pause and lock state.

## Muhasabah
- **Khawatir (first framing):** "Hash is back to `799d`, so resolved." Not enough on its own.
- **Muraqaba (watching for bias):** I didn't accept that the index was "logically equal" on the basis of root's listing hashes. I parsed the binaries myself and tied the exact stat-refreshed set to the capture's byte-identical files. I also didn't let my own pin-hash slip stand as a finding without checking git's objects.
- **Mujahada (the actual work):** this is what surfaced the recurrence and the stale stat entries that will persist, which is why condition 1 is mandatory rather than advisory.
- **Gate:**
  - Provenance: PASS.
  - Assumptions, stated: nothing wrote to the index between my reads; I observed its mtime and hash stable before and after.
  - Fabrication: PASS. No earlier verdict or unrecorded timing is claimed.
  - Requirements: PASS. Both questions are answered with conditions and CARRY.
  - Risk: read-only; the index, the 45 protected indexes and the pin index were unchanged at the end.

Nothing was written. Save this text externally.
