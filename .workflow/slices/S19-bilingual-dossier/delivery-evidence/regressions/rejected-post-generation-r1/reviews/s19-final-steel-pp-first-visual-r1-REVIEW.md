# Final steel / polypropylene and first-page visual review

Verdict: **REJECT** the assigned rendered cohort. Two concrete presentation findings remain. The unchanged strict checker reports 44 documents / 1,948 pages / zero geometry-content issues; that PASS does not resolve the visual findings.

## Preparation and actual coverage

Reused the governing authority/Core/control/owner preparation; refreshed accepted Task3/4/5 print requirements and the latest S19-only delivery-then-stop boundary. Persona: independent bilingual paged-media and rendered-product reviewer. Applied strict-reviewer, PDF, Sanad, al-Muhasibi and Muhasabah skills. No product, index, service, generation or GitHub write occurred.

Directly viewed all 68 bound contact sheets: 183 steel pages, 177 polypropylene pages, and all 44 first pages (404 page slots, 396 unique pages). No earlier view was silently reused. Six native-resolution views are listed in VIEWED-EVIDENCE.json, including the additional foil page requested by root. All contact/constituent hashes and all 44 renderer-input PDF hashes were directly rechecked. Contacts show uncropped pages at half native dimensions: layout coverage, not a claim that every small glyph was read at native scale. Initial contact setup assumed a `pp-` prefix and failed its page-count assertion before writing sheets; corrected discovery used actual `polypropylene-`. A final binding check initially resolved relative contact paths against cwd and stopped before writes; corrected directory resolution is explicitly recorded. Neither attempt changed source/evidence inputs.

## Findings

1. **BIDI-REF-01 — reason and source reference interleave in gap tables.** Native foil simulated AR11 and steel simulated AR13 visibly split a technical reason across an intervening evidence-link prefix, producing combinations such as `SYECONOMIC_ROUTE_EXISTS` and `SYN-OT_ESTABLISHED` while source strings remain intact. Frozen dossier.py:717/719 concatenates narrative or an inline reason bdi with inline reference anchors; isolation does not create separate reading lines. The accepted design requires readable complete technical IDs and safe wrapping. Root also bound profiles AR15; the other reviewer observed streptomycin AR11. Those observations remain attributed, not counted as my native views. Fix the two gap tables locally so the complete reason/narrative and each complete reference occupy separate wrapping blocks. Preserve bytes, hrefs, fonts and bounds. Scoped CSS is a proportionate candidate; prove actual Range/reference line separation and native PDF readability, retaining this RED cohort.

2. **NESTED-DT-01 — nested counterfactual heading detached from its first fact.** Native steel simulated EN24 ends with “Brownfield versus greenfield comparison”; EN25 begins with “Incremental capacity 50”. The nested `record-group > dt` is separated from its `dd` content. This violates the accepted no-orphan-heading requirement even though both pages contain other content. Print-only `break-after: avoid` on that term is the smallest candidate and keeps long records breakable. Measure its success on the actual PDF; if it fails to keep the term and first complete label/value together, report the failed candidate rather than silently escalating implementation.

No other distinct blocker was found in this assigned coverage. All 44 summaries fit their first page. Native steel public EN26 preserves the actual coating-range contradiction and public passport; PP simulated EN26 distinguishes minimum support 0 from unsupported NPV/IRR “Not calculable”, retaining the explanation and both simulation disclosures. Prior bounded section introductions and complete terminal records appear closed in this cohort; these observations do not erase the findings above.

## Evidence and disposition

CONTACT-SOURCES.json binds the 68 sheets and source PNGs. VIEWED-EVIDENCE.json binds actual views, six native images, the eight first-page sheets and two requested representative native pages. They may be retained as reviewed historical evidence, not an accepted corrected-final subset. Renderer/strict results remain valid historical checks for their exact PDF bytes.

The two-path CSS/test proposal is reviewed separately within this ongoing source review. Canonical capture and whole-candidate acceptance remain held pending corrected output and the already-required gates. No new framework or later-slice work is introduced.

Sanad: direct raster/contact/source/strict-record reads and SHA checks are distinguished from attributed root/specialist observations. Requirements: accepted experience design print section and implementation Task3/4 PDF gate. Assumptions: contact-scale coverage cannot establish every glyph's readability; the dt candidate is unverified until actual output. Risks: block-flow changes may repaginate reports; changed output needs actual review and unchanged output reuse requires exact PNG hashes. Unverified: corrected source, complete functional/final44 proof, canonical capture, exact-candidate/CI/delivery gates.

Muhasabah: **PASS for this review record**; product verdict **REJECT**. Actual findings are explicit, geometry PASS remains bounded, and no unviewed page or future gate is approved.
