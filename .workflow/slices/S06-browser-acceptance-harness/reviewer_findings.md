# Independent reviewer findings — S06 Real-Browser Acceptance Harness

Reviewer: Grok 4.6 (`cursor-grok-4.6-xhigh`), independent read-only seat.
Implementer: GPT-5.6 Sol (`gpt-5.6-sol-max`).
Supervisor: Claude (`claude-fable-5-1-thinking-max`).
Candidate: uncommitted working tree on `slice/S06-browser-acceptance-harness` at HEAD/base `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`.
Data classification: `confidential_demo`. `.env` existence/ignore/untracked status was checked; contents were not opened or printed.

Skills used (opened with the file-reading tool before verdict):

- `/home/barami/.agents/skills/strict-reviewer/SKILL.md`
- `/home/barami/.cursor/plugins/cache/cursor-public/superpowers/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/requesting-code-review/SKILL.md`
- `/home/barami/.cursor/plugins/cache/cursor-public/superpowers/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/requesting-code-review/code-reviewer.md`
- `/home/barami/.cursor/skills/muhasib/SKILL.md`
- `/home/barami/.agents/skills/sanad-provenance/SKILL.md`

This seat did not modify, stage, commit, or delete any file other than this findings file.

---

## 1. Scope read

Start-of-slice ritual (file-reading tool): `AGENTS.md`; `.cursor/rules/00-authority.mdc`, `10-domain-guardrails.mdc`, `20-proof.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md`; Core 01 journeys/NFR-004/006/007/008; Core 09 §2.6, §2.7, Gate G, §7; UX spec cited via GAP/SLICE; `docs/milestones/v0.3.0/GAP_ANALYSIS.md` area A and R-4; `SLICE_GRAPH.md` S06/S07; ADR-004/007/010.

Slice records: `persona.md`, `context.md`, `plan.md` (full), `plan_review.md`, `implementation_log.md`, `implementation_review.md`, `test_evidence.md`, `reference-screenshots/v0.2.0/index.md`.

Candidate: `git diff` of all 18 modified tracked files; new `browser_tests/` (Python modules, `THIRD_PARTY_NOTICES.md`, `SOURCE.json`, `LICENSE`, axe header); `scripts/check_browser_prerequisites.py`; `tests/test_browser_harness_contract.py`; UI diffs in `styles.css` and `dossier.py`; unchanged `index.html` / `app.js` for locator context. Two pre-existing `.workflow/runs/*.sh` helpers were left unread as out of candidate.

---

## 2. Ground-truth commands (reviewer-run)

Protected paths:

```text
$ git diff --name-only -- config data docs/core docs/authority
(empty)
```

Default suite:

```text
$ PYTHONPATH=src .venv/bin/python -m pytest -q
308 passed, 1 warning in 0.76s
```

The warning is the pre-existing Starlette/`httpx` deprecation. Default collection: `308 tests collected`; `browser_tests` matches in that collection: `0`. Direct `pytest --collect-only -q browser_tests --browser chromium`: `62 tests collected`.

Integrity:

```text
$ PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
```

Smoke:

```text
$ PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Browser gate (with the disclosed local `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs`; `E2E_REFERENCE_DIR` left at the Makefile default `.artifacts/e2e/reference`):

```text
$ export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs && make e2e
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
chromium=.../chromium-1234/chrome-linux64/chrome
axe_sha256=c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1
font_family=DejaVu Sans
62 passed in 62.81s
```

Branch/HEAD: `slice/S06-browser-acceptance-harness` at `d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`. `git diff --check`: empty. `.env` exists, is ignored by `.gitignore:7`, and is not a Git-tracked path; contents were not read.

---

## 3. Per-area verification notes

### Plan inventory and locators

Seventeen named tests exist and collect as 62 Chromium nodes. Domain expectations in `browser_tests/harness.py` match plan §9.3 (steel public/simulated `INVESTIGATE`/`ADVANCE`; PP both `REJECT`; synthetic label exact). Locators use roles, labels, and existing `data-*` attributes; no `data-testid`. Journeys cover cards, select, steel hero, both mode directions, five nav buttons, methodology hero, four popups, four clipboard payloads. `/docs` is in the keyboard inventory as `href:/docs` and is never activated (`assert "/docs" not in page.url`).

### Failure channels, server, axe, RTL, PDF, screenshots

`BrowserFailureCollector` records the five required categories and exposes no ignore/exclude/suppress API. Ordinary journeys use `assert_clean()` with no exclusion path. Child command is `[sys.executable, "-m", "uvicorn", "ior_mvp.app:app", "--fd", ...]` with allow-listed env (`PATH`, `HOME`, `LANG=C.UTF-8`, `PYTHONPATH=<root>/src`, `PYTHONUNBUFFERED=1`). Bind is `127.0.0.1:0`. Health polling uses `time.monotonic` and `urlopen` with no `time.sleep` / `wait_for_timeout`. Health version is `ior_mvp.__version__` (SR-01). Axe is injected from SHA-verified vendored bytes; `AXE_TAGS` are exactly `wcag2a/wcag2aa/wcag21a/wcag21aa`; no `disableRules`. Canvas non-tofu check compares Arabic vs U+FFFD widths and pixel signatures and requires ≥2 distinct glyph signatures. PDF asserts `%PDF-`, stripped `%%EOF`, ≥10240 bytes, and `/Type /Page`. Popup uses `expect_popup()`; clipboard uses real `navigator.clipboard.readText()`. Four viewports as specified.

Reference set: 40 WebPs, 4,650,022 aggregate bytes, max file 245,674 < 512 KiB. Sample SHA matches `index.md`. Tracked `styles.css` / `dossier.py` hashes in the index (`d9e1843c…`, `24d8ff3f…`) differ from the current post-fix files (`f51ea2ca…`, `62d1858f…`); `index.html` / `app.js` hashes match. Capture was therefore before the UI remediations. No `to_have_screenshot`, `pixelmatch`, or URL axe injection in `browser_tests/*.py`.

### Supervisor rulings

PR-01: `e2e` extra is exact pins; `dev` remains `pytest>=8,<9` and `httpx>=0.27,<1`; `uv.lock` root extras match. PR-02: `sys.executable`. PR-03: `/docs` focused not activated; KL-31 OPEN. SR-01: no quoted `0.x.y` application literal in `harness.py`. SR-02: `e2e: uv-sync-e2e` while `ci: uv-sync`.

### Tests vs product regressions

Axe/contrast/overflow/reduced-motion remediations are token-based and paired with new source/API regressions (`test_accessibility_text_tokens_meet_wcag_aa_on_used_surfaces`, `test_workspace_heading_can_wrap_without_page_overflow`, `test_reduced_motion_context_disables_transient_colour_states`, `test_dossier_metadata_uses_a_wcag_aa_design_token`). Existing `tests/` diffs are additive; no skip/xfail/deletion of prior assertions. `index.html` and `app.js` unchanged.

### CI shape

`browser-gates` matches plan §15.1: `ubuntu-24.04`, Python 3.12, `uv sync --locked --extra dev --extra e2e --python "3.12"`, `actions/cache@v6.1.0`, `fonts-noto-core`, `--with-deps chromium`, `make UV=uv e2e`, `actions/upload-artifact@v7.0.1` with exactly one `if: ${{ failure() }}`. Legacy jobs retain `compileall -q src scripts tests` and have no `if`. Default suite remains browser-independent. Explicit gate uses `pytest.fail` when `IOR_E2E_EXPLICIT=1`.

### Security / privacy

No `.env` read in harness/preflight. Child env strips `SECRET_TOKEN`-class parent keys (unit-tested). Bind is localhost. Axe bytes do not match the four prohibited-file secret regexes (`ghp_`, `AKIA`, private-key header, `sk-`). No `/home/barami` in `browser_tests/`, preflight script, Makefile, workflow, `pyproject.toml`, or `src/`. `.gitignore` adds `.artifacts/e2e/`, `test-results/`, `playwright-report/`, `node_modules/` and does not ignore the slice reference folder.

### Documentation

KL-22 is a provisional v0.3.0 closure row; KL-31 is OPEN. V3-A1…A6 are `TESTED`, not `COMPLETE`. ADR-007 enumerates five checks including `browser / Chromium / Python 3.12`. CHANGELOG has `Unreleased` without a 0.3.0 date. `final_acceptance.sh` retains the `STEP_NUMBER != 42` guard and `make_ci`; stale “Browser paint was not executed” / “KL-22 limits product proof” strings are gone; axe vendor disposition is the exact path. `DEVELOPMENT_GUIDE` / `OPERATOR_RUNBOOK` `make e2e` commands match the observed gate. `uv.lock` `dev` extra unchanged.

### Authority

Protected-path diff empty. Integrity PASS. Public goldens unchanged. No `build_manifests.py` evidence. Manifest/core/config/data untouched.

---

## 4. Findings

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | FAILURE_SCENARIO | REQUIRED_REMEDIATION | PROVING_TEST |
|---|---|---|---|---|---|---|---|
| RV-01 | BLOCKER | Plan §7.8 / §8 test #16 (index records v0.2.0 tag/commit); AC-18 / SLICE_GRAPH S06 (“browser job green in CI”); ADR-007 (merge requires `browser / Chromium / Python 3.12` green); `actions/checkout@v4` README: `fetch-depth` default 1, `fetch-tags` default false | `browser_tests/conftest.py:208-209` calls `git_revision("v0.2.0^{}")` during session setup of `reference_recorder`, which every `make e2e` run instantiates because `test_capture_documentary_reference_set` is 4 of 62 collected nodes. `browser_tests/harness.py:411-420` raises `RuntimeError` on any nonzero `git rev-parse`. `.github/workflows/ci.yml:109-112` checkout is only `persist-credentials: false` — no `fetch-tags`, no `fetch-depth`. Observed locally: `git cat-file -t v0.2.0` → `tag` (annotated); `git rev-parse 'v0.2.0^{}'` → `ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6`. `tests/test_ci_contract.py` does not lock tag fetch. | The documentary-capture fixture peels an annotated release tag that the hosted shallow checkout does not fetch. Local 62-pass evidence cannot see this because this clone has tags. | On `browser-gates`, checkout fetches only the PR head commit. Fixture setup raises `unable to resolve Git revision: v0.2.0^{}`. The four capture nodes error, `make e2e` is nonzero, the new required check is red, and ADR-007 forbids merge. | Do not call `git rev-parse v0.2.0^{}` at fixture setup. Prefer a constant `V0_2_0_RELEASE_SHA = "ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6"` (already recorded in the tracked index) locked by a browserless contract against `reference-screenshots/v0.2.0/index.md`. If git resolution is kept, add `fetch-tags: true` to the browser-gates checkout (annotated-tag peel needs the tag object) and assert it in `tests/test_ci_contract.py`. Keep `persist-credentials: false`. Do not recapture the tracked 40 WebPs. | `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_browser_harness_contract.py tests/test_ci_contract.py` plus a tag-absent probe: `git rev-parse` of `v0.2.0^{}` must not be required for `reference_recorder` construction. Hosted proof: `browser-gates` `make e2e` reports `62 passed`. |

Finding count: 1 unresolved.

---

## 5. Residual observations (non-blocking)

- Axe browser tests assert `violations == []` and the contract locks `AXE_TAGS`; they do not assert a non-empty `passes`/`testEngine` payload. A stub `axe.run` returning `{violations: []}` would still be caught by the SHA/licence preflight unless the stub replaced the vendored bytes and `SOURCE.json` together.
- Keyboard wrap helper special-cases one Chromium `body` stop after the 15 controls; the inventory itself is exact.
- Dossier popup title is only asserted non-empty, not equal to `decision_headline`.
- Historical NFR-006/007, TL-07, GATE-G, DOD-08/09 remain `COMPLETE` while citing `S06-LOCAL`; V3-A1…A6 are correctly `TESTED`. Plan §19 asked to update those evidence columns, not to demote them.
- `test_evidence.md` “Fresh command evidence” still quotes `make ci` at 306 pytest nodes; the fix-round section records 308. I observed 308.
- KL-21 rationale still says “S05 does not edit the frontend”; plan §19 forbade changing KL-21 substance. Hex-outside-`:root` remains true.
- `reference_recorder` deletes every `*.webp` in `IOR_E2E_REFERENCE_DIR` at session start. Ordinary `make e2e` uses ignored artifacts. Re-running the provenance command in `index.md` against the slice folder would overwrite the pre-fix v0.2.0 set.
- Legacy `uv-gates`/`pip-gates` compileall still omits `browser_tests` (plan §15.1: do not alter those jobs).
- Health readiness is a tight poll loop rather than `sleep`; that matches the plan’s sleep ban.
- OPERATOR_RUNBOOK still contains pre-existing `/home/barami/...` paths outside this slice (noted by the Supervisor for S21).

---

## 6. Cannot verify

- Hosted `browser-gates` execution (no PR yet). RV-01 is the predicted hosted failure mode from checkout defaults plus the fixture; it is not an observed GitHub log.
- `fc-match :lang=ar` on Ubuntu 24.04 with `fonts-noto-core` (local match is DejaVu Sans).
- `pip-gates` on a `.[dev]`-only interpreter that lacks Playwright. This `.venv` has the `e2e` extra installed. Contract tests import `browser_tests.harness` but not Playwright; risk is low and unproven here.
- Staged `scripts/check_prohibited_files.py` over Git-tracked new files (scanner is tracked-only; axe bytes were grepped against the four secret regexes and were clean).
- Full `make ci` after SR-01/02. I ran default pytest, `make e2e`, integrity, and smoke; I did not rerun the combined Makefile target.

---

## 7. Muhasib

- Scope stayed inside S06 review; no product files were edited except this findings file.
- Claims above are tied to files, diffs, or commands I ran; hosted CI redness is inferred from checkout defaults plus the fixture, and is labelled as such.
- I did not approve implementer or Supervisor summaries; I re-read the candidate and re-ran the mandated gates.
- Residual items are not treated as zero-finding cover.
- Result: `PASS` as a review handoff. This is not an approval of the candidate.

Verdict: REJECT — 1 unresolved

---

## Re-review round 1

Reviewer: Grok 4.6 (`cursor-grok-4.6-xhigh`), same independent seat. First-round text above is unchanged. This section covers only the RV-01 / RO-1 / RO-2 candidate.

### Files re-read

`browser_tests/harness.py` (constant at line 29), `browser_tests/conftest.py` (import and `release_sha=V0_2_0_RELEASE_SHA`), `browser_tests/test_dossier.py` (title equality), `tests/test_browser_harness_contract.py` (`test_reference_fixture_does_not_require_the_release_tag`), `test_evidence.md` (Fresh command table + Fix round 2), `implementation_log.md` (Fix round 2 ledger). Workflow still has no `fetch-tags`. Tracked reference `index.md` and WebP count inspected; current `styles.css` / `dossier.py` hashes compared to the index.

### Ground truth (reviewer-run)

```text
$ git diff --name-only -- config data docs/core docs/authority
(empty)

$ rg -n 'v0\.2\.0\^' browser_tests
(no matches)

$ PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_browser_harness_contract.py
23 passed in 0.03s

$ PYTHONPATH=src .venv/bin/python -m pytest -q
309 passed, 1 warning in 0.76s

$ export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs && make e2e
BROWSER PREFLIGHT PASS
62 passed in 59.60s
```

`E2E_REFERENCE_DIR` remained the Makefile default `.artifacts/e2e/reference`. Tracked reference folder: 40 WebPs, 4,650,022 bytes. Index still lists pre-fix UI hashes `styles.css` `d9e1843c…` and `dossier.py` `24d8ff3f…`; current files hash `f51ea2ca…` and `62d1858f…`. Product-release SHA in the index is `ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6`, equal to `V0_2_0_RELEASE_SHA`. `git_revision` in `conftest.py` is only `git_revision("HEAD")`.

### Dispositions

| ID | Disposition | Evidence |
|---|---|---|
| RV-01 | RESOLVED | Tag peel removed from `browser_tests/`. Fixture uses the constant; contract forbids `v0.2.0^{}` and any `git_revision` argument other than `"HEAD"`, and equals the tracked index SHA. Workflow was correctly left without `fetch-tags`. Local 62-pass `make e2e` no longer depends on annotated-tag objects. |
| RO-1 | RESOLVED | Fresh-command table and Fix round 2 now record 309 default tests and 62 browser nodes. Observed 309 / 62 match. |
| RO-2 | RESOLVED | All four popup nodes assert nonempty `h1` text and `popup.title() == decision_headline`. Renderer uses the same `decision_headline` for `<title>` and `<h1>` (`dossier.py:134,149`). |

### New-defect check

No scope creep into `ci.yml`, Core/config/data, or the tracked 40 WebPs. No assertion was weakened: the new contract is additive; popup title is stricter than nonempty. The SHA constant is release provenance, not a hidden application-version literal; `test_harness_uses_runtime_versions_without_application_literals` still passed. New findings: none.

Residual (not a finding): the historical 3.14 row in the original Fresh-command table still says `306 passed`; Fix round 2 and the 3.12 pytest row are 309. Supervisor separately observed 309 on 3.14.

### Muhasib

Re-read the changed files; re-ran the named gates; did not trust summaries for counts or hashes; did not rewrite round 1; did not recapture references. Result: `PASS` as a review handoff.

Verdict: APPROVE — zero unresolved findings
