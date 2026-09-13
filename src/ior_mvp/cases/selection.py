"""Deterministic S14 deep-case selection from frozen screening evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import yaml

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.screening.snapshot import load_screening_snapshot_directory


SCHEMA_VERSION = "1.0.0"
RULE_ID = "S14-CS-1"
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
_HS4_PATTERN = re.compile(r"[0-9]{4}")
_PROFILE_ORDER = (
    "coated_steel",
    "fabricated_aluminium",
    "technical_plastics",
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
) -> None:
    """Validate the governed HS6 disclosure-term bundle."""
    if set(payload) != {"schema_version", "rule_id", "rows"}:
        raise ValueError("disclosure terms top-level keys mismatch")
    if (
        payload.get("schema_version") != SCHEMA_VERSION
        or payload.get("rule_id") != RULE_ID
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


def validate_identity_exclusions(payload: Mapping[str, Any]) -> None:
    """Validate the governed OD-11 identity-exclusion table."""
    if set(payload) != {"schema_version", "rule_id", "entries"}:
        raise ValueError("identity exclusions top-level keys mismatch")
    if (
        payload.get("schema_version") != SCHEMA_VERSION
        or payload.get("rule_id") != RULE_ID
    ):
        raise ValueError("identity exclusions identity mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("identity exclusions entries must be a list")
    codes: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != _EXCLUSION_KEYS:
            raise ValueError("identity exclusion row keys mismatch")
        hs6 = entry.get("hs6")
        if not isinstance(hs6, str) or len(hs6) != 6 or not hs6.isdigit():
            raise ValueError("identity exclusion HS6 invalid")
        if not isinstance(entry.get("reason"), str) or not entry["reason"]:
            raise ValueError("identity exclusion reason required")
        if not isinstance(entry.get("basis"), str) or not entry["basis"]:
            raise ValueError("identity exclusion basis required")
        codes.append(hs6)
    if codes != sorted(set(codes)):
        raise ValueError("identity exclusions must be HS6-sorted and unique")


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
) -> dict[str, Any]:
    """Select cases from already-loaded governed inputs."""
    validate_terms_bundle(terms_bundle)
    validate_identity_exclusions(identity_exclusions)
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
        tier = tier_of(record, memberships)
        if tier[0] == 7:
            continue
        if hs6 in exclusions_by_code:
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
    return {
        "profiles": profile_outputs,
        "selected_hs6": sorted(selected_all),
    }


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
) -> dict[str, Any]:
    """Load governed inputs and execute S14-CS-1."""
    screening = load_screening_snapshot_directory(screening_dir)
    universe = _json_object(universe_path)
    families = _yaml_object(families_path)
    terms = _json_object(terms_path)
    identity_exclusions = _json_object(identity_exclusions_path)
    headings = family_headings_by_profile(families)
    expected_codes = {
        record["hs6"]
        for record in screening["records"]
        if _profile_for(record["hs6"], headings) in quotas
    }
    validate_terms_bundle(terms, expected_hs6=expected_codes)
    validate_identity_exclusions(identity_exclusions)
    allowed_sources = {
        source for row in terms["rows"] for source in row["sources"]
    }
    documents, document_paths = _load_document_records(
        documents_root, allowed_sources=allowed_sources
    )
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
    )
    screening_paths = [
        path
        for path in screening_dir.rglob("*")
        if path.is_file()
    ]
    inputs = {
        "screening": {
            "path": _manifest_key(screening_dir),
            "snapshot_id": screening["snapshot_id"],
            **_inventory_identity(screening_paths),
        },
        "universe": {
            "path": _manifest_key(universe_path),
            "snapshot_id": universe["snapshot_id"],
            "sha256": _sha256(universe_path),
        },
        "product_families": {
            "path": _manifest_key(families_path),
            "version": families.get("metadata", {}).get("version"),
            "sha256": _sha256(families_path),
        },
        "terms": {
            "path": _manifest_key(terms_path),
            "sha256": _sha256(terms_path),
        },
        "identity_exclusions": {
            "path": _manifest_key(identity_exclusions_path),
            "sha256": _sha256(identity_exclusions_path),
        },
        "documents": {
            "path": _manifest_key(documents_root),
            "source_ids": sorted(allowed_sources),
            **_inventory_identity(document_paths),
        },
        "rule_parameters": {
            "quotas": dict(sorted(quotas.items())),
            "frozen_hs6": sorted(frozen_hs6),
            "viability_latest_import_net_weight": use_viability,
            "disclosure_coverage_key": use_disclosure_key,
        },
    }
    digest = hashlib.sha256(_canonical_compact(inputs)).hexdigest()
    family_count = sum(
        bool(family.get("hs4_headings"))
        and family.get("sector_profile") in quotas
        for family in families["families"].values()
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "selection_id": f"CASE-SELECTION-S14-{digest[:12]}",
        "rule_id": RULE_ID,
        "family_count": family_count,
        "inputs": inputs,
        **selected,
    }


def write_selection(record: Mapping[str, Any], out_dir: Path) -> Path:
    """Write one canonical selection record without overwriting history."""
    selection_id = record.get("selection_id")
    if not isinstance(selection_id, str) or not selection_id.startswith(
        "CASE-SELECTION-S14-"
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
