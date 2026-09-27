"""Finite record-to-finding rules for a supplied, validated subject scope."""

from __future__ import annotations

from typing import Any, Mapping

from .candidate_record_contract import _customs_usable, _hs_in
from .evidence_needs import NOT_CALCULABLE, _ROUTE_EFFECTS

FindingSupport = tuple[dict[str, Any], tuple[tuple[str, str], ...]]


def next_request(
    need_code: str, field: str, dataset: str, subject_id: str,
    *, action_code: str | None = None, route_effect: str | None = None,
) -> dict[str, Any]:
    return {
        "need_code": need_code,
        "missing_field": field,
        "dataset_or_action": dataset,
        "route_effect": route_effect or _ROUTE_EFFECTS[need_code],
        "subject_scope": subject_id,
        "numeric_evsi": NOT_CALCULABLE,
        "action_code": action_code or need_code,
    }


def _finding(
    item_id: str, dimension: str, current: Any, needed: Any, status: str,
    rule_id: str, facts: list[Mapping[str, Any]], reason: str,
    request: dict[str, Any] | None, support_fields: tuple[str, ...] = (),
    *, source_refs: list[Any] | None = None, window: Mapping[str, Any] | None = None,
    gap: float | None = None,
) -> FindingSupport:
    refs = source_refs if source_refs is not None else [
        ref for fact in facts for ref in fact["source_refs"]
    ]
    if window is None and facts:
        window = facts[0]["window"]
    finding = {
        "requirement_item_id": item_id,
        "dimension": dimension,
        "current_recorded": current,
        "needed": needed,
        "status": status,
        "origin": "UNKNOWN" if current is None and not facts else "REVIEWED_INFERENCE",
        "rule_id": rule_id,
        "source_refs": refs,
        "temporal_scope": window,
        "quantified_gap": gap,
        "reason_code": reason,
        "action_code": "NO_ADDITIONAL_REQUEST" if request is None else request["action_code"],
        "next_evidence": request,
    }
    support = tuple(
        (fact["fact_id"], field)
        for fact in facts for field in support_fields
    ) if status == "SUPPORTED" else ()
    return finding, support


def _absence(
    rows: list[Mapping[str, Any]], dataset_kind: str, subject_id: str,
) -> tuple[str, Any]:
    scoped = [row for row in rows if row["dataset_kind"] == dataset_kind]
    if not scoped:
        return "DATASET_UNAVAILABLE", {"dataset_kind": dataset_kind}
    complete = next(
        (row for row in scoped if row["completeness"] in {"COMPLETE", "SEARCHED_EMPTY"}),
        None,
    )
    if complete is None:
        return "COVERAGE_INCOMPLETE", {
            "dataset_kind": dataset_kind, "window": scoped[0]["window"],
            "scope": subject_id,
        }
    return "NOT_FOUND_IN", {
        "dataset_kind": dataset_kind, "window": complete["window"],
        "scope": subject_id,
    }


def _covered(
    fact: Mapping[str, Any], rows: list[Mapping[str, Any]],
    company_id: str | None = None,
) -> bool:
    """A dated record can support only the declared searched extract period."""
    return any(
        row["dataset_kind"] == fact["dataset_kind"]
        and (
            fact["subject_id"] in row["covered_subject_ids"]
            or (fact["subject_type"] == "PLANT" and company_id is not None
                and row["subject_type"] == "COMPANY"
                and company_id in row["covered_subject_ids"])
        )
        and row["window"]["start"] <= fact["window"]["start"]
        and fact["window"]["end"] <= row["window"]["end"]
        for row in rows
    )


def _attribution_request(subject_id: str) -> dict[str, Any]:
    return next_request(
        "line-level production or producer-grade matrix",
        "factory_attribution_link", "FACTORY_CUSTOMS_ATTRIBUTION", subject_id,
        action_code="FACTORY_ATTRIBUTION",
        route_effect=(
            "Can establish whether this transaction supports a named plant's "
            "incumbent assessment; it does not prove capability."
        ),
    )


def _equipment(
    subject_id: str, item: Mapping[str, Any],
    facts: Mapping[str, list[Mapping[str, Any]]],
) -> FindingSupport:
    customs = [
        fact for fact in facts.get("FACTORY_CUSTOMS", [])
        if _customs_usable(fact)
        and _hs_in(fact, list(item["admitted_hs6"]), str(item["hs_revision"]))
    ]
    cases = {
        ("H6", "847981", "HOT_DIP_ZINC_COATING", "STEEL_STRIP"):
            "P04_GALVANISING_ACQUISITION",
        ("H6", "847720", "EXTRUSION", "PLASTICS"):
            "P04_PLASTICS_WORKING_CONTEXT",
    }
    linked: list[tuple[Mapping[str, Any], Mapping[str, Any], str]] = []
    for tech in facts.get("EQUIPMENT_TECHNICAL", []):
        v = tech["values"]
        for raw in customs:
            c = raw["values"]
            same_transaction = (
                raw["fact_id"] == v["customs_fact_id"]
                and c["transaction_id"] and c["transaction_id"] == v["transaction_id"]
                and c["equipment_model_id"]
                and c["equipment_model_id"] == v["equipment_model_id"]
            )
            overlaps = (
                raw["window"]["start"] < tech["window"]["end"]
                and tech["window"]["start"] < raw["window"]["end"]
            )
            reason = cases.get((
                c["hs_revision"], c["hs6"], v["function"], v["workpiece_material"],
            ))
            if same_transaction and overlaps and reason is not None:
                linked.append((raw, tech, reason))
    reasons = {reason for _, _, reason in linked}
    if len(reasons) > 1:
        return _finding(
            str(item["item_id"]), "equipment_acquisition", None,
            {"hs_revision": item["hs_revision"], "admitted_hs6": item["admitted_hs6"]},
            "CONFLICTED", "P04", [], "P04_CONFLICTED_BASIS",
            next_request("line-level production or producer-grade matrix", "function",
                         "TECHNICAL_ENRICHMENT", subject_id),
        )
    if linked:
        raw, tech, reason = linked[0]
        current = {
            "hs_revision": raw["values"]["hs_revision"],
            "hs6": raw["values"]["hs6"],
            "function": tech["values"]["function"],
            "workpiece_material": tech["values"]["workpiece_material"],
        }
        return _finding(
            str(item["item_id"]), "equipment_acquisition", current,
            {"hs_revision": item["hs_revision"], "admitted_hs6": item["admitted_hs6"]},
            "SUPPORTED", "P04", [raw, tech], reason, None,
            ("hs6", "function", "workpiece_material"),
            window=raw["window"],
        )
    return _finding(
        str(item["item_id"]), "equipment_acquisition", None,
        {"hs_revision": item["hs_revision"], "admitted_hs6": item["admitted_hs6"]},
        "NOT_ESTABLISHED", "P04", [], "P04_BASIS_NOT_ESTABLISHED",
        next_request("line-level production or producer-grade matrix", "function",
                     "TECHNICAL_ENRICHMENT", subject_id),
    )


def _line_findings(
    subject_id: str,
    requirement_items: list[Mapping[str, Any]],
    facts: Mapping[str, list[Mapping[str, Any]]],
    assessment: Mapping[str, Any] | None,
    required_quantity_kt: float | None,
) -> list[FindingSupport]:
    rows: list[FindingSupport] = []
    comparisons = {
        row["field_id"]: row
        for row in assessment.get("comparisons", [])
    } if assessment is not None else {}
    for item in requirement_items:
        field = str(item["field_id"])
        result = comparisons.get(field)
        supporting = [
            fact for fact in facts.get("TECHNICAL_FIELD", [])
            if fact["values"]["field_id"] == field
            and fact["values"]["requirement_id"] == field
        ]
        status = "NOT_ESTABLISHED" if result is None else result["status"]
        current = None if result is None else result["current_recorded"]
        request = None if status in {"SUPPORTED", "NOT_REQUIRED"} else next_request(
            "line-level production or producer-grade matrix", field,
            "TECHNICAL_ENRICHMENT", subject_id,
        )
        rows.append(_finding(
            str(item["item_id"]), field, current, item.get("required_value"),
            status, "P06", supporting if result is not None else [],
            "P06_TECHNICAL_" + status, request, ("value",),
        ))
    capacity = None if assessment is None else assessment.get("capacity")
    status = "NOT_ESTABLISHED"
    current = None
    gap = None
    if capacity is not None:
        current = {
            "admitted_qualified_supply_kt": capacity["admitted_qualified_supply_kt"],
            "window_result": capacity["window_result"],
        }
        gap = capacity["shortage_kt"]
        if capacity["window_result"] == "MISMATCH":
            status = "LIMITATION_IDENTIFIED"
        elif capacity["admitted_qualified_supply_kt"] is not None:
            status = "SUPPORTED" if gap is not None and gap <= 0 else "LIMITATION_IDENTIFIED"
    supply_facts = [
        fact for kind in ("CAPACITY", "ALLOCATION", "WINDOW")
        for fact in facts.get(kind, [])
    ]
    rows.append(_finding(
        "qualified_volume", "qualified_volume", current, required_quantity_kt, status,
        "P09", supply_facts if assessment is not None else [],
        "P09_VOLUME_" + status,
        None if status == "SUPPORTED" else next_request(
            "line-level production or producer-grade matrix", "qualified_available_kt",
            "TECHNICAL_ENRICHMENT", subject_id,
        ), ("qualified_available_kt",), gap=gap,
    ))
    return rows


def evaluate_findings(
    *,
    subject_type: str,
    subject_id: str,
    target_family: str | None,
    items: list[Mapping[str, Any]],
    requirement_items: list[Mapping[str, Any]],
    facts_by_kind: Mapping[str, list[Mapping[str, Any]]],
    coverage_rows: list[Mapping[str, Any]],
    line_assessments: Mapping[str, Mapping[str, Any]],
    line_to_plant: Mapping[str, str],
    target_output_fact_ids: frozenset[str],
    company_context_facts: list[Mapping[str, Any]] | None = None,
    company_id: str | None = None,
    required_quantity_kt: float | None = None,
) -> list[FindingSupport]:
    """Evaluate only records selected for this subject by discovery."""
    if subject_type == "LINE":
        if subject_id not in line_to_plant:
            return []
        return _line_findings(
            subject_id, requirement_items, facts_by_kind,
            line_assessments.get(subject_id), required_quantity_kt,
        )
    rows: list[FindingSupport] = []
    registry = facts_by_kind.get("REGISTRY_ACTIVITY", [])
    production = facts_by_kind.get("PRODUCTION_ACTUAL", [])
    for item in items:
        rule = item.get("rule_id")
        item_id = str(item["item_id"])
        if subject_type == "COMPANY" and rule not in {"P03", "P08"}:
            continue
        if rule == "P01":
            operating = [
                fact for fact in registry
                if fact["values"]["country"] == "SA"
                and fact["values"]["status"] == "OPERATING"
                and fact["values"]["operating_status_asserted_by_registry"] is True
            ]
            operating.sort(key=lambda fact: fact["values"]["product_family"] != target_family)
            selected = operating[:1]
            rows.append(_finding(
                item_id, item_id, selected[0]["values"] if selected else registry[0]["values"] if registry else None,
                {"country": "SA", "status": "OPERATING"},
                "SUPPORTED" if selected else "NOT_ESTABLISHED", "P01",
                selected or registry[:1],
                ("P01_OPERATING_FAMILY" if selected[0]["values"]["product_family"] == target_family
                 else "P01_RECORDED_RELATED_FAMILY") if selected else "P01_NOT_OPERATING",
                None if selected else next_request(
                    "line-level production or producer-grade matrix",
                    "operating_status_asserted_by_registry", "REGISTRY", subject_id,
                ), ("operating_status_asserted_by_registry", "product_family"),
            ))
        elif rule == "P02":
            own = [
                fact for fact in production
                if fact["values"]["production_kind"] == "OWN_PRODUCTION"
                and fact["values"]["quantity_kt"] > 0
            ]
            own.sort(key=lambda fact: fact["fact_id"] not in target_output_fact_ids)
            target_recorded = bool(own and own[0]["fact_id"] in target_output_fact_ids)
            rows.append(_finding(
                item_id, item_id, own[0]["values"] if own else None,
                {"production_kind": "OWN_PRODUCTION"},
                "SUPPORTED" if own else "NOT_ESTABLISHED", "P02", own[:1],
                ("P02_HISTORICAL_OUTPUT" if target_recorded else "P02_RELATED_STAGE_OUTPUT")
                if own else "P02_OUTPUT_NOT_ESTABLISHED",
                None if own else next_request(
                    "line-level production or producer-grade matrix", "quantity_kt",
                    "PRODUCTION_ACTUALS", subject_id,
                ), ("production_kind", "hs6", "quantity_kt"),
            ))
        elif rule == "P03":
            customs = facts_by_kind.get("FACTORY_CUSTOMS", [])
            matches = [
                fact for fact in customs
                if _customs_usable(fact)
                and _hs_in(fact, list(item["admitted_hs6"]), str(item["hs_revision"]))
                and _covered(fact, coverage_rows, company_id)
            ]
            historic = [
                fact for fact in customs
                if _customs_usable(fact)
                and _hs_in(fact, list(item["admitted_hs6"]), str(item["hs_revision"]))
                and not _covered(fact, coverage_rows, company_id)
            ]
            unattributed = [
                fact for fact in (company_context_facts or [])
                if _customs_usable(fact)
                and _hs_in(fact, list(item["admitted_hs6"]), str(item["hs_revision"]))
                and _covered(fact, coverage_rows)
            ]
            reason, boundary = _absence(coverage_rows, "FACTORY_CUSTOMS", subject_id)
            company_context = subject_type == "COMPANY" and not matches and bool(customs)
            needs_attribution = (subject_type == "COMPANY" and bool(matches)) or (
                subject_type == "PLANT" and not matches and bool(unattributed)
            )
            current = matches[0]["values"] if matches else (
                historic[0]["values"] if historic else (
                    unattributed[0]["values"] if needs_attribution and unattributed else (
                        customs[0]["values"] if company_context else boundary
                    )
                )
            )
            selected = matches[:1] or historic[:1] or (
                unattributed[:1] if needs_attribution else customs[:1] if company_context else []
            )
            status = "SUPPORTED" if matches else "NOT_ESTABLISHED"
            request = None
            if needs_attribution:
                request = _attribution_request(subject_id)
            elif not matches and historic:
                request = next_request(
                    "line-level production or producer-grade matrix",
                    "in_scope_procurement_record", "FACTORY_CUSTOMS", subject_id,
                    action_code="IN_SCOPE_PROCUREMENT_RECORD",
                    route_effect=(
                        "Can establish whether a covered-period procurement record "
                        "supports this plant's incumbent assessment."
                    ),
                )
            elif not matches:
                request = next_request(
                    "line-level production or producer-grade matrix", "hs6",
                    "FACTORY_CUSTOMS", subject_id,
                )
            rows.append(_finding(
                item_id, item_id, current,
                {"hs_revision": item["hs_revision"], "admitted_hs6": item["admitted_hs6"]},
                status, "P03", selected,
                "P03_COMPANY_PROCUREMENT_CONTEXT" if subject_type == "COMPANY" and matches
                else "P03_PROCUREMENT_SIGNAL" if matches
                else "P03_OUTSIDE_SEARCHED_WINDOW" if historic
                else "P03_ATTRIBUTION_NOT_ESTABLISHED" if needs_attribution
                else "P03_COMPANY_TRADE_CONTEXT_NOT_INPUT" if company_context else reason,
                request, ("hs_revision", "hs6", "flow", "reexport"),
            ))
        elif rule == "P04":
            rows.append(_equipment(subject_id, item, facts_by_kind))
        elif rule == "P05":
            selected = next(
                (fact for fact in registry if fact["values"]["process_route"] == item["process_route"]),
                None,
            )
            rows.append(_finding(
                item_id, item_id,
                {"process_route": (selected or registry[0])["values"]["process_route"]} if registry else None,
                {"process_route": item["process_route"]},
                "SUPPORTED" if selected else "NOT_ESTABLISHED", "P05",
                [selected] if selected else registry[:1],
                "P05_RECORDED_ROUTE" if selected else "P05_STAGE_NOT_ESTABLISHED",
                None if selected else next_request(
                    "line-level production or producer-grade matrix", "process_route",
                    "REGISTRY", subject_id,
                ), ("process_route",),
            ))
        elif rule == "P07":
            selected = [
                fact for fact in facts_by_kind.get("CERTIFICATE", [])
                if item.get("scope") is not None and fact["values"]["scope"] == item["scope"]
            ]
            rows.append(_finding(
                item_id, item_id, selected[0]["values"] if selected else None,
                {"scope": item.get("scope")},
                "SUPPORTED" if selected else "NOT_ESTABLISHED", "P07",
                selected[:1],
                "P07_SCOPED_CERTIFICATE" if selected else "P07_CERTIFICATE_NOT_ESTABLISHED",
                None if selected else next_request(
                    "qualification/profile hard gates", "scope",
                    "TECHNICAL_ENRICHMENT", subject_id,
                ), ("scope",),
            ))
        elif rule == "P08":
            apps = facts_by_kind.get("APPLICATION", [])
            current = None if not apps else {
                "stage": apps[0]["values"]["stage"],
                "reason_code": apps[0]["values"]["reason_code"],
                "establishes_installation": False,
            }
            rows.append(_finding(
                item_id, item_id, current, {"establishes_installation": False},
                "SUPPORTED" if apps else "NOT_ESTABLISHED", "P08", apps[:1],
                "P08_INTENT" if apps else "P08_NO_APPLICATION",
                None if apps else next_request(
                    "line-level production or producer-grade matrix", "stage",
                    "APPLICATION_TAPE", subject_id,
                ), ("stage", "reason_code"),
            ))
    if subject_type == "PLANT" and not any(
        plant_id == subject_id and line_id in line_assessments
        for line_id, plant_id in line_to_plant.items()
    ):
        for item in requirement_items:
            field = str(item["field_id"])
            rows.append(_finding(
                str(item["item_id"]), field, None, item.get("required_value"),
                "NOT_ESTABLISHED", "P06", [],
                "P06_CURRENT_TECHNICAL_NOT_ESTABLISHED",
                next_request(
                    "line-level production or producer-grade matrix",
                    field, "TECHNICAL_ENRICHMENT", subject_id,
                ),
            ))
        rows.append(_finding(
            "qualified_volume", "qualified_volume", None, None,
            "NOT_ESTABLISHED", "P09", [], "P09_VOLUME_NOT_ESTABLISHED",
            next_request(
                "line-level production or producer-grade matrix",
                "qualified_available_kt", "TECHNICAL_ENRICHMENT", subject_id,
            ),
        ))
    return rows
