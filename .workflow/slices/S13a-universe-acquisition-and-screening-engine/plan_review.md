# Plan review — S13 decomposition and s13a plan (attempt 1)

**Subjects:** `.autonomous-workflow/plans/s13-public-universe-screening/cycle-1/decomposition-1.json` (SHA-256 `93ba2443…`) and
`plan-1-s13a.json` (SHA-256 `9d1f8134…`), authored by `planner-fable` against base `81eac4f2aaaa2710b658b657e627294528785395`.
**Supervisor (owner lead agent) material review — 2026-09-12:** no B1–B7 finding. Independent review by `reviewer-grok` follows; `PLAN_APPROVED` only on its APPROVE.

## Supervisor checks

- B1: five owner-named queues per the owner-approved SLICE_GRAPH with methodology §8.2(c) recorded NOT_CALCULABLE (OD-3, a Manifest §10 interpretation
  decision recorded and reported); ADVANCE never produced by screening; thresholds only from versioned YAML; frozen goldens untouched; `app.py` and other
  visual-manifest-pinned modules untouched in s13a (BF-16) — no conflict found.
- B2: Comtrade facts limited to OR-4's sanitized verification; every other endpoint fact is deferred to the recorded W0 observation; the stored ZATCA
  pages are re-read as `PageNotFound.aspx` (KL-43 correction) — verifiable in `data/raw/zatca_tariff/**`.
- B3: universe acceptance gated on JSON dataset content, `count == rows`, reporter 682, contract period/flow/partner, six-digit HS6, one classification
  per unit, no duplicates, DD-18 COMPLETE, §11 passports; frozen-oracle proof commands present (goldens, byte-identical set, visual manifest, partner
  snapshot byte identity, manifest rows).
- B4: Core 01/02/03/04/05/07/09 v2 text and ADR-019 before exactly one `build_manifests.py` run; §11 mirror; new §7.3 config `screening.v1.yaml` and
  `acquisition_sources` 1.3.0.
- B5: named RED tests per step; engine proven on doubles before any window; dispositions with reason codes.
- B6: credential by env-var NAME only; `ocp-apim-subscription-key` added to the response-header denylist; `CredentialEchoed` guard; 401 recorded as
  sanitized HTTP_ERROR.
- B7: no frontend, no KL-34 code, no graph, no deep cases in s13a.

## Owner rulings (local record `.autonomous-workflow/owner-decisions/20260912-s13-plan-1-rulings.md`)

Decomposition ACCEPTED. OD-1, OD-2, OD-3, OD-5, OD-6 ACCEPTED as proposed; OD-4 noted; OD-7 and OD-8 pre-ruled (stop-and-report on a budget breach;
any official UN Comtrade terms page qualifies, else honest LICENSE_UNRECORDED + escalation).

## IAC (transferred)

- IAC-1 `scripts/reconstruct_snapshot.py` prints PASS lines only when every pass (snapshots incl. universe, documents, entities, screening) succeeds; tamper tests unchanged.
- IAC-2 The implementer prints every verification command from the JSON before running it; the candidate identity uses the IAC-6 procedure with the
  s13a slice-record folder excluded; `PYTHONPYCACHEPREFIX` outside the repository on every command.
- IAC-3 Every operator window's parameters and rationale are logged BEFORE execution; RunReports pasted verbatim; the key never appears in any file,
  log or test (assert with a repository-wide grep for the value's prefix is NOT permitted — the implementer never learns the value; assert only that
  no file contains the env var's value by checking that `IOR_COMTRADE_SUBSCRIPTION_KEY` appears in config as a name only).
- IAC-4 Provider `count` versus stored rows recorded per (year, flow) unit in the RunReport and the universe snapshot coverage; any mismatch → INCOMPLETE.
- IAC-5 Classification catalogue (HS6 descriptions from `includeDesc`), tariff schedule (ZATCA) and observed trade stay distinct artifacts/kinds.
- IAC-6 Size measurements (raw compressed, universe snapshot, screening snapshot) recorded in the ADR and the log.

### Independent plan review — `reviewer-grok`, 2026-09-12: APPROVE, zero findings, six advisories

Record: `.autonomous-workflow/evidence/s13-public-universe-screening/plan-1-review.json`. Both SHA-256s matched; twenty-plus baseline facts and the
OR-4 Comtrade facts spot-checked; the ZATCA `PageNotFound.aspx` claim verified against the stored raw pages. **State: `PLAN_APPROVED`** (D-0001).

Transferred advisories (IAC):
- IAC-7 (A-01) No PASS line until snapshots (incl. new universe/partners), documents, entities and screening all succeed; `SCREENING RECONSTRUCTION PASS`
  contains the tamper-test substring — keep `^RECONSTRUCTION PASS/FAIL` on their own lines; never weaken tamper assertions.
- IAC-8 (A-02) In T9, before the single T11 manifest run, add `data/screening/` to both `allowed_extra_prefixes` tuples in `tests/test_integrity_contract.py`
  with a positive/negative partition probe.
- IAC-9 (A-03) At T3 (after W1, before T11) run `reconstruct_snapshot.py --all --no-check-manifest`; default checking only after T11.
- IAC-10 (A-04) `motCode=0&customsCode=C00` are S11-template parameters to confirm in W0; partner world `0` is the owner's directive; ADR-019 attributes
  only OR-4's verified facts to OR-4; limits, pagination and terms stay OPEN until W0 records them.
- IAC-11 (A-05) Verification [8] is a hint, not fail-closed; [15] cannot surface `NAME=value` — rely on the T1 FakeTransport/CredentialEchoed tests and
  `check_prohibited_files.py`; run heredoc commands with newlines preserved.
- IAC-12 (A-06) TradeObservation has 21 fields; UNICOIL span counts per record are 6/44/65/90; the universe (~40k rows, ~34 MB) fits the 48 MiB budget but
  the ~5k-HS6 screening snapshot may approach 32 MiB — stop on OD-7 if exceeded; W2 batches sized only to the W0-documented limit; if the limit is
  NOT OBSERVED, stop and ask before setting `MAX_REQUESTS` to the full survivor count (OD-5).

### Amendment AM-1 (2026-09-12, owner decision OD-9) — reviewer-grok APPROVE

`implementer-sol` stopped at T2: DD-4's snapshot-level `hs_revisions` cannot be produced because `acquisition/snapshots.py:366` passes only `selected`
to `KindSpec.extra_fields` and the plan pins `snapshots.py` byte-identical. Owner-approved amendment
`.autonomous-workflow/plans/s13-public-universe-screening/cycle-1/plan-1-s13a-amendment-1.json` (SHA-256 `d562ddca…`): no snapshot-level field;
`_validate_universe` (kinds.py) enforces one `hs_revision` per (year, flow) unit and a non-empty `hs_revision` on every row; the engine derives
`hs_revisions_by_year` from rows; `snapshots.py` byte-identical. Independent bounded review: APPROVE, zero findings
(`.autonomous-workflow/evidence/s13-public-universe-screening/plan-1-amendment-1-review.json`). Advisories → IAC-13: prove `snapshots.py` identity
with an explicit `git diff --quiet HEAD -- src/ior_mvp/acquisition/snapshots.py` (verification [8] covers top-level modules only); read AC-3 as the
row invariant; revert any working-tree `extra_fields(selected, rows)` attempt and implement AM-1 only in `_validate_universe`.

### Amendment AM-2 (2026-09-12, owner decision OD-12) — reviewer-grok APPROVE

Triggers verified by the reviewer: single-file screening snapshot 57,164,360 B (5,443 records) over the DD-15 budgets; universe proven (W1-ter
`20260912T143742Z`, 8/8 COMPLETE, 24,195,845 B); PARTNERS template UNAVAILABLE → 59 W2 attempts ENDPOINT_UNVERIFIED. Amendment
`plan-1-s13a-amendment-2.json` (SHA-256 `88abbab2…`): (a) ScreeningSnapshot 1.0.0 stored as a write-once directory (summary + queues + per-HS-chapter
record shards; deduplicated common fields; per-file 48 MiB and total 100 MiB budgets; full validation, reconstruction and manifest coverage; lazy
shard loading); (b) W0-ter read-only Chromium observation of the developer portal for the PARTNERS token (verbatim or NOT OBSERVED); (c) the third
manifest run remains the last. Review record `plan-1-amendment-2-review.json`: APPROVE, zero findings. Advisories → IAC-14: fresh Playwright context
for W0-ter; retire the single-file 32 MiB budget reading in config/ADR; describe the directory layout in Core 04 without a silent schema-version bump.
