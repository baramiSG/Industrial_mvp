"""Document connector acquire-path tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import BaseConnector, default_registry
from ior_mvp.acquisition.connectors.documents import DocumentConnector, ProducerUnicoilConnector
from ior_mvp.acquisition.contracts import (
    AcquisitionConfigurationError,
    ProductScope,
    QueryContract,
    Stage,
    UNAVAILABLE,
    UnavailableRecord,
    UnavailableReason,
    sha256_bytes,
)
from ior_mvp.acquisition.pipeline import plan_units
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.acquisition.transport import FetchResult, NetworkError, SizeBudgetExceeded
from tests.acquisition_doubles import (
    FakeTransport,
    document_fetch_result,
    document_list_payload,
    pre_observation_document_source_config,
)
from tests.test_acquisition_institutional_connectors import assert_attempt, assert_refused, setup

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "acquisition" / "documents"
DOC_URL = "https://example.test/doc.pdf"


def _test_store(tmp_path: Path) -> RawStore:
    raw_cfg = acquisition_sources_config()["raw_store"]
    return RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )


def _document_contract(source_id: str, url: str = DOC_URL) -> QueryContract:
    return QueryContract(
        source_id=source_id,
        stage=Stage.DOCUMENT,
        reporter="SAU",
        partner=UNAVAILABLE,
        flow=UNAVAILABLE,
        product_scope=ProductScope.NOT_APPLICABLE,
        product_codes=(),
        nomenclature=UNAVAILABLE,
        periods=(),
        parameters=(("document_url", url),),
    )


def _observed_document_config(source_id: str, *, evidence_class: str = "C", **overrides: object) -> dict:
    cfg = {
        **pre_observation_document_source_config(
            source_id, authority="TEST authority", evidence_class=evidence_class
        ),
        "source_id": source_id,
        "access_classification": "public_open",
        "documentation_reference": "https://example.test/docs",
        "terms_reference": UNAVAILABLE,
        "license_capture_required": False,
        "endpoint_templates": {"DOCUMENT": "{document_url}", "TERMS": UNAVAILABLE},
        "recorded_on": "2026-09-12",
    }
    cfg.update(overrides)
    return {"metadata": {"version": "1.2.0"}, "sources": {source_id: cfg}}


def _document_setup(
    tmp_path: Path,
    source_id: str = "producer_unicoil",
    *,
    body: bytes | None = None,
    content_type: str = "application/pdf",
    config: dict | None = None,
    environ: dict | None = None,
    connector_cls: type = ProducerUnicoilConnector,
) -> tuple[dict, RawStore, DocumentConnector, QueryContract, FakeTransport]:
    config = config or _observed_document_config(source_id)
    cfg = config["sources"][source_id]
    body = body if body is not None else (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    response = document_fetch_result(body, content_type)
    transport = FakeTransport({DOC_URL: response}, [])
    store = _test_store(tmp_path)
    connector = connector_cls(
        source_config=cfg,
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ=environ or {},
        sleeper=lambda _: None,
    )
    return config, store, connector, _document_contract(source_id), transport


def _pages(store: RawStore, contract: QueryContract, connector: DocumentConnector):
    return store.pages_for(contract.source_id, contract.query_hash(), connector.run_id)


def test_default_registry_has_twenty_one_ids_and_document_kinds() -> None:
    reg = default_registry()
    assert reg.ids() == (
        "baci_cepii", "etimad_tenders", "gastat", "ministry_of_industry", "modon",
        "producer_advanced_petrochemical", "producer_altaiseer_talco",
        "producer_alupco", "producer_hadeed", "producer_maaden",
        "producer_sabic", "producer_tasnee", "producer_unicoil",
        "saber_registry", "saso_catalogue", "saso_documents", "tadawul_disclosures",
        "un_comtrade", "wco_hs_nomenclature", "wits_trade", "zatca_tariff",
    )


def test_pre_storage_hook_base_behaviour(tmp_path: Path) -> None:
    from ior_mvp.acquisition.connectors.base import BaseConnector

    store = _test_store(tmp_path)
    base = BaseConnector(
        source_config=_observed_document_config("producer_unicoil")["sources"]["producer_unicoil"],
        store=store,
        transport=FakeTransport({}, []),
        run_id="20260912T120000Z",
        environ={},
    )
    sample = document_fetch_result(b'{"phone":null}', "application/json")
    for stage in (Stage.UNIVERSE, Stage.TARIFF, Stage.BULK, Stage.TERMS):
        assert base._pre_storage_refusal(sample, stage) is None

    assert_refused(tmp_path / "personal", b'{"phone":null}', error="PersonalDataFields")
    assert_refused(
        tmp_path / "pdf-directory",
        b"%PDF-1.4 clean text",
        "application/pdf",
        error="UninspectableTextPayload",
    )

    _, store, connector, contract, _ = _document_setup(tmp_path / "doc-hook")
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    assert _pages(store, contract, connector)[0].normalization_status == "NORMALIZED"


INSTITUTIONAL_REFUSAL_MESSAGE = (
    "Response refused by institutional text-only privacy policy; body not stored"
)


def test_pre_storage_hook_pins_institutional_refusal_literals_and_delegation(tmp_path: Path) -> None:
    """IAC-10: the DIRECTORY/REGISTRY hook returns exactly the S12a error types and message.

    DocumentConnector must delegate those stages to BaseConnector (DD-7) rather than
    re-implement them, so both classes return identical tuples for identical inputs.
    """
    from ior_mvp.acquisition.connectors.base import BaseConnector

    store = _test_store(tmp_path)
    cfg = _observed_document_config("producer_unicoil")["sources"]["producer_unicoil"]
    kwargs = dict(
        source_config=cfg, store=store, transport=FakeTransport({}, []),
        run_id="20260912T120000Z", environ={},
    )
    base = BaseConnector(**kwargs)
    document = ProducerUnicoilConnector(**kwargs, sleeper=lambda _: None)
    personal = document_fetch_result(b'{"phone":null}', "application/json")
    uninspectable = document_fetch_result(b"%PDF-1.4 clean text", "application/pdf")
    clean = document_fetch_result(b'{"organization":"TEST"}', "application/json")
    for stage in (Stage.DIRECTORY, Stage.REGISTRY):
        for connector in (base, document):
            assert connector._pre_storage_refusal(personal, stage) == (
                "PersonalDataFields", INSTITUTIONAL_REFUSAL_MESSAGE
            )
            assert connector._pre_storage_refusal(uninspectable, stage) == (
                "UninspectableTextPayload", INSTITUTIONAL_REFUSAL_MESSAGE
            )
            assert connector._pre_storage_refusal(clean, stage) is None
    # non-document stages other than DIRECTORY/REGISTRY never refuse, in either class
    for stage in (Stage.UNIVERSE, Stage.TARIFF, Stage.BULK, Stage.TERMS):
        assert base._pre_storage_refusal(personal, stage) is None
        assert document._pre_storage_refusal(personal, stage) is None
    # DOCUMENT stage applies only the envelope policy (DD-6/DD-22): a personal-data label inside
    # an accepted text/plain envelope is not screened, while a non-envelope type is refused
    assert document._pre_storage_refusal(
        document_fetch_result(b'{"phone":null}', "text/plain"), Stage.DOCUMENT
    ) is None
    assert document._pre_storage_refusal(
        document_fetch_result(b"BINARY", "application/octet-stream"), Stage.DOCUMENT
    ) == (
        "UnsupportedDocumentEnvelope",
        "Response refused by document envelope policy; body not stored",
    )
    # the refusal recorded on an acquire path carries the same literal message
    attempt = assert_refused(tmp_path / "personal-literal", b'{"phone":null}', error="PersonalDataFields")
    assert attempt["observed_response"]["error_message_redacted"] == INSTITUTIONAL_REFUSAL_MESSAGE
    assert attempt["observed_response"]["error_type"] == "PersonalDataFields"
    attempt = assert_refused(
        tmp_path / "uninspectable-literal", b"%PDF-1.4 clean text", "application/pdf",
        error="UninspectableTextPayload",
    )
    assert attempt["observed_response"]["error_message_redacted"] == INSTITUTIONAL_REFUSAL_MESSAGE
    assert attempt["observed_response"]["error_type"] == "UninspectableTextPayload"


def test_no_list_unit_yields_endpoint_unverified_zero_requests(tmp_path: Path) -> None:
    source_id = "producer_unicoil"
    config = _observed_document_config(source_id)
    store = _test_store(tmp_path)
    transport = FakeTransport({}, [])
    connector = ProducerUnicoilConnector(
        source_config=config["sources"][source_id],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={UNAVAILABLE: "canary"},
        sleeper=lambda _: None,
    )
    units = plan_units(
        Stage.DOCUMENT,
        source_id=source_id,
        years=(),
        flows=(),
        candidates=None,
        config=config,
    )
    assert len(units) == 1 and units[0].parameters == (("document_url", UNAVAILABLE),)
    result = connector.acquire(units[0], max_requests=1)
    attempt = assert_attempt(
        store, units[0], connector, result, UnavailableReason.ENDPOINT_UNVERIFIED, requests=0
    )
    assert attempt["credential_env_var"] is None
    assert not transport.calls


def test_unobserved_access_yields_license_unrecorded_zero_requests(tmp_path: Path) -> None:
    config = _observed_document_config("producer_unicoil")
    config["sources"]["producer_unicoil"]["access_classification"] = UNAVAILABLE
    _, store, connector, contract, transport = _document_setup(
        tmp_path, config=config
    )
    result = connector.acquire(contract, max_requests=2)
    assert_attempt(store, contract, connector, result, UnavailableReason.LICENSE_UNRECORDED)
    assert not transport.calls


def test_pdf_response_stored_with_pdf_extension_and_normalized(tmp_path: Path) -> None:
    _, store, connector, contract, transport = _document_setup(tmp_path)
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    arts, coverage = result
    assert coverage.status == "COMPLETE"
    assert coverage.completeness_basis.value == "SINGLE_RESPONSE_NO_PAGINATION"
    assert coverage.requests_made == 1
    page = _pages(store, contract, connector)[0]
    assert page.normalization_status == "NORMALIZED"
    assert any(path.name.endswith(".payload.pdf.gz") for path in store.root.rglob("*.gz"))
    assert transport.calls == [DOC_URL]


def test_no_text_layer_pdf_stored_unparsed_no_text_layer(tmp_path: Path) -> None:
    body = (FIXTURES / "test_double_no_text_layer.pdf").read_bytes()
    _, store, connector, contract, _ = _document_setup(tmp_path, body=body)
    connector.acquire(contract, max_requests=1)
    page = _pages(store, contract, connector)[0]
    assert (page.normalization_status, page.normalization_reason) == ("UNPARSED", "no_text_layer")


@pytest.mark.parametrize(
    "content_type,ext",
    [
        ("text/html", "html"),
        ("text/plain", "txt"),
    ],
)
def test_html_and_plain_stored_with_extensions(tmp_path: Path, content_type: str, ext: str) -> None:
    body = (
        FIXTURES / "test_double_arabic_english.html"
        if content_type == "text/html"
        else FIXTURES / "test_double_plain_crlf.txt"
    ).read_bytes()
    _, store, connector, contract, _ = _document_setup(
        tmp_path, body=body, content_type=content_type
    )
    connector.acquire(contract, max_requests=1)
    assert any(path.name.endswith(f".payload.{ext}.gz") for path in store.root.rglob("*.gz"))


@pytest.mark.parametrize(
    "mime,missing_header",
    [
        ("application/zip", False),
        ("application/octet-stream", False),
        ("image/png", False),
        ("application/x-pdf", False),
        (None, True),
    ],
)
def test_unsupported_envelopes_refused_hash_only(
    tmp_path: Path, mime: str | None, missing_header: bool
) -> None:
    body = b"BINARY-NOT-STORED"
    headers = () if missing_header else (("content-type", mime),)
    response = FetchResult(
        http_status=200,
        headers_subset=headers,
        body=body,
        final_url_redacted=DOC_URL,
        fetched_at="2026-09-12T00:00:00Z",
        content_length_header=len(body),
    )
    transport = FakeTransport({DOC_URL: response}, [])
    config = _observed_document_config("producer_unicoil")
    store = _test_store(tmp_path)
    connector = ProducerUnicoilConnector(
        source_config=config["sources"]["producer_unicoil"],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = _document_contract("producer_unicoil")
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.OUT_OF_SCOPE_CONTENT
    assert result.observed_response.error_type == "UnsupportedDocumentEnvelope"
    assert result.observed_response.body_sha256 == sha256_bytes(body)
    assert result.observed_response.body_byte_count == len(body)
    assert result.coverage.status == "INCOMPLETE"
    assert not list(store.root.rglob("*.gz"))


def test_declared_pdf_with_non_pdf_bytes_is_stored_then_parser_error(tmp_path: Path) -> None:
    body = (FIXTURES / "test_double_garbage.pdf").read_bytes()
    _, store, connector, contract, _ = _document_setup(tmp_path, body=body)
    connector.acquire(contract, max_requests=1)
    page = _pages(store, contract, connector)[0]
    assert page.normalization_status == "UNPARSED"
    assert store.read_payload(page) == body


def test_size_budget_exceeded_recorded(tmp_path: Path) -> None:
    config = _observed_document_config("producer_unicoil")
    store = RawStore(tmp_path / "raw", max_artifact_bytes=16, max_store_bytes=4096)
    transport = FakeTransport({}, [])
    transport.responses[DOC_URL] = SizeBudgetExceeded("budget")
    connector = ProducerUnicoilConnector(
        source_config=config["sources"]["producer_unicoil"],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    result = connector.acquire(_document_contract("producer_unicoil"), max_requests=1)
    assert result.reason == UnavailableReason.SIZE_BUDGET_EXCEEDED
    assert not _pages(store, _document_contract("producer_unicoil"), connector)


@pytest.mark.parametrize("status,reason", [(403, "HTTP_ERROR"), (404, "HTTP_ERROR"), (429, "RATE_LIMITED")])
def test_http_error_network_error_rate_limited_recorded(
    tmp_path: Path, status: int, reason: str
) -> None:
    body = b"error-body"
    config = _observed_document_config("producer_unicoil")
    store = _test_store(tmp_path)
    transport = FakeTransport({}, [])
    if status == 429:
        transport.responses[DOC_URL] = FetchResult(
            status, (("content-type", "text/plain"),), body, DOC_URL, "2026-09-12T00:00:00Z", len(body)
        )
    else:
        transport.responses[DOC_URL] = FetchResult(
            status, (("content-type", "text/plain"),), body, DOC_URL, "2026-09-12T00:00:00Z", len(body)
        )
    connector = ProducerUnicoilConnector(
        source_config=config["sources"]["producer_unicoil"],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    result = connector.acquire(_document_contract("producer_unicoil"), max_requests=1)
    assert result.reason.value == reason
    assert not _pages(store, _document_contract("producer_unicoil"), connector)


def test_network_error_recorded(tmp_path: Path) -> None:
    config = _observed_document_config("producer_unicoil")
    store = _test_store(tmp_path)
    transport = FakeTransport({}, [])
    transport.responses[DOC_URL] = NetworkError("TLS failure (TEST double)")
    connector = ProducerUnicoilConnector(
        source_config=config["sources"]["producer_unicoil"],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    result = connector.acquire(_document_contract("producer_unicoil"), max_requests=1)
    assert result.reason == UnavailableReason.NETWORK_ERROR


def test_terms_capture_then_document_uses_two_requests(tmp_path: Path) -> None:
    config = _observed_document_config(
        "producer_unicoil",
        license_capture_required=True,
        terms_reference="https://example.test/terms",
    )
    config["sources"]["producer_unicoil"]["endpoint_templates"]["TERMS"] = "https://example.test/terms"
    body = (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    transport = FakeTransport(
        {
            "https://example.test/terms": document_fetch_result(b"terms text", "text/plain"),
            DOC_URL: document_fetch_result(body, "application/pdf"),
        },
        [],
    )
    store = _test_store(tmp_path)
    connector = ProducerUnicoilConnector(
        source_config=config["sources"]["producer_unicoil"],
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = _document_contract("producer_unicoil")
    result = connector.acquire(contract, max_requests=2)
    assert isinstance(result, tuple)
    assert len(transport.calls) == 2
    terms = list(store.iter_contracts(stage="TERMS"))
    assert terms[0].normalization_status == "UNPARSED"
    with pytest.raises(AcquisitionConfigurationError):
        from ior_mvp.acquisition.pipeline import _run_units, PipelineDeps
        from ior_mvp.acquisition.connectors.base import ConnectorRegistry

        deps = PipelineDeps(
            config,
            store,
            transport,
            ConnectorRegistry({"producer_unicoil": ProducerUnicoilConnector}),
            "20260912T120001Z",
            {},
            lambda _: None,
        )
        _run_units(
            deps,
            source_id="producer_unicoil",
            stage=Stage.DOCUMENT,
            units=(contract,),
            max_requests=1,
        )


def test_sentinel_credential_never_looked_up_or_sent(tmp_path: Path) -> None:
    config = _observed_document_config("producer_unicoil")
    config["sources"]["producer_unicoil"]["credential_env_var"] = UNAVAILABLE
    _, store, connector, contract, transport = _document_setup(
        tmp_path, config=config, environ={UNAVAILABLE: "canary"}
    )
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    page = _pages(store, contract, connector)[0]
    assert transport.request_headers == [{}]
    assert page.credential_env_var is None and page.credential_used is False


def test_validate_checks_identity_envelope_and_hash(tmp_path: Path) -> None:
    _, store, connector, contract, _ = _document_setup(tmp_path)
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    report = connector.validate(result[0][0])
    assert report.status == "PASS"
    names = {check.check_id for check in report.checks}
    assert names == {"source_stage_reporter", "document_envelope", "payload_hash"}


def test_document_connector_does_not_import_network_modules() -> None:
    import ast
    from pathlib import Path

    root = Path("src/ior_mvp/acquisition/documents")
    targets = [root / "__init__.py", root / "lists.py", root / "store.py", root / "textlayer.py"]
    targets.append(Path("src/ior_mvp/acquisition/connectors/documents.py"))
    banned = {"urllib", "socket", "ssl", "http"}
    for path in targets:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in banned, path
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in banned, path
