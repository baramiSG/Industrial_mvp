"""Deterministic raw evidence store with write-once semantics."""

from __future__ import annotations

import gzip
import json
import os
import re
from pathlib import Path
from typing import Iterator

from ..config import PROJECT_ROOT
from .contracts import (
    CoverageRecord,
    RawArtifact,
    RawStoreIntegrityError,
    SourceContractRecord,
    UnavailableRecord,
    canonical_dumps,
    sha256_bytes,
)

TEST_DOUBLE_CLASS = "test_double"
TEST_FIXTURE_SOURCE = "TEST-FIXTURE"
_PATH_UNSAFE = re.compile(r"[\\/]|^\.\.")


def deterministic_gzip(payload: bytes) -> bytes:
    """Return deterministic gzip bytes (level 9, mtime=0, empty filename)."""
    return gzip.compress(payload, compresslevel=9, mtime=0)


def _content_extension(content_type: str) -> str:
    lowered = content_type.lower()
    if "json" in lowered:
        return "json"
    if "html" in lowered:
        return "html"
    if "zip" in lowered:
        return "zip"
    if "csv" in lowered:
        return "csv"
    return "bin"


def redact_text(text: str, secrets: tuple[tuple[str, str], ...]) -> str:
    """Replace secret values with redacted placeholders."""
    result = text
    for name, value in secrets:
        if value:
            result = result.replace(value, f"<REDACTED:{name}>")
    return result


class RawStore:
    """Write-once hashed raw artifact store."""

    def __init__(
        self,
        root: Path,
        *,
        max_artifact_bytes: int,
        max_store_bytes: int,
    ) -> None:
        self.root = root.resolve()
        self.max_artifact_bytes = max_artifact_bytes
        self.max_store_bytes = max_store_bytes

    def _validate_segment(self, value: str, label: str) -> None:
        if not value or _PATH_UNSAFE.search(value):
            raise RawStoreIntegrityError(
                f"Invalid {label} for raw store path: {value!r}"
            )

    def _reject_production_test_double(
        self,
        access_classification: str,
        source_id: str,
    ) -> None:
        repo_data = Path(__file__).resolve().parents[3] / "data"
        try:
            self.root.relative_to(repo_data.resolve())
        except ValueError:
            return
        if (
            access_classification == TEST_DOUBLE_CLASS
            or source_id == TEST_FIXTURE_SOURCE
        ):
            raise RawStoreIntegrityError(
                "test_double artifacts are not permitted under repository data/"
            )

    def _reject_forbidden_roots(self) -> None:
        repo_data = Path(__file__).resolve().parents[3] / "data"
        forbidden = (
            repo_data / "snapshots" / "public",
            repo_data / "synthetic",
        )
        for path in forbidden:
            try:
                self.root.relative_to(path.resolve())
            except ValueError:
                continue
            raise RawStoreIntegrityError(
                f"Raw store root may not be under {path}"
            )

    def unit_dir(
        self,
        source_id: str,
        query_hash: str,
        run_id: str,
    ) -> Path:
        """Return the directory for one acquisition unit run."""
        self._reject_forbidden_roots()
        self._validate_segment(source_id, "source_id")
        self._validate_segment(query_hash, "query_hash")
        self._validate_segment(run_id, "run_id")
        return self.root / source_id / query_hash / run_id

    def total_compressed_bytes(self) -> int:
        """Sum compressed byte counts of all payload files."""
        total = 0
        if not self.root.exists():
            return 0
        for path in self.root.rglob("page-*.payload.*.gz"):
            total += path.stat().st_size
        return total

    def _check_budgets(self, compressed_size: int) -> None:
        if compressed_size > self.max_artifact_bytes:
            raise RawStoreIntegrityError(
                "Artifact exceeds max_artifact_bytes_compressed budget"
            )
        projected = self.total_compressed_bytes() + compressed_size
        if projected > self.max_store_bytes:
            raise RawStoreIntegrityError(
                "Store exceeds max_store_bytes_compressed budget"
            )

    def write_page(
        self,
        payload: bytes,
        contract: SourceContractRecord,
    ) -> RawArtifact:
        """Write one page payload and contract JSON write-once."""
        self._reject_production_test_double(
            contract.access_classification,
            contract.source_id,
        )
        compressed = deterministic_gzip(payload)
        self._check_budgets(len(compressed))
        compressed_hash = sha256_bytes(compressed)

        unit = self.unit_dir(
            contract.source_id,
            contract.query_hash,
            contract.run_id,
        )
        unit.mkdir(parents=True, exist_ok=True)
        ext = _content_extension(contract.content_type)
        page_name = f"page-{contract.page_index:04d}"
        payload_path = unit / f"{page_name}.payload.{ext}.gz"
        contract_path = unit / f"{page_name}.contract.json"

        from dataclasses import replace

        try:
            rel_path = payload_path.relative_to(PROJECT_ROOT.resolve())
        except ValueError:
            rel_path = payload_path
        stored_contract = replace(
            contract,
            compressed_sha256=compressed_hash,
            byte_count=len(payload),
            raw_file_path=str(rel_path.as_posix()),
        )

        if payload_path.exists():
            existing = payload_path.read_bytes()
            if existing != compressed:
                raise RawStoreIntegrityError(
                    f"Write-once conflict: {payload_path}"
                )
        else:
            tmp = payload_path.with_suffix(payload_path.suffix + ".tmp")
            tmp.write_bytes(compressed)
            os.replace(tmp, payload_path)

        contract_json = canonical_dumps(stored_contract.to_json())
        if contract_path.exists():
            if contract_path.read_text(encoding="utf-8") != contract_json:
                raise RawStoreIntegrityError(
                    f"Write-once conflict: {contract_path}"
                )
        else:
            tmp = contract_path.with_suffix(".json.tmp")
            tmp.write_text(contract_json, encoding="utf-8")
            os.replace(tmp, contract_path)

        return RawArtifact(contract=stored_contract, path=payload_path)

    def write_coverage(self, record: CoverageRecord) -> Path:
        """Write coverage.json for one planned unit."""
        unit = self.unit_dir(record.source_id, record.query_hash, record.run_id)
        unit.mkdir(parents=True, exist_ok=True)
        path = unit / "coverage.json"
        content = canonical_dumps(record.to_json())
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise RawStoreIntegrityError(
                    f"Write-once conflict: {path}"
                )
        else:
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(content, encoding="utf-8")
            os.replace(tmp, path)
        return path

    def write_unavailable(self, record: UnavailableRecord) -> Path:
        """Write attempt.json for an unavailable or incomplete unit."""
        unit = self.unit_dir(
            record.source_id,
            record.query_hash,
            record.run_id,
        )
        unit.mkdir(parents=True, exist_ok=True)
        path = unit / "attempt.json"
        content = canonical_dumps(record.to_json())
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise RawStoreIntegrityError(
                    f"Write-once conflict: {path}"
                )
        else:
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(content, encoding="utf-8")
            os.replace(tmp, path)
        return path

    def read_payload(self, contract: SourceContractRecord) -> bytes:
        """Read and verify one page payload."""
        unit = self.unit_dir(
            contract.source_id,
            contract.query_hash,
            contract.run_id,
        )
        ext = _content_extension(contract.content_type)
        page_name = f"page-{contract.page_index:04d}"
        path = unit / f"{page_name}.payload.{ext}.gz"
        compressed = path.read_bytes()
        actual_compressed_hash = sha256_bytes(compressed)
        if contract.compressed_sha256:
            if actual_compressed_hash != contract.compressed_sha256:
                raise RawStoreIntegrityError(
                    f"Compressed hash mismatch: {path}"
                )
        payload = gzip.decompress(compressed)
        if sha256_bytes(payload) != contract.sha256:
            raise RawStoreIntegrityError(
                f"Payload hash mismatch: {path}"
            )
        return payload

    def read_coverage(
        self,
        source_id: str,
        query_hash: str,
        run_id: str,
    ) -> CoverageRecord:
        """Load coverage.json for one unit run."""
        path = self.unit_dir(source_id, query_hash, run_id) / "coverage.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return CoverageRecord.from_json(payload)

    def pages_for(
        self,
        source_id: str,
        query_hash: str,
        run_id: str,
    ) -> list[SourceContractRecord]:
        """Return page contracts sorted by page_index."""
        unit = self.unit_dir(source_id, query_hash, run_id)
        contracts: list[SourceContractRecord] = []
        for path in sorted(unit.glob("page-*.contract.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            contracts.append(SourceContractRecord.from_json(payload))
        return sorted(contracts, key=lambda item: item.page_index)

    def _iter_unit_dirs(self) -> Iterator[Path]:
        if not self.root.exists():
            return
        for source_dir in sorted(self.root.iterdir()):
            if not source_dir.is_dir():
                continue
            for hash_dir in sorted(source_dir.iterdir()):
                if not hash_dir.is_dir():
                    continue
                for run_dir in sorted(hash_dir.iterdir()):
                    if run_dir.is_dir():
                        yield run_dir

    def iter_contracts(
        self,
        *,
        source_id: str | None = None,
        stage: str | None = None,
    ) -> list[SourceContractRecord]:
        """Iterate all page contracts, optionally filtered."""
        records: list[SourceContractRecord] = []
        for unit in self._iter_unit_dirs():
            for path in sorted(unit.glob("page-*.contract.json")):
                payload = json.loads(path.read_text(encoding="utf-8"))
                record = SourceContractRecord.from_json(payload)
                if source_id and record.source_id != source_id:
                    continue
                if stage and record.query_contract.stage.value != stage:
                    continue
                records.append(record)
        return sorted(records, key=lambda r: (r.source_id, r.query_hash, r.run_id, r.page_index))

    def iter_coverage(
        self,
        *,
        source_id: str | None = None,
        stage: str | None = None,
    ) -> list[CoverageRecord]:
        """Iterate coverage records sorted by unit_key and run_id."""
        records: list[CoverageRecord] = []
        for unit in self._iter_unit_dirs():
            path = unit / "coverage.json"
            if not path.exists():
                continue
            record = CoverageRecord.from_json(
                json.loads(path.read_text(encoding="utf-8"))
            )
            if source_id and record.source_id != source_id:
                continue
            if stage and record.stage.value != stage:
                continue
            records.append(record)
        return sorted(records, key=lambda r: (r.unit_key, r.run_id))

    def iter_unavailable(self) -> list[UnavailableRecord]:
        """Iterate all attempt.json records."""
        records: list[UnavailableRecord] = []
        for unit in self._iter_unit_dirs():
            path = unit / "attempt.json"
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            qc_raw = payload["query_contract"]
            from .contracts import QueryContract, Stage, ProductScope

            parameters = tuple(
                sorted(
                    (item["key"], item["value"])
                    for item in qc_raw.get("parameters", [])
                )
            )
            contract = QueryContract(
                source_id=qc_raw["source_id"],
                stage=Stage(qc_raw["stage"]),
                reporter=qc_raw["reporter"],
                partner=qc_raw["partner"],
                flow=qc_raw["flow"],
                product_scope=ProductScope(qc_raw["product_scope"]),
                product_codes=tuple(qc_raw["product_codes"]),
                nomenclature=qc_raw["nomenclature"],
                periods=tuple(qc_raw["periods"]),
                parameters=parameters,
            )
            coverage_raw = payload.get("coverage")
            coverage = (
                CoverageRecord.from_json(coverage_raw)
                if isinstance(coverage_raw, dict)
                else None
            )
            observed_raw = payload.get("observed_response")
            from .contracts import ObservedResponse, UnavailableReason

            observed = (
                ObservedResponse.from_json(observed_raw)
                if isinstance(observed_raw, dict)
                else None
            )
            records.append(
                UnavailableRecord(
                    source_id=str(payload["source_id"]),
                    query_contract=contract,
                    query_hash=str(payload["query_hash"]),
                    run_id=str(payload["run_id"]),
                    attempted_at=str(payload["attempted_at"]),
                    reason=UnavailableReason(payload["reason"]),
                    observed_response=observed,
                    endpoint_or_document=str(payload["endpoint_or_document"]),
                    credential_env_var=payload.get("credential_env_var"),
                    credential_present=bool(payload["credential_present"]),
                    coverage=coverage,
                )
            )
        return records

    def latest_runs(
        self,
        *,
        source_id: str,
        stage: str,
    ) -> dict[tuple[str, ...], tuple[CoverageRecord, tuple[str, ...]]]:
        """Select latest run_id per unit_key for one source and stage."""
        by_key: dict[tuple[str, ...], list[CoverageRecord]] = {}
        for record in self.iter_coverage(source_id=source_id, stage=stage):
            by_key.setdefault(record.unit_key, []).append(record)

        result: dict[tuple[str, ...], tuple[CoverageRecord, tuple[str, ...]]] = {}
        for key, records in by_key.items():
            sorted_runs = sorted(records, key=lambda r: r.run_id)
            selected = sorted_runs[-1]
            superseded = tuple(r.run_id for r in sorted_runs[:-1])
            result[key] = (selected, superseded)
        return result
