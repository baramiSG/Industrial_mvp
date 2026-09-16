from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.scenario_contract import validate_simulation_contract

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "data" / "synthetic" / "historical" / "v1_1"
HISTORICAL_V2_0 = ROOT / "data" / "synthetic" / "historical" / "v2_0"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_historical_v1_1_hashes_are_pinned() -> None:
    assert _sha256(HISTORICAL / "SYN-MINISTRY-STEEL-001.json") == (
        "8867f0833662108746e0639082847d40841c0b3e550628199be93e75d46f9aea"
    )
    assert _sha256(HISTORICAL / "SYN-MINISTRY-PP-001.json") == (
        "06517bb93d68911b75c83adb5bf4eab085a2843d1aaa245b56555c999eeee5ea"
    )


def _leaves(value: object, path: tuple[str | int, ...] = ()) -> list[tuple[tuple[str | int, ...], object]]:
    if isinstance(value, dict):
        rows: list[tuple[tuple[str | int, ...], object]] = []
        for key, item in value.items():
            rows.extend(_leaves(item, path + (key,)))
        return rows
    if isinstance(value, list):
        rows = []
        for index, item in enumerate(value):
            rows.extend(_leaves(item, path + (index,)))
        return rows
    return [(path, value)]


def _get_path(root: object, path: tuple[str | int, ...]) -> object:
    current = root
    for key in path:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int):
            current = current[key]
        else:
            raise TypeError(path)
    return current


@pytest.mark.parametrize("name", ["STEEL", "PP"])
def test_live_2_0_0_preserves_1_1_0_synthetic_inputs(name: str) -> None:
    old = json.loads(
        (HISTORICAL / f"SYN-MINISTRY-{name}-001.json").read_text(
            encoding="utf-8"
        )
    )
    new = json.loads(
        (ROOT / "data" / "synthetic" / f"SYN-MINISTRY-{name}-001.json").read_text(
            encoding="utf-8"
        )
    )
    assert old["scenario_version"] == "1.1.0"
    assert new["scenario_version"] == "2.0.0"
    for key in (
        "scenario_id",
        "opportunity_id",
        "synthetic_flag",
        "display_label",
        "seed_basis",
        "evidence_class",
        "source",
        "ground_truth",
    ):
        assert old[key] == new[key], key
    for path, value in _leaves(old["synthetic_inputs"]):
        assert _get_path(new["synthetic_inputs"], path) == value, path
    for state, narrative in old["decision_narrative"].items():
        for field in ("headline", "route_label", "rationale"):
            assert (
                new["decision_narrative"][state][field]["en"]
                == narrative[field]
            )
        for field in ("conditions", "kill_conditions"):
            assert [
                item["en"] for item in new["decision_narrative"][state][field]
            ] == narrative[field]


def test_historical_v1_1_contract_is_rejected_at_runtime() -> None:
    scenario = json.loads(
        (HISTORICAL / "SYN-MINISTRY-STEEL-001.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(
        EvidenceIntegrityError,
        match="unsupported",
    ):
        validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    ("name", "expected_hash"),
    [
        (
            "SYN-MINISTRY-ALU-FOIL-001.json",
            "35808c7558bff6e7ba6fe6d0986920a2a523a3487054e6b03ac97fca7e7dcdb6",
        ),
        (
            "SYN-MINISTRY-ALU-PROFILES-001.json",
            "a96ae1b49db2c24d538aebdbf3e6109b174e0d9e583d28b5c727c400d378d3e9",
        ),
    ],
)
def test_s16b_live_2_1_preserves_exact_2_0_history(
    name: str,
    expected_hash: str,
) -> None:
    historical_path = HISTORICAL_V2_0 / name
    live_path = ROOT / "data" / "synthetic" / name
    assert _sha256(historical_path) == expected_hash
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    live = json.loads(live_path.read_text(encoding="utf-8"))
    assert historical["scenario_version"] == "2.0.0"
    assert live["scenario_version"] == "2.1.0"
    assert {
        key: value
        for key, value in live.items()
        if key != "scenario_version" and key != "synthetic_inputs"
    } == {
        key: value
        for key, value in historical.items()
        if key != "scenario_version" and key != "synthetic_inputs"
    }
    assert {
        key: value
        for key, value in live["synthetic_inputs"].items()
        if key != "shared_enabler"
    } == historical["synthetic_inputs"]
