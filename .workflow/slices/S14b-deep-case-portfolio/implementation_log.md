# S14b implementation log

## 2026-09-13T01:54:00Z — T0 preflight and provisional build

Seat: `implementer-sol`, slot 1. Persona and scope are recorded in
`persona.md` and `context.md`.

`PARALLEL_MODE`: s14a is an uncommitted sibling in the primary checkout.
This worktree is isolated. The primary checkout is read-only for the in-flight
case modules, case artifacts, and S14a implementation log named in the brief.

The approved-plan hashes were checked before implementation:

```bash
sha256sum \
  .autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14b.json \
  .autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14b-amendment-1.json \
  .autonomous-workflow/plans/s14-deep-cases-a/cycle-1/decomposition-1.json
```

```text
af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2  plan-1-s14b.json
8dc1b75d5ce91ce041ed82798b5c00c9fb60e1f7c29fe985f40aa88385eca7c7  plan-1-s14b-amendment-1.json
48741467ed2e3d6185cb0e5aac13b56d6c9d81847a3b114b960547740b877f3a  decomposition-1.json
```

Command recorded before execution:

```bash
test "$(git branch --show-current)" = \
  slice/s14b-deep-case-portfolio-scenarios-and-goldens &&
git merge-base --is-ancestor \
  ab6211f86307ad95a0e61f0597664023f09b7177 HEAD &&
echo BRANCH_OK
git rev-parse HEAD
git status --short
git -C /home/barami/projects/industrial-opportunity-resolution-mvp \
  status --short | wc -l
```

Result:

```text
BRANCH_OK
ab6211f86307ad95a0e61f0597664023f09b7177
?? .workflow/slices/S14b-deep-case-portfolio/
80
```

The count is only a read-only observation of the in-flight sibling; no primary
file was edited.

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python scripts/verify_integrity.py
```

Result:

```text
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python scripts/reconstruct_snapshot.py --all
```

Result (exit 0; the pre-existing pypdf warnings about rotated text, malformed
CMaps, and the recorded HTTP-wrapped PDF were emitted before these lines):

```text
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python scripts/demo_smoke.py
```

Result:

```text
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python scripts/validate_scenarios.py
```

Result:

```text
SCENARIO VALIDATION PASS (2 scenarios)
- SYN-MINISTRY-PP-001.json status=PASS; Gate B has demand,
  nameplate, factors and qualified availability PASS; demand layers
  INFORMATIONAL; the remaining five checks NOT_APPLICABLE;
  ground_truth_backtest PASS.
- SYN-MINISTRY-STEEL-001.json status=PASS; Gate B has demand,
  nameplate, factors and base-demand/probability/MES PASS; qualified
  availability and the four optional allocation/flow checks NOT_APPLICABLE;
  demand layers INFORMATIONAL; ground_truth_backtest PASS.
```

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest --collect-only -q \
  > /tmp/ior-s14b-t0-pytest-collect.txt
```

Result:

```text
2275 tests collected in 1.71s
```

Command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python -c \
  "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']), p['change_ref'])"
```

Result:

```text
VISUAL_MANIFEST_OK 56 S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
```

Commands recorded before execution:

```bash
docker version --format '{{.Server.Version}}'
for root in data/snapshots/public data/synthetic data/golden \
  browser_tests/baselines; do
  git rev-parse "HEAD:$root"
done
```

Results:

```text
29.7.2
data/snapshots/public  2ad27d6eaa9b3ce474f2c9ed62ecaa873ecd5e04
data/synthetic         3fb2247a36b57b85fc0f966717aad5502aa25f4b
data/golden            72618db654110823ec7a8d4dd6415a37e4554e33
browser_tests/baselines c2b3b66bbc6afaefe6e951772984d567cac53522
```

Provisional command recorded before execution:

```bash
PROVISIONAL=/tmp/ior-s14b-provisional-slot1-0452
mkdir -p "$PROVISIONAL"
for brief in \
  /home/barami/projects/industrial-opportunity-resolution-mvp/data/cases/briefs/CASE-BRIEF-SAU-H6-*-v1.json
do
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
  UV_OFFLINE=1 PATH=.venv/bin:$PATH \
  PYTHONPATH=/home/barami/projects/industrial-opportunity-resolution-mvp/src \
  .venv/bin/python -m ior_mvp.cases build \
    --brief "$brief" --out "$PROVISIONAL"
done
sha256sum "$PROVISIONAL"/*.json
```

Result — **PROVISIONAL PublicSnapshot 2.1.0; every hash is superseded at
INT-4b and is not a golden oracle**:

```text
868f5cd54330c41dac184655e9fb67e15d17ef23b1a5e6dcaf74f23fc838cd8d  PUBLIC-SAU-H6-392010-2026-09-12.json
23239bac2625cf322b9a78190d5039efdace534ae151f96ead68032920752bd0  PUBLIC-SAU-H6-721012-2026-09-12.json
3e8455f97963854fd8824dcf6bfb3a2be02c61a6e294ac9e698f22d65230fdae  PUBLIC-SAU-H6-721061-2026-09-12.json
6dcc35d3ada4664e51f161106be7dcb146a928ff92ba750635df47ba2ee9758a  PUBLIC-SAU-H6-760429-2026-09-12.json
65e7cc5c90bf19f89668ae337a6fe3f7387f5cdf10da1d7acf442219281116f7  PUBLIC-SAU-H6-760711-2026-09-12.json
```

Read-only state probe:

```text
392010 schema=2.1.0 rows=42 brief=PARTNER_DETAIL_OBSERVED attempts=1
721012 schema=2.1.0 rows=12 brief=PARTNER_DETAIL_OBSERVED attempts=1
721061 schema=2.1.0 rows=UNAVAILABLE brief=PARTNER_DETAIL_MISSING
       reason=COVERAGE_INDETERMINATE attempts=2
760429 schema=2.1.0 rows=43 brief=PARTNER_DETAIL_OBSERVED attempts=1
760711 schema=2.1.0 rows=27 brief=PARTNER_DETAIL_OBSERVED attempts=1
```

BF-15 preparation observations:

- Docker daemon responded with server version 29.7.2; canonical image use is
  still a T8 observation.
- The 76-entry estimate remains 11.11–11.79 MB against the 12,582,912-byte
  cap; actual compliance is unverified until T8.
- The in-flight builder CLI accepted `build --brief <path> --out <dir>` and
  emitted all five 2.1.0 snapshots.
- The merged-main 721061 state and the simulation sensitivity are deferred to
  INT-3/T6 as required by AM-1.

T0 result: baseline gates passed; the in-flight S14a builder moved from the
base-plan provisional hashes, as anticipated by AM-1. No stop condition
triggered.

## 2026-09-13T02:00:00Z — T1 five authored scenarios and provisional proof

The five scenario JSON files were generated mechanically from the gated
`scenario_designs[*].design` objects. They are canonical, sorted, indented
JSON with a trailing LF. OD-8 adds only:

```json
"narrative_metadata": {
  "arabic_text_status": "ANALYST_AUTHORED_DRAFT"
}
```

A semantic comparison removed that one metadata block and deep-compared every
remaining leaf with the retained planner drafts. Result:

```text
SCENARIO_DESIGN_EXACT_PLUS_OD8_METADATA SYN-MINISTRY-ALU-FOIL-001.json
SCENARIO_DESIGN_EXACT_PLUS_OD8_METADATA SYN-MINISTRY-ALU-PROFILES-001.json
SCENARIO_DESIGN_EXACT_PLUS_OD8_METADATA SYN-MINISTRY-GALVALUME-001.json
SCENARIO_DESIGN_EXACT_PLUS_OD8_METADATA SYN-MINISTRY-PE-FILM-001.json
SCENARIO_DESIGN_EXACT_PLUS_OD8_METADATA SYN-MINISTRY-TINPLATE-001.json
```

Final authored hashes at preparation:

```text
7fa4b2a370cbaf33494c8a817d24b5ef30b127c4636e7fe6eb9773eed3aa3764  SYN-MINISTRY-GALVALUME-001.json
5da1b652490cceb27a3a59d39892bea85c83a78c6537dea4bc7bccd201a17024  SYN-MINISTRY-TINPLATE-001.json
35808c7558bff6e7ba6fe6d0986920a2a523a3487054e6b03ac97fca7e7dcdb6  SYN-MINISTRY-ALU-FOIL-001.json
a96ae1b49db2c24d538aebdbf3e6109b174e0d9e583d28b5c727c400d378d3e9  SYN-MINISTRY-ALU-PROFILES-001.json
74afb97f76b98acd4af58bd1be5eb159ce78b8c1f4a2c6d8feb5ecd1a397f6de  SYN-MINISTRY-PE-FILM-001.json
```

Dry-run command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python /tmp/ior-s14b-dry-run-slot1.py
```

The post-T4b repeat against the same provisional 2.1.0 snapshots produced:

```text
SAU-H6-721061
  GATE_B PASS
  checks: PASS, NOT_APPLICABLE, PASS, NOT_APPLICABLE, INFORMATIONAL,
          NOT_APPLICABLE, NOT_APPLICABLE, NOT_APPLICABLE,
          NOT_APPLICABLE, PASS
  PUBLIC INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED
         fired [R0,R1-D,R12] material [R1-D]
  SIMULATED ADVANCE 3 ALL_ADVANCE_GATES_PASS BACKTEST True
  PUBLIC_FINGERPRINT_UNCHANGED True
  designed/computed: D*=0.25; effective=24.872; gap=23.128;
    unsupported NPV=-4.743; IRR=0.08686; S*=5.0; ΔNV=82.0;
    competition=1.1494; route=3

SAU-H6-721012
  GATE_B PASS
  checks: PASS, NOT_APPLICABLE, PASS, NOT_APPLICABLE, INFORMATIONAL,
          NOT_APPLICABLE, NOT_APPLICABLE, NOT_APPLICABLE,
          NOT_APPLICABLE, PASS
  PUBLIC INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED
         fired [R0,R1-D,R2,R4-D,R12] material [R1-D,R2]
  SIMULATED ADVANCE 7 ALL_ADVANCE_GATES_PASS BACKTEST True
  PUBLIC_FINGERPRINT_UNCHANGED True
  designed/computed: D*=0.9; effective=0.0; gap=95.0;
    unsupported NPV=-136.839; IRR=0.06986; S*=137.0; ΔNV=220.0;
    competition=1.125; route=7

SAU-H6-760711
  GATE_B PASS
  checks: PASS, NOT_APPLICABLE, PASS, NOT_APPLICABLE, INFORMATIONAL,
          NOT_APPLICABLE, NOT_APPLICABLE, NOT_APPLICABLE,
          NOT_APPLICABLE, PASS
  PUBLIC INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED
         fired [R0,R1-D,R2,R12] material [R1-D,R2]
  SIMULATED ADVANCE 6 ALL_ADVANCE_GATES_PASS BACKTEST True
  PUBLIC_FINGERPRINT_UNCHANGED True
  designed/computed: D*=0.5667; effective=0.0; gap=40.0;
    unsupported NPV=-50.09; IRR=0.07904; S*=51.0; ΔNV=172.0;
    competition=1.0588; route=6

SAU-H6-760429
  GATE_B PASS
  checks: PASS, NOT_APPLICABLE, PASS, PASS, INFORMATIONAL, PASS, PASS,
          NOT_APPLICABLE, PASS, PASS
  PUBLIC INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED
         fired [R0,R1-D,R2,R3,R4-D,R5,R9-S,R10,R12]
         material [R1-D,R2,R5,R9-S]
  SIMULATED ADVANCE 4 ALL_ADVANCE_GATES_PASS BACKTEST True
  PUBLIC_FINGERPRINT_UNCHANGED True
  designed/computed: D*=0.25; formula=2.497; qualified=2.5; gap=3.5;
    unsupported NPV=1.19; IRR=0.16319; S*=0.0; ΔNV=31.0;
    competition=1.1725; route=4

SAU-H6-392010
  GATE_B PASS
  checks: PASS, NOT_APPLICABLE, PASS, PASS, INFORMATIONAL, PASS,
          NOT_APPLICABLE, NOT_APPLICABLE, NOT_APPLICABLE,
          NOT_APPLICABLE
  PUBLIC INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED
         fired [R0,R1-D,R2,R4-D,R12] material [R1-D,R2]
  SIMULATED REJECT 0 HARD_EXCLUSION_SATISFIED BACKTEST True
  PUBLIC_FINGERPRINT_UNCHANGED True
  designed/computed: D*=0.0; formula=23.085; qualified=24.0; gap=-8.0;
    S*=0.0; competition=None; route=0; EX-04 SATISFIED

DRY_RUN_FAILURES 0
```

Every printed numeric pin equalled `scenario_designs[*].computed`; every
synthetic row was Class D, generator-sourced, flagged and labelled. No scenario
value was adjusted.

T1 RED command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest -q tests/test_s14b_portfolio.py
```

Initial result:

```text
42 failed, 5 passed in 0.30s
```

The five metadata/contract nodes passed. Forty-one nodes failed exactly at
`integration snapshot is pending`; the AM-1 zero-vs-missing double failed
because R3 still returned `BOTH_BASES_NOT_CALCULABLE`. T4b later made that
double GREEN. The `_scaled` six-decimal regression test was then added from
AM-3 VF-8 and is intentionally RED until `ior_mvp.cases.projection` arrives
through the s14a integration.

## 2026-09-13T02:08:00Z — T2 golden and seven-case contracts

Changed the project golden list from two to seven in OD-7 order, appended ten
named golden tests after the frozen first 119 lines, and extended the scenario,
API, performance and synthetic-isolation inventories.

Commands and results:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest -q tests/test_golden_cases.py \
  -k 'steel or polypropylene'
```

```text
4 passed, 10 deselected in 0.15s
```

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest -q tests/test_golden_cases.py \
  -k 'galvalume or tinplate or alu_foil or alu_profiles or pe_film'
```

```text
10 failed, 4 deselected in 0.16s
```

All ten fail with `Unknown opportunity: SAU-H6-…`, the intended integration
RED.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest -q \
  tests/test_scenario_validation.py::test_repository_scenario_validator_passes_current_fixtures \
  tests/test_scenario_validation.py::test_validator_reports_exact_ground_truth_for_all_scenarios \
  tests/test_api.py::test_opportunity_list_modes
```

```text
SCENARIO VALIDATION FAIL (5/7 scenarios failed)
  each new scenario: No public case matches scenario opportunity_id
API opportunity count: expected 7, actual 2
3 failed, 1 warning in 0.59s
```

Prefix oracle:

```text
GOLDEN_FIRST_119_LINES_BYTE_IDENTICAL_PASS
```

## 2026-09-13T02:15:00Z — T3 browser harness preparation

`harness.CASES` is seven in the governed order. Journey counts are derived
from `CASES`; the two frozen exact rule strings remain pinned; new-case rows
use their localized API values; unlock counts are API-derived with the
designed simulated counts `1/1/1/0/5`. The new ten-node EN/AR journey checks
observed/calculated public evidence, unresolved evidence as missing rather
than zero, visible data unlocks, absent public synthetic labels, and visible
Class-D synthetic rows/dual states in simulated mode. The accessibility tab
order gains exactly five case-card controls. The dossier HS token now derives
H0/H6 from the case id.

Collection command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest --collect-only -q browser_tests -m 'e2e and not visual'
```

```text
332/336 tests collected (4 deselected) in 0.10s
```

RED command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/pytest -q \
  browser_tests/test_journeys.py::test_portfolio_loads_expected_cases_and_states \
  browser_tests/test_journeys.py::test_new_case_view_distinguishes_observed_missing_and_simulated \
  browser_tests/test_accessibility.py::test_keyboard_tab_order_reaches_every_interactive_control_with_visible_focus
```

```text
30 failed in 312.03s
Locator expected count 7; actual value 2.
```

That common failure is the intended T5 boundary, not a browser or accessibility
defect.

## 2026-09-13T02:20:00Z — T4 visual matrix code only

Added the five `journey-g-*-public-workspace` identities and captures after
the 56 existing scenes. No baseline, manifest or digest was regenerated.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc \
UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src \
.venv/bin/python - <<'PY'
from browser_tests.visual_baselines import _expected_matrix, validate_manifest
assert len(_expected_matrix()) == 76
print("EXPECTED_VISUAL_MATRIX", len(_expected_matrix()))
try:
    validate_manifest()
except ValueError as exc:
    assert str(exc) == "visual baseline matrix is incomplete"
    print("VISUAL_RED", exc)
PY
```

```text
EXPECTED_VISUAL_MATRIX 76
VISUAL_RED visual baseline matrix is incomplete
```

The named visual pytest produced four setup errors with that exact expected
message; canonical regeneration remains exclusively T8. Budget remains the
approved estimate: 11.11–11.79 MB against 12,582,912 bytes, unverified until
T8.

## 2026-09-13T02:24:00Z — T4b additive PublicSnapshot 2.2 carry

RED-first additions cover:

- accepted 2.1.0/2.2.0 versions and strict version-gated top-level keys;
- exact `partner_detail` keys, tri-state, reason vocabulary and cross-rules;
- MISSING and OBSERVED ZERO metric reasons;
- state-specific R3/R4-D codes without changing 2.1.0 or observed behavior;
- narrative/UI catalogue 1.3.0 parity;
- analysis, GenUI, dossier 1.2 and static renderer projections;
- no numeric HHI for MISSING/ZERO;
- the deferred Core 04/07 realized-text contract.

Initial RED:

```text
19 failed, 3 passed, 1 warning in 0.92s
```

The three preservation tests already GREEN were: 2.1.0 rejects
`partner_detail` as an extra key; generic metric fallback reasons remain
byte-exact; frozen/observed rule paths retain their codes.

Implementation:

- PublicSnapshot current builder target `2.2.0`; supported versions are
  `{2.1.0, 2.2.0}`; frozen 2.1.0 semantics and bytes are untouched.
- Missing reasons equal the worktree `UnavailableReason` enum plus
  `NOT_ACQUIRED` and `REVISION_MISMATCH`, without a runtime acquisition
  import. INT-3 must add `PARTNER_DESCRIPTIONS_UNAVAILABLE` if merged AM-3
  carries it.
- OBSERVED attempts accept
  `PARTNER_DETAIL_ATTEMPT_SUPERSEDED:`; MISSING attempts retain
  `PARTNER_DETAIL_MISSING:`.
- Trade metrics and R3/R4-D distinguish MISSING from OBSERVED ZERO while
  preserving output shapes and generic 2.1.0 branches.
- Both governed catalogues advance 1.2.0 → 1.3.0 with exact EN/AR parity;
  no decision threshold changes.
- Analysis, metric-grid and dossier carry the additive block; missing HHI
  stays the unavailable glyph, never numeric zero.

Focused GREEN after one test correction (`NOT_CALCULABLE` is the existing
non-numeric metric sentinel, not `None`):

```text
21 passed, 1 warning in 0.90s
```

Complete component regression:

```text
11 failed, 270 passed, 1 warning in 3.31s
```

The eleven failures are exactly `test_opportunity_list_modes` plus the ten
new golden tests, all awaiting the five integrated snapshots. An additive
expected-payload fixture was updated for catalogue 1.3.0 and the two new null
projection fields; its direct API oracle is GREEN.

Static gates:

```text
THRESHOLD LITERAL SCAN PASS (71 Python files; 23 configured numeric values)
ES MODULE CHECK PASS (27 files)
decision.js: 124 lines (limit 199)
```

T4b source-list oracle:

```text
src/ior_mvp/config.py
src/ior_mvp/decision_engine.py
src/ior_mvp/dossier.py
src/ior_mvp/genui.py
src/ior_mvp/narratives.py
src/ior_mvp/public_snapshot.py
src/ior_mvp/rules.py
src/ior_mvp/static/modules/renderers/decision.js
src/ior_mvp/trade_metrics.py
```

This is exactly AM-1 C-7 minus the two post-rebase `cases/**` paths.
`evidence.py` remains byte-identical, as approved.

Core 04's merged §12 does not exist at base `ab6211f`, and both Core 04 and
Core 07 are integration/shared authority files. Their T-23 contract remains
RED until the merged s14a section is available; editing a substitute section
before W1 would violate the integration seam.

## 2026-09-13T02:38:00Z — final provisional refresh after sibling AM-3 movement

The read-only sibling moved while preparation was running: 721061 changed from
MISSING/COVERAGE_INDETERMINATE to OBSERVED with seven partner rows and four
attempt records. A second fresh `/tmp` build was therefore run from the current
primary case artifacts. No worktree snapshot was written.

```text
868f5cd54330c41dac184655e9fb67e15d17ef23b1a5e6dcaf74f23fc838cd8d  PUBLIC-SAU-H6-392010-2026-09-12.json
23239bac2625cf322b9a78190d5039efdace534ae151f96ead68032920752bd0  PUBLIC-SAU-H6-721012-2026-09-12.json
6ca534fa64c71847a702dad1c7e568e49c8671dafb6eedc5c86bbb06078ff1d9  PUBLIC-SAU-H6-721061-2026-09-12.json
6dcc35d3ada4664e51f161106be7dcb146a928ff92ba750635df47ba2ee9758a  PUBLIC-SAU-H6-760429-2026-09-12.json
65e7cc5c90bf19f89668ae337a6fe3f7387f5cdf10da1d7acf442219281116f7  PUBLIC-SAU-H6-760711-2026-09-12.json
FINAL_PROVISIONAL_721061 2.1.0 list 7 PARTNER_DETAIL_OBSERVED None 4
```

These are still provisional 2.1.0 hashes and are superseded at INT-4b.

The five-scenario dry run was repeated against this final provisional set:

```text
721061 public: INVESTIGATE / null / ROUTE_CHANGING_EVIDENCE_UNRESOLVED
  fired [R0,R1-D,R3,R10,R12]; material [R1-D]
  simulated: designed ADVANCE/3; computed ADVANCE/3; Gate B PASS;
  back-test true; fingerprint unchanged; all numeric pins exact.
  The observed partner rows add public R3 to support signals:
  designed provisional [R8], computed [R3,R8]. This is the approved AM-2/AM-3
  sensitivity; state, route, gap constraint, economics and precedence do not
  change.

721012 public INVESTIGATE; designed/computed ADVANCE/7; Gate B PASS.
760711 public INVESTIGATE; designed/computed ADVANCE/6; Gate B PASS.
760429 public INVESTIGATE; designed/computed ADVANCE/4; Gate B PASS.
392010 public INVESTIGATE; designed/computed REJECT/0; Gate B PASS.
PUBLIC_FINGERPRINT_UNCHANGED True ×5
DRY_RUN_FAILURES 0
```

No SC-4 or SC-10 stop was triggered: all planted truths still match by
computation and every public state remains INVESTIGATE.

## 2026-09-13T02:45:00Z — PREP_HANDOFF_W1_PENDING muhasib

Self-audit result: `MUHASABAH_PASS` for the authorized preparation boundary;
this is an implementation hand-off, not self-approval.

Verified:

- Approved plan, AM-1 and decomposition hashes match the brief.
- Worktree branch remains
  `slice/s14b-deep-case-portfolio-scenarios-and-goldens` at
  `ab6211f86307ad95a0e61f0597664023f09b7177`; index is empty.
- No public snapshot, historical file, visual baseline, Core 06 file or
  `.autonomous-workflow/**` tracked byte changed.
- Five authored scenarios remain untracked and deep-equal the approved planner
  drafts after removing only the OD-8 analyst-authorship metadata.
- Latest provisional dry run: Gate B PASS ×5, planted truth match ×5, public
  fingerprint unchanged ×5, all public states INVESTIGATE and no scenario
  value changed.
- T4b schema/rule/catalogue/view tests are GREEN; the self-audit added and
  verified a malformed-attempt-id fail-closed case and two distinct
  SUPERSEDED attempt passports for the OBSERVED double.
- Fresh full pytest result is exactly
  `108 failed, 2294 passed, 1 warning in 41.69s`; every failure maps to the
  intentionally absent integrated snapshots/builder/Core text or the deferred
  T8/W2 visual/frozen state.
- Complete T4b component result is
  `11 failed, 270 passed, 1 warning in 3.29s`; the failures are exactly the
  API count plus ten new goldens awaiting integration.
- Four original golden tests pass. Threshold scan, ES-module scan,
  prohibited-file scan, absolute-path scan, `git diff --check`, frozen-byte
  checks and IDE diagnostics pass.
- Every Python invocation used bytecode isolation; no network request, `.env`
  read, manifest generation, baseline regeneration, staging, commit, fetch,
  rebase, push or PR action occurred.

Assumed/deferred:

- The primary checkout now has a different read-only HEAD than the preparation
  base, but no explicit owner message has declared the s14a squash merge `M`,
  WIP W1 or rebase. This seat does not infer those gates from repository state.
- INT-3 must read the merged `UnavailableReason` enum and add
  `PARTNER_DESCRIPTIONS_UNAVAILABLE` to the local reason set if AM-3 carries
  it; current T-6 correctly matches the preparation-base enum.
- The merged Core 04 §12 text, authoritative 2.2.0 builder bytes, final 721061
  tri-state, snapshot/scenario hashes and final fired sets remain unverified
  until INT-3/INT-4b/T6.
- Visual drift, byte budgets and canonical image availability remain
  unverified until T8; independent reviewer approval, CI, PR and merge remain
  later gates.

Stop-condition audit: none triggered. The observed sibling movement was
handled by a new read-only provisional build and recomputation; no value was
tuned and no frozen artifact was copied into the worktree.

State: `PREP_HANDOFF_W1_PENDING`. Stop here until the owner lead explicitly
reports `M`, creates WIP W1 and rebases this branch.

## 2026-09-13T03:05:16Z — Integration delta (INT-3 through T6)

Owner-reported and read-only verified integration identities:

```text
s14a merge M   ec859f72a1b438b7e5946334f60a4d72cbbf1fb1
origin/main     1289e31e50c1d835760f6943e697d6d537ac0a18
W1' / HEAD      4068a80f8a6231e41c54900d0d7659d4f6e71f26
```

OD-14 records the sole additive rebase conflict in
`tests/test_integrity_contract.py`. The read-only command
`git diff 1289e31 4068a80 -- tests/test_integrity_contract.py` shows only the
appended s14b function after s14a's function; both were retained in that
order.

INT-3 verified the rewritten SC-9 before editing `cases/**`:

```text
BRIEF 1.1.0 PARTNER_DETAIL_OBSERVED None 4
SNAPSHOT_SCHEMA 2.1.0
PARTNER_ROWS 7
P-COMTRADE-721061-PARTNERS calculated
P-COMTRADE-721061-PARTNERS-ATTEMPT unresolved
  PARTNER_DETAIL_ATTEMPT_SUPERSEDED:VARIANT_NOT_TRANSMITTED
P-COMTRADE-721061-PARTNERS-ATTEMPT-2 unresolved
  PARTNER_DETAIL_ATTEMPT_SUPERSEDED:COVERAGE_INDETERMINATE
P-WITS-721061-PARTNERS-ATTEMPT unresolved
  PARTNER_DETAIL_ATTEMPT_SUPERSEDED:FORMAT_NOT_PARSEABLE
execution_cap contains " Partner detail: PARTNER_DETAIL_OBSERVED "
```

The merged enum has 20 members, including
`PARTNER_DESCRIPTIONS_UNAVAILABLE`. The five briefs, selection record
`CASE-SELECTION-S14-250cd516de0a`, Comtrade partner snapshot and three
partner snapshots were present. Baseline case reconstruction passed with
zero committed case snapshots. Scenario validation had exactly the expected
five `No public case matches` failures before INT-4b; the two frozen scenarios
passed. Integrity was expected RED because W1's two catalogue changes are
not authority-hash-pinned until T10:
`ui_strings.v1.yaml` and `decision_narratives.v1.yaml`.

INT-4a was test-first. Five focused tests failed because the merged builder
still emitted 2.1.0/no `partner_detail` and CaseBrief owned duplicate
vocabularies. The implementation imports both vocabularies from
`public_snapshot.py`, includes the merged enum member, emits schema 2.2.0 and
derives the exact partner block from the brief plus emitted passport IDs.
The full projection/brief/schema suites then passed: `100 passed`.

INT-4b invoked only `python -m ior_mvp.cases build`; no snapshot was edited by
hand. Two independent `/tmp` builds were byte-identical across all five
files, then the same builder wrote the worktree files and a byte comparison
passed. First authoritative 2.2.0 hashes:

```text
700cf8758bb9e633afd7a2bd6dc55e227100b49d08fb8d6ed44573584aedeb94  PUBLIC-SAU-H6-392010-2026-09-12.json
51b15c094cf21daae5e36f5eb0dcad47a67ca3ee1d14c8e7954065e4d4abc7ea  PUBLIC-SAU-H6-721012-2026-09-12.json
b0bc67f7eb53a1b5da3cf29918cbc27a11c1d9d19b7a61ba60df78d73b23fb19  PUBLIC-SAU-H6-721061-2026-09-12.json
9e36b94039292ff20ea3985d762bb5c072e4ea3cf38526c233ec64f351ba4a08  PUBLIC-SAU-H6-760429-2026-09-12.json
58d556fe8b022a4146c83c6831bea15c1e07a6532787443f50718d062af343e2  PUBLIC-SAU-H6-760711-2026-09-12.json
```

`python scripts/reconstruct_snapshot.py --all --no-check-manifest` passed:
case 5/5; acquisition 4 snapshots/34 artifacts; documents 20/20; entities
2 artifacts/44 links; screening 1 snapshot. Direct case reconstruction also
reported `CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)`.

T6 verification [21] was recorded before final golden assertions. Every
public case computed `INVESTIGATE / null /
ROUTE_CHANGING_EVIDENCE_UNRESOLVED`; every simulation matched its planted
truth and Gate B passed:

```text
721061 public fired R0,R1-D,R3,R10,R12; partner OBSERVED;
  R3 FULL/CONCENTRATED_ON_CALCULABLE_BASIS;
  R4-D DISABLED/COVERAGE_INSUFFICIENT;
  designed/computed ADVANCE/3; Gate B PASS
721012 public fired R0,R1-D,R2,R4-D,R12; partner OBSERVED;
  R3 DISABLED/BOTH_BASES_NOT_CALCULABLE;
  R4-D DEGRADED/DESCRIPTIVE_DISPERSION;
  designed/computed ADVANCE/7; Gate B PASS
760711 public fired R0,R1-D,R2,R12; partner OBSERVED;
  R3 DISABLED/BOTH_BASES_NOT_CALCULABLE;
  R4-D DISABLED/COVERAGE_INSUFFICIENT;
  designed/computed ADVANCE/6; Gate B PASS
760429 public fired R0,R1-D,R2,R3,R4-D,R5,R9-S,R10,R12; partner OBSERVED;
  R3 FULL/QUANTITY_CONCENTRATED_VALUE_NOT_CALCULABLE;
  R4-D DEGRADED/DESCRIPTIVE_DISPERSION;
  designed/computed ADVANCE/4; Gate B PASS
392010 public fired R0,R1-D,R2,R4-D,R12; partner OBSERVED;
  R3 DISABLED/BOTH_BASES_NOT_CALCULABLE;
  R4-D DEGRADED/DESCRIPTIVE_DISPERSION;
  designed/computed REJECT/0; Gate B PASS
```

Final scenario hashes are, in the same case order:
`7fa4b2a370cbaf33494c8a817d24b5ef30b127c4636e7fe6eb9773eed3aa3764`,
`5da1b652490cceb27a3a59d39892bea85c83a78c6537dea4bc7bccd201a17024`,
`35808c7558bff6e7ba6fe6d0986920a2a523a3487054e6b03ac97fca7e7dcdb6`,
`a96ae1b49db2c24d538aebdbf3e6109b174e0d9e583d28b5c727c400d378d3e9`,
`74afb97f76b98acd4af58bd1be5eb159ce78b8c1f4a2c6d8feb5ecd1a397f6de`.

After those recordings, golden assertions were updated only for observed
shape: 721061's fired set adds computed R3/R10; the assessment key is the
existing `evidence_class`; no-action REJECT legitimately omits the route
competition ratio/warning. The integrated case/portfolio/golden/scenario/API
suites passed: `136 passed, 1 warning`.

No SC-1 through SC-4, SC-9 or SC-10 stop condition triggered. No scenario
value, brief, selection record, partner snapshot, merged s14a artifact or
frozen 2.1.0 root was modified.

## 2026-09-13T03:26:15Z — T7 functional browser integration

The first full `make e2e-functional` run was RED:

```text
10 failed, 322 passed, 4 deselected, 36 errors
```

Two integration defects were isolated test-first. Tinplate carries an
`UNAVAILABLE` trade-series point; `trade.js` passed that string into the SVG
path and rendered `NaN`. A static executable regression first reproduced
`M0,1 L1,UNAVAILABLE L2,3`, then the renderer was changed to accept only
finite numeric values, break paths and omit circles at missing points,
preserve original x positions, and guard zero maxima. This necessary
integration fix adds
`src/ior_mvp/static/modules/renderers/trade.js` beyond AM-1 C-7 and must be
called out to the reviewer.

The journey assertion also compared visible public-mode evidence unlocks with
resolved simulation missing facts. It now derives the visible count from the
manifest's `localized_missing_facts`, matching the GenUI public branch.

Focused GREEN evidence:

```text
static frontend + ES regression: 5 passed
ES MODULE CHECK PASS (27 files)
focused browser journey matrix: 38 passed, 58 deselected
```

The required clean full rerun then passed:

```text
make e2e-functional
332 passed, 4 deselected in 517.16s (0:08:37)
```

This covers `CASES=7` across public/simulated modes and English/Arabic
locales. No BrowserFailureCollector record remained. No scenario value was
changed and no stop condition triggered.

## 2026-09-13T03:34:13Z — T8 canonical visuals and W2 boundary

Exactly one canonical update was executed, using change reference
`S14b-deep-case-portfolio-scenarios-and-goldens:af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2`.
It reported the required Chromium assertion and `4 passed, 332 deselected`.
The regenerated manifest validates at 76 entries. Total encoded bytes are
11,116,140 of 12,582,912; the largest file is 230,892 of 614,400 bytes.
Ownership and absolute-path checks pass.

The 56-entry comparison against s14a merge `ec859f7` has zero findings:
eight portfolio entries changed inside the approved KPI/compact-section
region; eight desktop workspaces changed materially in the select control
with their remainder passing tolerance; eight tablet workspaces pass
whole-image tolerance; all 32 dossier/screening entries pass tolerance.
Seven screening files have byte-level encoder drift but zero significant
pixels; no dossier file changed. The full table, DOM rectangles and crops are
under the approved `visual-s14b/` evidence directory. Host visual compare
passed all four nodes.

The pre-existing visual contract still expected 56 entries and omitted the
five new screen identities. The full-suite RED exposed this T8 expectation
gap; adding the five screens and replacing both exact counts with 76 made its
21 tests GREEN. This is a test-only T8 deviation required by the already
approved 76-entry matrix.

Future tree OIDs were computed through an isolated temporary index/object
store, leaving the worktree index untouched:

```text
data/snapshots/public   a67a921c1909c20e1afe2647e6f41a792cecd08a
data/synthetic          7459beb8a8777fe33592c314bac54de0a1833f25
data/golden             72618db654110823ec7a8d4dd6415a37e4554e33
browser_tests/baselines 709325b65f4fb567f10d3fa23a0139b1ef0de602
```

Final worktree pytest is `5 failed, 2542 passed, 1 warning in 53.65s`.
Three frozen-tree tests are expected RED until owner W2 commits the pinned
roots. Two shared integrity-contract tests remain expected RED until T9:
the pre-build `(0 snapshots, 5 briefs)` recording must become `(5, 5)`, and
Core 04/07 still lack the approved final partner-detail sentences.

No SC-1 through SC-13 condition is active. SC-5 was checked with measured
regions and returned `DRIFT_FAILURES 0`; SC-11 did not trigger. HEAD remains
W1' and the real index remains empty.

State: `T8_HANDOFF_W2_PENDING`.

## 2026-09-13T03:52:00Z — OD-15 corrections prepared; canonical stop

Owner W2 was verified at
`ec2eae10e924983ff774242dc59766dd69c1e0cb`; the real index was empty and
`tests/test_frozen_public_evidence_pins.py` had passed for the owner.

OD-15(a) requires another canonical regeneration. Before editing, the
portfolio chip was measured inside all eight portfolio captures:

```text
EN desktop [1213,222,1398,257]  EN tablet [262,267,447,302]
AR desktop [42,222,218,257]     AR tablet [586,268,762,303]
```

The same rectangles apply in public and simulated modes. The correction
therefore cannot be masked from the governed matrix. The prepared
implementation computes both values after the selected analysis loads:
seven opportunities and the active rule-ledger length (15 public; 19
simulated), interpolated through bilingual `portfolio.chip` catalogue
templates. Locale rerender recomputes the chip from current state.

OD-15(b) is also prepared. `decision_object_status` now fails closed through
three explicit catalogue keys instead of replacing underscores in raw
English. The Arabic generic-HS6 label is
`رمز النظام المنسق العام فقط`; the public decision-subject paragraph for
all seven cases is covered by the UX-01 parity predicate.

RED-first browser result:

```text
11 failed, 92 deselected in 62.58s
```

The failures were exactly four stale portfolio-chip assertions and seven
English decision-subject labels. After implementation, catalogue/static
tests passed 42 nodes, the ES module check passed 27 files, and the focused
browser set passed:

```text
11 passed, 92 deselected in 7.43s
```

The visual provenance oracle now intentionally reports exactly four stale
pinned paths:

```text
config/ui_strings.v1.yaml
src/ior_mvp/static/modules/events.js
src/ior_mvp/static/modules/portfolio.js
src/ior_mvp/static/modules/renderers/decision.js
```

No second canonical regeneration was run. T9–T12 have not started.

State: `CHIP_REGEN_PENDING`.

## 2026-09-13T04:12:00Z — OD-16 T8b canonical correction

OD-16 authorized exactly one second canonical update under the original
change reference. The first corrected functional matrix passed 339 selected
nodes. Before regeneration, a new pixel-preservation assertion exposed that
the initial English catalogue labels used title case and would unnecessarily
change English workspace pixels:

```text
1 failed: test_decision_object_status_preserves_english_pixels_and_localizes_arabic
```

The English labels were restored byte-for-render to the previous lowercase
status text while Arabic remains catalogue-localized. Catalogue/static tests
then passed 43 nodes and the required final full rerun passed:

```text
make e2e-functional
339 passed, 4 deselected in 521.47s (0:08:41)
```

Authorized canonical execution 2:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14b-pyc UV_OFFLINE=1 PATH=.venv/bin:$PATH PYTHONPATH=src IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF="S14b-deep-case-portfolio-scenarios-and-goldens:af5ae5d870eeedb8383d5f71756a189dc30dfa3f78d11c1a7b5d42a0e97879f2" make e2e-update-baselines
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 339 deselected in 78.01s (0:01:18)
```

The validated output is 76 entries, 11,117,096 governed image bytes and
11,157,252 complete-root bytes. The largest image is 230,892 bytes. Ownership
and absolute-path checks pass; SC-11 did not trigger.

The W2-to-T8b comparison changed exactly 15 WebP files:

- all eight portfolio entries, with every significant pixel inside the
  measured chip rectangles;
- seven Arabic desktop public-workspace entries (steel, polypropylene and the
  five new cases), with every significant pixel inside the decision-subject
  card;
- zero Arabic tablet workspace entries because that card is below the captured
  viewport; zero English workspace, dossier or screening entries.

`DRIFT_FAILURES 0`. The 76-row extension and paired before/after/diff crops are
recorded under `visual-s14b/drift-t8b.*` and `visual-s14b/crops-t8b/`.

Host comparison passed:

```text
make e2e-visual
4 passed, 339 deselected in 58.73s
```

An isolated temporary index/object store computed the future baseline tree
OID as `0259f800dbcc4c3726549b3af2ed78cc570ef281`; the pin constant now carries
that value. The pin suite is expected RED until W2':
`2 failed, 15 passed`. W2' is exactly 15 WebPs, manifest, digest and the pin
test (18 paths); no source module belongs to W2'.

ADR-022 records both canonical commands/results, the owner conflict
resolution and the two drift receipts. No manifest command or T10 work ran.
The real index remains empty.

State: `T8b_HANDOFF_W2PRIME_PENDING`.

## 2026-09-13T04:57:00Z — T9 through T11

Owner W2' is `5354a6f230bfee24e3aed97ad8120f804e97f603`; its
baseline tree and pin are `0259f800…`. T9 finalized Core 04 §12, Core 07
§7.8/§7.9, Core 09 §2.4/§2.7/§7/§10, the route matrix, ADR-022,
KL-100/KL-104…KL-108 and the control documents. MONITOR is recorded
UNDEMONSTRATED for S14b: every new public case fires material R1-D, so the
route-0 predicate requiring an empty material-trigger set is false.

The T9 documentation contracts first failed, then passed. The first full
pre-manifest regression exposed two expected integration recordings: browser
inventory 32→33 after OD-15 parity coverage and case reconstruction 0→5
snapshots. Those exact assertions were updated; the final pre-manifest run was
`2549 passed, 1 warning`.

T10 receipt was written before invocation at `2026-09-13T04:25:49Z`.
`scripts/build_manifests.py` ran exactly once. Its chained immediate oracle
reported:

```text
SNAPSHOT_ROWS 628 -> 638
SNAPSHOT_ADDED 10
SNAPSHOT_PRIOR_CHANGED 0
AUTHORITY_ROWS 19 -> 19
AUTHORITY_CHANGED 5
config/decision_narratives.v1.yaml
config/ui_strings.v1.yaml
docs/core/04_CANONICAL_DATA_MODEL.md
docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
MANIFEST_DELTA_ORACLE_PASS
INTEGRITY PASS
```

The first post-generation `make ci` run correctly exposed two stale partition
allowlists for the ten newly manifested public/scenario paths. The tests were
tightened to allow exactly those ten paths while continuing to reject
arbitrary public and synthetic additions. Final local `make ci` exited 0:
2,549 Python tests, 339 functional and four visual browser nodes.

T11 copied the candidate to `/tmp/ior-s14b-portability-t11`, where integrity,
seven-scenario validation, all reconstruction stages and smoke passed;
`ABSOLUTE_PATHS_PASS` and `PORTABILITY_GATE_PASS` were emitted. A scratch
clone committed the candidate on W2' as local-only commit `4e39cc8`. Its first
offline Python 3.14 run passed reconstruction, smoke and all 2,549 tests but
stopped before browser tests because the CPython 3.14 Pillow wheel was absent
from the local cache. The same unchanged commit was rerun with the project CI
Python 3.12 interpreter and `CI=1`; it exited 0 with 2,549 + 339 + 4.

No network, `.env`, real-index mutation, second manifest run, PR, merge or
approval occurred. T12 identity remains.

## 2026-09-13T05:00:00Z — T12 uncommitted review hand-off

IAC-6 used `base =
5354a6f230bfee24e3aed97ad8120f804e97f603`, literal
`wip_parent = 1289e31`, and excluded both
`.workflow/slices/S14-deep-cases-a/**` and
`.workflow/slices/S14b-deep-case-portfolio/**`. The payload has exactly
`base`, `wip_parent`, `files`; each row has `path`, `sha256`, `bytes`; compact
sorted-key UTF-8 serialization ends with LF.

```text
CANDIDATE_IDENTITY 6307ccb311c208f4874d96ec48386f2411a5134a96d3e592d2b88347e2e3d156
CANDIDATE_FILE_COUNT 121
INDEX_EMPTY_PASS
STATE_JSON_VALID_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
17 frozen-pin tests passed
```

Commit/delta inventory:

```text
W1' 4068a80f8a6231e41c54900d0d7659d4f6e71f26 — 36 paths
W2  ec2eae10e924983ff774242dc59766dd69c1e0cb — 64 paths
W2' 5354a6f230bfee24e3aed97ad8120f804e97f603 — 18 paths
uncommitted product/control delta — 31 paths
```

Final `pytest -q`: `2549 passed, 1 warning in 48.61s`. No stop condition is
active. Work remains provisional and uncommitted pending Supervisor and
independent reviewer gates.

State: `T12_HANDOFF_REVIEW_PENDING`.

### Muhasib correction — exact final scratch identity

The hand-off audit found that local scratch commit `4e39cc8` predated the
final state/progress/traceability recording. Product bytes were equal, but the
candidate identity was not. A fresh local clone therefore applied the complete
121-file candidate to W2', committed it as
`d41ed7df5c1d942ac5fb67abdc1437232a2deb13`, and ran
`CI=1 UV_PYTHON=3.12 make ci` offline. It exited 0:

```text
2549 passed, 1 warning in 48.45s
339 passed, 4 deselected in 517.84s
4 passed, 339 deselected in 56.79s
```

This exact-candidate run supersedes `4e39cc8` as the T11 scratch-clone proof.
The earlier runs remain recorded as diagnostics.

## 2026-09-13T05:36:00Z — S14B-IR1-F01 correction RED

Reviewer-grok round 1 returned REJECT on identity `6307ccb3…` with one HIGH
finding, S14B-IR1-F01. OD-18 adjudicates it VALID: Core 04 §12 names three
fields absent from the implemented PublicSnapshot 2.2.0 validator and omits
two required fields.

The exact-key test was strengthened before Core 04 was edited. It scopes
assertions to §12, requires the eight implemented names in order, and forbids
the three obsolete names. RED was observed:

```text
tests/test_integrity_contract.py::
test_s14b_core_04_and_07_partner_detail_sentences
AssertionError: exact-key `partner_detail` marker absent
1 failed in 0.09s
```

No implementation, data, scenario, visual, route, manifest or git-state
change preceded this RED.

GREEN followed the minimum Core 04 §12 correction:

```text
tests/test_integrity_contract.py::
test_s14b_core_04_and_07_partner_detail_sentences
1 passed in 0.07s
```

The Core block now lists only the validator's eight keys and states the
OBSERVED/MISSING/ZERO row, source, observed-passport and unresolved-attempt
relationships. No runtime or governed-data file changed.

Pre-generation correction regression:

```text
pytest -q: 2549 passed, 1 warning in 52.05s
verify_integrity.py: expected RED, Core 04 hash mismatch only
PRE_MANIFEST_CORE04_ONLY_RED_PASS
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
make e2e-functional: 339 passed, 4 deselected in 512.73s
make e2e-visual: 4 passed, 339 deselected in 56.17s
```

The second/final S14b manifest receipt was written before invocation at
`2026-09-13T05:49:09Z`. Its only reason is to hash the OD-18 Core 04
correction; permitted generated change is Core 04's authority row and the §11
mirror. Snapshot rows must remain byte-identical.

The run and chained immediate oracle passed:

```text
BUILD_MANIFESTS_EXIT 0
SNAPSHOT_MANIFEST_BYTE_IDENTICAL_PASS rows=638
AUTHORITY_ROWS 19 -> 19
AUTHORITY_CHANGED 1
AUTHORITY_CHANGED_PATH docs/core/04_CANONICAL_DATA_MODEL.md
SECOND_MANIFEST_DELTA_ORACLE_PASS
test_human_authority_table_matches_machine_manifest_exactly: 1 passed
INTEGRITY PASS
```

The second S14b run is exhausted; no third run is authorized.

Correction portability and exact scratch proof:

```text
/tmp/ior-s14b-correction-portability
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
ABSOLUTE_PATHS_PASS
CORRECTION_PORTABILITY_GATE_PASS

scratch commit 7d597015bdba41f7a6bc55aab4bbde95159aaf91
parent 5354a6f230bfee24e3aed97ad8120f804e97f603
CI=1, Python 3.12, offline
INTEGRITY PASS
SCENARIO VALIDATION PASS (7 scenarios)
all reconstruction stages PASS
2549 passed, 1 warning in 50.92s
SMOKE PASS
339 passed, 4 deselected in 514.70s
4 passed, 339 deselected in 56.86s
```

`make ci` was not rerun, per OD-18; owner retains that gate after re-review.

Corrected IAC-6 identity:

```text
base 5354a6f230bfee24e3aed97ad8120f804e97f603
wip_parent 1289e31
CORRECTED_CANDIDATE_IDENTITY 24c3b3cc219168dae4b1d720f7913cc71a31217ff6eafc0dccd39172335c3a38
CANDIDATE_FILE_COUNT 121
CHANGED_VS_6307CCB3 5
docs/ARCHITECTURE_DECISIONS.md
docs/authority/00_AUTHORITY_MANIFEST.md
docs/authority/authority_hashes.json
docs/core/04_CANONICAL_DATA_MODEL.md
tests/test_integrity_contract.py
ADDED_VS_6307CCB3 0
REMOVED_VS_6307CCB3 0
FULL_DELTA_PLUS_UNTRACKED_PASS
EXCLUDED_S14_RECORD_FOLDERS_PASS
COMPACT_JSON_TRAILING_LF_PASS
EXACT_CORRECTION_SCRATCH_MATCH_PASS
INDEX_EMPTY_PASS
```

The five changed identity paths are exactly the correction test, Core text,
ADR record and two generated authority mirrors. The append-only implementation
and test evidence files changed too but are excluded by IAC-6. State:
`T12_CORRECTION_HANDOFF_REVIEW_PENDING`.
