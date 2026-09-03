from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

import ior_mvp.data_repository as data_repository
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.public_snapshot import (
    PUBLIC_SNAPSHOT_SCHEMA_VERSION,
    PublicSnapshotIntegrityError,
    capability_hard_gate_names,
    has_known_hard_gate_failure,
    validate_public_snapshot,
)
from scripts.validate_scenarios import _index_public_cases
from tests.legacy_snapshot_v1 import (
    HISTORICAL_V1_ROOT,
    LIVE_PUBLIC_ROOT,
    candidate_v21_from_legacy,
    load_legacy_snapshot,
)


SNAPSHOT_FILES = (
    "SAU-H0-721049.json",
    "SAU-H0-390210.json",
)


def _candidate(
    tmp_path: Path,
    filename: str = "SAU-H0-721049.json",
) -> tuple[dict[str, Any], Path, Path]:
    source = LIVE_PUBLIC_ROOT / filename
    assert source.is_file()
    legacy = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    candidate = candidate_v21_from_legacy(legacy)
    root = tmp_path / "project"
    historical = root / candidate["supersedes"]
    historical.parent.mkdir(parents=True, exist_ok=True)
    historical.write_text(
        json.dumps(legacy, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    live = root / "data" / "snapshots" / "public" / filename
    live.parent.mkdir(parents=True, exist_ok=True)
    return candidate, root, live


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_exact_in_memory_v2_candidates_validate(
    tmp_path: Path,
    filename: str,
) -> None:
    candidate, root, live = _candidate(tmp_path, filename)

    validate_public_snapshot(candidate, path=live, root=root)

    assert candidate["schema_version"] == PUBLIC_SNAPSHOT_SCHEMA_VERSION
    assert "rule_context" not in candidate


@pytest.mark.parametrize("filename", SNAPSHOT_FILES)
def test_live_v2_is_exact_field_for_field_approved_migration(
    filename: str,
) -> None:
    legacy = load_legacy_snapshot(HISTORICAL_V1_ROOT / filename)
    live = load_legacy_snapshot(LIVE_PUBLIC_ROOT / filename)

    assert live == candidate_v21_from_legacy(legacy)
    validate_public_snapshot(live, path=LIVE_PUBLIC_ROOT / filename)


@pytest.mark.parametrize(
    "filename",
    [
        "advance-route-3.json",
        "monitor-r3-only.json",
        "reject-hard-exclusion.json",
        "reject-equivalence.json",
    ],
)
def test_synthetic_free_public_decision_fixtures_validate(
    filename: str,
) -> None:
    path = (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / filename
    )
    payload = load_legacy_snapshot(path)

    validate_public_snapshot(payload)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("public_decision_contract", {}),
        ("state", "ADVANCE"),
        ("route_code", 3),
        ("screening_disposition", "CANDIDATE"),
        ("gap_class", {"primary": "quantity"}),
        ("narrative", {}),
        ("missing_facts", []),
        ("conditions", []),
        ("kill_conditions", []),
        ("route_hypotheses", []),
    ],
)
def test_schema_rejects_every_authored_decision_output(
    tmp_path: Path,
    key: str,
    value: Any,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate[key] = value

    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="authored decision outcome",
    ):
        validate_public_snapshot(candidate, path=live, root=root)


def test_schema_rejects_free_text_or_unknown_support_codes(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["evidence"][0]["supports"] = ["trade value"]

    with pytest.raises(PublicSnapshotIntegrityError, match="support code"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_profile_hard_gate_set_status_and_evidence_are_fail_closed(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    gates = candidate["domestic_capability"]["profile_hard_gates"]
    removed = next(iter(gates))
    del gates[removed]
    with pytest.raises(PublicSnapshotIntegrityError, match="hard gate"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    gate = next(
        iter(
            candidate["domestic_capability"][
                "profile_hard_gates"
            ].values()
        )
    )
    gate["status"] = "RESOLVED"
    with pytest.raises(PublicSnapshotIntegrityError, match="evidence_ids"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    gate = next(
        iter(
            candidate["domestic_capability"][
                "profile_hard_gates"
            ].values()
        )
    )
    gate["status"] = "KNOWN_FAILURE"
    with pytest.raises(PublicSnapshotIntegrityError, match="evidence_ids"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_hard_exclusion_and_decision_input_domains_are_validated(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["hard_exclusion_inputs"]["unsatisfiable_hard_gate"][
        "gate_domain"
    ] = "invented"
    with pytest.raises(PublicSnapshotIntegrityError, match="gate_domain"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    candidate["hard_exclusion_inputs"][
        "transitory_or_measurement_gap"
    ]["dominant_cause"] = "PERMANENT"
    with pytest.raises(PublicSnapshotIntegrityError, match="dominant_cause"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate = load_legacy_snapshot(
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "advance-route-3.json"
    )
    candidate["decision_inputs"]["route_evidence"][0][
        "binding_constraint"
    ] = "invented"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="binding_constraint",
    ):
        validate_public_snapshot(candidate)


def test_route_eight_is_forbidden_in_snapshot_route_evidence() -> None:
    candidate = load_legacy_snapshot(
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "advance-route-3.json"
    )
    candidate["decision_inputs"]["route_evidence"][0]["route_code"] = 8

    with pytest.raises(PublicSnapshotIntegrityError, match="route_code"):
        validate_public_snapshot(candidate)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda candidate: next(
            item
            for item in candidate["evidence"]
            if item["evidence_id"] == "E-ROUTE"
        ).__setitem__("evidence_class", "D"),
        lambda candidate: next(
            item
            for item in candidate["evidence"]
            if item["evidence_id"] == "E-ROUTE"
        ).__setitem__(
            "supports",
            ["ROUTE_ECONOMICS", "ROUTE_COMPETITION"],
        ),
    ],
)
def test_route_evidence_requires_abc_covering_passports(mutation) -> None:
    candidate = load_legacy_snapshot(
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "advance-route-3.json"
    )
    mutation(candidate)

    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="route evidence",
    ):
        validate_public_snapshot(candidate)


def test_monitor_trigger_requires_covering_monitor_evidence() -> None:
    candidate = load_legacy_snapshot(
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "monitor-r3-only.json"
    )
    candidate["decision_inputs"]["monitor_trigger"][
        "evidence_ids"
    ] = ["E-ID"]

    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="MONITOR_TRIGGER",
    ):
        validate_public_snapshot(candidate)


def test_new_snapshot_may_use_exact_unavailable_supersedes() -> None:
    candidate = load_legacy_snapshot(
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "advance-route-3.json"
    )

    validate_public_snapshot(candidate)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: value.pop("schema_version"), "schema_version"),
        (
            lambda value: value.__setitem__("schema_version", "1.0.0"),
            "schema_version",
        ),
        (
            lambda value: value.__setitem__("rule_context", {}),
            "authored rule outcome",
        ),
        (
            lambda value: value.__setitem__("fired", True),
            "authored rule outcome",
        ),
        (
            lambda value: value["opportunity"].__setitem__(
                "execution", "FULL"
            ),
            "authored rule outcome",
        ),
        (
            lambda value: value["trade"][0].__setitem__(
                "unknown_trade_key", 1
            ),
            "unexpected key",
        ),
    ],
)
def test_schema_rejects_missing_wrong_unknown_or_authored_keys(
    tmp_path: Path,
    mutation: Any,
    match: str,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    mutation(candidate)

    with pytest.raises(PublicSnapshotIntegrityError, match=match):
        validate_public_snapshot(candidate, path=live, root=root)


@pytest.mark.parametrize(
    ("supersedes", "match"),
    [
        ("../SAU-H0-721049.json", "supersedes"),
        (
            "data/snapshots/public/SAU-H0-721049.json",
            "historical/v1",
        ),
        (
            "/data/snapshots/public/historical/v1/SAU-H0-721049.json",
            "relative",
        ),
    ],
)
def test_supersedes_must_be_safe_historical_v1_path(
    tmp_path: Path,
    supersedes: str,
    match: str,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["supersedes"] = supersedes

    with pytest.raises(PublicSnapshotIntegrityError, match=match):
        validate_public_snapshot(candidate, path=live, root=root)


def test_supersedes_must_exist_and_match_identity(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    historical = root / candidate["supersedes"]
    historical.unlink()
    with pytest.raises(PublicSnapshotIntegrityError, match="does not exist"):
        validate_public_snapshot(candidate, path=live, root=root)

    legacy = load_legacy_snapshot(
        (
            HISTORICAL_V1_ROOT
            if HISTORICAL_V1_ROOT.is_dir()
            else LIVE_PUBLIC_ROOT
        )
        / SNAPSHOT_FILES[0]
    )
    legacy["snapshot_id"] = "MISMATCH"
    historical.write_text(json.dumps(legacy), encoding="utf-8")
    with pytest.raises(PublicSnapshotIntegrityError, match="snapshot_id"):
        validate_public_snapshot(candidate, path=live, root=root)


@pytest.mark.parametrize(
    "value",
    [True, float("nan"), float("inf"), -0.01],
)
def test_trade_numeric_cells_reject_bool_nonfinite_and_negative(
    tmp_path: Path,
    value: Any,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["trade"][0]["imports_usd_m"] = value

    with pytest.raises(PublicSnapshotIntegrityError, match="imports_usd_m"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_disclosed_export_import_ratio_is_checked_against_computation(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(
        tmp_path,
        "SAU-H0-390210.json",
    )
    candidate["trade"][-1]["export_import_value_ratio"] = 50.6514

    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="export_import_value_ratio",
    ):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate["trade"][-1]["export_import_value_ratio"] = 50.6513
    validate_public_snapshot(candidate, path=live, root=root)


def _partner_observations() -> list[dict[str, Any]]:
    return [
        {
            "year": 2024,
            "partner": "Alpha",
            "flow": "imports",
            "trade_value_usd_m": 60.0,
            "net_weight_kt": 50.0,
            "quantity_unit": "kt",
            "validity_flags": {
                "value_valid": True,
                "net_weight_valid": True,
                "quantity_comparable": True,
            },
            "gross_flow": True,
            "source_evidence_id": "S-WITS-721049",
        },
        {
            "year": 2024,
            "partner": "Beta",
            "flow": "imports",
            "trade_value_usd_m": 40.0,
            "net_weight_kt": 50.0,
            "quantity_unit": "kt",
            "validity_flags": {
                "value_valid": True,
                "net_weight_valid": True,
                "quantity_comparable": True,
            },
            "gross_flow": True,
            "source_evidence_id": "S-WITS-721049",
        },
    ]


def test_partner_rows_validate_units_flags_uniqueness_and_references(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["partner_observations"] = _partner_observations()
    validate_public_snapshot(candidate, path=live, root=root)

    duplicate = deepcopy(candidate)
    duplicate["partner_observations"].append(
        deepcopy(duplicate["partner_observations"][0])
    )
    with pytest.raises(PublicSnapshotIntegrityError, match="duplicate"):
        validate_public_snapshot(duplicate, path=live, root=root)

    invalid = deepcopy(candidate)
    invalid["partner_observations"][0]["quantity_unit"] = "tonnes"
    with pytest.raises(PublicSnapshotIntegrityError, match="quantity_unit"):
        validate_public_snapshot(invalid, path=live, root=root)

    invalid = deepcopy(candidate)
    invalid["partner_observations"][0]["validity_flags"][
        "value_valid"
    ] = "yes"
    with pytest.raises(PublicSnapshotIntegrityError, match="value_valid"):
        validate_public_snapshot(invalid, path=live, root=root)

    invalid = deepcopy(candidate)
    invalid["partner_observations"][0][
        "source_evidence_id"
    ] = "MISSING"
    with pytest.raises(PublicSnapshotIntegrityError, match="MISSING"):
        validate_public_snapshot(invalid, path=live, root=root)


def test_disclosed_concentration_domains_and_basis_are_exact(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["disclosed_concentration"]["value"]["hhi"] = 1.01
    with pytest.raises(PublicSnapshotIntegrityError, match="hhi"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    candidate["disclosed_concentration"]["value"]["basis"] = "quantity"
    with pytest.raises(PublicSnapshotIntegrityError, match="basis"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_disclosed_dispersion_rejects_in_band_outlier_and_bad_source(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["disclosed_dispersion"]["outlier_observation"][
        "unit_value_usd_t"
    ] = 800
    with pytest.raises(PublicSnapshotIntegrityError, match="outside"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    candidate["disclosed_dispersion"]["source_evidence_id"] = "MISSING"
    with pytest.raises(PublicSnapshotIntegrityError, match="MISSING"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_domestic_flow_arithmetic_and_sentinel_are_fail_closed(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    flows = candidate["domestic_flows"]
    flows["retained_imports_kt"] = 250.0
    flows["reexports_kt"] = 37.9
    validate_public_snapshot(candidate, path=live, root=root)

    flows["retained_imports_kt"] = 249.9
    with pytest.raises(PublicSnapshotIntegrityError, match="retained_imports"):
        validate_public_snapshot(candidate, path=live, root=root)

    candidate, root, live = _candidate(tmp_path)
    candidate["domestic_flows"]["domestic_production_kt"] = "unknown"
    with pytest.raises(PublicSnapshotIntegrityError, match="UNAVAILABLE"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_criticality_designation_requires_resolvable_passport(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["criticality_designation"] = {
        "authority": "Responsible authority",
        "reference": "REF-1",
        "date": "2026-08-31",
        "evidence_id": "S-WITS-721049",
    }
    validate_public_snapshot(candidate, path=live, root=root)

    candidate["criticality_designation"]["evidence_id"] = "MISSING"
    with pytest.raises(PublicSnapshotIntegrityError, match="MISSING"):
        validate_public_snapshot(candidate, path=live, root=root)


def test_typed_signals_nameplates_and_hard_gates_validate(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    validate_public_snapshot(candidate, path=live, root=root)
    capability = candidate["domestic_capability"]
    assert capability_hard_gate_names(capability) == [
        "exact imported specification",
        "customer/application qualification",
        "effective spare capacity and allocation",
    ]
    assert has_known_hard_gate_failure(capability) is False

    profile_gate = next(
        iter(capability["profile_hard_gates"].values())
    )
    profile_gate["status"] = "KNOWN_FAILURE"
    profile_gate["evidence_ids"] = ["S-UNICOIL-EPD"]
    assert has_known_hard_gate_failure(capability) is True
    profile_gate["status"] = "UNAVAILABLE"
    profile_gate["evidence_ids"] = []

    capability["unresolved_hard_gates"][0]["state"] = "known_failure"
    capability["unresolved_hard_gates"][0]["evidence_ids"] = [
        "S-UNICOIL-EPD"
    ]
    assert has_known_hard_gate_failure(capability) is True
    validate_public_snapshot(candidate, path=live, root=root)

    invalid = deepcopy(candidate)
    invalid["domestic_capability"]["coarse_adjacency_signals"][0][
        "signal_type"
    ] = "invented"
    with pytest.raises(PublicSnapshotIntegrityError, match="signal_type"):
        validate_public_snapshot(invalid, path=live, root=root)

    invalid = deepcopy(candidate)
    invalid["domestic_capability"]["producer_evidence"][0][
        "nameplate_source_evidence_id"
    ] = "MISSING"
    with pytest.raises(PublicSnapshotIntegrityError, match="MISSING"):
        validate_public_snapshot(invalid, path=live, root=root)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("period", None),
        ("retrieved_at", "not-a-date"),
        ("transformation", None),
        ("reviewer_status", ""),
        ("contradiction", 123),
    ],
)
def test_public_passports_require_v2_fields(
    tmp_path: Path,
    field: str,
    value: Any,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["evidence"][0][field] = value

    with pytest.raises(PublicSnapshotIntegrityError, match=field):
        validate_public_snapshot(candidate, path=live, root=root)


def _write_live_candidate(
    candidate: dict[str, Any],
    live: Path,
) -> None:
    live.write_text(
        json.dumps(candidate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_repository_loads_only_direct_v2_files_and_ignores_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    _write_live_candidate(candidate, live)
    monkeypatch.setattr(data_repository, "DATA_DIR", root / "data")
    data_repository.clear_repository_caches()
    try:
        cases = data_repository.public_cases()
        assert list(cases) == ["SAU-H0-721049"]
        assert cases["SAU-H0-721049"]["schema_version"] == "2.1.0"
    finally:
        data_repository.clear_repository_caches()


def test_repository_rejects_v1_copied_into_live_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    public = root / "data" / "snapshots" / "public"
    public.mkdir(parents=True)
    legacy = load_legacy_snapshot(
        HISTORICAL_V1_ROOT / SNAPSHOT_FILES[0]
    )
    (public / SNAPSHOT_FILES[0]).write_text(
        json.dumps(legacy),
        encoding="utf-8",
    )
    monkeypatch.setattr(data_repository, "DATA_DIR", root / "data")
    data_repository.clear_repository_caches()
    try:
        with pytest.raises(
            PublicSnapshotIntegrityError,
            match="schema_version",
        ):
            data_repository.public_cases()
    finally:
        data_repository.clear_repository_caches()


def test_repository_rejects_duplicate_opportunity_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    _write_live_candidate(candidate, live)
    duplicate = deepcopy(candidate)
    duplicate_name = "duplicate.json"
    duplicate["supersedes"] = (
        "data/snapshots/public/historical/v1/"
        f"{duplicate_name}"
    )
    historical = root / duplicate["supersedes"]
    historical.write_text(
        json.dumps(
            load_legacy_snapshot(
                HISTORICAL_V1_ROOT / SNAPSHOT_FILES[0]
            )
        ),
        encoding="utf-8",
    )
    _write_live_candidate(duplicate, live.parent / duplicate_name)
    monkeypatch.setattr(data_repository, "DATA_DIR", root / "data")
    data_repository.clear_repository_caches()
    try:
        with pytest.raises(
            PublicSnapshotIntegrityError,
            match="Duplicate public opportunity.id",
        ):
            data_repository.public_cases()
    finally:
        data_repository.clear_repository_caches()


def test_gate_b_public_index_reuses_schema_validator(
    tmp_path: Path,
) -> None:
    candidate, _, live = _candidate(tmp_path)
    _write_live_candidate(candidate, live)
    assert list(_index_public_cases(live.parent)) == ["SAU-H0-721049"]

    candidate["evidence"][0]["reviewer_status"] = ""
    _write_live_candidate(candidate, live)
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="reviewer_status",
    ):
        _index_public_cases(live.parent)
