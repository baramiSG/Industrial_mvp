# Finite S19 nested-record and source-caption pagination correction

Status: PROPOSED for independent review and coordinator acceptance; production and tests remain frozen. Persona: bilingual paged-media/browser regression engineer. Skills actually applied: project-orientation, task-standards, systematic-debugging, verification-before-completion, Sanad, al-Muhasibi and Muhasabah; accepted Task3/4 and owner S19-only stop boundary refreshed. No new feature, schema, domain change, framework, dependency, harness or graph operation.

## Exact observed batch and cause

Frozen source ledger18180060d91ef4c91cb5152114bebe3fed2e9704370839703a9455b06694dbc2,1759 files. Current44 producer passed839 functional tests; strict44/1950 passed, but actual manual review rejects these five associations:

- NESTED-DT-02: polypropylene simulatedAR32 ends Quantity / «الكمية»;33 begins Recorded basis / «الأساس المسجل» = quantity. Source `blocks.ledger.records.rules[rule_id=R3].metrics.quantity.basis`.
- NESTED-DT-03: aluminium foil simulatedEN49 ends Scenario reconciliation;50 begins Status = PASS. Source `blocks.authority.records.integrity.scenario_reconciliation.status`.
- NESTED-DT-04: aluminium profiles simulatedAR32 ends National value / «القيمة الوطنية»;33 begins Displacement / «الإزاحة» =2. Source `evidence_pack.scenario_inputs.economics.data.national_value.displacement`.
- CAPTION-ORPHAN-01: penicillin simulatedAR30 ends the R1-D source-original caption;31 begins positive observed years2022,2023,2024.
- CAPTION-ORPHAN-02: profiles simulatedAR35 ends the same R1-D caption;36 begins its positive observed years2022,2023,2024. Both caption cases consume `blocks.ledger.records.rules[rule_id=R1-D].metrics.positive_years`.

Native reports and old files remain immutable. `DIAGNOSIS.json` SHA c1ba9766514694eea9a11d5d6be02ef8a6d8d367b4ec7d86b3254d21f3e8a420 binds actual PP pages32/33 and a stock pinned Chromium computed-style observation. Quantity dt already has break-after:avoid, while its dd, nested dl and first grid row have break-before:auto. The existing term constraint permits a break deeper inside the empty leading content boxes. Rule captions currently have no keep-with-next constraint, unlike passport captions. `FOIL-ORIGINAL-RED.json` records the actual English old-PDF heading/first-fact predicate failure.

## Exact production delta

Only `src/ior_mvp/static/css/dossier.css`, inside its existing @media print block, add:

```css
  .dossier-record .record-group > dd,
  .dossier-record .record-group > dd > .dossier-record,
  .dossier-record .record-group > dd > .dossier-record > :first-child,
  .rule-record > .dossier-source-caption + .dossier-record,
  .rule-record > .dossier-source-caption + .dossier-record > :first-child {
    break-before: avoid;
  }
  .rule-record > .dossier-source-caption { break-after: avoid; }
```

Retain the existing nested-dt break-after rule, BIDI block rules and all previous repairs. These constraints join only each introduction to the first actual row across the existing containers. No break-inside:avoid on a complete record/section/table; later rows remain breakable. Preserve fonts,14/27mm margins, spacing, source text, all IDs/links and content. CSS preimage d124607ce4466fad488678c33aacffd248b198f77d7a9b1097ccf39d9fc63b13.

## Exact source-test delta and honest Arabic proof

Only `browser_tests/test_dossier.py::test_dossier_print_media_and_pdf_are_valid`, preserving its full existing body/name/matrix and prior BIDI and steel-q3 checks. Test preimage2912d949c90395251180f1442fb486046686938a3150eb23f783d59eedcb0f97. Extend the existing evidence record with exact source-equal nested heading/first-row and rule-caption/first-metric DOM associations for the actual named targets. Resolve the R3/R1-D rules by actual rule_id, use governed locale catalogue labels, and compare first values against their exact source paths above; no hardcoded fabricated business value. Add a direct actual-PDF English Scenario reconciliation + Status/source-value same-page predicate alongside the existing steel-q3 predicate. Keep all original producer artifacts and assertions.

The stock pypdf Arabic extraction contains missing/NUL glyphs and presentation forms. Do not reverse text or call a geometry-only preceding-text surrogate an exact Arabic heading test. For the four Arabic associations, extend the already permitted external finite PDF acceptance in a new preserved successor copy of `O/check_pdf_matrix.py`, using its existing PDFium overlay and `label_present` character-multiplicity predicate. No dependency/source/harness change. The exact finite additions are:

1. In actual PP simulatedAR extracted pages, locate the unique complete Quantity heading line and require the complete Recorded basis + source value on that SAME page. In profiles simulatedAR, do the same for unique complete National value + Displacement/source value. Exact DOM/source equality is separately required above. No page-number hardcoding.
2. In the actual penicillin/profiles simulatedAR rule ledger text bounded by the unique ASCII rule tokens R1-D and following R2, associate the source-original caption and complete first positive-years row with their actual page indexes and require those indexes equal. This prevents an unrelated caption elsewhere on the first-metric page from satisfying the check. Strip only the known list bullet presentation character when comparing the first-row label and all source year values, retaining every data character and multiplicity. Preserve the record boundary tokens and actual page mapping in output.
3. Absence, duplicate/ambiguous target headings/records, missing full first field/value, or different pages fail. Existing all44 content/footers/bounds/fonts/public-narrative and raster predicates remain byte-identical. A small conditional block in the existing loop is sufficient; no generalized layout scanner or new test/harness name.

The external Arabic assertion supplements, and does not replace, mandatory native paired-page reading. This proof split is explicitly requested for independent concurrence; no unsupported claim that stock pypdf proves logical Arabic reading order.

## Execution and stop boundaries

First run the added finite predicates against preserved current PDFs/text to retain meaningful original RED for all five findings. The original Arabic target DOM source assertions must pass while the actual PDF association fails. Then apply only the approved two tracked paths and the bounded external checker successor; freeze and bind pre/postimages.

Use the stock producer first on the four reports containing the five defects: PP simulatedAR, penicillin simulatedAR, profiles simulatedAR, foil simulatedEN. Retain actual source/PDF/HTML/summary/layout outputs; run unchanged strict bounds/font/content proof plus added association checks,144dpi rasters and native old/new page inspection. If the keep-chain hypothesis fails, stop and report; do not stack speculative rules or start a full run. Once affected reports pass, retain/recheck steel simulatedEN plus foil/strep simulatedAR for existing q3/BIDI closures (profilesAR also covers BIDI). Send exact source/output bindings for independent implementation and output review before any fullfunctional operation.

Fresh preservation must prove all230 graph inputs, six generated outputs,44 protected indexes and unstaged source. No graph replay: neither CSS nor existing browser test is in the230 graph inputs. Actual22dossier +22analysis JSON and complete public decisions remain byte-identical;44HTML may change only by one exact old/new bound dossier-CSS substitution inside the sole embedded style, with every other byte equal, as already reviewed for the preceding CSS unit. Retain old/source API outputs and failed PDF cohorts. Rebind canonical preparation to actual final visual/source inputs before its still-unconsumed single capture; no capture allocated here.

After independent targeted closure, the coordinator may release the existing required fullfunctional/final44 proof on the exact frozen source. Reuse only explicitly hash-identical reviewed raster pages; inspect changed/new pages and preserve complete required first/longest/steel/PP/aluminium coverage. All strict tolerances remain0.01pt. Durable accepted PDFs wait actual final manual acceptance; no old cohort relabelling.

Sanad: accepted parent Tasks3/4, actual computed DOM and source preimages, retained fullfunctional/strict outputs, independent five actual native page findings and direct English old-PDF failure. Muhasabah: PASS proposal scope; CSS effectiveness and four Arabic same-page assertions remain unverified until review and actual RED/GREEN execution. No production modification, generator or canonical allocation is claimed or performed.
