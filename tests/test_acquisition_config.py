"""Acquisition config validation tests."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from ior_mvp.acquisition import source_config
from ior_mvp.acquisition.contracts import AcquisitionConfigurationError
from ior_mvp.acquisition.source_config import (
    ACQUISITION_SOURCES_PATH,
    acquisition_sources_config,
    validate_acquisition_sources,
)
from ior_mvp.config import PROJECT_ROOT


@pytest.fixture
def valid_config() -> dict:
    path = PROJECT_ROOT / "config" / "acquisition_sources.v1.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_loads_yaml_version_and_four_sources(valid_config: dict) -> None:
    assert valid_config["metadata"]["version"] == "1.0.0"
    assert set(valid_config["sources"]) == {
        "wits_trade",
        "un_comtrade",
        "baci_cepii",
        "zatca_tariff",
    }


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
    assert cfg["metadata"]["version"] == "1.0.0"
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
