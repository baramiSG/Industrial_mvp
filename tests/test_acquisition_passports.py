"""Passport completeness tests."""

from __future__ import annotations

import pytest

from ior_mvp.acquisition.contracts import CompletenessBasis, CoverageRecord, Stage
from ior_mvp.acquisition.passports import assert_passport_complete, build_acquired_passport


def test_assert_passport_complete_rejects_synthetic() -> None:
    passport = {
        "passport_id": "p1",
        "source_id": "wits_trade",
        "synthetic_flag": True,
        "status": "observed",
        "evidence_class": "B",
        "reviewer_status": "unconfirmed_by_responsible_authority",
        "supports": ["TRADE_VALUE"],
        "source_identity": {},
        "query_contract": {},
        "retrieval": {},
        "coverage": {},
        "transformation_record": {},
        "observation_context": {},
        "measurement": {},
        "contradiction_record": None,
    }
    with pytest.raises(ValueError):
        assert_passport_complete(passport)
