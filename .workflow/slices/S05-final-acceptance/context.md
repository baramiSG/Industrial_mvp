# Context — S05 Final Acceptance

## Base and branch
- Base: `main` after S04 squash merge (record SHA). Branch: `slice/S05-final-acceptance`.
- State after S04: 231 tests; gates = prohibited → threshold → compile → node → integrity → Gate B (policy + reconciliation + ground-truth back-test) → pytest → smoke; thresholds 1.1.0; evidence_policy 1.1.0; scenarios 1.1.0; hashes current. CI runs on PRs #1–#4 all green 4/4.

## Residual notes carried from independent reviews (fix or record, each with evidence)
- S02 (Grok 080a70fa): validator exempts configured `1.0`/`3` by design; `check_threshold_literals.py` uses top-level `glob("*.py")` — make recursive (`rglob`) or document; no GenUI test for PP `supplier_concentration == {}` — add test; R1-D `confidence_cap` string — record.
- S03 (Grok 5aef4c24): `/api/opportunities` list route maps only `EvidenceIntegrityError`; `RepositoryError`/`ValueError` there would surface as 500 — map to 404 consistently and test; `lru_cache` makes a successful scenario load sticky per process — record as accepted (process restart reloads); dossier HTML test uses a weak "0 synthetic records" substring — tighten.
- S04 (Grok 1194ea8b): an unused local variable in the new engine code — remove; stale FR-044 traceability pointer — correct; scenarios not deep-copied before use in `_simulate` — confirm no mutation of cached scenario (add a test asserting the cached scenario is unchanged after `analyze_simulated`).

## Traceability promotion policy for S05
- Rows still `IMPLEMENTED` from S01 (their tests executed in every CI run since PR #1) → `TESTED` with CI evidence, then all `TESTED` rows → `COMPLETE` after the S05 PR merges with CI green. FR-073 stays `NOT_APPLICABLE`. NFR-005 gains a timing test and becomes `TESTED`. GATE-G (product) is proven at API + static-contract level; browser interaction remains KL-22 (record the exact scope in the row).

## Release
- Version `0.1.0` → `0.2.0` in `pyproject.toml` and `src/ior_mvp/__init__.py`; `CHANGELOG.md` 0.2.0 entry summarising S01–S05; `uv lock` re-run (project version appears in `uv.lock`) — deterministic; Docker image rebuild proof. Tag `v0.2.0` on the merge commit after CI green (Supervisor).

## Documents to produce/update (owner mandate §28)
`docs/FINAL_BUILD_REPORT.md` (what was built / not built; requirements completed; tests executed; validator results; CI status with run IDs; PRs merged; architecture implemented; acceptance demonstrations; security/privacy validation; deployment instructions; known limitations; deferred work; unresolved owner decisions; final commit; tag), `docs/OPERATOR_RUNBOOK.md` (start/stop/restart, health, logs, demo script pointer, failure interpretation, integrity/gates), `docs/DEPLOYMENT_GUIDE.md` (WSL, Linux, Docker; ports; env vars; security posture from SECURITY_AND_DEPLOYMENT_NOTES), `docs/DEVELOPMENT_GUIDE.md` (update gates list incl. Gate B; slice workflow; authority-change procedure), `docs/KNOWN_LIMITATIONS.md` (final state), `docs/ARCHITECTURE_DECISIONS.md` (ADR statuses final; ADR-009 for the S05 residual fixes if any behaviour changes), `docs/REQUIREMENTS_TRACEABILITY.md` (final statuses).

## Constraints
- No config, data, `docs/core` or DOCX change; no hash regeneration (integrity must PASS unchanged). Behaviour changes limited to the residual fixes above (404 mapping on the list route; unused local; validator recursion) — each with a test.
- Repository keyword scan (`TODO|FIXME|HACK|TEMP|temporary|placeholder|mock|disabled|skip|xfail|hardcoded`, case-insensitive) over tracked files excluding `.workflow/` plans: every hit must be listed with a disposition (legitimate — e.g. `DISABLED` execution state, `monkeypatch` in tests, `.env.example` placeholders — or fixed).
- Execution conventions as before; detached scripts under `.workflow/logs/`; Supervisor controls commit/push/PR/merge/tag.
