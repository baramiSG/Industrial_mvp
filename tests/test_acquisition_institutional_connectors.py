"""Actual connector boundaries, using Class D transport doubles and real storage."""

import json
import re
from dataclasses import replace

import pytest

from ior_mvp.acquisition import snapshots
from ior_mvp.acquisition.connectors.base import BaseConnector, ConnectorRegistry, default_registry
from ior_mvp.acquisition.contracts import AcquisitionUnavailable, PageMeta, Stage, UNAVAILABLE, UnavailableRecord, UnavailableReason, sha256_bytes
from ior_mvp.acquisition.coverage import evaluate_coverage
from ior_mvp.acquisition.pipeline import plan_units
from ior_mvp.acquisition.transport import FetchResult, NetworkError
from tests.acquisition_doubles import FakeTransport, institutional_config, pre_observation_source_config
from tests.test_acquisition_snapshots import _fixture, _temp_store

CASES = [("gastat", Stage.AGGREGATE, "production"), ("ministry_of_industry", Stage.DIRECTORY, "directory"), ("modon", Stage.DIRECTORY, "directory"), ("saso_catalogue", Stage.REGISTRY, "registry"), ("saber_registry", Stage.REGISTRY, "registry")]
PRIVACY_SOURCES = CASES[1:]


class InstitutionalParserMixin:
    """Only test code knows this explicitly fake envelope; validators stay real."""

    def parse_rows(self, payload, content_type):
        mime = content_type.split(";", 1)[0].strip().casefold()
        if mime not in {"application/json", "text/json"} and not re.fullmatch(r"application/[^/\s]+\+json", mime):
            return []
        try:
            data = json.loads(payload.decode("utf-8-sig"))
        except (UnicodeError, ValueError):
            return []
        if not isinstance(data, dict) or data.get("_test_fixture") is not True:
            return []
        return data.get("rows", [])

    def page_meta(self, payload, content_type):
        try:
            data = json.loads(payload.decode("utf-8-sig"))
        except (UnicodeError, ValueError):
            return super().page_meta(payload, content_type)
        if not isinstance(data, dict) or data.get("_test_fixture") is not True:
            return super().page_meta(payload, content_type)
        return PageMeta(data.get("page_index", 1), data.get("pages_expected", UNAVAILABLE), data.get("next_page_token_present", False), len(data.get("rows", [])), None)


def payload_for(source, kind):
    payload = _fixture(f"test_double_{kind}_rows.json")
    return payload.replace(b"saso_catalogue", b"saber_registry") if source == "saber_registry" else payload


def setup(tmp_path, source="modon", stage=Stage.DIRECTORY, kind="directory", *, payload=None, mime="application/json", config=None, environ=None, status=200):
    config = config or institutional_config(source, stage)
    cfg = config["sources"][source]
    contract = plan_units(stage, source_id=source, years=(2024,), flows=(), candidates=None, config=config)[0]
    body = payload_for(source, kind) if payload is None else payload
    headers = () if mime is None else (("content-type", mime),)
    response = FetchResult(status, headers, body, "https://example.test/data?page=1", "2026-09-04T00:00:00Z", len(body))
    transport = FakeTransport({"https://example.test/data?page=1": response}, [])
    store = _temp_store(tmp_path)
    registry = default_registry()
    # Before registration, exercise the existing boundary to obtain behavioral RED.
    actual_cls = type(registry.get(source, source_config=cfg, store=store, transport=transport, run_id="unused", environ={})) if source in registry.ids() else BaseConnector
    connector_cls = type("TestParsedInstitutionalConnector", (InstitutionalParserMixin, actual_cls), {}) if source in registry.ids() else BaseConnector
    connector = connector_cls(source_config=cfg, store=store, transport=transport, run_id="20260904T120000Z", environ=environ or {}, sleeper=lambda _: None)
    return config, store, connector, contract, transport


def pages(store, contract, connector):
    return store.pages_for(contract.source_id, contract.query_hash(), connector.run_id)


def assert_attempt(store, contract, connector, result, reason, requests=0):
    assert isinstance(result, UnavailableRecord)
    assert result.reason == reason
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.requests_made == requests
    directory = store.root / contract.source_id / contract.query_hash() / connector.run_id
    attempt = json.loads((directory / "attempt.json").read_text())
    assert attempt["coverage"] == json.loads((directory / "coverage.json").read_text())
    return attempt


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_institutional_registry_parser_and_fresh_acquire_reconstruction(tmp_path, source, stage, kind):
    config, store, connector, contract, transport = setup(tmp_path, source, stage, kind)
    assert source in default_registry().ids()
    assert connector.snapshot_kinds == frozenset({kind})
    payload = payload_for(source, kind)
    assert connector.parse_rows(payload, "application/json") == json.loads(payload)["rows"]
    assert connector.parse_rows(b'{"unknown":[]}', "application/json") == []
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple) and result[1].status == "COMPLETE"
    assert pages(store, contract, connector)[0].normalization_status == "NORMALIZED"
    registry = ConnectorRegistry({source: type(connector)})
    record = snapshots.build_row_snapshot(store, config, registry, source_id=source, kind=kind)
    assert record["quality_summary"] == "PASS" and record["rows"]
    assert all(p["evidence_class"] == "D" for p in record["evidence"])
    path = snapshots.write_snapshot(record, tmp_path, allow_test_double=True)
    assert snapshots.reconstruct(path, store, config, registry).match
    assert transport.calls == ["https://example.test/data?page=1"]


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_pre_observation_source_yields_endpoint_unverified_with_null_credential(tmp_path, source, stage, kind):
    cfg = pre_observation_source_config(source, stage=stage, authority="TEST authority")
    config = {"sources": {source: cfg}, "metadata": {"version": "1.1.0"}}
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind, config=config, environ={UNAVAILABLE: "canary"})
    result = connector.acquire(contract, max_requests=2)
    attempt = assert_attempt(store, contract, connector, result, UnavailableReason.ENDPOINT_UNVERIFIED)
    assert attempt["credential_env_var"] is None and attempt["credential_present"] is False
    assert result.coverage.stop_reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert not pages(store, contract, connector) and not transport.calls


@pytest.mark.parametrize("source,stage,kind", CASES)
@pytest.mark.parametrize("template", [UNAVAILABLE, "https://example.test/{missing}", "https://example.test/{reporter}", "https://example.test/{flow_code}"])
def test_unverified_endpoint_tokens_precede_terms_and_budget(tmp_path, source, stage, kind, template):
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind)
    cfg = connector.source_config
    cfg["endpoint_templates"][stage.value] = template
    cfg["parameters"]["reporter_token"] = UNAVAILABLE
    cfg["parameters"]["flow_tokens"] = UNAVAILABLE
    cfg["license_capture_required"] = True
    result = connector.acquire(contract, max_requests=2)
    assert_attempt(store, contract, connector, result, UnavailableReason.ENDPOINT_UNVERIFIED)
    assert not transport.calls and connector.request_budget.used == 0


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_observed_template_unobserved_access_yields_license_unrecorded(tmp_path, source, stage, kind):
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind)
    connector.source_config.update(access_classification=UNAVAILABLE, credential_env_var=UNAVAILABLE)
    result = connector.acquire(contract, max_requests=2)
    attempt = assert_attempt(store, contract, connector, result, UnavailableReason.LICENSE_UNRECORDED)
    assert attempt["credential_env_var"] is None
    assert not pages(store, contract, connector) and not transport.calls


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_sentinel_credential_never_sent_or_stored(tmp_path, source, stage, kind):
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind, environ={UNAVAILABLE: "canary"})
    connector.source_config["credential_env_var"] = UNAVAILABLE
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    page = pages(store, contract, connector)[0]
    assert transport.request_headers == [{}]
    assert page.credential_env_var is None and page.credential_used is False


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_observed_credential_name_absent_records_credential_absent(tmp_path, source, stage, kind):
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind)
    connector.source_config["credential_env_var"] = "IOR_TEST_SOURCE_KEY"
    result = connector.acquire(contract, max_requests=1)
    attempt = assert_attempt(store, contract, connector, result, UnavailableReason.CREDENTIAL_ABSENT)
    assert attempt["observed_response"] is None and attempt["credential_present"] is False
    assert not pages(store, contract, connector) and not transport.calls


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_sentinel_mappings_never_dereferenced(tmp_path, source, stage, kind):
    payload = json.loads(payload_for(source, kind))
    payload.update(pages_expected=2, next_page_token_present=True, next="unobserved-field")
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind, payload=json.dumps(payload).encode())
    connector.source_config["parameters"]["flow_tokens"] = UNAVAILABLE
    connector.source_config["pagination"] = {"kind": "NEXT_TOKEN", "parameters": UNAVAILABLE}
    result = connector.acquire(contract, max_requests=3)
    assert len(transport.calls) == 1 and len(pages(store, contract, connector)) == 1
    assert isinstance(result, UnavailableRecord) and result.coverage.status == "INCOMPLETE"


@pytest.mark.parametrize("source,stage,kind", CASES)
@pytest.mark.parametrize("status,reason", [(403, "HTTP_ERROR"), (404, "HTTP_ERROR"), (503, "HTTP_ERROR"), (429, "RATE_LIMITED")])
def test_http_failures_record_observed_hash(tmp_path, source, stage, kind, status, reason):
    body = b'{"email":"DO-NOT-STORE"}'
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind, payload=body, status=status)
    result = connector.acquire(contract, max_requests=1)
    assert result.reason.value == reason and result.observed_response.http_status == status
    assert result.observed_response.body_sha256 == sha256_bytes(body)
    assert result.observed_response.headers_subset == (("content-type", "application/json"),)
    assert result.observed_response.error_type == "HTTPError"
    assert not pages(store, contract, connector) and len(transport.calls) == 1


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_network_error_and_terms_capture_failure(tmp_path, source, stage, kind):
    _, store, connector, contract, transport = setup(tmp_path, source, stage, kind)
    transport.responses["https://example.test/data?page=1"] = NetworkError("TLS certificate verification failed (TEST double)")
    result = connector.acquire(contract, max_requests=1)
    assert result.reason == UnavailableReason.NETWORK_ERROR
    assert result.observed_response.error_type == "NetworkError"
    assert result.observed_response.error_message_redacted == "TLS certificate verification failed (TEST double)"
    assert not pages(store, contract, connector)
    connector.run_id = "20260905T120000Z"
    connector.source_config["license_capture_required"] = True
    transport.responses["https://example.test/terms"] = NetworkError("TLS test failure")
    result = connector.acquire(contract, max_requests=2)
    assert result.reason == UnavailableReason.LICENSE_UNRECORDED


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_unavailable_page_total_is_incomplete(tmp_path, source, stage, kind):
    body = json.loads(payload_for(source, kind))
    body["pages_expected"] = UNAVAILABLE
    _, store, connector, contract, _ = setup(tmp_path, source, stage, kind, payload=json.dumps(body).encode())
    connector.source_config["pagination"]["kind"] = "NONE"
    result = connector.acquire(contract, max_requests=1)
    assert result.coverage.status == "INCOMPLETE"
    assert result.coverage.stop_reason == UnavailableReason.COVERAGE_INDETERMINATE
    assert len(pages(store, contract, connector)) == 1


def privacy_acquire(tmp_path, body, mime="application/json", *, source="modon", stage=Stage.DIRECTORY, kind="directory"):
    config, store, connector, contract, transport = setup(tmp_path, source, stage, kind, payload=body, mime=mime)
    connector.source_config["pagination"]["kind"] = "NONE"
    result = connector.acquire(contract, max_requests=1)
    return result, store, connector, contract, transport


def assert_refused(tmp_path, body, mime="application/json", *, error="PersonalDataFields", **source_args):
    result, store, connector, contract, transport = privacy_acquire(tmp_path, body, mime, **source_args)
    attempt = assert_attempt(store, contract, connector, result, UnavailableReason.OUT_OF_SCOPE_CONTENT, requests=1)
    assert result.coverage.stop_reason == UnavailableReason.OUT_OF_SCOPE_CONTENT
    assert result.coverage.observed_stop == result.observed_response
    assert result.observed_response.error_type == error
    assert result.observed_response.body_sha256 == sha256_bytes(body)
    assert result.observed_response.body_byte_count == len(body)
    assert result.observed_response.http_status == 200
    assert not pages(store, contract, connector) and len(transport.calls) == 1
    assert not list(store.root.rglob("*.gz"))
    return attempt


@pytest.mark.parametrize("source,stage,kind", PRIVACY_SOURCES)
@pytest.mark.parametrize("body", [b"\xff", b"PK\x03\x04\x00binary", b"text\x00value"])
def test_directory_page_unassessable_shape_refused(tmp_path, source, stage, kind, body):
    assert_refused(tmp_path, body, "application/octet-stream", error="UninspectableTextPayload", source=source, stage=stage, kind=kind)


@pytest.mark.parametrize("body,mime", [(b"unknown text", "text/plain"), (b'{"unknown": []}', "application/json"), (b"{broken", "application/json")])
def test_directory_unknown_decodable_shape_stored_unparsed(tmp_path, body, mime):
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body, mime)
    page = pages(store, contract, connector)[0]
    assert (page.normalization_status, page.normalization_reason) == ("UNPARSED", "no_rows_parsed")
    assert store.read_payload(page) == body


@pytest.mark.parametrize("label", [
    "phone", "phone_number", "phone_no", "telephone", "telephone_number", "telephone_no",
    "mobile", "mobile_number", "mobile_no", "email", "email_address", "e_mail", "e_mail_address",
    "contact_person", "contact_person_name", "contact_name", "person_name", "national_id", "national_id_number", "national_id_no",
    "هاتف", "الهاتف", "رقم الهاتف", "جوال", "الجوال", "رقم الجوال", "البريد الإلكتروني", "البريد الالكتروني",
    "بريد إلكتروني", "بريد الكتروني", "اسم شخص الاتصال", "اسم مسؤول التواصل", "الهوية الوطنية", "رقم الهوية الوطنية",
    "department.phone_number_en", "contactPersonName", "nationalIDNumber", "URLPhoneNumber",
])
@pytest.mark.parametrize("envelope", ["json", "csv", "tsv", "html"])
def test_privacy_field_patterns_json_csv_tsv_html(tmp_path, label, envelope):
    bodies = {"json": json.dumps({"nested": [{label: None}]}), "csv": '\n"' + label + '",organization\n,TEST', "tsv": '\n"' + label + '"\torganization\n\tTEST', "html": '<table><th>' + label + '</th></table>'}
    types = {"json": "application/json", "csv": "text/csv", "tsv": "text/tab-separated-values", "html": "text/html"}
    assert_refused(tmp_path, bodies[envelope].encode(), types[envelope])


@pytest.mark.parametrize("label", ["entity_name_ar", "organization", "issued_to_text", "contactID", "contactIDNumber", "xphone", "telephonebook", "phone_numbering", "اسم_الشركة", "x_رقم_الهاتف", "رقم_الهاتف_ar"])
def test_privacy_allows_organization_fields_and_nonmatching_boundaries(tmp_path, label):
    body = json.dumps({label: "TEST"}).encode()
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body)
    assert store.read_payload(pages(store, contract, connector)[0]) == body


@pytest.mark.parametrize("body,mime", [(b'{"organization":"email phone person_name"}', "application/json"), (b'<p>phone email</p><a name="email">phone</a><script>email</script><style>phone</style>', "text/html"), (b'organization\nemail', "text/csv")])
def test_privacy_does_not_classify_values_or_free_prose(tmp_path, body, mime):
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body, mime)
    assert store.read_payload(pages(store, contract, connector)[0]) == body


def test_privacy_refusal_records_hash_only_and_preserves_prior_pages(tmp_path):
    first = json.loads(payload_for("modon", "directory"))
    first["pages_expected"] = 2
    _, store, connector, contract, transport = setup(tmp_path, payload=json.dumps(first).encode())
    body = b'{"phone":"PRIVATE-CANARY","pages_expected":2}'
    transport.responses["https://example.test/data?page=2"] = FetchResult(200, (("content-type", "application/json"),), body, "https://example.test/data?page=2", "2026-09-04T00:00:00Z", len(body))
    result = connector.acquire(contract, max_requests=2)
    assert_attempt(store, contract, connector, result, UnavailableReason.OUT_OF_SCOPE_CONTENT, requests=2)
    assert result.coverage.pages_fetched == 1
    assert len(pages(store, contract, connector)) == 1
    assert store.read_payload(pages(store, contract, connector)[0]) == json.dumps(first).encode()
    assert result.observed_response.error_type == "PersonalDataFields"
    assert all(b"PRIVATE-CANARY" not in path.read_bytes() for path in store.root.rglob("*") if path.is_file())


def test_privacy_guard_leaves_s11_and_terms_behavior_unchanged(tmp_path):
    from tests.test_acquisition_normalization_status import setup_acquire
    for index, stage in enumerate([Stage.UNIVERSE, Stage.TERMS]):
        _, store, connector, contract, _ = setup_acquire(tmp_path / str(index), payload=b'{"phone":null}', stage=stage)
        connector.acquire(contract, max_requests=1)
        assert len(pages(store, contract, connector)) == 1
    _, store, connector, contract, transport = setup(tmp_path / "institutional-terms")
    connector.source_config["license_capture_required"] = True
    transport.responses["https://example.test/terms"] = FetchResult(200, (("content-type", "application/pdf"),), b'\xff\x00phone', "https://example.test/terms", "2026-09-04T00:00:00Z", 7)
    connector.acquire(contract, max_requests=2)
    assert len(store.iter_contracts(stage="TERMS")) == 1


def test_unknown_shape_offline_parser_fresh_acquire_reconstruct_preserves_first_run(tmp_path):
    body = json.dumps({"offline_rows": json.loads(payload_for("modon", "directory"))["rows"], "pages_expected": 1}).encode()
    config, store, connector, contract, _ = setup(tmp_path, payload=body)
    connector.source_config["pagination"]["kind"] = "NONE"
    connector.acquire(contract, max_requests=1)
    first_page = pages(store, contract, connector)[0]
    assert first_page.normalization_status == "UNPARSED"
    before = {p: p.read_bytes() for p in store.root.rglob("*") if p.is_file()}
    class OfflineParser(type(connector)):
        def parse_rows(self, payload, content_type):
            return json.loads(payload)["offline_rows"]
    registry = ConnectorRegistry({"modon": OfflineParser})
    with pytest.raises(AcquisitionUnavailable) as refused:
        snapshots.build_row_snapshot(store, config, registry, source_id="modon", kind="directory")
    assert refused.value.reason == UnavailableReason.FORMAT_NOT_PARSEABLE
    fresh = OfflineParser(source_config=connector.source_config, store=store, transport=connector.transport, run_id="20260905T120000Z", environ={}, sleeper=lambda _: None)
    fresh.acquire(contract, max_requests=1)
    assert pages(store, contract, fresh)[0].normalization_status == "NORMALIZED"
    record = snapshots.build_row_snapshot(store, config, registry, source_id="modon", kind="directory")
    path = snapshots.write_snapshot(record, tmp_path, allow_test_double=True)
    assert snapshots.reconstruct(path, store, config, registry).match
    assert all(p.read_bytes() == content for p, content in before.items())


@pytest.mark.parametrize("body,mime,refused", [(b'{"email":null}', "text/csv", False), (b'email,value\n,TEST', "application/json", False), (b'<input name="email">', "application/json", False), (b'{"email":null}', "application/problem+json", True), (b'{"email":null}', "Application/JSON; charset=latin1", True), (b'{"email":null}', "application/+json", False), (b'{"email":null}', "application/a/b+json", False), (b'{"email":null}', "application/a b+json", False), (b'{"email":null}', "text/json", True)])
def test_declared_mime_selects_exactly_one_envelope(tmp_path, body, mime, refused):
    if refused:
        assert_refused(tmp_path, body, mime)
    else:
        _, store, connector, contract, _ = privacy_acquire(tmp_path, body, mime)
        assert pages(store, contract, connector)[0].normalization_status == "UNPARSED"


def test_routing_uses_response_content_type_not_expected_content_types(tmp_path):
    _, store, connector, contract, _ = setup(tmp_path, payload=b'{"email":null}', mime="text/plain")
    connector.source_config["expected_content_types"] = ["application/json"]
    connector.acquire(contract, max_requests=1)
    assert pages(store, contract, connector)[0].normalization_status == "UNPARSED"


@pytest.mark.parametrize("tag", ["input", "select", "textarea", "button"])
def test_html_field_extraction_uses_only_named_controls(tmp_path, tag):
    assert_refused(tmp_path / "name", f'<{tag} name="email"></{tag}>'.encode(), "text/html")
    body = f'<{tag} id="email" placeholder="phone" title="person_name">email</{tag}><script><th>email</th></script><style><th>phone</th></style>'.encode()
    _, store, connector, contract, _ = privacy_acquire(tmp_path / "attributes", body, "application/xhtml+xml")
    assert len(pages(store, contract, connector)) == 1


@pytest.mark.parametrize("mime", ["application/pdf", "application/zip", "application/gzip", "image/png", "audio/test", "video/test", "font/woff"])
def test_declared_binary_mime_refuses_clean_text_bytes(tmp_path, mime):
    assert_refused(tmp_path, b"%PDF-1.4 clean text", mime, error="UninspectableTextPayload")


@pytest.mark.parametrize("mime", [None, "", "application/octet-stream", "application/unknown", "text/plain"])
def test_unknown_missing_empty_octet_stream_are_opaque_unparsed(tmp_path, mime):
    body = b'{"email":null}'
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body, mime)
    assert pages(store, contract, connector)[0].normalization_status == "UNPARSED"
    assert store.read_payload(pages(store, contract, connector)[0]) == body


def test_utf8_bom_is_accepted_and_raw_bytes_preserved(tmp_path):
    body = b"\xef\xbb\xbf" + payload_for("modon", "directory")
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body)
    page = pages(store, contract, connector)[0]
    assert page.normalization_status == "NORMALIZED" and store.read_payload(page) == body
    assert_refused(tmp_path / "private", b'\xef\xbb\xbf{"email":null}')


@pytest.mark.parametrize("body", [b"\xff", b"valid\x00utf8", b"valid\x7futf8", b"valid\x0butf8"])
def test_control_character_refusal_is_distinct_from_decode_failure(tmp_path, body):
    if body != b"\xff":
        body.decode("utf-8")  # Controls are valid UTF-8: this is a distinct refusal path.
    assert_refused(tmp_path, body, "text/plain", error="UninspectableTextPayload")


@pytest.mark.parametrize("label,refused", [("contactID", False), ("contactIDNumber", False), ("nationalIDNumber", True), ("URLPhoneNumber", True), ("company/email_address_text", True), ("رقم_الهاتف", True), ("قسم_رقم_الهاتف", False), ("رقم_الهاتف_en", False)])
def test_acronym_and_language_matching_boundaries(tmp_path, label, refused):
    body = json.dumps({label: None}).encode()
    if refused:
        assert_refused(tmp_path, body)
    else:
        _, store, connector, contract, _ = privacy_acquire(tmp_path, body)
        assert len(pages(store, contract, connector)) == 1


@pytest.mark.parametrize("pagination", ["NONE", "PAGE_NUMBER", "NEXT_TOKEN", "INDEX_ENUMERATION"])
def test_refused_unit_is_incomplete_with_reason_and_error_type(tmp_path, pagination):
    _, store, connector, contract, _ = setup(tmp_path)
    connector.acquire(contract, max_requests=1)
    page = pages(store, contract, connector)[0]
    page = replace(page, page_meta=replace(page.page_meta, enumerated_children=(1,)))
    attempt = assert_refused(tmp_path / "refused", b'{"email":null}')
    from ior_mvp.acquisition.contracts import ObservedResponse
    observed = ObservedResponse(**{**attempt["observed_response"], "headers_subset": tuple(tuple(x) for x in attempt["observed_response"]["headers_subset"])})
    coverage = evaluate_coverage([page], pagination_kind=pagination, requests_made=2, stop_reason=UnavailableReason.OUT_OF_SCOPE_CONTENT, observed_stop=observed, contract=contract, run_id=connector.run_id)
    assert coverage.status == "INCOMPLETE" and coverage.stop_reason == UnavailableReason.OUT_OF_SCOPE_CONTENT
    assert coverage.observed_stop.error_type == "PersonalDataFields" and coverage.requests_made == 2


def test_uninspectable_payload_kl_uses_policy_refusal_code(tmp_path):
    attempt = assert_refused(tmp_path, b"%PDF text", "application/pdf", error="UninspectableTextPayload")
    citation = attempt["reason"] + ":" + attempt["observed_response"]["error_type"]
    assert citation == "OUT_OF_SCOPE_CONTENT:UninspectableTextPayload"
    assert "FORMAT_NOT_PARSEABLE" not in json.dumps(attempt)


@pytest.mark.parametrize("source,stage,kind", CASES)
@pytest.mark.parametrize("mutation", ["missing_identity", "bad_text_type", "wrong_reporter", "wrong_registry"])
def test_actual_connector_quality_refuses_invalid_rows(tmp_path, source, stage, kind, mutation):
    body = json.loads(payload_for(source, kind))
    if mutation == "missing_identity":
        body["rows"] = [{}]
    elif mutation == "bad_text_type":
        body["rows"][0][{"production": "indicator_text", "directory": "entity_name_ar", "registry": "title_ar"}[kind]] = 123
    elif mutation == "wrong_reporter":
        body["rows"][0]["geography_text"] = "USA"
    else:
        body["rows"][0]["registry"] = "saber_registry" if source != "saber_registry" else "saso_catalogue"
    config, store, connector, contract, _ = setup(tmp_path, source, stage, kind, payload=json.dumps(body).encode())
    if mutation == "wrong_reporter" and kind != "production" or mutation == "wrong_registry" and kind != "registry":
        connector.source_config["reporter_code"] = "USA"
    connector.acquire(contract, max_requests=1)
    with pytest.raises(AcquisitionUnavailable) as error:
        snapshots.build_row_snapshot(store, config, ConnectorRegistry({source: type(connector)}), source_id=source, kind=kind)
    assert error.value.reason == UnavailableReason.FORMAT_NOT_PARSEABLE


@pytest.mark.parametrize("source,stage,kind", CASES)
def test_production_parsers_do_not_recognize_unobserved_or_test_shapes(tmp_path, source, stage, kind):
    from datetime import date

    _, store, test_connector, contract, transport = setup(tmp_path, source, stage, kind)
    assert source in default_registry().ids()
    connector = default_registry().get(source, source_config=test_connector.source_config, store=store, transport=transport, run_id=test_connector.run_id, environ={}, sleeper=lambda _: None)
    for body in [payload_for(source, kind), b'{"rows":[{"source_record_id":"TEST"}]}', b'{"unknown":[]}', b"not json"]:
        assert connector.parse_rows(body, "application/json") == []
    connector.source_config["pagination"]["kind"] = "NONE"
    connector.acquire(contract, max_requests=1)
    assert pages(store, contract, connector)[0].normalization_status == "UNPARSED"
    with pytest.raises(AcquisitionUnavailable) as refused:
        connector.snapshot(json.loads(payload_for(source, kind))["rows"], date(1999, 1, 1))
    assert refused.value.reason == UnavailableReason.FORMAT_NOT_PARSEABLE


@pytest.mark.parametrize("source,stage,kind", PRIVACY_SOURCES)
def test_personal_fields_double_refused_by_each_actual_source(tmp_path, source, stage, kind):
    assert_refused(tmp_path, _fixture("test_double_directory_personal_fields.json"), source=source, stage=stage, kind=kind)


def test_privacy_json_inspects_lists_and_duplicate_object_keys(tmp_path):
    assert_refused(tmp_path, b'{"outer":[[1,{"nested":[{"email":null}]}]]}')
    assert_refused(tmp_path / "duplicate", b'{"outer":{"email":null},"outer":{}}')


def test_text_guard_preserves_allowed_controls_and_recorded_mime(tmp_path):
    body = "\t\r\norganization \u200f ـ\n".encode()
    _, store, connector, contract, _ = privacy_acquire(tmp_path, body, "Text/Plain; charset=legacy")
    page = pages(store, contract, connector)[0]
    assert page.content_type == "Text/Plain"
    assert page.normalization_status == "UNPARSED"
    assert store.read_payload(page) == body


def test_observed_credential_is_sent_only_under_real_configured_name(tmp_path):
    _, store, connector, contract, transport = setup(tmp_path, environ={"IOR_TEST_SOURCE_KEY": "TEST-ONLY-KEY"})
    connector.source_config["credential_env_var"] = "IOR_TEST_SOURCE_KEY"
    connector.acquire(contract, max_requests=1)
    assert transport.request_headers == [{"Authorization": "Bearer TEST-ONLY-KEY"}]
    page = pages(store, contract, connector)[0]
    assert page.credential_env_var == "IOR_TEST_SOURCE_KEY" and page.credential_used is True
    assert all(b"TEST-ONLY-KEY" not in path.read_bytes() for path in store.root.rglob("*") if path.is_file())


@pytest.mark.parametrize("source,stage,kind", CASES)
@pytest.mark.parametrize("config_version", ["1.1.0", "arbitrary-other-version"])
def test_actual_connector_snapshot_helper_uses_stored_evidence(tmp_path, monkeypatch, source, stage, kind, config_version):
    from datetime import date

    config, store, parsed, contract, transport = setup(tmp_path, source, stage, kind)
    registry = default_registry()
    connector = registry.get(source, source_config=parsed.source_config, store=store, transport=transport,
                             run_id=parsed.run_id, environ={}, sleeper=lambda _: None,
                             config_version=config_version)
    # Patch only the unobserved source parsing in tests. The object, snapshot
    # method, acquisition, normalizer, quality validator and builder stay real.
    monkeypatch.setattr(type(connector), "parse_rows", InstitutionalParserMixin.parse_rows)
    monkeypatch.setattr(type(connector), "page_meta", InstitutionalParserMixin.page_meta)
    assert isinstance(connector.acquire(contract, max_requests=1), tuple)
    record = connector.snapshot([{"invented": "must never enter output"}], date(1999, 1, 1))
    assert record["source_id"] == source and record["kind"] == kind
    assert record["snapshot_id"].endswith("-2026-09-04")
    assert record["as_of_date"] == "2026-09-04"
    assert record["transformation_record"]["config_version"] == "1.1.0"
    assert all(p["transformation_record"]["config_version"] == "1.1.0" for p in record["evidence"])
    assert record == connector.snapshot([], date(2099, 12, 31))
    assert record == snapshots.build_row_snapshot(store, config, registry, source_id=source, kind=kind)
    path = snapshots.write_snapshot(record, tmp_path, allow_test_double=True)
    assert snapshots.reconstruct(path, store, config, registry).match
    connector.run_id = "20260905T120000Z"
    assert isinstance(connector.acquire(contract, max_requests=2), tuple)
    newer = connector.snapshot([], date(1999, 1, 1))
    assert newer["coverage"]["units"][0]["selected_run_id"] == "20260905T120000Z"
    assert newer["coverage"]["units"][0]["superseded_run_ids"] == ["20260904T120000Z"]
    assert snapshots.reconstruct(path, store, config, registry).detail["reason"] == "SELECTION_CHANGED"
    assert json.loads(path.read_text())["coverage"]["units"][0]["selected_run_id"] == "20260904T120000Z"


def test_source_connector_protocol_has_optional_parser_and_baci_stays_pending(tmp_path):
    from typing import Any, Callable, get_type_hints
    from ior_mvp.acquisition.connectors.base import SourceConnector
    from ior_mvp.acquisition.connectors.baci_cepii import BaciCepiiConnector

    hints = get_type_hints(SourceConnector)
    assert "parse_rows" in hints
    assert hints["parse_rows"] == Callable[[bytes, str], list[dict[str, Any]]] | None
    connector = BaciCepiiConnector(source_config={}, store=_temp_store(tmp_path), transport=FakeTransport({}, []), run_id="TEST", environ={})
    assert connector.parse_rows is None
    assert connector.classify_page(b"unparsed archive", "application/zip", Stage.BULK) == ("PENDING", None)
