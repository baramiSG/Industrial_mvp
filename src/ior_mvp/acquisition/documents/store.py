"""DocumentRecord 1.0.0 store, builder, validator and reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from ...config import PROJECT_ROOT
from ..connectors.base import ConnectorRegistry
from ..contracts import (
    AcquisitionConfigurationError,
    CoverageRecord,
    RawStoreIntegrityError,
    SELECTION_RULE,
    SnapshotWriteConflict,
    SourceContractRecord,
    Stage,
    canonical_dumps,
    sha256_bytes,
    source_tag,
)
from ..harmonise import PIPELINE_VERSION
from ..passports import build_acquired_passport
from ..raw_store import RawStore, TEST_FIXTURE_SOURCE, _PATH_UNSAFE
from ..snapshots import ReconstructionResult
from .lists import LIST_ID_PATTERN, DocumentList, list_sha256
from .textlayer import SEGMENTATION_METHOD, derive_text_layer, page_text_sha256

DOCUMENT_SCHEMA_VERSION = "1.0.0"
DOCUMENT_ID_SCHEME = "DOCUMENT_ID_V1"
DOCUMENT_CONFIG_VERSION = "1.2.0"

_RECORD_KEYS = frozenset({
    "schema_version", "document_id", "document_id_scheme", "source_id", "source_boundary",
    "kind", "as_of_date", "list_ref", "declared", "raw_artifact_ref", "coverage",
    "text_layer", "segmentation", "page_count", "line_count", "pages", "transformation_record",
    "quality_summary", "evidence",
})
_NESTED_RECORD_KEYS = {
    "list_ref": frozenset({"path", "sha256", "list_id", "entry_id"}),
    "declared": frozenset({
        "publisher_text", "publisher_kind", "document_kind", "languages",
        "expected_content_type", "evidence_class_target", "supports", "title_text",
        "document_date_text", "source_reference_text",
    }),
    "raw_artifact_ref": frozenset({
        "source_id", "stage", "unit_key", "query_hash", "run_id", "artifact", "path",
        "sha256", "compressed_sha256", "byte_count", "content_type", "http_status",
        "retrieved_at", "endpoint_or_document",
    }),
    "coverage": frozenset({
        "selection_rule", "unit_key", "query_hash", "selected_run_id",
        "superseded_run_ids", "status", "completeness_basis",
    }),
    "text_layer": frozenset({
        "status", "reason", "detail", "detail_error_type", "method_id",
        "method_version", "extraction_mode", "dependency",
    }),
    "segmentation": frozenset({"method_id", "version"}),
    "transformation_record": frozenset({
        "formula", "parameters", "exclusions", "pipeline_version", "config_version",
    }),
}
_TRANSFORMATION_PARAMETER_KEYS = frozenset({
    "source_id", "text_layer_method_id", "text_layer_method_version",
    "segmentation_method_id", "segmentation_version", "dependency",
})
_PAGE_KEYS = frozenset({"page_index", "line_count", "text_sha256", "lines"})


@dataclass(frozen=True)
class DocumentBuildReport:
    built: tuple[str, ...]
    already_stored: tuple[str, ...]
    unavailable: tuple[str, ...]
    skipped_no_entry: tuple[str, ...]


def document_id(source_id: str, query_hash: str, raw_sha256: str) -> str:
    return f"DOC-{source_tag(source_id)}-{query_hash[:12]}-{raw_sha256[:12]}"


def validate_list_id(list_id: str) -> None:
    if not isinstance(list_id, str) or LIST_ID_PATTERN.fullmatch(list_id) is None:
        raise AcquisitionConfigurationError(f"Invalid document list_id: {list_id!r}")


class DocumentStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._reject_forbidden_roots()

    def _reject_forbidden_roots(self) -> None:
        repo_data = PROJECT_ROOT / "data"
        forbidden = (repo_data / "snapshots" / "public", repo_data / "synthetic")
        for path in forbidden:
            try:
                self.root.resolve().relative_to(path.resolve())
            except ValueError:
                continue
            raise RawStoreIntegrityError(f"Document store root may not be under {path}")

    def list_path(self, source_id: str, list_id: str) -> Path:
        validate_list_id(list_id)
        self._validate_segment(source_id, "source_id")
        self._validate_segment(list_id, "list_id")
        return self.root / source_id / "lists" / f"{list_id}.json"

    def record_path(self, source_id: str, document_id_value: str) -> Path:
        self._validate_segment(source_id, "source_id")
        self._validate_segment(document_id_value, "document_id")
        return self.root / source_id / "records" / f"{document_id_value}.json"

    @staticmethod
    def _validate_segment(value: str, label: str) -> None:
        if not isinstance(value, str) or not value or _PATH_UNSAFE.search(value):
            raise RawStoreIntegrityError(
                f"Invalid {label} for document store path: {value!r}"
            )

    def write_record(
        self, record: dict[str, Any], *, allow_test_double: bool = False
    ) -> Path:
        source_id = str(record["source_id"])
        doc_id = str(record["document_id"])
        if not allow_test_double:
            repo_data = PROJECT_ROOT / "data"
            try:
                self.root.resolve().relative_to(repo_data.resolve())
            except ValueError:
                pass
            else:
                if source_id == TEST_FIXTURE_SOURCE or record.get("synthetic_flag"):
                    raise RawStoreIntegrityError(
                        "test doubles are not permitted under repository data/documents"
                    )
        path = self.record_path(source_id, doc_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = canonical_dumps(record)
        if path.exists():
            if path.read_text(encoding="utf-8") == payload:
                return path
            raise SnapshotWriteConflict(f"Document record already exists: {path}")
        path.write_text(payload, encoding="utf-8")
        return path

    def iter_records(self, source_id: str | None = None) -> Iterator[tuple[Path, dict[str, Any]]]:
        if source_id:
            records_dir = self.root / source_id / "records"
            if not records_dir.exists():
                return iter(())
            paths = sorted(records_dir.glob("*.json"))
        else:
            paths = sorted(self.root.rglob("records/*.json"))
        for path in paths:
            import json

            yield path, json.loads(path.read_text(encoding="utf-8"))


def build_document_record(
    raw_store: RawStore,
    config: dict[str, Any],
    *,
    source_id: str,
    page: SourceContractRecord,
    coverage: CoverageRecord,
    superseded_run_ids: tuple[str, ...],
    document_list: DocumentList,
    list_path: Path,
) -> dict[str, Any]:
    payload = raw_store.read_payload(page)
    raw_sha = page.sha256
    doc_id = document_id(source_id, page.query_hash, raw_sha)
    entry = document_list.entry_for_url(dict(page.query_contract.parameters)["document_url"])
    if entry is None:
        raise ValueError("missing list entry for stored document")
    derived = derive_text_layer(payload, page.content_type)
    pages_payload: list[dict[str, Any]] = []
    line_count = 0
    for index, lines in enumerate(derived.pages, start=1):
        line_count += len(lines)
        pages_payload.append({
            "page_index": index,
            "line_count": len(lines),
            "text_sha256": page_text_sha256(lines),
            "lines": list(lines),
        })
    page_count = (
        len(pages_payload)
        if derived.status == "AVAILABLE" or derived.detail == "NO_TEXT_LAYER"
        else None
    )
    quality = "PASS" if derived.status == "AVAILABLE" else "RAW_ONLY"
    dependency = None
    if derived.dependency:
        import pypdf

        dependency = {"name": "pypdf", "version": pypdf.__version__}
    transformation = {
        "formula": "derive_document_text_layer",
        "parameters": {
            "source_id": source_id,
            "text_layer_method_id": derived.method_id,
            "text_layer_method_version": derived.method_version,
            "segmentation_method_id": SEGMENTATION_METHOD[0],
            "segmentation_version": SEGMENTATION_METHOD[1],
            "dependency": dependency,
        },
        "exclusions": [],
        "pipeline_version": PIPELINE_VERSION,
        "config_version": DOCUMENT_CONFIG_VERSION,
    }
    source_cfg = config["sources"][source_id]
    passport = build_acquired_passport(
        [page],
        coverage,
        source_config=source_cfg,
        supports=list(entry.supports),
        transformation_record=transformation,
        observation_context={
            "stage": "DOCUMENT",
            "document_id": doc_id,
            "document_kind": entry.document_kind,
            "languages": list(entry.languages),
            "publisher_text": entry.publisher_text,
        },
        measurement={
            "page_count": page_count,
            "line_count": line_count,
            "byte_count": page.byte_count,
        },
        contradiction_record=None,
    )
    rel_raw = page.raw_file_path or str(
        raw_store.unit_dir(source_id, page.query_hash, page.run_id)
        / f"page-{page.page_index:04d}.payload.*.gz"
    )
    return {
        "schema_version": DOCUMENT_SCHEMA_VERSION,
        "document_id": doc_id,
        "document_id_scheme": DOCUMENT_ID_SCHEME,
        "source_id": source_id,
        "source_boundary": "public",
        "kind": "document",
        "as_of_date": page.retrieved_at[:10],
        "list_ref": {
            "path": (
                list_path.resolve().relative_to((PROJECT_ROOT / "data").resolve()).as_posix()
                if list_path.resolve().is_relative_to((PROJECT_ROOT / "data").resolve())
                else list_path.resolve().as_posix()
            ),
            "sha256": list_sha256(list_path),
            "list_id": document_list.list_id,
            "entry_id": entry.entry_id,
        },
        "declared": {
            "publisher_text": entry.publisher_text,
            "publisher_kind": entry.publisher_kind,
            "document_kind": entry.document_kind,
            "languages": list(entry.languages),
            "expected_content_type": entry.expected_content_type,
            "evidence_class_target": entry.evidence_class_target,
            "supports": list(entry.supports),
            "title_text": entry.title_text,
            "document_date_text": entry.document_date_text,
            "source_reference_text": entry.source_reference_text,
        },
        "raw_artifact_ref": {
            "source_id": source_id,
            "stage": "DOCUMENT",
            "unit_key": list(coverage.unit_key),
            "query_hash": page.query_hash,
            "run_id": page.run_id,
            "artifact": f"page-{page.page_index:04d}",
            "path": page.raw_file_path,
            "sha256": page.sha256,
            "compressed_sha256": page.compressed_sha256,
            "byte_count": page.byte_count,
            "content_type": page.content_type,
            "http_status": page.http_status,
            "retrieved_at": page.retrieved_at,
            "endpoint_or_document": page.endpoint_or_document,
        },
        "coverage": {
            "selection_rule": SELECTION_RULE,
            "unit_key": list(coverage.unit_key),
            "query_hash": coverage.query_hash,
            "selected_run_id": coverage.run_id,
            "superseded_run_ids": list(superseded_run_ids),
            "status": coverage.status,
            "completeness_basis": coverage.completeness_basis.value,
        },
        "text_layer": {
            "status": "COMPLETE" if derived.status == "AVAILABLE" else "UNAVAILABLE",
            "reason": derived.reason,
            "detail": derived.detail,
            "detail_error_type": derived.detail_error_type,
            "method_id": derived.method_id,
            "method_version": derived.method_version,
            "extraction_mode": derived.extraction_mode,
            "dependency": dependency,
        },
        "segmentation": {
            "method_id": SEGMENTATION_METHOD[0],
            "version": SEGMENTATION_METHOD[1],
        },
        "page_count": page_count,
        "line_count": line_count,
        "pages": pages_payload,
        "transformation_record": transformation,
        "quality_summary": quality,
        "evidence": [passport],
    }


def validate_document_record(
    record: dict[str, Any], *, allow_test_double: bool = False
) -> None:
    from ..passports import ACQUIRED_SUPPORT_CODES
    from .lists import SOURCE_ALLOWED_SUPPORTS

    if set(record) != _RECORD_KEYS:
        raise ValueError(f"unexpected record keys: {set(record) - _RECORD_KEYS}")
    for field, expected_keys in _NESTED_RECORD_KEYS.items():
        value = record[field]
        if not isinstance(value, dict) or set(value) != expected_keys:
            raise ValueError(f"{field} keys mismatch")
    parameters = record["transformation_record"]["parameters"]
    if not isinstance(parameters, dict) or set(parameters) != _TRANSFORMATION_PARAMETER_KEYS:
        raise ValueError("transformation_record.parameters keys mismatch")
    dependency = record["text_layer"]["dependency"]
    if dependency is not None and (
        not isinstance(dependency, dict) or set(dependency) != {"name", "version"}
    ):
        raise ValueError("text_layer.dependency keys mismatch")
    if not isinstance(record["pages"], list) or any(
        not isinstance(page, dict) or set(page) != _PAGE_KEYS
        for page in record["pages"]
    ):
        raise ValueError("pages keys mismatch")
    if record["schema_version"] != DOCUMENT_SCHEMA_VERSION:
        raise ValueError("schema_version mismatch")
    if record["document_id_scheme"] != DOCUMENT_ID_SCHEME:
        raise ValueError("document_id_scheme mismatch")
    if record["synthetic_flag"] if "synthetic_flag" in record else False:
        raise ValueError("synthetic_flag not permitted")
    if not allow_test_double and record["source_id"] == TEST_FIXTURE_SOURCE:
        raise ValueError("test fixture source not permitted under repository data")
    if record["kind"] != "document":
        raise ValueError("kind mismatch")
    if record["source_boundary"] != "public":
        raise ValueError("source_boundary must be public")
    expected_id = document_id(
        record["source_id"],
        record["raw_artifact_ref"]["query_hash"],
        record["raw_artifact_ref"]["sha256"],
    )
    if record["document_id"] != expected_id:
        raise ValueError("document_id mismatch")
    allowed = SOURCE_ALLOWED_SUPPORTS.get(record["source_id"], frozenset())
    for code in record["declared"]["supports"]:
        if code not in allowed or code not in ACQUIRED_SUPPORT_CODES:
            raise ValueError(f"unsupported support code: {code}")
    line_count = 0
    for expected_index, page in enumerate(record["pages"], start=1):
        if page["page_index"] != expected_index:
            raise ValueError("page_index must match physical page order")
        if page["line_count"] != len(page["lines"]):
            raise ValueError("page line_count mismatch")
        if page["text_sha256"] != page_text_sha256(page["lines"]):
            raise ValueError("text_sha256 mismatch")
        line_count += len(page["lines"])
    if record["line_count"] != line_count:
        raise ValueError("line_count mismatch")
    if record["page_count"] is not None and record["page_count"] != len(record["pages"]):
        raise ValueError("page_count mismatch")
    if record["text_layer"]["status"] == "COMPLETE":
        if record["quality_summary"] != "PASS":
            raise ValueError("quality_summary inconsistent with text_layer")
        if not any(line.strip() for page in record["pages"] for line in page["lines"]):
            raise ValueError("COMPLETE text layer has no non-whitespace line")
    elif record["text_layer"]["status"] == "UNAVAILABLE":
        if record["quality_summary"] != "RAW_ONLY":
            raise ValueError("quality_summary inconsistent with text_layer")
        if any(line.strip() for page in record["pages"] for line in page["lines"]):
            raise ValueError("UNAVAILABLE text layer has non-whitespace content")
    else:
        raise ValueError("unsupported text_layer status")


def build_document_records(
    raw_store: RawStore,
    config: Mapping[str, Any],
    registry: ConnectorRegistry,
    doc_store: DocumentStore,
    *,
    source_id: str,
    list_id: str,
) -> DocumentBuildReport:
    from .lists import load_document_list

    list_path = doc_store.list_path(source_id, list_id)
    source_cfg = config["sources"][source_id]
    document_list = load_document_list(
        list_path,
        source_id=source_id,
        default_evidence_class=source_cfg["default_evidence_class"],
    )
    built: list[str] = []
    already: list[str] = []
    unavailable: list[str] = []
    skipped: list[str] = []
    selected = raw_store.latest_runs(source_id=source_id, stage=Stage.DOCUMENT.value)
    for _, (coverage, superseded_run_ids) in sorted(selected.items()):
        import json

        if coverage.status != "COMPLETE":
            unavailable.append(coverage.query_hash)
            continue
        run_dir = raw_store.unit_dir(source_id, coverage.query_hash, coverage.run_id)
        contracts = sorted(run_dir.glob("page-*.contract.json"))
        if not contracts:
            unavailable.append(coverage.query_hash)
            continue
        contract = SourceContractRecord.from_json(
            json.loads(contracts[0].read_text(encoding="utf-8"))
        )
        url = dict(contract.query_contract.parameters).get("document_url", "")
        if document_list.entry_for_url(url) is None:
            skipped.append(url)
            continue
        doc_id = document_id(source_id, contract.query_hash, contract.sha256)
        record_path = doc_store.record_path(source_id, doc_id)
        if record_path.exists():
            already.append(doc_id)
            continue
        record = build_document_record(
            raw_store,
            dict(config),
            source_id=source_id,
            page=contract,
            coverage=coverage,
            superseded_run_ids=superseded_run_ids,
            document_list=document_list,
            list_path=list_path,
        )
        doc_store.write_record(record)
        built.append(doc_id)
    return DocumentBuildReport(
        built=tuple(built),
        already_stored=tuple(already),
        unavailable=tuple(unavailable),
        skipped_no_entry=tuple(skipped),
    )


def reconstruct_document(
    record_path: Path,
    raw_store: RawStore,
    config: Mapping[str, Any],
    doc_store: DocumentStore,
) -> ReconstructionResult:
    import json

    record = json.loads(record_path.read_text(encoding="utf-8"))
    doc_id = record["document_id"]
    list_ref = record["list_ref"]
    list_path = (doc_store.root / record["source_id"] / "lists" / f"{list_ref['list_id']}.json").resolve()
    if list_sha256(list_path) != list_ref["sha256"]:
        return ReconstructionResult(
            False, list_ref["sha256"], list_sha256(list_path), 0, doc_id,
            {"reason": "LIST_HASH_MISMATCH"},
        )
    raw_ref = record["raw_artifact_ref"]
    contract_path = raw_store.root / raw_ref["source_id"] / raw_ref["query_hash"] / raw_ref["run_id"] / f"{raw_ref['artifact']}.contract.json"
    contract = SourceContractRecord.from_json(json.loads(contract_path.read_text(encoding="utf-8")))
    payload = raw_store.read_payload(contract)
    if sha256_bytes(payload) != raw_ref["sha256"]:
        return ReconstructionResult(
            False, raw_ref["sha256"], sha256_bytes(payload), 0, doc_id,
            {"reason": "RAW_HASH_MISMATCH"},
        )
    derived = derive_text_layer(payload, contract.content_type)
    evidence_coverage = record["evidence"][0]["coverage"]
    rebuilt = build_document_record(
        raw_store,
        dict(config),
        source_id=record["source_id"],
        page=contract,
        coverage=CoverageRecord.from_json(evidence_coverage),
        superseded_run_ids=tuple(record["coverage"].get("superseded_run_ids", ())),
        document_list=__import__(
            "ior_mvp.acquisition.documents.lists", fromlist=["load_document_list"]
        ).load_document_list(
            list_path,
            source_id=record["source_id"],
            default_evidence_class=config["sources"][record["source_id"]]["default_evidence_class"],
        ),
        list_path=list_path,
    )
    if canonical_dumps(rebuilt) != canonical_dumps(record):
        return ReconstructionResult(
            False, sha256_bytes(canonical_dumps(record).encode()), sha256_bytes(canonical_dumps(rebuilt).encode()),
            1, doc_id, {"reason": "BYTE_MISMATCH"},
        )
    return ReconstructionResult(True, record["raw_artifact_ref"]["sha256"], record["raw_artifact_ref"]["sha256"], 1, doc_id, {})
