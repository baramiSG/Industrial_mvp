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
        "version": "1.1.0",
        "effective_date": "2026-09-02",
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


def test_ui_catalogue_values_are_nonempty_nfc_strings() -> None:
    for locale, strings in _catalogue()["strings"].items():
        for key, value in strings.items():
            assert isinstance(value, str), (locale, key)
            assert value.strip() == value and value, (locale, key)
            assert unicodedata.normalize("NFC", value) == value


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
        "catalogue_version": "1.1.0",
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
