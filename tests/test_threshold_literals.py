from __future__ import annotations

from pathlib import Path

from ior_mvp.config import PROJECT_ROOT
from scripts.check_threshold_literals import (
    Finding,
    SOURCE_DIR,
    THRESHOLDS_PATH,
    collect_numeric_values,
    main,
    scan_repository,
    scan_source,
)


def _write_thresholds(path: Path) -> None:
    path.write_text(
        "rules:\n"
        "  probe:\n"
        "    limit: 0.40\n",
        encoding="utf-8",
    )


def test_collect_numeric_values_recurses_and_excludes_strings_and_bools() -> None:
    payload = {
        "rules": {
            "ratio": 1.25,
            "nested": [50, {"share": 0.40}],
            "version": "1.25",
            "enabled": True,
        }
    }
    assert collect_numeric_values(payload) == {0.4, 1.25, 50.0}


def test_scan_source_flags_configured_comparison_literal() -> None:
    findings = scan_source(
        "def check(x: float) -> bool:\n"
        "    return x <= 0.40\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4},
    )
    assert findings == [
        Finding(
            path="src/ior_mvp/probe.py",
            line=2,
            value=0.4,
        )
    ]


def test_scan_source_checks_left_and_all_comparator_operands() -> None:
    findings = scan_source(
        "def check(x: float) -> bool:\n"
        "    return 0.40 < x < 1.25\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4, 1.25},
    )
    assert findings == [
        Finding(path="src/ior_mvp/probe.py", line=2, value=0.4),
        Finding(path="src/ior_mvp/probe.py", line=2, value=1.25),
    ]


def test_scan_source_exempts_state_and_formula_bounds_zero_to_three() -> None:
    findings = scan_source(
        "def valid(state: int) -> bool:\n"
        "    return 0 <= state <= 3\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.0, 1.0, 2.0, 3.0},
    )
    assert findings == []


def test_scan_source_ignores_configured_values_outside_comparisons() -> None:
    findings = scan_source(
        "LIMIT = 0.40\n"
        "WARNING = 1.25\n"
        "def check(x: float) -> bool:\n"
        "    return x <= LIMIT\n",
        path="src/ior_mvp/probe.py",
        threshold_values={0.4, 1.25},
    )
    assert findings == []


def test_main_returns_one_and_reports_file_line_value(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "result = value <= 0.40\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 1
    assert "src/probe.py:1:0.4" in capsys.readouterr().out


def test_main_returns_zero_for_clean_sources(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "LIMIT = 0.40\n"
        "result = value <= LIMIT\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 0
    assert "THRESHOLD LITERAL SCAN PASS" in capsys.readouterr().out


def test_main_returns_two_for_invalid_yaml(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    threshold_path.write_text("rules: [", encoding="utf-8")
    (source_dir / "probe.py").write_text("value = 1\n", encoding="utf-8")

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 2
    assert "THRESHOLD LITERAL SCAN ERROR" in capsys.readouterr().err


def test_main_returns_two_for_python_parse_error(
    tmp_path: Path,
    capsys,
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    threshold_path = tmp_path / "thresholds.yaml"
    _write_thresholds(threshold_path)
    (source_dir / "probe.py").write_text(
        "def broken(:\n",
        encoding="utf-8",
    )

    status = main(source_dir, threshold_path, tmp_path)

    assert status == 2
    assert "SyntaxError" in capsys.readouterr().err


def test_repository_has_no_embedded_threshold_comparison_literals() -> None:
    findings, source_count, threshold_count = scan_repository(
        SOURCE_DIR,
        THRESHOLDS_PATH,
        root=PROJECT_ROOT,
    )
    assert source_count > 0
    assert threshold_count > 0
    assert findings == []


def test_frontend_hhi_caption_uses_payload_threshold() -> None:
    source = (
        PROJECT_ROOT / "src" / "ior_mvp" / "static" / "app.js"
    ).read_text(encoding="utf-8")
    assert "Resilience review threshold: 0.25" not in source
    assert "props.supplier_concentration?.hhi_threshold" in source
