# S08 — Public Snapshot Schema v2 and Computed Rule Ledger Implementation Plan

> **For the Implementer:** execute this plan test-first, task by task, on `slice/S08-snapshot-v2-computed-rules`. Stay uncommitted for Supervisor and independent review. Do not stage, commit, push, open a PR, merge, tag, install, update locks, or regenerate an unapproved artifact.

**Goal:** Replace author-supplied public rule flags with a validated public snapshot schema `2.0.0` and evidence-derived R-rule ledger, while preserving every existing public and simulated golden outcome and exposing contradictions in the bilingual Decision Dossier. **[SPECIFIED]**

**Architecture:** Keep the aggregate world trade rows unchanged, add optional typed partner/disclosure blocks and explicit unknowns, and validate them before a live snapshot enters the repository cache. Put pure trade arithmetic in a focused module, keep rule orchestration in `rules.py`, project an additive compatibility view for the current metric grid, and retain `public_decision_contract` only until S09. Historical v1 bytes remain hashed but are never loaded by the production repository. **[PROPOSED]**

**Tech stack:** Python 3.12/3.14, standard-library JSON/math/path handling, FastAPI, PyYAML, pytest, ES modules, Playwright 1.62.0/Chromium `1234`, Pillow lossless WebP, and the existing digest-pinned visual container. No dependency or lock change is needed. **[DERIVED]**

**Planner persona:** Senior Deterministic Rules and Data-Contract Engineer for evidence-governed industrial screening, as established in `persona.md` after reading the authority. **[VERIFIED]**

**Data classification:** `confidential_demo`; only the repository's frozen public evidence and existing Class-D synthetic scenarios may be used. **[SPECIFIED]**

---

## 1. Objective

Deliver one reviewable S08 candidate in which:

1. live public snapshots validate as schema `2.0.0`, carry the same `snapshot_id` and `as_of_date` as v1, and point through `supersedes` to byte-identical historical v1 files; **[SPECIFIED]**
2. `rule_context` is impossible in a valid live snapshot and R4-D, R5, R9-S, R10, and R11 are derived from typed evidence; **[SPECIFIED]**
3. R2 uses compound annual growth over the two latest usable observed years, R3 evaluates value and quantity concentration separately, R5 exposes the methodology §3.3 flow formulas, and R1-D reads its confidence cap from configuration; **[SPECIFIED]**
4. steel remains public `INVESTIGATE`, PP remains public `REJECT` route 0, and both simulation outcomes and all frozen numeric results remain unchanged; **[SPECIFIED]**
5. JSON and localized HTML dossiers contain a contradiction register without synthetic leakage; **[SPECIFIED]**
6. the visual-baseline update container writes as the host UID/GID, all functional gates are green before capture, and the 40 canonical baselines are regenerated once for the enumerated rendered-text changes; **[SPECIFIED]**
7. Core 02/04/07/09, ADR-012, manifests, traceability, limitations, development documentation, and the changelog describe exactly what changed and what remains deferred. **[SPECIFIED]**

This slice does not generalize public decision selection. `_public_decision` only replaces its authored R11 guard with the computed R11 row; S09 owns the state selector, real-ADVANCE gate, `MONITOR`, hard exclusions, gap taxonomy, missing-fact derivation, and route hypotheses. **[SPECIFIED]**

## 2. Requirement IDs

### 2.1 Milestone and gap requirements

- `C1`: remove fixture-dependent authored rule behavior for the S08-owned rules. (`GAP_ANALYSIS.md:96-103`) **[SPECIFIED]**
- `C2` partial: any conforming snapshot can execute the public rule ledger without Python edits; decision selection remains S09. (`GAP_ANALYSIS.md:96-103`; `SLICE_GRAPH.md:58-68`) **[SPECIFIED]**
- `D2` / interpretation `I2`: compute R3 HHI and largest share on value and quantity; either basis may fire; unavailable basis is `NOT_CALCULABLE`. (`GAP_ANALYSIS.md:111-116,200-203`) **[SPECIFIED]**
- `D4`: project contradictory evidence into the dossier. (`GAP_ANALYSIS.md:111-117`) **[SPECIFIED]**
- `D7`: implement retained imports, net exposure, apparent consumption, and penetration, while leaving unavailable public inputs unknown. (`GAP_ANALYSIS.md:115-119,160-163`) **[SPECIFIED]**
- `D12` / KL-30: source R1-D confidence cap from `thresholds.rules.R1_D.confidence_cap`. (`GAP_ANALYSIS.md:121-123`; `KNOWN_LIMITATIONS.md:43-51`) **[SPECIFIED]**
- `I3`: R2 quantity growth is CAGR over the observed span. (`GAP_ANALYSIS.md:199-204`) **[SPECIFIED]**
- KL-26 formula/schema portion: close computation and schema; public production/re-export inputs remain unavailable pending S12. (`SLICE_GRAPH.md:283-289`) **[SPECIFIED]**
- KL-32: move closure from S13 to S08 because this slice necessarily regenerates the oracle. (`context.md:10-15`) **[SPECIFIED]**

### 2.2 Core and product requirements

- `FR-010`–`FR-015`: canonical opportunity/evidence, explicit public boundary, and retained contradictions. (`docs/core/01_PRODUCT_AND_REQUIREMENTS.md:157-166`) **[SPECIFIED]**
- `FR-020`–`FR-025`: complete rule rows, deterministic R2, protected R4-D interpretation, R9-S screen, and evidence-warranted R11 rejection. (`docs/core/01_PRODUCT_AND_REQUIREMENTS.md:167-175`) **[SPECIFIED]**
- `INV-08`: unit-value evidence never proves grade. (`REQUIREMENTS_TRACEABILITY.md:88-99`) **[SPECIFIED]**
- `INV-10` / `INV-11`: hashed local goldens only; steel and PP public states remain exact. (`REQUIREMENTS_TRACEABILITY.md:96-100`) **[SPECIFIED]**
- `TL-01`, `TL-02`, `TL-03`, `TL-04`, `TL-08`, `TL-09`: integrity, formulas, rule coverage, goldens, boundaries, and synthetic isolation. (`REQUIREMENTS_TRACEABILITY.md:102-122`) **[SPECIFIED]**
- New v0.3 rows to add: `V3-C2-partial`, `V3-D2`, `V3-D4`, `V3-D7`, `V3-D12`, and `V3-KL32`; each is promoted only to `TESTED` after actual local evidence and never to `COMPLETE` by the Implementer. **[PROPOSED]**

### 2.3 Governing invariants

- Real decisions use public evidence only; synthetic rows remain Class D and affect only simulation. (`AGENTS.md:23-37`; Authority Manifest §6, `00_AUTHORITY_MANIFEST.md:80-93`) **[SPECIFIED]**
- Unknown inputs never become zero or improve permission. (`AGENTS.md:25-31`; `GAP_ANALYSIS.md:225-234`) **[SPECIFIED]**
- Thresholds remain in versioned YAML; PR-02 authorizes only `rules.R4_D.minimum_valid_value_coverage: 0.70` and the associated metadata bump in `config/thresholds.v1.yaml` from `1.1.0` to `1.2.0`. (`AGENTS.md:31-35`; Core 07 §9, `07_DETERMINISTIC_ENGINE_SPEC.md:269-275`; `plan_review.md` PR-02) **[SPECIFIED]**
- Unit-value dispersion is descriptive only. (Methodology mirror §5.2.2, `methodology_extracted.md:530-559`) **[SPECIFIED]**
- No golden expectation, methodology DOCX, sector profile, evidence policy, synthetic scenario, or public-decision selection semantics may change. **[SPECIFIED]**

## 3. Existing-state assessment

The following is the implementation baseline at branch/HEAD `slice/S08-snapshot-v2-computed-rules` / `9f045a4ecf929b82a0c4ad9013d255e148bc837d`. **[VERIFIED]**

| Area | Existing state and evidence | S08 consequence |
|---|---|---|
| Live loader | `data_repository.public_cases` uses non-recursive `glob("*.json")`, checks only opportunity ID and `source_boundary`, and silently accepts v1 (`src/ior_mvp/data_repository.py:29-44`). **[VERIFIED]** | Retain non-recursion; add v2 validation, duplicate rejection, and historical-link checks before caching. |
| R1-D | Confidence metric is literal `"C"` (`rules.py:470-483`). **[VERIFIED]** | Read both metric and rendered effect from configuration. |
| R2 | Selects the last two sorted rows and uses one-period `latest / previous - 1` (`rules.py:487-529`). **[VERIFIED]** | Keep the same pair selection, add observed-span years and CAGR. |
| R3 | Reads authored `supplier_metrics_2024.partner_value_hhi` and only one basis (`rules.py:542-586`). **[VERIFIED]** | Compute from rows when available, otherwise consume source-attributed disclosure; emit two basis records. |
| R4-D/R5 | Both depend on `rule_context`; R5 always reports its ratio `NOT_CALCULABLE` (`rules.py:590-648`). **[VERIFIED]** | Replace flags with typed evidence and calculate each flow measure independently. |
| R9-S/R10/R11 | R9, R10, and R11 depend on three author flags (`rules.py:680-735`). **[VERIFIED]** | Derive from process/signals/gates, R3/designation, and ratio/nameplate respectively. |
| Public selector | `_public_decision` requires both `rule_context.generic_capacity_reject` and R11 (`decision_engine.py:37-65`). **[VERIFIED]** | Read computed `R11.fired` only; leave all returned narratives and branches unchanged. |
| Public response | `analyze_public` exposes old `supplier_metrics_2024` and no schema/flow/criticality fields (`decision_engine.py:68-108`). **[VERIFIED]** | Add schema and evidence blocks; keep a compatibility supplier projection for the metric grid. |
| Reconciliation | `_public_nameplate_total` reads `producer_evidence[].installed_capacity_tpy`; latest trade reads aggregate `trade` (`evidence.py:161-179,269-306`). **[VERIFIED]** | Preserve aggregate trade keys and adapt nameplate handling to exact `UNAVAILABLE`. |
| Dossier | `build_dossier` counts evidence but does not project contradictions; HTML has no contradiction section (`dossier.py:22-89,112-273`). **[VERIFIED]** | Add an additive typed register and escaped/localized HTML section. |
| Catalogue | `validate_ui_strings` hard-codes version `1.0.0` (`config.py:110-130`); no contradiction keys exist (`ui_strings.v1.yaml:201-220,402-420`). **[VERIFIED]** | Bump catalogue to 1.1.0 before the single post-regression authority-generator run. |
| Steel v1 | Contains HHI 0.36, top-two 0.763, bulk band 776–864, Austrian 1.0 kt / 4179, typed-adjacent producer facts, six authored flags, and one contradiction (`SAU-H0-721049.json:59-75,77-131,147-203`). **[VERIFIED]** | Re-express only these facts; do not fabricate partner rows or flows. |
| PP v1 | Contains 50.6× latest export/import ratio, two positive numeric nameplates, authored flags, and no concentration block (`SAU-H0-390210.json:16-43,55-106`). **[VERIFIED]** | R11 must fire from ratio + established nameplate; quantity/value concentration stay unavailable. |
| Manifest generation | `build_manifests.py` recursively hashes `data/snapshots/**/*.json` (`scripts/build_manifests.py:27-39`). **[VERIFIED]** | Historical v1 remains hashed without changing the generator. |
| Visual runner | Docker command has no user mapping; writable bind mounts are baseline and artifact roots (`run_visual_baseline_container.py:21-37,52-100`). **[VERIFIED]** | Add host UID/GID, safe non-root HOME/cache, and post-run ownership validation. |
| Visual matrix | 40 images = 10 screens × 2 locales × 2 viewports; source-tree hash includes Python/static/catalogue (`visual_baselines.py:31-48,131-145,164-191`). **[VERIFIED]** | Any engine/catalogue change makes provenance stale; regenerate all 40 once. |
| Baseline tests | Current default suite is `377 passed, 1 warning`; integrity and smoke pass in this planning session. **[VERIFIED]** | These are baseline observations only, not implementation evidence. |
| Missing requested path | There is no `tests/test_dossier.py`; the relevant files are `tests/test_dossier_contract.py` and `browser_tests/test_dossier.py`. **[VERIFIED]** | Modify those actual files; do not create a duplicate ambiguous test module. |
| Worktree | Pre-existing Supervisor-owned paths are `.gitignore`, `.workflow/state.json`, S07 records, `docs/BUILD_PROGRESS.md`, `docs/KNOWN_LIMITATIONS.md`, and `docs/REQUIREMENTS_TRACEABILITY.md`; two `.workflow/runs/*.sh` files are untracked. **[VERIFIED]** | Do not overwrite unrelated hunks and never stage the helper scripts. |

## 4. Relevant code and contract map

| Responsibility | Existing file(s) | Planned owner |
|---|---|---|
| Public schema and cross-reference validation | No dedicated module; minimal checks in `data_repository.py` | New `src/ior_mvp/public_snapshot.py` |
| Trade formulas, CAGR, partner concentration/dispersion | Interleaved in `rules.py:363-586` | New `src/ior_mvp/trade_metrics.py` |
| R-rule assembly and result text | `src/ior_mvp/rules.py` | Modify; keep orchestration and configured predicates |
| Live snapshot discovery/cache | `src/ior_mvp/data_repository.py` | Modify; production accepts live v2 only |
| Public decision/response | `src/ior_mvp/decision_engine.py` | Modify additively; no S09 selector work |
| Synthetic/public reconciliation | `src/ior_mvp/evidence.py`, `scripts/validate_scenarios.py` | Modify only for validated v2/nameplate compatibility |
| Dossier projection/rendering | `src/ior_mvp/dossier.py` | Modify; bump additive dossier contract |
| UI catalogue validation | `src/ior_mvp/config.py`, `config/ui_strings.v1.yaml` | Modify to 1.1.0 with six exact key pairs |
| Existing browser renderers | `static/modules/renderers/{rules,evidence,decision}.js`, `static/modules/methodology.js` | Intentionally unchanged; existing source-island rendering is sufficient |
| Container ownership | `scripts/run_visual_baseline_container.py`, `browser_tests/visual_container.py` | Modify |
| Baseline oracle | `browser_tests/baselines/v0.3.0/**`, `browser_tests/visual_baselines.py` | Regenerate; no comparator/tolerance/matrix change |
| Authority | Core 02/04/07/09, thresholds 1.2.0, catalogue 1.1.0, Manifest §11, ADR-012 | Complete all governed edits before one recorded generator run |
| Proof | Rule/schema/migration/dossier/API/integrity/browser tests | Extend and add focused modules |

Every new public function listed in §5.8 is added to Core 02 §9's implementation map before review closes. **[SPECIFIED]**

## 5. Architecture

### 5.1 Data flow

```text
live public/*.json
  -> read JSON object
  -> validate schema_version == 2.0.0
  -> validate exact blocks, source references, and supersedes path
  -> cache by opportunity.id
  -> pure trade_metrics calculations
  -> rules.evaluate_rules
  -> computed R11 -> existing public selector
  -> additive analysis response
  -> dossier contradiction projection / existing GenUI

historical/v1/*.json
  -> manifest hashing only
  -> direct test-only legacy adapter only
  -> never production discovery
```

This ordering fails closed before malformed evidence can influence a decision or enter the process-local cache. **[DERIVED]**

### 5.2 Schema boundary

`public_snapshot.py` owns:

- `PUBLIC_SNAPSHOT_SCHEMA_VERSION = "2.0.0"`;
- exact allowed/required top-level keys;
- exact `UNAVAILABLE` sentinel handling;
- scalar/list/object validators that reject booleans as numbers and reject NaN/infinity;
- evidence-ID referential integrity;
- partner validity/unit/flow constraints;
- disclosed metric domains;
- producer evidence and hard-gate state validation;
- evidence-passport completeness;
- safe `supersedes` resolution under `data/snapshots/public/historical/v1/`;
- same `snapshot_id`, `as_of_date`, and `opportunity.id` between v2 and referenced v1;
- normalization of typed hard-gate objects back to a list of unresolved names for the unchanged capability engine.

Unknown top-level keys are rejected. This allow-list, plus exact nested allow-lists, prevents an author from hiding `fired`, `execution`, `rule_result`, `rule_outcomes`, `rule_context`, or an equivalent public-rule payload in a valid live snapshot. `public_decision_contract` remains the single explicit temporary decision contract because S09, not S08, removes it. **[PROPOSED]**

### 5.3 Loader and history

The live repository continues to use `Path.glob("*.json")`; it never recurses into `historical/`. A live object without schema version `2.0.0`, including a copied v1 historical object, raises `EvidenceIntegrityError`. Duplicate opportunity IDs raise the same typed error rather than last-file-wins replacement. **[PROPOSED]**

The two v1 files are moved byte-for-byte to:

```text
data/snapshots/public/historical/v1/SAU-H0-721049.json
data/snapshots/public/historical/v1/SAU-H0-390210.json
```

The two v2 files keep their original live paths, snapshot IDs, and dates. This implements SD-1's representation-migration policy and does not assert an evidence refresh. **[SPECIFIED]**

### 5.4 Rule computation

`trade_metrics.py` is pure and has no repository/config access. `rules.py` supplies threshold mappings and converts metric results into the existing `_rule` contract. This separation keeps mathematical tests independent from rendered rule text and lets the threshold scanner inspect both modules recursively. **[PROPOSED]**

For every aggregate trade row, the metric layer computes `export_import_value_ratio = exports_usd_m / imports_usd_m` when both operands are finite, present, and strictly positive. A row's disclosed ratio remains source evidence rather than the computational input. When both values exist, validation requires `abs(disclosed_ratio - computed_ratio) <= 0.05`, the half-unit tolerance for a figure disclosed to one decimal place; the response reports both values and the consistency result. **[SPECIFIED]**

### 5.5 Supplier compatibility projection

`build_supplier_metrics(case, r3_metrics, r4d_metrics)` returns the existing flat keys used by `decision.js`:

```json
{
  "partner_value_hhi": 0.36,
  "largest_supplier_share": "NOT_CALCULABLE",
  "top_two_value_share": 0.763,
  "partner_quantity_hhi": "NOT_CALCULABLE",
  "largest_supplier_quantity_share": "NOT_CALCULABLE",
  "bulk_uv_range_usd_t": [776, 864],
  "small_high_uv_observation": {
    "partner": "Austria",
    "quantity_kt": 1.0,
    "uv_usd_t": 4179
  }
}
```

For PP, it remains `null` because no supplier concentration disclosure exists. The metric-grid lookup therefore continues to render steel HHI `0.36` and PP unavailable without renderer changes. New nested R3 metrics remain available to API consumers. **[DERIVED]**

### 5.6 Dossier contradiction register

`build_dossier` filters non-empty `evidence[].contradiction` values into:

```json
{
  "public": [
    {
      "evidence_id": "S-UNICOIL-SPEC",
      "source": "UNICOIL",
      "contradiction": "Published coating range differs from EPD and is retained for confirmation.",
      "synthetic_flag": false
    }
  ],
  "synthetic": [],
  "synthetic_status": "NOT_APPLICABLE"
}
```

In simulated mode the same public row remains, synthetic rows are separately filtered, and `synthetic_status` is `NONE_RECORDED` when no synthetic contradiction exists or `PRESENT` when at least one exists. Public mode always uses `NOT_APPLICABLE` and never scans or renders an inactive synthetic scenario. HTML escapes every field, treats evidence IDs as technical LTR tokens, renders source and contradiction as governed English source-language islands, and uses catalogue-owned chrome/status text. **[PROPOSED]**

### 5.7 KL-32 ownership fix

The host runner obtains `os.getuid()` / `os.getgid()`, adds `--user <uid>:<gid>`, and passes:

```text
HOME=/tmp
XDG_CACHE_HOME=/tmp/.cache
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
IOR_HOST_UID=<uid>
IOR_HOST_GID=<gid>
```

`visual_container.py` asserts its effective UID/GID match the supplied host values before running pytest. `/ms-playwright` stays read-only and executable from the pinned image; temporary home/cache paths are writable by the arbitrary user. After a successful update, the host runner recursively checks the two writable mount roots with `os.stat(..., follow_symlinks=False).st_uid == os.getuid()` and exits 2 with the first relative offending path if ownership is wrong. Compare mode does not require the ownership sweep. **[PROPOSED]**

The no-network and exact mount allow-list remain unchanged, so `.env` is neither read nor mounted. **[VERIFIED]**

### 5.8 New/changed interfaces

The exact proposed public Python interfaces are:

```python
# public_snapshot.py
class PublicSnapshotIntegrityError(EvidenceIntegrityError): ...

def validate_public_snapshot(
    record: dict[str, Any],
    *,
    path: Path | None = None,
    root: Path = PROJECT_ROOT,
) -> None: ...

def capability_hard_gate_names(
    capability: dict[str, Any],
) -> list[str]: ...

def has_known_hard_gate_failure(
    capability: dict[str, Any],
) -> bool: ...

# trade_metrics.py
def compound_annual_growth(
    latest: float,
    previous: float,
    years: int,
) -> float: ...

def latest_usable_trade_pair(
    trade: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]] | None: ...

def export_import_value_ratio(
    trade_row: dict[str, Any],
) -> dict[str, Any]: ...

def concentration_metrics(
    case: dict[str, Any],
    basis: Literal["value", "quantity"],
) -> dict[str, Any]: ...

def degraded_dispersion_metrics(
    case: dict[str, Any],
    minimum_valid_value_coverage: float,
) -> dict[str, Any]: ...

def domestic_flow_metrics(
    latest_trade: dict[str, Any],
    domestic_flows: dict[str, Any],
) -> dict[str, Any]: ...

def established_domestic_nameplate(
    capability: dict[str, Any],
) -> dict[str, Any]: ...

def build_supplier_metrics(
    case: dict[str, Any],
    r3_metrics: dict[str, Any],
    r4d_metrics: dict[str, Any],
) -> dict[str, Any] | None: ...
```

All public functions have type hints; none mutates its input. **[PROPOSED]**

### 5.9 Governed generation boundary

Core 02/04/07/09, thresholds 1.2.0, catalogue 1.1.0, historical moves, live v2 files, ADR/docs, and all implementation/tests are completed before a full regression. Only after that regression is green does the Supervisor-controlled path run `scripts/build_manifests.py` once and audit the exact §18.6 diff. A later second run is exceptional recovery for a separately justified and recorded governed fix, not part of the planned sequence. **[SPECIFIED]**

## 6. File plan

### 6.1 Create

- `src/ior_mvp/public_snapshot.py` — schema v2 and historical-link validator.
- `src/ior_mvp/trade_metrics.py` — CAGR, concentration, dispersion, flows, nameplate, and compatibility projection.
- `tests/legacy_snapshot_v1.py` — imported test-only characterization adapter for v1; never imported by production.
- `tests/test_public_snapshot_schema.py` — schema, loader, non-recursion, forbidden key, path, and passport tests.
- `tests/test_trade_metrics.py` — pure formula/unknown/failure tests.
- `tests/test_snapshot_migration_equivalence.py` — historical-v1 versus live-v2 anti-drift proof.
- `data/snapshots/public/SAU-H0-721049.json` — new v2 representation at the existing live path.
- `data/snapshots/public/SAU-H0-390210.json` — new v2 representation at the existing live path.

### 6.2 Move byte-identically

- `data/snapshots/public/SAU-H0-721049.json` v1 bytes → `data/snapshots/public/historical/v1/SAU-H0-721049.json`.
- `data/snapshots/public/SAU-H0-390210.json` v1 bytes → `data/snapshots/public/historical/v1/SAU-H0-390210.json`.

Verify each moved file's SHA-256 and byte count remain `10efb192… / 6,850` and `cc28e77d… / 5,572` respectively before any manifest generation. **[VERIFIED]**

### 6.3 Modify production

- `src/ior_mvp/data_repository.py`
- `src/ior_mvp/rules.py`
- `src/ior_mvp/decision_engine.py`
- `src/ior_mvp/evidence.py`
- `src/ior_mvp/dossier.py`
- `src/ior_mvp/config.py`
- `scripts/validate_scenarios.py`
- `scripts/run_visual_baseline_container.py`
- `browser_tests/visual_container.py`

### 6.4 Modify tests

- `tests/test_rules.py`
- `tests/test_threshold_boundaries.py`
- `tests/test_scenario_validation.py`
- `tests/test_simulation_fidelity.py`
- `tests/test_synthetic_isolation.py`
- `tests/test_dossier_contract.py`
- `tests/test_api.py`
- `tests/test_integrity_contract.py`
- `tests/test_authority_disclosure.py`
- `tests/test_threshold_literals.py`
- `tests/test_ui_catalogue.py`
- `tests/test_visual_baseline_contract.py`
- `browser_tests/test_journeys.py`
- `browser_tests/test_dossier.py`

### 6.5 Modify governed artifacts and docs

- `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`
- `docs/core/04_CANONICAL_DATA_MODEL.md`
- `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`
- `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`
- `config/ui_strings.v1.yaml` (`1.0.0` → `1.1.0`; exact contradiction keys only)
- `config/thresholds.v1.yaml` (`1.1.0` → `1.2.0`; exact R4-D coverage key and metadata only)
- `docs/ARCHITECTURE_DECISIONS.md` (ADR-012)
- `docs/authority/authority_hashes.json` (generated once under §18 after all governed edits and full regression)
- `data/manifests/snapshot_manifest.json` (generated under §18)
- `docs/authority/00_AUTHORITY_MANIFEST.md` §11 (machine-manifest values copied exactly)
- `docs/DEVELOPMENT_GUIDE.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/BUILD_PROGRESS.md` (S08 local candidate evidence only; preserve Supervisor-owned S07 hunks)
- `CHANGELOG.md`
- `browser_tests/baselines/v0.3.0/manifest.json`
- `browser_tests/baselines/v0.3.0/manifest.sha256`
- all 40 `browser_tests/baselines/v0.3.0/{en,ar}/{desktop-1440x900,tablet-1024x768}/*.webp`

### 6.6 Explicitly unchanged

- methodology DOCX and extracted mirror;
- Core 01, 03, 05, 06, and 08;
- `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml`, and `project.yaml`;
- all `data/synthetic/*.json` and `data/golden/*.json`;
- `scripts/build_manifests.py`, `scripts/verify_integrity.py`, and `scripts/check_threshold_literals.py`;
- `src/ior_mvp/capability.py`, `genui.py`, and `app.py`;
- `src/ior_mvp/static/modules/renderers/{rules,evidence,decision}.js` and `static/modules/methodology.js`;
- visual Dockerfile, comparator, tolerance, image digest, viewports, screen set, and browser dependency pins;
- milestone baseline documents and S07 completion records except Supervisor-owned pre-existing changes;
- `.env`, `.workflow/runs/*.sh`, locks, dependency metadata, Docker/runtime configuration, and any non-primary worktree.

If implementation proves any explicitly unchanged file is necessary, stop and return the exact requirement and proposed diff to the Supervisor; do not broaden silently. **[SPECIFIED]**

## 7. Exact schema v2 golden JSON and validator rules

### 7.1 Steel — exact live `data/snapshots/public/SAU-H0-721049.json`

```json
{
  "schema_version": "2.0.0",
  "snapshot_id": "PUBLIC-SAU-H0-721049-2026-08-31",
  "as_of_date": "2026-08-31",
  "supersedes": "data/snapshots/public/historical/v1/SAU-H0-721049.json",
  "source_boundary": "public",
  "authority_note": "Frozen from the public worked case in the Industrial Opportunity Resolution Methodology. Gross WITS/UN Comtrade flows; not retained domestic demand.",
  "opportunity": {
    "id": "SAU-H0-721049",
    "hs_revision": "H0",
    "hs6": "721049",
    "national_tariff_line": "UNAVAILABLE",
    "sector_profile": "coated_steel",
    "commercial_name_en": "Non-corrugated zinc-coated flat-rolled iron or non-alloy steel, width 600 mm or more",
    "commercial_name_ar": "منتجات مسطحة مدرفلة من حديد أو صلب غير مخلوط، مطلية بالزنك، بعرض 600 مم أو أكثر، غير مموجة",
    "decision_object_status": "partially_resolved",
    "application_boundary": "Multiple applications; target customer/application remains unresolved in public evidence.",
    "as_of_date": "2026-08-31"
  },
  "trade": [
    {
      "year": 2021,
      "imports_usd_m": 194.1,
      "imports_kt": 177.4,
      "import_uv_usd_t": 1094.0,
      "exports_usd_m": 49.6,
      "exports_kt": 39.7,
      "gross_net_usd_m": 144.5,
      "gross_net_kt": 137.8
    },
    {
      "year": 2023,
      "imports_usd_m": 186.0,
      "imports_kt": 173.8,
      "import_uv_usd_t": 1070.0,
      "exports_usd_m": 16.3,
      "exports_kt": 15.8,
      "gross_net_usd_m": 169.7,
      "gross_net_kt": 158.0
    },
    {
      "year": 2024,
      "imports_usd_m": 236.9,
      "imports_kt": 287.9,
      "import_uv_usd_t": 823.0,
      "exports_usd_m": 27.1,
      "exports_kt": 27.6,
      "gross_net_usd_m": 209.8,
      "gross_net_kt": 260.3
    }
  ],
  "trade_quality": {
    "flow_basis": "gross",
    "reexports_separated": false,
    "domestic_origin_exports_separated": false,
    "missing_years": [2022],
    "monthly_partner_tariff_line_available": false,
    "quantity_comparable": true,
    "execution_cap": "DEGRADED where continuity or tariff-line detail is required"
  },
  "partner_observations": "UNAVAILABLE",
  "disclosed_concentration": {
    "value": {
      "year": 2024,
      "flow": "imports",
      "flow_basis": "gross",
      "basis": "value",
      "hhi": 0.36,
      "largest_supplier_share": "UNAVAILABLE",
      "top_two_share": 0.763,
      "top_two_suppliers": ["China", "Korea, Rep."],
      "source_evidence_id": "S-WITS-721049",
      "status": "calculated"
    },
    "quantity": "UNAVAILABLE"
  },
  "disclosed_dispersion": {
    "year": 2024,
    "basis": "annual_partner",
    "flow_basis": "gross",
    "unit": "USD/t",
    "valid_value_coverage": "UNAVAILABLE",
    "valid_quantity_coverage": "UNAVAILABLE",
    "weighted_median_usd_t": "UNAVAILABLE",
    "iqr_usd_t": "UNAVAILABLE",
    "bulk_band_usd_t": [776, 864],
    "outlier_observation": {
      "partner": "Austria",
      "net_weight_kt": 1.0,
      "unit_value_usd_t": 4179
    },
    "comparison_observations": "UNAVAILABLE",
    "coverage_note": "Annual partner data permit only the degraded R4-D path; complete row-level value and comparable-quantity coverage are not present in the frozen fixture.",
    "source_evidence_id": "S-WITS-721049",
    "status": "calculated"
  },
  "domestic_flows": {
    "period_year": 2024,
    "domestic_production_kt": "UNAVAILABLE",
    "retained_imports_kt": "UNAVAILABLE",
    "domestic_origin_exports_kt": "UNAVAILABLE",
    "reexports_kt": "UNAVAILABLE",
    "source_evidence_ids": []
  },
  "criticality_designation": "UNAVAILABLE",
  "domestic_capability": {
    "verified_present": true,
    "same_process_family": true,
    "coarse_adjacency_signals": [
      {
        "signal_type": "core_process",
        "description": "continuous hot-dip galvanising",
        "evidence_ids": ["S-UNICOIL-EPD"]
      },
      {
        "signal_type": "core_process",
        "description": "cold rolling and pickling",
        "evidence_ids": ["S-UNICOIL-EPD"]
      },
      {
        "signal_type": "adjacent_output",
        "description": "published ASTM/SASO grades",
        "evidence_ids": ["S-UNICOIL-EPD", "S-UNICOIL-SPEC"]
      },
      {
        "signal_type": "relevant_certification",
        "description": "ISO/IEC 17025 laboratory",
        "evidence_ids": ["S-UNICOIL-EPD"]
      }
    ],
    "producer_evidence": [
      {
        "producer": "UNICOIL",
        "process_family": "coated_steel",
        "process_route": "continuous hot-dip galvanising",
        "published_standards": ["SASO-ASTM A653/A653M"],
        "published_coating_range_g_m2": [45, 350],
        "installed_capacity_tpy": 250000,
        "nameplate_status": "observed",
        "nameplate_source_evidence_id": "S-UNICOIL-EPD",
        "evidence_class": "C",
        "evidence_ids": ["S-UNICOIL-EPD", "S-UNICOIL-SPEC"]
      },
      {
        "producer": "Hadeed",
        "process_family": "coated_steel",
        "process_route": "cold-rolled galvanised and colour-coated coil publicly listed",
        "published_standards": "UNAVAILABLE",
        "published_coating_range_g_m2": "UNAVAILABLE",
        "installed_capacity_tpy": "UNAVAILABLE",
        "nameplate_status": "unresolved",
        "nameplate_source_evidence_id": "UNAVAILABLE",
        "evidence_class": "C",
        "evidence_ids": ["S-HADEED"]
      }
    ],
    "public_dimension_states": {
      "feedstock_chemistry": 0,
      "core_process_route": 0,
      "equipment_envelope": 1,
      "finishing_spec_control": 1,
      "qa_lab_metrology": 0,
      "certification_customer_qualification": "U",
      "capacity_time_window": "U",
      "utilities_ehs_permitting": "U",
      "skills_market_integration": 1
    },
    "unresolved_hard_gates": [
      {"name": "exact imported specification", "state": "unresolved"},
      {"name": "customer/application qualification", "state": "unresolved"},
      {"name": "effective spare capacity and allocation", "state": "unresolved"}
    ]
  },
  "public_decision_contract": {
    "expected_state": "INVESTIGATE",
    "route_restriction": "Test brownfield first; greenfield is not justified from public evidence.",
    "missing_facts": [
      "Line-level production by grade, coating mass, dimensions, application and destination",
      "Availability, yield, qualification share, utilisation, backlog and planned outages",
      "Importer/offtaker specifications and reason local supply was not selected",
      "Re-export and domestic-origin flow decomposition",
      "Delivered local cost, import parity and unsupported brownfield economics"
    ],
    "kill_conditions": [
      "Demand is temporary, re-exported or below efficient scale",
      "Incumbent expansion already closes the specification-adjusted gap"
    ]
  },
  "evidence": [
    {
      "evidence_id": "S-WITS-721049",
      "title": "WITS/UN Comtrade Saudi trade rows for HS 721049",
      "source": "WITS/UN Comtrade",
      "url": "https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Imports/partner/ALL/product/721049",
      "period": "2021/2023/2024",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "B",
      "synthetic_flag": false,
      "supports": ["trade value", "trade quantity", "partner concentration"],
      "transformation": "Frozen annual world rows; concentration and dispersion are disclosed aggregates from the methodology worked case.",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    },
    {
      "evidence_id": "S-UNICOIL-EPD",
      "title": "UNICOIL 2024 Environmental Product Declaration",
      "source": "UNICOIL",
      "url": "https://www.unicoil.com.sa/wp-content/uploads/2026/05/EPD-Report_GS_Unicoil_Rev02-1_1.pdf",
      "period": "2023/2024",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["installed capacity", "process route", "published specification envelope", "laboratory accreditation"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    },
    {
      "evidence_id": "S-UNICOIL-SPEC",
      "title": "UNICOIL Arabic and English galvanized product specifications",
      "source": "UNICOIL",
      "url": "https://www.unicoil.com.sa/products%26services/gi-product-brands-specifications-2/",
      "period": "UNAVAILABLE",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["bilingual specification extraction", "published coating and dimension envelope"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": "Published coating range differs from EPD and is retained for confirmation."
    },
    {
      "evidence_id": "S-HADEED",
      "title": "Hadeed flat-products catalogue",
      "source": "Hadeed",
      "url": "https://hadeed.com.sa/products?group-category=cold-rolled-galvanized&main-category=flat-products",
      "period": "UNAVAILABLE",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["additional incumbent process-family evidence"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    }
  ]
}
```

Steel numeric provenance:

- `trade[*]`, missing 2022, and gross-net figures: methodology §13.1 (`methodology_extracted.md:1278-1355`) and byte-identical v1 (`SAU-H0-721049.json:16-57`). **[SPECIFIED]**
- HHI `0.36`, top-two `0.763`, band `776–864`, Austria `1.0 kt / 4179`: methodology §13.2–§13.3 (`methodology_extracted.md:1373-1398`) and v1 (`SAU-H0-721049.json:59-75`). **[SPECIFIED]**
- `250000 tpy`, coating range `45–350`, and public dimension states `0/1/U`: frozen v1 (`SAU-H0-721049.json:77-121`); the EPD source basis is Appendix D S-U2 (`methodology_extracted.md:1819-1825`). **[SPECIFIED]**
- Evidence period `2023/2024` is the Core 04 passport example (`04_CANONICAL_DATA_MODEL.md:127-146`); all `retrieved_at` dates use Appendix D's stated 31 August 2026 recheck date (`methodology_extracted.md:1807-1813`). **[SPECIFIED]**
- Schema/date/supersedes numbers and unchanged snapshot identity implement SD-1 (`context.md:9-12`); no empirical value is introduced. **[SPECIFIED]**

### 7.2 Polypropylene — exact live `data/snapshots/public/SAU-H0-390210.json`

```json
{
  "schema_version": "2.0.0",
  "snapshot_id": "PUBLIC-SAU-H0-390210-2026-08-31",
  "as_of_date": "2026-08-31",
  "supersedes": "data/snapshots/public/historical/v1/SAU-H0-390210.json",
  "source_boundary": "public",
  "authority_note": "Frozen from the public worked case in the Industrial Opportunity Resolution Methodology. Gross WITS/UN Comtrade flows; not retained domestic demand.",
  "opportunity": {
    "id": "SAU-H0-390210",
    "hs_revision": "H0",
    "hs6": "390210",
    "national_tariff_line": "UNAVAILABLE",
    "sector_profile": "technical_plastics",
    "commercial_name_en": "Polypropylene, in primary forms",
    "commercial_name_ar": "بولي بروبيلين بأشكاله الأولية",
    "decision_object_status": "generic_hs6_only",
    "application_boundary": "Generic capacity case; narrow grade/application exceptions remain unresolved.",
    "as_of_date": "2026-08-31"
  },
  "trade": [
    {
      "year": 2021,
      "imports_usd_m": 91.2,
      "imports_kt": 50.5,
      "exports_usd_m": 6827.8,
      "exports_kt": null,
      "export_import_value_ratio": 74.9
    },
    {
      "year": 2023,
      "imports_usd_m": 91.0,
      "imports_kt": 67.0,
      "exports_usd_m": 4806.3,
      "exports_kt": 3666.6,
      "export_import_value_ratio": 52.8
    },
    {
      "year": 2024,
      "imports_usd_m": 92.3,
      "imports_kt": 56.0,
      "exports_usd_m": 4670.5,
      "exports_kt": 4257.9,
      "export_import_value_ratio": 50.6,
      "import_uv_usd_t": 1649.0,
      "export_uv_usd_t": 1097.0
    }
  ],
  "trade_quality": {
    "flow_basis": "gross",
    "reexports_separated": false,
    "domestic_origin_exports_separated": false,
    "missing_years": [2022],
    "monthly_partner_tariff_line_available": false,
    "quantity_comparable": true,
    "execution_cap": "DEGRADED where continuity or grade resolution is required"
  },
  "partner_observations": "UNAVAILABLE",
  "disclosed_concentration": {
    "value": "UNAVAILABLE",
    "quantity": "UNAVAILABLE"
  },
  "disclosed_dispersion": {
    "year": 2024,
    "basis": "annual_gross_flow_average",
    "flow_basis": "gross",
    "unit": "USD/t",
    "valid_value_coverage": "UNAVAILABLE",
    "valid_quantity_coverage": "UNAVAILABLE",
    "weighted_median_usd_t": "UNAVAILABLE",
    "iqr_usd_t": "UNAVAILABLE",
    "bulk_band_usd_t": "UNAVAILABLE",
    "outlier_observation": "UNAVAILABLE",
    "comparison_observations": [
      {"flow": "imports", "unit_value_usd_t": 1649},
      {"flow": "exports", "unit_value_usd_t": 1097}
    ],
    "coverage_note": "Gross-flow average unit values are a product-mix, grade, origin, or distribution research signal; they do not establish a specialty-grade gap.",
    "source_evidence_id": "P-WITS-390210",
    "status": "calculated"
  },
  "domestic_flows": {
    "period_year": 2024,
    "domestic_production_kt": "UNAVAILABLE",
    "retained_imports_kt": "UNAVAILABLE",
    "domestic_origin_exports_kt": "UNAVAILABLE",
    "reexports_kt": "UNAVAILABLE",
    "source_evidence_ids": []
  },
  "criticality_designation": "UNAVAILABLE",
  "domestic_capability": {
    "verified_present": true,
    "same_process_family": true,
    "coarse_adjacency_signals": [
      {
        "signal_type": "core_process",
        "description": "large established Saudi polypropylene production",
        "evidence_ids": ["P-ADVANCED", "P-TASNEE"]
      },
      {
        "signal_type": "adjacent_output",
        "description": "broad producer grade portfolios",
        "evidence_ids": ["P-SABIC"]
      }
    ],
    "producer_evidence": [
      {
        "producer": "SABIC",
        "process_family": "polypropylene",
        "process_route": "UNAVAILABLE",
        "published_standards": "UNAVAILABLE",
        "portfolio": "homo, random and impact products and compounds",
        "installed_capacity_tpy": "UNAVAILABLE",
        "nameplate_status": "unresolved",
        "nameplate_source_evidence_id": "UNAVAILABLE",
        "evidence_class": "C",
        "evidence_ids": ["P-SABIC"]
      },
      {
        "producer": "Advanced Petrochemical",
        "process_family": "polypropylene",
        "process_route": "UNAVAILABLE",
        "published_standards": "UNAVAILABLE",
        "public_note": "Jubail complex exceeded nameplate in Q1 2026",
        "installed_capacity_tpy": 450000,
        "nameplate_status": "observed",
        "nameplate_source_evidence_id": "P-ADVANCED",
        "evidence_class": "C",
        "evidence_ids": ["P-ADVANCED"]
      },
      {
        "producer": "Tasnee",
        "process_family": "polypropylene",
        "process_route": "UNAVAILABLE",
        "published_standards": "UNAVAILABLE",
        "installed_capacity_tpy": 720000,
        "nameplate_status": "observed",
        "nameplate_source_evidence_id": "P-TASNEE",
        "evidence_class": "C",
        "evidence_ids": ["P-TASNEE"]
      }
    ],
    "public_dimension_states": {
      "feedstock_chemistry": 0,
      "core_process_route": 0,
      "equipment_envelope": 0,
      "finishing_spec_control": "U",
      "qa_lab_metrology": "U",
      "certification_customer_qualification": "U",
      "capacity_time_window": "U",
      "utilities_ehs_permitting": 0,
      "skills_market_integration": 0
    },
    "unresolved_hard_gates": [
      {"name": "named imported grade", "state": "unresolved"},
      {"name": "buyer application and qualification", "state": "unresolved"},
      {"name": "local grade availability in required volume and timing", "state": "unresolved"}
    ]
  },
  "public_decision_contract": {
    "expected_state": "REJECT",
    "route_restriction": "Reject generic polypropylene capacity support; investigate only explicitly defined grade/application exceptions.",
    "missing_facts": [
      "Saudi tariff-line and invoice description",
      "Importer/offtaker application and qualification",
      "Producer grade and local-availability matrix",
      "Plant allocation and utilisation",
      "Delivered economics for a named niche"
    ],
    "kill_conditions": [
      "Imported and domestic products are shown equivalent and qualified",
      "No specification-adjusted gap exists"
    ]
  },
  "evidence": [
    {
      "evidence_id": "P-WITS-390210",
      "title": "WITS/UN Comtrade Saudi trade rows for HS 390210",
      "source": "WITS/UN Comtrade",
      "url": "https://wits.worldbank.org/trade/comtrade/en/country/SAU/year/2024/tradeflow/Imports/partner/ALL/product/390210",
      "period": "2021/2023/2024",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "B",
      "synthetic_flag": false,
      "supports": ["trade value", "trade quantity", "export/import ratio"],
      "transformation": "Frozen annual world rows; export/import ratios and 2024 average unit values are disclosed calculations from the methodology worked case.",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    },
    {
      "evidence_id": "P-SABIC",
      "title": "SABIC polypropylene portfolio",
      "source": "SABIC",
      "url": "https://www.sabic.com/en/products/polymers/polypropylene-pp",
      "period": "UNAVAILABLE",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["broad domestic-linked polypropylene family portfolio"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    },
    {
      "evidence_id": "P-ADVANCED",
      "title": "Advanced Petrochemical company information",
      "source": "Advanced Petrochemical",
      "url": "https://advancedpetrochem.com/about/",
      "period": "UNAVAILABLE",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["450,000 t/y nameplate capacity"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    },
    {
      "evidence_id": "P-TASNEE",
      "title": "Tasnee petrochemicals page",
      "source": "Tasnee",
      "url": "https://www.tasnee.com/en/products/petrochemicals",
      "period": "UNAVAILABLE",
      "retrieved_at": "2026-08-31",
      "status": "observed",
      "evidence_class": "C",
      "synthetic_flag": false,
      "supports": ["720,000 t/y Saudi polypropylene capacity"],
      "transformation": "UNAVAILABLE",
      "reviewer_status": "unconfirmed_by_responsible_authority",
      "contradiction": null
    }
  ]
}
```

PP numeric provenance:

- 2021/2023/2024 trade, ratios `74.9/52.8/50.6`, and missing 2022: methodology §14.1 (`methodology_extracted.md:1532-1545`) and v1 (`SAU-H0-390210.json:16-53`). **[SPECIFIED]**
- 2024 unit values `1649/1097`: methodology §14.2 (`methodology_extracted.md:1546-1560`) and v1 (`SAU-H0-390210.json:33-43`). **[SPECIFIED]**
- Nameplates `450000/720000`, public note Q1 2026, and public dimension states: frozen v1 (`SAU-H0-390210.json:55-97`); Appendix D P-A1/P-A2/P-T1 lists the producer basis (`methodology_extracted.md:1823-1829`). **[SPECIFIED]**
- Retrieval, schema, date, and history values follow the same cited Appendix D and SD-1 policy as steel. **[SPECIFIED]**

### 7.3 Validator rules

1. Top-level required keys are `schema_version`, `snapshot_id`, `as_of_date`, `supersedes`, `source_boundary`, `authority_note`, `opportunity`, `trade`, `trade_quality`, `domestic_flows`, `criticality_designation`, `domestic_capability`, `public_decision_contract`, and `evidence`. Optional keys are exactly `partner_observations`, `disclosed_concentration`, and `disclosed_dispersion`. Any other top-level key fails. **[PROPOSED]**
2. `schema_version` is exactly `"2.0.0"` and `source_boundary` exactly `"public"`. **[SPECIFIED]**
3. `rule_context`, any top-level/nested rule-ledger structure, and nested keys `fired`, `execution`, `decision_effect`, or `rule_id` are forbidden by the allow-lists. **[SPECIFIED]**
4. `snapshot_id`, `as_of_date`, opportunity ID, and opportunity as-of date are non-empty; dates parse as ISO dates and the two as-of values match. **[PROPOSED]**
5. `supersedes` is a relative POSIX path under the exact historical-v1 directory, has no `..`, resolves inside the project root, exists, and contains the same identity/date/opportunity. **[PROPOSED]**
6. Aggregate `trade` stays backward-compatible: years are unique integers; known numeric cells are finite non-boolean numbers or the existing `null` where v1 already used it; units remain encoded in key names. `export_import_value_ratio` on a row is a disclosed one-decimal figure, never the computational source. Whenever imports and exports are both present, finite, and positive, validation computes `exports_usd_m / imports_usd_m`; if a disclosed ratio also exists, `abs(disclosed - computed) <= 0.05` is required. The latest usable R2/R11 row is not otherwise a validator concern. Steel has no disclosed ratios but computes 2024 `27.1 / 236.9 = 0.1144`; PP reports computed `4670.5 / 92.3 = 50.6013` and disclosed `50.6`, with consistency true. **[SPECIFIED]**
7. `partner_observations` is absent, `"UNAVAILABLE"`, or a non-empty list. Each row requires `year`, `partner`, `flow`, `trade_value_usd_m`, `net_weight_kt`, `quantity_unit`, `validity_flags`, `gross_flow`, and `source_evidence_id`. Flow is `imports|exports`; quantity unit is `kt|UNAVAILABLE`; flags are exact booleans `value_valid`, `net_weight_valid`, and `quantity_comparable`; a `true` flag requires a finite non-negative corresponding value and a false flag forbids that value from entering a calculation. **[PROPOSED]**
8. `disclosed_concentration` has exact `value` and `quantity` keys, each `"UNAVAILABLE"` or the typed object shown above. HHI/shares are in `[0,1]`; basis matches its key; `flow_basis` is `gross|retained`; status is `calculated`; source ID resolves. Top-two share is never substituted for largest share. **[SPECIFIED]**
9. `disclosed_dispersion` is `"UNAVAILABLE"` or the exact object shape shown. Every supplied unit value is positive and finite; band low ≤ high; an outlier must fall outside the supplied band; `flow_basis` is explicit; status is `calculated`; source ID resolves. Its presence represents a source-attributed disclosed diagnostic, not an authored rule outcome. **[PROPOSED]**
10. `domestic_flows` carries the exact four methodology quantities, each finite non-negative or `"UNAVAILABLE"`, a period year, and evidence IDs. If both re-exports and direct retained imports are numeric, direct retained imports must equal gross imports minus re-exports within calculation tolerance; re-exports cannot exceed gross imports. **[PROPOSED]**
11. `criticality_designation` is exactly `"UNAVAILABLE"` or `{authority, reference, date, evidence_id}` with non-empty strings, an ISO date, and a resolvable evidence ID. **[SPECIFIED]**
12. `coarse_adjacency_signals[].signal_type` is one of `matching_feedstock`, `core_process`, `equipment`, `adjacent_output`, `relevant_certification`, `imported_inputs`; each description is non-empty and every evidence ID resolves. **[SPECIFIED]**
13. Producer records require producer, process family, process route/unknown, standards/unknown, capacity/unknown, nameplate status, nameplate source, evidence class, and evidence IDs. A numeric positive nameplate requires status `observed`, a Class A/B/C passport, and a matching source ID. `"UNAVAILABLE"` requires `unresolved` and no source. Product-specific carried fields are allow-listed and typed. **[PROPOSED]**
14. `unresolved_hard_gates` contains `{name, state}` records; state is `unresolved|known_failure`. Both block D* publication; only `known_failure` suppresses the coarse R9-S screen. **[PROPOSED]**
15. Every public evidence passport sets `synthetic_flag=false`, has unique evidence ID, source, status, class, supports, period, retrieved_at, transformation, reviewer status, and contradiction (`null` or non-empty string). **[SPECIFIED]**
16. No validator repairs, defaults, interpolates, or coerces an invalid value. The exact uppercase sentinel is the only typed unknown in new blocks. **[SPECIFIED]**

The only threshold change is:

```yaml
metadata:
  version: "1.2.0"
rules:
  R4_D:
    minimum_valid_value_coverage: 0.70
    rationale: "Methodology §5.2.2 disables the degraded diagnostic when comparable coverage is inadequate but states no figure; the R4-F comparable-quantity coverage floor is adopted as the initial R4-D gate."
    sector_scope: all
    revision_date: "2026-09-02"
```

Retain every other existing `metadata` and `R4_D` member byte-semantically unchanged. The threshold scanner must discover the new key and prove rule code reads it; tests bind `0.6999/0.7000/0.7001`. This is a Manifest §7.3 governed calibration recorded in ADR-012, not a case-specific literal. **[SPECIFIED]**

## 8. Algorithms and execution-state decision tables

### 8.1 Unchanged rules

R0, R1-F, R4-F, R6, R7, R8, and R12 retain their public selection, execution, result, effect, and metric semantics. R12 may continue reading `public_decision_contract.missing_facts` until S09. **[SPECIFIED]**

### 8.2 R1-D

Use the existing positive-year/window predicate. Set:

```python
confidence_cap = thresholds["R1_D"]["confidence_cap"]
```

Both `metrics.confidence_cap` and `"Generate INVESTIGATE only; confidence capped at {confidence_cap}."` use that variable. A test injects a non-`C` config into the predicate/row builder to prove no hidden literal remains. **[PROPOSED]**

### 8.3 R2 — exact formula and pair selection

From valid aggregate rows, sort ascending and choose the two latest observed rows with positive import value and quantity. Missing calendar years are not interpolated. The pair remains 2023→2024 for both goldens because R2 evaluates the latest observed expansion; 2021→2023 is used only when no later valid observation exists. **[DERIVED]**

```text
years = latest.year − previous.year
ΔlnV = ln(Vlatest / Vprevious)
ΔlnQ = ln(Qlatest / Qprevious)
ΔlnUV = ln(UVlatest / UVprevious)
quantity contribution = |ΔlnQ| / (|ΔlnQ| + |ΔlnUV|)
quantity CAGR = (Qlatest / Qprevious)^(1 / years) − 1
```

Reported positive `import_uv_usd_t` remains preferred over reconstructed UV so the frozen 4-decimal decomposition does not drift; when absent, UV is `imports_usd_m * 1000 / imports_kt`. **[DERIVED]**

R2 fires when positive quantity log change is required and present, contribution ≥ configured share, and CAGR ≥ configured minimum. Add `observed_span_years` and `quantity_cagr` metrics; preserve existing 4-decimal fields:

```text
steel: 0.2419, 0.5047, -0.2625, 0.6579, CAGR 0.6565
PP:    0.0142, -0.1793, 0.1940, 0.4804, CAGR -0.1642
```

These values were independently recomputed during planning from the frozen rows; expected tests remain sourced to the snapshots/methodology. **[VERIFIED]**

| Input state | Execution | Fired |
|---|---|---|
| Two positive usable observations | `FULL` | configured predicate |
| Fewer than two usable observations | `DISABLED` | `null` |
| Non-positive direct helper input | helper raises `ValueError`; orchestrator does not call it | none |

Boundary proof: CAGR `0.0499 / 0.0500 / 0.0501`; 1-year pair; 2-year `100 → 110.25` equals 5%; explicit 2021→2023 missing-2022 fixture; golden still 2023→2024. **[SPECIFIED]**

### 8.4 R3 — value and quantity

For each basis and selected latest year:

```text
eligible value_i = valid import partner trade value
eligible quantity_i = valid, comparable import partner net weight in kt
coverage_basis = Σ eligible partner basis / matching world aggregate basis
share_i = basis_i / Σ basis_i
HHI_basis = Σ share_i²
largest_basis = max(share_i)
```

Row-derived basis is `FULL` only when eligible partner totals reconcile to the matching world aggregate within a non-domain floating calculation tolerance; otherwise that basis is `NOT_CALCULABLE` with coverage and reason. Rows take precedence over disclosure for the same basis; disclosure remains visible as source metadata. **[PROPOSED]**

A valid `disclosed_concentration.<basis>` with `status=calculated` is `FULL` for that basis. SD-2 explicitly accepts the worked-case steel value HHI as FULL despite the fixture retaining only the disclosed aggregate. **[SPECIFIED]**

Every basis metric carries `flow_basis`. The goldens report `gross`, matching `trade_quality`; FULL means the supplier distribution is calculable at that disclosed basis, not that gross imports became retained domestic demand. **[SPECIFIED]**

```text
basis fires = HHI >= thresholds.R3.supplier_hhi
              OR largest >= thresholds.R3.largest_supplier_share
R3 fires = value basis fires OR quantity basis fires
```

| Value basis | Quantity basis | Rule execution | Fired |
|---|---|---|---|
| `FULL` | any | `FULL` | OR of calculable tests |
| unavailable | `FULL` | `FULL` | OR of calculable tests |
| unavailable | unavailable | `DISABLED` | `null` |

Steel: value FULL/HHI 0.36/fires; quantity `NOT_CALCULABLE`; overall FULL/true. PP: both unavailable; overall DISABLED/null. Top-two 0.763 is displayed only and never used as largest supplier. **[SPECIFIED]**

For API compatibility, R3 keeps legacy top-level aliases `hhi`, `largest_supplier_share`, `top_two_share`, `hhi_threshold`, and `largest_supplier_threshold` (all reflecting the value basis) and additively adds nested `value` and `quantity` basis records. PP may therefore add explicit basis-status metrics where its old disabled row had `{}`; no existing populated metric is removed or repurposed. **[PROPOSED]**

Boundary proof covers HHI and largest share below/equal/above on both basis paths and a case where quantity alone fires. **[SPECIFIED]**

### 8.5 R4-D — partner rows or disclosed dispersion

Partner-row path:

1. Calculate unit value only for valid comparable rows: `USD_m * 1000 / kt`.
2. Calculate valid comparable value and quantity coverage.
3. Require value coverage ≥ the dedicated `thresholds.rules.R4_D.minimum_valid_value_coverage`; PR-02 fixes it at `0.70` in versioned configuration without coupling R4-D code to the R4-F key. **[SPECIFIED]**
4. Sort positive unit values; calculate quantity-weighted Q1, median, Q3, and `IQR = Q3 − Q1` using the first observation whose cumulative net-weight share reaches 25%, 50%, and 75%.
5. Report the observation with greatest absolute log distance from the weighted median as `outlier_candidate`, together with its quantity share. It is a candidate, not a confirmed statistical outlier or grade.
6. Fire DEGRADED only when coverage passes, at least two distinct valid observations exist, and IQR is positive.

Implement quartile probabilities as named mathematical fractions `(1 / 4, 1 / 2, 3 / 4)` passed into one weighted-quantile helper, rather than comparison literals `0.25/0.50/0.75`; those decimal values overlap configured thresholds and would correctly trigger the repository's anti-literal scanner if embedded in comparisons. **[DERIVED]**

Disclosed path:

- When row computation is unavailable and `disclosed_dispersion.status=calculated` resolves to a passport, return DEGRADED/true.
- Steel uses its disclosed annual-partner band/outlier.
- PP uses the methodology's disclosed import/export UV comparison as a product-mix research signal; the result does not call it partner dispersion or prove a specialty gap.

| Evidence | Execution | Fired | Result boundary |
|---|---|---|---|
| Valid row coverage + dispersion | `DEGRADED` | true | descriptive only |
| Valid source-attributed disclosure | `DEGRADED` | true | disclosed descriptive signal |
| Rows below coverage, no disclosure | `DISABLED` | `null` | name coverage failure |
| No rows/disclosure | `DISABLED` | `null` | name missing input |

No cluster, grade, quality, or localisation conclusion is emitted. **[SPECIFIED]**

PR-02 resolves OQ-02: quantity-weighted quartiles, named fractions, the dedicated R4-D `0.70` coverage key, and the explicitly non-confirmed farthest `outlier_candidate` are the approved conventions. **[SPECIFIED]**

### 8.6 R5 and §3.3 flow formulas

First compute latest positive imports and verified domestic presence. The degraded coexistence proxy is:

```text
domestic_capability.verified_present is true
AND (latest imports_kt > 0 OR latest imports_usd_m > 0)
```

Then calculate each physical measure only when its own inputs are numeric:

```text
Mret = M − RX
Net exposure = Mret − Xdom
Apparent consumption = Qprod + Mret − Xdom
Import penetration = Mret / Apparent consumption
```

If a verified direct `retained_imports_kt` is present while RX is unavailable, use that value and record basis `reported_verified_retained_imports`; if both direct Mret and RX are present, validation requires equality to `M − RX`. **[PROPOSED]**

| Data state | Execution | Fired |
|---|---|---|
| Verified presence + numeric Mret/Qprod/Xdom and positive apparent consumption | `FULL` | penetration ≥ configured R5 threshold |
| Verified presence + positive imports but formula inputs unavailable | `DEGRADED` | true coexistence proxy |
| Domestic presence known false or imports known non-positive | `FULL` or `DEGRADED` according to available inputs | false |
| Domestic presence unknown or no usable import measure | `DISABLED` | `null` |

Metrics always contain `retained_imports_kt`, `net_import_exposure_kt`, `apparent_consumption_kt`, `retained_import_share_of_apparent_consumption`, the configured threshold, calculation basis, and a per-metric reason naming every `UNAVAILABLE` input. No unavailable field becomes zero. **[SPECIFIED]**

Golden R5 stays DEGRADED/true for both cases and names `reexports_kt`, `retained_imports_kt`, `domestic_production_kt`, and `domestic_origin_exports_kt` as unavailable. Public acquisition in S12 may later make the FULL path calculable. **[DERIVED]**

### 8.7 R9-S

Qualifying signal types are exactly the six methodology signals represented by the schema. Derive:

```text
same_family = domestic_capability.same_process_family is true
additional_signal = any typed qualifying signal with resolvable evidence
known_failure = any unresolved_hard_gates[].state == "known_failure"
fires = same_family AND additional_signal AND NOT known_failure
```

Plain `unresolved` gates continue to block D* publication but do not suppress this coarse screen; R9-S exists to open the full assessment while facts remain unresolved. It never calculates or publishes D*. **[DERIVED]**

| Inputs | Execution | Fired |
|---|---|---|
| same-family boolean and typed gate/signal lists valid | `FULL` | predicate above |
| same-family is `UNAVAILABLE` | `DISABLED` | `null` |
| known failure | `FULL` | false |

Both goldens remain FULL/true. Tests cover no signal, false family, unresolved gate, and known failure. **[SPECIFIED]**

### 8.8 R10

| Criticality designation | Computed R3 | Execution | Fired |
|---|---|---|---|
| valid designation object | any | `FULL` | true |
| `UNAVAILABLE` | R3 fired true | `DEGRADED` | true |
| `UNAVAILABLE` | R3 false/null | `DISABLED` | `null` |

FULL result says responsible-authority designation is present and includes authority/reference/date/evidence ID. DEGRADED result says concentration warrants resilience review but is not formal criticality. Steel stays DEGRADED/true; PP stays DISABLED/null. **[SPECIFIED]**

### 8.9 R11

Established domestic capability requires all of:

```text
domestic_capability.verified_present is true
at least one producer installed_capacity_tpy is finite and > 0
that producer nameplate_status == "observed"
its evidence_class is A, B, or C
nameplate_source_evidence_id resolves to that producer/passport
```

Then:

```text
computed_ratio = latest exports_usd_m / latest imports_usd_m
fires = computed_ratio
        > thresholds.rules.R11.generic_capacity_export_import_value_ratio
        AND established domestic capability
```

Compute the ratio from the latest trade row whenever imports and exports are both present, finite, and strictly positive; never use a disclosed ratio as the predicate input. Preserve the disclosed one-decimal figure as a separately named metric and report the validation consistency result when it exists. The strict `>` boundary remains unchanged. **[SPECIFIED]**

| Computed ratio | Capability | Execution | Fired |
|---|---|---|---|
| numeric | established | `FULL` | configured predicate |
| numeric | not established/unknown | `DEGRADED` | false |
| imports or exports genuinely `UNAVAILABLE`/non-positive | established or unavailable | `DEGRADED` | false |

PP computes `4670.5 / 92.3 = 50.6013`, reports disclosed `50.6` and consistency true, and fires because the 450,000 and 720,000 t/y observed nameplates establish capability. Steel computes `27.1 / 236.9 = 0.1144`, has no disclosed ratio, and executes `FULL`/false because the configured strict threshold is not met. No product ID or authored generic-capacity flag participates. **[DERIVED]**

R11 preserves compatibility `metrics.export_import_value_ratio` (`50.6` disclosed PP; computed `0.1144` steel where no disclosure exists) and `export_import_value_ratio_threshold`; neither compatibility alias drives the predicate. It additively emits `computed_export_import_value_ratio` (`50.6013` PP, `0.1144` steel), `disclosed_export_import_value_ratio` (`50.6` PP, JSON `null` steel), `disclosed_ratio_consistent` (`true` PP, JSON `null` steel), the exact `ratio_basis: "gross_trade_value"`, ratio status/reason, and established-nameplate evidence. A fixture with exports genuinely `UNAVAILABLE` retains the DEGRADED/false incomplete-input branch. **[PROPOSED]**

### 8.10 R3/R4/R5 status vocabulary

Rule-level `execution` remains exactly `FULL|DEGRADED|DISABLED`. Metric-level unavailable bases/values use exact string `NOT_CALCULABLE`; snapshot inputs use exact string `UNAVAILABLE`. Do not add a fourth rule execution enum. **[SPECIFIED]**

All threshold predicates compare full-precision intermediate values. Source observations are emitted unchanged; calculated log changes, CAGR, shares, HHI, coverage, penetration, ratios, physical quantities, and weighted unit values are rounded to four decimal places. A rounded display value never changes a boundary outcome. **[PROPOSED]**

## 9. API and response changes

All endpoint paths and methods remain unchanged. Detailed public and simulated analysis responses gain:

```json
{
  "schema_version": "2.0.0",
  "domestic_flows": {},
  "criticality_designation": "UNAVAILABLE",
  "supplier_metrics": {},
  "rules": [
    {
      "rule_id": "R3",
      "metrics": {
        "hhi": 0.36,
        "largest_supplier_share": "NOT_CALCULABLE",
        "top_two_share": 0.763,
        "value": {},
        "quantity": {},
        "hhi_threshold": 0.25,
        "largest_supplier_threshold": 0.5
      }
    }
  ]
}
```

`supplier_metrics` preserves the old flat fields and adds quantity-basis fields; it is not accepted as rule input. R3/R5 preserve populated legacy metric keys and add nested/status/formula fields. R11 preserves PP's populated compatibility ratio, fills steel's formerly null alias from computation, and reports computed/disclosed values separately; only the computed field drives the predicate. `rules[*]` keeps every existing required key. `trade` stays byte-semantic compatible for reconciliation and charts. **[PROPOSED]**

The dossier JSON bumps `dossier_version` from `"1.0"` to `"1.1"` and additively gains `contradiction_register`. Existing keys and synthetic disclosure semantics remain unchanged. **[PROPOSED]**

Malformed live snapshots raise `PublicSnapshotIntegrityError`, which is an `EvidenceIntegrityError`; detailed/list/dossier/manifest API paths therefore return the existing typed HTTP 422 contract rather than partial results. Unknown opportunity remains 404. **[DERIVED]**

Opportunity list payload shape is unchanged. UI manifest component registry and manifest version remain unchanged. **[SPECIFIED]**

## 10. UI and rendered-text change enumeration

Exactly 13 rendered-text contracts change or are added; this count treats one bilingual catalogue key as one contract. **[PROPOSED]**

| ID | Surface | Exact English / catalogue key | Exact Arabic when catalogue-owned |
|---|---|---|---|
| RT-01 | R3 steel result | `External supply is concentrated on the value basis; quantity concentration is NOT_CALCULABLE.` | Engine source-language island; no translation in S08 |
| RT-02 | R3 no-basis result | `Value- and quantity-basis partner concentration are NOT_CALCULABLE.` | Engine source-language island |
| RT-03 | R4-D disclosed result | `A source-attributed annual unit-value dispersion summary supports a descriptive product-mix signal; no cluster or grade conclusion.` | Engine source-language island |
| RT-04 | R4-D row result | `Comparable annual partner unit values show descriptive dispersion; no cluster or grade conclusion.` | Engine source-language island |
| RT-05 | R4-D disabled result | `Comparable annual partner coverage is insufficient; R4-D is not calculable.` | Engine source-language island |
| RT-06 | R11 computed non-fire result | `Gross exports are 0.1144× imports; the configured generic-capacity warning threshold is not met.` | Engine source-language island |
| RT-07 | R11 incomplete-input result | `Export/import ratio or established nameplate capability is NOT_CALCULABLE; no generic-capacity exclusion fires.` | Engine source-language island |
| RT-08 | Dossier heading | `dossier.contradiction_register`: `Contradiction register` | `سجل التناقضات` |
| RT-09 | Dossier subsection | `dossier.public_contradictions`: `Public evidence contradictions` | `تناقضات الأدلة العامة` |
| RT-10 | Dossier subsection | `dossier.synthetic_contradictions`: `Synthetic evidence contradictions` | `تناقضات الأدلة الاصطناعية` |
| RT-11 | Dossier empty state | `dossier.no_public_contradictions`: `No public contradictions recorded.` | `لا توجد تناقضات مسجلة في الأدلة العامة.` |
| RT-12 | Dossier public-mode state | `dossier.synthetic_not_applicable`: `Synthetic evidence is not active in public mode.` | `الأدلة الاصطناعية غير نشطة في وضع الأدلة العامة.` |
| RT-13 | Dossier simulated state | `dossier.no_synthetic_contradictions`: `No synthetic contradictions are recorded for this simulation.` | `لا توجد تناقضات اصطناعية مسجلة لهذه المحاكاة.` |

All other golden rule result/effect strings remain byte-identical where the new evidence computation reaches the same branch, including the PP firing R11 text. **[PROPOSED]**

No renderer receives raw metric JSON or a new column. `rules.js` and `methodology.js` already display `result`; `decision.js` continues reading the compatibility HHI; `evidence.js` remains the evidence summary while the contradiction detail appears only in the dossier. This avoids an S08 UI redesign. **[DERIVED]**

`browser_tests/test_journeys.py` adds exact golden assertions inside existing parameterized tests for RT-01/02/03/06. The unit rule test with genuinely unavailable exports asserts RT-07. `browser_tests/test_dossier.py` asserts RT-08..13 and the steel contradiction without adding a new browser test function/node. **[PROPOSED]**

PR-03 resolves OQ-01: the six exact Arabic strings in RT-08..13 are Supervisor-approved, owner-amendable catalogue defaults, never described as owner-approved wording. Catalogue metadata moves from `1.0.0` to `1.1.0`; implementation may not vary the approved strings. **[SPECIFIED]**

## 11. Integration points

1. `data_repository.public_cases` calls the v2 validator before indexing/caching. **[PROPOSED]**
2. `scripts.validate_scenarios._index_public_cases` calls the same validator, so Gate B cannot bypass the production contract. **[PROPOSED]**
3. `decision_engine.analyze_public` normalizes typed hard gates for `evaluate_capability`, evaluates rules, and then projects supplier/flow/criticality fields. **[PROPOSED]**
4. `evidence._public_nameplate_total` treats exact `"UNAVAILABLE"` as absent, not invalid, and still computes steel `250.0 kt` and PP `1170.0 kt`; other malformed non-null values remain failures. **[PROPOSED]**
5. `reconcile_synthetic_scenario` continues to read unchanged aggregate `trade` and producer nameplates; all existing scenario checks and ground-truth back-tests remain exact. **[SPECIFIED]**
6. `_public_decision` receives the computed rules and rejects only when computed R11 fires; all other decision contract fields are unchanged. **[SPECIFIED]**
7. `genui.build_ui_manifest` needs no code change because `supplier_metrics` and rule-row contracts are maintained. **[DERIVED]**
8. `build_dossier` consumes the additive passport fields but never mutates analysis evidence. **[PROPOSED]**
9. `ui_text` resolves the six new dossier keys after catalogue version validation moves to 1.1.0. **[PROPOSED]**
10. visual provenance automatically captures Python/static/catalogue hashes and the new change reference. **[VERIFIED]**

## 12. Failure behaviour

- Invalid JSON/I/O remains `RepositoryError`; valid JSON that violates schema becomes `PublicSnapshotIntegrityError`. **[PROPOSED]**
- A v1 object in the live directory fails with `schema_version must equal 2.0.0`; it is not auto-migrated. **[SPECIFIED]**
- An unsafe/missing/mismatched `supersedes` link fails before caching. **[PROPOSED]**
- Duplicate opportunity IDs, evidence IDs, years, or partner-row identities fail. **[PROPOSED]**
- Out-of-domain HHI/share, invalid units/flags, unknown signal types, malformed passport fields, unresolved evidence references, or contradictory retained-flow arithmetic fail. **[PROPOSED]**
- R2 helper rejects non-positive direct inputs; orchestrated R2 disables rather than taking a logarithm of an invalid observation. **[SPECIFIED]**
- A calculable rule with a below-threshold value returns false; a rule lacking even a defensible proxy returns null/disabled except the explicitly preserved degraded R5/R11 non-fire contracts. **[SPECIFIED]**
- Dossier text is always HTML escaped; a contradiction containing markup renders as text. **[DERIVED]**
- Any synthetic row found in a public snapshot fails existing public-evidence validation. **[SPECIFIED]**
- Container UID/GID mismatch, unwritable temp/cache, missing browser, nonzero visual pytest, or wrong post-run ownership returns nonzero; no baseline is accepted. **[PROPOSED]**
- Manifest diff outside §18, changed golden outcome, or unexplained historical hash drift is a stop condition, not a reason to regenerate again. **[SPECIFIED]**

## 13. Unknown-input behaviour

| Input | Representation | Analytical behavior |
|---|---|---|
| Optional partner rows absent | absent or `UNAVAILABLE` | Try disclosed aggregate; otherwise basis/rule not calculable |
| Quantity concentration absent | `disclosed_concentration.quantity = UNAVAILABLE` | R3 quantity metric `NOT_CALCULABLE`; never inferred from value |
| Largest supplier absent | `UNAVAILABLE` | HHI may still fire; top-two is not substituted |
| Dispersion coverage/rows absent | `UNAVAILABLE` | Disclosed path only; no invented median/IQR |
| Domestic production/re-export/domestic exports absent | exact `UNAVAILABLE` | Each dependent R5 formula is `NOT_CALCULABLE` with named fields |
| Criticality designation absent | exact `UNAVAILABLE` | R10 is DEGRADED only if computed R3 fires; otherwise DISABLED |
| Same-process-family unknown | exact `UNAVAILABLE` | R9-S DISABLED/null |
| Producer nameplate unknown | exact `UNAVAILABLE` | Does not contribute to established capability or reconciliation total |
| Passport period/transformation unavailable | exact `UNAVAILABLE` | Retained visibly; not silently filled |
| Contradiction absent | JSON `null` | Not listed as a contradiction; dossier emits localized empty state |

`null` remains accepted only in unchanged aggregate trade fields where v1 already used it and for “no contradiction recorded”; new analytical unknown fields use uppercase `UNAVAILABLE`. **[PROPOSED]**

## 14. Privacy and security

- No network access is added to runtime, tests, migration, or baselines; the canonical visual run retains `--network=none`. **[SPECIFIED]**
- No `.env` content is read. The planning check confirmed `.env` exists and is ignored; it is absent from the visual mount allow-list. **[VERIFIED]**
- No secret, credential, personal data, Ministry dataset, or unrestricted client record enters snapshots or logs. **[SPECIFIED]**
- `supersedes` is path-contained and cannot traverse the project root. **[PROPOSED]**
- HTML rendering escapes source, contradiction, IDs, and status before insertion. **[PROPOSED]**
- Public evidence references only public passports; synthetic evidence remains separately generated, labelled, and excluded from real decision fingerprints. **[SPECIFIED]**
- Host UID/GID is operational metadata, not a secret; it is passed as numeric container identity and may be logged safely. **[DERIVED]**
- The existing prohibited-file scan must remain green; planning observed `PROHIBITED FILE SCAN PASS (344 tracked files)`. **[VERIFIED]**

## 15. Concurrency and determinism

- Metric functions are pure, operate on isolated copies, and have no global mutable state. **[PROPOSED]**
- Repository caching remains process-local and read-only after successful validation; invalid records never populate the cache. **[DERIVED]**
- Duplicate keys are rejected before cache construction, eliminating order-dependent overwrite behavior. **[PROPOSED]**
- Manifest generation and baseline update are Supervisor-controlled single-writer operations. CI is compare-only, and no concurrent update process is supported. **[SPECIFIED]**
- The visual update uses the existing candidate-directory atomic swap; the ownership check runs only after the update subprocess exits. **[VERIFIED]**
- Given identical v2 snapshots/config/code/as-of date, calculations remain deterministic apart from JSON key order as required by Core 07 §11 (`07_DETERMINISTIC_ENGINE_SPEC.md:286-296`). **[SPECIFIED]**

## 16. Versioning and compatibility

### 16.1 Versions

- Public snapshot schema: `2.0.0` (major; authored flags removed and typed blocks added). **[SPECIFIED]**
- Core 04 and 07: add exact marker `<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->`; Core 02 and 09 already carry it and receive S08 content edits without a duplicate marker. **[SPECIFIED]**
- Threshold catalogue: `config/thresholds.v1.yaml` `1.1.0 → 1.2.0` for the dedicated R4-D valid-value coverage gate. **[SPECIFIED]**
- UI catalogue: `1.0.0 → 1.1.0` (additive localized dossier keys). **[PROPOSED]**
- Dossier JSON: `"1.0" → "1.1"` (additive register). **[PROPOSED]**
- Sectors, evidence policy, scenarios, project, UI manifest, and application release remain unchanged. **[SPECIFIED]**

### 16.2 Snapshot identity policy

Schema-only re-expression of the same facts/date retains `snapshot_id` and `as_of_date`; it sets `schema_version` and a historical `supersedes` path. An evidence refresh still requires a new ID/date/query/hash under Manifest §7.5. ADR-012 records this distinction. **[SPECIFIED]**

### 16.3 Manifest diff

After generation, `snapshot_manifest.json` has seven rows:

1. live PP v2 at the original path, new hash/bytes;
2. live steel v2 at the original path, new hash/bytes;
3. historical PP v1 at the moved path, old hash `cc28e77d…`, 5,572 bytes;
4. historical steel v1 at the moved path, old hash `10efb192…`, 6,850 bytes;
5. two unchanged synthetic rows;
6. one unchanged extraction golden row.

This is semantically “two moved v1 rows plus two new v2 rows”; no old hash disappears. Exact new hashes/byte counts are generated, never predicted in the plan. **[DERIVED]**

`authority_hashes.json` final row changes are limited to Core 02/04/07/09, `config/thresholds.v1.yaml`, and `config/ui_strings.v1.yaml`; every other governed hash/byte count remains exact. `generated_on` may change only to the actual single-run date. Manifest §11 must equal the machine JSON exactly. **[PROPOSED]**

### 16.4 Compatibility

- Production loader supports only live v2; no runtime legacy compatibility branch is retained. **[PROPOSED]**
- Historical v1 remains readable only through the test adapter and ordinary JSON tools. **[PROPOSED]**
- Aggregate `trade`, opportunity IDs, snapshot IDs, decision contracts, evidence IDs, and public API endpoints stay compatible. **[SPECIFIED]**
- Flat `supplier_metrics` remains compatible for S07 frontend code while nested rule metrics expose v2 detail. **[PROPOSED]**

## 17. Complete test inventory

### 17.1 Schema and loader — new `test_public_snapshot_schema.py`

- accepts both exact goldens;
- rejects absent/wrong schema version;
- rejects `rule_context`, `fired`, `execution`, unknown top-level/nested keys;
- rejects unsafe, absent, or identity-mismatched `supersedes`;
- rejects boolean/NaN/infinite/negative values where numeric;
- validates partner row units, flags, flow, uniqueness, and source references;
- validates each disclosed concentration/dispersion domain;
- validates domestic flow sentinel/numeric combinations and arithmetic;
- validates criticality designation object/unavailable;
- validates typed producer, signals, nameplate source/class, and hard-gate states;
- validates complete passports and duplicate/missing evidence IDs;
- proves live loader ignores nested historical files;
- proves a v1 object copied into live is rejected;
- proves duplicate opportunity IDs fail rather than overwrite.

### 17.2 Pure metrics — new `test_trade_metrics.py`

- CAGR 1-year and 2-year exacts and invalid year span/values;
- latest usable pair with missing 2022 and later 2024 precedence;
- row-derived value/quantity HHI and largest share;
- incomplete-basis reconciliation returns `NOT_CALCULABLE`;
- disclosed fallback and row precedence;
- weighted Q1/median/Q3/IQR and farthest outlier candidate;
- R4-D coverage below/equal/above;
- retained imports/direct retained precedence/reconciliation;
- net exposure, apparent consumption, penetration;
- per-metric unknown reasons naming fields;
- non-positive apparent consumption remains not calculable;
- established nameplate accepts only positive observed A/B/C sourced evidence;
- row ratio computes from positive imports/exports, rounds to four decimals for output, and ignores disclosed ratio as predicate input;
- disclosed/computed ratio consistency accepts exact/within-`0.05` cases and rejects a difference above `0.05`;
- steel 2024 computes `0.1144`; PP computes `50.6013`, reports disclosed `50.6`, and reports consistency true.

### 17.3 Migration equivalence

`tests/legacy_snapshot_v1.py` first characterizes v1 using the old semantics and production math helpers, and converts each still-live v1 record to the exact proposed v2 in memory for tests. Before any production `rule_context` read is removed, run (a) a characterization test proving the legacy canonical summary matches the current production ledger and (b) the complete deep-equivalence test proving a temporary/private v2 evaluation path differs only at paths in the explicit `INTENDED_S08_MIGRATION_DIFFERENCES` allow-list. Only after both are green may Task 6 move the v1 bytes, install the exact live v2 JSON, switch `evaluate_rules`, and delete the legacy production path. The same test then directly reloads historical v1 and live v2 and must remain green for:

- all 15 public rule IDs in order;
- every `fired` and `execution` value except steel `R11.execution: DEGRADED → FULL`; steel `R11.fired` remains false;
- R1-D confidence cap;
- R2 from/to years and decomposition to 4 decimals;
- steel HHI 0.36/top-two 0.763 and unavailable largest/quantity;
- R5 `NOT_CALCULABLE` penetration plus threshold;
- PP compatibility export/import ratio `50.6`, computed ratio `50.6013`, disclosed ratio `50.6`, consistency true, and threshold;
- steel computed export/import ratio `0.1144` and threshold;
- public state/route;
- unchanged snapshot ID/as-of/opportunity ID;
- no `rule_context` in live v2.

The allow-list is data, not a broad key filter. It names exact opportunity/rule/field paths and expected old/new values:

- steel `R11.execution`: `DEGRADED → FULL`;
- steel `R11.metrics.export_import_value_ratio`: `null → 0.1144`;
- additive R2 keys `observed_span_years`, `quantity_cagr`;
- additive R3 keys: steel `value` and `quantity`; PP `hhi`, `largest_supplier_share`, `top_two_share`, `hhi_threshold`, `largest_supplier_threshold`, `value`, and `quantity`;
- additive R4-D keys `calculation_basis`, `valid_value_coverage`, `valid_quantity_coverage`, `minimum_valid_value_coverage`, `weighted_q1_usd_t`, `weighted_median_usd_t`, `weighted_q3_usd_t`, `iqr_usd_t`, `outlier_candidate`;
- additive R5 keys `retained_imports_kt`, `net_import_exposure_kt`, `apparent_consumption_kt`, `retained_import_share_of_apparent_consumption`, `calculation_basis`, `unavailable_reasons`;
- additive R9-S keys `same_process_family`, `qualifying_signal_count`, `known_hard_gate_failure`; additive R10 keys `criticality_status`, `criticality_evidence_id`;
- additive R11 keys `computed_export_import_value_ratio`, `disclosed_export_import_value_ratio`, `disclosed_ratio_consistent`, `ratio_basis`, `ratio_status`, `ratio_reason`, `established_nameplate`;
- exact result paths: steel R3→RT-01, PP R3→RT-02, steel and PP R4-D→RT-03, and steel R11→RT-06. RT-04/05/07 are test-only branches, not golden migration differences.

The assertion deep-diffs the complete ordered rule objects and response identity/state fields, fails on any unexpected missing, changed, or added path, and separately requires each allow-list entry to occur with its declared old/new values. The converter and canonicalizer are test oracles, never production migration fallbacks. A temporary private v1/v2 dispatch used to establish the pre-cutover proof is removed in the same Task 6 cutover; the final production tree supports v2 only and contains no `rule_context` read. **[SPECIFIED]**

### 17.4 Existing rule/boundary tests

- Update `test_rules.py` for nested R3 metrics, config-sourced R1-D, R4-D disclosed paths, full/degraded R5, typed R9, R10, and R11.
- Update `test_threshold_boundaries.py`:
  - R2 share and CAGR `below/equal/above`;
  - R3 HHI value and quantity `0.2499/0.2500/0.2501`;
  - largest shares both bases `0.4999/0.5000/0.5001`;
  - R4-D dedicated configured coverage `0.6999/0.7000/0.7001`;
  - R5 penetration `0.1999/0.2000/0.2001`;
  - R11 strict ratio `49.99/50.00/50.01` with/without nameplate;
  - `test_r11_missing_ratio_is_degraded_and_does_not_fire` rebuilt on a fixture whose latest `exports_usd_m` is genuinely `UNAVAILABLE`;
  - no product-ID dispatch.
- Preserve all capability/economics boundaries.

### 17.5 Golden, scenario, isolation, API

- `test_golden_cases.py`: expectations are not weakened; add exact rule execution and new R2 metrics.
- `test_scenario_validation.py`: nameplate totals still 250/1170 kt, Gate B two scenarios PASS.
- `test_simulation_fidelity.py`: public ledger still has zero synthetic rows; simulation appends exactly R6/R7/R8 and outputs unchanged.
- `test_synthetic_isolation.py`: all public passports validate; live snapshots contain no synthetic fields/rows; real fingerprint unchanged.
- `test_api.py`: additive schema/flows/criticality/nested R3 fields and existing HTTP behavior.
- `test_authority_disclosure.py`: final catalogue version 1.1.0 appears.
- `test_integrity_contract.py`: exact four public snapshot paths (two live/two historical) and unchanged synthetic/golden rows.
- `test_threshold_literals.py`: recursive scan includes `public_snapshot.py` and `trade_metrics.py`, sees `rules.R4_D.minimum_valid_value_coverage`, and finds no configured comparison literal in code.

### 17.6 Dossier/catalogue

- Public steel register has one public contradiction, no synthetic rows, `NOT_APPLICABLE`.
- Public PP register has empty public list and localized public empty state.
- Simulated steel retains one public contradiction, has no synthetic contradiction, `NONE_RECORDED`, and retains both policy warning labels.
- A planted synthetic contradiction appears only in simulated test input and is labelled; it never enters public analysis.
- HTML escapes a malicious contradiction fixture.
- Both locales render all six exact catalogue strings; English contradiction content is a source-language island in Arabic.
- Catalogue metadata/endpoint moves to 1.1.0; key/placeholder/NFC/usage/copy checks stay green.
- Dossier contract version is 1.1; existing JSON remains locale-neutral.

### 17.7 KL-32 and browser

- `build_command(uid=123, gid=456)` contains exact `--user 123:456`, HOME/cache/browser env, and host UID/GID.
- Container-side UID/GID mismatch exits 2 before pytest.
- Positive ownership helper accepts current-user files.
- Negative ownership helper reports the first relative path and runner exits 2.
- Mount allow-list remains exact and excludes `.env`.
- Existing browser journey/dossier functions assert the applicable RT-01..06 and RT-08..13 golden text without changing the 18-test/122-node inventory; the unavailable-exports unit fixture asserts RT-07.
- All 40 updated WebPs, manifest hash, source hashes, dimensions, RGB/lossless format, file/aggregate budgets, and fixed tolerance pass.
- Update target remains absent from CI.

### 17.8 Required unchanged proofs

- steel public `INVESTIGATE`, simulated `ADVANCE` route 5 with 57.509/46.491/D* 0.2667/S* 18/ΔNV 198/ratio 1.0751;
- PP public/simulated `REJECT` route 0 with -24 kt gap and zero support;
- two synthetic reconciliations and back-tests PASS;
- no threshold drift beyond the exact authorized R4-D 1.2.0 change, and no sector/evidence-policy/synthetic/DOCX drift;
- no synthetic leakage;
- browser accessibility, keyboard, RTL, responsive, network, console, print/PDF, and visual tests remain green.

## 18. Validators, Core wording, and generator-diff controls

### 18.1 Exact Core 04 proposal

Add the v2 marker and replace/extend the applicable sections with this normative text:

```markdown
### PublicSnapshot v2

A live public snapshot shall set `schema_version: "2.0.0"`. A schema-only
re-expression of identical frozen facts retains `snapshot_id` and
`as_of_date` and sets `supersedes` to the byte-identical historical v1 path.
An evidence refresh instead receives a new snapshot ID and date under the
Authority Manifest §7.5 process.

Aggregate `trade` rows remain the frozen world series. Optional
`partner_observations` retain year × partner × flow value, net weight,
quantity unit, gross-flow status, source evidence ID, and independent value,
weight, and comparability validity flags. Where the frozen authority
discloses only an aggregate calculation, `disclosed_concentration` and
`disclosed_dispersion` retain that calculation, status, period, basis, source
evidence ID, coverage note, and explicit `UNAVAILABLE` fields. A disclosed
aggregate is evidence, never an authored rule result.

For each aggregate trade row with positive numeric imports and exports, the
system computes export/import value ratio from those flows. A disclosed
one-decimal ratio is retained separately and must be within `0.05` of the
computed value; both are reported.

`domestic_flows` contains domestic production, retained imports,
domestic-origin exports, and re-exports in kt; each value is numeric or exact
`UNAVAILABLE`. `criticality_designation` is either exact `UNAVAILABLE` or a
responsible-authority record with authority, reference, date, and evidence
ID. Producer evidence retains process family, process route, typed adjacency
signals, standards, observed nameplate and unit, evidence class, and passport
references. Hard-gate evidence distinguishes unresolved from known failure.

Every public EvidencePassport includes period, retrieved_at, status,
evidence_class, synthetic_flag=false, supports, transformation,
reviewer_status, and contradiction. Contradiction is retained; it is not
silently harmonised away.

A valid public snapshot contains no `rule_context`, `fired`, `execution`, or
other authored rule outcome. `public_decision_contract` is retained
temporarily for the S09 selector migration.
```

**[PROPOSED]**

### 18.2 Exact Core 07 proposal

```markdown
### S08 computed public-rule semantics

R1-D emits the configured `confidence_cap`.

R2 compares the two latest usable observed years and computes quantity CAGR
over their observed span:
`(Q_latest / Q_previous)^(1 / (year_latest - year_previous)) - 1`.
Missing years are not interpolated.

R3 computes HHI and largest-supplier share independently on value and
quantity. A basis without complete partner rows or a source-attributed
calculated disclosure is `NOT_CALCULABLE`. The rule fires when either
calculable basis meets either configured test. The frozen steel calculated
value disclosure executes FULL; its quantity basis is NOT_CALCULABLE.

R4-D computes valid comparable coverage against its dedicated configured
`minimum_valid_value_coverage`, quantity-weighted median and
quartiles, IQR, and a descriptive farthest-observation candidate from annual
partner rows, or uses a source-attributed calculated disclosure. It remains
DEGRADED and may open only product-mix/specification research. It never claims
a cluster, grade, quality, or localization case.

R5 computes retained imports, net import exposure, apparent consumption, and
import penetration when their physical inputs exist. Missing inputs remain
`NOT_CALCULABLE` with named reasons. Verified domestic capability plus
positive imports is a DEGRADED coexistence proxy; the FULL rule applies the
configured penetration threshold.

R9-S requires verified same process family, at least one typed methodology
signal, and no known hard-gate failure. Unresolved gates still block route
publication but do not prevent the coarse screen.

R10 is FULL when a responsible-authority criticality designation exists,
DEGRADED when computed R3 alone opens a resilience review, and DISABLED
otherwise.

R11 computes gross `export_import_value_ratio = exports_usd_m / imports_usd_m`
from the latest row whenever both operands are positive and numeric. A
disclosed ratio is retained and reported separately and, when present, must
be consistent with the computed value within absolute tolerance `0.05`.
The public generic-capacity warning requires the computed ratio to exceed the
configured strict threshold and established domestic capability evidenced by
at least one positive observed A/B/C producer nameplate. Missing exports or
imports produce DEGRADED/false; a calculable ratio with established capability
executes FULL whether the predicate is true or false. Product IDs, disclosed
ratios, and authored flags never determine the predicate.
```

**[PROPOSED]**

Core 07 §10 also names malformed schema, unsafe historical link, invalid concentration domains, and contradictory flow arithmetic as fail-closed evidence-integrity errors. **[PROPOSED]**

### 18.3 Exact Core 02 proposal

Update §3's R1-D/R2/R3/R4-D/R5/R9-S/R10/R11 rows to name the functions in §5.8 and evidence-derived semantics. Add a §4 trade-flow subsection with all four §3.3 formulas. Add every new public function to §9's traceability map with its primary tests and visible output. **[SPECIFIED]**

Exact traceability wording:

```markdown
| Public snapshot v2 validation | `public_snapshot.validate_public_snapshot` | Core 04 PublicSnapshot v2; Core 05 §§5–7 | `test_public_snapshot_schema.py` | snapshot/schema identity and fail-closed loader |
| Observed-span CAGR | `trade_metrics.compound_annual_growth`, `latest_usable_trade_pair` | Methodology §4 R2; I3 | `test_trade_metrics.py`, `test_threshold_boundaries.py` | R2 ledger metrics |
| Dual-basis concentration | `trade_metrics.concentration_metrics` | Methodology §3.3/R3; I2 | rule/boundary/migration tests | R3 ledger and HHI card |
| Degraded dispersion | `trade_metrics.degraded_dispersion_metrics` | Methodology §5.2.2 | rule/boundary tests | R4-D ledger |
| Domestic flow formulas | `trade_metrics.domestic_flow_metrics` | Methodology §3.3/Appendix A | formula/rule tests | R5 ledger metrics |
| Gross export/import ratio | `trade_metrics.export_import_value_ratio` | Methodology §14.1/R11 | metric/rule/migration tests | R11 computed and disclosed ratio metrics |
| Established nameplate | `trade_metrics.established_domestic_nameplate` | Methodology R9-S/R11; worked case §14 | rule tests | R9-S/R11 ledger |
| Supplier compatibility projection | `trade_metrics.build_supplier_metrics` | Aggregate response contract | API/GenUI tests | metric grid |
| Hard-gate normalization | `public_snapshot.capability_hard_gate_names`, `has_known_hard_gate_failure` | Core 04/07 v2 | schema/R9 tests | capability and R9-S |
```

**[PROPOSED]**

### 18.4 Exact Core 09 proposal

```markdown
### Public snapshot schema-migration proof

Golden schema migrations retain the historical bytes and compare a test-only
legacy evaluation with the live schema result. For every migrated golden the
proof deep-compares every ordered rule and response identity/state field,
failing on any difference outside an exact old/new allow-list. The allow-list
contains steel R11 execution `DEGRADED` to `FULL`, steel compatibility ratio
`null` to `0.1144`, individually named
additive metric keys, and the exact approved changed result-text paths. Fired
values, snapshot identity, and public state remain identical. The production loader is
non-recursive and accepts only the current live schema; historical paths are
manifested but never loaded at runtime.

R2 tests cover one- and multi-year observed spans and missing-year
non-interpolation. R3 boundaries run on value and quantity. R4-D tests cover
coverage and no-grade wording. R5 tests cover numeric and UNAVAILABLE flows.
R9-S, R10, and R11 tests prove evidence-derived predicates and the absence of
author flags. Dossier tests prove public/synthetic contradiction separation.
```

**[PROPOSED]**

### 18.5 ADR-012 required record

ADR-012 records:

- ADR-010 and SD-1/2/3 approval basis;
- Manifest class §7.4 for Core 02/04/07/09, §7.5 representation migration for data with the explicit unchanged-ID rationale, and §7.3 for thresholds 1.2.0 and catalogue 1.1.0;
- exact v1 hash/byte retention;
- no new empirical number policy and the disclosed aggregate fallback;
- exact R2/R3/R4-D/R5/R9-S/R10/R11 derivations, including the dedicated R4-D coverage gate and computed/disclosed R11 ratio contract;
- PR-02's exact R4-D threshold rationale, `sector_scope: all`, `revision_date: "2026-09-02"`, and threshold scanner/boundary proof;
- PR-03's attribution of the six Arabic strings as Supervisor-approved, owner-amendable defaults, never owner-approved;
- migration deep-equivalence allow-list and steel R11 `FULL`/false rationale;
- why `public_decision_contract` remains until S09;
- KL-32 host ownership design;
- one `build_manifests.py` run after all governed edits and full regression, plus one separate visual-baseline update;
- unchanged golden outcomes, scenarios, DOCX, and non-goals.

OQ-01 and OQ-02 are resolved by PR-03 and PR-02 respectively; ADR-012 and the PR record those Supervisor rulings exactly. **[SPECIFIED]**

### 18.6 Generator sequence and allowed diffs

There is exactly **one** planned `scripts/build_manifests.py` run. The preliminary one-run note in `persona.md` is confirmed by PR-04 and requires no persona-file amendment; this revision is constrained to `plan.md`. **[SPECIFIED]**

**Run G1 — final governed-artifact gate**

Preconditions: Core 02/04/07/09, thresholds 1.2.0, catalogue 1.1.0, both byte-identical v1 moves, both exact live v2 files, schema/loader/rules/engine/reconciliation/dossier/KL-32 code, all test/docs changes, migration equivalence, goldens, isolation, API, catalogue, localized HTML, browser functional tests, and the full default functional suite are complete and green; exact historical hashes are verified. **[SPECIFIED]**

The single expected generated diff is:

- `snapshot_manifest.json`: two moved v1 rows at historical paths preserving old hashes/bytes, two new live v2 rows with generated hashes/bytes, unchanged two synthetic rows, unchanged extraction-golden row, and `generated_on`;
- `authority_hashes.json`: changed rows only for Core 02/04/07/09, `config/thresholds.v1.yaml`, and `config/ui_strings.v1.yaml`, plus `generated_on`;
- `docs/authority/00_AUTHORITY_MANIFEST.md` §11: exact human-table copies of those final machine rows, with every unaffected row unchanged.

After G1, audit every path/hash/byte/date, copy machine values into Manifest §11, and run integrity, human-table equality, migration, golden, Gate B, smoke, and the full regression again. A second generator run is permitted only if a later justified governed fix changes a hashed input; record the defect, authority, exact fix, first-run diff, second-run reason, and final diff before running it. Routine mismatch repair, date refresh, or catalogue sequencing is not justification. **[SPECIFIED]**

The later visual update target is one separate governed baseline generation and is not counted as a `build_manifests.py` run. **[DERIVED]**

## 19. Acceptance criteria

- **AC-01:** only live schema `2.0.0` loads; nested history is ignored; v1 in live fails. **[SPECIFIED]**
- **AC-02:** historical v1 bytes/hashes/sizes are exact and manifested. **[SPECIFIED]**
- **AC-03:** live snapshots have unchanged snapshot IDs/dates and exact `supersedes` links. **[SPECIFIED]**
- **AC-04:** live snapshots contain no `rule_context` or authored rule outcome. **[SPECIFIED]**
- **AC-05:** every new empirical number is traceable through §7; no partner/flow/criticality number is invented. **[SPECIFIED]**
- **AC-06:** R1-D cap is config-sourced and scanner-clean. **[SPECIFIED]**
- **AC-07:** R2 uses observed-span CAGR and preserves frozen decomposition/pair. **[SPECIFIED]**
- **AC-08:** R3 evaluates both bases, steel value remains FULL/0.36/true, both golden quantity bases are not calculable. **[SPECIFIED]**
- **AC-09:** R4-D derives from typed disclosure/rows, both goldens remain DEGRADED/true, and no grade/cluster claim appears. **[SPECIFIED]**
- **AC-10:** R5 computes all four formulas when numeric and returns named unknowns for the goldens. **[SPECIFIED]**
- **AC-11:** R9-S, R10, and R11 derive only from typed evidence; PP R11 is FULL/true from computed `50.6013`, steel is FULL/false from computed `0.1144`, and disclosed PP `50.6` is reported consistently. **[SPECIFIED]**
- **AC-12:** public decision selector reads computed R11 only and preserves both public states/routes. **[SPECIFIED]**
- **AC-13:** both simulations, reconciliations, numeric goldens, and real fingerprints are unchanged. **[SPECIFIED]**
- **AC-14:** detailed API is additive and steel HHI card still displays 0.36. **[SPECIFIED]**
- **AC-15:** dossier JSON/HTML has correctly separated contradictions in both modes/locales and zero public synthetic leakage. **[SPECIFIED]**
- **AC-16:** catalogue is 1.1.0 with exact parity and no policy-label duplication. **[PROPOSED]**
- **AC-17:** container command includes host user; container identity and post-update host ownership tests pass. **[SPECIFIED]**
- **AC-18:** all 40 baselines are regenerated only after functional green using the exact change reference and inspected before review. **[SPECIFIED]**
- **AC-19:** Core/ADR/docs/traceability are exact and every new function is mapped. **[SPECIFIED]**
- **AC-20:** exactly one planned manifest run occurs after all governed edits/full regression and final machine/human manifests agree; any later justified fix/run is explicitly recorded. **[SPECIFIED]**
- **AC-21:** required focused/default/browser/integrity/Gate B/smoke/CI gates have fresh recorded output. **[SPECIFIED]**
- **AC-22:** zero Supervisor findings and independent Grok approval are external gates; the Implementer and Planner do not self-approve. **[SPECIFIED]**

## 20. Documentation updates

- `DEVELOPMENT_GUIDE.md`: document schema 2.0.0 blocks, exact unknowns, live-only loader, historical policy, the single post-regression manifest gate, host-owned visual updates, and the exact S08 baseline command. **[PROPOSED]**
- `KNOWN_LIMITATIONS.md`: provisionally close KL-30 and KL-32 on actual evidence; mark KL-26's formula/schema portion closed while public data remains unavailable pending S12. Do not claim the S12 input gap closed. **[SPECIFIED]**
- `REQUIREMENTS_TRACEABILITY.md`: add an S08 local evidence registry and the v0.3 rows named in §2.1 at `TESTED` only after execution; update FR-020–025, INV-08, TL-01/02/03/04/08/09 evidence without rewriting historical S01–S07 records. **[PROPOSED]**
- `BUILD_PROGRESS.md`: update only S08 row/log with actual plan/implementation/review/test state; preserve Supervisor-owned S07 post-merge hunks. **[SPECIFIED]**
- `ARCHITECTURE_DECISIONS.md`: ADR-012 per §18.5, initially Proposed until the Supervisor promotes it. **[PROPOSED]**
- `CHANGELOG.md`: add schema v2/history, computed rules/formulas, contradiction dossier, and host-owned baseline update bullets; keep Unreleased chronological and do not claim release. **[PROPOSED]**
- Core 02/04/07/09 and Manifest §11: exact proposals and generated values in §18. **[PROPOSED]**

## 21. Traceability table

| Requirement | Implementation | Primary proof | Task |
|---|---|---|---|
| C1/C2 rules | `public_snapshot.py`, `rules.py`, `data_repository.py` | schema + migration tests | 2–6 |
| D2/I2 | `trade_metrics.concentration_metrics` | dual-basis boundaries/goldens | 4 |
| D4/FR-015 | `dossier.py`, catalogue | dossier/API/browser tests | 7–8, 10 |
| D7/KL-26 | `trade_metrics.domestic_flow_metrics`, R5 | formula/unknown/boundary tests | 5 |
| D12/KL-30 | R1-D config projection | mutation + threshold scanner | 4 |
| I3/R2 | CAGR/pair functions | one/two-year/missing-year/golden | 4 |
| FR-020/021 | `evaluate_rules` | all-rule schema/migration | 4–6 |
| FR-022 | decomposition + CAGR | exact 4-decimal values | 4 |
| FR-023/INV-08 | R4-D wording/metrics | anti-grade + rendered text | 5, 10 |
| FR-024 | R9-S typed predicate | signal/gate tests | 5 |
| FR-025 | R11 computed gross ratio + typed nameplate predicate + computed selector | PP/steel/unavailable/boundary/API/migration | 5–6 |
| INV-01/02/03/04/10/11 | unchanged isolation/history | leakage, fingerprints, manifests, goldens | 3, 6, 11 |
| TL-01/02/03/04/08/09 | validators/formulas/rules/goldens/boundaries/isolation | suites in §17 | all |
| KL-32/R-4 | user-mapped container | command/ownership + visual compare | 9–10 |
| Core 02 §9 | Core map rows | integrity + doc test | 7, 11 |

## 22. Non-goals

- no public decision-selection rewrite, real-ADVANCE gate, `MONITOR`, screening disposition, hard exclusions, gap taxonomy, computed missing facts, route sequence/hypotheses, or five profiles (S09); **[SPECIFIED]**
- no simulation schema/allocation/expansion/R8/class-if-confirmed work (S10); **[SPECIFIED]**
- no acquisition, live connectors, raw artifacts, new public cases, or new empirical values (S11/S12); **[SPECIFIED]**
- no graph, screening surface, Executive Mode, dossier redesign/PDF redesign, or extraction corpus; **[SPECIFIED]**
- no threshold change beyond PR-02's exact R4-D key/version/metadata, and no sector-profile, evidence-policy, synthetic scenario, project version, DOCX, or golden expectation change; **[SPECIFIED]**
- no frontend component/CSS redesign or new GenUI type; **[SPECIFIED]**
- no dependency install, lock update, direct Docker command, host baseline generation, baseline tolerance/mask/matrix change, or CI update mode; **[SPECIFIED]**
- no unrelated cleanup of Supervisor-owned working-tree changes or `.workflow/runs` helpers. **[SPECIFIED]**

## 23. TDD task sequence

The workflow instruction that implementation remains uncommitted overrides the writing-plans skill's generic “commit after each task” advice. Every task ends Confirm → Validate → Test; the Supervisor alone performs delivery after review. **[SPECIFIED]**

### Task 0 — Protect the slice boundary

**Files:** read-only status and governed path inventory.

- [ ] Record branch/HEAD and `git status --short`; compare with `context.md`.
- [ ] Record SHA-256/bytes for both live v1 snapshots before moving.
- [ ] Confirm `.env` ignored without reading it; record prohibited scan.
- [ ] Confirm no plan path includes synthetic, thresholds, sectors, DOCX, lock, or untracked helpers.

**Confirm:** base and pre-existing paths match the slice contract.
**Validate:** no unexplained tracked/untracked path.
**Test:** existing integrity, 377-test default suite, and smoke as characterization only.

### Task 1 — Freeze the legacy oracle before removing `rule_context`

**Files:** create `tests/legacy_snapshot_v1.py`, `tests/test_snapshot_migration_equivalence.py`.

- [ ] Write a test-only canonicalizer for old 15-rule order, execution, fired state, selected metrics, and old public selector outcome.
- [ ] Add characterization tests that compare the adapter with current `evaluate_rules` and `_public_decision` on both still-live v1 objects.
- [ ] Run and observe PASS; label these characterization tests honestly (they protect existing behavior rather than begin RED).
- [ ] Add the future historical/live comparison test and observe RED because historical paths/schema v2 do not exist.

**Confirm:** the adapter matches old production before deletion.
**Validate:** production imports no test helper.
**Test:** focused migration module shows characterization PASS + migration RED for the intended missing v2 behavior.

### Task 2 — Specify and validate the v2 candidate in memory

**Files:** create `public_snapshot.py`, `test_public_snapshot_schema.py`; extend the test-only converter in `legacy_snapshot_v1.py`. Do not move the live v1 files yet.

- [ ] Write RED tests for all §7.3 rules, exact sentinel behavior, and exact JSON structures.
- [ ] Implement the minimal validator and historical-link normalization.
- [ ] Implement the test-only v1→exact-v2 converter and assert its output equals §7.1/§7.2 field for field.
- [ ] Run schema tests GREEN against in-memory v2 candidates.
- [ ] Keep the equivalence test RED only because the private v2 rule evaluation does not yet exist.

**Confirm:** production still uses untouched live v1; the validated candidate contains no `rule_context`.
**Validate:** no invented number against §7 provenance ledger.
**Test:** schema/loader-independent focused suite.

### Task 3 — Specify loader and Gate B cutover

**Files:** modify `data_repository.py`, `validate_scenarios.py`, schema tests.

- [ ] Write RED tests for live-v2-only, nested history ignored, duplicate ID, and validator reuse by Gate B.
- [ ] Add the final validator calls behind a temporary private schema dispatch so existing v1 characterization remains runnable until Task 6.
- [ ] Keep final live-v2-only assertions RED until the Task 6 data cutover; make duplicate/reference unit behavior GREEN.
- [ ] Clear caches in every monkeypatch test teardown.

**Confirm:** no historical directory can be discovered even during transition.
**Validate:** typed errors reach existing API mapping.
**Test:** schema + scenario-validation focused suites with cutover RED explicitly recorded.

### Task 4 — Implement R1-D, R2, and R3

**Files:** create `trade_metrics.py`, `test_trade_metrics.py`; modify `rules.py`, rule/boundary tests.

- [ ] Write RED CAGR/pair tests, including 2021→2023 and latest 2023→2024 precedence.
- [ ] Implement CAGR/pair helpers; GREEN.
- [ ] Write RED config-cap test; remove R1-D literal; GREEN.
- [ ] Write RED value/quantity row and disclosure concentration tests.
- [ ] Implement a temporary private v2 rule path for basis metrics and nested R3 result while leaving the characterized v1 entry path intact; GREEN.
- [ ] Add all below/equal/above tests; GREEN.
- [ ] Verify steel R2/R3 and PP R2 exacts.

**Confirm:** no threshold literal or product ID.
**Validate:** quantity basis never inferred from value.
**Test:** metrics + rule + boundary + threshold scan.

### Task 5 — Implement R4-D, R5, R9-S, R10, R11

**Files:** `trade_metrics.py`, `rules.py`, `config/thresholds.v1.yaml`, schema/rule/metric/boundary/scanner tests.

- [ ] Apply resolved PR-02 exactly: add only the dedicated R4-D `0.70` key, version `1.2.0`, exact rationale/scope/date, scanner assertion, and `0.6999/0.7000/0.7001` boundaries.
- [ ] RED→GREEN R4-D row coverage/quantile/outlier-candidate/disclosure/disabled paths and anti-grade wording.
- [ ] RED→GREEN all four flow formulas, direct retained reconciliation, unknown reasons, and R5 FULL/DEGRADED decisions.
- [ ] RED→GREEN typed R9 signal/family/unresolved/known-failure paths.
- [ ] RED→GREEN R10 designation/R3/disabled table.
- [ ] RED→GREEN row-computed R11 ratio, disclosed/computed `0.05` validation, separately reported values, established nameplate, and strict ratio/capability conjunction.
- [ ] Re-base `test_r11_missing_ratio_is_degraded_and_does_not_fire` on a latest row whose exports are genuinely `UNAVAILABLE`.
- [ ] Complete the private v2 branch with no `rule_context` read; retain the isolated characterized v1 branch only until the Task 6 equivalence gate.

**Confirm:** the in-memory v2 candidates reach the same rule states while live v1 still behaves identically.
**Validate:** unknowns never become false proof or zero.
**Test:** focused metrics/rules/boundaries plus anti-grade test.

### Task 6 — Prove equivalence, then cut over and integrate

**Files:** move/add the four snapshot files; modify `rules.py`, `data_repository.py`, `validate_scenarios.py`, `decision_engine.py`, `evidence.py`, `dossier.py`, and scenario/simulation/isolation/API/golden tests.

- [ ] Run the full legacy-response versus in-memory-v2 deep-diff proof GREEN for both goldens while the old production path still exists; require every difference to match the exact §17.3 path and old/new value.
- [ ] Record the green output; only now move v1 bytes, write exact live v2 JSON, switch the repository and `evaluate_rules` to v2, and delete the temporary v1 production branch and every production `rule_context` read.
- [ ] Re-run equivalence against historical-v1/live-v2 and require only the exact allow-listed steel R11 execution/ratio, additive computed-ratio keys, approved result text, and individually named additive metric keys.
- [ ] RED test that `_public_decision` rejects on computed R11 with no `rule_context`; replace only that guard; GREEN both public goldens.
- [ ] RED tests for v2 nameplate reconciliation and exact existing totals; adapt sentinel handling; GREEN Gate B.
- [ ] Add analysis `schema_version`, flow, criticality, nested rule, and supplier compatibility fields; GREEN API/GenUI tests.
- [ ] RED→GREEN additive JSON contradiction register and dossier version.
- [ ] Run all default functional tests and smoke GREEN.

**Confirm:** pre-removal equivalence was green, the final production tree has no legacy branch, and selector semantics beyond the guard are unchanged.
**Validate:** public/simulated fingerprints and numerical exacts.
**Test:** golden, scenario, fidelity, isolation, dossier, API suites.

### Task 7 — Complete all governed content before generation

**Files:** Core 02/04/07/09, ADR-012, `ui_strings.v1.yaml`, `config.py`, `dossier.py`, catalogue/dossier/API/browser assertions, initial docs.

- [ ] Apply exact §18.1–18.5 wording and function map; add doc contract tests where needed.
- [ ] Record ADR-012 as Proposed with both resolved rulings, versions 1.2.0/1.1.0, R11 computed/disclosed semantics, migration allow-list, and exact single-run diff.
- [ ] Apply resolved PR-03's exact six EN/AR pairs and catalogue 1.1.0; never label them owner-approved or vary their text.
- [ ] RED→GREEN catalogue metadata/key/parity/usage, localized escaped HTML register, API, and browser assertions.
- [ ] Complete Development Guide, limitations, traceability, progress, and changelog content that affects the final governed diff.
- [ ] Do not run `build_manifests.py` in this task.

**Confirm:** every governed source edit is complete and generator count is zero.
**Validate:** OQ-01/OQ-02 wording and exact versions/config metadata.
**Test:** catalogue, dossier, API, doc contract, migration, goldens, Gate B, full default suite, smoke.

### Task 8 — Full regression and single authority generation

**Files:** machine manifests and Manifest §11 only after all Task 0–7 governed changes are complete.

- [ ] Verify exact historical v1 hashes and audit the complete governed changed-path inventory.
- [ ] Run focused, migration, golden, Gate B, catalogue, dossier, API, browser-functional, smoke, and full default regression GREEN.
- [ ] Run `build_manifests.py` exactly once (G1).
- [ ] Audit the single expected diff in §18.6: four public snapshot rows, thresholds row, catalogue row, Core 02/04/07/09 rows, and `generated_on`; all synthetic/golden/other authority rows remain exact.
- [ ] Copy final machine rows to Manifest §11 and rerun integrity, table equality, migration, goldens, Gate B, smoke, and full regression.
- [ ] Do not run the generator again unless a later justified governed fix is first recorded with the evidence required by §18.6.

**Confirm:** planned manifest-generator count is exactly one and its diff is allow-listed.
**Validate:** no unexplained row/hash/byte/date and no synthetic policy-label duplication.
**Test:** authority table, integrity, migration, goldens, Gate B, smoke, full default suite.

### Task 9 — Fix KL-32 after functional green

**Files:** visual runner/container, visual contract tests.

- [ ] Write RED command-shape tests for `--user`, HOME/cache/browser path, host UID/GID.
- [ ] Implement command construction; GREEN.
- [ ] Write RED container identity and host post-run ownership tests.
- [ ] Implement fail-closed checks; GREEN.
- [ ] Re-run all functional/default tests before any baseline update.

**Confirm:** exact mount/network/image restrictions remain.
**Validate:** update failure cannot be reported as success.
**Test:** visual baseline contract and full default suite.

### Task 10 — Assert rendered text, regenerate, inspect, compare

**Files:** existing browser journey/dossier tests and all baseline artifacts.

- [ ] Add exact RT-01..13 assertions inside existing browser functions/contracts; run functional browser suite GREEN.
- [ ] Run the one authorized canonical update with exact change reference.
- [ ] Verify every generated file/directory host UID with both runner result and independent `os.stat` check.
- [ ] Inspect all 40 images, prioritizing four workspaces, four dossiers, both locales, and tablet overflow.
- [ ] Run compare mode, accessibility, RTL, keyboard, PDF, console/network, and responsive tests GREEN.
- [ ] Confirm 18 named browser tests / 122 nodes, unchanged matrix/tolerance/budgets.

**Confirm:** no known defect is captured.
**Validate:** baseline manifest provenance/change reference/ownership.
**Test:** `make e2e` and default visual contract tests.

### Task 11 — Documentation, final local evidence, and handoff

**Files:** Development Guide, limitations, traceability, progress, changelog, implementation/test records (the Implementer writes only records authorized by the Supervisor).

- [ ] Update docs exactly as §20, preserving pre-existing Supervisor hunks.
- [ ] Run mechanical Core 02 new-function map check and Sanad/source audit.
- [ ] Run fresh §24 gates in order.
- [ ] Audit `git diff --check`, full changed-path list, protected unchanged paths, v1 hashes, machine/human manifests, no untracked helper inclusion, and no secret path.
- [ ] Record actual outputs/assumptions/limitations; stop uncommitted for Supervisor review.

**Confirm:** every AC maps to actual evidence.
**Validate:** no self-approval or premature closure language.
**Test:** complete local gate set.

## 24. Verification commands

Run from the project root. No install, lock, baseline host update, or direct Docker command is part of this plan.

### 24.1 Focused default tests

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_public_snapshot_schema.py \
  tests/test_trade_metrics.py \
  tests/test_snapshot_migration_equivalence.py \
  tests/test_rules.py \
  tests/test_threshold_boundaries.py \
  tests/test_scenario_validation.py \
  tests/test_simulation_fidelity.py \
  tests/test_synthetic_isolation.py \
  tests/test_dossier_contract.py \
  tests/test_api.py \
  tests/test_integrity_contract.py \
  tests/test_authority_disclosure.py \
  tests/test_threshold_literals.py \
  tests/test_ui_catalogue.py \
  tests/test_visual_baseline_contract.py
```

Expected only after implementation: zero failures; warning output is recorded, not hidden. **[PROPOSED]**

### 24.2 Single authority generator G1

After all governed edits and the full pre-generation regression are green:

```bash
PYTHONPATH=src .venv/bin/python scripts/build_manifests.py
PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_integrity_contract.py
```

Execute this generator block exactly once in the planned path. A second run is allowed only for a later justified governed fix recorded under §18.6; it is not a routine retry or sequencing step. **[SPECIFIED]**

### 24.3 Functional browser before baseline

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
make e2e-functional
```

Expected only after implementation: all nonvisual nodes pass before update. **[SPECIFIED]**

### 24.4 One canonical baseline update

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S08-computed-rules-dossier-contradictions" \
make e2e-update-baselines
```

The Make target invokes the fixed container; it is not a host-renderer update. **[SPECIFIED]**

Independent ownership evidence:

```bash
PYTHONPATH=src .venv/bin/python -c 'import os; from pathlib import Path; roots=(Path("browser_tests/baselines/v0.3.0"), Path(".artifacts/e2e")); bad=[str(p) for root in roots for p in (root, *root.rglob("*")) if p.exists() and os.stat(p, follow_symlinks=False).st_uid != os.getuid()]; assert not bad, bad'
```

### 24.5 Compare and required proof

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
make e2e
PYTHONPATH=src .venv/bin/python scripts/check_prohibited_files.py
PYTHONPATH=src .venv/bin/python scripts/check_threshold_literals.py
PYTHONPATH=src .venv/bin/python scripts/check_ui_contracts.py
PYTHONPATH=src .venv/bin/python scripts/check_es_modules.py --node node
PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
make ci
```

The workspace rule's canonical aliases must also be represented in test evidence:

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/demo_smoke.py
```

### 24.6 Diff and history audits

```bash
git diff --check
git status --short
sha256sum \
  data/snapshots/public/historical/v1/SAU-H0-721049.json \
  data/snapshots/public/historical/v1/SAU-H0-390210.json
git diff -- \
  config/sector_profiles.v1.yaml \
  config/evidence_policy.v1.yaml \
  data/synthetic \
  docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
```

Expected protected diff: empty. Audit `config/thresholds.v1.yaml` separately and require only the authorized `1.1.0 → 1.2.0`, exact R4-D key/rationale/scope/date diff. Expected historical hashes: the two exact v1 hashes in §6.2. **[SPECIFIED]**

## 25. Rollback and recovery

- Before review/delivery, use ordinary file edits or a non-destructive `git revert`-style patch prepared by the authorized role; never use hard reset or checkout to destroy Supervisor-owned work. **[SPECIFIED]**
- If migration fails before G1, restore live v1 paths from the byte-identical historical copies and remove only unapproved v2 files; do not delete the sole v1 bytes. **[PROPOSED]**
- If G1 diff is outside the allow-list, stop, preserve logs, and restore the previous machine/human manifests from the branch diff; do not “fix” it by an unrecorded generator rerun. A second run requires a later justified governed source fix and the §18.6 record. **[SPECIFIED]**
- If the baseline update fails, the existing candidate/backup swap restores the previous oracle; verify ownership and compare before retrying the same authorized update. **[VERIFIED]**
- If updated baselines contain a defect, fix the product/test, rerun functional green, and request Supervisor authorization before another capture; the plan authorizes only one capture. **[SPECIFIED]**
- After merge, rollback is a new reviewed revert PR that restores the prior loader/rules/live snapshot paths/manifests/catalogue/baselines together. Historical v1 remains retained throughout. **[PROPOSED]**

## 26. Resolved questions

### OQ-01 — Arabic contradiction-register copy — RESOLVED

PR-03 approves the six exact Arabic strings in RT-08..13 as Supervisor-approved, owner-amendable defaults for catalogue 1.1.0. They must never be represented as owner-approved, and implementation may not vary them. ADR-012 and the PR record this attribution. **[SPECIFIED]**

### OQ-02 — R4-D row-path quantitative convention — RESOLVED

PR-02 approves quantity-weighted quartiles using named fractions, the farthest log-distance observation as explicitly non-confirmed `outlier_candidate`, and a dedicated `rules.R4_D.minimum_valid_value_coverage: 0.70` gate. Threshold metadata becomes 1.2.0 with the exact §7.3 rationale, scope, and revision date; tests bind `0.6999/0.7000/0.7001`, and the scanner must see the key. **[SPECIFIED]**

No open decision remains: SD-1 fixes identity/history, SD-2 fixes numeric provenance/disclosure fallback, SD-3 fixes baseline ownership scope, PR-01 fixes computed R11 semantics, PR-04 fixes single-run sequencing, and S09/S10 deferrals are explicit. **[DERIVED]**

## 27. Skills used

- `writing-plans`: used to produce one file-resolved, task-sized, test-first implementation plan at the user-specified path. **[VERIFIED]**
- `test-driven-development`: used to order characterization, RED observation, minimal GREEN implementation, and regression per behavior. **[VERIFIED]**
- `verification-before-completion`: used to distinguish planning baseline evidence from future implementation proof and to require fresh commands before success claims. **[VERIFIED]**
- `sanad`: used to classify consequential claims and tie decisions/numbers to repository authority. **[VERIFIED]**
- `muhasib`: used for the final scope/evidence/no-self-approval audit in §28. **[VERIFIED]**
- `task-standards` and `project-orientation`: used to adopt the established senior persona, inspect existing implementation before proposing new modules, and avoid duplicating the actual dossier/browser tests. **[VERIFIED]**

The generic `using-superpowers` skill explicitly exempts a dispatched subagent; it was read but not claimed as materially used. **[VERIFIED]**

## 28. Sanad ledger and Muhasib

### 28.1 Sanad ledger

Mechanical count command:

```bash
for tag in VERIFIED SPECIFIED DERIVED PROPOSED OPEN; do
  printf '%s ' "$tag"
  rg -o "\[$tag\]" \
    .workflow/slices/S08-snapshot-v2-computed-rules/plan.md \
    | wc -l
done
```

Mechanically synchronized counts:

- VERIFIED: `43`
- SPECIFIED: `135` (corrected by the Supervisor from the planner-stated 100 after a mechanical recount; RI-01)
- DERIVED: `18`
- PROPOSED: `63`
- OPEN: `0`

Interpretation: VERIFIED is directly observed repository/command state; SPECIFIED is governing authority, binding slice context, or the Supervisor's recorded rulings; DERIVED follows stated formulas/contracts; PROPOSED requires plan approval; OPEN is zero because PR-02 and PR-03 resolved OQ-02/OQ-01. No empirical figure is supported only by planner memory. **[VERIFIED]**

### 28.2 Muhasib pre-handoff audit

- Requested artifact: only this `plan.md`; no implementation, test mutation, staging, commit, push, PR, merge, or tag was performed. **[VERIFIED]**
- Authority: mandatory manifest/methodology/core/milestone/control/slice/code/data/test files and required skills were read; the DOCX remains authoritative and the Markdown mirror was used only as the required search aid. **[VERIFIED]**
- Scope: decision selection, S09/S10 work, acquisitions, threshold changes beyond PR-02's exact R4-D addition, scenarios, and unrelated UI work are excluded. **[VERIFIED]**
- Numbers: both exact JSON fixtures use only methodology/v1 values or explicit `UNAVAILABLE`; computed ratios are derived from those rows, and PR-02 resolves the quantitative convention. **[VERIFIED]**
- Baseline evidence: branch/HEAD/status, ignored `.env` status without contents, prohibited scan, integrity, `377 passed`, and smoke were observed during planning; none is represented as post-implementation proof. **[VERIFIED]**
- Working tree: pre-existing Supervisor-owned changes and untracked helper scripts are named and protected. **[VERIFIED]**
- Review boundary: this is a planner handoff, not approval. The Supervisor has ruled on OQ-01/OQ-02 and must review the revised plan to zero findings; the Implementer and independent Grok reviewer remain separate seats. **[SPECIFIED]**
- Residual risk: no planning decision remains open; new v2 hashes/bytes and post-change test counts are intentionally not invented, and implementation evidence remains future work. **[SPECIFIED]**

**Muhasib result: PASS for planning handoff; the Sanad ledger is mechanically synchronized and no file outside this plan was intentionally changed.**
