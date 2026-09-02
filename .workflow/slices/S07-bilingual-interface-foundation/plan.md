# S07 Bilingual Interface Foundation — Implementation Plan

> **For the governed Implementer:** execute this plan only after the Supervisor records `PLAN_APPROVED`. Use RED→GREEN TDD in the stated order, keep the candidate uncommitted, and stop for Supervisor and independent review. Do not stage, commit, push, open or merge a PR, tag, approve your own work, weaken an existing test, or run the manifest generator more than the single authorized run in Task 11.

**Goal:** Deliver complete Arabic/English interface-chrome parity, correct RTL/LTR behavior, policy-sourced bilingual synthetic warnings, a token-only and ES-module frontend, deterministic local fonts, and governed visual-regression baselines without changing decision semantics or either public golden outcome.

**Architecture:** Serve one validated, governed YAML catalogue through an additive FastAPI locale-resource endpoint; keep policy safety labels exclusively in `evidence_policy.v1.yaml`; render engine-authored English analytical values as marked LTR source-language islands. Split the browser code and CSS by responsibility, make one CSS token layer the only raw visual-literal zone, and compare 40 canonical lossless WebP viewport images with a pinned Pillow implementation under the S06 fail-closed browser harness.

**Tech stack:** FastAPI; Python 3.12/3.14; plain browser ES modules; CSS custom properties and logical properties; YAML; Playwright/Chromium 1.62.0; `pytest-playwright==0.9.0`; `Pillow==12.3.0`; uv; Node ES-module syntax checking; vendored Fontsource Noto webfonts.

**Data classification:** `confidential_demo`. Only frozen public evidence and explicitly labelled Class-D simulation data may appear. No `.env` content, credential, Ministry record, unrestricted dataset, or external runtime request is permitted.

**Plan status:** Planner artifact only. It is not implementation, test evidence, authority approval, independent review, delivery, or permission to regenerate hashes.

---

## 1. Objective

- [SPECIFIED] The analyst can enter either `?locale=en` or `?locale=ar`, switch locale from a visible keyboard-reachable topbar control, and see all static and dynamic interface chrome in the selected locale with the choice persisted as the sole `localStorage` value (`ior.locale`). Source: approved S07 scope and `SLICE_GRAPH.md:49-57`.
- [SPECIFIED] Arabic sets `<html lang="ar" dir="rtl">`; English sets `<html lang="en" dir="ltr">`; layout mirroring is achieved with logical CSS properties and browser-observed evidence, not inferred from markup. Source: SG-TR-008, Core 01 NFR-006/NFR-007, and slice `context.md:5-16`.
- [SPECIFIED] Every synthetic marker visibly carries both exact policy labels—English and Arabic—from `config/evidence_policy.v1.yaml` 1.2.0. Neither label may be duplicated in the UI catalogue, JavaScript, Python renderer, HTML, or test constants. Source: approved scope items 3 and 12; Core 06 §8–§9.
- [SPECIFIED] Engine-emitted analytical prose remains English in S07. Arabic UI presents it honestly as `lang="en" dir="ltr"` source-language islands with a visible, catalogue-governed explanation; it is never machine-translated. Source: binding interpretation in `context.md:10-13`.
- [SPECIFIED] Raw colour, spacing, radius, shadow, typography, motion, border-width, breakpoint, and z-index values occur only in the token layer. Every browser module uses named exports and contains at most 199 physical lines. Source: SG-TR-008 and approved scope items 1–2.
- [SPECIFIED] S07 establishes the first executable visual oracle after the redesign: 10 principal screens × 2 baseline viewports (1440×900 and 1024×768) × 2 locales = 40 lossless WebP baselines, each hashed and reviewer-governed. Presentation widths 1920×1080 and 2560×1440 remain covered by functional overflow/actionability/keyboard nodes only. The S06 40-WebP documentary set remains byte-identical and is never read as an oracle. Source: ADR-010 R-4, `SLICE_GRAPH.md:49-57`, and Supervisor ruling PR-01.
- [SPECIFIED] KL-21 closes through token/module enforcement. KL-31 closes by removing the demo topbar link to CDN-backed `/docs`; FastAPI `/docs` remains an engineer-only route and is not part of the offline Ministry surface.
- [SPECIFIED] Decision rules, GenUI registry types, thresholds, sector profiles, data snapshots, scenario bytes, methodology DOCX, golden expectations, and application version remain unchanged.

## 2. Governing requirements and IDs

| ID / authority | S07 obligation | Sanad |
|---|---|---|
| V3-A3 | Preserve actionability and no horizontal overflow at 1440×900, 1024×768, 1920×1080, and 2560×1440 in both directions/locales. | [SPECIFIED] `REQUIREMENTS_TRACEABILITY.md:166-173`; approved scope |
| V3-A6 / R-4 | Replace documentary-only capture behavior with governed post-redesign visual oracles while preserving the S06 reference set. | [SPECIFIED] `REQUIREMENTS_TRACEABILITY.md:173-175`; ADR-010 |
| V3-A8 | Complete Arabic/English switching for interface chrome and governed labels. | [SPECIFIED] `GAP_ANALYSIS.md:76-79` |
| V3-A10 / SG-TR-008 | Tokens only; modules/components under 200 lines; named exports; keyboard, contrast, locale parity and bidi layout verified. | [SPECIFIED] `GAP_ANALYSIS.md:78-79`; firm interface rule |
| V3-G7 | Synthetic evidence is never described as observed, official, or Ministry-provided in either language. | [SPECIFIED] `GAP_ANALYSIS.md:153-156` |
| FR-004 / INV-03 | Synthetic isolation controls and safety labels load from versioned evidence policy. | [SPECIFIED] Core 01 §6.1; `REQUIREMENTS_TRACEABILITY.md:27-29,87-91` |
| FR-014 | Public and synthetic rows remain visibly distinct. | [SPECIFIED] Core 01 §6.2 |
| FR-060–063 | The approved ten-type GenUI registry remains fixed; browser modules render only those types and no arbitrary executable model output. | [SPECIFIED] Core 01 §6.7; Core 03 §7 |
| FR-064 | JSON and printable HTML dossiers remain available; S07 localizes HTML chrome only. | [SPECIFIED] Core 01 §6.7; S19 owns full bilingual dossier content |
| NFR-004 | Demo runtime remains offline and keyless; fonts, catalogue, scripts and UI assets are local. | [SPECIFIED] Core 01 §7; UX spec §11 |
| NFR-006 | Semantic controls, visible focus, contrast and keyboard access pass in both locales. | [SPECIFIED] Core 01 §7; UX spec §10 |
| NFR-007 v2 | Interface chrome and governed-label parity, direction switching, bidi isolation and honest source-language treatment become the Core v2 contract. | [SPECIFIED] ADR-010 Core-v2 authorization; approved S07 scope |
| Core 06 §4/§8/§9 | Synthetic metadata remains Class D, generator-sourced and visibly disclosed; no “Ministry data” implication. | [SPECIFIED] `06_SYNTHETIC_MINISTRY_DATA_SPEC.md:75-88,203-222` |
| Core 08 §5 | Normalize Arabic/Western numerals internally while preserving original source spans. | [SPECIFIED] `08_AI_EXTRACTION_AND_EVIDENCE_SPEC.md:64-75` |
| Core 09 §2.7/Gate G v2 | Static contracts plus real Playwright locale/layout/accessibility and governed visual comparisons. | [SPECIFIED] `09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md:124-135,219-226` |
| Core 02 §9 | Map every new domain-visible locale resource and bilingual policy-label function before implementation review closes. | [SPECIFIED] `02_METHODOLOGY_IMPLEMENTATION_MAP.md:195-199` |
| Manifest §7.3 | Policy 1.2.0 and the new catalogue are operating-configuration changes with rationale, approval, regression and updated hashes. | [SPECIFIED] `00_AUTHORITY_MANIFEST.md:104-114` |
| Manifest §7.4 / ADR-010 | Core 01/02/09 receive the opening per-document v2 markers and minimal contract text; methodology DOCX is unchanged. | [SPECIFIED] `00_AUTHORITY_MANIFEST.md:114-118`; ADR-010 |
| Manifest §8/§11 | One controlled manifest generation follows regression; machine JSON and the human hash table agree exactly. | [SPECIFIED] `00_AUTHORITY_MANIFEST.md:123-131,147-165` |
| KL-21 / KL-31 | Close the monolith/literal debt and remove the offline demo’s discoverable CDN-doc path. | [SPECIFIED] `KNOWN_LIMITATIONS.md:5-9,31-37` |

## 3. Existing-state assessment with file:line evidence

### 3.1 Repository and role boundary

- [VERIFIED] Read-only Git inspection found branch `slice/S07-bilingual-interface-foundation` at exact base/HEAD `6d00e27ff156e1342d488495c7b48e68eeefe100`.
- [VERIFIED] Pre-existing modified paths are `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, `docs/KNOWN_LIMITATIONS.md`, and `docs/REQUIREMENTS_TRACEABILITY.md`. Pre-existing untracked paths are the two prohibited helper scripts, S06 `completion.md`/`pr_record.md`, and S07 `context.md`/`persona.md`.
- [SPECIFIED] The planner modifies only this `plan.md`. The implementer must preserve every Supervisor-owned S06 hunk and must never touch `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, the two `.workflow/runs/*.sh` helpers, or the S06 records. S07 additions to KNOWN_LIMITATIONS/REQUIREMENTS_TRACEABILITY must be additive and must not rewrite the pending S06 changes.
- [VERIFIED] `.env` exists, is ignored, and is untracked. Its contents were not opened or printed.
- [VERIFIED] The DOCX SHA-256 was checked read-only as `5717cbd42acc9947ce5e450013719275acb7ed1470847b21fb2cc547c8ac4ce9`, matching `authority_hashes.json:4-9`. The binary file-reading tool cannot render DOCX; relevant authoritative sections were located through the hash-identical searchable mirror and cross-checked against the frozen Core.
- [VERIFIED] No `docs/project/` overlay exists; project-local authority is the manifest/core/control/milestone corpus named here.

### 3.2 Current interface

- [VERIFIED] `index.html:2` fixes `lang="en"` and has no page direction; `index.html:12-159` hard-codes all visible chrome in English; `index.html:48` exposes `/docs`; `index.html:165` loads classic deferred `/static/app.js`.
- [VERIFIED] `app.js:1-464` is one module. It mixes state, network, formatting, portfolio, all ten approved renderers, events and boot logic; English UI copy occurs throughout, including KPIs at `:68-72`, renderer labels at `:162-369`, and toast/error copy at `:386,453-456`.
- [VERIFIED] `styles.css:1-30` contains a partial `:root` palette, but `:31-353` contains raw hex/RGB(A), spacing, font, radius, shadow, motion and directional physical properties. Examples include physical sidebar placement at `:59-67`, `margin-left` at `:96,158,328,335`, and left-aligned tables at `:232-235`.
- [VERIFIED] `styles.css:50` requests non-vendored Inter; `:175` requests system Segoe UI/Tahoma for Arabic. Current `fc-match :lang=ar` resolves DejaVu Sans, and S06 hosted evidence also selected DejaVu rather than Noto.
- [VERIFIED] `app.js:257` reduces a policy label to hard-coded `SYNTHETIC`; `:340` emits another hard-coded boundary chip. Therefore not every synthetic marker currently comes from policy.
- [VERIFIED] `dossier.py:129-163` emits `<html lang="en">`, English headings and inline raw CSS; one product-name paragraph alone has `dir="rtl"` at `:152`.
- [VERIFIED] `dossier.py:83-86,100-113` and `genui.py:19-29` carry only the English scenario label. `evidence.py:98-103` validates only `display_label`; `rules.py:50-58` projects only that label.
- [VERIFIED] `config/evidence_policy.v1.yaml:1-35` is 1.1.0 and has only `synthetic_isolation.display_label`.
- [VERIFIED] `config.py:62-80` has cached loaders for project/threshold/sector/evidence policy but no UI catalogue. `app.py:56-141` has no locale resource and dossier HTML accepts only `mode`.

### 3.3 Current proof/toolchain

- [VERIFIED] S06 delivered 17 named browser tests / 62 nodes and observed 62/62 locally and in hosted CI; see `completion.md:5-25`. The current suite uses function-isolated contexts, reduced motion, fail-closed console/page/network collectors, axe and four fixed viewports.
- [VERIFIED] `browser_tests/conftest.py:160-168` hard-codes context locale `en-US`; browser helpers and assertions use English labels. `browser_tests/test_accessibility.py:41-112` locks an English 15-control order containing `/docs`.
- [VERIFIED] `test_reference_screenshots.py:23-146` creates non-oracle WebPs. The tracked S06 WebPs are under the S06 workflow record; ordinary runs target ignored `.artifacts/e2e/reference`.
- [VERIFIED] `tests/test_static_frontend.py:8-293` assumes hard-coded English strings and literal hex contrast pairs. `tests/test_dossier_contract.py:84-121` extracts a raw dossier hex token. These contracts must be rewritten to resolve token names/catalogue values rather than weakened.
- [VERIFIED] `Makefile:50-62`, both Python CI jobs (`ci.yml:45-59,77-92`), `final_acceptance.sh:198`, and deployment/development docs syntax-check only classic `app.js`.
- [VERIFIED] The installed browser tools are Playwright 1.62.0 and pytest-playwright 0.9.0 on Python 3.12.13; Pillow is not installed. Node is v22.22.3. Local OS is Ubuntu 26.04/WSL2 x86_64; hosted browser CI is Ubuntu 24.04.
- [VERIFIED] `build_manifests.py:41-47` names exactly three config artifacts and then all Core Markdown. The new governed catalogue needs an explicit path.

## 4. Relevant existing code and reuse points

| Existing code | Planned reuse | Sanad |
|---|---|---|
| `config._load_yaml`, cached config pattern | Add a cached, validated catalogue loader without creating another configuration mechanism. | [DERIVED] `config.py:23-80` |
| `evidence._synthetic_policy` and typed `EvidenceIntegrityError` | Validate both policy label fields and expose one policy-sourced label map to all projections. | [DERIVED] `evidence.py:31-103` |
| `genui.build_ui_manifest` | Preserve the ten component types; add the Arabic label beside the existing label in props only. | [SPECIFIED] FR-060–063 |
| `dossier.build_dossier` | Preserve JSON fields additively; enrich disclosure/rule rows with policy labels and localize only HTML chrome. | [DERIVED] `dossier.py:7-69` |
| `app.py` query/exception style | Add one GET locale resource and one additive HTML-dossier locale query; no write endpoint. | [DERIVED] `app.py:76-127` |
| S06 `BrowserFailureCollector` | Keep all five channels and absence of exclusions unchanged. | [SPECIFIED] V3-A5 |
| S06 case/mode/viewport constants | Add locale as an orthogonal dimension; retain case, mode and viewport expectations exactly. | [DERIVED] `harness.py:43-108` |
| S06 `verify_arabic_rendering` | Strengthen it to prove the unique vendored product font, document direction and source-island direction. | [DERIVED] `harness.py:642-757` |
| Existing static/API/dossier/isolation suites | Convert source-shape assertions into catalogue/token/module contracts while preserving behavioral assertions. | [SPECIFIED] anti-weakening rule |

- [PROPOSED] No new GenUI component type or decision-semantic field is introduced. Additive `display_label_ar` disclosure metadata is projected beside the existing English label; locale selection remains application chrome, not manifest composition.
- [PROPOSED] No bundler, npm runtime, package.json, client framework, runtime YAML parser, database or service worker is introduced.

## 5. Architecture

### 5.1 ES-module graph

[PROPOSED] Keep `/static/app.js` as a small module entry and create the following named-export graph. Every listed `.js` file is limited to 199 physical lines, contains at least one named `export`, contains no `export default`, and has one responsibility:

```text
static/app.js                         init() and guarded boot
static/modules/state.js               state object, request epoch
static/modules/api.js                 getJSON(), endpoint builders
static/modules/i18n.js                locale resolution/application, t(), placeholders
static/modules/formatters.js          latn number/date/currency/unit formatting
static/modules/dom.js                 escaping, bidi/source islands, chips, toast
static/modules/portfolio.js           load/render KPIs, cards, selector
static/modules/workspace.js           load analysis/manifest, dispatch, actions
static/modules/methodology.js         methodology summary rendering
static/modules/extraction.js          extraction-demo rendering
static/modules/events.js              delegated events, locale/mode/case/nav actions
static/modules/renderers/index.js      immutable ten-type renderer registry
static/modules/renderers/integrity.js integrity banner
static/modules/renderers/decision.js  decision hero and metric grid
static/modules/renderers/trade.js     SVG trade chart
static/modules/renderers/rules.js     rule ledger and fire/execution labels
static/modules/renderers/capability.js capability matrix
static/modules/renderers/economics.js economics/national-value/EVSI panel
static/modules/renderers/evidence.js  evidence ledger, unlocks, dossier/JSON actions
```

- [PROPOSED] `state.js` exports one mutable state object with `mode`, `locale`, `ui`, `opportunities`, `selectedId`, `analysis`, `manifest`, and `requestEpoch`. Locale changes increment `requestEpoch`; stale asynchronous responses do not render.
- [PROPOSED] Event delegation replaces per-render listener rebinding. `events.js` handles stable `data-*` actions; renderers only return escaped markup.
- [PROPOSED] `index.html` loads `<script type="module" src="/static/app.js"></script>` and contains empty `data-i18n` slots rather than visible English/Arabic prose.
- [PROPOSED] `scripts/check_es_modules.py --node node` recursively reads every production `.js` file and sends each source on stdin to `node --input-type=module --check`. It reports the real path on failure. This is the exact ES-module equivalent of the current syntax-only gate; it does not execute DOM code or resolve network imports.

### 5.2 Token layer and stylesheet decomposition

[PROPOSED] `styles.css` becomes a local import façade:

```css
@import url("./css/tokens.css") layer(tokens);
@import url("./css/base.css") layer(base);
@import url("./css/shell.css") layer(shell);
@import url("./css/overview.css") layer(overview);
@import url("./css/workspace.css") layer(workspace);
@import url("./css/content.css") layer(content);
@import url("./css/responsive.css") layer(responsive);
```

[PROPOSED] `css/tokens.css` is the only production CSS source allowed to contain raw visual literals. Its custom-property grammar is:

```text
--color-*       palette and semantic foreground/background/border/state colours
--space-*       spacing scale, including --space-0
--size-*        dimensions, percentages, chart strokes and control sizes
--layout-*      grid templates, sidebar offsets and responsive structural values
--breakpoint-*  documented breakpoint identities
--border-*      hairlines and widths
--radius-*      corner radii
--shadow-*      complete shadow values
--font-*        family, size, weight, line-height and tracking
--z-*           stacking levels
--motion-*      duration/easing/transform distances
--gradient-*    complete gradients
```

[PROPOSED] Responsive raw breakpoint literals live inside `@layer tokens`; those media blocks change custom properties. Component styles consume the properties, allowing physical breakpoint numbers to remain in the sole literal zone. Component styles use `margin-inline-*`, `padding-inline-*`, `inset-inline-*`, `border-inline-*`, `text-align:start/end`, and direction-neutral transforms. `left/right` declarations outside the token layer are rejected.

[PROPOSED] `scripts/check_ui_contracts.py` implements a brace-aware token-layer extractor and fails with path/line/category on:

1. any `#rgb`, `#rrggbb`, `rgb[a]()`, `hsl[a]()` or named colour other than `transparent`/`currentColor` outside `tokens.css`;
2. any nonzero literal with `px`, `rem`, `em`, `%`, `vh`, `vw`, `vmin`, `vmax`, `ch`, `pt`, `ms` or `s` outside `tokens.css`;
3. any raw `font-family`, `font-size`, `font-weight`, `line-height`, `letter-spacing`, `border-radius`, `box-shadow`, `z-index`, spacing or physical-direction value that does not resolve through a `var(--token-name)` reference;
4. any `1px` exception—hairline borders must use `var(--border-hairline)`;
5. any physical `left`/`right` property or `text-align:left/right`;
6. any production `style=` attribute except the single bounded runtime binding `--capability-fill:<0..100>%`;
7. any custom-property declaration outside `tokens.css`, except that bounded runtime binding.

[PROPOSED] The precise allow-list outside the token layer is: unitless `0`; CSS keywords (`auto`, `none`, `normal`, `inherit`, `initial`, `unset`, `transparent`, `currentColor`); data-derived SVG numeric attributes; and the validated capability-fill custom property. Unitless nonzero structural values must also be token references. This is intentionally stricter than allowing `1px`.

- [PROPOSED] `tokens.css` may contain only `@font-face`, the `@layer tokens` block, `:root`/`:root[dir]` token declarations, and responsive media blocks whose descendants declare custom properties. A class/id/component selector in this file is a scanner finding, preventing ordinary CSS from hiding in the exempt zone.
- [PROPOSED] Hard-coded-copy scanning uses `html.parser` for visible HTML text nodes; scans renderer template raw text nodes after removing tags/attributes; requires `.textContent`, accessible-name setters and `toast()` to receive `t(...)`; requires dossier labels to use `ui_text(...)`; and rejects any catalogue scalar duplicated in production source. Exact exemptions are technical constants (selectors, paths, locale/state codes, HTML tag/attribute names, punctuation) and developer error codes prefixed `UI_`; exemptions cannot contain a visible sentence.

### 5.3 Governed catalogue and offline loading

- [PROPOSED] Create `config/ui_strings.v1.yaml`, metadata version `1.0.0`, and hash it as rank-3 operating configuration.
- [PROPOSED] Serve it through `GET /api/ui-strings/{locale}` rather than exposing YAML or generating static JSON. This reuses safe YAML loading, validates the whole catalogue once, keeps policy labels separate, works offline, and avoids a build artifact that could drift.
- [PROPOSED] Catalogue keys are flat dotted identifiers. `en` and `ar` key sets and `{placeholder}` sets must match exactly; every scalar is a non-empty string; unknown or unused keys fail validation.
- [PROPOSED] Synthetic labels are forbidden catalogue keys. The endpoint appends a separate `synthetic_labels` object obtained from evidence policy.

Exact shape and representative copy:

```yaml
metadata:
  artifact: industrial-opportunity-ui-strings
  version: "1.0.0"
  effective_date: "2026-09-02"
  authority: "Core 01 NFR-006/NFR-007 and UX GenUI Demo Specification"
  status: frozen_for_demo_cycle
  default_locale: en
locales:
  en:
    bcp47: en-US
    direction: ltr
  ar:
    bcp47: ar-SA
    direction: rtl
strings:
  en:
    app.document_title: "Industrial Opportunity Resolution Engine"
    nav.primary_label: "Primary navigation"
    nav.overview: "Executive overview"
    nav.workspace: "Decision workspace"
    mode.group_label: "Evidence mode"
    mode.public: "Public evidence"
    mode.simulated: "Ministry simulation"
    locale.switch: "العربية"
    locale.switch_aria: "Switch interface language to Arabic"
    source_language.caption: "Analytical text remains in its governed English source language in this release."
    dossier.product_identity: "Product identity"
    dossier.none: "None"
  ar:
    app.document_title: "محرك حسم الفرص الصناعية"
    nav.primary_label: "التنقل الرئيسي"
    nav.overview: "الملخص التنفيذي"
    nav.workspace: "مساحة عمل القرار"
    mode.group_label: "وضع الأدلة"
    mode.public: "الأدلة العامة"
    mode.simulated: "محاكاة الوزارة"
    locale.switch: "English"
    locale.switch_aria: "تبديل لغة الواجهة إلى الإنجليزية"
    source_language.caption: "يبقى النص التحليلي باللغة الإنجليزية المصدر المعتمدة في هذا الإصدار."
    dossier.product_identity: "هوية المنتج"
    dossier.none: "لا يوجد"
```

[PROPOSED] The complete key inventory must cover, without wildcard lookup: document title/description; brand; all five navigation items and ordinals’ accessible text; frozen snapshot status/date; topbar/locale/mode labels; overview copy/actions/decision-flow labels; portfolio heading/chip/KPIs/card labels/actions; workspace label/region/loading/error copy; every component heading/subheading/table header/unit/state/execution/fire/boundary/action/toast; methodology summary; extraction labels/score/pass/fail/normalized label; governance cards; footer; dossier title/meta/sections/boundary/authority/print labels; and source-language captions. Tests derive used keys from `data-i18n`, `t("…")`, and Python `ui_text("…")` calls and require exact equality with catalogue keys.

### 5.4 Locale runtime and formatting

- [PROPOSED] Locale precedence is: valid URL `locale` → valid `localStorage["ior.locale"]` → deterministic default `en`. Browser preference is not used, so captures and demos do not vary by machine.
- [PROPOSED] Invalid URL/localStorage values normalize to `en`; `history.replaceState` writes the canonical query while retaining unrelated query keys and the hash.
- [PROPOSED] A switch first fetches/validates the target bundle, then atomically updates state, `<html lang/dir>`, URL and localStorage, applies static strings, and rerenders cached dynamic content. A failed fetch leaves the prior locale and rendered UI intact and emits a fatal console error.
- [PROPOSED] `popstate` reapplies the URL locale. Case and evidence-mode state remain selected. Only `ior.locale` is persisted.
- [PROPOSED] Western (`latn`) digits are used in both locales for side-by-side technical comparability: `en-US-u-nu-latn` and `ar-SA-u-ca-gregory-nu-latn`. Gregorian dates use UTC components. Currency/unit labels come from the catalogue. Arabic/Western digits in original source spans are preserved verbatim, satisfying Core 08 §5 rather than rewriting evidence.
- [PROPOSED] IDs, HS codes, hashes, standards, currencies, quantities and dates use `<bdi dir="ltr">` plus `unicode-bidi:isolate`; original Arabic spans use `lang="ar" dir="rtl"`.

### 5.5 Source-language islands

[SPECIFIED] In Arabic UI, each group has one visible `source_language.caption`; every value below is escaped and wrapped with `class="source-language-island" lang="en" dir="ltr"`:

| Field family | Arabic-UI presentation |
|---|---|
| Rules | `name`, `result`, `decision_effect` are individual table-cell islands; enum execution/fired labels are Arabic catalogue strings. |
| Decision | `headline`, `rationale`, `route_label`, conditions and kill conditions are islands under one visible caption; state enum is localized with the raw code isolated. |
| Missing facts | `missing_facts` / `data_unlocks` items are numbered islands. |
| Evidence | evidence `title`, `source`, and any displayed support text are islands; class/status/boundary chrome is localized. |
| Capability | profile label, dimension names and `control_message` are islands; K/U/D* and state codes are isolated technical values. |
| Economics/EVSI | `reason`, `finding`, `next_fact`, national-value labels emitted by the engine, and other narrative values are islands; numeric values use locale formatters. |
| Synthetic blocks | input-key-derived titles and `seed_basis` are islands; both policy labels remain visible outside the island. |
| Extraction | field names and normalized-record keys/JSON are source-language islands; Arabic and English source spans keep their own `lang`/`dir`. |
| Dossier | decision headline/route, demand and supply conclusions, conditions, kill conditions, evidence actions, simulated rule prose, seed basis and application boundary are islands; dossier section chrome is localized. |

- [DERIVED] Opportunity `commercial_name_ar` is used as the primary Arabic title when present; `commercial_name_en` remains a secondary marked island. Technical source names, standard identifiers and authority filenames remain LTR isolates, not translated.
- [SPECIFIED] Full bilingual engine narratives, computed decision copy and full dossier content remain S08–S10/S19 work.

### 5.6 Fonts

[PROPOSED] Vendor only weight-axis, normal-style WOFF2 subsets needed by this UI, each with its own OFL and `SOURCE.json`:

| Asset | Exact source/version | Bytes | SHA-256 | Licence |
|---|---|---:|---|---|
| `noto-sans-latin-wght-normal.woff2` | `@fontsource-variable/noto-sans@5.3.0`, font metadata v42 | 35,820 | `51ca196f49a33e79e7870ff88ebd2829a3f627a51e7d690986618f0e7ad2b52d` | OFL-1.1, 4,518-byte upstream `LICENSE`, SHA `54ec7b5a35310ad66f9f3091426f7028484cbf9ae1ab5da30122ee412a3009e1` |
| `noto-sans-arabic-arabic-wght-normal.woff2` | `@fontsource-variable/noto-sans-arabic@5.2.10`, font metadata v33 | 165,960 | `ce85091f020920b65762b387b194ef59457ea5b25b760f2dcc35240a94bb8669` | OFL-1.1, 4,380-byte upstream `LICENSE`, SHA `91053c23e8a0fe5fc9b5fdbe5ff74ceffd66f6f996c123f1a6ca4c23487c1fff` |

- [VERIFIED] The sizes/hashes above were measured read-only from the exact versioned jsDelivr package assets; registry metadata identifies both as OFL-1.1 and zero-dependency Fontsource packages.
- [VERIFIED] Exact acquisition URLs are `https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans@5.3.0/files/noto-sans-latin-wght-normal.woff2`, `https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans@5.3.0/LICENSE`, `https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans-arabic@5.2.10/files/noto-sans-arabic-arabic-wght-normal.woff2`, and `https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans-arabic@5.2.10/LICENSE`.
- [PROPOSED] Runtime files are `/static/assets/fonts/noto-sans/noto-sans-latin-wght-normal.woff2` and `/static/assets/fonts/noto-sans-arabic/noto-sans-arabic-arabic-wght-normal.woff2`; no runtime URL references a remote host.
- [PROPOSED] `@font-face` names are unique (`IOR Noto Sans`, `IOR Noto Sans Arabic`), range 100–900, `font-display:block`, and explicit Unicode ranges. English uses Latin first; Arabic/interface and `[lang="ar"]` use Arabic first.
- [SPECIFIED] Each font `SOURCE.json` records verbatim the exact `unicode-range` declaration from its version-pinned Fontsource CSS. The Latin asset records `U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD`; the Arabic asset records `U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0897-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC,U+102E0-102FB,U+10E60-10E7E,U+10EC2-10EC4,U+10EFC-10EFF,U+1EE00-1EE03,U+1EE05-1EE1F,U+1EE21-1EE22,U+1EE24,U+1EE27,U+1EE29-1EE32,U+1EE34-1EE37,U+1EE39,U+1EE3B,U+1EE42,U+1EE47,U+1EE49,U+1EE4B,U+1EE4D-1EE4F,U+1EE51-1EE52,U+1EE54,U+1EE57,U+1EE59,U+1EE5B,U+1EE5D,U+1EE5F,U+1EE61-1EE62,U+1EE64,U+1EE67-1EE6A,U+1EE6C-1EE72,U+1EE74-1EE77,U+1EE79-1EE7C,U+1EE7E,U+1EE80-1EE89,U+1EE8B-1EE9B,U+1EEA1-1EEA3,U+1EEA5-1EEA9,U+1EEAB-1EEBB,U+1EEF0-1EEF1`. Catalogue values and renderer/dossier template literals may contain only ASCII, characters covered by those vendored ranges, and Arabic blocks; the scanner has no additional allow-list. Source: Supervisor ruling PR-02 and version-pinned Fontsource CSS.
- [SPECIFIED] Chrome glyphs outside those ranges—including `→` U+2192, `✓` U+2713 and `✕` U+2715—are never emitted as text. Render them as deterministic inline SVG or CSS-drawn elements with catalogue-driven accessible names. `—` and `·`, which are covered by General Punctuation, may remain text. Source: Supervisor ruling PR-02.
- [PROPOSED] Browser preflight verifies exact local bytes, source metadata and licences. Browser assertions wait for `document.fonts.ready`, require `document.fonts.check()` for the Arabic sample, require computed family to begin with the expected IOR family, and run the existing Arabic-vs-U+FFFD glyph-signature test. System `fc-match` may be recorded diagnostically but no longer satisfies the product-font gate.

Exact one-time acquisition and verification commands for the Implementer:

```bash
curl --fail --location --proto '=https' --tlsv1.2 \
  --output src/ior_mvp/static/assets/fonts/noto-sans/noto-sans-latin-wght-normal.woff2 \
  'https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans@5.3.0/files/noto-sans-latin-wght-normal.woff2'
curl --fail --location --proto '=https' --tlsv1.2 \
  --output src/ior_mvp/static/assets/fonts/noto-sans/LICENSE \
  'https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans@5.3.0/LICENSE'
curl --fail --location --proto '=https' --tlsv1.2 \
  --output src/ior_mvp/static/assets/fonts/noto-sans-arabic/noto-sans-arabic-arabic-wght-normal.woff2 \
  'https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans-arabic@5.2.10/files/noto-sans-arabic-arabic-wght-normal.woff2'
curl --fail --location --proto '=https' --tlsv1.2 \
  --output src/ior_mvp/static/assets/fonts/noto-sans-arabic/LICENSE \
  'https://cdn.jsdelivr.net/npm/@fontsource-variable/noto-sans-arabic@5.2.10/LICENSE'
printf '%s  %s\n' \
  '51ca196f49a33e79e7870ff88ebd2829a3f627a51e7d690986618f0e7ad2b52d' \
  'src/ior_mvp/static/assets/fonts/noto-sans/noto-sans-latin-wght-normal.woff2' \
  '54ec7b5a35310ad66f9f3091426f7028484cbf9ae1ab5da30122ee412a3009e1' \
  'src/ior_mvp/static/assets/fonts/noto-sans/LICENSE' \
  'ce85091f020920b65762b387b194ef59457ea5b25b760f2dcc35240a94bb8669' \
  'src/ior_mvp/static/assets/fonts/noto-sans-arabic/noto-sans-arabic-arabic-wght-normal.woff2' \
  '91053c23e8a0fe5fc9b5fdbe5ff74ceffd66f6f996c123f1a6ca4c23487c1fff' \
  'src/ior_mvp/static/assets/fonts/noto-sans-arabic/LICENSE' \
  | sha256sum --check
```

### 5.7 Dossier

- [PROPOSED] Move dossier rules to `static/css/dossier.css`; `dossier.py` embeds `tokens.css` and `dossier.css` into the standalone response so printing remains one document and uses the same token source.
- [PROPOSED] HTML route becomes `/api/opportunities/{opportunity_id}/dossier.html?mode={public|simulated}&locale={en|ar}`; default is `en`. Query locale, not `Accept-Language`, is authoritative for deterministic URLs, popup tests and exports.
- [PROPOSED] `<html lang dir>` and all headings/meta/boundary/authority labels use catalogue strings. Engine fields use source-language islands. JSON dossier contract remains locale-neutral.
- [PROPOSED] Every simulated dossier displays both policy labels in the warning and each synthetic rule entry; public dossiers display neither.
- [SPECIFIED] Existing A4 print behavior, zero public synthetic rows and authority disclosure remain regression-locked.

### 5.8 KL-31 decision

- [PROPOSED] Remove the visible `/docs` anchor from the demo topbar and keep FastAPI `/docs` unchanged for engineers who deliberately navigate to it.
- [DERIVED] This closes the offline demo defect with zero Swagger asset/vendor weight, avoids shipping a second frontend and licence surface, and aligns with NFR-004/UX §11. The new one-button locale switch occupies the same keyboard position, so the current 15-control count remains 15.
- [PROPOSED] Static and browser tests assert the rendered demo contains no anchor to `/docs`; no ordinary journey activates the engineer-only route.

### 5.9 Visual baselines

- [PROPOSED] Replace the ordinary `test_capture_documentary_reference_set` browser test with `test_governed_visual_baselines_match`. Do not delete, rewrite, recapture or compare the 40 tracked S06 WebPs.
- [SPECIFIED] Store exactly 40 lossless normalized WebPs under `browser_tests/baselines/v0.3.0/<locale>/<viewport>/<screen>.webp`, plus `manifest.json` and `manifest.sha256`: ten S06 state identities (portfolio public/simulated; steel public/simulated workspace; PP public/simulated workspace; four dossier states) × `en`/`ar` × desktop 1440×900/tablet 1024×768. Source: Supervisor ruling PR-01.
- [SPECIFIED] Presentation widths 1920×1080 and 2560×1440 have no pixel baseline; functional overflow, actionability and keyboard nodes continue to cover them. Source: Supervisor ruling PR-01.
- [PROPOSED] Capture viewport screenshots with `full_page=False`, device scale 1, `animations="disabled"`, hidden caret, fixed scroll anchor, UTC, light colour scheme, reduced motion, `document.fonts.ready`, and launch flags `--font-render-hinting=none`, `--disable-lcd-text`, `--force-color-profile=srgb`.
- [SPECIFIED] Normalize decoded screenshot bytes deterministically through Pillow to opaque RGB before hashing/comparison, then encode baseline files as WebP with `lossless=True` and no metadata. Source: Supervisor ruling PR-01.
- [PROPOSED] Pillow 12.3.0 is an exact e2e-only pin. It is not a pure-Python implementation; it is selected because its maintained manylinux wheels support Python 3.12/3.14 and its decoded-pixel behavior is stable. No NumPy or perceptual-image dependency is added.

Exact comparison rule:

```text
dimensions and mode: exact
decoded output: opaque RGB, exact dimensions
significant pixel: max(|RΔ|, |GΔ|, |BΔ|) > 8
significant_pixel_ratio: <= 0.001 (0.10%)
mean_absolute_channel_error over all RGB channels: <= 0.20
```

- [PROPOSED] Both ratio and mean gates must pass. A mismatch writes normalized actual WebP, amplified lossless diff WebP, JSON metrics and baseline path under `.artifacts/e2e/visual-diffs/`, then fails.
- [DERIVED] The channel threshold of 8 discards only low-amplitude raster noise; the 0.10% ratio allows at most 786 significant pixels at 1024×768 while a shifted component affects a materially larger region; the independent mean-error gate catches broad low-amplitude colour drift. Repeat-capture calibration must record observed values but may not silently revise these predeclared limits.
- [SPECIFIED] Each WebP is at most 600 KiB and all 40 total at most 12 MiB. The manifest records path, locale, screen, case/mode, viewport/dimensions, bytes, SHA-256, source-tree hashes, font hashes, exact Playwright Chromium revision/browser version, launch flags and tolerance. `manifest.sha256` hashes the canonical JSON bytes. Source: Supervisor rulings PR-01 and PR-05.
- [DERIVED] Baselines are rank-6 test oracles, not industrial-method authority. They therefore use their own hash manifest and reviewer gate rather than entering `authority_hashes.json`; `build_manifests.py` governs the catalogue/policy/Core changes only.
- [PROPOSED] Canonical updates run in `mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d` (Ubuntu 24.04 manifest list) through `browser_tests/visual/Dockerfile`, with exact `uv==0.12.9` and the project lock. `.dockerignore` excludes `.env`, `.git`, `.venv`, agent logs and artifacts from build context.
- [SPECIFIED] `scripts/run_visual_baseline_container.py` checks Docker availability before invocation and exits 2 with a clear diagnostic when unavailable. Inside the container it asserts Playwright 1.62.0 uses the same pinned `chromium-1234` revision as the host contract before compare/update, and records the observed browser version and exact flags in `manifest.json`. Source: Supervisor ruling PR-05.
- [SPECIFIED] Normal `make e2e` local/hosted comparison is Docker-free and remains on the exact host-installed Playwright Chromium with the flags and vendored fonts; only canonical diagnosis/update targets invoke Docker. The Noble update container removes the local WSL 26.04/host-font source of truth. Source: Supervisor ruling PR-05.

## 6. Complete file plan

### 6.1 Create

| Path | Responsibility |
|---|---|
| `config/ui_strings.v1.yaml` | Governed EN/AR chrome catalogue 1.0.0. |
| `src/ior_mvp/static/modules/{state,api,i18n,formatters,dom,portfolio,workspace,methodology,extraction,events}.js` | Named-export modules in §5.1. |
| `src/ior_mvp/static/modules/renderers/{index,integrity,decision,trade,rules,capability,economics,evidence}.js` | Ten-type renderer implementation groups. |
| `src/ior_mvp/static/css/{tokens,base,shell,overview,workspace,content,responsive,dossier}.css` | Sole token layer plus token-only component/dossier styles. |
| `src/ior_mvp/static/assets/fonts/noto-sans/{noto-sans-latin-wght-normal.woff2,LICENSE,SOURCE.json}` | Exact Latin font provenance. |
| `src/ior_mvp/static/assets/fonts/noto-sans-arabic/{noto-sans-arabic-arabic-wght-normal.woff2,LICENSE,SOURCE.json}` | Exact Arabic font provenance. |
| `src/ior_mvp/static/assets/fonts/THIRD_PARTY_NOTICES.md` | Runtime font notices. |
| `scripts/check_es_modules.py` | Recursive named module syntax check via Node module mode. |
| `scripts/check_ui_contracts.py` | Token, direction, catalogue parity and hard-coded-copy scanner. |
| `scripts/run_visual_baseline_container.py` | Allow-listed, no-secret Docker mounts and canonical compare/update invocation without shell interpolation. |
| `tests/test_ui_catalogue.py` | Schema/parity/API/no-duplication/failure tests. |
| `tests/test_ui_tokens.py` | Literal scanner/token grammar/dossier/token contrast tests. |
| `tests/test_es_modules.py` | Module size/export/import/syntax tests. |
| `tests/test_font_assets.py` | Exact bytes/hash/licence/font-face/preflight tests. |
| `tests/test_visual_baseline_contract.py` | Manifest matrix/hash/budget/tolerance/update/CI-ban tests. |
| `browser_tests/visual_baselines.py` | Opaque-RGB/lossless-WebP normalization, compare, diff artifacts, manifest/update core. |
| `browser_tests/test_visual_baselines.py` | Four locale×baseline-viewport nodes, ten screens per node. |
| `browser_tests/visual/Dockerfile` | Digest-pinned Noble update environment. |
| `browser_tests/baselines/v0.3.0/<locale>/<viewport>/<screen>.webp` | Exactly 40 governed baseline images. |
| `browser_tests/baselines/v0.3.0/manifest.json` | Deterministic 40-entry hash/capture manifest. |
| `browser_tests/baselines/v0.3.0/manifest.sha256` | Hash of canonical manifest JSON. |
| `.dockerignore` | Prevent ignored secrets/workspace material entering canonical build context. |
| `.workflow/slices/S07-bilingual-interface-foundation/{implementation_log,test_evidence}.md` | Later Implementer evidence only; planner does not create them. |

### 6.2 Modify

| Path | Exact purpose |
|---|---|
| `config/evidence_policy.v1.yaml` | 1.1.0→1.2.0; add exact Arabic safety label only. |
| `scripts/build_manifests.py` | Add the catalogue explicit authority path. |
| `docs/authority/authority_hashes.json` | Single-generator output: policy/catalogue/Core 01/02/09 rows. |
| `docs/authority/00_AUTHORITY_MANIFEST.md` | Refresh only matching §11 rows/add catalogue row. |
| `docs/core/01_PRODUCT_AND_REQUIREMENTS.md` | Marker 2.0.0; minimal NFR-007 extension. |
| `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md` | Marker 2.0.0; map locale resource and policy-label projection. |
| `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md` | Marker 2.0.0; §2.7 real-browser/visual-oracle wording. |
| `src/ior_mvp/static/{index.html,app.js,styles.css}` | Empty i18n shell, module entry, CSS import façade. |
| `src/ior_mvp/{app,config,evidence,rules,decision_engine,genui,dossier}.py` | Locale resource/query, catalogue loader, dual policy labels and localized dossier chrome. |
| `scripts/check_browser_prerequisites.py` | Require exact vendored fonts and report intended product families. |
| `scripts/final_acceptance.sh` | Replace classic single-file Node check with recursive ES-module checker. |
| `Makefile` | UI/module gates, functional/visual e2e targets, guarded canonical update target. |
| `pyproject.toml`, `uv.lock` | Add Pillow exact e2e pin/visual marker; one intentional lock regeneration. |
| `.github/workflows/ci.yml` | UI and ES-module gates; remove system-font reliance; retain fail-closed browser job. |
| `tests/test_{static_frontend,api,dossier_contract,synthetic_isolation,simulation_fidelity,authority_disclosure,integrity_contract,browser_harness_contract,ci_contract,final_acceptance_contract}.py` | Update/add contracts without deleting behavioral coverage. |
| `browser_tests/{conftest,harness,pages,test_journeys,test_dossier,test_accessibility,test_responsive,test_guardrails}.py` | Locale dimension, intended-font/direction assertions, stable locators. |
| `browser_tests/THIRD_PARTY_NOTICES.md` | Pillow and canonical Playwright-image notices. |
| `docs/{DEVELOPMENT_GUIDE,OPERATOR_RUNBOOK,KNOWN_LIMITATIONS,REQUIREMENTS_TRACEABILITY,ARCHITECTURE_DECISIONS,DEPLOYMENT_GUIDE}.md` | S07 operation/governance/closure/syntax documentation. |
| `docs/implementation/UX_GENUI_DEMO_SPEC.md` | Replace §8 with implemented whole-interface locale/bidi/source-island contract. |
| `README.md`, `CHANGELOG.md` | Locale operation/tooling summary and Unreleased entry. |

### 6.3 Delete/rename

- [PROPOSED] Delete `browser_tests/test_reference_screenshots.py` only after creating `test_visual_baselines.py` with equivalent ten-state coverage plus comparison. Remove now-unused `ReferenceRecorder` code from harness/conftest.
- [SPECIFIED] This source-file replacement does not delete or modify `.workflow/slices/S06-browser-acceptance-harness/reference-screenshots/v0.2.0/**`.

### 6.4 Explicitly unchanged

- [SPECIFIED] No `data/**`, `config/thresholds.v1.yaml`, `config/sector_profiles.v1.yaml`, methodology DOCX, extraction golden, public/synthetic snapshot, decision threshold, expected golden state/value, GenUI component-type registry, project version, or application Dockerfile change.
- [SPECIFIED] No edits to `.workflow/state.json`, `docs/BUILD_PROGRESS.md`, S06 records, or `.workflow/runs/*.sh`.
- [DERIVED] `scripts/verify_integrity.py` needs no code edit because it already verifies every machine-manifest entry.

## 7. Data/config schema changes

### 7.1 Evidence policy 1.2.0

[PROPOSED] Exact hand edit; all omitted sections remain byte-for-byte unchanged:

```yaml
metadata:
  version: "1.2.0"
  effective_date: "2026-09-02"
  authority: "Industrial Opportunity Resolution Methodology, Sections 2.1, 10 and 11"

synthetic_isolation:
  invariant: "Synthetic evidence can never change the real decision state."
  required_fields:
    - synthetic_flag
    - scenario_id
    - opportunity_id
    - display_label
    - seed_basis
    - evidence_class
    - source
    - synthetic_inputs
  required_evidence_class: D
  required_source: DEMO_GENERATOR
  allowed_decision_field: simulation_decision
  forbidden_decision_field: real_decision
  display_label: "SIMULATED — NOT MINISTRY EVIDENCE"
  display_label_ar: "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"
```

- [SPECIFIED] Scenario JSON is not edited and continues to carry/validate the English `display_label`. `display_label_ar` is a required non-empty policy control projected at runtime.
- [SPECIFIED] Supervisor-approved default Arabic policy text (ruling PR-03; not yet seen by the owner, owner-amendable) is exactly `محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة`. It is governed, owner-amendable only through a later Manifest §7.3 authority change, and implementation/tests may not vary or paraphrase it. Source: Supervisor ruling PR-03 resolving OQ-01.
- [PROPOSED] `synthetic_display_labels()` returns `{"en": policy["display_label"], "ar": policy["display_label_ar"]}` only after validating both fields; evidence rows, synthetic rules, simulation decision/scenario disclosure, GenUI and dossier all consume this function’s values.

### 7.2 Catalogue validation schema

Required typed interfaces are `SUPPORTED_UI_LOCALES: tuple[str, ...] = ("en", "ar")`, `ui_strings_config() -> dict[str, Any]`, `validate_ui_strings(payload: dict[str, Any]) -> None`, `ui_strings_bundle(locale: str) -> dict[str, Any]`, and the existing `clear_config_caches() -> None` extended to clear `ui_strings_config`.

- [PROPOSED] `ui_strings_bundle` returns a defensive copy with `catalogue_version`, `locale`, `bcp47`, `direction`, `strings`, and policy-sourced `synthetic_labels`.
- [PROPOSED] Key regex is `^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$`. Locale sets, key sets, placeholders and scalar types are exact. Values are Unicode-normalized NFC and non-empty after strip.
- [PROPOSED] Any key beginning `synthetic.`, any value equal to either policy safety label, or any third locale is rejected.

### 7.3 Per-document Core v2 markers

[PROPOSED] Add immediately below each changed Core title:

```markdown
<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->
```

- [DERIVED] Core migration is per document during v0.3.0: Core files without a marker remain the frozen v1 contract until their owning slice updates them. ADR-011 records this rolling-marker rule; no unmodified Core file is touched merely to add a marker.
- [PROPOSED] Replace Core 01 NFR-007 with exactly:

```markdown
- **NFR-007 Bilingual interface and Arabic support:** All interface chrome and governed labels shall have Arabic/English content parity; the document language and direction shall switch correctly; Arabic and mixed-direction content shall render without corruption. Until governed bilingual engine narratives exist, English analytical text shall remain visibly identified and directionally isolated as source-language content.
```

- [PROPOSED] Replace Core 09 §2.7 with exactly:

```markdown
### 2.7 Frontend contract and real-browser visual tests

Static contracts shall enforce the approved component registry, token-only styling,
ES-module boundaries, catalogue parity, synthetic disclosure and offline assets.
Real Chromium tests shall exercise every supported locale, evidence mode, primary
control and approved viewport, including keyboard focus, WCAG 2.1 A/AA, bidirectional
layout, intended-font rendering, dossier print/PDF, console and network failures.
Post-redesign visual baselines are hashed test oracles: comparison is deterministic,
updates require an explicit reviewer-approved procedure, and CI shall never update them.
```

- [PROPOSED] Add these exact Core 02 §2 map entries and retain §9 unchanged:

```markdown
| 5 / 10 — Bilingual presentation boundary | Interface chrome is localized from a governed catalogue; engine analytical text remains marked source-language content until a governed narrative exists | `config.ui_strings_bundle`, `app.ui_strings`, static ES modules | catalogue/API/browser parity tests | whole-interface AR/EN switch |
| 2.1 / 10 / 11 — Synthetic disclosure language | English and Arabic warning labels are policy controls and every synthetic projection uses them without changing evidence class or real decision | `evidence.synthetic_display_labels`, `rules`, `genui`, `dossier` | isolation, dossier, API and browser disclosure tests | bilingual synthetic warning |
```

## 8. Algorithms and deterministic rules

### 8.1 Catalogue parity

1. [PROPOSED] Parse YAML mapping; reject aliases/non-mapping locale sections through normal safe-loader/type checks.
2. [PROPOSED] Require metadata/locales exactly as §7.2.
3. [PROPOSED] Compare `set(en) == set(ar)`.
4. [PROPOSED] Reject blank values and leading/trailing whitespace.
5. [PROPOSED] Extract placeholders with `\{([a-z][a-z0-9_]*)\}` and require equal sets per key.
6. [PROPOSED] Extract statically referenced keys from HTML/JS/Python and require exact equality with catalogue keys; dynamic enum families have explicit required-key sets.
7. [PROPOSED] Fail on catalogue-label duplication of policy safety text.

### 8.2 Direction/bidi rules

- [PROPOSED] Document direction controls macro layout. No component reverses arrays/data order merely because locale is Arabic.
- [PROPOSED] Flex/grid use logical order; sidebar uses `inset-inline-start`; main offset uses `margin-inline-start`; toast uses `inset-inline-end`.
- [PROPOSED] Technical and source-language islands use `unicode-bidi:isolate`; mixed interpolations use `<bdi>`.
- [PROPOSED] Tables retain column order for analytical comparability but headers/cells use `text-align:start`; scroll origin and sidebar placement mirror in RTL.
- [PROPOSED] Browser mirroring evidence records sidebar bounding edge, main offset, topbar text alignment and logical control order, not only computed `direction`.

### 8.3 Numerals/date/units

- [SPECIFIED] The Supervisor-approved (ruling PR-04), owner-amendable presentation policy is Western (`latn`) digits in both locales, Gregorian dates, and source spans displayed verbatim. ADR-011 and UX spec §8 must record that later changes require owner amendment. Source: Supervisor ruling PR-04.
- [PROPOSED] `Intl.NumberFormat` receives `{numberingSystem:"latn"}` and locale-specific separators; percentages multiply once; null is the catalogue unavailable marker.
- [PROPOSED] Gregorian dates are parsed as date-only UTC and formatted with `ar-SA-u-ca-gregory-nu-latn` or `en-GB-u-ca-gregory-nu-latn`.
- [PROPOSED] `SAR`, `USD`, `kt`, `%`, `D*`, `K`, `U`, HS and standards remain LTR technical tokens; surrounding labels localize.
- [SPECIFIED] Source-span numerals are never normalized for display; only normalized analytical values use this policy.

### 8.4 Visual comparison

- [PROPOSED] Decode reference/current, normalize RGB, reject dimensions, calculate per-channel absolute differences in Pillow, and count pixels whose maximum channel delta exceeds 8.
- [PROPOSED] Calculate ratio and mean using integer sums before the final division; serialize metrics with six decimal places.
- [PROPOSED] No blur, crop, mask, anti-alias ignore region, per-screen tolerance or auto-accept exists.
- [SPECIFIED] Update mode normalizes all captures to opaque RGB, encodes all 40 as lossless WebP, validates the exact 2-locale × 2-viewport × 10-screen matrix, per-file/total budgets, hashes and decoded properties in a temporary ignored directory, then replaces the tracked set and manifest atomically. Partial output never replaces a valid set. Source: Supervisor ruling PR-01.

## 9. API changes

### 9.1 Locale resource

```python
@app.get("/api/ui-strings/{locale}")
def ui_strings(locale: str) -> dict[str, Any]:
    try:
        return ui_strings_bundle(locale)
    except UnsupportedUILocaleError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "UI_LOCALE_NOT_FOUND", "locale": locale},
        ) from exc
    except UIStringConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail={"code": "UI_CATALOGUE_INTEGRITY_ERROR"},
        ) from exc
```

- [PROPOSED] `en` and `ar` return 200 and identical string keys. Unknown path locale returns the exact 404 object. Configuration error returns no partial/fallback catalogue and does not echo values.

### 9.2 Dossier HTML

```python
@app.get(
    "/api/opportunities/{opportunity_id}/dossier.html",
    response_class=HTMLResponse,
)
def dossier_html(
    opportunity_id: str,
    mode: Literal["public", "simulated"] = Query(default="public"),
    locale: Literal["en", "ar"] = Query(default="en"),
) -> HTMLResponse:
    dossier_value = build_dossier(_safe_analysis(opportunity_id, mode))
    return HTMLResponse(render_dossier_html(dossier_value, locale=locale))
```

- [PROPOSED] Existing URLs remain English-compatible. JSON dossier and analysis/UI-manifest routes remain locale-neutral.

## 10. UI changes

- [PROPOSED] Empty static shell with `data-i18n`/`data-i18n-attr` hooks prevents duplicated visible copy. Body remains hidden/`aria-busy=true` until catalogue, fonts and first state are ready.
- [PROPOSED] Topbar locale button shows the target language (`العربية` in English, `English` in Arabic), has a localized accessible name, and preserves case/mode/scroll context.
- [PROPOSED] Mode/state/execution/fire/status labels are localized while raw domain enum codes remain available in isolated technical text for auditability.
- [PROPOSED] Both policy warnings appear together at every active simulated banner, rule chip, evidence row, active-block disclosure, simulated-mode governance disclosure and dossier warning; primary locale is ordered first. Public mode has no active synthetic warning.
- [PROPOSED] All controls retain semantic button/select/label behavior, visible focus and text-not-colour state identification.
- [PROPOSED] No visual redesign beyond direction-safe token migration and deterministic typography; information hierarchy and component registry remain unchanged.

## 11. Integration points

- [DERIVED] `config.py` owns catalogue loading/version disclosure; `app.py` owns HTTP mapping; client `api.js` fetches only same-origin JSON.
- [DERIVED] `evidence.py` is the sole safety-label policy resolver. `rules.py`, `decision_engine.py`, `genui.py` and `dossier.py` consume projected labels rather than reloading/duplicating text.
- [DERIVED] `authority_summary.config_versions` gains `ui_strings`, so banner/dossier/API authority tests expose catalogue version 1.0.0.
- [DERIVED] `dossier.py` embeds the same token source used by the workspace; token scanner exercises a real rendered dossier in both locales.
- [DERIVED] S06 context/server/failure hooks remain the runtime harness; locale and visual comparison are orthogonal additions.
- [DERIVED] Package data already includes `static/**/*`; Docker already copies `src` and `config`, so modules/fonts/catalogue enter pip/Docker without changing the application Dockerfile.

## 12. Failure behavior

| Failure | Required result | Sanad |
|---|---|---|
| Missing/blank/mismatched catalogue key | `UIStringConfigurationError`; locale endpoint 500 code; client does not partially switch. | [PROPOSED] fail closed |
| Unknown API locale | Exact 404 `UI_LOCALE_NOT_FOUND`; no fallback payload. | [PROPOSED] resource semantics |
| Invalid URL/localStorage locale | Canonicalize to `en`; never request an arbitrary path. | [PROPOSED] safe client boundary |
| Missing/mismatched policy label | `EvidenceIntegrityError`; simulated analysis cannot complete. | [SPECIFIED] Core 06 policy gate |
| Missing/tampered font or licence | Browser preflight nonzero; no system-font acceptance. | [PROPOSED] deterministic rendering |
| Font not actually selected | RTL/font browser node fails with computed family/font-load/glyph evidence. | [PROPOSED] NFR-007 proof |
| Module >199 lines/default export/unresolved import/syntax error | UI/module scanner or Node checker exits nonzero in both Python CI jobs. | [SPECIFIED] SG-TR-008 |
| CSS literal/physical direction/illegal style | UI contract scanner exits 1 with file/line/category. | [SPECIFIED] token-only rule |
| Visual mismatch | Test fails; actual/diff/metrics retained; no baseline write in compare mode. | [SPECIFIED] governed oracle |
| Baseline update in CI/missing flag or reason | Exit 2 before capture and leave tracked baselines unchanged. | [SPECIFIED] no CI updates |
| External request/console/page/HTTP error/axe violation | Existing S06 collector/axe gate fails without exclusion. | [SPECIFIED] V3-A5 |

## 13. Unknown or missing-input behavior

- [SPECIFIED] Unknown analytical content remains English and visibly marked; no translation guess, blank substitution or invented Arabic narrative.
- [PROPOSED] Missing optional `commercial_name_ar` displays the English name as a marked source-language island and an existing unknown marker; it does not synthesize Arabic.
- [PROPOSED] Null numeric values remain the localized unavailable marker and never become zero.
- [PROPOSED] If `localStorage` is unavailable, URL/document locale still works for the session; only persistence is absent and no application data is stored elsewhere.
- [PROPOSED] If canonical local WSL comparison exceeds tolerance but the Noble canonical comparison passes, record an environment mismatch; never update images from the noncanonical host.
- [SPECIFIED] A first hosted mismatch blocks the PR. Diagnose browser/font/source hashes; do not raise tolerance or regenerate in CI.

## 14. Privacy and security

- [SPECIFIED] `.env` is never read, mounted into the canonical container, copied into Docker context, printed or staged.
- [PROPOSED] `.dockerignore` excludes `.env`, `.git`, `.venv`, `.workflow/logs`, `.artifacts`, test reports and untracked agent scratch.
- [PROPOSED] Canonical update container mounts only required project paths plus the baseline/artifact outputs; runtime uses `--network=none`. Dependency image build is the only networked setup step.
- [SPECIFIED] Runtime requests are same-origin only; fonts/catalogue/CSS/modules are local. The S06 external-origin collector remains exact.
- [PROPOSED] `localStorage` stores only `en` or `ar`; no opportunity, mode, evidence, clipboard, user or identifier data.
- [SPECIFIED] Baseline screenshots contain only `confidential_demo` surface data. Failure artifacts retain the existing private 14-day hosted policy.
- [SPECIFIED] Font acquisition uses public versioned assets with recorded hashes/licences; no script executes from either package.

## 15. Concurrency

- [DERIVED] Server/domain concurrency does not change; both new endpoints are read-only and cached like current config.
- [PROPOSED] Client request epochs prevent stale mode/case responses from overwriting a later locale switch. The locale control is disabled only during its bundle transition.
- [PROPOSED] Browser nodes remain serial—no xdist—and use one isolated context per node. Visual update uses one process and rejects duplicate paths.
- [SPECIFIED] Existing CI workflow concurrency/cancellation and BrowserFailureCollector behavior remain unchanged.

## 16. Versioning and compatibility

### 16.1 Exact dependency fragment

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8,<9",
  "httpx>=0.27,<1"
]
e2e = [
  "Pillow==12.3.0",
  "playwright==1.62.0",
  "pytest-playwright==0.9.0"
]

[tool.pytest.ini_options]
markers = [
  "e2e: real-Chromium acceptance tests; excluded from default testpaths",
  "visual: governed visual-regression matrix"
]
```

- [VERIFIED] Pillow 12.3.0 requires Python ≥3.10 and supports Python 3.12 and 3.14; licence is MIT-CMU.
- [SPECIFIED] `dev` remains byte-for-byte the same two entries; only `e2e` and lock metadata grow.
- [PROPOSED] Run `uv lock` exactly once for this dependency edit, separately from the one later manifest-generator run; review every lock change and confirm Playwright/pytest-playwright versions remain exact.
- [SPECIFIED] Evidence policy becomes 1.2.0; catalogue is 1.0.0; changed Core documents become 2.0.0; app/project remains 0.2.0.
- [PROPOSED] ES syntax checker supports the current Node 22 and CI Node available on Ubuntu. A missing `--input-type=module --check` capability exits 2 rather than silently falling back.

### 16.2 Exact Make/CI direction

```make
UI_CONTRACTS = $(UV_RUN) python scripts/check_ui_contracts.py
ES_MODULE_CHECK = $(UV_RUN) python scripts/check_es_modules.py --node "$(NODE)"
E2E_FUNCTIONAL_TESTS = $(E2E_TESTS) -m "e2e and not visual"
E2E_VISUAL_TESTS = $(E2E_TESTS) -m visual
VISUAL_BASELINE_IMAGE = ior-visual-baselines:playwright-1.62.0-noble

.PHONY: e2e-functional e2e-visual e2e-visual-canonical e2e-update-baselines visual-baseline-image

e2e-functional: uv-sync-e2e
	$(E2E_PREFLIGHT)
	$(E2E_FUNCTIONAL_TESTS)

e2e-visual: uv-sync-e2e
	$(E2E_PREFLIGHT)
	$(E2E_VISUAL_TESTS)

e2e: e2e-functional e2e-visual

visual-baseline-image:
	docker build --file browser_tests/visual/Dockerfile \
		--tag "$(VISUAL_BASELINE_IMAGE)" .

e2e-visual-canonical: visual-baseline-image
	$(UV_RUN_E2E) python scripts/run_visual_baseline_container.py \
		--image "$(VISUAL_BASELINE_IMAGE)" \
		--mode compare

e2e-update-baselines: visual-baseline-image
	@test "$(IOR_UPDATE_VISUAL_BASELINES)" = "1" || \
		(echo "IOR_UPDATE_VISUAL_BASELINES=1 is required" >&2; exit 2)
	@test -n "$(IOR_BASELINE_CHANGE_REF)" || \
		(echo "IOR_BASELINE_CHANGE_REF is required" >&2; exit 2)
	@test -z "$(CI)" || \
		(echo "CI may not update visual baselines" >&2; exit 2)
	$(UV_RUN_E2E) python scripts/run_visual_baseline_container.py \
		--image "$(VISUAL_BASELINE_IMAGE)" \
		--mode update \
		--change-ref "$(IOR_BASELINE_CHANGE_REF)"
```

[SPECIFIED] `scripts/run_visual_baseline_container.py` is mandatory only for canonical diagnosis/update targets: it checks Docker availability and exits 2 with a clear message when unavailable, builds an allow-listed no-secret mount list, invokes Docker without a shell, and asserts container Chromium revision `chromium-1234` before running. Normal `make e2e` compare never calls this script or Docker. Source: Supervisor ruling PR-05.

[PROPOSED] In `make ci`, insert UI contracts after threshold scanning, then Python compile, then ES-module syntax; retain integrity → Gate B → pytest → smoke; finish with functional and visual e2e. Both uv/pip hosted Python jobs run UI contracts and ES-module syntax in the same position. Browser CI still runs `make UV=uv e2e`.

Exact canonical image:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d

ARG UV_VERSION=0.12.9
RUN python -m pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /workspace
COPY pyproject.toml uv.lock README.md ./
RUN UV_PROJECT_ENVIRONMENT=/opt/ior-venv \
    uv sync --locked --extra dev --extra e2e \
    --no-install-project --python "3.12"

ENV PATH="/opt/ior-venv/bin:${PATH}" \
    PLAYWRIGHT_BROWSERS_PATH="/ms-playwright" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"
```

[PROPOSED] The container runner mounts these inputs read-only: `src/`, `config/`, `data/`, `docs/authority/`, `browser_tests/`, `scripts/`, `pyproject.toml`, and `uv.lock`; it overlays only `browser_tests/baselines/v0.3.0/` and `.artifacts/e2e/` read-write. It passes only `IOR_E2E_EXPLICIT`, artifact/baseline mode/path and change-reference variables, uses `--network=none --ipc=host`, and never mounts repository root, `.env`, `.git`, home or the Docker socket.

Exact `.dockerignore` minimum:

```dockerignore
.env
.git
.venv
.workflow
.artifacts
.pytest_cache
test-results
playwright-report
node_modules
__pycache__
*.pyc
```

Exact active CI command changes:

```yaml
- name: Validate UI catalogue, token and copy contracts
  run: uv run --locked --extra dev python scripts/check_ui_contracts.py
- name: Compile Python
  run: uv run --locked --extra dev python -m compileall -q src scripts tests
- name: Check JavaScript ES-module syntax
  run: uv run --locked --extra dev python scripts/check_es_modules.py --node node
```

```yaml
- name: Install Chromium dependencies
  run: >
    uv run --locked --extra dev --extra e2e
    python -m playwright install --with-deps chromium
- name: Run bilingual real-browser and visual gates
  run: make UV=uv e2e
```

- [PROPOSED] The pip job uses the same two script commands without `uv run`; the local Make target uses `$(UI_CONTRACTS)` and `$(ES_MODULE_CHECK)`. Remove the explicit `fonts-noto-core` apt line because local product-font hashes and actual rendering—not host fontconfig—become the gate. Keep job name, action versions, failure-only artifacts, permissions, checkout credentials and all optional-failure prohibitions unchanged.

## 17. Tests

### 17.1 Default/browserless contracts

[PROPOSED] Exact new or materially changed tests:

```text
tests/test_ui_catalogue.py::
  test_ui_catalogue_metadata_locales_and_version_are_exact
  test_ui_catalogue_locale_keys_and_placeholders_match
  test_ui_catalogue_values_are_nonempty_nfc_strings
  test_ui_catalogue_excludes_policy_synthetic_labels
  test_every_ui_string_usage_resolves_without_unused_keys
  test_visible_ui_copy_is_not_hard_coded_outside_catalogue
  test_ui_strings_endpoint_returns_valid_en_and_ar_bundles
  test_unknown_ui_strings_locale_returns_404
  test_malformed_ui_catalogue_fails_closed_without_partial_bundle

tests/test_ui_tokens.py::
  test_token_layer_declares_every_required_token_family
  test_every_production_stylesheet_is_literal_free_outside_tokens
  test_rendered_dossier_css_is_literal_free_outside_tokens
  test_only_bounded_capability_fill_inline_style_is_allowed
  test_scanner_rejects_colour_length_font_shadow_z_and_physical_direction_literals
  test_accessibility_token_pairs_resolve_to_wcag_aa

tests/test_es_modules.py::
  test_index_loads_app_as_an_es_module
  test_module_graph_has_named_exports_no_defaults_and_resolved_local_imports
  test_every_browser_module_has_at_most_199_lines
  test_es_module_syntax_checker_checks_every_js_file_in_module_mode

tests/test_font_assets.py::
  test_vendored_fonts_and_licenses_match_exact_bytes_and_hashes
  test_font_source_metadata_records_exact_fontsource_unicode_ranges_and_local_urls
  test_browser_preflight_requires_intended_product_fonts
  test_catalogue_and_renderer_literals_are_covered_by_vendored_unicode_ranges
  test_uncovered_chrome_symbols_use_accessible_svg_or_css_glyphs

tests/test_visual_baseline_contract.py::
  test_visual_manifest_has_exact_40_entry_locale_viewport_screen_matrix
  test_visual_manifest_and_every_webp_hash_size_dimensions_and_rgb_decode_match
  test_visual_baseline_files_are_lossless_webp_with_600_kib_and_12_mib_budgets
  test_visual_tolerance_is_global_fixed_and_strict
  test_visual_code_never_reads_s06_documentary_references
  test_update_requires_explicit_flag_reason_non_ci_and_canonical_image
  test_container_runner_exits_2_with_clear_message_when_docker_is_unavailable
  test_container_runner_mounts_only_the_exact_allow_list
  test_container_runner_requires_chromium_1234_and_records_browser_metadata
  test_make_e2e_compare_does_not_require_docker_or_container_runner
  test_ci_contains_no_baseline_update_mode_or_target
```

- [PROPOSED] `test_static_frontend.py` retains evidence-mode, disclosure, authority, dossier-action, accessibility and reduced-motion assertions, but reads catalogue/token/module sources instead of hard-coded English/hex.
- [PROPOSED] `test_dossier_contract.py` runs both locale HTML variants; checks `<html lang/dir>`, localized headings, print tokens, source islands, dual policy labels in simulated mode, and zero labels in public mode.
- [PROPOSED] `test_synthetic_isolation.py` asserts policy 1.2.0, both policy labels, English scenario compatibility, and every synthetic evidence row’s two projected labels.
- [PROPOSED] `test_simulation_fidelity.py` asserts rule/decision/scenario projections contain both exact policy values without adding scenario fields.
- [PROPOSED] `test_authority_disclosure.py` adds `ui_strings: 1.0.0`; `test_integrity_contract.py` requires the catalogue and Core markers in the authority manifest.
- [PROPOSED] `test_api.py` covers locale resource, static module/CSS/font serving, dossier locale query and removal of the `/docs` demo anchor.

### 17.2 Browser inventory

[PROPOSED] Add `Locale(code, bcp47, direction)` constants `EN`/`AR`. Parameterize all existing 17 behaviors by locale and add one dedicated switch test. Rename only the visual test. Node matrix:

| Test | Nodes after locale dimension |
|---|---:|
| portfolio | 4 |
| card open | 8 |
| selector | 8 |
| hero | 4 |
| mode switch | 4 |
| navigation | 2 |
| `test_locale_switch_updates_document_url_storage_and_preserves_state` | 2 |
| dossier popup | 8 |
| clipboard | 8 |
| print/PDF | 8 |
| keyboard/focus | 16 |
| workspace axe | 8 |
| dossier axe | 8 |
| workspace bidi/font | 4 |
| dossier bidi/font | 8 |
| responsive/mirroring | 16 |
| governed visual baseline | 4 |
| failure-collector self-test | 2 |
| **Total** | **122** |

- [DERIVED] Nonvisual functional nodes are 118; visual nodes are 4; the visual nodes compare 40 lossless WebPs.
- [DERIVED] S06 hosted execution was 62 nodes in 139.9 seconds. Linear scaling gives about 284 seconds; S07 sets a six-minute browser-test execution budget excluding dependency setup and records actual duration rather than claiming it in advance.
- [SPECIFIED] Axe has 16 locale/page-state nodes, keyboard has 16 locale/viewport nodes, and failure hooks have no new filter, ignore or accepted-error path.
- [PROPOSED] English/Arabic locators use stable IDs/data attributes plus catalogue expectations, never English-only role names.

### 17.3 Required behavioral assertions

- [SPECIFIED] Both locales reproduce steel public INVESTIGATE, steel simulated ADVANCE with real unchanged, and PP public/simulated REJECT.
- [PROPOSED] Arabic nodes assert html `dir=rtl`, computed body direction, sidebar on the right, main logical offset on the right, `text-align:start` resolving right, and English analytical islands resolving LTR.
- [PROPOSED] English nodes assert inverse layout evidence.
- [PROPOSED] Locale switch in each direction preserves PP selection and simulated mode, updates URL/storage/html/catalogue copy, and survives reload/back-forward.
- [PROPOSED] Every simulated surface contains both exact policy labels; every public surface contains neither.

## 18. Validators and generator-diff controls

- [PROPOSED] `scripts/check_ui_contracts.py` exit codes: 0 pass; 1 deterministic findings; 2 read/parse/schema execution error.
- [PROPOSED] `scripts/check_es_modules.py` exit codes: 0 all syntax valid; 1 Node syntax finding; 2 Node/file/process error.
- [SPECIFIED] `scripts/check_threshold_literals.py` and `scripts/check_prohibited_files.py` remain unchanged and run.
- [PROPOSED] Before generation, `verify_integrity.py` is expected to report only hash mismatches for manually changed governed files already present in its manifest (policy and Core 01/02/09); the new catalogue is absent until generation. Any other mismatch stops.
- [SPECIFIED] One `scripts/build_manifests.py` run is permitted only after ADR-011 exists, focused/default/smoke/Goldens/Gate B/118 functional browser nodes/40-baseline update/122 compare nodes pass, and the hand-diff is exactly the authorized governed paths.
- [PROPOSED] Permitted generated/human manifest diff:
  - `authority_hashes.json`: changed hash/bytes for evidence policy and Core 01/02/09; one new catalogue row; `generated_on` only if the date differs;
  - `snapshot_manifest.json`: no file-entry change; at most `generated_on` if the date differs;
  - Manifest §11: the same four changed rows plus one new catalogue row;
  - no other authority/config/Core/data row.
- [SPECIFIED] A second generator run is prohibited. Unexpected path, hash row, byte row, generated date or snapshot entry stops the slice for Supervisor review.

## 19. Observable acceptance criteria

1. [SPECIFIED] `?locale=en` produces `lang=en/dir=ltr`; `?locale=ar` produces `lang=ar/dir=rtl`.
2. [SPECIFIED] One topbar control switches both directions, is keyboard reachable, persists only locale, canonicalizes URL, survives reload/popstate, and preserves selected case/mode.
3. [SPECIFIED] Catalogue EN/AR keys/placeholders are equal and non-empty; every visible chrome string resolves from it.
4. [SPECIFIED] No English or Arabic UI chrome is hard-coded in HTML/JS/Python outside the catalogue.
5. [SPECIFIED] Both policy safety labels—not catalogue copies—appear on every simulated marker in both locales; public surfaces contain neither.
6. [SPECIFIED] Engine analytical fields listed in §5.5 are visibly captioned and marked English/LTR in Arabic UI.
7. [SPECIFIED] Every production CSS raw visual literal occurs in `tokens.css`; scanner has zero findings.
8. [SPECIFIED] Logical properties mirror sidebar/main/alignment with no overflow at all four widths.
9. [SPECIFIED] All browser modules use named exports, no defaults, resolved local imports and ≤199 lines.
10. [SPECIFIED] Recursive ES-module syntax check replaces every active classic single-file check.
11. [SPECIFIED] Vendored font files/licences match exact bytes/hashes and load without external requests.
12. [SPECIFIED] Browser proof identifies `IOR Noto Sans Arabic` as loaded and rendered; tofu checks pass.
13. [SPECIFIED] Dossier HTML chrome supports `locale=en|ar`, keeps print behavior, dual disclosure and source islands; JSON compatibility is unchanged.
14. [SPECIFIED] Demo UI has no `/docs` link; engineer `/docs` route remains available.
15. [SPECIFIED] Browser suite collects/passes 18 named tests / 122 nodes (118 functional + 4 visual), zero explicit skips, zero collector errors and zero axe violations.
16. [SPECIFIED] Exactly 40 lossless WebP baselines (10 screens × 2 locales × desktop/tablet) satisfy ≤600 KiB each and ≤12 MiB total, and a valid hash manifest compares them under one fixed tolerance; 1920×1080 and 2560×1440 remain functionally covered without pixel baselines.
17. [SPECIFIED] Baseline update is impossible in CI or without explicit flag/reason and uses the pinned Noble image; ordinary `make e2e` comparison remains Docker-free.
18. [SPECIFIED] S06 documentary reference directory is byte-identical and absent from comparator inputs.
19. [SPECIFIED] Authority manifests verify after the one generator run; only enumerated rows change.
20. [SPECIFIED] Steel/PP public goldens and both simulated outcomes remain exact.
21. [SPECIFIED] KL-21/KL-31 and V3-A3/A6/A8/A10/G7 documentation is evidence-accurate and provisional until delivery.
22. [SPECIFIED] No secret/prohibited/helper/data/threshold/sector/DOCX/golden path enters the candidate.
23. [SPECIFIED] Supervisor and independent Grok Reviewer reach zero findings before delivery; local green is not approval.

## 20. Documentation changes

- [PROPOSED] `DEVELOPMENT_GUIDE`: catalogue schema/edit discipline; module map; token grammar/scanner; exact font provenance; locale URL/localStorage; source islands; native and canonical browser commands; baseline compare/update procedure; tolerance, image budget, diff artifacts and CI mismatch handling.
- [PROPOSED] `OPERATOR_RUNBOOK`: visible locale switch, `?locale=`, persistence/reset instruction, Arabic/English demo check, engineer-only `/docs` boundary, and both labels’ interpretation.
- [PROPOSED] `KNOWN_LIMITATIONS`: move KL-21 and KL-31 to provisional S07 closure rows with implementation/test pointers only; no invented PR/CI/merge fact.
- [PROPOSED] `REQUIREMENTS_TRACEABILITY`: add provisional S07 evidence registry; add V3-A8, V3-A10, V3-G7 and promote those new rows no higher than `TESTED` after matching local evidence; extend the already-`COMPLETE` V3-A3/V3-A6 evidence text without demotion or rewriting S06 evidence.
- [SPECIFIED] `ARCHITECTURE_DECISIONS`: ADR-011 records authority class/approval basis, catalogue endpoint, source islands, the exact approved Arabic safety label as owner-amendable governed text that implementation may not vary, owner-amendable Western (`latn`) digits/Gregorian dates/verbatim source spans, fonts, KL-31 removal, the 40-WebP comparator/tolerance/update governance, Core marker strategy and exact generator diff. Source: Supervisor rulings PR-01, PR-03 and PR-04.
- [SPECIFIED] `UX_GENUI_DEMO_SPEC` §8 records whole-interface locale parity, html direction, logical layout, source-language islands, dual policy labels, and owner-amendable Western digits/Gregorian dates/verbatim source spans; it makes no claim of bilingual engine narrative. Source: Supervisor rulings PR-03 and PR-04.
- [PROPOSED] `DEPLOYMENT_GUIDE`, `README`, `final_acceptance.sh`: recursive ES-module syntax command and locale/font/offline asset facts.
- [PROPOSED] `CHANGELOG` Unreleased: bilingual shell, policy labels, modules/tokens/fonts, governed baselines, and API-link removal; no 0.3.0 release claim.
- [SPECIFIED] The PR description reports the exact byte size of all binary additions, separated into vendored fonts and governed WebP baselines, and records the approved Arabic label. Source: Supervisor plan-review condition and PR-03.

### 20.1 Reviewer-approved baseline update procedure

1. [SPECIFIED] Link the intended UI change and review reference in `IOR_BASELINE_CHANGE_REF`; baseline-only “make CI green” changes are prohibited.
2. [SPECIFIED] Run 118 nonvisual nodes green first: `make e2e-functional`.
3. [SPECIFIED] Run `IOR_UPDATE_VISUAL_BASELINES=1 IOR_BASELINE_CHANGE_REF="<slice/finding>" make e2e-update-baselines` outside CI.
4. [SPECIFIED] Inspect all changed WebPs, manifest, size/hash/source inputs and generated diff artifacts; no known defect may be captured.
5. [SPECIFIED] Run `make e2e` in compare mode and full default/golden/integrity/smoke gates.
6. [SPECIFIED] Independent Reviewer examines image changes and returns zero findings. CI only compares; it never writes.
7. [SPECIFIED] If CI exceeds tolerance, retain artifacts and determine source/environment mismatch. Do not update from CI, loosen thresholds, mask regions or accept a platform exception. A platform/Chromium/font change requires a reviewed baseline update and documented rationale.
8. [PROPOSED] Use `make e2e-visual-canonical` to distinguish host-rendering drift from a real candidate mismatch; a canonical pass does not waive a red required CI check.

## 21. Requirement traceability

| Requirement | Implementation | Proving evidence |
|---|---|---|
| V3-A3 | logical CSS/token responsive values | 16 responsive nodes + visual matrix |
| V3-A6 / R-4 | 40 lossless WebPs, manifest, comparator/update gate | 4 visual nodes + browserless manifest tests |
| V3-A8 / NFR-007 | catalogue, locale endpoint/runtime, html direction | catalogue/API/switch/bidi tests |
| V3-A10 / SG-TR-008 | tokens, modules, named exports, ≤199 lines | UI/module scanners; axe/keyboard |
| V3-G7 / INV-03 | policy 1.2.0 dual labels and projections | policy/isolation/API/browser/dossier tests |
| NFR-004 | local modules/CSS/fonts/catalogue; no `/docs` link | collector, static/API font tests |
| NFR-006 | semantic switch, focus, contrast | 16 keyboard + 16 axe nodes |
| FR-014 | dual policy marker and synthetic row treatment | static/isolation/browser assertions |
| FR-060–063 | unchanged ten renderer registry | API registry and module-dispatch tests |
| FR-064 | locale-aware printable HTML, unchanged JSON | dossier contract/browser print/PDF |
| Core 08 §5 | latn normalized analytics; original spans preserved | formatter/extraction browser tests |
| Core 09 §2.7/Gate G | doubled locale browser layer + visual oracle | 122-node run and CI |
| Core 02 §9 | locale resource and label policy map entries | Core text/hash/integrity test |
| Manifest §7.3/§7.4/§8 | policy/catalogue/Core ADR and one generation | ADR-011, exact diff, integrity |
| KL-21 | zero literals + modular JS | scanners/module tests |
| KL-31 | remove demo link | static + keyboard inventory + collector |

## 22. Explicit non-goals

- [SPECIFIED] No Executive Mode (S18), screening, graph, claim drill-down, reset flow or new dashboard.
- [SPECIFIED] No translation of rule/decision/evidence/capability/economics narrative generated by engine/snapshots/scenarios; S08–S10 own governed narrative generalization.
- [SPECIFIED] No full bilingual dossier body or productized PDF endpoint; S19 owns them.
- [SPECIFIED] No new GenUI type or registry change.
- [SPECIFIED] No engine formula, state, route, threshold, data, scenario, snapshot, sector-profile, extraction-golden or methodology-DOCX change.
- [SPECIFIED] No Swagger asset vendoring; `/docs` remains engineer-only and absent from demo navigation.
- [SPECIFIED] No external font/CDN/script request at runtime or test runtime.
- [SPECIFIED] No baseline mask, per-screen tolerance, CI update, auto-accept, capture with known defect, S06 reference recapture or lossy baseline.
- [SPECIFIED] No authentication, authorization, official override, Ministry connector/data, live source, database, deployment or app-version bump.
- [PROPOSED] No Firefox/WebKit visual matrix; the governed renderer is the existing Chromium gate.

## 23. TDD task sequence for the Implementer

Every task ends **Confirm → Validate → Test**. Record each intended RED and observed GREEN. Existing behavior that passes immediately is characterization, never fabricated RED.

### Task 0 — Reconfirm authority/protected baseline

1. [ ] Confirm branch/HEAD/status and record every pre-existing modified/untracked path; hash the S06 documentary directory.
2. [ ] Confirm `.env` exists/ignored/untracked without reading it; confirm planned Docker mounts/context exclude it.
3. [ ] Read the approved plan/review, ADR-010 and affected current files; draft ADR-011 authority rationale before governed edits.
4. [ ] Run the existing default and 62-node S06 suite as characterization with `E2E_REFERENCE_DIR` left at ignored default; record actual results.
5. [ ] Confirm no generator, install, lock or browser-install command has yet run.

### Task 1 — RED→GREEN: ES-module decomposition

1. [ ] Add failing module-entry/graph/export/line-count/import/syntax tests.
2. [ ] Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_es_modules.py tests/test_static_frontend.py \
  tests/test_api.py
```

3. [ ] Confirm RED identifies the classic entry/monolith.
4. [ ] Create the exact module graph in §5.1, preserving DOM/API/state behavior and ten-type registry.
5. [ ] Implement `check_es_modules.py`; update active Make/CI/final-acceptance commands and contract tests.
6. [ ] Observe focused GREEN, then run all existing S06 journeys before continuing.

### Task 2 — RED→GREEN: token-only CSS

1. [ ] Add token-scanner negative fixtures and project/dossier failing tests.
2. [ ] Observe RED on current hex/RGB/spacing/font/physical-direction literals.
3. [ ] Create token/CSS files, migrate all values and inline static styles, and change physical to logical properties.
4. [ ] Rewrite S06 contrast contracts to resolve named token pairs, never hard-coded hex pairs.
5. [ ] Observe scanner/static/axe/responsive GREEN; do not alter failure thresholds.

### Task 3 — RED→GREEN: catalogue loader/API and client i18n

1. [ ] Add failing schema/parity/placeholder/no-duplication/API/unknown-locale/hard-coded-copy tests.
2. [ ] Add `ui_strings.v1.yaml` and loader/resource; implement empty-shell `data-i18n`, locale precedence, atomic switch, URL/storage and formatters.
3. [ ] Add source-island/bidi helpers and cover every §5.5 field.
4. [ ] Observe focused default/API GREEN. Do not run the manifest generator.

### Task 4 — RED→GREEN: policy-sourced Arabic safety label

1. [ ] Add failing policy/isolation/simulation/manifest/dossier tests for both policy fields and catalogue exclusion.
2. [ ] Hand-edit policy to exact 1.2.0 §7.1.
3. [ ] Implement one validated label-map function and propagate through evidence, rules, decision, GenUI, dossier and locale bundle.
4. [ ] Observe focused GREEN; verify no data/scenario edit and no literal duplicate.

### Task 5 — RED→GREEN: deterministic vendored fonts

1. [ ] Add failing exact-hash/licence/source/preflight/font-face tests plus a browserless scanner fixture proving that catalogue values and renderer/dossier template literals reject every character outside vendored Fontsource unicode ranges ∪ ASCII ∪ Arabic blocks with no other allow-list.
2. [ ] Acquire only the four exact public files in §5.6 without scripts; verify hashes before copying.
3. [ ] Record the exact Fontsource CSS `unicode-range` values in each `SOURCE.json`; add local font faces/tokens and strengthen preflight/RTL helper.
4. [ ] Replace uncovered text symbols (`→`, `✓`, `✕`) with deterministic inline SVG or CSS-drawn glyphs whose accessible names come from the catalogue; retain covered `—` and `·` as text.
5. [ ] Observe static/preflight/scanner and both-locale font/glyph GREEN with zero external requests.

### Task 6 — RED→GREEN: localized dossier chrome

1. [ ] Add failing EN/AR query, headings, html direction, source-island, dual-label, print-token and public-zero-disclosure tests.
2. [ ] Move CSS to `dossier.css`, embed shared token/dossier layers, add locale query/renderer argument.
3. [ ] Preserve JSON schema and print/PDF behavior.
4. [ ] Observe focused dossier/API/browser GREEN.

### Task 7 — RED→GREEN: close KL-31

1. [ ] Add failing test that demo HTML/browser keyboard inventory has no `/docs` link and retains 15 controls with locale switch.
2. [ ] Remove only the topbar link; leave FastAPI `/docs` route.
3. [ ] Observe static/keyboard/external-origin GREEN.

### Task 8 — RED→GREEN: Arabic browser matrix

1. [ ] Add locale constants/fixtures and parameterize every S06 behavior.
2. [ ] Add dedicated locale-switch test and RTL/LTR mirroring/source-island assertions.
3. [ ] Update stable locators and exact 18-name/122-node contracts without removing any S06 behavior.
4. [ ] Run 118 nonvisual nodes; resolve product defects test-first. Zero skips/collector errors/axe violations required.

### Task 9 — RED→GREEN: comparator/update governance

1. [ ] Add failing Pillow/lossless-WebP/tolerance/40-image-matrix/hash/600-KiB-per-file/12-MiB-total/update-guard/S06-separation tests, plus unit tests for Docker-unavailable exit 2, exact mount allow-list, `chromium-1234` assertion/browser metadata, and Docker-free `make e2e`.
2. [ ] Add `Pillow==12.3.0`, run the one intentional `uv lock`, inspect lock diff and supported Python resolution.
3. [ ] Implement opaque-RGB/lossless-WebP comparator, diff artifacts, canonical Docker update environment and guarded targets; keep host compare independent of Docker.
4. [ ] Run comparator negative fixtures proving one-pixel-under/over, dimension, encoding, budget and manifest failures; verify clear exit 2 when Docker is unavailable.

### Task 10 — Establish governed baselines

1. [ ] Hard precondition: Task 8's complete 118-node functional Arabic/English matrix is green, with zero skips, collector errors or axe violations, before any baseline capture. Also confirm token/module/catalogue/font/default/golden/smoke/Gate B tests are green.
2. [ ] Generate the initial 40-lossless-WebP candidate with:

```bash
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S07-initial-governed-baseline" \
make e2e-update-baselines
```

3. [ ] Validate the exact 10-screen × 2-locale × 2-viewport matrix, opaque-RGB decode, lossless encoding, dimensions, hashes, `manifest.sha256`, ≤600 KiB per image, ≤12 MiB total, font/source hashes, canonical image identity, Chromium revision/browser version and flags.
4. [ ] Run all 122 compare nodes. If any defect is visible, fix it first and repeat the governed update procedure; never retain a known defect.
5. [ ] Re-hash the S06 documentary directory and prove byte identity.

### Task 11 — Authority/Core/ADR finalization and the one generator run

1. [ ] Finalize ADR-011 and Core 01/02/09 markers/minimal wording/mappings.
2. [ ] Run all pre-generation regression except integrity; prove exact goldens and synthetic isolation.
3. [ ] Run `verify_integrity.py` once expecting only the enumerated stale rows; stop on any other finding.
4. [ ] Audit hand-diff: only policy, catalogue, Core 01/02/09 among governed files.
5. [ ] Execute the single generator command shown in §24.2 exactly once and mark that gate consumed; every later reference to manifest generation is verification, not permission for another run.
6. [ ] Audit machine manifests against §18; manually refresh only matching Manifest §11 rows from JSON. Never rerun the generator.
7. [ ] Observe post-generation integrity GREEN.

### Task 12 — Documentation and complete verification

1. [ ] Update docs in §20, preserving Supervisor-owned S06 hunks and using `TESTED` only after observed local proof.
2. [ ] Run the exact proof sequence in §24 on Python 3.12 and default pytest on Python 3.14.
3. [ ] Inspect complete diff, baseline visual set, manifest/hash, protected paths and prohibited/untracked paths.
4. [ ] Write implementation/test-evidence records with actual outputs, assumptions and limitations; prepare the PR-description evidence including exact byte totals for added font binaries and WebP baselines.
5. [ ] Stop uncommitted with candidate path/hash inventory. Do not self-approve.

## 24. Verification commands and evidence

### 24.1 Pre-generation

```bash
uv lock --check
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
.venv/bin/python scripts/check_ui_contracts.py
.venv/bin/python scripts/check_es_modules.py --node node

export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
make e2e-functional
make e2e

PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_golden_cases.py \
  tests/test_synthetic_isolation.py \
  tests/test_simulation_fidelity.py \
  tests/test_ui_catalogue.py \
  tests/test_ui_tokens.py \
  tests/test_es_modules.py \
  tests/test_font_assets.py \
  tests/test_visual_baseline_contract.py
```

- [SPECIFIED] Do not point `E2E_REFERENCE_DIR` at any tracked directory.
- [SPECIFIED] The canonical update command in Task 10 is the only baseline write.
- [SPECIFIED] Delivery evidence/PR description must report exact binary-addition byte totals for fonts and baselines separately.

### 24.2 Single generation and post-generation proof

```bash
PYTHONPATH=src .venv/bin/python scripts/build_manifests.py   # exactly once

PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py

PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
.venv/bin/python scripts/check_prohibited_files.py
.venv/bin/python scripts/check_threshold_literals.py
.venv/bin/python scripts/check_ui_contracts.py
.venv/bin/python -m compileall -q src scripts tests browser_tests
.venv/bin/python scripts/check_es_modules.py --node node
make e2e
make ci
git diff --check
```

- [SPECIFIED] The three workspace proof commands remain in required integrity → pytest → smoke order.
- [PROPOSED] Python 3.14 compatibility:

```bash
uv sync --locked --extra dev --python "3.14"
PYTHONPATH=src uv run --locked --extra dev pytest -q
```

- [SPECIFIED] The Implementer records local evidence only. The Supervisor later stages exact paths, reruns tracked-file prohibited scan and full gates, obtains Grok APPROVE, and owns delivery/hosted CI.

## 25. Rollback and recovery

- [PROPOSED] Before commit, rollback is an inverse patch limited to §6; never use hard reset or discard unrelated Supervisor/untracked work.
- [PROPOSED] Module rollback restores `app.js`/classic script and removes module/CSS/font files together; token rollback restores old stylesheet/dossier CSS and old source contracts together.
- [PROPOSED] Authority rollback restores policy/catalogue/Core/authority JSON/Manifest §11 as one reviewed unit. Do not run the generator merely to accept unexplained restored bytes.
- [PROPOSED] Baseline rollback removes only S07 WebP/manifest/comparator changes; S06 WebPs remain untouched.
- [DERIVED] A stale `ior.locale=ar` after full feature rollback is harmless because v0.2.0 code does not read it.
- [PROPOSED] After merge, revert the single S07 squash commit through a new reviewed PR only if no later slice depends on catalogue/modules/tokens. Otherwise plan a forward compatibility fix.

## 26. Open questions and skills read

### 26.1 Resolved decision

- [SPECIFIED] **OQ-01 — RESOLVED.** The Supervisor-approved default Arabic safety label (owner-amendable; flagged to the owner in the Supervisor report) is exactly `محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة`. It is owner-amendable governed text through a later Manifest §7.3 change; S07 implementation may not vary it. Source: Supervisor ruling PR-03.

### 26.2 Skills read and material effect

| Skill | Material effect |
|---|---|
| `writing-plans` | [VERIFIED] Required exact paths/interfaces/fragments, bite-sized TDD steps and an implementable handoff; user path overrides its default plan location. |
| `test-driven-development` | [VERIFIED] Every behavior/refactor begins with an observed relevant RED; existing S06 paths are honestly characterized. |
| `verification-before-completion` | [VERIFIED] No predicted green claim; §24 defines fresh evidence before handoff. |
| `sanad` | [VERIFIED] Separates governing facts, observed repository state, derivations, proposals and the one open copy decision. |
| `muhasib` | [VERIFIED] Requires scope/path/secrets/tests/assumptions/no-self-approval audit before handoff. |
| `task-standards` | [VERIFIED] Established the principal bilingual government-interface/frontend architecture persona after reading authority. |
| `project-orientation` | [VERIFIED] Required inspection of README, authority/core/control/milestone docs, current code, scripts and tests before proposing additions. |
| `sanad-provenance` | [VERIFIED] Required inline sources for repository facts, public dependency/font metadata and every numerical design input, with proposals labelled rather than presented as authority. |
| `muhasabah-gate` | [VERIFIED] Drives the final check for unsourced claims, hidden assumptions, unmet scope, irreversibility and accidental edits. |
| `al-muhasibi` | [VERIFIED] Challenged the convenient choices: system fonts versus exact vendoring, Swagger vendoring versus removing its demo link, and host-native baselines versus a canonical Noble update environment. |

## 27. Sanad ledger and Muhasib self-audit

### 27.1 Sanad

Tags:

- `VERIFIED`: directly observed in repository/read-only command output or exact public package metadata.
- `SPECIFIED`: explicit owner/rule/methodology/Core/slice requirement.
- `DERIVED`: consequence of cited verified/specified evidence.
- `PROPOSED`: implementation choice subject to Supervisor approval.
- `OPEN`: missing exact owner/linguistic decision.

Mechanical count command:

```bash
rg -o '\[(VERIFIED|SPECIFIED|DERIVED|PROPOSED|OPEN)\]' \
  ".workflow/slices/S07-bilingual-interface-foundation/plan.md" \
  | sort | uniq -c
```

```text
VERIFIED=40
SPECIFIED=123
DERIVED=22
PROPOSED=127
OPEN=0
```

### 27.2 Muhasib

- [VERIFIED] Mandatory authority, relevant Core/implementation/control/milestone/slice records, current frontend/server/config/tests/toolchain and required skills were opened before planning.
- [VERIFIED] The planner attempted the authoritative DOCX with the file-reading tool; binary rendering was unsupported. Its exact governed hash was verified and the relevant sections were read through the searchable mirror, with Core cross-checks. No claim is made that the binary document text itself was rendered.
- [VERIFIED] The planner performed read-only Git/status/version/font/hash inspection and public font/dependency metadata lookup only; no install, lock, browser install, test suite, manifest generation, stage, commit, push, merge or tag occurred.
- [VERIFIED] `.env` content and helper-script content were not read; no secret value was printed.
- [VERIFIED] The only planner-created artifact is this `plan.md`; `persona.md` and every Supervisor-owned path remain untouched.
- [SPECIFIED] The plan preserves both public goldens, synthetic isolation, ten GenUI component types, decision semantics and later-slice ownership.
- [PROPOSED] Engineering figures introduced here—font files, 199-line maximum, 40 images, 600-KiB per-file/12-MiB total budgets, tolerance and six-minute browser budget—are explicitly implementation controls, not business facts.
- [SPECIFIED] OQ-01 is resolved by Supervisor ruling PR-03; the exact approved Arabic warning, owner-amendable status, and no-variation implementation constraint are recorded in §§7.1, 20 and 26.1.
- [SPECIFIED] Implementer builds but cannot approve; Supervisor controls delivery; Grok independently reviews the final exact candidate.
- [VERIFIED] Muhasib result: PASS for planner handoff, subject to Supervisor plan review; this is not implementation approval.
