from __future__ import annotations

from ior_mvp.ai_extraction import extract_specification, run_extraction_golden_set


def test_ar_en_golden_set_is_exact() -> None:
    result = run_extraction_golden_set()
    assert result["passed"] == result["total"] == 4
    assert result["accuracy"] == 1.0


def test_unknown_text_remains_unresolved() -> None:
    result = extract_specification("نص غير محدد", "Unrelated text")
    assert result["fields"] == {}
    assert result["warnings"]
