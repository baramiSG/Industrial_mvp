"""Deterministic CaseBrief projection to PublicSnapshot 2.1.0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.public_snapshot import validate_public_snapshot

from .brief import UNAVAILABLE, validate_case_brief

_ISO_DATE_PREFIX_LENGTH = len("YYYY-MM-DD")


def canonical_bytes(record: Any) -> bytes:
    """Return canonical governed JSON bytes."""
    return (
        json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _scaled(value: Any) -> float | str:
    numeric = _number(value)
    if numeric is None or numeric <= 0:
        return UNAVAILABLE
    return round(numeric / 1_000_000, 6)


def _unit_value(value: Any, weight: Any) -> float | None:
    numeric_value = _number(value)
    numeric_weight = _number(weight)
    if (
        numeric_value is None
        or numeric_weight is None
        or numeric_value <= 0
        or numeric_weight <= 0
    ):
        return None
    return round(numeric_value / (numeric_weight / 1_000), 1)


def derive_trade(
    universe_rows: list[Mapping[str, Any]],
    hs6: str,
    hs_revision: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Project one latest-revision HS6 series without revision splicing."""
    selected = [
        row
        for row in universe_rows
        if row.get("hs6") == hs6 and row.get("hs_revision") == hs_revision
    ]
    years = sorted(
        {
            int(row["year"])
            for row in selected
            if isinstance(row.get("year"), int)
        }
    )
    if not years:
        raise ValueError(f"no {hs_revision} universe rows for {hs6}")
    trade: list[dict[str, Any]] = []
    missing_import_years: list[int] = []
    import_quantities_present = True
    for year in years:
        by_flow: dict[str, Mapping[str, Any]] = {}
        for row in selected:
            if row.get("year") != year or row.get("flow") not in {
                "imports",
                "exports",
            }:
                continue
            flow = str(row["flow"])
            if flow in by_flow:
                raise ValueError(f"duplicate {flow} row for {hs6}/{year}")
            by_flow[flow] = row
        imports = by_flow.get("imports")
        exports = by_flow.get("exports")
        if imports is None:
            missing_import_years.append(year)
        import_weight = imports.get("net_weight") if imports else None
        import_quantity = _scaled(import_weight)
        if import_quantity == UNAVAILABLE:
            import_quantities_present = False
        item: dict[str, Any] = {
            "year": year,
            "imports_usd_m": (
                _scaled(imports.get("trade_value"))
                if imports
                else UNAVAILABLE
            ),
            "imports_kt": import_quantity,
            "exports_usd_m": (
                _scaled(exports.get("trade_value"))
                if exports
                else UNAVAILABLE
            ),
            "exports_kt": (
                _scaled(exports.get("net_weight"))
                if exports
                else UNAVAILABLE
            ),
        }
        import_uv = _unit_value(
            imports.get("trade_value") if imports else None,
            import_weight,
        )
        export_uv = _unit_value(
            exports.get("trade_value") if exports else None,
            exports.get("net_weight") if exports else None,
        )
        if import_uv is not None:
            item["import_uv_usd_t"] = import_uv
        if export_uv is not None:
            item["export_uv_usd_t"] = export_uv
        trade.append(item)
    quality = {
        "flow_basis": "gross",
        "reexports_separated": False,
        "domestic_origin_exports_separated": False,
        "missing_years": missing_import_years,
        "monthly_partner_tariff_line_available": False,
        "quantity_comparable": import_quantities_present,
        "execution_cap": (
            "DEGRADED where continuity or tariff-line detail is required; "
            "2021 (H5) excluded by the latest-revision H6 rule"
        ),
    }
    return trade, quality


def derive_partner_observations(
    partner_snapshot: Mapping[str, Any] | None,
    hs6: str,
) -> tuple[list[dict[str, Any]] | str, Mapping[str, Any] | None]:
    """Project source rows for one HS6, excluding the World aggregate."""
    if partner_snapshot is None:
        return UNAVAILABLE, None
    evidence = next(
        (
            passport
            for passport in partner_snapshot.get("evidence", [])
            if passport.get("query_contract", {}).get("unit_key")
            == [hs6, "imports", "2024"]
        ),
        None,
    )
    if evidence is None:
        return UNAVAILABLE, None
    source_id = str(partner_snapshot.get("source_id", "wits_trade"))
    source_tag = "COMTRADE" if source_id == "un_comtrade" else "WITS"
    rows: list[dict[str, Any]] = []
    for source in partner_snapshot.get("rows", []):
        if (
            source.get("hs6") != hs6
            or source.get("flow") != "imports"
            or str(source.get("partner", "")).casefold() in {"world", "wld"}
        ):
            continue
        value = _scaled(source.get("trade_value"))
        quantity = _scaled(source.get("net_weight"))
        rows.append(
            {
                "year": int(source["year"]),
                "partner": str(source["partner"]),
                "flow": "imports",
                "trade_value_usd_m": value,
                "net_weight_kt": quantity,
                "quantity_unit": "kt",
                "validity_flags": {
                    "value_valid": value != UNAVAILABLE,
                    "net_weight_valid": quantity != UNAVAILABLE,
                    "quantity_comparable": quantity != UNAVAILABLE,
                },
                "gross_flow": True,
                "source_evidence_id": f"P-{source_tag}-{hs6}-PARTNERS",
            }
        )
    if not rows:
        return UNAVAILABLE, None
    return sorted(rows, key=lambda row: (row["year"], row["partner"])), evidence


def _retrieval_date(value: Any) -> str:
    if not isinstance(value, str) or len(value) < _ISO_DATE_PREFIX_LENGTH:
        return UNAVAILABLE
    return value[:_ISO_DATE_PREFIX_LENGTH]


def _universe_passport(
    universe: Mapping[str, Any],
    hs6: str,
    flow: str,
) -> dict[str, Any]:
    source = next(
        (
            passport
            for passport in universe.get("evidence", [])
            if passport.get("query_contract", {}).get("unit_key")
            == [flow, "2024"]
        ),
        None,
    )
    if source is None:
        raise ValueError(f"universe passport missing for {flow}")
    suffix = "M" if flow == "imports" else "X"
    supports = ["TRADE_QUANTITY", "TRADE_VALUE"]
    if flow == "exports":
        supports.append("EXPORT_IMPORT_RATIO")
    return {
        "evidence_id": f"P-COMTRADE-{hs6}-{suffix}",
        "title": f"UN Comtrade Saudi {flow} rows for HS {hs6}",
        "source": str(
            source.get("source_identity", {}).get(
                "authority", universe.get("source_id", "UN Comtrade")
            )
        ),
        "url": str(source["retrieval"]["endpoint_or_document"]),
        "period": "2022/2023/2024",
        "retrieved_at": _retrieval_date(source["retrieval"]["retrieved_at"]),
        "status": "calculated",
        "evidence_class": str(source.get("evidence_class", "B")),
        "synthetic_flag": False,
        "supports": sorted(supports),
        "transformation": (
            "LATEST_REVISION_ONLY H6 rows; trade value divided by 1,000,000 "
            "to USD million and net weight divided by 1,000,000 to kt."
        ),
        "reviewer_status": str(
            source.get(
                "reviewer_status",
                "unconfirmed_by_responsible_authority",
            )
        ),
        "contradiction": None,
    }


def _document_passport(
    evidence: Mapping[str, Any],
    document: Mapping[str, Any],
) -> dict[str, Any]:
    acquired = (
        document.get("evidence", [{}])[0]
        if isinstance(document.get("evidence"), list)
        and document.get("evidence")
        else {}
    )
    raw = document["raw_artifact_ref"]
    return {
        "evidence_id": evidence["evidence_id"],
        "title": str(document["declared"]["title_text"]),
        "source": str(document["source_id"]),
        "url": str(raw["endpoint_or_document"]),
        "period": evidence["period"],
        "retrieved_at": _retrieval_date(raw["retrieved_at"]),
        "status": "observed",
        "evidence_class": str(
            document["declared"]["evidence_class_target"]
        ),
        "synthetic_flag": False,
        "supports": sorted(evidence["supports"]),
        "transformation": (
            f"Verbatim span from DocumentRecord {document['document_id']}."
        ),
        "reviewer_status": str(
            acquired.get(
                "reviewer_status",
                "unconfirmed_by_responsible_authority",
            )
        ),
        "contradiction": None,
    }


def _partner_passport(
    source: Mapping[str, Any],
    hs6: str,
    source_id: str,
    observed_partner_rows: int,
) -> dict[str, Any]:
    source_tag = "COMTRADE" if source_id == "un_comtrade" else "WITS"
    source_title = "UN Comtrade" if source_id == "un_comtrade" else "WITS"
    return {
        "evidence_id": f"P-{source_tag}-{hs6}-PARTNERS",
        "title": (
            f"{source_title} Saudi 2024 import partner rows for HS {hs6}"
        ),
        "source": str(
            source.get("source_identity", {}).get(
                "authority", source.get("source_id", "World Bank WITS")
            )
        ),
        "url": str(source["retrieval"]["endpoint_or_document"]),
        "period": "2024",
        "retrieved_at": _retrieval_date(source["retrieval"]["retrieved_at"]),
        "status": "calculated",
        "evidence_class": str(source.get("evidence_class", "B")),
        "synthetic_flag": False,
        "supports": ["SUPPLIER_CONCENTRATION"],
        "transformation": (
            "World aggregate excluded; value divided by 1,000,000 to USD "
            "million and net weight divided by 1,000,000 to kt. "
            "Partner detail state: PARTNER_DETAIL_OBSERVED "
            f"({source_id}; {observed_partner_rows} partner rows)."
        ),
        "reviewer_status": str(
            source.get(
                "reviewer_status",
                "unconfirmed_by_responsible_authority",
            )
        ),
        "contradiction": None,
    }


def _source_label(source_id: str) -> tuple[str, str, str]:
    if source_id == "un_comtrade":
        return "COMTRADE", "UN Comtrade", "B"
    if source_id == "wits_trade":
        return "WITS", "World Bank WITS", "B"
    raise ValueError(f"unsupported partner source: {source_id}")


def _attempt_passports(
    brief: Mapping[str, Any],
    *,
    root: Path,
) -> list[dict[str, Any]]:
    state = str(brief["partner_detail"]["state"])
    hs6 = str(brief["hs6"])
    complete_attempt = next(
        (
            attempt
            for attempt in brief["partner_detail"]["attempts"]
            if attempt["coverage_status"] == "COMPLETE"
            and attempt["normalization_status"] == "NORMALIZED"
        ),
        None,
    )
    passports: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    for attempt in brief["partner_detail"]["attempts"]:
        is_attempt = (
            state == "PARTNER_DETAIL_MISSING"
            or attempt["normalization_status"] in {"UNPARSED", "PENDING"}
            or attempt["coverage_status"] != "COMPLETE"
            or (
                isinstance(attempt["http_status"], int)
                and attempt["http_status"] >= 400
            )
        )
        if not is_attempt:
            continue
        source_id = str(attempt["source_id"])
        source_tag, source_title, evidence_class = _source_label(source_id)
        source_counts[source_id] = source_counts.get(source_id, 0) + 1
        suffix = (
            ""
            if source_counts[source_id] == 1
            else f"-{source_counts[source_id]}"
        )
        contract = json.loads(
            (root / str(attempt["contract_path"])).read_text(encoding="utf-8")
        )
        http_status = attempt["http_status"]
        attempt_reason = (
            "FORMAT_NOT_PARSEABLE"
            if attempt["normalization_status"] in {"UNPARSED", "PENDING"}
            else attempt["stop_reason"] or brief["partner_detail"]["reason"]
        )
        if (
            state == "PARTNER_DETAIL_OBSERVED"
            and attempt["source_id"] == "un_comtrade"
            and attempt["stop_reason"] == "PARTNER_DESCRIPTIONS_UNAVAILABLE"
            and {
                item.get("key"): item.get("value")
                for item in contract.get("query_contract", {}).get(
                    "parameters", []
                )
            }.get("partner_dimension_query")
            == ""
        ):
            attempt_reason = "VARIANT_NOT_TRANSMITTED"
        if state == "PARTNER_DETAIL_OBSERVED":
            if complete_attempt is None:
                raise ValueError(
                    "OBSERVED partner detail requires a COMPLETE unit"
                )
            marker = "PARTNER_DETAIL_ATTEMPT_SUPERSEDED"
            outcome = (
                "superseded by COMPLETE unit "
                f"{complete_attempt['source_id']}/"
                f"{str(complete_attempt['query_hash'])[:12]}/"
                f"{complete_attempt['run_id']}. "
            )
        else:
            marker = "PARTNER_DETAIL_MISSING"
            outcome = "no partner rows were parsed. "
        passports.append(
            {
                "evidence_id": (
                    f"P-{source_tag}-{hs6}-PARTNERS-ATTEMPT{suffix}"
                ),
                "title": (
                    f"{source_title} Saudi 2024 import partner attempt "
                    f"for HS {hs6}"
                ),
                "source": source_title,
                "url": str(attempt["endpoint_or_document"]),
                "period": "2024",
                "retrieved_at": _retrieval_date(contract.get("retrieved_at")),
                "status": "unresolved",
                "evidence_class": evidence_class,
                "synthetic_flag": False,
                "supports": ["SUPPLIER_CONCENTRATION"],
                "transformation": (
                    f"{marker}:"
                    f"{attempt_reason}; unit "
                    f"{source_id}/{str(attempt['query_hash'])[:12]}/"
                    f"{attempt['run_id']}; http_status {http_status}; "
                    "normalization_status "
                    f"{attempt['normalization_status']}; {outcome}"
                    "This passport evidences the attempt, "
                    "not trade."
                ),
                "reviewer_status": "unconfirmed_by_responsible_authority",
                "contradiction": None,
            }
        )
    return passports


def _zero_passport(
    brief: Mapping[str, Any],
    *,
    root: Path,
) -> dict[str, Any]:
    detail = brief["partner_detail"]
    source_id = str(detail["source_id"])
    source_tag, source_title, evidence_class = _source_label(source_id)
    attempt = next(
        row
        for row in detail["attempts"]
        if row["source_id"] == source_id
        and row["normalization_status"] == "NORMALIZED_EMPTY"
    )
    contract = json.loads(
        (root / str(attempt["contract_path"])).read_text(encoding="utf-8")
    )
    hs6 = str(brief["hs6"])
    return {
        "evidence_id": f"P-{source_tag}-{hs6}-PARTNERS-ZERO",
        "title": (
            f"{source_title} Saudi 2024 import partner zero-row response "
            f"for HS {hs6}"
        ),
        "source": source_title,
        "url": str(attempt["endpoint_or_document"]),
        "period": "2024",
        "retrieved_at": _retrieval_date(contract.get("retrieved_at")),
        "status": "observed",
        "evidence_class": evidence_class,
        "synthetic_flag": False,
        "supports": ["SUPPLIER_CONCENTRATION"],
        "transformation": (
            "PARTNER_TRADE_OBSERVED_ZERO; unit "
            f"{source_id}/{str(attempt['query_hash'])[:12]}/"
            f"{attempt['run_id']}; provider count 0; normalized response "
            "contained zero partner rows."
        ),
        "reviewer_status": "unconfirmed_by_responsible_authority",
        "contradiction": None,
    }


def derive_passports(
    brief: Mapping[str, Any],
    universe: Mapping[str, Any],
    partner_passport: Mapping[str, Any] | None,
    documents: Mapping[str, Mapping[str, Any]],
    *,
    root: Path,
) -> list[dict[str, Any]]:
    """Build PublicSnapshot evidence passports from governed inputs."""
    hs6 = str(brief["hs6"])
    passports = [
        _universe_passport(universe, hs6, "imports"),
        _universe_passport(universe, hs6, "exports"),
    ]
    if partner_passport is not None:
        detail = brief["partner_detail"]
        passports.append(
            _partner_passport(
                partner_passport,
                hs6,
                str(detail["source_id"]),
                int(detail["observed_partner_rows"]),
            )
        )
    passports.extend(_attempt_passports(brief, root=root))
    if brief["partner_detail"]["state"] == "PARTNER_TRADE_OBSERVED_ZERO":
        passports.append(_zero_passport(brief, root=root))
    passports.extend(
        _document_passport(evidence, documents[evidence["document_id"]])
        for evidence in brief["document_evidence"]
    )
    return sorted(passports, key=lambda row: row["evidence_id"])


def _evidence_ids_for_spans(
    span_ids: list[str],
    spans: Mapping[str, Mapping[str, Any]],
    evidence_by_document: Mapping[str, str],
) -> list[str]:
    return sorted(
        {
            evidence_by_document[spans[span_id]["document_id"]]
            for span_id in span_ids
        }
    )


def _capability(
    brief: Mapping[str, Any],
    documents: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    source = brief["capability"]
    spans = {row["span_id"]: row for row in brief["spans"]}
    evidence_by_document = {
        row["document_id"]: row["evidence_id"]
        for row in brief["document_evidence"]
    }

    def evidence_ids(span_ids: list[str]) -> list[str]:
        return _evidence_ids_for_spans(
            span_ids, spans, evidence_by_document
        )

    producers = []
    for producer in source["producer_evidence"]:
        ids = evidence_ids(producer["span_ids"])
        classes = [
            str(documents[spans[span_id]["document_id"]]["declared"][
                "evidence_class_target"
            ])
            for span_id in producer["span_ids"]
        ]
        capacity = producer["installed_capacity_tpy"]
        producers.append(
            {
                "producer": producer["producer"],
                "process_family": producer["process_family"],
                "process_route": producer["process_route"],
                "published_standards": producer["published_standards"],
                "installed_capacity_tpy": capacity,
                "nameplate_status": (
                    "observed" if capacity != UNAVAILABLE else "unresolved"
                ),
                "nameplate_source_evidence_id": (
                    ids[0] if capacity != UNAVAILABLE else UNAVAILABLE
                ),
                "evidence_class": min(classes or ["E"]),
                "evidence_ids": ids,
            }
        )
    return {
        "verified_present": source["verified_present"]["value"],
        "same_process_family": source["same_process_family"]["value"],
        "coarse_adjacency_signals": [
            {
                "signal_type": row["signal_type"],
                "description": row["description"],
                "evidence_ids": evidence_ids(row["span_ids"]),
            }
            for row in source["coarse_adjacency_signals"]
        ],
        "producer_evidence": producers,
        "public_dimension_states": {
            name: row["state"]
            for name, row in source["public_dimension_states"].items()
        },
        "profile_hard_gates": {
            name: {
                "status": row["status"],
                "evidence_ids": evidence_ids(row["span_ids"]),
            }
            for name, row in source["profile_hard_gates"].items()
        },
        "unresolved_hard_gates": [
            {"name": name, "state": "unresolved", "evidence_ids": []}
            for name in source["unresolved_hard_gates"]
        ],
    }


def _hard_exclusion_inputs() -> dict[str, Any]:
    return {
        "heterogeneous_residual_code": {
            "commercial_product_separable": UNAVAILABLE,
            "product_level_evidence_available": UNAVAILABLE,
            "evidence_ids": [],
        },
        "downside_market_below_mes": {
            "sustainable_downside_demand_kt": UNAVAILABLE,
            "minimum_efficient_scale_kt": UNAVAILABLE,
            "credible_export_contract": UNAVAILABLE,
            "evidence_ids": [],
        },
        "unsatisfiable_hard_gate": {
            "gate_domain": UNAVAILABLE,
            "gate_satisfiability": UNAVAILABLE,
            "evidence_ids": [],
        },
        "idle_equivalent_domestic_capacity": {
            "domestic_specification_equivalent": UNAVAILABLE,
            "qualified_idle_capacity_kt": UNAVAILABLE,
            "target_specification_demand_kt": UNAVAILABLE,
            "binding_market_failure": UNAVAILABLE,
            "evidence_ids": [],
        },
        "transitory_or_measurement_gap": {
            "dominant_cause": UNAVAILABLE,
            "evidence_ids": [],
        },
        "redundancy_or_crowd_out": {
            "competition_finding": UNAVAILABLE,
            "evidence_ids": [],
        },
    }


def build_public_snapshot(
    brief: Mapping[str, Any],
    universe: Mapping[str, Any],
    *,
    partners: Mapping[str, Any] | None,
    documents: Mapping[str, Mapping[str, Any]],
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Build and validate a PublicSnapshot solely from governed inputs."""
    validate_case_brief(brief, root=root, documents=documents)
    if brief["universe_snapshot_id"] != universe.get("snapshot_id"):
        raise ValueError("CaseBrief universe snapshot mismatch")
    if (
        brief["partner_snapshot_id"] != UNAVAILABLE
        and (
            partners is None
            or brief["partner_snapshot_id"] != partners.get("snapshot_id")
        )
    ):
        raise ValueError("CaseBrief partner snapshot mismatch")
    trade, trade_quality = derive_trade(
        list(universe.get("rows", [])),
        str(brief["hs6"]),
        str(brief["hs_revision"]),
    )
    partner_rows, partner_source = derive_partner_observations(
        partners, str(brief["hs6"])
    )
    detail = brief["partner_detail"]
    state = str(detail["state"])
    if state == "PARTNER_DETAIL_OBSERVED" and partner_rows == UNAVAILABLE:
        raise ValueError("PARTNER_DETAIL_OBSERVED contradicts loaded snapshot")
    if state != "PARTNER_DETAIL_OBSERVED" and partner_rows != UNAVAILABLE:
        raise ValueError(f"{state} contradicts loaded snapshot")
    partner_passport_ids: list[str] = []
    if state == "PARTNER_DETAIL_OBSERVED":
        source_tag = (
            "COMTRADE" if detail["source_id"] == "un_comtrade" else "WITS"
        )
        partner_passport_ids.append(
            f"P-{source_tag}-{brief['hs6']}-PARTNERS"
        )
        authority_partner = (
            f"OBSERVED from {detail['source_id']}"
        )
    elif state == "PARTNER_DETAIL_MISSING":
        counts: dict[str, int] = {}
        for attempt in detail["attempts"]:
            source_id = str(attempt["source_id"])
            counts[source_id] = counts.get(source_id, 0) + 1
            tag = "COMTRADE" if source_id == "un_comtrade" else "WITS"
            suffix = "" if counts[source_id] == 1 else f"-{counts[source_id]}"
            partner_passport_ids.append(
                f"P-{tag}-{brief['hs6']}-PARTNERS-ATTEMPT{suffix}"
            )
        authority_partner = (
            f"MISSING ({detail['reason']}) — missing evidence, not zero trade"
        )
    else:
        tag = "COMTRADE" if detail["source_id"] == "un_comtrade" else "WITS"
        partner_passport_ids.append(
            f"P-{tag}-{brief['hs6']}-PARTNERS-ZERO"
        )
        authority_partner = f"OBSERVED ZERO from {detail['source_id']}"
    detail_marker = state
    if detail["reason"] is not None:
        detail_marker += f":{detail['reason']}"
    passport_text = ", ".join(partner_passport_ids) or "no passport"
    trade_quality["execution_cap"] += (
        f" Partner detail: {detail_marker} ({passport_text})."
    )
    as_of = str(universe["as_of_date"])
    record = {
        "schema_version": "2.1.0",
        "snapshot_id": (
            f"PUBLIC-{brief['opportunity_id']}-{as_of}"
        ),
        "as_of_date": as_of,
        "supersedes": UNAVAILABLE,
        "source_boundary": "public",
        "authority_note": (
            f"{brief['authority_note']} Derived from "
            f"{brief['universe_snapshot_id']} rows of HS revision H6 "
            "(2022–2024); the 2021 H5 row is excluded to avoid splicing "
            "revisions. Gross flows; not retained domestic demand. "
            f"Partner detail for 2024 imports is {authority_partner}."
        ),
        "opportunity": {
            "id": brief["opportunity_id"],
            "hs_revision": brief["hs_revision"],
            "hs6": brief["hs6"],
            "national_tariff_line": UNAVAILABLE,
            "sector_profile": brief["sector_profile"],
            "commercial_name_en": brief["commercial_name_en"],
            "commercial_name_ar": brief["commercial_name_ar"],
            "decision_object_status": brief["decision_object_status"],
            "application_boundary": brief["application_boundary"],
            "as_of_date": as_of,
        },
        "trade": trade,
        "trade_quality": trade_quality,
        "partner_observations": partner_rows,
        "domestic_flows": {
            "period_year": max(row["year"] for row in trade),
            "domestic_production_kt": UNAVAILABLE,
            "retained_imports_kt": UNAVAILABLE,
            "domestic_origin_exports_kt": UNAVAILABLE,
            "reexports_kt": UNAVAILABLE,
            "source_evidence_ids": [],
        },
        "criticality_designation": UNAVAILABLE,
        "domestic_capability": _capability(brief, documents),
        "hard_exclusion_inputs": _hard_exclusion_inputs(),
        "decision_inputs": {
            "target_specification_demand": UNAVAILABLE,
            "specification_equivalence": UNAVAILABLE,
            "route_evidence": UNAVAILABLE,
            "monitor_trigger": UNAVAILABLE,
        },
        "evidence": derive_passports(
            brief, universe, partner_source, documents, root=root
        ),
    }
    validate_public_snapshot(record, root=root)
    return record
