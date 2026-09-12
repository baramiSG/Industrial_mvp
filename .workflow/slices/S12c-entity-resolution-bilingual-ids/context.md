# S12c implementation context

Base: `a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941` (main after PR #18; S12b merged at `9a9d5c7`).
Branch: `slice/s12c-entity-resolution-bilingual-ids`.

Authority for this slice: the owner's 2026-09-12 delegation to the owner lead agent; the approved S12 split
(`docs/BUILD_ROADMAP.md` §S12 split; `.autonomous-workflow/plans/s12-acquisition-institutional-documents/cycle-1/decomposition-1.json`,
SHA-256 `ad234d819270e40b63ef2e12fff435379e9e412630feda3e0c5629dcd887dbd7`, child `s12c` goal, acceptance boundary and open_decisions[1]);
AGENTS.md; Manifest; Core 04 (§2.4 plant/company/parent-group/line ids; §4 identity and keys), Core 05 §6.5, Core 08 §10; methodology §§2, 3.2, 6, 11.

Reality the plan must start from (verified 2026-09-12):
- Acquired entity-bearing evidence is small: no S12a institutional rows exist (five ENDPOINT_UNVERIFIED attempts); twelve S12b DocumentRecords exist
  (six SASO technical regulations — publisher SASO; six UNICOIL disclosures — publisher UNICOIL; passports carry `observation_context.publisher_text`,
  list entries carry `publisher_text`/`publisher_kind`); the frozen public snapshots and Core 05 §2 name UNICOIL, Hadeed, SABIC, Advanced
  Petrochemical and Tasnee as producers (Class C evidence inside `data/snapshots/public/**`, which is byte-frozen and may only be read).
- Therefore the artifact will legitimately contain few resolved entities; the framework (ID scheme, normalisation, precedence, statuses,
  time-versioning, reconstruction) is proven by boundary tests and doubles, and every real link must cite exact document/passport evidence or a
  deterministic identifier. Ambiguity stays pending; nothing is fabricated. That is a complete slice outcome.

Owner dispositions for planning (each still justified in the slice ADR-018):
1. Artifact placement (open_decisions[1]): a new §7.5 data root `data/entities/**` (governed, hashed, enumerated by `build_manifests.py`) rather than an
   acquisition snapshot kind — entity resolution is a derived cross-source artifact, not a per-(kind, source) snapshot. The planner may argue for the
   alternative with reasons.
2. Persistent ID scheme: deterministic from the entity type and a normalised canonical key, versioned (`ENTITY_ID_V1`), never re-issued; aliases and
   name changes are time-versioned records pointing at the same ID.
3. Normalisation rules are versioned (`NAME_NORMALISATION_V1`) and always retain the original span (`source span verbatim + normalised form`); no
   transliteration inference beyond an explicit, versioned variant table; no fuzzy scoring that can promote a link above `proposed_pending_review`.
4. Link statuses fixed by the boundary: `DETERMINISTIC_IDENTIFIER`, `EXACT_DOCUMENT_EVIDENCE`, `PROPOSED_PENDING_REVIEW`, `UNRESOLVED`. Only the first
   two count as resolved. No engine/screening/graph consumption (KL-45 analogue). No AI/LLM proposals.
5. One `scripts/build_manifests.py` run after ADR-018 and full regression; S11/S12a/S12b raw, snapshots, documents, frozen roots and browser
   baselines byte-identical.
6. Frozen public snapshots are read-only inputs; no edit, no re-issue.

Environment: uv-locked `.venv`; `PYTHONPYCACHEPREFIX` outside the repository; `.env` never read; runtime, tests and CI offline; no network is expected
in this slice (no acquisition). No commit before independent implementation APPROVE; PR + hosted CI green on the exact head + recorded owner merge
decision before merge.
