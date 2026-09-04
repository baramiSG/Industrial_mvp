"""Network transport with offline guard — sole network module in acquisition."""

from __future__ import annotations

import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Mapping, Protocol, Sequence

from .contracts import (
    AcquisitionError,
    OfflineGuardViolation,
    UnavailableReason,
    sha256_bytes,
    utc_now_iso,
)
from .raw_store import redact_text


class NetworkError(AcquisitionError):
    """Transport-level network failure."""


class SizeBudgetExceeded(AcquisitionError):
    """Response body exceeds configured budget before read."""


@dataclass(frozen=True)
class FetchResult:
    http_status: int
    headers_subset: tuple[tuple[str, str], ...]
    body: bytes
    final_url_redacted: str
    fetched_at: str
    content_length_header: int | None


class Transport(Protocol):
    """Protocol for injectable transport (live or fake)."""

    def fetch(
        self,
        url: str,
        *,
        explicit_live: bool,
        headers: Mapping[str, str] | None = None,
        method: str = "GET",
        secrets: Sequence[tuple[str, str]] = (),
        max_body_bytes: int | None = None,
    ) -> FetchResult:
        """Fetch one URL with offline guard and redaction."""


def assert_live_permitted(
    explicit_live: bool,
    environ: Mapping[str, str],
    live_env_var: str,
) -> None:
    """Raise OfflineGuardViolation unless operator live access is permitted."""
    if not explicit_live:
        raise OfflineGuardViolation(
            "Live acquisition requires explicit_live=True"
        )
    if environ.get(live_env_var) != "1":
        raise OfflineGuardViolation(
            f"Environment variable {live_env_var} must equal '1'"
        )


def _filter_headers(
    headers: Mapping[str, str],
    allowed: Sequence[str],
    denied: Sequence[str],
) -> tuple[tuple[str, str], ...]:
    allowed_lower = {name.lower() for name in allowed}
    denied_lower = {name.lower() for name in denied}
    result: list[tuple[str, str]] = []
    for name, value in headers.items():
        lowered = name.lower()
        if lowered in denied_lower:
            continue
        if lowered in allowed_lower:
            result.append((lowered, value))
    return tuple(sorted(result))


class UrllibTransport:
    """Production transport using urllib with TLS verification."""

    def __init__(
        self,
        *,
        user_agent: str,
        timeout_seconds: float,
        allowed_headers: Sequence[str],
        denied_headers: Sequence[str],
        live_env_var: str,
        environ: Mapping[str, str] | None = None,
        clock: datetime | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.allowed_headers = allowed_headers
        self.denied_headers = denied_headers
        self.live_env_var = live_env_var
        self.environ = environ if environ is not None else {}
        self.clock = clock

    def fetch(
        self,
        url: str,
        *,
        explicit_live: bool,
        headers: Mapping[str, str] | None = None,
        method: str = "GET",
        secrets: Sequence[tuple[str, str]] = (),
        max_body_bytes: int | None = None,
    ) -> FetchResult:
        assert_live_permitted(explicit_live, self.environ, self.live_env_var)
        request_headers = {"User-Agent": self.user_agent}
        if headers:
            request_headers.update(headers)

        req = urllib.request.Request(url, method=method, headers=request_headers)
        context = ssl.create_default_context()

        try:
            with urllib.request.urlopen(
                req,
                timeout=self.timeout_seconds,
                context=context,
            ) as response:
                content_length_raw = response.headers.get("Content-Length")
                content_length = (
                    int(content_length_raw)
                    if content_length_raw is not None
                    else None
                )
                if (
                    max_body_bytes is not None
                    and content_length is not None
                    and content_length > max_body_bytes
                ):
                    raise SizeBudgetExceeded(
                        UnavailableReason.SIZE_BUDGET_EXCEEDED.value
                    )
                body = response.read(
                    max_body_bytes + 1 if max_body_bytes else None
                )
                if max_body_bytes is not None and len(body) > max_body_bytes:
                    raise SizeBudgetExceeded(
                        UnavailableReason.SIZE_BUDGET_EXCEEDED.value
                    )
                if (
                    content_length is not None
                    and len(body) != content_length
                ):
                    raise NetworkError(
                        "Content-Length does not match body length"
                    )
                status = getattr(response, "status", response.getcode())
                header_map = {
                    key.lower(): value
                    for key, value in response.headers.items()
                }
                filtered = _filter_headers(
                    header_map,
                    self.allowed_headers,
                    self.denied_headers,
                )
                final_url = redact_text(response.geturl(), tuple(secrets))
                return FetchResult(
                    http_status=int(status),
                    headers_subset=filtered,
                    body=body,
                    final_url_redacted=final_url,
                    fetched_at=utc_now_iso(self.clock),
                    content_length_header=content_length,
                )
        except urllib.error.HTTPError as exc:
            header_map = {
                key.lower(): value for key, value in exc.headers.items()
            }
            filtered = _filter_headers(
                header_map,
                self.allowed_headers,
                self.denied_headers,
            )
            body = exc.read() if exc.fp else b""
            final_url = redact_text(exc.geturl(), tuple(secrets))
            return FetchResult(
                http_status=int(exc.code),
                headers_subset=filtered,
                body=body,
                final_url_redacted=final_url,
                fetched_at=utc_now_iso(self.clock),
                content_length_header=(
                    int(exc.headers.get("Content-Length"))
                    if exc.headers.get("Content-Length")
                    else None
                ),
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            message = redact_text(str(exc), tuple(secrets))
            raise NetworkError(message) from exc
