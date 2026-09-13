# S15a implementation log — implementer-sol slot 1

## 2026-09-13T03:10:44Z — Orientation and T0 preflight declaration

Persona: `implementer-sol`, senior public-evidence and deterministic-selection
data engineer. Data classification: `confidential_demo`; public-source evidence
and labelled test doubles only. No Ministry/private/paid/personal data is in
scope.

Worktree: `/home/barami/projects/ior-worktrees/s15a`; branch
`slice/s15a-case-selection-evidence-pharma-fertilizers`; preparation base
`1289e31e50c1d835760f6943e697d6d537ac0a18`. This is the owner-approved
parallel preparation phase. T1–T10 are limited to the DD-14 preparation file
set. Core/ADR/KL/control-document integration, M15 proof, manifest generation,
candidate identity, commits, staging, fetching, rebasing, PR activity and
delivery are not part of this phase. The terminal state is
`PREP_HANDOFF_PENDING_M15`.

Authority and plan identities verified before implementation:

- `plan-1-s15a.json` SHA-256
  `819e08fd115373f300a3494f1b486fdf6ffa0779e55d0783a11efac253ae78b5`;
- `decomposition-1.json` SHA-256
  `ea01de65ac299cb2914c01f8f76ec692ce6d691b6530ad868e13b007ac0ab611`;
- pre-planning rulings SHA-256
  `df130f0c9729663904e475c700ada64eee73c6544d1b21ef9d5e02a6201b1bf5`;
- plan rulings SHA-256
  `985eccaf9d692df9fca66ded02aba40cffa298fc8370be686370a5bc89999f3d`;
- live operating rules SHA-256
  `0dc1a8105ac6148f23fbaa48c09328dc7d9de0639a1381afa748115de00329d0`.

The governing DOCX SHA-256 matches Manifest §11:
`5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9`.
The IDE reader cannot render DOCX binaries, so the full extracted searchable
mirror was read under the repository's recorded precedent; it was not treated
as higher authority than the hash-matched DOCX. `docs/project/` is absent in
this repository; task-specific authority is supplied by AGENTS, the Manifest,
the approved S15 plan/rulings/reviews, Core 02/04/05/09, milestone documents,
configuration and the S14 records.

Every Python command below and throughout this phase uses:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src
```

No network is permitted before W-A15a. No `.env` value is read or printed.

T0 verification commands recorded before execution:

```bash
test "$(git branch --show-current)" = slice/s15a-case-selection-evidence-pharma-fertilizers && test "$(git rev-parse HEAD)" = 1289e31e50c1d835760f6943e697d6d537ac0a18 && git merge-base --is-ancestor 1289e31e50c1d835760f6943e697d6d537ac0a18 HEAD && echo BRANCH_OK
git status --short
for r in data/snapshots/public data/synthetic data/golden browser_tests/baselines; do printf '%s %s\n' "$r" "$(git rev-parse HEAD:$r)"; done
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/demo_smoke.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/validate_scenarios.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest --co -q
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 -c "from browser_tests.visual_baselines import validate_manifest; p=validate_manifest(); print('VISUAL_MANIFEST_OK', len(p['entries']))"
rg -n "PARTNER_DETAIL_STATES|SCHEMA_VERSION" src/ior_mvp/public_snapshot.py
```

T0 results:

```text
BRANCH_OK
git status --short: ?? .workflow/slices/S15-deep-cases-b/
data/snapshots/public 2ad27d6eaa9b3ce474f2c9ed62ecaa873ecd5e04
data/synthetic 3fb2247a36b57b85fc0f966717aad5502aa25f4b
data/golden 72618db654110823ec7a8d4dd6415a37e4554e33
browser_tests/baselines c2b3b66bbc6afaefe6e951772984d567cac53522
INTEGRITY PASS
CASE RECONSTRUCTION PASS (0 snapshots, 5 briefs)
RECONSTRUCTION PASS (4 snapshots, 34 artifacts)
DOCUMENT RECONSTRUCTION PASS (20 records, 20 artifacts)
ENTITY RECONSTRUCTION PASS (2 artifacts, 44 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
SMOKE PASS
SCENARIO VALIDATION PASS (2 scenarios)
2416 tests collected in 1.74s
VISUAL_MANIFEST_OK 56
PUBLIC_SNAPSHOT_SCHEMA_VERSION = "2.1.0"
```

The reconstruction command exited 0 with the already-governed PDF extraction
warnings described by KL-63/KL-64/KL-66. BF-13(a) is absent on the preparation
base exactly as the plan permits: PublicSnapshot is 2.1.0 and no
`PARTNER_DETAIL_STATES` constant exists yet. The 2.2.0 proof remains an M15
integration obligation and is not simulated here. BF-13(b)–(f) remain open
until their explicitly bounded windows; no source availability, terms,
storage permission, raw-store outcome, static SFDA rows or Comtrade partner
rows is asserted at T0.

## 2026-09-13T03:14:00Z — T1 RED: S14-CS-1.1 selection contract

Tests are authored before implementation for the eleven plan-named
behaviours: uniform GAP_YEARS exclusion, missing-year provenance, frozen 1.0
semantics, stored-WCO identity validation, governed exclusion reasons, 1.1
output shape, version-derived write prefix, recorded-family resolution,
byte-exact reconstruction/refusal, owner designation isolation, and S14
reproduction against its recorded family identity. CLI argument capture is
extended in the existing CLI test.

RED command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py
```

## 2026-09-13T03:42:00Z — Append-only chronology continuation

Some earlier append hunks were placed after repeated command-fence anchors
rather than at physical EOF by the patch applicator. No prior text was deleted
or rewritten; timestamps and command-before-execution ordering remain factual.
This uniquely anchored continuation is the physical append point for all
remaining records.

T5 generated/validated evidence-table identities:

```text
TERMS_V2_ROWS 91
TERMS_V2_SHA256 eebe4ffab2d541b4356209407cc53b5710b16d65c2a14179fb06495762f22756
IDENTITY_V2_ROWS ['293339', '294190', '310590']
IDENTITY_V2_SHA256 464f25e3c88efd3bde577412792eebfa9a8b9244df3e262daf3094ad34b5f301
```

The selection document inventory includes only the three WCO records cited by
the identity table and the producer records cited by terms-v2 that exist before
W-A15b; unrelated WCO Chapters 39/72/76 are not made selection inputs.

Two consecutive selection commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 -m ior_mvp.cases select --rule-version S14-CS-1.1 --record-prefix CASE-SELECTION-S15- --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json --families config/product_families.v1.yaml --terms data/cases/selection/hs6-disclosure-terms-v2.json --identity-exclusions data/cases/selection/identity-exclusions-v2.json --quota pharma_api=2,fertilizers=2 --out data/cases/selection
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 -m ior_mvp.cases select --rule-version S14-CS-1.1 --record-prefix CASE-SELECTION-S15- --screening data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8 --universe data/snapshots/universe/UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json --families config/product_families.v1.yaml --terms data/cases/selection/hs6-disclosure-terms-v2.json --identity-exclusions data/cases/selection/identity-exclusions-v2.json --quota pharma_api=2,fertilizers=2 --out /tmp/ior-s15a-select-repeat
sha256sum data/cases/selection/CASE-SELECTION-S15-*.json /tmp/ior-s15a-select-repeat/CASE-SELECTION-S15-*.json
cmp data/cases/selection/CASE-SELECTION-S15-*.json /tmp/ior-s15a-select-repeat/CASE-SELECTION-S15-*.json && echo S15_SELECTION_TWO_RUNS_BYTE_IDENTICAL
```

Selection output from both runs:

```text
CASE SELECTION PASS (4 selected; 2 profiles; 2 families)
pharma_api: 294110, 294120; runner-up 294130; 53 substitutes;
  identity exclusions 293339/294190; series gaps 293723/293919;
  viability exclusion 293711
fertilizers: 310430, 310510; runner-up 310221; 11 substitutes;
  identity exclusion 310590; series gaps 310229/310530/310551/310560;
  viability exclusion 310420
owner_designated_cases: []
selection_id: CASE-SELECTION-S15-b96de36ff0ce
selection_sha256: 65d1fe62f7dba44a7dd52f5bc40d4566576d696cc679b5c0a97e3f31efcd3fbe
S15_SELECTION_TWO_RUNS_BYTE_IDENTICAL
```

Inputs: screening inventory `231b8c3c…`; universe `758acdb4…`; product
families `0e37381f…`; terms `eebe4ffa…`; identity table `464f25e3…`;
five-document inventory `fc3842f4…`. The candidate list is the sorted selected
set exactly; no owner-designated line exists because OD-4 is no waiver.

T5 GREEN commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py tests/test_screening_config.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 -m ior_mvp.cases reconstruct-selection
```

T5 result: `43 passed in 2.66s` and
`CASE SELECTION RECONSTRUCTION PASS (2 records)`. Both S14 and S15 records
reconstruct byte-for-byte from recorded content hashes. No producer/register
record acquired after selection can reorder this pinned run.

## 2026-09-13T03:46:00Z — T6 W-A15b pre-window record

Purpose: bounded acquisition only after the pinned selection: two SPIMACO
Class-C PDFs, one SABIC Agri-Nutrients Class-C report and one SFDA Class-B
register-page observation. No personal-data field is authored; the HTML
DocumentRecord stores only the source page text layer and the later brief may
cite only verbatim stored spans. This search cannot establish absence of
API-synthesis capability.

Consultation phase 1 is at most eight verified-TLS HTTP requests: robots then
one landing/list page for each target host. It prints only response metadata,
relevant robots directives, target-path permission and candidate legal/terms/
privacy hrefs; bodies are not stored. A robots disallow or TLS/non-200 result
stops that host without bypass. No acquisition command runs until linked terms
are assessed.

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import re
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

UA = "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)"
HOSTS = (
    ("producer_spimaco", "https://ir.spimaco.com.sa/robots.txt", "https://ir.spimaco.com.sa/"),
    ("producer_sabic_agrinutrients_legacy", "https://safco.com.sa/robots.txt", "https://safco.com.sa/"),
    ("producer_sabic_agrinutrients_current", "https://www.sabic-agrinutrients.com/robots.txt", "https://www.sabic-agrinutrients.com/en/investor-relations/reports"),
    ("sfda_registers", "https://www.sfda.gov.sa/robots.txt", "https://www.sfda.gov.sa/en/drug-companies"),
)
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.rows.append((" ".join("".join(self.text).split()), self.href))
            self.href = None
def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        print("CONSULT", response.status, response.headers.get_content_type(), len(body), hashlib.sha256(body).hexdigest(), response.geturl())
        return body, response.geturl()
for source, robots_url, landing_url in HOSTS:
    print("HOST", source)
    try:
        robots_body, _ = fetch(robots_url)
    except Exception as exc:
        print("ROBOTS_UNAVAILABLE", type(exc).__name__, str(exc))
        continue
    robots_text = robots_body.decode("utf-8", errors="strict")
    directives = [line.strip() for line in robots_text.splitlines() if re.match(r"(?i)^(user-agent|disallow|allow):", line.strip())]
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())
    print("ROBOTS_RELEVANT", directives)
    print("ROBOTS_TARGET_ALLOWED", parser.can_fetch(UA, landing_url), landing_url)
    if not parser.can_fetch(UA, landing_url):
        continue
    try:
        landing_body, final_url = fetch(landing_url)
    except Exception as exc:
        print("LANDING_UNAVAILABLE", type(exc).__name__, str(exc))
        continue
    links = Links()
    links.feed(landing_body.decode("utf-8", errors="strict"))
    candidates = sorted({
        urllib.parse.urljoin(final_url, href)
        for text, href in links.rows
        if re.search(r"(?i)(terms|privacy|legal|usage|use.policy)", f"{text} {href}")
    })
    print("LEGAL_LINK_CANDIDATES", candidates)
PY
```

T1 result: `1 failed, 23 passed in 0.93s`. All 1.1 doubles, version-derived
prefix, CLI capture, stored-WCO address validation and byte-exact S14
reconstruction are GREEN. The sole expected RED is
`test_s14_selection_reproduces_from_recorded_inputs_with_families_1_2_0_live`,
which asserts the T2 live version before T2 changes it. The existing S14
selection record itself already reconstructs byte-for-byte through its recorded
1.1.0 family identity.

## 2026-09-13T03:19:00Z — T2 RED: families 1.2.0 and retained input

The superseded 1.1.0 bytes were copied to
`config/history/product_families.v1-1.1.0.yaml` before changing the live file,
as required by DD-4. Verification and RED commands recorded before execution:

```bash
sha256sum config/product_families.v1.yaml config/history/product_families.v1-1.1.0.yaml
cmp config/product_families.v1.yaml config/history/product_families.v1-1.1.0.yaml && echo PRODUCT_FAMILIES_1_1_RETENTION_BYTE_IDENTICAL
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_screening_config.py tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only tests/test_case_selection.py::test_s14_selection_reproduces_from_recorded_inputs_with_families_1_2_0_live
```

Retention proof: both files hash to
`62fa9c2944474ffbc5952801ba676a2adf750870a88969c59e22337b4564446b`;
`PRODUCT_FAMILIES_1_1_RETENTION_BYTE_IDENTICAL`.

Observed RED: `7 failed, 12 passed in 0.23s`. Five failures require the 1.2.0
version/membership rows, one shows that the new history file is not yet a
superseded live version/admitted by the old screening-only history rule, and
one is the expected S14 recorded-input pin.

T2 GREEN commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_screening_config.py tests/test_integrity_contract.py::test_config_history_files_are_superseded_versions_only tests/test_case_selection.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all
sha256sum config/history/product_families.v1-1.1.0.yaml data/cases/selection/CASE-SELECTION-S14-250cd516de0a.json
```

T2 result: `42 passed in 1.95s`; reconstruction exited 0 and retained
`SCREENING RECONSTRUCTION PASS (1 snapshots)`. The retained family file remains
`62fa9c2944474ffbc5952801ba676a2adf750870a88969c59e22337b4564446b`.
The frozen S14 selection remains
`19cb6e4c9b70152089e3689a77faf8be6de4b5147188e7087483e3e69deda016`,
reproduces byte-for-byte from the recorded family identity, and retains selected
lists coated steel `[721061, 721012]`, fabricated aluminium
`[760711, 760429]`, technical plastics `[392010]`.

## 2026-09-13T03:25:00Z — T3 RED: acquisition 1.5.0 and lists

Tests are authored first for the three exact source ids/classes, shared
observed-fact predicates, `regulatory_authority` restriction, three bounded
producer/register lists, and the WCO v2 Chapter 29/30/31 list. The WCO-list
test remains expected RED until W-A15a supplies verbatim index hrefs; the
ADR-023/no-1.4.0-history test remains expected RED until T11 by plan.

RED command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_document_lists.py
```

T3 result: `2 failed, 327 passed in 5.15s`. This is the exact expected
pre-window/deferred set:

- `test_wco_v2_entries_are_chapters_29_30_31_with_identity_support_only`
  remains RED because no Chapter URL may be guessed before W-A15a reads the
  index;
- `test_no_history_copy_required_for_1_4_0_is_documented` remains RED because
  ADR-023 is deferred to T11 after M15.

The 1.5.0 loader, 24-source exact set, classes C/C/B, shared observed-fact
validation, new publisher kind, and SPIMACO/SABIC Agri-Nutrients/SFDA list
contracts are GREEN offline.

## 2026-09-13T03:30:00Z — T4 W-A15a pre-window record

Purpose: obtain only the WCO HS 2022 Chapter 29/30/31 legal identity texts
(Class B, `TARGET_PRODUCT_IDENTITY` only) before any identity judgment or S15
selection. Consultation request count is three: robots, standard terms and the
HS 2022 index. The acquisition command then has `MAX_REQUESTS=4`: one governed
TERMS capture plus exactly three list entries. Verified TLS is mandatory; no
credential or `.env` is involved. The Chapter hrefs are copied verbatim from
the index result; the discovery-ledger 0629/0630/0631 strings are leads only.
Any non-200, disallow, TLS failure or missing href ends the affected unit as
typed UNAVAILABLE; no bypass or guessed URL.

Consultation command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser

URLS = (
    "https://www.wcoomd.org/robots.txt",
    "https://www.wcoomd.org/en/about-us/legal-instruments/wco-standard-terms-and-conditions_council-decision-n331.aspx",
    "https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition/hs-nomenclature-2022-edition.aspx",
)
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []
    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.rows.append((" ".join("".join(self.text).split()), self.href))
            self.href = None

bodies = {}
for url in URLS:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        bodies[url] = body
        print("CONSULT", response.status, response.headers.get_content_type(), len(body), hashlib.sha256(body).hexdigest(), response.geturl())
robots = bodies[URLS[0]].decode("utf-8", errors="strict")
print("ROBOTS_RELEVANT", [line.strip() for line in robots.splitlines() if re.match(r"(?i)^(user-agent|disallow|allow):", line.strip())])
parser = Links()
parser.feed(bodies[URLS[2]].decode("utf-8", errors="strict"))
for chapter in ("29", "30", "31"):
    matches = [(text, urllib.parse.urljoin(URLS[2], href)) for text, href in parser.rows if re.search(rf"\bChapter\s+{chapter}\b", text, re.I)]
    print("WCO_INDEX_HREF", chapter, matches)
PY
```

The corrected scan found exactly 91 family HS6 rows and exactly one stored WCO
subheading line for each. Stored-text identity judgments:

- ENTER `293339`, Chapter 29 page 17 lines 3/12/27: two-dash Other is
  the residual of the unfused-pyridine group and does not resolve one
  commercial product class;
- ENTER `294190`, Chapter 29 page 21 lines 10/17: Other is the residual
  of heading 29.41 after five named antibiotic classes;
- ENTER `310590`, Chapter 31 page 2 line 42 plus page 3 line 15: Other is
  the residual of heading 31.05 after named nutrient combinations/forms;
- KEEP `310510`, Chapter 31 page 2 lines 42–46: its identity is defined by
  tablets/similar forms or packages not exceeding 10 kg, not by a residual
  catch-all;
- KEEP the other considered rows
  `293319,293329,293349,293359,293369,293379,293399,293499,293590,293629,293690,293719,293729,293790,293919,293949,293959,293969,293979,293980,310229,310290,310319,310390,310490,310559`:
  the stored group/heading supplies a named chemical-structure, molecule,
  alkaloid, hormone, vitamin, or nutrient class. Under OD-3's accepted variant
  B and the 7604.29 counter-example, the word Other alone is not an exclusion.

The three entered rows carry H6, rule S14-CS-1.1, the COMPLETE WCO document id,
verbatim-normalized parent/group/subheading text, page/line maps and an explicit
identity judgment. The selected list is not authored.

Terms-v2 generation command recorded before execution. It maps all 91 frozen
screening rows to their unique stored WCO subheading line, uses specific group
context instead of a bare `Other`, and assigns producer sources only as ruled:
SABIC Agri-Nutrients for 310210; Ma'aden for 310530/310540.

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import json
from pathlib import Path

from ior_mvp.cases.selection import (
    GENERIC_DISCLOSURE_TERMS,
    canonical_bytes,
    validate_identity_exclusions,
    validate_terms_bundle,
)

root = Path(".")
screening = root / "data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/records"
codes = sorted(
    row["hs6"]
    for shard in ("29.json", "31.json")
    for row in json.loads((screening / shard).read_text(encoding="utf-8"))
    if row["hs6"][:4] in {"2933", "2934", "2935", "2936", "2937", "2939", "2941", "3102", "3103", "3104", "3105"}
)
document_paths = {
    "29": root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fd99902db1af-d01a792902be.json",
    "31": root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fe3ed4f5325a-88edcc1ee93d.json",
}
documents = {chapter: json.loads(path.read_text(encoding="utf-8")) for chapter, path in document_paths.items()}
other_context = {
    "293319": "Other compounds containing an unfused pyrazole ring",
    "293329": "Other compounds containing an unfused imidazole ring",
    "293339": "Other compounds containing an unfused pyridine ring",
    "293349": "Other compounds containing a quinoline or isoquinoline ring-system",
    "293359": "Other compounds containing a pyrimidine or piperazine ring",
    "293369": "Other compounds containing an unfused triazine ring",
    "293399": "Other heterocyclic compounds of heading 29.33",
    "293499": "Other nucleic-acid salts or heterocyclic compounds of heading 29.34",
    "293590": "Other sulphonamides",
    "293719": "Other polypeptide, protein or glycoprotein hormones",
    "293729": "Other steroidal hormones",
    "293790": "Other hormones and related products of heading 29.37",
    "293919": "Other opium alkaloids and derivatives",
    "293949": "Other ephedra alkaloids and derivatives",
    "293959": "Other theophylline or aminophylline derivatives",
    "293969": "Other rye-ergot alkaloids and derivatives",
    "293979": "Other alkaloids of vegetal origin",
    "293980": "Other alkaloids and derivatives of heading 29.39",
    "294190": "Other antibiotics",
    "310229": "Other ammonium-sulphate and ammonium-nitrate double salts or mixtures",
    "310319": "Other superphosphates",
    "310390": "Other mineral or chemical fertilisers, phosphatic",
    "310490": "Other mineral or chemical fertilisers, potassic",
    "310559": "Other nitrogen-and-phosphorus mineral or chemical fertilisers",
    "310590": "Other goods and fertilisers of heading 31.05",
}
source_rows = {
    "310210": ["producer_sabic_agrinutrients"],
    "310530": ["producer_maaden"],
    "310540": ["producer_maaden"],
}
term_overrides = {
    "310210": ["urea", "urea in aqueous solution"],
    "310530": ["DAP", "diammonium hydrogenorthophosphate", "diammonium phosphate"],
    "310540": ["MAP", "ammonium dihydrogenorthophosphate", "monoammonium phosphate"],
}
rows = []
for code in codes:
    document = documents[code[:2]]
    token = f"{code[:4]}.{code[4:]}"
    matches = [
        (page["page_index"], index, " ".join(line.split()))
        for page in document["pages"]
        for index, line in enumerate(page["lines"], 1)
        if token in line
    ]
    if len(matches) != 1:
        raise SystemExit(f"{code}: expected one stored WCO line, got {matches}")
    page_index, line_index, line = matches[0]
    description = line.split(token, 1)[1].lstrip(" -")
    if description.casefold() == "other":
        description = other_context[code]
    terms = sorted(term_overrides.get(code, [description]), key=str.casefold)
    if any(term.strip().casefold() in GENERIC_DISCLOSURE_TERMS for term in terms):
        raise SystemExit(f"{code}: generic term")
    rows.append(
        {
            "hs6": code,
            "sector_profile": "pharma_api" if code.startswith("29") else "fertilizers",
            "sources": source_rows.get(code, []),
            "terms": terms,
            "basis": (
                f"WCO HS 2022 subheading {token} legal text; "
                f"TITLE_VERIFICATION: {document['document_id']} "
                f"page {page_index} line {line_index}."
            ),
        }
    )
payload = {"schema_version": "1.1.0", "rule_id": "S14-CS-1.1", "rows": rows}
validate_terms_bundle(payload, expected_hs6=set(codes), rule_version="S14-CS-1.1")
identity_path = root / "data/cases/selection/identity-exclusions-v2.json"
identity = json.loads(identity_path.read_text(encoding="utf-8"))
validate_identity_exclusions(identity, documents=list(documents.values()), rule_version="S14-CS-1.1")
path = root / "data/cases/selection/hs6-disclosure-terms-v2.json"
path.write_bytes(canonical_bytes(payload))
print("TERMS_V2_ROWS", len(rows))
print("TERMS_V2_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
print("IDENTITY_V2_ROWS", [row["hs6"] for row in identity["entries"]])
print("IDENTITY_V2_SHA256", hashlib.sha256(identity_path.read_bytes()).hexdigest())
PY
```

Multi-page identity-address test GREEN: `1 passed`. The address scan exited 1
before producing data because screening shard files are JSON arrays, not
objects with a `records` member. Corrected read-only scan command recorded
before execution; no governed file changed:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
screening = root / "data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/records"
codes = []
for shard in ("29.json", "31.json"):
    codes.extend(row["hs6"] for row in json.loads((screening / shard).read_text(encoding="utf-8")))
records = {
    "29": json.loads((root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fd99902db1af-d01a792902be.json").read_text(encoding="utf-8")),
    "31": json.loads((root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fe3ed4f5325a-88edcc1ee93d.json").read_text(encoding="utf-8")),
}
family_codes = sorted(code for code in codes if code[:4] in {"2933", "2934", "2935", "2936", "2937", "2939", "2941", "3102", "3103", "3104", "3105"})
print("FAMILY_CODE_COUNT", len(family_codes))
for code in family_codes:
    token = f"{code[:4]}.{code[4:]}"
    matches = [
        (page["page_index"], index, " ".join(line.split()))
        for page in records[code[:2]]["pages"]
        for index, line in enumerate(page["lines"], 1)
        if token in line
    ]
    print("WCO_HS6_ADDRESS", code, matches)
PY
```

Offline inspection of the captured HTTP-200 index table verified these
verbatim pairings:

```text
29 | Organic chemicals.       | /-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/0629_2022e.pdf?la=en | 0629-2022E
30 | Pharmaceutical products. | /-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/0630_2022e.pdf?la=en | 0630-2022E
31 | Fertilisers.              | /-/media/wco/public/global/pdf/topics/nomenclature/instruments-and-tools/hs-nomenclature-2022/2022/0631_2022e.pdf?la=en | 0631-2022E
```

The v2 list was authored only after this check. W-A15a acquisition and offline
derivation commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_document_lists.py::test_wco_v2_entries_are_chapters_29_30_31_with_identity_support_only
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-documents SOURCE=wco_hs_nomenclature LIST_ID=wco_hs_nomenclature-v2 MAX_REQUESTS=4
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-documents SOURCE=wco_hs_nomenclature LIST_ID=wco_hs_nomenclature-v2
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
```

W-A15a RunReport summary: run `20260913T033253Z`, application exit 0,
`MAX_REQUESTS=4`, three COMPLETE units, zero unavailable units. Each document
returned HTTP 200 / `application/pdf`; coverage final cumulative budget values
are 2, 3 and 4. The top-level `requests_made=9` is the known KL-65 cumulative
aggregate-count artefact (`2+3+4`), not nine transport calls; the stored page
contracts and bound prove four transport fetches (one TERMS + three PDFs).

Built records:

- Chapter 29:
  `DOC-WCO-HS-NOMENCLATURE-fd99902db1af-d01a792902be`, raw 408,932
  bytes / SHA-256
  `d01a792902be71381aa2c8484ce7663a1bc9b7838ef692ee07db87c59e7d25bd`,
  21 pages / 1,115 lines;
- Chapter 30:
  `DOC-WCO-HS-NOMENCLATURE-4e3dbeff29ba-7ad8d2b476a9`, raw 161,048
  bytes / SHA-256
  `7ad8d2b476a97e2326fee5fbf6af0947d5213cc9a7f5e337667a7cbaa07af11d`,
  4 pages / 225 lines;
- Chapter 31:
  `DOC-WCO-HS-NOMENCLATURE-fe3ed4f5325a-88edcc1ee93d`, raw 136,798
  bytes / SHA-256
  `88edcc1ee93dec8e927500988c578fb155e6b66c89a2f7ab42dfb15c4f8865f2`,
  3 pages / 173 lines.

All three are `COMPLETE`, `quality_summary=PASS`,
`publisher_kind=nomenclature_authority`, evidence Class B, and support only
`TARGET_PRODUCT_IDENTITY`. Their first pages carry the expected chapter title
lines. Pre-manifest reconstruction exited 0 with
`DOCUMENT RECONSTRUCTION PASS (23 records, 23 artifacts)`.

Record-identity command recorded before execution:

```bash
sha256sum data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-{fd99902db1af-d01a792902be,4e3dbeff29ba-7ad8d2b476a9,fe3ed4f5325a-88edcc1ee93d}.json
wc -c data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-{fd99902db1af-d01a792902be,4e3dbeff29ba-7ad8d2b476a9,fe3ed4f5325a-88edcc1ee93d}.json
```

Record hashes/bytes:

```text
b60762f9c60b9ee26e176f6e8cf4ebee683549743ace207ecaf72ec604e2f168  83,236  Chapter 29 record
9d0cba7d3127b6dbc4aa715e667e7720ff60cbf5e2766926208e58b3a710dede  24,865  Chapter 30 record
8073a7e800d16b30b7ba169e6de6cc213b6005d15699fd36c7a82267bc2238e4  17,820  Chapter 31 record
```

## 2026-09-13T03:36:00Z — T5 RED: stored-text exclusions and S15 pin

The real-output pin and a multi-page WCO-address contract are authored before
the identity table, terms table or selection record. The multi-page case is
required because heading 31.05 is on stored Chapter 31 page 2 while subheading
3105.90 is on page 3; both must be verified without weakening the verbatim
address rule.

RED command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py::test_identity_row_supports_multi_page_wco_group_address tests/test_case_selection.py::test_s15_selection_from_frozen_screening_snapshot_matches_recorded_list
```

Observed RED: both tests failed for their intended reasons: the validator
accepts only a single-page address, and no S15 selection record exists.

Stored-text address scan and the first focused GREEN command recorded before
execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py::test_identity_row_supports_multi_page_wco_group_address
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
screening = root / "data/screening/snapshots/SCREENING-SAU-2026-09-12-9b6b22032fd8/records"
codes = []
for shard in ("29.json", "31.json"):
    payload = json.loads((screening / shard).read_text(encoding="utf-8"))
    codes.extend(row["hs6"] for row in payload["records"])
records = {
    "29": json.loads((root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fd99902db1af-d01a792902be.json").read_text(encoding="utf-8")),
    "31": json.loads((root / "data/documents/wco_hs_nomenclature/records/DOC-WCO-HS-NOMENCLATURE-fe3ed4f5325a-88edcc1ee93d.json").read_text(encoding="utf-8")),
}
family_codes = sorted(code for code in codes if code[:4] in {"2933", "2934", "2935", "2936", "2937", "2939", "2941", "3102", "3103", "3104", "3105"})
print("FAMILY_CODE_COUNT", len(family_codes))
for code in family_codes:
    token = f"{code[:4]}.{code[4:]}"
    matches = [
        (page["page_index"], index, " ".join(line.split()))
        for page in records[code[:2]]["pages"]
        for index, line in enumerate(page["lines"], 1)
        if token in line
    ]
    print("WCO_HS6_ADDRESS", code, matches)
PY
```

The corrective request returned the same HTTP 200 body and SHA-256
`5cb88ba09b95487fad80781706dde3144a115dca85232ff342b194043b20ba24`,
but the bounded context predicate again emitted no hrefs. The response itself
is available; only the in-memory predicate is defective. One final diagnostic
index request is recorded before execution to emit the returned HTML to
captured stdout for offline text inspection. It writes no repository or
governed evidence file and cannot itself supply an identity row. No further
index request is permitted in this window after this diagnostic.

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import sys
import urllib.request

url = "https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition/hs-nomenclature-2022-edition.aspx"
request = urllib.request.Request(
    url,
    headers={"User-Agent": "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    body = response.read()
    print("DIAGNOSTIC_INDEX", response.status, response.headers.get_content_type(), len(body), hashlib.sha256(body).hexdigest(), response.geturl())
    sys.stdout.buffer.write(body)
PY
```

Consultation result: robots, terms and index each returned HTTP 200 under
verified TLS. Bodies were not stored. The robots directives disallow only
Sitecore/application/search paths and do not disallow the targeted index,
terms or `/-/media/` PDF paths. The first in-memory anchor-text predicate
returned no Chapter 29/30/31 rows. This is the same bounded parser condition
recorded in S14a KL-95 and does not authorize guessing the numeric filenames.

One disclosed corrective index read is therefore recorded before execution.
It searches the freshly returned index bytes for each literal Chapter label
and reports only href attributes inside that label's bounded HTML context:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import html
import re
import urllib.parse
import urllib.request

url = "https://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition/hs-nomenclature-2022-edition.aspx"
request = urllib.request.Request(
    url,
    headers={"User-Agent": "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    body = response.read()
    print("CORRECTIVE_INDEX", response.status, response.headers.get_content_type(), len(body), hashlib.sha256(body).hexdigest(), response.geturl())
text = body.decode("utf-8", errors="strict")
for chapter in ("29", "30", "31"):
    matches = list(re.finditer(rf"Chapter(?:\s|&nbsp;|&#160;)+{chapter}\b", text, re.I))
    rows = []
    for match in matches:
        context = text[max(0, match.start() - 1500):match.end() + 1500]
        for raw_href in re.findall(r'href\s*=\s*["\x27]([^"\x27]+)["\x27]', context, re.I):
            href = urllib.parse.urljoin(url, html.unescape(raw_href))
            if "_2022e.pdf" in href.casefold():
                rows.append(href)
    print("WCO_CONTEXT_HREF", chapter, sorted(set(rows)))
PY
```

Observed RED: `264 failed, 65 passed in 6.97s`. The large count is the expected
fixture fan-out from the still-pinned 1.4.0 validator and old exact source-id
set; the three plan-named list/source behaviours also fail because their code
and files do not yet exist. No failure depends on network access.

T3 GREEN-attempt command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_document_lists.py
```

Observed RED: `17 failed, 7 passed in 0.26s`. The failures are caused by the
missing 1.1 API/CLI/reconstruction behaviour and the deliberately still-live
families version 1.1.0. Representative failures: `select_cases_from_records`
does not accept `rule_version`, `validate_identity_exclusions` does not accept
stored documents, `write_selection` does not accept a version-checking prefix,
`resolve_recorded_input`/`reconstruct_selection` are not exposed by the
selection module, the CLI rejects `--rule-version`/`--record-prefix`, and the
S14 retained-input pin sees live families 1.1.0 rather than the T2 target
1.2.0. This is the expected feature-missing RED, not a syntax or fixture error.

T1 GREEN-attempt command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py
```

<!-- S15A_APPEND_CURSOR_001 -->

T6 consultation phase 1 results:

- `ir.spimaco.com.sa`: robots HTTP 200; `/media/` and the landing page are
  allowed; landing HTTP 200; linked privacy URL is on the separate
  `spimaco.com.sa` host;
- `safco.com.sa`: robots HTTP 200 with empty Disallow; landing HTTP 200;
  linked legal-disclaimer URL observed;
- `www.sabic-agrinutrients.com`: robots HTTP 200 with empty Disallow; reports
  page HTTP 200; linked legal-disclaimer URL observed;
- `www.sfda.gov.sa`: robots HTTP 200 and the target page is allowed; Drug
  Companies page HTTP 200; linked privacy-policy and terms-of-use URLs
  observed.

Consultation phase 2 is recorded before execution. It first attempts the
separate SPIMACO corporate robots URL; the linked privacy page is requested
only if robots is reachable and permits it. The already-allowed same-host
legal/terms/privacy pages are each read once. Only response metadata and
bounded visible-text snippets around legal-use terms are printed; no body is
stored.

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import hashlib
import re
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

UA = "industrial-opportunity-resolution-mvp/0.2.0 (public-data acquisition; offline runtime)"
class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.suppressed = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template", "noscript"}:
            self.suppressed += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "template", "noscript"} and self.suppressed:
            self.suppressed -= 1
    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)
def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
        print("LEGAL_CONSULT", response.status, response.headers.get_content_type(), len(body), hashlib.sha256(body).hexdigest(), response.geturl())
        return body, response.geturl()
targets = []
robots_url = "https://spimaco.com.sa/robots.txt"
privacy_url = "https://spimaco.com.sa/privacy/privacy-en.html"
try:
    robots_body, _ = fetch(robots_url)
    robots_text = robots_body.decode("utf-8", errors="strict")
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_text.splitlines())
    allowed = parser.can_fetch(UA, privacy_url)
    print("SPIMACO_CORPORATE_PRIVACY_ALLOWED", allowed)
    if allowed:
        targets.append(("producer_spimaco", privacy_url))
except Exception as exc:
    print("SPIMACO_CORPORATE_ROBOTS_UNAVAILABLE", type(exc).__name__, str(exc))
targets.extend(
    [
        ("producer_sabic_agrinutrients_legacy", "https://safco.com.sa/en/legal-dislaimer"),
        ("producer_sabic_agrinutrients_current", "https://www.sabic-agrinutrients.com/en/legal-dislaimer"),
        ("sfda_privacy", "https://www.sfda.gov.sa/en/privacy-policy"),
        ("sfda_terms", "https://www.sfda.gov.sa/en/terms-of-use"),
    ]
)
for source, url in targets:
    print("LEGAL_TARGET", source)
    try:
        body, _ = fetch(url)
    except Exception as exc:
        print("LEGAL_UNAVAILABLE", type(exc).__name__, str(exc))
        continue
    parser = VisibleText()
    parser.feed(body.decode("utf-8", errors="strict"))
    text = " ".join(" ".join(parser.parts).split())
    matches = []
    for match in re.finditer(r"(?i)(copyright|download|reproduc|distribut|personal data|privacy|terms of use|use of)", text):
        snippet = text[max(0, match.start() - 140):match.end() + 260]
        if snippet not in matches:
            matches.append(snippet)
        if len(matches) == 8:
            break
    print("LEGAL_TEXT_SNIPPETS", matches)
PY
```

<!-- S15A_APPEND_CURSOR_002 -->

T6 consultation phase 2 outcomes:

- SPIMACO corporate `spimaco.com.sa/robots.txt` failed normal certificate
  verification; the linked privacy body was not requested and TLS was not
  bypassed. The separate `ir.spimaco.com.sa` robots/landing consultation
  remains successful; document-reuse terms were not identified within those
  sources. Per the owner-approved UNICOIL precedent, the public-open source
  remains `terms_reference=UNAVAILABLE` and `license_capture_required=false`;
- both legacy and current SABIC Agri-Nutrients legal-disclaimer pages returned
  HTTP 200. Their visible text states that browsing/downloading/copying is
  subject to the linked terms; no explicit storage prohibition or numeric rate
  was identified within the bounded snippets. The legacy terms URL is captured
  by the connector;
- SFDA privacy and terms pages returned HTTP 200. The terms reserve SFDA
  copyright and describe the portal as available for personal use; the
  register page is acquired only as a bounded public-authority observation
  under captured terms, with no unrestricted-reuse claim.

W-A15b acquisition parameters are fixed before execution:

- `producer_spimaco`, list v1, two document units, `MAX_REQUESTS=2`, no terms
  capture;
- `producer_sabic_agrinutrients`, list v1, one TERMS + one document,
  `MAX_REQUESTS=2`;
- `sfda_registers`, list v1, one TERMS + one document, `MAX_REQUESTS=2`.

No retry beyond each bound; any non-200/TLS/policy result becomes typed
UNAVAILABLE. Commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py tests/test_acquisition_document_lists.py
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-documents SOURCE=producer_spimaco LIST_ID=producer_spimaco-v1 MAX_REQUESTS=2
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-documents SOURCE=producer_sabic_agrinutrients LIST_ID=producer_sabic_agrinutrients-v1 MAX_REQUESTS=2
IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-documents SOURCE=sfda_registers LIST_ID=sfda_registers-v1 MAX_REQUESTS=2
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-documents SOURCE=producer_spimaco LIST_ID=producer_spimaco-v1
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-documents SOURCE=producer_sabic_agrinutrients LIST_ID=producer_sabic_agrinutrients-v1
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-documents SOURCE=sfda_registers LIST_ID=sfda_registers-v1
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_size_budget.py
```

<!-- S15A_APPEND_CURSOR_003 -->

## 2026-09-13T03:54:00Z — Binding stop at T6

The offline acquisition source/list suites reached their exact deferred state:
`1 failed, 328 passed in 5.12s`; the only failure is the T11-deferred
ADR-023/no-1.4.0-history assertion.

The first W-A15b acquisition command
(`producer_spimaco`, list v1, `MAX_REQUESTS=2`) exited at local connector
lookup before transport:

```text
KeyError: 'Unknown source_id: producer_spimaco'
make: *** [Makefile:164: acquire-documents] Error 1
```

No RunReport was emitted, no request budget was charged, no HTTP request was
made by the acquisition command and no raw acquisition artifact was written.
The preceding robots/terms consultations remain the only T6 network activity.
The SABIC Agri-Nutrients and SFDA acquisition commands were not attempted after
this deterministic failure.

Root cause verified in current code:

- `src/ior_mvp/acquisition/source_config.py` now correctly governs the three
  S15 source ids;
- `src/ior_mvp/acquisition/connectors/base.py::default_registry` is an explicit
  fixed map ending at the S14 document sources and has no S15 ids;
- `src/ior_mvp/acquisition/connectors/documents.py` defines one explicit
  `DocumentConnector` subclass per source and has no S15 subclasses;
- `DOCUMENT_SOURCE_STAGES` is not used to construct the connector registry.

The minimum persisted fix therefore requires edits to
`src/ior_mvp/acquisition/connectors/documents.py` and
`src/ior_mvp/acquisition/connectors/base.py`. Both are outside plan DD-14
`files.modify`; O-2/SC-2a requires every acquisition module not named there to
remain byte-identical. A command-local injected registry would conceal the
missing product contract and is not an authorized workaround. SC-2a is
therefore binding. T6–T10 stop here pending an owner-approved plan amendment
that adds these two files and their tests, or another explicit ruling.

Read-only stop-evidence commands recorded before execution:

```bash
git status --short
git diff --name-only 1289e31e50c1d835760f6943e697d6d537ac0a18
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_selection.py tests/test_screening_config.py tests/test_acquisition_config.py tests/test_acquisition_document_lists.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 -m ior_mvp.cases reconstruct-selection
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/verify_integrity.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
git diff --stat 1289e31e50c1d835760f6943e697d6d537ac0a18 -- data/snapshots/public data/synthetic data/golden browser_tests ':(glob)src/ior_mvp/*.py' src/ior_mvp/static src/ior_mvp/cases/brief.py src/ior_mvp/cases/projection.py src/ior_mvp/cases/build.py config/project.yaml config/thresholds.v1.yaml config/sector_profiles.v1.yaml config/evidence_policy.v1.yaml config/ui_strings.v1.yaml config/decision_narratives.v1.yaml config/entity_resolution.v1.yaml config/screening.v1.yaml
git ls-files --others -- data/snapshots/public data/synthetic data/golden browser_tests
```

<!-- S15A_APPEND_CURSOR_004 -->

Focused stop evidence: `1 failed, 371 passed in 7.67s`; the sole failure is
the expected T11-deferred ADR-023 assertion. Selection reconstruction remains
`CASE SELECTION RECONSTRUCTION PASS (2 records)`. Pre-manifest integrity fails
only on the two authorized live configuration hashes:

```text
config/acquisition_sources.v1.yaml expected 1da67cc7… actual ee2ca701…
config/product_families.v1.yaml expected 62fa9c29… actual 0e37381f…
```

No manifest generator was run. Protected-root diff and untracked checks
printed no paths.

Muhasib audit commands recorded before execution:

```bash
git diff --check
git diff --stat 1289e31e50c1d835760f6943e697d6d537ac0a18
git diff 1289e31e50c1d835760f6943e697d6d537ac0a18 -- src/ior_mvp/acquisition/source_config.py src/ior_mvp/acquisition/documents/lists.py src/ior_mvp/cases/selection.py src/ior_mvp/cases/cli.py src/ior_mvp/screening/config.py tests/test_acquisition_config.py tests/test_acquisition_document_lists.py tests/test_case_selection.py tests/test_integrity_contract.py tests/test_screening_config.py config/acquisition_sources.v1.yaml config/product_families.v1.yaml
```

IDE lint diagnostics are checked for every changed Python file. New S15
evidence paths are scanned for the credential-header name and synthetic
markers; no secret value is ever inspected.

<!-- S15A_APPEND_CURSOR_005 -->

## 2026-09-13T04:00:00Z — Stop audit

Full pytest at the T6 stop: `12 failed, 2438 passed, 1 warning in 51.35s`.
The exact failure set and causes are recorded in `test_evidence.md`: one
T11-deferred ADR test, one T12-deferred manifest test, five incomplete-source
raw/detector tests caused by the T6 registry stop, and four outside-DD-14
screening API/fixture expectations still pinned to product families 1.1.0.

`git diff --check` exited 0. The tracked diff was read in full. IDE diagnostics
reported no linter errors. New case/document evidence contains neither the
credential-header name nor a synthetic marker. No raw file exists for any of
the three T6 sources. Protected-root tracked and untracked checks are empty.

Muhasib: `BLOCKED`. T0–T5 evidence is supported by actual outputs; T6–T10,
brief tri-states and engine results are not claimed. No manifest, git-state
mutation, secret access, primary-checkout write, s14b write, threshold change,
frozen-root change, synthetic input, hand-edited selected list or unsupported
absence claim occurred. The next authorized action is an owner plan amendment
covering the two connector-registry production files and associated tests.

<!-- S15A_APPEND_CURSOR_006 -->

## 2026-09-13T04:02:00Z — Resume under owner ruling OD-12

OD-12 extends DD-14/O-2 for additive-only source registration in
`acquisition/connectors/documents.py` and `acquisition/connectors/base.py`.
The three new source ids are `producer_spimaco`,
`producer_sabic_agrinutrients` and `sfda_registers`.
`wco_hs_nomenclature-v2` is the already validated DocumentList id under the
existing registered source id `wco_hs_nomenclature`; no fourth source id is
invented.

RED commands recorded before execution:

```bash
sha256sum .autonomous-workflow/owner-decisions/20260913-s15-plan-1-rulings.md
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py::test_default_registry_contains_all_s15_document_sources_and_wco_v2_list
```

<!-- S15A_APPEND_CURSOR_007 -->

OD-12 ruling SHA-256:
`41ea4497df96502738834421debd2bc4f5c3127c09e56d7cf56c606b57775a73`.

RED observed: the focused test failed at the first new id with
`AssertionError: assert 'producer_spimaco' in registry.ids()` (`1 failed`).
The existing `wco_hs_nomenclature` id remains the connector for the governed
`wco_hs_nomenclature-v2` list.

<!-- S15A_APPEND_CURSOR_008 -->

GREEN command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_config.py::test_default_registry_contains_all_s15_document_sources_and_wco_v2_list tests/test_acquisition_config.py::test_default_registry_contains_all_s14_document_sources
```

<!-- S15A_APPEND_CURSOR_009 -->

Registration GREEN: `2 passed in 0.11s`.

W-A15b resumed under the parameters recorded at
2026-09-13T03:46:00Z. Outcomes:

- `producer_spimaco`: the first unit was requested once and stored COMPLETE
  (`run_id=20260913T035150Z`, query `1eb1608f…`, HTTP 200, 322,368 bytes,
  one request). The command then raised local
  `pypdf.errors.DependencyError: cryptography>=3.1 is required for AES
  algorithm` while classifying that body, so it emitted no aggregate
  RunReport and did not request E-002. The command was not retried. Offline
  build subsequently derived a COMPLETE 8-page/373-line record for E-001;
  E-002 remains UNAVAILABLE because it was not attempted after the bounded
  command failure.
- `producer_sabic_agrinutrients`: RunReport
  `20260913T035235Z`, exit 0, 2 requests (TERMS + DOCUMENT), one COMPLETE
  unit, HTTP 200, 7,313,847 bytes, 47 pages / 3,088 lines. The extractor
  warned that rotated text makes output incomplete.
- `sfda_registers`: RunReport `20260913T035254Z`, exit 0, 2 requests
  (TERMS + DOCUMENT), one COMPLETE unit, HTTP 200, 67,381 bytes, 1 page /
  2,335 lines.

Built records:

```text
DOC-PRODUCER-SPIMACO-1eb1608ff72b-884197ccc5a7
DOC-PRODUCER-SABIC-AGRINUTRIENTS-d853eeed63fa-42fdc62825bc
DOC-SFDA-REGISTERS-e4dc16615481-5f1b33b9c8fc
```

Raw-size budget proof: `1 passed in 0.06s`.

<!-- S15A_APPEND_CURSOR_010 -->

## 2026-09-13T03:55:00Z — T7 W-P15 pre-window record

Purpose: acquire UN Comtrade V3 partner detail for exactly the four pinned S15
selection lines (`294110`, `294120`, `310430`, `310510`), reporter 682,
period 2024, imports, HS, `partner_dimension_query=&includeDesc=true`.
The source's recorded terms URL is requested before each data unit by the
license-capture contract. `MAX_REQUESTS=2` therefore bounds every unit to one
TERMS request plus one PARTNERS request. No WITS request is permitted.

The credential is exported only by sourcing the primary checkout's ignored
`.env` inside this acquisition command; no value is printed, read as text or
persisted:

```bash
set -a; . /home/barami/projects/industrial-opportunity-resolution-mvp/.env; set +a; IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-partners SOURCE=un_comtrade CANDIDATES=data/cases/selection/comtrade-partners-s15-v1.json YEARS=2024 FLOWS=imports MAX_REQUESTS=2 PARAMETERS='partner_dimension_query=&includeDesc=true'
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-snapshots KIND=partners SOURCE=un_comtrade
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
```

<!-- S15A_APPEND_CURSOR_011 -->

The first command exited locally before transport:
`AcquisitionConfigurationError: max_requests 2 below minimum 5`. The
pipeline budgets the four units plus one shared TERMS request across the
invocation; it does not apply `MAX_REQUESTS` separately to each unit. No HTTP
request was made and no credential material was emitted. The corrected bound
is five total requests (one shared TERMS + four data), which is 1.25 requests
per unit and remains within OD-5's ≤2 HTTP per unit.

Corrected command recorded before execution:

```bash
set -a; . /home/barami/projects/industrial-opportunity-resolution-mvp/.env; set +a; IOR_ACQUISITION_LIVE=1 UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make acquire-partners SOURCE=un_comtrade CANDIDATES=data/cases/selection/comtrade-partners-s15-v1.json YEARS=2024 FLOWS=imports MAX_REQUESTS=5 PARAMETERS='partner_dimension_query=&includeDesc=true'
```

<!-- S15A_APPEND_CURSOR_012 -->

W-P15 acquisition RunReport: run `20260913T035527Z`, exit 0, four
COMPLETE units (`294110`, `294120`, `310430`, `310510`), each one page with
`PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000`, no unavailable reason.
The shared budget reached five actual HTTP requests (one TERMS plus four
data), within the corrected maximum. The aggregate RunReport serializes
`requests_made=14` because `_run_units` sums the cumulative per-unit values
2+3+4+5; this is a reporting defect, not 14 transport requests, and is not
changed in this preparation because `pipeline.py` is outside DD-14.

The offline snapshot build then stopped at the canonical write-once guard:

```text
SnapshotWriteConflict:
data/snapshots/partners/PARTNERS-SAU-UN-COMTRADE-2026-09-13.json
```

That path is a pre-existing tracked S14 artifact and has SHA-256
`e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b`.
`git diff --exit-code -- <path>` passed after the refusal, proving it was not
changed. The plan does not authorize replacement of a write-once snapshot or
define a second identity on the same `as_of_date`; selecting either policy is
an owner/architecture decision. T8–T10 are not started.

Stop-status verification commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
git diff --check
git diff --stat 1289e31e50c1d835760f6943e697d6d537ac0a18
git diff --exit-code 1289e31e50c1d835760f6943e697d6d537ac0a18 -- data/snapshots/public data/synthetic data/golden browser_tests
git ls-files --others --exclude-standard -- data/snapshots/public data/synthetic data/golden browser_tests
```

<!-- S15A_APPEND_CURSOR_013 -->

The stop-state full suite exposed the two additional exact registry oracles
and the stored-artifact source-set oracle covered by OD-12/O-2. They were
updated additively to the same three source ids. Focused GREEN command
recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_connectors.py::test_default_registry_ids tests/test_acquisition_document_connectors.py::test_default_registry_has_twenty_four_ids_and_document_kinds tests/test_acquisition_stored_artifacts.py::test_repository_raw_store_has_no_stored_evidence_problems tests/test_acquisition_stored_artifacts.py::test_detector_meta_credential_absent_credential_env_var_changed tests/test_acquisition_stored_artifacts.py::test_detector_sentinel_configured_source_is_uncredentialed
```

<!-- S15A_APPEND_CURSOR_014 -->

The first focused run was RED only because the exact tuple placed
`sfda_registers` after `tadawul_disclosures`; `ConnectorRegistry.ids()` is
sorted. After correcting the oracle ordering, all five adjusted tests passed:
`5 passed in 0.45s`.

The pre-oracle stop-state full suite was `11 failed, 2450 passed, 1 warning in
51.38s`. A final stop-state full suite command is recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
```

<!-- S15A_APPEND_CURSOR_015 -->

Final pytest: `6 failed, 2455 passed, 1 warning in 52.98s`. The exact six
deferred failures and their gates are recorded in `test_evidence.md`.

Muhasib: `BLOCKED_ON_PARTNER_SNAPSHOT_WRITE_ONCE_IDENTITY`. OD-12 was applied
test-first and its connector/source-set oracles are GREEN. T6 evidence is
reported at the unit level, including the SPIMACO local parser exception and
unattempted E-002; no source availability is overstated. T7's four acquired
units are stored and COMPLETE, but no partner snapshot or derived tri-state
is claimed because the canonical write was refused. The RunReport's
cumulative-sum defect is disclosed separately from the five-request shared
budget. T8–T10, briefs and engine results are not claimed. No manifest was
run; no existing write-once snapshot was replaced; protected roots, git
state, thresholds and primary/s14b worktrees were not changed; no credential
material was printed or stored.

Required owner decision: define the governed same-day partner-snapshot policy
for the pre-existing tracked
`PARTNERS-SAU-UN-COMTRADE-2026-09-13.json`—either authorize a new canonical
identity/version that preserves the old bytes, or explicitly authorize and
specify replacement/aggregation semantics plus the affected manifest oracle.
Work cannot resume at T8 until that decision is recorded.

<!-- S15A_APPEND_CURSOR_016 -->

## 2026-09-13T04:08:00Z — Resume under OD-13

Reviewer confirmation IAC-OD12-REGISTRATION was checked against the candidate:
exactly three empty `DocumentConnector` subclasses and three registry entries;
24 sorted ids; no second WCO connector; exact tuple, DD-22 kinds and both
stored-artifact source sets cover the three ids.

OD-13 authorizes scoped analytical-snapshot identity only when the unscoped
same-kind/source/nomenclature/as-of path already exists with different bytes.
The scope token uses repository-canonical JSON bytes of the sorted unit-key
arrays. The scoped record carries those exact `scope_units` plus the unscoped
id in `coexists_with`; it never carries `supersedes`.

RED command recorded before execution:

```bash
sha256sum .autonomous-workflow/owner-decisions/20260913-s15-plan-1-rulings.md
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_snapshots.py::test_same_day_collision_uses_deterministic_scope_and_reconstructs
```

<!-- S15A_APPEND_CURSOR_017 -->

OD-13 ruling SHA-256:
`94100b0052715909751621745ed668e6e7ce096ac6ac828bf3225347929f8861`.
RED reproduced the original `SnapshotWriteConflict`. GREEN plus kind-registry
and reconstruction suites: `52 passed`; the only failure was the expected
T12-deferred manifest coverage assertion.

Production scoped-build and reconstruction commands recorded before
execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-snapshots KIND=partners SOURCE=un_comtrade
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
```

<!-- S15A_APPEND_CURSOR_018 -->

T7 scoped snapshot built:
`PARTNERS-SAU-UN-COMTRADE-2026-09-13-b77e879286ae`.
The existing unscoped snapshot remains byte-unchanged. Full offline
reconstruction passed with `RECONSTRUCTION PASS (5 snapshots, 44 artifacts)`.

T8 RED command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_entity_resolution_artifact.py::test_s15_mentions_v3_spans_verified_and_third_artifact_reconstructs
```

<!-- S15A_APPEND_CURSOR_019 -->

T8 RED: `mentions-v3.json` did not exist. The authored list contains only two
verbatim PUBLISHER_NAME spans: SPIMACO page 8 line 7 and SABIC
Agri-Nutrients page 5 line 45. No plant span is promoted without a governed
same-line company/site association; no SPIMACO E-002 claim is made.

Build and GREEN commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make build-entities MENTION_LIST_ID=mentions-v3
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_entity_resolution_artifact.py::test_s15_mentions_v3_spans_verified_and_third_artifact_reconstructs
```

<!-- S15A_APPEND_CURSOR_020 -->

T8 build initially rejected the one-based addresses; correcting SPIMACO to
page 8 line 8 and SABIC Agri-Nutrients to page 5 line 46 produced
`ENTITIES-2026-09-13-219b097bddda`. Both links are
`EXACT_DOCUMENT_EVIDENCE`; entity test GREEN (`1 passed in 0.19s`).

T9 RED command recorded before brief creation:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_case_briefs_real.py::test_each_s14_brief_validates_and_builds_deterministically tests/test_case_briefs_real.py::test_s15_briefs_reference_scoped_observed_partner_units
```

<!-- S15A_APPEND_CURSOR_021 -->

T9 RED found that provider page counts include the World aggregate. The
validator's stored-row filter proved the honest non-World counts:
294110=10, 294120=4, 310430=11, 310510=11. Corrected brief validation and
scoped-partner tests are GREEN (`2 passed in 2.42s`).

Provisional engine proof command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q -s tests/test_case_briefs_real.py
```

<!-- S15A_APPEND_CURSOR_022 -->

T9 provisional suite: `8 passed in 8.70s`. The engine test proves all nine
built snapshots are INVESTIGATE with null route; exact S15 fired sets are
recorded below from a separate evidence-print command.

T10 RED commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_entity_resolution_cli.py::test_reconstruct_script_entities_temp_root_exit_0_and_three_pass_lines tests/test_case_selection.py::test_makefile_wires_case_selection_reconstruction
```

<!-- S15A_APPEND_CURSOR_023 -->

T10 RED reproduced both missing integrations. Script and Makefile wiring are
GREEN (`2 passed in 0.55s`).

Final preparation proof commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import json
from pathlib import Path
from ior_mvp.capability import evaluate_capability
from ior_mvp.cases.build import build_from_brief
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.public_decision import compute_public_decision
from ior_mvp.public_snapshot import capability_hard_gate_names
from ior_mvp.rules import evaluate_rules
for hs6 in ("294110", "294120", "310430", "310510"):
    path = PROJECT_ROOT / "data" / "cases" / "briefs" / f"CASE-BRIEF-SAU-H6-{hs6}-v1.json"
    snapshot = build_from_brief(path, root=PROJECT_ROOT)
    rules = evaluate_rules(snapshot)
    capability = evaluate_capability(snapshot["opportunity"]["sector_profile"], snapshot["domestic_capability"]["public_dimension_states"], snapshot["domestic_capability"]["profile_hard_gates"], capability_hard_gate_names(snapshot["domestic_capability"]))
    decision = compute_public_decision(snapshot, rules, capability)
    print(json.dumps({"hs6": hs6, "state": decision["state"], "route_code": decision["route_code"], "reason": decision["decision_reason_code"], "fired": [row["rule_id"] for row in rules if row.get("fired") is True]}, sort_keys=True))
PY
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make reconstruct-selection
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
```

<!-- S15A_APPEND_CURSOR_024 -->

S15 provisional engine results (all honest, no input adjusted):

```text
294110 INVESTIGATE route=null ROUTE_CHANGING_EVIDENCE_UNRESOLVED
294120 INVESTIGATE route=null ROUTE_CHANGING_EVIDENCE_UNRESOLVED
310430 INVESTIGATE route=null ROUTE_CHANGING_EVIDENCE_UNRESOLVED
310510 INVESTIGATE route=null ROUTE_CHANGING_EVIDENCE_UNRESOLVED
fired each: R0,R1-D,R2,R3,R4-D,R10,R12
```

All four partner-detail tri-states are `PARTNER_DETAIL_OBSERVED` with the
scoped snapshot and non-World row counts 10/4/11/11. Capability dimensions
are all `U`; all profile hard gates, verified presence and same-process-family
facts are UNAVAILABLE.

Selection-only reconstruction passed for both records. Full reconstruction
passed: 0 committed snapshots / 9 briefs; 5 acquisition snapshots / 44
artifacts; 26 document records; 3 entity artifacts / 46 links; 1 screening
snapshot; 2 selection records.

The first final suite was `8 failed, 2457 passed, 1 warning`; two newly
exposed count oracles were within T8/T9 scope (S14 artifact discovery must
tolerate the third artifact; case reconstruction now counts 9 briefs).
Focused and final rerun commands recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_entity_resolution_artifact.py tests/test_integrity_contract.py::test_reconstruct_script_prints_case_reconstruction_pass_line tests/test_case_briefs_real.py
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
```

<!-- S15A_APPEND_CURSOR_025 -->

Final focused proof: `16 passed in 9.48s`. Final preparation suite:
`6 failed, 2459 passed, 1 warning in 57.55s`; exact deferred set is in
`test_evidence.md`.

File set at PREP handoff:

- production/config: `Makefile`, `scripts/reconstruct_snapshot.py`,
  acquisition connector base/documents, source config, document-list policy,
  kind registry and snapshots, case selection/CLI, screening config,
  acquisition sources 1.5.0 and product families 1.2.0;
- tests: acquisition config/connectors/document connectors/document lists/
  snapshots/stored artifacts, case briefs/selection, entity artifact/CLI,
  integrity and screening config;
- new governed inputs/evidence: retained families 1.1.0; S15 selection,
  terms, exclusions and partner candidates; four briefs; WCO v2 list,
  records and raw evidence; producer/register lists, records and raw
  evidence; Comtrade partner raw run and scoped snapshot; mentions-v3 and
  the third entity artifact; append-only slice records.

Muhasib: `PREP_HANDOFF_PENDING_M15`, not delivery complete. Acceptance
criteria T0–T10 are traced to actual RED/GREEN, acquisition, reconstruction
and engine outputs. Assumptions are limited to repository-canonical JSON as
OD-13's hash byte representation and analyst-labelled Arabic translations.
The scoped snapshot includes the complete latest selected-unit set, retaining
the 59 historical typed exclusions and prior 721061 unit alongside the four
new COMPLETE units, as DD-7 requires; it does not supersede the S14 snapshot.
Known limitations: SPIMACO E-002 was never requested after the local bounded
parser failure; the Comtrade aggregate RunReport overstates five transport
requests as 14 by summing cumulative coverage counters; rotated SABIC text
is incomplete; all new capability dimensions and hard gates remain unknown.
No manifest, commit, rebase, external write, secret disclosure, frozen-root
change or primary/s14b write occurred. Independent OD-13 confirmation,
M15 integration, T11 authority text/ADR/KLs, T12 manifest/CI and reviewer
approval remain outstanding.

<!-- S15A_APPEND_CURSOR_026 -->

## 2026-09-13T04:27:00Z — OD-14 correction

IAC-OD13 and OD-14 were read from the owner rulings. The incorrect uncommitted
64-unit scoped file
`PARTNERS-SAU-UN-COMTRADE-2026-09-13-b77e879286ae.json` (170127 bytes) was
deleted exactly as authorized. No network or credential environment was used.

RED command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q tests/test_acquisition_snapshots.py::test_same_day_collision_uses_deterministic_scope_and_reconstructs
```

The revised oracle builds the scoped record from a one-unit
`selected_override`, reconstructs both siblings, and rejects wrong scope12,
overlap, missing sibling and `supersedes`.

<!-- S15A_APPEND_CURSOR_027 -->

OD-14 RED failed because sibling-aware validation was absent. GREEN:
`1 passed in 0.15s`. The write path now refuses any overlap before assigning
a scope, and scoped validation resolves the one-way unscoped sibling under
the provided data root and checks identity, date, nomenclature, source and
unit disjointness.

Corrected offline build command recorded before execution:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 - <<'PY'
import json
from ior_mvp.acquisition.connectors.base import default_registry
from ior_mvp.acquisition.contracts import Stage
from ior_mvp.acquisition.coverage import select_latest_units
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.snapshots import build_row_snapshot, write_snapshot
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
config = acquisition_sources_config()
raw = config["raw_store"]
store = RawStore(PROJECT_ROOT / "data" / "raw", max_artifact_bytes=raw["max_artifact_bytes_compressed"], max_store_bytes=raw["max_store_bytes_compressed"])
latest = select_latest_units(store, source_id="un_comtrade", stage=Stage.PARTNERS)
candidates = json.loads((PROJECT_ROOT / "data/cases/selection/comtrade-partners-s15-v1.json").read_text())
keys = [(hs6, "imports", "2024") for hs6 in candidates["hs6_codes"]]
record = build_row_snapshot(store, config, default_registry(), kind="partners", source_id="un_comtrade", selected_override={key: latest[key] for key in keys})
path = write_snapshot(record, PROJECT_ROOT / "data")
print(path)
PY
```

<!-- S15A_APPEND_CURSOR_028 -->

Corrected snapshot:
`PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196`.
It has exactly four COMPLETE units, no exclusions, no 721061 rows, and is
disjoint from the unchanged unscoped sibling. All four briefs now reference
the corrected id. Exact scope/reconstruction and brief suite:
`10 passed in 8.50s`.

Final proof reruns recorded before execution: the four-case engine print
command previously recorded at `S15A_APPEND_CURSOR_024`, followed by:

```bash
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src make reconstruct-selection
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src python3 scripts/reconstruct_snapshot.py --all --no-check-manifest
UV_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/ior-s15a-pyc PATH=.venv/bin:$PATH PYTHONPATH=src pytest -q
```

<!-- S15A_APPEND_CURSOR_029 -->

OD-14 final results:

- corrected scoped id `PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196`;
- 4 COMPLETE candidate units, 0 exclusions, disjoint from sibling;
- wrong b77e file absent and no b77e reference remains under `data/`;
- S14a sibling hash unchanged at
  `e523c834e18193385f5f29c954c48b1c9e79023d401d560b5ddea78036cbe47b`;
- all four engine outputs unchanged;
- reconstruction passed with 42 acquisition artifacts;
- final pytest `6 failed, 2460 passed, 1 warning in 57.57s`, exactly the
  deferred T11/T12/post-M15 set.

OD-12 was rechecked: only the three ruled empty subclasses and registry
entries exist; no second WCO connector. Protected roots have zero tracked or
untracked diff. `git diff --check` passes.

Muhasib: `PREP_HANDOFF_PENDING_M15`, not delivery complete. The original
handoff's union-scope assumption was wrong and is superseded by this OD-14
evidence. Corrected facts come from the four-key candidate list, stored raw
units, generated scoped record and passing negative/production-pin tests.
No network, `.env`, credential, Git-state, primary-checkout, s14b, manifest
or frozen-root operation occurred. Remaining work is still independent
review, M15 integration, T11 authority/ADR/KL work, T12 manifest/CI and
delivery approval.

<!-- S15A_APPEND_CURSOR_030 -->

## 2026-09-13T07:34:00Z — T11 M15 integration stop (SC-9)

OD-15 was read and the integrated state was verified:

```text
branch slice/s15a-case-selection-evidence-pharma-fertilizers
HEAD/W1' 7d4853e8d979d86a5fa932fbd4468bceacfb63b4
wip_parent/M15 6dc966a9f210b47a94b96aaeffadcbcc6642415f
status: only .workflow/slices/S15-deep-cases-b/ untracked
PublicSnapshot schema 2.2.0 and PARTNER_DETAIL_STATES present
cases CLI includes select, validate-brief, build, reconstruct,
  reconstruct-selection
M15 frozen/case focused gate: 70 passed in 13.78s
```

The required T11 selection rerun triggered binding SC-9 before any Core,
ADR, KL, control, manifest or identity work:

```text
recorded:
  CASE-SELECTION-S15-b96de36ff0ce
  sha256 65d1fe62f7dba44a7dd52f5bc40d4566576d696cc679b5c0a97e3f31efcd3fbe
M15 rerun:
  CASE-SELECTION-S15-55869cad5a8c
  sha256 931145fd7d16bb7c333da01074e4bbbab1526e4f61700ca08150f627692eb602
```

The selected set and ordering are unchanged (294110, 294120, 310430,
310510). The byte diff is exactly:

1. document inventory 4 → 5;
2. added stored SABIC Agri-Nutrients record
   `DOC-PRODUCER-SABIC-AGRINUTRIENTS-d853eeed63fa-42fdc62825bc`
   (`aaf9df26f90416450442c573be049b5029b12ab965a659340239c063346ce28d`);
3. document-inventory hash
   `fc3842f4…` → `beea3cc9…`;
4. non-selected HS 310210 changes `disclosure_covered` false → true and gains
   that document id;
5. selection id changes accordingly.

This is the expected temporal interaction between T5 (selection deliberately
run before W-A15b) and T6 (the later SABIC record), but the approved T11
oracle requires byte identity and SC-9 forbids hand-editing or silently
accepting a new record. Execution stopped. No inputs were adjusted. No
network, `.env`, authority edits, manifest generation, Git-state change,
primary checkout or other worktree write occurred.

Owner decision required: either authorize an exact recorded-input replay
mechanism that keeps T5's four-document inventory, or authorize the new
post-acquisition selection identity and its consequential governed-reference
updates. T12/T13 were not started.

<!-- S15A_APPEND_CURSOR_031 -->

## 2026-09-13T07:55:00Z — T11 resumed under OD-16

OD-16 was read before resuming. The diagnostic
`CASE-SELECTION-S15-55869cad5a8c` remains only under `/tmp`; it was not
written, promoted or substituted. The approved recorded-input oracle passed:

```text
CASE SELECTION RECONSTRUCTION PASS (2 records)
retained S15: CASE-SELECTION-S15-b96de36ff0ce
```

Merged PublicSnapshot 2.2.0 support was verified without changing its pinned
modules. All four briefs validated and rebuilt under
`/tmp/ior-s15a-build-m15/`. Integrated engine proof:

```text
294110 2.2.0 PARTNER_DETAIL_OBSERVED 10 INVESTIGATE null
294120 2.2.0 PARTNER_DETAIL_OBSERVED  4 INVESTIGATE null
310430 2.2.0 PARTNER_DETAIL_OBSERVED 11 INVESTIGATE null
310510 2.2.0 PARTNER_DETAIL_OBSERVED 11 INVESTIGATE null
reason each: ROUTE_CHANGING_EVIDENCE_UNRESOLVED
fired each: R0,R1-D,R2,R3,R4-D,R10,R12
all capability dimensions: U
all profile hard gates: UNAVAILABLE
```

Here `U` means not identified within the cited stored evidence, not absent.
No Class-D input enters the public proof. The no-tender result is recorded only
as `NO_PUBLIC_TENDER_FOUND` within the recorded public search boundary.

Pre-manifest all-reconstruction run exited 0:

```text
CASE RECONSTRUCTION PASS (5 snapshots, 9 briefs)
RECONSTRUCTION PASS (5 snapshots, 42 artifacts)
DOCUMENT RECONSTRUCTION PASS (26 records, 26 artifacts)
ENTITY RECONSTRUCTION PASS (3 artifacts, 46 links)
SCREENING RECONSTRUCTION PASS (1 snapshots)
CASE SELECTION RECONSTRUCTION PASS (2 records)
```

T11 RED `test_s15a_core_v2_contracts` failed on missing governed text, then
passed after Core 02/04/05/09 updates. ADR-023 records OD-16 sensitivity and
the exact integration delta. KL-109–117, the S15 split, runbook,
traceability, progress and machine state were updated before any manifest
generation. Manifest run count remains zero at this point.

<!-- S15A_APPEND_CURSOR_032 -->

## 2026-09-13T07:43:54Z — T12 manifest receipt recorded before invocation

Pre-generation regression is complete. Full pytest produced the single
expected missing-manifest-row RED:

```text
1 failed, 2599 passed, 1 warning in 63.34s
failure: test_manifest_lists_gz_payload_paths
```

Other pre-generation evidence includes BRANCH_OK, focused authority/API 17
passed, focused frozen/case 70 passed, SMOKE PASS, SCENARIO VALIDATION PASS
(7 scenarios), threshold/prohibited scans PASS, VISUAL_MANIFEST_OK 76,
RUNTIME_IMPORT_BOUNDARY_OK, FROZEN_OUTCOMES_OK, protected M15 paths unchanged,
and all reconstruction stages passing without manifest checking.

Authorized invocation count before execution: zero. Receipt:

```text
UTC 2026-09-13T07:43:54Z
reason: ADR-023 S15a evidence/config/Core authority change after OD-16
pre snapshot manifest: 638 rows
pre snapshot manifest sha256:
  b97ca2085314405427ffa33edd719b23fae9707f8c80b90308c9f516c3b6d092
pre authority hashes: 19 rows
pre authority hashes sha256:
  07942d5e708053425debdbe160fbaa157d050b70e7f4e48ac4819a58686ee333
permitted authority changes:
  config/acquisition_sources.v1.yaml
  config/product_families.v1.yaml
  docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md
  docs/core/04_CANONICAL_DATA_MODEL.md
  docs/core/05_DATA_SOURCES_AND_INGESTION.md
  docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md
```

Exactly one S15a `scripts/build_manifests.py` execution follows. No second
invocation is authorized.

<!-- S15A_APPEND_CURSOR_033 -->

The single authorized generator invocation exited 0. Immediate oracle:

```text
INTEGRITY PASS
snapshot manifest: 638 -> 698 rows
added rows: 60
changed pre-existing rows: 0
removed rows: 0
authority hashes: 19 -> 19 rows
changed rows: exactly config/acquisition_sources.v1.yaml,
  config/product_families.v1.yaml and Core 02/04/05/09
snapshot manifest sha256:
  9842fa8a75698fb18c662b36beaf10fb3128dad7b1a31649e858a82b21c6abc7
authority hashes sha256:
  5160a840aba54e383122dbd552cc5e4406606cbfad148d9ba1efe5bd6ba0ce47
```

The generated Manifest §11 table mirrors the 19-row machine file; focused
manifest/authority tests passed (`29 passed`). S15a manifest invocation count
is now exactly one and exhausted. No second run is authorized.

<!-- S15A_APPEND_CURSOR_034 -->

## T12 post-generation and T13 hand-off evidence

Post-generation:

```text
pytest: 2600 passed, 1 warning in 64.66s
all reconstruction stages PASS
PORTABILITY_PASS from /tmp/ior-s15a-portability
local make ci: exit 0
  pytest 2600 passed, 1 warning
  smoke PASS
  browser functional 339 passed, 4 deselected
  browser visual 4 passed, 339 deselected
```

The plan's raw `/home/` scan also matches the pre-existing public URL
`https://saber.sa/home/aboutsaber`; the precise filesystem-path scan
`(^|["' :=])/home/` returned zero. No committed local absolute path exists.

Scratch proof used a committed copy of the exact 20-file uncommitted delta.
Two environment-only attempts are retained honestly:

1. the first scratch selected Python 3.14 and stopped after 2600 passing tests
   and smoke because the offline cache lacked Pillow's CPython 3.14 wheel;
2. the first Python 3.12 browser execution reached 331/339 tests, then an
   unrelated concurrent workload exhausted `/tmp` inodes and Chromium emitted
   `ERR_INSUFFICIENT_RESOURCES`, cascading into closed contexts.

No product input or expectation changed. The candidate was recopied unchanged
to `/home/barami/.cache/ior-s15a-ci-scratch`, committed there as temporary
scratch head `dde43a99638a9fc13c075752ca4335847f12920e`, verified on the locked
Python 3.12 environment with temp/cache paths on the home filesystem, and:

```text
CI=1 make ci: exit 0
pytest 2600 passed, 1 warning
SMOKE PASS
browser functional 339 passed, 4 deselected
browser visual 4 passed, 339 deselected
SCRATCH_EXACT_CANDIDATE_PASS 20 files
```

Plan-defined IAC-6 serialization:

```text
base: 7d4853e8d979d86a5fa932fbd4468bceacfb63b4
wip_parent: 6dc966a9f210b47a94b96aaeffadcbcc6642415f
wip_commits:
  - 7d4853e8d979d86a5fa932fbd4468bceacfb63b4
CANDIDATE_FILE_COUNT 20
CANDIDATE_IDENTITY 9e2853cfc7a6ae4208c24ab12daf90dfd24a8ccabbb0e5f3ebf87c9df3dbca31
INDEX_EMPTY_PASS
PROTECTED_SET_BYTE_IDENTICAL_PASS
STATE_JSON_VALID_PASS
AUTONOMOUS_WORKFLOW_TRACKED_UNCHANGED_PASS
```

The active worktree remains uncommitted and unstaged at W1'. This is an
implementation candidate only; independent reviewer approval is not claimed.

<!-- S15A_APPEND_CURSOR_035 -->
