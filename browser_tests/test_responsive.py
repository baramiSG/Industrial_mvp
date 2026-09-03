from __future__ import annotations

import json
from itertools import product

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    CASES,
    LOCALES,
    MODES,
    VIEWPORTS,
    BrowserSession,
    Locale,
    Mode,
    Viewport,
)
from browser_tests.pages import goto_portfolio


pytestmark = pytest.mark.e2e
MODE_VIEWPORT_LOCALES = tuple(product(MODES, VIEWPORTS, LOCALES))


@pytest.mark.parametrize(
    ("mode", "viewport", "locale"),
    MODE_VIEWPORT_LOCALES,
    ids=[
        f"{mode}-{viewport.name}-{locale.code}"
        for mode, viewport, locale in MODE_VIEWPORT_LOCALES
    ],
)
def test_layout_has_no_horizontal_overflow_and_primary_controls_are_actionable(
    browser_session: BrowserSession,
    mode: Mode,
    viewport: Viewport,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    dimensions = page.evaluate(
        """() => {
          const root = document.documentElement;
          const body = document.body;
          const main = document.querySelector("main.main");
          const sidebar = document.querySelector(".sidebar");
          const topbar = document.querySelector(".topbar h1");
          const island = document.querySelector(".source-language-island");
          const disclosure = document.querySelector(
            ".portfolio-synthetic-disclosure"
          );
          const opportunityGrid = document.querySelector(".opportunity-grid");
          const stateBadge = document.querySelector(".decision-state-large");
          const decisionBoxes = document.querySelectorAll(
            ".decision-lists > div"
          );
          const box = (node) => {
            if (!node) return null;
            const rect = node.getBoundingClientRect();
            return {
              left: Math.round(rect.left),
              top: Math.round(rect.top),
              right: Math.round(rect.right),
              bottom: Math.round(rect.bottom),
              width: Math.round(rect.width),
            };
          };
          return {
            direction: getComputedStyle(root).direction,
            document: {
              clientWidth: root.clientWidth,
              scrollWidth: root.scrollWidth,
            },
            body: {
              clientWidth: body.clientWidth,
              scrollWidth: body.scrollWidth,
            },
            main: {
              ...box(main),
              clientWidth: main.clientWidth,
              scrollWidth: main.scrollWidth,
            },
            sidebar: box(sidebar),
            topbarAlign: getComputedStyle(topbar).textAlign,
            islandDirection: island
              ? getComputedStyle(island).direction
              : null,
            disclosure: box(disclosure),
            opportunityGrid: box(opportunityGrid),
            stateBadge: box(stateBadge),
            decisionBoxes: [...decisionBoxes].map(box),
          };
        }"""
    )
    diagnostic = (
        browser_session.artifact_dir
        / "responsive"
        / f"{mode}-{viewport.name}-{locale.code}.json"
    )
    diagnostic.parent.mkdir(parents=True, exist_ok=True)
    diagnostic.write_text(
        json.dumps(dimensions, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    for area in ("document", "body", "main"):
        assert dimensions[area]["scrollWidth"] <= dimensions[area][
            "clientWidth"
        ], dimensions
    assert dimensions["direction"] == locale.direction
    assert dimensions["islandDirection"] == "ltr"
    if locale.direction == "rtl":
        assert dimensions["sidebar"]["right"] == viewport.width
        assert dimensions["main"]["right"] <= (
            viewport.width - dimensions["sidebar"]["width"]
        )
        assert dimensions["topbarAlign"] in {"start", "right"}
        if mode == "simulated":
            assert (
                dimensions["disclosure"]["right"]
                == dimensions["opportunityGrid"]["right"]
            )
    else:
        assert dimensions["sidebar"]["left"] == 0
        assert dimensions["main"]["left"] >= dimensions["sidebar"]["width"]
        assert dimensions["topbarAlign"] in {"start", "left"}
        if mode == "simulated":
            assert (
                dimensions["disclosure"]["left"]
                == dimensions["opportunityGrid"]["left"]
            )
    badge = dimensions["stateBadge"]
    for decision_box in dimensions["decisionBoxes"]:
        intersects = not (
            badge["right"] <= decision_box["left"]
            or badge["left"] >= decision_box["right"]
            or badge["bottom"] <= decision_box["top"]
            or badge["top"] >= decision_box["bottom"]
        )
        assert not intersects, dimensions
    route_text = page.locator(".route-pill").inner_text()
    assert ": " in route_text
    if locale.code == "ar":
        expected_tokens = {f"HS {case.hs6}" for case in CASES}
        token_details = page.locator(
            "bdi.technical-token"
        ).evaluate_all(
            """nodes => nodes.map(node => ({
              text: node.textContent,
              direction: getComputedStyle(node).direction,
              unicodeBidi: getComputedStyle(node).unicodeBidi,
            }))"""
        )
        for expected in expected_tokens:
            detail = next(
                item for item in token_details if item["text"] == expected
            )
            assert detail == {
                "text": expected,
                "direction": "ltr",
                "unicodeBidi": "isolate",
            }
    mode_group = page.locator(".mode-control")
    selector = page.locator("#opportunity-select")
    dossier = page.locator("[data-dossier-html]")
    copy_json = page.locator("[data-copy-json]")
    locale_switch = page.locator("#locale-switch")
    for control in (
        mode_group,
        selector,
        dossier,
        copy_json,
        locale_switch,
    ):
        expect(control).to_be_visible()
    for control in (selector, dossier, copy_json, locale_switch):
        expect(control).to_be_enabled()
        control.click(trial=True)
    for button in mode_group.get_by_role("button").all():
        expect(button).to_be_enabled()
        button.click(trial=True)
    assert page.viewport_size == viewport.as_dict()
