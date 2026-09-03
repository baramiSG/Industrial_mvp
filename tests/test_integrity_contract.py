from __future__ import annotations

import json
import re
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


def test_manifests_exist_and_track_expected_files() -> None:
    snapshot_manifest = PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json"
    authority_manifest = PROJECT_ROOT / "docs" / "authority" / "authority_hashes.json"
    assert snapshot_manifest.exists()
    assert authority_manifest.exists()

    snapshots = json.loads(snapshot_manifest.read_text(encoding="utf-8"))
    authorities = json.loads(authority_manifest.read_text(encoding="utf-8"))
    snapshot_paths = {item["path"] for item in snapshots["files"]}
    authority_paths = {item["path"] for item in authorities["files"]}

    assert "data/snapshots/public/SAU-H0-721049.json" in snapshot_paths
    assert "data/snapshots/public/SAU-H0-390210.json" in snapshot_paths
    assert "data/synthetic/SYN-MINISTRY-STEEL-001.json" in snapshot_paths
    assert "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx" in authority_paths
    assert "config/thresholds.v1.yaml" in authority_paths
    assert "config/ui_strings.v1.yaml" in authority_paths
    assert "config/decision_narratives.v1.yaml" in authority_paths


def test_s08_snapshot_manifest_retains_live_and_historical_public_rows(
) -> None:
    manifest = json.loads(
        (
            PROJECT_ROOT
            / "data"
            / "manifests"
            / "snapshot_manifest.json"
        ).read_text(encoding="utf-8")
    )
    paths = {item["path"] for item in manifest["files"]}

    assert {
        "data/snapshots/public/SAU-H0-721049.json",
        "data/snapshots/public/SAU-H0-390210.json",
        (
            "data/snapshots/public/historical/v1/"
            "SAU-H0-721049.json"
        ),
        (
            "data/snapshots/public/historical/v1/"
            "SAU-H0-390210.json"
        ),
        "data/synthetic/SYN-MINISTRY-STEEL-001.json",
        "data/synthetic/SYN-MINISTRY-PP-001.json",
        "data/synthetic/historical/v1_1/SYN-MINISTRY-STEEL-001.json",
        "data/synthetic/historical/v1_1/SYN-MINISTRY-PP-001.json",
        "data/golden/ar_en_spec_extraction.json",
    } == paths


def test_s07_core_v2_markers_and_minimal_contract_text_are_exact() -> None:
    marker = (
        "<!-- core_version: 2.0.0; supersedes: 1.0.0; "
        "effective_date: 2026-09-02 -->"
    )
    core_01 = (
        PROJECT_ROOT / "docs" / "core" / "01_PRODUCT_AND_REQUIREMENTS.md"
    ).read_text(encoding="utf-8")
    core_02 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")

    assert core_01.splitlines()[2] == marker
    assert core_02.splitlines()[2] == marker
    assert core_09.splitlines()[2] == marker
    assert (
        "**NFR-007 Bilingual interface and Arabic support:** "
        "All interface chrome and governed labels shall have "
        "Arabic/English content parity"
    ) in core_01
    assert "config.ui_strings_bundle" in core_02
    assert "evidence.synthetic_display_labels" in core_02
    assert "### 2.7 Frontend contract and real-browser visual tests" in core_09
    assert "Post-redesign visual baselines are hashed test oracles" in core_09


def test_s08_core_v2_contracts_map_schema_and_computed_rules() -> None:
    marker = (
        "<!-- core_version: 2.0.0; supersedes: 1.0.0; "
        "effective_date: 2026-09-02 -->"
    )
    core_02 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_07 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")

    assert core_02.count(marker) == 1
    assert core_04.splitlines()[2] == marker
    assert core_07.splitlines()[2] == marker
    assert core_09.count(marker) == 1
    for function in (
        "public_snapshot.validate_public_snapshot",
        "trade_metrics.compound_annual_growth",
        "trade_metrics.latest_usable_trade_pair",
        "trade_metrics.concentration_metrics",
        "trade_metrics.degraded_dispersion_metrics",
        "trade_metrics.domestic_flow_metrics",
        "trade_metrics.export_import_value_ratio",
        "trade_metrics.established_domestic_nameplate",
        "trade_metrics.build_supplier_metrics",
        "public_snapshot.capability_hard_gate_names",
        "public_snapshot.has_known_hard_gate_failure",
    ):
        assert function in core_02
    assert "### PublicSnapshot 2.1" in core_04
    assert "contains no `public_decision_contract`" in core_04
    assert "### S08 computed public-rule semantics" in core_07
    assert "Product IDs, disclosed ratios, and authored flags" in core_07
    assert "### Public snapshot schema-migration proof" in core_09
    assert "historical paths are manifested but never loaded" in core_09


def test_s09_core_v2_contracts_define_the_generalized_public_engine() -> None:
    marker = (
        "<!-- core_version: 2.0.0; supersedes: 1.0.0; "
        "effective_date: 2026-09-02 -->"
    )
    core = {
        number: (
            PROJECT_ROOT / "docs" / "core" / filename
        ).read_text(encoding="utf-8")
        for number, filename in {
            "01": "01_PRODUCT_AND_REQUIREMENTS.md",
            "02": "02_METHODOLOGY_IMPLEMENTATION_MAP.md",
            "04": "04_CANONICAL_DATA_MODEL.md",
            "07": "07_DETERMINISTIC_ENGINE_SPEC.md",
            "09": "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md",
        }.items()
    }

    assert all(text.count(marker) == 1 for text in core.values())
    assert (
        "stop at `INVESTIGATE` when route-changing decision-critical "
        "evidence is unavailable; permit `ADVANCE` when actual A/B/C "
        "evidence and every methodology gate pass."
    ) in core["01"]
    for requirement in range(35, 40):
        assert f"**FR-0{requirement}**" in core["01"]
    for requirement in range(46, 50):
        assert f"**FR-0{requirement}**" in core["01"]
    for implementation in (
        "public_decision.assess_decision_critical_fields",
        "public_decision.evaluate_hard_exclusions",
        "public_decision.classify_gap",
        "route_hypotheses.py",
        "evidence_needs.py",
        "narratives.py",
        "signals.py",
    ):
        assert implementation in core["02"]
    assert "advance_supporting_signal_rule_ids" in core["02"]
    assert "### PublicSnapshot 2.1" in core["04"]
    assert "contains no `public_decision_contract`" in core["04"]
    assert "### 7.2 Decision-critical field assessment" in core["07"]
    assert "### 7.6 Formal state and screening disposition" in core["07"]
    assert "### 7.7 Route hypotheses and selection" in core["07"]
    assert "Route 8 always returns `NOT_CALCULABLE`" in core["07"]
    normalized_core_07 = " ".join(core["07"].split())
    assert (
        "fails closed with a decision-integrity error rather than being "
        "silently called REJECT or MONITOR"
    ) in normalized_core_07
    assert "ADVANCE_SUPPORT_SIGNAL_DEGRADED" in core["07"]
    assert "ROUTE_DETERMINATION_UNRESOLVED" in core["07"]
    assert "may_support_advance" in core["07"]
    assert "unregistered REJECT" in core["07"]
    assert "MONITOR_NO_IMMEDIATE_ACTION" in core["07"]
    assert "investigate.route.unresolved" in core["07"]
    assert "rationale.route_unresolved" in core["07"]
    idx_77 = core["07"].index("### 7.7 Route hypotheses and selection")
    idx_78 = core["07"].index("### 7.8 Golden public outcomes")
    section_77 = core["07"][idx_77:idx_78]
    assert "MONITOR_NO_IMMEDIATE_ACTION" in section_77
    assert "MONITOR_NO_IMMEDIATE_ACTION" not in core["07"][:idx_77]
    investigate_section = core["07"].split("INVESTIGATE selects route label", 1)[1]
    assert "decision.public.investigate.rationale.preferred" in investigate_section
    assert (
        "otherwise the engine uses `route.hypothesis.priority` with "
        "`rationale.preferred`"
    ) not in normalized_core_07
    assert "### Public decision generalization proof" in core["09"]
    normalized_core_09 = " ".join(core["09"].split())
    assert (
        "A/B/C decision-critical evidence and every "
        "route/economics/policy gate passing must reach real ADVANCE"
    ) in normalized_core_09
    assert "ADVANCE_SUPPORT_SIGNAL_DEGRADED" in normalized_core_09
    assert "mocked-loader missing-economics proof" in normalized_core_09
    assert "typed rejection narratives" in normalized_core_09
    assert "fired-rule confidence cap" in normalized_core_09
    assert "Exact-Arabic catalogue proofs" in normalized_core_09


def test_s10_core_v2_contracts_define_the_generalized_simulation() -> None:
    marker = (
        "<!-- core_version: 2.0.0; supersedes: 1.0.0; "
        "effective_date: 2026-09-02 -->"
    )
    core = {
        number: (
            PROJECT_ROOT / "docs" / "core" / filename
        ).read_text(encoding="utf-8")
        for number, filename in {
            "01": "01_PRODUCT_AND_REQUIREMENTS.md",
            "02": "02_METHODOLOGY_IMPLEMENTATION_MAP.md",
            "04": "04_CANONICAL_DATA_MODEL.md",
            "06": "06_SYNTHETIC_MINISTRY_DATA_SPEC.md",
            "07": "07_DETERMINISTIC_ENGINE_SPEC.md",
            "09": "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md",
        }.items()
    }
    snapshot_manifest = json.loads(
        (
            PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json"
        ).read_text(encoding="utf-8")
    )
    synthetic_paths = {
        row["path"]
        for row in snapshot_manifest["files"]
        if row["path"].startswith("data/synthetic/")
    }

    assert all(text.splitlines()[2] == marker for text in core.values())
    for requirement in range(55, 60):
        assert f"**FR-0{requirement}**" in core["01"]
    for symbol in (
        "simulation.compute_simulated_decision",
        "scenario_contract.project_simulated_case",
        "scenario_contract.validate_simulation_contract",
        "route_hypotheses.evaluate_shared_enabler_route",
        "route_hypotheses.shared_enabler_unlock_value",
    ):
        assert symbol in core["02"]
    assert "class_if_confirmed" in core["04"]
    for token in (
        "historical/v1_1",
        "tariff_line_allocation",
        "CLASS_IF_CONFIRMED",
    ):
        assert token in core["06"]
    assert "### Generalized simulation proof" in core["09"]
    assert "data/synthetic/historical/v1_1/SYN-MINISTRY-STEEL-001.json" in (
        synthetic_paths
    )
    assert "data/synthetic/historical/v1_1/SYN-MINISTRY-PP-001.json" in (
        synthetic_paths
    )


def test_manifest_generator_includes_the_governed_ui_catalogue() -> None:
    source = (
        PROJECT_ROOT / "scripts" / "build_manifests.py"
    ).read_text(encoding="utf-8")

    assert 'ROOT / "config" / "ui_strings.v1.yaml"' in source
    assert (
        'ROOT / "config" / "decision_narratives.v1.yaml"'
        in source
    )


def test_human_authority_table_matches_machine_manifest_exactly() -> None:
    machine = json.loads(
        (
            PROJECT_ROOT / "docs" / "authority" / "authority_hashes.json"
        ).read_text(encoding="utf-8")
    )
    authority = (
        PROJECT_ROOT / "docs" / "authority" / "00_AUTHORITY_MANIFEST.md"
    ).read_text(encoding="utf-8")
    table = authority.split("<!-- HASH_TABLE_START -->", maxsplit=1)[1].split(
        "<!-- HASH_TABLE_END -->",
        maxsplit=1,
    )[0]
    rows = {
        path: (digest, int(byte_count.replace(",", "")))
        for path, digest, byte_count in re.findall(
            r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9,]+) \|",
            table,
        )
    }
    expected = {
        item["path"]: (item["sha256"], item["bytes"])
        for item in machine["files"]
    }

    assert rows == expected
