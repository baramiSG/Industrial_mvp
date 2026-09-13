"""Real S14a brief reconstruction and public-engine proof."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


BRIEF_ROOT = PROJECT_ROOT / "data" / "cases" / "briefs"
EXPECTED_HS6 = (
    "294110",
    "294120",
    "310430",
    "310510",
    "392010",
    "721012",
    "721061",
    "760429",
    "760711",
)


def _paths() -> list[Path]:
    paths = sorted(BRIEF_ROOT.glob("CASE-BRIEF-SAU-H6-*-v1.json"))
    assert [path.name.split("-")[-2] for path in paths] == list(EXPECTED_HS6)
    return paths


def _build(path: Path) -> dict:
    from ior_mvp.cases.build import build_from_brief

    return build_from_brief(path, root=PROJECT_ROOT)


def test_each_s14_brief_validates_and_builds_deterministically() -> None:
    from ior_mvp.cases.brief import load_case_brief
    from ior_mvp.cases.projection import canonical_bytes

    for path in _paths():
        load_case_brief(path, root=PROJECT_ROOT)
        assert canonical_bytes(_build(path)) == canonical_bytes(_build(path))


def test_each_built_snapshot_validates_against_public_snapshot_2_1_0() -> None:
    from ior_mvp.public_snapshot import validate_public_snapshot

    for path in _paths():
        snapshot = _build(path)
        validate_public_snapshot(snapshot, root=PROJECT_ROOT)


def test_721061_brief_partner_detail_matches_stored_v3_defective_v1_and_wits_units() -> None:
    from ior_mvp.cases.brief import load_case_brief

    brief = load_case_brief(
        BRIEF_ROOT / "CASE-BRIEF-SAU-H6-721061-v1.json",
        root=PROJECT_ROOT,
    )
    detail = brief["partner_detail"]
    assert detail["state"] == "PARTNER_DETAIL_OBSERVED"
    assert detail["reason"] is None
    assert detail["observed_partner_rows"] == 7
    assert [
        (row["source_id"], row["normalization_status"], row["coverage_status"])
        for row in detail["attempts"]
    ] == [
        ("un_comtrade", "NORMALIZED", "COMPLETE"),
        ("un_comtrade", "NORMALIZED", "INCOMPLETE"),
        ("un_comtrade", "NORMALIZED", "INCOMPLETE"),
        ("wits_trade", "UNPARSED", "COMPLETE"),
    ]
    for attempt in detail["attempts"]:
        contract = json.loads(
            (PROJECT_ROOT / attempt["contract_path"]).read_text(
                encoding="utf-8"
            )
        )
        assert contract["query_hash"] == attempt["query_hash"]
        assert contract["run_id"] == attempt["run_id"]


def test_s15_briefs_reference_scoped_observed_partner_units() -> None:
    expected_rows = {
        "294110": 10,
        "294120": 4,
        "310430": 11,
        "310510": 11,
    }
    snapshot_id = "PARTNERS-SAU-UN-COMTRADE-2026-09-13-edbd1926e196"
    for hs6, observed_rows in expected_rows.items():
        brief = json.loads(
            (
                BRIEF_ROOT / f"CASE-BRIEF-SAU-H6-{hs6}-v1.json"
            ).read_text(encoding="utf-8")
        )
        detail = brief["partner_detail"]
        assert brief["partner_snapshot_id"] == snapshot_id
        assert detail["partner_snapshot_id"] == snapshot_id
        assert detail["state"] == "PARTNER_DETAIL_OBSERVED"
        assert detail["reason"] is None
        assert detail["observed_partner_rows"] == observed_rows
        assert len(detail["attempts"]) == 1
        assert detail["attempts"][0]["coverage_status"] == "COMPLETE"


def test_built_snapshots_and_briefs_contain_no_credential_header_or_env_value() -> None:
    forbidden_header = "ocp-" + "apim-subscription-key"
    secret = os.environ.get("IOR_COMTRADE_SUBSCRIPTION_KEY")
    chunks = [
        path.read_text(encoding="utf-8")
        for root in (
            PROJECT_ROOT / "data" / "cases",
            PROJECT_ROOT / "data" / "raw" / "un_comtrade",
            PROJECT_ROOT / ".workflow" / "slices" / "S14-deep-cases-a",
        )
        for path in root.rglob("*.json")
        if path.is_file()
    ]
    chunks.extend(
        json.dumps(_build(path), ensure_ascii=False) for path in _paths()
    )
    text = "\n".join(chunks)
    assert forbidden_header not in text.casefold()
    if secret:
        assert secret not in text


def test_each_built_snapshot_partner_layer_distinguishes_missing_zero_observed() -> None:
    for path in _paths():
        brief = json.loads(path.read_text(encoding="utf-8"))
        snapshot = _build(path)
        state = brief["partner_detail"]["state"]
        ids = {row["evidence_id"]: row for row in snapshot["evidence"]}
        if state == "PARTNER_DETAIL_OBSERVED":
            assert isinstance(snapshot["partner_observations"], list)
            assert snapshot["partner_observations"]
            source_tag = (
                "COMTRADE"
                if brief["partner_detail"]["source_id"] == "un_comtrade"
                else "WITS"
            )
            assert f"P-{source_tag}-{brief['hs6']}-PARTNERS" in ids
        elif state == "PARTNER_DETAIL_MISSING":
            assert snapshot["partner_observations"] == "UNAVAILABLE"
            attempts = [
                row
                for evidence_id, row in ids.items()
                if "-PARTNERS-ATTEMPT" in evidence_id
            ]
            assert attempts
            assert all(row["status"] == "unresolved" for row in attempts)
            assert any(
                row["transformation"].startswith(
                    "PARTNER_DETAIL_MISSING:FORMAT_NOT_PARSEABLE;"
                )
                for row in attempts
            )
        else:
            assert state == "PARTNER_TRADE_OBSERVED_ZERO"
            assert snapshot["partner_observations"] == "UNAVAILABLE"
            assert any(
                evidence_id.endswith("-PARTNERS-ZERO")
                and row["status"] == "observed"
                for evidence_id, row in ids.items()
            )


def test_public_engine_state_is_investigate_with_null_route_for_each_built_snapshot(
    capsys,
) -> None:
    from ior_mvp.capability import evaluate_capability
    from ior_mvp.public_decision import compute_public_decision
    from ior_mvp.public_snapshot import capability_hard_gate_names
    from ior_mvp.rules import evaluate_rules

    observed = []
    for path in _paths():
        snapshot = _build(path)
        rules = evaluate_rules(snapshot)
        capability = evaluate_capability(
            snapshot["opportunity"]["sector_profile"],
            snapshot["domestic_capability"]["public_dimension_states"],
            snapshot["domestic_capability"]["profile_hard_gates"],
            capability_hard_gate_names(snapshot["domestic_capability"]),
        )
        decision = compute_public_decision(snapshot, rules, capability)
        fired = [
            row["rule_id"] for row in rules if row.get("fired") is True
        ]
        proof = (
            snapshot["opportunity"]["id"],
            decision["state"],
            decision["route_code"],
            decision["decision_reason_code"],
            fired,
        )
        print("ENGINE_PROOF", proof)
        observed.append(proof)
    assert all(state == "INVESTIGATE" for _, state, _, _, _ in observed)
    assert all(route is None for _, _, route, _, _ in observed)
    steel = next(row for row in observed if row[0] == "SAU-H6-721061")
    assert {"R0", "R1-D", "R12"} <= set(steel[4])
    assert "R3" in steel[4]
    assert "ENGINE_PROOF" in capsys.readouterr().out


def test_no_built_snapshot_contains_synthetic_or_authored_decision_fields() -> None:
    forbidden = {
        "real_decision",
        "simulation_decision",
        "active_decision",
        "route_code",
        "screening_disposition",
        "synthetic_inputs",
        "scenario_id",
    }

    def walk(value):
        if isinstance(value, dict):
            assert not (set(value) & forbidden)
            assert value.get("synthetic_flag") is not True
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for path in _paths():
        walk(_build(path))
