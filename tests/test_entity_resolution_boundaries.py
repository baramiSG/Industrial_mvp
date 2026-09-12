from __future__ import annotations

import copy

from ior_mvp.acquisition.entities.mentions import Mention, VerifiedMention
from ior_mvp.acquisition.entities.resolver import resolve
from ior_mvp.acquisition.entities.rules import entity_resolution_rules

DOC_ID = "DOC-TEST-FIXTURE-aaaaaaaaaaaa-bbbbbbbbbbbb"


def _vm(
    mention_id: str,
    span: str,
    *,
    kind: str = "COMPANY_NAME",
    entity_type: str = "COMPANY",
    line: int = 1,
    subject: str | None = None,
    identifier: dict | None = None,
    statement: dict | None = None,
) -> VerifiedMention:
    return VerifiedMention(
        Mention(
            mention_id=mention_id,
            source_kind="DOCUMENT_RECORD",
            address={"document_id": DOC_ID, "page_index": 1, "line_index": line},
            span_text=span,
            mention_kind=kind,
            entity_type_observed=entity_type,
            language="en",
            text_order="logical",
            subject_mention_id=subject,
            alias=None,
            identifier=identifier,
            statement=statement,
            designation_text=None,
        ),
        "a" * 64,
        "2026-09-12",
    )


def _resolve(*mentions, seed_entities=()):
    return resolve(
        tuple(mentions),
        documents={},
        snapshots={},
        rules=entity_resolution_rules(),
        seed_entities=seed_entities,
    )


def test_same_name_different_plant_yields_two_plant_ids() -> None:
    result = _resolve(
        _vm("M-001", "Acme"),
        _vm(
            "M-002",
            "Al-Jubail",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=2,
            subject="M-001",
        ),
        _vm(
            "M-003",
            "Jeddah",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=3,
            subject="M-001",
        ),
    )
    plants = [item for item in result.entities if item["entity_type"] == "PLANT"]
    assert len(plants) == 2
    assert len({item["entity_id"] for item in plants}) == 2


def test_licence_holder_that_is_not_the_producer_stays_unlinked() -> None:
    different = _resolve(
        _vm("M-001", "Acme"),
        _vm(
            "M-002",
            "Other Holder",
            kind="LICENCE_HOLDER_NAME",
            entity_type="LICENCE_HOLDER",
        ),
    )
    assert len(different.entities) == 2
    same = _resolve(
        _vm("M-001", "Acme"),
        _vm(
            "M-002",
            "Acme",
            kind="LICENCE_HOLDER_NAME",
            entity_type="LICENCE_HOLDER",
        ),
    )
    holder = next(link for link in same.links if link["mention_id"] == "M-002")
    assert holder["rule_applied"] == "CROSS_TYPE_NAME_EQUALITY"
    assert holder["link_status"] == "PROPOSED_PENDING_REVIEW"


def test_merger_across_as_of_dates_keeps_ids_and_records_dated_merger() -> None:
    result = _resolve(
        _vm("M-001", "Survivor"),
        _vm("M-002", "Merged Company"),
        _vm(
            "M-003",
            "Merged Company merged in 2020",
            kind="OWNERSHIP_STATEMENT",
            subject="M-001",
            statement={
                "statement_kind": "MERGER",
                "effective_date_text": "2020",
                "owner_span_text": "Merged Company",
                "description_text": "Merged Company merged in 2020",
            },
        ),
    )
    assert len(result.merge_records) == 1
    assert result.merge_records[0]["effective_date_text"] == "2020"
    assert len(result.entities) == 2
    assert any(entity["merged_into"] for entity in result.entities)


def test_transliteration_variants_link_only_as_pending() -> None:
    result = _resolve(
        _vm("M-001", "Jubail Industrial City"),
        _vm("M-002", "Jubail"),
    )
    link = next(item for item in result.links if item["mention_id"] == "M-002")
    assert link["link_status"] == "PROPOSED_PENDING_REVIEW"


def test_deliberately_ambiguous_pair_held_pending() -> None:
    base = _resolve(_vm("M-001", "Acme"))
    left = base.entities[0]
    right = copy.deepcopy(left)
    right["entity_id"] = "COMPANY-ffffffffffffffff"
    right["canonical_key"] += "|other"
    result = _resolve(_vm("M-002", "Acme"), seed_entities=(left, right))
    link = result.links[0]
    assert link["link_status"] == "PROPOSED_PENDING_REVIEW"
    assert len(link["candidate_entity_ids"]) == 2
