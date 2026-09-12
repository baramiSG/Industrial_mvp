# Independent reviewer findings — S12a Acquisition Framework and Institutional Sources

**Reviewer:** independent implementation reviewer, Claude Code session (model `claude-fable-5`), operating six read-only review agents; separate from the Codex implementer session (`gpt-5.6-sol`, reasoning high) and from the step-level Codex sub-reviewers recorded in `implementation_log.md`.
**Reviewed candidate:** uncommitted working tree on `slice/s12a-acquisition-framework-institutional-sources`, HEAD `a043ed8dc1d477de50149b39de657bc963e785d7`; candidate identity `98a0f95b83abbfc81b4f7cd9a4f1686e020cc194df02bcc7a31eb4a2a56ace1b` (65 files; 70 with the five slice records).
**Verdict:** APPROVE — zero defects, 2026-09-12T02:41Z (relayed to the implementer session 02:43:56Z).

## Independently reproduced by the reviewer

- `pytest -q` 1,755 passed / 1 warning (rerun twice); integrity PASS; scenario validation PASS (2 scenarios, ground-truth backtests); reconstruction PASS (1 snapshot / 4 artifacts — correctly still one, no institutional snapshot exists); smoke PASS; all four static checks; browser preflight PASS and functional browser gate rerun: 118 passed.
- Frozen decisions: steel public `INVESTIGATE`, steel simulated `ADVANCE` with real state unchanged, polypropylene public `REJECT`.
- Six canonical oracles executed verbatim and passing: [4], [5] exit 0; [12] `MANIFEST_S11_ROWS_UNCHANGED`; [17] `PARTNER_SNAPSHOT_BYTE_IDENTICAL`; [20] `CONFIG_VERSION_PROVENANCE_OK`; [26] `CORE_05_STATUS_ROWS_OK`.
- S11 byte compatibility against real evidence: all 17 stored unit directories recompute to byte-identical unit keys, dicts and query hashes; the S11 partner snapshot rebuilds byte-for-byte (45,297 B) through the new generic builder; top-level `src/ior_mvp/*.py`, `static/`, `browser_tests/` and all frozen data roots untouched; exactly one manifest generation with all manifest rows re-hashed and matching.
- Privacy/envelope policy implemented as approved (processing order, control ranges, `_content_type` routing, envelope table including the `+json` rule, no sniffing — 47 adversarial probes with zero divergences, eight required matcher probe labels, hash-only refusal metadata with a canary proven absent from every stored file, `UNPARSED`-not-`PENDING` for institutional pages); the plan's 18 named tests exist and pass (228 parametrized cases).
- Bug hunt with live reproductions found no defect: parameter values cannot reach filesystem paths; injected loaders cannot poison the production cache; `PRE_OBSERVATION` sources consume zero budget, zero fetches, zero environment reads; no secret can reach stored artifacts.
- Governance records: owner ruling recorded verbatim (`DIRECT_OWNER_RULING`); `plan-5-owner-approved.json` consolidated with the six commands byte-identical to plan-4 and [22] superseded; checkpoint re-pinned; candidate identity independently recomputed to an exact match; slice branch from `a043ed8` with everything uncommitted and nothing staged; `.env` untouched. ADR-016, KL-47–KL-51 and traceability are truthful — nothing is marked COMPLETE and the five `ENDPOINT_UNVERIFIED` outcomes are exactly what the plan's truthfulness rule required.

## Stated limits of the review (preserved verbatim in substance)

The four visual tests and `make ci` were **not** rerun by the reviewer (`make ci` mutates `.venv` via `uv sync`, which the read-only review agents refused). Both remain implementer-reported evidence, corroborated by the recorded logs, the rerun functional gate and oracle [5] proving no baseline change, until hosted CI exercises them on the exact PR head (`browser-gates` runs `make UV=uv e2e`; the uv and pip jobs run the full gate list).

## Low-severity observations — none blocking, none changing the candidate

1. YAML `!!omap` tuple gap in forbidden-key traversal (unreachable; configuration is hash-pinned).
2. Duplicate `units` entries crash write-once rather than being rejected at configuration load (pre-existing S11 pattern).
3. Shared mutable cached-dict behaviour (identical to S11).
4. `<th>` text-join quirk (specification-silent; covered by the bounded-guard clause).
5. `tests/test_acquisition_contracts.py` was listed in the plan's modify set but needed no modification.

These are carried as follow-up notes for the next slice's KNOWN_LIMITATIONS update; they are not corrections to this candidate.

## Disposition

Cleared for delivery in the approved order: identity re-verification → safe staging with fail-closed secret scan → commit → push → PR → exact-SHA hosted CI green → owner merge approval → merge. The verbatim verdict text is retained locally at `.autonomous-workflow/evidence/s12a-acquisition-framework-institutional-sources/implementation-review/approve-20260912T024356Z.md` (SHA-256 `cabeaedfa40c460ded4d459711ea0aeb71b4a90db4b6f96053c87eaf8a09ee5b`).
