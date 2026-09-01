from __future__ import annotations

from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


def test_frontend_contains_evidence_mode_and_arabic_support() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert "Public evidence" in html
    assert "Ministry simulation" in html
    assert 'dir="rtl"' in html
    assert "Decision workspace" in html


def test_frontend_has_no_external_cdn_dependency() -> None:
    html = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "index.html").read_text(encoding="utf-8")
    assert "cdnjs" not in html
    assert "unpkg" not in html
    assert "jsdelivr" not in html
    assert "fonts.googleapis" not in html


def test_synthetic_warning_style_exists() -> None:
    css = (PROJECT_ROOT / "src" / "ior_mvp" / "static" / "styles.css").read_text(encoding="utf-8")
    assert ".synthetic-warning" in css
    assert ".synthetic-row" in css
