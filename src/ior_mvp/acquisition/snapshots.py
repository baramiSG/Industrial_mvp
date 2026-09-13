"""Deterministic snapshot builders and validators."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from ..config import PROJECT_ROOT
from ..public_snapshot import _reject_authored_outcomes
from .connectors.base import ConnectorRegistry
from .contracts import (
    AcquisitionUnavailable,
    RawArtifact,
    RawStoreIntegrityError,
    SELECTION_RULE,
    SnapshotWriteConflict,
    SourceContractRecord,
    Stage,
    UNAVAILABLE,
    UnavailableReason,
    canonical_dumps,
    sha256_bytes,
)
from .coverage import (
    aggregate_exclusion_coverage,
    aggregate_snapshot_coverage,
    coverage_matches,
    evaluate_coverage,
    select_latest_units,
)
from .harmonise import transformation_record
from .passports import assert_passport_complete, build_acquired_passport
from .raw_store import RawStore, TEST_DOUBLE_CLASS, TEST_FIXTURE_SOURCE
from .kinds import CompletenessPolicy, KindRegistry, default_kind_registry

UNIVERSE_SCHEMA_VERSION = "1.0.0"
TARIFF_SCHEMA_VERSION = "1.0.0"
PARTNERS_SCHEMA_VERSION = "1.0.0"

SNAPSHOT_ROOTS = default_kind_registry().roots()
KIND_STAGE = {kind: default_kind_registry().stage_for(kind) for kind in SNAPSHOT_ROOTS}


@dataclass(frozen=True)
class ReconstructionResult:
    match: bool
    expected_sha256: str
    actual_sha256: str
    artifacts_verified: int
    snapshot_id: str
    detail: dict[str, Any]


def snapshot_id(kind: str, *, source_id: str, nomenclature: str,
                as_of_date: date, kinds: KindRegistry | None = None,
                scope_units: Sequence[Sequence[str]] | None = None) -> str:
    return (kinds or default_kind_registry()).snapshot_id(
        kind,
        source_id=source_id,
        nomenclature=nomenclature,
        as_of_date=as_of_date,
        scope_units=scope_units,
    )


def _scope_units(record: dict[str, Any]) -> list[list[str]]:
    units: list[list[str]] = []
    for coverage_unit in record.get("coverage", {}).get("units", []):
        unit_key = coverage_unit.get("unit_key")
        if (
            not isinstance(unit_key, list)
            or not unit_key
            or any(not isinstance(value, str) or not value for value in unit_key)
        ):
            raise ValueError("scope unit_key must be a non-empty string array")
        units.append(list(unit_key))
    units.sort(key=canonical_dumps)
    if not units or len({canonical_dumps(unit) for unit in units}) != len(units):
        raise ValueError("scope_units must be non-empty and unique")
    return units


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
    for passport in record.get("evidence", []):
        if passport.get("source_identity", {}).get("access_classification") == TEST_DOUBLE_CLASS:
            raise ValueError("test_double passport access_classification rejected")


def validate_snapshot(record: dict[str, Any], *, kinds: KindRegistry | None = None,
                      allow_test_double: bool = False,
                      data_root: Path = PROJECT_ROOT / "data") -> None:
    kinds = kinds or default_kind_registry()
    spec = kinds.get(record["kind"])
    _validate_common(
        record,
        kind=spec.kind,
        kinds=kinds,
        allow_test_double=allow_test_double,
        data_root=data_root,
    )
    spec.validator_extra(record)


def _validate_named(
    record: dict[str, Any],
    kind: str,
    allow_test_double: bool,
    data_root: Path,
) -> None:
    if record.get("kind") != kind:
        raise ValueError(f"kind mismatch: {kind}")
    validate_snapshot(
        record,
        allow_test_double=allow_test_double,
        data_root=data_root,
    )


def validate_universe_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
    data_root: Path = PROJECT_ROOT / "data",
) -> None:
    _validate_named(record, "universe", allow_test_double, data_root)


def validate_tariff_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
    data_root: Path = PROJECT_ROOT / "data",
) -> None:
    _validate_named(record, "tariff", allow_test_double, data_root)


def validate_partner_snapshot(
    record: dict[str, Any],
    *,
    allow_test_double: bool = False,
    data_root: Path = PROJECT_ROOT / "data",
) -> None:
    _validate_named(record, "partners", allow_test_double, data_root)


def _validate_common(
    record: dict[str, Any],
    *,
    kind: str,
    kinds: KindRegistry,
    allow_test_double: bool,
    data_root: Path,
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
    scope_units = record.get("scope_units")
    coexists_with = record.get("coexists_with")
    if (scope_units is None) != (coexists_with is None):
        raise ValueError("scope_units and coexists_with must appear together")
    base_id = snapshot_id(
        kind,
        source_id=record["source_id"],
        nomenclature=record["nomenclature"],
        as_of_date=date.fromisoformat(record["as_of_date"]),
        kinds=kinds,
    )
    if scope_units is not None:
        if scope_units != _scope_units(record):
            raise ValueError("scope_units must equal sorted coverage unit keys")
        if coexists_with != base_id:
            raise ValueError("coexists_with must equal the unscoped snapshot id")
        if "supersedes" in record:
            raise ValueError("scoped analytical snapshots must not supersede")
        sibling_path = (
            _snapshot_directory(data_root, kinds.get(kind).root)
            / f"{coexists_with}.json"
        )
        if not sibling_path.is_file():
            raise ValueError("coexists_with sibling does not exist")
        try:
            sibling = json.loads(sibling_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("coexists_with sibling is unreadable") from exc
        for field in ("kind", "source_id", "nomenclature", "as_of_date"):
            if sibling.get(field) != record[field]:
                raise ValueError(f"coexists_with sibling {field} mismatch")
        if sibling.get("snapshot_id") != coexists_with:
            raise ValueError("coexists_with sibling identity mismatch")
        if "scope_units" in sibling or "coexists_with" in sibling:
            raise ValueError("coexists_with sibling must be unscoped")
        sibling_units = {
            canonical_dumps(unit)
            for unit in _scope_units(sibling)
        }
        if sibling_units & {canonical_dumps(unit) for unit in scope_units}:
            raise ValueError("scoped and sibling unit keys overlap")
        expected_id = snapshot_id(
            kind,
            source_id=record["source_id"],
            nomenclature=record["nomenclature"],
            as_of_date=date.fromisoformat(record["as_of_date"]),
            kinds=kinds,
            scope_units=scope_units,
        )
    else:
        expected_id = base_id
    if record["snapshot_id"] != expected_id:
        raise ValueError("snapshot_id mismatch")
    stage = kinds.stage_for(kind)
    for ref in record["raw_artifact_refs"]:
        if ref["source_id"] != record["source_id"]:
            raise ValueError("mixed source_id in refs")
        if ref["stage"] != stage.value:
            raise ValueError("wrong stage in refs")
    for passport in record.get("evidence", []):
        assert_passport_complete(passport)


def snapshot_sha256(record: dict[str, Any]) -> str:
    return sha256_bytes(canonical_dumps(record).encode("utf-8"))


def _snapshot_directory(root: Path, kind_root: str) -> Path:
    """Resolve a registry path inside its data root and outside frozen evidence."""
    relative = Path(kind_root)
    if relative.is_absolute() or not kind_root.startswith("data/") or ".." in relative.parts:
        raise SnapshotWriteConflict(f"Unsafe snapshot kind root: {kind_root}")
    resolved_root = root.resolve()
    directory = (resolved_root / kind_root.removeprefix("data/")).resolve()
    if not directory.is_relative_to(resolved_root):
        raise SnapshotWriteConflict(f"Snapshot directory escapes data root: {kind_root}")
    for forbidden in (PROJECT_ROOT / "data" / "snapshots" / "public", PROJECT_ROOT / "data" / "synthetic"):
        if directory.is_relative_to(forbidden.resolve()):
            raise SnapshotWriteConflict(f"Snapshot directory may not be under {forbidden}")
    return directory


def write_snapshot(
    record: dict[str, Any],
    root: Path,
    *,
    allow_test_double: bool = False,
    kinds: KindRegistry | None = None,
) -> Path:
    kind = record["kind"]
    kinds = kinds or default_kind_registry()
    spec = kinds.get(kind)
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

    validate_snapshot(
        record,
        kinds=kinds,
        allow_test_double=allow_test_double,
        data_root=root,
    )

    out_dir = _snapshot_directory(root, spec.root)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{record['snapshot_id']}.json"
    content = canonical_dumps(record)
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return path
        if "scope_units" in record or "coexists_with" in record:
            raise SnapshotWriteConflict(f"Snapshot write conflict: {path}")
        existing = json.loads(path.read_text(encoding="utf-8"))
        validate_snapshot(
            existing,
            kinds=kinds,
            allow_test_double=allow_test_double,
            data_root=root,
        )
        existing_units = {
            canonical_dumps(unit) for unit in _scope_units(existing)
        }
        candidate_units = {
            canonical_dumps(unit) for unit in _scope_units(record)
        }
        if existing_units & candidate_units:
            raise ValueError("scoped and sibling unit keys overlap")
        scoped = {
            **record,
            "snapshot_id": snapshot_id(
                kind,
                source_id=record["source_id"],
                nomenclature=record["nomenclature"],
                as_of_date=date.fromisoformat(record["as_of_date"]),
                kinds=kinds,
                scope_units=_scope_units(record),
            ),
            "scope_units": _scope_units(record),
            "coexists_with": existing["snapshot_id"],
        }
        validate_snapshot(
            scoped,
            kinds=kinds,
            allow_test_double=allow_test_double,
            data_root=root,
        )
        path = out_dir / f"{scoped['snapshot_id']}.json"
        content = canonical_dumps(scoped)
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise SnapshotWriteConflict(f"Snapshot write conflict: {path}")
        if not path.exists():
            path.write_text(content, encoding="utf-8")
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
    store: RawStore, config: dict[str, Any], *, source_id: str,
    selected: dict[tuple[str, ...], tuple[Any, tuple[str, ...]]],
) -> None:
    for key, (coverage, _) in selected.items():
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        if not pages:
            raise RawStoreIntegrityError(f"Missing pages for complete unit {key}")
        # RawStore reconstructs this complete QueryContract from the stored JSON.
        contract = pages[0].query_contract
        derived = evaluate_coverage(
            pages, pagination_kind=config["sources"][source_id]["pagination"]["kind"],
            requests_made=coverage.requests_made, stop_reason=coverage.stop_reason,
            observed_stop=coverage.observed_stop, contract=contract, run_id=coverage.run_id,
        )
        if not coverage_matches(coverage, derived):
            raise RawStoreIntegrityError(f"Coverage tampered for unit {key}")


def build_row_snapshot(
    store: RawStore, config: dict[str, Any], registry: ConnectorRegistry, *,
    kind: str, source_id: str, kinds: KindRegistry | None = None,
    selected_override: dict[tuple[str, ...], tuple[Any, tuple[str, ...]]] | None = None,
) -> dict[str, Any]:
    kinds = kinds or default_kind_registry()
    spec = kinds.get(kind)
    if kind not in registry.snapshot_kinds(source_id):
        raise AcquisitionUnavailable(UnavailableReason.OUT_OF_SCOPE_CONTENT, {"source_id": source_id})
    selected = selected_override or select_latest_units(
        store, source_id=source_id, stage=spec.stage
    )
    complete = {key: value for key, value in selected.items() if value[0].status == "COMPLETE"}
    incomplete = [key for key in selected if key not in complete]
    source_cfg = config["sources"][source_id]
    connector = registry.get(
        source_id,
        source_config=source_cfg,
        store=store,
        transport=None,
        run_id="",
        environ={},
        config_version=spec.config_version,
    )
    if spec.completeness_policy == CompletenessPolicy.ALL_UNITS_COMPLETE:
        if incomplete:
            raise AcquisitionUnavailable(UnavailableReason.COVERAGE_INCOMPLETE, {"unit_keys": incomplete})
        coverage_block = aggregate_snapshot_coverage(selected, source_id=source_id, stage=spec.stage)
        exclusions = []
    elif spec.completeness_policy == CompletenessPolicy.AT_LEAST_ONE_COMPLETE_WITH_EXCLUSIONS:
        unparseable = {
            key
            for key, (coverage, _) in complete.items()
            if not (
                (pages := store.pages_for(
                    source_id, coverage.query_hash, coverage.run_id
                ))
                and all(
                    page.normalization_status not in {"PENDING", "UNPARSED"}
                    for page in pages
                )
            )
        }
        effective_selected = {
            key: (
                replace(
                    coverage,
                    status="INCOMPLETE",
                    stop_reason=UnavailableReason.FORMAT_NOT_PARSEABLE,
                ),
                superseded,
            )
            if key in unparseable
            else (coverage, superseded)
            for key, (coverage, superseded) in selected.items()
        }
        complete = {
            key: value for key, value in complete.items() if key not in unparseable
        }
        if not complete:
            reason = (
                UnavailableReason.FORMAT_NOT_PARSEABLE
                if unparseable
                else UnavailableReason.COVERAGE_INCOMPLETE
            )
            raise AcquisitionUnavailable(reason, {"unit_keys": list(selected)})
        coverage_block = aggregate_exclusion_coverage(
            effective_selected, source_id=source_id, stage=spec.stage
        )
        exclusions = coverage_block["units_excluded"]
    else:
        raise ValueError(f"Unknown completeness policy: {spec.completeness_policy}")
    _verify_selected_coverage(
        store,
        config,
        source_id=source_id,
        selected={
            key: value
            for key, value in selected.items()
            if value[0].status == "COMPLETE"
        },
    )
    refs = _build_refs(store, source_id=source_id, stage=spec.stage, selected=complete)
    rows: list[dict[str, Any]] = []
    all_pages: list[SourceContractRecord] = []
    for _, (coverage, _) in sorted(complete.items()):
        pages = store.pages_for(source_id, coverage.query_hash, coverage.run_id)
        all_pages.extend(pages)
        for page in pages:
            raw = RawArtifact(contract=page, path=Path("."))
            quality = connector.validate(raw)
            if quality.status != "PASS" or any(check.result != "PASS" for check in quality.checks):
                raise AcquisitionUnavailable(UnavailableReason.FORMAT_NOT_PARSEABLE,
                                             {"source_id": source_id, "quality_status": quality.status})
            rows.extend(obs.__dict__ for obs in connector.normalize(raw))
    if not rows:
        raise AcquisitionUnavailable(UnavailableReason.FORMAT_NOT_PARSEABLE, {"source_id": source_id})
    as_of = _derive_as_of_date(all_pages)
    record = {
        "schema_version": spec.schema_version,
        "snapshot_id": kinds.snapshot_id(kind, source_id=source_id, nomenclature=source_cfg["nomenclature"], as_of_date=as_of),
        "source_id": source_id, "as_of_date": as_of.isoformat(),
        "source_boundary": "public", "kind": kind, "nomenclature": source_cfg["nomenclature"],
        **spec.extra_fields(selected),
        "coverage": coverage_block, "raw_artifact_refs": refs,
        "transformation_record": transformation_record(
            formula=spec.formula, parameters={"source_id": source_id},
            exclusions=exclusions, config_version=spec.config_version),
        "quality_summary": "PASS",
        "evidence": [
            build_acquired_passport(
                store.pages_for(source_id, cov.query_hash, cov.run_id), cov,
                source_config=source_cfg, supports=list(spec.supports),
                transformation_record=transformation_record(
                    formula=spec.formula, parameters={}, exclusions=exclusions,
                    config_version=spec.config_version),
                observation_context={"stage": spec.stage.value},
                measurement={spec.measurement_key: len(rows)}, contradiction_record=None,
            ) for _, (cov, _) in sorted(complete.items())
        ],
        spec.rows_key: sorted(rows, key=spec.row_sort_key),
    }
    validate_snapshot(record, kinds=kinds, allow_test_double=True)
    return record


def build_universe_snapshot(store: RawStore, config: dict[str, Any], registry: ConnectorRegistry, *, source_id: str) -> dict[str, Any]:
    return build_row_snapshot(store, config, registry, kind="universe", source_id=source_id)


def build_tariff_snapshot(store: RawStore, config: dict[str, Any], registry: ConnectorRegistry, *, source_id: str) -> dict[str, Any]:
    return build_row_snapshot(store, config, registry, kind="tariff", source_id=source_id)


def build_partner_snapshot(store: RawStore, config: dict[str, Any], registry: ConnectorRegistry, *, source_id: str) -> dict[str, Any]:
    return build_row_snapshot(store, config, registry, kind="partners", source_id=source_id)


def _selection_changed(
    record: dict[str, Any],
    store: RawStore,
    kinds: KindRegistry,
) -> bool:
    """Return True when latest store run differs from snapshot selection."""
    kind = record["kind"]
    source_id = record["source_id"]
    stage = kinds.stage_for(kind)
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


def _recorded_selection(
    record: dict[str, Any],
    store: RawStore,
) -> dict[tuple[str, ...], tuple[Any, tuple[str, ...]]]:
    source_id = record["source_id"]
    selected: dict[tuple[str, ...], tuple[Any, tuple[str, ...]]] = {}
    for unit in record.get("coverage", {}).get("units", []):
        key = tuple(unit["unit_key"])
        coverage = store.read_coverage(
            source_id,
            str(unit["query_hash"]),
            str(unit["selected_run_id"]),
        )
        if coverage.unit_key != key or coverage.source_id != source_id:
            raise RawStoreIntegrityError("snapshot recorded selection mismatch")
        selected[key] = (
            coverage,
            tuple(unit.get("superseded_run_ids", [])),
        )
    if not selected:
        raise RawStoreIntegrityError("snapshot recorded selection is empty")
    return selected


def reconstruct_pinned(
    snapshot_path: Path,
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
    kinds: KindRegistry | None = None,
) -> ReconstructionResult:
    """Rebuild a historical snapshot from its recorded raw-run selection."""
    kinds = kinds or default_kind_registry()
    record = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected_sha = snapshot_sha256(record)
    selected = _recorded_selection(record, store)
    rebuilt = build_row_snapshot(
        store,
        config,
        registry,
        kind=record["kind"],
        source_id=record["source_id"],
        kinds=kinds,
        selected_override=selected,
    )
    if "scope_units" in record:
        rebuilt = {
            **rebuilt,
            "snapshot_id": record["snapshot_id"],
            "scope_units": record["scope_units"],
            "coexists_with": record["coexists_with"],
        }
        validate_snapshot(
            rebuilt,
            kinds=kinds,
            allow_test_double=True,
            data_root=snapshot_path.parents[2],
        )
    actual_sha = snapshot_sha256(rebuilt)
    return ReconstructionResult(
        match=actual_sha == expected_sha,
        expected_sha256=expected_sha,
        actual_sha256=actual_sha,
        artifacts_verified=len(record.get("raw_artifact_refs", [])),
        snapshot_id=record["snapshot_id"],
        detail={},
    )


def reconstruct(
    snapshot_path: Path,
    store: RawStore,
    config: dict[str, Any],
    registry: ConnectorRegistry,
    kinds: KindRegistry | None = None,
) -> ReconstructionResult:
    kinds = kinds or default_kind_registry()
    record = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected_sha = snapshot_sha256(record)
    kind = record["kind"]
    source_id = record["source_id"]
    kinds.get(kind)
    if _selection_changed(record, store, kinds):
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
    try:
        rebuilt = build_row_snapshot(store, config, registry, kind=kind, source_id=source_id, kinds=kinds)
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
    if "scope_units" in record:
        rebuilt = {
            **rebuilt,
            "snapshot_id": record["snapshot_id"],
            "scope_units": record["scope_units"],
            "coexists_with": record["coexists_with"],
        }
        validate_snapshot(
            rebuilt,
            kinds=kinds,
            allow_test_double=True,
            data_root=snapshot_path.parents[2],
        )
    actual_sha = snapshot_sha256(rebuilt)
    return ReconstructionResult(
        match=actual_sha == expected_sha,
        expected_sha256=expected_sha,
        actual_sha256=actual_sha,
        artifacts_verified=len(record.get("raw_artifact_refs", [])),
        snapshot_id=record["snapshot_id"],
        detail={},
    )
