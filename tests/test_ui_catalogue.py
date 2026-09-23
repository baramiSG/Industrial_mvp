from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from string import Formatter

import pytest
import yaml
from fastapi.testclient import TestClient

import ior_mvp.config as config
from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT


CATALOGUE_PATH = PROJECT_ROOT / "config" / "ui_strings.v1.yaml"
CHECKER = PROJECT_ROOT / "scripts" / "check_ui_contracts.py"
EXPECTED_ARABIC_LABEL = "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"
NEED_SLUGS = {
    "identity/tariff-line": "identity_tariff_line",
    "target specification/application": "target_specification_application",
    "line-level production or producer-grade matrix": (
        "line_level_production_or_producer_grade_matrix"
    ),
    "re-export/origin decomposition": "re_export_origin_decomposition",
    "capacity/availability/allocation": "capacity_availability_allocation",
}
QUEUE_REASON_CODES = {
    "MULTIPLE_MATERIAL_SIGNALS",
    "R9S_AND_OTHER_MATERIAL_TRIGGER",
    "SUPPLIER_CONCENTRATION_SIGNAL",
    "SCREENING_WARNING",
    "R2_FULL_FIRED",
    "EVSI_NOT_CALCULABLE",
    "PERSISTENCE_ONLY",
}
EXCLUSION_CODES = {
    "EX-01_HETEROGENEOUS_RESIDUAL",
    "EX-02_MARKET_BELOW_MES",
    "EX-03_UNSATISFIABLE_HARD_GATE",
    "EX-04_IDLE_EQUIVALENT_CAPACITY",
    "EX-05_TRANSITORY_OR_MEASUREMENT",
    "EX-06_REDUNDANCY_OR_CROWD_OUT",
}
SCREENING_RESULT_CODES = {
    "R0_DISABLED_NA",
    "R0_FULL_FIRED",
    "R0_DEGRADED_FIRED",
    "R1_F_DISABLED_NA",
    "R1_F_FULL_NOT_FIRED",
    "R1_D_DEGRADED_FIRED",
    "R1_D_DEGRADED_NOT_FIRED",
    "R2_DISABLED_NA",
    "R2_FULL_FIRED",
    "R2_FULL_NOT_FIRED",
    "R3_DISABLED_NA",
    "R3_FULL_FIRED",
    "R3_FULL_NOT_FIRED",
    "R4_D_DISABLED_NA",
    "R4_D_DEGRADED_FIRED",
    "R5_DISABLED_NA",
    "R5_FULL_FIRED",
    "R5_FULL_NOT_FIRED",
    "R5_DEGRADED_FIRED",
    "R5_DEGRADED_NOT_FIRED",
    "R9_S_DISABLED_NA",
    "R9_S_FULL_FIRED",
    "R9_S_FULL_NOT_FIRED",
    "R10_DISABLED_NA",
    "R10_FULL_FIRED",
    "R10_DEGRADED_FIRED",
    "R11_FULL_FIRED",
    "R11_FULL_NOT_FIRED",
    "R11_DEGRADED_NOT_FIRED",
}
SCREENING_EFFECT_CODES = {
    "R0_EFFECT",
    "R1_F_EFFECT",
    "R1_D_EFFECT",
    "R2_EFFECT",
    "R3_EFFECT",
    "R4_D_EFFECT",
    "R5_EFFECT",
    "R9_S_EFFECT",
    "R10_EFFECT",
    "R11_EFFECT",
}
SCREENING_CHROME_KEYS = {
    "nav.screening",
    "screening.eyebrow",
    "screening.title",
    "screening.subtitle",
    "screening.boundary_public_only",
    "screening.summary.title",
    "screening.universe.title",
    "screening.universe.status",
    "screening.universe.reasons",
    "screening.universe.hs6_count",
    "screening.universe.years",
    "screening.universe.flows",
    "screening.universe.units",
    "screening.universe.unavailable_body",
    "screening.universe.partial_body",
    "screening.coverage.title",
    "screening.coverage.tariff_tree",
    "screening.coverage.partner_detail",
    "screening.coverage.partner_detail_counts",
    "screening.coverage.production_aggregates",
    "screening.coverage.entity_artifact",
    "screening.counts.title",
    "screening.counts.dispositions",
    "screening.counts.indications",
    "screening.counts.unqueued",
    "screening.counts.unqueued_note",
    "screening.mapping.title",
    "screening.mapping.note",
    "screening.queues.title",
    "screening.queues.subtitle",
    "screening.queue.count",
    "screening.queue.ordering_basis",
    "screening.queue.methodology_ref",
    "screening.queue.open",
    "screening.queue.back_to_summary",
    "screening.queue.empty",
    "screening.queue.empty_body",
    "screening.queue.pareto_rank",
    "screening.queue.pareto_note",
    "screening.queue.hs6",
    "screening.queue.disposition",
    "screening.queue.indicated_state",
    "screening.queue.reasons",
    "screening.queue.metrics",
    "screening.queue.open_record",
    "screening.queue.showing",
    "screening.queue.previous",
    "screening.queue.next",
    "screening.record.title",
    "screening.record.back_to_queue",
    "screening.record.disposition",
    "screening.record.disposition_reason",
    "screening.record.indicated_state",
    "screening.record.indication_reason",
    "screening.record.no_indication",
    "screening.record.ledger",
    "screening.record.not_evaluated",
    "screening.record.exclusions",
    "screening.record.exclusion",
    "screening.record.exclusion_status",
    "screening.record.exclusion_reason",
    "screening.record.evidence_ids",
    "screening.record.no_evidence_ids",
    "screening.record.warnings",
    "screening.record.ratio_warning",
    "screening.record.ratio_value",
    "screening.record.price_led_growth",
    "screening.record.continuity",
    "screening.record.needs",
    "screening.record.adjacency",
    "screening.record.same_process_family",
    "screening.record.qualifying_signals",
    "screening.record.known_gate_failure",
    "screening.record.metrics",
    "screening.record.evidence_basis_title",
    "screening.record.evidence_basis_intro",
    "screening.record.no_record_passports",
    "screening.record.record_passports",
    "screening.loading",
    "screening.error",
    "screening.evidence.title",
    "screening.evidence.intro",
    "screening.evidence.passport_id",
    "screening.evidence.passport_source",
    "screening.evidence.passport_stage",
    "screening.evidence.passport_unit",
    "screening.evidence.passport_class",
    "screening.evidence.passport_status",
    "screening.evidence.passport_coverage",
    "screening.evidence.passport_endpoint",
    "screening.evidence.passport_retrieved",
    "screening.evidence.passport_reference",
    "screening.evidence.completeness_basis",
    "screening.evidence.query_hash",
    "screening.evidence.selected_run",
    "screening.evidence.superseded_runs",
    "screening.evidence.no_superseded_runs",
    "screening.evidence.passport_detail_not_exposed",
    "screening.evidence.no_snapshot",
    "screening.evidence.unit_without_passport",
    "screening.flow.imports",
    "screening.flow.exports",
    "common.yes",
    "common.no",
}


def _catalogue() -> dict:
    payload = yaml.safe_load(CATALOGUE_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _placeholders(value: str) -> set[str]:
    return {
        field
        for _, field, _, _ in Formatter().parse(value)
        if field is not None
    }


def test_ui_catalogue_metadata_locales_and_version_are_exact() -> None:
    payload = _catalogue()

    assert payload["metadata"] == {
        "artifact": "industrial-opportunity-ui-strings",
        "version": "1.5.0",
        "effective_date": "2026-09-16",
        "authority": (
            "Core 01 NFR-006/NFR-007 and UX GenUI Demo Specification"
        ),
        "status": "frozen_for_demo_cycle",
        "default_locale": "en",
    }
    assert payload["locales"] == {
        "en": {"bcp47": "en-US", "direction": "ltr"},
        "ar": {"bcp47": "ar-SA", "direction": "rtl"},
    }
    assert getattr(config, "SUPPORTED_UI_LOCALES", None) == ("en", "ar")


def test_ui_catalogue_has_exact_s08_contradiction_copy() -> None:
    strings = _catalogue()["strings"]

    assert {
        key: strings["en"][key]
        for key in (
            "dossier.contradiction_register",
            "dossier.public_contradictions",
            "dossier.synthetic_contradictions",
            "dossier.no_public_contradictions",
            "dossier.synthetic_not_applicable",
            "dossier.no_synthetic_contradictions",
        )
    } == {
        "dossier.contradiction_register": "Contradiction register",
        "dossier.public_contradictions": (
            "Public evidence contradictions"
        ),
        "dossier.synthetic_contradictions": (
            "Synthetic evidence contradictions"
        ),
        "dossier.no_public_contradictions": (
            "No public contradictions recorded."
        ),
        "dossier.synthetic_not_applicable": (
            "Synthetic evidence is not active in public mode."
        ),
        "dossier.no_synthetic_contradictions": (
            "No synthetic contradictions are recorded for this simulation."
        ),
    }
    assert {
        key: strings["ar"][key]
        for key in (
            "dossier.contradiction_register",
            "dossier.public_contradictions",
            "dossier.synthetic_contradictions",
            "dossier.no_public_contradictions",
            "dossier.synthetic_not_applicable",
            "dossier.no_synthetic_contradictions",
        )
    } == {
        "dossier.contradiction_register": "سجل التناقضات",
        "dossier.public_contradictions": "تناقضات الأدلة العامة",
        "dossier.synthetic_contradictions": (
            "تناقضات الأدلة الاصطناعية"
        ),
        "dossier.no_public_contradictions": (
            "لا توجد تناقضات مسجلة في الأدلة العامة."
        ),
        "dossier.synthetic_not_applicable": (
            "الأدلة الاصطناعية غير نشطة في وضع الأدلة العامة."
        ),
        "dossier.no_synthetic_contradictions": (
            "لا توجد تناقضات اصطناعية مسجلة لهذه المحاكاة."
        ),
    }


def test_ui_catalogue_locale_keys_and_placeholders_match() -> None:
    strings = _catalogue()["strings"]

    assert set(strings) == {"en", "ar"}
    assert set(strings["en"]) == set(strings["ar"])
    assert len(strings["en"]) >= 120
    for key in strings["en"]:
        assert re.fullmatch(
            r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$",
            key,
        )
        assert _placeholders(strings["en"][key]) == _placeholders(
            strings["ar"][key]
        )


def test_decision_object_status_preserves_english_pixels_and_localizes_arabic(
) -> None:
    strings = _catalogue()["strings"]
    assert {
        key: strings["en"][key]
        for key in (
            "decision_object.generic_hs6_only",
            "decision_object.partially_resolved",
            "decision_object.resolved",
        )
    } == {
        "decision_object.generic_hs6_only": "generic hs6 only",
        "decision_object.partially_resolved": "partially resolved",
        "decision_object.resolved": "resolved",
    }
    assert strings["ar"]["decision_object.generic_hs6_only"] == (
        "رمز النظام المنسق العام فقط"
    )


def test_partner_detail_metric_and_dossier_keys_exist_in_both_locales_and_are_used(
) -> None:
    strings = _catalogue()["strings"]
    expected = {
        "metric.hhi_partner_detail_missing": (
            "Partner detail missing ({reason}) — missing evidence, not "
            "zero trade"
        ),
        "metric.hhi_partner_trade_zero": (
            "Partner trade observed zero — no partner rows"
        ),
        "dossier.partner_detail": "Partner detail (2024 imports)",
        "dossier.partner_detail_observed": (
            "Observed from {source} — {rows} partner rows"
        ),
        "dossier.partner_detail_missing": (
            "MISSING ({reason}) — missing evidence, not zero trade; "
            "attempts: {attempts}"
        ),
        "dossier.partner_detail_zero": (
            "Observed ZERO from {source} — zero partner rows"
        ),
    }
    source = "\n".join(
        (
            (
                PROJECT_ROOT
                / "src/ior_mvp/static/modules/renderers/decision.js"
            ).read_text(encoding="utf-8"),
            (
                PROJECT_ROOT / "src/ior_mvp/dossier.py"
            ).read_text(encoding="utf-8"),
        )
    )

    for key, value in expected.items():
        assert strings["en"][key] == value
        assert re.search(r"[\u0600-\u06ff]", strings["ar"][key]), key
        assert _placeholders(strings["en"][key]) == _placeholders(
            strings["ar"][key]
        )
        assert key in source


def test_ui_catalogue_values_are_nonempty_nfc_strings() -> None:
    for locale, strings in _catalogue()["strings"].items():
        for key, value in strings.items():
            assert isinstance(value, str), (locale, key)
            assert value.strip() == value and value, (locale, key)
            assert unicodedata.normalize("NFC", value) == value


def _required_screening_keys() -> tuple[set[str], set[str]]:
    screening = yaml.safe_load(
        (
            PROJECT_ROOT / "config" / "screening.v1.yaml"
        ).read_text(encoding="utf-8")
    )
    vocab = screening["vocabularies"]
    queue_ids = set(screening["queues"])
    codes = (
        set(vocab["dispositions"])
        | set(vocab["reason_codes"])
        | {"NO_SCREENING_SNAPSHOT"}
        | queue_ids
        | QUEUE_REASON_CODES
        | EXCLUSION_CODES
        | {"SATISFIED", "NOT_SATISFIED", "NOT_CALCULABLE"}
        | {
            "EXCLUSION_SATISFIED",
            "EXCLUSION_NOT_SATISFIED",
            "EXCLUSION_INPUT_UNAVAILABLE",
        }
        | {"CONTINUOUS", "GAP_YEARS", "REVISION_CHANGE_IN_WINDOW"}
        | {
            "NONE",
            "GAP_YEARS",
            "ABSENT_BEFORE_REVISION_CHANGE",
            "ABSENT_AFTER_REVISION_CHANGE",
        }
        | {
            "AVAILABLE",
            "PARTIAL",
            "UNAVAILABLE",
            "NOT_CALCULABLE",
            "CALCULATED",
            "COMPLETE",
        }
        | SCREENING_RESULT_CODES
        | SCREENING_EFFECT_CODES
        | {
            "R0",
            "R1-F",
            "R1-D",
            "R2",
            "R3",
            "R4-D",
            "R5",
            "R9-S",
            "R10",
            "R11",
        }
        | {
            "imports_usd_m_latest",
            "quantity_cagr",
            "export_import_value_ratio",
            "largest_supplier_share_value",
            "qualifying_signal_count",
            "fired_signal_count",
            "hhi_value",
            "delta_ln_value",
        }
    )
    required = set(SCREENING_CHROME_KEYS)
    required |= {
        f"disposition.{code.lower()}"
        for code in vocab["dispositions"]
    }
    required |= {
        f"reason.{code.lower()}"
        for code in [*vocab["reason_codes"], "NO_SCREENING_SNAPSHOT"]
    }
    required |= {f"queue.{code}" for code in queue_ids}
    required |= {
        f"queue_reason.{code.lower()}"
        for code in QUEUE_REASON_CODES
    }
    required |= {
        f"need.{NEED_SLUGS[code]}"
        for code in vocab["evidence_need_codes"]
    }
    required |= {
        f"exclusion.{code.lower()}"
        for code in EXCLUSION_CODES
    }
    required |= {
        f"exclusion_status.{code.lower()}"
        for code in ("SATISFIED", "NOT_SATISFIED", "NOT_CALCULABLE")
    }
    required |= {
        f"exclusion_reason.{code.lower()}"
        for code in (
            "EXCLUSION_SATISFIED",
            "EXCLUSION_NOT_SATISFIED",
            "EXCLUSION_INPUT_UNAVAILABLE",
        )
    }
    required |= {
        f"continuity_status.{code.lower()}"
        for code in ("CONTINUOUS", "GAP_YEARS", "REVISION_CHANGE_IN_WINDOW")
    }
    required |= {
        f"continuity_pattern.{code.lower()}"
        for code in (
            "NONE",
            "GAP_YEARS",
            "ABSENT_BEFORE_REVISION_CHANGE",
            "ABSENT_AFTER_REVISION_CHANGE",
        )
    }
    required |= {
        f"screening.status.{code.lower()}"
        for code in (
            "AVAILABLE",
            "PARTIAL",
            "UNAVAILABLE",
            "NOT_CALCULABLE",
            "CALCULATED",
            "COMPLETE",
        )
    }
    required |= {
        f"screening.metric.{code}"
        for code in (
            "imports_usd_m_latest",
            "quantity_cagr",
            "export_import_value_ratio",
            "largest_supplier_share_value",
            "qualifying_signal_count",
            "fired_signal_count",
            "hhi_value",
            "delta_ln_value",
        )
    }
    required |= {
        f"screening.rule.{code.lower().replace('-', '_')}"
        for code in (
            "R0",
            "R1-F",
            "R1-D",
            "R2",
            "R3",
            "R4-D",
            "R5",
            "R9-S",
            "R10",
            "R11",
        )
    }
    required |= {
        f"screening.result.{code.lower()}"
        for code in SCREENING_RESULT_CODES
    }
    required |= {
        f"screening.effect.{code.lower()}"
        for code in SCREENING_EFFECT_CODES
    }
    required.add(
        "screening.not_evaluated_reason.inputs_not_public_at_screening_grain"
    )
    return required, codes


def test_ui_catalogue_covers_every_screening_vocabulary_code() -> None:
    required, _ = _required_screening_keys()
    strings = _catalogue()["strings"]

    assert required <= set(strings["en"])
    assert required <= set(strings["ar"])


def test_screening_labels_are_arabic_and_never_equal_a_code() -> None:
    required, codes = _required_screening_keys()
    strings = _catalogue()["strings"]

    for key in required:
        assert re.search(r"[\u0600-\u06ff]", strings["ar"][key]), key
        assert strings["en"][key] not in codes, key
        assert strings["ar"][key] not in codes, key
    assert (
        strings["en"]["reason.no_screening_snapshot"]
        != "NO_SCREENING_SNAPSHOT"
    )


def test_ui_catalogue_excludes_policy_synthetic_labels() -> None:
    payload = _catalogue()
    policy = yaml.safe_load(
        (
            PROJECT_ROOT / "config" / "evidence_policy.v1.yaml"
        ).read_text(encoding="utf-8")
    )["synthetic_isolation"]
    values = {
        value
        for strings in payload["strings"].values()
        for value in strings.values()
    }

    assert not any(
        key.startswith("synthetic.")
        for strings in payload["strings"].values()
        for key in strings
    )
    assert policy["display_label"] not in values
    assert policy["display_label_ar"] not in values
    assert policy["display_label_ar"] == EXPECTED_ARABIC_LABEL


def test_every_ui_string_usage_resolves_without_unused_keys() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--check-catalogue-usage"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "catalogue usage exact" in result.stdout


def test_visible_ui_copy_is_not_hard_coded_outside_catalogue() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--check-copy"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "visible copy catalogue-sourced" in result.stdout


@pytest.mark.parametrize("locale", ["en", "ar"])
def test_ui_strings_endpoint_returns_valid_en_and_ar_bundles(
    locale: str,
) -> None:
    response = TestClient(app).get(f"/api/ui-strings/{locale}")

    assert response.status_code == 200
    payload = response.json()
    catalogue = _catalogue()
    assert payload == {
        "catalogue_version": "1.5.0",
        "locale": locale,
        **catalogue["locales"][locale],
        "strings": catalogue["strings"][locale],
        "synthetic_labels": {
            "en": yaml.safe_load(
                (
                    PROJECT_ROOT / "config" / "evidence_policy.v1.yaml"
                ).read_text(encoding="utf-8")
            )["synthetic_isolation"]["display_label"],
            "ar": EXPECTED_ARABIC_LABEL,
        },
    }


def test_unknown_ui_strings_locale_returns_404() -> None:
    response = TestClient(app).get("/api/ui-strings/fr")

    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "UI_LOCALE_NOT_FOUND",
            "locale": "fr",
        }
    }


def test_malformed_ui_catalogue_fails_closed_without_partial_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    malformed = tmp_path / "ui_strings.v1.yaml"
    payload = _catalogue()
    del payload["strings"]["ar"]["nav.overview"]
    malformed.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    monkeypatch.setattr(config, "UI_STRINGS_PATH", malformed)
    config.clear_config_caches()
    try:
        response = TestClient(
            app,
            raise_server_exceptions=False,
        ).get("/api/ui-strings/ar")
    finally:
        config.clear_config_caches()

    assert response.status_code == 500
    assert response.json() == {
        "detail": {"code": "UI_CATALOGUE_INTEGRITY_ERROR"}
    }
    assert "strings" not in json.dumps(response.json())
