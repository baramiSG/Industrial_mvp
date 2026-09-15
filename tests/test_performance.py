from __future__ import annotations

from statistics import median
from time import perf_counter

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app


client = TestClient(app)
WARM_MEASUREMENTS = 5
MAX_MEDIAN_MS = 250.0
OPPORTUNITY_IDS = (
    "SAU-H0-721049",
    "SAU-H0-390210",
    "SAU-H6-721061",
    "SAU-H6-721012",
    "SAU-H6-760711",
    "SAU-H6-760429",
    "SAU-H6-392010",
    "SAU-H6-294110",
    "SAU-H6-294120",
    "SAU-H6-310430",
    "SAU-H6-310510",
)
MODES = ("public", "simulated")
ANALYSIS_PATHS = (
    *(
        f"/api/opportunities?mode={mode}"
        for mode in MODES
    ),
    *(
        f"/api/opportunities/{opportunity_id}{suffix}"
        f"?mode={mode}"
        for mode in MODES
        for opportunity_id in OPPORTUNITY_IDS
        for suffix in (
            "",
            "/ui-manifest",
            "/dossier",
            "/dossier.html",
        )
    ),
)


@pytest.mark.parametrize("path", ANALYSIS_PATHS)
def test_warm_analysis_endpoint_median_is_below_250_ms(
    path: str,
) -> None:
    warmup = client.get(path)
    assert warmup.status_code == 200

    elapsed_ms: list[float] = []
    for _ in range(WARM_MEASUREMENTS):
        started = perf_counter()
        response = client.get(path)
        elapsed_ms.append(
            (perf_counter() - started) * 1000
        )
        assert response.status_code == 200

    measured_median = median(elapsed_ms)
    assert measured_median < MAX_MEDIAN_MS, (
        f"{path} median {measured_median:.3f} ms "
        f"from samples {elapsed_ms!r} "
        f"must be below {MAX_MEDIAN_MS:.1f} ms"
    )


def test_warm_mounted_screening_endpoints_median_below_250_ms() -> None:
    summary = client.get("/api/screening")
    assert summary.status_code == 200
    assert summary.headers["content-type"].startswith("application/json")
    queue = client.get(
        "/api/screening/queues/robust_public_finding?offset=0&limit=1"
    )
    assert queue.status_code == 200
    first_hs6 = queue.json()["entries"][0]["hs6"]
    paths = (
        "/api/screening",
        "/api/screening/queues/likely_false_positive?offset=0&limit=50",
        f"/api/screening/records/{first_hs6}",
        "/api/screening/evidence",
    )

    for path in paths:
        warmup = client.get(path)
        assert warmup.status_code == 200
        assert warmup.headers["content-type"].startswith("application/json")
        elapsed_ms: list[float] = []
        for _ in range(WARM_MEASUREMENTS):
            started = perf_counter()
            response = client.get(path)
            elapsed_ms.append((perf_counter() - started) * 1000)
            assert response.status_code == 200
        measured_median = median(elapsed_ms)
        assert measured_median < MAX_MEDIAN_MS, (
            f"{path} median {measured_median:.3f} ms "
            f"from samples {elapsed_ms!r} "
            f"must be below {MAX_MEDIAN_MS:.1f} ms"
        )
