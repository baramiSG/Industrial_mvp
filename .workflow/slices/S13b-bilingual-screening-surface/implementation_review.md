# Supervisor Implementation Review — S13b Bilingual Screening Surface

Reviewer: owner lead agent (Cursor, claude-fable-5.1) acting as Flight Supervisor and delegated owner. Precedes and does not replace the independent `reviewer-grok` verdicts (`reviewer_findings.md`).

## Seats

Planner `planner-fable` (plan-1, AM-1, AM-2); implementer `implementer-sol` slot 1 (OD-10 — the configured ladder start at `implementer-composer` was skipped for the reasons recorded in s12c/s13a, reported as a deviation); reviewer `reviewer-grok` (one fresh instance for the slice). The owner lead made the two WIP commits under OD-4/OD-16; the implementer never touched git state.

## Environment action

Docker Desktop's WSL integration for the `Ubuntu` distro had been disabled (settings changed 2026-09-09); under owner authorization (OR-6) the owner lead changed the single documented setting (`EnableIntegrationWithDefaultWslDistro: true` in `settings-store.json`), restarted Docker Desktop only (no WSL shutdown), verified `docker info` from Ubuntu and that the unrelated running workload returned healthy. The canonical image `ior-visual-baselines:playwright-1.62.0-noble` was already present.

## Supervisor checks

- Plan gate: B1–B7 review with no finding; owner rulings OD-1…OD-14 (notably OD-4 WIP-commit protocol, OD-10 seats, OD-12 additive evidence route, OD-13/OD-14 amendment consistency) recorded before dispatch.
- T8 hand-off (OD-15): `VISUAL_MANIFEST_OK 56` with the plan change ref; baselines tree OID recomputed from a temporary index (`3297e2f8…` then, after SC-5, `c2b3b66b…`) equal to the pin; all files host-owned; no absolute path in `manifest.json`; 7.2 MB against the 12 MB budget; drift table read and before/after crops inspected (AR/EN sidebar item "06 الفرز / Screening"; version string); two new screens inspected (AR summary, EN record).
- SC-5 (OD-16): verified the changed set was exactly eight paths within the four T8 path groups; harness diff reviewed (fonts ready, three stable scroll frames, integer scroll target, `SCREENING_ANCHOR_NOT_SETTLED` assertion); second WIP commit.
- Candidate: identity recomputed (the implementer's `611de6bf…` did not reproduce; every one of its 85 inventory rows matched the tree byte-for-byte, so only the serialization deviated — it recomputed under the approved recipe to `8fb01e4d…`, equal to the owner's value, and recorded the correction with the original line retained); `data/**` and frozen configs byte-identical to `ab4add6`; `api.py` additive-only (0 deleted lines); goldens exact by direct `analyze`; router mounted before the SPA fallback; ES-module line rule satisfied (CSS is outside the rule and pre-existing CSS files already exceeded 199 lines); KL-34 text aligned with Core 07 step 8; ADR-020 records the executions; UX spec §8 amended.
- Owner `make ci` on the product-identity tree: exit 0 — `INTEGRITY PASS`, four reconstruction passes, `SMOKE PASS`, 2275 tests, 152 functional + 4 visual (log `owner-make-ci-s13b-8fb01e4d.log`, local evidence).
- Stale control record: the reviewer's advisory on `.workflow/state.json` was corrected by the owner lead (single-line, style-preserving); the resulting identity `85b34dfa…` was confirmed by the reviewer as a state.json-only delta.
- Secret scan over all 91 staged paths before commit (Comtrade key literal loaded in-shell without display plus generic credential patterns): zero hits.

## Observations carried forward

- The routed multi-surface shell (UX-02, KL-85) is deferred to a later frontend slice and must be planned there.
- The parity grammar admits ALL-CAPS/snake_case/dotted tokens by construction (KL-89); the `label_leaks` check mitigates label-as-code leaks but cannot detect a prose label authored as a code token — reviewers should keep inspecting rendered Arabic surfaces.
- The passport `access classification` and `terms observation` are not on the passport payload (registry not imported at runtime); a later slice may expose them if the product needs them.
