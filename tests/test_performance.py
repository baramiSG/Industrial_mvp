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
