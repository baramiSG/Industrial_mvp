"""CaseBrief 1.0.0 fail-closed contract."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest


DIMENSIONS = (
    "feedstock_chemistry",
    "core_process_route",
    "equipment_envelope",
    "finishing_spec_control",
    "qa_lab_metrology",
    "certification_customer_qualification",
    "capacity_time_window",
    "utilities_ehs_permitting",
    "skills_market_integration",
)
GATES = (
    "polymer_additive_compatibility",
    "conversion_route",
    "tooling",
    "performance_requirement",
    "application_qualification",
)


def _write_document(root: Path, *, line: str = "3920.10 - Of polymers of ethylene") -> str:
    document_id = "DOC-WCO-TEST"
    path = (
        root
        / "data"
        / "documents"
        / "wco_hs_nomenclature"
        / "records"
        / f"{document_id}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "document_id": document_id,
                    "source_id": "wco_hs_nomenclature",
                    "coverage": {"status": "COMPLETE"},
                    "declared": {
                        "publisher_kind": "nomenclature_authority",
                        "evidence_class_target": "B",
                        "title_text": "TEST WCO document",
                        "supports": ["TARGET_PRODUCT_IDENTITY"],
                    },
                    "raw_artifact_ref": {
                        "endpoint_or_document": "https://example.test/wco.pdf",
                        "retrieved_at": "2026-09-12T00:00:00Z",
                    },
                    "pages": [{"page_index": 1, "lines": [line]}],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    return document_id


def _brief(document_id: str) -> dict:
    return {
        "schema_version": "1.1.0",
        "brief_id": "CASE-BRIEF-SAU-H6-392010-v1",
        "opportunity_id": "SAU-H6-392010",
        "hs6": "392010",
        "hs_revision": "H6",
        "sector_profile": "technical_plastics",
        "trade_series_rule": "LATEST_REVISION_ONLY",
        "universe_snapshot_id": "UNIVERSE-SAU-TEST",
        "partner_snapshot_id": "UNAVAILABLE",
        "partner_detail": {
            "state": "PARTNER_DETAIL_MISSING",
            "reason": "NOT_ACQUIRED",
            "source_id": "UNAVAILABLE",
            "partner_snapshot_id": "UNAVAILABLE",
            "unit_key": ["392010", "imports", "2024"],
            "observed_partner_rows": "UNAVAILABLE",
            "attempts": [],
            "basis": (
                "No stored partner-detail unit was acquired; missing evidence "
                "is not evidence of zero trade."
            ),
        },
        "commercial_name_en": "Of polymers of ethylene",
        "name_basis": "WCO_HS_2022_LEGAL_TEXT",
        "commercial_name_ar": "من بوليمرات الإيثيلين",
        "name_basis_ar": "ANALYST_TRANSLATION",
        "decision_object_status": "generic_hs6_only",
        "application_boundary": "Target application and specification unresolved.",
        "authority_note": "Public evidence only; H6 rows only.",
        "capability": {
            "verified_present": {"value": "UNAVAILABLE", "span_ids": []},
            "same_process_family": {"value": "UNAVAILABLE", "span_ids": []},
            "coarse_adjacency_signals": [],
            "producer_evidence": [],
            "public_dimension_states": {
                name: {"state": "U", "span_ids": []} for name in DIMENSIONS
            },
            "profile_hard_gates": {
                name: {"status": "UNAVAILABLE", "span_ids": []}
                for name in GATES
            },
            "unresolved_hard_gates": list(GATES),
        },
        "document_evidence": [
            {
                "evidence_id": "P-WCO-392010",
                "document_id": document_id,
                "supports": ["TARGET_PRODUCT_IDENTITY"],
                "period": "2022",
            }
        ],
        "spans": [
            {
                "span_id": "SPAN-WCO-392010",
                "document_id": document_id,
                "page_index": 1,
                "line_index": 1,
                "span_text": "Of polymers of ethylene",
                "text_order": "logical",
            }
        ],
    }


def _stored_partner_case(
    root: Path,
    brief: dict,
    *,
    normalization_status: str,
    rows: list[dict] | None = None,
    exclusion_reason: str | None = None,
) -> None:
    source_id = "un_comtrade"
    query_hash = "a" * 64
    run_id = "20260913T010000Z"
    contract_path = (
        root
        / "data"
        / "raw"
        / source_id
        / query_hash
        / run_id
        / "page-0001.contract.json"
    )
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract = {
        "query_hash": query_hash,
        "run_id": run_id,
        "endpoint_or_document": "https://example.test/partners",
        "http_status": 200,
        "normalization_status": normalization_status,
        "retrieved_at": "2026-09-13T01:00:00Z",
    }
    contract_bytes = (json.dumps(contract, sort_keys=True) + "\n").encode()
    contract_path.write_bytes(contract_bytes)
    coverage_status = "COMPLETE"
    coverage = {
        "status": coverage_status,
        "stop_reason": None,
        "unit_key": ["392010", "imports", "2024"],
    }
    (contract_path.parent / "coverage.json").write_text(
        json.dumps(coverage, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    snapshot_id = "PARTNERS-SAU-UN-COMTRADE-TEST"
    unit_status = "INCOMPLETE" if exclusion_reason else "COMPLETE"
    snapshot = {
        "snapshot_id": snapshot_id,
        "source_id": source_id,
        "coverage": {
            "units": [
                {
                    "unit_key": ["392010", "imports", "2024"],
                    "status": unit_status,
                    "query_hash": query_hash,
                    "selected_run_id": run_id,
                }
            ]
        },
        "transformation_record": {
            "exclusions": (
                [
                    {
                        "unit_key": ["392010", "imports", "2024"],
                        "selected_run_id": run_id,
                        "reason": exclusion_reason,
                    }
                ]
                if exclusion_reason
                else []
            )
        },
        "rows": rows or [],
        "evidence": [
            {
                "query_contract": {
                    "unit_key": ["392010", "imports", "2024"]
                },
                "retrieval": {
                    "endpoint_or_document": contract[
                        "endpoint_or_document"
                    ],
                    "retrieved_at": contract["retrieved_at"],
                },
                "source_identity": {"authority": "UN Comtrade"},
                "evidence_class": "B",
                "reviewer_status": "unconfirmed_by_responsible_authority",
            }
        ],
    }
    snapshot_path = root / "data" / "snapshots" / "partners"
    snapshot_path.mkdir(parents=True, exist_ok=True)
    (snapshot_path / f"{snapshot_id}.json").write_text(
        json.dumps(snapshot, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    brief["partner_snapshot_id"] = snapshot_id
    brief["partner_detail"].update(
        {
            "source_id": source_id,
            "partner_snapshot_id": snapshot_id,
            "attempts": [
                {
                    "source_id": source_id,
                    "query_hash": query_hash,
                    "run_id": run_id,
                    "endpoint_or_document": contract["endpoint_or_document"],
                    "http_status": 200,
                    "normalization_status": normalization_status,
                    "coverage_status": coverage_status,
                    "stop_reason": None,
                    "contract_path": contract_path.relative_to(root).as_posix(),
                    "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
                }
            ],
        }
    )


def test_partner_detail_exact_keys_schema_1_1_0_and_state_enum(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    validate_case_brief(brief, root=tmp_path)
    brief["partner_detail"]["extra"] = True
    with pytest.raises(ValueError, match="partner_detail keys"):
        validate_case_brief(brief, root=tmp_path)
    brief = _brief(_write_document(tmp_path))
    brief["partner_detail"]["state"] = "ZERO"
    with pytest.raises(ValueError, match="partner_detail.state"):
        validate_case_brief(brief, root=tmp_path)


def test_partner_detail_reason_set_equals_unavailable_reason_enum_plus_not_acquired_and_revision_mismatch() -> None:
    from ior_mvp.acquisition.contracts import UnavailableReason
    from ior_mvp.cases.brief import PARTNER_DETAIL_MISSING_REASONS

    assert PARTNER_DETAIL_MISSING_REASONS == frozenset(
        {reason.value for reason in UnavailableReason}
        | {"NOT_ACQUIRED", "REVISION_MISMATCH"}
    )


def test_partner_descriptions_unavailable_is_governed_reason_and_requires_matching_normalized_attempt(
    tmp_path: Path,
) -> None:
    from ior_mvp.acquisition.contracts import UnavailableReason
    from ior_mvp.cases.brief import (
        PARTNER_DETAIL_MISSING_REASONS,
        validate_case_brief,
    )

    reason = "PARTNER_DESCRIPTIONS_UNAVAILABLE"
    assert UnavailableReason.PARTNER_DESCRIPTIONS_UNAVAILABLE.value == reason
    assert reason in PARTNER_DETAIL_MISSING_REASONS

    brief = _brief(_write_document(tmp_path))
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="NORMALIZED",
        exclusion_reason=reason,
    )
    attempt = brief["partner_detail"]["attempts"][0]
    coverage_path = tmp_path / attempt["contract_path"]
    coverage_path = coverage_path.parent / "coverage.json"
    coverage = json.loads(coverage_path.read_text())
    coverage.update({"status": "INCOMPLETE", "stop_reason": reason})
    coverage_path.write_text(json.dumps(coverage, sort_keys=True) + "\n")
    attempt.update({"coverage_status": "INCOMPLETE", "stop_reason": reason})
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_MISSING",
            "reason": reason,
            "observed_partner_rows": "UNAVAILABLE",
        }
    )
    validate_case_brief(brief, root=tmp_path)

    contract_path = tmp_path / attempt["contract_path"]
    contract = json.loads(contract_path.read_text())
    contract["normalization_status"] = "UNPARSED"
    encoded = (json.dumps(contract, sort_keys=True) + "\n").encode()
    contract_path.write_bytes(encoded)
    attempt["normalization_status"] = "UNPARSED"
    attempt["contract_sha256"] = hashlib.sha256(encoded).hexdigest()
    with pytest.raises(ValueError, match="NORMALIZED"):
        validate_case_brief(brief, root=tmp_path)


def test_partner_detail_missing_requires_typed_reason_and_resolvable_stored_attempt(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
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
    validate_case_brief(brief, root=tmp_path)
    brief["partner_detail"]["attempts"][0]["contract_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="contract"):
        validate_case_brief(brief, root=tmp_path)


def test_partner_detail_missing_refused_when_named_unit_is_complete_and_normalized(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="NORMALIZED_EMPTY",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_DETAIL_MISSING",
            "reason": "FORMAT_NOT_PARSEABLE",
            "observed_partner_rows": "UNAVAILABLE",
        }
    )
    with pytest.raises(ValueError, match="MISSING"):
        validate_case_brief(brief, root=tmp_path)


def test_partner_detail_observed_zero_refused_when_unit_page_is_unparsed(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    _stored_partner_case(
        tmp_path,
        brief,
        normalization_status="UNPARSED",
        exclusion_reason="FORMAT_NOT_PARSEABLE",
    )
    brief["partner_detail"].update(
        {
            "state": "PARTNER_TRADE_OBSERVED_ZERO",
            "reason": None,
            "observed_partner_rows": 0,
        }
    )
    with pytest.raises(ValueError, match="ZERO"):
        validate_case_brief(brief, root=tmp_path)


def test_partner_detail_observed_requires_rows_and_matching_hs_revision(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
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
                "hs_revision": "H0",
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
    with pytest.raises(ValueError, match="revision"):
        validate_case_brief(brief, root=tmp_path)
    snapshot_path = next(
        (tmp_path / "data" / "snapshots" / "partners").glob("*.json")
    )
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot["rows"][0]["hs_revision"] = "H6"
    snapshot_path.write_text(
        json.dumps(snapshot, sort_keys=True) + "\n", encoding="utf-8"
    )
    validate_case_brief(brief, root=tmp_path)


def test_partner_detail_snapshot_id_equals_legacy_partner_snapshot_id(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["partner_detail"]["partner_snapshot_id"] = "OTHER"
    with pytest.raises(ValueError, match="partner_snapshot_id"):
        validate_case_brief(brief, root=tmp_path)


def test_exact_keys_and_versions(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    validate_case_brief(brief, root=tmp_path)
    extra = copy.deepcopy(brief)
    extra["extra"] = True
    with pytest.raises(ValueError, match="keys"):
        validate_case_brief(extra, root=tmp_path)


def test_span_must_be_verbatim_substring_of_document_line(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["spans"][0]["span_text"] = "invented identity"
    with pytest.raises(ValueError, match="verbatim"):
        validate_case_brief(brief, root=tmp_path)


def test_non_u_dimension_state_without_span_is_refused(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["capability"]["public_dimension_states"]["core_process_route"] = {
        "state": 0,
        "span_ids": [],
    }
    with pytest.raises(ValueError, match="dimension"):
        validate_case_brief(brief, root=tmp_path)


def test_numeric_nameplate_without_span_is_refused(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["capability"]["producer_evidence"] = [
        {
            "producer": "TEST PRODUCER",
            "process_family": "technical_plastics",
            "process_route": "UNAVAILABLE",
            "published_standards": "UNAVAILABLE",
            "installed_capacity_tpy": 1000,
            "span_ids": [],
        }
    ]
    with pytest.raises(ValueError, match="nameplate"):
        validate_case_brief(brief, root=tmp_path)


def test_resolved_gate_without_class_c_span_is_refused(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["capability"]["profile_hard_gates"]["conversion_route"] = {
        "status": "RESOLVED",
        "span_ids": [],
    }
    with pytest.raises(ValueError, match="gate"):
        validate_case_brief(brief, root=tmp_path)


def test_forbidden_decision_keys_are_refused(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    brief["capability"]["state"] = "INVESTIGATE"
    with pytest.raises(ValueError, match="decision"):
        validate_case_brief(brief, root=tmp_path)


def test_unavailable_partner_snapshot_literal_accepted(tmp_path: Path) -> None:
    from ior_mvp.cases.brief import validate_case_brief

    brief = _brief(_write_document(tmp_path))
    assert brief["partner_snapshot_id"] == "UNAVAILABLE"
    validate_case_brief(brief, root=tmp_path)


def test_case_cli_validates_and_builds_to_explicit_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from ior_mvp.cases import cli

    brief_path = tmp_path / "CASE-BRIEF-SAU-H6-392010-v1.json"
    brief_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(
        cli,
        "load_case_brief",
        lambda _path: {"brief_id": "CASE-BRIEF-SAU-H6-392010-v1"},
        raising=False,
    )
    built = tmp_path / "out" / "PUBLIC-SAU-H6-392010-2026-09-12.json"

    def fake_build(_brief_path: Path, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True)
        built.write_text("{}\n", encoding="utf-8")
        return built

    monkeypatch.setattr(
        cli, "build_brief_to_directory", fake_build, raising=False
    )
    assert cli.main(["validate-brief", "--brief", str(brief_path)]) == 0
    assert (
        cli.main(
            [
                "build",
                "--brief",
                str(brief_path),
                "--out",
                str(tmp_path / "out"),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "CASE BRIEF VALID" in output
    assert built.as_posix() in output
