# Fresh S19 PDF manual coverage — preparation only

This records the existing procedure and observation lineage, not execution or approval of the forthcoming cohort. No PDF, raster, browser, service, candidate, index or Git operation was performed. `E` means `/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/overnight-2026-09-23`; `M` means its sibling `mission-20260925`.

Preparation: refreshed `M/HANDOFF.md`, approved S19 implementation Task 4/6, completion addendum, current browser operation draft and retained renderer/manual receipts. After reading, adopted bilingual print reviewer and evidence-provenance reviewer personas. Read/applied installed task-standards, project-orientation, PDF, Sanad, al-muhasibi and Muhasabah. The task is bounded procedural preparation; independent Claude GO and subsequent readiness acceptance belong to the coordinator/reviewer.

## Required finite coverage

Authority: `E/planning/s19/S19-IMPLEMENTATION-PLAN.md:104–108`; current binding: `M/browser-preparation/BROWSER-PDF-OPERATION-DRAFT-r2.json`, `/pdf_cohort_and_manual` (draft, not itself a release). The cohort is eleven named cases × public/simulated × EN/AR, 44 reports. Use actual emitted filenames and page counts, not historical expectations.

| Set | Required observation |
|---|---|
| All 44 page 1 images | Fresh actual views, even if identical to old images. Check one physical summary page, required summary content, distinct supporting/contradictory roles where present, EN/AR direction/shaping, technical IDs, disclosures and clipping. Native `view_image` is the direct method; contact-only small text must be escalated to readable native scale. |
| `steel-{public,simulated}-{en,ar}.pdf` and `polypropylene-{public,simulated}-{en,ar}.pdf` | Every page of these eight reports; retain steel contradiction and PP zero-support interpretation. |
| `alu-foil-{public,simulated}-{en,ar}.pdf` and `alu-profiles-{public,simulated}-{en,ar}.pdf` | Every page of these eight route-8 reports. |
| Longest EN and longest AR | Derive from the fresh renderer result; cover every page, including ties if any. Deduplicate against the preceding sets. Historical longest were profiles simulated EN63/AR73; these are attributed old measurements, not fresh results or a cap. |
| Remaining reports | Contact sheets covering every remaining page; actually inspect those sheets. The seven other case prefixes are fert-retail-packs, galvalume, pe-film, penicillin-api, sop, streptomycin-api and tinplate. |
| Suspected clipping, wrap, BIDI, heading/caption separation, footer collision, short terminal/orphan page | Inspect the actual native PNG at original resolution; preserve exact filenames and findings. Recheck affected adjacent pages when pagination changes. |

“Every page” does not mean an undocumented claim to have read every glyph at native resolution. The accepted procedure inspected page layouts on contact sheets and opened detailed anomalies/representative pages natively. For example, `E/reviews/s19-final-steel-pp-first-visual-r1/VIEWED-EVIDENCE.json` explicitly records 68 contact views and six native views; the later independent r4 review accepts the complete corrected lineage. Preserve that distinction. The strict text/geometry checks complement visual observations.

For appendix pages (page ≥2), exact-byte reuse below can satisfy the recorded observation level. New, changed, absent-from-lineage or otherwise uncovered required pages need actual fresh views. All 44 first pages are excluded from reuse. Assess page-count reasonableness and blank/orphan-only pages from the fresh results; do not impose 1,958 total/73 maximum as a contractual expectation or reduce fonts/content to reach them.

## Existing files and interfaces

Fresh outputs reserved by the browser draft are `M/browser-execution/functional/pdf/`, `M/browser-execution/rendered/` and `M/browser-execution/strict/`. The coordinator owns the single producer/raster/strict execution and its failure policy. This note adds no rerun.

* Renderer: `E/planning/s19/renderer-proof/render_pdf.py`, SHA-256 `80f17b6ff9040acc445001b33882efa0e44afbe820cac74b50338b5e2bb7f88b`; interface `python /tool/render_pdf.py --input /input --output /output`. Its `RENDER-RESULT.json` has `/reports[]/{pdf,pdf_sha256,pages[]}`; each page has `page`, `png`, `png_sha256`, `raster_px`, text hash and bounds diagnostics. Image names are `<pdf-stem>-page-<one-based:02>.png`; all pages are 144 dpi, uncropped.
* Strict checker: `E/s19/nonrule-caption-correction-r1/check_pdf_matrix.py`, SHA-256 `a68250a4168efa1ce444802099283ed4150326384815002ce2284125f15a2444`; interface `python /check_pdf_matrix.py --input /input --rendered /rendered --output /output`. Renderer exit zero alone is not acceptance. Reuse exact existing container/overlay command arrays from the current operation draft; historical counterparts are `E/s19/final-pdf-review-r4/{RENDER-COMMAND,STRICT-COMMAND}.json`.
* Contact recipe: `E/s19/product-implementation-r1/make_r11_contacts.py`, SHA-256 `d1968e19316a5ad98d1b9fa1c38333effda1f73ceea8beb36384d2560a7b638d`. It has **no CLI flags** and is hardcoded to historical paths; do not invoke it unchanged against old artifacts. It makes labeled 2-column ×3-row PNG sheets, 595×842 page thumbnails, 1190×2616 total, and writes `CONTACTS.json` with contact hashes, source page paths/hashes, recipe hash and renderer-result hash. Creation explicitly does not claim viewing.

After coordinator release and sealed fresh output, the existing recipe can be copied externally to `M/browser-execution/manual/make_r11_contacts.py`, with only its path-assignment line bound to `root=O; rendered=O.parent/'rendered'; out=O/'contacts'; out.mkdir(exist_ok=True)`. Supply `manual/PAGE-COUNTS.json` in its existing shape `[{'pdf': r['pdf'], 'pages': len(r['pages'])} for r in render_result['reports']]`. Record original/copy hashes and the exact path-only change. Keep its grouping/layout/hash behavior: all first pages, longest EN/AR, and other-seven-case reports. For changed/uncovered steel/PP/aluminium pages outside its longest groups, open the native pages directly; no new contact framework or selector is necessary.

The established image can run this path-bound recipe without installing anything:

```bash
docker run --rm --pull=never --network none --read-only --user 1000:1000 \
  --tmpfs /tmp:rw,size=128m -e HOME=/tmp -e PYTHONDONTWRITEBYTECODE=1 \
  --mount type=bind,src="$M/browser-execution",dst=/proof,readonly \
  --mount type=bind,src="$M/browser-execution/manual",dst=/proof/manual \
  --entrypoint python \
  sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112 \
  /proof/manual/make_r11_contacts.py
```

This is a future method, not an executed command or independent allocation. `$M` must be set to the absolute mission path above. For actual viewing use `view_image` with `detail: "original"` on each required page/contact path. Record the observation only after the tool returns an image and it has been inspected. An example future call is `view_image({path: M + '/browser-execution/rendered/steel-public-ar-page-01.png', detail: 'original'})`; that path is not asserted to exist here.

## Exact appendix reuse and concrete lineage

**Expressly accepted precedent:** `E/reviews/s19-final-steel-pp-first-visual-r4/REVIEW.md` (SHA-256 `4fcd30d3241a08269d4787fc8be516d2068324b11bbb157389a3b84b1bf44170`) states every current page matches an actually observed accepted print-first page, attributes coverage to its three reviewers, and approves full44 readiness without claiming new views. Current draft `/pdf_cohort_and_manual/acceptance` expressly allows old-page observations only with exact pixel identity and original review lineage, while requiring fresh first pages. Await the actual current GO; the historical approval alone does not release the new operation.

Use the old r4 rendered root `E/s19/final-pdf-review-r4/rendered/` as the comparison boundary. Join by exact report identity/locale/mode and page number. Rehash both actual PNG files and require equal SHA-256; also verify PDF and render-result identities. This strong byte-equality method matches the accepted receipt. Do not introduce approximate similarity, crop/mask changed footer/IDs, infer equality from HTML or whole-PDF text, or reuse a shifted page by loose content matching.

The separate companion `MANUAL-PDF-LINEAGE-SOURCES.json` hashes the existing manifests/observation ledgers below. It is an index of retained sources, not a fresh coverage receipt.

| Partition | r4 entry point and trace to actual observation |
|---|---|
| Steel/PP (8 reports) | `E/reviews/s19-final-steel-pp-first-visual-r4/CONTACT-SOURCES.json` `/reuse[]` → `prior_own_observation.{path,view_ledger,view_ledger_sha256}`. Its sibling `VIEWED-EVIDENCE.json` supplies scope, native views and accepted closures. Follow print-first `reviews/s19-nonrule-caption-correction-r1/visual/CONTACT-SOURCES.json`, then `reviews/s19-final-steel-pp-first-visual-r3/CONTACT-SOURCES.json` `/reuse[]/prior_own_observation` or `/contacts[]`, until an actual contact/native entry in the bound `VIEWED-EVIDENCE.json`. Contacts must match that ledger's actually-viewed list. |
| Aluminium (8 reports) | `E/reviews/s19-final-aluminium-visual-r4/PNG-REUSE.json` `/pages[]` → `reviews/s19-capability-caption-aluminium-r1/REVIEW.json` `/coverage[]` → `reviews/s19-final-aluminium-visual-r3/{REVIEW,VIEW-PROGRESS,CONTACTS}.json`. `VIEW-PROGRESS.json` `/all_contacts_actually_viewed[]` owns new contact observations; `/reused_exact_prior_observations[]/prior_views[]` points to r2 then r1/root-r2 as necessary. Each `CONTACTS.json` alone still says not-yet-viewed; the completed view-progress record is essential. |
| Other seven cases (28 reports) | `E/s19/final-pdf-review-r4/PNG-REUSE.json` `/exact_prior_own_observations[]` → its `/prior_own_view_ledger` at `s19/nonrule-caption-correction-r1/print44-review-r1/VIEWED-EVIDENCE.json`. Follow its `PNG-REUSE.json` and r3 contact bindings. `s19/final-pdf-review-r3/contacts-other28/CONTACT-SOURCES.json` `/exact_prior_view_reuse[]/prior_view` includes original ledger/contact paths and hashes; `/contacts[]` joins `/directly_viewed_contacts[]` in r3 `VIEWED-EVIDENCE.json`. Original r1 `/viewed_contacts[]` embeds every covered page path/hash; `/viewed_fullsize[]` records native inspection. |

Concrete terminal examples in the retained chain:

* **Native:** steel public EN page26, PNG `14d9a8ad11a010c13d962a460ee85dd0a4363a6a89cfa198d66ed0a9532ea71a`, in r4 steel/PP `VIEWED-EVIDENCE.json` `/representative_native_pages_exact_own_prior_reuse[]`, points to the actually viewed r1 native page.
* **Contact:** fertilizer public AR page2, PNG `f6f53f2ea8052ece718b00179462bf87384601b7d88dfb1cc406e1be960937f7`, appears inside r1 other28 `/viewed_contacts[]` in `fert-retail-packs-public-ar-01-12.jpg`, contact SHA `f202146e45a42f25b313820ddcc3de0c6dde03e0e2c706ed75f0c740efd9a04d`. This establishes layout observation, not native glyph reading.
* **Contact:** aluminium foil public AR page21, PNG `98a4f1c3c709bcdc8b123e60f7054cda45996ac1c01c8035b1de9cf39a1c4b82`, is in r3 aluminium `/all_contacts_actually_viewed[]` for `alu-foil-public-ar-changed-contact-01.png`, contact SHA `a5989802343280945135abac9fce9531bc32eb93f49ae31105e0f6cf8bc380d1`.

These examples illustrate existing mappings; no example is a fresh-cohort equality assertion. For each reused new appendix page, retain fresh PDF/page/path/hash → old r4 path/hash → original observation ledger/hash + contact/hash or native entry + accepted closure/review. Preserve original reviewer attribution; do not call another reviewer's observation your own. Any broken link or insufficient observation level means fresh viewing. Historical REJECT records remain REJECT; only unchanged observations carry through the documented corrections into independent r4 acceptance.

## Recording and limits

Reuse the existing receipt shapes: `CONTACT-SOURCES.json`/`CONTACTS.json` for image membership, `PNG-REUSE.json` for exact old/new bindings, and `VIEWED-EVIDENCE.json` or `VIEW-PROGRESS.json` for actual views, reviewer identity, inspection level, findings/closures and pending pages. Record fresh first-page count44 separately; coverage union must contain every required fresh page, with no pending anomaly. Strict PASS, generated contacts, page-hash equality without observation lineage, and durable selected-image presence cannot independently establish manual acceptance.

Sanad: requirements are direct reads of the approved plan and current draft; historical acceptance/observations are attributed to the named retained receipts; tool interfaces and hashes were directly inspected. No fresh render comparison or visual inspection was performed in this task. The lineage index records source-file hashes, not revalidation of every historical image. Assumptions: the released operation preserves these bindings; actual emitted counts/longest reports are still to be determined. Muhasabah: **PASS for bounded preparation**—no new approval, unviewed-page claim, output generation or competing proof protocol. Future strict/manual readiness, candidate CI and delivery remain unverified.
