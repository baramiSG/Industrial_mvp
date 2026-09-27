**Verdict: APPROVE the M1 correction plan**, SHA-256 `b84f53f6ba5c04e89dc050f514ae6677e63d15e6a49d8cd9ade6d0c69c13b8ec`. This approves the plan only, with two binding conditions below. It does not approve the implementation or the successor, and it does not mean READY_FOR_CI. Everything was read-only: no edits, tests, Git writes or services.

## Claims verified in the actual code (proof 241e4df / tree fe98722)

- **The cause is as stated.** Per-producer `same_process_family = (family == sector)` compares the producer's recorded family (`polypropylene`) with the sector profile (`technical_plastics`), which are different vocabularies. `config/product_families.v1.yaml` maps HS 3902 to `polypropylene_primary_forms` and HS 7210 to `coated_steel`. The same `technical_plastics` sector also contains the separate `technical_plastics_conversion` family (3917/3920/3921), so the planned sector-versus-family negative test for 392010 is meaningful.
- **The reuse is implementable without touching `screening/config.py`.** `family_for_hs6(hs6, value=None)` (lines 135–144) accepts an explicit config value, and `validate_product_families` (lines 100–118) and `_load` exist separately from the cached `product_families_config()` (lines 128–132, `lru_cache` bound to `PROJECT_ROOT`). Loading and validating the root's own YAML and passing it explicitly is feasible, and that is the right correction to the cached-default risk.
- **The input-closure gap is real.** In `discover_inputs`, the `ENGINE_IMPLEMENTATION` group globs only `src/ior_mvp`, `src/ior_mvp/cases` and `src/ior_mvp/graph`, so `screening/config.py` is not a graph input. `product_families.v1.yaml` is already bound through the `AUTHORITY_FILE` group. Admitting the helper as a required, fail-closed input is correct.
- **The unknown-family semantics are right.** `evaluate_r9s` (`rules.py:1246–1275`) maps `UNAVAILABLE` to `DISABLED` with `fired=None`. Passing the sentinel without editing `rules.py`, and exposing null (not `NOT_CALCULABLE`) in the scoped row, correctly keeps unknown separate from false.
- **The expected outcomes are correct.**
  - SABIC fires, because it solely owns the `P-SABIC` `adjacent_output` signal.
  - Advanced and Tasnee become same-family true but stay unfired, because the shared `P-ADVANCED`/`P-TASNEE` core-process signal is not fanned out to either.
  - Steel Hadeed and UNICOIL are unchanged.
  - The reference ledger and the eleven decisions are unchanged.
  - The scoped semantic-delta gate (exactly three PP rows) and the stop-on-unexpected-delta rule are adequate.
- **Governance is proportionate.** The ADR-033 record plus the Core02 mapping follow the correct authority order. The authority manifest and hashes regenerate through the existing gated sequence, while the DOCX, config, public, golden and synthetic bytes stay unchanged. The plan is also correct that byte-equal captures are an observation, not a requirement: only generated-token differences with unchanged geometry and content are admissible, and each must be inspected.

## Binding conditions

1. **Close the package initializer too.** Importing `ior_mvp.screening.config` first executes `src/ior_mvp/screening/__init__.py` (117 bytes; it imports `.config`). Admit that exact file as a required `ENGINE_IMPLEMENTATION` input, fail-closed, alongside `config.py`, so the executed import path is fully bound. The expected input count then becomes 238 + 2, confirmed by actual membership inspection. No other screening modules.
2. **Stop and report if strict R1 fails.** The regenerated engine and projection IDs change the native run token, and the held M-A4 v2 geometry successor was never implemented. If the new token crosses the known 459 px reflow threshold, the original strict R1 will fail. In that case root must stop, report, and not apply M-A4 or any waiver unless it has been separately reconciled on the real evidence.

## Nonblocking notes

- `candidate_discovery._family_id` also calls `family_for_hs6` with the cached default config. Normal same-root builds are unaffected; the new input binding closes its dependency. Explicit root threading there is outside M1 scope.
- Null edge properties are only reachable from the unknown-label test fixtures, not from the actual artifact. The live-equality comparison remains null-safe.

**Scope:** plan approval for the bounded M1 correction. Sol's red/green diff, the scoped generation and delta inspection, the capture, the fresh freeze, the full affected gates and this same implementation review all remain pending. Hosted CI and M-A3 live Aura are later.

**Muhasabah: PASS.** Each point is checked against the actual source lines and the governed config. Unexecuted outcomes are labelled as expectations.
