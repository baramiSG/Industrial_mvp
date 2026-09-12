# Test evidence — S13b bilingual screening surface

## 2026-09-12T18:41:54Z — T0 preflight

All commands in this record were printed before execution. Unless a block states otherwise, commands ran from the repository root with:

```text
UV_OFFLINE=1
PYTHONPYCACHEPREFIX=/tmp/ior-s13b-pyc
PATH=.venv/bin:$PATH
PYTHONPATH=src
```

### Branch and authority identity

```text
$ test "$(git branch --show-current)" = slice/s13b-bilingual-screening-surface && git merge-base --is-ancestor ab4add6adad742cb07eddd4cd8a9dd12f82efd8b HEAD && echo BRANCH_OK
BRANCH_OK

$ git rev-parse HEAD
ab4add6adad742cb07eddd4cd8a9dd12f82efd8b

$ git rev-parse HEAD:browser_tests/baselines
9f334b8d820778638d13afdd80b4087a85189bc0

$ git diff --cached --quiet && echo INDEX_EMPTY_PASS
INDEX_EMPTY_PASS
```

Approved artifact hashes:

```text
plan-1-s13b.json             560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
plan-1-s13b-amendment-1.json 341d813f6988e9ac4621b047c9762220e0f4831f290a7a66814ce12b108105d9
plan-1-s13b-amendment-2.json fae4ec0276077609bbb049472470a682b36a55ada43b5633bda2b6ceca46a58a
```

### Baseline oracles

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

$ PYTHONPATH=src .venv/bin/pytest --co -q | tail -1
2198 tests collected in 1.18s

$ PYTHONPATH=src .venv/bin/pytest --co -q browser_tests -m 'e2e and not visual' | tail -1
118/122 tests collected (4 deselected) in 0.05s

$ .venv/bin/python scripts/check_es_modules.py --node node | tail -1
ES MODULE CHECK PASS (19 files)

$ PYTHONPATH=src .venv/bin/python scripts/check_browser_prerequisites.py
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
chromium=<user-cache>/ms-playwright/chromium-1234/chrome-linux64/chrome
axe_sha256=c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1
font_family=DejaVu Sans
font_file=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
product_fonts=IOR Noto Sans,IOR Noto Sans Arabic
```

The reconstruction process exited 0. Its known PDF extraction warnings preceded all four required reconstruction PASS lines.

Only `data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/summary.json` is present and tracked. The superseded `311f105c4ccf` paths returned by an initial broad discovery result were stale and direct reads confirmed they do not exist.

### AM-2 RED baseline

```text
$ PYTHONPATH=src .venv/bin/python - <<'PY'
# throwaway FastAPI app mounting the existing screening router
EVIDENCE_ROUTE_BASELINE 404 {'detail': 'Not Found'}
RECORD_PASSPORT_BASELINE 200 []
RECORD_NOT_EVALUATED_BASELINE ['R4-F', 'R6', 'R7', 'R8', 'R12']
PY
```

T0 status: PASS. No stop condition triggered.

## 2026-09-12T18:46:26Z — T1 RED

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py -k 'cli_latest_snapshot or cli_and_repository_select'
F.F                                                                      [100%]
FAILED tests/test_screening_candidates.py::test_cli_latest_snapshot_selects_by_as_of_date_then_snapshot_id_not_directory_order
E AssertionError: SCREENING-Z-OLDER != SCREENING-B-NEWER
FAILED tests/test_screening_candidates.py::test_cli_latest_snapshot_fails_closed_on_invalid_summary
E Failed: DID NOT RAISE <class 'ValueError'>
2 failed, 1 passed, 6 deselected in 0.05s
```

RED validity: both failures directly expose the approved missing behavior; they are not setup, import, or syntax failures.

## 2026-09-12T18:47:23Z — T1 GREEN

Focused GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py -k 'cli_latest_snapshot or cli_and_repository_select'
...                                                                      [100%]
3 passed, 6 deselected in 0.06s
```

Combined-suite integration correction:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py tests/test_screening_repository_and_api.py
FAILED tests/test_screening_candidates.py::test_screening_cli_main_exit_codes_and_no_socket
E FileNotFoundError: .../SCREENING-TEST/summary.json
1 failed, 17 passed, 1 warning in 0.42s
```

The existing no-socket test double was extended with a minimal summary-loader result because T1 now intentionally validates every candidate directory. No assertion was removed.

Final GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_candidates.py tests/test_screening_repository_and_api.py
..................                                                       [100%]
18 passed, 1 warning in 0.25s

$ PYTHONPATH=src .venv/bin/python -m ior_mvp.screening validate --check-inputs
SCREENING VALIDATION PASS
```

T1 status: PASS.

## 2026-09-12T18:49:19Z — T2 RED

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_repository_and_api.py tests/test_api.py -k 'evidence_route or existing_three_route or screening_router_is_mounted or screening_mount_ignores'
FFF.FF                                                                   [100%]
FAILED tests/test_screening_repository_and_api.py::test_evidence_route_returns_eight_universe_passports_verbatim
E assert 404 == 200
FAILED tests/test_screening_repository_and_api.py::test_evidence_route_without_snapshot_is_explicit
E assert 404 == 200
FAILED tests/test_screening_repository_and_api.py::test_evidence_route_ignores_mode_and_carries_no_synthetic_flag_true
E assert 404 == 200
FAILED tests/test_api.py::test_screening_router_is_mounted_before_the_spa_fallback
E assert 'text/html; charset=utf-8'.startswith('application/json')
FAILED tests/test_api.py::test_screening_mount_ignores_evidence_mode_query
E json.decoder.JSONDecodeError: Expecting value
5 failed, 1 passed, 44 deselected, 1 warning in 0.28s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_leakage.py::test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode tests/test_performance.py::test_warm_mounted_screening_endpoints_median_below_250_ms
FF                                                                       [100%]
FAILED tests/test_screening_leakage.py::test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode
E json.decoder.JSONDecodeError: Expecting value
FAILED tests/test_performance.py::test_warm_mounted_screening_endpoints_median_below_250_ms
E assert 'text/html; charset=utf-8'.startswith('application/json')
2 failed, 1 warning in 0.19s
```

RED validity: the new route is absent and the router is not mounted before the SPA fallback, exactly the approved T2 behavior gap.

## 2026-09-12T18:51:54Z — T2 GREEN

Focused behavior:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_repository_and_api.py tests/test_api.py -k 'evidence_route or existing_three_route or screening_router_is_mounted or screening_mount_ignores'
......                                                                   [100%]
6 passed, 44 deselected, 1 warning in 0.35s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_leakage.py::test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode tests/test_performance.py::test_warm_mounted_screening_endpoints_median_below_250_ms
..                                                                       [100%]
2 passed, 1 warning in 0.30s
```

Order-isolation regression encountered and corrected:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_repository_and_api.py tests/test_api.py tests/test_screening_leakage.py tests/test_performance.py tests/test_offline_guard.py
FAILED/ERROR: repository LRU retained deleted test_latest_snapshot_selected_0/SCREENING-B-NEWER
6 failed, 69 passed, 1 warning in 3.18s

$ same command after additive per-test cache isolation
........................................................................ [ 96%]
...                                                                      [100%]
75 passed, 1 warning in 2.97s
```

The final cache-isolation fixture removes no existing line, test, or assertion. It prevents order dependence introduced by the pre-existing monkeypatch test.

Additive-only and import-boundary proof:

```text
$ N=$(git show ab4add6:src/ior_mvp/screening/api.py | wc -l) && diff <(git show ab4add6:src/ior_mvp/screening/api.py) <(head -n "$N" src/ior_mvp/screening/api.py) && [ "$(git diff --numstat ab4add6 -- src/ior_mvp/screening/api.py tests/test_screening_repository_and_api.py | awk '{s+=$2} END {print s+0}')" = 0 ] && echo API_ADDITIVE_ONLY_PASS
API_ADDITIVE_ONLY_PASS

$ git diff --numstat ab4add6 -- src/ior_mvp/screening/api.py tests/test_screening_repository_and_api.py
25	0	src/ior_mvp/screening/api.py
153	0	tests/test_screening_repository_and_api.py

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# remove loaded ior_mvp modules; import ior_mvp.app; assert no acquisition.transport
RUNTIME_IMPORT_BOUNDARY_OK
PY

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# mounted summary, evidence, typed 404, and ignored-mode assertions
SCREENING_MOUNT_OK
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_leakage.py
...                                                                      [100%]
3 passed, 1 warning in 1.99s
```

The Starlette/httpx deprecation warning is pre-existing. T2 status: PASS.

## 2026-09-12T18:54:35Z — T3 RED

Pre-change compatibility baseline:

```text
$ PYTHONPATH=src .venv/bin/python - <<'PY'
# canonical name/result/decision_effect fields for both goldens in both modes
LEDGER_PROSE_HEAD_ROWS 68
LEDGER_PROSE_HEAD_SHA256 6ebeb73699a7cee6c95805ec02f664b79af6322eef95ba0eaf7cfc34e820c23e
LEDGER_PROSE_HEAD_PATH /tmp/ior-s13b-ledger-prose-head.json
PY
```

RED:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py -k 'typed_result or builders_pass_codes or metadata_and_locale or rule_ledger_catalogue or english_rule_ledger or arabic_rule_ledger or catalogue_has_213 or rule_ledger_component or pre_cutover_in_memory_v2_diff'
FFFFFFFFFF                                                               [100%]
FAILED tests/test_rules.py::test_every_rule_row_carries_typed_result_and_effect_codes
E KeyError: 'result_code'
FAILED tests/test_rules.py::test_rule_builders_pass_codes_at_every_call_site
E AssertionError: assert 'result_code' in {}
FAILED tests/test_decision_narratives.py::test_decision_catalogue_metadata_and_locale_contract_are_exact
E version/effective_date 1.1.0/2026-09-03 != 1.2.0/2026-09-12
FAILED tests/test_decision_narratives.py::test_rule_ledger_catalogue_keys_cover_every_code_and_nothing_more
FAILED tests/test_decision_narratives.py::test_english_rule_ledger_catalogue_equals_engine_prose
E assert hasattr(narratives_module, 'localize_rule_rows')
FAILED tests/test_decision_narratives.py::test_arabic_rule_ledger_entries_are_arabic_with_ltr_isolated_computed_values
FAILED tests/test_decision_narratives.py::test_catalogue_has_213_keys_with_parity_and_validator_pass
E assert 126 == 213
FAILED tests/test_genui_decision_contract.py::test_rule_ledger_component_carries_localized_rows
E KeyError: 'localized'
FAILED tests/test_snapshot_migration_equivalence.py::test_pre_cutover_in_memory_v2_diff_is_exactly_allow_listed[SAU-H0-721049.json]
FAILED tests/test_snapshot_migration_equivalence.py::test_pre_cutover_in_memory_v2_diff_is_exactly_allow_listed[SAU-H0-390210.json]
10 failed, 58 deselected in 0.22s
```

RED validity: failures are caused by the absent approved fields, functions, version, templates, and engine hook; no setup or syntax failure.

## 2026-09-12T19:01:37Z — T3 GREEN

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py::test_rule_builders_pass_codes_at_every_call_site tests/test_rules.py::test_every_rule_row_carries_typed_result_and_effect_codes
..                                                                       [100%]
2 passed in 0.06s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# AST enumeration of literal call-site variants
RULE_NAME_KEYS 19
RULE_RESULT_KEYS 43
RULE_EFFECT_KEYS 21
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py -k 'typed_result or builders_pass_codes or metadata_and_locale or rule_ledger_catalogue or english_rule_ledger or arabic_rule_ledger or catalogue_has_213 or rule_ledger_component or pre_cutover_in_memory_v2_diff'
..........                                                               [100%]
10 passed, 58 deselected in 0.18s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_rules.py tests/test_decision_narratives.py tests/test_genui_decision_contract.py tests/test_snapshot_migration_equivalence.py tests/test_golden_cases.py tests/test_public_decision.py tests/test_simulation_generalized.py tests/test_simulation_fidelity.py
........................................................................ [ 43%]
........................................................................ [ 87%]
.....................                                                    [100%]
165 passed in 0.63s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# compare rule_id/name/result/decision_effect for all 68 golden rows
LEDGER_PROSE_UNCHANGED_PASS 68
LEDGER_PROSE_CURRENT_SHA256 6ebeb73699a7cee6c95805ec02f664b79af6322eef95ba0eaf7cfc34e820c23e
PY

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# version, key parity, exact count
DECISION_NARRATIVES_OK 213
PY

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# steel/PP public and simulated states/routes
FROZEN_OUTCOMES_OK
PY
```

T3 status: PASS.

## 2026-09-12T19:05:38Z — T4 RED

```text
$ PYTHONPATH=src .venv/bin/python - <<'PY'
# validate fixture, mount it through the existing app, request public analysis
KL34_FIXTURE_VALID_PASS
KL34_PRE_FIX_HTTP 422
KL34_PRE_FIX_DETAIL {'code': 'EVIDENCE_INTEGRITY_ERROR', 'message': 'Admitted deep case has no legal branch'}
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py -k 'no_fired_signal or other_unmatched_residual or no_trigger_fired_is or no_candidate_expected_payloads or no_candidate_disposition'
.FFFFF                                                                   [100%]
FAILED tests/test_public_decision.py::test_no_fired_signal_deep_case_is_no_candidate_with_null_state
E DecisionIntegrityError: Admitted deep case has no legal branch
FAILED tests/test_public_decision.py::test_no_trigger_fired_is_a_registered_decision_reason_code
E assert 'NO_TRIGGER_FIRED' in DECISION_REASON_CODES
FAILED tests/test_api.py::test_no_fired_signal_deep_case_returns_200_no_candidate_not_422
E assert 422 == 200
FAILED tests/test_api.py::test_no_candidate_expected_payloads_match_engine_output
E assert expected_path.is_file()
FAILED tests/test_dossier_contract.py::test_dossier_renders_no_candidate_disposition_label_instead_of_none
E DecisionIntegrityError: Admitted deep case has no legal branch
5 failed, 1 passed, 107 deselected, 1 warning in 0.33s
```

RED validity: the approved fixture validates and reaches the exact pre-fix step-8 failure; the separate fired-signal residual test already passes, proving the fail-closed branch remains distinct.

## 2026-09-12T19:09:31Z — T4 GREEN

Intermediate dossier diagnostic:

```text
$ PYTHONPATH=src .venv/bin/python - <<'PY'
# locate any visible >None< in the generated English dossier
NONE_CONTEXT ...<section class="box kill-conditions">...<li>None</li>...
NONE_CONTEXT ...<section class="box next-actions">...<li>None</li>...
PY
```

Those are the existing governed `dossier.none` labels for empty lists, not leaked null state. The final regression checks the state block for `NO_CANDIDATE` and absence of `None`/`null`, while requiring the localized disposition label in each rendered dossier.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py -k 'no_fired_signal or other_unmatched_residual or no_trigger_fired_is or no_candidate_disposition'
.....                                                                    [100%]
5 passed, 108 deselected, 1 warning in 0.27s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# generate canonical list_entry + analysis + ui_manifest
KL34_EXPECTED_WRITTEN tests/fixtures/public_decision/no-candidate-no-fired-signal.expected.json
KL34_EXPECTED_SHA256 f0ec0fc5e33af9a2f8bc251e9df849595450b43cf386ab35cfb86dcced1a8e74
KL34_EXPECTED_BYTES 199062
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py tests/test_api.py tests/test_dossier_contract.py tests/test_decision_narratives.py tests/test_golden_cases.py
........................................................................ [ 50%]
......................................................................   [100%]
142 passed, 1 warning in 1.25s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py::test_no_fired_signal_deep_case_is_no_candidate_with_null_state tests/test_public_decision.py::test_other_unmatched_residual_still_fails_closed tests/test_public_decision.py::test_no_trigger_fired_is_a_registered_decision_reason_code tests/test_public_decision.py::test_unregistered_reject_reason_fails_closed tests/test_api.py::test_no_fired_signal_deep_case_returns_200_no_candidate_not_422 tests/test_api.py::test_no_candidate_expected_payloads_match_engine_output tests/test_dossier_contract.py::test_dossier_renders_no_candidate_disposition_label_instead_of_none
.......                                                                  [100%]
7 passed, 1 warning in 0.37s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# steel/PP public and simulated states/routes
FROZEN_OUTCOMES_OK
PY
```

Fixture portability/leak scan: no match for `/home/`, `"synthetic_flag": true`, `DEMO_GENERATOR`, or `SYN-MINISTRY`.

T4 status: PASS.

## 2026-09-12T19:11:41Z — T5 RED

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'metadata_locales_and_version or endpoint_returns_valid or covers_every_screening or screening_labels_are_arabic'
FFFFF                                                                    [100%]
FAILED tests/test_ui_catalogue.py::test_ui_catalogue_metadata_locales_and_version_are_exact
E version/effective_date 1.1.0/2026-09-02 != 1.2.0/2026-09-12
FAILED tests/test_ui_catalogue.py::test_ui_catalogue_covers_every_screening_vocabulary_code
E missing approved screening keys
FAILED tests/test_ui_catalogue.py::test_screening_labels_are_arabic_and_never_equal_a_code
E KeyError: 'screening.loading'
FAILED tests/test_ui_catalogue.py::test_ui_strings_endpoint_returns_valid_en_and_ar_bundles[en]
E catalogue_version 1.1.0 != 1.2.0
FAILED tests/test_ui_catalogue.py::test_ui_strings_endpoint_returns_valid_en_and_ar_bundles[ar]
E catalogue_version 1.1.0 != 1.2.0
5 failed, 8 deselected, 1 warning in 0.28s
```

RED validity: failures expose the absent approved version and key set; no setup or syntax failure.

## 2026-09-12T19:15:16Z — T5 GREEN

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'metadata_locales_and_version or endpoint_returns_valid or covers_every_screening or screening_labels_are_arabic'
.....                                                                    [100%]
5 passed, 8 deselected, 1 warning in 0.33s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
UI_CATALOGUE_KEYS 434
SCREENING_REQUIRED_KEYS 227
UI_CATALOGUE_ADDITIONS_FROM_207 227
SCREENING_KEYS_MISSING 0
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py
.......F.....                                                            [100%]
FAILED tests/test_ui_catalogue.py::test_every_ui_string_usage_resolves_without_unused_keys
1 failed, 12 passed, 1 warning in 0.65s
```

The sole failure is the plan-deferred T6 usage oracle: the checker reports the new screening keys as unused before their modules exist. All key/version/parity/NFC/copy/endpoint/malformed-catalogue tests pass.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_ui_catalogue.py -k 'not every_ui_string_usage_resolves_without_unused_keys'
............                                                             [100%]
12 passed, 1 deselected, 1 warning in 0.58s

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# /api/ui-strings/{en,ar}, version and count
UI_CATALOGUE_1_2_OK 434
PY

$ PYTHONPATH=src .venv/bin/python - <<'PY'
# refresh T4 expected payload after final UI metadata change
KL34_EXPECTED_REFRESHED tests/fixtures/public_decision/no-candidate-no-fired-signal.expected.json
KL34_EXPECTED_SHA256 eb649138fa028e3ba391fa82d2e2d9fb58793fca9ec744c63766eefc1e3dbed4
KL34_EXPECTED_BYTES 199062
PY

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_api.py::test_no_candidate_expected_payloads_match_engine_output
.                                                                        [100%]
1 passed, 1 warning in 0.22s
```

T5 status: PASS with the explicitly deferred T6 catalogue-usage assertion.

## 2026-09-12T19:16:56Z — T6 RED

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py tests/test_ui_catalogue.py::test_every_ui_string_usage_resolves_without_unused_keys -k 'screening or null_state or rule_ledgers or integrity_banner_displays or module_graph or browser_module or syntax_checker or every_ui_string_usage'
FFFFFFFFFFFF                                                             [100%]
FAILED tests/test_static_frontend.py::test_integrity_banner_displays_public_and_active_states_together
FAILED tests/test_static_frontend.py::test_shell_has_screening_nav_item_and_section
FAILED tests/test_static_frontend.py::test_screening_modules_render_explicit_states_and_no_ordinal
E FileNotFoundError: modules/screening/queue.js
FAILED tests/test_static_frontend.py::test_screening_need_codes_are_rendered_only_through_labels
FAILED tests/test_static_frontend.py::test_screening_labels_fail_closed_on_unknown_codes
FAILED tests/test_static_frontend.py::test_rule_ledgers_render_localized_rows_not_english_islands
FAILED tests/test_static_frontend.py::test_null_state_renders_disposition_chip
FAILED tests/test_static_frontend.py::test_screening_css_layer_is_imported_and_token_only
FAILED tests/test_es_modules.py::test_module_graph_has_named_exports_no_defaults_and_resolved_local_imports
FAILED tests/test_es_modules.py::test_every_browser_module_has_at_most_199_lines
FAILED tests/test_es_modules.py::test_es_module_syntax_checker_checks_every_js_file_in_module_mode
FAILED tests/test_ui_catalogue.py::test_every_ui_string_usage_resolves_without_unused_keys
12 failed, 19 deselected, 1 warning in 0.61s
```

RED validity: every failure is attributable to an absent or unchanged approved T6 frontend contract.

## 2026-09-12T19:25:01Z — T6 GREEN

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py -k 'screening or null_state or rule_ledgers or integrity_banner_displays or module_graph or browser_module or syntax_checker'
...........                                                              [100%]
11 passed, 19 deselected in 0.42s

$ .venv/bin/python scripts/check_ui_contracts.py
UI CONTRACT CHECK FAIL
- src/ior_mvp/static/css/screening.css:203: length: 900px
```

The hard-coded breakpoint was replaced with responsive layout tokens inside the existing token-layer media query.

```text
$ .venv/bin/python scripts/check_ui_contracts.py --check-catalogue-usage
UI CONTRACT CHECK PASS: catalogue usage exact

$ .venv/bin/python scripts/check_ui_contracts.py --check-copy
UI CONTRACT CHECK PASS: visible copy catalogue-sourced

$ .venv/bin/python scripts/check_ui_contracts.py --scan-css src/ior_mvp/static/css/screening.css
UI CONTRACT CHECK PASS

$ .venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (27 files)

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_static_frontend.py tests/test_es_modules.py tests/test_ui_catalogue.py tests/test_ui_tokens.py
.......................................................                  [100%]
55 passed, 1 warning in 1.50s
```

New screening JS module sizes: evidence 155; index 138; labels 113; ledger-labels 79; queue 130; record-evidence 135; record 122; summary 122. All are ≤199 lines.

T6 static status: PASS.

## 2026-09-12T19:32:53Z — T7 RED and fixture/grammar substeps

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_parity_grammar.py
ERROR tests/test_parity_grammar.py
E ModuleNotFoundError: No module named 'browser_tests.parity_grammar'
1 error in 0.06s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_surface_fixtures.py
FF                                                                       [100%]
FAILED test_unavailable_and_partial_fixtures_match_api_output
E missing summary-unavailable.json
FAILED test_screening_surface_fixtures_are_portable_and_public_only
E assert []
2 failed, 1 warning in 0.17s

$ PYTHONPATH=src .venv/bin/pytest -q browser_tests/test_screening.py browser_tests/test_journeys.py -m 'e2e and not visual' --collect-only
ERROR browser_tests/test_screening.py
ERROR browser_tests/test_journeys.py
E ImportError: cannot import name 'arabic_parity_report' from browser_tests.pages
no tests collected, 2 errors in 0.07s
```

Substep GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_parity_grammar.py
.......................................                                  [100%]
39 passed in 0.08s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_screening_surface_fixtures.py
..                                                                       [100%]
2 passed, 1 warning in 0.18s
```

Generated route-derived fixture hashes:

```text
summary-unavailable.json                    649a0588df9a03bf29dad94ffc119dccce5b2ffd31fb8a360f884abf9ab5d3cf
evidence-unavailable.json                   1f200951a25ba277f713918d52c270235460b061f085b6c1f624b1ffd2a677a2
queue-empty.json                            c0093945c3c66e4494ccfd63335c188a4c8ac55eacf52c9dd1e309b9e90312cb
summary-partial.json                        31827714288281416cfcdcecfdb4f75a8f776ceca722831805705bce03924598
evidence-partial.json                       f020ae3af5c270e782d6c2dd0771b8e71d7583ff49154c249eeeb51a16b8d975
queue-partial-robust_public_finding.json     40b88653d4865b8fe86bc54ded5cbc4e798fb53f5e1ae9d5aababa0d93ff4912
record-partial-030579.json                   c0155b2a5c6a8473710afb914e9cc6fd5f2973f1ed8ed3b4f978cf85ede93d6b
```

## 2026-09-12T19:47:38Z — T7 GREEN

Initial rendered run:

```text
$ IOR_E2E_EXPLICIT=1 IOR_E2E_ARTIFACT_DIR=.artifacts/e2e PYTHONPATH=src .venv/bin/pytest -q browser_tests/test_screening.py -m 'e2e and not visual' --browser chromium --tracing retain-on-failure --screenshot only-on-failure --output=.artifacts/e2e/playwright
.F.....F.FF.........F..F.F.F.F                                           [100%]
9 failed, 21 passed in 100.72s
```

Failures were localized state-label visibility, one screening-scroll topbar contrast result (3.98:1), unclassified methodology references/unavailable dash, and expected label-leak detections from redundant raw codes. Corrections changed rendering, not the parity grammar or tests.

```text
$ IOR_E2E_EXPLICIT=1 ... pytest -q <journey + six screening axe nodes>
........                                                                 [100%]
8 passed in 25.59s

$ IOR_E2E_EXPLICIT=1 ... pytest -q <screening parity + one injected negative>
..                                                                       [100%]
2 passed, 5 deselected in 6.01s

$ IOR_E2E_EXPLICIT=1 ... pytest -q browser_tests/test_screening.py -m 'e2e and not visual' --browser chromium ...
..............................                                           [100%]
30 passed in 92.83s
```

Modified existing-browser checks initially found only the four simulated deep-ledger containers carrying repeated English evidence-policy warning text:

```text
2 failed, 32 passed, 46 deselected in 29.00s
```

Arabic synthetic rows were corrected to show their Arabic policy warning; the surrounding simulated surface continues to display both policy labels.

```text
$ IOR_E2E_EXPLICIT=1 ... pytest -q browser_tests/test_journeys.py::test_workspace_and_methodology_ledgers_have_no_english_catalogue_prose_in_arabic --browser chromium
....                                                                     [100%]
4 passed in 3.91s

$ PYTHONPATH=src .venv/bin/pytest -q tests/test_parity_grammar.py tests/test_screening_surface_fixtures.py tests/test_static_frontend.py tests/test_es_modules.py tests/test_ui_catalogue.py tests/test_ui_tokens.py
........................................................................ [ 75%]
........................                                                 [100%]
96 passed, 1 warning in 1.58s

$ make e2e-functional
........................................................................ [ 47%]
........................................................................ [ 94%]
........                                                                 [100%]
152 passed, 4 deselected in 252.26s
```

Functional summary:

```text
collected 152
passed 152
failed 0
skipped 0
exit_status 0
explicit_gate true
```

Screening parity reports (`source_spans=0`, failures=0, Latin runs=0, label leaks=0 for every row):

```text
summary:
  catalogue_key=16 code_token=24 governed_id=8 hex_digest=8
  iso_datetime=8 number=26 run_id=26 url=8
queue-robust:
  catalogue_key=16 code_token=24 governed_id=8 hex_digest=8 hs_code=50
  iso_datetime=8 number=159 run_id=26 url=8
queue-lfp:
  catalogue_key=16 code_token=24 governed_id=8 hex_digest=8 hs_code=50
  iso_datetime=8 number=159 run_id=26 url=8
record:
  catalogue_key=16 code_token=34 governed_id=27 hex_digest=8 hs_code=1
  iso_datetime=8 number=22 run_id=26 url=8
```

Deep-ledger parity reports (`source_spans=0`; all other failure lists empty):

```text
workspace steel public:          code_token=12 governed_id=5 hs_code=1 number=3
workspace steel simulated:       code_token=16 governed_id=5 hs_code=1 number=3
workspace polypropylene public:  code_token=12 governed_id=5 hs_code=1 number=3
workspace polypropylene simulated: code_token=16 governed_id=5 hs_code=1 number=3
methodology steel public:        code_token=11 governed_id=5 hs_code=1 number=3
methodology steel simulated:     code_token=15 governed_id=5 hs_code=1 number=3
methodology polypropylene public: code_token=11 governed_id=5 hs_code=1 number=3
methodology polypropylene simulated: code_token=15 governed_id=5 hs_code=1 number=3
```

Collection after T7:

```text
2270 tests collected
152/156 browser tests collected (4 visual deselected)
```

T7 status: PASS.

## 2026-09-12T19:49:43Z — T8 RED

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py -k 'exact_56 or baseline_files'
FF                                                                       [100%]
FAILED tests/test_visual_baseline_contract.py::test_visual_manifest_has_exact_56_entry_locale_viewport_screen_matrix
E assert 40 == 56
FAILED tests/test_visual_baseline_contract.py::test_visual_baseline_files_are_lossless_webp_with_600_kib_and_12_mib_budgets
E assert 40 == 56
2 failed, 15 deselected in 0.05s
```

RED validity: the test requests the approved 56-entry matrix while the frozen baseline is still the 40-entry pre-S13b set.

## 2026-09-12T20:14:08Z — T8 canonical regeneration and handoff

```text
$ docker version --format '{{.Server.Version}}'
29.7.2

$ make visual-baseline-image
exit 0
image ior-visual-baselines:playwright-1.62.0-noble
```

The mandated image build rebuilt its dependency layer and reported package downloads. Subsequent builds were cached. This is disclosed against the brief's general no-network rule.

Canonical attempts, all under:

```text
S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
```

1. Collection stopped before capture because `tests/fixtures/parity/**` is outside the canonical mount allow-list:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 ...
ERROR browser_tests/test_screening.py
FileNotFoundError: /workspace/tests/fixtures/parity/parity-negative-cases.json
122 deselected, 1 error
```

2. Runtime-only fixture loading made collection mount-safe:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 ...
....                                                                     [100%]
4 passed, 152 deselected in 52.34s
```

3. Host/canonical compare revealed first-frame Screening-summary raster instability. Stability RED then GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py::test_screening_visual_anchor_quantizes_scroll_before_capture
F
1 failed in 0.04s

$ same command after integer scroll quantization
.
1 passed in 0.02s

$ same command after discarded warm-up screenshot contract
.
1 passed in 0.02s
```

4. Final corrective update:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
....                                                                     [100%]
4 passed, 152 deselected in 52.80s
```

Final host compare:

```text
$ make e2e-visual
....                                                                     [100%]
4 passed, 152 deselected in 39.99s
```

Manifest/image/ownership:

```text
VISUAL_MANIFEST_OK 56 S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
VISUAL_GENERATED_ON 2026-09-12
VISUAL_BROWSER 151.0.7922.34 chromium-1234 1.62.0 0.9.0
VISUAL_TOTAL_BYTES 7171852
VISUAL_MAX_FILE_BYTES 231028
VISUAL_OWNERSHIP_OK 1000
CANONICAL_IMAGE_ID sha256:9281e58776e3dc18527431cf137e803935f38a8b123fccb7cd408d787e0aeb3c
NO_HOME_PATHS_IN_BASELINES
```

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py
..................                                                       [100%]
18 passed in 0.07s
```

Measured drift:

```text
DRIFT_ROWS 40
DRIFT_CHANGED 24
DRIFT_TOLERANCE_FAILURES 0
DRIFT_MAX_SIGNIFICANT_RATIO 0.000749
DRIFT_MAX_MEAN_ERROR 0.069542
DRIFT_SIDEBAR_ONLY 8
DRIFT_SIDEBAR_AND_INTEGRITY 16
DRIFT_DOSSIER_CHANGED 0
OUTSIDE_ALLOWED 0
DRIFT_EVIDENCE_OK 81 files 80 crops
```

The initial one-bit union-mask implementation falsely reported 24 outside-region rows. The corrected eight-bit mask reported zero; the final table replaced the preliminary table and links every changed region to before/after crops.

Final future tree:

```text
$ TEMP_INDEX_DIR=$(mktemp -d) && GIT_INDEX_FILE="$TEMP_INDEX_DIR/index" git add -- browser_tests/baselines && GIT_INDEX_FILE="$TEMP_INDEX_DIR/index" git write-tree --prefix=browser_tests/baselines/
3297e2f8d75fcdc03e072788d96d44be559b186d
```

Pre-WIP pins:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_frozen_public_evidence_pins.py
FF...............                                                        [100%]
FAILED test_public_and_synthetic_bytes_unchanged_from_base
FAILED test_visual_baseline_tree_unchanged_from_base
2 failed, 15 passed in 1.45s
```

Full pytest after all expectation corrections:

```text
$ PYTHONPATH=src .venv/bin/pytest -q
FAILED tests/test_frozen_public_evidence_pins.py::test_public_and_synthetic_bytes_unchanged_from_base
FAILED tests/test_frozen_public_evidence_pins.py::test_visual_baseline_tree_unchanged_from_base
2 failed, 2269 passed, 1 warning in 27.70s
```

Both failures are transient and exact to OD-4: HEAD has old baseline tree `9f334b8d820778638d13afdd80b4087a85189bc0`, while the pin and uncommitted candidate have future tree `3297e2f8d75fcdc03e072788d96d44be559b186d`; 16 new WebPs are untracked until the owner WIP commit.

Final functional gate:

```text
$ make e2e-functional
........................................................................ [ 47%]
........................................................................ [ 94%]
........                                                                 [100%]
152 passed, 4 deselected in 254.74s
```

Final state:

```text
PROTECTED_SET_BYTE_IDENTICAL_PASS
API_ADDITIVE_ONLY_PASS
INDEX_EMPTY_PASS
$ git status --short | wc -l
104
```

T8 WIP groups and all 61 hashes are recorded in `implementation_log.md`. T8 status: `T8_HANDOFF_WIP_PENDING`; T9 not started.

Final self-audit checks:

```text
$ git diff --check
exit 0
$ .venv/bin/python scripts/check_prohibited_files.py
PROHIBITED FILE SCAN PASS (1110 tracked files)
$ .venv/bin/python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (71 Python files; 23 configured numeric values)
$ .venv/bin/python scripts/check_ui_contracts.py
UI CONTRACT CHECK PASS
$ .venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (27 files)
MANIFESTS_UNTOUCHED_T8
INDEX_EMPTY_PASS
$ PYTHONPATH=src .venv/bin/python - <<'PY'
# high-risk signature scan over modified and untracked candidate files
CANDIDATE_SECRET_SCAN_PASS 122 files 82 text 40 binary
PY
```

## 2026-09-12T20:26:13Z — T9 authority-contract RED and WIP verification

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
.................                                                        [100%]
17 passed in 1.37s
```

The owner WIP commit contains 45 changed/added files, not 61. The prior
61-file list included sixteen unchanged dossier WebPs because it enumerated
the complete baseline subtree. OD-15's 45-file touched set controls.

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_integrity_contract.py -k s13b_governed_surface_contracts_are_recorded
F                                                                        [100%]
E AssertionError: assert 'FR-084' in core_01
FAILED tests/test_integrity_contract.py::test_s13b_governed_surface_contracts_are_recorded
1 failed, 20 deselected in 0.06s
```

The test was then renamed to the plan-prescribed
`test_s13b_core_v2_surface_contracts` before GREEN. Manifest run count remains
0 at this point.

T9 GREEN:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_integrity_contract.py::test_s13b_core_v2_surface_contracts
.                                                                        [100%]
1 passed in 0.02s
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_integrity_contract.py
.....................                                                    [100%]
21 passed in 0.49s
$ rg -n 'remains English in this release' docs/implementation/UX_GENUI_DEMO_SPEC.md
UX_ENGLISH_REMAINS_ABSENT_PASS
$ python3 -m json.tool .workflow/state.json >/dev/null && echo STATE_JSON_VALID_PASS
STATE_JSON_VALID_PASS
$ git diff --check
exit 0
```

The first GREEN attempt exposed two preserved-contract wording requirements
plus the new exact marker: Core 03 must retain the S13a heading, Core 07 must
retain the fail-closed unmatched-residual sentence, and the new null-state
sentence must be contiguous. The authority text was corrected without changing
behavior or removing an assertion; the 21-test result above is final T9 GREEN.

## 2026-09-12T20:48:00Z — SC-5 post-WIP visual correction evidence

Pre-generation behavior before the visual finding:

```text
$ PYTHONPATH=src .venv/bin/pytest -q
2272 passed, 1 warning in 28.95s
$ make e2e-functional
152 passed, 4 deselected in 259.57s (0:04:19)
```

The first host comparison failed all four Screening summary captures with
significant-pixel ratios around 2.9%; an unchanged reproduction passed
`4 passed, 152 deselected`. Subsequent full-matrix instrumentation printed
calculated-target/actual-scroll mismatches of 43, 6, 40 and 5 pixels,
confirming the active nav smooth-scroll race.

Test-first stabilization:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py::test_screening_visual_anchor_waits_for_fonts_before_measuring_layout
1 failed in 0.04s
$ same command after font wait
1 passed
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py::test_screening_visual_anchor_cancels_smooth_scroll_before_capture
1 failed in 0.05s
$ same contract after explicit auto scroll
1 passed
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py::test_screening_visual_anchor_waits_for_navigation_scroll_to_settle
1 failed in 0.05s
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_visual_baseline_contract.py -k screening_visual_anchor
4 passed, 17 deselected in 0.02s
```

The canonical assertion-only attempt failed with
`SCREENING_ANCHOR_NOT_SETTLED` and finalized nothing. The stable-frame
correction then produced:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 152 deselected in 57.14s
```

Immediate validation rejected that finalized root because 38 expected paths
were absent. An isolated recovery execution of the same canonical command
passed 4/4 and yielded:

```text
VISUAL_MANIFEST_OK 56 S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
VISUAL_TOTAL_DIRECTORY_BYTES 7196180
VISUAL_OWNERSHIP_RELATIVE_PATHS_PASS
$ make e2e-visual
4 passed, 152 deselected in 43.33s
```

Delta from WIP `d1d1462`:

```text
browser_tests/baselines/v0.3.0/ar/desktop-1440x900/journey-f-screening-summary.webp
browser_tests/baselines/v0.3.0/ar/tablet-1024x768/journey-f-screening-summary.webp
browser_tests/baselines/v0.3.0/en/desktop-1440x900/journey-f-screening-summary.webp
browser_tests/baselines/v0.3.0/en/tablet-1024x768/journey-f-screening-summary.webp
browser_tests/baselines/v0.3.0/manifest.json
browser_tests/baselines/v0.3.0/manifest.sha256
FUTURE_BASELINE_TREE c2b3b66bbc6afaefe6e951772984d567cac53522
```

All 40 pre-S13b entries and twelve other new screening entries are unchanged
from OD-15, so the accepted 24/40 drift/mask table remains exact.

Revised pre-WIP pins:

```text
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_frozen_public_evidence_pins.py
FAILED test_public_and_synthetic_bytes_unchanged_from_base
FAILED test_visual_baseline_tree_unchanged_from_base
2 failed, 15 passed in 1.42s
```

The exact committed-tree mismatch is
`3297e2f8d75fcdc03e072788d96d44be559b186d !=
c2b3b66bbc6afaefe6e951772984d567cac53522`. Manifest run count remains 0;
T10 is paused before generation pending the owner WIP/base ruling.

## 2026-09-12T20:52:00Z — OD-16 accepted WIP and corrected canonical history

```text
$ git rev-parse HEAD
f9fec2d72c118623e164564c2e2d4dd55f2c52b1
$ git rev-parse HEAD^
d1d1462ce214f45b7fd286c6436a6bb2f0ca7f47
$ git rev-parse HEAD^^
ab4add6adad742cb07eddd4cd8a9dd12f82efd8b
$ git diff --cached --quiet && echo INDEX_EMPTY_PASS
INDEX_EMPTY_PASS
$ git rev-parse HEAD:browser_tests/baselines
c2b3b66bbc6afaefe6e951772984d567cac53522
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_frozen_public_evidence_pins.py
17 passed in 1.37s
```

The complete SC-5 terminal record contains an assertion precursor
(`SCREENING_ANCHOR_NOT_SETTLED`; 4 failed, 1 error in 44.72 s, no finalize)
followed by three canonical executions:

```text
4 passed, 152 deselected in 57.46s
4 passed, 152 deselected in 57.14s
4 passed, 152 deselected in 56.42s
```

The first two successful jobs inadvertently overlapped; immediate validation
rejected their incomplete finalized root (38 paths absent). The 56.42-second
isolated recovery produced the accepted complete tree. Host comparison then
passed `4 passed, 152 deselected in 43.33s`.

## 2026-09-12T20:53:47Z — T10 manifest receipt and immediate oracle

```text
$ python3 - <<PY  # pre-generation manifest inventory
AUTHORITY_ROWS_BEFORE 19
SNAPSHOT_ROWS_BEFORE 535
AUTHORITY_STALE_ROWS_BEFORE 6
config/ui_strings.v1.yaml
config/decision_narratives.v1.yaml
docs/core/01_PRODUCT_AND_REQUIREMENTS.md
docs/core/03_SYSTEM_ARCHITECTURE.md
docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
$ git diff --name-only -- docs/authority/authority_hashes.json data/manifests/snapshot_manifest.json docs/authority/00_AUTHORITY_MANIFEST.md
(no output)
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-12T20:53:47Z
$ PYTHONPATH=src .venv/bin/python scripts/build_manifests.py
BUILD_MANIFESTS_EXIT 0
$ PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_integrity_contract.py
21 passed in 0.25s
```

Post-generation oracle:

```text
AUTHORITY_ROWS_AFTER 19
SNAPSHOT_ROWS_AFTER 535
AUTHORITY_PATH_SET_EQUAL True
SNAPSHOT_PATH_SET_EQUAL True
AUTHORITY_CHANGED_ROWS 6
config/decision_narratives.v1.yaml
config/ui_strings.v1.yaml
docs/core/01_PRODUCT_AND_REQUIREMENTS.md
docs/core/03_SYSTEM_ARCHITECTURE.md
docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
SNAPSHOT_CHANGED_ROWS 0
AUTHORITY_MANIFEST_SHA256 a4a95d8491eabc23010a19d49a5e4640fb8f1a827d1a7db3b40915d6f16c956d
SNAPSHOT_MANIFEST_SHA256 2bd3a4e849aaec999c68d80aa64f27bfc846984c87c8d893053acf24482ac42e
```

The generator updated only `docs/authority/authority_hashes.json` and its
§11 mirror; `data/manifests/snapshot_manifest.json` remained byte-identical.
Manifest run count is 1; no further run is authorized.

## 2026-09-12T20:55:13Z — T11 alternate-path portability gate

The candidate was copied without `.git`, `.venv`, `.artifacts`,
`__pycache__` or `.autonomous-workflow` to the distinct absolute path
`/tmp/ior-s13b-portability-20260912-2055`.

```text
$ rsync -a --exclude .git --exclude .venv --exclude .artifacts --exclude __pycache__ --exclude .autonomous-workflow ./ /tmp/ior-s13b-portability-20260912-2055/
$ (cd /tmp/ior-s13b-portability-20260912-2055 && PYTHONPATH=src /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin/python scripts/verify_integrity.py && PYTHONPATH=src /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin/python scripts/reconstruct_snapshot.py --all && PYTHONPATH=src /home/barami/projects/industrial-opportunity-resolution-mvp/.venv/bin/python -m ior_mvp.screening validate --check-inputs && echo PORTABILITY_GATE_PASS)
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SCREENING VALIDATION PASS
PORTABILITY_GATE_PASS
```

The approved optional scratch-clone proof was not repeated after OD-16; the
owner had already verified all 17 frozen-pin tests on WIP `f9fec2d`.

## 2026-09-12T21:01:22Z — T11 complete CI and focused final proofs

```text
$ UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s13b-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make ci
INTEGRITY PASS
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
2275 passed, 1 warning in 26.61s
SMOKE PASS
152 passed, 4 deselected in 253.31s (0:04:13)
4 passed, 152 deselected in 43.37s
exit 0
```

Focused final proofs:

```text
$ N=$(git show ab4add6:src/ior_mvp/screening/api.py | wc -l) && diff <(git show ab4add6:src/ior_mvp/screening/api.py) <(head -n "$N" src/ior_mvp/screening/api.py) && [ "$(git diff --numstat ab4add6 -- src/ior_mvp/screening/api.py tests/test_screening_repository_and_api.py | awk '{s+=$2} END {print s+0}')" = 0 ] && echo API_ADDITIVE_ONLY_PASS
API_ADDITIVE_ONLY_PASS
$ PYTHONPATH=src .venv/bin/python -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']), p['change_ref'])"
VISUAL_MANIFEST_OK 56 S13b-bilingual-screening-surface:560695023cd626e4e6e936d7fc7d9b67465e0062d168a16eaec55597cad9f14e
$ PYTHONPATH=src .venv/bin/pytest -q tests/test_public_decision.py::test_no_fired_signal_deep_case_is_no_candidate_with_null_state tests/test_api.py::test_no_fired_signal_deep_case_returns_200_no_candidate_not_422 tests/test_api.py::test_no_candidate_expected_payloads_match_engine_output tests/test_dossier_contract.py::test_dossier_renders_no_candidate_disposition_label_instead_of_none
4 passed, 1 warning in 0.29s
```

The KL-34 fixture proof covers null formal state plus `NO_CANDIDATE`, HTTP
200 rather than 422, the frozen expected API/UI payload and bilingual dossier
labels without `None`/`null`.

## 2026-09-12T21:03:00Z — T12 IAC-6 candidate identity

Identity payload metadata:

```text
base f9fec2d72c118623e164564c2e2d4dd55f2c52b1
wip_commits d1d1462ce214f45b7fd286c6436a6bb2f0ca7f47 f9fec2d72c118623e164564c2e2d4dd55f2c52b1
wip_parent ab4add6adad742cb07eddd4cd8a9dd12f82efd8b
CANDIDATE_IDENTITY 611de6bf05c16ba2fc4bb328988b6e22f5d0f3428f9a45e62e0065c6590593b8
CANDIDATE_FILE_COUNT 85
INDEX_EMPTY_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
STATE_JSON_VALID_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
REPOSITORY_RELATIVE_FIXTURES_PASS
git status --short --untracked-files=all | wc -l
91
```

Both `.workflow/slices/S13-public-universe-screening/**` and
`.workflow/slices/S13b-bilingual-screening-surface/**` are excluded. No
candidate path is deleted; the required deleted-path representation remains
`sha256: null`, `bytes: 0`.

Canonical candidate rows (`sha256 bytes path`):

```text
5aea46f67422493694f124a89b36173724cf805bc77118f7c168d95ea632968c 30533 .workflow/state.json
d0fb68d48dcfcc184c8c9344cd5a756c6d687ffb781ad151de2f637dd1256855 24982 browser_tests/harness.py
3a3339c388c68eb3fba67a9fa0690d371f01784eeaf10dac6450c36f1f1a9f08 12437 browser_tests/pages.py
fc683bb96fd2a4cb75af74f4a09b759ba259d55a0180178905b87ac0409807dc 2407 browser_tests/parity_grammar.py
185970aaa001257c0a20f4f2c5851798f50c0a76c1d55fa823addefd2b4588e6 7445 browser_tests/test_accessibility.py
53db60e385ba53dd5855a63e54ec18f13c2610ce726a9b5f36e2452c4bf83276 13346 browser_tests/test_journeys.py
520424f9487e078b0030caa8bd4a5b26cc7800b3cb67a4c6b079d4212826309c 26041 browser_tests/test_screening.py
0c9c60b8210ff4eaaa48d019777a977c199ee30b77116eef4741a7248ee0128a 52041 config/decision_narratives.v1.yaml
27b85e9e5ddbcc8fb6d27d91fe9183066ef3a61af730c6b23d84ca3680d67695 59329 config/ui_strings.v1.yaml
5f614f48dc93a1fc2fe2def431b3bfdc5a46c41786d51104e6e7ec438e2d26a4 110145 docs/ARCHITECTURE_DECISIONS.md
868d5ee32305b19ca4ac336ad17a756930a21d1e9cf6cdd608497236320c0b26 33539 docs/BUILD_PROGRESS.md
cf201c9f9b0f900f71fcc623b730de7244f8bd0552b42071609dac4302ec643e 15340 docs/BUILD_ROADMAP.md
d9b7580f464dd156b58fa6feecd6242f2fef174710338ad316efe4e98e372f48 38199 docs/KNOWN_LIMITATIONS.md
66028cb5d7b8fe484ff93b663952618cf8d8a951eb7bb1c7ec25463911e39ac8 50246 docs/REQUIREMENTS_TRACEABILITY.md
b105116f3af95542a138941c199edbea7985fbb9ca762ef769faa22e39f28f98 10909 docs/authority/00_AUTHORITY_MANIFEST.md
a4a95d8491eabc23010a19d49a5e4640fb8f1a827d1a7db3b40915d6f16c956d 3376 docs/authority/authority_hashes.json
70035bb5e743afb3f4a869ecf50447b1657996b7603ab25b0835642c067b9eca 17520 docs/core/01_PRODUCT_AND_REQUIREMENTS.md
dcbac0b9283014c50b6218c833ed547bb307d5521a8a9f5c490955f584712385 12883 docs/core/03_SYSTEM_ARCHITECTURE.md
3d8a311c3179f13f1d9c80aaa4f57ae76be792281e0cea76bd8811f0173d8dfe 27298 docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
35fd6e9784e0026d0d40f7927d423ab1c6225dae618aa24ebbc9736c49cf719e 16891 docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
0ad3cbd24dd14c105b623cc4a8314ea1921eefb12a5d217d0990be1fa651cdce 6508 docs/implementation/UX_GENUI_DEMO_SPEC.md
0d753b51032f4fb24c43d09d8016fea95d75af8e8a7193589d80b624f5a88861 5113 src/ior_mvp/app.py
26e25770e5a5a8ccf436d3b3ebd5054583ca458c56e77c8f7912684e67b94295 11679 src/ior_mvp/config.py
153340580981b2cae3258bf3fcfa918664868e446715cf33d0a5a3c9a09544fb 8444 src/ior_mvp/decision_engine.py
fb3293ffa65e77830dad2540e7388a282f131d9c4077cd9e0aa237a2589ef8af 18437 src/ior_mvp/dossier.py
6f39c07d7996f2fbfee7510feb411376d53bfcce7c3ea047729f4dac1b9ce4d5 5009 src/ior_mvp/genui.py
494243a532d959c4a06126d74badca2b27f1e5abd4ca6e686a2eeda9d8b4372b 10099 src/ior_mvp/narratives.py
c77c77061fb5b44f6c179af5e6c4c8d88ea368c773e86415ceff815a2d98e417 53821 src/ior_mvp/public_decision.py
cba0aca54b0b70b4e0d6c063ea85534518dfa0a4f8ad9c5fec206a25b39aea9f 50493 src/ior_mvp/rules.py
8361f255d90021216eab039e66f80491bcad325173ef30b89bc90426ae39ee59 5843 src/ior_mvp/screening/api.py
68f85aaddd1922f2e69f215a55f05e78847aa2f54a37a0f3aa480e6284fdef61 5981 src/ior_mvp/screening/cli.py
501d0a2b980af5a0c29daa9d48142d809ee4af4ddbed6e375732e9e8ce19fe4b 675 src/ior_mvp/static/app.js
afeefb22d9b4e0d482ffdacd76bc12d98d8a929964d0cac5f2c8c24d93035da6 4274 src/ior_mvp/static/css/screening.css
aa84f68fa490533191e99bdc7f6348af028a9c26f1de12c73a77996a70be349a 11943 src/ior_mvp/static/css/tokens.css
e73bdd098529f16094b1815308beae9d198af965ca44c8541be71b71660d9d7e 10848 src/ior_mvp/static/css/workspace.css
f2e1549e714d50dca708baf0237d94c1a72807fa41aa78e1c0c4720af0a269e3 8821 src/ior_mvp/static/index.html
46a62bdb3fa9c6781b39394d7b9e7f8e618ccb935a8cad0eb47a23f992815760 1604 src/ior_mvp/static/modules/api.js
9db1bbe7cea3f2cfd5b20f5225f099959d2675c954fca8998e0d6b6ab4b11f70 4466 src/ior_mvp/static/modules/dom.js
2704a69b03f0b6108d464c881457cdf37e7c98225520b44fd6c3f71b359d0bce 4739 src/ior_mvp/static/modules/events.js
c135a5f834f8e5f058f94a6c6d457a4f4a0a015eeb567ab4d8e961f41d2cdd5e 2048 src/ior_mvp/static/modules/methodology.js
950e7f4b34816ede2f9e18d49955ac41fa94146bdbf2856086f7342f540d88ab 4235 src/ior_mvp/static/modules/portfolio.js
fdf06e13f58c006ddc752805a9f163f1108c3d4ee196f64fd427d77baf1c36a8 4074 src/ior_mvp/static/modules/renderers/decision.js
eca35891e22b475c528bd0c92991cd53c52a98f417742a6b8c9df62e96c21b18 2100 src/ior_mvp/static/modules/renderers/integrity.js
9ca947c6292ded17cce7dc67245cc45f3e3d732bc71a8b038e5d8ec99a032e40 1614 src/ior_mvp/static/modules/renderers/rules.js
3d3e8fe999a21177f22da66964cd4ce30d360efaa6ee8d6b6b4c369d5ec6a88b 7041 src/ior_mvp/static/modules/screening/evidence.js
86be3aeaf5a5f7e4e2d7fdf510aa431308233e06a2e1ea9d90a0dbf710125963 3902 src/ior_mvp/static/modules/screening/index.js
f74147af90161c5726e9631a8b1fe2beebf7889fff47b7edc28b5940091d9e0f 5265 src/ior_mvp/static/modules/screening/labels.js
3ab34e831b2e26e3372dc334a67d5a7270e2244730c7150befbbd52efa08fcbe 3059 src/ior_mvp/static/modules/screening/ledger-labels.js
61c609d2c7d21d7682bca42e8708b81a90401b2641afe0c37de83222651342d3 4252 src/ior_mvp/static/modules/screening/queue.js
1278b1a20f03487b80eb2ec5a161e556069cc7bfd56bf8bf94d702c275c0cede 5375 src/ior_mvp/static/modules/screening/record-evidence.js
18283308d13f8785ea5c18167999ef0ed49b35f2784df288561253c854084a23 3889 src/ior_mvp/static/modules/screening/record.js
af465851653f98dccf57ff2565bf3d73cf47f0c220c7a11efbaaa8bd20ba7038 5184 src/ior_mvp/static/modules/screening/summary.js
320afca14e87da09b6840f6fe62c008af8415960b82f985c6fe5bd69ffe902e1 453 src/ior_mvp/static/modules/state.js
fc045e8385ea3237e8533204985cfdf16b5e0a04669a07d1ed20c95eb847c170 396 src/ior_mvp/static/styles.css
611f180a8bb58553e153a63f5901a039c4be5697b8486a178717ee97342bc6c8 996 tests/fixtures/parity/parity-negative-cases.json
eb649138fa028e3ba391fa82d2e2d9fb58793fca9ec744c63766eefc1e3dbed4 199062 tests/fixtures/public_decision/no-candidate-no-fired-signal.expected.json
8445620603f42d14c2b983bdc2eb7b704a967b2d4b882fe258e8ef8ed48ad55d 8553 tests/fixtures/public_decision/no-candidate-no-fired-signal.json
f020ae3af5c270e782d6c2dd0771b8e71d7583ff49154c249eeeb51a16b8d975 1355 tests/fixtures/screening/evidence-partial.json
1f200951a25ba277f713918d52c270235460b061f085b6c1f624b1ffd2a677a2 392 tests/fixtures/screening/evidence-unavailable.json
c0093945c3c66e4494ccfd63335c188a4c8ac55eacf52c9dd1e309b9e90312cb 178 tests/fixtures/screening/queue-empty.json
40b88653d4865b8fe86bc54ded5cbc4e798fb53f5e1ae9d5aababa0d93ff4912 514 tests/fixtures/screening/queue-partial-robust_public_finding.json
c0155b2a5c6a8473710afb914e9cc6fd5f2973f1ed8ed3b4f978cf85ede93d6b 8993 tests/fixtures/screening/record-partial-030579.json
31827714288281416cfcdcecfdb4f75a8f776ceca722831805705bce03924598 3833 tests/fixtures/screening/summary-partial.json
649a0588df9a03bf29dad94ffc119dccce5b2ffd31fb8a360f884abf9ab5d3cf 2164 tests/fixtures/screening/summary-unavailable.json
029c3ce7db0f1c32eae830512bfb0ebfffc82681d9fb5905d8904500b367539a 27488 tests/test_api.py
8b64d4b508de5f24e9e3165c72613bdc595c8cf541997ffed81899fdce7b7600 5502 tests/test_authority_disclosure.py
2e1ce8f98bc60372084a84de7d5a69bc2b856f9febd415221f13fcaab895249e 18965 tests/test_browser_harness_contract.py
dc2e3876925efab6e3f32303d157f63ce82b1158e9082ad7ad09911fc08134ea 12667 tests/test_ci_contract.py
4cc2d17ac89875f9138983043704a3791b16161f55ed57b41715ec953a1a5556 29553 tests/test_decision_narratives.py
1ea342e27b4fab962cd87d37e4b0372403ac99bcfc12898182cf6b861cb505dd 17286 tests/test_dossier_contract.py
15b7d8ed6ea23685fcaea8725ef9adefc9cda08c982ca96940a6c6ee56247431 3333 tests/test_es_modules.py
17d926efdb0d7a880987446634a8c9d3d2b6fdc5e230009315bba5aa912ebe6f 3593 tests/test_genui_decision_contract.py
a650232004e2f27a535d90aae6630321521ac18b261eddee5332c4addf701768 32241 tests/test_integrity_contract.py
1128fb4f564251e10d849ba22f830b4de91a419910a67ef2f7861d764cb2009d 4955 tests/test_parity_grammar.py
00daaeacabbb581ea4197c628ac9a270185158bcaec52257cc7cec3f7ad9099d 2768 tests/test_performance.py
a145c49a612ed07b15dd2cde124220e7c88ece70d1439ce42769f83435f0c172 38317 tests/test_public_decision.py
0ea4f40b9c8d42b924a5054a8629263854844eec99da620e2d783449c66951fb 19440 tests/test_rules.py
00568bbd30cd1154317fd5c95f73ca2b020c57a77564c6a919db20ce242cdded 5150 tests/test_screening_candidates.py
4bd6f167b7331061a49eb7b1e64ef7a293d1e98e91d674a3138c75e2dea7cd2a 2465 tests/test_screening_leakage.py
d3ef2e1b5e8697d37ba8ca0b649febc487f2d94b5c275d25f78a46bacb6fd832 11176 tests/test_screening_repository_and_api.py
54d96b07e9ecd1670614b6332c5595750ea768f11fb244a63ea71343fe37c4b5 3425 tests/test_screening_surface_fixtures.py
40f23cf055f67f9604fee24fd435ee650b9b55463e5e9271de12bc054106f3dd 10821 tests/test_snapshot_migration_equivalence.py
432ce7abdbb2a87c4c10f53fced9895ddbe3142b5702f9d93913885d9154f17d 14928 tests/test_static_frontend.py
a8927c4263ec67a5d559f63f12d00f6965a1a46ad1c6b6addfaa025860cd8fd7 18679 tests/test_ui_catalogue.py
86e5102d72089d243b15baff1b44379bbd4c7ed1a9da9a65ce20c0de512cd44e 13168 tests/test_visual_baseline_contract.py
```

## 2026-09-12T21:06:00Z — IAC-6 identity serialization correction

The original historical identity remains recorded above:
`611de6bf05c16ba2fc4bb328988b6e22f5d0f3428f9a45e62e0065c6590593b8`.
Its 85 file rows were correct, but its payload deviated from amended IAC-6 in
two ways: it included a top-level `wip_commits` array, and serialization used
`indent=2` instead of compact `separators=(",", ":")`.

The recipe-conformant payload contains exactly the top-level keys `base`,
`wip_parent` and `files`. Every file row contains exactly `path`, `sha256` and
`bytes`; deleted paths, if any, use JSON null and zero bytes. It is serialized
with `json.dumps(payload, sort_keys=True, separators=(",", ":"),
ensure_ascii=False) + "\n"` and UTF-8 encoded before SHA-256.

```text
CANDIDATE_IDENTITY 8fb01e4d338380be52b01dfcc7fe26370958aefcbf1667d7c216bce29ddfb79c
CANDIDATE_FILE_COUNT 85
PAYLOAD_KEYS ['base', 'files', 'wip_parent']
ROW_KEYS ['bytes', 'path', 'sha256']
TRAILING_NEWLINE True
```

This correction changes only this excluded slice evidence record; the 85-row
candidate tree and its file hashes are unchanged.
