# Completion — S13b Bilingual Screening Surface

**State:** MERGED (2026-09-13). Merge commit `cdf6ab0aceb3c053c08daee0832615e580b779ef`; PR #23; PR CI run `34720051770` 5/5 on head `2cc18f1`; default-branch CI run `34720370015` 5/5 on the merge SHA. The S13 split is complete (s13a #21 `834ba60`, s13b #23 `cdf6ab0`); parent S13 is COMPLETE.

## Delivered

- `app.py` mounts the s13a screening router ahead of the SPA fallback; one additive read-only route `GET /api/screening/evidence` (OD-12) exposes the eight verbatim universe passports and acquisition units (public-only, `synthetic_flag: false`, explicit `NO_SCREENING_SNAPSHOT` state); the three existing routes are contract-identical (`API_ADDITIVE_ONLY_PASS`, key-set pin).
- Analyst Screening surface (nav item 06) in English and Arabic: summary (universe status with reason codes; coverage accounting for tariff tree, partner detail and production aggregates; disposition and indication counts; 135 persistence-only unqueued; methodology §8.2 mapping incl. §8.2(c) `NOT_CALCULABLE`), five route-specific queues (`pareto_rank`, `ordering_basis`, counts, pagination, no ordinal master list; two real empty queues rendered as explicit states), record drill-down (screening ledger through the catalogue, exclusions, warnings, needs, adjacency, evidence basis with in-page anchors to the persistent passport cards); UNAVAILABLE / PARTIAL / empty states explicit; keyboard traversal, WCAG 2.1 A/AA (axe), RTL, registry component types, named-export modules ≤199 lines, tokens-only logical CSS. Eight new ES modules under `static/modules/screening/`.
- KL-34 closed: Core 07 §7.6 step 8 — an admitted deep case with no fired candidate signal yields `NO_CANDIDATE` with a null formal state and reason `NO_TRIGGER_FIRED` (HTTP 200); other unmatched residuals still raise; fixture proof; dossier never prints `None`/`null`.
- UX-01 satisfied: `ui_strings` 1.2.0 and `decision_narratives` 1.2.0 (additive; EN templates byte-equal to engine prose) label every rule title, result, effect, disposition, indication, queue, reason and need code in Arabic; two-part Playwright parity predicate with the 11-class technical grammar (`browser_tests/parity_grammar.py`) and `label_leaks` check — `label_leaks == []` on every measured container; `docs/implementation/UX_GENUI_DEMO_SPEC.md` §8 amended.
- Visual oracle: 56 entries regenerated once in the canonical container; 24 of 40 pre-existing entries drift only in the sidebar item and the version string; 16 dossier entries byte-identical; SC-5 capture-stability correction (settled navigation scroll before capture) recorded; `FROZEN_TREE_OIDS['browser_tests/baselines'] = c2b3b66b…`, `VISUAL_BASELINE_ENTRIES = 56`.
- A-04-residual closed (CLI latest snapshot by `(as_of_date, snapshot_id)`); TL-09 extended to the four screening routes and the DOM; Core 01 §12 FR-084…FR-087; ADR-020; KL-84…KL-89; one manifest run.

## Review and evidence

- Plan-1 + AM-1 + AM-2: planner-fable; reviewer-grok REJECT (passport journey unsatisfiable) → REJECT (oracle inconsistency after OD-12) → APPROVE; owner rulings OD-1…OD-14.
- Implementation: `implementer-sol` slot 1 (OD-10); owner-lead WIP commits `d1d1462` (OD-4/OD-15) and `f9fec2d` (OD-16); reviewer-grok implementation APPROVE zero findings on `8fb01e4d…` with independent visual inspection, live Arabic parity probe and both-locale journey walks; confirmation round APPROVE on `85b34dfa…` (state.json-only delta).
- Local: owner `make ci` exit 0 (2275 tests; 152 functional + 4 visual); pre-push portability gate PASS. Hosted: run `34720051770` 5/5 on the exact head. Post-merge local `main`: `INTEGRITY PASS`, 2275 tests, `SMOKE PASS`, four reconstruction passes.
- Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`; simulated outcomes unchanged.

## Carried forward

- KL-85: routed multi-surface shell (UX-02) deferred to a later frontend slice (S18/S21 planning must carry it).
- KL-89: parity-grammar residual (ALL-CAPS/snake_case tokens admitted by construction) mitigated by `label_leaks`; rendered Arabic surfaces stay under reviewer inspection each slice.
- Passport `access classification` and `terms observation` are not on the passport payload (registry not imported at runtime).
- Partner detail remains UNAVAILABLE (KL-40; Comtrade all-partners token behind the developer-portal sign-in wall).
- Next: S14 deep cases A (coated steel, fabricated aluminium, technical plastics; ≥5 cases; route-matrix rows) planned with the S14/S15 pre-planning rulings PR-1…PR-7, the official-source discovery ledger and the product-family HS4 proposal (authority change through the S14 plan and reviewer gate).
