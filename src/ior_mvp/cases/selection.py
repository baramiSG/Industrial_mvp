"""Versioned deterministic deep-case selection from frozen evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

import yaml

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.screening.snapshot import (
    load_screening_snapshot_directory,
    resolve_recorded_input,
)


SCHEMA_VERSION = "1.0.0"
RULE_ID = "S14-CS-1"
RULE_ID_V1_1 = "S14-CS-1.1"
RULE_VERSIONS = (RULE_ID, RULE_ID_V1_1)
_SCHEMA_BY_RULE = {
    RULE_ID: SCHEMA_VERSION,
    RULE_ID_V1_1: "1.1.0",
}
_PREFIX_BY_SCHEMA = {
    SCHEMA_VERSION: "CASE-SELECTION-S14-",
    "1.1.0": "CASE-SELECTION-S15-",
}
GENERIC_DISCLOSURE_TERMS = frozenset(
    {
        "bar",
        "film",
        "foil",
        "other",
        "pipe",
        "plate",
        "profile",
        "rod",
        "sheet",
        "strip",
        "tube",
    }
)
_TERM_KEYS = frozenset(
    {"hs6", "sector_profile", "sources", "terms", "basis"}
)
_EXCLUSION_KEYS = frozenset({"hs6", "reason", "basis"})
_EXCLUSION_V1_1_KEYS = frozenset(
    {
        "hs6",
        "reason",
        "hs_revision",
        "basis",
        "document_id",
        "page_index",
        "line_indices",
        "rule_version",
    }
)
_EXCLUSION_BASIS_KEYS = frozenset(
    {
        "parent_heading_text",
        "one_dash_group_text",
        "subheading_text",
        "identity_judgment",
    }
)
_EXCLUSION_QUOTE_KEYS = (
    "parent_heading_text",
    "one_dash_group_text",
    "subheading_text",
)
_GOVERNED_IDENTITY_REASONS = frozenset(
    {"RESIDUAL_CATCH_ALL_SUBHEADING"}
)
_OWNER_DESIGNATION_KEYS = frozenset(
    {"hs6", "reason", "ruling_reference"}
)
_HS4_PATTERN = re.compile(r"[0-9]{4}")
_PROFILE_ORDER = (
    "coated_steel",
    "fabricated_aluminium",
    "technical_plastics",
    "pharma_api",
    "fertilizers",
)


def canonical_bytes(record: Any) -> bytes:
    """Return the governed canonical JSON representation."""
    return (
        json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _canonical_compact(record: Any) -> bytes:
    return json.dumps(
        record,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_key(path: Path, root: Path = PROJECT_ROOT) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("selection input path must be inside repository") from exc
    return relative.as_posix()


def _json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain an object")
    return payload


def _yaml_object(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a mapping")
    return payload


def family_headings_by_profile(
    families: Mapping[str, Any],
) -> dict[str, tuple[str, ...]]:
    """Group the union of family HS4 headings by sector profile."""
    grouped: dict[str, set[str]] = {}
    family_rows = families.get("families")
    if not isinstance(family_rows, Mapping):
        raise ValueError("product families must contain a families mapping")
    for family_id, family in family_rows.items():
        if not isinstance(family, Mapping):
            raise ValueError(f"invalid product family: {family_id}")
        profile = family.get("sector_profile")
        headings = family.get("hs4_headings")
        if (
            not isinstance(profile, str)
            or not profile
            or not isinstance(headings, list)
            or any(
                not isinstance(heading, str)
                or _HS4_PATTERN.fullmatch(heading) is None
                for heading in headings
            )
        ):
            raise ValueError(f"invalid product family: {family_id}")
        grouped.setdefault(profile, set()).update(headings)
    return {
        profile: tuple(sorted(headings))
        for profile, headings in sorted(grouped.items())
    }


def queue_memberships(
    queues: Mapping[str, Any],
) -> dict[str, frozenset[str]]:
    """Return queue-id memberships as deterministic HS6 sets."""
    result: dict[str, frozenset[str]] = {}
    for queue_id, queue in queues.items():
        if not isinstance(queue_id, str) or not isinstance(queue, Mapping):
            raise ValueError("invalid queue block")
        entries = queue.get("entries")
        if not isinstance(entries, list):
            raise ValueError(f"queue {queue_id} entries must be a list")
        codes = []
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise ValueError(f"queue {queue_id} entry must be an object")
            code = entry.get("hs6")
            if not isinstance(code, str) or len(code) != 6 or not code.isdigit():
                raise ValueError(f"queue {queue_id} contains invalid HS6")
            codes.append(code)
        result[queue_id] = frozenset(codes)
    return result


def tier_of(
    record: Mapping[str, Any],
    memberships: Mapping[str, frozenset[str]],
) -> tuple[int, str]:
    """Apply the ruled PR-7 queue order and warning-class tiers."""
    hs6 = record.get("hs6")
    if not isinstance(hs6, str):
        raise ValueError("screening record HS6 missing")
    if record.get("screening_disposition") != "CANDIDATE":
        return 7, "NOT_SELECTABLE"
    if hs6 in memberships.get("robust_public_finding", frozenset()):
        return 1, "ROBUST_PUBLIC_FINDING"
    if hs6 in memberships.get(
        "high_evsi_evidence_investigation", frozenset()
    ):
        return 2, "HIGH_EVSI_EVIDENCE_INVESTIGATION"
    if hs6 in memberships.get("likely_false_positive", frozenset()):
        warnings = record.get("warnings")
        if not isinstance(warnings, Mapping):
            raise ValueError("likely-false-positive record warnings missing")
        if warnings.get("export_import_ratio_warning") is True:
            return 5, "EXPORT_IMPORT_RATIO_WARNING"
        if warnings.get("price_led_growth") is True:
            return 4, "PRICE_LED_GROWTH"
        continuity = warnings.get("classification_continuity")
        if not isinstance(continuity, Mapping) or continuity.get("status") not in {
            "REVISION_CHANGE_IN_WINDOW",
            "ABSENT_BEFORE_REVISION_CHANGE",
        }:
            raise ValueError(
                "tier-3 record must carry a classification-continuity warning"
            )
        return 3, "CLASSIFICATION_CONTINUITY_ONLY"
    return 6, "PERSISTENCE_ONLY"


def validate_terms_bundle(
    payload: Mapping[str, Any],
    *,
    expected_hs6: set[str] | None = None,
    rule_version: str | None = None,
) -> None:
    """Validate the governed HS6 disclosure-term bundle."""
    expected_rule = rule_version or payload.get("rule_id")
    if expected_rule not in RULE_VERSIONS:
        raise ValueError("disclosure terms rule version invalid")
    if set(payload) != {"schema_version", "rule_id", "rows"}:
        raise ValueError("disclosure terms top-level keys mismatch")
    if (
        payload.get("schema_version") != _SCHEMA_BY_RULE[expected_rule]
        or payload.get("rule_id") != expected_rule
    ):
        raise ValueError("disclosure terms identity mismatch")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("disclosure terms rows must be a list")
    codes: list[str] = []
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != _TERM_KEYS:
            raise ValueError("disclosure term row keys mismatch")
        hs6 = row.get("hs6")
        if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
            raise ValueError("disclosure term HS6 invalid")
        profile = row.get("sector_profile")
        if not isinstance(profile, str) or not profile:
            raise ValueError("disclosure term sector profile required")
        sources = row.get("sources")
        if (
            not isinstance(sources, list)
            or any(not isinstance(source, str) or not source for source in sources)
            or sources != sorted(set(sources))
        ):
            raise ValueError("disclosure term sources must be sorted and unique")
        terms = row.get("terms")
        if (
            not isinstance(terms, list)
            or not terms
            or any(not isinstance(term, str) or not term.strip() for term in terms)
            or terms != sorted(set(terms), key=str.casefold)
        ):
            raise ValueError("disclosure terms must be sorted and unique")
        if any(term.strip().casefold() in GENERIC_DISCLOSURE_TERMS for term in terms):
            raise ValueError("generic disclosure term is forbidden")
        if not isinstance(row.get("basis"), str) or not row["basis"].strip():
            raise ValueError("disclosure term basis required")
        codes.append(hs6)
    if codes != sorted(set(codes)):
        raise ValueError("disclosure term rows must be HS6-sorted and unique")
    if expected_hs6 is not None and set(codes) != expected_hs6:
        raise ValueError("disclosure term rows must cover every family HS6")


def _normalised_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _document_by_id(
    documents: Iterable[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for document in documents:
        document_id = document.get("document_id")
        if not isinstance(document_id, str) or not document_id:
            continue
        if document_id in result:
            raise ValueError("duplicate identity document id")
        result[document_id] = document
    return result


def _validate_v1_1_identity_entry(
    entry: Mapping[str, Any],
    *,
    documents: Mapping[str, Mapping[str, Any]],
) -> None:
    if set(entry) != _EXCLUSION_V1_1_KEYS:
        raise ValueError("identity exclusion row keys mismatch")
    hs6 = entry.get("hs6")
    if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
        raise ValueError("identity exclusion HS6 invalid")
    if entry.get("reason") not in _GOVERNED_IDENTITY_REASONS:
        raise ValueError("identity exclusion reason must be governed")
    if (
        entry.get("hs_revision") != "H6"
        or entry.get("rule_version") != RULE_ID_V1_1
    ):
        raise ValueError("identity exclusion revision or rule version invalid")
    basis = entry.get("basis")
    if not isinstance(basis, Mapping) or set(basis) != _EXCLUSION_BASIS_KEYS:
        raise ValueError("identity exclusion basis keys mismatch")
    if any(
        not isinstance(basis.get(key), str) or not basis[key].strip()
        for key in _EXCLUSION_BASIS_KEYS
    ):
        raise ValueError("identity exclusion basis values required")
    document_id = entry.get("document_id")
    document = documents.get(str(document_id))
    if (
        document is None
        or document.get("source_id") != "wco_hs_nomenclature"
        or document.get("coverage", {}).get("status") != "COMPLETE"
    ):
        raise ValueError(
            "identity exclusion requires a COMPLETE wco_hs_nomenclature record"
        )
    page_index = entry.get("page_index")
    line_indices = entry.get("line_indices")
    pages = document.get("pages")
    if not isinstance(pages, list):
        raise ValueError("identity exclusion page/line address invalid")
    if isinstance(page_index, Mapping) and isinstance(
        line_indices, Mapping
    ):
        if (
            set(page_index) != set(_EXCLUSION_QUOTE_KEYS)
            or set(line_indices) != set(_EXCLUSION_QUOTE_KEYS)
        ):
            raise ValueError("identity exclusion page/line address invalid")
        addresses = {
            key: (page_index[key], line_indices[key])
            for key in _EXCLUSION_QUOTE_KEYS
        }
    else:
        addresses = {
            key: (page_index, line_indices)
            for key in _EXCLUSION_QUOTE_KEYS
        }
    for key, (quoted_page, quoted_lines) in addresses.items():
        if (
            not isinstance(quoted_page, int)
            or isinstance(quoted_page, bool)
            or quoted_page <= 0
            or not isinstance(quoted_lines, list)
            or not quoted_lines
            or any(
                not isinstance(index, int)
                or isinstance(index, bool)
                or index <= 0
                for index in quoted_lines
            )
            or quoted_lines != sorted(set(quoted_lines))
        ):
            raise ValueError("identity exclusion page/line address invalid")
        page = next(
            (
                item
                for item in pages
                if isinstance(item, Mapping)
                and item.get("page_index") == quoted_page
            ),
            None,
        )
        lines = page.get("lines") if isinstance(page, Mapping) else None
        if not isinstance(lines, list) or any(
            index > len(lines) for index in quoted_lines
        ):
            raise ValueError("identity exclusion page/line address invalid")
        addressed = [
            _normalised_line(lines[index - 1])
            for index in quoted_lines
            if isinstance(lines[index - 1], str)
        ]
        if not any(
            _normalised_line(str(basis[key])) in stored
            for stored in addressed
        ):
            raise ValueError(
                "identity exclusion quoted text must match a verbatim stored line"
            )


def validate_identity_exclusions(
    payload: Mapping[str, Any],
    *,
    documents: Iterable[Mapping[str, Any]] = (),
    rule_version: str | None = None,
) -> None:
    """Validate a versioned governed identity-exclusion table."""
    expected_rule = rule_version or payload.get("rule_id")
    if expected_rule not in RULE_VERSIONS:
        raise ValueError("identity exclusions rule version invalid")
    if set(payload) != {"schema_version", "rule_id", "entries"}:
        raise ValueError("identity exclusions top-level keys mismatch")
    if (
        payload.get("schema_version") != _SCHEMA_BY_RULE[expected_rule]
        or payload.get("rule_id") != expected_rule
    ):
        raise ValueError("identity exclusions identity mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("identity exclusions entries must be a list")
    documents_by_id = _document_by_id(documents)
    codes: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("identity exclusion row keys mismatch")
        if expected_rule == RULE_ID_V1_1:
            _validate_v1_1_identity_entry(
                entry,
                documents=documents_by_id,
            )
        else:
            if set(entry) != _EXCLUSION_KEYS:
                raise ValueError("identity exclusion row keys mismatch")
            hs6 = entry.get("hs6")
            if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
                raise ValueError("identity exclusion HS6 invalid")
            if not isinstance(entry.get("reason"), str) or not entry["reason"]:
                raise ValueError("identity exclusion reason required")
            if not isinstance(entry.get("basis"), str) or not entry["basis"]:
                raise ValueError("identity exclusion basis required")
        codes.append(str(entry["hs6"]))
    if codes != sorted(set(codes)):
        raise ValueError("identity exclusions must be HS6-sorted and unique")


def _validated_owner_designations(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in rows:
        if set(row) != _OWNER_DESIGNATION_KEYS:
            raise ValueError("owner designation row keys mismatch")
        hs6 = row.get("hs6")
        if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
            raise ValueError("owner designation HS6 invalid")
        if any(
            not isinstance(row.get(key), str) or not row[key].strip()
            for key in ("reason", "ruling_reference")
        ):
            raise ValueError("owner designation reason and ruling required")
        result.append(
            {
                "hs6": hs6,
                "reason": str(row["reason"]),
                "ruling_reference": str(row["ruling_reference"]),
            }
        )
    if [row["hs6"] for row in result] != sorted(
        {row["hs6"] for row in result}
    ):
        raise ValueError("owner designations must be HS6-sorted and unique")
    return result


def classify_gap_years(
    record: Mapping[str, Any],
    universe_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Return the typed 1.1 exclusion for a CANDIDATE GAP_YEARS record."""
    if record.get("screening_disposition") != "CANDIDATE":
        return None
    warnings = record.get("warnings")
    continuity = (
        warnings.get("classification_continuity")
        if isinstance(warnings, Mapping)
        else None
    )
    if (
        not isinstance(continuity, Mapping)
        or continuity.get("status") != "GAP_YEARS"
    ):
        return None
    hs6 = record.get("hs6")
    if not isinstance(hs6, str):
        raise ValueError("screening record HS6 missing")
    matching = [
        row
        for row in universe_rows
        if row.get("hs6") == hs6 and isinstance(row.get("year"), int)
    ]
    if not matching:
        raise ValueError("GAP_YEARS record has no universe rows")
    observed_years = sorted({int(row["year"]) for row in matching})
    import_years = {
        int(row["year"])
        for row in matching
        if row.get("flow") == "imports"
    }
    missing = [
        year
        for year in range(observed_years[0], observed_years[-1] + 1)
        if year not in import_years
    ]
    if not missing:
        raise ValueError("GAP_YEARS record has no missing import year")
    revisions = sorted(
        {
            str(row["hs_revision"])
            for row in matching
            if isinstance(row.get("hs_revision"), str)
        }
    )
    return {
        "hs6": hs6,
        "reason": "SERIES_GAP_YEARS",
        "missing_import_years": missing,
        "hs_revisions": revisions,
        "rule_version": RULE_ID_V1_1,
        "basis": (
            "Persistence rules need a continuous series; missing years are "
            "not zero trade. Screening continuity is GAP_YEARS; missing "
            f"import years {missing}."
        ),
    }


def _document_text(record: Mapping[str, Any]) -> Iterable[str]:
    declared = record.get("declared")
    if isinstance(declared, Mapping):
        title = declared.get("title_text")
        if isinstance(title, str):
            yield title
    pages = record.get("pages")
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, Mapping):
                continue
            lines = page.get("lines")
            if isinstance(lines, list):
                yield from (line for line in lines if isinstance(line, str))


def disclosure_covered(
    term_row: Mapping[str, Any],
    document_records: Iterable[Mapping[str, Any]],
) -> list[str]:
    """Return COMPLETE producer records matching a listed source and term."""
    sources = set(term_row.get("sources", []))
    terms = [
        term.casefold()
        for term in term_row.get("terms", [])
        if isinstance(term, str)
    ]
    matches: set[str] = set()
    for record in document_records:
        declared = record.get("declared")
        if (
            record.get("source_id") not in sources
            or record.get("coverage", {}).get("status") != "COMPLETE"
            or not isinstance(declared, Mapping)
            or declared.get("publisher_kind") != "producer"
        ):
            continue
        if any(
            term in text.casefold()
            for text in _document_text(record)
            for term in terms
        ):
            document_id = record.get("document_id")
            if isinstance(document_id, str):
                matches.add(document_id)
    return sorted(matches)


def _latest_import(
    rows: Iterable[Mapping[str, Any]], hs6: str, latest_year: int
) -> Mapping[str, Any] | None:
    matches = [
        row
        for row in rows
        if row.get("hs6") == hs6
        and row.get("flow") == "imports"
        and row.get("year") == latest_year
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate latest import row for {hs6}")
    return matches[0] if matches else None


def viable(
    universe_rows: Iterable[Mapping[str, Any]],
    hs6: str,
    latest_year: int,
) -> bool:
    """Return whether latest-year imports carry a positive numeric net weight."""
    latest = _latest_import(universe_rows, hs6, latest_year)
    weight = latest.get("net_weight") if latest else None
    return (
        isinstance(weight, (int, float))
        and not isinstance(weight, bool)
        and weight > 0
    )


def _profile_for(
    hs6: str, headings: Mapping[str, tuple[str, ...]]
) -> str | None:
    matches = [
        profile
        for profile, prefixes in headings.items()
        if any(hs6.startswith(prefix) for prefix in prefixes)
    ]
    if len(matches) > 1:
        raise ValueError(f"HS6 maps to multiple quota profiles: {hs6}")
    return matches[0] if matches else None


def _row_facts(
    record: Mapping[str, Any],
    *,
    profile: str,
    tier: tuple[int, str],
    universe_rows: list[Mapping[str, Any]],
    latest_year: int,
    term_row: Mapping[str, Any] | None,
    document_records: list[Mapping[str, Any]],
    use_disclosure_key: bool,
) -> dict[str, Any]:
    hs6 = str(record["hs6"])
    import_rows = [
        row
        for row in universe_rows
        if row.get("hs6") == hs6 and row.get("flow") == "imports"
    ]
    latest = _latest_import(universe_rows, hs6, latest_year)
    document_ids = (
        disclosure_covered(term_row, document_records)
        if term_row is not None and use_disclosure_key
        else []
    )
    imports = record.get("metrics", {}).get(
        "imports_usd_m_latest", "UNAVAILABLE"
    )
    if not isinstance(imports, (int, float)) or isinstance(imports, bool):
        imports = 0.0
    return {
        "profile": profile,
        "hs6": hs6,
        "tier": tier[0],
        "tier_label": tier[1],
        "disclosure_covered": bool(document_ids),
        "disclosure_document_ids": document_ids,
        "r2_fired": "R2" in record.get("fired_signal_rule_ids", []),
        "imports_usd_m_latest": imports,
        "positive_import_years": sorted(
            {
                int(row["year"])
                for row in import_rows
                if isinstance(row.get("year"), int)
                and isinstance(row.get("trade_value"), (int, float))
                and not isinstance(row.get("trade_value"), bool)
                and row["trade_value"] > 0
            }
        ),
        "hs_revisions": sorted(
            {
                str(row["hs_revision"])
                for row in import_rows
                if isinstance(row.get("hs_revision"), str)
            }
        ),
        "latest_net_weight_kg": (
            latest.get("net_weight") if latest is not None else "UNAVAILABLE"
        ),
        "selected": False,
        "substitution_rank": None,
    }


def select_cases_from_records(
    *,
    records: list[Mapping[str, Any]],
    queues: Mapping[str, Any],
    universe_rows: list[Mapping[str, Any]],
    families: Mapping[str, Any],
    quotas: Mapping[str, int],
    terms_bundle: Mapping[str, Any],
    document_records: list[Mapping[str, Any]],
    identity_exclusions: Mapping[str, Any],
    frozen_hs6: frozenset[str],
    use_viability: bool = True,
    use_disclosure_key: bool = True,
    rule_version: str = RULE_ID,
    owner_designations: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Select cases from already-loaded governed inputs."""
    if rule_version not in RULE_VERSIONS:
        raise ValueError("selection rule version invalid")
    validate_terms_bundle(terms_bundle, rule_version=rule_version)
    validate_identity_exclusions(
        identity_exclusions,
        documents=document_records,
        rule_version=rule_version,
    )
    designations = _validated_owner_designations(owner_designations)
    if any(
        not isinstance(quota, int)
        or isinstance(quota, bool)
        or quota <= 0
        for quota in quotas.values()
    ):
        raise ValueError("selection quotas must be positive integers")
    memberships = queue_memberships(queues)
    headings = family_headings_by_profile(families)
    terms_by_code = {row["hs6"]: row for row in terms_bundle["rows"]}
    exclusions_by_code = {
        row["hs6"]: row for row in identity_exclusions["entries"]
    }
    years = [
        int(row["year"])
        for row in universe_rows
        if row.get("flow") == "imports" and isinstance(row.get("year"), int)
    ]
    if not years:
        raise ValueError("universe has no import years")
    latest_year = max(years)

    by_profile: dict[str, list[dict[str, Any]]] = {
        profile: [] for profile in quotas
    }
    identity_removed: dict[str, list[dict[str, str]]] = {
        profile: [] for profile in quotas
    }
    frozen_removed: dict[str, list[str]] = {profile: [] for profile in quotas}
    viability_removed: dict[str, list[str]] = {profile: [] for profile in quotas}
    gap_removed: dict[str, list[dict[str, Any]]] = {
        profile: [] for profile in quotas
    }
    seen: set[str] = set()
    for record in records:
        hs6 = record.get("hs6")
        if not isinstance(hs6, str) or hs6 in seen:
            if hs6 in seen:
                raise ValueError(f"duplicate screening record: {hs6}")
            raise ValueError("screening record HS6 invalid")
        seen.add(hs6)
        profile = _profile_for(hs6, headings)
        if profile not in quotas:
            continue
        if rule_version == RULE_ID_V1_1:
            gap_exclusion = classify_gap_years(record, universe_rows)
            if gap_exclusion is not None:
                gap_removed[profile].append(gap_exclusion)
                continue
        tier = tier_of(record, memberships)
        if tier[0] == 7:
            continue
        if hs6 in exclusions_by_code:
            if rule_version == RULE_ID_V1_1:
                identity_removed[profile].append(
                    dict(exclusions_by_code[hs6])
                )
            else:
                identity_removed[profile].append(
                    {
                        "hs6": hs6,
                        "reason": str(exclusions_by_code[hs6]["reason"]),
                    }
                )
            continue
        if hs6 in frozen_hs6:
            frozen_removed[profile].append(hs6)
            continue
        if use_viability and not viable(universe_rows, hs6, latest_year):
            viability_removed[profile].append(hs6)
            continue
        by_profile[profile].append(
            _row_facts(
                record,
                profile=profile,
                tier=tier,
                universe_rows=universe_rows,
                latest_year=latest_year,
                term_row=terms_by_code.get(hs6),
                document_records=document_records,
                use_disclosure_key=use_disclosure_key,
            )
        )

    profile_outputs: dict[str, Any] = {}
    selected_all: list[str] = []
    for profile in sorted(quotas, key=lambda item: (
        _PROFILE_ORDER.index(item) if item in _PROFILE_ORDER else len(_PROFILE_ORDER),
        item,
    )):
        ordered = sorted(
            by_profile[profile],
            key=lambda row: (
                row["tier"],
                not row["disclosure_covered"],
                not row["r2_fired"],
                -float(row["imports_usd_m_latest"]),
                row["hs6"],
            ),
        )
        quota = quotas[profile]
        selected = [row["hs6"] for row in ordered[:quota]]
        substitutes = [row["hs6"] for row in ordered[quota:]]
        for index, row in enumerate(ordered):
            row["selected"] = index < quota
            row["substitution_rank"] = None if index < quota else index - quota + 1
        selected_all.extend(selected)
        profile_outputs[profile] = {
            "quota": quota,
            "selected": selected,
            "substitution_order": substitutes,
            "excluded_by_identity": sorted(
                identity_removed[profile], key=lambda row: row["hs6"]
            ),
            "excluded_frozen": sorted(frozen_removed[profile]),
            "excluded_by_viability": sorted(viability_removed[profile]),
            "rows": ordered,
        }
        if rule_version == RULE_ID_V1_1:
            profile_outputs[profile]["excluded_series_gap_years"] = sorted(
                gap_removed[profile], key=lambda row: row["hs6"]
            )
    result = {
        "profiles": profile_outputs,
        "selected_hs6": sorted(selected_all),
    }
    if rule_version == RULE_ID_V1_1:
        return {
            "schema_version": _SCHEMA_BY_RULE[rule_version],
            "rule_version": rule_version,
            "owner_designated_cases": designations,
            **result,
        }
    return result


def _inventory_identity(
    paths: list[Path],
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    rows = [
        {"path": _manifest_key(path, root), "sha256": _sha256(path)}
        for path in sorted(paths, key=lambda item: _manifest_key(item, root))
    ]
    return {
        "file_count": len(rows),
        "files_sha256": hashlib.sha256(_canonical_compact(rows)).hexdigest(),
        "files": rows,
    }


def _load_document_records(
    documents_root: Path,
    *,
    allowed_sources: set[str],
) -> tuple[list[dict[str, Any]], list[Path]]:
    paths = sorted(
        path
        for source in allowed_sources
        for path in (documents_root / source / "records").glob("*.json")
    )
    return [_json_object(path) for path in paths], paths


def _inventory_matches(
    identity: Mapping[str, Any],
    paths: list[Path],
    *,
    root: Path,
) -> bool:
    actual = _inventory_identity(paths, root=root)
    return all(actual.get(key) == identity.get(key) for key in actual)


def select_cases(
    *,
    screening_dir: Path,
    universe_path: Path,
    families_path: Path,
    quotas: Mapping[str, int],
    terms_path: Path,
    identity_exclusions_path: Path,
    documents_root: Path,
    frozen_hs6: frozenset[str],
    use_viability: bool = True,
    use_disclosure_key: bool = True,
    rule_version: str = RULE_ID_V1_1,
    families_identity: Mapping[str, Any] | None = None,
    owner_designations_path: Path | None = None,
    document_paths: Sequence[Path] | None = None,
    recorded_inputs: Mapping[str, Any] | None = None,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Load governed inputs and execute a governed selection rule."""
    if rule_version not in RULE_VERSIONS:
        raise ValueError("selection rule version invalid")
    screening = load_screening_snapshot_directory(screening_dir)
    universe = _json_object(universe_path)
    resolved_families_path = families_path
    if families_identity is not None:
        resolved_families_path = resolve_recorded_input(
            dict(families_identity),
            root=root,
        )
    families = _yaml_object(resolved_families_path)
    terms = _json_object(terms_path)
    identity_exclusions = _json_object(identity_exclusions_path)
    headings = family_headings_by_profile(families)
    expected_codes = {
        record["hs6"]
        for record in screening["records"]
        if _profile_for(record["hs6"], headings) in quotas
    }
    validate_terms_bundle(
        terms,
        expected_hs6=expected_codes,
        rule_version=rule_version,
    )
    allowed_sources = {
        source for row in terms["rows"] for source in row["sources"]
    }
    document_sources = set(allowed_sources)
    if rule_version == RULE_ID_V1_1:
        document_sources.add("wco_hs_nomenclature")
    if document_paths is None:
        documents, selected_document_paths = _load_document_records(
            documents_root, allowed_sources=document_sources
        )
        if rule_version == RULE_ID_V1_1:
            identity_document_ids = {
                str(row["document_id"])
                for row in identity_exclusions["entries"]
            }
            selected_pairs = [
                (document, path)
                for document, path in zip(
                    documents,
                    selected_document_paths,
                    strict=True,
                )
                if document.get("source_id") != "wco_hs_nomenclature"
                or document.get("document_id") in identity_document_ids
            ]
            documents = [document for document, _ in selected_pairs]
            selected_document_paths = [path for _, path in selected_pairs]
    else:
        selected_document_paths = list(document_paths)
        documents = [_json_object(path) for path in selected_document_paths]
        if any(
            document.get("source_id") not in document_sources
            for document in documents
        ):
            raise ValueError("INPUTS_CHANGED")
    validate_identity_exclusions(
        identity_exclusions,
        documents=documents,
        rule_version=rule_version,
    )
    owner_designations: list[dict[str, str]] = []
    owner_identity: dict[str, Any] | None = None
    if owner_designations_path is not None:
        owner_payload = _json_object(owner_designations_path)
        if set(owner_payload) != {"schema_version", "rule_id", "rows"}:
            raise ValueError("owner designation bundle keys mismatch")
        if (
            owner_payload.get("schema_version") != "1.1.0"
            or owner_payload.get("rule_id") != RULE_ID_V1_1
        ):
            raise ValueError("owner designation bundle identity mismatch")
        owner_designations = _validated_owner_designations(
            owner_payload["rows"]
        )
        owner_identity = {
            "path": _manifest_key(owner_designations_path, root),
            "sha256": _sha256(owner_designations_path),
        }
    selected = select_cases_from_records(
        records=screening["records"],
        queues=screening["queues"],
        universe_rows=universe["rows"],
        families=families,
        quotas=quotas,
        terms_bundle=terms,
        document_records=documents,
        identity_exclusions=identity_exclusions,
        frozen_hs6=frozen_hs6,
        use_viability=use_viability,
        use_disclosure_key=use_disclosure_key,
        rule_version=rule_version,
        owner_designations=owner_designations,
    )
    screening_paths = [
        path
        for path in screening_dir.rglob("*")
        if path.is_file()
    ]
    current_families_identity = {
        "path": _manifest_key(families_path, root),
        "version": families.get("metadata", {}).get("version"),
        "sha256": _sha256(resolved_families_path),
    }
    if families_identity is not None:
        current_families_identity = dict(families_identity)
        if (
            current_families_identity.get("version")
            != families.get("metadata", {}).get("version")
        ):
            raise ValueError("INPUTS_CHANGED")
    inputs: dict[str, Any] = {
        "screening": {
            "path": _manifest_key(screening_dir, root),
            "snapshot_id": screening["snapshot_id"],
            **_inventory_identity(screening_paths, root=root),
        },
        "universe": {
            "path": _manifest_key(universe_path, root),
            "snapshot_id": universe["snapshot_id"],
            "sha256": _sha256(universe_path),
        },
        "product_families": current_families_identity,
        "terms": {
            "path": _manifest_key(terms_path, root),
            "sha256": _sha256(terms_path),
        },
        "identity_exclusions": {
            "path": _manifest_key(identity_exclusions_path, root),
            "sha256": _sha256(identity_exclusions_path),
        },
        "documents": {
            "path": _manifest_key(documents_root, root),
            "source_ids": sorted(document_sources),
            **_inventory_identity(selected_document_paths, root=root),
        },
        "rule_parameters": {
            "quotas": dict(sorted(quotas.items())),
            "frozen_hs6": sorted(frozen_hs6),
            "viability_latest_import_net_weight": use_viability,
            "disclosure_coverage_key": use_disclosure_key,
        },
    }
    if rule_version == RULE_ID_V1_1:
        inputs["rule_parameters"]["rule_version"] = rule_version
    if owner_identity is not None:
        inputs["owner_designations"] = owner_identity
    if recorded_inputs is not None:
        inputs = json.loads(json.dumps(recorded_inputs))
    digest = hashlib.sha256(_canonical_compact(inputs)).hexdigest()
    family_count = sum(
        bool(family.get("hs4_headings"))
        and family.get("sector_profile") in quotas
        for family in families["families"].values()
    )
    record = {
        "schema_version": _SCHEMA_BY_RULE[rule_version],
        "selection_id": f"{_PREFIX_BY_SCHEMA[_SCHEMA_BY_RULE[rule_version]]}{digest[:12]}",
        "rule_id": rule_version,
        "family_count": family_count,
        "inputs": inputs,
        **selected,
    }
    return record


def _resolve_inventory_paths(
    identity: Mapping[str, Any],
    *,
    root: Path,
) -> list[Path]:
    files = identity.get("files")
    if not isinstance(files, list):
        raise ValueError("INPUTS_CHANGED")
    paths = [
        resolve_recorded_input(dict(item), root=root)
        for item in files
        if isinstance(item, Mapping)
    ]
    if len(paths) != len(files) or not _inventory_matches(
        identity,
        paths,
        root=root,
    ):
        raise ValueError("INPUTS_CHANGED")
    return paths


def reconstruct_selection(
    record_path: Path,
    *,
    root: Path = PROJECT_ROOT,
) -> bytes:
    """Re-run a recorded selection from its exact input identities."""
    recorded = load_selection(record_path)
    inputs = recorded.get("inputs")
    if not isinstance(inputs, Mapping):
        raise ValueError("INPUTS_CHANGED")
    screening_identity = inputs.get("screening")
    documents_identity = inputs.get("documents")
    if not isinstance(screening_identity, Mapping) or not isinstance(
        documents_identity, Mapping
    ):
        raise ValueError("INPUTS_CHANGED")
    screening_paths = _resolve_inventory_paths(
        screening_identity,
        root=root,
    )
    screening_dir = root / str(screening_identity.get("path"))
    actual_screening_paths = sorted(
        path for path in screening_dir.rglob("*") if path.is_file()
    )
    if screening_paths != actual_screening_paths:
        raise ValueError("INPUTS_CHANGED")
    document_paths = _resolve_inventory_paths(
        documents_identity,
        root=root,
    )
    universe_identity = inputs.get("universe")
    families_identity = inputs.get("product_families")
    terms_identity = inputs.get("terms")
    exclusions_identity = inputs.get("identity_exclusions")
    if any(
        not isinstance(identity, Mapping)
        for identity in (
            universe_identity,
            families_identity,
            terms_identity,
            exclusions_identity,
        )
    ):
        raise ValueError("INPUTS_CHANGED")
    universe_path = resolve_recorded_input(
        dict(universe_identity),
        root=root,
    )
    families_path = resolve_recorded_input(
        dict(families_identity),
        root=root,
    )
    terms_path = resolve_recorded_input(dict(terms_identity), root=root)
    exclusions_path = resolve_recorded_input(
        dict(exclusions_identity),
        root=root,
    )
    parameters = inputs.get("rule_parameters")
    if not isinstance(parameters, Mapping):
        raise ValueError("INPUTS_CHANGED")
    quotas = parameters.get("quotas")
    frozen = parameters.get("frozen_hs6")
    if not isinstance(quotas, Mapping) or not isinstance(frozen, list):
        raise ValueError("INPUTS_CHANGED")
    rule_version = str(
        recorded.get("rule_version") or recorded.get("rule_id")
    )
    owner_path: Path | None = None
    owner_identity = inputs.get("owner_designations")
    if owner_identity is not None:
        if not isinstance(owner_identity, Mapping):
            raise ValueError("INPUTS_CHANGED")
        owner_path = resolve_recorded_input(dict(owner_identity), root=root)
    elif recorded.get("owner_designated_cases"):
        raise ValueError("INPUTS_CHANGED")
    generated = select_cases(
        screening_dir=screening_dir,
        universe_path=universe_path,
        families_path=families_path,
        families_identity=dict(families_identity),
        quotas={str(key): int(value) for key, value in quotas.items()},
        terms_path=terms_path,
        identity_exclusions_path=exclusions_path,
        documents_root=root / str(documents_identity.get("path")),
        document_paths=document_paths,
        frozen_hs6=frozenset(str(item) for item in frozen),
        use_viability=bool(
            parameters.get("viability_latest_import_net_weight")
        ),
        use_disclosure_key=bool(
            parameters.get("disclosure_coverage_key")
        ),
        rule_version=rule_version,
        owner_designations_path=owner_path,
        recorded_inputs=inputs,
        root=root,
    )
    content = canonical_bytes(generated)
    if content != record_path.read_bytes():
        raise ValueError("SELECTION_RECONSTRUCTION_MISMATCH")
    return content


def reconstruct_all_selections(*, root: Path = PROJECT_ROOT) -> int:
    """Reconstruct every stored S14/S15 selection record."""
    selection_root = root / "data" / "cases" / "selection"
    paths = sorted(selection_root.glob("CASE-SELECTION-*.json"))
    for path in paths:
        reconstruct_selection(path, root=root)
    return len(paths)


def write_selection(
    record: Mapping[str, Any],
    out_dir: Path,
    *,
    record_prefix: str | None = None,
) -> Path:
    """Write one canonical selection record without overwriting history."""
    schema_version = record.get("schema_version")
    expected_prefix = _PREFIX_BY_SCHEMA.get(str(schema_version))
    if expected_prefix is None:
        raise ValueError("selection schema version invalid")
    if record_prefix is not None and record_prefix != expected_prefix:
        raise ValueError("record prefix does not match schema version")
    selection_id = record.get("selection_id")
    if not isinstance(selection_id, str) or not selection_id.startswith(
        expected_prefix
    ):
        raise ValueError("selection_id invalid")
    content = canonical_bytes(record)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{selection_id}.json"
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("selection write conflict")
        return path
    path.write_bytes(content)
    return path


def load_selection(path: Path) -> dict[str, Any]:
    """Load a canonical selection record."""
    record = _json_object(path)
    if path.read_bytes() != canonical_bytes(record):
        raise ValueError("selection record is not canonical")
    if path.name != f"{record.get('selection_id')}.json":
        raise ValueError("selection file identity mismatch")
    return record
