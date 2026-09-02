# Context — S07 Bilingual Interface Foundation

## Base and branch
- Base: `main` at `6d00e27ff156e1342d488495c7b48e68eeefe100` (S06 squash merge; default-branch CI run 33602662668 success, five jobs). Branch: `slice/S07-bilingual-interface-foundation`.
- Working tree at branch start carries the Supervisor's post-merge S06 records (`pr_record.md`, `completion.md`, `state.json`, `BUILD_PROGRESS.md`, KL-22 closure, V3-A1..A6 → COMPLETE). They are committed with this slice; the Implementer must not modify them.
- State: 309 default tests (Python 3.12 and 3.14); `browser_tests/` 17 tests / 62 Chromium nodes; `make ci` = eight legacy gates + preflight + browser suite; five hosted CI jobs.

## Governing decisions for this slice
- `SLICE_GRAPH.md` S07 (approved with amendments): ES-module decomposition (< 200 lines, named exports); tokens only with a scanner; governed bilingual string catalogue for UI chrome; `lang`/`dir` switching with persisted choice; offline Arabic-capable typography (vendored open-licensed fonts with licence files, or a justified system stack); `evidence_policy` 1.1.0 → 1.2.0 adding the Arabic synthetic display label; every synthetic marker in both languages; Playwright parity journeys per locale with RTL screenshots; **governed visual-regression baselines established here** (owner ruling R-4) for both locales and all four widths with a reviewer-approved update procedure. Closes KL-21 and KL-31.
- Authority changes in this slice (Manifest §7.3/§7.4, ADR-010 basis, slice ADR-011 required): `config/evidence_policy.v1.yaml` 1.2.0; a new governed catalogue artifact (planner proposes path/format; if it lives under `config/`, `scripts/build_manifests.py` must hash it and Manifest §11 must list it); Core 01 v2 NFR-007 (bilingual interface parity and RTL) and Core 09 v2 §2.7 (Playwright layer present; visual baselines governed like goldens) as the opening Core v2 edits — minimal wording, with a `core_version` marker strategy the planner proposes; exactly one `scripts/build_manifests.py` run after regression with the diff limited to the changed governed files. No `thresholds`, `sector_profiles`, `data/**` or DOCX change. Goldens unchanged.
- Engine-emitted analytical text (rule `result`/`decision_effect`, decision `headline`/`rationale`, `missing_facts`, `conditions`, scenario `decision_narrative`) is English from code and governed snapshots until S08–S10 introduce bilingual narrative catalogues. **S07 must not translate it.** It is rendered inside the Arabic UI as explicitly marked source-language islands (`lang="en" dir="ltr"`, bidi-isolated) with a governed caption from the catalogue (e.g., "Analytical text in source language — bilingual narratives arrive in later slices"). This interpretation is DERIVED from SLICE_GRAPH S07/S09/S10 and must be stated in the plan and documented for the reviewer.
- UI edits are the substance of this slice, but decision semantics, GenUI component types, API contracts (other than additive locale resources), synthetic labelling rules and golden outcomes must not change.

## Observed facts (Supervisor read, 2026-09-02)
- `styles.css` (now 353 lines after S06): `:root` tokens at lines 1–30 (inks, paper/surface/line, teal/gold/red/blue variants, shadows, radii, `--sidebar`); many hex literals remain outside `:root` (KL-21); media queries at 1180/900/560 plus the S06 reduced-motion block; `body` font stack `Inter, ui-sans-serif, system-ui, …` (Inter is not vendored — falls back to system fonts); `.opportunity-card .arabic` uses `"Segoe UI", Tahoma, sans-serif`.
- `index.html`: `lang="en"`; all chrome text hard-coded in English; one `.sr-only` Arabic note; nav/mode/hero/section headings; `/docs` "API" link (KL-31).
- `app.js` (464 lines, single file): `state`, formatters, `getJSON`, portfolio/KPI/cards/select, manifest renderers for the ten approved components, methodology summary, extraction demo, global events. English strings inline throughout (labels, KPI titles, notes, toasts, chart legend, table headers).
- `dossier.py`: English HTML with inline CSS (one `--dossier-muted` token from S06); one `dir="rtl"` paragraph; disclosure label from policy.
- `genui.py` passes `synthetic_label` from `analysis.simulation_scenario.display_label` (policy string) into the banner props; `rules.py` synthetic rows carry `display_label`; `evidence.py` validates `display_label` equals policy `synthetic_isolation.display_label` ("SIMULATED — NOT MINISTRY EVIDENCE").
- `scripts/build_manifests.py` hashes the DOCX, three named config files and `docs/core/*.md`; a new governed artifact needs an explicit entry there and in the Manifest §11 table (`docs/authority/00_AUTHORITY_MANIFEST.md` HASH_TABLE block).
- S06 harness: `browser_tests/harness.py` case/viewport constants, `BrowserFailureCollector`, axe/RTL/PDF helpers; `conftest.py` contexts with `locale="en-US"`, `reduced_motion="reduce"`; 40 documentary WebPs under the S06 slice record (never compared; do not touch).
- Hosted browser job: fontconfig chose DejaVu Sans for `:lang=ar` despite `fonts-noto-core`; local WSL also DejaVu. Vendored fonts make rendering deterministic for baselines.
- Python Playwright has no `to_have_screenshot`; image comparison needs a pinned pure-Python approach (e.g., Pillow) or a small deterministic diff implementation; the planner justifies the choice and pins versions.

## Constraints
- Offline: no CDN, no external font or script; the S06 external-origin blocker must stay clean in both locales.
- `PYTHONPATH=src pytest -q` stays browser-independent; new static contracts (token scanner, module contract, catalogue parity, policy label) live in `tests/`.
- Baseline images: tracked under `browser_tests/` (planner names the folder), PNG or WebP with a hashed manifest, size budget stated; update only through an explicit `make e2e-update-baselines` (or equivalent) that is recorded in the slice record and approved by the reviewer; CI never updates baselines.
- `make ci` and the hosted browser job must remain within a reasonable time budget (the planner states the expected node count and duration).
- No `.env` read; no secret values; no live external source.

## Records to produce in this slice folder
`plan.md`, `plan_review.md`, `implementation_log.md`, `implementation_review.md`, `reviewer_findings.md`, `test_evidence.md`, `pr_record.md`, `completion.md`; ADR-011 in `docs/ARCHITECTURE_DECISIONS.md`.
