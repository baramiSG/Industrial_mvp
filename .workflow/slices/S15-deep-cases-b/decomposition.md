# S15 — Deep demonstration cases B (pharma/API, fertilizers): decomposition assessment (mirror)

Machine record: `.autonomous-workflow/plans/s15-deep-cases-b/cycle-1/decomposition-1.json`
(SHA-256 `ea01de65ac299cb2914c01f8f76ec692ce6d691b6530ad868e13b007ac0ab611`; this Markdown is a
human-readable mirror and is not authoritative over the JSON).

Seat: `planner-fable`. Assessed against `main` = `origin/main` = `ab6211f86307ad95a0e61f0597664023f09b7177`
with S14a in flight on the primary checkout (read-only) and s14b prepared in a worktree. The S15 children
base on the merged main after both S14 children (`M15`, recorded at dispatch). Observed at the final check: main moved to `ec859f72` (S14a squash-merged, PR #25) during planning; every in-flight hash recorded equals the merged bytes. Plan only — no
implementation, no product-file edit, no git state change, no network, no `.env` read; every read-only
Python run under `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-planner-s15-pyc` against an
rsync copy of `src/ior_mvp` in `/tmp/ior-planner-s15`.

## 1. Why S15 is split, and where

The four S14 couplings are unchanged in code (portfolio 404, frozen tree OIDs, visual matrix/portfolio
cards, screening input hash with `config/history` retention). A fifth coupling appears for the first time:

5. **Selection-input coupling.** The merged S14 record `CASE-SELECTION-S14-250cd516de0a.json` pins the
   live `config/product_families.v1.yaml` identity (version 1.1.0, sha256 `62fa9c29…`) inside its
   `selection_id` digest; `tests/test_case_selection.py::test_s14_selection_from_frozen_screening_snapshot_matches_recorded_list`
   re-runs the rule with the LIVE families file and asserts `generated == recorded` and exactly one
   `CASE-SELECTION-S14-*.json`; the `config/history` rule admits only hashes referenced by screening
   snapshots. Adopting pharma/fertilizer rows (1.1.0 → 1.2.0) therefore requires: retaining 1.1.0 under
   `config/history/`, resolving the recorded selection input by content hash, extending the history rule
   to case-selection inputs, a rule-version-gated output shape and a `CASE SELECTION RECONSTRUCTION` pass.

| Child | Branch | Touches frozen roots / visual oracle | Minimum cases | Depends on |
|---|---|---|---|---|
| `s15a-case-selection-evidence-pharma-fertilizers` | `slice/s15a-case-selection-evidence-pharma-fertilizers` | **No** (byte-identical proof vs `M15`) | 0 portfolio cases; 4 validated briefs (2 pharma_api, 2 fertilizers; a 5th for 310560 only under OD-4) proven by the public engine in a temporary directory | — (prepared in parallel per OD-11; integrated onto `M15`) |
| `s15b-deep-case-portfolio-pharma-fertilizers` | `slice/s15b-deep-case-portfolio-pharma-fertilizers` | **Yes, once** (snapshots + scenarios + regeneration under the OD-6 budget ruling + one WIP pin commit) | 4 cases → 7 (S14 incl. originals) + 4 = **11 ≥ 10** across all five profiles; optional 5th (MONITOR) → 12 | s15a |

Minimum per the brief is 3 (≥1 pharma, ≥1 fertilizers, +1). The "+1" is the second fertilizers case
(310510 → REJECT via EX-01): fertilizers hold the only Class C domestic producer evidence and the second
distinct outcome class. The second pharma case (294120 → REJECT via EX-03) is the margin case and the
third exclusion class. Substitution: next fertilizers 310221, next pharma 294130.

## 2. Computed candidates (S14-CS-1.1, frozen snapshots; PROVISIONAL identity rows pending WCO text)

Quotas pharma_api 2 / fertilizers 2; viability on; coverage on (False for every S15 line at the base
store — no re-ordering); GAP_YEARS lines excluded `SERIES_GAP_YEARS` before tiering.

| Profile | Variant A (no identity rows) | **Variant B (rows 294190, 293339, 310590)** | Variant C (+ 310510 packaging row) |
|---|---|---|---|
| pharma_api | 294190, 293339 | **294110, 294120** — runner-ups 294130, 293722, 293942, 293331, 293590, 293319 | 294110, 294120 |
| fertilizers | 310590, 310430 | **310430, 310510** — runner-ups 310221, 310250, 310230, 310490, 310520, 310390 | 310430, 310221 |

Exclusions (typed reason — verbatim basis):
- `SERIES_GAP_YEARS` — pharma 293723 (missing import year 2022), 293919 (missing 2023); fertilizers
  310229 (missing 2021 only — H6 series complete), 310530 DAP (T5; missing 2021 only), 310551 (missing
  2024 → also not viable), 310560 (missing 2023). Basis: screening `classification_continuity` GAP_YEARS =
  a year in the observed span without an imports row; missing years ≠ zero trade. S14 families: none.
- `RESIDUAL_CATCH_ALL_SUBHEADING` (PROVISIONAL, entered only from the stored Chapter 29/31 text with
  page/line address): 294190 (2941.90 "Other" of heading 29.41), 293339 (2933.39 two-dash "Other" of the
  unfused-pyridine group), 310590 (3105.90 "Other" of heading 31.05). 310510 KEPT (form/packaging-defined,
  not a residual) — OD-3.
- `VIABILITY_LATEST_NET_WEIGHT_UNAVAILABLE` — 293711 (905 USD, no 2024 net weight); 310420 potassium
  chloride (23.2 M USD, no 2024 net weight).
- `NOT_SELECTABLE` (NO_CANDIDATE) — pharma 293333, 293334, 293372, 293391, 293392, 293530, 293712,
  293941; fertilizers 310240, 310280, 310311, 310319.
- Boundary sets excluded by scope (shown): 3002/3003/3004 (35 lines; the only T1 lines in the pharma
  scope are 300242, 300249, 300259; 3004 imports 6.30 bn USD in 2024); 3101 (1 line, T3).

Selected-line facts (universe H6 2024): 294110 penicillins 12.195518 M USD / 343.0 t (R2 CAGR 0.6519);
294120 streptomycins 9.954578 M USD / 47.8 t; 310430 potassium sulphate 16.676513 M USD / 22,461 t
(exports 8.388 M USD, X/M 0.50); 310510 packaged fertilisers 6.72977 M USD / 2,445.8 t. Titles are
TITLE_UNVERIFIED until the Chapter 29/31 records are stored.

## 3. MONITOR reachability (computed snapshot-wide)

MONITOR (Core 07 §7.6 step 6) needs no material trigger (R1-D, R2, R5–R8, R9-S, R11), at least one
non-material fired signal (R3/R4-D/R10 → partner rows) and a named trigger; it is reachable only in the
simulated branch. On the H6-only series 4,873 of 4,996 CANDIDATE lines fire R1-D or R2; the 123
material-free lines are 50 non-viable (no 2024 import) and 73 GAP_YEARS (53 viable). Under
S14-CS-1.1 as ruled **no selectable line in any family can reach MONITOR**. In scope the only viable
material-free lines are GAP_YEARS-excluded **310560** (112,200 USD / 60 t; H6 positive years 2022 and
2024; R2 not fired) and 293723 (338 USD / 5 kg). Dry run with HYPOTHETICAL partner rows: 310560 computes
MONITOR / NAMED_TRIGGER_MONITOR; without rows the simulated selector has no fired signal. PR-S15-1 and
s14b OD-2 conflict on this line → **OD-4** (default: no waiver, KL, KL-23 clause returned to the owner;
alternative: owner-designated case + Comtrade rows firing R3/R4-D).

## 4. Scenario designs handed to s15b (computed on provisional snapshots)

| Case | Intended | Computed | Lower routes |
|---|---|---|---|
| SAU-H6-294110 / SYN-MINISTRY-PENICILLIN-API-001 | ADVANCE route 1 (registration/GMP-recognition barrier) | ADVANCE 1 ALL_ADVANCE_GATES_PASS; S* 2.0 M SAR; NV 53.0 | 0 fails ROUTE_0_GAP_REQUIRES_ACTION; 2/3/4/6 CONSTRAINT_CLASS_NOT_APPLICABLE; 5/7 blocked |
| SAU-H6-294120 / SYN-MINISTRY-STREPTOMYCIN-API-001 | REJECT route 0 via EX-03 (environmental gate unsatisfiable) | REJECT 0 HARD_EXCLUSION_SATISFIED | 0 passes EVIDENCED_NO_INTERVENTION |
| SAU-H6-310430 / SYN-MINISTRY-SOP-001 | ADVANCE route 2 (information/market linkage) | ADVANCE 2 ALL_ADVANCE_GATES_PASS; S* 1.0 M SAR; NV 53.0 | 1 fails CONSTRAINT_CLASS_NOT_APPLICABLE; 3/4/6 not applicable; 5/7 blocked |
| SAU-H6-310510 / SYN-MINISTRY-FERT-RETAIL-PACKS-001 | REJECT route 0 via EX-01 (heterogeneous residual code) | REJECT 0 HARD_EXCLUSION_SATISFIED; Gate B tariff-line sum PASS | 0 passes |
| SAU-H6-310560 / SYN-MINISTRY-PK-FERT-001 (conditional) | MONITOR | MONITOR 0 NAMED_TRIGGER_MONITOR only with observed partner rows | 0 passes MONITOR_NO_IMMEDIATE_ACTION |

Public branch for every case: INVESTIGATE / route null / ROUTE_CHANGING_EVIDENCE_UNRESOLVED. Route
coverage expected after S15: 0–7 demonstrated; 8 pending S16; MONITOR conditional.

## 5. Open decisions (defaults)

OD-1 split (default two children) · OD-2 quotas 2+2 → 11 cases (alt. minimum 3) · OD-3 identity rows
(default: 294190/293339/310590 if the text confirms; 310510 kept) · **OD-4 MONITOR waiver for 310560
(explicit ruling required)** · OD-5 Comtrade V3 partner window (default open) · **OD-6 visual budget:
92–96 entries breach MAX_TOTAL_BYTES 12 MiB by ≈1.7–2.9 MB → default raise to 16 MiB with recorded
reasoning (explicit ruling required before s15b T8)** · OD-7 sources (WCO 29/30/31; SPIMACO; SABIC AN;
SFDA Drug Companies List; nothing else) · OD-8 Core 07 §7.5 text-only clarification (s14b OD-5 item) ·
OD-9 exclusion exposure (default: selection artifact + authority note + dossier line; alt. UI panel) ·
OD-10 seats (implementer-sol → implementer-fable; reviewer-grok) · OD-11 parallel preparation with the
DD-14 file set.
