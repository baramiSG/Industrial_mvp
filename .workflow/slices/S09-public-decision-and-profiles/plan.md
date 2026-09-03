# S09 — Generalized Public Decision Engine and Five Sector Profiles Implementation Plan

> **For agentic workers:** Execute this plan test-first and remain uncommitted. The Supervisor alone may approve, stage, commit, push, open or merge the PR. Use the test-driven-development and verification-before-completion disciplines at every task boundary.

**Goal:** Compute the public decision, screening disposition, evidence-class gate, hard exclusions, gap class, route hypotheses, preferred hypothesis, missing facts, kill conditions, and bilingual decision narrative for any conforming PublicSnapshot 2.1.0 while preserving both public goldens and both packaged simulations exactly. **[SPECIFIED]**

**Architecture:** Keep evidence assessment, state selection, route evaluation, evidence needs, and narrative rendering as focused pure-function modules. `decision_engine.py` orchestrates those modules; snapshots contain typed facts and provenance but no state, route, rule, narrative, missing-fact, or kill-condition outcome. Route alternatives are evaluated in order 0→8, lower-route resolution blocks escalation, and final selection uses maximum defensible incremental national value rather than first-pass selection. **[SPECIFIED]**

**Tech stack:** Python 3.12/3.14, FastAPI, PyYAML, pytest, browser-independent domain functions, named-export ES modules, Playwright Chromium, and the existing governed visual-baseline harness. No new dependency is required. **[DERIVED]**

**Data classification:** `confidential_demo`; frozen public evidence and isolated Class-D synthetic scenarios only. Never read `.env`, print a secret, or add restricted data. **[SPECIFIED]**

---

## 1. Role, baseline, and slice boundary

The planning persona is **Principal Decision-Engine Architect for evidence-governed industrial policy**, adopted after reading the governing documents, slice contract, implementation, tests, and current data. **[VERIFIED]**

Read-only baseline established on 2026-09-02:

- Branch: `slice/S09-public-decision-and-profiles`. **[VERIFIED]**
- HEAD/base: `8b6d55cc8f1f10b828f3af7a6a1e045364cb5537`. **[VERIFIED]**
- Existing suite: `PYTHONPATH=src .venv/bin/python -m pytest -q` → `506 passed, 1 warning in 2.60s`. **[VERIFIED]**
- The warning is the existing Starlette `httpx` deprecation emitted from the installed environment; this slice does not add or suppress it. **[VERIFIED]**
- Current production selector copies `public_decision_contract`, returning PP `REJECT` when computed R11 fires and steel `INVESTIGATE` otherwise; `MONITOR`, public `ADVANCE`, taxonomy, exclusions, and route selection are not executed. **[VERIFIED]**
- Current `evidence_policy.v1.yaml` 1.2.0 names the four ADVANCE-gate fields but no source code executes that block. **[VERIFIED]**

Pre-existing paths belong to the Supervisor and are never edited, reverted, staged, or included in a candidate-identity claim by the Implementer:

```text
.workflow/state.json
docs/BUILD_PROGRESS.md
docs/KNOWN_LIMITATIONS.md
docs/REQUIREMENTS_TRACEABILITY.md
.workflow/runs/demo_start.sh
.workflow/runs/s05_release_merge_tag.sh
.workflow/slices/S08-snapshot-v2-computed-rules/completion.md
.workflow/slices/S08-snapshot-v2-computed-rules/pr_record.md
.workflow/slices/S09-public-decision-and-profiles/persona.md
.workflow/slices/S09-public-decision-and-profiles/context.md
```

The first eight paths are pre-existing modified/untracked S08 or helper-script state; the S09 directory already contains Supervisor-authored `persona.md` and `context.md`. Only this `plan.md` is planner-authored. **[VERIFIED]**

## 2. Governing requirements and non-negotiable outcomes

This plan implements:

- `SLICE_GRAPH.md` S09 and gaps C1, C2, C4-public, C5-public, C8, D1, D3, and D9-public. **[SPECIFIED]**
- Owner interpretations I1 amended, I5 amended, I6, and I7, plus rulings R-1 and R-2 from `GAP_ANALYSIS.md` §7/§7A and ADR-010. **[SPECIFIED]**
- Methodology §§1.2, 2.1, 4.2, 5.3, 6.3–6.6, 7.1–7.5, 8.2, 9, 12–15. **[SPECIFIED]**
- Core 01 FR-030..FR-054, Core 02 §§4–9, Core 04 schema evolution, Core 06 §9, Core 07 §§4–8/10–11, and Core 09 gates and anti-gaming rules. **[SPECIFIED]**

Frozen outcomes:

```text
Steel public:       INVESTIGATE, route_code null, preferred hypothesis route 5
Steel simulated:    ADVANCE, route 5, 57.509 kt capacity, 46.491 kt gap,
                    D*=0.2667, NPV=-18, IRR=0.095, S*=18,
                    ΔNV=198, capacity ratio=1.0751
PP public:          REJECT, route 0
PP simulated:       REJECT, route 0, formula capacity=104.49 kt,
                    qualified availability=80 kt, gap=-24 kt, support=0
```

Every listed state, route, and number remains exact. Fired-rule expectations also remain exact: steel R1-D/R2/R3/R4-D/R9-S true and R11 false; PP R1-D/R4-D/R5/R9-S/R11 true, R2 false, and R3/R10 not evaluable. **[SPECIFIED]**

Non-goals are the S10 generalized simulation contract/routes, S13 screening universe, S14/S15 new cases, S16 graph activation, threshold-value changes, methodology DOCX changes, and any new dependency. **[SPECIFIED]**

## 3. Core v2 normative text — write before implementation

The Implementer first edits the Core documents and adds exact integrity-contract assertions for this wording. Existing `core_version: 2.0.0` markers remain exactly once per document; no 2.1 marker and no duplicate marker is added. **[SPECIFIED]**

### 3.1 Exact replacement text for Core 07 §§4–8, §10, and §11

Replace Core 07 §§4–8 and §§10–11 with the following normative text. Preserve §§1–3 and §9 except for cross-reference corrections required by the new subsection numbers. **[PROPOSED]**

```markdown
## 4. Capability engine

### 4.1 Effective capacity

`Qeffective = Nameplate × Availability × Yield × Qualification share × Market allocation`.
All factors are within `[0,1]`. A public nameplate without the other factors
does not establish effective qualified supply.

### 4.2 Dimension states

Capability states are `0`, `1`, `2`, `3`, and `U` with the meanings fixed by
methodology §6.4. `U` is unknown evidence, never zero distance.

### 4.3 K, U and D*

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

For an admitted deep-resolution case, `screening_disposition` remains
`CANDIDATE`, including a case that ultimately reaches REJECT. The separate
screening helper used by S13 emits `NO_CANDIDATE` when no candidate trigger
exists and `SCREENED_OUT` when an evidenced screen exclusion applies; it
does not assign a formal deep state.

Deep state selection is ordered:

1. a satisfied hard exclusion yields REJECT route 0;
2. another satisfied evidenced rejection condition yields REJECT route 0;
3. a selected route greater than 0 with all ADVANCE gates passing yields
   ADVANCE and that route code;
4. an unresolved or contradictory decision-critical fact with positive
   decision value yields INVESTIGATE and null `route_code`;
5. when no rejection condition exists, at least one signal exists, the
   material trigger is absent, and a named observable future trigger exists,
   the state is MONITOR route 0; and
6. an admitted deep case that satisfies none of these branches fails closed
   with a decision-integrity error rather than being silently called REJECT or
   MONITOR.

MONITOR always names one of demand, regulation, technology, supplier
concentration, or capacity state as an observable trigger.

### 7.7 Route hypotheses and selection

The engine emits exactly nine ordered records, route codes 0 through 8. Each
record has `status` (`passes`, `fails`, or `NOT_CALCULABLE`), feasibility,
constraint-resolution, additionality, policy, economics, national value,
competition, evidence IDs, reason codes, and any lower-route blocker.

A lower-cost route that passes and fully resolves the binding constraint
blocks escalation to every more interventionist route. Financial support is
not evaluated as selectable until unsupported and applicable non-financial
routes fail.

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
Route 8 always returns `NOT_CALCULABLE` with reason `GRAPH_REQUIRED` until
S16 supplies a graph-identified shared enabler and positive UnlockValue from
the governed Neo4j projection. Snapshot or in-memory substitutes are
forbidden.

### 7.8 Golden public outcomes

For the frozen steel snapshot, decision-critical demand and hard gates remain
unresolved; the state is INVESTIGATE, `route_code` is null, and route 5 is the
preferred brownfield hypothesis. For the frozen polypropylene snapshot, the
computed generic-capacity rejection condition is satisfied; the state is
REJECT and route 0 is selected. Both results are computed, not read from
data.

### 7.9 Simulation branch

S09 does not generalize simulation selection. `_simulate` retains its S08
state/route logic and exact numeric outputs.

The packaged steel simulation continues to require a positive
specification-adjusted gap, publishable D*, D* within the configured
incremental-upgrade band, passing minimum-support economics, positive
incremental national value, and no competition warning before selecting
ADVANCE route 5. The packaged polypropylene simulation continues to select
REJECT route 0 when equivalent qualified availability is at least target
demand.

S09 does not localize or replace simulation narratives. After `_simulate`
returns, `analyze_simulated` continues to render the selected state entry from
the scenario's existing `decision_narrative` exactly as today. In locale `ar`,
those English fields remain explicit source-language islands. This
presentation must not participate in simulation state, route selection, or
ground-truth back-testing. S10 owns bilingual scenario narratives,
class-if-confirmed gating, and generalized routes 0–7 in scenario contract
2.0.0.

## 8. Conditions and kill conditions

Every formal decision emits conditions, kill conditions, and evidence needs
from controlled reason codes rendered through
`config/decision_narratives.v1.yaml`.

No condition or kill condition is copied from PublicSnapshot 2.1.0. A hard
exclusion uses its exclusion-specific rejection rationale. INVESTIGATE names
the route-changing fact. MONITOR names the observable future trigger.
ADVANCE names continuation conditions and a gate-failure kill condition.

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
- route 8 before graph activation → `NOT_CALCULABLE` / `GRAPH_REQUIRED`;
- unknown profile → fail closed;
- malformed narrative catalogue, locale-key mismatch, placeholder mismatch,
  or unescaped rendering attempt → narrative-integrity error;
- the existing formula and scenario-integrity errors remain unchanged.

## 11. Determinism and independence

Given identical snapshots, configuration, code, and as-of date, the ordered
field assessments, exclusions, gap classes, rejection conditions, route
hypotheses, preferred hypothesis, state, conditions, kill conditions, and
bilingual narratives are byte-stable apart from JSON object ordering.

No gate or selector may contain an opportunity ID, source name, producer name,
`source` branch, or `synthetic_flag` branch. Tests inspect the relevant ASTs.
The public selector consumes evidence semantics, never source type.
```

### 3.2 Exact Core 01 additions

Append these requirements without changing existing IDs or wording. **[PROPOSED]**

```markdown
- **FR-035** The engine shall load all five methodology §6.3 sector profiles,
  require weights that sum to 1.0, require each configured hard gate, and fail
  closed on an unknown profile.
- **FR-036** Public capability shall distinguish configured profile hard gates
  from decision-specific gates; either unresolved set shall withhold D* and a
  route band.
- **FR-037** The public engine shall assess product identity,
  target-specification demand, domestic supply/capability, and hard
  regulatory/process gates from covering evidence passports.
- **FR-038** The ADVANCE gate shall use configured blocked evidence classes
  and resolution statuses and shall not branch on evidence source type.
- **FR-039** The engine shall execute all six typed methodology §4.2 hard
  exclusions and emit exactly one primary methodology §5.3 gap class.
- **FR-046** The public branch shall emit ordered route hypotheses 0–8 with
  pass, fail, or NOT_CALCULABLE status and evidence-backed reasons.
- **FR-047** A fully resolving lower route shall block escalation; otherwise
  the engine shall select maximum defensible incremental national value among
  feasible, additional, permissible alternatives.
- **FR-048** Route 8 shall remain NOT_CALCULABLE with GRAPH_REQUIRED until a
  governed dependency graph supplies the shared-enabler calculation.
- **FR-049** Missing facts, conditions, kill conditions, and decision
  narratives shall be computed and rendered from a versioned bilingual
  catalogue rather than authored in a public snapshot.
```

In Core 01 §4.1, replace “stop at `INVESTIGATE` when decision-critical evidence is unavailable” with “stop at `INVESTIGATE` when route-changing decision-critical evidence is unavailable; permit `ADVANCE` when actual A/B/C evidence and every methodology gate pass.” Preserve §4.2 simulation wording. **[SPECIFIED]**

### 3.3 Exact Core 02 mapping additions

Update the section and domain-behaviour tables with these rows. **[PROPOSED]**

```markdown
| 2.1 / 12 — Decision-critical evidence gate | Four field assessments from controlled passport support codes; configured class/status gate; no source-type predicate | `public_decision.assess_decision_critical_fields`, `evidence.evaluate_advance_gate`, `evidence_policy.v1.yaml` | field-class, source-independence, positive/downgrade ADVANCE tests | evidence assessment and gate diagnostics |
| 4.2 — Hard exclusions | Six typed checks; unknown is NOT_CALCULABLE; satisfied exclusion rejects before deep routes | `public_decision.evaluate_hard_exclusions` | six-check truth tables and unknown tests | hard-exclusion diagnostics |
| 5.3 — Gap taxonomy | Exactly one primary methodology class and ordered secondary classes | `public_decision.classify_gap` | taxonomy table tests | gap class |
| 7.1.1 / 7.4 / 12 — Public routes | Ordered 0–8 hypotheses; precedence then maximum defensible ΔNV; route 8 GRAPH_REQUIRED | `route_hypotheses.py` | order, precedence, max-ΔNV, tie and graph tests | route hypotheses and preferred hypothesis |
| 6.3 — Five sector profiles | Five frozen profiles, nine weights each, complete profile hard gates | `capability.py`, `sector_profiles.v1.yaml` | per-profile weight/Kmin/band/gate tests | capability matrix |
| 9 / 15 — Evidence needs and narrative | Computed evidence needs, conditions, kill conditions and governed EN/AR narrative | `evidence_needs.py`, `narratives.py`, `decision_narratives.v1.yaml` | exact golden copy, parity, escaping and browser tests | hero, unlocks, dossier |
```

Change the route map’s route-8 MVP use to “contract emitted as `GRAPH_REQUIRED`; graph activation deferred to S16.” Change the decision-state map so real public ADVANCE is allowed by evidence and methodology gates, MONITOR requires a named trigger, and screening dispositions are not formal states. **[SPECIFIED]**

### 3.4 Required Core 04 PublicSnapshot 2.1.0 edit

Core 04 currently says `public_decision_contract` is temporarily retained for S09. A 2.1.0 schema removal without changing Core 04 would leave rank-2 authority contradicting the implementation, so this minimal Core 04 edit is mandatory even though the short S09 authority list emphasizes Core 01/02/07/09. **[DERIVED]**

Replace the PublicSnapshot v2 paragraph with:

```markdown
### PublicSnapshot 2.1

A live public snapshot sets `schema_version: "2.1.0"`. The two frozen golden
files retain their snapshot IDs, as-of dates, and historical-v1 `supersedes`
links. A new snapshot with no predecessor may set `supersedes:
"UNAVAILABLE"`; an evidence refresh still follows Authority Manifest §7.5.

Evidence passports use the controlled support-code vocabulary defined by
Core 07 §7.2. Free-text support claims are invalid. `domestic_capability`
contains all configured `profile_hard_gates` with typed status and evidence
references, plus decision-specific unresolved gates.

`hard_exclusion_inputs` carries the six typed methodology §4.2 input blocks.
`decision_inputs` may carry target-specification demand, specification
equivalence, route evidence for routes 1–7, and a named monitor trigger.
Missing facts remain exact `UNAVAILABLE`.

The snapshot contains no `public_decision_contract`, authored state, route,
screening disposition, gap class, rule result, route-hypothesis result,
narrative, missing-fact list, condition, or kill-condition list. All are
computed.
```

Update §2.10 and §3 response examples additively for `screening_disposition`, `gap_class`, `evidence_class_assessment`, `hard_exclusions`, `route_hypotheses`, `preferred_hypothesis`, and `narrative_version`. **[PROPOSED]**

### 3.5 Exact Core 09 proof additions

Append this section after the existing schema-migration proof. **[PROPOSED]**

```markdown
### Public decision generalization proof

Tests use synthetic-free PublicSnapshot 2.1 fixtures under `tests/fixtures/`;
they never add demonstration data. One fixture with resolved A/B/C
decision-critical evidence and every route/economics/policy gate passing must
reach real ADVANCE. Downgrading each critical field independently to D and E
must block ADVANCE.

The proof covers all six hard exclusions, unknown exclusion inputs, exactly
one primary gap class, MONITOR with a named trigger, screening dispositions,
evidenced REJECT conditions, route order 0–8, lower-route precedence,
maximum-ΔNV selection, lower-route tie resolution, and route 8
GRAPH_REQUIRED.

An AST contract fails if gate or selector functions reference `source`,
`synthetic_flag`, producer names, opportunity IDs, or scenario IDs.

The two public goldens retain their states, routes, fired rules, and all
English compatibility narrative fields except the ten legacy missing-fact
sentences, whose substance remains five needs per golden under generic
predicate-selected wording. Both packaged simulation narratives, outcomes,
and exact numeric values remain unchanged. Public EN/AR catalogue keys and
placeholders have exact parity, and browser tests prove that Arabic public
decision narratives are Arabic text rather than English source-language
islands. Simulation narrative fields remain English source-language islands
in locale `ar` until S10.
```

Update Gate C to include taxonomy, hard exclusions, and state selection; Gate D to include five profiles and complete profile gates; Gate E to include route-hypothesis order/precedence/max-ΔNV; Gate G to include localized decision narratives. **[PROPOSED]**

## 4. Module architecture and data flow

### 4.1 New focused modules

Create:

1. `src/ior_mvp/public_decision.py` — controlled field assessment, hard exclusions, rejection conditions, gap taxonomy, state table, and one `compute_public_decision` orchestrator. It contains no opportunity IDs, source-name predicates, or synthetic predicates. **[PROPOSED]**
2. `src/ior_mvp/route_hypotheses.py` — ordered route records, route-evidence calculations, precedence, maximum-ΔNV selection, tie handling, route-7 gate, and route-8 `GRAPH_REQUIRED`. **[PROPOSED]**
3. `src/ior_mvp/evidence_needs.py` — controlled evidence-need codes, deterministic coalescing/order, and condition/kill reason-code derivation. **[PROPOSED]**
4. `src/ior_mvp/narratives.py` — fail-closed catalogue loader, key/locale/placeholder validation, safe structured interpolation, and compatibility-English projection. **[PROPOSED]**

All public functions receive type hints. No bare `except` is introduced. Pure functions take explicit dictionaries/config objects, return new values, and do not mutate snapshots or cached repository objects. **[SPECIFIED]**

### 4.2 Orchestration

`analyze_public` becomes:

```text
load/deep-copy and validate snapshot
validate every public passport is non-synthetic
evaluate evidence-derived R0–R12
evaluate capability using dimensions + profile/decision-specific hard gates
assess decision-critical fields
evaluate configured ADVANCE gate
evaluate six hard exclusions
classify one primary gap and secondary classes
derive rejection conditions and evidence needs
evaluate route hypotheses 0→8
select preferred hypothesis
select formal state from the ordered table
render bilingual narrative and English compatibility fields
return existing response plus additive diagnostics
```

`rules.evaluate_rules` constructs R0–R11 first, calls the shared evidence-need resolver with the case and those preliminary rows, and then appends R12. The public selector reuses the exact controlled needs carried by R12; it does not run a second divergent missing-fact algorithm. Route-economics needs are inferred from typed `decision_inputs.route_evidence` plus the preliminary R9-S/R11 rows, so the resolver does not depend on a selected state. **[PROPOSED]**

`_simulate` remains unchanged. `analyze_simulated` receives the computed
public result as today and preserves the scenario-authored English
`decision_narrative` selected by `_simulate`; locale `ar` wraps those fields
as source-language islands rather than attaching catalogue translations. No
narrative field participates in `_simulate` selection or ground-truth
back-testing. **[SPECIFIED]**

### 4.3 Key interfaces

```text
assess_decision_critical_fields(
  case: dict[str, Any],
  capability: dict[str, Any]
) -> dict[str, dict[str, Any]]

evaluate_advance_gate(
  assessments: dict[str, dict[str, Any]],
  advance_policy: dict[str, Any]
) -> dict[str, Any]

evaluate_hard_exclusions(
  case: dict[str, Any]
) -> list[dict[str, Any]]

classify_gap(
  case: dict[str, Any],
  rules: list[dict[str, Any]],
  assessments: dict[str, dict[str, Any]],
  exclusions: list[dict[str, Any]]
) -> dict[str, Any]

evaluate_route_hypotheses(
  case: dict[str, Any],
  rules: list[dict[str, Any]],
  capability: dict[str, Any],
  gap_class: dict[str, Any],
  rejection_conditions: list[dict[str, Any]]
) -> list[dict[str, Any]]

select_preferred_hypothesis(
  hypotheses: list[dict[str, Any]]
) -> dict[str, Any] | None

compute_public_decision(
  case: dict[str, Any],
  rules: list[dict[str, Any]],
  capability: dict[str, Any]
) -> dict[str, Any]

derive_evidence_needs(
  case: dict[str, Any],
  preliminary_rules: list[dict[str, Any]]
) -> list[dict[str, Any]]

render_catalogue_entry(
  key: str,
  locale: str,
  values: dict[str, NarrativeValue] | None = None
) -> dict[str, Any]
```

`NarrativeValue` distinguishes `localized` values from `computed` values. Rendered output is `{text, segments}`; every segment is plain text, and presentation code performs HTML escaping. **[PROPOSED]**

## 5. File plan

### 5.1 Create

- `src/ior_mvp/public_decision.py`
- `src/ior_mvp/route_hypotheses.py`
- `src/ior_mvp/evidence_needs.py`
- `src/ior_mvp/narratives.py`
- `config/decision_narratives.v1.yaml`
- `tests/test_decision_evidence.py`
- `tests/test_hard_exclusions.py`
- `tests/test_gap_taxonomy.py`
- `tests/test_public_decision.py`
- `tests/test_route_hypotheses.py`
- `tests/test_decision_narratives.py`
- `tests/test_sector_profiles.py`
- `tests/test_genui_decision_contract.py`
- `tests/fixtures/public_decision/advance-route-3.json`
- `tests/fixtures/public_decision/monitor-r3-only.json`
- `tests/fixtures/public_decision/reject-hard-exclusion.json`
- `tests/fixtures/public_decision/reject-equivalence.json`

These fixtures are public-shaped, `synthetic_flag=false`, test-only records and are not added to `data/`, project golden lists, or snapshot manifests. **[SPECIFIED]**

### 5.2 Modify production and presentation

- `src/ior_mvp/decision_engine.py`
- `src/ior_mvp/evidence.py`
- `src/ior_mvp/public_snapshot.py`
- `src/ior_mvp/rules.py`
- `src/ior_mvp/capability.py`
- `src/ior_mvp/config.py`
- `src/ior_mvp/genui.py`
- `src/ior_mvp/dossier.py`
- `src/ior_mvp/static/modules/dom.js`
- `src/ior_mvp/static/modules/renderers/decision.js`
- `src/ior_mvp/static/modules/renderers/evidence.js`
- `src/ior_mvp/static/modules/renderers/economics.js`
- `src/ior_mvp/static/modules/renderers/integrity.js` only if the narrative version is displayed; the default plan keeps the version in API/dossier authority JSON and does not add new UI chrome. **[PROPOSED]**
- `browser_tests/visual_baselines.py` to include the decision catalogue in source-tree provenance
- `scripts/demo_smoke.py` to assert the computed gap/preferred-hypothesis/narrative fields without changing its existing printed lines

No component exceeds 199 physical lines; if `decision.js`, `evidence.js`, or `dom.js` would cross that boundary, extract a named-export `modules/narrative.js` rather than violating the S07 contract. **[SPECIFIED]**

### 5.3 Modify governed artifacts

- `docs/core/01_PRODUCT_AND_REQUIREMENTS.md`
- `docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md`
- `docs/core/04_CANONICAL_DATA_MODEL.md`
- `docs/core/07_DETERMINISTIC_ENGINE_SPEC.md`
- `docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md`
- `config/evidence_policy.v1.yaml` 1.2.0 → 1.3.0
- `config/sector_profiles.v1.yaml` 1.0.0 → 1.1.0
- `data/snapshots/public/SAU-H0-721049.json` schema 2.0.0 → 2.1.0 in place
- `data/snapshots/public/SAU-H0-390210.json` schema 2.0.0 → 2.1.0 in place
- `scripts/build_manifests.py`
- `docs/authority/00_AUTHORITY_MANIFEST.md` §11 generated-row copy

Core 04 is included because its current temporary-contract sentence must be retired for schema 2.1.0. **[DERIVED]**

### 5.4 Modify tests and migration oracle

- `tests/legacy_snapshot_v1.py`
- `tests/test_snapshot_migration_equivalence.py`
- `tests/test_public_snapshot_schema.py`
- `tests/test_golden_cases.py`
- `tests/test_rules.py`
- `tests/test_threshold_boundaries.py`
- `tests/test_capability_economics.py`
- `tests/test_simulation_fidelity.py`
- `tests/test_synthetic_isolation.py`
- `tests/test_dossier_contract.py`
- `tests/test_api.py`
- `tests/test_integrity_contract.py`
- `tests/test_authority_disclosure.py`
- `tests/test_ui_catalogue.py` only to prove the narrative catalogue is separate and not duplicated
- `tests/test_visual_baseline_contract.py`
- `tests/test_browser_harness_contract.py` only if no new browser test function can absorb the assertions
- `browser_tests/test_journeys.py`
- `browser_tests/test_dossier.py`
- the 40 governed WebPs plus visual manifest/hash through the authorized baseline procedure

### 5.5 Modify delivery documentation after evidence exists

- `docs/ARCHITECTURE_DECISIONS.md` — ADR-013
- `docs/DEVELOPMENT_GUIDE.md`
- `docs/KNOWN_LIMITATIONS.md` — S09 local/provisional KL-20, KL-23-public, KL-24 treatment only
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/BUILD_PROGRESS.md` — append S09 local evidence without overwriting the Supervisor’s S08 lines
- `docs/milestones/v0.3.0/SLICE_GRAPH.md` — route-matrix note only
- `CHANGELOG.md`
- `.workflow/slices/S09-public-decision-and-profiles/implementation_log.md`
- `.workflow/slices/S09-public-decision-and-profiles/test_evidence.md`

The Implementer must not edit `.workflow/state.json`, the S08 records, the two helper scripts, or any Supervisor-owned pre-existing hunk. **[SPECIFIED]**

### 5.6 Explicitly unchanged

`docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx`, `config/thresholds.v1.yaml`, `config/ui_strings.v1.yaml`, `config/project.yaml`, `data/synthetic/**`, `data/golden/**`, historical v1 snapshot bytes, acquisition/graph code, CI dependency files, lockfiles, and package metadata remain unchanged. **[SPECIFIED]**

## 6. PublicSnapshot 2.1.0 contract

### 6.1 Top-level shape

Required keys become:

```text
schema_version, snapshot_id, as_of_date, supersedes, source_boundary,
authority_note, opportunity, trade, trade_quality, domestic_flows,
criticality_designation, domestic_capability, hard_exclusion_inputs,
decision_inputs, evidence
```

Existing optional partner/concentration/dispersion keys remain. `public_decision_contract` is forbidden, as are state, route, screening, gap, narrative, missing-fact, condition, kill-condition, rule, and hypothesis outcome keys at any depth. **[SPECIFIED]**

`supersedes` accepts the existing safe historical-v1 link or exact `UNAVAILABLE`. Both live goldens retain their current safe links; no historical bytes move or change. **[PROPOSED]**

### 6.2 Controlled passport `supports` vocabulary

Free-text `supports` values are replaced with the following exact allow-list:

```text
TRADE_VALUE
TRADE_QUANTITY
SUPPLIER_CONCENTRATION
EXPORT_IMPORT_RATIO
TARGET_PRODUCT_IDENTITY
TARGET_SPECIFICATION_DEMAND
BILINGUAL_SPECIFICATION_EXTRACTION
DOMESTIC_NAMEPLATE_CAPACITY
DOMESTIC_PROCESS_ROUTE
DOMESTIC_PROCESS_FAMILY
DOMESTIC_PRODUCT_PORTFOLIO
DOMESTIC_SPECIFICATION_ENVELOPE
DOMESTIC_DIMENSION_ENVELOPE
DOMESTIC_LABORATORY_METROLOGY
DOMESTIC_CAPABILITY_ASSESSMENT
HARD_REGULATORY_PROCESS_GATES
ROUTE_ECONOMICS
ROUTE_NATIONAL_VALUE
ROUTE_COMPETITION
MONITOR_TRIGGER
```

No free-text fallback is retained: unknown codes fail validation. Human descriptions remain in titles, transformations, and source spans, not in an ungoverned decision map. **[PROPOSED]**

Critical-field mapping:

```text
product_identity
  TARGET_PRODUCT_IDENTITY
  BILINGUAL_SPECIFICATION_EXTRACTION
  DOMESTIC_PRODUCT_PORTFOLIO
  DOMESTIC_SPECIFICATION_ENVELOPE
  DOMESTIC_DIMENSION_ENVELOPE

demand_at_required_specification
  TARGET_SPECIFICATION_DEMAND

domestic_supply_or_capability
  DOMESTIC_NAMEPLATE_CAPACITY
  DOMESTIC_PROCESS_ROUTE
  DOMESTIC_PROCESS_FAMILY
  DOMESTIC_PRODUCT_PORTFOLIO
  DOMESTIC_SPECIFICATION_ENVELOPE
  DOMESTIC_LABORATORY_METROLOGY
  DOMESTIC_CAPABILITY_ASSESSMENT

hard_regulatory_or_process_gate
  DOMESTIC_PROCESS_ROUTE
  DOMESTIC_SPECIFICATION_ENVELOPE
  DOMESTIC_LABORATORY_METROLOGY
  HARD_REGULATORY_PROCESS_GATES
```

Trade-only codes do not improve any decision-critical field. Route-economics codes support route gates, not the four class assessments. **[PROPOSED]**

Exact golden migration:

```text
Steel S-WITS-721049
  trade value                     → TRADE_VALUE
  trade quantity                  → TRADE_QUANTITY
  partner concentration           → SUPPLIER_CONCENTRATION

Steel S-UNICOIL-EPD
  installed capacity              → DOMESTIC_NAMEPLATE_CAPACITY
  process route                   → DOMESTIC_PROCESS_ROUTE
  published specification envelope→ DOMESTIC_SPECIFICATION_ENVELOPE
  laboratory accreditation        → DOMESTIC_LABORATORY_METROLOGY

Steel S-UNICOIL-SPEC
  bilingual specification extraction            → BILINGUAL_SPECIFICATION_EXTRACTION
  published coating and dimension envelope       →
      DOMESTIC_SPECIFICATION_ENVELOPE,
      DOMESTIC_DIMENSION_ENVELOPE

Steel S-HADEED
  additional incumbent process-family evidence   → DOMESTIC_PROCESS_FAMILY

PP P-WITS-390210
  trade value                     → TRADE_VALUE
  trade quantity                  → TRADE_QUANTITY
  export/import ratio             → EXPORT_IMPORT_RATIO

PP P-SABIC
  broad domestic-linked polypropylene family portfolio →
      DOMESTIC_PRODUCT_PORTFOLIO

PP P-ADVANCED
  450,000 t/y nameplate capacity  → DOMESTIC_NAMEPLATE_CAPACITY

PP P-TASNEE
  720,000 t/y Saudi polypropylene capacity →
      DOMESTIC_NAMEPLATE_CAPACITY
```

These substitutions normalize the same stated facts; no evidence class, source, title, value, date, transformation, or contradiction changes. **[DERIVED]**

### 6.3 Profile hard-gate block

Add `domestic_capability.profile_hard_gates`. Its keys must exactly equal the selected profile’s configured hard gates. Each value is:

```json
{
  "status": "RESOLVED | UNAVAILABLE | KNOWN_FAILURE",
  "evidence_ids": []
}
```

`RESOLVED` requires at least one resolvable A/B/C passport; `KNOWN_FAILURE` requires evidence; `UNAVAILABLE` requires an empty evidence list. Existing decision-specific `unresolved_hard_gates` entries advance from `{name,state}` to `{name,state,evidence_ids}`. An `unresolved` entry may have an empty list; a `known_failure` requires at least one resolvable A/B/C passport. The two goldens add empty `evidence_ids` to their three existing unresolved entries without changing the fact. **[PROPOSED]**

For both goldens, every profile hard gate is `UNAVAILABLE` with `evidence_ids: []` because the worked cases do not prove target-specific resolution. This preserves unknown rather than inferring resolution from a broad portfolio. **[DERIVED]**

### 6.4 Hard-exclusion input block

The exact shape is:

```json
{
  "heterogeneous_residual_code": {
    "commercial_product_separable": "UNAVAILABLE",
    "product_level_evidence_available": "UNAVAILABLE",
    "evidence_ids": []
  },
  "downside_market_below_mes": {
    "sustainable_downside_demand_kt": "UNAVAILABLE",
    "minimum_efficient_scale_kt": "UNAVAILABLE",
    "credible_export_contract": "UNAVAILABLE",
    "evidence_ids": []
  },
  "unsatisfiable_hard_gate": {
    "gate_domain": "UNAVAILABLE",
    "gate_satisfiability": "UNAVAILABLE",
    "evidence_ids": []
  },
  "idle_equivalent_domestic_capacity": {
    "domestic_specification_equivalent": "UNAVAILABLE",
    "qualified_idle_capacity_kt": "UNAVAILABLE",
    "target_specification_demand_kt": "UNAVAILABLE",
    "binding_market_failure": "UNAVAILABLE",
    "evidence_ids": []
  },
  "transitory_or_measurement_gap": {
    "dominant_cause": "UNAVAILABLE",
    "evidence_ids": []
  },
  "redundancy_or_crowd_out": {
    "competition_finding": "UNAVAILABLE",
    "evidence_ids": []
  }
}
```

Allowed enums:

```text
gate_domain:
  legal | safety | environmental | ip | customer_qualification | UNAVAILABLE
gate_satisfiability:
  SATISFIABLE | UNSATISFIABLE | UNAVAILABLE
dominant_cause:
  REEXPORT | ONE_OFF_PROJECT | TEMPORARY_PRICE_ARBITRAGE |
  CLASSIFICATION_DISCONTINUITY | OTHER | UNAVAILABLE
competition_finding:
  ACCEPTABLE | UNACCEPTABLE_REDUNDANT_CAPACITY |
  UNACCEPTABLE_CROWD_OUT | UNAVAILABLE
```

Every input in both goldens remains exact `UNAVAILABLE` with no evidence IDs. Methodology §§13–14 do not establish any of the six exclusions as a typed fact; PP’s R11 generic-capacity rejection is a separate computed rejection condition. **[SPECIFIED]**

### 6.5 Decision-input block

The exact shape is:

```json
{
  "target_specification_demand": "UNAVAILABLE",
  "specification_equivalence": "UNAVAILABLE",
  "route_evidence": "UNAVAILABLE",
  "monitor_trigger": "UNAVAILABLE"
}
```

Populated alternatives:

```json
{
  "target_specification_demand": {
    "quantity_kt": 100.0,
    "downside_quantity_kt": 90.0,
    "evidence_ids": ["E-DEMAND"]
  },
  "specification_equivalence": {
    "domestic_product_equivalent": true,
    "qualified_available_kt": 120.0,
    "evidence_ids": ["E-EQUIVALENCE"]
  },
  "route_evidence": [
    {
      "route_code": 3,
      "binding_constraint": "qualification_or_certification",
      "technical_feasibility_confirmed": true,
      "binding_constraint_fully_removed": true,
      "investment_already_approved_or_financed": false,
      "proceeds_without_intervention": false,
      "policy_prohibition_identified": false,
      "distortion_unacceptable": false,
      "intervention_proportionate_to_constraint": true,
      "downside_cash_flows_m_sar": [-10.0, 6.0, 6.0],
      "hurdle_rate": 0.10,
      "national_value": {
        "domestic_value_added": 50.0,
        "exports": 10.0,
        "resilience_value": 5.0,
        "knowledge_skills": 5.0,
        "fiscal_receipts": 5.0,
        "government_cost": 5.0,
        "displacement": 1.0,
        "resource_environment": 1.0,
        "risk_allowance": 2.0
      },
      "competition": {
        "existing_effective_capacity_kt": 100.0,
        "proposed_incremental_capacity_kt": 0.0,
        "downside_demand_kt": 100.0
      },
      "evidence_ids": ["E-ROUTE"]
    }
  ],
  "monitor_trigger": {
    "domain": "capacity_state",
    "condition_code": "qualified_supply_falls_below_target_demand",
    "evidence_ids": ["E-TRIGGER"]
  }
}
```

`route_code` is 1–7 in snapshot route evidence. Code 0 is engine-derived, and code 8 rejects snapshot input because it is graph-owned. Allowed binding constraints are:

```text
specification_or_grade
capacity_or_availability
cost_or_competitiveness
capability_or_technology
qualification_or_certification
commercial_or_relationship
administrative_or_regulatory
information_or_market_linkage
demand_fragmentation_or_offtake
```

Other enum values fail closed. **[PROPOSED]**

Each route finding
`technical_feasibility_confirmed`,
`binding_constraint_fully_removed`,
`investment_already_approved_or_financed`,
`proceeds_without_intervention`,
`policy_prohibition_identified`,
`distortion_unacceptable`, and
`intervention_proportionate_to_constraint`
is boolean or exact `UNAVAILABLE`. The snapshot never supplies the derived
`feasibility`, `additionality`, `policy_permissibility`, route `status`, or
selected route. **[PROPOSED]**

Both goldens use all-`UNAVAILABLE` decision inputs; their state and route logic derives from existing evidence/rules/capability. **[SPECIFIED]**

## 7. Decision-critical evidence assessment and ADVANCE gate

### 7.1 Assessment algorithm

For each configured field:

1. collect passports whose controlled support code maps to the field;
2. absent collection → Class E / `MISSING`;
3. any covering unresolved-status passport → `UNRESOLVED`;
4. any unconfirmed non-null contradiction on a covering passport → `CONTRADICTORY`;
5. otherwise select the strongest class among covering passports using `A < B < C < D < E`;
6. apply the field-specific resolution predicate from Core 07 §7.2;
7. emit sorted support codes and evidence IDs for determinism.

The “strongest covering passport” rule does not scan unrelated evidence; completion predicates prevent a broad Class C portfolio from turning a partial field into `RESOLVED`. **[PROPOSED]**

Expected goldens:

```text
Steel
product_identity                  class C, CONTRADICTORY, S-UNICOIL-SPEC
demand_at_required_specification class E, MISSING
domestic_supply_or_capability     class C, UNRESOLVED
hard_regulatory_or_process_gate  class C, UNRESOLVED

PP
product_identity                  class C, PARTIAL
demand_at_required_specification class E, MISSING
domestic_supply_or_capability     class C, UNRESOLVED
hard_regulatory_or_process_gate  class E, MISSING
```

Steel’s specification contradiction remains visible and blocks resolution; its recorded evidence class remains C. **[SPECIFIED]**

### 7.2 Evidence-policy 1.3.0

Retain classes, statuses, and all synthetic-isolation fields/labels exactly. Change only metadata version/effective date and normalize `advance_gate` to:

```yaml
metadata:
  version: "1.3.0"
  effective_date: "2026-09-02"

advance_gate:
  decision_critical_fields:
    - product_identity
    - demand_at_required_specification
    - domestic_supply_or_capability
    - hard_regulatory_or_process_gate
  blocked_classes:
    - D
    - E
  blocked_resolution_statuses:
    - PARTIAL
    - UNRESOLVED
    - CONTRADICTORY
    - MISSING
  confirmed_reviewer_status: confirmed_by_responsible_authority
```

Rationale for Manifest §7.3: the existing four fields and D/E rule are unchanged; the shape becomes directly executable and adds the SD-1 contradiction/resolution contract without deriving policy from a YAML key name. **[DERIVED]**

### 7.3 Gate output

```json
{
  "passes": false,
  "blocked_classes": ["D", "E"],
  "blocked_resolution_statuses": [
    "PARTIAL", "UNRESOLVED", "CONTRADICTORY", "MISSING"
  ],
  "blocked_fields": [
    {
      "field": "demand_at_required_specification",
      "evidence_class": "E",
      "resolution_status": "MISSING",
      "reasons": ["BLOCKED_CLASS", "BLOCKED_RESOLUTION"]
    }
  ]
}
```

No source metadata is accepted as an argument to `evaluate_advance_gate`. **[SPECIFIED]**

## 8. Six typed hard exclusions

Each function returns the common result shape:

```json
{
  "code": "EX-01_HETEROGENEOUS_RESIDUAL",
  "status": "NOT_CALCULABLE",
  "reason_code": "EXCLUSION_INPUT_UNAVAILABLE",
  "inputs": {},
  "evidence_ids": []
}
```

Truth tables:

1. **EX-01** is `SATISFIED` only when `commercial_product_separable=false` and `product_level_evidence_available=false`; either true yields `NOT_SATISFIED`; otherwise `NOT_CALCULABLE`. **[SPECIFIED]**
2. **EX-02** is `SATISFIED` only when downside demand `<` MES and `credible_export_contract=false`; demand `>=` MES or a credible contract yields `NOT_SATISFIED`; unknown yields `NOT_CALCULABLE`. No new “materiality” threshold is invented. **[SPECIFIED]**
3. **EX-03** is `SATISFIED` only for `UNSATISFIABLE`; `SATISFIABLE` is `NOT_SATISFIED`; unknown is `NOT_CALCULABLE`. **[SPECIFIED]**
4. **EX-04** is `SATISFIED` only when equivalence is true, idle qualified capacity is at least target demand, and binding market failure is false; any explicit contrary input yields `NOT_SATISFIED`; unknown yields `NOT_CALCULABLE`. **[DERIVED]**
5. **EX-05** is `SATISFIED` for the four named dominant causes; `OTHER` is `NOT_SATISFIED`; unknown is `NOT_CALCULABLE`. **[SPECIFIED]**
6. **EX-06** is `SATISFIED` for either unacceptable competition finding; `ACCEPTABLE` is `NOT_SATISFIED`; unknown is `NOT_CALCULABLE`. The existing 1.25 ratio remains a warning, not automatic “unacceptable” proof. **[SPECIFIED]**

All six checks run on every case even if an earlier one satisfies; state selection uses the first satisfied code in methodology order for the primary rejection narrative and retains the full diagnostic list. **[PROPOSED]**

Each check includes English `narrative` and `localized_narrative: {en, ar}` rendered from its `exclusion.*` catalogue key. Narrative text never controls the check status. **[PROPOSED]**

## 9. Gap taxonomy

### 9.1 Ordered primary tests

1. Any unresolved critical assessment → `evidence`.
2. Satisfied EX-01/EX-05, or a fully evidenced generic-capacity contradiction → `false_or_measurement`.
3. Target-spec demand greater than verified effective qualified capacity → `quantity`.
4. Equivalent product false with resolved grade/performance mismatch → `specification_or_quality`.
5. Same product but wrong end use/customer qualification → `application`.
6. Supply availability after the demand window → `timing`.
7. R3 or formal R10 criticality with no earlier class → `resilience`.
8. If no deterministic class is possible, emit `evidence`, never a guessed business class.

Because I6 explicitly prioritizes unresolved decision-critical evidence, both current goldens have primary `evidence`. **[SPECIFIED]**

### 9.2 Golden classification

```json
Steel:
{
  "primary": "evidence",
  "secondary": ["resilience"],
  "constraint_class": "capacity_or_availability",
  "reason_codes": [
    "TARGET_SPECIFICATION_DEMAND_MISSING",
    "CAPABILITY_GATES_UNRESOLVED",
    "SUPPLIER_CONCENTRATION_SIGNAL"
  ]
}

PP:
{
  "primary": "evidence",
  "secondary": ["false_or_measurement"],
  "constraint_class": "cost_or_competitiveness",
  "reason_codes": [
    "TARGET_SPECIFICATION_DEMAND_MISSING",
    "TARGET_GRADE_UNRESOLVED",
    "GENERIC_CAPACITY_CONTRADICTED"
  ]
}
```

R4-D does not add `specification_or_quality`; it adds only an evidence-need reason because unit values do not prove a grade. **[SPECIFIED]**

Every `gap_class` object also carries compatibility `label` from the English catalogue and `localized_label: {en, ar}` from the matching `gap.*` key; neither label participates in classification. **[PROPOSED]**

## 10. Rejection conditions and state-selection table

### 10.1 Computed rejection conditions

Emit an ordered list with status `SATISFIED`, `NOT_SATISFIED`, or `NOT_CALCULABLE` for:

```text
hard_exclusion
false_or_measurement_gap
equivalent_idle_qualified_supply
uneconomic_at_efficient_scale
structural_overcapacity
generic_capacity_contradicted
```

PP satisfies `generic_capacity_contradicted` from computed R11, the gross-ratio evidence passport, and observed A/B/C nameplate passport IDs. Steel does not. No condition branches on an opportunity ID. **[SPECIFIED]**

### 10.2 Total deep-state table

| Priority | Evidence condition | State | route_code | preferred hypothesis |
|---:|---|---|---:|---|
| 1 | Any hard exclusion `SATISFIED` | `REJECT` | 0 | route 0 |
| 2 | Any other rejection condition `SATISFIED` | `REJECT` | 0 | route 0 |
| 3 | Field gate passes; all exclusions `NOT_SATISFIED`; selected route 1–7 passes all route/policy gates | `ADVANCE` | selected route | selected route |
| 4 | Critical field unresolved/contradictory and at least one named need can change state/route | `INVESTIGATE` | null | evidence-derived hypothesis or null |
| 5 | No rejection; at least one signal; material trigger absent; named allowed monitor trigger | `MONITOR` | 0 | route 0 |
| 6 | Admitted deep case with no legal branch | integrity error | — | — |

`screening_disposition` is `CANDIDATE` for both goldens and every fixture passed to deep analysis. The standalone screening helper returns `NO_CANDIDATE` or `SCREENED_OUT` with `state=None`; those outputs are for S13 and never relabel a deep PP rejection. **[SPECIFIED]**

Decision `confidence` is the weakest A/B/C class among the passports that support the selected rejection, route, or evidence-bounded conclusion, further limited by any fired-rule confidence cap. Missing fields that cause INVESTIGATE are reported in the field assessment rather than coercing the supported conclusion itself to Class E. Steel and PP therefore retain confidence C; the positive fixture also returns C. **[PROPOSED]**

## 11. Exact synthetic-free decision fixtures

All four files are complete PublicSnapshot 2.1.0 JSON records. They share the following exact non-decision boilerplate; each file expands it physically rather than using `$ref`, inheritance, or runtime generation. **[PROPOSED]**

```json
{
  "schema_version": "2.1.0",
  "as_of_date": "2026-09-02",
  "supersedes": "UNAVAILABLE",
  "source_boundary": "public",
  "authority_note": "Synthetic-free deterministic test fixture; not a demonstration evidence artifact.",
  "opportunity": {
    "hs_revision": "H0",
    "hs6": "999999",
    "national_tariff_line": "UNAVAILABLE",
    "sector_profile": "technical_plastics",
    "commercial_name_en": "Test product",
    "commercial_name_ar": "منتج اختباري",
    "decision_object_status": "resolved",
    "application_boundary": "Named test specification and application.",
    "as_of_date": "2026-09-02"
  },
  "trade_quality": {
    "flow_basis": "gross",
    "reexports_separated": true,
    "domestic_origin_exports_separated": true,
    "missing_years": [],
    "monthly_partner_tariff_line_available": false,
    "quantity_comparable": true,
    "execution_cap": "FULL for the supplied test grain"
  },
  "partner_observations": "UNAVAILABLE",
  "disclosed_concentration": {
    "value": "UNAVAILABLE",
    "quantity": "UNAVAILABLE"
  },
  "disclosed_dispersion": "UNAVAILABLE",
  "criticality_designation": "UNAVAILABLE",
  "domestic_capability": {
    "verified_present": true,
    "same_process_family": false,
    "coarse_adjacency_signals": [],
    "producer_evidence": [],
    "public_dimension_states": {
      "feedstock_chemistry": 0,
      "core_process_route": 0,
      "equipment_envelope": 0,
      "finishing_spec_control": 0,
      "qa_lab_metrology": 0,
      "certification_customer_qualification": 0,
      "capacity_time_window": 0,
      "utilities_ehs_permitting": 0,
      "skills_market_integration": 0
    },
    "profile_hard_gates": {
      "polymer_additive_compatibility": {"status": "RESOLVED", "evidence_ids": ["E-GATE"]},
      "conversion_route": {"status": "RESOLVED", "evidence_ids": ["E-GATE"]},
      "tooling": {"status": "RESOLVED", "evidence_ids": ["E-GATE"]},
      "performance_requirement": {"status": "RESOLVED", "evidence_ids": ["E-GATE"]},
      "application_qualification": {"status": "RESOLVED", "evidence_ids": ["E-GATE"]}
    },
    "unresolved_hard_gates": []
  },
  "hard_exclusion_inputs": {
    "heterogeneous_residual_code": {
      "commercial_product_separable": true,
      "product_level_evidence_available": true,
      "evidence_ids": ["E-ID"]
    },
    "downside_market_below_mes": {
      "sustainable_downside_demand_kt": 100.0,
      "minimum_efficient_scale_kt": 50.0,
      "credible_export_contract": false,
      "evidence_ids": ["E-DEMAND"]
    },
    "unsatisfiable_hard_gate": {
      "gate_domain": "customer_qualification",
      "gate_satisfiability": "SATISFIABLE",
      "evidence_ids": ["E-GATE"]
    },
    "idle_equivalent_domestic_capacity": {
      "domestic_specification_equivalent": false,
      "qualified_idle_capacity_kt": 0.0,
      "target_specification_demand_kt": 100.0,
      "binding_market_failure": true,
      "evidence_ids": ["E-CAP"]
    },
    "transitory_or_measurement_gap": {
      "dominant_cause": "OTHER",
      "evidence_ids": ["E-ID"]
    },
    "redundancy_or_crowd_out": {
      "competition_finding": "ACCEPTABLE",
      "evidence_ids": ["E-ROUTE"]
    }
  }
}
```

Unless a fixture subsection replaces it, `decision_inputs` is exactly:

```json
{
  "target_specification_demand": {
    "quantity_kt": 100.0,
    "downside_quantity_kt": 90.0,
    "evidence_ids": ["E-DEMAND"]
  },
  "specification_equivalence": {
    "domestic_product_equivalent": false,
    "qualified_available_kt": 100.0,
    "evidence_ids": ["E-CAP"]
  },
  "route_evidence": "UNAVAILABLE",
  "monitor_trigger": "UNAVAILABLE"
}
```

Every fixture uses unique `snapshot_id` and `opportunity.id` equal to its filename stem prefixed `FIX-PUBLIC-`; no production code contains those strings. **[PROPOSED]**

### 11.1 `advance-route-3.json`

Exact distinguishing content:

```json
{
  "snapshot_id": "FIX-PUBLIC-ADVANCE-ROUTE-3",
  "opportunity.id": "FIX-PUBLIC-ADVANCE-ROUTE-3",
  "trade": [
    {
      "year": 2026,
      "imports_usd_m": 10.0,
      "imports_kt": 10.0,
      "exports_usd_m": 1.0,
      "exports_kt": 1.0
    }
  ],
  "domestic_flows": {
    "period_year": 2026,
    "domestic_production_kt": 100.0,
    "retained_imports_kt": 10.0,
    "domestic_origin_exports_kt": 0.0,
    "reexports_kt": 0.0,
    "source_evidence_ids": ["E-CAP"]
  },
  "domestic_capability.public_dimension_states.certification_customer_qualification": 1,
  "decision_inputs": {
    "target_specification_demand": {
      "quantity_kt": 100.0,
      "downside_quantity_kt": 100.0,
      "evidence_ids": ["E-DEMAND"]
    },
    "specification_equivalence": {
      "domestic_product_equivalent": false,
      "qualified_available_kt": 100.0,
      "evidence_ids": ["E-CAP"]
    },
    "route_evidence": [
      {
        "route_code": 3,
        "binding_constraint": "qualification_or_certification",
        "technical_feasibility_confirmed": true,
        "binding_constraint_fully_removed": true,
        "investment_already_approved_or_financed": false,
        "proceeds_without_intervention": false,
        "policy_prohibition_identified": false,
        "distortion_unacceptable": false,
        "intervention_proportionate_to_constraint": true,
        "downside_cash_flows_m_sar": [-10.0, 6.0, 6.0],
        "hurdle_rate": 0.10,
        "national_value": {
          "domestic_value_added": 50.0,
          "exports": 10.0,
          "resilience_value": 5.0,
          "knowledge_skills": 5.0,
          "fiscal_receipts": 5.0,
          "government_cost": 5.0,
          "displacement": 1.0,
          "resource_environment": 1.0,
          "risk_allowance": 2.0
        },
        "competition": {
          "existing_effective_capacity_kt": 100.0,
          "proposed_incremental_capacity_kt": 0.0,
          "downside_demand_kt": 100.0
        },
        "evidence_ids": ["E-ROUTE"]
      }
    ],
    "monitor_trigger": "UNAVAILABLE"
  },
  "evidence": [
    {"evidence_id": "E-ID", "class": "B", "supports": ["TARGET_PRODUCT_IDENTITY"]},
    {"evidence_id": "E-DEMAND", "class": "B", "supports": ["TARGET_SPECIFICATION_DEMAND"]},
    {"evidence_id": "E-CAP", "class": "C", "supports": ["DOMESTIC_CAPABILITY_ASSESSMENT"]},
    {"evidence_id": "E-GATE", "class": "C", "supports": ["HARD_REGULATORY_PROCESS_GATES"]},
    {"evidence_id": "E-ROUTE", "class": "B", "supports": ["ROUTE_ECONOMICS", "ROUTE_NATIONAL_VALUE", "ROUTE_COMPETITION"]}
  ]
}
```

Each compact row above is physically expanded in the fixture with these exact values; there is no omitted or defaulted passport field:

```json
[
  {
    "evidence_id": "E-ID",
    "title": "Target product identity fixture",
    "source": "TEST_FIXTURE",
    "url": "https://example.invalid/e-id",
    "period": "2026",
    "retrieved_at": "2026-09-02",
    "status": "observed",
    "evidence_class": "B",
    "synthetic_flag": false,
    "supports": ["TARGET_PRODUCT_IDENTITY"],
    "transformation": "No transformation; synthetic-free test fixture.",
    "reviewer_status": "confirmed_by_responsible_authority",
    "contradiction": null
  },
  {
    "evidence_id": "E-DEMAND",
    "title": "Target-specification demand fixture",
    "source": "TEST_FIXTURE",
    "url": "https://example.invalid/e-demand",
    "period": "2026",
    "retrieved_at": "2026-09-02",
    "status": "observed",
    "evidence_class": "B",
    "synthetic_flag": false,
    "supports": ["TARGET_SPECIFICATION_DEMAND"],
    "transformation": "No transformation; synthetic-free test fixture.",
    "reviewer_status": "confirmed_by_responsible_authority",
    "contradiction": null
  },
  {
    "evidence_id": "E-CAP",
    "title": "Domestic capability fixture",
    "source": "TEST_FIXTURE",
    "url": "https://example.invalid/e-cap",
    "period": "2026",
    "retrieved_at": "2026-09-02",
    "status": "observed",
    "evidence_class": "C",
    "synthetic_flag": false,
    "supports": ["DOMESTIC_CAPABILITY_ASSESSMENT"],
    "transformation": "No transformation; synthetic-free test fixture.",
    "reviewer_status": "confirmed_by_responsible_authority",
    "contradiction": null
  },
  {
    "evidence_id": "E-GATE",
    "title": "Hard-gate resolution fixture",
    "source": "TEST_FIXTURE",
    "url": "https://example.invalid/e-gate",
    "period": "2026",
    "retrieved_at": "2026-09-02",
    "status": "observed",
    "evidence_class": "C",
    "synthetic_flag": false,
    "supports": ["HARD_REGULATORY_PROCESS_GATES"],
    "transformation": "No transformation; synthetic-free test fixture.",
    "reviewer_status": "confirmed_by_responsible_authority",
    "contradiction": null
  },
  {
    "evidence_id": "E-ROUTE",
    "title": "Route economics and policy fixture",
    "source": "TEST_FIXTURE",
    "url": "https://example.invalid/e-route",
    "period": "2026",
    "retrieved_at": "2026-09-02",
    "status": "observed",
    "evidence_class": "B",
    "synthetic_flag": false,
    "supports": [
      "ROUTE_ECONOMICS",
      "ROUTE_NATIONAL_VALUE",
      "ROUTE_COMPETITION"
    ],
    "transformation": "No transformation; synthetic-free test fixture.",
    "reviewer_status": "confirmed_by_responsible_authority",
    "contradiction": null
  }
]
```

`TEST_FIXTURE` is test data only and is never interpreted by a gate or selector; the source-independence test proves that changing it cannot alter the result. **[PROPOSED]**

Expected result: field classes B/B/C/C, all resolution statuses `RESOLVED`, route 3 `passes`, unsupported NPV/IRR pass, ΔNV = 66.0, capacity ratio 1.0, state `ADVANCE`, route 3. Downgrading each one of E-ID/E-DEMAND/E-CAP/E-GATE independently to D and then E yields `INVESTIGATE`, null route, and the named blocked field. **[DERIVED]**

### 11.2 `monitor-r3-only.json`

Exact distinguishing content:

```text
snapshot/opportunity ID: FIX-PUBLIC-MONITOR-R3-ONLY
trade: one 2026 row, imports 100 USD m / 100 kt, exports 1 USD m / 1 kt
partner rows: Alpha 60 USD m / 60 kt; Beta 40 USD m / 40 kt;
              both valid, comparable, gross, source E-TRADE
domestic flows: production 90 kt, retained imports 10 kt,
                domestic-origin exports 0, reexports 90 kt
critical passports: B/B/C/C, all resolved exactly as advance fixture
target demand: 100 kt; downside demand: 100 kt
specification equivalence: false; qualified availability: 100 kt
route evidence: UNAVAILABLE
monitor trigger: capacity_state /
  qualified_supply_falls_below_target_demand / E-TRIGGER
E-TRIGGER supports MONITOR_TRIGGER, Class C, confirmed
```

The partner rows reference this exact additional passport:

```json
{
  "evidence_id": "E-TRADE",
  "title": "Partner concentration fixture",
  "source": "TEST_FIXTURE",
  "url": "https://example.invalid/e-trade",
  "period": "2026",
  "retrieved_at": "2026-09-02",
  "status": "observed",
  "evidence_class": "B",
  "synthetic_flag": false,
  "supports": ["TRADE_VALUE", "TRADE_QUANTITY", "SUPPLIER_CONCENTRATION"],
  "transformation": "No transformation; synthetic-free test fixture.",
  "reviewer_status": "confirmed_by_responsible_authority",
  "contradiction": null
}
```

The trigger references the same fully expanded passport shape with ID `E-TRIGGER`, title `Capacity-state monitor trigger fixture`, URL `https://example.invalid/e-trigger`, Class C, and supports `["MONITOR_TRIGGER"]`; every other field is byte-identical to E-TRADE’s common passport fields. **[PROPOSED]**

R3 fires at HHI 0.52; R10 is the same derived resilience signal. R1-D/R2/R4-D/R5/R9-S/R11 do not fire. No rejection condition exists, no positive material gap exists, and the named capacity-state trigger is present. Expected state `MONITOR`, route 0, gap primary `resilience`, screening disposition `CANDIDATE`. **[DERIVED]**

### 11.3 `reject-hard-exclusion.json`

Exact distinguishing content:

```text
snapshot/opportunity ID: FIX-PUBLIC-REJECT-HARD-EXCLUSION
critical passports/classes: B/B/C/C, all resolved
trade and domestic flows: exact advance-fixture values
hard_exclusion_inputs.unsatisfiable_hard_gate:
  gate_domain: safety
  gate_satisfiability: UNSATISFIABLE
  evidence_ids: [E-GATE]
all other common exclusion inputs: unchanged NOT_SATISFIED values
decision_inputs target demand/equivalence: exact common values
decision_inputs.route_evidence: UNAVAILABLE
decision_inputs.monitor_trigger: UNAVAILABLE
```

Expected EX-03 `SATISFIED`; every other exclusion `NOT_SATISFIED`; state `REJECT`, route 0, exclusion-specific rationale, and no escalation. **[DERIVED]**

### 11.4 `reject-equivalence.json`

Exact distinguishing content:

```text
snapshot/opportunity ID: FIX-PUBLIC-REJECT-EQUIVALENCE
critical passports/classes: B/B/C/C, all resolved
trade and domestic flows: exact advance-fixture values
target demand/downside demand: 100/90 kt, evidence E-DEMAND
specification equivalence:
  domestic_product_equivalent: true
  qualified_available_kt: 120.0
  evidence_ids: [E-EQUIVALENCE]
E-EQUIVALENCE: Class C, confirmed, supports DOMESTIC_CAPABILITY_ASSESSMENT
hard exclusion EX-04 block: all four inputs UNAVAILABLE
route evidence/monitor trigger: UNAVAILABLE
```

`E-EQUIVALENCE` is a fully expanded passport with title `Domestic equivalence fixture`, source `TEST_FIXTURE`, URL `https://example.invalid/e-equivalence`, period/retrieval/status/transformation/reviewer/contradiction equal to the common passports, Class C, `synthetic_flag:false`, and supports `["DOMESTIC_CAPABILITY_ASSESSMENT"]`. **[PROPOSED]**

Expected hard exclusions all `NOT_CALCULABLE` or `NOT_SATISFIED`, rejection condition `equivalent_idle_qualified_supply` satisfied from the separate decision input, state `REJECT`, route 0. This proves the non-exclusion rejection branch. **[DERIVED]**

## 12. Route-hypothesis contract and amended-I5 selection

### 12.1 Output shape

Every analysis emits nine records:

```json
{
  "route_code": 5,
  "route_key": "brownfield_incremental_expansion",
  "status": "NOT_CALCULABLE",
  "feasibility": "NOT_CALCULABLE",
  "resolves_binding_constraint": "NOT_CALCULABLE",
  "additionality": "NOT_CALCULABLE",
  "policy_permissibility": "NOT_CALCULABLE",
  "economics": {
    "unsupported_npv_m": "NOT_CALCULABLE",
    "unsupported_irr": "NOT_CALCULABLE",
    "minimum_effective_support_m": "NOT_CALCULABLE"
  },
  "incremental_national_value_m_sar": "NOT_CALCULABLE",
  "competition": "NOT_CALCULABLE",
  "precedence": {
    "blocked_by_lower_route": null
  },
  "reason_codes": ["INCUMBENT_ADJACENCY_PRIORITY", "ECONOMICS_UNAVAILABLE"],
  "reasons": [
    "Verified incumbent adjacency makes brownfield the priority hypothesis; effective capacity and economics remain required.",
    "Downside route economics are unavailable."
  ],
  "localized_reasons": {
    "en": [
      "Verified incumbent adjacency makes brownfield the priority hypothesis; effective capacity and economics remain required.",
      "Downside route economics are unavailable."
    ],
    "ar": [
      "يجعل التجاور المثبت للمنتج القائم المسار القائم هو الفرضية ذات الأولوية؛ وتظل الطاقة الفعلية والاقتصاديات مطلوبة.",
      "اقتصاديات المسار في السيناريو المتحفظ غير متاحة."
    ]
  },
  "evidence_ids": []
}
```

`preferred_hypothesis` is a reference object:

```json
{
  "route_code": 5,
  "selection_basis": "EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE",
  "incremental_national_value_m_sar": "NOT_CALCULABLE",
  "reason_code": "BROWNFIELD_BEFORE_GREENFIELD",
  "reason": "Verified incumbent adjacency makes brownfield the priority hypothesis; effective capacity and economics remain required.",
  "localized_reason": {
    "en": "Verified incumbent adjacency makes brownfield the priority hypothesis; effective capacity and economics remain required.",
    "ar": "يجعل التجاور المثبت للمنتج القائم المسار القائم هو الفرضية ذات الأولوية؛ وتظل الطاقة الفعلية والاقتصاديات مطلوبة."
  }
}
```

When a route is formally selected, `selection_basis` is `MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE` or `EVIDENCED_NO_INTERVENTION`. **[PROPOSED]**

### 12.2 Per-route public tests

```text
0 no intervention
  passes for a satisfied rejection condition or MONITOR no-action state;
  otherwise NOT_CALCULABLE while the gap remains unresolved.

1 administrative/classification/regulatory barrier
  requires route evidence with administrative_or_regulatory constraint.

2 information/market linkage
  requires route evidence with commercial_or_relationship constraint.

3 certification/testing/quality
  requires route evidence with qualification_or_certification or
  specification_or_grade constraint.

4 demand aggregation/offtake
  requires route evidence with demand_fragmentation_or_offtake constraint.

5 brownfield incremental expansion
  may be preferred as NOT_CALCULABLE when R9-S fires and
  capacity_time_window or effective-capacity/allocation is unresolved;
  passes only through complete route evidence.

6 technology/JV
  requires complete route evidence and a compatible major-line/JV capability
  hypothesis; it cannot leapfrog a fully resolving route 1–5.

7 targeted greenfield
  requires complete route evidence, D* > configured 0.65 boundary,
  demand >= MES, and passing competition; it cannot leapfrog any fully
  resolving lower route.

8 shared enabler
  always NOT_CALCULABLE / GRAPH_REQUIRED in S09.
```

No route uses “first passing wins.” **[SPECIFIED]**

### 12.3 Golden route outputs

- Steel: route 5 is preferred because R9-S proves incumbent process-family adjacency and the capacity/time field is unresolved; route 5 remains `NOT_CALCULABLE` because effective capacity and economics are unavailable; route 7 `fails` its precedence/evidence gate; route 8 is `GRAPH_REQUIRED`; formal route remains null. **[SPECIFIED]**
- PP: route 0 `passes` because computed R11 establishes the generic-capacity rejection; every route 1–7 is `fails` with `LOWER_ROUTE_FULLY_RESOLVES`; route 8 remains `GRAPH_REQUIRED`; route 0 is selected. **[SPECIFIED]**

### 12.4 Numeric selection tests

Use pure, exact route records:

1. routes 5 and 6 pass, neither lower route fully resolves, ΔNV 80.0 and 120.0 → route 6;
2. routes 5 and 6 pass at ΔNV 120.0 each → route 5 tie-break;
3. route 2 passes and fully resolves; route 5 has ΔNV 200.0 → route 2 and route 5 `fails` by precedence;
4. route 5 unsupported economics fail but minimum support passes only after routes 0–4 explicitly fail → route 5 remains eligible;
5. route 7 with D*=0.65 fails strict greenfield band; 0.6501 may pass only with MES and competition; use configured values, not code literals in production;
6. route 8 remains `NOT_CALCULABLE` even if a snapshot attempts route-8 evidence.

These fixtures prove precedence before maximum ΔNV and maximum ΔNV after precedence. **[SPECIFIED]**

## 13. Computed evidence needs, conditions, and kill conditions

### 13.1 Controlled need order

The resolver emits and de-duplicates codes in this order:

```text
identity/tariff-line
target specification/application
line-level production or producer-grade matrix
capacity/availability/allocation
qualification/profile hard gates
re-export/origin decomposition
route economics
```

Each need records `blocked_field`, `route_effect`, `evidence_ids`, and `numeric_evsi: NOT_CALCULABLE` unless all four EVSI inputs exist. A need with no plausible route effect cannot cause INVESTIGATE. **[SPECIFIED]**

Each emitted record contains `need_code`, `variant`, and `template_key`.
Dispatch is a total table over evidence state; it never accepts an
opportunity ID, commercial name, producer name, or sector profile. Unknown
exclusion checks do not create six extra requests: their missing inputs map
to these same controlled need codes and are de-duplicated. **[PROPOSED]**

### 13.2 Complete evidence-state variant table

| Template key | Field predicate selecting the variant | Placeholder |
|---|---|---|
| `need.identity.tariff_line` | `decision_object_status == generic_hs6_only`; this is the unresolved product-identity variant regardless of case or sector | none |
| `need.specification.line_production` | the decision object is partially resolved, but producer evidence does not resolve line-level production for the target specification/application | none |
| `need.specification.producer_grade_matrix` | domestic product portfolio is evidenced, while target-grade/application equivalence and local availability remain unresolved | none |
| `need.capacity.availability_allocation` | `capacity_time_window` is unknown, or effective qualified availability/allocation needed by a plausible route is unavailable | none |
| `need.demand.importer_specification` | demand at the required specification is missing and a target specification is partially resolved, but buyer/offtaker specification and local-supply non-selection reason are unavailable | none |
| `need.demand.importer_application_qualification` | demand at the required specification is missing and importer/offtaker application or qualification remains unresolved | none |
| `need.flows.reexport_origin_decomposition` | retained domestic demand cannot be resolved because re-export or domestic-origin decomposition is unavailable | none |
| `need.economics.route_delivered_cost` | an evidenced plausible route has unavailable delivered-cost/import-parity/downside economics | `{route_label}`, rendered from the governed `route.N.short` selected by the route code |
| `need.economics.named_exception_delivered_cost` | generic-capacity contradiction is evidenced, only a named specification/application exception can re-enter, and its delivered economics are unavailable | none |

When more than one demand or specification predicate is true, retain the
most specific variant in table order within that need code; do not emit two
requests for the same blocked fact. Unknown EX-01 maps to identity or
specification, EX-02 to demand/economics, EX-03 to
specification/qualification, EX-04 to specification/capacity, EX-05 to
flows/demand, and EX-06 to economics. The normal need-code de-duplicator then
keeps one substantive request per blocked fact. **[PROPOSED]**

### 13.3 Golden predicate mappings

Steel emits exactly five substantive needs:

```text
partially resolved specification + line-level production unresolved
  → need.specification.line_production
capacity-time-window/effective allocation unresolved
  → need.capacity.availability_allocation
required-specification demand + buyer selection reason unavailable
  → need.demand.importer_specification
retained/re-export/origin decomposition unavailable
  → need.flows.reexport_origin_decomposition
plausible route 5 + delivered-cost economics unavailable
  → need.economics.route_delivered_cost {route_label: route.5.short}
```

PP emits exactly five substantive needs:

```text
generic-HS6-only decision object
  → need.identity.tariff_line
importer application/qualification unresolved
  → need.demand.importer_application_qualification
portfolio evidenced + target-grade equivalence unresolved
  → need.specification.producer_grade_matrix
capacity-time-window/effective allocation unresolved
  → need.capacity.availability_allocation
named specification/application exception + economics unavailable
  → need.economics.named_exception_delivered_cost
```

Tests assert these keys, predicates, order, exact catalogue-rendered EN/AR
output, and five-item count. They do not assert the removed legacy sentences.
**[SPECIFIED]**

### 13.4 Kill/condition derivation

Reason-code sets:

```text
Steel INVESTIGATE / preferred route 5
  condition NO_GREENFIELD_BEFORE_CAPACITY_AND_SPEC
  kills TRANSITORY_REEXPORT_OR_BELOW_MES, INCUMBENT_EXPANSION_CLOSES_GAP

PP generic-capacity REJECT / route 0
  condition NAMED_SPECIALTY_EXCEPTION_ONLY
  kills DOMESTIC_EQUIVALENCE_CONFIRMED, NO_SPECIFICATION_ADJUSTED_GAP

ADVANCE
  condition ALL_GATES_REMAIN_SATISFIED
  kill ANY_ADVANCE_GATE_FAILS

MONITOR
  condition REASSESS_ON_NAMED_TRIGGER
```

## 14. Governed bilingual decision narrative catalogue

### 14.1 Schema and validation

`config/decision_narratives.v1.yaml`:

```yaml
metadata:
  artifact: industrial-opportunity-decision-narratives
  version: "1.0.0"
  effective_date: "2026-09-02"
  authority: "Industrial Opportunity Resolution Methodology §§1.2, 4.2, 5.3, 7.1.1, 7.4, 9, 12 and 15; Core 07 v2"
  status: frozen_for_demo_cycle
  default_locale: en
locales:
  en: {bcp47: en-US, direction: ltr}
  ar: {bcp47: ar-SA, direction: rtl}
placeholder_kinds:
  route_code: computed
  trigger: localized
  product_name: localized
  route_label: localized
  route_short_label: localized
templates:
  en: {}
  ar: {}
```

Validation requires exact locales, identical key sets, identical placeholder sets, allowed placeholder kinds, NFC/non-empty strings, no synthetic-policy warning label, and exact version 1.0.0. Unknown keys and malformed braces fail closed. **[PROPOSED]**

The catalogue never duplicates `SIMULATED — NOT MINISTRY EVIDENCE` or its Arabic policy label. **[SPECIFIED]**

### 14.2 Exact English and Supervisor-approved Arabic defaults

The following is the complete initial key set. Every Arabic string is a
**Supervisor-approved, owner-amendable default**, never owner-approved or
official Ministry wording. PR-04 resolves OQ-01; restructured keys are
re-read at implementation review. **[SPECIFIED]**

```yaml
templates:
  en:
    decision.public.investigate.headline: "INVESTIGATE — binding constraint unresolved"
    decision.public.investigate.rationale: "Test brownfield first; greenfield is not justified from public evidence."
    decision.public.investigate.condition.no_greenfield: "No greenfield or financial support recommendation before effective capacity and target specification are resolved."
    decision.public.investigate.kill.transitory: "Demand is temporary, re-exported or below efficient scale"
    decision.public.investigate.kill.incumbent_expansion: "Incumbent expansion already closes the specification-adjusted gap"

    decision.public.reject_generic.headline: "REJECT — generic capacity support"
    decision.public.reject_generic.route: "No intervention for generic capacity"
    decision.public.reject_generic.rationale: "Reject generic {product_name} capacity support; investigate only explicitly defined grade/application exceptions."
    decision.public.reject_generic.condition.named_exception: "Only a named specialty grade/application exception may re-enter INVESTIGATE."
    decision.public.reject_generic.kill.equivalence: "Imported and domestic products are shown equivalent and qualified"
    decision.public.reject_generic.kill.no_gap: "No specification-adjusted gap exists"

    decision.public.advance.headline: "ADVANCE — route {route_code}"
    decision.public.advance.rationale: "Evidence supports the selected route and every hard gate is satisfied."
    decision.public.advance.condition: "All evidence, economics, additionality and competition gates must remain satisfied."
    decision.public.advance.kill: "Stop or reroute if any ADVANCE gate ceases to pass."

    decision.public.monitor.headline: "MONITOR — no immediate intervention"
    decision.public.monitor.route: "No intervention; watch the named trigger"
    decision.public.monitor.rationale: "No rejection condition is evidenced; the material trigger is absent."
    decision.public.monitor.condition: "Reassess when {trigger}."

    decision.public.reject_exclusion.headline: "REJECT — hard exclusion satisfied"
    decision.public.reject_exclusion.condition: "Reopen only if evidence shows that the hard exclusion no longer applies."
    decision.public.reject_exclusion.kill: "Stop the proposition while the hard exclusion remains satisfied."
    decision.public.reject_equivalence.headline: "REJECT — equivalent qualified supply"
    decision.public.reject_equivalence.rationale: "Equivalent qualified domestic supply meets or exceeds target demand; capacity intervention is not additional."
    decision.public.reject_equivalence.condition: "Reopen only for a named specification or application that is not equivalently supplied."
    decision.public.reject_equivalence.kill: "Stop capacity support while equivalent qualified supply remains available."

    decision.simulated.investigate.headline: "SIMULATED INVESTIGATE — one or more gates remain unresolved"
    decision.simulated.investigate.route: "Simulation controls did not all pass"
    decision.simulated.investigate.rationale: "The simulated branch did not satisfy every hard gate."

    need.identity.tariff_line: "Saudi tariff-line and invoice description"
    need.specification.line_production: "Line-level production by specification, application and destination"
    need.specification.producer_grade_matrix: "Producer grade, application-equivalence and local-availability matrix"
    need.capacity.availability_allocation: "Effective availability, allocation, utilisation, yield, qualification share, backlog and planned outages"
    need.demand.importer_specification: "Importer/offtaker specifications and reason local supply was not selected"
    need.demand.importer_application_qualification: "Importer/offtaker application and qualification requirements"
    need.flows.reexport_origin_decomposition: "Re-export and domestic-origin flow decomposition"
    need.economics.route_delivered_cost: "Delivered cost, import parity and unsupported {route_label} economics"
    need.economics.named_exception_delivered_cost: "Delivered economics for the named specification/application exception"

    exclusion.heterogeneous_residual: "The commercial product cannot be separated from a highly heterogeneous residual code and no product-level evidence is available."
    exclusion.market_below_mes: "The sustainable downside market is below minimum efficient scale and no credible export contract exists."
    exclusion.unsatisfiable_gate: "A legal, safety, environmental, IP or customer-qualification hard gate cannot be satisfied."
    exclusion.idle_equivalent_capacity: "Domestic production meets the required specification with material idle capacity and no binding market failure is evidenced."
    exclusion.transitory_gap: "The apparent gap is dominated by re-export, one-off project demand, temporary price arbitrage or classification discontinuity."
    exclusion.redundancy: "The intervention would create unacceptable redundant capacity or crowd out a more efficient incumbent."

    monitor.trigger.demand: "verified target-specification demand exceeds effective qualified capacity"
    monitor.trigger.regulation: "a binding regulation changes"
    monitor.trigger.technology: "a required technology becomes available or unavailable"
    monitor.trigger.supplier_concentration: "supplier concentration or disruption exposure materially increases"
    monitor.trigger.capacity_state: "effective qualified capacity falls below target-specification demand"

    route.hypothesis.priority: "{route_short_label} priority to test"
    route.0.short: "No intervention"
    route.1.short: "Barrier removal"
    route.2.short: "Market linkage"
    route.3.short: "Certification support"
    route.4.short: "Demand aggregation"
    route.5.short: "Brownfield"
    route.6.short: "Technology / JV"
    route.7.short: "Targeted greenfield"
    route.8.short: "Shared enabler"

    route.0.label: "No intervention"
    route.1.label: "Remove an administrative, classification or regulatory barrier"
    route.2.label: "Information, market linkage or investor/technology matching"
    route.3.label: "Certification, testing, metrology or quality-system support"
    route.4.label: "Demand aggregation, procurement commitment or conditional offtake"
    route.5.label: "Debottlenecking, yield improvement or incremental line expansion"
    route.6.label: "Technology licensing, specialist line or joint venture"
    route.7.label: "Targeted greenfield entry"
    route.8.label: "Shared enabling infrastructure"

    route.0.reason: "No action is the comparator and is selected when an evidenced rejection condition fully resolves the proposition."
    route.0.reason.monitor: "No immediate action is selected while the named observable trigger is monitored."
    route.1.reason: "Administrative, classification or regulatory barrier evidence is required."
    route.2.reason: "A verified information, linkage or matching constraint is required."
    route.3.reason: "A verified specification, certification, testing or qualification constraint is required."
    route.4.reason: "A verified demand-fragmentation or offtake constraint is required."
    route.5.reason: "Verified incumbent adjacency makes brownfield the priority hypothesis; effective capacity and economics remain required."
    route.6.reason: "A verified technology constraint and major-line/JV adjacency are required."
    route.7.reason: "Greenfield requires failed lower routes, D* above the configured band, demand at MES, and passing competition gates."
    route.8.reason: "GRAPH_REQUIRED: route 8 requires the governed dependency graph and a positive UnlockValue."
    route.reason.input_unavailable: "Required public route evidence is unavailable."
    route.reason.lower_route_resolves: "A lower-intervention route fully resolves the binding constraint."
    route.reason.economics_unavailable: "Downside route economics are unavailable."
    route.reason.economics_failed: "The route does not pass downside economics."
    route.reason.national_value_nonpositive: "The route does not have positive incremental national value."
    route.reason.competition_failed: "The route does not pass the competition control."
    route.reason.additionality_failed: "The intervention is not additional."
    route.reason.policy_failed: "The route is prohibited, disproportionate or unacceptably distortive."
    route.reason.max_nv_selected: "The route has the highest defensible incremental national value after precedence gates."

    gap.false_or_measurement: "False or measurement gap"
    gap.quantity: "Quantity gap"
    gap.specification_or_quality: "Specification or quality gap"
    gap.application: "Application gap"
    gap.timing: "Timing gap"
    gap.resilience: "Resilience gap"
    gap.evidence: "Evidence gap"

  ar:
    decision.public.investigate.headline: "تحقّق — القيد الملزم غير محسوم"
    decision.public.investigate.rationale: "اختبر المسار القائم أولاً؛ فلا تبرر الأدلة العامة إنشاء مشروع جديد مستقل."
    decision.public.investigate.condition.no_greenfield: "لا توصية بمشروع جديد أو دعم مالي قبل حسم الطاقة الفعلية والمواصفة المستهدفة."
    decision.public.investigate.kill.transitory: "الطلب مؤقت أو معاد التصدير أو دون الحد الأدنى للكفاءة"
    decision.public.investigate.kill.incumbent_expansion: "توسّع منتج قائم يسد بالفعل الفجوة المعدلة بالمواصفة"

    decision.public.reject_generic.headline: "رفض — دعم الطاقة الإنتاجية العامة"
    decision.public.reject_generic.route: "لا تدخل لدعم طاقة إنتاجية عامة"
    decision.public.reject_generic.rationale: "ارفض دعم طاقة إنتاج {product_name} العامة؛ ولا تتحقق إلا من استثناءات محددة بوضوح للدرجة أو التطبيق."
    decision.public.reject_generic.condition.named_exception: "لا تعاد الحالة إلى التحقق إلا لاستثناء مسمى لدرجة متخصصة أو تطبيق مدعوم بدليل."
    decision.public.reject_generic.kill.equivalence: "ثبت تكافؤ المنتجات المستوردة والمحلية وتأهيلها"
    decision.public.reject_generic.kill.no_gap: "لا توجد فجوة معدلة بالمواصفة"

    decision.public.advance.headline: "تقدّم — المسار {route_code}"
    decision.public.advance.rationale: "تدعم الأدلة المسار المختار، وجميع البوابات الصلبة مستوفاة."
    decision.public.advance.condition: "يجب أن تبقى بوابات الأدلة والاقتصاديات والإضافية والمنافسة مستوفاة."
    decision.public.advance.kill: "أوقف المسار أو غيّره إذا لم تعد أي بوابة من بوابات التقدّم مستوفاة."

    decision.public.monitor.headline: "راقب — لا تدخل فوري"
    decision.public.monitor.route: "لا تدخل؛ راقب المحفّز المسمى"
    decision.public.monitor.rationale: "لم يثبت شرط رفض، والمحفّز المادي غير متحقق."
    decision.public.monitor.condition: "أعد التقييم عندما {trigger}."

    decision.public.reject_exclusion.headline: "رفض — تحقق استبعاد صلب"
    decision.public.reject_exclusion.condition: "لا تُفتح الحالة مجدداً إلا إذا أثبتت الأدلة أن الاستبعاد الصلب لم يعد منطبقاً."
    decision.public.reject_exclusion.kill: "أوقف المقترح ما دام الاستبعاد الصلب متحققاً."
    decision.public.reject_equivalence.headline: "رفض — عرض مؤهل مكافئ"
    decision.public.reject_equivalence.rationale: "يلبي العرض المحلي المؤهل المكافئ الطلب المستهدف أو يتجاوزه؛ ولذلك لا يحقق تدخل الطاقة إضافية."
    decision.public.reject_equivalence.condition: "لا تُفتح الحالة مجدداً إلا لمواصفة أو تطبيق مسمى لا يتوافر له عرض مكافئ."
    decision.public.reject_equivalence.kill: "أوقف دعم الطاقة ما دام العرض المؤهل المكافئ متاحاً."

    decision.simulated.investigate.headline: "تحقّق مُحاكى — ما زالت بوابة واحدة أو أكثر غير محسومة"
    decision.simulated.investigate.route: "لم تجتز المحاكاة جميع الضوابط"
    decision.simulated.investigate.rationale: "لم يستوف فرع المحاكاة جميع البوابات الصلبة."

    need.identity.tariff_line: "بند التعرفة السعودي ووصف الفاتورة"
    need.specification.line_production: "الإنتاج على مستوى الخط حسب المواصفة والتطبيق والوجهة"
    need.specification.producer_grade_matrix: "مصفوفة درجات المنتجين وتكافؤ التطبيقات والإتاحة المحلية"
    need.capacity.availability_allocation: "الإتاحة الفعلية والتخصيص والاستغلال والمردود وحصة التأهيل وتراكم الطلبات والتوقفات المخططة"
    need.demand.importer_specification: "مواصفات المستورد أو المتعهد وسبب عدم اختيار العرض المحلي"
    need.demand.importer_application_qualification: "تطبيق المستورد أو المتعهد ومتطلبات التأهيل"
    need.flows.reexport_origin_decomposition: "تفصيل إعادة التصدير وتدفقات الصادرات ذات المنشأ المحلي"
    need.economics.route_delivered_cost: "التكلفة المسلّمة وتعادل الاستيراد واقتصاديات {route_label} غير المدعومة"
    need.economics.named_exception_delivered_cost: "اقتصاديات التسليم لاستثناء مسمى للمواصفة أو التطبيق"

    exclusion.heterogeneous_residual: "يتعذر فصل المنتج التجاري عن رمز متبق شديد التباين، ولا يتوافر دليل على مستوى المنتج."
    exclusion.market_below_mes: "السوق المستدام في سيناريو الطلب المتحفظ أدنى من الحد الأدنى للكفاءة، ولا يوجد عقد تصدير موثوق."
    exclusion.unsatisfiable_gate: "يتعذر استيفاء بوابة إلزامية قانونية أو متعلقة بالسلامة أو البيئة أو الملكية الفكرية أو تأهيل العميل."
    exclusion.idle_equivalent_capacity: "يلبي الإنتاج المحلي المواصفة المطلوبة بطاقة عاطلة مؤثرة، ولم يثبت وجود إخفاق سوقي ملزم."
    exclusion.transitory_gap: "تهيمن على الفجوة الظاهرة إعادة التصدير أو طلب مشروع لمرة واحدة أو موازنة سعرية مؤقتة أو انقطاع في التصنيف."
    exclusion.redundancy: "سيؤدي التدخل إلى طاقة فائضة غير مقبولة أو إلى مزاحمة منتج قائم أكثر كفاءة."

    monitor.trigger.demand: "يتجاوز الطلب المثبت للمواصفة المستهدفة الطاقة الفعلية المؤهلة"
    monitor.trigger.regulation: "يتغير تنظيم ملزم"
    monitor.trigger.technology: "تصبح تقنية مطلوبة متاحة أو غير متاحة"
    monitor.trigger.supplier_concentration: "يرتفع تركز الموردين أو التعرض للانقطاع بصورة مؤثرة"
    monitor.trigger.capacity_state: "تنخفض الطاقة الفعلية المؤهلة دون طلب المواصفة المستهدفة"

    route.hypothesis.priority: "أولوية اختبار {route_short_label}"
    route.0.short: "عدم التدخل"
    route.1.short: "إزالة العائق"
    route.2.short: "الربط بالسوق"
    route.3.short: "دعم الشهادات"
    route.4.short: "تجميع الطلب"
    route.5.short: "المسار القائم"
    route.6.short: "التقنية أو المشروع المشترك"
    route.7.short: "مشروع جديد موجّه"
    route.8.short: "مُمكّن مشترك"

    route.0.label: "لا تدخل"
    route.1.label: "إزالة عائق إداري أو تصنيفي أو تنظيمي"
    route.2.label: "المعلومات أو الربط بالسوق أو مواءمة المستثمر والتقنية"
    route.3.label: "دعم الشهادات أو الاختبار أو القياس أو نظام الجودة"
    route.4.label: "تجميع الطلب أو التزام المشتريات أو الشراء المشروط"
    route.5.label: "إزالة اختناقات أو تحسين المردود أو توسعة تدريجية للخط"
    route.6.label: "ترخيص تقنية أو خط متخصص أو مشروع مشترك"
    route.7.label: "دخول موجّه بمشروع جديد"
    route.8.label: "بنية تحتية تمكينية مشتركة"

    route.0.reason: "عدم التدخل هو أساس المقارنة ويُختار عندما يحسم شرط رفض مثبت المقترح بالكامل."
    route.0.reason.monitor: "لا يُتخذ إجراء فوري أثناء مراقبة المحفّز المرصود المسمى."
    route.1.reason: "يلزم دليل على عائق إداري أو تصنيفي أو تنظيمي."
    route.2.reason: "يلزم قيد مثبت في المعلومات أو الربط أو المواءمة."
    route.3.reason: "يلزم قيد مثبت في المواصفة أو الشهادة أو الاختبار أو التأهيل."
    route.4.reason: "يلزم قيد مثبت في تجزؤ الطلب أو الشراء."
    route.5.reason: "يجعل التجاور المثبت للمنتج القائم المسار القائم هو الفرضية ذات الأولوية؛ وتظل الطاقة الفعلية والاقتصاديات مطلوبة."
    route.6.reason: "يلزم قيد تقني مثبت وتجاور لخط رئيسي أو مشروع مشترك."
    route.7.reason: "يتطلب المشروع الجديد فشل المسارات الأدنى، ومسافة قدرة أعلى من النطاق المحدد، وطلباً عند الحد الأدنى للكفاءة، واجتياز بوابات المنافسة."
    route.8.reason: "يتطلب المسار 8 الرسم البياني المحكوم وقيمة فتح موجبة؛ الرسم البياني مطلوب."
    route.reason.input_unavailable: "دليل المسار العام المطلوب غير متاح."
    route.reason.lower_route_resolves: "يحسم مسار أقل تدخلاً القيد الملزم بالكامل."
    route.reason.economics_unavailable: "اقتصاديات المسار في السيناريو المتحفظ غير متاحة."
    route.reason.economics_failed: "لا يجتاز المسار الاقتصاديات في السيناريو المتحفظ."
    route.reason.national_value_nonpositive: "لا يحقق المسار قيمة وطنية إضافية موجبة."
    route.reason.competition_failed: "لا يجتاز المسار ضابط المنافسة."
    route.reason.additionality_failed: "لا يحقق التدخل إضافية."
    route.reason.policy_failed: "المسار محظور أو غير متناسب أو يسبب تشوهاً غير مقبول."
    route.reason.max_nv_selected: "يحقق المسار أعلى قيمة وطنية إضافية قابلة للدفاع بعد بوابات الأسبقية."

    gap.false_or_measurement: "فجوة زائفة أو ناتجة عن القياس"
    gap.quantity: "فجوة كمية"
    gap.specification_or_quality: "فجوة مواصفة أو جودة"
    gap.application: "فجوة تطبيق"
    gap.timing: "فجوة توقيت"
    gap.resilience: "فجوة مرونة"
    gap.evidence: "فجوة أدلة"
```

`decision.simulated.investigate.*` is the only simulated catalogue family.
Its three English values were verified byte-for-byte against both
`data/synthetic/*` `decision_narrative.INVESTIGATE` entries. The current
`_decision_narrative` helper has no authored fallback: it requires and returns
the selected scenario entry. Therefore S09 does not dispatch these catalogue
keys for packaged simulations and does not add Arabic simulation text; the
keys are generic wrappers only, and scenario-specific ADVANCE/REJECT text
remains solely in the scenario records. **[VERIFIED]**

For public `INVESTIGATE`, the route label is never fixed to brownfield.
Render `route.hypothesis.priority` with the preferred hypothesis's governed
`route.N.short`. Route 5 therefore produces exactly `Brownfield priority to
test`; a route-3 hypothesis produces `Certification support priority to
test`. The Arabic renderer uses the matching Arabic short label and template.
If there is no preferred hypothesis, the route label is absent rather than
invented. **[PROPOSED]**

### 14.3 Compatibility and rendering

Public and simulation decisions retain scalar English `headline`,
`route_label`, `rationale`, `conditions`, `kill_conditions`, and
`missing_facts`. Add the following structured localization to the public
decision only in S09:

```json
{
  "narrative_version": "1.0.0",
  "localized_narrative": {
    "en": {
      "headline": {
        "text": "INVESTIGATE — binding constraint unresolved",
        "segments": [
          {"kind": "literal", "text": "INVESTIGATE — binding constraint unresolved"}
        ]
      },
      "route_label": {
        "text": "Brownfield priority to test",
        "segments": [
          {"kind": "literal", "text": "Brownfield priority to test"}
        ]
      },
      "rationale": {
        "text": "Test brownfield first; greenfield is not justified from public evidence.",
        "segments": [
          {"kind": "literal", "text": "Test brownfield first; greenfield is not justified from public evidence."}
        ]
      },
      "conditions": [],
      "kill_conditions": [],
      "missing_facts": []
    },
    "ar": {}
  }
}
```

The public English scalar fields are mechanically asserted equal to the EN
`.text` values. The server and browser escape every segment. Arabic templates
render normally; only `computed` placeholder segments receive
`<bdi lang="en" dir="ltr">`. Simulation scalar/list fields remain exactly the
selected scenario record and are presented as source-language islands in
`ar`; they do not receive `localized_narrative` in S09. **[PROPOSED]**

For the generic-capacity rationale, `product_name` is a localized value, not a case key: English uses the case-folded commercial-name segment before the first comma (`Polypropylene, in primary forms` → `polypropylene`), while Arabic uses `commercial_name_ar`. The PP English result therefore remains exact without an opportunity-ID or producer-name branch. Tests cover a second comma-free product name to prevent fixture-specific parsing. **[PROPOSED]**

## 15. Sector profiles 1.1.0

Retain the existing coated-steel and technical-plastics mappings byte-semantically. Set metadata version 1.1.0/effective date 2026-09-02 and append exactly:

```yaml
  pharma_api:
    label: Pharma/API
    weights:
      feedstock_chemistry: 0.10
      core_process_route: 0.20
      equipment_envelope: 0.10
      finishing_spec_control: 0.10
      qa_lab_metrology: 0.15
      certification_customer_qualification: 0.15
      capacity_time_window: 0.05
      utilities_ehs_permitting: 0.10
      skills_market_integration: 0.05
    hard_gates:
      - named_molecule_and_synthesis_route
      - gmp
      - containment
      - impurity_control
      - analytical_validation
      - effluent
      - ip_fto

  fertilizers:
    label: Fertilizers
    weights:
      feedstock_chemistry: 0.15
      core_process_route: 0.20
      equipment_envelope: 0.15
      finishing_spec_control: 0.10
      qa_lab_metrology: 0.05
      certification_customer_qualification: 0.05
      capacity_time_window: 0.10
      utilities_ehs_permitting: 0.15
      skills_market_integration: 0.05
    hard_gates:
      - feedstock_route
      - formulation_granulation
      - nutrient_basis
      - agronomic_performance
      - emissions_and_safe_handling

  fabricated_aluminium:
    label: Fabricated aluminium
    weights:
      feedstock_chemistry: 0.10
      core_process_route: 0.15
      equipment_envelope: 0.15
      finishing_spec_control: 0.15
      qa_lab_metrology: 0.10
      certification_customer_qualification: 0.15
      capacity_time_window: 0.10
      utilities_ehs_permitting: 0.05
      skills_market_integration: 0.05
    hard_gates:
      - alloy
      - forming_fabrication
      - heat_treatment
      - joining_finishing
      - engineering_certification
      - customer_liability
```

Weights and phrases are direct decimal/snake-case projections of methodology §6.3. `ip_fto` preserves the source abbreviation rather than expanding it into a new legal claim. **[DERIVED]**

Per-profile tests:

- exact profile set, dimension-key order, labels, hard-gate lists, and sum `1.0`;
- one exact K=0.70 dimension subset per profile;
- `publication_allowed` at 0.6999/0.7000/0.7001 for every profile;
- route-band 0.20/0.40/0.65 below/equal/above for every profile using configured bands;
- one missing profile gate blocks publication; all resolved permits it; one known failure blocks it;
- a non-hard-gate dimension at state 3 contributes to D* without being misread as a hard-gate failure;
- all current and fixture cases use a known profile; an unknown profile fails.

No new demonstration case uses the three new profiles until S14/S15; tests use synthetic-free capability dictionaries, not invented evidence artifacts. **[SPECIFIED]**

In `capability.py`, replace the blanket `has_known_state_three` publication input with the typed `has_known_hard_gate_failure` result. This aligns the existing implementation with methodology §6.4: only a hard gate at state 3 blocks publication; an ordinary dimension at state 3 may legitimately contribute to a greenfield-likely D*. Both packaged simulations are unchanged because neither relies on the old blanket condition. **[DERIVED]**

## 16. API, GenUI, dossier, and frontend contracts

### 16.1 Analysis response

Add top-level:

```text
screening_disposition
gap_class
route_hypotheses
preferred_hypothesis
evidence_class_assessment
advance_gate
hard_exclusions
rejection_conditions
narrative_version
```

Add `schema_version: "2.1.0"` and the localized narrative under the public
decision. The simulated decision retains the scenario-authored English
fields with no S09 catalogue projection. Existing endpoint paths, methods,
mode semantics, and scalar English compatibility fields remain. **[PROPOSED]**

### 16.2 GenUI

`decision_hero.props` gains `localized_narrative`, `screening_disposition`, `gap_class`, `preferred_hypothesis`, and `narrative_version`. `data_unlocks.props` receives localized missing facts. No new component type is needed in S09. **[PROPOSED]**

For public mode, the hero and unlock list select the current locale, escape
every segment, and stop showing `source_language.caption` around governed
public fields. For simulated mode in locale `ar`, the hero narrative remains
the scenario's English `decision_narrative` and retains its
`source_language.caption`/source-island treatment. Rule results, application
boundaries, source titles, supply JSON, economics reasons, and source
contradictions remain source-language islands where currently applicable.
**[SPECIFIED]**

### 16.3 Dossier

The JSON dossier additively projects `decision_rationale`, the new
diagnostics, and the public bilingual narrative. Public dossier HTML adds one
rationale paragraph and selects localized headline/route/rationale/conditions/
kill/missing facts without wrapping them as English in Arabic. Simulated
dossier HTML adds the scenario-authored rationale but retains source-island
treatment for all scenario narrative fields in `ar`. Demand/supply/source
evidence keeps its current source-island treatment, and S09 does not attempt
KL-33’s S19 structural supply redesign. **[SPECIFIED]**

### 16.4 Authority disclosure

`authority_summary.config_versions` adds:

```json
"decision_narratives": "1.0.0"
```

The value appears in analysis and dossier authority JSON. S09 does not add a new UI-chrome label or change `ui_strings.v1.yaml`; S19 may choose how to display all dossier version labels. **[PROPOSED]**

## 17. Rendered-text change inventory and visual oracle

There are **24** enumerated rendered-text changes:

- RT-01..RT-11: steel public headline, route, rationale, one condition, two kill conditions, five missing facts.
- RT-12..RT-22: PP public headline, route, rationale, one condition, two kill conditions, five missing facts.
- RT-23: remove the English source-language caption from public decision-hero, localized unlock-list, and public dossier narrative blocks; retain it for simulated scenario narratives and rule, application, supply, contradiction, and other still-English source content.
- RT-24: add the active decision rationale paragraph to dossier HTML in both modes/locales; public text is governed catalogue output, while simulated text remains the scenario record.

Public headline/route/rationale/condition/kill text remains exact; missing-fact
text changes only where generic predicate-selected templates replace legacy
phrasing, while each golden retains five requests with the same substance.
Packaged simulation text is not a rendered-text change: every scalar/list and
competition finding remains exactly scenario-authored English in both locales,
with source-island treatment in `ar`. Hard-exclusion, MONITOR, route-reason,
and gap-label templates are new contracts but are not rendered by the two
current public goldens, so they do not increment this count. **[DERIVED]**

Extend existing browser test functions rather than creating a 19th named browser test:

- `test_opportunity_select_loads_each_case` asserts exact catalogue-rendered EN/AR public hero and five predicate-selected missing facts per golden; it asserts keys/substance rather than removed legacy sentences;
- the same test asserts every packaged simulation scalar/list and competition finding equals its scenario `decision_narrative`, and locale `ar` retains English source islands;
- `test_open_dossier_popup_matches_case_and_mode` asserts public localized decision sections contain no `.source-language-island`, while simulated scenario narrative and remaining source blocks do;
- steel public route remains exactly `Brownfield priority to test`, and a non-steel fixture proves the label follows another preferred route's `route.N.short`.

Run all functional nodes first. Then one canonical update with:

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
IOR_UPDATE_VISUAL_BASELINES=1 \
IOR_BASELINE_CHANGE_REF="S09-generalized-public-decision-narratives" \
make e2e-update-baselines
```

This command is for the later authorized Implementer/Supervisor execution,
not the Planner. Inspect all 40 images. The expected pixel-changing subset is
24 images: all 16 dossier images because the rationale is newly rendered,
plus the eight public workspace images across both locales/cases/viewports
because generic missing-fact wording and Arabic public localization change.
Portfolio and simulated workspace images should remain pixel-identical. Any
additional changed image requires explanation before acceptance. **[DERIVED]**

`browser_tests/visual_baselines.py::_source_hashes` adds `config/decision_narratives.v1.yaml`; the manifest records all new/changed engine and frontend module hashes automatically. **[PROPOSED]**

## 18. Simulation-preservation proof

`_simulate`, `_capacity_projection`, `_simulation_capability`,
`_simulation_economics`, `evaluate_simulated_rules`, and
`_decision_narrative` remain selection- and presentation-semantically
unchanged. Do not call the new gate from `_simulate` in S09 because the
existing scenario 1.1.0 contract has no class-if-confirmed fields; I4 belongs
to S10. **[SPECIFIED]**

There is no S09 post-selection simulation-template dispatch. The selected
state reads the scenario's own `decision_narrative` exactly as today for
`ADVANCE`, `REJECT`, or `INVESTIGATE`; the current helper has no separate
fallback text. Locale `ar` marks that English narrative as source-language
content. S10 replaces this boundary with bilingual narrative fields in
scenario contract 2.0.0. **[SPECIFIED]**

Add/retain exact assertions for:

- every state, route, capacity, capability, economics, national-value, competition, EVSI, and synthetic R6–R8 value;
- complete `integrity.ground_truth_backtest`;
- public decision equality before/after simulation;
- no changed `data/synthetic/**` bytes or hashes;
- simulated decision scalar/list/competition text equals the selected
  scenario narrative in both locale responses and remains excluded from the
  back-test tuple;
- `decision.simulated.investigate.*` catalogue values equal both scenarios'
  shared INVESTIGATE trio, but no packaged simulation dispatches through the
  catalogue.

A source-diff audit must show no edits inside `_simulate` unless the Supervisor explicitly approves a no-behaviour helper extraction; the default plan has none. **[PROPOSED]**

## 19. Complete test inventory

### 19.1 Field classes and source independence

`tests/test_decision_evidence.py`:

- every support code maps to the expected field(s);
- each current passport has exactly the normalized code list in §6.2;
- unrelated best-class passport never improves a field;
- one covering A/B/C/D/E passport produces that class;
- absent support produces E/MISSING;
- unconfirmed contradiction produces CONTRADICTORY;
- confirmed contradiction does not silently disappear but may resolve only under the exact confirmed status;
- identity partial, demand absent, capability unresolved, and profile gates unresolved for both goldens;
- policy lists exactly four fields, blocked D/E, and blocked statuses;
- positive fixture gate passes;
- each critical field downgraded separately to D and E blocks;
- changing every passport `source` string while preserving support/class/status leaves assessment, gate, and state unchanged;
- AST of gate/assessment/selector/route functions contains no `source`, `synthetic_flag`, scenario/opportunity IDs, or producer/source names.

The AST check targets functions rather than all of `evidence.py`, because that module legitimately validates synthetic source/flags elsewhere. **[DERIVED]**

### 19.2 Hard exclusions

`tests/test_hard_exclusions.py`:

- all three outcomes for each of six truth tables;
- each individual input `UNAVAILABLE` → `NOT_CALCULABLE`;
- `NOT_CALCULABLE` never yields REJECT;
- first satisfied code supplies primary narrative while all diagnostics remain;
- EX-02 uses strict demand `< MES` and no hidden threshold;
- EX-04 equality availability==demand satisfies;
- EX-06 does not equate ratio warning 1.25 with unacceptable impact;
- both goldens return six `NOT_CALCULABLE`.

### 19.3 Gap taxonomy

`tests/test_gap_taxonomy.py`:

- each seven-class primary branch;
- evidence overrides unresolved business hypotheses;
- exactly one primary and ordered unique secondary classes;
- steel evidence + resilience;
- PP evidence + false/measurement;
- R4-D alone never yields specification/quality;
- invalid zero/two-primary internal result raises.

### 19.4 State and screening

`tests/test_public_decision.py`:

- four exact JSON fixtures in §11;
- ADVANCE and eight single-field D/E downgrades;
- MONITOR R3-only with named capacity trigger;
- MONITOR rejected for missing/unknown trigger and for no signal;
- hard-exclusion REJECT and equivalence REJECT;
- PP R11 REJECT;
- unresolved positive-value fact INVESTIGATE;
- standalone NO_CANDIDATE/SCREENED_OUT returns no formal state;
- both deep goldens remain CANDIDATE;
- admitted deep no-legal-branch raises fail-closed error.

### 19.5 Route hypotheses

`tests/test_route_hypotheses.py`:

- exact route code order 0..8;
- every status vocabulary value;
- every route’s required constraint mapping;
- lower fully resolving route blocks all higher routes;
- max-ΔNV and exact tie tests;
- full precision controls before rounded output;
- financial support eligible only after unsupported/non-financial failures;
- route 7 D*/MES/competition boundaries;
- route 8 always GRAPH_REQUIRED and rejects snapshot route-8 evidence;
- steel preferred route5/null formal route;
- PP route0 and higher-route precedence failures;
- no opportunity-ID string in module AST.

### 19.6 Profiles

`tests/test_sector_profiles.py` implements every proof in §15 and asserts `sector_profiles` authority version 1.1.0. Existing formula/boundary tests remain. **[PROPOSED]**

### 19.7 Narrative catalogue

`tests/test_decision_narratives.py`:

- metadata/version/locales exact;
- EN/AR exact key parity and placeholder parity;
- every value non-empty, trimmed, NFC;
- every `need.*` variant has the exact field predicate in §13.2, and no
  selector input contains an ID, name, producer, or profile;
- both goldens emit the exact five generic need keys in §13.3 with
  catalogue-rendered EN/AR text and the same substantive requests;
- route-economics interpolation uses the governed localized route label;
- `route.hypothesis.priority` plus all nine `route.N.short` keys have EN/AR
  parity; steel renders exactly `Brownfield priority to test`, and route 3
  renders `Certification support priority to test`;
- no `missing.steel.*`, `missing.generic.*`,
  `decision.simulated.route5_advance.*`, or
  `decision.simulated.route0_reject.*` key exists;
- the three `decision.simulated.investigate.*` English strings equal both
  scenario records; `_decision_narrative` has no authored fallback and
  packaged simulations do not dispatch through the catalogue;
- exact English public golden narrative fields equal old scalar fields except
  the approved missing-fact wording changes;
- exact Arabic defaults from §14;
- policy warning labels absent;
- invalid key/locale/placeholder/version fails closed;
- `<script>` in a computed placeholder remains text in API and escaped in HTML;
- structured segments mark only computed values as LTR;
- compatibility scalar equals EN rendered text;
- catalogue cache clears with other config caches.

### 19.8 Schema and migration

Update `test_public_snapshot_schema.py`:

- exact 2.1 candidates and live files validate;
- `public_decision_contract` and all authored decision-output keys reject;
- old free-text supports and unknown controlled codes reject;
- profile hard-gate set/status/evidence rules;
- six exclusion block shapes/domains;
- decision-input and route-evidence domains;
- route 8 snapshot input rejects;
- `supersedes` safe path or exact UNAVAILABLE only;
- all current validation negatives remain.

Update migration tests per §20.

### 19.9 Goldens, rules, simulation, leakage

- `test_golden_cases.py`: public states/routes/fired rules plus gap, field
  assessment, exclusions, preferred hypothesis, exact non-need English
  narratives, five generic substantive needs per golden, and every existing
  simulation narrative/outcome exact.
- `test_rules.py`: R12 uses computed need codes, exact five-item order and
  catalogue-rendered text; it contains no legacy sentence or contract read.
- `test_simulation_fidelity.py`: `_simulate` selection/numbers and
  scenario-authored narrative unchanged; no catalogue narrative drives the
  back-test.
- `test_synthetic_isolation.py`: public snapshots 2.1, no contract, no synthetic decision input; real decision equality still exact.
- `test_capability_economics.py` and boundaries: five profiles and public profile gates.

### 19.10 API, GenUI, dossier, browser

- API detailed response contains all additive fields and schema 2.1.
- malformed decision/narrative/profile evidence maps to typed 422 without a partial result.
- `test_genui_decision_contract.py` asserts exact props and allowed registry unchanged.
- dossier JSON projects public diagnostics/locales; HTML public
  localization/escaping and simulated source-island boundaries exact.
- authority summary adds narrative 1.0.0.
- integrity generator includes the new catalogue and exact Core/config rows.
- browser assertions prove exact generic public needs, preferred-route-derived
  INVESTIGATE label, unchanged scenario-authored simulation narrative, and
  the visual matrix in §17.

## 20. Snapshot migration-equivalence strategy

### 20.1 Test-only adapter

Rename/extend the oracle to `candidate_v21_from_legacy`. It converts historical v1 directly to the exact live 2.1 representation:

- retains identity, dates, trade, producer facts, classes, and contradictions;
- applies the controlled support-code map;
- adds all-unknown golden profile gates, exclusion inputs, and decision inputs;
- drops `rule_context` and `public_decision_contract`;
- never reads old `expected_state` to select a new state.

The v1 files remain byte-identical at the S08 hashes and byte counts. **[SPECIFIED]**

### 20.2 Exact comparisons

For each golden:

1. live 2.1 snapshot equals converted historical v1 field-for-field;
2. R0–R11 execution/fired/result/metrics equal the S08 live ledger;
3. R12 emits the exact generic need-code sequence in §13.3, five English
   missing facts with the same substance per golden, and matching Arabic
   catalogue output; removed legacy sentence equality is not required;
4. old and new public decision compatibility fields are identical except for
   the path-by-path allow-listed missing-fact wording changes;
5. new diagnostics are compared against a path-by-path additive allow-list;
6. no broad prefix/key ignore is permitted;
7. an in-memory fact drift still breaks equality.

Intended public-decision additions are exactly:

```text
screening_disposition
gap_class
route_hypotheses
preferred_hypothesis
evidence_class_assessment
advance_gate
hard_exclusions
rejection_conditions
narrative_version
localized_narrative
```

Snapshot-level intended changes are schema 2.0→2.1, support-code normalization, profile-gate/exclusion/decision blocks, and contract removal. No empirical field changes. **[SPECIFIED]**

## 21. Authority change, generator, and exact expected generated diff

### 21.1 Manifest classification

- Core 01/02/04/07/09: Manifest §7.4 implementation-core revision authorized by ADR-010. **[SPECIFIED]**
- Evidence policy 1.3.0 and sector profiles 1.1.0: §7.3 operating configuration. **[SPECIFIED]**
- New narrative catalogue 1.0.0: §7.3 governed operating text. **[SPECIFIED]**
- Live snapshot 2.1.0 rewrites: authorized representation migration under SD-5 adjacent to §7.5; IDs/dates/facts unchanged and v1 history untouched. **[SPECIFIED]**
- Thresholds, synthetic scenarios, golden extraction data, and DOCX: unchanged. **[SPECIFIED]**

### 21.2 Generator extension

Add exactly:

```python
ROOT / "config" / "decision_narratives.v1.yaml",
```

to `authority_paths`, after `ui_strings.v1.yaml`. Do not add test fixtures to snapshot paths. **[PROPOSED]**

### 21.3 Single run gate

Complete every governed hand edit, behavioral test, functional browser test, visual baseline update, ADR, and generator script change first. Audit the governed diff. Then run exactly once:

```bash
PYTHONPATH=src .venv/bin/python scripts/build_manifests.py
```

The Planner does not run it. A second run is forbidden unless a later separately justified governed correction is approved and recorded by the Supervisor. **[SPECIFIED]**

### 21.4 Exact expected machine diff

`docs/authority/authority_hashes.json`:

- changed rows only for `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml`, Core 01/02/04/07/09;
- one new row for `decision_narratives.v1.yaml`;
- unchanged rows/hashes/bytes for DOCX, thresholds, UI strings, Core 03/05/06/08;
- `generated_on` only if execution date differs.

`data/manifests/snapshot_manifest.json`:

- changed hashes/bytes only for the two live public snapshots;
- historical-v1, both synthetic, and extraction-golden rows byte-identical;
- no new path;
- `generated_on` only if execution date differs.

Copy the complete generated authority table into Manifest §11 and prove exact machine/human equality. Any extra path/hash change stops the slice. **[SPECIFIED]**

## 22. ADR-013 required content

Append ADR-013 only after implementation facts exist:

```markdown
## ADR-013 — Generalized public decision engine and five sector profiles

**Status:** Proposed 2026-09-02; implementation evidence pending independent
review and delivery.

**Context:** S09 executes the owner-approved amended I1/I5, I6/I7, R-1/R-2,
removes the temporary authored public decision contract, and must preserve all
four frozen outcomes.

**Decision:** [record, with exact sources, the PublicSnapshot 2.1 schema;
controlled support vocabulary; four field assessments; evidence-policy 1.3
gate; six exclusions; methodology-primary taxonomy; state table and separate
screening disposition; route 0–8 hypotheses, precedence/max-ΔNV/tie rule and
GRAPH_REQUIRED route 8; evidence needs; narrative catalogue; sector profiles;
simulation non-change; baseline reference; one generator run and exact diff.]

Arabic decision narratives are Supervisor-approved, owner-amendable defaults
under the S09 plan review. They are not represented as owner-approved or as
official Ministry wording.

**Consequences:** [record exact golden preservation, public real-ADVANCE
technical capability proven only by a test fixture, deferrals to S10/S13/S16,
and no authorization impersonation.]
```

Every interpretation cites methodology, Core, context SD, or ADR-010; implementation choices such as tie resolution and structured segments are labelled as plan-review-approved proposals. **[SPECIFIED]**

## 23. Documentation and traceability updates

After test evidence exists:

- `DEVELOPMENT_GUIDE.md`: schema 2.1 authoring, controlled supports, profile gates, route evidence, decision catalogue, one-generator sequence, and Arabic narrative boundary.
- `KNOWN_LIMITATIONS.md`: mark KL-20, KL-23-public, and KL-24 as provisionally closed by local S09 evidence, effective only after review/merge/hosted CI; retain KL-33; state simulation MONITOR/routes remain S10.
- `REQUIREMENTS_TRACEABILITY.md`: add S09-local registry; evidence FR-030..FR-049, V3-C1/C2/C4/C5-public/C8/D1/D3/D9-public at `TESTED`, not COMPLETE.
- `BUILD_PROGRESS.md`: append one S09 local-candidate line; do not alter S08 completion facts.
- `SLICE_GRAPH.md` route matrix: route 0 is re-proven by public computation; S09’s steel route 5 is only a preferred public hypothesis, not a new demonstrated route. Routes 1–7 await S14/S15 and route 8 awaits S16.
- `CHANGELOG.md`: generalized public selector, profile expansion, schema 2.1, and bilingual narratives.

No documentation claims independent approval, PR CI, merge, limitation closure, or milestone completion before those events. **[SPECIFIED]**

## 24. TDD task sequence

Every task records the failing assertion, why it failed, minimal implementation, passing command, and affected regression. No production code precedes its RED test. **[SPECIFIED]**

### Task 0 — Protect boundary and baseline

- Add a changed-path/protected-path checklist to the implementation log.
- Re-run the focused current golden and simulation suites as characterization.
- Record current branch/HEAD/status and exclude Supervisor-owned paths.
- Expected: existing tests green; no repository mutation outside later approved files.

### Task 1 — Write Core v2 text first

- Add failing integrity-contract assertions for the exact §3 wording.
- Observe failure because the contracts are absent.
- Edit Core 01/02/04/07/09 exactly.
- Run the focused integrity-contract test excluding hash verification; observe green.

### Task 2 — Narrative catalogue RED→GREEN

- Write metadata/parity/placeholder/Arabic/escaping failures; add RED tests
  for all predicate-selected `need.*` variants, all nine route short labels,
  route-derived INVESTIGATE labels, removed key families, generic simulated
  INVESTIGATE parity, and absence of simulation catalogue dispatch.
- Add catalogue, `narratives.py`, config cache, and authority-summary version.
- Keep scalar English compatibility.
- Run `tests/test_decision_narratives.py tests/test_authority_disclosure.py`.

### Task 3 — Field assessment RED→GREEN

- Add controlled vocabulary and A–E/absence/contradiction tests.
- Implement support validation and pure assessments.
- Migrate only in-memory fixture candidates first; do not edit live data yet.
- Run `tests/test_decision_evidence.py`.

### Task 4 — ADVANCE gate RED→GREEN

- Add positive A/B/C fixture gate and every D/E downgrade.
- Normalize evidence policy to 1.3.0 and implement generic gate.
- Add AST independence test.
- Run field/gate tests and synthetic-policy tests.

### Task 5 — Hard exclusions RED→GREEN

- Add six truth tables and unknown tests.
- Implement pure checks with no new threshold.
- Run `tests/test_hard_exclusions.py`.

### Task 6 — Gap taxonomy RED→GREEN

- Add seven primary branches, priority, secondary uniqueness, and golden classifications.
- Implement taxonomy and constraint refinement.
- Run `tests/test_gap_taxonomy.py`.

### Task 7 — State selection and screening RED→GREEN

- Add four decision fixtures and all I1 branches.
- Implement rejection conditions, screening helper, deep state table, and fail-closed terminal.
- Keep decisions as reason codes before narrative rendering.
- Run public-decision tests.

### Task 8 — Route hypotheses RED→GREEN

- Add order/status, precedence, max-ΔNV, tie, support sequencing, route7, route8, and golden tests.
- Implement route module and integrate preferred hypothesis.
- Run route/public-decision/economics tests.

### Task 9 — Five profiles RED→GREEN

- Add exact YAML/profile/Kmin/band/gate/unknown-profile tests.
- Append three profiles and integrate public profile gates.
- Run sector/capability/boundary tests.

### Task 10 — Schema 2.1 and contract removal RED→GREEN

- Extend test-only legacy adapter and schema tests in memory.
- Add support/profile/exclusion/decision validators.
- Prove intended migration diff.
- Rewrite both live files in place with only §6 changes and remove contract.
- Prove live==converted history and public compatibility equality.

### Task 11 — Rules and public orchestrator RED→GREEN

- Replace R12 contract read with predicate-selected generic need codes and
  catalogue rendering; prove five substantive needs per golden without
  legacy sentence assertions.
- Replace `_public_decision` with `compute_public_decision`.
- Add all top-level API fields.
- Run rules/golden/migration/synthetic-isolation/simulation-fidelity tests.

### Task 12 — UI and dossier RED→GREEN

- Add GenUI/dossier/localized-segment tests.
- Render localized public narrative fields; retain source islands for
  scenario-authored simulation narratives and other untranslated content.
- Preserve component registry and <200-line modules.
- Run API/GenUI/dossier/UI contracts/ES syntax.

### Task 13 — Browser text RED→GREEN

- Add exact generic-need, route-derived-label, and unchanged simulation
  scenario assertions to existing journey/dossier functions.
- Observe Arabic public old English-island failures while simulated source
  islands remain required.
- Complete rendering until functional Chromium suite passes.
- Do not update baselines while functional failures remain.

### Task 14 — Governed baseline regeneration

- Run canonical update once with the §17 reference.
- Inspect all 40 images, ownership, dimensions, manifest, changed-image subset, and comparison.
- Record actual changed images; do not adjust tolerance.

### Task 15 — Complete governed records before generation

- Add ADR-013, DEVELOPMENT_GUIDE, traceability, limitation/progress/changelog, Core final cross-references, and generator path; leave Manifest §11 hash rows unchanged until the generated rows can be copied exactly.
- Audit no governed edit remains pending.

### Task 16 — Single manifest generation

- Run behavioral/full browser pre-generation gates that do not require refreshed hashes.
- Audit protected diff.
- Run generator once.
- Copy machine rows to Manifest §11.
- Run exact generated-diff and machine/human-table checks.

### Task 17 — Final verification and handoff

- Run focused, full default, integrity, Gate B, smoke, UI, browser functional/visual, and `make ci` gates.
- Inspect full diff and candidate hashes excluding Supervisor/reviewer records.
- Complete implementation/test records with actual output only.
- Stop uncommitted for Supervisor review.

## 25. Verification commands and expected evidence

Planner-run baseline already observed:

```text
506 passed, 1 warning in 2.60s
```

Implementation focused commands:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_decision_evidence.py \
  tests/test_hard_exclusions.py \
  tests/test_gap_taxonomy.py \
  tests/test_public_decision.py \
  tests/test_route_hypotheses.py \
  tests/test_decision_narratives.py \
  tests/test_sector_profiles.py

PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_public_snapshot_schema.py \
  tests/test_snapshot_migration_equivalence.py \
  tests/test_rules.py \
  tests/test_threshold_boundaries.py \
  tests/test_capability_economics.py

PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_golden_cases.py \
  tests/test_simulation_fidelity.py \
  tests/test_synthetic_isolation.py \
  tests/test_api.py \
  tests/test_genui_decision_contract.py \
  tests/test_dossier_contract.py \
  tests/test_authority_disclosure.py \
  tests/test_integrity_contract.py
```

Pre-baseline functional browser:

```bash
export LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs
IOR_E2E_EXPLICIT=1 PYTHONPATH=src .venv/bin/python -m pytest -q \
  browser_tests -m "e2e and not visual" \
  --browser chromium --output=.artifacts/e2e/playwright
```

Post-generation mandatory proof:

```bash
PYTHONPATH=src .venv/bin/python scripts/verify_integrity.py
PYTHONPATH=src .venv/bin/python scripts/validate_scenarios.py
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python scripts/demo_smoke.py
LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make e2e
LD_LIBRARY_PATH=/tmp/ior-s06-browser-libs make ci
```

Also run the workspace-mandated Python-3 default forms before handoff if `make ci` does not visibly show them:

```bash
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python3 scripts/demo_smoke.py
```

No install, lock, browser-install, manifest, Docker, or baseline-update command is executed by the Planner. **[VERIFIED]**

## 26. Failure behavior, security, and determinism

- Invalid config/snapshot/narrative inputs map to `EvidenceIntegrityError`/subclass and HTTP 422 without partial analysis.
- Catalogue API corruption remains HTTP 500 only for catalogue-serving endpoints; analysis corruption is an evidence/authority integrity failure and must not leak internals.
- Test fixtures use fictional data and no external network.
- HTML and JavaScript escape catalogue literals and computed placeholders; malicious fixture values remain text.
- Sorting is explicit for evidence IDs, secondary classes, rejection conditions, and route hypotheses.
- No locale changes arithmetic/state.
- Cached config/repository objects are never mutated.
- Public branch remains public-only; simulation fingerprint remains exact.

These controls extend existing NFR-001/002/003/004/009/010 and synthetic-isolation contracts. **[SPECIFIED]**

## 27. Expected changed-path boundary

The Implementer-authored candidate may contain only:

```text
the files listed in §§5.1–5.5
browser_tests/baselines/v0.3.0/{en,ar}/**/*.webp
browser_tests/baselines/v0.3.0/manifest.json
browser_tests/baselines/v0.3.0/manifest.sha256
docs/authority/authority_hashes.json
data/manifests/snapshot_manifest.json
.workflow/slices/S09-public-decision-and-profiles/{implementation_log.md,test_evidence.md}
```

The full working tree also contains the pre-existing Supervisor/planner slice records and S08 control paths listed in §1; they are excluded from Implementer candidate hashes and are not treated as unexpected changes. Before handoff, compare Implementer-authored paths against this allow-list and separately show that `data/synthetic/**`, historical v1, threshold values, DOCX, UI strings, project config, lockfiles, and Supervisor-owned hunks have no Implementer-authored diff. **[SPECIFIED]**

## 28. Rollback and recovery

- Before the one generator run, a failing RED/GREEN step is corrected only in its task-owned files and rerun; do not regenerate hashes.
- If a governed interpretation conflicts with source authority, stop and return the exact conflict to the Supervisor; do not choose a convenient implementation.
- If the generator diff exceeds §21.4, preserve logs, do not run it again, and revert only the generated outputs through a non-destructive patch after Supervisor direction.
- If baseline output differs beyond the 24 expected images, inspect actual images and DOM/text assertions; never raise tolerance or update again merely to accept drift.
- If a golden state/rule/simulation number changes, treat it as an implementation defect unless the Supervisor presents a formal authority change.
- Rollback unit is the uncommitted S09 candidate. Historical v1 and synthetic files provide recovery oracles; no destructive Git command is needed.

## 29. Resolved decision

### OQ-01 — Arabic decision catalogue wording — RESOLVED

PR-04 approves every surviving Arabic string in §14.2 as a
Supervisor-approved, owner-amendable default for S09. The attribution is
recorded exactly in ADR-013 and the PR and is never described as
owner-approved or official Ministry wording. Restructured keys are re-read at
implementation review, and any correction occurs before the single manifest
run and baseline regeneration. **[SPECIFIED]**

There is no open domain-method decision: I1, I5, I6, I7, R-1, R-2, SD-1..SD-9, profile weights, golden outcomes, schema version, and generator count are already binding. **[SPECIFIED]**

## 30. Skills applied

- `writing-plans`: exact files, interfaces, TDD tasks, commands, rollback, and no placeholders.
- `test-driven-development`: RED→GREEN order for every behavior.
- `verification-before-completion`: baseline and required fresh final commands.
- `sanad`: every consequential choice classified and grounded.
- `muhasib`: scope, authority, evidence, protected paths, and non-self-approval audit.
- `project-orientation` and `task-standards`: reuse-first repository inspection and the post-reading expert persona.
- `autonomous-delivery`: planner-only role boundary and structured handoff.
- `sanad-provenance` and `muhasabah-gate`: final no-free-facts and requirement/scope/risk audit.

## 31. Sanad ledger and mechanical count

Authority read includes `AGENTS.md`, all three workspace rules, Authority Manifest, required methodology sections, Core 01/02/04/06/07/09, milestone gap/slice documents, ADRs 006/008/010/011/012, limitations/traceability/progress, S09 persona/context, S08 plan/reviews/completion, all named engine/config/data/frontend/test files, and the five requested skills. **[VERIFIED]**

Classification rules:

- VERIFIED: observed file contents or command output.
- SPECIFIED: explicit methodology/Core/owner/context requirement.
- DERIVED: necessary consequence with the derivation stated.
- PROPOSED: implementation convention requiring plan approval.
- OPEN: genuine Supervisor wording decision.

Mechanical command:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path

path = Path(".workflow/slices/S09-public-decision-and-profiles/plan.md")
text = path.read_text(encoding="utf-8")
for label in ("VERIFIED", "SPECIFIED", "DERIVED", "PROPOSED", "OPEN"):
    token = chr(91) + label + chr(93)
    print(f"{label}={text.count(token)}")
PY
```

Actual command output:

```text
VERIFIED=20
SPECIFIED=61
DERIVED=16
PROPOSED=43
OPEN=0
```

## 32. Muhasib pre-handoff checklist

- One artifact authored by the Planner: this plan. **[VERIFIED]**
- No implementation, test, config, data, Core, control, manifest, baseline, Git, or external mutation performed. **[VERIFIED]**
- The only executed suite was the explicitly allowed existing read-only pytest command. **[VERIFIED]**
- Core wording precedes code tasks and includes R-1, I1, I5, I6, I7, and route-8 deferral. **[VERIFIED]**
- All four fixture branches, six exclusions, seven gap classes, nine routes, five profiles, both locales, both public goldens, and both simulations have named proof. **[VERIFIED]**
- Threshold values remain unchanged and route 8 has no in-memory implementation. **[VERIFIED]**
- Arabic wording is recorded as Supervisor-approved and owner-amendable,
  never owner-approved. **[VERIFIED]**
- Plan approval and implementation/review remain with separate governed seats. **[VERIFIED]**

Muhasib result is PASS for revised planner handoff, subject to independent
Supervisor plan review; OQ-01 is resolved, and this is not implementation
approval. **[VERIFIED]**
