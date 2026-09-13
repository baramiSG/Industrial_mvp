# S16 — Neo4j capability and dependency graph (backend): plan-1 (mirror)

Machine record: `.autonomous-workflow/plans/s16-graph-backend/cycle-1/plan-1-s16.json`
(SHA-256 `7e888e7a9b04d45579bfe799113a39066d4ea39e274aa2ceb5f573e0770d1b8d`; the JSON is binding, this
Markdown is a mirror). Seat: `planner-fable` (fresh instance). Planned against `origin/main` at
`ab6211f8…`; the S16 base `M16` is recorded at T0 **after the S14 parent (s14a + s14b) has merged**.
Implementer: `implementer-sol` (fresh, isolated worktree); ladder `implementer-fable` → `implementer-sol`;
`reviewer-grok` sole approver (OR-2 fallback for infrastructure failure only). Docker required
(Compose Neo4j; canonical visual container).

Binding inputs: planner-brief-1 (`d87aea32…`), pre-rulings PR-S16-1…12 (`50595cea…`), OR-7,
research observations (`e7b2b877…`; corrections adopted: graph text is Core 04 §8, Core 03 has no graph
section, NFR-005 is Core 01, GAP E2 says 13 edges where the file has 14, no KL graph row), sanitized Aura
evidence (`c56ada18…`), SLICE_GRAPH §3 S16/§9, GAP §4.E/§7A, Core 01–09, methodology §8.2/§8.3.

## Decomposition assessment

**SPLIT RECOMMENDED** (OD-1, default). Seam = the visual `source_tree` pins (every top-level
`src/ior_mvp/*.py`, static assets, `config/{ui_strings,evidence_policy,decision_narratives}.v1.yaml`).

| Child | Content | Frozen roots / visual |
|---|---|---|
| s16a `slice/s16a-graph-projection-and-provisioning` | `src/ior_mvp/graph/**`, `data/graph/**` artifact + validator + reconstruction pass, Compose service + credential, loader (compose/ci/aura tooling), fail-closed service + API module (unmounted), `graph_tests/` live suites, CI `graph-gates`, extra `graph` + lock, Core 03 §13 / Core 04 §8 v2 / Core 02 / Core 09 graph layer, runbook, ADR part A, one manifest run | untouched; **no regeneration** |
| s16b `slice/s16b-route-eight-activation-and-graph-api` | Core 06 §3.5 enabler block (contract 2.1.0, Gate B check 11), route-8 activation (`route_hypotheses`, `public_decision`, `simulation`, `decision_engine`), thresholds 1.3.0, narratives 1.3.0, `/api/graph` mount, TL-09 graph assertions, Core 01/06/07/09 text, two S14 scenarios re-versioned (historical v2_0 copies), integration task on merged main, **one** canonical visual regeneration (manifest only), frozen-pin WIP, PR-S16-11 Aura verification, §9 row 8, ADR part B, one manifest run | `data/synthetic` (2 M + 2 A), `browser_tests/baselines` manifest, pins file |

If not split: T0–T12 sequentially in one PR; one regeneration; one manifest run.

## PR-S16-12 — requirement → source → approach → test (summary)

| Id | Requirement | Source | Delivery approach (Aura-safe: Cypher 5; no GDS; no APOC dependence) | Test |
|---|---|---|---|---|
| RQ-1 | R9-S adjacency explanation (view 1) | S16 scope; S17; E4; Core 07 §3 | `(Plant\|Company)-[:ADJACENT_TO{derived}]->(Product)` from the R9-S ledger row + `USES_PROCESS`/`CERTIFIED_TO` signal facts with `SUPPORTED_BY_EVIDENCE`; Cypher V1 pattern query; artifact function `engine_feed.adjacency_explanation` | == R9-S row for all cases/modes; Cypher == artifact |
| RQ-2 | Route-blocking capability (view 2) | S16 scope; S17; Core 07 §4.3/§7.7 | `(Intervention route)-[:CONSTRAINED_BY{reason_code}]->(Capability dim/gate/D*)` derived from reason codes; Cypher V2; `engine_feed.route_blocking_capability` | == route reason codes and capability states; Cypher == artifact |
| RQ-3 | §8.3 UnlockValue → route 8 | Core 07 §7.7/§7.9/§10; FR-048/055; I5; R-2; PR-S16-4 | Evidence layer `(Product)-[:UNLOCKED_BY{P, share, ΔNV_i, …}]->(Intervention enabler{cost})` from Core 06 §3.5 blocks (Class D) or passported public evidence (none today); deterministic engine computation via `engine_feed.shared_enabler_inputs` → `evaluate_shared_enabler_route`; Cypher V3 aggregation must equal the engine value | boundary suite; fixture pair ADVANCE 8; governed scenarios evaluated+positive+blocked; public byte-identical; Cypher == engine |
| RQ-4 | Shared-enabler queue input | S16 scope; GAP §5 §8; methodology §8.2 | `engine_feed.shared_enabler_queue_rows` + `GET /api/graph/portfolio/shared-enablers`; screening queues untouched | rows == aggregation; public → [] |
| RQ-5 | EVSI evidence linkage (view 4) | S16 scope; S17; Core 07 §6 | `(Decision)-[:CONSTRAINED_BY{need_code…}]->(blocked node)-[:SUPPORTED_BY_EVIDENCE]->(Evidence)`; numeric EVSI Class D only where scenario inputs exist; Cypher V4; `engine_feed.evidence_linkage` | == evidence needs; Cypher == artifact |
| RQ-6 | Rebuild reproducibility | S16 objective; R-3; Core 07 §11 | canonical JSON, sorted, `projection_id` from inputs hash, `engine_run_id`; `GRAPH RECONSTRUCTION PASS`; `ORDER BY` everywhere | two builds byte-identical; reconstruction; equality suites |
| RQ-7 | Fail-closed `GRAPH_UNAVAILABLE` | S16 objective; R-6; PR-S16-6; Core 03 §12 precedent | `GraphService` maps NOT_CONFIGURED / DRIVER_NOT_INSTALLED / CONNECTION_FAILED / INSTANCE_MISMATCH / PROJECTION_MISMATCH to a typed HTTP 200 payload; `OfflineGuardViolation` never swallowed | fake-driver tests; service stopped locally and in CI (`docker stop`) |
| RQ-8 | Provenance 100%; partition; public filters | R-3; E3; §8 item 1; PR-S16-3 | validator + Cypher null-counts; `scenario_id='PUBLIC'` sentinel; public templates filter nodes and edges; filter lives in the graph package (Core 07 §11 AST rule) | GRAPH VALIDATION PASS; null-count 0; TL-09 10–12 |
| RQ-9 | Idempotent init; constraints/indexes; MERGE by governed ids | R-6; PR-S16-10; OR-7 | uniqueness constraints `IF NOT EXISTS` on all 19 labels (Community-compatible; existence/key constraints are Enterprise-only and not used); `UNWIND … MERGE … SET n = props`; implicit transactions | second load creates 0/0; `SHOW CONSTRAINTS` = 19 |
| RQ-10 | Route 8 in §9 matrix (R-5) | SLICE_GRAPH §9; R-2; R-5 | governed: evaluated, positive UnlockValue, `fails LOWER_ROUTE_FULLY_RESOLVES` (selected routes 6/4 fully resolve); fixture pair proves selection; row 8 = ACTIVATED, governed selection NOT DEMONSTRATED → owner re-approval | route-8 tests; §9 text pinned |
| RQ-11 | Derived nodes never feed back | PR-S16-5; R-3 | phase-2 engine run; `derived=true` + `engine_run_id`; feed reads `derived=false` only | mutated-fixture test |
| RQ-12 | TariffLine only from a COMPLETE unit | PR-S16-9; Core 04 §2.3 | no COMPLETE ZATCA unit exists (run INCOMPLETE / MAX_REQUESTS_EXHAUSTED) → one `TARIFF-SA12-UNAVAILABLE` marker, zero `CLASSIFIED_AS` | marker test; COMPLETE-unit double |
| RQ-13 | Typed API for S17 (bilingual keys, ids, provenance, synthetic_flag, drill-down) | S17 scope; Core 09 §2.7; Core 04 §2.8; G5 | `config/graph_views.v1.yaml` catalogue; payload schema with provenance block, `display_labels` on synthetic elements, `drilldown` evidence ids/document addresses; typed 404s | API contract tests; parity check |
| RQ-14 | Aura verification | OR-7; PR-S16-11 | `verify --target aura --confirm-instance 8a7338e0`: counts, provenance, partition, sample V1–V3, app AVAILABLE/UNAVAILABLE; sanitized JSON | operator step recorded before/after |
| RQ-15 | NFR-004/005/009 | Core 01 §7; PR-S16-6 | engine reads the cached artifact in-process; graph API is the only live path | `test_performance.py` unchanged; smoke unchanged |
| RQ-16 | §8.3 sequencing / common exposure / cannibalisation / option value; §8.1 priors | methodology (mirror) | **not in S16 scope** (not named by SLICE_GRAPH/GAP/PR-S16-12); vocabulary supports them; no governed facts → KL, no computation | KL present |
| RQ-17 | GDS constraint; APOC not required | PR-S16-12; Aura evidence | no `gds.` anywhere; no `apoc.` in required paths | grep/AST assertion; suites identical on Community CI and Aura |

Nothing was found undeliverable with supported approaches; no KL-escalation is needed before gating.

## Graph model (Core 04 §8 v2) — summary

- **19 labels**: Product (= opportunity id), TariffLine (marker `TARIFF-SA12-UNAVAILABLE` today), Specification
  (public marker UNAVAILABLE; synthetic target spec), Application, Plant and Company (ENTITY_ID_V1 union across
  artifacts; producers without an entity → `PRODUCER-<snapshot>-<i>` with `identity_basis`), ProductionLine
  (synthetic `plant_line`), Process (`PROC-<slug>`), Equipment, Capability (nine dimensions, gates, derived D*),
  Standard, Certification, Input, Technology (types exist; no governed facts), CustomerSegment (synthetic),
  Evidence (public passports; synthetic rows `<scenario_id>::<block>`), Scenario, Decision (derived),
  Intervention (derived route records; declared shared enablers `ENABLER-SYN-<SLUG>-001`).
- **15 edge types** with endpoint rules: CLASSIFIED_AS, REQUIRES_SPECIFICATION, USED_IN, PRODUCED_BY, HAS_LINE,
  USES_PROCESS, HAS_CAPABILITY, REQUIRES_INPUT, CERTIFIED_TO, QUALIFIED_FOR, DEPENDS_ON (incl. Decision →
  Intervention `{role}`), ADJACENT_TO (derived R9-S), SUPPORTED_BY_EVIDENCE, CONSTRAINED_BY (route blocking;
  evidence needs), UNLOCKED_BY (`P`, `share`, `ΔNV_i`, constraint classes).
- **v1 → v2 mapping**: Opportunity→Product; Buyer→CustomerSegment; Utility→Input{utility};
  HAS_SPECIFICATION→REQUIRES_SPECIFICATION; REQUIRES_STANDARD→CONSTRAINED_BY; REQUIRES_EQUIPMENT→DEPENDS_ON;
  QUALIFIED_BY→CERTIFIED_TO; DEMANDED_BY→USED_IN + QUALIFIED_FOR; BLOCKED_BY→CONSTRAINED_BY; ALTERNATIVE_TO retired.
- **Provenance on 100% of nodes and edges**: `evidence_id`, `as_of`, `evidence_class`, `synthetic_flag`,
  `scenario_id` (`'PUBLIC'` sentinel for public elements — Neo4j has no null properties) plus `origin_kind`,
  `origin_ref`, `derived`/`engine_run_id`, `projection_id`, display labels on synthetic elements.
- **Partition**: a synthetic edge may start at a public Product; no public edge may end at a synthetic node;
  public queries filter nodes and edges by `synthetic_flag=false`.
- **Artifact**: `data/graph/projections/<GRAPH-SAU-<as_of>-<hash12>>/{projection.json, manifest.json}` +
  `data/graph/current.json`; write-once; history retained; §7.5 hashed; `GRAPH RECONSTRUCTION PASS`.

## Projection / loader / API design (brief)

- **Build** `scripts/build_graph.py` → `python -m ior_mvp.graph build`: phase 1 evidence layer from public
  snapshots 2.1.0/2.2.0, scenarios 2.0.0/2.1.0, entity artifacts, case briefs, the ZATCA attempt (incl.
  `UNLOCKED_BY` edges with ΔNV_i computed by `route_hypotheses._national_value` from the dependent's ground-truth
  route record); phase 2 runs the engine with the phase-1 projection injected → derived Decision / Intervention /
  D* / ADJACENT_TO / CONSTRAINED_BY. Deterministic ids and canonical bytes; validator before write.
- **Engine feed** (`graph/engine_feed.py`) reads the committed artifact (cached) — route-8 inputs, adjacency,
  route blocking, evidence linkage, queue rows — branch-filtered inside the graph package. The engine never
  opens a socket; goldens and `demo_smoke` stay offline (NFR-004).
- **Route 8** (Core 07 §7.7 v2): `None` → NOT_CALCULABLE/GRAPH_REQUIRED byte-identical; counted dependents ≥
  `thresholds.routes.shared_enabler.minimum_dependent_opportunities` (1.3.0, default 2) else
  `SHARED_ENABLER_DEPENDENTS_INSUFFICIENT`; UnlockValue > 0 else `UNLOCK_VALUE_NONPOSITIVE`; components as routes
  1–7 (missing → NOT_CALCULABLE); evaluated records are precedence-blockable; `select_preferred_hypothesis`
  admits route 8. Public branch: `None` without passported public enabler evidence (not hard-coded).
- **Core 06 §3.5 block** (`shared_enabler`, contract 2.1.0): `enabler_id`, `enabler_kind`, bilingual `label`
  (synthetic design basis), `constraint_classes_addressed`, `removes_binding_constraint`, `unlock_probability`,
  `dependency_share`, `enabler_cost_m_sar`, `components`, `basis`; Gate B check 11; cross-scenario consistency;
  default governed pair OD-3 = ALU-FOIL-001 + ALU-PROFILES-001 (values recorded from the engine, never asserted).
- **Loader** (`graph/loader.py`): targets `compose | ci | aura` from env NAMES; uniqueness constraints + indexes
  `IF NOT EXISTS`; `MERGE` by id with full property maps (second run 0/0); `verify` compares counts, provenance,
  partition, sample views against the artifact and writes a sanitized report; `clear` only with
  `--confirm-clear <instance-id|container-name>`.
- **Service/API** (`graph/service.py`, `graph/api.py`, mounted in s16b): `GET /api/graph/status`, `/catalogue`,
  `/opportunities/{id}/views/{view_id}?mode=`, `/portfolio/shared-enablers`; typed payloads with ids, provenance,
  `synthetic_flag`, bilingual catalogue keys, drill-down; `GRAPH_UNAVAILABLE` as HTTP 200 typed state; typed
  404s; injected service (tests use a fake). No GenUI registry change (S17).

## Dependency and CI changes

- `pyproject.toml` extra `graph = ["neo4j>=5.28,<6"]`; `uv.lock` regenerated once; T0 verifies
  `uv sync --locked --extra dev --extra graph` on **3.12 and 3.14** (5.28.x on 3.14 is UNVERIFIED — PR-S16-7
  fallback to 6.x only with justification; SC-9 otherwise). `Dockerfile` unchanged; a CI step proves the image
  has no `neo4j` package.
- `.github/workflows/ci.yml`: new job `graph-gates` (uv / 3.12) with `services.neo4j` image
  `neo4j:5.26.30@sha256:<digest recorded at T0>`, run-scoped ephemeral `NEO4J_AUTH` (never a committed value),
  ports 7688/7475, `python -m ior_mvp.graph wait`, `build --check`, `load` ×2, `verify`, `pytest -q graph_tests`,
  `docker stop ${{ job.services.neo4j.id }}`, `pytest -q graph_tests -m graph_unavailable`. Other jobs verify the
  artifact only; `compileall` adds `graph_tests`. A red designated job is never a skip (PR-S16-1).
- `docker-compose.yml`: service `industrial-mvp-neo4j` (pinned digest; 7475/7474, 7688/7687; named volume;
  project network; `NEO4J_AUTH_FILE=/run/secrets/neo4j_auth` from git-ignored `.secrets/neo4j_auth.txt`;
  `cypher-shell` healthcheck reading the secret). `Makefile`: `graph-*` targets and `graph-gate` inside `make ci`.
  `.gitignore` `.secrets/`; `.env.example` variable names; prohibited-path rule `.secrets/`.

## Aura safety rules (as planned)

- Aura `Industrial_mvp` (8a7338e0) is the integration/deployment-verification target only (OR-7 supersedes R-6's
  "no Aura" for this role; local Compose remains the offline/demo option; hosted CI uses the isolated container).
- Connection values by variable NAME only; `.env` loaded in-shell inside the operator command; nothing printed,
  read as text, stored or committed; reports sanitized (instance id only).
- `load --target aura` requires `--confirm-instance <id>` equal to `AURA_INSTANCEID` **and** to the `neo4j+s`
  URI host prefix, verified before the driver is created (SC-2); loads are idempotent MERGE; any
  `DETACH DELETE` requires `--confirm-clear 8a7338e0` (SC-3).
- Ordinary tests never touch Aura: `tests/conftest.py` deletes the Neo4j/Aura env names (strengthening);
  `graph_tests/` refuses `aura` unless `IOR_GRAPH_AURA_OPERATOR=1` and the confirm flag are present; `make ci`
  and hosted CI never see Aura.
- PR-S16-11 verification is an operator step (parameters before; sanitized report after): counts vs artifact,
  provenance 100%, partition, sample V1–V3, application AVAILABLE / `GRAPH_UNAVAILABLE` behaviours.

## Integration precondition on S14 (exact)

S16 implementation starts only when **all** hold: s14a squash-merged with its records PR landed; s14b
squash-merged with its records PR landed (S14 parent COMPLETE in `.workflow/state.json` and
`docs/BUILD_ROADMAP.md`); the delivery queue's current slice is s16 (or its child); `M16` recorded in
`context.md` together with: seven public snapshots, seven scenarios, `SCENARIO VALIDATION PASS (7 scenarios)`,
`CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)`, `VISUAL_MANIFEST_OK <n>`, `pytest -q` green,
`INTEGRITY PASS`. If S15 merges first, the recording is repeated against that main. Integration task T10:
owner-lead W1 preparation commit → rebase on `M16` → merged-interface confirmation → historical copies + 2.1.0
blocks → validate → build → gates → one canonical regeneration → owner-lead W2 → IAC-6 (base W2, wip_parent
M16). The reviewer assesses the integration delta separately.

## Tasks (abridged; RED test names in the JSON)

| Id | Child | Goal | Oracle strings |
|---|---|---|---|
| T0 | both | Preflight on `M16`; BF-19 confirmations (lock 3.12/3.14, image digest + `cypher-shell`, ports, ΔNV of the OD-3 pair, s14b pins) | `BRANCH_OK`, `LOCK_RESOLVES_3_12_AND_3_14`, `IMAGE_DIGEST_RECORDED`, `PORTS_FREE 7475 7688` |
| T1 | s16a | Model, projection, derived layer, artifact, build CLI (TDD, 27 tests) | `GRAPH BUILD PASS`, `GRAPH VALIDATION PASS`, two builds identical |
| T2 | s16a | Engine feed, Cypher templates, loader, fail-closed service, API module (TDD, 25 tests) | offline suites green; `RUNTIME_IMPORT_BOUNDARY_OK` |
| T3 | s16a | Compose, credential, Makefile, live `graph_tests` on loopback, unavailable test | `GRAPH LOAD PASS … second run 0/0`, `GRAPH VERIFY PASS`, `GRAPH_UNAVAILABLE_OK` |
| T4 | s16a | Extra `graph` + lock; CI `graph-gates`; image neo4j-free step | lock resolves; ci.yml contract test |
| T5 | s16a | Core 03 §13, Core 04 §8 v2, Core 02/09, runbook, ADR A, KLs | core contract test |
| T6 | s16a | Manifest roots, graph reconstruction pass, one manifest run, portability, IAC-6 | `GRAPH RECONSTRUCTION PASS`, `PORTABILITY_PASS`, `make ci` 0 |
| T7 | s16b | Core 06 block, contract 2.1.0, Gate B 11, consistency (TDD, fixtures) | `SCENARIO VALIDATION PASS (7 scenarios)` |
| T8 | s16b | Route-8 activation; thresholds/narratives 1.3.0 with history (TDD, 15 tests) | `FROZEN_OUTCOMES_OK`, `ROUTE8_ACTIVATION_OK` |
| T9 | s16b | Mount `/api/graph`; TL-09 graph 10–12; Core 01/06/07/09 text; ADR B | TL-09 green |
| T10 | s16b | Integration on merged main; scenario re-versioning; build; gates; one regeneration; WIP pins | `SHARED ENABLER CONSISTENCY PASS (1 enablers, 2 dependents)`, zero pixel drift |
| T11 | s16b | PR-S16-11 Aura operator step | `AURA_VERIFY PASS (8a7338e0; …)` |
| T12 | both | §9 row 8, KLs, control docs, one manifest run, identity, stop uncommitted | `CANDIDATE_IDENTITY`, `INDEX_EMPTY_PASS` |

## Open decisions (defaults in force on silence)

OD-1 split (default split) · OD-2 engine consumes the governed artifact with Cypher equality proof (default;
live-at-request rejected) · OD-3 governed pair ALU-FOIL + ALU-PROFILES with `ENABLER-SYN-ALU-CASTHOUSE-001`
(default) · OD-4 contract 2.1.0 additive + historical v2_0 (default) · OD-5 route-8 precedence/selection semantics
(default) · OD-6 min dependents key = 2 (default) · OD-7 ΔNV_i from the ground-truth route record (default) ·
OD-8 v1→v2 mapping; no 16th edge type (default) · OD-9 keep `GRAPH_REQUIRED` for the public no-enabler case
(default) · OD-10 run-scoped CI credential (default) · OD-11 cypher-shell healthcheck + wait command (default) ·
OD-12 graph gate unconditional in `make ci` (default) · OD-13 `config/graph_views.v1.yaml` (default) ·
OD-14 queue input as typed rows; screening untouched (default) · OD-15 Aura verification after APPROVE, before
PR (default) · OD-16 seats recorded · OD-17 OR-7 supersedes R-6 "no Aura" for the deployment target (recorded).

## Stop conditions (abridged)

Golden change (SC-1); Aura instance-id mismatch (SC-2); write without confirmation / clear without flag / Aura
env in tests or CI (SC-3); undeliverable required query → KL + escalate before gating (SC-4); credential printed
(SC-5); synthetic marker in a public payload or path (SC-6); non-deterministic build (SC-7); pixel drift (SC-8);
lock unresolvable (SC-9); a governed selected route would change (SC-10); ports/image blocked (SC-11); second
manifest run needed (SC-12); designated CI job unusable = red, not skipped (SC-13); reviewer fallback rules (SC-14).

## Muhasib (verified vs assumed)

- **Verified this session**: route-8 contract code paths; simulation/engine wiring; scenario contract closed key
  set and the two tests that use `shared_enabler` / `2.1.0` as negative probes; visual `source_tree` pins on every
  top-level module and three configs; the exact public payload fixture; the socket guard; toolchain files; the
  empty tariff snapshot root and the INCOMPLETE ZATCA run; the frozen snapshot/scenario structures; the s14a/s14b
  plan protocols and provisional S14 outcomes; the Aura sanitized evidence; official Neo4j pages (constraint
  editions, compose secrets, `execute_query`, connect/Aura URI, `CALL IN TRANSACTIONS`, Aura APOC subset).
- **Assumed (confirm at T0, BF-19)**: 5.28.x lock resolution on 3.14; local image presence and `cypher-shell`;
  ports 7475/7688 free; positive ΔNV of the OD-3 pair on merged main; `job.services.neo4j.id` availability;
  s14b test pins on `synthetic_inputs_used`.
- **Disclosed limitations**: governed route-8 *selection* is not reachable without changing a golden (every
  S14 scenario is won by a fully resolving lower route) — the plan activates route 8 honestly and returns
  selection to the owner under R-5; the enabler design values are Class-D proposals to be recorded from the
  engine; the primary worktree's HEAD moved to `13eeea1e…` (owner-lead s14a commit) during planning — not this
  seat's action; `origin/main` remains `ab6211f8…`.
- **Not done by this seat**: no product file edited, no git state change, no Docker pull, no dependency install,
  no `.env` read, no network beyond the recorded official documentation pages; this seat does not approve,
  implement or review its own plan.
