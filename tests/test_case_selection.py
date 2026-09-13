"""Deterministic S14 case-selection rule."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT


def _record(
    hs6: str,
    *,
    imports: float,
    fired: tuple[str, ...] = ("R1-D",),
    disposition: str = "CANDIDATE",
    continuity: str = "REVISION_CHANGE_IN_WINDOW",
    price_led: bool = False,
    ratio_warning: bool = False,
) -> dict:
    return {
        "hs6": hs6,
        "screening_disposition": disposition,
        "fired_signal_rule_ids": list(fired),
        "metrics": {"imports_usd_m_latest": imports},
        "warnings": {
            "classification_continuity": {
                "pattern": "ABSENT_BEFORE_REVISION_CHANGE",
                "status": continuity,
            },
            "price_led_growth": price_led,
            "export_import_ratio_warning": ratio_warning,
        },
    }


def _trade(
    hs6: str,
    *,
    year: int = 2024,
    flow: str = "imports",
    value: float = 1_000_000,
    weight: float | None = 1_000_000,
    revision: str = "H6",
) -> dict:
    return {
        "hs6": hs6,
        "year": year,
        "flow": flow,
        "trade_value": value,
        "net_weight": weight,
        "hs_revision": revision,
    }


def _families() -> dict:
    return {
        "metadata": {"version": "1.1.0"},
        "families": {
            "steel": {
                "sector_profile": "coated_steel",
                "hs4_headings": ["7210"],
            },
            "plastics_primary": {
                "sector_profile": "technical_plastics",
                "hs4_headings": ["3902"],
            },
            "plastics_conversion": {
                "sector_profile": "technical_plastics",
                "hs4_headings": ["3917", "3920", "3921"],
            },
            "aluminium": {
                "sector_profile": "fabricated_aluminium",
                "hs4_headings": ["7604"],
            },
        },
    }


def _queues(*, robust=(), high=(), false_positive=()) -> dict:
    def block(codes: tuple[str, ...]) -> dict:
        return {"entries": [{"hs6": code} for code in codes]}

    return {
        "robust_public_finding": block(tuple(robust)),
        "high_evsi_evidence_investigation": block(tuple(high)),
        "likely_false_positive": block(tuple(false_positive)),
        "incumbent_upgrade_investigation": block(()),
        "resilience_case": block(()),
    }


def _terms(*rows: dict, rule_id: str = "S14-CS-1") -> dict:
    return {
        "schema_version": (
            "1.1.0" if rule_id == "S14-CS-1.1" else "1.0.0"
        ),
        "rule_id": rule_id,
        "rows": sorted(rows, key=lambda row: row["hs6"]),
    }


def _term_row(
    hs6: str,
    *,
    profile: str = "coated_steel",
    sources: tuple[str, ...] = ("producer_unicoil",),
    terms: tuple[str, ...] = ("Hot Dip GL",),
) -> dict:
    return {
        "hs6": hs6,
        "sector_profile": profile,
        "sources": list(sources),
        "terms": list(terms),
        "basis": "TITLE_VERIFICATION: UNAVAILABLE",
    }


def _select(
    records: list[dict],
    rows: list[dict],
    *,
    queues: dict | None = None,
    families: dict | None = None,
    terms: dict | None = None,
    documents: list[dict] | None = None,
    identity_exclusions: dict | None = None,
    quotas: dict[str, int] | None = None,
    frozen: frozenset[str] = frozenset(),
    rule_version: str = "S14-CS-1",
    owner_designations: list[dict] | None = None,
) -> dict:
    from ior_mvp.cases.selection import select_cases_from_records

    return select_cases_from_records(
        records=records,
        queues=queues
        or _queues(false_positive=tuple(record["hs6"] for record in records)),
        universe_rows=rows,
        families=families or _families(),
        quotas=quotas
        or {
            "coated_steel": 2,
            "fabricated_aluminium": 2,
            "technical_plastics": 1,
        },
        terms_bundle=terms or _terms(),
        document_records=documents or [],
        identity_exclusions=identity_exclusions
        or {"schema_version": "1.0.0", "rule_id": "S14-CS-1", "entries": []},
        frozen_hs6=frozen,
        rule_version=rule_version,
        owner_designations=owner_designations or [],
    )


def _v11_families() -> dict:
    return {
        "metadata": {"version": "1.2.0"},
        "families": {
            "pharma": {
                "sector_profile": "pharma_api",
                "hs4_headings": ["2941"],
            },
            "fertilizers": {
                "sector_profile": "fertilizers",
                "hs4_headings": ["3105"],
            },
        },
    }


def _v11_exclusions(*entries: dict) -> dict:
    return {
        "schema_version": "1.1.0",
        "rule_id": "S14-CS-1.1",
        "entries": sorted(entries, key=lambda row: row["hs6"]),
    }


def _wco_record(*, complete: bool = True) -> dict:
    return {
        "document_id": "DOC-WCO-TEST",
        "source_id": "wco_hs_nomenclature",
        "coverage": {"status": "COMPLETE" if complete else "INCOMPLETE"},
        "declared": {"publisher_kind": "nomenclature_authority"},
        "pages": [
            {
                "page_index": 7,
                "lines": [
                    "29.41 Antibiotics.",
                    "- Penicillins and their derivatives with a penicillanic acid structure; salts thereof:",
                    "2941.90 - Other",
                ],
            }
        ],
    }


def _identity_row(*, reason: str = "RESIDUAL_CATCH_ALL_SUBHEADING") -> dict:
    return {
        "hs6": "294190",
        "reason": reason,
        "hs_revision": "H6",
        "basis": {
            "parent_heading_text": "29.41 Antibiotics.",
            "one_dash_group_text": "2941.90 - Other",
            "subheading_text": "2941.90 - Other",
            "identity_judgment": (
                "Residual of heading 29.41; the remaining scope does not "
                "resolve one commercial product class."
            ),
        },
        "document_id": "DOC-WCO-TEST",
        "page_index": 7,
        "line_indices": [1, 3],
        "rule_version": "S14-CS-1.1",
    }


def test_membership_groups_families_by_sector_profile() -> None:
    from ior_mvp.cases.selection import family_headings_by_profile

    grouped = family_headings_by_profile(_families())
    assert grouped["technical_plastics"] == ("3902", "3917", "3920", "3921")
    assert grouped["coated_steel"] == ("7210",)
    assert "7604" not in grouped["technical_plastics"]


def test_tiers_follow_pr7_queue_order_then_warning_classes() -> None:
    from ior_mvp.cases.selection import queue_memberships, tier_of

    records = [
        _record("721011", imports=1),
        _record("721012", imports=1),
        _record("721013", imports=1),
    ]
    queues = _queues(
        robust=("721011",),
        high=("721012",),
        false_positive=("721013",),
    )
    memberships = queue_memberships(queues)
    assert tier_of(records[0], memberships)[:1] == (1,)
    assert tier_of(records[1], memberships)[:1] == (2,)
    assert tier_of(records[2], memberships)[:1] == (3,)


def test_continuity_only_warning_is_tier_3_price_led_tier_4_ratio_tier_5() -> None:
    from ior_mvp.cases.selection import queue_memberships, tier_of

    records = [
        _record("721011", imports=1),
        _record("721012", imports=1, price_led=True),
        _record("721013", imports=1, price_led=True, ratio_warning=True),
    ]
    memberships = queue_memberships(
        _queues(false_positive=tuple(row["hs6"] for row in records))
    )
    assert [tier_of(row, memberships)[0] for row in records] == [3, 4, 5]


def test_viability_requires_positive_latest_year_net_weight() -> None:
    records = [
        _record("721011", imports=3),
        _record("721012", imports=2),
        _record("721013", imports=1),
    ]
    rows = [
        _trade("721011", weight=1),
        _trade("721012", weight=None),
        _trade("721013", weight=0),
    ]
    selected = _select(
        records,
        rows,
        quotas={"coated_steel": 1},
    )
    profile = selected["profiles"]["coated_steel"]
    assert profile["selected"] == ["721011"]
    assert profile["excluded_by_viability"] == ["721012", "721013"]


def test_disclosure_coverage_uses_only_complete_producer_records_and_term_table() -> None:
    from ior_mvp.cases.selection import disclosure_covered

    row = _term_row("721061")
    complete = {
        "source_id": "producer_unicoil",
        "coverage": {"status": "COMPLETE"},
        "declared": {
            "publisher_kind": "producer",
            "title_text": "EPD-Report_for Hot Dip GL Steel Coil",
        },
        "pages": [],
        "document_id": "DOC-GL",
    }
    incomplete = copy.deepcopy(complete)
    incomplete["coverage"]["status"] = "INCOMPLETE"
    authority = copy.deepcopy(complete)
    authority["declared"]["publisher_kind"] = "standards_authority"
    assert disclosure_covered(row, [complete]) == ["DOC-GL"]
    assert disclosure_covered(row, [incomplete, authority]) == []


def test_in_tier_order_coverage_then_r2_then_imports_then_hs6() -> None:
    codes = ("721061", "721012", "721013", "721011")
    records = [
        _record("721061", imports=1),
        _record("721012", imports=2, fired=("R1-D", "R2")),
        _record("721013", imports=9),
        _record("721011", imports=9),
    ]
    rows = [_trade(code) for code in codes]
    terms = _terms(
        *[
            _term_row(
                code,
                terms=("Hot Dip GL",) if code == "721061" else (f"product {code}",),
            )
            for code in codes
        ]
    )
    document = {
        "source_id": "producer_unicoil",
        "coverage": {"status": "COMPLETE"},
        "declared": {
            "publisher_kind": "producer",
            "title_text": "Hot Dip GL",
        },
        "pages": [],
        "document_id": "DOC-GL",
    }
    selected = _select(
        records,
        rows,
        terms=terms,
        documents=[document],
        quotas={"coated_steel": 1},
    )
    profile = selected["profiles"]["coated_steel"]
    assert profile["selected"] == ["721061"]
    assert profile["substitution_order"] == ["721012", "721011", "721013"]


def test_quota_and_substitution_order_per_profile() -> None:
    records = [
        _record("721011", imports=3),
        _record("721012", imports=2),
        _record("721013", imports=1),
        _record("760411", imports=3),
        _record("760412", imports=2),
        _record("392010", imports=3),
        _record("392020", imports=2),
    ]
    rows = [_trade(record["hs6"]) for record in records]
    result = _select(
        records,
        rows,
        quotas={
            "coated_steel": 2,
            "fabricated_aluminium": 1,
            "technical_plastics": 1,
        },
    )
    assert result["profiles"]["coated_steel"]["selected"] == ["721011", "721012"]
    assert result["profiles"]["coated_steel"]["substitution_order"] == ["721013"]
    assert result["profiles"]["fabricated_aluminium"]["selected"] == ["760411"]
    assert result["profiles"]["technical_plastics"]["selected"] == ["392010"]


def test_output_is_canonical_write_once_with_inputs_hashes(tmp_path: Path) -> None:
    from ior_mvp.cases.selection import canonical_bytes, write_selection

    payload = {
        "schema_version": "1.0.0",
        "selection_id": "CASE-SELECTION-S14-test",
        "rule_id": "S14-CS-1",
        "inputs": {
            "identity_exclusions": {"sha256": "a" * 64},
            "terms": {"sha256": "b" * 64},
        },
        "profiles": {},
        "selected_hs6": ["392010", "721012"],
    }
    path = write_selection(payload, tmp_path)
    assert path.read_bytes() == canonical_bytes(payload)
    assert write_selection(payload, tmp_path) == path
    changed = copy.deepcopy(payload)
    changed["selected_hs6"].append("721061")
    with pytest.raises(ValueError, match="write conflict"):
        write_selection(changed, tmp_path)

    candidates = {
        "candidate_source": payload["selection_id"],
        "hs6_codes": sorted(["392010", "721012"]),
        "recorded_on": "2026-09-13",
    }
    assert candidates["hs6_codes"] == sorted(payload["selected_hs6"])


def test_no_candidate_and_screened_out_are_never_selected() -> None:
    records = [
        _record("721011", imports=3, disposition="NO_CANDIDATE"),
        _record("721012", imports=2, disposition="SCREENED_OUT"),
        _record("721013", imports=1),
    ]
    rows = [_trade(record["hs6"]) for record in records]
    result = _select(records, rows, quotas={"coated_steel": 3})
    assert result["profiles"]["coated_steel"]["selected"] == ["721013"]


def test_identity_exclusion_applies_before_quota_and_keeps_unrelated_other_code() -> None:
    records = [
        _record("392190", imports=100, fired=("R1-D", "R2")),
        _record("392010", imports=50, fired=("R1-D", "R2")),
        _record("391739", imports=25, fired=("R1-D", "R2")),
        _record("760429", imports=10, fired=("R1-D", "R2")),
    ]
    rows = [_trade(record["hs6"]) for record in records]
    exclusions = {
        "schema_version": "1.0.0",
        "rule_id": "S14-CS-1",
        "entries": [
            {
                "hs6": "392190",
                "reason": "RESIDUAL_CATCH_ALL_SUBHEADING",
                "basis": "TITLE_VERIFICATION: UNAVAILABLE",
            }
        ],
    }
    result = _select(
        records,
        rows,
        identity_exclusions=exclusions,
        quotas={"technical_plastics": 1, "fabricated_aluminium": 1},
    )
    plastics = result["profiles"]["technical_plastics"]
    assert plastics["selected"] == ["392010"]
    assert plastics["substitution_order"] == ["391739"]
    assert plastics["excluded_by_identity"] == [
        {
            "hs6": "392190",
            "reason": "RESIDUAL_CATCH_ALL_SUBHEADING",
        }
    ]
    assert result["profiles"]["fabricated_aluminium"]["selected"] == ["760429"]


def test_disclosure_coverage_ignores_records_from_sources_not_listed_for_hs6() -> None:
    from ior_mvp.cases.selection import disclosure_covered

    row = _term_row("721061", sources=("producer_unicoil",))
    record = {
        "source_id": "producer_hadeed",
        "coverage": {"status": "COMPLETE"},
        "declared": {
            "publisher_kind": "producer",
            "title_text": "Hot Dip GL",
        },
        "pages": [],
        "document_id": "DOC-OTHER",
    }
    assert disclosure_covered(row, [record]) == []
    record["source_id"] = "producer_unicoil"
    assert disclosure_covered(row, [record]) == ["DOC-OTHER"]


def test_terms_table_rows_have_profile_sources_and_non_generic_terms() -> None:
    from ior_mvp.cases.selection import validate_terms_bundle

    valid = _terms(
        _term_row("392010", profile="technical_plastics", sources=(), terms=("polymers of ethylene",)),
        _term_row("721061"),
    )
    validate_terms_bundle(valid, expected_hs6={"392010", "721061"})
    invalid = copy.deepcopy(valid)
    invalid["rows"][0]["terms"] = ["film"]
    with pytest.raises(ValueError, match="generic"):
        validate_terms_bundle(invalid, expected_hs6={"392010", "721061"})


def test_gap_years_candidate_is_excluded_series_gap_years_before_tiering_regardless_of_flags() -> None:
    records = [
        _record("294110", imports=5),
        _record("294120", imports=4, continuity="GAP_YEARS"),
        _record("294130", imports=3, continuity="GAP_YEARS", price_led=True),
        _record("294140", imports=2, continuity="GAP_YEARS", ratio_warning=True),
    ]
    rows = [
        _trade(code, year=2022)
        for code in ("294110", "294120", "294130", "294140")
    ] + [
        _trade(code, year=2024)
        for code in ("294110", "294120", "294130", "294140")
    ] + [
        _trade("294110", year=2023),
    ]
    terms = _terms(
        *[
            _term_row(
                row["hs6"],
                profile="pharma_api",
                sources=(),
                terms=(f"molecule {row['hs6']}",),
            )
            for row in records
        ],
        rule_id="S14-CS-1.1",
    )
    result = _select(
        records,
        rows,
        families=_v11_families(),
        terms=terms,
        identity_exclusions=_v11_exclusions(),
        quotas={"pharma_api": 2},
        rule_version="S14-CS-1.1",
    )
    profile = result["profiles"]["pharma_api"]
    assert profile["selected"] == ["294110"]
    assert [
        row["hs6"] for row in profile["excluded_series_gap_years"]
    ] == ["294120", "294130", "294140"]


def test_gap_years_row_records_missing_import_years_from_universe_and_basis() -> None:
    record = _record("310530", imports=2, continuity="GAP_YEARS", ratio_warning=True)
    rows = [
        _trade("310530", year=2021, flow="exports"),
        _trade("310530", year=2022),
        _trade("310530", year=2024),
    ]
    terms = _terms(
        _term_row(
            "310530",
            profile="fertilizers",
            sources=(),
            terms=("diammonium hydrogenorthophosphate",),
        ),
        rule_id="S14-CS-1.1",
    )
    result = _select(
        [record],
        rows,
        families=_v11_families(),
        terms=terms,
        identity_exclusions=_v11_exclusions(),
        quotas={"fertilizers": 1},
        rule_version="S14-CS-1.1",
    )
    [excluded] = result["profiles"]["fertilizers"][
        "excluded_series_gap_years"
    ]
    assert excluded["hs6"] == "310530"
    assert excluded["reason"] == "SERIES_GAP_YEARS"
    assert excluded["missing_import_years"] == [2021, 2023]
    assert excluded["rule_version"] == "S14-CS-1.1"
    assert excluded["hs_revisions"] == ["H6"]
    assert excluded["basis"] == (
        "Persistence rules need a continuous series; missing years are not "
        "zero trade. Screening continuity is GAP_YEARS; missing import years "
        "[2021, 2023]."
    )


def test_rule_1_0_still_raises_for_fail_closed_gap_years() -> None:
    with pytest.raises(
        ValueError,
        match="tier-3 record must carry a classification-continuity warning",
    ):
        _select(
            [_record("721011", imports=1, continuity="GAP_YEARS")],
            [_trade("721011")],
            quotas={"coated_steel": 1},
            rule_version="S14-CS-1",
        )


def test_identity_row_requires_complete_wco_record_and_verbatim_address() -> None:
    from ior_mvp.cases.selection import validate_identity_exclusions

    payload = _v11_exclusions(_identity_row())
    validate_identity_exclusions(payload, documents=[_wco_record()])

    with pytest.raises(ValueError, match="COMPLETE wco_hs_nomenclature"):
        validate_identity_exclusions(
            payload,
            documents=[_wco_record(complete=False)],
        )

    changed = copy.deepcopy(payload)
    changed["entries"][0]["basis"]["subheading_text"] = "2941.90 - Not stored"
    with pytest.raises(ValueError, match="verbatim stored line"):
        validate_identity_exclusions(changed, documents=[_wco_record()])

    changed = copy.deepcopy(payload)
    changed["entries"][0]["line_indices"] = [1, 2]
    with pytest.raises(ValueError, match="verbatim stored line"):
        validate_identity_exclusions(changed, documents=[_wco_record()])


def test_identity_row_supports_multi_page_wco_group_address() -> None:
    from ior_mvp.cases.selection import validate_identity_exclusions

    document = _wco_record()
    document["document_id"] = "DOC-WCO-31"
    document["pages"] = [
        {
            "page_index": 2,
            "lines": [
                "31.05 Mineral or chemical fertilisers containing two or three of the fertilising elements."
            ],
        },
        {
            "page_index": 3,
            "lines": ["3105.90 - Other"],
        },
    ]
    row = _identity_row()
    row.update(
        {
            "hs6": "310590",
            "document_id": "DOC-WCO-31",
            "basis": {
                "parent_heading_text": (
                    "31.05 Mineral or chemical fertilisers containing two or "
                    "three of the fertilising elements."
                ),
                "one_dash_group_text": "3105.90 - Other",
                "subheading_text": "3105.90 - Other",
                "identity_judgment": (
                    "Residual of heading 31.05; the remaining scope does not "
                    "resolve one commercial product class."
                ),
            },
            "page_index": {
                "parent_heading_text": 2,
                "one_dash_group_text": 3,
                "subheading_text": 3,
            },
            "line_indices": {
                "parent_heading_text": [1],
                "one_dash_group_text": [1],
                "subheading_text": [1],
            },
        }
    )
    validate_identity_exclusions(
        _v11_exclusions(row),
        documents=[document],
    )

    changed = copy.deepcopy(row)
    changed["line_indices"]["parent_heading_text"] = [2]
    with pytest.raises(ValueError, match="page/line address"):
        validate_identity_exclusions(
            _v11_exclusions(changed),
            documents=[document],
        )


def test_identity_row_reason_must_be_governed() -> None:
    from ior_mvp.cases.selection import validate_identity_exclusions

    with pytest.raises(ValueError, match="identity exclusion reason"):
        validate_identity_exclusions(
            _v11_exclusions(_identity_row(reason="OTHER")),
            documents=[_wco_record()],
        )


def test_output_schema_1_1_0_adds_rule_version_gap_exclusions_and_owner_designations() -> None:
    owner_designation = {
        "hs6": "310560",
        "reason": "OWNER_WAIVER_MONITOR_DEMONSTRATION",
        "ruling_reference": "OD-4-ALTERNATIVE",
    }
    terms = _terms(
        _term_row(
            "310510",
            profile="fertilizers",
            sources=(),
            terms=("fertilisers in packages not exceeding 10 kg",),
        ),
        rule_id="S14-CS-1.1",
    )
    result = _select(
        [_record("310510", imports=1)],
        [_trade("310510")],
        families=_v11_families(),
        terms=terms,
        identity_exclusions=_v11_exclusions(),
        quotas={"fertilizers": 1},
        rule_version="S14-CS-1.1",
        owner_designations=[owner_designation],
    )
    assert result["schema_version"] == "1.1.0"
    assert result["rule_version"] == "S14-CS-1.1"
    assert result["owner_designated_cases"] == [owner_designation]
    assert result["profiles"]["fertilizers"]["excluded_series_gap_years"] == []


def test_write_selection_prefix_follows_schema_version(tmp_path: Path) -> None:
    from ior_mvp.cases.selection import write_selection

    s14 = {
        "schema_version": "1.0.0",
        "selection_id": "CASE-SELECTION-S14-test",
        "rule_id": "S14-CS-1",
    }
    s15 = {
        "schema_version": "1.1.0",
        "selection_id": "CASE-SELECTION-S15-test",
        "rule_id": "S14-CS-1.1",
        "rule_version": "S14-CS-1.1",
    }
    assert write_selection(s14, tmp_path).name == "CASE-SELECTION-S14-test.json"
    assert write_selection(s15, tmp_path).name == "CASE-SELECTION-S15-test.json"
    with pytest.raises(ValueError, match="record prefix"):
        write_selection(s15, tmp_path, record_prefix="CASE-SELECTION-S14-")


def test_families_identity_resolves_live_or_history_by_hash_else_inputs_changed(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.selection import resolve_recorded_input

    config_root = tmp_path / "config"
    history_root = config_root / "history"
    history_root.mkdir(parents=True)
    live = config_root / "product_families.v1.yaml"
    live.write_text("metadata:\n  version: 1.2.0\n", encoding="utf-8")
    retained = history_root / "product_families.v1-1.1.0.yaml"
    retained_bytes = b"metadata:\n  version: 1.1.0\n"
    retained.write_bytes(retained_bytes)
    identity = {
        "path": "config/product_families.v1.yaml",
        "sha256": hashlib.sha256(retained_bytes).hexdigest(),
    }
    assert resolve_recorded_input(identity, root=tmp_path) == retained
    live.write_bytes(retained_bytes)
    assert resolve_recorded_input(identity, root=tmp_path) == live
    live.write_text("metadata:\n  version: 1.2.0\n", encoding="utf-8")
    duplicate = history_root / "duplicate.yaml"
    duplicate.write_bytes(retained_bytes)
    with pytest.raises(ValueError, match="ambiguous retained config"):
        resolve_recorded_input(identity, root=tmp_path)
    duplicate.unlink()
    with pytest.raises(ValueError, match="INPUTS_CHANGED"):
        resolve_recorded_input(
            {**identity, "sha256": "f" * 64},
            root=tmp_path,
        )


def test_reconstruct_selection_reproduces_bytes_and_refuses_changed_inputs(
    tmp_path: Path,
) -> None:
    from ior_mvp.cases.selection import (
        canonical_bytes,
        load_selection,
        reconstruct_selection,
    )

    selection_root = PROJECT_ROOT / "data" / "cases" / "selection"
    [record_path] = sorted(selection_root.glob("CASE-SELECTION-S14-*.json"))
    assert reconstruct_selection(record_path, root=PROJECT_ROOT) == record_path.read_bytes()

    changed = load_selection(record_path)
    changed["inputs"]["terms"]["sha256"] = "f" * 64
    changed_path = tmp_path / f"{changed['selection_id']}.json"
    changed_path.write_bytes(canonical_bytes(changed))
    with pytest.raises(ValueError, match="INPUTS_CHANGED"):
        reconstruct_selection(changed_path, root=PROJECT_ROOT)


def test_owner_designated_rows_do_not_alter_selected_or_substitution_lists() -> None:
    records = [
        _record("310510", imports=2),
        _record("310520", imports=1),
    ]
    rows = [_trade(record["hs6"]) for record in records]
    terms = _terms(
        *[
            _term_row(
                row["hs6"],
                profile="fertilizers",
                sources=(),
                terms=(f"fertilizer product {row['hs6']}",),
            )
            for row in records
        ],
        rule_id="S14-CS-1.1",
    )
    kwargs = {
        "families": _v11_families(),
        "terms": terms,
        "identity_exclusions": _v11_exclusions(),
        "quotas": {"fertilizers": 1},
        "rule_version": "S14-CS-1.1",
    }
    ordinary = _select(records, rows, **kwargs)
    designated = _select(
        records,
        rows,
        owner_designations=[
            {
                "hs6": "310560",
                "reason": "OWNER_WAIVER_MONITOR_DEMONSTRATION",
                "ruling_reference": "OD-4-ALTERNATIVE",
            }
        ],
        **kwargs,
    )
    for field in ("selected", "substitution_order"):
        assert (
            designated["profiles"]["fertilizers"][field]
            == ordinary["profiles"]["fertilizers"][field]
        )


def test_select_cli_writes_canonical_record_and_reports_profiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from ior_mvp.cases import cli

    record = {
        "schema_version": "1.0.0",
        "selection_id": "CASE-SELECTION-S14-test",
        "rule_id": "S14-CS-1",
        "inputs": {
            "identity_exclusions": {"sha256": "a" * 64},
            "terms": {"sha256": "b" * 64},
        },
        "profiles": {
            "technical_plastics": {
                "selected": ["392010"],
                "substitution_order": ["391739"],
                "excluded_series_gap_years": [],
                "excluded_by_identity": [
                    {
                        "hs6": "392190",
                        "reason": "RESIDUAL_CATCH_ALL_SUBHEADING",
                    }
                ],
                "excluded_frozen": ["390210"],
                "excluded_by_viability": [],
            }
        },
        "selected_hs6": ["392010"],
    }
    called = {}

    def fake_select_cases(**kwargs):
        called.update(kwargs)
        return record

    monkeypatch.setattr(cli, "select_cases", fake_select_cases)
    code = cli.main(
        [
            "select",
            "--rule-version",
            "S14-CS-1",
            "--record-prefix",
            "CASE-SELECTION-S14-",
            "--screening",
            "screening",
            "--universe",
            "universe.json",
            "--families",
            "families.yaml",
            "--terms",
            "terms.json",
            "--identity-exclusions",
            "identity-exclusions.json",
            "--documents-root",
            "documents",
            "--quota",
            "technical_plastics=1",
            "--out",
            str(tmp_path),
        ]
    )
    assert code == 0
    assert (tmp_path / "CASE-SELECTION-S14-test.json").is_file()
    output = capsys.readouterr().out
    assert "CASE SELECTION PASS (1 selected; 1 profiles" in output
    assert "technical_plastics: 392010 (runner-up 391739" in output
    assert "identity_exclusions sha256=" + "a" * 64 in output
    assert called["rule_version"] == "S14-CS-1"


def test_s14_selection_reproduces_from_recorded_inputs_with_families_1_2_0_live() -> None:
    from ior_mvp.cases.selection import load_selection, select_cases

    selection_root = PROJECT_ROOT / "data" / "cases" / "selection"
    recorded_paths = sorted(selection_root.glob("CASE-SELECTION-S14-*.json"))
    assert len(recorded_paths) == 1
    recorded = load_selection(recorded_paths[0])
    families_live = json.loads(
        json.dumps(
            __import__("yaml").safe_load(
                (PROJECT_ROOT / "config" / "product_families.v1.yaml").read_text(
                    encoding="utf-8"
                )
            )
        )
    )
    assert families_live["metadata"]["version"] == "1.2.0"
    generated = select_cases(
        screening_dir=(
            PROJECT_ROOT
            / "data"
            / "screening"
            / "snapshots"
            / "SCREENING-SAU-2026-09-12-9b6b22032fd8"
        ),
        universe_path=(
            PROJECT_ROOT
            / "data"
            / "snapshots"
            / "universe"
            / "UNIVERSE-SAU-UN-COMTRADE-HS-2026-09-12.json"
        ),
        families_path=PROJECT_ROOT / "config" / "product_families.v1.yaml",
        families_identity=recorded["inputs"]["product_families"],
        quotas={
            "coated_steel": 2,
            "fabricated_aluminium": 2,
            "technical_plastics": 1,
        },
        terms_path=selection_root / "hs6-disclosure-terms-v1.json",
        identity_exclusions_path=selection_root / "identity-exclusions-v1.json",
        documents_root=PROJECT_ROOT / "data" / "documents",
        frozen_hs6=frozenset({"721049", "390210"}),
        rule_version="S14-CS-1",
    )
    assert generated == recorded
    assert generated["profiles"]["coated_steel"]["selected"] == ["721061", "721012"]
    assert generated["profiles"]["fabricated_aluminium"]["selected"] == ["760711", "760429"]
    plastics = generated["profiles"]["technical_plastics"]
    assert plastics["selected"] == ["392010"]
    assert plastics["substitution_order"][0] == "391739"
    assert plastics["excluded_by_identity"] == [
        {
            "hs6": "392190",
            "reason": "RESIDUAL_CATCH_ALL_SUBHEADING",
        }
    ]
    assert "392190" not in generated["selected_hs6"]
    assert "760429" in generated["selected_hs6"]
    assert hashlib.sha256(recorded_paths[0].read_bytes()).hexdigest()
    candidates = json.loads(
        (selection_root / "wits-partners-s14-v1.json").read_text(encoding="utf-8")
    )
    assert candidates["hs6_codes"] == sorted(generated["selected_hs6"])


def test_s15_selection_from_frozen_screening_snapshot_matches_recorded_list() -> None:
    from ior_mvp.cases.selection import load_selection, reconstruct_selection

    selection_root = PROJECT_ROOT / "data" / "cases" / "selection"
    recorded_paths = sorted(selection_root.glob("CASE-SELECTION-S15-*.json"))
    assert len(recorded_paths) == 1
    recorded_path = recorded_paths[0]
    recorded = load_selection(recorded_path)
    assert reconstruct_selection(recorded_path, root=PROJECT_ROOT) == (
        recorded_path.read_bytes()
    )
    assert recorded["rule_version"] == "S14-CS-1.1"
    assert recorded["profiles"]["pharma_api"]["selected"] == [
        "294110",
        "294120",
    ]
    assert recorded["profiles"]["fertilizers"]["selected"] == [
        "310430",
        "310510",
    ]
    assert [
        row["hs6"]
        for row in recorded["profiles"]["pharma_api"][
            "excluded_series_gap_years"
        ]
    ] == ["293723", "293919"]
    assert [
        row["hs6"]
        for row in recorded["profiles"]["fertilizers"][
            "excluded_series_gap_years"
        ]
    ] == ["310229", "310530", "310551", "310560"]
    assert [
        row["hs6"]
        for row in recorded["profiles"]["pharma_api"]["excluded_by_identity"]
    ] == ["293339", "294190"]
    assert [
        row["hs6"]
        for row in recorded["profiles"]["fertilizers"][
            "excluded_by_identity"
        ]
    ] == ["310590"]
    assert recorded["profiles"]["pharma_api"]["excluded_by_viability"] == [
        "293711"
    ]
    assert recorded["profiles"]["fertilizers"]["excluded_by_viability"] == [
        "310420"
    ]
    assert recorded["owner_designated_cases"] == []
    candidates = json.loads(
        (
            selection_root / "comtrade-partners-s15-v1.json"
        ).read_text(encoding="utf-8")
    )
    assert candidates["candidate_source"] == recorded["selection_id"]
    assert candidates["hs6_codes"] == sorted(recorded["selected_hs6"])


def test_makefile_wires_case_selection_reconstruction() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "reconstruct-selection:" in makefile
    assert "python -m ior_mvp.cases reconstruct-selection" in makefile

