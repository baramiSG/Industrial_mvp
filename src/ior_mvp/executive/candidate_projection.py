"""Project validated simulation diagnostics into strict executive DTOs."""

from __future__ import annotations

from typing import Any, Mapping

from .line_models import (
    CandidateDiagnostic, CandidateRow, LineDiagnostic, LineRow, R9SScreen,
    TargetRequirement,
    unavailable_candidates, unavailable_lines,
)
from .provenance_models import EvidenceClass
from ..line_comparison import required_quantity_kt


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def build_candidate_diagnostics(
    simulated: Mapping[str, Any] | None,
    opportunity_id: str,
    scenario_source: Mapping[str, Any] | None = None,
) -> tuple[CandidateDiagnostic, LineDiagnostic]:
    """Keep public/unavailable branches distinct from Class-D current records."""
    if simulated is None:
        return unavailable_candidates(), unavailable_lines()
    scenario = _mapping(simulated.get("simulation_scenario"), "simulation scenario")
    scenario_id = scenario.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise ValueError("simulation scenario identity is missing")
    discovery = _mapping(simulated.get("candidate_discovery"), "candidate discovery")
    assessment = _mapping(simulated.get("line_assessment"), "line assessment")
    if not discovery.get("available"):
        return (
            unavailable_candidates(discovery["reason"]),
            unavailable_lines(assessment["reason"]),
        )
    if discovery.get("opportunity_id") != opportunity_id:
        raise ValueError("candidate discovery opportunity differs from case")
    if discovery.get("scenario_id") != scenario_id:
        raise ValueError("candidate discovery scenario differs from branch")
    if assessment.get("available") is not True:
        raise ValueError("available register requires a line assessment")
    if scenario_source is None:
        raise ValueError("available diagnostics require the validated source scenario")
    if (scenario_source.get("scenario_id") != scenario_id
            or scenario_source.get("opportunity_id") != opportunity_id):
        raise ValueError("candidate source scenario differs from branch")
    source_inputs = _mapping(scenario_source.get("synthetic_inputs"), "synthetic inputs")
    source_register = _mapping(source_inputs.get("candidate_register"), "candidate register")
    source_lines = _mapping(source_inputs.get("candidate_lines"), "candidate lines")
    additions = _mapping(source_lines.get("requirements_additions"), "requirements additions")
    target = _mapping(source_inputs.get("target_specification"), "target specification")
    specification = {
        key: target[key] for key in
        ("standard", "coating_mass_g_m2", "thickness_mm", "width_mm")
        if key in target
    }
    specification.update({
        key: additions[key] for key in ("mfr_required", "mfr_test_condition")
        if key in additions
    })
    requirement = TargetRequirement.model_validate({
        "target_name": target["name"], "application": target["application"],
        "specification": specification,
        "target_demand_kt": required_quantity_kt(scenario_source),
        "request_window_months": additions["request_window_months"],
    })
    companies = {row["company_id"]: row for row in source_register["companies"]}
    plants = {row["plant_id"]: row for row in source_register["plants"]}
    facts = {fact["fact_id"]: fact for fact in source_register["facts"]}
    effort_by_line = {
        fact["subject_id"]: fact["values"]
        for fact in source_register["facts"] if fact["kind"] == "EFFORT"
    }
    rows = []
    for raw in discovery["rows"]:
        row = _mapping(raw, "candidate row")
        company = companies.get(row["company_id"])
        if company is None:
            raise ValueError("candidate row has no source company")
        plant_id = row.get("plant_id") or (
            row["entity_id"] if row["entity_kind"] == "PLANT" else None
        )
        plant = plants.get(plant_id) if plant_id else None
        if (row["entity_kind"] != "COMPANY" and
                (plant is None or plant["company_id"] != row["company_id"])):
            raise ValueError("candidate row has no owning source plant")
        screen = row.get("r9s")
        r9s = None
        if screen is not None:
            screen = _mapping(screen, "R9-S screen")
            metrics = _mapping(screen.get("metrics"), "R9-S metrics")
            r9s = R9SScreen(
                fired=screen["fired"],
                result_code=screen["result_code"],
                qualifying_signal_count=metrics["qualifying_signal_count"],
            )
        findings = []
        for finding in row["findings"]:
            inputs = []
            for ref in finding["source_refs"]:
                pointer = ref.get("pointer")
                if pointer is None:
                    continue
                fact_id = pointer.removeprefix(
                    "/synthetic_inputs/candidate_register/facts/"
                )
                if fact_id not in facts or not pointer.endswith("/" + fact_id):
                    raise ValueError("finding source pointer does not resolve")
                fact = facts[fact_id]
                record = {
                    "fact_id": fact_id, "origin": fact["origin"],
                    "subject_type": fact["subject_type"],
                    "subject_id": fact["subject_id"], "window": fact["window"],
                }
                if record not in inputs:
                    inputs.append(record)
            findings.append({**finding, "input_records": inputs})
        rows.append(CandidateRow.model_validate({
            **row, "r9s": r9s, "findings": findings,
            "company_name_en": company["name_en"],
            "company_name_ar": company["name_ar"],
            "plant_status": plant["status"] if plant else None,
        }))
    line_rows = []
    for raw in assessment["rows"]:
        row = _mapping(raw, "line row")
        capability = _mapping(row.get("capability"), "line capability")
        line_rows.append(LineRow.model_validate({
            "line_id": row["line_id"],
            "reference_role": row["reference_role"],
            "comparisons": row["comparisons"],
            "gates": row["gates"],
            "gate_requirements": row["gate_requirements"],
            "known_weight_coverage": capability["known_weight_coverage"],
            "d_star": capability["d_star"],
            "dimensions": capability["dimensions"],
            "declared_effort": effort_by_line.get(row["line_id"]),
            "capacity": row["capacity"],
        }))
    return (
        CandidateDiagnostic(
            available=True,
            reason=None,
            opportunity_id=opportunity_id,
            scenario_id=scenario_id,
            target_family=discovery["target_family"],
            requirement=requirement,
            synthetic_flag=True,
            evidence_class=EvidenceClass.D,
            source="DEMO_GENERATOR",
            rows=tuple(rows),
        ),
        LineDiagnostic(
            available=True,
            reason=None,
            scenario_id=scenario_id,
            synthetic_flag=True,
            evidence_class=EvidenceClass.D,
            source="DEMO_GENERATOR",
            rows=tuple(line_rows),
            winner=None,
        ),
    )
