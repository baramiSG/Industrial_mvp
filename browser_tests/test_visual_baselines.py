from __future__ import annotations

from itertools import product
from typing import Any

import pytest

from browser_tests.executive_pages import goto_executive
from browser_tests.graph_pages import install_graph_routes, prepare_graph_capture
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


def _executive_scene_payload(page: Any, case: Any, locale: Locale, step: str, mode: str) -> tuple[str, list[Any]]:
    """Bind complete scene children to actual API context before viewport proof."""
    from urllib.parse import parse_qs, urlsplit
    from playwright.sync_api import expect
    from browser_tests.executive_pages import api_json

    targets = {
        "SIGNAL": '[data-active-step="SIGNAL"] .workspace-card',
        "ROUTE_COMPARISON": '[data-active-step="ROUTE_COMPARISON"] [data-route-branch="SIMULATED"]',
        "MISSING_MINISTRY_FACTS": '[data-active-step="MISSING_MINISTRY_FACTS"] .executive-datasets',
        "PUBLIC_CONCLUSION": '[data-active-step="PUBLIC_CONCLUSION"] > .executive-public',
    }
    assert step in targets and mode == ("simulated" if step == "ROUTE_COMPARISON" else "public")
    assert case.id == (POLYPROPYLENE.id if step == "PUBLIC_CONCLUSION" else STEEL.id)
    query = parse_qs(urlsplit(page.url).query)
    assert (query["opportunity"], query["locale"], query["step"]) == ([case.id], [locale.code], [step])
    expect(page.locator("[data-executive-ready]")).to_have_attribute("data-executive-ready", case.id)
    expect(page.locator("[data-active-step]")).to_have_attribute("data-active-step", step)
    expect(page.locator("html")).to_have_attribute("lang", locale.code)
    expect(page.locator("html")).to_have_attribute("dir", locale.direction)
    detail = api_json(page, f"/api/executive/opportunities/{case.id}")
    real = api_json(page, f"/api/opportunities/{case.id}?mode=public")
    strings = api_json(page, f"/api/ui-strings/{locale.code}")["strings"]
    expected = ("REJECT", 0) if case.id == POLYPROPYLENE.id else ("INVESTIGATE", None)
    assert (real["real_decision"]["state"], real["real_decision"]["route_code"]) == expected
    assert (detail["decisions"]["public"]["state"], detail["decisions"]["public"]["route_code"]) == expected
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-state", expected[0])
    expect(page.locator('[data-branch="PUBLIC"]')).to_have_attribute("data-route", str(expected[1]) if expected[1] is not None else "NOT_CALCULABLE")
    target = page.locator(targets[step])
    expect(target).to_have_count(1)
    if step == "SIGNAL":
        expect(target.locator("h3")).to_have_text(strings["trade.title"])
        expect(target.locator(".exec-chip")).to_have_text(strings["trade.boundary"])
        chart = target.locator("svg")
        expect(chart).to_have_attribute("aria-label", strings["trade.aria"])
        assert chart.locator(".chart-value").get_attribute("d")
        assert chart.locator(".chart-point-value").count() == sum(isinstance(row["imports_usd_m"], (int, float)) for row in real["trade"])
        assert chart.locator(".chart-label").all_text_contents() == [str(row["year"]) for row in sorted(real["trade"], key=lambda row: row["year"])]
        required = [target.locator(".card-header"), chart, target.locator(".chart-legend")]
    elif step == "ROUTE_COMPARISON":
        simulated = api_json(page, f"/api/opportunities/{case.id}?mode=simulated")
        decision = detail["decisions"]["simulated"]
        assert (decision["state"], decision["route_code"]) == ("ADVANCE", 5)
        assert (simulated["simulation_decision"]["state"], simulated["simulation_decision"]["route_code"]) == ("ADVANCE", 5)
        expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-state", "ADVANCE")
        expect(page.locator('[data-branch="SIMULATED"]')).to_have_attribute("data-route", "5")
        expect(target.locator(":scope > h3")).to_have_text(strings["executive.ui.simulated"])
        for language, text in decision["display_labels"].items():
            expect(target.locator(f'.synthetic-labels > [lang="{language}"]')).to_have_text(text)
        rows = target.locator("[data-route-row]")
        assert rows.evaluate_all("nodes=>nodes.map(node=>Number(node.dataset.routeRow))") == list(range(9))
        assert [row["route_code"] for row in simulated["simulation_decision"]["route_hypotheses"]] == list(range(9))
        for index, row in enumerate(simulated["simulation_decision"]["route_hypotheses"]):
            expect(rows.nth(index).locator("h4")).to_have_text(strings[f'executive.route.{row["route_code"]}'])
            expect(rows.nth(index).locator(".executive-status")).to_have_text(strings['executive.status.' + row["status"].lower()])
        required = [target.locator(":scope > h3"), target.locator(".synthetic-labels"), rows.nth(0).locator(":scope > div"), rows.nth(1).locator(":scope > div")]
    elif step == "MISSING_MINISTRY_FACTS":
        summary = api_json(page, "/api/executive/summary")
        expect(target.locator(":scope > h3")).to_have_text(strings["executive.ui.missing"])
        expect(target.locator(":scope > p")).to_have_text(strings["executive.ui.dataset_note"])
        required = [target.locator(":scope > h3"), target.locator(":scope > p")]
        for row in summary["public_dataset_unlocks"][:2]:
            card = target.locator(f'[data-dataset="{row["dataset_kind"]}"]')
            expect(card.locator("h4")).to_have_text(strings['executive.dataset.' + row["dataset_kind"].lower()])
            assert card.locator(":scope > dl > dt").all_text_contents() == [strings["executive.ui.loaded_cases"], strings["executive.ui.screening_records"]]
            assert card.locator(":scope > dl > dd").all_text_contents() == [str(row["loaded_case_count"]), str(row["screening_record_count"])]
            required.append(card)
    else:
        narrative = real["real_decision"]["localized_narrative"][locale.code]
        expect(target.locator(":scope > h3")).to_have_text(narrative["headline"]["text"])
        paragraphs = target.locator(":scope > p")
        expect(paragraphs.nth(0)).to_have_text(narrative["rationale"]["text"])
        expect(paragraphs.nth(1)).to_have_text(strings["executive.ui.public_boundary"])
        expect(target.locator(":scope > h4").first).to_have_text(strings["executive.ui.hypothesis"])
        expect(paragraphs.nth(2)).to_have_text("0")
        expect(paragraphs.nth(3)).to_have_text(narrative["route_label"]["text"])
        required = [target.locator(":scope > h3"), target.locator(":scope > h4").first, *paragraphs.all()]
    return targets[step], required


def _executive_capture_boxes(required: list[Any]) -> list[dict]:
    return [node.evaluate("node=>{const r=node.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom,viewportWidth:innerWidth,viewportHeight:innerHeight}}") for node in required]


def _assert_executive_scene_visible(required: list[Any]) -> list[dict]:
    boxes = _executive_capture_boxes(required)
    for index, box in enumerate(boxes):
        assert box["width"] > 0 and box["height"] > 0, (index, box)
        assert box["x"] >= 0 and box["y"] >= 0 and box["right"] <= box["viewportWidth"] and box["bottom"] <= box["viewportHeight"], (index, box)
    return boxes


def _prepare_executive_capture(page: Any, case: Any, locale: Locale, step: str, mode: str) -> list[Any]:
    target, required = _executive_scene_payload(page, case, locale, step, mode)
    page.locator(target).evaluate("""async node => {
      await document.fonts.ready;
      window.scrollTo({top: Math.floor(node.getBoundingClientRect().top + scrollY), behavior: 'instant'});
      let previous = null, stable = 0;
      for (let frame = 0; frame < 60 && stable < 3; frame++) {
        await new Promise(requestAnimationFrame);
        const rect = node.getBoundingClientRect();
        const current = JSON.stringify([scrollX, scrollY, rect.x, rect.y, rect.width, rect.height]);
        stable = current === previous ? stable + 1 : 0; previous = current;
      }
      if (stable < 3) throw new Error('EXECUTIVE_CAPTURE_NOT_SETTLED');
    }""")
    _assert_executive_scene_visible(required)
    return required


def _check_lossless_encoder(tmp_path: Any) -> None:
    from PIL import Image
    from browser_tests.visual_baselines import normalized_rgb, write_lossless_webp
    rgb = Image.new("RGB", (257, 129))
    rgb.putdata([((x * y) % 256, (x // 5 * 17 + y * 11) % 256, (x ^ y) % 256)
                 for y in range(129) for x in range(257)])
    rgba = rgb.convert("RGBA")
    rgba.putalpha(Image.frombytes("L", rgb.size, bytes((i * 37) % 256 for i in range(257 * 129))))
    palette = rgb.quantize(colors=32)
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, source in (("rgb", rgb), ("rgba", rgba), ("palette", palette)):
        actual, repeat, reference = [tmp_path / f"{name}-{kind}.webp" for kind in ("actual", "repeat", "reference")]
        normalized = normalized_rgb(source)
        write_lossless_webp(source, actual)
        write_lossless_webp(source, repeat)
        normalized.save(reference, format="WEBP", lossless=True, quality=100, method=6, exact=True)
        assert actual.read_bytes()[12:16] == b"VP8L"
        with Image.open(actual) as decoded:
            assert decoded.mode == "RGB"
            assert decoded.size == source.size
            assert decoded.tobytes() == normalized.tobytes()
        assert actual.read_bytes() == repeat.read_bytes()
        assert actual.read_bytes() == reference.read_bytes()
    effort80 = tmp_path / "rgb-effort80.webp"
    rgb.save(effort80, format="WEBP", lossless=True, quality=80, method=6, exact=True)
    assert effort80.read_bytes() != (tmp_path / "rgb-reference.webp").read_bytes()


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
    tmp_path: Any,
    locale: Locale,
    viewport: Viewport,
) -> None:
    _check_lossless_encoder(tmp_path)
    page = browser_session.page
    install_graph_routes(page)
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

    goto_portfolio(page, "public", locale)
    page.locator("#selection details").evaluate_all(
        "elements => elements.forEach(element => { element.open = true; })"
    )
    _anchor(page, "#selection")
    visual_session.capture(
        page,
        locale=locale.code,
        viewport=viewport.name,
        screen="journey-h-selection-exclusions",
        case_id=None,
        mode="public",
    )

    graph_states = (
        (STEEL, "public", "adjacency", "journey-i-graph-adjacency"),
        (STEEL, "simulated", "route_blocking", "journey-i-graph-route-blocking"),
        (
            next(case for case in CASES if case.id == "SAU-H6-760711"),
            "simulated",
            "shared_enabler",
            "journey-i-graph-shared-enabler",
        ),
        (STEEL, "public", "evidence_to_change", "journey-i-graph-evidence-to-change"),
    )
    for case, mode, view_id, screen in graph_states:
        goto_portfolio(page, mode, locale)
        select_case(page, case, mode, locale)
        prepare_graph_capture(page, view_id)
        visual_session.capture(
            page,
            locale=locale.code,
            viewport=viewport.name,
            screen=screen,
            case_id=case.id,
            mode=mode,
        )

    executive_states = (
        (STEEL, "SIGNAL", "public", "journey-j-executive-signal-public"),
        (STEEL, "ROUTE_COMPARISON", "simulated", "journey-j-executive-simulated-route"),
        (STEEL, "MISSING_MINISTRY_FACTS", "public", "journey-j-executive-ministry-unlocks"),
        (POLYPROPYLENE, "PUBLIC_CONCLUSION", "public", "journey-j-executive-reject"),
    )
    for case, step, mode, screen in executive_states:
        goto_executive(page, case, locale, step)
        required = _prepare_executive_capture(page, case, locale, step, mode)
        before = _assert_executive_scene_visible(required)
        visual_session.capture(
            page, locale=locale.code, viewport=viewport.name,
            screen=screen, case_id=case.id, mode=mode,
        )
        assert _assert_executive_scene_visible(required) == before
