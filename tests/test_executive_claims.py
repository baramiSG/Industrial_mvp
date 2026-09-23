"""Evidence-bound executive claim registry contracts."""

from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.data_repository import public_cases
from ior_mvp.decision_engine import analyze


def _claims_by_id(analysis: dict):
    from ior_mvp.executive.claims import build_claim_registry

    return {
        claim.claim_id: claim
        for claim in build_claim_registry(analysis)
    }


def test_trade_r3_r11_route_and_r12_claims_use_exact_stored_evidence() -> None:
    steel = analyze("SAU-H0-721049", "public")
    steel_claims = _claims_by_id(steel)
    assert steel_claims["metric.trade"].evidence_ids == ("S-WITS-721049",)
    assert steel_claims["metric.concentration"].evidence_ids == (
        "S-WITS-721049",
    )
    assert steel_claims["rule.R3"].evidence_ids == ("S-WITS-721049",)
    assert steel_claims["rule.R12"].evidence_ids == (
        "S-UNICOIL-EPD",
        "S-UNICOIL-SPEC",
        "S-WITS-721049",
    )
    assert set(steel_claims["route.5"].evidence_ids) == {
        "S-WITS-721049",
        "S-UNICOIL-EPD",
        "S-UNICOIL-SPEC",
        "S-HADEED",
    }

    polypropylene = analyze("SAU-H0-390210", "public")
    pp_claims = _claims_by_id(polypropylene)
    assert set(pp_claims["rule.R11"].evidence_ids) == {
        "P-WITS-390210",
        "P-SABIC",
        "P-ADVANCED",
        "P-TASNEE",
    }


def test_every_real_public_rule_id_uses_the_amended_exact_mapping() -> None:
    from ior_mvp.executive.models import ClaimStatus

    claims = _claims_by_id(analyze("SAU-H0-721049", "public"))
    assert {
        claim_id.removeprefix("rule.")
        for claim_id in claims
        if claim_id.startswith("rule.")
    } == {
        "R0",
        "R1-F",
        "R1-D",
        "R2",
        "R3",
        "R4-F",
        "R4-D",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9-S",
        "R10",
        "R11",
        "R12",
    }
    for rule_id in ("R1-F", "R1-D", "R2", "R3", "R4-F", "R4-D", "R5"):
        assert claims[f"rule.{rule_id}"].evidence_ids == (
            "S-WITS-721049",
        )
    for rule_id in ("R6", "R7", "R8", "R10"):
        claim = claims[f"rule.{rule_id}"]
        assert claim.status is ClaimStatus.UNRESOLVED
        assert claim.evidence_ids == ()
    assert "rule.R4" not in claims


def test_steel_simulated_claims_use_exact_current_scenario_sources() -> None:
    from ior_mvp.evidence import synthetic_display_labels
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.models import DecisionBranch, EvidenceClass

    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    claims = {
        claim.claim_id: claim
        for claim in build_claim_registry(public, simulated)
    }
    scenario_id = "SYN-MINISTRY-STEEL-001"
    prefix = f"{scenario_id}::"
    public_decision_ids = {
        "S-HADEED",
        "S-UNICOIL-EPD",
        "S-UNICOIL-SPEC",
        "S-WITS-721049",
    }
    expected_synthetic = {
        row["evidence_id"]
        for row in simulated["evidence"]
        if row.get("synthetic_flag") is True
    }
    expected_route = {
        f"{prefix}{suffix}"
        for suffix in (
            "route_evidence",
            "counterfactual",
            "hard_exclusion_inputs",
            "class_if_confirmed",
        )
    }
    expected_intervention = {
        f"{prefix}{suffix}"
        for suffix in ("economics", "evsi", "route_evidence", "counterfactual")
    }
    expected_decision = public_decision_ids | {
        f"{prefix}{suffix}"
        for suffix in (
            "class_if_confirmed",
            "counterfactual",
            "demand",
            "equivalence",
            "hard_exclusion_inputs",
            "route_evidence",
        )
    }
    expected = {
        "decision.simulated": expected_decision,
        "step.SIMULATED_EVIDENCE.simulated": expected_synthetic,
        "step.ROUTE_COMPARISON.simulated": expected_route,
        "step.INTERVENTION.simulated": expected_intervention,
        "step.CONDITIONS_AND_KILL.simulated": expected_decision,
    }
    for claim_id, evidence_ids in expected.items():
        claim = claims[claim_id]
        assert set(claim.evidence_ids) == evidence_ids
        assert claim.branch is DecisionBranch.SIMULATED
        assert claim.synthetic_flag is True
        assert claim.scenario_id == scenario_id
        assert claim.evidence_class is EvidenceClass.D
        assert claim.source == "DEMO_GENERATOR"
        assert claim.display_labels.model_dump() == synthetic_display_labels()


def test_all_cases_keep_public_and_simulated_claim_evidence_isolated() -> None:
    from ior_mvp.evidence import synthetic_display_labels
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.models import DecisionBranch

    labels = synthetic_display_labels()
    for opportunity_id in sorted(public_cases()):
        public = analyze(opportunity_id, "public")
        simulated = analyze(opportunity_id, "simulated")
        public_ids = {row["evidence_id"] for row in public["evidence"]}
        scenario_id = simulated["simulation_scenario"]["scenario_id"]
        synthetic_ids = {
            row["evidence_id"]
            for row in simulated["evidence"]
            if row.get("synthetic_flag") is True
        }
        claims = build_claim_registry(public, simulated)
        by_id = {claim.claim_id: claim for claim in claims}
        for claim in claims:
            referenced = set(claim.evidence_ids)
            if claim.branch is DecisionBranch.PUBLIC:
                assert referenced <= public_ids
                assert not referenced & synthetic_ids
                continue
            assert referenced <= public_ids | synthetic_ids
            assert referenced & synthetic_ids
            assert all(
                evidence_id.startswith(f"{scenario_id}::")
                for evidence_id in referenced & synthetic_ids
            )
            assert claim.display_labels.model_dump() == labels
        assert set(
            by_id["step.SIMULATED_EVIDENCE.simulated"].evidence_ids
        ) == synthetic_ids
        assert set(
            by_id["step.ROUTE_COMPARISON.simulated"].evidence_ids
        ) == {
            evidence_id
            for evidence_id in synthetic_ids
            if evidence_id.rsplit("::", 1)[-1]
            in {
                "route_evidence",
                "counterfactual",
                "hard_exclusion_inputs",
                "class_if_confirmed",
            }
        }
        assert set(
            by_id["step.INTERVENTION.simulated"].evidence_ids
        ) == {
            evidence_id
            for evidence_id in synthetic_ids
            if evidence_id.rsplit("::", 1)[-1]
            in {"economics", "evsi", "route_evidence", "counterfactual"}
        }
        assert (
            by_id["decision.simulated"].evidence_ids
            == by_id["step.CONDITIONS_AND_KILL.simulated"].evidence_ids
        )


def test_contradicted_and_genuinely_unresolved_claims_are_explicit() -> None:
    from ior_mvp.executive.models import ClaimStatus

    steel = deepcopy(analyze("SAU-H0-721049", "public"))
    steel["evidence"][0]["contradiction"] = "Conflicting trade disclosure."
    trade_claim = _claims_by_id(steel)["metric.trade"]
    assert trade_claim.status is ClaimStatus.CONTRADICTED
    assert trade_claim.evidence_ids == ("S-WITS-721049",)

    polypropylene = analyze("SAU-H0-390210", "public")
    product_claim = _claims_by_id(polypropylene)["metric.product_specification"]
    assert product_claim.status is ClaimStatus.UNRESOLVED
    assert product_claim.evidence_ids == ()
    assert product_claim.missing_need_codes == (
        "identity/tariff-line",
        "line-level production or producer-grade matrix",
        "target specification/application",
    )


def test_every_claim_reference_resolves_to_the_analysis_evidence_index() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
        "SAU-H6-294110",
    ):
        analysis = analyze(opportunity_id, "public")
        stored = {row["evidence_id"] for row in analysis["evidence"]}
        claims = _claims_by_id(analysis)
        assert all(
            set(claim.evidence_ids) <= stored
            for claim in claims.values()
        )


def test_absent_referenced_evidence_id_fails_closed() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    analysis = deepcopy(analyze("SAU-H0-721049", "public"))
    analysis["route_hypotheses"][5]["evidence_ids"] = ["MISSING-EVIDENCE"]

    with pytest.raises(
        ExecutiveIntegrityError,
        match="MISSING-EVIDENCE",
    ):
        build_claim_registry(analysis)


def test_duplicate_semantic_claim_id_fails_closed() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    analysis = deepcopy(analyze("SAU-H0-721049", "public"))
    analysis["route_hypotheses"].append(
        deepcopy(analysis["route_hypotheses"][0])
    )

    with pytest.raises(
        ExecutiveIntegrityError,
        match="Duplicate executive claim id: route.0",
    ):
        build_claim_registry(analysis)


def test_synthetic_evidence_cannot_attach_to_a_public_claim() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    analysis = deepcopy(analyze("SAU-H0-721049", "public"))
    analysis["evidence"].append(
        {
            "evidence_id": "SYN-LEAK",
            "source": "DEMO_GENERATOR",
            "status": "synthetic",
            "evidence_class": "D",
            "synthetic_flag": False,
            "scenario_id": "SYN-LEAK",
            "supports": ["TRADE_VALUE"],
        }
    )

    with pytest.raises(
        ExecutiveIntegrityError,
        match="synthetic evidence",
    ):
        build_claim_registry(analysis)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("source", "MINISTRY"),
        ("evidence_class", "A"),
        ("scenario_id", "SYN-WRONG"),
        ("synthetic_flag", False),
        ("display_labels", None),
    ),
)
def test_simulated_claims_reject_wrong_or_missing_synthetic_metadata(
    field: str,
    value: object,
) -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    public = analyze("SAU-H0-721049", "public")
    simulated = deepcopy(analyze("SAU-H0-721049", "simulated"))
    synthetic = next(
        row for row in simulated["evidence"] if row["synthetic_flag"] is True
    )
    synthetic[field] = value
    with pytest.raises(ExecutiveIntegrityError):
        build_claim_registry(public, simulated)


def test_simulated_claims_reject_cross_scenario_evidence() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    public = analyze("SAU-H0-721049", "public")
    simulated = deepcopy(analyze("SAU-H0-721049", "simulated"))
    foreign = next(
        row
        for row in analyze("SAU-H0-390210", "simulated")["evidence"]
        if row["synthetic_flag"] is True
    )
    simulated["evidence"].append(deepcopy(foreign))
    with pytest.raises(ExecutiveIntegrityError, match="scenario"):
        build_claim_registry(public, simulated)


def test_simulated_claims_reject_absent_references() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    public = analyze("SAU-H0-721049", "public")
    simulated = deepcopy(analyze("SAU-H0-721049", "simulated"))
    assessment = next(
        iter(
            simulated["simulation_decision"][
                "evidence_class_assessment"
            ].values()
        )
    )
    assessment["evidence_ids"] = ["ABSENT-SIMULATED-EVIDENCE"]
    with pytest.raises(
        ExecutiveIntegrityError,
        match="ABSENT-SIMULATED-EVIDENCE",
    ):
        build_claim_registry(public, simulated)


def test_simulated_claims_reject_incomplete_scenario_policy_labels() -> None:
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    public = analyze("SAU-H0-721049", "public")
    simulated = deepcopy(analyze("SAU-H0-721049", "simulated"))
    simulated["simulation_scenario"]["display_labels"] = {
        "en": "UNAPPROVED",
        "ar": "UNAPPROVED",
    }
    with pytest.raises(ExecutiveIntegrityError, match="labels"):
        build_claim_registry(public, simulated)


@pytest.mark.parametrize("claim_id", ["decision.simulated", "step.CONDITIONS_AND_KILL.simulated"])
def test_am4_steel_simulated_claim_preserves_linked_contradiction(claim_id):
    from ior_mvp.executive.claims import build_claim_registry
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    claims = build_claim_registry(public, simulated)
    claim = next(c for c in claims if c.claim_id == claim_id)
    assert "S-UNICOIL-SPEC" in claim.evidence_ids
    assert claim.status.value == "CONTRADICTED"
    assert tuple(c for c in claims if c.branch.value == "PUBLIC") == build_claim_registry(public)
    assert claim.branch.value == "SIMULATED" and claim.evidence_class.value == "D"
    assert claim.scenario_id == "SYN-MINISTRY-STEEL-001"


@pytest.mark.parametrize("suffix,expected", [("economics", "CONTRADICTED"), ("demand", "SUPPORTED")])
def test_am4_only_linked_synthetic_contradictions_affect_claim(suffix, expected):
    from ior_mvp.executive.claims import build_claim_registry
    public = analyze("SAU-H0-721049", "public")
    simulated = deepcopy(analyze("SAU-H0-721049", "simulated"))
    original_decision = deepcopy(simulated["simulation_decision"])
    row = next(r for r in simulated["evidence"] if r["evidence_id"] == f"SYN-MINISTRY-STEEL-001::{suffix}")
    row["contradiction"] = "Injected stored contradiction"
    claim = next(c for c in build_claim_registry(public, simulated) if c.claim_id == "step.INTERVENTION.simulated")
    assert claim.status.value == expected
    assert (row["evidence_id"] in claim.evidence_ids) == (suffix == "economics")
    assert simulated["simulation_decision"] == original_decision


def test_am4_no_fabricated_missing_need():
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError
    public = deepcopy(analyze("SAU-H0-721049", "public"))
    r12 = next(r for r in public["rules"] if r["rule_id"] == "R12")
    r12["metrics"]["evidence_needs"] = []
    with pytest.raises(ExecutiveIntegrityError, match="need|support"):
        build_claim_registry(public)
    r12["metrics"]["evidence_needs"] = [{"need_code": "route economics", "evidence_ids": []}]
    claim = next(c for c in build_claim_registry(public) if c.claim_id == "rule.R12")
    assert claim.status.value == "UNRESOLVED"
    assert claim.missing_need_codes == ("route economics",) and not claim.evidence_ids


@pytest.mark.parametrize("opportunity_id", ["SAU-H6-760429", "SAU-H6-760711"])
def test_am4_aluminium_dependency_retained_but_claims_scenario_local(opportunity_id):
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.graph.engine_feed import shared_enabler_inputs
    from ior_mvp.graph.repository import graph_projection
    from ior_mvp.data_repository import synthetic_scenarios
    from ior_mvp.evidence import synthetic_evidence_rows
    public = analyze(opportunity_id, "public")
    simulated = analyze(opportunity_id, "simulated")
    original = deepcopy(simulated)
    scenario_id = simulated["simulation_scenario"]["scenario_id"]
    feed = shared_enabler_inputs(graph_projection(), opportunity_id, branch=("simulated", scenario_id))
    expected = {"SYN-MINISTRY-ALU-FOIL-001::shared_enabler", "SYN-MINISTRY-ALU-PROFILES-001::shared_enabler"}
    route = next(r for r in simulated["simulation_decision"]["route_hypotheses"] if r["route_code"] == 8)
    assert set(route["evidence_ids"]) == set(route["shared_enabler"]["evidence_ids"]) == set(feed["evidence_ids"]) == expected
    assert feed["dependent_opportunity_ids"] == ["SAU-H6-760429", "SAU-H6-760711"]
    for dependent in feed["dependent_opportunity_ids"]:
        scenario = synthetic_scenarios()[dependent]
        assert scenario["synthetic_inputs"]["shared_enabler"]["enabler_id"] == feed["enabler_id"]
        assert f"{scenario['scenario_id']}::shared_enabler" in {r["evidence_id"] for r in synthetic_evidence_rows(scenario)}
    stored = {r["evidence_id"] for r in simulated["evidence"]}
    for claim in build_claim_registry(public, simulated):
        assert set(claim.evidence_ids) <= stored
    assert simulated == original


@pytest.mark.parametrize("mutation", ["unrelated_shared", "absent", "wrong_route", "wrong_field",
                                      "forged_declaration", "missing_declaration", "missing_stored"])
def test_am4_claims_reject_invalid_foreign_dependencies(monkeypatch, mutation):
    from ior_mvp.executive.claims import build_claim_registry
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError
    from ior_mvp.data_repository import synthetic_scenarios
    from ior_mvp.evidence import synthetic_evidence_rows
    import ior_mvp.executive.provenance as provenance

    public = analyze("SAU-H6-760429", "public")
    simulated = deepcopy(analyze("SAU-H6-760429", "simulated"))
    decision = simulated["simulation_decision"]
    foreign_id = "SYN-MINISTRY-ALU-FOIL-001::shared_enabler"
    if mutation in {"unrelated_shared", "absent", "wrong_route"}:
        bad = {"unrelated_shared": "ANY-UNRELATED::shared_enabler",
               "absent": "ANY-UNRELATED::other_suffix", "wrong_route": foreign_id}[mutation]
        decision["route_hypotheses"][0]["evidence_ids"].append(bad)
    elif mutation == "wrong_field":
        decision["unrelated"] = {"evidence_ids": [foreign_id]}
    elif mutation == "missing_stored":
        monkeypatch.setattr(provenance, "synthetic_evidence_rows", lambda scenario: [
            row for row in synthetic_evidence_rows(scenario) if row["evidence_id"] != foreign_id
        ], raising=False)
    else:
        scenarios = deepcopy(synthetic_scenarios())
        inputs = scenarios["SAU-H6-760711"]["synthetic_inputs"]
        if mutation == "missing_declaration":
            inputs.pop("shared_enabler")
        else:
            inputs["shared_enabler"]["enabler_id"] = "FORGED"
        monkeypatch.setattr(provenance, "synthetic_scenarios", lambda: scenarios, raising=False)
    with pytest.raises(ExecutiveIntegrityError):
        build_claim_registry(public, simulated)
