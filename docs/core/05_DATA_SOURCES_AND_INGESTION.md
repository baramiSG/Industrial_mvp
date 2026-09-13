# 05 — Public Data Sources, Snapshots and Ingestion

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Objective

The MVP must run end to end without live dependencies while preserving a production-ready data contract. Public sources identify signals, products, incumbent capability and strategic context. Ministry data later resolves the line-level facts that public evidence cannot defend.

## 2. Implemented data in this package

The packaged POC uses the public evidence already frozen in the final methodology’s worked cases.

| Block | Implemented snapshot |
|---|---|
| Trade | WITS/UN Comtrade annual Saudi rows for HS 721049 and HS 390210, 2021/2023/2024 |
| Supplier concentration | Steel 2024 top-two share and HHI from the worked case |
| Producer capability | UNICOIL, Hadeed, SABIC, Advanced Petrochemical and Tasnee public evidence |
| Specification | UNICOIL bilingual published specification spans and EPD contradiction |
| Synthetic internal analogs | line capacity, qualification share, allocation, customer target, economics and grade equivalence |

These records are stored locally, hashed and never refreshed during runtime.

## 3. Production public-source catalogue

### 3.1 Trade and demand

| Source | Use | Grain / caution | MVP status |
|---|---|---|---|
| UN Comtrade / WITS | HS6 value, quantity, partner and time series | Reporter record; gross flows; quantity quality varies | official v1 Comtrade universe COMPLETE (2021–2024; imports and exports; 5,443 HS6); WITS partner detail OBSERVED for 392010/721012/760429/760711; corrected W-C V3 Comtrade partner detail OBSERVED for 721061 with seven named non-World H6 rows; original WITS and Comtrade attempts retained; ZATCA tariff tree UNAVAILABLE |
| BACI (CEPII) | reconciled bilateral HS6 and cross-country consistency | annual; release-version pinning required | connector implemented (S11); raw evidence only, no analytical kind |
| ITC Trade Map | monthly and mirror diagnostics | registration/licensing conditions; not a substitute for Saudi administrative data | connector planned |
| GASTAT foreign trade and open data | official domestic aggregate anchor | reconcile definitions and revisions | connector planned |
| ZATCA integrated tariff | Saudi 12-digit line tree and duties | classification tree is needed even when transactions are not public | connector implemented (S11) |
| Reporter-country mirror flows | gap and anomaly diagnostic | mirror statistics do not replace the reporter record | planned diagnostic |

Mirror data may help explain a missing year or partner anomaly. It must not be silently spliced into a Saudi reporter series as if it were the same measurement.

### 3.2 Supply and capability

| Source | Use | Evidence class expectation |
|---|---|---|
| GASTAT economic census and industrial surveys | sector/establishment anchor | B/C until product-line reconciliation; connector implemented (S12a); availability and coverage recorded per run |
| Ministry of Industry open data | licences and activity | B/C; licence is not production; connector implemented (S12a); availability and coverage recorded per run |
| MODON directories | plant/entity discovery | C; connector implemented (S12a); availability and coverage recorded per run |
| Tadawul filings and annual reports | nameplate, expansion and financial context | C; connector implemented (S12b); availability and coverage recorded per run |
| EPDs and product sheets | process, range, standards and certifications | C; connector implemented (S12b); availability and coverage recorded per run |
| Hadeed public catalogue | coated-steel process/product envelope | C; S14a run `20260912T233102Z` COMPLETE; one span-addressable record |
| ALUPCO public profile | aluminium extrusion, sites and disclosed production envelope | C; S14a run `20260912T233130Z` COMPLETE; one span-addressable record |
| Al Taiseer Group TALCO profile | aluminium profile manufacture, extrusion and finishing | C; S14a run `20260912T233154Z` COMPLETE; one span-addressable record |
| Ma'aden annual report and results page | aluminium rolling and company production context | C; S14a run `20260912T233222Z` COMPLETE; two span-addressable records |
| SPIMACO investor disclosures | publisher identity and disclosed pharmaceutical context only | C; S15 run `20260913T035150Z` stored one COMPLETE PDF unit; a second listed unit was not requested after the local parser dependency stop |
| SABIC Agri-Nutrients annual report | publisher identity and disclosed fertiliser-company context only | C; S15 run `20260913T035235Z` COMPLETE; one span-addressable report |
| SFDA drug-companies register | regulatory publisher/company-list observation | B; S15 run `20260913T035254Z` COMPLETE; `regulatory_authority` does not prove product manufacture, capacity or qualification |
| GPCA / sector associations | sector capacity context | B/C |

Public nameplate capacity does not establish current effective capacity, qualification share, allocation or availability.

### 3.3 Specifications and qualification

| Source | Use | Control |
|---|---|---|
| SASO catalogue | standard identity and scope | title/scope does not prove compliance; connector implemented (S12a); availability and coverage recorded per run |
| SASO public technical regulations | mandatory requirement documents as published | title/scope does not prove compliance; connector implemented (S12b); availability and coverage recorded per run |
| Purchased anchor standards | detailed requirement extraction | copyright and access controls |
| Etimad tenders and awards | real bilingual demand specifications | exact document/page span required; connector implemented (S12b); availability and coverage recorded per run |
| SABER registry | conformity evidence | registration does not prove every buyer qualification; connector implemented (S12a); availability and coverage recorded per run |
| Producer catalogues / certificates | published product envelope | confirm current edition and contradiction; connector implemented (S12b); availability and coverage recorded per run |
| WCO HS Nomenclature 2022 chapter texts | target-product classification identity only | B; source `wco_hs_nomenclature`; Chapters 39/72/76 COMPLETE in S14a; never capability/nameplate support |
| WCO HS Nomenclature 2022 chapter texts, S15 extension | target-product classification identity only | B; Chapters 29/30/31 COMPLETE in run `20260913T033253Z`; residual `identity_exclusions` require verbatim stored addresses |

### 3.4 Economics

| Source | Use | Caution |
|---|---|---|
| CIF unit values | import-parity starting point | not transaction price or grade proof |
| ZATCA tariff/duty | landed-cost adjustment | exemption and origin treatment required |
| Published Saudi energy/feedstock prices | utility/feedstock scenarios | effective industrial contract may differ |
| Public feasibility and engineering literature | capex/opex prior | Class D until validated for route/scale |
| Damodaran / comparable finance benchmarks | hurdle-rate reference | Ministry-approved sector/risk rate governs |

### 3.5 Strategic priors

- Harvard Atlas / OEC product-space and complexity releases;
- NIDLP, NIS and Invest Saudi published opportunity material;
- official critical-product and resilience designations.

These are priors and strategic context. They never replace plant capability or target-specification evidence.

## 4. Source contract

Every acquired artifact shall record:

```yaml
source_id:
authority:
access_classification:
endpoint_or_document:
query_contract:
reporter:
partner:
flow:
product_code:
nomenclature:
period:
retrieved_at:
source_refresh_date:
raw_file_path:
sha256:
license_or_usage_note:
```

## 5. Snapshot workflow

1. Freeze decision/as-of date.
2. Acquire the raw file or response.
3. Store the unmodified raw artifact.
4. Calculate SHA-256.
5. Record query contract and retrieval metadata.
6. Parse into normalized staging tables.
7. Apply classification, unit, valuation, origin and entity controls.
8. Record exclusions and transformations.
9. Produce the analytical snapshot.
10. Hash the analytical snapshot.
11. Run quality and golden tests.
12. Release a new snapshot ID; never overwrite the prior historical snapshot.

## 6. Harmonisation rules

### 6.1 Classification

- store reported HS revision and year;
- use official concordances;
- preserve one-to-many mappings;
- preserve Saudi national tariff suffix;
- retain ambiguous descriptions as unresolved.

### 6.2 Quantity

- keep value, net weight, supplementary quantity and unit separately;
- disable unit-value analysis when units are incompatible or implausible;
- report valid quantity coverage;
- never infer a physical unit from value alone.

### 6.3 Valuation and currency

- preserve import CIF and export FOB unless explicitly adjusted;
- retain original nominal currency/value;
- version conversion and deflation methods.

### 6.4 Origin and re-export

- separate gross imports, re-imports, re-exports and domestic-origin exports when possible;
- when unavailable, retain gross values and reduce confidence;
- do not call gross net exposure domestic demand.

### 6.5 Entity

- normalize Arabic and English company/plant names;
- use persistent IDs;
- time-version ownership, merger and name changes;
- distinguish licence holder, company, plant and line.

S12c loads `config/entity_resolution.v1.yaml` and applies `ENTITY_ID_V1` plus the two-level `NAME_NORMALISATION_V1` to verbatim declared spans. Precedence is `DETERMINISTIC_IDENTIFIER`, `EXACT_DOCUMENT_EVIDENCE`, `PROPOSED_PENDING_REVIEW`, then `UNRESOLVED`; there is no fuzzy scoring and no AI proposals. Authored lists and write-once artifacts remain under `data/entities/` and are not consumed by the engine until S13/S14.

### 6.6 Documents

- preserve original source span;
- normalize numerals, units, symbols, transliterations and standard references;
- retain contradiction rather than selecting the convenient value.

S12b stores the original span layer verbatim; normalisation remains S20.

## 7. Current frozen public snapshots

### 7.1 Steel HS 721049

Public facts represented:

- 2021, 2023 and 2024 gross trade;
- 2022 missing and not interpolated;
- 2023→2024 quantity-led expansion;
- 2024 concentration HHI 0.36;
- bulk unit-value band and small Austrian outlier;
- UNICOIL published 250 kt/y nameplate and galvanising process;
- Hadeed process-family evidence;
- unresolved line utilisation, allocation and customer qualification.

### 7.2 Polypropylene HS 390210

Public facts represented:

- 2021, 2023 and 2024 gross trade;
- exports above 50× import value in 2023 and 2024;
- 2023→2024 quantity decline and unit-value increase;
- broad producer capability evidence;
- unresolved named grade/application exception.

## 8. Synthetic seeding from public marginals

Synthetic scenarios are not random fake tables. They are constrained demonstrations.

Rules:

1. total synthetic demand must not exceed the public quantity boundary without disclosure;
2. synthetic plant capacity must remain consistent with public nameplate evidence;
3. line shares must sum within plausible plant totals;
4. tariff-line or buyer allocations must reconcile to the public HS6 aggregate;
5. scenario values must be deliberately chosen to exercise known route logic;
6. every planted truth must be documented and testable.

Example:

```text
Public steel nameplate = 250 kt
Synthetic availability = 92%
Synthetic yield = 94%
Synthetic qualification share = 38%
Synthetic market allocation = 70%
Effective target-spec capacity = 57.509 kt
```

## 9. Data-quality gates

| Gate | Failure behavior |
|---|---|
| Classification unresolved | R0 evidence case; no scoring |
| Quantity unit invalid | disable UV and R2 quantity path |
| Missing continuity | R1-F disabled; consider R1-D |
| Gross flow only | reduce confidence; no retained-demand claim |
| Partner-month cells absent | R4-F disabled; R4-D only |
| Public nameplate only | no effective-capacity conclusion |
| Contradictory product ranges | retain contradiction and request confirmation |
| Live source changed | create new snapshot; do not mutate golden fixture |

## 10. Ingestion implementation (S11)

Production connectors implement `acquisition.connectors.base.SourceConnector`:

```python
class SourceConnector:
    def acquire(self, query_contract, *, max_requests) -> RawArtifact | UnavailableRecord: ...
    def validate(self, raw) -> QualityReport: ...
    def normalize(self, raw) -> list[Observation]: ...
    def snapshot(self, observations, as_of_date) -> Snapshot: ...
```

Raw store layout: `data/raw/<source_id>/<query_hash>/<run_id>/` holds one `page-<NNNN>.payload.<ext>.gz` + `page-<NNNN>.contract.json` pair per response, plus `coverage.json` or `attempt.json` per planned unit run.

Unit-level two-stage acquisition: UNIVERSE (ALL HS6), PARTNERS (explicit HS6 list), TARIFF (national tree), BULK (BACI raw-only). UNAVAILABLE reasons are enumerated in `UnavailableReason`. Offline guard blocks socket connect unless explicit live flag and env var are set. Reconstruction proof re-derives snapshots byte-for-byte from stored artifacts under default manifest checking.

S12a extends the registry-driven stage list with AGGREGATE (GASTAT production aggregates, period-scoped), DIRECTORY (Ministry of Industry and MODON establishment/licence directories, period-free) and REGISTRY (SASO catalogue and SABER conformity registry, period-free). `SourceConnector.normalize` returns the `Row` union, including the three Core 04 row contracts; optional `parse_rows` supplies store-time classification. A nonempty recognized parse is `NORMALIZED`; an absent parser is `PENDING`; an unknown or failed parse is `UNPARSED` with `no_rows_parsed`. Institutional connectors implement `parse_rows` and return an empty list for unobserved shapes, including test-fixture envelopes; production parsers are not inferred from doubles. TERMS behavior remains unchanged. Classification metadata is write-once: offline parser development against retained UNPARSED text cannot relabel the old run; a fresh acquisition is required for a new NORMALIZED run and snapshot proof.

For DIRECTORY/REGISTRY data responses only, after HTTP-error handling and before classification or storage, the approved text-only guard uses the declared response content type from the existing header helper (first exact lowercase `content-type` header, parameters/outer whitespace stripped, missing header defaults to `application/octet-stream`); casefolding affects routing only, not the recorded type. `expected_content_types` never selects an envelope. Declared `application/pdf`, `application/zip`, `application/gzip`, or `image/`, `audio/`, `video/`, `font/` prefixes are refused. Remaining bodies must decode as strict UTF-8 (a leading UTF-8 BOM is accepted for inspection only) and contain none of U+0000–U+0008, U+000B–U+000C, U+000E–U+001F, U+007F; TAB/LF/CR, U+200F and tatweel are allowed. No charset override, replacement decoding, OCR or decompression is attempted. Stored payload bytes remain original.

Exactly one envelope is selected; there is no body sniffing, retry or fallback:

| Declared type | Field labels inspected |
|---|---|
| `application/json`, `text/json`, `application/<nonempty-subtype>+json` (subtype has no slash or whitespace) | Every object key recursively, including objects inside lists |
| `text/csv` | Standard quoted comma-delimited CSV; first record with any non-whitespace cell supplies labels |
| `text/tab-separated-values` | Standard quoted tab-delimited CSV; first record with any non-whitespace cell supplies labels |
| `text/html`, `application/xhtml+xml` | Only `th` text and `name` attributes on `input`, `select`, `textarea`, `button`; script/style contents excluded |
| All other declarations, including missing, empty, unknown and `application/octet-stream` | Opaque inspectable text, no inferred fields and no recognized rows |

Failed selected-format parsing is an unknown shape, not a reason to try another envelope or refuse solely for unfamiliarity. HTML prose, links, IDs, placeholders and unrelated attributes are not inspected. Field-label normalization applies `([A-Z]+)([A-Z][a-z]) → group1_group2`, then `([a-z0-9])([A-Z]) → group1_group2`, then NFC, casefolding and replacement of whitespace/underscore/hyphen/slash/dot runs with `_`, trimming boundary underscores. English matching is underscore-boundary suffix matching, optionally followed by `_ar`, `_en` or `_text`, for: `phone`, `phone_number`, `phone_no`, `telephone`, `telephone_number`, `telephone_no`, `mobile`, `mobile_number`, `mobile_no`, `email`, `email_address`, `e_mail`, `e_mail_address`, `contact_person`, `contact_person_name`, `contact_name`, `person_name`, `national_id`, `national_id_number`, `national_id_no`; `contact_id` and `contact_id_number` are intentionally not aliases. Arabic matching is exact whole normalized label only, without prefix or language/text suffix, for: `هاتف`, `الهاتف`, `رقم_الهاتف`, `جوال`, `الجوال`, `رقم_الجوال`, `البريد_الإلكتروني`, `البريد_الالكتروني`, `بريد_إلكتروني`, `بريد_الكتروني`, `اسم_شخص_الاتصال`, `اسم_مسؤول_التواصل`, `الهوية_الوطنية`, `رقم_الهوية_الوطنية`. Labels are checked even for null values; values and free prose are not classified. This is bounded schema-label screening, not universal personal-data detection.

Refusal is `OUT_OF_SCOPE_CONTENT` with `PersonalDataFields` for matched labels or `UninspectableTextPayload` for uninspectable bodies. Only hash-based response metadata is retained (status, filtered headers, byte count, SHA-256, constant safe message/error type), never the refused body or matched values/labels; prior pages and records remain intact. Refusal overrides apparent pagination completeness with INCOMPLETE coverage and stop reason OUT_OF_SCOPE_CONTENT, and embedded attempt coverage equals its sibling coverage. Unknown but inspectable text may be stored UNPARSED. The DD-15(b) offline-parser path is limited to retained text: PDF/XLSX and non-UTF-8/legacy-encoded bodies are outside it; a later parser cannot recover an unstored body. Format/encoding support needs a separate governed change. Such policy refusals must not be called FORMAT_NOT_PARSEABLE, which describes stored-UNPARSED build refusal. S11 stages and TERMS remain outside this new guard.

**DOCUMENT stage (S12b):** `Stage.DOCUMENT` adds one contract per recorded document URL with parameters `(document_url, …)`. Acquisition is list-driven: operator-authored DocumentList 1.0.0 entries define publisher metadata, expected envelope, evidence-class target and allowed support codes before any live window. The **DOCUMENT_ENVELOPE** policy stores exactly `application/pdf`, `text/html`, `application/xhtml+xml` and `text/plain`; anything else is refused before storage as `OUT_OF_SCOPE_CONTENT` / `UnsupportedDocumentEnvelope` with hash-only metadata. There is no prose personal-data screening on document bodies; bounded schema restrictions apply only to DIRECTORY/REGISTRY rows as above. Derivation uses `PDF_TEXT_LAYER_PYPDF_LAYOUT` (layout mode, dev-only `pypdf==6.16.1`), `HTML_TEXT_LAYER_STDLIB`, `PLAIN_TEXT_LAYER_STDLIB` and `LINE_SEGMENTATION_V1`, preserving verbatim Arabic/English lines in PDF content-stream order without normalisation (where a publisher PDF paints Arabic in visual order, the stored lines are visual-order; `COMPLETE` / `PASS` denotes an extracted text layer, not logical reading order — Core 04 DocumentRecord 1.0.0). Every parseable PDF page is retained at its physical 1-based page number, including empty-text pages; `page_count` equals the physical PDF page count and each page hash is `sha256("\n".join(lines))`. `text_layer.status` is `COMPLETE` only when any page contains a non-whitespace line, otherwise `UNAVAILABLE` (`FORMAT_NOT_PARSEABLE` with `NO_TEXT_LAYER`, `PARSER_ERROR` or `NOT_UTF8`); `RAW_ONLY` records retain stored bytes and, for a parseable textless PDF, its empty physical page entries. Layout: raw bytes under `data/raw/<source_id>/<query_hash>/<run_id>/`; derived **DocumentRecord** JSON under `data/documents/<source_id>/records/` with list hashes under `lists/`. Reconstruction re-derives records byte-for-byte from pinned raw artifacts and list rows.

## 11. Acquisition run governance

- Operator-invoked only; `--years` is required on `acquire-universe`, `acquire-partners` and `acquire-baci`, and `--max-requests` on every acquire command, with rationale recorded in the slice implementation log (no suggested defaults in runbook or code); `acquire-tariff` takes no `--years` because the tariff tree is acquired as one period-free contract whose as-of date comes from retrieval.
- Credentials referenced by environment variable name only; absence recorded as `CREDENTIAL_ABSENT`.
- Licence capture boundary: terms must be captured when `license_capture_required` is true or run fails `LICENSE_UNRECORDED`.
- Size budget enforced by `RawStore` (`max_artifact_bytes_compressed`, `max_store_bytes_compressed` in hashed YAML).
- Rate-limit floor: `min_interval_seconds` from source config between requests.
- Completeness accounting (DD-18): every planned unit receives coverage with `pages_fetched`, `pages_expected`, and `status`; truncated pagination never becomes a universe/tariff snapshot.
- Source partition and selection (DD-21): one analytical snapshot per `(kind, source_id)`; latest run per source/stage/unit key; superseded runs retained; a universe with any INCOMPLETE selected unit is never written as the Saudi HS6 universe.
- BACI raw-only (DD-22): BULK stored as evidence; never spliced into reporter universe.
- Re-run discipline: higher `MAX_REQUESTS` may produce a new run_id; latest selection may change and trigger `SELECTION_CHANGED` on reconstruction.
- History retention: all runs remain under `data/raw/`; manifest lists every regular file.
- Stop conditions: (A) zero real artifacts across all sources → halt before snapshot build; (B) zero normalized analytical snapshots after parsers → halt before reconstruction CI wiring.

- S12a commands require explicit `--source` and `--max-requests`; `acquire-aggregates` also requires `--years`, whereas `acquire-directory` and `acquire-registry` are period-free and take no years or flows. Make targets retain explicit live-intent and not-CI guards; runtime and CI remain offline. `parameters.units` and request tokens are recorded only from observed official documentation; unknown values remain `UNAVAILABLE`, never guessed from portal names or borrowed from trade sources. An unverified endpoint/unit fails before terms capture or budget use. Only observed credential-variable names can require a credential; the `UNAVAILABLE` sentinel causes no lookup or Authorization header.
- DIRECTORY/REGISTRY operators apply the §10 pre-storage policy: `PersonalDataFields` or `UninspectableTextPayload` means OUT_OF_SCOPE_CONTENT with no refused body retained, not a recoverable stored-UNPARSED payload; preserve the safe attempt metadata, INCOMPLETE coverage and prior pages, and cite the actual refusal without values or matched labels.
- The five S12a implemented status cells in §3.2/§3.3 describe connector code coverage, not source availability or validated production/compliance facts. The accepted T7 operator records in `.workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md` record five zero-request ENDPOINT_UNVERIFIED attempts with INCOMPLETE coverage and no institutional pages or snapshots; the existing S11 partner snapshot remains the reconstruction oracle. Per-run facts and outstanding limitations belong in the RunReports, ADR and Known Limitations, without promoting unavailable evidence or test-double rows into observations.
- S12b `acquire-documents` requires explicit `--source`, `--list-id` and `--max-requests`; it takes no `--years` or flow parameters. Document lists are authored and hashed before the live window; a list is never edited after a run (corrections use a new `list_id`). Each list entry is an independent DOCUMENT unit and contributes to the minimum request bound; per-entry COMPLETE, RAW_ONLY or honest INCOMPLETE outcomes are acceptable terminal evidence. `build-documents` selects only the latest stored run per source/stage/unit and records sorted prior run ids as superseded before deriving DocumentRecord JSON offline. Size budgets, rate-limit floors and licence-capture rules are unchanged from S11/S12a.
- S12c `build-entities` is offline and requires `--mention-list-id`. Mention lists are operator-authored, validated and hashed before a build and are never edited after one (a correction uses a new `list_id`); every span is verified verbatim against its stored line or JSON value before the write-once entity artifact is emitted and reconstructed byte-for-byte.
- **W0–W3 operator-window discipline (S13a):** W0 observes official
  documentation without credentials and records every fact or `NOT OBSERVED`;
  W1 attempts the complete year/flow universe with a fixed request bound; W2
  requests partner detail only for engine-emitted R2 survivors and only within
  a documented provider limit; W3 runs only when W0 establishes a documented
  ZATCA tariff-tree endpoint. Parameters and rationale are logged before each
  window. Unknown terms, limits, pagination or endpoint facts remain
  `UNAVAILABLE`; no inferred value may enable a request.
- UN Comtrade universe coverage is COMPLETE only for a JSON object with
  `data`, integer `count == len(data)`, empty error, reporter 682, matching
  period/flow/world partner, unique six-digit HS6 rows and one verbatim
  `classificationCode` per unit. Any mismatch remains INCOMPLETE and cannot
  become the Saudi universe. Stage-two partner rows and tariff schedules remain
  distinct artifacts.

- **S14a W-A/W-T/W-P discipline:** every robots and linked-terms observation,
  source/list id, request bound and rationale is recorded before execution.
  WCO Chapter URLs come from observed index hrefs; no numeric filename pattern
  is guessed. WCO identity text is Class B and
  `TARGET_PRODUCT_IDENTITY`-only. Producer disclosures are Class C and may
  affect capability only through verified DocumentRecord spans. Tasnee and
  SPIMACO remain `UNAVAILABLE` after one system-CA verification failure each;
  TLS was not bypassed. WITS partner acquisition used the ruled five-HS6 list,
  2024 imports and `MAX_REQUESTS=6`. Four units normalized; 721061 redirected
  to an HTTP-200 error page and is a derived `FORMAT_NOT_PARSEABLE` exclusion.
  Historical and current partner snapshots reconstruct from their own recorded
  raw-run selections. Transport-complete but `PENDING/UNPARSED` units may be
  excluded only for an `AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS` kind; all-unit
  kinds continue to fail closed.
- **S14a W-C source substitution:** a substitute source is admissible only
  when reporter, year, flow, HS6 and classification match from stored response
  rows under that source's own terms and credential contract; the original
  attempt remains visible. For 721061, V1 omitted `partnerCode` and returned a
  clear `count == len(data) == 8` envelope with one World and seven non-World
  H6 rows. The seven partner codes had null descriptions, so the required
  partner-description predicate failed. AM-3 added raw-Decimal aggregate
  reconciliation and a governed `&includeDesc=true` V3 variant. The first
  operator command did not transmit V3 because Make left its ampersand
  unquoted; OD-18 classified that immutable repeat as a tooling defect.
  Test-first quoting then carried the exact variant into the URL and contract.
  Corrected V3 returned seven unique non-World descriptions, and their
  primary-value sum 71,149,266.221 reconciled exactly to the stored universe
  World value within tolerance 0.0035. Coverage is COMPLETE and the separate
  `PARTNERS-SAU-UN-COMTRADE-2026-09-13` snapshot retains the defective repeat,
  V1 and WITS units as superseded attempts. No row was filtered or renamed.
  A clear JSON `count == 0 == len(data)` response would be
  `NORMALIZED_EMPTY`/ZERO; an error, only-World or unparseable response remains
  MISSING and never becomes zero.

- **S15 W-A15a/W-A15b/W-P15 discipline:** robots/terms and request parameters
  were recorded before each bounded window. W-A15a stored WCO Chapters
  29/30/31 from observed index rows and built three Class-B identity records.
  W-A15b stored one SPIMACO PDF unit, one SABIC Agri-Nutrients report and one
  SFDA register page. The SPIMACO run stopped after the stored first unit when
  local PDF parsing required an unavailable dependency; no retry or second
  document request was made. W-P15 requested only 294110, 294120, 310430 and
  310510 for 2024 Saudi imports. One terms request plus four data requests
  produced four COMPLETE units; each reconciles its named non-World rows to
  the stored World aggregate. The resulting scoped snapshot has those four
  units only and coexists with, rather than supersedes or unions with, the
  same-day S14a snapshot.
- S15 capability and hard-gate values remain `U`/`UNAVAILABLE` unless a
  CaseBrief cites a verified supporting span. Here `U` means not identified
  within the named stored evidence and search boundary, never that capability
  is absent. `NO_PUBLIC_TENDER_FOUND` is likewise limited to the recorded
  public-evidence search; it is not proof that no tender or specification
  exists. Missing trade years and unavailable values are never numeric zero.
