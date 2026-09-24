"""Typed validation at executive projection extraction boundaries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from .taxonomy import ExecutiveIntegrityError


def mapping(value: object, field: str) -> Mapping[str, Any]:
    """Require a mapping without coercing malformed input.

    Args:
        value: Supplied projection input.
        field: Fixed, non-sensitive field label for an integrity error.

    Returns:
        The original mapping.

    Raises:
        ExecutiveIntegrityError: The value is not a mapping.
    """
    if not isinstance(value, Mapping):
        raise ExecutiveIntegrityError(f"{field} must be a mapping")
    return value


def mapping_rows(
    value: object, field: str, *, nonempty: bool = False,
) -> tuple[Mapping[str, Any], ...]:
    """Require a sequence containing mappings only.

    Args:
        value: Supplied row sequence.
        field: Fixed, non-sensitive field label for an integrity error.
        nonempty: Whether an empty sequence is invalid at this boundary.

    Returns:
        The validated rows as a tuple, retaining input order.

    Raises:
        ExecutiveIntegrityError: The sequence or a row is malformed.
    """
    if (not isinstance(value, Sequence) or isinstance(value, (str, bytes))
            or not all(isinstance(row, Mapping) for row in value)):
        raise ExecutiveIntegrityError(f"{field} must contain mappings")
    if nonempty and not value:
        raise ExecutiveIntegrityError(f"{field} must not be empty")
    return tuple(value)


def latest_trade(value: object) -> Mapping[str, Any]:
    """Select the latest trade row only after validating its year.

    Args:
        value: Supplied nonempty trade sequence.

    Returns:
        The original latest-year row; tied years retain input order.

    Raises:
        ExecutiveIntegrityError: Rows are missing or any year is not an integer.
    """
    rows = mapping_rows(value, "trade", nonempty=True)
    if any(type(row.get("year")) is not int for row in rows):
        raise ExecutiveIntegrityError("trade year must be an integer")
    return max(rows, key=lambda row: row["year"])


def finite_number(value: object, field: str) -> float:
    """Require a finite numeric value, excluding booleans and numeric strings.

    Args:
        value: Supplied numeric input or result.
        field: Fixed, non-sensitive field label for an integrity error.

    Returns:
        The number as a float, matching the existing response representation.

    Raises:
        ExecutiveIntegrityError: The value is not a finite number.
    """
    if type(value) not in (int, float):
        raise ExecutiveIntegrityError(f"{field} must be a finite number")
    try:
        number = float(value)
    except OverflowError:
        raise ExecutiveIntegrityError(f"{field} must be a finite number") from None
    if not isfinite(number):
        raise ExecutiveIntegrityError(f"{field} must be a finite number")
    return number
