from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from browser_tests.harness import (
    AppServer,
    BrowserFailureCollector,
    DESKTOP,
)


pytestmark = pytest.mark.e2e


def test_failure_collector_observes_all_required_channels(
    new_context: Any,
    app_server: AppServer,
    artifact_dir: Path,
) -> None:
    context = new_context(
        base_url=app_server.base_url,
        locale="en-US",
        permissions=["clipboard-read", "clipboard-write"],
        reduced_motion="reduce",
        viewport=DESKTOP.as_dict(),
    )
    collector = BrowserFailureCollector(app_server.base_url)
    collector.attach_context(context)
    context.route(
        "**/s06-requestfailed-probe",
        lambda route: route.abort("failed"),
    )
    context.route(
        "https://example.invalid/**",
        lambda route: route.abort("blockedbyclient"),
    )
    page = context.new_page()
    collector.attach_page(page)
    page.goto("/")

    page.evaluate("console.error('s06-console-probe')")
    with page.expect_event("pageerror"):
        page.evaluate(
            "setTimeout(() => { "
            "throw new Error('s06-pageerror-probe'); "
            "}, 0)"
        )
    page.evaluate(
        "fetch('/s06-requestfailed-probe').catch(() => null)"
    )
    page.evaluate(
        "fetch('/api/opportunities/DOES-NOT-EXIST')"
        ".then(() => null)"
    )
    page.evaluate(
        "fetch('https://example.invalid/s06-external-probe')"
        ".catch(() => null)"
    )

    categories = {record.category for record in collector.records}
    assert categories == {
        "console-error",
        "pageerror",
        "requestfailed",
        "app-http-error",
        "external-request",
    }
    rendered = collector.render()
    for probe in (
        "s06-console-probe",
        "s06-pageerror-probe",
        "s06-requestfailed-probe",
        "DOES-NOT-EXIST",
        "s06-external-probe",
    ):
        assert probe in rendered
    (artifact_dir / "failure-collector-summary.json").write_text(
        json.dumps(
            {
                "categories": sorted(categories),
                "observation_only": True,
                "ordinary_collector_exclusions": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
