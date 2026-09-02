# S06 test evidence — Real-browser acceptance harness

All evidence below is local implementation evidence from the uncommitted
candidate on branch `slice/S06-browser-acceptance-harness` at base/HEAD
`d338f5d9ed49457d3a595b2d1e6b4f0bb7683efc`. Ephemeral server origins are
recorded as `http://127.0.0.1:<ephemeral>`.

## Environment

| Item | Observed value |
|---|---|
| Host | Ubuntu 26.04 LTS under WSL2; kernel `6.6.114.1-microsoft-standard-WSL2` |
| Final active Python | CPython 3.12.13 in `.venv` |
| Compatibility Python | CPython 3.14.4 |
| uv | 0.11.31 |
| Node / npm | 22.22.3 / 10.9.8 |
| Playwright / pytest-playwright | 1.62.0 / 0.9.0 |
| Chromium | Playwright revision 1234; `151.0.7922.34` |
| axe-core | 4.13.0; SHA-256 `c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1` |
| Arabic font | `fonts-dejavu-core 2.37-8build1`; DejaVu Sans; `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` |
| Data classification | `confidential_demo` |

The local WSL image lacked four Chromium runtime library families
(`libnspr4`, NSS, SMIME, ALSA). No `sudo`, `apt`, or
`playwright install --with-deps` command was run. The fresh local evidence
used an ignored `/tmp/ior-s06-browser-libs` `LD_LIBRARY_PATH` assembled from
the already-cached official Playwright Noble image. CI installs supported
system dependencies directly. This environment deviation is not hidden as a
product pass condition.

## Dependency and prerequisite evidence

### Lock

```text
$ uv lock --check
Resolved 39 packages in 0.62ms
exit 0
```

`uv sync --locked --extra dev --extra e2e --python "3.12"` used CPython
3.12.13 and checked 38 installed packages. The resolver records exact
`playwright==1.62.0`, `pytest-playwright==0.9.0`, their transitive graph, and
the unchanged two-entry `dev` extra.

### axe acquisition

- URL:
  `https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz`
- Expected and observed registry SRI:
  `sha512-UzGt8zg7Ny8djbYMhxl2zuEevVa7r2gJjYY5Lwr1xM7+XU2nd6CkIWFTVcCIbAP63vSz71NaVyyuSk9lHKcy0A==`
- Extracted only `axe.min.js` and `LICENSE`; no npm script, package manifest,
  lock, or `node_modules` was created.
- `axe.min.js` SHA-256:
  `c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1`.
- Upstream licence SHA-256:
  `af175b9d96ee93c21a036152e1b905b0b95304d4ae8c2c921c7609100ba8df7e`;
  MPL-2.0.

### Real preflight

```text
BROWSER PREFLIGHT PASS
playwright=1.62.0
pytest-playwright=0.9.0
chromium=/home/barami/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome
axe_sha256=c24f097bd2f451d4f933e8bc7d8d539f8672a2ebcb5cc9f9f3eec8ca9470a0c1
font_family=DejaVu Sans
font_file=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
exit 0
```

With `PLAYWRIGHT_BROWSERS_PATH` pointed to an empty temporary directory,
direct `pytest browser_tests` returned exit 0 with one session-scope skip and
the documented install reason. The same run with `IOR_E2E_EXPLICIT=1`
returned nonzero with a prerequisite error. Explicit gates therefore never
turn a missing browser into a skip.

## Browser inventory and server lifecycle

Final ordinary `make e2e` output:

```text
.............................................................. [100%]
62 passed in 63.14s
exit 0
```

Final `make ci` browser tail:

```text
.............................................................. [100%]
62 passed in 62.74s
exit 0
```

`.artifacts/e2e/run-summary.json` records:

```text
named tests = 17
collected = 62
passed = 62
failed = 0
skipped = 0
explicit gate = true
```

The session fixture pre-bound `127.0.0.1:0`, passed its inherited descriptor
to `[sys.executable, -m, uvicorn, ior_mvp.app:app, --fd, <fd>,
--log-level, warning]`, polled
`http://127.0.0.1:<ephemeral>/api/health` to exact status/version, and sent
SIGTERM during teardown. A process check after focused execution found no
remaining `ior_mvp.app:app --fd` child. No startup or browser fixed sleep is
present.

## Journey matrix

| Path | Public | Simulated |
|---|---|---|
| Portfolio load | two cards/KPIs; steel `INVESTIGATE`, PP `REJECT`; no synthetic label | two cards/KPIs; steel active `ADVANCE`, PP `REJECT`; real states unchanged; exact synthetic label |
| Card buttons | both IDs selected and rendered | both IDs selected and rendered |
| Opportunity select | both target detail and manifest URLs returned 200 | both target detail and manifest URLs returned 200 |
| Steel hero | steel loaded after PP, mode preserved | steel loaded after PP, mode preserved |
| Mode direction | PP preserved public → simulated | PP preserved simulated → public |
| Navigation | five section buttons plus methodology hero reached exact sections | covered on public journey; mode-independent controls |
| Dossier popup | steel/PP ID, mode, state, title, RTL, no warning | steel/PP ID, mode, state, title, RTL, exact warning |
| Clipboard | real Chromium clipboard JSON parsed for both cases | parsed for both cases with exact synthetic disclosure |

Fixed domain expectations observed:

```text
steel/public:    real=INVESTIGATE active=INVESTIGATE
steel/simulated: real=INVESTIGATE active=ADVANCE
PP/public:       real=REJECT      active=REJECT
PP/simulated:    real=REJECT      active=REJECT
label:           SIMULATED — NOT MINISTRY EVIDENCE
```

## Failure-channel evidence

The observation-only self-test recorded exactly:

```text
app-http-error
console-error
external-request
pageerror
requestfailed
```

Every other page and popup used the ordinary enforcing collector. All 61
ordinary nodes completed with zero collector records and zero exclusions.
Non-app HTTP(S) has no allow-list; `data:`, `blob:`, and `about:` do not count
as network origins. The `/docs` link was focused by Tab and never activated.

## Keyboard/focus matrix

| Viewport | Public | Simulated |
|---|---|---|
| 1440×900 | 15/15 in DOM order; all `:focus-visible`; all signatures changed | same |
| 1024×768 | 15/15 in DOM order; all `:focus-visible`; all signatures changed | same |
| 1920×1080 | 15/15 in DOM order; all `:focus-visible`; all signatures changed | same |
| 2560×1440 | 15/15 in DOM order; all `:focus-visible`; all signatures changed | same |

The order was five navigation buttons, two mode buttons, `/docs` API link,
two hero buttons, two case-card buttons, opportunity select, open dossier,
and copy JSON. The next interactive focus after the normal noninteractive
document wrap returned to the first navigation control. Eight ignored
`.artifacts/e2e/focus/*.json` files preserve the before/focused signatures.

## Axe matrix

Vendored SHA-verified bytes were injected with exactly:

```text
wcag2a, wcag2aa, wcag21a, wcag21aa
```

No rule was disabled, excluded, accepted, impact-filtered, or suppressed.

| Surface | Steel public | PP public | Steel simulated | PP simulated |
|---|---:|---:|---:|---:|
| Workspace/full application | 0 | 0 | 0 | 0 |
| Dossier popup | 0 | 0 | 0 | 0 |

Before remediation, workspace nodes reported serious `color-contrast`,
dossier `.meta` reported 4.41:1, and one reduced-motion run caught an
in-flight 4.24:1 mode transition. The defect ledger in `implementation_log.md`
links the retained browser tests, focused source regressions, and before/after
screenshots. Final ignored axe output contains only eight zero-violation
summary files.

## RTL and non-tofu evidence

`fc-match`, `document.fonts.ready`, computed direction/text/box checks, and
canvas proof all passed.

| Surface | Nodes | Arabic width | Equal-count U+FFFD width | Arabic signature | U+FFFD signature | Distinct Arabic glyph signatures |
|---|---:|---:|---:|---|---|---:|
| Workspace public | 7 | 492.4921875 | 1181.25 | `5288:8:493:4:52:1026718327` | `25487:5:1185:0:44:2120594254` | 3 |
| Workspace simulated | 7 | 492.4921875 | 1181.25 | different from U+FFFD | different from Arabic | 3 |
| Each dossier case/mode | 1 | 492.4921875 | 1181.25 | different from U+FFFD | different from Arabic | 3 |

Every visible RTL node contained Arabic-range text, computed `direction: rtl`,
and had a non-zero bounding box. Six ignored RTL summaries preserve the
metrics.

## Print and PDF matrix

Every dossier matched print media, had a white body, no `.page` shadow or
screen max-width, zero page margin, and no page-level horizontal overflow.

| Case/mode | Bytes | `/Type /Page` objects | `%PDF-` | `%%EOF` | Ignored path |
|---|---:|---:|---|---|---|
| Steel/public | 39,573 | 2 | PASS | PASS | `.artifacts/e2e/pdf/steel-public.pdf` |
| Steel/simulated | 45,810 | 2 | PASS | PASS | `.artifacts/e2e/pdf/steel-simulated.pdf` |
| PP/public | 34,289 | 1 | PASS | PASS | `.artifacts/e2e/pdf/polypropylene-public.pdf` |
| PP/simulated | 39,658 | 2 | PASS | PASS | `.artifacts/e2e/pdf/polypropylene-simulated.pdf` |

All exceed 10,240 bytes and were produced with A4,
`print_background=True`, and `prefer_css_page_size=True`.

## Responsive matrix

Both modes passed at 1440×900, 1024×768, 1920×1080, and 2560×1440:
document/body/main scroll width did not exceed client width; the mode group,
opportunity selector, open-dossier button, and copy-JSON button were visible;
all actionable controls were enabled and passed `click(trial=True)`.

The first run exposed 1,538 px document width at 1,440 and 1,445 px at 1,024.
After the focused wrap/intrinsic-width fix, all eight nodes passed. Ignored
responsive JSON preserves the dimensions and offenders list.

## Documentary references

The untouched v0.2.0 capture was executed before any UI fix:

```text
E2E_REFERENCE_DIR=.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0 make e2e
```

Its expected characterization result was 50 passed / 12 product-defect
failures; all four reference nodes still ran. The tracked index proves:

```text
files = 40 WebPs
aggregate = 4,650,022 bytes
individual maximum allowed = 524,288 bytes
aggregate maximum allowed = 8,388,608 bytes
index = .workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0/index.md
```

`file` identified all 40 captures as non-zero-dimension WebP images. The index
contains source/browser/font provenance and each image's SHA-256/byte count.
No test compares the images; ordinary post-fix capture writes 40 equivalents
to ignored `.artifacts/e2e/reference/` (4,682,264 bytes).

## Fresh command evidence

| Command | Exit / observed result |
|---|---|
| `uv lock --check` | 0; 39 packages resolved |
| `uv sync --locked --extra dev --extra e2e --python "3.12"` | 0; CPython 3.12.13, 38 packages |
| `uv run --locked --extra dev --extra e2e python scripts/check_browser_prerequisites.py` | 0; PASS with exact versions/hash/font |
| focused browserless contracts including packaging | 0; final rerun 41 passed |
| `make e2e` | 0; 62 passed, 0 skipped |
| `make ci` | 0; fresh post-RV-01 run: scanners/compile/Node/integrity/Gate B/309 pytest/smoke/preflight/62 browser all passed |
| `PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py` | 0; `INTEGRITY PASS` |
| `PYTHONPATH=src .venv/bin/python -m pytest -q` / locked equivalent | 0; fresh post-RV-01 rerun 309 passed, one pre-existing warning |
| `PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py` | 0; `SMOKE PASS` |
| `PYTHONPATH=src uv run --locked --extra dev python scripts/validate_scenarios.py` | 0; `SCENARIO VALIDATION PASS (2 scenarios)` and both ground-truth back-tests PASS |
| `uv run --locked --extra dev python scripts/check_prohibited_files.py` | 0; PASS on 181 tracked files |
| `uv run --locked --extra dev python scripts/check_threshold_literals.py` | 0; PASS, 13 Python files / 23 configured numeric values |
| `uv run --locked --extra dev python -m compileall -q src scripts tests browser_tests` | 0; no output |
| `node --check src/ior_mvp/static/app.js` | 0; no output |
| `git diff --check` | 0; no output |
| `uv sync --locked --extra dev --python "3.14"` then default pytest | 0; 306 passed with the pre-existing Starlette warning |
| restore `uv sync --locked --extra dev --extra e2e --python "3.12"` | 0; final active environment restored |

The system `pytest` command was unavailable, so the mandated Python proof
commands used the locked `.venv/bin/python` or `uv run` interpreter, as
authorized by the plan. The only warning was Starlette's existing httpx
deprecation notice.

## Golden, protected-path, and scan evidence

- `INTEGRITY PASS`.
- Gate B: two scenarios PASS; both ground-truth back-tests PASS.
- Smoke: steel public `INVESTIGATE`; steel simulated `ADVANCE` with real state
  unchanged; PP public `REJECT` generic capacity; extraction 100%.
- No `config/**`, `data/**`, `docs/core/**`, methodology DOCX,
  `authority_hashes.json`, snapshot manifest, golden expectation, or engine
  semantic changed. `scripts/build_manifests.py` was never run.
- `.env` was not read; only exists/ignored/untracked booleans were checked.
- The scanner API was also run without staging over all 80 modified or
  untracked candidate/slice-record files except the two prohibited helper
  scripts: zero findings.
- The prohibited-file scanner intentionally reads Git-tracked files only.
  At Implementer handoff, all new S06 files remain untracked, so its current
  PASS does not cover them. The Supervisor must stage exactly the approved
  candidate paths and rerun the scanner before commit.

This is local implementation evidence. It does not claim Supervisor review,
independent review, hosted CI, staging, commit, merge, effective KL-22 closure,
project completion, tag, or release.

## Fix round 1

SR-01 and SR-02 were exercised browserlessly before implementation. The
focused RED run returned `2 failed`: the harness still contained the quoted
application version `"0.2.0"`, and the Makefile lacked `uv-sync-e2e`. The
focused GREEN rerun returned `2 passed`; the final contract shape has two new
test nodes, one for each finding.

Fresh command evidence:

- `PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src pytest -q` exited 0:
  `308 passed, 1 warning in 0.80s`. The warning is the pre-existing
  Starlette/httpx deprecation.
- `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e` exited 0. The new
  prerequisite ran
  `uv sync --locked --extra dev --extra e2e`, preflight reported
  `BROWSER PREFLIGHT PASS`, and Chromium reported
  `62 passed in 60.71s`.
- The browser command used the ordinary ignored
  `IOR_E2E_REFERENCE_DIR=".artifacts/e2e/reference"`; the tracked documentary
  reference directory was not passed or recaptured.
- `PATH="$PWD/.venv/bin:$PATH" python -m compileall -q browser_tests tests`
  exited 0 with no output.

This fix-round evidence remains local implementation evidence only.

## Fix round 2

RV-01 was exercised RED→GREEN with
`test_reference_fixture_does_not_require_the_release_tag`. The RED run failed
because `conftest.py` contained `git_revision("v0.2.0^{}")`. After replacing
that lookup with `V0_2_0_RELEASE_SHA`, the focused GREEN run returned
`1 passed`. The contract permits only `git_revision("HEAD")` in the fixture
and proves the constant equals the tracked index Product release SHA
`ce5786b423f2b5de81e13a73c1fbe57da2a8f5e6`; it therefore supplies the
minimum requested tag-independence proof without recapturing references. A
separate clone was not used because this uncommitted candidate would not be
present in a clone of `HEAD`.

RO-2 strengthened all four dossier popup nodes: each popup title must now
equal its rendered dossier `decision_headline` `h1`, rather than merely being
non-empty.

Fresh post-fix command evidence:

- `PYTHONPATH=src .venv/bin/python -m pytest -q` exited 0:
  `309 passed, 1 warning in 0.77s`.
- `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e` exited 0:
  `BROWSER PREFLIGHT PASS` and `62 passed in 61.95s`.
- `LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make ci` exited 0:
  prohibited-file and threshold scans passed; compileall and Node checks
  passed; integrity, both scenario back-tests, smoke, and preflight passed;
  default pytest reported `309 passed, 1 warning in 0.79s`; Chromium reported
  `62 passed in 61.41s`.
- Both browser runs used the ordinary ignored
  `IOR_E2E_REFERENCE_DIR=".artifacts/e2e/reference"`. The tracked documentary
  reference set was not passed, modified, or recaptured.

This fix-round evidence remains local implementation evidence only and does
not replace independent review or hosted CI.
