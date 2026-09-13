from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

import ior_mvp.data_repository as data_repository
import ior_mvp.public_snapshot as public_snapshot
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.public_snapshot import (
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

    assert candidate["schema_version"] == (
        public_snapshot.LEGACY_PUBLIC_SNAPSHOT_SCHEMA_VERSION_2_1
    )
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


def _v22_candidate(
    tmp_path: Path,
) -> tuple[dict[str, Any], Path, Path]:
    candidate, root, live = _candidate(tmp_path)
    candidate["schema_version"] = "2.2.0"
    candidate.pop("partner_observations", None)
    return candidate, root, live


def _partner_passport(
    candidate: dict[str, Any],
    evidence_id: str,
    *,
    status: str,
    transformation: str,
) -> dict[str, Any]:
    passport = deepcopy(candidate["evidence"][0])
    passport.update(
        {
            "evidence_id": evidence_id,
            "status": status,
            "transformation": transformation,
            "synthetic_flag": False,
            "contradiction": None,
        }
    )
    return passport


def _partner_row(evidence_id: str) -> dict[str, Any]:
    return {
        "year": 2024,
        "partner": "Test partner",
        "flow": "imports",
        "trade_value_usd_m": 92.3,
        "net_weight_kt": 56.0,
        "quantity_unit": "kt",
        "validity_flags": {
            "value_valid": True,
            "net_weight_valid": True,
            "quantity_comparable": True,
        },
        "gross_flow": True,
        "source_evidence_id": evidence_id,
    }


def _partner_detail(
    *,
    state: str,
    reason: str | None,
    rows: int | str,
    attempts: list[str],
    observed: str | None,
) -> dict[str, Any]:
    return {
        "state": state,
        "reason": reason,
        "source_id": (
            "UNAVAILABLE"
            if state == "PARTNER_DETAIL_MISSING"
            else "un_comtrade"
        ),
        "partner_snapshot_id": (
            "UNAVAILABLE"
            if state == "PARTNER_DETAIL_MISSING"
            else "PARTNERS-TEST"
        ),
        "unit_key": ["721049", "imports", "2024"],
        "observed_partner_rows": rows,
        "attempt_passport_ids": attempts,
        "observed_passport_id": observed,
    }


def test_supported_versions_are_2_1_0_and_2_2_0_and_constant_is_2_2_0(
) -> None:
    assert public_snapshot.SUPPORTED_PUBLIC_SNAPSHOT_SCHEMA_VERSIONS == (
        frozenset({"2.1.0", "2.2.0"})
    )
    assert public_snapshot.PUBLIC_SNAPSHOT_SCHEMA_VERSION == "2.2.0"
    assert (
        public_snapshot.LEGACY_PUBLIC_SNAPSHOT_SCHEMA_VERSION_2_1
        == "2.1.0"
    )


def test_2_1_0_record_with_partner_detail_is_refused_as_extra_key(
    tmp_path: Path,
) -> None:
    candidate, root, live = _candidate(tmp_path)
    candidate["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_MISSING",
        reason="NOT_ACQUIRED",
        rows="UNAVAILABLE",
        attempts=[],
        observed=None,
    )

    with pytest.raises(
        PublicSnapshotIntegrityError,
        match=r"snapshot: unexpected key\(s\): partner_detail",
    ):
        validate_public_snapshot(candidate, path=live, root=root)


def test_2_2_0_partner_detail_exact_keys_state_enum_and_reason_vocabulary(
    tmp_path: Path,
) -> None:
    candidate, root, live = _v22_candidate(tmp_path)
    candidate["partner_observations"] = "UNAVAILABLE"
    candidate["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_MISSING",
        reason="NOT_ACQUIRED",
        rows="UNAVAILABLE",
        attempts=[],
        observed=None,
    )
    validate_public_snapshot(candidate, path=live, root=root)

    extra = deepcopy(candidate)
    extra["partner_detail"]["authored_outcome"] = "MISSING"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match=r"partner_detail: unexpected key\(s\): authored_outcome",
    ):
        validate_public_snapshot(extra, path=live, root=root)

    invalid_state = deepcopy(candidate)
    invalid_state["partner_detail"]["state"] = "UNKNOWN"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail.state",
    ):
        validate_public_snapshot(invalid_state, path=live, root=root)

    invalid_reason = deepcopy(candidate)
    invalid_reason["partner_detail"]["reason"] = "NOT_A_REASON"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail.reason",
    ):
        validate_public_snapshot(invalid_reason, path=live, root=root)

    invalid_attempt_type = deepcopy(candidate)
    invalid_attempt_type["partner_detail"]["reason"] = "HTTP_ERROR"
    invalid_attempt_type["partner_detail"]["attempt_passport_ids"] = [{}]
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail.attempt_passport_ids",
    ):
        validate_public_snapshot(
            invalid_attempt_type,
            path=live,
            root=root,
        )


def test_2_2_0_cross_rules_list_requires_observed_unavailable_requires_missing_or_zero_absent_requires_absent(
    tmp_path: Path,
) -> None:
    candidate, root, live = _v22_candidate(tmp_path)
    validate_public_snapshot(candidate, path=live, root=root)

    unavailable_without_detail = deepcopy(candidate)
    unavailable_without_detail["partner_observations"] = "UNAVAILABLE"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail",
    ):
        validate_public_snapshot(
            unavailable_without_detail,
            path=live,
            root=root,
        )

    missing = deepcopy(unavailable_without_detail)
    missing["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_MISSING",
        reason="NOT_ACQUIRED",
        rows="UNAVAILABLE",
        attempts=[],
        observed=None,
    )
    validate_public_snapshot(missing, path=live, root=root)

    rows_without_detail = deepcopy(candidate)
    rows_without_detail["partner_observations"] = [
        _partner_row("P-PARTNERS")
    ]
    rows_without_detail["evidence"].append(
        _partner_passport(
            rows_without_detail,
            "P-PARTNERS",
            status="calculated",
            transformation="NORMALIZED_PARTNER_ROWS",
        )
    )
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail",
    ):
        validate_public_snapshot(rows_without_detail, path=live, root=root)

    observed = deepcopy(rows_without_detail)
    observed["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_OBSERVED",
        reason=None,
        rows=1,
        attempts=[],
        observed="P-PARTNERS",
    )
    validate_public_snapshot(observed, path=live, root=root)

    detail_without_layer = deepcopy(candidate)
    detail_without_layer["partner_detail"] = observed["partner_detail"]
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="partner_detail",
    ):
        validate_public_snapshot(
            detail_without_layer,
            path=live,
            root=root,
        )


def test_2_2_0_attempt_and_observed_passport_references_resolve_with_required_status(
    tmp_path: Path,
) -> None:
    candidate, root, live = _v22_candidate(tmp_path)
    candidate["partner_observations"] = "UNAVAILABLE"
    candidate["evidence"].append(
        _partner_passport(
            candidate,
            "P-PARTNERS-ATTEMPT",
            status="unresolved",
            transformation="PARTNER_DETAIL_MISSING:HTTP_ERROR",
        )
    )
    candidate["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_MISSING",
        reason="HTTP_ERROR",
        rows="UNAVAILABLE",
        attempts=["P-PARTNERS-ATTEMPT"],
        observed=None,
    )
    validate_public_snapshot(candidate, path=live, root=root)

    wrong_prefix = deepcopy(candidate)
    wrong_prefix["evidence"][-1]["transformation"] = "HTTP_ERROR"
    with pytest.raises(
        PublicSnapshotIntegrityError,
        match="transformation",
    ):
        validate_public_snapshot(wrong_prefix, path=live, root=root)

    observed = deepcopy(candidate)
    observed_id = "P-COMTRADE-390210-PARTNERS"
    observed["partner_observations"] = [_partner_row(observed_id)]
    observed["evidence"][-1]["transformation"] = (
        "PARTNER_DETAIL_ATTEMPT_SUPERSEDED:HTTP_ERROR"
    )
    observed["evidence"].append(
        _partner_passport(
            observed,
            "P-WITS-390210-PARTNERS-ATTEMPT",
            status="unresolved",
            transformation=(
                "PARTNER_DETAIL_ATTEMPT_SUPERSEDED:"
                "FORMAT_NOT_PARSEABLE"
            ),
        )
    )
    observed["evidence"].append(
        _partner_passport(
            observed,
            observed_id,
            status="calculated",
            transformation="NORMALIZED_PARTNER_ROWS",
        )
    )
    observed["partner_detail"] = _partner_detail(
        state="PARTNER_DETAIL_OBSERVED",
        reason=None,
        rows=1,
        attempts=[
            "P-PARTNERS-ATTEMPT",
            "P-WITS-390210-PARTNERS-ATTEMPT",
        ],
        observed=observed_id,
    )
    validate_public_snapshot(observed, path=live, root=root)

    zero = deepcopy(candidate)
    zero_id = "P-COMTRADE-390210-PARTNERS-ZERO"
    zero["evidence"].append(
        _partner_passport(
            zero,
            zero_id,
            status="observed",
            transformation="PARTNER_TRADE_OBSERVED_ZERO",
        )
    )
    zero["partner_detail"] = _partner_detail(
        state="PARTNER_TRADE_OBSERVED_ZERO",
        reason=None,
        rows=0,
        attempts=["P-PARTNERS-ATTEMPT"],
        observed=zero_id,
    )
    validate_public_snapshot(zero, path=live, root=root)


def test_partner_detail_missing_reasons_equal_unavailable_reason_enum_plus_not_acquired_and_revision_mismatch(
) -> None:
    from ior_mvp.acquisition.contracts import UnavailableReason

    assert public_snapshot.PARTNER_DETAIL_MISSING_REASONS == (
        {reason.name for reason in UnavailableReason}
        | {"NOT_ACQUIRED", "REVISION_MISMATCH"}
    )
