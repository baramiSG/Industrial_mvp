# Context — S14 Deep Demonstration Cases A

## Position

- S13 is COMPLETE (s13a #21 `834ba60`, s13b #23 `cdf6ab0`; records #22/#24). `main` at planning time: `ab6211f86307ad95a0e61f0597664023f09b7177`.
- S14 depends on S10 (simulation routes 0–7 and the route-8 contract), S12 (acquisition framework, document store, entity ids) and S13 (screening queues) — all merged.

## Inputs available on main

- Frozen screening snapshot `SCREENING-SAU-2026-09-12-9b6b22032fd8` (5,443 records; queues 119/0/0/4,727/15; all 43 family HS6 lines sit only in `likely_false_positive` because 4,542/5,443 records carry the universe-wide H5→H6 continuity flag — the planner verified this, which is why the literal PR-7 rule was empty and the selection rule S14-CS-1 extends to warning-class tiers).
- Universe snapshot `UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12` (34,955 rows; 5,443 HS6; H5 2021, H6 2022–2024). Partner detail UNAVAILABLE from Comtrade (token behind the developer-portal wall); the S11 WITS partner snapshot (2026-09-03) covers two lines only.
- S12b document store: twelve records (six SASO, six UNICOIL incl. the "Hot Dip GL" EPD); S12c entity artifact (five companies, two UNICOIL plants).
- Discovery ledger `.autonomous-workflow/evidence/s14-s15-source-discovery.md` (46 candidate official documents; statuses; robots/terms) and the HS4 proposal `.autonomous-workflow/drafts/product-families-proposal.md`; owner pre-rulings PR-1…PR-7 (`20260912-s14-s15-preplanning-rulings.md`).

## Couplings that shaped the split (verified by the planner in code)

1. `data_repository` globs the portfolio roots and the simulated portfolio 404s if any public snapshot lacks a scenario — snapshot and scenario must land together (s14b).
2. `FROZEN_TREE_OIDS` pins `data/snapshots/public`, `data/synthetic`, `data/golden`, `browser_tests/baselines` — any added case moves two OIDs (owner-lead WIP protocol, once, in s14b).
3. The visual matrix contains the two portfolio screens and `harness.CASES` asserts two cards — one canonical regeneration per portfolio change (s14b).
4. The screening snapshot pins the sha256 of `product_families.v1.yaml` and `acquisition_sources.v1.yaml`; `reconstruct_snapshot.py --all` checks inputs → the §7.3 change needs the `config/history/` retention rule with content-hash resolution (OD-4, s14a).

## Owner rulings for plan-1-s14a

OD-1…OD-10 in `.autonomous-workflow/owner-decisions/20260913-s14-plan-1-rulings.md`; OD-3 extends `technical_plastics` with 3917/3920/3921 (Manifest §10 reading from the methodology's profile row) — amendment AM-1 re-runs the selection.

## Environment

Docker daemon reachable from `Ubuntu` (OR-6); canonical visual image present (needed in s14b). Python 3.12 `.venv` offline; acquisition windows run only with `IOR_ACQUISITION_LIVE=1` inside recorded operator windows.
