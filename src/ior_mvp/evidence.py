from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from .config import evidence_policy_config


class EvidenceIntegrityError(RuntimeError):
    pass


def validate_public_evidence(evidence: Iterable[dict[str, Any]]) -> None:
    for item in evidence:
        if item.get("synthetic_flag") is not False:
            raise EvidenceIntegrityError(
                f"Public evidence {item.get('evidence_id', '<unknown>')} is not explicitly non-synthetic"
            )


def validate_synthetic_scenario(scenario: dict[str, Any]) -> None:
    policy = evidence_policy_config()["synthetic_isolation"]
    if scenario.get("synthetic_flag") is not True:
        raise EvidenceIntegrityError("Synthetic scenario must set synthetic_flag=true")
    for field in policy["required_fields"]:
        if field not in scenario:
            raise EvidenceIntegrityError(f"Synthetic scenario is missing required field: {field}")
    if scenario.get("source") != "DEMO_GENERATOR":
        raise EvidenceIntegrityError("Demo synthetic evidence must use source=DEMO_GENERATOR")


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
    inputs = scenario.get("synthetic_inputs", {})
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
            }
        )
    return rows


def isolated_copy(value: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy so the simulation branch cannot mutate public records."""
    return deepcopy(value)
