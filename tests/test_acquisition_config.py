"""Acquisition config validation tests."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path

import pytest
import yaml

from ior_mvp.acquisition import source_config
from ior_mvp.acquisition.contracts import AcquisitionConfigurationError, Stage, UNAVAILABLE
from ior_mvp.acquisition.source_config import (
    ACQUISITION_SOURCES_PATH,
    acquisition_sources_config,
    validate_acquisition_sources,
)
from ior_mvp.config import PROJECT_ROOT
from tests.acquisition_doubles import pre_observation_document_source_config, pre_observation_source_config


INSTITUTIONAL = {
    "gastat": (Stage.AGGREGATE, "GASTAT economic census and industrial surveys", "B"),
    "ministry_of_industry": (Stage.DIRECTORY, "Ministry of Industry open data", "B"),
    "modon": (Stage.DIRECTORY, "MODON directories", "C"),
    "saso_catalogue": (Stage.REGISTRY, "SASO catalogue", "B"),
    "saber_registry": (Stage.REGISTRY, "SABER registry", "C"),
}
DOCUMENT = {
    "tadawul_disclosures": ("Tadawul filings and annual reports", "C"),
    "etimad_tenders": ("Etimad tenders and awards", "B"),
    "saso_documents": ("SASO public technical regulations", "B"),
    "producer_unicoil": ("UNICOIL public disclosures", "C"),
    "producer_sabic": ("SABIC (incl. Hadeed) public disclosures", "C"),
    "producer_advanced_petrochemical": ("Advanced Petrochemical public disclosures", "C"),
    "producer_tasnee": ("Tasnee public disclosures", "C"),
}
S11 = {"wits_trade", "un_comtrade", "baci_cepii", "zatca_tariff"}


def _head_config() -> dict:
    return yaml.safe_load(subprocess.check_output(
        ["git", "show", "HEAD:config/acquisition_sources.v1.yaml"], cwd=PROJECT_ROOT
    ))


@pytest.fixture
def phased_config() -> dict:
    cfg = _head_config()
    cfg["metadata"]["version"] = "1.2.0"
    for sid, (stage, authority, _) in INSTITUTIONAL.items():
        cfg["sources"][sid] = pre_observation_source_config(sid, stage=stage, authority=authority)
    for sid, (authority, evidence_class) in DOCUMENT.items():
        cfg["sources"][sid] = pre_observation_document_source_config(
            sid, authority=authority, evidence_class=evidence_class,
        )
    return cfg


def _set_fact(source: dict, path: str, value: object) -> None:
    keys = path.split(".")
    for key in keys[:-1]:
        source = source[key]
    source[keys[-1]] = value


def _fact_paths(stage: Stage) -> set[str]:
    return {
        "access_classification", "documentation_reference", "terms_reference",
        f"endpoint_templates.{stage.value}", "endpoint_templates.TERMS",
        "parameters.product_all_token", "parameters.partner_world_token",
        "parameters.reporter_token", "parameters.flow_tokens", "parameters.units",
        "pagination.kind", "pagination.documentation_reference", "pagination.parameters",
        "nomenclature", "credential_env_var", "rate_limit.documented_policy",
        "expected_content_types",
    }


@pytest.fixture
def valid_config() -> dict:
    path = PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_loads_yaml_version_and_sixteen_sources(valid_config: dict) -> None:
    assert valid_config["metadata"]["version"] == "1.2.0"
    assert set(valid_config["sources"]) == S11 | set(INSTITUTIONAL) | set(DOCUMENT)


def test_locked_literals(valid_config: dict) -> None:
    rs = valid_config["raw_store"]
    assert rs["max_artifact_bytes_compressed"] == 16777216
    assert rs["max_store_bytes_compressed"] == 100663296
    assert valid_config["offline_guard"]["live_env_var"] == "IOR_ACQUISITION_LIVE"
    assert (
        valid_config["rate_limit_defaults"]["undocumented_min_interval_seconds"]
        == 2.0
    )
    for sid in valid_config["sources"]:
        src = valid_config["sources"][sid]
        if sid in INSTITUTIONAL:
            assert src["default_evidence_class"] == INSTITUTIONAL[sid][2]
        elif sid in DOCUMENT:
            assert src["default_evidence_class"] == DOCUMENT[sid][1]
        else:
            assert src["default_evidence_class"] == "B"
        assert (
            src["default_reviewer_status"]
            == "unconfirmed_by_responsible_authority"
        )


def test_credential_env_var_only_for_un_comtrade(valid_config: dict) -> None:
    assert (
        valid_config["sources"]["un_comtrade"]["credential_env_var"]
        == "IOR_COMTRADE_SUBSCRIPTION_KEY"
    )
    for sid in ("wits_trade", "baci_cepii", "zatca_tariff"):
        assert valid_config["sources"][sid]["credential_env_var"] is None


def test_license_capture_implications(valid_config: dict) -> None:
    assert valid_config["sources"]["baci_cepii"]["license_capture_required"] is True
    assert valid_config["sources"]["un_comtrade"]["license_capture_required"] is True
    for sid, src in valid_config["sources"].items():
        if src["access_classification"] != "public_open":
            assert src["license_capture_required"] is True


def test_malformed_configs_raise(valid_config: dict) -> None:
    bad = copy.deepcopy(valid_config)
    del bad["sources"]["wits_trade"]
    with pytest.raises(AcquisitionConfigurationError):
        validate_acquisition_sources(bad)

    bad2 = copy.deepcopy(valid_config)
    bad2["raw_store"]["max_artifact_bytes_compressed"] = -1
    with pytest.raises(AcquisitionConfigurationError):
        validate_acquisition_sources(bad2)

    bad3 = copy.deepcopy(valid_config)
    bad3["sources"]["wits_trade"]["rate_limit"]["min_interval_seconds"] = 0
    with pytest.raises(AcquisitionConfigurationError):
        validate_acquisition_sources(bad3)

    bad4 = copy.deepcopy(valid_config)
    bad4["years"] = [2024]
    with pytest.raises(AcquisitionConfigurationError):
        validate_acquisition_sources(bad4)


def test_config_loader_lives_in_acquisition_package_and_caches() -> None:
    assert (
        ACQUISITION_SOURCES_PATH
        == PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml"
    )
    acquisition_sources_config.cache_clear()
    cfg = acquisition_sources_config()
    assert cfg["metadata"]["version"] == "1.2.0"
    assert acquisition_sources_config() is cfg


def test_config_loader_fails_closed_on_invalid_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    valid_config: dict,
) -> None:
    bad = copy.deepcopy(valid_config)
    bad["years"] = [2024]
    bad_path = tmp_path / "acquisition_sources.v1.yaml"
    bad_path.write_text(yaml.safe_dump(bad), encoding="utf-8")
    monkeypatch.setattr(source_config, "ACQUISITION_SOURCES_PATH", bad_path)
    source_config.acquisition_sources_config.cache_clear()
    try:
        with pytest.raises(AcquisitionConfigurationError):
            source_config.acquisition_sources_config()
    finally:
        source_config.acquisition_sources_config.cache_clear()


@pytest.mark.parametrize("field", ["access_classification", "expected_content_types", "credential_env_var"])
def test_s11_mappings_unchanged_and_strict(valid_config: dict, phased_config: dict, field: str) -> None:
    head = _head_config()
    assert {sid: valid_config["sources"][sid] for sid in S11} == {
        sid: head["sources"][sid] for sid in S11
    }
    validate_acquisition_sources(phased_config)
    for sid in S11:
        bad = copy.deepcopy(phased_config)
        bad["sources"][sid][field] = UNAVAILABLE
        with pytest.raises(AcquisitionConfigurationError):
            validate_acquisition_sources(bad)


@pytest.mark.parametrize("sid", INSTITUTIONAL)
def test_institutional_credential_env_var_sentinel_or_observed(valid_config: dict, sid: str) -> None:
    src = valid_config["sources"][sid]
    value = src["credential_env_var"]
    assert value is None or value == UNAVAILABLE or (
        isinstance(value, str) and source_config.CREDENTIAL_PATTERN.fullmatch(value)
    )
    if src["recorded_on"] == UNAVAILABLE:
        assert value == UNAVAILABLE


@pytest.mark.parametrize("sid", INSTITUTIONAL)
def test_institutional_pre_observation_entry_accepted(phased_config: dict, sid: str) -> None:
    validate_acquisition_sources(phased_config)
    src = phased_config["sources"][sid]
    assert source_config.observation_state(sid, src) == "PRE_OBSERVATION"
    assert source_config.observed_fact_values(sid, src) == {
        path: UNAVAILABLE for path in _fact_paths(INSTITUTIONAL[sid][0])
    }
    assert src["recorded_on"] == UNAVAILABLE
    assert src["license_capture_required"] is True


@pytest.mark.parametrize("sid", INSTITUTIONAL)
@pytest.mark.parametrize("field,value", [
    ("credential_env_var", None), ("parameters.flow_tokens", {}), ("pagination.parameters", {}),
])
def test_null_or_empty_mapping_is_observed_not_pre_observation(phased_config: dict, sid: str, field: str, value: object) -> None:
    validate_acquisition_sources(phased_config)
    src = phased_config["sources"][sid]
    _set_fact(src, field, value)
    assert source_config.observation_state(sid, src) == "OBSERVED"
    with pytest.raises(AcquisitionConfigurationError, match="recorded_on"):
        validate_acquisition_sources(phased_config)
    src["recorded_on"] = "2026-09-11"
    validate_acquisition_sources(phased_config)
    assert source_config.observation_state(sid, src) == "OBSERVED"


@pytest.mark.parametrize("sid", INSTITUTIONAL)
@pytest.mark.parametrize("field,value", [
    ("access_classification", "public_whatever"),
    ("expected_content_types", []), ("expected_content_types", "text/json"),
    ("expected_content_types", [""]), ("expected_content_types", [1]),
    ("parameters.units", []), ("parameters.units", ["unit"]),
    ("parameters.units", [{"unit": 1}]), ("parameters.units", [{}]),
    ("parameters.units", [{"": "value"}]),
    ("parameters.flow_tokens", "tokens"), ("parameters.flow_tokens", []),
    ("parameters.flow_tokens", {"imports": ""}), ("parameters.flow_tokens", {"": "M"}),
    ("pagination.parameters", "tokens"), ("pagination.parameters", []),
    ("pagination.parameters", {"page": 1}), ("pagination.parameters", {"": "1"}),
    ("pagination.kind", "INVENTED"), ("pagination.kind", []),
    ("nomenclature", "TEST-HS"), ("nomenclature", None),
    ("credential_env_var", "lowercase_name"), ("credential_env_var", ""),
    ("documentation_reference", ""), ("terms_reference", None),
    ("endpoint_templates.TERMS", []), ("pagination.documentation_reference", ""),
    ("parameters.product_all_token", ""), ("parameters.partner_world_token", 1),
    ("parameters.reporter_token", None), ("rate_limit.documented_policy", ""),
])
def test_institutional_observed_values_must_satisfy_s11_rules(phased_config: dict, sid: str, field: str, value: object) -> None:
    validate_acquisition_sources(phased_config)
    src = phased_config["sources"][sid]
    src["recorded_on"] = "2026-09-11"
    _set_fact(src, field, value)
    with pytest.raises(AcquisitionConfigurationError, match=field):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize("recorded_on", [UNAVAILABLE, "yesterday", "2026-02-30", "20260911", "2026-09-11T00:00:00Z", None])
def test_recorded_on_required_once_any_fact_recorded(phased_config: dict, recorded_on: object) -> None:
    validate_acquisition_sources(phased_config)
    src = phased_config["sources"]["gastat"]
    src["documentation_reference"] = "https://example.test/docs"
    src["recorded_on"] = recorded_on
    with pytest.raises(AcquisitionConfigurationError, match="recorded_on"):
        validate_acquisition_sources(phased_config)


def test_unavailable_access_requires_license_capture(phased_config: dict) -> None:
    validate_acquisition_sources(phased_config)
    phased_config["sources"]["gastat"]["license_capture_required"] = False
    with pytest.raises(AcquisitionConfigurationError, match="license_capture"):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize("container", ["", "parameters", "pagination", "rate_limit", "endpoint_templates"])
def test_unknown_source_key_rejected_for_institutional(phased_config: dict, container: str) -> None:
    validate_acquisition_sources(phased_config)
    source = phased_config["sources"]["gastat"]
    target = source[container] if container else source
    target["unknown_key"] = "TEST"
    with pytest.raises(AcquisitionConfigurationError, match="keys"):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize("key", ["years", "default_years", "max_requests", "default_max_requests"])
@pytest.mark.parametrize("location", ["root", "mapping", "nested_lists"])
def test_forbidden_keys_still_rejected(phased_config: dict, key: str, location: str) -> None:
    validate_acquisition_sources(phased_config)
    if location == "root":
        phased_config[key] = "TEST"
    elif location == "mapping":
        phased_config["metadata"]["nested"] = {"inner": {key: "TEST"}}
    else:
        phased_config["metadata"]["nested"] = [[{"inner": [{key: "TEST"}]}]]
    with pytest.raises(AcquisitionConfigurationError, match="Forbidden key"):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize("change", ["version", "fifteen", "seventeen"])
def test_version_and_id_set_exact(phased_config: dict, change: str) -> None:
    validate_acquisition_sources(phased_config)
    if change == "version":
        phased_config["metadata"]["version"] = "1.1.0"
    elif change == "fifteen":
        del phased_config["sources"]["gastat"]
    else:
        phased_config["sources"]["unknown"] = phased_config["sources"]["gastat"]
    with pytest.raises(AcquisitionConfigurationError):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize("sid", DOCUMENT)
def test_document_pre_observation_entry_accepted(phased_config: dict, sid: str) -> None:
    validate_acquisition_sources(phased_config)
    src = phased_config["sources"][sid]
    assert source_config.observation_state(sid, src) == "PRE_OBSERVATION"
    assert src["recorded_on"] == UNAVAILABLE


@pytest.mark.parametrize(
    "field,value",
    [
        ("access_classification", "public_whatever"),
        ("documentation_reference", ""),
        ("terms_reference", None),
        ("endpoint_templates.TERMS", []),
        ("parameters.product_all_token", ""),
        ("parameters.partner_world_token", 1),
        ("parameters.reporter_token", None),
        ("parameters.flow_tokens", {"imports": ""}),
        ("pagination.documentation_reference", ""),
        ("nomenclature", "TEST-HS"),
        ("credential_env_var", "lowercase_name"),
        ("rate_limit.documented_policy", ""),
        ("expected_content_types", []),
    ],
)
def test_document_observed_values_must_satisfy_shared_rules(
    phased_config: dict, field: str, value: object
) -> None:
    source = phased_config["sources"]["producer_unicoil"]
    source["recorded_on"] = "2026-09-12"
    _set_fact(source, field, value)
    with pytest.raises(AcquisitionConfigurationError, match=field):
        validate_acquisition_sources(phased_config)


@pytest.mark.parametrize(
    "container", ["", "parameters", "pagination", "rate_limit", "endpoint_templates"]
)
def test_unknown_source_key_rejected_for_document(
    phased_config: dict, container: str
) -> None:
    source = phased_config["sources"]["producer_unicoil"]
    target = source[container] if container else source
    target["unknown_key"] = "TEST"
    with pytest.raises(AcquisitionConfigurationError, match="keys"):
        validate_acquisition_sources(phased_config)


def test_document_structural_pins_exact(valid_config: dict) -> None:
    for sid in DOCUMENT:
        src = valid_config["sources"][sid]
        assert src["endpoint_templates"]["DOCUMENT"] == "{document_url}"
        assert src["pagination"]["kind"] == "NONE"
        assert src["pagination"]["parameters"] == {}
        assert "units" not in src["parameters"]


def test_s11_and_s12a_mappings_unchanged_and_strict(valid_config: dict) -> None:
    head = _head_config()
    for sid in head["sources"]:
        assert valid_config["sources"][sid] == head["sources"][sid]
    assert valid_config["raw_store"] == head["raw_store"]


@pytest.mark.parametrize("value,expected", [(None, None), ("", None), (UNAVAILABLE, None), ("IOR_X", "IOR_X")])
def test_configured_credential_env_var_helper(value: str | None, expected: str | None) -> None:
    assert source_config.configured_credential_env_var({"credential_env_var": value}) == expected


def test_live_yaml_loads_without_invented_enums() -> None:
    cfg = acquisition_sources_config()
    assert set(cfg["sources"]) == S11 | set(INSTITUTIONAL) | set(DOCUMENT)
    for sid, (authority, evidence_class) in DOCUMENT.items():
        src = cfg["sources"][sid]
        assert src["authority"] == authority
        assert src["default_evidence_class"] == evidence_class
        state = source_config.observation_state(sid, src)
        if src["recorded_on"] == UNAVAILABLE:
            assert state == "PRE_OBSERVATION"
        else:
            assert state == "OBSERVED"
    for sid, (stage, authority, _) in INSTITUTIONAL.items():
        src = cfg["sources"][sid]
        assert src["authority"] == authority
        if src["recorded_on"] == UNAVAILABLE:
            assert source_config.observed_fact_values(sid, src) == {
                path: UNAVAILABLE for path in _fact_paths(stage)
            }
            assert source_config.observation_state(sid, src) == "PRE_OBSERVATION"
    test_credential_env_var_only_for_un_comtrade(cfg)


@pytest.mark.parametrize("sid", INSTITUTIONAL)
def test_institutional_observed_values_accepted(phased_config: dict, sid: str) -> None:
    src = phased_config["sources"][sid]
    stage = INSTITUTIONAL[sid][0]
    facts = {
        "access_classification": "public_open",
        "documentation_reference": "https://example.test/docs",
        "terms_reference": "https://example.test/terms",
        f"endpoint_templates.{stage.value}": "https://example.test/data/{unit}",
        "endpoint_templates.TERMS": "https://example.test/terms",
        "parameters.product_all_token": "TESTALL",
        "parameters.partner_world_token": "TESTWORLD",
        "parameters.reporter_token": "SAU",
        "parameters.flow_tokens": {"imports": "M"},
        "parameters.units": [{"unit": "TEST-main"}],
        "pagination.kind": "PAGE_NUMBER",
        "pagination.documentation_reference": "https://example.test/docs",
        "pagination.parameters": {"page": ""},
        "nomenclature": "TEST1",
        "credential_env_var": "IOR_TEST_KEY",
        "rate_limit.documented_policy": "TEST policy",
        "expected_content_types": ["application/json"],
    }
    src["recorded_on"] = "2026-09-11"
    # Each observed fact must independently load beside the remaining sentinels.
    for field, value in facts.items():
        candidate = copy.deepcopy(phased_config)
        _set_fact(candidate["sources"][sid], field, value)
        validate_acquisition_sources(candidate)
        assert source_config.observation_state(sid, candidate["sources"][sid]) == "OBSERVED"
    for field, value in facts.items():
        _set_fact(src, field, value)
    validate_acquisition_sources(phased_config)
    assert source_config.observed_fact_values(sid, src) == facts


@pytest.mark.parametrize("sid", INSTITUTIONAL)
def test_unknown_source_key_and_missing_required_keys(phased_config: dict, sid: str) -> None:
    validate_acquisition_sources(phased_config)
    source = phased_config["sources"][sid]
    for container in ("", "parameters", "pagination", "rate_limit", "endpoint_templates"):
        for key in (source[container] if container else source):
            bad = copy.deepcopy(phased_config)
            target = bad["sources"][sid]
            del (target[container] if container else target)[key]
            with pytest.raises(AcquisitionConfigurationError):
                validate_acquisition_sources(bad)
