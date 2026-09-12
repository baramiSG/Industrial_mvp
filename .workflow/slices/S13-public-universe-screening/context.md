# S13 implementation context

Base: `81eac4f2aaaa2710b658b657e627294528785395` (main after PR #20); branch `slice/s13-public-universe-screening` (planner may split into s13a/s13b; children get their own
branches `slice/s13a-…`, `slice/s13b-…` per the S12 precedent, recorded in BUILD_ROADMAP and state.json).

Authority: SLICE_GRAPH §3 S13 (objective; outcome areas B5/B6/B7; scope; depends S09/S11/S07; authority Core 01/02/03/04/07/09 v2 + universe snapshot
§7.5; non-goals), GAP_ANALYSIS rulings R-1…R-6 and interpretations I1/I5/I6/I7, Core 07 rule semantics, Core 05 §3.1/§10/§11, KL-34/40/42/43/45/46,
owner directives of 2026-09-12 (14:46 and 15:09: WITS 200 = availability observation only; verify content/coverage/completeness/provenance before any
run counts as the universe; Comtrade for detailed observations (OR-4), WITS/UNCTAD TRAINS for tariff rates, World Bank indicators where the analysis
needs economic context; classification catalogues, tariff schedules and observed trade kept distinct; honest UNAVAILABLE fallback; UX-01 Arabic
rule-ledger parity into the frontend acceptance criteria).

Data reality (verified 2026-09-12): no Saudi HS6 universe snapshot in the repository (KL-42/46); UN Comtrade v1 API authenticated and returning the
full HS6 import universe for 2023 in one response (5,038 rows, classification H6) — see OR-4 sanitized facts; the S11 `un_comtrade` contract targets the
wrong host and must be replaced under §7.3; ZATCA tariff tree incomplete (KL-43); no production aggregates (KL-47); S12c entity artifact holds 5
companies / 2 plants; S12b store holds 12 documents; frozen public snapshots untouched.

Owner dispositions for planning (each justified in the slice ADR):
1. Decomposition proposal s13a (backend/data/API) + s13b (bilingual Screening surface + UX-01 parity) — planner confirms or refutes with reasons.
2. `un_comtrade` contract replacement: official endpoint, `Ocp-Apim-Subscription-Key` header from the configured env var name, envelope
   `count/data/error`, documented limits observed at the developer portal and recorded; `CredentialEchoed` guard retained; the key value never appears
   anywhere in the repository, logs, records or tests.
3. Universe acceptance criteria as stated in the owner directive (content, reporter, years, flows, HS6 completeness vs provider `count`, DD-18 COMPLETE,
   §11 passports); otherwise UNAVAILABLE with typed dispositions.
4. Screening thresholds only from versioned YAML (new keys → §7.3 with ADR); frozen golden outcomes unchanged; offline runtime/tests/CI.
5. One manifest generation after the ADR and full regression per child.
6. Implementer seat: `implementer-sol` first (OD precedent), `reviewer-grok` reviews; fresh sessions.

Environment: uv-locked `.venv`; `PYTHONPYCACHEPREFIX` outside the repository; `.env` never read by agents (the acquisition CLI reads the env var at run
time only inside the guarded window); runtime, tests and CI offline; live network only in the recorded operator window.
