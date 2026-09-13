# S14b — Deep-case portfolio, scenarios and goldens: plan-1 (mirror)

Machine record: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14b.json`
(SHA-256 `af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2`; the JSON is binding, this
Markdown is a mirror). Child 1 of the S14 decomposition (`decomposition-1.json`
`48741467ed2e3d6185cb0e5aac13b56d6c9d81847a3b114b960547740b877f3a`), planned against the approved
s14a interfaces (plan-1-s14a `8fbfa4e6…` DD-9/DD-10/DD-11; AM-1 `8c61a0a2…`; AM-2 when present) and the owner
rulings OD-1…OD-12 (`20260913-s14-plan-1-rulings.md`, `19afdc8c…`).

Seat: `planner-fable`. Worktree: `/home/barami/projects/ior-worktrees/s14b`, branch
`slice/s14b-deep-case-portfolio-scenarios-and-goldens`, base `ab6211f8…` (= `origin/main`), own Python 3.12
`.venv`. **Parallel mode:** s14a is uncommitted on the primary checkout; s14b is prepared against the
interfaces and integrated against the merged main `M` (task T5) before delivery. Implementer:
`implementer-sol` first (recorded deviation), `implementer-fable` fallback; `reviewer-grok` sole approver.
Docker required only for T8.

## Objective (abridged)

Five derived public snapshots (built by the merged s14a builder, never authored) plus five Class-D scenarios
under contract 2.0.0 with planted ground truth reconciled to the public marginals, each reaching its stated
outcome by computation; Core 09 §2.4 Golden C–G and Core 07 §7.8 text; `project.yaml` golden list (seven);
`harness.CASES` = 7 with journeys in both locales and the observed / missing / Class-D distinction on every
new view (OD-12(c)); visual matrix 56 → 76 regenerated once; frozen pins for three roots via the owner-lead
WIP protocol; SLICE_GRAPH §9 rows for routes 0 (second row), 3, 4, 6, 7; ADR-022; KLs (MONITOR not
demonstrable from S14 evidence); exactly one manifest run after integration; IAC-6 identity with
`wip_parent = M`.

## Public branch today and designed simulations (computed this session; provisional until merged main)

| Case | Public today (in-flight briefs rebuilt to /tmp; hashes = s14a log) | Designed simulated outcome | Route | Why the public evidence alone cannot |
|---|---|---|---|---|
| `SAU-H6-721061` coated steel (Al-Zn coated coil) | INVESTIGATE / route null / `ROUTE_CHANGING_EVIDENCE_UNRESOLVED`; fired R0, R1-D, R12 (R2 not fired: quantity share 0.21); capability all U; partner detail missing (WITS unparsed; AM-2 tri-state pending) | `SYN-MINISTRY-GALVALUME-001` → **ADVANCE** (`ALL_ADVANCE_GATES_PASS`) | **3** certification / customer qualification | No FULL signal, no resolved field, no route record; the design plants an incumbent GL line whose output is not certified to the target standard (equivalence False → application gap), a passing route-3 record (S* 5, ΔNV 82, ratio 1.149) and R8 committed demand as the FULL signal; routes 0–2 and 4–7 fail by computation |
| `SAU-H6-721012` coated steel (tinplate) | INVESTIGATE / null; fired R0, R1-D, R2 (CAGR 0.70), R4-D, R12; capability all U | `SYN-MINISTRY-TINPLATE-001` → **ADVANCE** | **7** targeted greenfield | No domestic line (plant_line nameplate 0), D* 0.90 > 0.65, downside 80 ≥ MES 60, competition 1.125, S* 137, ΔNV 220; route 5 infeasible, routes 1–4/6 constraint-class inapplicable, route 0 gap requires action |
| `SAU-H6-760711` fabricated aluminium (foil) | INVESTIGATE / null; fired R0, R1-D, R2 (CAGR 0.94), R12; capability all U | `SYN-MINISTRY-ALU-FOIL-001` → **ADVANCE** | **6** technology licensing / JV | Incumbent flat-rolled mill with zero foil-qualified output; D* 0.5667 in (0.40, 0.65]; route-6 record passes (S* 51, ΔNV 172, ratio 1.059); route 5 infeasible for foil gauges; route 7 blocked by the lower fully-resolving route |
| `SAU-H6-760429` fabricated aluminium (alloy profiles) | INVESTIGATE / null; fired R0, R1-D, R2, R3 (quantity basis), R4-D, R5, R9-S, R10, R12; verified_present True (ALUPCO/TALCO spans); preferred hypothesis route 5 by evidence priority; K 0.15 | `SYN-MINISTRY-ALU-PROFILES-001` → **ADVANCE** | **4** demand aggregation / conditional offtake | Equivalent incumbents with spare capacity (R7 FULL) but 2.5 kt qualified vs 6.0 kt target (quantity gap); route 4 passes with ZERO support (NPV +1.19); route 5 fails proportionality; 1–3/6 inapplicable; 5–7 blocked; retained flows, tariff-line and buyer allocations reconcile exactly to 9.189841 kt |
| `SAU-H6-392010` technical plastics (PE film/sheet) | INVESTIGATE / null; fired R0, R1-D, R2, R4-D, R12; R11 ratio 4.0 < 50; capability all U | `SYN-MINISTRY-PE-FILM-001` → **REJECT** (`HARD_EXCLUSION_SATISFIED`) | **0** no intervention | Net-exporter line (188.7 kt exported vs 21.7 kt imported): equivalent grade with 24 kt qualified ≥ 16 kt target and no binding market failure → EX-04 SATISFIED (Core 07 §7.4/§7.6 step 1) |

MONITOR is unreachable for all five in both branches (R1-D fires publicly; Core 07 §7.6 step 6 needs no
material trigger) — recorded as a KL and OD-2, never manufactured. Gate B passes for all five drafts; the
public decision fingerprint is unchanged by every simulation; every synthetic row is Class D.

## Tasks

| Id | Goal | RED tests (exact names in the JSON) | Oracle strings |
|---|---|---|---|
| T0 | Preflight in the worktree; declare parallel mode; provisional builds of the five briefs into /tmp with the in-flight builder | — | `BRANCH_OK`, `INTEGRITY PASS`, `SCENARIO VALIDATION PASS (2 scenarios)`, `2275 tests collected`, `VISUAL_MANIFEST_OK 56` |
| T1 | Author the five scenarios exactly per `scenario_designs`; /tmp dry run against provisional snapshots; `tests/test_s14b_portfolio.py` RED | `tests/test_s14b_portfolio.py` (10) | dry run: 5 back-tests match; Gate B PASS ×5; fingerprint unchanged ×5 |
| T2 | `project.yaml` seven rows; ten golden tests appended (first 119 lines byte-identical); count/id extensions | `test_golden_cases.py::test_{galvalume,tinplate,alu_foil,alu_profiles,pe_film}_{public,simulated}_golden_case`; `test_scenario_validation` `(7 scenarios)`; `test_api` `== 7` | four original golden tests green |
| T3 | `harness.CASES` = 7; journeys `len(CASES)`; API-derived unlock counts; accessibility tuple; new-case distinction test | `test_journeys.py::test_new_case_view_distinguishes_observed_missing_and_simulated` (10 nodes) | functional node count recorded |
| T4 | Visual `SCREENS` + five `journey-g-<slug>-public-workspace`; captures; no regeneration | `test_visual_baselines.py` RED until T8 | `len(_expected_matrix())` = 76 |
| T5 | **INTEGRATION** against merged main (see below) | — | W1 recorded; linear rebase; five `PUBLIC-SAU-H6-*.json` built by the merged builder; `SCENARIO VALIDATION PASS (7 scenarios)`; `CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)` |
| T6 | Post-integration recordings (verification [21]) before finalising golden assertions; suites GREEN | T1–T3 python suites GREEN | ten new golden tests green; predicted pin failures only |
| T7 | `make e2e-functional` for seven cases × two modes × two locales | T3 browser tests GREEN | `run-summary-functional.json` failed 0 |
| T8 | Single canonical regeneration (Docker), drift table, pins → STOP → owner-lead WIP pin commit W2 | `test_visual_baselines.py`; `test_frozen_public_evidence_pins.py` after W2 | `CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234`, `VISUAL_MANIFEST_OK 76` |
| T9 | Core 07 §7.8/§7.9, Core 09 §2.4/§2.7/§7/§10, SLICE_GRAPH §9 rows, ADR-022, KLs, control docs, state.json | `test_integrity_contract.py::test_s14b_core_v2_golden_contracts` | contract test green |
| T10 | Pre-generation regression; **exactly one** `build_manifests.py`; §11 mirror; immediate oracle | `test_human_authority_table_matches_machine_manifest_exactly` | `INTEGRITY PASS`; integrity-contract suite green; ten added rows, zero pre-existing changes |
| T11 | Portability copy; `make ci` | — | `PORTABILITY_GATE_PASS`, `ABSOLUTE_PATHS_PASS`, `make ci` exit 0 |
| T12 | IAC-6 identity (`base` = W2, `wip_parent` = M, `wip_commits` = [W1', W2]); stop uncommitted | — | `CANDIDATE_IDENTITY`, `INDEX_EMPTY_PASS`, `PROTECTED_SET_BYTE_IDENTICAL_PASS`, `STATE_JSON_VALID_PASS` |

## Integration task (T5)

Pre-conditions: s14a (with its AM-2 correction round) squash-merged to main as `M` and recorded in
`context.md`; s14b is the delivery-queue current slice (only it touches GitHub, and not before review).
INT-1 (owner lead) WIP commit **W1** `wip(s14b): preparation against approved s14a interfaces
(pre-integration)` with exactly the preparation set (project.yaml; the test files; browser_tests/*.py; the
slice record) — no file under the frozen roots or the pins test (the five scenarios stay untracked).
INT-2 (owner lead) `git fetch origin && git rebase <M>` — linear by construction (the preparation touches no
s14a file); a conflict is a STOP; record **W1'**. INT-3 (implementer) confirm the merged tree carries
`src/ior_mvp/cases/**`, the briefs, the selection record and the AM-2 tri-state tokens (else SC-9); baseline
gates on M. INT-4 build the five snapshots with the **merged** builder
(`python -m ior_mvp.cases build --brief <brief> --out data/snapshots/public`), record sha256 and compare
with the provisional hashes (a difference only for 721061 via AM-2 is expected; any other difference is a
STOP). INT-5 re-run all gates (`SCENARIO VALIDATION PASS (7 scenarios)`, `CASE RECONSTRUCTION PASS
(5 snapshots, 5 briefs)`, verification [21] recordings written verbatim before any golden assertion is
finalised; the T1–T3 suites GREEN). INT-6 write the "Integration delta" section (M, W1', hash table,
recordings, gates). INT-7 (reviewer-grok) assess the integration delta separately — `git diff M W1'`,
`git diff W1' W2` and the uncommitted delta — confirm no snapshot byte was authored, OD-12(c) on the
721061 view, and recompute every scenario by running verification [7] and [21].

## Owner-lead WIP protocol and identity (s13b OD-4/OD-15/OD-16)

W2 (end of T8) `wip(s14b): five derived snapshots, five scenarios, regenerated visual baselines (76 entries)
and frozen-tree pins` — exactly `data/snapshots/public/PUBLIC-SAU-H6-*.json` (5 A),
`data/synthetic/SYN-MINISTRY-*-001.json` (5 A), `browser_tests/baselines/v0.3.0/**`,
`browser_tests/visual_baselines.py`, `browser_tests/test_visual_baselines.py`,
`tests/test_frozen_public_evidence_pins.py` — after the owner lead verifies additions-only, the four PINS,
`VISUAL_MANIFEST_OK 76`, ownership, bytes, the drift table and the three tree OIDs recomputed from a temporary
index. The implementer never touches git state. Identity: `base` = W2, `wip_parent` = M,
`wip_commits` = [W1', W2]; the reviewer reviews every commit since M plus the uncommitted delta.

## Manifest §7 mapping

- §7.2: tests and browser code only; no engine change.
- §7.3: `config/project.yaml` golden list 2 → 7 (not in the authority hash set); five scenario-parameter
  artifacts (contract 2.0.0).
- §7.4: Core 07 §7.8/§7.9 (five S14 public outcomes; routes 3/4/6/7 and REJECT 0 by computation); Core 09
  §2.4 Golden C–G, §2.7 (76 entries), §7, §10. Core 06 byte-identical (OD-12 default).
- §7.5: five derived snapshots and five scenarios added; nothing overwritten.
- Frozen visual oracle regenerated once with change ref `S14b-…:<plan sha256>`; three tree OIDs and
  `VISUAL_BASELINE_ENTRIES = 76` via W2.
- Exactly one `build_manifests.py` run (T10) after T5, W2 and T9; permitted generated diff: ten added
  snapshot-manifest rows; authority rows changed only for Core 07 and Core 09; §11 mirror exact.

## Authority / frozen files changed

`data/snapshots/public/` (+5, built), `data/synthetic/` (+5), `browser_tests/baselines/v0.3.0/**`
(regenerated), `tests/test_frozen_public_evidence_pins.py` (three OIDs, entries 76), `config/project.yaml`,
`docs/core/07`, `docs/core/09`, `docs/milestones/v0.3.0/SLICE_GRAPH.md` §9, ADR-022, KLs, control docs,
`.workflow/state.json`, generated manifests. Byte-identical: the two frozen snapshots and scenarios and
their historical copies, `data/golden`, every `src/ior_mvp/**` module, scripts, Makefile, the other ten
configs, Core 01/02/03/04/05/06/08, the DOCX, the first 119 lines of `tests/test_golden_cases.py`.

## Stop conditions

SC-1 golden change of the two original cases; SC-2 synthetic leakage; SC-3 any authored public field
(builder byte mismatch); SC-4 a scenario failing Gate B / back-test / recompute — no tuning, a redesign is a
new version with owner notice; SC-5 visual drift outside the predicted regions (8 portfolio entries within
`#kpi-grid` ∪ `section.compact-section`; 16 workspace entries within `#opportunity-select`; dossier and
screening entries pass); SC-6 portability/absolute path; SC-7 post-manifest-run authority edit; SC-8 Docker
unavailable; SC-9 merged main lacks the 721061 tri-state; SC-10 a new public state ≠ INVESTIGATE (record
honestly, never force); SC-11 visual budget breach (STOP, owner decides); SC-12 rebase conflict; SC-13
reviewer infrastructure.

## Open decisions (silence = default)

OD-1 visual variant (default one public-workspace screen per case, 76 entries; alt simulated-workspace; alt
64 on budget breach); OD-2 MONITOR unreachable → KL and S15 (informational ruling); OD-3 392010 REJECT via
EX-04 (alt EX-02); OD-4 760429 route 4 (alt route 2, reserved for S15); OD-5 'timing' gap class for absent
capability (informational); OD-6 AM-2 dependency (SC-9 default); OD-7 portfolio order steel, PP, 721061,
721012, 760711, 760429, 392010; OD-8 scenario-declared bilingual narratives with the Arabic drafts (no
catalogue change); OD-9 prep WIP W1 by the owner lead; OD-10 seats; OD-11 leave `final_acceptance.sh` /
`demo_smoke.py` to S22 (KL); OD-12 Core 06 byte-identical.

## Sanad / muhasib

Every baseline fact carries a path/line or a read-only command executed this session; the five briefs were
rebuilt with the in-flight builder (hashes equal the s14a log) and run through the public engine; the five
scenario drafts were run through contract validation, Gate B, `simulate` and the ground-truth back-test
(DRY_RUN_FAILURES 0) and their full designs and computed values are embedded in the JSON for the reviewer's
recompute; MONITOR unreachability is computed, not asserted. Assumed (to confirm at T0/T5/T6): merged main
carries AM-2; Docker available; the 76-entry budget fits (estimate 11.11–11.79 MB of 12.58 MB); the merged
builder CLI is unchanged; AM-2 does not change 721061's simulated outcome. The s14a tree moved during
planning (its log and manifests were regenerated by the s14a implementer at ~01:15Z); the in-flight hashes
are as read. Nothing was implemented, committed, regenerated, fetched or read from `.env`; the only
repository writes are the plan JSON (ignored tree) and this mirror (new untracked slice-record folder).

## Amendment AM-1 (2026-09-13) — carry of AM-2 C-3; SC-9/INT-3 repair

Machine record: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14b-amendment-1.json`
(SHA-256 `8dc1b75d5ce91ce041ed82798b5c00c9fb60e1f7c29fe985f40aa88385eca7c7`; binding; precedence AM-1 > plan-1-s14b;
the base JSON `af5ae5d8…` is not rewritten). Trigger: reviewer-grok REJECT (`plan-1-s14b-review.json`:
S14B-C3-NOT-CARRIED B7, S14B-SC9-MISREADS-AM2-C2 B3) and owner ruling s14b OD-13 (Option A, binding); inputs
s14a AM-2 C-2/C-3 and s14a OD-13…OD-16 (AM-3 ruled by OD-16, JSON not yet present).

**DD-AM1-1 — PublicSnapshot 2.2.0 is additive and version-gated; the two frozen 2.1.0 snapshots are not
migrated.** `SUPPORTED_PUBLIC_SNAPSHOT_SCHEMA_VERSIONS = {2.1.0, 2.2.0}`; `PUBLIC_SNAPSHOT_SCHEMA_VERSION = 2.2.0`
(builder output); `LEGACY_PUBLIC_SNAPSHOT_SCHEMA_VERSION_2_1 = 2.1.0`. 2.1.0 records keep today's rules byte-for-byte
(a `partner_detail` key is refused as extra); 2.2.0 admits the optional exact-key `partner_detail` block
`{state, reason, source_id, partner_snapshot_id, unit_key, observed_partner_rows, attempt_passport_ids,
observed_passport_id}` with cross-rules (list ⇒ OBSERVED with matching count/passport; UNAVAILABLE ⇒ MISSING or
ZERO with referenced attempt/ZERO passports; absent ⇒ absent). Why additive: frozen bytes, the four PINS, the
`historical/**` trees and the migration-equivalence oracle stay untouched; `data/snapshots/public` changes by
five `A` lines only; the two golden outcomes are protected by construction (no `partner_detail` on the frozen
files ⇒ no new engine branch executes); the frozen cases have no MISSING/ZERO state to express and a migrated
block would have to be authored (SC-3). The migration path (two rewritten files, new `supersedes`/historical
copies, two changed manifest rows, changed PINS/OID beyond additions, test 267/448 expectation changes, golden
re-derivation) is recorded as weighed and rejected; not unavoidable.

**Modules leaving the byte-identical set (C-7), with tests:** `public_snapshot.py` (test_public_snapshot_schema
T-1…T-6); `cases/projection.py`, `cases/brief.py` (test_case_projection T-7…T-9, test_case_brief T-10);
`trade_metrics.py` (T-11…T-13); `rules.py` (T-14…T-16); `narratives.py` + `config/decision_narratives.v1.yaml`
1.2.0→1.3.0 (T-17); `config.py` + `config/ui_strings.v1.yaml` 1.2.0→1.3.0 (T-18); `decision_engine.py` (T-19);
`genui.py` (T-20); `dossier.py` dossier_version 1.1→1.2 (T-21); `static/modules/renderers/decision.js` (T-22;
≤199 lines, no new module); `docs/core/04` §12 (T-23). `evidence.py` stays byte-identical (no partner logic).
Verification [8] is rewritten to an exact src modified-path oracle. Authority-hash rows changed by s14b become
exactly five: Core 04, Core 07, Core 09, `ui_strings`, `decision_narratives` (T10 oracle updated).

**Engine/catalogue carry (C-3…C-6):** `trade_metrics` final fallbacks name `PARTNER_DETAIL_MISSING:<reason>` or
`PARTNER_TRADE_OBSERVED_ZERO` (shapes unchanged); R3 and R4-D emit state-specific result codes
`PARTNER_DETAIL_MISSING` (with `result_values.partner_detail_reason`) / `PARTNER_TRADE_OBSERVED_ZERO`, DISABLED,
fired None — a stated refinement of C-3 (iii) because ledger text is catalogue-rendered per code; catalogue keys
in en and ar: `rule.r3.result.partner_detail_missing`, `rule.r3.result.partner_trade_observed_zero`,
`rule.r4-d.result.partner_detail_missing`, `rule.r4-d.result.partner_trade_observed_zero`,
`metric.hhi_partner_detail_missing`, `metric.hhi_partner_trade_zero`, `dossier.partner_detail{,_observed,_missing,_zero}`;
analysis/GenUI metric_grid/dossier carry `partner_detail` (None for 2.1.0); the HHI box never renders 0.

**SC-9 (rewritten):** a correct AM-2 C-2 merge is the accepted precondition — 721061 brief 1.1.0 with
`partner_detail.state` MISSING or OBSERVED, and the merged builder's 2.1.0 snapshot carrying either
`partner_observations: UNAVAILABLE` + ≥1 `-PARTNERS-ATTEMPT` passport (status `unresolved`, transformation
`PARTNER_DETAIL_MISSING:<reason>`, any governed reason) or an observed row list with the `P-COMTRADE-721061-PARTNERS`
passport and the WITS attempt passport still present. STOP only on: no `partner_detail` in the brief; UNAVAILABLE
with no ATTEMPT/ZERO passport (bare literal); brief/snapshot contradiction; missing execution_cap sentence. The
2.2.0 block is never expected from the merge: s14b's builder call produces it (INT-4a applies C-2 to the merged
`cases/**`, INT-4b builds; never by hand). INT-3 no longer greps `public_snapshot.py`.

**Sequence:** new task T4b (pinned-module and catalogue edits on doubles, RED-first) after T4 and before W1;
INT-3 (rewritten) → INT-4a (C-2) → INT-4b (build, first authoritative hashes; provisional/BF-4 hashes superseded)
→ INT-5/INT-6 → T6 records hashes, the merged 721061 state, AM-3 presence and R3/R4-D codes BEFORE finalising any
golden or pin. Single regeneration (T8) and single manifest run (T10) unchanged.

**Binding advisories restated (C-12):** MONITOR non-manufacture (OD-2; pin the unreachability test); SC-11
headroom ≈ 798 KB at the max estimate — measure after T8 before W2, never drop a screen; goldens/pins only after
T5 and [21]; worktree isolation, no git by the implementer, single GitHub queue, bytecode isolation; s14a overlays
bind (identity_exclusions 392190, observed row counts read-only, T-12 stands for 2.1.0 and is superseded by the
`partner_detail` references for 2.2.0).

Muhasib: plan only; no product edit, git change, network or `.env`; facts from reads and hashes (no engine run
needed). Deviations stated: R4-D state-specific code instead of a re-texted COVERAGE_INSUFFICIENT; `evidence.py`
unchanged; catalogue bumps to 1.3.0; block attempts carried as passport references. Assumed: s14a merge leaves
every pinned module and both catalogues at ab6211f bytes (OD-13/OD-14; rebase conflict is a STOP).
