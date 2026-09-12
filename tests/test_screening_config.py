"""Screening configuration contracts."""

from __future__ import annotations

import copy

import pytest


def _module():
    from ior_mvp.screening import config

    config.screening_config.cache_clear()
    config.product_families_config.cache_clear()
    return config


def test_screening_config_loads_and_pins_version_1_0_0():
    module = _module()
    assert module.screening_config()["metadata"]["version"] == "1.0.0"
    assert module.product_families_config()["metadata"]["version"] == "1.0.0"


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
