# S07 Independent Reviewer Findings — Bilingual Interface Foundation

**Role:** Independent Reviewer (read-only). Not Supervisor, not Implementer.
**Model:** Cursor Grok 4.6 (`cursor-grok-4.6`). Deliberately different from Supervisor (Claude) and Implementer (GPT-5.6 Sol).
**Persona (after reading):** Senior independent bilingual UI / RTL / design-token / visual-oracle reviewer for a governed industrial-decision product.
**Data classification:** `confidential_demo`. `.env` exists and is gitignored (`.gitignore:7`); contents were not opened or printed.
**Candidate:** uncommitted working tree on `slice/S07-bilingual-interface-foundation`, base/HEAD `6d00e27ff156e1342d488495c7b48e68eeefe100`.
**Reviewer authority:** may write only this file. No other create/modify/stage/commit/delete. Canonical Docker container was not run. `make e2e-update-baselines` was not run. `E2E_REFERENCE_DIR` / `IOR_UPDATE_VISUAL_BASELINES` were not set.

**Skills used (opened and applied):**

- `/home/barami/.agents/skills/strict-reviewer/SKILL.md`
- `/home/barami/.cursor/plugins/cache/cursor-public/superpowers/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/requesting-code-review/SKILL.md`
- `/home/barami/.cursor/plugins/cache/cursor-public/superpowers/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/requesting-code-review/code-reviewer.md` (checklist only; no subagent dispatch)
- `/home/barami/.cursor/skills/muhasib/SKILL.md`
- `/home/barami/.agents/skills/sanad-provenance/SKILL.md`
- `/home/barami/.agents/skills/task-standards/SKILL.md`
- `/home/barami/.agents/skills/muhasabah-gate/SKILL.md`

Supervisor-owned S06 post-merge records (`.workflow/slices/S06-browser-acceptance-harness/pr_record.md`, `completion.md`, `state.json` / `BUILD_PROGRESS.md` hunks, S06 text in `KNOWN_LIMITATIONS.md` / `REQUIREMENTS_TRACEABILITY.md`) are in-scope as legitimate branch content, not defects. Two untracked `.workflow/runs/*.sh` helpers are out of candidate scope.

---

## 1. Scope read

Read in the start-of-slice order, then the candidate:

| Authority | What was checked |
|---|---|
| `AGENTS.md`; `.cursor/rules/00-authority.mdc`, `10-domain-guardrails.mdc`, `20-proof.mdc` | Overlay, goldens, synthetic isolation, proof commands |
| `docs/authority/00_AUTHORITY_MANIFEST.md` §6, §7.3/§7.4, §8, §11 | Invariants, change class, integrity, hash table |
| Core 01 NFR-004/006/007 (v2 marker); Core 02 map rows; Core 03 §7; Core 06 §4/§8/§9; Core 09 §2.7 | Exact `git diff` of Core 01/02/09 vs authorized plan §7.3 text |
| `GAP_ANALYSIS.md` §4 A3/A8/A9/A10/G7, §6, §7A R-4; `SLICE_GRAPH.md` S06–S10/S19 | Slice ownership and later-slice boundaries |
| ADR-004/007/010 and ADR-011 | Arabic label / digit policy attributed as Supervisor-approved owner-amendable defaults, not owner-approved |
| Slice `persona.md`, `context.md`, full `plan.md` (PR-01..05), `plan_review.md`, `implementation_log.md`, `implementation_review.md`, `test_evidence.md` | Binding interpretation: engine English remains marked source-language islands; 40 lossless WebP; exact Arabic label; Western digits; Docker-free compare; chromium-1234 |
| Candidate sources listed in the review charge | Modules, tokens/CSS, catalogue, policy 1.2.0, engine/evidence/rules/genui/dossier/app, scanners, browser tests, visual comparator, container runner, `.dockerignore`, CI, Makefile, `pyproject.toml`/`uv.lock`, docs, hashes |

---

## 2. Ground-truth commands (this reviewer, this checkout)

Commands were executed independently. Outputs below are from this review session, not copied from slice records.

### 2.1 Default pytest — Python 3.12 (`.venv`)

```
PYTHONPATH=src .venv/bin/python -m pytest -q
377 passed, 1 warning in 2.19s
```

Starlette/httpx `TestClient` deprecation warning only.

### 2.2 Default pytest — Python 3.14 (`/tmp/venv314`)

```
UV_PROJECT_ENVIRONMENT=/tmp/venv314 PYTHONPATH=src uv run --locked --extra dev --python 3.14 python -m pytest -q
377 passed, 1 warning in 2.05s
```

### 2.3 UI / ES scanners

```
.venv/bin/python scripts/check_ui_contracts.py
UI CONTRACT CHECK PASS

.venv/bin/python scripts/check_es_modules.py --node node
ES MODULE CHECK PASS (19 files)
```

### 2.4 Integrity, scenarios, smoke

```
PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
INTEGRITY PASS
- data/manifests/snapshot_manifest.json
- docs/authority/authority_hashes.json

PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
SCENARIO VALIDATION PASS (2 scenarios)
… ground_truth_backtest: PASS (both SYN-MINISTRY-PP-001 and SYN-MINISTRY-STEEL-001)

PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

Live TestClient probe (no secrets): steel public `INVESTIGATE`/`INVESTIGATE`; steel simulated real `INVESTIGATE` + simulation `ADVANCE` with real unchanged; PP public `REJECT`; `/docs` HTTP 200 with Swagger UI present; index HTML has no `/docs` link; `GET /api/ui-strings/ar` returns 201 keys; unknown locale 404 `UI_LOCALE_NOT_FOUND`.

### 2.5 Browser gates (`LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e`)

Preflight both runs: Playwright 1.62.0, pytest-playwright 0.9.0, `chromium-1234`, product fonts `IOR Noto Sans,IOR Noto Sans Arabic`. Host `fc-match` remains DejaVu (diagnostic only, as recorded).

```
functional: 118 passed, 4 deselected in 121.59s
visual:     4 passed, 118 deselected in 23.60s
```

Host visual compare against the tracked canonical baselines **passed**. That is positive local-determinism evidence; it is not a substitute for hosted Ubuntu 24.04 CI.

### 2.6 Protected paths and S06 documentary set

```
git diff --name-only -- data config/thresholds.v1.yaml config/sector_profiles.v1.yaml docs/core/03* docs/core/04* docs/core/05* docs/core/06* docs/core/07* docs/core/08*
(empty)

git status --short .workflow/slices/S06-browser-acceptance-harness/reference-screenshots
(empty)

git diff -- data/manifests/snapshot_manifest.json
(empty)
```

`.env` exists; `git check-ignore -v .env` → `.gitignore:7:.env`.

### 2.7 Authority hash diff (authorized rows only)

`git diff -- docs/authority/authority_hashes.json` changes only:

- `config/evidence_policy.v1.yaml` → `30018295…` / 1479
- **new** `config/ui_strings.v1.yaml` → `59ccb67a…` / 23183
- Core 01 → `8c8cea8f…` / 11942
- Core 02 → `4352f990…` / 11416
- Core 09 → `81b221b5…` / 6671

Independent SHA-256/byte recompute of every `authority_hashes.json` row matched. Manifest §11 table matches the JSON. `generated_on` remains `2026-09-02`. `snapshot_manifest.json` untouched.

---

## 3. Per-area verification notes

### 3.1 Core 06 §9 / G7 — Arabic warning and Ministry implication

Policy 1.2.0 adds only `display_label_ar: "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"` beside existing English `SIMULATED — NOT MINISTRY EVIDENCE` (`config/evidence_policy.v1.yaml:35-36`). Production Python/JS/HTML do not contain either string; `evidence.synthetic_display_labels()` is the projection (`evidence.py:51-56`; `config.py:160-192` rejects catalogue duplication and `synthetic.*` keys).

Arabic wording, as Supervisor PR-03 required: “simulation — not data or evidence issued by the Ministry.” It is stricter than the English and does **not** describe synthetic records as Ministry evidence. Mode chrome `محاكاة الوزارة` / “Ministry simulation” includes the word simulation (Core 06 §9 forbids “Ministry data” *without* simulated). Catalogue has no policy-label duplicate (201/201 key parity, zero empty values, zero policy-string collisions — verified by loading YAML + `evidence_policy_config`).

Public portfolio/workspace screenshots (en/ar) show **neither** yellow disclosure. Simulated portfolio/workspace/dossier screenshots show **both** labels. Browser `wait_for_workspace` asserts banner contains both labels in simulated mode and neither in public (`browser_tests/pages.py:56-62`). Dossier public contract: `test_public_dossier_contains_neither_policy_label`.

The always-visible governance card (`index.html:137-141`) injects both labels via `applyPolicyLabels` into a card that *describes* the simulation layer. That is educational chrome, not a claim that public evidence is synthetic. Traceability V3-G7 “public surfaces display neither” is true for decision surfaces (banner/portfolio/dossier); the governance explainer is in-DOM in every mode.

### 3.2 Goldens and engine semantics

`git diff` of `decision_engine.py` / `rules.py` is additive `display_labels` only. Thresholds, sector profiles, `data/**`, Core 03–08, DOCX, and golden expectations are untouched. Smoke + `tests/test_golden_cases.py` + Gate B back-tests: steel public **INVESTIGATE**, steel simulated **ADVANCE** with real unchanged, PP public **REJECT**.

### 3.3 Modules, tokens, catalogue

19 production JS files; max **132** lines (`i18n.js`); named exports; no `export default` (`tests/test_es_modules.py`). `styles.css` is an `@import` façade only. Colour/length/physical/font/shadow/radius/z-index literals in `static/css/*.css` excluding `tokens.css` were not found; scanner `check_ui_contracts.py` + `test_ui_tokens.py` pass. Logical properties used for shell mirroring. Font hashes match plan §5.6 exactly (35,820 / 165,960 bytes).

Copy scanner: HTML visible-text parser + `.textContent`/`toast()` literal assignments + catalogue-scalar duplication. No current module emits a raw English/Arabic sentence outside `t()` / `ui_text()` / policy labels. Scanner does not HTML-parse JS templates (see residuals).

### 3.4 S06 behaviours per locale; failure hooks; visual comparator

All 17 named S06 tests remain; locale is an added dimension (plus `test_locale_switch_…` and `test_governed_visual_baselines_match`). Keyboard inventory is still **15** controls, with `id:locale-switch` replacing `/docs` (`test_accessibility.py:55-80`) and an explicit `"/docs" not in body` assertion. Collector still has five channels; `assert_clean` has no exclusion list (`harness.py:659-664`); probe test records `"ordinary_collector_exclusions": 0`. `ReferenceRecorder` is absent (`test_browser_harness_contract.py:140`). Documentary S06 WebP directory is unmodified.

Visual rule is global: channel delta **>8** is significant; pass requires ratio **≤0.001** and mean **≤0.20** (`scripts/visual_metrics.py:7-11`). Pillow `mask` in `compare_images` is the significant-pixel bitmap, **not** an ignore-region. No per-screen tolerance, no auto-accept. Update requires `IOR_CANONICAL_VISUAL=1`, `IOR_CHROMIUM_REVISION=chromium-1234`, and a change_ref (`visual_baselines.py:231-236`). Makefile update target additionally requires `IOR_UPDATE_VISUAL_BASELINES=1`, change_ref, and empty `CI`. CI workflow has none of `IOR_UPDATE_VISUAL_BASELINES`, `e2e-update-baselines`, or `--mode update` (`ci.yml`; `test_visual_baseline_contract.py:274-281`). `make e2e` is Docker-free.

40 lossless RGB WebPs, total **4,987,732** bytes, max **229,272** (<600 KiB / <12 MiB). Manifest `change_ref=S07-SR-01-defect-fixes`, `chromium-1234`, browser `151.0.7922.34`, canonical image digest suffix `87e8d767a090ea3f740d`. `manifest.sha256` matches file digest `0d21e94a…`. Container runner: `--network=none`, allow-listed mounts, `.env` not mounted, Docker-missing exit 2, in-container `chromium-1234` assertion (`run_visual_baseline_container.py`, `visual_container.py`). `.dockerignore` first line is `.env`.

`dev` extra remains `pytest` + `httpx`. Pillow **12.3.0** is `e2e` only (`pyproject.toml:18-26`; `uv.lock` markers).

### 3.5 Visual inspection of baselines

Converted with Pillow (no baseline-update path) and viewed:

| Converted PNG | Checks |
|---|---|
| `ar` desktop steel-simulated workspace | RTL sidebar on the right; both policy labels; `HS 721049` logical order; bilingual chips `تحقق INVESTIGATE` / `تقدم ADVANCE` (Arabic label + one isolated code, not English double-word); years `2024` / `31 أغسطس 2026` ungrouped Western digits |
| `ar` desktop portfolio simulated | Both labels; steel ADVANCE + INVESTIGATE; PP REJECT; no chip-text duplication |
| `ar` desktop portfolio public | **No** yellow disclosure; steel INVESTIGATE; PP REJECT |
| `en` desktop portfolio public | LTR sidebar left; neither label; INVESTIGATE / REJECT |
| `en` desktop steel-public workspace | Public boundary copy; single INVESTIGATE; no simulated labels; Decision object note `partially resolved` |
| `en` tablet 1024 public workspace | Stacked layout; no observed badge/conditions overlap |
| `ar` tablet 1024 steel-simulated workspace | Labels present; no observed overlap |
| `ar` desktop/tablet simulated dossier | Both labels; HS `H0 / 721049` isolate; source-language captions |

SR-01 a–f defects (grouped years, doubled English chips, missing label/value separator, RTL-reordered HS tokens, 1024 overlap, disclosure `flex-end`) are not visible on the regenerated set. Browser tests now assert those classes (`test_responsive.py` rectangle non-intersection; ungrouped years; technical `unicode-bidi: isolate`).

### 3.6 Docs truthfulness

- V3-A8 / V3-A10 / V3-G7 are **TESTED**, not COMPLETE (`REQUIREMENTS_TRACEABILITY.md:174-176`).
- KL-21 / KL-31 closures are **provisional** pending independent approval, merge, and green CI (`KNOWN_LIMITATIONS.md:24-25`).
- ADR-011 attributes the Arabic label and digit/date policy as Supervisor-approved owner-amendable defaults under PR-03/PR-04, “not as owner-approved wording” (`docs/ARCHITECTURE_DECISIONS.md:94-98`).
- Two generator runs are recorded and justified (catalogue `common.label_value` after SR-01c). Governed diff versus `main` remains the authorized rows. ADR-011 line 104 still says the generator “runs exactly once” — stale relative to the later justified second run; hashes themselves are correct (residual).

### 3.7 Offline / NFR-004

Fonts are local WOFF2. No `/docs` in demo UI. FastAPI `/docs` remains (200 + swagger). No external request path in the functional collector’s ordinary run.

---

## 4. Findings

None. Style preferences and non-blocking scanner/documentation gaps are in §5.

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | FAILURE_SCENARIO | REQUIRED_REMEDIATION | PROVING_TEST |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

---

## 5. Residual observations (non-blocking)

1. **Copy scanner vs plan §5.2.** `copy_findings()` does not HTML-parse JS template literals; it catches `.textContent` / `toast()` string literals and catalogue-scalar duplication. Current modules go through `t()` / `ui_text()`. A future hardcoded sentence inside a template would not necessarily fail CI.
2. **Token scanner does not read `styles.css`.** It globs `static/css/*.css`. The façade is import-only today; a hex added there would not be scanned. Dossier embedded CSS *is* scanned via `--scan-rendered-css`.
3. **JS motion / SVG user-space literals.** Toast dwell `2400` (`dom.js:18-21`); `scrollIntoView({behavior:"smooth"})` (`events.js:28-31`) does not read `--motion-scroll`; trade chart `r="4"` and viewBox geometry (`trade.js:13-38`). CSS motion tokens are used for transitions. Not a present visual-oracle defect.
4. **`decision_object_status` is not a source-language island.** When economics is omitted, `renderMetricGrid` emits `replaceAll("_", " ")` through `escapeHtml` (`decision.js:87-96`). Plan §5.5 Decision family does not list this field; capability dimension names *are* islanded. English public steel workspace shows “partially resolved”. Low NFR-007 honesty gap, not a golden/label failure. S08–S10 remain the bilingual-narrative owners.
5. **Governance card always receives both policy labels** via `data-policy-labels`, including in public mode. Decision surfaces do not. Tests correctly scope “neither label” to banner/portfolio/dossier public.
6. **ADR-011 and early `implementation_log` still say one generator run.** Fix-round records two justified runs; this reviewer confirmed the hash diff is still the authorized rows only. `snapshot_manifest.json` unchanged.
7. **`CHANGELOG.md` Unreleased** concatenates S06 documentary-screenshot bullets with S07 oracle bullets. Accurate as a sequence; slightly easy to misread as a single slice.
8. **Host `fc-match` is DejaVu.** Product `@font-face` families are IOR Noto; visual compare passed on this WSL host.

---

## 6. Cannot verify

- Hosted GitHub Actions (`browser / Chromium / Python 3.12` on ubuntu-24.04). Local `make e2e` is not CI.
- Canonical Noble container compare/update (explicitly forbidden for this review). Chromium assertion and mount allow-list were reviewed as code + unit tests only.
- Pixel inspection of all 40 WebPs. Ten representative screens were converted and viewed.
- Native-speaker Arabic linguistic review beyond PR-03 wording, catalogue consistency, and sampled chrome.
- DOCX visual rendering. SHA-256 `5717cbd42acc…ce9` / 224,257 bytes matches Manifest §11.
- Future S08–S10/S19 bilingual engine/dossier narrative completeness (out of S07 scope; islands are the specified honesty control).

---

## 7. Muhasib

- Scope stayed inside S07 review. No code, baseline, or hash was modified.
- Consequential claims carry command output, `git diff`, or file:line.
- Supervisor SR-01/SR-02 were re-checked on regenerated images and tests, not taken on trust.
- Goldens, protected paths, policy-only engine edits, and hash-row allow-list were independently confirmed.
- Residuals were not promoted into findings to manufacture a REJECT after green gates.
- Assumption: hosted Ubuntu 24.04 paint will stay inside the governed tolerance, as local host compare already did against the same canonical images.

**Muhasib result: PASS.**

---

Verdict: APPROVE — zero unresolved findings

---

## Post-approval record correction

Supervisor edited only the ADR-011 “Core revision markers…” paragraph in `docs/ARCHITECTURE_DECISIONS.md` (line 104). It now states `scripts/build_manifests.py` ran once for the initial governed set and a second recorded time for the Supervisor-review catalogue fix that added the label/value pattern, with the same permitted generated-diff allow-list. That matches `implementation_log.md` Fix round 1 (runs total **2**; catalogue row `59ccb67a…` / 23,183 bytes; `generated_on` unchanged) and the independently recomputed `authority_hashes.json` diff (evidence policy, new catalogue, Core 01/02/09 only; `snapshot_manifest.json` untouched). `find` of the tree newer than this findings file listed only `docs/ARCHITECTURE_DECISIONS.md`. Re-run: `PYTHONPATH=src .venv/bin/python -m pytest -q` → **377 passed, 1 warning in 2.21s**. `git status --short | wc -l` → **82**. Residual 4 (`decision_object_status` not islanded) may be carried to S18/S19; wrapping it now would force a 40-image baseline regeneration for a low honesty gap that plan §5.5 does not list. **APPROVE stands** for this exact candidate.
