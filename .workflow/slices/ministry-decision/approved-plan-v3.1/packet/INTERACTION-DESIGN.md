# Ministry decision journey — interaction contract v3.1

Proposed design, not implemented UI. Reuse the governed fonts, design tokens, cards, tables, drawers, graph controls and dossier renderer. Prefer a quiet ivory/ink workspace with a restrained green accent, strong typographic hierarchy and one persistent requirement strip. Status is text plus shape/icon, never colour alone. No decorative stock imagery or invented Ministry branding is needed. WIREFRAMES.html is an external, static bilingual review illustration; its values are proposed fixture views, not a running product.

## 1. Entry and sequence

Keep all eight `STEP_IDS`, direct step links, API enums and Back/Next order. Five question labels group monotonically:

| Question EN / AR | Existing steps | Main decision content |
|---|---|---|
| 1 · What must be supplied? / ما المطلوب توفيره؟ | SIGNAL, FALSE_POSITIVE_CONTROLS | Product/HS revision, application, explicit specification, demand, modeled window; real signal versus insufficiently detailed gap. |
| 2 · What is established publicly? / ماذا تثبت البيانات العامة؟ | PUBLIC_CONCLUSION | Public producers and limits, disputed facts, unchanged public outcome. |
| 3 · Which companies merit assessment? / ما الشركات التي تستحق التقييم؟ | MISSING_MINISTRY_FACTS, SIMULATED_EVIDENCE | Public needs first; simulated register discovery, factory/line details, comparison and next evidence when simulation is available. |
| 4 · Which route is justified? / ما المسار المبرر؟ | ROUTE_COMPARISON | Reference route ladder and current missing capabilities; candidate diagnostics remain distinct from selection. |
| 5 · What action and conditions? / ما الإجراء وشروطه؟ | INTERVENTION, CONDITIONS_AND_KILL | Conditional reference economics, evidence action, conditions/kill criteria and direct dossier. |

The screening bridge uses existing selected record ID/HS/revision/period and public CaseBrief joins. Exactly nine H6 links; preserve the mixed-H5/H6 warning in `likely_false_positive` and explain the H6 detailed scope. No fabricated H0 link. The `deep_assessment` added key contains public opportunity/brief references only, not the substring `scenario_id`; extend exact-key and leakage tests.

Q2 has a public producer box: UNICOIL published45–350 g/m² and250,000tpy, disputed range chip, Hadeed details unavailable. Caption: “Manufactures the family; target specification, qualified quantity and timing still require evidence.” / «يصنّع العائلة المنتجية؛ وتحتاج المواصفة المستهدفة والكمية المؤهلة والتوقيت إلى أدلة إضافية.» Public K=.75/three unknowns is the existing reference result, not a result assigned to each producer. The link to candidate discovery targets SIMULATED_EVIDENCE only if `decisions.simulated.availability` is available; omit for294110/294120/310430/310510.

## 2. Steel — discovery screen and interaction

```text
Steel sheet · HS 721049 / H0              Public | Ministry simulation
Need: Z275 · .7–1.5 mm · 1000–1250 mm · 104 kt · modeled months [18,30)
Demonstration · Simulated Ministry dataset                         Provenance
Which companies merit assessment?                  Searched register / periods
Company → Factory       Why it appears       What is supported / still needed
Steel A → plant A       Operating + output   Family/process supported; inspect line A
Steel B → plant B       Operating + output   Width/customer limitation; inspect line B
Steel C → plant C       Cold-rolled output   Related stage; galvanising not established
Other results (5)       PP / unrelated / importer / planned — exact exclusion/context
                         [Inspect company] [Why this result?]
Selected company A › plant A › line A
Current requirement | Recorded value / origin | Finding | Useful next evidence
Width 1000–1250      | 600–1300 / declaration  | MET     | referenced envelope
Qualified quantity  | 57.5092kt / P09 inference | SHORT | incremental qualification/allocation
                                   [Trace in graph] [Compare lines] [Open dossier]
```

No default “winner” row or best-fit sorting. Stable entity-ID order; filter results by factual status, never hide excluded controls without count/reason. Opening a company expands its factories, then known lines. Missing lines show “Line records not supplied” and the scoped next-record request. Removing optional enrichment keeps the company table useful. The display does not claim those companies are real factories.

Steel C illustrates the initial answer without inventory: “Cold-rolled output is recorded. Hot-dip galvanising and the required finishing/qualification are not established in these extracts. Check the licensed-activity and product/production records for this plant; if unresolved, obtain a process confirmation.” / «تُظهر السجلات إنتاجاً مدرفلاً على البارد. ولا تثبت هذه المستخرجات الجلفنة بالغمس الساخن والتشطيب والتأهيل المطلوبين. تُراجع سجلات النشاط المرخص والمنتجات والإنتاج لهذا المصنع، ثم يُطلب تأكيد العملية إذا بقي الأمر غير محسوم.» This is a rule-bound template with operands, not generated advice to buy equipment.

The reason drawer presents Target → record → P-rule → bounded conclusion → unresolved requirement → next evidence/action. Each input chip names origin, scope, period and source; full evidence labels are in accessible Details. The drawer distinguishes known mismatch, not found in supplied extract, unavailable dataset and conflicting facts. “Not established” never becomes “the company cannot produce.”

Every finding row and its drawer conclusion shows an origin badge from DOMAIN's closed vocabulary plus its P01–P09 rule ID. Each drawer step identifies the same assessment rule and preserves the displayed operand's own origin; a DIRECT_RECORD input does not acquire an inference origin merely because P03 uses it. The 57.5092 kt finding is **REVIEWED_INFERENCE · P09**, over separately identified ENGINEERING_DECLARATION capacity inputs; “calculation” is not an origin enum. Width's comparison is REVIEWED_INFERENCE · P06 over a declared envelope. Registry copy is “Registry asserts operating · Class D” / «يفيد السجل بأن المصنع يعمل · الفئة د», never confirmation that a real factory was verified.

**Required next-evidence element, every finding:** render four labelled slots from that finding's validated typed request/action: (1) **missing field** — existing `need.*` category label plus exact `missing_field`/`blocked_field` identifier; (2) **likely source dataset or confirmation action** — existing `executive.dataset.*` category plus the specifically named source dataset/record/field or confirmation action; (3) **affected decision** — the request's typed possible `route_effect`, without promising a route change; (4) **subject scope** — exact company and, only where attributed, plant/line IDs plus requirement item. Do not derive these slots from free-text prose or substitute a generic “more data needed”. The source is labelled likely, not a claim that the Ministry supplies that field. Company-only attribution requests name the company and missing factory link; they never display an invented factory/line.

Use one native `<details>` per finding for concise disclosure: its visible summary names the next field/action and subject; opening it exposes all four slots. The corresponding reason drawer exposes the same request at its next-action step; the selected-request rail shows all four slots without a second expansion. Changes of subject/locale update the whole request together. A supported finding with no remaining request uses typed `action_code=NO_ADDITIONAL_REQUEST`, renders missing-field/source-action as NOT_APPLICABLE, states that this finding has no pending evidence-driven decision change, and retains its exact scope. Other findings' unresolved requests remain visible; no fictitious missing fact is introduced to fill a slot.

The existing `evidence_needs.py:197–210` supplies `blocked_field`, `need_code` and `route_effect`; its effect text (`:23–44`) is currently English-only. The planned bilingual catalogue successor must render that existing finite effect meaning by need code, and the exact field/action labels where existing broad `need.*` keys are insufficient. Do not claim these Arabic keys already exist, expose English prose in Arabic, or introduce a new effect formula/EVSI number. Example for a company-only zinc transaction: **Field:** factory attribution link / «ربط السجل بالمصنع»; **Source/action:** factory customs allocation record or producer confirmation / «سجل تخصيص الجمارك للمصنع أو تأكيد المنتج»; **Decision effect:** establish whether this signal can support a named plant's incumbent assessment, not its capability / «تحديد ما إذا كانت هذه القرينة تدعم تقييم مصنع قائم محدد، دون إثبات قدرته»; **Scope:** the recorded company, plant/line not established / «الشركة المسجلة؛ المصنع وخط الإنتاج غير محددين». Render typed identifiers separately from localized labels. Optional surveys are never a prerequisite to the initial result.

## 3. Steel — comparison and intervention

```text
Compare recorded line capabilities                     Inspection, not a ranking
Requirement        A · reference       B · alternative       C · related potential
Target width       MET                1100 < 1250            Not established
Customer approval  Current share      NOT_QUALIFIED           Not established
Qualified supply   57.5092 / 104       0                       Not calculable
Current result     Capacity short     Requirement not met     Unresolved
Effort basis       Declared           Declared, show states    All U
Known coverage K   1                  Existing typed value     0
D*                 .2667             Withheld                Withheld
```

Use `executive.status.satisfied/not_satisfied` for MET/NOT_MET, with catalogue Arabic «متحقق/غير متحقق», not the illustrative wireframe's «مستوفٍ/غير مستوفٍ»; Arabic width heading «حدود عرض الخط» and inspect «ب · فحص». Render K through existing `capability.known` (English “Known coverage K”) and its existing capability legend, never bare K1/K0 or an accuracy percentage. Display “Declared effort to close (Class D, not derived)” / «جهد الإغلاق المصرّح به (فئة د، غير مشتق)» for a failed line; do not hide states behind a withheld D*. A successful comparison on current qualified share coexists with legacy finishing effort2 and pending incremental upgrade. The typed `CURRENT_SHARE_MET_INCREMENTAL_PENDING` reason links these scopes without parsing prose.

Q4 reuses `simulation_decision.counterfactual.q2_missing_capabilities` and `q3_brownfield_versus_greenfield`, route6/7 reason codes and `blocked_by_lower_route=5`. If greenfield is UNAVAILABLE, say so. No cheaper-than-greenfield claim without comparable cash flows. Selecting B/C changes the evidence focus only; reference route5 remains visibly reference A.

Q5 shows reference unsupported NPV −18 million SAR, support18, national value198, EVSI129.3 and competition ratio1.0751 only from existing typed fields. Policy-owned EN/AR context sentence:

> “Reference economics assume the planned 50 kt increment becomes qualified within 18 months. That condition is not yet established for the increment.”
>
> «تفترض اقتصاديات الحالة المرجعية تأهيل الزيادة المخططة البالغة 50 ألف طن خلال 18 شهراً. ولم يُثبت تحقق هذا الشرط للزيادة بعد.»

These numbers bind to legacy upgrade/counterfactual fields; use interpolated typed values rather than duplicated magic constants. No50kt is added to admitted current supply. Conditions cite the actual existing condition records; a planning label such as finishing stability is not invented as a new fulfilled condition. The next-evidence queue has no numeric EVSI unless the existing reference result supplies one. “Most useful next record” means the stated dependency order, not a statistical value-of-information model.

Comparison findings and the Q5 selected-request rail use the same four-slot contract in §2, including failed/unknown and supported/no-additional-request states. Concision permits native disclosure; it never permits omission of the missing field, likely source/action, possible decision effect or scope.

## 4. Polypropylene — full journey, not a steel reskin

```text
PP primary forms · HS390210/H0
Modeled detailed request: MFR12–20 at stated condition · 56kt · [0,12)
Legacy reference: aggregate1170kt, qualified allocation80kt; REJECT / route0
Discovery: resin companies PP A and PP B; other6 have explicit context/exclusion
                                  PP A                       PP B
MFR capability / same condition   8–24 → MET                  2–6 → NOT_MET
Declared allocation               70kt (independent input)    0
Request coverage                  14kt headroom              56kt short
Recommendation                    no new selected winner; preserve aggregate no-support result
[Why no generic capacity support?] [Show exact performance gap] [Open dossier]
```

Arabic headings: «المتطلب التفصيلي المُمثّل»; «معدل تدفق المصهور عند شرط الاختبار المحدد»; «الحالة المرجعية تجميعية وليست خط إنتاج واحداً»; «لا يُبرر دعم طاقة إنتاجية عامة». New MFR/demand/window/allocation are explicit Class-D assumptions, not inferred grade demand from HS or unit value. Do not turn resin production into a compounder demonstration without a separately reviewed scope. Mutating the MFR condition gives incomparable/unknown rather than numerical fit. The legacy80kt allocation is not reused as PP A70 or summed with physical candidates.

## 5. Graph, dossier and shared capability

Reuse adjacency. On “Trace in graph,” validate target/case/mode/locale/company/plant/line against the loaded typed response. Select corresponding permitted node or property scope and highlight the supported fact and bounded inference; the table alternative lists identical relationships/source refs. Graph layout does not invent a Company→Plant edge where the vocabulary has only parent properties. Candidate source, preliminary inference and declared Test2 calculation have distinct badges. Constraint→evidence detail and affected requirements remain navigable by keyboard.

Actual source conflict view: state both published coating ranges and the evidence IDs; show which claims inherit CONTRADICTED under the existing predicate. Explain that Z275 lies within both ranges, while confirmation of the disputed envelope remains needed. Do not convert a provenance conflict into a physical-failure verdict or suppress it because the count is high.

“Open dossier” / «افتح ملف القرار» uses existing `actions.open_dossier` and calls `dossierHtmlEndpoint(opportunity,mode,locale)` in a new tab. Preserve its Analyst return link and existing test. This increment admits new source keys explicitly in the S19 successor whitelist but does not add discovery/candidate blocks to dossier output; show “Dossier covers the reference case; candidate diagnostics remain in this workspace.” / «يغطي ملف القرار الحالة المرجعية؛ وتبقى تشخيصات المرشحين في مساحة العمل.» All22JSON/44HTML/44PDF proofs still apply. No unimplemented line anchor or arbitrary return URL is promised.

The existing aluminium shared-capability example is a separate case link: show declared dependency evidence and35.28m unlock value, route precedence and what that value means. It is not a claim that these new candidates share equipment. A shared-facility allocation or line-specific joint economics would need additional computation and remains excluded.

## 6. Disclosure and state contract

Policy1.5 adds the exact headline “Demonstration · Simulated Ministry dataset” / «عرض توضيحي · مجموعة بيانات وزارية مُحاكاة». It appears once per active simulated executive surface. Existing catalogue `graph.boundary_synthetic` remains “Synthetic Class D” / «اصطناعي من الفئة د» on compact fact groups. Full historical policy labels and raw metadata remain unchanged. Details are available before disclosure-dependent action, not hidden by hover.

The ruling amends the executive interpretation of Core01/03/06/09 and UX§8 “surface”/“prominently”: within the executive workspace a persistent headline plus group markers and expandable full provenance Details meets the obligation. Public MISSING_MINISTRY_FACTS has no synthetic headline. Standalone graph, graph passport, GenUI, dossier and print are **not** granted this exception; preserve browser_tests/test_graph.py warning assertion547/test556 and browser_tests/test_dossier.py101.

Read URL state before loading, then validate after the selected case payload arrives. Case changes clear foreign company/plant/line/requirement params; locale preserves only still-valid IDs. Add company/plant/line to cache identity; cancel/ignore stale fetches. Restoring an invalid ID falls back to an explicit “selection unavailable” state, not another company. Escape all labels/source text. Native details/table semantics and aria-expanded/controls/status must convey loading and selection once, without repeated announcement noise.

## 7. Concrete future UI oracles

Extend these **existing tests at ce407db**, preserving their current assertions. Reconcile paths/bodies against delivered S19 and admit actual extensions before generation; names below are not claims of already implemented candidate coverage:

| Existing test (under `browser_tests/`) | Required extension |
|---|---|
| `test_executive_accessibility.py::test_executive_steps_have_no_viewport_overflow` | Candidate rows, expanded requests and long EN/AR labels at390/1024/1440. |
| `test_executive_accessibility.py::test_executive_native_keyboard_and_technical_isolation` | Native Details, selected request, drawer focus/return, technical isolation and reduced motion. |
| `test_executive_accessibility.py::test_complete_arabic_executive_subtree_has_no_unmarked_english` | Expanded findings/requests, origin labels and exact catalogue terms. |
| `test_executive_states.py::test_unresolved_claim_names_actual_case_wide_needs` | Separate candidate-request fixture path and four-slot oracle below; preserve the existing case-wide R6 assertion. |
| `test_executive_races.py::test_delayed_locale_response_cannot_restore_previous_case` | Subject/request/locale changes cannot restore a foreign stale selection. |
| `test_graph.py::test_graph_keyboard_accessibility_rtl` | Selected producer/requirement/source navigation and equivalent table. |
| `test_dossier.py::test_dossier_print_media_and_pdf_are_valid` | Preserve reference dossier/print/disclosure proof and direct-entry context. |

**Four-slot DOM oracle:** in EN and AR, open each finding's Details, corresponding drawer and selected-request rail. Compare all four labelled values to independently authored typed-request expectations, scoped to that finding/request ID; text elsewhere cannot satisfy the assertion. Cover plant/line/company-only scope, unavailable source, known failure, supported/no-additional-request and no-enrichment states. Confirm origin + P-rule and input-origin separation. With valid data unchanged, remove each required rendered slot in turn and require the same completeness assertion to fail, then restore the valid rendering before the next omission. A collapsed control whose content is absent fails on opening. Preserve the current public/no-simulation negatives; an absent candidate request must never be filled from another company, public needs or generic prose. These are future tests in existing suites, not a new verification framework.

The following names remain **proposed new bodies**, not existing tests; independently admit their final names/parameters before generation. Withdraw the unbound 200% browser-zoom promise rather than treating deviceScaleFactor or pinch zoom as an equivalent. Responsive, keyboard/focus, RTL, reduced-motion and human-review requirements remain:

| Proposed test | Exact behavior |
|---|---|
| `test_executive_discovery_dynamic_company` | Added qualifying register company appears without candidate-list edit; inspect shows correct factory/line scope and record/rule. |
| `test_executive_preliminary_without_enrichment` | Strip optional facts in fixture; table still explains supported/unknown/action fields; no fabricated D*/survey prerequisite. |
| `test_executive_simulation_context_is_data_scoped` | Public needs has no synthetic headline; simulated step has one; full provenance and standalone warnings survive removal-negative controls. |
| `test_executive_candidate_locale_retains_valid_context` | EN↔AR keeps valid IDs; case change clears them; delayed old response cannot restore foreign selection. |
| `test_executive_candidate_arabic_copy_and_overflow` |390/1024/1440, long AR fixture labels, latn isolated technical strings, no clipped actionable text; catalogue terms and «مليون ريال». |
| `test_executive_candidate_keyboard_focus` |Full tab/focus path, native Details, table alternative, drawer open/close returns focus, existing aria-live="polite" settled-result behavior; reduced-motion no animation dependency. |
| `test_executive_reference_economics_condition` | Reference condition sentence source-equal in both locales; no alternative economics/winner on selection. |
| `test_executive_direct_dossier_preserves_analyst_return` | Correct endpoint/mode/locale/new tab; unchanged Analyst return; reference-only scope text and full print disclosures. |
| `test_graph_discovery_context_and_source` | Selected producer properties/links equal typed data; unavailable live graph remains unavailable; no phantom graph edges or synthetic public content. |

Use existing accessibility, state, graph and dossier suites; no new verification framework. Browser or screenshot success does not certify Arabic quality: require recorded bilingual reviewer sign-off and a Ministry-question walkthrough covering need, company, constraint, route, uncertainty and next action. No performance budget relaxation; extend existing five-warm-sample median<250ms checks to new projections.

Sources: ce407 executive labels/render/context/data, graph service/render/model, scenario/engine typed fields; Claude C8–C10 and source-bound records in companion contracts. All layout/copy is proposed. Real Ministry usability, rendered geometry and final Arabic sign-off are unverified. **Muhasabah: PASS for design specification only.**
