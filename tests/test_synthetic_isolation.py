from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.decision_engine import analyze
from ior_mvp.evidence import EvidenceIntegrityError, validate_public_evidence, validate_synthetic_scenario


def test_public_snapshots_contain_no_synthetic_rows() -> None:
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        case = get_public_case(opportunity_id)
        validate_public_evidence(case["evidence"])
        assert all(row["synthetic_flag"] is False for row in case["evidence"])


def test_simulated_analysis_keeps_real_decision_identical() -> None:
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    assert simulated["real_decision"] == public["real_decision"]
    assert simulated["simulation_decision"] != public["real_decision"]


def test_every_synthetic_row_is_labeled() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    synthetic = [row for row in result["evidence"] if row["synthetic_flag"]]
    assert synthetic
    for row in synthetic:
        assert row["source"] == "DEMO_GENERATOR"
        assert row["evidence_class"] == "D"
        assert row["display_label"] == "SIMULATED — NOT MINISTRY EVIDENCE"


def test_malformed_synthetic_scenario_fails_closed() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    malformed = deepcopy(scenario)
    del malformed["scenario_id"]
    with pytest.raises(EvidenceIntegrityError):
        validate_synthetic_scenario(malformed)
