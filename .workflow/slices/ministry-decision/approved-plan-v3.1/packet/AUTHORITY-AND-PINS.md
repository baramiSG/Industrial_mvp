# PLAN v3 — authority and delivery note

Planning only, 2026-09-25. `R/` = isolated ce407db checkout; `V2/` = retained v2 packet; `S/` = copied v1 S19 sources; `Review/` = full Claude v2 review, copied into v3 sources. Root reports remote main still ce407db and S19 undelivered; no network check by this agent.

## Actual preparation and evidence boundary

Read actual AGENTS/Manifest, relevant governing DOCX paragraphs directly via ZIP/XML (P63,143,265,401–508,832,847,903,939), original minutes, v2 plan/contract/design/delivery and review context; read the FULL Claude v2 review. Viewed all five v3 screenshot files with `view_image`. Then selected **governance/delivery architect** and **evidence-policy/bilingual-contract auditor**; read/invoked installed task-standards, sanad-provenance, al-muhasibi and muhasabah-gate. Later reads verified literal source/pin details. No tests, runtime engine probes, services, Aura, active S19 reads or mutations.

Screenshots establish displayed card claims, including registry counts, product-level production, named-firm customs and applications. They do not establish joins, line-level grain, access, current coverage or engineering envelopes. Screenshot2's “Nothing here is synthetic” describes the presented Ministry platform, never this demo's new fixtures. Minutes P13–15 distinguish prioritisation from technical definition; P26 requires repeatable decision support. Discovery now and Codex/Cascade/Claude roles are settled owner instructions, not open options. Record the seat mapping in repository owner-control records at actual-base reconciliation; preserve historical same-model Codex S19 reviews. Do not infer that AGENTS' old named seat text itself appointed Claude.

## 1. Authority ruling and smaller delivery structure

Recommend **S19 delivered → combined F1+F2 defect PR → one coherent M discovery/comparison/journey PR**. This expressly reverses v2's separate F1/F2 deliveries, following Claude C2/OD-A2's reversal of its earlier recommendation; it needs plan acceptance, not retrospective alteration of approvals. Each PR still has its own source closure, governed graph/manifests/canonical operation, exact-tree review, owner acceptance, hosted checks, merge and post-merge receipt. Combined defects save one closure, not any required proof.

Proposed ruling text:

> Authorize the bounded F1/F2 diagnostic corrections and their enumerated observable changes, preserving decision outcomes and scoped source records. For F, use the ADR010/011 §7.4 Core04/07 contract-correction precedent, with the governing DOCX unchanged during F and the observable delta enumerated. For M, apply §7.3 to scenario2.2, evidence-policy and UI-catalogue successors; apply §7.4 to the explicitly listed Core revisions and the narrowly specified preliminary-assessment DOCX amendment. Preserve §6.4 state meanings, formulas, Kmin/λ, hard gates, route order, public/synthetic isolation and accountable authorization. No registry/customs inference becomes an installed-capability fact, state0–3, K uplift or resolved hard gate. Resolve ADR-030's §7.2 conflict prospectively for this work; do not rewrite historical rulings.

Manifest§7.2 requires unchanged observable behavior (`R/docs/authority/00_AUTHORITY_MANIFEST.md:102`), so the defects' changed counts/statuses/endpoints cannot honestly be called pure refactors. ADR010/011 permits Core revisions under §7.4 with DOCX unchanged for unchanged methodology (`R/docs/ARCHITECTURE_DECISIONS.md:85,94`), but the proposed preliminary assessment is now an explicit **DOCX§6.0/§10.2 amendment** per domain design. Remove v2's blanket DOCX-unchanged promise. Before any code, approve exact wording, mirror update, Core02/04/05/06/07/09 mapping and source-to-output rules. Keep preliminary supported indicators/not-established/conflict/next-record-action distinct from Test2 capability states and EVSI. Survey/equipment inventory enrich the answer; they do not become prerequisites to preliminary discovery.

Retain §10 ambiguous-term and §8 unauthorized-hash-repair stops. Missing external Flight Control authority cannot be replaced with a new local framework; existing owner-directed roles must be recorded through existing controls.

## 2. C1/F1 — exact summary semantics and enumeration

Direct source confirms the mismatch (`capability.py:114–146`, `scenario_contract.py:957–966`) and decision-specific known-failure loss (`simulation.py:174–186`). The scenario classifier disagrees; it is not itself the duplicate's cause. H6 duplicate source lists are required by `cases/brief.py:650–675` and projected at `cases/projection.py:598–601`; retain both scoped lists and provenance, deduplicate only summary identifiers.

Use one finite classifier, case-folded **prefix** grammar: `resolved`, `known failure`/`known_failure`, `not applicable`/`not_applicable`; otherwise UNAVAILABLE. Canonical enums are RESOLVED, KNOWN_FAILURE, NOT_APPLICABLE, UNAVAILABLE. Preserve raw text. Typed decision-specific statuses must survive into capability and graph projection; known failure is not an unknown. Dict NOT_APPLICABLE must behave like either accepted non-applicable string: no unresolved-profile entry and no publication block. Preserve the enum/basis instead of relabeling to RESOLVED in the candidate adapter. Do **not** widen public snapshot/CaseBrief schema: `public_snapshot.py:1403–1408,2155–2172` and `cases/brief.py:660` continue rejecting NOT_APPLICABLE there.

Proposed independently authored ordered-list oracle (static source reading, **not a fresh engine run**):

```text
S=[substrate_range,width_thickness_envelope,coating_route_and_mass,surface_treatment,mandatory_or_customer_standard]
P=[polymer_additive_compatibility,conversion_route,tooling,performance_requirement,application_qualification]
F=[feedstock_route,formulation_granulation,nutrient_basis,agronomic_performance,emissions_and_safe_handling]
A=[alloy,forming_fabrication,heat_treatment,joining_finishing,engineering_certification,customer_liability]
H=[named_molecule_and_synthesis_route,gmp,containment,impurity_control,analytical_validation,effluent,ip_fto]
S0=S+["exact imported specification","customer/application qualification","effective spare capacity and allocation"]
P0=P+["named imported grade","buyer application and qualification","local grade availability in required volume and timing"]
```

| Opportunity | Public old→new summary count; new exact list | Simulated new unresolved list |
|---|---|---|
| SAU-H0-721049 | 8→8; S0 | [] |
| SAU-H0-390210 | 8→8; P0 | [] |
| SAU-H6-294110 | 14→7; H | [] |
| SAU-H6-294120 | 14→7; H | [] |
| SAU-H6-310430 | 10→5; F | [] |
| SAU-H6-310510 | 10→5; F | [] |
| SAU-H6-392010 | 10→5; P | [] |
| SAU-H6-721012 | 10→5; S | [] |
| SAU-H6-721061 | 10→5; S | [] |
| SAU-H6-760429 | 12→6; A | [] |
| SAU-H6-760711 | 12→6; A | [] |

Streptomycin simulated changes from two unknown effluent entries to **known_hard_gate_failures=[effluent]**, retaining profile and decision-specific sources; other simulated known-failure lists remain empty. Source literals: `config/sector_profiles.v1.yaml`, each public snapshot's `/domestic_capability/unresolved_hard_gates`, and each current scenario's `/synthetic_inputs/{hard_gates,decision_specific_hard_gates}`. Claude C1 supplies independently reproduced prior counts; this note confirms input literals, not its runtime results.

Extend `tests/test_s17_generation.py:64–90` with the 22 expected lists, public/real equality, branch-correct active_decision and all existing state/route expectations. Executive EXECUTION_FEASIBILITY count changes accordingly (294120 public14→7); do not claim all public response bytes unchanged. Focused RED/negative coverage belongs in existing capability/scenario/graph tests: reciprocal spelling, case/prefix, typed non-applicability, known failure versus unknown, duplicate scoped references, no arbitrary prose pass. Old public validators and both scoped source lists must remain intact.

## 3. C2/F2 — finite semantic and pin changes

Fix `R/src/ior_mvp/graph/derived.py:294–335` only as designed: broad needs target Product; genuine specific targets require validated references. Tests: `test_graph_projection.py`, `test_graph_engine_feed.py`, `test_graph_service_offline.py`, `test_graph_api_offline.py` with nonempty needs, multiple sorted capabilities and exact reference preservation. Assert no Decision→Capability CONSTRAINED_BY edge for these governed broad-need fixtures.

Claude C2's **reused F2-only ce407 in-memory result**:925/1045 unchanged; Decision→Capability42→0 (26 supply+16 hard-gate); Decision→Product30→72; capacity-time-window disappears from evidence_to_change in22 branches. Simulated view edge counts: steel14→15, PP13→16, profiles12→14; other view edge counts unchanged. Revalidate combined F1/F2's complete semantic diff independently; don't present F2-only results as a combined final artifact.

Explicit pin permissions:

- `browser_tests/graph_pages.py:406–421`: only affected steel public/simulated evidence_to_change **edge** PASSPORT_SOURCE_COUNTS, currently7/9. New span counts require AM4 independent rendered/raw enumeration; **no guessed successors**.
- `browser_tests/test_graph.py:845,867`: new engine token; second row's target becomes Product `SAU-H0-721049`. Preserve remaining source-equal row/geometry and original-CSS negative controls; revised endpoint oracle is accepted before capture, not reported as old R1 equality.
- `tests/test_s17_generation.py:55–59`: keep925/1045 for F2; exact combined proof required. C2's snapshot726→728 is ce407-only. After delivered S19, bind actual count N and enumerate the one preserved graph generation's additions (normally N+2), never transplant728 blindly. Mirror actual membership in `test_integrity_contract.py:1298`, `test_s17_status_docs.py:33`.
- New `data/graph/current.json`, write-once projection artifacts, snapshot manifest, baseline manifest `source_tree`/source hashes/change_ref and baseline subtree OID. Public/synthetic/golden roots remain frozen for defect PR. F2-only authority bytes/count20 are unchanged; combined F1 Core/control amendments may change authority hash **values**, so bind them explicitly instead of repeating “untouched”.

## 4. C3 — literal successor addendum for no fifth view

Conditional on delivered S19's128 images/51 modules, add exactly three **non-graph** scene stems:
`journey-k-executive-candidate-lines-steel`, `journey-k-executive-candidate-lines-polypropylene`, `journey-k-executive-candidate-discovery`. Each EN/AR × desktop1440×900/tablet1024×768 =4. M=140=124non-graph+16graph. No new viewport, graph view or `graph_views.v1.yaml` version. Budget remains600KiB/image and16MiB aggregate; measured failure stops.

| Literal/contract | Delivered-S19 expectation → M | Future S20, separately authorized |
|---|---|---|
| UI config guard/error, catalogue/endpoint/authority/graph-fixture adapter | 1.7.0→1.8.0 | 1.8.0→1.9.0 |
| `browser_tests/test_graph.py:74/75/76` fresh/graph/retained | 16/16/112→16/16/124 | 16/16/124→16/16/140 |
| `GRAPH_REPLACEMENT_SCREENS:51–56` | same four literal stems | same four |
| `tests/test_visual_baseline_contract.py:34–66` and capture SCREENS |32→35 stems; append three above |35→39; four approved extraction states; literal stems still require admission |
| `test_visual_baseline_contract.py:121,186`; `test_s17_status_docs.py:34`; frozen `VISUAL_BASELINE_ENTRIES:57` |128→140 |140→156 |
| frozen baselines subtree OID `:48` | exact reviewed generated successor | exact reviewed successor |
| `test_es_modules.py:13` exact set |51→54; append modules/executive/resolution.js, modules/executive/candidates.js, modules/graph/context.js | retain54; no additional S20 module |
| browser file/name inventory | preserve actual S19 set; add candidate_pages.py and extend existing tests. Conditional file count27→28; admit actual new test bodies/names | inherited set + extraction_pages.py/test_extraction.py: conditional28→30 files; actual names independently admitted |

Choose resolution.js for discovery/context/next-fact composition, candidates.js for line comparison/detail, graph/context.js for validated request/cache context. Each≤199 physical lines. No third executive module now; if meaningful implementation cannot fit, stop for named-module amendment, never compress unreadably or silently change54. New executive DTOs live in `executive/line_models.py`; existing modules remain≤500 where governed (AM1:79), not expanded beyond cap. Use the explicitly admitted browser_tests/candidate_pages.py for the three new scene fixtures, preserving all existing helpers. This is one helper admission, not a new verification framework.

S20 plan/design specify summary, selected supported record, contradiction/unresolved and empty states, but the inspected copies contain no literal journey stem names (`V2/../sources/s20/S20-EXPERIENCE-DESIGN.md:42`, plan:149). Do not manufacture those four names now; bind them through its exact future inventory admission.

Map additive successor ruling to old amendment lines25,28,38–44,99–101,130–138: retain old bytes; replace prospective version/count clauses only. S20's “no edit” ES clause becomes inherit54 rather than51; graph permission is124→140 retained, not112→128. M pre-generation inherited count112 versus planned124 can be classified only under the exact accepted pending-predicate process; final140 must pass unchanged gates. S20 pre-generation is124 versus planned140; provisional matrix140, final156. No skipped/phase-aware fixture or resource waiver. S19 browser later amendment27files/83names supersedes earlier26; no invented new named-test total. Preserve historical S17 counts/ID and frozen UI1.3 adapter inputs/two-field-only version delta.

## 5. C5/C7/C8/C9 — provenance, policy and entry contract

Recommend Line A Class-D facts citing public IDs `S-UNICOIL-SPEC` and `S-UNICOIL-EPD` by pointer, with exact fact scope. Envelope/nameplate reconcile to public marginals; availability/yield/.38 qualification/allocation/effort/+50 remain simulated, not observed UNICOIL facts. All five manufacturer assignments stay null. Scope references independently: a public pointer does not promote the synthetic assertion. Every candidate capacity/effort container carries the Class-D marker. Remove blanket “all anonymous”/“public anchors substantiate no envelope” wording.

Accept C7 shrink: no proposal/after block, no line_comparison config; finite reviewed mapping in line_comparison.py, target leaves by validated pointer, per-line ceilings/parent fields. Existing legacy upgrade/economics remain explicitly conditional. New register/discovery keys must be named in2.2; no unused reserved keys. Retain the policy-owned bilingual economics-basis sentence requested by C9(b): reference route5 economics/competition ratio assume the planned50kt becomes qualified within18months, a pending condition rather than an observed result. Bind it wherever those economics appear beside a candidate whose incremental qualified supply is unestablished, with a DOM omission-negative test. Requirement/preliminary mapping needs its exact domain-authority home, not a hidden policy threshold.

**Keep bounded consolidation**, responding to repeated-warning concern. Policy1.5 owns the concise bilingual headline; reuse catalogue `graph.boundary_synthetic` **unchanged in both locales** (“Synthetic Class D” / “اصطناعي من الفئة د”, ui_strings:678/1419). Do not duplicate the compact marker in policy or reorder just its English. Preserve raw full labels and `synthetic_display_labels()` `{en,ar}` shape. New validated policy-headline resolver/UI-bundle field requires exact shape/missing-locale negatives, `evidence.py:136`, `config.py:188,244`, i18n.js:93, `test_synthetic_isolation.py:112ff` version/date, `test_ui_catalogue.py:585,643`. Strengthen policy nonduplication to cover headline without banning the existing compact catalogue label.

Headline is **data-scoped**, shown only when active executive content contains simulated groups, not all Q3 steps. Q2 simulated comparison link targets SIMULATED_EVIDENCE and is absent when simulated availability is UNAVAILABLE. Full warnings stay in accessible provenance Details, independent graph/elements/passports, GenUI, on-screen dossier and every simulated PDF page. No new graph-surface exception is needed. Amend Core01/03/06/09 executive placement and UX§8 (including stale1.2 policy reference); preserve `browser_tests/test_graph.py:547` warning assertion and `:556` test, removal control, and `browser_tests/test_dossier.py:101`.

Direct dossier is an explicit new executive link via existing `dossierHtmlEndpoint(id,mode,locale)`. Preserve S19 Analyst return link/test unchanged; open a new tab retaining executive state. Do not add arbitrary return URL or promise new executive return/line anchor. New candidate/register fields may be admitted-but-not-projected in S19 successor whitelist, explicitly listed as excluded; report dossier scope honestly. Full22JSON/44HTML/44PDF isolation/print proof remains.

Named proposed browser oracles, admitted only after real bodies exist: `test_executive_simulation_context_is_data_scoped`, `test_executive_direct_dossier_preserves_analyst_return`, `test_executive_candidate_locale_retains_valid_context`, `test_executive_candidate_arabic_copy_and_overflow`. Cover EN/AR390/1024/1440, latn IDs/ranges, catalogue MET/NOT_MET/INVESTIGATE terms, actual source-equal text and zero/unknown. Either add concrete zoom/delay/aria-live checks to existing accessibility/state tests or remove those promises. Record bilingual human sign-off separately; no screenshot or automatic parity test alone certifies Arabic quality.

## 6. C10 — bounded future Aura proof

Use existing operator target resolution/load/verify only (`Makefile:307–324`, `graph/loader.py:135,287,480`). No `graph_tests.loaded_graph` on Aura: that fixture clears. First bind final projection/target and inspect identity/counts/provenance/partition. Same projection verifies; empty authorized target loads; different projection stops for an exact replacement/rollback ruling. Never infer clearing authority from planning acceptance. Repeat authorized load must create0 nodes/relationships.

One bounded read-only operator step then calls existing `loader.execute_view():582` for the **four existing** views and fixed case/branch matrix, comparing normalized rows to the accepted artifact equivalents used by `graph_tests/test_views_equal_artifact.py:40–105`, without importing its fixtures. Bind per-producer adjacency oracle to the reviewed scope correction; don't compare new producer-specific facts to old opportunity-wide broadcasts. Preserve source/branch IDs and no synthetic public rows. Reuse existing serializer/DTO assertions for record detail; no fifth-view procedure or unrestricted query API. Traverse actual EN/AR app graph→passport→dossier; simulate unavailable through isolated app configuration, never Aura mutation. Sanitized receipts bind final artifact and target, not credentials. Local/mock success never substitutes for live acceptance.

## Planning allowance, not measured duration

Budget one combined defect closure instead of two: estimated1–1.5 person-days for RED/fixes/source review plus1.5–2.5 for the relevant graph/manifest/canonical gates and one correction round. M's final artifact/browser/PDF closure should reserve4–6 days after source readiness, plus0.5–1 for bilingual review and0.5–1 for authorized Aura proof. Add actual-base/ruling preparation and domain/UI/discovery implementation estimates separately; avoid double-counting a second capture cycle already inside a task. Assume one accepted source-final generation operation and one review-correction allowance; an unexpected source change requires an explicit rebinding/correction operation, not unlimited refreshes. Owner/reviewer response waits are calendar dependencies, not implementation days. These are task-based estimates, not measured repository throughput or a claim about S18b's hours.

## Sources, assumptions, limits and self-audit

Direct: cited clone source/config/data/tests, direct DOCX, minutes and five screenshots; copied v2 contracts/S19 successor; full Claude review. Reused and attributed: Claude's runtime counts/F2 rebuild; root's remote/S19 status. Proposed:22-list oracle, combined closure,54 modules,140/156 matrix, wording and future tests. Actual S19 bytes, new passport spans, resource fit, Arabic sign-off, final graph counts/hashes and live Aura remain unverified. Discovery intent/roles/direct dossier are settled; exact methodology/fixture/provenance/disclosure ruling, combined-defect/successor amendment and conditional Aura replacement await concrete acceptance. No permission question is repeated here.

Muhasabah PASS for planning support: removed fifth-view arithmetic, policy-marker duplication, false implementation-preserving classification and owner-approval inflation; runtime evidence is attributed; no claimed execution or independent approval. Only this v3 notes file was written.
