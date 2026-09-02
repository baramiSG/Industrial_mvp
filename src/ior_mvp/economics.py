from __future__ import annotations

from typing import Any

from .config import thresholds_config


NATIONAL_VALUE_KEYS = (
    "domestic_value_added",
    "exports",
    "resilience_value",
    "knowledge_skills",
    "fiscal_receipts",
    "government_cost",
    "displacement",
    "resource_environment",
    "risk_allowance",
)
EVSI_KEYS = (
    "route_change_probability",
    "value_difference_m_sar",
    "evidence_cost_m_sar",
    "delay_cost_m_sar",
)


def _require_keys(
    values: dict[str, Any],
    required_keys: tuple[str, ...],
    label: str,
) -> None:
    missing = [
        key for key in required_keys if key not in values
    ]
    if missing:
        raise ValueError(
            f"{label} missing required keys: {', '.join(missing)}"
        )


def npv(rate: float, cash_flows: list[float]) -> float:
    if rate <= -1:
        raise ValueError("Discount rate must be greater than -100%")
    return sum(value / ((1 + rate) ** period) for period, value in enumerate(cash_flows))


def irr(cash_flows: list[float], *, tolerance: float = 1e-9) -> float | None:
    if not cash_flows or not any(value < 0 for value in cash_flows) or not any(value > 0 for value in cash_flows):
        return None

    def f(rate: float) -> float:
        return npv(rate, cash_flows)

    low, high = -0.9999, 1.0
    f_low, f_high = f(low), f(high)
    while f_low * f_high > 0 and high < 1024:
        high *= 2
        f_high = f(high)
    if f_low * f_high > 0:
        return None

    for _ in range(250):
        midpoint = (low + high) / 2
        f_mid = f(midpoint)
        if abs(f_mid) <= tolerance:
            return midpoint
        if f_low * f_mid <= 0:
            high = midpoint
            f_high = f_mid
        else:
            low = midpoint
            f_low = f_mid
    return (low + high) / 2


def minimum_effective_support(
    cash_flows: list[float], hurdle_rate: float
) -> dict[str, Any]:
    config = thresholds_config()["economics"]
    step = float(config["support_search_step_m_sar"])
    maximum = float(config["support_search_max_m_sar"])
    npv_tolerance = float(config["npv_tolerance_m_sar"])
    irr_tolerance = float(config["irr_tolerance"])

    unsupported_npv = npv(hurdle_rate, cash_flows)
    unsupported_irr = irr(cash_flows)
    support = 0.0
    passing_cash_flows: list[float] | None = None
    passing_npv: float | None = None
    passing_irr: float | None = None

    while support <= maximum + 1e-9:
        adjusted = list(cash_flows)
        adjusted[0] += support
        candidate_npv = npv(hurdle_rate, adjusted)
        candidate_irr = irr(adjusted)
        if (
            candidate_npv >= -npv_tolerance
            and candidate_irr is not None
            and candidate_irr >= hurdle_rate - irr_tolerance
        ):
            passing_cash_flows = adjusted
            passing_npv = candidate_npv
            passing_irr = candidate_irr
            break
        support = round(support + step, 10)

    return {
        "unsupported_npv_m": round(unsupported_npv, 3),
        "unsupported_irr": round(unsupported_irr, 5) if unsupported_irr is not None else None,
        "hurdle_rate": hurdle_rate,
        "minimum_effective_support_m": round(support, 3) if passing_cash_flows is not None else None,
        "supported_npv_m": round(passing_npv, 3) if passing_npv is not None else None,
        "supported_irr": round(passing_irr, 5) if passing_irr is not None else None,
        "passes": passing_cash_flows is not None,
        "search_step_m": step,
    }


def incremental_national_value(components: dict[str, float]) -> dict[str, Any]:
    _require_keys(
        components,
        NATIONAL_VALUE_KEYS,
        "national value",
    )
    benefits = (
        components["domestic_value_added"]
        + components["exports"]
        + components["resilience_value"]
        + components["knowledge_skills"]
        + components["fiscal_receipts"]
    )
    costs = (
        components["government_cost"]
        + components["displacement"]
        + components["resource_environment"]
        + components["risk_allowance"]
    )
    value = benefits - costs
    return {
        "benefits_m_sar": round(benefits, 3),
        "costs_m_sar": round(costs, 3),
        "incremental_national_value_m_sar": round(value, 3),
        "positive": value > 0,
        "components": components,
    }


def approximate_evsi(evsi_inputs: dict[str, float | str]) -> dict[str, Any]:
    _require_keys(evsi_inputs, EVSI_KEYS, "EVSI")
    probability = float(evsi_inputs["route_change_probability"])
    value_difference = float(evsi_inputs["value_difference_m_sar"])
    evidence_cost = float(evsi_inputs["evidence_cost_m_sar"])
    delay_cost = float(evsi_inputs["delay_cost_m_sar"])
    value = probability * value_difference - evidence_cost - delay_cost
    return {
        "route_change_probability": probability,
        "value_difference_m_sar": value_difference,
        "evidence_cost_m_sar": evidence_cost,
        "delay_cost_m_sar": delay_cost,
        "approximate_evsi_m_sar": round(value, 3),
        "positive": value > 0,
        "next_fact": evsi_inputs.get("next_fact"),
    }
