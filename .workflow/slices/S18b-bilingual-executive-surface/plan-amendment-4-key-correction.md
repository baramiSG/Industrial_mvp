# S18b AM4 additive capability-key correction

> Implement only after a different reviewer approves this exact addendum and root records delegated acceptance. Use the existing separately assigned writer and executing-plans workflow. This author cannot approve the correction or the unfinished implementation.

**Goal:** Rename the internal unknown-capability catalogue key from `executive.capability.state.U` to `executive.capability.state.u`, preserving visible/domain `U` and every approved English/Arabic value.

**Architecture:** Apply exactly two YAML key-name edits, retain the unchanged full catalogue validator, add one narrow regression, and use the lowercase key when the already-approved Task5 consumer is subsequently implemented. No version, schema, grammar, domain, styling or API expansion.

**Spec:** Parent AM4v2 plan `fb0bc97072c65b18aec7807c31b63c14bab48f7ead6eca217794725bcc4a65ac`; original companion `0929af623764f8008aae70ab79007c829d3c73c9f16998bef03270eb2ad00bbf`; original15-pair copy `b4bf32029506def8cf36230f6e96e8aa1a74e90f68d4d7c33727700044da89e6`. Preserve both original45-entry v1 and53-entry v2 packets, their historical assignments/reviews and any byte-identical repository copies. This addendum overrides only the machine spelling `.state.U` in those references. It does not rewrite the parent plan or reinterpret state U.

**Status:** Proposed correction. The parent copy contained an invalid uppercase machine key; this is the planner's copy-specification defect. Four current Task4 tests failed before their rendering checks because catalogue loading rejects that key. Correcting it does not validate the unfinished passport code, Task5 UI or the rest of AM4.

## Preparation and exact evidence

Reused full governing AGENTS/authority/original-DOCX/Core preparation and refreshed AM4v2/companion/catalogue, current source schema, complete failure cause, source pause and proposed patch before choosing personas. The current worktree authority manifest's normative text matches the previously read authority; its generated hash table is not permission to alter rules. After these reads, adopted schema-contract engineer and regression-review personas. Applied installed writing-plans, systematic-debugging, verification-before-completion/test-driven development, GitHub-flow, Sanad, al-Muhasibi and Muhasabah. Owner/root delegation permits this independently reviewed bounded correction, not author self-approval.

Actual unchanged `src/ior_mvp/config.py` SHA-256 `b0f74a3276c7531516a86b37f69537dd8fdc51c562c440951907bb09eefe576d` defines `^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$` and raises `UIStringConfigurationError` on an invalid key. Current catalogue has the exact original uppercase key once per locale. `am4-task4-unit-green-r1.log` records **4 failed /63 passed**, all four at `UI catalogue key is invalid: executive.capability.state.U`; the filename is not a GREEN result.

Writer patch `30768c973114dda116257c65463ffa3924c215e2cfe29e6be5a121c7cefcc79d` is unapplied. Catalogue preimage `89c182ec233b71053673e1413852e1706ab7c7ee70b3425f65e1dcb190a01670` becomes `ebbedde20eb9b454ca635681cac8e33484144d6a9340385f63d4dd4a0428e874` under exactly those two key edits. My isolated unchanged-validator probe independently rejects the original complete catalogue and accepts that exact proposed postimage, with metadata/locales/every other value preserved and all corrected15 key pairs valid. The different reviewer's independent diagnostic is also retained and attributed, not treated as final approval.

The writer's85-path pause checkpoint `45fcf23ecbea299b93f124eb6f2df557a8a84f6bc6369f95d032b46a41e4efbc` matches every selected path at planning verification. Task5 has not started: actual `capabilityDetail` still renders bare numeric/unknown values and has no state-key lookup. No existing consumer patch is invented.

## Exact bounded changes

| Path/reference | Sole correction permission |
|---|---|
| `config/ui_strings.v1.yaml` | Apply the supplied two-line key rename, one EN and one AR. Metadata/version1.6/date, all values, every other key, total15 additions and both-locale parity remain exact. |
| `tests/test_ui_catalogue.py` | Explicitly admit exactly the one regression body below, using existing `_catalogue`, config and pytest imports. Earlier parent/AM1 catalogue authority is not treated as blanket AM4 test permission. No other assertion change in this file. |
| `src/ior_mvp/static/modules/executive/simulation.js` | During original Task5 implementation, the unknown visible state U resolves through literal `executive.capability.state.u`; numeric0–3 mappings retain their approved keys. The consumer does not yet exist. All other consumer work remains solely within original Task5. |
| `tests/test_executive_frontend_contract.py`, `browser_tests/test_executive.py`, `browser_tests/test_executive_accessibility.py` | Existing AM4 Task5 tests use the corrected machine key and independently assert visible U, exact locale meaning, unchanged unknown/known semantics and simulation disclosure. Extend only their already permitted legend/unknown assertions; no new named browser function or invented existing reference. |
| Slice/control records | Add `.workflow/slices/S18b-bilingual-executive-surface/plan-amendment-4-key-correction.md` as this exact approved addendum and `am4-catalogue-additions-corrected.json` as the exact corrected companion. Append exact review/acceptance/RED-GREEN references in existing plan_review/implementation_log/test_evidence/reviewer_findings and an additive ADR/control note where needed. Preserve original plan/companion/copy records. |

`CATALOGUE-ADDITIONS-CORRECTED.json` SHA-256 `e140d77756c915c7f5458e5039d220790fdb746b6a143c725dfe6e959c43c2e6` is the exact original15-pair JSON with only the two internal key strings renamed. The companion's seven-key list is read additively as `.state.u`; the visible `U` and all prose remain unchanged. Do not edit frozen source packets or replace their historical hashes.

`config.py`, its `UI_KEY_PATTERN`, all global key/technical/parity grammars, API/errors, evidence policy, domain state/data/unknown penalty, labels, metadata, thresholds, dependency locks and generation algorithms are **unchanged**. No uppercase alias or case-normalizing lookup is introduced. Fifty modules,23 browser files and76 named browser functions remain exact. The new unit regression does not change browser inventory.

## Precise regression and resumption sequence

1. Root records different-reviewer approval and delegated acceptance externally. Writer reconfirms the85-path pause checkpoint and catalogue/config preimages before resuming; any unexpected delta returns for review. Preserve original failure log and all prior evidence.
2. Add exactly this meaningful regression to the already existing test file, before applying the key patch:

```python
def test_am4_unknown_capability_key_is_lowercase_and_uppercase_fails_closed() -> None:
    payload = _catalogue()
    config.validate_ui_strings(payload)
    meanings = {
        "en": "Unknown; evidence acquisition required.",
        "ar": "غير معروفة؛ يلزم جمع الأدلة.",
    }
    for locale, meaning in meanings.items():
        values = payload["strings"][locale]
        assert values["executive.capability.state.u"] == meaning
        assert "executive.capability.state.U" not in values
    for locale in ("en", "ar"):
        values = payload["strings"][locale]
        values["executive.capability.state.U"] = values.pop(
            "executive.capability.state.u"
        )
    with pytest.raises(
        config.UIStringConfigurationError,
        match=r"UI catalogue key is invalid: executive\.capability\.state\.U$",
    ):
        config.validate_ui_strings(payload)
```

Run this exact test against the paused source. Retain meaningful RED at the actual validator's uppercase-key rejection, not an import/collection failure. `_catalogue()` returns a newly loaded payload; the mutation is local and must never write YAML or change cached application data.

3. Apply the supplied exact two-line patch. Verify the exact proposed catalogue postimage SHA and unchanged config.py SHA. Run the new regression to GREEN: it verifies real whole-catalogue acceptance, exact two translations, absent uppercase key, and explicit whole-catalogue rejection when only those two keys are mutated back to the original defect. No mocked validator or relaxed key predicate.
4. Rerun the original Task4 unit command verbatim from the retained writer receipt. Run existing `test_current_ui_catalogue_passes_complete_validator`, `test_ui_catalogue_locale_keys_and_placeholders_match`, both-locale mounted `test_ui_strings_endpoint_returns_valid_en_and_ar_bundles` and `test_malformed_ui_catalogue_fails_closed_without_partial_bundle`. Record actual counts/exits and preserve the4/63 failure. Any remaining passport/rendering failure is a separate actual finding within the original Task4 correction workflow, not cleared by this key approval.
5. Resume original Task5 after prerequisite tests genuinely pass. Future lookup must map displayed/domain U to lowercase machine key while keeping the visible U marker, unknown/unavailable semantics, original numerical states0–3, `known`, K/U/D*, unknown penalty, API equality and both ClassD simulation warnings. No display of lowercase u, zero substitution or invented confirmation. Strengthen the existing approved unit/browser legend cases in both locales and inspect expanded legend/keyboard/axe/parity as already required. This packet does not claim that consumer or its UI tests already exist or pass.
6. After Task5 uses the capability keys, run the **entire** catalogue/static/UI/ES-module suites and original AM4 functional quality diagnostics. In particular the existing unused-key scanner must pass on the completed source; do not delete unused-key detection to accommodate the intermediate not-yet-written consumer. All unknown-state and synthetic-boundary assertions remain. Direct executive shell, typed passports and legend must be verified through the original real browser sequence, not this planner's pure probe.
7. Preserve the exact AM4v2 pre-generation sequencing: full unmodified diagnostics, only the ten individually matched stale unit outputs and exact retained96-versus112 graph teardown may be pending, external actual16/provisional112 resource checks, independent source/UI inspection, separately reviewed Task6 operation, final128/112 full-functional exit0, fixed encoding/resource/R1 and both clean-root gates. This uppercase-key failure is **not** added to the pending-output allowances; it must be fully fixed before source readiness.

## Generated identities and records

This corrects the already authorized UI catalogue input before final graph/authority/visual binding. It may change deterministic input/projection hashes, which are already allocated through the parent operation; it creates no additional allocation, schema version, snapshot or graph topology. The future existing Task5 module is already a visual-hashed input. Bind final corrected YAML/consumer bytes normally; graph semantics remain925/1045 and canonical128 matrix, producer/fonts/tolerances and600KiB/16MiB budgets remain. No generator is run as part of this addendum.

Additive ADR sentence: “AM4's uppercase internal unknown-capability key conflicted with the unchanged lowercase-only catalogue schema. The reviewed correction renames only the EN/AR key to executive.capability.state.u; visible U, both exact meanings, domain unknown behavior and the15-pair contract remain unchanged. A real-validator regression accepts the corrected catalogue and rejects the original uppercase-key mutation. Original AM4 packet bytes and failure history remain preserved.”

## Sanad and Muhasabah

Direct planner evidence: unchanged authority-rule comparison, schema/source reads, original full error cause, exact two-key byte/postimage calculation, all15 key grammar checks, isolated full-validator RED/acceptance, Task5 consumer absence,85 paused path hashes and original45+53 manifest verification. Writer execution evidence is the actual4failed/63passed log and checkpoint, explicitly attributed. The separate reviewer's pure probe is supporting evidence, not approval.

Assumptions: the writer remains paused until root acceptance and its bound preimages still hold. Risks: a later consumer could incorrectly lowercase visible U, omit warnings or treat unknown as0; prescribed real UI/API/unknown tests must detect those failures. Unverified: patch application, new regression execution, Task4 success after removing the schema blocker, Task5 implementation, browser UI, generation, final gates/CI and exact candidate. This plan does not validate unfinished typed-passport work.

Muhasabah PASS for this narrow authored correction. The planner's original copy error is explicit; no evidence is invented, old records rewritten, checker weakened or approval claimed. All current actions are offline reads, pure in-memory diagnostics and new external packet writes. Source/index/graph/services/network/browser were not changed; another reviewer decides approval. No active owned process remains.
