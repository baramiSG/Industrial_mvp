# S18b0 independent implementation review R1

**REJECT** exact candidate tree `42e7b8db8865e474bd94720cec240ecc73d66433`: two blocking numeric-boundary findings below. This verdict is issued without waiting for the full gates because the defects were directly reproduced; the coordinator stopped the current gate runners and preserved their partial evidence. No gate pass, implementation acceptance or delivery is inferred for this tree.

Reviewer: `/root/s18a_delivery_review`, a separate Codex implementation reviewer, not the author or planner. This is owner-delegated same-model review, not Claude approval or cross-model review.

## Preparation and reviewed identity

Reused prior full governing preparation and read the task-specific approved B0 plan, plan review, model-cycle correction review/patch acceptance, handoff, current controls and implementation evidence. Revisited the authoritative methodology DOCX evidence/authorization/dossier requirements, applicable Core04/Core09 executive contracts and operating configuration. The approved plan SHA-256 is `00dc585a6f909b291195faceb7bc94b5decbd6cccccf8182b7039557d42bc67e`; plan-review SHA-256 is `1198c5f0a02c822938e3da7b0a20da440a81b9ab13f418ecd8b36d722b7bb481`; correction review is `975be3ae8b780399fd15e53b71bfe6e6c1a74954166171b26e4bc864ea23fe72`.

After reading, adopted typed-API boundary reviewer and evidence-publication auditor personas because the candidate hardens malformed numeric/mapping inputs and publishes immutable provenance evidence. Applied installed strict-reviewer, test-driven-development, verification-before-completion, github-flow, sanad-provenance, al-muhasibi and muhasabah-gate skills; the relevant skill files were read and their proof, boundary and attribution requirements used.

Created an independent inspection clone `/tmp/s18b0-independent-review-r1`, checked out proof-only commit `f30afc5c5fbfa4253e060318a1702ed0d100a189`, and verified its tree equals the submitted candidate. Synced only its own locked dev environment, using Python3.14.6/Pydantic2.13.5. No source/proof-runner worktree, service, Docker, Aura, source index or GitHub state was modified by this reviewer. The inspection copy remains clean apart from ignored environment files.

## Blocking findings

### B0-R1-F1 — Integer conversion overflow escapes the new finite-number boundary

Severity: **P2, blocking this bounded malformed-EVSI repair**.

Location: `src/ior_mvp/executive/validation.py:85–87`; exercised through `service._evsi_summary` and `GET /api/executive/summary`.

`finite_number` accepts exact integer/float types but calls `math.isfinite(value)` before protecting float conversion. Python converts a sufficiently large integer internally and raises `OverflowError`. Therefore the newly introduced validator violates its typed-error contract for supplied numeric inputs that cannot be represented in the response's finite float representation.

Direct reviewer proof on the exact candidate:

```text
finite_number(10**400, "EVSI evidence_cost_m_sar") -> OverflowError: int too large to convert to float
finite_number(-(10**400), "EVSI evidence_cost_m_sar") -> OverflowError
SyntheticEvsiCase(..., evidence_cost_m_sar=10**400) -> ValidationError
```

With the real API and only `service.analyze` patched to return a deep copy of the normal steel simulated analysis whose `evsi.evidence_cost_m_sar` is `10**400`, `TestClient(app, raise_server_exceptions=False).get('/api/executive/summary')` returns **HTTP500 `Internal Server Error`**, not the existing governed422. Executive caches were cleared before and after the probe. No canonical input was edited. This is an injected boundary defect; current frozen-input reachability is not asserted.

Required correction: validate exact accepted numeric types, perform the necessary float conversion with narrowly scoped conversion-overflow handling, and reject unrepresentable/nonfinite values with the existing sanitized `ExecutiveIntegrityError`. Preserve all finite representable numbers and existing serialization. Do not add a policy threshold, clamp, default value or broad API/service exception catch.

Required regression: direct helper and real API injection tests for positive and negative oversized integers, preferably parameterized across the five supplied EVSI numeric fields; retain the model's rejection. Capture RED against this exact rejected tree before correction, then typed422 GREEN. Positive controls must retain integer/float zero, ordinary finite values and individually representable large positive/negative floats.

### B0-R1-F2 — All three EVSI aggregate operations can overflow despite finite members

Severity: **P2, blocking this bounded malformed-EVSI repair**.

Location: `src/ior_mvp/executive/service.py:186–190` (`total_approximate_evsi_m_sar`, `positive_approximate_evsi_m_sar`, `non_positive_approximate_evsi_m_sar`).

Per-row finite validation does not establish that `math.fsum` can represent the aggregate. `fsum` raises `OverflowError` for the reproduced finite-value cases. Each exception currently escapes as HTTP500. Guarding only the total is insufficient: a finite total may coexist with an overflowing positive or non-positive bucket.

Direct `_evsi_summary` and real API probes produced these results on the exact candidate:

| Injected approximate EVSI values, in listed case order | Failure | API |
|---|---|---|
| steel=`1e308`, tinplate=`1e308` | total `fsum`: `OverflowError: intermediate overflow in fsum` | 500 |
| steel=`-1e308`, tinplate=`-1e308` | total `fsum`: same error | 500 |
| steel=`1e308`, polypropylene=`-1e308`, galvalume=`1e308` | total is representable; positive bucket overflows at line187 | 500 |
| steel=`-1e308`, polypropylene=`1e308`, galvalume=`-1e308` | total is `-1e308` and positive bucket representable; non-positive bucket overflows at line188 | 500 |

The actual `_opportunity_order()` begins steel, polypropylene, galvalume, tinplate, so the bucket probes exercise the same order over the real summary endpoint. Other analyses remain unchanged deep copies. Positive control: a single steel approximate EVSI=`1e308` succeeds in both direct summary construction and the real API, returning HTTP200 with total=`1e308`. Direct `finite_number(0)`, `finite_number(1.0)`, `finite_number(1e308)` and `finite_number(-1e308)` also succeed.

Required correction: narrowly handle overflow for **each of the existing three `fsum` operations** and fail with the existing sanitized integrity error; require finite representable output. Preserve `math.fsum` and every successful output byte. Do not replace the summation algorithm, introduce arbitrary limits, silently omit rows, clamp, or return zero/unavailable on failure. The API mapping itself must remain unchanged.

Required regression: direct and real API tests for positive/negative total overflow and both balanced/interspersed bucket-overflow cases above; expect `ExecutiveIntegrityError` directly and governed422 over HTTP. Include successful cancellation/large-finite, zero, optional-absence and ordinary response-byte controls. Each newly added regression must be demonstrably RED on this rejected candidate before repair.

The correction can remain within the already permitted `validation.py`, `service.py` and `tests/test_executive_validation.py` paths. It implements numeric representation/error handling, not a new economic threshold or summation policy. If the proposed correction requires another path or changes valid semantics, obtain a separate reviewed amendment instead of extending this finding's scope. The correction plan/patch requires independent review and separate delegated acceptance before application; a changed candidate must be frozen and run the complete prescribed gate set anew.

## Requirement and evidence assessment

| Requirement | Reviewer evidence | Assessment |
|---|---|---|
| Typed trade/year/R11 and dependent scenario mappings | Actual source/test diff; own focused run; API injection tests exercise service/provenance boundaries rather than only helper mocks | Implemented for enumerated fixtures; no broader malformed-path certification |
| Strict finite supplied EVSI/model construction | Corrected model SHA-256 `9804686261c2f1fd7e1dfde9201e3d4d051f0f74bec226b2d9ba5e002537ddf1` matches separately approved correction; direct oversized-int/model/API and aggregate probes above | **REJECT: F1/F2** |
| Legitimate public ClassD and optional absent/zero EVSI | Existing and new positive tests, independently rerun | PASS for scoped cases |
| Public/synthetic partition; referenced-row fail-closed | New evidence marker/model/row tests plus retained AM4 assertions | PASS for covered cases |
| Existing AM4 True/False422, B3, claim tests preserved | Git diff confirms the only test-path delta is new `tests/test_executive_validation.py`; original executive tests remain byte-identical | PASS |
| Meaningful original-defect evidence | Read full-original-RED identity/results: base tree1364789a plus only the new test file,113 failed/177 passed, no pre-existing suite failures; retained import-cycle failure and separately approved correction are disclosed | Evidence credible and accurately scoped; counts attributed to retained author/coordinator run |
| Focused suite on candidate | Reviewer ran the complete prescribed seven-file focused command in own clone: **290 passed,1 warning,22.02s** | PASS, but tests omitted F1/F2 |
| Valid response/outcome preservation | Reviewer independently compared12 raw API responses,12 canonical responses and22 complete analyses against all46 saved base artifacts, verified their hashes, all11 real decisions equal | PASS |
| Frozen roots and scope | Git tree equality against base for `docs/core`, `docs/authority`, `config`, `data`, `browser_tests`, `src/ior_mvp/static`; exact plan hash; product diff limited to allowed executive files | PASS |
| Five controls and state | Read appended control sections; original state key/values compare equal, with only `overnight_completion_20260923` added semantically (formatting expanded). Precise deferrals and same-model attribution retained | No additional blocking finding; update narrow repair claims after F1/F2 handling |
| Immutable S18a evidence publication | Independently checked54 records/hash/size (1,940,576 content bytes), bound manifest as55th file; all56 subset checksum entries pass; original full receipt and original856-entry list correctly distinguished from published subset | PASS |
| Publication security and claims | Existing scanner passes on1637 tracked files; supplemental credential-pattern scan found zero alerts. Wrapper maps renamed `.log.txt` paths; no prohibited archive/index/credential/transcript payload. GitHub confirms PR37 merge/time/commit and six successful main jobs | No additional blocking finding; scoped scan is not a general security certification |
| Full exact-candidate gates and independent acceptance | Coordinator began the prescribed two-root proof and stopped it after confirmed blocking findings | **Not complete/not approved**; partial logs remain historical, no carry-forward approval |

## Publication and historical accuracy

The publication manifest retains its reviewed SHA-256 `45359ab136094d6ddb14bb50ab58fa810ced7e8f76475b72072c24a278c175ef`. The immutable receipt remains `8fc1368371a067bc3e2fe99359600be5d01c663024644e9e3d8147478e4122fb`; the wrapper explains its historical review-pending wording and local-only paths without editing the source bytes. It explicitly publishes a subset rather than all856 original files. The known main-run facts in the delivery record were confirmed against GitHub run35920687954 at merge `b4a00adb685c61c4d50c24e94647fbd24e599096`, all six jobs successful. The original Claude implementation approval and this reviewer’s earlier same-model delivery approval remain distinct.

Public D proxies, optional EVSI absence and existing successful field serialization are not findings. The retained model import-cycle failure was corrected under independently reviewed authority and is not concealed as an initial GREEN result. Explicit case-level EVSI availability, broad R12 case-wide needs and other untested malformed paths remain open; their deferral does not erase F1/F2 within the supplied-numeric boundary currently being repaired.

## Sanad provenance and Muhasabah

**PASS for this REJECT verdict.** Direct evidence: isolated exact-tree checkout; actual source/test/control/publication inspection; own290-test run; own46-artifact comparison; own hash/secret/frozen-tree/state checks; real helper/model/direct-summary/TestClient overflow probes with positive controls; current GitHub merge/main-run queries. Attributed evidence: original RED counts, prior correction review assertions, and coordinator-started/stopped full gates remain attributed to their retained records rather than claimed as my executions. Assumptions: injected malformed analysis values test the advertised boundary contract; they do not demonstrate current frozen data is corrupt or that arbitrary callers can inject them. Risks: this repair must preserve successful `fsum` outputs, reject overflows only at their numeric operations, and never weaken checks. Unverified: complete B0 full gates, hosted checks, delivery, later frontend/Aura work and final Claude release review. No source/index/service/Aura/GitHub mutation was made by this reviewer; only the independent inspection environment and this external report were created.
