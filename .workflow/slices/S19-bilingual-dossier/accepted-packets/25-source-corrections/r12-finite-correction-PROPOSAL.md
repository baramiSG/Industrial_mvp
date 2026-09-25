# S19 r12 finite rendered-product correction proposal

Status: proposed, product source paused pending independent concurrence and root acceptance. This corrects actual r11 review findings within accepted Tasks3/4. It does not authorize generation, canonical allocation, staging, commits or a new verification framework.

## Exact source boundary

- `src/ior_mvp/dossier.py`: existing renderer only; small consumed markup helpers within this file.
- `src/ior_mvp/static/css/dossier.css`: print-only `.dossier-intro { break-inside: avoid; }` for the bounded units below; retain existing rules unless the exact replaced markup makes a selector unnecessary, in which case leave it harmlessly unchanged for this correction.
- `config/ui_strings.v1.yaml`: only the existing generic `dossier.field.description` English/Arabic values, from Planned upgrade / التحديث المخطط to Description / الوصف. Same key, mapping, version and owner-bound effective date.
- `tests/test_dossier_projection.py`: finite renderer regression assertions for the corrected existing consumers and complete value preservation. No seven admitted browser-body edits, literal inventory changes, new browser function or checker change.

Validator specialist paths `dossier_validation.py` and `test_dossier_isolation.py` remain frozen. Documentation writer paths remain frozen. Projection/JSON schema, analysis/domain logic, public conclusions, all source values/IDs, footer architecture, font minima, page margins and strict0.01pt predicates remain unchanged.

## Source attribution: exact ten consumer groups

Reuse the existing governed `h.caption()` and existing language/direction isolates. Do not translate original evidence. Do not introduce a language classifier or captions for arbitrary technical identifiers. For fields, explicitly identify the affected supplied prose keys; for grouped records, put the existing caption beside the affected original-source record rather than beside localized UI prose. Empty/absent optional prose is not a reason to add a caption.

1. Identity available prose fields: `application_boundary`, simulated target `name` and `application`. Caption in those value cells; names, standards, HS and other technical tokens retain existing treatment.
2. Supply available selected upgrade `description`: caption in its value cell.
3. Coarse adjacency original record group, containing observed descriptions in steel/PP/profiles.
4. Capability hard-gate original record group (`profile_hard_gates`, `unresolved_hard_gates`, `known_hard_gate_failures`), including PP public named-imported-grade and buyer-application/qualification source phrases.
5. Counterfactual original record group containing the tinplate simulated `greenfield_alternative` sentence.
6. Buyer allocation original record group containing profiles simulated buyer-segment/basis prose.
7. Selected route-evidence/cash-flow original record group containing supplied `basis` sentences.
8. Competition original assessment record containing supplied `finding`/`note` prose.
9. Contradiction register original contradiction paragraphs, including steel coating-range prose independently of its passport copy.
10. Authority integrity original record containing simulated reconciliation detail/formula explanations.

Existing trade-quality/flow/supplier-metric/producer/economics/rule-metric/passport/EVSI captions stay intact. The finite assertions use the actual source values at these consumer paths and check caption adjacency plus unchanged prose and references.

## Bounded introduction markup

The existing generic `h3 { break-after: avoid }` does not reliably protect chains crossing wrappers. Use explicit small `<div class="dossier-intro">` units, containing real initial content, with the single print keep-together declaration above. Long table/record bodies remain outside these units.

- Route: place its existing h3, localized status and existing four-row feasibility table in one intro. Existing economics, precedence, competition, reasons and refs follow normally. No table splitting, row duplication or whole-route unbreakability.
- Rule: place existing h3, execution/fire status and first localized result paragraph in one intro; decision-effect paragraph and metrics follow normally. For the first synthetic rule only, include the existing simulated-ledger title and bilingual policy card in this same intro before its h3. Every rule and warning appears exactly once.
- Evidence: retain the complete `.contradiction-register` wrapper. Inside it, one intro contains the evidence-section h2, count, contradiction-register h3, public-contradiction h3/caption and the first actual public contradiction paragraph or truthful empty-state paragraph. Additional public paragraphs and the synthetic subsection follow inside the same register; passports remain outside the register as currently. The evidence section retains its ID and semantic h2 exactly once; its helper omits only the otherwise duplicate outer heading.
- Evidence boundary and Counterfactual: a local renderer helper emits the existing h3/caption plus the first complete definition-list dt/dd pair in one intro, then emits the remaining pairs using the ordinary existing record renderer. No string/DOM parsing, recursive restructuring or duplicate values. Actual22 outputs establish that integrity begins with boolean `real_decision_uses_public_only`; simulated counterfactual begins with boolean `q1_incumbent_meets_specification_without_capital`; public counterfactual is absent and its heading remains with the existing unavailable text. Do not wrap a long nested value if that assumption ever fails; the finite actual-source assertion guards this use.
- Selection provenance: move the exact existing selection ID/rule/profile/path paragraph beside authority metadata, before the long integrity group. No textual or ordering change within the source record itself.

## Targeted proof before the full matrix

Preserve r11 source/PDF/raster and actual failing page adjacencies. Retain assertions that demonstrate the old broken adjacency/final-only page against those exact outputs. Produce corrected PDFs using the existing pinned network-none browser recipe and approved renderer, and run the unchanged strict bounds/footer/font/public-content predicates. Inspect the corresponding corrected intro and end-page rasters before the full44 run.

Targeted reports: steel public EN (routes); steel simulated EN (evidence-count intro) and AR (Evidence boundary); PP simulated EN (ledger intro); fertilizer-retail-packs simulated AR (selection-only final page); penicillin simulated EN (ledger chain) and AR (selection tail); SOP simulated AR (Counterfactual heading) and public EN (selection-only final page). These nine cover all observed markup classes, including author findings. Caption/label source regressions cover the ten exact groups across actual22JSON/44HTML; relevant rendered Arabic pages are inspected. Then freeze the integrated candidate, regenerate the required44PDF/every-page rasters through the same proof recipe and repeat strict acceptance/necessary visual review. Old strict negative controls remain valid only while exact checker bytes remain unchanged.

Sanad: direct current renderer/CSS read; independent `reviews/s19-r11-steel-pp-rendered-r1/REVIEW.md` and `reviews/s19-r11-steel-visual-assessment-r1/REVIEW.md`; author `r11-author-visual/VIEWED.json` SHA459c367c1ff99bd3e6adde78e26ca182391a8ddbde370e79c1447b51ec84aa99 and binding SHA6314e69231fa5cd0aa03fb17c2aee3f8448d890051a74565c186b8bac1784273. Actual22 first-pair inspection independently corroborated by reviewer.

Muhasabah: evidence supports these finite defects and markup boundaries; implementation and corrected pagination remain unverified. Assumption: bounded first scalar/first narrative units remain short, checked against actual sources. Requirements preserve all evidence, decisions, typography and strict geometry. Risk: captions and wrappers alter downstream page breaks, so r11 geometry approval cannot transfer. Independent concurrence/root acceptance precede source writes; final independent source/product acceptance and all downstream generation/delivery gates remain pending.
