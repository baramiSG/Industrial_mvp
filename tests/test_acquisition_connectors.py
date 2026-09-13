"""Connector registry and acquire-path tests."""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import (
    BaseConnector,
    ConnectorRegistry,
    default_registry,
)
from ior_mvp.acquisition.connectors.un_comtrade import UnComtradeConnector
from ior_mvp.acquisition.contracts import (
    CompletenessBasis,
    ProductScope,
    QueryContract,
    RawArtifact,
    Stage,
    UnavailableReason,
    UnavailableRecord,
)
from ior_mvp.acquisition.pipeline import PipelineDeps, _run_units
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition import snapshots
from ior_mvp.acquisition.snapshots import build_universe_snapshot
from ior_mvp.acquisition.transport import FetchResult
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import (
    DoubleConnector,
    FakeTransport,
    comtrade_envelope,
    comtrade_row,
    seed_unit,
)


def test_default_registry_ids() -> None:
    reg = default_registry()
    assert reg.ids() == (
        "baci_cepii", "etimad_tenders", "gastat", "ministry_of_industry", "modon",
        "producer_advanced_petrochemical", "producer_altaiseer_talco",
        "producer_alupco", "producer_hadeed", "producer_maaden",
        "producer_sabic", "producer_sabic_agrinutrients", "producer_spimaco",
        "producer_tasnee", "producer_unicoil",
        "saber_registry", "saso_catalogue", "saso_documents", "sfda_registers",
        "tadawul_disclosures", "un_comtrade", "wco_hs_nomenclature", "wits_trade",
        "zatca_tariff",
    )


def test_snapshot_kinds_per_dd22() -> None:
    reg = default_registry()
    assert reg.snapshot_kinds("wits_trade") == frozenset({"universe", "partners"})
    assert reg.snapshot_kinds("zatca_tariff") == frozenset({"tariff"})
    assert reg.snapshot_kinds("baci_cepii") == frozenset()
    for source, kind in [("gastat", "production"), ("ministry_of_industry", "directory"), ("modon", "directory"), ("saso_catalogue", "registry"), ("saber_registry", "registry")]:
        assert reg.snapshot_kinds(source) == frozenset({kind})
    for source in (
        "tadawul_disclosures", "etimad_tenders", "saso_documents", "producer_unicoil",
        "producer_sabic", "producer_advanced_petrochemical", "producer_tasnee",
        "producer_hadeed", "producer_alupco", "producer_altaiseer_talco",
        "producer_maaden", "producer_spimaco", "producer_sabic_agrinutrients",
        "sfda_registers", "wco_hs_nomenclature",
    ):
        assert reg.snapshot_kinds(source) == frozenset({"document"})


def _test_store(tmp_path: Path) -> RawStore:
    raw_cfg = acquisition_sources_config()["raw_store"]
    return RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )


def _universe_contract(source_id: str = "TEST-PAGE") -> QueryContract:
    return QueryContract(
        source_id=source_id,
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )


def _paginated_source_config(source_id: str = "TEST-PAGE") -> dict:
    return {
        **acquisition_sources_config()["sources"]["wits_trade"],
        "source_id": source_id,
        "license_capture_required": False,
        "terms_reference": "UNAVAILABLE",
        "endpoint_templates": {
            "UNIVERSE": "http://fake.test/universe?page={page}",
            "TERMS": "UNAVAILABLE",
        },
        "pagination": {
            "kind": "PAGE_NUMBER",
            "documentation_reference": "test",
            "parameters": {},
        },
    }


def _fetch_result(body: bytes) -> FetchResult:
    return FetchResult(
        http_status=200,
        headers_subset=(("content-type", "application/json"),),
        body=body,
        final_url_redacted="http://fake.test/universe",
        fetched_at="2026-09-04T00:00:00Z",
        content_length_header=len(body),
    )


def _credential_source_config(
    source_id: str,
    *,
    custom_header: bool,
) -> dict:
    source = copy.deepcopy(
        acquisition_sources_config()["sources"]["wits_trade"]
    )
    source.update(
        {
            "source_id": source_id,
            "credential_env_var": "IOR_TEST_SUBSCRIPTION_KEY",
            "license_capture_required": False,
            "terms_reference": "UNAVAILABLE",
            "endpoint_templates": {
                "UNIVERSE": "http://fake.test/credential",
                "TERMS": "UNAVAILABLE",
            },
            "pagination": {
                "kind": "NONE",
                "documentation_reference": "TEST DOUBLE",
                "parameters": {},
            },
        }
    )
    if custom_header:
        source["credential_header"] = "Ocp-Apim-Subscription-Key"
    return source


def _stored_bytes(root: Path) -> bytes:
    chunks: list[bytes] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        content = path.read_bytes()
        chunks.append(content)
        if path.suffix == ".gz":
            chunks.append(gzip.decompress(content))
    return b"\n".join(chunks)


def test_custom_credential_header_sent_and_never_stored(
    tmp_path: Path,
) -> None:
    source_id = "TEST-CUSTOM-HEADER"
    source = _credential_source_config(source_id, custom_header=True)
    payload = b'{"pages_expected":1,"rows":[]}'
    transport = FakeTransport(
        responses={
            "http://fake.test/credential": _fetch_result(payload),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source,
        store=_test_store(tmp_path),
        transport=transport,
        run_id="20260912T120000Z",
        environ={
            "IOR_TEST_SUBSCRIPTION_KEY": "TEST-SENTINEL-NOT-A-SECRET"
        },
        sleeper=lambda _: None,
    )

    result = connector.acquire(
        _universe_contract(source_id),
        max_requests=1,
    )

    assert isinstance(result, tuple)
    assert transport.request_headers == [
        {
            "Ocp-Apim-Subscription-Key": (
                "TEST-SENTINEL-NOT-A-SECRET"
            )
        }
    ]
    assert "Authorization" not in transport.request_headers[0]
    stored = _stored_bytes(tmp_path / "raw")
    assert b"TEST-SENTINEL-NOT-A-SECRET" not in stored
    contract_path = next((tmp_path / "raw").rglob("page-0001.contract.json"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["credential_env_var"] == "IOR_TEST_SUBSCRIPTION_KEY"
    assert contract["credential_used"] is True
    assert "Ocp-Apim-Subscription-Key" not in contract_path.read_text(
        encoding="utf-8"
    )


def test_bearer_default_unchanged_for_wits_trade(tmp_path: Path) -> None:
    source_id = "TEST-BEARER-DEFAULT"
    source = _credential_source_config(source_id, custom_header=False)
    payload = b'{"pages_expected":1,"rows":[]}'
    transport = FakeTransport(
        responses={
            "http://fake.test/credential": _fetch_result(payload),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source,
        store=_test_store(tmp_path),
        transport=transport,
        run_id="20260912T120001Z",
        environ={"IOR_TEST_SUBSCRIPTION_KEY": "TEST-BEARER-SENTINEL"},
        sleeper=lambda _: None,
    )

    result = connector.acquire(
        _universe_contract(source_id),
        max_requests=1,
    )

    assert isinstance(result, tuple)
    assert transport.request_headers == [
        {"Authorization": "Bearer TEST-BEARER-SENTINEL"}
    ]
    assert b"TEST-BEARER-SENTINEL" not in _stored_bytes(
        tmp_path / "raw"
    )


def test_401_records_http_error_with_sanitized_observed_response(
    tmp_path: Path,
) -> None:
    source_id = "TEST-CUSTOM-401"
    source = _credential_source_config(source_id, custom_header=True)
    body = b'{"statusCode":401,"message":"Access denied"}'
    response = FetchResult(
        http_status=401,
        headers_subset=(("content-type", "application/json"),),
        body=body,
        final_url_redacted="http://fake.test/credential",
        fetched_at="2026-09-12T12:00:02Z",
        content_length_header=len(body),
    )
    transport = FakeTransport(
        responses={"http://fake.test/credential": response},
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source,
        store=_test_store(tmp_path),
        transport=transport,
        run_id="20260912T120002Z",
        environ={"IOR_TEST_SUBSCRIPTION_KEY": "TEST-401-SENTINEL"},
        sleeper=lambda _: None,
    )

    result = connector.acquire(
        _universe_contract(source_id),
        max_requests=1,
    )

    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.HTTP_ERROR
    assert result.observed_response is not None
    assert result.observed_response.http_status == 401
    assert result.observed_response.body_byte_count == len(body)
    assert result.observed_response.error_message_redacted == "HTTP 401"
    assert not list((tmp_path / "raw").rglob("page-*.payload.*.gz"))
    assert b"TEST-401-SENTINEL" not in _stored_bytes(tmp_path / "raw")


def _comtrade_source_config() -> dict:
    source = copy.deepcopy(
        acquisition_sources_config()["sources"]["un_comtrade"]
    )
    source.update(
        {
            "access_classification": "public_open",
            "credential_env_var": None,
            "license_capture_required": False,
            "terms_reference": "UNAVAILABLE",
            "endpoint_templates": {
                "UNIVERSE": "http://fake.test/comtrade-universe",
                "PARTNERS": "http://fake.test/comtrade-partners",
                "TERMS": "UNAVAILABLE",
            },
            "pagination": {
                "kind": "NONE",
                "documentation_reference": "TEST DOUBLE",
                "parameters": {},
            },
        }
    )
    source.pop("credential_header", None)
    return source


def _comtrade_contract(
    *,
    stage: Stage = Stage.UNIVERSE,
    hs6: str = "721049",
    flow: str = "imports",
    period: str = "2024",
) -> QueryContract:
    explicit = stage is Stage.PARTNERS
    return QueryContract(
        source_id="un_comtrade",
        stage=stage,
        reporter="SAU",
        partner="ALL" if explicit else "0",
        flow=flow,
        product_scope=(
            ProductScope.EXPLICIT
            if explicit
            else ProductScope.ALL_HS6
        ),
        product_codes=(hs6,) if explicit else ("ALL",),
        nomenclature="HS",
        periods=(period,),
    )


def _acquire_comtrade(
    tmp_path: Path,
    payload: bytes,
    *,
    contract: QueryContract | None = None,
    content_type: str = "application/json",
    source_config: dict | None = None,
    seed_universe: bool = True,
) -> tuple[UnComtradeConnector, object]:
    query = contract or _comtrade_contract()
    url = (
        "http://fake.test/comtrade-partners"
        if query.stage is Stage.PARTNERS
        else "http://fake.test/comtrade-universe"
    )
    response = FetchResult(
        http_status=200,
        headers_subset=(("content-type", content_type),),
        body=payload,
        final_url_redacted=url,
        fetched_at="2026-09-12T12:30:00Z",
        content_length_header=len(payload),
    )
    store = _test_store(tmp_path)
    source = source_config or _comtrade_source_config()
    if query.stage is Stage.PARTNERS and seed_universe:
        try:
            envelope = json.loads(payload.decode("utf-8"))
            rows = envelope.get("data", [])
            reference = next(
                (
                    row.get("primaryValue")
                    for row in rows
                    if str(row.get("partnerCode")) == "0"
                ),
                sum(
                    (
                        Decimal(str(row.get("primaryValue")))
                        for row in rows
                        if str(row.get("partnerCode")) != "0"
                        and row.get("primaryValue") is not None
                    ),
                    Decimal(0),
                ),
            )
            seed_unit(
                store,
                contract=_comtrade_contract(
                    hs6=query.product_codes[0],
                    flow=query.flow,
                    period=query.periods[0],
                ),
                run_id="20260912T120000Z",
                payload=comtrade_envelope(
                    [
                        comtrade_row(
                            query.product_codes[0],
                            primary_value=float(reference),
                        )
                    ]
                ),
                source_config=source,
            )
        except (AttributeError, StopIteration, TypeError, ValueError):
            pass
    connector = UnComtradeConnector(
        source_config=source,
        store=store,
        transport=FakeTransport(
            responses={url: response},
            calls=[],
        ),
        run_id="20260912T123000Z",
        environ={},
        sleeper=lambda _: None,
    )
    return connector, connector.acquire(query, max_requests=1)


def _stored_comtrade_artifact(
    connector: UnComtradeConnector, contract: QueryContract
) -> RawArtifact:
    pages = connector.store.pages_for(
        contract.source_id, contract.query_hash(), connector.run_id
    )
    assert len(pages) == 1
    return RawArtifact(
        contract=pages[0],
        path=PROJECT_ROOT / pages[0].raw_file_path,
    )


def test_un_comtrade_universe_single_response_complete_when_count_matches(
    tmp_path: Path,
) -> None:
    payload = comtrade_envelope(
        [comtrade_row("721049"), comtrade_row("390210")]
    )

    connector, result = _acquire_comtrade(tmp_path, payload)

    assert isinstance(result, tuple)
    artifacts, coverage = result
    assert coverage.status == "COMPLETE"
    assert (
        coverage.completeness_basis
        == CompletenessBasis.PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000
    )
    assert coverage.pages_expected == 1
    assert artifacts[0].contract.page_meta is not None
    assert artifacts[0].contract.page_meta.rows_in_page == 2
    assert connector.validate(artifacts[0]).status == "PASS"


def test_un_comtrade_count_mismatch_is_incomplete_indeterminate(
    tmp_path: Path,
) -> None:
    payload = comtrade_envelope([comtrade_row()], count=2)

    _, result = _acquire_comtrade(tmp_path, payload)

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert (
        result.coverage.stop_reason
        == UnavailableReason.COUNT_MISMATCH
    )
    assert result.coverage.pages_expected == "UNAVAILABLE"


def test_un_comtrade_documented_record_cap_is_incomplete_truncation_risk(
    tmp_path: Path,
) -> None:
    _, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope([comtrade_row()], count=100_000),
    )

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.stop_reason == UnavailableReason.RECORD_CAP_REACHED


@pytest.mark.parametrize(
    "rows,error,expected_reason",
    [
        ([comtrade_row()], {"code": "TEST_ERROR"}, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row(reporter_code=840)], None, UnavailableReason.REPORTER_MISMATCH),
        ([comtrade_row(period=2023)], None, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row(flow_code="X")], None, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row(partner_code=156)], None, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row("7210")], None, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row(classification_code="")], None, UnavailableReason.COVERAGE_INDETERMINATE),
        ([comtrade_row(), comtrade_row()], None, UnavailableReason.COVERAGE_INDETERMINATE),
    ],
)
def test_un_comtrade_each_completeness_predicate_fails_closed(
    tmp_path: Path,
    rows: list[dict],
    error: object,
    expected_reason: UnavailableReason,
) -> None:
    _, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(rows, error=error),
    )

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.completeness_basis == CompletenessBasis.UNAVAILABLE
    assert result.coverage.stop_reason == expected_reason


def test_un_comtrade_partners_use_same_count_and_cap_completeness(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    _, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(
            [comtrade_row(partner_code=156, partner_desc="China")]
        ),
        contract=contract,
    )

    assert isinstance(result, tuple)
    _, coverage = result
    assert coverage.status == "COMPLETE"
    assert (
        coverage.completeness_basis
        == CompletenessBasis.PROVIDER_COUNT_MATCH_BELOW_DOCUMENTED_CAP_100000
    )


def test_un_comtrade_stored_page_preserves_observed_response_when_coverage_indeterminate(
    tmp_path: Path,
) -> None:
    source = _comtrade_source_config()
    source["pagination"] = {
        "kind": "UNAVAILABLE",
        "documentation_reference": "UNAVAILABLE",
        "parameters": {},
    }

    _, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope([comtrade_row()]),
        source_config=source,
    )

    assert isinstance(result, UnavailableRecord)
    assert result.observed_response is not None
    assert result.observed_response.http_status == 200
    assert result.observed_response.body_byte_count > 0
    assert result.observed_response.error_type is None
    assert result.observed_response.error_message_redacted is None


def test_un_comtrade_error_envelope_is_incomplete(tmp_path: Path) -> None:
    payload = comtrade_envelope(
        [comtrade_row()],
        error={"code": "TEST_ERROR"},
    )

    _, result = _acquire_comtrade(tmp_path, payload)

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.pages_expected == "UNAVAILABLE"


def test_un_comtrade_html_landing_page_never_becomes_universe(
    tmp_path: Path,
) -> None:
    _, result = _acquire_comtrade(
        tmp_path,
        b"<html><body>TEST LANDING PAGE</body></html>",
        content_type="text/html",
    )

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.pages_expected == "UNAVAILABLE"


def test_un_comtrade_reporter_mismatch_fails_validation(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract()
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope([comtrade_row(reporter_code=840)]),
        contract=contract,
    )

    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.stop_reason == UnavailableReason.REPORTER_MISMATCH
    report = connector.validate(_stored_comtrade_artifact(connector, contract))
    assert report.status == "FAIL"
    assert next(
        check
        for check in report.checks
        if check.check_id == "reporter_682_all_rows"
    ).result == "FAIL"


def test_un_comtrade_mixed_classification_in_unit_fails_validation(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract()
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(
            [
                comtrade_row("721049", classification_code="H5"),
                comtrade_row("390210", classification_code="H6"),
            ]
        ),
        contract=contract,
    )

    assert isinstance(result, UnavailableRecord)
    report = connector.validate(_stored_comtrade_artifact(connector, contract))
    assert report.status == "FAIL"
    assert next(
        check
        for check in report.checks
        if check.check_id == "single_classification_code_per_unit"
    ).result == "FAIL"


def test_un_comtrade_duplicate_hs6_in_unit_fails_validation(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract()
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope([comtrade_row(), comtrade_row()]),
        contract=contract,
    )

    assert isinstance(result, UnavailableRecord)
    report = connector.validate(_stored_comtrade_artifact(connector, contract))
    assert report.status == "FAIL"
    assert next(
        check
        for check in report.checks
        if check.check_id == "no_duplicate_hs6_per_unit"
    ).result == "FAIL"


def test_universe_rows_carry_classification_code_verbatim(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(
            [comtrade_row(classification_code="H6")]
        ),
    )

    assert isinstance(result, tuple)
    artifact = result[0][0]
    parsed = connector.parse_rows(
        connector.store.read_payload(artifact.contract),
        artifact.contract.content_type,
    )
    observations = connector.normalize(artifact)
    assert [row["classification_code"] for row in parsed] == ["H6"]
    assert [row.hs_revision for row in observations] == ["H6"]


def test_un_comtrade_partner_rows_keep_partner_desc_and_world_row(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(
            [
                comtrade_row(primary_value=600_000),
                comtrade_row(
                    partner_code=156,
                    partner_desc="China",
                    primary_value=600_000,
                    net_weight=700_000,
                ),
            ]
        ),
        contract=contract,
    )

    assert isinstance(result, tuple)
    artifact = result[0][0]
    report = connector.validate(artifact)
    assert report.status == "PASS"
    assert next(
        check
        for check in report.checks
        if check.check_id == "partner_rows_unique_per_unit"
    ).result == "PASS"
    observations = connector.normalize(artifact)
    assert [row.partner for row in observations] == ["World", "China"]


def test_un_comtrade_partners_validate_uses_partner_pair_uniqueness_and_single_valued_secondary_dimensions(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    rows = [
        comtrade_row(partner_code=156, partner_desc="China"),
        comtrade_row(partner_code=840, partner_desc="United States"),
    ]
    rows[0].update({"partner2Code": 0, "motCode": 0, "customsCode": "C00"})
    rows[1].update({"partner2Code": 1, "motCode": 0, "customsCode": "C00"})
    connector, result = _acquire_comtrade(
        tmp_path, comtrade_envelope(rows), contract=contract
    )
    assert isinstance(result, UnavailableRecord)
    report = connector.validate(_stored_comtrade_artifact(connector, contract))
    checks = {check.check_id: check.result for check in report.checks}
    assert checks["partner_rows_unique_per_unit"] == "PASS"
    assert checks["secondary_dimensions_single_valued"] == "FAIL"

    rows[1]["partner2Code"] = 0
    connector, result = _acquire_comtrade(
        tmp_path / "single", comtrade_envelope(rows), contract=contract
    )
    assert isinstance(result, tuple)
    report = connector.validate(result[0][0])
    checks = {check.check_id: check.result for check in report.checks}
    assert checks["partner_rows_unique_per_unit"] == "PASS"
    assert checks["secondary_dimensions_single_valued"] == "PASS"
    assert checks["partner_desc_present_for_non_world_rows"] == "PASS"


def test_un_comtrade_partners_zero_row_envelope_is_complete_normalized_empty_not_format_not_parseable(
    tmp_path: Path,
) -> None:
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    connector, result = _acquire_comtrade(
        tmp_path, comtrade_envelope([]), contract=contract
    )
    assert isinstance(result, tuple)
    artifacts, coverage = result
    assert coverage.status == "COMPLETE"
    assert coverage.stop_reason is None
    assert artifacts[0].contract.normalization_status == "NORMALIZED_EMPTY"
    assert (
        artifacts[0].contract.normalization_reason
        == "zero_rows_provider_count_0"
    )
    assert connector.validate(artifacts[0]).status == "PASS"


@pytest.mark.parametrize(
    "rows,error",
    [
        ([comtrade_row()], None),
        (
            [comtrade_row(partner_code=156, partner_desc="China")],
            {"code": "TEST_ERROR"},
        ),
    ],
)
def test_un_comtrade_partners_only_world_rows_or_error_envelope_is_incomplete_coverage_indeterminate(
    tmp_path: Path,
    rows: list[dict],
    error: object,
) -> None:
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    _, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(rows, error=error),
        contract=contract,
    )
    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.stop_reason == UnavailableReason.COVERAGE_INDETERMINATE


def _acquire_reconciled_partner_payload(
    tmp_path: Path,
    payload: bytes,
    *,
    universe_value: str = "10.000",
) -> tuple[UnComtradeConnector, object]:
    store = _test_store(tmp_path)
    source = _comtrade_source_config()
    universe = (
        '{"count":1,"data":[{"period":2024,"flowCode":"M",'
        '"reporterCode":682,"partnerCode":0,"cmdCode":"721049",'
        '"classificationCode":"H6","primaryValue":'
        + universe_value
        + '}],"error":null}'
    ).encode()
    seed_unit(
        store,
        contract=_comtrade_contract(),
        run_id="20260912T120000Z",
        payload=universe,
        source_config=source,
    )
    response = FetchResult(
        http_status=200,
        headers_subset=(("content-type", "application/json"),),
        body=payload,
        final_url_redacted="http://fake.test/comtrade-partners",
        fetched_at="2026-09-12T12:30:00Z",
        content_length_header=len(payload),
    )
    connector = UnComtradeConnector(
        source_config=source,
        store=store,
        transport=FakeTransport(
            responses={"http://fake.test/comtrade-partners": response},
            calls=[],
        ),
        run_id="20260912T123000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = _comtrade_contract(stage=Stage.PARTNERS)
    return connector, connector.acquire(contract, max_requests=1)


def _partner_payload(
    values: tuple[str, str] = ("4.999", "5.001"),
    *,
    descs: tuple[str | None, str | None] = ("China", "Korea"),
    world: str = "10.000",
) -> bytes:
    def desc(value: str | None) -> str:
        return "null" if value is None else json.dumps(value)

    return (
        '{"count":3,"data":['
        '{"period":2024,"flowCode":"M","reporterCode":682,'
        '"partnerCode":0,"partnerDesc":"World","cmdCode":"721049",'
        '"classificationCode":"H6","primaryValue":'
        + world
        + '},'
        '{"period":2024,"flowCode":"M","reporterCode":682,'
        '"partnerCode":156,"partnerDesc":'
        + desc(descs[0])
        + ',"cmdCode":"721049","classificationCode":"H6","primaryValue":'
        + values[0]
        + '},'
        '{"period":2024,"flowCode":"M","reporterCode":682,'
        '"partnerCode":410,"partnerDesc":'
        + desc(descs[1])
        + ',"cmdCode":"721049","classificationCode":"H6","primaryValue":'
        + values[1]
        + '}],"error":null}'
    ).encode()


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (("4.999", "5.001"), "PASS"),
        (("4.999", "5.002"), "PASS"),
        (("4.999", "5.003"), "FAIL"),
    ],
)
def test_un_comtrade_partners_aggregate_reconciles_uses_decimal_sum_and_stored_scale_tolerance(
    tmp_path: Path,
    values: tuple[str, str],
    expected: str,
) -> None:
    connector, result = _acquire_reconciled_partner_payload(
        tmp_path, _partner_payload(values)
    )
    artifact = (
        result[0][0]
        if isinstance(result, tuple)
        else _stored_comtrade_artifact(
            connector, _comtrade_contract(stage=Stage.PARTNERS)
        )
    )
    check = next(
        row
        for row in connector.validate(artifact).checks
        if row.check_id == "aggregate_reconciles"
    )
    assert check.result == expected
    assert all(token in check.detail for token in ("S=", "R=", "diff=", "s=3", "tolerance=0.001"))


def test_un_comtrade_partners_aggregate_reconciles_missing_reference_fails(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_comtrade(
        tmp_path,
        _partner_payload(),
        contract=_comtrade_contract(stage=Stage.PARTNERS),
        seed_universe=False,
    )
    assert isinstance(result, UnavailableRecord)
    report = connector.validate(
        _stored_comtrade_artifact(
            connector, _comtrade_contract(stage=Stage.PARTNERS)
        )
    )
    check = next(row for row in report.checks if row.check_id == "aggregate_reconciles")
    assert check.result == "FAIL"
    assert "reference unavailable" in check.detail


def test_un_comtrade_partners_zero_envelope_fails_aggregate_reconciles_when_reference_positive(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_reconciled_partner_payload(
        tmp_path, comtrade_envelope([])
    )
    assert isinstance(result, UnavailableRecord)
    assert result.coverage is not None
    assert result.coverage.stop_reason == UnavailableReason.COVERAGE_INDETERMINATE


def test_un_comtrade_partners_world_row_must_match_reference_within_half_unit(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_reconciled_partner_payload(
        tmp_path, _partner_payload(world="10.001")
    )
    assert isinstance(result, UnavailableRecord)
    report = connector.validate(
        _stored_comtrade_artifact(
            connector, _comtrade_contract(stage=Stage.PARTNERS)
        )
    )
    assert next(
        row for row in report.checks if row.check_id == "aggregate_reconciles"
    ).result == "FAIL"


def test_un_comtrade_partners_duplicate_partner_desc_fails_unique_check(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_reconciled_partner_payload(
        tmp_path, _partner_payload(descs=("Same", "Same"))
    )
    assert isinstance(result, UnavailableRecord)
    report = connector.validate(
        _stored_comtrade_artifact(
            connector, _comtrade_contract(stage=Stage.PARTNERS)
        )
    )
    assert next(
        row
        for row in report.checks
        if row.check_id == "partner_desc_unique_for_non_world_rows"
    ).result == "FAIL"


def test_un_comtrade_partners_only_missing_descriptions_maps_to_typed_reason(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_reconciled_partner_payload(
        tmp_path, _partner_payload(descs=(None, None))
    )
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.PARTNER_DESCRIPTIONS_UNAVAILABLE
    report = connector.validate(
        _stored_comtrade_artifact(
            connector, _comtrade_contract(stage=Stage.PARTNERS)
        )
    )
    assert {
        row.check_id for row in report.checks if row.result == "FAIL"
    } == {"partner_desc_present_for_non_world_rows"}


def test_stored_v1_coverage_bytes_are_unchanged() -> None:
    path = PROJECT_ROOT / (
        "data/raw/un_comtrade/"
        "e71395bbc925e4fbb59435020937df3035c9470aae1e9fc44a5b5bc4026df184/"
        "20260913T010452Z/coverage.json"
    )
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "faa48dee5d066d9f26e6df4ec8f5973ed87ad672b5c728e62e6a429608351dc4"
    )


def test_un_comtrade_universe_validation_unchanged_by_partners_mapping(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_comtrade(
        tmp_path, comtrade_envelope([comtrade_row()])
    )
    assert isinstance(result, tuple)
    report = connector.validate(result[0][0])
    assert report.status == "PASS"
    assert [check.check_id for check in report.checks] == [
        "content_type_json",
        "envelope_shape",
        "no_error_field",
        "count_matches_rows",
        "rows_present",
        "reporter_682_all_rows",
        "period_matches_contract",
        "flow_matches_contract",
        "partner_matches_stage",
        "cmd_code_hs6_all_rows",
        "single_classification_code_per_unit",
        "no_duplicate_hs6_per_unit",
    ]


def test_universe_snapshot_records_config_version_1_3_0(
    tmp_path: Path,
) -> None:
    connector, result = _acquire_comtrade(
        tmp_path,
        comtrade_envelope(
            [
                comtrade_row("721049", classification_code="H6"),
                comtrade_row("390210", classification_code="H6"),
            ]
        ),
    )
    assert isinstance(result, tuple)
    config = copy.deepcopy(acquisition_sources_config())
    config["sources"]["un_comtrade"] = connector.source_config

    record = build_universe_snapshot(
        connector.store,
        config,
        default_registry(),
        source_id="un_comtrade",
    )

    assert record["transformation_record"]["config_version"] == "1.3.0"
    assert all(
        passport["transformation_record"]["config_version"] == "1.3.0"
        for passport in record["evidence"]
    )


def test_partners_kind_config_version_unchanged_and_wits_snapshot_reconstructs(
) -> None:
    config = acquisition_sources_config()
    kinds = snapshots.default_kind_registry()
    assert kinds.get("partners").config_version == "1.0.0"
    raw_cfg = config["raw_store"]
    store = RawStore(
        PROJECT_ROOT / "data" / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    path = (
        PROJECT_ROOT
        / "data"
        / "snapshots"
        / "partners"
        / "PARTNERS-SAU-WITS-TRADE-2026-09-03.json"
    )
    assert snapshots.reconstruct_pinned(
        path,
        store,
        config,
        default_registry(),
    ).match


def test_acquire_credential_absent_records_unavailable(tmp_path: Path) -> None:
    config = acquisition_sources_config()
    store = _test_store(tmp_path)
    source_cfg = config["sources"]["un_comtrade"]
    connector = UnComtradeConnector(
        source_config=source_cfg,
        store=store,
        transport=FakeTransport(responses={}, calls=[]),
        run_id="20260904T120000Z",
        environ={},
    )
    contract = QueryContract(
        source_id="un_comtrade",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="HS2017",
        periods=("2024",),
    )
    result = connector.acquire(contract, max_requests=5)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.CREDENTIAL_ABSENT
    assert (tmp_path / "raw" / "un_comtrade").exists()


def test_acquire_endpoint_unverified_records_unavailable(tmp_path: Path) -> None:
    store = _test_store(tmp_path)
    source_cfg = {
        **_paginated_source_config("TEST-UNVERIFIED"),
        "parameters": {
            **acquisition_sources_config()["sources"]["wits_trade"]["parameters"],
            "product_all_token": "UNAVAILABLE",
        },
    }
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=FakeTransport(responses={}, calls=[]),
        run_id="20260904T120000Z",
        environ={},
    )
    result = connector.acquire(_universe_contract("TEST-UNVERIFIED"), max_requests=5)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED


def test_fake_transport_max_requests_one_stops_after_page_one(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    store = _test_store(tmp_path)
    source_id = "TEST-PAGE"
    source_cfg = _paginated_source_config(source_id)
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={},
    )
    contract = _universe_contract(source_id)
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.MAX_REQUESTS_EXHAUSTED
    assert result.coverage is not None
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.pages_fetched == 1
    assert len(transport.calls) == 1
    registry = ConnectorRegistry({source_id: DoubleConnector})
    config = acquisition_sources_config()
    config = {
        **config,
        "sources": {**config["sources"], source_id: source_cfg},
    }
    with pytest.raises(Exception):
        build_universe_snapshot(store, config, registry, source_id=source_id)


def test_fake_transport_two_page_complete_write(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    store = _test_store(tmp_path)
    source_id = "TEST-PAGE"
    source_cfg = _paginated_source_config(source_id)
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={},
    )
    result = connector.acquire(_universe_contract(source_id), max_requests=2)
    assert isinstance(result, tuple)
    artifacts, coverage = result
    assert coverage.status == "COMPLETE"
    assert len(artifacts) == 2
    assert len(transport.calls) == 2


def test_multi_unit_budget_exhaustion_never_attempted_coverage(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import ConnectorRegistry

    source_id = "TEST-BUDGET"
    source_cfg = _paginated_source_config(source_id)
    config = acquisition_sources_config()
    config = {
        **config,
        "sources": {**config["sources"], source_id: source_cfg},
    }
    store = _test_store(tmp_path)
    registry = ConnectorRegistry({source_id: DoubleConnector})
    page1 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page1_of_2.json"
    ).read_bytes()
    page2 = (
        PROJECT_ROOT / "tests" / "fixtures" / "acquisition" / "test_double_trade_page2_of_2.json"
    ).read_bytes()
    transport = FakeTransport(
        responses={
            "http://fake.test/universe?page=1": _fetch_result(page1),
            "http://fake.test/universe?page=2": _fetch_result(page2),
        },
        calls=[],
    )
    units = (
        _universe_contract(source_id),
        QueryContract(
            source_id=source_id,
            stage=Stage.UNIVERSE,
            reporter="SAU",
            partner="WLD",
            flow="exports",
            product_scope=ProductScope.ALL_HS6,
            product_codes=("ALL",),
            nomenclature="H0",
            periods=("2024",),
        ),
    )
    deps = PipelineDeps(
        config=config,
        store=store,
        transport=transport,
        registry=registry,
        run_id="20260904T130000Z",
        environ={},
        sleeper=lambda _: None,
    )
    report = _run_units(
        deps,
        source_id=source_id,
        stage=Stage.UNIVERSE,
        units=units,
        max_requests=2,
    )
    assert report.exit_code == 3
    exports_hash = units[1].query_hash()
    cov_path = (
        tmp_path
        / "raw"
        / source_id
        / exports_hash
        / "20260904T130000Z"
        / "coverage.json"
    )
    assert cov_path.exists()
    cov = json.loads(cov_path.read_text(encoding="utf-8"))
    assert cov["pages_fetched"] == 0
    assert cov["status"] == "INCOMPLETE"
