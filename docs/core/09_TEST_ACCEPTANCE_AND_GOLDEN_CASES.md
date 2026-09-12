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
7. a malformed synthetic scenario fails closed.

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
- the two public golden outcomes are correct;
- the steel simulated transition is correct and visibly disclosed;
- the PP simulation still rejects unnecessary support;
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
