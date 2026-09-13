"""CaseBrief 1.0.0 validation with verbatim-span enforcement."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from ior_mvp.acquisition.contracts import UnavailableReason
from ior_mvp.config import PROJECT_ROOT, sector_profiles_config
from ior_mvp.public_decision import SUPPORT_CODES


SCHEMA_VERSION = "1.1.0"
TRADE_SERIES_RULE = "LATEST_REVISION_ONLY"
UNAVAILABLE = "UNAVAILABLE"
PARTNER_DETAIL_STATES = frozenset(
    {
        "PARTNER_DETAIL_OBSERVED",
        "PARTNER_DETAIL_MISSING",
        "PARTNER_TRADE_OBSERVED_ZERO",
    }
)
PARTNER_DETAIL_MISSING_REASONS = frozenset(
    {reason.value for reason in UnavailableReason}
    | {"NOT_ACQUIRED", "REVISION_MISMATCH"}
)
_TOP_KEYS = frozenset(
    {
        "schema_version",
        "brief_id",
        "opportunity_id",
        "hs6",
        "hs_revision",
        "sector_profile",
        "trade_series_rule",
        "universe_snapshot_id",
        "partner_snapshot_id",
        "partner_detail",
        "commercial_name_en",
        "name_basis",
        "commercial_name_ar",
        "name_basis_ar",
        "decision_object_status",
        "application_boundary",
        "authority_note",
        "capability",
        "document_evidence",
        "spans",
    }
)
_PARTNER_DETAIL_KEYS = frozenset(
    {
        "state",
        "reason",
        "source_id",
        "partner_snapshot_id",
        "unit_key",
        "observed_partner_rows",
        "attempts",
        "basis",
    }
)
_PARTNER_ATTEMPT_KEYS = frozenset(
    {
        "source_id",
        "query_hash",
        "run_id",
        "endpoint_or_document",
        "http_status",
        "normalization_status",
        "coverage_status",
        "stop_reason",
        "contract_path",
        "contract_sha256",
    }
)
_CAPABILITY_KEYS = frozenset(
    {
        "verified_present",
        "same_process_family",
        "coarse_adjacency_signals",
        "producer_evidence",
        "public_dimension_states",
        "profile_hard_gates",
        "unresolved_hard_gates",
    }
)
_SPAN_KEYS = frozenset(
    {
        "span_id",
        "document_id",
        "page_index",
        "line_index",
        "span_text",
        "text_order",
    }
)
_DOCUMENT_EVIDENCE_KEYS = frozenset(
    {"evidence_id", "document_id", "supports", "period"}
)
_FACT_KEYS = frozenset({"value", "span_ids"})
_DIMENSION_KEYS = frozenset({"state", "span_ids"})
_GATE_KEYS = frozenset({"status", "span_ids"})
_SIGNAL_KEYS = frozenset({"signal_type", "description", "span_ids"})
_PRODUCER_KEYS = frozenset(
    {
        "producer",
        "process_family",
        "process_route",
        "published_standards",
        "installed_capacity_tpy",
        "span_ids",
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
_FORBIDDEN_KEYS = frozenset(
    {
        "route_code",
        "screening_disposition",
        "public_decision_contract",
        "real_decision",
        "simulation_decision",
        "active_decision",
        "scenario_id",
        "synthetic_inputs",
        "ground_truth",
    }
)


class CaseBriefIntegrityError(ValueError):
    """A CaseBrief contains an unsupported or untraceable assertion."""


def _fail(message: str) -> None:
    raise CaseBriefIntegrityError(message)


def _exact(value: Any, expected: frozenset[str], field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        _fail(f"{field} keys mismatch")
    return value


def _text(value: Any, field: str, *, unavailable: bool = False) -> str:
    if unavailable and value == UNAVAILABLE:
        return UNAVAILABLE
    if not isinstance(value, str) or not value:
        _fail(f"{field} must be a non-empty string")
    return value


def _span_ids(
    value: Any,
    field: str,
    known: set[str],
    *,
    required: bool = False,
) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or item not in known for item in value)
        or value != sorted(set(value))
    ):
        _fail(f"{field} span ids must be sorted, unique, and resolved")
    if required and not value:
        _fail(f"{field} requires a verified span")
    return value


def _reject_forbidden(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _FORBIDDEN_KEYS:
                _fail(f"authored decision or synthetic key prohibited: {key}")
            if (
                key == "state"
                and "public_dimension_states" not in path
                and "partner_detail" not in path
            ):
                _fail("authored decision state prohibited")
            if key == "synthetic_flag" or child == "DEMO_GENERATOR":
                _fail("synthetic marker prohibited in CaseBrief")
            _reject_forbidden(child, (*path, str(key)))
    elif isinstance(value, list):
        for child in value:
            _reject_forbidden(child, path)


def _document_records(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    documents_root = root / "data" / "documents"
    for path in sorted(documents_root.glob("*/records/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        document_id = record.get("document_id")
        if isinstance(document_id, str):
            records[document_id] = record
    return records


def _partner_snapshot(root: Path, snapshot_id: str) -> Mapping[str, Any]:
    path = root / "data" / "snapshots" / "partners" / f"{snapshot_id}.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CaseBriefIntegrityError(
            f"partner snapshot does not resolve: {snapshot_id}"
        ) from exc
    if not isinstance(value, Mapping) or value.get("snapshot_id") != snapshot_id:
        _fail("partner snapshot identity mismatch")
    return value


def _validate_partner_attempts(
    root: Path,
    attempts: Any,
    *,
    allow_empty: bool,
) -> list[Mapping[str, Any]]:
    if not isinstance(attempts, list) or (not attempts and not allow_empty):
        _fail("partner_detail attempts must resolve stored units")
    validated: list[Mapping[str, Any]] = []
    identities: set[tuple[str, str, str]] = set()
    for raw in attempts:
        attempt = _exact(raw, _PARTNER_ATTEMPT_KEYS, "partner attempt")
        source_id = _text(attempt["source_id"], "partner attempt source_id")
        query_hash = _text(attempt["query_hash"], "partner attempt query_hash")
        run_id = _text(attempt["run_id"], "partner attempt run_id")
        identity = (source_id, query_hash, run_id)
        if identity in identities:
            _fail("partner attempt identities must be unique")
        identities.add(identity)
        relative = Path(_text(attempt["contract_path"], "contract_path"))
        if relative.is_absolute() or ".." in relative.parts:
            _fail("partner attempt contract_path must be repo-relative")
        contract_path = (root / relative).resolve()
        try:
            contract_path.relative_to(root.resolve())
            contract_bytes = contract_path.read_bytes()
            contract = json.loads(contract_bytes)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            raise CaseBriefIntegrityError(
                "partner attempt contract does not resolve"
            ) from exc
        if hashlib.sha256(contract_bytes).hexdigest() != attempt["contract_sha256"]:
            _fail("partner attempt contract sha256 mismatch")
        for field in (
            "query_hash",
            "run_id",
            "endpoint_or_document",
            "http_status",
            "normalization_status",
        ):
            if contract.get(field) != attempt[field]:
                _fail(f"partner attempt contract {field} mismatch")
        coverage_path = contract_path.parent / "coverage.json"
        try:
            coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise CaseBriefIntegrityError(
                "partner attempt coverage does not resolve"
            ) from exc
        if (
            coverage.get("status") != attempt["coverage_status"]
            or coverage.get("stop_reason") != attempt["stop_reason"]
        ):
            _fail("partner attempt coverage mismatch")
        validated.append(attempt)
    return validated


def _validate_partner_detail(
    brief: Mapping[str, Any],
    root: Path,
) -> None:
    detail = _exact(brief["partner_detail"], _PARTNER_DETAIL_KEYS, "partner_detail")
    state = detail["state"]
    if state not in PARTNER_DETAIL_STATES:
        _fail("partner_detail.state invalid")
    reason = detail["reason"]
    source_id = detail["source_id"]
    if source_id not in {"un_comtrade", "wits_trade", UNAVAILABLE}:
        _fail("partner_detail.source_id invalid")
    if detail["partner_snapshot_id"] != brief["partner_snapshot_id"]:
        _fail("partner_detail partner_snapshot_id mismatch")
    expected_unit = [brief["hs6"], "imports", "2024"]
    if detail["unit_key"] != expected_unit:
        _fail("partner_detail.unit_key mismatch")
    _text(detail["basis"], "partner_detail.basis")
    allow_empty = state == "PARTNER_DETAIL_MISSING" and reason == "NOT_ACQUIRED"
    attempts = _validate_partner_attempts(
        root, detail["attempts"], allow_empty=allow_empty
    )

    snapshot_id = detail["partner_snapshot_id"]
    snapshot = (
        None
        if snapshot_id == UNAVAILABLE
        else _partner_snapshot(root, str(snapshot_id))
    )
    unit = None
    if snapshot is not None:
        unit = next(
            (
                row
                for row in snapshot.get("coverage", {}).get("units", [])
                if row.get("unit_key") == expected_unit
            ),
            None,
        )

    if state == "PARTNER_DETAIL_MISSING":
        if reason not in PARTNER_DETAIL_MISSING_REASONS:
            _fail("partner_detail MISSING requires a typed reason")
        if detail["observed_partner_rows"] != UNAVAILABLE:
            _fail("partner_detail MISSING cannot report observed rows")
        if reason == "NOT_ACQUIRED":
            if attempts or snapshot is not None or source_id != UNAVAILABLE:
                _fail("partner_detail NOT_ACQUIRED cannot claim a stored unit")
            return
        if not attempts:
            _fail("partner_detail MISSING requires a stored attempt")
        if reason == "PARTNER_DESCRIPTIONS_UNAVAILABLE" and not any(
            attempt["normalization_status"] == "NORMALIZED"
            and attempt["stop_reason"] == reason
            and attempt["coverage_status"] == "INCOMPLETE"
            for attempt in attempts
        ):
            _fail(
                "PARTNER_DESCRIPTIONS_UNAVAILABLE requires a NORMALIZED "
                "attempt with the matching stop reason"
            )
        if snapshot is not None:
            exclusions = snapshot.get("transformation_record", {}).get(
                "exclusions", []
            )
            if not any(
                row.get("unit_key") == expected_unit
                and row.get("reason") == reason
                for row in exclusions
            ):
                _fail("partner_detail MISSING snapshot exclusion mismatch")
            if unit is not None and unit.get("status") == "COMPLETE":
                _fail("partner_detail MISSING contradicts a COMPLETE unit")
        if reason == "FORMAT_NOT_PARSEABLE" and not any(
            row["normalization_status"] in {"UNPARSED", "PENDING"}
            and row["coverage_status"] == "COMPLETE"
            for row in attempts
        ):
            _fail("partner_detail MISSING lacks an unparsed stored attempt")
        if reason == "HTTP_ERROR" and not any(
            isinstance(row["http_status"], int) and row["http_status"] >= 400
            for row in attempts
        ):
            _fail("partner_detail HTTP_ERROR lacks an HTTP failure")
        return

    if reason is not None:
        _fail("observed partner states require reason null")
    if snapshot is None or unit is None or unit.get("status") != "COMPLETE":
        _fail(f"partner_detail {state} requires a COMPLETE snapshot unit")
    if snapshot.get("source_id") != source_id:
        _fail("partner_detail source_id does not match snapshot")
    rows = [
        row
        for row in snapshot.get("rows", [])
        if row.get("hs6") == brief["hs6"]
        and row.get("flow") == "imports"
        and str(row.get("partner", "")).casefold() not in {"world", "wld"}
    ]
    if state == "PARTNER_DETAIL_OBSERVED":
        if not rows or detail["observed_partner_rows"] != len(rows):
            _fail("partner_detail OBSERVED row count mismatch")
        if (
            source_id == "un_comtrade"
            and any(
                row.get("hs_revision") != brief["hs_revision"]
                for row in rows
            )
        ):
            _fail("partner detail revision mismatch")
        return

    if rows or detail["observed_partner_rows"] != 0:
        _fail("partner_detail ZERO contradicts stored partner rows")
    source_attempts = [row for row in attempts if row["source_id"] == source_id]
    if not source_attempts or not any(
        row["normalization_status"] == "NORMALIZED_EMPTY"
        and row["coverage_status"] == "COMPLETE"
        for row in source_attempts
    ):
        _fail("partner_detail ZERO requires a normalized-empty COMPLETE unit")
    if any(
        row["normalization_status"] in {"UNPARSED", "PENDING"}
        for row in source_attempts
    ):
        _fail("partner_detail ZERO cannot use an unparsed unit")


def _verify_spans(
    brief: Mapping[str, Any],
    documents: Mapping[str, Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    spans = brief["spans"]
    if not isinstance(spans, list):
        _fail("spans must be a list")
    by_id: dict[str, Mapping[str, Any]] = {}
    for raw in spans:
        span = _exact(raw, _SPAN_KEYS, "span")
        span_id = _text(span["span_id"], "span.span_id")
        if span_id in by_id:
            _fail("span ids must be unique")
        document_id = _text(span["document_id"], "span.document_id")
        record = documents.get(document_id)
        if record is None or record.get("coverage", {}).get("status") != "COMPLETE":
            _fail(f"span document is not COMPLETE: {document_id}")
        page_index = span["page_index"]
        line_index = span["line_index"]
        if (
            type(page_index) is not int
            or page_index < 1
            or type(line_index) is not int
            or line_index < 1
        ):
            _fail("span address must use positive one-based indexes")
        try:
            page = record["pages"][page_index - 1]
            if page.get("page_index") != page_index:
                raise KeyError("page_index")
            line = page["lines"][line_index - 1]
        except (KeyError, IndexError, TypeError) as exc:
            raise CaseBriefIntegrityError(
                "span address does not resolve"
            ) from exc
        text = _text(span["span_text"], "span.span_text")
        if not isinstance(line, str) or text not in line:
            _fail("span must be a verified verbatim substring")
        if span["text_order"] not in {"logical", "visual"}:
            _fail("span text_order invalid")
        by_id[span_id] = span
    return by_id


def validate_case_brief(
    record: Mapping[str, Any],
    *,
    root: Path = PROJECT_ROOT,
    documents: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    """Validate one CaseBrief against stored DocumentRecord lines."""
    brief = _exact(record, _TOP_KEYS, "CaseBrief")
    _reject_forbidden(brief)
    if brief["schema_version"] != SCHEMA_VERSION:
        _fail("CaseBrief schema_version must be 1.1.0")
    hs6 = _text(brief["hs6"], "hs6")
    if len(hs6) != 6 or not hs6.isdigit():
        _fail("hs6 must be six digits")
    opportunity_id = _text(brief["opportunity_id"], "opportunity_id")
    if opportunity_id != f"SAU-H6-{hs6}":
        _fail("opportunity_id mismatch")
    if brief["brief_id"] != f"CASE-BRIEF-{opportunity_id}-v1":
        _fail("brief_id mismatch")
    if brief["hs_revision"] != "H6":
        _fail("hs_revision must be H6")
    if brief["trade_series_rule"] != TRADE_SERIES_RULE:
        _fail("trade_series_rule mismatch")
    for field in (
        "universe_snapshot_id",
        "commercial_name_en",
        "commercial_name_ar",
        "application_boundary",
        "authority_note",
    ):
        _text(brief[field], field)
    _text(brief["partner_snapshot_id"], "partner_snapshot_id", unavailable=True)
    _validate_partner_detail(brief, root)
    if brief["name_basis"] not in {
        "WCO_HS_2022_LEGAL_TEXT",
        "ANALYST_DESCRIPTION",
    }:
        _fail("name_basis invalid")
    if brief["name_basis_ar"] != "ANALYST_TRANSLATION":
        _fail("name_basis_ar must disclose analyst translation")
    if brief["decision_object_status"] not in {
        "generic_hs6_only",
        "partially_resolved",
        "resolved",
    }:
        _fail("decision_object_status invalid")

    loaded_documents = dict(documents or _document_records(root))
    evidence_rows = brief["document_evidence"]
    if not isinstance(evidence_rows, list) or not evidence_rows:
        _fail("document_evidence must be a non-empty list")
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    evidence_by_document: dict[str, Mapping[str, Any]] = {}
    for raw in evidence_rows:
        evidence = _exact(
            raw, _DOCUMENT_EVIDENCE_KEYS, "document_evidence"
        )
        evidence_id = _text(evidence["evidence_id"], "evidence_id")
        document_id = _text(evidence["document_id"], "document_id")
        document = loaded_documents.get(document_id)
        if (
            evidence_id in evidence_by_id
            or document_id in evidence_by_document
            or document is None
            or document.get("coverage", {}).get("status") != "COMPLETE"
        ):
            _fail("document evidence identity unresolved or duplicate")
        supports = evidence["supports"]
        if (
            not isinstance(supports, list)
            or not supports
            or supports != sorted(set(supports))
            or any(code not in SUPPORT_CODES for code in supports)
        ):
            _fail("document evidence support codes invalid")
        declared_supports = set(
            document.get("declared", {}).get("supports", [])
        )
        if not set(supports) <= declared_supports:
            _fail("document evidence exceeds DocumentRecord supports")
        _text(evidence["period"], "document_evidence.period", unavailable=True)
        evidence_by_id[evidence_id] = evidence
        evidence_by_document[document_id] = evidence

    spans = _verify_spans(brief, loaded_documents)
    known_span_ids = set(spans)
    if any(
        span["document_id"] not in evidence_by_document
        for span in spans.values()
    ):
        _fail("span document must have a document_evidence row")
    if (
        brief["name_basis"] == "WCO_HS_2022_LEGAL_TEXT"
        and not any(
            "TARGET_PRODUCT_IDENTITY" in evidence["supports"]
            and any(
                span["document_id"] == evidence["document_id"]
                for span in spans.values()
            )
            for evidence in evidence_rows
        )
    ):
        _fail("WCO name basis requires a verified identity span")

    capability = _exact(brief["capability"], _CAPABILITY_KEYS, "capability")
    for field in ("verified_present", "same_process_family"):
        fact = _exact(capability[field], _FACT_KEYS, f"capability.{field}")
        value = fact["value"]
        if value != UNAVAILABLE and not isinstance(value, bool):
            _fail(f"capability.{field} must be boolean or UNAVAILABLE")
        cited = _span_ids(
            fact["span_ids"],
            f"capability.{field}",
            known_span_ids,
            required=isinstance(value, bool),
        )
        if value == UNAVAILABLE and cited:
            _fail(f"capability.{field} UNAVAILABLE cannot cite spans")

    signals = capability["coarse_adjacency_signals"]
    if not isinstance(signals, list):
        _fail("coarse_adjacency_signals must be a list")
    for raw in signals:
        signal = _exact(raw, _SIGNAL_KEYS, "coarse signal")
        if signal["signal_type"] not in _SIGNAL_TYPES:
            _fail("coarse signal type invalid")
        _text(signal["description"], "coarse signal description")
        _span_ids(
            signal["span_ids"],
            "coarse signal",
            known_span_ids,
            required=True,
        )

    producers = capability["producer_evidence"]
    if not isinstance(producers, list):
        _fail("producer_evidence must be a list")
    for raw in producers:
        producer = _exact(raw, _PRODUCER_KEYS, "producer evidence")
        _text(producer["producer"], "producer")
        _text(producer["process_family"], "process_family")
        process_route = _text(
            producer["process_route"], "process_route", unavailable=True
        )
        standards = producer["published_standards"]
        if standards != UNAVAILABLE and (
            not isinstance(standards, list)
            or not standards
            or any(not isinstance(item, str) or not item for item in standards)
        ):
            _fail("published_standards invalid")
        capacity = producer["installed_capacity_tpy"]
        if capacity != UNAVAILABLE and (
            isinstance(capacity, bool)
            or not isinstance(capacity, (int, float))
            or capacity <= 0
        ):
            _fail("nameplate must be positive or UNAVAILABLE")
        required = (
            process_route != UNAVAILABLE
            or standards != UNAVAILABLE
            or capacity != UNAVAILABLE
        )
        _span_ids(
            producer["span_ids"],
            "producer nameplate/process fact",
            known_span_ids,
            required=required,
        )
        if capacity != UNAVAILABLE and not producer["span_ids"]:
            _fail("numeric nameplate requires a span")

    profiles = sector_profiles_config()["profiles"]
    profile = brief["sector_profile"]
    if profile not in profiles:
        _fail("sector_profile invalid")
    dimensions = capability["public_dimension_states"]
    if not isinstance(dimensions, Mapping) or set(dimensions) != set(
        profiles[profile]["weights"]
    ):
        _fail("dimension set mismatch")
    for name, raw in dimensions.items():
        dimension = _exact(raw, _DIMENSION_KEYS, f"dimension {name}")
        state = dimension["state"]
        if state != "U" and (
            isinstance(state, bool)
            or not isinstance(state, int)
            or not 0 <= state <= 3
        ):
            _fail(f"dimension {name} state invalid")
        cited = _span_ids(
            dimension["span_ids"],
            f"dimension {name}",
            known_span_ids,
            required=state != "U",
        )
        if state == "U" and cited:
            _fail(f"dimension {name} U cannot cite spans")

    gates = capability["profile_hard_gates"]
    expected_gates = set(profiles[profile]["hard_gates"])
    if not isinstance(gates, Mapping) or set(gates) != expected_gates:
        _fail("profile gate set mismatch")
    unresolved = capability["unresolved_hard_gates"]
    if (
        not isinstance(unresolved, list)
        or any(not isinstance(name, str) for name in unresolved)
        or len(unresolved) != len(set(unresolved))
    ):
        _fail("unresolved_hard_gates must be unique")
    for name, raw in gates.items():
        gate = _exact(raw, _GATE_KEYS, f"gate {name}")
        status = gate["status"]
        if status not in {"RESOLVED", "UNAVAILABLE", "KNOWN_FAILURE"}:
            _fail(f"gate {name} status invalid")
        cited = _span_ids(
            gate["span_ids"],
            f"gate {name}",
            known_span_ids,
            required=status != "UNAVAILABLE",
        )
        if status == "UNAVAILABLE" and cited:
            _fail(f"gate {name} UNAVAILABLE cannot cite spans")
    if set(unresolved) != {
        name
        for name, raw in gates.items()
        if raw["status"] == "UNAVAILABLE"
    }:
        _fail("unresolved_hard_gates must match unavailable profile gates")


def load_case_brief(
    path: Path,
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Load and validate one canonical CaseBrief."""
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CaseBriefIntegrityError(f"cannot load CaseBrief: {path}") from exc
    if not isinstance(record, dict):
        _fail("CaseBrief must contain an object")
    validate_case_brief(record, root=root)
    if path.name != f"{record['brief_id']}.json":
        _fail("CaseBrief file name must equal brief_id")
    return record
