# AGENTS.md — Industrial Opportunity Resolution Domain Overlay

This file is **not** a replacement for Flight Control or the Universal New-Project Guide. Reusable planning, review, task-state, retry, CI and merge behavior remains governed externally through:

- `${FLIGHT_CONTROL_HOME}`
- `${UNIVERSAL_NEW_PROJECT_GUIDE}`

If either external authority is unavailable, an agent may inspect and test the repository but must not invent a competing orchestration protocol.

## Mandatory authority order

Before changing domain behavior, read in this order:

1. `docs/authority/00_AUTHORITY_MANIFEST.md`
2. `docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx`
3. the relevant file in `docs/core/`
4. `config/thresholds.v1.yaml`
5. `config/sector_profiles.v1.yaml`
6. `config/evidence_policy.v1.yaml`
7. the affected hashed snapshot and its golden test

`docs/authority/methodology_extracted.md` is a searchable convenience mirror. It is not authoritative over the DOCX.

## Project-specific non-negotiables

1. **Synthetic evidence can never change `real_decision`.** It may affect only `simulation_decision` and `active_decision` in simulated mode.
2. Never label a synthetic value as observed, official, Ministry-provided or Class A/B/C.
3. Never produce `ADVANCE` while a decision-critical identity, target-specification demand, domestic capability or hard process/regulatory gate remains Class D/E in the real evidence branch.
4. Unknown capability dimensions never improve adjacency. Preserve the λ penalty, Kmin gate and hard-gate rule.
5. Brownfield, non-financial and no-action routes are evaluated before supported greenfield.
6. Unit value is a diagnostic signal, not proof of grade or quality.
7. Thresholds are loaded from versioned configuration. Do not duplicate their values in implementation logic or modify them case by case.
8. Golden cases run against hashed local snapshots only. Do not call live sources in CI.
9. The steel public fixture must remain `INVESTIGATE`. The polypropylene public fixture must remain `REJECT` for generic capacity support.
10. Public intervention and overrides remain accountable acts. Code may calculate and recommend; it may not impersonate authorization.

## Required proof for a domain change

A change is not complete until it includes, as applicable:

- updated methodology-to-code mapping;
- deterministic unit tests at threshold boundaries;
- a golden-case regression;
- synthetic-leakage test;
- snapshot/config hash update through the approved change gate;
- evidence of `pytest -q` and `python scripts/verify_integrity.py` passing.

## Scope control

Do not broaden a slice to add unrelated dashboards, generic AI chat, investor CRM, document management or live connectors. The demo product is one adaptive decision workspace centered on the Decision Dossier and the Public / Ministry Simulation evidence toggle.

## Build-control records (completion build, September 2026)

The owner delegated Supervisor/Flight Control authority for the completion build on 2026-09-02. Records live in the repository so that work survives restarts and context loss:

- `docs/BUILD_ROADMAP.md`, `docs/BUILD_PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/KNOWN_LIMITATIONS.md`
- `.workflow/state.json` (machine state) and `.workflow/slices/SXX-<slug>/` (persona, context, plan, plan review, implementation log and review, reviewer findings, test evidence, PR record, completion)

Every slice runs on branch `slice/SXX-<slug>` and passes: planner subagent (model ≠ Supervisor) → Supervisor plan review → implementer → Supervisor implementation review → independent reviewer (model ≠ implementer) → zero findings → local gates → PR → CI green → squash merge. No subagent approves or merges its own work.

Start-of-slice ritual: read this file, `docs/authority/00_AUTHORITY_MANIFEST.md`, the mapped `docs/core/*` documents, the five control documents, `.workflow/state.json`, prior slice records, the affected code and tests; discover and use applicable skills; write `persona.md`; confirm branch and base commit; confirm no secrets or prohibited files will enter Git.

Any change to `config/*.yaml`, `data/**`, `docs/core/**` or a golden expectation is an authority change under manifest §7. It must be justified in the slice ADR and PR before `scripts/build_manifests.py` is run, and the two public golden outcomes must be shown unchanged.
