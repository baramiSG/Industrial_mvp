"""Institutional framework tests use fake Class D responses and real storage."""

import json
from dataclasses import replace

import pytest

from ior_mvp.acquisition import repository, snapshots, harmonise
from ior_mvp.acquisition.connectors.base import ConnectorRegistry, RequestBudget
from ior_mvp.acquisition.contracts import AcquisitionUnavailable, Stage, UnavailableReason, unit_key
from ior_mvp.acquisition.coverage import not_attempted_coverage
from ior_mvp.acquisition.passports import assert_passport_complete
from ior_mvp.acquisition.pipeline import plan_units
from ior_mvp.acquisition.transport import FetchResult
from tests.acquisition_doubles import FakeTransport, InstitutionalDouble, institutional_config, seed_unit
from tests.test_acquisition_snapshots import _fixture, _temp_store

CASES = [
    ("gastat", "AGGREGATE", "production", "DOMESTIC_PRODUCTION_AGGREGATE", "PRODUCTION-SAU-GASTAT"),
    ("ministry_of_industry", "DIRECTORY", "directory", "ESTABLISHMENT_LICENCE_DIRECTORY", "DIRECTORY-SAU-MINISTRY-OF-INDUSTRY"),
    ("modon", "DIRECTORY", "directory", "ESTABLISHMENT_LICENCE_DIRECTORY", "DIRECTORY-SAU-MODON"),
    ("saso_catalogue", "REGISTRY", "registry", "STANDARD_CONFORMITY_REGISTRY", "REGISTRY-SAU-SASO-CATALOGUE"),
    ("saber_registry", "REGISTRY", "registry", "STANDARD_CONFORMITY_REGISTRY", "REGISTRY-SAU-SABER-REGISTRY"),
]


def setup(tmp_path, source, stage_name):
    stage = Stage(stage_name)
    config = institutional_config(source, stage)
    units = plan_units(stage, source_id=source, years=(2024,), flows=(), candidates=None, config=config)
    return config, _temp_store(tmp_path), units, ConnectorRegistry({source: InstitutionalDouble})


@pytest.mark.parametrize("source,stage,kind,support,prefix", CASES)
@pytest.mark.parametrize("version", ["1.1.0", "arbitrary-other-version"])
def test_institutional_snapshot_round_trip_exclusions_and_provenance(tmp_path, source, stage, kind, support, prefix, version):
    config, store, (contract, excluded), registry = setup(tmp_path, source, stage)
    config["metadata"]["version"] = version
    payload = _fixture(f"test_double_{kind}_rows.json")
    if source == "saber_registry":
        payload = payload.replace(b"saso_catalogue", b"saber_registry")
    seed_unit(store, contract=contract, run_id="20260904T120000Z", payload=payload, source_config=config["sources"][source])
    store.write_coverage(not_attempted_coverage(excluded, run_id="20260904T120000Z", stop_reason=UnavailableReason.ENDPOINT_UNVERIFIED))
    record = snapshots.build_row_snapshot(store, config, registry, kind=kind, source_id=source)
    assert record["snapshot_id"] == prefix + "-2026-09-04"
    assert record["quality_summary"] == "PASS"
    assert record["coverage"]["stage"] == stage
    assert record["coverage"]["units_complete"] == 1
    assert record["coverage"]["units_excluded"] == record["transformation_record"]["exclusions"]
    assert record["coverage"]["units_excluded"][0]["unit_key"] == list(unit_key(excluded))
    assert record["transformation_record"]["config_version"] == "1.1.0"
    assert record["transformation_record"]["pipeline_version"] == "1.0.0"
    for passport in record["evidence"]:
        assert_passport_complete(passport)
        assert passport["supports"] == [support] and passport["evidence_class"] == "D"
        assert passport["source_identity"]["access_classification"] == "test_double"
        assert passport["transformation_record"]["config_version"] == "1.1.0"
    rows = record["rows"]
    if kind == "production":
        assert rows[0]["indicator_text"] == "اختبار أ"
        numeric = next(row for row in rows if row["value"] is not None)
        assert numeric["value"] == 12.5 and numeric["value_original_text"] == "12.50"
        assert rows[0]["product_code_text"] == "UNAVAILABLE"
    else:
        assert [row["source_record_id"] for row in rows] == ["TEST-1", "TEST-2"]
    forbidden = {"nameplate", "capacity", "capacity_value", "compliance_confirmed", "qualified", "approved", "person_name", "phone", "email"}
    assert all(not forbidden.intersection(row) for row in rows)
    originals = json.loads(payload)["rows"]
    arabic_field = {"production": "indicator_text", "directory": "entity_name_ar", "registry": "title_ar"}[kind]
    assert {row[arabic_field].encode() for row in rows} == {row[arabic_field].encode() for row in originals}
    snapshots.validate_snapshot(record, allow_test_double=True)
    path = snapshots.write_snapshot(record, tmp_path, allow_test_double=True)
    assert repository.acquired_snapshots(kind, data_root=tmp_path, allow_test_double=True)[record["snapshot_id"]] == json.loads(path.read_text())
    assert snapshots.reconstruct(path, store, config, registry).match
    seed_unit(store, contract=contract, run_id="20260905T120000Z", payload=payload, source_config=config["sources"][source])
    assert snapshots.reconstruct(path, store, config, registry).detail["reason"] == "SELECTION_CHANGED"


@pytest.mark.parametrize("source,stage,kind,support,prefix", CASES)
@pytest.mark.parametrize("identity", ["UNAVAILABLE", "", "unknown"])
def test_institutional_unknown_unit_refuses_before_terms_budget_or_transport(tmp_path, source, stage, kind, support, prefix, identity):
    config, store, (contract, _), registry = setup(tmp_path, source, stage)
    cfg = config["sources"][source]
    cfg["endpoint_templates"][stage] = "https://example.test/no-unit-token"
    cfg["license_capture_required"] = True
    budget = RequestBudget(2)
    transport = FakeTransport({}, [])
    connector = registry.get(source, source_config=cfg, store=store, transport=transport, run_id="20260904T120000Z", environ={}, request_budget=budget)
    result = connector.acquire(replace(contract, parameters=(("unit", identity),)), max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert result.coverage.requests_made == 0
    assert budget.used == 0 and transport.calls == [] and transport.request_headers == []


def test_partial_directory_never_builds_snapshot_and_complete_pair_does(tmp_path):
    config, store, (contract, _), registry = setup(tmp_path, "modon", "DIRECTORY")
    first = _fixture("test_double_directory_page1_of_2.json")
    second = _fixture("test_double_directory_page2_of_2.json")
    transport = FakeTransport({f"https://example.test/data?page={page}": FetchResult(200, (("content-type", "application/json"),), body, f"https://example.test/data?page={page}", "2026-09-04T00:00:00Z", len(body)) for page, body in [(1, first), (2, second)]}, [])
    connector = registry.get("modon", source_config=config["sources"]["modon"], store=store, transport=transport, run_id="20260904T120000Z", environ={})
    result = connector.acquire(contract, max_requests=1)
    assert result.reason == UnavailableReason.MAX_REQUESTS_EXHAUSTED
    assert transport.calls == ["https://example.test/data?page=1"]
    with pytest.raises(AcquisitionUnavailable):
        snapshots.build_row_snapshot(store, config, registry, kind="directory", source_id="modon")
    connector.run_id = "20260905T120000Z"
    connector.acquire(contract, max_requests=2)
    assert len(snapshots.build_row_snapshot(store, config, registry, kind="directory", source_id="modon")["rows"]) == 2


def test_equal_parameter_values_do_not_supersede_different_named_units(tmp_path):
    config, store, (contract, _), registry = setup(tmp_path, "modon", "DIRECTORY")
    for index, parameters in enumerate([(("directory", "same"),), (("catalogue", "same"),)]):
        seed_unit(store, contract=replace(contract, parameters=parameters), run_id=f"2026090{index + 4}T120000Z", payload=_fixture("test_double_directory_rows.json"), source_config=config["sources"]["modon"])
    latest = store.latest_runs(source_id="modon", stage="DIRECTORY")
    assert len(latest) == 2
    assert all(not superseded for _, superseded in latest.values())
    assert {tuple(store.pages_for("modon", cov.query_hash, cov.run_id)[0].query_contract.parameters) for cov, _ in latest.values()} == {(("directory", "same"),), (("catalogue", "same"),)}


@pytest.mark.parametrize("stage,kind,payload", [("AGGREGATE", "production", {"geography_text": "USA", "indicator_text": "TEST"}), ("DIRECTORY", "directory", {}), ("REGISTRY", "registry", {})])
def test_builder_calls_actual_institutional_validation(tmp_path, stage, kind, payload):
    config, store, (contract, _), registry = setup(tmp_path, "TEST-FIXTURE", stage)
    seed_unit(store, contract=contract, run_id="20260904T120000Z", payload=json.dumps({"rows": [payload]}).encode(), source_config=config["sources"]["TEST-FIXTURE"])
    with pytest.raises(AcquisitionUnavailable):
        snapshots.build_row_snapshot(store, config, registry, kind=kind, source_id="TEST-FIXTURE")


def test_mappers_preserve_text_and_discard_forbidden_fields():
    assert hasattr(harmonise, "directory_row_from_row"), "institutional mapper missing"
    raw = json.loads(_fixture("test_double_directory_personal_fields.json"))["rows"][0]
    row = harmonise.directory_row_from_row(raw, field_map={}, source_evidence_id="TEST-evidence").__dict__
    assert row["capacity_text"] == "١٢٫٥ طن — نص وهمي"
    assert not {"email", "phone", "person_name", "capacity", "nameplate"}.intersection(row)
    row = harmonise.registry_row_from_row({"registry": "saber_registry", "qualified": True, "approved": True, "compliance_confirmed": True}, field_map={}, source_evidence_id="TEST-evidence").__dict__
    assert not {"qualified", "approved", "compliance_confirmed"}.intersection(row)


@pytest.mark.parametrize("kind,stage", [("production", "AGGREGATE"), ("directory", "DIRECTORY"), ("registry", "REGISTRY")])
def test_snapshot_validator_refuses_institutional_row_shape_and_extra_fields(tmp_path, kind, stage):
    config, store, (contract, _), registry = setup(tmp_path, "TEST-FIXTURE", stage)
    seed_unit(store, contract=contract, run_id="20260904T120000Z", payload=_fixture(f"test_double_{kind}_rows.json"), source_config=config["sources"]["TEST-FIXTURE"])
    record = snapshots.build_row_snapshot(store, config, registry, kind=kind, source_id="TEST-FIXTURE")
    for rows in [[], [{}], [{**record["rows"][0], "email": "fake@example.test"}], [{**record["rows"][0], "source_evidence_id": None}]]:
        with pytest.raises(ValueError):
            snapshots.validate_snapshot({**record, "rows": rows}, allow_test_double=True)


def test_production_mapper_uses_only_attributable_numeric_value():
    assert hasattr(harmonise, "production_observation_from_row"), "production mapper missing"
    mapper = harmonise.production_observation_from_row
    obs = mapper({"printed": " 12.50 ", "numeric": 12.5, "capacity": 900}, field_map={"value_original_text": "printed", "value": "numeric"}, source_evidence_id="TEST")
    assert obs.value == 12.5 and obs.value_original_text == " 12.50 "
    assert mapper({"capacity": 900}, field_map={}, source_evidence_id="TEST").value is None
    assert mapper({"value_original_text": "17.5"}, field_map={}, source_evidence_id="TEST").value == 17.5
    for value in [True, float("inf"), float("nan"), {"value": 5}]:
        with pytest.raises(ValueError):
            mapper({"value": value}, field_map={}, source_evidence_id="TEST")


@pytest.mark.parametrize("kind", ["production", "directory", "registry"])
def test_default_institutional_repository_wrappers_use_kind_cache(kind):
    loader = getattr(repository, f"{kind}_snapshots", None)
    assert loader is not None, "institutional repository wrapper missing"
    repository.clear_acquisition_caches()
    assert loader() is repository.acquired_snapshots(kind)


@pytest.mark.parametrize("stage", ["AGGREGATE", "DIRECTORY", "REGISTRY"])
def test_unavailable_unit_config_remains_refusible_without_placeholder(tmp_path, stage):
    config, store, _, registry = setup(tmp_path, "TEST-FIXTURE", stage)
    cfg = config["sources"]["TEST-FIXTURE"]
    cfg["parameters"]["units"] = "UNAVAILABLE"
    cfg["endpoint_templates"][stage] = "https://example.test/no-placeholder"
    cfg["license_capture_required"] = True
    (contract,) = plan_units(Stage(stage), source_id="TEST-FIXTURE", years=(2024,), flows=(), candidates=None, config=config)
    budget = RequestBudget(2)
    transport = FakeTransport({}, [])
    connector = registry.get("TEST-FIXTURE", source_config=cfg, store=store, transport=transport, run_id="20260904T120000Z", environ={}, request_budget=budget)
    result = connector.acquire(contract, max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert contract.parameters == (("unit", "UNAVAILABLE"),)
    assert budget.used == 0 and not transport.calls and not transport.request_headers


@pytest.mark.parametrize("period", ["", "UNAVAILABLE"])
def test_aggregate_unobserved_period_never_consumes_budget(tmp_path, period):
    config, store, (contract, _), registry = setup(tmp_path, "TEST-FIXTURE", "AGGREGATE")
    transport = FakeTransport({}, [])
    budget = RequestBudget(2)
    connector = registry.get("TEST-FIXTURE", source_config=config["sources"]["TEST-FIXTURE"], store=store, transport=transport, run_id="20260904T120000Z", environ={}, request_budget=budget)
    result = connector.acquire(replace(contract, periods=(period,)), max_requests=2)
    assert result.reason == UnavailableReason.ENDPOINT_UNVERIFIED
    assert budget.used == 0 and transport.calls == []


def test_institutional_credential_refusal_precedes_unknown_identity(tmp_path):
    config, store, (contract, _), registry = setup(tmp_path, "TEST-FIXTURE", "DIRECTORY")
    cfg = config["sources"]["TEST-FIXTURE"]
    cfg["credential_env_var"] = "TEST_MISSING_KEY"
    transport = FakeTransport({}, [])
    connector = registry.get("TEST-FIXTURE", source_config=cfg, store=store, transport=transport, run_id="20260904T120000Z", environ={})
    result = connector.acquire(replace(contract, parameters=(("unit", "unknown"),)), max_requests=1)
    assert result.reason == UnavailableReason.CREDENTIAL_ABSENT and not transport.calls


@pytest.mark.parametrize("source,stage,kind,support,prefix", CASES)
@pytest.mark.parametrize("operation", ["validate", "write", "load"])
def test_real_source_id_cannot_hide_test_double_passport(tmp_path, source, stage, kind, support, prefix, operation):
    config, store, (contract, _), registry = setup(tmp_path, source, stage)
    payload = _fixture(f"test_double_{kind}_rows.json")
    if source == "saber_registry":
        payload = payload.replace(b"saso_catalogue", b"saber_registry")
    seed_unit(store, contract=contract, run_id="20260904T120000Z", payload=payload, source_config=config["sources"][source])
    record = snapshots.build_row_snapshot(store, config, registry, kind=kind, source_id=source)
    assert record["source_id"] == source
    assert record["evidence"][0]["source_identity"]["access_classification"] == "test_double"
    # These are the actual framework refs; their historical byte shape has no access field.
    assert all("access_classification" not in ref for ref in record["raw_artifact_refs"])
    snapshots.validate_snapshot(record, allow_test_double=True)
    if operation == "load":
        snapshots.write_snapshot(record, tmp_path, allow_test_double=True)
        assert record["snapshot_id"] in repository.acquired_snapshots(kind, data_root=tmp_path, allow_test_double=True)
    with pytest.raises(ValueError, match="test_double"):
        if operation == "validate":
            snapshots.validate_snapshot(record)
        elif operation == "write":
            snapshots.write_snapshot(record, tmp_path)
        else:
            repository.acquired_snapshots(kind, data_root=tmp_path)
    if operation == "write":
        assert not (tmp_path / "snapshots" / kind).exists()
