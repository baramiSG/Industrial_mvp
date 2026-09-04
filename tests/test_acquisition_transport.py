"""Transport offline guard tests."""

from __future__ import annotations

import hashlib
import io
import json
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import (
    OfflineGuardViolation,
    ProductScope,
    QueryContract,
    Stage,
    UnavailableReason,
    UnavailableRecord,
    sha256_bytes,
)
from ior_mvp.acquisition.raw_store import RawStore
from ior_mvp.acquisition.source_config import acquisition_sources_config
from ior_mvp.acquisition.transport import (
    NetworkError,
    UrllibTransport,
    assert_live_permitted,
)
from tests.acquisition_doubles import DoubleConnector


PLAN4_SENTINEL = (
    "PLAN4-SENTINEL-"
    + hashlib.sha256(b"plan-4 in-memory redaction proof").hexdigest()[:24]
)
CREDENTIAL_NAME = "IOR_COMTRADE_SUBSCRIPTION_KEY"


class _FakeResponse:
    def __init__(
        self,
        *,
        status: int,
        headers: dict[str, str],
        body: bytes,
        url: str,
    ) -> None:
        self.status = status
        self._headers = headers
        self._body = body
        self._url = url

    def read(self, n: int | None = -1) -> bytes:
        if n is None or n < 0:
            return self._body
        return self._body[:n]

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    @property
    def headers(self) -> Message:
        message = Message()
        for key, value in self._headers.items():
            message[key] = value
        return message

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def _transport_config() -> dict[str, object]:
    config = acquisition_sources_config()
    guard = config["offline_guard"]
    return {
        "user_agent": "test-agent",
        "timeout_seconds": 5.0,
        "allowed_headers": guard["header_allowlist"],
        "denied_headers": guard["header_denylist"],
        "live_env_var": guard["live_env_var"],
        "environ": {"IOR_ACQUISITION_LIVE": "1"},
    }


def _credentialed_source_config() -> dict[str, object]:
    return {
        "authority": "Test",
        "access_classification": "public_open",
        "documentation_reference": "UNAVAILABLE",
        "terms_reference": "UNAVAILABLE",
        "license_capture_required": False,
        "credential_env_var": CREDENTIAL_NAME,
        "nomenclature": "HS2017",
        "reporter_code": "SAU",
        "default_evidence_class": "B",
        "default_reviewer_status": "unconfirmed_by_responsible_authority",
        "expected_content_types": ["application/json"],
        "user_agent": "test-agent",
        "recorded_on": "2026-09-04",
        "endpoint_templates": {"UNIVERSE": "http://example.invalid/universe"},
        "parameters": {
            "product_all_token": "ALL",
            "partner_world_token": "WLD",
            "reporter_token": "SAU",
            "flow_tokens": {"imports": "M"},
        },
        "pagination": {"kind": "NONE", "documentation_reference": "UNAVAILABLE", "parameters": {}},
        "rate_limit": {
            "documented_policy": "UNAVAILABLE",
            "min_interval_seconds": 2.0,
            "max_attempts": 1,
            "timeout_seconds": 5.0,
        },
    }


def _universe_contract(source_id: str = "un_comtrade") -> QueryContract:
    return QueryContract(
        source_id=source_id,
        stage=Stage.UNIVERSE,
        reporter="SAU",
        partner="0",
        flow="imports",
        product_scope=ProductScope.ALL_HS6,
        product_codes=("ALL",),
        nomenclature="HS2017",
        periods=("2024",),
    )


def _test_store(tmp_path: Path) -> RawStore:
    config = acquisition_sources_config()
    raw_store = config["raw_store"]
    return RawStore(
        tmp_path / "raw",
        max_artifact_bytes=raw_store["max_artifact_bytes_compressed"],
        max_store_bytes=raw_store["max_store_bytes_compressed"],
    )


def test_assert_live_permitted_requires_explicit_and_env() -> None:
    with pytest.raises(OfflineGuardViolation):
        assert_live_permitted(False, {}, "IOR_ACQUISITION_LIVE")
    with pytest.raises(OfflineGuardViolation):
        assert_live_permitted(True, {}, "IOR_ACQUISITION_LIVE")
    with pytest.raises(OfflineGuardViolation):
        assert_live_permitted(True, {"IOR_ACQUISITION_LIVE": "0"}, "IOR_ACQUISITION_LIVE")
    assert_live_permitted(True, {"IOR_ACQUISITION_LIVE": "1"}, "IOR_ACQUISITION_LIVE")


def test_urllib_transport_blocks_without_live(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = UrllibTransport(
        user_agent="test",
        timeout_seconds=5,
        allowed_headers=["content-type"],
        denied_headers=["authorization"],
        live_env_var="IOR_ACQUISITION_LIVE",
        environ={},
    )
    with pytest.raises(OfflineGuardViolation):
        transport.fetch("http://example.test", explicit_live=False)


def test_urllib_transport_redacts_final_url_and_filters_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = f"https://example.invalid/api?subscription-key={PLAN4_SENTINEL}"
    body = b"ok"

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status=200,
            headers={
                "Content-Type": "application/json",
                "Set-Cookie": "session=abc",
                "Authorization": "Bearer hidden",
                "ETag": '"abc"',
            },
            body=body,
            url=url,
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    transport = UrllibTransport(**_transport_config())
    result = transport.fetch(
        url,
        explicit_live=True,
        secrets=((CREDENTIAL_NAME, PLAN4_SENTINEL),),
    )
    assert PLAN4_SENTINEL not in result.final_url_redacted
    assert f"<REDACTED:{CREDENTIAL_NAME}>" in result.final_url_redacted
    assert result.headers_subset == (("content-type", "application/json"), ("etag", '"abc"'))


def test_urllib_transport_http_error_redacts_url(monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"https://example.invalid/forbidden?key={PLAN4_SENTINEL}"

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> None:
        raise urllib.error.HTTPError(
            url,
            403,
            "Forbidden",
            Message(),
            io.BytesIO(b""),
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    transport = UrllibTransport(**_transport_config())
    result = transport.fetch(
        url,
        explicit_live=True,
        secrets=((CREDENTIAL_NAME, PLAN4_SENTINEL),),
    )
    assert result.http_status == 403
    assert PLAN4_SENTINEL not in result.final_url_redacted
    assert f"<REDACTED:{CREDENTIAL_NAME}>" in result.final_url_redacted


def test_urllib_transport_url_error_redacts_message(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> None:
        raise urllib.error.URLError(f"failed for {PLAN4_SENTINEL}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    transport = UrllibTransport(**_transport_config())
    with pytest.raises(NetworkError) as exc_info:
        transport.fetch(
            "https://example.invalid/unavailable",
            explicit_live=True,
            secrets=((CREDENTIAL_NAME, PLAN4_SENTINEL),),
        )
    assert PLAN4_SENTINEL not in str(exc_info.value)
    assert f"<REDACTED:{CREDENTIAL_NAME}>" in str(exc_info.value)


def test_urllib_transport_end_to_end_credentialed_acquire_stores_redacted_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    url = f"http://example.invalid/universe?token={PLAN4_SENTINEL}"
    body = b'{"rows": [{"hs6": "721049", "value": "1"}]}'
    captured: dict[str, str] = {}

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> _FakeResponse:
        captured["authorization"] = request.headers["Authorization"]
        return _FakeResponse(
            status=200,
            headers={"Content-Type": "application/json", "ETag": '"1"'},
            body=body,
            url=url,
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    store = _test_store(tmp_path)
    transport = UrllibTransport(**_transport_config())
    connector = DoubleConnector(
        source_config=_credentialed_source_config(),
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={CREDENTIAL_NAME: PLAN4_SENTINEL},
        sleeper=lambda _seconds: None,
    )
    result = connector.acquire(_universe_contract(), max_requests=1)
    assert captured["authorization"] == f"Bearer {PLAN4_SENTINEL}"
    assert isinstance(result, tuple)
    artifacts, coverage = result
    assert coverage.status == "COMPLETE"
    contract = artifacts[0].contract
    assert contract.credential_used is True
    assert contract.credential_env_var == CREDENTIAL_NAME
    assert f"<REDACTED:{CREDENTIAL_NAME}>" in contract.endpoint_or_document
    assert PLAN4_SENTINEL not in contract.endpoint_or_document
    sentinel_bytes = PLAN4_SENTINEL.encode()
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert sentinel_bytes not in path.read_bytes()


def test_dd24_credential_echoed_body_not_stored(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    url = "http://example.invalid/universe"
    body = f'{{"token":"{PLAN4_SENTINEL}"}}'.encode()

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            body=body,
            url=url,
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    store = _test_store(tmp_path)
    transport = UrllibTransport(**_transport_config())
    connector = DoubleConnector(
        source_config=_credentialed_source_config(),
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={CREDENTIAL_NAME: PLAN4_SENTINEL},
        sleeper=lambda _seconds: None,
    )
    result = connector.acquire(_universe_contract(), max_requests=1)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.OUT_OF_SCOPE_CONTENT
    observed = result.observed_response
    assert observed is not None
    assert observed.error_type == "CredentialEchoed"
    assert observed.body_sha256 == sha256_bytes(body)
    assert observed.body_byte_count == len(body)
    run_dir = store.unit_dir(
        "un_comtrade",
        _universe_contract().query_hash(),
        "20260904T120000Z",
    )
    assert not list(run_dir.glob("page-*"))
    coverage_path = run_dir / "coverage.json"
    assert coverage_path.exists()
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    assert coverage["status"] == "INCOMPLETE"
    assert coverage["stop_reason"] == "OUT_OF_SCOPE_CONTENT"
    assert (run_dir / "attempt.json").exists()
    sentinel_bytes = PLAN4_SENTINEL.encode()
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert sentinel_bytes not in path.read_bytes()


def test_dd24_terms_capture_credential_echo_yields_license_unrecorded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source_cfg = {
        **_credentialed_source_config(),
        "terms_reference": "https://example.invalid/terms",
        "license_capture_required": True,
        "endpoint_templates": {
            "UNIVERSE": "http://example.invalid/universe",
            "TERMS": "http://example.invalid/terms",
        },
    }
    body = PLAN4_SENTINEL.encode()

    def fake_urlopen(request: urllib.request.Request, **_kwargs: object) -> _FakeResponse:
        return _FakeResponse(
            status=200,
            headers={"Content-Type": "text/html"},
            body=body,
            url=request.full_url,
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    store = _test_store(tmp_path)
    transport = UrllibTransport(**_transport_config())
    connector = DoubleConnector(
        source_config=source_cfg,
        store=store,
        transport=transport,
        run_id="20260904T120000Z",
        environ={CREDENTIAL_NAME: PLAN4_SENTINEL},
        sleeper=lambda _seconds: None,
    )
    result = connector.acquire(_universe_contract(), max_requests=2)
    assert isinstance(result, UnavailableRecord)
    assert result.reason == UnavailableReason.LICENSE_UNRECORDED
    assert not list(store.unit_dir(
        "un_comtrade",
        _universe_contract().query_hash(),
        "20260904T120000Z",
    ).glob("page-*"))
