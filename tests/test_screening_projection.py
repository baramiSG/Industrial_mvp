"""Per-HS6 screening projection tests."""

from __future__ import annotations


def _row(year=2024, flow="imports", value=2_000_000, weight=4_000_000, **extra):
    return {
        "year": year,
        "flow": flow,
        "hs6": "721049",
        "trade_value": value,
        "net_weight": weight,
        "hs_revision": "H6",
        "source_evidence_id": "E1",
        **extra,
    }


def _project(universe=None, partners=None, capability=None):
    from ior_mvp.screening.projection import project_case

    return project_case(
        "721049",
        universe or [_row()],
        partners or [],
        {},
        capability,
    )


def test_usd_to_usd_m_and_kg_to_kt_conversions_exact():
    trade = _project()["trade"][0]
    assert trade["imports_usd_m"] == 2
    assert trade["imports_kt"] == 4
    assert trade["import_uv_usd_t"] == 500


def test_missing_net_weight_is_unavailable_not_zero():
    assert _project([_row(weight=None)])["trade"][0]["imports_kt"] == "UNAVAILABLE"


def test_exports_absent_is_unavailable():
    assert _project()["trade"][0]["exports_usd_m"] == "UNAVAILABLE"


def test_missing_years_and_quantity_comparable_flags():
    case = _project([_row(year=2021), _row(year=2023, weight=None)])
    assert case["trade_quality"]["missing_years"] == [2022]
    assert case["trade_quality"]["quantity_comparable"] is False


def test_world_row_excluded_from_partner_observations_and_recorded():
    case = _project(
        partners=[
            _row(partner="World", partner_code="0"),
            _row(partner="China", partner_code="156"),
        ]
    )
    assert [row["partner"] for row in case["partner_observations"]] == ["China"]
    assert case["projection_exclusions"] == ["PARTNER_WORLD_ROW"]


def test_hard_exclusion_inputs_shape_all_unavailable():
    blocks = _project()["hard_exclusion_inputs"]
    assert len(blocks) == 6
    assert all(
        value == "UNAVAILABLE"
        for block in blocks.values()
        for key, value in block.items()
        if key != "evidence_ids"
    )


def test_capability_shape_unavailable_without_family_link():
    capability = _project()["domestic_capability"]
    assert capability["same_process_family"] == "UNAVAILABLE"
    assert capability["verified_present"] == "UNAVAILABLE"


def test_capability_shape_with_link_yields_no_known_gate_failure_and_nothing_resolved():
    capability = _project(
        capability={
            "family_id": "coated_steel",
            "links": [
                {
                    "signal_type": "core_process",
                    "evidence_ids": ["LINK-1"],
                }
            ],
        }
    )["domestic_capability"]
    assert capability["same_process_family"] is True
    assert capability["verified_present"] is True
    assert capability["unresolved_hard_gates"] == []
    assert capability["profile_hard_gates"] == {}
