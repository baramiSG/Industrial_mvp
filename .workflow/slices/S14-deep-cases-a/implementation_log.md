# Implementation log — S14a case selection, evidence and families

## 2026-09-12T23:00:36Z — Orientation and governed stance

- Seat: `implementer-sol`, slot 1.
- Discipline persona: senior data/evidence engineer for deterministic industrial-decision pipelines, holding a strict public-evidence, reproducibility, and fail-closed acquisition stance.
- Data classification: `confidential_demo`; public official/statistical/corporate evidence and labelled test doubles only. No personal, Ministry-private, paid, or credential data. `.env` is not read.
- Authority precedence applied: OD-1…OD-11 > AM-1 > approved base plan > decomposition read-through. Independent plan review is `APPROVE`; IAC-1…IAC-7 and all reviewer advisories are binding.
- OD-11 implementation: a canonical hashed `identity_exclusions` data row for `392190` / `RESIDUAL_CATCH_ALL_SUBHEADING`; the rule is re-run. No flag and no hand edit. Expected ruled plastics output is `392010`, runner-up `391739`; `760429` remains selectable.
- Execution environment outside T4 windows: `UV_OFFLINE=1`, `PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc`, `PATH=.venv/bin:$PATH`, `PYTHONPATH=src`.
- Network boundary: no network before T4. Each T4 consultation/acquisition window will be logged before execution. TLS verification, robots directives, access walls, and licence gates will not be bypassed.
- Git boundary: read-only Git inspection only; no add, commit, stash, checkout, reset, clean, or other Git-state mutation. Candidate stops unstaged and uncommitted.
- Manifest generator invocation count: `0`.

### T0 verification commands (recorded before execution)

```bash
test "$(git branch --show-current)" = slice/s14a-case-selection-evidence-and-families &&
git merge-base --is-ancestor ab6211f86307ad95a0e61f0597664023f09b7177 HEAD &&
test "$(git rev-parse HEAD)" = ab6211f86307ad95a0e61f0597664023f09b7177 &&
echo BRANCH_OK
git status --short
git diff --cached --quiet && echo INDEX_EMPTY_PASS
```

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
```

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

```bash
PYTHONPATH=src python3 scripts/demo_smoke.py
```

```bash
PYTHONPATH=src python3 scripts/validate_scenarios.py
```

```bash
PYTHONPATH=src pytest --collect-only -q
```

```bash
PYTHONPATH=src python3 -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']))"
```

```bash
for r in data/snapshots/public data/synthetic data/golden browser_tests/baselines; do
  printf '%s %s\n' "$r" "$(git rev-parse "HEAD:$r")"
done
```

### Authoritative methodology orientation command (recorded before execution)

`ReadFile` cannot decode DOCX. The following read-only command extracts text directly from the authoritative DOCX package; it writes nothing:

```bash
PYTHONPATH=src python3 - <<'PY'
from docx import Document
document = Document("docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx")
for paragraph in document.paragraphs:
    if paragraph.text.strip():
        print(paragraph.style.name, paragraph.text)
PY
```

Outcome: authoritative DOCX text extracted successfully from `word/document.xml` (1,264 non-empty paragraphs/table rows). The governing clauses directly confirmed for this slice are: unresolved product identity cannot advance; public fields require attached evidence spans; H5/H6 revisions are not silently spliced; R1-D is a three-positive-year degraded signal; technical-plastics and fabricated-aluminium profile gates are fixed; `U` cannot improve adjacency; no action/brownfield precede greenfield; acquisition evidence must be frozen, hashed, and reproducible; public worked outcomes remain steel `INVESTIGATE` and generic polypropylene capacity support `REJECT`.

## 2026-09-12T23:01:49Z — T0 baseline results

- Branch/base: `BRANCH_OK`; branch `slice/s14a-case-selection-evidence-and-families`; HEAD/base `ab6211f86307ad95a0e61f0597664023f09b7177`.
- Working tree before product implementation: only `?? .workflow/slices/S14-deep-cases-a/`; index empty.
- `INTEGRITY PASS`.
- Reconstruction:
  - `RECONSTRUCTION PASS (2 snapshots, 20 artifacts)`
  - `DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)`
  - `ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)`
  - `SCREENING RECONSTRUCTION PASS (1 snapshots)`
- `SMOKE PASS`; steel public `INVESTIGATE`, steel simulated `ADVANCE` with unchanged real state, polypropylene public `REJECT`.
- `SCENARIO VALIDATION PASS (2 scenarios)`.
- `2275 tests collected in 1.34s`.
- `VISUAL_MANIFEST_OK 56`.
- Frozen OIDs match the approved plan: public `2ad27d6e…`, synthetic `3fb2247a…`, golden `72618db6…`, browser baselines `c2b3b66b…`.
- BF-18(a) confirmed: entity mention code verifies a verbatim DocumentRecord line substring at `{document_id,page_index,line_index}` and is reusable by contract, though the case brief validator will use a smaller direct verifier.
- BF-18(b) confirmed: WITS PARTNERS planning accepts an explicit arbitrary six-digit `hs6_codes` tuple; no two-code cap.
- BF-18(c) confirmed: `tests/test_offline_guard.py` already checks runtime acquisition transport isolation and can be extended for `ior_mvp.cases`.
- BF-18(d) confirmed: raw budgets are configuration-driven and tested; the ledger sizes are leads only and will be checked against compressed stored artifacts before/after each window.
- No `.env` read; no network used.
- T0: COMPLETE.

## 2026-09-12T23:05:56Z — T1a RED: deterministic case selection

Tests were authored before production code. They cover profile-union membership, PR-7/warning tiers, positive-latest-weight viability, source-restricted disclosure coverage, ordered keys, profile quota/substitution, write-once canonical output, no-candidate refusal, OD-11 identity exclusion before quota, the non-generic term schema, and the ruled real-snapshot output.

RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_case_selection.py
```

T1b GREEN result: `14 passed in 0.63s`.

Ruled selection output:

```text
CASE SELECTION PASS (5 selected; 3 profiles; 4 families)
coated_steel: 721061, 721012 (runner-up 721069; 5 substitutes; 3 viability exclusions; 0 identity exclusions; 1 frozen exclusions)
fabricated_aluminium: 760711, 760429 (runner-up 761610; 22 substitutes; 4 viability exclusions; 0 identity exclusions; 0 frozen exclusions)
technical_plastics: 392010 (runner-up 391739; 36 substitutes; 0 viability exclusions; 1 identity exclusions; 1 frozen exclusions)
```

Input hashes: screening inventory `231b8c3c999f3b69fea9c45d38c2dfc93d1a1e9faccef0e735658aa4adab06cc`; universe `758acdb41c5759e5be2c6215405e9c6829bc527b73850d8c4b54327c61b0c78d`; product families `79a201e3db89bec20cf18acedc759ba1e038932d96f6f12ce03362bab22c51ff`; terms `a8e385cce354d7ad6ea9a19e3884be4d2ebdd3ec5be9ea90c80e306d99ee6dde`; identity exclusions `8bfdd55090e949fc1ca6810a5a87da67b92ff8897955221cb2f46ebaaf6d8430`; referenced producer documents inventory `45be1d0e99460c9648c114f5dc8c4e1156759fedce52cd7893940f508d419023`.

Recorded file: `CASE-SELECTION-S14-ca2a6321a1df.json`, SHA-256 `9c47e360565530a59c4eb137e9e3d02046846b77b1cffd44c5bbc890fe5045c8`.

T1b: COMPLETE.

## 2026-09-12T23:21:00Z — T3 retained acquisition config

Mechanical exact-byte copy command (recorded before execution):

```bash
python3 -c "from pathlib import Path; source=Path('config/acquisition_sources.v1.yaml'); target=Path('config/history/acquisition_sources.v1-1.3.0.yaml'); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())"
sha256sum config/history/acquisition_sources.v1-1.3.0.yaml
```

Expected SHA-256: `fbe061496bc6c9b5ddd039b25536d78fb24c22ba3d84650fcd2c9374977673cc`.

Real-snapshot RED result: `1 failed, 12 passed`; the one remaining failure is the expected absent governed term table (`FileNotFoundError: data/cases/selection/hs6-disclosure-terms-v1.json`).

CLI RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_case_selection.py::test_select_cli_writes_canonical_record_and_reports_profiles
```

CLI RED result: `1 failed` for the expected absent `ior_mvp.cases.cli`.

CLI GREEN result after implementing the offline parser/writer: `1 passed in 0.03s`.

T1a status: selection functions, canonical writer, OD-11 data-driven exclusion path, and offline `select` CLI are implemented; `12` rule/doubles tests plus the CLI test pass. The real-snapshot pin remains RED by approved ordering.

## 2026-09-12T23:09:00Z — T2 RED: families and retained inputs

The superseded product-family bytes were copied first to `config/history/product_families.v1-1.0.0.yaml`.

History-byte verification command (recorded before execution):

```bash
sha256sum config/history/product_families.v1-1.0.0.yaml
```

Expected: `841bc5ac732b9f9348495d3594926dea84dd4df7aab134092f81d06b4de7ecd4`.

T2 RED commands will be recorded after the tests are authored and before execution.

History-byte result: exact expected SHA-256 `841bc5ac732b9f9348495d3594926dea84dd4df7aab134092f81d06b4de7ecd4`.

T2 RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q \
  tests/test_screening_config.py \
  tests/test_screening_snapshot.py::test_check_inputs_passes_when_live_config_matches \
  tests/test_screening_snapshot.py::test_check_inputs_resolves_superseded_config_from_history_by_content_hash \
  tests/test_screening_snapshot.py::test_check_inputs_rejects_unknown_hash_even_with_history_present \
  tests/test_screening_snapshot.py::test_history_resolution_never_applies_to_data_inputs \
  tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only
```

T2 RED result: `12 failed, 7 passed`; failures were exactly the absent 1.1.0 family semantics and absent `resolve_recorded_input`.

T2 GREEN result: `19 passed in 0.06s`.

T2 reconstruction and threshold-scan commands (recorded before execution):

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

```bash
python3 scripts/check_threshold_literals.py
```

First T2 oracle run exposed two expected pre-manifest integration gaps:

- reconstruction stopped at the stale manifest row for the live product-family config before history resolution;
- the threshold scanner rejected an HS4 length literal in the new selection module.

Corrections: screening manifest verification now resolves a changed `config/` input against the retained bytes by the recorded hash before comparison; non-config inputs retain the old direct path rule. The HS4 check now uses a structural regex. Re-run threshold result: `THRESHOLD LITERAL SCAN PASS (75 Python files; 23 configured numeric values)`.

## 2026-09-12T23:13:00Z — T1b ruled real-snapshot run

The governed selection rule files are now authored:

- `hs6-disclosure-terms-v1.json`: one source-restricted, product-specific row for every 78 in-family screening HS6; titles remain explicitly `TITLE_VERIFICATION: UNAVAILABLE` except two pre-existing stored UNICOIL title matches.
- `identity-exclusions-v1.json`: OD-11 row `392190 / RESIDUAL_CATCH_ALL_SUBHEADING`; no flag and no hand-edited output.

Selection commands (recorded before execution):

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out /tmp/ior-s14a-select-1
```

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out /tmp/ior-s14a-select-2
```

```bash
sha256sum /tmp/ior-s14a-select-1/CASE-SELECTION-S14-*.json /tmp/ior-s14a-select-2/CASE-SELECTION-S14-*.json
```

Initial execution failed closed because five manually authored term arrays were not casefold-sorted. A diagnostic enumerated only rows `391710`, `392020`, `392030`, `392111`, and `392112`; those arrays were reordered without changing content. Both full re-runs then passed with identical file SHA-256 `9c47e360565530a59c4eb137e9e3d02046846b77b1cffd44c5bbc890fe5045c8`.

Recorded-output command (recorded before execution):

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out data/cases/selection
```

RED result: `13 failed`; every test failed for the expected missing feature (`ModuleNotFoundError: No module named 'ior_mvp.cases'`).

T1a doubles GREEN command (recorded before execution; the real-snapshot pin remains intentionally RED until T2/T1b):

```bash
PYTHONPATH=src pytest -q tests/test_case_selection.py -k "not frozen_screening_snapshot"
```

Intermediate T1a corrections: the first doubles run exposed two test-fixture defects (unordered helper rows; missing ruled 3917 membership) and one over-broad fixture term that covered every steel row. The fixtures were corrected without weakening assertions.

GREEN result: `12 passed, 1 deselected in 0.03s`.

Real-snapshot RED command (recorded before execution; expected to fail because T2/T1b governed files do not yet exist):

```bash
PYTHONPATH=src pytest -q tests/test_case_selection.py
```

Outcome: exit `1`, `ModuleNotFoundError: No module named 'docx'`. No package installation or network was attempted.

Fallback read-only command (recorded before execution) uses only the standard library and reads the authoritative `word/document.xml`, including table paragraphs:

```bash
PYTHONPATH=src python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

path = Path("docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx")
with ZipFile(path) as archive:
    root = ET.fromstring(archive.read("word/document.xml"))
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
for paragraph in root.findall(".//w:p", ns):
    text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
    if text:
        print(text)
PY
```

## 2026-09-12T23:20:01Z — Chronological clarification and T1b GREEN command

Clarification without deleting prior record text: the `python-docx` import failure and standard-library DOCX fallback belong to the initial orientation section. The T1 sequence was full RED (`13` missing-package failures), doubles GREEN (`12` plus one deselected real test), real-pin RED (missing governed table), CLI RED/GREEN, then the ruled T1b runs above. T2 completed between T1a and T1b as AM-1 requires.

T2 reconstruction re-run completed exit `0`:

```text
RECONSTRUCTION PASS (2 snapshots, 20 artifacts)
DOCUMENT RECONSTRUCTION PASS (12 records, 12 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

T1b full GREEN command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_case_selection.py
```

T1b GREEN result: `14 passed in 0.63s`.

T3 retained acquisition config SHA-256 matched the exact superseded bytes:
`fbe061496bc6c9b5ddd039b25536d78fb24c22ba3d84650fcd2c9374977673cc`.

## 2026-09-12T23:23:00Z — T3 RED: source and DocumentList contracts

T3 RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_document_lists.py
```

T3 RED result: `263 failed, 53 passed`; the exact-set/version guard rejected the missing five source contracts, lists, publisher kind, support mapping, and connector registrations before any network use.

T3 GREEN result after the minimum governed implementation: `316 passed in 4.67s`.

The current source set adds exactly four producer sources plus `wco_hs_nomenclature`; each producer v1 list contains only ledger-observed URLs. The WCO list remains intentionally absent until T4 reads the index hrefs verbatim.

T3 offline reconstruction/budget commands (recorded before execution):

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

```bash
PYTHONPATH=src pytest -q tests/test_acquisition_size_budget.py
```

T3 results: reconstruction exit `0` with the unchanged four baseline PASS lines; size budget `1 passed in 0.04s`.

## 2026-09-12T23:27:00Z — T4 W-A/W-P consultation-only window (recorded before execution)

- Explicit live intent: `IOR_ACQUISITION_LIVE=1` for this bounded consultation command only.
- Purpose: read current robots directives, identify linked terms pages, obtain WCO Chapter 39/72/76 hrefs verbatim, and inspect ALUPCO download hrefs before any `acquire-*` command.
- Request ceiling: 12 consultation GETs; no retries; default verified TLS; 60-second timeout; response bodies held in memory only and discarded.
- URLs, in order:
  1. `https://www.wcoomd.org/robots.txt`
  2. `https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition/hs-nomenclature-2022-edition.aspx`
  3. `https://hadeed.com.sa/robots.txt`
  4. `https://hadeed.com.sa/`
  5. `https://alupco.com/robots.txt`
  6. `https://alupco.com/downloads/`
  7. `https://altaiseer.com/robots.txt`
  8. `https://altaiseer.com/en/%d8%aa%d8%a7%d9%84%d9%83%d9%88-%d9%81%d9%8a-%d8%b3%d8%b7%d9%88%d8%b1/`
  9. `https://www.maaden.com/robots.txt`
  10. `https://www.maaden.com/news-insights/latest-news/maaden-fourth-quarter-and-full-year-2025-results`
  11. `https://axvpvthrjz64.compat.objectstorage.me-jeddah-1.oraclecloud.com/robots.txt`
  12. `https://wits.worldbank.org/robots.txt`
- `www.rajhisteel.com` is not requested.
- Parser output: status/final URL/content type/bytes/SHA-256; plaintext robots lines; terms/legal/privacy/copyright links; WCO chapter links; ALUPCO PDF links. No body is stored.

Consultation command (recorded before execution):

```bash
IOR_ACQUISITION_LIVE=1 PYTHONPATH=src python3 - <<'PY'
# urllib with the system default verified TLS context; one GET per recorded URL;
# HTMLParser emits only governed link candidates and no response body.
PY
```

### 2026-09-12T23:28:00Z — Consultation facts recorded before acquisition

- WCO: robots `200 text/plain`, 316 bytes, SHA-256 `0370725d…`; twelve disallows cover Sitecore/app/temp/upload/search internals only, not the index or `/-/media/` paths. Index `200 text/html`, 136,138 bytes, SHA-256 `5cb88ba0…`; linked `WCO standard terms and conditions - Council Decision n° 331` at `/en/about-us/legal-instruments/wco-standard-terms-and-conditions_council-decision-n331.aspx`. The first parser predicate emitted no chapter hrefs, so no Chapter 39/72 URL is treated as observed yet.
- Hadeed: `/robots.txt` returned `200 text/html` (site shell, 64,331 bytes), not a robots policy; root `200 text/html`, 64,291 bytes; no terms link observed. No disallow rule or wall was observed for the listed catalogue path.
- ALUPCO: robots `200 text/plain`, disallow `/wp-admin/` only and allow `admin-ajax.php`; `/downloads/` returned HTTP `500`, 15,723 bytes. No PDF href or terms link was obtained. The already-listed `/about/` path is not disallowed; no download PDF is added.
- Al Taiseer/TALCO: robots `200 text/plain` with empty `Disallow`; target page `200 text/html`, 166,208 bytes; no terms link observed.
- Ma'aden site: robots `200 text/plain`, `Allow: /`, disallow `/api/` and `/_next/`; results page `200 text/html`, 482,007 bytes and links `/terms-and-conditions` plus `/privacy-policy`. Neither target path is disallowed.
- Ma'aden object storage: `/robots.txt` returned `404 application/xml`, 219 bytes; no robots rules or terms link observed.
- WITS: robots `200 text/plain`, empty general `Disallow` plus `/cgi-bin/`; planned PARTNERS path is not disallowed.
- No TLS verification was disabled; no login/purchase wall was observed; no request to Rajhi Steel occurred.

### W-A-C1 corrective/terms consultation (recorded before execution)

Reason: the one completed WCO index consultation established access but the in-memory extraction predicate emitted no chapter hrefs. A bounded corrective read is required to avoid guessing Chapter 39/72 URLs. This is disclosed as a second index request, not hidden as the original single-read plan.

- Explicit live intent: `IOR_ACQUISITION_LIVE=1`.
- Request ceiling: four GETs, no retries, default verified TLS, response bodies held only in memory:
  1. WCO standard terms page observed above;
  2. Ma'aden terms page observed above;
  3. World Bank dataset terms already named by the governed WITS source contract;
  4. WCO index corrective read, emitting every HS-2022 PDF href with nearby anchor text.
- No acquisition command runs until these facts are appended.

```bash
IOR_ACQUISITION_LIVE=1 PYTHONPATH=src python3 - <<'PY'
# Four exact GETs as listed; status/type/bytes/hash and bounded terms/PDF-link
# text only are printed. Default verified TLS; no body is stored.
PY
```

### 2026-09-12T23:30:00Z — Terms facts and W-A acquisition parameters recorded before execution

- WCO standard-terms page: `200 text/html`, 42,223 bytes, SHA-256 `be6a31b4…`; page identifies `Copyright World Customs Organization`. A terms URL is therefore observed and `license_capture_required=true`; the acquired TERMS response will be stored before the three documents.
- WCO corrective index read: `200`, byte/hash identical to the first read. Verbatim index hrefs resolve to Chapter 39 `0739_2022e.pdf?la=en`, Chapter 72 `1572_2022e.pdf?la=en`, and Chapter 76 `1576_2022e.pdf?la=en`. `wco_hs_nomenclature-v1` contains exactly those three entries.
- Ma'aden terms page: `200 text/html`, 323,440 bytes, SHA-256 `0437796b…`; the observed URL is configured and `license_capture_required=true`.
- World Bank terms URL redirected to `https://www.worldbank.org/ext/en/legal/terms-conditions`, `200 text/html`, 46,882 bytes, SHA-256 `89ac4970…`; text incorporates dataset-specific terms and limits non-commercial use with attribution. The existing WITS source contract remains terms-gated.

Per-source W-A parameters and rationale:

| Source | List | Entries | MAX_REQUESTS | Terms | Rationale |
|---|---|---:|---:|---|---|
| `wco_hs_nomenclature` | `wco_hs_nomenclature-v1` | 3 | 4 | captured first | Three owner-ruled identity chapters plus one observed terms request. |
| `producer_hadeed` | `producer_hadeed-v1` | 1 | 1 | UNAVAILABLE; no link observed | One ledger-observed catalogue; target path not disallowed. |
| `producer_alupco` | `producer_alupco-v1` | 1 | 1 | UNAVAILABLE; no link observed | `/downloads/` is HTTP 500, so only the ledger-observed `/about/` entry is attempted. |
| `producer_altaiseer_talco` | `producer_altaiseer_talco-v1` | 1 | 1 | UNAVAILABLE; no link observed | One ledger-observed public profile page; robots allows all. |
| `producer_maaden` | `producer_maaden-v1` | 2 | 3 | captured first | One report and one results page plus the observed publisher terms request. |

Every command uses verified TLS and the source-configured two-second minimum interval; no retries beyond connector policy and request budget. Any non-200, envelope mismatch, wall, or size refusal remains typed `UNAVAILABLE`.

W-A acquisition/build commands (recorded before execution):

```bash
IOR_ACQUISITION_LIVE=1 make acquire-documents SOURCE=wco_hs_nomenclature LIST_ID=wco_hs_nomenclature-v1 MAX_REQUESTS=4
make build-documents SOURCE=wco_hs_nomenclature LIST_ID=wco_hs_nomenclature-v1
```

```bash
IOR_ACQUISITION_LIVE=1 make acquire-documents SOURCE=producer_hadeed LIST_ID=producer_hadeed-v1 MAX_REQUESTS=1
make build-documents SOURCE=producer_hadeed LIST_ID=producer_hadeed-v1
```

```bash
IOR_ACQUISITION_LIVE=1 make acquire-documents SOURCE=producer_alupco LIST_ID=producer_alupco-v1 MAX_REQUESTS=1
make build-documents SOURCE=producer_alupco LIST_ID=producer_alupco-v1
```

```bash
IOR_ACQUISITION_LIVE=1 make acquire-documents SOURCE=producer_altaiseer_talco LIST_ID=producer_altaiseer_talco-v1 MAX_REQUESTS=1
make build-documents SOURCE=producer_altaiseer_talco LIST_ID=producer_altaiseer_talco-v1
```

```bash
IOR_ACQUISITION_LIVE=1 make acquire-documents SOURCE=producer_maaden LIST_ID=producer_maaden-v1 MAX_REQUESTS=3
make build-documents SOURCE=producer_maaden LIST_ID=producer_maaden-v1
```

### W-A RunReport — `wco_hs_nomenclature` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wco_hs_nomenclature/53d6f01ac0627b9cab0f1468634e00c587d7d0ed897035abc03da3541673aad4/20260912T233006Z/page-0001.payload.pdf.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wco_hs_nomenclature/5530bdf97060af4b3ce52384db361a790245636ef316e02319ecc2cec3d1c72e/20260912T233006Z/page-0001.payload.pdf.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wco_hs_nomenclature/69bd7323c7aa1880a0872bc8da166ac85a0c25f2068a945b44250e6d7b033b6b/20260912T233006Z/page-0001.payload.pdf.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "53d6f01ac0627b9cab0f1468634e00c587d7d0ed897035abc03da3541673aad4",
      "requests_made": 2,
      "run_id": "20260912T233006Z",
      "source_id": "wco_hs_nomenclature",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/0739_2022e.pdf?la=en"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/0739_2022e.pdf?la=en\"]]"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "5530bdf97060af4b3ce52384db361a790245636ef316e02319ecc2cec3d1c72e",
      "requests_made": 3,
      "run_id": "20260912T233006Z",
      "source_id": "wco_hs_nomenclature",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/1572_2022e.pdf?la=en"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/1572_2022e.pdf?la=en\"]]"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "69bd7323c7aa1880a0872bc8da166ac85a0c25f2068a945b44250e6d7b033b6b",
      "requests_made": 4,
      "run_id": "20260912T233006Z",
      "source_id": "wco_hs_nomenclature",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/1576_2022e.pdf?la=en"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://www.wcoomd.org/-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/1576_2022e.pdf?la=en\"]]"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [],
  "max_requests": 4,
  "requests_made": 9,
  "run_id": "20260912T233006Z",
  "source_id": "wco_hs_nomenclature",
  "stage": "DOCUMENT",
  "unavailable": [],
  "years": []
}
```

Interpretation: three document units COMPLETE; actual transport budget use was four (one TERMS plus three PDFs). `requests_made: 9` is the pre-existing cumulative-coverage aggregate artefact documented by KL-65, not nine transport calls.

WCO offline build report: built
`DOC-WCO-HS-NOMENCLATURE-53d6f01ac062-0926bf9934da`,
`DOC-WCO-HS-NOMENCLATURE-5530bdf97060-8da42b5156a2`, and
`DOC-WCO-HS-NOMENCLATURE-69bd7323c7aa-bd350605a78a`; no unavailable unit.

### W-A RunReport — `producer_hadeed` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/producer_hadeed/92ca24b2076fb16f30a350e505f7ae96551b00ca1b39aa7dc29dab7dc10d4180/20260912T233102Z/page-0001.payload.pdf.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "92ca24b2076fb16f30a350e505f7ae96551b00ca1b39aa7dc29dab7dc10d4180",
      "requests_made": 1,
      "run_id": "20260912T233102Z",
      "source_id": "producer_hadeed",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://hadeed.com.sa/pdf/product-catalouge.pdf"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://hadeed.com.sa/pdf/product-catalouge.pdf\"]]"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [],
  "max_requests": 1,
  "requests_made": 1,
  "run_id": "20260912T233102Z",
  "source_id": "producer_hadeed",
  "stage": "DOCUMENT",
  "unavailable": [],
  "years": []
}
```

Hadeed offline build report: built
`DOC-PRODUCER-HADEED-92ca24b2076f-253eed8b773e`; no unavailable unit.

### W-A RunReport — `producer_alupco` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/producer_alupco/135870d0e4c778d93fbb4ec9feea28d3478288179aabc157070acc6db7cf6f62/20260912T233130Z/page-0001.payload.html.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "135870d0e4c778d93fbb4ec9feea28d3478288179aabc157070acc6db7cf6f62",
      "requests_made": 1,
      "run_id": "20260912T233130Z",
      "source_id": "producer_alupco",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://alupco.com/about/"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://alupco.com/about/\"]]"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [],
  "max_requests": 1,
  "requests_made": 1,
  "run_id": "20260912T233130Z",
  "source_id": "producer_alupco",
  "stage": "DOCUMENT",
  "unavailable": [],
  "years": []
}
```

ALUPCO offline build report: built
`DOC-PRODUCER-ALUPCO-135870d0e4c7-0261d54ca8a6`; no unavailable unit.

### W-A RunReport — `producer_altaiseer_talco` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/producer_altaiseer_talco/b68e0eef2440c5f2050fd2a6a939a123790bd196164fdc862c5a5509dbf29d03/20260912T233154Z/page-0001.payload.html.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "b68e0eef2440c5f2050fd2a6a939a123790bd196164fdc862c5a5509dbf29d03",
      "requests_made": 1,
      "run_id": "20260912T233154Z",
      "source_id": "producer_altaiseer_talco",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://altaiseer.com/en/%d8%aa%d8%a7%d9%84%d9%83%d9%88-%d9%81%d9%8a-%d8%b3%d8%b7%d9%88%d8%b1/"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://altaiseer.com/en/%d8%aa%d8%a7%d9%84%d9%83%d9%88-%d9%81%d9%8a-%d8%b3%d8%b7%d9%88%d8%b1/\"]]"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [],
  "max_requests": 1,
  "requests_made": 1,
  "run_id": "20260912T233154Z",
  "source_id": "producer_altaiseer_talco",
  "stage": "DOCUMENT",
  "unavailable": [],
  "years": []
}
```

TALCO offline build report: built
`DOC-PRODUCER-ALTAISEER-TALCO-b68e0eef2440-b339b1ac8d87`; no unavailable unit.

### W-A RunReport — `producer_maaden` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/producer_maaden/b1dd369ea0fe25bd8ea590cda7c2f450d0abecfad242c5454f1bc1e449b0cb86/20260912T233222Z/page-0001.payload.pdf.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/producer_maaden/a48b1f95cba905046d71a8b0066fce0d189dfcae19bcaedfbb41fa34d80bd04a/20260912T233222Z/page-0001.payload.html.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "b1dd369ea0fe25bd8ea590cda7c2f450d0abecfad242c5454f1bc1e449b0cb86",
      "requests_made": 2,
      "run_id": "20260912T233222Z",
      "source_id": "producer_maaden",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://axvpvthrjz64.compat.objectstorage.me-jeddah-1.oraclecloud.com/maaden-website-assets/reports/annual-reports/maaden-ar-updated-ver---mar-26-eng-ver_compressed.pdf"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://axvpvthrjz64.compat.objectstorage.me-jeddah-1.oraclecloud.com/maaden-website-assets/reports/annual-reports/maaden-ar-updated-ver---mar-26-eng-ver_compressed.pdf\"]]"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "a48b1f95cba905046d71a8b0066fce0d189dfcae19bcaedfbb41fa34d80bd04a",
      "requests_made": 3,
      "run_id": "20260912T233222Z",
      "source_id": "producer_maaden",
      "stage": "DOCUMENT",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "parameters": {
          "document_url": "https://www.maaden.com/news-insights/latest-news/maaden-fourth-quarter-and-full-year-2025-results"
        },
        "period": null,
        "stage": "DOCUMENT"
      },
      "unit_key": [
        "[[\"document_url\",\"https://www.maaden.com/news-insights/latest-news/maaden-fourth-quarter-and-full-year-2025-results\"]]"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [],
  "max_requests": 3,
  "requests_made": 5,
  "run_id": "20260912T233222Z",
  "source_id": "producer_maaden",
  "stage": "DOCUMENT",
  "unavailable": [],
  "years": []
}
```

Interpretation: two document units COMPLETE; actual transport budget use was three (one TERMS plus two documents). `requests_made: 5` is the known cumulative-coverage aggregate artefact.

Ma'aden offline build report: built
`DOC-PRODUCER-MAADEN-b1dd369ea0fe-dae44e050e70` and
`DOC-PRODUCER-MAADEN-a48b1f95cba9-956b9a16c655`; no unavailable unit.

## 2026-09-12T23:33:00Z — T4 W-T TLS observation (recorded before execution)

- Purpose: the single owner-ruled verified-TLS re-test for Tasnee and SPIMACO; observation only, no document acquisition.
- Explicit live intent: `IOR_ACQUISITION_LIVE=1`.
- Requests: exactly one HTTPS GET each to `https://www.tasnee.com/robots.txt` and `https://www.spimaco.com.sa/robots.txt`; no retry.
- TLS: Python system default context; no custom CA, no `verify=False`, no warning suppression; 60-second timeout; bodies discarded.
- Output: default verify paths followed by status/final URL/content type/bytes/peer certificate subject+issuer, or the verbatim verification error.

```bash
PYTHONPATH=src python3 -c "import ssl; print(ssl.get_default_verify_paths())"
IOR_ACQUISITION_LIVE=1 PYTHONPATH=src python3 - <<'PY'
# one verified urllib GET per recorded URL; no retry or bypass
PY
```

W-T verbatim result:

```text
DefaultVerifyPaths(cafile=None, capath='/etc/ssl/certs', openssl_cafile_env='SSL_CERT_FILE', openssl_cafile='/etc/ssl/cert.pem', openssl_capath_env='SSL_CERT_DIR', openssl_capath='/etc/ssl/certs')
TLS_OBSERVATION URL=https://www.tasnee.com/robots.txt STATUS=NO_RESPONSE ERROR=URLError:<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)>
TLS_OBSERVATION URL=https://www.spimaco.com.sa/robots.txt STATUS=NO_RESPONSE ERROR=URLError:<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)>
```

Both sources are `UNAVAILABLE / TLS_CERTIFICATE_VERIFY_FAILED` from this environment. Verification was not disabled and neither host was retried.

## 2026-09-12T23:34:00Z — T4 W-P WITS partner window (recorded before execution)

- Source: `wits_trade`; candidate file: `data/cases/selection/wits-partners-s14-v1.json`.
- Candidate codes (sorted ruled selection): `392010`, `721012`, `721061`, `760429`, `760711`.
- Period: `2024`; flow: `imports`; `MAX_REQUESTS=6` (one configured terms request plus five HS6 units).
- Robots fact: WITS robots `200 text/plain`; no general disallow and only `/cgi-bin/` disallowed. The planned `/trade/comtrade/` paths are not disallowed.
- Terms fact: the configured World Bank terms URL returned `200` after the recorded redirect; use is terms-gated and attributed.
- Explicit live intent: `IOR_ACQUISITION_LIVE=1`; no credential is read; verified TLS; no retry around HTTP errors.
- Fallback: any HTTP or coverage failure is retained as typed `UNAVAILABLE`; no partner snapshot is fabricated.

```bash
IOR_ACQUISITION_LIVE=1 make acquire-partners \
  SOURCE=wits_trade \
  CANDIDATES=data/cases/selection/wits-partners-s14-v1.json \
  YEARS=2024 \
  FLOWS=imports \
  MAX_REQUESTS=6
```

Offline follow-up commands (recorded before execution):

```bash
make build-snapshots KIND=partners SOURCE=wits_trade
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
```

### W-P RunReport — `wits_trade` (verbatim)

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wits_trade/73fee7942370a560970adeadd1a36777ef35bd5d645b935439038e4e8011068b/20260912T233403Z/page-0001.payload.html.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wits_trade/ac22708082e052fb156814e1c6e66ec24a6e6b6d9f7561383c6b31d1a549b371/20260912T233403Z/page-0001.payload.html.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wits_trade/ed5759a33b4ffc375ef1f3aba6a46d0f5dc076247dc16a3bfdc883a9c04e311e/20260912T233403Z/page-0001.payload.html.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wits_trade/9b2c9a2e52352e2bcb9165f51cbcf51325003e0de03a46961bc1e73079f3b2f4/20260912T233403Z/page-0001.payload.html.gz",
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/wits_trade/a407b8cd2b1dc0193cc1ae193bcba797abf02d53fc5b79c8f3919d8dd5ffd383/20260912T233403Z/page-0001.payload.html.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "73fee7942370a560970adeadd1a36777ef35bd5d645b935439038e4e8011068b",
      "requests_made": 2,
      "run_id": "20260912T233403Z",
      "source_id": "wits_trade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "392010",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "392010",
        "imports",
        "2024"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "ac22708082e052fb156814e1c6e66ec24a6e6b6d9f7561383c6b31d1a549b371",
      "requests_made": 3,
      "run_id": "20260912T233403Z",
      "source_id": "wits_trade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "721012",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "721012",
        "imports",
        "2024"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "ed5759a33b4ffc375ef1f3aba6a46d0f5dc076247dc16a3bfdc883a9c04e311e",
      "requests_made": 4,
      "run_id": "20260912T233403Z",
      "source_id": "wits_trade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "721061",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "721061",
        "imports",
        "2024"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "9b2c9a2e52352e2bcb9165f51cbcf51325003e0de03a46961bc1e73079f3b2f4",
      "requests_made": 5,
      "run_id": "20260912T233403Z",
      "source_id": "wits_trade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "760429",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "760429",
        "imports",
        "2024"
      ]
    },
    {
      "completeness_basis": "SINGLE_RESPONSE_NO_PAGINATION",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "a407b8cd2b1dc0193cc1ae193bcba797abf02d53fc5b79c8f3919d8dd5ffd383",
      "requests_made": 6,
      "run_id": "20260912T233403Z",
      "source_id": "wits_trade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "760711",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "760711",
        "imports",
        "2024"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [
    "imports"
  ],
  "max_requests": 6,
  "requests_made": 20,
  "run_id": "20260912T233403Z",
  "source_id": "wits_trade",
  "stage": "PARTNERS",
  "unavailable": [],
  "years": [
    2024
  ]
}
```

Interpretation: all five partner units COMPLETE; actual transport budget use was six (one TERMS plus five data requests). `requests_made: 20` is the known cumulative-coverage aggregate artefact, not twenty transport calls.

W-P offline build result: exit `2`; `AcquisitionUnavailable: FORMAT_NOT_PARSEABLE`.
The five returned HTML pages are retained as public raw evidence but do not become normalized partner rows or a new partner snapshot. The build was not retried or worked around. `partner_snapshot_id` therefore remains `UNAVAILABLE` for every S14a brief; R3/R4-D partner paths remain `NOT_CALCULABLE`.

T4 offline verification commands (recorded before execution):

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
```

The no-check-manifest switch is used only before the one T9 manifest generation, because new write-once T4 paths are not yet enumerated. It does not bypass input/hash reconstruction.

```bash
PYTHONPATH=src pytest -q tests/test_acquisition_size_budget.py tests/test_acquisition_document_records.py
```

```bash
PYTHONPATH=src python3 - <<'PY'
# Read stored T4 page contracts and DocumentRecords; print source, run,
# HTTP status, content type, byte count, SHA-256 and record identity.
PY
```

The first pre-manifest reconstruction failed honestly:

```text
RECONSTRUCTION FAIL: PARTNERS-SAU-WITS-TRADE-2026-09-03 (SELECTION_CHANGED)
```

Root-cause evidence: four new WITS units are `COMPLETE/NORMALIZED`; `721061` returned HTTP 200 only after redirect to `Error.aspx`, 1,891 bytes, and is `COMPLETE/UNPARSED`. The generic partner builder treated that unit as transport-complete and failed the entire at-least-one snapshot; the historical reconstruction path also compared the 2026-09-03 snapshot to the latest run set instead of its recorded run IDs. Existing historical snapshots must remain byte-reconstructible while newer snapshots are retained.

Regression RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q \
  tests/test_acquisition_snapshots.py::test_partner_snapshot_excludes_complete_transport_unit_with_unparsed_page \
  tests/test_acquisition_snapshots.py::test_pinned_reconstruction_keeps_historical_snapshot_reproducible
```

Regression RED: two expected failures (at-least-one builder rejected an `UNPARSED` transport-complete unit; `reconstruct_pinned` absent). GREEN after the bounded fix: `2 passed in 0.05s`.

The fix preserves existing `reconstruct()` and its `SELECTION_CHANGED` oracle, adds a separate pinned historical reconstruction path for the release script, and converts transport-complete but `PENDING/UNPARSED` units to derived `INCOMPLETE / FORMAT_NOT_PARSEABLE` exclusions only for `AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS` kinds. The new WITS snapshot then built as `PARTNERS-SAU-WITS-TRADE-2026-09-12.json`; 721061 is the sole excluded unit. No network was retried.

Pre-manifest reconstruction GREEN:

```text
RECONSTRUCTION PASS (3 snapshots, 32 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (1 artifacts, 38 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

WCO verified identity spans were located in the three COMPLETE records. The technical-plastics family basis, OD-11 exclusion basis, and selected-HS6 term rows now cite the exact stored page/line addresses.

The previously recorded uncommitted selection `CASE-SELECTION-S14-ca2a6321a1df.json` (SHA-256 `9c47e360565530a59c4eb137e9e3d02046846b77b1cffd44c5bbc890fe5045c8`) predates those WCO provenance updates. Per the approved pre-commit correction rule, it will be removed and the rule rerun; selected codes may not be hand edited.

Corrected selection commands (recorded before execution):

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out /tmp/ior-s14a-select-final-1
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out /tmp/ior-s14a-select-final-2
sha256sum /tmp/ior-s14a-select-final-{1,2}/CASE-SELECTION-S14-*.json
```

After equal hashes:

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out data/cases/selection
```

Corrected selection runs were byte-identical. Final record:
`CASE-SELECTION-S14-250cd516de0a.json`, SHA-256
`19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016`.
Final input hashes: product families `62fa9c2944474ffbc5952801ba676a2adf750870a88969c59e22337b4564446b`;
terms `27b97683ab41c75dc90ce9224db9f561d9c5f62ddc27fa581444f39e1b3f918f`;
identity exclusions `5e18dd7a5573610d6d02909cf9f6e792646de61650d1a6d7c5eb37a9308941c6`;
screening/universe/referenced-document inventory hashes unchanged. Selected and runner-up codes are unchanged.

T4 stored evidence totals: eight new COMPLETE DocumentRecords (WCO 3, Hadeed 1, ALUPCO 1, TALCO 1, Ma'aden 2); five normalized WITS partner responses minus one derived `FORMAT_NOT_PARSEABLE` exclusion; one new partner snapshot. Compressed raw store is `41,673,354` bytes across 65 artifacts; largest compressed artifact `9,837,279` bytes, within both governed budgets.

## 2026-09-12T23:40:00Z — T5 RED: producer mentions v2

RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_entity_resolution_artifact.py::test_s14_mentions_v2_spans_verified_and_second_artifact_reconstructs
```

T5 RED result: one expected failure because `mentions-v2.json` did not exist.

The authored list contains nine verbatim spans: four producer company/publisher names and five named site localities. It contains no personal/contact fields. Only Hadeed/Jubail is within the frozen locality and subject-window rules; all other plant links are allowed to remain pending/unresolved.

Build and GREEN commands (recorded before execution):

```bash
PYTHONPATH=src python3 -m ior_mvp.acquisition build-entities --mention-list-id mentions-v2
```

```bash
PYTHONPATH=src pytest -q tests/test_entity_resolution_artifact.py::test_s14_mentions_v2_spans_verified_and_second_artifact_reconstructs
```

The first build refused M-009 because its subject was in a different Ma'aden document. The next build exposed that out-of-window site labels with no existing plant candidate cannot form a valid pending link. Before any artifact existed, the list was corrected to six spans: four publisher/company names, exact Hadeed `Al-Jubail` within the two-line subject window, and same-line Ma'aden/Ras Al-Khair (honestly unresolved because the locality is outside the frozen table). ALUPCO/TALCO site labels were omitted with the reason recorded in the list, not forced.

Final build report:

```text
artifact_id: ENTITIES-2026-09-13-bebc9d15cbf1
entities: COMPANY 4, PLANT 1, LINE 0, LICENCE_HOLDER 0
links: EXACT_DOCUMENT_EVIDENCE 5, UNRESOLVED 1
passport links: EXACT_DOCUMENT_EVIDENCE 4, UNRESOLVED 16
```

T5 GREEN: `1 passed in 0.07s`.

## 2026-09-12T23:44:00Z — T6 RED: CaseBrief and PublicSnapshot derivation

RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q \
  tests/test_case_brief.py \
  tests/test_case_projection.py \
  tests/test_case_briefs_real.py \
  tests/test_offline_guard.py::test_runtime_app_does_not_import_cases_package
```

T6 RED: `25 failed, 1 passed`; every production test failed for the absent brief/projection modules or absent real briefs, while the runtime import-boundary test already passed.

Unit contract GREEN after implementation and two fixture corrections: `21 passed in 0.05s`. The validator refuses unsupported document support codes, non-verbatim spans, non-`U` dimensions without spans, numeric nameplates without spans, resolved gates without spans, authored decision keys, and synthetic markers.

Five real CaseBriefs were authored for exactly `392010`, `721012`, `721061`, `760429`, and `760711`. Initial real validation/build determinism: `1 passed in 1.10s`.

Engine observation command (recorded before any state assertion):

```bash
PYTHONPATH=src python3 - <<'PY'
# Load each brief, build in memory, evaluate rules and capability, then print
# opportunity id, state, route, decision_reason_code and fired rule ids.
# No assertion or input mutation occurs in this observation command.
PY
```

Observed engine proofs:

```text
SAU-H6-392010 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R4-D,R12
SAU-H6-721012 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R4-D,R12
SAU-H6-721061 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R12
SAU-H6-760429 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R3,R4-D,R5,R9-S,R10,R12
SAU-H6-760711 INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED R0,R1-D,R2,R12
```

No SC-2b stop triggered. Assertions then passed: `4 passed in 2.59s`.

Case CLI RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_case_brief.py::test_case_cli_validates_and_builds_to_explicit_output
```

CLI RED: one expected parser failure (`validate-brief` absent). GREEN: `1 passed in 0.02s`.

Temporary build commands (recorded before execution):

```bash
for brief in data/cases/briefs/CASE-BRIEF-*.json; do
  PYTHONPATH=src python3 -m ior_mvp.cases validate-brief --brief "$brief"
  PYTHONPATH=src python3 -m ior_mvp.cases build --brief "$brief" --out /tmp/ior-s14a-build
done
sha256sum /tmp/ior-s14a-build/PUBLIC-SAU-H6-*.json
```

T6 GREEN commands (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_case_brief.py tests/test_case_projection.py tests/test_case_briefs_real.py tests/test_offline_guard.py
```

```bash
PYTHONPATH=src python3 scripts/check_threshold_literals.py
```

Temporary case-build hashes:

```text
056b693e15675e68123fb10cc4b5581415fc04ea80c0a16954744e07aaf68d1b  PUBLIC-SAU-H6-392010-2026-09-12.json
8e999b08a2086c5807a14a8732d6aed8ec214f1a3ce40e98a19437789a814999  PUBLIC-SAU-H6-721012-2026-09-12.json
93f7f713d637fc1f1daae11fd26a8305bdebbdceed4418e06df0498728022fc7  PUBLIC-SAU-H6-721061-2026-09-12.json
eddb302dc1e70b0231d940cee5cb670871c5533663a43beea4209a234803e3d2  PUBLIC-SAU-H6-760429-2026-09-12.json
669fc1b117782ae16c5eec090989837f21e77602b0bbf441207f7e67158d294a  PUBLIC-SAU-H6-760711-2026-09-12.json
```

All five files exist only under `/tmp/ior-s14a-build`; no portfolio root was touched.

T6 suite GREEN: `30 passed in 2.92s`. Initial threshold scan identified only an ISO-date slice-length literal; it was replaced by a structural constant. Re-run: `THRESHOLD LITERAL SCAN PASS (78 Python files; 23 configured numeric values)`.

## 2026-09-12T23:50:00Z — T7 RED: manifest roots and case reconstruction

RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q \
  tests/test_integrity_contract.py::test_build_manifests_includes_cases_root_and_config_history \
  tests/test_integrity_contract.py::test_reconstruct_script_prints_case_reconstruction_pass_line
```

T7 RED: two expected failures for absent manifest-root enumeration and absent case reconstruction function. GREEN after implementation: `2 passed in 0.56s`.

Make/CLI verification commands (recorded before execution):

```bash
make validate-briefs
make cases-reconstruct
```

```bash
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
```

T7 Make targets validated all five briefs and printed
`CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)`.
The complete pre-manifest reconstruction passed:

```text
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (3 snapshots, 32 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
```

## 2026-09-12T23:53:00Z — T8 RED: authority contracts

RED command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_integrity_contract.py::test_s14a_core_v2_case_contracts
```

T8 RED: one expected missing-contract failure at `CaseBrief 1.0.0`. Core
02/04/05/09, ADR-021, KL-90…KL-99, the S14 split, runbook, progress,
traceability and machine state were then updated before any manifest run.
Focused Core GREEN: `1 passed in 0.02s`.

T8 control verification commands (recorded before execution):

```bash
PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path
state=json.loads(Path(".workflow/state.json").read_text(encoding="utf-8"))
assert state["milestones"]["v0.3.0"]["split"]["s14"]["state"] == "IN_PROGRESS"
assert state["milestones"]["v0.3.0"]["current_slice"] == "s14a-case-selection-evidence-and-families"
print("STATE_JSON_VALID_PASS")
PY
```

```bash
PYTHONPATH=src pytest -q \
  tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only \
  tests/test_integrity_contract.py::test_build_manifests_includes_cases_root_and_config_history \
  tests/test_integrity_contract.py::test_reconstruct_script_prints_case_reconstruction_pass_line \
  tests/test_integrity_contract.py::test_s14a_core_v2_case_contracts
```

```bash
PYTHONPATH=src pytest -q --ignore=tests/test_integrity_contract.py
```

Pre-manifest broad regression result: `19 failed, 2329 passed, 1 warning`.
One failure is the expected stale raw-manifest inventory before T9. The other
18 exposed compatibility assertions: two old registry inventories, six
all-unparseable reason-code regressions, two repository tests using the
latest-selection diagnostic instead of pinned historical reconstruction,
three stored-source inventories, one exact reconstruction-output list, and
four screening-authority fixtures still pinned to product families 1.0.0.
No domain input or outcome was changed to resolve them.

Compatibility rerun command (recorded before execution; only the expected
pre-manifest inventory assertion is deselected):

```bash
PYTHONPATH=src pytest -q --ignore=tests/test_integrity_contract.py \
  -k "not manifest_lists_gz_payload_paths"
```

Compatibility GREEN: `2347 passed, 1 deselected, 1 warning in 31.82s`.

## 2026-09-13T00:22:00Z — T9 pre-generation gate

Manifest generator invocation count remains `0`.

Pre-generation integrity-contract command (recorded before execution):

```bash
PYTHONPATH=src pytest -q tests/test_integrity_contract.py
```

This run may fail only on stale generated manifest/Manifest §11 rows. Any
other failure is corrected before the single generator invocation.

First integrity-contract run exposed one exact Core 05 table expectation that
had not admitted the additive S14 source rows. The expected list was extended
without removing any prior row. Full pre-generation integrity contracts then
passed: `25 passed in 0.88s`.

Remaining pre-generation commands (all recorded before execution):

```bash
PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path
snapshot=json.loads(Path("data/manifests/snapshot_manifest.json").read_text())
authority=json.loads(Path("docs/authority/authority_hashes.json").read_text())
print("MANIFEST_ROWS_BEFORE", len(snapshot["files"]), len(authority["files"]))
print("AUTHORITY_PATHS_BEFORE", *sorted(row["path"] for row in authority["files"]))
PY
```

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
```

Expected before generation: authorized hash/missing-row failures only.

```bash
python3 scripts/check_prohibited_files.py
python3 scripts/check_threshold_literals.py
PYTHONPATH=src python3 scripts/validate_scenarios.py
PYTHONPATH=src python3 scripts/demo_smoke.py
```

```bash
PYTHONPATH=src pytest -q
```

```bash
test "$(git branch --show-current)" = slice/s14a-case-selection-evidence-and-families &&
test "$(git rev-parse HEAD)" = ab6211f86307ad95a0e61f0597664023f09b7177 &&
git diff --cached --quiet &&
echo PRE_MANIFEST_BRANCH_INDEX_PASS
```

```bash
git diff --stat ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  data/snapshots/public data/synthetic data/golden browser_tests \
  'src/ior_mvp/*.py' src/ior_mvp/static config/project.yaml \
  config/thresholds.v1.yaml config/sector_profiles.v1.yaml \
  config/evidence_policy.v1.yaml config/ui_strings.v1.yaml \
  config/decision_narratives.v1.yaml config/entity_resolution.v1.yaml \
  config/screening.v1.yaml data/screening data/snapshots/universe \
  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json \
  data/entities/mentions/mentions-v1.json \
  data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json \
  .github/workflows/ci.yml Dockerfile pyproject.toml uv.lock \
  tests/conftest.py tests/test_frozen_public_evidence_pins.py \
  tests/test_golden_cases.py docs/core/01_PRODUCT_AND_REQUIREMENTS.md \
  docs/core/03_SYSTEM_ARCHITECTURE.md \
  docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md \
  docs/core/07_DETERMINISTIC_ENGINE_SPEC.md \
  docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md
git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests
echo PROTECTED_SET_EXPECT_NO_PATHS_ABOVE
```

```bash
PYTHONPATH=src python3 -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']))"
PYTHONPATH=src python3 -m ior_mvp.screening validate --check-inputs
```

```bash
PYTHONPATH=src python3 - <<'PY'
from ior_mvp.decision_engine import analyze
s=analyze("SAU-H0-721049","public"); p=analyze("SAU-H0-390210","public")
assert s["real_decision"]["state"]=="INVESTIGATE" and s["real_decision"]["route_code"] is None and s["preferred_hypothesis"]["route_code"]==5
assert p["real_decision"]["state"]=="REJECT" and p["real_decision"]["route_code"]==0
print("FROZEN_OUTCOMES_OK")
PY
```

```bash
rg -n "/home/" data/cases data/documents/*/lists config/history
rg -l "SAU-H6-390220" data/cases config docs/core src tests
echo PORTABLE_TEXT_EXPECT_NO_PATHS_ABOVE
```

Pre-generation results:

- manifest rows before: snapshot `535`, authority `19`; authority path set is
  unchanged;
- integrity failed only on the six authorized configuration/Core hashes;
- prohibited, threshold, scenario, smoke, branch/index, visual, screening and
  frozen-outcome gates passed;
- full pytest: `2372 passed, 1 failed, 1 warning`; the only failure is the
  expected stale raw-manifest inventory;
- the first protected command used Git's ordinary wildcard pathspec, which
  also matched nested subpackages and therefore printed seven authorized
  acquisition/screening files. This was a pathspec diagnostic defect, not a
  top-level-module change;
- the first `/home/` scan matched the public URL
  `https://saber.sa/home/aboutsaber`, not a filesystem path.

Corrected protected/portability commands (recorded before execution):

```bash
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  data/snapshots/public data/synthetic data/golden browser_tests \
  ':(glob)src/ior_mvp/*.py' src/ior_mvp/static config/project.yaml \
  config/thresholds.v1.yaml config/sector_profiles.v1.yaml \
  config/evidence_policy.v1.yaml config/ui_strings.v1.yaml \
  config/decision_narratives.v1.yaml config/entity_resolution.v1.yaml \
  config/screening.v1.yaml data/screening data/snapshots/universe \
  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json \
  data/entities/mentions/mentions-v1.json \
  data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json \
  .github/workflows/ci.yml Dockerfile pyproject.toml uv.lock \
  tests/conftest.py tests/test_frozen_public_evidence_pins.py \
  tests/test_golden_cases.py docs/core/01_PRODUCT_AND_REQUIREMENTS.md \
  docs/core/03_SYSTEM_ARCHITECTURE.md \
  docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md \
  docs/core/07_DETERMINISTIC_ENGINE_SPEC.md \
  docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md)" &&
test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)" &&
echo PROTECTED_SET_BYTE_IDENTICAL_PASS
```

## 2026-09-13T02:28:00Z — AM-3 Manifest Case C

ADR-021 contains the Case C receipt before invocation. This is exactly the
third and last S14a manifest generator run. Commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/build_manifests.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py
```

The immediate oracle compares every manifest row present at base
`ab6211f86307ad95a0e61f0597664023f09b7177` byte-for-byte and compares the
base authority path set. No further manifest invocation is permitted.

Case C result: generator and integrity exited 0; the corrected read-only oracle
reported `PREEXISTING_ROWS_UNCHANGED_PASS 535`,
`AUTHORITY_PATH_SET_UNCHANGED_PASS 19`, and `MANIFEST_ROWS_AFTER 628`.

Final proof: full pytest `2416 passed, 1 warning`; `make ci` exit 0 with 2416
pytest, 152 functional browser and 4 visual browser tests; copied-tree
integrity/reconstruction `PORTABILITY_AM3_PASS` with 4 acquired snapshots /
34 artifacts. Final canonical identity against base ab6211f, excluding both
S14 record folders:
`78c9b0c6c0085cdc89e303d159a56041b5923fd720b64637ff6829c5009fc6cb`,
153 files. Index empty; frozen roots and top-level modules unchanged.

## 2026-09-13T02:10:00Z — OD-18 RED/GREEN and corrected V3 window

The first dry-run-only assertion was discarded because tokenization with
`shlex.split` does not execute shell control operators and therefore passed
without proving the defect. The replacement unit test executes the Make recipe
with a local argv-capture double. RED proved the capture received only
`partner_dimension_query=` (`1 failed`). The Make recipe now quotes
`"$(PARAMETERS)"`; GREEN proved the CLI receives
`partner_dimension_query=&includeDesc=true`, the QueryContract retains that
exact tuple and the built URL ends in `&includeDesc=true` (`1 passed`).

Corrected W-C parameters and fix are recorded before execution:

- one corrected V3 data request for sole HS6 721061, plus one governed TERMS
  capture; `MAX_REQUESTS=2`; no further request under any outcome;
- `PARAMETERS='partner_dimension_query=&includeDesc=true'`, now protected by
  Make double quotes; partnerCode omitted, no V2 or all-token;
- existing robots HTTP 404/no-directives receipt and UN Comtrade policy/terms
  receipts carried forward; verified TLS required;
- key sourced inside the command only, never printed/read/stored; configured
  denylist and echo refusal remain active;
- defective repeated-V1 unit
  `e71395bb…/20260913T014942Z` remains write-once and will be listed as an
  attempt, described as variant-not-transmitted without inventing a new enum.

Command recorded before execution:

```bash
set -a; . ./.env; set +a; IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-partners SOURCE=un_comtrade CANDIDATES=data/cases/selection/comtrade-partners-s14-v1.json YEARS=2024 FLOWS=imports MAX_REQUESTS=2 PARAMETERS='partner_dimension_query=&includeDesc=true'
```

Corrected V3 RunReport (verbatim):

```json
{
  "artifacts": [
    "/home/barami/projects/industrial-opportunity-resolution-mvp/data/raw/un_comtrade/050a03afdc481f7f720589c24600401ae40aaa77abc534d1a7b0aaf4bff60174/20260913T015620Z/page-0001.payload.json.gz"
  ],
  "coverage": [
    {
      "completeness_basis": "PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "050a03afdc481f7f720589c24600401ae40aaa77abc534d1a7b0aaf4bff60174",
      "requests_made": 2,
      "run_id": "20260913T015620Z",
      "source_id": "un_comtrade",
      "stage": "PARTNERS",
      "status": "COMPLETE",
      "stop_reason": null,
      "unit": {
        "flow": "imports",
        "hs6": "721061",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "721061",
        "imports",
        "2024"
      ]
    }
  ],
  "exit_code": 0,
  "flows": [
    "imports"
  ],
  "max_requests": 2,
  "requests_made": 2,
  "run_id": "20260913T015620Z",
  "source_id": "un_comtrade",
  "stage": "PARTNERS",
  "unavailable": [],
  "years": [
    2024
  ]
}
```

The corrected window is closed permanently. Offline observation/build commands
recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Print corrected V3 contract, coverage, description tokens, Decimal
# reconciliation, net weights, V1 value comparison and QualityReport.
PY
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-snapshots KIND=partners SOURCE=un_comtrade
```

Observed V3: HTTP 200, 8,425 bytes; count 8; seven non-World H6 rows with
unique descriptions `Rep. of Korea`, `India`, `USA`, `China`,
`United Arab Emirates`, `Other Asia, nes`, and `Finland`. S=R=
71149266.221, diff 0.000, tolerance 0.0035; net-weight sum
93,232,034.488; row values match V1. Coverage COMPLETE and the separate
Comtrade partner snapshot was built.

Case validation and engine-proof commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_briefs_real.py tests/test_case_projection.py tests/test_acquisition_snapshots.py tests/test_acquisition_connectors.py tests/test_acquisition_cli.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q -s tests/test_case_briefs_real.py::test_public_engine_state_is_investigate_with_null_route_for_each_built_snapshot
```

## 2026-09-13T02:05:00Z — AM-3 implementation start

Persona: implementer-sol, data/evidence engineer. Data classification:
confidential_demo; only public-source acquisition records and synthetic test
doubles are in scope.

Authority: OD-16/OD-17 and approved AM-3
`6e5969323405e858fdc584d8a4f1d67d1c23317b6164669384fa3119fd33e5fb`;
reviewer-grok APPROVE with ten binding advisories. No V3 request is permitted
until T-26 through T-39 are RED then GREEN.

Commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_connectors.py tests/test_case_brief.py tests/test_case_projection.py
```

RED: `11 failed, 372 passed in 11.13s`; failures covered missing V3 config,
aggregate/World/reference/zero/unique checks, typed reason, validator evidence
and the superseded-attempt marker. The first GREEN attempt exposed the
expected source-config V1/V2 exact-set validator plus a test-double fixture
defect: a two-row tolerance was incorrectly asserted as 0.003 rather than
2 × 0.0005 = 0.001. The assertion was corrected to the formula in AM-3.
Final pre-window GREEN: `383 passed in 11.28s`.

## 2026-09-13T02:24:00Z — W-C V3 operator window preconditions

This is the single OD-16/AM-3 V3 window. All parameters and consultation facts
are recorded before execution:

- source `un_comtrade`; sole HS6 `721061` from
  `data/cases/selection/comtrade-partners-s14-v1.json`;
- reporter SAU / 682; period 2024; imports / M; nomenclature H6;
- variant V3 enters only through
  `partner_dimension_query=&includeDesc=true`; `partnerCode` remains omitted,
  V2 is not used, and there is no `all`/`ALL` token;
- `MAX_REQUESTS=2`: exactly one configured TERMS capture and one data request;
  no retry, repeat V3, V2, or second data request under any outcome;
- the existing verified-TLS robots consultation is carried forward: HTTP 404
  `Resource Not Found`, no directives available; no new robots request;
- the existing terms evidence is carried forward: official policy HTTP 200 at
  `2026-09-12T14:07:09.935238+00:00`, subscriptions page HTTP 200 at
  `2026-09-12T14:07:17.986724+00:00`, and stored TERMS contract
  `b80d2e94c96a35656776a7f8d7b7e334d6691162ebd8627be9f05ec243f245d7/20260912T143742Z`;
- verified TLS remains mandatory. The key is sourced from `.env` only by the
  shell inside the following acquisition command. It is not printed, read as
  text, or stored; the configured header denylist and echo refusal apply.
- `includeDesc` being documented is OD-16's owner statement. The official
  parameter table remains unobserved here; only returned V3 rows establish
  its effect.

Command recorded before execution:

```bash
set -a; . ./.env; set +a; IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-partners SOURCE=un_comtrade CANDIDATES=data/cases/selection/comtrade-partners-s14-v1.json YEARS=2024 FLOWS=imports MAX_REQUESTS=2 PARAMETERS='partner_dimension_query=&includeDesc=true'
```

### W-C V3 window STOP — V3 was not transmitted

The Make recipe expanded the parameter without shell quoting:

```text
--parameter partner_dimension_query=&includeDesc=true
```

The shell treated `&` as a control operator. The acquisition process therefore
received `partner_dimension_query=` and made one repeated V1 data request;
`includeDesc=true` was not part of the stored endpoint or query contract.
The command emitted only the recipe line to captured stdout, so no RunReport
JSON was available to paste. The immutable stored unit is
`e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184/20260913T014942Z`;
its contract proves endpoint omission and its coverage records requests_made 2,
INCOMPLETE / PARTNER_DESCRIPTIONS_UNAVAILABLE.

This consumed the window's sole data-request budget. SC-13 closes the window:
no corrected V3, retry, V2, or other parameter is attempted. Because V3 did
not execute, AM-3 Case C does not authorize a third manifest invocation. The
new write-once repeated-V1 unit is retained; it is not deleted or rewritten.
This is a binding stop, not worked around.

Offline inspection command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Read the stored 20260913T014942Z contract, coverage and gzip payload;
# print their JSON, Decimal reconciliation, description presence and the
# current connector QualityReport. No network and no credential access.
PY
```

Offline inspection printed the contract, coverage and all requested Decimal
metrics, then exited 1 because `QualityReport` has no `to_json` method. This
does not reopen the network window. Replacement quality-report-only command
recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Re-open the same immutable page offline and serialize QualityReport fields
# explicitly. No network and no credential access.
PY
```

Captured acquisition stdout (verbatim; no RunReport JSON followed):

```text
PYTHONPATH=src /home/barami/.local/bin/uv run --locked --extra dev python -m ior_mvp.acquisition acquire-partners --source un_comtrade --candidates data/cases/selection/comtrade-partners-s14-v1.json --years 2024 --max-requests 2 --flows imports --parameter partner_dimension_query=&includeDesc=true
```

Stored coverage (verbatim):

```json
{
  "completeness_basis": "UNAVAILABLE",
  "missing_pages": [],
  "observed_stop": null,
  "pages_expected": 1,
  "pages_fetched": 1,
  "query_hash": "e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184",
  "requests_made": 2,
  "run_id": "20260913T014942Z",
  "source_id": "un_comtrade",
  "stage": "PARTNERS",
  "status": "INCOMPLETE",
  "stop_reason": "PARTNER_DESCRIPTIONS_UNAVAILABLE",
  "unit": {
    "flow": "imports",
    "hs6": "721061",
    "period": "2024",
    "product_scope": "EXPLICIT",
    "stage": "PARTNERS"
  },
  "unit_key": [
    "721061",
    "imports",
    "2024"
  ]
}
```

Offline stored-row result:

```text
WC_ATTEMPT_ENVELOPE 8 8 ''
WC_ATTEMPT_DISTINCT partnerCode {"0": 1, "156": 1, "246": 1, "410": 1, "490": 1, "699": 1, "784": 1, "842": 1}
WC_ATTEMPT_DISTINCT partner2Code {"0": 8}
WC_ATTEMPT_DISTINCT motCode {"0": 8}
WC_ATTEMPT_DISTINCT customsCode {"C00": 8}
WC_ATTEMPT_DISTINCT classificationCode {"H6": 8}
WC_ATTEMPT_NON_WORLD_ROWS 7
WC_ATTEMPT_NON_WORLD_DESCS_PRESENT False
WC_ATTEMPT_NON_WORLD_PRIMARY_VALUE_SUM 71149266.221
WC_ATTEMPT_UNIVERSE_WORLD_VALUE 71149266.221
WC_ATTEMPT_ABS_DIFF 0.000
WC_ATTEMPT_TOLERANCE 0.0035
```

The quality report was FAIL with exactly
`partner_desc_present_for_non_world_rows`; `aggregate_reconciles` PASS
(`S=71149266.221; R=71149266.221; diff=0.000; s=3;
tolerance=0.0035; world_match=True`) and description uniqueness PASS. This is
a repeated-V1 observation, not V3 evidence.

No 721061 brief, partner snapshot, engine input, governed Core/ADR/KL text, or
manifest was changed after the stop. The final state therefore remains the
pre-window AM-2 state: PARTNER_DETAIL_MISSING / COVERAGE_INDETERMINATE and
engine INVESTIGATE with the previously recorded fired set R0, R1-D, R12.

Canonical candidate-identity command recorded before execution:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Parse git status --porcelain=v1 -z; exclude .autonomous-workflow, ignored
# trees, and both S14 record folders; hash sorted present files against base
# ab6211f; canonical compact JSON plus trailing LF; print file count/identity.
PY
```

```text
CANDIDATE_IDENTITY 0868e32720f2ecf33e2332d3b7e081ee294c856bd632c1278349fb997f5fb4f6
CANDIDATE_FILE_COUNT 147
CANDIDATE_SERIALIZATION compact-sort_keys-trailing-LF
```

Final non-mutating stop checks recorded before execution:

```bash
git diff --cached --quiet && echo INDEX_EMPTY_PASS
git diff --check && echo DIFF_CHECK_PASS
git diff --quiet ab6211f86307ad95a0e61f0597664023f09b7177 -- .autonomous-workflow && echo AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- ':(glob)src/ior_mvp/*.py')" && echo TOP_LEVEL_MODULES_UNCHANGED_PASS
```

Muhasib stop audit:

- Verified: AM-3 and review hashes/authority were read; doubles went RED then
  GREEN (`383 passed`); the network command made one TERMS and one data
  request; the stored endpoint and contract omitted V3; raw Decimal metrics
  and exact check set were recomputed offline; the canonical identity excludes
  both S14 record folders.
- Assumed: the Make recipe's unquoted expansion is the shell-control cause,
  based on captured command text plus the stored contract. No assumption is
  made about how a correctly transmitted V3 would behave.
- Not claimed: V3 execution, description availability, OBSERVED partner state,
  R3, third manifest run, full pytest, `make ci`, portability, independent
  approval, or completion.

## 2026-09-13T02:02:00Z — OD-18 tooling correction

OD-18 classifies the untransmitted variant as a Make/CLI tooling defect and
authorizes one corrected V3 data request. Test-first command recorded before
execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_cli.py::test_make_acquire_partners_quotes_variant_ampersand_for_cli_contract_and_url
```

## 2026-09-13T01:26:00Z — AM-2 correction-round handoff

- T-12 passed first (`1 passed`).
- Doubles and real tri-state gates passed; final focused suite:
  `547 passed`.
- W-C stopped after V1: TERMS HTTP 200 / 464,768 bytes; data HTTP 200 /
  7,320 bytes; clear count 8, one World and seven non-World H6 rows; all
  partner descriptions null; unit
  `INCOMPLETE / COVERAGE_INDETERMINATE`. Unit coverage records two requests;
  the known unavailable-branch RunReport aggregate printed zero. V2 did not
  open because secondary dimensions and pair uniqueness passed.
- Brief states: 392010 OBSERVED/42; 721012 OBSERVED/12; 721061
  MISSING/COVERAGE_INDETERMINATE; 760429 OBSERVED/43; 760711 OBSERVED/27.
- All five public-engine results remain INVESTIGATE/null; 721061 fired
  `{R0, R1-D, R12}`.
- Manifest Case B second/final run:
  `2026-09-13T01:15:40Z`; rows 535→616, 81 additions, zero base-row changes;
  authority 19→19 with unchanged path set and the six authorized changed
  paths. No third run is authorized.
- Final gates: `2400 passed, 1 warning`; `make ci` exit 0 with 2400 pytest,
  152 functional and 4 visual browser tests; copied-tree
  `PORTABILITY_AM2_PASS`.
- Final IAC-6 identity, base
  `ab6211f86307ad95a0e61f0597664023f09b7177`, excluding
  `.workflow/slices/S14-deep-cases-a/` and
  `.workflow/slices/S14b-deep-case-portfolio/`:
  `baf0b4dd4bab1316804a90e7e5a5017c6c71337fbacc5fd1b07bc550022eafb5`,
  141 files, canonical compact sorted serialization with trailing LF.
- Index empty; product tree intentionally uncommitted and unstaged.

Stop accounting: no AM-2 SC-11/SC-12 or inherited correction-round stop
triggered. W-C terminated under AM-2 C-5 branch (iii), which is an honest
INCOMPLETE outcome rather than a workaround. The earlier S14a W-T
verified-TLS stops remain recorded. No wall, TLS failure, robots rule or
provider predicate was bypassed.

Muhasib self-audit: verified from files and executed outputs are the stored
W-C contracts/coverage, row counts and null descriptions; all five brief
states/passports/engine proofs; manifest oracle; selection and WITS hashes;
protected-set/index/header-name scans; pytest, `make ci`, portability and
identity. Assumptions/interpretations carried to independent review are:
(1) the correction brief's explicit OBSERVED 42/12/43/27 instruction governs
the immutable WITS H0 partner rows, while strict H6 matching remains applied
to the Comtrade substitution; (2) ADR-021's `01:13:59Z` value is the
pre-invocation authorization-record timestamp, while `01:15:40Z` is the
authoritative generator execution receipt. No independent approval, commit,
PR, hosted CI or merge is claimed.

## 2026-09-13T00:53:00Z — AM-2 correction-round entry

Persona remains `implementer-sol`, data/evidence engineering. Data
classification remains `confidential_demo`: public-source records and
synthetic fixtures only; no restricted client data. OD-12 through OD-15,
AM-2 (`5bccc8a539e6574fea699a9ec3ed167ea7945b5a0a369fcbb65ab50780f1a020`)
and reviewer-grok's APPROVE with ten binding advisories were read before work.
Precedence is OD-12/OD-13 over AM-2 over AM-1 over the base plan.

Correction-round start commands and results:

```bash
sha256sum .autonomous-workflow/plans/s14-deep-cases-a/cycle-1/plan-1-s14a-amendment-2.json \
  .autonomous-workflow/evidence/s14-deep-cases-a/plan-1-amendment-2-review.json
git diff --stat -- data/manifests/snapshot_manifest.json \
  docs/authority/authority_hashes.json
git rev-parse HEAD
git status --short
```

AM-2 hash matched. HEAD remained
`ab6211f86307ad95a0e61f0597664023f09b7177`. Both generated manifest
outputs were modified and ADR-021 records manifest invocation 1, so C-11
**Case B** applies: exactly one further `build_manifests.py` invocation is
authorized after all AM-2 governed text; it will be S14a's second and last.
No third invocation is authorized.

### OD-14 scope-deviation justifications

The following four implementation modules were outside the base plan's §7.2
enumeration. Each change answered an observed RED and is retained for
independent review; this does not authorize further scope.

- `src/ior_mvp/acquisition/snapshots.py`: W-P's HTTP-200 WITS `Error.aspx`
  page for 721061 had transport coverage COMPLETE but normalization UNPARSED.
  The pre-fix builder RED raised `AcquisitionUnavailable:
  FORMAT_NOT_PARSEABLE` instead of retaining a typed derived exclusion, and
  the pre-fix reconstruction RED selected a newer run and failed
  `SELECTION_CHANGED`. The change preserves UNPARSED as an honest exclusion
  for `AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS` kinds and reconstructs the
  recorded query-hash/run-id selection.
- `src/ior_mvp/acquisition/connectors/base.py`: T3 registry coverage was RED
  because the newly governed producer/WCO source IDs had no registered
  connector factories, so configured sources could not be acquired through
  the shared registry. The change registers only those governed connectors.
- `src/ior_mvp/acquisition/connectors/documents.py`: T3 document-connector
  tests were RED because no connector classes existed for the newly governed
  WCO and four producer source contracts. The change supplies those
  source-specific classes while retaining the shared document acquisition
  path.
- `src/ior_mvp/acquisition/documents/lists.py`: T3 list-contract tests were RED
  because `nomenclature_authority`, the governed source-to-publisher
  restrictions, and the source support-code sets were absent. The change adds
  those closed-list validations so unsupported source/kind/support
  combinations fail before acquisition.

The original no-LF IAC-6 identity remains in `test_evidence.md`; its dated
OD-14 correction now records the same-tree 127-file canonical trailing-LF
identity `9c93643388cdb4dc99ca16ceeaa9ede5d0ce22a460ed139eaa0bc905c5531acd`.

### T-12 first — command recorded before execution

Per OD-13 and `IAC-T12-UNREFERENCED-PASSPORT-PASSES`, this proof runs before
the other AM-2 implementation. Expected result: PASS. An unexpected failure is
a stop/escalation; text inside `execution_cap` is not treated as a formal
evidence reference.

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_projection.py::test_unreferenced_attempt_passport_is_accepted_by_validate_public_snapshot_2_1_0
```

T-12 result: `1 passed in 0.03s`; no OD-13 escalation was triggered.

### CaseBrief tri-state RED — command recorded before execution

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_brief.py
```

CaseBrief RED result: `14 failed, 1 passed`; failures showed the 1.0.0 exact
key/schema contract and missing reason-set export. GREEN after implementation:
`15 passed in 0.04s`.

### Comtrade partner doubles RED — command recorded before execution

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q \
  tests/test_acquisition_connectors.py::test_un_comtrade_partners_validate_uses_partner_pair_uniqueness_and_single_valued_secondary_dimensions \
  tests/test_acquisition_connectors.py::test_un_comtrade_partners_zero_row_envelope_is_complete_normalized_empty_not_format_not_parseable \
  tests/test_acquisition_connectors.py::test_un_comtrade_partners_only_world_rows_or_error_envelope_is_incomplete_coverage_indeterminate \
  tests/test_acquisition_connectors.py::test_un_comtrade_universe_validation_unchanged_by_partners_mapping \
  tests/test_acquisition_config.py::test_un_comtrade_partners_template_omits_partner_token_and_variants_are_v1_empty_v2_partner2code_zero \
  tests/test_acquisition_cli.py::test_acquire_partners_parameter_flag_enters_contract_parameters_and_query_hash_and_rejects_reserved_names
```

Comtrade doubles RED result: `4 failed, 3 passed`; failures proved the old
HS6-grain duplicate check, zero-row `REPORTER_MISMATCH`, unavailable PARTNERS
template and absent CLI parameter path. GREEN after implementation:
`7 passed in 0.13s`.

### Projection tri-state RED — command recorded before execution

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q \
  tests/test_case_projection.py::test_missing_state_projects_unavailable_rows_with_attempt_passport_marker_and_stored_url \
  tests/test_case_projection.py::test_observed_zero_state_projects_zero_passport_not_attempt_passport \
  tests/test_case_projection.py::test_observed_rows_from_un_comtrade_snapshot_use_comtrade_passport_and_keep_wits_attempt_passport \
  tests/test_case_projection.py::test_projection_refuses_brief_state_that_contradicts_loaded_snapshot
```

Projection RED result: `3 failed, 1 passed`; MISSING had no attempt passport,
ZERO had no ZERO passport, and observed Comtrade rows remained UNAVAILABLE.
GREEN after implementation: `4 passed in 0.04s`.

### Pre-W-C doubles gate — command recorded before execution

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_brief.py tests/test_case_projection.py \
  tests/test_acquisition_connectors.py tests/test_acquisition_config.py \
  tests/test_acquisition_cli.py
```

Pre-W-C doubles gate initially exposed one updated existing partner test and
backward-compatible fixture configs; after correcting those test/contracts,
the gate passed: `410 passed in 12.52s`. T-1…T-12 and T-16…T-21 are therefore
GREEN before W-C.

## 2026-09-13T01:08:00Z — T4 W-C operator window preconditions

This is the one OD-12/AM-2 W-C window. Parameters and consultation facts are
recorded before any W-C network request:

- Source: `un_comtrade`; official Class-B source substitution under OR-4.
- Candidate file:
  `data/cases/selection/comtrade-partners-s14-v1.json`; sole HS6 `721061`.
- Contract: reporter SAU / reporterCode 682; 2024; imports / flowCode M;
  explicit HS6 `721061`; classification must be observed as one value and must
  equal H6 before it can enter the H6 brief.
- V1: `partner_dimension_query=` (omit `partnerCode`; null hypothesis).
- V2, conditional only if V1 is INCOMPLETE and its only failures are partner
  uniqueness/secondary-dimension checks with observed multi-valued
  `partner2Code`: `partner_dimension_query=&partner2Code=0`.
- No V3 and no `all`/`ALL` token are permitted.
- Per invocation `MAX_REQUESTS=2`: one configured TERMS capture and one data
  request. At most two data requests and at most four connector HTTP requests.
  Verified TLS, configured two-second minimum interval, no retry around an
  HTTP status. Because the base-plan host-consultation rule is binding and no
  `comtradeapi.un.org/robots.txt` receipt exists in the S13a record, W-C first
  makes one bounded verified-TLS robots consultation. It is consultation
  overhead, not a data-request variant; if a disallow covers the v1 data path,
  W-C stops without acquisition.
- Credential: the name is `IOR_COMTRADE_SUBSCRIPTION_KEY`; its value will be
  loaded by shell sourcing `.env` only inside the V1/V2 acquisition command.
  It is never printed, read as text by the agent or stored. The configured
  case-insensitive subscription-header denylist and response echo refusal
  remain active.
- Existing S13a terms receipt copied forward: W0-bis observed the official
  policy URL at `2026-09-12T14:07:09.935238+00:00`, HTTP 200,
  `text/html; charset=UTF-8`, including the re-dissemination restriction; the
  subscriptions page at `2026-09-12T14:07:17.986724+00:00`, HTTP 200,
  recorded “max 100K records per call”, “500 calls/day” and “5 calls per
  second”. W1-ter stored TERMS contract
  `b80d2e94c96a35656776a7f8d7b7e334d6691162ebd8627be9f05ec243f245d7/20260912T143742Z`,
  HTTP 200, retrieved `2026-09-12T14:37:47Z`, raw SHA-256
  `b50bd4f2cc86dd8d0abdff1b64ffe9dd552368867b0f04df3146138472e46c8d`.
- Stop honestly on any wall, robots disallow, TLS failure, credential absence,
  HTTP error, error envelope, only-World rows, count mismatch, record cap,
  contract contradiction, mixed/non-H6 classification or other incomplete
  coverage. `FORMAT_NOT_PARSEABLE` is never ZERO. ZERO requires a well-formed
  clear-error envelope with `count == len(data) == 0`.

Offline observation O-0 was executed before W-C against the stored 2024
imports universe payload:

```text
O0_SORTED_ROW_FIELDS ["aggrLevel", "altQty", "altQtyUnitAbbr", "altQtyUnitCode", "cifvalue", "classificationCode", "classificationSearchCode", "cmdCode", "cmdDesc", "customsCode", "customsDesc", "flowCode", "flowDesc", "fobvalue", "freqCode", "grossWgt", "isAggregate", "isAltQtyEstimated", "isGrossWgtEstimated", "isLeaf", "isNetWgtEstimated", "isOriginalClassification", "isQtyEstimated", "isReported", "legacyEstimationFlag", "mosCode", "motCode", "motDesc", "netWgt", "partner2Code", "partner2Desc", "partner2ISO", "partnerCode", "partnerDesc", "partnerISO", "period", "primaryValue", "qty", "qtyUnitAbbr", "qtyUnitCode", "refMonth", "refPeriodId", "refYear", "reporterCode", "reporterDesc", "reporterISO", "typeCode"]
O0_WORLD_VALUE partnerCode 0
O0_WORLD_VALUE partner2Code 0
O0_WORLD_VALUE motCode 0
O0_WORLD_VALUE customsCode "C00"
O0_ENVELOPE count 5012 len_data 5012 error ""
```

Pre-window WITS byte oracle:

```text
0a5a564594ecdb35ad129f7c111e3e5f62ba6d152fac275cea6d0ecc0e08dc63  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-12.json
cdcc904af656b8d1ba02f6dd23593071cddcf21739e58290d4cf197e6723657f  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json
a6ce53e3807527c56092e4a580896fedc99bb1c4f6503de2581ada5b3cfae07c  data/raw/wits_trade/ed5759a33b4ffc375ef1f3aba6a46d0f5dc076247dc16a3bfdc883a9c04e311e/20260912T233403Z/page-0001.contract.json
```

Robots consultation command recorded before execution:

```bash
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src \
python3 - <<'PY'
# One verified-TLS GET to https://comtradeapi.un.org/robots.txt; print status,
# content type, bytes, SHA-256 and text directives only. No credential loaded.
PY
```

Robots consultation result: verified TLS succeeded and the host returned HTTP
404 `Resource Not Found`; no robots body or directive was available to bypass.
The official authenticated v1 API route remains governed by the recorded
UN Comtrade policy/subscription terms and OR-4. No credential was loaded for
this consultation.

### W-C RUN 1 / V1 — command recorded before execution

```bash
set -a
. ./.env
set +a
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src \
make acquire-partners SOURCE=un_comtrade \
  CANDIDATES=data/cases/selection/comtrade-partners-s14-v1.json \
  YEARS=2024 FLOWS=imports MAX_REQUESTS=2 \
  PARAMETERS='partner_dimension_query='
```

V1 provider request returned one stored page and
`INCOMPLETE / COVERAGE_INDETERMINATE`; the ladder decision is made only after
the following offline contract/coverage/QualityReport/payload observation.
Command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Read only the stored V1 contract, coverage, quality report and gzip payload;
# print envelope count/len/error, distinct dimension values/counts, World-row
# presence, non-World row count, classification and value reconciliation.
PY
```

V1 RunReport (verbatim):

```json
{
  "artifacts": [],
  "coverage": [
    {
      "completeness_basis": "UNAVAILABLE",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 1,
      "pages_fetched": 1,
      "query_hash": "e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184",
      "requests_made": 2,
      "run_id": "20260913T010452Z",
      "source_id": "un_comtrade",
      "stage": "PARTNERS",
      "status": "INCOMPLETE",
      "stop_reason": "COVERAGE_INDETERMINATE",
      "unit": {
        "flow": "imports",
        "hs6": "721061",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "721061",
        "imports",
        "2024"
      ]
    }
  ],
  "exit_code": 3,
  "flows": [
    "imports"
  ],
  "max_requests": 2,
  "requests_made": 0,
  "run_id": "20260913T010452Z",
  "source_id": "un_comtrade",
  "stage": "PARTNERS",
  "unavailable": [
    "COVERAGE_INDETERMINATE"
  ],
  "years": [
    2024
  ]
}
```

The top-level `requests_made: 0` is the known RunReport unavailable-branch
aggregation defect; the immutable unit coverage is authoritative and records
two requests (one TERMS, one data). No retry was made.

Offline V1 observation:

```text
WC_V1_QUALITY_REPORT {"checks": [{"check_id": "content_type_json", "detail": "application/json", "result": "PASS"}, {"check_id": "envelope_shape", "detail": "count integer and data list required", "result": "PASS"}, {"check_id": "no_error_field", "detail": "error must be absent, null, or empty", "result": "PASS"}, {"check_id": "count_matches_rows", "detail": "count=8; stored_rows=8", "result": "PASS"}, {"check_id": "count_below_documented_cap", "detail": "count=8; cap=100000", "result": "PASS"}, {"check_id": "rows_or_zero_envelope", "detail": "8 rows; zero_envelope=False", "result": "PASS"}, {"check_id": "reporter_682_all_rows", "detail": "expected reporterCode=682", "result": "PASS"}, {"check_id": "period_matches_contract", "detail": "expected period=2024", "result": "PASS"}, {"check_id": "flow_matches_contract", "detail": "expected flowCode=M", "result": "PASS"}, {"check_id": "partner_matches_stage", "detail": "PARTNERS", "result": "PASS"}, {"check_id": "cmd_code_hs6_all_rows", "detail": "six-digit explicit HS6 required", "result": "PASS"}, {"check_id": "single_classification_code_per_unit", "detail": "classification_codes=['H6']", "result": "PASS"}, {"check_id": "partner_rows_unique_per_unit", "detail": "(cmdCode, partnerCode) must be unique", "result": "PASS"}, {"check_id": "secondary_dimensions_single_valued", "detail": "present partner2Code/motCode/customsCode fields", "result": "PASS"}, {"check_id": "partner_desc_present_for_non_world_rows", "detail": "non-World rows require partnerDesc", "result": "FAIL"}], "query_hash": "e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184", "run_id": "20260913T010452Z", "source_id": "un_comtrade", "status": "FAIL"}
WC_V1_ENVELOPE count 8 len_data 8 error ""
WC_V1_DISTINCT partnerCode {"0": 1, "156": 1, "246": 1, "410": 1, "490": 1, "699": 1, "784": 1, "842": 1}
WC_V1_DISTINCT partner2Code {"0": 8}
WC_V1_DISTINCT motCode {"0": 8}
WC_V1_DISTINCT customsCode {"C00": 8}
WC_V1_DISTINCT classificationCode {"H6": 8}
WC_V1_WORLD_ROWS 1
WC_V1_NON_WORLD_ROWS 7
WC_V1_NON_WORLD_DESCS_PRESENT False
WC_V1_NON_WORLD_PRIMARY_VALUE_SUM 71149266.221
WC_UNIVERSE_721061_ROWS 1
WC_UNIVERSE_721061_PRIMARY_VALUE 71149266.221
```

Every returned row, including the seven non-World rows, had
`partnerDesc: null` and `partnerISO: null`. The only failing predicate is
`partner_desc_present_for_non_world_rows`; uniqueness and every secondary
dimension predicate passed, with `partner2Code` single-valued at 0. The V2
condition is therefore false. Per AM-2 C-5 branch (iii), W-C stops with no V2,
no filtering, no inferred partner names and no Comtrade partner snapshot.
The honest 721061 state remains
`PARTNER_DETAIL_MISSING / COVERAGE_INDETERMINATE`; the separate WITS
`FORMAT_NOT_PARSEABLE` attempt remains visible.

### Post-W-C real tri-state gate — command recorded before execution

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_brief.py tests/test_case_projection.py \
  tests/test_case_briefs_real.py \
  tests/test_acquisition_snapshots.py::test_un_comtrade_partner_snapshot_id_is_distinct_and_wits_snapshot_bytes_unchanged \
  tests/test_acquisition_stored_artifacts.py::test_repository_raw_store_has_no_stored_evidence_problems \
  tests/test_acquisition_stored_artifacts.py::test_no_stored_un_comtrade_artifact_or_log_contains_subscription_key_header_name
```

The first real gate RED was six `revision mismatch` failures because the WITS
partner snapshot's immutable source label is H0 while the four governed
briefs are H6. The binding AM-2 review nevertheless explicitly classifies
those four units OBSERVED and supplies their non-World counts
42/12/43/27; strict revision matching remains enforced for the H6 Comtrade
substitution. With that source-bounded rule, the gate passed:
`10 passed in 4.32s`.

Engine-proof and tri-state command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
# Build all five briefs; print declared state/reason/count, projected row and
# partner-passport counts, and actual engine state/route/reason/fired set.
PY
```

Engine/tri-state output:

```text
CASE_PROOF 392010 PARTNER_DETAIL_OBSERVED None 42 projected_rows 42 passports ["P-WITS-392010-PARTNERS"] engine INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED fired ["R0", "R1-D", "R2", "R4-D", "R12"]
CASE_PROOF 721012 PARTNER_DETAIL_OBSERVED None 12 projected_rows 12 passports ["P-WITS-721012-PARTNERS"] engine INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED fired ["R0", "R1-D", "R2", "R4-D", "R12"]
CASE_PROOF 721061 PARTNER_DETAIL_MISSING COVERAGE_INDETERMINATE UNAVAILABLE projected_rows 0 passports ["P-COMTRADE-721061-PARTNERS-ATTEMPT", "P-WITS-721061-PARTNERS-ATTEMPT"] engine INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED fired ["R0", "R1-D", "R12"]
CASE_PROOF 760429 PARTNER_DETAIL_OBSERVED None 43 projected_rows 43 passports ["P-WITS-760429-PARTNERS"] engine INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED fired ["R0", "R1-D", "R2", "R3", "R4-D", "R5", "R9-S", "R10", "R12"]
CASE_PROOF 760711 PARTNER_DETAIL_OBSERVED None 27 projected_rows 27 passports ["P-WITS-760711-PARTNERS"] engine INVESTIGATE None ROUTE_CHANGING_EVIDENCE_UNRESOLVED fired ["R0", "R1-D", "R2", "R12"]
```

SC-2b did not trigger: 721061 remains INVESTIGATE/null and its fired set is
the permitted `{R0, R1-D, R12}`. No state, route or input was authored.

Full AM-2 focused gate command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc \
PATH=.venv/bin:$PATH PYTHONPATH=src \
pytest -q tests/test_case_brief.py tests/test_case_projection.py \
  tests/test_case_briefs_real.py tests/test_acquisition_connectors.py \
  tests/test_acquisition_config.py tests/test_acquisition_cli.py \
  tests/test_acquisition_snapshots.py \
  tests/test_acquisition_stored_artifacts.py
```

The shell loads the subscription key only for this acquisition process. The
command does not print it; stored headers remain denylisted.

V1 preflight RunReport (verbatim):

```json
{
  "artifacts": [],
  "coverage": [
    {
      "completeness_basis": "UNAVAILABLE",
      "missing_pages": [],
      "observed_stop": null,
      "pages_expected": 0,
      "pages_fetched": 0,
      "query_hash": "c5da9e4813c887a486e99447b189c11af880f9c2fb03b912bcf15acf6456fb6e",
      "requests_made": 0,
      "run_id": "20260913T010344Z",
      "source_id": "un_comtrade",
      "stage": "PARTNERS",
      "status": "INCOMPLETE",
      "stop_reason": "ENDPOINT_UNVERIFIED",
      "unit": {
        "flow": "imports",
        "hs6": "721061",
        "period": "2024",
        "product_scope": "EXPLICIT",
        "stage": "PARTNERS"
      },
      "unit_key": [
        "721061",
        "imports",
        "2024"
      ]
    }
  ],
  "exit_code": 3,
  "flows": [
    "imports"
  ],
  "max_requests": 2,
  "requests_made": 0,
  "run_id": "20260913T010344Z",
  "source_id": "un_comtrade",
  "stage": "PARTNERS",
  "unavailable": [
    "ENDPOINT_UNVERIFIED"
  ],
  "years": [
    2024
  ]
}
```

No HTTP request occurred. Offline diagnosis found a CLI dispatch defect: the
parsed parameter tuple had been passed to `acquire_universe` instead of
`acquire_partners`, so the V1 template token was absent and fail-closed before
transport. The dispatch was corrected, its test expanded to exercise
`cli.main`, and the regression passed (`1 passed in 0.08s`). Because the
provider was never contacted and the request count is zero, this is a
preflight attempt, not a data variant. The stored attempt remains immutable.

V1 retry command recorded before execution:

```bash
set -a
. ./.env
set +a
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 \
PYTHONPYCACHEPREFIX=/tmp/ior-s14a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src \
make acquire-partners SOURCE=un_comtrade \
  CANDIDATES=data/cases/selection/comtrade-partners-s14-v1.json \
  YEARS=2024 FLOWS=imports MAX_REQUESTS=2 \
  PARAMETERS='partner_dimension_query='
```

T10 identity:

```text
CANDIDATE_IDENTITY 08f5f78395e5b99db55ba0ae9a6de36aff4d6f0b60b606dd1fa926b25fec04bb
CANDIDATE_FILE_COUNT 127
CANDIDATE_SERIALIZATION compact-sort_keys-no-trailing-newline
INDEX_EMPTY_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
STATE_JSON_VALID_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
```

Final muhasib diff commands (recorded before execution):

```bash
git diff --check
git diff --stat ab6211f86307ad95a0e61f0597664023f09b7177
git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- config/*.yaml
```

```bash
PYTHONPATH=src python3 - <<'PY'
# Recompute the compact IAC-6 payload after slice-record edits and assert the
# identity and file count remain exact.
PY
```

Muhasib diff results: `git diff --check` passed; tracked diff is 44 files
(`1923` insertions, `79` deletions) plus write-once untracked evidence/code
paths; live config diff names are exactly
`config/acquisition_sources.v1.yaml` and
`config/product_families.v1.yaml`. Compact IAC-6 identity reverified:
`08f5f78395e5b99db55ba0ae9a6de36aff4d6f0b60b606dd1fa926b25fec04bb`,
127 files.

Stop conditions: SC-5 applied to the two W-T hosts and stopped those source
paths without bypass. No whole-slice stop condition applied. The WCO second
index consultation is a disclosed bounded deviation caused by the first
in-memory predicate returning no hrefs. All remaining assumptions and the
no-self-approval boundary are recorded in `test_evidence.md`.

T10: COMPLETE. Candidate is UNCOMMITTED and UNSTAGED for supervisor and
independent reviewer review.

```bash
test -z "$(rg -l '/home/barami/' data/cases data/documents/*/lists config/history || true)" &&
test -z "$(rg -l 'SAU-H6-390220' data/cases config docs/core src tests || true)" &&
echo PORTABLE_TEXT_PASS
```

Corrected results: `PROTECTED_SET_BYTE_IDENTICAL_PASS`;
`PORTABLE_TEXT_PASS`.

### Single authorized manifest invocation and immediate oracle

Generator invocation count before command: `0`.

Command recorded before execution:

```bash
printf 'MANIFEST_RUN_STARTED_UTC %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PYTHONPATH=src python3 scripts/build_manifests.py
printf 'MANIFEST_RUN_FINISHED_UTC %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q tests/test_integrity_contract.py
PYTHONPATH=src python3 - <<'PY'
# Compare current manifests with git-show HEAD manifests:
# every old snapshot row exact; additions only under authorized S14a prefixes;
# authority path set unchanged; changed authority rows exactly acquisition
# sources, product families and Core 02/04/05/09.
PY
```

No second invocation is authorized. If any immediate oracle fails, SC-7
applies.

Manifest invocation receipt: started and finished
`2026-09-13T00:25:27Z`, exit `0`. Generator invocation count is now **1** and
authorization is exhausted.

Immediate results:

- `INTEGRITY PASS`;
- row oracle `MANIFEST_ORACLE_PASS`: snapshot rows `535 → 607`, 72 additions,
  zero pre-existing changes; authority rows remain 19 with exactly the six
  authorized changes;
- the full integrity-contract suite had two test-only prefix-list failures
  because the historical partition helper did not yet admit the newly
  authorized `data/cases/` and `config/history/` manifest roots. No generated
  row, config or Core text was wrong.

The test helper was extended with positive and sibling-prefix-negative probes.
No generated/governed source was edited and no second generator run occurred.
Immediate-oracle confirmation command (recorded before execution):

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q tests/test_integrity_contract.py
```

Confirmation result: `INTEGRITY PASS`; `25 passed in 0.89s`.

### T9 post-generation commands (recorded before execution)

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
PYTHONPATH=src python3 scripts/validate_scenarios.py
PYTHONPATH=src python3 scripts/demo_smoke.py
python3 scripts/check_prohibited_files.py
python3 scripts/check_threshold_literals.py
```

```bash
PYTHONPATH=src python3 -m ior_mvp.cases select \
  --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 \
  --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json \
  --terms data/cases/selection/hs6-disclosure-terms-v1.json \
  --quota coated_steel=2,fabricated_aluminium=2,technical_plastics=1 \
  --out /tmp/ior-s14a-select-post-manifest
sha256sum /tmp/ior-s14a-select-post-manifest/CASE-SELECTION-S14-*.json \
  data/cases/selection/CASE-SELECTION-S14-*.json
```

```bash
for brief in data/cases/briefs/CASE-BRIEF-*.json; do
  PYTHONPATH=src python3 -m ior_mvp.cases validate-brief --brief "$brief"
  PYTHONPATH=src python3 -m ior_mvp.cases build --brief "$brief" --out /tmp/ior-s14a-build-post-manifest
done
sha256sum /tmp/ior-s14a-build-post-manifest/PUBLIC-SAU-H6-*.json
```

```bash
PYTHONPATH=src python3 - <<'PY'
import sys, importlib
for module in list(sys.modules):
    if module.startswith("ior_mvp"):
        del sys.modules[module]
importlib.import_module("ior_mvp.app")
assert not any(module.startswith("ior_mvp.cases") for module in sys.modules)
assert "ior_mvp.acquisition.transport" not in sys.modules
print("RUNTIME_IMPORT_BOUNDARY_OK")
PY
```

```bash
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  data/snapshots/public data/synthetic data/golden browser_tests \
  ':(glob)src/ior_mvp/*.py' src/ior_mvp/static config/project.yaml \
  config/thresholds.v1.yaml config/sector_profiles.v1.yaml \
  config/evidence_policy.v1.yaml config/ui_strings.v1.yaml \
  config/decision_narratives.v1.yaml config/entity_resolution.v1.yaml \
  config/screening.v1.yaml data/screening data/snapshots/universe \
  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json \
  data/entities/mentions/mentions-v1.json \
  data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json \
  .github/workflows/ci.yml Dockerfile pyproject.toml uv.lock \
  tests/conftest.py tests/test_frozen_public_evidence_pins.py \
  tests/test_golden_cases.py docs/core/01_PRODUCT_AND_REQUIREMENTS.md \
  docs/core/03_SYSTEM_ARCHITECTURE.md \
  docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md \
  docs/core/07_DETERMINISTIC_ENGINE_SPEC.md \
  docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md)" &&
test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)" &&
echo PROTECTED_SET_BYTE_IDENTICAL_PASS
PYTHONPATH=src python3 -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']))"
```

```bash
rm -rf /tmp/ior-portability
cp -a . /tmp/ior-portability
(cd /tmp/ior-portability &&
  UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py &&
  UV_OFFLINE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s14a-portable-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all)
echo PORTABILITY_PASS
```

```bash
make ci
```

T9 post-generation results:

- full pytest: `2373 passed, 1 warning in 32.86s`;
- manifest-checked reconstruction: case `0/5`; acquired snapshots `3/32`;
  documents `20/20`; entities `2/44`; screening `1`;
- selection re-run hash equals recorded hash
  `19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016`;
- all five post-manifest built-snapshot hashes equal their pre-manifest hashes;
- `RUNTIME_IMPORT_BOUNDARY_OK`;
- `PROTECTED_SET_BYTE_IDENTICAL_PASS`; `VISUAL_MANIFEST_OK 56`;
- portability copied-tree integrity and reconstruction passed:
  `PORTABILITY_PASS`;
- `make ci` exited `0`: 2373 pytest tests, 152 functional Chromium nodes and
  4 visual nodes passed. Elapsed 401.845 seconds.

T9: COMPLETE. Generator invocation count: exactly `1`.

## 2026-09-13T00:37:00Z — T10 candidate identity commands

Commands recorded before execution:

```bash
PYTHONPATH=src python3 - <<'PY'
# Parse `git status --porcelain=v1 -z --untracked-files=all`; exclude both S14
# slice-record folders and ignored trees; hash every remaining present file;
# sort by path; serialize exactly with ensure_ascii=False, sort_keys=True and
# separators=(",",":") with no trailing newline; print identity/count/list.
PY
```

```bash
git diff --cached --quiet && echo INDEX_EMPTY_PASS
git diff --quiet ab6211f86307ad95a0e61f0597664023f09b7177 -- .autonomous-workflow &&
echo AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
PYTHONPATH=src python3 -c "import json; json.load(open('.workflow/state.json')); print('STATE_JSON_VALID_PASS')"
git status --short
```

```bash
test -z "$(git diff --name-only ab6211f86307ad95a0e61f0597664023f09b7177 -- \
  data/snapshots/public data/synthetic data/golden browser_tests \
  ':(glob)src/ior_mvp/*.py' src/ior_mvp/static config/project.yaml \
  config/thresholds.v1.yaml config/sector_profiles.v1.yaml \
  config/evidence_policy.v1.yaml config/ui_strings.v1.yaml \
  config/decision_narratives.v1.yaml config/entity_resolution.v1.yaml \
  config/screening.v1.yaml data/screening data/snapshots/universe \
  data/snapshots/partners/PARTNERS-SAU-WITS-TRADE-2026-09-03.json \
  data/entities/mentions/mentions-v1.json \
  data/entities/resolution/ENTITIES-2026-09-12-a12e24c31b02.json \
  .github/workflows/ci.yml Dockerfile pyproject.toml uv.lock \
  tests/conftest.py tests/test_frozen_public_evidence_pins.py \
  tests/test_golden_cases.py docs/core/01_PRODUCT_AND_REQUIREMENTS.md \
  docs/core/03_SYSTEM_ARCHITECTURE.md \
  docs/core/06_SYNTHETIC_MINISTRY_DATA_SPEC.md \
  docs/core/07_DETERMINISTIC_ENGINE_SPEC.md \
  docs/core/08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md)" &&
test -z "$(git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests)" &&
echo PROTECTED_SET_BYTE_IDENTICAL_PASS
```

