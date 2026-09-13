from __future__ import annotations

import json
import re
from itertools import product
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import expect

from browser_tests.harness import (
    AR,
    EN,
    CASES,
    LOCALES,
    MODES,
    POLYPROPYLENE,
    STEEL,
    BrowserSession,
    Case,
    Locale,
    Mode,
)
from browser_tests.pages import (
    arabic_parity_report,
    assert_arabic_parity,
    goto_portfolio,
    locale_bundle,
    open_case_card,
    select_case,
    select_mode,
    wait_for_document,
    wait_for_portfolio,
    wait_for_workspace,
)


pytestmark = pytest.mark.e2e
MODE_LOCALES = tuple(product(MODES, LOCALES))
CASE_MODE_LOCALES = tuple(product(MODES, CASES, LOCALES))
NEW_CASE_LOCALES = tuple(product(CASES[2:], LOCALES))
NEW_SIMULATED_UNLOCK_COUNTS = {
    "SAU-H6-721061": 1,
    "SAU-H6-721012": 1,
    "SAU-H6-760711": 1,
    "SAU-H6-760429": 0,
    "SAU-H6-392010": 5,
}


@pytest.mark.parametrize(
    ("mode", "locale"),
    MODE_LOCALES,
    ids=[f"{mode}-{locale.code}" for mode, locale in MODE_LOCALES],
)
def test_portfolio_loads_expected_cases_and_states(
    browser_session: BrowserSession,
    mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)

    expect(page.locator("#kpi-grid .kpi-card")).to_have_count(4)
    expect(page.locator("[data-open-id]")).to_have_count(len(CASES))
    expect(page.locator("#opportunity-select option")).to_have_count(
        len(CASES)
    )
    assert {
        button.get_attribute("data-open-id")
        for button in page.locator("[data-open-id]").all()
    } == {case.id for case in CASES}
    for case in CASES:
        card = page.locator(
            f'[data-open-id="{case.id}"]'
        ).locator("xpath=ancestor::article[1]")
        expect(card).to_contain_text(case.hs6)
        expect(card).to_contain_text(case.real_state)
        expect(card).to_contain_text(case.active_state(mode))
    visible_text = page.locator("body").inner_text()
    assert re.search(r"\b[12][,\u066c]\d{3}\b", visible_text) is None
    for chip in page.locator(".state-chip, .exec-chip, .rule-fire").all():
        words = re.findall(r"[\w-]+", chip.inner_text().casefold())
        assert all(
            current != following
            for current, following in zip(words, words[1:], strict=False)
        ), chip.inner_text()
    strings = locale_bundle(locale)["strings"]
    expect(page.locator("#kpi-grid")).to_contain_text(
        strings["kpi.leakage_label"]
    )
    expect(page.locator("#kpi-grid")).to_contain_text("0")
    portfolio = page.locator("section.compact-section")
    labels = locale_bundle(locale)["synthetic_labels"]
    for label in labels.values():
        if mode == "simulated":
            expect(portfolio).to_contain_text(label)
        else:
            expect(portfolio).not_to_contain_text(label)
    expect(
        page.locator(f'.mode-button[data-mode="{mode}"]')
    ).to_have_class(re.compile(r"\bactive\b"))


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_opportunity_card_opens_selected_workspace(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    open_case_card(page, case, mode, locale)
    wait_for_workspace(page, case, mode, locale)


@pytest.mark.parametrize(
    ("mode", "case", "locale"),
    CASE_MODE_LOCALES,
    ids=[
        f"{mode}-{case.slug}-{locale.code}"
        for mode, case, locale in CASE_MODE_LOCALES
    ],
)
def test_opportunity_select_loads_each_case(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    detail, manifest = select_case(page, case, mode, locale)

    assert (
        f"{urlsplit(detail.url).path}?{urlsplit(detail.url).query}"
        == f"/api/opportunities/{case.id}?mode={mode}"
    )
    assert (
        f"{urlsplit(manifest.url).path}?{urlsplit(manifest.url).query}"
        == f"/api/opportunities/{case.id}/ui-manifest?mode={mode}"
    )
    assert detail.status == manifest.status == 200
    payload = detail.json()
    manifest_payload = manifest.json()
    by_rule = {
        row["rule_id"]: row
        for row in payload["rules"]
        if row.get("synthetic_flag") is not True
    }
    if case == STEEL:
        expected_results = {
            "R3": (
                "External supply is concentrated on the value basis; "
                "quantity concentration is NOT_CALCULABLE."
            ),
            "R4-D": (
                "A source-attributed annual unit-value dispersion summary "
                "supports a descriptive product-mix signal; no cluster or "
                "grade conclusion."
            ),
            "R11": (
                "Gross exports are 0.1144× imports; the configured "
                "generic-capacity warning threshold is not met."
            ),
        }
    elif case == POLYPROPYLENE:
        expected_results = {
            "R3": (
                "Value- and quantity-basis partner concentration are "
                "NOT_CALCULABLE."
            ),
            "R4-D": (
                "A source-attributed annual unit-value dispersion summary "
                "supports a descriptive product-mix signal; no cluster or "
                "grade conclusion."
            ),
        }
    else:
        expected_results = {}
    for rule_id, row in by_rule.items():
        visible = row["localized"][locale.code]["result"]["text"]
        expect(page.locator("#workspace")).to_contain_text(visible)
        expected = expected_results.get(rule_id)
        if expected is not None:
            assert row["result"] == expected
        if locale == EN and expected is not None:
            assert visible == expected

    hero = page.locator(".decision-hero")
    unlocks = page.locator(".unlock-list li")
    if mode == "public":
        narrative = payload["active_decision"][
            "localized_narrative"
        ][locale.code]
        for field in ("headline", "route_label", "rationale"):
            expect(hero).to_contain_text(narrative[field]["text"])
        for field in ("conditions", "kill_conditions"):
            for item in narrative[field]:
                expect(hero).to_contain_text(item["text"])
        expected_unlocks = (
            5
            if case in {STEEL, POLYPROPYLENE}
            else len(narrative["missing_facts"])
        )
        expect(unlocks).to_have_count(expected_unlocks)
        assert [item.inner_text().split(" ", maxsplit=1)[-1] for item in unlocks.all()]
        for item in narrative["missing_facts"]:
            expect(page.locator(".unlock-list")).to_contain_text(
                item["text"]
            )
        assert hero.locator(".source-language-island").count() == 0
        assert (
            page.locator(".unlock-list .source-language-island").count()
            == 0
        )
        if case == STEEL and locale == EN:
            expect(hero).to_contain_text(
                "Brownfield priority to test"
            )
    else:
        decision = payload["simulation_decision"]
        narrative = decision["localized_narrative"][locale.code]
        for field in ("headline", "route_label", "rationale"):
            expect(hero).to_contain_text(narrative[field]["text"])
        for field in ("conditions", "kill_conditions"):
            for item in narrative[field]:
                expect(hero).to_contain_text(item["text"])
        expected_unlocks = (
            5
            if case in {STEEL, POLYPROPYLENE}
            else NEW_SIMULATED_UNLOCK_COUNTS[case.id]
        )
        assert len(decision["missing_facts"]) == expected_unlocks
        expect(unlocks).to_have_count(expected_unlocks)
        unlock_props = next(
            row
            for row in manifest_payload["components"]
            if row["type"] == "data_unlocks"
        )["props"]["localized_missing_facts"][locale.code]
        for item in unlock_props:
            text = item["text"] if isinstance(item, dict) else item
            expect(page.locator(".unlock-list")).to_contain_text(text)
        finding = payload.get("competition", {}).get("finding")
        if finding:
            expect(page.locator("#workspace")).to_contain_text(
                finding
            )
        assert hero.locator(".source-language-island").count() == 0
        if locale == AR:
            assert (
                page.locator(".unlock-list .source-language-island").count()
                == 0
            )
            assert hero.locator(".source-language-caption").count() == 0


@pytest.mark.parametrize(
    ("case", "locale"),
    NEW_CASE_LOCALES,
    ids=[
        f"{case.slug}-{locale.code}"
        for case, locale in NEW_CASE_LOCALES
    ],
)
def test_new_case_view_distinguishes_observed_missing_and_simulated(
    browser_session: BrowserSession,
    case: Case,
    locale: Locale,
) -> None:
    page = browser_session.page
    strings = locale_bundle(locale)["strings"]
    labels = locale_bundle(locale)["synthetic_labels"]

    goto_portfolio(page, "public", locale)
    public_response, _ = select_case(page, case, "public", locale)
    public = public_response.json()
    public_evidence = public["evidence"]
    observed = [
        row
        for row in public_evidence
        if row["status"] in {"observed", "calculated"}
    ]
    assert observed
    assert all(
        row["status"] in {"observed", "calculated", "unresolved"}
        and row["evidence_class"] in {"B", "C"}
        and row["synthetic_flag"] is False
        for row in public_evidence
    )
    expect(page.locator("#workspace")).to_contain_text(observed[0]["title"])
    expect(page.locator("#workspace")).to_contain_text(
        strings["common.unavailable"]
    )
    assert public["data_unlocks"]
    expect(page.locator(".unlock-list li")).to_have_count(
        len(public["data_unlocks"])
    )
    for label in labels.values():
        expect(page.locator("#workspace")).not_to_contain_text(label)

    if case.id == "SAU-H6-721061":
        partner_detail = public["partner_detail"]
        assert partner_detail["state"] in {
            "PARTNER_DETAIL_MISSING",
            "PARTNER_DETAIL_OBSERVED",
        }
        assert partner_detail["state"] != "PARTNER_TRADE_OBSERVED_ZERO"
        if partner_detail["state"] == "PARTNER_DETAIL_MISSING":
            note = strings["metric.hhi_partner_detail_missing"].format(
                reason=partner_detail["reason"]
            )
            expect(page.locator("#workspace")).to_contain_text(note)
            assert public["supplier_metrics"] is None
        else:
            assert partner_detail["observed_partner_rows"] > 0
            expect(page.locator("#workspace")).not_to_contain_text(
                strings["metric.hhi_partner_detail_missing"].split(
                    "{reason}",
                    maxsplit=1,
                )[0].strip()
            )

    goto_portfolio(page, "simulated", locale)
    simulated_response, _ = select_case(
        page,
        case,
        "simulated",
        locale,
    )
    simulated = simulated_response.json()
    scenario = simulated["simulation_scenario"]
    assert scenario["scenario_id"].startswith("SYN-MINISTRY-")
    assert scenario["seed_basis"]
    assert simulated["real_decision"]["state"] == "INVESTIGATE"
    assert simulated["simulation_decision"]["state"] == (
        case.simulated_active_state
    )
    synthetic_evidence = [
        row for row in simulated["evidence"] if row["synthetic_flag"] is True
    ]
    synthetic_rules = [
        row
        for row in simulated["rules"]
        if row.get("synthetic_flag") is True
    ]
    assert synthetic_evidence and synthetic_rules
    assert all(
        row["evidence_class"] == "D"
        and row["source"] == "DEMO_GENERATOR"
        for row in synthetic_evidence
    )
    evidence_table = page.locator("#workspace .evidence-table")
    expect(evidence_table).to_contain_text("DEMO_GENERATOR")
    expect(evidence_table).to_contain_text("D")
    for label in labels.values():
        expect(page.locator("#workspace")).to_contain_text(label)


@pytest.mark.parametrize(
    ("mode", "locale"),
    MODE_LOCALES,
    ids=[f"{mode}-{locale.code}" for mode, locale in MODE_LOCALES],
)
def test_hero_opens_steel_case_preserving_mode(
    browser_session: BrowserSession,
    mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, locale)
    select_case(page, POLYPROPYLENE, mode, locale)
    page.locator("#open-first-case").click()
    wait_for_workspace(page, STEEL, mode, locale)


@pytest.mark.parametrize(
    ("start_mode", "end_mode", "locale"),
    tuple(
        (start, end, locale)
        for start, end in (
            ("public", "simulated"),
            ("simulated", "public"),
        )
        for locale in LOCALES
    ),
    ids=[
        f"{start}-to-{end}-{locale.code}"
        for start, end in (
            ("public", "simulated"),
            ("simulated", "public"),
        )
        for locale in LOCALES
    ],
)
def test_mode_switch_preserves_selected_case(
    browser_session: BrowserSession,
    start_mode: Mode,
    end_mode: Mode,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, start_mode, locale)
    select_case(page, POLYPROPYLENE, start_mode, locale)
    select_mode(page, end_mode, locale)
    wait_for_workspace(page, POLYPROPYLENE, end_mode, locale)


@pytest.mark.parametrize(
    "locale",
    LOCALES,
    ids=[locale.code for locale in LOCALES],
)
def test_navigation_and_methodology_action_reach_sections(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    for section_id in (
        "overview",
        "workspace",
        "methodology",
        "extraction",
        "governance",
        "screening",
    ):
        button = page.locator(
            f'.nav-item[data-target="{section_id}"]'
        )
        button.click()
        expect(button).to_have_class(re.compile(r"\bactive\b"))
        expect(page.locator(f"#{section_id}")).to_be_in_viewport()
    page.locator('.nav-item[data-target="overview"]').click()
    page.locator("#view-methodology").click()
    expect(page.locator("#methodology")).to_be_in_viewport()


@pytest.mark.parametrize(
    ("mode", "case"),
    tuple(product(MODES, CASES)),
    ids=[
        f"{mode}-{case.slug}"
        for mode, case in product(MODES, CASES)
    ],
)
def test_workspace_and_methodology_ledgers_have_no_english_catalogue_prose_in_arabic(
    browser_session: BrowserSession,
    mode: Mode,
    case: Case,
) -> None:
    page = browser_session.page
    goto_portfolio(page, mode, AR)
    detail, _ = select_case(page, case, mode, AR)
    payload = detail.json()

    workspace = page.locator("#workspace .rule-table")
    methodology = page.locator("#methodology .rule-table")
    for row in payload["rules"]:
        localized = row["localized"]["ar"]
        for field in ("name", "result", "decision_effect"):
            expect(workspace).to_contain_text(localized[field]["text"])
        expect(methodology).to_contain_text(localized["name"]["text"])
        expect(methodology).to_contain_text(localized["result"]["text"])

    for container, selector in (
        ("workspace", "#workspace .rule-table"),
        ("methodology", "#methodology .rule-table"),
    ):
        report = arabic_parity_report(page, selector)
        assert_arabic_parity(report, expected_source_spans=0)
        output = (
            browser_session.artifact_dir
            / f"parity-{container}-{case.slug}-{mode}-ar.json"
        )
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )


@pytest.mark.parametrize(
    ("locale", "target"),
    ((EN, AR), (AR, EN)),
    ids=("en-to-ar", "ar-to-en"),
)
def test_locale_switch_updates_document_url_storage_and_preserves_state(
    browser_session: BrowserSession,
    locale: Locale,
    target: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "simulated", locale)
    select_case(page, POLYPROPYLENE, "simulated", locale)

    page.locator("#locale-switch").click()
    wait_for_workspace(page, POLYPROPYLENE, "simulated", target)
    assert parse_qs(urlsplit(page.url).query)["locale"] == [target.code]
    storage = page.evaluate(
        "() => Object.fromEntries(Object.entries(localStorage))"
    )
    assert storage == {"ior.locale": target.code}
    strings = locale_bundle(target)["strings"]
    expect(page.locator('[data-target="overview"]')).to_contain_text(
        strings["nav.overview"]
    )

    page.reload(wait_until="domcontentloaded")
    wait_for_portfolio(page, "public", target)
    select_mode(page, "simulated", target)
    select_case(page, POLYPROPYLENE, "simulated", target)
    page.evaluate(
        """(code) => {
          const url = new URL(location.href);
          url.searchParams.set("locale", code);
          history.pushState({}, "", url);
          dispatchEvent(new PopStateEvent("popstate"));
        }""",
        locale.code,
    )
    wait_for_document(page, locale)
    wait_for_workspace(page, POLYPROPYLENE, "simulated", locale)
