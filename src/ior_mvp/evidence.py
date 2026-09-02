from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Iterable, Literal

from .config import evidence_policy_config


class EvidenceIntegrityError(RuntimeError):
    pass


ReconciliationResult = Literal[
    "PASS",
    "FAIL",
    "NOT_APPLICABLE",
    "INFORMATIONAL",
]


def validate_public_evidence(evidence: Iterable[dict[str, Any]]) -> None:
    for item in evidence:
        if item.get("synthetic_flag") is not False:
            raise EvidenceIntegrityError(
                f"Public evidence {item.get('evidence_id', '<unknown>')} "
                "is not explicitly non-synthetic"
            )


def _synthetic_policy() -> dict[str, Any]:
    policy = evidence_policy_config().get("synthetic_isolation")
    if not isinstance(policy, dict):
        raise EvidenceIntegrityError(
            "Evidence policy synthetic_isolation must be a mapping"
        )
    return policy


def _required_policy_value(
    policy: dict[str, Any],
    field: str,
) -> Any:
    if field not in policy:
        raise EvidenceIntegrityError(
            f"Evidence policy synthetic_isolation is missing: {field}"
        )
    return policy[field]


def synthetic_display_labels() -> dict[str, str]:
    """Return the two validated policy-owned synthetic warnings."""
    policy = _synthetic_policy()
    labels = {
        "en": _required_policy_value(policy, "display_label"),
        "ar": _required_policy_value(policy, "display_label_ar"),
    }
    for locale, value in labels.items():
        if (
            not isinstance(value, str)
            or not value
            or value.strip() != value
        ):
            raise EvidenceIntegrityError(
                "Evidence policy synthetic_isolation "
                f"display_label_{locale} must be a non-empty string"
            )
    return labels


def validate_synthetic_scenario(scenario: dict[str, Any]) -> None:
    policy = _synthetic_policy()
    required_fields = _required_policy_value(policy, "required_fields")
    if not isinstance(required_fields, list) or not all(
        isinstance(field, str) for field in required_fields
    ):
        raise EvidenceIntegrityError(
            "Evidence policy synthetic_isolation.required_fields "
            "must be a list of field names"
        )

    missing = [
        field
        for field in required_fields
        if field not in scenario
    ]
    if missing:
        raise EvidenceIntegrityError(
            "Synthetic scenario is missing required field(s): "
            + ", ".join(missing)
        )

    if scenario.get("synthetic_flag") is not True:
        raise EvidenceIntegrityError(
            "Synthetic scenario must set synthetic_flag=true"
        )

    required_class = _required_policy_value(
        policy,
        "required_evidence_class",
    )
    if scenario.get("evidence_class") != required_class:
        raise EvidenceIntegrityError(
            "Synthetic scenario evidence_class must equal policy "
            f"required_evidence_class={required_class}"
        )

    required_source = _required_policy_value(
        policy,
        "required_source",
    )
    if scenario.get("source") != required_source:
        raise EvidenceIntegrityError(
            "Synthetic scenario source must equal policy "
            f"required_source={required_source}"
        )

    required_label = synthetic_display_labels()["en"]
    if scenario.get("display_label") != required_label:
        raise EvidenceIntegrityError(
            "Synthetic scenario display_label must equal policy "
            f"display_label={required_label}"
        )

    if not isinstance(scenario.get("synthetic_inputs"), dict):
        raise EvidenceIntegrityError(
            "Synthetic scenario synthetic_inputs must be a mapping"
        )


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        return None
    number = float(value)
    return number if isfinite(number) else None


def _check(
    rule_id: str,
    source: str,
    formula: str,
    result: ReconciliationResult,
    *,
    blocking: bool,
    inputs: dict[str, Any],
    detail: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "source": source,
        "formula": formula,
        "result": result,
        "blocking": blocking,
        "inputs": inputs,
        "detail": detail,
    }


def _latest_trade(
    public_case: dict[str, Any],
) -> dict[str, Any]:
    trade = public_case.get("trade")
    if not isinstance(trade, list) or not trade:
        raise EvidenceIntegrityError(
            "Public case has no trade rows for scenario reconciliation"
        )
    rows = [
        row
        for row in trade
        if isinstance(row, dict)
        and _finite_number(row.get("year")) is not None
    ]
    if not rows:
        raise EvidenceIntegrityError(
            "Public case has no dated trade row for scenario reconciliation"
        )
    return max(rows, key=lambda row: float(row["year"]))


def _demand_check(
    inputs: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    source = (
        "Core 06 §5.1 lines 92-101; "
        "Core 05 §8 lines 182-195"
    )
    formula = (
        "target_spec_demand_kt <= latest_public_imports_kt"
    )
    demand = inputs.get("demand")
    if not isinstance(demand, dict):
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail=(
                "Synthetic demand block is missing or is not a mapping."
            ),
        )

    target = _finite_number(
        demand.get("target_spec_demand_kt")
    )
    if target is None or target < 0:
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={
                "target_spec_demand_kt": demand.get(
                    "target_spec_demand_kt"
                )
            },
            detail=(
                "target_spec_demand_kt must be a finite, non-negative "
                "number."
            ),
        )

    latest = _latest_trade(public_case)
    public_imports = _finite_number(
        latest.get("imports_kt")
    )
    check_inputs = {
        "target_spec_demand_kt": target,
        "latest_public_year": latest.get("year"),
        "latest_public_imports_kt": public_imports,
    }
    if public_imports is None:
        return _check(
            "target_spec_demand_within_public_imports",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs=check_inputs,
            detail=(
                "Latest public import quantity is unavailable; "
                "the compatible public marginal is explicit unknown."
            ),
        )

    passes = target <= public_imports
    return _check(
        "target_spec_demand_within_public_imports",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs=check_inputs,
        detail=(
            f"{target:g} kt <= {public_imports:g} kt."
            if passes
            else f"{target:g} kt exceeds {public_imports:g} kt."
        ),
    )


def _public_nameplate_total(
    public_case: dict[str, Any],
) -> tuple[float | None, list[float | None], bool]:
    capability = public_case.get("domestic_capability")
    producers = (
        capability.get("producer_evidence")
        if isinstance(capability, dict)
        else None
    )
    if not isinstance(producers, list):
        return None, [], False

    disclosed: list[float | None] = []
    invalid = False
    for producer in producers:
        raw = (
            producer.get("installed_capacity_tpy")
            if isinstance(producer, dict)
            else None
        )
        if raw is None or raw == "UNAVAILABLE":
            disclosed.append(None)
            continue
        capacity = _finite_number(raw)
        if capacity is None or capacity < 0:
            invalid = True
            disclosed.append(None)
            continue
        disclosed.append(capacity)

    numeric = [
        capacity
        for capacity in disclosed
        if capacity is not None
    ]
    if not numeric:
        return None, disclosed, invalid
    return sum(numeric) / 1000.0, disclosed, invalid


def _nameplate_check(
    inputs: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    source = (
        "Core 06 §5.1 lines 92-101; "
        "Core 05 §8 lines 182-195"
    )
    formula = (
        "plant_line.nameplate_kt <= "
        "sum(non_null installed_capacity_tpy) / 1000"
    )
    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail=(
                "Synthetic plant_line block is missing or is not a "
                "mapping."
            ),
        )

    nameplate = _finite_number(line.get("nameplate_kt"))
    if nameplate is None or nameplate < 0:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={
                "line_nameplate_kt": line.get("nameplate_kt")
            },
            detail=(
                "nameplate_kt must be a finite, non-negative number."
            ),
        )

    public_total, disclosed, invalid = _public_nameplate_total(
        public_case
    )
    check_inputs = {
        "line_nameplate_kt": nameplate,
        "disclosed_installed_capacity_tpy": disclosed,
        "disclosed_public_nameplate_kt": public_total,
    }
    if invalid:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs=check_inputs,
            detail=(
                "A non-null public installed_capacity_tpy value is "
                "not a finite, non-negative number."
            ),
        )
    if public_total is None:
        return _check(
            "line_nameplate_within_disclosed_public_capacity",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs=check_inputs,
            detail=(
                "No numeric public installed nameplate is disclosed."
            ),
        )

    passes = nameplate <= public_total
    return _check(
        "line_nameplate_within_disclosed_public_capacity",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs=check_inputs,
        detail=(
            f"{nameplate:g} kt <= {public_total:g} kt."
            if passes
            else f"{nameplate:g} kt exceeds {public_total:g} kt."
        ),
    )


def _capacity_factor_check(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    source = (
        "Core 06 §10 item 3 lines 226-233; "
        "Core 06 §6.2 lines 148-156; "
        "Core 05 §8 lines 197-203"
    )
    formula = "for every capacity factor: 0 <= factor <= 1"
    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "capacity_factors_within_unit_interval",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail=(
                "Synthetic plant_line block is missing or is not a "
                "mapping."
            ),
        )

    required = (
        "availability",
        "yield",
        "qualification_share",
        "market_allocation_share",
    )
    names = required + (
        ("current_utilisation",)
        if "current_utilisation" in line
        else ()
    )
    raw_values = {
        name: line.get(name)
        for name in names
    }
    values = {
        name: _finite_number(raw_values[name])
        for name in names
    }
    invalid = [
        name
        for name, value in values.items()
        if value is None or not 0 <= value <= 1
    ]
    return _check(
        "capacity_factors_within_unit_interval",
        source,
        formula,
        "FAIL" if invalid else "PASS",
        blocking=True,
        inputs=raw_values,
        detail=(
            "Invalid capacity factor(s): " + ", ".join(invalid)
            if invalid
            else "All declared capacity factors are within [0,1]."
        ),
    )


def _qualified_availability_check(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    source = (
        "Core 06 §5.1 lines 92-101; "
        "Core 06 §10 item 3 lines 226-233"
    )
    formula = (
        "qualified_available_kt <= "
        "nameplate_kt * availability * yield"
    )
    equivalence = inputs.get("equivalence")
    if not isinstance(equivalence, dict) or (
        "qualified_available_kt" not in equivalence
    ):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "NOT_APPLICABLE",
            blocking=True,
            inputs={},
            detail="No qualified_available_kt is declared.",
        )

    line = inputs.get("plant_line")
    if not isinstance(line, dict):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={},
            detail=(
                "Physical output cannot be calculated without "
                "plant_line."
            ),
        )

    qualified = _finite_number(
        equivalence.get("qualified_available_kt")
    )
    nameplate = _finite_number(line.get("nameplate_kt"))
    availability = _finite_number(line.get("availability"))
    yield_rate = _finite_number(line.get("yield"))
    values = (
        qualified,
        nameplate,
        availability,
        yield_rate,
    )
    if any(
        value is None or value < 0
        for value in values
    ):
        return _check(
            "qualified_availability_within_physical_output",
            source,
            formula,
            "FAIL",
            blocking=True,
            inputs={
                "qualified_available_kt": equivalence.get(
                    "qualified_available_kt"
                ),
                "nameplate_kt": line.get("nameplate_kt"),
                "availability": line.get("availability"),
                "yield": line.get("yield"),
            },
            detail=(
                "Physical-availability inputs must be finite and "
                "non-negative."
            ),
        )

    assert qualified is not None
    assert nameplate is not None
    assert availability is not None
    assert yield_rate is not None
    physical_ceiling = (
        nameplate * availability * yield_rate
    )
    passes = qualified <= physical_ceiling
    return _check(
        "qualified_availability_within_physical_output",
        source,
        formula,
        "PASS" if passes else "FAIL",
        blocking=True,
        inputs={
            "qualified_available_kt": qualified,
            "nameplate_kt": nameplate,
            "availability": availability,
            "yield": yield_rate,
            "physical_output_ceiling_kt": round(
                physical_ceiling,
                6,
            ),
        },
        detail=(
            f"{qualified:g} kt <= {physical_ceiling:g} kt."
            if passes
            else (
                f"{qualified:g} kt exceeds "
                f"{physical_ceiling:g} kt."
            )
        ),
    )


def _demand_layer_observation(
    inputs: dict[str, Any],
) -> dict[str, Any]:
    source = "Core 04 §2.6 lines 102-112"
    formula = (
        "observe downside_demand_kt <= target_spec_demand_kt and "
        "committed_demand_kt <= target_spec_demand_kt; "
        "no decision effect"
    )
    demand = inputs.get("demand")
    if not isinstance(demand, dict):
        return _check(
            "demand_layers_remain_separate",
            source,
            formula,
            "INFORMATIONAL",
            blocking=False,
            inputs={},
            detail=(
                "Demand layers are unavailable for observation."
            ),
        )

    target = _finite_number(
        demand.get("target_spec_demand_kt")
    )
    downside = _finite_number(
        demand.get("downside_demand_kt")
    )
    committed = _finite_number(
        demand.get("committed_demand_kt")
    )
    return _check(
        "demand_layers_remain_separate",
        source,
        formula,
        "INFORMATIONAL",
        blocking=False,
        inputs={
            "target_spec_demand_kt": target,
            "downside_demand_kt": downside,
            "committed_demand_kt": committed,
            "downside_within_target": (
                None
                if target is None or downside is None
                else downside <= target
            ),
            "committed_within_target": (
                None
                if target is None or committed is None
                else committed <= target
            ),
        },
        detail=(
            "Demand layers are reported separately; no ordering "
            "constraint is enforced."
        ),
    )


def _allocation_check() -> dict[str, Any]:
    return _check(
        "tariff_line_or_buyer_allocations_reconcile",
        (
            "Core 06 §5.1 lines 92-101; "
            "Core 05 §8 lines 182-195"
        ),
        (
            "sum(buyer quantities) <= public HS6 imports; "
            "sum(tariff-line transactions) == parent HS6 total "
            "when a governed compatible block exists"
        ),
        "NOT_APPLICABLE",
        blocking=True,
        inputs={},
        detail=(
            "No governed tariff-line or buyer allocation block is "
            "present; no allocation sum was evaluated."
        ),
    )


def reconcile_synthetic_scenario(
    scenario: dict[str, Any],
    public_case: dict[str, Any],
) -> dict[str, Any]:
    validate_synthetic_scenario(scenario)
    public_opportunity = public_case.get("opportunity")
    public_opportunity_id = (
        public_opportunity.get("id")
        if isinstance(public_opportunity, dict)
        else None
    )
    if scenario.get("opportunity_id") != public_opportunity_id:
        raise EvidenceIntegrityError(
            "Synthetic scenario opportunity_id does not match "
            "the public case opportunity.id"
        )

    inputs = scenario["synthetic_inputs"]
    checks = [
        _demand_check(inputs, public_case),
        _nameplate_check(inputs, public_case),
        _capacity_factor_check(inputs),
        _qualified_availability_check(inputs),
        _demand_layer_observation(inputs),
        _allocation_check(),
    ]
    blocking_results = [
        check["result"]
        for check in checks
        if check["result"] != "INFORMATIONAL"
    ]
    if "FAIL" in blocking_results:
        status = "FAIL"
    elif "PASS" in blocking_results:
        status = "PASS"
    else:
        status = "NOT_APPLICABLE"
    return {
        "status": status,
        "scenario_id": scenario["scenario_id"],
        "opportunity_id": scenario["opportunity_id"],
        "public_snapshot_id": public_case.get("snapshot_id"),
        "checks": checks,
    }


def require_scenario_reconciliation(
    report: dict[str, Any],
) -> None:
    failures = [
        check["rule_id"]
        for check in report.get("checks", [])
        if check.get("result") == "FAIL"
    ]
    if failures:
        raise EvidenceIntegrityError(
            "Synthetic scenario reconciliation failed for "
            f"{report.get('scenario_id', '<unknown>')}: "
            + ", ".join(failures)
        )


def public_decision_fingerprint(decision: dict[str, Any]) -> tuple[Any, ...]:
    return (
        decision.get("state"),
        decision.get("route_code"),
        decision.get("headline"),
        tuple(decision.get("missing_facts", [])),
    )


def assert_real_decision_unchanged(
    before: dict[str, Any], after: dict[str, Any]
) -> None:
    if public_decision_fingerprint(before) != public_decision_fingerprint(after):
        raise EvidenceIntegrityError(
            "Synthetic analysis attempted to change the real decision state"
        )


def synthetic_evidence_rows(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    validate_synthetic_scenario(scenario)
    inputs = scenario["synthetic_inputs"]
    labels = synthetic_display_labels()
    rows: list[dict[str, Any]] = []
    for key in sorted(inputs):
        rows.append(
            {
                "evidence_id": f"{scenario['scenario_id']}::{key}",
                "title": key.replace("_", " ").title(),
                "source": scenario["source"],
                "status": "synthetic",
                "evidence_class": scenario["evidence_class"],
                "synthetic_flag": True,
                "scenario_id": scenario["scenario_id"],
                "supports": [f"Simulation branch input: {key}"],
                "display_label": scenario["display_label"],
                "display_labels": labels,
            }
        )
    return rows


def isolated_copy(value: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy so the simulation branch cannot mutate public records."""
    return deepcopy(value)
