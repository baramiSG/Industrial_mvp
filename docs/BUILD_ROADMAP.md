# Build Roadmap — Completion of the IOR MVP

## Purpose

This roadmap converts the governing specification (methodology DOCX → `docs/core/01–09` → `config/*.v1.yaml` → hashed data) into bounded, independently reviewable slices that close every conformance gap found in the v0.1.0 package and bring the repository under CI, PR and traceability control.

The baseline package (`CHANGELOG.md` 0.1.0) already implements `BUILD_OVERLAY.md` slices S01–S12. The slices below are **conformance and completion** slices; they do not add backlog features (`MVP_BACKLOG.md` P1–P6 remain post-acceptance work per `BUILD_OVERLAY.md` §7 and `AGENTS.md` scope control).

## Governing hierarchy used

1. Owner instructions (autonomous Supervisor/Flight Control mandate, 2026-09-02).
2. `docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx`.
3. `AGENTS.md`, `.cursor/rules/*.mdc`.
4. `docs/authority/00_AUTHORITY_MANIFEST.md`, `docs/core/01–09`.
5. `config/thresholds.v1.yaml`, `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml`.
6. Hashed snapshots and golden tests.
7. Existing implementation (evidence, not requirement).

## Slices

| ID | Slice | Objective | Governing requirements | Merge gate |
|---|---|---|---|---|
| S00 | Baseline import (Supervisor bootstrap) | Initialise git, remove Windows `Zone.Identifier` artifacts, commit v0.1.0 package plus build-control documents to `main`, push to `baramiSG/Industrial_mvp`. | BC-01, BC-02, BC-03 | Supervisor (ADR-001 exception) |
| S01 | CI pipeline, local gates and toolchain | GitHub Actions running integrity, pytest, smoke, compile, prohibited-file and secret scans on PR/push; `make ci` local equivalent; `uv` developer path with lockfile while preserving documented pip path. | Core 09 §2.1, §6 Gate H; AGENTS.md proof rule; BC-04, BC-05; SG-TR-007 | PR + CI green + zero findings |
| S02 | Threshold governance | Remove every embedded threshold literal from engine code (`0.40`, `1.25`, `50`), fix R3 largest-supplier semantics, add `R11` export/import ratio key through the §7.3 change gate (`thresholds` 1.0.0 → 1.1.0), add AST validator that fails on embedded threshold literals, add Core 09 §3 boundary tests. | AGENTS.md #7; Manifest §6.7, §7.3; Core 07 §9; Core 09 §3; FR-002 | PR + CI green + zero findings |
| S03 | Evidence-isolation and scenario-validation hardening | `display_label` mandatory in evidence policy (1.0.0 → 1.1.0) with typed fail-closed errors; real dossier carries no synthetic disclosure (Core 09 §4.6 test); scenario-to-public-marginal reconciliation validator (Core 06 §5.1, §10.2; Gate B); methodology/config versions in every case response, banner and dossier (FR-001); R5 explicit NOT_CALCULABLE transparency. | Core 06 §4, §5.1, §10; Core 09 §4, Gate B; FR-001; INV-03, INV-04 | PR + CI green + zero findings |
| S04 | Simulation-branch fidelity | Scenario `scenario_version`, `ground_truth`, and `decision_narrative` blocks; simulated-state selection driven by Core 07 §7.3/§7.4 from scenario content (no opportunity-ID dispatch); conditions/kill conditions sourced from scenario; back-test assertion engine == ground truth (Core 06 §10.5); R6/R7/R8 re-evaluated in the simulated ledger as labelled synthetic rows with NOT_CALCULABLE where inputs are absent (Core 02 §3); UI and dossier disclose synthetic rule rows. | Core 02 §3; Core 06 §5.3, §10; Core 07 §7.2–7.4, §8; FR-020, FR-021, FR-052; INV-02 | PR + CI green + zero findings |
| S05 | Final acceptance | Full specification re-read and audit; complete traceability audit; clean install, startup, journeys, failure paths; repository scan for placeholders; different-model final reviewer; final documents; tag. | Owner mandate §27–28; Core 09 §7 | Supervisor after zero findings |

Slices may be split before implementation if the Planner shows a slice is too large for one reviewable PR. Splits are recorded here and in `.workflow/state.json`.

## Explicit non-goals for this build

- No live connectors, public-universe expansion, Etimad corpus, capability graph, Ministry pilot or calibration (`MVP_BACKLOG.md` P1–P6).
- No change to the two public golden outcomes or to any frozen public snapshot.
- No generic AI chat, CRM, document management or extra dashboards.
- No production authentication or authorization workflow.

## Slice record location

Each slice keeps its persona, context, plan, plan review, implementation log, implementation review, reviewer findings, test evidence, PR record and completion record in `.workflow/slices/SXX-<slug>/`.

---

# Milestone v0.3.0 — Ministerial Demonstration Readiness

Opened by the owner on 2026-09-02 after acceptance of v0.2.0 (`ce5786b`, tag `v0.2.0`) as the frozen two-case technical demonstration baseline. Governing planning documents, approved with amendments under ADR-010:

- `docs/milestones/v0.3.0/GAP_ANALYSIS.md` — owner objective vs v0.2.0, gap register A–G, uncovered normative statements, authority-change inventory, interpretations I1–I8 and owner rulings R-1..R-6.
- `docs/milestones/v0.3.0/SLICE_GRAPH.md` — slices S06–S22, dependencies, execution order, release-acceptance mapping, known-limitation disposition and the routes 0–8 coverage matrix.

## Approved execution order

```text
M3-P0 → S06 → S07 → S08 → S09 → S10 → S11 → S12 → S13 → S14 → S15 → S16 → S17 → S18 → S19 → S20 → S21 → S22
```

| ID | Slice | Objective (one line) | Merge gate |
|---|---|---|---|
| M3-P0 | Planning baseline (docs only) | Gap analysis, slice graph, ADR-010, roadmap/progress/state updates on `main` before S06. | PR + CI green; Supervisor merge |
| S06 | Real-browser acceptance harness | Chromium/Playwright gates for console, network, accessibility, keyboard, widths, print/PDF; reference screenshots of v0.2.0. | PR + CI green + zero findings |
| S07 | Bilingual interface foundation | AR/EN switch, RTL, design tokens, module decomposition, governed visual-regression baselines. | PR + CI green + zero findings |
| S08 | Snapshot schema v2 and computed rule ledger | Rules computed from evidence; goldens re-expressed with identical outcomes; contradictions in dossier. | PR + CI green + zero findings |
| S09 | Generalized public decision and five profiles | Evidence-gated ADVANCE, MONITOR, hard exclusions, gap taxonomy, route hypotheses, five sector profiles. | PR + CI green + zero findings |
| S10 | Generalized simulation branch | Routes 0–7, route-8 contract (`GRAPH_REQUIRED`), R8, allocation/expansion schemas, amended I5 selection. | PR + CI green + zero findings |
| S11 | Acquisition I | Connector framework, raw store, trade sources, tariff hierarchy, reconstruction proof. | PR + CI green + zero findings |
| S12 | Acquisition II | Institutional and document sources with passports; `UNAVAILABLE` recorded, never fabricated. | PR + CI green + zero findings |
| S13 | Universe screening and queues | Cheap rules across the Saudi HS6 universe; five queues; screening dispositions. | PR + CI green + zero findings |
| S14 | Deep cases A | ≥5 cases: coated steel, fabricated aluminium, technical plastics; route matrix rows. | PR + CI green + zero findings |
| S15 | Deep cases B | Remaining cases to ≥10 across five profiles: pharma/API, fertilizers; route matrix rows. | PR + CI green + zero findings |
| S16 | Neo4j graph backend | Project-owned provisioned graph as governed projection; graph-fed results; route 8 activated. | PR + CI green + zero findings |
| S17 | Interactive graph view | Four governed graph views, bilingual, keyboard-operable. | PR + CI green + zero findings |
| S18 | Executive Mode | Eight-step narrative, side-by-side states, "What Ministry data unlocks", claim drill-down. | PR + CI green + zero findings |
| S19 | Bilingual dossier and PDF | All §15 blocks, AR/EN, print and Chromium PDF. | PR + CI green + zero findings |
| S20 | Extraction corpus and adapter | Real labelled AR/EN corpus, metrics, adapter contract, optional LM Studio adapter. | PR + CI green + zero findings |
| S21 | Demonstration experience | `make demo-up` / `make demo-reset`, bilingual 5- and 15-minute journeys. | PR + CI green + zero findings |
| S22 | Final acceptance and release | Full re-read, traceability and route-matrix audit, holistic review, tag `v0.3.0`. | Supervisor after zero findings and green default-branch CI |


## S12 split (SLICE_GRAPH §5)

S12 is partitioned by contract/modality into the following approved children; the historical parent execution order above remains the original milestone record. Effective sequence: S11 → s12a → s12b → s12c → S13; the parent is not complete until every child is delivered. S12a is a leaf, not further decomposed. Child dependencies below are relative to the parent; S11 is the inherited parent prerequisite.

### s12a-acquisition-framework-institutional-sources

S12a: Generalize the S11 acquisition framework from trade/tariff units to institutional acquisition units and snapshot kinds without changing any S11 raw artifact, snapshot, passport or reconstruction result, and acquire GASTAT public aggregates (official production/industrial statistics that supply R5 production and retained-flow inputs where the source publishes them), Ministry of Industry open data and MODON public directories, and SASO catalogue / SABER registry public metadata into passported, hashed, reconstructible snapshots — recording every unobtainable source as UNAVAILABLE with the observed response and recording the S12 split in docs/BUILD_ROADMAP.md and .workflow/state.json.

Depends on: none within S12 (inherits S11).

### s12b-document-store-disclosures-tenders

S12b: Establish the governed span-addressable public document store on the generalized pipeline — persistent document ID, page and line addressing, original Arabic/English text preserved, raw document and derived text hashed and reconstructible under data/documents/** with manifest coverage — and acquire Tadawul issuer disclosures, Saudi producer disclosures (annual reports, environmental product declarations, product sheets and catalogue pages), Etimad public tender/specification documents and SASO public documents into it with §11-complete passports, typing producer nameplate/expansion evidence as Class C, and recording blocked or unreachable sources as UNAVAILABLE with the observed response.

Depends on: `s12a-acquisition-framework-institutional-sources`.

### s12c-entity-resolution-bilingual-ids

S12c: Resolve the companies, plants, production lines and licence holders named across the acquired institutional directories, registries, disclosures and documents into persistent bilingual entity IDs per Core 05 §6.5 and Core 08 §10 — Arabic/English name normalisation, deterministic linking rules with explicit precedence, time-versioned ownership and name changes, and the licence-holder / company / plant / line distinction — producing a governed, hashed, reconstructible entity-resolution artifact that links acquired passports and observations to persistent IDs, holding ambiguous links at a reviewer-pending status and never fabricating a match.

Depends on: `s12a-acquisition-framework-institutional-sources`, `s12b-document-store-disclosures-tenders`.

Approved assessment identities (local recovery records, never source evidence): parent `.autonomous-workflow/plans/s12-acquisition-institutional-documents/cycle-1/decomposition-1.json`, SHA-256 `ad234d819270e40b63ef2e12fff435379e9e412630feda3e0c5629dcd887dbd7` (required=true, three children); child `.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/decomposition-1.json`, SHA-256 `158590b4e07f5f8d548adb0675e3a43d7172227a2962a8a73f21287026f722b8` (required=false, no children). S12a's owner-approved plan is `.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json`, SHA-256 `b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64`.

S12a is MERGED (PR #15, `cc85cbc`) with five honest unavailable-source attempts. S12b is MERGED (PR #17, `9a9d5c7`) with twelve COMPLETE DocumentRecords and five honest unavailable sources. S12c is MERGED (PR #19, `78c002f`): deterministic bilingual entity resolution with a governed, hashed, reconstructible artifact — 5 COMPANY and 2 PLANT entities from verbatim spans and frozen-snapshot labels, 0 LINE, 0 LICENCE_HOLDER, 0 deterministic identifiers, three mentions pending review, six SASO passports out of scope (KL-67–73). The parent S12 is complete. Downstream screening/engine consumption, extraction metrics and graph work remain in their later slices. No parent obligation is closed by test-double rows alone.

## S13 split (SLICE_GRAPH §5)

The approved decomposition
`.autonomous-workflow/plans/s13-public-universe-screening/cycle-1/decomposition-1.json`
(SHA-256 `93ba2443455aa368ed83814f49795a0a04f59a66d3c5d7006125afe5b27793a8`)
partitions S13 into:

1. `s13a-universe-acquisition-and-screening-engine` — official-source
   acquisition contract, fail-closed universe, screening engine, five queues,
   hashed snapshot and mounted-ready runtime API; depends on completed S12.
2. `s13b-bilingual-screening-surface` — application mount, bilingual analyst
   surface, KL-34/UX-01 and browser/visual acceptance; depends on s13a.

The parent completes only after both children merge. S13a does not edit
`app.py`, browser tests, visual-pinned config or baselines. Its approved plan is
`plan-1-s13a.json` (`9d1f8134…`) plus AM-1 (`d562ddca…`) and
AM-2 (`88abbab2…`).

S13a is MERGED (PR #21, squash `834ba60`, 2026-09-12). OD-11/W1-ter proved all
eight universe units and built the 5,443-HS6 universe. AM-2 stores the
4,996-candidate screening output as a validated write-once directory
(`SCREENING-SAU-2026-09-12-9b6b22032fd8`, rebuilt under OD-15 with
repository-relative input paths after hosted CI-F-01; 96/96 shards identical
to the superseded `311f105c4ccf`). W0-ter observed no all-partners token, so
partner coverage remains 0/1,471 and W2 was not repeated.

Child s13b is MERGED (PR #23, squash `cdf6ab0`, 2026-09-13) under plan
`plan-1-s13b.json` (`560695023c…`), AM-1 (`341d813f…`) and AM-2
(`fae4ec02…`, precedence AM-2 > AM-1 > base). It mounts the public screening
router and the additive evidence route (OD-12), supplies bilingual
summary/queue/record views with explicit states, closes KL-34, satisfies UX-01
on the workspace/methodology/screening ledgers and extends the canonical visual
matrix to 56 entries (owner-lead WIP commits `d1d1462` and `f9fec2d`; SC-5
capture-stability correction recorded in ADR-020). Parent **S13 is COMPLETE**
(s13a #21 `834ba60`, s13b #23 `cdf6ab0`). The routed multi-surface shell
(UX-02, KL-85) is carried to a later frontend slice.

## S14 split (SLICE_GRAPH §5)

The approved decomposition
`.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/decomposition-1.json`
(`48741467…`) partitions S14 into:

1. `s14a-case-selection-evidence-and-families` — deterministic selection from
   the frozen S13 snapshot; product-family authority; bounded WCO/producer/WITS
   acquisition; entity mentions v2; `CaseBrief 1.1.0`; temporary PublicSnapshot
   builds and honest public-engine proof. It changes no portfolio, scenario,
   golden or browser root.
2. `s14b-deep-case-portfolio-scenarios-and-goldens` — consumes the pinned S14a
   list and builder, adds five public snapshots with five Class-D scenarios,
   golden/project lists, route-coverage rows and Playwright/visual oracles under
   the owner-lead frozen-pin protocol. In the same single visual regeneration,
   it upgrades new snapshots to PublicSnapshot 2.2.0 with a version-gated
   `partner_detail` block, requires rows iff OBSERVED and UNAVAILABLE iff
   MISSING/ZERO, adds MISSING/ZERO concentration and R3/R4-D result codes,
   renders the state in ledger/dossier views, and proves the frozen
   721049/390210 snapshots and goldens byte-identical.

The parent completes only after both children merge. S14a is MERGED (PR #25,
squash `ec859f7`, 2026-09-13) under `plan-1-s14a.json` (`8fbfa4e6…`), AM-1
(`8c61a0a2…`), AM-2 (`5bccc8a5…`), AM-3 (`6e596932…`) and OD-1…OD-23. The ruled
selected set is 721061, 721012, 760711, 760429 and 392010 (392190 excluded as a
residual catch-all with verbatim WCO basis). It delivered eight COMPLETE
DocumentRecords, a WITS partner snapshot (721061 `FORMAT_NOT_PARSEABLE`), a
Comtrade partner snapshot for 721061 (seven observed partners, exact
reconciliation), a second entity artifact, five validated CaseBrief 1.1.0
records with tri-state partner coverage and five public INVESTIGATE/null-route
engine proofs.

S14b is MERGED ([PR #27](https://github.com/baramiSG/Industrial_mvp/pull/27),
squash `a8c4763`, 2026-09-13) under plan `af5ae5d8…`, AM-1 `8dc1b75d…` and
OD-1…OD-20. Owner WIP commits were W1' `4068a80` (preparation rebased onto
S14a records), W2 `ec2eae1` (five builder-derived snapshots, five Class-D
scenarios and the first 76-entry visual set) and W2' `5354a6f` (truth/parity
corrections and the second canonical visual set). Computed simulations
demonstrate routes 3, 7, 6, 4 and a second route-0 rejection; all five public
cases remain INVESTIGATE/null and synthetic evidence leaves `real_decision`
unchanged. MONITOR is not manufactured because every case fires material R1-D.
The reviewer found and the owner corrected Core 04's 2.2.0 exact-key names
before a second/final S14b manifest generation. PR CI and merged-main CI both
passed 5/5. Parent **S14 is COMPLETE**; S15 is next.

## S15 split (SLICE_GRAPH §5)

The approved decomposition
`.autonomous-workflow/plans/s15-deep-cases-b/cycle-1/decomposition-1.json`
(`ea01de65…`) partitions S15 into:

1. `s15a-case-selection-evidence-pharma-fertilizers` — `S14-CS-1.1`,
   product-family/source versioning, bounded WCO/producer/SFDA/Comtrade
   evidence, mentions-v3, four CaseBriefs and PublicSnapshot 2.2.0 engine
   proofs. It changes no portfolio, scenario, golden or browser root.
2. `s15b-deep-case-portfolio-scenarios-and-goldens` — consumes the reviewed
   S15a records, adds portfolio/scenario/golden/browser coverage and computes
   the owner-approved route demonstrations without changing real decisions.

The parent completes only after both children merge. S15a preparation W1
`697322e` was rebased onto M15
`6dc966a9f210b47a94b96aaeffadcbcc6642415f` as W1'
`7d4853e8d979d86a5fa932fbd4468bceacfb63b4`. The owner resolved the sole
integration conflict to `CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)`.
OD-16 retains recorded selection `CASE-SELECTION-S15-b96de36ff0ce`; its
recorded-input reconstruction passes after W-A15b even though a current-state
diagnostic sees the later SABIC document and changes its digest without
changing the selected set. S15a remains an unapproved local implementation
candidate until independent review.

## Explicit non-goals for v0.3.0

Authentication, role-based approval, official override workflow, confidential Ministry connectors, live customs transactions, paid-data acquisition, model training on Ministry applications, causal incentive-effect claims, generic AI chat, CRM, document management, any change to the methodology DOCX, and any alteration of the v0.2.0 tag, release records or frozen v1 golden snapshot files.
