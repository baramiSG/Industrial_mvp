"""Public screening artifacts cannot contain synthetic or formal decisions."""

from __future__ import annotations

import json
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


def _snapshots():
    return [
        json.loads(path.read_text())
        for path in sorted(
            (PROJECT_ROOT / "data" / "screening" / "snapshots").glob("*.json")
        )
    ]


def test_no_synthetic_flag_true_or_demo_generator_in_screening_data_or_api():
    text = json.dumps(_snapshots(), sort_keys=True)
    assert '"synthetic_flag": true' not in text.lower()
    assert "DEMO_GENERATOR" not in text


def test_screening_records_have_no_formal_state_route_or_d_star():
    for snapshot in _snapshots():
        for record in snapshot["records"]:
            assert not {"state", "route_code", "d_star"} & set(record)
