"""Public screening artifacts cannot contain synthetic or formal decisions."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT, evidence_policy_config
from ior_mvp.screening.snapshot import load_screening_snapshot_directory


def _snapshots():
    return [
        load_screening_snapshot_directory(path)
        for path in sorted(
            (PROJECT_ROOT / "data" / "screening" / "snapshots").glob("SCREENING-*")
        )
        if path.is_dir()
    ]


def test_no_synthetic_flag_true_or_demo_generator_in_screening_data_or_api():
    assert _snapshots()
    text = json.dumps(_snapshots(), sort_keys=True)
    assert '"synthetic_flag": true' not in text.lower()
    assert "DEMO_GENERATOR" not in text


def test_screening_records_have_no_formal_state_route_or_d_star():
    for snapshot in _snapshots():
        for record in snapshot["records"]:
            assert not {"state", "route_code", "d_star"} & set(record)


def test_mounted_screening_views_carry_no_synthetic_marker_in_any_mode():
    client = TestClient(app)
    summary = client.get("/api/screening")
    evidence = client.get("/api/screening/evidence")
    assert summary.status_code == evidence.status_code == 200

    payloads = [summary.json(), evidence.json()]
    for queue in summary.json()["queues"]:
        response = client.get(
            f"/api/screening/queues/{queue['queue_id']}?offset=0&limit=200"
        )
        assert response.status_code == 200
        payloads.append(response.json())
    robust = client.get(
        "/api/screening/queues/robust_public_finding?offset=0&limit=3"
    ).json()
    for entry in robust["entries"]:
        response = client.get(f"/api/screening/records/{entry['hs6']}")
        assert response.status_code == 200
        payloads.append(response.json())

    policy = evidence_policy_config()["synthetic_isolation"]
    text = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
    for forbidden in (
        '"synthetic_flag": true',
        "DEMO_GENERATOR",
        "SYN-MINISTRY",
        "scenario_id",
        policy["display_label"],
        policy["display_label_ar"],
    ):
        assert forbidden not in text
    assert client.get("/api/screening?mode=simulated").json() == summary.json()
    assert (
        client.get("/api/screening/evidence?mode=simulated").json()
        == evidence.json()
    )
