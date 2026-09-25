# S19 print-footer amendment R1 — independent review

**APPROVE.** The native page-margin footer is a bounded, demonstrated correction to the failed fixed body footer. No findings remain against this architecture amendment. Coordinator acceptance may authorize its integration and the required focused tests; this is not source readiness or candidate/PDF approval.

Subject: `planning/s19-print-footer-r1/AMENDMENT.md`, SHA256 `00d5c6d48c0bdcc4d9678c35aac3094713ba2e37b8c14d0d63c069ddcdae2ae7`; sealed manifest SHA256 `1b6e2bdf144344195eb1797cc377921dec93d9a977bae82a1c7d583f8cfff2a6`. Independent `EVIDENCE.json` SHA256 `cdbcec07b0854ddde00ac689a3294df3a4cc6d2f0dc3f7c62cc9a504d352e567`.

Reviewer `/root/s19_source_reviewer` is separate from author `/root/s19_delivered_base_handoff` and the product writer. Refreshed parent Task3/4, the approved design/PDF environment, bound renderer/CSS/tokens, actual failed fixed-footer records, prototype diff, producer/renderer and diagnostic. Adopted paged-media, CSS/HTML boundary security, bilingual typography and evidence-integrity reviewer roles. Reread and applied strict-reviewer, PDF, existing-design constraints from frontend-design-pro, verification-before-completion, Sanad, Al-Muhasibi and Muhasabah. Same-model delegated Codex review is not cross-model approval.

## Why the correction is appropriate

The old fixed child places its warning at the top of appendix pages and covers the heading. Direct old EN/AR page2 inspection confirms that failure. A native `@bottom-center` margin box places the disclosure in the reserved print margin without inserting an out-of-content fixed child. [Chrome's primary documentation](https://developer.chrome.com/blog/print-margins) describes this facility from Chrome131; the sealed producer records use actual Chromium151.0.7922.34. The empirical bound sample is the relevant feasibility evidence.

The exact diff changes only the3 already permitted production files. It keeps A4,14mm top/side margins and27mm bottom reserve; replaces the258mm position token with a5mm margin-box gap; raises only footer9pt→11.5pt; preserves body10.5ptEN/11.5ptAR, fonts, source content, projection and public decisions. Existing on-screen/section warnings remain. No PDF service, alternative browser, dependency, framework, generator, font reduction or content omission is authorized. Cleanup of the unused fixed-footer selector/interpolation is within the stated boundary.

## Escaping and isolation

Direct inspection traces footer labels to the existing validated policy pair. The prototype joins Arabic, one newline and English, then serializes every character as a terminated hexadecimal CSS escape inside one quoted string. It cannot introduce literal `<`, `>`, an internal quote, raw newline, CSS delimiter or closing-style tag. Decoding occurs within the CSS string rather than retokenizing decoded punctuation as stylesheet syntax.

I extracted and executed the exact serializer AST. An independent decoder recovered the exact policy pair/newline, plus hostile quote/backslash/newline/CR/formfeed/tab/closing-style/script/comment/import strings and Arabic/supplementary-character samples. Every encoded result matched the restricted escape grammar, and HTML parsing produced exactly one style element and no injected element. This is a direct boundary check, not a claim that unvalidated arbitrary strings are policy labels. Source tests for these cases remain required during integration as the amendment prescribes.

Only a present validated simulated disclosure appends the content rule. Public styles retain `content:none`; no policy wording is hardcoded into shared CSS. The patch removes the fixed body footer and does not introduce a scenario fetch or alter disclosure/projection interfaces. Public absence and unchanged screen/native export journeys remain explicit required regressions.

## Bound proof and independent measurements

All375 manifest entries rehash correctly. The r5 source ledger, all3 preimages, exact reconstructed diff, producer, renderer, wheel and PDFium binary match their recorded hashes. Local read-only image inspection returns the exact approved image ID. The sealed production command mounts r5 read-only with exactly3 read-only overlay replacements, and uses the actual `analyze → build_dossier → render_dossier_html` producer, fonts ready, A4 and print backgrounds. Network is disabled and sources/tools are read-only. The producer's inherited S18a scope string is stale descriptive text; the explicit command/source binding establishes this S19 prototype provenance and does not confer approval.

I independently re-read all8 actual old/new PDF byte streams using the same verified PDFium bytes. Page counts, English label boxes, footer text, footer-region status, physical glyph violations and body/footer gaps exactly reproduce the retained per-page observations. The same negative-control assertion was freshly executed for both cohorts: old exits1 at a real footer-region failure; new exits0.

| Steel sample | Pages, old = new | Old footer failures | New footer failures |
|---|---:|---:|---:|
| Public EN |28|0|0|
| Public AR |31|0|0|
| Simulated EN |52|52|0|
| Simulated AR |59|59|0|

All111 new simulated pages have exactly one English policy label in the footer and Arabic footer characters matching the policy. Exact source serialization and raster review complement that Arabic character comparison; sorted characters alone do not prove reading order. All59 public pages have no English warning anywhere and no Arabic footer. The new footer's maximum glyph top is60.3915pt within the0–76.5354pt reserved region. Minimum measured body/footer separation is21.6734ptEN and22.1110ptAR; physical-page glyph violations are zero. The records therefore establish the specific footer placement correction, not all body-region or content-completeness requirements.

The170 new page rasters/text hashes match the PDFs and render record:144dpi,1190×1684, no crop. I directly viewed new simulated EN1/EN2, AR1/AR2/AR59, public AR1, and old simulated EN2/AR2. New footer lines are readable and correctly shaped on those views, with visible separation and unobscured appendix headings. Only these8 named images were manually reviewed; all170 rasterizations are attributed to the sealed execution record.

## Scope, remaining gates and self-audit

The current writer's `dossier.py` has advanced beyond the frozen r5 preimage; both CSS preimages still match at review. This verdict binds the frozen amendment/prototype, not mutable writer source. Its ordinary integration and later paused-source review must bind the final bytes. No additional review process is introduced.

The amendment retains the full44-PDF matrix, complete source/text/font/section/ID/numeric/public-decision checks, full physical/content/footer bounds, missing-document/page rejection, old/out-of-page negatives, all prescribed raster review and page-count-quality assessment. The28/31/52/59-page prototype is not accepted as final document quality. Integrated hostile-string/public-isolation tests and all other source, browser, generation, canonical visual/pin/R1, two clean-root CI, hosted/exact-head and delivery gates remain required.

Sanad: direct fresh checks are the hashes/diff/image identity, serializer and HTML-boundary probes, PDF measurement reconstruction, negative assertion results and8 named raster views. Chromium production and raster execution are attributed to sealed command/result records; no fresh production, browser/service or rasterization ran here. Inference is limited to replacing body-positioning failure with the measured margin-box behavior; no internal Chromium fragmentation algorithm is asserted. Assumptions are the unchanged governed policy pair and pinned print environment. Other print engines, automatic browser print-dialog headers/footers, full Arabic reading order and final44-document quality are not certified by this sample.

Only this report and minimal external evidence were written. No product/index/service/canonical generated/GitHub writes or subagents. **Muhasabah: PASS** for this bounded architecture approval: facts are attributed, limitations explicit, existing acceptance standards preserved and no partial result promoted to product completion.
