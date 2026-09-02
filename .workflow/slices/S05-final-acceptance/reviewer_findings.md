# Independent Reviewer Findings — S05 Final Holistic Acceptance

**Reviewer model:** Cursor Grok 4.6 (`cursor-grok-4.6-xhigh`)
**Implementer model:** GPT-5.6 Sol (`gpt-5.6-sol-max`)
**Supervisor model:** Claude (`claude-fable-5-1-thinking-max`)
**Seat:** Independent FINAL HOLISTIC REVIEWER (read-only). Not the Supervisor. Not any Implementer. Cannot remediate or approve own findings.
**Discipline persona:** Delivery / system-level audit (sanad-provenance + al-muhasibi).
**Data classification:** `confidential_demo` (frozen public snapshots and Class-D demo scenarios only).
**Scope:** The merged S00–S04 system on `main` at `98c1a40` plus staged uncommitted S05 work on `slice/S05-final-acceptance`. This is a whole-system review against the governing specification, not a slice-diff review.
**Skill applied:** `requesting-code-review` / `code-reviewer.md` (plan/spec alignment, fail-closed behaviour, test fidelity, architecture, security, production readiness; severity by actual harm).

This review does not authorise merge, commit, push, PR, tagging, or public support.

---

## Scope read (confirm)

Read in the mandated order, in full unless noted:

1. `AGENTS.md`; `.cursor/rules/00-authority.mdc`, `10-domain-guardrails.mdc`, `20-proof.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md` (entire).
2. `docs/authority/methodology_extracted.md` — **entire file, lines 1–1890** (searchable mirror of the governing DOCX). The DOCX bytes were not re-parsed; hash identity was taken from `authority_hashes.json` / Manifest §11.
3. `docs/core/01` through `docs/core/09` — all nine, in full.
4. `config/thresholds.v1.yaml`, `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml`, `project.yaml`; both public snapshots; both synthetic scenarios; `data/golden/ar_en_spec_extraction.json`; `data/manifests/snapshot_manifest.json`; `docs/authority/authority_hashes.json`.
5. `docs/BUILD_ROADMAP.md`, `BUILD_PROGRESS.md`, `REQUIREMENTS_TRACEABILITY.md` (every row), `ARCHITECTURE_DECISIONS.md` (ADR-001..009), `KNOWN_LIMITATIONS.md`, `FINAL_BUILD_REPORT.md`, `OPERATOR_RUNBOOK.md`, `DEPLOYMENT_GUIDE.md`, `DEVELOPMENT_GUIDE.md`; `docs/implementation/` (API_REFERENCE, BUILD_OVERLAY, DELIVERY_NOTES, MINISTRY_DEMO_SCRIPT, MVP_BACKLOG, SECURITY_AND_DEPLOYMENT_NOTES, UX_GENUI_DEMO_SPEC); `README.md`; `CHANGELOG.md`.
6. `.workflow/state.json`; S00–S04 `completion.md` / `plan_review.md` / `implementation_review.md` / `reviewer_findings.md` / `test_evidence.md` as present; S05 `acceptance_results.md`, `implementation_log.md`, `implementation_review.md`, `plan.md`, `plan_review.md`, `test_evidence.md`.
7. All `src/ior_mvp/*.py` and `src/ior_mvp/static/*`; `scripts/*`; `Makefile`; `.github/workflows/ci.yml`; `Dockerfile`; `docker-compose.yml`; `pyproject.toml`; `uv.lock` header and root package stanza (`industrial-opportunity-resolution-mvp` `0.2.0`).
8. All 18 files under `tests/`.
9. Skill: `requesting-code-review/code-reviewer.md`.

---

## Skill result (`code-reviewer.md`)

### Strengths

- Dual-state isolation is real, not theatrical: public analysis uses only hashed snapshots; simulation fingerprints `real_decision`; synthetic rows are Class D / `DEMO_GENERATOR` / labelled; steel public stays `INVESTIGATE` and PP public/simulated stay `REJECT` with route 0.
- After S04, `_simulate` is generic (Core 07 §7.4 then §7.3 then INVESTIGATE). Opportunity-ID dispatch is gone. Ground truth does not select the route. Thresholds used in comparisons are config-sourced; the recursive literal scanner is in CI and `make ci`.
- Capability publication, λ/U, Kmin, and hard-gate withholding match Core 07 for the steel public and steel simulated fixtures. Formula goldens (57.509 kt, 46.491 kt, D\* 0.2667, S\* 18, ΔNV 198, ratio 1.0751) are independently reproducible from the frozen inputs.
- S05 release identity is internally consistent at `0.2.0` (`pyproject.toml`, `__init__.py`, `config/project.yaml`, `uv.lock` root package, health test, CHANGELOG, runbook/deployment). Traceability correctly stops at `TESTED` and does not invent S05 merge/CI/tag facts. KL-20–KL-30 record the main methodological MVP cuts honestly.
- CI topology, Makefile `ci`, and DEVELOPMENT_GUIDE gates match (prohibited scan → threshold scan → compile → node → integrity → Gate B → pytest → smoke; pip path preserved).

### Issues

See the findings table. Two HIGH security/packaging defects are material at system level. Domain goldens and synthetic isolation are not the failure mode.

### Assessment

**Ready to merge?** No, from this seat, until the unresolved findings are fixed and re-reviewed.

**Reasoning:** The industrial decision method for the two packaged cases is largely faithful. The packaged runtime, however, can read arbitrary files via the SPA catch-all and can ship a local `.env` through `make package`. Those are system defects, not slice nits.

---

## Answers to the mandated questions

### 1. Does this system genuinely satisfy the governing specification (methodology + Core 01–09)?

**For the frozen two-case Ministry demonstration: largely yes**, with the cuts recorded in KL-20–KL-30, Core 01 §8 exclusions, Core 02 deferred items (outcome learning, portfolio/UnlockValue), and FR-073 `NOT_APPLICABLE (production)`. The two public golden outcomes and both simulated outcomes match Core 09 §2.4 and methodology §§13–14.

**Normative statements with no implementation, no test, and no recorded limitation** (not automatically findings; listed because mandated):

| Statement | Where | Why it is uncovered |
|---|---|---|
| Supplier HHI on **quantity** as well as value | Methodology §3.3 / Appendix A | Steel snapshot and R3 use `partner_value_hhi` only (`SAU-H0-721049.json:59-65`; `rules.py:539-572`). No quantity-HHI field, test, or KL. |
| `evidence_policy.advance_gate.blocked_if_D_or_E` as an executed control | `config/evidence_policy.v1.yaml:13-18`; Core 01 FR-053 | Policy is loaded for synthetic isolation only. No `src/` reference to `advance_gate`. Public ADVANCE is vacuously impossible (KL-24), so the gate is not an executable policy check. |
| Methodology §15 contradiction register on the Decision Dossier | Methodology `:1618-1624` | Steel snapshot retains `contradiction` (`SAU-H0-721049.json:189`). Dossier JSON/HTML and the evidence table do not project it (`dossier.py:57-64`; `app.js:329-345`). FR-015 is tested as retain-in-record, not dossier visibility. No KL. |

Everything else material is either implemented and tested, explicitly excluded (Core 01 §8), or recorded (KL-20–KL-30 / Core 02 future maps).

### 2. Is anything claimed but not actually implemented?

**Yes.**

- `README.md:114` says the simulation branch introduces “tariff-line allocation”. Packaged scenarios have no such block; KL-28 records `NOT_APPLICABLE`. See **RV-04**.
- `docs/implementation/DELIVERY_NOTES.md` is still titled and evidenced as v0.1.0 / 35 tests. It is a historical note, not the S05 release claim; not a finding if readers treat the title as version-bound.
- Traceability, FINAL_BUILD_REPORT, and ADR statuses that were checked against files are not inventing S05 merge/CI/tag. KL closures KL-01–KL-09 cite merged PRs; KL-20–KL-30 remain accepted. No false COMPLETE promotion on this branch.
- Journey A “synthetic leakage is zero” is **enforced in the engine and tests**, but the overview KPI is a hardcoded `"0"` (`app.js:72`), not a live integrity measurement (residual, not a finding).

### 3. Did autonomous slice development introduce cross-slice inconsistency?

**Mostly no on contracts; yes on a few surfaces.**

Aligned: public vs simulated R6–R8 labelling (S04); 404 vs 422 mapping (ADR-009 / API_REFERENCE / runbook); CI vs `make ci` vs DEVELOPMENT_GUIDE gate order; authority object on analysis, banner, and dossier; release `0.2.0`.

Inconsistent / stale:

- `docs/BUILD_PROGRESS.md` still shows S05 as `PLAN_DRAFT` while `.workflow/state.json` is `IMPLEMENTING` (expected mid-slice; not a product defect).
- `Makefile` `run` uses `--reload`; OPERATOR_RUNBOOK does not. Harmless.
- README “Integrity and tests” still points at `make verify` (integrity + pytest only), while the required local proof is `make ci` (DEVELOPMENT_GUIDE). Residual docs drift.
- `docker compose` publishes `8000:8000` on all host interfaces; runbook `docker run` binds `127.0.0.1:8000`. Combined with RV-01 this is material.

### 4. Are there architectural contradictions?

**Yes, three that matter.**

- Policy values in code: **fixed** for R11/D\*/competition (S02). `evidence_policy.advance_gate` is still unused configuration (see Q1).
- Hidden dispatch: **removed** for simulation (ADR-006). Public R4-D / R5 / R9-S / R10 / R11 still consume snapshot `rule_context` flags rather than recomputing from raw partner cells; that is consistent with Core 05 “POC begins at the snapshot stage” and the frozen worked cases, not a silent ID branch.
- Unknown → value: `incremental_national_value` and `approximate_evsi` coerce missing numeric keys to `0` (`economics.py:87-125`). That can make ΔNV/EVSI look calculable when inputs are absent. See **RV-05**.
- Synthetic leakage path in the **decision** branch: not found. Isolation, fingerprint, and Class D labelling hold for the packaged cases.
- Authority disclosure: implemented (S03) and tested; no drift vs `authority_hashes.json` on the files read.
- Capability hard-gate parser treats only the exact strings `not applicable` / `not_applicable` as resolved. PP scenario uses `"not applicable to resin production"`, so tooling is treated as unresolved and D\* is withheld in PP simulation. See **RV-03**.

### 5. Are tests giving false confidence?

**Partially, in the usual MVP ways; goldens are not weakened on the current files.**

- Core 09 §2.7 frontend tests are static source/CSS contrast parsing, not browser interaction (KL-22). Honest if readers accept that gate.
- Monkeypatching `get_synthetic_scenario` for HTTP 422/404 is required by ADR-009 (no runtime data-root override). Those tests still exercise `app.py` mapping, not a fake engine.
- Boundary tests in `test_threshold_boundaries.py` hit below/equal/above for R1-D, R2, R3, R11, Kmin, D\* bands, competition, R6, R7. R11 uses strict `>` (matches “more than 50×”). Competition uses `>` (matches “ratio >1.25”).
- `tests/test_golden_cases.py` currently asserts the Core 09 §2.4 contract, including steel simulated exacts and PP simulated gap/support/route. This session **could not** execute `git log -p -- tests/test_golden_cases.py` (Windows git: dubious ownership on the UNC path; WSL wrapper returned no status). S04 reviewer recorded the golden diff as assertion-additive. Independent history verification is therefore incomplete (see Cannot-verify).
- `scripts/demo_smoke.py` does not assert PP simulated `REJECT`. Pytest goldens do.
- Overview “Synthetic leakage = 0” is not asserted from `integrity` (residual).

### 6. Missing real-world failure paths?

| Path | Behaviour | Judgement |
|---|---|---|
| Malformed config | `_load_yaml` raises `FileNotFoundError`/`ValueError`; `AuthorityConfigurationError` is uncaught → HTTP 500. Core 03 §10 allows request failure. Not a structured 422. Residual. |
| Missing data files | `RepositoryError` → 404. Acceptable. |
| Concurrent requests | Process-local `lru_cache` of immutable files + `deepcopy` (KL-29). No write endpoint. Residual. |
| Unknown mode | FastAPI `Literal` → HTTP 422. Exercised by S05 `http_failures`. |
| Oversized input | GET-only API. Residual. |
| Unicode/RTL in dossier HTML | Arabic name is `dir="rtl"` (`dossier.py:152`). Not browser-verified (KL-22). |
| **SPA `/{path:path}` with `..`** | **No containment.** See **RV-01**. S05 failure step only GETs `/nonexistent-static` and asserts 200 HTML (`final_acceptance.sh:747-753`). |

### 7. Is anything still mocked or superficial? Partly implemented features?

- Offline extractor is a schema-constrained regex demo (Core 08). Not a production LLM. FR-073 N/A. Honest.
- Public decision selector is fixture-bounded: generic-capacity REJECT vs INVESTIGATE from snapshot contract + R11 (KL-24). Not a full Core 07 §7.1 else-branch.
- R6/R7/R8 public DISABLED; simulated R6/R7 evaluate labelled proxies; R8 stays DISABLED (KL-25). Honest.
- GenUI is a constrained component picker, not a model. Matches Core 03/08.
- No Playwright (KL-22).

### 8. Documentation vs behaviour?

- API_REFERENCE matches `app.py` routes and the 404/422 split. It also says “static frontend paths: served by the SPA fallback” without stating that resolved paths are not confined to `static/`.
- Runbook commands vs Makefile: `make ci` matches; pip path matches DEVELOPMENT_GUIDE; `make run` vs runbook host/reload differ slightly.
- Deployment guide vs Dockerfile: Dockerfile listens `0.0.0.0:8000` (required for published ports). Runbook `docker run -p 127.0.0.1:8000:8000` is the safe mapping. **`docker-compose.yml` publishes `8000:8000` unbound.** README’s Docker path is `docker compose up --build`.
- README tariff-line claim: **RV-04**.

### 9. Security / privacy

- App does not call live sources; goldens load local JSON. `cli.py` reads only `IOR_HOST` / `IOR_PORT`. No `load_dotenv`.
- `.gitignore` lists `.env`. Prohibited-file scanner flags tracked `.env` and `sk-` patterns in **tracked** files. This working tree **has a gitignored `.env`** containing live-looking third-party API key variables. This review opened that file; values are **not** repeated here. Operator should treat those keys as exposed to this review process and rotate them. Git tracking could not be confirmed from this Windows-side git (see Cannot-verify); CI prohibited scan would fail if it were tracked.
- Dockerfile does not `COPY` `.env`. **`scripts/package_project.sh` zips the project tree without excluding `.env`.** See **RV-02**.
- Synthetic labelling on API evidence rows, UI synthetic rows/warning, dossier JSON/HTML disclosure: present for packaged simulated responses. Public dossier asserts zero synthetic records.
- SPA catch-all can serve any process-readable file. See **RV-01**.

### 10. Release / version / tag procedure

- Package/API/project contract: `0.2.0` aligned (`pyproject.toml:7`, `__init__.py:3`, `project.yaml:4`, `uv.lock` root package `0.2.0`, `test_api.py:21`, CHANGELOG 0.2.0).
- Thresholds `1.1.0`, evidence policy `1.1.0`, sector profiles `1.0.0`, scenarios `1.1.0` remain separate artifacts, as DEPLOYMENT_GUIDE states.
- Tag procedure is Supervisor-only after release-state PR (`DEPLOYMENT_GUIDE.md:138-140`). This branch correctly does not pre-populate tag SHA. No finding.

---

## Findings table

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | REQUIRED REMEDIATION |
|---|---|---|---|---|---|
| RV-01 | HIGH | NFR-010 / Core 03 §8.1–§9 (offline local demo, no auth) still must not serve arbitrary files; owner mandate asked specifically about `spa_fallback` and `..` | `src/ior_mvp/app.py:135-140`; `Dockerfile:15`; `docker-compose.yml:4-5`; `scripts/final_acceptance.sh:747-753`; working-tree gitignored `.env` | `spa_fallback` sets `candidate = STATIC_DIR / path` and returns `FileResponse(candidate)` if it exists as a file. There is no `resolve()` + “must remain under STATIC_DIR” check. `..` segments therefore escape `src/ior_mvp/static/` into the project tree (and, in Docker as the default image user, toward other process-readable paths). Compose publishes host port 8000 on all interfaces. S05 HTTP failure proof never sends `..`. A local `.env` would be a concrete leak target on `START_DEMO_WSL.sh` / uvicorn from this tree. | Resolve the candidate path, reject anything whose resolved location is not strictly inside `STATIC_DIR.resolve()`, and add tests for `..`, encoded `..`, and a file outside `static/`. Bind compose to `127.0.0.1:8000:8000` unless an approved proxy is documented. Do not treat `/nonexistent-static → index.html` as traversal proof. |
| RV-02 | HIGH | BC-02; NFR-004/NFR-010; Core 09 §7 DOD-10; `Makefile` `package` | `scripts/package_project.sh:7-8`; `Makefile:23-24`; `README.md:36-42`; `.gitignore:7` | `zip -qr` packs the project basename and excludes only venv/pycache/`*.pyc`. It does **not** honour `.gitignore`. A workspace `.env` (present here with third-party API-key variables) would enter `Industrial_Opportunity_Resolution_MVP_POC.zip`. S05 `step_source_archive` uses `git ls-files` (safer) but `make package` / README unzip path uses this script. Archive audit also does not deny a `.env` member by name (`final_acceptance.sh:1229-1243`). | Make packaging git-aware (or explicitly exclude `.env`, `.git`, logs, secrets). Fail the archive audit if `.env` or credential basenames appear. Re-run packaging on a clean tree. |
| RV-03 | MEDIUM | Core 07 §4.3 (every sector hard gate resolved, including N/A); Core 06 §7 PP simulation should show resolved internal capability while still REJECT | `src/ior_mvp/capability.py:88-91`; `data/synthetic/SYN-MINISTRY-PP-001.json:72-77` | Hard-gate dict values count as unresolved unless they `startswith("resolved")` or equal exactly `not applicable` / `not_applicable`. PP `tooling` is `"not applicable to resin production"`, so it is unresolved, `route_publishable` is false, and simulated PP D\* is withheld. Golden B-S still REJECT via §7.4 equivalence, so tests stay green. The simulated PP capability matrix shows D\* GATED despite an intended N/A gate. | Treat a documented not-applicable token (prefix or policy-controlled set) as resolved, **or** change the frozen scenario string through the authority gate to an accepted exact token, then assert PP simulated `route_publishable` / D\* in tests. |
| RV-04 | MEDIUM | Docs must not claim synthetic blocks the engine does not load (KL-28; Core 06 §5.1) | `README.md:110-114`; `docs/KNOWN_LIMITATIONS.md` KL-28; `data/synthetic/*.json` `synthetic_inputs` keys | README tells operators the simulation introduces “tariff-line allocation”. No packaged scenario contains a tariff-line or buyer-allocation block; reconciliation reports `NOT_APPLICABLE`. | Remove or qualify that phrase so it matches KL-28 and the actual scenario keys. |
| RV-05 | MEDIUM | NFR-003 / Core 07 §5.5–§6 / mandate unknown→value | `src/ior_mvp/economics.py:87-125`; `src/ior_mvp/decision_engine.py:531-552,652-662` | `incremental_national_value` uses `.get(component, 0)`. `approximate_evsi` uses `.get(..., 0)` for probability, value difference, and costs. Missing keys become numeric zeros, `positive` can still be true, and ADVANCE conjunction can pass. Packaged steel/PP fixtures happen to include the full key sets, so goldens do not catch the fail-open. | Require the declared component keys (or return `NOT_CALCULABLE` / `passes=False`) when any required numeric input is absent; add a test that omitted `displacement` or EVSI probability does not yield a false positive. |

**Counts:** BLOCKER 0 · HIGH 2 · MEDIUM 3 · LOW 0. Unresolved: **5**.

---

## Cannot verify from files

- This session did not re-execute `PYTHONPATH=src pytest -q`, `scripts/verify_integrity.py`, `scripts/demo_smoke.py`, `make ci`, Docker run, or `scripts/final_acceptance.sh`. S05 `acceptance_results.md` records local harness pass `20260902T033607Z-17501` (260 pytest, integrity, Docker). Those logs were not independently replayed here.
- `git log -p -- tests/test_golden_cases.py` could not be run: Windows git reports dubious ownership on the UNC worktree; a WSL git invocation returned no status. Golden **current** assertions match Core 09; **history** weakening is unverified in this seat (S04 review said addition-only).
- Whether `.env` is tracked: `.gitignore` lists it; prohibited-file CI would fail if it were tracked; `git ls-files` was not successfully executed here.
- Whether a particular HTTP client normalises `..` before it reaches `spa_fallback` (browsers vs `curl --path-as-is` vs Starlette TestClient). The **handler** has no containment regardless.
- Browser paint, keyboard traversal, print CSS, and RTL rendering (KL-22).
- Binary DOCX vs `methodology_extracted.md` byte-level fidelity (mirror read in full; DOCX hash taken from the authority manifest).
- Hosted S05 CI, merge SHA, and tag `v0.2.0` (correctly unclaimed).

---

## Residual observations (not findings)

1. Journey A “Synthetic leakage” KPI is hardcoded `"0"` in `app.js:72` rather than read from `integrity`. Isolation is tested elsewhere.
2. Economics panel renders `minimum_effective_support_m == null` as `SAR 0m` (`app.js:318`); metric grid uses `—`. Misleading only on non-golden INVESTIGATE economics payloads.
3. `public_decision_fingerprint` hashes a subset (`state`, `route_code`, `headline`, `missing_facts`), not the full record. `analyze_simulated` does not write `real_decision`; pytest compares full objects.
4. `evidence_policy.advance_gate` is documentation-in-YAML, not an executed predicate (covered in Q1).
5. Public R4-D/R5/R9-S/R10 fire from snapshot `rule_context` flags. Acceptable for Core 05 snapshot-stage POC; not independent recomputation from partner-month cells.
6. `scripts/demo_smoke.py` omits PP simulated REJECT; `test_golden_cases.py` covers it.
7. `docs/BUILD_PROGRESS.md` S05 row is stale vs `.workflow/state.json`.
8. `docs/implementation/DELIVERY_NOTES.md` remains a v0.1.0 evidence note.
9. Dossier HTML uses inline hex CSS (`dossier.py:135-143`); SG-TR-008 glob is frontend CSS/TSX. KL-21 already accepts `styles.css` token debt.
10. Health payload includes `project_root` (`app.py:62`), leaking the install path.
11. `getJSON` stringifies object `detail` poorly for 422 bodies (`app.js:31-32`).
12. S04 residual `has_equivalence` dead local is gone in the staged S05 engine (as claimed).
13. Quantity HHI (Q1 table) is an uncovered methodology formula, not a golden-case failure.
14. Workspace `.env` with third-party API-key variables is operator hygiene **and** a payload for RV-01/RV-02. Rotate those keys. Do not commit the file. Values are not recorded in this document.

Assumptions: packaged JSON is the only runtime scenario set; S05 staged tree is the system under review; Supervisor remains the only merge/tag authority.

---

## Al-muhasibi

Asked: whole-system REJECT/APPROVE against methodology + Core 01–09 + merged S01–S04 + staged S05, with explicit answers and a findings table.

Verified by reading: methodology mirror 1–1890; all nine core docs; configs; snapshots; scenarios; engine/API/UI/tests/CI/Docker/docs listed above.

Independently reproduced on paper: steel capacity 57.5092, gap 46.4908, competition 1.0751, PP gap −24, R11 50.6× > 50, PP tooling string not in the N/A allow-list.

Not re-executed: pytest, integrity, CI, Docker, git history, browser.

Not assumed as fact: S05 hosted CI; tag; that HTTP stacks always block `..` before `spa_fallback`.

---

Verdict: REJECT — 5 unresolved

---

## Re-review round 1

**Reviewer model:** Cursor Grok 4.6 (`cursor-grok-4.6-xhigh`)
**Seat:** Same independent FINAL HOLISTIC REVIEWER. Read-only except this append. Cannot remediate or approve own first-round findings; this is a disposition of the Implementer’s subsequent fixes.
**Scope of this pass:** RV-01..RV-05 production and test diffs listed in the Supervisor brief; Fix round 1 sections of `implementation_log.md` and `test_evidence.md`; refreshed `acceptance_results.md` run `20260902T040100Z-95877`; symlink / `resolve()` edge cases; whether anything new was introduced.

This pass does not re-read the full methodology mirror or Core 01–09. Domain goldens were re-checked only where the fixes touch capability, economics, or Gate B.

### Per-finding disposition

| ID | Disposition | Evidence | Verification |
|---|---|---|---|
| RV-01 | **RESOLVED** | `src/ior_mvp/app.py:137-141`; `tests/test_api.py:89-119`; `docs/implementation/API_REFERENCE.md:81` | `spa_fallback` now does `static_root = STATIC_DIR.resolve()`, `candidate = (STATIC_DIR / path).resolve()`, and serves only when `candidate.is_file() and candidate.is_relative_to(static_root)`. Direct handler call with `../../../pyproject.toml` returns `STATIC_DIR / "index.html"`. Encoded HTTP `..%2F` and `%2e%2e` return 200 HTML with the SPA title and without `pyproject.toml` bytes. `/static/app.js` and `/app.js` still serve the script. |
| RV-02 | **RESOLVED** | `scripts/package_project.sh:5-30`; `tests/test_packaging.py:11-76`; `Makefile:23-24`; `README.md:106-112` | Archive members come only from `git ls-files -z`. Script exits 2 when `rev-parse --show-toplevel` fails or is not the project root. Fixture test writes an untracked `.env`, packages, and asserts no `/.env` and no `/.git/` member. |
| RV-03 | **RESOLVED** | `src/ior_mvp/capability.py:88-99`; `tests/test_capability_economics.py:57-96`; `tests/test_golden_cases.py:34-37,80-84`; `docs/ARCHITECTURE_DECISIONS.md:77`; `CHANGELOG.md:11` | Case-insensitive prefix rule: `resolved*`, `not applicable*`, `not_applicable*`. Param cases include `"not applicable to resin production"` and `"NOT_APPLICABLE"` → resolved; `"pending"` / `"unresolved"` / `""` stay unresolved. PP simulated analysis: `unresolved_hard_gates == []`, `d_star == 0.0`, `immediate_adjacency`, `REJECT` / route 0. Steel simulated D\* remains `0.2667`. Gate B log: `SCENARIO VALIDATION PASS (2 scenarios)`. ADR-009 and CHANGELOG record the PP capability publication change. |
| RV-04 | **RESOLVED** | `README.md:122`; `docs/FINAL_BUILD_REPORT.md` (no “tariff-line allocation” claim); `docs/KNOWN_LIMITATIONS.md` KL-28 | README now states packaged scenarios do **not** contain tariff-line or buyer-allocation blocks and points at KL-28. FINAL_BUILD_REPORT has no contrary claim. Gate B still reports `tariff_line_or_buyer_allocations_reconcile: NOT_APPLICABLE`. |
| RV-05 | **RESOLVED** | `src/ior_mvp/economics.py:8-38,120-164`; `src/ior_mvp/decision_engine.py:543-549,663-669`; `tests/test_capability_economics.py:110-144`; `tests/test_api.py:264-302`; `tests/test_golden_cases.py:49` | Missing national-value or EVSI keys raise `ValueError` naming the keys. Simulation wraps those as `EvidenceIntegrityError` (HTTP 422). Packaged steel ΔNV `198.0` and EVSI `129.3` are unchanged. |

### RV-01 edge cases considered

- **`resolve()` on a missing path:** `Path.resolve()` defaults to `strict=False`. A non-existent candidate does not raise; `is_file()` is false and the handler returns `index.html`.
- **Symlink inside `static/` pointing outside:** `resolve()` follows the link; `is_relative_to(static_root)` is then false, so the handler returns `index.html` rather than the outside target. That is deny, not leak.
- **Absolute path as the catch-all segment** (POSIX `Path / "/etc/passwd"` replaces): the resolved candidate is outside `static_root`, so the handler returns `index.html`.
- **Uncaught `OSError`:** a circular symlink under `static/` could make `resolve()` raise and surface as HTTP 500. There is no user-writable upload into `static/`. Residual, not a new finding.
- **Live runner** `scripts/final_acceptance.sh:747-753` still only GETs `/nonexistent-static`. Traversal proof is the unit/API tests, not the 42-step HTTP failure step. Residual.

### RV-03 / RV-05 domain check

PP `capability_states` are all `0` (`SYN-MINISTRY-PP-001.json:61-70`). With the tooling N/A prefix now resolved, publication of D\* `0.0` / `immediate_adjacency` is the formula outcome, not a planted number. Exact equivalence still selects `REJECT` route 0 (`test_golden_cases.py:80-99`). Steel simulated D\*, S\*, ΔNV, and EVSI assertions in the protected golden file are unchanged.

### Acceptance / suite

| Check | Observed |
|---|---|
| Step table | `acceptance_results.md:64-107` — steps 01–42, every **Exit 0** |
| Status line | `.workflow/logs/s05-fix-round1-acceptance.log:44` — `__FINAL_ACCEPTANCE__ status=0` |
| Clean-pip pytest | `.workflow/logs/s05-final-acceptance/20260902T040100Z-95877/clean_pytest.log:11` — `280 passed, 1 warning in 0.73s` |
| Gate B | `clean_gate_b.log:1-17` — PASS, both planted state/route pairs |
| Added tests vs prior 260 | 20 new nodes (traversal 1 + encoded 2 + static 2 + hard-gate prefixes 8 + PP capability 1 + NV/EVSI unit 2 + packaging 2 + missing-economics HTTP 2) → **280** |

This seat did not re-execute the runner or pytest. Counts are taken from the cited logs.

### New findings

None. No RV-06+.

The following are **not** findings (same class as the first-round residuals, or leftover defense-in-depth the verification points did not require):

- `docker-compose.yml:4-5` still publishes `8000:8000` on all host interfaces. Traversal is now contained; this remains a local-demo bind residual, not a reopened HIGH.
- `step_archive_audit` still does not deny a `.env` member by name (`final_acceptance.sh:1229-1243`). Untracked `.env` cannot enter via `git ls-files`; a *tracked* `.env` would already fail the prohibited-file scanner.
- Hard-gate prefixes live in code (`capability.py:89-93`), not YAML. ADR-009 records that choice.
- API_REFERENCE 422 bullet does not name missing national-value/EVSI keys; the engine maps them through the existing `EVIDENCE_INTEGRITY_ERROR` contract (`test_api.py:271-302`).

### Cannot verify from this pass

- Independent re-run of `make ci`, `scripts/final_acceptance.sh`, or Docker.
- Browser paint / keyboard / RTL (KL-22).
- Whether a particular HTTP client normalises `..` before Starlette (handler-level and encoded TestClient cases were read).
- Hosted S05 CI, merge SHA, tag `v0.2.0`.

---

Verdict: APPROVE — zero unresolved findings
