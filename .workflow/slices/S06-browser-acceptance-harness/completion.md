# Completion — S06 Real-Browser Acceptance Harness

**State:** MERGED (2026-09-02). Merge commit `6d00e27ff156e1342d488495c7b48e68eeefe100`; PR #8; PR CI run 33602331107 (5/5); default-branch CI run 33602662668 (5/5).

## Delivered

- Exact-pinned `e2e` extra (playwright 1.62.0, pytest-playwright 0.9.0) separate from the unchanged `dev` extra; `uv.lock` re-locked once.
- `browser_tests/`: 17 named tests / 62 Chromium nodes over both cases and both evidence modes — selection paths, mode switch, navigation, dossier popup, real clipboard, print media and Chromium PDF structure, 15-control Tab order with `:focus-visible`, axe WCAG 2.1 A/AA (vendored, SHA-verified axe-core 4.13.0, MPL-2.0, no exclusions), Arabic RTL with canvas non-tofu proof, four viewports, five failure channels with a self-test.
- Bound-FD uvicorn fixture launched with `sys.executable` and an allow-listed environment; health polling; SIGTERM teardown; no sleeps.
- `scripts/check_browser_prerequisites.py`; `make e2e`, `make uv-sync-e2e`; `make ci` browser tail; hosted job `browser / Chromium / Python 3.12` (fifth required check under ADR-007).
- 40 documentary WebP references of the pre-fix v0.2.0 UI with a hashed index under this slice record (owner ruling R-4: never compared; governed baselines begin in S07).
- Four browser-revealed UI defects fixed minimally with tokens and paired regressions (workspace contrast, dossier `.meta` contrast, 1,538 px overflow at 1,440 px, reduced-motion transient). `index.html`/`app.js` unchanged.
- Documentation: DEVELOPMENT_GUIDE, OPERATOR_RUNBOOK, KNOWN_LIMITATIONS (KL-22 closed on this merge; KL-31 opened for the CDN-backed `/docs` page → S07), REQUIREMENTS_TRACEABILITY (V3-A1..A6 `TESTED`; Gate G/TL-07 scope updated), ADR-007 five checks, CHANGELOG `Unreleased`, truthful `final_acceptance.sh` wording (42 steps kept).

## Review trail

- Plan: 2 rounds — PR-01 (separate `e2e` extra), PR-02 (`sys.executable`), PR-03 (`/docs` link never activated; KL-31), RI-01 (Sanad ledger counts) → PLAN_APPROVED.
- Supervisor implementation review: SR-01 (application-version literal in health wait), SR-02 (`e2e` depended on dev-only sync) → fixed; negative contrast probe confirmed the gate fails on a real defect.
- Independent review (Grok 4.6): RV-01 BLOCKER — `git rev-parse v0.2.0^{}` at fixture setup would fail on the shallow tag-less hosted checkout (confirmed by the Supervisor in a `--depth 1 --no-tags` clone) → fixed with `V0_2_0_RELEASE_SHA` locked to the tracked index; RO-1 evidence consistency and RO-2 popup-title equality also done → re-review **APPROVE — zero unresolved findings**.

## Evidence

- Local (Supervisor-run on the staged candidate): `make ci` exit 0; `309 passed` on Python 3.12 and 3.14; `62 passed` browser nodes; integrity PASS; Gate B PASS; smoke PASS; prohibited scan 245 tracked files PASS; threshold scan PASS.
- Hosted: PR run 33602331107 and main run 33602662668, five jobs each, all green.

## Carried forward

- KL-31 (OPEN → S07): `/docs` Swagger UI loads assets from a public CDN.
- Local developer note: this WSL host lacks Chromium shared libraries; `make e2e` needs authorized `playwright install --with-deps` or an equivalent library path (documented in DEVELOPMENT_GUIDE). CI installs them.
- `docs/OPERATOR_RUNBOOK.md` still contains two pre-existing absolute `/home/barami/...` paths from S05 → S21 documentation slice.
- Hosted fontconfig preferred DejaVu Sans over Noto for `:lang=ar`; the non-tofu check passed, but S07 (which adds an offline Arabic-capable font stack) should assert the intended product font is the one rendered.
- Traceability rows V3-A1..A6 are promoted from `TESTED` to `COMPLETE` in the next slice's records now that PR CI and default-branch CI are observed.
