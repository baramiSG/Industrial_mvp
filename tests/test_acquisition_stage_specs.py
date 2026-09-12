"""S11 stage vocabulary and serialized unit compatibility."""

import pytest
from dataclasses import replace

from ior_mvp.acquisition import contracts
from ior_mvp.acquisition.contracts import AcquisitionConfigurationError, ProductScope, QueryContract, Stage, canonical_dumps, unit_key
from ior_mvp.acquisition.coverage import _unit_dict
from ior_mvp.acquisition.pipeline import plan_units


@pytest.mark.parametrize("stage,scope,codes,periods,want_key", [
    (Stage.UNIVERSE, ProductScope.ALL_HS6, ("ALL",), ("2024",), ("imports", "2024")),
    (Stage.PARTNERS, ProductScope.EXPLICIT, ("721049",), ("2024",), ("721049", "imports", "2024")),
    (Stage.TARIFF, ProductScope.ALL_TARIFF_LINES, ("ALL",), (), ("ALL_TARIFF_LINES",)),
    (Stage.TERMS, ProductScope.NOT_APPLICABLE, (), (), ("TERMS",)),
    (Stage.BULK, ProductScope.NOT_APPLICABLE, (), ("2024",), ("2024",)),
])
def test_stage_spec_preserves_serialized_unit(stage, scope, codes, periods, want_key):
    assert hasattr(contracts, "STAGE_SPECS"), "stage behavior registry is missing"
    contract = QueryContract("TEST-FIXTURE", stage, "SAU", "WLD", "imports", scope, codes, "H0", periods)
    assert set(contracts.STAGE_SPECS) == set(Stage)
    assert unit_key(contract) == want_key
    assert canonical_dumps(_unit_dict(contract)) == canonical_dumps({
        "stage": stage.value, "flow": "imports", "period": "2024" if periods else None,
        "product_scope": scope.value, "hs6": "721049" if stage == Stage.PARTNERS else None,
    })


def test_unknown_stage_fails_closed_at_contract_and_planning():
    with pytest.raises(AcquisitionConfigurationError):
        QueryContract("TEST-FIXTURE", "UNKNOWN", "SAU", "WLD", "imports", ProductScope.NOT_APPLICABLE, (), "H0", ())
    with pytest.raises(AcquisitionConfigurationError):
        plan_units("UNKNOWN", source_id="test", years=(), flows=(), candidates=None, config={"sources": {"test": {}}})


@pytest.mark.parametrize("name", ["AGGREGATE", "DIRECTORY", "REGISTRY"])
def test_institutional_named_units_plan_and_round_trip(name):
    assert name in Stage.__members__, "institutional stage missing"
    stage = Stage(name)
    config = {"sources": {"TEST-FIXTURE": {
        "reporter_code": "SAU", "nomenclature": "TEST-CLASSIFICATION",
        "parameters": {"units": [{"dataset_id": "same", "indicator_id": "x:y"}, {"catalogue": "same"}]},
    }}}
    units = plan_units(stage, source_id="TEST-FIXTURE", years=(2024,), flows=("imports", "exports"), candidates=None, config=config)
    assert len(units) == 2
    first, second = units
    assert first.reporter == "SAU"
    assert first.partner == first.flow == "UNAVAILABLE"
    assert first.periods == (("2024",) if name == "AGGREGATE" else ())
    assert first.product_scope == ProductScope.NOT_APPLICABLE and first.product_codes == ()
    assert _unit_dict(first) == {"stage": name, "period": "2024" if name == "AGGREGATE" else None, "parameters": {"dataset_id": "same", "indicator_id": "x:y"}}
    assert unit_key(first) != unit_key(second)
    reversed_first = replace(first, parameters=tuple(reversed(first.parameters)))
    assert unit_key(first) == unit_key(reversed_first)
    assert first.canonical_json() == reversed_first.canonical_json()
    for parameters in [(), (("a", "1"), ("a", "2")), (("period", "2024"),), (("page", "1"),), (("reporter", "SAU"),)]:
        with pytest.raises(AcquisitionConfigurationError):
            replace(first, parameters=parameters)
    with pytest.raises(AcquisitionConfigurationError):
        replace(first, periods=() if name == "AGGREGATE" else ("2024",))
    with pytest.raises(AcquisitionConfigurationError):
        replace(first, product_scope=ProductScope.EXPLICIT, product_codes=("721049",))
    for change in ({"reporter": "USA"}, {"partner": "WLD"}, {"flow": "imports"}):
        with pytest.raises(AcquisitionConfigurationError):
            replace(first, **change)
    config["sources"]["TEST-FIXTURE"]["parameters"]["units"] = "UNAVAILABLE"
    unavailable = plan_units(stage, source_id="TEST-FIXTURE", years=(2024,), flows=(), candidates=None, config=config)
    assert len(unavailable) == 1 and unavailable[0].parameters == (("unit", "UNAVAILABLE"),)


def test_named_identity_encoding_cannot_collide():
    assert "DIRECTORY" in Stage.__members__
    def contract(parameters):
        return QueryContract("TEST-FIXTURE", Stage.DIRECTORY, "SAU", "UNAVAILABLE", "UNAVAILABLE", ProductScope.NOT_APPLICABLE, (), "TEST", (), parameters)
    parameters = [(("a", "same"),), (("b", "same"),), (("a", "b:c"),), (("a:b", "c"),), (("a", '["b", "c"]'),), (("a", "b"), ("c", "d"))]
    assert len({unit_key(contract(p)) for p in parameters}) == len(parameters)


@pytest.mark.parametrize("units", [[{"dataset_id": "TEST-dataset"}], "UNAVAILABLE"])
def test_aggregate_empty_years_refused_instead_of_silent_no_units(units):
    config = {"sources": {"TEST-FIXTURE": {
        "reporter_code": "SAU", "nomenclature": "TEST", "parameters": {"units": units},
    }}}
    with pytest.raises(AcquisitionConfigurationError):
        plan_units(Stage.AGGREGATE, source_id="TEST-FIXTURE", years=(), flows=(), candidates=None, config=config)


def test_connector_row_interface_includes_all_five_governed_row_types():
    from typing import get_args, get_type_hints
    from ior_mvp.acquisition.connectors.base import BaseConnector, SourceConnector

    assert hasattr(contracts, "Row"), "governed Row alias missing"
    expected = {contracts.TradeObservation, contracts.TariffLine, contracts.ProductionObservation,
                contracts.DirectoryRow, contracts.RegistryRow}
    assert set(get_args(contracts.Row)) == expected
    for connector in (SourceConnector, BaseConnector):
        assert get_type_hints(connector.normalize)["return"] == list[contracts.Row]
