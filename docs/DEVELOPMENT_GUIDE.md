# Development Guide

## Authority and data boundary

Development uses repository code, frozen public evidence, and explicitly synthetic Class-D fixtures. No API key or live industrial source is required. Never run the manifest generator outside an approved Authority Manifest §7 change. The active slice ADR and PR must identify the exact governed bytes, approval basis, sensitivity/golden proof, and permitted generated diff before one controlled run.

## PublicSnapshot schema 2.0.0

Production discovery is deliberately non-recursive over
`data/snapshots/public/*.json` and accepts only validated schema `2.0.0`.
Historical schema-v1 files remain byte-identical under
`data/snapshots/public/historical/v1/`; they are integrity-manifest inputs,
not runtime cases. A representation-only migration keeps snapshot ID and
as-of date and uses `supersedes`; a real evidence refresh receives a new ID
and date.

Schema-v2 public records contain typed trade quality, optional partner rows or
source-attributed disclosed concentration/dispersion, domestic flows,
criticality designation, producer evidence, typed hard gates, and complete
evidence passports. Exact `UNAVAILABLE` is the only unknown sentinel in new
blocks. Authored outcomes (`rule_context`, `fired`, `execution`, or equivalent)
are rejected. R3, R4-D, R5, R9-S, R10, and R11 are computed from evidence;
R5 public production/re-export inputs remain `UNAVAILABLE` until a governed
acquisition supplies them.

For an approved schema/config/Core update, complete every governed hand edit
and all functional regression first. Run
`PYTHONPATH=src .venv/bin/python scripts/build_manifests.py` once, audit the
exact machine diff, copy machine rows into Manifest §11, then rerun integrity,
goldens, Gate B, smoke, and the full suites. Historical files are never
rewritten to make hashes pass.

## Prerequisites

Use WSL or native Linux with Python 3.11 or newer, Git, Make, Node, and `uv`. Docker is required for image/runtime compatibility checks and canonical visual-baseline updates. Real-browser acceptance additionally uses Python 3.12, `playwright==1.62.0`, `pytest-playwright==0.9.0`, `Pillow==12.3.0`, matching Playwright Chromium, and the exact vendored Noto Sans/Noto Sans Arabic assets. Host `fc-match` output is diagnostic only; product-font bytes and actual browser rendering are the gate.

The Makefile defaults to `NODE ?= node`. If Node is user-scoped:

```bash
make NODE="$HOME/.local/node/bin/node" ci
```

The Makefile invokes `$(HOME)/.local/bin/uv` unless overridden:

```bash
make UV=uv ci
make UV=/path/to/uv ci
```

Do not edit shell startup files merely to run the build.

## Install uv without changing shell profiles

```bash
curl -LsSf https://astral.sh/uv/install.sh \
  | env UV_NO_MODIFY_PATH=1 sh
"$HOME/.local/bin/uv" --version
make uv-sync
```

## Local CI-equivalent gates

```bash
make ci
```

The target executes:

1. locked development-environment sync;
2. prohibited tracked-file and deterministic credential-pattern scan;
3. configured-threshold comparison-literal scan;
4. bilingual catalogue, token, copy, and logical-direction contracts;
5. Python compilation;
6. recursive ES-module syntax;
7. governed-file integrity;
8. Gate B scenario policy/reconciliation/ground-truth back-test;
9. full pytest;
10. domain/extraction smoke;
11. real-Chromium prerequisite validation, 118 functional nodes, and four visual nodes comparing 40 governed baselines.

Any nonzero exit blocks review. Manifest generation is not a routine gate.

## Real-browser acceptance

Install the separate browser-test environment without changing the preserved
`dev` extra:

```bash
uv sync --locked --extra dev --extra e2e --python "3.12"
uv run --locked --extra dev --extra e2e \
  python -m playwright install chromium
make e2e
```

The `uv-sync-e2e` target installs the locked `dev` and `e2e` extras used by `make e2e`. Use `make e2e-functional` for the 118 nonvisual nodes and `make e2e-visual` for the four comparison nodes. Ordinary comparison is Docker-free.

On a Linux host where package installation is authorized, Playwright can
install its system dependencies with:

```bash
uv run --locked --extra dev --extra e2e \
  python -m playwright install --with-deps chromium
```

Do not use `--with-deps` where `sudo` is unavailable or unauthorized. The
host must instead provide Playwright's documented Chromium libraries and an
Arabic-capable browser libraries. CI runs the authorized `--with-deps`
command on Ubuntu 24.04; the application supplies its own SHA-verified fonts.

`make e2e` starts the application on a kernel-assigned `127.0.0.1` port,
waits for `/api/health`, runs headless Chromium, and terminates the child
server. It fails rather than skipping when packages, Chromium, vendored
axe-core, its MPL-2.0 licence, asset integrity, or Arabic font coverage is
missing. Direct diagnostic `pytest browser_tests` may skip at session scope
when prerequisites are absent; it is not an acceptance gate.

The browser suite is top-level `browser_tests/`, outside the default
`testpaths = ["tests"]`, so the normal pytest and `.[dev]` paths remain
browser-independent. Runtime output is ignored under `.artifacts/e2e/`:
server logs, retained-on-failure traces/screenshots, axe diagnostics, PDFs,
and visual diffs. The 40 tracked v0.2.0 WebPs under the S06 slice record are
documentary references only and remain untouched. The executable oracle is
the 40-image v0.3.0 matrix under `browser_tests/baselines/v0.3.0/`.

## Bilingual interface contracts

`config/ui_strings.v1.yaml` is a hashed operating artifact. English and
Arabic key and placeholder sets must remain identical, values must be
non-empty NFC strings, and policy warning labels must not be duplicated
there. `GET /api/ui-strings/{locale}` serves one complete validated bundle;
invalid locale returns `UI_LOCALE_NOT_FOUND`, while catalogue corruption
fails closed without a partial bundle.

The browser locale precedence is URL `locale` → `localStorage["ior.locale"]`
→ `en`. The switch updates the document `lang`/`dir`, URL, storage, static
chrome, and cached dynamic content atomically. Normalized analytical values
use Western digits and Gregorian dates in both locales; original source spans
remain verbatim. Engine-authored English narrative remains visibly captioned
and isolated with `lang="en" dir="ltr"` in Arabic UI.

`src/ior_mvp/static/styles.css` is an import façade. Raw colours, dimensions,
font values, shadows, radii, motion, z-index values, and breakpoints live only
in `css/tokens.css`; component CSS uses variables and logical properties.
Run:

```bash
.venv/bin/python scripts/check_ui_contracts.py
.venv/bin/python scripts/check_es_modules.py --node node
```

Every production JavaScript file is a named-export ES module with at most 199
physical lines. The recursive syntax checker parses every module through
Node's module grammar.

## Governed visual baselines

The fixed matrix is ten principal screens × English/Arabic × 1440×900 and
1024×768. Baselines are opaque RGB, lossless WebP, SHA-256 indexed, at most
600 KiB each and 12 MiB in aggregate. A pixel is significant only when its
maximum channel delta is greater than 8; both significant-pixel ratio ≤0.001
and mean absolute channel error ≤0.20 must pass. Mismatches write normalized
actual, amplified diff, and JSON metrics under
`.artifacts/e2e/visual-diffs/`.

Updates are never run in CI or on the host renderer:

```bash
make e2e-functional
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="<review-reference>" \
make e2e-update-baselines
make e2e
```

The update target uses the digest-pinned Playwright 1.62.0 Noble image,
asserts `chromium-1234`, mounts only allow-listed project paths, and runs with
`--network=none` as the host UID/GID. It sets its home/cache under `/tmp`,
uses `/ms-playwright`, asserts the effective container identity, and rejects
an update if any written baseline/artifact path is not owned by the host user.
Inspect every image and manifest change before review.

For S08, after all 118 functional nodes are green, the governed update is:

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S08-computed-rules-dossier-contradictions" \
make e2e-update-baselines

PYTHONPATH=src .venv/bin/python -c 'import os; from pathlib import Path; roots=(Path("browser_tests/baselines/v0.3.0"), Path(".artifacts/e2e")); bad=[str(p) for root in roots for p in (root, *root.rglob("*")) if p.exists() and os.stat(p, follow_symlinks=False).st_uid != os.getuid()]; assert not bad, bad'
make e2e
```

Focused examples:

```bash
IOR_E2E_EXPLICIT=1 PYTHONPATH=src \
  uv run --locked --extra dev --extra e2e pytest -q \
  browser_tests/test_dossier.py --browser chromium

IOR_E2E_EXPLICIT=1 PYTHONPATH=src \
  uv run --locked --extra dev --extra e2e pytest -q \
  browser_tests/test_accessibility.py --browser chromium
```

## Final acceptance

```bash
bash scripts/final_acceptance.sh
```

Run it detached under the active slice protocol and read the complete outer log plus `.workflow/slices/S05-final-acceptance/acceptance_results.md`. The 42-step runner adds a clean pip environment, Docker run/health, live HTTP journeys, median-of-five NFR-005 measurements, failure paths, restart, isolated revert/abort, repeated scans, documentation/source-archive checks, and per-hit keyword dispositions.

The script reports local evidence only. It does not approve review, hosted CI, merge, project completion, or tagging.

## Source packaging

```bash
make package
```

Packaging must run from the project-root Git working tree. The script reads the archive member list from `git ls-files -z`, so only tracked working-tree files are included. Untracked and ignored local files such as `.env`, `.venv`, `.git`, and `.workflow/logs` are outside the package input rather than maintained as an exclusion list.

## Preserved clean pip path

```bash
python3 -m venv --clear .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python scripts/check_ui_contracts.py
python -m compileall -q src scripts tests
python scripts/check_es_modules.py --node node
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src python scripts/validate_scenarios.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
```

## Lock maintenance

`pyproject.toml` is the dependency and package-metadata source. The `dev`
extra remains pytest/httpx only; Pillow, Playwright, and pytest-playwright
belong to the separate exact-pinned `e2e` extra. Regenerate `uv.lock` only
after an intentional change:

```bash
"$HOME/.local/bin/uv" lock
"$HOME/.local/bin/uv" sync --locked --extra dev
```

Do not use opportunistic `--upgrade`. Review the complete lock diff. For S05 release metadata, only the editable root package version may change.

## Docker compatibility

```bash
docker build --file Dockerfile \
  --tag industrial-opportunity-resolution-mvp:local .
docker run -d --name ior-local \
  -p 127.0.0.1:8001:8000 \
  industrial-opportunity-resolution-mvp:local
curl --fail --silent --show-error \
  http://127.0.0.1:8001/api/health
docker stop ior-local
docker rm ior-local
```

## Slice workflow

Each bounded slice follows:

1. create the recorded `slice/SXX-name` branch from `main`;
2. read authority, core, control records, current code/tests, and adopt the slice persona;
3. a different-model Planner writes `plan.md`;
4. the Supervisor reviews until zero plan findings and records `PLAN_APPROVED`;
5. the Implementer executes the approved plan test-first and records evidence without self-approval;
6. the Supervisor reviews the complete diff;
7. a model different from the Implementer performs read-only independent review;
8. valid findings return to the Implementer, followed by focused/full tests and review of fixed work;
9. fresh local gates and explicit-path staging are performed;
10. the Supervisor controls commit, push, PR, current-head CI, ADR-007 gate, squash merge, and durable-state updates.

No subagent approves or merges its own work. A green pipeline is evidence, not approval.

## Authority-change procedure

Edits to hashed config, `data/**`, `docs/core/**`, the methodology, a golden expectation, or another governed artifact are not ordinary refactors.

1. Classify the change under Authority Manifest §7.
2. Record rationale, scope, owner approval, and affected golden cases in the active ADR, plan, and PR.
3. Add deterministic boundary/sensitivity and unchanged-golden tests before changing governed bytes.
4. Audit the exact hand diff and protected paths.
5. Run every allowed pre-generation gate.
6. Run the manifest generator only under the approved one-run gate.
7. Audit every generated hash, byte count, path, and date change; stop on any extra diff.
8. Run integrity, Gate B, full tests, smoke, reviews, and hosted CI.

Never regenerate hashes merely to accept unexplained bytes. Never weaken a golden expectation to obtain green.

The S05 edit to `config/project.yaml project.version` is an approved unhashed release-identity change; all hashed config remains protected.

## CI topology

GitHub Actions runs locked `uv` gates on Python 3.12 and 3.14, the documented pip path on Python 3.12, an independent Docker image build, and `browser / Chromium / Python 3.12` on Ubuntu 24.04. The browser job installs matching Chromium system dependencies, verifies the vendored fonts, compares all governed baselines, caches Playwright by `uv.lock`, and uploads `.artifacts/e2e/` only when the job fails. It contains no baseline-update command. Workflow permissions are read-only for repository contents and checkout credentials are not persisted. Cancelled or skipped jobs are not green.

## Failure interpretation

- prohibited scan 1: prohibited tracked path or credential-pattern finding; output is path/rule only;
- prohibited scan 2: Git or tracked-file read error;
- threshold scan 1: embedded configured comparison literal;
- threshold scan 2: YAML, Python, or file-read error;
- lock/sync failure: lock absent, stale, or incompatible;
- compile/Node failure: syntax or required-tool failure;
- integrity failure: governed byte mismatch; do not regenerate without authority;
- Gate B 1: policy, reconciliation, or back-test failure;
- Gate B 2: execution/input error;
- pytest/smoke failure: implementation or frozen behavior is nonconformant;
- Docker/health failure: image/runtime compatibility issue;
- browser preflight failure: inspect exact package versions, matching Chromium
  executable, axe SHA-256/licence, and `fc-match :lang=ar`;
- Chromium shared-library failure: install Playwright's documented Linux
  dependencies in an authorized environment; do not bypass the gate;
- console/page/request/HTTP/external-origin failure: inspect the retained trace,
  server log, and sanitized collector records;
- axe, focus, overflow, RTL/tofu, print, or PDF failure: reproduce the named
  node and fix the product defect; exclusions and fixed waits are prohibited;
- final acceptance nonzero: inspect every step code and its full log.

## Evidence and detached execution

Every substantial command is launched through a uniquely named ignored script and log under `.workflow/logs/`. A wrapper uses `set -u`, changes to the repository, records each command exit code, and ends with `__DONE__`; the complete log must be read before a result is reported.

Raw logs, clean environments, temporary worktrees, and acceptance archives remain ignored. Sanitized command/results evidence belongs in the active slice `test_evidence.md`.

## Test-first and review discipline

Write the smallest failing test, observe the intended RED, implement the minimum change, observe GREEN, and run affected/full regression. Characterization tests that prove existing behavior are labelled honestly instead of being forced to fail. Use real local behavior when it can be exercised directly.

Before handoff, audit acceptance criteria, changed paths, protected paths, assumptions, limitations, rollback, and actual command output. Do not substitute predicted results for evidence.
