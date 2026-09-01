# UX and GenUI Demonstration Specification

## 1. Product surface

The MVP has one primary product: an adaptive **Decision Workspace**. The executive overview is an entry point, not a separate analytical product.

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
- Decision JSON can be copied.
- Navigation scrolls to page sections.
- All controls are keyboard reachable.

## 8. Arabic support

- Arabic names and source spans use `dir=rtl`;
- no transliteration replaces the original source;
- normalized English fields do not hide the Arabic evidence span.

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
