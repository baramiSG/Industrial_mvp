# S14 — Deep demonstration cases A: decomposition assessment (mirror)

Machine record: `.autonomous-workflow/plans/s14-deep-cases-a/cycle-1/decomposition-1.json`
(SHA-256 `48741467ed2e3d6185cb0e5aac13b56d6c9d81847a3b114b960547740b877f3a`; this Markdown is a
human-readable mirror and is not authoritative over the JSON).

Seat: `planner-fable`. Assessed against `main` = `origin/main` = `ab6211f86307ad95a0e61f0597664023f09b7177`
(PR #24 records-only on the S13b squash `cdf6ab0`; product tree identical). Plan only — no
implementation, no product-file edit, no git state change, no network, no `.env` read.

## 1. Why S14 is split, and where

Four couplings, each verified in code this session, fix the seam:

1. **Portfolio coupling.** `public_cases()` globs `data/snapshots/public/*.json`;
   `list_opportunities("simulated")` analyses every case and raises `ValueError` for a case without a
   scenario, which `app.py` turns into HTTP 404 for the whole simulated portfolio. A public snapshot
   cannot land without its scenario in the same PR.
2. **Frozen-tree coupling.** `tests/test_frozen_public_evidence_pins.py` pins the git tree OIDs of
   `data/snapshots/public`, `data/synthetic`, `data/golden`, `browser_tests/baselines` and the bytes of
   the four golden files. Any added case file moves two tree OIDs → owner-lead WIP protocol (s13b OD-4).
3. **Visual-oracle coupling.** The 56-entry matrix includes the two portfolio screens (KPI count,
   imports sum, one card per case); `browser_tests/harness.py` `CASES` has two cases and the portfolio
   journey asserts `to_have_count(2)`. Adding cases forces one canonical regeneration.
4. **Screening-input coupling.** The frozen screening snapshot records the sha256 of
   `config/product_families.v1.yaml` and `config/acquisition_sources.v1.yaml`;
   `scripts/reconstruct_snapshot.py --all` (in `make ci`) validates with `check_inputs=True`, so the PR-1
   family change and any new producer source contract break CI with `INPUTS_CHANGED` unless a
   superseded-input retention rule is introduced first.

The brief's suggested (a)/(b)/(c) partition would put snapshots into the portfolio without scenarios
or need two visual regenerations. The partition that respects all four couplings is:

| Child | Branch | Touches frozen roots / visual oracle | Minimum cases | Depends on |
|---|---|---|---|---|
| `s14a-case-selection-evidence-and-families` | `slice/s14a-case-selection-evidence-and-families` | **No** (byte-identical proof) | 0 portfolio cases; 5 validated briefs built into a temporary directory and proven by the public engine | — |
| `s14b-deep-case-portfolio-scenarios-and-goldens` | `slice/s14b-deep-case-portfolio-scenarios-and-goldens` | **Yes, once** (snapshots + scenarios + regeneration + one WIP pin commit) | 5 cases (2 coated steel, 2 fabricated aluminium, 1 technical plastics) | s14a |

"≥5 across three profiles" is met at the s14b merge. Each child: one branch, one PR, exact-SHA CI,
reviewer-grok sole approver, one `build_manifests.py` run.

## 2. Child goals (abridged — the JSON `goal` text is binding)

**s14a (evidence).** Selection rule S14-CS-1 as code with a pinned recorded list; `product_families`
1.1.0 (PR-1) with superseded bytes under `config/history/` and content-hash resolution in the screening
input check; `acquisition_sources` 1.4.0 with producer sources Hadeed, ALUPCO, Al Taiseer/TALCO,
Ma'aden; recorded windows W-A (disclosures), W-T (PR-5 TLS observation), W-P (WITS partner detail for
the five HS6, OD-5); mentions-v2 and a second entity artifact; CaseBrief 1.0.0 + deterministic
PublicSnapshot builder + five briefs; Core 02/04/05/09 text, ADR-021, KLs, split record; one manifest
run. Both goldens exact; frozen roots and visual oracle untouched.

**s14b (portfolio).** Build the five snapshots into `data/snapshots/public/` (ids `SAU-H6-<hs6>`);
author five Class-D scenarios (contract 2.0.0, planted ground truth, Gate B, bilingual narratives);
Core 09 §2.4 goldens C–G; `config/project.yaml` list (7); `tests/test_golden_cases.py` extended;
browser `CASES` (7) and journeys per case; visual matrix +5 public-workspace screens (76 entries,
budget-checked) regenerated once; frozen-pin WIP commit; SLICE_GRAPH §9 rows; ADR-022; one manifest run.

Intended planted truths (PROPOSED; each reached by computation or replaced by the honest computed
state): 721061 → simulated ADVANCE route 3 (certification); 721012 → route 7 (greenfield);
760711 → route 6 (technology/JV); 760429 → route 4 (demand aggregation); 390220 → REJECT route 0
via EX-02 (market below MES).

## 3. Deterministic case selection (rule S14-CS-1, computed read-only from the frozen snapshot)

Inputs: `SCREENING-SAU-2026-09-12-9b6b22032fd8` (summary `e06cb1c2…`, queues `4519f984…`),
`UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12` (`758acdb4…`), family sets coated_steel {7210},
fabricated_aluminium {7604–7614, 7616} (PR-1), technical_plastics {3902}, stored DocumentRecords.

PR-7's literal rule (robust queue, then high-EVSI queue, ∩ families) is **empty** for all three
profiles: every screened HS6 in these headings is a CANDIDATE sitting only in `likely_false_positive`,
because 4,542/5,443 records carry the universe-wide `classification_continuity` flag (2021 rows are
H5, 2022–2024 rows are H6). The rule therefore extends deterministically:

1. membership by HS4; 2. exclude frozen 721049/390210; 3. tiers T1 robust → T2 high-EVSI → T3 LFP with
only the continuity flag → T4 price-led growth → T5 ratio warning → T6 unqueued → T7 NO_CANDIDATE
(never); 4. viability: positive 2024 import net weight (Gate B demand reconciliation must be checkable);
5. in-tier order: disclosure-covered (stored producer records at base) → R2 fired → 2024 imports USD
desc → hs6 asc; 6. quota 2/2/1, rest = substitution order.

| Profile | Selected (default variant) | Substitution order | Excluded by viability |
|---|---|---|---|
| coated_steel | **721061** (Al-Zn coated; UNICOIL "Hot Dip GL" EPD stored; R1-D; 71.15 M USD, 93,232 t), **721012** (tinplate <0.5 mm; R1-D, R2; 115.37 M USD, 104,575 t) | 721069, 721041, 721011, 721020, 721090 (T4) | 721070 (PPGI, R2, 85.24 M USD, no 2024 net weight), 721030, 721050 |
| fabricated_aluminium | **760711** (foil ≤0.2 mm; R1-D, R2; 180.58 M USD, 53,679 t), **760429** (alloy profiles; R1-D, R2; 51.78 M USD, 9,190 t) | 761610, 760421, 760519, 760511, 760720, 760692, 760719, 761490, 761290, 761410, 760410, 761210, 760900, 761691, 761100, 760529, then T4 760612, 761010, 761090, 761699, 760521, 761300 | 760820, 760691, 760611, 760810 (T4) |
| technical_plastics | **390220** (polyisobutylene; R1-D, R2; 2.07 M USD, 610 t) | 390230 (T4), 390290 (T4) | — (390210 frozen, T5) |

Without the disclosure-coverage key the coated-steel pair is 721012 and 721069; aluminium and plastics
are unchanged.

## 4. Honest outcome map

Public branch: all five cases reach **INVESTIGATE** (R1-D fires on ≥3 positive years; demand and
identity fields unresolved). Public **REJECT** via generic capacity needs a ratio > 50 with an A/B/C
nameplate — no family line except the frozen 390210 exceeds 50. **MONITOR** needs no material trigger,
which R1-D defeats in both branches (the simulated selector receives the public rules). Distinct
outcomes are exercised as public INVESTIGATE (5), simulated REJECT (EX-02) and simulated ADVANCE on
routes 3, 4, 6, 7; MONITOR stays demonstrated by the S10 fixture only (KL).

## 5. Open decisions for the owner lead (defaults in the JSON)

OD-1 split shape (two children); OD-2 selection keys (warning tiers; viability filter — waiving it
would select 721070 PPGI instead of 721012; disclosure-coverage key — dropping it selects 721069
instead of 721061); OD-3 technical_plastics extension (default 3902 only → 390220; or 390230; or an
owner-cited extension); OD-4 superseded-config retention (`config/history/` + content-hash resolution)
versus a +52.8 MB screening rebuild; OD-5 WITS partner window W-P; OD-6 producer source set (no
Tadawul attempt, no PP producers); OD-7 accept unreachability KLs; OD-8 ids `SAU-H6-<hs6>` and H6-only
series; OD-9 s14b matrix extension; OD-10 seats (implementer-sol first).

## 6. Sanad / muhasib

Every coupling and every fact in §3–§4 was verified by direct reads and read-only computations at
`ab6211f` (paths and lines in the JSON `baseline_facts`). Ledger figures are leads, never evidence;
coverage rests on stored DocumentRecord titles/lines only; no UNICOIL nameplate span was found in the
store and none is assumed. The planner did not implement, commit, fetch or read `.env`.
