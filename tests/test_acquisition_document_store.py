"""DocumentRecord store, builder, validator and reconstruction tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.connectors.base import ConnectorRegistry
from ior_mvp.acquisition.connectors.documents import DocumentConnector
from ior_mvp.acquisition.contracts import (
    AcquisitionConfigurationError,
    ProductScope,
    QueryContract,
    RawStoreIntegrityError,
    SnapshotWriteConflict,
    Stage,
    UNAVAILABLE,
    sha256_bytes,
)
from ior_mvp.acquisition.documents.store import (
    DOCUMENT_CONFIG_VERSION,
    DOCUMENT_ID_SCHEME,
    DOCUMENT_SCHEMA_VERSION,
    DocumentBuildReport,
    DocumentStore,
    build_document_record,
    build_document_records,
    document_id,
    reconstruct_document,
    validate_document_record,
)
from ior_mvp.acquisition.harmonise import PIPELINE_VERSION
from ior_mvp.acquisition.raw_store import RawStore, TEST_FIXTURE_SOURCE
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import (
    FakeTransport,
    document_fetch_result,
    document_list_payload,
    pre_observation_document_source_config,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "acquisition" / "documents"
DOC_URL = "https://example.test/doc.pdf"


class FixtureDocumentConnector(DocumentConnector):
    source_id = TEST_FIXTURE_SOURCE


def _test_roots(tmp_path: Path) -> tuple[Path, RawStore, DocumentStore]:
    data_root = tmp_path / "data"
    raw_cfg = acquisition_sources_config()["raw_store"]
    store = RawStore(
        data_root / "raw",
        max_artifact_bytes=raw_cfg["max_artifact_bytes_compressed"],
        max_store_bytes=raw_cfg["max_store_bytes_compressed"],
    )
    doc_store = DocumentStore(data_root / "documents")
    return data_root, store, doc_store


def _test_source_config() -> dict:
    return {
        **pre_observation_document_source_config(
            TEST_FIXTURE_SOURCE, authority="TEST DOUBLE", evidence_class="C"
        ),
        "source_id": TEST_FIXTURE_SOURCE,
        "access_classification": "public_open",
        "license_capture_required": False,
        "endpoint_templates": {"DOCUMENT": "{document_url}", "TERMS": UNAVAILABLE},
    }


def _acquire_fixture(
    tmp_path: Path,
    *,
    payload_path: str = "test_double_latin_two_pages.pdf",
    content_type: str = "application/pdf",
) -> tuple[dict, RawStore, DocumentStore, dict, Path]:
    data_root, store, doc_store = _test_roots(tmp_path)
    source_cfg = _test_source_config()
    config = {"metadata": {"version": "1.2.0"}, "sources": {TEST_FIXTURE_SOURCE: source_cfg}}
    list_payload = document_list_payload(
        TEST_FIXTURE_SOURCE,
        list_id="test-fixture-v1",
        entries=[{
            **document_list_payload(TEST_FIXTURE_SOURCE)["entries"][0],
            "document_url": DOC_URL,
            "supports": ["DOMESTIC_PRODUCT_PORTFOLIO"],
        }],
    )
    list_id = "test-fixture-v1"
    list_path = doc_store.list_path(TEST_FIXTURE_SOURCE, list_id)
    list_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.write_text(json.dumps(list_payload), encoding="utf-8")
    body = (FIXTURES / payload_path).read_bytes()
    transport = FakeTransport({DOC_URL: document_fetch_result(body, content_type)}, [])
    connector = FixtureDocumentConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260912T120000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = QueryContract(
        TEST_FIXTURE_SOURCE,
        Stage.DOCUMENT,
        "SAU",
        UNAVAILABLE,
        UNAVAILABLE,
        ProductScope.NOT_APPLICABLE,
        (),
        UNAVAILABLE,
        (),
        (("document_url", DOC_URL),),
    )
    result = connector.acquire(contract, max_requests=1)
    assert isinstance(result, tuple)
    page = result[0][0].contract
    from ior_mvp.acquisition.documents.lists import load_document_list

    document_list = load_document_list(
        list_path, source_id=TEST_FIXTURE_SOURCE, default_evidence_class="C"
    )
    record = build_document_record(
        store,
        config,
        source_id=TEST_FIXTURE_SOURCE,
        page=page,
        coverage=result[1],
        superseded_run_ids=(),
        document_list=document_list,
        list_path=list_path,
    )
    return config, store, doc_store, record, list_path


def test_document_id_scheme_deterministic_and_persistent() -> None:
    qh = "a" * 64
    raw = "b" * 64
    first = document_id("producer_unicoil", qh, raw)
    second = document_id("producer_unicoil", qh, raw)
    assert first == second
    assert first.startswith("DOC-PRODUCER-UNICOIL-")


def test_build_record_from_stored_pdf_validates(tmp_path: Path) -> None:
    config, store, doc_store, record, list_path = _acquire_fixture(tmp_path)
    assert set(record) == {
        "schema_version", "document_id", "document_id_scheme", "source_id", "source_boundary",
        "kind", "as_of_date", "list_ref", "declared", "raw_artifact_ref", "coverage",
        "text_layer", "segmentation", "page_count", "line_count", "pages", "transformation_record",
        "quality_summary", "evidence",
    }
    assert record["schema_version"] == DOCUMENT_SCHEMA_VERSION
    assert record["document_id_scheme"] == DOCUMENT_ID_SCHEME
    assert record["quality_summary"] == "PASS"
    assert record["text_layer"]["status"] == "COMPLETE"
    assert record["transformation_record"]["config_version"] == DOCUMENT_CONFIG_VERSION
    assert record["transformation_record"]["pipeline_version"] == PIPELINE_VERSION
    assert record["evidence"][0]["supports"] == ["DOMESTIC_PRODUCT_PORTFOLIO"]
    assert record["evidence"][0]["evidence_class"] == "C"
    assert record["pages"]
    assert record["pages"][0]["text_sha256"]
    validate_document_record(record, allow_test_double=True)


def test_arabic_lines_byte_exact_in_record(tmp_path: Path) -> None:
    _, _, _, record, _ = _acquire_fixture(
        tmp_path, payload_path="test_double_arabic_cid.pdf"
    )
    assert record["pages"][0]["lines"][:2] == [
        "الحد الأدنى الإلزامي 60 جم/م2",
        "Minimum coating 60 gsm",
    ]


def test_raw_only_record_for_no_text_layer(tmp_path: Path) -> None:
    _, _, _, record, _ = _acquire_fixture(
        tmp_path, payload_path="test_double_no_text_layer.pdf"
    )
    assert record["quality_summary"] == "RAW_ONLY"
    assert record["text_layer"]["status"] == "UNAVAILABLE"
    assert record["page_count"] == 1
    assert record["line_count"] == 0
    assert record["pages"] == [
        {
            "page_index": 1,
            "line_count": 0,
            "text_sha256": sha256_bytes(b""),
            "lines": [],
        }
    ]
    validate_document_record(record, allow_test_double=True)


def test_write_once_identical_ok_different_conflict(tmp_path: Path) -> None:
    _, _, doc_store, record, _ = _acquire_fixture(tmp_path)
    path = doc_store.write_record(record, allow_test_double=True)
    assert doc_store.write_record(record, allow_test_double=True) == path
    tampered = {**record, "line_count": record["line_count"] + 1}
    with pytest.raises(SnapshotWriteConflict):
        doc_store.write_record(tampered, allow_test_double=True)


def test_reacquire_identical_bytes_reports_already_stored_and_writes_nothing(
    tmp_path: Path,
) -> None:
    data_root, store, doc_store = _test_roots(tmp_path)
    config, _, _, record, _ = _acquire_fixture(tmp_path)
    doc_store.write_record(record, allow_test_double=True)
    report = build_document_records(
        store,
        config,
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        doc_store,
        source_id=TEST_FIXTURE_SOURCE,
        list_id="test-fixture-v1",
    )
    assert report.built == ()
    assert len(report.already_stored) == 1
    assert len(list(doc_store.record_path(TEST_FIXTURE_SOURCE, record["document_id"]).parent.glob("*.json"))) == 1


def test_build_selects_latest_run_and_records_sorted_superseded_runs(
    tmp_path: Path,
) -> None:
    config, store, doc_store, _, _ = _acquire_fixture(tmp_path)
    body = (FIXTURES / "test_double_latin_two_pages.pdf").read_bytes()
    connector = FixtureDocumentConnector(
        source_config=config["sources"][TEST_FIXTURE_SOURCE],
        store=store,
        transport=FakeTransport(
            {DOC_URL: document_fetch_result(body, "application/pdf")}, []
        ),
        run_id="20260912T130000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = QueryContract(
        TEST_FIXTURE_SOURCE,
        Stage.DOCUMENT,
        "SAU",
        UNAVAILABLE,
        UNAVAILABLE,
        ProductScope.NOT_APPLICABLE,
        (),
        UNAVAILABLE,
        (),
        (("document_url", DOC_URL),),
    )
    connector.acquire(contract, max_requests=1)

    report = build_document_records(
        store,
        config,
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        doc_store,
        source_id=TEST_FIXTURE_SOURCE,
        list_id="test-fixture-v1",
    )
    assert len(report.built) == 1
    assert report.already_stored == ()

    record_path = doc_store.record_path(TEST_FIXTURE_SOURCE, report.built[0])
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["raw_artifact_ref"]["run_id"] == "20260912T130000Z"
    assert record["coverage"]["superseded_run_ids"] == ["20260912T120000Z"]


def test_acquire_documents_budget_counts_every_list_entry(tmp_path: Path) -> None:
    from ior_mvp.acquisition.pipeline import PipelineDeps, acquire_documents

    config, store, _, _, list_path = _acquire_fixture(tmp_path)
    payload = json.loads(list_path.read_text(encoding="utf-8"))
    payload["entries"].append(
        {
            **payload["entries"][0],
            "entry_id": "E-002",
            "document_url": "https://example.test/second.pdf",
        }
    )
    list_path.write_text(json.dumps(payload), encoding="utf-8")
    deps = PipelineDeps(
        config,
        store,
        FakeTransport({}, []),
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        "20260912T140000Z",
        {},
        lambda _: None,
    )

    with pytest.raises(AcquisitionConfigurationError, match="below minimum 2"):
        acquire_documents(
            TEST_FIXTURE_SOURCE,
            list_id="test-fixture-v1",
            deps=deps,
            max_requests=1,
        )


def test_acquire_documents_rejects_unsafe_list_id_before_transport(
    tmp_path: Path,
) -> None:
    from ior_mvp.acquisition.pipeline import PipelineDeps, acquire_documents

    _, store, _ = _test_roots(tmp_path)
    transport = FakeTransport({}, [])
    deps = PipelineDeps(
        {"metadata": {"version": "1.2.0"}, "sources": {TEST_FIXTURE_SOURCE: _test_source_config()}},
        store,
        transport,
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        "20260912T140000Z",
        {},
        lambda _: None,
    )

    with pytest.raises(AcquisitionConfigurationError, match="list_id"):
        acquire_documents(
            TEST_FIXTURE_SOURCE,
            list_id="../evil",
            deps=deps,
            max_requests=1,
        )
    assert transport.calls == []


def test_changed_bytes_create_new_document_id_and_retain_old(tmp_path: Path) -> None:
    config, store, doc_store, first, list_path = _acquire_fixture(tmp_path)
    doc_store.write_record(first, allow_test_double=True)
    body = (FIXTURES / "test_double_plain_crlf.txt").read_bytes()
    transport = FakeTransport({DOC_URL: document_fetch_result(body, "text/plain")}, [])
    connector = FixtureDocumentConnector(
        source_config=config["sources"][TEST_FIXTURE_SOURCE],
        store=store,
        transport=transport,
        run_id="20260912T130000Z",
        environ={},
        sleeper=lambda _: None,
    )
    contract = QueryContract(
        TEST_FIXTURE_SOURCE,
        Stage.DOCUMENT,
        "SAU",
        UNAVAILABLE,
        UNAVAILABLE,
        ProductScope.NOT_APPLICABLE,
        (),
        UNAVAILABLE,
        (),
        (("document_url", DOC_URL),),
    )
    connector.acquire(contract, max_requests=1)
    report = build_document_records(
        store,
        config,
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        doc_store,
        source_id=TEST_FIXTURE_SOURCE,
        list_id="test-fixture-v1",
    )
    assert len(report.built) == 1
    assert report.built[0] != first["document_id"]
    assert doc_store.record_path(TEST_FIXTURE_SOURCE, first["document_id"]).exists()


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_key",
        "extra_key",
        "nested_extra_key",
        "wrong_id",
        "synthetic_flag",
        "unsupported_code",
        "tampered_line",
        "line_count_mismatch",
        "wrong_sha",
        "kind_mismatch",
        "non_public_boundary",
        "quality_inconsistency",
    ],
)
def test_validate_negative_probes(tmp_path: Path, mutation: str) -> None:
    _, _, _, record, _ = _acquire_fixture(tmp_path)
    mutated = json.loads(json.dumps(record))
    if mutation == "missing_key":
        mutated.pop("pages")
    elif mutation == "extra_key":
        mutated["extra"] = True
    elif mutation == "nested_extra_key":
        mutated["coverage"]["extra"] = True
    elif mutation == "wrong_id":
        mutated["document_id"] = "DOC-WRONG"
    elif mutation == "synthetic_flag":
        mutated["synthetic_flag"] = True
    elif mutation == "unsupported_code":
        mutated["declared"]["supports"] = ["NOT_A_REAL_CODE"]
    elif mutation == "tampered_line":
        mutated["pages"][0]["lines"][0] = "tampered"
    elif mutation == "line_count_mismatch":
        mutated["line_count"] += 1
    elif mutation == "wrong_sha":
        mutated["pages"][0]["text_sha256"] = "0" * 64
    elif mutation == "kind_mismatch":
        mutated["kind"] = "snapshot"
    elif mutation == "non_public_boundary":
        mutated["source_boundary"] = "synthetic"
    elif mutation == "quality_inconsistency":
        mutated["quality_summary"] = "PASS"
        mutated["text_layer"]["status"] = "UNAVAILABLE"
    with pytest.raises(ValueError):
        validate_document_record(mutated, allow_test_double=True)


def test_test_double_refused_under_repository_data_documents(tmp_path: Path) -> None:
    doc_store = DocumentStore(PROJECT_ROOT / "data" / "documents")
    _, _, _, record, _ = _acquire_fixture(tmp_path)
    with pytest.raises(RawStoreIntegrityError):
        doc_store.write_record(record)


def test_root_guard_rejects_frozen_roots(tmp_path: Path) -> None:
    with pytest.raises(RawStoreIntegrityError):
        DocumentStore(PROJECT_ROOT / "data" / "snapshots" / "public")
    with pytest.raises(RawStoreIntegrityError):
        DocumentStore(PROJECT_ROOT / "data" / "synthetic")


def test_reconstruct_document_match_and_tamper(tmp_path: Path) -> None:
    config, store, doc_store, record, list_path = _acquire_fixture(tmp_path)
    path = doc_store.write_record(record, allow_test_double=True)
    assert reconstruct_document(path, store, config, doc_store).match

    payload_root = tmp_path / "payload"
    _, store_p, doc_store_p, record_p, _ = _acquire_fixture(payload_root)
    path_p = doc_store_p.write_record(record_p, allow_test_double=True)
    payload_path = next(store_p.root.rglob("page-*.gz"))
    data = bytearray(payload_path.read_bytes())
    data[-1] ^= 1
    payload_path.write_bytes(data)
    with pytest.raises(RawStoreIntegrityError):
        reconstruct_document(path_p, store_p, config, doc_store_p)

    record_root = tmp_path / "record"
    _, store_r, doc_store_r, record_r, _ = _acquire_fixture(record_root)
    path_r = doc_store_r.write_record(record_r, allow_test_double=True)
    tampered = json.loads(path_r.read_text(encoding="utf-8"))
    tampered["line_count"] += 1
    path_r.write_text(json.dumps(tampered), encoding="utf-8")
    assert not reconstruct_document(path_r, store_r, config, doc_store_r).match

    list_root = tmp_path / "list"
    _, store_l, doc_store_l, record_l, list_path_l = _acquire_fixture(list_root)
    path_l = doc_store_l.write_record(record_l, allow_test_double=True)
    list_copy = json.loads(list_path_l.read_text(encoding="utf-8"))
    list_copy["consultation_summary_text"] = "changed"
    list_path_l.write_text(json.dumps(list_copy), encoding="utf-8")
    assert not reconstruct_document(path_l, store_l, config, doc_store_l).match


def test_build_records_skips_units_without_list_entry_and_reports(tmp_path: Path) -> None:
    config, store, doc_store, record, _ = _acquire_fixture(tmp_path)
    doc_store.write_record(record, allow_test_double=True)
    list_payload = document_list_payload(TEST_FIXTURE_SOURCE, entries=[])
    list_payload["consultation_summary_text"] = "No matching entries."
    list_payload["list_id"] = "other-list-v1"
    other_list = doc_store.list_path(TEST_FIXTURE_SOURCE, "other-list-v1")
    other_list.write_text(json.dumps(list_payload), encoding="utf-8")
    report = build_document_records(
        store,
        config,
        ConnectorRegistry({TEST_FIXTURE_SOURCE: FixtureDocumentConnector}),
        doc_store,
        source_id=TEST_FIXTURE_SOURCE,
        list_id="other-list-v1",
    )
    assert report.built == ()
    assert report.skipped_no_entry


def test_repository_document_records_loader_validates_and_partition(tmp_path: Path) -> None:
    from ior_mvp.acquisition import repository

    data_root, store, doc_store = _test_roots(tmp_path)
    _, _, _, record, _ = _acquire_fixture(tmp_path)
    path = doc_store.write_record(record, allow_test_double=True)
    loaded = repository.document_records(data_root=data_root, allow_test_double=True)
    assert record["document_id"] in loaded
    assert path.stem == record["document_id"]
    assert path.parent.parent.name == TEST_FIXTURE_SOURCE


def test_no_normalisation_in_record(tmp_path: Path) -> None:
    _, _, _, record, _ = _acquire_fixture(
        tmp_path, payload_path="test_double_arabic_cid.pdf"
    )
    joined = json.dumps(record["pages"], ensure_ascii=False)
    assert "60 gsm" in joined
