# Completion — S12a Acquisition Framework and Institutional Sources

**State:** MERGED (2026-09-12). Merge commit `cc85cbcaa8e1537d8751cced6881dae65791b1f5`; PR #15; PR CI run `34669143106` 5/5; default-branch CI run `34669431254` 5/5.

## Delivered

- The S11 acquisition framework generalized from trade/tariff units to institutional acquisition units and snapshot kinds (`production`, `directory`, `registry`) through a kind registry, stage specifications and a generic snapshot builder — with every S11 raw artifact, unit key, query hash, passport, partner snapshot (45,297 B) and reconstruction result byte-identical.
- Guarded operator-only connectors for GASTAT, Ministry of Industry, MODON, SASO catalogue and SABER registry, with the approved privacy/envelope policy: processing order, control-character ranges, `_content_type` routing, exact envelope table, no content sniffing, hash-only refusal metadata, `UNPARSED`-not-`PENDING` for institutional pages, credential sentinels never stored.
- `config/acquisition_sources.v1.yaml` 1.0.0 → 1.1.0 with S11 source blocks preserved; Core 03/04/05/09 status rows; ADR-016; exactly one authorized manifest generation (2026-09-11 22:31:25 UTC) mirrored into Manifest §11.
- The S12 split (s12a → s12b → s12c) recorded in `docs/BUILD_ROADMAP.md` and `.workflow/state.json`.

## Truthful source outcomes

All five institutional attempts are `ENDPOINT_UNVERIFIED` with zero requests; no institutional row or snapshot exists; reconstruction still yields 1 snapshot / 4 artifacts. KL-47–KL-51 remain open. The framework is proven with test-only parsers and doubles. Later verification requires actual endpoint evidence and satisfaction of the project's access requirements; nothing here proves that the institutions lack public data.

## Review and evidence

- Approved plan-5 (owner-approved amendments of reviewer-approved plan-4): SHA-256 `b38981822fd139ce370245d8a2742d08179beb06997795958af33c8a38311a64`.
- Implementer (Codex `gpt-5.6-sol`) T0–T12 test-first with step-level independent sub-reviews; final independent implementation review (Claude Code `claude-fable-5`) APPROVE, zero defects, on identity `98a0f95b…`.
- Local: 1755 tests; integrity, scenario validation, reconstruction and smoke PASS; 26 executable canonical gates PASS ([22] superseded by owner ruling, never reported PASS); `make ci` incl. 118 functional + 4 visual nodes (implementer-reported).
- Hosted: PR run `34669143106` and main run `34669431254`, five jobs successful on each exact SHA; the browser job independently ran 118 functional and 4 visual nodes.
- Steel public remains `INVESTIGATE`; polypropylene public remains `REJECT`; simulated outcomes and exact values unchanged.

## Carried forward

- s12b (span-addressable document store; Tadawul / producer / Etimad / SASO documents) and s12c (bilingual entity resolution) are the remaining S12 children; the parent completes only after both.
- KL-45 (acquired snapshots not yet consumed by the engine) → S13/S14. KL-42/KL-46 (no Saudi HS6 universe snapshot: Comtrade credential absent, WITS HTTP 403) block S13 universe screening until an authorized acquisition succeeds.
- Reviewer low-severity observations (non-blocking): `!!omap` tuple gap in forbidden-key traversal; duplicate `units` entries crash write-once rather than failing at configuration load; shared mutable cached dict (S11 pattern); `<th>` text-join quirk; `tests/test_acquisition_contracts.py` listed in the plan but unchanged. Recorded in `reviewer_findings.md`; accepted without code change in this slice.
