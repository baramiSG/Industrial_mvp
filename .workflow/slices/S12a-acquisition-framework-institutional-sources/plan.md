# S12a approved implementation plan

Complete immutable plan: `.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json`.
SHA-256: `b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64`.

Owner ruling: `.autonomous-workflow/owner-decisions/20260911-owner-direct-s12a-implementation.md`, SHA-256 `5e39caf77cd045a160bd1c6af075b83eb725c2d49e59d3f8a6d6d1b2efaef40c`.

Original plan-4 and original reviewer approval preserved. Canonical commands [4], [5], [12], [17], [20], [26] copied directly from verified JSON strings, exact UTF-8 equality checked. [22] explicitly superseded by owner ruling. Implementation follows T0–T12 with approved amendments; no unrelated defects are absorbed.

No database or migration is introduced. Three new snapshot schemas are version 1.0.0; source configuration advances to 1.1.0 with S11 mappings and per-kind 1.0.0 provenance preserved. Exactly one manifest generation after T10 and ADR rationale, never before.
