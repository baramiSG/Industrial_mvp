# Completion — S15a Pharma/API and Fertiliser Evidence

**State:** MERGED (2026-09-13). [PR #29](https://github.com/baramiSG/Industrial_mvp/pull/29) squash-merged as `8053f2b70c4440efb6a00bbc7922e6d14e30377d`; PR CI run `34748809072` and merged-main run `34749303450` passed 5/5. S15a is the evidence child; S15 completes after s15b delivers portfolio/scenarios/goldens.

## Delivered

- Versioned S14-CS-1.1 selection selects four core cases: pharma/API 294110 and 294120; fertilizers 310430 and 310510. It makes `SERIES_GAP_YEARS` an explicit exclusion state, distinct from zero trade.
- Product-family 1.2.0 scope, retained 1.1.0 identity for S14 reproducibility, and source registry 1.5.0 for SPIMACO, SABIC Agri-Nutrients and SFDA. The WCO source is reused rather than duplicated.
- WCO legal identity records, producer/regulator records and write-once raw evidence; third entity artifact; scoped same-day Comtrade partner snapshot for exactly four disjoint S15 units.
- Four CaseBriefs with observed partner evidence and capability/hard-gate uncertainty honestly retained. Builder-derived public proof is `INVESTIGATE` with null route for all four; there are no S15 synthetic scenarios or public snapshot additions.
- Core 02/04/05/09, runbook, ADR-023, limitations, selection/case reconstruction and manifest controls.

## Evidence boundaries

- A selection diagnostic after the later SABIC record changed its input digest but not its selected list. The original pre-acquisition selection was retained and reconstructs from its recorded inputs; the diagnostic was not promoted.
- API-synthesis capability is unverified within the recorded public evidence, not established absent. Tender evidence is recorded as `NO_PUBLIC_TENDER_FOUND` only within the documented search boundary and access limits.
- Etimad/NUPCO paid/login booklet constraints remain explicit. No purchase, registration or bypass occurred.

## Proof

Independent reviewer APPROVE with zero findings; owner CI and exact scratch CI pass; PR CI 5/5. Clean merged-main integrity, 2,600 tests, smoke and all reconstruction stages pass. Default-branch CI is recorded in `pr_record.md`.

## Next

s15b integrates these four briefs into portfolio snapshots and Class-D scenarios; it must expose exclusions to users, preserve public/Class-D separation, apply the approved visual-budget rule and keep MONITOR honestly undemonstrated unless a governed case computes it.
