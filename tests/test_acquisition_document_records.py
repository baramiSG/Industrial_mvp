"""Read-only repository-tree oracles for the stored S12b DocumentRecords.

S12B-IR3-F01 (OD-11/OD-12): the six ``saso_documents`` records built under
``PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0`` store the publisher's Arabic cover lines in
visual (painted) order, declare ``ar`` truthfully and reference the corrected
``saso_documents-v4`` list; KNOWN_LIMITATIONS names each affected document_id.

S12B-IR3-F02: RunReport ``requests_made`` 27 / 21 are the deferred aggregate-count
artefact (sum of per-unit cumulative ``RequestBudget.used`` echoes), not transport
counts; the stored page contracts prove 7 and 6 fetches.

No network, no derivation: every assertion reads stored artifacts and control text.
"""

from __future__ import annotations

import json
import re

import pytest

from ior_mvp.config import PROJECT_ROOT

DOCUMENTS_ROOT = PROJECT_ROOT / "data" / "documents"
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
KNOWN_LIMITATIONS = PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md"
ARCHITECTURE_DECISIONS = PROJECT_ROOT / "docs" / "ARCHITECTURE_DECISIONS.md"

ARABIC_SCRIPT = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")

# Stored verbatim under PDF_TEXT_LAYER_PYPDF_LAYOUT 1.0.0. The SASO publisher PDFs paint
# this Arabic cover line in VISUAL (left-to-right glyph) order, so the stored string is
# the visual-order form of the SASO authority name — see KNOWN_LIMITATIONS (visual-order
# row) and OD-12. It is pinned exactly as stored: no bidi reordering, no reshaping.
SASO_AUTHORITY_LINE_VISUAL_ORDER = "ةدوجلاو سيياقلماو تافصاوملل ةيدوعسلا ةئيهلا"
# Reading the stored characters right-to-left yields the logical authority-name prefix.
SASO_AUTHORITY_LOGICAL_PREFIX = "الهيئة السعودية للمواصفات"

SASO_DOCUMENT_IDS = (
    "DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9",
    "DOC-SASO-DOCUMENTS-69ea78b9cd4e-000691d40661",
    "DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54",
    "DOC-SASO-DOCUMENTS-c778364b4087-b89ca084a45d",
    "DOC-SASO-DOCUMENTS-d5e242b67294-9189ec73295b",
    "DOC-SASO-DOCUMENTS-e57d73b6e5b7-0e0d00cb00cf",
)

# (document_id, page_index, line_index, leading layout spaces as stored)
SASO_COVER_LINES = (
    ("DOC-SASO-DOCUMENTS-641a518f410a-1bfd6143aaa9", 1, 14, 41),
    ("DOC-SASO-DOCUMENTS-710bf26c140e-b25658901d54", 1, 12, 42),
)


def _record(source_id: str, document_id: str) -> dict:
    path = DOCUMENTS_ROOT / source_id / "records" / f"{document_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _s12b_known_limitations_section() -> str:
    text = KNOWN_LIMITATIONS.read_text(encoding="utf-8")
    section = text.split("## S12b document acquisition outcomes", 1)[1]
    return section.split("\n## ", 1)[0]


def _adr_017_section() -> str:
    text = ARCHITECTURE_DECISIONS.read_text(encoding="utf-8")
    section = text.split("## ADR-017", 1)[1]
    return section.split("\n## ADR-", 1)[0]


@pytest.mark.parametrize(
    "document_id,page_index,line_index,leading_spaces", SASO_COVER_LINES
)
def test_saso_record_declares_arabic_references_v4_and_pins_visual_order_cover_line(
    document_id: str, page_index: int, line_index: int, leading_spaces: int
) -> None:
    record = _record("saso_documents", document_id)
    assert record["document_id"] == document_id
    # (a) the declaration is truthful: the derived text is Arabic (with English annexes where present)
    assert "ar" in record["declared"]["languages"]
    # (b) the record was rebuilt from the corrected declaration list (OD-11), same stored run
    assert record["list_ref"]["list_id"] == "saso_documents-v4"
    assert record["list_ref"]["path"] == "documents/saso_documents/lists/saso_documents-v4.json"
    assert record["raw_artifact_ref"]["run_id"] == "20260912T053622Z"
    assert record["text_layer"]["method_id"] == "PDF_TEXT_LAYER_PYPDF_LAYOUT"
    assert record["text_layer"]["method_version"] == "1.0.0"
    assert record["text_layer"]["status"] == "COMPLETE"
    # (c) the named cover line equals the exact visual-order string as stored (layout spaces kept)
    page = record["pages"][page_index - 1]
    assert page["page_index"] == page_index
    stored = page["lines"][line_index - 1]
    assert stored == " " * leading_spaces + SASO_AUTHORITY_LINE_VISUAL_ORDER
    assert stored.strip()[::-1].startswith(SASO_AUTHORITY_LOGICAL_PREFIX)
    # (d) KNOWN_LIMITATIONS names this document_id in a row that says "visual order"
    rows = [
        line
        for line in KNOWN_LIMITATIONS.read_text(encoding="utf-8").splitlines()
        if line.startswith("| KL-") and document_id in line
    ]
    assert rows, f"{document_id} is not named in a KNOWN_LIMITATIONS row"
    assert any("visual order" in row for row in rows)


def test_all_six_saso_records_declare_arabic_and_reference_v4() -> None:
    records_dir = DOCUMENTS_ROOT / "saso_documents" / "records"
    stored_ids = tuple(sorted(path.stem for path in records_dir.glob("*.json")))
    assert stored_ids == SASO_DOCUMENT_IDS
    kl_section = _s12b_known_limitations_section()
    for document_id in SASO_DOCUMENT_IDS:
        record = _record("saso_documents", document_id)
        assert "ar" in record["declared"]["languages"], document_id
        assert record["list_ref"]["list_id"] == "saso_documents-v4", document_id
        assert record["evidence"][0]["observation_context"]["languages"] == record["declared"]["languages"]
        assert document_id in kl_section, document_id


@pytest.mark.parametrize("source_id", ["saso_documents", "producer_unicoil"])
def test_declared_languages_are_consistent_with_derived_script(source_id: str) -> None:
    records_dir = DOCUMENTS_ROOT / source_id / "records"
    paths = sorted(records_dir.glob("*.json"))
    assert len(paths) == 6
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        lines = [line for page in record["pages"] for line in page["lines"]]
        has_arabic = any(ARABIC_SCRIPT.search(line) for line in lines)
        has_latin = any(LATIN_LETTERS.search(line) for line in lines)
        languages = record["declared"]["languages"]
        assert ("ar" in languages) == has_arabic, path.name
        if "en" in languages:
            assert has_latin, path.name


def test_saso_v4_list_is_a_declaration_correction_of_v3() -> None:
    lists_dir = DOCUMENTS_ROOT / "saso_documents" / "lists"
    v3 = json.loads((lists_dir / "saso_documents-v3.json").read_text(encoding="utf-8"))
    v4 = json.loads((lists_dir / "saso_documents-v4.json").read_text(encoding="utf-8"))
    assert v4["list_id"] == "saso_documents-v4"
    assert v4["documentation_urls_observed"] == v3["documentation_urls_observed"]
    assert len(v4["entries"]) == len(v3["entries"]) == 6
    for old, new in zip(v3["entries"], v4["entries"]):
        assert new["entry_id"] == old["entry_id"]
        assert new["document_url"] == old["document_url"]
        for key in (
            "publisher_text", "publisher_kind", "document_kind", "expected_content_type",
            "evidence_class_target", "supports", "title_text", "document_date_text",
            "source_reference_text",
        ):
            assert new[key] == old[key], (new["entry_id"], key)
        assert "ar" in new["languages"], new["entry_id"]


@pytest.mark.parametrize(
    "source_id,run_id,expected_payloads,expected_sum,max_requests",
    [
        ("saso_documents", "20260912T053622Z", 7, 27, 7),
        ("producer_unicoil", "20260912T053955Z", 6, 21, 6),
    ],
)
def test_run_report_requests_made_is_aggregate_count_artefact_not_transport_count(
    source_id: str, run_id: str, expected_payloads: int, expected_sum: int, max_requests: int
) -> None:
    run_dirs = sorted(RAW_ROOT.glob(f"{source_id}/*/{run_id}"))
    payloads = [path for run_dir in run_dirs for path in run_dir.glob("page-*.payload.*")]
    assert len(payloads) == expected_payloads
    per_unit: list[int] = []
    for run_dir in run_dirs:
        coverage_path = run_dir / "coverage.json"
        if not coverage_path.exists():
            # the TERMS capture unit stores a contract and payload without a coverage record
            assert (run_dir / "page-0001.payload.html.gz").exists(), run_dir
            continue
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        if coverage["stage"] == "DOCUMENT" and coverage["status"] == "COMPLETE":
            per_unit.append(int(coverage["requests_made"]))
    assert len(per_unit) == 6
    assert sum(per_unit) == expected_sum
    # each unit echoes the cumulative shared RequestBudget.used at its completion
    assert sorted(per_unit) == list(range(expected_payloads - 5, expected_payloads + 1))
    assert max(per_unit) == max_requests
    kl_section = _s12b_known_limitations_section()
    assert "aggregate-count" in kl_section
    adr = _adr_017_section()
    assert "aggregate-count" in adr
    assert "(1 TERMS + 6 documents)" not in adr


def test_saso_terms_page_is_the_seventh_stored_fetch() -> None:
    contracts = sorted(RAW_ROOT.glob("saso_documents/*/20260912T053622Z/page-0001.contract.json"))
    stages = sorted(
        json.loads(path.read_text(encoding="utf-8"))["query_contract"]["stage"] for path in contracts
    )
    assert stages == ["DOCUMENT"] * 6 + ["TERMS"]
    types = {
        json.loads(path.read_text(encoding="utf-8"))["content_type"] for path in contracts
    }
    assert types == {"application/pdf", "text/html"}
    unicoil = sorted(RAW_ROOT.glob("producer_unicoil/*/20260912T053955Z/page-0001.contract.json"))
    assert {
        json.loads(path.read_text(encoding="utf-8"))["content_type"] for path in unicoil
    } == {"application/pdf"}
