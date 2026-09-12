"""Harmonisation helpers for trade and tariff observations."""

from __future__ import annotations

from typing import Any, Mapping
from dataclasses import fields
from math import isfinite

from .contracts import UNAVAILABLE, DirectoryRow, ProductionObservation, RegistryRow, TariffLine, TradeObservation

PIPELINE_VERSION = "1.0.0"


def _published_fields(row: Mapping[str, Any], field_map: Mapping[str, str],
                      row_type: type, source_evidence_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field in fields(row_type):
        if field.name in {"value", "estimation_flags", "source_evidence_id"}:
            continue
        value = row.get(field_map.get(field.name, field.name))
        if value is None:
            value = UNAVAILABLE
        if not isinstance(value, str):
            raise ValueError(f"Published text must be a string: {field.name}")
        result[field.name] = value
    result["source_evidence_id"] = source_evidence_id
    return result


def production_observation_from_row(row: Mapping[str, Any], *, field_map: Mapping[str, str],
                                    source_evidence_id: str) -> ProductionObservation:
    """Preserve published production fields without conversion or HS mapping."""
    values = _published_fields(row, field_map, ProductionObservation, source_evidence_id)
    number = row.get(field_map.get("value", "value"))
    if number is None:
        try:
            number = float(values["value_original_text"])
        except ValueError:
            number = None
    if number is not None:
        if isinstance(number, bool) or not isinstance(number, (str, int, float)):
            raise ValueError("Production value must be an observed number")
        number = float(number)
        if not isfinite(number):
            raise ValueError("Production value must be finite")
    flags = row.get(field_map.get("estimation_flags", "estimation_flags"), ())
    if flags is None:
        flags = ()
    if not isinstance(flags, (list, tuple)) or any(not isinstance(flag, str) for flag in flags):
        raise ValueError("Estimation flags must be published strings")
    return ProductionObservation(**values, value=number, estimation_flags=tuple(flags))


def directory_row_from_row(row: Mapping[str, Any], *, field_map: Mapping[str, str],
                           source_evidence_id: str) -> DirectoryRow:
    """Retain organizational directory text; never infer numeric capacity."""
    return DirectoryRow(**_published_fields(row, field_map, DirectoryRow, source_evidence_id))


def registry_row_from_row(row: Mapping[str, Any], *, field_map: Mapping[str, str],
                          source_evidence_id: str) -> RegistryRow:
    """Retain registry metadata without asserting compliance or qualification."""
    values = _published_fields(row, field_map, RegistryRow, source_evidence_id)
    if values["registry"] not in {"saso_catalogue", "saber_registry"}:
        raise ValueError("Unknown institutional registry")
    return RegistryRow(**values)


def unit_value_analysis_enabled(obs: TradeObservation) -> bool:
    """Return False when weight is missing, estimated or incomparable."""
    if obs.net_weight is None:
        return False
    if "estimated" in obs.estimation_flags:
        return False
    if not obs.weight_unit or obs.weight_unit == UNAVAILABLE:
        return False
    return True


def trade_observation_from_row(
    row: Mapping[str, Any],
    *,
    field_map: Mapping[str, str],
    reporter_expected: str,
    hs_revision: str,
    source_evidence_id: str,
    valuation_by_flow: Mapping[str, str],
) -> TradeObservation:
    """Map one raw row to a TradeObservation."""
    flow = str(row.get(field_map.get("flow", "flow"), ""))
    valuation = valuation_by_flow.get(flow, UNAVAILABLE)
    weight_text = str(row.get(field_map.get("net_weight", "net_weight"), ""))
    weight_val = row.get(field_map.get("net_weight_value", "net_weight_value"))
    value_text = str(row.get(field_map.get("trade_value", "trade_value"), ""))
    value_val = row.get(field_map.get("trade_value_value", "trade_value_value"))
    estimation: list[str] = []
    if row.get("estimated"):
        estimation.append("estimated")
    obs = TradeObservation(
        year=int(row.get(field_map.get("year", "year"), 0)),
        reporter=str(row.get(field_map.get("reporter", "reporter"), reporter_expected)),
        partner=str(row.get(field_map.get("partner", "partner"), "")),
        flow=flow,
        hs_revision=hs_revision,
        hs6=str(row.get(field_map.get("hs6", "hs6"), "")),
        national_tariff_line=row.get(field_map.get("national_tariff_line", "national_tariff_line")),
        trade_value_original_text=value_text,
        trade_value=float(value_val) if value_val is not None else None,
        currency=str(row.get(field_map.get("currency", "currency"), UNAVAILABLE)),
        valuation=valuation,
        net_weight_original_text=weight_text,
        net_weight=float(weight_val) if weight_val is not None else None,
        weight_unit=str(row.get(field_map.get("weight_unit", "weight_unit"), UNAVAILABLE)),
        supplementary_quantity=row.get(field_map.get("supplementary_quantity", "supplementary_quantity")),
        supplementary_unit=row.get(field_map.get("supplementary_unit", "supplementary_unit")),
        estimation_flags=tuple(estimation),
        unit_value_analysis_enabled=False,
        gross_flow=bool(row.get("gross_flow", True)),
        reexport_status=str(row.get("reexport_status", UNAVAILABLE)),
        source_evidence_id=source_evidence_id,
    )
    return TradeObservation(
        year=obs.year,
        reporter=obs.reporter,
        partner=obs.partner,
        flow=obs.flow,
        hs_revision=obs.hs_revision,
        hs6=obs.hs6,
        national_tariff_line=obs.national_tariff_line,
        trade_value_original_text=obs.trade_value_original_text,
        trade_value=obs.trade_value,
        currency=obs.currency,
        valuation=obs.valuation,
        net_weight_original_text=obs.net_weight_original_text,
        net_weight=obs.net_weight,
        weight_unit=obs.weight_unit,
        supplementary_quantity=obs.supplementary_quantity,
        supplementary_unit=obs.supplementary_unit,
        estimation_flags=obs.estimation_flags,
        unit_value_analysis_enabled=unit_value_analysis_enabled(obs),
        gross_flow=obs.gross_flow,
        reexport_status=obs.reexport_status,
        source_evidence_id=obs.source_evidence_id,
    )


def tariff_line_from_row(
    row: Mapping[str, Any],
    *,
    field_map: Mapping[str, str],
    hs_revision: str,
    source_evidence_id: str,
) -> TariffLine:
    """Map one raw row to a TariffLine."""
    national_code = str(row.get(field_map.get("national_code", "national_code"), ""))
    hs6 = str(row.get(field_map.get("hs6", "hs6"), ""))
    if len(national_code) != 12:
        raise ValueError(f"national_code must be 12 digits: {national_code!r}")
    if len(hs6) != 6:
        raise ValueError(f"hs6 must be 6 digits: {hs6!r}")
    return TariffLine(
        national_code=national_code,
        hs6=hs6,
        hs6_mapping_basis=str(
            row.get(field_map.get("hs6_mapping_basis", "hs6_mapping_basis"), "prefix_6")
        ),
        description_ar=str(row.get(field_map.get("description_ar", "description_ar"), "")),
        description_en=str(row.get(field_map.get("description_en", "description_en"), "")),
        duty_fields=tuple(
            sorted(
                (str(k), str(v))
                for k, v in row.get(field_map.get("duty_fields", "duty_fields"), {}).items()
            )
        ),
        reported_nomenclature=hs_revision,
        source_evidence_id=source_evidence_id,
    )


def transformation_record(
    *,
    formula: str,
    parameters: dict[str, Any],
    exclusions: list[dict[str, Any]],
    pipeline_version: str = PIPELINE_VERSION,
    config_version: str,
) -> dict[str, Any]:
    """Build transformation_record block for snapshots."""
    return {
        "formula": formula,
        "parameters": parameters,
        "exclusions": exclusions,
        "pipeline_version": pipeline_version,
        "config_version": config_version,
    }
