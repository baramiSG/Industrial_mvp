from __future__ import annotations

from itertools import product
from typing import Any

import pytest

from browser_tests.harness import (
    AR,
    CASES,
    EN,
    DESKTOP,
    POLYPROPYLENE,
    STEEL,
    TABLET,
    BrowserSession,
    Locale,
    Viewport,
)
from browser_tests.pages import (
    first_queue_entry_hs6,
    goto_portfolio,
    open_dossier_popup,
    open_queue,
    open_record,
    open_screening,
    screening_back,
    select_case,
    select_mode,
)
from browser_tests.visual_baselines import VisualBaselineSession


pytestmark = [pytest.mark.e2e, pytest.mark.visual]
VISUAL_MATRIX = tuple(product((EN, AR), (DESKTOP, TABLET)))


def _anchor(page: Any, selector: str) -> None:
    page.locator(selector).evaluate(
        "(node) => node.scrollIntoView({block: 'start'})"
    )


def _anchor_screening(page: Any) -> None:
    page.locator("#screening").evaluate(
        """async (node) => {
          await document.fonts.ready;
          let previousScrollY = window.scrollY;
          let stableFrames = 0;
          for (let frame = 0; frame < 60 && stableFrames < 3; frame += 1) {
            await new Promise(requestAnimationFrame);
            const currentScrollY = window.scrollY;
            stableFrames = Math.abs(currentScrollY - previousScrollY) <= 0.5
              ? stableFrames + 1
              : 0;
            previousScrollY = currentScrollY;
          }
          if (stableFrames < 3) {
            throw new Error("NAVIGATION_SCROLL_NOT_SETTLED");
          }
          const root = document.documentElement;
          const previousBehavior = root.style.scrollBehavior;
          root.style.scrollBehavior = "auto";
          const margin = parseFloat(
            getComputedStyle(node).scrollMarginBlockStart
          ) || 0;
          const target = Math.round(
            node.getBoundingClientRect().top + window.scrollY - margin
          );
          window.scrollTo({top: target, left: 0, behavior: "auto"});
          await new Promise(requestAnimationFrame);
          await new Promise(requestAnimationFrame);
          if (Math.abs(window.scrollY - target) > 0.5) {
            throw new Error("SCREENING_ANCHOR_NOT_SETTLED");
          }
          root.style.scrollBehavior = previousBehavior;
        }"""
    )
    page.screenshot(
        full_page=False,
        animations="disabled",
        caret="hide",
    )


@pytest.mark.parametrize(
    ("locale", "viewport"),
    VISUAL_MATRIX,
    ids=[
        f"{locale.code}-{viewport.name}"
        for locale, viewport in VISUAL_MATRIX
    ],
)
def test_governed_visual_baselines_match(
    browser_session: BrowserSession,
    visual_session: VisualBaselineSession,
    locale: Locale,
    viewport: Viewport,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    _anchor(page, "section.compact-section")
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-a-portfolio-public",
        case_id=None,
        mode="public",
    )
    select_mode(page, "simulated", locale)
    _anchor(page, "section.compact-section")
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-a-portfolio-simulated",
        case_id=None,
        mode="simulated",
    )
    workspace_states = (
        (
            STEEL,
            "public",
            "journey-b-steel-public-workspace",
        ),
        (
            STEEL,
            "simulated",
            "journey-c-steel-simulated-workspace",
        ),
        (
            POLYPROPYLENE,
            "public",
            "journey-d-polypropylene-public-workspace",
        ),
        (
            POLYPROPYLENE,
            "simulated",
            "journey-d-polypropylene-simulated-workspace",
        ),
    )
    for case, mode, screen in workspace_states:
        goto_portfolio(page, mode, locale)
        select_case(page, case, mode, locale)
        _anchor(page, "#workspace")
        visual_session.capture(
            page,
            locale=locale.code,
            viewport=viewport.name,
            screen=screen,
            case_id=case.id,
            mode=mode,
        )
    dossier_states = (
        (
            STEEL,
            "public",
            "journey-e-steel-public-dossier",
        ),
        (
            STEEL,
            "simulated",
            "journey-e-steel-simulated-dossier",
        ),
        (
            POLYPROPYLENE,
            "public",
            "journey-e-polypropylene-public-dossier",
        ),
        (
            POLYPROPYLENE,
            "simulated",
            "journey-e-polypropylene-simulated-dossier",
        ),
    )
    for case, mode, screen in dossier_states:
        goto_portfolio(page, mode, locale)
        select_case(page, case, mode, locale)
        popup = open_dossier_popup(page, case, mode, locale)
        visual_session.capture(
            popup,
            locale=locale.code,
            viewport=viewport.name,
            screen=screen,
            case_id=case.id,
            mode=mode,
        )
        popup.close()

    goto_portfolio(page, "public", locale)
    open_screening(page, locale)
    _anchor_screening(page)
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-f-screening-summary",
        case_id=None,
        mode="public",
    )
    open_queue(page, "robust_public_finding", locale)
    _anchor_screening(page)
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-f-screening-queue-robust",
        case_id=None,
        mode="public",
    )
    screening_back(page, "summary", locale)
    open_queue(page, "resilience_case", locale)
    _anchor_screening(page)
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-f-screening-queue-empty",
        case_id=None,
        mode="public",
    )
    screening_back(page, "summary", locale)
    open_queue(page, "robust_public_finding", locale)
    hs6 = first_queue_entry_hs6(page)
    open_record(page, hs6, locale)
    _anchor_screening(page)
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-f-screening-record",
        case_id=hs6,
        mode="public",
    )

    for case in CASES[2:]:
        goto_portfolio(page, "public", locale)
        select_case(page, case, "public", locale)
        _anchor(page, "#workspace")
        visual_session.capture(
            page,
            locale=locale.code,
            viewport=viewport.name,
            screen=f"journey-g-{case.slug}-public-workspace",
            case_id=case.id,
            mode="public",
        )
