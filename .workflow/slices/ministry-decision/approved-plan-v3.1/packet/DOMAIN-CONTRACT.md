# Domain v3 — register evidence to a useful preliminary assessment

Proposed contract/amendment, not approval or implementation. Baseline is the isolated delivered S18b checkout `ce407db9832b61c5a8a85dfda2e3b7623da2fbc9`; S19 remains undelivered. Writes were limited to this note. No accepted calculations were repeated; no product tests, services, graph/Aura or source/index changes occurred.

**Preparation:** reread AGENTS/Manifest; direct governing DOCX §§4 R9-S,6,10,13; Core04/06/07/09/configs; original minutes; v2 packet's assessment, plan, contract, interaction and delivery; full Claude v2 review; viewed all five supplied screenshots. Then selected industrial evidence-method architect and process-capability analyst personas and read/applied task-standards, project-orientation, Sanad, al-muhasibi and Muhasabah. Coordinated register ownership/keys with `ux_api`; preparation reported to the coordinator.

## 1. Smallest defensible addition

Add **record-derived preliminary capability/gap findings**, alongside per-plant R9-S discovery and the retained finite line comparator. Each finding states what the record supports, what the requirement needs, the precise limitation, and the next useful action. Do not merely display customs rows beside authored distance states.

Existing R9-S accepts same-family plus one typed signal and no known failure (`src/ior_mvp/rules.py:1240`). Existing Test2 computes declared states, K and gated D* (`capability.py:47`); existing counterfactual q2 extracts states≥1, not missing equipment items (`simulation.py:641`). These are reusable but insufficient for the requested initial evidence-to-gap explanation.

Screenshots `sources/screenshots/line1654_img2.jpg` and `img5.jpg` show registry, production, factory customs and application datasets. They do **not** establish their detailed row schemas, production's firm-level grain, machinery ownership, operating envelopes or customer approvals. Screenshot counts describe the Ministry presentation, not this demonstration's records. The minutes P13–15/P21–26 require both prioritisation and specific actionable opportunities.

## 2. Proposed explicit DOCX amendment

Insert a short §6.0 before §6.1; add its control to §10.2 and reference it from R9-S. Proposed owner-review text:

> Before full Test2, a preliminary assessment may compare identified registry, production, customs, application and technical records with an explicit target requirement. Approved finite mapping rules may identify supported activity or process/input indicators, source-established limitations, and requirements not established within a named evidence boundary. Each conclusion records its subject, period, input facts, rule and field origin. Registration, procurement, exports and investment intentions do not by themselves establish installed, operating or target-qualified capacity. Absence from a record extract means not found within that extract, not physical absence.
>
> This preliminary vector is not a capability-distance estimate. It does not assign dimension states0–3, increase K, resolve final hard gates, publish D* or choose an intervention. Section6.4 remains unchanged. Useful preliminary conclusions and targeted records requests do not require an equipment inventory or site survey. Optional producer confirmation, technical records or survey may resolve specific remaining questions. Requests follow disclosed decision dependencies and available-record checks; no numeric accuracy or EVSI is implied.
>
> Under §10.2, every preliminary field identifies DIRECT_RECORD, REVIEWED_INFERENCE, ENGINEERING_DECLARATION or UNKNOWN origin separately from its evidence class. REVIEWED_INFERENCE requires an approved mapping-rule identity and exact source references; it never denotes automatic technical confirmation. A contradiction remains visible and blocks the affected claim. Preliminary conclusions cannot overwrite declared/confirmed Test2 evidence or either formal decision branch.

The finite rules below are the amendment's implementation table, frozen in `line_comparison.py`/the discovery module and Core mapping, **not a new config file**. This explicitly authorizes preliminary inference semantics under Manifest§7.4 (`docs/authority/00_AUTHORITY_MANIFEST.md:115`); it does not quietly reinterpret “verified present” (§6.4, direct DOCX P468–489). §13 already demonstrates useful preliminary route restrictions with D* withheld (P895–983). No new evidence→distance table is proposed.

## 3. Shared inputs and field origins

Use the agreed inline `synthetic_inputs.candidate_register` in both2.2 steel/PP scenarios, with identical canonical register content excluding the scenario envelope. Include all eight demonstration companies for both queries: five line controls, unrelated producer, importer-only firm and planned applicant. Do not pre-filter the input to expected winners. Stable entity-ID ordering is presentation, not ranking.

Use companion **DISCOVERY-GRAPH-CONTRACT** for canonical companies/plants/lines, coverage and attribution. Facts have exact `{fact_id,kind,dataset_kind,subject_type,subject_id,window,values,origin,source_refs,rule_id}`. Each field inherits that fact's origin; split mixed-origin facts. `rule_id` is required for REVIEWED_INFERENCE, otherwise null. Line assessments reference these facts without duplicated value ownership. Company→plant attribution requires a dated explicit record; company customs cannot fan out to every plant. Existing controls forbid creating a plant from a company name alone (`docs/core/04_CANONICAL_DATA_MODEL.md:172`).

* **DIRECT_RECORD:** literal value in the named register/source record, at its actual grain and date. In this demonstration, the record and field still remain ClassD/DEMO_GENERATOR; “direct” does not mean real Ministry evidence.
* **REVIEWED_INFERENCE:** a derived relationship/result from the finite approved rule table, with source field paths and rule identity. A reviewed rule is not confirmation of the particular factory.
* **ENGINEERING_DECLARATION:** explicit modeled/producer statement about an envelope, qualification, capacity factor, effort state or planned change; exact scope and source retained.
* **UNKNOWN:** no admissible value. Null stays distinct from zero, false and a negative declaration.

Public `analysis` omits both new synthetic result blocks. Simulated2.2 emits them; older simulated cases use typed unavailable with `NO_REGISTER`/`NO_LINE_RECORDS`. Existing public missing-fact content remains. Public evidence IDs may be cited by synthetic fields without importing their ClassC status. Validate ID membership in the associated public case/source artifact and reference exact fields/spans. Steel A is captioned “reference line reconciled to UNICOIL public marginals”; its simulated factors/effort/qualification/+50 remain ClassD. Preserve source conflicts (DOCX P901–903; `data/snapshots/public/SAU-H0-721049.json:148`), rather than treating public producer ranges as confirmed current performance.

Cross-case safeguard: the shared register contains explicit A engineering values, checked against the steel legacy reference; it cannot contain scenario-relative legacy pointers that would resolve to PP's aggregate in the PP copy. LegacyA pointer shortcuts exist only in steel's target-specific `candidate_lines`. Shared public pointers bind artifact identity/hash plus evidence ID from the explicitly allowlisted steel/PP public sources, preserving each source's subject; bare foreign IDs and arbitrary artifact paths are rejected.

## 4. Finite evidence→finding rules

`candidate_lines.requirement_items` contains explicit ClassD target requirements: item ID, dimension, required value/unit, applicable process/application scope and admitted record-field selectors. Legacy target leaves are read by pointer; only missing detail is added. No arbitrary expressions, model-generated process ontology, new HS crosswalk or fuzzy matching.

| Rule | Admissible evidence | Preliminary conclusion and boundary |
|---|---|---|
| P01 operating/family | Resolved Saudi plant plus operating-status/family records | Supports the recorded family only. Planned licence is prospective; company importer status alone is not plant operation. Existing governed family membership applies. |
| P02 own production | Positive, own-produced output with exact plant/product/window attribution | Supports recorded output family and historical production scale. Does not establish target-grade output, spare capacity, present utilisation or buyer acceptance. Aggregated HS production cannot be allocated to a company. |
| P03 input transaction | Revision-qualified exact customs identity in the requirement item's finite set: H6/HS2022 steel790111 or790112, PP290122; IMPORT, reexport=false, valid subject/window and explicit attribution for a plant signal. REGISTER §§1–2 binds six-digit types and field selectors; descriptions never match. | Supports a procurement/input signal. Does not prove consumption, batch purity, availability or an installed process. Company-only transactions remain useful company context and require an exact attribution link before plant use; never fan out to lines. |
| P04 machinery transaction | Raw customs plus an independently source-linked technical declaration, per REGISTER §§1–2: H6/847981 and same-transaction/model HOT_DIP_ZINC_COATING of STEEL_STRIP derives GALVANISING_EQUIPMENT; H6/847720 plus EXTRUSION/PLASTICS derives related PLASTICS_WORKING context only. Derived classification uses existing `reason_code` (`P04_GALVANISING_ACQUISITION` / `P04_PLASTICS_WORKING_CONTEXT`), exact operands stay in `current_recorded`, and origin is REVIEWED_INFERENCE/P04; no authored tag or new finding key. | Supports an equipment-acquisition signal only. Broad HS84/85, or generic8479, is not proof of a galvanising line. Installed/operating status remains unestablished. Four-digit headings are not hs6 values. PP plastics-working equipment does not prove resin polymerisation or receive that plant's R9-S equipment credit; missing/conflicting technical basis stays unestablished/conflicted. |
| P05 recorded process | Explicit process activity or a reviewed narrow output→process-family relationship | Supports that scope; identifies the required transformation stage still unestablished. A cold-rolling record does not establish hot-dip galvanising. Omission of galvanising is not proof it is absent. |
| P06 technical comparison | Current, same-line, same-requirement numeric/categorical technical declaration or admissible record | Retained comparator produces containment/membership result and exact shortfall, if calculable. Unknown/conflicting scope cannot pass. No millimetre shortfall→effort-state conversion. |
| P07 qualification | Matching certificate/customer/application/test scope and valid period | Supports only that scope. ISO management certification or exports cannot establish target customer approval. Explicit NOT_QUALIFIED identifies a limitation; missing approval is not a known failure. |
| P08 application/exports | Dated application/decision or export transaction | Application is declared intent; rejection reason is historical context; export is trade track record. None proves installation, success or target qualification. |
| P09 volume/window | Complete same-scope capacity factors/allocation and request window | Existing formula/comparator derives qualified-volume shortage or timing mismatch. Without those factors, capacity is not established; production/import volume is not substituted. |

No record yields a positive inferred status without admissible scope, identity and provenance. Conflicting current assertions produce CONFLICTED; historical facts remain useful historical indicators, not silently current facts. A single recorded failure on lineB does not declare every plant of its company incapable.

For per-plant R9-S, independently verified operating registry/family facts may use a distinct production fact as the extra `adjacent_output` signal. If production itself supplies the prerequisite, do not reuse that same assertion as its sole additional signal. This does not introduce a universal three-source requirement. Scope-matched known failure blocks the screen; unknown gates do not (`Core07:138`). SteelC's cold-rolled7209 output is RELATED_ONLY, not the configured coated-steel family7210 (`config/product_families.v1.yaml:7`). Do not widen that family to obtain a preferred result.

## 5. Derived output and useful initial answers

Each `candidate_discovery` record contains existing R9-S result plus `preliminary_assessment`:

```text
{entity_id, assessment_depth:REGISTER_ONLY|ENRICHED,
 findings:[{requirement_item_id,dimension,current_recorded,needed,
   status:SUPPORTED|LIMITATION_IDENTIFIED|NOT_ESTABLISHED|CONFLICTED,
   origin,rule_id,source_refs,temporal_scope,quantified_gap|null,
   reason_code,action_code}],
 evidence_boundary, next_evidence_actions}
```

SUPPORTED always names its scope, e.g. “input procurement signal supported”, never “capability verified” from an import. `NOT_FOUND_IN{dataset_kind,window,scope}` appears only after an actually supplied, searched extract. Missing/incomplete datasets instead say DATASET_UNAVAILABLE/COVERAGE_INCOMPLETE. Neither means physical absence. `current_recorded` and `needed` are operands, not narrative guesses. Derived findings are REVIEWED_INFERENCE; their input fields preserve their own origins.

Company-specific action statements are selected by finite rule precedence, not written by a language model:

* SteelA: operating galvanising and input records support an incumbent investigation; exact customer/qualified-volume coverage needs its source-bound line records. Optional records already supplied enable the retained line comparison. The reference upgrade/economics remain separately conditional.
* SteelB: register supports family activity; enriched width/customer records identify the exact current limitation. Action: verify the constrained width/application scope and evaluate a targeted remedy; never automatically recommend a new mill.
* SteelC: cold rolling is evidenced; galvanising/finishing is required but not established. Action: inspect existing licensed-activity/product/production records for that stage, then request a specific producer confirmation if unresolved. Do not infer “buy galvanising line” or state2/3 from no import row.
* PP lines: resin-family/output records support candidate discovery; MFR and qualification remain unestablished without detailed records. Optional matching-condition MFR records reveal the existing finite pass/failure. The legacy aggregate is not a third candidate.
* Importer-only/planned/unrelated entities remain visible with the exact reason they are not established operating same-family candidates; application rejection is not a capability rejection.

Coverage lists supported/limited/unestablished requirement items and named dataset boundaries. Do not call their count “accuracy”, K or percent readiness. This is an actionable initial answer without requiring a survey, even when numeric D* is unavailable.

Closed fixture matrix (authored demonstration inputs; optional details are not prerequisites):

| Entity | Register-only basis | Optional enrichment / required control |
|---|---|---|
| SteelA | Operating galvanising activity, own output, attributed input transactions | Existing reference factors/states unchanged; public-envelope pointers plus scoped ClassD qualification |
| SteelB | Operating galvanising, independent own-output/input signal | Width600–1100 against1000–1250; NOT_QUALIFIED, qualification share0/allocation0; own anonymous plant150kt design ceiling |
| SteelC | Operating coldroller7209; galvanising unestablished | Technical factors unknown; all nine effort statesU (K0/D*withheld), not v2's unsupported hot-dip0; own anonymous plant100kt design ceiling |
| PPA | Operating resin production and attributed input/output records | MFR8–24 versus12–20; independent modeled70kt allocation |
| PPB | Operating resin production and independent output/input records | MFR2–6 versus12–20; qualification share/allocation0 |
| Unrelated producer | Operating unrelated family | Not target-family; no false adjacency |
| Importer-only | Target imports; no evidenced producing plant | Buyer/procurement lead, not incumbent capability |
| Planned applicant | Under-establishment licence and application/rejection record | Prospective intent only; no current production inferred |

Existing target leaves remain unchanged; modeled request windows are steel[18,30), PP[0,12), with the detailed PP request56kt and MFR12–20 at the declared matching condition. B/C now have separate companies/plants, so no inherited shared-BC physical ceiling. This is a revised proposed fixture parameter, not a legacy-input change. C's all-U default replaces only the proposed v2C K=.30 expectation; it does not change any legacy reference. Engineering declarations may independently enrich it in explicit tests.

## 6. Evidence requests and shrunken line contract

Use non-numeric dependency order: (1) identity/scope conflicts; (2) exact target/application; (3) unresolved current process/specification/qualification constraint; (4) qualified allocation/window; (5) economics only for surviving alternatives. Within an unresolved item, inspect available registry/production/customs/application fields first; then request the particular producer sheet/certificate/customer record; a site survey is optional when these cannot settle the decisive question. Known technical failure calls for scoped remedy/alternative evidence, not an invented missing-data label.

Each request carries subject/item, existing need code, source dataset/action, missing field, reason and possible decision effect; `numeric_evsi=NOT_CALCULABLE`. This follows the existing renderer (`evidence_needs.py:197`) without claiming economic prioritisation. Do not add a need code: identity/operating/line-attribution requests reuse `line-level production or producer-grade matrix` with the exact missing field/action payload. Add the existing `qualification/profile hard gates` code to PRODUCER_CAPABILITY in the taxonomy (`executive/taxonomy.py:17`), with a focused mapping regression. All other requests reuse existing codes (`evidence_needs.py:14`). Keep candidate needs scenario-local; never feed them into public `build_dataset_unlocks`, which emits public-only aggregates.

Accept C6/C7 shrink: `candidate_lines` has `{reference_basis,requirements_additions,requirement_items,lines}`. Each line has `{line_id,reference_role,technical_fact_refs,capacity_ref,qualification_ref,window_ref,effort_ref,capacity_ceiling_ref,availability_basis,allocation_ref}`. References resolve the same register or finite allowlisted legacyA paths; nullable enrichments do not suppress discovery/preliminary output. Plant ownership comes from register; no separate plants/ceilings catalogues, comparison config, proposal/after-block or proposed-status engine. Legacy upgrade is displayed through its existing reference/counterfactual fields.

Closed types: `reference_basis={kind:LINE|AGGREGATE,line_id:string|null}`; steel uses canonical LINE-7315366f6a9166d8 with the separate legacy graph alias, PP has null and retains the separate legacy aggregate. `reference_role=REFERENCE_LINE|ALTERNATIVE`. A `ref` is an existing local fact ID or an exact allowlisted legacy JSON pointer, never a file/URL resolver. Only A admits `/synthetic_inputs/{plant_line,capability_states,equivalence}` refs. Technical refs map the fixed keys below to refs/null. Capacity records hold exactly the six legacy keys; qualification holds requirement/application scope, QUALIFIED/NOT_QUALIFIED/NOT_REQUIRED/UNKNOWN and validity window; effort has exactly nine configured dimensions; window is `[start,end)`. `capacity_ceiling_ref` names an ENGINEERING_DECLARATION fact whose `values` is exactly `{group_id,ceiling_kind:PUBLIC_NAMEPLATE|DECLARED_DESIGN,value_kt,basis}`; public evidence pointers belong only to its `source_refs`. Repeated groups must agree and reconcile line totals.

`requirement_items[]` has exact `{item_id,dimension,field_id,required_value_ref,record_selectors,basis}`. Selectors are enum pairs `(record_kind,value_field)` from P01–P09, not expressions. No unused reserved keys. `requirements_additions` also admits the finite `discovery_items` list specified in REGISTER-FIXTURE-AND-MAPPINGS; otherwise it admits only target fields absent from legacy: steel substrate/process/surface and request-window; PP polymer/grade/manufacturing-scope/MFR/test-condition/additive/tooling requirements and explicitly modeled detailed quantity/window. Referenced values carry origins/bases.

Fixed comparison fields: steel `substrate,process_route,thickness_mm,width_mm,coating_mass_g_m2,surface_treatment,standard,application`; PP `polymer_family,manufacturing_scope,grade_family,mfr_range_g_10min,mfr_test_condition,additives_required,tooling_required,application`; both qualified quantity, customer qualification and window. Equality/membership/full closed-range containment/window coverage only. Reject unknown keys/units, booleans-as-numbers, nonfinite values, inverted ranges, fractions outside[0,1], cross-subject facts and impossible allocations. All refs resolve before comparison. Missing enrichment is valid null, never an invented passing record.

Exact comparator mapping (register indicators alone never invoke it):

| Compared fields | Profile gate | Dimension masked U when UNKNOWN/CONFLICTED |
|---|---|---|
| Steel substrate | substrate_range | feedstock_chemistry |
| Steel width/thickness | width_thickness_envelope | equipment_envelope |
| Steel route/coating mass | coating_route_and_mass | core_process_route/finishing_spec_control respectively |
| Steel surface | surface_treatment | finishing_spec_control |
| Steel standard/application/customer qualification | mandatory_or_customer_standard | certification_customer_qualification |
| PP polymer/additives requirement | polymer_additive_compatibility | feedstock_chemistry |
| PP manufacturing scope/grade family | conversion_route | core_process_route |
| PP tooling requirement | tooling | equipment_envelope |
| PP MFR/condition | performance_requirement | finishing_spec_control |
| PP application/customer qualification | application_qualification | certification_customer_qualification |
| Either capacity/delivery window | None | capacity_time_window |

Gate aggregation: any NOT_MET→KNOWN_FAILURE; otherwise unknown/conflict→UNAVAILABLE; all required MET→RESOLVED; wholly justified non-applicability→NOT_APPLICABLE. Unknown/missing mapped fields never become state0. Other dimensions retain independently declared states/U; matching a field never manufactures a score.

Retain current finite comparison and declared-effort diagnostic. Pass reference `remaining` decision-specific gates unchanged as argument4 and record that inheritance (`simulation.py:173`). Exactly configured profile gates are admitted. F1 must support typed NOT_APPLICABLE directly, replacing the v2 RESOLVED adapter. Capacity/time unknowns mask only `capacity_time_window`; shortage is not process failure. Drop diagnostic `route_hint/control_message`. Half-open requested month windows span12 months; equality at endpoints covers the request. Preserve legacy declaration/reason `CURRENT_SHARE_MET_INCREMENTAL_PENDING` separately from current-share comparison; no string parsing. Candidate-only allocation≤formula validation must not retrofit ALU-PROFILES/PE-FILM (Claude C6g).

REGISTER-FIXTURE-AND-MAPPINGS is the normative closed selector/fixture/allocation supplement. It defines allocation facts and current qualified-supply admission; canonical A plant/line aliases; PP applicability rules; and exact scope checks. Its independent allocation is not encoded by altering a capacity factor.

## 7. Required fact-change acceptance

Tests must change facts and independently assert changed findings/actions:

1. Remove every optional line enrichment/effort record: discovery and differentiated company preliminary conclusions still run; final distance stays withheld, without a mandatory survey screen.
2. Add/remove an attributed input transaction and run REGISTER §5's B1 matrix: H6/790111↔790112 remains admitted for steel; steel790111→390210 or PP290122→790111 removes that procurement match and changes the scoped next-input request. H0 cannot match an H6 set; four-digit/missing/invalid HS identities fail strict validation. Description-only mutation changes no semantic finding/request/class/signal count (raw displayed text/provenance hashes may change). Flow/re-export/window/attribution negatives affect only their scope; never double-count imported_inputs/matching_feedstock. For optional P04, a correctly linked H6/847981 hot-dip declaration supports acquisition; wrong code/function/material/model/transaction/source/scope cannot. H6/847720 extrusion is context, not resin-process equipment. No installed-process claim, state0, K/D* increase, hard-gate resolution or formal/reference decision change. Classification uses exact typed source operands, not a renamed demo tag; full negative expectations and boundaries are normative in REGISTER §5.
3. Add a cold-rolling production record: related-output support changes; coated-steel R9-S remains unpassed. Add independently evidenced operating galvanising activity plus an additional signal: only that plant's screen changes.
4. Replace factory attribution with company-only customs, or aggregated production: no plant fan-out; scope-limited support/request changes.
5. Empty searched customs extract versus unavailable extract: NOT_FOUND_IN versus DATASET_UNAVAILABLE, never ABSENT. Duplicate transaction cannot create a second independent signal.
6. Change application planned→approved: intent context changes; installation/qualification do not. Change exports/unit value only: no grade or equipment inference.
7. Add optional exact envelope/customer/window records: findings improve or reveal mismatch. Cross-line, expired, wrong-application/conflicting records cannot pass. Test width max1100→1250 inclusively; PP maxMFR24→19; allocation70→55; zero versus unknown; equality at window boundaries. Independent qualification/capacity failures remain after repairing width alone.
8. Inferred support alone cannot populate Test2 states. Explicit engineering declaration may supply declared states, still guarded by actual comparison/unknowns and inherited gates. A pending remedy cannot resolve a current failure.
9. Mutate ground-truth expectations: runtime findings unchanged. Cross-scenario/foreign public references, orphan subjects and mismatched shared registers fail closed. Every new field remains ClassD with correct origin.
10. All11cases/bothbranches: real/reference decisions and accepted numbers unchanged; simulated-only additions absent from public outputs. Discovery never writes `domestic_capability`, reads graph-derived conclusions, or selects/copies economics.

**Sources/assumptions/limits:** exact code references above; direct DOCX paragraph numbers use one-based `w:p`; screenshots establish dataset descriptions only; Claude review C5–C7/§5 informed corrections. New mapping semantics, eight-company register, target items and detailed facts are proposed governed ClassD inputs, not actual Ministry records. Actual grain/attribution and future Arabic rendering remain unverified. No generic industrial design solver, numerical inference distance, producer ranking or automatic intervention is proposed.

**Muhasabah: PASS for this planning note.** Evidence-derived preliminary answers are substantive; evidence origins and uncertainty remain explicit; no absence/qualification/engineering-score inference is smuggled in; optional enrichment is genuinely optional. DOCX authority changes are identified, not approved. No implementation/test/live-verification claim is made.
