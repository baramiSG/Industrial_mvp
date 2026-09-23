"""Exact structured-need taxonomy for public dataset unlocks."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Collection, Iterable, Mapping, Sequence
from types import MappingProxyType
from typing import Any

from .models import DatasetKind, DatasetUnlock


class ExecutiveIntegrityError(RuntimeError):
    """Raised when governed executive inputs violate their contract."""


_NEED_CODE_TO_DATASET_KIND = MappingProxyType(
    {
        "identity/tariff-line": DatasetKind.IDENTITY_TARIFF,
        "target specification/application": (
            DatasetKind.TARGET_SPECIFICATION_DEMAND
        ),
        "line-level production or producer-grade matrix": (
            DatasetKind.PRODUCER_CAPABILITY
        ),
        "capacity/availability/allocation": (
            DatasetKind.EFFECTIVE_CAPACITY_ALLOCATION
        ),
        "re-export/origin decomposition": DatasetKind.RETAINED_FLOW,
        "route economics": DatasetKind.ROUTE_ECONOMICS,
    }
)


def classify_need_code(code: str) -> DatasetKind:
    """Classify one exact structured evidence-need code.

    Args:
        code: Structured need code emitted by the decision or screening engine.

    Returns:
        The governed dataset kind, or ``UNMAPPED`` for an unknown exact code.
    """
    return _NEED_CODE_TO_DATASET_KIND.get(code, DatasetKind.UNMAPPED)


def validate_frozen_need_codes(codes: Collection[str]) -> None:
    """Fail when frozen repository inputs contain an unmapped need code.

    Args:
        codes: Exact need codes observed across frozen loaded and screening data.

    Raises:
        ExecutiveIntegrityError: If one or more codes are not governed.
    """
    unmapped = sorted(
        code
        for code in set(codes)
        if classify_need_code(code) is DatasetKind.UNMAPPED
    )
    if unmapped:
        raise ExecutiveIntegrityError(
            "Frozen evidence need code(s) are unmapped: "
            + ", ".join(unmapped)
        )


def build_dataset_unlocks(
    loaded_needs: Mapping[str, Collection[str]],
    screening_records: Iterable[Mapping[str, Any]],
) -> tuple[DatasetUnlock, ...]:
    """Aggregate public structured needs without assigning synthetic EVSI."""

    codes: dict[DatasetKind, set[str]] = defaultdict(set)
    loaded: dict[DatasetKind, set[str]] = defaultdict(set)
    screening: dict[DatasetKind, set[str]] = defaultdict(set)
    for opportunity_id, need_codes in loaded_needs.items():
        for code in need_codes:
            kind = classify_need_code(code)
            codes[kind].add(code)
            loaded[kind].add(opportunity_id)
    for record in screening_records:
        hs6 = record.get("hs6")
        needs = record.get("evidence_needs")
        if (
            not isinstance(hs6, str)
            or not isinstance(needs, Sequence)
            or isinstance(needs, (str, bytes))
        ):
            raise ExecutiveIntegrityError("Screening evidence needs are invalid")
        for need in needs:
            if not isinstance(need, Mapping):
                raise ExecutiveIntegrityError("Screening evidence need is invalid")
            code = need.get("code")
            if not isinstance(code, str) or not code:
                raise ExecutiveIntegrityError(
                    f"Screening evidence need code is invalid for {hs6}"
                )
            kind = classify_need_code(code)
            codes[kind].add(code)
            screening[kind].add(hs6)
    return tuple(
        DatasetUnlock(
            dataset_kind=kind,
            need_codes=tuple(sorted(codes[kind])),
            synthetic_flag=False,
            loaded_case_count=len(loaded[kind]),
            loaded_opportunity_ids=tuple(sorted(loaded[kind])),
            screening_record_count=len(screening[kind]),
            screening_hs6=tuple(sorted(screening[kind])),
        )
        for kind in DatasetKind
        if codes[kind]
    )


def extract_case_need_codes(analysis: Mapping[str, Any]) -> tuple[str, ...]:
    """Extract exact structured R12 need codes from one analysis."""

    rules = analysis.get("rules")
    if not isinstance(rules, Sequence) or isinstance(rules, (str, bytes)):
        raise ExecutiveIntegrityError("analysis.rules must be a sequence")
    r12 = next(
        (
            row
            for row in rules
            if isinstance(row, Mapping) and row.get("rule_id") == "R12"
        ),
        None,
    )
    metrics = r12.get("metrics") if isinstance(r12, Mapping) else None
    needs = metrics.get("evidence_needs") if isinstance(metrics, Mapping) else None
    if not isinstance(needs, Sequence) or isinstance(needs, (str, bytes)):
        raise ExecutiveIntegrityError("R12 evidence_needs must be a sequence")
    codes = tuple(
        row.get("need_code") if isinstance(row, Mapping) else None
        for row in needs
    )
    if not all(isinstance(code, str) and code for code in codes):
        raise ExecutiveIntegrityError("R12 evidence need code is invalid")
    return tuple(sorted(codes))
