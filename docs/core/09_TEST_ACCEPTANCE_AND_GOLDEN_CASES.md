# 09 — Test Strategy, Acceptance Gates and Golden Cases

## 1. Objective

Testing must prove methodological fidelity, not merely code coverage. The highest-risk defects are:

- synthetic evidence leaking into the real decision;
- hidden threshold drift;
- an unknown capability state improving adjacency;
- a degraded unit-value diagnostic becoming a grade claim;
- a live source revision changing CI;
- an agent loosening a golden outcome to make a preferred result pass.

## 2. Test layers

### 2.1 Integrity

- governed files exist;
- SHA-256 matches authority and snapshot manifests;
- public snapshots contain no synthetic evidence;
- synthetic scenarios contain mandatory metadata.

### 2.2 Formula unit tests

- log decomposition identity;
- quantity contribution share;
- effective qualified capacity;
- K/U/D\* and λ penalty;
- Kmin/hard-gate publication control;
- NPV and IRR;
- S\* minimum-step behavior;
- incremental national value;
- EVSI.

### 2.3 Rule tests

- R1-D boundary;
- steel R2 fires;
- PP R2 does not fire;
- steel R3 fires;
- R4-F disabled on annual data;
- R4-D never claims grade;
- PP R11 generic-capacity warning fires.

### 2.4 Golden end-to-end tests

#### Golden A — Steel public

Expected:

```text
real state = INVESTIGATE
active state = INVESTIGATE
route code = null
D* not published
R1-D fires
R2 fires
R3 fires
R4-D fires
R9-S fires
greenfield not justified
```

#### Golden A-S — Steel simulation

Expected:

```text
real state remains INVESTIGATE
simulation state = ADVANCE
route code = 5
effective qualified capacity = 57.509 kt
gap = 46.491 kt
D* route = incremental upgrade
unsupported NPV = -18m
unsupported IRR = 9.5%
S* = 18m
incremental national value = 198m
post-entry capacity ratio <= 1.25
```

#### Golden B — Polypropylene public

Expected:

```text
real state = REJECT
route code = 0
R1-D fires
R2 does not fire
R11 fires
only named grade/application exceptions remain investigable
```

#### Golden B-S — Polypropylene simulation

Expected:

```text
real state remains REJECT
simulation state = REJECT
qualified availability > target demand
specification-adjusted gap < 0
support = 0
```

### 2.5 Extraction golden tests

- four labeled AR/EN fields;
- exact normalized output;
- exact source spans retained;
- 100% pass required for the offline fixture.

### 2.6 API tests

- health endpoint;
- opportunity listing in both modes;
- analysis response contract;
- UI manifest approved component types;
- dossier JSON and HTML;
- extraction endpoint.

### 2.7 Frontend contract tests

At minimum, static checks confirm:

- evidence-mode toggle exists;
- synthetic warning styles exist;
- public and simulated states can display together;
- dossier action exists;
- Arabic `dir=rtl` is present;
- no external CDN is required.

A production pipeline should add Playwright visual and interaction tests.

## 3. Threshold boundary tests

For every threshold, include below/equal/above cases where applicable.

Examples:

```text
R2 share: 0.5999 / 0.6000 / 0.6001
R3 HHI: 0.2499 / 0.2500 / 0.2501
Kmin: 0.6999 / 0.7000 / 0.7001
D* bands: 0.20, 0.40, 0.65
capacity ratio: 1.2499 / 1.2500 / 1.2501
```

## 4. Synthetic leakage tests

Required assertions:

1. public evidence rows all set `synthetic_flag=false`;
2. public analysis contains no synthetic row;
3. simulated analysis contains both public and labeled synthetic rows;
4. public-decision fingerprint before and after simulation is identical;
5. simulated dossier includes disclosure;
6. real dossier does not include a synthetic disclosure;
7. a malformed synthetic scenario fails closed.

## 5. Snapshot test policy

Golden cases never pull live Comtrade, WITS, BACI, company pages or standards.

A source refresh process creates a new candidate snapshot and runs comparison tests. If the result changes, reviewers determine whether the change reflects:

- a legitimate data revision;
- a classification change;
- a source error;
- an implementation defect;
- a methodology/calibration issue.

Tests are not loosened merely because a live source changed.

## 6. Acceptance gates by subsystem

### Gate A — Authority

- original methodology present;
- frozen core complete;
- hashes pass;
- external build machinery referenced, not copied.

### Gate B — Data

- snapshots validate;
- units and gross-flow boundary visible;
- source records and hashes present;
- synthetic scenarios reconcile to public marginals.

### Gate C — Rules

- every R-rule visible;
- thresholds loaded from config;
- steel and PP rule expectations pass.

### Gate D — Capability

- effective capacity exact;
- unknown penalty exact;
- public D\* gated;
- simulated D\* published only after hard gates resolve.

### Gate E — Economics

- unsupported case calculated;
- S\* minimal and reproducible;
- national value and competition controls visible;
- PP does not receive support merely because economics is available.

### Gate F — Evidence isolation

- zero synthetic leakage;
- dual states visible;
- all synthetic rows labeled.

### Gate G — Product

- professional responsive frontend;
- case selection and mode toggle function;
- GenUI manifest adapts panels;
- dossier opens and prints;
- Arabic text renders correctly.

### Gate H — Release

```bash
python3 scripts/build_manifests.py   # only after approved changes
python3 scripts/verify_integrity.py
pytest -q
python3 scripts/demo_smoke.py
```

All must pass.

## 7. Definition of done for the packaged MVP

The MVP is complete when:

- it starts from a clean Python environment with documented commands;
- no external key is required;
- all tests pass;
- integrity passes;
- the two public golden outcomes are correct;
- the steel simulated transition is correct and visibly disclosed;
- the PP simulation still rejects unnecessary support;
- the interface is usable at desktop and tablet widths;
- the Decision Dossier is available in JSON and printable HTML;
- documentation and source are included in one zip.

## 8. Reviewer anti-gaming rule

A failing golden test is evidence of one of three things:

1. the implementation is wrong;
2. the frozen evidence/config changed;
3. the governing methodology changed.

The reviewer must identify which one. Changing the expected result without an authority change is prohibited.
