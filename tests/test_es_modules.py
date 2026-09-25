from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


STATIC_ROOT = PROJECT_ROOT / "src" / "ior_mvp" / "static"
MODULE_ROOT = STATIC_ROOT / "modules"
EXPECTED_MODULES = {
    "modules/dossier-actions.js",
    "app.js",
    "modules/api.js",
    "modules/dom.js",
    "modules/events.js",
    "modules/extraction.js",
    "modules/formatters.js",
    "modules/graph/diagram.js",
    "modules/graph/evidence.js",
    "modules/graph/index.js",
    "modules/graph/labels.js",
    "modules/graph/layout.js",
    "modules/graph/model.js",
    "modules/graph/passports.js",
    "modules/graph/render.js",
    "modules/i18n.js",
    "modules/methodology.js",
    "modules/portfolio.js",
    "modules/screening/evidence.js",
    "modules/screening/index.js",
    "modules/screening/labels.js",
    "modules/screening/ledger-labels.js",
    "modules/screening/queue.js",
    "modules/screening/record-evidence.js",
    "modules/screening/record.js",
    "modules/screening/summary.js",
    "modules/selection/index.js",
    "modules/selection/render.js",
    "modules/state.js",
    "modules/workspace.js",
    "modules/renderers/capability.js",
    "modules/renderers/decision.js",
    "modules/renderers/economics.js",
    "modules/renderers/evidence.js",
    "modules/renderers/index.js",
    "modules/renderers/integrity.js",
    "modules/renderers/rules.js",
    "modules/renderers/trade.js",
    "modules/analyst-navigation.js",
    "modules/claim-links.js",
    "modules/executive/context.js",
    "modules/executive/data.js",
    "modules/executive/evidence.js",
    "modules/executive/index.js",
    "modules/executive/labels.js",
    "modules/executive/registry.js",
    "modules/executive/render.js",
    "modules/executive/routes.js",
    "modules/executive/simulation.js",
    "modules/executive/steps.js",
    "modules/executive/summary.js",
}


def _production_modules() -> dict[str, Path]:
    paths = [STATIC_ROOT / "app.js", *sorted(MODULE_ROOT.rglob("*.js"))]
    return {
        path.relative_to(STATIC_ROOT).as_posix(): path
        for path in paths
        if path.is_file()
    }


def test_index_loads_app_as_an_es_module() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert '<script type="module" src="/static/app.js"></script>' in html
    assert '<script src="/static/app.js" defer></script>' not in html


def test_module_graph_has_named_exports_no_defaults_and_resolved_local_imports() -> None:
    modules = _production_modules()

    assert set(modules) == EXPECTED_MODULES
    for relative, path in modules.items():
        source = path.read_text(encoding="utf-8")
        assert "export default" not in source, relative
        assert re.search(
            r"\bexport\s+(?:async\s+)?(?:const|function|class|\{)",
            source,
        ), relative
        for specifier in re.findall(
            r"""(?:from\s+|import\s*)["'](\.[^"']+)["']""",
            source,
        ):
            target = (path.parent / specifier).resolve()
            if target.suffix != ".js":
                target = target.with_suffix(".js")
            assert target.is_file(), f"{relative}: unresolved {specifier}"
            assert target.is_relative_to(STATIC_ROOT.resolve())


def test_every_browser_module_has_at_most_199_lines() -> None:
    modules = _production_modules()

    assert set(modules) == EXPECTED_MODULES
    for relative, path in modules.items():
        physical_lines = len(path.read_text(encoding="utf-8").splitlines())
        assert physical_lines <= 199, f"{relative}: {physical_lines} lines"


def test_es_module_syntax_checker_checks_every_js_file_in_module_mode() -> None:
    checker = PROJECT_ROOT / "scripts" / "check_es_modules.py"
    result = subprocess.run(
        [sys.executable, str(checker), "--node", "node"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"ES MODULE CHECK PASS ({len(EXPECTED_MODULES)} files)" in result.stdout
