"""Operator-recorded EntityMentionList 1.0.0 validation and verification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from ..contracts import canonical_dumps
from .rules import EntityResolutionError, EntityRules, entity_resolution_rules

MENTION_LIST_SCHEMA_VERSION = "1.0.0"
MENTION_ID_PATTERN = re.compile(r"^M-[0-9]{3}$")
LIST_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,79}$")

SOURCE_KINDS = frozenset({"DOCUMENT_RECORD", "PUBLIC_SNAPSHOT"})
MENTION_KINDS = frozenset(
    {
        "COMPANY_NAME",
        "PUBLISHER_NAME",
        "ALIAS_STATEMENT",
        "PLANT_LOCATION",
        "LINE_STATEMENT",
        "LICENCE_HOLDER_NAME",
        "IDENTIFIER",
        "OWNERSHIP_STATEMENT",
    }
)
ENTITY_TYPES_OBSERVED = frozenset(
    {"COMPANY", "PLANT", "LINE", "LICENCE_HOLDER", "STANDARDS_AUTHORITY"}
)
LANGUAGES = frozenset({"ar", "en"})
TEXT_ORDERS = frozenset({"logical", "visual"})
STATEMENT_KINDS = frozenset({"OWNERSHIP_CHANGE", "MERGER", "NAME_CHANGE"})

_TOP_KEYS = {
    "schema_version",
    "list_id",
    "recorded_on",
    "recorded_by_seat",
    "consultation_summary_text",
    "mentions",
}
_MENTION_KEYS = {
    "mention_id",
    "source_kind",
    "address",
    "span_text",
    "mention_kind",
    "entity_type_observed",
    "language",
    "text_order",
    "subject_mention_id",
    "alias",
    "identifier",
    "statement",
    "designation_text",
}
_DOCUMENT_ADDRESS_KEYS = {"document_id", "page_index", "line_index"}
_SNAPSHOT_ADDRESS_KEYS = {"snapshot_id", "json_pointer"}
_ALIAS_KEYS = {"primary_span_text", "alias_span_text"}
_IDENTIFIER_KEYS = {"kind", "value_text"}
_STATEMENT_KEYS = {
    "statement_kind",
    "effective_date_text",
    "owner_span_text",
    "description_text",
}
_SUBJECT_KINDS = {
    "COMPANY_NAME",
    "PUBLISHER_NAME",
    "LICENCE_HOLDER_NAME",
    "ALIAS_STATEMENT",
}
_SUBJECT_REQUIRED_KINDS = {
    "PLANT_LOCATION",
    "LINE_STATEMENT",
    "IDENTIFIER",
    "OWNERSHIP_STATEMENT",
}


@dataclass(frozen=True)
class Mention:
    mention_id: str
    source_kind: str
    address: dict[str, Any]
    span_text: str
    mention_kind: str
    entity_type_observed: str
    language: str
    text_order: str
    subject_mention_id: str | None
    alias: dict[str, str] | None
    identifier: dict[str, str] | None
    statement: dict[str, Any] | None
    designation_text: str | None


@dataclass(frozen=True)
class MentionList:
    schema_version: str
    list_id: str
    recorded_on: str
    recorded_by_seat: str
    consultation_summary_text: str
    mentions: tuple[Mention, ...]


@dataclass(frozen=True)
class VerifiedMention:
    mention: Mention
    input_sha256: str
    as_of_date: str


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EntityResolutionError(f"{field} must be an object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        raise EntityResolutionError(
            f"{field} has unknown keys {sorted(actual - expected)} "
            f"or missing keys {sorted(expected - actual)}"
        )


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise EntityResolutionError(f"{field} must be a non-empty string")
    return value


def _iso_date(value: Any, field: str) -> str:
    text = _nonempty(value, field)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise EntityResolutionError(f"{field} must be an ISO date") from exc
    return text


def _validate_address(mention: dict[str, Any], index: int) -> None:
    source_kind = mention["source_kind"]
    address = _mapping(mention["address"], f"mentions[{index}].address")
    if source_kind == "DOCUMENT_RECORD":
        _exact_keys(address, _DOCUMENT_ADDRESS_KEYS, f"mentions[{index}].address")
        _nonempty(address["document_id"], f"mentions[{index}].address.document_id")
        for key in ("page_index", "line_index"):
            if type(address[key]) is not int or address[key] < 1:
                raise EntityResolutionError(
                    f"mentions[{index}].address.{key} must be >= 1"
                )
    else:
        _exact_keys(address, _SNAPSHOT_ADDRESS_KEYS, f"mentions[{index}].address")
        _nonempty(address["snapshot_id"], f"mentions[{index}].address.snapshot_id")
        pointer = _nonempty(
            address["json_pointer"], f"mentions[{index}].address.json_pointer"
        )
        if not pointer.startswith("/"):
            raise EntityResolutionError("json_pointer must be an RFC 6901 pointer")


def _validate_kind_fields(mention: dict[str, Any], index: int, rules: EntityRules) -> None:
    kind = mention["mention_kind"]
    alias = mention["alias"]
    identifier = mention["identifier"]
    statement = mention["statement"]
    designation = mention["designation_text"]

    if kind == "ALIAS_STATEMENT":
        alias_value = _mapping(alias, f"mentions[{index}].alias")
        _exact_keys(alias_value, _ALIAS_KEYS, f"mentions[{index}].alias")
        for key in _ALIAS_KEYS:
            _nonempty(alias_value[key], f"mentions[{index}].alias.{key}")
    elif alias is not None:
        raise EntityResolutionError("alias is permitted only for ALIAS_STATEMENT")

    if kind == "IDENTIFIER":
        identifier_value = _mapping(identifier, f"mentions[{index}].identifier")
        _exact_keys(identifier_value, _IDENTIFIER_KEYS, f"mentions[{index}].identifier")
        if identifier_value["kind"] not in rules.identifier_kinds:
            raise EntityResolutionError("identifier.kind is not governed")
        _nonempty(identifier_value["value_text"], "identifier.value_text")
    elif identifier is not None:
        raise EntityResolutionError("identifier is permitted only for IDENTIFIER")

    if kind == "OWNERSHIP_STATEMENT":
        statement_value = _mapping(statement, f"mentions[{index}].statement")
        _exact_keys(statement_value, _STATEMENT_KEYS, f"mentions[{index}].statement")
        if statement_value["statement_kind"] not in STATEMENT_KINDS:
            raise EntityResolutionError("statement.statement_kind is not governed")
        _nonempty(statement_value["effective_date_text"], "statement.effective_date_text")
        _nonempty(statement_value["description_text"], "statement.description_text")
        owner = statement_value["owner_span_text"]
        if owner is not None:
            _nonempty(owner, "statement.owner_span_text")
    elif statement is not None:
        raise EntityResolutionError(
            "statement is permitted only for OWNERSHIP_STATEMENT"
        )

    if kind == "LINE_STATEMENT":
        if designation is not None:
            _nonempty(designation, f"mentions[{index}].designation_text")
    elif designation is not None:
        raise EntityResolutionError(
            "designation_text is permitted only for LINE_STATEMENT"
        )


def _validate_subjects(mentions: list[dict[str, Any]]) -> None:
    prior: dict[str, dict[str, Any]] = {}
    for index, mention in enumerate(mentions):
        mention_id = mention["mention_id"]
        subject_id = mention["subject_mention_id"]
        kind = mention["mention_kind"]
        if kind in _SUBJECT_REQUIRED_KINDS:
            if not isinstance(subject_id, str) or subject_id not in prior:
                raise EntityResolutionError(
                    f"{mention_id} subject must be an earlier mention"
                )
            subject = prior[subject_id]
            if subject["mention_kind"] not in _SUBJECT_KINDS:
                raise EntityResolutionError(
                    f"{mention_id} subject must be an earlier name mention"
                )
            if (
                mention["source_kind"] != "DOCUMENT_RECORD"
                or subject["source_kind"] != "DOCUMENT_RECORD"
                or mention["address"]["document_id"]
                != subject["address"]["document_id"]
            ):
                raise EntityResolutionError(
                    f"{mention_id} subject must be in the same document"
                )
        elif subject_id is not None:
            raise EntityResolutionError(
                f"{mention_id} subject_mention_id is not permitted for {kind}"
            )
        prior[mention_id] = mention


def validate_mention_list(
    payload: dict[str, Any], *, rules: EntityRules | None = None
) -> None:
    """Validate exact EntityMentionList shape and intra-list references."""
    configured = rules or entity_resolution_rules()
    root = _mapping(payload, "mention list")
    _exact_keys(root, _TOP_KEYS, "mention list")
    if root["schema_version"] != MENTION_LIST_SCHEMA_VERSION:
        raise EntityResolutionError("schema_version must be 1.0.0")
    list_id = _nonempty(root["list_id"], "list_id")
    if LIST_ID_PATTERN.fullmatch(list_id) is None:
        raise EntityResolutionError("list_id is unsafe or invalid")
    _iso_date(root["recorded_on"], "recorded_on")
    _nonempty(root["recorded_by_seat"], "recorded_by_seat")
    _nonempty(root["consultation_summary_text"], "consultation_summary_text")
    mentions = root["mentions"]
    if not isinstance(mentions, list) or not mentions:
        raise EntityResolutionError("mentions must be a non-empty list")
    ids: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(mentions):
        mention = _mapping(raw, f"mentions[{index}]")
        _exact_keys(mention, _MENTION_KEYS, f"mentions[{index}]")
        mention_id = _nonempty(mention["mention_id"], f"mentions[{index}].mention_id")
        if MENTION_ID_PATTERN.fullmatch(mention_id) is None:
            raise EntityResolutionError("mention_id must match M-[0-9]{3}")
        if mention_id in ids:
            raise EntityResolutionError("mention_id values must be unique")
        ids.add(mention_id)
        for field, allowed in (
            ("source_kind", SOURCE_KINDS),
            ("mention_kind", MENTION_KINDS),
            ("entity_type_observed", ENTITY_TYPES_OBSERVED),
            ("language", LANGUAGES),
            ("text_order", TEXT_ORDERS),
        ):
            if mention[field] not in allowed:
                raise EntityResolutionError(f"{field} is not governed")
        _nonempty(mention["span_text"], f"mentions[{index}].span_text")
        if mention["text_order"] == "visual" and mention["language"] != "ar":
            raise EntityResolutionError("visual text_order is permitted only for Arabic")
        _validate_address(mention, index)
        _validate_kind_fields(mention, index, configured)
        validated.append(mention)
    _validate_subjects(validated)


def _mention_from_dict(payload: dict[str, Any]) -> Mention:
    return Mention(
        mention_id=payload["mention_id"],
        source_kind=payload["source_kind"],
        address=dict(payload["address"]),
        span_text=payload["span_text"],
        mention_kind=payload["mention_kind"],
        entity_type_observed=payload["entity_type_observed"],
        language=payload["language"],
        text_order=payload["text_order"],
        subject_mention_id=payload["subject_mention_id"],
        alias=dict(payload["alias"]) if payload["alias"] is not None else None,
        identifier=(
            dict(payload["identifier"]) if payload["identifier"] is not None else None
        ),
        statement=(
            dict(payload["statement"]) if payload["statement"] is not None else None
        ),
        designation_text=payload["designation_text"],
    )


def _list_from_payload(payload: dict[str, Any]) -> MentionList:
    return MentionList(
        schema_version=payload["schema_version"],
        list_id=payload["list_id"],
        recorded_on=payload["recorded_on"],
        recorded_by_seat=payload["recorded_by_seat"],
        consultation_summary_text=payload["consultation_summary_text"],
        mentions=tuple(_mention_from_dict(item) for item in payload["mentions"]),
    )


def mention_list_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise EntityResolutionError(f"Cannot read mention list: {path}") from exc


def load_mention_list(path: Path) -> MentionList:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EntityResolutionError(f"Cannot load mention list: {path}") from exc
    validate_mention_list(payload)
    if path.stem != payload["list_id"]:
        raise EntityResolutionError("mention list file name must equal list_id")
    return _list_from_payload(payload)


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise EntityResolutionError("Invalid RFC 6901 JSON pointer")
    value = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(value, list):
                if token == "-" or not token.isdigit():
                    raise KeyError(token)
                value = value[int(token)]
            elif isinstance(value, Mapping):
                value = value[token]
            else:
                raise KeyError(token)
        except (KeyError, IndexError) as exc:
            raise EntityResolutionError(
                f"JSON pointer does not resolve: {pointer}"
            ) from exc
    return value


def _payload_and_metadata(value: Any) -> tuple[dict[str, Any], str, str]:
    if hasattr(value, "record"):
        payload = value.record
    elif hasattr(value, "payload"):
        payload = value.payload
    else:
        payload = value
    if not isinstance(payload, dict):
        raise EntityResolutionError("Verified input must contain a JSON object")
    digest = getattr(value, "sha256", None)
    if not isinstance(digest, str):
        digest = hashlib.sha256(canonical_dumps(payload).encode("utf-8")).hexdigest()
    as_of_date = payload.get("as_of_date")
    if not isinstance(as_of_date, str):
        as_of_date = payload.get("metadata", {}).get("as_of_date")
    if not isinstance(as_of_date, str):
        raise EntityResolutionError("Verified input has no as_of_date")
    return payload, digest, as_of_date


def _document_line(payload: dict[str, Any], mention: Mention) -> str:
    page_index = mention.address["page_index"]
    line_index = mention.address["line_index"]
    try:
        page = payload["pages"][page_index - 1]
        if page.get("page_index") != page_index:
            raise KeyError("page_index")
        line = page["lines"][line_index - 1]
    except (KeyError, IndexError, TypeError) as exc:
        raise EntityResolutionError(
            f"{mention.mention_id} document address does not resolve"
        ) from exc
    if not isinstance(line, str):
        raise EntityResolutionError("Addressed document line must be a string")
    return line


def _screen_and_verify_span(
    mention: Mention, line: str | None, rules: EntityRules
) -> None:
    folded = mention.span_text.casefold()
    if any(token in folded for token in rules.span_forbidden_substrings):
        raise EntityResolutionError(
            f"{mention.mention_id} span contains a forbidden token"
        )
    if line is not None and mention.span_text not in line:
        raise EntityResolutionError(
            f"{mention.mention_id} span is not a verbatim substring"
        )
    if mention.alias is not None and any(
        value not in mention.span_text for value in mention.alias.values()
    ):
        raise EntityResolutionError(
            f"{mention.mention_id} alias sub-spans must occur in span_text"
        )
    if mention.statement is not None:
        effective = mention.statement["effective_date_text"]
        if line is None or effective not in line:
            raise EntityResolutionError(
                f"{mention.mention_id} effective_date_text is absent from its line"
            )
        owner = mention.statement["owner_span_text"]
        if owner is not None and owner not in mention.span_text:
            raise EntityResolutionError(
                f"{mention.mention_id} owner_span_text is absent from span_text"
            )


def verify_mentions(
    mentions: MentionList | dict[str, Any],
    *,
    documents: Mapping[str, Any],
    snapshots: Mapping[str, Any],
    rules: EntityRules | None = None,
) -> tuple[VerifiedMention, ...]:
    """Verify all spans atomically against addressed stored inputs."""
    configured = rules or entity_resolution_rules()
    if isinstance(mentions, dict):
        validate_mention_list(mentions, rules=configured)
        mention_list = _list_from_payload(mentions)
    else:
        mention_list = mentions
    verified: list[VerifiedMention] = []
    for mention in sorted(mention_list.mentions, key=lambda item: item.mention_id):
        if mention.source_kind == "DOCUMENT_RECORD":
            document_id = mention.address["document_id"]
            if document_id not in documents:
                raise EntityResolutionError(f"Missing document record: {document_id}")
            payload, digest, as_of_date = _payload_and_metadata(documents[document_id])
            if payload.get("document_id") != document_id:
                raise EntityResolutionError("Document input identity mismatch")
            line = _document_line(payload, mention)
            _screen_and_verify_span(mention, line, configured)
        else:
            snapshot_id = mention.address["snapshot_id"]
            if snapshot_id not in snapshots:
                raise EntityResolutionError(f"Missing public snapshot: {snapshot_id}")
            payload, digest, as_of_date = _payload_and_metadata(snapshots[snapshot_id])
            if payload.get("snapshot_id") not in (None, snapshot_id):
                raise EntityResolutionError("Snapshot input identity mismatch")
            value = resolve_json_pointer(payload, mention.address["json_pointer"])
            if not isinstance(value, str) or value != mention.span_text:
                raise EntityResolutionError(
                    f"{mention.mention_id} snapshot pointer must resolve to equal string"
                )
            _screen_and_verify_span(mention, None, configured)
        verified.append(
            VerifiedMention(
                mention=mention,
                input_sha256=digest,
                as_of_date=as_of_date,
            )
        )
    return tuple(verified)
