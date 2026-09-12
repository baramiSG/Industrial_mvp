from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from acquisition_doubles import entity_document_double, entity_snapshot_double
from ior_mvp.acquisition.contracts import SnapshotWriteConflict, canonical_dumps
from ior_mvp.acquisition.entities.mentions import Mention, VerifiedMention
from ior_mvp.acquisition.entities.resolver import resolve
from ior_mvp.acquisition.entities.rules import EntityResolutionError, entity_resolution_rules
from ior_mvp.acquisition.entities.store import (
    DocumentInput,
    EntityStore,
    SnapshotInput,
    artifact_id,
    build_entity_resolution,
    reconstruct_entity_artifact,
    validate_entity_artifact,
)

DOC_ID = "DOC-TEST-FIXTURE-0123456789ab-0123456789ab"


def _mention(
    mention_id: str,
    span: str,
    *,
    kind: str = "COMPANY_NAME",
    entity_type: str = "COMPANY",
    page: int = 1,
    line: int = 1,
    subject: str | None = None,
    alias: dict | None = None,
    identifier: dict | None = None,
    statement: dict | None = None,
    designation: str | None = None,
    source_kind: str = "DOCUMENT_RECORD",
    address: dict | None = None,
    language: str = "en",
    text_order: str = "logical",
) -> VerifiedMention:
    return VerifiedMention(
        mention=Mention(
            mention_id=mention_id,
            source_kind=source_kind,
            address=address
            or {"document_id": DOC_ID, "page_index": page, "line_index": line},
            span_text=span,
            mention_kind=kind,
            entity_type_observed=entity_type,
            language=language,
            text_order=text_order,
            subject_mention_id=subject,
            alias=alias,
            identifier=identifier,
            statement=statement,
            designation_text=designation,
        ),
        input_sha256="a" * 64,
        as_of_date="2026-09-12",
    )


def _resolve(*mentions: VerifiedMention, documents=None, snapshots=None):
    return resolve(
        tuple(mentions),
        documents=documents or {},
        snapshots=snapshots or {},
        rules=entity_resolution_rules(),
    )


def _link(result, mention_id: str) -> dict:
    return next(item for item in result.links if item["mention_id"] == mention_id)


def test_company_name_mints_and_exact_self_links() -> None:
    result = _resolve(_mention("M-001", "Acme Company"))
    assert len(result.entities) == 1
    assert _link(result, "M-001")["rule_applied"] == "MINTED_FROM_MENTION"
    assert _link(result, "M-001")["link_status"] == "EXACT_DOCUMENT_EVIDENCE"


def test_alias_statement_creates_alias_then_acronym_links_exact() -> None:
    result = _resolve(
        _mention(
            "M-001",
            "Acme Company (ACME)",
            kind="ALIAS_STATEMENT",
            alias={"primary_span_text": "Acme Company", "alias_span_text": "ACME"},
        ),
        _mention("M-002", "ACME"),
    )
    entity = result.entities[0]
    assert {name["role"] for name in entity["names"]} == {"PRIMARY", "ALIAS"}
    assert _link(result, "M-002")["rule_applied"] == "EXACT_ALIAS_EQUALITY"


def test_legal_form_variant_is_pending_with_candidate_and_mints_nothing() -> None:
    result = _resolve(
        _mention("M-001", "Acme Company"),
        _mention("M-002", "Acme"),
    )
    link = _link(result, "M-002")
    assert len(result.entities) == 1
    assert link["link_status"] == "PROPOSED_PENDING_REVIEW"
    assert link["candidate_entity_ids"] == [result.entities[0]["entity_id"]]


def test_multiple_exact_candidates_are_pending() -> None:
    first = _resolve(_mention("M-001", "Acme"))
    duplicated = copy.deepcopy(first.entities[0])
    duplicated["entity_id"] = "COMPANY-ffffffffffffffff"
    duplicated["canonical_key"] += "-other"
    result = resolve(
        (_mention("M-002", "Acme"),),
        documents={},
        snapshots={},
        rules=entity_resolution_rules(),
        seed_entities=(first.entities[0], duplicated),
    )
    assert _link(result, "M-002")["rule_applied"] == "MULTIPLE_CANDIDATES"


def test_plant_location_canonical_within_window_is_exact_and_mints_site_locality_plant() -> None:
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "Al-Jubail",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=3,
            subject="M-001",
        ),
    )
    plant = next(entity for entity in result.entities if entity["entity_type"] == "PLANT")
    assert plant["granularity"] == "SITE_LOCALITY"
    assert _link(result, "M-002")["rule_applied"] == "EXACT_LOCALITY_WITHIN_WINDOW"


def test_plant_location_variant_spelling_is_pending() -> None:
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "Al-Jubail",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=2,
            subject="M-001",
        ),
        _mention(
            "M-003",
            "Al-Jubail Industrial City",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=3,
            subject="M-001",
        ),
    )
    assert _link(result, "M-003")["rule_applied"] == "LOCALITY_VARIANT"


def test_plant_location_subject_on_other_page_is_pending() -> None:
    result = _resolve(
        _mention("M-001", "Acme", page=1),
        _mention(
            "M-002",
            "Al-Jubail",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            page=2,
            subject="M-001",
        ),
    )
    assert _link(result, "M-002")["rule_applied"] == "SUBJECT_OUTSIDE_WINDOW"


def test_plant_never_minted_from_company_name_alone() -> None:
    result = _resolve(_mention("M-001", "Acme"))
    assert all(entity["entity_type"] != "PLANT" for entity in result.entities)


def test_line_statement_without_designation_is_unresolved_count_only() -> None:
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "five production lines",
            kind="LINE_STATEMENT",
            entity_type="LINE",
            subject="M-001",
        ),
    )
    assert _link(result, "M-002")["unresolved_reason"] == "COUNT_ONLY_NO_IDENTITY"


def test_line_statement_with_designation_mints_line_under_plant() -> None:
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "Al-Jubail",
            kind="PLANT_LOCATION",
            entity_type="PLANT",
            line=2,
            subject="M-001",
        ),
        _mention(
            "M-003",
            "Line 4",
            kind="LINE_STATEMENT",
            entity_type="LINE",
            line=3,
            subject="M-001",
            designation="Line 4",
        ),
    )
    assert any(entity["entity_type"] == "LINE" for entity in result.entities)
    assert _link(result, "M-003")["link_status"] == "EXACT_DOCUMENT_EVIDENCE"


def test_identifier_equality_links_deterministic_and_records_identifier() -> None:
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "CR 123",
            kind="IDENTIFIER",
            subject="M-001",
            identifier={"kind": "COMMERCIAL_REGISTRATION", "value_text": "123"},
        ),
        _mention("M-003", "Acme Holdings"),
        _mention(
            "M-004",
            "CR 123",
            kind="IDENTIFIER",
            subject="M-003",
            identifier={"kind": "COMMERCIAL_REGISTRATION", "value_text": "123"},
        ),
    )
    assert _link(result, "M-004")["link_status"] == "DETERMINISTIC_IDENTIFIER"
    identified = next(entity for entity in result.entities if entity["identifiers"])
    assert identified["identifiers"][0]["value_text"] == "123"


def test_ownership_statement_records_dedupe_citations_and_keep_dates() -> None:
    statement = {
        "statement_kind": "OWNERSHIP_CHANGE",
        "effective_date_text": "2004",
        "owner_span_text": None,
        "description_text": "became 100% Saudi-owned in 2004",
    }
    result = _resolve(
        _mention("M-001", "Acme"),
        _mention(
            "M-002",
            "became 100% Saudi-owned in 2004",
            kind="OWNERSHIP_STATEMENT",
            subject="M-001",
            statement=statement,
        ),
        _mention(
            "M-003",
            "became 100% Saudi-owned in 2004",
            kind="OWNERSHIP_STATEMENT",
            subject="M-001",
            statement=statement,
        ),
    )
    assert len(result.ownership_records) == 1
    assert len(result.ownership_records[0]["evidence"]) == 2
    assert result.ownership_records[0]["effective_date_text"] == "2004"


def test_publisher_standards_authority_is_unresolved_out_of_scope() -> None:
    result = _resolve(
        _mention(
            "M-001",
            "SASO",
            kind="PUBLISHER_NAME",
            entity_type="STANDARDS_AUTHORITY",
        )
    )
    assert _link(result, "M-001")["unresolved_reason"] == "OUT_OF_SCOPE_ENTITY_TYPE"


def test_documents_without_mentions_listed_and_passports_unresolved_no_mention_recorded() -> None:
    doc = entity_document_double(DOC_ID)
    result = _resolve(documents={DOC_ID: doc})
    assert result.documents_without_mentions == [DOC_ID]
    assert result.passport_links[0]["unresolved_reason"] == "NO_MENTION_RECORDED"


def test_passport_links_cover_every_input_passport_exactly_once() -> None:
    doc = entity_document_double(DOC_ID)
    snapshot_id = "FIX-ENTITY-DOUBLE"
    snapshot = entity_snapshot_double(
        snapshot_id,
        sources=[
            {"source": "Unaddressed", "evidence_id": "S-0"},
            {"source": "Acme", "evidence_id": "S-1"},
        ],
    )
    result = _resolve(
        _mention("M-001", "Acme", kind="PUBLISHER_NAME"),
        _mention(
            "M-002",
            "Acme",
            kind="PUBLISHER_NAME",
            source_kind="PUBLIC_SNAPSHOT",
            address={
                "snapshot_id": snapshot_id,
                "json_pointer": "/evidence/1/source",
            },
        ),
        documents={DOC_ID: doc},
        snapshots={snapshot_id: snapshot},
    )
    assert len(result.passport_links) == 2
    assert result.passport_links[0]["passport_ref"]["passport_id"] == f"P-{DOC_ID}"
    assert result.passport_links[1]["passport_ref"]["evidence_id"] == "S-1"


def test_observation_links_for_producer_evidence_rows() -> None:
    snapshot_id = "FIX-ENTITY-DOUBLE"
    snapshot = entity_snapshot_double(
        snapshot_id,
        producers=[{"producer": "Acme"}],
    )
    result = _resolve(
        _mention(
            "M-001",
            "Acme",
            kind="PUBLISHER_NAME",
            source_kind="PUBLIC_SNAPSHOT",
            address={
                "snapshot_id": snapshot_id,
                "json_pointer": "/domestic_capability/producer_evidence/0/producer",
            },
        ),
        snapshots={snapshot_id: snapshot},
    )
    assert result.observation_links[0]["link_status"] == "EXACT_DOCUMENT_EVIDENCE"


def test_same_document_url_corroboration_exact_equality_only() -> None:
    url = "https://example.test/entity-double.pdf"
    doc = entity_document_double(DOC_ID, url=url)
    snapshot_id = "FIX-ENTITY-DOUBLE"
    snapshot = entity_snapshot_double(
        snapshot_id,
        sources=[{"source": "Acme", "evidence_id": "S-1", "url": url}],
    )
    result = _resolve(
        _mention("M-001", "Acme", kind="PUBLISHER_NAME"),
        _mention(
            "M-002",
            "Acme",
            kind="PUBLISHER_NAME",
            source_kind="PUBLIC_SNAPSHOT",
            address={
                "snapshot_id": snapshot_id,
                "json_pointer": "/evidence/0/source",
            },
        ),
        documents={DOC_ID: doc},
        snapshots={snapshot_id: snapshot},
    )
    snapshot_link = next(
        item
        for item in result.passport_links
        if item["passport_ref"]["kind"] == "PUBLIC_SNAPSHOT_PASSPORT"
    )
    assert snapshot_link["corroboration"] == {"same_document_url_as": DOC_ID}
    snapshot["evidence"][0]["url"] = f"{url}/"
    changed = _resolve(
        _mention("M-001", "Acme", kind="PUBLISHER_NAME"),
        _mention(
            "M-002",
            "Acme",
            kind="PUBLISHER_NAME",
            source_kind="PUBLIC_SNAPSHOT",
            address={
                "snapshot_id": snapshot_id,
                "json_pointer": "/evidence/0/source",
            },
        ),
        documents={DOC_ID: doc},
        snapshots={snapshot_id: snapshot},
    )
    assert changed.passport_links[-1]["corroboration"] is None


def _build_fixture(tmp_path: Path):
    data_root = tmp_path / "data"
    mention_path = data_root / "entities" / "mentions" / "test-double-mentions.json"
    mention_path.parent.mkdir(parents=True)
    payload = {
        "schema_version": "1.0.0",
        "list_id": "test-double-mentions",
        "recorded_on": "2026-09-12",
        "recorded_by_seat": "TEST-DOUBLE",
        "consultation_summary_text": "TEST DOUBLE — NOT REAL EVIDENCE.",
        "mentions": [
            {
                "mention_id": "M-001",
                "source_kind": "DOCUMENT_RECORD",
                "address": {
                    "document_id": DOC_ID,
                    "page_index": 1,
                    "line_index": 1,
                },
                "span_text": "Acme Company",
                "mention_kind": "PUBLISHER_NAME",
                "entity_type_observed": "COMPANY",
                "language": "en",
                "text_order": "logical",
                "subject_mention_id": None,
                "alias": None,
                "identifier": None,
                "statement": None,
                "designation_text": None,
            }
        ],
    }
    mention_path.write_text(canonical_dumps(payload), encoding="utf-8")
    doc = entity_document_double(
        DOC_ID, [["TEST DOUBLE — NOT REAL EVIDENCE: Acme Company"]]
    )
    doc_path = data_root / "documents" / "TEST-FIXTURE" / "records" / f"{DOC_ID}.json"
    doc_path.parent.mkdir(parents=True)
    doc_path.write_text(canonical_dumps(doc), encoding="utf-8")

    def documents(_root, *, allow_test_double=False):
        assert allow_test_double
        return {
            DOC_ID: DocumentInput.from_path(DOC_ID, doc_path, doc),
        }

    def snapshots(_root):
        return {}

    report = build_entity_resolution(
        data_root,
        mention_list_id="test-double-mentions",
        document_loader=documents,
        snapshot_loader=snapshots,
        allow_test_double=True,
    )
    artifact_path = Path(report.artifact_path)
    return data_root, mention_path, doc_path, artifact_path, json.loads(
        artifact_path.read_text(encoding="utf-8")
    )


def test_artifact_exact_keys_sorted_lists_and_validate_negative_probes(
    tmp_path: Path,
) -> None:
    _, _, _, _, artifact = _build_fixture(tmp_path)
    validate_entity_artifact(artifact, allow_test_double=True)
    assert artifact["entities"] == sorted(
        artifact["entities"], key=lambda item: item["entity_id"]
    )
    probes = []
    missing = copy.deepcopy(artifact)
    missing.pop("quality_summary")
    probes.append(missing)
    extra = copy.deepcopy(artifact)
    extra["extra"] = True
    probes.append(extra)
    bad_id = copy.deepcopy(artifact)
    bad_id["entities"][0]["entity_id"] = "bad"
    probes.append(bad_id)
    resolved_without_id = copy.deepcopy(artifact)
    resolved_without_id["links"][0]["entity_id"] = None
    probes.append(resolved_without_id)
    pending_with_id = copy.deepcopy(artifact)
    pending_with_id["links"][0]["link_status"] = "PROPOSED_PENDING_REVIEW"
    probes.append(pending_with_id)
    bad_reason = copy.deepcopy(artifact)
    bad_reason["links"][0]["link_status"] = "UNRESOLVED"
    bad_reason["links"][0]["entity_id"] = None
    bad_reason["links"][0]["unresolved_reason"] = "MAGIC"
    probes.append(bad_reason)
    bad_counts = copy.deepcopy(artifact)
    bad_counts["counts"]["entities_by_type"]["COMPANY"] = 99
    probes.append(bad_counts)
    synthetic = copy.deepcopy(artifact)
    synthetic["synthetic_flag"] = True
    probes.append(synthetic)
    for probe in probes:
        with pytest.raises(EntityResolutionError):
            validate_entity_artifact(probe, allow_test_double=True)


def test_artifact_write_once_identical_ok_different_conflict(tmp_path: Path) -> None:
    _, _, _, artifact_path, artifact = _build_fixture(tmp_path)
    store = EntityStore(artifact_path.parents[1])
    assert store.write_artifact(artifact, allow_test_double=True) == artifact_path
    changed = copy.deepcopy(artifact)
    changed["transformation_record"]["exclusions"] = ["changed"]
    with pytest.raises(SnapshotWriteConflict):
        store.write_artifact(changed, allow_test_double=True)


def test_artifact_id_from_recorded_on_and_mention_list_hash(tmp_path: Path) -> None:
    _, mention_path, _, _, artifact = _build_fixture(tmp_path)
    import hashlib

    digest = hashlib.sha256(mention_path.read_bytes()).hexdigest()
    assert artifact["artifact_id"] == artifact_id("2026-09-12", digest)


def test_reconstruct_artifact_match_and_tamper(tmp_path: Path) -> None:
    data_root, mention_path, doc_path, artifact_path, _ = _build_fixture(tmp_path)
    assert reconstruct_entity_artifact(
        artifact_path, data_root=data_root
    ).match
    original = mention_path.read_bytes()
    mention_path.write_bytes(original + b" ")
    assert reconstruct_entity_artifact(
        artifact_path, data_root=data_root
    ).detail["reason"] == "MENTION_LIST_HASH_MISMATCH"
    mention_path.write_bytes(original)
    doc_original = doc_path.read_bytes()
    doc_path.write_bytes(doc_original + b" ")
    assert reconstruct_entity_artifact(
        artifact_path, data_root=data_root
    ).detail["reason"] == "INPUT_HASH_MISMATCH"


def test_build_is_deterministic_across_two_process_invocations(tmp_path: Path) -> None:
    _, _, _, artifact_path, artifact = _build_fixture(tmp_path)
    before = artifact_path.read_bytes()
    validate_entity_artifact(artifact, allow_test_double=True)
    assert artifact_path.read_bytes() == before


def test_visual_order_spans_match_only_visual_order_names() -> None:
    visual = "ةئيهلا"
    result = _resolve(
        _mention(
            "M-001", visual, language="ar", text_order="visual"
        ),
        _mention(
            "M-002", visual, language="ar", text_order="logical"
        ),
    )
    assert len(result.entities) == 2


def test_operator_labels_are_never_matched() -> None:
    doc = entity_document_double(DOC_ID)
    doc["declared"] = {"publisher_text": "Acme"}
    result = _resolve(documents={DOC_ID: doc})
    assert result.entities == []


def test_zero_links_above_deterministic_without_identifier_or_exact_span() -> None:
    result = _resolve(
        _mention("M-001", "Acme Company"),
        _mention("M-002", "Acme"),
    )
    assert not any(
        link["link_status"] == "DETERMINISTIC_IDENTIFIER" for link in result.links
    )
