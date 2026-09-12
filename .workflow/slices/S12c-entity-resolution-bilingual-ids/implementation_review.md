# Implementation review — S12c Entity Resolution and Bilingual Persistent IDs

**State:** independently APPROVED (zero findings); owner acceptance recorded (OD-10); delivery in progress.
**Data classification:** public documents already in the governed store, frozen public snapshots (read-only) and test doubles; no personal name enters
`data/entities/**` (the 1997 founding-shareholder sentence is deliberately not harvested); `.env` never read; no network in this slice.

## Governed trail

- Plan: `plan-1-dispatch1.json` (`6370547f…`) by `planner-fable`; `reviewer-grok` APPROVE; owner rulings OD-1…OD-8; OD-9 started the ladder at
  `implementer-sol` for cause (s12b history). An interrupted first planner wait and a second bounded dispatch produced an alternative plan
  (`plan-1-dispatch2.json`, archived, not gated).
- Implementation: `implementer-sol` slot 1 — T0 stop on an ignored bytecode file inside a frozen root (relocated by the supervisor; before/after evidence
  in `plan_review.md`), then T0–T10 complete: 68 plan-named tests, one manifest run (2026-09-12T11:25:47Z, ADR-018 first), candidate `c2370180…`.
- Independent review: `reviewer-grok` APPROVE, zero findings, two non-blocking advisories (`reviewer_findings.md`).

## Owner acceptance (lead agent, 2026-09-12)

- Identity recomputed after the review: exact match; index empty.
- `make ci` on the identical tree: exit 0 — scanners, `INTEGRITY PASS`, scenario validation, `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`,
  `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`, `ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)`, 2027 tests, `SMOKE PASS`,
  118 functional + 4 visual Chromium nodes.

## Truthful delivery limits

- The real artifact resolves 5 companies (Universal Metal Coating Company alias UNICOIL from exact document spans; Hadeed, SABIC, Advanced Petrochemical
  and Tasnee from frozen-snapshot short labels with legal names unresolved) and 2 UNICOIL site-locality plants (Al-Jubail, Jeddah); no production line,
  licence holder or deterministic identifier exists in the acquired evidence; jurisdiction and Arabic primary names are UNAVAILABLE; three mentions are
  held `PROPOSED_PENDING_REVIEW`; the six SASO passports are `UNRESOLVED/OUT_OF_SCOPE_ENTITY_TYPE`.
- No engine, screening or graph consumption (KL-45 analogue); frozen public/synthetic/golden data, S11/S12a/S12b evidence and browser baselines
  byte-identical to the base.
