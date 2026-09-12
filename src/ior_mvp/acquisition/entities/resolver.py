"""Pure deterministic entity resolution for verified mentions."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from .ids import (
    company_key,
    entity_id,
    licence_holder_key,
    line_key,
    plant_key,
)
from .mentions import VerifiedMention
from .normalisation import normalise_exact, normalise_name, normalise_variant
from .rules import EntityRules

_STATUSES = (
    "DETERMINISTIC_IDENTIFIER",
    "EXACT_DOCUMENT_EVIDENCE",
    "PROPOSED_PENDING_REVIEW",
    "UNRESOLVED",
)


@dataclass
class ResolutionResult:
    entities: list[dict[str, Any]]
    links: list[dict[str, Any]]
    passport_links: list[dict[str, Any]]
    observation_links: list[dict[str, Any]]
    ownership_records: list[dict[str, Any]]
    name_change_records: list[dict[str, Any]]
    merge_records: list[dict[str, Any]]
    documents_without_mentions: list[str]
    counts: dict[str, dict[str, int]]


def _payload(value: Any) -> dict[str, Any]:
    payload = value.record if hasattr(value, "record") else value
    return payload if isinstance(payload, dict) else {}


def _normalised_name(
    verified: VerifiedMention,
    *,
    span_text: str | None = None,
    role: str,
) -> dict[str, Any]:
    mention = verified.mention
    value = span_text if span_text is not None else mention.span_text
    normalised = normalise_name(
        value,
        language=mention.language,
        text_order=mention.text_order.upper(),
    )
    return {
        "name_text": value,
        "language": mention.language,
        "text_order": mention.text_order,
        "normalised_exact": normalised.exact,
        "normalised_variant": normalised.variant,
        "role": role,
        "established_by_mention_ids": [mention.mention_id],
    }


def _new_entity(
    verified: VerifiedMention,
    *,
    entity_type: str,
    name_text: str,
    canonical_key: str,
    granularity: str,
    parent: dict[str, str | None] | None = None,
    locality_token: str | None = None,
) -> dict[str, Any]:
    mention = verified.mention
    name = _normalised_name(verified, span_text=name_text, role="PRIMARY")
    return {
        "entity_id": entity_id(entity_type, canonical_key),
        "entity_type": entity_type,
        "canonical_key": canonical_key,
        "primary_name_en": name_text if mention.language == "en" else "UNAVAILABLE",
        "primary_name_ar": name_text if mention.language == "ar" else "UNAVAILABLE",
        "jurisdiction": "UNAVAILABLE",
        "granularity": granularity,
        "parent": parent
        or {"company_entity_id": None, "plant_entity_id": None},
        "locality_token": locality_token,
        "names": [name],
        "identifiers": [],
        "attributes_unresolved": [],
        "merged_into": None,
        "first_observed_as_of": verified.as_of_date,
        "evidence_mention_ids": [mention.mention_id],
    }


def _link_evidence(verified: VerifiedMention) -> dict[str, Any]:
    mention = verified.mention
    return {
        "source_kind": mention.source_kind,
        "address": copy.deepcopy(mention.address),
        "span_text": mention.span_text,
        "language": mention.language,
        "text_order": mention.text_order,
        "input_sha256": verified.input_sha256,
        "as_of_date": verified.as_of_date,
    }


def _link(
    verified: VerifiedMention,
    *,
    status: str,
    rank: int,
    rule: str,
    entity_id_value: str | None = None,
    candidates: Sequence[str] = (),
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "link_id": "",
        "mention_id": verified.mention.mention_id,
        "entity_type": verified.mention.entity_type_observed,
        "link_status": status,
        "precedence_rank": rank,
        "rule_applied": rule,
        "entity_id": entity_id_value,
        "candidate_entity_ids": sorted(set(candidates)),
        "unresolved_reason": reason,
        "evidence": _link_evidence(verified),
    }


def _candidate_entities(
    entities: list[dict[str, Any]],
    verified: VerifiedMention,
    *,
    exact: bool,
    entity_type: str | None = None,
) -> list[dict[str, Any]]:
    mention = verified.mention
    form = (
        normalise_exact(mention.span_text)
        if exact
        else normalise_variant(mention.span_text)
    )
    candidates = []
    for entity in entities:
        if entity_type is not None and entity["entity_type"] != entity_type:
            continue
        for name in entity["names"]:
            if name["text_order"] != mention.text_order:
                continue
            key = "normalised_exact" if exact else "normalised_variant"
            if name[key] == form:
                candidates.append(entity)
                break
    return sorted(candidates, key=lambda item: item["entity_id"])


def _entity_by_id(entities: list[dict[str, Any]], value: str | None) -> dict[str, Any] | None:
    return next((item for item in entities if item["entity_id"] == value), None)


def _mint_name_entity(
    entities: list[dict[str, Any]], verified: VerifiedMention
) -> dict[str, Any]:
    mention = verified.mention
    exact = normalise_exact(mention.span_text)
    if mention.entity_type_observed == "COMPANY":
        key = company_key(exact)
        granularity = "LEGAL_ENTITY"
    else:
        key = licence_holder_key(exact)
        granularity = "LEGAL_ENTITY"
    entity = _new_entity(
        verified,
        entity_type=mention.entity_type_observed,
        name_text=mention.span_text,
        canonical_key=key,
        granularity=granularity,
    )
    entities.append(entity)
    return entity


def _resolve_name(
    entities: list[dict[str, Any]], verified: VerifiedMention
) -> dict[str, Any]:
    mention = verified.mention
    if mention.entity_type_observed == "STANDARDS_AUTHORITY":
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="OUT_OF_SCOPE_ENTITY_TYPE",
            reason="OUT_OF_SCOPE_ENTITY_TYPE",
        )
    same_exact = _candidate_entities(
        entities, verified, exact=True, entity_type=mention.entity_type_observed
    )
    if len(same_exact) > 1:
        return _link(
            verified,
            status="PROPOSED_PENDING_REVIEW",
            rank=3,
            rule="MULTIPLE_CANDIDATES",
            candidates=[item["entity_id"] for item in same_exact],
        )
    if len(same_exact) == 1:
        entity = same_exact[0]
        role = next(
            name["role"]
            for name in entity["names"]
            if name["text_order"] == mention.text_order
            and name["normalised_exact"] == normalise_exact(mention.span_text)
        )
        if mention.mention_id not in entity["evidence_mention_ids"]:
            entity["evidence_mention_ids"].append(mention.mention_id)
        return _link(
            verified,
            status="EXACT_DOCUMENT_EVIDENCE",
            rank=2,
            rule="EXACT_ALIAS_EQUALITY" if role == "ALIAS" else "EXACT_NAME_EQUALITY",
            entity_id_value=entity["entity_id"],
        )
    cross_type = _candidate_entities(entities, verified, exact=True)
    if cross_type:
        return _link(
            verified,
            status="PROPOSED_PENDING_REVIEW",
            rank=3,
            rule="CROSS_TYPE_NAME_EQUALITY",
            candidates=[item["entity_id"] for item in cross_type],
        )
    same_variant = _candidate_entities(
        entities, verified, exact=False, entity_type=mention.entity_type_observed
    )
    if same_variant:
        return _link(
            verified,
            status="PROPOSED_PENDING_REVIEW",
            rank=3,
            rule="VARIANT_NAME_EQUALITY",
            candidates=[item["entity_id"] for item in same_variant],
        )
    entity = _mint_name_entity(entities, verified)
    return _link(
        verified,
        status="EXACT_DOCUMENT_EVIDENCE",
        rank=2,
        rule="MINTED_FROM_MENTION",
        entity_id_value=entity["entity_id"],
    )


def _resolve_alias(
    entities: list[dict[str, Any]], verified: VerifiedMention
) -> dict[str, Any]:
    mention = verified.mention
    assert mention.alias is not None
    primary_text = mention.alias["primary_span_text"]
    synthetic_primary = replace(
        verified, mention=replace(mention, span_text=primary_text)
    )
    link = _resolve_name(entities, synthetic_primary)
    if link["entity_id"] is None:
        link["evidence"] = _link_evidence(verified)
        return link
    entity = _entity_by_id(entities, link["entity_id"])
    assert entity is not None
    alias_name = _normalised_name(
        verified, span_text=mention.alias["alias_span_text"], role="ALIAS"
    )
    if not any(
        name["normalised_exact"] == alias_name["normalised_exact"]
        and name["text_order"] == alias_name["text_order"]
        for name in entity["names"]
    ):
        entity["names"].append(alias_name)
    link.update(
        {
            "mention_id": mention.mention_id,
            "rule_applied": "ALIAS_STATEMENT",
            "evidence": _link_evidence(verified),
        }
    )
    if mention.mention_id not in entity["evidence_mention_ids"]:
        entity["evidence_mention_ids"].append(mention.mention_id)
    return link


def _resolved_subject(
    links_by_mention: Mapping[str, dict[str, Any]], subject_id: str | None
) -> dict[str, Any] | None:
    link = links_by_mention.get(subject_id or "")
    if (
        link is None
        or link["precedence_rank"] > 2
        or link["link_status"] not in {"DETERMINISTIC_IDENTIFIER", "EXACT_DOCUMENT_EVIDENCE"}
    ):
        return None
    return link


def _resolve_plant(
    entities: list[dict[str, Any]],
    links_by_mention: Mapping[str, dict[str, Any]],
    verified_by_id: Mapping[str, VerifiedMention],
    verified: VerifiedMention,
    rules: EntityRules,
) -> dict[str, Any]:
    mention = verified.mention
    subject_link = _resolved_subject(links_by_mention, mention.subject_mention_id)
    if subject_link is None:
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="NO_SUBJECT_ENTITY",
            reason="NO_SUBJECT_ENTITY",
        )
    company = _entity_by_id(entities, subject_link["entity_id"])
    if company is None or company["entity_type"] != "COMPANY":
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="NO_SUBJECT_ENTITY",
            reason="NO_SUBJECT_ENTITY",
        )
    subject = verified_by_id[mention.subject_mention_id or ""].mention
    same_page = subject.address.get("page_index") == mention.address.get("page_index")
    within = (
        same_page
        and abs(subject.address.get("line_index", 0) - mention.address.get("line_index", 0))
        <= rules.plant_subject_window_lines
    )
    existing_plants = [
        item
        for item in entities
        if item["entity_type"] == "PLANT"
        and item["parent"]["company_entity_id"] == company["entity_id"]
    ]
    if not within:
        return _link(
            verified,
            status="PROPOSED_PENDING_REVIEW",
            rank=3,
            rule="SUBJECT_OUTSIDE_WINDOW",
            candidates=[item["entity_id"] for item in existing_plants],
        )
    span_exact = normalise_exact(mention.span_text)
    for token, locality in rules.localities.items():
        canonical_exact = normalise_exact(locality["canonical_en"])
        if span_exact == canonical_exact:
            key = plant_key(company["entity_id"], token)
            plant_id = entity_id("PLANT", key)
            plant = _entity_by_id(entities, plant_id)
            if plant is None:
                plant = _new_entity(
                    verified,
                    entity_type="PLANT",
                    name_text=mention.span_text,
                    canonical_key=key,
                    granularity="SITE_LOCALITY",
                    parent={
                        "company_entity_id": company["entity_id"],
                        "plant_entity_id": None,
                    },
                    locality_token=token,
                )
                entities.append(plant)
            elif mention.mention_id not in plant["evidence_mention_ids"]:
                plant["evidence_mention_ids"].append(mention.mention_id)
            return _link(
                verified,
                status="EXACT_DOCUMENT_EVIDENCE",
                rank=2,
                rule="EXACT_LOCALITY_WITHIN_WINDOW",
                entity_id_value=plant_id,
            )
    span_variant = normalise_variant(mention.span_text)
    for token, locality in rules.localities.items():
        variants = [locality["canonical_en"], *locality["variants_en"], *locality["variants_ar"]]
        if any(span_variant == normalise_variant(value) for value in variants):
            key = plant_key(company["entity_id"], token)
            plant_id = entity_id("PLANT", key)
            return _link(
                verified,
                status="PROPOSED_PENDING_REVIEW",
                rank=3,
                rule="LOCALITY_VARIANT",
                candidates=[plant_id] if _entity_by_id(entities, plant_id) else [],
            )
    return _link(
        verified,
        status="UNRESOLVED",
        rank=4,
        rule="LOCALITY_NOT_IN_TABLE",
        reason="LOCALITY_NOT_IN_TABLE",
    )


def _resolve_line(
    entities: list[dict[str, Any]],
    links_by_mention: Mapping[str, dict[str, Any]],
    verified: VerifiedMention,
) -> dict[str, Any]:
    mention = verified.mention
    if mention.designation_text is None:
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="COUNT_ONLY_NO_IDENTITY",
            reason="COUNT_ONLY_NO_IDENTITY",
        )
    subject = _resolved_subject(links_by_mention, mention.subject_mention_id)
    subject_entity = _entity_by_id(entities, subject["entity_id"]) if subject else None
    plants: list[dict[str, Any]] = []
    if subject_entity is not None and subject_entity["entity_type"] == "PLANT":
        plants = [subject_entity]
    elif subject_entity is not None and subject_entity["entity_type"] == "COMPANY":
        plants = [
            item
            for item in entities
            if item["entity_type"] == "PLANT"
            and item["parent"]["company_entity_id"] == subject_entity["entity_id"]
        ]
    if len(plants) != 1:
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="NO_SUBJECT_ENTITY",
            reason="NO_SUBJECT_ENTITY",
        )
    plant = plants[0]
    designation_exact = normalise_exact(mention.designation_text)
    key = line_key(plant["entity_id"], designation_exact)
    line_id = entity_id("LINE", key)
    if _entity_by_id(entities, line_id) is None:
        entities.append(
            _new_entity(
                verified,
                entity_type="LINE",
                name_text=mention.designation_text,
                canonical_key=key,
                granularity="LINE_DESIGNATION",
                parent={
                    "company_entity_id": None,
                    "plant_entity_id": plant["entity_id"],
                },
            )
        )
    return _link(
        verified,
        status="EXACT_DOCUMENT_EVIDENCE",
        rank=2,
        rule="LINE_DESIGNATION_UNDER_PLANT",
        entity_id_value=line_id,
    )


def _resolve_identifier(
    entities: list[dict[str, Any]],
    links_by_mention: Mapping[str, dict[str, Any]],
    verified: VerifiedMention,
) -> dict[str, Any]:
    mention = verified.mention
    assert mention.identifier is not None
    kind = mention.identifier["kind"]
    value_exact = normalise_exact(mention.identifier["value_text"])
    matches = []
    for entity in entities:
        if entity["entity_type"] != mention.entity_type_observed:
            continue
        if any(
            item["kind"] == kind
            and normalise_exact(item["value_text"]) == value_exact
            for item in entity["identifiers"]
        ):
            matches.append(entity)
    if len(matches) == 1:
        entity = matches[0]
        identifier = next(
            item
            for item in entity["identifiers"]
            if item["kind"] == kind
            and normalise_exact(item["value_text"]) == value_exact
        )
        if mention.mention_id not in identifier["mention_ids"]:
            identifier["mention_ids"].append(mention.mention_id)
        return _link(
            verified,
            status="DETERMINISTIC_IDENTIFIER",
            rank=1,
            rule="IDENTIFIER_EQUALITY",
            entity_id_value=entity["entity_id"],
        )
    subject = _resolved_subject(links_by_mention, mention.subject_mention_id)
    entity = _entity_by_id(entities, subject["entity_id"]) if subject else None
    if entity is None or entity["entity_type"] != mention.entity_type_observed:
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="NO_SUBJECT_ENTITY",
            reason="NO_SUBJECT_ENTITY",
        )
    entity["identifiers"].append(
        {
            "kind": kind,
            "value_text": mention.identifier["value_text"],
            "mention_ids": [mention.mention_id],
        }
    )
    return _link(
        verified,
        status="EXACT_DOCUMENT_EVIDENCE",
        rank=2,
        rule="SUBJECT_STATEMENT",
        entity_id_value=entity["entity_id"],
    )


def _statement_record_id(*parts: str) -> str:
    return "R-" + hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _resolve_statement(
    entities: list[dict[str, Any]],
    links_by_mention: Mapping[str, dict[str, Any]],
    verified: VerifiedMention,
    ownership_records: list[dict[str, Any]],
    name_change_records: list[dict[str, Any]],
    merge_records: list[dict[str, Any]],
) -> dict[str, Any]:
    mention = verified.mention
    assert mention.statement is not None
    subject = _resolved_subject(links_by_mention, mention.subject_mention_id)
    entity = _entity_by_id(entities, subject["entity_id"]) if subject else None
    if entity is None:
        return _link(
            verified,
            status="UNRESOLVED",
            rank=4,
            rule="NO_SUBJECT_ENTITY",
            reason="NO_SUBJECT_ENTITY",
        )
    statement = mention.statement
    owner_span = statement["owner_span_text"]
    owner_candidates: list[dict[str, Any]] = []
    if owner_span:
        owner_exact = normalise_exact(owner_span)
        owner_candidates = [
            item
            for item in entities
            if item["entity_type"] == "COMPANY"
            and any(name["normalised_exact"] == owner_exact for name in item["names"])
        ]
    owner_entity_id = (
        owner_candidates[0]["entity_id"] if len(owner_candidates) == 1 else None
    )
    owner_status = (
        "EXACT_DOCUMENT_EVIDENCE"
        if owner_entity_id
        else (
            "PROPOSED_PENDING_REVIEW"
            if owner_span and owner_candidates
            else "UNRESOLVED"
        )
    )
    description_exact = normalise_exact(statement["description_text"])
    key = (
        entity["entity_id"],
        statement["statement_kind"],
        statement["effective_date_text"],
        description_exact,
    )
    evidence = {
        "mention_id": mention.mention_id,
        "address": copy.deepcopy(mention.address),
        "span_text": mention.span_text,
        "as_of_date": verified.as_of_date,
    }
    existing = next(
        (
            item
            for item in ownership_records
            if item["_dedupe_key"] == key
        ),
        None,
    )
    if existing is None:
        existing = {
            "record_id": _statement_record_id(*key),
            "entity_id": entity["entity_id"],
            "statement_kind": statement["statement_kind"],
            "effective_date_text": statement["effective_date_text"],
            "owner_entity_id": owner_entity_id,
            "owner_span_text": owner_span,
            "description_text": statement["description_text"],
            "owner_link_status": owner_status,
            "evidence": [],
            "_dedupe_key": key,
        }
        ownership_records.append(existing)
    existing["evidence"].append(evidence)
    if statement["statement_kind"] == "MERGER" and owner_entity_id:
        merged = _entity_by_id(entities, owner_entity_id)
        if merged is not None:
            merged["merged_into"] = entity["entity_id"]
        if not any(
            item["surviving_entity_id"] == entity["entity_id"]
            and item["merged_entity_id"] == owner_entity_id
            and item["effective_date_text"] == statement["effective_date_text"]
            for item in merge_records
        ):
            merge_records.append(
                {
                    "surviving_entity_id": entity["entity_id"],
                    "merged_entity_id": owner_entity_id,
                    "effective_date_text": statement["effective_date_text"],
                    "evidence": [evidence],
                }
            )
    if statement["statement_kind"] == "NAME_CHANGE":
        name_change_records.append(
            {
                "entity_id": entity["entity_id"],
                "from_name_text": entity["primary_name_en"],
                "to_name_text": owner_span or statement["description_text"],
                "effective_date_text": statement["effective_date_text"],
                "evidence": [evidence],
            }
        )
    return _link(
        verified,
        status="EXACT_DOCUMENT_EVIDENCE",
        rank=2,
        rule="SUBJECT_STATEMENT",
        entity_id_value=entity["entity_id"],
    )


def _passport_result(
    *,
    ref: dict[str, Any],
    mention_links: list[dict[str, Any]],
    no_mentions_reason: str,
    corroboration: dict[str, str] | None = None,
) -> dict[str, Any]:
    resolved_ids = sorted(
        {
            link["entity_id"]
            for link in mention_links
            if link["entity_id"] is not None
            and link["link_status"] in {
                "DETERMINISTIC_IDENTIFIER",
                "EXACT_DOCUMENT_EVIDENCE",
            }
        }
    )
    out_of_scope = any(
        link["unresolved_reason"] == "OUT_OF_SCOPE_ENTITY_TYPE"
        for link in mention_links
    )
    if len(resolved_ids) == 1:
        status = "EXACT_DOCUMENT_EVIDENCE"
        entity_id_value = resolved_ids[0]
        reason = None
        candidates: list[str] = []
    elif len(resolved_ids) > 1:
        status = "PROPOSED_PENDING_REVIEW"
        entity_id_value = None
        reason = None
        candidates = resolved_ids
    else:
        status = "UNRESOLVED"
        entity_id_value = None
        reason = "OUT_OF_SCOPE_ENTITY_TYPE" if out_of_scope else no_mentions_reason
        candidates = []
    return {
        "passport_ref": ref,
        "entity_id": entity_id_value,
        "link_status": status,
        "unresolved_reason": reason,
        "via_mention_ids": sorted(link["mention_id"] for link in mention_links),
        "candidate_entity_ids": candidates,
        "corroboration": corroboration,
    }


def _build_input_links(
    verified: Sequence[VerifiedMention],
    links: list[dict[str, Any]],
    documents: Mapping[str, Any],
    snapshots: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    links_by_id = {item["mention_id"]: item for item in links}
    document_mentions: dict[str, list[VerifiedMention]] = {}
    for item in verified:
        if item.mention.source_kind == "DOCUMENT_RECORD":
            document_mentions.setdefault(item.mention.address["document_id"], []).append(item)
    documents_without_mentions = sorted(
        document_id for document_id in documents if document_id not in document_mentions
    )
    passport_links: list[dict[str, Any]] = []
    for document_id in sorted(documents):
        record = _payload(documents[document_id])
        passport_id = None
        if record.get("evidence"):
            passport_id = record["evidence"][0].get("passport_id")
        publisher_mentions = [
            item
            for item in document_mentions.get(document_id, [])
            if item.mention.mention_kind == "PUBLISHER_NAME"
        ]
        passport_links.append(
            _passport_result(
                ref={
                    "kind": "DOCUMENT_RECORD_PASSPORT",
                    "passport_id": passport_id,
                    "evidence_id": None,
                    "document_id": document_id,
                    "snapshot_id": None,
                    "json_pointer": None,
                },
                mention_links=[links_by_id[item.mention.mention_id] for item in publisher_mentions],
                no_mentions_reason="NO_MENTION_RECORDED",
            )
        )
    observation_links: list[dict[str, Any]] = []
    document_urls = {
        _payload(value).get("raw_artifact_ref", {}).get("endpoint_or_document"): document_id
        for document_id, value in documents.items()
    }
    for snapshot_id in sorted(snapshots):
        record = _payload(snapshots[snapshot_id])
        for index, evidence in enumerate(record.get("evidence", [])):
            pointer = f"/evidence/{index}/source"
            matching = [
                item
                for item in verified
                if item.mention.source_kind == "PUBLIC_SNAPSHOT"
                and item.mention.address.get("snapshot_id") == snapshot_id
                and item.mention.address.get("json_pointer") == pointer
                and item.mention.mention_kind == "PUBLISHER_NAME"
            ]
            if not matching:
                continue
            url = evidence.get("url")
            corroborated = document_urls.get(url) if isinstance(url, str) else None
            passport_links.append(
                _passport_result(
                    ref={
                        "kind": "PUBLIC_SNAPSHOT_PASSPORT",
                        "passport_id": None,
                        "evidence_id": evidence.get("evidence_id"),
                        "document_id": None,
                        "snapshot_id": snapshot_id,
                        "json_pointer": pointer,
                    },
                    mention_links=[links_by_id[item.mention.mention_id] for item in matching],
                    no_mentions_reason="NO_MENTION_RECORDED",
                    corroboration=(
                        {"same_document_url_as": corroborated}
                        if corroborated is not None
                        else None
                    ),
                )
            )
        producers = record.get("domestic_capability", {}).get("producer_evidence", [])
        for index, _producer in enumerate(producers):
            pointer = f"/domestic_capability/producer_evidence/{index}/producer"
            matching = [
                item
                for item in verified
                if item.mention.source_kind == "PUBLIC_SNAPSHOT"
                and item.mention.address.get("snapshot_id") == snapshot_id
                and item.mention.address.get("json_pointer") == pointer
            ]
            passport_result = _passport_result(
                ref={
                    "kind": "PUBLIC_SNAPSHOT_PASSPORT",
                    "passport_id": None,
                    "evidence_id": None,
                    "document_id": None,
                    "snapshot_id": snapshot_id,
                    "json_pointer": pointer,
                },
                mention_links=[links_by_id[item.mention.mention_id] for item in matching],
                no_mentions_reason="NO_MENTION_RECORDED",
            )
            observation_links.append(
                {
                    "observation_ref": {
                        "snapshot_id": snapshot_id,
                        "json_pointer": pointer,
                    },
                    "entity_id": passport_result["entity_id"],
                    "link_status": passport_result["link_status"],
                    "unresolved_reason": passport_result["unresolved_reason"],
                    "via_mention_ids": passport_result["via_mention_ids"],
                    "candidate_entity_ids": passport_result["candidate_entity_ids"],
                }
            )
    return passport_links, observation_links, documents_without_mentions


def _status_counts(items: Sequence[dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(item["link_status"] == status for item in items)
        for status in _STATUSES
    }


def resolve(
    verified: Sequence[VerifiedMention],
    *,
    documents: Mapping[str, Any],
    snapshots: Mapping[str, Any],
    rules: EntityRules,
    seed_entities: Sequence[dict[str, Any]] = (),
) -> ResolutionResult:
    """Resolve verified mentions by the frozen first-match precedence."""
    ordered = sorted(verified, key=lambda item: item.mention.mention_id)
    verified_by_id = {item.mention.mention_id: item for item in ordered}
    entities = copy.deepcopy(list(seed_entities))
    links: list[dict[str, Any]] = []
    links_by_mention: dict[str, dict[str, Any]] = {}
    ownership_records: list[dict[str, Any]] = []
    name_change_records: list[dict[str, Any]] = []
    merge_records: list[dict[str, Any]] = []
    for item in ordered:
        kind = item.mention.mention_kind
        if kind == "ALIAS_STATEMENT":
            link = _resolve_alias(entities, item)
        elif kind in {"COMPANY_NAME", "PUBLISHER_NAME", "LICENCE_HOLDER_NAME"}:
            link = _resolve_name(entities, item)
        elif kind == "PLANT_LOCATION":
            link = _resolve_plant(
                entities, links_by_mention, verified_by_id, item, rules
            )
        elif kind == "LINE_STATEMENT":
            link = _resolve_line(entities, links_by_mention, item)
        elif kind == "IDENTIFIER":
            link = _resolve_identifier(entities, links_by_mention, item)
        elif kind == "OWNERSHIP_STATEMENT":
            link = _resolve_statement(
                entities,
                links_by_mention,
                item,
                ownership_records,
                name_change_records,
                merge_records,
            )
        else:  # pragma: no cover - mention validation prevents this
            raise AssertionError(kind)
        link["link_id"] = f"L-{len(links) + 1:03d}"
        links.append(link)
        links_by_mention[item.mention.mention_id] = link
    for entity in entities:
        entity["names"].sort(
            key=lambda name: (
                name["role"] != "PRIMARY",
                name["language"],
                name["text_order"],
                name["normalised_exact"],
            )
        )
        entity["identifiers"].sort(key=lambda value: (value["kind"], value["value_text"]))
        entity["evidence_mention_ids"] = sorted(set(entity["evidence_mention_ids"]))
    entities.sort(key=lambda item: item["entity_id"])
    for record in ownership_records:
        record.pop("_dedupe_key", None)
        record["evidence"].sort(key=lambda item: item["mention_id"])
    ownership_records.sort(key=lambda item: item["record_id"])
    passport_links, observation_links, documents_without_mentions = _build_input_links(
        ordered, links, documents, snapshots
    )
    entity_counts = {
        entity_type: sum(item["entity_type"] == entity_type for item in entities)
        for entity_type in ("COMPANY", "PLANT", "LINE", "LICENCE_HOLDER")
    }
    return ResolutionResult(
        entities=entities,
        links=links,
        passport_links=passport_links,
        observation_links=observation_links,
        ownership_records=ownership_records,
        name_change_records=sorted(
            name_change_records,
            key=lambda item: (item["entity_id"], item["effective_date_text"]),
        ),
        merge_records=sorted(
            merge_records,
            key=lambda item: (
                item["surviving_entity_id"],
                item["merged_entity_id"],
                item["effective_date_text"],
            ),
        ),
        documents_without_mentions=documents_without_mentions,
        counts={
            "entities_by_type": entity_counts,
            "links_by_status": _status_counts(links),
            "passport_links_by_status": _status_counts(passport_links),
            "observation_links_by_status": _status_counts(observation_links),
        },
    )
