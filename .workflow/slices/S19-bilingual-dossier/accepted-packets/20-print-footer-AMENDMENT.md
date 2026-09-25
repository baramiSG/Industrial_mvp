# S19 print-footer amendment R1

Status: PROPOSED; independent plan review and recorded delegated acceptance required before product adoption. This is the Task3.5 print-architecture stop resolution, not implementation approval.

## Authority and preparation

Preserve parent S19 plan SHA-256 `7749006ae850adf66fea862934c8362d9ea5c9254aaf74ded702504e69ce44d1`, design `db03f9330e75f1e857dfcc0493fbad792321a2f522e4498ed610d30b6dfdead1`, PDF environment `e8cb88f443acff3262876bbfa6c121458151877a3a8add6e7a9ba489b5162eeb`, and all accepted amendments byte-for-byte. This additive amendment changes only placement of the already required repeating simulated print disclosure.

After the prior full governing reads, refreshed Task3/4, the design/PDF environment, current dossier renderer/CSS/tokens and actual failed r4 artifacts. Adopted a paged-media/PDF engineer persona to diagnose coordinate placement and preserve Arabic typography and evidence boundaries. Applied systematic-debugging, writing-plans, PDF, existing-design constraints from frontend-design-pro, project-orientation/task-standards/github-flow, Sanad, al-Muhasibi and Muhasabah. No installation or broad feasibility investigation repeated.

## Measured defect and different approach

The r5 frozen source used for r4 prints a body child with `position:fixed; inset-block-start:258mm` while A4 margins reserve a 256mm content height. Direct inspection of old EN pages1/2 and AR page2 confirms no reserved-margin disclosure on page1 and a repeated disclosure overlapping the appendix heading near the top of page2. The old EN page2 warning occupies PDF y=773.58–780.20pt, not the bottom margin. Its exact Chromium fragmentation algorithm is not established; a modulo-content-height explanation remains an inference. The established defect is using a body fixed-position box outside the print content area to implement page-margin content. The preceding negative-bottom experiment also failed and remains retained.

Use native `@page { @bottom-center { ... } }` generated content, with no fixed body disclosure. Chrome documents support from version131; this packet tests the actual pinned Chromium151.0.7922.34, rather than assuming portability: https://developer.chrome.com/blog/print-margins . No server PDF service, JavaScript pagination, dependency, browser replacement or general verification framework.

## Exact permitted production changes

All paths below are already allowed by the parent plan; no new product path is added. `INPUT-BINDING.json`, `preimages/` and `PROTOTYPE.patch` bind the three old source files and the tested overlay. The implementation may use normal project formatting and remove the now-unused `.print-disclosure` selector/interpolation; it must preserve this behavior.

1. `src/ior_mvp/dossier.py`: replace only the fixed-footer assembly/insertion with simulated-only print CSS generated from the already validated `labels['ar']` and `labels['en']`, joined by one newline. Add a small private CSS-string serializer here: encode each Unicode scalar as a CSS hexadecimal escape followed by a terminating space and wrap the sequence in double quotes. This prevents quote, backslash, newline and `</style>` termination; do not use HTML escaping as CSS escaping. Keep both exact policy strings; do not duplicate their wording, introduce a catalogue key or retranslate them. Public output emits no policy content rule, and the fixed disclosure body element is absent. Existing on-screen and section disclosures remain. Render/build interfaces, validation, data projection and public decision are unchanged.
2. `src/ior_mvp/static/css/dossier.css`: within the existing print `@page`, add `@bottom-center` with default `content:none`, `white-space:pre`, existing Arabic font family, medium weight, existing Arabic print line height, navy text, `direction:rtl; unicode-bidi:plaintext`, top vertical alignment and the footer-gap token. Retain A4, 14mm top/side margins and 27mm bottom margin. Remove the fixed-position disclosure rule. The simulated-only later rule sets the escaped content. No other layout change is authorized by this amendment.
3. `src/ior_mvp/static/css/tokens.css`: replace unused footer-top258mm with footer-gap5mm; raise footer font9pt to11.5pt so both lines meet the larger existing Arabic minimum. Preserve body10.5ptEN/11.5ptAR and all other tokens/content. A page-count reduction is not a reason to reduce fonts or omit data.
4. Existing allowed `tests/test_dossier_contract.py`/`tests/test_dossier_isolation.py` and dossier browser/PDF tests: add focused assertions below without removing inherited checks. No Makefile, CI, checker, generator or new tooling dependency change.

The bottom27mm is the footer region (PDF bottom-origin y=0–76.5354pt). Body content remains within the existing content region; footer glyphs must be entirely within the reserved region with positive measured separation, not merely inside the physical page. The prototype's footer top is60.3916pt. Automatic browser headers/footers remain disabled in the existing controlled Chromium PDF invocation; other print engines are not certified by this proof.

## Required tests and unchanged acceptance

Before product adoption, retain the original fixed-footer sample as RED: identical footer-region assertion exits1, while the four margin-box samples exit0 (`NEGATIVE-CONTROL.json`). Add source tests decoding the serialized CSS back to exactly the two policy values plus newline, with hostile quotes/backslashes/newlines/closing-style text unable to escape the string; public CSS/HTML contains neither policy label nor synthetic payload. Unknown/malformed input remains governed by existing typed validation. Screen warnings and both-locale native print/download/context journeys remain covered.

For the final44 PDFs, preserve every parent Task4 requirement: fonts ready; print/A4/backgrounds; all11×2×2; every page at144dpi with unchanged SHA-bound PDFium; complete PDF/text/font/section/identifier/numeric/real-decision checks; page1 summary/page2 appendix; public isolation; both exact policy labels every simulated page; full physical/content/footer bounds and positive non-overlap; explicit rejection of missing documents/pages; off-page and old-dossier negative controls. Add this actual failed-fixed-footer negative control to the existing bounded PDF acceptance. Missing footer, footer at the top, malformed policy text or footer/body overlap must fail, even when the renderer itself exits0. Arabic text extraction can use visual order: supplementary normalized character comparison is not proof of correct order; exact source-policy decoding plus actual Arabic raster review remains required.

Retain the prescribed visual inspection of all44 first pages, every page of longest EN/AR, steel/PP/route8 reports, remaining contact sheets and full-resolution anomalies. Bind the reasonable page-count maximum only after reviewed candidate prototype; this amendment does not accept the current sample's 28/31/52/59 pages or any other product-quality issue. All other source/browser, graph/manifest, canonical visual/pin/R1, two clean-root make ci, independent exact-tree review, GitHub/exact-head/merge/main gates remain unchanged. Complete accepted source before the normal single generation sequence; any generation stop remains binding.

## Actual bounded experiment

Frozen source is `../../s19/product-implementation-r1/source-prototype-r5`, bound by manifest SHA `c68d91707d48772c635141a098843d327af981c5fa2b65c8c2f0dec4528a8df7`. Only the three external overlay copies changed. The unchanged producer and renderer ran in immutable image `sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112`, network disabled, read-only root/source/tools, only owned outputs/tmpfs writable. Commands, stdout/stderr and exit records are retained. Actual pypdfium2 5.13.0/PDFium153.0.7999.0, all170 pages144dpi. The producer's historical scope string is not an S19 approval; this packet states the actual S19 input provenance.

| Actual sample | Pages, old = new | Old footer failures | New footer failures |
|---|---:|---:|---:|
| Steel public EN | 28 | 0 | 0 |
| Steel public AR | 31 | 0 | 0 |
| Steel simulated EN | 52 | 52 | 0 |
| Steel simulated AR | 59 | 59 | 0 |

`SAMPLE-SUMMARY.json` binds all eight PDF hashes. All111 simulated pages have one exact English warning within the reserved footer and Arabic characters matching the source policy; all59 public pages contain neither English warning nor Arabic footer. New minimum body/footer gap is21.6734ptEN/22.1110ptAR; zero physical-page glyph violations. This proves the bounded footer placement, not all body-content boundaries, logical Arabic text order or full dossier correctness. `r4-analysis/FOOTER-OBSERVATION.json` contains every page's coordinates. The finite diagnostic remains external and does not replace the existing candidate acceptance.

Directly viewed old EN1/EN2/AR2 and new simulated EN1/EN2/EN52, AR1/AR2/AR59, public AR1/EN28 rasters. New examples show readable, correctly shaped bilingual bottom disclosure and unobscured appendix heading. All170 pages were rasterized and coordinate-inspected; manual viewing is limited to the named pages, not falsely represented as the final required review of all44 documents. No complete S19 candidate, all44PDF gate or final page-count approval is claimed.

## Sanad and Muhasabah

Direct evidence: immutable source preimages and patch; actual old/new PDFs; exact producer/renderer/image hashes; all-page glyph measurements; stated raster views; RED exit1/GREEN exit0. Attributed: previous negative-bottom attempt and current writer's broader implementation progress. Primary external support: Chrome's margin-box capability documentation, supplemented by this pinned-image experiment. Inference: fixed-body positioning/fragmentation explains displacement; no Chromium internal modulo algorithm claim.

Self-audit: this proposal repairs a measured defect without relaxing policy, isolation, typography or final gates. Only external owned packet files/containers were written; no source worktree, Git index, canonical artifact or retained service changed. Assumptions: policy labels remain the validated fixed pair and accepted Chrome print environment remains pinned; tests bind both. Remaining risks/unverified work: final44 cases, all content-region checks, full visual/Arabic semantic review, page-count quality, accepted-source integration and every final delivery gate. Independent reviewer must approve the concrete amendment before the writer adopts it. Author offers no approval of their own amendment.
