# Reviewer Findings — S14b Deep-case Portfolio, Scenarios and Goldens

Reviewer seat: `reviewer-grok` (cursor-grok-4.6-xhigh), the independent approver for the S14 plan and both S14 children. Verdict evidence is retained locally under `.autonomous-workflow/evidence/s14-deep-cases-a/`.

## Plan and amendment reviews

- Base plan `plan-1-s14b.json` (`af5ae5d8…`): REJECT — the plan omitted the pinned-module obligations deferred from S14a (PublicSnapshot 2.2.0 partner carrier, R3/R4-D state reasons and dossier labels) and its SC-9 integration test would reject a correct S14a AM-2 carrier.
- AM-1 `8dc1b75d…`: APPROVE, zero findings. It made the 2.2.0 carrier additive and version-gated, kept the frozen 2.1.0 snapshots intact, carried the deferred work inside the single visual regeneration, and accepted either the observed or missing S14a partner state where the passport encoding is correct.

## Implementation reviews

- Candidate `6307ccb3…` (121 paths, integration parent `1289e31`, W2' base `5354a6f`): REJECT — S14B-IR1-F01. `docs/core/04_CANONICAL_DATA_MODEL.md` §12 named fields that did not exist in the validated 2.2.0 `partner_detail` carrier and omitted actual required fields. The reviewer independently confirmed all other candidate obligations: builder-derived public snapshots, public/synthetic isolation, scenario outcomes, visual pins and inspected views, manifests, route matrix, Arabic parity and the 2,549-test suite.
- Corrected candidate `24c3b3cc219168dae4b1d720f7913cc71a31217ff6eafc0dccd39172335c3a38` (same 121 paths): APPROVE, zero findings. The correction delta was exactly Core 04, its contract pin, ADR-022, authority hashes and the §11 mirror. Core 04 now lists the live exact keys in order: `state`, `reason`, `source_id`, `partner_snapshot_id`, `unit_key`, `observed_partner_rows`, `attempt_passport_ids`, `observed_passport_id`; the obsolete names are absent. The reviewer verified the RED/GREEN proof, the second/final manifest generation, 638 unchanged snapshot-manifest rows, authority set 19 with only Core 04 rehashed by the correction, portability and the exact scratch candidate.

## Independently recomputed facts

- Five derived public cases are `INVESTIGATE` with null route; the original steel public result remains `INVESTIGATE` and polypropylene remains `REJECT`.
- Gate B and the back-test computed: 721061 → simulated ADVANCE route 3; 721012 → route 7; 760711 → route 6; 760429 → route 4; 392010 → REJECT route 0. Synthetic evidence did not alter `real_decision`.
- PublicSnapshot 2.2.0 is additive; the two original 2.1.0 files remain byte-identical and reject the new carrier.
- The 76-entry visual manifest and baseline pin are valid; actual English and Arabic views and drift crops were inspected. W2' changed only the eight portfolio chips and seven Arabic decision-subject cards; the remaining 61 images stayed byte-identical.

The reviewer did not run the owner `make ci` gate; the owner did on the exact corrected candidate, and hosted CI ran the full matrix.
