from __future__ import annotations

import math
from typing import Any

from . import signals
from .narratives import (
    NarrativeValue,
    render_catalogue_entry,
)


NOT_CALCULABLE = "NOT_CALCULABLE"
NEED_CODE_ORDER = (
    "identity/tariff-line",
    "target specification/application",
    "line-level production or producer-grade matrix",
    "capacity/availability/allocation",
    "qualification/profile hard gates",
    "re-export/origin decomposition",
    "route economics",
)
_ROUTE_EFFECTS = {
    "identity/tariff-line": (
        "Can resolve the decision object and change the admissible route."
    ),
    "target specification/application": (
        "Can establish target demand and change state or route."
    ),
    "line-level production or producer-grade matrix": (
        "Can establish domestic equivalence and change the incumbent route."
    ),
    "capacity/availability/allocation": (
        "Can distinguish no action, brownfield expansion, and new capacity."
    ),
    "qualification/profile hard gates": (
        "Can resolve a hard gate and change route permission."
    ),
    "re-export/origin decomposition": (
        "Can distinguish retained demand from a false or transitory gap."
    ),
    "route economics": (
        "Can determine whether the plausible route proceeds unsupported."
    ),
}


def _fired(
    preliminary_rules: list[dict[str, Any]],
    rule_id: str,
) -> bool:
    return any(
        row.get("rule_id") == rule_id
        and row.get("fired") is True
        for row in preliminary_rules
    )


def _supports(
    case: dict[str, Any],
    codes: set[str],
) -> list[str]:
    evidence = case.get("evidence")
    if not isinstance(evidence, list):
        return []
    return sorted(
        {
            str(item.get("evidence_id"))
            for item in evidence
            if isinstance(item, dict)
            and isinstance(item.get("supports"), list)
            and bool(set(item["supports"]) & codes)
        }
    )


def _unavailable(value: Any) -> bool:
    return value is None or value == "UNAVAILABLE"


def _weak_support(
    case: dict[str, Any],
    codes: set[str],
) -> bool:
    evidence = case.get("evidence")
    if not isinstance(evidence, list):
        return True
    covering = [
        item
        for item in evidence
        if isinstance(item, dict)
        and isinstance(item.get("supports"), list)
        and bool(set(item["supports"]) & codes)
    ]
    return not covering or all(
        item.get("evidence_class") in {"D", "E"}
        for item in covering
    )


def render_need(
    *,
    need_code: str,
    variant: str,
    template_key: str,
    blocked_field: str,
    evidence_ids: list[str],
    route_code: int | None = None,
) -> dict[str, Any]:
    return _render_need(
        need_code=need_code,
        variant=variant,
        template_key=template_key,
        blocked_field=blocked_field,
        evidence_ids=evidence_ids,
        route_code=route_code,
    )


EXCLUSION_NEED_FALLBACKS = (
    {
        "exclusion_code": "EX-01_HETEROGENEOUS_RESIDUAL",
        "block_name": "heterogeneous_residual_code",
        "need_code": "identity/tariff-line",
        "variant": "exclusion_ex01",
        "template_key": "need.identity.tariff_line",
        "blocked_field": "heterogeneous_residual_code",
    },
    {
        "exclusion_code": "EX-02_MARKET_BELOW_MES",
        "block_name": "downside_market_below_mes",
        "need_code": "target specification/application",
        "variant": "exclusion_ex02",
        "template_key": "need.demand.importer_specification",
        "blocked_field": "downside_market_below_mes",
    },
    {
        "exclusion_code": "EX-03_UNSATISFIABLE_HARD_GATE",
        "block_name": "unsatisfiable_hard_gate",
        "need_code": "qualification/profile hard gates",
        "variant": "exclusion_ex03",
        "template_key": "need.demand.importer_application_qualification",
        "blocked_field": "hard_regulatory_or_process_gate",
    },
    {
        "exclusion_code": "EX-04_IDLE_EQUIVALENT_CAPACITY",
        "block_name": "idle_equivalent_domestic_capacity",
        "need_code": "capacity/availability/allocation",
        "variant": "exclusion_ex04",
        "template_key": "need.capacity.availability_allocation",
        "blocked_field": "idle_equivalent_domestic_capacity",
    },
    {
        "exclusion_code": "EX-05_TRANSITORY_OR_MEASUREMENT",
        "block_name": "transitory_or_measurement_gap",
        "need_code": "re-export/origin decomposition",
        "variant": "exclusion_ex05",
        "template_key": "need.flows.reexport_origin_decomposition",
        "blocked_field": "transitory_or_measurement_gap",
    },
    {
        "exclusion_code": "EX-06_REDUNDANCY_OR_CROWD_OUT",
        "block_name": "redundancy_or_crowd_out",
        "need_code": "route economics",
        "variant": "exclusion_ex06",
        "template_key": "need.economics.named_exception_delivered_cost",
        "blocked_field": "route_economics",
    },
)


def _render_need(
    *,
    need_code: str,
    variant: str,
    template_key: str,
    blocked_field: str,
    evidence_ids: list[str],
    route_code: int | None = None,
) -> dict[str, Any]:
    rendered: dict[str, dict[str, Any]] = {}
    for locale in ("en", "ar"):
        values = None
        if route_code is not None:
            route_label = render_catalogue_entry(
                f"route.{route_code}.short",
                locale,
            )["text"]
            values = {
                "route_label": NarrativeValue.localized(route_label)
            }
        rendered[locale] = render_catalogue_entry(
            template_key,
            locale,
            values,
        )
    return {
        "need_code": need_code,
        "variant": variant,
        "template_key": template_key,
        "blocked_field": blocked_field,
        "route_effect": _ROUTE_EFFECTS[need_code],
        "evidence_ids": evidence_ids,
        "numeric_evsi": NOT_CALCULABLE,
        "text": rendered["en"]["text"],
        "localized_text": {
            locale: value["text"]
            for locale, value in rendered.items()
        },
        "localized_narrative": rendered,
    }


def _common_state(case: dict[str, Any]) -> dict[str, Any]:
    opportunity = case.get("opportunity")
    status = (
        opportunity.get("decision_object_status")
        if isinstance(opportunity, dict)
        else None
    )
    decision_inputs = case.get("decision_inputs")
    inputs = decision_inputs if isinstance(decision_inputs, dict) else {}
    capability = case.get("domestic_capability")
    capability_values = capability if isinstance(capability, dict) else {}
    dimensions = capability_values.get("public_dimension_states")
    dimension_values = dimensions if isinstance(dimensions, dict) else {}
    flows = case.get("domestic_flows")
    flow_values = flows if isinstance(flows, dict) else {}
    portfolio = bool(
        _supports(case, {"DOMESTIC_PRODUCT_PORTFOLIO"})
    )
    return {
        "status": status,
        "target": inputs.get("target_specification_demand"),
        "equivalence": inputs.get("specification_equivalence"),
        "routes": inputs.get("route_evidence"),
        "capacity_unknown": (
            dimension_values.get("capacity_time_window") == "U"
        ),
        "flow_unknown": any(
            _unavailable(flow_values.get(key))
            for key in (
                "retained_imports_kt",
                "domestic_origin_exports_kt",
                "reexports_kt",
            )
        ),
        "portfolio": portfolio,
        "profile_gates": capability_values.get("profile_hard_gates"),
        "decision_gates": capability_values.get(
            "unresolved_hard_gates"
        ),
        "weak_identity": _weak_support(
            case,
            {
                "TARGET_PRODUCT_IDENTITY",
                "BILINGUAL_SPECIFICATION_EXTRACTION",
                "DOMESTIC_PRODUCT_PORTFOLIO",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_DIMENSION_ENVELOPE",
            },
        ),
        "weak_demand": _weak_support(
            case,
            {"TARGET_SPECIFICATION_DEMAND"},
        ),
        "weak_capability": _weak_support(
            case,
            {
                "DOMESTIC_NAMEPLATE_CAPACITY",
                "DOMESTIC_PROCESS_ROUTE",
                "DOMESTIC_PROCESS_FAMILY",
                "DOMESTIC_PRODUCT_PORTFOLIO",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_LABORATORY_METROLOGY",
                "DOMESTIC_CAPABILITY_ASSESSMENT",
            },
        ),
        "weak_gate": _weak_support(
            case,
            {
                "DOMESTIC_PROCESS_ROUTE",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_LABORATORY_METROLOGY",
                "HARD_REGULATORY_PROCESS_GATES",
            },
        ),
    }


def _route_determination_unresolved(
    case: dict[str, Any],
) -> bool:
    decision_inputs = case.get("decision_inputs")
    routes = (
        decision_inputs.get("route_evidence")
        if isinstance(decision_inputs, dict)
        else None
    )
    if routes == "UNAVAILABLE" or routes is None:
        return True
    if not isinstance(routes, list) or not routes:
        return True
    for record in routes:
        if not isinstance(record, dict):
            continue
        if record.get("technical_feasibility_confirmed") is not True:
            continue
        cash_flows = record.get("downside_cash_flows_m_sar")
        hurdle = record.get("hurdle_rate")
        if (
            isinstance(cash_flows, list)
            and cash_flows
            and isinstance(hurdle, (int, float))
            and math.isfinite(float(hurdle))
            and all(
                isinstance(value, (int, float))
                and math.isfinite(float(value))
                for value in cash_flows
            )
        ):
            return False
    return True


def derive_evidence_needs(
    case: dict[str, Any],
    preliminary_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    state = _common_state(case)
    status = state["status"]
    demand_missing = _unavailable(state["target"])
    equivalence_missing = _unavailable(state["equivalence"])
    route_inputs_missing = _unavailable(state["routes"])
    needs: list[dict[str, Any]] = []

    if status == "resolved" and state["weak_identity"]:
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[0],
                variant="identity_evidence_class_blocked",
                template_key="need.identity.tariff_line",
                blocked_field="product_identity",
                evidence_ids=_supports(
                    case,
                    {"TARGET_PRODUCT_IDENTITY"},
                ),
            )
        )
    if (
        status == "resolved"
        and not demand_missing
        and state["weak_demand"]
    ):
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[1],
                variant="demand_evidence_class_blocked",
                template_key="need.demand.importer_specification",
                blocked_field="demand_at_required_specification",
                evidence_ids=_supports(
                    case,
                    {"TARGET_SPECIFICATION_DEMAND"},
                ),
            )
        )
    if (
        status == "resolved"
        and not state["capacity_unknown"]
        and state["weak_capability"]
    ):
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[3],
                variant="capability_evidence_class_blocked",
                template_key="need.capacity.availability_allocation",
                blocked_field="domestic_supply_or_capability",
                evidence_ids=_supports(
                    case,
                    {"DOMESTIC_CAPABILITY_ASSESSMENT"},
                ),
            )
        )
    if status == "resolved" and state["weak_gate"]:
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[4],
                variant="hard_gate_evidence_class_blocked",
                template_key=(
                    "need.demand.importer_application_qualification"
                ),
                blocked_field="hard_regulatory_or_process_gate",
                evidence_ids=_supports(
                    case,
                    {"HARD_REGULATORY_PROCESS_GATES"},
                ),
            )
        )

    if status == "generic_hs6_only":
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[0],
                variant="generic_hs6_only",
                template_key="need.identity.tariff_line",
                blocked_field="product_identity",
                evidence_ids=_supports(
                    case,
                    {"TARGET_PRODUCT_IDENTITY"},
                ),
            )
        )
        if demand_missing:
            needs.append(
                _render_need(
                    need_code=NEED_CODE_ORDER[1],
                    variant="application_qualification_unresolved",
                    template_key=(
                        "need.demand."
                        "importer_application_qualification"
                    ),
                    blocked_field=(
                        "demand_at_required_specification"
                    ),
                    evidence_ids=[],
                )
            )
        if state["portfolio"] and equivalence_missing:
            needs.append(
                _render_need(
                    need_code=NEED_CODE_ORDER[2],
                    variant="portfolio_without_grade_equivalence",
                    template_key=(
                        "need.specification.producer_grade_matrix"
                    ),
                    blocked_field=(
                        "domestic_supply_or_capability"
                    ),
                    evidence_ids=_supports(
                        case,
                        {"DOMESTIC_PRODUCT_PORTFOLIO"},
                    ),
                )
            )
    elif status == "partially_resolved":
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[2],
                variant="line_production_unresolved",
                template_key=(
                    "need.specification.line_production"
                ),
                blocked_field="product_identity",
                evidence_ids=_supports(
                    case,
                    {
                        "DOMESTIC_SPECIFICATION_ENVELOPE",
                        "DOMESTIC_DIMENSION_ENVELOPE",
                    },
                ),
            )
        )

    if state["capacity_unknown"]:
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[3],
                variant="availability_allocation_unresolved",
                template_key=(
                    "need.capacity.availability_allocation"
                ),
                blocked_field="domestic_supply_or_capability",
                evidence_ids=_supports(
                    case,
                    {
                        "DOMESTIC_NAMEPLATE_CAPACITY",
                        "DOMESTIC_CAPABILITY_ASSESSMENT",
                    },
                ),
            )
        )

    if demand_missing and status == "partially_resolved":
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[1],
                variant="buyer_specification_unresolved",
                template_key=(
                    "need.demand.importer_specification"
                ),
                blocked_field="demand_at_required_specification",
                evidence_ids=[],
            )
        )

    if (
        not state["capacity_unknown"]
        and (
            isinstance(state["decision_gates"], list)
            and bool(state["decision_gates"])
        )
    ):
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[4],
                variant="hard_gates_unresolved",
                template_key=(
                    "need.demand.importer_application_qualification"
                ),
                blocked_field="hard_regulatory_or_process_gate",
                evidence_ids=[],
            )
        )

    if state["flow_unknown"] and status == "partially_resolved":
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[5],
                variant="retained_flow_unresolved",
                template_key=(
                    "need.flows.reexport_origin_decomposition"
                ),
                blocked_field="demand_at_required_specification",
                evidence_ids=_supports(
                    case,
                    {"TRADE_VALUE", "TRADE_QUANTITY"},
                ),
            )
        )

    if _fired(preliminary_rules, "R11") and route_inputs_missing:
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[6],
                variant="named_exception_economics_unresolved",
                template_key=(
                    "need.economics.named_exception_delivered_cost"
                ),
                blocked_field="route_economics",
                evidence_ids=_supports(
                    case,
                    {"EXPORT_IMPORT_RATIO"},
                ),
            )
        )
    elif _fired(preliminary_rules, "R9-S") and route_inputs_missing:
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[6],
                variant="plausible_route_economics_unresolved",
                template_key="need.economics.route_delivered_cost",
                blocked_field="route_economics",
                evidence_ids=[],
                route_code=5,
            )
        )

    if (
        signals.material_trigger_rule_ids(preliminary_rules)
        and _route_determination_unresolved(case)
    ):
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[6],
                variant="route_determination_unresolved",
                template_key="need.route.evidence_required",
                blocked_field="route_economics",
                evidence_ids=_supports(
                    case,
                    {
                        "ROUTE_ECONOMICS",
                        "ROUTE_NATIONAL_VALUE",
                        "ROUTE_COMPETITION",
                    },
                ),
            )
        )
    elif (
        not signals.advance_supporting_signal_rule_ids(
            preliminary_rules
        )
        and signals.degraded_material_signal_rule_ids(
            preliminary_rules
        )
    ):
        needs.append(
            _render_need(
                need_code=NEED_CODE_ORDER[5],
                variant="full_execution_signal_unresolved",
                template_key=(
                    "need.flows.reexport_origin_decomposition"
                ),
                blocked_field="demand_at_required_specification",
                evidence_ids=_supports(
                    case,
                    {"TRADE_VALUE", "TRADE_QUANTITY"},
                ),
            )
        )

    exclusion_inputs = case.get("hard_exclusion_inputs")
    exclusion_blocks = (
        exclusion_inputs
        if isinstance(exclusion_inputs, dict)
        else {}
    )

    def block_unknown(name: str) -> bool:
        block = exclusion_blocks.get(name)
        return (
            not isinstance(block, dict)
            or any(
                value == "UNAVAILABLE"
                for key, value in block.items()
                if key != "evidence_ids"
            )
        )

    def add_fallback(
        *,
        need_code: str,
        variant: str,
        template_key: str,
        blocked_field: str,
        block_name: str,
    ) -> None:
        if any(
            need["need_code"] == need_code for need in needs
        ):
            return
        block = exclusion_blocks.get(block_name)
        evidence_ids = (
            [
                value
                for value in block.get("evidence_ids", [])
                if isinstance(value, str)
            ]
            if isinstance(block, dict)
            else []
        )
        needs.append(
            _render_need(
                need_code=need_code,
                variant=variant,
                template_key=template_key,
                blocked_field=blocked_field,
                evidence_ids=evidence_ids,
            )
        )

    if block_unknown("heterogeneous_residual_code"):
        if status == "partially_resolved":
            add_fallback(
                need_code=NEED_CODE_ORDER[2],
                variant="residual_product_separation_unresolved",
                template_key="need.specification.line_production",
                blocked_field="product_identity",
                block_name="heterogeneous_residual_code",
            )
        else:
            add_fallback(
                need_code=NEED_CODE_ORDER[0],
                variant="residual_identity_unresolved",
                template_key="need.identity.tariff_line",
                blocked_field="product_identity",
                block_name="heterogeneous_residual_code",
            )
    if block_unknown("downside_market_below_mes"):
        add_fallback(
            need_code=NEED_CODE_ORDER[1],
            variant="downside_market_scale_unresolved",
            template_key="need.demand.importer_specification",
            blocked_field="demand_at_required_specification",
            block_name="downside_market_below_mes",
        )
    if block_unknown("unsatisfiable_hard_gate"):
        add_fallback(
            need_code=NEED_CODE_ORDER[2],
            variant="hard_gate_satisfiability_unresolved",
            template_key=(
                "need.demand.importer_application_qualification"
            ),
            blocked_field="hard_regulatory_or_process_gate",
            block_name="unsatisfiable_hard_gate",
        )
    if block_unknown("idle_equivalent_domestic_capacity"):
        add_fallback(
            need_code=NEED_CODE_ORDER[3],
            variant="idle_equivalent_capacity_unresolved",
            template_key="need.capacity.availability_allocation",
            blocked_field="domestic_supply_or_capability",
            block_name="idle_equivalent_domestic_capacity",
        )
    if block_unknown("transitory_or_measurement_gap"):
        if status == "generic_hs6_only":
            add_fallback(
                need_code=NEED_CODE_ORDER[1],
                variant="transitory_demand_unresolved",
                template_key=(
                    "need.demand."
                    "importer_application_qualification"
                ),
                blocked_field="demand_at_required_specification",
                block_name="transitory_or_measurement_gap",
            )
        else:
            add_fallback(
                need_code=NEED_CODE_ORDER[5],
                variant="transitory_flow_unresolved",
                template_key=(
                    "need.flows.reexport_origin_decomposition"
                ),
                blocked_field="demand_at_required_specification",
                block_name="transitory_or_measurement_gap",
            )
    if block_unknown("redundancy_or_crowd_out"):
        add_fallback(
            need_code=NEED_CODE_ORDER[6],
            variant="competition_economics_unresolved",
            template_key=(
                "need.economics.named_exception_delivered_cost"
            ),
            blocked_field="route_economics",
            block_name="redundancy_or_crowd_out",
        )

    deduplicated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for need in needs:
        if need["need_code"] in seen:
            continue
        seen.add(need["need_code"])
        deduplicated.append(need)
    return deduplicated
