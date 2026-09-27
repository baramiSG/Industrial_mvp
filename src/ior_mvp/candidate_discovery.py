from __future__ import annotations

from typing import Any, Mapping

from .candidate_finding_rules import evaluate_findings, next_request
from .line_contract import _required_pointer_value
from .line_comparison import required_quantity_kt
from .rules import evaluate_r9s
from .screening.config import family_for_hs6

_SIGNAL_TYPES = frozenset(
    {
        "matching_feedstock",
        "core_process",
        "equipment",
        "adjacent_output",
        "relevant_certification",
        "imported_inputs",
    }
)

def _items(candidate_lines: Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
    if not isinstance(candidate_lines, Mapping):
        return []
    additions = candidate_lines.get("requirements_additions")
    if not isinstance(additions, Mapping):
        return []
    items = additions.get("discovery_items")
    return [item for item in items if isinstance(item, Mapping)] if isinstance(items, list) else []

def _facts(register: Mapping[str, Any], kind: str) -> list[Mapping[str, Any]]:
    return [
        fact
        for fact in register["facts"]
        if fact["kind"] == kind
    ]

def _attributed_plant(register: Mapping[str, Any], fact_id: str) -> str | None:
    owners = [
        link["plant_id"]
        for link in register["attribution_links"]
        if link["fact_id"] == fact_id
    ]
    if len(owners) == 1:
        return owners[0]
    return None


def _family_id(opportunity_hs6: str) -> str | None:
    family = family_for_hs6(opportunity_hs6)
    if family is None:
        return None
    return str(family["family_id"])


def _plant_facts(
    register: Mapping[str, Any],
    plant_id: str,
    kind: str,
) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for fact in _facts(register, kind):
        if fact["subject_type"] == "PLANT" and fact["subject_id"] == plant_id:
            rows.append(fact)
            continue
        if (
            fact["subject_type"] == "COMPANY"
            and _attributed_plant(register, fact["fact_id"]) == plant_id
        ):
            rows.append(fact)
    return rows

def _selected_coverage(
    register: Mapping[str, Any],
    subject_type: str,
    subject_id: str,
    company_id: str | None = None,
) -> list[Mapping[str, Any]]:
    """Select only declared extract rows covering this exact subject."""
    return [
        row for row in register["coverage"]
        if (
            row["subject_type"] == subject_type
            and subject_id in row["covered_subject_ids"]
        ) or (
            subject_type == "PLANT" and company_id is not None
            and row["subject_type"] == "COMPANY"
            and company_id in row["covered_subject_ids"]
        )
    ]


def _selected_facts(
    register: Mapping[str, Any], subject_type: str, subject_id: str,
) -> dict[str, list[Mapping[str, Any]]]:
    kinds = {fact["kind"] for fact in register["facts"]}
    if subject_type == "PLANT":
        return {kind: _plant_facts(register, subject_id, kind) for kind in kinds}
    return {
        kind: [
            fact for fact in _facts(register, kind)
            if fact["subject_type"] == subject_type and fact["subject_id"] == subject_id
        ]
        for kind in kinds
    }


def _plant_basis(
    register: Mapping[str, Any],
    plant_id: str,
    target_family: str | None,
    related_hs4: list[str],
) -> dict[str, Any]:
    registry = _plant_facts(register, plant_id, "REGISTRY_ACTIVITY")
    production = _plant_facts(register, plant_id, "PRODUCTION_ACTUAL")
    operating = next((
        fact for fact in registry
        if fact["values"]["country"] == "SA"
        and fact["values"]["status"] == "OPERATING"
        and fact["values"]["operating_status_asserted_by_registry"] is True
    ), None)
    family = next((
        fact for fact in registry
        if fact["values"]["product_family"] == target_family
    ), None)
    related = [
        fact for fact in production
        if fact["values"]["production_kind"] == "OWN_PRODUCTION"
        and any(fact["values"]["hs6"].startswith(heading) for heading in related_hs4)
    ]
    target_output = []
    for fact in production:
        member = family_for_hs6(fact["values"]["hs6"])
        if (
            fact["values"]["production_kind"] == "OWN_PRODUCTION"
            and member is not None and member["family_id"] == target_family
        ):
            target_output.append(fact)
    return {
        "same_family": operating is not None and family is not None,
        "prerequisite_fact_ids": {
            fact["fact_id"] for fact in (operating, family) if fact is not None
        },
        "target_output_fact_ids": frozenset(
            fact["fact_id"] for fact in target_output
        ),
        "related": related,
        "registry": registry,
    }


def _signals(
    pairs: list[tuple[dict[str, Any], tuple[tuple[str, str], ...]]],
    prerequisite_ids: set[str],
    target_output_fact_ids: frozenset[str],
) -> list[dict[str, Any]]:
    signal_for_rule = {
        "P02": "adjacent_output",
        "P03": "imported_inputs",
        "P04": "equipment",
        "P05": "core_process",
        "P07": "relevant_certification",
    }
    signals: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for finding, support in pairs:
        if finding["status"] != "SUPPORTED":
            continue
        if finding["rule_id"] == "P04" and finding["reason_code"] != "P04_GALVANISING_ACQUISITION":
            continue
        signal_type = signal_for_rule.get(finding["rule_id"])
        if signal_type not in _SIGNAL_TYPES:
            continue
        ids = list(dict.fromkeys(
            fact_id for fact_id, _ in support if fact_id not in prerequisite_ids
            and (finding["rule_id"] != "P02" or fact_id in target_output_fact_ids)
        ))
        key = (signal_type, tuple(ids))
        if ids and key not in seen:
            signals.append({"signal_type": signal_type, "evidence_ids": ids})
            seen.add(key)
    return signals


def _disposition(
    same_family: bool, fired: bool, related: list[Mapping[str, Any]],
    registry: list[Mapping[str, Any]], target_family: str | None,
) -> str:
    if same_family and fired:
        return "PASS_TO_ASSESSMENT"
    if related and not same_family:
        return "RELATED_ONLY"
    if any(fact["values"]["status"] == "UNDER_ESTABLISHMENT" for fact in registry):
        return "NOT_ESTABLISHED"
    if target_family is None:
        return "NOT_ESTABLISHED"
    if registry and not same_family and not related:
        return "OUTSIDE_TARGET"
    return "NOT_ESTABLISHED"


def discover_candidates(
    register: Mapping[str, Any],
    *,
    opportunity_id: str,
    opportunity_hs6: str,
    candidate_lines: Mapping[str, Any] | None,
    scenario_id: str,
    scenario: Mapping[str, Any] | None = None,
    line_assessment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose scoped record findings, then run the unchanged per-plant R9-S."""
    target_family = _family_id(opportunity_hs6)
    items = _items(candidate_lines)
    related_hs4 = [
        str(code) for item in items if item["item_id"] == "target_family"
        for code in item.get("related_hs4", [])
    ]
    requirement_items: list[Mapping[str, Any]] = []
    required_quantity = required_quantity_kt(scenario) if scenario is not None and candidate_lines is not None else None
    if candidate_lines is not None:
        for item in candidate_lines["requirement_items"]:
            required = None
            if scenario is not None:
                required = _required_pointer_value(scenario, item["required_value_ref"])
            requirement_items.append({**item, "required_value": required})
    line_to_plant = {
        line["line_id"]: line["plant_id"] for line in register["lines"]
    }
    assessment_rows = {
        row["line_id"]: row for row in line_assessment.get("rows", [])
    } if line_assessment is not None else {}
    rows: list[dict[str, Any]] = []
    plants_by_company: dict[str, list[Mapping[str, Any]]] = {}
    lines_by_plant: dict[str, list[str]] = {}
    for plant in register["plants"]:
        plants_by_company.setdefault(plant["company_id"], []).append(plant)
    for line_id, plant_id in line_to_plant.items():
        lines_by_plant.setdefault(plant_id, []).append(line_id)
    for company in sorted(register["companies"], key=lambda row: row["company_id"]):
        company_id = company["company_id"]
        plants = plants_by_company.get(company_id, [])
        company_facts = _selected_facts(register, "COMPANY", company_id)
        pairs = evaluate_findings(
            subject_type="COMPANY", subject_id=company_id,
            target_family=target_family, items=items,
            requirement_items=requirement_items,
            facts_by_kind=company_facts,
            coverage_rows=_selected_coverage(register, "COMPANY", company_id),
            line_assessments=assessment_rows, line_to_plant=line_to_plant,
            target_output_fact_ids=frozenset(),
        )
        findings = [finding for finding, _ in pairs]
        actions = [
            finding["next_evidence"] for finding in findings
            if finding["next_evidence"] is not None
        ]
        if not plants:
            actions.append(next_request(
                "line-level production or producer-grade matrix",
                "plant_id", "REGISTRY", company_id,
            ))
        rows.append({
            "entity_id": company_id, "entity_kind": "COMPANY",
            "company_id": company_id, "assessment_depth": "REGISTER_ONLY",
            "disposition": "NOT_ESTABLISHED", "findings": findings,
            "evidence_boundary": {"company_only": not bool(plants)},
            "next_evidence_actions": actions, "scenario_id": scenario_id,
        })
        if not plants:
            continue
        for plant in plants:
            plant_id = plant["plant_id"]
            basis = _plant_basis(register, plant_id, target_family, related_hs4)
            pairs = evaluate_findings(
                subject_type="PLANT", subject_id=plant_id,
                target_family=target_family, items=items,
                requirement_items=requirement_items,
                facts_by_kind=_selected_facts(register, "PLANT", plant_id),
                coverage_rows=_selected_coverage(
                    register, "PLANT", plant_id, company_id,
                ),
                line_assessments=assessment_rows, line_to_plant=line_to_plant,
                target_output_fact_ids=basis["target_output_fact_ids"],
                company_context_facts=company_facts.get("FACTORY_CUSTOMS", []),
                company_id=company_id,
            )
            signals = _signals(
                pairs, basis["prerequisite_fact_ids"], basis["target_output_fact_ids"],
            )
            r9s = evaluate_r9s({
                "same_process_family": basis["same_family"],
                "coarse_adjacency_signals": signals,
                "unresolved_hard_gates": [],
                "profile_hard_gates": {},
            })
            disposition = _disposition(
                basis["same_family"], r9s["fired"], basis["related"],
                basis["registry"], target_family,
            )
            findings = [finding for finding, _ in pairs]
            actions = [
                finding["next_evidence"] for finding in findings
                if finding["next_evidence"] is not None
            ]
            if not lines_by_plant.get(plant_id):
                actions.append(next_request(
                    "line-level production or producer-grade matrix",
                    "line_id", "TECHNICAL_ENRICHMENT", plant_id,
                ))
            rows.append({
                "entity_id": plant_id, "entity_kind": "PLANT",
                "company_id": company_id, "assessment_depth": "REGISTER_ONLY",
                "disposition": disposition, "r9s": r9s,
                "findings": findings,
                "evidence_boundary": {
                    "target_family": target_family,
                    "signal_fact_ids": [
                        signal["evidence_ids"][0] for signal in signals
                    ],
                },
                "next_evidence_actions": actions, "scenario_id": scenario_id,
            })
            if line_assessment is None:
                continue
            for line_id in sorted(lines_by_plant.get(plant_id, [])):
                if line_id not in assessment_rows:
                    continue
                line_pairs = evaluate_findings(
                    subject_type="LINE", subject_id=line_id,
                    target_family=target_family, items=items,
                    requirement_items=requirement_items,
                    facts_by_kind=_selected_facts(register, "LINE", line_id),
                    coverage_rows=_selected_coverage(register, "LINE", line_id),
                    line_assessments=assessment_rows, line_to_plant=line_to_plant,
                    target_output_fact_ids=frozenset(),
                    required_quantity_kt=required_quantity,
                )
                line_findings = [finding for finding, _ in line_pairs]
                rows.append({
                    "entity_id": line_id, "entity_kind": "LINE",
                    "company_id": company_id, "plant_id": plant_id,
                    "assessment_depth": "ENRICHED" if line_id in assessment_rows else "REGISTER_ONLY",
                    "disposition": disposition,
                    "findings": line_findings,
                    "evidence_boundary": {"target_family": target_family},
                    "next_evidence_actions": [
                        finding["next_evidence"] for finding in line_findings
                        if finding["next_evidence"] is not None
                    ],
                    "scenario_id": scenario_id,
                })
    return {
        "available": True, "reason": None,
        "opportunity_id": opportunity_id, "scenario_id": scenario_id,
        "target_family": target_family, "rows": rows,
    }

def unavailable_discovery(reason: str) -> dict[str, Any]:
    """Return a typed empty discovery result for older scenarios."""
    if reason not in {"NO_REGISTER", "NO_LINE_RECORDS"}:
        raise ValueError(f"Unknown discovery unavailability: {reason}")
    return {"available": False, "reason": reason, "rows": []}
