from __future__ import annotations

import unicodedata
from math import isfinite
from typing import Any

from .capability import effective_qualified_capacity
from .config import evidence_policy_config
from .economics import NATIONAL_VALUE_KEYS
from .evidence import EvidenceIntegrityError, synthetic_display_labels
from .public_snapshot import capability_hard_gate_names

SUPPORTED_SCENARIO_CONTRACT_VERSIONS = frozenset({"2.0.0"})
VALID_DECISION_STATES = frozenset({"REJECT", "MONITOR", "INVESTIGATE", "ADVANCE"})
GOVERNED_SYNTHETIC_INPUT_KEYS = frozenset(
    {
        "target_specification",
        "demand",
        "plant_line",
        "capability_states",
        "hard_gates",
        "upgrade",
        "economics",
        "equivalence",
        "evsi",
        "class_if_confirmed",
        "decision_specific_hard_gates",
        "route_evidence",
        "monitor_trigger",
        "hard_exclusion_inputs",
        "tariff_line_allocation",
        "buyer_allocation",
        "expansion_assumption",
        "production_and_retained_flows",
        "counterfactual",
        "competition_inputs",
    }
)
_BROWNFIELD_ROUTE_CODE = 5
_ROUTE5_INHERITED_FIELDS = frozenset(
    {
        "downside_cash_flows_m_sar",
        "hurdle_rate",
        "national_value",
        "competition",
    }
)


def _required_mapping(
    parent: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(f"{context}.{key} must be a mapping")
    return value


def _required_number(value: Any, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(float(value))
    ):
        raise EvidenceIntegrityError(f"{field} must be a finite number")
    return float(value)


def _validate_bilingual_text(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(f"{field} must be a bilingual mapping")
    result: dict[str, str] = {}
    for locale in ("en", "ar"):
        text = value.get(locale)
        if not isinstance(text, str) or not text.strip():
            raise EvidenceIntegrityError(
                f"{field}.{locale} must be a non-empty string"
            )
        normalized = unicodedata.normalize("NFC", text.strip())
        if "{" in normalized or "}" in normalized:
            raise EvidenceIntegrityError(
                f"{field}.{locale} must not contain placeholder characters"
            )
        policy = evidence_policy_config().get("synthetic_isolation", {})
        labels = {
            policy.get("display_label"),
            policy.get("display_label_ar"),
        }
        if normalized in labels:
            raise EvidenceIntegrityError(
                f"{field}.{locale} must not equal a policy label"
            )
        result[locale] = normalized
    return result


def _validate_bilingual_list(value: Any, field: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise EvidenceIntegrityError(f"{field} must be a list")
    return [_validate_bilingual_text(item, f"{field}[]") for item in value]


def validate_simulation_contract(scenario: dict[str, Any]) -> None:
    version = scenario.get("scenario_version")
    if version not in SUPPORTED_SCENARIO_CONTRACT_VERSIONS:
        raise EvidenceIntegrityError(
            "Synthetic scenario scenario_version is unsupported: "
            f"{version}"
        )
    ground_truth = _required_mapping(scenario, "ground_truth", "scenario")
    expected_state = ground_truth.get("expected_simulation_state")
    if expected_state not in VALID_DECISION_STATES:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_simulation_state "
            "must be a decision state"
        )
    route_code = ground_truth.get("expected_route_code")
    if route_code is not None and (
        isinstance(route_code, bool) or not isinstance(route_code, int)
    ):
        raise EvidenceIntegrityError(
            "scenario.ground_truth.expected_route_code "
            "must be an integer or null"
        )
    basis = ground_truth.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "scenario.ground_truth.basis must be a non-empty string"
        )
    inputs = _required_mapping(scenario, "synthetic_inputs", "scenario")
    unknown = set(inputs) - GOVERNED_SYNTHETIC_INPUT_KEYS
    if unknown:
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs contains unknown keys: "
            + ", ".join(sorted(unknown))
        )
    narratives = _required_mapping(
        scenario,
        "decision_narrative",
        "scenario",
    )
    for state, narrative in narratives.items():
        if state not in VALID_DECISION_STATES:
            raise EvidenceIntegrityError(
                f"scenario.decision_narrative.{state} is not a valid state"
            )
        _validate_bilingual_text(
            _required_mapping(
                narrative,
                "headline",
                f"scenario.decision_narrative.{state}",
            ),
            f"scenario.decision_narrative.{state}.headline",
        )
        _validate_bilingual_text(
            _required_mapping(
                narrative,
                "route_label",
                f"scenario.decision_narrative.{state}",
            ),
            f"scenario.decision_narrative.{state}.route_label",
        )
        _validate_bilingual_text(
            _required_mapping(
                narrative,
                "rationale",
                f"scenario.decision_narrative.{state}",
            ),
            f"scenario.decision_narrative.{state}.rationale",
        )
        _validate_bilingual_list(
            narrative.get("conditions", []),
            f"scenario.decision_narrative.{state}.conditions",
        )
        _validate_bilingual_list(
            narrative.get("kill_conditions", []),
            f"scenario.decision_narrative.{state}.kill_conditions",
        )
        if "competition_finding" in narrative:
            _validate_bilingual_text(
                narrative["competition_finding"],
                f"scenario.decision_narrative.{state}.competition_finding",
            )
    route_codes: set[int] = set()
    route_evidence = inputs.get("route_evidence")
    if route_evidence is not None:
        if not isinstance(route_evidence, list):
            raise EvidenceIntegrityError(
                "scenario.synthetic_inputs.route_evidence must be a list"
            )
        for index, record in enumerate(route_evidence):
            if not isinstance(record, dict):
                raise EvidenceIntegrityError(
                    f"route_evidence[{index}] must be a mapping"
                )
            code = record.get("route_code")
            if code == 8:
                raise EvidenceIntegrityError(
                    "route_evidence route_code 8 is forbidden in S10"
                )
            if (
                isinstance(code, bool)
                or not isinstance(code, int)
                or code < 1
                or code > 7
            ):
                raise EvidenceIntegrityError(
                    f"route_evidence[{index}].route_code must be 1-7"
                )
            if code in route_codes:
                raise EvidenceIntegrityError(
                    f"route_evidence duplicate route_code {code}"
                )
            route_codes.add(code)
            if code == _BROWNFIELD_ROUTE_CODE:
                for field in _ROUTE5_INHERITED_FIELDS:
                    if field in record:
                        raise EvidenceIntegrityError(
                            f"route-5 record must not declare {field}"
                        )
    if expected_state == "MONITOR" and not isinstance(
        inputs.get("monitor_trigger"),
        dict,
    ):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.monitor_trigger is required "
            "when ground_truth expects MONITOR"
        )
    _validate_optional_blocks(inputs)


def _validate_optional_blocks(inputs: dict[str, Any]) -> None:
    _validate_class_if_confirmed(inputs.get("class_if_confirmed"))
    _validate_decision_specific_hard_gates(
        inputs.get("decision_specific_hard_gates")
    )
    _validate_demand_extensions(inputs.get("demand"))
    _validate_economics_extensions(inputs.get("economics"))
    _validate_equivalence_block(inputs.get("equivalence"))
    _validate_tariff_line_allocation(inputs.get("tariff_line_allocation"))
    _validate_buyer_allocation(inputs.get("buyer_allocation"))
    _validate_expansion_assumption(inputs.get("expansion_assumption"))
    _validate_production_and_retained_flows(
        inputs.get("production_and_retained_flows")
    )
    _validate_counterfactual(inputs.get("counterfactual"))
    _validate_competition_inputs(inputs.get("competition_inputs"))
    _validate_monitor_trigger(inputs.get("monitor_trigger"))
    _validate_hard_exclusion_inputs(inputs.get("hard_exclusion_inputs"))


def _validate_class_if_confirmed(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.class_if_confirmed must be a mapping"
        )
    allowed = {
        "product_identity",
        "demand_at_required_specification",
        "domestic_supply_or_capability",
        "hard_regulatory_or_process_gate",
        "basis",
    }
    unknown = set(value) - allowed
    if unknown:
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.class_if_confirmed contains "
            f"unknown keys: {', '.join(sorted(unknown))}"
        )
    for field, declared in value.items():
        if field == "basis":
            if not isinstance(declared, str) or not declared:
                raise EvidenceIntegrityError(
                    "class_if_confirmed.basis must be a non-empty string"
                )
            continue
        if declared not in {"A", "B", "C", "D", "E"}:
            raise EvidenceIntegrityError(
                f"class_if_confirmed.{field} must be A, B, C, D or E"
            )


def _validate_decision_specific_hard_gates(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.decision_specific_hard_gates "
            "must be a mapping"
        )
    for name, status in value.items():
        if not isinstance(name, str) or not name:
            raise EvidenceIntegrityError(
                "decision_specific_hard_gates keys must be non-empty strings"
            )
        if not isinstance(status, str) or not status:
            raise EvidenceIntegrityError(
                f"decision_specific_hard_gates.{name} must be a non-empty string"
            )


def _validate_demand_extensions(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.demand must be a mapping"
        )
    base = value.get("base_demand_kt")
    if base is not None:
        number = _required_number(base, "demand.base_demand_kt")
        if number <= 0:
            raise EvidenceIntegrityError(
                "demand.base_demand_kt must be greater than zero"
            )
    probability = value.get("commitment_probability")
    if probability is not None:
        number = _required_number(
            probability,
            "demand.commitment_probability",
        )
        if number < 0 or number > 1:
            raise EvidenceIntegrityError(
                "demand.commitment_probability must be between 0 and 1"
            )


def _validate_economics_extensions(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.economics must be a mapping"
        )
    mes = value.get("minimum_efficient_scale_kt")
    if mes is not None:
        number = _required_number(
            mes,
            "economics.minimum_efficient_scale_kt",
        )
        if number <= 0:
            raise EvidenceIntegrityError(
                "economics.minimum_efficient_scale_kt must be greater than zero"
            )


def _validate_equivalence_block(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.equivalence must be a mapping"
        )
    equivalent = value.get("domestic_grade_equivalent")
    if not isinstance(equivalent, bool):
        raise EvidenceIntegrityError(
            "equivalence.domestic_grade_equivalent must be boolean"
        )
    qualified = value.get("qualified_available_kt")
    if qualified is not None:
        number = _required_number(
            qualified,
            "equivalence.qualified_available_kt",
        )
        if number < 0:
            raise EvidenceIntegrityError(
                "equivalence.qualified_available_kt must be non-negative"
            )


def _validate_tariff_line_allocation(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.tariff_line_allocation must be a mapping"
        )
    basis = value.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "tariff_line_allocation.basis must be a non-empty string"
        )
    lines = value.get("lines")
    if not isinstance(lines, list) or not lines:
        raise EvidenceIntegrityError(
            "tariff_line_allocation.lines must be a non-empty list"
        )
    for index, line in enumerate(lines):
        if not isinstance(line, dict):
            raise EvidenceIntegrityError(
                f"tariff_line_allocation.lines[{index}] must be a mapping"
            )
        tariff_line = line.get("national_tariff_line")
        if not isinstance(tariff_line, str) or not tariff_line:
            raise EvidenceIntegrityError(
                f"tariff_line_allocation.lines[{index}].national_tariff_line "
                "must be a non-empty string"
            )
        description = line.get("description_en")
        if not isinstance(description, str) or not description:
            raise EvidenceIntegrityError(
                f"tariff_line_allocation.lines[{index}].description_en "
                "must be a non-empty string"
            )
        qty = _required_number(
            line.get("quantity_kt"),
            f"tariff_line_allocation.lines[{index}].quantity_kt",
        )
        if qty < 0:
            raise EvidenceIntegrityError(
                f"tariff_line_allocation.lines[{index}].quantity_kt "
                "must be non-negative"
            )
        if "value_usd_m" in line:
            val = _required_number(
                line.get("value_usd_m"),
                f"tariff_line_allocation.lines[{index}].value_usd_m",
            )
            if val < 0:
                raise EvidenceIntegrityError(
                    f"tariff_line_allocation.lines[{index}].value_usd_m "
                    "must be non-negative"
                )


def _validate_buyer_allocation(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.buyer_allocation must be a mapping"
        )
    basis = value.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "buyer_allocation.basis must be a non-empty string"
        )
    buyers = value.get("buyers")
    if not isinstance(buyers, list) or not buyers:
        raise EvidenceIntegrityError(
            "buyer_allocation.buyers must be a non-empty list"
        )
    for index, buyer in enumerate(buyers):
        if not isinstance(buyer, dict):
            raise EvidenceIntegrityError(
                f"buyer_allocation.buyers[{index}] must be a mapping"
            )
        buyer_id = buyer.get("buyer_id")
        if not isinstance(buyer_id, str) or not buyer_id:
            raise EvidenceIntegrityError(
                f"buyer_allocation.buyers[{index}].buyer_id "
                "must be a non-empty string"
            )
        segment = buyer.get("segment")
        if not isinstance(segment, str) or not segment:
            raise EvidenceIntegrityError(
                f"buyer_allocation.buyers[{index}].segment "
                "must be a non-empty string"
            )
        qty = _required_number(
            buyer.get("quantity_kt"),
            f"buyer_allocation.buyers[{index}].quantity_kt",
        )
        if qty < 0:
            raise EvidenceIntegrityError(
                f"buyer_allocation.buyers[{index}].quantity_kt "
                "must be non-negative"
            )


def _validate_expansion_assumption(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.expansion_assumption must be a mapping"
        )
    planned = _required_number(
        value.get("planned_nameplate_kt"),
        "expansion_assumption.planned_nameplate_kt",
    )
    if planned <= 0:
        raise EvidenceIntegrityError(
            "expansion_assumption.planned_nameplate_kt must be greater than zero"
        )
    year = value.get("commissioning_year")
    if isinstance(year, bool) or not isinstance(year, int):
        raise EvidenceIntegrityError(
            "expansion_assumption.commissioning_year must be an integer"
        )
    basis = value.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "expansion_assumption.basis must be a non-empty string"
        )
    if value.get("disclosed") is not True:
        raise EvidenceIntegrityError(
            "expansion_assumption.disclosed must be true"
        )


def _validate_production_and_retained_flows(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.production_and_retained_flows "
            "must be a mapping"
        )
    year = value.get("period_year")
    if isinstance(year, bool) or not isinstance(year, int):
        raise EvidenceIntegrityError(
            "production_and_retained_flows.period_year must be an integer"
        )
    basis = value.get("basis")
    if not isinstance(basis, str) or not basis:
        raise EvidenceIntegrityError(
            "production_and_retained_flows.basis must be a non-empty string"
        )
    for field in (
        "domestic_production_kt",
        "retained_imports_kt",
        "domestic_origin_exports_kt",
        "reexports_kt",
    ):
        raw = value.get(field)
        if raw == "UNAVAILABLE":
            continue
        number = _required_number(
            raw,
            f"production_and_retained_flows.{field}",
        )
        if number < 0:
            raise EvidenceIntegrityError(
                f"production_and_retained_flows.{field} must be non-negative"
            )


def _validate_counterfactual(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.counterfactual must be a mapping"
        )
    allowed = {
        "q1_incumbent_meets_specification_without_capital",
        "q4_downside_demand_supports_incumbent_and_new_entrant",
        "q5_new_entry_displaces_efficient_domestic_production",
        "q6_technology_jv_superior_to_expansion_or_greenfield",
    }
    unknown = set(value) - allowed
    if unknown:
        raise EvidenceIntegrityError(
            "counterfactual contains unknown keys: "
            + ", ".join(sorted(unknown))
        )
    for key, answer in value.items():
        if answer not in {True, False, "UNAVAILABLE"}:
            raise EvidenceIntegrityError(
                f"counterfactual.{key} must be true, false or UNAVAILABLE"
            )


def _validate_competition_inputs(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.competition_inputs must be a mapping"
        )
    market = value.get("market_concentration")
    if market == "UNAVAILABLE" or market is None:
        return
    if not isinstance(market, dict):
        raise EvidenceIntegrityError(
            "competition_inputs.market_concentration must be a mapping or "
            "UNAVAILABLE"
        )
    for field in ("hhi_before", "hhi_after"):
        number = _required_number(
            market.get(field),
            f"competition_inputs.market_concentration.{field}",
        )
        if number < 0 or number > 1:
            raise EvidenceIntegrityError(
                f"competition_inputs.market_concentration.{field} "
                "must be between 0 and 1"
            )


def _validate_monitor_trigger(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.monitor_trigger must be a mapping"
        )
    domain = value.get("domain")
    allowed_domains = {
        "demand",
        "regulation",
        "technology",
        "supplier_concentration",
        "capacity_state",
    }
    if domain not in allowed_domains:
        raise EvidenceIntegrityError(
            "monitor_trigger.domain must be one of the allowed domains"
        )
    condition = value.get("condition_code")
    if not isinstance(condition, str) or not condition:
        raise EvidenceIntegrityError(
            "monitor_trigger.condition_code must be a non-empty string"
        )


def _validate_hard_exclusion_inputs(value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise EvidenceIntegrityError(
            "scenario.synthetic_inputs.hard_exclusion_inputs must be a mapping"
        )
    allowed_blocks = {
        "heterogeneous_residual_code",
        "downside_market_below_mes",
        "unsatisfiable_hard_gate",
        "idle_equivalent_domestic_capacity",
        "transitory_or_measurement_gap",
        "redundancy_or_crowd_out",
    }
    unknown = set(value) - allowed_blocks
    if unknown:
        raise EvidenceIntegrityError(
            "hard_exclusion_inputs contains unknown blocks: "
            + ", ".join(sorted(unknown))
        )


def validate_scenario_pairing(
    scenario: dict[str, Any],
    public_case: dict[str, Any],
) -> None:
    opportunity = public_case.get("opportunity")
    public_id = opportunity.get("id") if isinstance(opportunity, dict) else None
    if scenario.get("opportunity_id") != public_id:
        raise EvidenceIntegrityError(
            "Synthetic scenario opportunity_id does not match the public case"
        )
    capability = public_case.get("domestic_capability")
    raw_unresolved = (
        capability.get("unresolved_hard_gates", [])
        if isinstance(capability, dict)
        else []
    )
    unresolved_names = {
        row["name"]
        for row in raw_unresolved
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    declared = scenario.get("synthetic_inputs", {}).get(
        "decision_specific_hard_gates"
    )
    if isinstance(declared, dict):
        unknown = set(declared) - unresolved_names
        if unknown:
            raise EvidenceIntegrityError(
                "decision_specific_hard_gates names unknown to public case: "
                + ", ".join(sorted(unknown))
            )


def decision_narrative_for_state(
    scenario: dict[str, Any],
    state: str,
) -> dict[str, Any] | None:
    narratives = scenario.get("decision_narrative")
    if not isinstance(narratives, dict):
        return None
    narrative = narratives.get(state)
    return narrative if isinstance(narrative, dict) else None


def _gate_status(raw: str) -> str:
    lowered = raw.lower()
    if lowered.startswith("resolved"):
        return "RESOLVED"
    if lowered.startswith("known failure"):
        return "KNOWN_FAILURE"
    if lowered.startswith("not applicable"):
        return "NOT_APPLICABLE"
    return "UNAVAILABLE"


def project_simulated_case(
    public_case: dict[str, Any],
    scenario: dict[str, Any],
    capacity: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, Any]:
    validate_simulation_contract(scenario)
    sid = scenario["scenario_id"]
    inputs = scenario["synthetic_inputs"]
    labels = synthetic_display_labels()
    target_spec = inputs.get("target_specification", {})
    name = target_spec.get("name") if isinstance(target_spec, dict) else None
    application = (
        target_spec.get("application")
        if isinstance(target_spec, dict)
        else None
    )
    opportunity = dict(public_case["opportunity"])
    if isinstance(name, str) and name and isinstance(application, str) and application:
        opportunity["decision_object_status"] = "resolved"
    public_capability = public_case["domestic_capability"]
    hard_gates = inputs.get("hard_gates", {})
    profile_hard_gates: dict[str, dict[str, Any]] = {}
    if isinstance(hard_gates, dict):
        for gate_name, status in hard_gates.items():
            profile_hard_gates[gate_name] = {
                "status": _gate_status(str(status)),
                "evidence_ids": [f"{sid}::hard_gates"],
            }
    decision_gates = inputs.get("decision_specific_hard_gates", {})
    raw_unresolved = public_capability.get("unresolved_hard_gates", [])
    if isinstance(decision_gates, dict):
        unresolved = [
            row
            for row in raw_unresolved
            if isinstance(row, dict)
            and isinstance(row.get("name"), str)
            and (
                row["name"] not in decision_gates
                or not str(decision_gates[row["name"]]).lower().startswith(
                    "resolved"
                )
            )
        ]
    else:
        unresolved = [
            row for row in raw_unresolved if isinstance(row, dict)
        ]
    demand = inputs.get("demand", {})
    equivalence = inputs.get("equivalence")
    upgrade = inputs.get("upgrade", {})
    economics = inputs.get("economics", {})
    effective = capacity.get("effective_qualified_capacity_kt")
    if effective is None:
        effective = capacity.get("formula_capacity_kt")
    qualified_available = capacity.get("qualified_available_kt", effective)
    route_records: Any = "UNAVAILABLE"
    raw_routes = inputs.get("route_evidence")
    if isinstance(raw_routes, list) and raw_routes:
        projected_routes = []
        for record in raw_routes:
            projected = dict(record)
            projected["evidence_ids"] = [f"{sid}::route_evidence"]
            if projected.get("route_code") == _BROWNFIELD_ROUTE_CODE:
                projected["downside_cash_flows_m_sar"] = economics.get(
                    "cash_flows_without_support"
                )
                projected["hurdle_rate"] = economics.get("hurdle_rate")
                projected["national_value"] = economics.get("national_value")
                projected["competition"] = {
                    "existing_effective_capacity_kt": effective,
                    "proposed_incremental_capacity_kt": upgrade.get(
                        "incremental_capacity_kt"
                    ),
                    "downside_demand_kt": demand.get("downside_demand_kt"),
                }
            projected_routes.append(projected)
        route_records = projected_routes
    monitor = inputs.get("monitor_trigger")
    monitor_trigger = (
        {
            "domain": monitor["domain"],
            "condition_code": monitor["condition_code"],
            "evidence_ids": [f"{sid}::monitor_trigger"],
        }
        if isinstance(monitor, dict)
        else "UNAVAILABLE"
    )
    hard_exclusion_inputs = _project_hard_exclusions(
        inputs,
        sid,
        demand,
        economics,
        equivalence,
    )
    flows = inputs.get("production_and_retained_flows")
    domestic_flows = (
        {
            "retained_imports_kt": flows.get("retained_imports_kt", "UNAVAILABLE"),
            "domestic_origin_exports_kt": flows.get(
                "domestic_origin_exports_kt",
                "UNAVAILABLE",
            ),
            "reexports_kt": flows.get("reexports_kt", "UNAVAILABLE"),
            "evidence_ids": [f"{sid}::production_and_retained_flows"],
        }
        if isinstance(flows, dict)
        else {
            "retained_imports_kt": "UNAVAILABLE",
            "domestic_origin_exports_kt": "UNAVAILABLE",
            "reexports_kt": "UNAVAILABLE",
        }
    )
    evidence = [
        {
            "evidence_id": f"{sid}::{block}",
            "source": scenario["source"],
            "status": "synthetic",
            "evidence_class": scenario["evidence_class"],
            "synthetic_flag": True,
            "scenario_id": sid,
            "supports": [f"Simulation branch input: {block}"],
            "display_label": scenario["display_label"],
            "display_labels": labels,
        }
        for block in sorted(inputs)
    ]
    spec_equiv = "UNAVAILABLE"
    if isinstance(equivalence, dict):
        spec_equiv = {
            "domestic_product_equivalent": equivalence.get(
                "domestic_grade_equivalent"
            ),
            "qualified_available_kt": qualified_available,
            "evidence_ids": [f"{sid}::equivalence"],
        }
    return {
        "schema_version": public_case["schema_version"],
        "opportunity": opportunity,
        "snapshot_id": public_case["snapshot_id"],
        "as_of_date": public_case["as_of_date"],
        "domestic_capability": {
            **public_capability,
            "simulated_dimension_states": inputs.get("capability_states"),
            "profile_hard_gates": profile_hard_gates,
            "unresolved_hard_gates": unresolved,
        },
        "evidence": public_case["evidence"] + evidence,
        "decision_inputs": {
            "target_specification_demand": {
                "quantity_kt": demand.get("target_spec_demand_kt"),
                "downside_quantity_kt": demand.get("downside_demand_kt"),
                "evidence_ids": [f"{sid}::demand"],
            },
            "specification_equivalence": spec_equiv,
            "route_evidence": route_records,
            "monitor_trigger": monitor_trigger,
        },
        "hard_exclusion_inputs": hard_exclusion_inputs,
        "domestic_flows": domestic_flows,
        "trade": public_case["trade"],
    }


def _project_hard_exclusions(
    inputs: dict[str, Any],
    sid: str,
    demand: dict[str, Any],
    economics: dict[str, Any],
    equivalence: dict[str, Any] | None,
) -> dict[str, Any]:
    declared = inputs.get("hard_exclusion_inputs")
    if not isinstance(declared, dict):
        declared = {}
    effective = (
        equivalence.get("qualified_available_kt")
        if isinstance(equivalence, dict)
        else None
    )
    mes = economics.get("minimum_efficient_scale_kt")
    result: dict[str, Any] = {}
    for block_name, fields in (
        (
            "heterogeneous_residual_code",
            ("commercial_product_separable", "product_level_evidence_available"),
        ),
        ("downside_market_below_mes", ("credible_export_contract",)),
        ("unsatisfiable_hard_gate", ("gate_domain", "gate_satisfiability")),
        (
            "idle_equivalent_domestic_capacity",
            ("qualified_idle_capacity_kt", "binding_market_failure"),
        ),
        ("transitory_or_measurement_gap", ("dominant_cause",)),
        ("redundancy_or_crowd_out", ("competition_finding",)),
    ):
        block = declared.get(block_name, {})
        if not isinstance(block, dict):
            block = {}
        projected: dict[str, Any] = {
            key: block.get(key, "UNAVAILABLE") for key in fields
        }
        projected["evidence_ids"] = [f"{sid}::hard_exclusion_inputs"]
        if block_name == "downside_market_below_mes":
            projected["sustainable_downside_demand_kt"] = demand.get(
                "downside_demand_kt"
            )
            projected["minimum_efficient_scale_kt"] = mes
        if block_name == "idle_equivalent_domestic_capacity":
            projected["domestic_specification_equivalent"] = (
                equivalence.get("domestic_grade_equivalent")
                if isinstance(equivalence, dict)
                else "UNAVAILABLE"
            )
            projected["target_specification_demand_kt"] = demand.get(
                "target_spec_demand_kt"
            )
            if projected.get("qualified_idle_capacity_kt") == "UNAVAILABLE":
                projected["qualified_idle_capacity_kt"] = effective
        result[block_name] = projected
    return result
