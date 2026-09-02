# S07 implementation log — Bilingual interface foundation

This is Implementer evidence from the uncommitted candidate on
`slice/S07-bilingual-interface-foundation`. It is not approval, hosted-CI
evidence, delivery, merge, limitation closure, or release evidence.

## Identity, boundary, and authority

- [VERIFIED] Role/model: Implementer, GPT-5.6 Sol; Supervisor is Claude and the
  independent Reviewer is Grok.
- [VERIFIED] Persona:
  Principal Frontend Engineer for bilingual Arabic/English government decision
  interfaces, RTL/bidi architecture, design tokens, ES modules, offline
  typography, and governed visual regression.
- [SPECIFIED] Data classification: `confidential_demo`; only frozen public and
  explicit Class-D simulation records were rendered.
- [VERIFIED] Branch/base remained
  `slice/S07-bilingual-interface-foundation` /
  `6d00e27ff156e1342d488495c7b48e68eeefe100`.
- [VERIFIED] The DOCX reader could not render the binary methodology. Its
  governed SHA-256 was verified through the authority manifest, and the
  relevant sections were read from the hash-governed searchable mirror and
  cross-checked against Core 01/02/03/06/09.
- [SPECIFIED] The approved contract is `plan.md` Tasks 0–12 and
  `plan_review.md` `PLAN_APPROVED`, including rulings PR-01–PR-05 and RI-01.
- [VERIFIED] `.env` existence and ignore/untracked state were confirmed without
  reading its contents. The Docker context and mounts exclude it.
- [VERIFIED] The two untracked `.workflow/runs/*.sh` helpers, Supervisor-owned
  S06 records, `.workflow/state.json`, and `docs/BUILD_PROGRESS.md` were not
  edited.

## Environment and pinned inputs

| Item | Observed value |
|---|---|
| Host | Ubuntu 26.04 / WSL2, kernel 6.6.114.1 |
| Primary Python | CPython 3.12.13 in `.venv` |
| Compatibility Python | CPython 3.14.4 in `/tmp/venv314` |
| uv | 0.11.31 |
| Node | 22.22.3 |
| Docker | 29.7.2 |
| Playwright / pytest-playwright | 1.62.0 / 0.9.0 |
| Chromium | revision `chromium-1234`; browser `151.0.7922.34` |
| Pillow | 12.3.0, exact `e2e` pin, MIT-CMU |
| axe-core | 4.13.0; SHA-256 `c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1` |
| Canonical image | `mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d` |

- [VERIFIED] One `uv lock` run added only `pillow==12.3.0`; final `uv.lock`
  SHA-256 is `321f0d4b1677984a904192ab2995acc8f202a085218dd8adf395b2382d2ae216`.
- [VERIFIED] The two WOFF2 additions total 201,780 bytes:
  - Noto Sans Latin variable subset: 35,820 bytes, SHA-256
    `51ca196f49a33e79e7870ff88ebd2829a3f627a51e7d690986618f0e7ad2b52d`,
    Fontsource 5.3.0 / font metadata 42 / OFL-1.1.
  - Noto Sans Arabic variable subset: 165,960 bytes, SHA-256
    `ce85091f020920b65762b387b194ef59457ea5b25b760f2dcc35240a94bb8669`,
    Fontsource 5.2.10 / font metadata 33 / OFL-1.1.
- [VERIFIED] Both upstream licence files matched the approved hashes and exact
  byte counts; `SOURCE.json` records the versioned source URLs, runtime URLs,
  and verbatim Unicode ranges.

## File changes

### Configuration and authority

- `config/evidence_policy.v1.yaml`: 1.1.0 → 1.2.0; exact
  `display_label_ar` only.
- `config/ui_strings.v1.yaml`: new 1.0.0 governed EN/AR catalogue with exact
  key/placeholder parity and no policy-label duplication.
- `docs/core/01_PRODUCT_AND_REQUIREMENTS.md`: per-document Core 2.0.0 marker
  and exact NFR-007 bilingual/source-island contract.
- `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`: marker and two exact
  locale-resource / bilingual-disclosure map entries.
- `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`: marker and exact
  real-browser/visual-oracle §2.7 wording.
- `scripts/build_manifests.py`: catalogue added to the explicit authority
  artifact list.
- `docs/authority/authority_hashes.json` and Manifest §11: one generated
  catalogue row and changed policy/Core 01/02/09 rows only.
- `docs/ARCHITECTURE_DECISIONS.md`: ADR-011 records §7.3/§7.4 classification,
  ADR-010/plan-review basis, owner-amendable wording/digits, islands, fonts,
  KL-31, visual governance, marker strategy, and exact generator diff.

### Server/domain projections

- `src/ior_mvp/config.py`: validated cached catalogue, typed failure classes,
  defensive locale bundles, `ui_text`, cache clearing, and authority version.
- `src/ior_mvp/app.py`: `GET /api/ui-strings/{locale}` and deterministic
  dossier `locale` query.
- `src/ior_mvp/evidence.py`: sole validated `synthetic_display_labels` source
  and bilingual evidence-row projection.
- `src/ior_mvp/rules.py`, `decision_engine.py`, `genui.py`, `dossier.py`:
  additive bilingual policy-label projection; localized dossier chrome;
  unchanged decision calculations and JSON dossier contract.

### Frontend

- `static/index.html`: empty catalogue-bound shell, module entry, locale
  switch, no `/docs` anchor.
- `static/app.js` plus 18 files under `static/modules/`: named-export graph for
  state, API, locale runtime, formatters, DOM/bidi, portfolio, workspace,
  methodology, extraction, events, and ten approved renderer types. Every file
  is at most 199 physical lines.
- `static/styles.css` plus eight `static/css/*.css` files: import façade,
  exclusive token layer, logical-direction shell/workspace/content/responsive
  rules, and embedded dossier styles.
- `static/assets/fonts/**`: exact WOFF2s, upstream licences, source metadata,
  and third-party notices.

### Browser/visual toolchain

- `browser_tests/conftest.py`, `harness.py`, `pages.py`, and five functional
  test files: locale dimension, stable locators, intended-font proof,
  mirroring/source-island assertions, and 118 functional nodes.
- `browser_tests/test_visual_baselines.py`, `visual_baselines.py`,
  `visual_container.py`, `visual/Dockerfile`: four visual nodes, 40-screen
  capture/compare, canonical revision assertion, and update transaction.
- `browser_tests/baselines/v0.3.0/**`: 40 opaque-RGB lossless WebPs plus
  manifest/hash; 5,037,854 image bytes total.
- `scripts/run_visual_baseline_container.py`, `visual_metrics.py`,
  `check_browser_prerequisites.py`: allow-listed shell-free container run,
  codec-free metric tests, exact fonts, and diagnostic-only fontconfig.
- `Makefile`, CI workflow, `.dockerignore`, `.gitignore`, `pyproject.toml`,
  `uv.lock`: functional/visual targets, compare-only CI, guarded update path,
  Pillow pin, and ignored temporary outputs.
- `browser_tests/test_reference_screenshots.py`: replaced by the governed
  visual test; the S06 documentary directory itself was not changed.

### Browserless tests and documentation

- Added catalogue, token, ES-module, font, and visual-baseline contract suites;
  updated existing API, dossier, isolation, authority, CI, frontend, scanner,
  and browser-harness contracts without skips, xfails, or weakened goldens.
- Updated README, development/operator/deployment guides, UX §8, changelog,
  known-limitations and traceability records. Supervisor-owned S06 evidence
  text/statuses were preserved; S07 rows remain provisional/`TESTED`.

## TDD and characterization ledger

| Task | First observed result | Root requirement / cause | Green evidence |
|---|---|---|---|
| 0 characterization | 309 default passed; 62 Chromium passed | Existing S06 baseline | recorded before edits |
| 1 modules | 4 intended failures; integration contracts then 4 failures | classic script and missing graph/checker | 83 focused passed; 62 Chromium passed |
| 2 tokens | 12 intended failures | missing layer/scanner and existing literals/inline styles | 29 focused passed; scanner PASS; 62 Chromium passed |
| 3 catalogue/runtime | 10 intended failures | missing catalogue/API/check modes | catalogue/API focused green |
| 4 policy labels | 11 intended failures | policy 1.1.0 and one-language projections | 83 then 100 focused passed |
| 5 fonts | 3 intended failures | missing exact assets/metadata/preflight contract | 28 focused passed; preflight PASS |
| 6 dossier | 4 intended failures | English-only document/chrome and no islands | localized dossier/API/authority suites passed |
| 7 KL-31 | 1 intended failure after restoring the pre-change anchor | demo exposed `/docs` | static/API contracts passed; engineer route retained |
| 8 browser matrix | 108 passed / 10 failed | dossier family selection and a test reload assumption | focused 10 passed, then 118/118 |
| 9 comparator | 12 intended failures | missing Pillow/comparator/guards/container | 13/13 contract tests |
| 10 baselines | initial canonical capture completed; visual review found defects | known defects cannot enter oracle | defects fixed test-first; 118 functional passed before each recapture; host compare 4/4 |
| 11 authority | 2 intended failures | missing markers/generator catalogue path | Core/generator contracts and post-generation integrity passed |
| scanner deletion | 1 intended failure | tracked deletion was unreadable before staging | 31 scanner tests and live prohibited scan passed |
| Python 3.14 | first final run had 1 stale contract failure | assertion followed a moved metric helper | corrected contract; full 3.14 suite passed |

## Browser-revealed defect ledger

- **S07-UI-01 — dossier Arabic family selection.** Eight locale/case nodes
  exposed inherited Latin/default family reporting. Dossier root and Arabic
  spans now select `IOR Noto Sans Arabic`; intended-family and tofu checks pass.
- **S07-UI-02 — state-label collision.** Canonical review showed localized
  state text touching the raw audit code. A tokenized gap now separates them.
- **S07-UI-03 — sticky anchor clipping.** Canonical review showed the workspace
  heading under sticky chrome. A tokenized logical scroll margin fixes browser
  navigation and capture anchors.
- **S07-UI-04 — host/container dossier glyph drift.** The first host compare
  isolated all material difference to user-agent monospace in the supply JSON
  source island. Source/code islands now explicitly use the vendored interface
  family; canonical and WSL comparison pass under the fixed tolerance.
- **S07-UI-05 — simulated-surface disclosure completeness.** A final safety
  audit added failing governance and portfolio assertions, exposing surfaces
  without the policy pair. The governance card and simulated portfolio now
  render both labels directly from the locale bundle; public mode renders
  neither. All 118 functional nodes passed before the final canonical capture.

## Baseline provenance and governance

- [SPECIFIED] Matrix: 10 screens × 2 locales × 2 viewports = 40 WebPs;
  presentation widths remain functional-only.
- [VERIFIED] Final image total: 5,037,854 bytes; every image is below 600 KiB
  and total is below 12 MiB.
- [VERIFIED] Manifest SHA-256:
  `b0295568b764fc08e1d414bbea4d706dcba7f2f8f877eb2770eb3b890a264a50`;
  `manifest.sha256` content validates it.
- [VERIFIED] Canonical updates asserted `chromium-1234` inside the pinned Noble
  image and recorded browser `151.0.7922.34` plus all launch flags.
- [SPECIFIED] Significant channel delta is >8; ratio ≤0.001 and mean absolute
  channel error ≤0.20 must both pass. No masks, per-screen overrides, or CI
  update path exists.
- [VERIFIED] Initial visual review found defects, so that candidate was not
  retained. Each correction was followed by all 118 functional nodes before a
  canonical recapture. The final Docker-free host comparison passed 4/4.

## Authority generator and protected paths

- [VERIFIED] `scripts/build_manifests.py` ran exactly once.
- [VERIFIED] Generated machine diff: evidence policy
  `30018295…7081` / 1,479 bytes; catalogue
  `c6532773…9590` / 23,097 bytes; Core 01
  `8c8cea8f…8080` / 11,942 bytes; Core 02
  `4352f990…104c` / 11,416 bytes; Core 09
  `81b221b5…0559` / 6,671 bytes. No other row or generated date changed.
- [VERIFIED] `snapshot_manifest.json` remained byte-identical with SHA-256
  `0fb34f96a1d4a9745e93ee2a54f210b97e6f4597a1d75bd9d6c74c5d430d9a1e`.
- [VERIFIED] Manifest §11 is mechanically tested against every machine row;
  post-generation integrity reports `INTEGRITY PASS`.
- [VERIFIED] No `data/**`, thresholds, sector profiles, Core 03–08, DOCX,
  scenario, snapshot, or golden expectation changed.
- [VERIFIED] A non-staging scan of all 147 Implementer candidate files found
  zero prohibited-path or credential-pattern findings.
- [VERIFIED] The S06 documentary directory aggregate remained
  `d71041e0811509746a94ec9baf7c2511236b64c22fd2774e732d08ed50dc6784`
  when hashed from the tracked path list.

## Adjudications and limitations

- [DERIVED] Reload persists locale only; selected case and evidence mode return
  to deterministic defaults because no requirement authorizes storing them.
  Immediate switching and popstate preserve both.
- [DERIVED] Host fontconfig remains DejaVu Sans but is diagnostic only; exact
  vendored bytes and browser-observed `IOR Noto Sans Arabic` are controlling.
- [DERIVED] Source-language islands are intentional truthfulness controls, not
  completion of S19's full bilingual dossier-body scope.
- [DERIVED] A post-generator request-epoch correction changed only ungoverned
  browser source. The consumed generator output remained exact for every
  governed file; the final visual oracle was recaptured and its source hashes
  now match. No second generator run was performed.
- [SPECIFIED] Arabic warning wording and Western-digit/Gregorian presentation
  are Supervisor-approved owner-amendable defaults, not owner-approved facts.
- [SPECIFIED] Local green evidence cannot approve this candidate. Supervisor
  review and independent Grok review remain mandatory.
- Open items: none.

## Sanad count

`VERIFIED=20`, `SPECIFIED=6`, `DERIVED=4`, `PROPOSED=0`, `OPEN=0`.

## Recovery

Before delivery, rollback is an inverse patch limited to S07 paths. The
authority policy/catalogue/Core/hash/table changes roll back as one reviewed
unit; no generator is rerun to accept unexplained bytes. The v0.3.0 baselines
and comparator roll back together. The S06 documentary references remain
untouched.

## Fix round 1

Supervisor findings SR-01 and SR-02 were implemented test-first without
changing policy, Core, data, thresholds, sector profiles, scenarios, S06
records, decision logic, or golden expectations.

- **SR-01a — ungrouped years/identifiers.** Before: portfolio and chart text
  rendered `2,024` / `2,021`. After: the new non-grouping integer formatter
  renders `2024` / `2021`; the four locale/mode portfolio nodes reject any
  four-digit year containing `,` or `٬`.
- **SR-01b — state/execution duplication.** Before: English chips and dossier
  state rendered `Investigate INVESTIGATE` or `Reject REJECT`. After: English
  renders the isolated raw code once; Arabic renders the localized label plus
  one isolated code. Existing parameterized journeys and dossiers assert that
  no adjacent chip word repeats.
- **SR-01c — label/value composition.** Before: route label and value touched
  without punctuation. After: the governed `common.label_value:
  "{label}: {value}"` pattern supplies a visible colon and the value is an LTR
  source-language `bdi`; all 16 responsive nodes assert the separator.
- **SR-01d — technical-token isolation.** Before: split label/value nodes
  visually reordered `HS 721049` and `HS H0 / 721049` in RTL. After: each
  complete token is one `bdi.technical-token[dir=ltr]`; Arabic responsive and
  dossier assertions prove exact logical `textContent`, computed
  `direction=ltr`, and `unicode-bidi=isolate`.
- **SR-01e — hero badge overlap.** Before: the 1024×768 English state badge
  intersected Conditions. After: `--layout-decision-columns` becomes one
  column at the approved `max-width: 1180px`; all 16 locale/mode/viewport
  responsive nodes calculate badge/conditions/kill-condition rectangles and
  assert no intersection.
- **SR-01f — Arabic disclosure alignment.** Before: `flex-end` placed the
  simulated disclosure at the RTL inline end. After: logical `flex-start`
  aligns it to inline start; the responsive mirroring assertions compare its
  right edge in Arabic and left edge in English to the portfolio grid.
- **SR-02 — durable mode summaries.** Functional and visual runs now write
  `run-summary-functional.json` and `run-summary-visual.json`. Atomic
  directory-level replacement also permits a host compare to replace the
  root-owned visual summary produced by the canonical container.

The catalogue change required the one authorized additional
`scripts/build_manifests.py` run. Generator runs total **2** for S07. Relative
to the pre-fix candidate, only the `config/ui_strings.v1.yaml` authority row
changed to SHA-256
`59ccb67a882ee4fa70390a4588873724074a2e689a17b7bcc6dc850cb1602f41`
and 23,183 bytes; `generated_on` remained `2026-09-02`. Integrity passed.

Canonical regeneration used change reference
`S07-SR-01-defect-fixes`: 40 lossless WebPs, manifest SHA-256
`0d21e94a99128b0d4f2dc38b5f0f57b0967f58228eb32921cb85f5939207e3bd`,
4,987,732 image bytes. The required host comparison then passed 118
functional and 4 visual nodes. Final `make ci` exited 0.
