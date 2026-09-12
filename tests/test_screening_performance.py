"""Warm screening API budget."""

from __future__ import annotations

import statistics
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_warm_screening_endpoints_median_below_250_ms():
    from ior_mvp.screening.api import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    paths = (
        "/api/screening",
        "/api/screening/queues/robust_public_finding",
        "/api/screening/records/000000",
    )
    for path in paths:
        client.get(path)
    for path in paths:
        elapsed = []
        for _ in range(15):
            started = time.perf_counter()
            client.get(path)
            elapsed.append((time.perf_counter() - started) * 1000)
        assert statistics.median(elapsed) < 250.0
