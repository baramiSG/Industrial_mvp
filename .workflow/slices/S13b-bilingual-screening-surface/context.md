# Context — S13b Bilingual Screening Surface

## Position in the milestone

- Second and last child of the S13 split (`decomposition-1.json`, `93ba2443…`), owner-accepted. s13a is MERGED (PR #21 `834ba60`; records PR #22 `ab4add6`). Parent S13 completes when s13b merges.
- Branch `slice/s13b-bilingual-screening-surface` created from `main` at `ab4add6` on 2026-09-12.

## Inputs consumed from s13a (byte-identical; consumed, not altered)

- `/api/screening` router (`src/ior_mvp/screening/api.py`: summary, `queues/{queue_id}`, `records/{hs6}`), repository loaders (`repository.py`, latest snapshot by `as_of_date` then id), governed `config/screening.v1.yaml` and `config/product_families.v1.yaml`.
- Real sharded snapshot `data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/` — 5,443 records; dispositions 4,996 CANDIDATE / 447 NO_CANDIDATE / 0 SCREENED_OUT; queues 119 / 0 / 0 / 4,727 / 15 (two queues empty — real empty-queue states to render); 135 persistence-only unqueued; universe AVAILABLE; partner detail 0 / 1,471 UNAVAILABLE (`PARTNER_DETAIL_NOT_ACQUIRED`); tariff tree UNAVAILABLE; §8.2(c) greenfield `NOT_CALCULABLE` (`D_STAR_NOT_ASSIGNED_AT_SCREENING`).
- Residual advisory carried in: A-04-residual (CLI `_latest_snapshot` ordering).

## Frontend state at base

- Shell `src/ior_mvp/static/{index.html,app.js,styles.css}`, modules under `static/modules/` (api, dom, events, extraction, formatters, i18n, methodology, portfolio, state, workspace) and `modules/renderers/` (capability, decision, economics, evidence, index, integrity, rules, trade); GenUI registry in `src/ior_mvp/genui.py` (ten approved component types).
- Catalogues: `config/ui_strings.v1.yaml` (433 lines), `config/decision_narratives.v1.yaml` (307 lines) — both authority-hashed.
- Browser suite: 118 functional + 4 visual nodes; visual matrix `browser_tests/visual_baselines.py` `SCREENS` (10 screens × 2 viewports × 2 locales), baselines under `browser_tests/baselines/v0.3.0/{en,ar}` pinned by `FROZEN_TREE_OIDS['browser_tests/baselines']` and the visual manifest `source_tree` (hashes every `src/ior_mvp/*.py`, `index.html`, `app.js`, `styles.css`, modules).
- UX baseline observations: UX-01 (Arabic mode leaves rule titles, evidence-effect and decision-boundary text in English — content-parity gap, now an acceptance criterion), UX-02 (long single page; not in scope unless the plan justifies it).
- `docs/implementation/UX_GENUI_DEMO_SPEC.md` §8 still states engine-emitted narrative remains English in this release — superseded by the owner's UX-01 directive; the spec must be amended in this slice.

## Environment

- Docker daemon reachable from the `Ubuntu` WSL distro after owner-authorized configuration change OR-6 (default-distro WSL integration enabled; Docker Desktop restarted; other workload preserved). Canonical image `ior-visual-baselines:playwright-1.62.0-noble` present locally.
- Python 3.12 `.venv` (uv, offline); Python 3.14.6 available via `uv python find` for interpreter checks only.

## Governance

- Authority files this slice may change (Manifest §7.3/§7.4, one `build_manifests.py` run): Core 01/03/07/09, `config/ui_strings.v1.yaml`, `config/decision_narratives.v1.yaml`, possibly `config/screening.v1.yaml` (a new KL-34 reason code — to be justified by the plan). `data/**` byte-identical.
- Frozen goldens: steel public `INVESTIGATE`, polypropylene public `REJECT` — unchanged.
- Standing gates added after s13a: pre-push portability copy check; TL-09 synthetic-leakage extended to screening views.
