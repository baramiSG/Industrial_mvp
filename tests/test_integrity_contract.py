from __future__ import annotations

import hashlib
import json
import re
import tomllib
from pathlib import Path

import yaml

from ior_mvp.config import PROJECT_ROOT


S14B_PUBLIC_AND_SYNTHETIC = {
    f"data/snapshots/public/PUBLIC-SAU-H6-{hs6}-2026-09-12.json"
    for hs6 in ("392010", "721012", "721061", "760429", "760711")
} | {
    f"data/synthetic/SYN-MINISTRY-{slug}-001.json"
    for slug in (
        "ALU-FOIL",
        "ALU-PROFILES",
        "GALVALUME",
        "PE-FILM",
        "TINPLATE",
    )
}
S15B_PUBLIC_AND_SYNTHETIC = {
    f"data/snapshots/public/PUBLIC-SAU-H6-{hs6}-2026-09-12.json"
    for hs6 in ("294110", "294120", "310430", "310510")
} | {
    f"data/synthetic/SYN-MINISTRY-{slug}-001.json"
    for slug in ("PENICILLIN-API", "STREPTOMYCIN-API", "SOP", "FERT-RETAIL-PACKS")
}
S16B_HISTORICAL_SCENARIOS = {
    "data/synthetic/historical/v2_0/SYN-MINISTRY-ALU-FOIL-001.json",
    "data/synthetic/historical/v2_0/SYN-MINISTRY-ALU-PROFILES-001.json",
}


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

    frozen = {
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
    } | S14B_PUBLIC_AND_SYNTHETIC | S15B_PUBLIC_AND_SYNTHETIC | S16B_HISTORICAL_SCENARIOS
    assert frozen <= paths
    allowed_extra_prefixes = (
        "data/raw/",
        "data/documents/",
        "data/entities/",
        "data/cases/",
        "data/screening/",
        "data/graph/",
        "config/history/",
        "data/snapshots/universe/",
        "data/snapshots/tariff/",
        "data/snapshots/partners/",
        "data/snapshots/production/",
        "data/snapshots/directory/",
        "data/snapshots/registry/",
    )
    extra = paths - frozen
    assert all(
        any(path.startswith(prefix) for prefix in allowed_extra_prefixes)
        for path in extra
    )


def _partition_valid(paths: set[str]) -> bool:
    frozen = {
        "data/snapshots/public/SAU-H0-721049.json",
        "data/snapshots/public/SAU-H0-390210.json",
        "data/snapshots/public/historical/v1/SAU-H0-721049.json",
        "data/snapshots/public/historical/v1/SAU-H0-390210.json",
        "data/synthetic/SYN-MINISTRY-STEEL-001.json",
        "data/synthetic/SYN-MINISTRY-PP-001.json",
        "data/synthetic/historical/v1_1/SYN-MINISTRY-STEEL-001.json",
        "data/synthetic/historical/v1_1/SYN-MINISTRY-PP-001.json",
        "data/golden/ar_en_spec_extraction.json",
    } | S14B_PUBLIC_AND_SYNTHETIC | S15B_PUBLIC_AND_SYNTHETIC | S16B_HISTORICAL_SCENARIOS
    if not frozen <= paths:
        return False
    allowed_extra_prefixes = (
        "data/raw/",
        "data/documents/",
        "data/entities/",
        "data/cases/",
        "data/screening/",
        "data/graph/",
        "config/history/",
        "data/snapshots/universe/",
        "data/snapshots/tariff/",
        "data/snapshots/partners/",
        "data/snapshots/production/",
        "data/snapshots/directory/",
        "data/snapshots/registry/",
    )
    extra = paths - frozen
    return all(
        any(path.startswith(prefix) for prefix in allowed_extra_prefixes)
        for path in extra
    )


def test_s11_snapshot_manifest_rejects_public_partition_leak() -> None:
    manifest = json.loads(
        (
            PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json"
        ).read_text(encoding="utf-8")
    )
    paths = {item["path"] for item in manifest["files"]}
    assert _partition_valid(paths)
    for required in S15B_PUBLIC_AND_SYNTHETIC | S16B_HISTORICAL_SCENARIOS:
        assert not _partition_valid(paths - {required})
    assert not _partition_valid(paths | {"data/snapshots/public/extra.json"})
    assert not _partition_valid(paths | {"data/synthetic/extra.json"})
    assert not _partition_valid(
        paths | {"data/synthetic/historical/v2_0/extra.json"}
    )
    for kind in ("production", "directory", "registry"):
        assert _partition_valid(paths | {f"data/snapshots/{kind}/extra.json"})
        assert not _partition_valid(paths | {f"data/snapshots/{kind}-other/extra.json"})
    assert _partition_valid(paths | {"data/documents/producer_unicoil/records/extra.json"})
    assert not _partition_valid(paths | {"data/documents-other/extra.json"})
    assert _partition_valid(paths | {"data/entities/resolution/extra.json"})
    assert not _partition_valid(paths | {"data/entities-other/extra.json"})
    assert _partition_valid(paths | {"data/screening/snapshots/extra.json"})
    assert not _partition_valid(paths | {"data/screening-other/extra.json"})
    assert _partition_valid(paths | {"data/cases/briefs/extra.json"})
    assert not _partition_valid(paths | {"data/cases-other/extra.json"})
    assert _partition_valid(paths | {"data/graph/projections/extra.json"})
    assert not _partition_valid(paths | {"data/graph-other/extra.json"})
    assert _partition_valid(paths | {"config/history/extra.yaml"})
    assert not _partition_valid(paths | {"config/history-other/extra.yaml"})
    assert not _partition_valid(paths | {"data/snapshots/unknown/extra.json"})


def test_s12a_core_v2_institutional_contracts() -> None:
    from ior_mvp.acquisition.passports import ACQUIRED_SUPPORT_CODES
    from ior_mvp.public_decision import SUPPORT_CODES

    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_05 = (
        PROJECT_ROOT / "docs" / "core" / "05_DATA_SOURCES_AND_INGESTION.md"
    ).read_text(encoding="utf-8")
    trade = core_05.split("### 3.1 Trade and demand\n", 1)[1].split(
        "### 3.2 Supply and capability\n", 1
    )[0]
    assert trade.splitlines().count(
        "| GASTAT foreign trade and open data | official domestic aggregate anchor | "
        "reconcile definitions and revisions | connector planned |"
    ) == 1
    assert "S12a" not in trade

    supply = core_05.split("### 3.2 Supply and capability\n", 1)[1].split(
        "### 3.3 Specifications and qualification\n", 1
    )[0]
    qualification = core_05.split(
        "### 3.3 Specifications and qualification\n", 1
    )[1].split("### 3.4 Economics\n", 1)[0]
    assert [line for line in supply.splitlines() if line.startswith("|")] == [
        "| Source | Use | Evidence class expectation |",
        "|---|---|---|",
        "| GASTAT economic census and industrial surveys | sector/establishment anchor | B/C until product-line reconciliation; connector implemented (S12a); availability and coverage recorded per run |",
        "| Ministry of Industry open data | licences and activity | B/C; licence is not production; connector implemented (S12a); availability and coverage recorded per run |",
        "| MODON directories | plant/entity discovery | C; connector implemented (S12a); availability and coverage recorded per run |",
        "| Tadawul filings and annual reports | nameplate, expansion and financial context | C; connector implemented (S12b); availability and coverage recorded per run |",
        "| EPDs and product sheets | process, range, standards and certifications | C; connector implemented (S12b); availability and coverage recorded per run |",
        "| Hadeed public catalogue | coated-steel process/product envelope | C; S14a run `20260912T233102Z` COMPLETE; one span-addressable record |",
        "| ALUPCO public profile | aluminium extrusion, sites and disclosed production envelope | C; S14a run `20260912T233130Z` COMPLETE; one span-addressable record |",
        "| Al Taiseer Group TALCO profile | aluminium profile manufacture, extrusion and finishing | C; S14a run `20260912T233154Z` COMPLETE; one span-addressable record |",
        "| Ma'aden annual report and results page | aluminium rolling and company production context | C; S14a run `20260912T233222Z` COMPLETE; two span-addressable records |",
        "| SPIMACO investor disclosures | publisher identity and disclosed pharmaceutical context only | C; S15 run `20260913T035150Z` stored one COMPLETE PDF unit; a second listed unit was not requested after the local parser dependency stop |",
        "| SABIC Agri-Nutrients annual report | publisher identity and disclosed fertiliser-company context only | C; S15 run `20260913T035235Z` COMPLETE; one span-addressable report |",
        "| SFDA drug-companies register | regulatory publisher/company-list observation | B; S15 run `20260913T035254Z` COMPLETE; `regulatory_authority` does not prove product manufacture, capacity or qualification |",
        "| GPCA / sector associations | sector capacity context | B/C |",
    ]
    assert supply.count("connector implemented (S12a)") == 3
    assert supply.count("connector implemented (S12b)") == 2
    assert [line for line in qualification.splitlines() if line.startswith("|")] == [
        "| Source | Use | Control |",
        "|---|---|---|",
        "| SASO catalogue | standard identity and scope | title/scope does not prove compliance; connector implemented (S12a); availability and coverage recorded per run |",
        "| SASO public technical regulations | mandatory requirement documents as published | title/scope does not prove compliance; connector implemented (S12b); availability and coverage recorded per run |",
        "| Purchased anchor standards | detailed requirement extraction | copyright and access controls |",
        "| Etimad tenders and awards | real bilingual demand specifications | exact document/page span required; connector implemented (S12b); availability and coverage recorded per run |",
        "| SABER registry | conformity evidence | registration does not prove every buyer qualification; connector implemented (S12a); availability and coverage recorded per run |",
        "| Producer catalogues / certificates | published product envelope | confirm current edition and contradiction; connector implemented (S12b); availability and coverage recorded per run |",
        "| WCO HS Nomenclature 2022 chapter texts | target-product classification identity only | B; source `wco_hs_nomenclature`; Chapters 39/72/76 COMPLETE in S14a; never capability/nameplate support |",
        "| WCO HS Nomenclature 2022 chapter texts, S15 extension | target-product classification identity only | B; Chapters 29/30/31 COMPLETE in run `20260913T033253Z`; residual `identity_exclusions` require verbatim stored addresses |",
    ]
    assert qualification.count("connector implemented (S12a)") == 2
    assert qualification.count("connector implemented (S12b)") == 3

    acquisition = core_04.split("### Acquisition snapshots 1.0.0\n", 1)[1].split(
        "### PublicSnapshot 2.1\n", 1
    )[0]
    for kind in (
        "ProductionAggregateSnapshot",
        "EstablishmentDirectorySnapshot",
        "StandardConformityRegistrySnapshot",
    ):
        assert acquisition.count(f"`{kind}`") == 1
    acquisition_note = core_04.split("§2.8 note:", 1)[1].split("\n\n", 1)[0]
    institutional_codes = {
        "DOMESTIC_PRODUCTION_AGGREGATE",
        "ESTABLISHMENT_LICENCE_DIRECTORY",
        "STANDARD_CONFORMITY_REGISTRY",
    }
    for code in institutional_codes:
        assert acquisition_note.count(f"`{code}`") == 1
    assert institutional_codes <= ACQUIRED_SUPPORT_CODES
    assert institutional_codes.isdisjoint(SUPPORT_CODES)


def test_s11_core_03_and_05_v2_markers_on_line_three() -> None:
    marker = (
        "<!-- core_version: 2.0.0; supersedes: 1.0.0; "
        "effective_date: 2026-09-02 -->"
    )
    for name in ("03_SYSTEM_ARCHITECTURE.md", "05_DATA_SOURCES_AND_INGESTION.md"):
        text = (PROJECT_ROOT / "docs" / "core" / name).read_text(encoding="utf-8")
        assert text.splitlines()[2] == marker
        assert text.count(marker) == 1


def test_authority_manifest_lists_acquisition_config() -> None:
    authority = json.loads(
        (PROJECT_ROOT / "docs" / "authority" / "authority_hashes.json").read_text(
            encoding="utf-8"
        )
    )
    paths = {item["path"] for item in authority["files"]}
    assert "config/acquisition_sources.v1.yaml" in paths


def test_build_manifests_includes_acquisition_config_and_raw_files() -> None:
    source = (PROJECT_ROOT / "scripts" / "build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert 'ROOT / "config" / "acquisition_sources.v1.yaml"' in source
    assert '"data"' in source and "raw" in source


def test_build_manifests_includes_screening_roots_and_configs() -> None:
    source = (PROJECT_ROOT / "scripts" / "build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert 'ROOT / "data" / "screening"' in source
    assert 'ROOT / "config" / "screening.v1.yaml"' in source
    assert 'ROOT / "config" / "product_families.v1.yaml"' in source


def test_s13a_core_v2_screening_contracts() -> None:
    core = {
        number: (
            PROJECT_ROOT / "docs" / "core" / name
        ).read_text(encoding="utf-8")
        for number, name in {
            "01": "01_PRODUCT_AND_REQUIREMENTS.md",
            "02": "02_METHODOLOGY_IMPLEMENTATION_MAP.md",
            "03": "03_SYSTEM_ARCHITECTURE.md",
            "04": "04_CANONICAL_DATA_MODEL.md",
            "05": "05_DATA_SOURCES_AND_INGESTION.md",
            "07": "07_DETERMINISTIC_ENGINE_SPEC.md",
            "09": "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md",
        }.items()
    }
    assert "FR-080 — Public-universe screening dispositions" in core["01"]
    assert "FR-081 — Five route-specific queues without an ordinal master list" in core["01"]
    assert "FR-082 — Hashed reconstructible ScreeningSnapshot and API" in core["01"]
    assert "FR-083 — Fail-closed universe acceptance and honest UNAVAILABLE" in core["01"]
    for function in (
        "screening.projection.project_case",
        "screening.rules.screening_ledger",
        "screening.dispositions.classify",
        "screening.queues.assign_queues",
        "screening.snapshot.build_screening_snapshot",
        "screening.repository.screening_snapshot",
        "screening.api.router",
        "screening.cli.emit_candidates",
    ):
        assert function in core["02"]
    assert "S13a screening runtime boundary" in core["03"]
    assert "ScreeningSnapshot 1.0.0" in core["04"]
    assert "W0–W3 operator-window discipline" in core["05"]
    trade_row = next(
        line
        for line in core["05"].splitlines()
        if line.startswith("| UN Comtrade / WITS |")
    )
    assert "official v1 Comtrade universe COMPLETE" in trade_row
    assert "5,443 HS6" in trade_row
    assert "corrected W-C V3 Comtrade partner detail OBSERVED for 721061" in trade_row
    assert "original WITS and Comtrade attempts retained" in trade_row
    assert "ZATCA tariff tree UNAVAILABLE" in trade_row
    assert "- full 1,300-product universe;" not in core["01"]
    assert (
        "full-universe deep resolution beyond the acquired-universe screen"
        in core["01"]
    )
    assert "S13a screening-grain execution" in core["07"]
    assert "Screening reconstruction gate" in core["09"]
    limitations = (
        PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md"
    ).read_text(encoding="utf-8")
    assert (
        "Methodology §8.2(c) greenfield candidates are NOT_CALCULABLE at "
        "screening grain because R9-S assigns no D* and route 7 requires "
        "D* > 0.65."
    ) in limitations
    assert (
        "Persistence-only CANDIDATEs are counted unqueued (135 in the current "
        "snapshot) with no invented materiality floor."
    ) in limitations
    adr = (
        PROJECT_ROOT / "docs" / "ARCHITECTURE_DECISIONS.md"
    ).read_text(encoding="utf-8")
    assert (
        "owner-approved amendments AM-1 (`d562ddca…`) and AM-2 "
        "(`88abbab2…`)"
    ) in adr


def test_missing_snapshot_kinds_cited_in_known_limitations() -> None:
    from ior_mvp.acquisition.connectors.base import default_registry
    from ior_mvp.acquisition.snapshots import KIND_STAGE, SNAPSHOT_ROOTS

    kl_text = (PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md").read_text(
        encoding="utf-8"
    )
    registry = default_registry()
    raw_root = PROJECT_ROOT / "data" / "raw"
    stage_for_kind = {kind: stage.value for kind, stage in KIND_STAGE.items()}

    for kind, rel_root in SNAPSHOT_ROOTS.items():
        snap_dir = PROJECT_ROOT / rel_root
        stage_value = stage_for_kind[kind]
        for source_id in registry.ids():
            if kind not in registry.snapshot_kinds(source_id):
                continue
            has_snapshot = False
            if snap_dir.exists():
                for snap_path in snap_dir.glob("*.json"):
                    record = json.loads(snap_path.read_text(encoding="utf-8"))
                    if record.get("source_id") == source_id:
                        has_snapshot = True
                        break
            if has_snapshot:
                continue
            source_raw = raw_root / source_id
            assert source_raw.is_dir(), f"missing raw dir for {source_id}"
            latest_marker = None
            for attempt_path in sorted(source_raw.rglob("attempt.json")):
                attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
                stage = attempt.get("coverage", {}).get("stage")
                if stage != stage_value:
                    continue
                latest_marker = attempt.get("query_hash") or str(
                    attempt_path.relative_to(PROJECT_ROOT)
                )
            if latest_marker is None:
                for cov_path in sorted(source_raw.rglob("coverage.json")):
                    cov = json.loads(cov_path.read_text(encoding="utf-8"))
                    if cov.get("stage") != stage_value:
                        continue
                    if cov.get("status") == "COMPLETE":
                        continue
                    latest_marker = cov.get("query_hash") or str(
                        cov_path.relative_to(PROJECT_ROOT)
                    )
            if latest_marker is None:
                continue
            assert latest_marker in kl_text or source_id in kl_text, (
                f"({kind}, {source_id}) missing KL citation for {latest_marker}"
            )


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
    assert (
        "Route 8 returns `NOT_CALCULABLE` with reason `GRAPH_REQUIRED` when no"
        in core["07"]
    )
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


def test_s12b_core_v2_document_contracts() -> None:
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_05 = (
        PROJECT_ROOT / "docs" / "core" / "05_DATA_SOURCES_AND_INGESTION.md"
    ).read_text(encoding="utf-8")
    assert "### DocumentRecord 1.0.0" in core_04
    assert core_04.index("### DocumentRecord 1.0.0") < core_04.index("### 2.4 Plant and ProductionLine")
    section_10 = core_05.split("## 10.", 1)[1].split("## 11.", 1)[0]
    section_11 = core_05.split("## 11.", 1)[1].split("## 12.", 1)[0]
    assert "DOCUMENT_ENVELOPE" in section_10
    assert "DocumentRecord" in section_10
    assert "acquire-documents" in section_11
    assert "--list-id" in section_11
    # OD-12 (S12B-IR3-F01): the PDF text-order disclosure is part of the DocumentRecord contract
    document_section = core_04.split("### DocumentRecord 1.0.0", 1)[1].split(
        "### 2.4 Plant and ProductionLine", 1
    )[0]
    assert "content-stream text order verbatim" in document_section
    assert "visual-order Arabic" in document_section
    assert "not logical reading order" in document_section
    assert "No bidi reordering or reshaping is applied" in document_section
    assert "PDF content-stream order" in section_10
    assert "not logical reading order" in section_10


def test_s12c_core_v2_entity_contracts() -> None:
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_05 = (
        PROJECT_ROOT / "docs" / "core" / "05_DATA_SOURCES_AND_INGESTION.md"
    ).read_text(encoding="utf-8")
    required_04 = {
        "EntityResolutionArtifact 1.0.0",
        "EntityMentionList 1.0.0",
        "ENTITY_ID_V1",
        "NAME_NORMALISATION_V1",
        "COMPANY",
        "PLANT",
        "LINE",
        "LICENCE_HOLDER",
        "DETERMINISTIC_IDENTIFIER",
        "EXACT_DOCUMENT_EVIDENCE",
        "PROPOSED_PENDING_REVIEW",
        "UNRESOLVED",
        "SITE_LOCALITY",
        "data/entities/",
        "visual",
        "never re-issued",
    }
    required_05 = {
        "ENTITY_ID_V1",
        "NAME_NORMALISATION_V1",
        "DETERMINISTIC_IDENTIFIER",
        "EXACT_DOCUMENT_EVIDENCE",
        "PROPOSED_PENDING_REVIEW",
        "UNRESOLVED",
        "data/entities/",
        "S12c",
        "config/entity_resolution.v1.yaml",
        "build-entities",
        "--mention-list-id",
    }
    assert not (required_04 - set(token for token in required_04 if token in core_04))
    assert not (required_05 - set(token for token in required_05 if token in core_05))


def test_build_manifests_includes_entity_rules_config() -> None:
    source = (PROJECT_ROOT / "scripts" / "build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert 'ROOT / "config" / "entity_resolution.v1.yaml"' in source
    assert '"entities"' in source


def test_build_manifests_includes_cases_root_and_config_history() -> None:
    source = (PROJECT_ROOT / "scripts" / "build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert 'ROOT / "data" / "cases"' in source
    assert 'ROOT / "config" / "history"' in source
    assert "retained superseded operating-configuration bytes" in source


def test_reconstruct_script_prints_case_reconstruction_pass_line(
    capsys,
) -> None:
    from scripts.reconstruct_snapshot import _reconstruct_cases

    committed, briefs = _reconstruct_cases(
        PROJECT_ROOT / "data",
        check_manifest=False,
        manifest_rows={},
    )
    assert (committed, briefs) == (9, 9)
    assert (
        "CASE RECONSTRUCTION PASS (9 snapshots, 9 briefs)"
        in capsys.readouterr().out
    )


def test_config_history_files_are_superseded_versions_only() -> None:
    history_root = PROJECT_ROOT / "config" / "history"
    paths = sorted(history_root.glob("*.yaml"))
    assert paths
    screening_hashes = {
        identity["sha256"]
        for summary_path in (
            PROJECT_ROOT / "data" / "screening" / "snapshots"
        ).glob("SCREENING-*/summary.json")
        for group in json.loads(
            summary_path.read_text(encoding="utf-8")
        )["inputs"].values()
        for identity in group
    }
    selection_family_hashes = {
        record["inputs"]["product_families"]["sha256"]
        for selection_path in (
            PROJECT_ROOT / "data" / "cases" / "selection"
        ).glob("CASE-SELECTION-*.json")
        for record in [
            json.loads(selection_path.read_text(encoding="utf-8"))
        ]
    }
    retained_authority_hashes = {
        "thresholds.v1": "4e891b9706408f6a661565e09609d0d663e1a00a17bda4e283a4b2ee63d3c47a",
        "decision_narratives.v1": "0190f136f1b4abc2360c6f1347e26984f85333149c8a9605fe1b6c1e3150b045",
    }
    for path in paths:
        match = re.fullmatch(r"(.+)-([0-9]+\.[0-9]+\.[0-9]+)\.yaml", path.name)
        assert match is not None
        live_path = PROJECT_ROOT / "config" / f"{match.group(1)}.yaml"
        assert live_path.is_file()
        retained = yaml.safe_load(path.read_text(encoding="utf-8"))
        live = yaml.safe_load(live_path.read_text(encoding="utf-8"))
        assert retained["metadata"]["version"] == match.group(2)
        assert retained["metadata"]["version"] != live["metadata"]["version"]
        recorded_hashes = set(screening_hashes)
        if match.group(1) == "product_families.v1":
            recorded_hashes.update(selection_family_hashes)
        if match.group(1) in retained_authority_hashes:
            recorded_hashes.add(retained_authority_hashes[match.group(1)])
        assert hashlib.sha256(path.read_bytes()).hexdigest() in recorded_hashes


def test_document_sources_without_records_cited_in_known_limitations() -> None:
    from ior_mvp.acquisition.connectors.base import default_registry

    kl_text = (PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md").read_text(encoding="utf-8")
    raw_root = PROJECT_ROOT / "data" / "raw"
    documents_root = PROJECT_ROOT / "data" / "documents"
    document_sources = (
        "tadawul_disclosures",
        "etimad_tenders",
        "saso_documents",
        "producer_unicoil",
        "producer_sabic",
        "producer_advanced_petrochemical",
        "producer_tasnee",
        "producer_hadeed",
        "producer_alupco",
        "producer_altaiseer_talco",
        "producer_maaden",
        "wco_hs_nomenclature",
    )
    for source_id in document_sources:
        assert (raw_root / source_id).is_dir(), f"missing raw dir for {source_id}"
        records_dir = documents_root / source_id / "records"
        if records_dir.exists() and any(records_dir.glob("*.json")):
            continue
        latest_marker = None
        for attempt_path in sorted((raw_root / source_id).rglob("attempt.json")):
            attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
            if attempt.get("coverage", {}).get("stage") != "DOCUMENT":
                continue
            latest_marker = attempt.get("query_hash") or str(
                attempt_path.relative_to(PROJECT_ROOT)
            )
        assert latest_marker is not None, f"no DOCUMENT attempt for {source_id}"
        assert latest_marker in kl_text or source_id in kl_text, (
            f"{source_id} missing KL citation for {latest_marker}"
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


def test_s13b_core_v2_surface_contracts() -> None:
    core_01 = (
        PROJECT_ROOT / "docs" / "core" / "01_PRODUCT_AND_REQUIREMENTS.md"
    ).read_text(encoding="utf-8")
    core_03 = (
        PROJECT_ROOT / "docs" / "core" / "03_SYSTEM_ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    core_07 = (
        PROJECT_ROOT / "docs" / "core" / "07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")
    ux_spec = (
        PROJECT_ROOT / "docs" / "implementation" / "UX_GENUI_DEMO_SPEC.md"
    ).read_text(encoding="utf-8")
    limitations = (PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md").read_text(
        encoding="utf-8"
    )

    for requirement_id in ("FR-084", "FR-085", "FR-086", "FR-087"):
        assert requirement_id in core_01
    assert "`GET /api/screening/evidence`" in core_03
    assert "mounted in S13b" in core_03
    assert "`NO_TRIGGER_FIRED`" in core_07
    assert (
        "yields the screening disposition `NO_CANDIDATE` with null formal state"
        in core_07
    )
    assert "TL-09 assertions 8" in core_09
    assert "56 entries" in core_09
    assert "Engine-emitted analytical narrative remains English in this release" not in ux_spec
    assert "| KL-34 |" in limitations


def test_s14a_core_v2_case_contracts() -> None:
    core_02 = (
        PROJECT_ROOT / "docs" / "core" / "02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_05 = (
        PROJECT_ROOT / "docs" / "core" / "05_DATA_SOURCES_AND_INGESTION.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join((core_02, core_04, core_05, core_09))
    for token in (
        "CaseBrief 1.1.0",
        "LATEST_REVISION_ONLY",
        "config/history/",
        "INPUTS_CHANGED",
        "SAU-H6-",
        "CASE RECONSTRUCTION PASS",
        "identity_exclusions",
        "wco_hs_nomenclature",
        "PARTNER_DETAIL_MISSING",
        "NORMALIZED_EMPTY",
        "source substitution",
    ):
        assert token in combined
    assert "CaseBrief 1.1.0" in core_04
    assert "LATEST_REVISION_ONLY" in core_04
    assert "config/history/" in core_04
    assert "INPUTS_CHANGED" in core_09
    assert "CASE RECONSTRUCTION PASS" in core_09


def test_s14b_core_04_and_07_partner_detail_sentences() -> None:
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_07 = (
        PROJECT_ROOT / "docs" / "core" / "07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")

    for token in ("PublicSnapshot 2.2.0", "2.1.0 records remain valid unchanged"):
        assert token in core_04
    section_12 = core_04.split(
        "## 12. CaseBrief 1.1.0 and derived PublicSnapshot provenance",
        maxsplit=1,
    )[1]
    exact_key_marker = (
        "Its exact-key `partner_detail` block contains exactly:\n"
    )
    assert exact_key_marker in section_12
    exact_key_block = section_12.split(
        exact_key_marker,
        maxsplit=1,
    )[1].split("\n\n", maxsplit=1)[0]
    assert re.findall(r"`([^`]+)`", exact_key_block) == [
        "state",
        "reason",
        "source_id",
        "partner_snapshot_id",
        "unit_key",
        "observed_partner_rows",
        "attempt_passport_ids",
        "observed_passport_id",
    ]
    for obsolete_name in (
        "source_snapshot_id",
        "observed_row_count",
        "calculated_passport_id",
    ):
        assert obsolete_name not in section_12
    for token in (
        "PARTNER_DETAIL_MISSING",
        "PARTNER_TRADE_OBSERVED_ZERO",
        "missing evidence is never rendered as zero",
    ):
        assert token in core_07


def test_s15a_core_v2_contracts() -> None:
    core_02 = (
        PROJECT_ROOT / "docs" / "core" / "02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_04 = (
        PROJECT_ROOT / "docs" / "core" / "04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_05 = (
        PROJECT_ROOT / "docs" / "core" / "05_DATA_SOURCES_AND_INGESTION.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT
        / "docs"
        / "core"
        / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")

    combined = "\n".join((core_02, core_04, core_05, core_09))
    for token in (
        "S14-CS-1.1",
        "SERIES_GAP_YEARS",
        "CASE SELECTION RECONSTRUCTION PASS",
        "regulatory_authority",
        "NO_PUBLIC_TENDER_FOUND",
        "identity_exclusions",
    ):
        assert token in combined
    assert "CASE-SELECTION-S15-b96de36ff0ce" in core_04
    assert "coexists_with" in core_04
    assert "scope_units" in core_04
    assert "recorded four document identities" in core_09
    assert "missing years are not zero trade" in core_09


def test_s14b_governed_docs_record_portfolio_routes_and_limits() -> None:
    core_07 = (
        PROJECT_ROOT / "docs" / "core" / "07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT / "docs" / "core" / "09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")
    slice_graph = (
        PROJECT_ROOT
        / "docs"
        / "milestones"
        / "v0.3.0"
        / "SLICE_GRAPH.md"
    ).read_text(encoding="utf-8")
    limitations = (
        PROJECT_ROOT / "docs" / "KNOWN_LIMITATIONS.md"
    ).read_text(encoding="utf-8")

    for token in (
        "SAU-H6-721061",
        "SAU-H6-721012",
        "SAU-H6-760711",
        "SAU-H6-760429",
        "SAU-H6-392010",
        "MONITOR is UNDEMONSTRATED",
    ):
        assert token in core_07
    for token in (
        "Golden C — Galvalume",
        "Golden D — Tinplate",
        "Golden E — Aluminium foil",
        "Golden F — Aluminium profiles",
        "Golden G — PE film",
        "76 entries",
        "CASE RECONSTRUCTION PASS (5 snapshots, 5 briefs)",
    ):
        assert token in core_09
    for token in (
        "SYN-MINISTRY-PE-FILM-001",
        "ADVANCE (route 3)",
        "ADVANCE (route 4)",
        "ADVANCE (route 6)",
        "ADVANCE (route 7)",
        "UNDEMONSTRATED (material R1-D trigger)",
    ):
        assert token in slice_graph
    for token in (
        "`_scaled`",
        "six decimal places",
        "KL-85 remains open",
        "S22 release-script backlog",
        "OD-15",
    ):
        assert token in limitations
def test_ci_workflow_has_graph_gates_service_job_pinned_by_digest() -> None:
    project = tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert project["project"]["optional-dependencies"]["graph"] == [
        "neo4j>=5.28,<6"
    ]
    workflow = (
        PROJECT_ROOT / ".github/workflows/ci.yml"
    ).read_text(encoding="utf-8")
    assert "graph-gates:" in workflow
    assert "name: graph / Neo4j service / Python 3.12" in workflow
    assert (
        "neo4j:5.26.30@sha256:"
        "037cf5756f0135cbfd66b739b6df7c7c4bb100f9ce11602f6f9538e17e02c74d"
    ) in workflow
    assert "7688:7687" in workflow
    assert "7475:7474" in workflow
    assert "job.services.neo4j.id" in workflow
    assert "--extra graph" in workflow
    assert "compileall -q src scripts tests graph_tests" in workflow
    assert "IMAGE_HAS_NO_NEO4J_OK" in workflow


def test_graph_gate_stops_on_failure_and_clears_only_with_confirmation() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    graph_down = makefile.split("graph-down:\n", maxsplit=1)[1].split(
        "\ngraph-unavailable-test:",
        maxsplit=1,
    )[0]
    graph_gate = makefile.split("graph-gate:\n", maxsplit=1)[1].split(
        "\ngraph-aura-load:",
        maxsplit=1,
    )[0]
    assert "docker compose down --remove-orphans" in graph_down
    assert "--volumes" not in graph_down
    assert " -v" not in graph_down
    assert "set -eu;" in graph_gate
    assert (
        "clear --target compose "
        "--confirm-clear industrial-mvp-neo4j"
    ) in graph_gate


def test_s16a_core_v2_graph_contracts() -> None:
    core_02 = (
        PROJECT_ROOT / "docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_03 = (
        PROJECT_ROOT / "docs/core/03_SYSTEM_ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    core_04 = (
        PROJECT_ROOT / "docs/core/04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT / "docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join((core_02, core_03, core_04, core_09))
    for token in (
        "Graph projection runtime",
        "CLASSIFIED_AS",
        "UNLOCKED_BY",
        "`scenario_id='PUBLIC'`",
        "GRAPH_UNAVAILABLE",
        "GRAPH RECONSTRUCTION PASS",
        "data/graph/",
        "Gate I — Graph",
    ):
        assert token in combined
    for symbol in (
        "graph.projection.build_repository_projection",
        "graph.artifact.validate_projection",
        "graph.engine_feed.adjacency_explanation",
        "graph.engine_feed.route_blocking_capability",
        "graph.engine_feed.evidence_linkage",
        "graph.loader.load",
        "graph.loader.verify",
        "graph.service.GraphService",
        "graph.api.router",
    ):
        assert symbol in core_02
    for label in (
        "Product",
        "TariffLine",
        "Specification",
        "Application",
        "Plant",
        "ProductionLine",
        "Process",
        "Equipment",
        "Capability",
        "Standard",
        "Certification",
        "Input",
        "Technology",
        "Company",
        "CustomerSegment",
        "Evidence",
        "Scenario",
        "Decision",
        "Intervention",
    ):
        assert label in core_04
    assert "v1 → v2 mapping" in core_04
    assert "TL-09 assertions 10–12" in core_09
    assert "ADR-024" in (
        PROJECT_ROOT / "docs/ARCHITECTURE_DECISIONS.md"
    ).read_text(encoding="utf-8")
    assert "KL-118" in (
        PROJECT_ROOT / "docs/KNOWN_LIMITATIONS.md"
    ).read_text(encoding="utf-8")
    assert (
        PROJECT_ROOT / "docs/implementation/GRAPH_RUNBOOK.md"
    ).is_file()


def test_build_manifests_includes_graph_root_and_graph_views_config() -> None:
    source = (PROJECT_ROOT / "scripts/build_manifests.py").read_text(
        encoding="utf-8"
    )
    assert 'ROOT / "data" / "graph"' in source
    assert 'ROOT / "config" / "graph_views.v1.yaml"' in source


def test_reconstruct_script_prints_graph_reconstruction_pass_line(
    capsys,
) -> None:
    from scripts.reconstruct_snapshot import _reconstruct_graph

    projections, nodes, edges = _reconstruct_graph(
        PROJECT_ROOT / "data",
        check_manifest=False,
        manifest_rows={},
    )
    assert projections == 1
    assert nodes > 0
    assert edges > 0
    assert "GRAPH RECONSTRUCTION PASS (1 projections," in capsys.readouterr().out


def test_s15b_core_and_control_contracts_are_present() -> None:
    core_01 = (
        PROJECT_ROOT / "docs/core/01_PRODUCT_AND_REQUIREMENTS.md"
    ).read_text(encoding="utf-8")
    core_02 = (
        PROJECT_ROOT / "docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md"
    ).read_text(encoding="utf-8")
    core_03 = (
        PROJECT_ROOT / "docs/core/03_SYSTEM_ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    core_04 = (
        PROJECT_ROOT / "docs/core/04_CANONICAL_DATA_MODEL.md"
    ).read_text(encoding="utf-8")
    core_07 = (
        PROJECT_ROOT / "docs/core/07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")
    core_09 = (
        PROJECT_ROOT / "docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join(
        (core_01, core_02, core_03, core_04, core_07, core_09)
    )

    for token in (
        "GET /api/case-selection",
        "CASE_SELECTION_INTEGRITY_ERROR",
        "CASE-SELECTION-S15-b96de36ff0ce",
        "SYN-MINISTRY-PENICILLIN-API-001",
        "SYN-MINISTRY-STREPTOMYCIN-API-001",
        "SYN-MINISTRY-SOP-001",
        "SYN-MINISTRY-FERT-RETAIL-PACKS-001",
        "evsi: null",
        "SERIES_GAP_YEARS",
        "eleven cases",
    ):
        assert token in combined
    assert "ADR-025" in (
        PROJECT_ROOT / "docs/ARCHITECTURE_DECISIONS.md"
    ).read_text(encoding="utf-8")
    limitations = (
        PROJECT_ROOT / "docs/KNOWN_LIMITATIONS.md"
    ).read_text(encoding="utf-8")
    assert "KL-124" in limitations
    assert "KL-125" in limitations
