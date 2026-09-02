# S07 test evidence — Bilingual interface foundation

All results are local Implementer evidence for the uncommitted candidate. They
do not claim Supervisor approval, independent review, hosted CI, staging,
commit, PR, merge, effective limitation closure, or release.

## Environment

```text
branch: slice/S07-bilingual-interface-foundation
base/HEAD: 6d00e27ff156e1342d488495c7b48e68eeefe100
primary Python: 3.12.13
compatibility Python: 3.14.4
uv: 0.11.31
Node: 22.22.3
Docker: 29.7.2
Playwright: 1.62.0
pytest-playwright: 0.9.0
Pillow: 12.3.0
Chromium: chromium-1234 / 151.0.7922.34
data classification: confidential_demo
```

The local WSL Chromium commands used
`LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs`, the S06-documented local
shared-library workaround. No `sudo`, `apt`, or local `--with-deps` command was
run.

## Characterization

Before implementation:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q
309 passed, 1 warning

LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e
62 passed
```

The warning is the pre-existing Starlette/httpx TestClient deprecation.

## TDD evidence

| Contract | RED | GREEN |
|---|---|---|
| ES module entry/graph/export/size/syntax | 4 failed | 83 focused passed; recursive checker PASS (19 files) |
| Make/CI/final-acceptance ES gate | 4 failed | 43 then 46 focused contract tests passed |
| Token layer/scanner/dossier CSS | 12 failed | 29 focused passed; UI checker PASS |
| Catalogue/API/copy usage | 10 failed | catalogue/API focused passed |
| Dual policy labels | 11 failed | 83 then 100 focused passed |
| Exact fonts/provenance/preflight | 3 failed | 28 focused passed; preflight PASS |
| Dossier locale/islands | 4 failed | dossier/API/authority focused passed |
| Demo `/docs` removal | 1 failed | static/API 2 passed |
| Locale browser matrix | 108 passed, 10 failed | focused 10 passed; then 118 passed |
| Visual comparator/container/guard | 12 failed | 13 contract tests passed |
| Captured UI defects | focused static regressions failed | each focused regression passed |
| Simulated-surface disclosure audit | governance static and two portfolio nodes failed | policy-bundle disclosure added; 118 functional nodes passed |
| Core markers/generator list | 2 failed | 3 then 4 integrity contracts passed |
| Deleted tracked-test scanner handling | 1 failed | 31 scanner tests; live scanner PASS |

No test was skipped, xfailed, disabled, loosened, masked, or given a
per-screen tolerance.

## Final Python and authority gates

### Python 3.12

```text
PYTHONPATH=src .venv/bin/python -m pytest -q
377 passed, 1 warning in 2.04s
exit 0
```

### Python 3.14

```text
UV_PROJECT_ENVIRONMENT=/tmp/venv314 \
  PYTHONPATH=src uv run --locked --extra dev --python 3.14 \
  python -m pytest -q
377 passed, 1 warning in 2.00s
exit 0
```

### Lock, integrity, Gate B, smoke, and static gates

```text
uv lock --check
Resolved 40 packages
exit 0

PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json
exit 0

PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)
ground_truth_backtest: PASS (2/2)
exit 0

PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
exit 0

.venv/bin/python scripts/check_ui_contracts.py
UI CONTRACT CHECK PASS
exit 0

.venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (19 files)
exit 0

.venv/bin/python scripts/check_prohibited_files.py
PROHIBITED FILE SCAN PASS (244 tracked files)
exit 0

.venv/bin/python scripts/check_threshold_literals.py
THRESHOLD LITERAL SCAN PASS (13 Python files; 23 configured numeric values)
exit 0

.venv/bin/python -m compileall -q src scripts tests browser_tests
exit 0; no output
```

## Browser and visual evidence

Final explicit comparison:

```text
LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e
functional: 118 passed, 4 deselected in 119.22s
visual: 4 passed, 118 deselected in 23.70s
exit 0
```

`make ci` also completed with exit 0 and observed:

```text
prohibited scan PASS
threshold scan PASS
UI contracts PASS
compile PASS
ES module check PASS (19 files)
integrity PASS
Gate B PASS (2 scenarios)
377 default tests passed
smoke PASS
118 functional browser nodes passed
4 visual browser nodes passed
```

The final browser inventory is 18 named behaviors / 122 nodes. Functional
coverage includes both locales for case cards/select, both mode directions,
navigation, locale switch, dossier popup/clipboard/print/PDF, 16 keyboard
nodes, 16 axe workspace/dossier nodes, intended Arabic font/tofu tests,
16 responsive/mirroring nodes, and two collector self-tests.

## Canonical baseline evidence

The first required functional precondition was:

```text
make e2e-functional
118 passed, 4 deselected
exit 0
```

Canonical update command:

```text
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S07-initial-governed-baseline" \
make e2e-update-baselines
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234
4 visual nodes passed, 118 deselected
exit 0
```

Image inspection found state-label collision, sticky-anchor clipping, and
host-dependent monospace source JSON. Those candidates were not retained.
Each fix received a focused regression and a fresh 118-node functional pass
before canonical recapture. The final set:

```text
40 lossless WebPs
10 screens × 2 locales × 2 viewports
opaque RGB; no alpha
images: 5,037,854 bytes
font binaries: 201,780 bytes
manifest SHA-256:
b0295568b764fc08e1d414bbea4d706dcba7f2f8f877eb2770eb3b890a264a50
browser: 151.0.7922.34
revision: chromium-1234
flags:
  --font-render-hinting=none
  --disable-lcd-text
  --force-color-profile=srgb
tolerance:
  max channel delta > 8
  significant ratio <= 0.001
  mean absolute channel error <= 0.20
```

Final Docker-free host comparison passed 4/4. Comparator unit contracts prove
channel-delta equality, ratio overrun, mean calculation, dimension failure,
lossless WebP structure, exact manifest/hash/source/font provenance, budgets,
Docker-unavailable exit 2, mount allow-list, and CI update prohibition.

## Single generator evidence

Pre-generation `verify_integrity.py` failed only on the authorized existing
rows:

```text
config/evidence_policy.v1.yaml
docs/core/01_PRODUCT_AND_REQUIREMENTS.md
docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
```

`PYTHONPATH=src .venv/bin/python scripts/build_manifests.py` ran exactly once.
The generated diff was limited to:

```text
evidence_policy: 30018295a801cbcffa0681fc634982b2601e87f8756d1350ef37d9c67e327081 / 1,479
ui_strings:      c6532773bb0539411c011aae44d37840ffb59947c96421b4766bbe75d6f99590 / 23,097
Core 01:         8c8cea8fc58db821b4bc151a2170bd74188085526419e62b7e2752eb62fa8080 / 11,942
Core 02:         4352f990e9ef146be8312fa932ba2f9b8383e098cdfca1286fdc59f02617104c / 11,416
Core 09:         81b221b5e715ca5c0a5318c1d42e15c9942b863a17f4c4e7854a45aa69420559 / 6,671
```

`snapshot_manifest.json` had no diff and remains SHA-256
`0fb34f96a1d4a9745e93ee2a54f210b97e6f4597a1d75bd9d6c74c5d430d9a1e`.
The human Manifest §11 table is tested as an exact machine-manifest mirror.

## Protected-path and security audit

```text
git diff --name-only -- data docs/core/0{3,4,5,6,7,8}* \
  config/thresholds.v1.yaml config/sector_profiles.v1.yaml
(no output)

git diff --check
(no output)

S06 documentary directory aggregate:
d71041e0811509746a94ec9baf7c2511236b64c22fd2774e732d08ed50dc6784
(identical before and after)
```

- `.env` was not opened, copied, mounted, printed, or staged.
- Canonical runtime used `--network=none`; only the version-pinned image build
  used network access.
- Container mounts are the exact allow-list; repository root, home, `.git`,
  `.env`, Docker socket, and unrelated projects are absent.
- Runtime modules, fonts, CSS and locale resources are same-origin only.
- A non-staging scan of all 147 Implementer candidate files (excluding the
  named Supervisor/planner records and two helper scripts) returned zero
  prohibited-path or credential-pattern findings.
- This candidate remains uncommitted and unstaged.

## Fix round 1 evidence

Focused RED evidence:

```text
summary contract: 1 failed (mode-specific files absent)
browser defect assertions: 22 failed / 6 passed
observed: grouped 2,024 and 2,021; missing route colon; repeated English
state; missing combined Arabic HS isolate
```

Focused GREEN evidence:

```text
summary/catalogue contracts: 11 passed
UI CONTRACT CHECK PASS
ES MODULE CHECK PASS (19 files)
frontend/browserless contracts: 74 passed
browser defect matrix: 28 passed
```

Defect proof:

| ID | Before | After |
|---|---|---|
| SR-01a | `2,024 imports`; chart `2,021` | `2024 imports`; chart `2021`; locale/mode regex assertions pass |
| SR-01b | `Investigate INVESTIGATE`, `Reject REJECT` | English isolated code once; Arabic label plus isolated code; adjacent-word assertions pass |
| SR-01c | `RouteBrownfield…`; `…expansionالمسار` | catalogue pattern emits `Route: Brownfield…` / `المسار: Brownfield…`; 16 separator assertions pass |
| SR-01d | RTL showed `721049 HS` and split `721049 / H0 HS` | one isolate has exact `HS 721049` or `HS H0 / 721049`, computed LTR/isolate |
| SR-01e | 1024×768 badge intersected Conditions | one-column layout at ≤1180 px; 16 rectangle-intersection assertions pass |
| SR-01f | Arabic disclosure aligned left | inline-start/right edge matches the RTL portfolio grid; mirroring assertions pass |
| SR-02 | visual run overwrote `run-summary.json` | separate functional/visual summaries persist; atomic replace handles container ownership |

Required execution evidence:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q
377 passed, 1 warning in 2.14s

UV_PROJECT_ENVIRONMENT=/tmp/venv314 ... python -m pytest -q
377 passed, 1 warning in 1.98s

LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e-functional
118 passed, 4 deselected in 121.10s

IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S07-SR-01-defect-fixes" \
make e2e-update-baselines
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234
4 passed, 118 deselected in 32.15s

LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e
118 passed, 4 deselected in 122.71s
4 passed, 118 deselected in 23.78s
exit 0

LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make ci
377 default tests passed
118 functional browser nodes passed
4 visual browser nodes passed
exit 0

PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS

git diff --check
(no output)

protected-path audit
(no output)

S06 documentary aggregate
d71041e0811509746a94ec9baf7c2511236b64c22fd2774e732d08ed50dc6784
```

The first concurrent 3.12/3.14 default-suite attempt caused a shared temporary
CSS fixture race in the 3.14 process (the 3.12 process deleted the same file).
The required 3.14 suite was rerun alone and passed 377/377; no product or test
change was made for this execution-only collision.

The second and final authorized manifest-generator run was justified solely
by the new bilingual `common.label_value` catalogue entry. The catalogue row
is now SHA-256
`59ccb67a882ee4fa70390a4588873724074a2e689a17b7bcc6dc850cb1602f41`,
23,183 bytes; all other machine rows remained at their pre-fix candidate
values and integrity passed. Generator runs total: **2**.
