from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from ior_mvp.config import PROJECT_ROOT, thresholds_config
from ior_mvp.rules import (
    NOT_CALCULABLE,
    log_change,
    quantity_contribution_share,
    r1d_fires,
    r2_fires,
    r3_fires,
)


LIVE_PUBLIC_ROOT = PROJECT_ROOT / "data" / "snapshots" / "public"
HISTORICAL_V1_ROOT = LIVE_PUBLIC_ROOT / "historical" / "v1"


def load_legacy_snapshot(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Legacy snapshot must be an object: {path}")
    return value


def _rule(
    rule_id: str,
    name: str,
    execution: str,
    fired: bool | None,
    result: str,
    decision_effect: str,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "name": name,
        "execution": execution,
        "fired": fired,
        "result": result,
        "decision_effect": decision_effect,
        "metrics": metrics or {},
    }


def legacy_evaluate_rules(case: dict[str, Any]) -> list[dict[str, Any]]:
    """Frozen test-only characterization of the schema-v1 public ledger."""
    thresholds = thresholds_config()["rules"]
    trade = sorted(case["trade"], key=lambda row: row["year"])
    quality = case["trade_quality"]
    context = case["rule_context"]
    results: list[dict[str, Any]] = []

    results.append(
        _rule(
            "R0",
            "Identity gate",
            "FULL",
            True,
            (
                f"HS revision {case['opportunity']['hs_revision']} and HS6 "
                f"{case['opportunity']['hs6']} are frozen in the snapshot; "
                "specification/application remains separately gated."
            ),
            "Continue to screening while preserving the unresolved decision object.",
        )
    )
    results.append(
        _rule(
            "R1-F",
            "Persistent retained exposure — full",
            "DISABLED" if quality.get("missing_years") else "FULL",
            None if quality.get("missing_years") else False,
            (
                "Full continuity is unavailable and gross flows are not retained imports."
                if quality.get("missing_years")
                else "Full persistence test did not fire."
            ),
            "Do not claim the full persistence rule.",
            {"missing_years": quality.get("missing_years", [])},
        )
    )

    positive_years = [
        row["year"] for row in trade if row.get("imports_usd_m", 0) > 0
    ]
    r1d_fired = r1d_fires(positive_years, thresholds["R1_D"])
    results.append(
        _rule(
            "R1-D",
            "Persistence signal — degraded",
            "DEGRADED",
            r1d_fired,
            (
                f"{len(positive_years)} positive observed years within the "
                "configured window; no interpolation used."
            ),
            "Generate INVESTIGATE only; confidence capped at C.",
            {"positive_years": positive_years, "confidence_cap": "C"},
        )
    )

    if len(trade) >= 2 and all(
        trade[-1].get(key) is not None and trade[-2].get(key) is not None
        for key in ("imports_usd_m", "imports_kt")
    ):
        previous, latest = trade[-2], trade[-1]
        delta_v = log_change(
            latest["imports_usd_m"], previous["imports_usd_m"]
        )
        delta_q = log_change(latest["imports_kt"], previous["imports_kt"])
        uv_latest = latest.get("import_uv_usd_t") or (
            latest["imports_usd_m"] * 1000 / latest["imports_kt"]
        )
        uv_previous = previous.get("import_uv_usd_t") or (
            previous["imports_usd_m"] * 1000 / previous["imports_kt"]
        )
        delta_uv = log_change(uv_latest, uv_previous)
        share = quantity_contribution_share(delta_q, delta_uv)
        quantity_growth = latest["imports_kt"] / previous["imports_kt"] - 1
        fired = r2_fires(
            delta_q,
            share,
            quantity_growth,
            thresholds["R2"],
        )
        results.append(
            _rule(
                "R2",
                "Quantity-led expansion",
                "FULL",
                fired,
                (
                    "Quantity-led expansion signal fires."
                    if fired
                    else (
                        "Value movement is not quantity-led under the "
                        "configured test."
                    )
                ),
                "Separate structural volume growth from price movement.",
                {
                    "from_year": previous["year"],
                    "to_year": latest["year"],
                    "delta_ln_value": round(delta_v, 4),
                    "delta_ln_quantity": round(delta_q, 4),
                    "delta_ln_unit_value": round(delta_uv, 4),
                    "quantity_contribution_share": round(share, 4),
                },
            )
        )
    else:
        results.append(
            _rule(
                "R2",
                "Quantity-led expansion",
                "DISABLED",
                None,
                "Comparable value and quantity observations are unavailable.",
                "No inference.",
            )
        )

    supplier = case.get("supplier_metrics_2024")
    if supplier:
        config = thresholds["R3"]
        hhi = supplier.get("partner_value_hhi")
        largest = supplier.get("largest_supplier_share")
        fired = r3_fires(hhi, largest, config)
        results.append(
            _rule(
                "R3",
                "Supplier concentration",
                "FULL",
                fired,
                (
                    "External supply is concentrated."
                    if fired
                    else "Concentration threshold not met."
                ),
                (
                    "Generate a resilience/diversification review, not an "
                    "automatic localisation recommendation."
                ),
                {
                    "hhi": hhi,
                    "hhi_threshold": float(config["supplier_hhi"]),
                    "largest_supplier_share": (
                        largest if largest is not None else NOT_CALCULABLE
                    ),
                    "largest_supplier_threshold": float(
                        config["largest_supplier_share"]
                    ),
                    "top_two_share": supplier.get("top_two_value_share"),
                },
            )
        )
    else:
        results.append(
            _rule(
                "R3",
                "Supplier concentration",
                "DISABLED",
                None,
                (
                    "Partner concentration metrics are absent from the "
                    "frozen case snapshot."
                ),
                "No concentration inference.",
            )
        )

    results.append(
        _rule(
            "R4-F",
            "Product-tier heterogeneity — full",
            "DISABLED",
            None,
            "Partner-month × tariff-line cells are unavailable.",
            "Do not fit clusters or claim grades.",
        )
    )
    r4d = bool(context.get("r4_degraded_dispersion_signal"))
    results.append(
        _rule(
            "R4-D",
            "Unit-value dispersion — degraded",
            "DEGRADED",
            r4d,
            (
                "Annual/partner product-mix signal is visible."
                if r4d
                else "No material degraded dispersion signal recorded."
            ),
            "Open specification research only; no grade conclusion.",
        )
    )

    r5 = bool(
        context.get("domestic_production_exists")
        and context.get("material_imports_exist")
    )
    r5_config = thresholds["R5"]
    results.append(
        _rule(
            "R5",
            "Domestic supply plus continued imports",
            "DEGRADED",
            r5,
            (
                "Verified domestic capability coexists with material gross imports."
                if r5
                else "Coexistence condition not met."
            ),
            (
                "Test specification, qualification, capacity, price, "
                "application and allocation mismatch."
            ),
            {
                "retained_import_share_of_apparent_consumption": (
                    NOT_CALCULABLE
                ),
                "reason": (
                    "Domestic production quantity and retained-import flow "
                    "are absent from the frozen public snapshot; gross "
                    "imports cannot establish apparent consumption."
                ),
                "threshold": float(
                    r5_config[
                        "retained_import_share_of_apparent_consumption"
                    ]
                ),
            },
        )
    )

    results.extend(
        [
            _rule(
                "R6",
                "Capacity pressure",
                "DISABLED",
                None,
                (
                    "Effective utilisation and target-specification shortage "
                    "are not public."
                ),
                (
                    "Obtain line-level availability, yield, qualification "
                    "share and allocation."
                ),
            ),
            _rule(
                "R7",
                "Latent domestic capacity",
                "DISABLED",
                None,
                (
                    "Idle qualified capacity and specification equivalence "
                    "are not established publicly."
                ),
                "Do not assume latent capacity.",
            ),
            _rule(
                "R8",
                "Committed future demand",
                "DISABLED",
                None,
                (
                    "Awarded/financed demand at the target specification is "
                    "unavailable."
                ),
                (
                    "Keep base, committed and announced demand separate when "
                    "provided."
                ),
            ),
        ]
    )

    r9 = bool(context.get("same_process_family_plus_signal"))
    results.append(
        _rule(
            "R9-S",
            "Coarse incumbent adjacency screen",
            "FULL",
            r9,
            (
                "A verified Saudi plant is in the same process family with "
                "additional capability signals."
                if r9
                else "No defensible coarse adjacency signal."
            ),
            (
                "Open the full line-level capability assessment; do not "
                "publish D* from screening alone."
            ),
        )
    )

    r10 = bool(context.get("strategic_resilience_review"))
    results.append(
        _rule(
            "R10",
            "Strategic criticality",
            "DEGRADED" if r10 else "DISABLED",
            r10 if r10 else None,
            (
                "A resilience review is warranted by concentration; formal "
                "criticality still requires authority confirmation."
                if r10
                else (
                    "No responsible-authority criticality designation is "
                    "present in the demo snapshot."
                )
            ),
            "Keep commercial viability and strategic value separate.",
        )
    )

    latest = trade[-1]
    ratio = latest.get("export_import_value_ratio")
    r11_config = thresholds["R11"]
    r11 = bool(
        context.get("generic_capacity_reject")
        and ratio is not None
        and ratio
        > float(r11_config["generic_capacity_export_import_value_ratio"])
    )
    results.append(
        _rule(
            "R11",
            "Economic exclusion / generic-capacity warning",
            "FULL" if ratio is not None else "DEGRADED",
            r11,
            (
                f"Gross exports are {ratio:.1f}× imports; generic new "
                "capacity cannot be justified from HS6 imports alone."
                if r11
                else "No public-data generic-capacity exclusion fires."
            ),
            (
                "Reject generic support or move only a named specialty "
                "exception to investigation."
            ),
            {
                "export_import_value_ratio": ratio,
                "export_import_value_ratio_threshold": float(
                    r11_config[
                        "generic_capacity_export_import_value_ratio"
                    ]
                ),
            },
        )
    )

    missing = case["public_decision_contract"].get("missing_facts", [])
    results.append(
        _rule(
            "R12",
            "Evidence-value trigger",
            "DEGRADED",
            bool(missing),
            f"{len(missing)} named facts could change the route.",
            (
                "Prioritise the smallest evidence request with a plausible "
                "route effect; quantify EVSI when cost and value inputs exist."
            ),
            {"named_missing_facts": missing},
        )
    )
    return results


def legacy_public_decision(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    contract = case["public_decision_contract"]
    r11 = next(row for row in rules if row["rule_id"] == "R11")
    if case["rule_context"].get("generic_capacity_reject") and r11["fired"]:
        return {
            "state": "REJECT",
            "route_code": 0,
            "route_label": "No intervention for generic capacity",
            "headline": "REJECT — generic capacity support",
            "rationale": contract["route_restriction"],
            "confidence": "C",
            "missing_facts": contract["missing_facts"],
            "conditions": [
                (
                    "Only a named specialty grade/application exception may "
                    "re-enter INVESTIGATE."
                )
            ],
            "kill_conditions": contract["kill_conditions"],
            "synthetic_flag": False,
        }
    return {
        "state": "INVESTIGATE",
        "route_code": None,
        "route_label": "Brownfield priority to test",
        "headline": "INVESTIGATE — binding constraint unresolved",
        "rationale": contract["route_restriction"],
        "confidence": "C",
        "missing_facts": contract["missing_facts"],
        "conditions": [
            (
                "No greenfield or financial support recommendation before "
                "effective capacity and target specification are resolved."
            )
        ],
        "kill_conditions": contract["kill_conditions"],
        "synthetic_flag": False,
    }


def candidate_v2_from_legacy(case: dict[str, Any]) -> dict[str, Any]:
    """Return the exact S08 schema-v2 representation for a frozen v1 case."""
    case = deepcopy(case)
    if case.get("schema_version") == "2.0.0":
        return case
    hs6 = case["opportunity"]["hs6"]
    if hs6 == "721049":
        return _steel_candidate(case)
    if hs6 == "390210":
        return _polypropylene_candidate(case)
    raise ValueError(f"No approved S08 migration oracle for HS {hs6}")


def _base_candidate(
    case: dict[str, Any],
    *,
    opportunity: dict[str, Any],
    disclosed_concentration: dict[str, Any],
    disclosed_dispersion: dict[str, Any],
    domestic_capability: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    filename = f"{case['opportunity']['id']}.json"
    return {
        "schema_version": "2.0.0",
        "snapshot_id": case["snapshot_id"],
        "as_of_date": case["as_of_date"],
        "supersedes": (
            "data/snapshots/public/historical/v1/"
            f"{filename}"
        ),
        "source_boundary": case["source_boundary"],
        "authority_note": case["authority_note"],
        "opportunity": opportunity,
        "trade": case["trade"],
        "trade_quality": case["trade_quality"],
        "partner_observations": "UNAVAILABLE",
        "disclosed_concentration": disclosed_concentration,
        "disclosed_dispersion": disclosed_dispersion,
        "domestic_flows": {
            "period_year": 2024,
            "domestic_production_kt": "UNAVAILABLE",
            "retained_imports_kt": "UNAVAILABLE",
            "domestic_origin_exports_kt": "UNAVAILABLE",
            "reexports_kt": "UNAVAILABLE",
            "source_evidence_ids": [],
        },
        "criticality_designation": "UNAVAILABLE",
        "domestic_capability": domestic_capability,
        "public_decision_contract": case["public_decision_contract"],
        "evidence": evidence,
    }


def _opportunity(case: dict[str, Any]) -> dict[str, Any]:
    old = case["opportunity"]
    return {
        "id": old["id"],
        "hs_revision": old["hs_revision"],
        "hs6": old["hs6"],
        "national_tariff_line": "UNAVAILABLE",
        "sector_profile": old["sector_profile"],
        "commercial_name_en": old["commercial_name_en"],
        "commercial_name_ar": old["commercial_name_ar"],
        "decision_object_status": old["decision_object_status"],
        "application_boundary": old["application_boundary"],
        "as_of_date": case["as_of_date"],
    }


def _passport(
    old: dict[str, Any],
    *,
    period: str,
    transformation: str,
) -> dict[str, Any]:
    return {
        "evidence_id": old["evidence_id"],
        "title": old["title"],
        "source": old["source"],
        "url": old["url"],
        "period": period,
        "retrieved_at": "2026-08-31",
        "status": old["status"],
        "evidence_class": old["evidence_class"],
        "synthetic_flag": False,
        "supports": old["supports"],
        "transformation": transformation,
        "reviewer_status": "unconfirmed_by_responsible_authority",
        "contradiction": old.get("contradiction"),
    }


def _steel_candidate(case: dict[str, Any]) -> dict[str, Any]:
    evidence_by_id = {
        item["evidence_id"]: item for item in case["evidence"]
    }
    evidence = [
        _passport(
            evidence_by_id["S-WITS-721049"],
            period="2021/2023/2024",
            transformation=(
                "Frozen annual world rows; concentration and dispersion are "
                "disclosed aggregates from the methodology worked case."
            ),
        ),
        _passport(
            evidence_by_id["S-UNICOIL-EPD"],
            period="2023/2024",
            transformation="UNAVAILABLE",
        ),
        _passport(
            evidence_by_id["S-UNICOIL-SPEC"],
            period="UNAVAILABLE",
            transformation="UNAVAILABLE",
        ),
        _passport(
            evidence_by_id["S-HADEED"],
            period="UNAVAILABLE",
            transformation="UNAVAILABLE",
        ),
    ]
    old_capability = case["domestic_capability"]
    domestic_capability = {
        "verified_present": True,
        "same_process_family": True,
        "coarse_adjacency_signals": [
            {
                "signal_type": "core_process",
                "description": "continuous hot-dip galvanising",
                "evidence_ids": ["S-UNICOIL-EPD"],
            },
            {
                "signal_type": "core_process",
                "description": "cold rolling and pickling",
                "evidence_ids": ["S-UNICOIL-EPD"],
            },
            {
                "signal_type": "adjacent_output",
                "description": "published ASTM/SASO grades",
                "evidence_ids": [
                    "S-UNICOIL-EPD",
                    "S-UNICOIL-SPEC",
                ],
            },
            {
                "signal_type": "relevant_certification",
                "description": "ISO/IEC 17025 laboratory",
                "evidence_ids": ["S-UNICOIL-EPD"],
            },
        ],
        "producer_evidence": [
            {
                "producer": "UNICOIL",
                "process_family": "coated_steel",
                "process_route": "continuous hot-dip galvanising",
                "published_standards": ["SASO-ASTM A653/A653M"],
                "published_coating_range_g_m2": [45, 350],
                "installed_capacity_tpy": 250000,
                "nameplate_status": "observed",
                "nameplate_source_evidence_id": "S-UNICOIL-EPD",
                "evidence_class": "C",
                "evidence_ids": [
                    "S-UNICOIL-EPD",
                    "S-UNICOIL-SPEC",
                ],
            },
            {
                "producer": "Hadeed",
                "process_family": "coated_steel",
                "process_route": (
                    "cold-rolled galvanised and colour-coated coil "
                    "publicly listed"
                ),
                "published_standards": "UNAVAILABLE",
                "published_coating_range_g_m2": "UNAVAILABLE",
                "installed_capacity_tpy": "UNAVAILABLE",
                "nameplate_status": "unresolved",
                "nameplate_source_evidence_id": "UNAVAILABLE",
                "evidence_class": "C",
                "evidence_ids": ["S-HADEED"],
            },
        ],
        "public_dimension_states": old_capability[
            "public_dimension_states"
        ],
        "unresolved_hard_gates": [
            {"name": name, "state": "unresolved"}
            for name in old_capability["unresolved_hard_gates"]
        ],
    }
    return _base_candidate(
        case,
        opportunity=_opportunity(case),
        disclosed_concentration={
            "value": {
                "year": 2024,
                "flow": "imports",
                "flow_basis": "gross",
                "basis": "value",
                "hhi": 0.36,
                "largest_supplier_share": "UNAVAILABLE",
                "top_two_share": 0.763,
                "top_two_suppliers": ["China", "Korea, Rep."],
                "source_evidence_id": "S-WITS-721049",
                "status": "calculated",
            },
            "quantity": "UNAVAILABLE",
        },
        disclosed_dispersion={
            "year": 2024,
            "basis": "annual_partner",
            "flow_basis": "gross",
            "unit": "USD/t",
            "valid_value_coverage": "UNAVAILABLE",
            "valid_quantity_coverage": "UNAVAILABLE",
            "weighted_median_usd_t": "UNAVAILABLE",
            "iqr_usd_t": "UNAVAILABLE",
            "bulk_band_usd_t": [776, 864],
            "outlier_observation": {
                "partner": "Austria",
                "net_weight_kt": 1.0,
                "unit_value_usd_t": 4179,
            },
            "comparison_observations": "UNAVAILABLE",
            "coverage_note": (
                "Annual partner data permit only the degraded R4-D path; "
                "complete row-level value and comparable-quantity coverage "
                "are not present in the frozen fixture."
            ),
            "source_evidence_id": "S-WITS-721049",
            "status": "calculated",
        },
        domestic_capability=domestic_capability,
        evidence=evidence,
    )


def _polypropylene_candidate(case: dict[str, Any]) -> dict[str, Any]:
    evidence_by_id = {
        item["evidence_id"]: item for item in case["evidence"]
    }
    evidence = [
        _passport(
            evidence_by_id["P-WITS-390210"],
            period="2021/2023/2024",
            transformation=(
                "Frozen annual world rows; export/import ratios and 2024 "
                "average unit values are disclosed calculations from the "
                "methodology worked case."
            ),
        ),
        _passport(
            evidence_by_id["P-SABIC"],
            period="UNAVAILABLE",
            transformation="UNAVAILABLE",
        ),
        _passport(
            evidence_by_id["P-ADVANCED"],
            period="UNAVAILABLE",
            transformation="UNAVAILABLE",
        ),
        _passport(
            evidence_by_id["P-TASNEE"],
            period="UNAVAILABLE",
            transformation="UNAVAILABLE",
        ),
    ]
    old_capability = case["domestic_capability"]
    domestic_capability = {
        "verified_present": True,
        "same_process_family": True,
        "coarse_adjacency_signals": [
            {
                "signal_type": "core_process",
                "description": (
                    "large established Saudi polypropylene production"
                ),
                "evidence_ids": ["P-ADVANCED", "P-TASNEE"],
            },
            {
                "signal_type": "adjacent_output",
                "description": "broad producer grade portfolios",
                "evidence_ids": ["P-SABIC"],
            },
        ],
        "producer_evidence": [
            {
                "producer": "SABIC",
                "process_family": "polypropylene",
                "process_route": "UNAVAILABLE",
                "published_standards": "UNAVAILABLE",
                "portfolio": (
                    "homo, random and impact products and compounds"
                ),
                "installed_capacity_tpy": "UNAVAILABLE",
                "nameplate_status": "unresolved",
                "nameplate_source_evidence_id": "UNAVAILABLE",
                "evidence_class": "C",
                "evidence_ids": ["P-SABIC"],
            },
            {
                "producer": "Advanced Petrochemical",
                "process_family": "polypropylene",
                "process_route": "UNAVAILABLE",
                "published_standards": "UNAVAILABLE",
                "public_note": "Jubail complex exceeded nameplate in Q1 2026",
                "installed_capacity_tpy": 450000,
                "nameplate_status": "observed",
                "nameplate_source_evidence_id": "P-ADVANCED",
                "evidence_class": "C",
                "evidence_ids": ["P-ADVANCED"],
            },
            {
                "producer": "Tasnee",
                "process_family": "polypropylene",
                "process_route": "UNAVAILABLE",
                "published_standards": "UNAVAILABLE",
                "installed_capacity_tpy": 720000,
                "nameplate_status": "observed",
                "nameplate_source_evidence_id": "P-TASNEE",
                "evidence_class": "C",
                "evidence_ids": ["P-TASNEE"],
            },
        ],
        "public_dimension_states": old_capability[
            "public_dimension_states"
        ],
        "unresolved_hard_gates": [
            {"name": name, "state": "unresolved"}
            for name in old_capability["unresolved_hard_gates"]
        ],
    }
    return _base_candidate(
        case,
        opportunity=_opportunity(case),
        disclosed_concentration={
            "value": "UNAVAILABLE",
            "quantity": "UNAVAILABLE",
        },
        disclosed_dispersion={
            "year": 2024,
            "basis": "annual_gross_flow_average",
            "flow_basis": "gross",
            "unit": "USD/t",
            "valid_value_coverage": "UNAVAILABLE",
            "valid_quantity_coverage": "UNAVAILABLE",
            "weighted_median_usd_t": "UNAVAILABLE",
            "iqr_usd_t": "UNAVAILABLE",
            "bulk_band_usd_t": "UNAVAILABLE",
            "outlier_observation": "UNAVAILABLE",
            "comparison_observations": [
                {"flow": "imports", "unit_value_usd_t": 1649},
                {"flow": "exports", "unit_value_usd_t": 1097},
            ],
            "coverage_note": (
                "Gross-flow average unit values are a product-mix, grade, "
                "origin, or distribution research signal; they do not "
                "establish a specialty-grade gap."
            ),
            "source_evidence_id": "P-WITS-390210",
            "status": "calculated",
        },
        domestic_capability=domestic_capability,
        evidence=evidence,
    )
