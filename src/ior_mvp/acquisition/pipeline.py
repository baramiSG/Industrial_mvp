"""Acquisition pipeline — plan units, acquire, build snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .connectors.base import ConnectorRegistry, RequestBudget, default_registry
from .contracts import (
    AcquisitionConfigurationError,
    AcquisitionUnavailable,
    PRODUCT_SCOPE_ALL,
    ProductScope,
    QueryContract,
    Stage,
    UNAVAILABLE,
    UnavailableReason,
    new_run_id,
)
from .coverage import not_attempted_coverage
from .raw_store import RawStore
from .snapshots import (
    build_partner_snapshot,
    build_tariff_snapshot,
    build_universe_snapshot,
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
    source_cfg = config["sources"][source_id]
    nomenclature = source_cfg["nomenclature"]
    reporter = source_cfg["reporter_code"]
    partner = source_cfg["parameters"].get("partner_world_token", "WLD")
    units: list[QueryContract] = []

    if stage == Stage.UNIVERSE:
        for year in years:
            for flow in flows:
                units.append(
                    QueryContract(
                        source_id=source_id,
                        stage=Stage.UNIVERSE,
                        reporter=reporter,
                        partner=partner,
                        flow=flow,
                        product_scope=ProductScope.ALL_HS6,
                        product_codes=(PRODUCT_SCOPE_ALL,),
                        nomenclature=nomenclature,
                        periods=(str(year),),
                    )
                )
    elif stage == Stage.PARTNERS:
        if candidates is None:
            raise AcquisitionConfigurationError(
                "PARTNERS requires candidates"
            )
        for year in years:
            for flow in flows:
                for hs6 in candidates.hs6_codes:
                    units.append(
                        QueryContract(
                            source_id=source_id,
                            stage=Stage.PARTNERS,
                            reporter=reporter,
                            partner=partner,
                            flow=flow,
                            product_scope=ProductScope.EXPLICIT,
                            product_codes=(hs6,),
                            nomenclature=nomenclature,
                            periods=(str(year),),
                        )
                    )
    elif stage == Stage.TARIFF:
        # DD-5: one contract for the whole published tariff tree. The tree is
        # not period-scoped (its as-of date comes from retrieval), so `years`
        # is ignored and the contract carries no period.
        units.append(
            QueryContract(
                source_id=source_id,
                stage=Stage.TARIFF,
                reporter=reporter,
                partner=partner,
                flow=UNAVAILABLE,
                product_scope=ProductScope.ALL_TARIFF_LINES,
                product_codes=(PRODUCT_SCOPE_ALL,),
                nomenclature=nomenclature,
                periods=(),
            )
        )
    elif stage == Stage.BULK:
        for year in years:
            units.append(
                QueryContract(
                    source_id=source_id,
                    stage=Stage.BULK,
                    reporter=reporter,
                    partner=partner,
                    flow=UNAVAILABLE,
                    product_scope=ProductScope.NOT_APPLICABLE,
                    product_codes=(),
                    nomenclature=nomenclature,
                    periods=(str(year),),
                )
            )
    return tuple(units)


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


def build_snapshots(
    kind: str,
    deps: PipelineDeps,
    *,
    source_id: str | None = None,
    data_root: Path | None = None,
    allow_test_double: bool = False,
) -> BuildReport:
    kinds = ("universe", "tariff", "partners") if kind == "all" else (kind,)
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
            builders = {
                "universe": build_universe_snapshot,
                "tariff": build_tariff_snapshot,
                "partners": build_partner_snapshot,
            }
            try:
                record = builders[snap_kind](
                    deps.store, deps.config, deps.registry, source_id=sid
                )
                path = write_snapshot(
                    record,
                    root,
                    allow_test_double=allow_test_double,
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
