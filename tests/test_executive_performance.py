"""Warm executive endpoint performance contract."""

from __future__ import annotations

from statistics import median
from time import perf_counter

from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.executive.service import clear_executive_caches

WARM_MEASUREMENTS = 5
MAX_MEDIAN_MS = 250.0
EXECUTIVE_PATHS = (
    "/api/executive/summary",
    "/api/executive/opportunities/SAU-H0-721049",
)


def test_warm_executive_endpoint_medians_are_below_250_ms() -> None:
    clear_executive_caches()
    client = TestClient(app)
    for path in EXECUTIVE_PATHS:
        warmup = client.get(path)
        assert warmup.status_code == 200
        assert warmup.headers["content-type"].startswith("application/json")
        elapsed_ms: list[float] = []
        for _ in range(WARM_MEASUREMENTS):
            started = perf_counter()
            response = client.get(path)
            elapsed_ms.append((perf_counter() - started) * 1000)
            assert response.status_code == 200
            assert response.headers["content-type"].startswith(
                "application/json"
            )
        measured = median(elapsed_ms)
        assert measured < MAX_MEDIAN_MS, (
            f"{path} median {measured:.3f} ms from {elapsed_ms!r} "
            f"must be below {MAX_MEDIAN_MS:.1f} ms"
        )
