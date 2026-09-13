from __future__ import annotations

import json
from pathlib import Path

from ior_mvp.acquisition.entities.mentions import (
    load_mention_list,
    verify_mentions,
)
from ior_mvp.acquisition.entities.store import (
    default_document_loader,
    default_snapshot_loader,
    validate_entity_artifact,
)
from ior_mvp.config import PROJECT_ROOT

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "data"
    / "entities"
    / "resolution"
    / "ENTITIES-2026-09-12-a12e24c31b02.json"
)
MENTION_PATH = (
    PROJECT_ROOT / "data" / "entities" / "mentions" / "mentions-v1.json"
)


def _artifact() -> dict:
    value = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    validate_entity_artifact(value)
    return value


def test_real_entity_resolution_artifact_pins_dd14_entities_and_links() -> None:
    artifact = _artifact()
    assert artifact["counts"]["entities_by_type"] == {
        "COMPANY": 5,
        "PLANT": 2,
        "LINE": 0,
        "LICENCE_HOLDER": 0,
    }
    companies = {
        item["primary_name_en"]
        for item in artifact["entities"]
        if item["entity_type"] == "COMPANY"
    }
    assert companies == {
        "Universal Metal Coating Company",
        "Hadeed",
        "SABIC",
        "Advanced Petrochemical",
        "Tasnee",
    }
    plants = {
        item["locality_token"]: item
        for item in artifact["entities"]
        if item["entity_type"] == "PLANT"
    }
    assert set(plants) == {"SAU-JUBAIL", "SAU-JEDDAH"}
    assert {item["granularity"] for item in plants.values()} == {"SITE_LOCALITY"}
    assert plants["SAU-JUBAIL"]["evidence_mention_ids"] == ["M-005", "M-013"]
    assert plants["SAU-JEDDAH"]["evidence_mention_ids"] == ["M-006", "M-014"]
    assert all(
        item["jurisdiction"] == "UNAVAILABLE"
        and item["primary_name_ar"] == "UNAVAILABLE"
        for item in artifact["entities"]
    )

    expected_pending = {
        "M-009": "LOCALITY_VARIANT",
        "M-017": "SUBJECT_OUTSIDE_WINDOW",
        "M-020": "VARIANT_NAME_EQUALITY",
    }
    expected_unresolved = {
        "M-007": "COUNT_ONLY_NO_IDENTITY",
        **{
            f"M-{number:03d}": "OUT_OF_SCOPE_ENTITY_TYPE"
            for number in range(21, 28)
        },
    }
    links = {item["mention_id"]: item for item in artifact["links"]}
    assert set(links) == {f"M-{number:03d}" for number in range(1, 39)}
    for mention_id, link in links.items():
        if mention_id in expected_pending:
            assert link["link_status"] == "PROPOSED_PENDING_REVIEW"
            assert link["rule_applied"] == expected_pending[mention_id]
        elif mention_id in expected_unresolved:
            assert link["link_status"] == "UNRESOLVED"
            assert link["unresolved_reason"] == expected_unresolved[mention_id]
        else:
            assert link["link_status"] == "EXACT_DOCUMENT_EVIDENCE"
    assert artifact["counts"]["links_by_status"] == {
        "DETERMINISTIC_IDENTIFIER": 0,
        "EXACT_DOCUMENT_EVIDENCE": 27,
        "PROPOSED_PENDING_REVIEW": 3,
        "UNRESOLVED": 8,
    }


def test_real_ownership_and_documents_without_mentions_are_exact() -> None:
    artifact = _artifact()
    assert len(artifact["ownership_records"]) == 1
    ownership = artifact["ownership_records"][0]
    assert ownership["statement_kind"] == "OWNERSHIP_CHANGE"
    assert ownership["effective_date_text"] == "2004"
    assert ownership["description_text"] == "100% Saudi-owned"
    assert ownership["owner_entity_id"] is None
    assert ownership["owner_span_text"] is None
    assert ownership["owner_link_status"] == "UNRESOLVED"
    assert [item["mention_id"] for item in ownership["evidence"]] == [
        "M-004",
        "M-012",
    ]
    assert artifact["documents_without_mentions"] == [
        "DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0",
        "DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a",
    ]


def test_real_passport_observation_and_corroboration_outcomes() -> None:
    artifact = _artifact()
    assert artifact["counts"]["passport_links_by_status"] == {
        "DETERMINISTIC_IDENTIFIER": 0,
        "EXACT_DOCUMENT_EVIDENCE": 10,
        "PROPOSED_PENDING_REVIEW": 0,
        "UNRESOLVED": 8,
    }
    unresolved = [
        item["unresolved_reason"]
        for item in artifact["passport_links"]
        if item["link_status"] == "UNRESOLVED"
    ]
    assert unresolved.count("NO_MENTION_RECORDED") == 2
    assert unresolved.count("OUT_OF_SCOPE_ENTITY_TYPE") == 6
    assert artifact["counts"]["observation_links_by_status"] == {
        "DETERMINISTIC_IDENTIFIER": 0,
        "EXACT_DOCUMENT_EVIDENCE": 5,
        "PROPOSED_PENDING_REVIEW": 0,
        "UNRESOLVED": 0,
    }
    unicoil_epd = next(
        item
        for item in artifact["passport_links"]
        if item["passport_ref"]["evidence_id"] == "S-UNICOIL-EPD"
    )
    assert unicoil_epd["corroboration"] == {
        "same_document_url_as": (
            "DOC-PRODUCER-UNICOIL-70151205e3a4-1762d53d6cab"
        )
    }


def test_every_real_span_and_resolved_link_reverifies_against_stored_input() -> None:
    mention_list = load_mention_list(MENTION_PATH)
    documents = default_document_loader(PROJECT_ROOT / "data")
    snapshots = default_snapshot_loader(PROJECT_ROOT / "data")
    verified = verify_mentions(
        mention_list,
        documents=documents,
        snapshots=snapshots,
    )
    assert len(verified) == 38
    verified_ids = {item.mention.mention_id for item in verified}
    artifact = _artifact()
    assert {
        item["mention_id"]
        for item in artifact["links"]
        if item["entity_id"] is not None
    } <= verified_ids
    forbidden = (
        "@",
        "contact name",
        "e-mail",
        "email",
        "phone",
        "mobile",
        "p.o.box",
        "p.o. box",
    )
    assert all(
        not any(token in item.mention.span_text.casefold() for token in forbidden)
        for item in verified
    )


def test_known_limitations_names_unmentioned_and_out_of_scope_documents() -> None:
    text = (PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md").read_text(
        encoding="utf-8"
    )
    required = {
        "DOC-PRODUCER-UNICOIL-7d21f605fc4e-6eb00a1886d0",
        "DOC-PRODUCER-UNICOIL-9cf950950e95-6217c780a89a",
        "DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9",
        "DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661",
        "DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54",
        "DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d",
        "DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b",
        "DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf",
    }
    assert not {value for value in required if value not in text}


def test_s14_mentions_v2_spans_verified_and_second_artifact_reconstructs() -> None:
    mention_path = (
        PROJECT_ROOT
        / "data"
        / "entities"
        / "mentions"
        / "mentions-v2.json"
    )
    mention_list = load_mention_list(mention_path)
    documents = default_document_loader(PROJECT_ROOT / "data")
    snapshots = default_snapshot_loader(PROJECT_ROOT / "data")
    verified = verify_mentions(
        mention_list,
        documents=documents,
        snapshots=snapshots,
    )
    assert len(verified) == 6
    assert {
        item.mention.address["document_id"] for item in verified
    } == {
        "DOC-PRODUCER-ALTAISEER-TALCO-b68e0eef2440-b339b1ac8d87",
        "DOC-PRODUCER-ALUPCO-135870d0e4c7-0261d54ca8a6",
        "DOC-PRODUCER-HADEED-92ca24b2076f-253eed8b773e",
        "DOC-PRODUCER-MAADEN-b1dd369ea0fe-dae44e050e70",
    }

    paths = sorted(
        (
            PROJECT_ROOT / "data" / "entities" / "resolution"
        ).glob("ENTITIES-*.json")
    )
    assert len(paths) == 2
    artifact = next(
        record
        for path in paths
        if (
            record := json.loads(path.read_text(encoding="utf-8"))
        )["inputs"]["mention_list"]["list_id"]
        == "mentions-v2"
    )
    validate_entity_artifact(artifact)
    assert artifact["quality_summary"] == "PASS"
    assert sum(artifact["counts"]["links_by_status"].values()) == 6
