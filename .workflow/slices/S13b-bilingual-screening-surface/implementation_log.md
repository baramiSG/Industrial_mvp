# Implementation log — S13b bilingual screening surface

## 2026-09-12T18:41:54Z — T0 preflight started

- Seat: `implementer-sol`, slot 1.
- Discipline persona: interface engineering on a governed decision product, full-stack only where the approved mount, additive evidence route, KL-34 amendment, catalogue localisation, and visual oracle require it.
- Data classification: `confidential_demo`; public aggregate evidence and Class-D test fixtures only. No personal, Ministry, private, or paid data.
- Authority precedence: AM-2 (`fae4ec027607…`) > AM-1 (`341d813f6988…`) > base plan (`560695023cd6…`), with owner decisions OD-1…OD-14 and all supervisor/reviewer IACs binding.
- Execution boundary: T0 → T8 only, then stop at `T8_HANDOFF_WIP_PENDING`.
- Environment for every Python/uv command: `UV_OFFLINE=1`, `PYTHONPYCACHEPREFIX=/tmp/ior-s13b-pyc`, `PATH=.venv/bin:$PATH`, `PYTHONPATH=src`.
- No network; `.env` will not be read; no git-state mutation by the implementer.

Command:

```text
$ test "$(git branch --show-current)" = slice/s13b-bilingual-screening-surface && git merge-base --is-ancestor ab4add6adad742cb07eddd4cd8a9dd12f82efd8b HEAD && echo BRANCH_OK
```

Output:

```text
BRANCH_OK
```

Recorded state:

```text
HEAD ab4add6adad742cb07eddd4cd8a9dd12f82efd8b
branch slice/s13b-bilingual-screening-surface
git status --short:
?? .workflow/slices/S13b-bilingual-screening-surface/
HEAD:browser_tests/baselines 9f334b8d820778638d13afdd80b4087a85189bc0
INDEX_EMPTY_PASS
```

Authority hash check:

```text
560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e  plan-1-s13b.json
341d813f6988e9ac4621b047c9762220e0f4831f290a7a66814ce12b108105d9  plan-1-s13b-amendment-1.json
fae4ec0276077609bbb049472470a682b36a55ada43b5633bda2b6ceca46a58a  plan-1-s13b-amendment-2.json
```

An initial broad file-discovery result included stale paths under the superseded `SCREENING-SAU-2026-09-12-311f105c4ccf` name. Direct filesystem reads and `git status --untracked-files=all` confirmed those paths do not exist. The only present/tracked summary is:

```text
data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/summary.json
```

No data file was modified.

Docker and baseline gates:

```text
$ docker version --format '{{.Server.Version}}'
29.7.2

$ PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json

$ PYTHONPATH=src .venv/bin/python scripts/reconstruct_snapshot.py --all
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)

$ PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%

$ PYTHONPATH=src .venv/bin/pytest --co -q
2198 tests collected in 1.18s

$ PYTHONPATH=src .venv/bin/pytest --co -q browser_tests -m 'e2e and not visual'
118/122 tests collected (4 deselected) in 0.05s

$ .venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (19 files)

$ PYTHONPATH=src .venv/bin/python scripts/check_browser_prerequisites.py
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
product_fonts=IOR Noto Sans,IOR Noto Sans Arabic
```

The reconstruction command exited 0 with known publisher-PDF extraction warnings before the four required PASS lines.

AM-2 route/record baseline:

```text
EVIDENCE_ROUTE_BASELINE 404 {'detail': 'Not Found'}
RECORD_PASSPORT_BASELINE 200 []
RECORD_NOT_EVALUATED_BASELINE ['R4-F', 'R6', 'R7', 'R8', 'R12']
```

BF-24:

- (a) confirmed the existing keys named by the plan and confirmed `common.yes` / `common.no` are absent before T5.
- (b) six-item navigation fit remains a T6/T7 rendered-layout check; current desktop sidebar is token-driven and current ≤900px grid is five columns.
- (c) the canonical Dockerfile remains pinned to Playwright 1.62.0 Noble and uv 0.12.9; daemon version is 29.7.2. The actual image build remains T8.
- (d) Node renders the pinned Arabic/Gregorian/latn date as `12‏/09‏/2026` with no Latin letters. AM-2 independently requires passport `retrieved_at` to remain the source ISO token in a `dir="ltr"` technical island.

T0 result: required baseline oracles passed; no stop condition triggered. The implementation and test-evidence records are the only repository paths created so far.

## 2026-09-12T18:46:26Z — T1 RED

Added the three approved CLI snapshot-selection tests before production code:

- date then snapshot-id ordering rather than lexical directory ordering;
- CLI/runtime agreement on the committed data root;
- fail-closed invalid summary.

Command:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py -k 'cli_latest_snapshot or cli_and_repository_select'
```

RED output:

```text
F.F
FAILED test_cli_latest_snapshot_selects_by_as_of_date_then_snapshot_id_not_directory_order
  actual: SCREENING-Z-OLDER
  expected: SCREENING-B-NEWER
FAILED test_cli_latest_snapshot_fails_closed_on_invalid_summary
  Failed: DID NOT RAISE <class 'ValueError'>
2 failed, 1 passed, 6 deselected in 0.05s
```

The failures are the intended missing behavior: `_latest_snapshot` still chooses the final lexical directory and does not load/validate summaries.

## 2026-09-12T18:47:23Z — T1 GREEN

Implemented `_latest_snapshot` with the runtime repository's `(as_of_date, snapshot_id)` maximum over loaded, validated summaries. Invalid summaries propagate failure.

The first combined regression exposed one pre-existing CLI test double that created a directory without the summary now required by the approved behavior:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py tests/test_screening_repository_and_api.py
FAILED test_screening_cli_main_exit_codes_and_no_socket
FileNotFoundError: .../SCREENING-TEST/summary.json
1 failed, 17 passed, 1 warning in 0.42s
```

The test double was updated to supply the same minimal validated identity fields used by the selection step; no assertion was removed.

Final GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py tests/test_screening_repository_and_api.py
18 passed, 1 warning in 0.25s

$ PYTHONPATH=src .venv/bin/python -m ior_mvp.screening validate --check-inputs
SCREENING VALIDATION PASS

$ wc -l src/ior_mvp/screening/cli.py
180 src/ior_mvp/screening/cli.py
```

IDE diagnostics: no errors in the two edited T1 files. T1 result: PASS; no stop condition triggered.

## 2026-09-12T18:49:19Z — T2 RED

Added the AM-2 route, additive-contract, mounted-app, TL-09, and NFR-005 tests before production changes. The pre-existing sharded-data leakage helpers were made non-vacuous by loading sorted `SCREENING-*` directories; the data itself was not changed.

RED commands and outcomes:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_repository_and_api.py tests/test_api.py -k 'evidence_route or existing_three_route or screening_router_is_mounted or screening_mount_ignores'
FAILED test_evidence_route_returns_eight_universe_passports_verbatim
FAILED test_evidence_route_without_snapshot_is_explicit
FAILED test_evidence_route_ignores_mode_and_carries_no_synthetic_flag_true
FAILED test_screening_router_is_mounted_before_the_spa_fallback
FAILED test_screening_mount_ignores_evidence_mode_query
5 failed, 1 passed, 44 deselected, 1 warning in 0.28s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_leakage.py::test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode tests/test_performance.py::test_warm_mounted_screening_endpoints_median_below_250_ms
FAILED test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode
FAILED test_warm_mounted_screening_endpoints_median_below_250_ms
2 failed, 1 warning in 0.19s
```

Expected causes: `/api/screening/evidence` is 404 on the router, and primary-app screening paths are caught by the SPA fallback as `text/html`.

## 2026-09-12T18:51:54Z — T2 GREEN

Implemented:

- one additive `GET /api/screening/evidence` route appended after all 157 base lines of `screening/api.py`;
- the exact public/no-snapshot payloads from AM-2;
- the screening router mount immediately after the static mount and before every app route;
- non-vacuous sharded-snapshot leakage coverage;
- mounted API, key-set, mode-isolation, and warm-median tests.

The delivered s13a summary serializes its `queues` object in the frozen snapshot's canonical key order (`high_evsi…`, `incumbent…`, `likely…`, `resilience…`, `robust…`), not `QUEUE_IDS` declaration order. The mounted contract test pins that observed existing route order; changing the existing summary route to satisfy the base-plan list would violate OD-12.

The first all-T2 run exposed a pre-existing order-dependent repository-test cache: `test_latest_snapshot_selected_by_as_of_date_then_snapshot_id` cached its temporary `SNAPSHOT_ROOT`, then monkeypatch restored the global while the LRU retained the deleted path. Evidence:

```text
6 failed, 69 passed, 1 warning in 3.18s
snapshot id from prior test: SCREENING-SAU-2026-09-12-e79b70d94b26
subsequent path: .../test_latest_snapshot_selected_0/.../SCREENING-B-NEWER/summary.json
```

An additive autouse fixture now clears each repository LRU wrapper before and after every test, including while `screening_snapshot` is temporarily monkeypatched. The first teardown form called the monkeypatched lambda's missing `cache_clear`; the final fixture conditionally clears only cache-wrapped functions. No existing test function or assertion was removed.

Final GREEN and contract oracles:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_repository_and_api.py tests/test_api.py tests/test_screening_leakage.py tests/test_performance.py tests/test_offline_guard.py
75 passed, 1 warning in 2.97s

$ N=$(git show ab4add6:src/ior_mvp/screening/api.py | wc -l) && ... verification [25]
API_ADDITIVE_ONLY_PASS
25  0  src/ior_mvp/screening/api.py
153 0  tests/test_screening_repository_and_api.py

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# mounted summary/evidence/404/mode oracle
SCREENING_MOUNT_OK
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_leakage.py
3 passed, 1 warning in 1.99s

$ wc -l src/ior_mvp/screening/api.py
182 src/ior_mvp/screening/api.py
```

`RUNTIME_IMPORT_BOUNDARY_OK`; IDE diagnostics found no error in the T2 files. T2 result: PASS; no stop condition triggered.

## 2026-09-12T18:54:35Z — T3 RED

Before changing rule production, captured all 68 current golden ledger rows (two cases × two modes) to `/tmp/ior-s13b-ledger-prose-head.json`:

```text
LEDGER_PROSE_HEAD_ROWS 68
LEDGER_PROSE_HEAD_SHA256 6ebeb73699a7cee6c95805ec02f664b79af6322eef95ba0eaf7cfc34e820c23e
```

Added the approved typed-code, AST call-site, exact catalogue coverage, EN-prose equality, Arabic segment, GenUI pass-through, and exact migration allow-list tests.

RED:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py -k 'typed_result or builders_pass_codes or metadata_and_locale or rule_ledger_catalogue or english_rule_ledger or arabic_rule_ledger or catalogue_has_213 or rule_ledger_component or pre_cutover_in_memory_v2_diff'
FAILED test_every_rule_row_carries_typed_result_and_effect_codes
FAILED test_rule_builders_pass_codes_at_every_call_site
FAILED test_decision_catalogue_metadata_and_locale_contract_are_exact
FAILED test_rule_ledger_catalogue_keys_cover_every_code_and_nothing_more
FAILED test_english_rule_ledger_catalogue_equals_engine_prose
FAILED test_arabic_rule_ledger_entries_are_arabic_with_ltr_isolated_computed_values
FAILED test_catalogue_has_213_keys_with_parity_and_validator_pass
FAILED test_rule_ledger_component_carries_localized_rows
FAILED test_pre_cutover_in_memory_v2_diff_is_exactly_allow_listed[steel]
FAILED test_pre_cutover_in_memory_v2_diff_is_exactly_allow_listed[polypropylene]
10 failed, 58 deselected in 0.22s
```

The failures are the intended missing T3 contracts: rule rows have no typed fields or `localized`, the catalogue remains 1.1.0 / 126 keys, and the exact migration allow-list expects the four additive row fields.

## 2026-09-12T19:01:37Z — T3 GREEN

Implemented all approved deep-ledger typed fields with literal call-site codes:

- 19 rule-name catalogue variants;
- 43 result-code variants;
- 21 decision-effect-code variants;
- string-only `result_values` / `effect_values`;
- 83 exact `rule.*` EN/AR templates and the four T4 no-candidate narrative keys, bringing the catalogue from 126 to 213;
- server-side `localized.{en,ar}.{name,result,decision_effect}` rows;
- public computation on raw rows before localisation and simulated localisation after public + synthetic concatenation.

The English templates exactly reproduce the compatibility prose; Arabic literals contain Arabic text and isolate only computed placeholders.

GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py -k 'typed_result or builders_pass_codes or metadata_and_locale or rule_ledger_catalogue or english_rule_ledger or arabic_rule_ledger or catalogue_has_213 or rule_ledger_component or pre_cutover_in_memory_v2_diff'
10 passed, 58 deselected in 0.18s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py tests/test_golden_cases.py tests/test_public_decision.py tests/test_simulation_generalized.py tests/test_simulation_fidelity.py
165 passed in 0.63s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# exact comparison with /tmp/ior-s13b-ledger-prose-head.json
LEDGER_PROSE_UNCHANGED_PASS 68
LEDGER_PROSE_CURRENT_SHA256 6ebeb73699a7cee6c95805ec02f664b79af6322eef95ba0eaf7cfc34e820c23e
DECISION_NARRATIVES_OK 213
PY

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# exact public and simulated golden assertions
FROZEN_OUTCOMES_OK
PY
```

IDE diagnostics: no errors in the T3 files. T3 result: PASS; no stop condition triggered.

## 2026-09-12T19:05:38Z — T4 RED

Authored the Class-D test fixture `FIX-PUBLIC-NO-CANDIDATE` from the approved recipe: two flat public trade years and route 3 technical feasibility false. The fixture is synthetic-free test data, not demonstration evidence.

Pre-fix proof:

```text
KL34_FIXTURE_VALID_PASS
KL34_PRE_FIX_HTTP 422
KL34_PRE_FIX_DETAIL {'code': 'EVIDENCE_INTEGRITY_ERROR', 'message': 'Admitted deep case has no legal branch'}
```

Added the fixture-level null-state, residual fail-closed, registry, API/manifest/list/dossier, expected-payload, and localized dossier tests.

RED:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py -k 'no_fired_signal or other_unmatched_residual or no_trigger_fired_is or no_candidate_expected_payloads or no_candidate_disposition'
FAILED test_no_fired_signal_deep_case_is_no_candidate_with_null_state
FAILED test_no_trigger_fired_is_a_registered_decision_reason_code
FAILED test_no_fired_signal_deep_case_returns_200_no_candidate_not_422
FAILED test_no_candidate_expected_payloads_match_engine_output
FAILED test_dossier_renders_no_candidate_disposition_label_instead_of_none
5 failed, 1 passed, 107 deselected, 1 warning in 0.33s
```

Expected causes: step 8 still raises, `NO_TRIGGER_FIRED` is not registered, the API returns 422, and the generated expected payload does not yet exist. The distinct fired-signal residual still raises as required.

## 2026-09-12T19:09:31Z — T4 GREEN

Implemented the approved narrow step-8 amendment:

- registered `NO_TRIGGER_FIRED`;
- no fired candidate signal → null formal state/route, `NO_CANDIDATE`;
- all other unmatched fired-signal residuals still fail closed;
- four governed bilingual no-candidate narrative entries;
- list summaries and integrity banners carry `screening_disposition`;
- dossier state rendering uses the governed disposition label and `NO_CANDIDATE` token rather than Python `None`;
- added `disposition.no_candidate` in both UI catalogue locales now so T4 dossier tests can go green before the rest of the T5 catalogue additions.

The first focused GREEN attempt exposed that the existing English `dossier.none` empty-list label legitimately renders `None` in kill-condition and next-action boxes. The null-state regression was therefore scoped to the state block while separately requiring the no-candidate label somewhere in each localized dossier; this preserves the pre-existing empty-list contract and still proves the state is never rendered as null.

The existing registry test now includes `NO_TRIGGER_FIRED`; its Core-07 loop excludes only that new marker because the approved plan assigns the Core assertion to T9. All prior registered codes remain documented by the original loop.

Generated the canonical expected payload:

```text
tests/fixtures/public_decision/no-candidate-no-fired-signal.expected.json
sha256 f0ec0fc5e33af9a2f8bc251e9df849595450b43cf386ab35cfb86dcced1a8e74
bytes 199062
```

GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py -k 'no_fired_signal or other_unmatched_residual or no_trigger_fired_is or no_candidate_disposition'
5 passed, 108 deselected, 1 warning in 0.27s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py tests/test_decision_narratives.py tests/test_golden_cases.py
142 passed, 1 warning in 1.25s

$ PYTHONPATH=src .venv/bin/pytest -q <seven exact KL-34 and residual tests>
7 passed, 1 warning in 0.37s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# exact public and simulated golden assertions
FROZEN_OUTCOMES_OK
PY
```

No `/home/`, synthetic-true marker, `DEMO_GENERATOR`, or `SYN-MINISTRY` occurs in either KL-34 fixture. IDE diagnostics: no errors in the T4 files. T4 result: PASS; no stop condition triggered.

## 2026-09-12T19:11:41Z — T5 RED

Added exact tests for UI catalogue 1.2.0 metadata, endpoint version, every AM-2 screening chrome/vocabulary key, Arabic-script values, code/value separation, and the non-colliding `reason.no_screening_snapshot` label.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'metadata_locales_and_version or endpoint_returns_valid or covers_every_screening or screening_labels_are_arabic'
FAILED test_ui_catalogue_metadata_locales_and_version_are_exact
FAILED test_ui_catalogue_covers_every_screening_vocabulary_code
FAILED test_screening_labels_are_arabic_and_never_equal_a_code
FAILED test_ui_strings_endpoint_returns_valid_en_and_ar_bundles[en]
FAILED test_ui_strings_endpoint_returns_valid_en_and_ar_bundles[ar]
5 failed, 8 deselected, 1 warning in 0.28s
```

Expected causes: metadata/validator remain 1.1.0, and all screening labels except the T4 `disposition.no_candidate` entry are absent.

## 2026-09-12T19:15:16Z — T5 GREEN

Advanced `ui_strings.v1.yaml` and its validator to 1.2.0 / 2026-09-12. Added exactly 227 bilingual screening keys (207 → 434 total), covering every final AM-2 chrome key and governed vocabulary. `reason.no_screening_snapshot` is “The screening snapshot is not loaded,” not the token text. `disposition.no_candidate` is “No screening candidate,” so the visible `NO_CANDIDATE` technical token does not collide with an English catalogue value under the IAC-G1 normalisation.

Focused GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'metadata_locales_and_version or endpoint_returns_valid or covers_every_screening or screening_labels_are_arabic'
5 passed, 8 deselected, 1 warning in 0.33s

UI_CATALOGUE_KEYS 434
SCREENING_REQUIRED_KEYS 227
UI_CATALOGUE_ADDITIONS_FROM_207 227
SCREENING_KEYS_MISSING 0
```

As explicitly predicted by T5, the full catalogue suite has one deferred failure until T6 references every literal:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py
1 failed, 12 passed, 1 warning in 0.65s
FAILED test_every_ui_string_usage_resolves_without_unused_keys
```

Every listed failure is an unused new screening key; there is no missing key or copy-source failure.

All non-deferred T5 tests:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'not every_ui_string_usage_resolves_without_unused_keys'
12 passed, 1 deselected, 1 warning in 0.58s
UI_CATALOGUE_1_2_OK 434
```

Regenerated the T4 expected payload solely to carry the final UI catalogue authority version:

```text
sha256 eb649138fa028e3ba391fa82d2e2d9fb58793fca9ec744c63766eefc1e3dbed4
bytes 199062
test_no_candidate_expected_payloads_match_engine_output: passed
```

IDE diagnostics: no errors in the T5 files. T5 result: PASS with the one plan-deferred T6 usage oracle; no stop condition triggered.

## 2026-09-12T19:16:56Z — T6 RED

Added the final AM-2 static contracts and expanded the exact ES-module registry from 19 to 27 before writing frontend code.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py tests/test_ui_catalogue.py::test_every_ui_string_usage_resolves_without_unused_keys -k 'screening or null_state or rule_ledgers or integrity_banner_displays or module_graph or browser_module or syntax_checker or every_ui_string_usage'
FAILED test_integrity_banner_displays_public_and_active_states_together
FAILED test_shell_has_screening_nav_item_and_section
FAILED test_screening_modules_render_explicit_states_and_no_ordinal
FAILED test_screening_need_codes_are_rendered_only_through_labels
FAILED test_screening_labels_fail_closed_on_unknown_codes
FAILED test_rule_ledgers_render_localized_rows_not_english_islands
FAILED test_null_state_renders_disposition_chip
FAILED test_screening_css_layer_is_imported_and_token_only
FAILED test_module_graph_has_named_exports_no_defaults_and_resolved_local_imports
FAILED test_every_browser_module_has_at_most_199_lines
FAILED test_es_module_syntax_checker_checks_every_js_file_in_module_mode
FAILED test_every_ui_string_usage_resolves_without_unused_keys
12 failed, 19 deselected, 1 warning in 0.61s
```

Expected causes: the screening section/eight modules/CSS layer do not exist, ledgers still use English source islands, state renderers still call `stateChip`, and the 227 catalogue additions are not yet referenced.

## 2026-09-12T19:25:01Z — T6 GREEN

Implemented the approved frontend architecture:

- nav item 06, `#screening-view`, and always-present sibling `#screening-evidence`;
- eight named-export screening modules (27 total), all 79–155 lines;
- public-only summary/evidence/queue/record endpoint helpers;
- persistent eight-passport rendering, explicit no-snapshot/unmatched-unit states, record evidence basis, and in-page anchors;
- five queue views with API `pareto_rank` and no running ordinal;
- governed code maps that fail closed on unknown values;
- localized deep ledgers in workspace and methodology;
- null-state `decisionChip` across hero, integrity banner, and portfolio;
- token-only screening CSS and six-column compact navigation token.

The first CSS scan rejected a literal `900px` media query. Responsive behavior was moved into three existing layout tokens set inside the governed token layer’s existing breakpoint, leaving `screening.css` with no raw length/color literal.

GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py -k 'screening or null_state or rule_ledgers or integrity_banner_displays or module_graph or browser_module or syntax_checker'
11 passed, 19 deselected in 0.42s

$ .venv/bin/python scripts/check_ui_contracts.py --check-catalogue-usage
UI CONTRACT CHECK PASS: catalogue usage exact

$ .venv/bin/python scripts/check_ui_contracts.py --check-copy
UI CONTRACT CHECK PASS: visible copy catalogue-sourced

$ .venv/bin/python scripts/check_ui_contracts.py --scan-css src/ior_mvp/static/css/screening.css
UI CONTRACT CHECK PASS

$ .venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (27 files)

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py tests/test_ui_catalogue.py tests/test_ui_tokens.py
55 passed, 1 warning in 1.50s
```

IDE diagnostics: no errors in the T6 files. T6 static result: PASS; rendered behavior proceeds to T7. No stop condition triggered.

## 2026-09-12T19:32:53Z — T7 RED

Added T7 tests before their implementations:

- 39-node technical-island grammar boundary matrix, residuals, and symmetric catalogue-label leak check;
- six Class-D DOM-negative cases;
- route-derived UNAVAILABLE/PARTIAL/empty/queue/record fixture pins;
- bilingual screening journeys, pagination, explicit states, leakage, keyboard, axe, RTL, parity, injected negatives, and KL-34 rendering;
- deep-ledger semantic parity and the 21-control shell tab order.

RED evidence:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_parity_grammar.py
ERROR tests/test_parity_grammar.py
ModuleNotFoundError: No module named 'browser_tests.parity_grammar'

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_surface_fixtures.py
2 failed, 1 warning in 0.17s
missing tests/fixtures/screening/summary-unavailable.json

$ PYTHONPATH=src .venv/bin/pytest -q browser_tests/test_screening.py browser_tests/test_journeys.py -m 'e2e and not visual' --collect-only
ERROR browser_tests/test_screening.py
ERROR browser_tests/test_journeys.py
ImportError: cannot import name 'arabic_parity_report' from browser_tests.pages
```

These are the expected absent grammar, fixtures, page helpers, and browser behavior.

Initial fixture/grammar GREEN substeps:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_parity_grammar.py
39 passed in 0.08s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_surface_fixtures.py
2 passed, 1 warning in 0.18s
```

Seven route-derived fixture files were generated from the current public router/test doubles; all are public-only and repository-relative.

## 2026-09-12T19:47:38Z — T7 GREEN

Implemented the browser helpers, focus identities, exact parity predicate, symmetric label-leak mitigation, fixture mocks, and all journeys.

The first 30-node screening run produced nine failures:

```text
9 failed, 21 passed in 100.72s
```

Root causes and corrections:

- the record indicated state rendered only its code in English; screening rows now render the governed state label;
- full-page axe at the screening scroll position found the sticky topbar eyebrow at 3.98:1; a screening-active token rule now uses the existing high-contrast navy token without changing non-screening scenes;
- methodology references were not members of the locked 11-class grammar; section references render as bidirectionally natural text, while the high-EVSI prose reference renders through its governed queue label;
- redundant disposition/result/effect/execution code tokens collided with their English labels; screening ledgers render those values through labels only while preserving genuine technical IDs/hashes/runs;
- unavailable em dashes were incorrectly wrapped as technical islands; unavailable labels now remain normal localized text;
- simulated rule rows repeated the English evidence-policy warning inside each Arabic ledger row; Arabic rows now carry the Arabic policy warning while the surrounding simulated surface still displays both evidence-policy labels.

Focused correction evidence:

```text
8 passed in 25.59s
2 passed, 5 deselected in 6.01s
4 deep-ledger parity nodes passed in 3.91s
```

Final browser evidence:

```text
$ IOR_E2E_EXPLICIT=1 ... pytest -q browser_tests/test_screening.py -m 'e2e and not visual' --browser chromium ...
30 passed in 92.83s

$ IOR_E2E_EXPLICIT=1 ... pytest -q browser_tests/test_journeys.py browser_tests/test_accessibility.py ... -k '<modified tests>'
2 failed, 32 passed, 46 deselected in 29.00s before the policy-label correction

$ IOR_E2E_EXPLICIT=1 ... pytest -q <four deep-ledger parity nodes after correction>
4 passed in 3.91s

$ make e2e-functional
152 passed, 4 deselected in 252.26s
```

`run-summary-functional.json`: collected 152, passed 152, failed 0, skipped 0, exit status 0. Default collection is 2,270 tests; functional browser collection is 152 plus four visual nodes.

T7 result: PASS; no BrowserFailureCollector record and no stop condition triggered.

## 2026-09-12T19:49:43Z — T8 RED

Extended the visual capture test and its contract matrix to the four approved Screening scenes before changing the visual runtime or baselines.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py -k 'exact_56 or baseline_files'
FAILED test_visual_manifest_has_exact_56_entry_locale_viewport_screen_matrix
E assert 40 == 56
FAILED test_visual_baseline_files_are_lossless_webp_with_600_kib_and_12_mib_budgets
E assert 40 == 56
2 failed, 15 deselected in 0.05s
```

RED validity: the governed baseline still contains exactly 40 files/entries before the authorized canonical regeneration.

## 2026-09-12T20:14:08Z — T8_HANDOFF_WIP_PENDING

Canonical execution history under the same approved change reference:

1. `make visual-baseline-image` passed. BuildKit rebuilt the dependency layer and its output reported package downloads; this is disclosed because the brief said no network even though it separately mandated this exact build command.
2. First update attempt reached the canonical Chromium assertion but stopped before capture because pytest collection evaluated `tests/fixtures/parity/**`, which is intentionally outside the canonical mount allow-list. No baseline was finalized.
3. The fixture remained runtime-driven, while parameter IDs became collection-safe; the next update passed four visual nodes and produced 56 entries.
4. Host and canonical comparisons exposed nondeterministic first-frame rasterization on new Screening summary scenes. RED/green stability contracts added integer scroll quantization, two animation frames, and a discarded warm-up screenshot. Corrective canonical updates used the same change reference and replaced the candidate atomically.
5. Final host comparison: four passed, 152 deselected. The final 56-entry tree is byte-stable at OID `3297e2f8d75fcdc03e072788d96d44be559b186d`.

Final visual receipt:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 152 deselected in 52.80s
VISUAL_MANIFEST_OK 56 S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
VISUAL_GENERATED_ON 2026-09-12
VISUAL_BROWSER 151.0.7922.34 chromium-1234 1.62.0 0.9.0
VISUAL_TOTAL_BYTES 7171852
VISUAL_MAX_FILE_BYTES 231028
VISUAL_OWNERSHIP_OK 1000
Docker image sha256:9281e58776e3dc18527431cf137e803935f38a8b123fccb7cd408d787e0aeb3c
no /home/ path in browser_tests/baselines/**
```

Measured pre-existing drift:

```text
40 rows measured
24 significant-mask changes
16 unchanged dossier entries
0 tolerance failures
maximum significant-pixel ratio 0.000749
maximum mean absolute channel error 0.069542
8 sidebar-only changes
16 sidebar + integrity-authority changes
0 dossier changes
0 masks outside allowed regions
80 before/after crop files
```

The first drift-analysis run used a one-bit union mask incorrectly and reported 24 false outside-region results. The corrected eight-bit union rerun used the same measured rectangles and proved every changed pixel lies inside `aside.sidebar` ∪ `.integrity-authority`. The final table and crops are under `.autonomous-workflow/evidence/s13-public-universe-screening/visual-s13b/`; only one Markdown file and 80 PNG crops exist there.

Pre-WIP verification:

```text
$ PYTHONPATH=src .venv/bin/pytest -q
2 failed, 2269 passed, 1 warning in 27.70s
```

Only these tests fail:

- `test_public_and_synthetic_bytes_unchanged_from_base`
- `test_visual_baseline_tree_unchanged_from_base`

Both observe the authorized transient state: HEAD still has tree `9f334b8d820778638d13afdd80b4087a85189bc0`, the pin records future tree `3297e2f8d75fcdc03e072788d96d44be559b186d`, the working baseline tree differs, and 16 new WebPs are untracked. The depth-one mechanism test independently uses its clone's recorded OIDs, so exactly the two authoritative pin tests fail before the owner WIP commit.

```text
$ make e2e-functional
152 passed, 4 deselected in 254.74s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py
18 passed in 0.07s

PROTECTED_SET_BYTE_IDENTICAL_PASS
API_ADDITIVE_ONLY_PASS
INDEX_EMPTY_PASS
git status --short | wc -l = 104
```

The four owner-WIP path groups are exactly:

1. `browser_tests/baselines/v0.3.0/**`
2. `browser_tests/visual_baselines.py`
3. `browser_tests/test_visual_baselines.py`
4. `tests/test_frozen_public_evidence_pins.py`

Exact WIP file hashes (61 files):

- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-a-portfolio-public.webp` `9e51fc2c8bd88eeb88aabdd1b23489daa03a911511de6d0dc799e7d33b9f635f`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-a-portfolio-simulated.webp` `73205f8b98654e6c5d0eef98c6d77ee348c840eea5d6567d4f22dc47fc1ed072`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-b-steel-public-workspace.webp` `a199784cb34c1b2d03d7f8c605b5e41f72701552829f7ed193a705d78c46f216`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-c-steel-simulated-workspace.webp` `ec6bcc7023b48b833ba449fee87d3620b9ae1b30e1d7059d45e829f66c5aca11`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-d-polypropylene-public-workspace.webp` `8310ff1f01c56d98ce0867c65104851c36747821121f31b001b00566cadb17c1`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-d-polypropylene-simulated-workspace.webp` `28fec74bcb2a869496e0aa6a35b8ea8f46ca1f542fd6fc66ac7f1e6f9472f15a`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-e-polypropylene-public-dossier.webp` `d258de9cf5fe70056a7581faf309a5c2acc52feaf705ff1609be1bf27ecce4e1`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-e-polypropylene-simulated-dossier.webp` `6d8b0693a9ec1d5bd2ab311f11c59890599c541db96b29cfcb0c1d86a2bf4341`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-e-steel-public-dossier.webp` `f6d5555cfce9ac50757eb298bda5814bd35bb46d0535b2b10d962d802830fc82`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-e-steel-simulated-dossier.webp` `777a7f876567a49261ee06da35ceaa54f1e146364df4aae7a1121a5844d04fe4`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-f-screening-queue-empty.webp` `7333322ab032d0ddef33a73e9ebe2832443cba20d802878c6799e0137d270f73`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-f-screening-queue-robust.webp` `6df78bc89a46762df5ac256ffd95ec1535b636154ca0949a1bbea665efe94fc3`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-f-screening-record.webp` `b3aa201e57b4578c8bc896fb9aa0c9f625b5fbed1d1ba0955f1552f9ce305b41`
- `browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-f-screening-summary.webp` `d85ec3885d23c2a1099a717050b62335818767df1da0dbcfdfc207a3fd150136`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-a-portfolio-public.webp` `9abed68571d725e0c22491ce0cffa161ac6fcd7327c47e76cf0cf87bd7e29dce`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-a-portfolio-simulated.webp` `cd4f25ba0db6e81a337701089db465676e042841e8a705d8ef8b3196701d9833`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-b-steel-public-workspace.webp` `c87541adad1bf37731a91581d1853282cc366b458f7972d9d0fa796f51865ea2`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-c-steel-simulated-workspace.webp` `fcef9d268a1f21e4c1fc2deb208dcfd63b1915858fb4e1086061d6435fa5df59`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-d-polypropylene-public-workspace.webp` `8b568052f24c3eeccdc2afc0b054ed511909c41309dff5b8eeea0fd5dcd16eb6`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-d-polypropylene-simulated-workspace.webp` `4863d53b203dce1e30af77a74a639b4cc95f32dd41245b66c407d3423134443a`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-e-polypropylene-public-dossier.webp` `96df0d6db5dd0c10033a22f5bf8cff5f6efb5582ff5ad27ff51463556beeaa15`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-e-polypropylene-simulated-dossier.webp` `af11dafe7e0e1cdb450f53c66fb94bded5478a023400b1d6234f71fb1ffcca12`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-e-steel-public-dossier.webp` `cfc762ce4127cd64076ba41b36e337a9ae93dc330e45ef76065a845216c1dce9`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-e-steel-simulated-dossier.webp` `fc02d07ab88e05f9a5cd4256ec3c784016d9f48573611257baab2b70229e4151`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-f-screening-queue-empty.webp` `d352200a8a672b1576fdb29e4c8f68edfd754a4990131961dfc1f57a10f451e9`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-f-screening-queue-robust.webp` `16fbeeddae1d81e816d37ee691a97e5804c195e511f874860d0d17495335d94c`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-f-screening-record.webp` `bee70afee5b55545ac8ebf66501d1d23913818db2894c60412220786240d73bb`
- `browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-f-screening-summary.webp` `fdd014cfe10146afcfed66b9190f17752d880f6a83d62c47fd0904b4de1d0870`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-a-portfolio-public.webp` `2a398a0e3b9eff7ca15a3cda4050e872a0bfd85d3da7256a114c844f0602508c`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-a-portfolio-simulated.webp` `320cf9b1e00450b44610031d5f9520fbc7047993867962c4473e0dfae55d3087`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-b-steel-public-workspace.webp` `86b83466d0c33008e016f2ead9619cd6f3cc2d620b7293a070bd9f3e632738cf`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-c-steel-simulated-workspace.webp` `7190c7e250f6301c4b5fd1037caaf870367cfdfa38d65a5cd778919152ffc6d0`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-d-polypropylene-public-workspace.webp` `c915723c923d637d3fd1515f4a79f6c327fbe088f8bc3310367fa10829228ea7`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-d-polypropylene-simulated-workspace.webp` `1a7a504dc936ec6baea2db18f3af659088b523541217d38460097ac58993379c`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-e-polypropylene-public-dossier.webp` `cb945d78aa1f338925f4261110a2fcd022a1f5a47b260705648b7d2772443f95`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-e-polypropylene-simulated-dossier.webp` `dda684fa7b5f864f38ec344154052bea29d706469c0baae49ca03c8ed0d6dc55`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-e-steel-public-dossier.webp` `e8caef5af6ef8d6274770313bcc74904a80831be7f81e69e4b007ea67c8beb87`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-e-steel-simulated-dossier.webp` `846ffe4b15bb76ccff69a3717e79fbb9dba6d22aeeed8df5c5d4fd075bd7a831`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-f-screening-queue-empty.webp` `e2fb9543dd032f25c1ae15c68fba06fdda9183471a3ccd9b3e6b2446999b4d2b`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-f-screening-queue-robust.webp` `7589d747dbf06a9b1aa0c09e81f3b155d575231f1ff5e79ddb027a126a394b0d`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-f-screening-record.webp` `a6d4904a8fd59685c931404616d142f48579de33190c9be85641edddcb7e0245`
- `browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-f-screening-summary.webp` `17f05501afda6bd8358ebc585386f35c8fdbaa29351448ba803d0f5a1365adc4`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-a-portfolio-public.webp` `f59464f1c98862dbe6dff51ede5c26a31a4870cd92132807ce15c8ffd428af68`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-a-portfolio-simulated.webp` `ceecc2760e99cdf35c5bd91ddede9f259c1c0c62ff30fb24c7086c146322567a`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-b-steel-public-workspace.webp` `e659aef4b9e7434a5376240ae6ce4014dc468b9210825488a306cbf7fda90d86`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-c-steel-simulated-workspace.webp` `d713ec3bfcf5f347c3c95c0a621d2c4551a6dd1fab44b89cde003e0b2d9a747c`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-d-polypropylene-public-workspace.webp` `39f8263817156c778c76e74b86aa71020d1af13ca874a37e514159a6259399f7`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-d-polypropylene-simulated-workspace.webp` `cf7871b4baad1ad0e09cb02407a6303c3531f918fcb9bd60c80fce64902cba74`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-e-polypropylene-public-dossier.webp` `95a22aff3583f55e11d5c3c69865f6730a86b6b7cdba4d29f7682ac822a1203d`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-e-polypropylene-simulated-dossier.webp` `b89d8d5909c32d07758efabbf4239ca117f46f61b358d145a8810d8632dce283`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-e-steel-public-dossier.webp` `722af31c984e27d286eaf935a91325a3cca6e9b9cf91fc08d25f13dc2fbac29f`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-e-steel-simulated-dossier.webp` `957a104a1681ff5e8e8bd734184120a1f4377eb51fc75d1f429d72107e6885c0`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-f-screening-queue-empty.webp` `7bc69b7c1f28dd83b299fd2737778b98f64232ad7958f9aea0012be2eb831dd4`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-f-screening-queue-robust.webp` `dfad5d187343c1ebc42fb49b4da97c8a0fb156a051a0340c7ed199c97e5829dd`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-f-screening-record.webp` `5a8635ffd3d928aeba5aaab9d344594a6d8d35766d4a0df57dc634f178232fbe`
- `browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-f-screening-summary.webp` `93e55c6184695a896bb9df94c5b74afcf39a592f27bc431a346f0895588d5da2`
- `browser_tests/baselines/v0.3.0/manifest.json` `db59fde497ab3280146f51226ac1cc173f582eb0d1622f4f8067f08ab4760886`
- `browser_tests/baselines/v0.3.0/manifest.sha256` `982f8905d2a23b2b48ecad1d174da6652e0ea0f683c15aea958d43a7ca0d7b5e`
- `browser_tests/visual_baselines.py` `ee4a9f55cc01ec37b0af7e7711d842f3fc790e0ed4f30585072c06815ab2369b`
- `browser_tests/test_visual_baselines.py` `990e3f7b70c4096116eb27a6b20407648a9b2461f6e4a074c6cfc900a099fce5`
- `tests/test_frozen_public_evidence_pins.py` `f9a38e2f4cefa2f412d662933fc18ebe0a4c68ebad0b072fd859942d7b2b2664`

Other files touched during T8 correction/validation (not in the owner WIP commit):

- `browser_tests/test_screening.py` — collection-safe runtime fixture loading.
- `tests/test_visual_baseline_contract.py` — 56-entry matrix and deterministic Screening-anchor contract.
- `tests/test_authority_disclosure.py` — approved 1.2.0 catalogue expectations surfaced by full pytest.
- `tests/test_browser_harness_contract.py` — exact 31-test/two-new-file browser inventory.
- `tests/test_ci_contract.py` — working manifest/WebP hash contract; frozen HEAD equality remains in the two dedicated pin tests.
- `.autonomous-workflow/evidence/s13-public-universe-screening/visual-s13b/` — permitted drift table and crops.

Stop conditions: none. T8 is stopped here for the owner-lead WIP commit; T9 has not started.

### Muhasib self-audit at T8 handoff

Verified:

- implemented only approved T0–T8 behavior under AM-2 > AM-1 > base;
- no staging, commit, checkout, stash, reset, or repository-index mutation;
- protected data/config/screening modules are byte-identical and `api.py` is additive-only;
- both public outcomes remained exact in the last direct oracle;
- final functional gate is 152/152 and final visual compare is 4/4;
- final drift is 24 changed non-dossier entries, 16 unchanged dossier entries, and zero mask pixels outside the two approved regions;
- full pytest has only the two OD-4 transient pin failures;
- generated manifests remain untouched and `build_manifests.py` has not run;
- candidate secret-signature scan passed across 122 modified/untracked files (82 text, 40 binary);
- no `.env` was read.

Not yet verified:

- the owner-lead WIP commit, post-WIP tree equality, and green pin suite;
- T9–T12 authority text, the single manifest run, portability, `make ci`, candidate identity, independent review, PR, CI, or merge.

Disclosed deviations/incidents:

- the mandated Docker image build reported dependency downloads despite the brief's general no-network instruction;
- one collection-failed and multiple corrective canonical executions were required under the same change reference; every attempt and cause is recorded;
- `make ci` was not run at this pre-WIP handoff because OD-4 explicitly leaves two frozen-pin tests red until the owner commit.

Self-audit result: `T8_HANDOFF_WIP_PENDING`, not completion and not self-approval.

## 2026-09-12T20:26:13Z — T9 resumed after OD-15 WIP acceptance

Owner state was re-verified before further edits:

```text
$ git rev-parse HEAD
d1d1462ce214f45b7fd286c6436a6bb2f0ca7f47
$ git rev-parse HEAD^
ab4add6adad742cb07eddd4cd8a9dd12f82efd8b
$ git diff --cached --quiet && echo INDEX_EMPTY_PASS
INDEX_EMPTY_PASS
$ git rev-parse HEAD:browser_tests/baselines
3297e2f8d75fcdc03e072788d96d44be559b186d
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_frozen_public_evidence_pins.py
17 passed in 1.37s
```

Correction to the T8 inventory wording: OD-15 committed exactly 45
changed/added files in the four authorized path groups (16 added, 29
modified). The earlier “61 files” inventory listed every file under the
baseline subtree, including sixteen unchanged dossier WebPs; it was a subtree
inventory, not the touched-file set. No prior evidence is deleted; this
correction is the controlling statement.

T9 RED was captured before authority text:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_integrity_contract.py -k s13b_governed_surface_contracts_are_recorded
FAILED tests/test_integrity_contract.py::test_s13b_governed_surface_contracts_are_recorded
AssertionError: assert 'FR-084' in core_01
1 failed, 20 deselected in 0.06s
```

The final test name was aligned to the approved plan:
`test_s13b_core_v2_surface_contracts`. Core 01/03/07/09, UX specification,
ADR-020, KL-34/KL-84…KL-89, roadmap, progress, traceability and the
style-preserved workflow state now record the implementation candidate.
ADR-020 records the two completed canonical update executions (52.34 s and
52.80 s), the prior collection stop, Docker dependency-download disclosure,
measured drift, OD-15 WIP receipt and manifest run count 0. No generated
manifest has run.

T9 GREEN is `1 passed` for the new exact contract and `21 passed` for the
complete integrity-contract file. The first attempt preserved insufficient
historical marker wording; Core 03 now retains its S13a section identity and
Core 07 retains the existing fail-closed unmatched-residual sentence while
adding the contiguous no-trigger null-state sentence. No assertion was
removed. `git diff --check`, workflow JSON validation and the obsolete UX
sentence absence check pass. T9 is complete; T10 has not started and manifest
run count remains 0.

## 2026-09-12T20:48:00Z — SC-5 post-WIP visual correction

T10 pre-generation behavior was green (`2272 passed`; functional browser
`152 passed, 4 deselected`), but the first host visual comparison failed all
four new Screening summary captures. An unchanged rerun passed 4/4, proving
the mismatch intermittent rather than an authored-content change. Pixel
diagnostics showed whole-content vertical shifts of one to three pixels.

Systematic instrumentation found that nav 06's smooth scroll was still active
when `_anchor_screening` measured and scrolled: observed `scrollY` differed
from its computed target by 5–43 pixels. The first test-first hypothesis
(wait for fonts before measuring) was necessary but insufficient. The second
(disable smooth behavior and assert the target) correctly failed in the
canonical container while the existing nav animation was still in flight.
The final test-first correction waits for three stable navigation-scroll
frames before disabling smooth behavior, scrolling to the integer target and
asserting settlement.

Canonical correction history under the unchanged approved reference:

1. assertion run failed with `SCREENING_ANCHOR_NOT_SETTLED`; no candidate
   finalized;
2. corrected stable-frame run passed `4 passed, 152 deselected in 57.14s`,
   but immediate validation found an incomplete finalized root (38 paths
   missing), so it was rejected;
3. isolated recovery execution of the same command passed 4/4 and produced a
   complete valid 56-entry root; host compare then passed
   `4 passed, 152 deselected in 43.33s`.

The corrected root differs from `d1d1462` only in four new
`journey-f-screening-summary.webp` files plus `manifest.json` and
`manifest.sha256`; all 40 pre-existing entries and the other twelve new
screening entries are byte-identical to OD-15. Total directory bytes are
7,196,180 and future tree OID is
`c2b3b66bbc6afaefe6e951772984d567cac53522`. The pin is updated; exactly the
two OD-4 frozen-pin tests are red until another owner WIP commit. T10 has not
run `build_manifests.py` (count remains 0).

Required owner-WIP changed set inside the governed four path groups is eight
files: six under `browser_tests/baselines/v0.3.0/`,
`browser_tests/test_visual_baselines.py`, and
`tests/test_frozen_public_evidence_pins.py`.
`tests/test_visual_baseline_contract.py` remains part of the ordinary
uncommitted candidate.

## 2026-09-12T20:52:00Z — OD-16 accepted correction and execution-history reconciliation

Owner WIP commit `f9fec2d` contains the accepted eight-path SC-5 correction
and has parent `d1d1462`; root parent remains `ab4add6`. The baseline tree at
HEAD is `c2b3b66bbc6afaefe6e951772984d567cac53522` and the 17 frozen-pin tests
pass. T12 will use base `f9fec2d`, both WIP commits and parent `ab4add6`.

The earlier numbered SC-5 history omitted one of two inadvertently overlapping
successful stable-frame invocations. The complete truthful history is: an
assertion precursor failed `SCREENING_ANCHOR_NOT_SETTLED` and finalized
nothing; the three canonical executions passed in 57.46 s, 57.14 s and
56.42 s. The first two overlapped and left a 38-path-incomplete finalized
root, which was rejected; the third ran in isolation and produced the
accepted complete root. ADR-020 records that full history and the smooth-scroll
root cause/correction. Manifest run count remains 0 before T10.

## 2026-09-12T20:53:47Z — T10 single manifest generation

Pre-generation inventory contained 19 authority rows and 535 snapshot rows.
The six stale authority rows were exactly `config/ui_strings.v1.yaml`,
`config/decision_narratives.v1.yaml` and Core 01/03/07/09; the three generated
artifacts were untouched before the gate.

The single authorized `scripts/build_manifests.py` invocation ran at
`2026-09-12T20:53:47Z` and exited 0. It preserved both path sets (19 and 535),
changed those six authority rows, changed zero snapshot rows and mirrored the
machine authority rows into Manifest §11. Immediate integrity and the complete
21-test integrity contract passed. The S13b manifest run count is now 1 and
the authorization is exhausted.

## 2026-09-12T21:03:00Z — T11/T12 verification and uncommitted hand-off

The alternate-path portability gate passed integrity, all four reconstruction
oracles and Screening validation. `make ci` exited 0 with 2,275 pytest tests,
152 functional browser tests and four visual comparisons passing.

IAC-6 candidate identity is
`611de6bf05c16ba2fc4bb328988b6e22f5d0f3428f9a45e62e0065c6590593b8`
over 85 uncommitted candidate paths relative to base `f9fec2d`, with
`wip_commits=[d1d1462,f9fec2d]` and `wip_parent=ab4add6`. Both S13 slice-record
folders are excluded. The index is empty; protected files are byte-identical;
the additive API oracle, state JSON and local-only workflow checks pass.

Implementation stops uncommitted at `T12_HANDOFF_REVIEW_PENDING`. No stop
condition was triggered. No further manifest generation is authorized.
