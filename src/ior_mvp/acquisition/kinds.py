"""Snapshot kind behavior and source-contract provenance pins."""

from __future__ import annotations

from dataclasses import dataclass, fields
from math import isfinite
from datetime import date
from enum import StrEnum
from typing import Any, Callable, Mapping

from .contracts import DirectoryRow, ProductionObservation, RegistryRow, Stage, canonical_dumps, source_tag, stage_spec


class CompletenessPolicy(StrEnum):
    ALL_UNITS_COMPLETE = "ALL_UNITS_COMPLETE"
    AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS = "AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS"


@dataclass(frozen=True)
class KindSpec:
    kind: str
    stage: Stage
    root: str
    schema_version: str
    id_prefix: str
    id_includes_nomenclature: bool
    rows_key: str
    row_sort_key: Callable[[dict[str, Any]], Any]
    formula: str
    supports: tuple[str, ...]
    measurement_key: str
    completeness_policy: CompletenessPolicy
    config_version: str
    extra_fields: Callable[[Mapping], dict[str, Any]]
    validator_extra: Callable[[dict[str, Any]], None]


class KindRegistry:
    def __init__(self, mapping: Mapping[str, KindSpec]) -> None:
        self._mapping = dict(mapping)
        for kind, spec in self._mapping.items():
            if kind != spec.kind:
                raise ValueError(f"Kind registration mismatch: {kind}")
            stage_spec(spec.stage)

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._mapping))

    def get(self, kind: str) -> KindSpec:
        try:
            return self._mapping[kind]
        except KeyError as exc:
            raise ValueError(f"Unknown snapshot kind: {kind}") from exc

    def roots(self) -> dict[str, str]:
        return {kind: self.get(kind).root for kind in self.ids()}

    def stage_for(self, kind: str) -> Stage:
        return self.get(kind).stage

    def snapshot_id(self, kind: str, *, source_id: str, nomenclature: str, as_of_date: date) -> str:
        spec = self.get(kind)
        classification = f"-{nomenclature}" if spec.id_includes_nomenclature else ""
        return f"{spec.id_prefix}-SAU-{source_tag(source_id)}{classification}-{as_of_date.isoformat()}"


def _universe_extra(selected: Mapping) -> dict[str, Any]:
    return {"reporter": "SAU", "partner": "WLD", "product_scope": "ALL_HS6",
            "flows": sorted({key[0] for key in selected}), "periods": sorted({key[1] for key in selected})}


def _no_extra(selected: Mapping) -> dict[str, Any]:
    del selected
    return {}


def _validate_universe(record: dict[str, Any]) -> None:
    if record.get("product_scope") != "ALL_HS6":
        raise ValueError("universe product_scope must be ALL_HS6")
    rows = record.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("universe rows must be non-empty")
    revisions_by_unit: dict[tuple[Any, Any], set[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("universe rows must be objects")
        revision = row.get("hs_revision")
        if not isinstance(revision, str) or not revision:
            raise ValueError("universe row hs_revision must be non-empty")
        unit = (row.get("year"), row.get("flow"))
        revisions_by_unit.setdefault(unit, set()).add(revision)
    if any(len(revisions) != 1 for revisions in revisions_by_unit.values()):
        raise ValueError("universe unit must carry one classification")
    coverage = record["coverage"]
    if coverage.get("status") != "COMPLETE":
        raise ValueError("universe coverage must be COMPLETE")
    for unit in coverage.get("units", []):
        if unit.get("status") != "COMPLETE":
            raise ValueError("universe unit must be COMPLETE")
        if unit.get("completeness_basis") == "UNAVAILABLE":
            raise ValueError("universe unit basis must not be UNAVAILABLE")


def _validate_tariff(record: dict[str, Any]) -> None:
    coverage = record["coverage"]
    if coverage.get("status") != "COMPLETE":
        raise ValueError("tariff coverage must be COMPLETE")
    if len(coverage.get("units", [])) != 1:
        raise ValueError("tariff snapshot requires exactly one unit")


def _validate_exclusions(record: dict[str, Any]) -> None:
    coverage = record["coverage"]
    if coverage.get("units_complete", 0) < 1:
        raise ValueError(f"{record['kind']} requires units_complete >= 1")
    if coverage.get("units_excluded") != record.get("transformation_record", {}).get("exclusions", []):
        raise ValueError(f"{record['kind']} exclusions mismatch")


def _validate_institutional(record: dict[str, Any], row_type: type) -> None:
    _validate_exclusions(record)
    rows = record.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Institutional snapshot requires rows")
    expected = {field.name for field in fields(row_type)}
    for row in rows:
        if not isinstance(row, dict) or set(row) != expected:
            raise ValueError("Institutional row shape mismatch")
        for key, value in row.items():
            if key == "value":
                if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)):
                    raise ValueError("Invalid production value")
            elif key == "estimation_flags":
                if not isinstance(value, (list, tuple)) or any(not isinstance(flag, str) for flag in value):
                    raise ValueError("Invalid estimation flags")
            elif not isinstance(value, str):
                raise ValueError(f"Institutional text field must be string: {key}")
        if row_type is RegistryRow and row["registry"] not in {"saso_catalogue", "saber_registry"}:
            raise ValueError("Invalid registry identity")


def default_kind_registry() -> KindRegistry:
    """Governed snapshot kinds with independently pinned source-contract versions."""
    return KindRegistry({
        "universe": KindSpec("universe", Stage.UNIVERSE, "data/snapshots/universe", "1.0.0", "UNIVERSE", True, "rows",
            lambda row: (row.get("year", 0), row.get("hs6", "")), "normalize_trade_rows", ("TRADE_VALUE", "TRADE_QUANTITY"),
            "row_count", CompletenessPolicy.ALL_UNITS_COMPLETE, "1.3.0", _universe_extra, _validate_universe),
        "tariff": KindSpec("tariff", Stage.TARIFF, "data/snapshots/tariff", "1.0.0", "TARIFF", False, "lines",
            lambda row: row.get("national_code", ""), "normalize_tariff_lines", ("NATIONAL_TARIFF_LINE_MAPPING",),
            "line_count", CompletenessPolicy.ALL_UNITS_COMPLETE, "1.0.0", _no_extra, _validate_tariff),
        "partners": KindSpec("partners", Stage.PARTNERS, "data/snapshots/partners", "1.0.0", "PARTNERS", False, "rows",
            lambda row: (row.get("hs6", ""), row.get("partner", "")), "normalize_partner_rows", ("TRADE_VALUE", "TRADE_QUANTITY"),
            "row_count", CompletenessPolicy.AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS, "1.0.0", _no_extra, _validate_exclusions),
        "production": KindSpec("production", Stage.AGGREGATE, "data/snapshots/production", "1.0.0", "PRODUCTION", False, "rows",
            lambda row: (row["period_text"], row["source_dataset_id"], row["indicator_text"], canonical_dumps(row)),
            "normalize_production_rows", ("DOMESTIC_PRODUCTION_AGGREGATE",), "row_count",
            CompletenessPolicy.AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS, "1.1.0", _no_extra,
            lambda record: _validate_institutional(record, ProductionObservation)),
        "directory": KindSpec("directory", Stage.DIRECTORY, "data/snapshots/directory", "1.0.0", "DIRECTORY", False, "rows",
            lambda row: (row["source_record_id"], canonical_dumps(row)), "normalize_directory_rows",
            ("ESTABLISHMENT_LICENCE_DIRECTORY",), "row_count",
            CompletenessPolicy.AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS, "1.1.0", _no_extra,
            lambda record: _validate_institutional(record, DirectoryRow)),
        "registry": KindSpec("registry", Stage.REGISTRY, "data/snapshots/registry", "1.0.0", "REGISTRY", False, "rows",
            lambda row: (row["registry"], row["source_record_id"], canonical_dumps(row)), "normalize_registry_rows",
            ("STANDARD_CONFORMITY_REGISTRY",), "row_count",
            CompletenessPolicy.AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS, "1.1.0", _no_extra,
            lambda record: _validate_institutional(record, RegistryRow)),
    })
