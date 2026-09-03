from __future__ import annotations

import json
import re
import ast
import unicodedata
from copy import deepcopy
from pathlib import Path
from string import Formatter

import pytest
import yaml

import ior_mvp.config as config_module
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import get_synthetic_scenario
from ior_mvp.data_repository import get_public_case
from ior_mvp.evidence_needs import (
    NEED_CODE_ORDER,
    derive_evidence_needs,
)
from ior_mvp.rules import evaluate_rules
from ior_mvp.narratives import (
    NarrativeCatalogueError,
    NarrativeValue,
    render_catalogue_entry,
    validate_decision_narratives,
)


CATALOGUE_PATH = (
    PROJECT_ROOT / "config" / "decision_narratives.v1.yaml"
)


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


def test_decision_catalogue_metadata_and_locale_contract_are_exact() -> None:
    payload = _catalogue()

    assert payload["metadata"] == {
        "artifact": "industrial-opportunity-decision-narratives",
        "version": "1.0.0",
        "effective_date": "2026-09-02",
        "authority": (
            "Industrial Opportunity Resolution Methodology §§1.2, 4.2, "
            "5.3, 7.1.1, 7.4, 9, 12 and 15; Core 07 v2"
        ),
        "status": "frozen_for_demo_cycle",
        "default_locale": "en",
    }
    assert payload["locales"] == {
        "en": {"bcp47": "en-US", "direction": "ltr"},
        "ar": {"bcp47": "ar-SA", "direction": "rtl"},
    }
    assert payload["placeholder_kinds"] == {
        "route_code": "computed",
        "trigger": "localized",
        "product_name": "localized",
        "route_label": "localized",
        "route_short_label": "localized",
    }


def test_decision_catalogue_has_exact_key_and_placeholder_parity() -> None:
    templates = _catalogue()["templates"]

    assert set(templates) == {"en", "ar"}
    assert set(templates["en"]) == set(templates["ar"])
    for locale, values in templates.items():
        for key, value in values.items():
            assert re.fullmatch(
                r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$",
                key,
            ), (locale, key)
            assert isinstance(value, str) and value.strip() == value
            assert unicodedata.normalize("NFC", value) == value
    for key in templates["en"]:
        assert _placeholders(templates["en"][key]) == _placeholders(
            templates["ar"][key]
        )


def test_catalogue_has_generic_needs_routes_and_no_case_specific_keys() -> None:
    keys = set(_catalogue()["templates"]["en"])
    expected_needs = {
        "need.identity.tariff_line",
        "need.specification.line_production",
        "need.specification.producer_grade_matrix",
        "need.capacity.availability_allocation",
        "need.demand.importer_specification",
        "need.demand.importer_application_qualification",
        "need.flows.reexport_origin_decomposition",
        "need.economics.route_delivered_cost",
        "need.economics.named_exception_delivered_cost",
    }

    assert expected_needs <= keys
    assert "route.hypothesis.priority" in keys
    assert {
        f"route.{route_code}.{suffix}"
        for route_code in range(9)
        for suffix in ("short", "label")
    } <= keys
    assert not any(
        fragment in key
        for key in keys
        for fragment in (
            "missing.steel",
            "missing.generic",
            "route5_advance",
            "route0_reject",
        )
    )
    assert {
        key
        for key in keys
        if key.startswith("decision.simulated.")
    } == {
        "decision.simulated.investigate.headline",
        "decision.simulated.investigate.route",
        "decision.simulated.investigate.rationale",
    }


def test_generic_simulated_investigate_wrapper_matches_both_scenarios() -> None:
    templates = _catalogue()["templates"]["en"]
    expected = {
        "headline": templates[
            "decision.simulated.investigate.headline"
        ],
        "route_label": templates[
            "decision.simulated.investigate.route"
        ],
        "rationale": templates[
            "decision.simulated.investigate.rationale"
        ],
    }
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        scenario = get_synthetic_scenario(opportunity_id)
        assert scenario is not None
        actual = scenario["decision_narrative"]["INVESTIGATE"]
        assert {
            key: actual[key] for key in expected
        } == expected


def test_route_priority_uses_governed_localized_short_label() -> None:
    brownfield = {
        locale: render_catalogue_entry(
            "route.hypothesis.priority",
            locale,
            {
                "route_short_label": NarrativeValue.localized(
                    render_catalogue_entry(
                        "route.5.short",
                        locale,
                    )["text"]
                )
            },
        )["text"]
        for locale in ("en", "ar")
    }
    certification = render_catalogue_entry(
        "route.hypothesis.priority",
        "en",
        {
            "route_short_label": NarrativeValue.localized(
                render_catalogue_entry(
                    "route.3.short",
                    "en",
                )["text"]
            )
        },
    )

    assert brownfield == {
        "en": "Brownfield priority to test",
        "ar": "أولوية اختبار المسار القائم",
    }
    assert certification["text"] == (
        "Certification support priority to test"
    )


def test_rendered_segments_mark_only_computed_values_for_ltr_isolation() -> None:
    advance = render_catalogue_entry(
        "decision.public.advance.headline",
        "ar",
        {"route_code": NarrativeValue.computed("<script>7</script>")},
    )
    product = render_catalogue_entry(
        "decision.public.reject_generic.rationale",
        "ar",
        {"product_name": NarrativeValue.localized("منتج اختباري")},
    )

    assert advance["text"] == "تقدّم — المسار <script>7</script>"
    assert advance["segments"] == [
        {"kind": "literal", "text": "تقدّم — المسار "},
        {
            "kind": "computed",
            "text": "<script>7</script>",
            "ltr_isolate": True,
        },
    ]
    assert product["segments"][1] == {
        "kind": "localized",
        "text": "منتج اختباري",
        "ltr_isolate": False,
    }


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["templates"]["ar"].pop(
            "decision.public.advance.headline"
        ),
        lambda value: value["templates"]["ar"].__setitem__(
            "decision.public.advance.headline",
            "تقدّم",
        ),
        lambda value: value["metadata"].__setitem__("version", "1.0.1"),
        lambda value: value["templates"]["en"].__setitem__(
            "bad key",
            "bad",
        ),
        lambda value: (
            value["templates"]["en"].__setitem__(
                "gap.evidence",
                "SIMULATED — NOT MINISTRY EVIDENCE",
            ),
            value["templates"]["ar"].__setitem__(
                "gap.evidence",
                "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة",
            ),
        ),
    ],
)
def test_malformed_decision_catalogue_fails_closed(mutation) -> None:
    payload = deepcopy(_catalogue())
    mutation(payload)

    with pytest.raises(NarrativeCatalogueError):
        validate_decision_narratives(payload)


def test_decision_catalogue_cache_clears_with_other_configuration() -> None:
    first = config_module.decision_narratives_config()

    config_module.clear_config_caches()

    assert config_module.decision_narratives_config() is not first
    assert Path(config_module.DECISION_NARRATIVES_PATH) == CATALOGUE_PATH


@pytest.mark.parametrize(
    ("opportunity_id", "rules", "expected_keys"),
    [
        (
            "SAU-H0-721049",
            [
                {"rule_id": "R9-S", "fired": True},
                {"rule_id": "R11", "fired": False},
            ],
            [
                "need.specification.line_production",
                "need.capacity.availability_allocation",
                "need.demand.importer_specification",
                "need.flows.reexport_origin_decomposition",
                "need.economics.route_delivered_cost",
            ],
        ),
        (
            "SAU-H0-390210",
            [
                {"rule_id": "R9-S", "fired": True},
                {"rule_id": "R11", "fired": True},
            ],
            [
                "need.identity.tariff_line",
                "need.demand.importer_application_qualification",
                "need.specification.producer_grade_matrix",
                "need.capacity.availability_allocation",
                "need.economics.named_exception_delivered_cost",
            ],
        ),
    ],
)
def test_goldens_emit_five_predicate_selected_substantive_needs(
    opportunity_id: str,
    rules: list[dict],
    expected_keys: list[str],
) -> None:
    needs = derive_evidence_needs(
        get_public_case(opportunity_id),
        rules,
    )

    assert [need["template_key"] for need in needs] == expected_keys
    assert len(needs) == 5
    assert len({need["need_code"] for need in needs}) == 5
    assert all(need["numeric_evsi"] == "NOT_CALCULABLE" for need in needs)
    assert all(need["route_effect"] for need in needs)
    assert all(
        need["text"] == need["localized_text"]["en"]
        and need["localized_text"]["ar"]
        for need in needs
    )
    assert all(
        need["need_code"] in NEED_CODE_ORDER for need in needs
    )


def test_route_economics_need_uses_governed_localized_route_label() -> None:
    needs = derive_evidence_needs(
        get_public_case("SAU-H0-721049"),
        [
            {"rule_id": "R9-S", "fired": True},
            {"rule_id": "R11", "fired": False},
        ],
    )
    route_need = next(
        need
        for need in needs
        if need["template_key"]
        == "need.economics.route_delivered_cost"
    )

    assert route_need["text"] == (
        "Delivered cost, import parity and unsupported Brownfield economics"
    )
    assert "المسار القائم" in route_need["localized_text"]["ar"]


def test_need_selector_ast_contains_no_case_name_id_or_profile_dispatch() -> None:
    path = PROJECT_ROOT / "src" / "ior_mvp" / "evidence_needs.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "derive_evidence_needs"
    )
    tokens = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name)
    } | {
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    assert not {
        "opportunity_id",
        "scenario_id",
        "sector_profile",
        "commercial_name_en",
        "commercial_name_ar",
        "producer",
        "SAU-H0-721049",
        "SAU-H0-390210",
    } & tokens


CORRECTION_ROUND_KEYS = {
    "decision.public.reject_uneconomic.headline": (
        "REJECT — uneconomic at efficient scale",
        "رفض — غير اقتصادي عند الحد الأدنى للكفاءة",
    ),
    "decision.public.reject_uneconomic.rationale": (
        "No technically feasible route passes downside economics at minimum efficient scale; capacity support is not justified.",
        "لا يجتاز أي مسار مجدٍ تقنياً الاقتصاديات في السيناريو المتحفظ عند الحد الأدنى للكفاءة؛ ولذلك لا يُبرر دعم الطاقة الإنتاجية.",
    ),
    "decision.public.reject_uneconomic.condition": (
        "Reopen only with new downside economics that pass the hurdle rate for a technically feasible route.",
        "لا تُفتح الحالة مجدداً إلا باقتصاديات جديدة للسيناريو المتحفظ تجتاز معدل العائد المطلوب لمسار مجدٍ تقنياً.",
    ),
    "decision.public.reject_uneconomic.kill": (
        "Stop capacity support while every feasible route fails downside economics.",
        "أوقف دعم الطاقة الإنتاجية ما دام كل مسار مجدٍ يفشل في اقتصاديات السيناريو المتحفظ.",
    ),
    "decision.public.reject_false_gap.headline": (
        "REJECT — false or measurement gap",
        "رفض — فجوة زائفة أو ناتجة عن القياس",
    ),
    "decision.public.reject_false_gap.rationale": (
        "The apparent import gap is a false or measurement gap; it does not evidence unmet domestic demand.",
        "الفجوة الظاهرة في الواردات فجوة زائفة أو ناتجة عن القياس، ولا تثبت وجود طلب محلي غير ملبّى.",
    ),
    "decision.public.reject_false_gap.condition": (
        "Reopen only if retained-flow evidence shows a real specification-adjusted gap.",
        "لا تُفتح الحالة مجدداً إلا إذا أثبتت أدلة التدفقات المحتجزة فجوة حقيقية معدلة بالمواصفة.",
    ),
    "decision.public.reject_false_gap.kill": (
        "Stop the proposition while the gap remains false or unmeasured.",
        "أوقف المقترح ما دامت الفجوة زائفة أو غير مقاسة.",
    ),
    "decision.public.reject_overcapacity.headline": (
        "REJECT — structural overcapacity",
        "رفض — طاقة فائضة بنيوية",
    ),
    "decision.public.reject_overcapacity.rationale": (
        "The intervention would add unacceptable redundant capacity or crowd out a more efficient incumbent; it is not additional.",
        "سيضيف التدخل طاقة فائضة غير مقبولة أو يزاحم منتجاً قائماً أكثر كفاءة؛ ولذلك لا يحقق إضافية.",
    ),
    "decision.public.reject_overcapacity.condition": (
        "Reopen only if competition evidence shows the added capacity is absorbed without crowding out an efficient incumbent.",
        "لا تُفتح الحالة مجدداً إلا إذا أثبتت أدلة المنافسة أن الطاقة المضافة تُستوعب دون مزاحمة منتج قائم كفء.",
    ),
    "decision.public.reject_overcapacity.kill": (
        "Stop capacity support while structural overcapacity remains evidenced.",
        "أوقف دعم الطاقة الإنتاجية ما دامت الطاقة الفائضة البنيوية مثبتة.",
    ),
    "decision.public.investigate.route.unresolved": (
        "Route not yet determined",
        "لم يُحدد المسار بعد",
    ),
    "decision.public.investigate.rationale.preferred": (
        "Preferred hypothesis: {route_short_label}; resolve the named evidence before any support decision.",
        "الفرضية المفضلة: {route_short_label}؛ احسم الأدلة المسماة قبل أي قرار دعم.",
    ),
    "decision.public.investigate.rationale.route_unresolved": (
        "No route hypothesis can be preferred from public evidence; resolve the named route evidence before any support decision.",
        "لا يمكن ترجيح أي فرضية مسار من الأدلة العامة؛ احسم أدلة المسار المسماة قبل أي قرار دعم.",
    ),
    "need.route.evidence_required": (
        "Route feasibility, additionality, policy and downside economics evidence for the candidate routes",
        "أدلة جدوى المسارات المرشحة وإضافيتها وجوازها من حيث السياسات واقتصادياتها في السيناريو المتحفظ",
    ),
}


def test_correction_round_keys_have_exact_english_and_arabic_literals() -> None:
    templates = _catalogue()["templates"]
    for key, (en_text, ar_text) in CORRECTION_ROUND_KEYS.items():
        assert templates["en"][key] == en_text, key
        assert templates["ar"][key] == ar_text, key


def test_catalogue_has_110_keys_with_parity_and_validator_pass() -> None:
    payload = _catalogue()
    en = payload["templates"]["en"]
    ar = payload["templates"]["ar"]
    assert len(en) == len(ar) == 110
    assert set(en) == set(ar)
    validate_decision_narratives(payload)


def test_preferred_rationale_renders_route_short_label_in_both_locales() -> None:
    short = render_catalogue_entry("route.3.short", "en")["text"]
    en = render_catalogue_entry(
        "decision.public.investigate.rationale.preferred",
        "en",
        {"route_short_label": NarrativeValue.localized(short)},
    )["text"]
    assert en == (
        "Preferred hypothesis: Certification support; resolve the "
        "named evidence before any support decision."
    )
    ar_short = render_catalogue_entry("route.3.short", "ar")["text"]
    ar = render_catalogue_entry(
        "decision.public.investigate.rationale.preferred",
        "ar",
        {"route_short_label": NarrativeValue.localized(ar_short)},
    )["text"]
    assert ar == (
        "الفرضية المفضلة: دعم الشهادات؛ احسم الأدلة المسماة "
        "قبل أي قرار دعم."
    )


def test_route_need_is_emitted_only_with_material_trigger_and_unresolved_route() -> None:
    advance = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "public_decision"
            / "advance-route-3.json"
        ).read_text(encoding="utf-8")
    )
    route_unavailable = deepcopy(advance)
    route_unavailable["decision_inputs"]["route_evidence"] = "UNAVAILABLE"
    keys = [
        need["template_key"]
        for need in derive_evidence_needs(
            route_unavailable,
            evaluate_rules(route_unavailable),
        )
    ]
    assert keys == ["need.route.evidence_required"]
    missing = deepcopy(advance)
    del missing["decision_inputs"]["route_evidence"][0][
        "downside_cash_flows_m_sar"
    ]
    assert [
        need["template_key"]
        for need in derive_evidence_needs(
            missing,
            evaluate_rules(missing),
        )
    ] == ["need.route.evidence_required"]
    assert derive_evidence_needs(
        advance,
        evaluate_rules(advance),
    ) == []
    monitor = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "public_decision"
            / "monitor-r3-only.json"
        ).read_text(encoding="utf-8")
    )
    assert derive_evidence_needs(
        monitor,
        evaluate_rules(monitor),
    ) == []


def test_full_execution_signal_need_is_emitted_for_degraded_only_material_signal() -> None:
    advance = json.loads(
        (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "public_decision"
            / "advance-route-3.json"
        ).read_text(encoding="utf-8")
    )
    degraded = deepcopy(advance)
    degraded["trade"] = [
        {
            "year": 2024,
            "imports_usd_m": 8.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2025,
            "imports_usd_m": 9.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2026,
            "imports_usd_m": 10.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
    ]
    keys = [
        need["template_key"]
        for need in derive_evidence_needs(
            degraded,
            evaluate_rules(degraded),
        )
    ]
    assert keys == ["need.flows.reexport_origin_decomposition"]
    assert derive_evidence_needs(
        advance,
        evaluate_rules(advance),
    ) == []
    for opportunity_id in ("SAU-H0-721049", "SAU-H0-390210"):
        case = get_public_case(opportunity_id)
        needs = derive_evidence_needs(case, evaluate_rules(case))
        assert len(needs) == 5
        assert len({need["need_code"] for need in needs}) == 5
