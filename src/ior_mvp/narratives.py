from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from string import Formatter
from typing import Any, Literal


SUPPORTED_LOCALES = ("en", "ar")
KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
)
ValueKind = Literal["computed", "localized"]


class NarrativeCatalogueError(RuntimeError):
    """The governed decision narrative catalogue is malformed."""


@dataclass(frozen=True)
class NarrativeValue:
    text: str
    kind: ValueKind

    @classmethod
    def computed(cls, value: Any) -> NarrativeValue:
        return cls(text=str(value), kind="computed")

    @classmethod
    def localized(cls, value: Any) -> NarrativeValue:
        return cls(text=str(value), kind="localized")


def _fields(template: str) -> tuple[str, ...]:
    try:
        parsed = tuple(Formatter().parse(template))
    except ValueError as exc:
        raise NarrativeCatalogueError(
            "Decision narrative contains malformed placeholders"
        ) from exc
    fields: list[str] = []
    for _, field, format_spec, conversion in parsed:
        if field is None:
            continue
        if (
            KEY_PATTERN.fullmatch(field) is None
            or format_spec
            or conversion
        ):
            raise NarrativeCatalogueError(
                "Decision narrative placeholder is invalid"
            )
        fields.append(field)
    if len(fields) != len(set(fields)):
        raise NarrativeCatalogueError(
            "Decision narrative repeats a placeholder"
        )
    return tuple(fields)


def validate_decision_narratives(payload: dict[str, Any]) -> None:
    from .config import evidence_policy_config

    metadata = payload.get("metadata")
    locales = payload.get("locales")
    placeholder_kinds = payload.get("placeholder_kinds")
    templates = payload.get("templates")
    if not all(
        isinstance(value, dict)
        for value in (
            metadata,
            locales,
            placeholder_kinds,
            templates,
        )
    ):
        raise NarrativeCatalogueError(
            "Decision narrative catalogue sections must be mappings"
        )
    assert isinstance(metadata, dict)
    assert isinstance(locales, dict)
    assert isinstance(placeholder_kinds, dict)
    assert isinstance(templates, dict)
    if metadata.get("version") != "1.4.0":
        raise NarrativeCatalogueError(
            "Decision narrative metadata.version must be 1.4.0"
        )
    if metadata.get("default_locale") != "en":
        raise NarrativeCatalogueError(
            "Decision narrative default locale must be en"
        )
    if locales != {
        "en": {"bcp47": "en-US", "direction": "ltr"},
        "ar": {"bcp47": "ar-SA", "direction": "rtl"},
    }:
        raise NarrativeCatalogueError(
            "Decision narrative locale metadata is invalid"
        )
    if set(placeholder_kinds.values()) - {
        "computed",
        "localized",
    }:
        raise NarrativeCatalogueError(
            "Decision narrative placeholder kind is invalid"
        )
    if any(
        not isinstance(key, str)
        or KEY_PATTERN.fullmatch(key) is None
        for key in placeholder_kinds
    ):
        raise NarrativeCatalogueError(
            "Decision narrative placeholder name is invalid"
        )
    if tuple(templates) != SUPPORTED_LOCALES:
        raise NarrativeCatalogueError(
            "Decision narrative locales must be exactly en and ar"
        )
    policy = evidence_policy_config().get("synthetic_isolation")
    policy_labels = (
        {
            policy.get("display_label"),
            policy.get("display_label_ar"),
        }
        if isinstance(policy, dict)
        else set()
    )
    localized: dict[str, dict[str, str]] = {}
    for locale in SUPPORTED_LOCALES:
        values = templates.get(locale)
        if not isinstance(values, dict):
            raise NarrativeCatalogueError(
                f"Decision narrative templates.{locale} must be a mapping"
            )
        localized[locale] = values
    if set(localized["en"]) != set(localized["ar"]):
        raise NarrativeCatalogueError(
            "Decision narrative locale key sets do not match"
        )
    for key in localized["en"]:
        if KEY_PATTERN.fullmatch(key) is None:
            raise NarrativeCatalogueError(
                f"Decision narrative key is invalid: {key}"
            )
        locale_fields: list[tuple[str, ...]] = []
        for locale in SUPPORTED_LOCALES:
            value = localized[locale][key]
            if (
                not isinstance(value, str)
                or not value
                or value.strip() != value
                or unicodedata.normalize("NFC", value) != value
            ):
                raise NarrativeCatalogueError(
                    f"Decision narrative value is invalid: {locale}.{key}"
                )
            if value in policy_labels:
                raise NarrativeCatalogueError(
                    "Decision narrative catalogue duplicates a "
                    "synthetic policy label"
                )
            locale_fields.append(_fields(value))
        if set(locale_fields[0]) != set(locale_fields[1]):
            raise NarrativeCatalogueError(
                f"Decision narrative placeholder mismatch: {key}"
            )
        unknown = set(locale_fields[0]) - set(placeholder_kinds)
        if unknown:
            raise NarrativeCatalogueError(
                f"Decision narrative placeholder kind is missing: {key}"
            )


def render_catalogue_entry(
    key: str,
    locale: str,
    values: dict[str, NarrativeValue] | None = None,
) -> dict[str, Any]:
    from .config import decision_narratives_config

    if locale not in SUPPORTED_LOCALES:
        raise NarrativeCatalogueError(
            f"Unsupported decision narrative locale: {locale}"
        )
    payload = decision_narratives_config()
    templates = payload["templates"][locale]
    if key not in templates:
        raise NarrativeCatalogueError(
            f"Decision narrative key is missing: {key}"
        )
    template = templates[key]
    required = _fields(template)
    supplied = values or {}
    if set(required) != set(supplied):
        raise NarrativeCatalogueError(
            f"Decision narrative interpolation mismatch: {key}"
        )
    kinds = payload["placeholder_kinds"]
    segments: list[dict[str, Any]] = []
    for literal, field, _, _ in Formatter().parse(template):
        if literal:
            segments.append({"kind": "literal", "text": literal})
        if field is None:
            continue
        value = supplied[field]
        if (
            not isinstance(value, NarrativeValue)
            or value.kind != kinds[field]
        ):
            raise NarrativeCatalogueError(
                f"Decision narrative placeholder kind mismatch: {key}.{field}"
            )
        segments.append(
            {
                "kind": value.kind,
                "text": value.text,
                "ltr_isolate": (
                    locale == "ar" and value.kind == "computed"
                ),
            }
        )
    return {
        "text": "".join(segment["text"] for segment in segments),
        "segments": segments,
    }


def _rule_key_part(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise NarrativeCatalogueError(
            f"Rule ledger {field} must be a non-empty string"
        )
    return value.lower()


def RULE_NAME_KEY(rule_id: str, synthetic: bool = False) -> str:
    suffix = ".synthetic" if synthetic else ""
    return f"rule.{_rule_key_part(rule_id, 'rule_id')}.name{suffix}"


def RULE_RESULT_KEY(rule_id: str, code: str) -> str:
    return (
        f"rule.{_rule_key_part(rule_id, 'rule_id')}.result."
        f"{_rule_key_part(code, 'result_code')}"
    )


def RULE_EFFECT_KEY(rule_id: str, code: str) -> str:
    return (
        f"rule.{_rule_key_part(rule_id, 'rule_id')}.effect."
        f"{_rule_key_part(code, 'decision_effect_code')}"
    )


def _computed_rule_values(
    row: dict[str, Any],
    field: str,
) -> dict[str, NarrativeValue]:
    values = row.get(field)
    if not isinstance(values, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in values.items()
    ):
        raise NarrativeCatalogueError(
            f"Rule ledger {field} must map strings to strings"
        )
    return {
        key: NarrativeValue.computed(value)
        for key, value in values.items()
    }


def localize_rule_rows(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    localized_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise NarrativeCatalogueError("Rule ledger row must be a mapping")
        rule_id = _rule_key_part(row.get("rule_id"), "rule_id")
        result_code = _rule_key_part(
            row.get("result_code"),
            "result_code",
        )
        effect_code = _rule_key_part(
            row.get("decision_effect_code"),
            "decision_effect_code",
        )
        localized = {
            locale: {
                "name": render_catalogue_entry(
                    RULE_NAME_KEY(
                        rule_id,
                        synthetic=row.get("synthetic_flag") is True,
                    ),
                    locale,
                ),
                "result": render_catalogue_entry(
                    RULE_RESULT_KEY(rule_id, result_code),
                    locale,
                    _computed_rule_values(row, "result_values"),
                ),
                "decision_effect": render_catalogue_entry(
                    RULE_EFFECT_KEY(rule_id, effect_code),
                    locale,
                    _computed_rule_values(row, "effect_values"),
                ),
            }
            for locale in SUPPORTED_LOCALES
        }
        localized_rows.append({**row, "localized": localized})
    return localized_rows
