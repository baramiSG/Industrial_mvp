"""Acquisition pipeline — plan units, acquire, build snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .connectors.base import ConnectorRegistry, RequestBudget
from .contracts import (
    AcquisitionConfigurationError,
    AcquisitionUnavailable,
    QueryContract,
    Stage,
    UNAVAILABLE,
    UnavailableReason,
    stage_spec,
)
from .coverage import not_attempted_coverage
from .raw_store import RawStore
from .kinds import KindRegistry, default_kind_registry
from .snapshots import (
    build_row_snapshot,
    write_snapshot,
)
from .transport import Transport


@dataclass(frozen=True)
class CandidateList:
    candidate_source: str
    hs6_codes: tuple[str, ...]
    recorded_on: str


@dataclass(frozen=True)
class PipelineDeps:
    config: dict[str, Any]
    store: RawStore
    transport: Transport
    registry: ConnectorRegistry
    run_id: str
    environ: Mapping[str, str]
    sleeper: Callable[[float], None]
    kinds: KindRegistry = field(default_factory=default_kind_registry)


@dataclass(frozen=True)
class RunReport:
    run_id: str
    source_id: str
    stage: str
    years: tuple[int, ...]
    flows: tuple[str, ...]
    max_requests: int
    requests_made: int
    artifacts: tuple[str, ...]
    coverage: tuple[Any, ...]
    unavailable: tuple[str, ...]
    exit_code: int


@dataclass(frozen=True)
class BuildReport:
    built: tuple[str, ...]
    unavailable: tuple[tuple[str, str, str], ...]
    raw_only: tuple[str, ...]


def load_candidate_list(path: Path) -> CandidateList:
    payload = json.loads(path.read_text(encoding="utf-8"))
    codes = tuple(payload["hs6_codes"])
    for code in codes:
        if len(code) != 6 or not code.isdigit():
            raise AcquisitionConfigurationError(
                f"Invalid HS6 code in candidates: {code!r}"
            )
    return CandidateList(
        candidate_source=str(payload["candidate_source"]),
        hs6_codes=codes,
        recorded_on=str(payload["recorded_on"]),
    )


def plan_units(
    stage: Stage,
    *,
    source_id: str,
    years: Sequence[int],
    flows: Sequence[str],
    candidates: CandidateList | None,
    config: dict[str, Any],
) -> tuple[QueryContract, ...]:
    return stage_spec(stage).plan_units(
        source_id=source_id, years=years, flows=flows, candidates=candidates, config=config)


def plan_requests(
    stage: Stage,
    *,
    years: Sequence[int],
    flows: Sequence[str],
    candidates: CandidateList | None,
    source_config: dict[str, Any],
) -> int:
    terms = 0
    if (
        source_config.get("license_capture_required")
        and source_config.get("terms_reference") != UNAVAILABLE
    ):
        terms = 1
    units = plan_units(
        stage,
        source_id=source_config.get("source_id", ""),
        years=years,
        flows=flows,
        candidates=candidates,
        config={"sources": {source_config.get("source_id", ""): source_config}},
    )
    return terms + len(units)


def _run_units(
    deps: PipelineDeps,
    *,
    source_id: str,
    stage: Stage,
    units: tuple[QueryContract, ...],
    max_requests: int,
    candidates: CandidateList | None = None,
) -> RunReport:
    source_cfg = deps.config["sources"][source_id]
    years = tuple(sorted({int(u.periods[0]) for u in units if u.periods}))
    flows = tuple(sorted({u.flow for u in units if u.flow != UNAVAILABLE}))
    min_required = plan_requests(
        stage,
        years=years,
        flows=flows,
        candidates=candidates,
        source_config={**source_cfg, "source_id": source_id},
    )
    if max_requests < min_required:
        raise AcquisitionConfigurationError(
            f"max_requests {max_requests} below minimum {min_required}"
        )

    artifacts: list[str] = []
    coverage_records: list[Any] = []
    unavailable: list[str] = []
    requests_made = 0

    connector = deps.registry.get(
        source_id,
        source_config=source_cfg,
        store=deps.store,
        transport=deps.transport,
        run_id=deps.run_id,
        environ=deps.environ,
        sleeper=deps.sleeper,
        config_version=deps.config["metadata"]["version"],
    )
    shared_budget = RequestBudget(max_requests=max_requests)

    for unit in units:
        connector.request_budget = shared_budget
        result = connector.acquire(unit, max_requests=max_requests)
        if isinstance(result, tuple):
            arts, cov = result
            artifacts.extend(str(a.path) for a in arts)
            coverage_records.append(cov.to_json())
            requests_made += cov.requests_made
        else:
            unavailable.append(result.reason.value)
            if result.coverage:
                coverage_records.append(result.coverage.to_json())
            else:
                cov = not_attempted_coverage(
                    unit,
                    run_id=deps.run_id,
                    stop_reason=result.reason,
                )
                deps.store.write_coverage(cov)
                coverage_records.append(cov.to_json())

    all_complete = all(
        c.get("status") == "COMPLETE" for c in coverage_records
    )
    exit_code = 0 if all_complete and not unavailable else 3
    years = tuple(
        sorted({int(u.periods[0]) for u in units if u.periods})
    )
    flows = tuple(sorted({u.flow for u in units if u.flow != UNAVAILABLE}))
    return RunReport(
        run_id=deps.run_id,
        source_id=source_id,
        stage=stage.value,
        years=years,
        flows=flows,
        max_requests=max_requests,
        requests_made=requests_made,
        artifacts=tuple(artifacts),
        coverage=tuple(coverage_records),
        unavailable=tuple(unavailable),
        exit_code=exit_code,
    )


def acquire_universe(
    source_id: str,
    *,
    years: Sequence[int],
    flows: Sequence[str],
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.UNIVERSE,
        source_id=source_id,
        years=years,
        flows=flows,
        candidates=None,
        config=deps.config,
    )
    return _run_units(
        deps,
        source_id=source_id,
        stage=Stage.UNIVERSE,
        units=units,
        max_requests=max_requests,
    )


def acquire_partners(
    source_id: str,
    *,
    candidates: CandidateList,
    years: Sequence[int],
    flows: Sequence[str],
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.PARTNERS,
        source_id=source_id,
        years=years,
        flows=flows,
        candidates=candidates,
        config=deps.config,
    )
    return _run_units(
        deps,
        source_id=source_id,
        stage=Stage.PARTNERS,
        units=units,
        max_requests=max_requests,
        candidates=candidates,
    )


def acquire_tariff(
    source_id: str,
    *,
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.TARIFF,
        source_id=source_id,
        years=(),
        flows=(),
        candidates=None,
        config=deps.config,
    )
    return _run_units(
        deps,
        source_id=source_id,
        stage=Stage.TARIFF,
        units=units,
        max_requests=max_requests,
    )


def acquire_baci(
    *,
    years: Sequence[int],
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    source_id = "baci_cepii"
    units = plan_units(
        Stage.BULK,
        source_id=source_id,
        years=years,
        flows=(),
        candidates=None,
        config=deps.config,
    )
    return _run_units(
        deps,
        source_id=source_id,
        stage=Stage.BULK,
        units=units,
        max_requests=max_requests,
    )


def acquire_aggregates(
    source_id: str,
    *,
    years: Sequence[int],
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.AGGREGATE, source_id=source_id, years=years, flows=(),
        candidates=None, config=deps.config,
    )
    return _run_units(
        deps, source_id=source_id, stage=Stage.AGGREGATE,
        units=units, max_requests=max_requests,
    )


def acquire_directory(
    source_id: str,
    *,
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.DIRECTORY, source_id=source_id, years=(), flows=(),
        candidates=None, config=deps.config,
    )
    return _run_units(
        deps, source_id=source_id, stage=Stage.DIRECTORY,
        units=units, max_requests=max_requests,
    )


def acquire_registry(
    source_id: str,
    *,
    deps: PipelineDeps,
    max_requests: int,
) -> RunReport:
    units = plan_units(
        Stage.REGISTRY, source_id=source_id, years=(), flows=(),
        candidates=None, config=deps.config,
    )
    return _run_units(
        deps, source_id=source_id, stage=Stage.REGISTRY,
        units=units, max_requests=max_requests,
    )


def build_snapshots(
    kind: str,
    deps: PipelineDeps,
    *,
    source_id: str | None = None,
    data_root: Path | None = None,
    allow_test_double: bool = False,
) -> BuildReport:
    kinds = deps.kinds.ids() if kind == "all" else (deps.kinds.get(kind).kind,)
    built: list[str] = []
    unavailable: list[tuple[str, str, str]] = []
    raw_only: list[str] = []
    root = data_root or deps.store.root.parent

    for snap_kind in kinds:
        for sid in deps.registry.ids():
            if source_id and sid != source_id:
                continue
            kinds_for_source = deps.registry.snapshot_kinds(sid)
            if not kinds_for_source:
                raw_only.append(sid)
                continue
            if snap_kind not in kinds_for_source:
                continue
            try:
                record = build_row_snapshot(
                    deps.store, deps.config, deps.registry, kind=snap_kind, source_id=sid, kinds=deps.kinds
                )
                path = write_snapshot(
                    record,
                    root,
                    allow_test_double=allow_test_double,
                    kinds=deps.kinds,
                )
                built.append(str(path))
            except AcquisitionUnavailable as exc:
                unavailable.append(
                    (snap_kind, sid, exc.reason.value)
                )

    if not built and kind != "all":
        raise AcquisitionUnavailable(
            UnavailableReason.FORMAT_NOT_PARSEABLE,
            {"built": built, "unavailable": unavailable},
        )
    return BuildReport(
        built=tuple(built),
        unavailable=tuple(unavailable),
        raw_only=tuple(sorted(set(raw_only))),
    )
