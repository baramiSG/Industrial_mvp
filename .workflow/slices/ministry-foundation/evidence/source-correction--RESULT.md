# F source-readiness correction result

Scope: sole authorized correction writer in `slice/ministry-foundation` after the Cursor exit recorded in `WRITER-TRANSFER.json`. This result covers F-R1 and F-R2 only. It does not approve the implementation, generated artifacts, delivery, or a new methodology. The original `SOURCE-READINESS.md` and its combined graph delta remain historical and are superseded for the corrected source.

## Corrections

- **F-R1:** `simulation_capability` now starts from the public case's ordered required decision-gate names, overlays supplied scenario declarations by name, and leaves omitted names `UNAVAILABLE`. Empty and partial mappings therefore withhold D*. A supplied known failure remains a known failure beside a different omitted gate. Original scenario and public records are unchanged. The accepted unknown-name validators and capability formula were not edited.
- **F-R2:** A simulated profile gate Capability node now carries only its profile status, raw declaration, and `::hard_gates` source. Its existing Scenario node carries each decision-specific gate's typed status, raw declaration, and `::decision_specific_hard_gates` source. A profile `RESOLVED` and decision-specific `KNOWN_FAILURE` therefore remain separate statements. Decision-only names are retained on the Scenario node. No graph node, edge type, status priority, or decision rule was added.
- **Core09:** replaced the newly added pre-generation graph-ID/count paragraph with identity-free procedural proof wording. It requires the generated identity to derive from admitted inputs, match the authorized current projection, and carry independently enumerated count pins while preserving historical artifacts.

Only `src/ior_mvp/simulation.py`, `capability.py` (type annotation), `graph/projection.py`, `tests/test_capability_economics.py`, `tests/test_graph_projection.py`, and `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` were touched in this correction. These files already contained the prior writer's uncommitted edits; `file-hashes.txt` binds their complete corrected bytes, not just this incremental patch. No staging or commit occurred.

## Executed proof

- Corrected RED: the five named test functions (six parameter cases) exited **1, six expected failures** before production changes; see `focused-red.log`. The first attempt's fixture path error was repaired and excluded from the meaningful RED claim.
- F-R1 GREEN: the partial, empty, and mixed-gate tests exited **0, three passed** after the `simulation.py` correction.
- F-R2 GREEN: the scoped streptomycin, disagreement, and decision-only graph tests exited **0, three passed** after the `graph/projection.py` correction.
- Final affected regression command (exact command below) exited **0, 251 passed, one generated-identity pin deselected, one Starlette deprecation warning**; raw output is `focused-green.log`. It includes all-eleven decision/active-decision and 22 gate-list tests, golden outcomes and economics checks already present, synthetic isolation, scenario validation/migration, and graph projection/artifact/loader/feed/service/API tests.
- Read-only graph property check exited **0**: `validate_projection` and `canonical_bytes` accepted the in-memory 925-node/1,045-edge graph; Neo4j `primitive_properties` encoded the Scenario's nested scoped declaration as JSON whose decoded value equals the artifact value. Output is `graph-property.log`. No graph artifact was written.
- `git diff --check` on the six correction files exited **0** with no output.

```text
PYTHONPATH=src .venv/bin/pytest -q tests/test_capability_economics.py tests/test_scenario_contract.py tests/test_scenario_validation.py tests/test_scenario_migration_equivalence.py tests/test_graph_projection.py tests/test_graph_artifact.py tests/test_graph_loader_offline.py tests/test_graph_engine_feed.py tests/test_graph_api_offline.py tests/test_graph_service_offline.py tests/test_s17_generation.py tests/test_golden_cases.py tests/test_synthetic_isolation.py -k 'not test_in_memory_g17_is_deterministic_and_writes_nothing'
```

## Historical RED-report errata

1. The original source-readiness report's 17 RED failures included two fixture `AttributeError`s (`object lacks target`), so not all 17 were product-bug reproductions.
2. Its synthetic sorted-capability test selected `CAP-SAU-TEST-alloy`. The real repository defects selected `capacity_time_window`; those findings must not be conflated.

## Limits and handback

The corrected source changes graph bytes and invalidates the earlier combined semantic delta and generated projection identity. Coordinator-owned exact source/semantic comparison, the all-eleven economics and all-22 need-provenance receipt, generation allocation, graph/current and manifest updates, visual/passport pins, full required gates, substantive Claude implementation review, and owner acceptance remain pending. The generated-identity pin was deliberately deselected because generation is forbidden in this phase; no pass is claimed for it. No generator, graph write, browser, PDF, service, Aura, other model, staging, commit, or push was run.

Sanad: direct handoff and approved F §2/§3, the two reproduced probe JSONs, current source/test reads, executed RED/GREEN/property outputs, `git diff --check`, and the complete SHA-256 list in `file-hashes.txt`. Prior PR/check/review receipts are attributed, not rerun here. Muhasabah: **PASS for this bounded correction and evidence record**; the first RED fixture error and the original report's two errata are explicit, and no pending generated or review gate is represented as complete. The five-stage Al-Muhasibi check rejected treating a missing mapping as resolved or collapsing conflicting scopes into one status; the tests and source preserve both uncertainties.

## Addendum: Core04 scoped-source wording before generation

The coordinator authorized one further wording-only correction to the new Core04 paragraph. Its final sentence now says that each profile and decision-specific declaration retains its own typed status, raw meaning, scope and evidence identifier, and that neither source confirms the other. This documents F-R2's implemented separation; it adds no rule or graph structure. The earlier result bytes were preserved as `RESULT.before-core04.md` (SHA-256 `c75af93e7b61b924f80d18183cfdce31201eb8e844d51d48fc90b1dd5d108487`), and the earlier hash list as `file-hashes.before-core04.txt` (SHA-256 `974a37434bb8463fa83ab72a5a82b4a88333a88afde093341867a1737f8cc91d`). The refreshed `file-hashes.txt` includes Core04 and current read-only hashes for the prior correction files. Its graph-test hash differs from the earlier list; this addendum makes no attribution or new test claim for that change. Core04 changed from SHA-256 `1d7920e32afd1d55dbb84dd59cee5f63f567e72781ecbceaebe2fb89f4ffdeff` to `7f07f7fd5e3db1262e0a9b0ac197eec373eb3d4a9729e5478e253c70b3e193f6`. `git diff --check -- docs/core/04_CANONICAL_DATA_MODEL.md` exited 0. No tests were rerun for this wording-only adjustment; the previous test receipts apply to the earlier source and test bytes as recorded above. The coordinator must bind the final source before generation.
