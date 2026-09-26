from __future__ import annotations

import math
from typing import Any

from .config import sector_profiles_config, thresholds_config
from .gate_status import GateStatus, classify_gate_status


def effective_qualified_capacity(
    nameplate: float,
    availability: float,
    yield_rate: float,
    qualification_share: float,
    market_allocation_share: float,
) -> float:
    values = [availability, yield_rate, qualification_share, market_allocation_share]
    if nameplate < 0 or any(value < 0 or value > 1 for value in values):
        raise ValueError("Capacity factors must be between 0 and 1 and nameplate must be non-negative")
    return nameplate * availability * yield_rate * qualification_share * market_allocation_share


def _gate_names(declarations: list[Any]) -> list[str]:
    """Read gate names from a name list or public unresolved rows."""
    names: list[str] = []
    for item in declarations:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return names


def _decision_gate_lists(
    declarations: list[str] | dict[str, str | None] | None,
) -> tuple[dict[str, str], list[str], list[str]]:
    """Classify typed declarations; a name list stays unresolved."""
    if isinstance(declarations, dict):
        statuses = {
            name: classify_gate_status(raw).value
            for name, raw in declarations.items()
        }
        unresolved = [
            name
            for name, status in statuses.items()
            if status == GateStatus.UNAVAILABLE.value
        ]
        known = [
            name
            for name, status in statuses.items()
            if status == GateStatus.KNOWN_FAILURE.value
        ]
        return statuses, unresolved, known
    names = [
        name for name in (declarations or []) if isinstance(name, str)
    ]
    return {}, names, []


def _unique_names(*groups: list[str]) -> list[str]:
    """Keep the first occurrence of each gate name."""
    seen: set[str] = set()
    unique: list[str] = []
    for group in groups:
        for name in group:
            if name in seen:
                continue
            seen.add(name)
            unique.append(name)
    return unique


def publication_allowed(
    d_star: float | None,
    known_weight_coverage: float,
    minimum_known_weight_coverage: float,
    unresolved_hard_gates: list[str],
    has_known_hard_gate_failure: bool,
) -> bool:
    return (
        d_star is not None
        and known_weight_coverage >= minimum_known_weight_coverage
        and not unresolved_hard_gates
        and not has_known_hard_gate_failure
    )


def route_band(distance: float, bands: dict[str, float]) -> dict[str, Any]:
    if distance <= bands["immediate_adjacency_max"]:
        return {"code": "immediate_adjacency", "label": "Immediate adjacency", "route_hint": "Existing capacity, linkage or simple debottlenecking"}
    if distance <= bands["incremental_upgrade_max"]:
        return {"code": "incremental_upgrade", "label": "Incremental upgrade", "route_hint": "Brownfield capex, quality system, certification or finishing stage"}
    if distance <= bands["major_line_or_jv_max"]:
        return {"code": "major_line_or_jv", "label": "Major line / JV adjacency", "route_hint": "Specialist line or technology partner using existing assets"}
    return {"code": "greenfield_likely", "label": "Greenfield likely", "route_hint": "Test targeted new entry only if efficient scale and demand are robust"}


def evaluate_capability(
    sector_profile: str,
    states: dict[str, int | str],
    hard_gates: list[str] | dict[str, Any],
    decision_specific_hard_gates: list[str] | dict[str, str | None] | None = None,
) -> dict[str, Any]:
    profiles = sector_profiles_config()["profiles"]
    if sector_profile not in profiles:
        raise ValueError(f"Unknown sector profile: {sector_profile}")
    profile = profiles[sector_profile]
    weights: dict[str, float] = profile["weights"]
    if (
        len(weights) != 9
        or not math.isclose(
            math.fsum(float(value) for value in weights.values()),
            1.0,
            rel_tol=0,
            abs_tol=1e-12,
        )
    ):
        raise ValueError(
            f"Invalid sector profile weights: {sector_profile}"
        )
    capability_cfg = thresholds_config()["capability"]
    lambda_unknown = float(capability_cfg["unknown_penalty_lambda"])
    kmin = float(capability_cfg["minimum_known_weight_coverage"])

    known_weights: list[float] = []
    weighted_distance_numerator = 0.0
    dimensions: list[dict[str, Any]] = []
    for dimension, weight in weights.items():
        state = states.get(dimension, "U")
        known = isinstance(state, int) and 0 <= state <= 3
        if known:
            known_weights.append(float(weight))
            weighted_distance_numerator += weight * (state / 3)
        dimensions.append(
            {
                "dimension": dimension,
                "weight": weight,
                "state": state,
                "known": known,
            }
        )

    known_weight = math.fsum(known_weights)
    unknown_weight = max(0.0, 1.0 - known_weight)
    d_known = (
        weighted_distance_numerator / known_weight if known_weight > 0 else None
    )
    d_star = (
        min(1.0, d_known + lambda_unknown * unknown_weight)
        if d_known is not None
        else None
    )

    expected_profile_gates = list(profile["hard_gates"])
    unresolved_profile: list[str] = []
    profile_known: list[str] = []
    profile_gate_status: dict[str, str] = {}
    decision_status, unresolved_decision, decision_known = (
        _decision_gate_lists(decision_specific_hard_gates)
    )
    if isinstance(hard_gates, dict):
        extras = sorted(set(hard_gates) - set(expected_profile_gates))
        if extras:
            raise ValueError(
                "Unknown configured profile hard gate(s): "
                + ", ".join(extras)
            )
        for name in expected_profile_gates:
            status = classify_gate_status(hard_gates.get(name))
            profile_gate_status[name] = status.value
            if status == GateStatus.KNOWN_FAILURE:
                profile_known.append(name)
            elif status == GateStatus.UNAVAILABLE:
                unresolved_profile.append(name)
    else:
        profile_gate_status = {
            name: GateStatus.UNAVAILABLE.value
            for name in expected_profile_gates
        }
        unresolved_profile = list(expected_profile_gates)
        unresolved_decision = [
            *_gate_names(hard_gates),
            *unresolved_decision,
        ]
    unresolved = _unique_names(unresolved_profile, unresolved_decision)
    known_failures = _unique_names(profile_known, decision_known)

    route_publishable = publication_allowed(
        d_star,
        known_weight,
        kmin,
        unresolved,
        bool(known_failures),
    )
    band = route_band(d_star, capability_cfg["route_bands"]) if route_publishable else None

    result = {
        "sector_profile": sector_profile,
        "profile_label": profile["label"],
        "dimensions": dimensions,
        "known_weight_coverage": round(known_weight, 4),
        "unknown_weight": round(unknown_weight, 4),
        "d_known": round(d_known, 4) if d_known is not None else None,
        "unknown_penalty_lambda": lambda_unknown,
        "d_star": round(d_star, 4) if route_publishable and d_star is not None else None,
        "internal_d_star_before_gate": round(d_star, 4) if d_star is not None else None,
        "minimum_known_coverage": kmin,
        "unresolved_hard_gates": unresolved,
        "unresolved_profile_hard_gates": unresolved_profile,
        "unresolved_decision_specific_hard_gates": unresolved_decision,
        "known_hard_gate_failures": known_failures,
        "profile_hard_gates": profile_gate_status,
        "route_publishable": route_publishable,
        "route_band": band,
        "control_message": (
            "Route band published: coverage and hard-gate controls pass."
            if route_publishable
            else "D* is not published because known coverage or hard-gate controls do not pass."
        ),
    }
    if isinstance(decision_specific_hard_gates, dict):
        result["decision_specific_hard_gates"] = decision_status
    return result
