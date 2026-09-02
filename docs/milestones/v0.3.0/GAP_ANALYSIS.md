# v0.3.0 — Ministerial Demonstration Readiness: Gap Analysis

**Status:** APPROVED WITH AMENDMENTS by the owner on 2026-09-02 (OD-1 and OD-2, see §10 and §7A). The owner's amendments to I1 and I5 and five additional binding rulings are incorporated below and are governing text for the Core v2 revision. No product code, configuration, data, core document or v0.2.0 release record has been changed by this planning baseline; it is delivered through the docs-only M3-P0 PR.
**Prepared by:** Supervisor / Flight Control seat (Claude, `claude-fable-5-1-thinking-max`), continuing the ADR-002 seat assignment.
**Date:** 2026-09-02.
**Data classification:** `confidential_demo` — frozen public evidence and Class-D synthetic scenarios only. No Ministry data. No credential values were read (only the presence of variable names in the git-ignored `.env` was confirmed).

Every consequential statement below carries a Sanad tag: **VERIFIED** (observed in files or command output this session, with location), **SPECIFIED** (stated in the methodology, Core 01–09, configuration or the owner's instruction), **DERIVED** (follows from specified material by stated reasoning), **PROPOSED** (a design choice for approval), **OPEN** (a decision the owner must make).

---

## 0. Baseline facts

| Fact | Evidence | Tag |
|---|---|---|
| `main` HEAD is `ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6` and carries annotated tag `v0.2.0`. | `git rev-parse HEAD`; `git describe --tags --exact-match HEAD` | VERIFIED |
| `verify_integrity.py` → `INTEGRITY PASS`; `validate_scenarios.py` (Gate B) → PASS, 2 scenarios, ground-truth back-test PASS; `pytest -q` → `280 passed`; `demo_smoke.py` → `SMOKE PASS` (steel public INVESTIGATE; steel simulated ADVANCE with real unchanged; PP public REJECT; extraction 100%). | Shell run on `main` at `ce5786b`, 2026-09-02 | VERIFIED |
| v0.2.0 is the frozen two-case technical demonstration baseline. It is not altered, moved, retagged or re-recorded by this milestone. `.workflow/state.json` `COMPLETE` refers to the v0.2.0 release contract only. | Owner instruction 2026-09-02 | SPECIFIED |
| Toolchain present: node 22.22.3, npm 10.9.8, Docker 29.7.2 (daemon up), uv 0.11.31, `gh` 2.93.0 authenticated as `baramiSG` (scopes `repo`, `workflow`), Python 3.14.4 in `.venv`. Playwright Chromium binaries are cached under `~/.cache/ms-playwright` (`chromium-1234`) but no Python Playwright package is installed. A `neo4j:5.26.30` image exists locally. Host ports 7474/7687 are occupied by a container belonging to a different project; it was not inspected and must not be reused (SG-TR-002). | `command -v`, `docker images`, `docker ps`, `gh auth status` | VERIFIED |
| Public-source reachability probe (HTTP HEAD only, no data pulled): WITS 200; Etimad 200; CEPII/BACI 200; ZATCA 302; UN Comtrade API host reachable (root returns 404, normal for an API root); SABER root 404 (host reachable); Tadawul 403 (bot protection); GASTAT timed out; MODON TLS chain verification failed. These are single-session observations, not source-status facts. | `curl -I` run 2026-09-02 | VERIFIED |
| Two untracked helper scripts from the v0.2.0 session remain in `.workflow/runs/` (`demo_start.sh`, `s05_release_merge_tag.sh`). They are not part of any release and were left untouched. | `git status --short` | VERIFIED |

## 1. Reading record (Sanad)

Read in full with the Read tool this session, in the authority order required by `AGENTS.md`:

1. `AGENTS.md`; `.cursor/rules/00-authority.mdc`, `10-domain-guardrails.mdc`, `20-proof.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md`.
2. `docs/authority/methodology_extracted.md`, lines 1–1889 (the searchable mirror of the governing DOCX; the DOCX hash identity is taken from `authority_hashes.json`, as the S05 final reviewer also did).
3. `docs/core/01` … `09`, all nine, in full.
4. `docs/FINAL_BUILD_REPORT.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/REQUIREMENTS_TRACEABILITY.md` (every row), `docs/BUILD_ROADMAP.md`, `docs/BUILD_PROGRESS.md`, `docs/ARCHITECTURE_DECISIONS.md` (ADR-001..009).
5. `.workflow/slices/S05-final-acceptance/reviewer_findings.md` — the complete final holistic review including the "Normative statements with no implementation, no test, and no recorded limitation" table, RV-01..05, residual observations 1–14 and the re-review round.
6. `docs/implementation/BUILD_OVERLAY.md`, `MVP_BACKLOG.md`, `UX_GENUI_DEMO_SPEC.md`, `MINISTRY_DEMO_SCRIPT.md`.
7. `config/thresholds.v1.yaml` (1.1.0), `sector_profiles.v1.yaml` (1.0.0), `evidence_policy.v1.yaml` (1.1.0), `project.yaml` (0.2.0); `data/manifests/snapshot_manifest.json`; `data/snapshots/public/SAU-H0-721049.json`; `data/synthetic/SYN-MINISTRY-STEEL-001.json`; the PP snapshot's `rule_context`, `public_decision_contract`, trade keys and capability keys.
8. All engine modules: `decision_engine.py`, `rules.py`, `capability.py`, `economics.py`, `evidence.py`, `genui.py`, `dossier.py`, `data_repository.py`, `config.py`, `app.py`, `ai_extraction.py`; `static/index.html`; the function map and lines 60–82 of `static/app.js`; `styles.css` media rules and hex-literal count.
9. `.github/workflows/ci.yml`, `Makefile`, `pyproject.toml`, `.gitignore`, `.env.example`, `.workflow/state.json`.
10. Skills opened: `autonomous-delivery`, `project-orientation`, `sanad`, `muhasib`, `task-standards`.

## 2. The owner objective (SPECIFIED)

The original objective, as fixed in the frozen core and restated by the owner on 2026-09-02:

- Core 01 §1: the MVP "must prove two propositions simultaneously: (1) public data is sufficient to identify material candidates, reject false capacity conclusions and name the exact fact required next; and (2) when Ministry-grade line-level records are added, the same engine can resolve effective capacity, capability distance, economics, minimum intervention, national value and route." It "is not a generic 'AI opportunity ranking' dashboard."
- Core 01 §9: success is when a Ministry audience can observe, without developer explanation, that the engine refuses unsupported factory recommendations, that public evidence yields meaningful decisions and precise evidence requests, that Ministry data changes identifiable gates, that synthetic evidence is honest and controlled, that calculations are inspectable, and that the output is a route and Decision Dossier, not a ranking.
- Core 01 §10: "Public data tells us where the decision is blocked. Your line-level records make the same decision decisive."
- Owner, 2026-09-02: "a professional, smart and genuinely interactive public-plus-synthetic POC that demonstrates the methodology's strength and the value of connecting Ministry data", delivered as "a generalized, ministerially presentable demonstration rather than only a two-fixture technical page", with required outcomes A–G and a release-acceptance list, and with authentication, official approval workflow and confidential Ministry connectors explicitly out of scope.

## 3. What v0.2.0 actually is (VERIFIED)

One offline FastAPI process serving a static single-page analyst workspace over two hand-frozen public snapshots and two synthetic scenarios. The deterministic core (R-rule ledger, effective capacity, K/U/D\*, NPV/IRR/S\*, ΔNV, competition ratio, EVSI), the public/synthetic isolation (deep copy, fingerprint, Class-D labelling, Gate B reconciliation, ground-truth back-test) and the release engineering (CI on three Python jobs plus Docker, integrity hashes, threshold-literal scanner, prohibited-file scanner, 42-step acceptance runner) are real and green.

Structurally, however, v0.2.0 is bound to its two fixtures in four places that matter for v0.3.0:

| # | Binding | Evidence | Consequence |
|---|---|---|---|
| F1 | The public decision is read from the snapshot, not computed. `_public_decision` returns `REJECT` when `rule_context.generic_capacity_reject` is true and R11 fires, otherwise `INVESTIGATE`; rationale, missing facts and kill conditions are copied from `public_decision_contract`. | `src/ior_mvp/decision_engine.py:37-65` | No `MONITOR`, no route sequence, no computed gap diagnosis. A new snapshot must carry a hand-authored decision to be analysable. |
| F2 | Five public rules fire from author-supplied boolean flags rather than from evidence: R4-D (`r4_degraded_dispersion_signal`), R5 (`domestic_production_exists`, `material_imports_exist`), R9-S (`same_process_family_plus_signal`), R10 (`strategic_resilience_review`), R11 (`generic_capacity_reject`). | `rules.py:596-731`; `SAU-H0-721049.json:124-131` | The snapshot author decides the rule outcome. Universe screening cannot reuse these rules. |
| F3 | The simulation selector knows only three outcomes: equivalence → `REJECT` route 0; the §7.3 conjunction → `ADVANCE` route 5; otherwise `INVESTIGATE`. Routes 1, 2, 3, 4, 6, 7, 8 and simulated `MONITOR` do not exist. | `decision_engine.py:671-694` | Ten deep cases spanning the intervention routes cannot be expressed. |
| F4 | Scenario and snapshot schemas omit the fields the methodology needs for R5, R8, tariff-line/buyer allocation, expansion assumptions, quantity-basis HHI and the four decision-critical evidence classes. | `rules.py:285-355` (R8 always DISABLED), `rules.py:608-645` (R5 always NOT_CALCULABLE), `evidence.py:615-635` (allocation NOT_APPLICABLE), `SAU-H0-721049.json:59-75` (value HHI only), `evidence_policy.v1.yaml:13-18` unused in `src/` | KL-25..28 and the reviewer's uncovered statements are schema gaps, not only code gaps. |

The interface is a single 464-line `app.js`, a 335-line `styles.css` with 71 lines carrying hex colour literals outside the `:root` token block, and an `index.html` declared `lang="en"` with Arabic present only as `dir="rtl"` spans. There is no browser-automation test (KL-22), no Executive Mode, no language switch, no graph, no screening surface, and the "Synthetic leakage" KPI is the literal string `"0"` (`app.js:72`).

## 4. Gap register by owner outcome area

Gap classes: **MISSING** (nothing exists), **PARTIAL** (exists but does not meet the owner requirement), **PRESENT** (meets it; must be preserved and extended). "Authority" states which Manifest §7 change class closing the gap requires. Slice IDs refer to `SLICE_GRAPH.md`.

### A. Real-browser and UX acceptance

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| A1 | Playwright end-to-end tests in real Chromium. | `tests/test_static_frontend.py` parses HTML/CSS/JS source; no browser automation anywhere in `tests/` (grep); KL-22 accepted. | MISSING | none (Core 09 §2.7 already names Playwright as the production addition) | S06 |
| A2 | Test every case selector, evidence-mode switch, dossier action, source drill-down, graph interaction, reset action. | Selectors, mode switch and dossier exist (`index.html:44-48, 96-98`; `app.js:363-392`). No drill-down links, no graph, no reset. | PARTIAL | none | S06 (existing controls), S17/S18/S21 (new controls) |
| A3 | Desktop, tablet and presentation-screen widths. | Media rules at 1180/900/560 px (`styles.css:296-326`); never rendered in a browser; no ≥1920 px treatment. | PARTIAL | none | S06, S07 |
| A4 | Keyboard traversal, focus visibility, Arabic RTL, printing and PDF output. | Native controls and `dir="rtl"` spans exist; dossier has `@media print` (`dossier.py:142`); none browser-verified (KL-22); no PDF generation. | PARTIAL | none | S06, S19 |
| A5 | Fail CI on browser-console errors, failed network requests, inaccessible controls. | CI has no browser job (`.github/workflows/ci.yml`). | MISSING | none | S06 |
| A6 | Visual-regression screenshots for all principal journeys. | None. | MISSING | none | S06 (reference screenshots of the v0.2.0 baseline only), S07 (governed visual-regression baselines for the v0.3 UI), then every UI slice |
| A7 | Preserve the analyst workspace; add a separate Executive Mode with the eight progressive steps. | One workspace; `index.html` sections overview/workspace/methodology/extraction/governance; no narrative mode. | MISSING | Core 01 (new journey/FRs), Core 03 §7 registry | S18 |
| A8 | Complete Arabic and English interface switching. | UI chrome English only (`index.html:2 lang="en"`); Arabic only in product names and extraction spans; dossier HTML English with one RTL paragraph (`dossier.py:152`). | MISSING | evidence_policy (Arabic synthetic label), Core 01 NFR-007 extension | S07 |
| A9 | Synthetic evidence visibly labelled at all times. | Enforced: policy label, `.synthetic-row`, banner, dossier disclosure (`evidence_policy.v1.yaml:35`; tests TL-09). | PRESENT | none — extend to Arabic and to graph/screening/exec surfaces | all UI slices |
| A10 | Firm interface rules (SG-TR-008): tokens only, components < 200 lines, named exports, keyboard reachable, contrast checked, locale parity with verified bidirectional layout. | 71 hex literals outside `:root`; one 464-line module; no ES modules (KL-21 accepted). | PARTIAL | none | S07 |
| A11 | Live integrity KPI rather than a hard-coded value. | `app.js:72` renders the string `"0"` for synthetic leakage (reviewer residual 1). | PARTIAL | none | S18 |

### B. Public-universe screening

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| B1 | Reproducible public-data acquisition and snapshot pipeline with explicit commands; runtime stays offline. | Core 05 §10 states "the current POC begins at the snapshot stage"; the `SourceConnector` interface is specified but not implemented; no `acquisition` module; no raw artifacts under `data/`. | MISSING | Core 05 v2 (implemented connectors, raw store), Core 03 (component), data/raw + manifests | S11, S12 |
| B2 | Preserve raw responses, query contracts, retrieval dates, licenses, hashes and transformations. | Snapshots carry `url`, `as_of_date`, `snapshot_id` and an authority note only (`SAU-H0-721049.json:1-5, 147-203`). No raw file, no query contract, no license, no per-source hash, no transformation record — the Core 05 §4 source contract and methodology §11.3 bundle are unimplemented. | MISSING | Core 04 §2.8 passport fields, Core 05 v2 | S11 |
| B3 | Sources: UN Comtrade or WITS; BACI where licensing permits; GASTAT aggregates; Saudi tariff hierarchy; Ministry/MODON directories; Tadawul and producer disclosures; Etimad documents; SASO/SABER metadata. | None implemented. Reachability this session: WITS/Etimad/CEPII/ZATCA reachable; Comtrade API host reachable; Tadawul bot-protected; GASTAT timed out; MODON TLS failure; SABER host reachable (§0). | MISSING | Core 05 v2 | S11 (trade + tariff), S12 (institutional + documents) |
| B4 | Never fabricate unavailable public fields. | Enforced for the two fixtures by construction. | PRESENT | none — becomes an acquisition-pipeline rule: every unobtainable field is `UNAVAILABLE` with the observed response recorded | S11, S12 |
| B5 | Low-cost screening across the available Saudi HS6 universe. | Two IDs; rules depend on author flags (F2). | MISSING | Core 07 v2 screening stage (§12 steps 3–5), Core 04 screening record, data universe snapshot | S13 |
| B6 | Candidate queues: robust public finding; incumbent-upgrade investigation; resilience case; likely false positive; high-EVSI evidence investigation. | None. Methodology §8.2 ranking rule requires five route-specific queues and forbids one ordinal list. | MISSING | Core 01 FR, Core 03 surface, Core 04 | S13 |
| B7 | Deep-resolution cases may remain a subset; universe screening must be real and reproducible. | n/a | — | — | S13 (screening), S14–S15 (subset) |

### C. Generalized case engine

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| C1 | Remove fixture-dependent behaviour. | F1–F4 above. | MISSING | Core 04, 06, 07 v2 | S08, S09, S10 |
| C2 | A new governed snapshot is analysable without modifying Python. | Requires an authored `public_decision_contract` and `rule_context` today; repository loads any `data/snapshots/public/*.json` (`data_repository.py:29-43`) but the engine still needs the authored decision. | PARTIAL | Core 04 schema v2 | S08, S09 |
| C3 | At least 10 deep cases across all five sector profiles. | 2 cases, 2 profiles (`sector_profiles.v1.yaml`; KL-20). | MISSING | sector_profiles 1.1.0; data/**; Core 09 golden list; `project.yaml` golden list | S09 (profiles), S14, S15 (cases) |
| C4 | Cases producing REJECT, MONITOR, INVESTIGATE, SIMULATED ADVANCE. | REJECT, INVESTIGATE, SIMULATED ADVANCE exist; MONITOR is an enum value only (`decision_engine.py:113`; KL-23). | PARTIAL | Core 07 v2 MONITOR condition (see OD-1) | S09, S14, S15 |
| C5 | Demonstrate no-action, administrative/information, certification, demand, brownfield expansion, technology/JV and greenfield route logic where evidence supports. | Routes 0 and 5 only (F3). Methodology §7.1.1 mandatory sequence and §7.4 decision tree not executed (KL-24). | MISSING | Core 07 v2 §7.1–7.4 | S09, S10 (routes 0–7 plus the governed route-8 contract), S16 (route 8 activated on the real graph) |
| C6 | Synthetic scenarios remain Class D and affect only `simulation_decision`. | Enforced (`evidence.py:51-108, 699-715`; TL-09). | PRESENT | none — preserve in every new scenario | all |
| C7 | Every scenario reconciles to public marginals and carries planted ground truth. | Enforced for demand, nameplate, factors, qualified availability; allocation stubbed `NOT_APPLICABLE` (`evidence.py:615-635`); ground truth mandatory (ADR-006). | PARTIAL | Core 06 v2 allocation schema | S10 |
| C8 | No product ID may directly determine a decision or route. | No ID dispatch since ADR-006, but the per-ID authored contract has the same effect (F1). | PARTIAL | Core 07 v2 | S09 |

### D. Material methodology gaps

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| D1 | All five sector profiles with tests. | 2 of 5 (KL-20). Methodology §6.3 gives exact weights for pharma/API, fertilizers and fabricated aluminium and "illustrative" hard gates. | MISSING | sector_profiles 1.0.0 → 1.1.0 (§7.3) | S09 |
| D2 | Supplier HHI on value and quantity. | `partner_value_hhi` only (`rules.py:539-572`); methodology §3.3 requires both bases. Quantity basis needs partner-level quantity rows that the frozen worked cases do not contain. | MISSING | Core 07 v2 (R3 dual basis, interpretation in OD-1), Core 04 partner rows | S08 |
| D3 | Execute the generic evidence-policy ADVANCE gate. | `evidence_policy.advance_gate` has zero references in `src/`, `scripts/`, `tests/` (grep). Public ADVANCE is vacuously impossible because the selector only emits REJECT/INVESTIGATE (F1) — an encoded "public can never ADVANCE", which the owner ruling R-1 (§7A) forbids in the generalized engine. | MISSING | Core 07 v2; evidence_policy 1.2.0 (field-class assessment contract) | S09 |
| D4 | Contradiction records in the Decision Dossier. | Snapshot retains `contradiction` (`SAU-H0-721049.json:189`); `dossier.py:7-69` does not project it; methodology §15 requires "Evidence: top supporting and contradictory evidence" and §15.1 a contradiction register. | MISSING | Core 04 §9 dossier projection | S08 |
| D5 | Governed tariff-line and buyer-allocation scenario schemas. | Absent (KL-28); reconciliation returns `NOT_APPLICABLE`. Core 05 §8 rule 4 and Core 06 §5.1 require reconciliation when blocks exist. | MISSING | Core 06 v2 | S10 |
| D6 | Governed expansion-assumption schema. | Absent (KL-27); nameplate ceiling is absolute. | MISSING | Core 06 v2 | S10 |
| D7 | R5 calculable when compatible production and retained-flow data exist. | Always `NOT_CALCULABLE` (`rules.py:630-644`); methodology §3.3 formulas for retained imports, apparent consumption and import penetration are not implemented. | MISSING | Core 04 fields, Core 07 v2 | S08 (formula + schema), S12 (public production aggregates where GASTAT permits) |
| D8 | R8 calculable when base demand, commitment probability and MES exist. | Always `DISABLED` (`rules.py:285-355`; KL-25). | MISSING | Core 06 v2 scenario fields | S10 |
| D9 | Exercise the complete mandatory route sequence. | Not executed (KL-24; F3). | MISSING | Core 07 v2 | S09 (public route hypotheses), S10 (simulation, routes 0–7 + route-8 contract), S16 (route 8), S22 (route-coverage matrix) |
| D10 | Preserve FULL, DEGRADED, DISABLED, NOT_CALCULABLE semantics exactly. | Implemented (`rules.py`, S04). | PRESENT | none — regression-locked | all |
| D11 | Missing evidence reduces permission rather than becoming zero. | Enforced after RV-05 (`economics.py:27-38`). | PRESENT | none — regression-locked | all |
| D12 | (KL-30) R1-D confidence cap emitted as a literal string. | `rules.py:478` hard-codes `"C"` although `thresholds.rules.R1_D.confidence_cap` exists. | PARTIAL | none | S08 |

### E. Real capability and dependency graph

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| E1 | Real Neo4j graph, not a diagram or JSON. | No graph; Core 03 §8.1 says the POC has "no database"; Core 04 §8 lists graph mapping as a production concept. | MISSING | Core 03 v2 (graph runtime), Core 04 §8 v2 | S16 |
| E2 | Governed node types (19 listed) and evidence-backed relationships (15 listed). | Core 04 §8 lists 17 nodes / 13 edges with different names (e.g. `HAS_SPECIFICATION`, `REQUIRES_STANDARD`, `BLOCKED_BY`, `ALTERNATIVE_TO`). The owner list adds `TariffLine`, `Capability`, `Company`, `CustomerSegment`, `Scenario` and edges `CLASSIFIED_AS`, `REQUIRES_SPECIFICATION`, `HAS_CAPABILITY`, `REQUIRES_INPUT`, `CERTIFIED_TO`, `QUALIFIED_FOR`, `ADJACENT_TO`, `CONSTRAINED_BY`. | MISSING | Core 04 §8 v2 must adopt the owner's vocabulary as the governed minimum and map the existing names | S16 |
| E3 | Provenance, as-of date, confidence class and synthetic/public status on every decision-relevant node and edge. | Evidence passports exist for public rows (`SAU-H0-721049.json:147-203`) and are generated for synthetic blocks (`evidence.py:718-735`); no graph carries them. | MISSING | Core 04 v2 | S16 |
| E4 | Interactive graph view: why brownfield is adjacent; which missing capability blocks the route; which shared enabler unlocks several opportunities; which evidence would change the decision. | None. Methodology §8.3 UnlockValue formula is unimplemented. | MISSING | Core 03 §7 registry (new approved component), Core 02 map | S17 |
| E5 | Graph queries contribute to actual results and tests; not decorative. | n/a | — | Core 07 v2 (which results are graph-fed), Core 09 | S16 |
| E6 | Local/CI operability. | Docker present; `neo4j:5.26.30` image cached; ports 7474/7687 taken by a foreign container (§0). CI has no service container. | MISSING | none | S16 |

### F. Bilingual specification extraction

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| F1 | Replace the four-record corpus with a meaningful labelled Arabic/English public corpus from real tenders and producer documents. | `data/golden/ar_en_spec_extraction.json` has 4 UNICOIL records; extractor is regex tuned to them (`ai_extraction.py:27-48`, e.g. `"60" in combined and "gsm"`). Core 08 §9 names Etimad as the next expansion set and states the package "does not fabricate Etimad excerpts". | MISSING | Core 08 v2; data/golden (§7.5 evidence refresh) | S20 (corpus from S12 documents) |
| F2 | Preserve exact source spans. | Contract preserves `source_spans` (`ai_extraction.py:20`); no document/page/line identity. | PARTIAL | Core 08 v2 §9 fields | S20 |
| F3 | Measure precision, recall and field-level accuracy. | Only pass count (`ai_extraction.py:54-82`); Core 08 §8 lists the metrics and suggested gate values as "implementation targets … require calibration on a real labeled corpus". | MISSING | Core 08 v2 | S20 |
| F4 | Production-shaped adapter contract. | FR-073 `NOT_APPLICABLE (production)`; Core 08 §7 dual pass specified, not implemented. | MISSING | Core 08 v2 | S20 |
| F5 | Optional local LM Studio adapter; offline deterministic golden path preserved; LLM never calculates D\*, NPV, IRR, S\*, ΔNV or routes. | No adapter. Core 08 §3 prohibits the calculations. | MISSING | Core 08 v2 | S20 |

### G. Ministry demonstration experience

| ID | Owner requirement | v0.2.0 state (evidence) | Gap | Authority | Slice |
|---|---|---|---|---|---|
| G1 | One-command clean start and one-command demo reset. | `START_DEMO_WSL.sh`, `make run`, `docker compose up` start the app; nothing resets state; with a graph and screening data a reset target is required. | PARTIAL | none | S21 |
| G2 | Five-minute executive journey and fifteen-minute analyst journey. | `MINISTRY_DEMO_SCRIPT.md` is a single ≈10-minute two-case script. | PARTIAL | none (implementation docs) | S21 |
| G3 | Public and simulated results side by side. | Toggle only; banner shows `real_state → active_state` (`genui.py:19-29`). | PARTIAL | Core 03 §7 registry | S18 |
| G4 | "What Ministry data unlocks" panel quantifying which missing datasets resolve which opportunities. | Per-case `data_unlocks` list of authored strings (`decision_engine.py:98`); no cross-case dataset → opportunity mapping; no quantification. Deterministic counts are honest; monetary quantification requires Class-D elicitation inputs and must be labelled as such. | MISSING | Core 01 FR, Core 04 (dataset taxonomy), Core 07 v2 (EVSI aggregation rule) | S18 |
| G5 | Source-level drill-down from every major claim. | Evidence ledger exists; metric cards and rule rows are not linked to evidence IDs (`genui.py`, `app.js:189-345`). | PARTIAL | Core 04 (claim → evidence_id contract) | S18 |
| G6 | Professionally formatted bilingual Decision Dossier export. | English HTML with inline hex CSS (`dossier.py:129-162`); covers only part of the methodology §15 block list (no gap-taxonomy class, no supply conclusion narrative, no contradictions, no competition block text). | PARTIAL | Core 04 §9 | S19 |
| G7 | Never describe synthetic evidence as observed, official or Ministry-provided. | Enforced in English (policy label, tests). Arabic label does not exist. | PARTIAL | evidence_policy 1.2.0 | S07 |

## 5. Additional normative statements found uncovered in the full methodology read

The S05 final reviewer listed three uncovered statements (quantity-basis HHI; the unexecuted `advance_gate`; the contradiction register on the dossier). The full re-read this session adds the following. None is a defect of the v0.2.0 release contract; each is a coverage gap the generalized engine must close or record.

| Methodology location | Statement | v0.2.0 coverage | Disposition in v0.3.0 |
|---|---|---|---|
| §3.3, Appendix A | Retained imports, net import exposure, apparent consumption, import penetration formulas. | Only `gross_net` stored; no computation. | S08 implements the formulas with explicit `UNAVAILABLE` inputs; public branch stays `NOT_CALCULABLE` unless GASTAT/production aggregates are acquired (S12). |
| §4 R1-F | Materiality "above the higher of the policy floor or the 75th percentile within its NIS cluster". | Config key `materiality_percentile_within_nis_cluster` exists; no cluster data; no policy floor value. | The policy floor is an owner policy value (SG-TR-001). Not requested now: R1-F remains DISABLED/DEGRADED honestly unless the owner later supplies the floor and a NIS cluster mapping. Recorded as a deferred owner decision, not a blocker. |
| §4 R2 | "initial quantity CAGR trigger ≥5%". | Single-period growth `latest/previous − 1` (`rules.py:497`); identical for adjacent years, not for a 2021→2023 pair with a missing year. | S08: compound annual rate over the observed span, disclosed in metrics; goldens unchanged (2023→2024 is one year). |
| §4.2 | Six hard exclusions before deep analysis. | Only the generic-capacity exclusion via R11. | S09 operationalizes each exclusion as a typed check with `NOT_CALCULABLE` where inputs are absent. |
| §5.3 | Gap taxonomy (false/measurement, quantity, specification, application, timing, resilience, evidence) and the dossier's "Gap diagnosis" block. | Not emitted as a typed field. | S09 adds a deterministic gap classifier; S19 projects it. |
| §6.6 | Brownfield-versus-greenfield counterfactual questions 1–6. | Partly implicit in route band. | S10 records the six answers as typed fields (answered, or `UNAVAILABLE`) in the simulation branch. |
| §7.1.1, §7.4 | Mandatory route sequence and intervention decision tree. | Routes 0 and 5 only. | S09/S10 (see C5, D9). |
| §7.5 | Competition gates: incumbent displacement, market concentration before/after, non-additional support, instrument neutrality, conditions and sunset. | Capacity ratio and displacement component only. | S10 adds non-additionality and concentration-before/after checks where inputs exist; `NOT_CALCULABLE` otherwise. |
| §8 | Four decision vectors kept separate (market/gap, strategic/resilience, execution feasibility, evidence confidence); §8.2 five queues; §8.3 UnlockValue. | Not emitted; no queues; no UnlockValue. | S13 (queues), S16 (UnlockValue), S18 (vectors in Executive Mode). |
| §11 evidence passport | Source identity, observation context, measurement, transformation, status, confidence, contradiction, approval. | Partial fields on public rows. | S11/S12 generate complete passports for acquired evidence; S08 extends the schema. |
| §12 pseudocode | `if not triggers: emit(MONITOR_or_REJECT)`; `emit(INVESTIGATE, next_fact=max_EVSI(...))`. | No MONITOR; EVSI only in simulation. | S09 (MONITOR condition, OD-1); S13 screening-stage emission. |
| §10.3, §16 | Accountable authorization/override record; outcome learning. | Documented extension points. | Out of scope for v0.3.0 by owner instruction (no approval workflow); remain documented extension points. |

## 6. Authority-change inventory (Manifest §7)

The owner's v0.3.0 requirements exceed what the frozen core (rank 2) and configuration (rank 3) currently define. `AGENTS.md` classifies any change to `config/*.yaml`, `data/**`, `docs/core/**` or a golden expectation as an authority change that must be justified in the slice ADR and PR before `scripts/build_manifests.py` runs, with the two public golden outcomes shown unchanged. The methodology DOCX (rank 1) is **not** changed by anything in this milestone.

| Artifact | Current | Proposed for v0.3.0 | Manifest class | Why |
|---|---|---|---|---|
| `docs/core/01`–`09` | frozen v1 set | core **v2** revision, per slice, each hashed through the change gate | §7.4 core version (methodology meaning unchanged; coverage extended) | Owner requirements A–G define contracts the v1 core does not (screening, acquisition, graph, executive surface, route generalization, schemas). |
| `config/sector_profiles.v1.yaml` | 1.0.0, 2 profiles | 1.1.0, 5 profiles with §6.3 weights; hard-gate names derived from §6.3 text | §7.3 | D1 |
| `config/evidence_policy.v1.yaml` | 1.1.0 | 1.2.0: Arabic display label; decision-critical field-class assessment contract for the executed ADVANCE gate; "assumed-if-confirmed class" rule for the simulation branch | §7.3 | D3, G7, A8 |
| `config/thresholds.v1.yaml` | 1.1.0 | unchanged unless a slice proves a missing key (any addition goes through §7.3 with rationale) | §7.3 if touched | Thresholds stay in YAML (AGENTS.md #7). |
| New governed bilingual narrative/label catalogue | none | versioned, hashed YAML for decision-state/route text in EN and AR | §7.3 (new operating artifact) | A8, G6; text must not live in code. |
| `data/snapshots/public/*` | 2 v1 files | v1 files retained byte-identical as historical; v2 re-expressions of the same frozen 2026-08-31 facts under new snapshot IDs; new acquired snapshots under their own IDs and as-of dates | §7.5 evidence refresh | C2, B1; Core 05 §5 step 12 forbids overwriting history. |
| `data/synthetic/*` | 2 scenarios, contract 1.1.0 | migrated to contract 2.0.0 with unchanged numeric inputs and unchanged outcomes; new Class-D scenarios for new cases | §7.3 scenario parameters | C7, D5, D6, D8 |
| `data/raw/**`, `data/universe/**`, `data/graph/**`, `data/golden/**` | absent / 4 records | raw artifacts with hashes and query contracts; universe screening snapshot; graph export; labelled extraction corpus | §7.5 | B, F |
| `data/manifests/snapshot_manifest.json`, `docs/authority/authority_hashes.json` | frozen | regenerated only inside reviewed PRs after regression | §8 | — |
| `config/project.yaml` | golden_cases 2 | golden list extended; version 0.3.0 at release | unhashed | C3 |

**Preservation rules that bind every slice (SPECIFIED):** steel public `INVESTIGATE` and PP public `REJECT` route 0 remain exact; steel simulated `ADVANCE` route 5 with 57.509 kt / 46.491 kt / D\* 0.2667 / S\* 18 / ΔNV 198 / ratio 1.0751 and PP simulated `REJECT` with −24 kt gap and zero support remain exact; no synthetic value is ever labelled observed, official, Ministry-provided or Class A/B/C; no real `ADVANCE` while a decision-critical field is Class D/E; unknown capability never improves D\*; thresholds stay in YAML; unit value never proves grade; lower-cost routes precede supported greenfield.

## 7. Interpretations fixed for the Core v2 text (OD-1: approved 2026-09-02, I1 and I5 as amended by the owner)

Manifest §10 requires stopping when a methodology term has more than one defensible interpretation. The generalized engine cannot be built without fixing the following in Core 07 v2. The owner approved I2, I3, I4, I6, I7 and I8 as written and amended I1 and I5; the amended text below is the governing wording.

| # | Term | Governing interpretation (SPECIFIED by owner ruling 2026-09-02) | Basis |
|---|---|---|---|
| I1 | Engine condition for `MONITOR`, and the screening disposition | At universe-screening level, the absence of candidate triggers is a **screening disposition** (`NO_CANDIDATE` / `SCREENED_OUT`), distinct from the four formal decision states; it is never automatically a formal `REJECT`. A formal `REJECT` requires an evidenced rejection condition or hard exclusion (false or measurement gap, §4.2 exclusion, uneconomic route at efficient scale, structural overcapacity, equivalence with idle qualified supply). R3-only resilience may produce `MONITOR`. A decision-critical unresolved or contradictory fact with positive evidence value produces `INVESTIGATE`. `MONITOR` requires a named observable future trigger (demand, regulation, technology, supplier concentration or capacity state) and applies when no exclusion or rejection condition is evidenced, at least one signal exists, and the material trigger is absent. | §1.2 state table ("watch a defined trigger"); §7.4 "No verified gap → REJECT or INVESTIGATE"; §4 R11 "Reject or monitor"; §12 `emit(MONITOR_or_REJECT)`; owner amendment. |
| I2 | R3 on two bases | Compute HHI and largest-supplier share on value and on quantity; report both; R3 fires when the configured test is met on either basis; `NOT_CALCULABLE` on a basis whose rows are absent. Golden steel unchanged (value HHI 0.36). | §3.3 "calculated on retained import value and quantity separately"; §4 R3 single threshold pair. |
| I3 | R2 growth window | Compound annual growth over the observed span between the two compared years. | §4 R2 "quantity CAGR". |
| I4 | ADVANCE gate inside the simulation branch | The gate evaluates the scenario's declared "class if confirmed" for the four decision-critical fields; the emitted record stays Class D, `SIMULATED`, and labelled — the actual evidence class of every synthetic record is always D. A scenario that does not declare a confirmed-class for a decision-critical field cannot produce `SIMULATED ADVANCE`. | Core 06 §1 "what the engine would calculate if the displayed Ministry-grade facts were confirmed"; methodology §2.1 ADVANCE GATE. |
| I5 | Route selection across routes 0–8 | Evaluate alternatives in the mandatory §7.1.1 sequence, each recorded as `passes` / `fails` / `NOT_CALCULABLE` with its reason. A lower-cost route that fully resolves the binding constraint prevents unnecessary escalation to a more interventionist route (precedence gate; supported greenfield cannot leapfrog lower routes). Among the remaining feasible, additional and policy-permissible alternatives, select the route with the **highest defensible incremental national value**, subject to downside economics, competition, distortion, proportionality and evidence gates. Financial support is evaluated only after unsupported and applicable non-financial routes fail. "First passing route wins" is **not** the final selection algorithm. Route 7 requires D\* > 0.65 with MES and competition tests passed. Route 8 requires a graph-identified shared enabler with positive UnlockValue computed on the governed Neo4j projection; until that graph exists (S16) route 8 is `NOT_CALCULABLE` / `GRAPH_REQUIRED` and is never approximated in memory. | §7.1.1, §7.4, §8.3, §12 `select_max_incremental_national_value(alternatives)`; owner amendment. |
| I6 | Gap taxonomy classifier | Ordered deterministic tests over evidence fields producing exactly one primary class and any secondary classes, `evidence` when decision-critical inputs are unresolved. | §5.3. |
| I7 | Hard exclusions | Each of the six §4.2 bullets becomes a typed check with explicit inputs; a satisfied exclusion yields `REJECT` before deep analysis; unknown inputs yield `NOT_CALCULABLE` (never a pass). | §4.2; NFR-003. |
| I8 | "What Ministry data unlocks" quantification | Deterministic counts of opportunities blocked per missing dataset are public-derived; monetary EVSI aggregates use scenario-declared elicitation inputs and are shown Class D with the synthetic label. | §9.1; Core 06 §9 prohibited behaviour. |

## 7A. Additional binding owner rulings (2026-09-02)

These rulings are governing for every v0.3.0 slice and are recorded as ADR-010.

| # | Ruling | Effect on slices |
|---|---|---|
| R-1 | **ADVANCE is evidence-gated, not source-type-gated.** The generalized public engine must technically permit a real `ADVANCE` whenever actual Class A/B/C evidence and every methodology gate genuinely support it. "Public can never ADVANCE" must not be hard-coded. No v0.3.0 demonstration case is required to reach a real public `ADVANCE`. Synthetic evidence remains Class D and may produce only `simulation_decision` (`SIMULATED ADVANCE` at most). | S09 selector and tests (a fixture with A/B/C evidence passing every gate must reach `ADVANCE`; the same fixture with any decision-critical field at D/E must not); S10 (I4); all goldens unchanged. |
| R-2 | **No route 8 before the graph.** S10 implements routes 0–7 plus the governed route-8 contract. Until S16, route 8 returns `NOT_CALCULABLE` / `GRAPH_REQUIRED`. S16 activates and tests route 8 using real Neo4j dependency queries and UnlockValue. No in-memory substitute may stand in for the graph to satisfy route coverage. | S10, S16, S22 route matrix. |
| R-3 | **Neo4j is a governed projection, not a second source of truth.** Canonical evidence records and frozen snapshots are the evidentiary system of record. Neo4j is an idempotently rebuildable projection of those governed records. No decision-relevant node or edge may exist without a canonical evidence origin; every decision-relevant node and edge carries provenance, as-of date, evidence class and public/synthetic state; rebuilding the graph from identical governed inputs must reproduce the same graph-fed results. Core v2 states this explicitly. | Core 03/04 v2 text; S16 rebuild-reproducibility test; S17; S21. |
| R-4 | **Visual-regression oracle sequencing.** S06 establishes real-browser functional, accessibility, network-failure and console-error gates, keyboard traversal, and reference screenshots of the v0.2.0 baseline. The governed visual-regression baselines are established in S07 after the bilingual/token/module redesign, so the oracle is not deliberately obsoleted one slice later. | S06, S07. |
| R-5 | **Route-coverage acceptance matrix.** By S22 an audit table for routes 0–8 must exist: route → case/scenario → binding constraint → why lower routes failed → evidence → expected state → actual state. Any route not truthfully demonstrated (routes 1, 2, 3, 4, 6, 7 and 8 in particular) is brought back to the owner for explicit re-approval before the milestone is called complete. | S14, S15, S16 populate; S22 audits (`SLICE_GRAPH.md` §9 template). |
| R-6 | **Neo4j provisioning.** A fresh project-owned Neo4j 5.x Docker service provisioned by the build itself (no Aura instance; no reuse or inspection of any container or database belonging to another project); the local `neo4j:5.26.30` image if compatible; dedicated container name (`industrial-mvp-neo4j`), dedicated volume, project-specific network, host ports other than the occupied 7474/7687 (preferably 7475 Browser / 7688 Bolt unless the planner finds a conflict), pinned version, health check, idempotent initialization, deterministic constraints/indexes, graph rebuilt entirely from governed snapshots/scenarios with no manually entered facts, provenance on every decision-relevant node and edge, public queries excluding synthetic evidence, fail-closed `GRAPH_UNAVAILABLE`, CI starting its own clean service and running real Cypher integration tests. No real password in Git: local runtime credentials are generated into a git-ignored runtime secret file without printing the password into agent context or logs; only an example/template is committed. `make demo-up` provisions Neo4j automatically; the owner never creates databases or nodes by hand. | S16, S21. |

## 8. Cross-cutting constraints carried into every slice

1. Synthetic isolation, Class-D labelling and the fingerprint assertion apply to every new surface: screening, graph, Executive Mode, Arabic strings, PDF. Public graph queries filter `synthetic_flag=false`.
2. No public field is ever fabricated. Acquisition records `UNAVAILABLE` with the observed response; blocked sources become recorded limitations, not invented rows.
3. Thresholds and governed text stay in versioned YAML; the AST literal scanner extends to new packages.
4. Unknown remains unknown (`NOT_CALCULABLE`, `UNAVAILABLE`, `GRAPH_UNAVAILABLE`); missing inputs never become zero or a pass.
5. LLM boundary (Core 08 §3): the optional adapter may only populate the extraction schema; all arithmetic, D\*, routes and states are code.
6. Offline runtime and CI: no live call in tests or runtime paths; acquisition runs only through explicit commands; goldens use hashed local snapshots.
7. Golden preservation and history retention: new snapshot IDs, never overwrite, historical snapshots retained; live-source drift never loosens a golden.
8. Model separation (ADR-002 continues): Supervisor = Claude; Planner and Implementer = GPT-5.6 Sol; Independent Reviewer and final holistic reviewer = Grok 4.6. Finite ladders: at most four plans and eight implementation candidates per slice; exhaustion is `BLOCKED_FOR_OWNER`.
9. Data classification `confidential_demo`: public and Class-D data only; agents verify only the existence, ignore-status and variable names of `.env`, never values.
10. Firm interface rules (SG-TR-008) apply to all new frontend code: tokens only, components under 200 lines, named exports, keyboard reachability, contrast checks, AR/EN content parity with verified bidirectional layout.

## 9. Risks

| Risk | Treatment |
|---|---|
| Live WITS/Comtrade figures for 721049/390210 as of 2026-09 differ from the frozen 2021/2023/2024 worked-case rows. | Golden snapshots stay bound to the methodology's frozen 31 Aug 2026 facts; acquired data receives its own snapshot ID and as-of date; the two are never spliced; differences are displayed and explained (Core 09 §5). |
| Source access or licensing: Comtrade may require a subscription key for bulk queries; BACI license terms; Tadawul bot protection; GASTAT availability; MODON TLS; ZATCA tariff tree may be HTML-only. | Record the license/terms from each source at acquisition; connectors fail closed to `UNAVAILABLE`; two-stage acquisition (world-total universe first, partner detail only for candidates surviving R1/R2) keeps volume and rate limits manageable; `BLOCKED_FOR_OWNER` only if a mandated source needs an owner-held credential. |
| Repository size from raw partner-level trade data. | Compressed raw artifacts; partner detail limited to surviving candidates; size budget tested; no Git LFS unless the planner proves necessity. |
| Neo4j in CI and locally: longer CI runs; host ports 7474/7687 already taken by a foreign container. | Project-owned compose service on distinct host ports and container name; GitHub Actions service container; runtime fail-closed `GRAPH_UNAVAILABLE`; graph tests split into stored-export unit tests and service integration tests. |
| Ten deep cases need real public evidence per profile; pharma/API and fertilizer disclosures may be thin. | Honest outcomes: `INVESTIGATE`/`MONITOR` where evidence stops; `SIMULATED ADVANCE` only where a reconciled scenario supports it; never fabricated public fields. |
| Extraction corpus labels are produced by agents, not domain reviewers. | Labels carry `reviewer_status: agent_labelled_pending_domain_review`; metrics are reported as demonstration metrics, not production gates. |
| Visual-regression flakiness. | Fixed viewports, disabled animations, deterministic fonts, tolerance thresholds, baseline updates governed like goldens (reviewer-approved). |
| Scope creep toward production features. | Authentication, approval workflow, confidential connectors, CRM, chat and document management remain excluded; each slice states explicit non-goals. |

## 10. Owner decisions — resolved 2026-09-02

**OD-1 — APPROVED WITH AMENDMENTS.** The owner authorizes the Core v2 revision under Manifest §7.4 with the methodology DOCX unchanged, the historical v0.2.0 release, tag and golden snapshots untouched, every authority change passing through its ADR and change gate, and the existing steel/PP outcomes proven unchanged in every affected PR. I2, I3, I4, I6, I7 and I8 are approved as written; I1 and I5 are approved as amended in §7; the binding rulings R-1 to R-6 in §7A apply.

**OD-2 — APPROVED WITH AMENDMENTS.** The slice graph and execution order `M3-P0 → S06 → S07 → S08 → S09 → S10 → S11 → S12 → S13 → S14 → S15 → S16 → S17 → S18 → S19 → S20 → S21 → S22` are approved with the S06/S07 oracle sequencing (R-4), the S10/S16 route-8 dependency (R-2) and the route-coverage matrix (R-5). The docs-only M3-P0 planning-baseline PR carries the amended documents; S06 implementation does not start until M3-P0 is merged and its default-branch CI is green.

Deferred (not blocking, recorded): the R1-F policy floor and NIS-cluster mapping (§5) remain an owner policy decision to be taken only if R1-F is to become `FULL`.

## 11. Owner action items carried from v0.2.0 (not decisions)

- Rotate the AI-provider API keys stored in the git-ignored workspace `.env`. This session confirmed only that the file exists, is ignored and contains three AI-provider key variable names; no value was read or printed. The S05 report and the S05 reviewer both recorded that an earlier implementer opened the file.
- Optionally move the repository to a GitHub plan with rulesets so the CI checks become required checks (ADR-007).

## 12. Muhasib self-audit

- Asked: a gap analysis between the owner objective and v0.2.0, and a v0.3.0 slice graph, after reading the methodology, Core 01–09, the final report, the limitations, the traceability, the complete final reviewer findings and the original objective; no code until approval.
- Read: everything in §1 with the Read tool; no document is claimed that was not opened.
- Verified: the baseline gates on `main` at `ce5786b`; every code citation by line; the absence of `advance_gate` references, browser tests, MONITOR production paths and Arabic UI strings by grep; tool and source reachability by command.
- Not verified: DOCX bytes against the mirror (hash identity from `authority_hashes.json`); source licences and access terms (to be recorded at acquisition); the content of the foreign Neo4j container (deliberately not inspected).
- Assumed: ADR-002 seat assignment continues; the owner's A–G text plus the 2026-09-02 rulings are the milestone scope; deep-case selection is an engineering decision within the five-profile requirement and the route-coverage matrix.
- Invented: nothing. No timeline, effort, cost or headcount figure appears in this document.
- Changed in the repository by M3-P0: this file, `SLICE_GRAPH.md`, ADR-010 in `docs/ARCHITECTURE_DECISIONS.md`, a v0.3.0 section in `docs/BUILD_ROADMAP.md`, a v0.3.0 ledger in `docs/BUILD_PROGRESS.md`, and an additive `milestones` block in `.workflow/state.json`. No v0.2.0 field, release record, code, config, data or core file is altered.
