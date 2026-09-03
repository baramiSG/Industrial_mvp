# Completion — S08 Public Snapshot Schema v2 and Computed Rule Ledger

**State:** MERGED (2026-09-02). Merge commit `8b6d55cc8f1f10b828f3af7a6a1e045364cb5537`; PR #10; PR CI 5/5; default-branch CI run 33637594756 (5/5).

## Delivered

- Schema v2 public snapshots (`schema_version` 2.0.0; snapshot IDs and as-of dates unchanged; v1 files byte-identical under `data/snapshots/public/historical/v1/`); `public_snapshot.py` validator rejects authored rule outcomes and unknown keys; loader non-recursive and fail-closed.
- `trade_metrics.py`: CAGR over observed span (I3); HHI/largest share on value and quantity (I2); degraded dispersion (weighted quartiles, `outlier_candidate`, descriptive only); §3.3 flow formulas with per-input `UNAVAILABLE` reasons; computed export/import ratio with disclosed consistency ≤ 0.05; established nameplate capability.
- Rules computed from evidence: R1-D cap from config (KL-30), R2 CAGR, R3 dual basis, R4-D with `rules.R4_D.minimum_valid_value_coverage` 0.70 (thresholds 1.2.0), R5 formulas, R9-S typed signals/known-failure gates, R10 designation/resilience, R11 computed ratio AND observed nameplate (steel now FULL/false 0.1144; PP FULL/true 50.6013 vs 50.6). `rule_context` removed; `public_decision_contract` remains until S09.
- Dossier 1.1 bilingual `contradiction_register`; catalogue 1.1.0 (six Supervisor-approved, owner-amendable Arabic strings).
- Migration-equivalence suite incl. live-v2 ≡ converted-v1 equality with a drift negative test; goldens exact by computation.
- KL-32 fixed (`--user` container, ownership sweep); 40 baselines regenerated host-owned.
- Core 02/04/07/09 v2; ADR-012 (SD-1 snapshot-ID policy for schema migration; SD-2 numbers policy); one generator run.

## Review trail

- Plan: 2 rounds — PR-01 computed export/import ratio (steel R11 FULL/false), PR-02 explicit R4-D coverage key, PR-03 Arabic strings approved as owner-amendable defaults, PR-04 single generator run, RI-01 ledger correction → PLAN_APPROVED.
- Supervisor implementation review: SR-01 permanent live-v2 ≡ converted-v1 test (my probe had shown identity) → fixed; validator negative probes rejected authored outcomes.
- Independent review (Grok 4.6): **APPROVE — zero unresolved findings**; steel/PP metrics independently recomputed; nine residuals.

## Evidence

- Local: `make ci` exit 0 — 362 tracked files scanned; threshold scan PASS; integrity PASS; Gate B PASS; `506 passed` (3.12 and 3.14); smoke PASS; 118 + 4 browser nodes.
- Hosted: PR checks 5/5 (browser 5m41s); main run 33637594756 5/5.

## Carried forward

- KL-33 (OPEN → S19): dossier "Supply conclusion" renders raw JSON; §15 structured block owed.
- Reviewer residuals: a `disclosed_dispersion` with `status: calculated` and all-`UNAVAILABLE` diagnostics would still validate (schema gate candidate for S13/S14 when new cases arrive); `public_snapshot.py` size (~1,300 lines) maintainability; authored-outcome grep test covers `rules.py` only (extend to `trade_metrics.py`/`decision_engine.py` in S09); PP R2 UV derivation note; disclosed-ratio tolerance `5/100` appears in two modules (schema constant, not a rule threshold).
- Public R5 physical inputs remain `UNAVAILABLE` until S12 acquisition; `public_decision_contract` removed in S09.
- Owner to confirm or amend: Arabic contradiction strings (owner-amendable), as with the S07 label and digit policy.
