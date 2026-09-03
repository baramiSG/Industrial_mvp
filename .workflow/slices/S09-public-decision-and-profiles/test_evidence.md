# S09 test evidence — correction round (plan-7)

Recorded by implementer-composer slot 2 on 2026-09-03. Implementation evidence only; not approval, CI, or merge.

## Local gates

| Command | Result |
|---|---|
| `PYTHONPATH=src .venv/bin/python -m pytest -q` | 811 passed, 1 warning |
| `PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py` | INTEGRITY PASS |
| `PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py` | SMOKE PASS |
| `PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py` | Gate B PASS |

## Correction proofs

- G-1 two-row fixture: R2 FULL, ADVANCE route 3, `advance_support_signal_rule_ids ['R2']`.
- FULL-vs-degraded API: degraded trade -> INVESTIGATE `ADVANCE_SUPPORT_SIGNAL_DEGRADED`; baseline -> ADVANCE route 3.
- Missing route economics (mocked loader, no validator): HTTP 200 INVESTIGATE `ROUTE_DETERMINATION_UNRESOLVED`; prior failure was `Admitted deep case has no legal branch` at 422.
- Frozen outcomes: steel INVESTIGATE route null; PP REJECT route 0; simulation numbers unchanged.

## Browser

- Functional nodes: 118 passed (canonical container, `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs`).
- Visual refresh: `IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF=S09-generalized-public-decision-corrections make e2e-update-baselines` (fifth canonical execution); 4 visual nodes passed; 40 WebP entry hashes unchanged vs pre-refresh manifest.

## Visual provenance

- Pre-refresh manifest copied to `/tmp/ior-s09-manifest-before.json`.
- Post-refresh `change_ref`: `S09-generalized-public-decision-corrections`.
- `tests/test_visual_baseline_contract.py::test_visual_manifest_and_every_webp_hash_size_dimensions_and_rgb_decode_match` was red between first engine/catalogue edit and T12 refresh (stale `source_tree`); green after refresh.

## Authority

- Second justified `scripts/build_manifests.py` run; `authority_hashes.json` delta: `config/decision_narratives.v1.yaml`, `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`, `docs/core/04_CANONICAL_DATA_MODEL.md`, `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`, `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` plus `generated_on`.
