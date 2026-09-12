# S12c implementation log

## 2026-09-12 — T0 preflight

Persona: senior data-provenance engineer implementing deterministic bilingual entity resolution under the governed Core contracts. Data classification: PUBLIC; no network, no `.env` access, and no protected data.

Branch `slice/s12c-entity-resolution-bilingual-ids`; HEAD/base `a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941`. Approved immutable plan `plan-1-dispatch1.json` SHA-256 verified as `6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd`.

Initial T0 stopped correctly when verification [6] found ignored `browser_tests/__pycache__/harness.cpython-312.pyc`. Owner lead established that it was bytecode left by an earlier browser-test run and relocated every repository `__pycache__` directory intact to `/tmp/ior-s12c-bytecode-recovery/`; no product file was touched. On owner instruction, [6] was re-run and passed with `FROZEN_ROOTS_UNCHANGED`; [5] was re-run and passed with `S11_S12A_S12B_BYTES_UNCHANGED`. All subsequent shell commands set `PYTHONPYCACHEPREFIX=/tmp/ior-s12c-bytecode`.

Previously observed before the environment stop: [0] `BRANCH_OK`; [5] `S11_S12A_S12B_BYTES_UNCHANGED`; [7] `BYTE_IDENTICAL_SET_OK`; `INTEGRITY PASS`; reconstruction `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)` and `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`; `data/documents/TEST-FIXTURE/records` file-free. These are re-verified as required before T0 closes.

## Execution ledger

- T0: complete — resumed after the owner-confirmed bytecode-environment correction; [0], [5]–[9], baseline pytest, reconstruction, integrity, and the TEST-FIXTURE file-free check all passed.
- T1: complete — versioned rules, fail-closed loader, and exact/variant normalization implemented test-first; [1], [2] first-file gate, and [7] passed.
- T2: complete — deterministic IDs, exact mention-list contracts and verbatim verification, JSON pointers, and EntityStore root/write-once primitives implemented test-first; exact [2] and [7] passed.
- T3: complete — resolver precedence, artifact builder/validator/reconstruction, passport/observation links, ownership records, and frozen-scope boundaries implemented test-first. IAC-8 [3] subset, [2], [7], and [10] passed.
- T4: complete — offline CLI/Make dispatch, three-line reconstruction discipline, manifest enumeration source, repository loader/cache, and integrity partition probes implemented test-first. Exact [3]–[11], [24], and [26] passed; Core contract test remains the planned W2 until T6.
- T5: complete with planned W3 open until T7 — `mentions-v1` contains 38 builder-verified spans; final artifact SHA-256 `97e68dd3e79b0ec1acb01bcdb5c5695296ba3d917f639afbd4079702d052f701` (57,033 bytes). [4], [12], [13], and [3] passed; artifact oracle 4/5 tests pass and the sole W3 failure is the two not-yet-authored KL citations.
- T6: complete — additive, marker-preserving governed Core 04/05/03/09 text authored under DD-10; [21], [22], [23] passed and W2 closed.
- T7: complete — ADR-018 authored before generation with S12c manifest count 0; KL-45/KL-67–73, runbook, progress, traceability §O, roadmap and state updated with facts only. [25] passed and W3 closed.
- T8: complete — filtered pre-generation regression `2008 passed, 1 deselected, 1 warning`; exact [0]–[13] and [21]–[26] all exited 0. Manifest run count remains 0.
- T9: complete — the one authorized manifest generator invocation ran at `2026-09-12T11:25:47Z`, exit 0; immediate [14] passed with two entity rows added and all prior rows unchanged; the generated seventeen-row authority table was mirrored into Manifest §11. S12c generator authorization is exhausted.
- T10: complete — [14]–[20] and [21]–[26] passed; full pytest `2027 passed, 1 warning`; `make ci` exit 0 with 118 functional and 4 visual Chromium nodes. Final [5]–[7], plan hash, diff check, plan file-set comparison and empty-index checks passed. Candidate identity `c2370180494658f0e845584e39c212994d7c2f594efe5044142a5bd275e88649` over 38 non-slice-record files.

## Muhasib self-audit

- Scope: actual 38-file candidate set equals the approved plan set; no unexpected or missing path.
- Authority/evidence: all real spans were copied from and re-verified against stored public inputs; no synthetic value enters the real artifact.
- Protected state: [5]–[7] pass after `make ci`; `.autonomous-workflow/**` and the Git index are unchanged.
- Manifest discipline: exactly one S12c generator invocation, after ADR-018/T8; immediate [14] passed; no rerun.
- Verification: reported counts and outputs are copied from executed commands. Assumption limited to the owner lead's stated provenance for the relocated T0 bytecode directory.
- Approval boundary: this is uncommitted implementation evidence only; independent reviewer approval, PR, CI and merge are not claimed.

## RED/GREEN ledger

- T1 RED — `pytest -q tests/test_entity_normalisation.py`, exit 2: collection failed with `ModuleNotFoundError: No module named 'ior_mvp.acquisition.entities'`, proving the planned package is absent.
- T1 GREEN — `pytest -q tests/test_entity_normalisation.py`, exit 0: `23 passed in 0.07s`.
- T2 RED — `pytest -q tests/test_entity_ids.py tests/test_entity_mentions.py`, exit 2: collection failed because the planned `entities.ids` and `entities.mentions` modules did not exist.
- T2 GREEN — `pytest -q tests/test_entity_ids.py tests/test_entity_mentions.py`, exit 0: `27 passed in 0.12s`; exact verification [2] then passed with `50 passed in 0.16s`.
- T3 RED — `pytest -q tests/test_entity_resolution_builder.py tests/test_entity_resolution_boundaries.py`, exit 2: collection failed with `ModuleNotFoundError` for the planned `entities.resolver`.
- T3 GREEN — resolver/boundary suite passed `30 passed in 0.09s`; IAC-8 gate [3] without the not-yet-created CLI file passed `213 passed in 4.78s`.
- T4 RED — CLI/wiring/core-marker selection run, exit 1: 11 failed and 3 passed, exposing the absent parser/dispatch/Make/reconstruction/repository/manifest wiring; the Core contract test is intentionally W2 until T6.
- T4 GREEN — wiring selection `13 passed in 0.59s`; exact [3] passed `225 passed in 5.31s`; pre-generation reconstruction printed all three PASS lines with `(0 artifacts, 0 links)` for entities.
- T5 initial real build — `make build-entities MENTION_LIST_ID=mentions-v1`, exit 0. Mention list `a12e24c31b02f11a0a7e116760b8a80814ddd97241716651c8cc60184ca1cc83` (21,091 bytes); initial artifact `ENTITIES-2026-09-12-a12e24c31b02`, SHA-256 `6e4f02139df922ab1003c886159f829532f43d5dd53a29d64d435b15fc2b82de` (57,984 bytes). Entity and mention-link DD-14 counts matched, but passport counts exposed two extra UNRESOLVED rows for unaddressed `/evidence/0/source` values.
- T5 resolver correction RED — `test_passport_links_cover_every_input_passport_exactly_once`, exit 1: expected two document/addressed-snapshot passports, observed three. DD-8 permits frozen-snapshot passports only when the `/evidence/<i>/source` is addressed by a `PUBLISHER_NAME` mention.
- T5 resolver correction GREEN — same test, exit 0: `1 passed in 0.04s`. The uncommitted initial artifact is removed before rebuilding from the unchanged, already-verified `mentions-v1`; this is a resolver correction, not a mention-list correction.
- T5 second build — same exact Make command, exit 0; artifact SHA-256 `d41004fb411561088ddde2bbd5f900c4059e1c9dcc48ab0037275d0736c7b1c0` (56,999 bytes), with corrected passport counts EXACT 10 / UNRESOLVED 8.
- T5 artifact-oracle RED — `pytest -q tests/test_entity_resolution_artifact.py`, exit 1: 2 failed, 3 passed. One failure correctly holds W3 open until T7 for the two verification-statement KL citations. The other proved that repeated exact plant mentions M-013/M-014 linked correctly but were not added to each plant's `evidence_mention_ids`; resolver corrected before another build.
- T5 final rebuild — same exact Make command, exit 0; DD-14 entity/link counts and DD-8 passport counts unchanged and correct, with plant evidence complete. Artifact oracle now has only the planned W3 failure: `1 failed, 4 passed`.
- T6 GREEN — `test_s12c_core_v2_entity_contracts` changed from planned W2 RED to `1 passed in 0.02s`.
- T7 GREEN — real artifact oracle changed from planned W3 RED to `5 passed in 0.05s`; [25] printed `CONTROL_RECORDS_PRESENT`.

## T0 observed evidence

- Baseline `pytest -q`: `1928 passed, 1 warning in 21.75s`.
- Baseline reconstruction, exit 0: `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`; `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`.
- Integrity, exit 0: `INTEGRITY PASS`.
- [0]: `BRANCH_OK`.
- [5]: `S11_S12A_S12B_BYTES_UNCHANGED`.
- [6]: `FROZEN_ROOTS_UNCHANGED`.
- [7]: `BYTE_IDENTICAL_SET_OK`.
- [8]: `51 passed in 1.57s`.
- [9]: `SMOKE PASS`, with frozen public outcomes Steel `INVESTIGATE` and Polypropylene `REJECT generic capacity`.
- `data/documents/TEST-FIXTURE/records`: `TEST_FIXTURE_RECORDS_FILE_FREE`.
- Manifest generator invocations: 0. Git staging/commit/push/stash/reset/checkout operations: 0.
