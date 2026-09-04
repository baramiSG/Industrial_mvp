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
| UN Comtrade / WITS | HS6 value, quantity, partner and time series | Reporter record; gross flows; quantity quality varies | connector implemented (S11); availability and coverage recorded per run |
| BACI (CEPII) | reconciled bilateral HS6 and cross-country consistency | annual; release-version pinning required | connector implemented (S11); raw evidence only, no analytical kind |
| ITC Trade Map | monthly and mirror diagnostics | registration/licensing conditions; not a substitute for Saudi administrative data | connector planned |
| GASTAT foreign trade and open data | official domestic aggregate anchor | reconcile definitions and revisions | connector planned |
| ZATCA integrated tariff | Saudi 12-digit line tree and duties | classification tree is needed even when transactions are not public | connector implemented (S11) |
| Reporter-country mirror flows | gap and anomaly diagnostic | mirror statistics do not replace the reporter record | planned diagnostic |

Mirror data may help explain a missing year or partner anomaly. It must not be silently spliced into a Saudi reporter series as if it were the same measurement.

### 3.2 Supply and capability

| Source | Use | Evidence class expectation |
|---|---|---|
| GASTAT economic census and industrial surveys | sector/establishment anchor | B/C until product-line reconciliation |
| Ministry of Industry open data | licences and activity | B/C; licence is not production |
| MODON directories | plant/entity discovery | C |
| Tadawul filings and annual reports | nameplate, expansion and financial context | C |
| EPDs and product sheets | process, range, standards and certifications | C |
| GPCA / sector associations | sector capacity context | B/C |

Public nameplate capacity does not establish current effective capacity, qualification share, allocation or availability.

### 3.3 Specifications and qualification

| Source | Use | Control |
|---|---|---|
| SASO catalogue | standard identity and scope | title/scope does not prove compliance |
| Purchased anchor standards | detailed requirement extraction | copyright and access controls |
| Etimad tenders and awards | real bilingual demand specifications | exact document/page span required |
| SABER registry | conformity evidence | registration does not prove every buyer qualification |
| Producer catalogues / certificates | published product envelope | confirm current edition and contradiction |

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

### 6.6 Documents

- preserve original source span;
- normalize numerals, units, symbols, transliterations and standard references;
- retain contradiction rather than selecting the convenient value.

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
