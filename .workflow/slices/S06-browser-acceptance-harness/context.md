# Context — S06 Real-Browser Acceptance Harness

## Base and branch
- Base: `main` at `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc` (M3-P0 squash merge; default-branch CI run 33593703368 success). Branch: `slice/S06-browser-acceptance-harness`.
- State: v0.2.0 engine and UI unchanged since tag `v0.2.0` (`ce5786b`); 280 tests; gates = prohibited → threshold → compile → node → integrity → Gate B → pytest → smoke; CI jobs: `uv / Python 3.12`, `uv / Python 3.14`, `pip / Python 3.12`, `Docker image build`.

## Governing decisions for this slice
- `SLICE_GRAPH.md` S06 (approved with amendments, ADR-010). Owner ruling R-4: S06 establishes real-browser functional, accessibility, network-failure and console-error gates, keyboard traversal and **reference screenshots of the v0.2.0 baseline**; the governed visual-regression baselines are established in S07 after the redesign. S06 must not introduce a visual-regression pass/fail oracle.
- No authority change: no `config/*.yaml`, `data/**`, `docs/core/**`, DOCX, golden or hash edit. Core 09 §2.7 already designates Playwright as the production addition; KL-22 closes; TL-07 and Gate G scope statements are updated in `docs/REQUIREMENTS_TRACEABILITY.md`.
- UI edits are permitted only for defects the browser gate reveals (e.g., a control with no visible focus style, an axe violation, an overflow at a tested width, a console error). Each edit is recorded with before/after evidence. No redesign, no i18n, no Executive Mode.

## Observed v0.2.0 interface facts (Supervisor read, 2026-09-02)
- `index.html`: `lang="en"`; sidebar nav — five `.nav-item` buttons (`data-target` overview/workspace/methodology/extraction/governance); topbar `.mode-control` with two `.mode-button` (`data-mode` public/simulated); `/docs` API link (`target="_blank"`); hero buttons `#open-first-case`, `#view-methodology`; portfolio `#kpi-grid`, `#opportunity-grid` (cards with `[data-open-id]` buttons); workspace `<select id="opportunity-select">`; `#workspace-manifest` region; `#methodology-summary`; `#extraction-grid` with `dir="rtl"` blocks; governance cards; `#toast` `role="status"`.
- `app.js` (464 lines): `setMode` reloads the portfolio and keeps `selectedId` when still present; `loadOpportunity` fetches analysis + ui-manifest; renderers for the ten approved components; `bindWorkspaceActions` — `[data-dossier-html]` opens `/api/opportunities/{id}/dossier.html?mode=` via `window.open(..., "_blank", "noopener")`; `[data-copy-json]` fetches the dossier JSON and writes to `navigator.clipboard`, then toasts; `handleError` calls `console.error` and toasts.
- `styles.css` (335 lines): media queries at 1180 px, 900 px, 560 px; 71 lines with hex literals outside `:root` (KL-21, S07 scope). Focus styling must be inspected in the browser (UX spec §10 says focus is "inherited from browser controls").
- Dossier HTML (`dossier.py`): one `dir="rtl"` paragraph; `@media print` rule; inline CSS.
- API: `/api/health`, `/api/project`, `/api/thresholds`, `/api/opportunities?mode=`, `/api/opportunities/{id}?mode=`, `/ui-manifest`, `/dossier`, `/dossier.html`, `/api/extraction-demo`; SPA fallback confined to `static/`.
- Existing frontend tests (`tests/test_static_frontend.py`) are static source/CSS checks; no browser automation exists anywhere in `tests/`.

## Environment facts (verified 2026-09-02)
- Local: node 22.22.3, npm 10.9.8, uv 0.11.31, Python 3.14.4 in `.venv`, Docker 29.7.2. Playwright Chromium binaries are already cached under `~/.cache/ms-playwright` (`chromium-1234`, `chromium_headless_shell-1234`) but no Python Playwright package is installed in the project environment.
- CI runners: `ubuntu-latest`; `playwright install --with-deps chromium` (or the Node equivalent) is the standard browser install step; an Arabic-capable font (e.g., `fonts-noto-core` via apt) may be required for a truthful RTL glyph check.
- Ports: 8000 is the demo default; e2e must bind `127.0.0.1` on an ephemeral or clearly distinct port and wait on `/api/health` rather than sleeping.

## Constraints
- `PYTHONPATH=src pytest -q` must still pass on a machine without browsers (e2e deselected by default via marker/config); the browser suite runs through an explicit command (`make e2e`) and a dedicated CI job.
- Test tooling must be offline at run time (no CDN); every new dependency is pinned (`uv.lock` re-locked if Python deps change; `package.json` + lockfile if Node deps are used) with licences recorded (axe-core is MPL-2.0).
- Reference screenshots: stored as documentary evidence with an index under the slice record (or a documented `tests/e2e/reference/` folder), total size kept small; they are not compared in any test.
- No `.env` read; no secret value printed; no live external source called.
- Execution conventions: the implementer runs commands directly and records exact commands and outputs in `test_evidence.md`; the Supervisor controls commit, push, PR and merge.

## Records to produce in this slice folder
`plan.md`, `plan_review.md`, `implementation_log.md`, `implementation_review.md`, `reviewer_findings.md`, `test_evidence.md`, `pr_record.md`, `completion.md` (plus the reference-screenshot index).
