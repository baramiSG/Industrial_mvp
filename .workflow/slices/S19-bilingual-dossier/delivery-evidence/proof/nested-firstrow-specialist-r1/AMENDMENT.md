# S19 first-scalar print fragmentation amendment

PROPOSED, independently review before product transfer. This adds one bounded rule to proposal160b6b759aac2b0aec3d5748ba4fa3f94952926e480533f55d09972e69c39ffe and order addendum6440f14a; their bytes and failed keep-chain result remain history.

## Diagnosis and smallest correction

The existing heading/ancestor break-before/after chain does not constrain fragmentation *inside* its first scalar CSS Grid row. Actual failed foilPDF still has Scenario reconciliation on49 and StatusPASS on50. A controlled1759-file copy changed only this rule inside existing @media print:

```css
  .dossier-record .record-group > dd > .dossier-record > .record-scalar:first-child,
  .rule-record > .dossier-source-caption + .dossier-record > .record-scalar:first-child { break-inside: avoid; }
```

Retain the accepted keep-before chain, caption rule and prior BIDI/nested-dt rules. No whole record/section/table is made unbreakable; no forced pages, font, margin, spacing, content or HTML changes. Only `src/ior_mvp/static/css/dossier.css` needs a product delta. Its failed preimage is `ae7f466d7a3d4b3413ad4f48079f7f82298133668a77a4e5cca70e3d118bb2c7`; tested postimage `440b06e0a743deb8d44645fef6e4916b27a003946b926c69e4485b398d74b6ea`. All1758 other source files, including the strengthened existing test body, are byte-identical.

The measured A/B result supports internal first-row fragmentation as the remaining cause. This is an inference from controlled browser behavior, not a Blink-internals trace. CSS distinguishes inter-box breaks from internal fragmentation and identifies grid items as parallel fragmentation flows ([CSS Break3](https://www.w3.org/TR/css-break-3/#break-propagation), [Grid1 pagination](https://www.w3.org/TR/css-grid-1/#pagination)).

## Actual feasibility, not full-candidate approval

The unchanged four-target producer passed4/4 in18.39s, processexit0. Foil heading+StatusPASS now share50. The already reviewed successor checker bfa13f1a… and target wrapper2633dd54… ran unchanged:4PDFs/250pages/zeroissues, including all four ordered Arabic associations. Existing renderer80f17b6f… generated all250pages144dpi with zero physical glyph violations. Native views cover ten exact pages: foil49/50; PP32/33; profiles32/33/35/36; penicillin30/31. Both captions and all three nested headings stay with their first facts. Full lists/hashes are in FEASIBILITY.json. All4 emittedHTML differ solely by the exactCSS replacement; all available analysis/dossierJSON are byte-equal.

## Transfer and remaining gates

After independent reviewer APPROVE and root delegated acceptance, the product implementer transfers only this testedCSS delta, binds full1759-source equality to SOURCE.json (`ba5bec02c6912ad4e2dcafcba18f6746852bdbd66687fd784b6af86b380f2bdc`), and may reuse these identical target outputs by exact binding. Preserve current browser tests and checker successor unchanged. Complete already-required priorBIDI/q3 targets and88API equality with soleCSS substitution, then the final fullfunctional/44PDF strict/raster/manual gates. Use the SAME successor checker in final44 and both exactcandidate roots. Canonical sourcebinding must reflect actual finalCSS; no graph regeneration is required by thisCSS-only delta. All existing gates and stop conditions remain.

Sanad: direct controlledsource/producer/strict/native evidence; previous five originalRED checks remain attributed to preserved prior records. Personas after refreshed Task3/4, proposal and actual failure reads: paged-media fragmentation specialist and provenance auditor. Applied systematic-debugging, PDF, task-standards, Sanad, al-Muhasibi and Muhasabah.

Muhasabah: PASS for this bounded investigation/proposal. No self-approval, no production/index/service/generator/canonical changes. Full250page manual review, full44, priorclosure targets, finalcandidate/CI/delivery remain unverified here. Changed pagination can affect other reports; existing fullcohort review remains necessary.
