"""Plant-family link validation is evidence-bound and write-once."""

from __future__ import annotations

import copy
import json

import pytest


def _valid():
    return {
        "schema_version": "1.0.0",
        "list_id": "plant-family-links-v1",
        "recorded_on": "2026-09-12",
        "entries": [
            {
                "link_id": "P1-coated-steel-core-process",
                "entity_id": "P1",
                "family_id": "coated_steel",
                "signal_type": "core_process",
                "evidence_class": "C",
                "evidence": [
                    {
                        "kind": "document_line",
                        "document_id": "DOC-1",
                        "page_index": 0,
                        "line_index": 0,
                        "verbatim_span": "cold rolled steel",
                    }
                ],
                "reviewer_status": "agent_authored_pending_domain_review",
            }
        ],
    }


def _inputs():
    entities = {"entities": [{"entity_id": "P1", "entity_type": "PLANT"}]}
    documents = {"DOC-1": {"pages": [{"lines": ["cold rolled steel plant"]}]}}
    snapshots = {"SNAP-1": {"rows": [{"value": "coated steel"}]}}
    return entities, documents, snapshots


def test_link_list_schema_and_write_once(tmp_path):
    from ior_mvp.screening.inputs import validate_family_links, write_family_links

    record = _valid()
    validate_family_links(record, *_inputs())
    path = write_family_links(record, tmp_path)
    assert json.loads(path.read_text()) == record
    assert write_family_links(record, tmp_path) == path
    changed = copy.deepcopy(record)
    changed["recorded_on"] = "2026-09-13"
    with pytest.raises(ValueError, match="conflict"):
        write_family_links(changed, tmp_path)


def test_link_requires_existing_plant_entity_id():
    from ior_mvp.screening.inputs import validate_family_links

    entities, documents, snapshots = _inputs()
    entities["entities"][0]["entity_type"] = "COMPANY"
    with pytest.raises(ValueError, match="PLANT"):
        validate_family_links(_valid(), entities, documents, snapshots)


def test_link_span_verified_verbatim_against_document_line():
    from ior_mvp.screening.inputs import validate_family_links

    validate_family_links(_valid(), *_inputs())


def test_link_span_verified_against_snapshot_json_pointer():
    from ior_mvp.screening.inputs import validate_family_links

    record = _valid()
    record["entries"][0]["evidence"] = [
        {
            "kind": "snapshot_value",
            "snapshot_id": "SNAP-1",
            "json_pointer": "/rows/0/value",
            "value": "coated steel",
        }
    ]
    validate_family_links(record, *_inputs())


def test_link_mismatch_refuses_build_before_writing(tmp_path):
    from ior_mvp.screening.inputs import validate_family_links

    record = _valid()
    record["entries"][0]["evidence"][0]["verbatim_span"] = "not present"
    with pytest.raises(ValueError, match="verbatim"):
        validate_family_links(record, *_inputs())
    assert not list(tmp_path.iterdir())


def test_link_evidence_class_is_c_only_and_no_nameplate_field():
    from ior_mvp.screening.inputs import validate_family_links

    record = _valid()
    record["entries"][0]["evidence_class"] = "B"
    with pytest.raises(ValueError, match="Class C"):
        validate_family_links(record, *_inputs())
    record = _valid()
    record["entries"][0]["nameplate_capacity"] = 100
    with pytest.raises(ValueError, match="keys"):
        validate_family_links(record, *_inputs())
