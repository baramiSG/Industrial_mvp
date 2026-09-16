"""Runtime screening loader and API contracts."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _client():
    from ior_mvp.screening.api import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def _isolate_repository_caches():
    from ior_mvp.screening import repository

    cached_names = (
        "_screening_directory",
        "screening_snapshot",
        "_screening_shard",
    )
    for name in cached_names:
        clear = getattr(getattr(repository, name), "cache_clear", None)
        if clear is not None:
            clear()
    yield
    for name in cached_names:
        clear = getattr(getattr(repository, name), "cache_clear", None)
        if clear is not None:
            clear()


def test_loader_lru_cache_and_fail_closed_on_invalid_snapshot(tmp_path, monkeypatch):
    from ior_mvp.screening import repository

    root = tmp_path / "snapshots"
    bad = root / "SCREENING-BAD"
    bad.mkdir(parents=True)
    (bad / "summary.json").write_text("{}")
    monkeypatch.setattr(repository, "SNAPSHOT_ROOT", root)
    repository.clear_screening_caches()
    with pytest.raises(ValueError):
        repository.screening_snapshot()


def test_latest_snapshot_selected_by_as_of_date_then_snapshot_id(
    tmp_path, monkeypatch
):
    from ior_mvp.screening import repository

    root = tmp_path / "snapshots"
    older = root / "SCREENING-Z-OLDER"
    newer_a = root / "SCREENING-A-NEWER"
    newer_b = root / "SCREENING-B-NEWER"
    for path in (older, newer_a, newer_b):
        path.mkdir(parents=True)
    summaries = {
        older: {"as_of_date": "2026-09-11", "snapshot_id": "SCREENING-Z"},
        newer_a: {"as_of_date": "2026-09-12", "snapshot_id": "SCREENING-A"},
        newer_b: {"as_of_date": "2026-09-12", "snapshot_id": "SCREENING-B"},
    }
    monkeypatch.setattr(repository, "SNAPSHOT_ROOT", root)
    monkeypatch.setattr(
        repository,
        "load_screening_summary_directory",
        lambda path: summaries[path],
    )
    repository.clear_screening_caches()
    assert repository._screening_directory() == newer_b


def test_import_api_does_not_load_acquisition_transport():
    for name in list(sys.modules):
        if name.startswith("ior_mvp.screening") or name == "ior_mvp.acquisition.transport":
            sys.modules.pop(name)
    importlib.import_module("ior_mvp.screening.api")
    assert "ior_mvp.acquisition.transport" not in sys.modules


def test_summary_contract_and_authority_versions():
    payload = _client().get("/api/screening").json()
    assert payload["synthetic_flag"] is False
    assert payload["authority"] == {
        "screening_config_version": "1.0.0",
        "thresholds_version": "1.3.0",
        "product_families_version": "1.2.0",
        "acquisition_config_version": "1.3.0",
    }


def test_queue_pagination_clamps_to_config_and_404_unknown_queue():
    client = _client()
    response = client.get("/api/screening/queues/not-a-queue")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "QUEUE_NOT_FOUND"
    response = client.get(
        "/api/screening/queues/robust_public_finding?limit=99999"
    )
    assert response.status_code == 200
    assert response.json()["limit"] == 200


def test_record_drilldown_contract_and_404_unknown_hs6():
    response = _client().get("/api/screening/records/000000")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "RECORD_NOT_FOUND"


def test_missing_snapshot_serves_200_unavailable_never_500(monkeypatch):
    from ior_mvp.screening import api

    monkeypatch.setattr(api.repository, "screening_snapshot", lambda: None)
    response = _client().get("/api/screening")
    assert response.status_code == 200
    assert response.json()["universe_status"]["status"] == "UNAVAILABLE"


def test_router_mounts_on_test_app_with_prefix():
    assert _client().get("/api/screening").status_code == 200


def test_screening_api_records_endpoint_reads_shard_lazily(
    tmp_path, monkeypatch
):
    from ior_mvp.screening import repository
    from ior_mvp.screening.config import screening_config
    from ior_mvp.screening.inputs import ScreeningInputs
    from ior_mvp.screening.snapshot import (
        build_screening_snapshot,
        write_screening_snapshot,
    )

    rows = []
    for year in (2021, 2022, 2023, 2024):
        for flow in ("imports", "exports"):
            for hs6 in ("390210", "721049"):
                rows.append(
                    {
                        "year": year,
                        "flow": flow,
                        "hs6": hs6,
                        "trade_value": 1_000_000,
                        "net_weight": 1_000_000,
                        "hs_revision": "H6",
                        "source_evidence_id": f"E-{year}-{flow}-{hs6}",
                    }
                )
    universe = {
        "snapshot_id": "U-LAZY",
        "as_of_date": "2026-09-12",
        "source_id": "un_comtrade",
        "flows": ["imports", "exports"],
        "coverage": {"units": []},
        "rows": rows,
        "evidence": [],
    }
    inputs = ScreeningInputs(
        universe=universe,
        partners=None,
        tariff=None,
        entities=None,
        family_links={"entries": []},
        inputs_block={
            "universe_snapshots": [],
            "partner_snapshots": [],
            "tariff_snapshots": [],
            "entity_artifacts": [],
            "plant_family_links": [],
            "configs": [],
        },
        unavailable_reasons=(),
    )
    root = tmp_path / "snapshots"
    snapshot_path = write_screening_snapshot(
        build_screening_snapshot(inputs, screening_config()), root
    )
    monkeypatch.setattr(repository, "SNAPSHOT_ROOT", root)
    repository.clear_screening_caches()
    opened: list[str] = []
    original_text = Path.read_text
    original_bytes = Path.read_bytes

    def track(path: Path) -> None:
        if snapshot_path in path.parents:
            opened.append(path.relative_to(snapshot_path).as_posix())

    def tracked_text(path: Path, *args, **kwargs):
        track(path)
        return original_text(path, *args, **kwargs)

    def tracked_bytes(path: Path, *args, **kwargs):
        track(path)
        return original_bytes(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", tracked_text)
    monkeypatch.setattr(Path, "read_bytes", tracked_bytes)
    response = _client().get("/api/screening/records/721049")
    assert response.status_code == 200
    assert "records/72.json" in opened
    assert "records/39.json" not in opened


def _frozen_summary() -> dict:
    from ior_mvp.config import PROJECT_ROOT

    path = (
        PROJECT_ROOT
        / "data"
        / "screening"
        / "snapshots"
        / "SCREENING-SAU-2026-09-12-9b6b22032fd8"
        / "summary.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_route_returns_eight_universe_passports_verbatim():
    expected = _frozen_summary()
    response = _client().get("/api/screening/evidence")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "snapshot_id",
        "as_of_date",
        "source_boundary",
        "synthetic_flag",
        "evidence_passports",
        "universe_units",
        "authority",
    }
    assert payload["snapshot_id"] == "SCREENING-SAU-2026-09-12-9b6b22032fd8"
    assert payload["source_boundary"] == "public"
    assert payload["synthetic_flag"] is False
    assert payload["evidence_passports"] == expected["evidence_passports"]
    assert payload["universe_units"] == expected["universe_status"]["units"]
    assert [list(row) for row in payload["evidence_passports"]] == [
        list(row) for row in expected["evidence_passports"]
    ]
    assert [list(row) for row in payload["universe_units"]] == [
        list(row) for row in expected["universe_status"]["units"]
    ]
    assert [row["passport_id"] for row in payload["evidence_passports"]] == [
        "un_comtrade-37d131466dff-20260912T143742Z",
        "un_comtrade-3f892bf254a9-20260912T143742Z",
        "un_comtrade-464c4f670ca8-20260912T143742Z",
        "un_comtrade-5bc875b4a56b-20260912T143742Z",
        "un_comtrade-6b9efd5f68db-20260912T143742Z",
        "un_comtrade-7a7ebf8cf5ab-20260912T143742Z",
        "un_comtrade-a3cc3f1befa0-20260912T143742Z",
        "un_comtrade-ceec907cc0b6-20260912T143742Z",
    ]
    assert payload["authority"] == {
        "screening_config_version": "1.0.0",
        "thresholds_version": "1.3.0",
        "product_families_version": "1.2.0",
        "acquisition_config_version": "1.3.0",
    }


def test_evidence_route_without_snapshot_is_explicit(monkeypatch):
    from ior_mvp.screening import api

    monkeypatch.setattr(api.repository, "screening_snapshot", lambda: None)
    response = _client().get("/api/screening/evidence")

    assert response.status_code == 200
    assert response.json() == {
        "snapshot_id": None,
        "as_of_date": None,
        "source_boundary": "public",
        "synthetic_flag": False,
        "evidence_passports": [],
        "universe_units": [],
        "reason_codes": ["NO_SCREENING_SNAPSHOT"],
        "authority": {
            "screening_config_version": "1.0.0",
            "thresholds_version": "1.3.0",
            "product_families_version": "1.2.0",
            "acquisition_config_version": "1.3.0",
        },
    }


def test_evidence_route_ignores_mode_and_carries_no_synthetic_flag_true():
    client = _client()
    public = client.get("/api/screening/evidence")
    simulated = client.get("/api/screening/evidence?mode=simulated")

    assert public.status_code == simulated.status_code == 200
    assert simulated.json() == public.json()
    for forbidden in (
        '"synthetic_flag":true',
        "DEMO_GENERATOR",
        "SYN-MINISTRY",
        "scenario_id",
    ):
        assert forbidden not in public.text


def test_existing_three_route_key_sets_are_unchanged():
    from ior_mvp.screening import repository

    client = _client()
    summary_payload = client.get("/api/screening").json()
    queue_payload = client.get(
        "/api/screening/queues/robust_public_finding?offset=0&limit=1"
    ).json()
    record_payload = client.get("/api/screening/records/030579").json()
    loaded_record = repository.screening_record("030579")

    assert set(summary_payload) == {
        "snapshot_id",
        "as_of_date",
        "universe_status",
        "coverage_accounting",
        "counts",
        "queues",
        "methodology_queue_mapping",
        "unqueued_candidates",
        "authority",
        "synthetic_flag",
    }
    assert set(queue_payload) == {
        "queue_id",
        "total",
        "offset",
        "limit",
        "ordering_basis",
        "entries",
    }
    assert loaded_record is not None
    assert set(record_payload) == set(loaded_record) | {"evidence_passports"}
