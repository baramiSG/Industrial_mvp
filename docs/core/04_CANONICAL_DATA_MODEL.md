# 04 — Canonical Data Model

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Modeling principle

The primary entity is not an HS code. An HS code is one coordinate used to locate evidence. The canonical decision object is:

```text
Product–Specification–Application–Capability–Demand–Route
```

The MVP stores each golden case as a versioned JSON aggregate. Production may normalize the same model into relational tables and a graph without changing the field semantics.

## 2. Core entities

### 2.1 Opportunity

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | string | yes | Persistent opportunity ID, independent of display name |
| `hs_revision` | string | yes | Reported nomenclature version |
| `hs6` | string | yes | Six-digit customs coordinate |
| `national_tariff_line` | string/null | production | Saudi line retained where available |
| `sector_profile` | enum | yes | Capability weight profile |
| `commercial_name_en/ar` | string | yes | Normalized bilingual names |
| `decision_object_status` | enum | yes | resolved, partially resolved or generic-HS-only |
| `application_boundary` | string | yes | Included and unresolved end-use boundary |
| `as_of_date` | date | yes | Reproducibility date |

### 2.2 Specification

| Group | Fields |
|---|---|
| Identity | material/chemical identity, model/part number, synonyms, excluded meanings |
| Composition | grade, purity, alloy, additive package, coating, impurity limits |
| Geometry | thickness, width, length, diameter, particle size, tolerance, surface, package |
| Performance | strength, barrier, conductivity, corrosion, temperature, pressure, sterility, shelf life |
| Standard | SASO, GSO, ASTM, ISO, EN, SFDA or customer standard and edition |
| Qualification | approved supplier, customer test, regulatory registration or application approval |
| Evidence | exact Arabic/English span, source, confidence and reviewer status |

The public steel case leaves the exact imported target specification unresolved. The simulated steel scenario adds a named, explicitly synthetic target specification.

### 2.3 TradeObservation

```json
{
  "year": 2024,
  "reporter": "Saudi Arabia",
  "partner": "World",
  "flow": "imports",
  "hs_revision": "H0",
  "hs6": "721049",
  "trade_value": 236.9,
  "currency": "USD_m",
  "net_weight": 287.9,
  "quantity_unit": "kt",
  "valuation": "CIF",
  "gross_flow": true,
  "reexport_status": "unresolved"
}
```

Value, weight, supplementary quantity and unit are never collapsed into one field.

§2.8 note: acquired analytical snapshots use source-qualified IDs (`UNIVERSE-SAU-<TAG>-…`, `TARIFF-SAU-<TAG>-…`, `PARTNERS-SAU-<TAG>-…`) and are never spliced into frozen public goldens. `PublicSnapshot 2.1` and `SUPPORT_CODES` are unchanged in S11. `NATIONAL_TARIFF_LINE_MAPPING` is acquisition-only until a later governed projection. No BACI snapshot kind exists in S11. S12a adds `DOMESTIC_PRODUCTION_AGGREGATE`, `ESTABLISHMENT_LICENCE_DIRECTORY` and `STANDARD_CONFORMITY_REGISTRY` only to `ACQUIRED_SUPPORT_CODES`; these do not extend the public decision support vocabulary or authorize a decision projection. S12b adds no support codes; document passports use existing codes only.

### AcquiredEvidencePassport 1.0.0

Eight §11 groups: `passport_id`, `source_id`, `synthetic_flag`, `status`, `evidence_class`, `reviewer_status`, `supports`, `source_identity`, `query_contract`, `retrieval`, `coverage`, `transformation_record`, `observation_context`, `measurement`, `contradiction_record`.

### 2.11 TariffLine

| Field | Meaning |
|---|---|
| `national_code` | 12-digit Saudi tariff line |
| `description` | Line description when present |
| `duty_rate` | Observed duty rate text |

### Acquisition snapshots 1.0.0

Kinds: `UniverseTradeSnapshot`, `TariffHierarchySnapshot`, `PartnerDetailSnapshot` at schema version `1.0.0`.

Mandatory keys include: `schema_version`, `snapshot_id`, `source_id`, `as_of_date`, `source_boundary`, `kind`, `nomenclature`, `coverage` (with `selection_rule`, `selected_run_id`, `superseded_run_ids`), `raw_artifact_refs` (with `path`, `sha256`, `unit_key`), `transformation_record`, `quality_summary`, `evidence`.

Universe snapshots carry `product_scope: ALL_HS6` sentinel. Partner snapshots carry `coverage.units_excluded` aligned with transformation exclusions.

S12a adds the following acquisition contracts, all at schema version `1.0.0`; a registered kind describes supported structure, not the existence or completeness of acquired source data.

| Snapshot type | Kind / stage | Source-qualified ID | Root |
|---|---|---|---|
| `ProductionAggregateSnapshot` | `production` / `AGGREGATE` | `PRODUCTION-SAU-GASTAT-<as_of>` | `data/snapshots/production/` |
| `EstablishmentDirectorySnapshot` | `directory` / `DIRECTORY` | `DIRECTORY-SAU-MINISTRY-OF-INDUSTRY-<as_of>` or `DIRECTORY-SAU-MODON-<as_of>` | `data/snapshots/directory/` |
| `StandardConformityRegistrySnapshot` | `registry` / `REGISTRY` | `REGISTRY-SAU-SASO-CATALOGUE-<as_of>` or `REGISTRY-SAU-SABER-REGISTRY-<as_of>` | `data/snapshots/registry/` |

Each institutional snapshot retains every mandatory key above and adds a nonempty `rows` array: `source_boundary` is `public`, `nomenclature` remains present (possibly `UNAVAILABLE`) but is not an ID segment, and `<as_of>` is the stored retrieval-derived ISO date, not the build date. One snapshot belongs to one `(kind, source_id)`; latest-run-per-source-stage-unit selection retains superseded runs. At least one selected unit must be COMPLETE, `coverage.units_excluded` must equal `transformation_record.exclusions`, and actual connector validation must pass before `quality_summary: PASS`; nonempty rows alone are insufficient. Raw references and acquired passports preserve source identity, coverage and transformations without joining sources or changing frozen public goldens.

Row contracts are field whitelists, with the original published text or `UNAVAILABLE` retained and no inferred product equivalence:

- `ProductionObservation`: `period_text`, `period_type_text`, `geography_text`, `activity_code_text`, `activity_classification_text`, `product_code_text`, `product_classification_text`, `indicator_text`, `value_original_text`, `value` (float or null), `unit_text`, `currency_text`, `estimation_flags` (strings), `source_dataset_id`, `source_evidence_id`; only published numeric text is parsed into `value`, with no unit conversion or HS mapping.
- `DirectoryRow`: `entity_name_ar`, `entity_name_en`, `record_type_text`, `licence_number_text`, `activity_description_ar`, `activity_description_en`, `activity_code_text`, `region_text`, `city_text`, `industrial_city_text`, `status_text`, `capacity_text`, `record_date_text`, `source_record_id`, `source_evidence_id`; capacity remains raw text, never a numeric nameplate or evidence of effective qualified supply.
- `RegistryRow`: `registry` (`saso_catalogue` or `saber_registry`), `standard_reference_text`, `title_ar`, `title_en`, `edition_or_year_text`, `scope_text`, `status_text`, `product_or_certificate_reference_text`, `conformity_type_text`, `issued_to_text` (observed text only), `validity_text`, `source_record_id`, `source_evidence_id`; registration does not establish compliance, qualification or approval.

Directory rows have no numeric capacity/nameplate fields; registry rows have no `compliance_confirmed`, `qualified` or `approved` flags; none of these row contracts admits person-name, phone or email fields. This schema restriction and the bounded store-time screening in Core 05 do not establish that arbitrary source values contain no personal data.

`transformation_record.config_version` at snapshot and passport level comes from the kind's governing `KindSpec.config_version` (`1.0.0` for universe/tariff/partners; `1.1.0` for production/directory/registry), not the current config metadata version; it identifies the acquisition-config source-contract semantics governing that kind, changes only through a §7.3 change to that kind's source contract, never rewrites a stored snapshot (later evidence follows §7.5 with history retained), and is independent of `pipeline_version`, which remains `1.0.0`.

### PublicSnapshot 2.1

A live public snapshot sets `schema_version: "2.1.0"`. The two frozen golden
files retain their snapshot IDs, as-of dates, and historical-v1 `supersedes`
links. A new snapshot with no predecessor may set `supersedes:
"UNAVAILABLE"`; an evidence refresh still follows Authority Manifest §7.5.

Evidence passports use the controlled support-code vocabulary defined by
Core 07 §7.2. Free-text support claims are invalid. `domestic_capability`
contains all configured `profile_hard_gates` with typed status and evidence
references, plus decision-specific unresolved gates.

`hard_exclusion_inputs` carries the six typed methodology §4.2 input blocks.
`decision_inputs` may carry target-specification demand, specification
equivalence, route evidence for routes 1–7, and a named monitor trigger.
Missing facts remain exact `UNAVAILABLE`.

The snapshot contains no `public_decision_contract`, authored state, route,
screening disposition, gap class, rule result, route-hypothesis result,
narrative, missing-fact list, condition, or kill-condition list. All are
computed.

### DocumentRecord 1.0.0

S12b stores span-addressable public documents as a parallel derived-record store under `data/documents/<source_id>/{lists,records}/`, separate from analytical snapshot kinds. Each record is one stored document URL (`Stage.DOCUMENT`), one raw page artifact and one derived text layer. Operator-authored **DocumentList 1.0.0** files under `data/documents/<source_id>/lists/` enumerate bounded entries before a live window; lists are hashed, validated fail-closed and never edited after a run.

**Identity:** `document_id_scheme` is `DOCUMENT_ID_V1`: `DOC-<SOURCE>-<query_hash[:12]>-<raw_sha256[:12]>`. Identical bytes report `ALREADY_STORED`; changed bytes retain history under a new id.

**Exact record keys:** `schema_version` (`1.0.0`), `document_id`, `document_id_scheme`, `source_id`, `source_boundary` (`public`), `kind` (`document`), `as_of_date` (retrieval date), `list_ref` (`path`, `sha256`, `list_id`, `entry_id`), `declared` (publisher/kind/language/type/class/support/title/date/reference copied verbatim from the list entry), `raw_artifact_ref` (source/stage/unit/query/run/artifact/path/sha256/compressed_sha256/byte_count/content_type/http_status/retrieved_at/endpoint_or_document), `coverage` (`LATEST_RUN_PER_SOURCE_STAGE_UNIT`, unit key, query hash, selected run, superseded runs, `COMPLETE` status), `text_layer`, `segmentation`, `page_count`, `line_count`, `pages`, `transformation_record`, `quality_summary`, `evidence` (one acquired passport).

**Text layer derivation (dev-only dependency `pypdf==6.16.1`; runtime image free of pypdf):**

| Content type | method_id | extraction |
|---|---|---|
| `application/pdf` | `PDF_TEXT_LAYER_PYPDF_LAYOUT` | layout mode; verbatim lines per page |
| `text/html`, `application/xhtml+xml` | `HTML_TEXT_LAYER_STDLIB` | stdlib block-tag extraction; script/style/template/noscript excluded |
| `text/plain` | `PLAIN_TEXT_LAYER_STDLIB` | strict UTF-8 |

Segmentation uses `LINE_SEGMENTATION_V1` / `1.0.0`: CRLF and lone CR become LF boundaries, exactly one trailing empty segment is dropped when text ends in LF, and all other lines remain verbatim. Each page carries `page_index`, `line_count`, `text_sha256 = sha256("\n".join(lines))` and `lines`. Every PDF page is retained in physical order with its 1-based PDF page number, including empty-text pages (`lines: []`, `line_count: 0`); `page_count` equals the physical PDF page count when the PDF is parseable. No OCR, normalisation or translation is applied.

**Text order (PDF):** `PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0` stores the PDF content-stream text order verbatim. Where a publisher PDF paints Arabic in visual (left-to-right glyph) order, the stored lines are visual-order Arabic; `quality_summary: PASS` denotes a COMPLETE extracted text layer, not logical reading order. Logical order is guaranteed only where the PDF's ToUnicode mapping yields it (the CID fixture case pinned by `test_arabic_cid_pdf_preserves_logical_order_verbatim`). No bidi reordering or reshaping is applied; logical-order recovery is S20 normalisation. Stored records affected by visual order are named in KNOWN_LIMITATIONS.

**Statuses:** `text_layer.status` is `COMPLETE` when at least one non-whitespace line exists on any page; otherwise `UNAVAILABLE` with `reason` `FORMAT_NOT_PARSEABLE` and `detail` in `{NO_TEXT_LAYER, PARSER_ERROR, NOT_UTF8}`. A parseable PDF with no text still retains all physical page entries for stable addressing. `quality_summary` is `PASS` for `COMPLETE` text layers and `RAW_ONLY` when the text layer is unavailable but the raw envelope was stored. `FORMAT_NOT_PARSEABLE` describes stored-body parse refusal at build time, not pre-storage policy refusals.

**Envelope policy (`DOCUMENT_ENVELOPE`):** exactly `application/pdf`, `text/html`, `application/xhtml+xml` and `text/plain` may be stored; other declared types are refused before storage as `OUT_OF_SCOPE_CONTENT` / `UnsupportedDocumentEnvelope` with hash-only metadata. Oversize bodies are honest `UNAVAILABLE` under unchanged raw-store budgets.

`transformation_record.config_version` for documents is `1.2.0` (acquisition config semantics); `pipeline_version` remains `1.0.0`. The builder selects the latest run per source/stage/unit and records every sorted prior run id in `coverage.superseded_run_ids`; records then pin that selected raw run and re-derive byte-for-byte under document reconstruction. No numeric, normalised capacity/compliance or personal-data fields appear in the record contract.

### 2.4 Plant and ProductionLine

| Field | Meaning |
|---|---|
| `plant_id`, `company_id`, `parent_group_id` | Persistent entity IDs |
| `line_id` | Specific production line |
| `process_route` | Physical/chemical transformation sequence |
| `equipment_envelope` | Dimensions, scale, operating conditions and tolerances |
| `nameplate` | Published or verified installed capacity |
| `availability` | Time available for production |
| `yield` | Good output / input |
| `qualification_share` | Share capable of the target specification |
| `market_allocation_share` | Share available to the target market and window |
| `utilisation` | Actual effective load, not assumed from nameplate |
| `certifications` | Quality, lab, regulatory and customer approvals |

**S12c entity identity — EntityResolutionArtifact 1.0.0 and EntityMentionList 1.0.0**

`ENTITY_ID_V1` has separate `COMPANY`, `PLANT`, `LINE` and `LICENCE_HOLDER` namespaces. Company and licence-holder keys use the exact-normalised first-observed primary name; plant and line keys additionally use their parent id and locality token or designation. IDs are never re-issued, and jurisdiction is an observed attribute rather than a key component. `NAME_NORMALISATION_V1` retains every verbatim span beside exact and variant forms; visual-order Arabic is flagged and normalized character-for-character, never reversed or reshaped. Operator labels are never evidence.

Resolution uses only the ordered statuses `DETERMINISTIC_IDENTIFIER`, `EXACT_DOCUMENT_EVIDENCE`, `PROPOSED_PENDING_REVIEW` and `UNRESOLVED`; only the first two are resolved. There is no fuzzy score or inferred identity. A plant supported only to locality granularity is `SITE_LOCALITY`, and a company name alone never mints a plant. Ownership, name-change and merger facts are dated records on persistent IDs.

Operator-authored `EntityMentionList 1.0.0` inputs live under `data/entities/mentions/`; write-once `EntityResolutionArtifact 1.0.0` outputs live under `data/entities/resolution/`. Each artifact records the mention-list, rule-table, DocumentRecord and public-snapshot hashes, entity and link evidence, passport and observation links, unresolved states, and byte-reconstruction parameters.

### 2.5 CapabilityAssessment

```json
{
  "sector_profile": "coated_steel",
  "dimensions": [
    {"dimension": "core_process_route", "weight": 0.20, "state": 0, "known": true},
    {"dimension": "capacity_time_window", "weight": 0.10, "state": "U", "known": false}
  ],
  "known_weight_coverage": 0.75,
  "unknown_weight": 0.25,
  "d_known": 0.18,
  "internal_d_star_before_gate": 0.305,
  "d_star": null,
  "unresolved_hard_gates": ["customer qualification"],
  "route_publishable": false
}
```

An internal calculation may exist for diagnostic purposes, but `d_star` remains null when publication controls fail.

### 2.6 DemandScenario

Demand layers remain separate:

- `base`
- `committed`
- `announced`
- `downside`
- `upside`

Each layer records quantity, timing, probability, buyer/application and evidence status. Announced demand is not silently added to the base.

### 2.7 EconomicsCase

| Block | Fields |
|---|---|
| Investment | engineering, equipment, construction, certification, working capital, contingency, commissioning |
| Operations | feedstock, utilities, labor, yield, ramp, maintenance, EHS, logistics and inventory |
| Revenue | volume and price by target specification, domestic/export split and timing |
| Finance/tax | hurdle rate, tax, depreciation, financing, incentive timing and residual value |
| Risk | technology, price, demand, feedstock, qualification and delay sensitivities |
| Output | unsupported NPV/IRR, S\*, supported NPV/IRR and scenario results |

### 2.8 EvidencePassport

Every decision-relevant fact must carry:

```json
{
  "evidence_id": "S-UNICOIL-EPD",
  "title": "UNICOIL 2024 Environmental Product Declaration",
  "source": "UNICOIL",
  "url": "...",
  "period": "2023/2024",
  "retrieved_at": "2026-08-31",
  "status": "observed",
  "evidence_class": "C",
  "synthetic_flag": false,
  "supports": ["installed capacity", "process route"],
  "transformation": null,
  "contradiction": "published coating range differs from web page",
  "reviewer_status": "unconfirmed by responsible authority"
}
```

### 2.9 SyntheticScenario

```json
{
  "scenario_id": "SYN-MINISTRY-STEEL-001",
  "opportunity_id": "SAU-H0-721049",
  "synthetic_flag": true,
  "display_label": "SIMULATED — NOT MINISTRY EVIDENCE",
  "seed_basis": "Public import and nameplate marginals",
  "evidence_class": "D",
  "source": "DEMO_GENERATOR",
  "synthetic_inputs": {
    "class_if_confirmed": {
      "product_identity": "A",
      "demand_at_required_specification": "A",
      "domestic_supply_or_capability": "A",
      "hard_regulatory_or_process_gate": "B"
    }
  }
}
```

The scenario is not inserted into the public opportunity record. It is loaded through a separate repository method.

### 2.10 DecisionRecord

```json
{
  "state": "INVESTIGATE",
  "route_code": null,
  "screening_disposition": "CANDIDATE",
  "route_label": "Brownfield priority to test",
  "headline": "INVESTIGATE — binding constraint unresolved",
  "rationale": "...",
  "confidence": "C",
  "gap_class": {},
  "evidence_class_assessment": {},
  "hard_exclusions": [],
  "route_hypotheses": [],
  "preferred_hypothesis": {},
  "narrative_version": "1.0.0",
  "conditions": [],
  "kill_conditions": [],
  "missing_facts": [],
  "decision_reason_code": "ROUTE_CHANGING_EVIDENCE_UNRESOLVED",
  "advance_support_signal_rule_ids": ["R2", "R3", "R9-S"],
  "synthetic_flag": false
}
```

Simulation creates a second `DecisionRecord` with `synthetic_flag=true`. The public record remains immutable.

## 3. Aggregate response contract

```json
{
  "opportunity": {},
  "snapshot_id": "PUBLIC-SAU-H0-721049-2026-08-31",
  "mode": "simulated",
  "real_decision": {},
  "simulation_decision": {},
  "active_decision": {},
  "screening_disposition": "CANDIDATE",
  "gap_class": {},
  "evidence_class_assessment": {},
  "hard_exclusions": [],
  "route_hypotheses": [],
  "preferred_hypothesis": {},
  "narrative_version": "1.0.0",
  "rules": [],
  "capacity": {},
  "capability": {},
  "economics": {},
  "competition": {},
  "evsi": {},
  "trade": [],
  "evidence": [],
  "data_unlocks": [],
  "synthetic_inputs_used": [],
  "integrity": {}
}
```

## 4. Identity and keys

- Opportunity IDs are stable across snapshot revisions.
- Snapshot IDs include boundary, opportunity and as-of date.
- Evidence IDs are stable within a source contract.
- Scenario IDs are unique and never reused for a different synthetic truth set.
- A future production decision ID should include opportunity, as-of date and decision version.
- `ENTITY_ID_V1` ids derive from type plus the exact-normalised first-observed primary name (and parent id plus locality/designation for plants and lines) and are never re-issued; later names, mergers and ownership changes are dated records on the same id.

## 5. State enums

### Evidence status

```text
observed | calculated | model_estimated | inferred | assumption | unresolved | synthetic
```

### Evidence class

```text
A | B | C | D | E
```

### Rule execution

```text
FULL | DEGRADED | DISABLED
```

### Decision state

```text
REJECT | MONITOR | INVESTIGATE | ADVANCE
```

### Capability state

```text
0 | 1 | 2 | 3 | U
```

## 6. Data invariants

1. `synthetic_flag` is mandatory on every evidence row.
2. A public snapshot may not contain `synthetic_flag=true`.
3. A synthetic scenario may not omit scenario ID, seed basis, source, class or warning label.
4. `real_decision.synthetic_flag` is always false.
5. `simulation_decision.synthetic_flag` is always true.
6. `d_star` is null when route publication controls fail.
7. R4-D output cannot contain `grade_confirmed=true` or a cluster label.
8. Values and quantities retain units.
9. Gross flows are never labeled retained imports.
10. Missing years are explicit; no implicit interpolation.

## 7. Relational production mapping

A production implementation can normalize to:

```text
opportunity
classification
specification
application
trade_observation
company
plant
production_line
capability_dimension
capacity_observation
demand_scenario
economics_case
intervention_case
evidence_passport
rule_execution
decision_record
decision_condition
snapshot
```

## 8. Graph production mapping (v2)

The evidentiary system of record remains the canonical files governed by this
document. `data/graph/` is a deterministic, idempotently rebuildable
projection; Neo4j is a live mirror of that projection and is never a second
source of truth. A node or edge enters the projection only from a named
canonical record or a deterministic engine run over those records.

### 8.1 Governed node vocabulary

The exact 19 labels are:

```text
Product, TariffLine, Specification, Application, Plant, ProductionLine,
Process, Equipment, Capability, Standard, Certification, Input, Technology,
Company, CustomerSegment, Evidence, Scenario, Decision, Intervention
```

- `Product.id` is the persistent opportunity id.
- `TariffLine` is created only from a COMPLETE tariff unit. Until one exists,
  the graph carries the single `TARIFF-SA12-UNAVAILABLE` marker and no
  `CLASSIFIED_AS` edge.
- Public target specifications remain typed `UNAVAILABLE` markers when the
  canonical snapshot does not resolve them. Synthetic target specifications
  remain Class D and scenario-scoped.
- `Plant` and `Company` use `ENTITY_ID_V1` where an exact governed entity link
  exists. A snapshot producer without such a link receives a deterministic
  `PRODUCER-<snapshot>-<index>` id with
  `identity_basis=SNAPSHOT_PRODUCER_LABEL`; it is not asserted to be a legal
  entity match.
- `Decision`, route `Intervention`, D*, `ADJACENT_TO`, and route/evidence
  constraints are derived engine outputs. They carry `derived=true` and an
  `engine_run_id` and never feed an engine-input function.
- `Input`, `Technology`, and `Equipment` remain valid types even when no
  governed fact currently instantiates them.

### 8.2 Governed edge vocabulary

The exact 15 relationship types and allowed directions are:

| Relationship | Allowed endpoints |
|---|---|
| `CLASSIFIED_AS` | Product → TariffLine |
| `REQUIRES_SPECIFICATION` | Product or Application → Specification |
| `USED_IN` | Product → Application |
| `PRODUCED_BY` | Product → Plant, Company or ProductionLine |
| `HAS_LINE` | Plant → ProductionLine |
| `USES_PROCESS` | Plant, ProductionLine or Company → Process |
| `HAS_CAPABILITY` | Product → Capability |
| `REQUIRES_INPUT` | Process or ProductionLine → Input |
| `CERTIFIED_TO` | Plant or Company → Certification or Standard |
| `QUALIFIED_FOR` | Plant, ProductionLine or Company → Specification or Application; CustomerSegment → Application |
| `DEPENDS_ON` | Product → Product/Input/Technology/Process; Process → Equipment; Decision → Intervention |
| `ADJACENT_TO` | Plant or Company → Product |
| `SUPPORTED_BY_EVIDENCE` | any governed node → Evidence |
| `CONSTRAINED_BY` | Intervention/Decision/Specification/Product → the permitted blocking node |
| `UNLOCKED_BY` | Product → shared-enabler Intervention |

### 8.3 v1 → v2 mapping

| v1 name | v2 meaning |
|---|---|
| `Opportunity` | `Product`, keyed by opportunity id |
| `Buyer` | `CustomerSegment` |
| `Utility` | `Input` with utility kind |
| `HAS_SPECIFICATION` | `REQUIRES_SPECIFICATION` |
| `REQUIRES_STANDARD` | `CONSTRAINED_BY` from Specification to Standard |
| `REQUIRES_EQUIPMENT` | `DEPENDS_ON` from Process to Equipment |
| `QUALIFIED_BY` | `CERTIFIED_TO` |
| `DEMANDED_BY` | `USED_IN` plus the application/customer qualification relation |
| `BLOCKED_BY` | `CONSTRAINED_BY` |
| `ALTERNATIVE_TO` | retired; one Decision owns ordered Intervention route records through `DEPENDS_ON {role}` |

The unchanged v1 labels and edges retain their v2 names. The mapping adds no
sixteenth relationship type.

### 8.4 Provenance and partition

Every node and edge has non-null `evidence_id`, `as_of`, `evidence_class`,
`synthetic_flag`, and `scenario_id`, plus `origin_kind`, `origin_ref`,
`projection_id`, and `derived`. Public elements use the explicit
`scenario_id='PUBLIC'` sentinel because Neo4j does not retain null
properties. Synthetic elements use their scenario id, Class D,
`source=DEMO_GENERATOR` through their Evidence origin, and both policy-owned
warning labels.

A synthetic edge may start at a public Product to attach a Class-D
scenario declaration. A public edge may never end at or start from a
synthetic node. Every public query filters both nodes and relationships on
`synthetic_flag=false`.

### 8.5 Artifact contract

The write-once layout is:

```text
data/graph/current.json
data/graph/projections/<projection_id>/projection.json
data/graph/projections/<projection_id>/manifest.json
```

`projection_id` is derived from the canonical governed input identities and
the maximum public as-of date. Nodes are sorted by `(label,id)` and edges by
`(type,source,target,key)`. The artifact retains rich JSON values; the Neo4j
loader stores only primitives or homogeneous primitive arrays and encodes
non-query nested values as canonical JSON text. Rebuilding identical inputs
must produce identical bytes and `GRAPH RECONSTRUCTION PASS`. The original
methodology, current Core/config bytes and engine sources are direct inputs;
generated authority/snapshot manifests are integrity outputs, not projection
inputs, which avoids a circular graph→manifest→graph identity.

### 8.6 Shared-enabler input and provenance

A non-derived `UNLOCKED_BY` relationship carries `unlock_probability`, `dependency_share`, positive `dependent_incremental_national_value_m_sar`, `valuation_route_code` and the precise `valuation_input_reference`. Its source is a public Product; a simulated relationship is Class D and its scenario membership resolves to one non-derived Scenario whose `opportunity_id` equals that Product. The target shared-enabler Intervention carries the common declaration, both labels, scenario membership list, cost and component evidence. Public and simulated feeds reject derived, ambiguous, unrelated or partition-invalid elements.

The route input aligns dependent opportunity IDs, probabilities, values, shares, valuation codes and references and retains the graph projection identity. Evaluated route 8 adds a `shared_enabler` audit block; the legacy `GRAPH_REQUIRED` record contains no evaluated-only fields.

## 9. Dossier projection

The Decision Dossier is a projection, not a separate source of truth. It is generated from the canonical record and includes:

- decision headline;
- identity;
- demand and supply conclusions;
- gap;
- capability route;
- economics;
- competition/policy;
- evidence summary;
- conditions and kill conditions.

## 10. Evolution rule

A new field may be added when it is required by the methodology or a source contract. A field may not be repurposed to carry a different concept merely because it is convenient. Version the schema when meaning changes.

## 11. ScreeningSnapshot 1.0.0

`ScreeningSnapshot` is public, synthetic-free and write-once under
`data/screening/snapshots/`. Its identity is
`SCREENING-SAU-<as_of_date>-<sha256(canonical inputs)[:12]>`. It contains
input paths/hashes/versions; typed universe status; coverage accounting;
HS6-sorted screening records; five route-specific queues; recomputable counts;
the methodology §8.2 mapping; compact evidence passports; and a versioned
transformation record.

Records carry coded rule execution, warnings, exclusions, dispositions,
indicated states, monitor triggers and evidence needs. They never carry formal
`state`, `route_code`, `d_star`, `public_decision_contract`, or synthetic data.
An unavailable universe requires zero records and empty queues. Per-row
`hs_revision` is preserved from the acquired source; each `(year, flow)` unit
must have exactly one revision. No snapshot-level revision list is required.

The unchanged logical schema version `1.0.0` is stored as a write-once
directory:
`data/screening/snapshots/<snapshot_id>/summary.json`,
optional `queues.json`, and `records/<hs2>.json` shards. `summary.json`
contains every top-level field except `records`, a sorted `record_shards`
index (`path`, `hs2`, `record_count`, `sha256`), and
`common_record_fields`. Fields identical across all records are omitted from
the shards and restored by the loader. `queues.json` is used when the queue
block exceeds 1 MiB; otherwise queues remain inline in `summary.json`.
Every file is canonical JSON and write-once. Validation checks the complete
directory, shard hashes/counts, logical record schema, forbidden fields,
per-file and total budgets, and exact file-set reconstruction. Runtime record
lookups load only the indexed HS2 shard; summary and queue metadata are eager.

### 11.1 Superseded operating-configuration inputs

A screening snapshot continues to identify the repository-relative
configuration path and SHA-256 that governed its build. When the current file
has a different approved version, validation may resolve that identity only
against an exact content-hash match under `config/history/`. History files are
immutable superseded bytes, separately manifested, and never substitute for
`data/**` inputs. No matching retained file, an ambiguous match, or any
non-config mismatch fails closed as `INPUTS_CHANGED`; the screening snapshot is
not rebuilt merely to relabel an unchanged historical decision cycle.

## 12. CaseBrief 1.1.0 and derived PublicSnapshot provenance

`CaseBrief 1.1.0` is the governed analyst-to-code boundary for a selected deep
case. It is public, synthetic-free and write-once under
`data/cases/briefs/CASE-BRIEF-SAU-H6-<hs6>-v1.json`. The paired opportunity id
is `SAU-H6-<hs6>`. A brief contains:

- the HS6, H6 revision, sector profile and `LATEST_REVISION_ONLY` trade rule;
- source snapshot ids plus an exact-key `partner_detail` block. Its state is
  `PARTNER_DETAIL_OBSERVED`, `PARTNER_DETAIL_MISSING` or
  `PARTNER_TRADE_OBSERVED_ZERO`; the missing reason is the complete
  `UnavailableReason` vocabulary plus `NOT_ACQUIRED` and
  `REVISION_MISMATCH`. Every stored attempt resolves a repo-relative contract
  path and hash. OBSERVED requires non-World rows; ZERO requires a COMPLETE
  `NORMALIZED_EMPTY` provider envelope with count zero; UNPARSED/PENDING can
  only support MISSING and never proves zero.
  `PARTNER_DESCRIPTIONS_UNAVAILABLE` means normalized rows whose only failed
  completeness predicate is missing non-World descriptions. Superseded
  attempts on an OBSERVED case use
  `PARTNER_DETAIL_ATTEMPT_SUPERSEDED:`; an untransmitted governed variant is
  described as `VARIANT_NOT_TRANSMITTED` in that transformation text rather
  than as an API outcome;
- English commercial identity tied to stored WCO legal-text spans (or an
  explicitly flagged analyst description), with Arabic marked
  `ANALYST_TRANSLATION`;
- application and authority boundaries that do not impersonate a product-
  specification decision;
- document-evidence rows and exact one-based
  `(document_id, page_index, line_index, span_text)` addresses;
- capability booleans, process facts, standards, nameplates, dimension states
  and resolved hard gates only when their `span_ids` resolve verbatim to a
  COMPLETE Class A/B/C DocumentRecord; otherwise booleans/nameplates/gates are
  `UNAVAILABLE` and dimensions are `U`; and
- no authored state, route, rule result, screening disposition, synthetic
  input or scenario truth.

The deterministic projection builds `PublicSnapshot 2.1.0` with id
`PUBLIC-SAU-H6-<hs6>-<universe_as_of>`. It retains only H6 rows for 2022–2024;
the 2021 H5 row is excluded rather than concorded or spliced. Published USD is
divided by 1,000,000 to `USD_m`; kilograms are divided by 1,000,000 to `kt`;
unit value is calculated only when both positive operands exist. Partner rows
come only from the named source-qualified partner snapshot and exclude the
World aggregate. PublicSnapshot 2.1.0 carries OBSERVED as rows plus a
source-qualified calculated passport, MISSING as `UNAVAILABLE` plus unresolved
attempt passports, and ZERO as `UNAVAILABLE` plus an observed ZERO passport;
the authority note and execution cap repeat the typed marker. The original
attempt remains visible when a substitute source is tried. Every capability
value maps cited spans to the corresponding public evidence passport. All
unobserved domestic flows, hard-exclusion inputs, target-specification demand,
equivalence, route evidence and monitor trigger remain exact `UNAVAILABLE`.

The builder validates before writing and is byte-deterministic. In S14a the
five outputs are built only to a temporary directory, so the portfolio roots
remain unchanged. `CASE RECONSTRUCTION PASS (<committed> snapshots, <briefs>
briefs)` validates every brief and, once S14b commits a derived snapshot,
compares the committed bytes with a fresh brief + universe + partner +
DocumentRecord projection.

S14b formalizes the carrier as version-gated `PublicSnapshot 2.2.0`.
Its exact-key `partner_detail` block contains exactly:

- `state`
- `reason`
- `source_id`
- `partner_snapshot_id`
- `unit_key`
- `observed_partner_rows`
- `attempt_passport_ids`
- `observed_passport_id`

The source ID and partner-snapshot ID identify the source-qualified input, or
carry explicit `UNAVAILABLE`; the unit key must identify the opportunity HS6,
imports and 2024. OBSERVED requires a positive row count equal to the partner
observations and a calculated public observed passport referenced by every
row; unresolved superseded attempts remain named. MISSING requires
`UNAVAILABLE` partner observations and row count, a governed missing reason,
a null observed-passport ID and unresolved attempt passports, except that
`NOT_ACQUIRED` may have no attempt. ZERO requires `UNAVAILABLE` partner
observations, row count zero, null reason and a public observed zero passport
whose ID ends `-PARTNERS-ZERO`. The builder derives every value from the
validated CaseBrief and referenced evidence; the block is never authored in a
snapshot.

PublicSnapshot 2.1.0 records remain valid unchanged. They retain the
passport-marker carrier above and do not acquire an authored 2.2.0 block.
Only the five S14b derived snapshots use 2.2.0. Concentration, R3, R4-D,
GenUI and dossier projections consume the typed state: missing evidence stays
`NOT_CALCULABLE`, observed zero stays distinct, and no absent value becomes
numeric zero.

`DocumentList 1.0.0` publisher kinds additionally include
`nomenclature_authority`, restricted to `wco_hs_nomenclature`, Class B and
`TARGET_PRODUCT_IDENTITY`; it cannot support producer capability or nameplate
facts.

## 13. S15 selection and scoped partner-snapshot identity

`S14-CS-1.1` extends the version-gated case-selection record. Before tiering it
removes every candidate with classification-continuity gaps as
`SERIES_GAP_YEARS`; each row records the missing import years, and missing
years are not observations of zero trade. Residual identity removal is allowed
only through a hashed `identity_exclusions` row carrying the HS revision,
reason, verbatim WCO text and stored page/line address.

The write-once S15 record is
`CASE-SELECTION-S15-b96de36ff0ce`. Its input block freezes the four document
identities available at T5. Reconstruction resolves those recorded identities
and compares canonical bytes; it does not substitute documents acquired later.
A current-state diagnostic after W-A15b includes a fifth SABIC Agri-Nutrients
record and therefore has a different digest, while retaining the same four
selected HS6 codes. That diagnostic is not a replacement selection record.

An acquired snapshot normally retains
`<KIND>-SAU-<SOURCE>[-<NOMENCLATURE>]-<as_of_date>`. When a different unit set
would collide at the same kind, source, nomenclature and date, only the new
record gains `-<scope12>`, where `scope12` is the first twelve hexadecimal
characters of SHA-256 over the canonical sorted unit keys. The scoped record
stores those keys in `scope_units` and a one-way `coexists_with` reference to
the unscoped sibling; it must not carry `supersedes`. Validation requires the
sibling to exist, requires equal identity dimensions, recomputes the suffix,
and rejects overlapping unit keys. Reconstruction uses each record's own
recorded units. Thus
`PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196` contains only the four S15
units and coexists with the unchanged S14a snapshot for its disjoint unit set.

`DocumentList 1.0.0` also admits `regulatory_authority` only for
`sfda_registers`, Class B and its configured support codes. This source kind
does not turn a company-list observation into product capability, production
or qualification evidence.

## 14. S15b public selection and optional EVSI projections

`GET /api/case-selection` projects only the manifest-verified write-once
`CASE-SELECTION-S15-b96de36ff0ce` record. Its response schema is `1.0.0` and
contains `source_boundary: public`, `synthetic_flag: false`, the selection and
rule identities, the repository-relative selection reference and hash, recorded
public input references, and ordered `pharma_api` then `fertilizers` profile
objects. Each profile retains its quota, selected pair, substitution order,
rows, and complete identity, viability, series-gap and frozen-case exclusions.
The endpoint takes no caller-selected file path and its result does not vary by
evidence mode.

The aggregate analysis field `evsi` is either the existing calculation mapping
or JSON `null`. Null means no EVSI calculation occurred because the optional
`synthetic_inputs.evsi` key was absent; it is not numeric zero and does not mean
that evidence has no decision value. If the key is supplied, it must remain a
mapping with all four required inputs and values accepted by the existing
calculation. Supplied null, wrong-type, empty, partial or non-convertible blocks
fail with the existing evidence-integrity error instead of becoming null.

The four S15b dossiers use version `1.3` and add
`evidence_summary.selection` with the selection id, rule version, repository
reference and sector profile. Earlier dossier records remain version `1.2` and
do not acquire that field.
