"""QueryContract and coverage record contract tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ior_mvp.acquisition.contracts import (
    AcquisitionConfigurationError,
    CompletenessBasis,
    CoverageRecord,
    ObservedResponse,
    ProductScope,
    QueryContract,
    SELECTION_RULE,
    SourceContractRecord,
    Stage,
    UnavailableReason,
    canonical_dumps,
    new_run_id,
    source_tag,
    unit_key,
)


def _universe_contract(**kwargs: object) -> QueryContract:
    defaults = {
        "source_id": "wits_trade",
        "stage": Stage.UNIVERSE,
        "reporter": "SAU",
        "partner": "WLD",
        "flow": "imports",
        "product_scope": ProductScope.ALL_HS6,
        "product_codes": ("ALL",),
        "nomenclature": "H0",
        "periods": ("2024",),
        "parameters": (("z", "1"), ("a", "2")),
    }
    defaults.update(kwargs)
    return QueryContract(**defaults)  # type: ignore[arg-type]


def test_query_hash_stable_across_parameter_order() -> None:
    c1 = _universe_contract(parameters=(("a", "2"), ("z", "1")))
    c2 = _universe_contract(parameters=(("z", "1"), ("a", "2")))
    assert c1.query_hash() == c2.query_hash()


def test_query_hash_differs_on_field_change() -> None:
    c1 = _universe_contract()
    c2 = _universe_contract(flow="exports")
    assert c1.query_hash() != c2.query_hash()


def test_post_init_invariants() -> None:
    with pytest.raises(AcquisitionConfigurationError):
        QueryContract(
            source_id="wits_trade",
            stage=Stage.PARTNERS,
            reporter="SAU",
            partner="WLD",
            flow="imports",
            product_scope=ProductScope.EXPLICIT,
            product_codes=("ALL",),
            nomenclature="H0",
            periods=("2024",),
        )
    with pytest.raises(AcquisitionConfigurationError):
        QueryContract(
            source_id="wits_trade",
            stage=Stage.PARTNERS,
            reporter="SAU",
            partner="WLD",
            flow="imports",
            product_scope=ProductScope.EXPLICIT,
            product_codes=("72104",),
            nomenclature="H0",
            periods=("2024",),
        )


def test_unit_key_per_stage() -> None:
    u = _universe_contract()
    assert unit_key(u) == ("imports", "2024")
    p = QueryContract(
        source_id="wits_trade",
        stage=Stage.PARTNERS,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.EXPLICIT,
        product_codes=("721049",),
        nomenclature="H0",
        periods=("2024",),
    )
    assert unit_key(p) == ("721049", "imports", "2024")
    t = QueryContract(
        source_id="zatca_tariff",
        stage=Stage.TARIFF,
        reporter="SAU",
        partner="WLD",
        flow="n/a",
        product_scope=ProductScope.ALL_TARIFF_LINES,
        product_codes=("ALL",),
        nomenclature="SA12",
        periods=("2024",),
    )
    assert unit_key(t) == ("ALL_TARIFF_LINES",)


def test_source_tags() -> None:
    assert source_tag("wits_trade") == "WITS-TRADE"
    assert source_tag("un_comtrade") == "UN-COMTRADE"
    assert source_tag("zatca_tariff") == "ZATCA-TARIFF"
    assert source_tag("baci_cepii") == "BACI-CEPII"


def test_canonical_dumps_trailing_newline() -> None:
    dumped = canonical_dumps({"b": 1, "a": 2})
    assert dumped.endswith("\n")
    assert '"a"' in dumped


def test_coverage_record_round_trip() -> None:
    record = CoverageRecord(
        source_id="wits_trade",
        stage=Stage.UNIVERSE,
        query_hash="abc",
        run_id="20260904T000000Z",
        unit_key=("imports", "2024"),
        unit={"stage": "UNIVERSE"},
        pages_fetched=1,
        pages_expected=1,
        requests_made=1,
        status="COMPLETE",
        completeness_basis=CompletenessBasis.SINGLE_RESPONSE_NO_PAGINATION,
        stop_reason=None,
        missing_pages=(),
        observed_stop=None,
    )
    restored = CoverageRecord.from_json(record.to_json())
    assert restored == record


def test_unavailable_reason_members() -> None:
    assert UnavailableReason.NO_UNITS_IN_STORE.value == "NO_UNITS_IN_STORE"


def test_new_run_id_format_and_order() -> None:
    early = new_run_id(datetime(2026, 9, 4, 0, 0, 0, tzinfo=UTC))
    late = new_run_id(datetime(2026, 9, 4, 1, 0, 0, tzinfo=UTC))
    assert early == "20260904T000000Z"
    assert early < late


def test_selection_rule_constant() -> None:
    assert SELECTION_RULE == "LATEST_RUN_PER_SOURCE_STAGE_UNIT"
