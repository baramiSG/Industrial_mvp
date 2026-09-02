# Supervisor Implementation Review — S06 Real-Browser Acceptance Harness

Reviewer: Supervisor (Claude, `claude-fable-5-1-thinking-max`). Implementer: agent 25e87e27 (GPT-5.6 Sol, `gpt-5.6-sol-max`). Candidate: uncommitted working tree on `slice/S06-browser-acceptance-harness` at base `d338f5d`; 76 changed/added paths (18 tracked modifications, `browser_tests/`, `scripts/check_browser_prerequisites.py`, `tests/test_browser_harness_contract.py`, 40 documentary WebPs + index, two slice records).

## What I inspected (2026-09-02)

- Complete `git diff` of the 18 tracked files (`ci.yml`, `.gitignore`, `CHANGELOG.md`, `Makefile`, ADR-007, `DEVELOPMENT_GUIDE`, `KNOWN_LIMITATIONS`, `OPERATOR_RUNBOOK`, `REQUIREMENTS_TRACEABILITY`, `pyproject.toml`, `final_acceptance.sh`, `dossier.py`, `styles.css`, four test files, `uv.lock` summary).
- New files read in full: `browser_tests/conftest.py` (212 lines), `browser_tests/harness.py` (1,047 lines), `scripts/check_browser_prerequisites.py` (260 lines); `browser_tests/vendor/axe-core-4.13.0/SOURCE.json`, `LICENSE` head and `axe.min.js` header; `implementation_log.md` in full; `test_evidence.md` structure.
- Protected paths: `git diff --name-only -- config data docs/core docs/authority` → none. No manifest generator ran; integrity PASS.
- Provenance: vendored `axe.min.js` SHA-256 `c24f097b…a0c1` matches `SOURCE.json`; file header `axe v4.13.0 Copyright Deque Systems`; MPL-2.0 licence present; registry SRI equals the value I verified independently at plan review.
- Machine-specific paths: none in `browser_tests/`, the preflight script, `Makefile`, `ci.yml` or `pyproject.toml`. The `LD_LIBRARY_PATH` workaround the implementer used locally (Chromium shared libraries exposed from a cached public `mcr.microsoft.com/playwright` image into ignored `/tmp/ior-s06-browser-libs`, because this WSL host lacks `libnspr4`/NSS/ALSA and `sudo` is interactive) touched no repository byte and is disclosed in the log; CI installs the libraries with `--with-deps`. `docs/OPERATOR_RUNBOOK.md` still carries two pre-existing S05 `cd /home/barami/...` lines — outside S06 scope, carried to S21.

## Verification I ran myself

| Check | Result |
|---|---|
| `PYTHONPATH=src .venv/bin/python -m pytest -q` (Python 3.12.13) | `306 passed, 1 warning` (280 pre-existing + 26 new browserless contracts) |
| `pytest --co` default collection contains `browser_tests` | 0 nodes — default suite is browser-independent |
| `uv lock --check` | resolved, lock current |
| `make ci` with `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs` | exit 0: prohibited scan, threshold scan, compile (incl. `browser_tests`), `node --check`, `INTEGRITY PASS`, Gate B PASS, 306 passed, `SMOKE PASS`, `BROWSER PREFLIGHT PASS` (playwright 1.62.0, pytest-playwright 0.9.0, chromium-1234, axe SHA, DejaVu Sans), **62 passed in 60.65 s** |
| `.artifacts/e2e/run-summary.json` | collected 62, passed 62, failed 0, skipped 0, explicit_gate true, 17 named tests |
| Negative probe (gate meaningfulness): reverted `--teal-text` to the pre-fix `#0f9f91` and ran `test_workspace_has_zero_wcag_21_aa_axe_violations` | FAILED with `id: color-contrast` (exit 1) — the gate detects the real defect; `styles.css` restored, SHA `f51ea2ca…` equals the implementer's recorded hash |
| Reference set | 40 WebPs, 4.6 MB total, index present; captured before the UI fixes (index records the pre-fix `styles.css`/`dossier.py` hashes); no test reads them |

## Plan conformance

- Tooling, `e2e` extra separate from `dev` (PR-01), `sys.executable` child (PR-02), `/docs` link focused-not-activated and KL-31 OPEN (PR-03): all implemented as ruled.
- Failure hooks, bound-FD server, health polling without sleeps, one context per node, axe with WCAG 2.1 A/AA tags and no exclusions, canvas non-tofu check, `page.pdf` structural assertions, popup and real clipboard: match plan §7.
- 17 tests / 62 nodes match plan §8 exactly.
- Four UI fixes are genuine defects revealed by the gate (three axe `color-contrast` findings on workspace/dossier, one real horizontal overflow of 1,538 px at a 1,440 px viewport, one reduced-motion transient), each minimal, token-based, paired with a source/API regression and recorded with before/after evidence. `index.html` and `app.js` unchanged.
- Documentation, traceability (V3-A1..A6 at `TESTED`), KL-22 provisional closure, ADR-007 five checks, CHANGELOG `Unreleased`, truthful `final_acceptance.sh` copy: present.

## Findings

| ID | Severity | Requirement | Evidence | Problem | Required correction |
|---|---|---|---|---|---|
| SR-01 | LOW | Plan §7.1 health contract; maintainability of a gate; AGENTS.md "no hidden literals" spirit | `browser_tests/harness.py:948` `payload.get("version") == "0.2.0"`; `harness.py:334-335` index lines `Playwright package: 1.62.0`, `pytest-playwright package: 0.9.0` | The health wait embeds the application release string. At the S22 bump to 0.3.0 the entire browser gate would fail for a non-defect. The index embeds package versions as literals rather than the installed metadata. | Compare `payload["version"]` with `ior_mvp.__version__` (import from `src`, which is on `PYTHONPATH`), and write the two package versions from `importlib.metadata.version(...)` (or the `PreflightReport`). Add a browserless contract assertion in `tests/test_browser_harness_contract.py` that `harness.py` contains no quoted application-version literal. |
| SR-02 | LOW | Plan §16 (`e2e` self-contained); ADR-004 | `Makefile`: `e2e: uv-sync` and `uv-sync: $(UV) sync --locked --extra dev`; observed in `make ci` output "Installed 10 packages in 9ms" at the preflight step | `uv sync --locked --extra dev` is exact and removes the ten `e2e` packages; `uv run --extra e2e` then reinstalls them on every run. Functionally self-healing but churns the environment and makes `make e2e` depend on a sync that does not include its own extra. | Add `uv-sync-e2e: $(UV) sync --locked --extra dev --extra e2e` and make `e2e` depend on it; leave `ci: uv-sync` and the legacy `UV_RUN` untouched (the e2e tail of `ci` still self-heals through `uv run --extra e2e`). Assert the new target in `tests/test_browser_harness_contract.py` and mention it in `DEVELOPMENT_GUIDE`. |

No BLOCKER/HIGH/MEDIUM findings. Both LOW findings are to be fixed before the independent review so the reviewed candidate is final.

## Round 2

Implementer (same agent) fixed SR-01 and SR-02. Supervisor verified in the files: `harness.py:20` imports `ior_mvp.__version__` and `:953` compares the health payload to it; `harness.py:15` imports `importlib.metadata.version` for the index package lines; no `"0.2.0"` literal remains in `harness.py`; `Makefile` gains `uv-sync-e2e` (line 41) with `e2e: uv-sync-e2e` (line 47) while `ci: uv-sync` and `UV_RUN` are unchanged; contract assertions added RED→GREEN in `tests/test_browser_harness_contract.py`; one sentence added to `DEVELOPMENT_GUIDE`. Tracked reference set untouched (40 WebPs, same directory state).

Supervisor re-verification: `PYTHONPATH=src pytest -q` → `308 passed`; `make e2e` → `62 passed in 60.43 s`.

Candidate identity captured for the independent review: 81 candidate paths (18 tracked modifications plus new files, excluding the two untracked `.workflow/runs/*.sh` helpers), SHA-256 list at `/tmp/s06_candidate_hashes.txt`, list digest `3573d58b0305bfafa1d585de22fdf0559b7a8bcefc1e405d5ea8837306ab2d49`. The identity is re-verified after the reviewer's verdict before any staging.

Unresolved Supervisor findings: **0**. Handing to the independent reviewer (Grok 4.6).
