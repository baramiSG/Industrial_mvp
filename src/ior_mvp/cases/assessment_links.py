"""Finite public CaseBrief join for H6 screening records."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from ior_mvp.config import PROJECT_ROOT

from .brief import load_case_brief

_H6_BRIEFS = (
    "294110", "294120", "310430", "310510", "392010",
    "721012", "721061", "760429", "760711",
)


@lru_cache(maxsize=2)
def _latest_universe_year(relative_path: str, expected_sha256: str) -> str:
    if not relative_path.startswith("data/snapshots/universe/") or ".." in Path(relative_path).parts:
        raise ValueError("screening universe path is outside the public source")
    data = (PROJECT_ROOT / relative_path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("screening universe source hash differs")
    universe = json.loads(data)
    years = universe.get("periods")
    if (not isinstance(years, list) or not years
            or any(not isinstance(year, str) or len(year) != len("YYYY") or not year.isdigit()
                   for year in years)):
        raise ValueError("screening universe period is invalid")
    return max(years)


@lru_cache(maxsize=1)
def _briefs() -> dict[str, Mapping[str, Any]]:
    rows: dict[str, Mapping[str, Any]] = {}
    for hs6 in _H6_BRIEFS:
        opportunity_id = f"SAU-H6-{hs6}"
        path = (
            PROJECT_ROOT / "data" / "cases" / "briefs"
            / f"CASE-BRIEF-{opportunity_id}-v1.json"
        )
        brief = load_case_brief(path)
        if (
            brief["opportunity_id"] != opportunity_id
            or brief["hs6"] != hs6
            or brief["hs_revision"] != "H6"
        ):
            raise ValueError("public brief identity differs from admitted H6 link")
        rows[hs6] = brief
    return rows


def deep_assessment_link(
    selected: Mapping[str, Any],
    screening_snapshot: Mapping[str, Any],
) -> dict[str, str] | None:
    """Return a public-only composite link when all source identities agree."""
    hs6 = selected.get("hs6")
    if hs6 not in _H6_BRIEFS:
        return None
    if (selected.get("synthetic_flag") is True or "scenario_id" in selected
            or selected.get("hs_revision", "H6") != "H6"
            or screening_snapshot.get("source_boundary") != "public"
            or screening_snapshot.get("synthetic_flag") is not False):
        raise ValueError("deep assessment requires a public H6 source")
    brief = _briefs()[hs6]
    universe = screening_snapshot["inputs"]["universe_snapshots"]
    if len(universe) != 1 or universe[0]["id"] != brief["universe_snapshot_id"]:
        raise ValueError("screening and brief universe identities differ")
    latest = _latest_universe_year(universe[0]["path"], universe[0]["sha256"])
    unit = brief["partner_detail"]["unit_key"]
    if (unit[:2] != [hs6, "imports"] or not isinstance(unit[2], str)
            or unit[2] != latest or selected.get("period_year", latest) != latest):
        raise ValueError("brief period is not the selected H6 import unit")
    if selected["hs6"] != brief["hs6"]:
        raise ValueError("screening record and brief HS6 differ")
    return {
        "opportunity_id": brief["opportunity_id"],
        "brief_id": brief["brief_id"],
        "screening_snapshot_id": screening_snapshot["snapshot_id"],
        "hs_revision": brief["hs_revision"],
        "hs6": hs6,
        "period_year": unit[2],
    }
