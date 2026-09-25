# Finite postcheck literal correction

**APPROVE** replacing only these three mistaken expected path strings in the disposable evidence postcheck:

| Mistaken literal | Already-reviewed literal |
| --- | --- |
| `docs/core/03_TECHNICAL_ARCHITECTURE_AND_GENUI.md` | `docs/core/03_SYSTEM_ARCHITECTURE.md` |
| `docs/core/04_DATA_ARCHITECTURE_EVIDENCE_API.md` | `docs/core/04_CANONICAL_DATA_MODEL.md` |
| `docs/core/09_TESTING_ACCEPTANCE_AND_CI.md` | `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` |

Preserve `s19/ops-generation-r1/EXECUTION-POSTCHECK-ATTEMPT1.json`, SHA256 `0c6d62288d4322857a6b0162e3a16b994929dd44e9bba5163e88b9cab60704e6`, as the failed assertion attempt. It is not a passing postcheck or a generator failure.

I directly compared the preserved preimage and actual generated authority manifests: both contain the same20 paths, and the five changed rows are exactly UI strings plus Core02/03/04/09 with the correct names above. That set independently equals the authority subset of the previously reviewed INPUT-COMPARISON.json (`cf0a25a2cb2ba78cc8403c7689f8b52d295f3457e05496ca1a7f8e31fd43b2c4`). This fixes an erroneous oracle literal using the pre-approved input boundary; it does not replace an expectation with whatever the current output happens to contain.

All original set/row/hash/table/source/index assertions remain required. After coordinator instruction, the writer may finish the existing postchecks and actual unpatched22 dossierJSON+22 analysisJSON+44 HTML comparison. No source change, generator rerun, forced identity, restoration or assertion weakening is approved. The final generated-result review remains pending its sealed complete receipt; neither this correction nor the separate capture proposal supplies that approval.

Sanad: direct failed-record hash, manifest row comparison and bound input-set equality; prior preparation and evidence-integrity persona reused with strict-reviewer/Sanad/Muhasabah. Assumption: the corrected disposable check changes only the three named strings. Unverified: remaining row/table checks, actual88-response comparison and final operation receipt. Only this external concurrence was written. **Muhasabah: PASS** for the finite correction, preserving the original failure and remaining obligations.
