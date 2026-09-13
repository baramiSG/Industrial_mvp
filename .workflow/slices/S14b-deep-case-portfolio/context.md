# S14b implementation context

## Identity and classification

- Worktree: `/home/barami/projects/ior-worktrees/s14b`
- Branch: `slice/s14b-deep-case-portfolio-scenarios-and-goldens`
- Preparation base: `ab6211f86307ad95a0e61f0597664023f09b7177`
- Data classification: `confidential_demo` — public evidence and visibly
  labelled Class-D synthetic scenarios only; no personal, private, paid, or
  Ministry data.
- Parallel mode: s14a remains uncommitted in the primary checkout. The primary
  checkout is read-only for the named in-flight `src/ior_mvp/cases/**`,
  `data/cases/**`, and S14a implementation-log artifacts used for provisional
  `/tmp` builds.

## Binding authority

Read in the governed order:

1. `AGENTS.md`
2. `docs/authority/00_AUTHORITY_MANIFEST.md` (§7, §10, §11 in particular)
3. authoritative methodology DOCX, SHA-256
   `5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9`
   (XML extracted read-only under `/tmp` because the file reader does not
   support DOCX)
4. `docs/core/04_CANONICAL_DATA_MODEL.md`
5. `docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md`
6. `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`
7. `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`
8. `config/thresholds.v1.yaml`, `config/sector_profiles.v1.yaml`,
   `config/evidence_policy.v1.yaml`
9. the approved plan, AM-1, owner rulings, plan reviews, decomposition, current
   code/tests, control documents, and the in-flight S14a implementation log.

Binding plan identities verified on 2026-09-13:

- base plan:
  `af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2`
- AM-1:
  `8dc1b75d5ce91ce041ed82798b5c00c9fb60e1f7c29fe985f40aa88385eca7c7`
- decomposition:
  `48741467ed2e3d6185cb0e5aac13b56d6c9d81847a3b114b960547740b877f3a`

AM-1 overrides the base plan wherever they differ. Reviewer-grok's AM-1
record is `APPROVE` with no findings and transfers the SUPERSEDED-prefix,
reason-set equality, no-migration, T4b-before-W1, five-authority-row and
one-manifest-run advisories.

## Preparation boundary

Authorized now: T0 through T4, then T4b on doubles. Stop at
`PREP_HANDOFF_W1_PENDING`.

Not authorized now:

- no integration or edits to `src/ior_mvp/cases/**`;
- no public snapshots under `data/snapshots/public/`;
- no visual regeneration or baseline writes;
- no manifest generation;
- no git state change;
- no network and no `.env` read.

Every Python run uses `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc`; project execution also uses
`UV_OFFLINE=1`, the worktree `.venv`, and `PYTHONPATH=src` (or the explicitly
authorized primary source path for provisional builds).

## Frozen boundary

The two frozen PublicSnapshot 2.1.0 files and `historical/v1/**` are never
migrated. PublicSnapshot 2.2.0 is additive and version-gated. Scenario files
remain untracked through this hand-off. Core 06 remains byte-identical.

## Deferred observations

- The authoritative merged-main `M`, the final 721061 AM-3 outcome, the
  first authoritative 2.2.0 hashes, and final golden fired sets are deferred
  to INT-3/T6.
- Visual budget compliance is measured only after the single T8 canonical
  regeneration.
- Independent implementation approval remains a later reviewer gate.
