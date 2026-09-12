"""Raw store write-once and budget tests."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import (
    CoverageRecord,
    CompletenessBasis,
    PageMeta,
    ProductScope,
    QueryContract,
    RawStoreIntegrityError,
    SourceContractRecord,
    Stage,
    UnavailableRecord,
    UnavailableReason,
    sha256_bytes,
)
from ior_mvp.acquisition.raw_store import RawStore, deterministic_gzip, redact_text
from ior_mvp.config import PROJECT_ROOT


def _contract(**kwargs: object) -> SourceContractRecord:
    qc = QueryContract(
        source_id="wits_trade",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )
    defaults = {
        "source_id": "wits_trade",
        "authority": "WITS",
        "access_classification": "public_open",
        "endpoint_or_document": "http://example.test",
        "query_contract": qc,
        "reporter": "SAU",
        "partner": "WLD",
        "flow": "imports",
        "product_code": "ALL",
        "product_scope": "ALL_HS6",
        "nomenclature": "H0",
        "period": "2024",
        "retrieved_at": "2026-09-04T00:00:00Z",
        "source_refresh_date": "2026-09-04",
        "raw_file_path": "",
        "sha256": sha256_bytes(b"payload"),
        "license_or_usage_note": "UNAVAILABLE",
        "query_hash": qc.query_hash(),
        "run_id": "20260904T000000Z",
        "page_index": 1,
        "page_meta": PageMeta(1, 1, False, 1, None),
        "compressed_sha256": "",
        "byte_count": 7,
        "content_type": "application/json",
        "http_status": 200,
        "response_headers_subset": (("content-type", "application/json"),),
        "credential_env_var": None,
        "credential_used": False,
        "normalization_status": "PENDING",
        "normalization_reason": None,
    }
    defaults.update(kwargs)
    return SourceContractRecord(**defaults)  # type: ignore[arg-type]


def test_deterministic_gzip_identical() -> None:
    payload = b'{"test": true}'
    assert deterministic_gzip(payload) == deterministic_gzip(payload)
    import gzip

    assert gzip.decompress(deterministic_gzip(payload)) == payload


def test_write_page_and_write_once(tmp_path: Path) -> None:
    root = tmp_path / "raw"
    store = RawStore(root, max_artifact_bytes=1024, max_store_bytes=4096)
    contract = _contract()
    payload = b"payload"
    contract = SourceContractRecord(
        **{
            **contract.__dict__,
            "sha256": sha256_bytes(payload),
        }
    )
    store.write_page(payload, contract)
    with pytest.raises(RawStoreIntegrityError):
        store.write_page(b"different", contract)


def test_rejects_test_double_under_repo_data(tmp_path: pytest.TempPathFactory) -> None:
    root = PROJECT_ROOT / "data" / "raw"
    store = RawStore(root, max_artifact_bytes=1024, max_store_bytes=4096)
    contract = _contract(access_classification="test_double")
    with pytest.raises(RawStoreIntegrityError):
        store.write_page(b"x", contract)


def test_redact_text() -> None:
    result = redact_text(
        "secret=abc123",
        (("KEY", "abc123"),),
    )
    assert "<REDACTED:KEY>" in result


def test_content_extension_mapping() -> None:
    from ior_mvp.acquisition.raw_store import _content_extension

    assert _content_extension("application/pdf") == "pdf"
    assert _content_extension("application/x-pdf") == "pdf"
    assert _content_extension("text/plain") == "txt"
    assert _content_extension("text/plain; charset=utf-8") == "txt"
    assert _content_extension("application/json") == "json"
    assert _content_extension("text/html") == "html"
    assert _content_extension("application/zip") == "zip"
    assert _content_extension("text/csv") == "csv"
    assert _content_extension("application/octet-stream") == "bin"


def test_latest_runs_selects_greatest_run_id(tmp_path: Path) -> None:
    root = tmp_path / "raw"
    store = RawStore(root, max_artifact_bytes=1024, max_store_bytes=4096)
    qc = QueryContract(
        source_id="wits_trade",
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="WLD",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="H0",
        periods=("2024",),
    )
    for run_id in ("20260904T000000Z", "20260904T010000Z"):
        cov = CoverageRecord(
            source_id="wits_trade",
            stage=Stage.UNIVERSE,
            query_hash=qc.query_hash(),
            run_id=run_id,
            unit_key=("imports", "2024"),
            unit={},
            pages_fetched=1,
            pages_expected=1,
            requests_made=1,
            status="COMPLETE",
            completeness_basis=CompletenessBasis.SINGLE_RESPONSE_NO_PAGINATION,
            stop_reason=None,
            missing_pages=(),
            observed_stop=None,
        )
        store.write_coverage(cov)
    selected = store.latest_runs(source_id="wits_trade", stage="UNIVERSE")
    assert selected[("imports", "2024")][0].run_id == "20260904T010000Z"
    assert selected[("imports", "2024")][1] == ("20260904T000000Z",)


def test_attempt_and_coverage_records_are_write_once(tmp_path: Path) -> None:
    store = RawStore(
        tmp_path / "raw", max_artifact_bytes=1024, max_store_bytes=4096
    )
    contract = _contract().query_contract
    coverage = CoverageRecord(
        source_id="wits_trade",
        stage=Stage.UNIVERSE,
        query_hash=contract.query_hash(),
        run_id="20260904T000000Z",
        unit_key=("imports", "2024"),
        unit={},
        pages_fetched=0,
        pages_expected=0,
        requests_made=0,
        status="INCOMPLETE",
        completeness_basis=CompletenessBasis.UNAVAILABLE,
        stop_reason=UnavailableReason.COVERAGE_INDETERMINATE,
        missing_pages=(),
        observed_stop=None,
    )
    attempt = UnavailableRecord(
        source_id="wits_trade",
        query_contract=contract,
        query_hash=contract.query_hash(),
        run_id="20260904T000000Z",
        attempted_at="2026-09-04T00:00:00Z",
        reason=UnavailableReason.COVERAGE_INCOMPLETE,
        observed_response=None,
        endpoint_or_document="http://example.test",
        credential_env_var=None,
        credential_present=False,
        coverage=coverage,
    )

    store.write_coverage(coverage)
    store.write_unavailable(attempt)

    with pytest.raises(RawStoreIntegrityError, match="Write-once conflict"):
        store.write_coverage(replace(coverage, requests_made=1))
    with pytest.raises(RawStoreIntegrityError, match="Write-once conflict"):
        store.write_unavailable(
            replace(attempt, reason=UnavailableReason.NETWORK_ERROR)
        )
