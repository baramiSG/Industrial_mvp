# S12b plan (attempt 1)

Complete immutable plan: `.autonomous-workflow/plans/s12b-document-store-disclosures-tenders/cycle-1/plan-1.json`
(SHA-256 `c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`, 118,220 bytes), authored by `planner-fable`
(claude-fable-5-1-thinking-max) against base `cdfd4ba4b016619b7ab33a373d334f22c337166d`. The planner's Task wait was interrupted at
~04:38Z while the planner was still compacting the JSON; an intermediate 121,873-byte version (SHA-256 `8b0ff175…`) was gated
prematurely by the supervisor at 04:41Z and the first `reviewer-grok` dispatch correctly refused it on identity mismatch (record
`.autonomous-workflow/evidence/s12b-document-store-disclosures-tenders/plan-1-review-identity-mismatch-8b0ff175.json`). The final
write at 04:42:11Z (118,220 bytes, SHA-256 above) is the gated plan; the supervisor verified it retains all 22 design decisions,
T0–T12, AC-1–AC-14, 27 verification commands, 25 baseline facts and the seven open decisions. This summary was written by the owner
lead agent from the JSON and adds nothing to it.

## Design in one page

- **Documents are an acquisition stage, not a snapshot kind.** `Stage.DOCUMENT` joins `STAGE_SPECS` (one contract per recorded document
  URL, `parameters = (('document_url', …),)`); raw bytes flow through the unchanged `BaseConnector.acquire`, `RawStore`, coverage and
  passport code. Derived per-document records live in a new `DocumentStore` under `data/documents/<source_id>/{lists,records}/`.
  `kinds.py`, `snapshots.py`, `coverage.py`, `harmonise.py`, `passports.py` stay byte-identical.
- **Explicit operator lists (DocumentList 1.0.0)** are hand-authored during the guarded window from links actually displayed on publisher
  pages, hashed, validated fail-closed and never edited after a run. No crawling; the plan asserts no URL is reachable.
- **Text layer:** `pypdf==6.16.1` (pure Python, BSD-3-Clause, no extras) pinned in the `dev` extra only; PDF pages extracted with
  `extraction_mode='layout'` (plain mode reverses RTL runs); HTML via stdlib `html.parser` with a fixed block-tag set; plain text strict
  UTF-8. `LINE_SEGMENTATION_V1` splits verbatim lines per page. No OCR, no normalisation. Documents without a text layer are stored raw
  with `text_layer.status = UNAVAILABLE / FORMAT_NOT_PARSEABLE` (`NO_TEXT_LAYER | PARSER_ERROR | NOT_UTF8`).
- **Identity:** `DOC-<SOURCE>-<query_hash[:12]>-<raw_sha256[:12]>` (`DOCUMENT_ID_V1`); identical bytes → `ALREADY_STORED`; changed
  bytes → new id, history retained. Records pin their own raw run and re-derive byte-for-byte under `scripts/reconstruct_snapshot.py --all`.
- **Envelope policy:** exactly `application/pdf`, `text/html`, `application/xhtml+xml`, `text/plain` are stored; anything else is refused
  before storage as `OUT_OF_SCOPE_CONTENT / UnsupportedDocumentEnvelope` with hash-only metadata, through a stage-aware
  `_pre_storage_refusal` hook that leaves the S12a DIRECTORY/REGISTRY guard behaviour and message unchanged.
- **Sources (config 1.2.0, §7.3):** `tadawul_disclosures` (C), `etimad_tenders` (B), `saso_documents` (B), `producer_unicoil`,
  `producer_sabic`, `producer_advanced_petrochemical`, `producer_tasnee` (C) — sixteen ids in total; S11/S12a mappings value-identical.
- **Passports:** one Class-target passport per record from existing support codes only (`DOMESTIC_*`, `TARGET_SPECIFICATION_DEMAND`,
  `BILINGUAL_SPECIFICATION_EXTRACTION`, `HARD_REGULATORY_PROCESS_GATES`); `synthetic_flag=false`; never a capacity/compliance claim.
- **Governance:** Core 04 `DocumentRecord 1.0.0` section, Core 05 rows/§6.6/§10/§11 text, Core 03 §4.11 and Core 09 §5 insertions (§7.4)
  with ADR-017 before exactly one `build_manifests.py` run; `build_manifests.py` enumerates `data/documents/**`.
- **Steps T0–T12** (TDD with named RED tests), **27 verification commands**, **AC-1…AC-14**, honest terminal states for every entry.

## Owner rulings on the plan's open decisions (recorded in `plan_review.md`)

OD-1 dev-extra placement — ACCEPTED. OD-2 classes (Etimad/SASO B, producers/Tadawul C) — ACCEPTED. OD-3 per-producer source ids — ACCEPTED.
OD-4 new Core 05 §3.3 row — ACCEPTED. OD-5 `snapshot_kinds = {'document'}` — ACCEPTED. OD-6 layout mode — ACCEPTED.
OD-7 four envelope types only — ACCEPTED (octet-stream/x-pdf refusals recorded as KL; widening is a later governed change).
