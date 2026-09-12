# Completion — S12b Document Store, Disclosures and Tenders

**State:** MERGED (2026-09-12). Merge commit `9a9d5c7562065437b2d763180e04e0402d430e0e`; PR #17; PR CI run `34683839745` 5/5; default-branch CI run `34684108497` 5/5.

## Delivered

- `Stage.DOCUMENT` on the generalized acquisition framework; write-once, span-addressable document store under `data/documents/<source>/{lists,records}/`: `DocumentList 1.0.0` explicit operator lists (hashed, never edited after a run — v1…v4 retained), `DocumentRecord 1.0.0` with `DOCUMENT_ID_V1`, physical page order, 1-based line addressing, per-page `sha256("\n".join(lines))`, versioned text-layer and segmentation methods, latest-run selection with `superseded_run_ids`, §11 passports from existing support codes, fail-closed validators and byte-exact reconstruction under `scripts/reconstruct_snapshot.py --all`.
- Text layer: `pypdf==6.16.1` (dev extra only; layout extraction mode), stdlib HTML (`html.parser`, literal DD-5 block boundaries) and strict-UTF-8 plain text; no OCR, normalisation or bidi reordering; documents without a text layer stay `RAW_ONLY` with spans `UNAVAILABLE / FORMAT_NOT_PARSEABLE`.
- Seven document sources under `config/acquisition_sources.v1.yaml` 1.2.0; document envelope policy (four declared types, hash-only refusal metadata) through a stage-aware hook that leaves the S12a DIRECTORY/REGISTRY guard unchanged; DD-10 path-segment / `list_id` validation before any I/O.
- Twelve COMPLETE records from real public documents: six SASO technical regulations (Class B) and six UNICOIL disclosures — EPDs (GS, PPGI), ESG report, product sheets (Class C). The SASO PDFs carry Arabic in visual content-stream order; disclosed (Core 04/05, ADR-017, KL), not reshaped.
- Core 03/04/05/09 additive text; ADR-017; KL-54…KL-66; runbook; four owner-authorized manifest runs recorded with reasons.

## Truthful source outcomes

`tadawul_disclosures` (HTTP 403), `etimad_tenders` (portal reachable; no qualifying public document URL verified), `producer_sabic` (HTTP 406 on subpages), `producer_tasnee` (no TCP connection), `producer_advanced_petrochemical` (no DNS) remain honest `UNAVAILABLE` attempt records (KL-56…KL-60). Nothing proves these publishers lack public documents; later verification needs a new authorized window.

## Review and evidence

- Plan-1 (`c70e9065…`): planner-fable; reviewer-grok APPROVE with six advisories → IAC-7…12; owner rulings OD-1…OD-7.
- Ladder: composer slots 1–3 (incomplete → complete → reviewer REJECT), fable slot 4 (corrections), sol slot 5 under owner ruling OR-3 (three further record-contract defects found and fixed; final corrections). Reviews: grok REJECT → Fable REJECT → Fable APPROVE zero findings on `5258e7d4…`.
- Local: 1928 tests; integrity, scenario validation, reconstruction (1/4 + 12/12) and smoke PASS; owner `make ci` exit 0 incl. 118 functional + 4 visual nodes. Hosted: PR run `34683839745` and main run `34684108497`, five jobs each on the exact SHAs (Python 3.14 leg proves cross-version determinism of the text layer).
- Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`; simulated outcomes and exact values unchanged.

## Carried forward

- s12c (bilingual entity resolution) is the last S12 child; the parent completes only after it.
- KL-45 extends to document records (no engine/screening consumption until S13/S14); KL-42/KL-46 still block the Saudi HS6 universe snapshot for S13.
- Accepted observations: visual-order Arabic in SASO PDFs (S20 normalisation), `lines: []` for empty PDF pages as the recorded 1.0.0 behaviour, `a<br>b` vs `a<br/>b` asymmetry under literal DD-5, uniform segment validation inside `reconstruct_document`/`iter_records`, the HTTP/1.0-wrapped UNICOIL payload stored as-is (KL-66).
