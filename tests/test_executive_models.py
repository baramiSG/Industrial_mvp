"""Typed executive response-model contracts."""

from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError


def _models():
    from ior_mvp.executive import models

    return models


def _labels():
    models = _models()
    return models.PolicyLabels(
        en="SIMULATED — NOT MINISTRY EVIDENCE",
        ar="محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة",
    )


def _opportunity():
    models = _models()
    return models.OpportunityReference(
        opportunity_id="SAU-H0-721049",
        hs6="721049",
        name_en="Zinc-coated flat steel",
        name_ar="منتجات مسطحة مطلية بالزنك",
        sector_profile="coated_steel",
        snapshot_id="PUBLIC-SAU-H0-721049-2026-08-31",
        as_of_date="2026-08-31",
    )


def _public_decision():
    models = _models()
    return models.DecisionProjection(
        branch=models.DecisionBranch.PUBLIC,
        availability=models.AvailabilityStatus.AVAILABLE,
        state=models.DecisionState.INVESTIGATE,
        route_code=None,
        synthetic_flag=False,
        headline="INVESTIGATE",
        rationale="Route-changing evidence remains unresolved.",
        conditions=("Obtain line-level evidence.",),
        kill_conditions=("Equivalent qualified supply closes the gap.",),
    )


def _simulated_decision():
    models = _models()
    return models.DecisionProjection(
        branch=models.DecisionBranch.SIMULATED,
        availability=models.AvailabilityStatus.AVAILABLE,
        state=models.DecisionState.ADVANCE,
        route_code=5,
        synthetic_flag=True,
        scenario_id="SYN-MINISTRY-STEEL-001",
        evidence_class=models.EvidenceClass.D,
        source="DEMO_GENERATOR",
        display_labels=_labels(),
        headline="SIMULATED ADVANCE",
        rationale="Class-D scenario resolves the route.",
        conditions=("Customer qualification passes.",),
        kill_conditions=("Demand falls below the route threshold.",),
    )


def _step(step_id):
    models = _models()
    return models.ExecutiveStep(
        step_id=step_id,
        availability=models.AvailabilityStatus.AVAILABLE,
        claim_ids=(f"step.{step_id.value.lower()}",),
        values=(
            models.ExecutiveValue(
                key="state",
                availability=models.AvailabilityStatus.AVAILABLE,
                value="INVESTIGATE",
                evidence_ids=("E-TRADE",),
            ),
        ),
    )


def _vector(vector_id):
    models = _models()
    return models.DecisionVector(
        vector_id=vector_id,
        availability=models.AvailabilityStatus.AVAILABLE,
        claim_ids=("decision.public",),
        values=(
            models.ExecutiveValue(
                key="signal",
                availability=models.AvailabilityStatus.AVAILABLE,
                value=True,
                evidence_ids=("E-TRADE",),
            ),
        ),
    )


def _case():
    models = _models()
    return models.ExecutiveCase(
        schema_version="1.0.0",
        opportunity=_opportunity(),
        decisions=models.DecisionComparison(
            public=_public_decision(),
            simulated=_simulated_decision(),
        ),
        steps=tuple(_step(step_id) for step_id in models.ExecutiveStepId),
        vectors=tuple(_vector(vector_id) for vector_id in models.DecisionVectorId),
        claims=(
            models.ClaimReference(
                claim_id="decision.public",
                status=models.ClaimStatus.SUPPORTED,
                evidence_ids=("E-TRADE",),
            ),
            *(
                models.ClaimReference(
                    claim_id=f"step.{step_id.value.lower()}",
                    status=models.ClaimStatus.SUPPORTED,
                    evidence_ids=("E-TRADE",),
                )
                for step_id in models.ExecutiveStepId
            ),
        ),
        evidence_index=(
            models.EvidenceReference(
                evidence_id="E-TRADE",
                source="UN_COMTRADE",
                status=models.EvidenceStatus.OBSERVED,
                evidence_class=models.EvidenceClass.B,
                synthetic_flag=False,
                supports=("TRADE_VALUE",),
            ),
        ),
        authority=(
            models.AuthorityReference(key="methodology_version", value="final"),
        ),
    )


def _summary():
    models = _models()
    return models.ExecutiveSummary(
        schema_version="1.0.0",
        opportunities=(_opportunity(),),
        public_dataset_unlocks=(
            models.DatasetUnlock(
                dataset_kind=models.DatasetKind.IDENTITY_TARIFF,
                need_codes=("identity/tariff-line",),
                synthetic_flag=False,
                loaded_case_count=1,
                loaded_opportunity_ids=("SAU-H0-721049",),
                screening_record_count=2,
                screening_hs6=("721049", "721061"),
            ),
        ),
        synthetic_evsi=models.SyntheticEvsiSummary(
            synthetic_flag=True,
            evidence_class=models.EvidenceClass.D,
            source="DEMO_GENERATOR",
            display_labels=_labels(),
            available_case_count=1,
            unavailable_case_count=0,
            total_approximate_evsi_m_sar=129.3,
            positive_approximate_evsi_m_sar=129.3,
            non_positive_approximate_evsi_m_sar=0.0,
            cases=(
                models.SyntheticEvsiCase(
                    opportunity_id="SAU-H0-721049",
                    scenario_id="SYN-MINISTRY-STEEL-001",
                    availability=models.AvailabilityStatus.AVAILABLE,
                    next_fact="Plant allocation",
                    approximate_evsi_m_sar=129.3,
                    route_change_probability=0.7,
                    value_difference_m_sar=200.0,
                    evidence_cost_m_sar=5.0,
                    delay_cost_m_sar=5.7,
                ),
            ),
        ),
        integrity=models.IntegritySummary(
            status=models.IntegrityResult.PASS,
            violation_count=0,
            checks=tuple(
                models.IntegrityCheck(
                    check_id=check_id,
                    status=models.IntegrityResult.PASS,
                    violation_count=0,
                )
                for check_id in models.IntegrityCheckId
            ),
        ),
        authority=(
            models.AuthorityReference(key="methodology_version", value="final"),
        ),
    )


def test_valid_summary_and_case_models_serialize_deterministically() -> None:
    summary = _summary()
    case = _case()

    assert summary.model_dump(mode="json") == summary.model_dump(mode="json")
    assert case.model_dump(mode="json") == case.model_dump(mode="json")
    assert [row["step_id"] for row in case.model_dump(mode="json")["steps"]] == [
        step_id.value for step_id in _models().ExecutiveStepId
    ]
    assert [row["vector_id"] for row in case.model_dump(mode="json")["vectors"]] == [
        vector_id.value for vector_id in _models().DecisionVectorId
    ]


def test_not_calculable_unavailable_and_unmapped_are_typed_and_visible() -> None:
    models = _models()
    unavailable = models.DecisionProjection(
        branch=models.DecisionBranch.SIMULATED,
        availability=models.AvailabilityStatus.UNAVAILABLE,
        state=None,
        route_code=None,
        synthetic_flag=False,
        conditions=(),
        kill_conditions=(),
    )
    value = models.ExecutiveValue(
        key="economics",
        availability=models.AvailabilityStatus.NOT_CALCULABLE,
        value=None,
        need_codes=("route economics",),
    )
    unmapped = models.DatasetUnlock(
        dataset_kind=models.DatasetKind.UNMAPPED,
        need_codes=("future governed need",),
        synthetic_flag=False,
        loaded_case_count=1,
        loaded_opportunity_ids=("SAU-H0-721049",),
        screening_record_count=0,
        screening_hs6=(),
    )

    assert unavailable.availability is models.AvailabilityStatus.UNAVAILABLE
    assert value.value is None
    assert unmapped.need_codes == ("future governed need",)


@pytest.mark.parametrize(
    "mutation",
    (
        "duplicate_steps",
        "wrong_step_order",
        "duplicate_vectors",
        "wrong_vector_order",
        "duplicate_claims",
    ),
)
def test_case_rejects_duplicate_or_out_of_order_contract_ids(mutation: str) -> None:
    payload = _case().model_dump(mode="python")
    payload["steps"] = list(payload["steps"])
    payload["vectors"] = list(payload["vectors"])
    if mutation == "duplicate_steps":
        payload["steps"][-1] = deepcopy(payload["steps"][0])
    elif mutation == "wrong_step_order":
        payload["steps"][0], payload["steps"][1] = (
            payload["steps"][1],
            payload["steps"][0],
        )
    elif mutation == "duplicate_vectors":
        payload["vectors"][-1] = deepcopy(payload["vectors"][0])
    elif mutation == "wrong_vector_order":
        payload["vectors"][0], payload["vectors"][1] = (
            payload["vectors"][1],
            payload["vectors"][0],
        )
    else:
        payload["claims"] = (*payload["claims"], deepcopy(payload["claims"][0]))

    with pytest.raises(ValidationError):
        _models().ExecutiveCase.model_validate(payload)


def test_public_decision_rejects_synthetic_metadata() -> None:
    payload = _public_decision().model_dump(mode="python")
    payload.update(
        {
            "synthetic_flag": True,
            "scenario_id": "SYN-INVALID",
            "evidence_class": "D",
            "source": "DEMO_GENERATOR",
            "display_labels": _labels(),
        }
    )

    with pytest.raises(ValidationError):
        _models().DecisionProjection.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("scenario_id", None),
        ("evidence_class", None),
        ("source", None),
        ("display_labels", None),
    ),
)
def test_available_simulated_decision_requires_class_d_metadata(
    field: str,
    value: object,
) -> None:
    payload = _simulated_decision().model_dump(mode="python")
    payload[field] = value

    with pytest.raises(ValidationError):
        _models().DecisionProjection.model_validate(payload)


def test_summary_rejects_mixed_public_dataset_and_synthetic_evsi_branches() -> None:
    models = _models()
    dataset_payload = _summary().public_dataset_unlocks[0].model_dump(mode="python")
    dataset_payload["synthetic_flag"] = True
    with pytest.raises(ValidationError):
        models.DatasetUnlock.model_validate(dataset_payload)

    evsi_payload = _summary().synthetic_evsi.model_dump(mode="python")
    evsi_payload["synthetic_flag"] = False
    with pytest.raises(ValidationError):
        models.SyntheticEvsiSummary.model_validate(evsi_payload)


def test_claim_reference_enforces_branch_specific_provenance() -> None:
    models = _models()
    simulated = models.ClaimReference(
        claim_id="decision.simulated",
        status=models.ClaimStatus.SUPPORTED,
        evidence_ids=("E-PUBLIC", "SYN-SCENARIO::route_evidence"),
        branch=models.DecisionBranch.SIMULATED,
        synthetic_flag=True,
        scenario_id="SYN-SCENARIO",
        evidence_class=models.EvidenceClass.D,
        source="DEMO_GENERATOR",
        display_labels=_labels(),
    )
    assert simulated.branch is models.DecisionBranch.SIMULATED

    public_payload = simulated.model_dump(mode="python")
    public_payload.update(
        {
            "claim_id": "decision.public",
            "branch": models.DecisionBranch.PUBLIC,
            "synthetic_flag": False,
        }
    )
    with pytest.raises(ValidationError):
        models.ClaimReference.model_validate(public_payload)

    for field in (
        "scenario_id",
        "evidence_class",
        "source",
        "display_labels",
    ):
        payload = simulated.model_dump(mode="python")
        payload[field] = None
        with pytest.raises(ValidationError):
            models.ClaimReference.model_validate(payload)
