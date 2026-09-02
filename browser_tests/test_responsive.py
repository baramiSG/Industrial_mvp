from __future__ import annotations

import json
from itertools import product

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    MODES,
    VIEWPORTS,
    BrowserSession,
    Mode,
    Viewport,
)
from browser_tests.pages import goto_portfolio


pytestmark = pytest.mark.e2e
MODE_VIEWPORTS = tuple(
    (mode, viewport)
    for mode, viewport in product(MODES, VIEWPORTS)
)


@pytest.mark.parametrize(
    ("mode", "viewport"),
    MODE_VIEWPORTS,
    ids=[
        f"{mode}-{viewport.name}"
        for mode, viewport in MODE_VIEWPORTS
    ],
)
def test_layout_has_no_horizontal_overflow_and_primary_controls_are_actionable(
    browser_session: BrowserSession,
    mode: Mode,
    viewport: Viewport,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode)

    dimensions = page.evaluate(
        """() => {
          const documentNode = document.documentElement;
          const main = document.querySelector("main.main");
          const describe = (node) => ({
            clientWidth: node.clientWidth,
            scrollWidth: node.scrollWidth,
          });
          const offenders = Array.from(document.querySelectorAll("body *"))
            .map((node) => {
              const box = node.getBoundingClientRect();
              return {
                selector: [
                  node.tagName.toLowerCase(),
                  node.id ? `#${node.id}` : "",
                  ...Array.from(node.classList).map(
                    (name) => `.${name}`
                  ),
                ].join(""),
                left: Math.round(box.left),
                right: Math.round(box.right),
                width: Math.round(box.width),
                scrollWidth: node.scrollWidth,
                clientWidth: node.clientWidth,
              };
            })
            .filter((item) => (
              item.right > documentNode.clientWidth + 1 ||
              item.left < -1 ||
              item.scrollWidth > item.clientWidth + 1
            ))
            .slice(0, 20);
          return {
            document: describe(documentNode),
            body: describe(document.body),
            main: describe(main),
            offenders,
          };
        }"""
    )
    diagnostic = (
        browser_session.artifact_dir
        / "responsive"
        / f"{mode}-{viewport.name}.json"
    )
    diagnostic.parent.mkdir(parents=True, exist_ok=True)
    diagnostic.write_text(
        json.dumps(dimensions, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    assert (
        dimensions["document"]["scrollWidth"]
        <= dimensions["document"]["clientWidth"]
    ), dimensions
    assert (
        dimensions["body"]["scrollWidth"]
        <= dimensions["body"]["clientWidth"]
    ), dimensions
    assert (
        dimensions["main"]["scrollWidth"]
        <= dimensions["main"]["clientWidth"]
    ), dimensions

    mode_group = page.get_by_role("group", name="Evidence mode")
    selector = page.get_by_label("Opportunity")
    dossier = page.get_by_role("button", name="Open dossier")
    copy_json = page.get_by_role(
        "button",
        name="Copy decision JSON",
    )
    for control in (mode_group, selector, dossier, copy_json):
        expect(control).to_be_visible()
    for control in (selector, dossier, copy_json):
        expect(control).to_be_enabled()
        control.click(trial=True)
    for button in mode_group.get_by_role("button").all():
        expect(button).to_be_enabled()
        button.click(trial=True)
    assert page.viewport_size == viewport.as_dict()
