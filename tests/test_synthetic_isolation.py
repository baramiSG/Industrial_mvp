from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

import ior_mvp.data_repository as data_repository
from ior_mvp.config import evidence_policy_config
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.decision_engine import analyze
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    synthetic_evidence_rows,
    validate_public_evidence,
    validate_synthetic_scenario,
)


MANDATORY_SCENARIO_FIELDS = [
    "synthetic_flag",
    "scenario_id",
    "opportunity_id",
    "display_label",
    "seed_basis",
    "evidence_class",
    "source",
    "synthetic_inputs",
]


def _steel_scenario() -> dict:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    return deepcopy(scenario)


def test_public_snapshots_contain_no_synthetic_rows() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        case = get_public_case(opportunity_id)
        validate_public_evidence(case["evidence"])
        assert all(
            row["synthetic_flag"] is False
            for row in case["evidence"]
        )


def test_simulated_analysis_keeps_real_decision_identical() -> None:
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    assert simulated["real_decision"] == public["real_decision"]
    assert (
        simulated["simulation_decision"]
        != public["real_decision"]
    )


def test_every_synthetic_row_is_labeled() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    synthetic = [
        row
        for row in result["evidence"]
        if row["synthetic_flag"]
    ]
    assert synthetic
    for row in synthetic:
        assert row["source"] == "DEMO_GENERATOR"
        assert row["evidence_class"] == "D"
        assert (
            row["display_label"]
            == "SIMULATED — NOT MINISTRY EVIDENCE"
        )


def test_evidence_policy_declares_the_core_06_metadata_contract() -> None:
    policy = evidence_policy_config()
    isolation = policy["synthetic_isolation"]
    assert policy["metadata"]["version"] == "1.1.0"
    assert policy["metadata"]["effective_date"] == "2026-09-02"
    assert isolation["required_fields"] == MANDATORY_SCENARIO_FIELDS
    assert isolation["required_evidence_class"] == "D"
    assert isolation["required_source"] == "DEMO_GENERATOR"
    assert (
        isolation["display_label"]
        == "SIMULATED — NOT MINISTRY EVIDENCE"
    )


@pytest.mark.parametrize("field", MANDATORY_SCENARIO_FIELDS)
def test_each_missing_mandatory_field_raises_typed_integrity_error(
    field: str,
) -> None:
    scenario = _steel_scenario()
    del scenario[field]

    with pytest.raises(EvidenceIntegrityError) as captured:
        validate_synthetic_scenario(scenario)

    assert field in str(captured.value)


@pytest.mark.parametrize(
    ("field", "invalid", "policy_key"),
    [
        (
            "display_label",
            "Ministry evidence",
            "display_label",
        ),
        ("evidence_class", "C", "required_evidence_class"),
        ("source", "MINISTRY", "required_source"),
    ],
)
def test_policy_controlled_value_mismatch_raises_integrity_error(
    field: str,
    invalid: str,
    policy_key: str,
) -> None:
    scenario = _steel_scenario()
    scenario[field] = invalid

    with pytest.raises(EvidenceIntegrityError) as captured:
        validate_synthetic_scenario(scenario)

    assert policy_key in str(captured.value)


def test_non_mapping_synthetic_inputs_raise_integrity_error() -> None:
    scenario = _steel_scenario()
    scenario["synthetic_inputs"] = []

    with pytest.raises(
        EvidenceIntegrityError,
        match="synthetic_inputs must be a mapping",
    ):
        validate_synthetic_scenario(scenario)


def test_false_synthetic_flag_raises_integrity_error() -> None:
    scenario = _steel_scenario()
    scenario["synthetic_flag"] = False

    with pytest.raises(
        EvidenceIntegrityError,
        match="synthetic_flag=true",
    ):
        validate_synthetic_scenario(scenario)


def test_missing_display_label_never_leaks_a_key_error() -> None:
    scenario = _steel_scenario()
    del scenario["display_label"]

    with pytest.raises(EvidenceIntegrityError) as captured:
        synthetic_evidence_rows(scenario)

    assert "display_label" in str(captured.value)


def test_repository_propagates_policy_failure_as_integrity_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    synthetic_dir = tmp_path / "synthetic"
    synthetic_dir.mkdir()
    scenario = _steel_scenario()
    del scenario["opportunity_id"]
    (synthetic_dir / "scenario.json").write_text(
        json.dumps(scenario),
        encoding="utf-8",
    )
    monkeypatch.setattr(data_repository, "DATA_DIR", tmp_path)
    data_repository.clear_repository_caches()
    try:
        with pytest.raises(
            EvidenceIntegrityError,
            match="opportunity_id",
        ):
            data_repository.synthetic_scenarios()
    finally:
        data_repository.clear_repository_caches()


@pytest.mark.parametrize(
    "opportunity_id",
    ["SAU-H0-721049", "SAU-H0-390210"],
)
def test_policy_validation_accepts_additive_s04_metadata(
    opportunity_id: str,
) -> None:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    assert scenario["scenario_version"] == "1.1.0"
    assert isinstance(scenario["ground_truth"], dict)
    assert isinstance(scenario["decision_narrative"], dict)

    validate_synthetic_scenario(scenario)
