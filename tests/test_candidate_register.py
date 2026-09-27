from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.candidate_register import (
    canonical_register_sha256,
    validate_candidate_register,
)
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.scenario_contract import validate_simulation_contract

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "data" / "synthetic" / "historical" / "v2_0"


def _scenario(name: str) -> dict:
    return json.loads(
        (ROOT / "data" / "synthetic" / name).read_text(encoding="utf-8")
    )


def test_steel_and_pp_share_one_register_and_keep_legacy_leaves() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    polypropylene = _scenario("SYN-MINISTRY-PP-001.json")
    archived_steel = json.loads(
        (HISTORICAL / "SYN-MINISTRY-STEEL-001.json").read_text(encoding="utf-8")
    )
    validate_simulation_contract(steel)
    validate_simulation_contract(polypropylene)
    assert canonical_register_sha256(
        steel["synthetic_inputs"]["candidate_register"]
    ) == canonical_register_sha256(
        polypropylene["synthetic_inputs"]["candidate_register"]
    )
    assert steel["synthetic_inputs"]["plant_line"] == archived_steel[
        "synthetic_inputs"
    ]["plant_line"]
    assert steel["ground_truth"] == archived_steel["ground_truth"]
    assert steel["synthetic_inputs"]["economics"] == archived_steel[
        "synthetic_inputs"
    ]["economics"]


def test_mirrored_qualification_application_scopes_follow_fact_identity() -> None:
    expected = {
        "FACT-QUAL-LINE-7315366f6a9166d8": "coastal construction panels",
        "FACT-QUAL-LINE-96f1bd96c5c6ccda": "coastal construction panels",
        "FACT-QUAL-LINE-4fbdbb0b2c107968": "coastal construction panels",
        "FACT-QUAL-LINE-e403e85a85052861": "general rigid packaging",
        "FACT-QUAL-LINE-cb9a42384c3523ec": "general rigid packaging",
    }
    registers = [
        _scenario(name)["synthetic_inputs"]["candidate_register"]
        for name in ("SYN-MINISTRY-STEEL-001.json", "SYN-MINISTRY-PP-001.json")
    ]
    assert registers[0] == registers[1]
    for register in registers:
        assert {
            fact["fact_id"]: fact["values"]["application"]
            for fact in register["facts"] if fact["kind"] == "QUALIFICATION"
        } == expected


def test_earlier_versions_reject_the_register() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    steel["scenario_version"] = "2.0.0"
    with pytest.raises(EvidenceIntegrityError, match="2.2.0"):
        validate_simulation_contract(steel)


def test_unknown_register_key_fails_closed() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    register["companies"][0]["description_tag"] = "GALVANISING_EQUIPMENT_DEMO"
    with pytest.raises(EvidenceIntegrityError, match="keys mismatch"):
        validate_candidate_register(register)


def test_valid_h0_identity_validates_and_is_not_an_h6_match() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    customs = next(
        fact for fact in register["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A"
    )
    customs["values"]["hs_revision"] = "H0"
    customs["values"]["hs6"] = "790111"
    validate_candidate_register(register)
    from ior_mvp.candidate_discovery import discover_candidates

    found = discover_candidates(
        register,
        opportunity_id=steel["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=steel["synthetic_inputs"]["candidate_lines"],
        scenario_id=steel["scenario_id"],
    )
    plant = next(
        row for row in found["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8"
    )
    procurement = next(item for item in plant["findings"] if item["rule_id"] == "P03")
    assert procurement["status"] == "NOT_ESTABLISHED"


def test_cumulative_allocation_cannot_exceed_source_quantity() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    company_id = "COMPANY-ed24005b198e52e5"
    customs = next(
        fact for fact in register["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A"
    )
    customs["subject_type"] = "COMPANY"
    customs["subject_id"] = company_id
    customs["values"]["quantity_kt"] = 1
    second = "PLANT-aaaaaaaaaaaaaaaa"
    register["plants"].append(
        {
            "plant_id": second,
            "company_id": company_id,
            "country": "SA",
            "status": "OPERATING",
            "registry_fact_ids": ["FACT-REG-CUMULATIVE"],
        }
    )
    register["facts"].append(
        {
            "fact_id": "FACT-REG-CUMULATIVE",
            "kind": "REGISTRY_ACTIVITY",
            "dataset_kind": "REGISTRY",
            "subject_type": "PLANT",
            "subject_id": second,
            "window": {"start": "2026-06-30", "end": "2026-07-01"},
            "values": {
                "country": "SA",
                "status": "OPERATING",
                "product_family": "coated_steel",
                "process_route": "HOT_DIP_GALVANISING",
                "operating_status_asserted_by_registry": True,
            },
            "origin": "DIRECT_RECORD",
            "source_refs": [{
                "pointer": "/synthetic_inputs/candidate_register/facts/FACT-REG-CUMULATIVE",
                "purpose": "class_d_demonstration",
            }],
            "rule_id": None,
        }
    )
    link = next(
        row
        for row in register["attribution_links"]
        if row["attribution_id"] == "ATTR-STEEL-A-ZN"
    )
    link["allocated_quantity"] = 0.6
    extra = deepcopy(link)
    extra["attribution_id"] = "ATTR-STEEL-A-ZN-B"
    extra["plant_id"] = second
    register["attribution_links"].append(extra)
    with pytest.raises(EvidenceIntegrityError, match="cumulative"):
        validate_candidate_register(register)


def test_effort_requires_the_nine_configured_dimensions() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    effort = next(
        fact
        for fact in register["facts"]
        if fact["fact_id"] == "FACT-EFF-LINE-7315366f6a9166d8"
    )
    del effort["values"]["skills_market_integration"]
    with pytest.raises(EvidenceIntegrityError, match="effort"):
        validate_candidate_register(register)


def test_malformed_identity_fails() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    register["companies"][0]["company_id"] = "COMPANY-not-an-id"
    with pytest.raises(EvidenceIntegrityError, match="identity"):
        validate_candidate_register(register)


def test_four_digit_heading_is_not_an_hs6_value() -> None:
    steel = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = deepcopy(steel["synthetic_inputs"]["candidate_register"])
    customs = next(
        fact for fact in register["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A"
    )
    customs["values"]["hs6"] = "7901"
    with pytest.raises(EvidenceIntegrityError, match="hs6"):
        validate_candidate_register(register)


@pytest.mark.parametrize("kind", ["PRODUCTION_ACTUAL", "FACTORY_CUSTOMS"])
def test_recorded_quantity_cannot_be_negative(kind: str) -> None:
    scenario = _scenario("SYN-MINISTRY-STEEL-001.json")
    register = scenario["synthetic_inputs"]["candidate_register"]
    fact = next(row for row in register["facts"] if row["kind"] == kind)
    fact["values"]["quantity_kt"] = -1
    with pytest.raises(EvidenceIntegrityError, match="quantity"):
        validate_candidate_register(register)


def test_unused_technical_fact_still_requires_its_field_unit_and_range() -> None:
    register = _scenario("SYN-MINISTRY-STEEL-001.json")[
        "synthetic_inputs"
    ]["candidate_register"]
    fact = next(
        row for row in register["facts"]
        if row["kind"] == "TECHNICAL_FIELD"
        and row["values"]["field_id"] == "width_mm"
    )
    fact["values"]["unit"] = "cm"
    with pytest.raises(EvidenceIntegrityError, match="technical unit"):
        validate_candidate_register(register)


def test_local_source_pointer_must_match_its_fact_subject() -> None:
    register = _scenario("SYN-MINISTRY-STEEL-001.json")[
        "synthetic_inputs"
    ]["candidate_register"]
    customs = next(
        row for row in register["facts"] if row["fact_id"] == "FACT-CUS-STEEL-A"
    )
    other = next(row for row in register["facts"] if row["kind"] == "APPLICATION")
    customs["source_refs"][0]["pointer"] = (
        "/synthetic_inputs/candidate_register/facts/" + other["fact_id"]
    )
    with pytest.raises(EvidenceIntegrityError, match="local subject"):
        validate_candidate_register(register)


def test_coverage_rejects_duplicate_subject_and_duplicate_id() -> None:
    register = _scenario("SYN-MINISTRY-STEEL-001.json")[
        "synthetic_inputs"
    ]["candidate_register"]
    row = register["coverage"][0]
    row["covered_subject_ids"].append(row["covered_subject_ids"][0])
    with pytest.raises(EvidenceIntegrityError, match="repeats"):
        validate_candidate_register(register)
    row["covered_subject_ids"].pop()
    register["coverage"].append(deepcopy(row))
    with pytest.raises(EvidenceIntegrityError, match="duplicate coverage_id"):
        validate_candidate_register(register)
