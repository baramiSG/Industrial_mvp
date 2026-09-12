from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import RawStoreIntegrityError
from ior_mvp.acquisition.entities.mentions import (
    EntityResolutionError,
    load_mention_list,
    mention_list_sha256,
    validate_mention_list,
    verify_mentions,
)
from ior_mvp.acquisition.entities.store import EntityStore
from ior_mvp.config import PROJECT_ROOT

DOC_ID = "DOC-PRODUCER-UNICOIL-0123456789ab-0123456789ab"
SNAPSHOT_ID = "monitor-r3-only"
LINE = "UNICOIL (Universal Metal Coating Company) was established in 1997."


def _mention(**changes) -> dict:
    value = {
        "mention_id": "M-001",
        "source_kind": "DOCUMENT_RECORD",
        "address": {
            "document_id": DOC_ID,
            "page_index": 1,
            "line_index": 1,
        },
        "span_text": "UNICOIL",
        "mention_kind": "COMPANY_NAME",
        "entity_type_observed": "COMPANY",
        "language": "en",
        "text_order": "logical",
        "subject_mention_id": None,
        "alias": None,
        "identifier": None,
        "statement": None,
        "designation_text": None,
    }
    value.update(changes)
    return value


def _payload(*mentions: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "list_id": "mentions-unit",
        "recorded_on": "2026-09-12",
        "recorded_by_seat": "implementer-sol",
        "consultation_summary_text": "Synthetic unit-test mentions only.",
        "mentions": list(mentions or (_mention(),)),
    }


def _write(tmp_path: Path, payload: dict, name: str = "mentions-unit.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _documents(line: str = LINE) -> dict:
    return {
        DOC_ID: {
            "document_id": DOC_ID,
            "as_of_date": "2026-09-12",
            "pages": [{"page_index": 1, "lines": [line]}],
        }
    }


def _snapshots() -> dict:
    return {
        SNAPSHOT_ID: {
            "snapshot_id": SNAPSHOT_ID,
            "as_of_date": "2026-09-12",
            "producer_evidence": [{"producer_name": "UNICOIL"}],
        }
    }


def test_mention_list_exact_keys_enums_and_unique_ids() -> None:
    validate_mention_list(_payload())
    duplicate = _payload(_mention(), _mention())
    with pytest.raises(EntityResolutionError, match="unique"):
        validate_mention_list(duplicate)
    bad = _payload()
    bad["mentions"][0]["extra"] = "forbidden"
    with pytest.raises(EntityResolutionError, match="unknown"):
        validate_mention_list(bad)
    bad_enum = _payload(_mention(mention_kind="GUESSED_NAME"))
    with pytest.raises(EntityResolutionError, match="mention_kind"):
        validate_mention_list(bad_enum)


@pytest.mark.parametrize(
    "mention",
    [
        _mention(mention_kind="ALIAS_STATEMENT"),
        _mention(mention_kind="IDENTIFIER", subject_mention_id="M-000"),
        _mention(mention_kind="OWNERSHIP_STATEMENT", subject_mention_id="M-000"),
        _mention(mention_kind="LINE_STATEMENT", subject_mention_id="M-000"),
        _mention(mention_kind="COMPANY_NAME", alias={"primary_span_text": "A", "alias_span_text": "B"}),
    ],
)
def test_mention_kind_specific_required_fields_fail_closed(mention: dict) -> None:
    with pytest.raises(EntityResolutionError):
        validate_mention_list(_payload(mention))


def test_document_span_must_be_verbatim_substring_of_addressed_line() -> None:
    payload = _payload(_mention(span_text="Universal  Metal Coating Company"))
    with pytest.raises(EntityResolutionError, match="verbatim"):
        verify_mentions(payload, documents=_documents(), snapshots={})


def test_snapshot_json_pointer_must_resolve_to_equal_string() -> None:
    mention = _mention(
        source_kind="PUBLIC_SNAPSHOT",
        address={
            "snapshot_id": SNAPSHOT_ID,
            "json_pointer": "/producer_evidence/0/producer_name",
        },
        span_text="UNICOIL",
    )
    verified = verify_mentions(_payload(mention), documents={}, snapshots=_snapshots())
    assert verified[0].mention.span_text == "UNICOIL"
    mention["span_text"] = "Unicoil"
    with pytest.raises(EntityResolutionError, match="equal"):
        verify_mentions(_payload(mention), documents={}, snapshots=_snapshots())


def test_alias_sub_spans_must_be_substrings_of_span() -> None:
    alias = _mention(
        span_text="UNICOIL (Universal Metal Coating Company)",
        mention_kind="ALIAS_STATEMENT",
        alias={
            "primary_span_text": "Universal Metal Coating Company",
            "alias_span_text": "NOT PRESENT",
        },
    )
    with pytest.raises(EntityResolutionError, match="alias"):
        verify_mentions(_payload(alias), documents=_documents(), snapshots={})


def test_effective_date_text_must_appear_in_addressed_line() -> None:
    ownership = _mention(
        mention_id="M-002",
        span_text="was established in 1997",
        mention_kind="OWNERSHIP_STATEMENT",
        subject_mention_id="M-001",
        statement={
            "statement_kind": "OWNERSHIP_CHANGE",
            "effective_date_text": "2004",
            "owner_span_text": None,
            "description_text": "was established in 1997",
        },
    )
    with pytest.raises(EntityResolutionError, match="effective_date_text"):
        verify_mentions(
            _payload(_mention(), ownership),
            documents=_documents(),
            snapshots={},
        )


def test_subject_must_be_earlier_same_document_name_mention() -> None:
    location = _mention(
        mention_id="M-001",
        span_text="Al-Jubail",
        mention_kind="PLANT_LOCATION",
        entity_type_observed="PLANT",
        subject_mention_id="M-002",
    )
    subject = _mention(mention_id="M-002")
    with pytest.raises(EntityResolutionError, match="earlier"):
        validate_mention_list(_payload(location, subject))


@pytest.mark.parametrize("span", ["a@b.test", "CONTACT NAME", "support EMAIL", "Phone"])
def test_span_screen_rejects_forbidden_tokens(span: str) -> None:
    with pytest.raises(EntityResolutionError, match="forbidden"):
        verify_mentions(
            _payload(_mention(span_text=span)),
            documents=_documents(f"prefix {span} suffix"),
            snapshots={},
        )


def test_visual_text_order_only_for_arabic() -> None:
    with pytest.raises(EntityResolutionError, match="visual"):
        validate_mention_list(_payload(_mention(text_order="visual", language="en")))
    validate_mention_list(
        _payload(
            _mention(
                span_text="ةئيهلا",
                language="ar",
                text_order="visual",
                entity_type_observed="STANDARDS_AUTHORITY",
                mention_kind="PUBLISHER_NAME",
            )
        )
    )


def test_mention_list_sha256_and_path_rules(tmp_path: Path) -> None:
    path = _write(tmp_path, _payload())
    loaded = load_mention_list(path)

    assert loaded.list_id == "mentions-unit"
    assert len(mention_list_sha256(path)) == 64
    mismatch = _write(tmp_path, _payload(), "different-name.json")
    with pytest.raises(EntityResolutionError, match="file name"):
        load_mention_list(mismatch)
    unsafe = copy.deepcopy(_payload())
    unsafe["list_id"] = "../escape"
    with pytest.raises(EntityResolutionError, match="list_id"):
        validate_mention_list(unsafe)


def test_test_double_refused_under_repository_data_entities() -> None:
    store = EntityStore(PROJECT_ROOT / "data" / "entities")
    artifact = {
        "artifact_id": "ENTITIES-2026-09-12-0123456789ab",
        "inputs": {"mention_list": {"list_id": "test-double-unit"}},
    }
    with pytest.raises(RawStoreIntegrityError, match="test double"):
        store.write_artifact(artifact)


@pytest.mark.parametrize(
    "root",
    [
        PROJECT_ROOT / "data" / "snapshots" / "public" / "entities",
        PROJECT_ROOT / "data" / "synthetic" / "entities",
    ],
)
def test_root_guard_rejects_frozen_roots(root: Path) -> None:
    with pytest.raises(RawStoreIntegrityError, match="may not be under"):
        EntityStore(root)
