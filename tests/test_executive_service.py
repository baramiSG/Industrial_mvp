"""Executive summary and case service contracts."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import fsum

import pytest

from ior_mvp.decision_engine import analyze
from ior_mvp.executive.service import (
    ExecutiveOpportunityNotFoundError,
    build_executive_case,
    build_executive_summary,
    clear_executive_caches,
)

ALL_IDS = (
    "SAU-H0-390210",
    "SAU-H0-721049",
    "SAU-H6-294110",
    "SAU-H6-294120",
    "SAU-H6-310430",
    "SAU-H6-310510",
    "SAU-H6-392010",
    "SAU-H6-721012",
    "SAU-H6-721061",
    "SAU-H6-760429",
    "SAU-H6-760711",
)
EXPECTED_LOADED_IDS = {
    "IDENTITY_TARIFF": tuple(
        row for row in ALL_IDS if row != "SAU-H0-721049"
    ),
    "TARGET_SPECIFICATION_DEMAND": ALL_IDS,
    "PRODUCER_CAPABILITY": ALL_IDS,
    "EFFECTIVE_CAPACITY_ALLOCATION": ALL_IDS,
    "RETAINED_FLOW": ("SAU-H0-721049",),
    "ROUTE_ECONOMICS": ALL_IDS,
}
EXPECTED_SCREENING = {
    "IDENTITY_TARIFF": (
        5443,
        "cf4eeb92da5aa7d804047da1e49a3add7674fc874048660e40021ee20c050fe0",
    ),
    "TARGET_SPECIFICATION_DEMAND": (
        4996,
        "d606c484a2bead7baef7a258a68eba901519d53b733ac5c655fc6abbd8a7e634",
    ),
    "PRODUCER_CAPABILITY": (
        4996,
        "d606c484a2bead7baef7a258a68eba901519d53b733ac5c655fc6abbd8a7e634",
    ),
    "EFFECTIVE_CAPACITY_ALLOCATION": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
    "RETAINED_FLOW": (
        1618,
        "e7fe82dfa03c2765f845f51384560be0bb6c902493ea0981ea4ee3c28cc49a63",
    ),
    "ROUTE_ECONOMICS": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
}


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_executive_caches()
    yield
    clear_executive_caches()


def test_public_dataset_counts_and_affected_ids_match_frozen_fixtures() -> None:
    rows = {
        row.dataset_kind.value: row
        for row in build_executive_summary().public_dataset_unlocks
    }
    assert set(rows) == set(EXPECTED_LOADED_IDS)
    for kind, expected_ids in EXPECTED_LOADED_IDS.items():
        row = rows[kind]
        assert row.loaded_opportunity_ids == expected_ids
        assert row.loaded_case_count == len(expected_ids)
        expected_count, expected_digest = EXPECTED_SCREENING[kind]
        assert row.screening_record_count == expected_count
        assert sha256(
            "\n".join(row.screening_hs6).encode()
        ).hexdigest() == expected_digest
        assert row.synthetic_flag is False


def test_class_d_evsi_is_separate_complete_and_fsum_reconciled() -> None:
    evsi = build_executive_summary().synthetic_evsi
    assert evsi.synthetic_flag is True
    assert evsi.evidence_class.value == "D"
    assert evsi.source == "DEMO_GENERATOR"
    assert evsi.display_labels.model_dump() == {
        "en": "SIMULATED — NOT MINISTRY EVIDENCE",
        "ar": "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة",
    }
    assert (evsi.available_case_count, evsi.unavailable_case_count) == (7, 4)
    values = tuple(
        row.approximate_evsi_m_sar
        for row in evsi.cases
        if row.approximate_evsi_m_sar is not None
    )
    assert fsum(values) == evsi.total_approximate_evsi_m_sar == 371.55
    assert evsi.positive_approximate_evsi_m_sar == 374.95
    assert evsi.non_positive_approximate_evsi_m_sar == -3.4


def test_integrity_zero_is_computed_from_all_loaded_pairs() -> None:
    from ior_mvp.executive.models import IntegrityCheckId, IntegrityResult

    integrity = build_executive_summary().integrity
    assert integrity.status is IntegrityResult.PASS
    assert integrity.violation_count == sum(
        row.violation_count for row in integrity.checks
    ) == 0
    assert tuple(row.check_id for row in integrity.checks) == tuple(
        IntegrityCheckId
    )


@pytest.mark.parametrize(
    ("mutation", "expected_check"),
    (
        ("public_synthetic_leak", "PUBLIC_SYNTHETIC_LEAKAGE"),
        ("changed_real_decision", "REAL_DECISION_EQUALITY"),
        ("wrong_source", "SYNTHETIC_METADATA"),
        ("wrong_class", "SYNTHETIC_METADATA"),
        ("wrong_flag", "SYNTHETIC_METADATA"),
        ("wrong_scenario", "SYNTHETIC_METADATA"),
        ("failed_reconciliation", "SCENARIO_VALIDATION"),
        ("failed_backtest", "SCENARIO_VALIDATION"),
    ),
)
def test_integrity_negative_fixtures_are_counted(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    expected_check: str,
) -> None:
    import ior_mvp.executive.service as service
    from ior_mvp.executive.models import IntegrityResult

    def mutated_analyze(opportunity_id: str, mode: str = "public"):
        analysis = deepcopy(analyze(opportunity_id, mode))
        if opportunity_id != "SAU-H0-721049":
            return analysis
        if mutation == "public_synthetic_leak" and mode == "public":
            simulated = analyze(opportunity_id, "simulated")
            analysis["evidence"].append(
                deepcopy(
                    next(
                        row
                        for row in simulated["evidence"]
                        if row["synthetic_flag"] is True
                    )
                )
            )
        if mode != "simulated":
            return analysis
        if mutation == "changed_real_decision":
            analysis["real_decision"]["state"] = "ADVANCE"
        elif mutation.startswith("wrong_"):
            synthetic = next(
                row
                for row in analysis["evidence"]
                if row["synthetic_flag"] is True
            )
            field, value = {
                "wrong_source": ("source", "MINISTRY"),
                "wrong_class": ("evidence_class", "A"),
                "wrong_flag": ("synthetic_flag", False),
                "wrong_scenario": ("scenario_id", "SYN-WRONG"),
            }[mutation]
            synthetic[field] = value
        elif mutation == "failed_reconciliation":
            analysis["integrity"]["scenario_reconciliation"]["status"] = "FAIL"
        elif mutation == "failed_backtest":
            analysis["integrity"]["ground_truth_backtest"]["match"] = False
        return analysis

    monkeypatch.setattr(service, "analyze", mutated_analyze)
    integrity = service.build_executive_summary().integrity
    failed = {
        row.check_id.value: row
        for row in integrity.checks
        if row.status is IntegrityResult.FAIL
    }
    assert set(failed) == {expected_check}
    assert failed[expected_check].affected_ids == ("SAU-H0-721049",)
    assert integrity.violation_count == 1


def test_steel_has_exact_steps_vectors_and_existing_branch_outcomes() -> None:
    from ior_mvp.executive.models import DecisionVectorId, ExecutiveStepId

    executive = build_executive_case("SAU-H0-721049")
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    assert tuple(row.step_id for row in executive.steps) == tuple(ExecutiveStepId)
    assert tuple(row.vector_id for row in executive.vectors) == tuple(
        DecisionVectorId
    )
    assert executive.decisions.public.state.value == public["real_decision"]["state"]
    assert executive.decisions.public.route_code == public["real_decision"]["route_code"]
    assert (
        executive.decisions.simulated.state.value
        == simulated["simulation_decision"]["state"]
    )
    assert executive.decisions.simulated.route_code == 5
    assert all(
        (
            f"step.{row.step_id.value}" in row.claim_ids
            if row.step_id not in {ExecutiveStepId.SIMULATED_EVIDENCE, ExecutiveStepId.INTERVENTION}
            else f"step.{row.step_id.value}.simulated" in row.claim_ids
        )
        for row in executive.steps
    )
    keys = {
        value.key for vector in executive.vectors for value in vector.values
    }
    assert not {"combined_score", "score", "rank", "ordinal_rank"} & keys


def test_simulated_step_values_carry_exact_branch_claim_evidence() -> None:
    from ior_mvp.executive.models import ExecutiveStepId

    executive = build_executive_case("SAU-H0-721049")
    claims = {claim.claim_id: claim for claim in executive.claims}
    steps = {step.step_id: step for step in executive.steps}
    expected_claim_ids = {
        ExecutiveStepId.SIMULATED_EVIDENCE: (
            "step.SIMULATED_EVIDENCE.simulated",
        ),
        ExecutiveStepId.ROUTE_COMPARISON: (
            "step.ROUTE_COMPARISON.simulated",
        ),
        ExecutiveStepId.INTERVENTION: (
            "step.INTERVENTION.simulated",
        ),
        ExecutiveStepId.CONDITIONS_AND_KILL: (
            "step.CONDITIONS_AND_KILL.simulated",
        ),
    }
    for step_id, simulated_claim_ids in expected_claim_ids.items():
        step = steps[step_id]
        assert set(simulated_claim_ids) <= set(step.claim_ids)
        expected_evidence = set(claims[simulated_claim_ids[0]].evidence_ids)
        simulated_values = tuple(
            value
            for value in step.values
            if (
                step_id
                in {
                    ExecutiveStepId.SIMULATED_EVIDENCE,
                    ExecutiveStepId.INTERVENTION,
                }
                or value.key.startswith("simulated_")
            )
        )
        assert simulated_values
        assert all(
            set(value.evidence_ids) == expected_evidence
            for value in simulated_values
        )


def test_polypropylene_rejection_does_not_invent_support() -> None:
    from ior_mvp.executive.models import ExecutiveStepId

    executive = build_executive_case("SAU-H0-390210")
    assert (
        executive.decisions.public.state.value,
        executive.decisions.public.route_code,
        executive.decisions.simulated.state.value,
        executive.decisions.simulated.route_code,
    ) == ("REJECT", 0, "REJECT", 0)
    intervention = next(
        row
        for row in executive.steps
        if row.step_id is ExecutiveStepId.INTERVENTION
    )
    values = {row.key: row.value for row in intervention.values}
    assert values["simulated_selected_route_code"] == 0
    assert values["simulated_minimum_effective_support_m_sar"] == 0.0
    assert values["simulated_incremental_national_value_m_sar"] is None


def test_case_without_scenario_has_typed_unavailable_simulation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ior_mvp.executive.service as service
    from ior_mvp.executive.models import AvailabilityStatus, ExecutiveStepId

    monkeypatch.setattr(service, "synthetic_scenarios", lambda: {})
    executive = service.build_executive_case("SAU-H0-721049")
    assert executive.decisions.simulated.availability is AvailabilityStatus.UNAVAILABLE
    simulated_step = next(
        row
        for row in executive.steps
        if row.step_id is ExecutiveStepId.SIMULATED_EVIDENCE
    )
    assert simulated_step.availability is AvailabilityStatus.UNAVAILABLE


def test_unknown_and_malformed_case_inputs_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ior_mvp.executive.service as service
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    with pytest.raises(ExecutiveOpportunityNotFoundError):
        build_executive_case("SAU-H0-000000")

    def malformed_analyze(opportunity_id: str, mode: str = "public"):
        analysis = deepcopy(analyze(opportunity_id, mode))
        if mode == "public":
            analysis["route_hypotheses"][5]["evidence_ids"] = ["ABSENT"]
        return analysis

    monkeypatch.setattr(service, "analyze", malformed_analyze)
    with pytest.raises(ExecutiveIntegrityError, match="ABSENT"):
        service.build_executive_case("SAU-H0-721049")


@pytest.mark.parametrize("opportunity_id", ALL_IDS)
def test_am4_all_cases_preserve_typed_steps_vectors_and_decisions(opportunity_id):
    from ior_mvp.data_repository import public_cases
    from ior_mvp.executive.models import ExecutiveCase, ExecutiveStepId, DecisionVectorId

    assert tuple(sorted(public_cases())) == ALL_IDS
    public = analyze(opportunity_id, "public")
    simulated = analyze(opportunity_id, "simulated")
    case = build_executive_case(opportunity_id)
    assert isinstance(case, ExecutiveCase)
    assert tuple(s.step_id for s in case.steps) == tuple(ExecutiveStepId)
    assert tuple(v.vector_id for v in case.vectors) == tuple(DecisionVectorId)
    for projected, original in ((case.decisions.public, public["real_decision"]),
                                (case.decisions.simulated, simulated["simulation_decision"])):
        assert (projected.state.value, projected.route_code) == (original["state"], original["route_code"])
    assert simulated["real_decision"] == public["real_decision"]
    value = next(v for s in case.steps for v in s.values if v.key == "preferred_route_code")
    absent = opportunity_id not in {"SAU-H0-390210", "SAU-H0-721049", "SAU-H6-760429"}
    assert (value.availability.value, value.value) == (
        ("NOT_CALCULABLE", None) if absent else ("AVAILABLE", public["preferred_hypothesis"]["route_code"])
    )


@pytest.mark.parametrize("opportunity_id", ["SAU-H0-721049", "SAU-H0-390210"])
@pytest.mark.parametrize("available", [True, False])
def test_am4_intervention_is_exclusively_simulated(monkeypatch, opportunity_id, available):
    import ior_mvp.executive.service as service

    if not available:
        monkeypatch.setattr(service, "synthetic_scenarios", lambda: {})
    case = build_executive_case(opportunity_id)
    step = next(s for s in case.steps if s.step_id.value == "INTERVENTION")
    assert step.claim_ids == (("step.INTERVENTION.simulated",) if available else ())
    assert {v.key for v in step.values} == {
        "simulated_selected_route_code", "simulated_unsupported_npv_m_sar",
        "simulated_minimum_effective_support_m_sar", "simulated_incremental_national_value_m_sar",
        "simulated_approximate_evsi_m_sar",
    }
    assert any(c.claim_id == "step.INTERVENTION" for c in case.claims)
    if not available:
        assert step.availability.value == "UNAVAILABLE"
        assert all(v.value is None and not v.evidence_ids and v.availability.value == "UNAVAILABLE" for v in step.values)
    else:
        original = analyze(opportunity_id, "simulated")
        expected = (original["simulation_decision"]["route_code"], original["economics"].get("unsupported_npv_m"),
                    original["economics"]["minimum_effective_support_m"],
                    (original["economics"].get("national_value") or {}).get("incremental_national_value_m_sar"),
                    (original.get("evsi") or {}).get("approximate_evsi_m_sar"))
        assert tuple(v.value for v in step.values) == expected
