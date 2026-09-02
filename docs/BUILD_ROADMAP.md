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
