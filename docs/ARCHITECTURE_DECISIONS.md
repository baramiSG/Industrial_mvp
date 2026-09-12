# Architecture Decision Records

Decisions below are subordinate to the methodology DOCX, `docs/core/*` and `AGENTS.md`. They record how this build implements or operates around those authorities; they never redefine them.

---

## ADR-001 — Baseline import committed directly to `main` (one-time bootstrap exception)

**Status:** Accepted 2026-09-02.
**Context:** The workspace held the v0.1.0 package with no git history; the GitHub repository `baramiSG/Industrial_mvp` was private and empty. The owner mandate requires every change to flow through slice branches and PRs, which is impossible before a default branch exists.
**Decision:** The Supervisor imports the unmodified v0.1.0 package (minus Windows `*:Zone.Identifier` download artifacts) together with the build-control documents (`docs/BUILD_ROADMAP.md`, `BUILD_PROGRESS.md`, `REQUIREMENTS_TRACEABILITY.md`, `ARCHITECTURE_DECISIONS.md`, `KNOWN_LIMITATIONS.md`, `.workflow/`) as the first commit on `main`. No engine, config, data or test file is altered in that commit.
**Consequences:** All subsequent changes, including CI itself, go through `slice/SXX-*` branches and PRs. The exception is not repeatable.

## ADR-002 — Model separation implemented with Cursor native subagents

**Status:** Accepted 2026-09-02.
**Context:** The owner mandate specifies Windsurf/Cascade native subagents with distinct models for Planner/Implementer and Reviewer. This build runs in Cursor, whose native equivalent is the `Task` subagent with an explicit `model` parameter.
**Decision:** Supervisor = `claude-fable-5-1-thinking-max`; Planner/Implementer = `gpt-5.6-sol-max`; Independent Reviewer = `cursor-grok-4.6-xhigh`. Every dispatch names its model explicitly. If a model is unavailable, a *different* listed model is substituted and recorded in the slice record; the same model is never reused across the Implementer and Reviewer seats. If separation cannot be met, the slice is set to `BLOCKED_FOR_OWNER`.
**Consequences:** Every slice record names the models used. No subagent approves or merges its own work; the Supervisor is the final gate.

## ADR-003 — Shell execution delegated to shell subagents during a Supervisor tool outage

**Status:** Accepted 2026-09-02.
**Context:** The Supervisor's direct shell tool stopped returning results mid-session ("execution backend unavailable"), while subagent shells continued to work.
**Decision:** All commands (git, gh, uv, pytest, scripts) run through shell subagents given exact command lists; the Supervisor verifies outcomes independently by reading produced files, git metadata and GitHub API responses rather than trusting summaries.
**Consequences:** Every test-evidence record cites the subagent run that produced it and the verifying artifact the Supervisor read.

## ADR-004 — `uv` adopted as the developer/CI toolchain alongside the documented pip path

**Status:** Accepted 2026-09-02 (implemented and merged in S01).
**Context:** Firm rule SG-TR-007 requires dependencies and environments via `uv`. The delivered runbook (`README.md`, `START_DEMO_WSL.sh`, `Dockerfile`) uses `venv` + `pip`, and the Ministry demonstration instructions must keep working unchanged.
**Decision:** Add `uv.lock` and `uv`-based `Makefile` targets and CI steps; keep `pip install -e .[dev]`, `START_DEMO_WSL.sh` and the `Dockerfile` functional and documented. `pyproject.toml` remains the single dependency source.
**Consequences:** Two supported install paths; CI proves both remain installable.

## ADR-005 — Threshold values live only in versioned configuration; config edits go through the §7.3 gate with owner authority

**Status:** Accepted 2026-09-02.
**Context:** `AGENTS.md` #7 and Core 07 §9 forbid threshold duplicates in code. The v0.1.0 engine embeds `0.40` (route band), `1.25` (competition warning) and `50` (R11 export/import ratio, stated in methodology §14.2). The first two already exist as keys in `thresholds.v1.yaml`; the third does not.
**Decision:** Engine code reads existing keys for `0.40` and `1.25`. The R11 export/import ratio is added as `rules.R11.generic_capacity_export_import_value_ratio` with rationale, sector scope and revision date; `metadata.version` moves 1.0.0 → 1.1.0 (file name `thresholds.v1.yaml` retained as the v1 major line). Authority hashes are regenerated only through `scripts/build_manifests.py` inside the reviewed PR, with strict-boundary sensitivity tests and the golden regression proving both public outcomes and the steel simulated outcome unchanged. The owner's 2026-09-02 mandate is recorded as the methodology-owner approval for this operating-configuration change. An AST-based validator test fails the build if a threshold-bearing literal reappears in engine code.
**Consequences:** `test_threshold_is_loaded_from_versioned_config` asserts the new version string; the change is an explicit, reviewed authority update rather than a silent regeneration.

## ADR-006 — Simulated-state selection is data-driven from scenario content, not opportunity IDs

**Status:** Accepted 2026-09-02.
**Context:** The v0.1.0 simulation dispatches on the two packaged opportunity IDs, embeds simulated decision narrative in `decision_engine.py`, and reuses public `DISABLED` R6/R7/R8 rows. Core 06 §5.3 and §10 require explicit planted ground truth and an engine back-test; Core 07 §7.3 and §7.4 define generic ADVANCE and no-gap REJECT selection; Core 02 §3 requires internal evidence to resolve or explicitly abstain on R6/R7/R8. Synthetic scenario edits are governed snapshot/scenario-parameter changes under Authority Manifest §5, §7.3 and §8.
**Decision:** Version both packaged scenarios as `scenario_version: "1.1.0"` and declare that support once in code as `SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"1.1.0"})`. Add `ground_truth` with `expected_simulation_state`, `expected_route_code` and authority `basis`, and add state-keyed `decision_narrative` carrying the existing selected and INVESTIGATE fallback text verbatim. Ground truth and narrative never drive selection. One generic `_simulate` first applies Core 07 §7.4 (exact equivalence and qualified availability at least target demand → REJECT route 0), then §7.3 (positive gap, publishable D*, D* within the configured incremental-upgrade band, passing minimum-support economics, positive incremental national value and no competition warning → ADVANCE route 5), otherwise INVESTIGATE. Runtime and Gate B compare only actual/expected state and route and fail closed on mismatch. Simulated mode appends Class-D, generator-sourced, visibly labelled R6/R7/R8 rows; absent sustained-period, base-demand, probability and MES inputs remain `NOT_CALCULABLE`. The R6 shortage denominator is effective qualified capacity.
The owner's 2026-09-02 completion-build mandate is the methodology-owner approval for the two governed scenario metadata/narrative edits. No numeric scenario input, threshold, evidence policy, sector profile, public/golden snapshot, frozen core or methodology file changes. After complete regression and exact governed-diff review, `scripts/build_manifests.py` runs once; only the two synthetic snapshot-manifest entries and, if needed, generated dates may change.
**Consequences:** A conforming future scenario can use the same calculation/selection path without adding an opportunity-ID branch. A planted mismatch blocks the API with typed 422 and fails Gate B rather than changing the engine result. Public decisions and public ledgers remain untouched; simulated users and dossiers see both public rows and separately labelled synthetic R6/R7/R8 evaluations. R8 remains disabled for the packaged scenarios until governed base-demand/probability/MES inputs exist. The two public golden outcomes and all existing synthetic numeric results remain unchanged.

## ADR-007 — Merge gating is enforced by the Supervisor protocol, not GitHub branch protection

**Status:** Accepted 2026-09-02.
**Context:** `baramiSG/Industrial_mvp` is a private repository on a GitHub plan where branch-protection rules and rulesets are not available. The owner mandate forbids merging past red checks and forbids administrative overrides.
**Decision:** Before any merge the Supervisor runs `gh pr checks <pr>` and requires every job (`uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build`, `browser / Chromium / Python 3.12`) to be green on the current PR head, zero Supervisor findings and zero independent-reviewer findings, then merges with `gh pr merge --squash`. Cancelled or skipped jobs are not green. The PR record in `.workflow/slices/*/pr_record.md` captures the checks output.
**Consequences:** Enforcement is procedural and auditable through the slice records; if the repository later moves to a plan with rulesets, the same five checks become required checks.

## ADR-008 — Evidence-policy validation, public-marginal reconciliation and authority disclosure fail closed

**Status:** Accepted 2026-09-02.
**Context:** Core 06 §4 requires eight scenario metadata fields and fixes synthetic evidence as Class D with an explicit warning and generator source, while policy 1.0.0 lists only five required fields and code hard-codes part of the rule. Core 06 §5.1/§10 and Core 05 §8 require synthetic detail to reconcile to compatible public marginals, but no analysis or CI gate performs that reconciliation. FR-001 also requires methodology/snapshot identity per case; the detailed response exposes snapshot/as-of only. R5's configured retained-import-share threshold cannot be evaluated from gross flows without domestic-production and retained-import series.
**Decision:** Update `config/evidence_policy.v1.yaml` on its existing v1 major line from metadata version 1.0.0 to 1.1.0, effective 2026-09-02. Its required fields become `synthetic_flag`, `scenario_id`, `opportunity_id`, `display_label`, `seed_basis`, `evidence_class`, `source`, and `synthetic_inputs`; policy also declares `required_evidence_class: D` and `required_source: DEMO_GENERATOR` while retaining the exact display label. The evidence guard reads all controls from policy and raises `EvidenceIntegrityError` for every violation.

The same evidence guard deterministically reconciles target-spec demand to latest public import quantity, line nameplate to the sum of non-null disclosed producer nameplate, physical factors to [0,1], and declared qualified availability to nameplate × availability × yield. Equality passes. A FAIL blocks simulation before arithmetic; absent compatible blocks are reported as NOT_APPLICABLE. Demand-layer ordering is INFORMATIONAL because Core 04 requires layer separation but states no ordering gate. Tariff-line/buyer allocation is NOT_APPLICABLE until authority defines an executable JSON schema; no field or threshold is invented. Passing reconciliation is a plausibility control only and never upgrades Class D evidence.

`scripts/validate_scenarios.py` applies these same functions to every packaged scenario and matching public case with deterministic exits 0/1/2, and runs immediately after integrity in both Python CI jobs and `make ci`. Detailed API integrity failures return 422 JSON, never a partial 200 or 500.

Every detailed analysis adds one `authority` object sourced from `authority_hashes.json`, config metadata, and `project.yaml`: methodology file/full SHA-256/12-hex prefix, thresholds/sector-profile/evidence-policy versions, and project version. GenUI passes the object to the integrity banner; dossier JSON and printable HTML project the same object. R5 retains its degraded coexistence signal but reports the retained-import share as `NOT_CALCULABLE` with source reason and configured threshold.

The owner completion-build mandate dated 2026-09-02 is the methodology-owner approval for this Manifest §7.3 operating-configuration change. `scripts/build_manifests.py` runs exactly once only after focused and full regression, scenario validation, threshold scan, unchanged golden outcomes, and an exact policy-only governed diff. Generated changes are restricted to the evidence-policy hash/bytes plus `generated_on` in `authority_hashes.json`, and `generated_on` only in `snapshot_manifest.json`; the human Manifest §11 row is copied from generated JSON and verified with `sha256sum`.
**Consequences:** Malformed or unreconciled scenarios cannot reach simulation arithmetic or a successful detailed API response. Both current scenarios pass without editing `data/**`; both public golden outcomes and both simulated outcomes remain unchanged. Responses and exports become additively auditable. Future expansion-assumption or allocation bypasses require a governed schema decision. The stricter policy changes its hash and byte count, so authority JSON and the Manifest §11 evidence-policy row change under the single-generator gate.

## ADR-009 — Final acceptance hardening uses evidence-separated release gates

**Status:** Accepted 2026-09-02.
**Context:** S05 must close the carried S02–S04 review observations, measure NFR-005, prove all five user journeys and failure/reversal paths, publish final documents, and version the application without changing governed industrial logic. Initial residuals were an unmapped list-route `RepositoryError`/`ValueError`, non-recursive threshold-source discovery, one dead local, and missing characterization/performance proof. The different-model holistic review then identified uncontained SPA file resolution, workspace-wide packaging, N/A hard-gate prefix handling, an allocation over-claim, and missing economics keys defaulting to numeric zero. There is no runtime data-directory override, and adding one only to plant a live failure would broaden behavior.
**Decision:** Map list-route `RepositoryError` and `ValueError` to the same HTTP 404 contract as detail routes while retaining `EvidenceIntegrityError` as 422. Change only `Path.glob("*.py")` to `Path.rglob("*.py")` in the threshold scanner. Remove the unused `has_equivalence` local without changing the equivalence branch. Add exact tests for PP empty GenUI concentration, public zero-synthetic HTML, unchanged cached scenarios, list-route 404, recursive scan, and median-of-five NFR-005. Resolve SPA candidates and serve them only when they remain files under the resolved static root. Build source packages from the NUL-delimited `git ls-files` set and reject non-Git roots. Treat case-insensitive `resolved`, `not applicable`, and `not_applicable` prefixes as resolved hard-gate values. Require every declared national-value and EVSI numeric key; missing keys raise named `ValueError`s that simulation wraps as `EvidenceIntegrityError`. Add one 42-step final-acceptance runner that records per-step evidence but grants no approval. Keep planted evidence-integrity HTTP 422 proof at TestClient level because no approved runtime data-root override exists. Version the application distribution, lock root, and unhashed `config/project.yaml project.version` together at 0.2.0; all other config/data/core/methodology/golden/hash bytes remain unchanged and no manifest generator runs.
**Consequences:** Packaged public decisions, formulas, thresholds, scenarios, and evidence hashes are unchanged. PP simulated capability now publishes D* 0.0 in the immediate-adjacency band because its documented N/A tooling gate resolves, while exact equivalence still selects `REJECT` route 0 and Gate B remains the controlling back-test. Missing economics inputs fail closed instead of becoming zero. Static traversal and ignored-workspace archive inputs are excluded by construction. The list endpoint fails consistently, future Python subpackages enter the threshold scan, and residual safe behavior is regression-locked. Gate G is stated at API/static level under KL-22; cache stickiness and the R1-D confidence-cap string remain accepted as KL-29/KL-30. Local acceptance evidence, Supervisor review, different-model review, hosted CI, implementation merge, release-state merge, durable completion promotion, and tag remain separate gates.

---

## ADR-010 — Milestone v0.3.0: Core v2 authorization and binding owner rulings

**Status:** Accepted 2026-09-02 (owner decisions OD-1 and OD-2, approved with amendments).
**Context:** v0.2.0 (`ce5786b`, tag `v0.2.0`) is the accepted and frozen two-case technical demonstration baseline. The owner opened milestone v0.3.0 "Ministerial Demonstration Readiness" with required outcomes A–G (real-browser acceptance, public-universe screening, generalized case engine, material methodology gaps, real Neo4j graph, bilingual extraction, Ministry demonstration experience). The Supervisor's gap analysis (`docs/milestones/v0.3.0/GAP_ANALYSIS.md`) showed that these outcomes exceed the frozen Core 01–09 contracts and require interpretations of methodology terms that Manifest §10 forbids agents from choosing alone: the `MONITOR` condition, R3 on two bases, the R2 growth window, the ADVANCE gate inside simulation, route selection across routes 0–8, the gap-taxonomy classifier, hard exclusions, and the quantification of "what Ministry data unlocks".
**Decision:** The owner authorizes a Core v2 revision of `docs/core/01–09` under Manifest §7.4, slice by slice, each through its own ADR, PR and single `scripts/build_manifests.py` run after regression, with the methodology DOCX unchanged, the historical v0.2.0 release, tag and golden snapshot files untouched, and the steel `INVESTIGATE` / PP `REJECT` outcomes (and both simulated outcomes with their exact values) proven unchanged in every affected PR. Interpretations I2, I3, I4, I6, I7 and I8 are approved as written in `GAP_ANALYSIS.md` §7; I1 and I5 are approved as amended there. Six binding rulings apply to every slice (`GAP_ANALYSIS.md` §7A): R-1 `ADVANCE` is evidence-gated, never source-type-gated — real public Class A/B/C evidence passing every gate may reach `ADVANCE`, synthetic Class D may reach only `simulation_decision`; R-2 route 8 is `NOT_CALCULABLE` / `GRAPH_REQUIRED` until the real Neo4j dependency graph exists in S16, with no in-memory substitute; R-3 Neo4j is an idempotently rebuildable projection of canonical evidence records, never a second source of truth, with provenance, as-of date, evidence class and public/synthetic state on every decision-relevant node and edge and reproducible graph-fed results; R-4 S06 establishes real-browser functional/accessibility/network/console gates and reference screenshots, and the governed visual-regression baselines are set in S07 after the bilingual/token/module redesign; R-5 a routes 0–8 coverage matrix (case, binding constraint, lower routes rejected, evidence, expected and actual outcome) is audited in S22 and any undemonstrated route returns to the owner for explicit re-approval; R-6 Neo4j is provisioned by the build as a fresh project-owned, pinned (`neo4j:5.26.30` if compatible), health-checked service named `industrial-mvp-neo4j` with its own volume and network on non-conflicting host ports (preferably 7475/7688), idempotent deterministic initialization, no manually entered facts, synthetic exclusion in public queries, fail-closed `GRAPH_UNAVAILABLE`, a clean CI service with real Cypher integration tests, and generated credentials kept in a git-ignored runtime secret file (template only in Git; never printed). The slice graph and order `M3-P0 → S06 → … → S22` in `docs/milestones/v0.3.0/SLICE_GRAPH.md` are approved. M3-P0 is a docs-only PR; S06 implementation begins only after M3-P0 is merged with green default-branch CI.
**Consequences:** Every v0.3.0 slice that touches `docs/core/**`, `config/*.yaml`, `data/**` or a golden expectation cites this ADR and its own slice ADR as the methodology-owner approval basis, and still carries the full change-gate proof. The `MONITOR` state, screening dispositions `NO_CANDIDATE` / `SCREENED_OUT`, the amended route-selection rule (precedence gates then highest defensible incremental national value), and the real-ADVANCE capability become governing text in Core 07 v2 before they become code. The ADR-002 seat assignment continues (Supervisor Claude; Planner/Implementer GPT-5.6 Sol; Reviewer Grok 4.6) with finite ladders of four plans and eight implementation candidates per slice.

---

## ADR-011 — Bilingual interface foundation and governed visual oracles

**Status:** Proposed 2026-09-02; implementation candidate pending independent review and delivery.
**Context:** S07 implements the bilingual interface and visual-oracle work authorized by ADR-010 and owner ruling R-4. The existing interface fixes English chrome in HTML and JavaScript, uses physical-direction CSS and raw visual literals, relies on host fonts, exposes a demo link to CDN-backed `/docs`, and has documentary screenshots but no comparison oracle. Core 06 requires synthetic evidence to remain visibly and honestly disclosed. The engine currently emits English analytical narratives; S08–S10, not S07, own governed bilingual engine narratives.
**Decision:** Authority classification is Manifest §7.3 for evidence policy 1.2.0 and UI strings 1.0.0, and §7.4 for the minimal Core 01/02/09 v2 edits. The approval basis is owner-authorized ADR-010 plus the Supervisor's `PLAN_APPROVED`; plan-review rulings PR-03 and PR-04 approve the Arabic warning and digit/date presentation as owner-amendable defaults, not as owner-approved wording.

Add governed `config/ui_strings.v1.yaml` version 1.0.0 and serve complete validated bundles from `GET /api/ui-strings/{locale}`. Interface chrome is localized from that catalogue; synthetic warning text remains exclusively in `config/evidence_policy.v1.yaml` version 1.2.0 and is projected through `evidence.synthetic_display_labels`. The Supervisor-approved default Arabic warning is exactly `محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة`; it has not been represented as owner-approved and remains owner-amendable only through a later Authority Manifest §7.3 change. English engine-authored analytical text remains visibly captioned and isolated with `lang="en" dir="ltr"` in Arabic UI.

The locale contract uses URL `locale`, then `localStorage["ior.locale"]`, then English; sets document `lang` and `dir`; preserves unrelated URL state; and formats normalized analytical values with Western (`latn`) digits and Gregorian dates in both locales while preserving source spans verbatim. This presentation policy is a Supervisor-approved default under the S07 plan review and remains owner-amendable.

The browser frontend is decomposed into named-export ES modules below 200 physical lines. Raw visual values are confined to `static/css/tokens.css`; all component styles use design tokens and logical properties. Exact Fontsource Noto Sans and Noto Sans Arabic WOFF2 files and OFL licences are vendored locally. Text glyphs outside their governed Unicode ranges are rendered as accessible inline SVG or CSS symbols. The demo topbar `/docs` link is removed while FastAPI's engineer-only `/docs` route remains.

S07 establishes 40 lossless WebP baselines: ten principal screens across English/Arabic and 1440×900/1024×768. Opaque-RGB comparison uses one global rule: channel delta greater than 8 is significant, significant-pixel ratio must be at most 0.001, and mean absolute channel error must be at most 0.20. CI and normal `make e2e` compare only and never update. Updates require an explicit flag and change reference and run only in the digest-pinned Playwright 1.62.0 Noble image with network disabled and an asserted `chromium-1234` revision. The S06 documentary set is neither read nor modified.

Core revision markers are per-document during v0.3.0: changed Core 01, 02 and 09 documents open their 2.0.0 contract with the marker authorized by ADR-010; untouched Core files remain on the frozen prior contract until their owning slice changes them. After all pre-generation regression passes, `scripts/build_manifests.py` runs once; a second, recorded run is permitted only when a later governed catalogue edit within the same slice changes the catalogue hash (S07 ran it twice: the initial governed set, then the Supervisor-review fix that added the label/value catalogue pattern). The permitted generated diff is limited to the evidence-policy row, new UI-catalogue row, Core 01/02/09 rows and `generated_on` in `authority_hashes.json`; `snapshot_manifest.json` may change only in `generated_on`. The Authority Manifest §11 rows are copied from the generated JSON after each run.
**Consequences:** Locale switching and RTL behavior become testable application contracts without translating or altering decision semantics. Synthetic disclosures remain policy-sourced in both languages. Visual changes gain a deterministic reviewer-governed oracle; host-specific fonts and baseline auto-acceptance are not permitted. The steel public `INVESTIGATE`, polypropylene public `REJECT`, and both simulated outcomes remain unchanged. The authority edits are implementation evidence under ADR-010 and the approved S07 plan; they are not self-approval, owner approval of the Arabic wording, or delivery.

---

## ADR-012 — PublicSnapshot v2, computed public rules, and host-owned visual updates

**Status:** Proposed 2026-09-02; implementation evidence pending independent review and delivery.
**Context:** ADR-010 authorizes the milestone Core v2 revision. S08 removes the
schema-v1 `rule_context` flags that authored R4-D, R5, R9-S, R10, and R11
outcomes, implements the missing §3.3 physical-flow formulas and I2/I3
interpretations, and must preserve the two public and two simulated golden
outcomes. Supervisor decisions SD-1, SD-2, and SD-3 require byte-identical v1
history, no empirical value beyond methodology §§13–14, and correction of the
root-owned visual-update container before this slice regenerates its rendered
oracle. Plan-review rulings PR-01–PR-04 additionally fix computed R11
semantics, the R4-D coverage calibration, six catalogue strings, and one
post-regression manifest-generator run.

**Decision:** Classify Core 02/04/07/09 changes under Manifest §7.4. Treat the
two live snapshot rewrites as a representation migration adjacent to §7.5,
not an evidence refresh: the facts, source rows, `snapshot_id`, and
`as_of_date` remain unchanged; each schema `2.0.0` record points through
`supersedes` to a byte-identical v1 file under
`data/snapshots/public/historical/v1/`. The steel v1 file remains SHA-256
`10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7`
at 6,850 bytes, and the polypropylene v1 file remains
`cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948`
at 5,572 bytes. A true evidence refresh still requires a new identity and date.
The production loader is non-recursive, accepts only live schema 2.0.0, and
fails on unsafe history links, duplicate IDs, authored rule outcomes, invalid
domains, unresolved evidence references, or contradictory flow arithmetic.

Only methodology and frozen worked-case numbers enter v2. Missing partner
rows, quantity concentration, domestic production/retained/re-export flows,
and criticality remain exact `UNAVAILABLE`. Source-attributed calculated
concentration/dispersion disclosures are valid evidence inputs but never
rule outcomes. R2 uses the two latest usable observations and quantity CAGR
over their observed span. R3 calculates value and quantity independently.
R4-D calculates quantity-weighted quartiles, IQR, coverage, and a farthest
log-distance non-confirmed `outlier_candidate`, or uses an attributed
disclosure. R5 calculates retained imports, net exposure, apparent
consumption, and penetration per methodology §3.3 while naming every unknown.
R9-S uses typed process-family signals and known-failure gates. R10 uses a
responsible-authority designation or a degraded computed-R3 resilience review.
R11 always computes gross exports/imports from positive numeric row values,
retains any disclosed one-decimal ratio separately, and requires absolute
consistency within `0.05`. It fires only when the computed ratio strictly
exceeds configuration and a positive observed A/B/C producer nameplate
establishes domestic capability. Thus steel executes `FULL`/false at `0.1144`;
polypropylene executes `FULL`/true at computed `50.6013`, disclosed `50.6`,
consistent.

The dedicated R4-D operating calibration is Manifest §7.3:
`rules.R4_D.minimum_valid_value_coverage: 0.70`; thresholds metadata moves
1.1.0 → 1.2.0. Its exact rationale is: “Methodology §5.2.2 disables the
degraded diagnostic when comparable coverage is inadequate but states no
figure; the R4-F comparable-quantity coverage floor is adopted as the initial
R4-D gate.” Scope is `all`, revision/effective date is 2026-09-02, and
0.6999/0.7000/0.7001 plus recursive literal-scanner tests bind the change.

The additive contradiction-register catalogue change is Manifest §7.3:
`ui_strings.v1.yaml` 1.0.0 → 1.1.0. The six English/Arabic pairs for the
register heading, public subsection, synthetic subsection, public empty
state, public-mode synthetic state, and simulated synthetic empty state are
Supervisor-approved, owner-amendable defaults under PR-03; they are not
represented as owner-approved wording. Dossier JSON moves 1.0 → 1.1 and
separates public/synthetic contradictions. Public mode never scans an inactive
scenario.

The migration proof deep-compares all 15 ordered rule rows, fired/execution
values, response identity, and public state. Its explicit differences are the
steel R11 execution `DEGRADED` → `FULL`, steel compatibility ratio `null` →
`0.1144`, individually named additive R2/R3/R4-D/R5/R9-S/R10/R11 metric
keys, and the exact approved R3/R4-D/steel-R11 result text. No broad key filter
is used. `public_decision_contract` remains only because S09 owns generalized
state/route selection; S08 replaces its selector guard with computed
`R11.fired`.

For KL-32, the canonical baseline container runs with
`--user <host-uid>:<host-gid>`, `HOME=/tmp`,
`XDG_CACHE_HOME=/tmp/.cache`, and
`PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`; it asserts effective identity and
the host runner rejects any update output not owned by the host user.
Functional browser tests must be green before canonical update with change
reference `S08-computed-rules-dossier-contradictions`, followed by ownership,
image, manifest, and compare checks. The Implementer ran an initial update,
then a full-precision self-audit found that R3, R5, and R11 predicates consumed
rounded display metrics at near-threshold values. New RED tests proved the
defect; predicates were corrected to consume unrounded intermediates while
their public metrics remained four-decimal. Because the visual manifest hashes
all engine modules, a second corrective update under the same reference was
required after another 118-node functional pass. The rendered golden output
did not change; both update executions and the final ownership/compare evidence
are recorded rather than represented as one.

All governed hand edits precede one planned
`PYTHONPATH=src .venv/bin/python scripts/build_manifests.py` run after full
regression. The allowed generated diff is: two v1 snapshot rows moved to
historical paths with unchanged hashes/bytes; two new live v2 rows; changed
authority rows only for thresholds, catalogue, Core 02/04/07/09; and
`generated_on` only if the date changes. A later second run is allowed only
for a separately justified governed fix recorded before execution. The
visual-baseline updates are separate oracle generations, not manifest runs.

**Consequences:** Public rule outcomes are evidence-derived without product-ID
dispatch or authored flags; unavailable inputs remain unknown; unit values
remain descriptive; steel remains public `INVESTIGATE` and simulated
`ADVANCE` route 5; polypropylene remains public/simulated `REJECT` route 0.
The S12 acquisition slice still owns real public production and retained-flow
inputs, and S09 still owns generalized public decision selection. This ADR and
local green evidence are implementation evidence, not approval.

---

## ADR-013 — Generalized public decision engine and five sector profiles

**Status:** Proposed 2026-09-02; implementation evidence pending independent
review and delivery.

**Context:** S09 executes owner-approved amended I1 and I5, I6 and I7, and
rulings R-1 and R-2 (`GAP_ANALYSIS.md` §7/§7A; ADR-010). It removes the
temporary authored `public_decision_contract` while preserving the two public
and two simulated frozen outcomes. The governing basis is methodology §§1.2,
2.1, 4.2, 5.3, 6.3–6.6, 7.1–7.5, 8.2, 9, 12–15; Core 01/02/04/06/07/09; and
the Supervisor-approved S09 plan and plan review.

**Decision:** PublicSnapshot advances to 2.1.0 in place as a representation
migration: the frozen snapshot IDs, dates, empirical facts and historical-v1
bytes remain unchanged. The schema removes `public_decision_contract`, uses
controlled passport support codes, adds complete typed profile-hard-gate,
hard-exclusion and decision-input blocks, and rejects authored decision
outputs. The public engine computes four evidence-class assessments, executes
evidence-policy 1.3.0, all six typed exclusions, one primary §5.3 gap class,
typed rejection conditions, and the total amended-I1 state table. Missing
exclusion inputs remain `NOT_CALCULABLE` and never pass or reject.

Routes 0–8 are emitted as ordered hypotheses. A fully resolving lower route
blocks escalation; otherwise selection uses greatest unrounded incremental
national value with an exact tie resolved to the lower code. Financial
support follows unsupported and applicable non-financial routes. Route 8 is
always `NOT_CALCULABLE` / `GRAPH_REQUIRED` until S16 supplies the governed
Neo4j projection. Where economics are absent, the engine may emit an
evidence-grounded preferred hypothesis without selecting a formal route.

Evidence needs are selected by controlled need code and evidence-state
predicate, never by case, producer or profile identity. Public decision text
is rendered from `decision_narratives.v1.yaml` 1.0.0 with exact English/Arabic
key and placeholder parity and structured escaping boundaries. The Arabic
decision narratives are Supervisor-approved, owner-amendable defaults under
the S09 plan review. They are not represented as owner-approved or as official
Ministry wording. Scenario-specific simulation narratives remain exclusively
in each scenario's `decision_narrative`; `_simulate` state, route and numeric
semantics are unchanged.

`sector_profiles.v1.yaml` advances to 1.1.0 with the methodology §6.3
pharma/API, fertilizers and fabricated-aluminium profiles. Every profile has
the same nine dimensions, weights summing to 1.0 and its complete frozen
hard-gate set. A non-hard-gate dimension at state 3 contributes to D* but does
not itself suppress publication; unresolved or failed configured hard gates
do.

The governed visual baseline reference is
`S09-generalized-public-decision`. After all governed hand edits, 118
functional browser nodes, four visual nodes and the complete pre-generation
browser-independent regression passed, the Implementer ran
`scripts/build_manifests.py` exactly once. The snapshot manifest changed only
the two live public rows. The authority manifest changed only Core
01/02/04/07/09, evidence policy, sector profiles, and the new decision
narrative catalogue row. Historical public snapshots, both synthetic
scenarios, extraction golden data, thresholds, UI strings, methodology and
Core 03/05/06/08 remained byte-identical. The complete hashes and byte counts
are recorded in Authority Manifest §11 and the S09 test evidence.

**Consequences:** Steel remains public `INVESTIGATE`, with null formal route
and route 5 as the preferred hypothesis; polypropylene remains public
`REJECT` route 0. The packaged steel simulation remains `ADVANCE` route 5 with
all frozen calculations unchanged, and the polypropylene simulation remains
`REJECT` route 0. A synthetic-free test fixture proves that actual A/B/C
public evidence can reach real `ADVANCE`; it is proof of technical capability,
not a demonstration evidence artifact or public authorization. Generalized
simulation, screening-universe dispositions and graph activation remain S10,
S13 and S16 respectively. This ADR and local evidence are implementation
evidence, not approval.

### Correction round 2026-09-03

Under approved plan `.autonomous-workflow/plans/s09-public-decision-and-profiles/plan-7.json` (owner-delegated ruling 2026-09-03T05:25Z): added `signals.py` with `may_support_advance` configuration guard; eight-step deep-state order with `ADVANCE_SUPPORT_SIGNAL_DEGRADED` and `ROUTE_DETERMINATION_UNRESOLVED`; typed rejection narratives and 16 reviewer-gated catalogue keys (94→110); route-determination INVESTIGATE including mocked-loader missing-economics proof with unchanged PublicSnapshot validator boundary (KL-36); MONITOR route-0 consistency; fired-rule confidence cap; second justified `build_manifests.py` run; fifth canonical visual execution `S09-generalized-public-decision-corrections` with zero WebP drift.

## ADR-014 — Generalized simulation branch and scenario contract 2.0.0

**Status:** Proposed

**Context:** S10 generalizes simulated route evaluation on scenario contract
2.0.0 while preserving frozen public goldens and byte-identical historical 1.1.0
scenarios under `data/synthetic/historical/v1_1/`.

**Decision:** Accept owner-amendable defaults for Arabic catalogue strings and
`minimum_efficient_scale_kt: 50.0` on the steel packaged scenario. Runtime
supports only 2.0.0 scenarios with bilingual narratives, ten Gate B reconciliation
checks, simulated R5/R8 ledger semantics, route-8 `GRAPH_REQUIRED`, and
`CLASS_IF_CONFIRMED` advance gating. Manifest regeneration uses
`scripts/build_manifests.py` with recursive synthetic JSON discovery.

**Authority classes (Manifest §7):**

- **§7.3 operating configuration:** synthetic scenario parameters advance to
  contract 2.0.0 (`data/synthetic/SYN-MINISTRY-STEEL-001.json` and
  `SYN-MINISTRY-PP-001.json`); `decision_narratives.v1.yaml` 1.1.0;
  `evidence_policy.v1.yaml` 1.4.0.
- **§7.4 methodology/core text:** Core 01/02/04/06/07/09 v2 edits under
  ADR-010/ADR-014; Core 06 opens with the standard v2 marker on line 3.
- **§7.2 implementation-preserving refactors:** route evaluation and
  `classify_gap` refactors with unchanged public goldens.

**Permitted generated diff:** `authority_hashes.json` rows for
`docs/core/01_PRODUCT_AND_REQUIREMENTS.md`,
`docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`,
`docs/core/04_CANONICAL_DATA_MODEL.md`,
`docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md`,
`docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`,
`docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`,
`config/decision_narratives.v1.yaml`, `config/evidence_policy.v1.yaml`, and
`generated_on`; `snapshot_manifest.json` rows for the two live synthetic files,
two new rows `data/synthetic/historical/v1_1/SYN-MINISTRY-PP-001.json`
(sha256 `06517bb9…`, 3,433 bytes) and
`data/synthetic/historical/v1_1/SYN-MINISTRY-STEEL-001.json`
(sha256 `8867f083…`, 4,711 bytes), and `generated_on`. Every other manifested
file remains byte-identical.

**Manifest regeneration:** Candidate 2 (T13) ran
`scripts/build_manifests.py` once after all governed engine/config/core edits.
Candidate 3 runs it once more because T12 corrected
`docs/core/01_PRODUCT_AND_REQUIREMENTS.md`; the second generated diff is
restricted to that Core 01 authority row and `generated_on` unless another
manifested file changed in the same correction.

**Consequences:** Public decisions remain unchanged. Simulated surfaces mirror
`simulation_decision` including bilingual narratives and counterfactual blocks.
Further graph activation remains deferred to S16.

## ADR-015 — Public acquisition framework, raw evidence store and reconstruction proof

**Status:** Proposed

**Context:** S11 implements operator-only public acquisition for trade, tariff and BACI sources with deterministic raw storage, source-partitioned snapshots, acquired evidence passports, and offline reconstruction proof, without changing frozen public goldens.

**Decision:** Adopt the locked engineering defaults DD-20 (1)–(9):

1. `raw_store.max_artifact_bytes_compressed` = 16777216 and `max_store_bytes_compressed` = 100663296 in hashed YAML only.
2. Default evidence class B and reviewer status `unconfirmed_by_responsible_authority` for all configured sources.
3. Live guard env var `IOR_ACQUISITION_LIVE` must equal `1` for any fetch.
4. Reconstruction with zero snapshots exits 1 before manifest checks; missing manifest rows exit 2; hash mismatch exits 1.
5. `--years` required on `acquire-universe`, `acquire-partners` and `acquire-baci`; `--max-requests` required on every acquire command; `acquire-tariff` takes no `--years` because the tariff tree is one period-free contract (DD-5/DD-19); rationale recorded in implementation log (no code defaults).
6. Rate-limit floor from source config `min_interval_seconds`.
7. Selection rule `LATEST_RUN_PER_SOURCE_STAGE_UNIT` (DD-21).
8. BACI BULK raw-only — no analytical snapshot kind (DD-22).
9. Completeness accounting per DD-18; truncated pagination never writes universe/tariff snapshots.

**Reconstruction exits (DD-11):** default `--all` checks every snapshot and referenced raw artifact path against `snapshot_manifest.json`; library `reconstruct()` returns `SELECTION_CHANGED` when latest store run differs from snapshot coverage.

**Stop conditions (DD-17):** Stop A when zero real artifacts exist; Stop B when zero normalized analytical snapshots exist after parsers.

**Module placement (recorded plan-3 deviation, DELIVERY-F-01):** the acquisition configuration loader (`acquisition/source_config.py`: `ACQUISITION_SOURCES_PATH`, `acquisition_sources_config()`) and the three read-only acquired-snapshot loaders (`acquisition/repository.py`: `universe_snapshots()`, `tariff_snapshots()`, `partner_snapshots()`, `clear_acquisition_caches()`) live inside `src/ior_mvp/acquisition/` instead of `config.py` and `data_repository.py`, where plan-3 `files.modify`/DD-15 placed them. The governed visual oracle (`browser_tests/visual_baselines.validate_manifest`) pins the SHA-256 of every top-level `src/ior_mvp/*.py` module in `browser_tests/baselines/v0.3.0/manifest.json` `source_tree` and fails closed on drift, while the same plan freezes `browser_tests/baselines` byte-identical to base `a610b49` (verification[4], AC7, T12, non-goals). Both hold only when `config.py` and `data_repository.py` remain byte-identical to base. DD-15 semantics are preserved (`lru_cache`, fail-closed validators, test-double rejection, cache clearing); no byte under `browser_tests/baselines/` changes in S11, and `tests/test_frozen_public_evidence_pins.py` pins that tree and runs `validate_manifest()` directly in the pytest gate.

**Manifest regeneration:** candidate 1 ran `build_manifests.py` prematurely before T10 authority artifacts; the final justified run follows T10 completion and updates Core 02/03/04/05/09 hashes only from governed doc edits plus acquisition config.

**Consequences:** Acquired snapshots are not consumed by the engine until S13/S14. Frozen public and synthetic outcomes remain exact.

**Verification contract for stored evidence (plan-4, owner ruling 2):** Under `.autonomous-workflow/owner-decisions/s11-acquisition-trade-tariff-2.json` (SHA-256 `1c52d3dbdc44b3c908fb35b9caf499bb010a07cf57887264df7d674507eb0b86`), production raw evidence is never required to carry a redaction marker. DD-23 defines the stored-evidence verification contract: source partition, header hygiene against `offline_guard` allow/deny lists, honest credential field names, and CREDENTIAL_ABSENT semantics (null `observed_response`, zero requests, sibling `coverage.json` equality, no page artifacts). Redaction is proven in-memory with a deterministic non-secret sentinel in tests only; a marker appears only where a credentialed request actually occurred. DD-24 adds a credential-echo fail-closed guard in `BaseConnector._fetch`: if a response body contains a non-empty secret value, the connector records `OUT_OF_SCOPE_CONTENT` with `error_type` `CredentialEchoed` and stores no page. Existing CREDENTIAL_ABSENT records in `data/raw/**` are the honest absence path and are never edited.

**Shallow-stable frozen-tree pins (plan-6, owner rulings 3 and 4; DD-25/DD-26):** Under `.autonomous-workflow/owner-decisions/s11-acquisition-trade-tariff-3.json` (SHA-256 `94bb3fee66652726d0d84047edf307dd7535a3ea2b7a1a66df1369997c082fb8`), `tests/test_frozen_public_evidence_pins.py` pins the four frozen evidence roots by Git tree OID (`HEAD:<root>` compared to `2ad27d6eaa9b3ce474f2c9ed62ecaa873ecd5e04`, `3fb2247a36b57b85fc0f966717aad5502aa25f4b`, `72618db654110823ec7a8d4dd6415a37e4554e33`, `9f334b8d820778638d13afdd80b4087a85189bc0`), requires `git diff --quiet HEAD` over those roots, rejects untracked paths there with `git ls-files --others` (no `--exclude-standard`, because runtime loaders glob those directories), and preserves the existing SHA-256 byte `PINS` and PIL-free visual-provenance mirror. The predicate is shallow-stable: depth-1 CI checkouts materialize `HEAD` and its root trees regardless of fetch depth, so `.github/workflows/ci.yml` stays byte-identical. The pinned OIDs are frozen evidence identities changeable only through Manifest §7 with a new approved plan. CI-F-01 on PR #14 (`acc00092`) was a plan/test-mechanism defect (`git diff a610b49` on a shallow clone), not a frozen-byte change — the bytes were and are identical. This paragraph supersedes the earlier description of pinning the baseline tree by base-commit diff; the pytest gate mirrors the oracle's provenance check PIL-free and pins the tree by OID. Plan-5 (`.autonomous-workflow/plans/s11-acquisition-trade-tariff/plan-5.json`, SHA-256 `de5f9e1a7ec56a1bfe159a77785b8dc55cfddafa6354e7bc3ac5915c73fccba2`) was rejected on P5-F01 — its broad delta-surface verification treated ignored build artifacts as untracked frozen-surface content — and superseded by plan-6 under owner ruling 4 (`.autonomous-workflow/owner-decisions/s11-acquisition-trade-tariff-4.json`, SHA-256 `dc68d130a43bc7cb61abc5412de7f0f00c3c6149ad45e41fe61fd8a31d5f45d6`) with the four-root no-exclude-standard untracked rejection and every product obligation unchanged.

## ADR-016 — Institutional acquisition framework and honest source outcomes (S12a)

**Status:** Implementation evidence under the directly owner-approved plan; final review, generated integrity, PR/CI and delivery remain pending at T9 authoring (2026-09-11). ADR-015's historical Proposed status is unchanged.

**Authority:** Owner ruling `.autonomous-workflow/owner-decisions/20260911-owner-direct-s12a-implementation.md`; immutable amended plan `.autonomous-workflow/plans/s12a-acquisition-framework-institutional-sources/cycle-1/plan-5-owner-approved.json`, SHA-256 `b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64`, based on `a043ed8dc1d477de50149b39de657bc963e785d7`. The original methodology §§2/3/11, Core 04/05/09 and Manifest §7 govern evidence meaning. The owner cancelled plugin orchestration and directly approved implementation: ordinary command logs replace plugin evidence capture; superseded verification[22] is not executed or called PASS. No fabricated plugin/reviewer receipt or automatic commit is substituted. Final session review, PR with green CI and owner merge approval remain separate.

### Decisions DD-1–DD-20

| Decision | Adopted contract and boundary |
|---|---|
| DD-1 | StageSpec/STAGE_SPECS and KindSpec/KindRegistry centralize stage and kind behavior; derived SNAPSHOT_ROOTS/KIND_STAGE preserve existing importers. Generic builders, loaders and reconstruction accept the registry; PipelineDeps gains a default kind registry. |
| DD-2 | Stage remains a governed fail-closed StrEnum, extended by AGGREGATE, DIRECTORY and REGISTRY, not arbitrary strings; five S11 stage specifications preserve unit keys/dicts and hashes. |
| DD-3 | Institutional QueryContract reuses existing fields: SAU reporter, UNAVAILABLE partner/flow, NOT_APPLICABLE product scope, no product codes, config nomenclature, one aggregate year or no directory/registry periods. Canonical sorted named parameter pairs identify units without name/value collisions; duplicate/reserved parameters fail closed. |
| DD-4 | Store-time classify_page stamps NORMALIZED only on recognized nonempty parser output, UNPARSED/no_rows_parsed on unknown/failed parsing, PENDING only when no parser exists; TERMS remains UNPARSED and BACI parserless. Existing S11 parsers are reused. Stored classification is immutable. |
| DD-5 | One generic row builder validates actual connector quality, selects latest units, verifies coverage, normalizes rows, derives as-of from stored retrieval, sorts deterministically and builds source-partitioned passports. Universe/tariff require all units complete; partners and institutional kinds require at least one complete unit plus matching exclusions. Existing wrappers remain. |
| DD-6 | Coverage verification rebuilds the actual QueryContract embedded in stored pages and re-evaluates coverage; mismatches fail instead of rewriting evidence or relaxing the S11 oracle. |
| DD-7 | Token-generic URL formatting reads observed mappings safely, never dereferences the UNAVAILABLE sentinel or guesses missing token names. Initial unit/template checks precede terms or budget; continuation URLs are checked before charging. Unsatisfied templates/tokens yield ENDPOINT_UNVERIFIED. |
| DD-8 | gastat → AGGREGATE/production; ministry_of_industry and modon → DIRECTORY/directory; saso_catalogue and saber_registry → REGISTRY/registry. Core 04 pins source-qualified IDs without nomenclature segments, roots and schema 1.0.0; one snapshot per kind/source. |
| DD-9 | Default evidence classes are gastat B, ministry_of_industry B, modon C, saso_catalogue B, saber_registry C; all reviewer defaults remain unconfirmed_by_responsible_authority. Aggregation, licence, catalogue and registry support limitations never become confirmed capacity/compliance facts. |
| DD-10 | ProductionObservation, DirectoryRow and RegistryRow are exact Core 04 field whitelists. Published text remains original/UNAVAILABLE; numeric production parsing does not convert units or map HS; directory capacity stays text; registry rows have no compliance/qualified/approved flags; no person-name/phone/email fields. |
| DD-11 | DOMESTIC_PRODUCTION_AGGREGATE, ESTABLISHMENT_LICENCE_DIRECTORY and STANDARD_CONFORMITY_REGISTRY extend only ACQUIRED_SUPPORT_CODES, following NATIONAL_TARIFF_LINE_MAPPING; public SUPPORT_CODES and engine projections remain unchanged. |
| DD-12 | Acquisition config is 1.1.0 with exactly nine sources; institutional exact key sets add parameters.units. Seventeen observed-fact paths use one UNAVAILABLE string sentinel until observed. Sentinel-first validation shares S11 predicates, validates mappings/lists and recorded_on, requires licence capture for unknown access and recursively forbids secret keys. The reserved credential sentinel is rejected for S11. |
| DD-13 | Thin acquire_aggregates/directory/registry wrappers use StageSpec planning; plan_requests retains terms + len(units). CLI requires explicit source/budget and aggregate years only; Make requires explicit live intent and not CI. Builds accept registered kinds or all, fail closed on unknown kinds, and remain offline. |
| DD-14 | The owner-approved DIRECTORY/REGISTRY pre-storage privacy policy is exact, declared-MIME-driven and text-only; bounded label matching and hash-only refusal take precedence over apparent completeness. S11 stages and TERMS remain unchanged. |
| DD-15 | Real complete normalized units may yield snapshots; stored UNPARSED text permits offline parser work but requires a fresh bounded acquisition for normalized metadata; attempts with honest existing reasons are acceptable terminal evidence and cited in KL. No invented production parser/test-envelope branch; current source parsers return [] because no live shape was acquired. |
| DD-16 | Core additions preserve unique line-3 markers and historical pins. Core05 §3.1 is byte-identical, GASTAT trade remains connector planned; exactly five §3.2/§3.3 status cells append the approved code-coverage sentence without adding a column or changing the six other rows. Core03 §4.11 and Core09 §5 each add one item, at most three lines and zero deletions. |
| DD-17 | Control records reconcile S11 MERGED/PR14/a043ed8 with the exact CI fallback “see PR #14 checks”; record the approved S12 split and S12a IMPLEMENTATION_EVIDENCE, never invented IDs, approvals or completion. Historical S05/v0.2.0 and S11 traceability remain intact. |
| DD-18 | Snapshot and every passport stamp KindSpec.config_version: 1.0.0 for universe/tariff/partners, 1.1.0 for production/directory/registry, regardless of current YAML metadata. PIPELINE_VERSION stays 1.0.0. The pin names the governing source-contract semantics; moving it needs §7.3 and later §7.5 evidence, never an edit to stored history. Stored page contracts gain no config_version. Existing _run_units connector construction remains metadata-version-based because it cannot determine stamps and BACI has no kind. |
| DD-19 | configured_credential_env_var(None/empty/UNAVAILABLE) means no lookup, no Authorization header, stored null/false credential fields. Observed missing credentials retain CREDENTIAL_ABSENT. Honest refusal order remains credential → endpoint/unit → access/terms; unknown access returns LICENSE_UNRECORDED only after endpoint validation. |
| DD-20 | The stored-evidence detector shares configured_credential_env_var with runtime; sentinel-configured sources must have null/false stored credential fields and cannot claim CREDENTIAL_ABSENT. Canonical pre-observation doubles share the single sentinel recipe with config/runtime tests. |

**DD-12 operating versus source facts:** fixed non-fact values derive from Core05/S11 precedent: authority is each source's own institutional catalogue row (not GASTAT foreign trade), reporter_code SAU, existing project user-agent, licence capture true, the DD-9 classes/reviewer defaults, and client operating floor 2.0 seconds / max_attempts 3 / timeout_seconds 60. These are §7.3 operating settings, not documented source rates. Null credentials and empty token/pagination mappings mean observed absence, not “unknown”; all seventeen unobserved fields use UNAVAILABLE. An observed field requires an actual consultation date. T7 changed only observed documentation/access/policy fields and recorded_on; every data endpoint, unit, data MIME, pagination and API credential contract remains UNAVAILABLE. GASTAT/SASO/SABER have limited OBSERVED documentation facts; Ministry/MODON remain PRE_OBSERVATION despite actual consultation dates.

**Repair provenance:** plan-1 F-01 is addressed by DD-18 per-kind stamps; plan-1 F-02 by DD-12 phased validation and DD-19 runtime refusal; plan-1 F-03 by non-destructive exact verification commands. Plan-2 F-01 is addressed by the single sentinel, helper sharing and runtime/detector proofs in DD-12/19/20. No hidden dictionary/credential defaults replace unobserved facts.

### Binding amendments AM-1–AM-9

| Amendment | Required implementation/proof |
|---|---|
| AM-1 | Canonical sorted named pairs, period participation, collision-free unit identity, duplicate/reserved-key refusal, S11 byte compatibility and filesystem/latest-run proof. |
| AM-2 | Existing partner exclusion aggregation is reused through a stage-aware helper; institutional exclusions name their own stage, S11 partner output unchanged. |
| AM-3 | Initial unit and every referenced template token verified before terms, request-budget charge or transport; continuation validation also precedes charging. Actual budgets/calls/headers prove refusal order. |
| AM-4 | Injected kind registry and data root support TEST-KIND build/write/load/reconstruct; bypassed/isolated caches cannot poison default loads. Top-level modules remain frozen. |
| AM-5 | Exact privacy policy before DIRECTORY/REGISTRY storage and actual row/source/geography quality validation before snapshot PASS; no nonempty-only validation and no deferred Comtrade fixes. |
| AM-6 | FORBIDDEN_KEYS traversal includes nested mappings and lists at every depth; exact institutional config shape and units rules preserve S11 behavior apart from the approved credential sentinel restriction. |
| AM-7 | If a pre-generation filtered gate is needed, exclude only the integrity-contract module and the single manifest-coupled reconstruction test, never the entire reconstruction module; full post-generation pytest has no exclusions. FakeTransport records headers for observable credential proofs. |
| AM-8 | New command parsers/dispatch live only in acquisition/cli.py; __main__.py remains byte-identical; module tests use offline/test roots. |
| AM-9 | Explicit owner narrowing: DD-15(b) retained-UNPARSED parser work applies only to text passing the guard. PDF/XLSX and non-UTF-8/legacy encodings are outside this path; no parser can recover an unstored body. Unknown inspectable text remains UNPARSED, not PENDING. |

**Privacy boundary:** Core05 §10 records the exact executable policy: DIRECTORY/REGISTRY data only after HTTP-error handling; binary MIME refusal, strict UTF-8/BOM inspection and prohibited-control rejection, then one declared-MIME envelope (JSON recursive keys, CSV/TSV first nonblank header, HTML th/named form controls, otherwise opaque text). No expected-content-type routing, body sniffing, fallback, replacement decoding, OCR or decompression. Exact case-split/NFC/casefold/separator normalization precedes twenty English boundary-suffix aliases (optional ar/en/text) and fourteen Arabic whole-label aliases; contact_id/contact_id_number are intentionally allowed. Null-valued labels count; values/prose are not classified. This is not universal personal-data detection. OUT_OF_SCOPE_CONTENT with PersonalDataFields or UninspectableTextPayload stores only status, filtered headers, byte count, body SHA-256 and constant safe error metadata, never body or matched label/value; prior pages remain and INCOMPLETE refusal coverage overrides apparent completion, with embedded/sibling coverage equality. A future unstored refusal must not be mislabeled FORMAT_NOT_PARSEABLE. None occurred in T7's zero-request acquisitions.

### Actual operator parameters and outcomes (T7, 2026-09-11 UTC)

The source is the coordinator's pre-run commands, rationales and emitted RunReports in `.workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md`; these are not suggested defaults.

| Command / source | YEARS | MAX_REQUESTS | run_id | Query hash |
|---|---|---|---|---|
| acquire-aggregates / gastat | 2025 | 2 | 20260911T215546Z | e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d |
| acquire-directory / ministry_of_industry | period-free | 1 | 20260911T215956Z | b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f |
| acquire-directory / modon | period-free | 1 | 20260911T215956Z | 94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135 |
| acquire-registry / saso_catalogue | period-free | 2 | 20260911T220134Z | 9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49 |
| acquire-registry / saber_registry | period-free | 2 | 20260911T220134Z | e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3 |

Every invocation used IOR_ACQUISITION_LIVE=1 with no CI/.env read and the existing locked local toolchain. Units were UNAVAILABLE, producing one explicit unverified unit. GASTAT's 2025 comes from the observed IPI methodology year, not physical production/retained-flow inference. Budgets 2 allowed one unit plus a documented terms-capture allowance; Ministry/MODON budget 1 was the minimum unit bound without an observed terms URL. Every application exited 3 (Make 2), requests_made=0, pages_fetched=0, coverage INCOMPLETE / ENDPOINT_UNVERIFIED, observed response/stop null, no data body or snapshot. Exact write-once attempt paths and consultation limitations are KL-47–51; sibling coverage matches. Separate website consultations are never represented as acquisition responses. No second run or parser invention was justified.

GASTAT website reuse/documentation was observed but not a data contract; Ministry connectivity and MODON certificate failures yielded no usable directory documentation; SASO API-documentation reachability/scope tension left access unknown; SABER account-based platform terms did not establish a bearer API or enumeration endpoint. No paid standard, authenticated dataset or personal data record was acquired. These bounded failures do not prove absence of public data.

Offline build-all exited 0 and named only the existing WITS partner snapshot. Every institutional kind/source build returned COVERAGE_INCOMPLETE. Existing partner reconstruction passed 1 snapshot / 4 artifacts; institutional reconstruction is TESTED with temporary doubles only. The T7 live window is CLOSED. Live source/R5 inputs remain BLOCKED, not zeros or proxy observations; engine consumption stays S13/S14. The pre-existing RunReport cumulative aggregate-count issue remains deferred; emitted zero counts here are retained, without a general claim that report totals equal transport calls.

### Change classes and single manifest-run authorization

- **§7.2:** table-driven framework and S11 compatibility refactors; frozen S11 raw/partner/passport/reconstruction and top-level engine behavior unchanged.
- **§7.3:** acquisition config 1.0.0 → 1.1.0 adds five sources and the exact phased contract; DD-9 class defaults, client operating values and per-kind config pins have the explicit rationale above. S11 source mappings, existing operating thresholds, sector profiles and evidence policy remain unchanged.
- **§7.4:** owner-approved additive Core03/04/05/09 acquisition-contract wording, with existing version/date markers and frozen decision meaning preserved; no methodology DOCX or public decision schema/support vocabulary change. This ADR records the approved gate, not independent permission for another methodology change.
- **§7.5:** five new write-once attempt/coverage pairs under the institutional data/raw prefixes. No institutional analytical snapshot was produced; no frozen/public/synthetic/golden/browser record is replaced.

At T9 authoring, **manifest run count = 0**. This ADR records rationale and permission before the **single planned T11** `scripts/build_manifests.py` invocation, after T9 review and T10 regression. The owner-direct substitution removes plugin ceremony, not verification. Before generation, preserve exact canonical frozen checks [4]/[5] and reconstruction [3]; after the one run, mirror the authority §11 table and run [12] immediately, then all post-generation integrity/reconstruction/full-suite/delivery gates, including [17] at T12. The allowed generated authority changes are only acquisition config and Core03/04/05/09 hashes plus generation metadata; snapshot manifest adds the actual institutional raw files and only any genuinely produced authorized snapshots (none at T9). All S11 and frozen rows remain byte-identical; [12] checks that exact delta. Manifest §11 table mirrors machine rows, never invented hashes. The pending run is not recorded as executed; the coordinator must append its actual result separately. Do not regenerate again to conceal mismatch or refresh browser provenance.

### S12 split and deferred scope

The approved parent assessment `.autonomous-workflow/plans/s12-acquisition-institutional-documents/cycle-1/decomposition-1.json` hashes to `ad234d819270e40b63ef2e12fff435379e9e412630feda3e0c5629dcd887dbd7`; the S12a leaf assessment hashes to `158590b4e07f5f8d548adb0675e3a43d7172227a2962a8a73f21287026f722b8`. Exact goals/dependencies are copied to BUILD_ROADMAP's “S12 split (SLICE_GRAPH §5)” and milestones.v0.3.0.split: s12a institutional framework/rows (inherits S11), s12b span-addressed documents/disclosures/tenders (depends on s12a), s12c bilingual persistent entity resolution (depends on s12a and s12b). Parent completion requires all three children; S12a is not further split. No document store, PDF extraction, persistent entity IDs, extraction metrics, graph, UI or downstream engine projection is delivered here. Top-level historical COMPLETE/S05 records and ADR-015 remain historical; S11 traceability stays TESTED. S12a is IMPLEMENTATION_EVIDENCE, not merged or fully delivered.

**T11 execution receipt (2026-09-11 22:31:25 UTC):** After independent T9 APPROVE and passing T10 gates, the coordinator ran `PYTHONPATH=src python3 scripts/build_manifests.py` exactly once (exit 0), mirrored the five changed authority rows into Manifest §11, and immediately passed canonical [12] (`MANIFEST_S11_ROWS_UNCHANGED`). Snapshot manifest: 73 rows, ten new institutional attempt/coverage files, all 63 prior rows unchanged. Authority manifest: 16 paths, only acquisition config and Core03/04/05/09 rows changed. Snapshot-manifest SHA-256 `96a98f278a532aed1bad42707da8d2a5a682b4113e64fce6505b284c1e9c45c5`; authority-manifest SHA-256 `42706ee68e8364715093ec86cb0841ab57aaf08270d61cac762cc10f62ab7ec3`. The single-run authorization is exhausted; T12 verification and session implementation review remain pending at this receipt. Exact logs are in the S12a slice test evidence; this is not PR/CI/merge approval.

## ADR-017 — Document store, text layer and honest publisher outcomes (S12b)

**Status:** Implementation evidence under the owner-approved plan; final review, generated integrity, PR/CI and delivery remain pending at T9 authoring (2026-09-12). ADR-016 remains the governing institutional framework record.

**Authority:** Immutable plan `.autonomous-workflow/plans/s12b-document-store-disclosures-tenders/cycle-1/plan-1.json`, SHA-256 `c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`, based on `cdfd4ba4b016619b7ab33a373d334f22c337166d`. Core 04/05/09, acquisition config 1.2.0 and Manifest §7 govern evidence meaning. Owner OD-8 (IAC-13) accepts plan-deviation pin updates to `tests/test_browser_harness_contract.py` and `tests/test_visual_baseline_contract.py` for the `pypdf==6.16.1` dev extra only.

### Decisions DD-1–DD-22 (S12b)

| Decision | Adopted contract |
|---|---|
| DD-1 | Documents are an acquisition **stage** with parallel derived records under `data/documents/**`, not a snapshot kind. Raw bytes use unchanged BaseConnector/RawStore/coverage/passport machinery. |
| DD-2 | `Stage.DOCUMENT` — one contract per recorded URL; parameters `(document_url, …)`; fail-closed token validation. |
| DD-3 | Seven document sources at config 1.2.0: `tadawul_disclosures`, `etimad_tenders`, `saso_documents`, four producers; sixteen source ids total; S11/S12a mappings untouched. |
| DD-4 | `pypdf==6.16.1` pinned in the **dev** extra only; PDF extraction uses layout mode; import failure raises `TextLayerDependencyError`, never UNAVAILABLE. |
| DD-5 | Versioned derivation methods and `LINE_SEGMENTATION_V1`; every physical PDF page retained in order; per-page `text_sha256 = sha256("\n".join(lines))`; COMPLETE requires a non-whitespace line; verbatim lines and no normalisation. |
| DD-6 | Envelope policy stores exactly PDF/HTML/XHTML/plain; other types refused pre-storage as `UnsupportedDocumentEnvelope`. |
| DD-7 | Stage-aware `_pre_storage_refusal`; S12a DIRECTORY/REGISTRY guard unchanged. |
| DD-8 | Size budgets unchanged; oversize is honest UNAVAILABLE. |
| DD-9 | `DOCUMENT_ID_V1` identity scheme; identical bytes → ALREADY_STORED. |
| DD-10 | DocumentStore layout, write-once lists/records, root guards. |
| DD-11 | **DocumentRecord 1.0.0** exact field contract (Core 04 §7.4), with latest-run-per-unit selection and actual sorted superseded run ids. |
| DD-12 | **DocumentList 1.0.0** — explicit operator lists, hashed, never edited after a run. |
| DD-13 | One Class-target passport per record; existing support codes only. |
| DD-14 | Config 1.2.0 shape and phased validator for document sources. |
| DD-15 | DocumentConnector on BaseConnector with list-driven units. |
| DD-16 | Raw-store extension mapping for document content types. |
| DD-17 | Pipeline, CLI (`acquire-documents`, `build-documents`), Makefile targets, reconstruct/build_manifests wiring. |
| DD-18 | Honest per-entry UNAVAILABLE/RAW_ONLY outcomes are complete slice outcomes. |
| DD-19 | Additive Core 03/04/05/09 wording; marker-preserving; verification literals [22]–[24]. |
| DD-20 | Control records cite facts only; slice IMPLEMENTATION_EVIDENCE in state/progress/traceability. |
| DD-21 | Runtime image and top-level `src/ior_mvp/*.py` remain free of `pypdf`; document modules remain offline-import clean. |
| DD-22 | No prose personal-data screening on document bodies; bounded schema restriction applies to DIRECTORY/REGISTRY rows only. |

**IAC-13 plan deviation (OD-8):** `tests/test_browser_harness_contract.py` and `tests/test_visual_baseline_contract.py` pin the exact dev-extra dependency list including `"pypdf==6.16.1"`. No other unplanned files may change.

### T7 operator windows

**T7-v1 (slot 1, history):** seven single-URL consultations; seven empty `-v1` lists; seven zero-request ENDPOINT_UNVERIFIED runs retained.

**T7-v2 (slot 2, 2026-09-12 ~05:18–05:23 UTC):** read-only publisher navigation; seven `-v2` lists (`producer_unicoil` and `saso_documents`: six verified PDFs each; others: empty with honest summaries). All v2 acquire runs made `requests_made=0`: `LICENSE_UNRECORDED` where entries existed (terms UNAVAILABLE); `ENDPOINT_UNVERIFIED` elsewhere. No DocumentRecord built. Duplicate slot-1 tadawul runs (`20260912T050943Z`/`050946Z`) retained without logged reason (SR-04); duplicate v2 unicoil/saso timestamps from repeated Makefile invocation in the same window.

**T7-v3 (slot 3, SR-06 correction, 2026-09-12 05:35:06–05:40:21 UTC):** read-only terms consultation for SASO acceptable-use policy (200, usage/disclaimer terms observed), SASO open-data page (200, reuse terms observed) and UNICOIL privacy policy (200, PDPL personal-data terms only — no document reuse terms). Config updated: `saso_documents` terms/rate-limit recorded from acceptable-use policy; `producer_unicoil` `license_capture_required: false` (ZATCA precedent). `-v3` lists authored with verbatim displayed link text (SR-07: SASO entries replaced with industrially relevant technical regulations). Re-runs: `saso_documents-v3` run `20260912T053622Z` — 6 COMPLETE records, RunReport `requests_made=27`; `producer_unicoil-v3` run `20260912T053955Z` — 6 COMPLETE records, RunReport `requests_made=21`. Those two RunReport figures are the deferred S11/S12a **aggregate-count artefact**, not transport counts: `pipeline._run_units` sums the per-unit `coverage.requests_made`, and each unit's coverage echoes the cumulative shared `RequestBudget.used` at its completion (SASO 2+3+4+5+6+7 = 27; UNICOIL 1+2+3+4+5+6 = 21). The stored page contracts prove **7 transport fetches** for `20260912T053622Z` (1 TERMS `text/html` + 6 `application/pdf`, `MAX_REQUESTS` 7) and **6** for `20260912T053955Z` (6 `application/pdf`, `MAX_REQUESTS` 6, `license_capture_required: false`); neither run exceeded its budget. The aggregate-count logic and emitted T7 records remain unchanged; slot 5 later changes only DocumentList propagation into minimum-request accounting (KL-65). All twelve records `text_layer.status=COMPLETE`, `quality_summary=PASS`.

Consultation connectivity (project user agent, read-only): `sabic.com` 200; `unicoil.com.sa` 200; `tenders.etimad.sa` 200; `saso.gov.sa/en` 200; `saudiexchange.sa` 403; `tasnee.com` no TCP; `advancedpetrochem.com` no DNS.

### Independent review findings and correction round (slot 4, `implementer-fable`, OD-10/OD-11/OD-12)

`reviewer-grok` REJECTED candidate `87084ed2…` (194 files) with two HIGH findings; both were adjudicated VALID by the owner lead agent and corrected on the same uncommitted tree without network access.

**S12B-IR3-F01 — visual-order Arabic and wrong `languages` (disposition OD-12, option (a) of the reviewer's required correction):** all six COMPLETE `saso_documents` records store the publisher's Arabic lines in visual (painted, left-to-right glyph) order under `PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0` — e.g. the authority-name cover line is stored as `ةدوجلاو سيياقلماو تافصاوملل ةيدوعسلا ةئيهلا`, whose character reversal reads `الهيئة السعودية للمواصفات…`. The method stores the PDF content-stream text order verbatim; `quality_summary: PASS` denotes a COMPLETE extracted text layer, not logical reading order; logical order is guaranteed only where the PDF's ToUnicode mapping yields it (the CID fixture pinned by `test_arabic_cid_pdf_preserves_logical_order_verbatim`, unchanged and green). No bidi reordering or reshaping is applied (non-goal; DD-5/OD-6); logical-order recovery is S20 normalisation. The disclosure is recorded in Core 04 `### DocumentRecord 1.0.0` ("Text order (PDF)"), the Core 05 §10 DOCUMENT paragraph and KL-64. The `-v3` list declared `languages: ["en"]` for the six `/ar/` PDFs whose derived text is Arabic; inspection of the derived text (Arabic/Latin line and character counts per record, slice log) gives `["ar","en"]` for E-001, E-003, E-004 and E-006 (English standard titles in annex tables) and `["ar"]` for E-002 and E-005 (Latin content limited to the publisher name, footer URL and parenthetical English equivalents). Under **OD-11** the six uncommitted v3-built records were replaced by records built offline from the corrected list `saso_documents-v4` (SHA-256 `16d9e29bd86f720c38a29ffcd7a24e5140c94a2893226fac7f67183a3a4338bb`; same URLs, order and verbatim texts as v3) against the SAME stored run `20260912T053622Z` — no new acquisition. The rebuilt records carry the same six `document_id`s and identical `pages`; they differ from the removed records only in `list_ref.{path,sha256,list_id}`, `declared.languages` and the passport copy `evidence[0].observation_context.languages` (removed-record SHA-256s in the slice log). The UNICOIL records' `["en"]` declarations were inspected and found truthful (0 Arabic characters). Proving tests: `tests/test_acquisition_document_records.py` (repository-tree, read-only; RED against the pre-correction tree, GREEN after).

**S12B-IR3-F02 — aggregate-count artefact wording:** the T7-v3 paragraph above, KL-65, the slice log and `test_evidence.md` now state that RunReport `requests_made` 27/21 are the deferred aggregate-count artefact and that the stored page contracts prove 7 and 6 transport fetches; the parenthesis that glossed 27 as one TERMS page plus six documents was removed. The aggregate-count logic and emitted T7 coverage records are unchanged; the later slot-5 `pipeline.py` correction only passes the DocumentList into minimum-request accounting. Read-only test: `test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count`.

**Advisories:** A02 stale BUILD_PROGRESS line corrected; A03 hook tests pin `PersonalDataFields`, `UninspectableTextPayload` and the literal `Response refused by institutional text-only privacy policy; body not stored`, and `DocumentConnector._pre_storage_refusal` now delegates DIRECTORY/REGISTRY to `super()` (behaviour unchanged; institutional test files byte-identical); A05 `expected_content_types` set to the observed `[application/pdf, text/html]` (`saso_documents`) and `[application/pdf]` (`producer_unicoil`) from the stored page contracts; A07 candidate identity recomputed by the IAC-6 procedure. A01 (one UNICOIL payload begins with an `HTTP/1.0 200` header block before `%PDF-1.4`; stored as-is under the no-sniffing rule, pypdf parses the embedded PDF, reconstruction matches) and A04 (per-URL consultation tuples live in the hashed lists and stored contracts) remain accepted observations. Slot 5 closes A06 with the exact plan-named `test_document_observed_values_must_satisfy_shared_rules`.

### Change classes and manifest-run authorizations

- **§7.3:** acquisition config 1.1.0 → 1.2.0 adds seven document sources; S11/S12a mappings unchanged.
- **§7.4:** Core 04 DocumentRecord section, Core 05 rows/§6.6/§10/§11, Core 03 §4.11 and Core 09 §5 insertions (this ADR records rationale).
- **§7.5:** new `data/documents/**` list files and `data/raw/{document-source}/**/attempt.json` (+ coverage) pairs; the initial T7-v1/v2 cutoff had no COMPLETE document payloads, while the later T7-v3 correction window produced the twelve COMPLETE records described above.

At T9 authoring, **S12b manifest run count = 0** (S12a exhausted its single run). One `scripts/build_manifests.py` invocation is authorized after T10 regression; mirror §11 immediately; run [14] before T12. Allowed generated changes: acquisition config 1.2.0 and Core03/04/05/09 hashes plus new manifest rows for actual document/raw artifacts. S11/frozen rows remain byte-identical.

**T11 first execution receipt (2026-09-12 05:26:47 UTC, slot 2):** After T10 regression, the coordinator ran `PYTHONPATH=src python3 scripts/build_manifests.py` exactly once (exit 0), mirrored five changed authority rows into Manifest §11, and immediately passed [14] (`MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`). Snapshot manifest: 161 rows (+88 document/raw attempt-coverage/list files; all 73 prior rows unchanged). Authority manifest SHA-256 `de8c0206c579aaa8a4e269f912fc05357b175bf037e72f57da08332f54927a11`; snapshot-manifest SHA-256 `62b1ae00433ffcb8a741796124f230fb05cc322dc66dcd88c2c99d0eb16e9122`.

**OD-9 second manifest run (owner-authorized, slot 3):** The first T11 generation preceded the SR-06 corrected T7-v3 operator window. Exactly one further `scripts/build_manifests.py` invocation is authorized after the v3 re-runs and T10 regression; [14] must pass immediately after. S12b manifest run count must be exactly 2 when slot 3 completes; no third run is authorized.

**T11 second execution receipt (2026-09-12 05:43:02 UTC, slot 3 OD-9):** After T7-v3 re-runs and T10 regression, `PYTHONPATH=src python3 scripts/build_manifests.py` ran exactly once (exit 0); §11 mirrored; immediate [14] PASS (`MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`). Twelve DocumentRecord rows and v3 acquire payloads added to snapshot manifest; S11/S12a/frozen rows unchanged. OD-9 authorization exhausted (2/2 runs at that point).

**OD-10 third manifest run (owner-authorized, slot 4):** the second generation hashed the six v3-built SASO records, the v3 lists and Core 04/05 text that the independent review found untruthful (F01/F02). Exactly one further `scripts/build_manifests.py` invocation was authorized after the F01/F02 corrections (v4 list, six replaced records, Core 04/05 disclosure, A05 config values) and the T10 regression, followed immediately by [14]; OD-10 itself authorized no fourth run. Reasons for those three runs: (1) 05:26:47Z — planned T11 after T10, before the SR-06 corrected operator window; (2) 05:43:02Z — OD-9, after the T7-v3 re-runs produced the twelve records; (3) OD-10 — after the reviewer-driven F01/F02 corrections replaced six derived records and changed governed text/config.

**T11 third execution receipt (2026-09-12 06:37:37 UTC, slot 4 OD-10):** after the T10 regression (1871 passed, 1 deselected) and gates [0], [1], [3]–[13], [22]–[26] (+ corrected [25]) on the corrected tree, `PYTHONPATH=src python3 scripts/build_manifests.py` ran exactly once (exit 0); the three changed authority rows (`config/acquisition_sources.v1.yaml` `bf45f2e7…` 20,093 B; `docs/core/04_CANONICAL_DATA_MODEL.md` `3f7a06c5…` 20,942 B; `docs/core/05_DATA_SOURCES_AND_INGESTION.md` `11c45ada…` 21,912 B) were mirrored into Manifest §11; immediate [14] PASS (`MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`). Snapshot manifest: 214 rows (213 + the `saso_documents-v4` list row; the six SASO record rows carry the rebuilt hashes); S11/S12a/frozen rows unchanged; authority path set unchanged. Snapshot-manifest SHA-256 `4fb8592d1b9d1e67c82d22dc3cd7a90ca9ebfb62d08117a818819858d29764c4`; authority-manifest SHA-256 `79015f4cee58ca3e61b5fd1ce28bc5543c54b0556c899eb1895b66d0835f8364`. At that point S12b manifest run count was **3 of 3 then authorized** (05:26:47Z, 05:43:02Z, 06:37:37Z). Post-generation: [14]–[20], [22]–[26] PASS; full `pytest -q` 1888 passed / 1 warning; `make ci` exit 0 (118 functional + 4 visual). Exact logs are in the S12b slice test evidence; this is not PR/CI/merge approval.

### OD-13 final correction round (slot 5, `implementer-sol`)

OD-13 validates three derived-record contract defects found in the OR-3 residual sweep: the page hash used canonical line-array JSON instead of `sha256("\n".join(lines))`; empty PDF pages were dropped and later pages re-indexed; and the builder wrote an empty `superseded_run_ids` list instead of selecting the latest run per unit with actual prior run ids. Slot 5 corrects these test-first, retains every physical PDF page and its 1-based index, rebuilds all twelve records offline from the existing raw runs without changing document ids, and records the sorted superseded runs. It also closes residual DD-5/DD-12/DD-14/DD-17 contract gaps: exact CR/LF segmentation, HTML template/noscript suppression and block tags, DocumentList entry ordering and ISO date, exact document-source nested config keys and the plan-named observed-value test, DocumentList-aware request minimums, strict nested record keys, and `build-documents --data-root` semantics.

**OD-13 fourth manifest run (owner-authorized, final):** exactly one final `scripts/build_manifests.py` invocation is authorized only after the corrected code, records, governed text and T10 regression are green, followed by the §11 mirror and immediate [14]. This is the fourth and last run of S12b; no fifth run is authorized. The four reasons are: (1) planned T11 at 05:26:47Z before SR-06; (2) OD-9 at 05:43:02Z after the twelve records were acquired; (3) OD-10 at 06:37:37Z after F01/F02 corrections; (4) OD-13 after correcting the page-hash, physical-page and superseded-run contracts and rebuilding all twelve records.

**T11 fourth execution receipt (2026-09-12 07:30:41 UTC, slot 5 OD-13):** after the corrected T10 regression passed 1904 tests with one intentional deselection, `PYTHONPATH=src python3 scripts/build_manifests.py` ran exactly once (exit 0). The Core 04/05 authority rows were mirrored into Manifest §11 and immediate [14] passed (`MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`). Snapshot manifest: 214 rows, SHA-256 `86328f39e9a2a44668184b1bedf4a2609bf58b34eb405d714ac51d69dfc353cb`; authority hashes: 16 rows, SHA-256 `f6d681f481be7f7b8ae57b025865e15b423e5e6387bb8e624049d296826c5100`. S12b manifest run count is **4** (05:26:47Z, 05:43:02Z, 06:37:37Z, 07:30:41Z); authorization is exhausted and no fifth run may occur.

### OD-14 independent-review correction and accepted observations

Fable review of candidate `94eb2f4e…` found two defects. Under OD-14, slot 5 implements `HTML_TEXT_LAYER_STDLIB 1.0.0` as literal DD-5 emission (`"\n"` at both boundaries of every `BLOCK_TAGS` member, including `td`/`th`, with suppressed-element data discarded) and pins exact fixture/table/nested/list output. `DocumentStore` now applies the raw-store `_PATH_UNSAFE` rule to every source/list/document path segment, applies the DD-10 list-id pattern before pipeline or CLI I/O, and proves traversal rejection before any transport fetch. All twelve stored records are PDFs, so these corrections require neither record rebuilding nor a fifth manifest run.

- **A01/A07:** `DOC-PRODUCER-UNICOIL-cec488bffcda-3017de71d962` reconstructs the publisher bytes exactly, including their `HTTP/1.0 200` preamble before `%PDF-1.4`; the no-sniffing policy preserves that envelope (KL-66).
- **A02:** `validate_document_record` proves the plan-named negative cases but does not yet validate every status-dependent literal or call the shared passport assertion; this is accepted as a future fail-closed hardening item, not evidence that the stored records are invalid.
- **A03:** unused locals/parameters, repeated derivation during reconstruction, dynamic-import style and the literal `pypdf==6.16.1` result string are accepted maintainability observations; the pinned dependency and current records remain deterministic.
- **A04:** an empty physical PDF page is represented by `lines: []` and `line_count: 0` under DocumentRecord 1.0.0, as Core 04 already states; changing that versioned edge case requires a future governed Core change.
- **A08:** DD-2's `{}` token shorthand has an implementation carve-out: `_document_url_tokens` returns the already validated `document_url` from the contract, and BaseConnector permits that reserved overlap only for `Stage.DOCUMENT` before the same contract parameter is applied. This preserves fail-closed URL validation while leaving every other stage's reserved-name rule unchanged.
- **A09:** the CID test does not pin its third Arabic-only line; repository-loader renamed-file/wrong-partition negatives and a two-prior-run supersession test are also absent. Existing implementation paths and stored superseded lists were independently verified; these are accepted additional-test opportunities.
- **A10:** the two successful public document sources retain the conservative hashed `credential_env_var: UNAVAILABLE` sentinel despite unauthenticated HTTP 200 observations. Recording `null` would require a later Manifest §7.3 authority change and is not authorized in OD-14.

## ADR-018 — Deterministic bilingual entity resolution (S12c)

**Status:** Implementation evidence under owner decision OD-9 and approved immutable plan `plan-1-dispatch1.json` (SHA-256 `6370547fc85f7124b658312681311063e485350edb2d3f80f864c2ffb82b10cd`). Independent implementation review, generated integrity, PR/CI and merge remain separate gates.

| DD | Adopted contract |
|---|---|
| DD-1 | Separate `ENTITY_ID_V1` namespaces for `COMPANY`, `PLANT`, `LINE` and `LICENCE_HOLDER`; observed exact-name keys, parent/locality or designation for plant/line, and no id re-issue. |
| DD-2 | Versioned `NAME_NORMALISATION_V1` exact/variant rules in `config/entity_resolution.v1.yaml`; verbatim spans retained and visual-order Arabic never reversed. |
| DD-3 | First-match precedence: deterministic identifier, exact document evidence, pending review, unresolved; no fuzzy score or AI proposal. |
| DD-4 | Ownership, name-change and merger statements become dated, deduplicated records; unnamed owners remain unresolved. |
| DD-5 | `data/entities/{mentions,resolution}/` is a guarded write-once §7.5 root, not a snapshot kind; repository test doubles are refused. |
| DD-6 | `EntityMentionList 1.0.0` records exact addresses and spans; all spans verify against stored lines or JSON values before writing. |
| DD-7 | `EntityResolutionArtifact 1.0.0` records deterministic entities, links, input hashes, counts and transformation provenance. |
| DD-8 | Document and addressed frozen-snapshot passports plus producer observations link only through governed mentions; exact URL equality alone records corroboration. |
| DD-9 | Artifacts, mention lists, rules and inputs reconstruct byte-for-byte under manifest checking. |
| DD-10 | Core 03/04/05/09 additions preserve markers and historical S12a/S12b blocks. |
| DD-11 | Boundary tests use injected Class-D doubles outside repository evidence roots; defaults validate real inputs. |
| DD-12 | Control records state observed facts and do not impersonate review or delivery approval. |
| DD-13 | Offline `build-entities --mention-list-id` dispatches before acquisition dependencies; pipeline/document/connector modules stay unchanged. |
| DD-14 | `mentions-v1` contains M-001…M-038. The real artifact has five companies, two SITE_LOCALITY plants, no lines/licence holders, 27 exact links, three pending and eight unresolved. |

The companies are Universal Metal Coating Company (alias UNICOIL), Hadeed, SABIC, Advanced Petrochemical and Tasnee. Both plants belong to the first company at `SAU-JUBAIL` and `SAU-JEDDAH`. Pending links are M-009 `LOCALITY_VARIANT`, M-017 `SUBJECT_OUTSIDE_WINDOW` and M-020 `VARIANT_NAME_EQUALITY`; M-007 is count-only and M-021…M-027 are out-of-scope SASO mentions. One 2004 unnamed-owner record cites M-004/M-012. `DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0` and `DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a` have no readable mention. The 1997 founding-shareholder sentence and HPD page 20 lines 9–12 are deliberately excluded under OD-7 and the personal/contact-span boundary.

**Change classes:** §7.2 adds offline modules/tests; §7.3 adds `config/entity_resolution.v1.yaml` and grows the authority path set 16 → 17; §7.4 adds approved Core text; §7.5 adds the mention list and resolution artifact. Frozen public/synthetic/golden/browser evidence, S11/S12a/S12b records and the methodology DOCX remain unchanged.

At T7 authoring, **S12c manifest run count = 0**. Exactly one `scripts/build_manifests.py` run is authorized only after ADR-018 and the T8 regression. The generated seventeen-row authority table is then mirrored into Manifest §11 and [14] runs immediately. A failure stops the slice without regeneration or hand editing; the actual UTC receipt is appended only after execution.

**T9 execution receipt (2026-09-12T11:25:47Z):** after the T8 regression (`2008 passed, 1 deselected, 1 warning`) and exact [0]–[13]/[21]–[26] gates passed, `PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/build_manifests.py` ran exactly once and exited 0. Immediate [14] passed: `MANIFEST_S11_S12A_S12B_ROWS_UNCHANGED_ENTITIES_PRESENT 2`. The snapshot manifest added only `data/entities/mentions/mentions-v1.json` and `data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json`; every prior row remained identical. The authority path set grew from 16 to 17 with `config/entity_resolution.v1.yaml`; only the four approved Core rows changed among prior authority paths. Manifest §11 mirrors all 17 generated rows. S12c manifest run count is **1**, authorization exhausted; no second run is permitted.

## ADR-019 — Public-universe acquisition and screening engine (S13a)

**Status:** implementation evidence under approved plan
`plan-1-s13a.json` (`9d1f8134…`) and owner-approved amendments AM-1 (`d562ddca…`) and AM-2 (`88abbab2…`).
Independent implementation review and delivery remain pending.

**Decisions DD-1–DD-18:** acquisition config 1.3.0 introduces the optional
validated custom credential-header name while storing no value; the official
UN Comtrade v1 universe contract is accepted only on dataset/count/scope/
classification/duplicate proof; AM-1 retains per-row `hs_revision` and one
revision per `(year, flow)` without changing the pinned generic snapshot
builder; W0–W3 are bounded operator windows; stage-two partner acquisition uses
only engine-emitted R2 survivors; screening is an offline subpackage with a
runtime transport-import boundary; per-HS6 projection preserves unknowns;
governed rule builders and threshold YAML are reused; dispositions are typed
and never formal decisions; the two cited product families are the only
populated memberships and no unsupported plant link is authored; five queues
use route-specific Pareto ordering with §8.2(c) `NOT_CALCULABLE`; the
write-once ScreeningSnapshot hashes every input; API summary/queue/record
contracts serve unavailable state without 500; AM-2 stores it as a directory
with a 48 MiB per-file and 100 MiB total budget; reconstruction checks every
file and input offline; controls preserve every frozen public/synthetic/golden/browser and
S11/S12 byte; Core 01/02/03/04/05/07/09 record the contracts.

**Observed windows:** W0 received the developer sign-in shell and a bounded
public preview with `count=500`, 500 rows and top-level
`count/data/elapsedTime/error`; it did not establish terms, pagination,
provider limits, all-partners token or a ZATCA data endpoint. W1 run
`20260912T134009Z` therefore recorded eight `LICENSE_UNRECORDED` units, zero
requests and no universe. OD-10 then authorized one corrective round. W0-bis
observed the official policy, subscription and key pages at
`uncomtrade.org/docs/`: Basic Individual limits are 100K records per call,
500 calls per day and 5 calls per second. Partner-all, pagination and
comma-separated command-code batching remained unobserved. W1-bis run
`20260912T141128Z` stored eight normalized responses; each provider `count`
equalled its stored-row count (3,651–5,061 rows), with `H5` in 2021 and `H6`
in 2022–2024. All eight units nevertheless remained
`INCOMPLETE / COVERAGE_INDETERMINATE`, because count equality without an
official pagination/completeness contract does not satisfy DD-3. No universe
snapshot or candidate list was built; W2 remained closed at zero requests,
and W3 remained closed. The corrected fallback snapshot is honestly
`UNAVAILABLE` with reason `COVERAGE_INDETERMINATE`, zero records/queues, and
5,279 bytes; the empty evidence-bound plant-family list is 118 bytes. W1-bis
stored 1,094,392 compressed bytes across the policy page and eight universe
responses; no universe or UN Comtrade partner snapshot file exists. OD-7 was
not triggered.

**Authority change classes:** Manifest §7.3 adds screening/product-family
configuration and acquisition config 1.3.0; §7.4 changes the seven Core files;
§7.5 adds W1/W1-bis raw and coverage records and screening artifacts. The
planned T11 manifest generation ran once on 2026-09-12, exited 0 and passed
the immediate integrity/20-test oracle. The implementer's later T12
self-review correctly found invalid product-family profile IDs, incomplete
four-year availability enforcement, wrong Make target names and wrong state
nesting. OD-10 authorized one corrective round and exactly one second and
final generation after those fixes, the W0-bis/W1-bis evidence, governed text
and regression. That second run is required solely to hash the authorized
corrections and new evidence; it must be followed immediately by the manifest
oracle. **OD-10 execution receipt:** the second and final invocation ran at
`2026-09-12T14:21:10Z`, exited 0, updated the generated manifests and §11
mirror, then immediately passed `INTEGRITY PASS` and all 20 manifest-contract
tests. S13a manifest run count was **2** at that gate: the first planned T11
receipt on 2026-09-12 and this OD-10 corrective receipt.

**OD-11 completeness correction:** official subscription documentation states
verbatim “max 100K records per call”, “500 calls/day” and “5 calls per
second”. `pagination.kind=NONE`; a unit is complete only when provider
`count` equals stored rows and is below 100,000, with an empty error, reporter
682, contract period/flow/partner, six-digit HS6, one classification and no
duplicate HS6. Run `20260912T143742Z` proved all eight 2021–2024 import/export
units complete (3,651–5,061 rows each; H5 in 2021, H6 thereafter), producing a
24,195,845-byte universe with 5,443 HS6.

The eight W1-bis `attempt.json` files in run `20260912T141128Z` were edited
after the run to copy response metadata from immutable page contracts. OD-11
retained the transparent correction as history, prohibited further edits and
superseded the run with W1-ter. Original → repaired SHA-256:
`9d511b9e6adeebf7fa154641864c375be1635d99afc9726c1a8e7abe23f0d32f`
→ `ff49dbbc10921914b436e951c61dd0cdec9f4fdf7581e0dd4d04f33a7ea8d1f1`;
`5d666a753c57c01e383a2e4435fabc96beea88d27d700242e183f50c7811c8be`
→ `6d1b62add41ce0e715f6ec1e9aa89ddbd1972e8ff1478dd99985d7dd0e2ec162`;
`1252e449a734955fd8ad75bd89cc1b2fde7a84c252cebb7194db7f80df1d998a`
→ `c70b040d453cc178697ec0bdaf42ac70d353cc0fdaa251d488a3dfb83af7a243`;
`e5a06a9c7f66e10a594db59763bb38b0cd33d3e9f938e8c252f3d5b134d399fe`
→ `6953fa7070dc9ba8d8295b13cfbe0fac26841d9ae872a1847679dc1ba06ad10e`;
`d21b9ab6256d2ca348a439200e983d7653a505d3169f905b8719420c750c7808`
→ `1c46b0c727123935f70ef9ca045227c944434d7eeef406a369208675074f7662`;
`d37c8c9e46c5d471676168b07e7f8eda5c1b1b4a7d28ebac2307a02e1bd7216e`
→ `4ab3e46a326ffc828dc95843e56632045076e08ce6b5801ce22a6039c7a98538`;
`d853b142e764d436f5e7616e0342bb2f56bf975e1af56f7838560a9bfce3aeeb`
→ `e48cfaeb88f35ed0e5d3123e26eecbcaa89060969b149685fe90bddb18954ceb`;
`cb209f9c94c59bcf04620de9192229fe4e1cc98f5c85519c29cfcfc2d795ccbb`
→ `b9ad4665e35167b3a106854131100a4e099c3469fd1ee27a0348c84bd0790418`.
RawStore tests prove
`attempt.json` and `coverage.json` cannot be overwritten through its API.

The proven-universe single-file screening result was 57,164,360 bytes and
triggered OD-7. OD-12/AM-2 replaces only its storage representation:
`summary.json`, external `queues.json` when over 1 MiB, and HS2 record shards,
with repeated common record fields removed and restored by the loader. The
logical `ScreeningSnapshot 1.0.0` contract and all 5,443 records remain
unchanged. The replacement has 98 files totaling 52,798,074 bytes; largest
file `records/84.json` is 5,125,636 bytes. This fits the 48 MiB per-file and
100 MiB total limits. Each screening cycle still adds about 52.8 MB of
governed repository content; deterministic compression is a candidate later
§7.4 change and is not implemented here.

W0-ter used a fresh read-only Chromium context without credentials. The
developer page redirected to sign-in and rendered only “Products”, “Sign in”,
“Welcome to UN Comtrade API portal!”, “Sign in to Comtrade Developer portal”
and “Powered by Azure API Management.” No parameter, all-partners token,
operation, record-limit statement or terms link was observed, so PARTNERS
remains `UNAVAILABLE` and W2 was not repeated. Historical W2 run
`20260912T144127Z` remains 59 `ENDPOINT_UNVERIFIED` units and zero requests;
all 1,471 emitted R2-FULL survivors remain
`PARTNER_DETAIL_NOT_ACQUIRED`.

OD-11 authorized a third manifest run for its correction; OD-12 preserves
that authorization and requires it only after AM-2, governed text and
regression. It is the third and last S13a manifest run. Its UTC execution
receipt and immediate oracle result are appended after execution; no fourth
run is authorized.

**OD-12 execution receipt:** the third and final invocation ran at
`2026-09-12T15:01:37Z`, exited 0, enumerated every regular file under the
sharded screening directory, updated both generated manifests and the §11
human mirror, then immediately passed `INTEGRITY PASS` and all 20
manifest-contract tests. S13a manifest run count was **3** at that gate.

**OD-13 review correction:** reviewer-grok rejected candidate `612626ed…`
because Core 05 §3.1 still described only the S11 connector state and the
known-limitations register omitted the governed §8.2(c) and persistence-only
outcomes. OD-13 also authorized the bounded A-01/A-03/A-04/A-05 corrections:
the ADR header cites both amendments; Core 01 distinguishes acquired-universe
screening from deep resolution; runtime selection orders snapshots by
`(as_of_date, snapshot_id)`; and CLI exit-code/no-socket behavior is pinned.
Because the two Core corrections are authority-hashed, OD-13 authorizes
exactly one fourth and final manifest generation after regression, followed
immediately by the manifest oracle. No data, snapshot or raw artifact may
change in this round.

**OD-13 execution receipt:** the fourth and final invocation ran at
`2026-09-12T15:36:59Z`, exited 0, updated the generated authority hashes and
their §11 human mirror for the authorized Core 01/Core 05 corrections, then
immediately passed `INTEGRITY PASS` and all 20 manifest-contract tests. S13a
manifest run count is **4**; authorization is exhausted and no fifth run is
permitted.
