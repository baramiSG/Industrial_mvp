from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from ior_mvp.acquisition.entities.normalisation import (
    NormalisedName,
    normalise_exact,
    normalise_name,
    normalise_variant,
)
from ior_mvp.acquisition.entities.rules import (
    ENTITY_RULES_PATH,
    EntityResolutionError,
    load_entity_rules,
)


EXPECTED_TOP_LEVEL_KEYS = {
    "metadata",
    "id_scheme",
    "normalisation",
    "linking",
    "localities",
    "span_screen",
}
EXPECTED_EXACT_KEYS = {
    "unicode_form",
    "casefold",
    "strip_arabic_tashkeel",
    "strip_tatweel",
    "fold_arabic_indic_digits",
    "punctuation_to_space",
    "collapse_whitespace",
}
EXPECTED_VARIANT_KEYS = {
    "arabic_letter_folds",
    "definite_article",
    "legal_form_tokens_en",
    "legal_form_tokens_ar",
    "transliteration_variants",
}


def _payload() -> dict:
    return yaml.safe_load(ENTITY_RULES_PATH.read_text(encoding="utf-8"))


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "entity_resolution.v1.yaml"
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def test_rules_yaml_loads_version_and_exact_shape() -> None:
    rules = load_entity_rules()

    assert rules.raw["metadata"]["artifact"] == "industrial-opportunity-entity-resolution"
    assert rules.raw["metadata"]["version"] == "1.0.0"
    assert rules.raw["normalisation"]["method_id"] == "NAME_NORMALISATION_V1"
    assert rules.raw["normalisation"]["version"] == "1.0.0"
    assert set(rules.raw) == EXPECTED_TOP_LEVEL_KEYS
    assert set(rules.raw["normalisation"]) == {
        "method_id",
        "version",
        "exact",
        "variant",
    }
    assert set(rules.raw["normalisation"]["exact"]) == EXPECTED_EXACT_KEYS
    assert set(rules.raw["normalisation"]["variant"]) == EXPECTED_VARIANT_KEYS
    assert rules.raw["id_scheme"]["entity_types"] == [
        "COMPANY",
        "PLANT",
        "LINE",
        "LICENCE_HOLDER",
    ]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda p: p.update({"unexpected": {}}), "unknown"),
        (lambda p: p["metadata"].update({"version": "2.0.0"}), "version"),
        (lambda p: p["normalisation"]["exact"].update({"casefold": "yes"}), "casefold"),
        (
            lambda p: p["linking"].update({"resolved_statuses": ["EXACT", "MAGIC"]}),
            "resolved_statuses",
        ),
    ],
)
def test_rules_reject_unknown_keys_wrong_version_and_bad_enums(
    tmp_path: Path,
    mutation,
    message: str,
) -> None:
    payload = copy.deepcopy(_payload())
    mutation(payload)

    with pytest.raises(EntityResolutionError, match=message):
        load_entity_rules(_write_payload(tmp_path, payload))


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("  Universal   Metal   Coating   Company   Ltd.  ", "universal metal coating company ltd"),
        ("Café", "café"),
        ("A،B؛C", "a b c"),
        ("A&B/C\\D_E-F", "a b c d e f"),
        ("١٢٣٤٥٦٧٨٩٠", "1234567890"),
        ("شَـرِكَة", "شركة"),
    ],
)
def test_normalise_exact_rules(span: str, expected: str) -> None:
    assert normalise_exact(span) == expected


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("Universal Metal Coating Company Ltd.", "Universal Metal Coating"),
        ("Universal Metal Coating شركة المحدودة", "Universal Metal Coating"),
        ("The Advanced Petrochemical Company", "Advanced Petrochemical"),
        ("Al Advanced Petrochemical", "Advanced Petrochemical"),
        ("الشركة", "شركه"),
        ("إتحاد", "اتحاد"),
        ("Al-Jubail Industrial City", "Jubail"),
    ],
)
def test_normalise_variant_rules(left: str, right: str) -> None:
    assert normalise_variant(left) == normalise_variant(right)


def test_variant_differs_when_only_an_unlisted_token_differs() -> None:
    assert normalise_variant("Universal Metal Coating Group") != normalise_variant(
        "Universal Metal Coating"
    )


def test_visual_order_arabic_is_never_reversed() -> None:
    visual = "ةدوجلاو سيياقلماو تافصاوملل ةيدوعسلا ةئيهلا"
    result = normalise_name(visual, language="ar", text_order="VISUAL")

    assert result.exact.startswith("ةدوجلاو")
    assert result.exact != visual[::-1]
    assert result.text_order == "VISUAL"


def test_original_span_retained_beside_normalised_form() -> None:
    span = "  Universal Metal Coating Company Ltd. "

    result = normalise_name(span, language="en", text_order="LOGICAL")

    assert result == NormalisedName(
        span_text=span,
        language="en",
        text_order="LOGICAL",
        exact="universal metal coating company ltd",
        variant="universal metal coating",
    )


def test_transliteration_only_from_injected_table(tmp_path: Path) -> None:
    assert normalise_variant("Yenbo") == "yenbo"
    payload = copy.deepcopy(_payload())
    payload["normalisation"]["variant"]["transliteration_variants"]["yenbo"] = "yanbu"
    injected = load_entity_rules(_write_payload(tmp_path, payload))

    assert normalise_variant("Yenbo", rules=injected) == "yanbu"


def test_definite_article_prefix_needs_two_remaining_characters() -> None:
    assert normalise_variant("ال") == "ال"
    assert normalise_variant("الا") == "الا"
    assert normalise_variant("الاب") == "اب"
