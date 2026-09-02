# S02 Threshold Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:test-driven-development` for every production change and `superpowers:executing-plans` or the repository's approved implementation protocol to execute this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking. This document is a Planner deliverable; it is not approval to implement, commit, push, or merge.

**Goal:** Remove configured threshold literals from executable engine/frontend behavior, correct R3 to compare largest-supplier share only with the largest-supplier threshold, govern the methodology-backed R11 export/import ratio in `thresholds.v1.yaml` 1.1.0, and enforce the result with deterministic boundary tests plus an AST CI guard.

**Architecture:** Pure predicates in `rules.py`, `capability.py`, and `decision_engine.py` receive the relevant versioned configuration mappings; orchestrators retain their response contracts and add threshold provenance fields. A standalone AST validator reads every numeric value from `config/thresholds.v1.yaml` and rejects matching direct numeric operands in comparisons under `src/ior_mvp/*.py`. The frontend receives R3 metrics through GenUI and renders the configured threshold rather than owning a copy.

**Tech stack:** Python 3.12/3.14, Python `ast`, PyYAML, pytest, FastAPI response dictionaries, plain JavaScript, GitHub Actions, GNU Make, SHA-256 authority manifests.

**Planner stance:** Principal Decision-Rules Engineer. Data classification: **Internal** repository source/configuration and public/synthetic fixtures; no Restricted data, credentials, secrets, personal data, or live source access is required.

## 1. Objective and completion boundary

S02 closes only the threshold-governance defects enumerated by the Supervisor in `.workflow/slices/S02-threshold-governance/context.md`:

1. Replace executable threshold copies `0.40`, `1.25`, and `50` with configuration lookups.
2. Replace the frontend caption copy `0.25` with the R3 threshold sent in the payload.
3. Stop comparing `top_two_value_share` with a largest-supplier threshold.
4. Add the methodology §14.2 R11 ratio as the sole new configuration key.
5. Add exact boundary proof for the Supervisor-specified R1-D, R2, R3, R11, Kmin, D\* band, and competition thresholds.
6. Add the missing explicit R4-F-disabled rule test.
7. Fail local and hosted CI if a configured numeric value is reintroduced as a direct Python comparison literal.
8. Regenerate governed hashes once, after the changed configuration has passed the full non-integrity regression.
9. Preserve steel/public `INVESTIGATE`, steel/simulated `ADVANCE` route 5, polypropylene/public `REJECT` route 0, and polypropylene/simulated `REJECT`.

“No threshold value in engine/frontend code” is operationalised by the exact scope-approved controls above: no configured value may be a Python comparison literal, and the R3 UI caption may not contain its configured value. Existing scenario decision-condition prose such as `50 kt`, `18 months`, and `72 kt` in `decision_engine.py` is not a `thresholds.v1.yaml` rule/gate and is governed by S04/KL-08; changing it here is prohibited.

## 2. Global constraints

- The methodology DOCX is authoritative. The extracted Markdown is only a searchable mirror.
- No existing threshold value changes. Strictness is preserved: R2/R3/Kmin/band equality continues to pass; competition and R11 fire only when strictly greater than their configured values.
- The sole new configuration key is `rules.R11.generic_capacity_export_import_value_ratio`.
- `config/thresholds.v1.yaml` remains the v1-major artifact; metadata moves from 1.0.0 to 1.1.0.
- Do not modify `sector_profiles.v1.yaml`, `evidence_policy.v1.yaml`, `data` payloads, `docs/core`, the DOCX, or golden expectations.
- `data/manifests/snapshot_manifest.json` may receive only the generator-produced `generated_on` change described in §17. No data entry, hash, path, or byte count may change.
- No R5/R6/R7/R8 evaluator is added. R4-F remains explicitly disabled on the annual public fixtures.
- No CSS change and no other UI change.
- Public functions have complete type hints; no bare `except`.
- No live sources, network data, or external credentials.
- Builder, Planner, Supervisor, and independent Reviewer remain separate seats. The Planner cannot approve or merge.
- Commit, push, PR, CI promotion, and merge remain Supervisor-controlled.

## 3. Governing requirements and sources

| ID / authority | Requirement applied in this slice |
|---|---|
| FR-002 | R-rule thresholds load from versioned YAML. |
| FR-025 | R11 supports evidence-warranted generic-capacity rejection. |
| FR-033 | D\* publication is blocked below Kmin or with unresolved gates. |
| FR-034 | Four capability route bands retain configured inclusive upper edges. |
| FR-044 | Post-entry capacity/downside-demand ratio and warning threshold remain visible. |
| INV-07 | No hidden threshold constants; thresholds are versioned configuration. |
| TL-03 | Add missing R1-D boundary, explicit R3, and explicit R4-F-disabled tests. |
| TL-08 | Add below/equal/above threshold tests. |
| GATE-C | Every R-rule remains visible and thresholds come from configuration. |
| ADR-005 | Exact R11 key enters through the operating-configuration gate; hashes and regressions are mandatory. |
| Manifest §6.7 | Thresholds are read from versioned configuration. |
| Manifest §7.2–7.3 | Preserve behavior for refactors; version, rationale, scope, sensitivity evidence, owner approval, regressions, and hashes for the new operating key. |
| Manifest §8, §11 | Regenerate machine hashes through the approved script and update the human table. |
| Core 07 §3 | R2, R3, and R11 semantics. |
| Core 07 §4.3–4.4 | Kmin/hard-gate publication and configured route bands. |
| Core 07 §5.6, §7.3 | Competition warning and steel-simulation selection. |
| Core 07 §9–§10 | No hidden threshold copies; fail closed at boundaries and missing inputs. |
| Core 09 §2.3–§2.4, §3, §8 | Rule, golden, boundary, and anti-gaming proof. |
| AGENTS.md #7 and proof rule | Configuration-only thresholds plus integrity, pytest, and smoke evidence. |

Authoritative DOCX verification found the governing statements: R1-D is at least three positive observed years in a four-year window; R2 is positive quantity, contribution at least 60%, and growth at least 5%; R3 is HHI at least 0.25 or top/largest supplier at least 50%; post-entry ratio greater than 1.25 is a warning; and established exports more than 50 times import value cannot justify generic PP capacity. These agree with the cited mirror/core passages and the context file.

## 4. Branch, base, baseline, and pre-existing worktree

- Confirmed branch: `slice/S02-threshold-governance`.
- Confirmed base: `432af8af1fa88a2258a0fd8d825a6855e408270f`.
- Confirmed base branch at dispatch: `main`.
- Baseline focused proof: 33 tests passed with the existing upstream Starlette deprecation warning.
- Baseline integrity: `INTEGRITY PASS` for both manifests.
- Existing prohibited-file scanner: `PROHIBITED FILE SCAN PASS (107 tracked files)`.

The initial status did **not** match the stated expectation. These paths pre-existed branch creation and are Supervisor-owned:

```text
 M .workflow/slices/S01-ci-and-toolchain/pr_record.md
 M .workflow/state.json
 M docs/BUILD_PROGRESS.md
?? .workflow/slices/S01-ci-and-toolchain/completion.md
?? .workflow/slices/S02-threshold-governance/
```

Do not revert, overwrite, misattribute, or silently stage the S01/control-record paths. Task 0 re-inventories them against the Supervisor's current state.

## 5. Existing-state assessment with line evidence

Line references are from base `432af8a`.

| Defect | Evidence | Required correction |
|---|---|---|
| Competition threshold duplicated as response data | `src/ior_mvp/decision_engine.py:130` sets `"warning_threshold": 1.25`. | Read `competition.post_entry_capacity_to_downside_demand_warning`. |
| Competition threshold duplicated in a gate | `src/ior_mvp/decision_engine.py:131` compares `ratio <= 1.25`. | Compute `warning_fires = ratio > configured_warning`; retain `passes_default_warning = not warning_fires`. |
| Steel route edge duplicated | `src/ior_mvp/decision_engine.py:140` compares `d_star <= 0.40`. | Compare with `capability.route_bands.incremental_upgrade_max`. |
| R11 ratio is hidden | `src/ior_mvp/rules.py:276` compares `export_import_ratio > 50`. | Compare with the new `rules.R11.generic_capacity_export_import_value_ratio`. |
| R3 compares unlike measures | `src/ior_mvp/rules.py:154` compares `top_two_value_share` with `R3.largest_supplier_share`. | Use only `supplier_metrics_2024.largest_supplier_share`; absent means `NOT_CALCULABLE`. |
| Frontend owns an R3 value | `src/ior_mvp/static/app.js:192` renders `Resilience review threshold: 0.25`. | Render `props.supplier_concentration.hhi_threshold`. |

Supporting evidence:

- `config/thresholds.v1.yaml:35-36` already defines R3 HHI and largest-supplier thresholds.
- `config/thresholds.v1.yaml:90-93` already defines all D\* band edges.
- `config/thresholds.v1.yaml:98` already defines the competition warning.
- `config/thresholds.v1.yaml:79-84` has the R11 cost-premium threshold but lacks the §14.2 ratio.
- `data/snapshots/public/SAU-H0-721049.json:59-65` carries `top_two_value_share: 0.763` and `partner_value_hhi: 0.36`, but no `largest_supplier_share`.
- `data/snapshots/public/SAU-H0-390210.json:39` carries the latest export/import ratio `50.6`, so strict `> 50` remains fired after externalisation.
- `tests/test_golden_cases.py:31` contains a test expectation `< 1.25`. Core 07 §9 permits tests to assert initial values, and changing this golden expectation is prohibited.

The exact mandated AST rule detects three current comparison hits:

```text
src/ior_mvp/decision_engine.py:131:1.25
src/ior_mvp/decision_engine.py:140:0.4
src/ior_mvp/rules.py:276:50
```

The dictionary literal at `decision_engine.py:130` is intentionally outside the AST comparison rule but is still removed by the implementation and covered by response-provenance tests. The JavaScript caption is covered by a separate static regression test.

## 6. Relevant existing code

- `src/ior_mvp/config.py`: cached `thresholds_config()` loader; no change required.
- `src/ior_mvp/rules.py`: R1-D/R2/R3/R11 orchestration and rule metrics.
- `src/ior_mvp/capability.py`: configured Kmin and route-band handling; extract only a pure publication predicate.
- `src/ior_mvp/decision_engine.py`: steel route and competition gates.
- `src/ior_mvp/genui.py`: builds the `metric_grid` props consumed by the frontend.
- `src/ior_mvp/static/app.js`: `renderMetricGrid` owns the current R3 caption copy.
- `scripts/build_manifests.py`: rewrites both snapshot and authority manifests using the current date.
- `scripts/verify_integrity.py`: verifies tracked hash entries and fails closed.
- `tests/test_rules.py`: current rule/golden-unit assertions and config version assertion.
- `tests/test_capability_economics.py`, `tests/test_golden_cases.py`, `tests/test_api.py`, `tests/test_integrity_contract.py`: regression-only in S02.
- `tests/test_ci_contract.py`: exact Python-job gate order.
- `.github/workflows/ci.yml`, `Makefile`: hosted/local gate sequences.

## 7. Files to create and change

### Create

- `scripts/check_threshold_literals.py`
- `tests/test_threshold_literals.py`
- `tests/test_threshold_boundaries.py`
- `.workflow/slices/S02-threshold-governance/implementation_log.md`
- `.workflow/slices/S02-threshold-governance/test_evidence.md`

### Modify

- `src/ior_mvp/rules.py`
- `src/ior_mvp/decision_engine.py`
- `src/ior_mvp/capability.py`
- `src/ior_mvp/genui.py`
- `src/ior_mvp/static/app.js`
- `config/thresholds.v1.yaml`
- `docs/authority/authority_hashes.json` — generator only
- `docs/authority/00_AUTHORITY_MANIFEST.md` — thresholds row only
- `.github/workflows/ci.yml`
- `Makefile`
- `tests/test_ci_contract.py`
- `tests/test_rules.py`
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/ARCHITECTURE_DECISIONS.md`

### Conditional generated companion

- `data/manifests/snapshot_manifest.json` — keep only the generator-produced `generated_on: "2026-09-02"` change if and only if every `files[]` entry is byte-for-byte unchanged.

No other path may change.

## 8. Architecture and interfaces

### 8.1 Predicate ownership

`rules.py` owns pure predicates for rule semantics:

```python
def r1d_fires(positive_years: list[int], rule_config: dict[str, Any]) -> bool: ...
def r2_fires(
    delta_ln_quantity: float,
    contribution_share: float,
    quantity_growth: float,
    rule_config: dict[str, Any],
) -> bool: ...
def r3_fires(
    hhi: float | None,
    largest_supplier_share: float | None,
    rule_config: dict[str, Any],
) -> bool: ...
def r11_generic_capacity_fires(
    generic_capacity_reject: bool,
    export_import_value_ratio: float | None,
    rule_config: dict[str, Any],
) -> bool: ...
```

`capability.py` owns the publication-control predicate without changing K/U/D\*:

```python
def publication_allowed(
    d_star: float | None,
    known_weight_coverage: float,
    minimum_known_weight_coverage: float,
    unresolved_hard_gates: list[str],
    has_known_state_three: bool,
) -> bool: ...
```

The existing `route_band(distance, bands)` remains the pure band predicate. `evaluate_capability` continues to pass `thresholds_config()["capability"]["route_bands"]`.

`decision_engine.py` owns the competition predicate:

```python
def competition_warning(
    post_entry_capacity_to_downside_demand: float,
    competition_config: dict[str, Any],
) -> bool: ...
```

### 8.2 Configuration consumption

- `evaluate_rules` loads `thresholds_config()["rules"]` once and passes `R1_D`, `R2`, `R3`, and `R11` mappings into the pure predicates.
- `_simulate_steel` loads `thresholds_config()` once, passes the competition mapping into `competition_warning`, publishes its configured warning value, and reads `capability.route_bands.incremental_upgrade_max` for the Core 07 §7.3 route gate.
- `evaluate_capability` continues to load Kmin and bands once; only the publication Boolean is delegated.
- No helper supplies a default threshold value. A missing key raises and fails closed.

### 8.3 Response contract

All changes are additive except that an existing value is now configuration-sourced.

R3 `metrics` retains `hhi` and `top_two_share`, and adds:

```text
hhi_threshold
largest_supplier_share
largest_supplier_threshold
```

When the source lacks `largest_supplier_share`, that metric is exactly the string `"NOT_CALCULABLE"`. `top_two_share` remains a disclosed diagnostic but is never an input to `r3_fires`.

R11 `metrics` retains `export_import_value_ratio` and adds:

```text
export_import_value_ratio_threshold
```

Steel `competition` retains existing fields, keeps `warning_threshold` but sources it from config, and adds:

```text
warning_fires
```

`passes_default_warning` remains the inverse for backward compatibility.

GenUI `metric_grid.props` adds:

```text
supplier_concentration
```

Its value is the complete R3 metrics mapping, so both configured R3 thresholds reach the UI without another config read in JavaScript.

## 9. Exact algorithms

### 9.1 AST threshold-literal validator

1. Load `config/thresholds.v1.yaml` using `yaml.safe_load`; require a top-level mapping.
2. Walk the YAML recursively.
3. Include Python/YAML integers and floats as `float` values.
4. Exclude booleans and strings, including dates/version strings.
5. Parse each direct `src/ior_mvp/*.py` file with `ast.parse`.
6. Visit every `ast.Compare`.
7. Examine only `Compare.left` and each direct member of `Compare.comparators`.
8. If an examined node is a numeric `ast.Constant`, normalise it to `float`.
9. Flag it when the value occurs in the YAML numeric set and is not one of `{0, 1, 2, 3}`.
10. Sort findings deterministically and report `file:line:value`.
11. Exit 0 when clean, 1 on findings, and 2 on source/config read, YAML, or Python parse errors.

This deliberately does not inspect numeric literals outside comparisons. Formula constants such as `state / 3`, IRR brackets, `* 1000`, and `range(250)` are not threshold comparisons. The exception set permits state/bounds 0–3. A separate frontend regression prevents the R3 caption copy.

### 9.2 R3

```text
hhi_fires = hhi is available AND hhi >= configured supplier_hhi
largest_fires =
    largest_supplier_share is available
    AND largest_supplier_share >= configured largest_supplier_share
fired = hhi_fires OR largest_fires
```

Missing largest-supplier data never borrows `top_two_value_share`; it is represented as `"NOT_CALCULABLE"` in metrics. HHI may still independently fire, preserving the steel result.

### 9.3 R11

```text
fired =
    generic_capacity_reject context is true
    AND export/import value ratio is available
    AND ratio > configured generic_capacity_export_import_value_ratio
```

Equality at 50.00 does not fire. Missing ratio remains `DEGRADED`, `fired=False`, with no fallback estimate.

### 9.4 Competition

```text
warning_fires = post-entry capacity / downside demand > configured warning
passes_default_warning = NOT warning_fires
```

Equality at 1.25 passes the default warning gate, exactly preserving methodology §7.5.

### 9.5 Kmin and bands

K/U/D\* calculations are unchanged. `publication_allowed` exactly preserves the current conjunction: D\* exists, K is at least configured Kmin, no hard gate is unresolved, and no known dimension has state 3. `route_band` retains inclusive configured maxima and falls through to greenfield only above the major/JV maximum.

## 10. Exact production drafts

### 10.1 `scripts/check_threshold_literals.py` — complete new file

```python
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS_PATH = ROOT / "config" / "thresholds.v1.yaml"
SOURCE_DIR = ROOT / "src" / "ior_mvp"
EXEMPT_NUMERIC_VALUES = {0.0, 1.0, 2.0, 3.0}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    value: float

    def render(self) -> str:
        return f"{self.path}:{self.line}:{self.value:g}"


def collect_numeric_values(value: Any) -> set[float]:
    if isinstance(value, bool):
        return set()
    if isinstance(value, (int, float)):
        return {float(value)}
    if isinstance(value, dict):
        values: set[float] = set()
        for nested in value.values():
            values.update(collect_numeric_values(nested))
        return values
    if isinstance(value, list):
        values = set()
        for nested in value:
            values.update(collect_numeric_values(nested))
        return values
    return set()


def scan_source(
    source: str,
    *,
    path: str,
    threshold_values: set[float],
) -> list[Finding]:
    tree = ast.parse(source, filename=path)
    findings: set[Finding] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for operand in (node.left, *node.comparators):
            if not isinstance(operand, ast.Constant):
                continue
            value = operand.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            numeric_value = float(value)
            if (
                numeric_value in threshold_values
                and numeric_value not in EXEMPT_NUMERIC_VALUES
            ):
                findings.add(
                    Finding(path=path, line=operand.lineno, value=numeric_value)
                )
    return sorted(findings)


def load_threshold_values(path: Path) -> set[float]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Threshold configuration must be a mapping: {path}")
    values = collect_numeric_values(payload)
    if not values:
        raise ValueError(f"Threshold configuration has no numeric values: {path}")
    return values


def scan_repository(
    source_dir: Path,
    threshold_path: Path,
    *,
    root: Path,
) -> tuple[list[Finding], int, int]:
    threshold_values = load_threshold_values(threshold_path)
    source_paths = sorted(source_dir.glob("*.py"))
    findings: list[Finding] = []
    for source_path in source_paths:
        display_path = (
            source_path.relative_to(root).as_posix()
            if source_path.is_relative_to(root)
            else source_path.as_posix()
        )
        source = source_path.read_text(encoding="utf-8")
        findings.extend(
            scan_source(
                source,
                path=display_path,
                threshold_values=threshold_values,
            )
        )
    return sorted(findings), len(source_paths), len(threshold_values)


def main(
    source_dir: Path = SOURCE_DIR,
    threshold_path: Path = THRESHOLDS_PATH,
    root: Path = ROOT,
) -> int:
    try:
        findings, source_count, threshold_count = scan_repository(
            source_dir,
            threshold_path,
            root=root,
        )
    except (OSError, UnicodeError, SyntaxError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(
            f"THRESHOLD LITERAL SCAN ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    if findings:
        print("THRESHOLD LITERAL SCAN FAIL")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(
        "THRESHOLD LITERAL SCAN PASS "
        f"({source_count} Python files; {threshold_count} configured numeric values)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

After the exact configuration edit, clean output is expected to report 13 Python files and 23 unique configured numeric values. Evidence must record observed output rather than copy that expectation.

### 10.2 `config/thresholds.v1.yaml` — exact governed change

Exact metadata replacement:

```yaml
metadata:
  artifact: industrial-opportunity-thresholds
  version: "1.1.0"
  effective_date: "2026-09-02"
  authority: "Industrial Opportunity Resolution Methodology, Appendix B"
  status: frozen_for_demo_cycle
  change_gate: "methodology-owner approval + golden-case regression"
```

Exact resulting R11 block:

```yaml
  R11:
    generic_capacity_export_import_value_ratio: 50
    downside_cost_premium_over_import_parity: 0.25
    rationale: "Economic exclusion absent verified strategic externality; established exports above the configured import ratio warn against generic capacity support."
    sector_scope: all
    revision_date: "2026-09-02"
```

All other lines in the YAML remain unchanged. For this exact draft, the Planner's advisory estimate is:

```text
SHA-256 32d868f9506f325e980f3363079031a75534d3829b30131548c2e6d36a23d261
Bytes   3,700
```

This estimate is not an acceptance constant or authority. Acceptance uses the reviewed YAML diff and the entry generated by `scripts/build_manifests.py`. Stop if `git diff -- config/thresholds.v1.yaml` contains any line outside the metadata `version`/`effective_date` changes and the exact R11 block above. A mismatch with the advisory estimate alone is not a stop condition.

### 10.3 `src/ior_mvp/rules.py`

Add immediately after `quantity_contribution_share`:

```python
NOT_CALCULABLE = "NOT_CALCULABLE"


def r1d_fires(
    positive_years: list[int],
    rule_config: dict[str, Any],
) -> bool:
    if not positive_years:
        return False
    window_span_years = max(positive_years) - min(positive_years)
    return (
        len(positive_years) >= int(rule_config["positive_observed_years"])
        and window_span_years < int(rule_config["window_years"])
    )


def r2_fires(
    delta_ln_quantity: float,
    contribution_share: float,
    quantity_growth: float,
    rule_config: dict[str, Any],
) -> bool:
    positive_quantity_required = bool(
        rule_config["require_positive_quantity_growth"]
    )
    return (
        (not positive_quantity_required or delta_ln_quantity > 0)
        and contribution_share
        >= float(rule_config["minimum_quantity_contribution_share"])
        and quantity_growth >= float(rule_config["minimum_quantity_cagr"])
    )


def r3_fires(
    hhi: float | None,
    largest_supplier_share: float | None,
    rule_config: dict[str, Any],
) -> bool:
    hhi_fires = (
        hhi is not None and hhi >= float(rule_config["supplier_hhi"])
    )
    largest_supplier_fires = (
        largest_supplier_share is not None
        and largest_supplier_share
        >= float(rule_config["largest_supplier_share"])
    )
    return hhi_fires or largest_supplier_fires


def r11_generic_capacity_fires(
    generic_capacity_reject: bool,
    export_import_value_ratio: float | None,
    rule_config: dict[str, Any],
) -> bool:
    return bool(
        generic_capacity_reject
        and export_import_value_ratio is not None
        and export_import_value_ratio
        > float(rule_config["generic_capacity_export_import_value_ratio"])
    )
```

Replace the current R1-D Boolean construction with:

```python
    positive_years = [
        row["year"] for row in trade if row.get("imports_usd_m", 0) > 0
    ]
    r1d_fired = r1d_fires(positive_years, thresholds["R1_D"])
```

Inside R2, compute and use:

```python
        quantity_growth = latest["imports_kt"] / previous["imports_kt"] - 1
        r2_fired = r2_fires(
            delta_q,
            share,
            quantity_growth,
            thresholds["R2"],
        )
```

Replace the R3 `if supplier:` body with:

```python
    if supplier:
        r3_config = thresholds["R3"]
        hhi = supplier.get("partner_value_hhi")
        largest_supplier_share = supplier.get("largest_supplier_share")
        r3_fired = r3_fires(
            hhi,
            largest_supplier_share,
            r3_config,
        )
        results.append(
            _rule(
                "R3",
                "Supplier concentration",
                "FULL",
                r3_fired,
                "External supply is concentrated."
                if r3_fired
                else "Concentration threshold not met.",
                "Generate a resilience/diversification review, not an automatic localisation recommendation.",
                {
                    "hhi": hhi,
                    "hhi_threshold": float(r3_config["supplier_hhi"]),
                    "largest_supplier_share": (
                        largest_supplier_share
                        if largest_supplier_share is not None
                        else NOT_CALCULABLE
                    ),
                    "largest_supplier_threshold": float(
                        r3_config["largest_supplier_share"]
                    ),
                    "top_two_share": supplier.get("top_two_value_share"),
                },
            )
        )
```

Replace the R11 calculation and metrics with:

```python
    latest = trade[-1]
    export_import_ratio = latest.get("export_import_value_ratio")
    r11_config = thresholds["R11"]
    r11 = r11_generic_capacity_fires(
        bool(context.get("generic_capacity_reject")),
        export_import_ratio,
        r11_config,
    )
```

and:

```python
            {
                "export_import_value_ratio": export_import_ratio,
                "export_import_value_ratio_threshold": float(
                    r11_config["generic_capacity_export_import_value_ratio"]
                ),
            },
```

No result text, execution-state rule, or decision effect changes.

### 10.4 `src/ior_mvp/capability.py`

Insert after `effective_qualified_capacity`:

```python
def publication_allowed(
    d_star: float | None,
    known_weight_coverage: float,
    minimum_known_weight_coverage: float,
    unresolved_hard_gates: list[str],
    has_known_state_three: bool,
) -> bool:
    return (
        d_star is not None
        and known_weight_coverage >= minimum_known_weight_coverage
        and not unresolved_hard_gates
        and not has_known_state_three
    )
```

Replace only the current `route_publishable` expression:

```python
    route_publishable = publication_allowed(
        d_star,
        known_weight,
        kmin,
        unresolved,
        any(row["state"] == 3 for row in dimensions if row["known"]),
    )
```

No formula, rounding, hard-gate parsing, band label, or return field changes.

### 10.5 `src/ior_mvp/decision_engine.py`

Change the config import to:

```python
from .config import project_config, thresholds_config
```

Add before `_simulate_steel`:

```python
def competition_warning(
    post_entry_capacity_to_downside_demand: float,
    competition_config: dict[str, Any],
) -> bool:
    return post_entry_capacity_to_downside_demand > float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
```

At the beginning of `_simulate_steel`, after `inputs`, add:

```python
    thresholds = thresholds_config()
    competition_config = thresholds["competition"]
    warning_threshold = float(
        competition_config[
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
    incremental_upgrade_max = float(
        thresholds["capability"]["route_bands"]["incremental_upgrade_max"]
    )
```

After calculating `ratio`, add `warning_fires` and replace the competition mapping:

```python
    warning_fires = competition_warning(ratio, competition_config)
    competition = {
        "post_entry_capacity_to_downside_demand": round(ratio, 4),
        "warning_threshold": warning_threshold,
        "warning_fires": warning_fires,
        "passes_default_warning": not warning_fires,
        "displacement_m_sar": inputs["economics"]["national_value"][
            "displacement"
        ],
    }
```

Replace only the D\* comparison in `passes`:

```python
        and capability["d_star"] <= incremental_upgrade_max
```

### 10.6 `src/ior_mvp/genui.py`

At the top of `build_ui_manifest`, after `real`, derive the already-used R3 metrics:

```python
    r3_metrics = next(
        (
            row["metrics"]
            for row in analysis["rules"]
            if row["rule_id"] == "R3"
        ),
        {},
    )
```

Add one metric-grid prop while preserving existing props:

```python
                "supplier_concentration": r3_metrics,
```

### 10.7 `src/ior_mvp/static/app.js`

At base line 190, before `const metrics`, add:

```javascript
  const hhiThreshold = props.supplier_concentration?.hhi_threshold;
  const hhiNote = hhi == null
    ? "Not available in this snapshot"
    : hhiThreshold == null
      ? "Configured resilience threshold unavailable"
      : `Resilience review threshold: ${hhiThreshold.toFixed(2)}`;
```

Replace base line 192 exactly:

```javascript
    ["Supplier HHI", hhi == null ? "—" : hhi.toFixed(2), hhiNote],
```

No style, layout, locale, or other UI string changes.

### 10.8 CI and Makefile integration

In each Python job, immediately after `Scan prohibited files and secret patterns`, add a step named exactly `Reject embedded threshold literals`.

uv job:

```yaml
      - name: Reject embedded threshold literals
        run: uv run --locked --extra dev python scripts/check_threshold_literals.py
```

pip job:

```yaml
      - name: Reject embedded threshold literals
        run: python scripts/check_threshold_literals.py
```

In `Makefile`, immediately after the prohibited scanner in `ci`:

```make
	$(UV_RUN) python scripts/check_threshold_literals.py
```

No job topology, action version, permissions, matrix, or other command changes.

## 11. Exact test drafts

### 11.1 `tests/test_threshold_literals.py` — complete new file

```python
from __future__ import annotations

from pathlib import Path

from ior_mvp.config import PROJECT_ROOT
from scripts.check_threshold_literals import (
    Finding,
    SOURCE_DIR,
    THRESHOLDS_PATH,
    collect_numeric_values,
    main,
    scan_repository,
    scan_source,
)


def _write_thresholds(path: Path) -> None:
    path.write_text(
        "rules:\n"
        "  probe:\n"
        "    limit: 0.40\n",
        encoding="utf-8",
    )


def test_collect_numeric_values_recurses_and_excludes_strings_and_bools() -> None:
    payload = {
        "rules": {
            "ratio": 1.25,
            "nested": [50, {"share": 0.40}],
            "version": "1.25",
            "enabled": True,
        }
    }
    assert collect_numeric_values(payload) == {0.4, 1.25, 50.0}


def test_scan_source_flags_configured_comparison_literal() -> None:
    findings = scan_source(
        "def check(x: float) -> bool:\n"
        "    return x <= 0.40\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4},
    )
    assert findings == [
        Finding(
            path="src/ior_mvp/probe.py",
            line=2,
            value=0.4,
        )
    ]


def test_scan_source_checks_left_and_all_comparator_operands() -> None:
    findings = scan_source(
        "def check(x: float) -> bool:\n"
        "    return 0.40 < x < 1.25\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4, 1.25},
    )
    assert findings == [
        Finding(path="src/ior_mvp/probe.py", line=2, value=0.4),
        Finding(path="src/ior_mvp/probe.py", line=2, value=1.25),
    ]


def test_scan_source_exempts_state_and_formula_bounds_zero_to_three() -> None:
    findings = scan_source(
        "def valid(state: int) -> bool:\n"
        "    return 0 <= state <= 3\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.0, 1.0, 2.0, 3.0},
    )
    assert findings == []


def test_scan_source_ignores_configured_values_outside_comparisons() -> None:
    findings = scan_source(
        "LIMIT = 0.40\n"
        "WARNING = 1.25\n"
        "def check(x: float) -> bool:\n"
        "    return x <= LIMIT\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4, 1.25},
    )
    assert findings == []


def test_main_returns_one_and_reports_file_line_value(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "result = value <= 0.40\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 1
    assert "src/probe.py:1:0.4" in capsys.readouterr().out


def test_main_returns_zero_for_clean_sources(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "LIMIT = 0.40\n"
        "result = value <= LIMIT\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 0
    assert "THRESHOLD LITERAL SCAN PASS" in capsys.readouterr().out


def test_main_returns_two_for_invalid_yaml(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    threshold_path.write_text("rules: [", encoding="utf-8")
    (source_dir / "probe.py").write_text("value = 1\n", encoding="utf-8")

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 2
    assert "THRESHOLD LITERAL SCAN ERROR" in capsys.readouterr().err


def test_main_returns_two_for_python_parse_error(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "def broken(:\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 2
    assert "SyntaxError" in capsys.readouterr().err


def test_repository_has_no_embedded_threshold_comparison_literals() -> None:
    findings, source_count, threshold_count = scan_repository(
        SOURCE_DIR,
        THRESHOLDS_PATH,
        root=PROJECT_ROOT,
    )
    assert source_count > 0
    assert threshold_count > 0
    assert findings == []


def test_frontend_hhi_caption_uses_payload_threshold() -> None:
    source = (
        PROJECT_ROOT / "src" / "ior_mvp" / "static" / "app.js"
    ).read_text(encoding="utf-8")
    assert "Resilience review threshold: 0.25" not in source
    assert "props.supplier_concentration?.hhi_threshold" in source
```

`capsys` intentionally remains unannotated because it is a pytest fixture, not a public production function.

### 11.2 `tests/test_threshold_boundaries.py` — complete new file

```python
from __future__ import annotations

import pytest

from ior_mvp.capability import (
    evaluate_capability,
    publication_allowed,
    route_band,
)
from ior_mvp.config import thresholds_config
from ior_mvp.decision_engine import analyze, competition_warning
from ior_mvp.genui import build_ui_manifest
from ior_mvp.rules import (
    r1d_fires,
    r2_fires,
    r3_fires,
    r11_generic_capacity_fires,
)


@pytest.mark.parametrize(
    ("positive_years", "expected"),
    [
        ([2022, 2023], False),
        ([2021, 2022, 2023], True),
        ([2020, 2021, 2022, 2023], True),
    ],
)
def test_r1d_positive_year_count_boundary(
    positive_years: list[int],
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R1_D"]
    assert r1d_fires(positive_years, config) is expected


@pytest.mark.parametrize(
    ("positive_years", "expected"),
    [
        ([2020, 2021, 2022], True),
        ([2020, 2021, 2023], True),
        ([2020, 2021, 2024], False),
    ],
)
def test_r1d_window_span_boundary(
    positive_years: list[int],
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R1_D"]
    assert r1d_fires(positive_years, config) is expected


@pytest.mark.parametrize(
    ("share", "expected"),
    [
        (0.5999, False),
        (0.6000, True),
        (0.6001, True),
    ],
)
def test_r2_quantity_contribution_share_boundary(
    share: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=0.01,
            contribution_share=share,
            quantity_growth=0.05,
            rule_config=config,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("growth", "expected"),
    [
        (0.0499, False),
        (0.0500, True),
        (0.0501, True),
    ],
)
def test_r2_quantity_growth_boundary(
    growth: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=0.01,
            contribution_share=0.60,
            quantity_growth=growth,
            rule_config=config,
        )
        is expected
    )


@pytest.mark.parametrize("delta_ln_quantity", [-0.0001, 0.0])
def test_r2_requires_strictly_positive_quantity_change(
    delta_ln_quantity: float,
) -> None:
    config = thresholds_config()["rules"]["R2"]
    assert (
        r2_fires(
            delta_ln_quantity=delta_ln_quantity,
            contribution_share=0.60,
            quantity_growth=0.05,
            rule_config=config,
        )
        is False
    )


@pytest.mark.parametrize(
    ("hhi", "expected"),
    [
        (0.2499, False),
        (0.2500, True),
        (0.2501, True),
    ],
)
def test_r3_hhi_boundary(
    hhi: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(hhi, None, config) is expected


@pytest.mark.parametrize(
    ("largest_supplier_share", "expected"),
    [
        (0.4999, False),
        (0.5000, True),
        (0.5001, True),
    ],
)
def test_r3_largest_supplier_boundary(
    largest_supplier_share: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R3"]
    assert (
        r3_fires(None, largest_supplier_share, config) is expected
    )


def test_r3_largest_supplier_missing_is_not_a_trigger() -> None:
    config = thresholds_config()["rules"]["R3"]
    assert r3_fires(0.2499, None, config) is False


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (49.99, False),
        (50.00, False),
        (50.01, True),
    ],
)
def test_r11_export_import_value_ratio_boundary(
    ratio: float,
    expected: bool,
) -> None:
    config = thresholds_config()["rules"]["R11"]
    assert (
        r11_generic_capacity_fires(True, ratio, config) is expected
    )


@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        (0.6999, False),
        (0.7000, True),
        (0.7001, True),
    ],
)
def test_publication_allowed_kmin_boundary(
    coverage: float,
    expected: bool,
) -> None:
    capability_config = thresholds_config()["capability"]
    assert (
        publication_allowed(
            d_star=0.1,
            known_weight_coverage=coverage,
            minimum_known_weight_coverage=float(
                capability_config["minimum_known_weight_coverage"]
            ),
            unresolved_hard_gates=[],
            has_known_state_three=False,
        )
        is expected
    )


@pytest.mark.parametrize(
    ("states", "expected_coverage", "expected_publishable"),
    [
        (
            {
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
            },
            0.65,
            False,
        ),
        (
            {
                "feedstock_chemistry": 0,
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
            },
            0.70,
            True,
        ),
        (
            {
                "feedstock_chemistry": 0,
                "core_process_route": 0,
                "equipment_envelope": 0,
                "finishing_spec_control": 0,
                "qa_lab_metrology": 0,
                "utilities_ehs_permitting": 0,
            },
            0.75,
            True,
        ),
    ],
)
def test_evaluate_capability_integrates_kmin_with_profile_weights(
    states: dict[str, int],
    expected_coverage: float,
    expected_publishable: bool,
) -> None:
    result = evaluate_capability("coated_steel", states, [])
    assert result["known_weight_coverage"] == pytest.approx(
        expected_coverage
    )
    assert result["route_publishable"] is expected_publishable


@pytest.mark.parametrize(
    ("distance", "expected_code"),
    [
        (0.1999, "immediate_adjacency"),
        (0.2000, "immediate_adjacency"),
        (0.2001, "incremental_upgrade"),
        (0.3999, "incremental_upgrade"),
        (0.4000, "incremental_upgrade"),
        (0.4001, "major_line_or_jv"),
        (0.6499, "major_line_or_jv"),
        (0.6500, "major_line_or_jv"),
        (0.6501, "greenfield_likely"),
    ],
)
def test_dstar_route_band_boundaries(
    distance: float,
    expected_code: str,
) -> None:
    bands = thresholds_config()["capability"]["route_bands"]
    assert route_band(distance, bands)["code"] == expected_code


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (1.2499, False),
        (1.2500, False),
        (1.2501, True),
    ],
)
def test_competition_warning_boundary(
    ratio: float,
    expected: bool,
) -> None:
    config = thresholds_config()["competition"]
    assert competition_warning(ratio, config) is expected


def test_r3_metrics_expose_configured_thresholds() -> None:
    result = analyze("SAU-H0-721049", "public")
    r3 = next(row for row in result["rules"] if row["rule_id"] == "R3")
    config = thresholds_config()["rules"]["R3"]
    assert r3["metrics"]["hhi_threshold"] == config["supplier_hhi"]
    assert r3["metrics"]["largest_supplier_threshold"] == (
        config["largest_supplier_share"]
    )
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"


def test_r11_metrics_expose_configured_threshold() -> None:
    result = analyze("SAU-H0-390210", "public")
    r11 = next(
        row for row in result["rules"] if row["rule_id"] == "R11"
    )
    config = thresholds_config()["rules"]["R11"]
    assert r11["metrics"]["export_import_value_ratio_threshold"] == (
        config["generic_capacity_export_import_value_ratio"]
    )


def test_competition_payload_exposes_configured_warning() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    config = thresholds_config()["competition"]
    assert result["competition"]["warning_threshold"] == (
        config["post_entry_capacity_to_downside_demand_warning"]
    )
    assert result["competition"]["warning_fires"] is False
    assert result["competition"]["passes_default_warning"] is True


def test_metric_grid_receives_r3_threshold_metrics() -> None:
    analysis = analyze("SAU-H0-721049", "public")
    manifest = build_ui_manifest(analysis)
    metric_grid = next(
        component
        for component in manifest["components"]
        if component["type"] == "metric_grid"
    )
    r3 = next(
        row for row in analysis["rules"] if row["rule_id"] == "R3"
    )
    assert metric_grid["props"]["supplier_concentration"] == r3["metrics"]
```

The coated-steel profile has weights in increments of 0.05, so exact constructed coverages 0.6999 and 0.7001 are impossible. The pure predicate supplies those exact boundary points. The integration matrix supplies exact reachable values immediately below/equal/above Kmin: 0.65, 0.70, 0.75. The exact 0.70 set is feedstock 0.05 + core process 0.20 + equipment 0.20 + finishing 0.15 + QA 0.10.

### 11.3 `tests/test_rules.py` — exact resulting changes

Add:

```python
from copy import deepcopy
```

Replace `test_pp_generic_capacity_warning_fires` with:

```python
def test_pp_generic_capacity_warning_fires() -> None:
    rules = evaluate_rules(get_public_case("SAU-H0-390210"))
    r11 = by_id(rules, "R11")
    config = thresholds_config()["rules"]["R11"]
    assert r11["fired"] is True
    assert r11["metrics"]["export_import_value_ratio"] == pytest.approx(
        50.6
    )
    assert r11["metrics"]["export_import_value_ratio_threshold"] == (
        config["generic_capacity_export_import_value_ratio"]
    )
```

Add after it:

```python
def test_r11_missing_ratio_is_degraded_and_does_not_fire() -> None:
    r11 = by_id(
        evaluate_rules(get_public_case("SAU-H0-721049")),
        "R11",
    )
    assert r11["execution"] == "DEGRADED"
    assert r11["fired"] is False
    assert r11["metrics"]["export_import_value_ratio"] is None


def test_r3_hhi_path_fires_when_largest_supplier_is_not_calculable() -> None:
    r3 = by_id(
        evaluate_rules(get_public_case("SAU-H0-721049")),
        "R3",
    )
    assert r3["fired"] is True
    assert r3["metrics"]["hhi"] == pytest.approx(0.36)
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"
    assert r3["metrics"]["top_two_share"] == pytest.approx(0.763)


def test_r3_does_not_substitute_top_two_share_for_largest_supplier() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    supplier = case["supplier_metrics_2024"]
    supplier["partner_value_hhi"] = 0.2499
    supplier["top_two_value_share"] = 0.9999
    supplier.pop("largest_supplier_share", None)

    r3 = by_id(evaluate_rules(case), "R3")

    assert r3["fired"] is False
    assert r3["metrics"]["largest_supplier_share"] == "NOT_CALCULABLE"


def test_r3_largest_supplier_path_uses_largest_supplier_metric() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    supplier = case["supplier_metrics_2024"]
    supplier["partner_value_hhi"] = 0.2499
    supplier["largest_supplier_share"] = 0.5000

    r3 = by_id(evaluate_rules(case), "R3")

    assert r3["fired"] is True
    assert r3["metrics"]["largest_supplier_share"] == pytest.approx(0.50)


def test_r4_full_rule_is_explicitly_disabled_on_annual_snapshots() -> None:
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        r4f = by_id(evaluate_rules(get_public_case(opportunity_id)), "R4-F")
        assert r4f["execution"] == "DISABLED"
        assert r4f["fired"] is None
        assert "Partner-month" in r4f["result"]
```

Replace the versioned-config test with:

```python
def test_threshold_is_loaded_from_versioned_config() -> None:
    config = thresholds_config()
    assert config["metadata"]["version"] == "1.1.0"
    assert config["metadata"]["effective_date"] == "2026-09-02"
    assert config["rules"]["R2"][
        "minimum_quantity_contribution_share"
    ] == pytest.approx(0.60)
    assert config["rules"]["R11"][
        "generic_capacity_export_import_value_ratio"
    ] == 50
    assert config["metadata"]["status"] == "frozen_for_demo_cycle"
```

### 11.4 `tests/test_ci_contract.py` — exact changed code

In `test_each_python_job_runs_every_required_gate`, use:

```python
    required_fragments = (
        "python scripts/check_prohibited_files.py",
        "python scripts/check_threshold_literals.py",
        "python -m compileall -q src scripts tests",
        "node --check src/ior_mvp/static/app.js",
        "python scripts/verify_integrity.py",
        "pytest -q",
        "python scripts/demo_smoke.py",
    )
```

Add:

```python
@pytest.mark.parametrize(
    ("job_name", "expected_command"),
    [
        (
            "uv-gates",
            "uv run --locked --extra dev "
            "python scripts/check_threshold_literals.py",
        ),
        (
            "pip-gates",
            "python scripts/check_threshold_literals.py",
        ),
    ],
)
def test_threshold_literal_scan_immediately_follows_prohibited_scan(
    job_name: str,
    expected_command: str,
) -> None:
    steps = _workflow()["jobs"][job_name]["steps"]
    prohibited_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Scan prohibited files and secret patterns"
    )
    threshold_step = steps[prohibited_index + 1]
    assert threshold_step == {
        "name": "Reject embedded threshold literals",
        "run": expected_command,
    }
```

No existing CI assertion is weakened.

## 12. UI behavior

`renderMetricGrid` still shows Supplier HHI to two decimal places. Its note uses the configured `hhi_threshold` from the R3 rule metrics. If HHI is absent, it retains “Not available in this snapshot.” If HHI exists but the threshold payload is missing, it shows “Configured resilience threshold unavailable”; it never falls back to a literal. No CSS, DOM structure, keyboard behavior, locale content, or bidirectional layout changes.

## 13. Failure, unknown-input, security, and concurrency behavior

### Failure behavior

- Missing threshold key: normal `KeyError` fails the request/test; no default value masks malformed governance.
- Missing/unreadable/malformed YAML or malformed Python in the validator: stderr diagnostic and exit 2.
- Embedded configured comparison literal: sorted findings and exit 1.
- Hash mismatch before approved regeneration: expected integrity failure; do not “repair” it early.
- Unexpected generated data-manifest change: stop and escalate; do not accept or manually edit generated entries.
- Golden result change: stop under Core 09 §8; do not alter the expectation.

### Unknown/missing input

- R3 missing largest-supplier share: `"NOT_CALCULABLE"` and no largest-supplier trigger; HHI remains independent.
- R3 missing supplier mapping entirely: existing `DISABLED`, `fired=None`.
- R11 missing ratio: existing `DEGRADED`, `fired=False`, ratio `None`.
- K=0, K below Kmin, unresolved hard gate, or known state 3: no published route band, unchanged.
- UI missing threshold field: explicit unavailable text, no inferred value.

### Privacy/security

No new external call, credential, secret, personal record, or protected dataset is introduced. The validator reads only repository Python and threshold YAML. Findings expose only relative path, line, and numeric value. Existing prohibited-file/secret scanning remains first in each Python job.

### Concurrency

None. Config loading is existing process-local cached behavior; predicate calls and validator scans are deterministic and single-process. GitHub's existing workflow concurrency policy is unchanged.

## 14. Versioning, integrity, and compatibility

- Configuration semantic version: `1.0.0` → `1.1.0` because a methodology-backed operating key is added without changing an existing key/value.
- Effective/revision date: `2026-09-02`, confirmed as the WSL generation date.
- Existing threshold values and strictness remain unchanged.
- Sensitivity proof: R11 49.99/50.00/50.01, all other boundary matrices, and unchanged A/A-S/B/B-S outcomes.
- Owner approval basis: the owner's 2026-09-02 completion-build mandate, already recorded in ADR-005/context; the Supervisor must confirm plan approval before the config edit.
- `authority_hashes.json` is changed only by `scripts/build_manifests.py`.
- Manifest Markdown table is manually synchronised from the generated JSON because the script does not edit the Markdown.
- Raw analysis and GenUI contracts are additive. Existing field names and types remain unchanged, except `warning_threshold` is now sourced from config while retaining the same numeric type/value.

## 15. Acceptance criteria

- [ ] Branch/base exactly match §4 and Supervisor plan approval is recorded.
- [ ] Only the approved paths plus the conditional generated `snapshot_manifest.json` date change differ.
- [ ] `git diff -- config/thresholds.v1.yaml` shows only the planned metadata `version`/`effective_date` changes and the R11 block in §10.2.
- [ ] R3 never uses `top_two_value_share` as largest-supplier share.
- [ ] Missing largest-supplier input is visibly `NOT_CALCULABLE`.
- [ ] R11 equality at 50.00 does not fire; 50.01 does.
- [ ] Competition equality at 1.2500 does not warn; 1.2501 does.
- [ ] Kmin and all D\* boundaries match the exact matrix.
- [ ] `scripts/check_threshold_literals.py` returns 0 on the repository and 1/2 in its test fixtures.
- [ ] Both CI Python jobs and `make ci` run the validator immediately after the prohibited scan.
- [ ] `app.js` contains no `Resilience review threshold: 0.25`.
- [ ] `rg -n '0\.40|1\.25|>\s*50|Resilience review threshold: 0\.25' src/ior_mvp -g '*.py' -g 'app.js'` returns no match.
- [ ] Explicit R4-F-disabled test passes.
- [ ] Steel public remains `INVESTIGATE`.
- [ ] Steel simulated remains `ADVANCE`, route 5, with 57.509 kt effective capacity, 46.491 kt gap, D\* 0.2667, S\* 18m, national value 198m, and no competition warning.
- [ ] PP public remains `REJECT`, route 0, and R11 fires at observed ratio 50.6.
- [ ] PP simulation remains `REJECT`.
- [ ] `sha256sum config/thresholds.v1.yaml` equals the `config/thresholds.v1.yaml` SHA-256 entry in `authority_hashes.json`.
- [ ] The Manifest §11 thresholds row is copied from the generated `authority_hashes.json` entry, including its hash and byte count.
- [ ] Snapshot manifest differs only in `generated_on`, if it differs.
- [ ] Required integrity, full pytest, and smoke commands pass after regeneration.
- [ ] Supervisor review and different-model independent review have zero unresolved findings.
- [ ] Final PR-head CI is green in uv 3.12, uv 3.14, pip 3.12, and Docker jobs.
- [ ] No self-approval or self-merge.

## 16. Documentation and traceability updates

### ADR-005

Change status exactly to:

```text
**Status:** Accepted 2026-09-02.
```

Update its Decision text to name:

```text
rules.R11.generic_capacity_export_import_value_ratio
```

Record that the owner mandate is the approval basis and that sensitivity is demonstrated by strict-boundary tests plus unchanged golden outcomes. Do not claim CI/review evidence until observed.

Use this exact authority-change justification in the reviewed PR description:

```text
Authority change — thresholds 1.1.0: add
rules.R11.generic_capacity_export_import_value_ratio = 50 for sector_scope
all. This does not invent or tune a policy value; it makes the
methodology §14.2 “more than 50×” generic-capacity test explicit in the
versioned operating configuration. Existing thresholds are unchanged.
Sensitivity is proven at 49.99 / 50.00 / 50.01, with equality not firing,
and by the unchanged steel/public, steel/simulated, PP/public and
PP/simulated golden outcomes. The owner’s 2026-09-02 completion-build
mandate is the recorded methodology-owner approval basis.
```

### Requirements traceability

After implementation but before execution, point rows to the exact source/tests/validator and use `IMPLEMENTED`. After actual final-head CI evidence is recorded, promote these rows to `TESTED`:

| Row | Final implementation/test evidence pointer |
|---|---|
| FR-002 | `rules.py`, `decision_engine.py`, `thresholds.v1.yaml`; `test_threshold_boundaries.py`; `check_threshold_literals.py`; S02 evidence. |
| FR-025 | `r11_generic_capacity_fires`; R11 49.99/50/50.01 and PP golden. |
| FR-033 | `publication_allowed`; exact Kmin predicate and profile integration tests. |
| FR-034 | `route_band`; three band-edge below/equal/above matrices. |
| FR-044 | `competition_warning`; payload provenance and 1.2499/1.2500/1.2501 tests. |
| INV-07 | AST validator in local/hosted CI plus no-literal repository test. |
| TL-03 | R1-D boundary, explicit R3 paths, explicit R4-F-disabled, R11 tests. |
| TL-08 | Complete S02 boundary matrix in `test_threshold_boundaries.py`. |
| GATE-C | All rules/goldens plus config/validator evidence. |

Do not use `COMPLETE` before merge. If the repository applies `VALIDATED` at independent-review time, the Supervisor may promote from `TESTED` only after recording that verdict; otherwise retain the established S01 convention and let S05 perform final validation promotion.

### KL-01–KL-03

Do not remove them from Open while implementation or CI is pending. After the current PR head is green and reviews have zero findings, move each to Closed with:

- resolution naming the exact code/validator/test;
- evidence pointing to `.workflow/slices/S02-threshold-governance/test_evidence.md` and the actual CI run;
- closure wording “Effective on squash merge of S02” plus the actual linked PR.

The Supervisor records the post-merge state; the Implementer does not pre-claim closure.

### Workflow records

- `implementation_log.md`: branch/base, data classification, pre-existing status inventory, exact files/behavior changed, owner/config gate basis, generated-file audit, deviations, and assumptions.
- `test_evidence.md`: every red and green command with actual exit/output, pre-manifest suite result, one generator invocation, hash/diff audit, final local gates, review records, and actual CI URL/head/job outcomes.
- Never write future output, fake pass counts, or placeholder URLs.

## 17. Manifest regeneration and generated-on rule

Run `scripts/build_manifests.py` **exactly once**, only after:

1. exact YAML/config review is complete;
2. focused tests pass;
3. the threshold validator is clean;
4. the complete pytest suite passes against version 1.1.0;
5. demo smoke confirms unchanged outcomes.

After the one invocation:

1. `docs/authority/authority_hashes.json` may change only:
   - `generated_on` to `2026-09-02`;
   - the `config/thresholds.v1.yaml` SHA-256 and byte count computed by the script over the reviewed file.
2. `data/manifests/snapshot_manifest.json` may change only:
   - `generated_on` to `2026-09-02`.
3. If snapshot-manifest `generated_on` is the sole diff, retain it as an acceptable generator-produced non-semantic companion, record it, and do not edit it manually.
4. If any snapshot path/hash/bytes/policy/version changes, stop. Do not stage, accept, regenerate, or “fix” it.
5. Run `sha256sum config/thresholds.v1.yaml` and require it to equal the generated JSON entry.
6. Copy the generated JSON entry's SHA-256 and byte count into only the `config/thresholds.v1.yaml` row in Manifest §11.

Then run integrity. A failure is investigated; hashes are never regenerated again merely to obtain green.

The §10.2 predicted SHA-256 and byte count remain advisory only; a difference from that estimate is not a failure when the YAML diff contains only the planned lines and the generated JSON, `sha256sum`, and Manifest row agree.

## 18. Rollback and recovery

Before commit, if the authority change is rejected, apply the reviewed inverse patch to restore together:

- YAML metadata and R11 block;
- source references that require the new key;
- generated authority JSON;
- Manifest §11 row;
- generated snapshot-manifest date;
- tests/docs that assert 1.1.0.

Do not leave config 1.0.0 paired with 1.1.0 hashes or vice versa. Do not use `git reset --hard`, `git checkout --`, or unreviewed manifest regeneration.

After merge, rollback is one Supervisor-controlled `git revert` of the S02 squash commit, followed by the complete integrity/pytest/smoke/CI gates. This atomically reverts code, config, hashes, table row, generated date, tests, and records without rewriting history.

If only non-governed Python/JavaScript code needs correction after manifest generation, fix it test-first; do not rerun manifests because governed bytes did not change. If any YAML wording/value must change after the one generator run, stop for a renewed owner decision and revised plan rather than silently running the generator twice.

## 19. Step-by-step implementation tasks

### Task 0: Approval and preflight

**Files:** read-only.

**Interfaces:** consumes Supervisor `PLAN_APPROVED`; produces verified branch/base/status/scope inventory.

- [ ] Read the Supervisor plan review. Stop unless it explicitly approves this exact plan.
- [ ] Run the short commands:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git rev-parse HEAD"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git branch --show-current"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git status --short"
```

- [ ] Require base `432af8af1fa88a2258a0fd8d825a6855e408270f` and branch `slice/S02-threshold-governance`.
- [ ] Distinguish Supervisor-owned pre-existing records from Implementer edits.
- [ ] Confirm the data classification and run the existing prohibited scanner.

**Confirm:** approval, branch, and base.
**Validate:** no pre-existing file is overwritten or misattributed.
**Test:** prohibited scan exits 0.

### Task 1: Build the AST validator test-first and prove the existing defect

**Files:** create `tests/test_threshold_literals.py`, then `scripts/check_threshold_literals.py`.

**Interfaces:** exact functions and exit codes in §10.1/§11.1.

- [ ] Transcribe `tests/test_threshold_literals.py`.
- [ ] Run the focused test before creating the script:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_threshold_literals.py -q"
```

Expected RED: collection fails because `scripts.check_threshold_literals` does not exist. Fix only transcription/import errors until the failure is for the missing implementation.

- [ ] Transcribe `scripts/check_threshold_literals.py`.
- [ ] Run the pure fixture tests while excluding the repository/frontend assertions:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_threshold_literals.py -q -k 'not repository_has_no_embedded and not frontend_hhi_caption'"
```

Expected GREEN: pure recursion, detection, exemptions, and 0/1/2 exits pass.

- [ ] Run the real validator before source fixes:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/check_threshold_literals.py"
```

Expected RED: exit 1 with exactly the three comparison findings in §5. Also run the frontend test and observe its expected caption failure.

**Confirm:** the validator follows the exact AST/YAML algorithm.
**Validate:** current defects are caught without formula false positives.
**Test:** synthetic `x <= 0.40`, main exit 0/1/2, actual repository red, frontend red.

### Task 2: Externalise rule/capability/competition thresholds test-first

**Files:** create `tests/test_threshold_boundaries.py`; modify `tests/test_rules.py`, `rules.py`, `capability.py`, `decision_engine.py`, `thresholds.v1.yaml`, and ADR-005.

**Interfaces:** predicates and metrics in §8–§11.

- [ ] Add the boundary/rule tests before production edits.
- [ ] Run them and verify RED for missing predicate imports, wrong R3 semantics, missing R11 key/version, and missing metric fields:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_threshold_boundaries.py tests/test_rules.py -q"
```

- [ ] Update ADR-005 status/key/approval basis before changing governed YAML.
- [ ] Apply the exact YAML edit in §10.2. Do not alter any other value.
- [ ] Add the pure predicates and replace only the specified orchestration blocks.
- [ ] Run the engine-focused rule/boundary tests to GREEN, leaving the deliberately red metric-grid integration test for Task 3.
- [ ] Run existing capability and golden tests:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_threshold_boundaries.py tests/test_rules.py tests/test_capability_economics.py tests/test_golden_cases.py -q -k 'not metric_grid_receives_r3_threshold_metrics'"
```

- [ ] If only the Kmin 0.70 integration case fails and the observed coverage prints as `0.7` but compares below Kmin because of floating-point precision, stop, record the full observed value, and report `DONE_WITH_CONCERNS`. Do not alter `publication_allowed`, Kmin, or the expected Boolean.
- [ ] Run the validator; it must now return 0 for Python.

Integrity is expected to fail until Task 6 and is not “fixed” here.

**Confirm:** one new config key, unchanged existing values/formulas.
**Validate:** strict/equal semantics and response provenance.
**Test:** every exact boundary matrix plus unchanged goldens.

### Task 3: Remove the frontend threshold copy

**Files:** modify `genui.py`, `app.js`; use existing red frontend test and metric-grid integration test.

- [ ] Confirm the frontend static test and metric-grid test are red for the missing payload path.
- [ ] Apply §10.6–§10.7 exactly.
- [ ] Run:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev pytest tests/test_threshold_literals.py::test_frontend_hhi_caption_uses_payload_threshold tests/test_threshold_boundaries.py::test_metric_grid_receives_r3_threshold_metrics -q"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- node --check src/ior_mvp/static/app.js
```

- [ ] Run the exact `rg` acceptance scan from §15.

**Confirm:** configured R3 metrics reach `renderMetricGrid`.
**Validate:** missing-payload fallback contains no numeric default.
**Test:** frontend static contract, GenUI integration, JavaScript syntax.

### Task 4: Wire local and hosted CI test-first

**Files:** modify `tests/test_ci_contract.py`, `.github/workflows/ci.yml`, `Makefile`.

- [ ] Apply only the test changes in §11.4.
- [ ] Run `tests/test_ci_contract.py` and observe RED because the step is absent.
- [ ] Add the exact two workflow steps and Makefile line.
- [ ] Run the CI contract to GREEN.
- [ ] Dry-run Make:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- make -n ci
```

Require prohibited scan → threshold scan → compile → JavaScript → integrity → pytest → smoke.

**Confirm:** both Python jobs use the same validator.
**Validate:** exact immediate ordering and no optional failure escape.
**Test:** CI static contract and Make dry run.

### Task 5: Complete pre-manifest regression

**Files:** append actual observations to implementation/evidence records; update traceability implementation pointers without claiming pass.

- [ ] Create ignored `.workflow/logs/s02_pre_manifest.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev python scripts/check_threshold_literals.py
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev pytest -q
PYTHONPATH=src "$HOME/.local/bin/uv" run --locked --extra dev python scripts/demo_smoke.py
```

- [ ] Run it detached under `.workflow/logs/` and read the complete log after completion.
- [ ] Require full pytest and smoke to pass on changed config 1.1.0.
- [ ] If any test or golden fails, fix the implementation—not the expectation—and rerun the pre-manifest suite. Do not run `build_manifests.py`.
- [ ] Run and record `git diff -- config/thresholds.v1.yaml`; require that it contains only the planned metadata `version`/`effective_date` lines and exact R11 block. Stop on any other YAML line. The §10.2 predicted hash/bytes are advisory and are not a stop condition.
- [ ] Put the exact authority-change justification from §16 into the reviewed PR draft/description record.
- [ ] Once the planned-only YAML diff, clean threshold validator, full pytest pass, and demo-smoke pass on 1.1.0 have all been observed and recorded, the Implementer is pre-authorised to proceed to Task 6 and run `scripts/build_manifests.py` exactly once; no mid-task Supervisor confirmation is required.

**Confirm:** changed config has passed full behavioral regression.
**Validate:** integrity has not been bypassed or regenerated early.
**Test:** validator, full pytest, smoke.

### Task 6: Regenerate hashes once and synchronise Manifest §11

**Files:** generator writes both JSON manifests; manually modify only the Manifest thresholds row.

- [ ] Reconfirm the recorded Task 5 pre-authorisation conditions: planned-only YAML diff, clean threshold validator, full pytest pass, and demo-smoke pass on 1.1.0.
- [ ] Run exactly once:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "PYTHONPATH=src ~/.local/bin/uv run --locked --extra dev python scripts/build_manifests.py"
```

- [ ] Inspect both generated diffs immediately:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- docs/authority/authority_hashes.json"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff -- data/manifests/snapshot_manifest.json"
```

- [ ] Enforce §17 exactly. Stop if `snapshot_manifest.json` changes anything except `generated_on`, or if an authority entry other than `generated_on` and the thresholds hash/bytes changes. Do not stop solely because the generated thresholds hash/bytes differ from the advisory estimate.
- [ ] Run `sha256sum config/thresholds.v1.yaml` and require it to equal the generated `authority_hashes.json` thresholds entry.
- [ ] Copy that JSON entry's hash and byte count into only the Manifest §11 thresholds row.
- [ ] Run integrity and record actual output.

**Confirm:** one generator invocation.
**Validate:** generated JSON and human table agree; snapshot entries unchanged.
**Test:** `verify_integrity.py` exits 0.

### Task 7: Complete documentation and self-audit

**Files:** traceability, known limitations lifecycle text, implementation log, test evidence, ADR.

- [ ] Apply §16 without fake CI/review outcomes.
- [ ] Record actual pre-manifest, generation, hash, and integrity evidence.
- [ ] Run `git diff --check`, status, and exact path inventory.
- [ ] Audit no prohibited/out-of-scope path or secret is included.
- [ ] Perform al-muhasibi self-audit: requested behavior vs implementation, verified outputs vs assumptions, exact YAML/hash, strictness, unknown paths, golden preservation, and rollback pairing.

**Confirm:** documentation matches observed state.
**Validate:** statuses do not exceed evidence.
**Test:** docs/static contracts and hygiene checks.

### Task 8: Supervisor and independent review

**Files:** complete current diff, read-only review; Implementer fixes only after findings.

- [ ] Implementer hands off without saying APPROVE.
- [ ] Supervisor reviews methodology fidelity, exact scope, generated diff, tests, API compatibility, and evidence.
- [ ] Fix each finding test-first; rerun affected tests.
- [ ] Dispatch the different-model independent Reviewer only on the fixed/current diff.
- [ ] A rejection is fixed before a new review; never rerun unchanged work until it “approves.”
- [ ] If any finding requires YAML change after generation, stop for owner/plan revision under §18.

**Confirm:** reviewer identities/models recorded.
**Validate:** zero unresolved findings on current files.
**Test:** review verdict is independent evidence, never self-approval.

### Task 9: Final local gates and intended-path staging

- [ ] Stage only explicit approved paths after Supervisor direction; never use `git add .`.
- [ ] Include the conditional snapshot manifest only after its one-line audit.
- [ ] Create an ignored detached final-validation script containing:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/barami/projects/industrial-opportunity-resolution-mvp

make ci

pip_env='.workflow/logs/s02-pip-venv'
python3 -m venv --clear "$pip_env"
source "$pip_env/bin/activate"
python -m pip install -e ".[dev]"
python scripts/check_prohibited_files.py
python scripts/check_threshold_literals.py
python -m compileall -q src scripts tests
node --check src/ior_mvp/static/app.js
PYTHONPATH=src python scripts/verify_integrity.py
PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/demo_smoke.py
deactivate

docker build --file Dockerfile --tag industrial-opportunity-resolution-mvp:s02-local .
```

- [ ] Run detached and inspect the complete log.
- [ ] Run short final hygiene:

```powershell
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff --check"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git status --short"
wsl -d Ubuntu --cd /home/barami/projects/industrial-opportunity-resolution-mvp -- bash -lc "git diff --cached --name-only"
```

**Confirm:** intended staged set only.
**Validate:** uv, clean pip, Docker, integrity, tests, smoke, scanners.
**Test:** all final local gates exit 0 on the reviewed diff.

### Task 10: PR, current-head CI, conditional closure, and merge gate

- [ ] Only the Supervisor authorises commit/push/PR.
- [ ] Require green current-head checks:
  - `uv / Python 3.12`
  - `uv / Python 3.14`
  - `pip / Python 3.12`
  - `Docker image build`
- [ ] Record actual run URL, PR head SHA, job names/outcomes, and sanitized outputs.
- [ ] Promote traceability to `TESTED` only with actual evidence.
- [ ] Move KL-01–KL-03 using close-on-merge wording only after current-head green/review evidence; use the actual linked PR/run.
- [ ] Require final CI again if evidence-only promotion changes the PR head.
- [ ] Only the Supervisor may squash merge after all gates; record the merge commit before `COMPLETE`.

**Confirm:** evidence refers to the final PR head.
**Validate:** no cancelled/skipped job is treated as green.
**Test:** hosted CI 4/4 and post-merge integrity as directed.

## 20. Exact command classification

### Short interactive

- Branch/base/status/diff/path inspection.
- Existing/final prohibited scanner.
- Focused pytest files/node IDs.
- AST validator CLI.
- JavaScript syntax check.
- `make -n ci`.
- `rg` literal scan.
- SHA-256/byte verification.
- The single `build_manifests.py` invocation.
- Integrity verification.
- `git diff --check`.

### Detached long-running

- Full pre-manifest pytest + smoke script.
- Final `make ci` + clean pip compatibility + Docker build script.
- GitHub Actions after push/PR.

All transient scripts, virtual environments, and logs stay under ignored `.workflow/logs/` and never enter Git.

## 21. Explicit non-goals

- No threshold value tuning or sector calibration.
- No new R1-F, R4-F, R5, R6, R7, or R8 evaluator.
- No R5 `NOT_CALCULABLE` payload work (S03).
- No scenario-schema, conditions, kill-condition, or opportunity-dispatch work (S04).
- No methodology/core/DOCX/data-fixture edit.
- No sector/evidence policy edit.
- No golden expectation edit.
- No CSS or visual redesign.
- No live connector, authentication, authorization, deployment, CRM, chat, dashboard, or portfolio work.
- No generic scanner of JavaScript numeric constants beyond the exact R3 caption regression.

## 22. Skills used

- Read and used `superpowers/writing-plans`: exact paths, interfaces, complete drafts, bite-sized tasks, no placeholders, explicit commands, and self-review.
- Read and applied `superpowers/test-driven-development`: every production behavior starts with a test, observed RED must be for the intended missing/defective behavior, then minimal GREEN and regression.
- Read `superpowers/using-superpowers`; its `SUBAGENT-STOP` applies to this dispatched Planner task.
- Inspected `C:\Users\Admin\.cursor\skills-cursor\` and `C:\Users\Admin\.cursor\skills\`.
- **No applicable installed skill found after discovery beyond writing-plans and test-driven-development.**

## 23. Open questions and owner decisions

No unresolved policy value or methodology interpretation remains:

- The key name and value are supplied by the Supervisor context and authoritative methodology.
- Strictness is explicit.
- The owner mandate is recorded as approval basis.
- The rationale text in §10.2 is a source-faithful explanation, not a new policy value.
- The change date is confirmed as 2026-09-02.

Operational issue for the Supervisor, not a policy question: the pre-existing S01/control-record worktree differs from the initial-status expectation. Task 0 must preserve and re-inventory it before implementation/staging.

## 24. Planner self-review (al-muhasibi)

- **Spec coverage:** every required objective, requirement ID, source defect, exact validator rule, predicate, API field, UI change, CI/Make integration, boundary value, version/hash step, documentation row, rollback, and non-goal maps to a section/task.
- **Authority:** no existing value or strictness changes; only the supplied R11 key is added; DOCX statements were checked directly and agree with mirror/core.
- **Type consistency:** function names/signatures used by production drafts and tests match exactly.
- **TDD:** validator, predicates, frontend payload, and CI wiring each have an explicit observed-red step before implementation.
- **Scope:** no prohibited source/config/data/core/golden/CSS behavior is planned; the generator-only snapshot date is explicitly audited.
- **Security/data:** Internal repository data only; no secrets or external data access.
- **Evidence honesty:** baseline outputs are identified as baseline; future pass counts, URLs, SHAs, and verdicts must be observed before recording.
- **Rollback:** config, hashes, table, generated date, source, and tests revert as one unit.
- **Assumptions:** the exact approved YAML draft remains byte-for-byte unchanged through implementation; current Python file count is 13 and numeric config set count becomes 23, but completion evidence uses observed output.
- **No self-approval:** this plan is provisional until Supervisor plan review; the Planner neither implements nor merges.
