# S19 corrected final PDF review — REJECT

Source ledger `18180060d91ef4c91cb5152114bebe3fed2e9704370839703a9455b06694dbc2`; cohort `0550e89602690c9930701a8195f4ea90115af1229a9d674e32cccd5b3a91ca8f`. This is an independent rendered-product review, not approval of source I previously authored.

- Unchanged renderer: **44 reports / 1,950 pages / 144 dpi**, exit0, SHA `12fe3a61c1667cf25d73c647211604398609e3db5b9808f932fca66cdd677428`.
- Unchanged strict checker: **44 / 1,950**, zero issues, exit0, SHA `3ddfe9024f033ad9cc68e3c0bd71aef962e952284581d2c9483fec1b8a4b81f2`. Automated PASS does not override visible defects.
- My assigned coverage: **28 reports / 1,214 pages**: all40 changed-page contacts (255pages) actually viewed,959 exact prior-viewed PNGs reused by hash, plus4 native page views. Exact filenames, constituents and hashes are in VIEWED-EVIDENCE.json and its bound CONTACT-SOURCES.json. Prior REJECT records remain intact.

## Blocking finding: CAPTION-ORPHAN-01

`penicillin-api-simulated-ar-page-30.png` ends R1-D with “النص الأصلي للمصدر”; its first metric (positive observed years2022/2023/2024) starts page31. Both native pages were viewed. The source at dossier.py:769 emits the caption immediately before the metric record; current CSS only keeps passport captions with their next block.

Keep the caption with its first actual fact, preserving all content, fonts, margins, footers and long-record flow. Prove this exact regression with the existing focused check and inspect its corrected native pages. No new framework is needed.

No other new blocker was found in my assigned coverage. The previous streptomycin BIDI interleaving is visibly closed. New SOP English page53 contains the complete terminal imports/unchanged-decision/expected-actual comparison, so it is not an orphan-only page. Assigned counts27–64 are explained by full ledgers/passports, with no blank pages observed; no universal page cap is approved while findings remain.

The independent reviewer separately reports polypropylene simulated Arabic page32’s Quantity heading detached from its first fact on33. That is attributed evidence, not a page I viewed. The fullcohort remains unapproved.

## Sanad and Muhasabah

Direct evidence: image views, source callsite/CSS, exact source1759/cohort220/coveredPNG1214 preservation checks, and actual unchanged-tool execution. Functional839passes are attributed to retained writer/root evidence. Contact sheets establish visible layout, with fullsize anomaly inspection; strict checks provide separate content coverage. No source/index/service writes, no self-approval of validator work, no new capture.

**Muhasabah: PASS for the bounded, evidence-qualified review; product verdict REJECT.** Remaining gates include correction/review, exact-candidate two-root PDF checks, canonical128/R1 and delivery. S19-only stop boundary and local preview remain preserved.
