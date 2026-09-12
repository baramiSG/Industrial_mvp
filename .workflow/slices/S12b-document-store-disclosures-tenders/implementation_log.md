# S12b implementation log

## 2026-09-12 — T0 preflight

Branch `slice/s12b-document-store-disclosures-tenders`; HEAD `cdfd4ba4b016619b7ab33a373d334f22c337166d`; plan SHA-256 verified `c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`.

T0 PASS: BRANCH_OK; baseline `pytest -q` → 1755 passed, 1 warning; reconstruct `--all --no-check-manifest` → `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)`; gates [6]-[10] PASS (document line absent pre-T6 as expected). No .env read; manifest runs 0; commits 0.

## Execution ledger

- T0: complete.
- T1: complete — RED then GREEN on pypdf pin tests; `uv lock` exit 0; `uv sync --locked --extra dev` exit 0; uv.lock +11 lines pypdf only.
- T2: complete — seven fixtures authored; textlayer.py implemented; 21/21 textlayer tests GREEN; pinned hash 52dd2a46192c39cf23f2551763a6c753fcf9573d5050a1119852b194e5fa6099.
- T3: complete — Stage.DOCUMENT, lists.py, source_config 1.2.0, config YAML seven PRE_OBSERVATION sources; stage/lists/config/stored-artifact pin updates; gates [6]-[10] PASS with document line (0 records).
- T4–T6: complete (slot 2) — `tests/test_acquisition_document_{connectors,store,cli}.py`, raw_store pin, integrity-contract W2/W4 updates; `_build_url` document_url overlap fix; DocumentStore PROJECT_ROOT guards; reconstruct document manifest checks; gates [3]-[5], [9], [12], [13] PASS; IAC-1 institutional connector files byte-identical.
- T7-v1 (slot 1, history): complete — seven consultations recorded; seven empty `-v1` lists; seven acquire runs ENDPOINT_UNVERIFIED, requests_made=0.
- T7-v2 (slot 2): complete — second window closed **2026-09-12 ~05:23 UTC**.

### T7-v2 consultation summary (read-only, `/tmp/s12b_t7_consult.py` → `/tmp/s12b_t7_consult.json`)

| Publisher | Landing URL | HTTP | Notes |
|---|---|---:|---|
| producer_sabic | https://www.sabic.com/en | 200 | Followed navigation; no qualifying PDF ≤16 MiB in bounded window |
| producer_unicoil | https://www.unicoil.com.sa | 200 | Six PDFs verified via publisher HTML links |
| etimad_tenders | https://tenders.etimad.sa | 200 | Public listing inspected; no tender document URL qualified |
| saso_documents | https://www.saso.gov.sa/en | 200 | Six regulation PDFs verified |
| tadawul_disclosures | https://www.saudiexchange.sa | 403 | Exchange front page blocked automated fetch |
| producer_tasnee | https://www.tasnee.com | 0 | No TCP connection (DNS resolves) |
| producer_advanced_petrochemical | https://www.advancedpetrochem.com | 0 | No DNS resolution |

### T7-v2 per-source table

| source | list_id | entries | list SHA-256 | MAX_REQUESTS | stop_reason | requests_made | records built |
|---|---|---:|---|---:|---|---:|---|
| producer_unicoil | producer_unicoil-v2 | 6 | 5b745939032505e57d8337258f9710a6ec719a1813ae7006e3dbb1b9af749a80 | 7 (1 TERMS + 6) | LICENSE_UNRECORDED | 0 | 0 |
| saso_documents | saso_documents-v2 | 6 | aff9e26c598f35ae965ed58f10fe92a79a108f5ce44f6900836af48bdf9e2c58 | 7 | LICENSE_UNRECORDED | 0 | 0 |
| producer_sabic | producer_sabic-v2 | 0 | 32c61951bb262757… | 1 | ENDPOINT_UNVERIFIED | 0 | 0 |
| etimad_tenders | etimad_tenders-v2 | 0 | 78a20ff4692054c0… | 1 | ENDPOINT_UNVERIFIED | 0 | 0 |
| tadawul_disclosures | tadawul_disclosures-v2 | 0 | 7b94bdb165478a77… | 1 | ENDPOINT_UNVERIFIED | 0 | 0 |
| producer_tasnee | producer_tasnee-v2 | 0 | 88163b5ccf46c28a… | 1 | ENDPOINT_UNVERIFIED | 0 | 0 |
| producer_advanced_petrochemical | producer_advanced_petrochemical-v2 | 0 | e40f28729e0b294c… | 1 | ENDPOINT_UNVERIFIED | 0 | 0 |

Duplicate slot-1 tadawul runs: `data/raw/tadawul_disclosures/83faa784…/20260912T050943Z` and `…/20260912T050946Z` — two zero-request ENDPOINT_UNVERIFIED invocations three seconds apart with no reason recorded in slot 1 (SR-04); both retained as write-once evidence and cited in KL-58.

Duplicate v2 runs: `producer_unicoil` and `saso_documents` each have paired run_ids (`052305`/`052309` and `052304`/`052309`) from a repeated Makefile invocation after the first pass logged LICENSE_UNRECORDED; all attempts retained.

- T8: complete — Core 04 DocumentRecord 1.0.0, Core 05/03/09 insertions; gates [22]-[24] PASS; W4 closed.
- T9: complete — ADR-017, KL-45 extension, KL-54–61, runbook, BUILD_PROGRESS, REQUIREMENTS_TRACEABILITY §N, `.workflow/state.json`; W2 closed.
- T10: complete — filtered pytest 1848 passed/1 deselected; gates [0]-[13], [22]-[26] PASS; [14] not run.
- T11: complete — `build_manifests.py` exit 0 at **2026-09-12T05:26:47Z**; §11 mirrored; immediate [14] PASS.
- T12: complete — [14]-[21] PASS; full pytest **1865 passed**, 1 warning; `make ci` PASS including **118 functional + 4 visual** Chromium nodes; gates [22]-[26] and corrected [25] PASS.

## Stop condition (2026-09-12, slot 1)

Frozen oracle **[5]** fails: T4–T6 test modules not yet authored. Resolved in slot 2.

## Supervisor review of implementation slot 1 (owner lead agent, 2026-09-12 ~05:20Z)

Slot 1 (`implementer-composer`, composer-2.5-fast, agent 23a5672e) stopped before T8 with the tree uncommitted. Supervisor findings on the actual tree:

- SR-01 (INCOMPLETE): T4–T6 named test modules not authored — **resolved slot 2**.
- SR-02 (REPORTING): mis-indexed verification commands — **discipline applied slot 2**.
- SR-03 (T7 QUALITY): v1 one-URL consultations — **v2 window redone slot 2**.
- SR-04 (DUPLICATE RUN): tadawul duplicate runs — **logged above and KL-58**.
- SR-05 (PLAN DEVIATION, ACCEPTED OD-8): browser/visual pin tests for pypdf — **named in ADR-017**.

Slot 2 continues on this tree (same seat, `implementer-composer`), brief `.autonomous-workflow/drafts/s12b-document-store-disclosures-tenders/implementer-brief-slot-2.md`.

## Supervisor implementation review of slot 2 (owner lead agent, 2026-09-12 ~05:45Z)

Slot 2 (`implementer-composer`, agent a3670614) completed T4–T12 on the slot-1 tree: 1865 tests, `make ci` (118 functional + 4 visual) reported green, one `build_manifests.py` run at 2026-09-12T05:26:47Z with [14] PASS, candidate `5eaf87e7…` (148 files), index empty. Supervisor findings on the actual tree:

- SR-06 (T7 PROCEDURE, must correct): `producer_unicoil-v2` and `saso_documents-v2` each list six verified `application/pdf` links, yet both acquire runs stopped `LICENSE_UNRECORDED` with `requests_made 0` because `terms_reference` / `endpoint_templates.TERMS` were left `UNAVAILABLE` although plan T7 step 1 requires replacing those sentinels with observed values. Supervisor read-only observation (2026-09-12 ~05:40Z, `curl -I -L`, project user agent): `https://www.saso.gov.sa/en/acceptable_use_policy/Pages/default.aspx` 200 and `https://www.saso.gov.sa/en/mediacenter/Pages/open_data.aspx` 200 (both already recorded by S12a for `saso_catalogue`); `https://www.unicoil.com.sa/privacy-policy/` 200 (the only legal page linked from the UNICOIL footer; `/terms-and-conditions/` 404); `https://www.sabic.com/en/terms-of-use` and `/en/legal-notice` 406 with the project user agent; `https://tenders.etimad.sa/Tender/AllTendersForVisitor` no response, `https://portal.etimad.sa/` 405. The UNICOIL EPD link `…/EPD-Report_GS_Unicoil_Rev02-1_1.pdf` answers 200 `application/pdf`. Correction: record the observed terms pages for `saso_documents`; for `producer_unicoil` either record the observed legal page with a truthful usage note or, if that page states no reuse terms, set `license_capture_required: false` with the ZATCA precedent and a KL row; then re-run the two `-v2` lists with the reason logged before each run (prior run `LICENSE_UNRECORDED`; sentinel replaced by observed value). Lists are not edited; if displayed link text differs from the recorded `title_text`, author `-v3` lists instead.
- SR-07 (advisory, not a finding): several SASO `-v2` entries are vehicle/tank/machinery regulations; where the consulted page displays industrially relevant technical regulations (steel, plastics, construction products, chemicals, fertilizers), prefer them in any `-v3` list — bounded to the same ≤ 6 entries and only from displayed links.
- SR-08 (MANIFEST): the single T11 generation (05:26:47Z) preceded the corrected operator window. The owner lead agent authorizes exactly one further `scripts/build_manifests.py` run (OD-9) after the SR-06 re-runs and the T10 regression, with [14] immediately after; ADR-017 must record both runs and the reason; no further run is authorized.
- Everything else observed as reported: pyproject/uv.lock delta limited to pypdf; the two dev-extra pin tests changed per OD-8; institutional test files byte-identical; S11/S12a partitions and frozen roots unchanged; both reconstruction lines present.

Slot 3 continues on this tree (same seat), brief `.autonomous-workflow/drafts/s12b-document-store-disclosures-tenders/implementer-brief-slot-3.md`.

## Slot 3 correction round (implementer-composer, 2026-09-12)

**T7-v3 window:** opened 2026-09-12T05:35:06Z, closed 2026-09-12T05:40:21Z.

### Terms consultation (read-only)

| URL | UTC | HTTP | Content-Type | Bytes | SHA-256 | Reuse/usage terms observed |
|---|---|---:|---|---:|---|---|
| `https://www.saso.gov.sa/en/acceptable_use_policy/Pages/default.aspx` | 05:35:06Z | 200 | text/html | 200737 | `12e63feb…` | Yes — Usage and Disclaimer, usage restrictions, intellectual property |
| `https://www.saso.gov.sa/en/mediacenter/Pages/open_data.aspx` | 05:35:08Z | 200 | text/html | 260705 | `a0717fc0…` | Yes — open data reuse/dissemination policy |
| `https://www.unicoil.com.sa/privacy-policy/` | 05:35:10Z | 200 | text/html | 85722 | `0fb3556c…` | No document reuse terms — PDPL personal-data policy only |

Config: `saso_documents` terms/rate-limit from acceptable-use policy; `producer_unicoil` `license_capture_required: false` (KL-62).

### T7-v3 per-source table

| source | list_id | entries | list SHA-256 | MAX_REQUESTS | stop_reason | RunReport `requests_made` (aggregate-count artefact, see note) | stored transport fetches | records built |
|---|---|---:|---|---:|---|---:|---:|---|
| saso_documents | saso_documents-v3 | 6 | `8a12aca74e38a53b…` | 7 | — | 27 | 7 (1 TERMS `text/html` + 6 `application/pdf`) | 6 COMPLETE |
| producer_unicoil | producer_unicoil-v3 | 6 | `1115ff78937738b2…` | 6 | — | 21 | 6 (6 `application/pdf`; `license_capture_required: false`) | 6 COMPLETE |

Note (slot 4, S12B-IR3-F02): 27 and 21 are the deferred S11/S12a **aggregate-count artefact** — `pipeline._run_units` sums the per-unit `coverage.requests_made`, each of which echoes the cumulative shared `RequestBudget.used` at that unit's completion (SASO 2+3+4+5+6+7; UNICOIL 1+2+3+4+5+6). The stored page contracts prove 7 and 6 transport fetches; neither run exceeded `MAX_REQUESTS`. `pipeline.py` is unchanged (KL-65).

Prior v2 runs retained (`LICENSE_UNRECORDED`, `requests_made=0`). Re-run reason logged before each acquire: prior run `20260912T052309Z` `LICENSE_UNRECORDED`; sentinel replaced by observed value.

### T10–T12 (slot 3)

- T10 regression: gates [0]–[13], [22]–[26] PASS (pre-manifest).
- T11 second run (OD-9): `build_manifests.py` exit 0 at **2026-09-12T05:43:02Z**; §11 mirrored; [14] PASS.
- T12: [14]–[21] PASS; full pytest **1878 passed**, 1 warning; `make ci` PASS (**118 functional + 4 visual**); [22]–[26] and corrected [25] PASS.
- `reconstruct_document` fix: use `evidence[0].coverage` and resolved list paths for multi-entry run reconstruction ([5]/[17]/[20]).
- Candidate SHA-256: `4cfe3ec71f3e9cc2d6d4dff466d83762b58ca3bc683f7c6c58c1c4544bc282e4` (200 files vs HEAD).

## Supervisor check of slot 3 and review candidate identity (owner lead agent, 2026-09-12 ~06:00Z)

Slot 3 (`implementer-composer`, agent 2761212e) delivered the SR-06 correction: observed terms recorded (SASO acceptable-use policy; UNICOIL privacy policy carries no reuse terms → `license_capture_required: false`, KL-62), `-v3` lists with verbatim displayed text, two re-runs (`saso_documents-v3` run `20260912T053622Z`, `producer_unicoil-v3` run `20260912T053955Z`) yielding 12 COMPLETE DocumentRecords with `text_layer.status = COMPLETE`, the OD-9 second manifest generation at 2026-09-12T05:43:02Z with [14] PASS, and T12 gates. Owner lead agent independently ran `make ci` on the unchanged tree: exit 0 — prohibited-file, threshold-literal, UI-contract and ES-module scans PASS; INTEGRITY PASS; scenario validation PASS; `RECONSTRUCTION PASS (1 snapshots, 4 artifacts)` and `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`; 1878 passed / 1 warning; SMOKE PASS; browser preflight PASS; 118 functional passed; 4 visual passed (log kept locally).

Review candidate identity (IAC-6 procedure, slice-record files excluded): SHA-256 `87084ed23328962a8cdaa021738280823af702fb7bc2a5959aaea41b197a6314`, 194 files, base `cdfd4ba4b016619b7ab33a373d334f22c337166d`, index empty; 200 prospective files including the six slice-record files. The implementer's reported `4cfe3ec7…` (200 files) included the slice records and is not the review identity.

Supervisor observations for the independent reviewer (not corrections applied by the supervisor): (a) RunReport `requests_made` 27 (SASO, MAX_REQUESTS 7) and 21 (UNICOIL, MAX_REQUESTS 6) are the pre-existing aggregate-count artefact carried from S11/S12a (deferred), not 27/21 transport requests — the per-unit page contracts show one stored page per unit plus one terms page; the records should say so explicitly; (b) duplicate v2 invocations are explained in the log and KL; (c) `store.py` gained a reconstruction fix in slot 3 once real records existed.

## Independent implementation review of candidate 87084ed2… — REJECT (reviewer-grok, 2026-09-12 ~06:15Z)

`reviewer-grok` (cursor-grok-4.6-xhigh, agent bea86489) recomputed the identity (match), executed [0], [1], [5]–[14], [17], [19], [20], [22]–[26] + corrected [25], `verify_integrity`, `pytest -q` (1878 passed), `validate_scenarios`, `demo_smoke` (frozen outcomes exact) and returned **REJECT** with two HIGH findings and seven advisories (record `.autonomous-workflow/evidence/s12b-document-store-disclosures-tenders/implementation-review-slot-3.json`):

- **S12B-IR3-F01** — all six COMPLETE `saso_documents` records store Arabic lines in visual (reversed) order under `PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0`, while their `-v3` list entries declare `languages: ["en"]`; KL-63 discloses spacing/rotation only; the logical-order contract is proven only for the CID/ToUnicode fixture. Required: honest disclosure (no reshaping/bidi), `languages` including `ar`, a repository-tree proving test.
- **S12B-IR3-F02** — ADR-017, the log and `test_evidence.md` present RunReport `requests_made` 27 (SASO) and 21 (UNICOIL) as if they were transport counts ("1 TERMS + 6 documents"); they are the deferred S11/S12a aggregate-count artefact (sum of per-unit cumulative `RequestBudget.used`); actual stored pages are 7 and 6. Required: name the artefact in ADR-017/KL/log/evidence; no `pipeline.py` change.
- Advisories A01–A07 (HTTP/1.0 preamble in one UNICOIL payload stored as-is under no-sniffing; stale OD-9 line in BUILD_PROGRESS; hook-test message pin; consultation tuples for the 12 document URLs; `expected_content_types` still UNAVAILABLE after observed `application/pdf`; one T3 test name absent; identity in `test_evidence.md` includes slice records).

Owner adjudication: F01 VALID (HIGH), F02 VALID (HIGH); advisories A02, A03, A05, A07 to be addressed in the correction round; A01, A04, A06 recorded. Composer slots exhausted → `implementer-fable` slot 4 under OD-10/OD-11/OD-12; brief `.autonomous-workflow/drafts/s12b-document-store-disclosures-tenders/implementer-brief-slot-4.md`.

## Slot 4 correction round (implementer-fable, claude-fable-5-1-thinking-max, 2026-09-12)

**Persona:** senior data-provenance / acquisition-pipeline engineer with bilingual (Arabic/English) PDF text-extraction experience — the round is about honest disclosure of content-stream (visual-order) Arabic under `PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0`, a governed record replacement in a write-once store, and control-record truthfulness. Skills applied: task-standards, sanad, muhasib.

**Preflight (06:25Z):** branch `slice/s12b-document-store-disclosures-tenders`; HEAD `cdfd4ba4b016619b7ab33a373d334f22c337166d`; plan SHA-256 re-verified `c70e90652b448e2e9b9447bf3cb6fb161fe9224d20f2021e00a1368e7a2fbdb5`; index empty; 54 porcelain entries (the reviewed candidate `87084ed2…`, 194 files + slice records). Network: none in this round (no consultation, no `IOR_ACQUISITION_LIVE`, no acquire). `.env` not read. Manifest runs this slice at start: 2 (05:26:47Z, 05:43:02Z).

**Finding adjudication (own reading of the tree, sanad):** F01 VALID — every SASO record stores the authority-name cover line as `ةدوجلاو سيياقلماو تافصاوملل ةيدوعسلا ةئيهلا` (memory order; character reversal yields `الهيئة السعودية للمواصفات…`), while the `-v3` entries declare `languages: ["en"]`. F02 VALID — `pipeline._run_units` sums `cov.requests_made` per unit (`pipeline.py:172`) and each unit's coverage echoes the shared cumulative `RequestBudget.used`; the stored `coverage.json` files of run `20260912T053622Z` carry `requests_made` 2,3,4,5,6,7 (sum 27) beside 7 stored payloads (1 TERMS `text/html` + 6 `application/pdf`); run `20260912T053955Z` carries 1..6 (sum 21) beside 6 payloads. A02, A03, A05, A07 VALID (addressed below); A01, A04, A06 accepted observations (below).

### F01 step 1 — derived-text inspection (scratch `/tmp/s12b_slot4/inspect_langs.py`, read-only)

Non-empty lines classified by script (Arabic block U+0600–U+06FF and presentation forms vs Latin letters):

| document_id | v3 entry | pages | Arabic-only lines | Latin-only lines | mixed lines | Arabic chars | Latin chars | Latin content | truthful `languages` |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54` | E-001 Machinery Safety | 106 | 1543 | 273 | 1941 | 110067 | 54461 | English standard titles in annex tables (e.g. "Textile machinery and accessories -", "Safety of machinery") | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661` | E-002 Conformity Models | 37 | 985 | 38 | 54 | 53368 | 1051 | only `SASO`, footer `www.saso.gov.sa`, parenthetical English equivalents (Type Approval, Supplier Declaration of Conformity) | `["ar"]` |
| `DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d` | E-003 Explosive Atmospheres | 38 | 672 | 126 | 365 | 42449 | 11265 | English standard titles ("Explosive atmospheres - Part …") | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf` | E-004 EMC | 28 | 450 | 108 | 328 | 28230 | 9950 | English standard titles ("Low-voltage switchgear and controlgear …") | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b` | E-005 Electrical/Electronic standby | 14 | 339 | 15 | 16 | 17005 | 354 | only `SASO`, footer URL, glossary equivalents (HiNA, Network Port) | `["ar"]` |
| `DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9` | E-006 Communications/IT devices | 37 | 688 | 98 | 277 | 37845 | 7823 | English equipment/standard titles ("Radio Equipment and Telecommunication Terminal Equipment") | `["ar","en"]` |

Rule applied (DERIVED, recorded for the reviewer): `ar` because the body text is Arabic in every record; `en` only where Latin-only lines carry English titles/descriptions beyond the publisher name, the footer URL and parenthetical glossary equivalents of Arabic terms. UNICOIL: all six records have 0 Arabic characters (Latin chars 543–75561) — `["en"]` is truthful; no UNICOIL change.

Visual-order confirmation (all six SASO records, page 1): the authority-name cover line is stored as `ةدوجلاو سيياقلماو تافصاوملل ةيدوعسلا ةئيهلا` (41–42 leading layout spaces); reversing the characters yields `الهيئة السعودية للمواصفات واملقاييس والجودة` (note the lam-alef ligature artefact `امل` — the reversed string is *not* claimed as a faithful logical string either; only the stored visual-order string is pinned). Regulation-title lines show the same pattern (e.g. `ةقباطلما جذامنل ةماعلا ةحئلالا`).

### F01 step 5 (RED first) — proving tests authored before any correction

New file `tests/test_acquisition_document_records.py` (brief-authorized location). Run against the pre-correction tree at 2026-09-12T06:27:35Z:

```
pytest -q tests/test_acquisition_document_records.py
FAILED …::test_saso_record_declares_arabic_references_v4_and_pins_visual_order_cover_line[DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9-1-14-41]  (assert 'ar' in ['en'])
FAILED …::test_saso_record_declares_arabic_references_v4_and_pins_visual_order_cover_line[DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54-1-12-42]  (assert 'ar' in ['en'])
FAILED …::test_all_six_saso_records_declare_arabic_and_reference_v4  (assert 'ar' in ['en'])
FAILED …::test_declared_languages_are_consistent_with_derived_script[saso_documents]  (('ar' in ['en']) == True)
FAILED …::test_saso_v4_list_is_a_declaration_correction_of_v3  (FileNotFoundError saso_documents-v4.json)
FAILED …::test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count[saso_documents-…]  (assert 'aggregate-count' in KL S12b section)
FAILED …::test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count[producer_unicoil-…]  (same)
7 failed, 2 passed in 0.06s
```

(The first RED run also exposed that the TERMS unit directory `18648a57…/20260912T053622Z` holds a contract + payload without `coverage.json`; the test was corrected to skip that unit and re-run RED with the same 7/2 result.) The two passing tests are pure stored-fact oracles (payload counts/content types) that do not depend on the correction.

### F01 step 2 — `saso_documents-v4` (DocumentList 1.0.0)

Authored by `/tmp/s12b_slot4/author_v4.py` from the v3 JSON: same six `document_url` values, same `entry_id` order, verbatim `title_text` / `document_date_text` / `source_reference_text` / `publisher_*` / `document_kind` / `expected_content_type` / `evidence_class_target` / `supports`; `languages` per the table above; `recorded_on` `2026-09-12`; `recorded_by_seat` `implementer-fable`; `documentation_urls_observed` copied from v3; `consultation_summary_text` states the declaration correction (F01, OD-11), run `20260912T053622Z`, no new consultation/acquisition, and quotes the v3 consultation text. Validated through `documents/lists.py` (`load_document_list` → 6 entries). **list_id `saso_documents-v4`, SHA-256 `16d9e29bd86f720c38a29ffcd7a24e5140c94a2893226fac7f67183a3a4338bb`, 6144 bytes.** v1/v2/v3 lists untouched (v3 SHA-256 `8a12aca74e38a53b8f3f83f8a148b92f653bce73c382260322e9ef837b1b26f6` re-verified).

### F01 step 3 — OD-11 replacement of the six v3-built SASO records (logged BEFORE removal, 06:25Z)

| document_id | SHA-256 of removed record file | bytes |
|---|---|---:|
| `DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9` | `fe0ba482584b92afda94a63ec0e17673a599784e3bbf406192242ff8bf12b6c8` | 205950 |
| `DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661` | `e5ad91008d8c1edb4fc3116721baf45da6debb94960f0c0815586a96e61db9d8` | 225194 |
| `DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54` | `51d1f9b44871cae95a60c089424c0536e45fc93aa35a20b3905061e3f9ed8570` | 689291 |
| `DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d` | `562b853ce9dafb4608c74a6a50975624500dc81c529c19a275aa9e29581bfeb2` | 232632 |
| `DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b` | `e4a6412eab81c30e474a8dbc277df515980bd8eaa14de9c43fae68794f39032e` | 82803 |
| `DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf` | `67c3057d2ac638862c60d07ae0739a68cb3ab3b619369bb63172600c90ad6f48` | 170887 |

Copies kept under `/tmp/s12b_slot4/old_records/` for the byte comparison only (outside the repository). These are uncommitted derived outputs (OD-11); raw run `20260912T053622Z` and the v1/v2/v3 lists are retained as history.

Removal (06:29Z): the six files above deleted from `data/documents/saso_documents/records/` (nothing else removed). Rebuild (offline; `UV_OFFLINE=1` so `uv run --locked` cannot touch the index; no `IOR_ACQUISITION_LIVE`; `build_document_records` iterates every stored COMPLETE DOCUMENT coverage under the source — the v2 runs are `LICENSE_UNRECORDED`/non-COMPLETE and the TERMS unit carries no coverage, so only the six `20260912T053622Z` units qualify):

```
$ UV_OFFLINE=1 make build-documents SOURCE=saso_documents LIST_ID=saso_documents-v4     # 2026-09-12T06:30:12Z → 06:30:22Z, exit 0
PYTHONPATH=src /home/barami/.local/bin/uv run --locked --extra dev python -m ior_mvp.acquisition build-documents --source saso_documents --list-id saso_documents-v4
Rotated text discovered. Output will be incomplete.
{
  "already_stored": [],
  "built": [
    "DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9",
    "DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661",
    "DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54",
    "DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d",
    "DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b",
    "DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf"
  ],
  "skipped_no_entry": [],
  "unavailable": []
}
```

(The `Rotated text discovered` line is a pypdf layout-mode warning on stderr — KL-63 extended by one phrase; the rebuilt `pages` are byte-identical to the removed records', so it changed nothing.)

Comparison (`/tmp/s12b_slot4/compare_records.py`, old copies vs rebuilt files): all six `document_id`s identical; `pages`, `line_count`, `page_count`, `raw_artifact_ref`, `coverage`, `text_layer`, `transformation_record`, `quality_summary` and `list_ref.entry_id` identical. Per-record diff keys — identical for all six: `list_ref.list_id` (`saso_documents-v3` → `saso_documents-v4`), `list_ref.path` (`…/saso_documents-v3.json` → `…/saso_documents-v4.json`), `list_ref.sha256` (`8a12aca7…` → `16d9e29b…`), `declared.languages` (`["en"]` → per table), and `evidence[0].observation_context.languages` (the passport's copy of the declared languages, built by `build_acquired_passport(observation_context={… 'languages': entry.languages …})` — a direct consequence of the same correction, reported here because OD-11 names `list_ref` and `declared.languages` only). Rebuilt file SHA-256s:

| document_id | rebuilt SHA-256 | bytes | `declared.languages` |
|---|---|---:|---|
| `DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9` | `9efcfd44ba8285f5e3eeeeeea8be36f2a327148d68733a85f24de20d00439627` | 205978 | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661` | `8a13c45199c20306a8bd59fb334ee66ae725a8ef90d6a02be1d95479c44f920c` | 225194 | `["ar"]` |
| `DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54` | `960781a5b43e7e0f5a835d1a04079745c2d478ed34cc046a2c5b393288735a62` | 689319 | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d` | `a11bc449f670d4a0b3cb6d06759d923bcba4a8b5f166ef9b8b597d0c1e09634d` | 232660 | `["ar","en"]` |
| `DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b` | `2de95461a23837469a5084f5a3e9b8a5a429177ce923be90a1355452b99a2606` | 82803 | `["ar"]` |
| `DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf` | `74e2fb0ad13cb9404a78bfad2adb88211944b421f983cf2dff5bd511f2d429ec` | 170915 | `["ar","en"]` |

### F01 step 4 — disclosure (OD-12; edits only inside text this slice introduced)

- Core 04 `### DocumentRecord 1.0.0`: new paragraph **"Text order (PDF)"** — content-stream order stored verbatim; visual-order Arabic where the publisher PDF paints it so; `quality_summary: PASS` = COMPLETE text layer, not logical reading order; logical order guaranteed only where ToUnicode yields it (CID fixture test named); no bidi/reshaping; S20 normalisation; affected records named in KL. All ten plan-fixed [24] tokens unchanged.
- Core 05 §10 DOCUMENT paragraph: did not literally say "logical order", but its unqualified "preserving verbatim Arabic/English lines" is the sentence a reader takes as a logical-order claim (the reviewer's reading); qualified in place with "in PDF content-stream order … (where a publisher PDF paints Arabic in visual order, the stored lines are visual-order; `COMPLETE` / `PASS` denotes an extracted text layer, not logical reading order — Core 04 DocumentRecord 1.0.0)". §3 rows untouched ([22] PASS).
- ADR-017: new section "Independent review findings and correction round (slot 4 …)" recording F01 (fact, OD-12 disposition, v4 list, OD-11 replacement, diff keys), F02, the advisories; T7-v3 paragraph corrected (F02); manifest section renamed "Change classes and manifest-run authorizations" with OD-10 and the three runs' reasons; third-run receipt appended after the run.
- KNOWN_LIMITATIONS: KL-55 rewritten to name the v4 rebuild (v3 retained as history); **KL-64** (visual-order Arabic; names the six document_ids; "visual order"; S20) and **KL-65** (aggregate-count artefact) added; S12b intro sentence extended; KL-63 one-phrase extension (rotated-text warning also during the SASO rebuild).
- `tests/test_integrity_contract.py::test_s12b_core_v2_document_contracts`: six assertions **added** (Core 04 section contains `content-stream text order verbatim`, `visual-order Arabic`, `not logical reading order`, `No bidi reordering or reshaping is applied`; Core 05 §10 contains `PDF content-stream order`, `not logical reading order`); no existing assertion removed or changed.
- `test_arabic_cid_pdf_preserves_logical_order_verbatim`: unchanged, GREEN.

Proving tests GREEN after the corrections (same file, 06:33Z): `pytest -q tests/test_acquisition_document_records.py tests/test_integrity_contract.py::test_s12b_core_v2_document_contracts tests/test_acquisition_document_textlayer.py::test_arabic_cid_pdf_preserves_logical_order_verbatim` → `11 passed`. (One intermediate GREEN run failed only because my own ADR text quoted the removed parenthesis literally; the ADR sentence was reworded to describe the removal without the literal — the test's "ADR must not gloss 27 as 1 TERMS + 6 documents" assertion is kept.)

### F02 — aggregate-count wording

ADR-017 T7-v3 paragraph (formerly "`requests_made=27` (1 TERMS + 6 documents)") now states RunReport `requests_made=27` / `=21` are the deferred S11/S12a aggregate-count artefact (sum of per-unit `coverage.requests_made`, each echoing cumulative `RequestBudget.used`; 2+3+4+5+6+7 and 1+2+3+4+5+6) and that the stored page contracts prove 7 (1 TERMS `text/html` + 6 `application/pdf`, `MAX_REQUESTS` 7) and 6 (`MAX_REQUESTS` 6, `license_capture_required: false`) transport fetches; KL-65 added; the T7-v3 tables in this log and in `test_evidence.md` gained a "stored transport fetches" column and a note. `pipeline.py` unchanged (verified by [8]'s exclusion set and by the untracked-file comparison below: `pipeline.py` identical to the candidate). Read-only test `test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count` pins payload count 7 / sum 27 and 6 / 21, the per-unit cumulative pattern, `max == MAX_REQUESTS`, `aggregate-count` in the KL S12b section and in ADR-017, and the absence of the "(1 TERMS + 6 documents)" gloss in ADR-017; `test_saso_terms_page_is_the_seventh_stored_fetch` pins the stage/content-type sets.

### Advisories

- **A02** — `docs/BUILD_PROGRESS.md`: the stale "OD-9 second manifest run pending T12" phrase replaced by the fact (executed 05:43:02Z, [14] PASS, slot-3 T12 complete); dated lines added for the review REJECT and for this correction round.
- **A03** — `DocumentConnector._pre_storage_refusal` now returns `super()._pre_storage_refusal(result, stage)` for every stage other than TERMS/DOCUMENT instead of copying the DIRECTORY/REGISTRY block (unused `_institutional_privacy_error` import removed; behaviour unchanged). New `tests/test_acquisition_document_connectors.py::test_pre_storage_hook_pins_institutional_refusal_literals_and_delegation` pins, for DIRECTORY and REGISTRY on both `BaseConnector` and `ProducerUnicoilConnector`, the exact tuples `("PersonalDataFields", "Response refused by institutional text-only privacy policy; body not stored")` and `("UninspectableTextPayload", …same message…)`, `None` for a clean body, `None` for UNIVERSE/TARIFF/BULK/TERMS, the DOCUMENT-stage envelope-only behaviour (`text/plain` body with a personal label → `None`; `application/octet-stream` → `UnsupportedDocumentEnvelope`), and the same literal in the stored `attempt.json` `observed_response.error_message_redacted` on two acquire paths. IAC-1: `tests/test_acquisition_institutional_connectors.py` and `tests/test_acquisition_institutional_snapshots.py` byte-identical to HEAD (`git diff --quiet HEAD --` → identical); 434 tests across the three connector files GREEN.
- **A05** — `config/acquisition_sources.v1.yaml`: `saso_documents.expected_content_types` → `[application/pdf, text/html]`; `producer_unicoil.expected_content_types` → `[application/pdf]` — the declared types observed in the stored page contracts of runs `20260912T053622Z` (6 × `application/pdf` + TERMS `text/html`) and `20260912T053955Z` (6 × `application/pdf`). Nothing else in either mapping changed (S11/S12a mappings value-identical per [11]). `tests/test_acquisition_config.py` 246 passed; [11] `CONFIG_1_2_0_AND_RAW_RECORDS_OK`. Records unaffected (`expected_content_types` is not read by the passport or the record builder; [20] re-derives all 12).
- **A07** — candidate identity recomputed with the IAC-6 procedure (slice records excluded) and written into `test_evidence.md` in place of the 200-file figure (below).
- **A01** (accepted, no change) — `data/raw/producer_unicoil/cec488bffcda…/20260912T053955Z/page-0001.payload.pdf.gz` begins with an `HTTP/1.0 200` header block before `%PDF-1.4`; stored as-is under the no-sniffing rule (OD-7); pypdf parses the embedded PDF; the record reconstructs. Recorded in ADR-017; a KL row for HTTP-wrapped bodies would be a new disclosure beyond this round's brief.
- **A04** (accepted, no change) — the twelve `document_url` values and their observed HTTP 200 / `application/pdf` responses are in the hashed lists and stored page contracts; not re-tabulated here.
- **A06** (accepted, no change) — plan T3 test name `test_document_observed_values_must_satisfy_shared_rules` absent; `source_config._validate_source_facts(document=True)` remains covered by `test_live_yaml_loads_without_invented_enums` and adjacent tests.

### Consequential control-record updates (facts only; consequences of OD-10/OD-11, not new scope)

`.workflow/state.json` slice entry: `manifest_runs` 2 → 3, `manifest_recorded_at` + `2026-09-12T06:37:37Z`, `manifest_status`, `seats.implementer` (+ slot 4), `seats.reviewer` (slot 3 REJECT; slot 4 pending), `source_outcomes` (v4 rebuild; KL-56–65). `docs/REQUIREMENTS_TRACEABILITY.md` §N evidence sentence: three manifest runs; REJECT and correction round named. Not edited (outside the brief; flagged for the supervisor): `docs/implementation/ACQUISITION_RUNBOOK.md` line "`-v3` lists and runs … (saso, 6 records)" (still true of the run; the records now reference v4 — KL-55/ADR-017 record that), `docs/BUILD_ROADMAP.md` §s12b status line (already stale since slot 3: "no COMPLETE DocumentRecords").

### T10 regression, gates, OD-10 manifest run, post-generation gates (all commands printed from the plan JSON by `/tmp/s12b_slot4/run_gates.py`; outputs in `test_evidence.md`)

- T10 (06:36:00Z–06:36:19Z): `pytest -q --ignore=tests/test_integrity_contract.py --deselect=tests/test_acquisition_reconstruction.py::test_manifest_lists_gz_payload_paths` → **1871 passed, 1 deselected, 1 warning**.
- Pre-generation [0], [1], [3]–[13], [22]–[26] + corrected [25]: all exit 0 (06:36:26Z–06:37:10Z): `BRANCH_OK`, `PYPDF_PIN_OK`, 29 + 938 tests passed, `PREGEN_RECON_OK` (1/4 + 12/12), `S11_S12A_BYTES_UNCHANGED`, `FROZEN_ROOTS_UNCHANGED`, `BYTE_IDENTICAL_SET_OK`, 42 passed, `SMOKE PASS`, `CONFIG_1_2_0_AND_RAW_RECORDS_OK`, `PYTHON_STANDARDS_OK`, `SCANNERS_OK`, `CORE_05_STATUS_ROWS_OK`, `CORE_03_09_INSERTION_ONLY_OK [['1','0',core03],['2','0',core09]]`, `CORE_04_DOCUMENT_SECTION_OK`, `RUNTIME_AND_DOCUMENT_MODULES_OFFLINE_OK` ×2, `DOCUMENT_TREE_CLEAN 29`.
- **Manifest run 3 (OD-10): `python3 scripts/build_manifests.py` at 2026-09-12T06:37:37Z, exit 0** (the only generator invocation of this round; run count of the slice now 3/3). Before: snapshot manifest `d55aceb3…`, authority hashes `de7a9fd0…`; after: snapshot manifest `4fb8592d1b9d1e67c82d22dc3cd7a90ca9ebfb62d08117a818819858d29764c4` (214 rows; +1 `saso_documents-v4` list row; six SASO record rows re-hashed), authority hashes `79015f4cee58ca3e61b5fd1ce28bc5543c54b0556c899eb1895b66d0835f8364` (only `config/acquisition_sources.v1.yaml`, Core 04 and Core 05 rows changed). §11 mirrored (three rows; scripted check `SECTION_11_MIRROR_OK` over all sixteen rows). **[14] immediately after (06:38:23Z): `MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`, exit 0** — no stop condition.
- Post-generation [14], [15]–[20], [22]–[26] + corrected [25] (06:38:33Z–06:39:46Z): all exit 0; `INTEGRITY PASS`; `SCENARIO VALIDATION PASS (2 scenarios)`; `POSTGEN_RECON_OK` (1/4 + 12/12); **`pytest -q` → 1888 passed, 1 warning** (1878 + 9 record-oracle tests + 1 hook test); `PARTNER_SNAPSHOT_BYTE_IDENTICAL`; `ALL_DOCUMENT_RECORDS_VALIDATE_AND_RECONSTRUCT 12`.
- [21] `UV_OFFLINE=1 make ci`: first pass 06:39:55Z–06:43:19Z exit 0; re-run on the final tree (after the ADR receipt, state.json, traceability, BUILD_PROGRESS edits) 06:46:12Z–06:49:38Z exit 0 — scans PASS, `INTEGRITY PASS`, reconstruction 1/4 + 12/12, 1888 passed, `SMOKE PASS` (Steel public INVESTIGATE; PP public REJECT generic capacity; steel simulated ADVANCE with real state unchanged), `BROWSER PREFLIGHT PASS`, **118 functional passed, 4 visual passed**; `browser_tests/` byte-identical to HEAD (no baseline update). `uv` ran offline (`UV_OFFLINE=1`; the e2e extra was re-installed from the local cache, no download lines). A final `make ci` after the last KL-63 phrase is recorded in `test_evidence.md`.
- Handoff gates re-run on the final tree (06:49:49Z–06:51:11Z): [5], [14], [15], [17], [19], [20], [25] + corrected, [6], [7] all exit 0 (outputs in `test_evidence.md`).

### Changed-file set delta versus candidate `87084ed2…` (verified: HEAD + reviewer's tracked diff re-applied under /tmp and hashed against the tree; untracked files by mtime and by known edits)

- Modified content, tracked (12): `.workflow/state.json`, `config/acquisition_sources.v1.yaml`, `data/manifests/snapshot_manifest.json`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/BUILD_PROGRESS.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/authority/00_AUTHORITY_MANIFEST.md`, `docs/authority/authority_hashes.json`, `docs/core/04_CANONICAL_DATA_MODEL.md`, `docs/core/05_DATA_SOURCES_AND_INGESTION.md`, `tests/test_integrity_contract.py`; the other 25 tracked files of the candidate are byte-identical to it.
- Modified content, untracked (8): the six `data/documents/saso_documents/records/*.json`, `src/ior_mvp/acquisition/connectors/documents.py`, `tests/test_acquisition_document_connectors.py`.
- Added (2): `data/documents/saso_documents/lists/saso_documents-v4.json`, `tests/test_acquisition_document_records.py`. Removed: none. Total 196 files (194 + 2), slice records excluded. `pipeline.py`, `store.py`, `textlayer.py`, `lists.py`, `base.py`, raw partitions, v1–v3 lists, UNICOIL records, browser baselines: unchanged from the candidate.

### Muhasib self-audit (slot 4)

1. Scope: exactly F01, F02, A02, A03, A05, A07 plus the log-only dispositions of A01/A04/A06; the two consequential control-record updates (state.json manifest count/seats; traceability sentence) and the one-phrase KL-63 extension are declared above rather than hidden. Not done: runbook/roadmap wording (flagged).
2. No invention: every count, hash, time and outcome above is copied from command output kept under `/tmp/s12b_slot4/`; the `languages` rule is stated so the reviewer can re-derive it from the records; the reversed Arabic string is not claimed as faithful logical text.
3. Tests: none weakened, skipped or deleted; additive assertions only in `test_s12b_core_v2_document_contracts`; new tests RED before / GREEN after; `test_arabic_cid_pdf_preserves_logical_order_verbatim` untouched.
4. Network: none (no consultation, no acquire; `UV_OFFLINE=1` on every `make`/`uv run`). `.env` not read. No `git add/commit/push/reset/checkout/stash/revert/clean`; index empty at every check. Nothing under `.autonomous-workflow/` edited.
5. Authority: OD-10 (one generator run — done once, 06:37:37Z, [14] PASS), OD-11 (six removals logged with SHA-256 before removal; rebuild from the same run; diff keys verified), OD-12 (disclosure in Core 04/05, ADR, KL) — all followed; the S11/S12a and frozen oracles ([6], [7], [8], [14], [19]) and the two public golden outcomes ([10]/smoke) unchanged.
6. Open for the reviewer: (a) the passport copy `evidence[0].observation_context.languages` also changed (consequence of the languages correction; OD-11 names `list_ref` and `declared.languages`); (b) Core 05 §10 was qualified although it did not literally say "logical order"; (c) `["ar"]` vs `["ar","en"]` is a judgment on Latin-only line content — the counts are tabulated for re-derivation.

## Owner-authorized records follow-up (slot 4, 2026-09-12 ~07:05 UTC)

Owner lead agent authorized exactly the two records edits flagged in the slot-4 self-audit (item 1, "Not done: runbook/roadmap wording"). Pre-check: `python3 -c "import json;print([r['path'] for r in json.load(open('docs/authority/authority_hashes.json'))['files']])"` lists 16 paths (DOCX, seven `config/*.yaml`, `docs/core/01`–`09`); neither `docs/implementation/ACQUISITION_RUNBOOK.md` nor `docs/BUILD_ROADMAP.md` appears — no manifest run needed or performed (count stays 3 of 3).

1. `docs/implementation/ACQUISITION_RUNBOOK.md`, T7-v3 operator-window paragraph: "(saso, 6 records)"/"(unicoil, 6 records)" → "6 COMPLETE units"; appended that the six `saso_documents` DocumentRecords are now built from `saso_documents-v4` against run `20260912T053622Z` (OD-11, same `document_id`s), the six `producer_unicoil` records from `producer_unicoil-v3` against run `20260912T053955Z`, and that v1/v2/v3 lists and all prior runs are retained as history.
2. `docs/BUILD_ROADMAP.md`, §s12b status sentence: replaced the stale "seven `-v2` lists … no COMPLETE DocumentRecords" with the current state — twelve COMPLETE DocumentRecords (six SASO technical regulations from `saso_documents-v4`/`20260912T053622Z`; six UNICOIL disclosures from `producer_unicoil-v3`/`20260912T053955Z`), five sources honest UNAVAILABLE (KL-56–60, verified against `docs/KNOWN_LIMITATIONS.md` rows 88–92), three authorized manifest runs (T11, OD-9, OD-10 — per ADR-017 receipts), uncommitted, independent re-review pending, no PR or merge.

Checks after editing (all with the slot-4 environment prefix): `scripts/verify_integrity.py` → `INTEGRITY PASS` (exit 0); `pytest -q -p no:cacheprovider tests/test_integrity_contract.py tests/test_ci_contract.py` → 34 passed; `git diff --check` → clean (exit 0). No git state change, no network, nothing under `.autonomous-workflow/` touched, no test touched. Candidate identity recomputed below (test_evidence.md identity line updated in place); self-audit item 1 above is superseded by this entry.

Identity after this follow-up: base `cdfd4ba4b016619b7ab33a373d334f22c337166d`, **196 files**, candidate SHA-256 `19d9eea310c1d9b51b1fbb7643809e8352aa520f730a9dc6f42fc79b74039e8c` (index empty; previous `1f8a1f61…`, same file set).

## Owner ruling OR-3 — seat override for the correction round (2026-09-12 07:04Z)

The owner directed that GPT-5.6 Sol performs the correction round and Fable reviews it (`.autonomous-workflow/owner-rulings.md` OR-3, verbatim). The fable follow-up completed at 07:04Z (runbook T7-v3 paragraph and BUILD_ROADMAP status corrected; identity `19d9eea310c1d9b51b1fbb7643809e8352aa520f730a9dc6f42fc79b74039e8c`, 196 files). Residual stale statement found by the owner lead agent: `docs/implementation/ACQUISITION_RUNBOOK.md` line 91 still says "S12b manifest run count must be **2** … no third run authorized" although OD-10 authorized and slot 4 performed the third run (06:37:37Z). Slot 5 (`implementer-sol`) takes ownership of the final candidate: fixes that statement, re-verifies the whole candidate against plan-1, IAC-1…13, reviewer findings F01/F02 and advisories A01–A07, and corrects any residual defect it finds in non-hashed files; no manifest run remains (3 of 3), so any authority-hashed file change must STOP for owner direction. Independent review of slot 5 by a fresh Fable reviewer session (OR-3), disclosing that slot-4 content shares the reviewer's model.

## Slot 5 (`implementer-sol`, OR-3) — sweep result and owner decision OD-13 (2026-09-12 ~07:35Z)

`implementer-sol` (gpt-5.6-sol-max, agent ba905239) re-verified the plan hash and identity (`19d9eea3…`, 196 files), opened every untracked artifact and stopped before any mutation with three findings that require hashed-file changes: (a) all twelve records' per-page `text_sha256` is computed over the JSON array of lines, not `sha256("\n".join(lines))` as DD-5 specifies (`textlayer.py:61-66`); (b) `textlayer.py:151-153` drops empty-text pages and re-indexes later pages — `DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b` records 14 pages for a 21-page PDF, breaking stable page addressing; (c) `store.py:363` always supplies `superseded_run_ids = ()`, omitting actual superseded runs in two SASO and six UNICOIL records. Owner lead agent adjudication: all three VALID (HIGH). OD-13 authorizes the test-first code fixes, offline rebuild of all twelve records from the stored runs, the corresponding governed-text corrections and a fourth, final manifest run. Same seat continues.

## Slot 5 OD-13 correction — pre-removal record receipt (2026-09-12)

Data classification: public publisher documents and repository test doubles only; no restricted data, credentials or `.env` access. Persona: senior data-provenance/acquisition-pipeline implementer. The new DD-5/DD-11 tests were observed RED before implementation: newline-joined page hash, physical PDF page retention with an empty middle page, exact CR/LF segmentation, non-whitespace COMPLETE decision and latest-run supersession. Residual plan-contract tests were also observed RED for exact document-source nested mappings, DocumentList entry ordering, DocumentList-aware minimum requests, `build-documents --data-root`, exact HTML suppression/block tags, ISO list dates and strict nested record keys; the exact plan-named `test_document_observed_values_must_satisfy_shared_rules` was added.

Before the OD-13-authorized removal, `sha256sum` returned:

| Record path | Pre-removal SHA-256 |
|---|---|
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9.json` | `9efcfd44ba8285f5e3eeeeeea8be36f2a327148d68733a85f24de20d00439627` |
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661.json` | `8a13c45199c20306a8bd59fb334ee66ae725a8ef90d6a02be1d95479c44f920c` |
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54.json` | `960781a5b43e7e0f5a835d1a04079745c2d478ed34cc046a2c5b393288735a62` |
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d.json` | `a11bc449f670d4a0b3cb6d06759d923bcba4a8b5f166ef9b8b597d0c1e09634d` |
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b.json` | `2de95461a23837469a5084f5a3e9b8a5a429177ce923be90a1355452b99a2606` |
| `data/documents/saso_documents/records/DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf.json` | `74e2fb0ad13cb9404a78bfad2adb88211944b421f983cf2dff5bd511f2d429ec` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-70151205e3a4-1762d53d6cab.json` | `ff379b5d9f7762c5818b846fa8e1dedd68e893e928b3f9db918370ed5217c3b9` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0.json` | `6d831e2e70d91f9ec06cefbb9144aca1e3598a319e4fc55a7d70063c71f75823` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a.json` | `be2040749a64530e99fce84a7d580795b5a9a1993409fff2843cc38e4b3d076e` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-cec488bffcda-3017de71d962.json` | `de3657b0b4d1b4f413f22dc380e645d81983fc4c9eb35cd201b231aa5d7273dd` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-d7302a241f7d-f35cfd06f777.json` | `f2554778fed52f853d08b735f674eb364274c173c0b274cf05ee905ca855875d` |
| `data/documents/producer_unicoil/records/DOC-PRODUCER-UNICOIL-ecb55cc26093-612efea9a835.json` | `a4d98a378c303dcca8834bda36a468895d371cfbc33582af7b9d4fa681c8d02e` |

The filename stems equal the twelve stored `document_id` values; this set is the post-rebuild identity oracle. Only these twelve derived record files are authorized for removal. Raw runs, attempts, coverage and lists remain untouched.

## Slot 5 OD-13 final implementation record (2026-09-12 07:30–07:39 UTC)

Test-first corrections and residual sweep:

- `src/ior_mvp/acquisition/documents/textlayer.py` — implemented DD-5 CR/LF-only segmentation, newline-joined page hashes, exact HTML block/suppression contract, physical PDF-page retention including empty pages, non-whitespace availability, and typed parser-error detail.
- `src/ior_mvp/acquisition/documents/store.py` — emits/validates every derived page, exact nested record keys and physical indexes; selects `RawStore.latest_runs` per DOCUMENT unit and records sorted actual superseded run ids.
- `src/ior_mvp/acquisition/documents/lists.py` — deterministic `entry_id` ordering and strict ISO `recorded_on`.
- `src/ior_mvp/acquisition/source_config.py` — exact nested key sets for document sources.
- `src/ior_mvp/acquisition/pipeline.py` — passes the DocumentList into `_run_units` so every entry contributes to the minimum request bound; aggregate-count logic unchanged.
- `src/ior_mvp/acquisition/cli.py` — interprets `build-documents --data-root` as the data root while retaining acquire-command raw-root semantics.
- `tests/test_acquisition_document_textlayer.py` — RED/GREEN page-hash, empty physical page, exact separator, non-whitespace and HTML suppression/block-tag tests; no Arabic CID semantic weakening.
- `tests/test_acquisition_document_store.py` — RED/GREEN latest/superseded selection, no-text physical-page record, request-minimum and strict nested-schema tests.
- `tests/test_acquisition_document_lists.py` — RED/GREEN entry ordering and ISO-date tests.
- `tests/test_acquisition_config.py` — exact plan-named `test_document_observed_values_must_satisfy_shared_rules` plus RED/GREEN document nested-key probes.
- `tests/test_acquisition_document_cli.py` — RED/GREEN build-document data-root contract and corrected document CLI arguments.
- All twelve `data/documents/{saso_documents,producer_unicoil}/records/*.json` files — OD-13-authorized offline rebuild from unchanged stored raw runs. Document ids are unchanged; current pages use physical PDF page numbering and newline-joined hashes; two SASO and all six UNICOIL records carry the actual prior run ids.
- `docs/core/04_CANONICAL_DATA_MODEL.md`, `docs/core/05_DATA_SOURCES_AND_INGESTION.md` — additive DD-5/DD-11 physical-page/hash/status/latest-run contract corrections.
- `docs/ARCHITECTURE_DECISIONS.md` — OD-13 rationale, residual corrections and four-run receipt.
- `docs/KNOWN_LIMITATIONS.md` — corrected current COMPLETE-record state, record-rebuild history and narrowed KL-65 pipeline wording.
- `docs/implementation/ACQUISITION_RUNBOOK.md` — replaced the stale two-run/no-third statement with the truthful four-run record.
- `docs/BUILD_PROGRESS.md`, `docs/BUILD_ROADMAP.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `.workflow/state.json` — current slot-5 ownership, rebuilt-record state, reviewer status and four-run history.
- `data/manifests/snapshot_manifest.json`, `docs/authority/authority_hashes.json` — generated, never hand-edited, by the fourth and final OD-13 run.
- `docs/authority/00_AUTHORITY_MANIFEST.md` §11 — Core 04/05 rows mirrored from the generated authority JSON.
- `.workflow/slices/S12b-document-store-disclosures-tenders/{implementation_log.md,test_evidence.md}` — append-only receipts, test outputs and handoff evidence.

Manifest receipt: run 4/4 started and ended `2026-09-12T07:30:41Z`, exit 0. §11 mirror followed; immediate [14] and post-generation [14] both returned `MANIFEST_S11_S12A_ROWS_UNCHANGED_DOCUMENTS_PRESENT`. Earlier runs remain T11 `05:26:47Z`, OD-9 `05:43:02Z`, OD-10 `06:37:37Z`. No fifth run is authorized or performed.

Verification: T10 `1904 passed, 1 deselected`; full `[18]` `1921 passed, 1 warning`; `[5]`/`[17]` reconstruct 1 snapshot/4 artifacts and 12 documents/12 artifacts; `[15]` integrity PASS; `[19]` partner snapshot byte-identical; `[20]` all 12 document records validate/passport/reconstruct; corrected `[25]` offline import gate PASS; `[26]` 29-file document tree clean; offline `make ci` exit 0 with 118 functional and 4 visual browser nodes. Plan [2] was owner-directed skipped; no baselines were updated.

Strict implementation self-review: no open defect found in the slot-5 diff after exact-contract, failure-path, provenance, generated-delta and stale-text inspection. Assumptions are limited to the governing records: OD-13 permits replacement of these twelve uncommitted derived records and exactly one fourth generator run; existing publisher-byte parser diagnostics are already disclosed limitations and are not reconstruction failures. No network, `.env`, staging, commit, push, destructive Git command, raw-run/list edit or `.autonomous-workflow/` edit occurred.

## Independent review of candidate 94eb2f4e… — REJECT (Fable reviewer under OR-3, 2026-09-12 ~08:00Z)

Reviewer (claude-fable-5-1-thinking-max, agent d0bf51da; disclosure: same model as the slot-4 implementer session, different session, authored nothing in the tree) recomputed the identity (match, start and end), ran every plan gate except [2]/[21], `pytest -q` (1921 passed), integrity, scenarios, smoke (frozen outcomes exact), independently verified all twelve records (schema, DOCUMENT_ID_V1, raw hashes, pypdf physical page counts incl. 21/21 with seven empty pages retained, `sha256("\n".join(lines))`, sorted superseded runs, byte-exact reconstruction, complete passports, truthful languages, zero Arabic presentation forms), the manifest/§11/raw-partition consistency (214 rows; 141 document/raw files all listed), lists v1–v4, budgets (store 24,988,157 B; max artifact 7,118,151 B), byte identity of every frozen path, and cross-process determinism on two real PDFs. Verdict **REJECT**: S12B-IR5-F01 (MEDIUM) HTML text layer not the literal DD-5 algorithm and untested by exact lines; S12B-IR5-F02 (LOW) DD-10 path-segment validation unimplemented. Ten advisories A01–A10. Record `.autonomous-workflow/evidence/s12b-document-store-disclosures-tenders/implementation-review-slot-5.json`. Owner lead agent `make ci` on this tree: exit 0 (1921 tests; 118 functional + 4 visual). Adjudication and corrections: OD-14; `implementer-sol` continues.

## Slot 5 OD-14 correction (`implementer-sol`, 2026-09-12T08:23:45Z)

Data classification remains public publisher documents and repository test doubles only. Persona remains senior data-provenance/acquisition-pipeline implementer. OD-14 adjudicated F01/F02 VALID and directed the listed advisory treatment. No network, `.env`, Git state-changing command, `.autonomous-workflow/**` edit, authority-hashed edit, `data/**` edit or manifest run occurred.

### Test-first findings and correction

- **F01 RED:** the exact fixture pin and three literal probes failed against the reviewed implementation. The hand-derived DD-5 tuples were table `("", "", "", "a", "", "b", "", "")`, nested block `("", "", "a", "")`, and list `("", "", "one", "", "two", "")`. The fixture pin includes the exact line `"العربية paragraph with U+200F\u200f marker"`. RED command: focused pytest over the fixture/probe and F02 tests; result 6 failed. The HTML derivation output changed because the old block-join algorithm was wrong; no stored record uses HTML derivation.
- **F01 GREEN:** `_HTMLTextExtractor` now appends `"\n"` literally at each start and end callback for every `BLOCK_TAGS` member (including `td`, `th` and `br` callbacks), appends all other unsuppressed character data verbatim, and discards data while inside `script`, `style`, `template` or `noscript`; `LINE_SEGMENTATION_V1` runs once over the joined character stream. Exact fixture/probe and subprocess-determinism tests pass.
- **F02 RED:** `DocumentStore.list_path`/`record_path` accepted unsafe segments, `acquire_documents(list_id="../evil")` reached a filesystem read, and both document CLI commands called `_deps` before rejecting the list id. The first focused run failed the store/pipeline cases; the dedicated CLI preflight run failed both parametrized cases.
- **F02 GREEN:** `validate_list_id` applies `^[a-z0-9][a-z0-9_-]{2,79}$`; `DocumentStore` applies raw-store `_PATH_UNSAFE` semantics to each source/list/document segment; pipeline entry points validate before constructing paths; CLI validates before `_deps`, so invalid IDs cause argparse exit 2 before config/raw-store/transport setup. Focused document suite: 74 passed.

### Changed files versus reviewed candidate `94eb2f4e…`

- `src/ior_mvp/acquisition/documents/textlayer.py` — literal DD-5 HTML boundary/data/suppression algorithm.
- `src/ior_mvp/acquisition/documents/store.py` — DD-10 list-id and source/list/document path-segment validation.
- `src/ior_mvp/acquisition/pipeline.py` — list-id preflight before document acquisition/build filesystem access.
- `src/ior_mvp/acquisition/cli.py` — list-id preflight before `_deps` and any CLI dependency I/O.
- `tests/test_acquisition_document_textlayer.py` — exact fixture tuple (including U+200F), hand-derived table/nested/list tuples, and HTML subprocess determinism.
- `tests/test_acquisition_document_lists.py` — invalid list-id/source/document path rejection assertions.
- `tests/test_acquisition_document_store.py` — invalid pipeline list-id rejection with zero FakeTransport calls.
- `tests/test_acquisition_document_cli.py` — acquire/build CLI rejection before `_deps`.
- `Makefile` — `acquire-documents` and `build-documents` added to `.PHONY` (A05).
- `docs/ARCHITECTURE_DECISIONS.md` — stale T7 statement corrected (A06); OD-14 F01/F02 and A01–A04/A08–A10 accepted observations recorded; A08 records the DOCUMENT-only reserved-token carve-out.
- `docs/KNOWN_LIMITATIONS.md` — KL-66 names the HTTP-wrapped UNICOIL document and its byte-exact/no-sniffing behavior (A07).
- This append-only slice log and `test_evidence.md` — correction and verification receipts; excluded from IAC-6.

### Advisory dispositions

A05–A07 were corrected as directed. A08 is documented precisely in ADR-017 rather than changing proven connector behavior. A01–A04, A09 and A10 are recorded as accepted observations in ADR-017/KL-66; A04 preserves DocumentRecord 1.0.0 empty-page `lines: []`, and A10 remains unchanged because config is authority-hashed. No Core file changed.

### Verification and immutable-byte receipt

All plan gates [0], [1], [3]–[20], [22]–[26] and corrected [25] passed; [2] was owner-directed skipped under mandatory `UV_OFFLINE=1`. Full pytest: **1928 passed, 1 warning**. Offline `make ci`: exit 0, the same 1928 tests, smoke/goldens PASS, browser preflight PASS, 118 functional and 4 visual tests passed; no baselines updated. A read-only oracle compared all 233 protected paths (all `data/**`, every authority-hash path, all Core files and both manifests) to candidate `94eb2f4e…` or its unchanged HEAD base and returned `PROTECTED_BYTE_IDENTICAL`. Manifest count remains **4/4** at `05:26:47Z`, `05:43:02Z`, `06:37:37Z`, `07:30:41Z`; no fifth run.

Final IAC-6: base `cdfd4ba4b016619b7ab33a373d334f22c337166d`, slice records excluded, **SHA-256 `5258e7d4dbc144d940792dcd57981e29d6faa1a301056fb9b26be0a00f3f674b`, 196 files, index empty**.

## Owner acceptance and delivery (owner lead agent, 2026-09-12 ~08:45Z)

Final independent review (Fable reviewer session, OR-3): APPROVE, zero findings, on candidate `5258e7d4dbc144d940792dcd57981e29d6faa1a301056fb9b26be0a00f3f674b` (196 files). Owner lead agent: identity recomputed (match; index empty); `make ci` on the identical tree exit 0 (1928 tests; 118 functional + 4 visual; integrity; reconstruction 1/4 + 12/12; smoke exact). OD-15 recorded. Staging: 204 paths (196 identity + 8 slice-record files) selectively staged; fail-closed prohibited-file/secret scan PASS (727 tracked files); `.env` and `.autonomous-workflow/` untouched. `git diff --cached --check` reports trailing whitespace only in the hand-authored PDF fixtures (xref entries are 20 bytes ending in SPACE+EOL by the PDF specification), the CRLF plain-text fixture (`\r` is the fixture's purpose) and two Markdown hard line breaks in `test_evidence.md`; none is a CI gate and none is altered.
