"""Deterministic NAME_NORMALISATION_V1 operations."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .rules import EntityResolutionError, EntityRules, entity_resolution_rules

_ARABIC_TASHKEEL = re.compile("[\u064b-\u0652\u0670]")
_ARABIC_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class NormalisedName:
    span_text: str
    language: str
    text_order: str
    exact: str
    variant: str


def _rules(rules: EntityRules | None) -> EntityRules:
    return rules if rules is not None else entity_resolution_rules()


def normalise_exact(text: str, rules: EntityRules | None = None) -> str:
    """Apply the frozen exact rules in their configured order."""
    if not isinstance(text, str):
        raise EntityResolutionError("normalise_exact text must be a string")
    configured = _rules(rules)
    exact = configured.exact
    value = unicodedata.normalize(exact["unicode_form"], text)
    if exact["casefold"]:
        value = value.casefold()
    if exact["strip_arabic_tashkeel"]:
        value = _ARABIC_TASHKEEL.sub("", value)
    if exact["strip_tatweel"]:
        value = value.replace("\u0640", "")
    if exact["fold_arabic_indic_digits"]:
        value = value.translate(_ARABIC_INDIC_DIGITS)
    value = value.translate(str.maketrans({char: " " for char in exact["punctuation_to_space"]}))
    if exact["collapse_whitespace"]:
        value = _WHITESPACE.sub(" ", value).strip()
    return value


def _fold_arabic(text: str, rules: EntityRules) -> str:
    return text.translate(str.maketrans(rules.variant["arabic_letter_folds"]))


def _strip_definite_articles(tokens: list[str], rules: EntityRules) -> list[str]:
    definite = rules.variant["definite_article"]
    english = set(definite["en_tokens"])
    prefix = definite["ar_prefix"]
    stripped: list[str] = []
    for token in tokens:
        if token in english:
            continue
        if token.startswith(prefix) and len(token) - len(prefix) >= 2:
            token = token[len(prefix) :]
        stripped.append(token)
    return stripped


def _legal_form_tokens(rules: EntityRules) -> set[str]:
    raw_tokens = (
        list(rules.variant["legal_form_tokens_en"])
        + list(rules.variant["legal_form_tokens_ar"])
    )
    result: set[str] = set()
    for raw in raw_tokens:
        folded = _fold_arabic(normalise_exact(raw, rules), rules)
        stripped = _strip_definite_articles(folded.split(), rules)
        if len(stripped) == 1:
            result.add(stripped[0])
    return result


def _replace_transliteration_phrases(text: str, rules: EntityRules) -> str:
    variants = rules.variant["transliteration_variants"]
    for source in sorted(variants, key=lambda item: (-len(item.split()), -len(item), item)):
        source_exact = normalise_exact(source, rules)
        target_exact = normalise_exact(variants[source], rules)
        pattern = re.compile(rf"(?<!\w){re.escape(source_exact)}(?!\w)")
        text = pattern.sub(target_exact, text)
    return _WHITESPACE.sub(" ", text).strip()


def normalise_variant(text: str, rules: EntityRules | None = None) -> str:
    """Apply exact normalization followed by the frozen variant rules."""
    configured = _rules(rules)
    value = _fold_arabic(normalise_exact(text, configured), configured)
    tokens = _strip_definite_articles(value.split(), configured)
    legal_forms = _legal_form_tokens(configured)
    while tokens and tokens[-1] in legal_forms:
        tokens.pop()
    value = " ".join(tokens)
    return _replace_transliteration_phrases(value, configured)


def normalise_name(
    span_text: str,
    *,
    language: str,
    text_order: str,
    rules: EntityRules | None = None,
) -> NormalisedName:
    """Retain the verbatim span beside both deterministic forms."""
    if language not in {"en", "ar"}:
        raise EntityResolutionError(f"Unsupported mention language: {language}")
    if text_order not in {"LOGICAL", "VISUAL"}:
        raise EntityResolutionError(f"Unsupported text order: {text_order}")
    if text_order == "VISUAL" and language != "ar":
        raise EntityResolutionError("VISUAL text order is permitted only for Arabic")
    configured = _rules(rules)
    return NormalisedName(
        span_text=span_text,
        language=language,
        text_order=text_order,
        exact=normalise_exact(span_text, configured),
        variant=normalise_variant(span_text, configured),
    )
