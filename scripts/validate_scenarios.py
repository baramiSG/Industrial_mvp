from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from ior_mvp.config import DATA_DIR
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    reconcile_synthetic_scenario,
    validate_synthetic_scenario,
)


SYNTHETIC_DIR = DATA_DIR / "synthetic"
PUBLIC_DIR = DATA_DIR / "snapshots" / "public"


class ScenarioValidationExecutionError(RuntimeError):
    pass


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ScenarioValidationExecutionError(
            f"Expected a JSON object: {path}"
        )
    return value


def _index_public_cases(
    public_dir: Path,
) -> dict[str, dict[str, Any]]:
    paths = sorted(public_dir.glob("*.json"))
    if not paths:
        raise ScenarioValidationExecutionError(
            f"No public JSON files found in {public_dir}"
        )
    cases: dict[str, dict[str, Any]] = {}
    for path in paths:
        case = _read_json_object(path)
        opportunity = case.get("opportunity")
        opportunity_id = (
            opportunity.get("id")
            if isinstance(opportunity, dict)
            else None
        )
        if not isinstance(opportunity_id, str) or not opportunity_id:
            raise ScenarioValidationExecutionError(
                f"Public case lacks opportunity.id: {path}"
            )
        if opportunity_id in cases:
            raise ScenarioValidationExecutionError(
                f"Duplicate public opportunity.id={opportunity_id}"
            )
        cases[opportunity_id] = case
    return cases


def validate_scenario_directories(
    synthetic_dir: Path = SYNTHETIC_DIR,
    public_dir: Path = PUBLIC_DIR,
) -> list[dict[str, Any]]:
    public_cases = _index_public_cases(public_dir)
    scenario_paths = sorted(synthetic_dir.glob("*.json"))
    if not scenario_paths:
        raise ScenarioValidationExecutionError(
            f"No synthetic JSON files found in {synthetic_dir}"
        )

    reports: list[dict[str, Any]] = []
    for path in scenario_paths:
        scenario = _read_json_object(path)
        scenario_id = scenario.get("scenario_id", "<missing>")
        opportunity_id = scenario.get("opportunity_id")
        try:
            validate_synthetic_scenario(scenario)
            if opportunity_id not in public_cases:
                raise EvidenceIntegrityError(
                    "No public case matches scenario "
                    f"opportunity_id={opportunity_id}"
                )
            report = reconcile_synthetic_scenario(
                scenario,
                public_cases[opportunity_id],
            )
            reports.append({"file": path.name, **report})
        except EvidenceIntegrityError as exc:
            reports.append(
                {
                    "file": path.name,
                    "scenario_id": scenario_id,
                    "opportunity_id": opportunity_id,
                    "public_snapshot_id": None,
                    "status": "FAIL",
                    "checks": [],
                    "error": str(exc),
                }
            )
    return reports


def _print_reports(reports: list[dict[str, Any]]) -> None:
    for report in reports:
        print(
            f"- {report['file']} "
            f"scenario={report['scenario_id']} "
            f"opportunity={report['opportunity_id']} "
            f"status={report['status']}"
        )
        if report.get("error"):
            print(f"  ERROR: {report['error']}")
        for check in report.get("checks", []):
            print(
                f"  {check['rule_id']}: {check['result']} "
                f"- {check['detail']}"
            )


def main(
    synthetic_dir: Path = SYNTHETIC_DIR,
    public_dir: Path = PUBLIC_DIR,
) -> int:
    try:
        reports = validate_scenario_directories(
            synthetic_dir,
            public_dir,
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ScenarioValidationExecutionError,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(
            "SCENARIO VALIDATION ERROR: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    failures = [
        report
        for report in reports
        if report["status"] == "FAIL"
    ]
    if failures:
        print(
            "SCENARIO VALIDATION FAIL "
            f"({len(failures)}/{len(reports)} scenarios failed)"
        )
        _print_reports(reports)
        return 1

    print(
        "SCENARIO VALIDATION PASS "
        f"({len(reports)} scenarios)"
    )
    _print_reports(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
