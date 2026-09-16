"""Class-D browser fixtures for explicit screening states."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ior_mvp.config import PROJECT_ROOT


FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "screening"


def _fixture(name: str) -> dict:
    path = FIXTURE_ROOT / name
    assert path.is_file()
    payload = json.loads(path.read_text(encoding="utf-8"))
    authority = payload.get("authority")
    if isinstance(authority, dict) and "thresholds_version" in authority:
        assert authority["thresholds_version"] == "1.2.0"
        authority["thresholds_version"] = "1.3.0"
    return payload


def _client() -> TestClient:
    from ior_mvp.screening.api import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_unavailable_and_partial_fixtures_match_api_output(
    monkeypatch,
) -> None:
    from ior_mvp.screening import api

    client = _client()
    unavailable_summary = _fixture("summary-unavailable.json")
    unavailable_evidence = _fixture("evidence-unavailable.json")
    empty_queue = _fixture("queue-empty.json")
    monkeypatch.setattr(
        api.repository,
        "screening_snapshot",
        lambda: None,
    )
    assert client.get("/api/screening").json() == unavailable_summary
    assert (
        client.get("/api/screening/evidence").json()
        == unavailable_evidence
    )
    assert (
        client.get(
            f"/api/screening/queues/{empty_queue['queue_id']}"
        ).json()
        == empty_queue
    )

    partial_summary = _fixture("summary-partial.json")
    partial_evidence = _fixture("evidence-partial.json")
    partial_queue = _fixture(
        "queue-partial-robust_public_finding.json"
    )
    partial_record = _fixture("record-partial-030579.json")
    queues = {
        row["queue_id"]: {
            "ordering_basis": row["ordering_basis"],
            "methodology_ref": row["methodology_ref"],
            "entries": (
                partial_queue["entries"]
                if row["queue_id"] == partial_queue["queue_id"]
                else []
            ),
        }
        for row in partial_summary["queues"]
    }
    partial_snapshot = {
        **partial_summary,
        "queues": queues,
        "evidence_passports": partial_evidence[
            "evidence_passports"
        ],
    }
    monkeypatch.setattr(
        api.repository,
        "screening_snapshot",
        lambda: partial_snapshot,
    )
    monkeypatch.setattr(
        api.repository,
        "screening_record",
        lambda hs6: (
            {
                key: value
                for key, value in partial_record.items()
                if key != "evidence_passports"
            }
            if hs6 == partial_record["hs6"]
            else None
        ),
    )
    assert client.get("/api/screening").json() == partial_summary
    assert client.get("/api/screening/evidence").json() == partial_evidence
    assert (
        client.get(
            "/api/screening/queues/robust_public_finding"
        ).json()
        == partial_queue
    )
    assert (
        client.get("/api/screening/records/030579").json()
        == partial_record
    )


def test_screening_surface_fixtures_are_portable_and_public_only() -> None:
    paths = sorted(FIXTURE_ROOT.glob("*.json"))
    assert paths
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "/home/" not in text
        assert '"synthetic_flag": true' not in text.lower()
        assert "DEMO_GENERATOR" not in text
        assert "SYN-MINISTRY" not in text
