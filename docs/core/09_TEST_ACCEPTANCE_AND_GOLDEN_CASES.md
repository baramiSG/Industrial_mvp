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
The S14b matrix has 76 entries. Five public-workspace screens extend the
S13b fourteen-screen matrix to nineteen screens in two locales and two
viewports. Canonical regeneration round one records the 56-entry comparison
against the S14a merge. OD-15 then corrects the portfolio count/rule chip and
Arabic decision-subject label; OD-16 authorizes canonical regeneration round
two. Its eight portfolio changes are confined to the chip bounding boxes and
its seven Arabic desktop public-workspace changes are confined to the
decision-subject card. All other baseline images remain byte-identical,
ownership and budget gates pass, and CI only compares.

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
maximum-ΔNV selection, lower-route tie resolution, and route 8
GRAPH_REQUIRED.

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
and route-8 `GRAPH_REQUIRED` refusal without synthetic leakage into
`real_decision`.

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
