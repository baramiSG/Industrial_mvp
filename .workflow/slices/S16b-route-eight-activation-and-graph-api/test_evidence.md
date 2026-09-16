# S16b verification evidence

Verified product subject: `fd047867bac64070ca776047281c3cfbe584065eeb3c55e4dab2feacf9596a1d`.
Verification commit: `c0d5ec2a873cda33d14adfff83ce717f01844dbf`; tree: `93d49154e28788d3a6067f09682bd6c08aaa3d7d`.

Both isolated verification and portability worktrees passed:

- Full pytest: 2,854 passed, zero failures, one existing deprecation warning.
- Functional Chromium: 498 passed, zero failures/skips.
- Visual Chromium: four passed, covering the 96-image matrix.
- Smoke, source/HEAD/tree/byte/mode checks.
- The unchanged-input static, integrity, 11-scenario/back-test, reconstruction and graph build-check/validation prefix was reused from the prior materialization; only one test file changed.

The local owned Neo4j mirror passed empty-before-clear proof, first load 925/1,045, second load 0/0, exact artifact verification, nine live tests including non-skipped route-8 equality, and two stopped-service tests. One `AURA_OPERATOR_ONLY` skip is not Aura evidence.

The separate owner Aura operation subsequently passed on `8a7338e0`: 925 nodes/1,045 edges, second load 0/0, complete provenance/partition, matching sample views, four catalogue entries, eight AVAILABLE and eight NOT_CONFIGURED application views. No Aura clear occurred. Sanitized receipt: `.autonomous-workflow/evidence/s16b-aura-pass-1.json`.

Visual manifest SHA-256: `91696291cbe4f17e49a479b72682c48278203ba8bcf691b75e163045382a8b79`. All 52 changed image pairs differ only within 6–7 by 10 pixel glyph rectangles consistent with threshold 1.2.0→1.3.0; the other 44 are identical. Total 14,721,036 bytes; maximum image 231,000 bytes. Original tolerances and matrix remain unchanged.

Public/golden roots and historical JSON/config/fixture bytes are retained. The previous 20 artifact-related unit failures and the two historical-partition failures are closed by actual full-suite results.

Complete local receipts: `.autonomous-workflow/evidence/s16b-final-verification-r2.json`, `s16b-artifacts-and-browser-1.json` and `s16b-materialization-2.json`. Record/status-only follow-up is separately inspected and does not stand in for product tests.
