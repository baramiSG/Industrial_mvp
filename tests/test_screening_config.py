"""Screening configuration contracts."""

from __future__ import annotations

import copy

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT


def _module():
    from ior_mvp.screening import config

    config.screening_config.cache_clear()
    config.product_families_config.cache_clear()
    return config


def test_screening_config_loads_and_pins_versions():
    module = _module()
    assert module.screening_config()["metadata"]["version"] == "1.0.0"
    assert module.product_families_config()["metadata"]["version"] == "1.2.0"


def test_five_queue_ids_exact_and_vocabularies_closed():
    config = _module().screening_config()
    assert tuple(config["queues"]) == (
        "robust_public_finding",
        "incumbent_upgrade_investigation",
        "resilience_case",
        "likely_false_positive",
        "high_evsi_evidence_investigation",
    )
    assert set(config["vocabularies"]["dispositions"]) == {
        "CANDIDATE",
        "SCREENED_OUT",
        "NO_CANDIDATE",
    }


def test_invalid_config_fails_closed():
    module = _module()
    valid = module.screening_config()
    probes = []
    missing_queue = copy.deepcopy(valid)
    missing_queue["queues"].pop("resilience_case")
    probes.append(missing_queue)
    unknown_reason = copy.deepcopy(valid)
    unknown_reason["vocabularies"]["reason_codes"].append("UNKNOWN")
    probes.append(unknown_reason)
    non_integer = copy.deepcopy(valid)
    non_integer["queues"]["robust_public_finding"][
        "minimum_fired_material_signals"
    ] = 1.5
    probes.append(non_integer)
    non_positive = copy.deepcopy(valid)
    non_positive["budgets"]["screening_snapshot_total_max_bytes"] = 0
    probes.append(non_positive)
    for probe in probes:
        with pytest.raises(module.ScreeningConfigurationError):
            module.validate_screening_config(probe)


def test_product_families_membership_cited_or_unavailable():
    module = _module()
    families = module.product_families_config()["families"]
    governed_profiles = {
        "coated_steel",
        "technical_plastics",
        "pharma_api",
        "fertilizers",
        "fabricated_aluminium",
    }
    for family in families.values():
        assert family["sector_profile"] in governed_profiles
        if family["hs4_headings"]:
            assert family["basis"]
            assert family["status"] == "AVAILABLE"
        else:
            assert family["status"] == "MEMBERSHIP_UNAVAILABLE"

    for invalid_profile in ("metals", "other"):
        invalid = copy.deepcopy(module.product_families_config())
        invalid["families"]["coated_steel"]["sector_profile"] = invalid_profile
        with pytest.raises(
            module.ScreeningConfigurationError, match="invalid sector profile"
        ):
            module.validate_product_families(invalid)


def test_sharded_screening_budgets_are_pinned():
    budgets = _module().screening_config()["budgets"]
    assert budgets == {
        "max_governed_file_bytes": 50_331_648,
        "screening_snapshot_total_max_bytes": 104_857_600,
    }


def test_family_lookup_by_hs4_prefix_unique_or_unavailable():
    module = _module()
    families = module.product_families_config()
    assert module.family_for_hs6("721049", families)["family_id"] == "coated_steel"
    assert (
        module.family_for_hs6("390210", families)["family_id"]
        == "polypropylene_primary_forms"
    )
    assert module.family_for_hs6("300001", families) is None


def test_product_families_version_pinned_to_1_2_0():
    assert _module().product_families_config()["metadata"]["version"] == "1.2.0"


def test_fabricated_aluminium_core_headings_available_with_pr1_basis():
    family = _module().product_families_config()["families"][
        "fabricated_aluminium"
    ]
    assert family["hs4_headings"] == [
        "7604",
        "7605",
        "7606",
        "7607",
        "7608",
        "7609",
        "7610",
        "7611",
        "7612",
        "7613",
        "7614",
        "7616",
    ]
    assert family["status"] == "AVAILABLE"
    assert "PR-1" in family["basis"]
    assert "76.15" in family["basis"]
    assert "76.01–76.03" in family["basis"]


def test_technical_plastics_conversion_headings_3917_3920_3921_available_with_od3_basis():
    family = _module().product_families_config()["families"][
        "technical_plastics_conversion"
    ]
    assert family["hs4_headings"] == ["3917", "3920", "3921"]
    assert family["status"] == "AVAILABLE"
    assert family["sector_profile"] == "technical_plastics"
    assert "OD-3" in family["basis"]
    assert (
        "Polymer/additive compatibility; conversion route; tooling; "
        "barrier/performance; food, medical or automotive qualification"
        in family["basis"]
    )


def test_polypropylene_primary_forms_unchanged_3902_only():
    family = _module().product_families_config()["families"][
        "polypropylene_primary_forms"
    ]
    assert family == {
        "sector_profile": "technical_plastics",
        "hs4_headings": ["3902"],
        "status": "AVAILABLE",
        "basis": "Methodology §14 worked case and frozen public opportunity",
    }


def test_pharma_api_core_headings_available_with_confirmed_basis():
    family = _module().product_families_config()["families"]["pharma_api"]
    assert family["hs4_headings"] == [
        "2933",
        "2934",
        "2935",
        "2936",
        "2937",
        "2939",
        "2941",
    ]
    assert family["status"] == "AVAILABLE"
    assert "Owner confirmation 2026-09-13" in family["basis"]
    assert "3002/3003/3004" in family["basis"]
    assert "excluded by owner scope" in family["basis"]
    assert "TITLE_VERIFICATION:" in family["basis"]


def test_fertilizers_core_headings_available_with_confirmed_basis():
    family = _module().product_families_config()["families"]["fertilizers"]
    assert family["hs4_headings"] == ["3102", "3103", "3104", "3105"]
    assert family["status"] == "AVAILABLE"
    assert "Owner confirmation 2026-09-13" in family["basis"]
    assert "3101" in family["basis"]
    assert "excluded by owner scope" in family["basis"]
    for feedstock in ("2814", "2809", "2510", "2503"):
        assert feedstock in family["basis"]
    assert "TITLE_VERIFICATION:" in family["basis"]


def test_other_families_byte_unchanged_from_1_1_0():
    retained = yaml.safe_load(
        (
            PROJECT_ROOT
            / "config"
            / "history"
            / "product_families.v1-1.1.0.yaml"
        ).read_text(encoding="utf-8")
    )
    live = _module().product_families_config()
    for family_id in (
        "coated_steel",
        "polypropylene_primary_forms",
        "technical_plastics_conversion",
        "fabricated_aluminium",
    ):
        assert live["families"][family_id] == retained["families"][family_id]


def test_family_for_hs6_294110_is_pharma_api_310430_is_fertilizers_300410_and_310100_are_none():
    module = _module()
    families = module.product_families_config()
    assert module.family_for_hs6("294110", families)["family_id"] == "pharma_api"
    assert module.family_for_hs6("310430", families)["family_id"] == "fertilizers"
    assert module.family_for_hs6("300410", families) is None
    assert module.family_for_hs6("310100", families) is None


def test_family_for_hs6_760429_is_fabricated_aluminium_and_761510_is_none():
    module = _module()
    families = module.product_families_config()
    assert module.family_for_hs6("760429", families)["family_id"] == (
        "fabricated_aluminium"
    )
    assert module.family_for_hs6("761510", families) is None


def test_family_for_hs6_392190_is_technical_plastics_conversion_and_390220_is_primary():
    module = _module()
    families = module.product_families_config()
    assert module.family_for_hs6("392190", families)["family_id"] == (
        "technical_plastics_conversion"
    )
    assert module.family_for_hs6("390220", families)["family_id"] == (
        "polypropylene_primary_forms"
    )
    assert module.family_for_hs6("391740", families)["sector_profile"] == (
        "technical_plastics"
    )
    assert module.family_for_hs6("390000", families) is None


def test_family_basis_titles_verified_against_stored_wco_record_or_flagged():
    family = _module().product_families_config()["families"][
        "technical_plastics_conversion"
    ]
    basis = family["basis"]
    assert "WCO HS 2022 Chapter 39" in basis
    assert "TITLE_VERIFICATION: " in basis
