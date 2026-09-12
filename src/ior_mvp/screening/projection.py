"""Project acquired trade rows into governed screening-rule inputs."""

from __future__ import annotations

from typing import Any

UNAVAILABLE = "UNAVAILABLE"
USD_TO_USD_M = 1_000_000
KG_TO_KT = 1_000_000


def _positive_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return float(value)


def _hard_exclusion_inputs() -> dict[str, dict[str, Any]]:
    return {
        "heterogeneous_residual_code": {
            "commercial_product_separable": UNAVAILABLE,
            "product_level_evidence_available": UNAVAILABLE,
            "evidence_ids": [],
        },
        "downside_market_below_mes": {
            "sustainable_downside_demand_kt": UNAVAILABLE,
            "minimum_efficient_scale_kt": UNAVAILABLE,
            "credible_export_contract": UNAVAILABLE,
            "evidence_ids": [],
        },
        "unsatisfiable_hard_gate": {
            "gate_domain": UNAVAILABLE,
            "gate_satisfiability": UNAVAILABLE,
            "evidence_ids": [],
        },
        "idle_equivalent_domestic_capacity": {
            "domestic_specification_equivalent": UNAVAILABLE,
            "qualified_idle_capacity_kt": UNAVAILABLE,
            "target_specification_demand_kt": UNAVAILABLE,
            "binding_market_failure": UNAVAILABLE,
            "evidence_ids": [],
        },
        "transitory_or_measurement_gap": {
            "dominant_cause": UNAVAILABLE,
            "evidence_ids": [],
        },
        "redundancy_or_crowd_out": {
            "competition_finding": UNAVAILABLE,
            "evidence_ids": [],
        },
    }


def _capability(value: dict[str, Any] | None) -> dict[str, Any]:
    links = value.get("links", []) if isinstance(value, dict) else []
    if not links:
        same_family: bool | str = UNAVAILABLE
        verified: bool | str = UNAVAILABLE
    else:
        same_family = True
        verified = True
    return {
        "family_id": value.get("family_id", UNAVAILABLE) if isinstance(value, dict) else UNAVAILABLE,
        "same_process_family": same_family,
        "verified_present": verified,
        "coarse_adjacency_signals": [
            {
                "signal_type": link["signal_type"],
                "evidence_ids": list(link.get("evidence_ids", [])),
            }
            for link in links
        ],
        "producer_evidence": [],
        "unresolved_hard_gates": [],
        "profile_hard_gates": {},
    }


def _flow_projection(row: dict[str, Any] | None, prefix: str) -> dict[str, Any]:
    if row is None:
        return {f"{prefix}_usd_m": UNAVAILABLE, f"{prefix}_kt": UNAVAILABLE}
    value = _positive_number(row.get("trade_value"))
    weight = _positive_number(row.get("net_weight"))
    return {
        f"{prefix}_usd_m": value / USD_TO_USD_M if value is not None else UNAVAILABLE,
        f"{prefix}_kt": weight / KG_TO_KT if weight is not None else UNAVAILABLE,
    }


def project_case(
    hs6: str,
    universe_rows: list[dict[str, Any]],
    partner_rows: list[dict[str, Any]],
    tariff_index: dict[str, Any],
    capability: dict[str, Any] | None,
) -> dict[str, Any]:
    del tariff_index
    relevant = [row for row in universe_rows if row.get("hs6") == hs6]
    years = sorted(
        {row["year"] for row in relevant if isinstance(row.get("year"), int)}
    )
    trade = []
    for year in years:
        imports = next(
            (row for row in relevant if row.get("year") == year and row.get("flow") == "imports"),
            None,
        )
        exports = next(
            (row for row in relevant if row.get("year") == year and row.get("flow") == "exports"),
            None,
        )
        projected = {
            "year": year,
            **_flow_projection(imports, "imports"),
            **_flow_projection(exports, "exports"),
        }
        imports_value = projected["imports_usd_m"]
        imports_weight = projected["imports_kt"]
        projected["import_uv_usd_t"] = (
            imports_value * 1000 / imports_weight
            if isinstance(imports_value, (int, float))
            and isinstance(imports_weight, (int, float))
            and imports_weight > 0
            else UNAVAILABLE
        )
        projected["evidence_ids"] = sorted(
            {
                str(row.get("source_evidence_id"))
                for row in (imports, exports)
                if isinstance(row, dict) and row.get("source_evidence_id")
            }
        )
        trade.append(projected)
    imports_years = {
        row["year"]
        for row in relevant
        if row.get("flow") == "imports" and isinstance(row.get("year"), int)
    }
    missing_years = (
        [year for year in range(min(years), max(years) + 1) if year not in imports_years]
        if years
        else []
    )
    import_rows = [row for row in relevant if row.get("flow") == "imports"]
    partner_observations = []
    exclusions: list[str] = []
    for row in partner_rows:
        if row.get("hs6") != hs6:
            continue
        if str(row.get("partner_code", "")) == "0" or row.get("partner") == "World":
            if "PARTNER_WORLD_ROW" not in exclusions:
                exclusions.append("PARTNER_WORLD_ROW")
            continue
        value = _positive_number(row.get("trade_value"))
        weight = _positive_number(row.get("net_weight"))
        partner_observations.append(
            {
                "partner": row.get("partner", UNAVAILABLE),
                "year": row.get("year"),
                "flow": row.get("flow"),
                "trade_value_usd_m": value / USD_TO_USD_M if value is not None else UNAVAILABLE,
                "net_weight_kt": weight / KG_TO_KT if weight is not None else UNAVAILABLE,
                "quantity_unit": "kt",
                "validity_flags": {
                    "value_valid": value is not None,
                    "net_weight_valid": weight is not None,
                    "quantity_comparable": weight is not None,
                },
                "evidence_ids": [row["source_evidence_id"]] if row.get("source_evidence_id") else [],
            }
        )
    latest = max(years) if years else UNAVAILABLE
    return {
        "hs6": hs6,
        "trade": trade,
        "trade_quality": {
            "flow_basis": "gross",
            "reexports_separated": False,
            "domestic_origin_exports_separated": False,
            "missing_years": missing_years,
            "monthly_partner_tariff_line_available": False,
            "quantity_comparable": bool(import_rows)
            and all(_positive_number(row.get("net_weight")) is not None for row in import_rows),
            "execution_cap": "SCREENING_GRAIN",
            "hs_revisions_by_year": {
                str(year): sorted(
                    {
                        row["hs_revision"]
                        for row in relevant
                        if row.get("year") == year
                        and isinstance(row.get("hs_revision"), str)
                        and row["hs_revision"]
                    }
                )
                for year in years
            },
        },
        "partner_observations": partner_observations,
        "projection_exclusions": exclusions,
        "domestic_flows": {
            "period_year": latest,
            "domestic_production_kt": UNAVAILABLE,
            "inventory_change_kt": UNAVAILABLE,
            "retained_imports_kt": UNAVAILABLE,
            "domestic_origin_exports_kt": UNAVAILABLE,
            "reexports_kt": UNAVAILABLE,
        },
        "criticality_designation": None,
        "hard_exclusion_inputs": _hard_exclusion_inputs(),
        "domestic_capability": _capability(capability),
    }
