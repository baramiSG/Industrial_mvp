# S18b AM3 — bounded successor pins implementation plan

> For the sole frontend writer: apply the exact four-file patch only after a different independent reviewer approves this packet and the coordinator records delegated acceptance. Continue the existing S18b implementation workflow; this is not candidate approval or permission to generate artifacts.

**Goal:** Make retained strict tests describe the already-approved S18b catalogue, module and browser additions while preserving every historical fixture and assertion.

**Architecture:** Two exact live UI-version literals and two finite, explicitly enumerated test inventories advance to the approved successor. No production behavior, discovery rule, tolerance, fixture file or graph input changes.

**Tech stack:** Existing pytest/AST/Node/browser test infrastructure; no dependency, service or environment change.

**Spec:** Parent S18b plan `ce2786284e0fafc4bcf89d66eed748362d0b2437c696af193b6471a8be772164`, design `d648d24330973a8b51be79829ce9188448cf83c0fec8fd1594756231b9fcc7a9`; AM1 `b93785dd5b241d66969c31b1d39366c39bc1be95212b0a2951aa7c6c6127e89d`; accepted AM2 v2 `013a032a2fcaaaa354d1abd970c7d7fbbff67cb8fdd29c0801c4eaf59aefea08`, independent review `1285aff1fe839797d80e2d8ede3b7216bb9f624232a98b975fb790ff9715bd76`. All remain unchanged.

**Status:** PROPOSED AM3. Planner `/root/s18_followup_plan_review`; a different independent reviewer must decide exact bytes. Same-model Codex delegation is not Claude approval. Source `/home/barami/projects/ior-worktrees/s18b` has one coordinator-designated writer, `/root/s18b_frontend_implementer`, who continues accepted work. No whole-candidate freeze or identity is claimed during this planning observation.

## Preparation and diagnosis

Reused the completed full governing/external workflow/original DOCX read; refreshed AGENTS, authority manifest, unchanged authoritative DOCX hash `5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9`, relevant Core03/09 frontend/graph contracts, roadmap, approved S18b plan/AM1/AM2, current handoff/findings and owner delegation/acceptance deltas before choosing personas. Adopted regression-contract maintainer and reproducible-delivery planner personas to distinguish necessary successor expectations from weakened checks. Actually invoked/applied writing-plans, systematic-debugging, test-driven-development/writing-good-tests, verification-before-completion, GitHub flow, project-orientation/task-standards, Sanad, al-Muhasibi and Muhasabah. The explicit owner/coordinator separate-author/reviewer workflow and external packet location govern over generic skill defaults.

The writer's frozen `SUCCESSOR-PIN-BLOCKER-PACKET.json` hash `5bb5e3d5b6863163c0230b3b710b95ff5bb1146dfda9e180ce49418add5720cb` reports 21 failed / 3,238 passed / one warning in the retained full pre-generation pytest run. Direct log reading classifies ten failures as this amendment's stale expectations: four authority UI-version assertions, one no-candidate full-payload equality, two browser inventories and three module inventory/count checks. One additional catalogue pin belongs to already-accepted AM2. The other ten are the retained graph/visual/status generation mismatches; their verification remains Task6/Task7, never waived by AM3. The unchanged Starlette TestClient deprecation warning is reported, not a new failure or dependency-upgrade authorization.

Read-only planner diagnostics confirm actual UI version 1.6.0, exactly 50 production modules, and exactly 23 browser top-level files. The old module expectations fail; the exact proposed 50-name set passes the **same** named-export/local-import and ≤199-physical-line function bodies, and the actual syntax checker prints `ES MODULE CHECK PASS (50 files)`. Old browser shape fails and exact proposed 23-file shape passes the same existing function. This is isolated expectation diagnosis, not a full suite pass or product review.

The writer confirmed 25 executive test names, including the two newly added races. Harness AST collection scans **all** top-level `FunctionDef` names in `browser_tests/test_*.py`, so six planned AM2 graph tests also belong in the successor set. At this packet's observation there are 70 actual named tests (45 retained +25 executive); the six graph tests are not yet present. The coordinator explicitly permits binding those six concrete writer-declared names now, with actual inventory GREEN required after AM2 implementation. No stubs or fabricated test execution fill that gap.

The separate full functional run finished during packet preparation: **583 passed, four deselected, three teardown errors** in 1,030.50 seconds. Direct final-log inspection identifies EN/AR no-candidate fixtures requesting `/api/executive/opportunities/FIX-PUBLIC-NO-CANDIDATE` and receiving 404 plus console-error; the third teardown triggers the unchanged graph visual preflight at 16,802,282 aggregate bytes, exceeding 16,777,216 by 25,066 bytes. **These behavioral and budget failures are excluded from AM3 and remain unresolved.** The pin adapter does not repair the endpoint request. Their causes and authorized corrections must be diagnosed/reviewed before Task6; no failure-collector exclusion or budget increase is permitted here. Root and writer were notified with the exact evidence. A needed out-of-boundary correction returns for separate amendment. The writer's separate race-test ordering correction is also outside AM3; its behavior and evidence remain subject to existing implementation review.

## Exact additional file boundaries and proposed bytes

`PROPOSED-PATCH.diff` contains every code/test change authorized by this amendment. `preimages/` and `postimages/` are exact external review copies, not applied source. Apply only if all four source preimage hashes match; if the writer has independently changed one, stop and reconcile through review rather than overwriting it.

| Path | Exact change | Preserved contract |
| --- | --- | --- |
| `tests/test_authority_disclosure.py` | One assertion literal: `result["authority"]["config_versions"]["ui_strings"] == "1.5.0"` → `"1.6.0"` | Full derived-authority/API equality; all four public/simulated × steel/polypropylene cases; methodology/threshold/narrative values and error tests |
| `tests/test_es_modules.py` | Append exactly the 13 approved module strings listed below to `EXPECTED_MODULES` | All 37 old members; exact set equality; named exports/no defaults; resolved local imports; ≤199 physical lines; real Node parser and exact reported count |
| `tests/test_browser_harness_contract.py` | Append exactly five approved top-level file strings and exactly 31 new named tests; rename only `test_browser_inventory_has_exactly_45_named_tests` to `test_browser_inventory_has_exactly_76_named_tests` | All old 18 files and 45 names; identical AST discovery and exact equality; every other dependency/locale/axe/failure collector/environment/visual assertion |
| `browser_tests/graph_fixtures.py` | In `adapt_no_candidate_expected`, one assignment literal `versions["ui_strings"] = "1.5.0"` → `"1.6.0"` | Frozen source UI 1.3.0 assertion, other historical version checks/adaptations, deepcopy, component order/identity, graph-view append, all other fixture functions |

Pre/post SHA-256 pairs are fully bound in `DIAGNOSIS.json`. Only the already-permitted slice/control records gain a byte-identical `plan-amendment-3.md`, additive plan-review reference, implementation/test-evidence entry and the ADR text below. Preserve every historical plan/design/amendment/review and assignment. No snapshot, frozen JSON, golden expectation file, data, manifest, production source, configuration, API, graph schema/service/layout, browser checker or dependency is changed by AM3.

### Exact 13 production-module additions

```text
modules/analyst-navigation.js
modules/claim-links.js
modules/executive/context.js
modules/executive/data.js
modules/executive/evidence.js
modules/executive/index.js
modules/executive/labels.js
modules/executive/registry.js
modules/executive/render.js
modules/executive/routes.js
modules/executive/simulation.js
modules/executive/steps.js
modules/executive/summary.js
```

These are the parent plan's eleven named executive modules, shared claim-links module and permitted analyst-navigation split. The amendment does not authorize an additional module, increase the line cap or replace the literal set with discovery-derived expectations. A new module remains a review event.

### Exact five browser-file additions

```text
executive_pages.py
test_executive.py
test_executive_accessibility.py
test_executive_races.py
test_executive_states.py
```

The exact 25 executive names are in `DIAGNOSIS.json.executive_test_names` and as literal additions in the patch. They include `test_delayed_locale_response_cannot_restore_previous_case` and `test_late_analyst_claim_response_cannot_restore_previous_sources`, which postdate the original blocker packet. Do not substitute that packet's stale 23-name executive list.

The six additional names in the existing `browser_tests/test_graph.py` are bound from the AM2 writer's declaration:

```text
test_graph_node_names_preserve_sources_and_arabic
test_graph_source_disclosure_mutations_fail_strict_oracles
test_graph_narrow_panel_contains_controls_and_text
test_graph_scroll_region_reaches_both_keyboard_endpoints
test_graph_all_view_states_fit_narrow_panel
test_graph_hostile_name_text_is_escaped
```

This is 45 historical +25 executive +6 AM2 =76 distinct names. Parametrized executions have a different count; never report 76 as the number of browser test cases executed. The six bodies and their required behavior remain governed by accepted AM2; an inventory name is not evidence those behaviors exist or pass. Before post-amendment GREEN, bind the final AST to this exact set and retain its file hashes. An unplanned name/removal needs explicit reconciliation, not a wildcard or automatically regenerated expected set.

## Task 1 — preserve evidence, authority and exact scope

- [ ] Different reviewer reads this packet and issues explicit exact-byte verdict; root records delegated acceptance separately. No self-approval or permission transfer from old implementation reviews.
- [ ] Sole writer verifies all four preimages from DIAGNOSIS.json, the frozen no-candidate expected JSON SHA-256 `15962184ce199e2fabfe36a5d8854bc4d8c50cfc483ab0bcf9f7620b8a8b362e`, and existing index/checkpoint preservation before applying the patch. No staging/commit at this stage.
- [ ] Retain the original full 21-failure log and independent typed diagnosis. It already demonstrates genuine RED in the unchanged four boundary files. Reproduce any needed focused failure with the same source before applying; preserve pre-generation graph/visual failures separately from these pins.
- [ ] Confirm final executive and graph test-name AST after AM2 is written; retain the six currently pending names as pending until then. Do not fill them with stubs or shrink the exact expected set to obtain GREEN.

## Task 2 — apply only exact pin updates and verify actual behavior

**Files:** only the four boundary paths above. **Interface:** existing fixtures, tests, module discovery and harness functions remain unchanged; the amended constants describe the reviewed successor.

- [ ] Apply `PROPOSED-PATCH.diff`; verify resulting four source hashes equal the bound postimages. Review diff to prove no assertion, expected legacy member, input guard, exclusion rule or file limit was removed.
- [ ] Run the actual affected tests after AM2's concrete test names exist:

```sh
uv run --locked --extra dev pytest -q tests/test_authority_disclosure.py tests/test_es_modules.py tests/test_browser_harness_contract.py tests/test_api.py::test_no_candidate_expected_payloads_match_engine_output tests/test_s17_graph_contract.py::test_no_candidate_adaptation_is_guarded_and_does_not_mutate_history
```

The four detailed authority cases must exercise actual API/engine results; they must all report 1.6.0 while keeping full metadata equality. The module tests must execute all 50 real files, enforce ≤199 lines, imports/exports and real parser success. Both harness equality assertions must pass with exactly 23 files and 76 names. The no-candidate API equality test must compare its entire actual payload; do not filter authority fields or compare a subset.

- [ ] Recheck no-candidate adapter and frozen bytes. The proposal's old→new adapter result delta is exactly `/analysis/authority/config_versions/ui_strings` and `/ui_manifest/components/0/props/authority/config_versions/ui_strings`, both 1.5.0→1.6.0; every other field is equal. Input remains unmodified. Its source guards still require 1.3.0 in both historical authority objects; changing either historical UI version to 1.5.0 must still reject, as the independent pure-function probe demonstrates. Keep the existing component-shape negative regression and historical fixture hash.
- [ ] Run the existing functional no-candidate case (`browser_tests/test_screening.py::test_no_candidate_deep_case_renders_disposition_label_not_null`) through the explicit browser environment, then the full required `make e2e-functional` after authorized fixes. Preserve complete payload equality, real null/disposition rendering and all existing failure-collector channels. Do not introduce exemptions for console, network, page or teardown errors.
- [ ] In an isolated proof copy, demonstrate sensitivity of finite inventories: an extra or removed JS module fails exact set equality; adding/removing a named browser test fails exact equality. Do not modify a source worktree or canonical artifact for negative controls. Retain all existing 199-line, import/export, syntax and harness guards; no new mirrored test is needed to restate constants.

## Task 3 — additive records and unchanged generation/delivery gates

- [ ] Append this precise ADR text under the existing S18b ADR/its next additive amendment subsection before any generation:

> S18b AM3 advances four omitted live test pins to the already-reviewed catalogue 1.6.0, 50 exact ES modules, 23 exact browser top-level files and 76 exact named browser tests (45 retained, 25 executive, six AM2 graph). The guarded no-candidate adapter changes only its two resulting live UI-version values; its frozen JSON and 1.3.0 input guards remain unchanged. No production behavior, graph input, test tolerance or acceptance criterion changes. graph_fixtures.py is already a visual source input and its final successor hash must be bound before canonical capture. All prior approvals and historical fixtures remain intact; this amendment neither authorizes generation nor resolves independent functional failures.

- [ ] Record actual RED/GREEN, final AST and full functional failure dispositions in existing S18b implementation/test-evidence records. Use accurate stage language. Add reviewer/hash references; do not embed a candidate's own tree OID inside it.
- [ ] Task6 source binding: read-only actual `discover_inputs(ROOT)` and visual `_source_hashes()` have been inspected and invoked. None of the four paths is a graph input. Only `browser_tests/graph_fixtures.py` is already in visual source discovery; the three `tests/` files are absent from both. Preserve that discovery logic. Bind the fixture's exact postimage `8c744097f8d0cd54c407334f6167fcfc72b7355104f5b8c780ac51a417997842` along with every other final visual source before allocation; re-run discovery at actual freeze. No new graph-input path or graph generation permission follows from AM3.
- [ ] Finish parent/AM1/AM2 inputs and required pre-generation verification, classify all errors, then return the exact Task6 operation packet for separate review. Parent graph→manifest→canonical visual sequence, semantic/count oracle 925/1,045, snapshot 726 and authority 20 expectations remain unchanged; discrepancies stop, never force an expected count.
- [ ] Preserve all 128 visual paths, fixed producer/fonts/dimensions, 600 KiB/image, 16 MiB total and tolerances. Strict R1 still requires 12/5 rows, exactly five one-token changes per locale, normalized ordered tuples, all untouched repeat/round-trip fields, and 0.01 section/button/line/clipping constraints with only inherited narrow span-width/shared-edge allowances. AM3 grants no pixel exception beyond already accepted parent/AM2.
- [ ] Full parent Task7, compare-only e2e, integrity/reconstruction/scenarios/public outcomes/equality, two clean-root `make ci`, independent exact-tree review, staged/committed identity, hosted checks/exact-head review and protected delivery remain mandatory. Preserve all indexes and approved evidence. No staging, service operation, generation, PR or merge is authorized by this planning packet alone.

## Review focus and stop conditions

1. Exact 13/5/31 additions must map to already-approved parent/AM2 work; no undeclared module or test expansion hidden in the pin repair.
2. All historical members/assertions remain; no dynamic expected-inventory oracle, subset comparison, missing test-body stub or raised 199-line budget.
3. Adapter retains original guard/deepcopy/full equality; no frozen fixture rewrite or drop of authority fields to mask differences.
4. Final functional errors are separate blockers for Task6 until their actual cause and authorized correction are reviewed; this proposal claims no full functional pass.
5. No new graph input or generation exception; the already-hashed visual fixture's final bytes must precede capture. If any extra file/behavior is needed, return concrete evidence for a new bounded review.

## Provenance, assumptions, risks and self-audit

Direct: governing/task documents, exact four preimages, full unit log, source/AST inventories, actual unchanged module/shape function probes, real Node parser, actual live authority summary, pure original/proposed fixture adapters and malformed historical-version checks, and actual graph/visual discovery membership. Writer-reported execution, with final unit/functional logs directly read and bound: 21/3,238 unit and 583/four/three functional results. Writer-declared: names of the six not-yet-written AM2 graph tests. Explicitly observed: 70 actual named tests, proposed future 76, no invented GREEN for the missing six. `DIAGNOSIS.json`, retained logs/records and exact patch bind these statements.

Assumptions: root controls the sole writer; parent/AM2 scope remains as approved; the six declared graph tests will implement their required behaviors before the finite inventory can pass. Risks: a literal inventory can go stale again; it must be deliberately reviewed rather than generalized away. Future slices may need their own catalogue/module/test successor adjustments; this plan grants none. Unverified: application of the patch, final graph-test bodies, full affected pytest/API/browser GREEN, unresolved 404/console and aggregate-budget errors, candidate identity, generation, all local/hosted gates and independent approval. No source/index/service/database mutation occurred during planning. Muhasabah PASS for a bounded sourced proposal; this author cannot approve its own plan.
