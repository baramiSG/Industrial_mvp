# Independent operation review: S19 D-S19-1 replacement generation unit

**Verdict: APPROVE (GO)** for releasing exactly one generation allocation under proposal `9ae96e6230fa1621b108e40ea3be4dbfd21cbc51f2f36a375389c3273039dc54` and source ledger `c99cdafa8b4d37085fe80c6ddf6b5ceac2a4ae91d8efdd9827633244160065b7`. The unit is one stock graph write, one stock manifest build, the five immediate gates, then the admitted token and three count literal edits.

I found no genuine blockers. The binding, the preservation controls and the stop-on-failure controls are enough for the delegated owner to release this one unit. Below are four execution conditions and some downstream CARRY items. None of them requires changing the proposal's bytes.

This GO does not cover canonical capture, the functional run or the all-44 PDF proof, R1, pins, the final candidate, CI, GitHub or Aura. It does not state 730 or the emitted IDs as results; both remain expectations until the operation actually runs.

**Reviewer:** Claude Code, `claude-opus-5-5`, read-only plan mode, tools limited to Read/Glob/Grep/Bash. I found no API-key variable in the environment. The subscription auth comes from `CLAUDE-COMMAND.json` (brief SHA `3c152614…`, which I verified). I ran no tests, no generator, no service and no agents, and I wrote nothing, including the plan file.

**Personas:**
- Release/change-control auditor
- Graph-projection determinism reviewer
- Test-literal and provenance auditor

**Skills read and applied:** project-orientation, task-standards, strict-reviewer, sanad-provenance, al-muhasibi, muhasabah-gate.

## 1. Bound subjects (hashes I computed)

| Subject | SHA-256 | Match |
|---|---|---|
| `GENERATION-OPERATION-PROPOSAL.json` | `9ae96e62…3039dc54` | ✔ brief |
| `GENERATION-SOURCE-BINDING.json` | `c99cdafa…160065b7` | ✔ brief/proposal |
| `S19-REPLACEMENT-OPERATION-DRAFT-r2.json` | `939830a3…19537` | ✔ proposal |
| `PRE-GENERATION-RECORD-DELTA.json` | `71991581…6ebd6ad` | ✔ proposal |
| Prior source review | `7e78bf3b…6e867` | ✔ |
| Source-readiness acceptance | `f2f1d767…1689c8` | ✔ |
| Mandate / delegated decisions | `9b91aba9…` / `9972f5fb…` | ✔ |
| Base-adoption amendment 09 (W and copy) | `5d058300…4501f` | ✔ |
| Corrected / predecessor observations | `2bf2bd78…` / `f8ec20b8…` | ✔ |
| `GRAPH-SEMANTICS-RESULT.json` / `comparison.py` | `398214bd…` / `eebc60a2…` | ✔ |
| `INITIAL-INDEX-BINDING.json` | `1c5e2862…` | ✔ |
| Reused recipe `ops-generation-r1/OPERATION-PROPOSAL.json` | `65ccd005…` | ✔ |
| Addendum / completion review | `51cd644c…` / `9b83fef2…` | ✔ |

## 2. Checks I ran myself

**Source ledger (worktree W = `/home/barami/projects/ior-worktrees/s19`)**
- All 1,759 ledger rows match W's bytes. I checked this at the start and again at the end.
- W's git-visible file set (`ls-files --cached --others --exclude-standard`) is exactly those 1,759 paths.
- HEAD is `ce407db…` on `slice/s19-bilingual-dossier`, with 0 staged paths.
- Compared with the parent ledger `5688e75d…`, exactly three paths differ: ADR, `implementation-log.md` and `plan-review.md`.
- For each of those three files:
  - the `pre-records` copy equals the recorded `before` hash, the parent ledger row and the unchanged source copy;
  - W equals `after`;
  - W's bytes begin with the whole original, so the changes are append-only (+3,761, +2,360 and +1,477 bytes).
- The source-readiness copy still matches all 1,759 parent-ledger rows.

**The 230 graph inputs**
- I re-implemented `discover_inputs` (`graph/projection.py:226-315`) as a pure glob. It finds exactly 230 paths in both W and the copy: none extra, none missing.
- All 230 rows match W's SHA and byte size.
- The inventory serialization hashes to `6f43b1a8c4aa…`, which equals `projection_id()` (`artifact.py:42-57`), giving the ID `GRAPH-SAU-2026-09-12-6f43b1a8c4aa`.
- None of the three record-delta paths or the five literal/pin test files is a graph input.

**Deltas against earlier projections**
- Against delivered `49b458a614f3` (from `ce407`): 220 unchanged, 8 changed, 2 added, 0 removed. The recorded before/after rows are exact.
- Against stored `ccd1`: 229 unchanged, and only `dossier.py` changed (`0e74a4f0…` → `34f20faa…`).

**Observations**
- The corrected graph, serialized the way `_json_bytes` does it (indent 2, sorted keys, trailing newline), gives 2,216,176 bytes with SHA `85b166d6…`.
- It shows 925 nodes / 1,045 edges and engine `ENGINE-6b54371e99f3`, and its input array equals the 230-row inventory.
- The predecessor observation equals delivered `49b4…/projection.json` byte for byte (`6292b1bc…`), which is direct evidence that construction is deterministic.

**Generator code**
- `write_projection` (`artifact.py:331-368`) writes a write-once directory with `projection.json` and `manifest.json`, then `current.json`. If the directory already exists with different bytes, it raises a conflict.
- `build --check` (`cli.py:38-42`) compares against the current pointer.
- `build_manifests.py` writes exactly `snapshot_manifest.json`, `authority_hashes.json` and the Manifest table.
- The three gate scripts I scanned (`verify_integrity`, `validate_scenarios`, `reconstruct_snapshot`) contain no write, git or subprocess calls.
- The commands and gates match the reused recipe and the Makefile's `UV_RUN` / `UV_RUN_GRAPH` exactly. The proposal only adds `UV_OFFLINE` and `UV_NO_PROGRESS`.

**Six-path output envelope**
- The envelope matches the stock writers exactly.
- I simulated the manifest builder in memory against W today:
  - it reproduces the current 728 rows in the same order and content;
  - adding the new pair gives 730, with 19 graph rows;
  - the 20 authority rows equal `authority_hashes.json`;
  - the regenerated HASH_TABLE text is identical;
  - there are no CR bytes.
- W's `generated_on` is already 2026-09-25, and local TZ is UTC. A same-day run therefore leaves `authority_hashes.json` and `00_AUTHORITY_MANIFEST.md` byte-identical. That is allowed; the proposal says those two "may remain" unchanged.

**Preservation**
- All 16 existing projection files match the draft hashes in both W and the copy, and they are the only files in `projections/`.
- The four overwrite preimages and the canonical visual-manifest preimage match in W and the copy.
- `…6f43b1a8c4aa/` is absent in both.
- All 45 indexes match, including `.git/worktrees/s19/index`. I checked before and after.

**Literals**
- The only live count sites are `tests/test_integrity_contract.py:1298`, `tests/test_s17_generation.py:58` and `tests/test_s17_status_docs.py:33` (my grep for 726/728/730 across `.py` files found no others). All three currently read `728`.
- `browser_tests/test_graph.py:845` currently holds `new_token, old_token = "ENGINE-5e01ef7c4b9d", "ENGINE-7ae34188bdec"`. `5e01…` is the `ccd1` engine ID.
- No other test, doc or browser file references `ccd1a2abd05c` or `5e01ef7c4b9d`.
- `test_graph.py` is in the visual `source_tree`. The three count test files are not.
- Amendment:30–32 grants the token permission and two of the count permissions. :34 keeps the status-doc count and change_ref permission. :38–42 set the ordering and sensitivity rules.
- ADR-031 already records this literal boundary before the manifest build, as amendment:38 requires.
- Addendum-review:71 says "two" count literals; the proposal correctly counts three.

**Draft corrections**
- W's baseline directory has 130 files: 128 WebP plus `manifest.json` and `manifest.sha256`, which `visual_baselines.py:401` writes. Draft r2 lists 129 paths and omits `manifest.sha256`. The proposal's correction to 130 is right.

**Environment**
- `.venv` already holds the locked dev and graph packages: pytest 8.4.2, httpx 0.28.1, pypdf 6.16.1 and neo4j 5.28.4 (matching `uv.lock:442,714`). The editable egg-info is present, and the venv is newer than `pyproject.toml`.
- The only lock holder is PID 2413, which holds the flock on `delivery.lock`.
- An idle `cursor-agent acp` (PID 27387, running 6 days) has its working directory at the main repo root, not W.

## 3. Evidence I retained without re-running

- `GRAPH-SEMANTICS-RESULT.json`: all-11 real-decision and normalized-graph PASS. The prior Claude review re-ran it; I only confirmed its procedure and input hashes.
- That the corrected observation came from a "double" construction.
- The HANDOFF's locked offline sync dry-run.
- All test, mutant, print and 674-test results in review `7e78bf3b…`. I kept them for the unchanged subjects and did not reopen the label or appendix design.

## 4. Findings

**Genuine blockers: none.**

**Execution conditions** (the delegated release record should state these; they only make the proposal's own failure policy concrete):
1. **Check between the two commands.** The stock `build` command has no emit-without-write mode, so "confirm graph command emits bound SHA before consuming allocation" (preflight 5) cannot be done before the write. Pre-write assurance is the fresh re-check of the 230 inputs and discovery, plus the retained observation. Straight after `build`, and **before** `build_manifests.py`, verify:
   - the ID `6f43b1a8c4aa`;
   - projection SHA `85b166d6…` and 2,216,176 bytes;
   - engine `ENGINE-6b54371e99f3`, 925/1,045 and 230 inputs;
   - exactly two new files and `current.json` changed.

   Any mismatch stops the run with the manifests not built. Do not run any extra `build`, `--out` or tmp-root call to "confirm".
2. **Re-verify immediately before release:**
   - `c99cdafa…` against W;
   - all 45 indexes;
   - the new directory is absent;
   - exclusivity (lock holder alive, no writer in W).
3. **Environment:** run with UTC and do not force `generated_on`. If the run crosses midnight UTC, `authority_hashes.json` changes its date only; that stays inside the envelope and must be recorded, not treated as a failure. Keep `uv run` inexact and do not substitute `uv sync`, which would prune e2e packages. Record uv's stderr. A `.venv` change is outside the source ledger but must be reported if it happens.
4. **Literal edits only after proof:**
   - Count edits need the membership proof first: old 728 plus exactly the two new paths, with `current.json` the only changed row.
   - The `new_token` edit needs the actual emitted `engine_run_id` first.
   - Record the exact hunks and a new complete ledger after the edits.
   - `old_token` stays `ENGINE-7ae34188bdec`, and the three historical S17 assertions (status-docs lines 36 onward) stay untouched.

**CARRY (downstream, not part of this unit):**
- **Sensitivity check needs its own binding.** The isolated-copy CSS negative control (amendment:40–41) has no bound command, copy root or evidence path in this proposal. It must be bound (EN/AR steel, public, evidence-to-change, 1440; fail on the protected anchor; correct CSS passes; the `a1dcbf0e7665` alternate only after a recorded insensitive first result) and reviewed before the functional or canonical stages. This GO does not cover running browser tools.
- **`test_graph.py` rebinding.** Its new hash is a visual input. The later change_ref at `test_s17_status_docs.py:35` and the pin at `test_frozen_public_evidence_pins.py:48` (the untested `0bc664f2…` value is superseded) follow only after an accepted capture.
- **Full pytest not yet run.** Plan Task5 step 1's pre-generation full unit/browser run has not happened on these bytes. The approved addendum sequence and delegated decision (c) do not require it, and the proposal is honest that it is unrun. The residual risk is that a non-stale failure found after generation would need a new reviewed allocation.
- **Downstream obligations unchanged:**
  - all-44 strict and manual PDF proof, even though only the 4 steel HTML summaries change;
  - canonical capture with 130 outputs under change_ref `S19-BILINGUAL-DOSSIER-2`, released separately;
  - R1 against `ce407db` (`ENGINE-a1dcbf0e7665`);
  - records and freeze;
  - Task 6 gates and CI;
  - GitHub delivery;
  - Aura `8a7338e0`.

**Preference:** the preflight wording should say "confirm after the write, before the manifest build" rather than "before consuming allocation". This does not block.

## 5. Sanad

Every PASS above rests on direct reads and SHA-256 hashes I computed on W, the source copy, the records, the indexes and the code (`cli.py`, `artifact.py`, `projection.py`, `build_manifests.py`, the gate scripts, the amendment, plan Task5, and addendum-review :71/:93/:105), plus my in-memory simulations. The items in §3 are attributed to their records and I did not re-run them.

## 6. Muhasabah

- **Khawatir (first framing):** "Hashes match and the recipe is stock, so GO." I rejected that as not enough on its own.
- **Muraqaba (watching for bias):**
  - Where I might trust the coordinator's inventories, I re-derived discovery, the deltas, manifest membership and the authority rows independently.
  - Where I might copy the old "authority rows change" postcondition, I confirmed the rows are unchanged.
  - The "two literals" wording in the addendum review was corrected to three.
- **Mujahada (the actual work):** this is what surfaced the build-before-check sequencing gap, the unbound sensitivity check and the date/timezone detail.
- **Gate:**
  - Provenance: PASS.
  - Assumptions, stated: output is deterministic (supported by the byte-exact predecessor reproduction); a same-day UTC run.
  - Fabrication: PASS. No emitted ID, count or gate result is claimed.
  - Requirements: PASS. Verdict, hashes, conditions, CARRY and the checked-vs-retained split are all given.
  - Risk: PASS. Read-only; W, the ledger and the indexes were unchanged at the end of the review (11:22 UTC).

**Pending:** the delegated release, the actual single run and its receipts, the literal-adoption review, and every downstream item.
