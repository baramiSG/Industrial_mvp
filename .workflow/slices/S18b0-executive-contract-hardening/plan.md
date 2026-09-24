# S18b0 executive malformed-input and partition hardening implementation plan

> Required implementation skill: executing-plans, TDD and systematic-debugging. Coordinator dispatches a distinct implementer only after a separate plan reviewer APPROVEs these exact bytes and delegated acceptance is recorded. No task-level commits; keep one exact uncommitted candidate for separate implementation review.

**Goal:** close the reproduced executive projection error and model partition gaps carried from AM4 without changing valid response bytes, schema, domain decisions, frozen inputs or generated artifacts.

**Architecture:** validate malformed values at their immediate projection boundary and raise existing ExecutiveIntegrityError; tighten EvidenceReference's public branch invariant; keep API's existing explicit exception mapping. Do not catch Exception/AttributeError/KeyError/TypeError globally or convert programming mistakes to an integrity success.

**Tech stack:** existing Python/Pydantic/FastAPI/pytest, no dependencies.

**Spec:** owner overnight mandate; AM4§5; Core04§15 public/synthetic partition; Core09§11 typed integrity422; existing accepted S18a contract. This plan is a separate additive follow-up, never an amendment of S18a candidate1364789a or its approval.

Status: PLANNER PROPOSAL v3; adds owner-requested immutable S18a durable evidence publication under a finite hash-bound whitelist. Previous v1/v2 retained in revisions/. Branch `slice/s18b0-executive-contract-hardening`, new isolated worktree from delivered S18a. S18b frontend depends on this child if approved, and must rebind its base after merge. Planner `/root/s18b_milestone_planner`; same-model Codex delegation, no approval issued.

## Preparation, authority and observed evidence

Read AGENTS/Manifest, original methodology DOCX §§2.1/10/11/15, Core04/09, approved S18a design/plan/AM1–4 and receipt, owner records and actual executive source/tests. Applied task-standards, project-orientation, writing-plans, sanad-provenance, al-muhasibi, muhasabah-gate and github-flow. Personas selected afterward: senior API-contract engineer and evidence-partition verification engineer. The broader frontend design skills apply to the sibling S18b plan, not product code here.

Direct read-only diagnostics in `ROBUSTNESS-READONLY-PROBES.json` on retained1364789a show:
- build_steps: empty trade→ValueError; missing trade.year→KeyError; missing R11→StopIteration.
- _evsi_summary: provided nonnumeric evidence_cost_m_sar→ValueError.
- EvidenceReference: flagfalse with status synthetic or source DEMO_GENERATOR is accepted.
These are reproducible projection/model observations, not assertions of currently reachable malformed frozen inputs or endpoint failures. Upstream loaders protect normal inputs today. The actual regression tests below must demonstrate API behavior with explicit service-layer injection and prove original defects RED.

## Global constraints and review focus

- Valid output serialization/schema_version1.0.0 remains byte-for-byte identical across all11 summary/case responses, excluding no field; engine outcomes/evidence unchanged.
- No Core/config/top-level source/browser/data/manifests/baselines/pins changes or generator invocations.
- Public ClassD **proxies** remain permitted. Reject synthetic provenance markers, not D alone; never equate all D with simulation.
- Optional absent EVSI remains allowed; numeric zero remains AVAILABLE and is not classified absent. Booleans/strings/nonfinite values are not accepted as numeric elicitation input.
- A missing referenced evidence row fails closed; there is no new obligation that optional EVSI rows exist or that every generic suffix always exists.
- Every source change must map to a reproduced failure or directly required validator test; no unrelated model cleanup.
- Module limits<=500 lines, Google-style docstrings/type signatures for new helpers. Source writer pauses before review.

Review focus: malformed empty sequence; wrong types in dependent scenarios; numeric bool/NaN/infinity coercion; false synthetic_flag laundering; valid public D and omitted EVSI false positives. Each has explicit tests below.

## Allowed paths

Modify `src/ior_mvp/executive/{case_projection,service,provenance,provenance_models}.py`. Add `src/ior_mvp/executive/validation.py` for shared mapping/rows/latest-trade/finite-number validators only when extracted helpers improve clarity and keep existing modules bounded. `models.py` may be modified **only** to reject nonfinite/boolean/string EVSI numerics in SyntheticEvsiCase and enforce its existing availability inputs/results; no fields/schema/defaults added. If centralized service validation fully enforces this for serialized API outputs, model changes still independently protect construction but must preserve correct valid values.

Tests: modify `tests/test_executive_{models,service,api,claims}.py`; create `tests/test_executive_validation.py` to keep existing tests under500 lines. Do not alter tests' AM4 assertions except moving intact tests to maintain line limits with preserved collection IDs documented. Capture line counts and full assertion diff.

Control paths: append new ADR to `docs/ARCHITECTURE_DECISIONS.md`, additive S18b0 rows/notes in `docs/{BUILD_ROADMAP,BUILD_PROGRESS,REQUIREMENTS_TRACEABILITY,KNOWN_LIMITATIONS}.md`, `.workflow/state.json`, and new `.workflow/slices/S18b0-executive-contract-hardening/{persona,context,plan,plan_review,implementation_log,test_evidence,implementation_review,reviewer_findings,pr_record,completion}.md`. Preserve historical S18a descriptions and approval packets. Coordinator owns control updates. External final tree/gate receipt; do not embed candidateOID in its own contents.

Additional additive publication paths: the54 `published_path` records in coordinator-prepared `../s18a-delivery/publication-draft/PUBLICATION-MANIFEST.json` (SHA256 `45359ab136094d6ddb14bb50ab58fa810ced7e8f76475b72072c24a278c175ef`) prefixed with `.workflow/slices/S18-executive-mode/delivery-evidence/`, plus that exact manifest itself (55 unchanged source files total), and new `delivery-evidence/{README.md,SHA256SUMS}` and `.workflow/slices/S18-executive-mode/delivery_record.md`. These are new files only; no existing approved S18a file may change. This coordinator export supersedes the unused56-file planner draft whitelist (retained locally as planning history). Publication is1.95MB by coordinator report; writer verifies actual bytes. No candidate archive, Git index, credential, owner source log or bulk runtime path is allowed.

Before writing, compute intersection of allowed paths with graph.inputs, visual.source_tree, authority and snapshot lists. It must be empty. New validation.py under executive is not included by current nonrecursive top-level graph/visual discovery, but verify actual discovery. Unexpected intersection or required new path stops for amendment.

## Task1 — snapshot valid contracts and demonstrate original defects

- [ ] Bind merged base and no competing writer. Save sorted canonical JSON for executive summary/all11 cases and all11 public/simulated analysis outcomes externally; hash each.
- [ ] Add tests for build_steps and build_vectors empty trade, trade row without year, noninteger/bool year, required R11 missing/duplicate (only require exactlyone if duplicate list violates existing unique-rule contract; if not established keep missing-only guard). Expect ExecutiveIntegrityError with sanitized field context.
- [ ] Add API tests using TestClient(raise_server_exceptions=False) and monkeypatch **service.analyze** to deepcopy valid analysis then inject the chosen malformed field. Clear executive caches around each test. Expect422/detail.code EXECUTIVE_INTEGRITY_ERROR, never500/partial200. Existing source must fail the assertion for at least the directly diagnosed cases; capture command/output/exit/tree.
- [ ] Add summary EVSI injected cases: absent required numeric key, None inside supplied available block, nonnumeric string, numeric string, True/False, NaN,+Inf,-Inf, malformed mapping and blank next_fact. Existing `_evsi_summary` coercion must produce RED where it coerces or leaks exceptions. Valid zero and missing block controls must stay valid.
- [ ] Add model RED for public flagfalse+statusSYNTHETIC and flagfalse+sourceDEMO_GENERATOR. Positive control public flagfalse/statusINFERRED/classD/sourcePUBLIC-PROXY, no scenario/labels, remains valid.

Example required regression:
```python
@pytest.mark.parametrize("marker", [{"status": "synthetic"}, {"source": "DEMO_GENERATOR"}])
def test_public_evidence_reference_rejects_synthetic_marker(marker):
    row = dict(evidence_id="E-PUBLIC", source="PUBLIC", status="observed",
               evidence_class="D", synthetic_flag=False, supports=())
    row.update(marker)
    with pytest.raises(ValidationError):
        EvidenceReference(**row)
```
This test fails on1364789a because both objects are accepted (read-only probe).

## Task2 — narrow typed validation and partition repair

Helper contracts if a shared module is needed:
`mapping(value: object, field: str) -> Mapping[str, Any]`;
`mapping_rows(value: object, field: str, *, nonempty: bool=False) -> tuple[Mapping[str,Any],...]`;
`latest_trade(value: object) -> Mapping[str,Any]` validates nonempty rows/year type before max;
`finite_number(value: object, field: str) -> float` accepts type int/float excludingbool, requires math.isfinite, raises ExecutiveIntegrityError otherwise. These validators do not introduce policy thresholds or default missing values.

- [ ] Validate nonempty trade and integer years before both max calls. Require needed R11 via explicit lookup and named integrity error, not bare next(). No new behavior for legitimate no-preferred-route cases; retain True/False route tests unchanged.
- [ ] Validate required supplied EVSI keys/types before float conversion; preserve original finite numeric values and math.fsum behavior,7available/4unavailable and valid zero. Do not reinterpret absent block as invalid, or return unavailable for a malformed supplied block.
- [ ] Guard dependent scenarios mapping and each synthetic_inputs mapping before `.get('shared_enabler')`; replace unique-ID scan's unchecked row.get with validated mapping traversal. Preserve exact graph feed/source-path/dependency membership policy and all B3 tests. Add direct injected nonmapping synthetic_inputs/list/None/string/scenario row mutation; typed422 fixture bypasses only loader to isolate this boundary. No foreign-ID exception expansion.
- [ ] Tighten EvidenceReference public else branch to reject statusSYNTHETIC or sourceDEMO_GENERATOR alongside existing scenario/labels prohibition. Synthetic branch retains all existing requirements; preserve public D proxy positive case.
- [ ] Keep executive/api.py entirely unchanged: its existing ExecutiveIntegrityError/ValidationError catch clauses already implement the intended mapping. Any newly needed API file edit or exception mapping requires a separate reviewed amendment; never add broad catch-all. API error detail must not leak raw source/credential paths; field label only.
- [ ] GREEN focused regression suite and canonical byte comparison of all valid responses against Task1 originals.

## Task3 — close or precisely retain validator observations

- [ ] Model mutation tests cover duplicate/out-of-order/missing steps/vectors, duplicate claims/evidence IDs, missing referenced IDs, public↔synthetic branch membership, wrong scenario/class/source/labels and supplied unavailable values. Existing failures proving correct validation are positive coverage, not invented bug fixes.
- [ ] Review current exact R4 mapping test: `test_every_real_public_rule_id_uses_the_amended_exact_mapping` already checks R4-F/R4-D and no R4. Record original “trivial R4-only coverage” observation as superseded by this source evidence; preserve that meaningful test, no redundant replacement.
- [ ] Remove a single actual referenced synthetic evidence row from copies of steel/aluminium responses and assert fail-closed. Separately exercise valid cases with absent optional EVSI and no EVSI row. Do not require absent optional suffix globally, and do not relax the remaining current-scenario evidence invariant.
- [ ] Record case-level explicit EVSI schema marker OPEN, with frontend exact summary-row availability join as presentation mitigation. Record broad R12 case-wide needs OPEN with honest case-wide labeling. These require separately reviewed contract expansion/mapping, not synthetic precision.
- [ ] Add new control entries describing exact closed malformed paths and exact still-unverified ones. “All malformed paths fixed” is prohibited. Update limitations with repro case names/tests.

## Task3b — publish immutable S18a review and essential verification evidence

- [ ] Use the coordinator's exact existing55-file publication-draft export; independent reviewer inspects security/scope, especially host environment/logs, for credentials or sensitive contents. No raw .env, owner transcript, source Git index, session JSONL or full candidate archive is allowed. If a whitelisted file contains sensitive material, exclude it through a reviewed manifest revision; never silently redact a byte-identical source file then claim its old hash.
- [ ] Copy only exact listed bytes to destination paths; .log sources become .txt destinations with identical bytes. Preserve receipt SHA256 `8fc1368371a067bc3e2fe99359600be5d01c663024644e9e3d8147478e4122fb`, original856-entry checksum-list SHA256 `af9c76a7594ed497ae2f0b6f9098031b90f1416cc1034666c3522ac7ad238214`, Claude review SHA256 `8c5ae016ada1adf520352afbe2679bbe82c455d121ff32a355695a315d8a5562`. Full original local bundle remains untouched.
- [ ] README explains immutable receipt's historical review-pending wording, links the later Claude verdict/owner delivery record, and maps essential local receipt references to the published relative counterparts. Original856 checksum list binds the complete retained local bundle; only the published subset is in Git. New subset SHA256SUMS verifies all published files, and PUBLICATION-MANIFEST records original source name/hash and new repository-relative path; never claim all856 original files are published.
- [ ] Add delivery_record.md with only observed PR37/head/tree/review/owner acceptance/hosted checks/merge/mainCI facts provided by coordinator. Do not preclaim merge or alter source candidate. If merge/mainCI still pending, state pending and allow later additive separately reviewed record.
- [ ] Scan entire publication using existing prohibited/secret scanner plus direct review of selected metadata; stage approved .txt/.json/.md/.py/.patch/checksum files only after exact candidate review. No source packet content modification. Independent implementation reviewer confirms artifact hashes and all claims are sourced.

## Task4 — exact proof, review and delivery

- [ ] Focused RED and GREEN: `PYTHONPATH=src uv run --locked --extra dev pytest -q tests/test_executive_validation.py tests/test_executive_models.py tests/test_executive_service.py tests/test_executive_api.py tests/test_executive_claims.py tests/test_executive_isolation.py tests/test_executive_performance.py`. Actual counts only after running.
- [ ] Finish allowed docs, freeze exact candidate with new alternate index; compare all valid API bytes/outcomes and all protected roots/packet/index digests. Source index unchanged before acceptance.
- [ ] Exact clean proof root full `make ci`, plus different-path root integrity/reconstruction/full pytest and `make e2e` compare-only. Local graph fresh owned container/credential; no Aura env. Full makeci already covers graph live/UI/unavailable; inspect every result. All tests pass; no generation needed. This child does not inherit AM4's ordered R1 special proof because pixels/runIDs are byte-identical, but demonstrate baseline tree/digests exactly preserved.
- [ ] Separate implementation reviewer in isolated exact copy checks diff, changed tests, original-defect evidence, valid bytes and full gate logs; explicit exact-tree APPROVE at zero blocking findings. Coordinator delegated acceptance separate.
- [ ] Stage/commit exact approved tree, push PR, inspect hosted checks at exact PR head, exact-head reviewer approval after greenCI, permitted merge, verify target-branchCI and publish durable receipt/hash/review as owner mandate. No release tag.

Stop for unexpected scope/hash/domain change, absent evidence of original defect, failed required gate, unknown semantic contract or attempted guard weakening. After two ineffective corrections of same issue choose a new approach/specialist; don't retry unchanged.

## Provenance and Muhasabah

Sanad: requirements above cite authoritative Core and AM4; diagnosed failure names/types are direct outputs in ROBUSTNESS-READONLY-PROBES.json, not assumptions. Current R4 coverage is source-observed; malformed endpoint failures have not yet been reproduced and are a required Task1 test. Model partition production reachability is not asserted because upstream validation currently rejects invalid canonical rows. No source edits, tests/generator/CI runs or approval by this planner.

Muhasabah PASS for bounded proposal. Risks: stricter validation must not reject legitimate publicD/omittedEVSI; valid-response byte comparison and positive controls protect those. Assumptions: source remains unchanged until root delivery, existing numeric inputs are finite numeric types. All unverified paths/schema enhancements are explicitly open; precise required evidence precedes any closure claim.
