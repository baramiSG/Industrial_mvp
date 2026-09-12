"""DocumentList 1.0.0 — explicit operator document lists."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from ..connectors.base import _personal_field
from ..contracts import AcquisitionConfigurationError
from ..raw_store import TEST_FIXTURE_SOURCE
from .textlayer import DOCUMENT_ENVELOPE_TYPES

DOCUMENT_KINDS = frozenset({
    "annual_report",
    "environmental_product_declaration",
    "product_sheet",
    "catalogue_page",
    "issuer_disclosure",
    "financial_statement",
    "tender_document",
    "tender_page",
    "technical_regulation",
    "standard_summary",
    "other_public_document",
})

PUBLISHER_KINDS = frozenset({
    "producer",
    "exchange",
    "procurement_authority",
    "standards_authority",
})

LANGUAGES = frozenset({"ar", "en"})

LIST_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,79}$")
ENTRY_ID_PATTERN = re.compile(r"^E-[0-9]{3}$")

SOURCE_ALLOWED_SUPPORTS: Mapping[str, frozenset[str]] = {
    "producer_unicoil": frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_PROCESS_FAMILY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    "producer_sabic": frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_PROCESS_FAMILY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    "producer_advanced_petrochemical": frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_PROCESS_FAMILY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    "producer_tasnee": frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_PROCESS_FAMILY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    "tadawul_disclosures": frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
    }),
    "etimad_tenders": frozenset({
        "TARGET_SPECIFICATION_DEMAND",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    "saso_documents": frozenset({
        "HARD_REGULATORY_PROCESS_GATES",
        "TARGET_SPECIFICATION_DEMAND",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
    TEST_FIXTURE_SOURCE: frozenset({
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_PROCESS_FAMILY",
        "DOMESTIC_PRODUCT_PORTFOLIO",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
        "BILINGUAL_SPECIFICATION_EXTRACTION",
    }),
}

_LIST_TOP_KEYS = frozenset({
    "schema_version",
    "list_id",
    "source_id",
    "recorded_on",
    "recorded_by_seat",
    "consultation_summary_text",
    "documentation_urls_observed",
    "entries",
})

_ENTRY_KEYS = frozenset({
    "entry_id",
    "document_url",
    "publisher_text",
    "publisher_kind",
    "document_kind",
    "languages",
    "expected_content_type",
    "evidence_class_target",
    "supports",
    "title_text",
    "document_date_text",
    "source_reference_text",
})


@dataclass(frozen=True)
class DocumentEntry:
    entry_id: str
    document_url: str
    publisher_text: str
    publisher_kind: str
    document_kind: str
    languages: tuple[str, ...]
    expected_content_type: str
    evidence_class_target: str
    supports: tuple[str, ...]
    title_text: str
    document_date_text: str
    source_reference_text: str


@dataclass(frozen=True)
class DocumentList:
    schema_version: str
    list_id: str
    source_id: str
    recorded_on: str
    recorded_by_seat: str
    consultation_summary_text: str
    documentation_urls_observed: tuple[str, ...]
    entries: tuple[DocumentEntry, ...]

    def entry_for_url(self, url: str) -> DocumentEntry | None:
        for entry in self.entries:
            if entry.document_url == url:
                return entry
        return None


def _entry_from_dict(payload: dict[str, Any]) -> DocumentEntry:
    return DocumentEntry(
        entry_id=str(payload["entry_id"]),
        document_url=str(payload["document_url"]),
        publisher_text=str(payload["publisher_text"]),
        publisher_kind=str(payload["publisher_kind"]),
        document_kind=str(payload["document_kind"]),
        languages=tuple(payload["languages"]),
        expected_content_type=str(payload["expected_content_type"]),
        evidence_class_target=str(payload["evidence_class_target"]),
        supports=tuple(payload["supports"]),
        title_text=str(payload["title_text"]),
        document_date_text=str(payload["document_date_text"]),
        source_reference_text=str(payload["source_reference_text"]),
    )


def _iso_date(value: Any) -> bool:
    if not isinstance(value, str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ) is None:
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_document_list(
    payload: dict[str, Any],
    *,
    source_id: str,
    default_evidence_class: str,
) -> None:
    if set(payload) != _LIST_TOP_KEYS:
        unknown = set(payload) - _LIST_TOP_KEYS
        raise AcquisitionConfigurationError(f"DocumentList unknown keys: {sorted(unknown)}")
    if payload["schema_version"] != "1.0.0":
        raise AcquisitionConfigurationError("DocumentList schema_version must be 1.0.0")
    if payload["source_id"] != source_id:
        raise AcquisitionConfigurationError("DocumentList source_id mismatch")
    list_id = payload["list_id"]
    if not isinstance(list_id, str) or LIST_ID_PATTERN.fullmatch(list_id) is None:
        raise AcquisitionConfigurationError("DocumentList list_id invalid")
    if not _iso_date(payload["recorded_on"]):
        raise AcquisitionConfigurationError("DocumentList recorded_on must be an ISO date")
    if not isinstance(payload["recorded_by_seat"], str) or not payload["recorded_by_seat"]:
        raise AcquisitionConfigurationError("DocumentList recorded_by_seat required")
    summary = payload["consultation_summary_text"]
    if not isinstance(summary, str) or not summary.strip():
        raise AcquisitionConfigurationError("DocumentList consultation_summary_text required")
    docs = payload["documentation_urls_observed"]
    if not isinstance(docs, list) or any(
        not isinstance(url, str) or not url.startswith(("http://", "https://"))
        for url in docs
    ):
        raise AcquisitionConfigurationError("documentation_urls_observed invalid")
    entries_raw = payload["entries"]
    if not isinstance(entries_raw, list):
        raise AcquisitionConfigurationError("DocumentList entries must be a list")
    if not entries_raw and not summary.strip():
        raise AcquisitionConfigurationError("empty entries require consultation_summary_text")
    entry_ids: set[str] = set()
    urls: set[str] = set()
    allowed = SOURCE_ALLOWED_SUPPORTS.get(source_id, frozenset())
    for entry in entries_raw:
        if not isinstance(entry, dict) or set(entry) != _ENTRY_KEYS:
            raise AcquisitionConfigurationError("DocumentList entry keys invalid")
        for key in entry:
            if _personal_field(key):
                raise AcquisitionConfigurationError(f"personal-data key in schema: {key}")
        entry_id = entry["entry_id"]
        if ENTRY_ID_PATTERN.fullmatch(entry_id) is None or entry_id in entry_ids:
            raise AcquisitionConfigurationError("entry_id invalid or duplicate")
        entry_ids.add(entry_id)
        url = entry["document_url"]
        if not isinstance(url, str) or not url.startswith(("http://", "https://")) or url in urls:
            raise AcquisitionConfigurationError("document_url invalid or duplicate")
        urls.add(url)
        if not entry["publisher_text"]:
            raise AcquisitionConfigurationError("publisher_text required")
        if entry["publisher_kind"] not in PUBLISHER_KINDS:
            raise AcquisitionConfigurationError("publisher_kind invalid")
        if entry["document_kind"] not in DOCUMENT_KINDS:
            raise AcquisitionConfigurationError("document_kind invalid")
        langs = entry["languages"]
        if not isinstance(langs, list) or not langs or not set(langs) <= LANGUAGES:
            raise AcquisitionConfigurationError("languages invalid")
        ctype = entry["expected_content_type"]
        if ctype not in DOCUMENT_ENVELOPE_TYPES:
            raise AcquisitionConfigurationError("expected_content_type invalid")
        if entry["evidence_class_target"] != default_evidence_class:
            raise AcquisitionConfigurationError("evidence_class_target must equal source default")
        supports = entry["supports"]
        if not isinstance(supports, list) or not supports:
            raise AcquisitionConfigurationError("supports required")
        if not set(supports) <= allowed:
            raise AcquisitionConfigurationError("supports not allowed for source")
        for text_key in ("title_text", "document_date_text", "source_reference_text"):
            value = entry[text_key]
            if not isinstance(value, str) or not value:
                raise AcquisitionConfigurationError(f"{text_key} required")


def load_document_list(
    path: Path,
    *,
    source_id: str,
    default_evidence_class: str,
) -> DocumentList:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_document_list(payload, source_id=source_id, default_evidence_class=default_evidence_class)
    entries = tuple(
        _entry_from_dict(entry)
        for entry in sorted(payload["entries"], key=lambda item: item["entry_id"])
    )
    return DocumentList(
        schema_version=str(payload["schema_version"]),
        list_id=str(payload["list_id"]),
        source_id=str(payload["source_id"]),
        recorded_on=str(payload["recorded_on"]),
        recorded_by_seat=str(payload["recorded_by_seat"]),
        consultation_summary_text=str(payload["consultation_summary_text"]),
        documentation_urls_observed=tuple(payload["documentation_urls_observed"]),
        entries=entries,
    )


def list_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
