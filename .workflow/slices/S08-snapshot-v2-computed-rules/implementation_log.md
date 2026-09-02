# S08 implementation log — PublicSnapshot v2 and computed rule ledger

This is uncommitted local Implementer evidence on
`slice/S08-snapshot-v2-computed-rules`. It is **implementation evidence, not
approval**. It does not claim Supervisor review, independent review, hosted
CI, staging, commit, PR, merge, effective limitation closure, or release.

## Identity, role, and boundary

- Role/model: Implementer, GPT-5.6 Sol. Supervisor: Claude. Independent
  Reviewer: Grok.
- Persona: Senior Deterministic Rules and Data-Contract Engineer for
  evidence-governed industrial screening.
- Data classification: `confidential_demo`.
- Base/HEAD at start:
  `9f045a4ecf929b82a0c4ad9013d255e148bc837d`.
- Branch: `slice/S08-snapshot-v2-computed-rules`.
- Approved contract: `plan.md` and `plan_review.md`, including PR-01 through
  PR-04 and SD-1 through SD-3.
- `.env` was confirmed ignored without reading it. The two untracked
  `.workflow/runs/*.sh` helpers were not read or modified.
- Supervisor-owned S07/state/ignore/control-document hunks were preserved.
  S08 control-document content was appended around them.

## Authority and skills

Read before code: `AGENTS.md`; all three `.cursor/rules/*.mdc`; Authority
Manifest §§5–8 and §§10–11; the complete approved S08 plan, review, persona,
and context; methodology mirror §3.3, §4, §4.1, §5.2.2, §§13.1–13.3,
§§14.1–14.2, and Appendices A–D; Core 02/04/05/07/09; ADR-005/006/008/010/011;
milestone gap/slice documents; five control documents and machine state; S07
records; affected code, scripts, browser harness, config, snapshots,
manifests, and every default test module. The file reader could not render the
binary DOCX; its governed hash matched the manifest, and only the required
search mirror was used for text.

Skills opened and applied: test-driven-development,
verification-before-completion, systematic-debugging, Sanad, Muhasib,
autonomous-delivery, task-standards, and project-orientation.

## Protected baseline

Before migration:

```text
10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7  data/snapshots/public/SAU-H0-721049.json
cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948  data/snapshots/public/SAU-H0-390210.json
 6850 data/snapshots/public/SAU-H0-721049.json
 5572 data/snapshots/public/SAU-H0-390210.json
```

Characterization:

```text
PROHIBITED FILE SCAN PASS (344 tracked files)
INTEGRITY PASS
377 passed, 1 warning in 2.28s
SMOKE PASS
- Steel / public: INVESTIGATE
- Steel / simulated: ADVANCE, real state unchanged
- Polypropylene / public: REJECT generic capacity
- AR/EN extraction golden gate: 100%
```

## TDD and implementation ledger

1. Frozen a test-only schema-v1 rule/decision oracle. Characterization passed
   for both live v1 files; the future history/live test failed because history
   did not yet exist.
2. Added PublicSnapshot 2.0.0 tests first. Initial collection failed with
   `ModuleNotFoundError: ior_mvp.public_snapshot`; validator and schema tests
   then passed. The validator rejects unknown/authored outcome keys, unsafe or
   mismatched history, invalid numbers/units/domains/references/passports,
   contradictory flows, invalid producer/nameplate evidence, and duplicate
   live IDs.
3. Added loader and Gate B tests before their validator calls. Production
   discovery remains non-recursive and v2-only; historical files cannot enter
   the cache.
4. Added CAGR/pair and dual-basis concentration tests before
   `trade_metrics.py`; initial collection failed because the module did not
   exist. Added config-projection and rule tests before R1-D/R2/R3 helpers.
5. Added row/disclosed dispersion, weighted quartile/outlier, four domestic
   flow formulas, nameplate, ratio, R4-D/R5/R9-S/R10/R11, exact result text,
   and boundary tests before implementation. Thresholds changed only to the
   approved 1.2.0 R4-D calibration.
6. The pre-cutover in-memory complete rule diff passed before any v1
   production path was removed:

```text
..                                                                       [100%]
2 passed, 4 deselected in 0.02s
```

7. Copied both v1 files byte-identically into `historical/v1`, verified their
   exact hashes/bytes, wrote the exact field-for-field v2 oracles at the live
   paths, removed every production `rule_context` read, switched
   `evaluate_rules`, and changed `_public_decision` to consume computed
   `R11.fired`.
8. Post-cutover schema/history/rule/state proof:

```text
......                                                                   [100%]
6 passed in 0.02s
```

   The exact allow-list contains individually named additive metrics and
   changed R3/R4-D/steel-R11 result paths; every fired value, ordered rule ID,
   response identity, and public state remains equal. Steel R11 alone changes
   execution `DEGRADED` → `FULL`, while remaining false, and its compatibility
   ratio changes `null` → `0.1144`.
9. Added dossier 1.1 contradiction tests and catalogue 1.1.0 tests before
   implementation. Public and synthetic contradictions are separated;
   public mode never scans an inactive scenario; HTML escapes source content
   and keeps English contradiction text in source-language islands.
10. Added KL-32 command/identity/ownership tests before implementing
    `--user uid:gid`, safe `/tmp` home/cache, `/ms-playwright`, container
    identity assertion, and post-update host ownership sweep.
11. A post-capture full-precision audit added RED tests showing R3, R5, and
    R11 predicates could consume rounded display metrics at very near
    boundaries. The predicates now consume unrounded intermediates and expose
    four-decimal metrics. Additional RED tests preserve disclosed source
    precision and reject contradictory direct-retained/re-export arithmetic.
    All became GREEN before final recapture.

No test was skipped, xfailed, deleted, weakened, masked, or given a
case-specific threshold.

## Data, schema, and computed outcomes

- Live schema: `2.0.0`; unchanged snapshot IDs, opportunity IDs, and
  `2026-08-31` dates; exact `supersedes` links.
- Historical v1:
  - steel `10efb192…f22f7`, 6,850 bytes;
  - polypropylene `cc28e77d…2a948`, 5,572 bytes.
- Live v2:
  - steel `173b45c8…23f0`, 9,992 bytes;
  - polypropylene `02e807de…69c`, 8,919 bytes.
- Steel: R2 CAGR `0.6565`; R3 value HHI `0.36`, quantity
  `NOT_CALCULABLE`; R4-D/R5/R9-S/R10 fire; R11 `FULL`/false at computed
  `0.1144`.
- Polypropylene: R2 CAGR `-0.1642`; R3 disabled on both absent bases;
  R4-D/R5/R9-S fire; R10 disabled; R11 `FULL`/true at computed `50.6013`,
  disclosed `50.6`, consistency true.
- Both public R5 physical inputs remain `UNAVAILABLE`; formula/schema support
  is present, but S12 still owns public acquisition.
- Goldens remain: steel public `INVESTIGATE`; steel simulated `ADVANCE` route
  5; polypropylene public and simulated `REJECT` route 0.

## Authority generator

`scripts/build_manifests.py` ran exactly **once**, after governed edits and
functional/browser regression. The pre-run integrity failure named only the
two live snapshots, thresholds, catalogue, and Core 02/04/07/09.

Generated snapshot-manifest diff:

```text
data/snapshots/public/SAU-H0-390210.json
  02e807de8c016e35341a22ffbc30b78947a0725058641866e3d041dc413cb69c / 8,919
data/snapshots/public/SAU-H0-721049.json
  173b45c821b932a6e82550ceecaa47a23bb98bdec82c8d602e0ef7da1db323f0 / 9,992
data/snapshots/public/historical/v1/SAU-H0-390210.json
  cc28e77dd3b9b85af4dedb864d1371809167f9242a1b4c1101ace6af8402a948 / 5,572
data/snapshots/public/historical/v1/SAU-H0-721049.json
  10efb192d7643c5a9f60bb526cc2f9281d62e755e18978194d8ce151bf8f22f7 / 6,850
```

Generated authority rows:

```text
config/thresholds.v1.yaml
  4e891b9706408f6a661565e09609d0d663e1a00a17bda4e283a4b2ee63d3c47a / 3,887
config/ui_strings.v1.yaml
  cb1881fdfbbbd757c83a01f5ad489ab6587a39a28c387522d982e08338d4a08b / 24,254
docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md
  daab176c8d19fe454731e1f05e93697c0141a9bc7fba5458931a7a0100007c3d / 14,172
docs/core/04_CANONICAL_DATA_MODEL.md
  354008fdec23d15fed6c00f89cd0ad79bb9e9b2fd62a31a219d078d09f89893d / 11,713
docs/core/07_DETERMINISTIC_ENGINE_SPEC.md
  da09c2523764ce35f1bbf7652a3b95a3558ec2a26f87403f7afb40381fbb1dcc / 11,305
docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
  8c59e2d429fa01988977a16615f1c591196ba92d9d5e60e2698470695c31dfa8 / 7,797
```

`generated_on` remained `2026-09-02`; every synthetic/golden and unaffected
authority row remained exact. Manifest §11 was copied from machine JSON and
its equality test passed. No second manifest-generator run occurred.

## Visual baseline generation

The first canonical update succeeded as host UID/GID 1000. A subsequent
full-precision source correction did not change rendered golden output but
made source-tree provenance stale; after new RED/GREEN tests and another full
118-node functional pass, a second corrective canonical capture used the same
approved reference. Both executions are disclosed; only the final set is the
candidate oracle.

Final evidence:

```text
CANONICAL CHROMIUM ASSERTION PASS revision=chromium-1234 executable=/ms-playwright/chromium-1234/chrome-linux64/chrome uid=1000 gid=1000
4 passed, 118 deselected in 32.53s
```

```text
BASELINE OWNERSHIP PASS uid=1000 paths=236 webps=40
1000 browser_tests/baselines/v0.3.0
1000 browser_tests/baselines/v0.3.0/manifest.json
1000 browser_tests/baselines/v0.3.0/manifest.sha256
1000 .artifacts/e2e
```

Final manifest:

```text
manifest_sha256=452db1c96b8e86cdd4ab770f7a83c4e895f1307b5b41eb428cdf34983cfb7b41
manifest_recorded_sha256=452db1c96b8e86cdd4ab770f7a83c4e895f1307b5b41eb428cdf34983cfb7b41
change_ref=S08-computed-rules-dossier-contradictions
entries=40 webps=40 bytes=4998710
browser=151.0.7922.34 revision=chromium-1234
```

Eight desktop dossier baselines were converted and viewed after the first
capture; four representative final desktop dossier baselines were converted
and viewed after recapture. English and Arabic public steel show the
contradiction register and source text; public PP shows the localized empty
state; simulated dossiers retain both policy warnings. No visual defect was
observed. Final compare passed 118 functional and 4 visual nodes.

## Sanad recount

Exact approved-plan recount command output, pasted verbatim:

```text
VERIFIED 43
SPECIFIED 135
DERIVED 18
PROPOSED 63
OPEN 0
```

Implementation Sanad classification: specified behavior came from the
approved plan/rulings and governing methodology/Core; observed hashes,
commands, test outputs, and visual review are VERIFIED; formula results are
DERIVED from frozen values; no OPEN implementation decision was introduced.

## Residuals and recovery

- `public_decision_contract` remains until S09 by explicit scope.
- Public production/re-export flow inputs remain `UNAVAILABLE` until S12.
- The pre-existing Starlette/httpx TestClient deprecation warning remains.
- Standalone system `pytest` is absent; the required alias succeeds when the
  project `.venv/bin` is placed first on `PATH`. uv and documented make targets
  are green.
- Before delivery, rollback is an inverse patch limited to S08 paths. Snapshot
  history/live/manifests and thresholds/catalogue/Core/hash-table changes roll
  back as one reviewed unit; no generator rerun is used to accept unexplained
  bytes.

The candidate remains uncommitted and unstaged for Supervisor and independent
review.

## Fix round 1

SR-01 adds a live-v2-to-converted-v1 anti-drift assertion for both public
goldens. Each rule is compared field-by-field on `execution`, `fired`,
`result`, and `metrics`; the live computed public decision is also compared
with the characterized legacy public decision.

RED was demonstrated without editing evidence files by deep-copying the live
steel case, changing only `trade[-1]["imports_kt"]` in memory, and running the
migration-equivalence module before wrapping the expected assertion failure:

```text
........F                                                                [100%]
E               AssertionError: ('R2', 'metrics')
E                 {'quantity_cagr': 0.6623} != {'quantity_cagr': 0.6565}
E                 {'delta_ln_quantity': 0.5082} != {'delta_ln_quantity': 0.5047}
E                 {'quantity_contribution_share': 0.6594} != {'quantity_contribution_share': 0.6579}
1 failed, 8 passed in 0.05s
```

GREEN after expressing that mutation as the negative regression:

```text
.........                                                                [100%]
9 passed in 0.03s
```

The required full default suite then passed:

```text
506 passed, 1 warning in 2.50s
```

No baseline was recaptured. This is implementation evidence, not approval.
