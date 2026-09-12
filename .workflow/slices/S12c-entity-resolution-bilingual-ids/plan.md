# S12c plan (attempt 1)

Complete immutable plan: `.autonomous-workflow/plans/s12c-entity-resolution-bilingual-ids/cycle-1/plan-1-dispatch1.json`
(SHA-256 `6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd`, 107,631 bytes), authored by `planner-fable`
(claude-fable-5-1-thinking-max) against base `a3a97adfc0e497d5d14a9a2a5dacc0d2c662b941`, independently APPROVED by `reviewer-grok`
(zero findings; `plan-1-review.json`). The planner's first Task wait was interrupted at ~79 minutes; the planner finished writing its file at
10:25Z. A second, bounded planner dispatch started before that file was discovered wrote an alternative plan (SHA-256 `a3c9e1f6…`), archived as
`plan-1-dispatch2.json`; it is NOT the gated plan and is not implemented. This summary was written by the owner lead agent from the gated JSON.

## Design in one page

- **Types and ids:** `COMPANY`, `PLANT`, `LINE`, `LICENCE_HOLDER` in separate namespaces; `ENTITY_ID_V1` = `<TYPE>-<sha256(canonical_key)[:16]>`
  with canonical keys from the exact-normalised first-observed primary name (plants embed the company id + locality token; lines embed the plant
  id + designation). Ids are never re-issued; later names, mergers and ownership changes are dated records on the same id.
- **Normalisation:** `NAME_NORMALISATION_V1` from a new §7.3 rule table `config/entity_resolution.v1.yaml` 1.0.0 (exact level: NFC, casefold,
  tashkeel/tatweel stripping, Arabic-Indic digit folding, punctuation-to-space; variant level: alef/ya/ta-marbuta folds, definite article,
  legal-form tokens, an explicit transliteration table); the verbatim span is always retained; visual-order Arabic is flagged, never reversed.
- **Linking:** explicit precedence — identifier equality → exact name/alias equality (same type, same text order) → variant matches and multiple
  candidates → `PROPOSED_PENDING_REVIEW` → `UNRESOLVED` with a typed reason; no fuzzy scoring, no AI proposals; a plant is never minted from a
  company name alone (`EXACT_LOCALITY_WITHIN_WINDOW` requires a resolved subject within two lines on the same page).
- **Inputs:** an operator-recorded, builder-verified `EntityMentionList 1.0.0` (every span copied verbatim from a stored DocumentRecord line or a
  frozen public snapshot JSON pointer; no NER), the twelve stored DocumentRecords and the two read-only frozen public snapshots.
- **Artifact:** `EntityResolutionArtifact 1.0.0` under the new §7.5 root `data/entities/{mentions,resolution}/`, write-once, manifest-enumerated,
  byte-reconstructible from its declared inputs through `scripts/reconstruct_snapshot.py --all` (third PASS line; PASS lines only when everything passes).
- **Real outcome expected (DD-14):** 5 COMPANY entities (Universal Metal Coating Company alias UNICOIL; Hadeed; SABIC; Advanced Petrochemical;
  Tasnee — the last four from frozen-snapshot labels with legal names unresolved), 2 PLANT entities (UMCC at SAU-JUBAIL and SAU-JEDDAH, site
  locality), 0 LINE ("five production lines" is count-only), 0 LICENCE_HOLDER (no S12a rows), one 2004 ownership-change record with the owner
  unnamed, six SASO passports `UNRESOLVED/OUT_OF_SCOPE_ENTITY_TYPE`, three mentions deliberately held pending, zero deterministic identifiers.
- **Governance:** Core 04 §2.4/§4 and Core 05 §6.5/§11 additive text, Core 03/09 insertions, ADR-018 before exactly one `build_manifests.py` run
  (authority path set grows by the new rule table); offline CLI `build-entities`; `pipeline.py`, documents/**, connectors/** byte-identical.
- **Steps T0–T10** (TDD with named RED tests), **27 verification commands**, **AC-1…AC-12**, five frozen-scope boundary tests as doubles.

## Owner rulings on the plan's open decisions (recorded in `plan_review.md`)

OD-1 `data/entities/**` root — ACCEPTED. OD-2 jurisdiction as attribute, not key — ACCEPTED. OD-3 SITE_LOCALITY plants from the EPD facility statements —
ACCEPTED. OD-4 SASO out of scope (standards authority) — ACCEPTED. OD-5 rule table under §7.3 — ACCEPTED. OD-6 frozen-snapshot short labels mint
COMPANY entities with exact self-links — ACCEPTED. OD-7 1997 founding-shareholder sentence not harvested (embedded personal name) — ACCEPTED.
OD-8 operator-recorded mention list, no pattern NER — ACCEPTED. OD-9 (seat): implementation starts at `implementer-sol`; `reviewer-grok` reviews.
