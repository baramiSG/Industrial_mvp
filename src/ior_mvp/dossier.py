from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .case_selection_view import case_selection_view
from .config import ui_text


STATIC_DIR = Path(__file__).resolve().parent / "static"
S15B_PROFILES = {
    "SAU-H6-294110": "pharma_api",
    "SAU-H6-294120": "pharma_api",
    "SAU-H6-310430": "fertilizers",
    "SAU-H6-310510": "fertilizers",
}


def _selection_reference(opportunity_id: str) -> dict[str, str] | None:
    profile = S15B_PROFILES.get(opportunity_id)
    if profile is None:
        return None
    selection = case_selection_view()
    return {
        "selection_id": selection["selection_id"],
        "rule_version": selection["rule_version"],
        "reference": selection["selection_reference"]["path"],
        "profile": profile,
    }


def _dossier_styles() -> str:
    parts = (
        STATIC_DIR / "css" / "tokens.css",
        STATIC_DIR / "css" / "dossier.css",
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in parts)


def build_dossier(analysis: dict[str, Any]) -> dict[str, Any]:
    decision = analysis["active_decision"]
    opportunity = analysis["opportunity"]
    selection_reference = _selection_reference(opportunity["id"])
    latest = max(analysis["trade"], key=lambda row: row["year"])
    capacity = analysis.get("capacity") or {}
    economics = analysis.get("economics") or {}
    evidence = analysis.get("evidence", [])
    public_count = sum(
        1 for row in evidence if row.get("synthetic_flag") is False
    )
    synthetic_count = sum(
        1 for row in evidence if row.get("synthetic_flag") is True
    )
    simulated_rules = [
        row
        for row in analysis.get("rules", [])
        if row.get("synthetic_flag") is True
    ]
    public_contradictions = [
        {
            "evidence_id": row["evidence_id"],
            "source": row["source"],
            "contradiction": row["contradiction"],
            "synthetic_flag": False,
        }
        for row in evidence
        if row.get("synthetic_flag") is False
        and isinstance(row.get("contradiction"), str)
        and row["contradiction"]
    ]
    synthetic_contradictions = (
        [
            {
                "evidence_id": row["evidence_id"],
                "source": row["source"],
                "contradiction": row["contradiction"],
                "synthetic_flag": True,
                "scenario_id": row["scenario_id"],
                "display_labels": row["display_labels"],
            }
            for row in evidence
            if row.get("synthetic_flag") is True
            and isinstance(row.get("contradiction"), str)
            and row["contradiction"]
        ]
        if analysis["mode"] == "simulated"
        else []
    )
    contradiction_register = {
        "public": public_contradictions,
        "synthetic": synthetic_contradictions,
        "synthetic_status": (
            "NOT_APPLICABLE"
            if analysis["mode"] == "public"
            else (
                "PRESENT"
                if synthetic_contradictions
                else "NONE_RECORDED"
            )
        ),
    }
    demand_conclusion = (
        f"Latest frozen public imports: USD "
        f"{latest.get('imports_usd_m', 0):,.1f}m and "
        f"{latest.get('imports_kt', 0):,.1f} kt in {latest['year']}."
    )
    if capacity:
        demand_conclusion += (
            " Simulation target demand is "
            f"{capacity.get('target_spec_demand_kt', 0):,.1f} kt; "
            "the specification-adjusted gap is "
            f"{capacity.get('specification_adjusted_gap_kt', 0):,.1f} kt."
        )
    return {
        "dossier_version": "1.3" if selection_reference else "1.2",
        "opportunity_id": opportunity["id"],
        "mode": analysis["mode"],
        "decision_headline": decision["headline"],
        "decision_rationale": decision["rationale"],
        "decision_state": decision["state"],
        "route": decision["route_label"],
        "localized_narrative": decision.get(
            "localized_narrative"
        ),
        "narrative_version": decision.get("narrative_version"),
        "screening_disposition": analysis[
            "screening_disposition"
        ],
        "gap_class": analysis["gap_class"],
        "route_hypotheses": analysis["route_hypotheses"],
        "preferred_hypothesis": analysis["preferred_hypothesis"],
        "evidence_class_assessment": analysis[
            "evidence_class_assessment"
        ],
        "advance_gate": analysis["advance_gate"],
        "hard_exclusions": analysis["hard_exclusions"],
        "rejection_conditions": analysis["rejection_conditions"],
        "product_identity": {
            "hs_revision": opportunity["hs_revision"],
            "hs6": opportunity["hs6"],
            "commercial_name_en": opportunity["commercial_name_en"],
            "commercial_name_ar": opportunity["commercial_name_ar"],
            "application_boundary": opportunity["application_boundary"],
        },
        "demand_conclusion": demand_conclusion,
        "supply_conclusion": analysis["domestic_capability"],
        "gap_diagnosis": {
            "public_state": analysis["real_decision"]["state"],
            "active_state": decision["state"],
            "gap_class": analysis["gap_class"],
            "capacity": capacity,
            "simulated_rules": simulated_rules,
        },
        "capability_route": analysis["capability"],
        "economics": economics,
        "competition_policy": analysis.get("competition"),
        "partner_detail": analysis.get("partner_detail"),
        "evidence_summary": {
            "public_records": public_count,
            "synthetic_records": synthetic_count,
            "snapshot_id": analysis["snapshot_id"],
            "as_of_date": analysis["as_of_date"],
            "authority": analysis["authority"],
            "integrity": analysis["integrity"],
            **(
                {"selection": selection_reference}
                if selection_reference is not None
                else {}
            ),
        },
        "contradiction_register": contradiction_register,
        "conditions": decision.get("conditions", []),
        "kill_conditions": decision.get("kill_conditions", []),
        "next_evidence_actions": decision.get("missing_facts", []),
        "counterfactual": (
            analysis.get("simulation_decision", {}).get("counterfactual")
            if analysis["mode"] == "simulated"
            else None
        ),
        "synthetic_disclosure": analysis.get("simulation_scenario"),
    }


def _state_text(state: str | None, locale: str) -> str:
    if state is None:
        return ui_text("disposition.no_candidate", locale)
    keys = {
        "ADVANCE": "state.advance",
        "REJECT": "state.reject",
        "INVESTIGATE": "state.investigate",
        "MONITOR": "state.monitor",
    }
    key = keys.get(state)
    return ui_text(key, locale) if key else state


def _execution_text(execution: str, locale: str) -> str:
    keys = {
        "FULL": "execution.full",
        "DEGRADED": "execution.degraded",
        "DISABLED": "execution.disabled",
    }
    key = keys.get(execution)
    return ui_text(key, locale) if key else execution


def render_dossier_html(
    dossier: dict[str, Any],
    locale: str = "en",
) -> str:
    """Render localized dossier chrome around unchanged analytical content."""

    def e(value: Any) -> str:
        return html.escape(str(value))

    def text(key: str, **values: Any) -> str:
        return e(ui_text(key, locale, **values))

    def island(value: Any, tag: str = "span") -> str:
        return (
            f'<{tag} class="source-language-island" '
            f'lang="en" dir="ltr">{e(value)}</{tag}>'
        )

    def structured(
        entry: dict[str, Any],
        tag: str = "span",
    ) -> str:
        if isinstance(entry.get("text"), str) and "segments" not in entry:
            return f"<{tag}>{e(entry['text'])}</{tag}>"
        segments = entry.get("segments")
        if not isinstance(segments, list):
            raise ValueError(
                "localized narrative entry requires segments or text"
            )
        rendered: list[str] = []
        for segment in segments:
            if not isinstance(segment, dict):
                raise ValueError(
                    "localized narrative segment must be a mapping"
                )
            escaped = e(segment.get("text", ""))
            if segment.get("ltr_isolate") is True:
                escaped = (
                    '<bdi class="ltr-isolate" lang="en" '
                    f'dir="ltr">{escaped}</bdi>'
                )
            rendered.append(escaped)
        return f"<{tag}>{''.join(rendered)}</{tag}>"

    def technical(value: Any) -> str:
        return (
            '<bdi class="ltr-isolate technical-token" '
            f'dir="ltr">{e(value)}</bdi>'
        )

    def technical_template(key: str, **values: Any) -> str:
        markers = {
            name: f"IORTECHNICAL{name.upper()}TOKEN"
            for name in values
        }
        rendered = e(ui_text(key, locale, **markers))
        for name, marker in markers.items():
            rendered = rendered.replace(marker, technical(values[name]))
        return rendered

    def localized_code(label: str, value: str) -> str:
        if locale == "en":
            return technical(value)
        return f"{e(label)} {technical(value)}"

    def caption() -> str:
        if locale != "ar":
            return ""
        return (
            '<p class="dossier-source-caption">'
            f'{text("source_language.caption")}</p>'
        )

    def source_list(values: list[Any]) -> str:
        if not values:
            return f"<li>{text('dossier.none')}</li>"
        return "".join(f"<li>{island(item)}</li>" for item in values)

    def structured_list(values: list[dict[str, Any]]) -> str:
        if not values:
            return f"<li>{text('dossier.none')}</li>"
        return "".join(
            f"<li>{structured(item)}</li>" for item in values
        )

    def fired_label(value: bool | None) -> str:
        if value is True:
            return ui_text("fire.yes", locale)
        if value is False:
            return ui_text("fire.no", locale)
        return ui_text("fire.na", locale)

    direction = "rtl" if locale == "ar" else "ltr"
    state_text = _state_text(dossier["decision_state"], locale)
    state_code = (
        dossier["decision_state"]
        if dossier["decision_state"] is not None
        else "NO_CANDIDATE"
    )
    mode_text = ui_text(
        "mode.simulated" if dossier["mode"] == "simulated" else "mode.public",
        locale,
    )
    disclosure = dossier.get("synthetic_disclosure")
    disclosure_html = ""
    if disclosure:
        labels = disclosure["display_labels"]
        order = ("ar", "en") if locale == "ar" else ("en", "ar")
        rendered_labels = "<br>".join(
            (
                f'<strong lang="ar" dir="rtl">{e(labels[key])}</strong>'
                if key == "ar"
                else f'<strong lang="en" dir="ltr">{e(labels[key])}</strong>'
            )
            for key in order
        )
        disclosure_html = (
            f'<div class="warning">{rendered_labels}<br>'
            f"{caption()}{island(disclosure['seed_basis'])}</div>"
        )
    partner_detail = dossier.get("partner_detail")
    partner_detail_html = ""
    if isinstance(partner_detail, dict):
        partner_state = partner_detail.get("state")
        if partner_state == "PARTNER_DETAIL_OBSERVED":
            partner_status_html = technical_template(
                "dossier.partner_detail_observed",
                source=partner_detail.get("source_id", "UNAVAILABLE"),
                rows=partner_detail.get(
                    "observed_partner_rows",
                    "UNAVAILABLE",
                ),
            )
        elif partner_state == "PARTNER_DETAIL_MISSING":
            attempts = ", ".join(
                partner_detail.get("attempt_passport_ids", [])
            ) or "UNAVAILABLE"
            partner_status_html = technical_template(
                "dossier.partner_detail_missing",
                reason=partner_detail.get("reason", "UNAVAILABLE"),
                attempts=attempts,
            )
        elif partner_state == "PARTNER_TRADE_OBSERVED_ZERO":
            partner_status_html = technical_template(
                "dossier.partner_detail_zero",
                source=partner_detail.get("source_id", "UNAVAILABLE"),
            )
        else:
            raise ValueError("unknown partner-detail state")
        partner_detail_html = (
            '<p class="small partner-detail">'
            f'<strong>{text("dossier.partner_detail")}</strong><br>'
            f"{partner_status_html}</p>"
        )
    simulated_rules = dossier["gap_diagnosis"].get("simulated_rules", [])
    simulated_rules_html = ""
    if simulated_rules:
        items = "".join(
            (
                "<li>"
                f"{technical(row['rule_id'])} · "
                f"{localized_code(_execution_text(row['execution'], locale), row['execution'])} · "
                f"{e(fired_label(row['fired']))}"
                f"<br>{island(row['result'])}"
                f"<br>{e(row['display_labels']['en'])}"
                f'<br><span lang="ar" dir="rtl">'
                f"{e(row['display_labels']['ar'])}</span>"
                "</li>"
            )
            for row in simulated_rules
        )
        simulated_rules_html = (
            f'<section class="box"><h2>{text("dossier.simulated_ledger")}'
            f"</h2>{caption()}<ul>{items}</ul></section>"
        )
    identity = dossier["product_identity"]
    if locale == "ar" and identity["commercial_name_ar"]:
        product_names = (
            f'<p lang="ar" dir="rtl"><strong>'
            f"{e(identity['commercial_name_ar'])}</strong></p>"
            f"<p>{island(identity['commercial_name_en'])}</p>"
        )
    else:
        product_names = (
            f"<p><strong>{island(identity['commercial_name_en'])}</strong></p>"
            f'<p lang="ar" dir="rtl">{e(identity["commercial_name_ar"])}</p>'
        )
    authority = dossier["evidence_summary"]["authority"]
    methodology = authority["methodology"]
    versions = authority["config_versions"]
    authority_html = (
        f'<p><strong>{text("integrity.methodology")}</strong><br>'
        f"{technical(methodology['file'])}</p>"
        f'<p class="small">{text("technical.sha256")} '
        f"{technical(methodology['sha256'])}</p>"
        f'<p class="small">{text("integrity.project")} '
        f"{technical(authority['project_version'])} · "
        f'{text("integrity.thresholds")} {technical(versions["thresholds"])} · '
        f'{text("integrity.sector_profiles")} '
        f'{technical(versions["sector_profiles"])} · '
        f'{text("integrity.evidence_policy")} '
        f'{technical(versions["evidence_policy"])} · '
        f'{text("integrity.ui_strings")} '
        f'{technical(versions["ui_strings"])}</p>'
    )
    evidence = dossier["evidence_summary"]
    evidence_counts = text(
        "dossier.evidence_counts",
        public=evidence["public_records"],
        synthetic=evidence["synthetic_records"],
    )
    selection = evidence.get("selection")
    selection_html = ""
    if isinstance(selection, dict):
        selection_html = (
            '<p class="small selection-reference">'
            + technical_template(
                "dossier.selection_reference",
                selection_id=selection["selection_id"],
                rule_version=selection["rule_version"],
                profile=selection["profile"],
            )
            + f"<br>{technical(selection['reference'])}</p>"
        )
    title = text("dossier.document_title", state=state_text)
    supply_json = json.dumps(
        dossier["supply_conclusion"],
        ensure_ascii=False,
        sort_keys=True,
    )
    contradiction_register = dossier["contradiction_register"]

    def contradiction_items(rows: list[dict[str, Any]]) -> str:
        return "".join(
            (
                "<li>"
                f"{technical(row['evidence_id'])} · "
                f"{island(row['source'])}"
                f"<br>{island(row['contradiction'])}"
                + (
                    (
                        f"<br>{e(row['display_labels']['en'])}"
                        f'<br><span lang="ar" dir="rtl">'
                        f"{e(row['display_labels']['ar'])}</span>"
                    )
                    if row.get("synthetic_flag") is True
                    else ""
                )
                + "</li>"
            )
            for row in rows
        )

    public_rows = contradiction_register["public"]
    synthetic_rows = contradiction_register["synthetic"]
    public_contradictions_html = (
        f"<ul>{contradiction_items(public_rows)}</ul>"
        if public_rows
        else f"<p>{text('dossier.no_public_contradictions')}</p>"
    )
    if contradiction_register["synthetic_status"] == "NOT_APPLICABLE":
        synthetic_contradictions_html = (
            f"<p>{text('dossier.synthetic_not_applicable')}</p>"
        )
    elif synthetic_rows:
        synthetic_contradictions_html = (
            f"<ul>{contradiction_items(synthetic_rows)}</ul>"
        )
    else:
        synthetic_contradictions_html = (
            f"<p>{text('dossier.no_synthetic_contradictions')}</p>"
        )
    contradictions_html = (
        '<section class="box contradiction-register">'
        f'<h2>{text("dossier.contradiction_register")}</h2>'
        f'<h3>{text("dossier.public_contradictions")}</h3>'
        f"{caption()}{public_contradictions_html}"
        f'<h3>{text("dossier.synthetic_contradictions")}</h3>'
        f"{synthetic_contradictions_html}</section>"
    )
    narrative_by_locale = dossier.get("localized_narrative")
    localized_narrative = (
        narrative_by_locale.get(locale)
        if isinstance(narrative_by_locale, dict)
        else None
    )
    if isinstance(localized_narrative, dict):
        headline_html = structured(
            localized_narrative["headline"],
            "h1",
        )
        rationale_html = structured(
            localized_narrative["rationale"],
            "p",
        )
        route_html = structured(
            localized_narrative["route_label"],
            "span",
        )
        conditions_html = structured_list(
            localized_narrative["conditions"]
        )
        kills_html = structured_list(
            localized_narrative["kill_conditions"]
        )
        missing = localized_narrative.get("missing_facts")
        if isinstance(missing, list) and missing:
            next_actions_html = structured_list(missing)
        elif dossier["next_evidence_actions"]:
            next_actions_html = "".join(
                f"<li>{e(item)}</li>"
                for item in dossier["next_evidence_actions"]
            )
        else:
            next_actions_html = f"<li>{text('dossier.none')}</li>"
        narrative_caption = ""
    else:
        headline_html = f"<h1>{island(dossier['decision_headline'])}</h1>"
        rationale_html = (
            f"<p>{island(dossier['decision_rationale'])}</p>"
        )
        route_html = island(dossier["route"], "span")
        conditions_html = source_list(dossier["conditions"])
        kills_html = source_list(dossier["kill_conditions"])
        next_actions_html = source_list(
            dossier["next_evidence_actions"]
        )
        narrative_caption = caption()
    return f"""<!doctype html>
<html lang="{locale}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{_dossier_styles()}</style>
</head>
<body class="dossier-body">
<main class="page" aria-label="{text("dossier.print_aria")}">
<div class="state">{localized_code(state_text, state_code)}</div>
<section class="decision-narrative">
{narrative_caption}
{headline_html}
{rationale_html}
<div class="meta">{technical(dossier["opportunity_id"])} · {route_html} · {text("dossier.mode")}: {e(mode_text)}</div>
</section>
{disclosure_html}
<div class="dossier-grid">
<section class="box"><h2>{text("dossier.product_identity")}</h2>{product_names}<p class="small">{technical(f"HS {identity['hs_revision']} / {identity['hs6']}")}</p><h3>{text("dossier.application_boundary")}</h3>{caption()}<p>{island(identity["application_boundary"])}</p></section>
<section class="box"><h2>{text("dossier.demand_conclusion")}</h2>{caption()}<p>{island(dossier["demand_conclusion"])}</p></section>
<section class="box"><h2>{text("dossier.supply_conclusion")}</h2>{caption()}<p>{island(supply_json, "code")}</p></section>
{simulated_rules_html}
{contradictions_html}
<section class="box decision-conditions"><h2>{text("dossier.decision_conditions")}</h2>{narrative_caption}<ul>{conditions_html}</ul></section>
<section class="box kill-conditions"><h2>{text("dossier.kill_conditions")}</h2>{narrative_caption}<ul>{kills_html}</ul></section>
<section class="box next-actions"><h2>{text("dossier.next_actions")}</h2>{narrative_caption}<ul>{next_actions_html}</ul></section>
<section class="box"><h2>{text("dossier.evidence_boundary")}</h2><p>{evidence_counts}</p>{selection_html}{partner_detail_html}<p class="small">{text("dossier.snapshot")} {technical(evidence["snapshot_id"])} · {text("dossier.as_of")} {technical(evidence["as_of_date"])}</p></section>
<section class="box"><h2>{text("dossier.authority")}</h2>{authority_html}</section>
</div>
</main>
</body></html>"""
