# Ministry F narrow test-pin adoption (2026-09-26)

Status: narrow test-source edits complete; candidate source writes paused. This is test-pin evidence, not implementation review, generation approval, visual capture, or baseline adoption. Persona: senior test engineer for governed graph evidence, applying project-orientation, task-standards, github-flow, TDD's independent-oracle discipline, sanad-provenance, al-muhasibi and muhasabah-gate. Approved scope: packet `AUTHORITY-AND-PINS.md` §§2–3 and `DELIVERY.md`; latest owner workflow record `20260926-proportionate-delivery-workflow-update-1.json` removes blanket duplicate local verification. Governed authority and plan were read in prior source-correction turn and reused unchanged here.

## Exact test-source literals

- `tests/test_integrity_contract.py:1298`, `tests/test_s17_generation.py:60`, `tests/test_s17_status_docs.py:33`: snapshot manifest count `730` → `732`. The actual post-generation manifest has 732 entries; current projection `GRAPH-SAU-2026-09-12-fd70279732aa` contributes the two new immutable projection members. Existing 925 nodes/1,045 edges and authority count 20 stay pinned.
- `browser_tests/test_graph.py:845`: current engine token `ENGINE-6b54371e99f3` → `ENGINE-bd1cbfb71689`; historical CSS substitution token `ENGINE-7ae34188bdec` remains. The first public edge still targets `INT-SAU-H0-721049-route-5`, now asserted at row index 0; the second row (index 1) targets Product `SAU-H0-721049`; index 2 retains that Product assertion. The 12-row/five-token count, untouched repeat, string-rewrite and EN/AR anchor geometry assertions remain.
- `browser_tests/graph_pages.py:409,413`: steel evidence-to-change selected-edge Arabic source-span counts public `7` → `0`, simulated `9` → `2`. No other passport count changed.

## Independent count basis and rendered checks

Read-only `artifact_graph_payload('evidence_to_change', 'SAU-H0-721049', mode)` enumeration selected first public edge `REL-a1e2c4e7b727a78044e6` and first simulated edge `REL-693b666ca9d0375aa47e`; both target their route-5 interventions and both have `properties.evidence_ids=[]`. Public graph and edge are non-synthetic, so the selected panel has no source-text or disclosure spans. Simulated graph and edge are synthetic, so the existing graph-level and selected-edge disclosure each render one English source island. The rendered AR parity test independently measured `source_spans=0` and `2`; it also checked empty island failures, Latin leakage and label leaks. Raw edge inventory has 12 public and 15 simulated edges; those totals were deliberately not used as passport counts.

The first isolated canonical-container AR run failed at the old public edge literal: actual 0 versus expected 7. After pinning 0, the second AR run failed at the old simulated edge literal: actual 2 versus expected 9. These are expected RED oracle mismatches, not geometry defects. Logs: `W/.artifacts/e2e/pin-adoption/selected-ar.log` SHA-256 `cc38e810d4c8767c5b2bcb23b3d83ae61460a02077d02aa29d186263fab85a27`; `selected-ar-2.log` SHA-256 `f90b6ae40f22deb3f566c4964ba257cca143e3ca27a988f0e01e0aa2dbeb563b`.

Focused host command: `uv run --locked --extra dev --extra graph pytest -q tests/test_integrity_contract.py::test_s17_history_current_graph_and_authority_outputs_are_manifested tests/test_s17_generation.py::test_in_memory_g17_is_deterministic_and_writes_nothing tests/test_s17_status_docs.py::test_s17_status_distinguishes_completed_generation_from_f01_visual_refresh` → **3 passed**. Selected browser command used `scripts/run_visual_baseline_container.py`'s exact allow-listed mounts and canonical image `sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112`, `--network=none`, dynamic fixture server, `IOR_E2E_ARTIFACT_DIR=/workspace/.artifacts/e2e/pin-adoption`, `-k 'test_graph_narrow_panel_contains_controls_and_text and steel and 1440'`, Chromium, compare mode → **2 passed, 40 deselected**. Final log SHA-256 `ce654be73c65bae11fa9f26d1653f62ad3bf75d13e895d356c993a2874b7a683`; session summary reports collected 2, passed 2, failed 0, skipped 0. `git diff --check` on the five edited test files exited 0.

## Source hashes, limits, handoff

```
477ed74944433083ff453d34182ae51897f077399201a0312096fd455184fabf  tests/test_integrity_contract.py
6f14155a6dd02ca0c4665febf9c3d52d1a4c6fb2901b94b894cd7e0570585a7f  tests/test_s17_generation.py
9538c29027bbe2b47686e04f3b06d05daf3b7b207df6788468f5f6c439addb7f  tests/test_s17_status_docs.py
ae1ae170ea9a6b3ee92bb3630683289825b0aa5f1c6793bc3e7c1f35208b53f2  browser_tests/test_graph.py
1d248d9c2e268f9cbabcc89466bc7eeeedb0afa8e710df486ef6ee9819fd1afd  browser_tests/graph_pages.py
```

Pending with coordinator: remaining existing graph selectors including separate source-disclosure/CSS negative controls; source-equal visual comparison and governed canonical capture/baseline pins; later exact-tree review and hosted checks. The selected browser run proves the affected rendered steel 1440 EN/AR matrix only. No production/Core/config/data/generator/baseline edit, Git index/ref/commit, Aura action, or independent implementation approval was performed in this pin adoption.

Sanad: generated `data/graph/current.json` and immutable projection, snapshot and authority manifests; read-only raw fixture enumeration; actual browser RED/GREEN logs and run summary; focused host test output; five SHA-256 file hashes above. Muhasabah: PASS for this narrow pin task—no guessed span count, no conflation of total graph edges with rendered source spans, no claim that unrun CSS-negative or capture gates passed, and no second approval claim.
