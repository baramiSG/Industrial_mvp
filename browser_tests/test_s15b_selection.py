from __future__ import annotations

import hashlib
import importlib.metadata
import io
import json
import os
import re
from pathlib import Path

import pytest
from PIL import Image, ImageChops
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import expect

from browser_tests.harness import (
    DESKTOP,
    LOCALES,
    TABLET,
    BrowserSession,
    Locale,
    start_app_server,
    stop_app_server,
)
from browser_tests.pages import (
    first_queue_entry_hs6,
    goto_portfolio,
    locale_bundle,
    open_queue,
    open_record,
    open_screening,
)
from browser_tests.test_visual_baselines import _anchor, _anchor_screening
from browser_tests.visual_baselines import LAUNCH_FLAGS, validate_manifest
from scripts.s15b_review_checks import (
    ReviewCheckError,
    _visual_drift,
    check_visual_phase_drift,
    phase_expected_state,
    phase_read_rgb,
    phase_record_problems,
    registered_metrics,
)


pytestmark = pytest.mark.e2e


def _inspection_rect(page, selector: str) -> list[int] | None:
    locator = page.locator(selector)
    if locator.count() == 0:
        return None
    return locator.first.evaluate(
        """node => {
          const rect = node.getBoundingClientRect();
          const clipped = [
            Math.max(0, Math.floor(rect.left)),
            Math.max(0, Math.floor(rect.top)),
            Math.min(innerWidth, Math.ceil(rect.right)),
            Math.min(innerHeight, Math.ceil(rect.bottom)),
          ];
          return clipped[0] < clipped[2] && clipped[1] < clipped[3]
            ? clipped
            : null;
        }"""
    )


def _inspection_open(page, locale: Locale) -> None:
    page.goto(f"/?locale={locale.code}", wait_until="domcontentloaded")
    expect(page.locator("body")).to_have_attribute("aria-busy", "false")


def _settle_workspace(page) -> None:
    page.locator("#workspace").evaluate(
        """async node => {
          await document.fonts.ready;
          let previous = null;
          let stable = 0;
          for (let frame = 0; frame < 60 && stable < 3; frame += 1) {
            await new Promise(requestAnimationFrame);
            const rect = node.getBoundingClientRect();
            const current = [rect.top, rect.left, scrollY];
            stable = previous && current.every(
              (value, index) => Math.abs(value - previous[index]) <= 0.5
            ) ? stable + 1 : 0;
            previous = current;
          }
          if (stable < 3 || document.fonts.status !== "loaded") {
            throw new Error("WORKSPACE_LAYOUT_NOT_SETTLED");
          }
        }"""
    )


def _workspace_layout_snapshot(page) -> dict:
    return page.locator("#workspace").evaluate(
        """async node => {
          const digest = async value => {
            const bytes = new TextEncoder().encode(value);
            const hash = await crypto.subtle.digest("SHA-256", bytes);
            return Array.from(new Uint8Array(hash))
              .map(item => item.toString(16).padStart(2, "0"))
              .join("");
          };
          const values = target => {
            const rect = target.getBoundingClientRect();
            return {
              bottom: rect.bottom,
              height: rect.height,
              left: rect.left,
              right: rect.right,
              top: rect.top,
              width: rect.width,
            };
          };
          const style = getComputedStyle(node);
          const html = node.innerHTML;
          const text = node.innerText;
          const normalize = value => value
            .replaceAll("1.3.0", "UI_VERSION")
            .replaceAll("1.4.0", "UI_VERSION");
          const workspace = values(node);
          return {
            absolute_workspace_top: workspace.top + scrollY,
            authority: values(document.querySelector(".integrity-authority")),
            device_pixel_ratio: devicePixelRatio,
            document_scroll_height: document.documentElement.scrollHeight,
            font_family: style.fontFamily,
            font_size: style.fontSize,
            font_status: document.fonts.status,
            html_sha256: await digest(html),
            inner_height: innerHeight,
            inner_width: innerWidth,
            max_scroll_y: document.documentElement.scrollHeight - innerHeight,
            normalized_html_sha256: await digest(normalize(html)),
            normalized_text: normalize(text),
            normalized_text_sha256: await digest(normalize(text)),
            scroll_margin_block_start: style.scrollMarginBlockStart,
            scroll_y: scrollY,
            text_sha256: await digest(text),
            topbar: values(document.querySelector(".topbar")),
            workspace,
          };
        }"""
    )


def _capture_existing_inspection(
    page,
    root: Path,
    locale: Locale,
    side: str,
    version: str,
) -> dict:
    _inspection_open(page, locale)
    _anchor(page, "section.compact-section")
    portfolio = root / f"{side}-portfolio-public.png"
    page.screenshot(path=portfolio, animations="disabled", caret="hide")
    portfolio_rects = {
        name: _inspection_rect(page, selector)
        for name, selector in {
            "chip": '[data-i18n="portfolio.chip"]',
            "kpis": "#kpi-grid",
            "cards": "#opportunity-grid",
        }.items()
    }

    page.locator("#opportunity-select").select_option("SAU-H0-721049")
    expect(page.locator("#workspace-title")).to_contain_text("721049")
    _anchor(page, "#workspace")
    workspace = root / f"{side}-steel-public-workspace.png"
    page.screenshot(path=workspace, animations="disabled", caret="hide")
    workspace_rect = _inspection_rect(page, ".integrity-authority")

    dossier = page.context.new_page()
    dossier.goto(
        "/api/opportunities/SAU-H0-721049/dossier.html"
        f"?mode=public&locale={locale.code}",
        wait_until="domcontentloaded",
    )
    expect(dossier.locator("main.page")).to_be_visible()
    dossier_path = root / f"{side}-steel-public-dossier.png"
    dossier.screenshot(path=dossier_path, animations="disabled", caret="hide")
    dossier_rect = _inspection_rect(
        dossier,
        f'p.small:has-text("{version}")',
    )
    dossier.close()

    _inspection_open(page, locale)
    open_screening(page, locale)
    _anchor_screening(page)
    screening = root / f"{side}-screening-summary.png"
    page.screenshot(path=screening, animations="disabled", caret="hide")
    screening_rect = _inspection_rect(
        page,
        f'#screening :text("{version}")',
    )
    return {
        "portfolio": {
            "screenshot": str(portfolio),
            "rectangles": portfolio_rects,
        },
        "workspace": {
            "screenshot": str(workspace),
            "authority_rectangle": workspace_rect,
        },
        "dossier": {
            "screenshot": str(dossier_path),
            "authority_rectangle": dossier_rect,
        },
        "screening": {
            "screenshot": str(screening),
            "catalogue_rectangle": screening_rect,
        },
    }


def _capture_new_inspection(page, root: Path, locale: Locale) -> dict:
    captures = {}
    for opportunity_id, slug in (
        ("SAU-H6-294110", "penicillin-api"),
        ("SAU-H6-294120", "streptomycin-api"),
        ("SAU-H6-310430", "sop"),
        ("SAU-H6-310510", "fert-retail-packs"),
    ):
        _inspection_open(page, locale)
        page.locator("#opportunity-select").select_option(opportunity_id)
        expect(page.locator("#workspace-title")).to_contain_text(
            opportunity_id.rsplit("-", maxsplit=1)[-1]
        )
        _anchor(page, "#workspace")
        path = root / f"after-{slug}-public-workspace.png"
        page.screenshot(path=path, animations="disabled", caret="hide")
        captures[slug] = str(path)

    _inspection_open(page, locale)
    page.locator("#selection details").evaluate_all(
        "elements => elements.forEach(element => { element.open = true; })"
    )
    _anchor(page, "#selection")
    selection = root / "after-selection-exclusions.png"
    page.screenshot(path=selection, animations="disabled", caret="hide")
    captures["selection-exclusions"] = str(selection)
    return captures


def _capture_workspace_coverage(
    page,
    root: Path,
    locale: Locale,
    side: str,
    version: str,
) -> dict:
    records = {}
    for opportunity_id, mode, expected_state, screen in (
        ("SAU-H0-721049", "public", "INVESTIGATE", "journey-b-steel-public-workspace"),
        ("SAU-H0-721049", "simulated", "ADVANCE", "journey-c-steel-simulated-workspace"),
        ("SAU-H0-390210", "public", "REJECT", "journey-d-polypropylene-public-workspace"),
        ("SAU-H0-390210", "simulated", "REJECT", "journey-d-polypropylene-simulated-workspace"),
        ("SAU-H6-721061", "public", "INVESTIGATE", "journey-g-galvalume-public-workspace"),
        ("SAU-H6-721012", "public", "INVESTIGATE", "journey-g-tinplate-public-workspace"),
        ("SAU-H6-760711", "public", "INVESTIGATE", "journey-g-alu-foil-public-workspace"),
        ("SAU-H6-760429", "public", "INVESTIGATE", "journey-g-alu-profiles-public-workspace"),
        ("SAU-H6-392010", "public", "INVESTIGATE", "journey-g-pe-film-public-workspace"),
    ):
        _inspection_open(page, locale)
        if mode == "simulated":
            page.locator('.mode-button[data-mode="simulated"]').click()
        expect(
            page.locator(f'.mode-button[data-mode="{mode}"]')
        ).to_have_class(re.compile(r"\bactive\b"))
        if page.locator("#opportunity-select").input_value() != opportunity_id:
            page.locator("#opportunity-select").select_option(opportunity_id)
        expect(page.locator("#opportunity-select")).to_have_value(opportunity_id)
        expect(page.locator("#workspace-title")).to_contain_text(
            opportunity_id.rsplit("-", maxsplit=1)[-1]
        )
        banner = page.locator(".integrity-banner")
        state_chips = banner.locator(".state-chip")
        expect(state_chips).to_have_count(2 if mode == "simulated" else 1)
        expect(state_chips.nth(-1)).to_contain_text(expected_state)
        synthetic_labels = banner.locator(".synthetic-labels span")
        expect(synthetic_labels).to_have_count(2 if mode == "simulated" else 0)
        if mode == "simulated":
            expect(page.locator("#workspace .evidence-table")).to_contain_text(
                "DEMO_GENERATOR"
            )
        authority = page.locator(".integrity-authority")
        expect(authority).to_contain_text(version)
        _anchor(page, "#workspace")
        _settle_workspace(page)
        screenshot = root / f"{side}-{screen}.png"
        page.screenshot(path=screenshot, animations="disabled", caret="hide")
        records[screen] = {
            "screenshot": str(screenshot),
            "opportunity_id": opportunity_id,
            "mode": mode,
            "expected_active_state": expected_state,
            "synthetic_disclosure_expected": mode == "simulated",
            "layout": _workspace_layout_snapshot(page),
            "authority_rectangle": _inspection_rect(
                page,
                ".integrity-authority",
            ),
        }
    return records


def _capture_dossier_coverage(
    page,
    root: Path,
    locale: Locale,
    side: str,
    version: str,
) -> dict:
    records = {}
    for opportunity_id, mode, screen in (
        ("SAU-H0-721049", "public", "journey-e-steel-public-dossier"),
        ("SAU-H0-721049", "simulated", "journey-e-steel-simulated-dossier"),
        ("SAU-H0-390210", "public", "journey-e-polypropylene-public-dossier"),
        ("SAU-H0-390210", "simulated", "journey-e-polypropylene-simulated-dossier"),
    ):
        page.goto(
            f"/api/opportunities/{opportunity_id}/dossier.html"
            f"?mode={mode}&locale={locale.code}",
            wait_until="domcontentloaded",
        )
        expect(page.locator("main.page")).to_be_visible()
        screenshot = root / f"{side}-{screen}.png"
        page.screenshot(path=screenshot, animations="disabled", caret="hide")
        records[screen] = {
            "screenshot": str(screenshot),
            "authority_rectangle": _inspection_rect(
                page,
                f'p.small:has-text("{version}")',
            ),
        }
    return records


def _capture_screening_coverage(
    page,
    root: Path,
    locale: Locale,
    side: str,
    version: str,
) -> dict:
    records = {}
    for screen in (
        "journey-f-screening-summary",
        "journey-f-screening-queue-robust",
        "journey-f-screening-queue-empty",
        "journey-f-screening-record",
    ):
        _inspection_open(page, locale)
        open_screening(page, locale)
        if screen == "journey-f-screening-queue-robust":
            open_queue(page, "robust_public_finding", locale)
        elif screen == "journey-f-screening-queue-empty":
            open_queue(page, "resilience_case", locale)
        elif screen == "journey-f-screening-record":
            open_queue(page, "robust_public_finding", locale)
            open_record(page, first_queue_entry_hs6(page), locale)
        _anchor_screening(page)
        screenshot = root / f"{side}-{screen}.png"
        page.screenshot(path=screenshot, animations="disabled", caret="hide")
        records[screen] = {
            "screenshot": str(screenshot),
            "catalogue_rectangle": _inspection_rect(
                page,
                f'#screening :text("{version}")',
            ),
        }
    return records


def _collect_visual_coverage(browser_session: BrowserSession) -> None:
    destination = os.environ.get("IOR_VISUAL_COVERAGE_DIR")
    baseline = os.environ.get("IOR_VISUAL_INSPECTION_BASE")
    if not destination or not baseline:
        return
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    server = start_app_server(Path(baseline), output / "before-server")
    browser = browser_session.context.browser
    records = []
    workspaces_only = os.environ.get(
        "IOR_VISUAL_COVERAGE_WORKSPACES_ONLY"
    ) == "1"
    try:
        for locale in LOCALES:
            for viewport in (DESKTOP, TABLET):
                matrix = output / locale.code / viewport.name
                matrix.mkdir(parents=True, exist_ok=True)
                common = {
                    "locale": locale.bcp47,
                    "reduced_motion": "reduce",
                    "viewport": viewport.as_dict(),
                }
                before_context = browser.new_context(
                    base_url=server.base_url,
                    **common,
                )
                after_context = browser.new_context(
                    base_url=browser_session.app_server.base_url,
                    **common,
                )
                try:
                    before_page = before_context.new_page()
                    after_page = after_context.new_page()
                    before = {
                        "workspaces": _capture_workspace_coverage(
                            before_page,
                            matrix,
                            locale,
                            "before",
                            "1.3.0",
                        )
                    }
                    after = {
                        "workspaces": _capture_workspace_coverage(
                            after_page,
                            matrix,
                            locale,
                            "after",
                            "1.4.0",
                        )
                    }
                    if not workspaces_only:
                        before.update(
                            {
                                "dossiers": _capture_dossier_coverage(
                                    before_page,
                                    matrix,
                                    locale,
                                    "before",
                                    "1.3.0",
                                ),
                                "screening": _capture_screening_coverage(
                                    before_page,
                                    matrix,
                                    locale,
                                    "before",
                                    "1.3.0",
                                ),
                            }
                        )
                        after.update(
                            {
                                "dossiers": _capture_dossier_coverage(
                                    after_page,
                                    matrix,
                                    locale,
                                    "after",
                                    "1.4.0",
                                ),
                                "screening": _capture_screening_coverage(
                                    after_page,
                                    matrix,
                                    locale,
                                    "after",
                                    "1.4.0",
                                ),
                            }
                        )
                    records.append(
                        {
                            "locale": locale.code,
                            "viewport": viewport.name,
                            "before": before,
                            "after": after,
                        }
                    )
                finally:
                    before_context.close()
                    after_context.close()
    finally:
        stop_app_server(server)
    (output / "coverage.json").write_text(
        json.dumps(
            {"schema_version": 1, "matrices": records},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _collect_visual_inspection(browser_session: BrowserSession) -> None:
    destination = os.environ.get("IOR_VISUAL_INSPECTION_DIR")
    baseline = os.environ.get("IOR_VISUAL_INSPECTION_BASE")
    if not destination or not baseline:
        return
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    base = Path(baseline)
    server = start_app_server(base, output / "before-server")
    browser = browser_session.context.browser
    records = []
    try:
        for locale in LOCALES:
            for viewport in (DESKTOP, TABLET):
                matrix = output / locale.code / viewport.name
                matrix.mkdir(parents=True, exist_ok=True)
                common = {
                    "locale": locale.bcp47,
                    "reduced_motion": "reduce",
                    "viewport": viewport.as_dict(),
                }
                before_context = browser.new_context(
                    base_url=server.base_url,
                    **common,
                )
                after_context = browser.new_context(
                    base_url=browser_session.app_server.base_url,
                    **common,
                )
                try:
                    before_page = before_context.new_page()
                    after_page = after_context.new_page()
                    records.append(
                        {
                            "locale": locale.code,
                            "viewport": viewport.name,
                            "before": _capture_existing_inspection(
                                before_page,
                                matrix,
                                locale,
                                "before",
                                "1.3.0",
                            ),
                            "after": _capture_existing_inspection(
                                after_page,
                                matrix,
                                locale,
                                "after",
                                "1.4.0",
                            ),
                            "new": _capture_new_inspection(
                                after_page,
                                matrix,
                                locale,
                            ),
                        }
                    )
                finally:
                    before_context.close()
                    after_context.close()
    finally:
        stop_app_server(server)
    (output / "inspection.json").write_text(
        json.dumps(
            {"schema_version": 1, "matrices": records},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


_PHASE_SNAPSHOT = """node => {
  const origin = node.getBoundingClientRect();
  const styleMap = style => Object.fromEntries(
    Array.from(style).map(name => [name, {
      value: style.getPropertyValue(name),
      priority: style.getPropertyPriority(name),
    }])
  );
  return {
    top: origin.top,
    scroll: scrollY,
    scroll_max: document.documentElement.scrollHeight - innerHeight,
    viewport_size: [innerWidth, innerHeight],
    dpr: devicePixelRatio,
    font_status: document.fonts.status,
    margin: parseFloat(getComputedStyle(node).scrollMarginBlockStart),
    local: Array.from(node.querySelectorAll('*')).map(element => {
      const rect = element.getBoundingClientRect();
      const rendered = element.getClientRects().length;
      return [
        element.tagName,
        element.textContent,
        rendered,
        rendered ? rect.left - origin.left : rect.left,
        rendered ? rect.top - origin.top : rect.top,
        rect.width,
        rect.height,
      ];
    }),
    width: origin.width,
    height: origin.height,
    header: ['.sidebar', '.topbar'].map(selector => {
      const rect = document.querySelector(selector).getBoundingClientRect();
      return [rect.left, rect.top, rect.width, rect.height];
    }),
    document: {
      lang: document.documentElement.lang,
      dir: document.documentElement.dir,
      body_class: document.body.className,
      body_aria_busy: document.body.getAttribute('aria-busy'),
    },
    element_style: node.getAttribute('style'),
    root_style: document.documentElement.getAttribute('style'),
    element_style_map: styleMap(node.style),
    root_style_map: styleMap(document.documentElement.style),
    element_margin_top: parseFloat(getComputedStyle(node).marginTop),
  };
}"""
_PHASE_ADJUST = """(node, delta) => {
  document.documentElement.style.overflowAnchor = 'none';
  document.documentElement.style.scrollBehavior = 'auto';
  node.style.marginTop = (
    parseFloat(getComputedStyle(node).marginTop) + delta
  ) + 'px';
}"""
_PHASE_RESTORE = """(node, saved) => {
  if (saved.style === null) node.removeAttribute('style');
  else node.setAttribute('style', saved.style);
  const root = document.documentElement;
  if (saved.rootStyle === null) root.removeAttribute('style');
  else root.setAttribute('style', saved.rootStyle);
}"""
_PHASE_DOM = """([targetSelector, side, kind, originalElementStyle, expectedSuffix]) => {
  const candidateSide = side === 'candidate';
  const roots = [
    document.querySelector('.sidebar'),
    document.querySelector('.topbar'),
    document.querySelector(targetSelector),
  ];
  if (roots.some(root => !root)) throw new Error('PHASE_REQUIRED_ROOT_MISSING');
  const actualControlValues = Object.fromEntries(
    roots.flatMap(root => Array.from(root.querySelectorAll('input, select, textarea')))
      .map(control => [control.id, {
        tag: control.tagName,
        name: control.getAttribute('name'),
        value: control.value,
        checked: control.checked === true,
      }])
  );
  const clones = roots.map(root => root.cloneNode(true));
  if (side === 'adjusted') {
    if (originalElementStyle === null) clones[2].removeAttribute('style');
    else clones[2].setAttribute('style', originalElementStyle);
  }
  if (kind === 'workspace') {
    const target = clones[2];
    const select = target.querySelector('#opportunity-select');
    const options = Array.from(select.options);
    const extras = [
      'SAU-H6-294110',
      'SAU-H6-294120',
      'SAU-H6-310430',
      'SAU-H6-310510',
    ];
    if (!candidateSide && options.length !== 7) {
      throw new Error('PHASE_REFERENCE_OPTIONS_INVALID');
    }
    if (candidateSide && (
      options.length !== 11 ||
      extras.some(value => options.filter(option => option.value === value).length !== 1)
    )) {
      throw new Error('PHASE_CANDIDATE_OPTIONS_INVALID');
    }
    const retained = options.filter(option => !extras.includes(option.value));
    if (retained.length !== 7) throw new Error('PHASE_RETAINED_OPTIONS_INVALID');
    select.replaceChildren(...retained.map(option => option.cloneNode(true)));
    const authority = target.querySelector('.integrity-authority');
    if (!authority) throw new Error('PHASE_AUTHORITY_MISSING');
    const tokens = Array.from(authority.children).filter(
      child => child.classList.contains('technical-token')
    );
    if (tokens.length !== 7) throw new Error('PHASE_AUTHORITY_TOKENS_INVALID');
    const expected = candidateSide ? '1.4.0' : '1.3.0';
    if (tokens[6].textContent !== expected) throw new Error('PHASE_UI_VERSION_INVALID');
    tokens[6].textContent = 'UI_CATALOGUE_VERSION';
  }
  const monitored = roots.flatMap(root => [
    root,
    ...root.querySelectorAll('*'),
    ...Array.from(function* () {
      let ancestor = root.parentElement;
      while (ancestor) {
        yield ancestor;
        ancestor = ancestor.parentElement;
      }
    }()),
  ]);
  const detached = new CSSStyleSheet();
  detached.replaceSync(expectedSuffix);
  const expectedRules = Array.from(detached.cssRules).map(rule => rule.cssText);
  if (!expectedRules.length) throw new Error('PHASE_SELECTION_SUFFIX_EMPTY');
  let exactSuffixSeen = false;
  const stylesheets = [];
  const visitStylesheet = sheet => {
    const source = sheet.href ? new URL(sheet.href).pathname : null;
    const imports = Array.from(sheet.cssRules)
      .filter(rule => rule.styleSheet)
      .map(rule => ({
        source: rule.href ? new URL(rule.href, document.baseURI).pathname : null,
        media: rule.media ? rule.media.mediaText : '',
        supports: rule.supportsText ?? null,
        layer: rule.layerName ?? null,
      }));
    const directRules = Array.from(sheet.cssRules).filter(rule => !rule.styleSheet);
    let rules = directRules.map(rule => rule.cssText);
    const selectionRules = directRules.filter(
      rule => rule.selectorText && rule.selectorText.includes('.selection-')
    );
    for (const rule of selectionRules) {
      const selectors = rule.selectorText.split(',').map(value => value.trim());
      if (selectors.some(selector => !selector.includes('.selection-'))) {
        throw new Error('PHASE_SELECTION_SELECTOR_INVALID');
      }
      if (monitored.some(element => selectors.some(selector => element.matches(selector)))) {
        throw new Error('PHASE_SELECTION_SELECTOR_MATCHED');
      }
    }
    if (!candidateSide && selectionRules.length) {
      throw new Error('PHASE_REFERENCE_SELECTION_RULES_INVALID');
    }
    if (candidateSide && source && source.endsWith('/overview.css')) {
      const actualSelection = selectionRules.map(rule => rule.cssText);
      const trailing = rules.slice(-expectedRules.length);
      if (JSON.stringify(actualSelection) !== JSON.stringify(expectedRules) ||
          JSON.stringify(trailing) !== JSON.stringify(expectedRules)) {
        throw new Error('PHASE_SELECTION_SUFFIX_INVALID');
      }
      rules = rules.slice(0, -expectedRules.length);
      exactSuffixSeen = true;
    } else if (candidateSide && selectionRules.length) {
      throw new Error('PHASE_SELECTION_RULES_WRONG_SOURCE');
    }
    stylesheets.push({source, imports, rules});
    for (const rule of sheet.cssRules) {
      if (rule.styleSheet) visitStylesheet(rule.styleSheet);
    }
  };
  for (const sheet of document.styleSheets) visitStylesheet(sheet);
  if (candidateSide && !exactSuffixSeen) {
    throw new Error('PHASE_CANDIDATE_SELECTION_RULES_MISSING');
  }
  return {
    roots: clones.map(root => root.outerHTML),
    controls: actualControlValues,
    stylesheets,
  };
}"""
_PHASE_STYLES = """targetSelector => {
  const keys = [
    'fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'fontStretch',
    'fontFeatureSettings', 'lineHeight', 'letterSpacing', 'wordSpacing',
    'whiteSpace', 'textTransform', 'color', 'backgroundColor',
    'backgroundImage', 'borderTop', 'borderRight', 'borderBottom',
    'borderLeft', 'boxShadow', 'opacity', 'filter', 'backdropFilter',
  ];
  const roots = [
    document.querySelector('.sidebar'),
    document.querySelector('.topbar'),
    document.querySelector(targetSelector),
  ];
  return roots.flatMap((root, rootIndex) => {
    const origin = root.getBoundingClientRect();
    return [root, ...root.querySelectorAll('*')]
      .filter(element => element.getClientRects().length)
      .map(element => {
        const parts = [];
        let current = element;
        while (current !== root) {
          parts.unshift(Array.from(current.parentElement.children).indexOf(current));
          current = current.parentElement;
        }
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return {
          path: rootIndex + ':' + parts.join('.'),
          tag: element.tagName,
          rect: [
            rect.left - origin.left,
            rect.top - origin.top,
            rect.width,
            rect.height,
          ],
          values: Object.fromEntries(keys.map(key => [key, style[key]])),
        };
      });
  });
}"""


def _phase_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phase_rgb(page, path: Path) -> Image.Image:
    payload = page.screenshot(
        path=path,
        animations="disabled",
        caret="hide",
    )
    with Image.open(io.BytesIO(payload)) as image:
        return image.convert("RGB")


def _phase_settle(page, selector: str) -> None:
    page.locator(selector).evaluate(
        """async node => {
          await document.fonts.ready;
          let previous = null;
          let stable = 0;
          for (let frame = 0; frame < 60 && stable < 3; frame += 1) {
            await new Promise(requestAnimationFrame);
            const rect = node.getBoundingClientRect();
            const current = [rect.top, rect.left, scrollY];
            stable = previous && current.every(
              (value, index) => Math.abs(value - previous[index]) <= 0.5
            ) ? stable + 1 : 0;
            previous = current;
          }
          if (stable < 3 || document.fonts.status !== 'loaded') {
            throw new Error('PHASE_LAYOUT_NOT_SETTLED');
          }
        }"""
    )


def _phase_observed_state(page, selector: str, expected: dict) -> dict:
    active_modes = page.locator(".mode-button.active")
    expect(active_modes).to_have_count(1)
    mode = active_modes.get_attribute("data-mode")
    locale, direction, width, height = page.evaluate(
        """() => [
          document.documentElement.lang,
          document.documentElement.dir,
          innerWidth,
          innerHeight,
        ]"""
    )
    viewport = {
        (1440, 900): "desktop-1440x900",
        (1024, 768): "tablet-1024x768",
    }.get((width, height))
    if selector == "#workspace":
        selected_id = page.locator("#opportunity-select").input_value()
        hs6 = selected_id.rsplit("-", 1)[-1]
        expect(page.locator("#workspace-title")).to_contain_text(hs6)
        tokens = page.locator(".integrity-banner .state-chip .technical-token")
        values = tokens.all_inner_texts()
        labels = page.locator(".integrity-banner .synthetic-labels span")
        label_count = labels.count()
        state = {
            "selected_id": selected_id,
            "hs6": hs6,
            "mode": mode,
            "real_state": values[0] if values else None,
            "active_state": values[-1] if values else None,
            "synthetic_disclosure": label_count > 0,
            "synthetic_label_count": label_count,
            "locale": locale,
            "viewport": viewport,
            "view": "workspace",
        }
    else:
        view = page.locator("#screening-view .screening-view")
        classes = view.get_attribute("class") or ""
        if "screening-record" in classes:
            actual_view = "journey-f-screening-record"
            hs6 = view.locator("h2 .technical-token").inner_text()
        elif "screening-queue" in classes:
            hs6 = None
            actual_view = (
                "journey-f-screening-queue-robust"
                if view.locator("button[data-hs6]").count()
                else "journey-f-screening-queue-empty"
            )
        else:
            actual_view, hs6 = "journey-f-screening-summary", None
        state = {
            "selected_id": None,
            "hs6": hs6,
            "mode": mode,
            "real_state": None,
            "active_state": None,
            "synthetic_disclosure": False,
            "synthetic_label_count": 0,
            "locale": locale,
            "viewport": viewport,
            "view": actual_view,
        }
    assert direction == {"en": "ltr", "ar": "rtl"}[locale]
    assert state == expected
    return state


def _phase_snapshot(
    page,
    selector: str,
    side: str,
    kind: str,
    expected_state: dict,
    suffix: str,
    original_element_style: str | None = None,
) -> dict:
    node = page.locator(selector)
    snapshot = node.evaluate(_PHASE_SNAPSHOT)
    snapshot["state"] = _phase_observed_state(page, selector, expected_state)
    snapshot["dom"] = page.evaluate(
        _PHASE_DOM,
        [selector, side, kind, original_element_style, suffix],
    )
    snapshot["styles"] = page.evaluate(_PHASE_STYLES, selector)
    return snapshot


def _phase_open_workspace(page, locale: Locale, state: dict, version: str) -> None:
    _inspection_open(page, locale)
    mode = state["mode"]
    if mode == "simulated":
        page.locator('.mode-button[data-mode="simulated"]').click()
    expect(page.locator(f'.mode-button[data-mode="{mode}"]')).to_have_class(
        re.compile(r"\bactive\b")
    )
    select = page.locator("#opportunity-select")
    if select.input_value() != state["selected_id"]:
        select.select_option(state["selected_id"])
    expect(select).to_have_value(state["selected_id"])
    expect(page.locator("#workspace-title")).to_contain_text(state["hs6"])
    banner = page.locator(".integrity-banner")
    chips = banner.locator(".state-chip")
    expect(chips).to_have_count(2 if mode == "simulated" else 1)
    expect(chips.first.locator(".technical-token")).to_have_text(state["real_state"])
    expect(chips.nth(-1).locator(".technical-token")).to_have_text(state["active_state"])
    expect(banner.locator(".synthetic-labels span")).to_have_count(
        2 if mode == "simulated" else 0
    )
    if mode == "simulated":
        expect(page.locator("#workspace .evidence-table")).to_contain_text(
            "DEMO_GENERATOR"
        )
    expect(page.locator(".integrity-authority")).to_contain_text(version)
    _anchor(page, "#workspace")
    _phase_settle(page, "#workspace")


def _phase_open_screening(page, locale: Locale, screen: str) -> str | None:
    _inspection_open(page, locale)
    open_screening(page, locale)
    hs6 = None
    if screen == "journey-f-screening-queue-robust":
        open_queue(page, "robust_public_finding", locale)
    elif screen == "journey-f-screening-queue-empty":
        open_queue(page, "resilience_case", locale)
    elif screen == "journey-f-screening-record":
        open_queue(page, "robust_public_finding", locale)
        hs6 = first_queue_entry_hs6(page)
        open_record(page, hs6, locale)
    _anchor_screening(page)
    _phase_settle(page, "#screening")
    return hs6


def _phase_registered_record(
    reference_page,
    candidate_page,
    output: Path,
    baseline_root: Path,
    candidate_root: Path,
    regions: dict,
    path: str,
    selector: str,
    kind: str,
    state: dict,
    suffix: str,
) -> dict:
    slug = path.replace("/", "__").removesuffix(".webp")
    reference_capture = output / f"{slug}__reference.png"
    candidate_capture = output / f"{slug}__candidate.png"
    adjusted_capture = output / f"{slug}__adjusted.png"
    restored_capture = output / f"{slug}__restored.png"
    reference_image = _phase_rgb(reference_page, reference_capture)
    candidate_image = _phase_rgb(candidate_page, candidate_capture)
    with Image.open(baseline_root / path) as image:
        baseline_image = image.convert("RGB")
    with Image.open(candidate_root / path) as image:
        retained_candidate = image.convert("RGB")
    reference_link = ImageChops.difference(reference_image, baseline_image).getbbox() is None
    candidate_link = ImageChops.difference(candidate_image, retained_candidate).getbbox() is None
    saved = reference_page.locator(selector).evaluate(
        """node => ({
          style: node.getAttribute('style'),
          rootStyle: document.documentElement.getAttribute('style'),
        })"""
    )
    reference = _phase_snapshot(
        reference_page, selector, "reference", kind, state, suffix, saved["style"]
    )
    candidate = _phase_snapshot(
        candidate_page, selector, "candidate", kind, state, suffix
    )
    delta = candidate["top"] - reference["top"]
    reference_page.locator(selector).evaluate(_PHASE_ADJUST, delta)
    _phase_settle(reference_page, selector)
    adjusted = _phase_snapshot(
        reference_page, selector, "adjusted", kind, state, suffix, saved["style"]
    )
    adjusted_image = _phase_rgb(reference_page, adjusted_capture)
    metrics = registered_metrics(
        adjusted_image,
        candidate_image,
        regions.get(path, []),
    )
    reference_page.locator(selector).evaluate(_PHASE_RESTORE, saved)
    _phase_settle(reference_page, selector)
    restored = _phase_snapshot(
        reference_page, selector, "reference", kind, state, suffix, saved["style"]
    )
    restored_image = _phase_rgb(reference_page, restored_capture)
    restoration_rgb = ImageChops.difference(
        restored_image,
        reference_image,
    ).getbbox() is None
    record = {
        "path": path,
        "kind": kind,
        "case_id": state.get("selected_id") or state.get("hs6"),
        "view": state.get("view"),
        "mode": state["mode"],
        "locale": state["locale"],
        "viewport": state["viewport"],
        "reference_baseline_sha256": _phase_sha(baseline_root / path),
        "candidate_baseline_sha256": _phase_sha(candidate_root / path),
        "reference_capture": str(reference_capture),
        "reference_capture_sha256": _phase_sha(reference_capture),
        "candidate_capture": str(candidate_capture),
        "candidate_capture_sha256": _phase_sha(candidate_capture),
        "adjusted_capture": str(adjusted_capture),
        "adjusted_capture_sha256": _phase_sha(adjusted_capture),
        "restored_capture": str(restored_capture),
        "restored_capture_sha256": _phase_sha(restored_capture),
        "reference": reference,
        "candidate": candidate,
        "adjusted": adjusted,
        "restored": restored,
        "delta": delta,
        "reference_link_exact": reference_link,
        "candidate_link_exact": candidate_link,
        "restoration_rgb_exact": restoration_rgb,
        "raw_drift_nonzero": ImageChops.difference(
            reference_image,
            candidate_image,
        ).getbbox() is not None,
        "registered_metrics": metrics,
    }
    problems = phase_record_problems(record, expected_state=state)
    assert problems == [], (path, problems)
    return record


def _phase_negative_proof(
    browser, base_url: str, valid_record: dict, suffix: str
) -> tuple[dict, dict]:
    context = browser.new_context(
        base_url=base_url,
        locale="en-US",
        reduced_motion="reduce",
        viewport=DESKTOP.as_dict(),
    )
    page = context.new_page()
    state = {
        "selected_id": "SAU-H0-721049",
        "hs6": "721049",
        "mode": "public",
        "real_state": "INVESTIGATE",
        "active_state": "INVESTIGATE",
        "synthetic_disclosure": False,
        "synthetic_label_count": 0,
        "locale": "en",
        "viewport": DESKTOP.name,
        "view": "workspace",
    }
    try:
        _phase_open_workspace(page, LOCALES[0], state, "1.4.0")
        page.locator("#workspace-title").evaluate(
            "node => { node.textContent += ' tampered'; }"
        )
        semantic = _phase_snapshot(
            page,
            "#workspace",
            "candidate",
            "workspace",
            state,
            suffix,
        )
        tampered = json.loads(json.dumps(valid_record))
        tampered["candidate"]["dom"] = semantic["dom"]
        assert phase_record_problems(tampered, expected_state=state)

        _phase_open_workspace(page, LOCALES[0], state, "1.4.0")
        page.locator(".decision-hero").evaluate(
            "node => { node.style.color = 'rgb(1, 2, 3)'; }"
        )
        styled = _phase_snapshot(
            page,
            "#workspace",
            "candidate",
            "workspace",
            state,
            suffix,
        )
        tampered = json.loads(json.dumps(valid_record))
        tampered["candidate"]["styles"] = styled["styles"]
        assert phase_record_problems(tampered, expected_state=state)

        _phase_open_workspace(page, LOCALES[0], state, "1.4.0")
        page.locator(".integrity-authority").evaluate("node => node.remove()")
        with pytest.raises(PlaywrightError, match="PHASE_AUTHORITY_MISSING"):
            _phase_snapshot(
                page,
                "#workspace",
                "candidate",
                "workspace",
                state,
                suffix,
            )
        return (
            {
                "semantic_text": True,
                "paint_style": True,
                "missing_element": True,
            },
            {
                "semantic_text": "workspace-title text mutation rejected",
                "paint_style": "decision-hero inline color mutation rejected",
                "missing_element": "PHASE_AUTHORITY_MISSING",
            },
        )
    finally:
        context.close()


def _collect_visual_phase_recovery(browser_session: BrowserSession) -> None:
    destination = os.environ.get("IOR_VISUAL_PHASE_RECOVERY_DIR")
    baseline = os.environ.get("IOR_VISUAL_INSPECTION_BASE")
    if not destination or not baseline:
        return
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    project = Path(__file__).resolve().parents[1]
    baseline_project = Path(baseline)
    baseline_root = baseline_project / "browser_tests/baselines/v0.3.0"
    candidate_root = project / "browser_tests/baselines/v0.3.0"
    manifest = validate_manifest(candidate_root)
    regions_path = Path(
        "/home/barami/.cache/industrial-opportunity-resolution-mvp/"
        "s15b-20260915-native01/visual-regions.json"
    )
    regions = json.loads(regions_path.read_text(encoding="utf-8"))["regions"]
    overview_reference = baseline_project / "src/ior_mvp/static/css/overview.css"
    overview_candidate = project / "src/ior_mvp/static/css/overview.css"
    reference_css = overview_reference.read_bytes()
    candidate_css = overview_candidate.read_bytes()
    assert candidate_css.startswith(reference_css)
    suffix = candidate_css[len(reference_css):].decode("utf-8")
    assert ".selection-" in suffix
    server = start_app_server(baseline_project, output / "reference-server")
    browser = browser_session.context.browser
    records = []
    workspace_screens = (
        "journey-b-steel-public-workspace",
        "journey-c-steel-simulated-workspace",
        "journey-d-polypropylene-public-workspace",
        "journey-d-polypropylene-simulated-workspace",
        "journey-g-galvalume-public-workspace",
        "journey-g-tinplate-public-workspace",
        "journey-g-alu-foil-public-workspace",
        "journey-g-alu-profiles-public-workspace",
        "journey-g-pe-film-public-workspace",
    )
    entries = {entry["path"]: entry for entry in manifest["entries"]}
    screening_states = (
        "journey-f-screening-summary",
        "journey-f-screening-queue-robust",
        "journey-f-screening-queue-empty",
        "journey-f-screening-record",
    )
    try:
        for locale in LOCALES:
            for viewport in (DESKTOP, TABLET):
                common = {
                    "locale": locale.bcp47,
                    "reduced_motion": "reduce",
                    "viewport": viewport.as_dict(),
                }
                reference_context = browser.new_context(
                    base_url=server.base_url,
                    **common,
                )
                candidate_context = browser.new_context(
                    base_url=browser_session.app_server.base_url,
                    **common,
                )
                try:
                    reference_page = reference_context.new_page()
                    candidate_page = candidate_context.new_page()
                    for screen in workspace_screens:
                        path = f"{locale.code}/{viewport.name}/{screen}.webp"
                        state = phase_expected_state(entries[path])
                        _phase_open_workspace(reference_page, locale, state, "1.3.0")
                        _phase_open_workspace(candidate_page, locale, state, "1.4.0")
                        records.append(
                            _phase_registered_record(
                                reference_page,
                                candidate_page,
                                output,
                                baseline_root,
                                candidate_root,
                                regions,
                                path,
                                "#workspace",
                                "workspace",
                                state,
                                suffix,
                            )
                        )
                    for screen in screening_states:
                        path = f"{locale.code}/{viewport.name}/{screen}.webp"
                        state = phase_expected_state(entries[path])
                        reference_hs6 = _phase_open_screening(reference_page, locale, screen)
                        candidate_hs6 = _phase_open_screening(candidate_page, locale, screen)
                        assert reference_hs6 == candidate_hs6 == state["hs6"]
                        records.append(
                            _phase_registered_record(
                                reference_page,
                                candidate_page,
                                output,
                                baseline_root,
                                candidate_root,
                                regions,
                                path,
                                "#screening",
                                "screening",
                                state,
                                suffix,
                            )
                        )
                finally:
                    reference_context.close()
                    candidate_context.close()
    finally:
        stop_app_server(server)
    negative_proof, negative_details = _phase_negative_proof(
        browser,
        browser_session.app_server.base_url,
        records[0],
        suffix,
    )
    common_paths = {
        entry["path"] for entry in manifest["entries"]
        if (baseline_root / entry["path"]).is_file()
    }
    additions = {
        entry["path"] for entry in manifest["entries"]
        if not (baseline_root / entry["path"]).is_file()
    }
    new_views = [
        entry for entry in manifest["entries"] if entry["path"] in additions
    ]
    assert len(new_views) == 20
    assert all(entry["mode"] == "public" for entry in new_views)
    assert {
        entry["screen"] for entry in new_views
    } == {
        "journey-g-penicillin-api-public-workspace",
        "journey-g-streptomycin-api-public-workspace",
        "journey-g-sop-public-workspace",
        "journey-g-fert-retail-packs-public-workspace",
        "journey-h-selection-exclusions",
    }
    new_view_inspections = []
    for entry in sorted(new_views, key=lambda item: item["path"]):
        with Image.open(candidate_root / entry["path"]) as image:
            image.load()
            assert image.format == "WEBP" and image.mode == "RGB"
            assert list(image.size) == entry["dimensions"]
            assert image.getbbox() is not None
            new_view_inspections.append(
                {
                    "path": entry["path"],
                    "format": image.format,
                    "mode": image.mode,
                    "dimensions": list(image.size),
                    "channel_extrema": [list(values) for values in image.getextrema()],
                    "nonblank_bbox": list(image.getbbox()),
                }
            )
    source = Path(__file__)
    reference_styles = {
        path.name: _phase_sha(path)
        for path in (baseline_project / "src/ior_mvp/static/css").glob("*.css")
        if path.name != "overview.css"
    }
    candidate_styles = {
        path.name: _phase_sha(path)
        for path in (project / "src/ior_mvp/static/css").glob("*.css")
        if path.name != "overview.css"
    }
    assert reference_styles == candidate_styles
    payload = {
        "schema_version": 1,
        "method": "S15B_DOM_PHASE_1",
        "bindings": {
            "base": "f671f36fe6ea56b2c009ede91847b7dbf950a939",
            "reference_manifest_sha256": _phase_sha(baseline_root / "manifest.json"),
            "candidate_manifest_sha256": _phase_sha(candidate_root / "manifest.json"),
            "regions_sha256": _phase_sha(regions_path),
            "capture_source": source.relative_to(project).as_posix(),
            "capture_source_sha256": _phase_sha(source),
            "browser_version": browser.version,
            "chromium_revision": "chromium-1234",
            "launch_flags": list(LAUNCH_FLAGS),
            "font_hashes": manifest["font_hashes"],
            "playwright_version": importlib.metadata.version("playwright"),
            "pytest_playwright_version": importlib.metadata.version("pytest-playwright"),
            "overview_reference_sha256": hashlib.sha256(reference_css).hexdigest(),
            "overview_candidate_sha256": hashlib.sha256(candidate_css).hexdigest(),
            "overview_suffix": suffix,
            "unchanged_stylesheets": candidate_styles,
        },
        "common": len(common_paths),
        "registered_pairs": len(records),
        "unadjusted_portfolio_pairs": 8,
        "identical_dossier_pairs": 16,
        "additions": len(additions),
        "removals": 0,
        "raw_strict_failure_retained": True,
        "records": records,
        "negative_proof": negative_proof,
        "negative_details": negative_details,
        "new_views": sorted(new_views, key=lambda entry: entry["path"]),
        "new_view_inspections": new_view_inspections,
    }
    assert len(records) == 52
    assert len(common_paths) == 76
    assert len(additions) == 20
    coverage_file = output / "phase-coverage.json"
    coverage_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tamper_cases = []
    wrong_binding = json.loads(json.dumps(payload))
    wrong_binding["bindings"]["browser_version"] = "wrong"
    tamper_cases.append(("wrong-binding", wrong_binding))
    fake_negative = json.loads(json.dumps(payload))
    fake_negative["negative_proof"] = {"anything": True}
    tamper_cases.append(("fake-negative", fake_negative))
    missing_negative = json.loads(json.dumps(payload))
    missing_negative["negative_proof"].pop("missing_element")
    tamper_cases.append(("missing-negative", missing_negative))
    duplicate_views = json.loads(json.dumps(payload))
    duplicate_views["new_views"].append(duplicate_views["new_views"][0])
    tamper_cases.append(("duplicate-view", duplicate_views))
    unsafe_path = json.loads(json.dumps(payload))
    unsafe_path["records"][0]["reference_capture"] = "/tmp/escape.png"
    tamper_cases.append(("unsafe-path", unsafe_path))
    inconsistent_raw = json.loads(json.dumps(payload))
    inconsistent_raw["records"][0]["raw_drift_nonzero"] = False
    tamper_cases.append(("raw-flag", inconsistent_raw))
    crop = output / "tampered-crop.png"
    Image.new("RGB", (2, 2), "white").save(crop)
    cropped = json.loads(json.dumps(payload))
    cropped["records"][0]["candidate_capture"] = str(crop)
    cropped["records"][0]["candidate_capture_sha256"] = _phase_sha(crop)
    tamper_cases.append(("crop", cropped))
    for name, tampered in tamper_cases:
        path = output / f"tamper-{name}.json"
        path.write_text(json.dumps(tampered), encoding="utf-8")
        with pytest.raises(ReviewCheckError):
            check_visual_phase_drift(
                baseline_root, candidate_root, regions_path, path
            )
    enlarged = json.loads(json.dumps({"regions": regions}))
    first_region = next(iter(enlarged["regions"]))
    enlarged["regions"][first_region][0] = [0, 0, 1440, 900]
    enlarged_path = output / "tamper-regions.json"
    enlarged_path.write_text(json.dumps(enlarged), encoding="utf-8")
    with pytest.raises(ReviewCheckError, match="approved subject"):
        check_visual_phase_drift(
            baseline_root, candidate_root, enlarged_path, coverage_file
        )


def _assert_am4_bitmap_regressions(root: Path) -> dict[str, str]:
    def drift_case(name: str, pixel: tuple[int, int], rectangle: list[int]):
        before = root / name / "before"
        after = root / name / "after"
        relative = Path("en/desktop/screen.webp")
        (before / relative).parent.mkdir(parents=True)
        (after / relative).parent.mkdir(parents=True)
        old = Image.new("RGB", (10, 10), "white")
        new = old.copy()
        new.putpixel(pixel, (0, 0, 0))
        old.save(before / relative, format="WEBP", lossless=True)
        new.save(after / relative, format="WEBP", lossless=True)
        regions = root / name / "regions.json"
        regions.write_text(
            json.dumps({"regions": {relative.as_posix(): [rectangle]}}),
            encoding="utf-8",
        )
        return before, after, regions

    for index, rectangle in enumerate(([0, 10, 5, 5], [0, 0, 11, 10], [0, 0, 0, 5])):
        values = drift_case(f"invalid-{index}", (1, 1), rectangle)
        with pytest.raises(ReviewCheckError, match="invalid visual region bounds"):
            _visual_drift(*values)
    inside = drift_case("inside", (1, 1), [0, 0, 2, 2])
    assert _visual_drift(*inside)["outside_changed"] == 0
    outside = drift_case("outside", (8, 8), [0, 0, 2, 2])
    with pytest.raises(ReviewCheckError, match="outside approved region"):
        _visual_drift(*outside)
    reference = Image.new("RGB", (100, 100), "white")
    candidate = reference.copy()
    candidate.putpixel((50, 50), (250, 255, 255))
    assert registered_metrics(reference, candidate, [])["passes"] is True
    ratio = reference.copy()
    for x in range(11):
        ratio.putpixel((x, 0), (246, 255, 255))
    ratio_metrics = registered_metrics(reference, ratio, [])
    assert ratio_metrics["passes"] is False
    assert ratio_metrics["significant_pixel_ratio"] > 0.001
    mean = reference.copy()
    for index in range(1000):
        mean.putpixel((index % 100, index // 100), (247, 247, 247))
    mean_metrics = registered_metrics(reference, mean, [])
    assert mean_metrics["passes"] is False
    assert mean_metrics["significant_pixel_ratio"] == 0
    assert mean_metrics["mean_absolute_channel_error"] > 0.20
    crop = root / "crop.png"
    Image.new("RGB", (2, 2), "white").save(crop)
    with pytest.raises(ReviewCheckError, match="dimensions or format"):
        phase_read_rgb(crop, [10, 10], format_name="PNG")
    alpha = root / "alpha.png"
    Image.new("RGBA", (10, 10), (255, 255, 255, 254)).save(alpha)
    with pytest.raises(ReviewCheckError, match="opaque RGB"):
        phase_read_rgb(alpha, [10, 10], format_name="PNG")
    return {
        "invalid_rectangles": "three bounds cases",
        "inside_region": "strict pass",
        "outside_region": "one-pixel strict rejection",
        "registered_positive": "nonzero raw in-tolerance pass",
        "registered_ratio_boundary": "fixed ratio rejection",
        "registered_mean_boundary": "fixed mean rejection",
        "dimension_and_alpha": "exact decode rejection",
    }


@pytest.mark.parametrize(
    "locale",
    LOCALES,
    ids=[locale.code for locale in LOCALES],
)
def test_s15b_selection_and_every_exclusion_render_bilingually(
    browser_session: BrowserSession,
    locale: Locale,
) -> None:
    page = browser_session.page
    goto_portfolio(page, "public", locale)
    strings = locale_bundle(locale)["strings"]
    selection = page.locator("#case-selection-view")

    expect(selection.locator(".selection-summary")).to_be_visible()
    profiles = selection.locator(".selection-profile")
    expect(profiles).to_have_count(2)
    pharma_heading = profiles.nth(0).locator("h3")
    profile_identifier = pharma_heading.locator(".technical-token")
    expect(profile_identifier).to_have_text("pharma_api")
    expect(profile_identifier).to_have_attribute("dir", "ltr")
    expect(pharma_heading).not_to_contain_text("pharma api")
    expect(selection).to_contain_text("CASE-SELECTION-S15-b96de36ff0ce")
    expect(selection).to_contain_text("S14-CS-1.1")
    for hs6 in ("294110", "294120", "310430", "310510"):
        expect(selection).to_contain_text(hs6)
    for key in (
        "selection.selected",
        "selection.substitution_order",
        "selection.identity_exclusions",
        "selection.viability_exclusions",
        "selection.series_gap_exclusions",
        "selection.frozen_exclusions",
        "selection.inputs",
    ):
        expect(selection).to_contain_text(strings[key])
    details = selection.locator("details")
    expect(details).to_have_count(11)
    for item in details.all():
        item.locator("summary").click()
    expect(selection).to_contain_text("SERIES_GAP_YEARS")
    expect(selection).to_contain_text("RESIDUAL_CATCH_ALL_SUBHEADING")
    expect(selection).to_contain_text("310420")
    expect(selection).to_contain_text("293711")
    correction_dir = os.environ.get("IOR_SELECTION_CORRECTION_DIR")
    if correction_dir:
        output = Path(correction_dir)
        output.mkdir(parents=True, exist_ok=True)
        _anchor(page, "#selection")
        page.screenshot(
            path=output / f"selection-{locale.code}.png",
            animations="disabled",
            caret="hide",
        )
    for label in locale_bundle(locale)["synthetic_labels"].values():
        expect(selection).not_to_contain_text(label)
    opportunity = page.locator("#opportunity-select")
    for case_id in (
        "SAU-H6-294120",
        "SAU-H6-310430",
        "SAU-H6-310510",
        "SAU-H6-760429",
    ):
        opportunity.select_option(case_id)
        expect(opportunity).to_have_value(case_id)
        hhi_metric = page.locator("#workspace .metric-box").filter(
            has_text=strings["metric.supplier_hhi"]
        )
        expect(hhi_metric.locator("strong")).to_have_text(
            strings["common.unavailable"]
        )
        expect(hhi_metric.locator("p")).to_have_text(
            strings["metric.hhi_unavailable"]
        )
        expect(hhi_metric).not_to_contain_text("NaN")
        public_states = page.locator(
            ".integrity-banner .state-chip .technical-token"
        )
        expect(public_states).to_have_count(1)
        expect(public_states).to_have_text("INVESTIGATE")


def test_s15b_selection_endpoint_is_loaded_once_without_mode_query(
    browser_session: BrowserSession,
    tmp_path: Path,
) -> None:
    bitmap_mapping = _assert_am4_bitmap_regressions(tmp_path / "am4-bitmap")
    assert len(bitmap_mapping) == 7
    page = browser_session.page
    requests: list[str] = []
    page.on(
        "request",
        lambda request: requests.append(request.url)
        if "/api/case-selection" in request.url
        else None,
    )

    goto_portfolio(page, "public", LOCALES[0])
    page.locator('.mode-button[data-mode="simulated"]').click()
    expect(page.locator('.mode-button[data-mode="simulated"]')).to_have_class(
        re.compile(r"\bactive\b")
    )

    assert len(requests) == 1
    assert requests[0].endswith("/api/case-selection")
    _collect_visual_inspection(browser_session)
    _collect_visual_coverage(browser_session)
    _collect_visual_phase_recovery(browser_session)
