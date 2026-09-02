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
    assert "### PublicSnapshot v2" in core_04
    assert "contains no `rule_context`, `fired`, `execution`" in core_04
    assert "### S08 computed public-rule semantics" in core_07
    assert "Product IDs, disclosed ratios, and authored flags" in core_07
    assert "### Public snapshot schema-migration proof" in core_09
    assert "historical paths are manifested but never loaded" in core_09


def test_manifest_generator_includes_the_governed_ui_catalogue() -> None:
    source = (
        PROJECT_ROOT / "scripts" / "build_manifests.py"
    ).read_text(encoding="utf-8")

    assert 'ROOT / "config" / "ui_strings.v1.yaml"' in source


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
