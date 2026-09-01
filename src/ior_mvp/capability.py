from __future__ import annotations

from typing import Any

from .config import sector_profiles_config, thresholds_config


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
    hard_gates: list[str] | dict[str, str],
) -> dict[str, Any]:
    profiles = sector_profiles_config()["profiles"]
    if sector_profile not in profiles:
        raise ValueError(f"Unknown sector profile: {sector_profile}")
    profile = profiles[sector_profile]
    weights: dict[str, float] = profile["weights"]
    capability_cfg = thresholds_config()["capability"]
    lambda_unknown = float(capability_cfg["unknown_penalty_lambda"])
    kmin = float(capability_cfg["minimum_known_weight_coverage"])

    known_weight = 0.0
    weighted_distance_numerator = 0.0
    dimensions: list[dict[str, Any]] = []
    for dimension, weight in weights.items():
        state = states.get(dimension, "U")
        known = isinstance(state, int) and 0 <= state <= 3
        if known:
            known_weight += weight
            weighted_distance_numerator += weight * (state / 3)
        dimensions.append(
            {
                "dimension": dimension,
                "weight": weight,
                "state": state,
                "known": known,
            }
        )

    unknown_weight = max(0.0, 1.0 - known_weight)
    d_known = (
        weighted_distance_numerator / known_weight if known_weight > 0 else None
    )
    d_star = (
        min(1.0, d_known + lambda_unknown * unknown_weight)
        if d_known is not None
        else None
    )

    if isinstance(hard_gates, dict):
        unresolved = [name for name, value in hard_gates.items() if not str(value).startswith("resolved") and value not in {"not applicable", "not_applicable"}]
    else:
        unresolved = list(hard_gates)

    route_publishable = (
        d_star is not None
        and known_weight >= kmin
        and not unresolved
        and not any(row["state"] == 3 for row in dimensions if row["known"])
    )
    band = route_band(d_star, capability_cfg["route_bands"]) if route_publishable else None

    return {
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
        "route_publishable": route_publishable,
        "route_band": band,
        "control_message": (
            "Route band published: coverage and hard-gate controls pass."
            if route_publishable
            else "D* is not published because known coverage or hard-gate controls do not pass."
        ),
    }
