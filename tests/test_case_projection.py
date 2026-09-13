"""CaseBrief-to-PublicSnapshot deterministic projection."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.test_case_brief import _brief, _stored_partner_case, _write_document


def _universe() -> dict:
    rows = []
    for year, revision in ((2021, "H5"), (2022, "H6"), (2023, "H6"), (2024, "H6")):
        for flow, multiplier in (("imports", 1), ("exports", 2)):
            rows.append(
                {
                    "year": year,
                    "flow": flow,
                    "hs6": "392010",
                    "hs_revision": revision,
                    "trade_value": float(year * 1_000_000 * multiplier),
                    "net_weight": float(year * 2_000_000 * multiplier),
                    "source_evidence_id": f"E-{flow}-{year}",
                }
            )
    evidence = []
    for flow in ("imports", "exports"):
        evidence.append(
            {
                "query_contract": {"unit_key": [flow, "2024"]},
                "retrieval": {
                    "endpoint_or_document": f"https://example.test/{flow}",
                    "retrieved_at": "2026-09-12T00:00:00Z",
                },
                "source_identity": {"authority": "UN Comtrade"},
                "evidence_class": "B",
                "reviewer_status": "unconfirmed_by_responsible_authority",
            }
        )
    return {
        "snapshot_id": "UNIVERSE-SAU-TEST",
        "as_of_date": "2026-09-12",
        "source_id": "un_comtrade",
        "rows": rows,
        "evidence": evidence,
    }


def _document(root: Path) -> tuple[str, dict]:
    document_id = _write_document(root)
    path = (
        root
        / "data"
        / "documents"
        / "wco_hs_nomenclature"
        / "records"
        / f"{document_id}.json"
    )
    import json

    return document_id, json.loads(path.read_text(encoding="utf-8"))


def _build(
    root: Path,
    brief: dict | None = None,
    universe: dict | None = None,
    partners: dict | None = None,
) -> dict:
    from ior_mvp.cases.projection import build_public_snapshot

    document_id, document = _document(root)
    return build_public_snapshot(
        brief or _brief(document_id),
        universe or _universe(),
        partners=partners,
        documents={document_id: document},
        root=root,
    )


def test_latest_revision_only_series_drops_h5_2021_and_keeps_h6_years() -> None:
    from ior_mvp.cases.projection import derive_trade

    trade, _quality = derive_trade(_universe()["rows"], "392010", "H6")
    assert [row["year"] for row in trade] == [2022, 2023, 2024]


def test_usd_to_usd_m_and_kg_to_kt_rounding_exact() -> None:
    from ior_mvp.cases.projection import derive_trade

    trade, _quality = derive_trade(_universe()["rows"], "392010", "H6")
    assert trade[0]["imports_usd_m"] == 2022.0
    assert trade[0]["imports_kt"] == 4044.0
    assert trade[0]["exports_usd_m"] == 4044.0
    assert trade[0]["exports_kt"] == 8088.0


def test_missing_net_weight_is_unavailable_not_zero_and_quantity_comparable_false() -> None:
    from ior_mvp.cases.projection import derive_trade

    universe = _universe()
    row = next(
        item
        for item in universe["rows"]
        if item["year"] == 2024 and item["flow"] == "imports"
    )
    row["net_weight"] = None
    trade, quality = derive_trade(universe["rows"], "392010", "H6")
    assert trade[-1]["imports_kt"] == "UNAVAILABLE"
    assert quality["quantity_comparable"] is False


def test_import_unit_value_only_when_both_operands_present() -> None:
    from ior_mvp.cases.projection import derive_trade

    universe = _universe()
    trade, _quality = derive_trade(universe["rows"], "392010", "H6")
    assert trade[-1]["import_uv_usd_t"] == 500.0
    next(
        item
        for item in universe["rows"]
        if item["year"] == 2024 and item["flow"] == "imports"
    )["net_weight"] = None
    trade, _quality = derive_trade(universe["rows"], "392010", "H6")
    assert "import_uv_usd_t" not in trade[-1]


def test_missing_years_and_execution_cap_text() -> None:
    from ior_mvp.cases.projection import derive_trade

    universe = _universe()
    universe["rows"] = [
        row
        for row in universe["rows"]
        if not (row["year"] == 2023 and row["flow"] == "imports")
    ]
    _trade, quality = derive_trade(universe["rows"], "392010", "H6")
    assert quality["missing_years"] == [2023]
    assert "H5" in quality["execution_cap"]
    assert "H6" in quality["execution_cap"]


def test_partner_observations_from_wits_rows_exclude_world_row() -> None:
    from ior_mvp.cases.projection import derive_partner_observations

    partner = {
        "snapshot_id": "PARTNERS-SAU-WITS-TEST",
        "rows": [
            {
                "hs6": "392010",
                "year": 2024,
                "partner": "World",
                "flow": "imports",
                "trade_value": 10_000_000,
                "net_weight": 5_000_000,
            },
            {
                "hs6": "392010",
                "year": 2024,
                "partner": "Alpha",
                "flow": "imports",
                "trade_value": 4_000_000,
                "net_weight": 2_000_000,
            },
        ],
        "evidence": [
            {
                "query_contract": {"unit_key": ["392010", "imports", "2024"]},
                "passport_id": "WITS-P",
            }
        ],
    }
    rows, passport = derive_partner_observations(partner, "392010")
    assert [row["partner"] for row in rows] == ["Alpha"]
    assert rows[0]["trade_value_usd_m"] == 4.0
    assert passport["passport_id"] == "WITS-P"


def test_partner_observations_unavailable_literal_without_snapshot() -> None:
    from ior_mvp.cases.projection import derive_partner_observations

    assert derive_partner_observations(None, "392010") == ("UNAVAILABLE", None)


def test_capability_u_and_unavailable_by_default(tmp_path: Path) -> None:
    snapshot = _build(tmp_path)
    capability = snapshot["domestic_capability"]
    assert capability["verified_present"] == "UNAVAILABLE"
    assert capability["same_process_family"] == "UNAVAILABLE"
    assert set(capability["public_dimension_states"].values()) == {"U"}
    assert {
        gate["status"] for gate in capability["profile_hard_gates"].values()
    } == {"UNAVAILABLE"}


def test_capability_from_spans_maps_span_ids_to_evidence_ids(tmp_path: Path) -> None:
    document_id, document_record = _document(tmp_path)
    document_record["declared"]["supports"] = [
        "DOMESTIC_PROCESS_ROUTE",
        "TARGET_PRODUCT_IDENTITY",
    ]
    document_path = (
        tmp_path
        / "data"
        / "documents"
        / "wco_hs_nomenclature"
        / "records"
        / f"{document_id}.json"
    )
    document_path.write_text(
        json.dumps(document_record, sort_keys=True),
        encoding="utf-8",
    )
    brief = _brief(document_id)
    brief["document_evidence"][0]["supports"] = [
        "DOMESTIC_PROCESS_ROUTE",
        "TARGET_PRODUCT_IDENTITY",
    ]
    brief["capability"]["verified_present"] = {
        "value": True,
        "span_ids": ["SPAN-WCO-392010"],
    }
    brief["capability"]["public_dimension_states"]["core_process_route"] = {
        "state": 0,
        "span_ids": ["SPAN-WCO-392010"],
    }
    snapshot = _build(tmp_path, brief=brief)
    assert snapshot["domestic_capability"]["verified_present"] is True
    assert snapshot["domestic_capability"]["public_dimension_states"][
        "core_process_route"
    ] == 0


def test_hard_exclusion_and_decision_inputs_all_unavailable(tmp_path: Path) -> None:
    snapshot = _build(tmp_path)
    assert snapshot["decision_inputs"] == {
        "target_specification_demand": "UNAVAILABLE",
        "specification_equivalence": "UNAVAILABLE",
        "route_evidence": "UNAVAILABLE",
        "monitor_trigger": "UNAVAILABLE",
    }
    assert all(
        value["evidence_ids"] == []
        for value in snapshot["hard_exclusion_inputs"].values()
    )


def test_snapshot_id_supersedes_and_schema(tmp_path: Path) -> None:
    snapshot = _build(tmp_path)
    assert snapshot["schema_version"] == "2.2.0"
    assert snapshot["snapshot_id"] == "PUBLIC-SAU-H6-392010-2026-09-12"
    assert snapshot["supersedes"] == "UNAVAILABLE"


def test_builder_writes_2_2_0_with_partner_detail_derived_from_brief_and_emitted_passports(
    tmp_path: Path,
) -> None:
    document_id = _write_document(tmp_path)
    brief = _brief(document_id)

    snapshot = _build(tmp_path, brief=brief)

    assert snapshot["schema_version"] == "2.2.0"
    assert snapshot["partner_detail"] == {
        "state": "PARTNER_DETAIL_MISSING",
        "reason": "NOT_ACQUIRED",
        "source_id": "UNAVAILABLE",
        "partner_snapshot_id": "UNAVAILABLE",
        "unit_key": ["392010", "imports", "2024"],
        "observed_partner_rows": "UNAVAILABLE",
        "attempt_passport_ids": [],
        "observed_passport_id": None,
    }


def test_built_snapshot_passes_validate_public_snapshot(tmp_path: Path) -> None:
    from ior_mvp.public_snapshot import validate_public_snapshot

    snapshot = _build(tmp_path)
    validate_public_snapshot(snapshot, root=tmp_path)


def test_unreferenced_attempt_passport_is_accepted_by_validate_public_snapshot_2_1_0(
    tmp_path: Path,
) -> None:
    from ior_mvp.public_snapshot import validate_public_snapshot

    snapshot = _build(tmp_path)
    assert snapshot["partner_observations"] == "UNAVAILABLE"
    snapshot["evidence"].append(
        {
            "evidence_id": "P-WITS-392010-PARTNERS-ATTEMPT",
            "title": "WITS Saudi 2024 import partner attempt for HS 392010",
            "source": "World Bank WITS",
            "url": "https://example.test/stored-attempt",
            "period": "2024",
            "retrieved_at": "2026-09-12",
            "status": "unresolved",
            "evidence_class": "B",
            "synthetic_flag": False,
            "supports": ["SUPPLIER_CONCENTRATION"],
            "transformation": (
                "PARTNER_DETAIL_MISSING:FORMAT_NOT_PARSEABLE; "
                "stored attempt, not trade."
            ),
            "reviewer_status": "unconfirmed_by_responsible_authority",
            "contradiction": None,
        }
    )

    validate_public_snapshot(snapshot, root=tmp_path)


def test_missing_state_projects_unavailable_rows_with_attempt_passport_marker_and_stored_url(
    tmp_path: Path,
) -> None:
    document_id = _write_document(tmp_path)
    brief = _brief(document_id)
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="UNPARSED",
        exclusion_reason="FORMAT_NOT_PARSEABLE",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_MISSING",
            "reason": "FORMAT_NOT_PARSEABLE",
            "observed_partner_rows": "UNAVAILABLE",
        }
    )
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    partners = json.loads(snapshot_path.read_text(encoding="utf-8"))

    snapshot = _build(tmp_path, brief=brief, partners=partners)

    assert snapshot["partner_observations"] == "UNAVAILABLE"
    passport = next(
        row
        for row in snapshot["evidence"]
        if row["evidence_id"].endswith("-PARTNERS-ATTEMPT")
    )
    assert passport["status"] == "unresolved"
    assert passport["url"] == "https://example.test/partners"
    assert passport["transformation"].startswith(
        "PARTNER_DETAIL_MISSING:FORMAT_NOT_PARSEABLE;"
    )
    assert "missing evidence, not zero trade" in snapshot["authority_note"]


def test_missing_state_block_references_every_attempt_passport_and_null_observed_passport(
    tmp_path: Path,
) -> None:
    document_id = _write_document(tmp_path)
    brief = _brief(document_id)
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="UNPARSED",
        exclusion_reason="FORMAT_NOT_PARSEABLE",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_MISSING",
            "reason": "FORMAT_NOT_PARSEABLE",
            "observed_partner_rows": "UNAVAILABLE",
        }
    )
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    partners = json.loads(snapshot_path.read_text(encoding="utf-8"))

    snapshot = _build(tmp_path, brief=brief, partners=partners)
    attempt_ids = [
        row["evidence_id"]
        for row in snapshot["evidence"]
        if "-PARTNERS-ATTEMPT" in row["evidence_id"]
    ]

    assert snapshot["partner_detail"]["attempt_passport_ids"] == attempt_ids
    assert snapshot["partner_detail"]["observed_passport_id"] is None


def test_observed_zero_state_projects_zero_passport_not_attempt_passport(
    tmp_path: Path,
) -> None:
    document_id = _write_document(tmp_path)
    brief = _brief(document_id)
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="NORMALIZED_EMPTY",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_TRADE_OBSERVED_ZERO",
            "reason": None,
            "observed_partner_rows": 0,
        }
    )
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    partners = json.loads(snapshot_path.read_text(encoding="utf-8"))

    snapshot = _build(tmp_path, brief=brief, partners=partners)

    assert snapshot["partner_observations"] == "UNAVAILABLE"
    ids = {row["evidence_id"] for row in snapshot["evidence"]}
    assert "P-COMTRADE-392010-PARTNERS-ZERO" in ids
    assert not any(value.endswith("-PARTNERS-ATTEMPT") for value in ids)
    zero = next(
        row for row in snapshot["evidence"] if row["evidence_id"].endswith("-ZERO")
    )
    assert zero["status"] == "observed"
    assert zero["transformation"].startswith("PARTNER_TRADE_OBSERVED_ZERO;")
    assert snapshot["partner_detail"]["observed_passport_id"] == zero["evidence_id"]
    assert snapshot["partner_detail"]["attempt_passport_ids"] == []


def test_observed_rows_from_un_comtrade_snapshot_use_comtrade_passport_and_keep_wits_attempt_passport(
    tmp_path: Path,
) -> None:
    import hashlib

    document_id = _write_document(tmp_path)
    brief = _brief(document_id)
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="NORMALIZED",
        rows=[
            {
                "hs6": "392010",
                "year": 2024,
                "flow": "imports",
                "partner": "China",
                "trade_value": 1_000_000,
                "net_weight": 2_000_000,
                "hs_revision": "H6",
            }
        ],
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_OBSERVED",
            "reason": None,
            "observed_partner_rows": 1,
        }
    )
    wits_hash = "b" * 64
    run_id = "20260912T233403Z"
    path = (
        tmp_path
        / "data"
        / "raw"
        / "wits_trade"
        / wits_hash
        / run_id
        / "page-0001.contract.json"
    )
    path.parent.mkdir(parents=True)
    contract = {
        "query_hash": wits_hash,
        "run_id": run_id,
        "endpoint_or_document": "https://example.test/wits-error",
        "http_status": 200,
        "normalization_status": "UNPARSED",
        "retrieved_at": "2026-09-12T23:34:12Z",
    }
    encoded = (json.dumps(contract, sort_keys=True) + "\n").encode()
    path.write_bytes(encoded)
    (path.parent / "coverage.json").write_text(
        json.dumps(
            {"status": "COMPLETE", "stop_reason": None}, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    brief["partner_detail"]["attempts"].append(
        {
            "source_id": "wits_trade",
            "query_hash": wits_hash,
            "run_id": run_id,
            "endpoint_or_document": contract["endpoint_or_document"],
            "http_status": 200,
            "normalization_status": "UNPARSED",
            "coverage_status": "COMPLETE",
            "stop_reason": None,
            "contract_path": path.relative_to(tmp_path).as_posix(),
            "contract_sha256": hashlib.sha256(encoded).hexdigest(),
        }
    )
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    partners = json.loads(snapshot_path.read_text(encoding="utf-8"))

    snapshot = _build(tmp_path, brief=brief, partners=partners)

    assert len(snapshot["partner_observations"]) == 1
    assert (
        snapshot["partner_observations"][0]["source_evidence_id"]
        == "P-COMTRADE-392010-PARTNERS"
    )
    ids = {row["evidence_id"] for row in snapshot["evidence"]}
    assert "P-COMTRADE-392010-PARTNERS" in ids
    assert "P-WITS-392010-PARTNERS-ATTEMPT" in ids
    attempt = next(
        row
        for row in snapshot["evidence"]
        if row["evidence_id"] == "P-WITS-392010-PARTNERS-ATTEMPT"
    )
    assert attempt["transformation"].startswith(
        "PARTNER_DETAIL_ATTEMPT_SUPERSEDED:"
    )
    assert "superseded by COMPLETE unit un_comtrade/" in attempt["transformation"]
    assert snapshot["partner_observations"][0]["partner"] == "China"
    assert (
        snapshot["partner_detail"]["observed_passport_id"]
        == "P-COMTRADE-392010-PARTNERS"
    )
    assert snapshot["partner_detail"]["observed_partner_rows"] == 1
    assert snapshot["partner_detail"]["attempt_passport_ids"] == [
        "P-WITS-392010-PARTNERS-ATTEMPT"
    ]


def test_projection_refuses_brief_state_that_contradicts_loaded_snapshot(
    tmp_path: Path,
) -> None:
    document_id = _write_document(tmp_path)
    brief = _brief(document_id)
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="NORMALIZED_EMPTY",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_OBSERVED",
            "reason": None,
            "observed_partner_rows": 1,
        }
    )
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    partners = json.loads(snapshot_path.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="OBSERVED"):
        _build(tmp_path, brief=brief, partners=partners)


def test_build_is_deterministic_byte_identical(tmp_path: Path) -> None:
    from ior_mvp.cases.projection import canonical_bytes

    first = _build(tmp_path)
    second = _build(tmp_path)
    assert canonical_bytes(first) == canonical_bytes(second)


def test_no_authored_decision_or_synthetic_fields(tmp_path: Path) -> None:
    snapshot = _build(tmp_path)
    text = str(snapshot)
    assert "DEMO_GENERATOR" not in text
    assert "route_code" not in text
    assert "real_decision" not in text
