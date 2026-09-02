from __future__ import annotations

import html
from typing import Any


def build_dossier(analysis: dict[str, Any]) -> dict[str, Any]:
    decision = analysis["active_decision"]
    opportunity = analysis["opportunity"]
    latest = max(analysis["trade"], key=lambda row: row["year"])
    capacity = analysis.get("capacity") or {}
    economics = analysis.get("economics") or {}
    evidence = analysis.get("evidence", [])
    public_count = sum(1 for row in evidence if row.get("synthetic_flag") is False)
    synthetic_count = sum(1 for row in evidence if row.get("synthetic_flag") is True)

    demand_conclusion = (
        f"Latest frozen public imports: USD {latest.get('imports_usd_m', 0):,.1f}m and "
        f"{latest.get('imports_kt', 0):,.1f} kt in {latest['year']}."
    )
    if capacity:
        demand_conclusion += (
            f" Simulation target demand is {capacity.get('target_spec_demand_kt', 0):,.1f} kt; "
            f"the specification-adjusted gap is {capacity.get('specification_adjusted_gap_kt', 0):,.1f} kt."
        )

    return {
        "dossier_version": "1.0",
        "opportunity_id": opportunity["id"],
        "mode": analysis["mode"],
        "decision_headline": decision["headline"],
        "decision_state": decision["state"],
        "route": decision["route_label"],
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
            "capacity": capacity,
        },
        "capability_route": analysis["capability"],
        "economics": economics,
        "competition_policy": analysis.get("competition"),
        "evidence_summary": {
            "public_records": public_count,
            "synthetic_records": synthetic_count,
            "snapshot_id": analysis["snapshot_id"],
            "as_of_date": analysis["as_of_date"],
            "authority": analysis["authority"],
            "integrity": analysis["integrity"],
        },
        "conditions": decision.get("conditions", []),
        "kill_conditions": decision.get("kill_conditions", []),
        "next_evidence_actions": analysis.get("data_unlocks", []),
        "synthetic_disclosure": analysis.get("simulation_scenario"),
    }


def render_dossier_html(dossier: dict[str, Any]) -> str:
    def e(value: Any) -> str:
        return html.escape(str(value))

    conditions = "".join(f"<li>{e(item)}</li>" for item in dossier["conditions"])
    kills = "".join(f"<li>{e(item)}</li>" for item in dossier["kill_conditions"])
    evidence_actions = "".join(
        f"<li>{e(item)}</li>" for item in dossier["next_evidence_actions"]
    )
    disclosure = dossier.get("synthetic_disclosure")
    disclosure_html = ""
    if disclosure:
        disclosure_html = f"""
        <div class="warning"><strong>{e(disclosure['display_label'])}</strong><br>{e(disclosure['seed_basis'])}</div>
        """

    authority = dossier["evidence_summary"]["authority"]
    methodology = authority["methodology"]
    versions = authority["config_versions"]
    authority_html = f"""
<p><strong>Methodology</strong><br>{e(methodology['file'])}</p>
<p class="small">SHA-256 {e(methodology['sha256'])}</p>
<p class="small">Project {e(authority['project_version'])}
 · Thresholds {e(versions['thresholds'])}
 · Sector profiles {e(versions['sector_profiles'])}
 · Evidence policy {e(versions['evidence_policy'])}</p>
"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(dossier['decision_headline'])}</title>
<style>
body{{font-family:Inter,Arial,sans-serif;color:#13233a;margin:0;background:#eef3f7}}
.page{{max-width:1050px;margin:28px auto;background:white;padding:44px;box-shadow:0 12px 40px rgba(12,32,56,.12)}}
h1{{font-size:30px;margin:0 0 6px}} h2{{font-size:16px;text-transform:uppercase;letter-spacing:.08em;color:#53677f;border-bottom:1px solid #dce5ed;padding-bottom:8px}}
.meta{{color:#667a91;margin-bottom:24px}} .state{{display:inline-block;padding:7px 11px;border-radius:999px;background:#102a43;color:white;font-weight:700}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} .box{{border:1px solid #dce5ed;border-radius:12px;padding:18px}}
.warning{{background:#fff5d6;border:1px solid #e7b93e;padding:14px;border-radius:10px;margin:18px 0}}
.small{{font-size:12px;color:#65768a}} ul{{padding-left:20px}} @media print{{body{{background:white}}.page{{box-shadow:none;margin:0;max-width:none}}}}
</style>
</head>
<body>
<main class="page">
<div class="state">{e(dossier['decision_state'])}</div>
<h1>{e(dossier['decision_headline'])}</h1>
<div class="meta">{e(dossier['opportunity_id'])} · {e(dossier['route'])} · Mode: {e(dossier['mode'])}</div>
{disclosure_html}
<div class="grid">
<section class="box"><h2>Product identity</h2><p><strong>{e(dossier['product_identity']['commercial_name_en'])}</strong></p><p dir="rtl">{e(dossier['product_identity']['commercial_name_ar'])}</p><p class="small">HS {e(dossier['product_identity']['hs_revision'])} / {e(dossier['product_identity']['hs6'])}</p></section>
<section class="box"><h2>Demand conclusion</h2><p>{e(dossier['demand_conclusion'])}</p></section>
<section class="box"><h2>Decision conditions</h2><ul>{conditions or '<li>None</li>'}</ul></section>
<section class="box"><h2>Kill conditions</h2><ul>{kills or '<li>None</li>'}</ul></section>
<section class="box"><h2>Next evidence actions</h2><ul>{evidence_actions or '<li>None</li>'}</ul></section>
<section class="box"><h2>Evidence boundary</h2><p>{e(dossier['evidence_summary']['public_records'])} public records; {e(dossier['evidence_summary']['synthetic_records'])} synthetic records.</p><p class="small">Snapshot {e(dossier['evidence_summary']['snapshot_id'])} · As of {e(dossier['evidence_summary']['as_of_date'])}</p></section>
<section class="box"><h2>Authority and versions</h2>{authority_html}</section>
</div>
</main>
</body></html>"""
