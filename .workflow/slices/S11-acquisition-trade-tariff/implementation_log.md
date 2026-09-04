# S11 implementation log

## Operator run parameters (recorded before live acquisition)

| Command | YEARS | MAX_REQUESTS | Rationale |
|---|---|---|---|
| acquire-universe un_comtrade | 2024 | 5 | One imports flow minimum plus credential probe headroom |
| acquire-tariff zatca_tariff | 2024 | 5 | Single tariff unit with INDEX_ENUMERATION pages |
| acquire-baci | 2024 | 3 | One BULK year plus terms attempt |
| acquire-partners wits_trade | 2024 | (prior run) | Explicit HS6 721049 and 390210 operator list |

## RunReports (2026-09-04)

- `un_comtrade`: CREDENTIAL_ABSENT, exit 3, coverage INCOMPLETE pages_fetched 0.
- `zatca_tariff`: MAX_REQUESTS_EXHAUSTED after 5 HTML pages, exit 3.
- `baci_cepii`: LICENSE_UNRECORDED, exit 3.
- `wits_trade` partners: prior run COMPLETE for two HS6 units; contracts repaired for `raw_file_path` and `compressed_sha256`.
- `wits_trade` universe: HTTP_ERROR (observed HTTP 403), exit 3, run_id `20260903T210859Z`, query_hash `27ed67ca6f2267ef904c9465f3990a9087fa6adebeb85b31f5545e549ce1d937`, coverage INCOMPLETE pages_fetched 0, YEARS=2024, MAX_REQUESTS=5.

## T8-GATE

Normalized analytical snapshots under `data/snapshots/partners/`: **1**.

## Manifest generation

- Candidate 1: premature `build_manifests.py` before T10 authority artifacts (superseded).
- Candidate 2: final run after Core/ADR/runbook/control records and acquisition code/tests green.

## BuildReport (partners rebuild)

Built `PARTNERS-SAU-WITS-TRADE-2026-09-03.json` with non-empty evidence passports and html.gz refs.

## Candidate 4 (implementer-fable, 2026-09-04) — DELIVERY-F-01 remediation

**Finding.** After reviewer-grok approved candidate 3 with zero findings, the supervisor's delivery gate ran plan-3 `verification[4]` (`git diff --quiet a610b49 -- … browser_tests/baselines`), which exited 1: candidate 3 had rewritten `browser_tests/baselines/v0.3.0/manifest.json` (`source_tree` rows for `src/ior_mvp/config.py` and `src/ior_mvp/data_repository.py`) and `manifest.sha256`, while ADR-015 and the runbook claimed a "provenance refresh" that the approved plan never authorized (non-goals: "no change to … browser baselines"; AC7/T12: "no baseline update").

**Root cause.** `browser_tests/visual_baselines.validate_manifest()` recomputes the SHA-256 of every top-level `src/ior_mvp/*.py` module and fails closed ("visual baseline source-tree provenance is stale") when they differ from the manifest. Plan-3 `files.modify`/DD-15 placed the acquisition config loader in `config.py` and the acquired-snapshot loaders in `data_repository.py`; any byte change there breaks the oracle unless the frozen manifest is rewritten. Candidates 1–3 resolved that tension on the wrong side.

**Remediation (minimum change, plan gates preserved).**

- `browser_tests/baselines/v0.3.0/manifest.json` and `manifest.sha256` restored to base `a610b49` bytes (working tree only; nothing staged).
- `src/ior_mvp/config.py` and `src/ior_mvp/data_repository.py` restored to base bytes.
- `src/ior_mvp/acquisition/source_config.py`: added `ACQUISITION_SOURCES_PATH` and `@lru_cache acquisition_sources_config()` (YAML load + fail-closed `validate_acquisition_sources`).
- `src/ior_mvp/acquisition/repository.py` (new): `universe_snapshots()`, `tariff_snapshots()`, `partner_snapshots()` (`lru_cache`, fail-closed validators, test-double rejection, file name must equal `snapshot_id`) and `clear_acquisition_caches()`.
- `src/ior_mvp/acquisition/cli.py`, `scripts/reconstruct_snapshot.py`, `tests/test_acquisition_{config,connectors,coverage,reconstruction,size_budget,snapshots}.py` import the relocated loader; the CLI clears only the acquisition config cache.
- ADR-015 "Visual baseline provenance" claim replaced by the module-placement record; runbook section replaced by "Visual baselines" (no baseline change; never `make e2e-update-baselines`).
- Regression tests: `tests/test_frozen_public_evidence_pins.py` adds `browser_tests/baselines` to the frozen-path diff, pins the baseline tree separately and calls `validate_manifest()` directly; `tests/test_acquisition_config.py` pins the relocated loader path, caching and fail-closed load; `tests/test_acquisition_snapshots.py` proves the loaders read only their kind, validate, cache, and reject test doubles under a temp data root.

**TDD evidence (`.autonomous-workflow/evidence/s11-acquisition-trade-tariff/4/`).** `red-1-inherited-tree` (collection errors for the relocated modules), `red-1b-pins-inherited-tree` (2 failed: frozen-path diff), `red-2-frozen-manifest-stale-provenance` (1 failed: "visual baseline source-tree provenance is stale" with the manifest frozen and the two modules still modified), `green-1-focused-regression` (38 passed). The provenance test was first written against `browser_tests.visual_baselines.validate_manifest`; the first full `make ci` (`plan-verification-27`, first driver pass) failed because `uv sync --locked --extra dev` prunes Pillow (an e2e-only dependency) before pytest. The test was rewritten as a PIL-free mirror of the oracle's provenance checks (`visual_provenance_problems`) with three detector meta-tests on a temporary tree (modified top-level module, unpinned new module, stale digest) — `red-3-tariff-years-and-pins-pilfree` / `green-2-tariff-years-and-pins`.

**Second deterministic gate failure found while running every approved-plan verification command (`plan-verification-09`, first pass, exit 1).** Plan `verification[9]` runs `acquire-tariff --source zatca_tariff --max-requests 1` without `--years` and expects exit 4 (offline guard); the inherited CLI made `--years` required on `acquire-tariff` (argparse exit 2), while `main()` already exempted `acquire-tariff` from its own `--years` check. `verification[6]` forbids an optional `years` action on any acquire command, and the plan interfaces (`acquire_tariff(source_id, *, deps, max_requests)`), DD-19 and the Makefile spec (`acquire-tariff [SOURCE=zatca_tariff] MAX_REQUESTS=<n>`) give `acquire-tariff` no `--years`. Correction: `cli.build_parser` adds no `--years` to `acquire-tariff`; `pipeline.acquire_tariff` drops `years`; `plan_units(TARIFF)` builds the single whole-tree contract with `periods=()` and ignores `years` (the tariff unit key `("ALL_TARIFF_LINES",)` is period-independent, DD-21); Makefile `acquire-tariff` drops `YEARS`; `tests/test_acquisition_cli.py` asserts no `years` action on `acquire-tariff` and runs the exit-4 probe exactly as `verification[9]` does; `tests/test_acquisition_reconstruction.py::test_plan_units_tariff_refuses_empty_years` (which pinned the plan-nonconformant behaviour) is replaced by `test_plan_units_tariff_is_one_period_free_unit` (one unit, `ALL_TARIFF_LINES`, `("ALL",)`, `periods == ()`, years ignored, `plan_requests == 1`). ADR-015 item 5, Core 05 §11 and the runbook now state the DD-19 rule precisely; the stored tariff run `20260903T212901Z` (issued with `--years 2024` by the candidate-3 CLI) is unchanged raw evidence.

**Manifest generation (second run, sequence step 4).** Reason: the Core 05 §11 wording correction above changed a hashed authority file. `build-manifests-second-run` ran `scripts/build_manifests.py` once. Diff 1 — `docs/authority/authority_hashes.json`: row `docs/core/05_DATA_SOURCES_AND_INGESTION.md` `48f2fb1907f41189852afe6fc3594ab207751a92002b42a4c53fac2efa816420` / 11,551 → `21bf334d74a3d19d39c39ff981e3f598cc1fd9c85f81704dce8857306a00332f` / 11,752; `generated_on` 2026-09-03 → 2026-09-04; no other row changed, none added or removed. Diff 2 — `data/manifests/snapshot_manifest.json`: `generated_on` 2026-09-03 → 2026-09-04 only; all 63 rows identical. The Manifest §11 Core 05 row was copied from the generated JSON. `post-generator-integrity-reconstruct`: INTEGRITY PASS, RECONSTRUCTION PASS (1 snapshots, 4 artifacts), integrity-contract and authority-disclosure tests 22 passed.

**Approved-plan `verification[26]` cannot pass on this evidence (surfaced, not worked around).** Its last assertion requires the literal `REDACTED` in some `data/raw/**/*.json` whenever any configured source has a `credential_env_var`. The only credentialed source, `un_comtrade`, was honestly recorded `CREDENTIAL_ABSENT` with zero requests (`attempt.json`: `observed_response: null`, `credential_present: false`, `endpoint_or_document: "UNAVAILABLE"`), and the connector sends the credential in a request header, so no stored URL, header subset or error text can carry a redaction marker until an owner-supplied `IOR_COMTRADE_SUBSCRIPTION_KEY` is used in a live run — which the plan forbids inventing. Raw records are write-once evidence and were not altered. This is reported to the supervisor as a plan-level inconsistency between `verification[26]` and the plan's own anticipated `CREDENTIAL_ABSENT` outcome (plan risk "UN Comtrade may require a key").

## Candidate 5 (implementer-composer, plan-4, 2026-09-04)

**Scope.** Owner ruling 2 (`.autonomous-workflow/owner-decisions/s11-acquisition-trade-tariff-2.json`, SHA-256 `1c52d3dbdc44b3c908fb35b9caf499bb010a07cf57887264df7d674507eb0b86`) replaced plan-3 `verification[26]` with DD-23 semantic stored-evidence checks. Plan-4 delta only: `stored_evidence_problems()` and detector meta-tests (DD-23 a–d), UrllibTransport sentinel redaction proofs and DD-24 credential-echo guard in `connectors/base.py`, ADR-015 verification-contract paragraph, runbook Environment sentence, slice/control records.

**Immutability.** No acquire-* command run. `data/raw/**` (53 files), `data/snapshots/**`, manifests, `config/*.yaml`, `docs/core/**`, `docs/authority/**`, and `browser_tests/**` byte-identical to candidate 4.

**TDD evidence (`.autonomous-workflow/evidence/s11-acquisition-trade-tariff/1/`).** RED: DD-24 transport test `test_dd24_credential_echoed_body_not_stored` before guard (page stored, sentinel in temp store). GREEN: after `CredentialEchoed` guard; repository `stored_evidence_problems` assertion GREEN on inherited honest evidence; transport redaction proofs (1)–(4) GREEN as regression pins on inherited transport.
