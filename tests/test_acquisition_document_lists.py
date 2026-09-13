"""DocumentList 1.0.0 schema and validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import (
    AcquisitionConfigurationError,
    RawStoreIntegrityError,
)
from ior_mvp.acquisition.documents.lists import (
    SOURCE_ALLOWED_SUPPORTS,
    load_document_list,
    list_sha256,
    validate_document_list,
)
from ior_mvp.acquisition.documents.store import DocumentStore
from tests.acquisition_doubles import document_list_payload


def test_valid_list_loads_and_entries_ordered(tmp_path: Path) -> None:
    payload = document_list_payload(
        "producer_unicoil",
        entries=[
            document_list_payload("producer_unicoil")["entries"][0]
            | {"entry_id": "E-002", "document_url": "https://example.test/two.pdf"},
            document_list_payload("producer_unicoil")["entries"][0],
        ],
    )
    path = tmp_path / "producer_unicoil-v1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = load_document_list(path, source_id="producer_unicoil", default_evidence_class="C")
    assert [entry.entry_id for entry in loaded.entries] == ["E-001", "E-002"]


def test_exact_keys_and_unknown_key_rejected() -> None:
    payload = document_list_payload("producer_unicoil")
    payload["extra"] = "x"
    with pytest.raises(AcquisitionConfigurationError, match="unknown keys"):
        validate_document_list(payload, source_id="producer_unicoil", default_evidence_class="C")


@pytest.mark.parametrize(
    "recorded_on", ["", "yesterday", "2026-02-30", "20260912", None]
)
def test_recorded_on_must_be_iso_date(recorded_on: object) -> None:
    payload = document_list_payload("producer_unicoil")
    payload["recorded_on"] = recorded_on
    with pytest.raises(AcquisitionConfigurationError, match="recorded_on"):
        validate_document_list(
            payload,
            source_id="producer_unicoil",
            default_evidence_class="C",
        )


def test_enums_url_scheme_uniqueness_and_languages() -> None:
    payload = document_list_payload("producer_unicoil")
    payload["entries"][0]["document_url"] = "ftp://example.test/x.pdf"
    with pytest.raises(AcquisitionConfigurationError):
        validate_document_list(payload, source_id="producer_unicoil", default_evidence_class="C")
    payload = document_list_payload("producer_unicoil")
    payload["entries"].append(payload["entries"][0] | {"entry_id": "E-002"})
    with pytest.raises(AcquisitionConfigurationError):
        validate_document_list(payload, source_id="producer_unicoil", default_evidence_class="C")


def test_evidence_class_target_must_equal_source_default() -> None:
    payload = document_list_payload("producer_unicoil")
    payload["entries"][0]["evidence_class_target"] = "B"
    with pytest.raises(AcquisitionConfigurationError):
        validate_document_list(payload, source_id="producer_unicoil", default_evidence_class="C")


def test_supports_subset_per_source() -> None:
    payload = document_list_payload("etimad_tenders")
    payload["entries"][0]["evidence_class_target"] = "B"
    payload["entries"][0]["publisher_kind"] = "procurement_authority"
    payload["entries"][0]["supports"] = ["DOMESTIC_PRODUCT_PORTFOLIO"]
    with pytest.raises(AcquisitionConfigurationError):
        validate_document_list(payload, source_id="etimad_tenders", default_evidence_class="B")
    allowed = SOURCE_ALLOWED_SUPPORTS["etimad_tenders"]
    payload["entries"][0]["supports"] = sorted(allowed)[:1]
    validate_document_list(payload, source_id="etimad_tenders", default_evidence_class="B")


def test_empty_entries_requires_consultation_text() -> None:
    payload = document_list_payload("producer_unicoil", entries=[])
    payload["consultation_summary_text"] = "No verifiable documents on consulted pages."
    validate_document_list(payload, source_id="producer_unicoil", default_evidence_class="C")


def test_schema_admits_no_personal_data_keys() -> None:
    from ior_mvp.acquisition.connectors.base import _personal_field
    from ior_mvp.acquisition.documents.lists import _ENTRY_KEYS, _LIST_TOP_KEYS

    for key in _LIST_TOP_KEYS | _ENTRY_KEYS:
        assert not _personal_field(key), key


def test_list_sha256_and_write_once_path_rules(tmp_path: Path) -> None:
    payload = document_list_payload("producer_unicoil")
    path = tmp_path / "producer_unicoil-v1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    first = list_sha256(path)
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert list_sha256(path) == first

    store = DocumentStore(tmp_path / "documents")
    for invalid_list_id in ("../x", "Bad_ID", "ab"):
        with pytest.raises((AcquisitionConfigurationError, RawStoreIntegrityError)):
            store.list_path("producer_unicoil", invalid_list_id)
    with pytest.raises(RawStoreIntegrityError):
        store.list_path("../producer_unicoil", "producer_unicoil-v1")
    with pytest.raises(RawStoreIntegrityError):
        store.record_path("producer_unicoil", "../../x")


def test_s14_producer_lists_validate_and_entries_match_observed_urls() -> None:
    root = Path(__file__).resolve().parents[1] / "data" / "documents"
    expected = {
        "producer_hadeed": {
            "https://hadeed.com.sa/pdf/product-catalouge.pdf",
        },
        "producer_alupco": {"https://alupco.com/about/"},
        "producer_altaiseer_talco": {
            "https://altaiseer.com/en/%d8%aa%d8%a7%d9%84%d9%83%d9%88-%d9%81%d9%8a-%d8%b3%d8%b7%d9%88%d8%b1/",
        },
        "producer_maaden": {
            "https://www.maaden.com/news-insights/latest-news/maaden-fourth-quarter-and-full-year-2025-results",
            "https://axvpvthrjz64.compat.objectstorage.me-jeddah-1.oraclecloud.com/maaden-website-assets/reports/annual-reports/maaden-ar-updated-ver---mar-26-eng-ver_compressed.pdf",
        },
    }
    for source_id, urls in expected.items():
        path = root / source_id / "lists" / f"{source_id}-v1.json"
        loaded = load_document_list(
            path,
            source_id=source_id,
            default_evidence_class="C",
        )
        assert {entry.document_url for entry in loaded.entries} == urls
        assert all(entry.publisher_kind == "producer" for entry in loaded.entries)


def test_nomenclature_authority_publisher_kind_governed_and_allowed_only_target_product_identity() -> None:
    payload = document_list_payload("wco_hs_nomenclature")
    entry = payload["entries"][0]
    entry.update(
        {
            "publisher_kind": "nomenclature_authority",
            "document_kind": "other_public_document",
            "evidence_class_target": "B",
            "supports": ["TARGET_PRODUCT_IDENTITY"],
        }
    )
    validate_document_list(
        payload,
        source_id="wco_hs_nomenclature",
        default_evidence_class="B",
    )

    wrong_support = json.loads(json.dumps(payload))
    wrong_support["entries"][0]["supports"] = [
        "DOMESTIC_NAMEPLATE_CAPACITY"
    ]
    with pytest.raises(AcquisitionConfigurationError, match="supports"):
        validate_document_list(
            wrong_support,
            source_id="wco_hs_nomenclature",
            default_evidence_class="B",
        )

    wrong_kind = json.loads(json.dumps(payload))
    wrong_kind["entries"][0]["publisher_kind"] = "producer"
    with pytest.raises(AcquisitionConfigurationError, match="publisher_kind"):
        validate_document_list(
            wrong_kind,
            source_id="wco_hs_nomenclature",
            default_evidence_class="B",
        )

    producer = document_list_payload("producer_unicoil")
    producer["entries"][0]["publisher_kind"] = "nomenclature_authority"
    with pytest.raises(AcquisitionConfigurationError, match="publisher_kind"):
        validate_document_list(
            producer,
            source_id="producer_unicoil",
            default_evidence_class="C",
        )
