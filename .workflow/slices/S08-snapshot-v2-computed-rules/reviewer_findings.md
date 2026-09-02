# Independent reviewer findings — S08 Public Snapshot Schema v2 and Computed Rule Ledger

**Role:** Independent reviewer (read-only). Not the Supervisor and not the Implementer.
**Model:** Cursor Grok 4.6 (`cursor-grok-4.6-xhigh`), distinct from Supervisor (Claude) and Implementer (GPT-5.6 Sol).
**Candidate:** uncommitted working tree on `slice/S08-snapshot-v2-computed-rules`, HEAD/base `9f045a4ecf929b82a0c4ad9013d255e148bc837d`.
**Data classification:** `confidential_demo`. `.env` was not read. No files were modified except this findings record.
**Skills used:** `strict-reviewer`, `requesting-code-review` (+ `code-reviewer.md`), `sanad-provenance`, `muhasib`, `muhasabah-gate`, `task-standards`.

This is a review verdict, not delivery, merge, limitation closure, or release.

---

## 1. Scope read (this session, file-reading tool)

1. `AGENTS.md`; `.cursor/rules/00-authority.mdc`, `10-domain-guardrails.mdc`, `20-proof.mdc`; `docs/authority/00_AUTHORITY_MANIFEST.md` §§5, 6, 7.3–7.5, 8, 10, 11.
2. Methodology mirror `docs/authority/methodology_extracted.md` §3.2–§3.3, §4 rulebook, §4.1, §5.2.2, §13.1–13.3, §14.1–14.2, Appendices A–D (DOCX bytes not rendered; identity taken from `authority_hashes.json`).
3. Core 02/04/07/09 via `git diff` against base (v2 markers; PublicSnapshot v2; computed derivations; schema-migration policy). Core 05 §5–§9 read for snapshot-workflow and data-quality gates (unchanged this slice).
4. `docs/milestones/v0.3.0/GAP_ANALYSIS.md` §3 F1–F4, §4 C1/C2/D2/D4/D7/D12, §5, §7 I2/I3, §7A; `SLICE_GRAPH.md` S08 (S09/S10 deferred); ADR-005/006/008/010/011 and ADR-012.
5. Slice records: `persona.md`, `context.md` (SD-1..3), `plan.md` / `plan_review.md` (PR-01..04), `implementation_log.md`, `implementation_review.md` (SR-01 fixed), `test_evidence.md`.
6. Candidate: `git diff` of tracked files; new modules and tests listed in the dispatch; live v2 snapshots and historical v1; `config/thresholds.v1.yaml` 1.2.0; `config/ui_strings.v1.yaml` 1.1.0; hashes, Manifest §11, snapshot manifest; KL-32 container `--user` path; Core 02/04/07/09; ADR-012; control docs.
7. Production rule/metric/engine/dossier/loader code and the migration-equivalence / schema / golden / rules suites, plus in-memory validator probes.

Supervisor-owned S07 post-merge records, control-document edits, and the two untracked `.workflow/runs/*.sh` scripts were treated as out of candidate defect scope, as instructed.

---

## 2. Ground truth (re-run this session)

| Check | Result | Source |
|---|---|---|
| Branch / HEAD | `slice/S08-snapshot-v2-computed-rules` at `9f045a4…` | `git rev-parse` |
| `PYTHONPATH=src .venv/bin/python -m pytest -q` | **506 passed**, 1 Starlette/httpx warning, ~2.29s | this session |
| 3.14 (`UV_PROJECT_ENVIRONMENT=/tmp/venv314` `uv run --locked --extra dev --python 3.14 python -m pytest -q`) | **506 passed**, 1 warning, ~2.27s | this session |
| `scripts/verify_integrity.py` | `INTEGRITY PASS` (snapshot manifest + authority hashes) | this session |
| `scripts/validate_scenarios.py` | `SCENARIO VALIDATION PASS (2 scenarios)`; steel/PP ground-truth back-tests PASS | this session |
| `scripts/demo_smoke.py` | `SMOKE PASS`: steel public INVESTIGATE; steel simulated ADVANCE, real unchanged; PP public REJECT generic capacity; extraction 100% | this session |
| `scripts/check_threshold_literals.py` | `THRESHOLD LITERAL SCAN PASS` (15 Python files; 23 configured numeric values) | this session |
| `scripts/check_ui_contracts.py` | `UI CONTRACT CHECK PASS` | this session |
| `export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs && make e2e` | functional **118 passed**, 4 deselected (~124.5s); visual **4 passed**, 118 deselected (~24.2s) | this session |
| Protected paths `git diff --name-only -- data/synthetic data/golden config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml docs/core/01* 03* 05* 06* 08*` | **empty** | this session |
| Historical v1 SHA-256 / bytes | PP `cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948` / 5,572; steel `10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7` / 6,850 | `sha256sum` + `wc -c` |
| Historical v1 vs base `main` live files | **byte-identical** to `9f045a4:data/snapshots/public/SAU-H0-*.json` | `git show` compare |
| Baseline ownership | `stat -c %u` → **1000** on `browser_tests/baselines/v0.3.0`, manifest, and `manifest.sha256`; host `id -u` = 1000; 42 files under the tree owned by that user | this session |
| Manifest §11 vs `authority_hashes.json` vs file bytes | rows match; SHA-256/byte recount of every hashed file **OK** | this session |
| Snapshot manifest | live v2 `02e807de…` / 8,919 and `173b45c8…` / 9,992; two moved historical rows only; synthetic/golden rows unchanged | this session |

The Starlette TestClient deprecation warning is pre-existing and does not fail the suite.

---

## 3. Independent recalculations

From methodology §13.1 / §14.1 frozen rows (not from engine output):

**Steel 2023→2024**

- ΔlnV = ln(236.9/186.0) = 0.241891437452 → **0.2419**
- ΔlnQ = ln(287.9/173.8) = 0.504707984787 → **0.5047**
- ΔlnUV = ln(823/1070) = −0.262457726779 → **−0.2625**
- quantity contribution share = |ΔlnQ| / (|ΔlnQ|+|ΔlnUV|) = 0.657886525920 → **0.6579**
- quantity CAGR (1-year span) = 287.9/173.8 − 1 = 0.656501726122 → **0.6565**
- export/import ratio = 27.1/236.9 = 0.114394259181 → **0.1144**
- partner-value HHI disclosure **0.36** ≥ configured 0.25 → R3 value basis fires; quantity basis remains `NOT_CALCULABLE`

**Polypropylene 2023→2024**

- quantity CAGR = 56.0/67.0 − 1 = −0.164179104478 → **−0.1642** (does not fire R2)
- computed ratio = 4670.5/92.3 = 50.601300108342 → **50.6013**
- disclosed **50.6**; |50.6013 − 50.6| = 0.0013 ≤ **0.05** → consistent
- 50.6013 > configured 50 (strict) with observed A/B/C nameplates 450,000 + 720,000 t/y → R11 FULL/true

Live engine ledger (`evaluate_rules` on `get_public_case`) matched these rounded metrics and the required execution/fired map:

| Rule | Steel | PP |
|---|---|---|
| R3 | FULL / true (value HHI 0.36; quantity NOT_CALCULABLE) | DISABLED / null |
| R4-D | DEGRADED / true (disclosed) | DEGRADED / true (disclosed) |
| R5 | DEGRADED / true; four `UNAVAILABLE` inputs; penetration NOT_CALCULABLE | same |
| R9-S | FULL / true (4 typed signals; no known hard-gate failure) | FULL / true (2 typed signals) |
| R10 | DEGRADED / true (R3-fired resilience review) | DISABLED / null |
| R11 | FULL / false at 0.1144 | FULL / true at 50.6013 / disclosed 50.6 |

Public selector (computed `R11.fired` only): steel **INVESTIGATE**; PP **REJECT** route 0.

Simulated goldens (this session `analyze`): steel ADVANCE route 5 with effective capacity **57.509** kt, gap **46.491** kt, D\* **0.2667**, S\* **18**, incremental national value **198**, capacity ratio **1.0751**; PP REJECT route 0, gap **−24** kt, support **0**. Real state unchanged under simulation.

`tests/test_golden_cases.py` gained only additive assertions (span/CAGR, R11 execution/computed/disclosed ratios). Frozen state/route/metric expectations remain. `test_r11_missing_ratio_is_degraded_and_does_not_fire` is re-based on steel with `exports_usd_m = "UNAVAILABLE"` (genuine missing exports), not a weakened assertion.

---

## 4. Per-area notes

### 4.1 Snapshot numbers and UNAVAILABLE discipline

Every numeric trade row in the two live v2 files traces to methodology §13.1 / §14.1 or the byte-identical v1 file. Partner-level rows are the exact string `UNAVAILABLE`; quantity concentration is `UNAVAILABLE`; domestic production/retained/re-export flows are `UNAVAILABLE`; criticality is `UNAVAILABLE`; national tariff line is `UNAVAILABLE`. Disclosed steel HHI 0.36, top-two 0.763 / China+Korea, bulk UV 776–864, Austria 1.0 kt at 4179, UNICOIL 250,000 t/y, PP ratios 74.9/52.8/50.6 and UV 1,649 vs 1,097, Advanced 450,000 and Tasnee 720,000 t/y are methodology/worked-case facts. Live v2 JSON is field-for-field equal to `candidate_v2_from_legacy(historical v1)` for both files. `snapshot_id` / `as_of_date` unchanged; `schema_version: "2.0.0"`; `supersedes` points at historical v1 (SD-1).

### 4.2 Rule semantics vs methodology / I2 / I3 / PR-01..02

- R3 computes value and quantity independently; fires on either calculable basis; absent basis is `NOT_CALCULABLE`. Steel disclosed value path is FULL per SD-2; quantity NC. Quantity-only unit test fires at HHI 0.40 with value HHI 0.20.
- R4-D uses dedicated `rules.R4_D.minimum_valid_value_coverage: 0.70` (thresholds 1.2.0, PR-02 rationale). Row path: 0.6999 → DISABLED/`None`; 0.7000/0.7001 → DEGRADED/`True`. Result text forbids cluster/grade. Outlier candidate carries `confirmed_outlier: false`.
- R5 implements M−RX, Mret−Xdom, Qprod+Mret−Xdom, Mret/apparent without coercing unknown→zero. Goldens remain DEGRADED coexistence with named unavailable inputs (KL-26 formula/schema; acquisition residual is S12).
- R9-S: same family + ≥1 typed methodology signal with evidence IDs + no `known_failure` gate. Unresolved gates do not block the screen.
- R10: designation dict → FULL; else R3-fired → DEGRADED; else DISABLED.
- R11: unrounded computed ratio and established observed A/B/C nameplate; disclosed ratio is validated (≤ 0.05) and reported, not used as the predicate (PR-01, Core 07). Steel FULL/false; PP FULL/true.
- R1-D confidence cap is read from configuration (KL-30). Injected `"B"` test projects into metrics and decision effect.
- R2 uses the two latest usable observed years and CAGR over the integer span (I3). 2023→2024 is one year, so CAGR equals single-period growth; goldens unchanged.

Grep of `rules.py`, `trade_metrics.py`, and `decision_engine.py` found no product IDs, no `rule_context`, and no hidden 0.25/0.50/0.70/50 decision literals. `_public_decision` branches only on computed `R11.fired`. Threshold scanner PASS.

### 4.3 Validator strength

In-memory probes against live steel v2, all **rejected**:

- `rule_context`, top-level `fired`, producer nested `fired`, `opportunity.execution`, `decision_effect`, `rules`
- nested unknown `domestic_capability.r9_fired` (unexpected-key, still fail-closed)
- unknown trade key; extra producer `should_fire`
- sentinels `N/A`, `unavailable`, `""` on production
- boolean / NaN / Inf as HHI
- duplicate evidence IDs
- `partner_observations: "none"`
- schema `1.0.0`
- disclosed ratio 99.0 inconsistent with 27.1/236.9

Loader: non-recursive `glob("*.json")`; historical v1 in a subdirectory is not loaded (explicit test); a v1 file copied into the live directory fails `schema_version`. Duplicate live opportunity IDs fail. Gate B now validates PublicSnapshot v2 on the same non-recursive glob.

### 4.4 Migration-equivalence honesty

`tests/test_snapshot_migration_equivalence.py` deep-diffs converted-v1 vs v2 rule maps. The allow-list is additive metric paths plus enumerated changed values (R3/R4-D result text; steel R11 `DEGRADED`→`FULL`, ratio `null`→`0.1144`, result text). Fired map, rule-ID order, identity, and public state stay equal. SR-01 added `test_live_v2_ledger_equals_converted_historical_v1` plus an in-memory `imports_kt` drift negative test. Independently: live JSON == converter output; live `evaluate_rules` equals `_evaluate_rules_v2(converted v1)` on execution/fired/result/metrics.

### 4.5 Dossier contradiction register

JSON `dossier_version` 1.1. Public steel: one public contradiction `S-UNICOIL-SPEC`, synthetic `[]`, `synthetic_status=NOT_APPLICABLE`, `synthetic_records=0`. Simulated steel: public contradiction retained, synthetic `[]`, `NONE_RECORDED`, synthetic evidence rows present and labelled. PP public empty/`NOT_APPLICABLE`; PP simulated `NONE_RECORDED`. Public HTML (`locale=ar`) contains `سجل التناقضات`, the six catalogue strings, `synthetic_not_applicable`, LTR islands for English source/contradiction text, and no `DEMO_GENERATOR`. Public mode does not scan an inactive scenario.

Catalogue 1.1.0 adds exactly the six Supervisor-approved, owner-amendable pairs (PR-03). ADR-012 states they are not owner-approved wording.

### 4.6 Authority discipline

- Thresholds 1.2.0: only the PR-02 R4-D coverage key, rationale, and revision date (plus metadata version).
- Catalogue 1.1.0: only the six key pairs.
- `authority_hashes.json` / Manifest §11 changed only for thresholds, catalogue, Core 02/04/07/09 (plus `generated_on` unchanged at 2026-09-02).
- Snapshot manifest: two live v2 rows and two moved historical rows; synthetic/golden hashes unchanged.
- Core 02/04/07/09 edits are additive v2 markers and the computed-rule / schema-migration contracts; they do not rewrite frozen golden numbers.
- ADR-012 records SD-1 (representation migration, same IDs), SD-2 (no invented rows), SD-3/KL-32, PR-01..04, Supervisor-approved owner-amendable catalogue text, and one planned generator run.
- Protected Core 01/03/05/06/08, sector profiles, evidence policy, synthetic, golden extraction, and the DOCX are untouched.

### 4.7 KL-32 and visuals

`scripts/run_visual_baseline_container.py` emits `--user {uid}:{gid}`, `HOME=/tmp`, `XDG_CACHE_HOME=/tmp/.cache`, `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`, and a host-ownership sweep. `browser_tests/visual_container.py` asserts container euid/egid. Unit tests cover command/identity/ownership. Regenerated tree is uid 1000. Visual compare 4/4. Change-ref in the manifest is `S08-computed-rules-dossier-contradictions`. Twelve of forty WebPs are byte-unchanged versus base (screens whose pixels did not move); that is consistent with a recapture that only differs where rule/dossier text changed, and the oracle still passed.

### 4.8 Records

S08 requirement rows in `REQUIREMENTS_TRACEABILITY.md` are **TESTED** (V3-C2-partial, V3-D2, V3-D4, V3-D7, V3-D12, V3-KL32) with `S08-LOCAL` evidence language. KL-26 formula/schema, KL-30, and KL-32 closures are **provisional** until independent approval, merge, and green CI; the OPEN KL-32 row remains controlling. `BUILD_PROGRESS` does not claim COMPLETE for S08. Implementer Sanad recount command is pasted in `test_evidence.md`. Slice statuses are not above TESTED.

---

## 5. Findings

No unresolved findings.

| ID | SEVERITY | REQUIREMENT | EVIDENCE | PROBLEM | FAILURE_SCENARIO | REQUIRED_REMEDIATION | PROVING_TEST |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

---

## 6. Residual observations (non-blocking)

1. A `disclosed_dispersion` object with `status: calculated` and every quantitative field `UNAVAILABLE` still validates and fires R4-D DEGRADED/true. The approved disclosed path and both goldens carry real methodology diagnostics (steel bulk band + Austria; PP import/export UV). A later schema gate could require at least one numeric diagnostic; it is not a golden or current-fixture defect.
2. Nested unknown keys outside `_FORBIDDEN_RULE_KEYS` (e.g. `domestic_capability.r9_fired`) fail as unexpected-key rather than authored-outcome. Still fail-closed.
3. Dossier “Supply conclusion” still renders `domestic_capability` as a raw JSON island (pre-existing; Supervisor recorded as KL-33 / S19). Not an S08 acceptance failure.
4. `public_snapshot.py` is ~1,310 lines. No Python line-limit rule applies; maintainability only.
5. `tests/test_public_rule_engine_has_no_authored_context_or_product_dispatch` greps only `rules.py`. This reviewer grepped `trade_metrics.py` and `decision_engine.py` as well; both are clean.
6. Public R5 physical inputs remain `UNAVAILABLE` until S12, as scoped. `public_decision_contract` remains until S09, as scoped.
7. PP R2 uses stored 2024 import UV 1,649 with a 2023 UV inferred from value/quantity. The alternative both-from-V/Q ΔlnUV would round to 0.1935; neither path fires R2. Not a golden change.
8. Disclosed-ratio absolute tolerance `0.05` is duplicated as `5/100` in `public_snapshot.py` and `trade_metrics.py` (Core 04 / ADR-012 schema constant, not a hidden R-rule threshold). Scanner PASS.
9. Hosted CI, DOCX-vs-mirror text identity, and pixel-level inspection of all 40 baselines were not independently re-run beyond local gates and the visual compare oracle.

---

## 7. Cannot verify

- Hosted GitHub Actions on a PR head (no PR exists; candidate is uncommitted).
- Binary DOCX text vs `methodology_extracted.md` (hash identity only, same method as prior slices).
- Effective uid inside the canonical update container at recapture time (source, unit tests, and host-owned outputs were verified).
- Visual content of every WebP by eye (canonical compare 4/4 passed; four dossier locales were not screenshot-reviewed by this seat).

---

## 8. Muhasib

Asked: independent read-only review of uncommitted S08 against the approved plan, methodology, Core v2, and SD/PR rulings.
Read: the ritual set plus candidate diffs and production/test modules named above.
Verified: the listed suites/gates, protected-path emptiness, historical hashes/bytes vs `main`, Manifest/hash recount, independent arithmetic, live rule ledgers, simulated exacts, validator smuggling probes, live≡converted, dossier isolation, `--user` source and uid 1000 ownership.
Assumed: Supervisor-owned S07 records are legitimate; two untracked run scripts are out of scope; DOCX matches its hashed identity.
Invented: nothing. Did not edit production files. Did not approve this seat’s own implementation.

Verdict below is for this candidate identity only. Merge, hosted CI, and limitation closure remain Supervisor-owned.

Verdict: APPROVE — zero unresolved findings
