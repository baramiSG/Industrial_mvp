from __future__ import annotations

import re
from urllib.parse import urlsplit

from playwright.sync_api import Page, Response, expect

from browser_tests.harness import (
    ASSERTION_TIMEOUT_MS,
    CASES,
    Case,
    Locale,
    Mode,
)
from browser_tests.parity_grammar import (
    LATIN_PROSE,
    LATIN_RUN,
    classify_island,
    label_leaks,
    normalize,
)
from ior_mvp.config import (
    decision_narratives_config,
    ui_strings_bundle,
)


def locale_bundle(locale: Locale) -> dict:
    return ui_strings_bundle(locale.code)


def _response_matches(response: Response, expected: str) -> bool:
    parsed = urlsplit(response.url)
    return f"{parsed.path}?{parsed.query}" == expected


def wait_for_document(page: Page, locale: Locale) -> None:
    root = page.locator("html")
    expect(root).to_have_attribute("lang", locale.code)
    expect(root).to_have_attribute("dir", locale.direction)
    body = page.locator("body")
    if body.get_attribute("aria-busy") is not None:
        expect(body).to_have_attribute("aria-busy", "false")


def wait_for_workspace(
    page: Page,
    case: Case,
    mode: Mode,
    locale: Locale,
) -> None:
    wait_for_document(page, locale)
    expect(page.locator("#workspace-title")).to_contain_text(
        case.hs6,
        timeout=ASSERTION_TIMEOUT_MS,
    )
    expect(page.locator("#opportunity-select")).to_have_value(case.id)
    banner = page.locator(".integrity-banner")
    expect(banner).to_be_visible()
    state_chips = banner.locator(".state-chip")
    expect(state_chips).to_have_count(2 if mode == "simulated" else 1)
    expect(state_chips.nth(0)).to_contain_text(case.real_state)
    expect(state_chips.nth(-1)).to_contain_text(case.active_state(mode))
    expect(page.locator(f'[data-dossier-html="{case.id}"]')).to_be_visible()
    expect(page.locator(f'[data-copy-json="{case.id}"]')).to_be_visible()
    labels = locale_bundle(locale)["synthetic_labels"]
    if mode == "simulated":
        for label in labels.values():
            expect(banner).to_contain_text(label)
    else:
        for label in labels.values():
            expect(banner).not_to_contain_text(label)


def wait_for_portfolio(
    page: Page,
    mode: Mode,
    locale: Locale,
) -> None:
    expect(page.locator("[data-open-id]")).to_have_count(
        len(CASES),
        timeout=ASSERTION_TIMEOUT_MS,
    )
    expect(page.locator("#opportunity-select option")).to_have_count(
        len(CASES)
    )
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))
    selected = page.locator("#opportunity-select").input_value()
    case = next(case for case in CASES if case.id == selected)
    wait_for_workspace(page, case, mode, locale)


def select_mode(
    page: Page,
    mode: Mode,
    locale: Locale,
) -> None:
    button = page.locator(f'.mode-button[data-mode="{mode}"]')
    if "active" in (button.get_attribute("class") or "").split():
        wait_for_portfolio(page, mode, locale)
        return
    selected = page.locator("#opportunity-select").input_value()
    case = next(case for case in CASES if case.id == selected)
    expected_list = f"/api/opportunities?mode={mode}"
    with page.expect_response(
        lambda response: _response_matches(response, expected_list)
    ):
        button.click()
    wait_for_portfolio(page, mode, locale)
    wait_for_workspace(page, case, mode, locale)


def goto_portfolio(
    page: Page,
    mode: Mode,
    locale: Locale,
) -> None:
    page.goto(
        f"/?locale={locale.code}",
        wait_until="domcontentloaded",
    )
    wait_for_portfolio(page, "public", locale)
    if mode != "public":
        select_mode(page, mode, locale)


def _select_case_once(
    page: Page,
    case: Case,
    mode: Mode,
    locale: Locale,
) -> tuple[Response, Response]:
    detail_path = f"/api/opportunities/{case.id}?mode={mode}"
    manifest_path = (
        f"/api/opportunities/{case.id}/ui-manifest?mode={mode}"
    )
    with page.expect_response(
        lambda response: _response_matches(response, detail_path)
    ) as detail_info:
        with page.expect_response(
            lambda response: _response_matches(response, manifest_path)
        ) as manifest_info:
            page.locator("#opportunity-select").select_option(case.id)
    wait_for_workspace(page, case, mode, locale)
    return detail_info.value, manifest_info.value


def select_case(
    page: Page,
    case: Case,
    mode: Mode,
    locale: Locale,
) -> tuple[Response, Response]:
    if page.locator("#opportunity-select").input_value() == case.id:
        other = next(item for item in CASES if item.id != case.id)
        _select_case_once(page, other, mode, locale)
    return _select_case_once(page, case, mode, locale)


def open_case_card(
    page: Page,
    case: Case,
    mode: Mode,
    locale: Locale,
) -> None:
    page.locator(f'[data-open-id="{case.id}"]').click()
    wait_for_workspace(page, case, mode, locale)


def open_dossier_popup(
    page: Page,
    case: Case,
    mode: Mode,
    locale: Locale,
) -> Page:
    with page.expect_popup() as popup_info:
        page.locator(f'[data-dossier-html="{case.id}"]').click()
    popup = popup_info.value
    expect(popup.locator("main.page")).to_be_visible(
        timeout=ASSERTION_TIMEOUT_MS
    )
    expect(popup.locator(".meta")).to_contain_text(case.id)
    expect(popup.locator(".meta")).to_contain_text(
        locale_bundle(locale)["strings"][
            "mode.simulated" if mode == "simulated" else "mode.public"
        ]
    )
    wait_for_document(popup, locale)
    return popup


def wait_for_screening_summary(
    page: Page,
    locale: Locale,
) -> None:
    wait_for_document(page, locale)
    expect(page.locator("#screening-view .screening-summary")).to_be_visible(
        timeout=ASSERTION_TIMEOUT_MS
    )
    expect(page.locator("#screening-view [data-queue-id]")).to_have_count(5)
    expect(page.locator("#screening-evidence h3")).to_be_visible()


def open_screening(page: Page, locale: Locale) -> None:
    page.locator('.nav-item[data-target="screening"]').click()
    wait_for_screening_summary(page, locale)
    expect(page.locator("#screening")).to_be_in_viewport()


def open_queue(
    page: Page,
    queue_id: str,
    locale: Locale,
    offset: int = 0,
) -> Response:
    expected = (
        f"/api/screening/queues/{queue_id}"
        f"?offset={offset}&limit=50"
    )
    with page.expect_response(
        lambda response: _response_matches(response, expected)
    ) as response_info:
        if offset == 0:
            page.locator(f'[data-queue-id="{queue_id}"]').click()
        else:
            page.locator("[data-screening-page='next']").click()
    response = response_info.value
    expect(page.locator("#screening-view .screening-queue")).to_be_visible()
    return response


def first_queue_entry_hs6(page: Page) -> str:
    value = page.locator("#screening-view [data-hs6]").first.get_attribute(
        "data-hs6"
    )
    if not value:
        raise AssertionError("screening queue has no first HS6 entry")
    return value


def open_record(
    page: Page,
    hs6: str,
    locale: Locale,
) -> Response:
    expected = f"/api/screening/records/{hs6}?"
    with page.expect_response(
        lambda response: _response_matches(response, expected)
    ) as response_info:
        page.locator(f'[data-hs6="{hs6}"]').click()
    response = response_info.value
    expect(page.locator("#screening-view .screening-record")).to_be_visible()
    wait_for_document(page, locale)
    return response


def screening_back(
    page: Page,
    target: str,
    locale: Locale,
) -> None:
    page.locator(f'[data-screening-back="{target}"]').click()
    selector = (
        ".screening-summary"
        if target == "summary"
        else ".screening-queue"
    )
    expect(page.locator(f"#screening-view {selector}")).to_be_visible()
    wait_for_document(page, locale)


def _english_catalogue_values() -> set[str]:
    return set(ui_strings_bundle("en")["strings"].values()) | set(
        decision_narratives_config()["templates"]["en"].values()
    )


def arabic_parity_report(page: Page, selector: str) -> dict:
    raw = page.evaluate(
        """(selector) => {
          const container = document.querySelector(selector);
          if (!container) throw new Error(`PARITY_CONTAINER_MISSING:${selector}`);
          const hasLtrAncestor = (node) => {
            let current = node.parentElement;
            while (current && current !== container) {
              if (current.getAttribute("dir") === "ltr") return true;
              current = current.parentElement;
            }
            return false;
          };
          const walker = document.createTreeWalker(
            container,
            NodeFilter.SHOW_TEXT
          );
          const outsideTexts = [];
          while (walker.nextNode()) {
            if (!hasLtrAncestor(walker.currentNode)) {
              outsideTexts.push(walker.currentNode.nodeValue || "");
            }
          }
          const islands = Array.from(
            container.querySelectorAll('[dir="ltr"]')
          ).filter((node) => {
            let current = node.parentElement;
            while (current && current !== container) {
              if (current.getAttribute("dir") === "ltr") return false;
              current = current.parentElement;
            }
            return true;
          }).map((node) => {
            let sibling = node.nextElementSibling;
            while (sibling && !sibling.classList.contains(
              "source-language-caption"
            )) sibling = sibling.nextElementSibling;
            const parentCaption = node.parentElement?.querySelector(
              ":scope > .source-language-caption"
            );
            return {
              text: node.textContent || "",
              sourceCandidate: (
                node.matches(
                  '[dir="ltr"][lang="en"].source-language-island'
                )
              ),
              caption: (
                sibling?.textContent || parentCaption?.textContent || ""
              ),
            };
          });
          return {outsideTexts, islands};
        }""",
        selector,
    )
    outside = [normalize(value) for value in raw["outsideTexts"]]
    outside = [value for value in outside if value]
    latin_prose_runs = [
        match.group(0)
        for value in outside
        for match in LATIN_PROSE.finditer(value)
    ]
    latin_runs = [
        match.group(0)
        for value in outside
        for match in LATIN_RUN.finditer(value)
    ]
    islands_by_class: dict[str, int] = {}
    island_failures: list[dict[str, str]] = []
    classified: list[dict[str, str]] = []
    source_spans = 0
    caption = ui_strings_bundle("ar")["strings"][
        "source_language.caption"
    ]
    for raw_island in raw["islands"]:
        text = normalize(raw_island["text"])
        if (
            raw_island["sourceCandidate"]
            and normalize(raw_island["caption"]) == normalize(caption)
        ):
            source_spans += 1
            continue
        classification = classify_island(text)
        if classification in {"empty", "unclassified"}:
            island_failures.append(
                {"text": text, "reason": classification}
            )
            continue
        islands_by_class[classification] = (
            islands_by_class.get(classification, 0) + 1
        )
        classified.append({"text": text, "class": classification})
    return {
        "islands_by_class": islands_by_class,
        "island_failures": island_failures,
        "source_spans": source_spans,
        "latin_prose_runs": latin_prose_runs,
        "latin_runs": latin_runs,
        "arabic_present": any(
            re.search(r"[\u0600-\u06ff]", value)
            for value in outside
        ),
        "label_leaks": label_leaks(
            classified,
            _english_catalogue_values(),
        ),
    }


def assert_arabic_parity(
    report: dict,
    expected_source_spans: int,
) -> None:
    assert report["island_failures"] == [], report
    assert report["latin_prose_runs"] == [], report
    assert report["latin_runs"] == [], report
    assert report["arabic_present"] is True, report
    assert report["source_spans"] == expected_source_spans, report
    assert report["label_leaks"] == [], report
