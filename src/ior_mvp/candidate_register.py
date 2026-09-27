"""Strict scenario 2.2 candidate register validation."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from typing import Any, Mapping

from .candidate_record_contract import (
    DATASET_KINDS, ORIGINS, PLANT_STATUS, _exact_keys, _fail,
    _finite_number, _register_source_references, _source_refs,
    _validate_fact_values, _window, validate_coverage_row,
)


REGISTER_KEYS = frozenset(
    {
        "register_id",
        "version",
        "as_of",
        "coverage",
        "companies",
        "plants",
        "lines",
        "facts",
        "attribution_links",
    }
)
COMPANY_KEYS = frozenset(
    {"company_id", "name_en", "name_ar", "manufacturer_assignment"}
)
PLANT_KEYS = frozenset(
    {"plant_id", "company_id", "country", "status", "registry_fact_ids"}
)
LINE_KEYS = frozenset({"line_id", "plant_id"})
FACT_KEYS = frozenset(
    {
        "fact_id",
        "kind",
        "dataset_kind",
        "subject_type",
        "subject_id",
        "window",
        "values",
        "origin",
        "source_refs",
        "rule_id",
    }
)
ATTRIBUTION_KEYS = frozenset(
    {
        "attribution_id",
        "fact_id",
        "plant_id",
        "window",
        "allocated_quantity",
        "unit",
        "source_refs",
    }
)
ENTITY_ID = re.compile(r"^(COMPANY|PLANT|LINE)-[0-9a-f]{16}$")


def validate_candidate_register(register: dict[str, Any]) -> dict[str, Any]:
    """Validate one inline candidate register and return it unchanged."""
    if not isinstance(register, dict):
        _fail("candidate_register must be an object")
    _exact_keys(register, REGISTER_KEYS, "candidate_register")
    if not isinstance(register["register_id"], str) or not register["register_id"]:
        _fail("candidate_register.register_id is required")
    if register["version"] not in {1, "1"}:
        _fail("candidate_register.version is not the admitted register version")
    try:
        date.fromisoformat(register["as_of"])
    except (TypeError, ValueError):
        _fail("candidate_register.as_of is not a date")
    companies = register["companies"]
    plants = register["plants"]
    lines = register["lines"]
    facts = register["facts"]
    if not all(isinstance(row, list) for row in (companies, plants, lines, facts)):
        _fail("candidate_register collections must be lists")
    company_ids = _ids(companies, "company_id", COMPANY_KEYS, "company")
    plant_ids: dict[str, dict[str, Any]] = {}
    for plant in plants:
        _exact_keys(plant, PLANT_KEYS, "plant")
        if ENTITY_ID.fullmatch(str(plant["plant_id"])) is None:
            _fail(f"malformed identity {plant['plant_id']}")
        if plant["plant_id"] in plant_ids:
            _fail(f"duplicate plant_id {plant['plant_id']}")
        if plant["company_id"] not in company_ids:
            _fail(f"plant {plant['plant_id']} has no company")
        if plant["country"] != "SA":
            _fail(f"plant {plant['plant_id']} is outside the Saudi register")
        if plant["status"] not in PLANT_STATUS:
            _fail(f"plant {plant['plant_id']} status is unknown")
        plant_ids[plant["plant_id"]] = plant
    line_ids: set[str] = set()
    for line in lines:
        _exact_keys(line, LINE_KEYS, "line")
        if ENTITY_ID.fullmatch(str(line["line_id"])) is None:
            _fail(f"malformed identity {line['line_id']}")
        if line["line_id"] in line_ids:
            _fail(f"duplicate line_id {line['line_id']}")
        if line["plant_id"] not in plant_ids:
            _fail(f"line {line['line_id']} has no plant")
        line_ids.add(line["line_id"])
    fact_ids: dict[str, dict[str, Any]] = {}
    for fact in facts:
        _exact_keys(fact, FACT_KEYS, "fact")
        if fact["fact_id"] in fact_ids:
            _fail(f"duplicate fact_id {fact['fact_id']}")
        if fact["dataset_kind"] not in DATASET_KINDS:
            _fail(f"{fact['fact_id']} dataset_kind is unknown")
        if fact["origin"] not in ORIGINS:
            _fail(f"{fact['fact_id']} origin is unknown")
        if fact["origin"] == "REVIEWED_INFERENCE":
            if not isinstance(fact["rule_id"], str) or not fact["rule_id"]:
                _fail(f"{fact['fact_id']} inference requires rule_id")
        elif fact["rule_id"] is not None:
            _fail(f"{fact['fact_id']} rule_id is only for reviewed inference")
        _window(fact["window"], fact["fact_id"])
        _source_refs(fact["source_refs"], fact["fact_id"])
        subject_type = fact["subject_type"]
        subject_id = fact["subject_id"]
        if subject_type == "COMPANY" and subject_id not in company_ids:
            _fail(f"{fact['fact_id']} company subject is unknown")
        elif subject_type == "PLANT" and subject_id not in plant_ids:
            _fail(f"{fact['fact_id']} plant subject is unknown")
        elif subject_type == "LINE" and subject_id not in line_ids:
            _fail(f"{fact['fact_id']} line subject is unknown")
        elif subject_type not in {"COMPANY", "PLANT", "LINE"}:
            _fail(f"{fact['fact_id']} subject_type is unknown")
        _validate_fact_values(fact)
        fact_ids[fact["fact_id"]] = fact
    seen_links: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    cumulative: dict[str, float] = {}
    line_plant = {line["line_id"]: line["plant_id"] for line in lines}
    for link in register["attribution_links"]:
        _exact_keys(link, ATTRIBUTION_KEYS, "attribution")
        if link["attribution_id"] in seen_links:
            _fail(f"duplicate attribution {link['attribution_id']}")
        seen_links.add(link["attribution_id"])
        pair = (link["fact_id"], link["plant_id"])
        if pair in seen_pairs:
            _fail(f"duplicate attribution for {pair[0]}")
        seen_pairs.add(pair)
        fact = fact_ids.get(link["fact_id"])
        plant = plant_ids.get(link["plant_id"])
        if fact is None or plant is None:
            _fail(f"{link['attribution_id']} attribution target is unknown")
        if fact["subject_type"] == "PLANT" and fact["subject_id"] != plant["plant_id"]:
            _fail(f"{link['attribution_id']} attribution ownership is not the plant")
        if fact["subject_type"] == "COMPANY" and fact["subject_id"] != plant["company_id"]:
            _fail(f"{link['attribution_id']} attribution ownership is not the company")
        if fact["subject_type"] == "LINE" and line_plant.get(fact["subject_id"]) != plant["plant_id"]:
            _fail(f"{link['attribution_id']} attribution ownership is not the line")
        link_window = _window(link["window"], link["attribution_id"])
        fact_window = _window(fact["window"], fact["fact_id"])
        if link_window[0] < fact_window[0] or link_window[1] > fact_window[1]:
            _fail(f"{link['attribution_id']} period is outside the source fact")
        _source_refs(link["source_refs"], link["attribution_id"])
        allocated = _finite_number(
            link["allocated_quantity"], link["attribution_id"]
        )
        if allocated < 0:
            _fail(f"{link['attribution_id']} allocation is negative")
        cumulative[link["fact_id"]] = cumulative.get(link["fact_id"], 0.0) + allocated
    for fact_id, total in cumulative.items():
        quantity = fact_ids[fact_id]["values"].get("quantity_kt")
        if isinstance(quantity, (int, float)) and not isinstance(quantity, bool):
            if total > float(quantity):
                _fail(f"cumulative allocation for {fact_id} exceeds source quantity")
    for plant in plants:
        for fact_id in plant["registry_fact_ids"]:
            registry_fact = fact_ids.get(fact_id)
            if (
                registry_fact is None
                or registry_fact["kind"] != "REGISTRY_ACTIVITY"
                or registry_fact["subject_id"] != plant["plant_id"]
            ):
                _fail(f"{plant['plant_id']} registry fact does not resolve")
    known_subjects = {
        "COMPANY": company_ids,
        "PLANT": set(plant_ids),
        "LINE": line_ids,
    }
    coverage_ids: set[str] = set()
    for coverage in register["coverage"]:
        validate_coverage_row(coverage, known_subjects)
        if coverage["coverage_id"] in coverage_ids:
            _fail(f"duplicate coverage_id {coverage['coverage_id']}")
        coverage_ids.add(coverage["coverage_id"])
    _register_source_references(register)
    return register


def _ids(
    rows: list[dict[str, Any]],
    key: str,
    allowed: frozenset[str],
    label: str,
) -> set[str]:
    found: set[str] = set()
    for row in rows:
        _exact_keys(row, allowed, label)
        if ENTITY_ID.fullmatch(str(row[key])) is None:
            _fail(f"malformed identity {row[key]}")
        if row[key] in found:
            _fail(f"duplicate {key} {row[key]}")
        if row.get("manufacturer_assignment") not in {None}:
            _fail(f"{row[key]} manufacturer_assignment must be null")
        found.add(row[key])
    return found


def canonical_register_bytes(register: Mapping[str, Any]) -> bytes:
    """Return the shared register payload without scenario-local identity."""
    return json.dumps(
        register,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_register_sha256(register: Mapping[str, Any]) -> str:
    """Return the hash used to prove the steel and PP registers match."""
    return hashlib.sha256(canonical_register_bytes(register)).hexdigest()
