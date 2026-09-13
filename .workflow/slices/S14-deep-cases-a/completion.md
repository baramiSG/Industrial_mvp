# Completion — S14a Case Selection, Evidence and Families

**State:** MERGED (2026-09-13). Merge commit `ec859f72a1b438b7e5946334f60a4d72cbbf1fb1`; PR #25; PR CI run `34733383228` 5/5 on head `274e7df`; default-branch CI run `34733717382` 5/5 on the merge SHA. First child of the S14 split; s14b (portfolio, scenarios, goldens, visual matrix) integrates against this main next; the parent S14 completes when s14b merges.

## Delivered

- Governed case selection (`src/ior_mvp/cases/`): rule S14-CS-1 with hashed inputs (product families 1.1.0, disclosure-terms table, `identity_exclusions` carrying the HS revision and verbatim WCO subheading text with stored addresses) → coated steel 721061, 721012; fabricated aluminium 760711, 760429; technical plastics 392010; runner-ups 721069 / 761610 / 391739; 392190 excluded (`RESIDUAL_CATCH_ALL_SUBHEADING`), 721070 excluded (2024 net-weight viability). Selection artifact `CASE-SELECTION-S14-250cd516de0a.json`; re-run byte-identical.
- Authority: `product_families` 1.1.0 (fabricated_aluminium 7604–7614/7616; `technical_plastics_conversion` 3917/3920/3921 from the methodology profile row); `acquisition_sources` 1.4.0 (Hadeed, ALUPCO, Al Taiseer/TALCO, Ma'aden, `wco_hs_nomenclature`; Comtrade PARTNERS template with observed variants); `config/history/` retention with content-hash resolution (frozen screening snapshot reconstructs unchanged).
- Evidence (recorded windows; robots/terms first; write-once; budgets): eight COMPLETE DocumentRecords (WCO Chapters 39/72/76; Hadeed; ALUPCO; TALCO; Ma'aden ×2); WITS partner snapshot `PARTNERS-SAU-WITS-TRADE-2026-09-12` (four lines normalized; 721061 `FORMAT_NOT_PARSEABLE`); Comtrade partner snapshot for 721061 (V1 observed 7 partners without descriptions; an untransmitted variant attempt retained as `VARIANT_NOT_TRANSMITTED`; corrected V3 COMPLETE — 7 partners with unique descriptions, Decimal reconciliation to the universe World value 71,149,266.221 exact); Tasnee/SPIMACO TLS failures recorded, not bypassed; `mentions-v2` and a second entity artifact.
- CaseBrief 1.1.0 with validated `partner_detail` tri-state (missing ≠ zero at every layer) and PublicSnapshot 2.1.0 passport encoding; deterministic builder; five public engine proofs: INVESTIGATE / null route each; 721061 fires {R0, R1-D, R3, R10, R12} from observed partner concentration (never forced). MONITOR/REJECT not reachable from this public evidence (recorded).
- Core 02/04/05/09 text; ADR-021 (three receipted manifest runs; SC-13 incident; OD-18); KLs incl. precise wording for unverified capability and `NO_PUBLIC_TENDER_FOUND`.

## Review and evidence

- Plan-1 + AM-1/AM-2/AM-3: planner-fable; reviewer-grok APPROVE each; owner rulings OD-1…OD-23.
- Implementation: implementer-sol slot 1; reviewer-grok implementation APPROVE zero findings on `78c9b0c6…` (recomputed selection, V3 payload, tri-states, engine proofs, manifest receipts, tests); bounded APPROVE on the CI-F-01 test fix `89ad2d5c…`.
- Local: owner `make ci` exit 0 (2416 tests; 152 functional + 4 visual); pre-push CI-equivalent scratch-clone gate 2416 passed. Hosted: run `34733383228` 5/5 on the exact head. Post-merge local `main`: `INTEGRITY PASS`, 2416 tests, `SMOKE PASS`, five reconstruction passes (4 snapshots/34 artifacts; 20 documents; 2 entity artifacts/44 links; 1 screening; 5 briefs).
- Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`; simulated outcomes unchanged.

## Carried forward

- s14b: five public snapshots + Class-D scenarios into the portfolio; goldens; `project.yaml`; Playwright; §9 route rows; single visual regeneration; the pinned-module obligations (PublicSnapshot 2.2.0 `partner_detail`, R3/R4-D reason codes naming the missing-evidence state, dossier labels; `_scaled` 6-dp pin).
- KL-80: Comtrade parameter semantics remain observations (partner dimension open → per-partner rows; `includeDesc=true` → descriptions), not documentation facts.
- Repository growth: raw store 41.7 MB compressed across 65 artifacts (largest 9.8 MB) within budgets; compression follow-up §7.4 remains.
- Standing rules added during the slice: bytecode isolation; precision of claims; evidence-based exclusions visible to users; pre-push CI-equivalent scratch-clone gate.
