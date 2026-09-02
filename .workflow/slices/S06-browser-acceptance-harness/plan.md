# S06 Real-Browser Acceptance Harness (Chromium) — Implementation Plan

> **For the governed Implementer:** execute this plan only after the Supervisor records `PLAN_APPROVED`. Use test-first changes, stop with all work uncommitted, and hand the exact candidate to the Supervisor. Do not stage, commit, push, open a PR, merge, tag, or approve your own work.

**Goal:** Add one deterministic local command and one independent hosted CI job that exercise the existing v0.2.0 decision workspace in real headless Chromium, fail closed on browser/accessibility/network defects, validate dossier print/PDF output, and retain compact reference screenshots as documentary—not visual-regression—evidence.

**Architecture:** Use pinned Python Playwright and `pytest-playwright` inside the existing uv development extra. Keep real-browser tests in top-level `browser_tests/`, outside the existing default `testpaths = ["tests"]`; a session fixture launches the FastAPI application on a kernel-assigned localhost socket, function-scoped contexts enforce failure hooks, and focused helpers cover accessibility, RTL glyphs, PDF structure, and documentary capture. The browser job runs independently of the three existing Python checks and Docker check.

**Tech stack:** Python 3.12 for the hosted browser job; Python 3.12/3.14 for existing uv dependency compatibility; `playwright==1.62.0`; `pytest-playwright==0.9.0`; Chromium supplied by that Playwright release; vendored `axe-core@4.13.0`; pytest; uv; FastAPI/uvicorn; GitHub Actions.

**Data classification:** `confidential_demo` — frozen public evidence and explicitly labelled Class-D synthetic scenarios only. No `.env` content, credentials, Ministry data, or live industrial source is permitted.

**Plan status:** Planner artifact only. It is not approval, implementation, test evidence, or delivery authorization.

---

## 1. Objective

- [SPECIFIED] The S06 outcome is a real-Chromium acceptance layer for the existing analyst workspace, not a new product surface (`docs/milestones/v0.3.0/SLICE_GRAPH.md:39-47`; slice `context.md:5-9`).
- [SPECIFIED] One documented command must start a localhost application on an ephemeral port, wait for `/api/health`, execute the suite, and stop the process; `make ci` must include this gate (user-approved S06 scope).
- [SPECIFIED] The suite covers both evidence modes, both cases, every existing selector path, dossier popup and clipboard actions, desktop/tablet/presentation widths, keyboard/focus, WCAG 2.1 AA, RTL glyph rendering, print media, and Chromium PDF bytes (user-approved S06 scope; Core 01 §5 and §7).
- [SPECIFIED] Every ordinary journey fails on console errors, uncaught page errors, failed requests, app-origin HTTP responses at status 400 or higher, prohibited external HTTP(S) requests, inaccessible controls, or unmet state assertions (owner area A5; `GAP_ANALYSIS.md:69-76`).
- [SPECIFIED] S06 reference screenshots document the v0.2.0 baseline only. No screenshot is compared, approved as a visual baseline, or used as a pass/fail oracle; governed visual baselines begin in S07 (ADR-010 R-4, `ARCHITECTURE_DECISIONS.md:80-84`; `SLICE_GRAPH.md:43`).
- [SPECIFIED] Existing UI files may change only after a browser test exposes a real defect, and every such edit requires recorded before/after evidence. No pre-emptive redesign is allowed (`context.md:10-12`).
- [DERIVED] The clean boundary is therefore: browser harness/tooling/CI/documentation are planned changes; frontend or dossier-renderer changes are conditional defect remediation only.

## 2. Governing requirements and authority

| Requirement | Binding meaning for S06 | Sanad |
|---|---|---|
| V3-A1 | Real Chromium Playwright end-to-end tests exist and run in a dedicated gate. | [SPECIFIED] `GAP_ANALYSIS.md:70` |
| V3-A2 | Exercise both card buttons, both `<select>` case values, the steel hero button, both mode directions, dossier popup, clipboard copy, and existing navigation. Graph/drill-down/reset controls do not exist and are excluded. | [SPECIFIED] `GAP_ANALYSIS.md:71`; `index.html:23-29,44-48,61-63,96-98`; user-approved scope |
| V3-A3 | Exercise 1440×900, 1024×768, 1920×1080, and 2560×1440; no page-level horizontal overflow; mode, selector, and dossier controls remain actionable. | [SPECIFIED] user-approved scope; `UX_GENUI_DEMO_SPEC.md:105-111` |
| V3-A4 | Real Tab traversal and focus visibility, Arabic RTL/non-tofu rendering, print CSS, and valid Chromium-generated PDFs. | [SPECIFIED] `GAP_ANALYSIS.md:73`; Core 01 NFR-006/NFR-007 |
| V3-A5 | CI fails on browser console/page errors, failed requests, app HTTP errors, external calls, inaccessible controls, and axe violations. | [SPECIFIED] `GAP_ANALYSIS.md:74`; user-approved scope |
| V3-A6 | Capture all principal journey states at every required width as compact reference evidence, never a comparison oracle. | [SPECIFIED] `GAP_ANALYSIS.md:75`; ADR-010 R-4 |
| NFR-004 | Runtime remains offline and requires no key or live source. | [SPECIFIED] Core 01 `01_PRODUCT_AND_REQUIREMENTS.md:217-222` |
| NFR-006 | Controls are semantic, high-contrast, and keyboard reachable. | [SPECIFIED] Core 01 `01_PRODUCT_AND_REQUIREMENTS.md:219-222`; UX spec §10 |
| NFR-007 | Arabic source text and product names render RTL without corruption. | [SPECIFIED] Core 01 `01_PRODUCT_AND_REQUIREMENTS.md:219-222`; UX spec §8 |
| NFR-008 | Supported execution remains WSL, native Linux, and Docker; S06 must not regress existing Docker behavior. | [SPECIFIED] Core 01 `01_PRODUCT_AND_REQUIREMENTS.md:219-223`; ADR-004 |
| Core 09 §2.7 / TL-07 | Static frontend contracts remain, and the named production Playwright addition is now implemented. | [SPECIFIED] `09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:124-135` |
| Core 09 Gate G | Case selection, mode toggle, adaptive manifest, dossier open/print, and Arabic rendering become browser-observed. | [SPECIFIED] `09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:219-226` |
| Core 09 §7 / DOD-08/09 | Desktop/tablet usability and printable dossier claims gain real-browser proof without changing the core text. | [SPECIFIED] `09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:239-251` |
| KL-22 | The lack of real-browser proof closes only after approved implementation, review, local gates, PR CI, and merge evidence exist. | [SPECIFIED] `KNOWN_LIMITATIONS.md:30` and governed delivery flow |
| R-4 | References now; governed visual-regression baselines in S07. | [SPECIFIED] `GAP_ANALYSIS.md:218-220`; ADR-010 |
| ADR-004 | Python dependencies and execution remain uv-locked while the documented pip path remains installable. | [SPECIFIED] `ARCHITECTURE_DECISIONS.md:29-34` |
| ADR-007 | The Supervisor treats every hosted job as mandatory green; browser becomes an additional required check. | [SPECIFIED] `ARCHITECTURE_DECISIONS.md:50-55` |
| ADR-010 | S06 is an implementation-preserving test/tooling slice; no Core/config/data/golden authority change is authorized. | [SPECIFIED] `ARCHITECTURE_DECISIONS.md:80-84`; slice `context.md:8-10` |

- [SPECIFIED] Files under `config/*.yaml`, `data/**`, `docs/core/**`, the methodology DOCX, hashes, and golden expectations are prohibited in this slice (`AGENTS.md:60-63`; `context.md:8-10`).
- [SPECIFIED] The public steel outcome remains `INVESTIGATE`; polypropylene remains `REJECT`; synthetic evidence cannot change `real_decision` (`AGENTS.md:24-36`).
- [DERIVED] No manifest regeneration is needed or allowed because no governed bytes are in the planned file set.

## 3. Existing-state assessment

### 3.1 Repository and environment

- [VERIFIED] Read-only Git inspection returned branch `slice/S06-browser-acceptance-harness` at exact HEAD `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`, matching `context.md:3`.
- [VERIFIED] Pre-existing untracked paths are `.workflow/runs/demo_start.sh`, `.workflow/runs/s05_release_merge_tag.sh`, this slice's `context.md`, and this slice's `persona.md`. The two helper scripts must never be staged. The planner did not alter any of them.
- [VERIFIED] Tool versions observed read-only: Node `v22.22.3`, npm `10.9.8`, uv `0.11.31`, and Python `3.14.4`.
- [VERIFIED] `~/.cache/ms-playwright` contains `chromium-1234`, `chromium_headless_shell-1234`, and `ffmpeg-1011`; this cache does not prove compatibility with the proposed Playwright pin.
- [VERIFIED] `.venv/bin/python -c "import playwright"` failed with `ModuleNotFoundError`; no Python Playwright package is currently installed.
- [VERIFIED] `.env` exists, is ignored by `.gitignore:7`, and has no tracked entry. Its content was not opened or printed.
- [VERIFIED] The project has no `docs/project/` directory. The slice-specific authority is the repository's manifest/core/control/milestone corpus named in this plan.

### 3.2 Browser-facing implementation

- [VERIFIED] `index.html:23-29` defines five native navigation buttons; `index.html:44-48` defines the two mode buttons; `index.html:61-63` defines the steel and methodology hero actions; `index.html:96-98` provides a labelled native opportunity `<select>`.
- [VERIFIED] Dynamic opportunity-card controls are emitted with `data-open-id` at `app.js:82-107`; both golden cases are loaded from the API.
- [VERIFIED] `setMode()` reloads the portfolio while retaining `selectedId` when it remains present (`app.js:40-58`).
- [VERIFIED] The selected case drives both analysis and manifest requests (`app.js:119-130`).
- [VERIFIED] The dynamic dossier and clipboard buttons are emitted at `app.js:363-373`; their event handlers open a new window and write fetched dossier JSON to the Clipboard API at `app.js:376-390`.
- [VERIFIED] `handleError()` writes failures to `console.error` (`app.js:453-456`), making a console-error gate meaningful.
- [VERIFIED] The current CSS has responsive rules at 1180, 900, and 560 pixels (`styles.css:296-335`) but no `:focus`, `:focus-visible`, or `outline` rule (read-only content search returned no matches). Chromium's native focus treatment is therefore the initial behavior under test.
- [VERIFIED] The main dossier renderer has one Arabic `dir="rtl"` product paragraph and an `@media print` rule (`dossier.py:129-163`).
- [VERIFIED] FastAPI serves `/api/health`, list/detail/manifest/dossier/dossier HTML/extraction routes and the static SPA (`app.py:56-141`).

### 3.3 Existing proof and toolchain

- [VERIFIED] `tests/test_static_frontend.py:8-198` performs source/CSS contracts only; no browser package or browser test exists under current `tests/`.
- [VERIFIED] `pyproject.toml:17-22` currently has only pytest and httpx in `dev`; `pyproject.toml:34-37` limits default discovery to `tests`.
- [VERIFIED] `.github/workflows/ci.yml:19-102` defines `uv-gates` (3.12/3.14 matrix), `pip-gates` (3.12), and `docker-build`; no browser job exists.
- [VERIFIED] `Makefile:32-40` runs the eight existing local gates and has no `e2e` target.
- [VERIFIED] `tests/test_ci_contract.py:49-218` locks the three current job keys and forbids optional failure escapes; it must be extended without weakening legacy-job assertions.
- [VERIFIED] `tests/test_packaging.py:11-75` tests tracked-only packaging and does not hard-code the CI or Makefile shape; no change is required there.
- [VERIFIED] `scripts/final_acceptance.sh:1116,1391,1462-1464` still asserts/reports the pre-S06 “no browser” scope even though its `make ci` step will begin running the browser gate; these statements must become truthful.
- [VERIFIED] `uv.lock:169-192` contains the editable root and only the current two-entry `dev` extra; dependency locking must add a separate `e2e` extra to the root stanza and its transitive package records while leaving `dev` unchanged.
- [DERIVED] The required S06 changes are additive: no decision engine, route selection, evidence data, or GenUI manifest semantics need modification.

## 4. Relevant existing code and reuse points

| Existing item | Reuse in S06 | Sanad |
|---|---|---|
| `src/ior_mvp/app.py` | Launch unchanged through uvicorn and probe `/api/health`; use real HTTP, not TestClient, in browser tests. | [DERIVED] from `app.py:56-141` |
| `src/ior_mvp/static/index.html` | Existing semantic labels/roles are the primary locators; no test IDs are initially needed. | [DERIVED] from `index.html:23-100` |
| `src/ior_mvp/static/app.js` | Existing `data-mode`, `data-open-id`, `data-dossier-html`, and `data-copy-json` attributes are stable test hooks. | [DERIVED] from `app.js:40-58,82-107,363-390` |
| `src/ior_mvp/static/styles.css` | Existing media queries are exercised; no style edit unless a test establishes a defect. | [SPECIFIED] slice scope plus `styles.css:296-335` |
| `src/ior_mvp/dossier.py` | Existing HTML and print CSS are exercised; renderer edit is conditional. | [DERIVED] from `dossier.py:129-163` |
| `tests/test_static_frontend.py` | Retain all static contracts; add defect-specific source regression only if UI remediation is required. | [SPECIFIED] anti-weakening rule |
| `tests/test_api.py` / `tests/test_dossier_contract.py` | Retain API/dossier semantics and add only a defect-specific assertion if renderer markup changes. | [SPECIFIED] scope control |
| `tests/test_ci_contract.py` | Extend exact job-set/legacy-invariance assertions and define the browser job contract. | [DERIVED] from existing exact assertions |
| `scripts/final_acceptance.sh` | Its existing `make ci` step carries S06 into final acceptance; only stale proof copy/audit fragments change. | [DERIVED] from `final_acceptance.sh:169-171,1520-1522` |
| `Makefile` / uv | Keep legacy `UV_RUN` unchanged, add locked `UV_RUN_E2E` for `dev` + `e2e`, and append the browser gate after smoke. | [DERIVED] from ADR-004 and `Makefile:1-40` |

- [PROPOSED] Do not add `data-testid` attributes. If a locator proves ambiguous despite role/label/existing data attributes, stop and document the exact ambiguity before adding the smallest non-visual `data-testid`; none is currently planned.
- [PROPOSED] Do not create a second server script. Keep process/socket orchestration in browser-test support code because it is acceptance infrastructure, not an operator runtime.

## 5. Tooling decision and exact proposed pins

### 5.1 Choice

- [PROPOSED] Choose Python `pytest-playwright`, not Node `@playwright/test`.
- [DERIVED] This keeps one dependency source (`pyproject.toml`), one lock (`uv.lock`), one test assertion style (pytest), and the existing uv/Python caches. A Node runner would add `package.json`, a second lock, npm cache policy, and a second test lifecycle solely for S06.
- [PROPOSED] Declare Playwright tooling only in a new `[project.optional-dependencies].e2e` extra. Preserve the existing two-entry `dev` extra exactly, so legacy uv jobs, operator setup, and the documented pip `-e ".[dev]"` path remain behaviorally byte-identical.
- [DERIVED] Top-level `browser_tests/` plus explicit pytest invocation satisfies browserless default discovery without weakening the existing suite.
- [DERIVED] Python fixtures can start the existing uvicorn application with a pre-bound localhost socket and use the existing Python domain/toolchain directly.

### 5.2 New versions

| Component | Exact proposed version | Licence | Verification rule |
|---|---:|---|---|
| `playwright` | `1.62.0` | Apache-2.0 | [PROPOSED] Add exact `==`; Implementer confirms the release exists and lock resolves on Python 3.12/3.14. PyPI/release metadata was read by the Planner. |
| `pytest-playwright` | `0.9.0` | Apache-2.0 | [PROPOSED] Add exact `==`; Implementer confirms index availability and records the resolved lock entry. PyPI metadata was read by the Planner. |
| `axe-core` | `4.13.0` | MPL-2.0 | [PROPOSED] Vendor `axe.min.js` and upstream licence from the exact npm tarball; record tarball SRI and local SHA-256. npm registry metadata was read by the Planner. |
| `actions/cache` | `v6.1.0` | action dependency | [PROPOSED] Use the exact release tag in the new job; Implementer verifies it resolves. |
| `actions/upload-artifact` | `v7.0.1` | action dependency | [PROPOSED] Use the exact release tag in the new job; Implementer verifies it resolves. |

- [VERIFIED] Playwright 1.62.0 metadata reports Python `>=3.10` and Apache-2.0; pytest-playwright 0.9.0 reports Python `>=3.10`, Playwright `>=1.18`, pytest `<10`, and Apache-2.0.
- [VERIFIED] npm registry metadata for axe-core 4.13.0 reports MPL-2.0 and tarball integrity `sha512-UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A==`.
- [PROPOSED] `fonts-noto-core` is an OS test prerequisite, not a Python/JS dependency. Pin the runner OS to `ubuntu-24.04`, install the package by name, record its actual `dpkg-query` version and `fc-match` result in `test_evidence.md`, and let the glyph test fail if coverage changes.
- [VERIFIED] Ubuntu package metadata lists `NotoSansArabic-Regular.ttf` and `NotoSansArabic-Bold.ttf` in `fonts-noto-core`.
- [PROPOSED] No `package.json`, `node_modules`, npm runtime install, CDN script, accessibility wrapper plugin, retry plugin, or PDF parser is added.
- [PROPOSED] If any exact proposed dependency/action version is unavailable or incompatible when the Implementer resolves it, stop and report the exact resolver evidence to the Supervisor. Do not silently substitute a different version.

## 6. Complete file plan

### 6.1 Create

| Path | Responsibility |
|---|---|
| `scripts/check_browser_prerequisites.py` | Fail-fast check for exact package versions, Chromium executable, axe asset/hash/licence, and Arabic fontconfig coverage; never reads environment values beyond safe paths/flags. |
| `tests/test_browser_harness_contract.py` | Browserless unit/static contracts for preflight behavior, vendor integrity/licences, default discovery separation, non-oracle screenshot policy, and helper failure classification. |
| `browser_tests/conftest.py` | Registered e2e marker, explicit-vs-direct missing-browser behavior, app-server fixture, viewport/context/page factories, failure-hook fixture, artifact roots. |
| `browser_tests/harness.py` | Typed case/viewport definitions, pre-bound uvicorn process, health readiness, browser failure collector, axe loader/result formatting, PDF and Arabic-glyph helpers, reference index writer. |
| `browser_tests/pages.py` | Small role/label/data-attribute page helpers and state-based readiness/selection functions. |
| `browser_tests/test_journeys.py` | Portfolio, card/select/hero, mode-preservation, navigation tests. |
| `browser_tests/test_dossier.py` | Popup, clipboard, print-media, and PDF tests. |
| `browser_tests/test_accessibility.py` | Tab/focus, workspace/dossier axe, workspace/dossier RTL glyph tests. |
| `browser_tests/test_responsive.py` | Required viewport matrix, overflow, and primary-control actionability. |
| `browser_tests/test_guardrails.py` | Isolated self-test proving all four failure channels are observed. |
| `browser_tests/test_reference_screenshots.py` | Four viewport nodes; each captures the ten named principal states and writes documentary metadata. |
| `browser_tests/THIRD_PARTY_NOTICES.md` | Exact component/version/source/licence record for Playwright, pytest-playwright, and axe-core. |
| `browser_tests/vendor/axe-core-4.13.0/axe.min.js` | Offline axe injection source; never fetched at test runtime. |
| `browser_tests/vendor/axe-core-4.13.0/LICENSE` | Verbatim upstream MPL-2.0 licence. |
| `browser_tests/vendor/axe-core-4.13.0/SOURCE.json` | Version, npm tarball URL, registry SRI, local asset SHA-256, acquisition date, and “unmodified vendored distribution” statement. |
| `.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0/index.md` | Human-readable non-oracle warning, capture provenance, browser/font/tool versions, file hashes/bytes, and 40-entry journey matrix. |
| `.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0/*.webp` | 40 compact viewport-scoped documentary captures: ten principal states × four widths. |
| `.workflow/slices/S06-browser-acceptance-harness/implementation_log.md` | Implementer-authored execution/defect/dependency record defined in §23. |
| `.workflow/slices/S06-browser-acceptance-harness/test_evidence.md` | Implementer-authored fresh command/output evidence defined in §23. |

### 6.2 Modify unconditionally

| Path | Exact purpose |
|---|---|
| `pyproject.toml` | Add a separate exact-pinned `e2e` optional extra; keep `dev` exactly two entries; register the `e2e` marker; preserve `testpaths = ["tests"]`. |
| `uv.lock` | Resolver-generated exact dependency graph; never hand-edit. |
| `Makefile` | Add `e2e`; append the same preflight/browser command to `ci`. |
| `.github/workflows/ci.yml` | Add independent `browser-gates` job only; preserve existing job behavior. |
| `.gitignore` | Ignore runtime browser artifacts, reports, and optional Node artifact directory. |
| `tests/test_ci_contract.py` | Preserve legacy assertions; add exact browser job/cache/font/install/artifact assertions and allow only the named failure-upload condition. |
| `tests/test_final_acceptance_contract.py` | Require truthful S06 browser wording and exact vendored-asset keyword disposition while retaining the 42-step order and all anti-escape assertions. |
| `scripts/final_acceptance.sh` | Update stale docs-audit/result/limitation wording and explicitly classify only the SHA-verified axe file as vendored third-party content; `make_ci` remains the mechanism that runs e2e. |
| `docs/DEVELOPMENT_GUIDE.md` | Browser prerequisites, install, one-command gate, artifacts, default exclusion, troubleshooting. |
| `docs/OPERATOR_RUNBOOK.md` | Operator command, prerequisites, expected failure handling, reference evidence location. |
| `docs/KNOWN_LIMITATIONS.md` | Move KL-22 to an S06 closure record without inventing PR/CI/merge facts. |
| `docs/REQUIREMENTS_TRACEABILITY.md` | Replace the old proof-scope paragraph; update TL-07/Gate G/NFR-006/NFR-007/DOD-08/DOD-09; add V3-A1…V3-A6. |
| `docs/ARCHITECTURE_DECISIONS.md` | Amend ADR-007 operational check list to include the S06 browser job while preserving the procedural gate decision. |
| `CHANGELOG.md` | Add an `Unreleased` S06 entry; do not assign a release date/version. |

### 6.3 Modify only after an observed defect

| Conditional path | Permitted reason | Required paired test |
|---|---|---|
| `src/ior_mvp/static/index.html` | Missing/incorrect accessible name, role, language/direction markup, or structural overflow source. | Failing browser test plus focused static regression in `tests/test_static_frontend.py`. |
| `src/ior_mvp/static/app.js` | Browser console error, inaccessible dynamic control, broken existing action, or unsafe focus behavior. | Failing browser test plus focused static/API contract where practical. |
| `src/ior_mvp/static/styles.css` | Focus is not visibly distinct, contrast violation, or required-width page overflow. | Failing browser/axe test plus focused static contrast/style contract. New values must be design tokens. |
| `src/ior_mvp/dossier.py` | Dossier axe/RTL/print defect. | Failing browser test plus focused `tests/test_dossier_contract.py` assertion. |

### 6.4 Explicitly unchanged

- [SPECIFIED] No `config/**`, `data/**`, `docs/core/**`, methodology DOCX, authority/snapshot manifest, golden expectation, decision-engine, capability, economics, evidence, or GenUI semantic change.
- [DERIVED] `tests/test_packaging.py`, `Dockerfile`, `docker-compose.yml`, `START_DEMO_WSL.sh`, and `scripts/run_demo.sh` require no edit; their behavior is exercised in regression.
- [SPECIFIED] Do not modify `persona.md`, `context.md`, the two untracked `.workflow/runs/*.sh` helper scripts, prior slice records, or `.workflow/state.json` as Implementer.

## 7. Harness architecture

### 7.1 App server fixture

- [PROPOSED] `app_server` is session-scoped and returns a typed immutable `AppServer(base_url, process, log_path)`.
- [PROPOSED] Parent code creates an IPv4 TCP socket, binds exactly `("127.0.0.1", 0)`, calls `listen()`, marks the descriptor inheritable, and launches:

```python
command = [
    sys.executable,
    "-m",
    "uvicorn",
    "ior_mvp.app:app",
    "--fd",
    str(inherited_fd),
    "--log-level",
    "warning",
]
```

- [DERIVED] Passing the already-bound descriptor via `subprocess.Popen(..., pass_fds=(fd,))` removes the “discover free port, close it, race another process” gap and avoids fixed-port collisions on WSL/Linux.
- [SPECIFIED] Launch the uvicorn child with `sys.executable`, the interpreter running pytest inside the uv environment, never a bare `python`; pass the command above to `subprocess.Popen`.
- [PROPOSED] Pass an allow-listed child environment (`PATH`, `HOME`, `LANG=C.UTF-8`, `PYTHONPATH=<root>/src`, `PYTHONUNBUFFERED=1`) rather than the full parent environment.
- [PROPOSED] Readiness uses a bounded loop of real GET requests to `<base_url>/api/health`, each with a network timeout, until exact JSON `status == "ok"` and version `0.2.0` is observed. The loop checks `process.poll()` on every failed attempt and includes the sanitized server log on premature exit.
- [PROPOSED] No `sleep`, shell `sleep`, `time.sleep`, or fixed startup delay is allowed. The only startup wait is health-state polling.
- [PROPOSED] Teardown sends SIGTERM, waits for normal uvicorn exit, and treats forced kill/non-terminal teardown as a test failure; the listening parent descriptor is always closed.

### 7.2 Browser and context fixtures

- [PROPOSED] Use pytest-playwright's session `browser` and function `new_context` fixtures, always with `--browser chromium` and headless default.
- [PROPOSED] Every ordinary context sets:

```python
{
    "base_url": app_server.base_url,
    "locale": "en-US",
    "permissions": ["clipboard-read", "clipboard-write"],
    "reduced_motion": "reduce",
    "viewport": {"width": viewport.width, "height": viewport.height},
}
```

- [PROPOSED] Grant clipboard permissions for `app_server.base_url` before navigation and clear context permissions on teardown.
- [PROPOSED] One isolated context per collected test node prevents state/clipboard/popup leakage. No storage state is persisted.
- [PROPOSED] All ordinary pages are created only after the context-level failure collector is installed; `context.on("page", ...)` attaches the same collector to popups.

### 7.3 Console/network/page failure hooks

- [PROPOSED] `BrowserFailureCollector` records structured records with category, method/type, sanitized URL, and message for:
  1. `page.on("console")` when `message.type == "error"`;
  2. `page.on("pageerror")`;
  3. `page.on("requestfailed")`;
  4. `page.on("response")` when the URL origin equals the app origin and `status >= 400`;
  5. `page.on("request")` for any HTTP(S) origin other than the app origin.
- [PROPOSED] `data:`, `blob:`, and `about:` URLs are not external network calls. No HTTP(S) allow-list beyond the exact ephemeral app origin exists.
- [PROPOSED] The collector's fixture finalizer fails with all collected records; it does not filter message text, status, resource type, or `net::ERR_*`.
- [PROPOSED] Only `test_failure_collector_observes_all_required_channels` uses a separately constructed observation-only collector to plant one named probe per category and assert classification. Ordinary journey collectors have no ignore/exclusion API.

### 7.4 Offline axe-core injection

- [PROPOSED] Load the vendored `axe.min.js` bytes from disk, verify its SHA-256 against `SOURCE.json`, and inject with `page.add_script_tag(content=...)` after each exact page-ready condition.
- [PROPOSED] Run `axe.run(document, {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]}})`.
- [PROPOSED] Assert `violations == []` and format every violation with ID, impact, help URL, target, failure summary, and HTML excerpt on failure.
- [SPECIFIED] Do not use `disableRules`, excluded selectors, impact filtering, incomplete-result suppression, or an “accepted violation” list.
- [SPECIFIED] If a violation is genuine, first write/retain the failing browser test, record the before output, make the smallest UI fix, and record zero-violation after evidence. If it cannot truthfully be fixed in scope, stop and return it as a Supervisor finding.

### 7.5 RTL and Arabic font strategy

- [PROPOSED] CI installs `fonts-noto-core`; preflight runs `fc-match -f '%{family}|%{file}\n' ':lang=ar'`, requires a real readable font file and non-empty family, and records the resolved package/family in evidence.
- [PROPOSED] Browser assertions wait on `document.fonts.ready`, require visible `[dir="rtl"]` nodes to have computed `direction: rtl`, non-empty Arabic-range text, and non-zero bounding boxes.
- [PROPOSED] The non-tofu check renders a representative Arabic string and an equal-codepoint-count U+FFFD replacement string to canvas using the resolved Arabic font/generic fallback, then requires different measured widths and different non-empty pixel signatures. It also requires at least two distinct Arabic glyph signatures.
- [DERIVED] Fontconfig coverage + `document.fonts.ready` + direction + canvas distinction is stronger than checking markup or string presence alone and prevents a replacement-glyph false pass.
- [PROPOSED] Do not change the product font stack merely to satisfy CI. Add a font-family declaration only if the browser evidence shows the installed capable font is not selected; such a fix remains conditional UI remediation.

### 7.6 Print and PDF

- [PROPOSED] For every case/mode, open the dossier through the real “Open dossier” action, wait for exact dossier identity/state, call `page.emulate_media(media="print")`, and assert:
  - `matchMedia("print").matches is True`;
  - body background is white;
  - `.page` has `box-shadow: none`, zero margin, and no screen max-width constraint;
  - no page-level horizontal overflow.
- [PROPOSED] Call `page.pdf(format="A4", print_background=True, prefer_css_page_size=True)` in headless Chromium, save an ignored artifact, and assert:
  - bytes start with `%PDF-`;
  - bytes end with `%%EOF` after trailing whitespace removal;
  - length is at least 10,240 bytes;
  - regex `rb"/Type\s*/Page\b"` matches at least once.
- [VERIFIED] Playwright's documented `page.pdf()` returns PDF bytes and is supported only by headless Chromium; this aligns with the mandated browser.

### 7.7 Popup and clipboard

- [PROPOSED] Use `page.expect_popup()` around the dossier button click; verify popup URL path/query, title, opportunity ID, mode, decision state, RTL product name, and presence/absence of the exact synthetic warning.
- [PROPOSED] For clipboard, grant permissions before navigation, click the real action, wait for the status toast text, read `navigator.clipboard.readText()`, parse with Python `json.loads`, and assert `opportunity_id`, `mode`, expected decision state, and disclosure invariants.
- [SPECIFIED] Do not stub `window.open`, `fetch`, or `navigator.clipboard`; the test must exercise Chromium's real APIs.

### 7.8 Reference screenshot capture and index

- [PROPOSED] Store committed reference evidence under the slice record, not under a test-baseline directory:

```text
.workflow/slices/S06-browser-acceptance-harness/
└── reference-screenshots/v0.2.0/
    ├── index.md
    └── <viewport>__<journey-state>.webp
```

- [DERIVED] Slice-record placement makes the R-4 documentary status explicit and reduces the risk that a later test runner treats these files as visual oracles.
- [PROPOSED] `test_capture_documentary_reference_set` has four collected viewport nodes; each captures these ten ready states:
  1. Journey A portfolio/public;
  2. Journey A portfolio/simulated;
  3. Journey B steel/public workspace;
  4. Journey C steel/simulated workspace;
  5. Journey D polypropylene/public workspace;
  6. Journey D polypropylene/simulated workspace;
  7. Journey E steel/public dossier;
  8. Journey E steel/simulated dossier;
  9. Journey E polypropylene/public dossier;
  10. Journey E polypropylene/simulated dossier.
- [PROPOSED] Capture only the relevant portfolio section, workspace section, or dossier `.page` locator—never an arbitrarily tall full page—as WebP quality 55.
- [PROPOSED] The exact baseline command, run before any conditional UI fix, is:

```bash
E2E_REFERENCE_DIR=.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0 \
make e2e
```

- [PROPOSED] The generated index records the non-oracle warning, v0.2.0 tag/commit, S06 base SHA, hashes of `index.html`, `app.js`, `styles.css`, and `dossier.py`, Playwright/Chromium/font versions, capture command, viewport, journey, mode, case, expected states, relative path, bytes, and SHA-256.
- [PROPOSED] Enforce exactly 40 files, each at most 512 KiB and total at most 8 MiB. If over budget, reduce WebP quality while retaining all states; do not delete a required state or reduce viewport dimensions.
- [SPECIFIED] Tests never read the committed screenshots. `to_have_screenshot`, pixel-diff thresholds, golden-image comparison, and update-baseline commands are prohibited until S07.
- [PROPOSED] Ordinary runs write equivalent captures to ignored `.artifacts/e2e/reference/`; only the explicit baseline command targets the tracked slice folder.

### 7.9 Runtime artifacts

- [PROPOSED] `.artifacts/e2e/` contains server logs, Playwright retained-on-failure traces, failure screenshots, PDFs, ordinary reference captures, axe JSON on failure, and a run summary.
- [PROPOSED] Artifact names use deterministic test IDs/case/mode/viewport; no timestamps are needed for file identity inside a single run.
- [SPECIFIED] Raw artifacts remain ignored. Only sanitized evidence summaries and the bounded reference set are tracked.

## 8. Exact browser test inventory

Constants:

```text
cases = SAU-H0-721049 (steel), SAU-H0-390210 (polypropylene)
modes = public, simulated
viewports =
  desktop-1440x900
  tablet-1024x768
  presentation-1920x1080
  presentation-2560x1440
```

| # | Exact pytest function | Collected nodes | Journey / assertions | Modes | Viewports |
|---:|---|---:|---|---|---|
| 1 | `test_portfolio_loads_expected_cases_and_states` | 2 | Two cards/KPIs, IDs, real/active states, mode active, disclosure boundary. | both | 1440×900 |
| 2 | `test_opportunity_card_opens_selected_workspace` | 4 | Click each existing `[data-open-id]`; select/title/manifest/state match. | both × both cases | 1440×900 |
| 3 | `test_opportunity_select_loads_each_case` | 4 | Select each option; exact analysis/manifest requests and state render. | both × both cases | 1440×900 |
| 4 | `test_hero_opens_steel_case_preserving_mode` | 2 | Start on PP, click `#open-first-case`, steel loads and current mode remains. | both | 1440×900 |
| 5 | `test_mode_switch_preserves_selected_case` | 2 | PP remains selected for public→simulated and simulated→public; expected states update. | both directions | 1440×900 |
| 6 | `test_navigation_and_methodology_action_reach_sections` | 1 | All five nav buttons and hero methodology action reach/activate their sections. | public | 1440×900 |
| 7 | `test_open_dossier_popup_matches_case_and_mode` | 4 | Real popup, URL, title, ID, state, mode, disclosure, RTL. | both × both cases | 1440×900 |
| 8 | `test_copy_decision_json_writes_expected_clipboard_payload` | 4 | Real clipboard JSON parses; ID/mode/state/disclosure exact; toast visible. | both × both cases | 1440×900 |
| 9 | `test_dossier_print_media_and_pdf_are_valid` | 4 | Print computed styles, no overflow, PDF header/EOF/page object/size. | both × both cases | A4 from 1440×900 context |
| 10 | `test_keyboard_tab_order_reaches_every_interactive_control_with_visible_focus` | 8 | All 15 current visible controls reached exactly once before wrap; DOM order, `:focus-visible`, changed focus signature. | both | all four |
| 11 | `test_workspace_has_zero_wcag_21_aa_axe_violations` | 4 | Offline axe, exact WCAG tags, zero violations after state ready. | both × both cases | 1440×900 |
| 12 | `test_dossier_has_zero_wcag_21_aa_axe_violations` | 4 | Same zero-violation gate on each dossier state. | both × both cases | 1440×900 |
| 13 | `test_workspace_rtl_elements_render_real_arabic_glyphs` | 2 | Every visible RTL node direction/text/box; fontconfig and canvas non-tofu proof. | both | 1440×900 |
| 14 | `test_dossier_rtl_element_renders_real_arabic_glyphs` | 4 | Dossier product Arabic direction/text/box/non-tofu. | both × both cases | 1440×900 |
| 15 | `test_layout_has_no_horizontal_overflow_and_primary_controls_are_actionable` | 8 | Document/main fit; mode group, selector, dossier buttons visible, enabled, `click(trial=True)`. | both | all four |
| 16 | `test_capture_documentary_reference_set` | 4 | Ten named state assertions and ten scoped WebPs per viewport; index completeness/size. | all ten states | all four |
| 17 | `test_failure_collector_observes_all_required_channels` | 1 | Isolated named probes prove console-error, pageerror, requestfailed, app HTTP 404, and blocked external-origin request collection. | public probe | 1440×900 |

- [PROPOSED] Planned browser inventory is **17 named tests / 62 collected nodes / 40 committed reference images**.
- [DERIVED] Item 10's current interactive set is 15 controls: five navigation buttons, two mode buttons, API link, two hero buttons, two case-card buttons, opportunity select, and two dossier actions (`index.html` plus dynamic `app.js`).
- [SPECIFIED] Test #10 focuses the topbar `/docs` “API” link and proves its keyboard/focus path, but S06 deliberately never activates it because FastAPI's default Swagger UI loads assets from a public CDN; offline API-docs remediation is an S07 candidate defect.
- [PROPOSED] When later UI slices add controls, they must update the expected keyboard inventory; S06 hard-locks the v0.2.0 surface only.

## 9. Deterministic rules and stable selectors

### 9.1 State waits

- [PROPOSED] Ban `page.wait_for_timeout`, `time.sleep`, shell `sleep`, and animation-duration waits.
- [PROPOSED] Do not use `networkidle` as the readiness oracle. Wait for exact visible state:
  - two `[data-open-id]` card buttons;
  - two select options;
  - `#workspace-title` containing expected HS6;
  - manifest action buttons present;
  - expected active/real state text in the integrity banner;
  - popup `<main class="page">` with expected dossier ID/mode.
- [PROPOSED] Use Playwright auto-waiting and `expect(...)` with a common 10-second assertion timeout. Server startup uses a separate 15-second health deadline and fails earlier if the process exits.
- [PROPOSED] Mode/case changes wait on exact DOM state and, where useful, `expect_response` for the expected app-origin endpoint; no response is mocked.

### 9.2 Locator contract

| Control | Preferred locator |
|---|---|
| Mode group/buttons | `get_by_role("group", name="Evidence mode")` then named button or `[data-mode]` |
| Opportunity selector | `get_by_label("Opportunity")` |
| Case cards | `[data-open-id="SAU-H0-721049"]`, `[data-open-id="SAU-H0-390210"]` |
| Steel hero | `#open-first-case` / role name “Open the steel case” |
| Methodology hero | `#view-methodology` / role name “Inspect rule coverage” |
| Navigation | `.nav-item[data-target="<section>"]` plus named role |
| Dossier | `[data-dossier-html="<id>"]` / role name “Open dossier” |
| Clipboard | `[data-copy-json="<id>"]` / role name “Copy decision JSON” |
| Workspace state | `#workspace-title`, `.integrity-banner`, `#opportunity-select` |
| Dossier | URL plus `main.page`, `.state`, `.meta`, `[dir="rtl"]` |

- [PROPOSED] Do not locate by CSS colour, pixel position, DOM index alone, or implementation-only text that is not part of the user-visible contract.
- [SPECIFIED] The keyboard inventory locates and focuses the `/docs` “API” link but never follows it in S06; activating FastAPI's CDN-backed default Swagger UI would correctly violate the offline/external-origin gate and is carried as an OPEN S07 limitation.
- [PROPOSED] No `data-testid` additions are planned.

### 9.3 Fixed domain expectations

```text
steel/public:     real=INVESTIGATE active=INVESTIGATE
steel/simulated:  real=INVESTIGATE active=ADVANCE
PP/public:        real=REJECT      active=REJECT
PP/simulated:     real=REJECT      active=REJECT
synthetic label:  SIMULATED — NOT MINISTRY EVIDENCE
```

- [SPECIFIED] These are existing golden contracts, not newly invented browser rules (Core 09 §2.4; AGENTS non-negotiables).
- [PROPOSED] Browser assertions may verify these public/simulated states but must not duplicate threshold values or infer a product grade from unit value.

## 10. Gate failure behavior

The explicit browser gate returns nonzero on any of:

1. [PROPOSED] missing/mismatched Playwright or pytest-playwright package;
2. [PROPOSED] missing Chromium executable for the exact Playwright release;
3. [PROPOSED] missing/tampered axe asset or licence;
4. [PROPOSED] no Arabic-capable fontconfig match;
5. [PROPOSED] application bind/start/health/teardown failure;
6. [SPECIFIED] any ordinary-page console error or uncaught page error;
7. [SPECIFIED] any failed request, prohibited external HTTP(S) request, or app HTTP response ≥400;
8. [SPECIFIED] broken selector/mode/dossier/clipboard journey;
9. [SPECIFIED] keyboard omission, order break, or absent visible-focus evidence;
10. [SPECIFIED] any axe WCAG 2.1 A/AA violation;
11. [SPECIFIED] wrong RTL direction, empty/corrupt Arabic, or tofu-risk test failure;
12. [SPECIFIED] required-width overflow or non-actionable primary control;
13. [SPECIFIED] print-media mismatch or malformed/trivial/no-page PDF;
14. [SPECIFIED] incomplete/oversized/duplicate documentary screenshot set or index;
15. [SPECIFIED] any existing integrity, scenario, unit, golden, smoke, or Docker gate regression.

- [SPECIFIED] No retries, rerun plugin, xfail, expected-failure marker, `continue-on-error`, `|| true`, broad exception suppression, or axe exclusion may turn one of these into green.
- [PROPOSED] Pytest should continue collecting remaining nodes after a failure so CI artifacts include a broad defect picture; there is no automatic retry.
- [PROPOSED] The isolated failure-hook self-test intentionally plants errors only in its non-enforcing collector and must assert all planted records. It cannot be used by product journeys.

## 11. Unknown or missing-input behavior

- [PROPOSED] Normal `PYTHONPATH=src pytest -q` does not collect `browser_tests/`; it therefore neither needs nor skips a browser and remains valid on a browserless machine.
- [PROPOSED] Direct `pytest browser_tests` without `IOR_E2E_EXPLICIT=1` checks Chromium. If absent, the browser suite skips at session scope with the exact reason and the install command; this is diagnostic use, not the gate.
- [SPECIFIED] `make e2e` and `make ci` set `IOR_E2E_EXPLICIT=1`; missing Chromium/font/vendor prerequisites must fail, never skip.
- [PROPOSED] Preflight error text names only the missing component and safe remediation command:

```bash
uv run --locked --extra dev --extra e2e python -m playwright install --with-deps chromium
```

- [PROPOSED] An unavailable/incompatible proposed package pin is a Supervisor decision after resolver evidence, not permission to use an unpinned or different version.
- [SPECIFIED] A genuine axe violation that cannot be remediated inside the allowed UI scope is a recorded finding and stops handoff; it is not excluded.
- [PROPOSED] If fontconfig reports a capable font but the browser tofu test fails, record both outputs and treat it as a real NFR-007 defect/environment incompatibility.

## 12. Privacy and security implications

- [SPECIFIED] Never read `.env`; never print environment values, tokens, credentials, or unrestricted logs.
- [PROPOSED] Bind only an inherited socket on `127.0.0.1`; never `0.0.0.0`.
- [PROPOSED] The child server receives an allow-listed environment and no secret-bearing full environment dump.
- [SPECIFIED] Browser runtime permits only its exact ephemeral localhost origin; any other HTTP(S) request fails the test. Axe is injected from tracked local bytes.
- [PROPOSED] Clipboard assertions contain only the generated dossier for frozen public/Class-D demo data; no operating-system clipboard value is read before the test writes its own payload.
- [SPECIFIED] Screenshots/PDFs contain only the approved `confidential_demo` product surface and remain in the private project/sanitized CI artifacts. They must not include terminal output or local filesystem paths.
- [PROPOSED] Server/browser logs record sanitized URL path/status/type only; query values are limited to `mode=public|simulated`.
- [SPECIFIED] Run `scripts/check_prohibited_files.py` after the Supervisor stages the exact candidate because its scanner intentionally checks Git-tracked files only (`check_prohibited_files.py:108-141`).
- [SPECIFIED] The two pre-existing untracked `.workflow/runs/*.sh` helpers are outside S06 and must never enter the staging list.

## 13. Concurrency implications

- [PROPOSED] Do not add pytest-xdist or run browser nodes in parallel in S06.
- [DERIVED] A single session server plus one isolated context per test gives reproducibility without shared UI state.
- [PROPOSED] The OS assigns the listening port while the parent owns the bound descriptor, so concurrent independent pytest processes cannot select the same port.
- [PROPOSED] File names include test/case/mode/viewport; the reference writer rejects duplicates and writes the index once at session completion.
- [PROPOSED] If a future runner enables xdist, each worker must receive its own server and worker-suffixed artifact directory before parallelism is approved; this is not implemented now.
- [VERIFIED] Existing workflow-level concurrency cancels an older run for the same PR/ref (`ci.yml:12-16`); S06 does not alter that behavior.
- [PROPOSED] `browser-gates` has no `needs`; it runs independently on its own hosted runner and cannot mask or cancel a failing legacy job.

## 14. Versioning and compatibility

### 14.1 `pyproject.toml`

Use exact new pins and preserve existing ranges:

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8,<9",
  "httpx>=0.27,<1"
]
e2e = [
  "playwright==1.62.0",
  "pytest-playwright==0.9.0"
]

[tool.pytest.ini_options]
pythonpath = ["src", "."]
testpaths = ["tests"]
addopts = "-ra"
markers = [
  "e2e: real-Chromium acceptance tests; excluded from default testpaths"
]
```

- [PROPOSED] Run `uv lock` once after this intentional dependency edit; inspect the full lock diff; require a separate root `e2e` reference plus exact `playwright 1.62.0` / `pytest-playwright 0.9.0` records, and verify the root `dev` reference remains exactly its two pre-existing entries.
- [SPECIFIED] The lock resolves the new `e2e` extra across supported Python 3.12 and 3.14, but existing `uv-gates` continue syncing only the unchanged locked `dev` environment and do not install or import Playwright.
- [PROPOSED] The new browser job uses Python 3.12, where both proposed packages declare support; browser execution is not added to the existing 3.14 matrix.
- [SPECIFIED] The documented pip `-e ".[dev]"` path remains behaviorally unchanged and installs only its existing development packages; browser setup is separately documented as `uv sync --locked --extra dev --extra e2e --python "3.12"` and never implicitly installs Chromium.
- [PROPOSED] Node stays at the existing syntax-check role. No Node version pin, package manifest, npm lock, or `node_modules` is introduced.

### 14.2 `.gitignore`

Append:

```gitignore
# Real-browser acceptance runtime artifacts (tracked references live in the S06 slice record)
.artifacts/e2e/
test-results/
playwright-report/
node_modules/
```

- [DERIVED] `node_modules/` is defensive only; S06 creates none.
- [SPECIFIED] Do not ignore `.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/`.

### 14.3 Browser/font compatibility

- [PROPOSED] Pin hosted browser OS to `ubuntu-24.04`; keep WSL/native Linux as documented local targets.
- [PROPOSED] Let Playwright's exact Python package install its matching Chromium build; never use system Chrome or `channel=chrome`.
- [PROPOSED] Cache key includes OS, architecture, and `hashFiles('uv.lock')`, so a Playwright lock change cannot reuse the wrong browser revision.
- [PROPOSED] Record `playwright.__version__` via package metadata, `browser.version`, Chromium executable basename, `dpkg-query` font package version, and `fc-match` family/file in test evidence.
- [SPECIFIED] Docker image/build behavior stays unchanged; S06 does not add browser binaries to the application image.

## 15. Hosted CI changes

### 15.1 Exact new job

Append this fourth YAML job definition; do not alter the commands/strategy of `uv-gates`, `pip-gates`, or `docker-build`:

```yaml
  browser-gates:
    name: browser / Chromium / Python 3.12
    runs-on: ubuntu-24.04
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Set up uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: uv.lock
      - name: Sync locked browser-test environment
        run: uv sync --locked --extra dev --extra e2e --python "3.12"
      - name: Cache Playwright Chromium
        uses: actions/cache@v6.1.0
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ runner.arch }}-${{ hashFiles('uv.lock') }}
      - name: Install Chromium dependencies and Arabic font
        run: |
          sudo apt-get update
          sudo apt-get install --yes --no-install-recommends fonts-noto-core
          uv run --locked --extra dev --extra e2e python -m playwright install --with-deps chromium
      - name: Run real-browser acceptance gate
        run: make UV=uv e2e
      - name: Upload browser diagnostics on failure
        if: ${{ failure() }}
        uses: actions/upload-artifact@v7.0.1
        with:
          name: browser-failure-${{ github.run_id }}-${{ github.run_attempt }}
          path: .artifacts/e2e/
          include-hidden-files: true
          if-no-files-found: warn
          retention-days: 14
```

- [PROPOSED] Always run Playwright's install command. On a cache hit it validates/reuses the matching lock-keyed browser; OS dependencies and the font are still installed.
- [PROPOSED] The failure artifact includes retained traces, failure screenshots, available references, PDFs, axe output, and server log. It is diagnostic only and cannot change the failed job result.
- [PROPOSED] Fourteen-day diagnostic retention is an implementation default, not a business retention policy; documentation must identify it as CI diagnostics.
- [SPECIFIED] Workflow permissions stay `contents: read`; checkout credentials remain non-persistent.

### 15.2 Contract-test implications

- [PROPOSED] `tests/test_ci_contract.py` changes expected YAML keys to exactly:

```python
{"uv-gates", "pip-gates", "docker-build", "browser-gates"}
```

- [SPECIFIED] Keep every current assertion for the uv matrix, pip path, required gate order, threshold/scenario adjacency, Docker build, no `continue-on-error`, no job `needs`, read-only permissions, and non-persistent checkout.
- [PROPOSED] For legacy jobs, continue forbidding every `if`.
- [PROPOSED] For `browser-gates`, allow exactly one conditional step: upload diagnostics with `if == "${{ failure() }}"`; no other step/job condition is allowed.
- [PROPOSED] Assert exact Python 3.12, locked `--extra dev --extra e2e` sync, action tags, cache path/key fragments, font package, e2e-scoped `playwright install --with-deps chromium`, `make UV=uv e2e`, artifact path, and absence of optional-failure escapes.

### 15.3 Required-check consequence

- [DERIVED] GitHub renders five mandatory checks after S06: uv/Python 3.12, uv/Python 3.14, pip/Python 3.12, Docker image build, and browser/Chromium/Python 3.12.
- [SPECIFIED] ADR-007 means the Supervisor cannot merge when browser is missing, skipped, cancelled, pending, or red, even without branch protection.
- [PROPOSED] Amend ADR-007's enumerated check list/consequence to five checks; do not rewrite its accepted rationale or enforcement mechanism.

## 16. Makefile changes

Add variables and the exact target/ci tail:

```make
UV_RUN_E2E = $(UV) run --locked --extra dev --extra e2e
E2E_ARTIFACT_DIR ?= .artifacts/e2e
E2E_REFERENCE_DIR ?= $(E2E_ARTIFACT_DIR)/reference
E2E_PREFLIGHT = $(UV_RUN_E2E) python scripts/check_browser_prerequisites.py
E2E_TESTS = IOR_E2E_EXPLICIT=1 \
	IOR_E2E_ARTIFACT_DIR="$(E2E_ARTIFACT_DIR)" \
	IOR_E2E_REFERENCE_DIR="$(E2E_REFERENCE_DIR)" \
	PYTHONPATH=src $(UV_RUN_E2E) pytest -q browser_tests \
	--browser chromium \
	--tracing retain-on-failure \
	--screenshot only-on-failure \
	--output="$(E2E_ARTIFACT_DIR)/playwright"

.PHONY: install test verify run smoke package uv-sync lock e2e ci

e2e: uv-sync
	$(E2E_PREFLIGHT)
	$(E2E_TESTS)

ci: uv-sync
	$(UV_RUN) python scripts/check_prohibited_files.py
	$(UV_RUN) python scripts/check_threshold_literals.py
	$(UV_RUN) python -m compileall -q src scripts tests browser_tests
	$(NODE) --check src/ior_mvp/static/app.js
	PYTHONPATH=src $(UV_RUN) python scripts/verify_integrity.py
	PYTHONPATH=src $(UV_RUN) python scripts/validate_scenarios.py
	PYTHONPATH=src $(UV_RUN) pytest -q
	PYTHONPATH=src $(UV_RUN) python scripts/demo_smoke.py
	$(E2E_PREFLIGHT)
	$(E2E_TESTS)
```

- [PROPOSED] Preserve existing `UV_RUN` and gate order exactly; define `UV_RUN_E2E` separately and append its preflight/browser invocations after smoke. Browser failure cannot prevent earlier domain/integrity evidence from being visible, but the combined target still exits nonzero.
- [SPECIFIED] `make e2e` does not install Chromium automatically. If the explicit browser is missing, preflight fails with the documented install command.
- [PROPOSED] Do not add a retry, headed-mode default, fixed server port, or browser-download fallback to the target.
- [PROPOSED] Add `browser_tests` to compile coverage because it is intentionally outside default pytest discovery.

## 17. Existing tests and validators impact

### 17.1 Required changes

- [PROPOSED] `tests/test_ci_contract.py`: update only the exact workflow-shape assumptions described in §15; retain all legacy semantic assertions.
- [PROPOSED] `tests/test_final_acceptance_contract.py`: add a test that `scripts/final_acceptance.sh` no longer contains “Browser paint or interaction was not executed” or “KL-22 limits product proof”, contains the real-browser-via-`make ci` evidence statement, and permits only the exact SHA-verified axe vendor path in its third-party keyword disposition.
- [PROPOSED] `tests/test_browser_harness_contract.py` must run without launching a browser and cover:
  - exact proposed dependency pins under `[project.optional-dependencies].e2e`;
  - `dev` remains exactly `["pytest>=8,<9", "httpx>=0.27,<1"]`;
  - `testpaths == ["tests"]` and top-level browser directory;
  - legacy `UV_RUN` is unchanged while `UV_RUN_E2E` is exactly locked with `--extra dev --extra e2e`;
  - `make e2e` explicit flag/preflight and `ci` inclusion;
  - server child command begins with `sys.executable`, never bare `python`, and receives only the allow-listed environment;
  - preflight missing-browser returns nonzero with safe remediation;
  - axe asset SHA/licence/notices;
  - no URL-based axe injection;
  - no screenshot-comparison API/pattern;
  - failure collector classifies each synthetic event record.

### 17.2 No-change assessments

- [VERIFIED] `tests/test_packaging.py` does not assert a fixed member list for this repository and needs no source edit. After S06 is tracked, `scripts/package_project.sh` includes browser tests, axe licence/asset, docs, and reference evidence automatically via `git ls-files`.
- [SPECIFIED] Run `tests/test_packaging.py` in the default suite to prove tracked-only packaging remains secure.
- [SPECIFIED] `tests/test_prohibited_files.py` and `scripts/check_prohibited_files.py` are unchanged. The staged candidate must pass the scanner, including vendored JavaScript and reference binaries.
- [SPECIFIED] `scripts/check_threshold_literals.py` is unchanged because no engine threshold is added; browser-test constants are test protocol dimensions, not decision thresholds.
- [SPECIFIED] `scripts/verify_integrity.py` and `scripts/validate_scenarios.py` are unchanged; no manifest generator runs.

### 17.3 Conditional UI-test changes

- [SPECIFIED] Add a static/dossier unit regression only after the corresponding browser failure is observed. Never modify an existing assertion merely to match a new implementation.
- [PROPOSED] If a CSS focus defect is found, add a static test requiring `:focus-visible` and token references; then add the smallest token-based rule.
- [PROPOSED] If axe identifies a name/role/contrast defect, add a focused source/API contract matching the exact defect before remediation.

## 18. Observable acceptance criteria

| AC | Observable result | Proving test/command |
|---:|---|---|
| AC-01 | Exact pinned Python tools resolve under the separate `e2e` extra, `dev` remains its exact two-entry baseline, and vendored axe has recorded licences. | `uv lock --check`; `tests/test_browser_harness_contract.py`; notices/source files |
| AC-02 | One command starts/stops a real app and real Chromium on localhost without a fixed port. | `make e2e`; server log/summary |
| AC-03 | Default pytest and legacy `dev` install paths are browser-independent and retain every existing test/dependency behavior. | `PYTHONPATH=src pytest -q`; dependency contract; collection contains no `browser_tests/` |
| AC-04 | Portfolio loads correctly in public and simulated modes. | browser test #1 |
| AC-05 | Every card, select option, and hero path works in each applicable mode. | browser tests #2–#4 |
| AC-06 | Switching either direction preserves PP selection and updates state. | browser test #5 |
| AC-07 | Existing navigation and methodology action are operable. | browser test #6 |
| AC-08 | Dossier opens as a real popup for all four case/mode combinations. | browser test #7 |
| AC-09 | Clipboard content is parseable dossier JSON with exact ID/mode/state. | browser test #8 |
| AC-10 | Every dossier honors print CSS and yields structurally valid, non-trivial PDF bytes. | browser test #9 |
| AC-11 | Every current interactive control is reached by Tab with visible focus at all widths and both modes. | browser test #10 |
| AC-12 | Workspace and dossier have zero WCAG 2.1 A/AA axe violations in all four case/mode states. | browser tests #11–#12 |
| AC-13 | Arabic nodes compute RTL and demonstrate non-tofu glyph rendering. | browser tests #13–#14 plus font preflight |
| AC-14 | No page-level overflow and required controls are actionable at all widths/modes. | browser test #15 |
| AC-15 | Exactly 40 compact, indexed, hashed non-oracle WebPs document all principal states/widths. | browser test #16 and tracked index |
| AC-16 | Collector wiring is proven and every ordinary journey is protected. | browser test #17 plus fixture finalizers |
| AC-17 | Any console/page/network/HTTP/external/axe defect makes e2e and CI nonzero. | guardrail self-test, collector unit contract, `make e2e` |
| AC-18 | Browser is an independent hosted job with cache/font/install/failure artifacts. | `tests/test_ci_contract.py`; hosted check |
| AC-19 | Existing Python and Docker jobs are behaviorally unchanged. | legacy CI contract tests and hosted checks |
| AC-20 | `make ci` includes all prior gates then browser. | Make contract plus fresh `make ci` |
| AC-21 | Integrity, scenario validation, goldens, smoke, packaging, and decision semantics remain unchanged. | required proof commands in §24 |
| AC-22 | KL-22/traceability/docs/ADR/changelog accurately describe implemented evidence without claiming hosted facts early. | docs review and final acceptance contract |
| AC-23 | No secret/prohibited/governed path enters the candidate. | staged prohibited scan; protected-path diff |
| AC-24 | Supervisor and independent Reviewer report zero findings before delivery; all five hosted checks are green. | later governed review/PR records, not Implementer self-claim |

## 19. Documentation changes

### `docs/DEVELOPMENT_GUIDE.md`

- [PROPOSED] Preserve the existing pip `-e ".[dev]"` instructions unchanged. Add the separate browser setup commands `uv sync --locked --extra dev --extra e2e --python "3.12"` and `uv run --locked --extra dev --extra e2e python -m playwright install --with-deps chromium`, plus exact pins, Arabic font prerequisite/check, `make e2e`, artifact locations, default browser-test exclusion, missing-browser failure semantics, and focused command examples.
- [PROPOSED] Extend local CI gate list with “real Chromium acceptance” after smoke.
- [SPECIFIED] State runtime is localhost/offline and axe is vendored; browser/dependency installation is setup, not a live test dependency.
- [SPECIFIED] State references are documentary and S07 owns visual-regression baselines.
- [PROPOSED] Add troubleshooting for browser revision mismatch, font/tofu failure, console/pageerror, requestfailed/HTTP≥400, axe violations, overflow/focus, PDF structure, and CI artifact download.

### `docs/OPERATOR_RUNBOOK.md`

- [PROPOSED] Add a “Real-browser acceptance” section with prerequisite install and single command:

```bash
make e2e
```

- [PROPOSED] Explain that the command owns ephemeral localhost startup/health/teardown, writes ignored diagnostics, and fails instead of skipping when Chromium is absent.
- [PROPOSED] Update “Required gates” so `make ci` is documented as including e2e.
- [SPECIFIED] Preserve the synthetic evidence warning and localhost boundary.

### `docs/KNOWN_LIMITATIONS.md`

- [PROPOSED] Move KL-22 from “Accepted for this MVP” to a v0.3.0 closure table with implementation/test pointers.
- [SPECIFIED] Do not invent PR number, hosted run, merge SHA, or closure date. Until the Supervisor delivers, say local implementation evidence is provisional and closure becomes effective on approved S06 merge with a green browser check.
- [PROPOSED] Add `KL-31` to the OPEN table: the topbar `/docs` API page depends on FastAPI's public-CDN Swagger assets, is not accepted for offline Ministry use, and is scheduled for S07 to vendor offline assets or remove the link.
- [SPECIFIED] Do not alter the substance of KL-20, KL-21, or KL-23–KL-30; the new API-docs row remains OPEN, not accepted or closed.

### `docs/REQUIREMENTS_TRACEABILITY.md`

- [PROPOSED] Replace the opening Gate G/TL-07 paragraph with actual real-browser scope, including the non-oracle screenshot boundary.
- [PROPOSED] Add an evidence-registry entry for S06 local evidence only after a fresh observed run; the Supervisor later adds hosted CI/merge facts.
- [PROPOSED] Update NFR-006, NFR-007, TL-07, GATE-G, DOD-08, and DOD-09 evidence/slice references to include S06.
- [PROPOSED] Add `## H. Milestone v0.3.0 — Real-browser acceptance` with exact rows `V3-A1` through `V3-A6`, each `TESTED` only after matching local evidence exists. Do not use `COMPLETE` before delivery.
- [SPECIFIED] Keep historical v0.2.0 evidence records unchanged.

### `docs/ARCHITECTURE_DECISIONS.md`

- [PROPOSED] Amend ADR-007's job enumeration from four rendered checks to five after S06 and name `browser / Chromium / Python 3.12`; procedural all-green enforcement remains unchanged.
- [SPECIFIED] Do not create an authority-change ADR because S06 changes no governed domain artifact.

### `CHANGELOG.md`

- [PROPOSED] Add `## Unreleased` bullets for real Chromium journeys, WCAG/keyboard/network/console gates, print/PDF proof, documentary references, and the additional CI job.
- [SPECIFIED] Do not assign version `0.3.0` or a date in S06.

### `scripts/final_acceptance.sh`

- [PROPOSED] Keep 42 steps and the existing `make_ci` call. Change only stale S05-era docs audit/result language so it states the browser gate ran through `make ci`, points to S06 evidence, and no longer treats KL-22 as accepted.
- [PROPOSED] Its keyword audit must record matches in `browser_tests/vendor/axe-core-4.13.0/axe.min.js` as `LEGITIMATE — SHA-verified vendored third-party source` only after the preflight/hash contract passes. Do not add a wildcard `browser_tests/` exclusion; project-authored browser code remains fully scanned.
- [SPECIFIED] Do not fold browser artifacts into the tracked S05 result or claim a new release.

## 20. Requirement traceability

| ID | Implementation | Tests / commands | Evidence artifact |
|---|---|---|---|
| V3-A1 | Pinned pytest-playwright/Chromium harness and server fixture | #1–#17; `make e2e` | `test_evidence.md`; browser CI |
| V3-A2 | Existing data/role locators; card/select/hero/mode/popup/clipboard/nav paths | #2–#8 | journey summary |
| V3-A3 | Four fixed viewport records and responsive fixture | #10, #15, #16 | responsive results + 40 references |
| V3-A4 | Tab/focus helper, RTL/font helper, print/PDF helper | #9–#10, #13–#14 | focus matrix, font record, PDF summaries |
| V3-A5 | Collector, external-origin blocker, axe gate, independent CI job | #11–#12, #17; CI contract | traces/screenshots/axe JSON on failure |
| V3-A6 | Documentary capture/index writer under slice record | #16 | `reference-screenshots/v0.2.0/index.md` |
| NFR-004 | Local vendored axe; app-only network policy; no keys | all guarded tests; preflight | collector summary / no external requests |
| NFR-006 | Native-role locators, Tab traversal, focus visibility, axe zero | #10–#12, #15 | accessibility summary |
| NFR-007 | RTL computed direction and non-tofu font/canvas checks | #13–#14 | font/glyph summary |
| NFR-008 | WSL/Linux local command; fixed Ubuntu browser job; Docker unchanged | `make e2e`, hosted job, Docker legacy job | local/CI records |
| Core 09 §2.7 / TL-07 | Real interaction layer complements static contracts | all browser tests + default static tests | traceability rows |
| Gate G | Browser-observed controls, adaptive states, dossier print, Arabic | #1–#16 | Gate G traceability |
| DOD-08 | Desktop/tablet real usability | #10, #15, #16 | viewport matrix |
| DOD-09 | JSON/HTML dossier plus print-to-PDF proof | #7–#9 | dossier/PDF summary |
| KL-22 | Real-browser gap removed after governed delivery | `make e2e`, CI, reviews | limitation closure row |
| R-4 | No reference comparison; S07 baseline authority preserved | #16 + non-oracle contract | index warning / source scan |
| ADR-004 | Exact Python pins and uv lock; pip install path remains | uv/pip hosted jobs; lock check | lock diff / CI |
| ADR-007 | Browser check added to all-green merge gate | CI contract; `gh pr checks` later | Supervisor PR record |
| ADR-010 | No authority artifact changes | protected diff/integrity | implementation log |

## 21. Explicit non-goals

- [SPECIFIED] No Executive Mode, AR/EN UI switch, full-interface RTL, design-token overhaul, ES-module split, component refactor, or visual redesign (S07/S18).
- [SPECIFIED] No visual-regression baseline, image comparison, snapshot threshold, or screenshot-update approval workflow (S07).
- [SPECIFIED] No vendoring of FastAPI Swagger UI assets and no removal/redesign of the topbar `/docs` API link; that OPEN offline-demo defect candidate is carried to S07.
- [SPECIFIED] No graph, drill-down, reset, screening, new cases, new route, or new analytical panel.
- [SPECIFIED] No change to decision semantics, thresholds, config, evidence, synthetic labelling, public/simulation isolation, goldens, Core, DOCX, or hashes.
- [SPECIFIED] No PDF API/export feature; S06 validates Chromium-generated PDF from existing printable HTML. Productized bilingual PDF belongs to S19.
- [SPECIFIED] No production authentication, authorization, deployment, live connector, database, Ministry data, or external test service.
- [PROPOSED] No mobile viewport beyond the four approved dimensions.
- [PROPOSED] No cross-browser Firefox/WebKit matrix; `page.pdf()` and the approved objective bind S06 to Chromium.
- [PROPOSED] No performance benchmark, Lighthouse, screen-reader automation, or manual WCAG certification claim.
- [SPECIFIED] No test weakening, deletion, xfail, skip in explicit gate, retry masking, or manifest regeneration.

## 22. TDD/characterization task sequence for the Implementer

Every task ends **Confirm → Validate → Test**. Do not combine tasks out of order, and do not begin documentation promotion before observed evidence exists.

### Task 0 — Reconfirm authority and protected baseline

1. [ ] Confirm branch, HEAD, status, tool versions, ignored/untracked `.env` status without reading it, and the four pre-existing untracked paths.
2. [ ] Record protected-path hashes/status; do not run `build_manifests.py`.
3. [ ] Confirm no browser/dev process is already running for this repository.
4. [ ] Validate proposed package/action versions against their registries and record exact metadata/licences; stop on mismatch.
5. [ ] Test: none—this is read-only preflight. Record evidence, not a pass claim.

### Task 1 — RED: lock the toolchain/CI/Make/vendor contract

1. [ ] Write failing assertions in `tests/test_browser_harness_contract.py` and extend `tests/test_ci_contract.py` for the exact `e2e` pins, unchanged two-entry `dev` extra, unchanged legacy `UV_RUN`, separate `UV_RUN_E2E`, directories, Make target, new CI job, axe asset/licence, and non-oracle ban.
2. [ ] Run:

```bash
PYTHONPATH=src pytest -q \
  tests/test_browser_harness_contract.py \
  tests/test_ci_contract.py
```

3. [ ] Confirm RED is for absent S06 files/targets/job, not a typo.
4. [ ] Add the exact pins under a new `e2e` extra without changing either existing `dev` entry; acquire axe-core 4.13.0 from its npm tarball with scripts disabled; copy only `axe.min.js` and `LICENSE`; write `SOURCE.json` and notices.
5. [ ] Run `uv lock`; inspect the complete lock diff, separate root `e2e` metadata, unchanged root `dev` metadata, and exact resolved versions across supported Python versions.
6. [ ] Add Makefile/CI/gitignore skeleton matching §§14–16.
7. [ ] Validate no `package.json` or npm lock was created.
8. [ ] Test the targeted contracts again; expected GREEN except behavior tests intentionally waiting for later tasks.

### Task 2 — RED/GREEN: prerequisite checker

1. [ ] Write unit tests for exact version success, missing browser nonzero, axe hash mismatch nonzero, and missing Arabic font nonzero using injected paths/subprocess results.
2. [ ] Observe focused RED.
3. [ ] Implement `scripts/check_browser_prerequisites.py` with typed public functions, no bare exception, no environment-value output, and exact safe remediation.
4. [ ] Observe focused GREEN.
5. [ ] Install matching Chromium for development only:

```bash
uv run --locked --extra dev --extra e2e python -m playwright install --with-deps chromium
```

6. [ ] Run real preflight; record package, browser, and font evidence.

### Task 3 — RED/GREEN: server, state helpers, and failure collector

1. [ ] Write pure unit tests for URL-origin classification, response threshold, console type filter, duplicate-free rendering, the allow-listed child environment, and a child command whose first element is `sys.executable` rather than bare `python`.
2. [ ] Observe focused RED.
3. [ ] Implement `browser_tests/harness.py`, `pages.py`, and `conftest.py` interfaces from §7.
4. [ ] Add `test_failure_collector_observes_all_required_channels`; observe RED until listeners classify all named probes.
5. [ ] Implement listener wiring without an ordinary-journey exclusion path.
6. [ ] Observe GREEN and verify server teardown leaves no child process.

### Task 4 — Characterize journeys A–D

1. [ ] Add tests #1–#6 one behavior at a time.
2. [ ] Run each new node immediately. Existing behavior may pass on first run; record it honestly as characterization, not fabricated RED.
3. [ ] If a test fails, first distinguish harness/locator error from a product defect using DOM/network/console evidence.
4. [ ] Fix only harness mistakes here. Defer genuine UI defects to Task 8.
5. [ ] Run all journey tests and confirm both modes/cases.

### Task 5 — Characterize dossier action, clipboard, print, and PDF

1. [ ] Add popup test #7 and run all four nodes.
2. [ ] Add clipboard test #8 and run all four nodes with real permissions/API.
3. [ ] Add print/PDF test #9 and run all four nodes; retain PDF summaries/artifacts.
4. [ ] Treat any genuine renderer/action failure as Task 8 work; do not weaken structural PDF checks.
5. [ ] Run `tests/test_api.py` and `tests/test_dossier_contract.py` after any renderer-related observation.

### Task 6 — Characterize accessibility, keyboard, and RTL

1. [ ] Add keyboard/focus test #10; capture exact 15-control order/signatures.
2. [ ] Add workspace/dossier axe tests #11–#12 with no exclusions.
3. [ ] Add RTL/font tests #13–#14.
4. [ ] Run focused nodes and preserve complete violation/glyph output.
5. [ ] Any product defect proceeds to Task 8 with the browser test frozen.

### Task 7 — Responsive matrix and untouched-baseline references

1. [ ] Add responsive test #15 and run all eight nodes.
2. [ ] Add reference capture/index test #16.
3. [ ] Before any UI remediation, capture the 40 v0.2.0 references using the exact command in §7.8.
4. [ ] Validate file count, dimensions, hashes, index, individual size, aggregate size, and non-oracle warning.
5. [ ] Record the base/UI-file hashes proving what was captured.

### Task 8 — RED/GREEN minimal defect remediation, only if needed

For each observed defect independently:

1. [ ] Record browser test/node, axe ID or console/network/focus/overflow evidence, and baseline screenshot path.
2. [ ] Retain the failing e2e test and add the smallest source/API regression that fails for the same cause.
3. [ ] Observe intended RED.
4. [ ] Change only the permitted conditional file; use design tokens for any CSS value.
5. [ ] Re-run the focused browser and source test; observe GREEN.
6. [ ] Capture an affected post-fix screenshot under ignored artifacts and record before/after evidence. Do not replace the v0.2.0 reference set.
7. [ ] Run all axe/keyboard/responsive nodes after every accessibility/layout fix.
8. [ ] If remediation requires redesign, i18n, domain policy, or an axe exclusion, stop and return a Supervisor finding.

### Task 9 — Truthful CI, final-acceptance copy, and documentation

1. [ ] Finalize `tests/test_ci_contract.py` and observe RED before final YAML if not already done.
2. [ ] Finalize exact CI job and observe contract GREEN.
3. [ ] Add `tests/test_final_acceptance_contract.py` stale-copy assertions and observe RED.
4. [ ] Update only the named `final_acceptance.sh` copy/audit fragments and exact axe vendor disposition; retain 42-step/order/anti-escape contracts and scan all project-authored browser code; observe GREEN.
5. [ ] Update development/operator/limitations/traceability/ADR/changelog per §19.
6. [ ] Run focused docs/CI/final-acceptance contract tests.

### Task 10 — Full verification and handoff records

1. [ ] Run the exact proof sequence in §24 with fresh output.
2. [ ] Run the full browser matrix and inspect the complete summary, not only exit code.
3. [ ] Confirm protected paths have no change; inspect all changed/untracked paths.
4. [ ] Write `implementation_log.md` and `test_evidence.md` with §23 content.
5. [ ] Run browserless pytest again after records/docs changes.
6. [ ] Stop uncommitted. Return candidate file list/hashes and unresolved risks; do not self-approve.

## 23. Required implementation and evidence records

### 23.1 `implementation_log.md`

The Implementer must record:

1. [SPECIFIED] Role/model/persona, approved plan revision, branch, exact base SHA, and pre-existing untracked paths.
2. [PROPOSED] Exact resolved package/action/axe versions, source URLs/SRI/SHA-256, licences, lock-diff summary, and font package/family.
3. [PROPOSED] File-by-file change summary separated into unconditional harness/tooling/docs and conditional UI fixes.
4. [SPECIFIED] TDD/characterization ledger: test name, first result, expected failure, minimal implementation/fix, green result. Never label first-pass existing behavior RED.
5. [SPECIFIED] Defect ledger for every UI edit: defect ID, requirement, before evidence, root cause, changed lines, focused test, after evidence, screenshot paths. Write “No UI defects observed; no UI files changed” if true.
6. [PROPOSED] Reference-capture provenance: capture command, UI hashes, 40-file count, total bytes, index path, and explicit non-oracle statement.
7. [SPECIFIED] Protected-path audit and statement that no config/data/core/DOCX/golden/hash change or generator run occurred.
8. [SPECIFIED] Security/privacy audit: `.env` not read, localhost only, external requests zero, helper scripts untouched, raw artifacts ignored.
9. [SPECIFIED] Known limitations/assumptions/open findings, including any Supervisor decision required.
10. [SPECIFIED] Explicit statement that the record is implementation evidence, not approval or delivery.

### 23.2 `test_evidence.md`

The Implementer must record actual output for:

1. [PROPOSED] Environment: OS/WSL, Python, uv, Node/npm, Playwright package, pytest-playwright, Chromium version/build, axe SHA, font package/family/file.
2. [PROPOSED] Preflight exit/output and server base origin with the ephemeral port redacted to `<ephemeral>` in the durable record.
3. [PROPOSED] Browser inventory: 17 named tests, actual collected/passed/failed/skipped count, duration, and explicit-command skip count (must be zero).
4. [PROPOSED] Journey matrix for both cases/modes and selector/action paths.
5. [PROPOSED] Failure-hook self-test categories and ordinary-journey error totals (all zero).
6. [PROPOSED] Keyboard matrix by viewport/mode, expected/reached control count, and focus-visible result.
7. [PROPOSED] Axe matrix by page state with violation count zero; if defects were fixed, link before/after records.
8. [PROPOSED] RTL/font matrix and non-tofu metrics.
9. [PROPOSED] PDF matrix with bytes, page-object count, header/EOF result, and ignored artifact path; do not commit PDFs.
10. [PROPOSED] Reference index/file count/size/hash validation and tracked path.
11. [SPECIFIED] Fresh outputs for default pytest, integrity, scenario validation, smoke, `make e2e`, `make ci`, JS/Python compile, packaging tests, prohibited scan, and `git diff --check`.
12. [SPECIFIED] Exact golden outcome summary proving steel public INVESTIGATE and PP public REJECT unchanged.
13. [SPECIFIED] Note that pre-stage prohibited scans do not cover untracked new files; the Supervisor must stage exact paths and rerun before commit.
14. [SPECIFIED] Explicit statement that local evidence does not claim Supervisor review, independent review, hosted CI, merge, limitation closure, or release.

## 24. Verification and proof commands

Run from repository root. Fresh final sequence:

```bash
uv lock --check
uv sync --locked --extra dev --extra e2e --python "3.12"
uv run --locked --extra dev --extra e2e python scripts/check_browser_prerequisites.py

PYTHONPATH=src uv run --locked --extra dev --extra e2e pytest -q \
  tests/test_browser_harness_contract.py \
  tests/test_ci_contract.py \
  tests/test_final_acceptance_contract.py \
  tests/test_packaging.py

make e2e
make ci

PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/demo_smoke.py

PYTHONPATH=src uv run --locked --extra dev python scripts/validate_scenarios.py
uv run --locked --extra dev python scripts/check_prohibited_files.py
uv run --locked --extra dev python scripts/check_threshold_literals.py
uv run --locked --extra dev python -m compileall -q src scripts tests browser_tests
node --check src/ior_mvp/static/app.js
git diff --check
```

- [SPECIFIED] The three workspace proof commands appear in their required integrity → pytest → smoke order.
- [PROPOSED] Also confirm Python 3.14 dependency/default-suite compatibility:

```bash
uv sync --locked --extra dev --python "3.14"
PYTHONPATH=src uv run --locked --extra dev pytest -q
```

- [SPECIFIED] Do not run `scripts/build_manifests.py`.
- [SPECIFIED] The Supervisor, after independent APPROVE and exact-path staging, reruns `make ci`, the prohibited scan, protected-path diff, and `git diff --check` on the staged candidate before commit.
- [SPECIFIED] Hosted acceptance is the new browser job plus every legacy job green on the exact PR head; local output is not a substitute.

## 25. Rollback and recovery

- [PROPOSED] Before commit, rollback is a reviewed inverse patch limited to the files in §6; never use `git reset --hard` or discard unrelated/untracked work.
- [PROPOSED] Remove new Python dependency declarations and the corresponding resolver-generated lock entries together; remove the browser job and Make targets together; restore truthful pre-S06 docs only if S06 is fully withdrawn.
- [PROPOSED] Delete only `.artifacts/e2e/` to clean runtime output. Browser cache under `~/.cache/ms-playwright` may remain because it is outside repository/product state.
- [PROPOSED] The server fixture owns SIGTERM/FD closure; recovery verifies no child uvicorn process remains.
- [PROPOSED] After merge, the Supervisor can revert the S06 squash commit through a new reviewed PR, then require all remaining legacy checks green. No data migration, database rollback, config downgrade, manifest regeneration, or tag movement is involved.
- [DERIVED] Removing documentary references does not affect a product oracle because S06 never makes them executable baselines.
- [SPECIFIED] If S07 has already established governed visual baselines, an S06 rollback must be separately assessed against S07 rather than deleting S07 artifacts.

## 26. Open questions for the Supervisor

- None. The owner-approved scope resolves the tooling family, required browser, viewport matrix, reference/oracle boundary, evidence modes, and gate behavior.
- [PROPOSED] Defaults adopted by this plan: Python pytest-playwright; browser job on Python 3.12/Ubuntu 24.04; vendored axe-core; `fonts-noto-core`; slice-record WebP references; 8 MiB aggregate reference budget; no xdist; five rendered required checks.
- [PROPOSED] Dependency/action pins remain subject to exact registry/lock verification at implementation time. A resolver mismatch is a stop-and-report contingency, not an unresolved design choice.

## 27. Installed skills read and material effect

| Skill read | Material effect |
|---|---|
| `autonomous-delivery` | [VERIFIED] Enforced role boundary, authority→persona→skills→Sanad→Muhasib order, fresh structured handoff, and no self-approval/delivery. |
| `task-standards` | [VERIFIED] Set the Senior Frontend Test-Automation and Accessibility Engineer persona after authority reading. |
| `project-orientation` | [VERIFIED] Required inspection of README, docs, implementation, scripts, tests, and existing partial frontend contracts before proposing new files. |
| `writing-plans` | [VERIFIED] Produced exact paths, interfaces, commands, RED/GREEN tasks, and an executable handoff rather than a high-level checklist. User-mandated plan path overrides that skill's default path. |
| `test-driven-development` | [VERIFIED] Separates genuine new-helper/contract RED→GREEN from honest characterization of existing UI; requires a failing test before every UI defect fix. |
| `verification-before-completion` | [VERIFIED] Prevents predicted pass claims and defines the fresh proof sequence and evidence content. The Planner did not run tests. |
| `sanad` | [VERIFIED] Every consequential plan claim is labelled and tied to governing files, observed code, derivation, or an explicit proposal. |
| `sanad-provenance` | [VERIFIED] Reinforced source attachment for versions, licences, environment facts, and requirements. |
| `muhasib` | [VERIFIED] Supplies the pre-handoff scope/secrets/changed-files/assumption/self-approval audit in §28. |
| `muhasabah-gate` | [VERIFIED] Required the final provenance, assumption, fabrication, scope, and reversibility check. |
| `using-superpowers` | [VERIFIED] Read as required; its explicit subagent stop says dispatched subagents ignore that skill, so it did not add a separate workflow or brainstorming step. |

## 28. Sanad ledger and Muhasib self-audit

### Sanad

Tags mean:

- `VERIFIED`: directly read in repository/tool output or fetched public package metadata.
- `SPECIFIED`: explicit governing requirement/owner ruling.
- `DERIVED`: reasoned consequence of cited verified/specified facts.
- `PROPOSED`: implementation choice for Supervisor review.
- `OPEN`: unresolved owner/Supervisor decision.

Marker counts in this completed plan are mechanically checked before handoff:

```bash
rg -o '\[(VERIFIED|SPECIFIED|DERIVED|PROPOSED|OPEN)\]' ".workflow/slices/S06-browser-acceptance-harness/plan.md" | sort | uniq -c
```

```text
VERIFIED=48
SPECIFIED=106
DERIVED=22
PROPOSED=141
OPEN=0
```

### Muhasib

- [VERIFIED] Mandatory authority, core, implementation, control, milestone, workflow, code, tests, validators, toolchain, guides, and relevant skills named by the task were opened with the file-reading tool.
- [VERIFIED] The Planner inspected branch/HEAD/status and environment read-only; no install, browser launch, test, mutation command, stage, commit, push, merge, or tag was performed.
- [VERIFIED] The Planner confirmed `.env` existence/ignore/tracked status without opening or printing it.
- [VERIFIED] The only artifact written by the Planner is this `plan.md`; `persona.md` was not modified.
- [SPECIFIED] The plan stays within S06 and explicitly excludes S07/S08+ functionality, domain semantics, governed artifacts, and release actions.
- [VERIFIED] Every claimed existing file/skill in the reading record was actually opened; the authoritative DOCX is not claimed as read because this non-domain slice did not require a methodology interpretation.
- [PROPOSED] All technical figures introduced by the plan (timeouts, PDF minimum, screenshot budget, CI retention) are labelled implementation defaults, not owner facts or business policy.
- [VERIFIED] No test is claimed passing; all verification commands are future Implementer/Supervisor obligations.
- [SPECIFIED] The Implementer remains a builder, the Supervisor owns delivery, and the independent Reviewer must return zero findings before merge.
- [VERIFIED] Self-audit result: `PASS`, subject to Supervisor plan review; this is not self-approval of implementation.
