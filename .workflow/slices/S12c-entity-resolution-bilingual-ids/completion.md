# Completion — S12c Entity Resolution and Bilingual Persistent IDs

**State:** MERGED (2026-09-12). Merge commit `78c002ff8d16656fd3733f9f49f9a1bd3dcf00f2`; PR #19; PR CI run `34692240675` 5/5; default-branch CI run `34692471195` 5/5. The S12 split is complete (s12a #15 `cc85cbc`, s12b #17 `9a9d5c7`, s12c #19 `78c002f`).

## Delivered

- `src/ior_mvp/acquisition/entities/` — `ENTITY_ID_V1` ids for `COMPANY`, `PLANT`, `LINE`, `LICENCE_HOLDER` (never re-issued; dated ownership / name-change / merger records on the same id); `NAME_NORMALISATION_V1` from the new §7.3 rule table `config/entity_resolution.v1.yaml` 1.0.0 (exact and variant levels; verbatim span retained; visual-order Arabic flagged, never reversed); explicit linking precedence with the four statuses (`DETERMINISTIC_IDENTIFIER`, `EXACT_DOCUMENT_EVIDENCE`, `PROPOSED_PENDING_REVIEW`, `UNRESOLVED`); no fuzzy scoring, no AI proposals; a plant is never minted from a company name alone.
- `EntityMentionList 1.0.0` (operator-recorded, builder-verified verbatim spans) and `EntityResolutionArtifact 1.0.0` under the new §7.5 root `data/entities/{mentions,resolution}/`, write-once, manifest-enumerated, byte-reconstructible (third pass of `scripts/reconstruct_snapshot.py --all`); offline CLI `build-entities`; repository loader not consumed by the engine.
- Real artifact from 38 verbatim mentions: 5 COMPANY (Universal Metal Coating Company alias UNICOIL from exact document spans; Hadeed, SABIC, Advanced Petrochemical, Tasnee from frozen-snapshot labels with legal names unresolved), 2 UNICOIL site-locality PLANT (Al-Jubail, Jeddah), 0 LINE, 0 LICENCE_HOLDER, 0 deterministic identifiers, one 2004 ownership record with the owner unnamed; links 27 EXACT / 3 pending / 8 unresolved; six SASO passports `UNRESOLVED/OUT_OF_SCOPE_ENTITY_TYPE`.
- Core 03/04/05/09 additive text; ADR-018; KL-45 extension and KL-67…KL-73; runbook; one manifest run (2026-09-12T11:25:47Z).

## Review and evidence

- Plan-1 (`6370547f…`): planner-fable; reviewer-grok APPROVE (six advisories → IAC-8…13); owner rulings OD-1…OD-8; OD-9 started the ladder at `implementer-sol`.
- Implementation: `implementer-sol` slot 1 (T0 stop on an ignored bytecode file resolved by relocation; T0–T10 complete); reviewer-grok APPROVE zero findings on `c2370180…`.
- Local: 2027 tests; integrity, scenario validation, reconstruction (1/4 + 12/12 + 1/38) and smoke PASS; owner `make ci` exit 0 incl. 118 functional + 4 visual nodes. Hosted: PR run `34692240675` 5/5 on the exact head (Python 3.14 leg confirms determinism).
- Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`; simulated outcomes unchanged.

## Carried forward

- KL-45 (no engine/screening consumption of acquired snapshots, documents or entity ids) → S13/S14. KL-42/KL-46 (no Saudi HS6 universe) → S13 guarded acquisition window (WITS answered HTTP 200 on 2026-09-12 — availability observation only; content, coverage, completeness and provenance must be verified before any run counts as the universe).
- Accepted observations: short-label companies with unresolved legal names; jurisdiction and Arabic primary names UNAVAILABLE; three mentions pending review; the unnamed-owner representation (null owner fields + description) per DD-7.
- Owner inputs requested 2026-09-12: optional UN Comtrade subscription key; producer/tender public document URLs for S14/S15.
