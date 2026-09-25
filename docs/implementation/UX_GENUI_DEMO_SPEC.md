# UX and GenUI Demonstration Specification

## 1. Product surface

The MVP has one primary product: an adaptive **Decision Workspace**. The executive overview is an entry point, not a separate analytical product.
The bilingual Screening section is a public-evidence sibling region within
that workspace: summary, five route-specific queues, record drill-down and
one persistent evidence-passport area. It is not a ranked opportunity
dashboard or a separate product.

The interface must make the evidence boundary legible before it makes the analysis impressive.

## 2. GenUI interpretation

For this regulated decision context, GenUI means:

> the backend selects and configures approved interface components at runtime from structured decision context.

It does not mean unrestricted model-generated HTML or executable code.

Benefits:

- the interface adapts to evidence availability;
- `INVESTIGATE`, `REJECT` and `ADVANCE` emphasize different decision content;
- the component registry remains testable and auditable;
- the same decision contract can later support analyst, executive and reviewer surfaces.

## 3. Approved component registry

| Component | When shown | Purpose |
|---|---|---|
| `integrity_banner` | always; enhanced in simulated mode | show public state, active state and synthetic warning |
| `decision_hero` | always | state, route and rationale |
| `metric_grid` | always | latest trade, concentration, gap and support |
| `trade_chart` | when trade exists | show public signal and quantity/value movement |
| `rule_ledger` | always | expose R0–R12 execution and evidence limits |
| `capability_matrix` | always | show K/U, states and D\* publication control |
| `economics_panel` | only when economics exists | show NPV, IRR, S\*, national value, capacity ratio and EVSI |
| `evidence_ledger` | always | source, class, status and boundary |
| `data_unlocks` | always | exact missing facts and active synthetic blocks |
| `decision_actions` | always | dossier and JSON output |
| `graph_view` | after decision actions; collapsed until opened | four fixed evidence-backed dependency views with deterministic SVG and native controls |
| `screening_summary` | Screening summary | universe, coverage, disposition and route-specific queue counts |
| `screening_queue` | a selected screening queue | Pareto-ordered entries and pagination without an ordinal master list |
| `screening_record` | a selected HS6 record | governed ledger, exclusions, needs, adjacency and evidence-basis anchors |

## 4. Context rules

### Public `INVESTIGATE`

- gold state;
- missing facts prominent;
- D\* shown as gated;
- no fabricated economics panel;
- route is a priority to test, not a recommendation.

### Public `REJECT`

- red state;
- falsifying evidence prominent;
- support shown as no intervention;
- narrow exceptions stated separately.

### Simulated `ADVANCE`

- public state remains visible;
- simulated state appears after an arrow;
- yellow synthetic warning mandatory;
- gap, D\*, economics, national value, conditions and kill conditions available.

### Simulated `REJECT`

- synthetic detail confirms why additional support is unnecessary;
- the interface must not imply that richer data always creates an opportunity.

## 5. Information hierarchy

1. Evidence boundary
2. Decision state and route
3. Four decision metrics
4. Public signal
5. R-rule ledger
6. Capability
7. Economics/EVSI if present
8. Evidence passport
9. Data unlocks
10. Dossier actions

## 6. Visual system

- deep navy communicates institutional seriousness;
- teal marks resolved/positive controls, not generic “good” scores;
- gold marks investigation and synthetic disclosure;
- red marks rejection or prohibited intervention;
- white analytical cards on a cool neutral background;
- typography prioritizes state and route over decorative dashboards.

## 7. Interaction requirements

- Public / Ministry Simulation toggle updates portfolio and active case.
- Opportunity selector preserves the chosen evidence mode.
- Case cards open the workspace.
- Dossier opens in a printable new window.
- The dossier toolbar provides native Print / Save PDF, downloadable JSON and return to the same case, evidence mode and locale. Executive→Analyst preserves case/locale; the user explicitly chooses analyst evidence mode before export.
- Decision JSON can be copied.
- Navigation scrolls to page sections.
- Screening navigation opens the summary; every queue entry drills into its
  record and each evidence-basis anchor focuses a passport card in the
  persistent evidence region.
- UNAVAILABLE, PARTIAL and empty-queue states remain labelled and actionable
  without fabricated counts.
- The graph remains request-free while collapsed; opening exposes the four fixed
  views, native node/edge controls and stored-evidence drill-down.
- Graph empty, unavailable, transport and rejected-response states remain
  distinct and never substitute fixture or artifact rows for a failed live view.
- All controls are keyboard reachable.

### S19 dossier and shared trade presentation

The dossier is an evidence-backed reading surface. Its first printed A4 page is a summary; the appendix begins on page2 and contains identity/boundary, demand, named supply, gap/false-positive controls, capability/all nine routes, economics/intervention, competition/policy, rule ledger, evidence/contradictions, conditions/kill conditions/next facts and authority. Full public conclusions stay visible alongside separately marked simulation. A lead condition may link to an accurately counted full list; do not truncate source content to fit. Missing data and NOT_CALCULABLE remain distinct from genuine zero.

Arabic chrome and rule name/result/effect come from governed Arabic catalogues/narratives. Original source passages remain attributed and correctly directed; technical IDs/HS/standards/units/URLs remain complete LTR isolates. Responsive390/1024/1440 layouts must retain readable full identity and both synthetic labels without body overflow or clipped rows. Both labels repeat on every simulated printed page in a reserved non-overlapping region; public exports carry neither. Minimum print body sizes are10.5pt EN/11.5pt AR. Native Chromium Save PDF is the explicit workflow, with no server PDF or accessibility-certification claim.

The shared public trade chart retains its existing curves and units in Analyst public/simulated and Executive Signal. A visible adjacent note states that each line uses its own scale, so line heights are not comparable. Closed native **View observed values** details expose a captioned table of every actual public year, value and quantity, with column/row headers, genuine zero and explicitly unavailable cells. Enter/Space toggles details and Tab reaches it with visible focus; no tooltip-only disclosure, interpolation or new calculation. In canonical Executive Signal, the note/closed summary and every prior required content box remain fully visible. Only the declared chart-local and necessary below-card flow changes are eligible for the reviewed visual refresh.

AR-V01 dossier clipping and TRADE-SCALE-01 explanation/data access remain required S19 repairs until original-defect RED→GREEN, complete rendered/PDF proof and independent implementation review pass. The experience specification states acceptance requirements; it does not certify the unfinished candidate.

## 8. Arabic support

- All interface chrome and governed labels have Arabic/English catalogue
  parity. `?locale=en` sets `<html lang="en" dir="ltr">`; `?locale=ar` sets
  `<html lang="ar" dir="rtl">`, and logical CSS properties mirror the shell.
- The visible topbar switch fetches and validates the target bundle before an
  atomic document, URL, local-storage and rendered-content update.
- IDs, HS codes, hashes, standards, currencies, quantities and dates are
  directionally isolated as LTR technical values. Arabic names and original
  Arabic source spans retain `lang="ar" dir="rtl"`.
- Governed rule names, results, decision effects, decision boundaries and
  screening vocabulary render from the active-locale catalogues. In Arabic,
  those values contain Arabic catalogue prose rather than English
  source-language islands. Only verbatim source spans and classified
  technical values remain directionally isolated LTR islands.
- Every simulated surface repeats both warning labels from evidence policy
  1.2.0. Neither label is duplicated in the UI catalogue.
- Western (`latn`) digits, Gregorian dates and verbatim source spans are the
  Supervisor-approved S07 presentation defaults. They are owner-amendable
  through the applicable authority change; implementation may not silently
  vary them.
- Exact local Noto Sans and Noto Sans Arabic assets are SHA-verified and
  rendered without a runtime CDN. Symbols outside their vendored Unicode
  ranges use catalogue-labelled inline SVG or CSS glyphs.

## 9. Responsive behavior

- desktop: fixed navigation, two-column workspace;
- tablet: single-column workspace, horizontal or wrapped controls;
- mobile: stacked navigation and metric cards.

## 10. Accessibility

- semantic buttons and labels;
- state is communicated by text, not color alone;
- sufficient contrast;
- SVG charts include accessible labels;
- visible focus behavior inherited from browser controls;
- reduced dependency on hover.

## 11. Demo-specific polish

The interface is deliberately offline and contains no external font, chart or CDN dependency. This prevents a Ministry presentation from failing because of network restrictions.

## 12. Executive journey and analyst continuity

Open `/executive?opportunity=SAU-H0-721049&step=SIGNAL&locale=en` or use `locale=ar` for Arabic. The case selector and eight-step rail, Previous/Next controls, locale switch and browser history preserve a complete selected-case context. The header compares immutable public and conditional simulated conclusions before the active explanation. Imports are an investigation signal; rules expose false-positive controls, public missing facts precede hypothetical evidence, and all nine routes retain lower-route precedence. Route detail and intervention expose stored economics, competition, support and national value; conditions explain when to stop.

The four vectors stay separate. Dataset unlocks distinguish loaded cases from screening records. Synthetic EVSI has its own warning and availability; an absent estimate is not zero. Claim controls show exact current passports, contradictions and case-wide unresolved needs; Escape returns focus. English source text retains its source-language caption in Arabic. Native Analyst/Executive links preserve opportunity and locale. A claim's graph link opens the existing analyst graph in its validated branch/view; service failure remains an unavailable state, with no fabricated graph content.

The executive surface uses the existing typography/tokens and fixed component registry, with RTL logical layout, readable identifiers, keyboard focus, native expandable detail and stacked narrow layouts. Loading, empty, unavailable, contradictory, not-calculable and failed-locale states are part of the experience contract. Actual screenshots and complete browser journeys must accompany independent review; baseline comparison alone does not establish usability.

### S18b AM2 graph refinement for §§8–10

At narrow widths the graph selector, warnings, native lists and source passports remain within the panel. The SVG intentionally scrolls horizontally with a named keyboard region and localized Arrow-key instruction; the full native list remains below. English company source names are preserved when Arabic is absent, with a visible Arabic source-language caption and accessible description. Genuine Arabic names retain Arabic direction. No invented translation, decorative graph content or global LTR exemption is permitted.


### S18b AM4 inspection additions

Open graph stored-evidence selections in both modes and locales. Confirm full source titles with visible source-language captions, localized evidence statuses, separate readable opportunity/evidence identities, safe named external links, retained contradictions and both simulation disclosures. Arabic company/source names are not invented. At390px graph controls wrap coherently; the720px diagram and native list remain usable. Tab into the two labelled analyst tables and use native arrows to reach both ends. In executive Simulated Evidence, expand the native capability legend, read0/1/2/3/U definitions and the simulation note, and verify every original dimension code against the API. U remains unknown/unavailable. Inspect all eight steps at390/1024/1440 in English and Arabic, including source return focus and open passports. Canonical screenshot approval remains separate from diagnostic capture.
