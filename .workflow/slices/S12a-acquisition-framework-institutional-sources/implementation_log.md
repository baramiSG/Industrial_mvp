# S12a implementation log

## 2026-09-11 — owner authorization and T0

Recorded the owner's direct authorization verbatim in a local-only dated ruling; consolidated plan-5 from original plan-4 and approved amendments; verified the six canonical command values byte-for-byte; re-pinned checkpoint; created the specified branch at the exact base. All these acts precede implementation code.

T0 PASS; see test_evidence.md for exact commands/results. 1002 baseline tests passed (one existing warning); integrity and reconstruction PASS; 17 frozen pin tests passed. Canonical [5] initially failed on 23 existing ignored bytecode files, preserved intact outside the repo; rerun passes unchanged. No raw evidence or tracked fixture was changed.

At T0: manifest runs 0; live operator windows 0; commits 0. Nothing staged; .env never read. Later step records below carry the cumulative state.

## Execution ledger

- T0: complete.
- T1: complete — full fresh coordinator gate 1052 passed (one existing warning); integrity, reconstruction, smoke and frozen oracles PASS; independent review findings resolved and re-review APPROVE. TDD and corrections recorded below and in local t1-report.md.
- T2: complete — three independent findings fixed test-first; re-review APPROVE; fresh coordinator 1117 passed with only approved W2 and existing warning, 137 focused/frozen passed; reconstruction/integrity/smoke/frozen oracles PASS.
- T3: complete — independent review APPROVE; coordinator 1348 passed with exactly W1/W2, config/sentinel/canonical and S11 reconstruction proofs PASS. Config hash mismatch intentionally awaits T11; source facts all UNAVAILABLE.
- T4: complete — snapshot/protocol omissions fixed test-first; independent privacy review and connector re-review APPROVE. Fresh coordinator 1699 passed with exactly W1/W2, 380 focused/frozen passed; reconstruction/smoke/canonical and frozen checks pass. Integrity remains config-only drift until T11.
- T5: complete — independent review APPROVE; fresh coordinator 1747 passed with exactly W1/W2, 85 focused/frozen passed; canonical/reconstruction/smoke/frozen checks pass. Request-count and custom build-root issues remain deferred.
- T6: complete — independent review APPROVE; coordinator 1747 passed with exactly eight W1/W2/W4 failures, 31 focused/frozen passed, canonical/reconstruction/smoke/frozen checks pass.
- T7: complete — independent review APPROVE; five honest zero-request ENDPOINT_UNVERIFIED attempts; coordinator 1753 passed with only W2/W4, 332 focused/frozen passed. Live window closed.
- T8: complete — independent review APPROVE; coordinator 1754 passed with only W2, exact Core/frozen/S11 oracles pass; W4 closed. No source/network work.
- T9: complete — independent review APPROVE, W2 closed; coordinator full 1755 passed, one existing warning. ADR-016 and source/split/control records verified; manifest count remains 0.
- T10: complete — prescribed filtered regression 1740 passed / 1 deselected / 1 existing warning; every applicable pre-generation canonical gate passed. Full T9 pytest 1755 passed without exclusions. Scope/prospective-secret/frozen/index checks pass.
- T11: complete — exactly one generation, exit 0 at 2026-09-11 22:31:25 UTC; five authority rows mirrored; immediate canonical [12] PASS. Ten new raw attempt/coverage rows, all 63 old evidence rows unchanged; no generation remains authorized.
- T12: complete — all 26 executable canonical gates PASS; [22] superseded. Full pytest 1755 passed, make ci PASS including 118 functional + 4 visual nodes, integrity/scenarios/reconstruction/smoke/frozen proofs PASS. No source network. Awaiting session implementation review, uncommitted.

Skill adaptation: use TDD, scoped subagent implementation/review, provenance and self-audit within the owner's approved plan. Do not create a competing workflow, a separate .superpowers ledger/worktree, commit between tasks, or auto-merge as generic skill defaults suggest. This slice record is the recovery ledger and ordinary evidence log.

## 2026-09-11 — authorized browser prerequisite download

The initial browser preflight found the pinned Chromium executable absent. In response to the session's specific browser-download question, the owner authorized: "yse download whatever is needed". This permits the existing test-runtime download outside the T7 data-source operator window; it does not authorize dependency upgrades, new project dependencies or baseline changes.

Playwright's `install --with-deps chromium` exited 1 because sudo requires interactive authentication, before browser installation. `install chromium` then exited 0, downloading Chromium and its headless shell (revision 1234) plus FFmpeg (revision 1011) to the user browser cache. The existing host libraries resolved; no sudo authentication or privileged package change occurred. Repository browser preflight and a real offline browser launch both passed. No project dependency/lockfile or baseline was changed by this operation.

## Consolidation audit

Independent read-only consolidation audit (`s12a_consolidation_check`, gpt-5.6-sol/high) returned advisory PASS: plan-4/plan-5/ruling/checkpoint hashes and six exact command strings verified; all nine amendments and owner substitutions consistent under the artifact's precedence. This is not implementation approval.

Execution clarifications, with no scope or immutable-plan change:

- Inherited `risks[6]` mentions restoring a manifest and restarting. The direct owner one-run limit and current `rollback_recovery[2]` control: preserve evidence and stop for owner direction after a premature or failed generation, never restore/regenerate automatically.
- AM-8's `acquisition/__main__.py` freeze remains mandatory even though inherited verification[6] is not an exhaustive frozen-file list. T5/T12 must additionally run a direct byte-identity Git check for this file and all other declared frozen paths.
- The exact approved MIME table is unchanged. Real XLSX binary envelopes fail the decode/control guard; an unknown MIME declaration alone does not add an unapproved refusal rule to the specified opaque-text branch.

## T1 review and correction ledger

- Parent review: classification now invokes parsers during acquisition, exposing expected malformed Comtrade-shape exceptions before storage. Implementer reproduced `data: null` / malformed period failures and added classification-only handling to preserve UNPARSED raw bodies; existing row normalization/reporter semantics remain deferred and unchanged.
- T1-R1: parent found a doubled backslash in the extracted ZATCA HTML regex. A read-only direct parse probe returned `[]` and failed its assertion (exit 1); implementer added an HTML classification/normalization RED, corrected the regex to the original supported attribute pattern, then observed GREEN. Existing parser behavior is restored, not expanded.
- Independent registry/coverage review (`s12a_t1_registry_review`, gpt-5.6-sol/high): no findings, including recheck of StageSpec URL-token compatibility. Read-only, no test execution.
- T1-R2: independent snapshot/loader review (`s12a_t1_snapshot_review`, gpt-5.6-sol/high) REJECT: injected KindSpec.root can bypass the original supplied-root-only guard, target public/synthetic paths or escape the data root, including loader reads. Required fix is normalized registry paths and resolved final-directory containment/prohibited-root checks, with temp-only write/load tests. No real frozen path may be used as a write target during reproduction.
- Coordinator fresh checks after T1-R1 but before T1-R2: 1042 tests passed (one existing warning), 21 golden/frozen tests, integrity, reconstruction and smoke PASS. These results do not waive T1-R2 or approve T1. Rerun gates after the fix and re-review before T2.
- T1-R2 resolved: 10-case temp-only write/load matrix exposed the defect, then passed with the shared private final-directory guard. Parent final full suite 1052 passed in 13.75s; integrity, reconstruction, smoke, canonical [4]/[5]/[6]/[10], additional frozen-file check and diff whitespace check all exit 0. Independent snapshot re-review APPROVE with no findings. T1 accepted for T2 only; no delivery/commit approval is implied.

## T2 review and correction ledger

- Coordinator initial gate: 1099 passed, one approved W2 failure (`KeyError: directory` in the old three-kind integrity-test lookup), one existing warning; focused plus frozen tests 119 passed. Reconstruction, integrity, smoke and canonical [4]/[5]/[6]/[10] passed. These are interim results, not full-suite GREEN.
- Independent bounded review (`s12a_t2_review`, gpt-5.6-sol/high): REJECT with three code-confirmed findings. T2-R1: real-looking institutional source IDs in Class-D doubles bypass the current default snapshot double guard because it checks only TEST-FIXTURE or an access marker absent from generated refs; inspect passport access classification and test default validate/write/load refusal with explicit-allow controls. T2-R2: AGGREGATE planning with no years returns zero units; reject missing periods at planning. T2-R3: approved five-type `Row` union and protocol/base normalize typing are missing. All three require focused tests before changes. T3 remains held until fixes, fresh gates and re-review.
- All three resolved: 18 targeted RED cases became GREEN; default test-double validate/write/load refusal covers five real-looking IDs without changing S11 ref bytes, empty aggregate years fail closed, and the exact Row union is used in the protocol/base annotations. Independent re-review APPROVE with no remaining findings. Fresh coordinator full run: 1117 passed, only approved W2 and existing warning; 137 focused/frozen passed; reconstruction, integrity, smoke and canonical [4]/[5]/[6]/[10] PASS. T2 accepted for T3 only; final session review still required before any commit.

## T3 review and acceptance

Independent review (`s12a_t3_review`, gpt-5.6-sol/high): APPROVE, no in-scope findings. Verified exact nine sources/version, all seventeen sentinel facts, non-fact pins, S11 block byte identity, shared predicates, strict institutional keys, recursive forbidden-key traversal and credential detector semantics. Coordinator reran the final candidate after the test-only baseline restriction: 1348 passed, exactly six W1 and one W2 failures, one existing warning; all 16 detector meta-tests passed. Canonical [4]/[5]/[6]/[10]/[20]/[21]/[24], S11 reconstruction and golden/smoke proof pass. Standalone integrity now reports only the expected acquisition-config hash mismatch; the single generator run remains reserved for T11. T3 accepted for T4 only.

## Additional accounting finding — owner choice pending

A bounded read-only audit (`s12a_request_accounting_audit`, gpt-5.6-sol/high), confirmed against HEAD and current control flow, identified preexisting S11 accounting issues: zero-page coverage drops the passed request count/observed_stop, and RunReport sums cumulative counters only for successful units. The new T4 privacy-refusal coverage obligations remain in approved scope and must preserve charged requests/hash-only metadata while leaving S11 derivation unchanged. A separate non-blocking owner question asks whether to correct the future RunReport total to the existing shared-budget count; no such reporting change is authorized or implemented yet. Generic coverage semantics and historical S11 records are not to be rewritten.

## T4 doubles-first interpretation

T4's exact step requires parsing kind JSON doubles in tests and also requires production `parse_rows` to return `[]` until real source shapes are known. The coordinator directed the implementer to keep fixture-specific parsing in test-only subclasses/parser overrides, exercising the actual connector acquisition, normalization and validation paths. Production code must not recognize `TEST-FIXTURE` envelopes as if they were observed institutional formats; both unrecognized live-like and tagged-test envelopes remain unknown to its default parser. This preserves DD-15's offline-parser workflow and the no-free-facts boundary. No source format has been observed or authorized for invention.

## T4 review observations

- Coordinator fresh full gate: 1688 passed, exactly six W1 and one W2 failures, existing warning only. Focused institutional/connector/frozen/golden group: 369 passed. Reconstruction, smoke, canonical [4]/[5]/[6]/[10]/[20]/[24]/[25] pass. Integrity differs only for the acquisition config awaiting T11. All 18 mandatory additional privacy test names are present, independently checked against the parsed immutable plan.
- Independent privacy review (`s12a_t6_boundary_map`, gpt-5.6-sol/high, separate bounded follow-up): APPROVE, no findings. Checked literal MIME/envelope/label/BOM/control policy, refusal seam and non-retention, coverage precedence, credential sentinel handling, and test-only fixture parsing. Read-only; coordinator executions provide fresh test evidence.
- Connector/integration review remains pending; no T5 implementation or T4 final acceptance yet.
- Parent T4-R1 REJECT: the immutable plan's new-connector interface explicitly requires `snapshot` delegation to the generic builder. All five new classes currently inherit BaseConnector.snapshot, which raises NotImplementedError. The implementation report and passing acquisition/pipeline tests did not exercise this interface. Required correction: per-source test-first direct snapshot calls over fresh temp acquisition, shared generic delegation following the existing S11 helper convention, and raw-derived date/provenance preserved rather than trusting the method's observations/as-of arguments. T5 remains held; independent connector review and fresh post-fix gates are required.
- Parent T4-R2: the approved base interface requires nullable `SourceConnector.parse_rows`, but runtime type-hint inspection shows the protocol declares only source_id/snapshot_kinds. BaseConnector already carries the correct nullable callable. Complete the protocol declaration test-first, retaining None for BACI and other parser-less connectors.
- Independent connector/integration review (`s12a_t5_boundary_map`, gpt-5.6-sol/high, separate bounded follow-up): REJECT exactly T4-R1/T4-R2; no additional findings. Source registration, credential/access order, privacy seam, real validator-before-PASS, test-only parsers and first-run byte preservation otherwise conform. The existing type-contract test is the preferred extension for R2. Re-review is required after both corrections; neither the privacy-only APPROVE nor the earlier 1688 passing tests closes these findings.
- Both findings resolved test-first: 11 focused RED cases became GREEN; one coherent optional-parser/BACI test stayed in the institutional module without duplicating existing Row-return assertions. Shared snapshot delegation preserves raw-derived date and kind config pins and refuses unparsed evidence despite supplied observations. Connector re-review APPROVE, no remaining findings; privacy behavior unchanged. Fresh coordinator full suite 1699 passed, only the exact seven W1/W2 failures and existing warning; 380 focused/frozen passed. Reconstruction 1 snapshot/4 artifacts, smoke, canonical [4]/[5]/[6]/[10]/[20]/[24]/[25], extra frozen-file/index/whitespace and branch/base checks pass. T4 accepted for T5 only, not final delivery approval. No manifest or source acquisition run occurred.

## T5 acceptance

Independent review (`s12a_t5_boundary_map`, gpt-5.6-sol/high, T5 follow-up) APPROVE, no findings. Verified parser/dispatch and pre-write permission ordering, thin stage-aware wrappers, generic kind builds, Make live/not-CI guards, fresh-interpreter and filesystem/tamper proofs, preserved S11 argument errors and frozen entry point. Coordinator fresh full suite: 1747 passed, exactly the same seven W1/W2 failures, one existing warning; 85 focused/frozen passed. Canonical [4]/[5]/[6]/[7]/[8]/[10]/[11]/[20]/[24]/[25], reconstruction, extra frozen/index/whitespace checks pass. Integrity remains the authorized config-only pre-generation mismatch. Eight existing reconstruction subprocess environment mappings now inherit external cache/PATH without changing assertions. No counter or custom-root semantic repair was absorbed. T5 accepted for T6 only; T7 network remains closed.

## T6 acceptance and T7 opening — 2026-09-11 UTC

Independent review (`s12a_t5_boundary_map`, gpt-5.6-sol/high, T6 follow-up) APPROVE, no findings. Both exact manifest prefixes, stage derivation, six real loader wrappers and scoped literal Core tests conform. Coordinator observed 1747 passes, exactly six W1 plus W2/W4 failures, one existing warning; 31 focused/frozen pass. Canonical [4]/[5]/[6]/[10]/[20]/[24]/[25], reconstruction and frozen/index/whitespace checks pass. A mistyped smoke filename exited 2; corrected existing `scripts/demo_smoke.py` exited 0. Integrity retains only the authorized config hash mismatch. No source raw records, Core edits or manifest run yet. T6 accepted.

T7 is now the sole active data-source network window. Consult only official public documentation/terms, with no .env reads, authentication bypass or restricted-body download. Consultations do not imply observed dataset endpoints, units, content types, pagination or credential policy. Record only verified facts and actual consultation date; leave other fields UNAVAILABLE. Per-source commands, budgets and rationale will be recorded below before execution. The optional RunReport accounting correction remains unapproved and deferred; report its emitted fields honestly without asserting equivalence to actual requests where the known preexisting discrepancy applies.

### T7 GASTAT consultation and pre-run parameters — 2026-09-11 UTC

Official documentation: https://www.stats.gov.sa/en/w/methodology-and-quality-report-for-the-annual-industrial-production-index-ipi-statistics-2025 . Official usage policy: https://stats.gov.sa/en/use-policy . Web lookup opens returned timeout/502; bounded direct urllib HEAD and GET (normal TLS, no credentials, memory only) returned HTTP 200 for both. Actual GET media type `text/html;charset=UTF-8`; methodology 238348 bytes, SHA-256 `cc1d80c933e9cb9aeca90af6d583c4cfeacc6beec78889e83d8e904140143c17`; policy 205644 bytes, SHA-256 `d4f5ca30c24b14262465a275296fb4b8591e917c8cb78d1c36a4d9ee439c49db`. These are documentation consultation observations, not raw acquired datasets, and the bodies were not written. An alternate official methodology 4.1 HEAD also returned 200; no new data facts were inferred from that probe.

The policy permits attributed reuse of website data, with separate indicator policies able to override it: record website access as `public_open`, observed documentation and terms references, and the exact terms URL as TERMS endpoint. This does not prove any specific API is credential-free; credential setting stays UNAVAILABLE. The methodology identifies calendar year 2025 and links https://database.stats.gov.sa/home/landing ; that landing page returned HTTP 200, 2858 bytes, `text/html`, only the title GASTAT in static text, and no verified dataset endpoint/unit/pagination contract. No script reverse engineering, hidden endpoint guessing or dataset download occurred. Aggregate endpoint, unit identifiers, data content types, nomenclature/token mappings, pagination and rate policy remain UNAVAILABLE. Source observation state is OBSERVED (limited documentation facts), not PRE_OBSERVATION.

Pre-run command (recorded before execution):

```bash
IOR_ACQUISITION_LIVE=1 make acquire-aggregates SOURCE=gastat YEARS=2025 MAX_REQUESTS=2
```

Execution environment: existing virtualenv PATH; `PYTHONPATH=src`; external bytecode prefix; `UV_OFFLINE=1` for the locked local toolchain only (does not alter the acquisition network guard); no CI; .env never read. `YEARS=2025` is the observed methodology reference year, not inferred from frozen cases. Units: UNAVAILABLE, so the approved planner emits one explicit unverified-unit contract, not an invented dataset id. Budget 2 covers the planner's single unit plus documented terms-capture allowance; endpoint refusal is expected before either request. A 2025 index is not relabelled physical production/retained-flow input. Unknown endpoint is an honest acquisition limit, not proof GASTAT lacks the data.

GASTAT result: Make exit 2 wrapping application exit 3; zero requests/pages, no response body, no snapshot. The local locked toolchain rebuilt only the editable project package; no lockfile or dependency declaration changed. An earlier read-only planning diagnostic called nonexistent `QueryContract.to_json` and exited 1 after config validation; this did not write evidence. Corrected existing `plan_requests` diagnostic exited 0 with minimum 2; the actual Make command independently enforces that minimum. RunReport output (JSON values preserved):

```json
{"artifacts":[],"coverage":[{"completeness_basis":"UNAVAILABLE","missing_pages":[],"observed_stop":null,"pages_expected":0,"pages_fetched":0,"query_hash":"e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d","requests_made":0,"run_id":"20260911T215546Z","source_id":"gastat","stage":"AGGREGATE","status":"INCOMPLETE","stop_reason":"ENDPOINT_UNVERIFIED","unit":{"parameters":{"unit":"UNAVAILABLE"},"period":"2025","stage":"AGGREGATE"},"unit_key":["[[\"unit\",\"UNAVAILABLE\"]]","2025"]}],"exit_code":3,"flows":[],"max_requests":2,"requests_made":0,"run_id":"20260911T215546Z","source_id":"gastat","stage":"AGGREGATE","unavailable":["ENDPOINT_UNVERIFIED"],"years":[2025]}
```

Write-once record: `data/raw/gastat/e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d/20260911T215546Z/attempt.json` plus sibling coverage. Observed response null, credential_env_var null, credential_present false. Endpoint/unit refusal precedes terms capture; the separate documentation HTTP observations above are not misrepresented as acquisition responses. No optional second run justified without an observed dataset contract.

### T7 Ministry and MODON consultation and pre-run parameters — 2026-09-11 UTC

Bounded official-site consultation by `s12a_t5_boundary_map` (21:52:56–21:57:52Z), followed by coordinator normal-TLS HEAD checks, found no accessible official directory documentation. MIM homepage https://mim.gov.sa/en/ and controlled data-sharing service https://mim.gov.sa/en/services/31347/ : reviewer browser opens timed out and direct HEAD timed out; coordinator HEAD raised `URLError: [Errno 101] Network is unreachable`. No HTTP response or body was obtained. Cached official-domain search extracts for the service concern controlled data sharing, not a public directory; no credential/access setting is inferred from them.

MODON homepage https://modon.gov.sa/en/ : reviewer and coordinator direct HEAD failed `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`; no HTTP response/body obtained and TLS verification was not disabled. Historical annual-report/service-guide search extracts do not establish a current public directory contract. Relevant discovered references included https://www.modon.gov.sa/ar/MediaCenter/AnnualReports/Modon%20Annual%20Report%202016%20-%20Lower%20V.pdf and https://modon.gov.sa/ar/Systems/Documents/Modon_ServicesBooklet.pdf ; these were not acquired as evidence or promoted to current technical facts. Recruitment-site policies and authenticated investor services were explicitly excluded.

Both mappings therefore remain PRE_OBSERVATION: all seventeen source facts UNAVAILABLE, with actual consultation date recorded. This means the current bounded consultation could not verify them, not that no public data exists. Pre-run commands (recorded before either execution):

```bash
IOR_ACQUISITION_LIVE=1 make acquire-directory SOURCE=ministry_of_industry MAX_REQUESTS=1
IOR_ACQUISITION_LIVE=1 make acquire-directory SOURCE=modon MAX_REQUESTS=1
```

Each is period-free (no YEARS), units UNAVAILABLE producing one explicit unverified-unit contract. Budget 1 is the minimum single-unit bound with no observed terms-capture URL; endpoint refusal should consume zero requests. Existing virtualenv PATH, `PYTHONPATH=src`, external bytecode prefix and `UV_OFFLINE=1` apply; no CI and no .env read. Parameters come from the observed absence of a usable contract, not frozen examples. No guessed directory ID or access classification is introduced.

### T7 ministry_of_industry result

Make exit 2 wrapping application exit 3; zero requests/pages, ENDPOINT_UNVERIFIED, INCOMPLETE, observed_stop null. Complete emitted RunReport values:

```json
{"artifacts":[],"coverage":[{"completeness_basis":"UNAVAILABLE","missing_pages":[],"observed_stop":null,"pages_expected":0,"pages_fetched":0,"query_hash":"b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f","requests_made":0,"run_id":"20260911T215956Z","source_id":"ministry_of_industry","stage":"DIRECTORY","status":"INCOMPLETE","stop_reason":"ENDPOINT_UNVERIFIED","unit":{"parameters":{"unit":"UNAVAILABLE"},"period":null,"stage":"DIRECTORY"},"unit_key":["[[\"unit\",\"UNAVAILABLE\"]]"]}],"exit_code":3,"flows":[],"max_requests":1,"requests_made":0,"run_id":"20260911T215956Z","source_id":"ministry_of_industry","stage":"DIRECTORY","unavailable":["ENDPOINT_UNVERIFIED"],"years":[]}
```

Raw record: `data/raw/ministry_of_industry/b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f/20260911T215956Z/attempt.json` plus sibling coverage. No acquisition HTTP response/body; documentation connectivity errors remain consultation observations above, not invented attempt responses.

### T7 modon result

Make exit 2 wrapping application exit 3; zero requests/pages, ENDPOINT_UNVERIFIED, INCOMPLETE, observed_stop null. Complete emitted RunReport values:

```json
{"artifacts":[],"coverage":[{"completeness_basis":"UNAVAILABLE","missing_pages":[],"observed_stop":null,"pages_expected":0,"pages_fetched":0,"query_hash":"94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135","requests_made":0,"run_id":"20260911T215956Z","source_id":"modon","stage":"DIRECTORY","status":"INCOMPLETE","stop_reason":"ENDPOINT_UNVERIFIED","unit":{"parameters":{"unit":"UNAVAILABLE"},"period":null,"stage":"DIRECTORY"},"unit_key":["[[\"unit\",\"UNAVAILABLE\"]]"]}],"exit_code":3,"flows":[],"max_requests":1,"requests_made":0,"run_id":"20260911T215956Z","source_id":"modon","stage":"DIRECTORY","unavailable":["ENDPOINT_UNVERIFIED"],"years":[]}
```

Raw record: `data/raw/modon/94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135/20260911T215956Z/attempt.json` plus sibling coverage. No acquisition HTTP response/body; documentation connectivity errors remain consultation observations above, not invented attempt responses.

### T7 SASO and SABER consultation and pre-run parameters — 2026-09-11 UTC

`s12a_t6_boundary_map` consultation finished 21:57:41Z; coordinator independently opened the official documentation/policy pages below and checked the API-documentation link. These are public read-only consultations, not raw dataset acquisitions.

SASO: https://www.saso.gov.sa/en/mediacenter/Pages/open_data.aspx explicitly lists Standards Data APIs and source-specific attribution/sharing conditions. Record that exact documentation/terms reference and TERMS endpoint. Generic library formats do not establish this API's MIME. The embedded https://api.saso.gov.sa/index.html?rs%3Aembed=true&urls.primaryName=SASO+Open+Data+API is a documentation UI, not a verified data endpoint; browser open failed and both reviewer direct checks and coordinator HEAD failed connection reset (coordinator `ConnectionResetError [Errno 104]`). No body retained. An official linked Saudi Standard 2024 catalogue page also failed browser opening; no unit/schema inferred from its title. Broad https://www.saso.gov.sa/en/privacy_policy/Pages/default.aspx limits portal reuse, whereas the source-specific open-data page describes open reuse. The consultant proposed public_open for that category; the coordinator leaves access_classification UNAVAILABLE until a concrete metadata endpoint's applicable scope is verified, rather than extending the open-data statement to paid standards or resolving the scope tension by assumption. The separate https://www.saso.gov.sa/en/acceptable_use_policy/Pages/default.aspx prohibits disproportionate infrastructure load; record this qualitative policy, not a numeric source rate. Existing client-side 2-second floor/3 attempts/60-second timeout are unchanged.

SABER: https://saber.sa/home/aboutsaber documents product registration and certificates. https://saber.sa/Home/Terms requires account creation and user credentials for the registration platform; `public_registered` is the explicit project-enum mapping of that observed platform access, not proof a public enumeration API exists. The same terms prohibit excessive infrastructure load, recorded qualitatively with URL. References/TERMS endpoint recorded. An interactive username/password is not a documented bearer/API credential contract: credential_env_var stays UNAVAILABLE, never an invented env-var name. The consultant's public HS-code and accepted-assessment-body pages were excluded from registry units because they describe requirements/issuers, not the intended product/certificate registrations. No authenticated page, paid standard, personal data record or data payload was acquired.

For both, REGISTRY endpoint, units, pagination, data MIME, nomenclature/tokens and API credential requirements remain UNAVAILABLE. Their state is OBSERVED due to limited documentation facts. Pre-run commands (recorded before either execution):

```bash
IOR_ACQUISITION_LIVE=1 make acquire-registry SOURCE=saso_catalogue MAX_REQUESTS=2
IOR_ACQUISITION_LIVE=1 make acquire-registry SOURCE=saber_registry MAX_REQUESTS=2
```

No YEARS (period-free). Each unit list is UNAVAILABLE, so one unverified-unit contract; budget 2 covers one unit plus one documented terms allowance. Endpoint/unit refusal precedes access/terms and is expected to consume zero requests. Same virtualenv/cache/PYTHONPATH/UV_OFFLINE environment, no CI, no .env read. No numeric rate, endpoint or unit is guessed merely to obtain a nonempty snapshot.

### T7 saso_catalogue result

Make exit 2 wrapping application exit 3; zero requests/pages, ENDPOINT_UNVERIFIED, INCOMPLETE, observed_stop null. Complete emitted RunReport values:

```json
{"artifacts":[],"coverage":[{"completeness_basis":"UNAVAILABLE","missing_pages":[],"observed_stop":null,"pages_expected":0,"pages_fetched":0,"query_hash":"9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49","requests_made":0,"run_id":"20260911T220134Z","source_id":"saso_catalogue","stage":"REGISTRY","status":"INCOMPLETE","stop_reason":"ENDPOINT_UNVERIFIED","unit":{"parameters":{"unit":"UNAVAILABLE"},"period":null,"stage":"REGISTRY"},"unit_key":["[[\"unit\",\"UNAVAILABLE\"]]"]}],"exit_code":3,"flows":[],"max_requests":2,"requests_made":0,"run_id":"20260911T220134Z","source_id":"saso_catalogue","stage":"REGISTRY","unavailable":["ENDPOINT_UNVERIFIED"],"years":[]}
```

Raw record: `data/raw/saso_catalogue/9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49/20260911T220134Z/attempt.json` plus sibling coverage. No acquisition HTTP response/body. No optional second run: no stored page exists from which a source parser could be authored.

### T7 saber_registry result

Make exit 2 wrapping application exit 3; zero requests/pages, ENDPOINT_UNVERIFIED, INCOMPLETE, observed_stop null. Complete emitted RunReport values:

```json
{"artifacts":[],"coverage":[{"completeness_basis":"UNAVAILABLE","missing_pages":[],"observed_stop":null,"pages_expected":0,"pages_fetched":0,"query_hash":"e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3","requests_made":0,"run_id":"20260911T220134Z","source_id":"saber_registry","stage":"REGISTRY","status":"INCOMPLETE","stop_reason":"ENDPOINT_UNVERIFIED","unit":{"parameters":{"unit":"UNAVAILABLE"},"period":null,"stage":"REGISTRY"},"unit_key":["[[\"unit\",\"UNAVAILABLE\"]]"]}],"exit_code":3,"flows":[],"max_requests":2,"requests_made":0,"run_id":"20260911T220134Z","source_id":"saber_registry","stage":"REGISTRY","unavailable":["ENDPOINT_UNVERIFIED"],"years":[]}
```

Raw record: `data/raw/saber_registry/e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3/20260911T220134Z/attempt.json` plus sibling coverage. No acquisition HTTP response/body. No optional second run: no stored page exists from which a source parser could be authored.

### T7 offline build and operator-window closure

After all five runs, `make build-snapshots KIND=all` ran with the same local toolchain environment but **without** IOR_ACQUISITION_LIVE, exit 0. Complete BuildReport values:

```json
{"built":["/home/barami/projects/industrial-opportunity-resolution-mvp/data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json"],"raw_only":["baci_cepii"],"unavailable":[["directory","ministry_of_industry","COVERAGE_INCOMPLETE"],["directory","modon","COVERAGE_INCOMPLETE"],["partners","un_comtrade","NO_UNITS_IN_STORE"],["production","gastat","COVERAGE_INCOMPLETE"],["registry","saber_registry","COVERAGE_INCOMPLETE"],["registry","saso_catalogue","COVERAGE_INCOMPLETE"],["tariff","zatca_tariff","COVERAGE_INCOMPLETE"],["universe","un_comtrade","COVERAGE_INCOMPLETE"],["universe","wits_trade","COVERAGE_INCOMPLETE"]]}
```

`PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest` exited 0: 1 snapshot / 4 artifacts. BuildReport.built names the existing partner snapshot; it does not indicate newly acquired institutional data. All five new source/kind pairs return COVERAGE_INCOMPLETE because their honest attempts contain no complete unit. Each requires a T9 KL row citing its actual query/source and consultation limitation. No institutional snapshot or source-specific parser was invented, and no existing raw record was relabelled.

The live operator window is CLOSED after these commands. T7 review and remaining T8–T12 are offline; no further source requests or downloads are authorized by this window. Manifest runs remain 0. Full fresh regression and independent T7 review follow before T8 acceptance.

T7 subsequently accepted: independent `s12a_t5_boundary_map` review APPROVE, zero findings, including recomputation of all five canonical query hashes and exact embedded/sibling coverage equality. Coordinator full 1753 passed with only W2/W4 and existing warning; focused 332 passed; canonical [4]/[5]/[6]/[9]/[20]/[24], reconstruction and smoke pass. Integrity retains only the authorized config mismatch until T11. T8 is authorized; no real institutional rows or complete institutional units exist, so downstream docs must not claim them.

## T8 Core contracts candidate

Existing Core contract test RED was observed before four document edits, then GREEN without changing the test. Core03/09 are two-line insertions only; Core04 documents three schemas, row whitelists, public acquisition boundary and per-kind config pins; Core05 retains the exact five authorized status-cell edits and adds store-time lifecycle, exact privacy/envelope policy and explicit text-only offline-parser limitation. Per-run T7 availability is distinguished from connector implementation. Coordinator inspected the complete Core diff and reran full regression (1754 passed, one expected T9-owned W2 failure, one existing warning), reconstruction/smoke and canonical identity/containment oracles. No production, test, source-config or raw changes during T8. Independent T8 review is pending; T9 has not started. Manifest count remains 0; live window remains closed.

T8 independent review subsequently APPROVE, zero findings (`s12a_t5_boundary_map`), with independent [23]/[26] and two scoped integrity tests passing and candidate hashes matching the implementer report. Coordinator approves T8 within its explicit W2/pre-generation windows and authorizes T9 only: ADR-016, limitations, runbook and five control records/state. No hashed files may change in T9, and generation remains pending until T10 passes. Exact plan4/5 hashes and six canonical-command UTF-8 byte equalities rechecked; both manifests, generator, acquisition entrypoint/init files and index remain unchanged.

## T9 acceptance — controls and authority rationale

Seven scoped files updated: five controls, acquisition runbook and `.workflow/state.json`. Existing missing-KL test RED was reproduced before edits; the integrity-contract module is now 14 passed with no test changes. ADR-016 records DD-1–20, AM-1–9, exact privacy/text-only narrowing, source classes/operating settings, actual five zero-request T7 outcomes, §7 change classes and one-run authorization. KL-47–51 cite actual raw attempts; KL-45 extends only the deferred consumption roots. Original S12 child goals/dependencies are copied exactly. Historical top-level S05/v0.2.0, earlier slices, ADR-015 and S11 §L traceability remain intact. S11 is correctly MERGED with PR #14/a043ed8 and the prescribed CI fallback. Live source/R5 inputs are BLOCKED; framework/reconstruction proofs are TESTED on doubles only.

Coordinator review corrected runbook years/guard scope and requested verbatim future-use privacy refusal templates, explicitly not actual T7 events. Implementer reran the final full suite after these additions: 1755 passed, one existing warning (15.85s). Coordinator independently ran the full suite: 1755 passed, one existing warning (15.80s), inspected all seven diffs and verified exact split/history invariants. A read-only split-check diagnostic initially used `task_id` instead of the original assessment's `child_task_id`; corrected check passed, no file changes from either probe. Independent `s12a_t5_boundary_map` T9 review APPROVE, zero findings; W2 closes. T9 report is local `t9-report.md`; no manifest or source-network action occurred. Coordinator accepts T9 and authorizes T10 only. Generation remains count 0 until T10 passes.

## T10–T12 completion and review hold

T10 prescribed filtered full regression passed (1740 passed/1 deselected/one existing warning); every applicable canonical gate passed, with [22] superseded and [12] correctly deferred. Prospective new-file secret/scope scan passed for 32 files, with empty index. ADR-016 and independent T9/production approvals were present before the single T11 invocation. Generator exited 0 by 2026-09-11 22:31:25 UTC; count is exactly 1 and permission exhausted. Only five machine authority rows changed and were mirrored into §11; snapshot manifest has ten new attempt/coverage rows, no changed/deleted old rows. Immediate [12] passed. Independent post-generation review APPROVE after one non-hashed state timestamp correction, reproduced before fixing and rechecked afterward; no generation retry.

T12 completed by 22:37:36 UTC: all 26 executable canonical entries passed; [22] remains superseded, never PASS. Unexcluded pytest 1755 passed/one existing warning (15.75s); local make ci also passed 1755 tests (15.66s), all four static checks and compilation, integrity, two-scenario validation, default reconstruction (1 snapshot/4 artifacts), smoke, 118 functional browser tests (131.49s) and four visual comparisons (25.75s). The six canonical S11/frozen/config/Core checks ran against uncommitted HEAD a043ed8. Full raw commands/results are in test_evidence.md. The standard locked dev/e2e environment synchronized cached extras; no dependency/lockfile change or network download was needed for final CI. No live source work followed T7.

Only final evidence/control metadata changed after these gates, not code/config/Core/raw/manifests/browser inputs. No database, migration, service or new dependency was introduced. The download authorized in this exchange installed the existing pinned browser runtime in the user cache; privileged dependency installation was unavailable and unnecessary after normal launch proof. All source acquisitions remain honestly unavailable; no institutional analytical snapshot or source-specific data parser was fabricated. DD-15(b)'s approved text-only policy remains an intentional limitation, not universal PII detection. Preexisting Comtrade/UV, narrative/extractor, RunReport counting, custom build-root and historical acceptance-script issues remain deferred; S12b/S12c/later work did not start.

Awaiting session implementation review. No staging, commit, push, PR or merge. Local-only ruling, plan, checkpoint and detailed drafts remain ignored/unstaged; .env was never read. Branch-handoff skill is adapted to the owner's explicit keep-uncommitted instruction; no integration menu, cleanup or automatic commit. TDD, read-first/provenance, strict independent reviews and final self-audit govern this handoff.


## Candidate identity and changed-file inventory

Review candidate SHA-256: `98a0f95b83abbfc81b4f7cd9a4f1686e020cc194df02bcc7a31eb4a2a56ace1b`.

Identity scope: 65 implementation/config/data/docs/control/test files, excluding the five S12a slice-record Markdown files to avoid self-reference; ignored local planning and the exported diff are also outside this identity. Base is `a043ed8dc1d477de50149b39de657bc963e785d7`. Reproduction: collect the tracked HEAD diff plus nonignored untracked paths, remove `.workflow/slices/S12a-acquisition-framework-institutional-sources/`, sort paths; form `{"base": HEAD, "files": [{"path": path, "sha256": SHA256(file_bytes), "bytes": len(file_bytes)}, ...]}`; serialize with Python `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n'`, UTF-8 encode, SHA-256. The full exported diff includes all 70 files, including the five excluded records, and is local-only under `.autonomous-workflow/drafts/s12a-acquisition-framework-institutional-sources/implementation-review.diff`.

Final inventory: 38 modified tracked files and 32 new nonignored files; none staged. `M`/`A` below describe the prospective candidate, not index state.

```text
A .workflow/slices/S12a-acquisition-framework-institutional-sources/context.md
A .workflow/slices/S12a-acquisition-framework-institutional-sources/implementation_log.md
A .workflow/slices/S12a-acquisition-framework-institutional-sources/persona.md
A .workflow/slices/S12a-acquisition-framework-institutional-sources/plan.md
A .workflow/slices/S12a-acquisition-framework-institutional-sources/test_evidence.md
M .workflow/state.json
M Makefile
M config/acquisition_sources.v1.yaml
M data/manifests/snapshot_manifest.json
A data/raw/gastat/e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d/20260911T215546Z/attempt.json
A data/raw/gastat/e7cb218115c5b69b8341bbae20e35d056fd55e67283bea3b7c6c1b7695eec81d/20260911T215546Z/coverage.json
A data/raw/ministry_of_industry/b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f/20260911T215956Z/attempt.json
A data/raw/ministry_of_industry/b5fd807aa458a97d4eae2dbb072075614f7061e77d3e130ffea85f46fb22673f/20260911T215956Z/coverage.json
A data/raw/modon/94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135/20260911T215956Z/attempt.json
A data/raw/modon/94801a4f5e4b99c963baca7ca892d508b7531bc01853205c4b950ec2b0480135/20260911T215956Z/coverage.json
A data/raw/saber_registry/e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3/20260911T220134Z/attempt.json
A data/raw/saber_registry/e20dac0cf35c1b06bc91836d25f7e5ca0670fb5b764f4af5adfb90289aa51be3/20260911T220134Z/coverage.json
A data/raw/saso_catalogue/9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49/20260911T220134Z/attempt.json
A data/raw/saso_catalogue/9529b34e0e2b6c2c39cdc9dfa404bf9b5b96c6f6b6de821a4281e928b8b07b49/20260911T220134Z/coverage.json
M docs/ARCHITECTURE_DECISIONS.md
M docs/BUILD_PROGRESS.md
M docs/BUILD_ROADMAP.md
M docs/KNOWN_LIMITATIONS.md
M docs/REQUIREMENTS_TRACEABILITY.md
M docs/authority/00_AUTHORITY_MANIFEST.md
M docs/authority/authority_hashes.json
M docs/core/03_SYSTEM_ARCHITECTURE.md
M docs/core/04_CANONICAL_DATA_MODEL.md
M docs/core/05_DATA_SOURCES_AND_INGESTION.md
M docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
M docs/implementation/ACQUISITION_RUNBOOK.md
M scripts/reconstruct_snapshot.py
M src/ior_mvp/acquisition/cli.py
M src/ior_mvp/acquisition/connectors/base.py
A src/ior_mvp/acquisition/connectors/gastat.py
A src/ior_mvp/acquisition/connectors/ministry_of_industry.py
A src/ior_mvp/acquisition/connectors/modon.py
A src/ior_mvp/acquisition/connectors/saber_registry.py
A src/ior_mvp/acquisition/connectors/saso_catalogue.py
M src/ior_mvp/acquisition/connectors/un_comtrade.py
M src/ior_mvp/acquisition/connectors/wits_trade.py
M src/ior_mvp/acquisition/connectors/zatca_tariff.py
M src/ior_mvp/acquisition/contracts.py
M src/ior_mvp/acquisition/coverage.py
M src/ior_mvp/acquisition/harmonise.py
A src/ior_mvp/acquisition/kinds.py
M src/ior_mvp/acquisition/passports.py
M src/ior_mvp/acquisition/pipeline.py
M src/ior_mvp/acquisition/repository.py
M src/ior_mvp/acquisition/snapshots.py
M src/ior_mvp/acquisition/source_config.py
M tests/acquisition_doubles.py
A tests/fixtures/acquisition/test_double_directory_page1_of_2.json
A tests/fixtures/acquisition/test_double_directory_page2_of_2.json
A tests/fixtures/acquisition/test_double_directory_personal_fields.json
A tests/fixtures/acquisition/test_double_directory_rows.json
A tests/fixtures/acquisition/test_double_production_rows.json
A tests/fixtures/acquisition/test_double_registry_rows.json
M tests/test_acquisition_cli.py
M tests/test_acquisition_config.py
M tests/test_acquisition_connectors.py
A tests/test_acquisition_institutional_connectors.py
A tests/test_acquisition_institutional_snapshots.py
A tests/test_acquisition_kind_registry.py
A tests/test_acquisition_normalization_status.py
M tests/test_acquisition_reconstruction.py
M tests/test_acquisition_snapshots.py
A tests/test_acquisition_stage_specs.py
M tests/test_acquisition_stored_artifacts.py
M tests/test_integrity_contract.py
```

Final post-record rerun: 1755 passed / one existing warning in 15.83s; integrity and all four static checks PASS. Final scope/prospective-secret scan, exact six canonical byte checks, frozen oracles, single-generation hashes and empty index PASS. Independent final handoff-record review APPROVE, zero findings. Muhasabah self-audit PASS. No unapproved scope deviation; the source-unavailability, privacy narrowing and unrelated deferrals above remain explicit. Session implementation review is still required before any commit.

## 2026-09-12 — independent implementation review and owner takeover

Independent implementation review (Claude Code session, model `claude-fable-5`, six read-only review agents, distinct from the Codex `gpt-5.6-sol` implementer): **APPROVE, zero defects** on candidate identity `98a0f95b83abbfc81b4f7cd9a4f1686e020cc194df02bcc7a31eb4a2a56ace1b`, 2026-09-12T02:41Z. The reviewer reran pytest (1755 passed, twice), integrity, scenario validation, reconstruction, smoke, the four static checks, browser preflight and the 118-node functional browser gate, executed the six canonical oracles verbatim, and audited all 70 files against the approved plan. The reviewer did **not** rerun `make ci` or the four visual tests; those remain implementer-reported until hosted CI runs them on the exact PR head. Details and the five low-severity non-blocking observations: `reviewer_findings.md`; verdict summary: `implementation_review.md`.

Owner lead-agent takeover (Cursor session, `claude-fable-5.1`): the owner delegated project decisions, acceptance, merge and delivery on 2026-09-12. Candidate identity was recomputed against the actual working tree and matched the retained approval exactly (65 files, base `a043ed8`, index empty). Owner proof commands on the unchanged candidate: integrity PASS, 1755 passed / 1 warning, smoke PASS, prohibited-file scan PASS. Approval preserved without re-implementation or repeated review. Delivery proceeds: selective staging of the 70 candidate paths plus these two review records, fail-closed secret scan, commit, non-force push, PR, exact-head hosted CI, recorded owner merge approval, merge, merged-main verification. Local-only records (`.autonomous-workflow/**`, `.env`) stay unstaged. Merge facts will be written to `pr_record.md` / `completion.md` and the control records after merge.
