# S18b AM1 — exact catalogue validator successor

> For agentic workers: apply executing-plans after separate plan approval and coordinator delegated acceptance. This additive amendment changes only the bounds below; the original plan/design/review remain byte-identical. No author self-approval, no Claude attribution.

**Goal:** Restore the approved S18b catalogue1.6.0 boot path while retaining strict fail-closed validation.
**Architecture:** Keep the existing validator and mounted locale endpoint. Change only its exact supported-version comparison and diagnostic from1.5.0 to1.6.0. No fallback, version range, API exception remapping or metadata relaxation.
**Spec:** Approved S18b plan ce2786284e0fafc4bcf89d66eed748362d0b2437c696af193b6471a8be772164; design d648d24330973a8b51be79829ce9188448cf83c0fec8fd1594756231b9fcc7a9; independent R3 review3bc55ba55accfe563a1bb984c937d9d5736a6e36657818569dbec70c0430be74. Task1 already authorizes the1.6.0 catalogue; this proposal repairs its omitted backend file boundary.
**Status:** PROPOSED; implementation and generation remain gated.

## Preparation and evidence

Read the applicable AGENTS, authority manifest, original methodology DOCX (5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9), relevant Core01/02/03/09, configs, golden case tests and extraction golden, roadmap/retained slice records, approved S18b packet, owner overnight/blocker/plan records, writer pause, patch and failed browser logs. Reused prior full governing preparation; read task-specific deltas. After reading, adopted API-contract engineer and provenance auditor personas: the issue is exact API bootstrap compatibility and generated-input accountability, not a new UI design.

Actually applied writing-plans, brainstorming (bounded repair; delegated review replaces a new owner prompt), test-driven-development and writing-good-tests, github-flow, Sanad, al-Muhasibi and Muhasabah. Frontend-design-pro informs the separately investigated graph observations; it authorizes no graphical changes in AM1. Existing token/font/domain constraints override decorative skill defaults.

Retained base306a63b4d24266a63b62dd3835c6585ba328bbcd, tree cd1369dad3e090a954da9faae4570928a2b4a7e4. Writer pause78111440115408c87931054ef5301d5cf0a37fe57ddda3819f8f1088e0835377 binds20changed/newpaths and zero staged. The actual Task1 RED lacks the executive shell. The attempted GREEN instead fails /api/ui-strings/ar with HTTP500; it is not a feature GREEN. Task2 prerequisite errors do not count as meaningful Task2 RED.

DIAGNOSIS.json records independent read-only execution: retained validate_ui_strings rejects actual1.6.0; exact proposed two-literal patch compiled only in memory accepts it. The same probe rejects1.5.0,1.7.0,1.6,null,true,numeric1.6 under the proposed validator. All20paused source hashes still match. This is diagnosis, not candidate test evidence.

## Exact boundaries

Newly permit **src/ior_mvp/config.py only**, at validate_ui_strings lines154–156, matching the author's exact unapplied patch SHA2560e62cef615bce26f73a73b2dadcebe92c6ed88f4b4c3fb14896dcb2a6c2d9811. Preimage SHA256f30759f154c8447aefa8d10c3d33da90e3dbb14b5949eb609da71b7292045063; postimage SHA256b0f74a3276c7531516a86b37f69537dd8fdc51c562c440951907bb09eefe576d. Change `metadata.get("version") != "1.5.0"` to exact1.6.0 and error literal likewise. All other bytes in this source file remain unchanged.

Already-permitted tests/test_ui_catalogue.py: update live metadata version to1.6.0, effective_date to actual reviewed catalogue date2026-09-24, and mounted endpoint version expectation to1.6.0. Add behavior regressions below. Preserve all historical documents and existing assertions except these exact live successor expectations. Already-permitted config/ui_strings.v1.yaml retains1.6.0/date and ordinary S18b key work; AM1 adds no keys. No app.py, graph module, loader, frontend renderer/style, threshold/profile/evidence policy, public/synthetic/golden edits.

Add immutable `.workflow/slices/S18b-bilingual-executive-surface/plan-amendment-1.md` as a byte-identical copy of this approved file; append review reference to existing plan_review.md and truthful implementation_log/test_evidence/reviewer_findings records. Original plan.md/design.md/R3 historical review text stays unchanged. Other documentation remains within the existing plan, with one truthful ADR/control note linking AM1 where required.

## Regression and implementation order

- [ ] Coordinator records separate review+acceptance externally, then author verifies all paused hashes/index and resumes as sole writer.
- [ ] In tests/test_ui_catalogue.py update only the three live version/date expectations, and add `test_current_ui_catalogue_passes_complete_validator`: load actual catalogue, assert validate_ui_strings returns normally. Add parameterized invalid-version behavior using deep copies of the complete catalogue for1.5.0,1.7.0,"1.6",None,True,False,1.6 and missing metadata.version. Every case must raise UIStringConfigurationError. Use independent literals, not an expected-version value read from implementation.
- [ ] Retain both-locale mounted endpoint tests and malformed missing-Arabic-key endpoint test. Before source patch run focused current-catalogue+both-locale endpoint tests; retain actual failure caused by version rejection. Original1.5.0-validator acceptance of a1.5.0 copy is additional meaningful policy-boundary RED once the new negative test exists. No blanket xfail, catch-all exception or mock endpoint.
- [ ] Apply only the exact patch above. Run entire tests/test_ui_catalogue.py, static/UI contract checks from Task1, and the original direct Arabic executive-shell browser test. Both mounted bundles must return200 with all locale strings and policy-sourced synthetic labels; malformed catalogue must still return500 UI_CATALOGUE_INTEGRITY_ERROR with no partial strings. Cache-changing tests use clear_config_caches in finally.
- [ ] Re-run Task2 RED only after Task1 genuinely passes; retain original failed logs. Any further unrelated blocker returns through amendment, not scope drift.

Suggested direct regression core:
```python
def test_current_ui_catalogue_passes_complete_validator():
    config.validate_ui_strings(_catalogue())

@pytest.mark.parametrize("bad", ["1.5.0", "1.7.0", "1.6", None, True, False, 1.6])
def test_unsupported_catalogue_version_fails_closed(bad):
    payload = _catalogue()
    payload["metadata"]["version"] = bad
    with pytest.raises(config.UIStringConfigurationError):
        config.validate_ui_strings(payload)
```
Missing-version test deletes the key and asserts the same typed exception. Existing malformed-key test proves the new valid version does not bypass later validation. These tests exercise validator and API behavior; exact metadata pin alone is insufficient.

## Task6 input-delta amendment and unchanged gates

Expand Task6.1's allowed graph input deltas from Core02/Core03/Core09/UI catalogue to **those same four paths plus src/ior_mvp/config.py with the exact postimage above**. discover_inputs already includes every top-level src/ior_mvp/*.py as ENGINE_IMPLEMENTATION; no discovery code change is needed or permitted. visual_baselines._source_hashes already includes config.py through the same top-level glob; no additional visual discovery change beyond the separately approved executive capture-helper addition. Independent DIAGNOSIS.json confirms actual graph-input row.

Finish this source change before the separately reviewed generation operation binds final graph identity. The graph semantic/count oracle remains925nodes/1045relationships; input/projection/run identities may change, graph domain values/topology may not. Preserve all old write-once projections and canonical evidence. Snapshot count726 expectation is unchanged because this repairs an existing source input and creates no new manifested snapshot file beyond the already planned two projection files. Authority table retains its existing20entries; config.py is not a new authority row. Any count discrepancy is investigated, not forced.

The exact graph operation proposal must list config.py pre/post SHA and full discovered delta. Generate graph→snapshot/authority closure→canonical visual allocation only after that independent operation approval. No generation permission is granted by AM1 alone. Existing128-image matrix, producer/font pins, image budgets, comparison thresholds, strict same-layout R1 geometry/round-trip oracle, compare-only e2e, Task7/full tests/reconstructions/scenarios, two clean-root make ci, exact-candidate implementation review, exact-head hosted checks/review and protected delivery remain unchanged. No borrowed predecessor approval applies to changed bytes.

## Review focus and stop conditions

Review current catalogue accepted, old/future/malformed versions rejected, remaining locale/policy/key checks active, actual mounted endpoint/direct-load path restored, and config.py bound to every generated-input receipt. Any additional source delta, different config postimage, API exception behavior change, graph semantic/count change or unrelated failure stops the dependent operation for separate review. The Arabic graph label and narrow graph clipping observations are **not part of AM1** and require a separate packet/verdict.

## Sanad and Muhasabah

Provenance: source validator/tests/discovery, actual catalogue and original DOCX read directly; failed browser logs and pause are author evidence; DIAGNOSIS.json is independent in-memory behavior evidence. Owner authorization comes from additive20260923overnight/blocker/plan records, not a claimed new owner quote. Assumptions: writer remains paused until coordinator acceptance and original task boundaries stay otherwise active. Risks: catalogue version changes cascade into graph/visual identities, addressed by Task6 expansion and full gates. Unverified: implementation/browser GREEN, generated identities, exact candidate, full local/hosted gates and final review. No source/index/service/data mutation was performed by planner; no candidate approval is asserted. Muhasabah PASS for bounded, sourced planning; product completion remains unverified.
