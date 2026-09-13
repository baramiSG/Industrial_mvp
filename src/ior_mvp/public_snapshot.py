"""Fail-closed PublicSnapshot 2.1 and 2.2 validation."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

from .config import PROJECT_ROOT, sector_profiles_config
from .evidence import EvidenceIntegrityError
from .public_decision import SUPPORT_CODES


LEGACY_PUBLIC_SNAPSHOT_SCHEMA_VERSION_2_1 = "2.1.0"
PUBLIC_SNAPSHOT_SCHEMA_VERSION = "2.2.0"
SUPPORTED_PUBLIC_SNAPSHOT_SCHEMA_VERSIONS = frozenset(
    {
        LEGACY_PUBLIC_SNAPSHOT_SCHEMA_VERSION_2_1,
        PUBLIC_SNAPSHOT_SCHEMA_VERSION,
    }
)
PARTNER_DETAIL_OBSERVED = "PARTNER_DETAIL_OBSERVED"
PARTNER_DETAIL_MISSING = "PARTNER_DETAIL_MISSING"
PARTNER_TRADE_OBSERVED_ZERO = "PARTNER_TRADE_OBSERVED_ZERO"
PARTNER_DETAIL_STATES = frozenset(
    {
        PARTNER_DETAIL_OBSERVED,
        PARTNER_DETAIL_MISSING,
        PARTNER_TRADE_OBSERVED_ZERO,
    }
)
# Kept local so the runtime public-snapshot validator does not import the
# acquisition package. A test pins equality with UnavailableReason plus the
# two projection-only states.
PARTNER_DETAIL_MISSING_REASONS = frozenset(
    {
        "CREDENTIAL_ABSENT",
        "ENDPOINT_UNVERIFIED",
        "NETWORK_ERROR",
        "HTTP_ERROR",
        "RATE_LIMITED",
        "MAX_REQUESTS_EXHAUSTED",
        "LICENSE_UNRECORDED",
        "LICENSE_NOT_PERMITTED",
        "PAID_ACCESS_REQUIRED",
        "SIZE_BUDGET_EXCEEDED",
        "FORMAT_NOT_PARSEABLE",
        "COUNT_MISMATCH",
        "RECORD_CAP_REACHED",
        "COVERAGE_INDETERMINATE",
        "COVERAGE_INCOMPLETE",
        "NO_UNITS_IN_STORE",
        "REPORTER_MISMATCH",
        "OUT_OF_SCOPE_CONTENT",
        "OPERATOR_DISABLED",
        "NOT_ACQUIRED",
        "REVISION_MISMATCH",
    }
)
UNAVAILABLE = "UNAVAILABLE"
HISTORICAL_V1_DIRECTORY = PurePosixPath(
    "data/snapshots/public/historical/v1"
)
DISCLOSED_RATIO_ABSOLUTE_TOLERANCE = 5 / 100
CALCULATION_TOLERANCE = 1 / 1_000_000

_FORBIDDEN_RULE_KEYS = frozenset(
    {
        "rule_context",
        "rules",
        "rule_id",
        "rule_result",
        "rule_outcomes",
        "fired",
        "execution",
        "decision_effect",
    }
)
_FORBIDDEN_DECISION_KEYS = frozenset(
    {
        "public_decision_contract",
        "screening_disposition",
        "gap_class",
        "narrative",
        "localized_narrative",
        "narrative_version",
        "missing_facts",
        "conditions",
        "kill_conditions",
        "route_hypotheses",
        "preferred_hypothesis",
        "rejection_conditions",
    }
)
_ROOT_DECISION_KEYS = _FORBIDDEN_DECISION_KEYS | {
    "state",
    "route_code",
    "route_label",
}
_EVIDENCE_CLASSES = frozenset({"A", "B", "C", "D", "E"})
_EVIDENCE_STATUSES = frozenset(
    {
        "observed",
        "calculated",
        "model_estimated",
        "inferred",
        "assumption",
        "unresolved",
        "synthetic",
    }
)
_SIGNAL_TYPES = frozenset(
    {
        "matching_feedstock",
        "core_process",
        "equipment",
        "adjacent_output",
        "relevant_certification",
        "imported_inputs",
    }
)


class PublicSnapshotIntegrityError(EvidenceIntegrityError):
    """A live public snapshot violates the governed schema-v2 contract."""


def _fail(field: str, message: str) -> None:
    raise PublicSnapshotIntegrityError(f"{field}: {message}")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(field, "must be an object")
    return value


def _exact_keys(
    value: Any,
    field: str,
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, Any]:
    mapping = _mapping(value, field)
    optional = optional or set()
    missing = sorted(required - set(mapping))
    extra = sorted(set(mapping) - required - optional)
    if missing:
        _fail(field, f"missing required key(s): {', '.join(missing)}")
    if extra:
        _fail(field, f"unexpected key(s): {', '.join(extra)}")
    return mapping


def _reject_authored_outcomes(value: Any, field: str = "snapshot") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if field == "snapshot" and key == "partner_detail":
                # PublicSnapshot 2.2 uses a typed evidence-state field. Its
                # exact-key validator below prevents decision fields from
                # being smuggled into this block.
                continue
            if key in _FORBIDDEN_RULE_KEYS:
                _fail(
                    f"{field}.{key}",
                    "authored rule outcome keys are forbidden",
                )
            if key in _FORBIDDEN_DECISION_KEYS:
                _fail(
                    f"{field}.{key}",
                    "authored decision outcome keys are forbidden",
                )
            _reject_authored_outcomes(nested, f"{field}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_authored_outcomes(
                nested,
                f"{field}[{index}]",
            )


def _nonempty_string(
    value: Any,
    field: str,
    *,
    unavailable: bool = False,
) -> str:
    if unavailable and value == UNAVAILABLE:
        return UNAVAILABLE
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
    ):
        _fail(field, "must be a non-empty trimmed string")
    return value


def _iso_date(value: Any, field: str) -> str:
    text = _nonempty_string(value, field)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise PublicSnapshotIntegrityError(
            f"{field}: must be an ISO date"
        ) from exc
    if parsed.isoformat() != text:
        _fail(field, "must use canonical YYYY-MM-DD form")
    return text


def _number(
    value: Any,
    field: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    positive: bool = False,
    unavailable: bool = False,
    null: bool = False,
) -> float | None | str:
    if unavailable and value == UNAVAILABLE:
        return UNAVAILABLE
    if null and value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        suffix = f" or {UNAVAILABLE}" if unavailable else ""
        _fail(field, f"must be a finite number{suffix}")
    number = float(value)
    if not math.isfinite(number):
        _fail(field, "must be a finite number")
    if positive and number <= 0:
        _fail(field, "must be positive")
    if minimum is not None and number < minimum:
        _fail(field, f"must be at least {minimum:g}")
    if maximum is not None and number > maximum:
        _fail(field, f"must be at most {maximum:g}")
    return number


def _integer(
    value: Any,
    field: str,
    *,
    minimum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(field, "must be an integer")
    if minimum is not None and value < minimum:
        _fail(field, f"must be at least {minimum}")
    return value


def _string_list(
    value: Any,
    field: str,
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        _fail(field, "must be a list of strings")
    if nonempty and not value:
        _fail(field, "must not be empty")
    for index, item in enumerate(value):
        _nonempty_string(item, f"{field}[{index}]")
    return value


def _evidence_passports(
    value: Any,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        _fail("evidence", "must be a non-empty list")
    passports: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    keys = {
        "evidence_id",
        "title",
        "source",
        "url",
        "period",
        "retrieved_at",
        "status",
        "evidence_class",
        "synthetic_flag",
        "supports",
        "transformation",
        "reviewer_status",
        "contradiction",
    }
    for index, item in enumerate(value):
        field = f"evidence[{index}]"
        passport = _exact_keys(
            item,
            field,
            required=keys,
        )
        evidence_id = _nonempty_string(
            passport["evidence_id"],
            f"{field}.evidence_id",
        )
        if evidence_id in by_id:
            _fail(f"{field}.evidence_id", f"duplicate ID {evidence_id}")
        for key in (
            "title",
            "source",
            "url",
            "reviewer_status",
        ):
            _nonempty_string(passport[key], f"{field}.{key}")
        _nonempty_string(
            passport["period"],
            f"{field}.period",
            unavailable=True,
        )
        _iso_date(passport["retrieved_at"], f"{field}.retrieved_at")
        if passport["status"] not in _EVIDENCE_STATUSES:
            _fail(f"{field}.status", "is not an allowed evidence status")
        if passport["evidence_class"] not in _EVIDENCE_CLASSES:
            _fail(f"{field}.evidence_class", "must be A, B, C, D, or E")
        if passport["synthetic_flag"] is not False:
            _fail(f"{field}.synthetic_flag", "must be false")
        supports = _string_list(
            passport["supports"],
            f"{field}.supports",
            nonempty=True,
        )
        if len(supports) != len(set(supports)):
            _fail(f"{field}.supports", "contains a duplicate support code")
        unknown_supports = sorted(set(supports) - SUPPORT_CODES)
        if unknown_supports:
            _fail(
                f"{field}.supports",
                "contains unknown controlled support code(s): "
                + ", ".join(unknown_supports),
            )
        _nonempty_string(
            passport["transformation"],
            f"{field}.transformation",
            unavailable=True,
        )
        contradiction = passport["contradiction"]
        if contradiction is not None:
            _nonempty_string(contradiction, f"{field}.contradiction")
        passports.append(passport)
        by_id[evidence_id] = passport
    return passports, by_id


def _evidence_references(
    value: Any,
    field: str,
    evidence_ids: set[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    references = _string_list(value, field, nonempty=nonempty)
    for evidence_id in references:
        if evidence_id not in evidence_ids:
            _fail(field, f"unresolved evidence ID {evidence_id}")
    return references


def _validate_opportunity(
    value: Any,
    snapshot_date: str,
) -> dict[str, Any]:
    opportunity = _exact_keys(
        value,
        "opportunity",
        required={
            "id",
            "hs_revision",
            "hs6",
            "national_tariff_line",
            "sector_profile",
            "commercial_name_en",
            "commercial_name_ar",
            "decision_object_status",
            "application_boundary",
            "as_of_date",
        },
    )
    for key in (
        "id",
        "hs_revision",
        "hs6",
        "sector_profile",
        "commercial_name_en",
        "commercial_name_ar",
        "decision_object_status",
        "application_boundary",
    ):
        _nonempty_string(opportunity[key], f"opportunity.{key}")
    _nonempty_string(
        opportunity["national_tariff_line"],
        "opportunity.national_tariff_line",
        unavailable=True,
    )
    opportunity_date = _iso_date(
        opportunity["as_of_date"],
        "opportunity.as_of_date",
    )
    if opportunity_date != snapshot_date:
        _fail("opportunity.as_of_date", "must match snapshot as_of_date")
    return opportunity


_TRADE_REQUIRED_KEYS = {
    "year",
    "imports_usd_m",
    "imports_kt",
    "exports_usd_m",
    "exports_kt",
}
_TRADE_OPTIONAL_KEYS = {
    "import_uv_usd_t",
    "export_uv_usd_t",
    "gross_net_usd_m",
    "gross_net_kt",
    "export_import_value_ratio",
}


def _known_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _validate_trade(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _fail("trade", "must be a non-empty list")
    years: set[int] = set()
    for index, item in enumerate(value):
        field = f"trade[{index}]"
        row = _exact_keys(
            item,
            field,
            required=_TRADE_REQUIRED_KEYS,
            optional=_TRADE_OPTIONAL_KEYS,
        )
        year = _integer(row["year"], f"{field}.year", minimum=1)
        if year in years:
            _fail(f"{field}.year", f"duplicate trade year {year}")
        years.add(year)
        for key in (
            "imports_usd_m",
            "imports_kt",
            "exports_usd_m",
            "exports_kt",
            "gross_net_usd_m",
            "gross_net_kt",
        ):
            if key in row:
                _number(
                    row[key],
                    f"{field}.{key}",
                    minimum=0,
                    unavailable=True,
                    null=True,
                )
        for key in ("import_uv_usd_t", "export_uv_usd_t"):
            if key in row:
                _number(
                    row[key],
                    f"{field}.{key}",
                    positive=True,
                    unavailable=True,
                    null=True,
                )
        if "export_import_value_ratio" in row:
            disclosed = _number(
                row["export_import_value_ratio"],
                f"{field}.export_import_value_ratio",
                positive=True,
            )
            imports = _known_number(row["imports_usd_m"])
            exports = _known_number(row["exports_usd_m"])
            if imports is not None and exports is not None and imports > 0:
                computed = exports / imports
                assert isinstance(disclosed, float)
                if (
                    abs(disclosed - computed)
                    > DISCLOSED_RATIO_ABSOLUTE_TOLERANCE
                ):
                    _fail(
                        f"{field}.export_import_value_ratio",
                        (
                            "is inconsistent with exports_usd_m / "
                            "imports_usd_m"
                        ),
                    )
    return value


def _validate_trade_quality(value: Any) -> dict[str, Any]:
    quality = _exact_keys(
        value,
        "trade_quality",
        required={
            "flow_basis",
            "reexports_separated",
            "domestic_origin_exports_separated",
            "missing_years",
            "monthly_partner_tariff_line_available",
            "quantity_comparable",
            "execution_cap",
        },
    )
    if quality["flow_basis"] != "gross":
        _fail("trade_quality.flow_basis", "must equal gross")
    for key in (
        "reexports_separated",
        "domestic_origin_exports_separated",
        "monthly_partner_tariff_line_available",
        "quantity_comparable",
    ):
        if not isinstance(quality[key], bool):
            _fail(f"trade_quality.{key}", "must be boolean")
    if not isinstance(quality["missing_years"], list):
        _fail("trade_quality.missing_years", "must be a list")
    seen: set[int] = set()
    for index, item in enumerate(quality["missing_years"]):
        year = _integer(
            item,
            f"trade_quality.missing_years[{index}]",
            minimum=1,
        )
        if year in seen:
            _fail("trade_quality.missing_years", f"duplicate year {year}")
        seen.add(year)
    _nonempty_string(
        quality["execution_cap"],
        "trade_quality.execution_cap",
    )
    return quality


def _validate_partner_observations(
    value: Any,
    evidence_ids: set[str],
) -> None:
    if value == UNAVAILABLE:
        return
    if not isinstance(value, list) or not value:
        _fail(
            "partner_observations",
            f"must be {UNAVAILABLE} or a non-empty list",
        )
    identities: set[tuple[int, str, str]] = set()
    required = {
        "year",
        "partner",
        "flow",
        "trade_value_usd_m",
        "net_weight_kt",
        "quantity_unit",
        "validity_flags",
        "gross_flow",
        "source_evidence_id",
    }
    for index, item in enumerate(value):
        field = f"partner_observations[{index}]"
        row = _exact_keys(item, field, required=required)
        year = _integer(row["year"], f"{field}.year", minimum=1)
        partner = _nonempty_string(row["partner"], f"{field}.partner")
        flow = row["flow"]
        if flow not in {"imports", "exports"}:
            _fail(f"{field}.flow", "must be imports or exports")
        identity = (year, partner, flow)
        if identity in identities:
            _fail(field, f"duplicate partner observation {identity}")
        identities.add(identity)
        value_number = _number(
            row["trade_value_usd_m"],
            f"{field}.trade_value_usd_m",
            minimum=0,
            unavailable=True,
        )
        weight_number = _number(
            row["net_weight_kt"],
            f"{field}.net_weight_kt",
            minimum=0,
            unavailable=True,
        )
        if row["quantity_unit"] not in {"kt", UNAVAILABLE}:
            _fail(
                f"{field}.quantity_unit",
                f"must be kt or {UNAVAILABLE}",
            )
        flags = _exact_keys(
            row["validity_flags"],
            f"{field}.validity_flags",
            required={
                "value_valid",
                "net_weight_valid",
                "quantity_comparable",
            },
        )
        for key in (
            "value_valid",
            "net_weight_valid",
            "quantity_comparable",
        ):
            if not isinstance(flags[key], bool):
                _fail(f"{field}.validity_flags.{key}", "must be boolean")
        if flags["value_valid"] and value_number == UNAVAILABLE:
            _fail(
                f"{field}.validity_flags.value_valid",
                "requires numeric trade_value_usd_m",
            )
        if flags["net_weight_valid"] and weight_number == UNAVAILABLE:
            _fail(
                f"{field}.validity_flags.net_weight_valid",
                "requires numeric net_weight_kt",
            )
        if (
            flags["quantity_comparable"]
            and row["quantity_unit"] != "kt"
        ):
            _fail(
                f"{field}.validity_flags.quantity_comparable",
                "requires quantity_unit kt",
            )
        if not isinstance(row["gross_flow"], bool):
            _fail(f"{field}.gross_flow", "must be boolean")
        source_id = _nonempty_string(
            row["source_evidence_id"],
            f"{field}.source_evidence_id",
        )
        if source_id not in evidence_ids:
            _fail(
                f"{field}.source_evidence_id",
                f"unresolved evidence ID {source_id}",
            )


def _validate_partner_detail(
    value: Any,
    *,
    partner_observations: Any,
    evidence_by_id: dict[str, dict[str, Any]],
    opportunity_hs6: str,
) -> None:
    detail = _exact_keys(
        value,
        "partner_detail",
        required={
            "state",
            "reason",
            "source_id",
            "partner_snapshot_id",
            "unit_key",
            "observed_partner_rows",
            "attempt_passport_ids",
            "observed_passport_id",
        },
    )
    state = detail["state"]
    if state not in PARTNER_DETAIL_STATES:
        _fail(
            "partner_detail.state",
            "must be a governed partner-detail state",
        )
    reason = detail["reason"]
    if state == PARTNER_DETAIL_MISSING:
        if reason not in PARTNER_DETAIL_MISSING_REASONS:
            _fail(
                "partner_detail.reason",
                "must be a governed missing-data reason",
            )
    elif reason is not None:
        _fail(
            "partner_detail.reason",
            "must be null unless state is PARTNER_DETAIL_MISSING",
        )

    source_id = _nonempty_string(
        detail["source_id"],
        "partner_detail.source_id",
        unavailable=True,
    )
    if source_id not in {"un_comtrade", "wits_trade", UNAVAILABLE}:
        _fail(
            "partner_detail.source_id",
            "must be un_comtrade, wits_trade or UNAVAILABLE",
        )
    _nonempty_string(
        detail["partner_snapshot_id"],
        "partner_detail.partner_snapshot_id",
        unavailable=True,
    )
    unit_key = detail["unit_key"]
    if unit_key != [opportunity_hs6, "imports", "2024"]:
        _fail(
            "partner_detail.unit_key",
            "must equal [opportunity.hs6, imports, 2024]",
        )

    observed_rows = detail["observed_partner_rows"]
    if state == PARTNER_DETAIL_OBSERVED:
        _integer(
            observed_rows,
            "partner_detail.observed_partner_rows",
            minimum=1,
        )
    elif state == PARTNER_TRADE_OBSERVED_ZERO:
        if observed_rows != 0 or isinstance(observed_rows, bool):
            _fail(
                "partner_detail.observed_partner_rows",
                "must equal 0 for PARTNER_TRADE_OBSERVED_ZERO",
            )
    elif observed_rows != UNAVAILABLE:
        _fail(
            "partner_detail.observed_partner_rows",
            "must equal UNAVAILABLE for PARTNER_DETAIL_MISSING",
        )

    attempts = detail["attempt_passport_ids"]
    if not isinstance(attempts, list):
        _fail(
            "partner_detail.attempt_passport_ids",
            "must be a list",
        )
    if any(
        not isinstance(attempt_id, str)
        or not attempt_id
        or attempt_id.strip() != attempt_id
        for attempt_id in attempts
    ):
        _fail(
            "partner_detail.attempt_passport_ids",
            "must contain non-empty trimmed evidence IDs",
        )
    if len(attempts) != len(set(attempts)):
        _fail(
            "partner_detail.attempt_passport_ids",
            "must not contain duplicates",
        )
    if (
        state == PARTNER_DETAIL_MISSING
        and reason != "NOT_ACQUIRED"
        and not attempts
    ):
        _fail(
            "partner_detail.attempt_passport_ids",
            "must name at least one attempt unless reason is NOT_ACQUIRED",
        )
    for index, attempt_id in enumerate(attempts):
        field = f"partner_detail.attempt_passport_ids[{index}]"
        attempt_id = _nonempty_string(attempt_id, field)
        passport = evidence_by_id.get(attempt_id)
        if passport is None:
            _fail(field, f"unresolved evidence ID {attempt_id}")
        if (
            passport.get("status") != "unresolved"
            or passport.get("synthetic_flag") is not False
        ):
            _fail(
                field,
                "must reference an unresolved public evidence passport",
            )
        transformation = passport.get("transformation")
        allowed_prefixes = ("PARTNER_DETAIL_MISSING:",)
        if state == PARTNER_DETAIL_OBSERVED:
            allowed_prefixes += (
                "PARTNER_DETAIL_ATTEMPT_SUPERSEDED:",
            )
        if not isinstance(transformation, str) or not transformation.startswith(
            allowed_prefixes
        ):
            _fail(
                f"{field}.transformation",
                "must carry a governed partner-detail attempt prefix",
            )

    observed_id = detail["observed_passport_id"]
    if state == PARTNER_DETAIL_MISSING:
        if observed_id is not None:
            _fail(
                "partner_detail.observed_passport_id",
                "must be null for PARTNER_DETAIL_MISSING",
            )
    else:
        observed_id = _nonempty_string(
            observed_id,
            "partner_detail.observed_passport_id",
        )
        passport = evidence_by_id.get(observed_id)
        if passport is None:
            _fail(
                "partner_detail.observed_passport_id",
                f"unresolved evidence ID {observed_id}",
            )
        expected_status = (
            "calculated"
            if state == PARTNER_DETAIL_OBSERVED
            else "observed"
        )
        if (
            passport.get("status") != expected_status
            or passport.get("synthetic_flag") is not False
        ):
            _fail(
                "partner_detail.observed_passport_id",
                f"must reference a public {expected_status} passport",
            )
        if (
            state == PARTNER_TRADE_OBSERVED_ZERO
            and not observed_id.endswith("-PARTNERS-ZERO")
        ):
            _fail(
                "partner_detail.observed_passport_id",
                "zero-state passport ID must end -PARTNERS-ZERO",
            )

    if isinstance(partner_observations, list):
        if state != PARTNER_DETAIL_OBSERVED:
            _fail(
                "partner_detail.state",
                "partner rows require PARTNER_DETAIL_OBSERVED",
            )
        if observed_rows != len(partner_observations):
            _fail(
                "partner_detail.observed_partner_rows",
                "must equal the partner-observation row count",
            )
        if any(
            row.get("source_evidence_id") != observed_id
            for row in partner_observations
            if isinstance(row, dict)
        ):
            _fail(
                "partner_observations.source_evidence_id",
                "must equal partner_detail.observed_passport_id",
            )
    elif partner_observations == UNAVAILABLE:
        if state not in {
            PARTNER_DETAIL_MISSING,
            PARTNER_TRADE_OBSERVED_ZERO,
        }:
            _fail(
                "partner_detail.state",
                "UNAVAILABLE partner rows require MISSING or ZERO state",
            )
    else:
        _fail(
            "partner_detail",
            "requires partner_observations",
        )


def _unavailable_or_share(value: Any, field: str) -> float | str:
    result = _number(
        value,
        field,
        minimum=0,
        maximum=1,
        unavailable=True,
    )
    assert isinstance(result, (float, str))
    return result


def _validate_disclosed_concentration(
    value: Any,
    evidence_ids: set[str],
) -> None:
    concentration = _exact_keys(
        value,
        "disclosed_concentration",
        required={"value", "quantity"},
    )
    required = {
        "year",
        "flow",
        "flow_basis",
        "basis",
        "hhi",
        "largest_supplier_share",
        "top_two_share",
        "top_two_suppliers",
        "source_evidence_id",
        "status",
    }
    for basis in ("value", "quantity"):
        item = concentration[basis]
        if item == UNAVAILABLE:
            continue
        field = f"disclosed_concentration.{basis}"
        disclosure = _exact_keys(item, field, required=required)
        _integer(disclosure["year"], f"{field}.year", minimum=1)
        if disclosure["flow"] not in {"imports", "exports"}:
            _fail(f"{field}.flow", "must be imports or exports")
        if disclosure["flow_basis"] not in {"gross", "retained"}:
            _fail(f"{field}.flow_basis", "must be gross or retained")
        if disclosure["basis"] != basis:
            _fail(f"{field}.basis", f"must equal {basis}")
        _unavailable_or_share(disclosure["hhi"], f"{field}.hhi")
        _unavailable_or_share(
            disclosure["largest_supplier_share"],
            f"{field}.largest_supplier_share",
        )
        _unavailable_or_share(
            disclosure["top_two_share"],
            f"{field}.top_two_share",
        )
        suppliers = disclosure["top_two_suppliers"]
        if suppliers != UNAVAILABLE:
            _string_list(
                suppliers,
                f"{field}.top_two_suppliers",
                nonempty=True,
            )
        source_id = _nonempty_string(
            disclosure["source_evidence_id"],
            f"{field}.source_evidence_id",
        )
        if source_id not in evidence_ids:
            _fail(
                f"{field}.source_evidence_id",
                f"unresolved evidence ID {source_id}",
            )
        if disclosure["status"] != "calculated":
            _fail(f"{field}.status", "must equal calculated")


def _validate_unit_value_pair(value: Any, field: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        _fail(field, "must contain exactly two unit values")
    low = _number(value[0], f"{field}[0]", positive=True)
    high = _number(value[1], f"{field}[1]", positive=True)
    assert isinstance(low, float)
    assert isinstance(high, float)
    if low > high:
        _fail(field, "low value must not exceed high value")
    return [low, high]


def _validate_disclosed_dispersion(
    value: Any,
    evidence_ids: set[str],
) -> None:
    if value == UNAVAILABLE:
        return
    required = {
        "year",
        "basis",
        "flow_basis",
        "unit",
        "valid_value_coverage",
        "valid_quantity_coverage",
        "weighted_median_usd_t",
        "iqr_usd_t",
        "bulk_band_usd_t",
        "outlier_observation",
        "comparison_observations",
        "coverage_note",
        "source_evidence_id",
        "status",
    }
    disclosure = _exact_keys(
        value,
        "disclosed_dispersion",
        required=required,
    )
    _integer(disclosure["year"], "disclosed_dispersion.year", minimum=1)
    _nonempty_string(disclosure["basis"], "disclosed_dispersion.basis")
    if disclosure["flow_basis"] not in {"gross", "retained"}:
        _fail(
            "disclosed_dispersion.flow_basis",
            "must be gross or retained",
        )
    if disclosure["unit"] != "USD/t":
        _fail("disclosed_dispersion.unit", "must equal USD/t")
    for key in ("valid_value_coverage", "valid_quantity_coverage"):
        _unavailable_or_share(
            disclosure[key],
            f"disclosed_dispersion.{key}",
        )
    _number(
        disclosure["weighted_median_usd_t"],
        "disclosed_dispersion.weighted_median_usd_t",
        positive=True,
        unavailable=True,
    )
    _number(
        disclosure["iqr_usd_t"],
        "disclosed_dispersion.iqr_usd_t",
        minimum=0,
        unavailable=True,
    )
    band: list[float] | None = None
    if disclosure["bulk_band_usd_t"] != UNAVAILABLE:
        band = _validate_unit_value_pair(
            disclosure["bulk_band_usd_t"],
            "disclosed_dispersion.bulk_band_usd_t",
        )
    outlier = disclosure["outlier_observation"]
    if outlier != UNAVAILABLE:
        item = _exact_keys(
            outlier,
            "disclosed_dispersion.outlier_observation",
            required={"partner", "net_weight_kt", "unit_value_usd_t"},
        )
        _nonempty_string(
            item["partner"],
            "disclosed_dispersion.outlier_observation.partner",
        )
        _number(
            item["net_weight_kt"],
            "disclosed_dispersion.outlier_observation.net_weight_kt",
            positive=True,
        )
        unit_value = _number(
            item["unit_value_usd_t"],
            "disclosed_dispersion.outlier_observation.unit_value_usd_t",
            positive=True,
        )
        assert isinstance(unit_value, float)
        if band is not None and band[0] <= unit_value <= band[1]:
            _fail(
                "disclosed_dispersion.outlier_observation",
                "unit value must fall outside the supplied bulk band",
            )
    comparisons = disclosure["comparison_observations"]
    if comparisons != UNAVAILABLE:
        if not isinstance(comparisons, list) or not comparisons:
            _fail(
                "disclosed_dispersion.comparison_observations",
                f"must be {UNAVAILABLE} or a non-empty list",
            )
        for index, comparison in enumerate(comparisons):
            field = (
                "disclosed_dispersion.comparison_observations"
                f"[{index}]"
            )
            row = _exact_keys(
                comparison,
                field,
                required={"flow", "unit_value_usd_t"},
            )
            if row["flow"] not in {"imports", "exports"}:
                _fail(f"{field}.flow", "must be imports or exports")
            _number(
                row["unit_value_usd_t"],
                f"{field}.unit_value_usd_t",
                positive=True,
            )
    _nonempty_string(
        disclosure["coverage_note"],
        "disclosed_dispersion.coverage_note",
    )
    source_id = _nonempty_string(
        disclosure["source_evidence_id"],
        "disclosed_dispersion.source_evidence_id",
    )
    if source_id not in evidence_ids:
        _fail(
            "disclosed_dispersion.source_evidence_id",
            f"unresolved evidence ID {source_id}",
        )
    if disclosure["status"] != "calculated":
        _fail("disclosed_dispersion.status", "must equal calculated")


def _validate_domestic_flows(
    value: Any,
    trade: list[dict[str, Any]],
    evidence_ids: set[str],
) -> dict[str, Any]:
    flows = _exact_keys(
        value,
        "domestic_flows",
        required={
            "period_year",
            "domestic_production_kt",
            "retained_imports_kt",
            "domestic_origin_exports_kt",
            "reexports_kt",
            "source_evidence_ids",
        },
    )
    year = _integer(
        flows["period_year"],
        "domestic_flows.period_year",
        minimum=1,
    )
    values: dict[str, float | str] = {}
    for key in (
        "domestic_production_kt",
        "retained_imports_kt",
        "domestic_origin_exports_kt",
        "reexports_kt",
    ):
        parsed = _number(
            flows[key],
            f"domestic_flows.{key}",
            minimum=0,
            unavailable=True,
        )
        assert isinstance(parsed, (float, str))
        values[key] = parsed
    _evidence_references(
        flows["source_evidence_ids"],
        "domestic_flows.source_evidence_ids",
        evidence_ids,
    )
    trade_row = next(
        (row for row in trade if row["year"] == year),
        None,
    )
    reexports = values["reexports_kt"]
    retained = values["retained_imports_kt"]
    if isinstance(reexports, float):
        if trade_row is None:
            _fail(
                "domestic_flows.period_year",
                "has no matching aggregate trade row",
            )
        gross_imports = _known_number(trade_row.get("imports_kt"))
        if gross_imports is None:
            _fail(
                "domestic_flows.reexports_kt",
                "requires numeric aggregate imports_kt",
            )
        if reexports > gross_imports:
            _fail(
                "domestic_flows.reexports_kt",
                "cannot exceed gross imports",
            )
        if (
            isinstance(retained, float)
            and abs(retained - (gross_imports - reexports))
            > CALCULATION_TOLERANCE
        ):
            _fail(
                "domestic_flows.retained_imports_kt",
                "must equal gross imports minus reexports",
            )
    return flows


def _validate_criticality(
    value: Any,
    evidence_ids: set[str],
) -> None:
    if value == UNAVAILABLE:
        return
    designation = _exact_keys(
        value,
        "criticality_designation",
        required={"authority", "reference", "date", "evidence_id"},
    )
    for key in ("authority", "reference"):
        _nonempty_string(
            designation[key],
            f"criticality_designation.{key}",
        )
    _iso_date(
        designation["date"],
        "criticality_designation.date",
    )
    evidence_id = _nonempty_string(
        designation["evidence_id"],
        "criticality_designation.evidence_id",
    )
    if evidence_id not in evidence_ids:
        _fail(
            "criticality_designation.evidence_id",
            f"unresolved evidence ID {evidence_id}",
        )


def _validate_capability(
    value: Any,
    evidence_by_id: dict[str, dict[str, Any]],
    sector_profile: str,
) -> dict[str, Any]:
    capability = _exact_keys(
        value,
        "domestic_capability",
        required={
            "verified_present",
            "same_process_family",
            "coarse_adjacency_signals",
            "producer_evidence",
            "public_dimension_states",
            "profile_hard_gates",
            "unresolved_hard_gates",
        },
    )
    for key in ("verified_present", "same_process_family"):
        if capability[key] != UNAVAILABLE and not isinstance(
            capability[key],
            bool,
        ):
            _fail(
                f"domestic_capability.{key}",
                f"must be boolean or {UNAVAILABLE}",
            )
    evidence_ids = set(evidence_by_id)
    signals = capability["coarse_adjacency_signals"]
    if not isinstance(signals, list):
        _fail(
            "domestic_capability.coarse_adjacency_signals",
            "must be a list",
        )
    for index, item in enumerate(signals):
        field = f"domestic_capability.coarse_adjacency_signals[{index}]"
        signal = _exact_keys(
            item,
            field,
            required={"signal_type", "description", "evidence_ids"},
        )
        if signal["signal_type"] not in _SIGNAL_TYPES:
            _fail(f"{field}.signal_type", "is not allowed")
        _nonempty_string(signal["description"], f"{field}.description")
        _evidence_references(
            signal["evidence_ids"],
            f"{field}.evidence_ids",
            evidence_ids,
            nonempty=True,
        )

    producers = capability["producer_evidence"]
    if not isinstance(producers, list):
        _fail(
            "domestic_capability.producer_evidence",
            "must be a list",
        )
    required = {
        "producer",
        "process_family",
        "process_route",
        "published_standards",
        "installed_capacity_tpy",
        "nameplate_status",
        "nameplate_source_evidence_id",
        "evidence_class",
        "evidence_ids",
    }
    optional = {
        "published_coating_range_g_m2",
        "portfolio",
        "public_note",
    }
    for index, item in enumerate(producers):
        field = f"domestic_capability.producer_evidence[{index}]"
        producer = _exact_keys(
            item,
            field,
            required=required,
            optional=optional,
        )
        for key in ("producer", "process_family"):
            _nonempty_string(producer[key], f"{field}.{key}")
        _nonempty_string(
            producer["process_route"],
            f"{field}.process_route",
            unavailable=True,
        )
        standards = producer["published_standards"]
        if standards != UNAVAILABLE:
            _string_list(
                standards,
                f"{field}.published_standards",
                nonempty=True,
            )
        if producer["evidence_class"] not in _EVIDENCE_CLASSES:
            _fail(f"{field}.evidence_class", "must be A, B, C, D, or E")
        references = _evidence_references(
            producer["evidence_ids"],
            f"{field}.evidence_ids",
            evidence_ids,
            nonempty=True,
        )
        capacity = _number(
            producer["installed_capacity_tpy"],
            f"{field}.installed_capacity_tpy",
            positive=True,
            unavailable=True,
        )
        source_id = producer["nameplate_source_evidence_id"]
        if isinstance(capacity, float):
            if producer["nameplate_status"] != "observed":
                _fail(
                    f"{field}.nameplate_status",
                    "numeric nameplate requires observed",
                )
            if producer["evidence_class"] not in {"A", "B", "C"}:
                _fail(
                    f"{field}.evidence_class",
                    "observed nameplate requires Class A, B, or C",
                )
            _nonempty_string(source_id, f"{field}.nameplate_source_evidence_id")
            if source_id not in references or source_id not in evidence_by_id:
                _fail(
                    f"{field}.nameplate_source_evidence_id",
                    f"unresolved evidence ID {source_id}",
                )
            if evidence_by_id[source_id]["evidence_class"] not in {
                "A",
                "B",
                "C",
            }:
                _fail(
                    f"{field}.nameplate_source_evidence_id",
                    "must resolve to a Class A, B, or C passport",
                )
        else:
            if producer["nameplate_status"] != "unresolved":
                _fail(
                    f"{field}.nameplate_status",
                    f"{UNAVAILABLE} nameplate requires unresolved",
                )
            if source_id != UNAVAILABLE:
                _fail(
                    f"{field}.nameplate_source_evidence_id",
                    f"must be {UNAVAILABLE}",
                )
        if "published_coating_range_g_m2" in producer:
            coating = producer["published_coating_range_g_m2"]
            if coating != UNAVAILABLE:
                _validate_unit_value_pair(
                    coating,
                    f"{field}.published_coating_range_g_m2",
                )
        for key in ("portfolio", "public_note"):
            if key in producer:
                _nonempty_string(producer[key], f"{field}.{key}")

    states = _mapping(
        capability["public_dimension_states"],
        "domestic_capability.public_dimension_states",
    )
    if not states:
        _fail(
            "domestic_capability.public_dimension_states",
            "must not be empty",
        )
    for name, state in states.items():
        _nonempty_string(name, "domestic_capability.public_dimension_states key")
        if state == "U":
            continue
        if (
            isinstance(state, bool)
            or not isinstance(state, int)
            or not 0 <= state <= 3
        ):
            _fail(
                f"domestic_capability.public_dimension_states.{name}",
                "must be 0, 1, 2, 3, or U",
            )

    profiles = sector_profiles_config().get("profiles")
    if (
        not isinstance(profiles, dict)
        or sector_profile not in profiles
        or not isinstance(profiles[sector_profile], dict)
    ):
        _fail(
            "opportunity.sector_profile",
            f"unknown sector profile {sector_profile}",
        )
    expected_dimensions = set(
        profiles[sector_profile].get("weights", {})
    )
    if set(states) != expected_dimensions:
        _fail(
            "domestic_capability.public_dimension_states",
            "must exactly match the selected profile dimensions",
        )
    expected_profile_gates = list(
        profiles[sector_profile].get("hard_gates", [])
    )
    profile_gates = _mapping(
        capability["profile_hard_gates"],
        "domestic_capability.profile_hard_gates",
    )
    if set(profile_gates) != set(expected_profile_gates):
        _fail(
            "domestic_capability.profile_hard_gates",
            "must exactly match the selected profile hard gate set",
        )
    for name in expected_profile_gates:
        field = f"domestic_capability.profile_hard_gates.{name}"
        gate = _exact_keys(
            profile_gates[name],
            field,
            required={"status", "evidence_ids"},
        )
        status = gate["status"]
        if status not in {
            "RESOLVED",
            "UNAVAILABLE",
            "KNOWN_FAILURE",
        }:
            _fail(
                f"{field}.status",
                "must be RESOLVED, UNAVAILABLE, or KNOWN_FAILURE",
            )
        references = _evidence_references(
            gate["evidence_ids"],
            f"{field}.evidence_ids",
            evidence_ids,
        )
        if status == "UNAVAILABLE" and references:
            _fail(
                f"{field}.evidence_ids",
                "must be empty when status is UNAVAILABLE",
            )
        if status in {"RESOLVED", "KNOWN_FAILURE"}:
            if not references:
                _fail(
                    f"{field}.evidence_ids",
                    f"must not be empty when status is {status}",
                )
            if any(
                evidence_by_id[evidence_id]["evidence_class"]
                not in {"A", "B", "C"}
                for evidence_id in references
            ):
                _fail(
                    f"{field}.evidence_ids",
                    "must resolve to Class A, B, or C evidence",
                )

    gates = capability["unresolved_hard_gates"]
    if not isinstance(gates, list):
        _fail(
            "domestic_capability.unresolved_hard_gates",
            "must be a list",
        )
    names: set[str] = set()
    for index, item in enumerate(gates):
        field = f"domestic_capability.unresolved_hard_gates[{index}]"
        gate = _exact_keys(
            item,
            field,
            required={"name", "state", "evidence_ids"},
        )
        name = _nonempty_string(gate["name"], f"{field}.name")
        if name in names:
            _fail(f"{field}.name", f"duplicate hard gate {name}")
        names.add(name)
        if gate["state"] not in {"unresolved", "known_failure"}:
            _fail(
                f"{field}.state",
                "must be unresolved or known_failure",
            )
        references = _evidence_references(
            gate["evidence_ids"],
            f"{field}.evidence_ids",
            evidence_ids,
        )
        if gate["state"] == "known_failure":
            if not references:
                _fail(
                    f"{field}.evidence_ids",
                    "known_failure requires evidence",
                )
            if any(
                evidence_by_id[evidence_id]["evidence_class"]
                not in {"A", "B", "C"}
                for evidence_id in references
            ):
                _fail(
                    f"{field}.evidence_ids",
                    "known_failure requires Class A, B, or C evidence",
                )
    return capability


def _boolean_or_unavailable(value: Any, field: str) -> None:
    if value != UNAVAILABLE and not isinstance(value, bool):
        _fail(field, f"must be boolean or {UNAVAILABLE}")


def _validate_hard_exclusion_inputs(
    value: Any,
    evidence_ids: set[str],
) -> None:
    blocks = _exact_keys(
        value,
        "hard_exclusion_inputs",
        required={
            "heterogeneous_residual_code",
            "downside_market_below_mes",
            "unsatisfiable_hard_gate",
            "idle_equivalent_domestic_capacity",
            "transitory_or_measurement_gap",
            "redundancy_or_crowd_out",
        },
    )

    def block(
        name: str,
        fields: set[str],
    ) -> dict[str, Any]:
        item = _exact_keys(
            blocks[name],
            f"hard_exclusion_inputs.{name}",
            required={*fields, "evidence_ids"},
        )
        _evidence_references(
            item["evidence_ids"],
            f"hard_exclusion_inputs.{name}.evidence_ids",
            evidence_ids,
        )
        return item

    heterogeneous = block(
        "heterogeneous_residual_code",
        {
            "commercial_product_separable",
            "product_level_evidence_available",
        },
    )
    for key in (
        "commercial_product_separable",
        "product_level_evidence_available",
    ):
        _boolean_or_unavailable(
            heterogeneous[key],
            f"hard_exclusion_inputs.heterogeneous_residual_code.{key}",
        )

    market = block(
        "downside_market_below_mes",
        {
            "sustainable_downside_demand_kt",
            "minimum_efficient_scale_kt",
            "credible_export_contract",
        },
    )
    for key in (
        "sustainable_downside_demand_kt",
        "minimum_efficient_scale_kt",
    ):
        _number(
            market[key],
            f"hard_exclusion_inputs.downside_market_below_mes.{key}",
            minimum=0,
            unavailable=True,
        )
    _boolean_or_unavailable(
        market["credible_export_contract"],
        (
            "hard_exclusion_inputs.downside_market_below_mes."
            "credible_export_contract"
        ),
    )

    gate = block(
        "unsatisfiable_hard_gate",
        {"gate_domain", "gate_satisfiability"},
    )
    if gate["gate_domain"] not in {
        "legal",
        "safety",
        "environmental",
        "ip",
        "customer_qualification",
        UNAVAILABLE,
    }:
        _fail(
            "hard_exclusion_inputs.unsatisfiable_hard_gate.gate_domain",
            "is not an allowed gate_domain",
        )
    if gate["gate_satisfiability"] not in {
        "SATISFIABLE",
        "UNSATISFIABLE",
        UNAVAILABLE,
    }:
        _fail(
            (
                "hard_exclusion_inputs.unsatisfiable_hard_gate."
                "gate_satisfiability"
            ),
            "is not an allowed gate_satisfiability",
        )

    idle = block(
        "idle_equivalent_domestic_capacity",
        {
            "domestic_specification_equivalent",
            "qualified_idle_capacity_kt",
            "target_specification_demand_kt",
            "binding_market_failure",
        },
    )
    for key in (
        "domestic_specification_equivalent",
        "binding_market_failure",
    ):
        _boolean_or_unavailable(
            idle[key],
            (
                "hard_exclusion_inputs.idle_equivalent_domestic_capacity."
                f"{key}"
            ),
        )
    for key in (
        "qualified_idle_capacity_kt",
        "target_specification_demand_kt",
    ):
        _number(
            idle[key],
            (
                "hard_exclusion_inputs.idle_equivalent_domestic_capacity."
                f"{key}"
            ),
            minimum=0,
            unavailable=True,
        )

    transitory = block(
        "transitory_or_measurement_gap",
        {"dominant_cause"},
    )
    if transitory["dominant_cause"] not in {
        "REEXPORT",
        "ONE_OFF_PROJECT",
        "TEMPORARY_PRICE_ARBITRAGE",
        "CLASSIFICATION_DISCONTINUITY",
        "OTHER",
        UNAVAILABLE,
    }:
        _fail(
            (
                "hard_exclusion_inputs.transitory_or_measurement_gap."
                "dominant_cause"
            ),
            "is not an allowed dominant_cause",
        )

    competition = block(
        "redundancy_or_crowd_out",
        {"competition_finding"},
    )
    if competition["competition_finding"] not in {
        "ACCEPTABLE",
        "UNACCEPTABLE_REDUNDANT_CAPACITY",
        "UNACCEPTABLE_CROWD_OUT",
        UNAVAILABLE,
    }:
        _fail(
            (
                "hard_exclusion_inputs.redundancy_or_crowd_out."
                "competition_finding"
            ),
            "is not an allowed competition_finding",
        )


def _validate_decision_inputs(
    value: Any,
    evidence_by_id: dict[str, dict[str, Any]],
) -> None:
    evidence_ids = set(evidence_by_id)
    inputs = _exact_keys(
        value,
        "decision_inputs",
        required={
            "target_specification_demand",
            "specification_equivalence",
            "route_evidence",
            "monitor_trigger",
        },
    )
    target = inputs["target_specification_demand"]
    if target != UNAVAILABLE:
        item = _exact_keys(
            target,
            "decision_inputs.target_specification_demand",
            required={
                "quantity_kt",
                "downside_quantity_kt",
                "evidence_ids",
            },
        )
        for key in ("quantity_kt", "downside_quantity_kt"):
            _number(
                item[key],
                f"decision_inputs.target_specification_demand.{key}",
                minimum=0,
            )
        _evidence_references(
            item["evidence_ids"],
            "decision_inputs.target_specification_demand.evidence_ids",
            evidence_ids,
            nonempty=True,
        )

    equivalence = inputs["specification_equivalence"]
    if equivalence != UNAVAILABLE:
        item = _exact_keys(
            equivalence,
            "decision_inputs.specification_equivalence",
            required={
                "domestic_product_equivalent",
                "qualified_available_kt",
                "evidence_ids",
            },
        )
        if not isinstance(item["domestic_product_equivalent"], bool):
            _fail(
                (
                    "decision_inputs.specification_equivalence."
                    "domestic_product_equivalent"
                ),
                "must be boolean",
            )
        _number(
            item["qualified_available_kt"],
            (
                "decision_inputs.specification_equivalence."
                "qualified_available_kt"
            ),
            minimum=0,
        )
        _evidence_references(
            item["evidence_ids"],
            "decision_inputs.specification_equivalence.evidence_ids",
            evidence_ids,
            nonempty=True,
        )

    route_evidence = inputs["route_evidence"]
    if route_evidence != UNAVAILABLE:
        if not isinstance(route_evidence, list) or not route_evidence:
            _fail(
                "decision_inputs.route_evidence",
                f"must be {UNAVAILABLE} or a non-empty list",
            )
        route_codes: set[int] = set()
        allowed_constraints = {
            "specification_or_grade",
            "capacity_or_availability",
            "cost_or_competitiveness",
            "capability_or_technology",
            "qualification_or_certification",
            "commercial_or_relationship",
            "administrative_or_regulatory",
            "information_or_market_linkage",
            "demand_fragmentation_or_offtake",
        }
        required = {
            "route_code",
            "binding_constraint",
            "technical_feasibility_confirmed",
            "binding_constraint_fully_removed",
            "investment_already_approved_or_financed",
            "proceeds_without_intervention",
            "policy_prohibition_identified",
            "distortion_unacceptable",
            "intervention_proportionate_to_constraint",
            "downside_cash_flows_m_sar",
            "hurdle_rate",
            "national_value",
            "competition",
            "evidence_ids",
        }
        for index, route_value in enumerate(route_evidence):
            field = f"decision_inputs.route_evidence[{index}]"
            route = _exact_keys(
                route_value,
                field,
                required=required,
            )
            route_code = _integer(
                route["route_code"],
                f"{field}.route_code",
                minimum=1,
            )
            if route_code > 7 or route_code in route_codes:
                _fail(
                    f"{field}.route_code",
                    "must be a unique route code from 1 through 7",
                )
            route_codes.add(route_code)
            if route["binding_constraint"] not in allowed_constraints:
                _fail(
                    f"{field}.binding_constraint",
                    "is not an allowed binding_constraint",
                )
            for key in (
                "technical_feasibility_confirmed",
                "binding_constraint_fully_removed",
                "investment_already_approved_or_financed",
                "proceeds_without_intervention",
                "policy_prohibition_identified",
                "distortion_unacceptable",
                "intervention_proportionate_to_constraint",
            ):
                _boolean_or_unavailable(
                    route[key],
                    f"{field}.{key}",
                )
            flows = route["downside_cash_flows_m_sar"]
            if not isinstance(flows, list) or not flows:
                _fail(
                    f"{field}.downside_cash_flows_m_sar",
                    "must be a non-empty list",
                )
            for flow_index, flow in enumerate(flows):
                _number(
                    flow,
                    (
                        f"{field}.downside_cash_flows_m_sar"
                        f"[{flow_index}]"
                    ),
                )
            _number(
                route["hurdle_rate"],
                f"{field}.hurdle_rate",
                minimum=0,
            )
            national_value = _exact_keys(
                route["national_value"],
                f"{field}.national_value",
                required={
                    "domestic_value_added",
                    "exports",
                    "resilience_value",
                    "knowledge_skills",
                    "fiscal_receipts",
                    "government_cost",
                    "displacement",
                    "resource_environment",
                    "risk_allowance",
                },
            )
            for key, amount in national_value.items():
                _number(amount, f"{field}.national_value.{key}")
            competition = _exact_keys(
                route["competition"],
                f"{field}.competition",
                required={
                    "existing_effective_capacity_kt",
                    "proposed_incremental_capacity_kt",
                    "downside_demand_kt",
                },
            )
            for key, amount in competition.items():
                _number(
                    amount,
                    f"{field}.competition.{key}",
                    minimum=0,
                    positive=key == "downside_demand_kt",
                )
            references = _evidence_references(
                route["evidence_ids"],
                f"{field}.evidence_ids",
                evidence_ids,
                nonempty=True,
            )
            if any(
                evidence_by_id[evidence_id]["evidence_class"]
                not in {"A", "B", "C"}
                for evidence_id in references
            ):
                _fail(
                    f"{field}.evidence_ids",
                    "public route evidence must be Class A, B, or C",
                )
            route_supports = {
                support
                for evidence_id in references
                for support in evidence_by_id[evidence_id]["supports"]
            }
            required_supports = {
                "ROUTE_ECONOMICS",
                "ROUTE_NATIONAL_VALUE",
                "ROUTE_COMPETITION",
            }
            if not required_supports <= route_supports:
                _fail(
                    f"{field}.evidence_ids",
                    "public route evidence must cover economics, "
                    "national value, and competition",
                )

    trigger = inputs["monitor_trigger"]
    if trigger != UNAVAILABLE:
        item = _exact_keys(
            trigger,
            "decision_inputs.monitor_trigger",
            required={"domain", "condition_code", "evidence_ids"},
        )
        if item["domain"] not in {
            "demand",
            "regulation",
            "technology",
            "supplier_concentration",
            "capacity_state",
        }:
            _fail(
                "decision_inputs.monitor_trigger.domain",
                "is not an allowed monitor domain",
            )
        _nonempty_string(
            item["condition_code"],
            "decision_inputs.monitor_trigger.condition_code",
        )
        references = _evidence_references(
            item["evidence_ids"],
            "decision_inputs.monitor_trigger.evidence_ids",
            evidence_ids,
            nonempty=True,
        )
        if any(
            "MONITOR_TRIGGER"
            not in evidence_by_id[evidence_id]["supports"]
            for evidence_id in references
        ):
            _fail(
                "decision_inputs.monitor_trigger.evidence_ids",
                "must resolve to evidence supporting MONITOR_TRIGGER",
            )


def _validate_supersedes(
    record: dict[str, Any],
    opportunity: dict[str, Any],
    *,
    path: Path | None,
    root: Path,
) -> None:
    raw = _nonempty_string(record["supersedes"], "supersedes")
    if raw == UNAVAILABLE:
        return
    if "\\" in raw:
        _fail("supersedes", "must be a relative POSIX path")
    relative = PurePosixPath(raw)
    if relative.is_absolute():
        _fail("supersedes", "must be a relative path")
    if ".." in relative.parts:
        _fail("supersedes", "must not contain parent traversal")
    if relative.parent != HISTORICAL_V1_DIRECTORY:
        _fail(
            "supersedes",
            "must resolve under data/snapshots/public/historical/v1",
        )
    if relative.suffix != ".json":
        _fail("supersedes", "must reference a JSON file")
    root_resolved = root.resolve()
    target = (root / Path(*relative.parts)).resolve()
    if not target.is_relative_to(root_resolved):
        _fail("supersedes", "resolves outside the project root")
    if not target.is_file():
        _fail("supersedes", f"referenced file does not exist: {raw}")
    if path is not None and path.name != target.name:
        _fail("supersedes", "historical and live filenames must match")
    try:
        legacy = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublicSnapshotIntegrityError(
            "supersedes: historical v1 cannot be read"
        ) from exc
    if not isinstance(legacy, dict):
        _fail("supersedes", "historical v1 must be an object")
    comparisons = (
        ("snapshot_id", record["snapshot_id"], legacy.get("snapshot_id")),
        ("as_of_date", record["as_of_date"], legacy.get("as_of_date")),
        (
            "opportunity.id",
            opportunity["id"],
            (
                legacy.get("opportunity", {}).get("id")
                if isinstance(legacy.get("opportunity"), dict)
                else None
            ),
        ),
    )
    for field, current, previous in comparisons:
        if current != previous:
            _fail(
                f"supersedes.{field}",
                "does not match historical v1",
            )


def validate_public_snapshot(
    record: dict[str, Any],
    *,
    path: Path | None = None,
    root: Path = PROJECT_ROOT,
) -> None:
    """Validate PublicSnapshot 2.1 or 2.2 without mutating or coercing it."""
    _mapping(record, "snapshot")
    schema_version = record.get("schema_version")
    if schema_version not in SUPPORTED_PUBLIC_SNAPSHOT_SCHEMA_VERSIONS:
        _fail(
            "schema_version",
            "must be one of "
            + ", ".join(sorted(SUPPORTED_PUBLIC_SNAPSHOT_SCHEMA_VERSIONS)),
        )
    root_outcomes = sorted(set(record) & _ROOT_DECISION_KEYS)
    if root_outcomes:
        _fail(
            f"snapshot.{root_outcomes[0]}",
            "authored decision outcome keys are forbidden",
        )
    _reject_authored_outcomes(record)
    snapshot = _exact_keys(
        record,
        "snapshot",
        required={
            "schema_version",
            "snapshot_id",
            "as_of_date",
            "supersedes",
            "source_boundary",
            "authority_note",
            "opportunity",
            "trade",
            "trade_quality",
            "domestic_flows",
            "criticality_designation",
            "domestic_capability",
            "hard_exclusion_inputs",
            "decision_inputs",
            "evidence",
        },
        optional=(
            {
                "partner_observations",
                "disclosed_concentration",
                "disclosed_dispersion",
                "partner_detail",
            }
            if schema_version == PUBLIC_SNAPSHOT_SCHEMA_VERSION
            else {
                "partner_observations",
                "disclosed_concentration",
                "disclosed_dispersion",
            }
        ),
    )
    if snapshot["source_boundary"] != "public":
        _fail("source_boundary", "must equal public")
    _nonempty_string(snapshot["snapshot_id"], "snapshot_id")
    snapshot_date = _iso_date(snapshot["as_of_date"], "as_of_date")
    _nonempty_string(snapshot["authority_note"], "authority_note")
    opportunity = _validate_opportunity(
        snapshot["opportunity"],
        snapshot_date,
    )
    trade = _validate_trade(snapshot["trade"])
    _validate_trade_quality(snapshot["trade_quality"])
    _, evidence_by_id = _evidence_passports(snapshot["evidence"])
    evidence_ids = set(evidence_by_id)
    if "partner_observations" in snapshot:
        _validate_partner_observations(
            snapshot["partner_observations"],
            evidence_ids,
        )
    if schema_version == PUBLIC_SNAPSHOT_SCHEMA_VERSION:
        has_partner_layer = "partner_observations" in snapshot
        has_partner_detail = "partner_detail" in snapshot
        if has_partner_layer != has_partner_detail:
            _fail(
                "partner_detail",
                "must be present exactly when partner_observations is present",
            )
        if has_partner_detail:
            _validate_partner_detail(
                snapshot["partner_detail"],
                partner_observations=snapshot["partner_observations"],
                evidence_by_id=evidence_by_id,
                opportunity_hs6=opportunity["hs6"],
            )
    if "disclosed_concentration" in snapshot:
        _validate_disclosed_concentration(
            snapshot["disclosed_concentration"],
            evidence_ids,
        )
    if "disclosed_dispersion" in snapshot:
        _validate_disclosed_dispersion(
            snapshot["disclosed_dispersion"],
            evidence_ids,
        )
    _validate_domestic_flows(
        snapshot["domestic_flows"],
        trade,
        evidence_ids,
    )
    _validate_criticality(
        snapshot["criticality_designation"],
        evidence_ids,
    )
    _validate_capability(
        snapshot["domestic_capability"],
        evidence_by_id,
        opportunity["sector_profile"],
    )
    _validate_hard_exclusion_inputs(
        snapshot["hard_exclusion_inputs"],
        evidence_ids,
    )
    _validate_decision_inputs(
        snapshot["decision_inputs"],
        evidence_by_id,
    )
    _validate_supersedes(
        snapshot,
        opportunity,
        path=path,
        root=root,
    )


def capability_hard_gate_names(
    capability: dict[str, Any],
) -> list[str]:
    """Project typed unresolved/failed gates for the existing capability API."""
    gates = capability.get("unresolved_hard_gates")
    if not isinstance(gates, list):
        raise PublicSnapshotIntegrityError(
            "domestic_capability.unresolved_hard_gates: must be a list"
        )
    names: list[str] = []
    for index, item in enumerate(gates):
        if not isinstance(item, dict):
            raise PublicSnapshotIntegrityError(
                "domestic_capability.unresolved_hard_gates"
                f"[{index}]: must be an object"
            )
        name = item.get("name")
        state = item.get("state")
        if (
            not isinstance(name, str)
            or not name
            or state not in {"unresolved", "known_failure"}
        ):
            raise PublicSnapshotIntegrityError(
                "domestic_capability.unresolved_hard_gates"
                f"[{index}]: invalid typed hard gate"
            )
        names.append(name)
    return names


def has_known_hard_gate_failure(
    capability: dict[str, Any],
) -> bool:
    """Return whether any typed public hard gate is a known failure."""
    gates = capability.get("unresolved_hard_gates")
    if not isinstance(gates, list):
        raise PublicSnapshotIntegrityError(
            "domestic_capability.unresolved_hard_gates: must be a list"
        )
    decision_failure = any(
        isinstance(item, dict) and item.get("state") == "known_failure"
        for item in gates
    )
    profile_gates = capability.get("profile_hard_gates")
    profile_failure = (
        any(
            isinstance(item, dict)
            and item.get("status") == "KNOWN_FAILURE"
            for item in profile_gates.values()
        )
        if isinstance(profile_gates, dict)
        else False
    )
    return decision_failure or profile_failure
