# S10 implementation log

## T0

- Plan hash verified: `05f105f1a7f352adc64ff482484d0c12b7c435219fc101cf277067a7fe32b104`
- Branch `slice/s10-generalized-simulation`, HEAD `66d4835d8c13b0421de271222e2422aff0cb5eb7`
- Nine carried paths confirmed; `T0-OK` printed
- Baseline: INTEGRITY PASS, SCENARIO VALIDATION PASS (2), SMOKE PASS, pytest 811 passed

## T1–T11 (candidate 2)

- Engine, schema, fixtures, browser functional assertions, and first manifest generation completed per plan-2.
- `scripts/build_manifests.py` **run 1 (T13, candidate 2):** updated authority rows for Core 01/02/04/06/07/09, `config/decision_narratives.v1.yaml`, `config/evidence_policy.v1.yaml`, and `generated_on`; snapshot rows for live synthetic 2.0.0 files plus historical `data/synthetic/historical/v1_1/SYN-MINISTRY-PP-001.json` (`06517bb9…`, 3,433 bytes) and `SYN-MINISTRY-STEEL-001.json` (`8867f083…`, 4,711 bytes).
- Visual baseline capture under `S10-generalized-simulation` (two canonical update executions after dom.js `narrativeEntry` fix).

## T12–T14 correction (candidate 3)

### Control documents (F-01)

- `docs/KNOWN_LIMITATIONS.md`: KL-23-sim, KL-25, KL-27, KL-28 → provisional S10 closure; KL-37/38/39 remain open.
- `docs/core/01_PRODUCT_AND_REQUIREMENTS.md`: Journey C bilingual/route-hypothesis/class-if-confirmed bullets; FR-055–FR-059 moved to §6.9; NFR-007 updated.
- `docs/REQUIREMENTS_TRACEABILITY.md`: S10-LOCAL registry; V3-C3/C5-simulated/C7/D5/D6/D8/D9-simulated and FR-055–FR-059 rows; INV-05/INV-09 evidence extended.
- `docs/ARCHITECTURE_DECISIONS.md`: ADR-014 moved after S09 correction round; §7.3/§7.4 classes and permitted generated diff recorded.
- `docs/BUILD_PROGRESS.md`: S10 IMPLEMENTED candidate line.
- `docs/authority/00_AUTHORITY_MANIFEST.md`: §11 Core 01 row synced after run 2.

### Visual oracle repair (F-02)

- Restored eight public workspace WebPs byte-identical from base `66d4835` (accidental 53-pixel host-render cluster rejected).
- Retained 13 simulated WebPs with legitimate bilingual narrative / dossier changes.
- Recomputed `manifest.json` / `manifest.sha256` for restored public entries.

### Generator run 2 (candidate 3, justified)

- Trigger: governed T12 edit to `docs/core/01_PRODUCT_AND_REQUIREMENTS.md`.
- **Permitted diff:** `docs/core/01_PRODUCT_AND_REQUIREMENTS.md` authority row only (`1b2e83a2…` / 14,309 → `59139b9e…` / 14,878); `generated_on` unchanged (`2026-09-03`); snapshot manifest byte-identical.

### Approved path set (candidate 3 delta)

- Reviewer-authorized beyond plan T15 exact-set: `tests/test_authority_disclosure.py` (decision_narratives pin 1.1.0), `src/ior_mvp/static/modules/dom.js` (`narrativeEntry` string/`{text}` renderer), `tests/test_snapshot_migration_equivalence.py` (`localized_missing_facts` in new-field equality set).

### Fixture value choices (T10 summary)

- Steel `minimum_efficient_scale_kt: 50.0` (Class D, equals brownfield increment; ADR-014 owner-amendable default).
- Ten fixtures under `tests/fixtures/simulation/` prove routes 1–4/6/7, MONITOR, max-ΔNV/tie, lower-route blocking, band gates, class-if-confirmed both directions, route-8 refusal, and reconciliation FAIL paths without repository loading.
