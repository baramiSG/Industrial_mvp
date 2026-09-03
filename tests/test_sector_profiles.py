from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.capability import (
    evaluate_capability,
    publication_allowed,
    route_band,
)
from ior_mvp.config import (
    sector_profiles_config,
    thresholds_config,
)


DIMENSIONS = (
    "feedstock_chemistry",
    "core_process_route",
    "equipment_envelope",
    "finishing_spec_control",
    "qa_lab_metrology",
    "certification_customer_qualification",
    "capacity_time_window",
    "utilities_ehs_permitting",
    "skills_market_integration",
)
EXPECTED_NEW_PROFILES = {
    "pharma_api": {
        "label": "Pharma/API",
        "weights": (0.10, 0.20, 0.10, 0.10, 0.15, 0.15, 0.05, 0.10, 0.05),
        "hard_gates": (
            "named_molecule_and_synthesis_route",
            "gmp",
            "containment",
            "impurity_control",
            "analytical_validation",
            "effluent",
            "ip_fto",
        ),
    },
    "fertilizers": {
        "label": "Fertilizers",
        "weights": (0.15, 0.20, 0.15, 0.10, 0.05, 0.05, 0.10, 0.15, 0.05),
        "hard_gates": (
            "feedstock_route",
            "formulation_granulation",
            "nutrient_basis",
            "agronomic_performance",
            "emissions_and_safe_handling",
        ),
    },
    "fabricated_aluminium": {
        "label": "Fabricated aluminium",
        "weights": (0.10, 0.15, 0.15, 0.15, 0.10, 0.15, 0.10, 0.05, 0.05),
        "hard_gates": (
            "alloy",
            "forming_fabrication",
            "heat_treatment",
            "joining_finishing",
            "engineering_certification",
            "customer_liability",
        ),
    },
}
K70_SUBSETS = {
    "coated_steel": {
        "feedstock_chemistry",
        "core_process_route",
        "equipment_envelope",
        "finishing_spec_control",
        "qa_lab_metrology",
    },
    "technical_plastics": {
        "feedstock_chemistry",
        "core_process_route",
        "equipment_envelope",
        "finishing_spec_control",
        "qa_lab_metrology",
    },
    "pharma_api": {
        "feedstock_chemistry",
        "core_process_route",
        "equipment_envelope",
        "finishing_spec_control",
        "qa_lab_metrology",
        "capacity_time_window",
    },
    "fertilizers": {
        "feedstock_chemistry",
        "core_process_route",
        "equipment_envelope",
        "finishing_spec_control",
        "qa_lab_metrology",
        "certification_customer_qualification",
    },
    "fabricated_aluminium": {
        "feedstock_chemistry",
        "core_process_route",
        "equipment_envelope",
        "finishing_spec_control",
        "qa_lab_metrology",
        "utilities_ehs_permitting",
    },
}


def _resolved_gates(profile: str) -> dict[str, dict]:
    gates = sector_profiles_config()["profiles"][profile][
        "hard_gates"
    ]
    return {
        gate: {"status": "RESOLVED", "evidence_ids": ["E-GATE"]}
        for gate in gates
    }


def test_sector_profile_version_set_and_new_values_are_exact() -> None:
    config = sector_profiles_config()

    assert config["metadata"]["version"] == "1.1.0"
    assert config["metadata"]["effective_date"] == "2026-09-02"
    assert tuple(config["profiles"]) == (
        "coated_steel",
        "technical_plastics",
        "pharma_api",
        "fertilizers",
        "fabricated_aluminium",
    )
    for profile_name, expected in EXPECTED_NEW_PROFILES.items():
        profile = config["profiles"][profile_name]
        assert profile["label"] == expected["label"]
        assert tuple(profile["weights"]) == DIMENSIONS
        assert tuple(profile["weights"].values()) == expected["weights"]
        assert tuple(profile["hard_gates"]) == expected["hard_gates"]


@pytest.mark.parametrize(
    "profile_name",
    (
        "coated_steel",
        "technical_plastics",
        "pharma_api",
        "fertilizers",
        "fabricated_aluminium",
    ),
)
def test_every_profile_has_nine_ordered_weights_summing_to_one(
    profile_name: str,
) -> None:
    profile = sector_profiles_config()["profiles"][profile_name]

    assert tuple(profile["weights"]) == DIMENSIONS
    assert sum(profile["weights"].values()) == pytest.approx(1.0)
    assert profile["hard_gates"]


@pytest.mark.parametrize("profile_name", tuple(K70_SUBSETS))
def test_each_profile_has_an_exact_k70_known_dimension_subset(
    profile_name: str,
) -> None:
    states = {
        dimension: (
            0 if dimension in K70_SUBSETS[profile_name] else "U"
        )
        for dimension in DIMENSIONS
    }
    result = evaluate_capability(
        profile_name,
        states,
        _resolved_gates(profile_name),
    )

    assert result["known_weight_coverage"] == pytest.approx(0.70)
    assert result["route_publishable"] is True


@pytest.mark.parametrize("profile_name", tuple(K70_SUBSETS))
@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        (0.6999, False),
        (0.7000, True),
        (0.7001, True),
    ],
)
def test_publication_boundary_applies_to_every_profile(
    profile_name: str,
    coverage: float,
    expected: bool,
) -> None:
    del profile_name
    minimum = float(
        thresholds_config()["capability"][
            "minimum_known_weight_coverage"
        ]
    )

    assert publication_allowed(
        d_star=0.1,
        known_weight_coverage=coverage,
        minimum_known_weight_coverage=minimum,
        unresolved_hard_gates=[],
        has_known_hard_gate_failure=False,
    ) is expected


@pytest.mark.parametrize("profile_name", tuple(K70_SUBSETS))
@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        (0.1999, "immediate_adjacency"),
        (0.2000, "immediate_adjacency"),
        (0.2001, "incremental_upgrade"),
        (0.3999, "incremental_upgrade"),
        (0.4000, "incremental_upgrade"),
        (0.4001, "major_line_or_jv"),
        (0.6499, "major_line_or_jv"),
        (0.6500, "major_line_or_jv"),
        (0.6501, "greenfield_likely"),
    ],
)
def test_route_band_boundaries_apply_to_every_profile(
    profile_name: str,
    distance: float,
    expected: str,
) -> None:
    del profile_name
    bands = thresholds_config()["capability"]["route_bands"]

    assert route_band(distance, bands)["code"] == expected


@pytest.mark.parametrize("profile_name", tuple(K70_SUBSETS))
def test_profile_gate_missing_resolved_and_known_failure_behaviors(
    profile_name: str,
) -> None:
    states = {dimension: 0 for dimension in DIMENSIONS}
    gates = _resolved_gates(profile_name)

    passing = evaluate_capability(profile_name, states, gates)
    assert passing["route_publishable"] is True

    missing = deepcopy(gates)
    removed = next(iter(missing))
    del missing[removed]
    blocked_missing = evaluate_capability(
        profile_name,
        states,
        missing,
    )
    assert blocked_missing["route_publishable"] is False
    assert blocked_missing["unresolved_profile_hard_gates"] == [
        removed
    ]

    failed = deepcopy(gates)
    failed[removed] = {
        "status": "KNOWN_FAILURE",
        "evidence_ids": ["E-GATE"],
    }
    blocked_failure = evaluate_capability(
        profile_name,
        states,
        failed,
    )
    assert blocked_failure["route_publishable"] is False
    assert blocked_failure["known_hard_gate_failures"] == [removed]


@pytest.mark.parametrize("profile_name", tuple(K70_SUBSETS))
def test_non_hard_dimension_state_three_contributes_without_blocking(
    profile_name: str,
) -> None:
    states = {dimension: 0 for dimension in DIMENSIONS}
    states["skills_market_integration"] = 3

    result = evaluate_capability(
        profile_name,
        states,
        _resolved_gates(profile_name),
    )

    assert result["internal_d_star_before_gate"] > 0
    assert result["route_publishable"] is True
    assert result["known_hard_gate_failures"] == []


def test_unknown_profile_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown sector profile"):
        evaluate_capability(
            "unknown_profile",
            {dimension: 0 for dimension in DIMENSIONS},
            {},
        )
