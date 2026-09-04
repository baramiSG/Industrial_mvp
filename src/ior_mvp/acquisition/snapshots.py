"""Deterministic snapshot builders and validators."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from ..config import PROJECT_ROOT
from ..public_snapshot import _reject_authored_outcomes
from .connectors.base import ConnectorRegistry
from .contracts import (
    AcquisitionUnavailable,
    PRODUCT_SCOPE_ALL,
    QueryContract,
    RawStoreIntegrityError,
    SELECTION_RULE,
    SnapshotWriteConflict,
    SourceContractRecord,
    Stage,
    UNAVAILABLE,
    UnavailableReason,
    canonical_dumps,
    sha256_bytes,
    source_tag,
)
from .coverage import (
    aggregate_partner_coverage,
    aggregate_snapshot_coverage,
    coverage_matches,
    evaluate_coverage,
    select_latest_units,
)
from .harmonise import PIPELINE_VERSION, transformation_record
from .passports import assert_passport_complete, build_acquired_passport
from .raw_store import RawStore, TEST_DOUBLE_CLASS, TEST_FIXTURE_SOURCE

UNIVERSE_SCHEMA_VERSION = "1.0.0"
TARIFF_SCHEMA_VERSION = "1.0.0"
PARTNERS_SCHEMA_VERSION = "1.0.0"

SNAPSHOT_ROOTS = {
    "universe": "data/snapshots/universe",
    "tariff": "data/snapshots/tariff",
    "partners": "data/snapshots/partners",
}

KIND_STAGE = {
    "universe": Stage.UNIVERSE,
    "tariff": Stage.TARIFF,
    "partners": Stage.PARTNERS,
}


@dataclass(frozen=True)
class ReconstructionResult:
    match: bool
    expected_sha256: str
    actual_sha256: str
    artifacts_verified: int
    snapshot_id: str
    detail: dict[str, Any]


def snapshot_id(
    kind: str,
    *,
    source_id: str,
    nomenclature: str,
    as_of_date: date,
) -> str:
    tag = source_tag(source_id)
    prefix = kind.upper()
    if kind == "universe":
        return f"UNIVERSE-SAU-{tag}-{nomenclature}-{as_of_date.isoformat()}"
    if kind == "tariff":
        return f"TARIFF-SAU-{tag}-{as_of_date.isoformat()}"
    if kind == "partners":
        return f"PARTNERS-SAU-{tag}-{as_of_date.isoformat()}"
    raise ValueError(f"Unknown snapshot kind: {kind}")


def _forbidden_keys_check(record: dict[str, Any]) -> None:
    _reject_authored_outcomes(record)


def _reject_test_double(record: dict[str, Any], *, allow_test_double: bool) -> None:
    if allow_test_double:
        return
    if record.get("source_id") == TEST_FIXTURE_SOURCE:
        raise ValueError("TEST-FIXTURE source_id rejected")
    for ref in record.get("raw_artifact_refs", []):
        if ref.get("access_classification") == TEST_DOUBLE_CLASS:
            raise ValueError("test_double access_classification rejected")


def validate_universe_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
) -> None:
    _validate_common(record, kind="universe", allow_test_double=allow_test_double)
    if record.get("product_scope") != "ALL_HS6":
        raise ValueError("universe product_scope must be ALL_HS6")
    coverage = record["coverage"]
    if coverage.get("status") != "COMPLETE":
        raise ValueError("universe coverage must be COMPLETE")
    for unit in coverage.get("units", []):
        if unit.get("status") != "COMPLETE":
            raise ValueError("universe unit must be COMPLETE")
        if unit.get("completeness_basis") == "UNAVAILABLE":
            raise ValueError("universe unit basis must not be UNAVAILABLE")


def validate_tariff_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
) -> None:
    _validate_common(record, kind="tariff", allow_test_double=allow_test_double)
    coverage = record["coverage"]
    if coverage.get("status") != "COMPLETE":
        raise ValueError("tariff coverage must be COMPLETE")
    if len(coverage.get("units", [])) != 1:
        raise ValueError("tariff snapshot requires exactly one unit")


def validate_partner_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
) -> None:
    _validate_common(record, kind="partners", allow_test_double=allow_test_double)
    coverage = record["coverage"]
    if coverage.get("units_complete", 0) < 1:
        raise ValueError("partners requires units_complete >= 1")
    exclusions = record.get("transformation_record", {}).get("exclusions", [])
    if coverage.get("units_excluded") != exclusions:
        raise ValueError("partners exclusions mismatch")


def _validate_common(
    record: dict[str, Any],
    *,
    kind: str,
    allow_test_double: bool,
) -> None:
    _forbidden_keys_check(record)
    _reject_test_double(record, allow_test_double=allow_test_double)
    required = (
        "schema_version",
        "snapshot_id",
        "source_id",
        "as_of_date",
        "source_boundary",
        "kind",
        "nomenclature",
        "coverage",
        "raw_artifact_refs",
        "transformation_record",
        "quality_summary",
        "evidence",
    )
    for key in required:
        if key not in record:
            raise ValueError(f"Missing key: {key}")
    if record["source_boundary"] != "public":
        raise ValueError("source_boundary must be public")
    if record["kind"] != kind:
        raise ValueError(f"kind mismatch: {kind}")
    if record["coverage"]["selection_rule"] != SELECTION_RULE:
        raise ValueError("invalid selection_rule")
    if record["coverage"]["source_id"] != record["source_id"]:
        raise ValueError("coverage source_id mismatch")
    expected_id = snapshot_id(
        kind,
        source_id=record["source_id"],
        nomenclature=record["nomenclature"],
        as_of_date=date.fromisoformat(record["as_of_date"]),
    )
    if record["snapshot_id"] != expected_id:
        raise ValueError("snapshot_id mismatch")
    stage = KIND_STAGE[kind]
    for ref in record["raw_artifact_refs"]:
        if ref["source_id"] != record["source_id"]:
            raise ValueError("mixed source_id in refs")
        if ref["stage"] != stage.value:
            raise ValueError("wrong stage in refs")
    for passport in record.get("evidence", []):
        assert_passport_complete(passport)


def snapshot_sha256(record: dict[str, Any]) -> str:
    return sha256_bytes(canonical_dumps(record).encode("utf-8"))


def write_snapshot(
    record: dict[str, Any],
    root: Path,
    *,
    allow_test_double: bool = False,
) -> Path:
    kind = record["kind"]
    if kind not in SNAPSHOT_ROOTS:
        raise ValueError(f"Unknown kind: {kind}")
    repo_data = PROJECT_ROOT / "data"
    resolved = root.resolve()
    for forbidden in (
        repo_data / "snapshots" / "public",
        repo_data / "synthetic",
    ):
        try:
            resolved.relative_to(forbidden.resolve())
            raise SnapshotWriteConflict(
                f"Snapshot root may not be under {forbidden}"
            )
        except ValueError:
            pass

    validators = {
        "universe": validate_universe_snapshot,
        "tariff": validate_tariff_snapshot,
        "partners": validate_partner_snapshot,
    }
    validators[kind](record, allow_test_double=allow_test_double)

    out_dir = root / SNAPSHOT_ROOTS[kind].replace("data/", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{record['snapshot_id']}.json"
    content = canonical_dumps(record)
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise SnapshotWriteConflict(f"Snapshot write conflict: {path}")
    else:
        path.write_text(content, encoding="utf-8")
    return path


def _derive_as_of_date(pages: Sequence[SourceContractRecord]) -> date:
    """Derive snapshot as_of_date from page retrieval dates."""
    dates: list[date] = []
    for page in pages:
        if not page.retrieved_at:
            continue
        try:
            dates.append(date.fromisoformat(page.retrieved_at.split("T", 1)[0]))
        except ValueError:
            continue
    if not dates:
        raise AcquisitionUnavailable(
            UnavailableReason.FORMAT_NOT_PARSEABLE,
            {"reason": "no retrieved_at on pages"},
        )
    return max(dates)


def _require_normalized_pages(pages: Sequence[SourceContractRecord]) -> None:
    """Refuse snapshot build from PENDING or UNPARSED pages."""
    for page in pages:
        if page.normalization_status in {"PENDING", "UNPARSED"}:
            raise AcquisitionUnavailable(
                UnavailableReason.FORMAT_NOT_PARSEABLE,
                {
                    "page_index": page.page_index,
                    "normalization_status": page.normalization_status,
                },
            )


def _build_refs(
    store: RawStore,
    *,
    source_id: str,
    stage: Stage,
    selected: dict[tuple[str, ...], tuple[Any, tuple[str, ...]]],
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for key, (coverage, _) in sorted(selected.items()):
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        _require_normalized_pages(pages)
        for page in pages:
            if not page.raw_file_path:
                raise RawStoreIntegrityError(
                    f"Missing raw_file_path for page {page.page_index}"
                )
            refs.append(
                {
                    "source_id": source_id,
                    "stage": stage.value,
                    "unit_key": list(key),
                    "query_hash": coverage.query_hash,
                    "run_id": coverage.run_id,
                    "artifact": f"page-{page.page_index:04d}",
                    "path": page.raw_file_path,
                    "sha256": page.sha256,
                }
            )
        cov_path = (
            f"data/raw/{source_id}/{coverage.query_hash}/"
            f"{coverage.run_id}/coverage.json"
        )
        cov_bytes = store.read_coverage(
            source_id, coverage.query_hash, coverage.run_id
        ).to_json()
        refs.append(
            {
                "source_id": source_id,
                "stage": stage.value,
                "unit_key": list(key),
                "query_hash": coverage.query_hash,
                "run_id": coverage.run_id,
                "artifact": "coverage",
                "path": cov_path,
                "sha256": sha256_bytes(
                    canonical_dumps(cov_bytes).encode("utf-8")
                ),
            }
        )
    return refs


def _verify_selected_coverage(
    store: RawStore,
    registry: ConnectorRegistry,
    *,
    source_id: str,
    selected: dict[tuple[str, ...], tuple[Any, tuple[str, ...]]],
    stage: Stage,
) -> None:
    connector = registry.get(
        source_id,
        source_config={},
        store=store,
        transport=None,
        run_id="",
        environ={},
    )
    for key, (coverage, _) in selected.items():
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        pagination = "NONE"
        sample_contract = QueryContract(
            source_id=source_id,
            stage=stage,
            reporter="SAU",
            partner="WLD",
            flow=str(key[0]) if stage == Stage.UNIVERSE else "",
            product_scope=__import__(
                "ior_mvp.acquisition.contracts",
                fromlist=["ProductScope"],
            ).ProductScope.ALL_HS6,
            product_codes=(PRODUCT_SCOPE_ALL,),
            nomenclature="H0",
            periods=(str(coverage.unit["period"]),),
        )
        derived = evaluate_coverage(
            pages,
            pagination_kind=pagination,
            requests_made=coverage.requests_made,
            stop_reason=coverage.stop_reason,
            observed_stop=coverage.observed_stop,
            contract=sample_contract,
            run_id=coverage.run_id,
        )
        if not coverage_matches(coverage, derived):
            raise RawStoreIntegrityError(
                f"Coverage tampered for unit {key}"
            )


def build_universe_snapshot(
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
    *,
    source_id: str,
) -> dict[str, Any]:
    if "universe" not in registry.snapshot_kinds(source_id):
        raise AcquisitionUnavailable(
            UnavailableReason.OUT_OF_SCOPE_CONTENT,
            {"source_id": source_id},
        )
    selected = select_latest_units(
        store, source_id=source_id, stage=Stage.UNIVERSE
    )
    incomplete = [
        key
        for key, (cov, _) in selected.items()
        if cov.status != "COMPLETE"
    ]
    if incomplete:
        raise AcquisitionUnavailable(
            UnavailableReason.COVERAGE_INCOMPLETE,
            {"unit_keys": incomplete},
        )
    _verify_selected_coverage(
        store, registry, source_id=source_id, selected=selected, stage=Stage.UNIVERSE
    )
    source_cfg = config["sources"][source_id]
    connector = registry.get(
        source_id,
        source_config=source_cfg,
        store=store,
        transport=None,
        run_id="",
        environ={},
        config_version=config["metadata"]["version"],
    )
    rows: list[dict[str, Any]] = []
    all_pages: list[SourceContractRecord] = []
    refs = _build_refs(
        store, source_id=source_id, stage=Stage.UNIVERSE, selected=selected
    )
    for key, (coverage, _) in sorted(selected.items()):
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        all_pages.extend(pages)
        for page in pages:
            observations = connector.normalize(
                __import__(
                    "ior_mvp.acquisition.contracts",
                    fromlist=["RawArtifact"],
                ).RawArtifact(contract=page, path=Path("."))
            )
            for obs in observations:
                rows.append(obs.__dict__)
    as_of = _derive_as_of_date(all_pages)
    if not rows:
        raise AcquisitionUnavailable(
            UnavailableReason.FORMAT_NOT_PARSEABLE,
            {"source_id": source_id},
        )
    coverage_block = aggregate_snapshot_coverage(
        selected, source_id=source_id, stage=Stage.UNIVERSE
    )
    record = {
        "schema_version": UNIVERSE_SCHEMA_VERSION,
        "snapshot_id": snapshot_id(
            "universe",
            source_id=source_id,
            nomenclature=source_cfg["nomenclature"],
            as_of_date=as_of,
        ),
        "source_id": source_id,
        "as_of_date": as_of.isoformat(),
        "source_boundary": "public",
        "kind": "universe",
        "nomenclature": source_cfg["nomenclature"],
        "reporter": "SAU",
        "partner": "WLD",
        "product_scope": "ALL_HS6",
        "flows": sorted({k[0] for k in selected}),
        "periods": sorted({k[1] for k in selected}),
        "coverage": coverage_block,
        "raw_artifact_refs": refs,
        "transformation_record": transformation_record(
            formula="normalize_trade_rows",
            parameters={"source_id": source_id},
            exclusions=[],
            config_version=config["metadata"]["version"],
        ),
        "quality_summary": "PASS",
        "evidence": [
            build_acquired_passport(
                store.pages_for(source_id, cov.query_hash, cov.run_id),
                cov,
                source_config=source_cfg,
                supports=["TRADE_VALUE", "TRADE_QUANTITY"],
                transformation_record=transformation_record(
                    formula="normalize_trade_rows",
                    parameters={},
                    exclusions=[],
                    config_version=config["metadata"]["version"],
                ),
                observation_context={"stage": "UNIVERSE"},
                measurement={"row_count": len(rows)},
                contradiction_record=None,
            )
            for _, (cov, _) in sorted(selected.items())
        ],
        "rows": sorted(rows, key=lambda r: (r.get("year", 0), r.get("hs6", ""))),
    }
    return record


def build_tariff_snapshot(
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
    *,
    source_id: str,
) -> dict[str, Any]:
    if "tariff" not in registry.snapshot_kinds(source_id):
        raise AcquisitionUnavailable(
            UnavailableReason.OUT_OF_SCOPE_CONTENT,
            {"source_id": source_id},
        )
    selected = select_latest_units(
        store, source_id=source_id, stage=Stage.TARIFF
    )
    incomplete = [
        key for key, (cov, _) in selected.items() if cov.status != "COMPLETE"
    ]
    if incomplete:
        raise AcquisitionUnavailable(
            UnavailableReason.COVERAGE_INCOMPLETE,
            {"unit_keys": incomplete},
        )
    source_cfg = config["sources"][source_id]
    connector = registry.get(
        source_id,
        source_config=source_cfg,
        store=store,
        transport=None,
        run_id="",
        environ={},
        config_version=config["metadata"]["version"],
    )
    lines: list[dict[str, Any]] = []
    all_pages: list[SourceContractRecord] = []
    refs = _build_refs(
        store, source_id=source_id, stage=Stage.TARIFF, selected=selected
    )
    for _, (coverage, _) in sorted(selected.items()):
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        all_pages.extend(pages)
        for page in pages:
            normalized = connector.normalize(
                __import__(
                    "ior_mvp.acquisition.contracts",
                    fromlist=["RawArtifact"],
                ).RawArtifact(contract=page, path=Path("."))
            )
            for line in normalized:
                lines.append(line.__dict__)
    as_of = _derive_as_of_date(all_pages)
    if not lines:
        raise AcquisitionUnavailable(
            UnavailableReason.FORMAT_NOT_PARSEABLE,
            {"source_id": source_id},
        )
    record = {
        "schema_version": TARIFF_SCHEMA_VERSION,
        "snapshot_id": snapshot_id(
            "tariff",
            source_id=source_id,
            nomenclature=source_cfg["nomenclature"],
            as_of_date=as_of,
        ),
        "source_id": source_id,
        "as_of_date": as_of.isoformat(),
        "source_boundary": "public",
        "kind": "tariff",
        "nomenclature": source_cfg["nomenclature"],
        "coverage": aggregate_snapshot_coverage(
            selected, source_id=source_id, stage=Stage.TARIFF
        ),
        "raw_artifact_refs": refs,
        "transformation_record": transformation_record(
            formula="normalize_tariff_lines",
            parameters={"source_id": source_id},
            exclusions=[],
            config_version=config["metadata"]["version"],
        ),
        "quality_summary": "PASS",
        "evidence": [
            build_acquired_passport(
                store.pages_for(source_id, cov.query_hash, cov.run_id),
                cov,
                source_config=source_cfg,
                supports=["NATIONAL_TARIFF_LINE_MAPPING"],
                transformation_record=transformation_record(
                    formula="normalize_tariff_lines",
                    parameters={},
                    exclusions=[],
                    config_version=config["metadata"]["version"],
                ),
                observation_context={"stage": "TARIFF"},
                measurement={"line_count": len(lines)},
                contradiction_record=None,
            )
            for _, (cov, _) in sorted(selected.items())
        ],
        "lines": sorted(lines, key=lambda r: r.get("national_code", "")),
    }
    return record


def build_partner_snapshot(
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
    *,
    source_id: str,
) -> dict[str, Any]:
    if "partners" not in registry.snapshot_kinds(source_id):
        raise AcquisitionUnavailable(
            UnavailableReason.OUT_OF_SCOPE_CONTENT,
            {"source_id": source_id},
        )
    selected = select_latest_units(
        store, source_id=source_id, stage=Stage.PARTNERS
    )
    complete = {
        k: v for k, v in selected.items() if v[0].status == "COMPLETE"
    }
    if not complete:
        raise AcquisitionUnavailable(
            UnavailableReason.COVERAGE_INCOMPLETE,
            {"unit_keys": list(selected)},
        )
    exclusions = [
        {
            "unit_key": list(key),
            "selected_run_id": cov.run_id,
            "reason": cov.stop_reason.value if cov.stop_reason else "INCOMPLETE",
        }
        for key, (cov, _) in selected.items()
        if cov.status != "COMPLETE"
    ]
    source_cfg = config["sources"][source_id]
    connector = registry.get(
        source_id,
        source_config=source_cfg,
        store=store,
        transport=None,
        run_id="",
        environ={},
        config_version=config["metadata"]["version"],
    )
    rows: list[dict[str, Any]] = []
    all_pages: list[SourceContractRecord] = []
    refs = _build_refs(
        store, source_id=source_id, stage=Stage.PARTNERS, selected=complete
    )
    for key, (coverage, _) in sorted(complete.items()):
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        all_pages.extend(pages)
        for page in pages:
            observations = connector.normalize(
                __import__(
                    "ior_mvp.acquisition.contracts",
                    fromlist=["RawArtifact"],
                ).RawArtifact(contract=page, path=Path("."))
            )
            for obs in observations:
                rows.append(obs.__dict__)
    as_of = _derive_as_of_date(all_pages)
    coverage_block = aggregate_partner_coverage(
        selected, source_id=source_id
    )
    record = {
        "schema_version": PARTNERS_SCHEMA_VERSION,
        "snapshot_id": snapshot_id(
            "partners",
            source_id=source_id,
            nomenclature=source_cfg["nomenclature"],
            as_of_date=as_of,
        ),
        "source_id": source_id,
        "as_of_date": as_of.isoformat(),
        "source_boundary": "public",
        "kind": "partners",
        "nomenclature": source_cfg["nomenclature"],
        "coverage": coverage_block,
        "raw_artifact_refs": refs,
        "transformation_record": transformation_record(
            formula="normalize_partner_rows",
            parameters={"source_id": source_id},
            exclusions=exclusions,
            config_version=config["metadata"]["version"],
        ),
        "quality_summary": "PASS",
        "evidence": [
            build_acquired_passport(
                store.pages_for(source_id, cov.query_hash, cov.run_id),
                cov,
                source_config=source_cfg,
                supports=["TRADE_VALUE", "TRADE_QUANTITY"],
                transformation_record=transformation_record(
                    formula="normalize_partner_rows",
                    parameters={},
                    exclusions=exclusions,
                    config_version=config["metadata"]["version"],
                ),
                observation_context={"stage": "PARTNERS"},
                measurement={"row_count": len(rows)},
                contradiction_record=None,
            )
            for _, (cov, _) in sorted(complete.items())
        ],
        "rows": sorted(rows, key=lambda r: (r.get("hs6", ""), r.get("partner", ""))),
    }
    return record


def _selection_changed(
    record: dict[str, Any],
    store: RawStore,
) -> bool:
    """Return True when latest store run differs from snapshot selection."""
    kind = record["kind"]
    source_id = record["source_id"]
    stage = KIND_STAGE[kind]
    latest = store.latest_runs(source_id=source_id, stage=stage.value)
    stored_units = {
        tuple(unit["unit_key"]): unit["selected_run_id"]
        for unit in record["coverage"].get("units", [])
    }
    for key, (cov, _) in latest.items():
        stored_run = stored_units.get(key)
        if stored_run is None or stored_run != cov.run_id:
            return True
    return False


def reconstruct(
    snapshot_path: Path,
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
) -> ReconstructionResult:
    record = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected_sha = snapshot_sha256(record)
    kind = record["kind"]
    source_id = record["source_id"]
    if _selection_changed(record, store):
        return ReconstructionResult(
            match=False,
            expected_sha256=expected_sha,
            actual_sha256="",
            artifacts_verified=0,
            snapshot_id=record["snapshot_id"],
            detail={
                "reason": "SELECTION_CHANGED",
                "units": list(record["coverage"].get("units", [])),
            },
        )
    builders = {
        "universe": build_universe_snapshot,
        "tariff": build_tariff_snapshot,
        "partners": build_partner_snapshot,
    }
    try:
        rebuilt = builders[kind](store, config, registry, source_id=source_id)
    except AcquisitionUnavailable as exc:
        if exc.reason == UnavailableReason.COVERAGE_INCOMPLETE:
            return ReconstructionResult(
                match=False,
                expected_sha256=expected_sha,
                actual_sha256="",
                artifacts_verified=0,
                snapshot_id=record["snapshot_id"],
                detail={
                    "reason": "COVERAGE_INCOMPLETE",
                    "units": exc.detail.get("unit_keys", []),
                },
            )
        raise
    actual_sha = snapshot_sha256(rebuilt)
    return ReconstructionResult(
        match=actual_sha == expected_sha,
        expected_sha256=expected_sha,
        actual_sha256=actual_sha,
        artifacts_verified=len(record.get("raw_artifact_refs", [])),
        snapshot_id=record["snapshot_id"],
        detail={},
    )
