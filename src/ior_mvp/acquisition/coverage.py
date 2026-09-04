"""Coverage evaluation and latest-run selection."""

from __future__ import annotations

from typing import Any, Sequence

from .contracts import (
    AcquisitionUnavailable,
    CompletenessBasis,
    CoverageRecord,
    ObservedResponse,
    QueryContract,
    SELECTION_RULE,
    SourceContractRecord,
    Stage,
    UnavailableReason,
    unit_key,
)
from .raw_store import RawStore


def not_attempted_coverage(
    contract: QueryContract,
    *,
    run_id: str,
    stop_reason: UnavailableReason,
) -> CoverageRecord:
    """Build coverage for a unit that was never attempted."""
    key = unit_key(contract)
    return CoverageRecord(
        source_id=contract.source_id,
        stage=contract.stage,
        query_hash=contract.query_hash(),
        run_id=run_id,
        unit_key=key,
        unit=_unit_dict(contract),
        pages_fetched=0,
        pages_expected=0,
        requests_made=0,
        status="INCOMPLETE",
        completeness_basis=CompletenessBasis.UNAVAILABLE,
        stop_reason=stop_reason,
        missing_pages=(),
        observed_stop=None,
    )


def _unit_dict(contract: QueryContract) -> dict[str, Any]:
    hs6 = None
    if contract.product_scope.value == "EXPLICIT":
        hs6 = contract.product_codes[0]
    return {
        "stage": contract.stage.value,
        "flow": contract.flow,
        "period": contract.periods[0] if contract.periods else None,
        "product_scope": contract.product_scope.value,
        "hs6": hs6,
    }


def evaluate_coverage(
    pages: Sequence[SourceContractRecord],
    *,
    pagination_kind: str,
    requests_made: int,
    stop_reason: UnavailableReason | None,
    observed_stop: ObservedResponse | None,
    contract: QueryContract,
    run_id: str,
) -> CoverageRecord:
    """Derive coverage record from stored pages per DD-18."""
    key = unit_key(contract)
    pages_fetched = len(pages)
    missing_pages: tuple[int, ...] = ()

    if not pages:
        return not_attempted_coverage(
            contract,
            run_id=run_id,
            stop_reason=stop_reason or UnavailableReason.COVERAGE_INDETERMINATE,
        )

    first_meta = pages[0].page_meta
    pages_expected: int | str = (
        first_meta.pages_expected if first_meta else "UNAVAILABLE"
    )

    if pagination_kind == "UNAVAILABLE" or pages_expected == "UNAVAILABLE":
        return CoverageRecord(
            source_id=contract.source_id,
            stage=contract.stage,
            query_hash=contract.query_hash(),
            run_id=run_id,
            unit_key=key,
            unit=_unit_dict(contract),
            pages_fetched=pages_fetched,
            pages_expected=pages_expected,
            requests_made=requests_made,
            status="INCOMPLETE",
            completeness_basis=CompletenessBasis.UNAVAILABLE,
            stop_reason=stop_reason or UnavailableReason.COVERAGE_INDETERMINATE,
            missing_pages=missing_pages,
            observed_stop=observed_stop,
        )

    if stop_reason == UnavailableReason.MAX_REQUESTS_EXHAUSTED:
        if isinstance(pages_expected, int):
            fetched_indices = {p.page_index for p in pages}
            missing_pages = tuple(
                idx
                for idx in range(1, pages_expected + 1)
                if idx not in fetched_indices
            )
        return CoverageRecord(
            source_id=contract.source_id,
            stage=contract.stage,
            query_hash=contract.query_hash(),
            run_id=run_id,
            unit_key=key,
            unit=_unit_dict(contract),
            pages_fetched=pages_fetched,
            pages_expected=pages_expected,
            requests_made=requests_made,
            status="INCOMPLETE",
            completeness_basis=CompletenessBasis.UNAVAILABLE,
            stop_reason=stop_reason,
            missing_pages=missing_pages,
            observed_stop=observed_stop,
        )

    basis = CompletenessBasis.UNAVAILABLE
    status = "INCOMPLETE"
    final_stop = stop_reason

    if pagination_kind == "NONE":
        if (
            isinstance(pages_expected, int)
            and pages_fetched < pages_expected
        ):
            fetched_indices = {p.page_index for p in pages}
            missing_pages = tuple(
                idx
                for idx in range(1, pages_expected + 1)
                if idx not in fetched_indices
            )
        elif pages_fetched == 1 and pages[0].http_status == 200:
            basis = CompletenessBasis.SINGLE_RESPONSE_NO_PAGINATION
            status = "COMPLETE"
            final_stop = None
    elif pagination_kind == "PAGE_NUMBER":
        if (
            isinstance(pages_expected, int)
            and pages_fetched == pages_expected
        ):
            basis = CompletenessBasis.SOURCE_TOTAL_INDICATOR
            status = "COMPLETE"
            final_stop = None
        elif isinstance(pages_expected, int):
            fetched_indices = {p.page_index for p in pages}
            missing_pages = tuple(
                idx
                for idx in range(1, pages_expected + 1)
                if idx not in fetched_indices
            )
    elif pagination_kind == "NEXT_TOKEN":
        last_meta = pages[-1].page_meta
        if last_meta and not last_meta.next_page_token_present:
            basis = CompletenessBasis.TERMINAL_PAGE_REACHED
            status = "COMPLETE"
            final_stop = None
    elif pagination_kind == "INDEX_ENUMERATION":
        last_meta = pages[-1].page_meta
        if last_meta and last_meta.enumerated_children is not None:
            expected = set(last_meta.enumerated_children)
            fetched = {p.page_index for p in pages}
            if expected <= fetched or pages_fetched >= len(expected):
                basis = CompletenessBasis.INDEX_ENUMERATION_COMPLETE
                status = "COMPLETE"
                final_stop = None

    return CoverageRecord(
        source_id=contract.source_id,
        stage=contract.stage,
        query_hash=contract.query_hash(),
        run_id=run_id,
        unit_key=key,
        unit=_unit_dict(contract),
        pages_fetched=pages_fetched,
        pages_expected=pages_expected,
        requests_made=requests_made,
        status=status,
        completeness_basis=basis,
        stop_reason=final_stop,
        missing_pages=missing_pages,
        observed_stop=observed_stop,
    )


def coverage_matches(
    stored: CoverageRecord,
    derived: CoverageRecord,
) -> bool:
    """Return True when stored and derived coverage agree."""
    return stored.to_json() == derived.to_json()


def select_latest_units(
    store: RawStore,
    *,
    source_id: str,
    stage: Stage,
) -> dict[tuple[str, ...], tuple[CoverageRecord, tuple[str, ...]]]:
    """Select latest run per unit key; raise if store empty."""
    selected = store.latest_runs(source_id=source_id, stage=stage.value)
    if not selected:
        raise AcquisitionUnavailable(
            UnavailableReason.NO_UNITS_IN_STORE,
            {"source_id": source_id, "stage": stage.value},
        )
    return selected


def aggregate_snapshot_coverage(
    selected: dict[tuple[str, ...], tuple[CoverageRecord, tuple[str, ...]]],
    *,
    source_id: str,
    stage: Stage,
) -> dict[str, Any]:
    """Build universe/tariff coverage block."""
    units: list[dict[str, Any]] = []
    complete = 0
    for key, (record, superseded) in sorted(selected.items()):
        if record.status == "COMPLETE":
            complete += 1
        units.append(
            {
                "unit_key": list(key),
                "status": record.status,
                "completeness_basis": record.completeness_basis.value,
                "selected_run_id": record.run_id,
                "superseded_run_ids": list(superseded),
                "query_hash": record.query_hash,
            }
        )
    return {
        "selection_rule": SELECTION_RULE,
        "source_id": source_id,
        "stage": stage.value,
        "status": (
            "COMPLETE"
            if complete == len(selected)
            and all(u["status"] == "COMPLETE" for u in units)
            else "INCOMPLETE"
        ),
        "units_requested": len(selected),
        "units_complete": complete,
        "units": units,
    }


def aggregate_partner_coverage(
    selected: dict[tuple[str, ...], tuple[CoverageRecord, tuple[str, ...]]],
    *,
    source_id: str,
) -> dict[str, Any]:
    """Build partner snapshot coverage block with exclusions."""
    base = aggregate_snapshot_coverage(
        selected,
        source_id=source_id,
        stage=Stage.PARTNERS,
    )
    excluded = [
        {
            "unit_key": list(key),
            "selected_run_id": record.run_id,
            "reason": (
                record.stop_reason.value
                if record.stop_reason
                else "INCOMPLETE"
            ),
        }
        for key, (record, _) in selected.items()
        if record.status != "COMPLETE"
    ]
    base["units_excluded"] = excluded
    return base
