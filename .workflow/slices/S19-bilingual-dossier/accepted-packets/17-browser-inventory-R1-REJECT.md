# S19 browser-inventory admission R1

**REJECT.** One required coverage finding, BI-01. Do not apply the proposed literal inventory update yet. The six submitted test bodies are otherwise substantive; this finding concerns a missing parent-required browser case, not an invented test framework or product verdict.

Exact admission packet: `s19/product-implementation-r1/S19-BROWSER-INVENTORY-ADDITION.json`, SHA256 `cbc2aea055efb580d40b6aeea220ff00daea444bba0e35920e7cb700dbc4bbca`. Independent evidence: `EVIDENCE.json`, SHA256 `03c09ba49757b1b11ca7cb103558eade975e9ff6d67c5df57a5f395ae68767a1`.

Reviewer `/root/s19_source_reviewer` is separate from the writer. Reused the governing preparation, refreshed the parent Task4 and successor/trade admission boundaries, then read the complete frozen bodies/helper, inventory preimage/patch, source snapshot bindings and actual collection/result records. Adopted browser-test integrity and bilingual rendering reviewer roles. Reread and applied strict-reviewer, verification-before-completion, Sanad, Al-Muhasibi and Muhasabah. Same-model Codex review is not Claude or cross-model approval.

## BI-01 — required rendered empty/unavailable/numeric-zero cases are absent

**Requirement:** Parent S19 Task4 explicitly requires browser unavailable/empty/contradiction/NOT_CALCULABLE cases. Task3 also requires truthful empty producers/passports. Tests must demonstrate the real renderer's behavior, rather than merely visiting a case that happens to contain an unavailable value.

**Evidence:** The frozen `test_dossier_failure_states.py` contains only `test_dossier_missing_case_and_invalid_mode_never_return_success`, which exercises endpoint404 and invalid-mode422. The complete frozen dossier browser tests/helper contain no assertion for empty producer/passport rendering or a scoped unavailable/NOT_CALCULABLE value distinguished from zero. Bounds, axe, download, identity and basic PDF structure checks do not establish those semantics.

**Preserved existing coverage:** `test_open_dossier_popup_matches_case_and_mode` already checks the actual steel coating contradiction, other cases' no-public-contradiction copy, no-synthetic-contradiction copy and public/synthetic disclosure distinction. That body is byte-for-byte preserved. No additional contradiction test is needed for this finding.

**Exact correction:** Add the missing bounded, parameterized browser rendering case in the already permitted `browser_tests/test_dossier_failure_states.py`. Use actual `build_dossier` and `render_dossier_html` with explicit isolated test fixtures and the existing browser facilities; do not use handcrafted replacement report markup or change the harness. Cover EN/AR empty producer and public-passport states, source-equal public UNAVAILABLE, and actual PP simulated minimum support0 versus unsupported NPV NOT_CALCULABLE. Assert the relevant visible, governed labels/values in their corresponding sections and absence of invented rows/zero substitutions. Preserve existing contradiction and404/422 checks. Distinguish controlled fixture facts from governed case facts.

Run the actual corrected cases, retain meaningful failure sensitivity and passing results, freeze the new body/source hashes and actual parameter IDs, and issue an additive corrected admission packet plus the revised finite literal hunk. Preserve this packet/rejection. The final named-function/node totals must follow the real corrected bodies, not a guessed count. No product or test-harness path expansion is necessary.

## What was independently verified

- All5 frozen source-file hashes match the packet and their stated proof snapshots: four new files at `source-prototype-r3`, final journey at `source-prototype-r4`. All6 body hashes and decorated-source hashes match. Body hashes use AST source segments without trailing newline; decorated hashes use the complete decorated text.
- Accepted-base inventory has exactly23 files/76 unique test names. Submitted snapshot has27/82 with precisely the4 permitted files and6 named additions, no duplicate names and no changed inherited test bodies. The inventory preimage matches the delivered base at `2dc6695c…`. The proposed patch adds only those literals and76→82 in the function name; existing equality/discovery/assertions remain.
- Collection contains exactly176 distinct node IDs, equal to the packet's full lists:44 journey,24 bounds,4 toolbar,2 endpoint failure,66 trade source equality and36 trade keyboard/width cases. The existing harness consumes the actual viewport parameter; the width matrices are not decorative parameters.
- New assertions exercise full exported `public_decision` equality, visible public headline and locale/context return; initial/leftmost text and element bounds with both exact policy labels; real print/download/return keyboard actions; endpoint failure status; complete public-source table values/units; and native Enter/Space/Tab behavior with bounds/axe. These are not pass-only bodies or expectations obtained from the rendered result itself.
- The retained inventory RED is exactly2 failures/22 passes at the file/name equality assertions. The r3-backed browser record is16 failures/308 passes, including132 new-file nodes; the final journey record is16 failures/44 passes with the actual final journey name and assertions. In both, the16 failures are the separate inherited keyboard tuple issue. These records do not establish a full source gate or final PDF acceptance.

After corrected admission approval and coordinator acceptance, the unchanged successor process still requires literal-update GREEN and disposable-copy old-member-removal/unapproved-addition negatives. This rejection neither removes those controls nor permits expectations derived from runtime discovery.

## Sanad / Muhasabah

Direct: exact hashes, AST/body/set comparisons,176 ID equality, complete frozen-source inspection and retained log/summary reads. Attributed: writer's browser executions and the separately sealed original AR/trade RED proof. No fresh browser, service or product test ran here; unchanged expensive proof was not replayed. Assumption: later source review will bind its own paused exact subject. Mutable product, complete print corpus, generation, candidate/CI/hosted/head/delivery gates remain unverified and unapproved.

Risk: admitting the current literals as the complete required test addition would leave truthful empty/missingness presentation untested in-browser. The correction is confined to existing scope and preserves all prior assertions. Only this report and minimal external evidence were written; no source/index/service/GitHub/generated writes or subagents.

**Muhasabah: PASS for the evidence-backed REJECT.** One actionable requirement gap is explicit; no partial result is promoted to product approval.
