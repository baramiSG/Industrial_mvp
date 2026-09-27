"""Closed record, source and coverage primitives for scenario 2.2."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from functools import lru_cache
from typing import Any, Mapping

from .config import PROJECT_ROOT
from .evidence import EvidenceIntegrityError

COVERAGE_KEYS = frozenset(
    {
        "coverage_id",
        "dataset_kind",
        "window",
        "subject_type",
        "covered_subject_ids",
        "completeness",
    }
)

DATASET_KINDS = frozenset(
    {
        "REGISTRY",
        "PRODUCTION_ACTUALS",
        "FACTORY_CUSTOMS",
        "APPLICATION_TAPE",
        "TECHNICAL_ENRICHMENT",
    }
)

FACT_VALUE_KEYS = {
    "REGISTRY_ACTIVITY": frozenset({"country", "status", "product_family", "process_route", "operating_status_asserted_by_registry"}),
    "PRODUCTION_ACTUAL": frozenset({"hs_revision", "hs6", "production_kind", "process_family", "quantity_kt"}),
    "FACTORY_CUSTOMS": frozenset({"hs_revision", "hs6", "description", "flow", "quantity_kt", "reexport", "transaction_id", "equipment_model_id"}),
    "EQUIPMENT_TECHNICAL": frozenset({"customs_fact_id", "transaction_id", "equipment_model_id", "function", "workpiece_material"}),
    "APPLICATION": frozenset({"stage", "reason_code", "proposed_activity", "proposed_capacity_kt", "proposed_start_month"}),
    "TECHNICAL_FIELD": frozenset({"field_id", "value", "unit", "requirement_id"}),
    "CAPACITY": frozenset({"nameplate_kt", "availability", "yield", "qualification_share", "market_allocation_share", "current_utilisation"}),
    "QUALIFICATION": frozenset({"requirement_id", "application", "customer_status", "valid_window_months"}),
    "WINDOW": frozenset({"available_window_months"}),
    "EFFORT": None,
    "ALLOCATION": frozenset({"qualified_available_kt", "requirement_id", "window_months"}),
    "CEILING": frozenset({"group_id", "ceiling_kind", "value_kt", "basis"}),
    "CERTIFICATE": frozenset({"certificate_kind", "scope", "valid_window_months"}),
}

ORIGINS = frozenset(
    {
        "DIRECT_RECORD",
        "REVIEWED_INFERENCE",
        "ENGINEERING_DECLARATION",
        "UNKNOWN",
    }
)

PLANT_STATUS = frozenset({"OPERATING", "UNDER_ESTABLISHMENT"})

PROCESS_ROUTES = frozenset(
    {"HOT_DIP_GALVANISING", "COLD_ROLLING", "RESIN_PRODUCTION", "OTHER"}
)

HS6_PATTERN = re.compile(r"^[0-9]{6}$")

WINDOW_KEYS = frozenset({"start", "end"})

SOURCE_REF_KEYS = frozenset(
    {"pointer", "artifact", "evidence_id", "purpose", "field"}
)

HS_REVISIONS = frozenset({"H0", "H6"})

EFFORT_DIMENSIONS = frozenset({"feedstock_chemistry", "core_process_route", "equipment_envelope", "finishing_spec_control", "qa_lab_metrology", "certification_customer_qualification", "capacity_time_window", "utilities_ehs_permitting", "skills_market_integration"})

_ENRICHMENT = "TECHNICAL_ENRICHMENT"

KIND_DATASET = {"REGISTRY_ACTIVITY": "REGISTRY", "PRODUCTION_ACTUAL": "PRODUCTION_ACTUALS", "FACTORY_CUSTOMS": "FACTORY_CUSTOMS", "APPLICATION": "APPLICATION_TAPE", **{kind: _ENRICHMENT for kind in ("EQUIPMENT_TECHNICAL", "TECHNICAL_FIELD", "CAPACITY", "QUALIFICATION", "WINDOW", "EFFORT", "ALLOCATION", "CEILING", "CERTIFICATE")}}

TECHNICAL_FIELDS = frozenset({"substrate", "process_route", "thickness_mm", "width_mm", "coating_mass_g_m2", "surface_treatment", "standard", "application", "polymer_family", "manufacturing_scope", "grade_family", "mfr_range_g_10min", "mfr_test_condition", "additives_required", "tooling_required"})

PUBLIC_ARTIFACTS = {
    "data/snapshots/public/SAU-H0-721049.json": (
        "5c2ab676e5b68509e002eddff4f80107c0d2cc1b78c3b063e26f84d13355512e"
    ),
    "data/snapshots/public/SAU-H0-390210.json": (
        "edaeaabf82276f75a1887aa0869b9e3a4070c3338fa0e9f677c55607cd8d0ac4"
    ),
}

CLAIMED_PUBLIC_PURPOSES = frozenset(
    {"observed", "official", "class_a", "class_b", "class_c"}
)

def _fail(message: str) -> None:
    raise EvidenceIntegrityError(message)

def _exact_keys(value: Mapping[str, Any], allowed: frozenset[str], label: str) -> None:
    unknown = set(value) - allowed
    missing = allowed - set(value)
    if unknown or missing:
        _fail(
            f"{label} keys mismatch: unknown={sorted(unknown)} "
            f"missing={sorted(missing)}"
        )

def _window(value: Any, label: str) -> tuple[date, date]:
    if not isinstance(value, dict):
        _fail(f"{label} window must be an object")
    _exact_keys(value, WINDOW_KEYS, f"{label} window")
    try:
        start = date.fromisoformat(value["start"])
        end = date.fromisoformat(value["end"])
    except (TypeError, ValueError):
        _fail(f"{label} window is not a date")
    if start >= end:
        _fail(f"{label} window is not ordered")
    return start, end

def _months(value: Any, label: str) -> None:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in value)
        or value[0] >= value[1]
    ):
        _fail(f"{label} month window is not half-open")

@lru_cache(maxsize=4)
def _public_artifact_text(artifact: str) -> str:
    expected = PUBLIC_ARTIFACTS.get(artifact)
    if expected is None:
        _fail(f"{artifact} is not an allowlisted public source")
    path = PROJECT_ROOT / artifact
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        _fail(f"{artifact} hash does not match the allowlisted source")
    return raw.decode("utf-8")

def _source_refs(value: Any, label: str) -> None:
    if not isinstance(value, list) or not value:
        _fail(f"{label} source_refs must be a non-empty list")
    for index, ref in enumerate(value):
        if not isinstance(ref, dict):
            _fail(f"{label} source_refs[{index}] must be an object")
        unknown = set(ref) - SOURCE_REF_KEYS
        if unknown or not isinstance(ref.get("purpose"), str) or not ref["purpose"]:
            _fail(f"{label} source_refs[{index}] is not an admitted pointer")
        if str(ref["purpose"]).casefold() in CLAIMED_PUBLIC_PURPOSES:
            _fail(f"{label} synthetic ref cannot claim a public evidence class")
        has_pointer = isinstance(ref.get("pointer"), str)
        has_public = isinstance(ref.get("artifact"), str) and isinstance(
            ref.get("evidence_id"), str
        )
        if has_pointer == has_public:
            _fail(f"{label} source_refs[{index}] must be local or public")
        if has_pointer:
            if set(ref) - {"pointer", "purpose", "field"} or not ref["pointer"]:
                _fail(f"{label} source_refs[{index}] local shape is invalid")
            if ref.get("field") is not None and (
                not isinstance(ref["field"], str) or not ref["field"]
            ):
                _fail(f"{label} source_refs[{index}] local field is invalid")
        if has_public:
            if set(ref) != {"artifact", "evidence_id", "purpose", "field"}:
                _fail(f"{label} source_refs[{index}] public shape is invalid")
            field = ref.get("field")
            if not isinstance(field, str) or not field or not ref["evidence_id"]:
                _fail(f"{label} public ref does not name a field")
            text = _public_artifact_text(ref["artifact"])
            if f'"{ref["evidence_id"]}"' not in text or field not in text:
                _fail(f"{label} public ref does not resolve")

def _hs6(value: Any, label: str) -> None:
    if not isinstance(value, str) or HS6_PATTERN.fullmatch(value) is None:
        _fail(f"{label} hs6 must be an exact six-digit string")

def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(f"{label} must be a finite number")
    if value != value or value in {float("inf"), float("-inf")}:
        _fail(f"{label} must be finite")
    return float(value)

def _validate_fact_values(fact: Mapping[str, Any]) -> None:
    kind = fact["kind"]
    values = fact["values"]
    if not isinstance(values, dict):
        _fail(f"{fact['fact_id']} values must be an object")
    allowed = FACT_VALUE_KEYS.get(kind)
    if kind not in FACT_VALUE_KEYS:
        _fail(f"{fact['fact_id']} kind is unknown")
    if KIND_DATASET.get(kind) != fact["dataset_kind"]:
        _fail(f"{fact['fact_id']} dataset_kind does not match its record kind")
    if kind == "EFFORT":
        if set(values) != EFFORT_DIMENSIONS:
            _fail(f"{fact['fact_id']} effort dimensions are not the configured nine")
        for key, raw in values.items():
            if raw == "U":
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= 3:
                _fail(f"{fact['fact_id']} effort {key} is not a declared state")
        return
    _exact_keys(values, allowed, f"{fact['fact_id']} values")
    if kind == "REGISTRY_ACTIVITY":
        if values["status"] not in PLANT_STATUS:
            _fail(f"{fact['fact_id']} status is unknown")
        if values["process_route"] not in PROCESS_ROUTES:
            _fail(f"{fact['fact_id']} process_route is unknown")
        if not isinstance(values["operating_status_asserted_by_registry"], bool):
            _fail(f"{fact['fact_id']} operating assertion must be boolean")
    if kind in {"PRODUCTION_ACTUAL", "FACTORY_CUSTOMS"}:
        if values["hs_revision"] not in HS_REVISIONS:
            _fail(f"{fact['fact_id']} hs_revision is unknown")
        _hs6(values["hs6"], fact["fact_id"])
        if _finite_number(values["quantity_kt"], f"{fact['fact_id']} quantity") < 0:
            _fail(f"{fact['fact_id']} quantity cannot be negative")
    if kind == "PRODUCTION_ACTUAL":
        if values["production_kind"] not in {"OWN_PRODUCTION", "AGGREGATE"}:
            _fail(f"{fact['fact_id']} production_kind is unknown")
    if kind == "FACTORY_CUSTOMS":
        if values["flow"] not in {"IMPORT", "EXPORT"}:
            _fail(f"{fact['fact_id']} flow is unknown")
        if not isinstance(values["reexport"], bool):
            _fail(f"{fact['fact_id']} reexport must be boolean")
        if values["description"] is not None and not isinstance(
            values["description"], str
        ):
            _fail(f"{fact['fact_id']} description must be text or null")
    if kind == "CAPACITY":
        for key, raw in values.items():
            if raw is None:
                continue
            number = _finite_number(raw, f"{fact['fact_id']} {key}")
            if key != "nameplate_kt" and not 0 <= number <= 1:
                _fail(f"{fact['fact_id']} {key} is outside [0,1]")
            if key == "nameplate_kt" and number < 0:
                _fail(f"{fact['fact_id']} nameplate is negative")
    if kind == "TECHNICAL_FIELD":
        if values["field_id"] not in TECHNICAL_FIELDS:
            _fail(f"{fact['fact_id']} technical field is unknown")
        if not isinstance(values["requirement_id"], str) or not values["requirement_id"]:
            _fail(f"{fact['fact_id']} requirement_id is required")
        field = values["field_id"]
        if values["unit"] != TECHNICAL_UNITS[field]:
            _fail(f"{fact['fact_id']} technical unit is wrong")
        _technical_value(field, values["value"], fact["fact_id"])
    if kind == "QUALIFICATION":
        if values["customer_status"] not in {
            "QUALIFIED",
            "NOT_QUALIFIED",
            "NOT_REQUIRED",
            "UNKNOWN",
        }:
            _fail(f"{fact['fact_id']} customer_status is unknown")
        if not isinstance(values["requirement_id"], str) or not values["requirement_id"]:
            _fail(f"{fact['fact_id']} qualification requirement is invalid")
        if not isinstance(values["application"], str) or not values["application"]:
            _fail(f"{fact['fact_id']} qualification application is invalid")
        _months(values["valid_window_months"], fact["fact_id"])
    if kind == "WINDOW":
        _months(values["available_window_months"], fact["fact_id"])
    if kind == "ALLOCATION":
        allocated = _finite_number(
            values["qualified_available_kt"], f"{fact['fact_id']} allocation"
        )
        if allocated < 0:
            _fail(f"{fact['fact_id']} allocation is negative")
        if not isinstance(values["requirement_id"], str) or not values["requirement_id"]:
            _fail(f"{fact['fact_id']} allocation requirement is invalid")
        _months(values["window_months"], fact["fact_id"])
    if kind == "CEILING":
        if values["ceiling_kind"] not in {"PUBLIC_NAMEPLATE", "DECLARED_DESIGN"}:
            _fail(f"{fact['fact_id']} ceiling_kind is unknown")
        if _finite_number(values["value_kt"], fact["fact_id"]) < 0:
            _fail(f"{fact['fact_id']} ceiling is negative")
    if kind == "APPLICATION":
        if values["stage"] not in {"APPLIED", "REJECTED", "APPROVED"}:
            _fail(f"{fact['fact_id']} application stage is unknown")
    if kind == "EQUIPMENT_TECHNICAL":
        if values["function"] not in {
            "HOT_DIP_ZINC_COATING",
            "EXTRUSION",
            "WIRE_COIL_WINDING",
            "OTHER",
        }:
            _fail(f"{fact['fact_id']} equipment function is unknown")
        if values["workpiece_material"] not in {"STEEL_STRIP", "PLASTICS", "OTHER"}:
            _fail(f"{fact['fact_id']} workpiece_material is unknown")
    if kind == "FACTORY_CUSTOMS":
        for key in ("transaction_id", "equipment_model_id"):
            if values[key] is not None and not isinstance(values[key], str):
                _fail(f"{fact['fact_id']} {key} must be text or null")

def _nested_records(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        rows = [value]
        for child in value.values():
            rows.extend(_nested_records(child))
        return rows
    if isinstance(value, list):
        rows = []
        for child in value:
            rows.extend(_nested_records(child))
        return rows
    return []

def _register_source_references(register: Mapping[str, Any]) -> None:
    facts = {fact["fact_id"]: fact for fact in register["facts"]}
    for row in [*register["facts"], *register["attribution_links"]]:
        for ref in row["source_refs"]:
            pointer = ref.get("pointer")
            if pointer is not None:
                prefix = "/synthetic_inputs/candidate_register/facts/"
                if not pointer.startswith(prefix) or pointer[len(prefix):] not in facts:
                    _fail("source_refs local pointer does not resolve")
                source = facts[pointer[len(prefix):]]
                field = ref.get("field")
                if field is not None and field not in source and field not in source["values"]:
                    _fail("source_refs local field does not resolve")
                if "subject_type" in row and (
                    source["subject_type"] != row["subject_type"]
                    or source["subject_id"] != row["subject_id"]
                ):
                    _fail("source_refs local subject does not match")
                continue
            public = json.loads(_public_artifact_text(ref["artifact"]))
            evidence_id = ref["evidence_id"]
            if not any(e.get("evidence_id") == evidence_id for e in public["evidence"]):
                _fail("public ref evidence_id is not a source member")
            field = ref["field"]
            if not any(
                (record.get("evidence_id") == evidence_id and field in record)
                or record.get(field) == evidence_id
                or (evidence_id in record.get("evidence_ids", []) and field in record)
                for record in _nested_records(public)
            ):
                _fail("public ref field is not associated with the source")

def _hs_in(fact: Mapping[str, Any], admitted: list[Any], revision: str) -> bool:
    values = fact["values"]
    if values.get("hs_revision") != revision:
        return False
    return values.get("hs6") in set(admitted)

def _customs_usable(fact: Mapping[str, Any]) -> bool:
    values = fact["values"]
    return values.get("flow") == "IMPORT" and values.get("reexport") is False

def validate_coverage_row(
    row: Mapping[str, Any],
    known_subjects: Mapping[str, set[str]],
) -> None:
    """Validate an extract boundary against caller-supplied subject indexes."""
    if not isinstance(row, Mapping):
        _fail("coverage row must be an object")
    _exact_keys(row, COVERAGE_KEYS, "coverage")
    if not isinstance(row["coverage_id"], str) or not row["coverage_id"]:
        _fail("coverage_id is required")
    if row["dataset_kind"] not in DATASET_KINDS:
        _fail(f"{row['coverage_id']} dataset_kind is unknown")
    _window(row["window"], row["coverage_id"])
    if row["completeness"] not in {"COMPLETE", "INCOMPLETE", "SEARCHED_EMPTY"}:
        _fail(f"{row['coverage_id']} completeness is unknown")
    subjects = known_subjects.get(row["subject_type"])
    if subjects is None:
        _fail(f"{row['coverage_id']} subject_type is unknown")
    covered = row["covered_subject_ids"]
    if not isinstance(covered, list) or any(
        not isinstance(subject, str) or subject not in subjects
        for subject in covered
    ):
        _fail(f"{row['coverage_id']} coverage subject does not resolve")
    if len(covered) != len(set(covered)):
        _fail(f"{row['coverage_id']} repeats a coverage subject")


TECHNICAL_UNITS = {
    "substrate": "class", "process_route": "route", "thickness_mm": "mm",
    "width_mm": "mm", "coating_mass_g_m2": "g/m2",
    "surface_treatment": "treatment", "standard": "standard",
    "application": "application", "polymer_family": "family",
    "manufacturing_scope": "scope", "grade_family": "grade",
    "mfr_range_g_10min": "g_10min", "mfr_test_condition": "condition",
    "additives_required": "boolean", "tooling_required": "boolean",
}

NUMERIC_FIELDS = frozenset({
    "thickness_mm", "width_mm", "coating_mass_g_m2", "mfr_range_g_10min",
})

BOOLEAN_FIELDS = frozenset({"additives_required", "tooling_required"})

def _technical_value(field: str, value: Any, label: str) -> None:
    if value is None:
        return
    if field in BOOLEAN_FIELDS:
        if not isinstance(value, bool):
            _fail(f"{label} must be boolean")
    elif field in NUMERIC_FIELDS:
        numbers = value if isinstance(value, list) else [value]
        if len(numbers) not in {1, 2} or any(
            isinstance(number, bool) or not isinstance(number, (int, float))
            or not math.isfinite(number) or number < 0 for number in numbers
        ):
            _fail(f"{label} must have finite nonnegative numbers")
        if len(numbers) == 2 and numbers[0] > numbers[1]:
            _fail(f"{label} range is inverted")
    elif not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be nonempty text")
