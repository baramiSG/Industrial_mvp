"""Fresh acquisition classifications and URL preflight, with real raw storage."""

import json
from dataclasses import replace

import pytest

from ior_mvp.acquisition.connectors.base import BaseConnector, ConnectorRegistry, RequestBudget
from ior_mvp.acquisition.connectors.wits_trade import WitsTradeConnector
from ior_mvp.acquisition.connectors.un_comtrade import UnComtradeConnector
from ior_mvp.acquisition.connectors.zatca_tariff import ZatcaTariffConnector
from ior_mvp.acquisition.contracts import ProductScope, QueryContract, Stage, UnavailableReason
from ior_mvp.acquisition.snapshots import build_universe_snapshot, reconstruct, write_snapshot
from ior_mvp.acquisition.transport import FetchResult
from tests.acquisition_doubles import FakeTransport
from tests.test_acquisition_snapshots import _config_with_test_source, _temp_store, _fixture


def setup_acquire(tmp_path, *, payload=None, connector_class=WitsTradeConnector, stage=Stage.UNIVERSE):
    config = _config_with_test_source("wits_trade")
    cfg = dict(config["sources"]["wits_trade"])
    cfg.update(endpoint_templates={stage.value: "https://example.test/data", "TERMS": "https://example.test/terms"}, terms_reference="https://example.test/terms", license_capture_required=False)
    config["sources"]["wits_trade"] = cfg
    body = payload if payload is not None else json.dumps({"dataset": {"data": json.loads(_fixture("test_double_trade_rows.json"))["rows"]}}).encode()
    result = FetchResult(200, (("content-type", "application/json"),), body, "https://example.test/data", "2026-09-04T00:00:00Z", len(body))
    transport = FakeTransport({"https://example.test/data": result, "https://example.test/terms": result}, [])
    store = _temp_store(tmp_path)
    connector = connector_class(source_config=cfg, store=store, transport=transport, run_id="20260904T120000Z", environ={}, sleeper=lambda _: None)
    contract = QueryContract("wits_trade", stage, "SAU", "WLD", "imports", ProductScope.NOT_APPLICABLE if stage == Stage.TERMS else ProductScope.ALL_HS6, () if stage == Stage.TERMS else ("ALL",), "H0", ("2024",))
    return config, store, connector, contract, transport


@pytest.mark.parametrize("cls,payload,stage,status,reason", [
    (WitsTradeConnector, None, Stage.UNIVERSE, "NORMALIZED", None),
    (WitsTradeConnector, b"{}", Stage.UNIVERSE, "UNPARSED", "no_rows_parsed"),
    (BaseConnector, b"{}", Stage.UNIVERSE, "PENDING", None),
    (WitsTradeConnector, None, Stage.TERMS, "UNPARSED", "no_rows_parsed"),
])
def test_fresh_acquire_persists_classification(tmp_path, cls, payload, stage, status, reason):
    _, store, connector, contract, _ = setup_acquire(tmp_path, payload=payload, connector_class=cls, stage=stage)
    artifacts, coverage = connector.acquire(contract, max_requests=1)
    page = store.pages_for("wits_trade", coverage.query_hash, coverage.run_id)[0]
    assert page.normalization_status == status
    assert page.normalization_reason == reason


def test_fresh_acquire_build_write_reconstruct(tmp_path):
    config, store, connector, contract, transport = setup_acquire(tmp_path)
    connector.acquire(contract, max_requests=1)
    registry = ConnectorRegistry({"wits_trade": WitsTradeConnector})
    record = build_universe_snapshot(store, config, registry, source_id="wits_trade")
    path = write_snapshot(record, tmp_path)
    assert reconstruct(path, store, config, registry).match
    assert record["rows"] and transport.calls == ["https://example.test/data"]


@pytest.mark.parametrize("template", ["https://example.test/{missing}", "https://example.test/{reporter}", "https://example.test/{", "https://example.test/{}"])
def test_initial_bad_template_refuses_before_terms_or_budget(tmp_path, template):
    _, store, connector, contract, transport = setup_acquire(tmp_path)
    connector.source_config["endpoint_templates"]["UNIVERSE"] = template
    connector.source_config["parameters"] = {**connector.source_config["parameters"], "reporter_token": "UNAVAILABLE"}
    connector.source_config["license_capture_required"] = True
    connector.request_budget = RequestBudget(2)
    result = connector.acquire(contract, max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert connector.request_budget.used == 0
    assert transport.calls == []
    assert store.pages_for("wits_trade", contract.query_hash(), connector.run_id) == []


@pytest.mark.parametrize("change", [
    {"flow": "UNAVAILABLE"}, {"flow": ""}, {"periods": ("UNAVAILABLE",)}, {"periods": ("",)},
    {"parameters": (("flow", "override"),)}, {"parameters": (("custom", "a"), ("custom", "b"))},
])
def test_unobserved_identity_and_reserved_parameters_refused_without_interpolation(tmp_path, change):
    _, _, connector, contract, transport = setup_acquire(tmp_path)
    connector.source_config["license_capture_required"] = True
    connector.request_budget = RequestBudget(2)
    result = connector.acquire(replace(contract, **change), max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert connector.request_budget.used == 0
    assert transport.calls == [] and transport.request_headers == []


@pytest.mark.parametrize("cls,payload", [
    (UnComtradeConnector, b'{"data":[{"period":2024,"flowCode":"M","cmdCode":"721049","primaryValue":100}]}'),
    (ZatcaTariffConnector, b'[{"national_code":"721049000000","hs6":"721049"}]'),
])
def test_other_existing_parsers_expose_classification(tmp_path, cls, payload):
    _, _, connector, _, _ = setup_acquire(tmp_path, connector_class=cls)
    assert connector.classify_page(payload, "application/json", Stage.UNIVERSE) == ("NORMALIZED", None)
    assert connector.classify_page(b"{}", "application/json", Stage.UNIVERSE) == ("UNPARSED", "no_rows_parsed")


def test_unobserved_mapping_tokens_do_not_crash_or_guess(tmp_path):
    _, _, connector, contract, transport = setup_acquire(tmp_path)
    connector.source_config["parameters"] = {**connector.source_config["parameters"], "flow_tokens": "UNAVAILABLE"}
    connector.source_config["pagination"] = {"kind": "NEXT_TOKEN", "parameters": "UNAVAILABLE"}
    assert connector._extract_next_token(b'{"next":"should-not-be-guessed"}') is None
    connector.acquire(contract, max_requests=1)
    assert transport.calls == ["https://example.test/data"]
    assert transport.request_headers == [{}]


def test_unobserved_continuation_token_never_consumes_second_request(tmp_path):
    from tests.acquisition_doubles import DoubleConnector
    payload = b'{"pages_expected":2,"next_page_token_present":true,"next":"UNAVAILABLE"}'
    _, _, connector, contract, transport = setup_acquire(tmp_path, connector_class=DoubleConnector, payload=payload)
    connector.source_config["endpoint_templates"]["UNIVERSE"] = "https://example.test/data{page_token}"
    connector.source_config["pagination"] = {"kind": "NEXT_TOKEN", "parameters": {"next_token_field": "next"}}
    connector.request_budget = RequestBudget(2)
    result = connector.acquire(contract, max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert result.coverage.status == "INCOMPLETE"
    assert connector.request_budget.used == 1
    assert transport.calls == ["https://example.test/data"]


def test_generic_parameter_token_is_rendered_and_unavailable_is_refused(tmp_path):
    _, _, connector, contract, transport = setup_acquire(tmp_path)
    template = "https://example.test/{unit}"
    assert connector._build_url(replace(contract, parameters=(("unit", "observed"),)), template) == "https://example.test/observed"
    connector.source_config["endpoint_templates"]["UNIVERSE"] = template
    result = connector.acquire(replace(contract, parameters=(("unit", "UNAVAILABLE"),)), max_requests=1)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert connector.request_budget.used == 0 and transport.calls == []


@pytest.mark.parametrize("payload", [b'{"data":null}', b'{"data":[{"period":"bad"}]}'])
def test_malformed_comtrade_payload_remains_stored_unparsed(tmp_path, payload):
    _, store, connector, contract, transport = setup_acquire(tmp_path, connector_class=UnComtradeConnector, payload=payload)
    result = connector.acquire(contract, max_requests=1)
    page = store.pages_for("wits_trade", contract.query_hash(), connector.run_id)[0]
    assert page.normalization_status == "UNPARSED"
    assert page.normalization_reason == "no_rows_parsed"
    assert store.read_payload(page) == payload
    assert transport.calls == ["https://example.test/data"]


def test_s11_world_partner_url_uses_observed_source_token(tmp_path):
    _, _, connector, contract, _ = setup_acquire(tmp_path)
    connector.source_config["parameters"] = {**connector.source_config["parameters"], "partner_world_token": "0"}
    assert connector._build_url(contract, "https://example.test/{partner}") == "https://example.test/0"
    partner_contract = replace(contract, stage=Stage.PARTNERS, product_scope=ProductScope.EXPLICIT, product_codes=("721049",), partner="ALL")
    assert connector._build_url(partner_contract, "https://example.test/{partner}") == "https://example.test/ALL"


def test_zatca_html_parser_preserves_existing_attributes_and_normalization(tmp_path):
    from tests.acquisition_doubles import seed_unit
    payload = '<div data-code="721049000000" data-hs6="721049" data-desc-en="Steel" data-desc-ar="فولاذ"></div>'.encode()
    _, store, connector, contract, _ = setup_acquire(tmp_path, connector_class=ZatcaTariffConnector)
    assert connector.classify_page(payload, "text/html", Stage.TARIFF) == ("NORMALIZED", None)
    raw = seed_unit(store, contract=contract, run_id=connector.run_id, payload=payload, source_config=connector.source_config)
    lines = connector.normalize(raw)
    assert len(lines) == 1
    assert lines[0].national_code == "721049000000"
    assert lines[0].hs6 == "721049"
    assert lines[0].description_en == "Steel"
    assert lines[0].description_ar == "فولاذ"
