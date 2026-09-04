"""Harmonisation invariant tests."""

from __future__ import annotations

from ior_mvp.acquisition.harmonise import trade_observation_from_row, unit_value_analysis_enabled
from ior_mvp.acquisition.contracts import TradeObservation


def test_unit_value_disabled_without_weight() -> None:
    obs = TradeObservation(
        year=2024,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        hs_revision="H0",
        hs6="721049",
        national_tariff_line=None,
        trade_value_original_text="1000",
        trade_value=1000.0,
        currency="USD",
        valuation="CIF",
        net_weight_original_text="",
        net_weight=None,
        weight_unit="kg",
        supplementary_quantity=None,
        supplementary_unit=None,
        estimation_flags=(),
        unit_value_analysis_enabled=False,
        gross_flow=True,
        reexport_status="UNAVAILABLE",
        source_evidence_id="test",
    )
    assert unit_value_analysis_enabled(obs) is False
