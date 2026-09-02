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

```text
Qeffective = Nameplate × Availability × Yield × Qualification share × Market allocation
```

All factors are within [0,1]. A public nameplate without the other factors does not establish supply.

### 4.2 Dimension states

```text
0 present
1 minor known upgrade
2 major specialist line / technology / JV but material site advantage
3 fundamentally absent
U unknown
```

### 4.3 K, U and D\*

```text
K = Σ known weights
U = 1 − K
Dknown = Σ(w × d/3) / K
D* = min(1, Dknown + λU)
```

D\* publication requires:

- K ≥ Kmin;
- no unresolved hard gate;
- no hard gate at state 3.

An internal pre-gate value may be returned for diagnostics, but the public `d_star` field remains null.

### 4.4 Route bands

Loaded from configuration:

- ≤0.20 immediate adjacency;
- ≤0.40 incremental upgrade;
- ≤0.65 major line/JV;
- >0.65 greenfield likely.

A route band is a technical route hypothesis, not public authorization.

## 5. Economics engine

### 5.1 Unsupported case first

The engine first calculates the route without financial support. If NPV and IRR already pass and no market failure remains, financial intervention is zero.

### 5.2 NPV

```text
NPV = Σ FCFt/(1+h)^t
```

Cash flows are annual in the MVP. Production can introduce dated cash flows while preserving the same contract.

### 5.3 IRR

IRR is solved deterministically by bracketing and bisection. A cash-flow series without both negative and positive values returns null.

### 5.4 Minimum effective support

The MVP searches support in configured increments, applied to the initial cash flow:

```text
S* = first S where NPV(S) ≥ tolerance and IRR(S) ≥ h − tolerance
```

If no support below the configured maximum passes, `passes=false` and the route cannot `ADVANCE` on that economics case.

### 5.5 Incremental national value

Benefits and costs remain explicit. Positive project NPV does not by itself justify public support.

### 5.6 Competition

The MVP exposes:

```text
(existing effective target capacity + proposed incremental capacity) / downside demand
```

A ratio above 1.25 is a warning requiring export demand or exceptional strategic rationale.

## 6. EVSI

The practical approximation is:

```text
P(route changes) × |value difference| − evidence cost − delay cost
```

The next evidence fact is shown only when it has a plausible route effect.

## 7. Decision algorithm

### 7.1 Public branch

```text
load frozen public case
validate every public evidence row is non-synthetic
evaluate R0-R12
evaluate public capability states
if generic-capacity exclusion is proven:
    REJECT route 0
else if decision-critical facts or hard gates unresolved:
    INVESTIGATE
else:
    evaluate complete route sequence
```

The current public fixtures deliberately exercise `INVESTIGATE` and `REJECT`.

### 7.2 Simulation branch

```text
public = analyze_public(case)
fingerprint = fingerprint(public.real_decision)
validate synthetic scenario
calculate target-spec demand and effective capacity
calculate specification-adjusted gap
calculate capability and route band
calculate unsupported economics, S*, national value and competition
calculate EVSI
select simulated state
assert fingerprint(public.real_decision) unchanged
return both states
```

### 7.3 Steel simulation selection

`SIMULATED ADVANCE` requires all of:

- positive specification-adjusted gap;
- route publication control passes;
- D\* ≤ 0.40;
- economics passes with minimum effective support;
- incremental national value positive;
- competition warning does not fire.

Selected route: code 5, conditional brownfield debottlenecking/line expansion.

### 7.4 PP simulation selection

If equivalent qualified availability exceeds target demand, generic capacity support remains `REJECT`, route 0, regardless of the availability of synthetic detail.

## 8. Conditions and kill conditions

A decision is incomplete without observable conditions and kill conditions.

Steel simulation conditions:

- customer acceptance for the named target specification;
- 50 kt incremental qualified capacity within 18 months;
- milestone-based, sunset-bound support with clawback.

Steel kill conditions:

- committed demand below 72 kt;
- another incumbent expansion closes the gap;
- customer qualification misses the contractual milestone.

## 9. Threshold enforcement

Implementation code must reference configuration keys. Tests may assert expected initial values, but domain functions shall not contain hidden duplicates of threshold values.

Changing a threshold requires a new version, rationale, sector scope and full regression.

## 10. Error and boundary handling

- non-positive log inputs → error;
- invalid capacity factors → error;
- K=0 → no D\*;
- unknown hard gate → no published route band;
- NPV rate ≤ −100% → error;
- no IRR sign change → null;
- missing synthetic scenario → error in simulated mode;
- malformed scenario → evidence-integrity error.
- malformed public schema, an unsafe historical link, an invalid concentration
  domain, or contradictory domestic-flow arithmetic → evidence-integrity error.

## 11. Determinism requirement

Given identical:

- source snapshots;
- configuration versions;
- code version;
- as-of date;

all calculations and decision outputs must be byte-for-byte stable apart from non-semantic JSON ordering.
