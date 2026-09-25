# 09 — Test Strategy, Acceptance Gates and Golden Cases

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Objective

Testing must prove methodological fidelity, not merely code coverage. The highest-risk defects are:

- synthetic evidence leaking into the real decision;
- hidden threshold drift;
- an unknown capability state improving adjacency;
- a degraded unit-value diagnostic becoming a grade claim;
- a live source revision changing CI;
- an agent loosening a golden outcome to make a preferred result pass.

## 2. Test layers

### 2.1 Integrity

- governed files exist;
- SHA-256 matches authority and snapshot manifests;
- public snapshots contain no synthetic evidence;
- synthetic scenarios contain mandatory metadata.

### 2.2 Formula unit tests

- log decomposition identity;
- quantity contribution share;
- effective qualified capacity;
- K/U/D\* and λ penalty;
- Kmin/hard-gate publication control;
- NPV and IRR;
- S\* minimum-step behavior;
- incremental national value;
- EVSI.

### 2.3 Rule tests

- R1-D boundary;
- steel R2 fires;
- PP R2 does not fire;
- steel R3 fires;
- R4-F disabled on annual data;
- R4-D never claims grade;
- PP R11 generic-capacity warning fires.

### 2.4 Golden end-to-end tests

#### Golden A — Steel public

Expected:

```text
real state = INVESTIGATE
active state = INVESTIGATE
route code = null
D* not published
R1-D fires
R2 fires
R3 fires
R4-D fires
R9-S fires
greenfield not justified
```

#### Golden A-S — Steel simulation

Expected:

```text
real state remains INVESTIGATE
simulation state = ADVANCE
route code = 5
effective qualified capacity = 57.509 kt
gap = 46.491 kt
D* route = incremental upgrade
unsupported NPV = -18m
unsupported IRR = 9.5%
S* = 18m
incremental national value = 198m
post-entry capacity ratio <= 1.25
```

#### Golden B — Polypropylene public

Expected:

```text
real state = REJECT
route code = 0
R1-D fires
R2 does not fire
R11 fires
only named grade/application exceptions remain investigable
```

#### Golden B-S — Polypropylene simulation

Expected:

```text
real state remains REJECT
simulation state = REJECT
qualified availability > target demand
specification-adjusted gap < 0
support = 0
```

#### Golden C — Galvalume

Public `SAU-H6-721061` computes INVESTIGATE/null. Scenario
`SYN-MINISTRY-GALVALUME-001` computes ADVANCE route 3 for certification and
customer qualification; `real_decision` remains INVESTIGATE.

#### Golden D — Tinplate

Public `SAU-H6-721012` computes INVESTIGATE/null. Scenario
`SYN-MINISTRY-TINPLATE-001` computes ADVANCE route 7 only after routes 0–6
fail or cannot fully resolve the constraint; `real_decision` is unchanged.

#### Golden E — Aluminium foil

Public `SAU-H6-760711` computes INVESTIGATE/null. Scenario
`SYN-MINISTRY-ALU-FOIL-001` computes ADVANCE route 6 for technology licensing,
a specialist line or joint venture; `real_decision` is unchanged.

#### Golden F — Aluminium profiles

Public `SAU-H6-760429` computes INVESTIGATE/null. Scenario
`SYN-MINISTRY-ALU-PROFILES-001` computes ADVANCE route 4 with zero financial
support because conditional offtake resolves the quantity gap;
`real_decision` is unchanged.

#### Golden G — PE film

Public `SAU-H6-392010` computes INVESTIGATE/null. Scenario
`SYN-MINISTRY-PE-FILM-001` computes REJECT route 0 because equivalent
qualified availability exceeds target demand and no binding market failure
remains; `real_decision` is unchanged.

For Goldens C–G, Gate B independently computes and compares state and route
with scenario ground truth. All five public snapshots are builder-derived
2.2.0 records; no scenario field can alter a real decision.

### 2.5 Extraction golden tests

- four labeled AR/EN fields;
- exact normalized output;
- exact source spans retained;
- 100% pass required for the offline fixture.

### 2.6 API tests

- health endpoint;
- opportunity listing in both modes;
- analysis response contract;
- UI manifest approved component types;
- dossier JSON and HTML;
- extraction endpoint.

### 2.7 Frontend contract and real-browser visual tests

Static contracts shall enforce the approved component registry, token-only styling,
ES-module boundaries, catalogue parity, synthetic disclosure and offline assets.
Real Chromium tests shall exercise every supported locale, evidence mode, primary
control and approved viewport, including keyboard focus, WCAG 2.1 A/AA, bidirectional
layout, intended-font rendering, dossier print/PDF, console and network failures.
Post-redesign visual baselines are hashed test oracles: comparison is deterministic,
updates require an explicit reviewer-approved procedure, and CI shall never update them.
The delivered S16b matrix has 96 entries. S17 adds four graph screens across
two locales and the existing two viewports, producing 112 images only through
the separately authorized canonical generation. The graph captures identify
fixture-backed UI evidence separately from the live-Cypher gate and include the
fixed catalogue, fixture/capture sources, current graph pointer and referenced
projection files in visual provenance. All paths remain opaque lossless RGB
WebP with the fixed 600 KiB per-file and 16 MiB aggregate budgets and unchanged
comparison tolerances. CI only compares and never updates.

Arabic analytical parity has two parts. First, governed prose and code labels
must come from the Arabic catalogues; verbatim source spans and classified
technical values are the only permitted LTR islands. Second, outside those
islands an Arabic container must have no run of three or more alphabetic Latin
words. Each island must match the technical-value grammar or be a verbatim
source span marked `lang=en` with a catalogue caption. Tests also reject any
catalogue label disguised as a `code_token`, `catalogue_key`, or `governed_id`.
The grammar can admit ALL-CAPS English words, snake/dotted lowercase English
and Title-Case-plus-digit strings; content parity therefore also requires
English-template equality and the catalogue-label leak check.

S18b AM2 extends §2.7 with literal source-name regression, the real Arabic-name branch, exact six-island whole-graph Arabic parity for the canonical steel adjacency case, five independent source-disclosure mutation oracles, malicious-name escaping, and containment of controls and text at390/1024/1440 in both locales. At390, real Tab/Arrow navigation must reach both diagram scroll endpoints and every native element; whole-document axe remains required. All four graph views exercise loading, empty, unavailable, invalid, transport-error and retry states in public and simulation mode. Existing geometry, collision, source, isolation and visual assertions remain in force.

### 2.8 Graph projection and live-Cypher tests

Offline tests validate the stored `data/graph/` export, exact 19-label and
15-edge vocabulary, endpoint rules, canonical ordering, write-once behavior,
input-derived identity, provenance completeness, public/Class-D partition,
derived-output flags and two-build byte equality.

Live tests are isolated under `graph_tests/`, outside default `testpaths`.
They require `IOR_GRAPH_TEST_EXPLICIT=1`, delete or reject inherited Aura
connection state, and permit only the local Compose or isolated CI target.
The designated graph gate creates all 19 uniqueness constraints, loads by
governed id, proves a second load creates 0/0, compares every label/type count,
checks provenance and partition with Cypher, and compares the four fixed
Cypher views with deterministic artifact functions. With the service stopped,
the API must return typed `GRAPH_UNAVAILABLE`, never HTTP 500 or an artifact
fallback.

`scripts/reconstruct_snapshot.py --all` additionally rebuilds the current
projection from its recorded governed inputs and emits
`GRAPH RECONSTRUCTION PASS`. Scenario validation preserves the original ten
checks and appends `shared_enabler_declaration_valid` as check 11, followed by
the separate ground-truth back-test. It proves exact common declaration
agreement, explicit valuation references, 35.28 for the governed pair,
ADVANCE/8 at 178 for the honest fixture and unchanged governed routes 6/4.
The Aura suite is operator-only and cannot collect without both the operator
flag and exact instance confirmation.

S17 adds a distinct `graph_ui` marker and loopback-only browser test after the
existing graph-only suite and before service stop. Its modules must import and
collect in a locked dev-only environment where Playwright, Neo4j and Pillow are
absent; optional imports, browser launch and driver creation occur only inside
the explicit live path after target guards. The test verifies the preloaded
projection, uses no graph-response interception, exercises the four fixed views
in both locales, compares rendered element identities with live API responses,
and verifies mirror identity and counts again afterward. Local and hosted graph
gates retain the order graph-only → graph UI → stop → unavailable.

## 3. Threshold boundary tests

For every threshold, include below/equal/above cases where applicable.

Examples:

```text
R2 share: 0.5999 / 0.6000 / 0.6001
R3 HHI: 0.2499 / 0.2500 / 0.2501
Kmin: 0.6999 / 0.7000 / 0.7001
D* bands: 0.20, 0.40, 0.65
capacity ratio: 1.2499 / 1.2500 / 1.2501
```

## 4. Synthetic leakage tests

Required assertions:

1. public evidence rows all set `synthetic_flag=false`;
2. public analysis contains no synthetic row;
3. simulated analysis contains both public and labeled synthetic rows;
4. public-decision fingerprint before and after simulation is identical;
5. simulated dossier includes disclosure;
6. real dossier does not include a synthetic disclosure;
7. a malformed synthetic scenario fails closed;
8. all four mounted screening routes are public-only: their JSON contains no
   synthetic marker, the summary and evidence payloads are unchanged by
   `?mode=simulated`, and the route does not accept a mode contract; and
9. every screening DOM view remains free of both evidence-policy synthetic
   warning labels while simulated opportunity mode is active, and screening
   requests carry no `mode` query parameter.

TL-09 assertions 8 and 9 extend the synthetic-isolation boundary to the
summary, queue, record and evidence-passport screening surfaces.

TL-09 assertions 10–12 extend the boundary to the graph:

10. every public graph query filters nodes and relationships with
    `synthetic_flag=false`;
11. no synthetic node or edge appears on a public graph payload or feeds a
    real-decision graph input; and
12. every public node and edge carries `synthetic_flag=false` and the
    `scenario_id='PUBLIC'` sentinel, while every synthetic element carries
    Class D, its scenario id and both visible warning labels; and
13. the graph serializer filters evidence-support edges to public or the exact
    selected simulated scenario, derives synthetic state from nodes and edges,
    and the browser rejects any synthetic element delivered to a public view.

## 5. Snapshot test policy

Golden cases never pull live Comtrade, WITS, BACI, company pages or standards.

Acquired snapshots receive their own source-qualified IDs and are never spliced into goldens or across sources.

A source refresh process creates a new candidate snapshot and runs comparison tests. If the result changes, reviewers determine whether the change reflects:

- a legitimate data revision;
- a classification change;
- a source error;
- an implementation defect;
- a methodology/calibration issue.

Tests are not loosened merely because a live source changed.

### Public snapshot schema-migration proof

Golden schema migrations retain the historical bytes and compare a test-only
legacy evaluation with the live schema result. For every migrated golden the
proof deep-compares every ordered rule and response identity/state field,
failing on any difference outside an exact old/new allow-list. The allow-list
contains steel R11 execution `DEGRADED` to `FULL`, steel compatibility ratio
`null` to `0.1144`, individually named additive metric keys, and the exact
approved changed result-text paths. Fired values, snapshot identity, and
public state remain identical. The production loader is non-recursive and
accepts only the current live schema; historical paths are manifested but never loaded
at runtime.

R2 tests cover one- and multi-year observed spans and missing-year
non-interpolation. R3 boundaries run on value and quantity. R4-D tests cover
coverage and no-grade wording. R5 tests cover numeric and UNAVAILABLE flows.
R9-S, R10, and R11 tests prove evidence-derived predicates and the absence of
author flags. Dossier tests prove public/synthetic contradiction separation.

### Public decision generalization proof

Tests use synthetic-free PublicSnapshot 2.1 fixtures under `tests/fixtures/`;
they never add demonstration data. One fixture with resolved A/B/C
decision-critical evidence and every route/economics/policy gate passing must
reach real ADVANCE. Downgrading each critical field independently to D and E
must block ADVANCE.

The proof covers all six hard exclusions, unknown exclusion inputs, exactly
one primary gap class, MONITOR with a named trigger, screening dispositions,
evidenced REJECT conditions, route order 0–8, lower-route precedence,
maximum-ΔNV selection, lower-route tie resolution, route-8 `GRAPH_REQUIRED`
without a feed, and evaluated route-8 selection from a governed fixture feed.

The proof includes FULL-vs-degraded API coverage: a conforming fixture with
two observed trade years reaches ADVANCE with `ALL_ADVANCE_GATES_PASS`;
degrading to a single year yields INVESTIGATE with
`ADVANCE_SUPPORT_SIGNAL_DEGRADED`.

Route-determination INVESTIGATE is proven through a mocked-loader
missing-economics proof that omits downside cash flows while bypassing the
PublicSnapshot validator; the API returns HTTP 200 with
`ROUTE_DETERMINATION_UNRESOLVED` instead of the prior 422
`Admitted deep case has no legal branch`.

typed rejection narratives are proven for every producible REJECT reason code,
including `UNECONOMIC_AT_EFFICIENT_SCALE`, `FALSE_OR_MEASUREMENT_GAP`, and
`STRUCTURAL_OVERCAPACITY`.

The fired-rule confidence cap is proven: R1-D caps decision confidence at C
even when all four fields are Class B.

Exact-Arabic catalogue proofs assert the 16 new EN/AR literals, 110/110 key
parity, and Arabic public decision text rather than English source-language
islands.

An AST contract fails if gate or selector functions reference `source`,
`synthetic_flag`, producer names, opportunity IDs, or scenario IDs.

The two public goldens retain their states, routes, fired rules, and all
English compatibility narrative fields except the ten legacy missing-fact
sentences, whose substance remains five needs per golden under generic
predicate-selected wording. Both packaged simulation narratives, outcomes,
and exact numeric values remain unchanged. Public EN/AR catalogue keys and
placeholders have exact parity, and browser tests prove that Arabic public
decision narratives are Arabic text rather than English source-language
islands. Simulation narrative fields remain English source-language islands
in locale `ar` until S10.

### Public acquisition and reconstruction proof

Connector tests run only against stored raw artifacts or `tests/acquisition_doubles.py` helpers; never live network.

Reconstruction is byte-exact for every acquired snapshot under the same latest-run selection. `scripts/reconstruct_snapshot.py --all` exits 1 when no snapshots exist, exit 2 when a manifest row is missing under default checking, exit 1 on hash mismatch. Manifest checking is switchable off only via `--no-check-manifest` before manifests exist.

Truncated page sets (FakeTransport page-1-of-2 with `max_requests=1`) never become universe/tariff snapshots.

Source-partition proofs: (a) superseded run retained but not selected; (b) sibling-source isolation; (c) two source-qualified snapshot IDs; (d) BACI never spliced into universe; (e) `SELECTION_CHANGED` when latest run_id differs.

Size budget, passport completeness, no-network guard, and every configured source having a contract or attempt record are tested. The `ZERO_NORMALIZED_SNAPSHOTS` gate requires at least one analytical snapshot before reconstruction CI wiring.

Acquired snapshots receive their own source-qualified IDs and are never spliced into goldens or across sources.

S12a institutional acquisition proof uses test-only parsers and an injected kind-registry double to demonstrate openness, store-time classification, privacy refusals, and production/directory/registry build-load-reconstruction with tamper and source-isolation checks; these doubles do not establish real source availability. Stored attempts and honest UNAVAILABLE citations account for sources without analytical snapshots, while the existing partner reconstruction and frozen golden boundaries remain enforced.

S12b document acquisition proof uses fixture PDFs/HTML/plain text and FakeTransport doubles for connector, store, CLI and reconstruction tests; live T7 outcomes are cited in Known Limitations when no DocumentRecord is built. Golden cases never pull live publisher pages; document lists and reconstruction oracles enforce verbatim line retention, envelope refusal, write-once list/record rules and manifest partition under `data/documents/**` without altering frozen public snapshots.

S12c entity proof verifies every declared Arabic/English span against its exact DocumentRecord line or public-snapshot JSON value, pins deterministic IDs and ambiguity states, refuses test doubles under repository `data/entities/`, and reconstructs the mention list, rule table, every input and the write-once artifact byte-for-byte without engine consumption.

## 6. Acceptance gates by subsystem

### Gate A — Authority

- original methodology present;
- frozen core complete;
- hashes pass;
- external build machinery referenced, not copied.

### Gate B — Data

- snapshots validate;
- units and gross-flow boundary visible;
- source records and hashes present;
- synthetic scenarios reconcile to public marginals;
- raw artifacts hashed, contract-complete, coverage-recorded and reconstructible.

### Gate C — Rules

- every R-rule visible;
- thresholds loaded from config;
- taxonomy, hard exclusions, and total public-state selection are deterministic;
- steel and PP rule expectations pass.

### Gate D — Capability

- effective capacity exact;
- unknown penalty exact;
- all five profiles and complete profile gates are validated;
- public D\* gated;
- simulated D\* published only after hard gates resolve.

### Gate E — Economics

- unsupported case calculated;
- S\* minimal and reproducible;
- route hypotheses preserve order, lower-route precedence, and maximum-ΔNV selection;
- national value and competition controls visible;
- PP does not receive support merely because economics is available.

### Gate F — Evidence isolation

- zero synthetic leakage;
- dual states visible;
- all synthetic rows labeled.

### Gate G — Product

- professional responsive frontend;
- case selection and mode toggle function;
- GenUI manifest adapts panels;
- dossier opens and prints;
- public decision narratives render from the governed active-locale catalogue;
- Arabic text renders correctly.

### Gate H — Release

```bash
python3 scripts/build_manifests.py   # only after approved changes
python3 scripts/verify_integrity.py
python3 scripts/reconstruct_snapshot.py --all
pytest -q
python3 scripts/demo_smoke.py
```

All must pass.

### Gate I — Graph

- the governed projection validates and reconstructs byte-for-byte;
- the local or designated CI Neo4j mirror is loaded with all 19 uniqueness
  constraints and exact artifact counts;
- the second load creates zero nodes and zero relationships;
- provenance null counts and public/Class-D partition violations are zero;
- required Cypher view results equal deterministic artifact functions;
- the stopped service returns typed `GRAPH_UNAVAILABLE`; and
- no ordinary test or CI job can select Aura.

## 7. Definition of done for the packaged MVP

The MVP is complete when:

- it starts from a clean Python environment with documented commands;
- no external key is required;
- all tests pass;
- integrity passes;
- all seven public golden outcomes are correct, including the unchanged
  original steel and polypropylene results;
- the steel simulated transition is correct and visibly disclosed;
- the PP simulation still rejects unnecessary support;
- all five S14b scenarios pass reconciliation and Gate B with their computed
  state/route equal to ground truth while leaving `real_decision` unchanged;
- the interface is usable at desktop and tablet widths;
- the Decision Dossier is available in JSON and printable HTML;
- documentation and source are included in one zip.

### Generalized simulation proof

Golden simulated steel remains ADVANCE route 5 with exact numeric pins.
Golden simulated polypropylene remains REJECT route 0 with
`HARD_EXCLUSION_SATISFIED`. Fixture scenarios prove routes 1–4, 6, 7, MONITOR,
partial resolution, lower-route blocking, class-if-confirmed both directions,
route-8 `GRAPH_REQUIRED` refusal without a feed, and an honest two-dependent
fixture that computes ADVANCE/8 at UnlockValue 178 without synthetic leakage
into `real_decision`.

### Scenario contract migration proof

Byte-identical 1.1.0 scenarios under `data/synthetic/historical/v1_1/` remain
manifested and rejected at runtime. Live 2.0.0 scenarios preserve every 1.1.0
`synthetic_inputs` leaf and English narrative string.

## 8. Reviewer anti-gaming rule

A failing golden test is evidence of one of three things:

1. the implementation is wrong;
2. the frozen evidence/config changed;
3. the governing methodology changed.

The reviewer must identify which one. Changing the expected result without an authority change is prohibited.

## 9. Screening reconstruction gate

Acceptance requires connector count/content/coverage negatives, threshold
injection tests, five-queue/Pareto tests, unavailable-universe output,
synthetic/formal-decision leakage refusal, runtime import isolation and warm API
performance. `scripts/reconstruct_snapshot.py --all` must print
`SCREENING RECONSTRUCTION PASS` only after acquired snapshots, documents,
entities and every screening snapshot and input hash have passed. Tampered
snapshot bytes, identities, counts, queue references or inputs fail closed.

The steel public fixture remains INVESTIGATE and the polypropylene public
fixture remains REJECT for generic capacity support; screening acceptance
cannot alter either golden.

The KL-34 fixture `no-candidate-no-fired-signal.json` is accepted by the
PublicSnapshot validator and must return HTTP 200 with null formal state,
null route, `screening_disposition=NO_CANDIDATE`, reason
`NO_TRIGGER_FIRED`, bilingual catalogue narrative and a null-safe dossier.
Another unmatched residual with a fired candidate signal must still raise the
decision-integrity error.

The visual acceptance matrix contains 56 entries. The canonical update,
manifest validation, host comparison, ownership check and measured 40-entry
drift review are distinct required proofs.

## 10. S14a case-selection and derivation proof

Case-selection determinism is tested on doubles and against the frozen S13
screening/universe inputs. `S14-CS-1` groups all configured families by sector
profile, applies the ruled queue/warning tiers, excludes the two frozen
opportunities, requires positive latest-year import net weight, applies
source-restricted disclosure coverage, then orders by R2, latest imports and
HS6. OD-11 is a hashed `identity_exclusions` row for 392190 with reason
`RESIDUAL_CATCH_ALL_SUBHEADING`; it is not a flag or an edited result list.
Two executions must produce equal bytes and the ruled output is pinned:
721061/721012, 760711/760429 and 392010, with 391739 the plastics runner-up.

`CaseBrief 1.1.0` tests reject a non-verbatim span, unsupported source claim,
non-`U` capability state without a span, numeric nameplate without a span,
resolved hard gate without Class A/B/C evidence, authored outcome and synthetic
marker. Partner-detail tests enforce exact tri-state keys, equality with the
complete `UnavailableReason` vocabulary plus `NOT_ACQUIRED` and
`REVISION_MISMATCH`, resolvable contract/hash attempts, non-World observed-row
counts, and mutual refusal between UNPARSED MISSING and well-formed
`NORMALIZED_EMPTY` ZERO. PublicSnapshot 2.1.0 accepts an unreferenced typed
attempt passport; projection tests require MISSING/OBSERVED/ZERO passport
markers and retain the WITS attempt beside any substitute-source outcome.
Projection tests rederive every trade value from the universe,
preserve `LATEST_REVISION_ONLY`, exclude H5 2021, verify unit conversions and
partner-World exclusion, and require byte-identical builds. The five real
briefs are then built to a temporary directory and passed through the live
public rule/capability/decision functions. Their honest S14a result is
`INVESTIGATE`, null route and
`ROUTE_CHANGING_EVIDENCE_UNRESOLVED`; a different result triggers SC-2b and is
recorded rather than forced.

AM-3/OD-18 adds a Make/CLI argv-capture test proving
`partner_dimension_query=&includeDesc=true` survives shell parsing, remains in
the QueryContract and enters the request URL. Partner completeness additionally
tests Decimal-from-raw-text aggregate reconciliation, scale-derived tolerance,
World/reference consistency, unique descriptions and exact typed-reason
mapping. The corrected 721061 V3 unit is COMPLETE with seven named non-World
rows; its computed engine proof remains INVESTIGATE/null and fires R3 naturally.

`scripts/reconstruct_snapshot.py --all` prints
`CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)` in S14a. After S14b commits
case snapshots, the same pass rebuilds and byte-compares them. Acquired
historical snapshots reconstruct from their recorded run ids while the
existing `reconstruct()` latest-selection diagnostic continues to emit
`SELECTION_CHANGED` when called for that purpose.

Screening input checking first compares the live repository-relative path.
An approved superseded `config/` hash may resolve to exactly one immutable file
under `config/history/`; data inputs never use that path and any unknown or
ambiguous hash remains `INPUTS_CHANGED`. Tests prove live match, retained match,
unknown-hash refusal and non-config refusal.

The manifest layer enumerates `data/cases/**`, `config/history/**`, new
raw/document/entity/partner evidence and preserves every pre-existing row.
The first authorized generator run followed the base S14a governed text.
OD-12/AM-2 Case B authorized the second run after the
tri-state, W-C records and corrected Core/ADR/control text; its immediate oracle
preserved every row that existed at base `ab6211f`. OD-16/OD-18 Case C
authorizes one third-and-last run after corrected V3 evidence and governed
records, again with the base-row oracle immediately after. Both original public
goldens, their scenarios, frozen roots and the 56-entry visual manifest remain
exact.

### 10.1 S14b portfolio, route and reconstruction proof

The merged S14a builder produces five committed PublicSnapshot 2.2.0 records
from the five validated briefs; no snapshot is edited by hand.
`scripts/reconstruct_snapshot.py --all` must print
`CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)`. The two original public
snapshots, scenarios and four historical outcomes remain byte-identical.

Seven cases load through the repository, API and browser harness. Goldens C–G
compute public INVESTIGATE/null and simulated routes 3, 7, 6, 4 and 0,
respectively. `scripts/validate_scenarios.py` validates all seven scenario
contracts, reconciliation checks and Gate B comparisons. Tests also prove
that all five S14b public cases fire material R1-D, so MONITOR is not
manufactured from this evidence.

The visual proof consists of two owner-authorized canonical executions under
the same S14b change reference, a 76-entry manifest, host comparison,
recursive ownership and byte-budget checks, and measured drift tables. OD-15
corrects the computed portfolio chip and catalogue-sourced Arabic decision
subject before the second execution.

### 10.2 S15a selection, evidence and integrated engine proof

`S14-CS-1.1` is tested on doubles and on the frozen S13 screening/universe
inputs. It excludes `SERIES_GAP_YEARS` before tiering regardless of queue flags,
requires addressed WCO evidence for every `identity_exclusions` row and keeps
missing-versus-zero semantics explicit: missing years are not zero trade.
The pinned S15 output selects pharma_api 294110/294120 and fertilizers
310430/310510. Its recorded four document identities are part of the
write-once input contract.

`reconstruct-selection` resolves those recorded identities and must print
`CASE SELECTION RECONSTRUCTION PASS (2 records)` after reproducing both S14 and
S15 canonical bytes. OD-16 distinguishes that acceptance oracle from a raw
current-state selection diagnostic: after W-A15b, the additional SABIC
Agri-Nutrients record changes disclosure coverage for non-selected 310210 and
therefore changes the diagnostic digest, but not the selected four-code set.
The diagnostic output is neither written nor promoted.

The four S15 CaseBriefs build through the merged PublicSnapshot 2.2.0 carrier.
Their partner detail is OBSERVED with 10, 4, 11 and 11 non-World rows. Every
public capability dimension is `U` and every profile hard gate is
`UNAVAILABLE`: those values mean not identified within the cited stored
evidence, not absent. All four computed public decisions are INVESTIGATE with
null route and `ROUTE_CHANGING_EVIDENCE_UNRESOLVED`; each fires
R0/R1-D/R2/R3/R4-D/R10/R12. No Class-D scenario input enters this child or its
public proof.

Acceptance additionally requires scoped and unscoped partner snapshots to
reconstruct independently from disjoint recorded units, nine briefs plus the
five committed S14 snapshots to pass case reconstruction, three entity
artifacts to reconstruct, the 76-entry visual manifest and frozen outcomes to
remain unchanged, and the single S15a manifest generation to add only governed
S15 evidence rows while changing only the two approved configuration and four
Core authority hashes.

### 10.3 S15b portfolio, selection and EVSI proof

The four S15a briefs must rebuild byte-identical PublicSnapshot 2.2.0 files and
extend the configured repository to eleven cases. Their public goldens remain
INVESTIGATE/null with observed partner counts 10, 4, 11 and 11 and the exact
R0/R1-D/R2/R3/R4-D/R10/R12 fired set. Their Class-D scenarios must compute,
in order, ADVANCE/1, REJECT/0 with EX-03, ADVANCE/2, and REJECT/0 with EX-01.
All original scenario and public outcomes remain covered.

Selection acceptance requires the manifest-verified
`CASE-SELECTION-S15-b96de36ff0ce` public projection, both selected pairs, quotas,
ordered substitutes, input references and every residual-identity, viability,
series-gap and frozen-case exclusion. API and browser tests prove the surface is
mode-independent, bilingual and synthetic-free; selected S15 dossiers alone add
the version-1.3 selection reference.

EVSI acceptance distinguishes true omission from a supplied invalid block. For
each S15b scenario, a failing spy proves omission does not call
`approximate_evsi`, direct simulation and API output return null, and public
`real_decision` and `data_unlocks` remain unchanged. Supplied null, top-level
wrong types, empty/partial mappings and conversion failures remain direct
integrity errors and typed HTTP 422. The seven existing supplied mappings retain
exact helper equality, including the steel 129.3 pin; test-only zero and negative
results remain numeric mappings. GenUI renders the localized unavailable value
without an EVSI next-fact note, dossiers remain usable, and the graph wrapper
retains `numeric_evsi: NOT_CALCULABLE` without synthesizing an estimate.

## 11. S18a executive projection acceptance

Acceptance requires model tests for frozen/strict contracts, exhaustive
taxonomy tests, claim-ID/evidence-reference tests, summary and case service
tests, synthetic-isolation tests, mounted API/OpenAPI tests and an excluded
warm-up plus five measured calls below NFR-005's 250 ms median for summary and
one case.

The frozen count oracle independently pins all six current dataset kinds,
separate loaded opportunity IDs, screening counts 5,443 / 4,996 / 4,996 / 0 /
1,618 / 0 and SHA-256 over each sorted affected-HS6 list. The exact current
structured-code set has zero `UNMAPPED` values. Tests must fail if prose is used
to classify a dataset.

The EVSI oracle requires eleven scenario-qualified rows, seven available and
four unavailable. `math.fsum` totals are 371.55 M SAR overall, 374.95 positive
and -3.4 non-positive. These values remain only in the synthetic summary with
Class D, `DEMO_GENERATOR`, scenario IDs and both policy labels; no public
dataset row, public vector or real decision may carry EVSI or a synthetic label.

The integrity oracle injects public synthetic leakage, changed real decisions,
wrong source/class/flag/scenario, failed reconciliation and failed back-test.
Each mutation must fail exactly its named check with the affected opportunity
ID. The unmodified violation count is calculated as zero; a literal constant is
not an acceptable implementation.

All eleven executive cases must equal the existing public and simulated states
and routes. Steel remains public INVESTIGATE and simulated ADVANCE/5;
polypropylene remains public and simulated REJECT/0 and cannot acquire a
positive support recommendation. Unknown opportunities return typed 404 and
governed projection failures typed 422. Executive routes are mounted before the
SPA fallback and accept no mode, path or source input.

Public rule claims use the exact delivered R0–R12 identifiers and support
families; R6/R7/R8/R10 remain unresolved without exact delivered support.
Simulated decision and step claims require current-scenario Class-D
`DEMO_GENERATOR` rows, scenario identity and both policy labels. Cross-scenario
rows, malformed metadata, absent references and synthetic-to-public linkage
must fail closed.

S18a graph identity and projection bytes change only because governed Core and
engine input hashes change. Graph node/edge semantics and counts are expected
to remain 925/1,045 and must be audited after the graph is generated. Visual
manifest and provenance bytes change because `app.py` and the graph
pointer/projection are visual sources. The accepted S18a AM-3 result was that
110 of 112 WebPs remained byte-identical; the two desktop public-steel
`evidence_to_change` images changed only for the run-qualified Decision ID.
No visual path, viewport or tolerance changed. The immutable AM-3/AM-4 packets
and their approvals retain their historical wording; this corrects the live
KL-132 acceptance description rather than rewriting that history.

Pre-generation acceptance runs focused executive, isolation, reconstruction,
portfolio and golden regressions, then the complete non-live gates. Read-only
in-memory graph construction binds the candidate identity only after every
graph-hashed Core and source byte is final. Graph, manifest and canonical
visual generation remain separate owner authorizations and are not part of the
pre-generation candidate.

## 12. S18b executive surface acceptance

Acceptance requires all eleven selected cases in both locales to match the
executive API states/routes, all eight steps and four separate vectors, and all
nine route rows per available branch in engine order. Steel remains public
INVESTIGATE and simulated ADVANCE/5; polypropylene remains REJECT/0, with actual
zero support distinct from absent NPV. The four unavailable EVSI rows remain
unavailable; the frontend joins summary rows by opportunity and scenario rather
than inventing a case-schema availability field or dataset allocation.

Source drills cover metric.trade, R1-F, R4-F, R4-D and both decisions, exact
passport membership, public contradictions retained in simulated claims,
malicious text/URLs, unresolved case-wide needs, Escape and return focus.
Malformed/foreign joins fail closed. Loading, empty, not-found, request error,
locale failure, missing simulation, zero-count/UNMAPPED dataset and graph
unavailability are explicit. Delayed responses and Back/Forward must not expose
stale case, branch, locale or source content. Analyst values and prior control
order remain intact with precisely added source and executive navigation controls.

Arabic parity checks the complete executive subtree, including opened source
passports: UI-controlled labels use governed Arabic, technical claim identifiers
have a finite grammar, and verbatim English source spans carry explicit language
and the existing source caption. Ordinary English prose and company names cannot
pass as technical IDs. Keyboard/focus, reduced-motion, axe at1440/1024 and
responsive390/1920/2560 checks accompany actual rendered-screen inspection.

Before canonical generation run the complete functional browser gate and inspect
all eight steps EN/AR at1440, route/unlocks/conditions at1024/390 and four failure
states in both locales. Retain actual screenshots, URLs and observations.
The visual matrix preserves all112 existing paths and adds exactly16 executive
images (four scenes × two locales × two viewports), for128 total. Existing
producer, comparison tolerances, budgets and untouched graph geometry remain
required. Reviewed changes are limited to declared UI additions, authority labels
and run-qualified identities; no automatic acceptance of unrelated image drift.

Core02/03/09 and catalogue changes require a separately reviewed, bound graph
build, then manifests, then canonical visual allocation after source pause.
Expected graph semantics/counts stay925/1045; unexpected changes stop the
operation. Snapshot726 and authority20 are observed output obligations, not
values to force. Every hashed source/capture helper is bound before generation.
Two clean-root exact-candidate gates, independent implementation review, exact
PR-head checks/review and delegated acceptance precede delivery. These are
acceptance requirements, not a claim that pending gates already passed.


### S18b AM4 quality and pre-generation acceptance

Extend source tests across all four graph views, both modes/locales and390/1024/1440 after actual stored-evidence selection; genuinely empty views retain no invented nodes. Whole-graph Arabic parity uses independently enumerated literal source-count fixtures, and full-page axe/keyboard/containment applies. Source/caption removal, raw English status, company-as-code, composite-ID wrong direction, unsafe URL and missing warning mutations must fail, retaining the five AM2 controls. Exact source text/URL/ID ordering, genuine Arabic/mixed/hostile strings, typed absence, unresolved valid-looking IDs and zero document indexes remain tested. Both callers preserve anchor/close/Escape/return focus. All eight executive steps are inspected EN/AR390/1024/1440, with expanded capability meanings, original API equality and unknown/warning negative controls. Table Tab order gains exactly two named stops; native Arrow scrolling covers both actual endpoints without relying on an assumed RTL zero origin.

WebP remains opaque lossless RGB, method6/exactTrue with compression effort100, fixed dimensions/fonts/producer/tolerances and600KiB per image/16MiB aggregate. Same-input80/100 decoded equality, repeat100 identity and preserved112 old bytes precede final128 review. The actual capture-source closure includes shared passports, executive evidence/simulation, graph CSS, UI, encoder and transitive browser helpers; no Pillow default-dev dependency is added.

Before generation the full unmodified functional command remains mandatory. Its sole admitted pending-output failure is graph preflight retained112 observing96 inherited nongraph images; it is reported nonzero, never GREEN. Verify the fresh16 graph capture matrix/resources separately, then the disjoint immutable96 plus fresh16 provisional112 budget. Final16 executive captures remain ungenerated/unverified until Task6. Only the ten explicitly mapped stale-output default-pytest cases may remain separately pending. After accepted generation, full functional exit0 with actual128/112 and every unchanged parent128visual/strictR1/two-rootCI/exact-review gate is required. This paragraph changes sequence honesty, not acceptance strength.

### S18b AM5 and parent-scope review regression proof

Computed executive integrity requires EN/AR PASS0, valid FAIL27 with all four ordered checks and affected IDs, unavailable transport/retry without stale PASS, and usable eight-step/source/keyboard journeys at390/1024/1440. Analyst identity tests cover all11 public and simulated contexts plus independent state/route/scenario conflicts, explicitly null versus route0. Screening's eight real reviewer statuses retain exact raw identity and faithful localized copy; the unchanged full Arabic scanner and all hostile injection controls remain mandatory.

Every returned vector claim must be reachable with its actual status and stored passport; contradictions cannot disappear behind a metric value. Genuine missing-scenario coverage must use the real builder and validate its DTOs, with eleven public cases and no invented EVSI row for the unavailable case. All eight steps in both locales preserve the public conclusion without synthetic fetch, metadata, policy-label or EVSI-value invention. Available-branch missing/mismatched EVSI and forged unavailable metadata still reject. Only the two exact legitimate unavailable-step claim IDs extend the narrow grammar; ordinary prose and malformed suffixes still fail.

The16 executive visual scenes must prove exact context and complete substantive content in the viewport before capture: public trade content; simulated route heading/both warnings/first two complete row headers; dataset explanation and complete named count cards; and polypropylene's public rejection/rationale/boundary/route. Entire required boxes, stable pre/post capture geometry and original-preparation RED evidence are required. All112 prior capture preparations, fixed dimensions, pinned producer, fonts, tolerances and600KiB/16MiB final128 budget remain unchanged. Local diagnostic screenshots/resource estimates do not certify canonical output. Independent source/UI review precedes the separately reviewed graph→manifest→visual operation and all exact-candidate gates.

## 13. S19 bilingual dossier and shared trade interpretation acceptance

DecisionDossier2.0.0 must pass all11 cases × public/simulated JSON combinations and both HTML locales:22 JSON and44 HTML/PDF outputs. Independently enumerated source-path assertions must verify complete public/active decisions, all nine routes in engine order, original passports, whitelist values and unchanged S15 selection membership. Fingerprint inputs before and after projection/rendering. Public exports must never call the scenario loader or contain scenario input paths, synthetic passports/labels or EVSI values. Simulated `public_decision` must equal the complete `real_decision`, not only state/route. Every conflicting scenario identity/version/source/Class-D/flag/disclosure mutation must fail as HTTP422 `DOSSIER_INTEGRITY_ERROR`; malformed required structures cannot become blank successful reports.

Availability tests distinguish genuine0 and boolean fields from absent/null/NOT_CALCULABLE; numeric booleans, strings and nonfinite values reject. Missing fields carry null source paths; existing null fields retain real paths. Cover empty producers/passports/conditions, optional absent EVSI, public steel contradictions, polypropylene's zero support and missing unsupported NPV, malicious HTML/URL values and local versus external route-8 IDs. Original-defect RED must precede corrected GREEN for raw supply JSON, English rule prose in Arabic, omitted sections and hidden public conclusions. Already-passing invariants remain preservation evidence, never invented RED.

Rendered acceptance includes the original Analyst→Dossier path and all44 Executive→existing Analyst link→explicit evidence-mode selection→Dossier→return journeys. Assert case/mode/locale preservation, full identity, named supply and every section, actual Arabic ledger name/result/effect, complete technical identifiers, keyboard toolbar/JSON/return focus, no console/network errors and no serious/critical axe failures. At390/1024/1440, test both locales/modes without horizontal body overflow, clipping, hidden content or truncation. AR-V01 specifically requires both actual Arabic1024 simulated steel and polypropylene original-defect RED and corrected GREEN, including both exact policy warnings and identity text at initial and legally reachable scroll positions.

### 13.1 Native Chromium PDF proof

Wait for local fonts, then emit all44 A4 PDFs with pinned Chromium and print backgrounds. Require valid structure, embedded fonts, nonempty selectable text on every page, all appendix headings and full expected technical IDs, canonical numbers/units, complete public conclusion and no public synthetic disclosure. Summary occupies page1; appendix begins page2. Both policy labels appear on every simulated page in a reserved region without content overlap. Minimum body sizes remain10.5pt EN/11.5pt AR. No content omission, small-font workaround, empty/orphan-only page or arbitrary page-count waiver.

Reuse the reviewed proof-only pypdfium2/PDFium overlay and immutable image; it is not a product dependency. Rasterize every page of every PDF at144dpi without cropping. The acceptance wrapper fails for missing documents/pages or tight glyph boxes beyond physical/content/footer bounds; preserve deliberately off-page and actual old-print negative controls. A renderer's diagnostic exit0 is not acceptance. Text extraction, including Arabic token checks, complements actual rendered inspection rather than replacing it. Inspect all44 first pages and every page of the longest EN/AR reports, steel contradiction, polypropylene zero-support and route-8 aluminium cases; inspect remaining contact sheets and expand anomalies at full resolution. Retain exact PDF/text/metadata/checksums and a reviewed bounded raster subset. This is not PDF-UA certification or human domain sign-off.

### 13.2 Shared chart disclosure and native observed-data access

TRADE-SCALE-01 requires original absent-note/control RED and corrected GREEN in Analyst and Executive Signal, both locales. Keep all existing curve paths/math and public values unchanged. Verify all observed year/value/quantity cells against actual public analysis across all11 cases, both Analyst modes and Executive Signal; retain complete `real_decision` equality. Test unsorted input without mutation, true0, null/missing/string/bool/nonfinite cells and empty rows. The visible note explains independent scales: steel2024's236.9 USD million and287.9kt are different units, not comparable curve heights. Native details must open/close with Enter/Space, remain reachable by Tab with visible focus, and retain readable full data at390/1024/1440. Preserve every inherited keyboard stop/order; the separately approved single `trade-data-summary` stop is an addition, not a weakened order check.

### 13.3 Source closure, generation and exact delivery

Finish source, catalogue1.7.0 (effective2026-09-24), Core contracts, source/UI review and real browser test-name admission before generation. Keep literal inventories and every inherited assertion; reject removed old or unapproved new members. Renderer mappings must have real consumers; unchanged stock usage/copy checks and unknown/unused/copy negative controls remain mandatory.

Run the reviewed read-only double graph build and full normalized semantic comparison, preserving edge multiplicity, with all11 complete real decisions unchanged. Only separately bounded authority/catalogue metadata and own derived IDs may differ; real-decision differences are never normalized. Bind one new graph write and one manifest build, preserve historical roots and verify actual membership/counts. Predecessor snapshot726 implies728 only after exactly two new graph paths and every old member are verified; authority membership stays20 and graph topology925/1045. These are required checks, not reports of completed S19 generation.

Canonical capture retains all128 paths, dimensions, producer/fonts, tolerances and600KiB per-image/16MiB total. Sixteen dossier images may redesign. The trade amendment additionally permits actual chart-local/necessary downstream-flow changes only within the56 eligible current chart-consumer paths; eligibility does not imply all change. In Executive Signal the closed summary/note and every old required box must fit without scrolling, resizing or hiding content. Review all actual changed pairs. Preserve exact graph token regression sensitivity, the strict R1 identifier-only geometry probe, mechanical current subtree pin and all frozen data/golden pins.

Final acceptance requires full focused/default tests, every stock integrity/reconstruction/scenario/smoke/static/package gate, compare-only `make e2e`, and two complete `make ci` runs in separate clean roots with independently reviewed resource isolation preventing retained-service interference. Each result must bind the exact candidate; prior S18b passes do not substitute. Independent exact-tree review and delegated acceptance precede exact staged/committed identity, hosted checks, independent exact-head approval, merge and required main checks. Preserve failures and attribution. Final S21 accepted-projection live Aura/bilingual application verification and S22 cross-model release certification remain separate requirements.
