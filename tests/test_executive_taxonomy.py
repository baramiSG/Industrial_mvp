"""Executive need-code taxonomy and screening iterator contracts."""

from __future__ import annotations

from collections import Counter

import pytest


KNOWN_MAPPING = {
    "identity/tariff-line": "IDENTITY_TARIFF",
    "target specification/application": "TARGET_SPECIFICATION_DEMAND",
    "line-level production or producer-grade matrix": "PRODUCER_CAPABILITY",
    "capacity/availability/allocation": "EFFECTIVE_CAPACITY_ALLOCATION",
    "re-export/origin decomposition": "RETAINED_FLOW",
    "route economics": "ROUTE_ECONOMICS",
}


@pytest.mark.parametrize(("code", "kind"), KNOWN_MAPPING.items())
def test_exact_need_code_mapping(code: str, kind: str) -> None:
    from ior_mvp.executive.taxonomy import classify_need_code

    assert classify_need_code(code).value == kind


def test_unknown_need_code_remains_visible_as_unmapped() -> None:
    from ior_mvp.executive.models import DatasetKind
    from ior_mvp.executive.taxonomy import classify_need_code

    assert classify_need_code("future governed need") is DatasetKind.UNMAPPED


def test_frozen_code_validation_fails_closed_on_unmapped_code() -> None:
    from ior_mvp.executive.taxonomy import (
        ExecutiveIntegrityError,
        validate_frozen_need_codes,
    )

    with pytest.raises(
        ExecutiveIntegrityError,
        match="future governed need",
    ):
        validate_frozen_need_codes((*KNOWN_MAPPING, "future governed need"))


def test_screening_iterator_returns_exact_unique_frozen_records_without_mutation() -> None:
    from ior_mvp.screening.repository import (
        clear_screening_caches,
        iter_screening_records,
        screening_record,
    )

    clear_screening_caches()
    records = tuple(iter_screening_records())
    assert len(records) == 5_443
    assert len({record["hs6"] for record in records}) == 5_443
    assert [record["hs6"] for record in records] == sorted(
        record["hs6"] for record in records
    )

    first_hs6 = records[0]["hs6"]
    records[0]["hs6"] = "MUTATED"
    stored = screening_record(first_hs6)
    assert stored is not None
    assert stored["hs6"] == first_hs6


def test_all_frozen_loaded_and_screening_need_codes_are_mapped() -> None:
    from ior_mvp.data_repository import public_cases
    from ior_mvp.decision_engine import analyze
    from ior_mvp.executive.models import DatasetKind
    from ior_mvp.executive.taxonomy import (
        classify_need_code,
        validate_frozen_need_codes,
    )
    from ior_mvp.screening.repository import iter_screening_records

    loaded_codes: Counter[str] = Counter()
    for opportunity_id in public_cases():
        analysis = analyze(opportunity_id, "public")
        r12 = next(row for row in analysis["rules"] if row["rule_id"] == "R12")
        loaded_codes.update(
            need["need_code"] for need in r12["metrics"]["evidence_needs"]
        )

    screening_codes = Counter(
        need["code"]
        for record in iter_screening_records()
        for need in record["evidence_needs"]
    )
    frozen_codes = set(loaded_codes) | set(screening_codes)
    validate_frozen_need_codes(frozen_codes)

    assert frozen_codes == set(KNOWN_MAPPING)
    assert all(
        classify_need_code(code) is not DatasetKind.UNMAPPED
        for code in frozen_codes
    )
