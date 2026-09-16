# 07 — Deterministic Rule, Capability, Economics and Decision Engine

<!-- core_version: 2.0.0; supersedes: 1.0.0; effective_date: 2026-09-02 -->

## 1. Scope

This specification governs all calculations and state transitions in the MVP. It combines the rulebook, capability test, economics, intervention logic and EVSI because they form one deterministic decision engine.

## 2. Execution-state contract

Every rule returns:

```json
{
  "rule_id": "R2",
  "execution": "FULL",
  "fired": true,
  "result": "Quantity-led expansion signal fires.",
  "decision_effect": "Separate structural volume growth from price movement.",
  "metrics": {}
}
```

Meanings:

- **FULL:** required grain and quality exist.
- **DEGRADED:** a disclosed proxy exists; cannot alone support `ADVANCE` or a specification conclusion.
- **DISABLED:** no defensible proxy; no inference.

A disabled rule remains visible in the ledger.

## 3. Rule semantics

### R0 — Identity

Passes when the frozen classification and mapping are valid. It does not mean the specification/application is fully resolved.

### R1-F — Full persistence

Requires complete monthly or consecutive-year retained exposure. The current public fixtures intentionally do not claim it.

### R1-D — Degraded persistence

Fires when at least three positive observed years exist in a four-year window, with no interpolation and no known classification break. Confidence is capped at C and it cannot support `ADVANCE` alone.

### R2 — Quantity-led expansion

```text
ΔlnV = ΔlnQ + ΔlnUV
share = |ΔlnQ| / (|ΔlnQ| + |ΔlnUV|)
```

Fires when:

- quantity change is positive;
- contribution share ≥ configured threshold;
- quantity growth meets the configured initial flag.

### R3 — Concentration

Fires when HHI or largest-supplier share meets the configured threshold. It creates a resilience/diversification candidate, not an automatic local factory.

### R4-F — Full UV heterogeneity

Requires coverage, cell count, BIC improvement, separation and cluster materiality. It is disabled in the current annual snapshots.

### R4-D — Degraded UV dispersion

May open product-mix/specification research. It shall never return a confirmed grade, cluster or quality conclusion.

### R5 — Domestic supply plus imports

Opens tests for specification, qualification, capacity, price, timing, application and allocation mismatch.

### R6 — Capacity pressure

Requires effective utilization and a target-specification shortage. Public nameplate is insufficient.

### R7 — Latent capacity

Requires verified equivalence, availability and timing. It may support no intervention, market linkage or barrier removal.

### R8 — Committed demand

Uses awarded/financed demand separately from announced pipeline.

### R9-S — Coarse adjacency

Same product/process family plus another capability signal opens full capability assessment. It does not assign D\*.

### R10 — Strategic criticality

Requires responsible-authority confirmation for formal criticality. Concentration may still open a resilience review.

### R11 — Economic exclusion

Rejects or monitors structurally uncompetitive or generic-capacity propositions. In the PP golden case, exports above 50× imports plus large established capability are sufficient to reject generic support.

### R12 — Evidence value

Names missing facts and, where inputs exist, calculates EVSI.

### S08 computed public-rule semantics

R1-D emits the configured `confidence_cap`.

R2 compares the two latest usable observed years and computes quantity CAGR
over their observed span:
`(Q_latest / Q_previous)^(1 / (year_latest - year_previous)) - 1`.
Missing years are not interpolated.

R3 computes HHI and largest-supplier share independently on value and
quantity. A basis without complete partner rows or a source-attributed
calculated disclosure is `NOT_CALCULABLE`. The rule fires when either
calculable basis meets either configured test. The frozen steel calculated
value disclosure executes FULL; its quantity basis is NOT_CALCULABLE.

R4-D computes valid comparable coverage against its dedicated configured
`minimum_valid_value_coverage`, quantity-weighted median and quartiles, IQR,
and a descriptive farthest-observation candidate from annual partner rows,
or uses a source-attributed calculated disclosure. It remains DEGRADED and
may open only product-mix/specification research. It never claims a cluster,
grade, quality, or localization case.

For PublicSnapshot 2.2.0, R3 and R4-D consume the typed `partner_detail`
state. Missing rows emit `PARTNER_DETAIL_MISSING` with the governed reason;
an observed empty provider envelope emits `PARTNER_TRADE_OBSERVED_ZERO`.
Neither state publishes HHI or dispersion. Missing evidence handling is
explicit: missing evidence is never rendered as zero. OBSERVED rows continue
through the calculations above.

R5 computes retained imports, net import exposure, apparent consumption, and
import penetration when their physical inputs exist. Missing inputs remain
`NOT_CALCULABLE` with named reasons. Verified domestic capability plus
positive imports is a DEGRADED coexistence proxy; the FULL rule applies the
configured penetration threshold.

R9-S requires verified same process family, at least one typed methodology
signal, and no known hard-gate failure. Unresolved gates still block route
publication but do not prevent the coarse screen.

R10 is FULL when a responsible-authority criticality designation exists,
DEGRADED when computed R3 alone opens a resilience review, and DISABLED
otherwise.

R11 computes gross `export_import_value_ratio = exports_usd_m / imports_usd_m`
from the latest row whenever both operands are positive and numeric. A
disclosed ratio is retained and reported separately and, when present, must
be consistent with the computed value within absolute tolerance `0.05`.
The public generic-capacity warning requires the computed ratio to exceed the
configured strict threshold and established domestic capability evidenced by
at least one positive observed A/B/C producer nameplate. Missing exports or
imports produce DEGRADED/false; a calculable ratio with established capability
executes FULL whether the predicate is true or false. Product IDs, disclosed ratios, and authored flags never determine the predicate.

## 4. Capability engine

### 4.1 Effective capacity

`Qeffective = Nameplate × Availability × Yield × Qualification share × Market allocation`.
All factors are within `[0,1]`. A public nameplate without the other factors
does not establish effective qualified supply.

### 4.2 Dimension states

Capability states are `0`, `1`, `2`, `3`, and `U` with the meanings fixed by
methodology §6.4. `U` is unknown evidence, never zero distance.

### 4.3 K, U and D\*

`K = Σ known weights`; `U = 1 − K`;
`Dknown = Σ(w × d/3) / K`; and
`D* = min(1, Dknown + λU)`.

The engine loads the nine weights and the complete hard-gate identifier set
from the selected sector profile. A profile is one of `coated_steel`,
`technical_plastics`, `pharma_api`, `fertilizers`, or
`fabricated_aluminium`. Unknown profiles fail closed.

D* publication requires all of the following:

1. `K >= Kmin`;
2. every configured profile hard gate is present and resolved;
3. every decision-specific hard gate is resolved;
4. no hard gate is a known failure/state `3`.

An internal pre-gate value may be returned for diagnostics. The public
`d_star` and route band remain null whenever a publication condition fails.
A state `3` on a non-hard-gate dimension remains part of D* and does not by
itself suppress a greenfield-likely band.

### 4.4 Route bands

The four route bands are loaded from versioned threshold configuration. A
published band is a technical hypothesis and never an authorization.

### 4.5 Sector profiles

Every profile contains the same nine dimension identifiers, weights that sum
to `1.0`, and the exact hard-gate identifiers derived from methodology §6.3.
Profiles are frozen per sector cycle and are never altered per case. Profile
weights and hard gates are operating configuration under Authority Manifest
§7.3.

## 5. Economics and route-evidence engine

### 5.1 Unsupported case first

Every public route hypothesis is evaluated against no action on the same
auditable basis. Unsupported use of existing capacity, unsupported
brownfield, and unsupported greenfield are evaluated before financial
support. A non-financial route is evaluated before a financial route that
addresses the same constraint.

### 5.2 Route evidence

For routes 1–7, a route-evidence record may supply evidence-backed findings
about technical feasibility, full removal of the binding constraint, whether
the investment is already approved/financed or would proceed without the
intervention, whether a policy prohibition exists, whether distortion is
unacceptable, whether the intervention is proportionate, downside cash
flows, national-value components, and competition inputs. Every record
carries public evidence IDs. Missing values remain `UNAVAILABLE`; derived
feasibility, additionality, permissibility, route status, and selection remain
`NOT_CALCULABLE`.

Route-evidence fields are analytical inputs, not authored decisions. State,
route status, precedence, and selection are calculated by code.

### 5.3 Economics

`NPV = Σ FCFt/(1+h)^t`. IRR is solved deterministically by bracketing and
bisection and is null without a sign change. `S*` is the minimum configured
support step for which NPV and IRR meet their configured tolerances; no passing
support below the configured maximum means the route does not pass economics.

Incremental national value is domestic value added + exports + resilience
value + knowledge/skills + fiscal receipts − government cost − displacement
− resource/environment cost − risk allowance. The competition ratio is
`(existing effective target capacity + proposed incremental capacity) /
downside demand`; its configured boundary remains a warning rather than an
automatic hard exclusion.

Threshold predicates use full-precision intermediates; rounded values are
presentation only.

A route can be `passes` only when its required downside economics, positive
incremental national value, competition, additionality, distortion,
proportionality, and policy gates pass. An explicit failed gate yields
`fails`; any required unavailable gate yields `NOT_CALCULABLE`.

## 6. Missing facts and value of information

The public engine derives evidence needs from unresolved decision-critical
fields, unknown capability dimensions, unresolved profile and
decision-specific hard gates, unavailable retained-flow decomposition, and
unavailable route economics. It does not read a missing-fact list from the
snapshot.

Each evidence need has a controlled code, the blocked field or route, the
public evidence IDs already available, and a plausible route effect. A need
has positive decision value for state selection only when the named fact can
change a state or route. Numerical EVSI remains `NOT_CALCULABLE` unless
probability, value-difference, evidence-cost, and delay-cost inputs exist.
When they exist, the practical calculation remains
`P(route changes) × |value difference| − evidence cost − delay cost`.

When a material trigger exists but route determination is unresolved
(route economics unavailable or no passing route-evidence record), the engine
emits a route-economics evidence need with positive decision value.

When only DEGRADED material signals fire and no FULL
configuration-permitted supporting signal exists, the engine emits a
re-export/origin decomposition need.

The engine renders evidence needs from the governed bilingual decision
narrative catalogue. The two public goldens retain five substantive needs
each; catalogue wording is selected only by controlled need code and
evidence-state predicate, so exact legacy missing-fact sentences are not a
compatibility requirement.

## 7. Decision algorithm

### 7.1 Public branch

The public branch performs the following ordered steps:

1. validate PublicSnapshot 2.1.0 and reject authored outcomes;
2. evaluate R0–R12 from public evidence;
3. evaluate capability K, U, D*, route publication, and every configured hard
   gate;
4. assess the four decision-critical fields from covering evidence passports;
5. execute the evidence-policy ADVANCE gate;
6. execute all six typed methodology §4.2 hard exclusions;
7. classify exactly one primary methodology §5.3 gap class and ordered
   secondary classes;
8. derive evidenced rejection conditions;
9. evaluate route hypotheses 0→8 and apply precedence;
10. select the preferred hypothesis;
11. derive missing facts, conditions, kill conditions, and bilingual
    narrative; and
12. select the formal state under §7.6.

No public state, route, narrative, missing fact, kill condition, rule result,
or gap class is accepted from a snapshot.

### 7.2 Decision-critical field assessment

The four fields are:

1. `product_identity`;
2. `demand_at_required_specification`;
3. `domestic_supply_or_capability`; and
4. `hard_regulatory_or_process_gate`.

Evidence passports use a controlled `supports` vocabulary. A passport covers
a field only through the governed support-code map. The assessment never
chooses an unrelated "best passport in the file".

For each field, the engine emits covering support codes and passport IDs,
the best evidence class among non-contradictory covering passports, and one
resolution status: `RESOLVED`, `PARTIAL`, `UNRESOLVED`, `CONTRADICTORY`, or
`MISSING`. Absent coverage is Class E and `MISSING`. A non-null contradiction
on a covering passport whose reviewer status is not
`confirmed_by_responsible_authority` makes the field `CONTRADICTORY` for the
gate even when another covering passport has Class A, B, or C.

Identity is `RESOLVED` only when the decision object is resolved. Demand is
`RESOLVED` only when target-specification quantity and its passport
references are present. Capability is `RESOLVED` only when its evidence
class is A/B/C and capability route publication passes. The hard-gate field
is `RESOLVED` only when every configured profile gate and every
decision-specific gate is resolved with covering A/B/C evidence.

### 7.3 ADVANCE gate

The gate loads `decision_critical_fields`, `blocked_classes`, and
`blocked_resolution_statuses` from `evidence_policy.advance_gate`.

The gate consumes only field name, evidence class, and resolution status. It
must not inspect `source`, `synthetic_flag`, producer name, opportunity ID, or
scenario ID.

A field in a blocked class or blocked resolution status blocks ADVANCE. A
real public case may reach ADVANCE when all four fields pass and every
methodology route, economics, national-value, competition, additionality,
distortion, proportionality, and hard-exclusion gate passes. Public evidence
is not categorically barred from ADVANCE.

Synthetic records remain actual Class D and may affect only
`simulation_decision`. S10 supplies the separate declared
`class_if_confirmed` projection required to reuse this gate for a simulated
ADVANCE; S09 does not infer such a class.

### 7.4 Hard exclusions

The engine executes all six methodology §4.2 exclusions before state
selection. Each check returns `SATISFIED`, `NOT_SATISFIED`, or
`NOT_CALCULABLE`, reason code, named inputs, and evidence IDs.

`UNAVAILABLE` input yields `NOT_CALCULABLE`; it never means pass and never
means reject. A `SATISFIED` exclusion yields formal REJECT route 0 before deep
route selection. ADVANCE requires all six checks to be `NOT_SATISFIED`.

### 7.5 Gap taxonomy

The primary class is exactly one of `false_or_measurement`, `quantity`,
`specification_or_quality`, `application`, `timing`, `resilience`, or
`evidence`. Ordered secondary classes use the same vocabulary and exclude the
primary.

`evidence` is primary whenever a decision-critical field is not resolved.
Otherwise the deterministic order is false/measurement, quantity,
specification/quality, application, timing, then resilience. Unit-value
dispersion may support only an evidence need or secondary research signal;
it never proves a specification/quality class.

An optional `constraint_class` refines the operational constraint as
`specification_or_grade`, `capacity_or_availability`,
`cost_or_competitiveness`, `capability_or_technology`,
`qualification_or_certification`, or `commercial_or_relationship`. It does
not replace the methodology primary class.

### 7.6 Formal state and screening disposition

Formal states are `REJECT`, `MONITOR`, `INVESTIGATE`, and `ADVANCE`.
`screening_disposition` is separate and is one of `CANDIDATE`,
`NO_CANDIDATE`, or `SCREENED_OUT`.

For an admitted deep-resolution case with at least one candidate trigger,
`screening_disposition` remains `CANDIDATE`, including a case that ultimately
reaches REJECT. If no candidate trigger fires, the deep selector uses the
same `NO_CANDIDATE` disposition as screening and leaves formal state null.
The separate screening helper used by S13 emits `SCREENED_OUT` when an
evidenced screen exclusion applies; it does not assign a formal deep state.

Deep state selection is ordered:

1. a satisfied hard exclusion yields REJECT route 0 with
   `decision_reason_code` `HARD_EXCLUSION_SATISFIED`;
2. another satisfied evidenced rejection condition yields REJECT route 0 with
   its typed reason code (`FALSE_OR_MEASUREMENT_GAP`,
   `EQUIVALENT_QUALIFIED_SUPPLY`, `UNECONOMIC_AT_EFFICIENT_SCALE`,
   `STRUCTURAL_OVERCAPACITY`, or `GENERIC_CAPACITY_CONTRADICTED`);
3. a selected route greater than 0 with all ADVANCE gates passing and at
   least one fired FULL configuration-permitted candidate signal yields
   ADVANCE with `decision_reason_code` `ALL_ADVANCE_GATES_PASS`;
4. a selected route greater than 0 with all ADVANCE gates passing but no
   fired FULL configuration-permitted candidate signal yields INVESTIGATE
   with null `route_code` and `decision_reason_code`
   `ADVANCE_SUPPORT_SIGNAL_DEGRADED`;
5. an unresolved or contradictory decision-critical fact with positive
   decision value yields INVESTIGATE with null `route_code` and
   `decision_reason_code` `ROUTE_CHANGING_EVIDENCE_UNRESOLVED`;
6. when no rejection condition exists, at least one candidate signal exists,
   no material trigger exists, and a named observable future trigger exists,
   the state is MONITOR route 0 with `decision_reason_code`
   `NAMED_TRIGGER_MONITOR`;
7. when material triggers exist but no determinable passing route exists,
   the state is INVESTIGATE with null `route_code` and
   `decision_reason_code` `ROUTE_DETERMINATION_UNRESOLVED`; and
8. an admitted deep case with no fired candidate signal yields the screening disposition `NO_CANDIDATE` with null formal state, null route and
   `decision_reason_code` `NO_TRIGGER_FIRED`. Any other unmatched residual
   fails closed with a decision-integrity error rather than being silently
   called REJECT or MONITOR.

Registered public `decision_reason_code` values are:
`HARD_EXCLUSION_SATISFIED`, `FALSE_OR_MEASUREMENT_GAP`,
`EQUIVALENT_QUALIFIED_SUPPLY`, `UNECONOMIC_AT_EFFICIENT_SCALE`,
`STRUCTURAL_OVERCAPACITY`, `GENERIC_CAPACITY_CONTRADICTED`,
`ALL_ADVANCE_GATES_PASS`, `ADVANCE_SUPPORT_SIGNAL_DEGRADED`,
`ROUTE_CHANGING_EVIDENCE_UNRESOLVED`, `NAMED_TRIGGER_MONITOR`, and
`ROUTE_DETERMINATION_UNRESOLVED`, and `NO_TRIGGER_FIRED`.

MONITOR always names one of demand, regulation, technology, supplier
concentration, or capacity state as an observable trigger.

### 7.7 Route hypotheses and selection

The engine emits exactly nine ordered records, route codes 0 through 8. Each
record has `status` (`passes`, `fails`, or `NOT_CALCULABLE`), feasibility,
constraint-resolution, additionality, policy, economics, national value,
competition, evidence IDs, reason codes, and any lower-route blocker.

A lower-cost route that passes and fully resolves the binding constraint
blocks escalation to every more interventionist route. Passing route 0 with
basis `MONITOR_NO_IMMEDIATE_ACTION` blocks higher routes exactly as
`EVIDENCED_NO_INTERVENTION` does. Financial support is not evaluated as
selectable until unsupported and applicable non-financial routes fail.

Among the remaining feasible, additional, policy-permissible routes with
defensible economics and national value, select the greatest unrounded
incremental national value. An exact tie selects the lower route code. This
tie rule preserves the mandatory lower-intervention ordering and does not
replace the maximum-value comparison.

When economics is unavailable, the engine may emit a
`preferred_hypothesis` from evidenced gap/capability logic, but `route_code`
remains null unless a REJECT/MONITOR route 0 or an ADVANCE route is formally
selected.

Route 7 additionally requires D* > the configured major-line/JV maximum,
demand at least minimum efficient scale, and passing competition controls.
Route 8 returns `NOT_CALCULABLE` with reason `GRAPH_REQUIRED` when no
governed branch-qualified graph input exists. An evaluated record requires a
non-derived shared enabler, declared scenario membership and explicit positive
dependent valuations. Only aligned dependents with probability > 0, dependency
share > 0 and value > 0 count toward the configured minimum and UnlockValue;
zero-weight rows remain explicit exclusions in the audit. Full constraint
resolution requires both the declaration's removal boolean and membership of
the actual detected constraint in its addressed classes. An absent or valid
mismatched detected class produces `PARTIAL_RESOLUTION`. Positive UnlockValue
and passing feasibility, additionality, policy and competition components
remain required. Snapshot or ungoverned in-memory substitutes are forbidden.

### 7.8 Golden public outcomes

For the frozen steel snapshot, decision-critical demand and hard gates remain
unresolved; the state is INVESTIGATE, `route_code` is null, and route 5 is the
preferred brownfield hypothesis. For the frozen polypropylene snapshot, the
computed generic-capacity rejection condition is satisfied; the state is
REJECT and route 0 is selected. Both results are computed, not read from
data.

S14b adds five derived public cases. Each computes INVESTIGATE with null route
because decision-critical target-specification demand and capability remain
unresolved:

| Opportunity | Fired rules |
|---|---|
| `SAU-H6-721061` | R0, R1-D, R3, R10, R12 |
| `SAU-H6-721012` | R0, R1-D, R2, R4-D, R12 |
| `SAU-H6-760711` | R0, R1-D, R2, R12 |
| `SAU-H6-760429` | R0, R1-D, R2, R3, R4-D, R5, R9-S, R10, R12 |
| `SAU-H6-392010` | R0, R1-D, R2, R4-D, R12 |

MONITOR is UNDEMONSTRATED by these governed cases. Route 0 can use
`MONITOR_NO_IMMEDIATE_ACTION` only when a named monitor trigger exists, at
least one signal fires, and `material_trigger_rule_ids(rules)` is empty.
Every S14b public case fires material R1-D, so that computation is false; no
value, threshold or result is changed to manufacture MONITOR. The generalized
MONITOR branch remains proved by the S09/S10 fixtures.

### 7.9 Simulation branch

S10 generalizes simulation selection on scenario contract 2.0.0 through
`simulation.simulate` → `simulation.compute_simulated_decision`, reusing the
public selector on a projected composite case from
`scenario_contract.project_simulated_case`.

Advance gating uses basis `CLASS_IF_CONFIRMED`: declared confirmed classes may
unlock simulated ADVANCE while actual synthetic assessments remain Class D.
Route evaluation adds `PARTIAL_RESOLUTION`, `CONSTRAINT_CLASS_NOT_APPLICABLE`,
`CAPABILITY_BAND_FAILED`, and `FEASIBILITY_FAILED` reason codes. Route 8 retains
`GRAPH_REQUIRED` without a feed and otherwise participates in the same lower-route
precedence and maximum-unrounded-national-value selection. An evaluated record
may truthfully retain `PARTIAL_RESOLUTION` alongside `LOWER_ROUTE_FULLY_RESOLVES`
when the detected class is absent or mismatched and a lower route also blocks
escalation. A 2.1.0 declaration without its matching graph feed is an integrity
error.

Packaged steel still reaches ADVANCE route 5 with frozen public goldens
unchanged. Packaged polypropylene still reaches REJECT route 0 with
`HARD_EXCLUSION_SATISFIED` when the idle-capacity exclusion is satisfied.
Simulated R5/R8 ledger rows follow configured thresholds with FULL/DEGRADED/
DISABLED execution states.

Aggregate EVSI is calculated only when the `synthetic_inputs.evsi` key is
supplied. True omission skips `approximate_evsi` and returns `evsi: null` while
ordinary state and route selection continues. Key presence controls this branch:
supplied null, wrong-type, empty, partial and non-convertible blocks retain their
existing evidence-integrity failures, and complete supplied mappings retain the
existing formula, rounding, positive flag and optional `next_fact`. A legitimate
calculated zero remains a mapping and is never represented as null.

The five S14b Class-D scenarios are reconciled to their public marginals and
reach planted ground truth only through the same computed selector:

| Scenario | Computed state / route | Binding result |
|---|---|---|
| `SYN-MINISTRY-GALVALUME-001` | ADVANCE / 3 | certification and customer qualification |
| `SYN-MINISTRY-TINPLATE-001` | ADVANCE / 7 | targeted greenfield after lower routes fail |
| `SYN-MINISTRY-ALU-FOIL-001` | ADVANCE / 6 | technology licensing / specialist line / JV |
| `SYN-MINISTRY-ALU-PROFILES-001` | ADVANCE / 4 | conditional offtake with zero financial support |
| `SYN-MINISTRY-PE-FILM-001` | REJECT / 0 | equivalent qualified availability exceeds demand |

The four S15b Class-D scenarios use the same selector and deliberately omit
aggregate EVSI because no estimates were supplied:

| Scenario | Computed state / route | Binding result |
|---|---|---|
| `SYN-MINISTRY-PENICILLIN-API-001` | ADVANCE / 1 | incumbent standard-product route |
| `SYN-MINISTRY-STREPTOMYCIN-API-001` | REJECT / 0 | EX-03 unsatisfiable hard gate |
| `SYN-MINISTRY-SOP-001` | ADVANCE / 2 | domestic process route |
| `SYN-MINISTRY-FERT-RETAIL-PACKS-001` | REJECT / 0 | EX-01 heterogeneous residual |

Gate B compares each computed state and route with its declared ground truth.
Synthetic evidence remains Class D, changes only `simulation_decision` and
`active_decision` in simulated mode, and never changes `real_decision`.

## 8. Conditions and kill conditions

Every formal decision emits conditions, kill conditions, and evidence needs
from controlled reason codes rendered through
`config/decision_narratives.v1.yaml`.

No condition or kill condition is copied from PublicSnapshot 2.1.0. A hard
exclusion uses its exclusion-specific rejection rationale. INVESTIGATE names
the route-changing fact. MONITOR names the observable future trigger.
ADVANCE names continuation conditions and a gate-failure kill condition.

REJECT branches render through `REJECTION_NARRATIVE_KEYS`: each producible
REJECT reason code maps to governed headline, route, rationale, condition and
kill keys (`decision.public.reject_uneconomic.*`,
`decision.public.reject_false_gap.*`,
`decision.public.reject_overcapacity.*`, plus the existing generic,
equivalence and exclusion keys). An unregistered REJECT reason code raises a
decision-integrity error.

INVESTIGATE selects route label and rationale by preferred hypothesis:
when `preferred_hypothesis` is null or `preferred.route_code` is 0, the
engine uses `decision.public.investigate.route.unresolved` and
`decision.public.investigate.rationale.route_unresolved`; when
`preferred.selection_basis` is `EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE`
and `preferred.route_code` is the brownfield route code, the engine uses
the legacy brownfield route label and
`decision.public.investigate.rationale`; otherwise the engine uses
`route.hypothesis.priority` with
`decision.public.investigate.rationale.preferred`.

The packaged steel simulation retains customer acceptance, 50 kt within 18
months, milestone/sunset/clawback conditions, and the existing 72 kt,
incumbent-expansion, and customer-qualification kill conditions. The
packaged polypropylene simulation retains its equivalent-capacity no-support
condition and kill condition.

The public decision compatibility fields remain English, with the approved
predicate-driven evidence-need wording changes. The public decision also
carries a bilingual structured narrative and
`narrative_version`. Presentation code escapes every literal and placeholder
value. Only engine-computed placeholder segments receive LTR source-language
isolation inside an Arabic template; the Arabic template itself is not
wrapped as English source text.

## 9. Threshold enforcement

Implementation code must reference configuration keys. Tests may assert expected initial values, but domain functions shall not contain hidden duplicates of threshold values.

Changing a threshold requires a new version, rationale, sector scope and full regression.

## 10. Error and boundary handling

- malformed PublicSnapshot 2.1.0, unknown support code, unknown sector
  profile, missing configured profile gate, unresolved evidence reference,
  authored outcome, or invalid route-evidence domain → evidence-integrity
  error;
- absent decision-critical support → Class E / `MISSING`;
- contradictory covering passport not confirmed by the responsible authority
  → `CONTRADICTORY` and ADVANCE blocked;
- unknown hard-exclusion input → `NOT_CALCULABLE`, never reject;
- zero or multiple primary gap classes → decision-integrity error;
- MONITOR without a named allowed trigger → decision-integrity error;
- unavailable required route input → `NOT_CALCULABLE`;
- route 8 without a governed branch-qualified feed → `NOT_CALCULABLE` / `GRAPH_REQUIRED`; malformed, mismatched or declaration-less feeds fail closed;
- unknown profile → fail closed;
- malformed narrative catalogue, locale-key mismatch, placeholder mismatch,
  or unescaped rendering attempt → narrative-integrity error;
- non-boolean `may_support_advance` → evidence-integrity error;
- unregistered REJECT reason code → decision-integrity error;
- the existing formula and scenario-integrity errors remain unchanged.

## 11. Determinism and independence

Given identical snapshots, configuration, code, and as-of date, the ordered
field assessments, exclusions, gap classes, rejection conditions, route
hypotheses, preferred hypothesis, state, conditions, kill conditions, and
bilingual narratives are byte-stable apart from JSON object ordering.

No gate or selector may contain an opportunity ID, source name, producer name,
`source` branch, or `synthetic_flag` branch. Tests inspect the relevant ASTs.
The public selector consumes evidence semantics, never source type.

## 12. S13a screening-grain execution

The screening engine projects acquired universe rows into the existing rule
input shape and calls the governed R1-D, R2, R3, R4-D, R5, R9-S, R10 and R11
builders with versioned thresholds. R0 is FULL only with a valid tariff-tree
mapping, DEGRADED when the tree is unavailable, and DISABLED for malformed
identity. R1-F is disabled across missing years. R4-F, R6, R7, R8 and R12 are
recorded `INPUTS_NOT_PUBLIC_AT_SCREENING_GRAIN`.

The engine assigns a typed screening disposition and optional **indicated**
state, never a formal decision. R3-only candidates may indicate MONITOR only
with the named `supplier_concentration` trigger. Material triggers indicate
INVESTIGATE; satisfied exclusions or FULL-fired R11 indicate REJECT. Unknown
capability does not improve adjacency and no screening record emits D* or
ADVANCE.
