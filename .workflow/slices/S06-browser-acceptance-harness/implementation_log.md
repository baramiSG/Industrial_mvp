# S06 implementation log — Real-browser acceptance harness

## Identity and authority

- Role/model: Implementer, GPT-5.6 Sol (`gpt-5.6-sol-max`).
- Persona: Senior Frontend Test-Automation and Accessibility Engineer.
- Data classification: `confidential_demo`.
- Approved contract: `plan.md` §1–§28, `PLAN_APPROVED` on 2026-09-02;
  Supervisor rulings PR-01, PR-02, PR-03 and RI-01 are incorporated.
- Branch: `slice/S06-browser-acceptance-harness`.
- Base/HEAD during implementation:
  `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`.
- Pre-existing untracked paths:
  `.workflow/runs/demo_start.sh`,
  `.workflow/runs/s05_release_merge_tag.sh`, and this slice's
  `context.md`, `persona.md`, `plan.md`, and `plan_review.md`.
  None was modified.
- A pre-existing user/demo uvicorn process was observed on
  `127.0.0.1:8000` and left untouched. The harness used its own inherited
  `127.0.0.1:<ephemeral>` socket, so the processes did not share a port.

## Skills read and material effect

- `autonomous-delivery`: preserved the Implementer boundary, exact structured
  handoff, uncommitted candidate, and prohibition on self-approval/delivery.
- `task-standards`: fixed the approved senior test-automation/accessibility
  persona and production evidence bar.
- `project-orientation`: required the authority, README, control documents,
  existing UI/API/tests/scripts, and no-duplicate search before implementation.
- `test-driven-development`: new contracts/helpers were observed RED before
  implementation; existing UI journeys were recorded honestly when they
  passed characterization on their first product run.
- `verification-before-completion`: all completion claims below are tied to
  fresh command output.
- `systematic-debugging`: browser-launch, teardown, focus-wrap, axe, and
  overflow failures were traced to their causes before changes.
- `sanad`: requirements and implementation choices remain tied to the
  approved plan, project documents, source, or observed output.
- `sanad-provenance`: prevented unsourced package, licence, environment, and
  hosted-action claims; Supervisor-verified facts are identified as such.
- `muhasib`: the final audit covers scope, actual diff, protected paths,
  secrets, tests, limitations, and role boundaries.
- `muhasabah-gate`: required the final fabrication, assumption, scope,
  reversibility, and evidence audit before handoff.

## Resolved dependencies and provenance

| Component | Resolved version/tag | Source and integrity | Licence / disposition |
|---|---|---|---|
| Playwright | `1.62.0` | PyPI lock record; Linux wheel SHA-256 is recorded in `uv.lock` | Apache-2.0, per approved plan and `THIRD_PARTY_NOTICES.md` |
| pytest-playwright | `0.9.0` | PyPI lock record; wheel SHA-256 `9d9dc74e335c647944cecfffa706cc9e6e4bf4c25e84592c128b584d494d4471` | Apache-2.0 |
| Chromium | Playwright revision `1234`; browser `151.0.7922.34` | `~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`; Playwright dry-run metadata and successful launch | Playwright-managed test prerequisite; not committed |
| axe-core | `4.13.0` | `https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz`; registry SRI `sha512-UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A==`; local `axe.min.js` SHA-256 `c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1`; upstream licence SHA-256 `af175b9d96ee93c21a036152e1b905b0b95304d4ae8c2c921c7609100ba8df7e` | MPL-2.0; unmodified vendored distribution |
| actions/cache | `v6.1.0` | Exact hosted-action tag specified by the approved plan and independently verified in `plan_review.md` | Hosted action; no source vendored |
| actions/upload-artifact | `v7.0.1` | Exact hosted-action tag specified by the approved plan and independently verified in `plan_review.md` | Hosted action; no source vendored |
| Arabic font | `fonts-dejavu-core 2.37-8build1` | `fc-match :lang=ar` → DejaVu Sans, `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` | Local OS prerequisite; CI installs `fonts-noto-core` |

`uv.lock` SHA-256 is
`30904a0d7b4a54d64addbf10f9df4ecf05b4e10eadef74d4d945f983ee439bba`.
One intentional `uv lock` run added the separate root `e2e` metadata and ten
transitive records: charset-normalizer, greenlet, playwright, pyee,
pytest-base-url, pytest-playwright, python-slugify, requests, text-unidecode,
and urllib3. Root `dev` remained exactly `httpx` plus `pytest`; no package.json,
npm lock, or `node_modules` was created.

## Changes — unconditional harness/tooling/documentation

- `pyproject.toml`, `uv.lock`: exact separate `e2e` pins and pytest marker;
  default `testpaths = ["tests"]` and two-entry `dev` extra preserved.
- `browser_tests/conftest.py`: explicit/direct prerequisite semantics,
  function-scoped contexts, collector finalization, inherited-FD app fixture,
  artifacts, documentary recorder, and deterministic run summary.
- `browser_tests/harness.py`: fixed case/viewport contracts, server lifecycle,
  failure collector, offline axe injection, keyboard/focus reporting,
  RTL/non-tofu proof, and reference index/budget enforcement.
- `browser_tests/pages.py`: state-based role/label/data-attribute journeys.
- `browser_tests/test_*.py`: the approved 17 tests / 62 nodes.
- `browser_tests/vendor/axe-core-4.13.0/*` and
  `browser_tests/THIRD_PARTY_NOTICES.md`: SHA-verified offline axe bytes,
  upstream MPL-2.0 licence, acquisition metadata, and notices.
- `scripts/check_browser_prerequisites.py`: exact package/browser/axe/font
  fail-fast checks with typed public functions and safe remediation.
- `Makefile`, `.github/workflows/ci.yml`, `.gitignore`: one-command e2e,
  browser tail in `make ci`, independent Ubuntu 24.04 browser job, and ignored
  runtime artifacts.
- `tests/test_browser_harness_contract.py`, `tests/test_ci_contract.py`,
  `tests/test_final_acceptance_contract.py`: browserless toolchain, CI,
  inventory, non-oracle, fail-closed, and truthful-copy contracts.
- `scripts/final_acceptance.sh`: only the approved stale browser/KL-22 copy,
  docs-audit phrase, and exact SHA-verified axe-vendor disposition changed;
  the 42-step guard remains.
- Development/operator/limitations/traceability/ADR/changelog documents:
  S06 setup, evidence, provisional KL-22 closure, OPEN KL-31, five-check
  ADR-007 enumeration, V3-A1–V3-A6 `TESTED`, and `Unreleased` notes.
- `reference-screenshots/v0.2.0/`: 40 bounded documentary WebPs plus index;
  never read or compared by tests.

## Changes — conditional UI fixes

- `src/ior_mvp/static/styles.css`: focused contrast tokens/text mappings,
  reduced-motion handling, and wrapping/intrinsic-width containment.
- `src/ior_mvp/dossier.py`: one standalone dossier metadata colour moved to
  a WCAG-AA custom-property token.
- `tests/test_static_frontend.py`, `tests/test_dossier_contract.py`: focused
  source/API regressions for the observed defects.
- `index.html` and `app.js` were not changed.

## TDD and characterization ledger

| Work item | First observed result | Cause / expected evidence | Minimal implementation or fix | Green evidence |
|---|---|---|---|---|
| Toolchain/Make/CI/vendor contract | 6 failed, 12 passed | S06 extra, directory, target, job and vendor files absent | Exact pins, one lock, vendored axe, Make/CI/gitignore additions | 18 passed at Task 1; final focused set 41 passed |
| Preflight | Initial missing-module collection error, then 4 intended failures | Checker/API absent | Typed package/browser/axe/font checks and clean CLI-based Chromium discovery | 10 passed, clean real preflight |
| Server/collector | 4 intended helper failures | Helper interfaces absent | Bound-FD uvicorn process, allow-listed environment, five-channel collector | Unit contracts green; guardrail self-test passed |
| Server teardown | Browser self-test passed but teardown reported `-15` | POSIX reports requested SIGTERM as `-SIGTERM` | Accept only exit 0 or the requested SIGTERM; forced kill remains failure | Guardrail 1 passed; no inherited-FD child remained |
| Journeys A–D | Existing behavior passed first product run | Honest characterization, not RED | No product change | 15 passed |
| Dossier popup/clipboard/print/PDF | Existing behavior passed first product run | Honest characterization, not RED | No product change | 12 passed |
| Keyboard/focus | 8 failed after all 15 controls were reached | Chromium places focus on noninteractive body once before wrapping | Bounded helper recognition of that non-control transition; exact control inventory unchanged | 8 passed with DOM order, `:focus-visible`, and changed signatures |
| Workspace axe | 4 failed with `color-contrast` | Light-surface text tokens and execution-state text were below 4.5:1 | Focused token mappings and contrast regression | 4 passed, zero violations |
| Dossier axe | 4 failed with `.meta` contrast 4.41:1 | Standalone metadata colour just below 4.5:1 | `--dossier-muted` token with tested contrast | 4 passed, zero violations |
| Reduced-motion axe stability | 1 residual simulated-PP failure after the colour fix | Axe observed an in-flight colour transition because CSS ignored reduced-motion context | Reduced-motion media rule disables transition/animation durations | Workspace axe 4 passed repeatedly |
| RTL/non-tofu | Existing behavior passed first product run | Honest characterization | No product change | 6 nodes passed |
| Responsive matrix | 4 failed, 4 passed | Workspace heading/select intrinsic width overflowed at 1440 and 1024 | Wrap heading, constrain tools/select, stack controls at the existing 1180 breakpoint | 8 passed |
| Untouched references | Baseline `make e2e`: 50 passed, 12 expected product-defect failures | Axe/overflow defects above; all reference nodes still completed | No UI fix until all 40 baseline images and index existed | 40 files, complete index and budgets; post-fix ignored set also captured |
| Final-acceptance wording | 1 intended stale-copy failure | Pre-S06 browser/KL-22 wording remained | Exact approved copy/vendor disposition only | 6 passed |

## UI defect ledger

### S06-UI-01 — Workspace WCAG colour contrast

- Requirement: V3-A5 / NFR-006.
- Before: all four workspace axe nodes reported serious
  `color-contrast`; examples included 3.05:1 teal eyebrow on paper,
  3.23:1 muted labels on white, and 2.72:1 gold execution text on white.
- Root cause: existing accent/muted tokens were used as small foreground text
  on light surfaces.
- Change: `styles.css` adds tested `--teal-text`, `--teal-on-dark`, and
  `--gold-text`; darkens the two muted ink tokens; maps affected text and
  disabled chips to contrast-safe tokens.
- Regression: `test_accessibility_text_tokens_meet_wcag_aa_on_used_surfaces`;
  browser tests #11–#12.
- After: all eight workspace/dossier axe nodes report zero violations.
- Before reference:
  `reference-screenshots/v0.2.0/desktop-1440x900__journey-b-steel-public-workspace.webp`.
- After screenshot:
  `.artifacts/e2e/reference/desktop-1440x900__journey-b-steel-public-workspace.webp`.

### S06-UI-02 — Dossier metadata contrast

- Requirement: V3-A5 / NFR-006.
- Before: all four dossier axe nodes reported `.meta` at 4.41:1.
- Root cause: inline `#667a91` fell just below the AA normal-text threshold.
- Change: `dossier.py` defines and uses `--dossier-muted:#5f7389`.
- Regression: `test_dossier_metadata_uses_a_wcag_aa_design_token`; browser
  test #12.
- After: all four dossier axe nodes report zero violations.
- Before reference:
  `reference-screenshots/v0.2.0/desktop-1440x900__journey-e-steel-public-dossier.webp`.
- After screenshot:
  `.artifacts/e2e/reference/desktop-1440x900__journey-e-steel-public-dossier.webp`.

### S06-UI-03 — Workspace horizontal overflow

- Requirement: V3-A3 / DOD-08.
- Before: document width was 1,538 px at a 1,440 px viewport and 1,445 px at
  a 1,024 px viewport; diagnostics identified `.workspace-tools` and the
  opportunity select as the right-edge source.
- Root cause: the workspace heading did not wrap and the select's intrinsic
  option width could not shrink.
- Change: wrap/constrain the heading tools and select; stack them at the
  existing 1,180 px breakpoint.
- Regression: `test_workspace_heading_can_wrap_without_page_overflow`;
  browser test #15.
- After: all eight responsive nodes report document/body/main widths within
  their clients, with primary controls trial-clickable.
- Before reference:
  `reference-screenshots/v0.2.0/tablet-1024x768__journey-b-steel-public-workspace.webp`.
- After screenshot:
  `.artifacts/e2e/reference/tablet-1024x768__journey-b-steel-public-workspace.webp`.

### S06-UI-04 — Reduced-motion transition state

- Requirement: V3-A5 / stable accessibility evaluation.
- Before: one post-token simulated-PP axe run observed the inactive mode
  button mid-transition at 4.24:1.
- Root cause: the context requested reduced motion but existing CSS
  transitions did not honor that preference.
- Change: reduced-motion media rules set scroll behavior to auto and
  transition/animation durations to zero.
- Regression:
  `test_reduced_motion_context_disables_transient_colour_states`; browser
  axe and keyboard matrices.
- After: complete accessibility matrix passed repeatedly.
- Before/after visual evidence uses the corresponding tracked baseline and
  ignored post-fix simulated-PP workspace captures.

## Reference provenance

The one tracked capture ran before every UI fix:

```text
E2E_REFERENCE_DIR=.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0 make e2e
```

The index records v0.2.0 tag commit `ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6`,
S06 base SHA, Playwright/Chromium/font versions, every image hash/byte count,
and these untouched source hashes:

- `index.html`: `031a50038d3fd2ff7c1113644e8774645ec508e741941b4fc166d847c7298398`
- `app.js`: `ade715f162099353b51aa6958085c310216988f461c5c386adfbd419635d312f`
- `styles.css`: `d9e1843c48d5fc338fa0f335a41854beefe6a8dda42f6bd0e1d0d73fa78030b7`
- `dossier.py`: `24d8ff3f5462fd56c3b54be449ee62c0a9a794cb25f216663483bcd14a48f470`

Count: 40 WebPs. Aggregate: 4,650,022 bytes. Every image is below
512 KiB; aggregate is below 8 MiB. `file` identified every artifact as a
non-zero-dimension WebP. These are documentary references, not comparison
oracles; no test reads an existing committed image or compares one.

## Protected-path and security audit

- `git diff --name-only -- config data docs/core
  docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx
  docs/authority/authority_hashes.json` returned no path.
- Protected hashes sampled at Task 0 remained unchanged; integrity reports
  `INTEGRITY PASS`. No manifest generator ran.
- No config, data, Core, DOCX, hash, golden, threshold, decision-engine,
  capability, economics, evidence, or synthetic-label semantic changed.
- `.env` existence/ignore/tracked state was checked without opening it:
  exists, ignored, untracked. No secret value or environment dump was read or
  printed.
- Application test servers bound only inherited `127.0.0.1:<ephemeral>`
  sockets and received only PATH, HOME, fixed LANG/PYTHONPATH, and
  PYTHONUNBUFFERED.
- Ordinary contexts observed zero console errors, page errors, failed
  requests, app HTTP errors, or external HTTP(S) requests. The one intentional
  external probe was aborted inside the observation-only self-test.
- Raw logs, traces, PDFs, post-fix images, and summaries remain ignored under
  `.artifacts/e2e/`.
- A non-staging invocation of the same scanner logic over all 80 modified or
  untracked candidate/slice-record files (excluding the two prohibited helper
  scripts) returned zero findings.
- The two pre-existing `.workflow/runs/*.sh` files remain untouched and
  untracked.

## Environment deviation, limitations, and recovery

- Ubuntu 26.04 WSL2 lacked local `libnspr4`, NSS, and ALSA runtime libraries,
  contradicting the previously recorded environment expectation. `sudo`,
  `apt`, and Playwright `--with-deps` were not used. For local evidence only,
  those shared libraries were exposed through `LD_LIBRARY_PATH` from the
  already-cached official `mcr.microsoft.com/playwright:v1.62.1-noble` image
  into ignored `/tmp/ior-s06-browser-libs`. No image was pulled, no repository
  byte changed, and the pinned Python Playwright 1.62.0/revision-1234 browser
  still ran. A fresh local shell needs authorized Playwright system
  dependencies; hosted CI installs them explicitly.
- The default suite emits the pre-existing Starlette/httpx deprecation warning;
  all tests pass and S06 does not change that dependency contract.
- KL-31 remains OPEN: `/docs` uses public-CDN Swagger assets. Keyboard coverage
  focuses but never activates the link; S07 owns the offline disposition.
- Hosted action execution, Supervisor review, independent review, staging,
  hosted CI, merge, limitation closure, and release remain unobserved.
- Before commit, rollback is an inverse reviewed patch limited to S06 files;
  ignored runtime output can be removed without changing product state. Do not
  reset or discard unrelated untracked files.

This record is implementation evidence only. It is not approval, delivery,
hosted-CI evidence, merge authorization, or release evidence.

## Fix round 1 ledger

- **SR-01 — runtime version provenance:** Added a RED browserless contract
  that rejected the quoted application-version literal, then replaced the
  health comparison with `ior_mvp.__version__` and generated the Playwright
  and pytest-playwright reference-index values from installed package
  metadata. The focused GREEN run passed.
- **SR-02 — self-contained e2e synchronization:** Added a RED Makefile
  contract, then introduced phony `uv-sync-e2e` with the locked `dev` and
  `e2e` extras and made only `e2e` depend on it. `ci: uv-sync`, `uv-sync`,
  `UV_RUN`, and `.github/workflows/ci.yml` remain unchanged. The focused
  GREEN run passed, and the developer guide now identifies the target.

Fresh verification: default pytest `308 passed, 1 warning`; ordinary
ignored-output `make e2e` `62 passed`; requested compileall exited 0 with no
output. No tracked reference screenshot was recaptured.

## Fix round 2 ledger

- **RV-01 — shallow-checkout-safe release provenance:** Added a RED
  browserless contract that exposed the annotated-tag peel in
  `reference_recorder`, then replaced it with
  `V0_2_0_RELEASE_SHA`. The contract permits only the shallow-safe
  `git_revision("HEAD")` call and checks the constant against the Product
  release SHA in the tracked v0.2.0 reference index. The focused GREEN run
  passed.
- **RO-1 — internally current command record:** Re-ran the combined local CI
  gate after RV-01 and refreshed the Fresh command evidence to record
  309 default tests and 62 browser tests.
- **RO-2 — dossier title oracle:** Strengthened the four case/mode popup nodes
  so the document title must equal the rendered dossier
  `decision_headline` heading, rather than only being non-empty.

Fresh verification: default pytest `309 passed, 1 warning`; ordinary
ignored-output `make e2e` `62 passed`; full `make ci` exited 0 with
309 default tests and 62 browser tests. Both browser executions wrote only to
the ignored `.artifacts/e2e/reference` path. No tracked reference screenshot
was recaptured, and `.github/workflows/ci.yml` was not changed in this round.
