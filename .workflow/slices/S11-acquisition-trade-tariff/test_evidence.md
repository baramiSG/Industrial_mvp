# S11 test evidence (candidate 4, implementer-fable, 2026-09-04)

Local gates on the uncommitted candidate (logs under `.autonomous-workflow/evidence/s11-acquisition-trade-tariff/4/`, referenced by label; every command ran through the evidence runner):

- Every approved-plan verification command (`plan-verification-pass2-00` … `-27`): 27 of 28 exit 0.
  - `[04]` frozen paths incl. `browser_tests/baselines` byte-identical to base `a610b49` — exit 0 (DELIVERY-F-01 proving command).
  - `[06]`/`[09]` CLI contract: `--years` required only on `acquire-universe`/`acquire-partners`/`acquire-baci`; `acquire-tariff --source zatca_tariff --max-requests 1` reaches the offline guard — exit 4 as required.
  - `[12]` permitted generated diff only (Core 05 row changed after the recorded second generator run; acquisition config the only added authority row; the nine public/synthetic/golden manifest rows unchanged).
  - `[18]` INTEGRITY PASS; `[20]`/`[21]` RECONSTRUCTION PASS (1 snapshots, 4 artifacts) with and without manifest checking.
  - `[23]` `pytest -q`: 970 passed. `[24]`/`[25]` demo smoke: steel public INVESTIGATE, PP public REJECT, steel simulated ADVANCE, PP simulated REJECT unchanged.
  - `[27]` `make ci`: exit 0 — scans, integrity, scenarios, reconstruction, 970 default tests, smoke, 118 functional Chromium nodes, 4 visual nodes (40 WebP comparisons against the unchanged baseline manifest).
  - `[26]` exit 1 — requires a `REDACTED` marker in `data/raw/**` because `un_comtrade` declares a credential variable; no such marker can exist while that source is honestly `CREDENTIAL_ABSENT` with zero requests and header-borne credentials. Reported to the supervisor as a plan-level inconsistency; raw evidence was not altered.
- First pass (`plan-verification-00` … `-27`) preserved as RED evidence for the inherited candidate: `[04]` exit 1 (baseline files rewritten), `[09]` exit 1 (`acquire-tariff` demanded `--years`), `[26]` exit 1, `[27]` exit 2 (the first provenance test imported Pillow, which `uv sync --extra dev` prunes).
- TDD: `red-1-inherited-tree`, `red-1b-pins-inherited-tree`, `red-2-frozen-manifest-stale-provenance`, `red-3-tariff-years-and-pins-pilfree` → `green-1-focused-regression` (38 passed), `green-2-tariff-years-and-pins` (93 passed).
- `build-manifests-second-run` (exit 0) and `post-generator-integrity-reconstruct` (INTEGRITY PASS, RECONSTRUCTION PASS, 22 integrity/authority-disclosure tests passed).

Regression tests added in candidate 4: frozen `browser_tests/baselines` tree pin; PIL-free visual-manifest provenance mirror with three detector meta-tests; relocated config loader (path, caching, fail-closed load); acquired-snapshot loaders (kind isolation, validation, caching, test-double rejection); `acquire-tariff` has no `--years` action and its exit-4 probe matches plan `verification[9]`; TARIFF plans one period-free unit.

Acquisition proving tests retained from candidates 1–3: proofs (a)–(e), page-1-of-2 truncation, per-source raw records, manifest gz paths, SELECTION_CHANGED, Core 03/05 v2 markers.

## Candidate 5 (implementer-composer, plan-4, 2026-09-04)

Evidence under `.autonomous-workflow/evidence/s11-acquisition-trade-tariff/1/`:

- **RED:** `test_dd24_credential_echoed_body_not_stored` on inherited `base.py` (echoed body stored; sentinel bytes under temp store).
- **GREEN:** DD-24 guard in `connectors/base.py`; DD-23 `stored_evidence_problems()` + 13 detector meta-tests; transport sentinel proofs (1)–(4) regression pins; repository assertion `test_repository_raw_store_has_no_stored_evidence_problems` GREEN on inherited `data/raw`.
- **verification[26]:** DD-23 semantic command — exit 0 (STORED-EVIDENCE SEMANTICS PASS).
- **Immutability:** `data/raw/**`, `data/snapshots/**`, manifests, config, docs/core, browser baselines byte-identical to candidate 4; no acquire-* run; no generator run.
