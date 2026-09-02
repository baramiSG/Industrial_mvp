from __future__ import annotations

import pytest
from playwright.sync_api import Locator

from browser_tests.harness import (
    POLYPROPYLENE,
    STEEL,
    VIEWPORTS,
    BrowserSession,
    ReferenceRecorder,
    Viewport,
)
from browser_tests.pages import (
    goto_portfolio,
    open_dossier_popup,
    select_case,
    select_mode,
)


pytestmark = pytest.mark.e2e


def _capture(
    locator: Locator,
    recorder: ReferenceRecorder,
    viewport: Viewport,
    state: str,
    *,
    journey: str,
    mode: str,
    case_id: str | None,
) -> None:
    path = recorder.path_for(viewport, state)
    locator.screenshot(
        path=str(path),
        type="webp",
        quality=55,
        animations="disabled",
    )
    recorder.record(
        path,
        viewport=viewport,
        state=state,
        journey=journey,
        mode=mode,
        case_id=case_id,
    )
    assert 0 < path.stat().st_size <= 512 * 1024


@pytest.mark.parametrize(
    "viewport",
    VIEWPORTS,
    ids=[viewport.name for viewport in VIEWPORTS],
)
def test_capture_documentary_reference_set(
    browser_session: BrowserSession,
    reference_recorder: ReferenceRecorder,
    viewport: Viewport,
) -> None:
    page = browser_session.page

    goto_portfolio(page, "public")
    _capture(
        page.locator("section.compact-section"),
        reference_recorder,
        viewport,
        "journey-a-portfolio-public",
        journey="A",
        mode="public",
        case_id=None,
    )
    select_mode(page, "simulated")
    _capture(
        page.locator("section.compact-section"),
        reference_recorder,
        viewport,
        "journey-a-portfolio-simulated",
        journey="A",
        mode="simulated",
        case_id=None,
    )

    workspace_states = (
        (STEEL, "public", "journey-b-steel-public-workspace", "B"),
        (STEEL, "simulated", "journey-c-steel-simulated-workspace", "C"),
        (
            POLYPROPYLENE,
            "public",
            "journey-d-polypropylene-public-workspace",
            "D",
        ),
        (
            POLYPROPYLENE,
            "simulated",
            "journey-d-polypropylene-simulated-workspace",
            "D",
        ),
    )
    for case, mode, state, journey in workspace_states:
        goto_portfolio(page, mode)
        select_case(page, case, mode)
        _capture(
            page.locator("#workspace"),
            reference_recorder,
            viewport,
            state,
            journey=journey,
            mode=mode,
            case_id=case.id,
        )

    dossier_states = (
        (STEEL, "public", "journey-e-steel-public-dossier"),
        (STEEL, "simulated", "journey-e-steel-simulated-dossier"),
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
    for case, mode, state in dossier_states:
        goto_portfolio(page, mode)
        select_case(page, case, mode)
        popup = open_dossier_popup(page, case, mode)
        _capture(
            popup.locator("main.page"),
            reference_recorder,
            viewport,
            state,
            journey="E",
            mode=mode,
            case_id=case.id,
        )
        popup.close()
