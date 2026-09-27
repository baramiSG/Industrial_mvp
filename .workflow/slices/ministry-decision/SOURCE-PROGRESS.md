# Ministry M source progress

Status: Implementation in progress; verification for the new candidate pending.
Worktree: `/home/barami/projects/ior-worktrees/ministry-decision`
Branch: `slice/ministry-decision`
Base: `bbcfe7836eb4e3c3e71ddd6b95986c45324267d4`
Tree at start: `6dbd0cfc2a3a15f8984775795e4bd7a5bfc26ea7`
Source is uncommitted. No generation, manifest, commit, push, or Aura operation was run.

The external mission path rejected this write from the implementation sandbox. This copy is the worktree record.

## Completed in this pass

1. Hadeed/UNICOIL attribution. Coarse certification and process edges attach only when every evidence id belongs to exactly one producer. The opportunity-wide R9-S ledger is stored on the engine-run evidence record as `REFERENCE_CASE`.
2. ADR-033 and the searchable methodology mirror §6.0 / §10.2 text. The governing DOCX binary is not amended.
3. Scenario 2.2.0 for steel and polypropylene. Exact preceding bytes are in `data/synthetic/historical/v2_0/`. The two live registers hash equal. Legacy plant, economics, and ground-truth leaves are unchanged.
4. Register validation, per-plant discovery, and finite line comparison. Public analysis omits the new blocks. Older simulated scenarios return `NO_REGISTER` / `NO_LINE_RECORDS`.
5. Dossier walk rejects `candidate_discovery`, `line_assessment`, `candidate_register`, and `candidate_lines`.
6. `qualification/profile hard gates` maps to producer capability.

## Focused results

RED, before the attribution repair:

`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-ministry-m-pyc PYTHONPATH=src .venv/bin/pytest -q tests/test_graph_projection.py::test_hadeed_does_not_inherit_unicoil_process_or_certification tests/test_graph_projection.py::test_public_adjacency_is_per_producer_and_keeps_reference_summary`

2 failed. Hadeed inherited a UNICOIL certification edge. Hadeed adjacency `fired` was true.

GREEN, after the repair, the same two tests passed. A later focused set of 17 tests passed in 0.34s, covering the register, discovery, line comparison, line contract, qualification mapping, and the two attribution tests.

The frozen-artifact test `tests/test_graph_engine_feed.py::test_adjacency_explanation_matches_r9s_ledger_for_all_cases_both_modes` fails because the saved F projection has no `REFERENCE_CASE` ledger. That failure stays until an authorized generation. It was not bypassed.

## Backend batch — 2026-09-26

The strict register, line contract, P01–P08 findings, and guarded line supply now match the approved contract for the cases listed in `BACKEND-COMPLETION.md`. Focused result: 31 passed. The six-test RED log is in `evidence/backend-red.txt`.

## Not started

Governing DOCX binary, policy 1.5, UI catalogue successor, executive `resolution.js` and `candidates.js`, graph `context.js`, screening bridge, scene stems, browser helper, manifest generation, and Aura. Overall M source remains pending.
