from __future__ import annotations

import math
from typing import Any, Literal


NOT_CALCULABLE = "NOT_CALCULABLE"
UNAVAILABLE = "UNAVAILABLE"
CALCULATION_TOLERANCE = 1 / 1_000_000


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _round(value: float) -> float:
    return round(value, 4)


def compound_annual_growth(
    latest: float,
    previous: float,
    years: int,
) -> float:
    """Return CAGR over a positive integer observed span."""
    if (
        isinstance(latest, bool)
        or isinstance(previous, bool)
        or not isinstance(latest, (int, float))
        or not isinstance(previous, (int, float))
        or not math.isfinite(float(latest))
        or not math.isfinite(float(previous))
        or latest <= 0
        or previous <= 0
    ):
        raise ValueError("CAGR requires positive finite values")
    if isinstance(years, bool) or not isinstance(years, int) or years <= 0:
        raise ValueError("CAGR requires a positive integer year span")
    return (float(latest) / float(previous)) ** (1 / years) - 1


def latest_usable_trade_pair(
    trade: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Select the two latest rows with positive import value and quantity."""
    usable: list[dict[str, Any]] = []
    for row in trade:
        if not isinstance(row, dict):
            continue
        year = row.get("year")
        value = _finite_number(row.get("imports_usd_m"))
        quantity = _finite_number(row.get("imports_kt"))
        if (
            isinstance(year, bool)
            or not isinstance(year, int)
            or value is None
            or quantity is None
            or value <= 0
            or quantity <= 0
        ):
            continue
        usable.append(row)
    usable.sort(key=lambda row: row["year"])
    if len(usable) < 2:
        return None
    return usable[-2], usable[-1]


def _unavailable_concentration(
    basis: Literal["value", "quantity"],
    *,
    year: int | str = NOT_CALCULABLE,
    flow_basis: str = NOT_CALCULABLE,
    source: str = "none",
    coverage: float | str = NOT_CALCULABLE,
    eligible_count: int | str = NOT_CALCULABLE,
    reason: str,
) -> dict[str, Any]:
    return {
        "basis": basis,
        "status": NOT_CALCULABLE,
        "year": year,
        "flow_basis": flow_basis,
        "source": source,
        "hhi": NOT_CALCULABLE,
        "largest_supplier_share": NOT_CALCULABLE,
        "top_two_share": NOT_CALCULABLE,
        "valid_coverage": coverage,
        "eligible_partner_count": eligible_count,
        "reason": reason,
    }


def _latest_trade_row(case: dict[str, Any]) -> dict[str, Any] | None:
    trade = case.get("trade")
    if not isinstance(trade, list):
        return None
    dated = [
        row
        for row in trade
        if isinstance(row, dict)
        and isinstance(row.get("year"), int)
        and not isinstance(row.get("year"), bool)
    ]
    return max(dated, key=lambda row: row["year"]) if dated else None


def partner_detail_state(
    case: dict[str, Any],
) -> tuple[str, str | None] | None:
    """Return the typed partner-detail state when PublicSnapshot 2.2 has it."""
    detail = case.get("partner_detail")
    if not isinstance(detail, dict):
        return None
    state = detail.get("state")
    if not isinstance(state, str):
        return None
    reason = detail.get("reason")
    return state, reason if isinstance(reason, str) else None


def _partner_concentration_fallback_reason(
    case: dict[str, Any],
    basis: Literal["value", "quantity"],
) -> str:
    detail = partner_detail_state(case)
    if detail is not None:
        state, reason = detail
        if state == "PARTNER_DETAIL_MISSING" and reason is not None:
            return (
                f"PARTNER_DETAIL_MISSING:{reason} — no partner rows were "
                "parsed; missing evidence, not zero trade."
            )
        if state == "PARTNER_TRADE_OBSERVED_ZERO":
            return (
                "PARTNER_TRADE_OBSERVED_ZERO — normalized response "
                "contained zero partner rows."
            )
    return (
        f"No partner rows or source-attributed {basis} concentration "
        "disclosure are available."
    )


def concentration_metrics(
    case: dict[str, Any],
    basis: Literal["value", "quantity"],
) -> dict[str, Any]:
    """Compute one concentration basis, preferring complete partner rows."""
    if basis not in {"value", "quantity"}:
        raise ValueError("Concentration basis must be value or quantity")
    latest = _latest_trade_row(case)
    if latest is None:
        return _unavailable_concentration(
            basis,
            reason="No dated aggregate trade row is available.",
        )
    year = latest["year"]
    flow_basis = (
        case.get("trade_quality", {}).get("flow_basis", NOT_CALCULABLE)
        if isinstance(case.get("trade_quality"), dict)
        else NOT_CALCULABLE
    )
    partner_rows = case.get("partner_observations")
    matching_rows = (
        [
            row
            for row in partner_rows
            if isinstance(row, dict)
            and row.get("year") == year
            and row.get("flow") == "imports"
        ]
        if isinstance(partner_rows, list)
        else []
    )
    if matching_rows:
        if basis == "value":
            aggregate_key = "imports_usd_m"
            observation_key = "trade_value_usd_m"
            valid = lambda flags, row: flags.get("value_valid") is True
        else:
            aggregate_key = "imports_kt"
            observation_key = "net_weight_kt"
            valid = lambda flags, row: (
                flags.get("net_weight_valid") is True
                and flags.get("quantity_comparable") is True
                and row.get("quantity_unit") == "kt"
            )
        world_total = _finite_number(latest.get(aggregate_key))
        eligible: list[float] = []
        for row in matching_rows:
            flags = row.get("validity_flags")
            if not isinstance(flags, dict) or not valid(flags, row):
                continue
            number = _finite_number(row.get(observation_key))
            if number is not None and number >= 0:
                eligible.append(number)
        eligible_total = sum(eligible)
        coverage = (
            eligible_total / world_total
            if world_total is not None and world_total > 0
            else None
        )
        rounded_coverage: float | str = (
            _round(coverage)
            if coverage is not None
            else NOT_CALCULABLE
        )
        if (
            world_total is None
            or world_total <= 0
            or eligible_total <= 0
            or not math.isclose(
                eligible_total,
                world_total,
                rel_tol=0,
                abs_tol=CALCULATION_TOLERANCE,
            )
        ):
            return _unavailable_concentration(
                basis,
                year=year,
                flow_basis=flow_basis,
                source="partner_observations",
                coverage=rounded_coverage,
                eligible_count=len(eligible),
                reason=(
                    "Eligible partner rows do not reconcile to the matching "
                    f"world aggregate {basis} basis."
                ),
            )
        shares = [number / eligible_total for number in eligible]
        ordered = sorted(shares, reverse=True)
        return {
            "basis": basis,
            "status": "FULL",
            "year": year,
            "flow_basis": flow_basis,
            "source": "partner_observations",
            "hhi": _round(sum(share * share for share in shares)),
            "largest_supplier_share": _round(max(shares)),
            "top_two_share": _round(sum(ordered[:2])),
            "valid_coverage": _round(coverage),
            "eligible_partner_count": len(eligible),
            "reason": None,
        }

    disclosed = case.get("disclosed_concentration")
    disclosure = (
        disclosed.get(basis)
        if isinstance(disclosed, dict)
        else None
    )
    if isinstance(disclosure, dict) and disclosure.get("status") == "calculated":
        def projected(key: str) -> float | str:
            number = _finite_number(disclosure.get(key))
            return (
                number
                if number is not None
                else NOT_CALCULABLE
            )

        return {
            "basis": basis,
            "status": "FULL",
            "year": disclosure["year"],
            "flow_basis": disclosure["flow_basis"],
            "source": "disclosed_concentration",
            "hhi": projected("hhi"),
            "largest_supplier_share": projected(
                "largest_supplier_share"
            ),
            "top_two_share": projected("top_two_share"),
            "valid_coverage": NOT_CALCULABLE,
            "eligible_partner_count": NOT_CALCULABLE,
            "reason": None,
        }
    return _unavailable_concentration(
        basis,
        year=year,
        flow_basis=flow_basis,
        reason=_partner_concentration_fallback_reason(case, basis),
    )


def _concentration_predicate_values(
    case: dict[str, Any],
    basis: Literal["value", "quantity"],
    metrics: dict[str, Any],
) -> tuple[float | None, float | None]:
    """Return unrounded HHI/largest share for the rule predicate."""
    if metrics.get("status") != "FULL":
        return None, None
    if metrics.get("source") == "disclosed_concentration":
        disclosed = case.get("disclosed_concentration")
        item = (
            disclosed.get(basis)
            if isinstance(disclosed, dict)
            else None
        )
        if not isinstance(item, dict):
            return None, None
        return (
            _finite_number(item.get("hhi")),
            _finite_number(item.get("largest_supplier_share")),
        )
    if metrics.get("source") != "partner_observations":
        return None, None
    rows = case.get("partner_observations")
    if not isinstance(rows, list):
        return None, None
    values: list[float] = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or row.get("year") != metrics.get("year")
            or row.get("flow") != "imports"
        ):
            continue
        flags = row.get("validity_flags")
        if not isinstance(flags, dict):
            continue
        if basis == "value":
            eligible = flags.get("value_valid") is True
            raw = row.get("trade_value_usd_m")
        else:
            eligible = (
                flags.get("net_weight_valid") is True
                and flags.get("quantity_comparable") is True
                and row.get("quantity_unit") == "kt"
            )
            raw = row.get("net_weight_kt")
        number = _finite_number(raw)
        if eligible and number is not None and number >= 0:
            values.append(number)
    total = sum(values)
    if total <= 0:
        return None, None
    shares = [value / total for value in values]
    return sum(share * share for share in shares), max(shares)


def _weighted_quantile(
    ordered: list[tuple[float, float, str]],
    probability: float,
) -> float:
    total_weight = sum(weight for _, weight, _ in ordered)
    cumulative = 0.0
    for value, weight, _ in ordered:
        cumulative += weight
        if cumulative / total_weight >= probability:
            return value
    return ordered[-1][0]


def _unavailable_dispersion(
    *,
    basis: str,
    value_coverage: float | str = NOT_CALCULABLE,
    quantity_coverage: float | str = NOT_CALCULABLE,
    minimum_coverage: float,
    reason: str,
) -> dict[str, Any]:
    return {
        "status": NOT_CALCULABLE,
        "calculation_basis": basis,
        "valid_value_coverage": value_coverage,
        "valid_quantity_coverage": quantity_coverage,
        "minimum_valid_value_coverage": minimum_coverage,
        "weighted_q1_usd_t": NOT_CALCULABLE,
        "weighted_median_usd_t": NOT_CALCULABLE,
        "weighted_q3_usd_t": NOT_CALCULABLE,
        "iqr_usd_t": NOT_CALCULABLE,
        "bulk_band_usd_t": NOT_CALCULABLE,
        "outlier_candidate": NOT_CALCULABLE,
        "reason": reason,
    }


def degraded_dispersion_metrics(
    case: dict[str, Any],
    minimum_valid_value_coverage: float,
) -> dict[str, Any]:
    """Calculate descriptive annual-partner dispersion or project disclosure."""
    if (
        isinstance(minimum_valid_value_coverage, bool)
        or not isinstance(minimum_valid_value_coverage, (int, float))
        or not math.isfinite(float(minimum_valid_value_coverage))
        or not 0 <= minimum_valid_value_coverage <= 1
    ):
        raise ValueError("Dispersion coverage threshold must be within [0,1]")
    minimum = float(minimum_valid_value_coverage)
    latest = _latest_trade_row(case)
    if latest is None:
        return _unavailable_dispersion(
            basis="none",
            minimum_coverage=minimum,
            reason="No dated aggregate trade row is available.",
        )
    partner_rows = case.get("partner_observations")
    matching_rows = (
        [
            row
            for row in partner_rows
            if isinstance(row, dict)
            and row.get("year") == latest["year"]
            and row.get("flow") == "imports"
        ]
        if isinstance(partner_rows, list)
        else []
    )
    if matching_rows:
        world_value = _finite_number(latest.get("imports_usd_m"))
        world_quantity = _finite_number(latest.get("imports_kt"))
        observations: list[tuple[float, float, str, float]] = []
        eligible_value = 0.0
        eligible_quantity = 0.0
        for row in matching_rows:
            flags = row.get("validity_flags")
            value = _finite_number(row.get("trade_value_usd_m"))
            quantity = _finite_number(row.get("net_weight_kt"))
            if (
                not isinstance(flags, dict)
                or flags.get("value_valid") is not True
                or flags.get("net_weight_valid") is not True
                or flags.get("quantity_comparable") is not True
                or row.get("quantity_unit") != "kt"
                or value is None
                or quantity is None
                or value <= 0
                or quantity <= 0
            ):
                continue
            unit_value = value * 1000 / quantity
            observations.append(
                (unit_value, quantity, str(row.get("partner")), value)
            )
            eligible_value += value
            eligible_quantity += quantity
        value_coverage = (
            eligible_value / world_value
            if world_value is not None and world_value > 0
            else None
        )
        quantity_coverage = (
            eligible_quantity / world_quantity
            if world_quantity is not None and world_quantity > 0
            else None
        )
        rounded_value_coverage: float | str = (
            _round(value_coverage)
            if value_coverage is not None
            else NOT_CALCULABLE
        )
        rounded_quantity_coverage: float | str = (
            _round(quantity_coverage)
            if quantity_coverage is not None
            else NOT_CALCULABLE
        )
        distinct = {item[0] for item in observations}
        if (
            value_coverage is not None
            and value_coverage >= minimum
            and len(distinct) >= 2
        ):
            ordered = sorted(
                (unit_value, quantity, partner)
                for unit_value, quantity, partner, _ in observations
            )
            quarter, half, three_quarters = (
                1 / 4,
                1 / 2,
                3 / 4,
            )
            q1 = _weighted_quantile(ordered, quarter)
            median = _weighted_quantile(ordered, half)
            q3 = _weighted_quantile(ordered, three_quarters)
            iqr = q3 - q1
            if iqr > 0:
                outlier = max(
                    observations,
                    key=lambda item: abs(math.log(item[0] / median)),
                )
                return {
                    "status": "CALCULABLE",
                    "calculation_basis": "partner_observations",
                    "valid_value_coverage": _round(value_coverage),
                    "valid_quantity_coverage": (
                        _round(quantity_coverage)
                        if quantity_coverage is not None
                        else NOT_CALCULABLE
                    ),
                    "minimum_valid_value_coverage": minimum,
                    "weighted_q1_usd_t": _round(q1),
                    "weighted_median_usd_t": _round(median),
                    "weighted_q3_usd_t": _round(q3),
                    "iqr_usd_t": _round(iqr),
                    "bulk_band_usd_t": NOT_CALCULABLE,
                    "outlier_candidate": {
                        "partner": outlier[2],
                        "unit_value_usd_t": _round(outlier[0]),
                        "quantity_share": _round(
                            outlier[1] / eligible_quantity
                        ),
                        "confirmed_outlier": False,
                    },
                    "reason": None,
                }
        row_failure = _unavailable_dispersion(
            basis="partner_observations",
            value_coverage=rounded_value_coverage,
            quantity_coverage=rounded_quantity_coverage,
            minimum_coverage=minimum,
            reason=(
                "Comparable annual partner coverage or dispersion is "
                "insufficient."
            ),
        )
    else:
        row_failure = None

    disclosure = case.get("disclosed_dispersion")
    if (
        isinstance(disclosure, dict)
        and disclosure.get("status") == "calculated"
    ):
        outlier = disclosure.get("outlier_observation")
        projected_outlier: dict[str, Any] | str = NOT_CALCULABLE
        if isinstance(outlier, dict):
            projected_outlier = {
                "partner": outlier["partner"],
                "net_weight_kt": outlier["net_weight_kt"],
                "unit_value_usd_t": outlier["unit_value_usd_t"],
                "confirmed_outlier": False,
            }
        return {
            "status": "DISCLOSED",
            "calculation_basis": "disclosed_dispersion",
            "valid_value_coverage": (
                NOT_CALCULABLE
                if disclosure.get("valid_value_coverage") == UNAVAILABLE
                else disclosure.get("valid_value_coverage")
            ),
            "valid_quantity_coverage": (
                NOT_CALCULABLE
                if disclosure.get("valid_quantity_coverage") == UNAVAILABLE
                else disclosure.get("valid_quantity_coverage")
            ),
            "minimum_valid_value_coverage": minimum,
            "weighted_q1_usd_t": NOT_CALCULABLE,
            "weighted_median_usd_t": (
                NOT_CALCULABLE
                if disclosure.get("weighted_median_usd_t") == UNAVAILABLE
                else disclosure.get("weighted_median_usd_t")
            ),
            "weighted_q3_usd_t": NOT_CALCULABLE,
            "iqr_usd_t": (
                NOT_CALCULABLE
                if disclosure.get("iqr_usd_t") == UNAVAILABLE
                else disclosure.get("iqr_usd_t")
            ),
            "bulk_band_usd_t": (
                NOT_CALCULABLE
                if disclosure.get("bulk_band_usd_t") == UNAVAILABLE
                else disclosure.get("bulk_band_usd_t")
            ),
            "outlier_candidate": projected_outlier,
            "comparison_observations": (
                NOT_CALCULABLE
                if disclosure.get("comparison_observations") == UNAVAILABLE
                else disclosure.get("comparison_observations")
            ),
            "source_evidence_id": disclosure.get("source_evidence_id"),
            "reason": disclosure.get("coverage_note"),
        }
    if row_failure is not None:
        return row_failure
    detail = partner_detail_state(case)
    if detail is not None:
        state, reason = detail
        if state == "PARTNER_DETAIL_MISSING" and reason is not None:
            return _unavailable_dispersion(
                basis="none",
                minimum_coverage=minimum,
                reason=(
                    f"PARTNER_DETAIL_MISSING:{reason} — no comparable "
                    "partner unit values exist; missing evidence, not zero "
                    "trade."
                ),
            )
        if state == "PARTNER_TRADE_OBSERVED_ZERO":
            return _unavailable_dispersion(
                basis="none",
                minimum_coverage=minimum,
                reason=(
                    "PARTNER_TRADE_OBSERVED_ZERO — no partner unit values "
                    "exist because zero partner rows were observed."
                ),
            )
    return _unavailable_dispersion(
        basis="none",
        minimum_coverage=minimum,
        reason=(
            "No comparable partner rows or source-attributed dispersion "
            "disclosure are available."
        ),
    )


def _unknown_fields(
    values: dict[str, Any],
    *names: str,
) -> list[str]:
    return sorted(
        name
        for name in names
        if _finite_number(values.get(name)) is None
    )


def domestic_flow_metrics(
    latest_trade: dict[str, Any],
    domestic_flows: dict[str, Any],
) -> dict[str, Any]:
    """Compute §3.3 physical-flow measures without coercing unknowns."""
    gross_imports = _finite_number(latest_trade.get("imports_kt"))
    production = _finite_number(
        domestic_flows.get("domestic_production_kt")
    )
    direct_retained = _finite_number(
        domestic_flows.get("retained_imports_kt")
    )
    domestic_exports = _finite_number(
        domestic_flows.get("domestic_origin_exports_kt")
    )
    reexports = _finite_number(domestic_flows.get("reexports_kt"))
    raw_inputs = {
        "domestic_production_kt": domestic_flows.get(
            "domestic_production_kt"
        ),
        "retained_imports_kt": domestic_flows.get(
            "retained_imports_kt"
        ),
        "domestic_origin_exports_kt": domestic_flows.get(
            "domestic_origin_exports_kt"
        ),
        "reexports_kt": domestic_flows.get("reexports_kt"),
    }
    unavailable_inputs = _unknown_fields(raw_inputs, *raw_inputs)
    reasons: dict[str, list[str] | str] = {}
    if gross_imports is not None and reexports is not None:
        if reexports > gross_imports:
            raise ValueError("reexports_kt cannot exceed gross imports_kt")
        computed_retained = gross_imports - reexports
        if (
            direct_retained is not None
            and abs(direct_retained - computed_retained)
            > CALCULATION_TOLERANCE
        ):
            raise ValueError(
                "retained_imports_kt must equal imports_kt minus reexports_kt"
            )
    if direct_retained is not None:
        retained = direct_retained
        basis = "reported_verified_retained_imports"
    elif gross_imports is not None and reexports is not None:
        retained = gross_imports - reexports
        basis = "computed_from_reexports"
    else:
        retained = None
        basis = NOT_CALCULABLE
        missing = ["retained_imports_kt"]
        if reexports is None:
            missing.append("reexports_kt")
        if gross_imports is None:
            missing.append("imports_kt")
        reasons["retained_imports_kt"] = sorted(missing)

    if retained is not None and domestic_exports is not None:
        net_exposure = retained - domestic_exports
    else:
        net_exposure = None
        reasons["net_import_exposure_kt"] = sorted(
            [
                name
                for name, value in (
                    ("retained_imports_kt", retained),
                    ("domestic_origin_exports_kt", domestic_exports),
                )
                if value is None
            ]
        )
    if (
        production is not None
        and retained is not None
        and domestic_exports is not None
    ):
        apparent = production + retained - domestic_exports
    else:
        apparent = None
        reasons["apparent_consumption_kt"] = sorted(
            [
                name
                for name, value in (
                    ("domestic_production_kt", production),
                    ("retained_imports_kt", retained),
                    ("domestic_origin_exports_kt", domestic_exports),
                )
                if value is None
            ]
        )
    if retained is not None and apparent is not None and apparent > 0:
        penetration = retained / apparent
    else:
        penetration = None
        if apparent is not None and apparent <= 0:
            reasons[
                "retained_import_share_of_apparent_consumption"
            ] = "requires positive apparent_consumption_kt"
        else:
            reasons[
                "retained_import_share_of_apparent_consumption"
            ] = sorted(
                [
                    name
                    for name, value in (
                        ("retained_imports_kt", retained),
                        ("apparent_consumption_kt", apparent),
                    )
                    if value is None
                ]
            )
    return {
        "retained_imports_kt": (
            _round(retained)
            if retained is not None
            else NOT_CALCULABLE
        ),
        "net_import_exposure_kt": (
            _round(net_exposure)
            if net_exposure is not None
            else NOT_CALCULABLE
        ),
        "apparent_consumption_kt": (
            _round(apparent)
            if apparent is not None
            else NOT_CALCULABLE
        ),
        "retained_import_share_of_apparent_consumption": (
            _round(penetration)
            if penetration is not None
            else NOT_CALCULABLE
        ),
        "calculation_basis": basis,
        "unavailable_inputs": unavailable_inputs,
        "unavailable_reasons": reasons,
    }


def _domestic_penetration_full_precision(
    latest_trade: dict[str, Any],
    domestic_flows: dict[str, Any],
) -> float | None:
    """Return unrounded import penetration for threshold comparison."""
    gross_imports = _finite_number(latest_trade.get("imports_kt"))
    retained = _finite_number(
        domestic_flows.get("retained_imports_kt")
    )
    reexports = _finite_number(domestic_flows.get("reexports_kt"))
    if retained is None and gross_imports is not None and reexports is not None:
        retained = gross_imports - reexports
    production = _finite_number(
        domestic_flows.get("domestic_production_kt")
    )
    domestic_exports = _finite_number(
        domestic_flows.get("domestic_origin_exports_kt")
    )
    if (
        retained is None
        or production is None
        or domestic_exports is None
    ):
        return None
    apparent = production + retained - domestic_exports
    if apparent <= 0:
        return None
    return retained / apparent


def export_import_value_ratio(
    trade_row: dict[str, Any],
) -> dict[str, Any]:
    """Compute gross export/import value ratio and retain disclosure."""
    imports = _finite_number(trade_row.get("imports_usd_m"))
    exports = _finite_number(trade_row.get("exports_usd_m"))
    disclosed = _finite_number(
        trade_row.get("export_import_value_ratio")
    )
    if (
        imports is None
        or exports is None
        or imports <= 0
        or exports <= 0
    ):
        missing = [
            name
            for name, value in (
                ("imports_usd_m", imports),
                ("exports_usd_m", exports),
            )
            if value is None or value <= 0
        ]
        return {
            "status": NOT_CALCULABLE,
            "computed_export_import_value_ratio": None,
            "disclosed_export_import_value_ratio": disclosed,
            "disclosed_ratio_consistent": None,
            "export_import_value_ratio": None,
            "ratio_basis": "gross_trade_value",
            "reason": (
                "Positive numeric "
                + " and ".join(missing)
                + " are required."
            ),
        }
    computed = exports / imports
    consistent = (
        abs(disclosed - computed) <= 5 / 100
        if disclosed is not None
        else None
    )
    return {
        "status": "CALCULABLE",
        "computed_export_import_value_ratio": _round(computed),
        "disclosed_export_import_value_ratio": disclosed,
        "disclosed_ratio_consistent": consistent,
        "export_import_value_ratio": (
            disclosed if disclosed is not None else _round(computed)
        ),
        "ratio_basis": "gross_trade_value",
        "reason": None,
    }


def _export_import_ratio_full_precision(
    trade_row: dict[str, Any],
) -> float | None:
    """Return the unrounded positive gross trade-value ratio."""
    imports = _finite_number(trade_row.get("imports_usd_m"))
    exports = _finite_number(trade_row.get("exports_usd_m"))
    if (
        imports is None
        or exports is None
        or imports <= 0
        or exports <= 0
    ):
        return None
    return exports / imports


def established_domestic_nameplate(
    capability: dict[str, Any],
) -> dict[str, Any]:
    """Project established observed A/B/C producer nameplate evidence."""
    if capability.get("verified_present") is not True:
        return {
            "established": False,
            "total_observed_nameplate_tpy": NOT_CALCULABLE,
            "producers": [],
            "evidence_ids": [],
            "reason": "Verified domestic capability is not established.",
        }
    producers = capability.get("producer_evidence")
    if not isinstance(producers, list):
        producers = []
    accepted: list[tuple[str, float, str]] = []
    for producer in producers:
        if not isinstance(producer, dict):
            continue
        capacity = _finite_number(producer.get("installed_capacity_tpy"))
        source = producer.get("nameplate_source_evidence_id")
        references = producer.get("evidence_ids")
        if (
            capacity is None
            or capacity <= 0
            or producer.get("nameplate_status") != "observed"
            or producer.get("evidence_class") not in {"A", "B", "C"}
            or not isinstance(source, str)
            or source == UNAVAILABLE
            or not isinstance(references, list)
            or source not in references
        ):
            continue
        accepted.append((str(producer.get("producer")), capacity, source))
    if not accepted:
        return {
            "established": False,
            "total_observed_nameplate_tpy": NOT_CALCULABLE,
            "producers": [],
            "evidence_ids": [],
            "reason": "No positive observed A/B/C producer nameplate exists.",
        }
    return {
        "established": True,
        "total_observed_nameplate_tpy": _round(
            sum(item[1] for item in accepted)
        ),
        "producers": [item[0] for item in accepted],
        "evidence_ids": [item[2] for item in accepted],
        "reason": None,
    }


def build_supplier_metrics(
    case: dict[str, Any],
    r3_metrics: dict[str, Any],
    r4d_metrics: dict[str, Any],
) -> dict[str, Any] | None:
    """Project the additive v2 metrics into the existing flat UI contract."""
    del case
    value = r3_metrics.get("value")
    quantity = r3_metrics.get("quantity")
    if (
        not isinstance(value, dict)
        or not isinstance(quantity, dict)
        or (
            value.get("status") != "FULL"
            and quantity.get("status") != "FULL"
        )
    ):
        return None
    projection: dict[str, Any] = {
        "partner_value_hhi": value.get("hhi", NOT_CALCULABLE),
        "largest_supplier_share": value.get(
            "largest_supplier_share",
            NOT_CALCULABLE,
        ),
        "top_two_value_share": value.get(
            "top_two_share",
            NOT_CALCULABLE,
        ),
        "partner_quantity_hhi": quantity.get("hhi", NOT_CALCULABLE),
        "largest_supplier_quantity_share": quantity.get(
            "largest_supplier_share",
            NOT_CALCULABLE,
        ),
        "bulk_uv_range_usd_t": r4d_metrics.get(
            "bulk_band_usd_t",
            NOT_CALCULABLE,
        ),
    }
    outlier = r4d_metrics.get("outlier_candidate")
    if isinstance(outlier, dict):
        projection["small_high_uv_observation"] = {
            "partner": outlier["partner"],
            "quantity_kt": outlier.get(
                "net_weight_kt",
                NOT_CALCULABLE,
            ),
            "uv_usd_t": outlier["unit_value_usd_t"],
        }
    else:
        projection["small_high_uv_observation"] = NOT_CALCULABLE
    return projection
