from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path

from ior_mvp.candidate_discovery import discover_candidates
from ior_mvp.candidate_register import validate_candidate_register
from ior_mvp.decision_engine import analyze

ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_backend_module_boundary_and_caps() -> None:
    names = (
        "candidate_record_contract", "candidate_register", "line_contract",
        "line_comparison", "candidate_finding_rules", "candidate_discovery",
    )
    trees = {
        name: ast.parse((ROOT / "src" / "ior_mvp" / f"{name}.py").read_text())
        for name in names
    }
    imports: dict[str, set[str]] = {}
    for name, tree in trees.items():
        path = ROOT / "src" / "ior_mvp" / f"{name}.py"
        assert len(path.read_text().splitlines()) <= 500, name
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                found.add(
                    f"ior_mvp.{module}" if node.level else module
                )
            elif isinstance(node, ast.Call):
                target = node.func
                assert not (
                    isinstance(target, ast.Name)
                    and target.id in {"__import__", "eval", "exec"}
                ), name
                assert not (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "importlib"
                ), name
        imports[name] = found
    assert imports["candidate_record_contract"] - {
        "__future__", "hashlib", "json", "math", "re", "datetime",
        "functools", "typing", "ior_mvp.config", "ior_mvp.evidence",
    } == set()
    assert imports["candidate_finding_rules"] - {
        "__future__", "typing", "ior_mvp.candidate_record_contract",
        "ior_mvp.evidence_needs",
    } == set()
    graph = {
        name: {
            imported.removeprefix("ior_mvp.")
            for imported in found
            if imported.removeprefix("ior_mvp.") in names
        }
        for name, found in imports.items()
    }
    def visit(name: str, active: set[str], complete: set[str]) -> None:
        assert name not in active, f"backend import cycle at {name}"
        if name in complete:
            return
        active.add(name)
        for child in graph[name]:
            visit(child, active, complete)
        active.remove(name)
        complete.add(name)
    complete: set[str] = set()
    for name in names:
        visit(name, set(), complete)
    definitions = {
        name: {
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for name, tree in trees.items()
    }
    for moved in {"equipment_finding", "register_context_finding",
                  "_register_source_references", "_hs_in", "_customs_usable"}:
        assert moved not in definitions["line_comparison"]
        assert moved not in definitions["line_contract"]
    for selector in {"_hs_in", "_customs_usable", "_register_source_references"}:
        assert {
            name for name, functions in definitions.items() if selector in functions
        } == {"candidate_record_contract"}
    for selector in {"_plant_facts", "_attributed_plant"}:
        assert {
            name for name, functions in definitions.items() if selector in functions
        } == {"candidate_discovery"}


def test_new_module_dependency_closure_cannot_reach_engine_or_graph() -> None:
    source_root = ROOT / "src" / "ior_mvp"
    known = {path.stem for path in source_root.glob("*.py")}
    dependencies: dict[str, set[str]] = {}
    for path in source_root.glob("*.py"):
        found: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.level == 1:
                if node.module:
                    found.add(node.module.split(".")[0])
                else:
                    found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Import):
                found.update(
                    alias.name.split(".")[1]
                    for alias in node.names
                    if alias.name.startswith("ior_mvp.")
                    and len(alias.name.split(".")) > 1
                )
        dependencies[path.stem] = found & known
    forbidden = {"candidate_discovery", "simulation", "decision_engine", "graph"}
    for root_name in ("candidate_record_contract", "candidate_finding_rules"):
        reached: set[str] = set()
        pending = [root_name]
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            reached.add(name)
            pending.extend(dependencies[name] - reached)
        assert not reached & forbidden, (root_name, reached & forbidden)


def test_runtime_findings_use_exact_fact_ids_and_line_scope() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    rows = result["candidate_discovery"]["rows"]
    steel_a = next(
        row for row in rows if row["entity_id"] == "PLANT-8932de539dd9d7d8"
    )
    assert steel_a["r9s"]["fired"] is True
    assert all(
        fact_id.startswith("FACT-")
        for fact_id in steel_a["evidence_boundary"]["signal_fact_ids"]
    )
    line_b = next(
        row for row in rows if row["entity_id"] == "LINE-96f1bd96c5c6ccda"
    )
    width = next(
        finding for finding in line_b["findings"]
        if finding["requirement_item_id"] == "width_mm"
    )
    assert width["rule_id"] == "P06"
    assert width["status"] == "LIMITATION_IDENTIFIED"
    assert width["next_evidence"]["subject_scope"] == line_b["entity_id"]
    volume = next(
        finding for finding in line_b["findings"]
        if finding["rule_id"] == "P09"
    )
    assert volume["current_recorded"]["admitted_qualified_supply_kt"] == 0


def test_not_required_tooling_has_no_request_without_erasing_real_needs() -> None:
    _scenario, _register, candidate_lines = _register_and_lines("SYN-MINISTRY-PP-001.json")
    assert candidate_lines["requirements_additions"]["customer_qualification_required"] is False
    polypropylene = analyze("SAU-H0-390210", "simulated")
    assert polypropylene["real_decision"]["state"] == "REJECT"
    assert polypropylene["simulation_decision"]["state"] == "REJECT"
    rows = {
        row["entity_id"]: row
        for row in polypropylene["candidate_discovery"]["rows"]
    }
    assessments = {
        row["line_id"]: row
        for row in polypropylene["line_assessment"]["rows"]
    }
    expected_actions = {
        "LINE-e403e85a85052861": [],
        "LINE-cb9a42384c3523ec": [
            "mfr_range_g_10min", "qualified_available_kt",
        ],
    }
    for line_id, expected in expected_actions.items():
        row = rows[line_id]
        findings = {
            finding["requirement_item_id"]: finding
            for finding in row["findings"]
        }
        tooling = findings["tooling_required"]
        assert tooling["rule_id"] == "P06"
        assert tooling["status"] == "NOT_REQUIRED"
        assert tooling["current_recorded"] is False
        assert tooling["needed"] is False
        assert tooling["origin"] == "REVIEWED_INFERENCE"
        assert tooling["source_refs"]
        assert tooling["next_evidence"] is None
        assert tooling["action_code"] == "NO_ADDITIONAL_REQUEST"
        assert [action["missing_field"] for action in row["next_evidence_actions"]] == expected

        additives = findings["additives_required"]
        assert (additives["status"], additives["current_recorded"], additives["needed"]) == (
            "SUPPORTED", False, False,
        )
        assert additives["next_evidence"] is None
        assert additives["action_code"] == "NO_ADDITIONAL_REQUEST"
        qualification = next(
            item for item in assessments[line_id]["comparisons"]
            if item["field_id"] == "customer_qualification"
        )
        assert (qualification["rule_id"], qualification["status"], qualification["needed"]) == (
            "P07", "NOT_REQUIRED", False,
        )
        assert qualification["current_recorded"] == "NOT_REQUIRED"

    resin_a = rows["LINE-e403e85a85052861"]
    assert next(finding for finding in resin_a["findings"]
                if finding["requirement_item_id"] == "mfr_range_g_10min")["next_evidence"] is None
    resin_b = rows["LINE-cb9a42384c3523ec"]
    mfr = next(finding for finding in resin_b["findings"]
               if finding["requirement_item_id"] == "mfr_range_g_10min")
    assert mfr["status"] == "LIMITATION_IDENTIFIED"
    assert mfr["next_evidence"]["missing_field"] == "mfr_range_g_10min"
    assert mfr["next_evidence"]["subject_scope"] == resin_b["entity_id"]

    company = rows["COMPANY-7b3497b64cf80470"]
    procurement = next(finding for finding in company["findings"]
                       if finding["rule_id"] == "P03")
    assert procurement["status"] == "SUPPORTED"
    assert procurement["action_code"] == "FACTORY_ATTRIBUTION"
    assert procurement["next_evidence"]["missing_field"] == "factory_attribution_link"
    assert procurement["next_evidence"]["subject_scope"] == company["entity_id"]
    assert procurement["next_evidence"] in company["next_evidence_actions"]

    steel = analyze("SAU-H0-721049", "simulated")
    steel_c = next(row for row in steel["candidate_discovery"]["rows"]
                   if row["entity_id"] == "LINE-4fbdbb0b2c107968")
    width = next(finding for finding in steel_c["findings"]
                 if finding["requirement_item_id"] == "width_mm")
    assert width["status"] == "NOT_ESTABLISHED"
    assert width["next_evidence"]["missing_field"] == "width_mm"
    assert width["next_evidence"]["subject_scope"] == steel_c["entity_id"]


def test_false_tooling_without_known_resin_scope_still_requests_evidence() -> None:
    from ior_mvp.line_comparison import compare_lines

    scenario, _register, _lines = _register_and_lines("SYN-MINISTRY-PP-001.json")
    changed = deepcopy(scenario)
    inputs = changed["synthetic_inputs"]
    register = inputs["candidate_register"]
    candidate_lines = inputs["candidate_lines"]
    line_id = "LINE-e403e85a85052861"
    line = next(row for row in candidate_lines["lines"] if row["line_id"] == line_id)
    line["technical_fact_refs"]["manufacturing_scope"] = None
    assessed = compare_lines(
        changed, register, sector_profile="technical_plastics",
        decision_gates=inputs["decision_specific_hard_gates"],
    )
    result = discover_candidates(
        register, opportunity_id=changed["opportunity_id"],
        opportunity_hs6="390210", candidate_lines=candidate_lines,
        scenario_id=changed["scenario_id"], scenario=changed,
        line_assessment=assessed,
    )
    row = next(item for item in result["rows"] if item["entity_id"] == line_id)
    tooling = next(finding for finding in row["findings"]
                   if finding["requirement_item_id"] == "tooling_required")
    assert tooling["current_recorded"] is False
    assert tooling["needed"] is False
    assert tooling["status"] == "NOT_ESTABLISHED"
    assert tooling["next_evidence"]["missing_field"] == "tooling_required"
    assert tooling["next_evidence"]["subject_scope"] == line_id
    assert tooling["next_evidence"] in row["next_evidence_actions"]


def test_conflicted_mfr_keeps_scoped_next_record_request() -> None:
    from ior_mvp.line_comparison import compare_lines

    scenario, _register, _lines = _register_and_lines("SYN-MINISTRY-PP-001.json")
    changed = deepcopy(scenario)
    inputs = changed["synthetic_inputs"]
    register = inputs["candidate_register"]
    original = next(fact for fact in register["facts"]
                    if fact["fact_id"] == "FACT-MFR-LINE-e403e85a85052861")
    conflicting = deepcopy(original)
    conflicting["fact_id"] = "FACT-MFR-CONFLICT-LINE-e403e85a85052861"
    conflicting["values"]["value"] = [2, 6]
    register["facts"].append(conflicting)
    assessed = compare_lines(
        changed, register, sector_profile="technical_plastics",
        decision_gates=inputs["decision_specific_hard_gates"],
    )
    result = discover_candidates(
        register, opportunity_id=changed["opportunity_id"],
        opportunity_hs6="390210", candidate_lines=inputs["candidate_lines"],
        scenario_id=changed["scenario_id"], scenario=changed,
        line_assessment=assessed,
    )
    line_id = "LINE-e403e85a85052861"
    row = next(item for item in result["rows"] if item["entity_id"] == line_id)
    mfr = next(finding for finding in row["findings"]
               if finding["requirement_item_id"] == "mfr_range_g_10min")
    assert mfr["status"] == "CONFLICTED"
    request = mfr["next_evidence"]
    assert request["missing_field"] == "mfr_range_g_10min"
    assert request["dataset_or_action"] == "TECHNICAL_ENRICHMENT"
    assert request["route_effect"]
    assert request["subject_scope"] == line_id
    assert request in row["next_evidence_actions"]


def test_company_only_customs_context_stays_at_company_grain() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    company = next(
        row for row in result["candidate_discovery"]["rows"]
        if row["entity_id"] == "COMPANY-18fe4f8ef742608b"
    )
    assert company["entity_kind"] == "COMPANY"
    procurement = next(
        finding for finding in company["findings"]
        if finding["rule_id"] == "P03"
    )
    assert procurement["status"] == "NOT_ESTABLISHED"
    assert procurement["reason_code"] == "P03_COMPANY_TRADE_CONTEXT_NOT_INPUT"
    assert procurement["current_recorded"]["hs6"] == "721049"
    assert procurement["next_evidence"]["subject_scope"] == company["entity_id"]


def _register_and_lines(name: str) -> tuple[dict, dict, dict]:
    scenario = json.loads(
        (ROOT / "data" / "synthetic" / name).read_text(encoding="utf-8")
    )
    return (
        scenario,
        scenario["synthetic_inputs"]["candidate_register"],
        scenario["synthetic_inputs"]["candidate_lines"],
    )


def test_p09_uses_same_governed_detailed_quantity_as_line_gap() -> None:
    from ior_mvp.line_comparison import compare_lines

    for name, hs6, profile, demand in (
        ("SYN-MINISTRY-STEEL-001.json", "721049", "coated_steel", 104),
        ("SYN-MINISTRY-PP-001.json", "390210", "technical_plastics", 56),
    ):
        scenario, register, lines = _register_and_lines(name)
        assessment = compare_lines(
            scenario, register, sector_profile=profile,
            decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
        )
        discovery = discover_candidates(
            register, opportunity_id=scenario["opportunity_id"],
            opportunity_hs6=hs6, candidate_lines=lines,
            scenario_id=scenario["scenario_id"], scenario=scenario,
            line_assessment=assessment,
        )
        by_line = {row["line_id"]: row for row in assessment["rows"]}
        for row in discovery["rows"]:
            if row["entity_kind"] != "LINE":
                continue
            volume = next(f for f in row["findings"] if f["rule_id"] == "P09")
            assert volume["needed"] == demand
            assert volume["current_recorded"]["admitted_qualified_supply_kt"] == by_line[row["entity_id"]]["capacity"]["admitted_qualified_supply_kt"]
            assert volume["quantified_gap"] == by_line[row["entity_id"]]["capacity"]["shortage_kt"]
        if hs6 == "390210":
            lines["requirements_additions"]["detailed_quantity_kt"] = 60
            assert scenario["synthetic_inputs"]["demand"]["target_spec_demand_kt"] == 56
            revised = compare_lines(
                scenario, register, sector_profile=profile,
                decision_gates=scenario["synthetic_inputs"]["decision_specific_hard_gates"],
            )
            changed = discover_candidates(
                register, opportunity_id=scenario["opportunity_id"],
                opportunity_hs6=hs6, candidate_lines=lines,
                scenario_id=scenario["scenario_id"], scenario=scenario,
                line_assessment=revised,
            )
            for row in changed["rows"]:
                if row["entity_kind"] == "LINE":
                    assert next(f for f in row["findings"] if f["rule_id"] == "P09")["needed"] == 60


def _rows(result: dict) -> dict[str, str]:
    return {row["entity_id"]: row["disposition"] for row in result["rows"]}


def test_steel_discovery_keeps_reference_decisions_and_screens_plants() -> None:
    public = analyze("SAU-H0-721049", "public")
    simulated = analyze("SAU-H0-721049", "simulated")
    assert public["real_decision"]["state"] == "INVESTIGATE"
    assert "candidate_discovery" not in public
    assert simulated["real_decision"]["state"] == "INVESTIGATE"
    assert simulated["simulation_decision"]["state"] == "ADVANCE"
    rows = _rows(simulated["candidate_discovery"])
    assert rows["PLANT-8932de539dd9d7d8"] == "PASS_TO_ASSESSMENT"
    assert rows["PLANT-b24ad239aa497c75"] == "PASS_TO_ASSESSMENT"
    assert rows["PLANT-5bb27c71985d4b9d"] == "RELATED_ONLY"
    assert rows["COMPANY-18fe4f8ef742608b"] == "NOT_ESTABLISHED"
    assert rows["PLANT-8aa26a75aa4f7ed2"] == "NOT_ESTABLISHED"
    assert rows["PLANT-9d6ea91bce253036"] == "OUTSIDE_TARGET"


def test_related_steel_plant_keeps_recorded_stage_without_target_credit() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    plant_id = "PLANT-5bb27c71985d4b9d"
    output_id = f"FACT-OUT-{plant_id}"
    recorded = next(fact for fact in register["facts"] if fact["fact_id"] == output_id)
    result = discover_candidates(
        register, opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049", candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    plant = next(row for row in result["rows"] if row["entity_id"] == plant_id)
    findings = {finding["rule_id"]: finding for finding in plant["findings"]}
    assert plant["disposition"] == "RELATED_ONLY"
    assert plant["r9s"]["fired"] is False
    assert output_id not in plant["evidence_boundary"]["signal_fact_ids"]
    assert findings["P01"]["status"] == "SUPPORTED"
    assert findings["P01"]["current_recorded"]["product_family"] == "cold_rolled_sheet"
    assert findings["P02"]["status"] == "SUPPORTED"
    assert findings["P02"]["current_recorded"]["hs6"] == "720916"
    assert findings["P02"]["current_recorded"]["quantity_kt"] == 80
    assert findings["P02"]["source_refs"] == recorded["source_refs"]
    assert findings["P02"]["temporal_scope"] == recorded["window"]
    assert findings["P02"]["next_evidence"] is None
    assert findings["P05"]["status"] == "NOT_ESTABLISHED"
    assert findings["P05"]["current_recorded"] == {"process_route": "COLD_ROLLING"}
    assert findings["P05"]["next_evidence"]["missing_field"] == "process_route"

    without_output = deepcopy(register)
    without_output["facts"] = [
        fact for fact in without_output["facts"] if fact["fact_id"] != output_id
    ]
    changed = discover_candidates(
        without_output, opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049", candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    changed_plant = next(row for row in changed["rows"] if row["entity_id"] == plant_id)
    changed_output = next(finding for finding in changed_plant["findings"] if finding["rule_id"] == "P02")
    assert changed_output["status"] == "NOT_ESTABLISHED"
    assert changed_output["current_recorded"] is None
    assert changed_plant["r9s"]["fired"] is False

    simulated = analyze("SAU-H0-721049", "simulated")
    line = next(row for row in simulated["line_assessment"]["rows"]
                if row["line_id"] == "LINE-4fbdbb0b2c107968")
    assert line["capability"]["known_weight_coverage"] == 0
    assert all(item["state"] == "U" for item in line["capability"]["dimensions"])
    assert line["capability"]["d_star"] is None
    assert line["capacity"]["admitted_qualified_supply_kt"] is None


def test_p05_supported_operand_and_provenance_follow_selected_registry_fact() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    plant_id = "PLANT-5bb27c71985d4b9d"
    original = next(fact for fact in register["facts"] if fact["fact_id"] == f"FACT-REG-{plant_id}")
    matching = deepcopy(original)
    matching["fact_id"] = f"FACT-REG-SECOND-{plant_id}"
    matching["values"]["process_route"] = "HOT_DIP_GALVANISING"
    matching["source_refs"][0]["pointer"] = f"/synthetic_inputs/candidate_register/facts/{matching['fact_id']}"
    register["facts"].append(matching)
    validate_candidate_register(register)
    for reverse in (False, True):
        if reverse:
            register["facts"].reverse()
        result = discover_candidates(
            register, opportunity_id=scenario["opportunity_id"],
            opportunity_hs6="721049", candidate_lines=lines,
            scenario_id=scenario["scenario_id"],
        )
        plant = next(row for row in result["rows"] if row["entity_id"] == plant_id)
        finding = next(row for row in plant["findings"] if row["rule_id"] == "P05")
        assert finding["status"] == "SUPPORTED"
        assert finding["current_recorded"] == {"process_route": "HOT_DIP_GALVANISING"}
        assert finding["source_refs"] == matching["source_refs"]
        assert finding["next_evidence"] is None


def ninth_company_fixture() -> tuple[dict, dict, dict]:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    added = deepcopy(register)
    company_id = "COMPANY-aaaaaaaaaaaaaaaa"
    plant_id = "PLANT-bbbbbbbbbbbbbbbb"
    added["companies"].append(
        {
            "company_id": company_id,
            "name_en": "Synthetic Ninth",
            "name_ar": "الشركة التاسعة التوضيحية",
            "manufacturer_assignment": None,
        }
    )
    added["plants"].append(
        {
            "plant_id": plant_id,
            "company_id": company_id,
            "country": "SA",
            "status": "OPERATING",
            "registry_fact_ids": ["FACT-REG-NINTH"],
        }
    )
    added["facts"].extend(
        [
            {
                "fact_id": "FACT-REG-NINTH",
                "kind": "REGISTRY_ACTIVITY",
                "dataset_kind": "REGISTRY",
                "subject_type": "PLANT",
                "subject_id": plant_id,
                "window": {"start": "2026-06-30", "end": "2026-07-01"},
                "values": {
                    "country": "SA",
                    "status": "OPERATING",
                    "product_family": "coated_steel",
                    "process_route": "HOT_DIP_GALVANISING",
                    "operating_status_asserted_by_registry": True,
                },
                "origin": "DIRECT_RECORD",
                "source_refs": [{
                    "pointer": "/synthetic_inputs/candidate_register/facts/FACT-REG-NINTH",
                    "purpose": "class_d_demonstration",
                }],
                "rule_id": None,
            },
            {
                "fact_id": "FACT-OUT-NINTH",
                "kind": "PRODUCTION_ACTUAL",
                "dataset_kind": "PRODUCTION_ACTUALS",
                "subject_type": "PLANT",
                "subject_id": plant_id,
                "window": {"start": "2024-01-01", "end": "2025-01-01"},
                "values": {
                    "hs_revision": "H6",
                    "hs6": "721049",
                    "production_kind": "OWN_PRODUCTION",
                    "process_family": "coated_steel",
                    "quantity_kt": 10,
                },
                "origin": "DIRECT_RECORD",
                "source_refs": [{
                    "pointer": "/synthetic_inputs/candidate_register/facts/FACT-OUT-NINTH",
                    "purpose": "class_d_demonstration",
                }],
                "rule_id": None,
            },
        ]
    )
    result = discover_candidates(
        added,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    scenario["synthetic_inputs"]["candidate_register"] = added
    return scenario, added, result


def test_ninth_company_is_discovered_without_a_line_entry() -> None:
    scenario, added, result = ninth_company_fixture()
    plant_id = "PLANT-bbbbbbbbbbbbbbbb"
    lines = scenario["synthetic_inputs"]["candidate_lines"]
    assert _rows(result)[plant_id] == "PASS_TO_ASSESSMENT"
    assert all(line["line_id"] != plant_id for line in lines["lines"])


def test_non_admitted_hs6_removes_procurement_support() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    baseline = discover_candidates(
        register,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    mutated = deepcopy(register)
    customs = next(
        fact for fact in mutated["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A"
    )
    customs["values"]["hs6"] = "390210"
    changed = discover_candidates(
        mutated,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )

    def procurement(result: dict) -> str:
        plant = next(
            row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8"
        )
        finding = next(
            item for item in plant["findings"] if item["rule_id"] == "P03"
        )
        return finding["status"]

    assert procurement(baseline) == "SUPPORTED"
    assert procurement(changed) == "NOT_ESTABLISHED"


def test_rendered_dossier_excludes_workspace_diagnostics() -> None:
    from ior_mvp.data_repository import get_synthetic_scenario
    from ior_mvp.dossier_projection import project_dossier

    simulated = analyze("SAU-H0-721049", "simulated")
    dossier = project_dossier(
        simulated,
        get_synthetic_scenario("SAU-H0-721049"),
    )
    assert "candidate_discovery" not in dossier
    assert "line_assessment" not in dossier
    assert "candidate_register" not in dossier["evidence_pack"]["scenario_inputs"]


def test_linked_hot_dip_acquisition_is_equipment_context_only() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    added = deepcopy(register)
    customs = {
        "fact_id": "FACT-EQ-CUS",
        "kind": "FACTORY_CUSTOMS",
        "dataset_kind": "FACTORY_CUSTOMS",
        "subject_type": "PLANT",
        "subject_id": "PLANT-8932de539dd9d7d8",
        "window": {"start": "2025-01-01", "end": "2025-06-01"},
        "values": {
            "hs_revision": "H6",
            "hs6": "847981",
            "description": "display only",
            "flow": "IMPORT",
            "quantity_kt": 1,
            "reexport": False,
            "transaction_id": "TX-EQ",
            "equipment_model_id": "MODEL-EQ",
        },
        "origin": "DIRECT_RECORD",
        "source_refs": [{
            "pointer": "/synthetic_inputs/candidate_register/facts/FACT-EQ-CUS",
            "purpose": "class_d_demonstration",
        }],
        "rule_id": None,
    }
    technical = {
        "fact_id": "FACT-EQ-TECH",
        "kind": "EQUIPMENT_TECHNICAL",
        "dataset_kind": "TECHNICAL_ENRICHMENT",
        "subject_type": "PLANT",
        "subject_id": "PLANT-8932de539dd9d7d8",
        "window": {"start": "2025-01-01", "end": "2025-06-01"},
        "values": {
            "customs_fact_id": "FACT-EQ-CUS",
            "transaction_id": "TX-EQ",
            "equipment_model_id": "MODEL-EQ",
            "function": "HOT_DIP_ZINC_COATING",
            "workpiece_material": "STEEL_STRIP",
        },
        "origin": "ENGINEERING_DECLARATION",
        "source_refs": [{
            "pointer": "/synthetic_inputs/candidate_register/facts/FACT-EQ-TECH",
            "purpose": "class_d_demonstration",
        }],
        "rule_id": None,
    }
    added["facts"].extend([customs, technical])
    items = deepcopy(lines)
    items["requirements_additions"]["discovery_items"].append(
        {
            "item_id": "equipment_acquisition",
            "rule_id": "P04",
            "record_selectors": [["FACTORY_CUSTOMS", "hs6"], ["EQUIPMENT_TECHNICAL", "function"]],
            "hs_revision": "H6",
            "admitted_hs6": ["847981"],
            "basis": "WCO HS 2022 subheading 8479.81",
        }
    )
    result = discover_candidates(
        added,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=items,
        scenario_id=scenario["scenario_id"],
    )
    plant = next(
        row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8"
    )
    finding = next(item for item in plant["findings"] if item["rule_id"] == "P04")
    assert finding["status"] == "SUPPORTED"
    assert finding["reason_code"] == "P04_GALVANISING_ACQUISITION"
    assert finding["origin"] == "REVIEWED_INFERENCE"
    assert plant["r9s"]["fired"] is True
    assert "installed" not in json.dumps(finding)


def test_wire_coil_winder_does_not_become_galvanising_equipment() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    added = deepcopy(register)
    added["facts"].extend([
        {
            "fact_id": "FACT-EQ-CUS-NEG",
            "kind": "FACTORY_CUSTOMS",
            "dataset_kind": "FACTORY_CUSTOMS",
            "subject_type": "PLANT",
            "subject_id": "PLANT-8932de539dd9d7d8",
            "window": {"start": "2025-01-01", "end": "2025-06-01"},
            "values": {
                "hs_revision": "H6", "hs6": "847981", "description": "display only",
                "flow": "IMPORT", "quantity_kt": 1, "reexport": False,
                "transaction_id": "TX-NEG", "equipment_model_id": "MODEL-NEG",
            },
            "origin": "DIRECT_RECORD",
            "source_refs": [{"pointer": "/synthetic_inputs/candidate_register/facts/FACT-EQ-CUS-NEG", "purpose": "class_d_demonstration"}],
            "rule_id": None,
        },
        {
            "fact_id": "FACT-EQ-TECH-NEG",
            "kind": "EQUIPMENT_TECHNICAL",
            "dataset_kind": "TECHNICAL_ENRICHMENT",
            "subject_type": "PLANT",
            "subject_id": "PLANT-8932de539dd9d7d8",
            "window": {"start": "2025-01-01", "end": "2025-06-01"},
            "values": {
                "customs_fact_id": "FACT-EQ-CUS-NEG",
                "transaction_id": "TX-NEG",
                "equipment_model_id": "MODEL-NEG",
                "function": "WIRE_COIL_WINDING",
                "workpiece_material": "STEEL_STRIP",
            },
            "origin": "ENGINEERING_DECLARATION",
            "source_refs": [{"pointer": "/synthetic_inputs/candidate_register/facts/FACT-EQ-TECH-NEG", "purpose": "class_d_demonstration"}],
            "rule_id": None,
        },
    ])
    result = discover_candidates(
        added,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    plant = next(row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8")
    finding = next(item for item in plant["findings"] if item["rule_id"] == "P04")
    assert finding["status"] == "NOT_ESTABLISHED"
    assert finding["reason_code"] == "P04_BASIS_NOT_ESTABLISHED"
    assert "equipment" not in {signal["signal_type"] for signal in plant.get("r9s", {}).get("coarse_adjacency_signals", [])}


def test_description_mutation_does_not_change_procurement_meaning() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    before = discover_candidates(
        register,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    mutated = deepcopy(register)
    customs = next(fact for fact in mutated["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A")
    customs["values"]["description"] = "GALVANISING_EQUIPMENT_DEMO"
    after = discover_candidates(
        mutated,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )

    def meaning(result: dict) -> tuple:
        plant = next(row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8")
        finding = next(item for item in plant["findings"] if item["rule_id"] == "P03")
        return (
            finding["status"], finding["reason_code"], finding["action_code"],
            plant["evidence_boundary"]["signal_fact_ids"], plant["disposition"],
        )

    assert meaning(before) == meaning(after)


def test_company_customs_do_not_fan_out_to_another_plant() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    mutated = deepcopy(register)
    customs = next(fact for fact in mutated["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A")
    customs["subject_type"] = "COMPANY"
    customs["subject_id"] = "COMPANY-ed24005b198e52e5"
    mutated["attribution_links"] = [
        link for link in mutated["attribution_links"] if link["fact_id"] != "FACT-CUS-STEEL-A"
    ]
    result = discover_candidates(
        mutated,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    steel_a = next(row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8")
    steel_b = next(row for row in result["rows"] if row["entity_id"] == "PLANT-b24ad239aa497c75")
    procurement = next(item for item in steel_a["findings"] if item["rule_id"] == "P03")
    assert procurement["status"] == "NOT_ESTABLISHED"
    assert "FACT-CUS-STEEL-A" not in steel_b["evidence_boundary"]["signal_fact_ids"]
    assert steel_b["disposition"] == "PASS_TO_ASSESSMENT"


def test_procurement_outside_searched_window_is_context_not_support() -> None:
    from ior_mvp.scenario_contract import validate_simulation_contract

    scenario, _register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    changed = deepcopy(scenario)
    register = changed["synthetic_inputs"]["candidate_register"]
    customs = next(f for f in register["facts"] if f["fact_id"] == "FACT-CUS-STEEL-A")
    customs["window"] = {"start": "2024-01-01", "end": "2025-01-01"}
    next(a for a in register["attribution_links"] if a["fact_id"] == customs["fact_id"])["window"] = deepcopy(customs["window"])
    validate_simulation_contract(changed)
    result = discover_candidates(register, opportunity_id=changed["opportunity_id"],
        opportunity_hs6="721049", candidate_lines=lines,
        scenario_id=changed["scenario_id"])
    plant = next(r for r in result["rows"] if r["entity_id"] == "PLANT-8932de539dd9d7d8")
    finding = next(f for f in plant["findings"] if f["rule_id"] == "P03")
    assert finding["status"] == "NOT_ESTABLISHED"
    assert finding["reason_code"] == "P03_OUTSIDE_SEARCHED_WINDOW"
    assert finding["temporal_scope"] == customs["window"]
    assert finding["source_refs"] == customs["source_refs"]
    assert finding["next_evidence"]["missing_field"] == "in_scope_procurement_record"
    assert customs["fact_id"] not in plant["evidence_boundary"]["signal_fact_ids"]


def test_company_grain_procurement_preserves_context_and_attribution_request() -> None:
    from ior_mvp.scenario_contract import validate_simulation_contract

    scenario, _register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    changed = deepcopy(scenario)
    register = changed["synthetic_inputs"]["candidate_register"]
    customs = next(f for f in register["facts"] if f["fact_id"] == "FACT-CUS-STEEL-A")
    company_id = "COMPANY-ed24005b198e52e5"
    customs["subject_type"], customs["subject_id"] = "COMPANY", company_id
    register["attribution_links"] = [
        a for a in register["attribution_links"] if a["fact_id"] != customs["fact_id"]
    ]
    validate_simulation_contract(changed)
    result = discover_candidates(register, opportunity_id=changed["opportunity_id"],
        opportunity_hs6="721049", candidate_lines=lines,
        scenario_id=changed["scenario_id"])
    company = next(r for r in result["rows"] if r["entity_id"] == company_id)
    plant = next(r for r in result["rows"] if r["entity_id"] == "PLANT-8932de539dd9d7d8")
    company_finding = next(f for f in company["findings"] if f["rule_id"] == "P03")
    plant_finding = next(f for f in plant["findings"] if f["rule_id"] == "P03")
    assert company_finding["source_refs"] == customs["source_refs"]
    assert company_finding["temporal_scope"] == customs["window"]
    assert company_finding["reason_code"] == "P03_COMPANY_PROCUREMENT_CONTEXT"
    assert company_finding["next_evidence"]["missing_field"] == "factory_attribution_link"
    assert company_finding["next_evidence"]["subject_scope"] == company_id
    assert plant_finding["status"] == "NOT_ESTABLISHED"
    assert plant_finding["next_evidence"]["missing_field"] == "factory_attribution_link"
    assert customs["fact_id"] not in plant["evidence_boundary"]["signal_fact_ids"]


def test_removing_line_enrichment_keeps_register_discovery() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    bare = deepcopy(register)
    bare["facts"] = [
        fact for fact in bare["facts"] if fact["dataset_kind"] != "TECHNICAL_ENRICHMENT"
    ]
    result = discover_candidates(
        bare,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    rows = _rows(result)
    assert rows["PLANT-8932de539dd9d7d8"] == "PASS_TO_ASSESSMENT"
    assert rows["PLANT-b24ad239aa497c75"] == "PASS_TO_ASSESSMENT"
    assert rows["PLANT-5bb27c71985d4b9d"] == "RELATED_ONLY"


def test_reexport_removes_only_the_affected_procurement_signal() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    mutated = deepcopy(register)
    customs = next(fact for fact in mutated["facts"] if fact["fact_id"] == "FACT-CUS-STEEL-A")
    customs["values"]["reexport"] = True
    result = discover_candidates(
        mutated,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    plant = next(row for row in result["rows"] if row["entity_id"] == "PLANT-8932de539dd9d7d8")
    procurement = next(item for item in plant["findings"] if item["rule_id"] == "P03")
    output = next(item for item in plant["findings"] if item["rule_id"] == "P02")
    assert procurement["status"] == "NOT_ESTABLISHED"
    assert output["status"] == "SUPPORTED"
    assert plant["disposition"] == "PASS_TO_ASSESSMENT"


def test_ground_truth_mutation_through_simulate_leaves_findings_unchanged() -> None:
    from ior_mvp.data_repository import get_public_case
    from ior_mvp.simulation import simulate

    scenario, _register, _lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    public = get_public_case("SAU-H0-721049")
    before = simulate(public, scenario)
    mutated = deepcopy(scenario)
    mutated["ground_truth"]["expected_simulation_state"] = "REJECT"
    after = simulate(public, mutated)
    assert before["candidate_discovery"] == after["candidate_discovery"]
    assert before["line_assessment"] == after["line_assessment"]
    assert before["simulation_decision"]["state"] == after["simulation_decision"]["state"]


def test_golden_real_decisions_stay_on_the_recorded_states() -> None:
    from ior_mvp.config import project_config

    for row in project_config()["golden_cases"]:
        result = analyze(row["opportunity_id"], "simulated")
        assert result["real_decision"]["state"] == row["public_expected_state"]
        assert result["simulation_decision"]["state"] == row["simulated_expected_state"]
        if row["opportunity_id"] not in {"SAU-H0-721049", "SAU-H0-390210"}:
            assert result["candidate_discovery"]["reason"] == "NO_REGISTER"
            assert result["line_assessment"]["reason"] == "NO_LINE_RECORDS"


def test_ground_truth_mutation_does_not_change_discovery() -> None:
    scenario, register, lines = _register_and_lines("SYN-MINISTRY-STEEL-001.json")
    before = discover_candidates(
        register,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    scenario["ground_truth"]["expected_simulation_state"] = "REJECT"
    after = discover_candidates(
        register,
        opportunity_id=scenario["opportunity_id"],
        opportunity_hs6="721049",
        candidate_lines=lines,
        scenario_id=scenario["scenario_id"],
    )
    assert before == after
