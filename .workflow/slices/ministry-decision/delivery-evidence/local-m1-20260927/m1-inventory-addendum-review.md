**Verdict: APPROVE the M1 inventory addendum**, SHA-256 `4a6e0aa7d1da56449c9a4ac89ae08bf85d63563e8493342fc15a6448b443d746`, with one binding condition. This approves the plan amendment only; no implementation, successor or gate is approved. Everything was read-only against frozen proof 241e4df / fe98722, and I did not touch the lease, credentials, Git or services.

## Verified directly

- **The saved c9841fe8 artifact has exactly seven public `PRODUCER_DISCLOSURE` ADJACENT_TO rows:** two steel, three PP and two aluminium.
  - Aluminium ALUPCO: `COMPANY-69d10bdb78064a59`, key `REL-86e0f9feaada056b9067`.
  - Aluminium TALCO: `PRODUCER-public-sau-h6-760429-2026-09-12-2`, key `REL-514c0b83c09734657191`.
  - Both aluminium rows currently read `same_process_family: true`, `FULL`, `fired: false`, count 0, `NO_DEFENSIBLE_SIGNAL`, with no owned signals, exactly as the addendum states.
- **The source records confirm the labels.** Both producers carry `process_family: fabricated_aluminium` in `data/cases/briefs/CASE-BRIEF-SAU-H6-760429-v1.json` (`6ce58c44…`, matching the addendum) and in `data/snapshots/public/PUBLIC-SAU-H6-760429-2026-09-12.json`. The case is HS 760429 with sector `fabricated_aluminium`.
- **The governed family covers it.** `config/product_families.v1.yaml:32` defines `fabricated_aluminium`, which includes heading 7604, so `family_for_hs6('760429')` resolves to `fabricated_aluminium`. With the exact alias `fabricated_aluminium → fabricated_aluminium` these rows stay true, the same as today. That is source-backed, not a new inference.
- **Without the third alias, the approved correction would have made an unapproved change.** It would have turned these two known rows from true to null/DISABLED, contradicting M1's "exactly three PP edges change" requirement.
- **Correction to my own earlier M1 verdict.** My scan there globbed `data/snapshots/public/SAU-*.json` and missed the `PUBLIC-*` snapshot and the case brief. Its conclusion still holds: only PP is currently wrong, because aluminium's source label happens to equal its sector string. But its statement that "no other public snapshot has producer evidence" was incomplete.

The complete producer-label inventory across the public snapshots and case briefs is exactly three labels: `coated_steel`, `polypropylene` and `fabricated_aluminium`.

## Binding condition

1. **The completeness regression must use the same source the build uses.** Enumerate every producer `process_family` label from the actual public-analysis input path used by `build_repository_projection`: the repository case loader's public snapshots and reconstructed briefs. Filename globs miss files, as mine did. The test must fail if any label lacks an exact alias, and it must not pin a literal count that could silently absorb a new unmapped fixture.

All other M1 and addendum limits stand:
- exact case-sensitive aliases, with no identity fallback, fuzzy matching or sector comparison;
- the UNKNOWN and same-sector conversion negatives;
- the aluminium preservation regression on the two exact rows;
- the successor may change exactly three PP edges and five leaves, with every steel, aluminium and other element equal after identity normalization;
- the two unchanged screening helpers join the input closure;
- a strict R1 failure means STOP, with no M-A4 waiver.

**Muhasabah: PASS.** The rows, labels, brief hash and family membership were read directly. I've disclosed and corrected my earlier scan's gap, and successor outcomes remain prospective.
