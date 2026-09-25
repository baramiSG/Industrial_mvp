# Industrial Opportunity Resolution Engine — MVP / POC

A runnable Ministry demonstration of the **Industrial Opportunity Resolution Methodology**. The repository converts frozen HS-based public evidence into evidence-bounded decisions and then shows, in a strictly isolated simulation branch, how Ministry-grade line-level records can make the same case decisive.

Application and demonstration project release: `0.2.0`.

The MVP is intentionally not a generic opportunity-ranking dashboard. Its decision object is:

> **Product × Specification × Application × Capability × Demand × Route**

## What the demo proves

| Case | Public evidence result | Isolated Ministry simulation |
|---|---|---|
| HS 721049 — zinc-coated flat steel | `INVESTIGATE`; brownfield tested before greenfield; exact missing facts named | `SIMULATED ADVANCE`; conditional brownfield specification upgrade, effective capacity, D\*, NPV/IRR, S\*, national value, competition and kill conditions calculated |
| HS 390210 — polypropylene | `REJECT` generic capacity support; investigate only named grade/application exceptions | `SIMULATED REJECT`; equivalent qualified supply exceeds target demand, so support remains zero |

The real decision state is immutable. Synthetic evidence is separately flagged, separately displayed and can only create a `simulation_decision`.

## Included

- Original final methodology as the governing domain authority.
- Ten-document frozen implementation core.
- Versioned threshold, sector-profile and evidence-policy configuration.
- Eleven hashed public golden-case snapshots, including four S15b builder-derived cases.
- Eleven explicitly Class-D synthetic scenarios seeded from public marginals.
- Deterministic R0–R12 execution ledger.
- Price–quantity decomposition, concentration, effective capacity, K/U/D\*, NPV, IRR, S\*, incremental national value, competition ratio and EVSI.
- Schema-driven GenUI decision workspace assembled from an approved component library.
- Arabic–English specification extraction golden gate with preserved source spans.
- DecisionDossier2.0.0 JSON and bilingual printable HTML, with a one-page decision summary backed by the full evidence appendix and native Chromium Print / Save PDF.
- Manifest-verified bilingual S15 case-selection and exclusion surface at `/api/case-selection`.
- Governed Class-D shared-enabler declarations, graph-fed route-8 evaluation and the mounted `/api/graph` contract.
- A collapsed, lazy-loaded bilingual graph component with four deterministic SVG/native-control views and stored-evidence drill-down.
- FastAPI backend, offline frontend, tests, integrity manifests, Docker support and WSL startup scripts.

## Start in WSL

```bash
cd ~/projects
unzip Industrial_Opportunity_Resolution_MVP_POC.zip
cd industrial-opportunity-resolution-mvp
chmod +x START_DEMO_WSL.sh
./START_DEMO_WSL.sh
```

Then open:

```text
http://127.0.0.1:8000/?locale=en
http://127.0.0.1:8000/?locale=ar
```

The topbar language control switches all interface chrome, sets the correct
document direction, and persists only `ior.locale`. Engine-authored analytical
text remains visibly marked English source-language content in Arabic UI.

Engineer-only API documentation is available by direct navigation and is not
linked from the offline Ministry surface:

```text
http://127.0.0.1:8000/docs
```

## Faster start when dependencies already exist

```bash
cd industrial-opportunity-resolution-mvp
export PYTHONPATH="$PWD/src"
python3 scripts/verify_integrity.py
pytest -q
uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000 --reload
```

## Docker

```bash
docker compose up --build
```

## Integrity and tests

```bash
make verify
```

The integrity gate verifies:

1. the original methodology and frozen implementation documents;
2. threshold, sector-profile and evidence-policy configuration;
3. every public snapshot, synthetic scenario and extraction golden fixture.

Golden CI invariants include:

- steel/public → `INVESTIGATE`;
- steel/simulated → `ADVANCE` while steel/real remains `INVESTIGATE`;
- polypropylene/public → `REJECT` generic capacity support;
- synthetic evidence cannot enter the public evidence set;
- threshold values are loaded from versioned configuration rather than embedded in rule code;
- Arabic–English extraction passes the labeled golden set.

## CI and local gates

GitHub Actions runs the prohibited-file scan, recursive threshold-literal scan,
bilingual catalogue/token/copy contracts, Python compilation, recursive
ES-module syntax, integrity verification, Gate B scenario
reconciliation/back-test, full test suite and demo smoke on uv/Python 3.12,
uv/Python 3.14 and the documented pip path; it also builds the Docker image and
runs the dedicated live graph/UI step after graph-only equality and before the
stopped-service proof, and compares the governed functional and visual Chromium
matrix. The S17 source target is 112 visual paths after its separately approved
canonical generation.

After installing uv as described in `docs/DEVELOPMENT_GUIDE.md`, reproduce the required gates locally with:

```bash
make ci
bash scripts/final_acceptance.sh
```

The existing `pip install -e ".[dev]"`, `START_DEMO_WSL.sh` and Docker paths remain supported.

Create the reviewable source package from Git-tracked files only:

```bash
make package
```

The packaging command must run at the root of a Git working tree. Untracked and ignored workspace files, including `.env`, `.venv`, `.git`, and `.workflow/logs`, are not archive inputs.

## Evidence modes

### Public evidence

Only frozen, attributable public records contribute to `real_decision`. Missing line-level facts remain unresolved. Public cases may end in `REJECT`, `MONITOR` or `INVESTIGATE`; they do not receive a false `ADVANCE` merely because the user switches screens.

### Ministry simulation

The packaged simulation scenarios contain line availability, yield, qualification share, market allocation, target specification, demand layers, equivalence, economics, EVSI, hard gates, and capability states. They do not contain tariff-line or buyer-allocation blocks; see KL-28 in `docs/KNOWN_LIMITATIONS.md`. Every synthetic record carries:

```yaml
synthetic_flag: true
scenario_id: ...
source: DEMO_GENERATOR
evidence_class: D
display_label: SIMULATED — NOT MINISTRY EVIDENCE
display_label_ar: محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة
```

The simulation branch is intended to demonstrate the **value of connecting and cleaning Ministry data**, not to impersonate that data.

## GenUI approach

The backend emits a constrained UI manifest based on the decision context. It selects only approved components such as:

- evidence-boundary banner;
- decision hero;
- trade chart;
- R-rule ledger;
- capability matrix;
- economics and EVSI panel;
- evidence passport table;
- data-unlock queue;
- dossier actions;
- four fixed interactive graph views with explicit empty and unavailable states.

The graph component makes no request while collapsed, rejects stale or
public/synthetic-mismatched responses, and uses only the existing fixed graph
API and stored opportunity evidence. The model does not generate executable browser code at runtime. This preserves auditability while allowing the interface to adapt to the decision state and available evidence.

## Repository map

```text
.
├── AGENTS.md                         # Thin domain overlay; reusable Flight Control is external
├── config/                           # Versioned thresholds, profiles, evidence policy and UI catalogue
├── data/
│   ├── snapshots/public/             # Frozen public golden cases
│   ├── synthetic/                    # Explicitly synthetic Ministry-grade scenarios
│   ├── golden/                       # AR/EN extraction fixture
│   └── manifests/                    # Snapshot hashes
├── docs/
│   ├── authority/                    # Original methodology, extracted mirror and hashes
│   ├── core/                         # Ten-document frozen implementation core
│   └── implementation/               # Build overlay, UI/API/runbook and later-binding notes
├── src/ior_mvp/                      # Deterministic engine, API, dossier, GenUI and frontend
├── browser_tests/                    # Bilingual Chromium journeys and governed visual baselines
├── tests/                            # Unit, golden, API, leakage and integrity tests
└── scripts/                          # Run, verify, smoke, manifest and package helpers
```

## Autonomous Cursor workflow

This repository does **not** copy Flight Control or the Universal New-Project Guide. Set their locations if your supervisor needs them:

```bash
export FLIGHT_CONTROL_HOME=~/projects/salim-autonomous-build
export UNIVERSAL_NEW_PROJECT_GUIDE=~/projects/<path>/Universal-New-Project-Guide.md
```

`AGENTS.md`, `.cursor/rules/` and `docs/implementation/BUILD_OVERLAY.md` provide only the project-specific reading list, methodology map and industrial-decision guardrails.

## Deliberate MVP boundary

This POC runs from frozen data and requires no external API key. It demonstrates end-to-end decision logic, evidence governance and interface behavior. Production expansion would add live or scheduled connectors for Saudi customs/tariff lines, GASTAT, Ministry licences and plants, Etimad/SABER, standards, approved-deal records and controlled LLM extraction, all behind the same schemas and gates.

## Bilingual executive journey

With the local application running, open `/executive?opportunity=SAU-H0-721049&step=SIGNAL&locale=en` (or `locale=ar`). Eight steps connect the import signal and false-positive checks to public evidence gaps, an explicitly Class-D scenario, all nine routes, intervention economics and stopping conditions. The public decision remains visible and immutable. Source controls open stored passports and restore keyboard focus on Escape. Missing economics/EVSI remain unavailable rather than zero. The native Analyst link preserves the selected case and locale; graph exploration uses the configured mirror and reports service unavailability honestly.

The executive surface was delivered in [PR39](https://github.com/baramiSG/Industrial_mvp/pull/39); [required main checks](https://github.com/baramiSG/Industrial_mvp/actions/runs/36062918988) passed. Its historical implementation checkpoints remain in [.workflow/slices/S18b-bilingual-executive-surface](.workflow/slices/S18b-bilingual-executive-surface/implementation_log.md). No final milestone release is implied.

## Bilingual Decision Dossier

From Executive Mode, follow **Analyst**, explicitly select **Public** or **Ministry Simulation**, then open the dossier action. The dossier toolbar offers **Print / Save PDF**, **Download JSON** and return to the same case, mode and locale. Chrome/Chromium's native print dialog produces the PDF; there is no server PDF download endpoint. Direct Analyst export remains available.

The summary leads with the decision and immutable public conclusion. The supporting appendix covers identity, demand, named supply, false-positive controls, capability and all nine routes, economics/intervention, competition/policy, rules, evidence/contradictions, stopping conditions and authority. Missing values remain unavailable or NOT_CALCULABLE; genuine zero support remains zero. Simulated output retains Class-D identity and both warning labels. Source passages keep their attribution; the Arabic rule ledger uses governed Arabic prose. The trade chart's visible note explains its independent scales, and **View observed values** opens the actual public observations without implying comparable line heights.

S19 is currently under source, rendered/PDF and exact-candidate verification; these instructions describe its implementation contract, not completed release acceptance. See the [accepted S19 plan](.workflow/slices/S19-bilingual-dossier/accepted-packets/00-s19-S19-IMPLEMENTATION-PLAN.md), [current progress](docs/BUILD_PROGRESS.md) and [limitations](docs/KNOWN_LIMITATIONS.md). Final live Aura verification and model-family release review remain required.
