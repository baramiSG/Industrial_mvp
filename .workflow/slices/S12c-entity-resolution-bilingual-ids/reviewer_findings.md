# Independent reviewer findings — S12c Entity Resolution and Bilingual Persistent IDs

**Plan review:** `reviewer-grok` (cursor-grok-4.6-xhigh) — `plan-1-dispatch1.json` (SHA-256 `6370547f…`) **APPROVE**, zero findings, six advisories
(→ IAC-8…IAC-13); the reviewer verified all 38 real mention addresses verbatim and the JSON pointers into the frozen snapshots (`plan-1-review.json`).

**Implementation review:** `reviewer-grok` on candidate `c2370180494658f0e845584e39c212994d7c2f594efe5044142a5bd275e88649` (38 files, base
`a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941`, implementer `implementer-sol` slot 1) — **APPROVE, zero findings** (`implementation-review-slot-1.json`).
Independently executed: plan gates [0]–[19], [21]–[26] (all PASS; [20] `make ci` left to the owner lead agent), `pytest -q` 2027 passed, integrity,
scenario validation, smoke (steel public `INVESTIGATE`, steel simulated `ADVANCE` real unchanged, PP public `REJECT`), reconstruction (1/4 + 12/12 +
1 entity artifact/38 links), byte identity of every frozen path and the tamper/pin tests. Independent oracles without importing the new package: all 38
mention spans verbatim at their addresses; artifact counts exactly DD-14 (5 COMPANY, 2 SITE_LOCALITY PLANT, 0 LINE, 0 LICENCE_HOLDER; 27 EXACT / 3
pending / 8 unresolved; 0 DETERMINISTIC_IDENTIFIER; one 2004 unnamed-owner record; two documents without mentions); `ENTITY_ID_V1` ids recompute; verbatim
spans retained; visual-order Arabic not reversed; no personal name under `data/entities/**`; passports EXACT 10 / UNRESOLVED 8, observations EXACT 5,
`S-UNICOIL-EPD` corroborated by `DOC-PRODUCER-UNICOIL-70151205e3a4-1762d53d6cab`; two-process reconstruction identical (`97e68dd3…`); authority path set
17 = 16 + `config/entity_resolution.v1.yaml`; §11 equals `authority_hashes.json`.

**Advisories (non-blocking):** S12C-IR1-A01 — the latest S12c prose in `docs/BUILD_PROGRESS.md`, `docs/BUILD_ROADMAP.md` and
`docs/REQUIREMENTS_TRACEABILITY.md` still reads as pre-generation although ADR-018, the runbook and `state.json` record the single manifest run at
2026-09-12T11:25:47Z — corrected in the post-merge records PR. S12C-IR1-A02 — the unnamed owner is represented by null owner fields plus
`description_text` per DD-7's exact key set (no `unresolved_reason` on ownership records) — accepted as designed (KL-72).

**Stated limits:** the reviewer did not run `make ci` or the browser tests; the owner lead agent ran `make ci` on the identical tree (exit 0; 2027 tests;
118 functional + 4 visual) and hosted CI runs the full matrix on the PR head.
